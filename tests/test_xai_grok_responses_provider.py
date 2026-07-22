from __future__ import annotations

import hashlib
import json

from benchmarks.providers import xai_grok_responses as provider


def test_build_body_normalizes_multimodal_prompt(monkeypatch):
    monkeypatch.setenv("XAI_GROK_REASONING_EFFORT", "medium")
    prompt = json.dumps(
        [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Inspect this image"},
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/png;base64,abc"},
                    },
                ],
            }
        ]
    )

    body = provider._build_body(prompt)

    assert body["model"] == "grok-4.5"
    assert body["reasoning"] == {"effort": "medium"}
    assert body["store"] is False
    assert body["text"]["format"] == provider.CROP_RESPONSE_FORMAT
    assert body["text"]["format"]["strict"] is True
    assert (
        "adjacent_text"
        in body["text"]["format"]["schema"]["properties"]["images"]["items"][
            "properties"
        ]
    )
    assert (
        "adjacent_text"
        not in body["text"]["format"]["schema"]["properties"]["images"]["items"][
            "required"
        ]
    )
    assert body["input"][0]["content"] == [
        {"type": "input_text", "text": "Inspect this image"},
        {
            "type": "input_image",
            "image_url": "data:image/png;base64,abc",
            "detail": "high",
        },
    ]


def test_build_body_selects_page_context_output_contract(monkeypatch):
    monkeypatch.setenv("XAI_GROK_OUTPUT_CONTRACT", "page_context_validation")

    body = provider._build_body("inspect both images")

    assert body["text"]["format"] == provider.PAGE_CONTEXT_RESPONSE_FORMAT
    assert body["text"]["format"]["schema"]["required"] == [
        "verdict",
        "has_page_text",
        "excessive_blank",
        "reason",
    ]


def test_build_body_rejects_unknown_output_contract():
    try:
        provider._build_body(
            "inspect",
            {"config": {"output_contract": "not-a-contract"}},
        )
    except ValueError as exc:
        assert "Unsupported xAI output contract" in str(exc)
    else:
        raise AssertionError("unknown output contract should fail before an API call")


def test_build_body_rejects_unsupported_prompt_content_without_dropping_it():
    prompt = json.dumps(
        [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Inspect the required file"},
                    {"type": "input_file", "file_id": "file-required"},
                ],
            }
        ]
    )

    try:
        provider._build_body(prompt)
    except ValueError as exc:
        assert str(exc) == "Unsupported prompt content type: 'input_file'"
    else:
        raise AssertionError("unsupported prompt content must fail before an API call")


def test_build_body_rejects_malformed_or_empty_message_content():
    invalid_prompts = [
        json.dumps(["not-a-message"]),
        json.dumps([{"role": "user"}]),
        json.dumps([{"role": "user", "content": []}]),
        json.dumps([{"role": "user", "content": [{"type": "text"}]}]),
        json.dumps([]),
    ]

    for prompt in invalid_prompts:
        try:
            provider._build_body(prompt)
        except ValueError:
            continue
        raise AssertionError(f"malformed prompt must fail closed: {prompt}")


def test_extracts_output_usage_and_reported_cost(monkeypatch):
    class FakeResponse:
        headers = {"x-zero-data-retention": "false"}

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "output": [
                    {"type": "reasoning", "content": []},
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": '{"images":[]}'}],
                    },
                ],
                "usage": {
                    "input_tokens": 100,
                    "input_tokens_details": {"cached_tokens": 20},
                    "output_tokens": 10,
                    "total_tokens": 110,
                    "cost_in_usd_ticks": 2400000,
                },
                "model": "grok-4.5",
                "status": "completed",
                "service_tier": "default",
                "id": "response-123",
            }

    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setattr(provider.httpx, "post", lambda *args, **kwargs: FakeResponse())

    result = provider.call_api("hello", {}, {})

    assert result == {
        "output": '{"images":[]}',
        "tokenUsage": {
            "prompt": 100,
            "completion": 10,
            "total": 110,
            "cached": 20,
        },
        "cost": 0.00024,
        "metadata": {
            "requested_model": "grok-4.5",
            "expected_served_model": "grok-4.5",
            "requested_reasoning_effort": "low",
            "requested_output_contract": "crop_regions",
            "requested_max_output_tokens": 4096,
            "requested_image_detail": "high",
            "requested_store": False,
            "served_model": "grok-4.5",
            "response_status": "completed",
            "zero_data_retention": "false",
            "service_tier": "default",
            "response_id": "response-123",
        },
    }


