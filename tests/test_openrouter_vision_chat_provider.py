import importlib.util
import json
from pathlib import Path

import httpx


PROVIDER_PATH = (
    Path(__file__).parents[1] / "benchmarks" / "providers" / "openrouter_vision_chat.py"
)
SPEC = importlib.util.spec_from_file_location("openrouter_vision_chat", PROVIDER_PATH)
assert SPEC and SPEC.loader
provider = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(provider)


def _response(payload):
    request = httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions")
    return httpx.Response(
        200, json=payload, headers={"x-request-id": "request-1"}, request=request
    )


def _payload(
    *, model="qwen/qwen3.8-max", upstream="Alibaba", finish="stop", content=None
):
    return {
        "id": "response-1",
        "model": model,
        "provider": upstream,
        "choices": [
            {
                "finish_reason": finish,
                "message": {"content": content or '{"images": []}'},
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 20,
            "total_tokens": 120,
            "cost": 0.001,
            "prompt_tokens_details": {"cached_tokens": 10},
            "cost_details": {"upstream_inference_cost": 0.0008},
        },
    }


def test_body_pins_exact_route_and_preserves_image(monkeypatch):
    data_uri = "data:image/png;base64,abc123"
    prompt = json.dumps(
        [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "find"},
                    {"type": "image_url", "image_url": {"url": data_uri}},
                ],
            }
        ]
    )

    body = provider._body(prompt)

    assert body["model"] == "qwen/qwen3.8-max"
    assert body["provider"] == {
        "order": ["Alibaba"],
        "allow_fallbacks": False,
        "require_parameters": True,
        "data_collection": "deny",
        "zdr": True,
    }
    assert body["reasoning"] == {"effort": "low", "exclude": True}
    assert body["messages"][0]["content"][1]["image_url"]["url"] == data_uri
    assert body["response_format"]["json_schema"]["strict"] is True


def test_success_requires_attributable_usage_and_cost(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(
        provider.httpx, "post", lambda *args, **kwargs: _response(_payload())
    )

    result = provider.call_api("return no images", {}, {})

    assert result["output"] == '{"images": []}'
    assert result["metadata"]["served_model"] == "qwen/qwen3.8-max"
    assert result["metadata"]["served_provider"] == "Alibaba"
    assert result["metadata"]["cost_estimated"] is False
    assert result["metadata"]["requested_data_collection"] == "deny"
    assert result["metadata"]["requested_zdr"] is True
    assert result["tokenUsage"] == {
        "prompt": 100,
        "completion": 20,
        "total": 120,
        "cached": 10,
    }
    assert result["cost"] == 0.001


def test_wrong_model_and_provider_fail_closed(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(
        provider.httpx,
        "post",
        lambda *args, **kwargs: _response(_payload(model="other")),
    )
    assert "unexpected model" in provider.call_api("x", {}, {})["error"]
    monkeypatch.setattr(
        provider.httpx,
        "post",
        lambda *args, **kwargs: _response(_payload(upstream="other")),
    )
    assert "unexpected provider" in provider.call_api("x", {}, {})["error"]


def test_incomplete_or_invalid_usage_fails_closed(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(
        provider.httpx,
        "post",
        lambda *args, **kwargs: _response(_payload(finish="length")),
    )
    assert "finish normally" in provider.call_api("x", {}, {})["error"]
    payload = _payload()
    payload["usage"].pop("cost")
    monkeypatch.setattr(
        provider.httpx, "post", lambda *args, **kwargs: _response(payload)
    )
    assert "invalid usage evidence" in provider.call_api("x", {}, {})["error"]


def test_schema_invalid_and_reversed_bbox_are_rejected(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    invalid = '{"images":[{"description":"x","bbox":[0.8,0.2,0.1,0.9]}]}'
    monkeypatch.setattr(
        provider.httpx,
        "post",
        lambda *args, **kwargs: _response(_payload(content=invalid)),
    )

    result = provider.call_api("x", {}, {})

    assert "coordinates must be ordered" in result["error"]
    assert "output" not in result
    assert len(result["metadata"]["invalid_output_sha256"]) == 64


def test_missing_key_and_lossy_prompt_fail_before_network(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    assert "not configured" in provider.call_api("x", {}, {})["error"]
    prompt = json.dumps(
        [{"role": "user", "content": [{"type": "input_audio", "data": "x"}]}]
    )
    assert "Unsupported prompt content" in provider.call_api(prompt, {}, {})["error"]
