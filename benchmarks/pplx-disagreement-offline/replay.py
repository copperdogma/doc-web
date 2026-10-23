"""Offline routing experiment using frozen synthetic native receipts; no providers."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/evals/evidence/066-offline-disagreement'
PRIOR = OUT / 'prior'
THRESHOLD = 0.8  # Original frozen threshold, never fitted to this exposed screen.
LABELS = {'conformant', 'format_drift', 'row_semantic_issue', 'mixed', 'uncertain'}


def disagreement_to_review(row):
    """Preserve valid low-confidence disagreement as review, not a new verdict."""
    result = deepcopy(row)
    confidence = row.get('confidence')
    candidate = row.get('pplx_status')
    authoritative = row.get('authoritative_status')
    if (
        row.get('route') == 'planner_fallback'
        and row.get('reason') == 'low_confidence'
        and candidate in LABELS
        and authoritative in LABELS
        and candidate != authoritative
        and type(confidence) in (int, float)
        and math.isfinite(confidence)
        and 0 <= confidence < THRESHOLD
    ):
        result.update(
            shadow_status='uncertain',
            route='review',
            reason='low_confidence_disagreement',
            warning={
                'candidate_status': candidate,
                'authoritative_status': authoritative,
                'confidence': confidence,
            },
        )
    return result


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable(value):
    if isinstance(value, dict):
        return {k: stable(v) for k, v in value.items() if k not in {'created_at', 'latency_ms'}}
    if isinstance(value, list):
        return [stable(v) for v in value]
    return value


def deny_network(*args, **kwargs):
    raise AssertionError('Offline-only experiment forbids network access')


def main():
    # Fail closed if any accidental native default transport is invoked.
    manifest = read(OUT / 'input-manifest.json')
    for item in manifest['files']:
        assert digest(ROOT / item['path']) == item['sha256'], item['path']
    frozen_module = PRIOR / 'snapshots/modules/validate/plan_onward_document_consistency_v1/pplx_shadow.py'
    spec = importlib.util.spec_from_file_location('frozen_paid_shadow', frozen_module)
    shadow = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = shadow
    spec.loader.exec_module(shadow)
    socket.socket = deny_network
    socket.create_connection = deny_network
    ledger = read(PRIOR / 'ledger.json')
    assert ledger['closed'] and ledger['unknown_usd'] == 0
    golds = {(r['document'], r['chapter']): r['gold'] for r in read(PRIOR / 'results.json')}
    rows = []
    canonical_count = 0
    receipt_count = 0
    for call in ledger['calls']:
        for suffix in ['request', 'response']:
            assert digest(PRIOR / 'native' / (call['name'] + '.' + suffix + '.json')) == call[suffix + '_sha256']
            receipt_count += 1
    replay_count = 0
    for trace in read(PRIOR / 'live-lineage.json'):
        rec = trace['record']
        folder = PRIOR / 'paid-artifacts' / rec['run_id']
        canonical_before = {name: digest(folder / name) for name in rec['canonical_sha256']}
        assert canonical_before == rec['canonical_sha256']
        calls = iter(c for c in ledger['calls'] if c['kind'] == 'candidate' and c['run_id'] == rec['run_id'])

        def request(payload, ignored_key):
            nonlocal replay_count
            call = next(calls)
            encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode()
            assert hashlib.sha256(encoded).hexdigest() == call['request_sha256']
            replay_count += 1
            return read(PRIOR / 'native' / (call['name'] + '.response.json'))

        original = shadow.run_shadow(
            trace['compact_chapters'], read(folder / 'consistency_plan.json'),
            read(folder / 'conformance_report.json'),
            env={'DOC_WEB_PPLX_SHADOW_EVAL': 'enabled', 'DOC_WEB_PERPLEXITY_API_KEY': 'offline-placeholder'},
            request=request,
        )
        assert next(calls, None) is None
        assert stable(original) == stable(read(folder / 'pplx_consistency_shadow_eval.json'))
        unchanged = deepcopy(original)
        for i, row in enumerate(original['chapters'], 1):
            chapter = f'chapter-{i:03d}.html'
            rows.append({
                'document': rec['document'], 'chapter': chapter,
                'gold': golds[(rec['document'], chapter)],
                'original': row, 'proposed': disagreement_to_review(row),
            })
        assert original == unchanged
        assert canonical_before == {name: digest(folder / name) for name in canonical_before}
        canonical_count += len(canonical_before)
    metrics = {}
    for arm in ['original', 'proposed']:
        metrics[arm] = {
            'exact_labels': sum(r[arm]['shadow_status'] == r['gold'] for r in rows),
            'unsafe_clean': sum(r[arm]['shadow_status'] == 'conformant' and r['gold'] != 'conformant' for r in rows),
            'review_routes': sum(r[arm]['route'] == 'review' for r in rows),
            'determinate_outputs': sum(r[arm]['shadow_status'] != 'uncertain' for r in rows),
            'candidate_accepted': sum(r[arm]['route'] == 'pplx' for r in rows),
        }
    result = {
        'status': 'offline_exploratory_replay_only', 'provider_calls': 0, 'new_spend_usd': 0,
        'source_observations': len(rows), 'source_unique_documents': 1,
        'native_receipts_verified': receipt_count, 'candidate_responses_replayed': replay_count,
        'canonical_artifacts_unchanged': canonical_count, 'metrics': metrics, 'rows': rows,
        'interpretation': 'Observed warning preserved as review; no new semantic correction, fresh quality proof, runtime integration or promotion.',
        'limits': 'Post-hoc policy on exposed first-document screen. Fifteen unique cases and all second repeats remain unmeasured. Synthetic boundary tests do not supply new model answers.',
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'rows'}, indent=2))


if __name__ == '__main__':
    main()
