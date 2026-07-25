"""Promptfoo provider for attributable Anthropic Messages API evals.

The repo's pinned Promptfoo Anthropic provider sends sampling parameters that
newer Claude models reject. This provider preserves the maintained multimodal
prompt shape and fails closed unless the requested model returns one complete,
schema-valid response with usable attribution and usage evidence.

Set ``ANTHROPIC_OPUS48_OUTPUT_CONTRACT=page_context_validation`` for the C5
page-context gate. The historical environment-variable prefix is retained so
existing recorded commands remain reproducible.
"""

from __future__ import annotations

import base64
import hashlib
import json
import math
import os
from typing import Any

import httpx


DEFAULT_MODEL = "claude-opus-4-8"
DEFAULT_MAX_TOKENS = 4096
DEFAULT_OUTPUT_CONTRACT = "crop_regions"
DEFAULT_INPUT_PRICE_PER_1M = 5.00
DEFAULT_OUTPUT_PRICE_PER_1M = 25.00

CROP_SCHEMA = {
    "type": "object",
    "properties": {
        "images": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "adjacent_text": {"type": "string"},
                    "bbox": {
                        "type": "array",
                        # Anthropic structured outputs reject numeric range
                        # constraints and maxItems. The fail-closed local
                        # validator below enforces range and exactly 4 values.
                        "items": {"type": "number"},
                        "minItems": 1,
                    },
                },
                "required": ["description", "bbox"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["images"],
    "additionalProperties": False,
}

PAGE_CONTEXT_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["pass", "fail"]},
        "has_page_text": {"type": "boolean"},
        "excessive_blank": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "required": ["verdict", "has_page_text", "excessive_blank", "reason"],
    "additionalProperties": False,
}

OUTPUT_CONTRACTS = {
    "crop_regions": CROP_SCHEMA,
    "page_context_validation": PAGE_CONTEXT_SCHEMA,
}


