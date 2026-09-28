import importlib.util
import json
from pathlib import Path
import httpx
import pytest

P = Path(__file__).resolve().parents[1] / "benchmarks/providers/sonnet55_guard.py"
spec = importlib.util.spec_from_file_location("sonnet_guard", P)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


@pytest.mark.parametrize("library", ["httpx", "httpx2"])
def test_guard_intercepts_actual_transport_and_retains_full_pair(
    tmp_path, monkeypatch, library
):
    lib = pytest.importorskip(library)
    monkeypatch.setattr(g, "RESULTS", tmp_path)
    g.write(
        tmp_path / "ledger.json",
        {"cap_usd": 5, "spent_usd": 0, "calls": [], "closed": False},
    )
    g.install()
    response = {
        "model": "claude-sonnet-5-5",
        "id": "test",
        "usage": {"input_tokens": 10, "output_tokens": 5},
        "stop_reason": "end_turn",
    }
    transport = lib.MockTransport(lambda req: lib.Response(200, json=response))
    with lib.Client(transport=transport) as client:
        client.post(
            "https://api.anthropic.com/v1/messages",
            json={
                "model": "claude-sonnet-5-5",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": "WA==",
                                },
                            }
                        ],
                    }
                ],
            },
        )
    d = json.loads((tmp_path / "ledger.json").read_text())
    assert len(d["calls"]) == 1
    assert d["calls"][0]["cost_usd"] == 0.00007
    assert json.loads((tmp_path / "response-001.json").read_text()) == response
    assert (tmp_path / "request-001.json").exists()


def test_guard_refuses_call_before_transport_when_cap_full(tmp_path, monkeypatch):
    monkeypatch.setattr(g, "RESULTS", tmp_path)
    g.write(
        tmp_path / "ledger.json",
        {"cap_usd": 0, "spent_usd": 0, "calls": [], "closed": False},
    )
    request = httpx.Request(
        "POST",
        "https://api.anthropic.com/v1/messages",
        json={
            "model": "claude-sonnet-5-5",
            "max_tokens": 4096,
            "messages": [{"content": [{"type": "image"}]}],
        },
    )
    with pytest.raises(RuntimeError, match="admission denied"):
        g.guarded_send(lambda *a, **k: pytest.fail("transport called"), None, request)
