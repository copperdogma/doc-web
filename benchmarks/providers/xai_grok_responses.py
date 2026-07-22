"""Promptfoo provider for direct xAI Responses API challenger evals.

The maintained crop prompts emit OpenAI-style multimodal chat messages. xAI's
Responses API accepts the same logical content after ``text`` / ``image_url``
blocks are normalized to ``input_text`` / ``input_image``.

The default ``crop_regions`` output contract preserves the maintained detector
lane. Set ``XAI_GROK_OUTPUT_CONTRACT=page_context_validation`` (or pass the
same value as provider config ``output_contract``) for the page-context gate.
When requesting an alias, set ``XAI_GROK_EXPECTED_SERVED_MODEL`` (or provider
config ``expected_served_model``) to the exact identity the response must report.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from typing import Any

import httpx


DEFAULT_MODEL = "grok-4.5"
DEFAULT_MAX_OUTPUT_TOKENS = 4096
DEFAULT_TIMEOUT_SECONDS = 180.0
DEFAULT_IMAGE_DETAIL = "high"
DEFAULT_OUTPUT_CONTRACT = "crop_regions"

CROP_RESPONSE_FORMAT = {
    "type": "json_schema",
    "name": "crop_regions",
    "strict": True,
    "schema": {
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
                            "items": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
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
    },
}

PAGE_CONTEXT_RESPONSE_FORMAT = {
    "type": "json_schema",
    "name": "page_context_validation",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": ["pass", "fail"]},
            "has_page_text": {"type": "boolean"},
            "excessive_blank": {"type": "boolean"},
            "reason": {"type": "string"},
        },
        "required": [
            "verdict",
            "has_page_text",
            "excessive_blank",
            "reason",
        ],
        "additionalProperties": False,
    },
}

OUTPUT_CONTRACTS = {
    "crop_regions": CROP_RESPONSE_FORMAT,
    "page_context_validation": PAGE_CONTEXT_RESPONSE_FORMAT,
}


def _provider_config(options: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(options, dict):
        return {}
    nested = options.get("config")
    config = dict(nested) if isinstance(nested, dict) else {}
    for key in {
        "image_detail",
        "expected_served_model",
        "max_output_tokens",
        "model",
        "output_contract",
        "reasoning_effort",
    }:
        if key in options and key not in config:
            config[key] = options[key]
    return config


def _request_settings(options: dict[str, Any] | None = None) -> dict[str, Any]:
    config = _provider_config(options)
    output_contract = str(
        config.get("output_contract")
        or os.environ.get("XAI_GROK_OUTPUT_CONTRACT", DEFAULT_OUTPUT_CONTRACT)
    )
    if output_contract not in OUTPUT_CONTRACTS:
        supported = ", ".join(sorted(OUTPUT_CONTRACTS))
        raise ValueError(
            f"Unsupported xAI output contract {output_contract!r}; choose {supported}"
        )

    requested_model = str(
        config.get("model") or os.environ.get("XAI_GROK_MODEL", DEFAULT_MODEL)
    )
    return {
        "model": requested_model,
        "expected_served_model": str(
            config.get("expected_served_model")
            or os.environ.get("XAI_GROK_EXPECTED_SERVED_MODEL", requested_model)
        ),
        "reasoning_effort": str(
            config.get("reasoning_effort")
            or os.environ.get("XAI_GROK_REASONING_EFFORT", "low")
        ),
        "max_output_tokens": int(
            config.get("max_output_tokens")
            or os.environ.get(
                "XAI_GROK_MAX_OUTPUT_TOKENS", str(DEFAULT_MAX_OUTPUT_TOKENS)
            )
        ),
        "image_detail": str(
            config.get("image_detail")
            or os.environ.get("XAI_GROK_IMAGE_DETAIL", DEFAULT_IMAGE_DETAIL)
        ),
        "output_contract": output_contract,
        # xAI recommends disabling storage for requests containing images.
        "store": False,
    }


def _content_item_to_responses(item: Any, image_detail: str) -> dict[str, Any]:
    if isinstance(item, str):
        if not item:
            raise ValueError("Prompt content text must not be empty")
        return {"type": "input_text", "text": item}
    if not isinstance(item, dict):
        raise ValueError("Prompt content items must be strings or objects")

    item_type = item.get("type")
    if item_type in {"input_text", "text"}:
        text_value = item.get("text")
        if not isinstance(text_value, str) or not text_value:
            raise ValueError(f"Prompt {item_type} content requires non-empty text")
        return {"type": "input_text", "text": text_value}
    if item_type in {"input_image", "image_url"}:
        image_url = item.get("image_url")
        if isinstance(image_url, dict):
            image_url = image_url.get("url")
        if not isinstance(image_url, str) or not image_url:
            raise ValueError(
                f"Prompt {item_type} content requires a non-empty image URL"
            )
        return {
            "type": "input_image",
            "image_url": image_url,
            "detail": str(item.get("detail") or image_detail),
        }
    raise ValueError(f"Unsupported prompt content type: {item_type!r}")


def _normalize_input(prompt: str, image_detail: str) -> list[dict[str, Any]] | str:
    try:
        parsed = json.loads(prompt)
    except json.JSONDecodeError:
        return prompt
    if not isinstance(parsed, list):
        return prompt
    if not parsed:
        raise ValueError("Prompt message list must not be empty")

    normalized: list[dict[str, Any]] = []
    for message_index, message in enumerate(parsed):
        if not isinstance(message, dict):
            raise ValueError(f"Prompt message {message_index} must be an object")
        content = message.get("content")
        if content is None:
            raise ValueError(f"Prompt message {message_index} is missing content")
        content_items = content if isinstance(content, list) else [content]
        if not content_items:
            raise ValueError(
                f"Prompt message {message_index} content must not be empty"
            )
        normalized_content = [
            _content_item_to_responses(item, image_detail) for item in content_items
        ]
        normalized.append(
            {
                "role": str(message.get("role") or "user"),
                "content": normalized_content,
            }
        )
    return normalized


def _build_body(prompt: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
    settings = _request_settings(options)
    return {
        "model": settings["model"],
        "input": _normalize_input(prompt, settings["image_detail"]),
        "reasoning": {"effort": settings["reasoning_effort"]},
        "max_output_tokens": settings["max_output_tokens"],
        "store": settings["store"],
        "text": {"format": OUTPUT_CONTRACTS[settings["output_contract"]]},
    }


def _extract_output_text(data: dict[str, Any]) -> str:
    output = data.get("output")
    if not isinstance(output, list):
        return ""
    messages = [
        item
        for item in output
        if isinstance(item, dict) and item.get("type") == "message"
    ]
    if not messages:
        return ""
    content = messages[-1].get("content")
    if not isinstance(content, list):
        return ""
    chunks: list[str] = []
    for content_item in content:
        if not isinstance(content_item, dict):
            continue
        if content_item.get("type") == "output_text":
            text_value = content_item.get("text")
            if isinstance(text_value, str):
                chunks.append(text_value)
    return "\n".join(chunks).strip()


def _is_finite_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    return isinstance(value, float) and math.isfinite(value)


def _validate_crop_regions(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return "root must be an object"
    if set(payload) != {"images"}:
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
            return (
                f"images[{index}] must contain description and bbox with only "
                "optional adjacent_text"
            )
        if not isinstance(image["description"], str):
            return f"images[{index}].description must be a string"
        if "adjacent_text" in image and not isinstance(image["adjacent_text"], str):
            return f"images[{index}].adjacent_text must be a string"
        bbox = image["bbox"]
        if not isinstance(bbox, list) or len(bbox) != 4:
            return f"images[{index}].bbox must be an array of four numbers"
        if any(
            not _is_finite_number(value) or value < 0 or value > 1 for value in bbox
        ):
            return f"images[{index}].bbox values must be finite numbers from 0 to 1"
    return None


def _validate_page_context(payload: Any) -> str | None:
    required = {"verdict", "has_page_text", "excessive_blank", "reason"}
    if not isinstance(payload, dict):
        return "root must be an object"
    if set(payload) != required:
        return (
            "root must contain exactly verdict, has_page_text, excessive_blank, reason"
        )
    if not isinstance(payload["verdict"], str) or payload["verdict"] not in {
        "pass",
        "fail",
    }:
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
    except json.JSONDecodeError as exc:
        return f"invalid JSON at line {exc.lineno} column {exc.colno}"
    except (RecursionError, ValueError) as exc:
        return f"invalid JSON structure: {type(exc).__name__}"
    if output_contract == "crop_regions":
        return _validate_crop_regions(payload)
    if output_contract == "page_context_validation":
        return _validate_page_context(payload)
    return f"unsupported output contract {output_contract!r}"


def _nonnegative_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _usage_evidence_error(data: dict[str, Any]) -> str | None:
    usage = data.get("usage")
    if usage is None:
        return None
    if not isinstance(usage, dict):
        return "usage must be an object"
    try:
        for field in {"input_tokens", "output_tokens", "total_tokens"}:
            if usage.get(field) is not None:
                _nonnegative_int(usage[field], f"usage.{field}")
        input_details = usage.get("input_tokens_details")
        if input_details is not None:
            if not isinstance(input_details, dict):
                return "usage.input_tokens_details must be an object"
            if input_details.get("cached_tokens") is not None:
                _nonnegative_int(
                    input_details["cached_tokens"],
                    "usage.input_tokens_details.cached_tokens",
                )
        ticks = usage.get("cost_in_usd_ticks")
        if ticks is not None:
            if not isinstance(ticks, (int, float)) or isinstance(ticks, bool):
                return "usage.cost_in_usd_ticks must be a finite non-negative number"
            if not math.isfinite(ticks) or ticks < 0:
                return "usage.cost_in_usd_ticks must be a finite non-negative number"
    except (OverflowError, TypeError, ValueError) as exc:
        return str(exc)
    return None


def _token_usage(data: dict[str, Any]) -> dict[str, int] | None:
    usage = data.get("usage")
    if not isinstance(usage, dict):
        return None
    try:
        prompt_tokens = _nonnegative_int(
            usage.get("input_tokens", 0), "usage.input_tokens"
        )
        completion_tokens = _nonnegative_int(
            usage.get("output_tokens", 0), "usage.output_tokens"
        )
        input_details = usage.get("input_tokens_details")
        cached_tokens = (
            _nonnegative_int(
                input_details.get("cached_tokens", 0),
                "usage.input_tokens_details.cached_tokens",
            )
            if isinstance(input_details, dict)
            else 0
        )
        total_tokens = _nonnegative_int(
            usage.get("total_tokens", prompt_tokens + completion_tokens),
            "usage.total_tokens",
        )
    except (TypeError, ValueError):
        return None
    return {
        "prompt": prompt_tokens,
        "completion": completion_tokens,
        "total": total_tokens,
        "cached": cached_tokens,
    }


def _reported_cost(data: dict[str, Any]) -> float | None:
    usage = data.get("usage")
    if not isinstance(usage, dict):
        return None
    ticks = usage.get("cost_in_usd_ticks")
    if ticks is None:
        return None
    if not isinstance(ticks, (int, float)) or isinstance(ticks, bool):
        return None
    try:
        numeric_ticks = float(ticks)
    except (OverflowError, TypeError, ValueError):
        return None
    if not math.isfinite(numeric_ticks) or numeric_ticks < 0:
        return None
    # xAI reports 1 USD as 10^10 cost ticks.
    return numeric_ticks / 10_000_000_000


def _provider_error(data: dict[str, Any]) -> Any | None:
    if "error" in data and data["error"] is not None:
        return data["error"]
    output = data.get("output")
    if not isinstance(output, list):
        return None
    for item in output:
        if not isinstance(item, dict):
            continue
        if item.get("type") == "error":
            return item
        if "error" in item and item["error"] is not None:
            return item["error"]
    return None


def _error_summary(error: Any) -> str:
    if isinstance(error, dict):
        message = error.get("message")
        code = error.get("code")
        if message and code:
            return f"{code}: {message}"
        if message:
            return str(message)
    return str(error)


def _response_metadata(
    *,
    body: dict[str, Any],
    data: dict[str, Any],
    response: httpx.Response,
    settings: dict[str, Any],
) -> dict[str, Any]:
    provider_error = _provider_error(data)
    values = {
        "requested_model": body["model"],
        "expected_served_model": settings["expected_served_model"],
        "requested_reasoning_effort": body["reasoning"]["effort"],
        "requested_output_contract": settings["output_contract"],
        "requested_max_output_tokens": body["max_output_tokens"],
        "requested_image_detail": settings["image_detail"],
        "requested_store": body["store"],
        "served_model": data.get("model"),
        "response_status": data.get("status"),
        "incomplete_details": data.get("incomplete_details"),
        "provider_error": provider_error,
        "usage_error": _usage_evidence_error(data),
        "zero_data_retention": response.headers.get("x-zero-data-retention"),
        "service_tier": data.get("service_tier"),
        "response_id": data.get("id"),
    }
    return {key: value for key, value in values.items() if value is not None}


def _result_with_evidence(
    *,
    body: dict[str, Any],
    data: dict[str, Any],
    response: httpx.Response,
    settings: dict[str, Any],
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "metadata": _response_metadata(
            body=body,
            data=data,
            response=response,
            settings=settings,
        )
    }
    token_usage = _token_usage(data)
    if token_usage is not None:
        result["tokenUsage"] = token_usage
    cost = _reported_cost(data)
    if cost is not None:
        result["cost"] = cost
    return result


def call_api(prompt: str, options: dict[str, Any], context: dict[str, Any]):
    key_env = os.environ.get("XAI_API_KEY_ENV", "XAI_API_KEY")
    api_key = os.environ.get(key_env) or os.environ.get("XAI_API_KEY")
    if not api_key:
        return {"error": f"{key_env} is not configured"}

    try:
        settings = _request_settings(options)
        body = _build_body(prompt, options)
        response = httpx.post(
            "https://api.x.ai/v1/responses",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=float(
                os.environ.get("XAI_GROK_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))
            ),
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("xAI Responses API response JSON must be an object")
    except httpx.HTTPStatusError as exc:
        return {"error": f"API error: {exc.response.status_code} {exc.response.text}"}
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}

    result = _result_with_evidence(
        body=body,
        data=data,
        response=response,
        settings=settings,
    )
    provider_error = _provider_error(data)
    if provider_error is not None:
        result["error"] = (
            "xAI Responses API returned a provider error: "
            f"{_error_summary(provider_error)}"
        )
        return result

    response_status = data.get("status")
    if response_status != "completed":
        result["error"] = (
            f"xAI Responses API did not complete: status={response_status!r}"
        )
        return result

    if data.get("incomplete_details") is not None:
        result["error"] = (
            "xAI Responses API reported incomplete details despite completed status"
        )
        return result

    usage_error = result["metadata"].get("usage_error")
    if usage_error is not None:
        result["error"] = (
            f"xAI Responses API returned invalid usage evidence: {usage_error}"
        )
        return result

    served_model = data.get("model")
    expected_served_model = settings["expected_served_model"]
    if served_model != expected_served_model:
        result["error"] = (
            "xAI Responses API served an unexpected model: "
            f"expected={expected_served_model!r}, served={served_model!r}"
        )
        return result

    output = _extract_output_text(data)
    if not output:
        result["error"] = "xAI Responses API returned no output text"
        return result

    contract_error = _contract_error(output, settings["output_contract"])
    if contract_error is not None:
        result["metadata"]["contract_error"] = contract_error
        result["metadata"]["invalid_output_sha256"] = hashlib.sha256(
            output.encode("utf-8")
        ).hexdigest()
        result["error"] = (
            "xAI Responses API output violated the requested "
            f"{settings['output_contract']} contract: {contract_error}"
        )
        return result

    result["output"] = output
    return result