def test_incomplete_http_200_is_rejected_with_usage_cost_and_metadata(monkeypatch):
    class FakeResponse:
        headers = {"x-zero-data-retention": "false"}

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "status": "incomplete",
                "incomplete_details": {"reason": "max_output_tokens"},
                "output_text": '{"images": []}',
                "usage": {
                    "input_tokens": 50,
                    "output_tokens": 5,
                    "total_tokens": 55,
                    "cost_in_usd_ticks": 1000000,
                },
                "model": "grok-4.5",
                "id": "response-incomplete",
            }

    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setattr(provider.httpx, "post", lambda *args, **kwargs: FakeResponse())

    result = provider.call_api("hello", {}, {})

    assert result["error"] == (
        "xAI Responses API did not complete: status='incomplete'"
    )
    assert "output" not in result
    assert result["tokenUsage"] == {
        "prompt": 50,
        "completion": 5,
        "total": 55,
        "cached": 0,
    }
    assert result["cost"] == 0.0001
    assert result["metadata"]["response_status"] == "incomplete"
    assert result["metadata"]["incomplete_details"] == {"reason": "max_output_tokens"}
    assert result["metadata"]["zero_data_retention"] == "false"


def test_provider_error_http_200_is_rejected_with_evidence(monkeypatch):
    class FakeResponse:
        headers = {"x-zero-data-retention": "true"}

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "status": "completed",
                "error": {"code": "server_error", "message": "try again"},
                "output_text": '{"images": []}',
                "usage": {
                    "input_tokens": 25,
                    "output_tokens": 2,
                    "cost_in_usd_ticks": 500000,
                },
                "model": "grok-4.5",
                "id": "response-error",
            }

    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setenv("XAI_GROK_REASONING_EFFORT", "high")
    monkeypatch.setenv("XAI_GROK_MAX_OUTPUT_TOKENS", "2048")
    monkeypatch.setenv("XAI_GROK_IMAGE_DETAIL", "low")
    monkeypatch.setenv("XAI_GROK_OUTPUT_CONTRACT", "page_context_validation")
    monkeypatch.setattr(provider.httpx, "post", lambda *args, **kwargs: FakeResponse())

    result = provider.call_api("hello", {}, {})

    assert result["error"] == (
        "xAI Responses API returned a provider error: server_error: try again"
    )
    assert "output" not in result
    assert result["tokenUsage"] == {
        "prompt": 25,
        "completion": 2,
        "total": 27,
        "cached": 0,
    }
    assert result["cost"] == 0.00005
    assert result["metadata"] == {
        "requested_model": "grok-4.5",
        "expected_served_model": "grok-4.5",
        "requested_reasoning_effort": "high",
        "requested_output_contract": "page_context_validation",
        "requested_max_output_tokens": 2048,
        "requested_image_detail": "low",
        "requested_store": False,
        "served_model": "grok-4.5",
        "response_status": "completed",
        "provider_error": {"code": "server_error", "message": "try again"},
        "zero_data_retention": "true",
        "response_id": "response-error",
    }


def test_completed_response_from_unexpected_model_is_rejected(monkeypatch):
    class FakeResponse:
        headers = {"x-zero-data-retention": "false"}

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "status": "completed",
                "model": "grok-4.5-mini",
                "output_text": '{"images":[]}',
                "usage": {
                    "input_tokens": 10,
                    "output_tokens": 2,
                    "cost_in_usd_ticks": 500000,
                },
                "id": "response-wrong-model",
            }

    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setattr(provider.httpx, "post", lambda *args, **kwargs: FakeResponse())

    result = provider.call_api("hello", {}, {})

    assert result["error"] == (
        "xAI Responses API served an unexpected model: "
        "expected='grok-4.5', served='grok-4.5-mini'"
    )
    assert "output" not in result
    assert result["cost"] == 0.00005
    assert result["metadata"]["expected_served_model"] == "grok-4.5"
    assert result["metadata"]["served_model"] == "grok-4.5-mini"


def test_completed_schema_invalid_output_is_rejected_with_hash(monkeypatch):
    invalid_output = '{"ok":true}'

    class FakeResponse:
        headers = {"x-zero-data-retention": "false"}

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "status": "completed",
                "model": "grok-4.5",
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": invalid_output}],
                    }
                ],
                "usage": {
                    "input_tokens": 10,
                    "output_tokens": 2,
                    "cost_in_usd_ticks": 500000,
                },
                "id": "response-invalid-contract",
            }

    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setattr(provider.httpx, "post", lambda *args, **kwargs: FakeResponse())

    result = provider.call_api("hello", {}, {})

    assert result["error"] == (
        "xAI Responses API output violated the requested crop_regions contract: "
        "root must contain only the required 'images' field"
    )
    assert "output" not in result
    assert result["cost"] == 0.00005
    assert result["metadata"]["contract_error"] == (
        "root must contain only the required 'images' field"
    )
    assert (
        result["metadata"]["invalid_output_sha256"]
        == hashlib.sha256(invalid_output.encode("utf-8")).hexdigest()
    )


