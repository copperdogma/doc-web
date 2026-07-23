import importlib.util
import json
from pathlib import Path

import httpx


PROVIDER_PATH = (
    Path(__file__).parents[1] / "benchmarks" / "providers" / "moonshot_kimi_chat.py"
)
SPEC = importlib.util.spec_from_file_location("moonshot_kimi_chat", PROVIDER_PATH)
assert SPEC and SPEC.loader
provider = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(provider)


def test_k3_body_uses_reasoning_effort_without_legacy_thinking(monkeypatch):
    monkeypatch.setenv("MOONSHOT_KIMI_MODEL", "kimi-k3")

    body = provider._build_body('[{"role":"user","content":"hello"}]')

    assert body["model"] == "kimi-k3"
    assert body["reasoning_effort"] == "max"
    assert "thinking" not in body
    assert "temperature" not in body
    assert "top_p" not in body
    assert body["response_format"]["type"] == "json_schema"
    assert body["response_format"]["json_schema"]["strict"] is True


def test_openrouter_k3_body_uses_router_reasoning_and_parameter_gate(monkeypatch):
    monkeypatch.setenv("MOONSHOT_KIMI_API_ROUTE", "openrouter")
    monkeypatch.setenv("MOONSHOT_KIMI_MODEL", "moonshotai/kimi-k3")

    body = provider._build_body('[{"role":"user","content":"hello"}]')

    assert body["model"] == "moonshotai/kimi-k3"
    assert body["reasoning"] == {"effort": "max", "exclude": True}
    assert body["max_tokens"] == 4096
    assert "max_completion_tokens" not in body
    assert "reasoning_effort" not in body
    assert body["provider"] == {
        "allow_fallbacks": False,
        "require_parameters": True,
    }


def test_k26_body_keeps_legacy_thinking_contract(monkeypatch):
    monkeypatch.setenv("MOONSHOT_KIMI_MODEL", "kimi-k2.6")
    monkeypatch.setenv("MOONSHOT_KIMI_THINKING", "enabled")

    body = provider._build_body("hello")

    assert body["thinking"] == {"type": "enabled"}
    assert "reasoning_effort" not in body


def test_k3_cost_uses_official_model_specific_prices():
    usage = {"prompt": 1_000_000, "cached": 250_000, "completion": 100_000}

    cost = provider._estimated_cost(usage, "kimi-k3")

    assert cost == 3.825


def test_unknown_model_cost_is_not_guessed():
    usage = {"prompt": 100, "cached": 0, "completion": 10}

    assert provider._estimated_cost(usage, "future-kimi") is None


def _response(payload):
    request = httpx.Request("POST", "https://api.moonshot.ai/v1/chat/completions")
    return httpx.Response(
        200,
        json=payload,
        headers={"x-request-id": "request-123"},
        request=request,
    )


