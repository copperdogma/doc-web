"""Fail-closed OpenRouter vision provider for bounded crop evaluations."""

from __future__ import annotations

import hashlib
import json
import math
import os
import time
from typing import Any

import httpx


DEFAULT_MODEL = "qwen/qwen3.8-max"
DEFAULT_PROVIDER = "Alibaba"
DEFAULT_MAX_TOKENS = 16384
DEFAULT_OUTPUT_CONTRACT = "crop_regions"

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
                        "items": {"type": "number", "minimum": 0, "maximum": 1},
                        "minItems": 4,
                        "maxItems": 4,
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
        "expected_served_model",
        "expected_served_provider",
        "max_tokens",
        "model",
        "output_contract",
        "reasoning_effort",
    }:
        if key in options and key not in config:
            config[key] = options[key]
    return config


def _settings(options: dict[str, Any] | None = None) -> dict[str, Any]:
    config = _provider_config(options)
    model = str(
        config.get("model") or os.environ.get("OPENROUTER_VISION_MODEL", DEFAULT_MODEL)
    )
    output_contract = str(
        config.get("output_contract")
        or os.environ.get("OPENROUTER_VISION_OUTPUT_CONTRACT", DEFAULT_OUTPUT_CONTRACT)
    )
    if output_contract not in OUTPUT_CONTRACTS:
        supported = ", ".join(sorted(OUTPUT_CONTRACTS))
        raise ValueError(
            f"Unsupported output contract {output_contract!r}; choose {supported}"
        )
    return {
        "model": model,
        "expected_served_model": str(
            config.get("expected_served_model")
            or os.environ.get("OPENROUTER_VISION_EXPECTED_MODEL", model)
        ),
        "expected_served_provider": str(
            config.get("expected_served_provider")
            or os.environ.get("OPENROUTER_VISION_EXPECTED_PROVIDER", DEFAULT_PROVIDER)
        ),
        "max_tokens": int(
            config.get("max_tokens")
            or os.environ.get("OPENROUTER_VISION_MAX_TOKENS", str(DEFAULT_MAX_TOKENS))
        ),
        "reasoning_effort": str(
            config.get("reasoning_effort")
            or os.environ.get("OPENROUTER_VISION_REASONING_EFFORT", "low")
        ),
        "output_contract": output_contract,
    }


def _normalize_block(block: Any) -> dict[str, Any]:
    if not isinstance(block, dict):
        raise ValueError("Prompt content blocks must be objects")
    if block.get("type") == "text":
        value = block.get("text")
        if not isinstance(value, str) or not value:
            raise ValueError("Prompt text blocks require non-empty text")
        return {"type": "text", "text": value}
    if block.get("type") == "image_url":
        image_url = block.get("image_url")
        if isinstance(image_url, str):
            image_url = {"url": image_url}
        if not isinstance(image_url, dict):
            raise ValueError("Prompt image_url blocks require an image URL")
        url = image_url.get("url")
        if not isinstance(url, str) or not url:
            raise ValueError("Prompt image_url blocks require a non-empty URL")
        normalized = {"url": url}
        if image_url.get("detail") is not None:
            normalized["detail"] = str(image_url["detail"])
        return {"type": "image_url", "image_url": normalized}
    raise ValueError(f"Unsupported prompt content type: {block.get('type')!r}")


def _normalize_messages(prompt: str) -> list[dict[str, Any]]:
    try:
        parsed = json.loads(prompt)
    except json.JSONDecodeError:
        return [{"role": "user", "content": prompt}]
    if not isinstance(parsed, list):
        return [{"role": "user", "content": prompt}]
    if not parsed:
        raise ValueError("Prompt message list must not be empty")
    messages = []
    for index, item in enumerate(parsed):
        if not isinstance(item, dict):
            raise ValueError(f"Prompt message {index} must be an object")
        role = str(item.get("role") or "user")
        content = item.get("content")
        if isinstance(content, str) and content:
            messages.append({"role": role, "content": content})
        elif isinstance(content, list) and content:
            messages.append(
                {
                    "role": role,
                    "content": [_normalize_block(block) for block in content],
                }
            )
        else:
            raise ValueError(f"Prompt message {index} requires non-empty content")
    return messages


