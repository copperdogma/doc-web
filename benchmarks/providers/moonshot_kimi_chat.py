"""Promptfoo provider for attributable Kimi Chat Completions evals.

The provider fails closed on transport and output evidence so benchmark scores
can only be attributed to the requested model and a complete structured reply.
Set ``MOONSHOT_KIMI_OUTPUT_CONTRACT=page_context_validation`` for the C5 gate.
Set ``MOONSHOT_KIMI_API_ROUTE=openrouter`` for the exact OpenRouter K3 route.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import time
from typing import Any

import httpx


DEFAULT_MODEL = "kimi-k2.6"
DEFAULT_MAX_COMPLETION_TOKENS = 4096
DEFAULT_OUTPUT_CONTRACT = "crop_regions"
MODEL_PRICES_PER_1M = {
    "kimi-k2.6": {"cache_hit": 0.16, "input": 0.95, "output": 4.00},
    "kimi-k3": {"cache_hit": 0.30, "input": 3.00, "output": 15.00},
    "moonshotai/kimi-k3": {"cache_hit": 0.30, "input": 3.00, "output": 15.00},
    "moonshotai/kimi-k3-20260715": {
        "cache_hit": 0.30,
        "input": 3.00,
        "output": 15.00,
    },
}

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
        "api_route",
        "expected_served_model",
        "max_completion_tokens",
        "model",
        "output_contract",
        "reasoning_effort",
    }:
        if key in options and key not in config:
            config[key] = options[key]
    return config


def _request_settings(options: dict[str, Any] | None = None) -> dict[str, Any]:
    config = _provider_config(options)
    api_route = str(
        config.get("api_route") or os.environ.get("MOONSHOT_KIMI_API_ROUTE", "moonshot")
    )
    if api_route not in {"moonshot", "openrouter"}:
        raise ValueError("Kimi API route must be 'moonshot' or 'openrouter'")
    model = str(
        config.get("model") or os.environ.get("MOONSHOT_KIMI_MODEL", DEFAULT_MODEL)
    )
    output_contract = str(
        config.get("output_contract")
        or os.environ.get("MOONSHOT_KIMI_OUTPUT_CONTRACT", DEFAULT_OUTPUT_CONTRACT)
    )
    if output_contract not in OUTPUT_CONTRACTS:
        supported = ", ".join(sorted(OUTPUT_CONTRACTS))
        raise ValueError(
            f"Unsupported Kimi output contract {output_contract!r}; choose {supported}"
        )
    return {
        "model": model,
        "api_route": api_route,
        "api_url": (
            "https://openrouter.ai/api/v1/chat/completions"
            if api_route == "openrouter"
            else "https://api.moonshot.ai/v1/chat/completions"
        ),
        "api_key_env": (
            "OPENROUTER_API_KEY" if api_route == "openrouter" else "MOONSHOT_API_KEY"
        ),
        "expected_served_model": str(
            config.get("expected_served_model")
            or os.environ.get("MOONSHOT_KIMI_EXPECTED_SERVED_MODEL", model)
        ),
        "max_completion_tokens": int(
            config.get("max_completion_tokens")
            or os.environ.get(
                "MOONSHOT_KIMI_MAX_COMPLETION_TOKENS",
                str(DEFAULT_MAX_COMPLETION_TOKENS),
            )
        ),
        "reasoning_effort": str(
            config.get("reasoning_effort")
            or os.environ.get("MOONSHOT_KIMI_REASONING_EFFORT", "max")
        ),
        "output_contract": output_contract,
    }


def _normalize_content_block(block: Any) -> dict[str, Any]:
    if not isinstance(block, dict):
        raise ValueError("Prompt content blocks must be objects")
    block_type = block.get("type")
    if block_type == "text":
        text = block.get("text")
        if not isinstance(text, str) or not text:
            raise ValueError("Prompt text blocks require non-empty text")
        return {"type": "text", "text": text}
    if block_type == "image_url":
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
    raise ValueError(f"Unsupported prompt content type: {block_type!r}")


def _normalize_messages(prompt: str) -> list[dict[str, Any]]:
    try:
        parsed = json.loads(prompt)
    except json.JSONDecodeError:
        return [{"role": "user", "content": prompt}]
    if not isinstance(parsed, list):
        return [{"role": "user", "content": prompt}]
    if not parsed:
        raise ValueError("Prompt message list must not be empty")

    messages: list[dict[str, Any]] = []
    for index, item in enumerate(parsed):
        if not isinstance(item, dict):
            raise ValueError(f"Prompt message {index} must be an object")
        role = str(item.get("role") or "user")
        content = item.get("content")
        if isinstance(content, list):
            if not content:
                raise ValueError(f"Prompt message {index} content must not be empty")
            normalized_content = [_normalize_content_block(block) for block in content]
            messages.append({"role": role, "content": normalized_content})
        elif isinstance(content, str) and content:
            messages.append({"role": role, "content": content})
        else:
            raise ValueError(f"Prompt message {index} requires non-empty content")
    return messages


def _response_format(output_contract: str) -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": output_contract,
            "strict": True,
            "schema": OUTPUT_CONTRACTS[output_contract],
        },
    }


def _build_body(prompt: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
    settings = _request_settings(options)
    body: dict[str, Any] = {
        "model": settings["model"],
        "messages": _normalize_messages(prompt),
        "response_format": _response_format(settings["output_contract"]),
    }
    if settings["api_route"] == "openrouter":
        body["max_tokens"] = settings["max_completion_tokens"]
        body["reasoning"] = {
            "effort": settings["reasoning_effort"],
            "exclude": True,
        }
        body["provider"] = {
            "allow_fallbacks": False,
            "require_parameters": True,
        }
    else:
        body["max_completion_tokens"] = settings["max_completion_tokens"]
        if settings["model"] == "kimi-k3":
            body["reasoning_effort"] = settings["reasoning_effort"]
        else:
            body["thinking"] = {
                "type": os.environ.get("MOONSHOT_KIMI_THINKING", "disabled"),
            }
    return body


def _first_choice(data: dict[str, Any]) -> dict[str, Any] | None:
    choices = data.get("choices")
    if not isinstance(choices, list) or len(choices) != 1:
        return None
    return choices[0] if isinstance(choices[0], dict) else None


def _extract_output_text(data: dict[str, Any]) -> str:
    choice = _first_choice(data)
    message = choice.get("message") if choice is not None else None
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    return content.strip() if isinstance(content, str) else ""


def _nonnegative_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _token_usage(data: dict[str, Any]) -> dict[str, int] | None:
    usage = data.get("usage")
    if not isinstance(usage, dict):
        return None
    prompt_tokens = _nonnegative_int(usage.get("prompt_tokens", 0), "prompt_tokens")
    completion_tokens = _nonnegative_int(
        usage.get("completion_tokens", 0), "completion_tokens"
    )
    details = usage.get("prompt_tokens_details")
    cached_value = (
        details.get("cached_tokens", 0)
        if isinstance(details, dict)
        else usage.get("cached_tokens", 0)
    )
    cached_tokens = _nonnegative_int(cached_value, "cached_tokens")
    total_tokens = _nonnegative_int(
        usage.get("total_tokens", prompt_tokens + completion_tokens), "total_tokens"
    )
    if (
        cached_tokens > prompt_tokens
        or total_tokens < prompt_tokens + completion_tokens
    ):
        raise ValueError("usage token totals are inconsistent")
    return {
        "prompt": prompt_tokens,
        "completion": completion_tokens,
        "total": total_tokens,
        "cached": cached_tokens,
    }


def _estimated_cost(
    token_usage: dict[str, int] | None, model: str | None = None
) -> float | None:
    if token_usage is None:
        return None
    selected_model = model or os.environ.get("MOONSHOT_KIMI_MODEL", DEFAULT_MODEL)
    prices = MODEL_PRICES_PER_1M.get(selected_model)
    if prices is None:
        return None
    uncached_tokens = max(0, token_usage["prompt"] - token_usage["cached"])
    return (
        uncached_tokens * prices["input"]
        + token_usage["cached"] * prices["cache_hit"]
        + token_usage["completion"] * prices["output"]
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


def _result_with_evidence(
    body: dict[str, Any],
    data: dict[str, Any],
    response: httpx.Response,
    settings: dict[str, Any],
) -> dict[str, Any]:
    choice = _first_choice(data)
    requested_reasoning = body.get("reasoning")
    metadata = {
        "api_route": settings["api_route"],
        "requested_model": body["model"],
        "expected_served_model": settings["expected_served_model"],
        "served_model": data.get("model"),
        "finish_reason": choice.get("finish_reason") if choice else None,
        "requested_reasoning_effort": (
            requested_reasoning.get("effort")
            if isinstance(requested_reasoning, dict)
            else body.get("reasoning_effort")
        ),
        "requested_output_contract": settings["output_contract"],
        "requested_max_completion_tokens": settings["max_completion_tokens"],
        "served_provider": data.get("provider"),
        "response_id": data.get("id"),
        "request_id": response.headers.get("x-request-id"),
    }
    result: dict[str, Any] = {
        "metadata": {key: value for key, value in metadata.items() if value is not None}
    }
    try:
        token_usage = _token_usage(data)
    except (TypeError, ValueError) as exc:
        result["metadata"]["usage_error"] = str(exc)
        token_usage = None
    if token_usage is not None:
        result["tokenUsage"] = token_usage
        cost = _estimated_cost(token_usage, body["model"])
        if cost is not None:
            result["cost"] = cost
    return result


def call_api(prompt: str, options: dict[str, Any], context: dict[str, Any]):
    del context
    try:
        settings = _request_settings(options)
        body = _build_body(prompt, options)
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}

    api_key = os.environ.get(settings["api_key_env"])
    if not api_key:
        return {"error": f"{settings['api_key_env']} is not configured"}

    timeout = float(os.environ.get("MOONSHOT_KIMI_TIMEOUT_SECONDS", "180"))
    max_attempts = int(os.environ.get("MOONSHOT_KIMI_MAX_ATTEMPTS", "4"))
    response: httpx.Response | None = None
    data: dict[str, Any] | None = None
    for attempt in range(max_attempts):
        try:
            response = httpx.post(
                settings["api_url"],
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=body,
                timeout=timeout,
            )
            response.raise_for_status()
            parsed = response.json()
            if not isinstance(parsed, dict):
                raise ValueError("Kimi response JSON must be an object")
            data = parsed
            break
        except httpx.HTTPStatusError as exc:
            retryable = exc.response.status_code in {429, 500, 502, 503, 504}
            if not retryable or attempt + 1 == max_attempts:
                return {
                    "error": f"API error: {exc.response.status_code} {exc.response.text}"
                }
            time.sleep(min(2**attempt, 8))
        except Exception as exc:
            return {"error": f"{type(exc).__name__}: {exc}"}

    if response is None or data is None:
        return {"error": "Kimi API returned no response"}

    result = _result_with_evidence(body, data, response, settings)
    if result["metadata"].get("usage_error") is not None:
        result["error"] = (
            "Kimi API returned invalid usage evidence: "
            f"{result['metadata']['usage_error']}"
        )
        return result

    if data.get("error") is not None:
        result["error"] = f"Kimi API returned a provider error: {data['error']}"
        return result

    choice = _first_choice(data)
    if choice is None:
        result["error"] = "Kimi API did not return exactly one response choice"
        return result
    finish_reason = choice.get("finish_reason")
    if finish_reason != "stop":
        result["error"] = (
            f"Kimi API response did not finish normally: {finish_reason!r}"
        )
        return result

    served_model = data.get("model")
    if served_model != settings["expected_served_model"]:
        result["error"] = (
            "Kimi API served an unexpected model: "
            f"expected={settings['expected_served_model']!r}, served={served_model!r}"
        )
        return result

    output = _extract_output_text(data)
    if not output:
        result["error"] = "Kimi API returned no output text"
        return result
    contract_error = _contract_error(output, settings["output_contract"])
    if contract_error is not None:
        result["metadata"]["contract_error"] = contract_error
        result["metadata"]["invalid_output_sha256"] = hashlib.sha256(
            output.encode("utf-8")
        ).hexdigest()
        result["error"] = (
            "Kimi API output violated the requested "
            f"{settings['output_contract']} contract: {contract_error}"
        )
        return result

    result["output"] = output
    return result
