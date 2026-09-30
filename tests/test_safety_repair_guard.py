"""Offline proof of Attempt048 count, money, and raw receipt custody."""

import json

import httpx
import pytest

from benchmarks.providers import safety_repair_guard as guard
from benchmarks.providers import openai_responses_model as owner


@pytest.fixture(autouse=True)
def isolate_guard(tmp_path, monkeypatch):
    monkeypatch.setattr(httpx.Client, "send", httpx.Client.send)
    try:
        import httpx2

        monkeypatch.setattr(httpx2.Client, "send", httpx2.Client.send)
    except ImportError:
        pass
    monkeypatch.setattr(guard, "RESULTS", tmp_path)
    guard.write(
        tmp_path / "ledger.json",
        {"cap_usd": 18, "spent_usd": 0, "calls": [], "closed": False},
    )


def body():
    prompt = json.dumps(
        [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "synthetic contract"},
                    {"type": "input_image", "image_url": "data:image/png;base64,AAAA"},
                    {"type": "input_image", "image_url": "data:image/png;base64,AAAA"},
                ],
            }
        ]
    )
    return owner._build_body(
        prompt,
        {
            "config": {
                "model": "gpt-6-luna",
                "reasoning_effort": "medium",
                "max_output_tokens": 4096,
                "output_contract": "page_context_validation",
            }
        },
    )


def test_receipts_retained_and_complete_usage_settles():
    def responder(request):
        assert (guard.RESULTS / "request-001.json").exists()
        assert (
            json.loads((guard.RESULTS / "ledger.json").read_text())["calls"][0][
                "cost_usd"
            ]
            is None
        )
        return httpx.Response(
            200,
            json={
                "model": "gpt-6-luna",
                "status": "completed",
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 20,
                    "input_tokens_details": {"cache_write_tokens": 100},
                },
            },
        )

    guard.install()
    httpx.Client(transport=httpx.MockTransport(responder)).post(
        "https://api.openai.com/v1/responses", json=body()
    )
    ledger = json.loads((guard.RESULTS / "ledger.json").read_text())
    assert ledger["spent_usd"] == (100 * 0.125 + 20 * 0.5) / 1e6
    assert ledger["calls"][0]["reserved_usd"] == 0.007798
    assert (guard.RESULTS / "response-001.json").exists()


def test_unknown_usage_keeps_entire_reservation():
    guard.install()
    httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(503, json={"error": "capacity"})
        )
    ).post("https://api.openai.com/v1/responses", json=body())
    ledger = json.loads((guard.RESULTS / "ledger.json").read_text())
    assert ledger["spent_usd"] == 0
    assert ledger["calls"][0]["cost_usd"] is None
    assert ledger["calls"][0]["reserved_usd"] == 0.007798


def test_quota_closes_ledger_and_second_dispatch_never_reaches_transport():
    reached = []

    def responder(request):
        reached.append(request)
        return httpx.Response(
            429,
            json={
                "error": {
                    "type": "insufficient_quota",
                    "code": "credit_balance_exhausted",
                }
            },
        )

    guard.install()
    client = httpx.Client(transport=httpx.MockTransport(responder))
    client.post("https://api.openai.com/v1/responses", json=body())
    ledger = json.loads((guard.RESULTS / "ledger.json").read_text())
    assert ledger["closed"]
    assert ledger["calls"][0]["cost_usd"] is None
    with pytest.raises(RuntimeError, match="Duplicate subject dispatch denied"):
        client.post("https://api.openai.com/v1/responses", json=body())
    assert len(reached) == 1


def test_continuation_consumes_final_recovery_and_denies_another(monkeypatch):
    monkeypatch.setenv("SAFETY_REPAIR_RECOVERY", "1")
    ledger = json.loads((guard.RESULTS / "ledger.json").read_text())
    ledger["spent_usd"] = 0.40784125
    ledger["calls"] = [
        {"model": "gpt-6-luna", "recovery": False, "cost_usd": 0} for _ in range(21)
    ] + [
        {
            "model": "gpt-6-luna",
            "recovery": False,
            "cost_usd": None,
            "reserved_usd": 0.007798,
        },
        {
            "model": "gpt-6-luna",
            "recovery": True,
            "cost_usd": None,
            "reserved_usd": 0.007798,
        },
    ]
    guard.write(guard.RESULTS / "ledger.json", ledger)
    reached = []

    def responder(request):
        reached.append(request)
        return httpx.Response(
            200,
            json={
                "model": "gpt-6-luna",
                "status": "completed",
                "usage": {"input_tokens": 100, "output_tokens": 20},
            },
        )

    guard.install()
    client = httpx.Client(transport=httpx.MockTransport(responder))
    client.post("https://api.openai.com/v1/responses", json=body())
    with pytest.raises(RuntimeError, match="Call/recovery admission denied"):
        client.post("https://api.openai.com/v1/responses", json=body())
    assert len(reached) == 1


@pytest.mark.parametrize("mode", ["dollar", "planned", "recovery"])
def test_admission_denied_before_http_transport(mode, monkeypatch):
    ledger = {
        "cap_usd": 0.001 if mode == "dollar" else 18,
        "spent_usd": 0,
        "calls": [],
        "closed": False,
    }
    if mode == "planned":
        ledger["calls"] = [{"recovery": False, "cost_usd": 0} for _ in range(105)]
    if mode == "recovery":
        monkeypatch.setenv("SAFETY_REPAIR_RECOVERY", "1")
        ledger["calls"] = [{"recovery": True, "cost_usd": 0} for _ in range(2)]
    guard.write(guard.RESULTS / "ledger.json", ledger)
    reached = []
    client = httpx.Client(
        transport=httpx.MockTransport(lambda request: reached.append(request))
    )
    guard.install()
    with pytest.raises(RuntimeError, match="admission denied"):
        client.post("https://api.openai.com/v1/responses", json=body())
    assert reached == []