def _body(prompt: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
    settings = _settings(options)
    return {
        "model": settings["model"],
        "messages": _normalize_messages(prompt),
        "max_tokens": settings["max_tokens"],
        "reasoning": {"effort": settings["reasoning_effort"], "exclude": True},
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": settings["output_contract"],
                "strict": True,
                "schema": OUTPUT_CONTRACTS[settings["output_contract"]],
            },
        },
        "provider": {
            "order": [settings["expected_served_provider"]],
            "allow_fallbacks": False,
            "require_parameters": True,
            "data_collection": "deny",
            "zdr": True,
        },
    }


def _nonnegative_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _usage(data: dict[str, Any]) -> tuple[dict[str, int], float, dict[str, Any]]:
    usage = data.get("usage")
    if not isinstance(usage, dict):
        raise ValueError("usage must be an object")
    prompt = _nonnegative_int(usage.get("prompt_tokens"), "prompt_tokens")
    completion = _nonnegative_int(usage.get("completion_tokens"), "completion_tokens")
    total = _nonnegative_int(usage.get("total_tokens"), "total_tokens")
    if total < prompt + completion:
        raise ValueError("usage token totals are inconsistent")
    details = usage.get("prompt_tokens_details")
    cached = _nonnegative_int(
        details.get("cached_tokens", 0) if isinstance(details, dict) else 0,
        "cached_tokens",
    )
    if cached > prompt:
        raise ValueError("cached_tokens exceeds prompt_tokens")
    cost = usage.get("cost")
    if (
        isinstance(cost, bool)
        or not isinstance(cost, (int, float))
        or not math.isfinite(cost)
        or cost < 0
    ):
        raise ValueError("usage.cost must be a finite non-negative number")
    safe_usage = {
        key: value
        for key, value in usage.items()
        if key
        in {
            "cost",
            "cost_details",
            "is_byok",
            "prompt_tokens_details",
            "completion_tokens_details",
        }
    }
    return (
        {"prompt": prompt, "completion": completion, "total": total, "cached": cached},
        float(cost),
        safe_usage,
    )


def _choice(data: dict[str, Any]) -> dict[str, Any] | None:
    choices = data.get("choices")
    if (
        not isinstance(choices, list)
        or len(choices) != 1
        or not isinstance(choices[0], dict)
    ):
        return None
    return choices[0]


def _output(data: dict[str, Any]) -> str:
    choice = _choice(data)
    message = choice.get("message") if choice else None
    content = message.get("content") if isinstance(message, dict) else None
    return content.strip() if isinstance(content, str) else ""


def _contract_error(output: str, contract: str) -> str | None:
    try:
        payload = json.loads(output)
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        return f"invalid JSON: {type(exc).__name__}"
    if contract == "page_context_validation":
        required = {"verdict", "has_page_text", "excessive_blank", "reason"}
        if not isinstance(payload, dict) or set(payload) != required:
            return "root must contain exactly the page-context fields"
        if payload["verdict"] not in {"pass", "fail"}:
            return "verdict must be pass or fail"
        if (
            type(payload["has_page_text"]) is not bool
            or type(payload["excessive_blank"]) is not bool
        ):
            return "page-context flags must be booleans"
        if not isinstance(payload["reason"], str):
            return "reason must be a string"
        return None
    if (
        not isinstance(payload, dict)
        or set(payload) != {"images"}
        or not isinstance(payload["images"], list)
    ):
        return "root must contain only an images array"
    for index, image in enumerate(payload["images"]):
        if not isinstance(image, dict):
            return f"images[{index}] must be an object"
        if not {"description", "bbox"}.issubset(image) or not set(image).issubset(
            {"description", "adjacent_text", "bbox"}
        ):
            return f"images[{index}] has missing or unsupported fields"
        if not isinstance(image["description"], str):
            return f"images[{index}].description must be a string"
        if "adjacent_text" in image and not isinstance(image["adjacent_text"], str):
            return f"images[{index}].adjacent_text must be a string"
        bbox = image["bbox"]
        if not isinstance(bbox, list) or len(bbox) != 4:
            return f"images[{index}].bbox must contain four numbers"
        if any(
            isinstance(v, bool)
            or not isinstance(v, (int, float))
            or not math.isfinite(v)
            or v < 0
            or v > 1
            for v in bbox
        ):
            return f"images[{index}].bbox values must be finite numbers from 0 to 1"
        if bbox[0] >= bbox[2] or bbox[1] >= bbox[3]:
            return f"images[{index}].bbox coordinates must be ordered"
    return None


