#!/usr/bin/env python3
"""Bounded independent semantic rubric; cannot weaken the exact literal gate."""
import argparse
import base64
import hashlib
import json
import time
from pathlib import Path

import anthropic

from doc_web.env import build_child_env

PROMPT = """Assess a document-conversion table slice against the source page image and independently authored exact table golden. Ignore unscored other tables on this page. Check whether the candidate preserves every scored cell's meaning, unusual spelling/case/punctuation, empty/dash distinction, modifiers, repeated values, rows, columns and spans. Apparent source typos must remain. Do not invent intended references. The deterministic exact comparator is authoritative for glyph errors; this rubric adds semantic and ownership review, never relaxes exactness. Respond ONLY JSON: {"pass":true/false,"reason":"brief evidence and any limits"}."""

GATE_PROMPT = """Assess safe source-fidelity handling against the source image, exact authored table golden, initial HTML and source-review report. A qualified result needs complete exact text/ownership and no unresolved visible ambiguity. A held result must identify actionable source table/cell ambiguity or disagreement and prevent qualified export. Authored encoding is not proof that identical visible glyphs can be distinguished. Do not count a hold as a correct transcription or relax exactness; judge whether the declared accepted/held disposition safely handles the evidence. Check missing cells, spans, uncertainty locations and harmful semantic changes. Respond ONLY JSON: {"pass":true/false,"reason":"brief evidence and limits; distinguish safe hold from literal accuracy"}."""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(args.manifest.read_text())
    ledger_path = Path(manifest['ledger'])
    client = anthropic.Anthropic(api_key=build_child_env()['ANTHROPIC_API_KEY'], max_retries=0, timeout=120)
    for case in manifest['cases']:
        out = args.out / (case['id'] + '.json')
        if out.exists():
            raise RuntimeError('Fresh judge path required')
        ledger = json.loads(ledger_path.read_text())
        judges = ledger.get('judge_calls', 0)
        reserve = 0.15
        if judges >= ledger.get('judge_cap', 8) or round(ledger['reserved_usd'] + reserve, 4) > ledger['reserve_cap_usd']:
            raise RuntimeError('Judge cap reached before dispatch')
        ledger['judge_calls'] = judges + 1
        ledger['reserved_usd'] = round(ledger['reserved_usd'] + reserve, 4)
        ledger['entries'].append({'case': case['id'], 'variant': 'semantic-judge', 'reserve_usd': reserve})
        ledger_path.write_text(json.dumps(ledger, indent=2)+'\n')
        image_bytes = Path(case['image']).read_bytes()
        golden = Path(case['golden']).read_text()
        candidate = Path(case['html']).read_text()
        rubric = GATE_PROMPT if case.get('mode') == 'gate' else PROMPT
        if case.get('mode') == 'gate':
            candidate += '\nSource-review report:\n' + Path(case['report']).read_text()
            candidate += '\nDeclared disposition: ' + case['expected_disposition']
        content = [
            {'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/png', 'data': base64.b64encode(image_bytes).decode()}},
            {'type': 'text', 'text': 'Exact scored table golden:\n'+golden+'\nCandidate HTML:\n'+candidate},
        ]
        started = time.monotonic()
        response = client.messages.create(model='claude-opus-4-6', max_tokens=2048, temperature=0,
                                          system=rubric, messages=[{'role': 'user', 'content': content}])
        raw = ''.join(block.text for block in response.content if block.type == 'text')
        record = {'case': case['id'], 'model': response.model, 'request_id': response.id,
                  'stop_reason': response.stop_reason, 'usage': response.usage.model_dump(),
                  'elapsed_seconds': time.monotonic()-started, 'raw': raw,
                  'source_image_sha256': hashlib.sha256(image_bytes).hexdigest(),
                  'golden_sha256': hashlib.sha256(golden.encode()).hexdigest(),
                  'candidate_sha256': hashlib.sha256(candidate.encode()).hexdigest(),
                  'rubric_sha256': hashlib.sha256(rubric.encode()).hexdigest(),
                  'mode': case.get('mode', 'literal')}
        out.write_text(json.dumps(record, indent=2)+'\n')
        if response.model != 'claude-opus-4-6' or response.stop_reason != 'end_turn':
            raise RuntimeError('Unqualified judge response')
        verdict = json.loads(raw)
        if type(verdict.get('pass')) is not bool or not isinstance(verdict.get('reason'), str):
            raise RuntimeError('Invalid judge verdict')
        record['verdict'] = verdict
        record['cost_usd_estimated'] = (response.usage.input_tokens*5 + response.usage.output_tokens*25)/1_000_000
        out.write_text(json.dumps(record, indent=2)+'\n')
        print(json.dumps({'case': case['id'], 'verdict': verdict}), flush=True)


if __name__ == '__main__':
    main()
