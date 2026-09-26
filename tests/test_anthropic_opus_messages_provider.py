import importlib.util
import json
from pathlib import Path

import httpx


PROVIDER_PATH = (
    Path(__file__).parents[1]
    / "benchmarks"
    / "providers"
    / "anthropic_opus48_messages.py"
)
SPEC = importlib.util.spec_from_file_location(
    "anthropic_opus48_messages", PROVIDER_PATH
)
assert SPEC and SPEC.loader
provider = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(provider)


def _response(payload):
    request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    return httpx.Response(
        200,
        json=payload,
        headers={"request-id": "request-123"},
        request=request,
    )


def _success_payload(*, model="claude-opus-5", stop_reason="end_turn", text=None):
    return {
        "id": "msg_123",
        "type": "message",
        "role": "assistant",
        "model": model,
        "stop_reason": stop_reason,
        "content": [
            {"type": "thinking", "thinking": "summary"},
            {"type": "text", "text": text or json.dumps({"images": []})},
        ],
        "usage": {
            "input_tokens": 100,
            "output_tokens": 20,
            "cache_read_input_tokens": 10,
            "cache_creation_input_tokens": 5,
        },
    }


def test_opus5_body_uses_adaptive_high_effort_and_strict_schema(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_OPUS48_MODEL", "claude-opus-5")
    monkeypatch.setenv("ANTHROPIC_OPUS48_MAX_TOKENS", "16384")

    body = provider._build_body('[{"role":"user","content":"hello"}]')

    assert body["model"] == "claude-opus-5"
    assert body["max_tokens"] == 16384
    assert body["thinking"] == {"type": "adaptive"}
    assert body["output_config"]["effort"] == "high"
    assert body["output_config"]["format"]["type"] == "json_schema"
    assert body["output_config"]["format"]["schema"] == provider.CROP_SCHEMA
    bbox_schema = provider.CROP_SCHEMA["properties"]["images"]["items"]["properties"][
        "bbox"
    ]
    assert bbox_schema["minItems"] == 1
    assert "maxItems" not in bbox_schema
    assert "minimum" not in bbox_schema["items"]
    assert "maximum" not in bbox_schema["items"]
    assert "temperature" not in body
    assert "top_p" not in body


def test_page_context_contract_is_selected(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_OPUS48_OUTPUT_CONTRACT", "page_context_validation")

    body = provider._build_body("inspect")

    assert body["output_config"]["format"]["schema"] == provider.PAGE_CONTEXT_SCHEMA


def test_integer_crop_projection_keeps_strict_type_and_local_bounds():
    options = {"config": {"output_contract": "crop_regions_integer"}}
    body = provider._build_body("inspect", options)
    bbox = body["output_config"]["format"]["schema"]["properties"]["images"]["items"][
        "properties"
    ]["bbox"]

    assert bbox["items"] == {"type": "integer"}
    assert (
        provider._contract_error(
            '{"images":[{"description":"x","bbox":[0,0,1000,1000]}]}',
            "crop_regions_integer",
        )
        is None
    )
    assert "integers from 0 to 1000" in provider._contract_error(
        '{"images":[{"description":"x","bbox":[0,0,1000,1359]}]}',
        "crop_regions_integer",
    )


def test_raw_envelope_is_saved_before_invalid_crop_is_rejected(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_MESSAGES_RAW_ENVELOPE_DIR", str(tmp_path))
    monkeypatch.setattr(
        provider.httpx,
        "post",
        lambda *args, **kwargs: _response(
            _success_payload(
                text='{"images":[{"description":"x","bbox":[0,0,1000,1359]}]}'
            )
        ),
    )

    result = provider.call_api(
        "inspect",
        {
            "config": {
                "model": "claude-opus-5",
                "output_contract": "crop_regions_integer",
            }
        },
        {},
    )

    assert "violated" in result["error"]
    assert "output" not in result
    saved = list(tmp_path.glob("*.json"))
    assert len(saved) == 1
    assert saved[0].stem == result["metadata"]["raw_response_sha256"]


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


def test_call_api_records_identity_terminal_state_usage_and_cost(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_OPUS48_MODEL", "claude-opus-5")
    monkeypatch.setenv("ANTHROPIC_OPUS48_MAX_TOKENS", "16384")
    monkeypatch.setattr(
        provider.httpx, "post", lambda *args, **kwargs: _response(_success_payload())
    )

    result = provider.call_api("hello", {}, {})

    assert result["output"] == '{"images": []}'
    assert result["metadata"] == {
        "requested_model": "claude-opus-5",
        "expected_served_model": "claude-opus-5",
        "served_model": "claude-opus-5",
        "stop_reason": "end_turn",
        "requested_thinking": "adaptive",
        "requested_effort": "high",
        "requested_output_contract": "crop_regions",
        "requested_max_tokens": 16384,
        "response_id": "msg_123",
        "request_id": "request-123",
    }
    assert result["tokenUsage"] == {
        "prompt": 115,
        "completion": 20,
        "total": 135,
        "cached": 10,
    }
    assert result["cost"] == 0.001075


def test_call_api_rejects_wrong_served_model(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_OPUS48_MODEL", "claude-opus-5")
    monkeypatch.setattr(
        provider.httpx,
        "post",
        lambda *args, **kwargs: _response(_success_payload(model="claude-opus-4-8")),
    )

    result = provider.call_api("hello", {}, {})

    assert "unexpected model" in result["error"]
    assert "output" not in result


def test_call_api_rejects_incomplete_response(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_OPUS48_MODEL", "claude-opus-5")
    monkeypatch.setattr(
        provider.httpx,
        "post",
        lambda *args, **kwargs: _response(_success_payload(stop_reason="max_tokens")),
    )

    result = provider.call_api("hello", {}, {})

    assert "did not finish normally" in result["error"]
    assert "output" not in result


def test_call_api_rejects_schema_invalid_output_without_retaining_it(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_OPUS48_MODEL", "claude-opus-5")
    invalid = json.dumps({"images": [{"description": "x", "bbox": [0, 1, 2]}]})
    monkeypatch.setattr(
        provider.httpx,
        "post",
        lambda *args, **kwargs: _response(_success_payload(text=invalid)),
    )

    result = provider.call_api("hello", {}, {})

    assert "violated" in result["error"]
    assert "output" not in result
    assert len(result["metadata"]["invalid_output_sha256"]) == 64


def test_call_api_rejects_missing_usage(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_OPUS48_MODEL", "claude-opus-5")
    payload = _success_payload()
    del payload["usage"]
    monkeypatch.setattr(
        provider.httpx, "post", lambda *args, **kwargs: _response(payload)
    )

    result = provider.call_api("hello", {}, {})

    assert "invalid usage evidence" in result["error"]
    assert "output" not in result
