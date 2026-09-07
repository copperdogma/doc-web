"""Offline spend-boundary checks for the one approved campaign."""

import importlib.util
import json
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "qwen0902_budgeted",
    Path(__file__).parents[1] / "benchmarks/providers/qwen0902_budgeted.py",
)
provider = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(provider)


@pytest.fixture
def setup_guard(tmp_path, monkeypatch):
    result = tmp_path / "results"
    result.mkdir()
    monkeypatch.setattr(provider, "ROOT", tmp_path)
    monkeypatch.setattr(provider, "RESULTS", result)
    ledger = result / "ledger.json"
    ledger.write_text(json.dumps({"cap_usd": 0.75, "spent_usd": 0, "calls": []}))
    return ledger


@pytest.mark.parametrize("cost", [float("inf"), float("nan"), -1, True, None])
def test_bad_cost_blocks_next_call(setup_guard, monkeypatch, cost):
    class Response:
        status_code = 200

        def json(self):
            return {"usage": {"cost": cost}}

    monkeypatch.setattr(provider, "_REAL_POST", lambda *a, **k: Response())
    provider.recorded_post("fake", json={"max_tokens": 1024})
    assert json.loads(setup_guard.read_text())["unresolved_cost"]
    with pytest.raises(RuntimeError, match="unresolved"):
        provider.recorded_post("fake", json={"max_tokens": 1024})


def test_budget_stops_before_network(setup_guard, monkeypatch):
    d = json.loads(setup_guard.read_text())
    d["spent_usd"] = 0.74
    setup_guard.write_text(json.dumps(d))

    def forbidden(*a, **k):
        raise AssertionError("network must not be reached")

    monkeypatch.setattr(provider, "_REAL_POST", forbidden)
    with pytest.raises(RuntimeError, match="budget guard"):
        provider.recorded_post("fake", json={"max_tokens": 1024})


def test_network_failure_leaves_fail_closed_intent(setup_guard, monkeypatch):
    def fail(*a, **k):
        raise TimeoutError("offline simulated timeout")

    monkeypatch.setattr(provider, "_REAL_POST", fail)
    with pytest.raises(TimeoutError):
        provider.recorded_post("fake", json={"max_tokens": 1024})
    assert json.loads(setup_guard.read_text())["unresolved_cost"]