def _success_payload(*, model="kimi-k3", finish_reason="stop", content=None):
    return {
        "id": "response-123",
        "model": model,
        "choices": [
            {
                "finish_reason": finish_reason,
                "message": {
                    "role": "assistant",
                    "content": content or json.dumps({"images": []}),
                },
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 20,
            "total_tokens": 120,
            "prompt_tokens_details": {"cached_tokens": 10},
        },
    }


def test_call_api_records_identity_terminal_state_and_cost(monkeypatch):
    monkeypatch.setenv("MOONSHOT_API_KEY", "test-key")
    monkeypatch.setenv("MOONSHOT_KIMI_MODEL", "kimi-k3")
    monkeypatch.setattr(
        provider.httpx, "post", lambda *args, **kwargs: _response(_success_payload())
    )

    result = provider.call_api("hello", {}, {})

    assert result["output"] == '{"images": []}'
    assert result["metadata"] == {
        "api_route": "moonshot",
        "requested_model": "kimi-k3",
        "expected_served_model": "kimi-k3",
        "served_model": "kimi-k3",
        "finish_reason": "stop",
        "requested_reasoning_effort": "max",
        "requested_output_contract": "crop_regions",
        "requested_max_completion_tokens": 4096,
        "response_id": "response-123",
        "request_id": "request-123",
    }
    assert result["tokenUsage"] == {
        "prompt": 100,
        "completion": 20,
        "total": 120,
        "cached": 10,
    }
    assert result["cost"] == 0.000573


def test_call_api_rejects_wrong_served_model(monkeypatch):
    monkeypatch.setenv("MOONSHOT_API_KEY", "test-key")
    monkeypatch.setenv("MOONSHOT_KIMI_MODEL", "kimi-k3")
    monkeypatch.setattr(
        provider.httpx,
        "post",
        lambda *args, **kwargs: _response(_success_payload(model="kimi-k2.6")),
    )

    result = provider.call_api("hello", {}, {})

    assert "unexpected model" in result["error"]
    assert result["metadata"]["served_model"] == "kimi-k2.6"


def test_call_api_rejects_incomplete_response(monkeypatch):
    monkeypatch.setenv("MOONSHOT_API_KEY", "test-key")
    monkeypatch.setenv("MOONSHOT_KIMI_MODEL", "kimi-k3")
    monkeypatch.setattr(
        provider.httpx,
        "post",
        lambda *args, **kwargs: _response(_success_payload(finish_reason="length")),
    )

    result = provider.call_api("hello", {}, {})

    assert "did not finish normally" in result["error"]
    assert result["metadata"]["finish_reason"] == "length"


def test_call_api_rejects_schema_invalid_output_without_retaining_it(monkeypatch):
    monkeypatch.setenv("MOONSHOT_API_KEY", "test-key")
    monkeypatch.setenv("MOONSHOT_KIMI_MODEL", "kimi-k3")
    invalid = json.dumps({"images": [{"description": "x", "bbox": [0, 1, 2]}]})
    monkeypatch.setattr(
        provider.httpx,
        "post",
        lambda *args, **kwargs: _response(_success_payload(content=invalid)),
    )

    result = provider.call_api("hello", {}, {})

    assert "violated" in result["error"]
    assert "output" not in result
    assert len(result["metadata"]["invalid_output_sha256"]) == 64


def test_page_context_contract_is_strict(monkeypatch):
    monkeypatch.setenv("MOONSHOT_KIMI_MODEL", "kimi-k3")
    monkeypatch.setenv("MOONSHOT_KIMI_OUTPUT_CONTRACT", "page_context_validation")

    body = provider._build_body("hello")

    schema = body["response_format"]["json_schema"]
    assert schema["name"] == "page_context_validation"
    assert schema["schema"]["required"] == [
        "verdict",
        "has_page_text",
        "excessive_blank",
        "reason",
    ]


def test_normalization_rejects_lossy_content_blocks():
    prompt = json.dumps(
        [{"role": "user", "content": [{"type": "input_audio", "data": "x"}]}]
    )

    try:
        provider._normalize_messages(prompt)
    except ValueError as exc:
        assert "Unsupported prompt content type" in str(exc)
    else:
        raise AssertionError("unsupported content must fail closed")


def test_openrouter_call_uses_router_key_and_endpoint(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "router-key")
    monkeypatch.setenv("MOONSHOT_KIMI_API_ROUTE", "openrouter")
    monkeypatch.setenv("MOONSHOT_KIMI_MODEL", "moonshotai/kimi-k3")
    seen = {}

    def fake_post(url, **kwargs):
        seen["url"] = url
        seen["authorization"] = kwargs["headers"]["Authorization"]
        return _response(_success_payload(model="moonshotai/kimi-k3"))

    monkeypatch.setattr(provider.httpx, "post", fake_post)

    result = provider.call_api("hello", {}, {})

    assert result["output"] == '{"images": []}'
    assert result["metadata"]["api_route"] == "openrouter"
    assert result["metadata"]["served_model"] == "moonshotai/kimi-k3"
    assert seen == {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "authorization": "Bearer router-key",
    }
