"""Offline trust-boundary checks for the bounded Scout103 evaluation tooling."""
import importlib.util
import json
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_unknown_model_is_denied_before_dispatch():
    guard = module('benchmarks/providers/scout103_guard.py', 'guard1')
    request = httpx.Request('POST', 'https://api.openai.com/v1/responses',
                            json={'model': 'other-model'})
    with pytest.raises(RuntimeError, match='unapproved requested model'):
        guard.send(lambda *a, **kw: pytest.fail('network dispatch'), None, request)


def test_hard_cap_counts_unknown_exposure(tmp_path, monkeypatch):
    guard = module('benchmarks/providers/scout103_guard.py', 'guard2')
    monkeypatch.setattr(guard, 'RESULTS', tmp_path)
    monkeypatch.setenv('SCOUT103_STAGE', 'native-table')
    (tmp_path / 'ledger.json').write_text(json.dumps({
        'spent_usd': 11.7, 'closed': False,
        'calls': [{'stage': 'unknown-call', 'reserved_usd': .3, 'cost_usd': None}],
    }))
    request = httpx.Request('POST', 'https://api.openai.com/v1/responses', json={
        'model': 'gpt-6.1-terra', 'max_output_tokens': 32768,
        'reasoning': {'effort': 'high'}, 'store': False,
        'service_tier': 'default', 'input': [],
    })
    with pytest.raises(RuntimeError, match='hard12USD cap'):
        guard.send(lambda *a, **kw: pytest.fail('network dispatch'), None, request)


def test_full_response_persists_before_exact_identity_rejection(tmp_path, monkeypatch):
    runner = module('benchmarks/scripts/scout103_reading.py', 'runner1')
    monkeypatch.setattr(runner, 'R', tmp_path)
    monkeypatch.setenv('OPENAI_API_KEY', 'offline-placeholder')
    monkeypatch.setattr(runner.guard, 'install', lambda: None)
    payload = {'model': 'wrong-served-model', 'status': 'completed',
               'output': [{'type': 'message', 'content': [
                   {'type': 'output_text', 'text': '<p>kept fully</p>'}]}],
               'usage': {'input_tokens': 1, 'output_tokens': 2}, 'id': 'offline'}
    class Response:
        def json(self):
            return payload
        def raise_for_status(self):
            return None
    monkeypatch.setattr(runner.httpx, 'post', lambda *a, **kw: Response())
    with pytest.raises(AssertionError):
        runner.google('gpt-6.1-terra', '', 'read', b'original bytes', stage='native-ocr')
    assert json.loads((tmp_path / 'native-ocr-decoded.json').read_text()) == payload
