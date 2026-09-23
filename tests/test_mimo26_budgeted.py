import importlib.util
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "benchmarks/providers"))

SPEC = importlib.util.spec_from_file_location("mimo26_budgeted", Path(__file__).parents[1] / "benchmarks/providers/mimo26_budgeted.py")
provider = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(provider)


def test_capacity_response_stops_a_second_network_attempt(tmp_path, monkeypatch):
    results = tmp_path / "results"; results.mkdir()
    monkeypatch.setattr(provider, "ROOT", tmp_path)
    monkeypatch.setattr(provider, "RESULTS", results)
    (results / "ledger.json").write_text(json.dumps({"cap_usd": .5, "spent_usd": 0, "unresolved_cost": False, "calls": []}))
    calls = []
    class Response:
        status_code = 429
        text = '{"error":"capacity"}'
        def json(self): return {"error": {"code": 429}}
    monkeypatch.setattr(provider, "_REAL_POST", lambda *a, **k: calls.append(1) or Response())
    provider.recorded_post("x", json={"max_tokens": 2048})
    try:
        provider.recorded_post("x", json={"max_tokens": 2048})
    except RuntimeError as exc:
        assert "unresolved" in str(exc)
    else:
        raise AssertionError("terminal capacity stop must block a second request")
    assert calls == [1]
