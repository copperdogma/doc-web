"""Offline guard tests: reservation before network and unknown billing retained."""

import importlib.util
import json
from pathlib import Path

import httpx
import pytest

SPEC = importlib.util.spec_from_file_location(
    "guard",
    Path(__file__).resolve().parents[1]
    / "benchmarks/providers/gpt6_image_rerun_guard.py",
)
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)


@pytest.fixture
def campaign(tmp_path, monkeypatch):
    monkeypatch.setattr(guard, "RESULTS", tmp_path)
    guard.write(tmp_path / "ledger.json", {"cap_usd": 2.5, "spent_usd": 0, "calls": []})
    return tmp_path


def request():
    return httpx.Request(
        "POST",
        "https://api.openai.com/v1/responses",
        json={
            "model": "gpt-6-sol",
            "store": False,
            "max_output_tokens": 4096,
            "input": [
                {
                    "content": [
                        {
                            "type": "input_image",
                            "image_url": "data:image/png;base64,AAA=",
                        }
                    ]
                }
            ],
        },
    )


def test_reserve_precedes_dispatch_and_cache_writes_settle(campaign):
    def send(client, req, **kwargs):
        ledger = json.loads((campaign / "ledger.json").read_text())
        assert ledger["calls"][0]["cost_usd"] is None
        assert ledger["calls"][0]["reserved_usd"] > 0
        return httpx.Response(
            200,
            json={
                "model": "gpt-6-sol",
                "usage": {
                    "input_tokens": 1000,
                    "output_tokens": 10,
                    "input_tokens_details": {
                        "cached_tokens": 200,
                        "cache_write_tokens": 300,
                    },
                },
            },
        )

    guard.guarded_send(send, None, request())
    ledger = json.loads((campaign / "ledger.json").read_text())
    assert ledger["spent_usd"] == pytest.approx(0.00189)
    assert (campaign / "response-001.json").exists()


def test_unknown_billing_keeps_reservation(campaign):
    guard.guarded_send(
        lambda *args, **kwargs: httpx.Response(500, json={"error": "unknown"}),
        None,
        request(),
    )
    ledger = json.loads((campaign / "ledger.json").read_text())
    assert ledger["calls"][0]["cost_usd"] is None
    assert ledger["calls"][0]["reserved_usd"] > 0


def test_over_cap_stops_before_dispatch(campaign):
    ledger = json.loads((campaign / "ledger.json").read_text())
    ledger["spent_usd"] = 2.49
    guard.write(campaign / "ledger.json", ledger)
    with pytest.raises(RuntimeError, match="admission"):
        guard.guarded_send(
            lambda *args, **kwargs: pytest.fail("network dispatched"), None, request()
        )
