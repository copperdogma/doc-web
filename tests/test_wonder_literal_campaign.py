"""Campaign admission and custody, no provider traffic."""

import json
import httpx
import pytest
from benchmarks.scripts import wonder_literal_campaign as c


@pytest.fixture
def guarded(tmp_path, monkeypatch):
    monkeypatch.setattr(c, "R", tmp_path)
    monkeypatch.setattr(c, "ROOT", tmp_path)
    monkeypatch.setenv("WONDER_STAGE", "test")
    c.save(
        tmp_path / "ledger.json",
        {"cap_usd": 10, "spent_usd": 0, "calls": [], "closed": False},
    )
    return tmp_path


def request():
    return httpx.Request(
        "POST",
        "https://openrouter.ai/api/v1/chat/completions",
        json={"model": "meta/muse-wonder"},
    )


def test_unknown_exposure_denies_before_post(guarded):
    c.save(
        guarded / "ledger.json",
        {
            "spent_usd": 0,
            "calls": [{"stage": "unknown", "reserved_usd": 6, "cost_usd": None}],
            "closed": False,
        },
    )
    with pytest.raises(RuntimeError, match="admission denied"):
        c.send(lambda *a, **k: pytest.fail("POST"), None, request())
    assert not (guarded / "request-002.json").exists()


def test_existing_response_denies_without_overwrite(guarded):
    p = guarded / "response-001.json"
    p.write_text("keep")
    with pytest.raises(RuntimeError, match="collision"):
        c.send(lambda *a, **k: pytest.fail("POST"), None, request())
    assert p.read_text() == "keep"


def test_transport_unknown_retains_reserved_intent(guarded):
    def fail(*a, **k):
        raise TimeoutError()

    with pytest.raises(TimeoutError):
        c.send(fail, None, request())
    ledger = json.loads((guarded / "ledger.json").read_text())
    assert (
        ledger["calls"][0]["cost_usd"] is None
        and ledger["calls"][0]["reserved_usd"] == 4.849664
    )
    assert (guarded / "request-001.json").exists()


def test_raw_preserved_before_missing_usage_parse(guarded):
    raw = b'{"error":{"message":"capacity"}}'
    result = c.send(lambda *a, **k: httpx.Response(503, content=raw), None, request())
    assert (
        result.status_code == 503
        and (guarded / "response-001.json").read_bytes() == raw
    )
    ledger = json.loads((guarded / "ledger.json").read_text())
    assert (
        ledger["calls"][0]["billing_unresolved"]
        and ledger["calls"][0]["cost_usd"] is None
    )
