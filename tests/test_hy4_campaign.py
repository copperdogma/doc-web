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
        "model": "tencent/hy4",
        "max_tokens": 32768,
        "reasoning": {"effort": "high"},
        "messages": [],
        "provider": {
            "only": ["tencent"],
            "allow_fallbacks": False,
            "require_parameters": True,
            "max_price": {"prompt": 0.417, "completion": 1.2505},
        },
    }


def test_hard_cap_counts_unknown_exposure(tmp_path, monkeypatch):
    g = load("benchmarks/providers/hy4_guard.py", "hy4_test_guard")
    monkeypatch.setattr(g, "RESULTS", tmp_path)
    monkeypatch.setenv("HY4_STAGE", "native-table")
    (tmp_path / "ledger.json").write_text(
        json.dumps(
            {
                "spent_usd": 4.8,
                "closed": False,
                "calls": [{"stage": "unknown", "reserved_usd": 0.2, "cost_usd": None}],
            }
        )
    )
    with pytest.raises(RuntimeError, match="hard5USD"):
        g.send(
            lambda *a, **k: pytest.fail("network"),
            None,
            httpx.Request(
                "POST", "https://openrouter.ai/api/v1/chat/completions", json=body()
            ),
        )


def test_route_and_price_required_before_dispatch(monkeypatch):
    g = load("benchmarks/providers/hy4_guard.py", "hy4_route_guard")
    monkeypatch.setenv("HY4_STAGE", "native-table")
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
    m = load("benchmarks/scripts/hy4_reading.py", "hy4_test_runner")
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
        m.google("tencent/hy4", "", "read", b"original", stage="native-ocr")
    assert json.loads((tmp_path / "native-ocr-decoded.json").read_text()) == d