def call_api(prompt: str, options: dict[str, Any], context: dict[str, Any]):
    del context
    try:
        settings = _settings(options)
        body = _body(prompt, options)
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return {"error": "OPENROUTER_API_KEY is not configured"}
    started = time.monotonic()
    try:
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=float(os.environ.get("OPENROUTER_VISION_TIMEOUT_SECONDS", "240")),
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("OpenRouter response JSON must be an object")
    except httpx.HTTPStatusError as exc:
        return {"error": f"API error: {exc.response.status_code} {exc.response.text}"}
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}
    latency_ms = round((time.monotonic() - started) * 1000)
    choice = _choice(data)
    metadata = {
        "requested_model": body["model"],
        "expected_served_model": settings["expected_served_model"],
        "served_model": data.get("model"),
        "expected_served_provider": settings["expected_served_provider"],
        "served_provider": data.get("provider"),
        "finish_reason": choice.get("finish_reason") if choice else None,
        "requested_reasoning_effort": settings["reasoning_effort"],
        "requested_output_contract": settings["output_contract"],
        "requested_max_tokens": settings["max_tokens"],
        "allow_fallbacks": False,
        "require_parameters": True,
        "requested_data_collection": "deny",
        "requested_zdr": True,
        "response_id": data.get("id"),
        "request_id": response.headers.get("x-request-id"),
        "latency_ms": latency_ms,
    }
    result: dict[str, Any] = {
        "metadata": {k: v for k, v in metadata.items() if v is not None}
    }
    try:
        token_usage, cost, safe_usage = _usage(data)
    except ValueError as exc:
        result["error"] = f"OpenRouter returned invalid usage evidence: {exc}"
        return result
    result["tokenUsage"] = token_usage
    result["cost"] = cost
    result["metadata"]["cost_estimated"] = False
    result["metadata"]["raw_usage"] = safe_usage
    if data.get("error") is not None:
        result["error"] = f"OpenRouter returned a provider error: {data['error']}"
        return result
    if choice is None:
        result["error"] = "OpenRouter did not return exactly one response choice"
        return result
    if choice.get("finish_reason") != "stop":
        result["error"] = (
            f"OpenRouter response did not finish normally: {choice.get('finish_reason')!r}"
        )
        return result
    if data.get("model") != settings["expected_served_model"]:
        result["error"] = "OpenRouter served an unexpected model"
        return result
    if data.get("provider") != settings["expected_served_provider"]:
        result["error"] = "OpenRouter served an unexpected provider"
        return result
    output = _output(data)
    if not output:
        result["error"] = "OpenRouter returned no output text"
        return result
    contract_error = _contract_error(output, settings["output_contract"])
    if contract_error is not None:
        result["metadata"]["contract_error"] = contract_error
        result["metadata"]["invalid_output_sha256"] = hashlib.sha256(
            output.encode()
        ).hexdigest()
        result["error"] = (
            f"OpenRouter output violated the requested contract: {contract_error}"
        )
        return result
    result["output"] = output
    return result
