"""Offline campaign trust boundaries; no inference."""

import importlib.util
import json
from pathlib import Path
import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(path, name):
    s = importlib.util.spec_from_file_location(name, ROOT / path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def body():
    return {
        "model": "anthropic/claude-fable-5.2",
        "max_tokens": 32768,
        "reasoning": {"effort": "xhigh"},
        "messages": [],
        "provider": {
            "only": ["anthropic"],
            "allow_fallbacks": False,
            "require_parameters": True,
            "max_price": {"prompt": 8, "completion": 40},
        },
    }


def test_hard_cap_counts_unknown_exposure(tmp_path, monkeypatch):
    g = load("benchmarks/providers/fable52_guard.py", "fable52_test_guard")
    monkeypatch.setattr(g, "RESULTS", tmp_path)
    monkeypatch.setattr(g, "E", tmp_path / "durable")
    monkeypatch.setenv("FABLE52_STAGE", "native-table")
    (tmp_path / "ledger.json").write_text(
        json.dumps(
            {
                "spent_usd": 29.8,
                "closed": False,
                "calls": [{"stage": "unknown", "reserved_usd": 0.2, "cost_usd": None}],
            }
        )
    )
    with pytest.raises(RuntimeError, match="hard30USD"):
        g.send(
            lambda *a, **k: pytest.fail("network"),
            None,
            httpx.Request(
                "POST", "https://openrouter.ai/api/v1/chat/completions", json=body()
            ),
        )


def test_route_and_price_required_before_dispatch(monkeypatch):
    g = load("benchmarks/providers/fable52_guard.py", "fable52_route_guard")
    monkeypatch.setenv("FABLE52_STAGE", "native-table")
    b = body()
    b["provider"]["max_price"]["completion"] = 2
    with pytest.raises(AssertionError):
        g.send(
            lambda *a, **k: pytest.fail("network"),
            None,
            httpx.Request(
                "POST", "https://openrouter.ai/api/v1/chat/completions", json=b
            ),
        )


def test_raw_envelope_retained_before_wrong_identity(tmp_path, monkeypatch):
    m = load("benchmarks/scripts/fable52_reading.py", "fable52_test_runner")
    monkeypatch.setattr(m, "R", tmp_path)
    monkeypatch.setattr(m.guard, "install", lambda: None)
    monkeypatch.setenv("OPENROUTER_API_KEY", "offline-placeholder")
    d = {
        "model": "wrong",
        "usage": {"prompt_tokens": 1, "completion_tokens": 2},
        "choices": [{"finish_reason": "stop", "message": {"content": "kept"}}],
    }

    class R:
        def json(self):
            return d

        def raise_for_status(self):
            return None

    monkeypatch.setattr(m.httpx, "post", lambda *a, **k: R())
    with pytest.raises(AssertionError):
        m.google(
            "anthropic/claude-fable-5.2", "", "read", b"original", stage="native-ocr"
        )
    assert json.loads((tmp_path / "native-ocr-decoded.json").read_text()) == d


def test_native_body_keeps_selected_effort_schema_and_source(monkeypatch):
    m = load("benchmarks/scripts/fable52_native.py", "fable52_native_test")
    schema = {
        "type": "object",
        "properties": {
            "bbox": {
                "type": "array",
                "items": {"type": "number"},
                "minItems": 4,
                "maxItems": 4,
            }
        },
        "required": ["bbox"],
        "additionalProperties": False,
    }
    b = m.body(
        "frozen policy", "frozen prompt", b"original pixels", "image/png", schema
    )
    assert b["model"] == "claude-fable-5-2"
    assert b["max_tokens"] == 32768 and b["output_config"]["effort"] == "xhigh"
    assert "temperature" not in b and b["system"] == "frozen policy"
    import base64

    assert (
        base64.b64decode(b["messages"][0]["content"][1]["source"]["data"])
        == b"original pixels"
    )
    assert b["output_config"]["format"]["type"] == "json_schema"
    assert schema["properties"]["bbox"]["minItems"] == 4


def test_http_error_without_usage_retains_unknown_reservation(tmp_path, monkeypatch):
    g = load("benchmarks/providers/fable52_guard.py", "fable52_error_guard")
    monkeypatch.setattr(g, "RESULTS", tmp_path)
    monkeypatch.setattr(g, "E", tmp_path / "durable")
    monkeypatch.setattr(g, "ROOT", tmp_path)
    monkeypatch.setenv("FABLE52_STAGE", "error-retention")
    (tmp_path / "ledger.json").write_text(
        json.dumps({"spent_usd": 0, "closed": False, "calls": []})
    )
    req = httpx.Request(
        "POST", "https://openrouter.ai/api/v1/chat/completions", json=body()
    )
    g.send(
        lambda *a, **k: httpx.Response(402, json={"error": {"code": 402}}, request=req),
        None,
        req,
    )
    ledger = json.loads((tmp_path / "ledger.json").read_text())
    assert ledger["calls"][0]["cost_usd"] is None
    assert ledger["calls"][0]["reserved_usd"] > 0
    assert (tmp_path / "durable" / "response-001.json").exists()
