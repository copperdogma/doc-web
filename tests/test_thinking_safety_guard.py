"""Offline transport and cap checks for GPT-6.1 evaluation custody."""

import json

import httpx
import pytest

from benchmarks.providers import thinking_safety_guard as guard


@pytest.fixture(autouse=True)
def restore_transport_after_test(monkeypatch):
    # The campaign intercept is process-wide; never leak it into other guard tests.
    monkeypatch.setattr(httpx.Client, "send", httpx.Client.send)
    try:
        import httpx2
    except ImportError:
        pass
    else:
        monkeypatch.setattr(httpx2.Client, "send", httpx2.Client.send)


def test_actual_httpx_send_intercept_retains_receipts(tmp_path, monkeypatch):
    monkeypatch.setattr(guard, "RESULTS", tmp_path)
    guard.write(
        tmp_path / "ledger.json",
        {"cap_usd": 14, "spent_usd": 0, "calls": [], "closed": False},
    )

    def responder(request):
        return httpx.Response(
            200,
            json={
                "id": "resp_test",
                "model": "gpt-6.1-sol",
                "status": "completed",
                "usage": {"input_tokens": 30, "output_tokens": 5},
                "output": [],
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(responder))
    body = {
        "model": "gpt-6.1-sol",
        "max_output_tokens": 4096,
        "store": False,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "probe"},
                    {"type": "input_image", "image_url": "data:image/png;base64,AAAA"},
                ],
            }
        ],
    }
    guard.install()
    client.post("https://api.openai.com/v1/responses", json=body)
    ledger = json.loads((tmp_path / "ledger.json").read_text())
    assert len(ledger["calls"]) == 1
    assert ledger["calls"][0]["cost_usd"] == (30 * 2 + 5 * 10) / 1e6
    assert ledger["calls"][0]["reserved_usd"] == (26000 * 2.5 + 4096 * 10) / 1e6
    assert (tmp_path / "request-001.json").is_file()
    assert (tmp_path / "response-001.json").is_file()


def test_cap_denial_before_actual_httpx_transport(tmp_path, monkeypatch):
    monkeypatch.setattr(guard, "RESULTS", tmp_path)
    guard.write(
        tmp_path / "ledger.json",
        {"cap_usd": 0.01, "spent_usd": 0, "calls": [], "closed": False},
    )
    reached = []
    client = httpx.Client(
        transport=httpx.MockTransport(lambda request: reached.append(request))
    )
    guard.install()
    with pytest.raises(RuntimeError, match="admission denied"):
        client.post(
            "https://api.openai.com/v1/responses",
            json={
                "model": "gpt-6.1-sol",
                "max_output_tokens": 4096,
                "store": False,
                "input": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_image",
                                "image_url": "data:image/png;base64,AAAA",
                            }
                        ],
                    }
                ],
            },
        )
    assert reached == []
    assert json.loads((tmp_path / "ledger.json").read_text())["calls"] == []


def test_unknown_usage_preserves_full_reservation(tmp_path, monkeypatch):
    monkeypatch.setattr(guard, "RESULTS", tmp_path)
    guard.write(
        tmp_path / "ledger.json",
        {"cap_usd": 14, "spent_usd": 0, "calls": [], "closed": False},
    )
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                503, json={"error": {"message": "unavailable"}}
            )
        )
    )
    guard.install()
    client.post(
        "https://api.openai.com/v1/responses",
        json={
            "model": "gpt-6-luna",
            "max_output_tokens": 4096,
            "store": False,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_image",
                            "image_url": "data:image/png;base64,AAAA",
                        },
                        {
                            "type": "input_image",
                            "image_url": "data:image/png;base64,AAAA",
                        },
                    ],
                }
            ],
        },
    )
    record = json.loads((tmp_path / "ledger.json").read_text())["calls"][0]
    assert record["cost_usd"] is None
    assert record["reserved_usd"] == 0.007798
    assert record["billing_unresolved"]
    assert (tmp_path / "response-001.json").exists()
