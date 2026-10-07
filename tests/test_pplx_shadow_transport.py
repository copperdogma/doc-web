"""Pre-dispatch budget and wire controls; all tests refuse networking."""

import importlib.util
from pathlib import Path
import pytest

PATH = Path(__file__).resolve().parents[1] / "benchmarks/pplx-shadow/runtime_support.py"
spec = importlib.util.spec_from_file_location("pplx_transport_test", PATH)
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)


def payload():
    return {
        "model": support.MODEL,
        "max_tokens": 8000,
        "response_format": {"type": "json_object"},
        "messages": [],
    }


@pytest.mark.parametrize(
    "change",
    [
        {"max_tokens": 8001},
        {"max_completion_tokens": 8001},
        {"max_tokens": True},
        {"max_tokens": 0},
        {"stream": True},
        {"n": 2},
        {"response_format": {"type": "text"}},
    ],
)
def test_output_contract_refuses_before_send(tmp_path, monkeypatch, change):
    monkeypatch.setattr(support, "RAW", tmp_path / "raw")
    monkeypatch.setattr(support, "EVIDENCE", tmp_path / "evidence")
    monkeypatch.setattr(support, "REAL_OPEN", lambda *a, **k: pytest.fail("network"))
    p = payload()
    p.update(change)
    with pytest.raises(RuntimeError, match="reservation mismatch"):
        support.send(p, "planner")
    assert not (support.EVIDENCE / "ledger.json").exists()


@pytest.mark.parametrize(
    "state,reason",
    [
        ({"unknown_usd": 0.01, "spent_usd": 0}, "unknown delivery"),
        ({"unknown_usd": 0, "spent_usd": 3.9}, "HardUSD4"),
        ({"unknown_usd": 0, "spent_usd": 0, "closed": True}, "closed"),
        (
            {"unknown_usd": 0, "spent_usd": 0, "calls": [{"kind": "planner"}] * 12},
            "request count",
        ),
    ],
)
def test_ledger_stops_before_dispatch(tmp_path, monkeypatch, state, reason):
    monkeypatch.setattr(support, "RAW", tmp_path / "raw")
    monkeypatch.setattr(support, "EVIDENCE", tmp_path / "evidence")
    monkeypatch.setattr(support, "REAL_OPEN", lambda *a, **k: pytest.fail("network"))
    ledger = {"cap_usd": 4, "spent_usd": 0, "unknown_usd": 0, "calls": []}
    ledger.update(state)
    support.write(support.EVIDENCE / "ledger.json", ledger)
    with pytest.raises(RuntimeError, match=reason):
        support.send(payload(), "planner")
    assert not list(support.RAW.glob("*.request.json"))