def test_page_context_contract_validator_matches_prompt_shape():
    valid_output = json.dumps(
        {
            "verdict": "fail",
            "has_page_text": True,
            "excessive_blank": False,
            "reason": "Caption text remains.",
        }
    )

    assert provider._contract_error(valid_output, "page_context_validation") is None
    assert (
        provider._contract_error(
            '{"verdict":"pass","has_page_text":false}',
            "page_context_validation",
        )
        == "root must contain exactly verdict, has_page_text, excessive_blank, reason"
    )


def test_page_context_contract_rejects_unhashable_verdict_cleanly():
    invalid_output = json.dumps(
        {
            "verdict": [],
            "has_page_text": False,
            "excessive_blank": False,
            "reason": "invalid verdict type",
        }
    )

    assert (
        provider._contract_error(invalid_output, "page_context_validation")
        == "verdict must be 'pass' or 'fail'"
    )


def test_crop_contract_rejects_huge_integer_without_overflow():
    invalid_output = json.dumps(
        {
            "images": [
                {
                    "description": "invalid bbox",
                    "bbox": [0, 0, 1, 10**309],
                }
            ]
        }
    )

    assert provider._contract_error(invalid_output, "crop_regions") == (
        "images[0].bbox values must be finite numbers from 0 to 1"
    )


def test_completed_non_object_response_is_rejected(monkeypatch):
    class FakeResponse:
        headers = {}

        def raise_for_status(self):
            return None

        def json(self):
            return []

    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setattr(provider.httpx, "post", lambda *args, **kwargs: FakeResponse())

    result = provider.call_api("hello", {}, {})

    assert result == {
        "error": "ValueError: xAI Responses API response JSON must be an object"
    }


def test_only_final_message_output_text_can_be_scored(monkeypatch):
    class FakeResponse:
        headers = {}

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "status": "completed",
                "model": "grok-4.5",
                "output": [
                    {
                        "type": "reasoning",
                        "content": [{"type": "output_text", "text": '{"images":[]}'}],
                    }
                ],
            }

    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setattr(provider.httpx, "post", lambda *args, **kwargs: FakeResponse())

    result = provider.call_api("hello", {}, {})

    assert result["error"] == "xAI Responses API returned no output text"
    assert "output" not in result


def test_only_last_message_output_text_is_scored(monkeypatch):
    class FakeResponse:
        headers = {}

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "status": "completed",
                "model": "grok-4.5",
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": '{"bad":true}'}],
                    },
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": '{"images":[]}'}],
                    },
                ],
            }

    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setattr(provider.httpx, "post", lambda *args, **kwargs: FakeResponse())

    result = provider.call_api("hello", {}, {})

    assert result["output"] == '{"images":[]}'


def test_empty_provider_error_object_is_still_rejected(monkeypatch):
    class FakeResponse:
        headers = {}

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "status": "completed",
                "model": "grok-4.5",
                "error": {},
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": '{"images":[]}'}],
                    }
                ],
            }

    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setattr(provider.httpx, "post", lambda *args, **kwargs: FakeResponse())

    result = provider.call_api("hello", {}, {})

    assert result["error"] == "xAI Responses API returned a provider error: {}"
    assert "output" not in result


def test_non_finite_cost_is_rejected_as_invalid_usage_evidence(monkeypatch):
    class FakeResponse:
        headers = {}

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "status": "completed",
                "model": "grok-4.5",
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": '{"images":[]}'}],
                    }
                ],
                "usage": {
                    "input_tokens": 10,
                    "output_tokens": 2,
                    "cost_in_usd_ticks": float("nan"),
                },
            }

    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setattr(provider.httpx, "post", lambda *args, **kwargs: FakeResponse())

    result = provider.call_api("hello", {}, {})

    assert result["error"] == (
        "xAI Responses API returned invalid usage evidence: "
        "usage.cost_in_usd_ticks must be a finite non-negative number"
    )
    assert result["tokenUsage"] == {
        "prompt": 10,
        "completion": 2,
        "total": 12,
        "cached": 0,
    }
    assert "cost" not in result
    assert "output" not in result


def test_malformed_usage_types_are_reported_without_raising():
    data = {"usage": {"input_tokens": [], "output_tokens": 2}}

    assert provider._token_usage(data) is None
    assert provider._usage_evidence_error(data) == (
        "usage.input_tokens must be a non-negative integer"
    )
    assert (
        provider._extract_output_text(
            {"output": [{"type": "message", "content": None}]}
        )
        == ""
    )


def test_contract_parser_rejects_pathological_json_without_raising():
    deeply_nested = "[" * 2000 + "]" * 2000
    over_limit_integer = "1" * 5000

    assert provider._contract_error(deeply_nested, "crop_regions") == (
        "invalid JSON structure: RecursionError"
    )
    assert provider._contract_error(over_limit_integer, "crop_regions") == (
        "invalid JSON structure: ValueError"
    )