def _provider_config(options: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(options, dict):
        return {}
    nested = options.get("config")
    config = dict(nested) if isinstance(nested, dict) else {}
    for key in {
        "effort",
        "expected_served_model",
        "max_tokens",
        "model",
        "output_contract",
        "thinking",
    }:
        if key in options and key not in config:
            config[key] = options[key]
    return config


def _request_settings(options: dict[str, Any] | None = None) -> dict[str, Any]:
    config = _provider_config(options)
    model = str(
        config.get("model") or os.environ.get("ANTHROPIC_OPUS48_MODEL", DEFAULT_MODEL)
    )
    output_contract = str(
        config.get("output_contract")
        or os.environ.get("ANTHROPIC_OPUS48_OUTPUT_CONTRACT", DEFAULT_OUTPUT_CONTRACT)
    )
    if output_contract not in OUTPUT_CONTRACTS:
        supported = ", ".join(sorted(OUTPUT_CONTRACTS))
        raise ValueError(
            f"Unsupported Anthropic output contract {output_contract!r}; "
            f"choose {supported}"
        )
    thinking = str(
        config.get("thinking")
        or os.environ.get("ANTHROPIC_OPUS48_THINKING", "adaptive")
    )
    if thinking not in {"adaptive", "disabled"}:
        raise ValueError("Anthropic thinking must be 'adaptive' or 'disabled'")
    effort = str(
        config.get("effort") or os.environ.get("ANTHROPIC_OPUS48_EFFORT", "high")
    )
    if effort not in {"low", "medium", "high", "xhigh", "max"}:
        raise ValueError("Unsupported Anthropic effort level")
    if thinking == "disabled" and effort in {"xhigh", "max"}:
        raise ValueError("Anthropic thinking cannot be disabled at xhigh or max effort")
    return {
        "model": model,
        "expected_served_model": str(
            config.get("expected_served_model")
            or os.environ.get("ANTHROPIC_OPUS48_EXPECTED_SERVED_MODEL", model)
        ),
        "max_tokens": int(
            config.get("max_tokens")
            or os.environ.get("ANTHROPIC_OPUS48_MAX_TOKENS", str(DEFAULT_MAX_TOKENS))
        ),
        "effort": effort,
        "thinking": thinking,
        "output_contract": output_contract,
    }


def _decode_data_uri(data_uri: str) -> tuple[str, str]:
    if not data_uri.startswith("data:") or "," not in data_uri:
        raise ValueError("Prompt image URLs must be base64 data URIs")
    header, data = data_uri.split(",", 1)
    if ";base64" not in header:
        raise ValueError("Prompt image URLs must use base64 encoding")
    media_type = header.removeprefix("data:").split(";", 1)[0] or "image/jpeg"
    try:
        base64.b64decode(data, validate=True)
    except Exception as exc:
        raise ValueError("Prompt image data must be valid base64") from exc
    return media_type, data


def _normalize_content_block(block: Any) -> dict[str, Any]:
    if not isinstance(block, dict):
        raise ValueError("Prompt content blocks must be objects")
    block_type = block.get("type")
    if block_type in {"text", "input_text"}:
        text = block.get("text")
        if not isinstance(text, str) or not text:
            raise ValueError("Prompt text blocks require non-empty text")
        return {"type": "text", "text": text}
    if block_type == "image" and isinstance(block.get("source"), dict):
        source = block["source"]
        if source.get("type") != "base64":
            raise ValueError("Anthropic prompt images must use base64 sources")
        media_type = source.get("media_type")
        data = source.get("data")
        if not isinstance(media_type, str) or not media_type.startswith("image/"):
            raise ValueError("Anthropic prompt images require an image media type")
        if not isinstance(data, str):
            raise ValueError("Anthropic prompt images require base64 data")
        try:
            base64.b64decode(data, validate=True)
        except Exception as exc:
            raise ValueError(
                "Anthropic prompt image data must be valid base64"
            ) from exc
        return {
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": data},
        }
    if block_type in {"image_url", "input_image"}:
        image_url = block.get("image_url")
        if isinstance(image_url, dict):
            image_url = image_url.get("url")
        if not isinstance(image_url, str):
            raise ValueError("Prompt image blocks require a non-empty image URL")
        media_type, data = _decode_data_uri(image_url)
        return {
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": data},
        }
    raise ValueError(f"Unsupported prompt content type: {block_type!r}")


def _normalize_messages(prompt: str) -> list[dict[str, Any]]:
    try:
        parsed = json.loads(prompt)
    except json.JSONDecodeError:
        if not prompt:
            raise ValueError("Prompt text must not be empty")
        return [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    if not isinstance(parsed, list):
        if not prompt:
            raise ValueError("Prompt text must not be empty")
        return [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    if not parsed:
        raise ValueError("Prompt message list must not be empty")

    messages: list[dict[str, Any]] = []
    for index, message in enumerate(parsed):
        if not isinstance(message, dict):
            raise ValueError(f"Prompt message {index} must be an object")
        role = message.get("role")
        if role not in {"user", "assistant"}:
            raise ValueError(f"Prompt message {index} has unsupported role {role!r}")
        content = message.get("content")
        content_items = (
            content
            if isinstance(content, list)
            else [{"type": "text", "text": content}]
            if isinstance(content, str)
            else [content]
        )
        if not content_items or content_items == [None]:
            raise ValueError(f"Prompt message {index} requires non-empty content")
        normalized = [_normalize_content_block(item) for item in content_items]
        messages.append({"role": role, "content": normalized})
    return messages


def _build_body(prompt: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
    settings = _request_settings(options)
    return {
        "model": settings["model"],
        "max_tokens": settings["max_tokens"],
        "messages": _normalize_messages(prompt),
        "thinking": {"type": settings["thinking"]},
        "output_config": {
            "effort": settings["effort"],
            "format": {
                "type": "json_schema",
                "schema": OUTPUT_CONTRACTS[settings["output_contract"]],
            },
        },
    }


def _extract_output_text(data: dict[str, Any]) -> str:
    content = data.get("content")
    if not isinstance(content, list):
        return ""
    text_blocks = [
        item.get("text")
        for item in content
        if isinstance(item, dict)
        and item.get("type") == "text"
        and isinstance(item.get("text"), str)
    ]
    if len(text_blocks) != 1:
        return ""
    return text_blocks[0].strip()


def _nonnegative_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _token_usage(data: dict[str, Any]) -> dict[str, int]:
    usage = data.get("usage")
    if not isinstance(usage, dict):
        raise ValueError("usage must be an object")
    uncached = _nonnegative_int(usage.get("input_tokens"), "input_tokens")
    cached = _nonnegative_int(
        usage.get("cache_read_input_tokens", 0), "cache_read_input_tokens"
    )
    cache_creation = _nonnegative_int(
        usage.get("cache_creation_input_tokens", 0),
        "cache_creation_input_tokens",
    )
    completion = _nonnegative_int(usage.get("output_tokens"), "output_tokens")
    prompt = uncached + cached + cache_creation
    return {
        "prompt": prompt,
        "completion": completion,
        "total": prompt + completion,
        "cached": cached,
    }


def _price_per_1m(kind: str, default: float) -> float:
    for env_name in (
        f"ANTHROPIC_MESSAGES_{kind}_PRICE_PER_1M",
        f"ANTHROPIC_OPUS48_{kind}_PRICE_PER_1M",
    ):
        raw_value = os.environ.get(env_name)
        if raw_value:
            return float(raw_value)
    return default


def _estimated_cost(token_usage: dict[str, int]) -> float:
    input_price = _price_per_1m("INPUT", DEFAULT_INPUT_PRICE_PER_1M)
    output_price = _price_per_1m("OUTPUT", DEFAULT_OUTPUT_PRICE_PER_1M)
    return (
        token_usage["prompt"] * input_price + token_usage["completion"] * output_price
    ) / 1_000_000


def _validate_crop_regions(payload: Any) -> str | None:
    if not isinstance(payload, dict) or set(payload) != {"images"}:
        return "root must contain only the required 'images' field"
    images = payload["images"]
    if not isinstance(images, list):
        return "images must be an array"
    allowed = {"description", "adjacent_text", "bbox"}
    required = {"description", "bbox"}
    for index, image in enumerate(images):
        if not isinstance(image, dict):
            return f"images[{index}] must be an object"
        if not required.issubset(image) or not set(image).issubset(allowed):
            return f"images[{index}] has missing or unsupported fields"
        if not isinstance(image["description"], str):
            return f"images[{index}].description must be a string"
        if "adjacent_text" in image and not isinstance(image["adjacent_text"], str):
            return f"images[{index}].adjacent_text must be a string"
        bbox = image["bbox"]
        if not isinstance(bbox, list) or len(bbox) != 4:
            return f"images[{index}].bbox must contain four numbers"
        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value < 0
            or value > 1
            for value in bbox
        ):
            return f"images[{index}].bbox values must be finite numbers from 0 to 1"
    return None


def _validate_page_context(payload: Any) -> str | None:
    required = {"verdict", "has_page_text", "excessive_blank", "reason"}
    if not isinstance(payload, dict) or set(payload) != required:
        return "root must contain exactly the page-context fields"
    if payload["verdict"] not in {"pass", "fail"}:
        return "verdict must be 'pass' or 'fail'"
    if type(payload["has_page_text"]) is not bool:
        return "has_page_text must be a boolean"
    if type(payload["excessive_blank"]) is not bool:
        return "excessive_blank must be a boolean"
    if not isinstance(payload["reason"], str):
        return "reason must be a string"
    return None


def _contract_error(output: str, output_contract: str) -> str | None:
    try:
        payload = json.loads(output)
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        return f"invalid JSON: {type(exc).__name__}"
    if output_contract == "crop_regions":
        return _validate_crop_regions(payload)
    return _validate_page_context(payload)


def call_api(prompt: str, options: dict[str, Any], context: dict[str, Any]):
    del context
    try:
        settings = _request_settings(options)
        body = _build_body(prompt, options)
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}

    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get(
        "DOC_WEB_ANTHROPIC_API_KEY"
    )
    if not api_key:
        return {"error": "ANTHROPIC_API_KEY is not configured"}

    timeout = float(os.environ.get("ANTHROPIC_OPUS48_TIMEOUT_SECONDS", "180"))
    try:
        response = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json=body,
            timeout=timeout,
        )
        response.raise_for_status()
        parsed = response.json()
        if not isinstance(parsed, dict):
            raise ValueError("Anthropic response JSON must be an object")
        data = parsed
    except httpx.HTTPStatusError as exc:
        return {"error": f"API error: {exc.response.status_code} {exc.response.text}"}
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}

    metadata = {
        "requested_model": body["model"],
        "expected_served_model": settings["expected_served_model"],
        "served_model": data.get("model"),
        "stop_reason": data.get("stop_reason"),
        "requested_thinking": settings["thinking"],
        "requested_effort": settings["effort"],
        "requested_output_contract": settings["output_contract"],
        "requested_max_tokens": settings["max_tokens"],
        "response_id": data.get("id"),
        "request_id": response.headers.get("request-id")
        or response.headers.get("x-request-id"),
    }
    result: dict[str, Any] = {
        "metadata": {key: value for key, value in metadata.items() if value is not None}
    }
    try:
        token_usage = _token_usage(data)
    except (TypeError, ValueError) as exc:
        result["metadata"]["usage_error"] = str(exc)
        result["error"] = (
            f"Anthropic Messages API returned invalid usage evidence: {exc}"
        )
        return result
    result["tokenUsage"] = token_usage
    result["cost"] = _estimated_cost(token_usage)

    if data.get("type") != "message" or data.get("role") != "assistant":
        result["error"] = "Anthropic Messages API returned a malformed message envelope"
        return result
    if data.get("stop_reason") != "end_turn":
        result["error"] = (
            "Anthropic Messages API response did not finish normally: "
            f"{data.get('stop_reason')!r}"
        )
        return result
    if data.get("model") != settings["expected_served_model"]:
        result["error"] = (
            "Anthropic Messages API served an unexpected model: "
            f"expected={settings['expected_served_model']!r}, "
            f"served={data.get('model')!r}"
        )
        return result

    output = _extract_output_text(data)
    if not output:
        result["error"] = (
            "Anthropic Messages API did not return exactly one text output block"
        )
        return result
    contract_error = _contract_error(output, settings["output_contract"])
    if contract_error is not None:
        result["metadata"]["contract_error"] = contract_error
        result["metadata"]["invalid_output_sha256"] = hashlib.sha256(
            output.encode("utf-8")
        ).hexdigest()
        result["error"] = (
            "Anthropic Messages API output violated the requested "
            f"{settings['output_contract']} contract: {contract_error}"
        )
        return result

    result["output"] = output
    return result
