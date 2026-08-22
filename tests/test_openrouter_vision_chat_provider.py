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


def test_public_fixture_route_omits_privacy_filters_and_provider_pin():
    body = provider._body(
        "return no images",
        {
            "config": {
                "model": "stealth/ox-alpha",
                "expected_served_model": "stealth/ox-alpha",
                "pin_provider": False,
                "require_parameters": True,
                "data_collection": None,
                "zdr": None,
            }
        },
    )

    assert body["model"] == "stealth/ox-alpha"
    assert body["provider"] == {"require_parameters": True}
    assert "models" not in body


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


def test_unpinned_route_records_provider_without_requiring_one(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(
        provider.httpx,
        "post",
        lambda *args, **kwargs: _response(
            _payload(model="stealth/ox-alpha", upstream="Stealth")
        ),
    )
    options = {
        "config": {
            "model": "stealth/ox-alpha",
            "expected_served_model": "stealth/ox-alpha",
            "pin_provider": False,
            "data_collection": None,
            "zdr": None,
        }
    }

    result = provider.call_api("x", options, {})

    assert result["output"] == '{"images": []}'
    assert result["metadata"]["served_provider"] == "Stealth"
    assert result["metadata"]["provider_pinned"] is False
    assert result["metadata"]["model_fallbacks_configured"] is False
    assert "requested_data_collection" not in result["metadata"]
    assert "requested_zdr" not in result["metadata"]


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


def test_integer_crop_contract_is_strict_and_locally_validated(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    valid = '{"images":[{"description":"x","bbox":[100,200,800,900]}]}'
    monkeypatch.setattr(
        provider.httpx,
        "post",
        lambda *args, **kwargs: _response(_payload(content=valid)),
    )
    options = {"config": {"output_contract": "crop_regions_integer"}}

    result = provider.call_api("x", options, {})

    assert result["output"] == valid
    body = provider._body("x", options)
    bbox = body["response_format"]["json_schema"]["schema"]["properties"]["images"][
        "items"
    ]["properties"]["bbox"]
    assert bbox["items"]["type"] == "integer"
    invalid = '{"images":[{"description":"x","bbox":[0.1,200,800,900]}]}'
    monkeypatch.setattr(
        provider.httpx,
        "post",
        lambda *args, **kwargs: _response(_payload(content=invalid)),
    )
    assert "integers from 0 to 1000" in provider.call_api("x", options, {})["error"]


def test_diagnostic_wrapper_cleanup_retains_raw_before_validation(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    fenced = '```json\n{"images":[{"description":"x","bbox":[1,2,3,4]}]}\n```'
    monkeypatch.setattr(
        provider.httpx,
        "post",
        lambda *args, **kwargs: _response(_payload(content=fenced)),
    )
    monkeypatch.setattr(
        provider.Path,
        "resolve",
        lambda self: tmp_path / "benchmarks" / "providers" / self.name,
    )
    options = {
        "config": {
            "output_contract": "crop_regions_integer",
            "diagnostic_raw_output_file": "public-diagnostic-{sha256}.json",
            "diagnostic_wrapper_cleanup": True,
        }
    }

    result = provider.call_api("x", options, {})

    assert result["output"] == '{"images":[{"description":"x","bbox":[1,2,3,4]}]}'
    assert result["metadata"]["diagnostic_only"] is True
    assert result["metadata"]["diagnostic_wrapper_cleanup_applied"] is True
    digest = provider.hashlib.sha256(fenced.encode()).hexdigest()
    retained = (
        tmp_path / "benchmarks" / "results" / f"public-diagnostic-{digest}.json"
    )
    assert json.loads(retained.read_text()) == {"raw_output": fenced}
    assert retained.stat().st_mode & 0o777 == 0o600


def test_diagnostic_raw_output_requires_safe_filename(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(
        provider.httpx, "post", lambda *args, **kwargs: _response(_payload())
    )

    result = provider.call_api(
        "x", {"config": {"diagnostic_raw_output_file": "../unsafe.json"}}, {}
    )

    assert "must be a JSON filename" in result["error"]


def test_missing_key_and_lossy_prompt_fail_before_network(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    assert "not configured" in provider.call_api("x", {}, {})["error"]
    prompt = json.dumps(
        [{"role": "user", "content": [{"type": "input_audio", "data": "x"}]}]
    )
    assert "Unsupported prompt content" in provider.call_api(prompt, {}, {})["error"]
