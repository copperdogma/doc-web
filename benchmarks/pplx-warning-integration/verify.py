"""Integrated sidecar saved-answer replay + real-driver offline artifact proof."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'benchmarks/pplx-shadow'))

OUT = ROOT / 'docs/evals/evidence/067-warning-integration'
PRIOR = OUT / 'prior'


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def deny_network(*args, **kwargs):
    raise AssertionError('Offline integration check forbids network')


def stable(value):
    if isinstance(value, dict):
        return {k: stable(v) for k, v in value.items() if k not in {'created_at', 'latency_ms'}}
    if isinstance(value, list):
        return [stable(v) for v in value]
    return value


def main():
    from modules.validate.plan_onward_document_consistency_v1 import pplx_shadow as shadow
    import campaign

    socket.socket = deny_network
    socket.create_connection = deny_network
    for item in read(OUT / 'input-manifest.json')['files']:
        assert digest(ROOT / item['path']) == item['sha256']
    ledger = read(PRIOR / 'ledger.json')
    for call in ledger['calls']:
        for suffix in ['request', 'response']:
            assert digest(PRIOR / 'native' / (call['name'] + '.' + suffix + '.json')) == call[suffix + '_sha256']
    trace = read(PRIOR / 'live-lineage.json')[0]
    folder = PRIOR / 'paid-artifacts' / trace['record']['run_id']
    for name, expected in trace['record']['canonical_sha256'].items():
        assert digest(folder / name) == expected
    calls = iter(c for c in ledger['calls'] if c['kind'] == 'candidate')
    replayed = 0

    def request(payload, ignored):
        nonlocal replayed
        call = next(calls)
        encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode()
        assert hashlib.sha256(encoded).hexdigest() == call['request_sha256']
        replayed += 1
        return read(PRIOR / 'native' / (call['name'] + '.response.json'))

    result = shadow.run_shadow(trace['compact_chapters'], read(folder / 'consistency_plan.json'),
                               read(folder / 'conformance_report.json'),
                               env={'DOC_WEB_PPLX_SHADOW_EVAL': 'enabled', 'DOC_WEB_PERPLEXITY_API_KEY': 'offline-placeholder'}, request=request)
    assert next(calls, None) is None
    original = read(folder / 'pplx_consistency_shadow_eval.json')
    assert stable(result['chapters'][:2]) == stable(original['chapters'][:2])
    old, new = original['chapters'][2], result['chapters'][2]
    assert old['shadow_status'] == 'conformant' and new['shadow_status'] == 'uncertain'
    assert new['route'] == 'review' and new['reason'] == 'low_confidence_disagreement'
    assert new['authoritative_status'] == old['authoritative_status'] == 'conformant'
    for name in ['pplx_status', 'confidence', 'probabilities', 'input_tokens', 'output_tokens', 'cost_usd']:
        assert new[name] == old[name]
    (OUT / 'saved-response-integrated.json').write_text(json.dumps(result, indent=2) + '\n')
    # Both are real driver invocations with identical fixed mock planner responses.
    off = campaign.driver('doc-01', 'offline-warning-integration', offline=True, shadow=False)
    on = campaign.driver('doc-01', 'offline-warning-integration', offline=True, shadow=True, failure='disagreement')
    assert off['canonical_sha256'] == on['canonical_sha256']
    livefolder = ROOT / on['folder']
    sidecar = read(livefolder / 'pplx_consistency_shadow_eval.json')
    assert sidecar['chapters'][0]['reason'] == 'low_confidence_disagreement'
    assert sidecar['chapters'][0]['route'] == 'review'
    authoritative = read(livefolder / 'conformance_report.json')
    assert authoritative['chapters'][0]['status'] == 'conformant'
    proof = {'provider_calls': 0, 'new_spend_usd': 0, 'native_receipt_hashes': 10,
             'saved_candidate_responses_replayed': replayed, 'unchanged_saved_canonical_artifacts': 4,
             'real_driver_off': off, 'real_driver_on': on, 'canonical_hashes_equal': True,
             'verified_warning': sidecar['chapters'][0],
             'limitations': 'Saved exposed cohort plus mocked driver proof; no fresh model quality or adoption evidence.'}
    (OUT / 'integration-proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print('PASS: integrated saved-answer warning, 10 receipt hashes, 2 native replays, real driver warning and 4 exact canonical hashes; zero network/spend')


if __name__ == '__main__':
    main()
