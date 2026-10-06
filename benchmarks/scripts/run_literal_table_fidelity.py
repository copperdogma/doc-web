#!/usr/bin/env python3
"""Bounded source-only OCR comparison; goldens never enter model requests."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import time
from pathlib import Path
from types import SimpleNamespace

from openai import OpenAI

from doc_web.env import build_child_env
from modules.extract.ocr_ai_gpt51_v1.main import (
    SYSTEM_PROMPT, _call_vision_model, _extract_code_fence, _extract_ocr_metadata,
    _resize_image_bytes, sanitize_html,
)

from modules.common.ocr_literal_policy import LITERAL_POLICY

USER_TEXT = ('Return HTML only. FIRST line MUST be: <meta name="ocr-metadata" '
             'data-ocr-quality="0.0-1.0" data-ocr-integrity="0.0-1.0" '
             'data-continuation-risk="0.0-1.0">')


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class RecordingResponses:
    def __init__(self, client, record, detail=None):
        self.client = client
        self.record = record
        self.detail = detail

    def create(self, **kwargs):
        kwargs['store'] = False
        if self.detail:
            for message in kwargs['input']:
                for item in message.get('content', []):
                    if item.get('type') == 'input_image':
                        item['detail'] = self.detail
        if kwargs['model'] == 'gpt-6-astra':
            kwargs['reasoning'] = {'effort': 'medium'}
        self.record['request'] = {
            'model': kwargs['model'], 'store': kwargs['store'],
            'max_output_tokens': kwargs['max_output_tokens'],
            'reasoning': kwargs.get('reasoning'), 'image_detail': self.detail,
        }
        response = self.client.responses.create(**kwargs)
        self.record.update(served_model=response.model, response_id=response.id,
                           status=response.status, usage=response.usage.model_dump(),
                           incomplete_details=str(response.incomplete_details))
        if response.status != 'completed':
            raise RuntimeError('Incomplete response; not a quality result')
        expected = kwargs['model']
        if response.model != expected and not re.fullmatch(re.escape(expected) + r'-20\d{2}-\d{2}-\d{2}', response.model):
            raise RuntimeError('Unexpected served model')
        return response


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--variant', choices=['baseline', 'literal', 'strong'], required=True)
    parser.add_argument('--case', action='append')
    parser.add_argument('--max-long-side', type=int, default=2048)
    parser.add_argument('--image-detail', choices=['auto', 'high', 'original'])
    parser.add_argument('--score-only', action='store_true')
    args = parser.parse_args()
    from benchmarks.scorers.literal_table_diff import compare_tables
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(args.manifest.read_text())
    ledger_path = Path(manifest['ledger'])
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {
        'calls': 0, 'reserved_usd': 0.0, 'call_cap': 24, 'reserve_cap_usd': 10.0,
        'entries': [],
    }
    prompt = SYSTEM_PROMPT
    if args.variant != 'baseline':
        prompt += '\n\n' + LITERAL_POLICY
    model = 'gpt-6-astra' if args.variant == 'strong' else 'gpt-5.1'
    client = None if args.score_only else OpenAI(
        api_key=build_child_env()['OPENAI_API_KEY'], max_retries=0, timeout=180,
    )
    scores = []
    for case in manifest['cases']:
        if args.case and case['id'] not in args.case:
            continue
        raw_path = args.out / (case['id'] + '.raw.html')
        clean_path = args.out / (case['id'] + '.html')
        record_path = args.out / (case['id'] + '.request.json')
        if not args.score_only:
            if raw_path.exists() or record_path.exists():
                raise RuntimeError('Fresh output paths required; no favorable reruns')
            image = Path(case['image']).read_bytes()
            mime = 'image/jpeg' if Path(case['image']).suffix.lower() in {'.jpg','.jpeg'} else 'image/png'
            image, mime, resized = _resize_image_bytes(image, args.max_long_side, mime)
            reserve = 0.85 if model == 'gpt-6-astra' else 0.15
            if ledger['calls'] >= ledger['call_cap'] or ledger['reserved_usd'] + reserve > ledger['reserve_cap_usd']:
                raise RuntimeError('Experiment cap reached before dispatch')
            ledger['calls'] += 1
            ledger['reserved_usd'] = round(ledger['reserved_usd'] + reserve, 4)
            ledger['entries'].append({'case': case['id'], 'variant': args.variant,
                                      'reserve_usd': reserve, 'out': str(args.out)})
            ledger_path.write_text(json.dumps(ledger, indent=2)+'\n')
            record = {'case':case['id'], 'source_image':case['image'],
                      'image_sha256':digest(Path(case['image']).read_bytes()),
                      'submitted_image_sha256':digest(image), 'resized':resized,
                      'prompt_sha256':digest(prompt.encode()), 'variant':args.variant}
            started = time.monotonic()
            try:
                raw, _, _ = _call_vision_model(
                    model, prompt, USER_TEXT,
                    'data:'+mime+';base64,'+base64.b64encode(image).decode(),
                    0.0, 8192, openai_client=SimpleNamespace(responses=RecordingResponses(client,record,args.image_detail)),
                )
                raw = _extract_code_fence(raw)
                raw, *_ = _extract_ocr_metadata(raw)
                raw_path.write_text(raw)
                clean_path.write_text(sanitize_html(raw))
            finally:
                record['elapsed_seconds'] = time.monotonic()-started
                record_path.write_text(json.dumps(record, indent=2)+'\n')
        golden = Path(case['golden']).read_text()
        raw_score = compare_tables(golden, raw_path.read_text(), table_index=case.get('table_index'))
        clean_score = compare_tables(golden, clean_path.read_text(), table_index=case.get('table_index'))
        scores.append({'case':case['id'],'raw':raw_score,'sanitized':clean_score})
        print(json.dumps({'case':case['id'],'variant':args.variant,
                          'raw_pass':raw_score['pass'],'sanitized_pass':clean_score['pass'],
                          'text_errors':clean_score['text_mismatch_count'],
                          'structure_errors':clean_score['structure_mismatch_count']}),flush=True)
    (args.out/'scores.json').write_text(json.dumps(scores, indent=2)+'\n')
    (args.out/'prompt.txt').write_text(prompt)


if __name__ == '__main__':
    main()
