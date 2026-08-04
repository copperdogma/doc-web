"""Promptfoo provider for qualified first-party OpenAI Responses evals.

The pinned promptfoo version can mis-normalize image prompts for new OpenAI
model ids. This provider keeps the Responses request body explicit, enforces a
strict task schema, and fails closed on lossy input normalization, incomplete
responses, wrong served identity, invalid usage, or contract-invalid output.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from typing import Any

import httpx


DEFAULT_MODEL = "gpt-5.6-sol"
DEFAULT_MAX_OUTPUT_TOKENS = 4096
DEFAULT_TIMEOUT_SECONDS = 120.0
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
        "required": ["verdict", "has_page_text", "excessive_blank", "reason"],
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
        "expected_served_model",
        "image_detail",
        "max_output_tokens",
        "model",
        "output_contract",
        "reasoning_effort",
        "reasoning_mode",
        "verbosity",
    }:
        if key in options and key not in config:
            config[key] = options[key]
    return config


def _request_settings(options: dict[str, Any] | None = None) -> dict[str, Any]:
    config = _provider_config(options)
    model = str(
        config.get("model") or os.environ.get("OPENAI_RESPONSES_MODEL", DEFAULT_MODEL)
    )
    output_contract = str(
        config.get("output_contract")
        or os.environ.get("OPENAI_RESPONSES_OUTPUT_CONTRACT", DEFAULT_OUTPUT_CONTRACT)
    )
    if output_contract not in OUTPUT_CONTRACTS:
        supported = ", ".join(sorted(OUTPUT_CONTRACTS))
        raise ValueError(
            f"Unsupported OpenAI output contract {output_contract!r}; choose {supported}"
        )
    return {
        "model": model,
        "expected_served_model": str(
            config.get("expected_served_model")
            or os.environ.get("OPENAI_RESPONSES_EXPECTED_SERVED_MODEL", model)
        ),
        "reasoning_effort": str(
            config.get("reasoning_effort")
            or os.environ.get("OPENAI_RESPONSES_REASONING_EFFORT", "none")
        ),
        "reasoning_mode": config.get("reasoning_mode")
        or os.environ.get("OPENAI_RESPONSES_REASONING_MODE"),
        "max_output_tokens": int(
            config.get("max_output_tokens")
            or os.environ.get(
                "OPENAI_RESPONSES_MAX_OUTPUT_TOKENS",
                str(DEFAULT_MAX_OUTPUT_TOKENS),
            )
        ),
        "verbosity": config.get("verbosity")
        or os.environ.get("OPENAI_RESPONSES_VERBOSITY"),
        "image_detail": str(
            config.get("image_detail")
            or os.environ.get("OPENAI_RESPONSES_IMAGE_DETAIL", DEFAULT_IMAGE_DETAIL)
        ),
        "output_contract": output_contract,
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
        value = item.get("text")
        if not isinstance(value, str) or not value:
            raise ValueError(f"Prompt {item_type} content requires non-empty text")
        return {"type": "input_text", "text": value}
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


def _normalize_input(prompt: str, image_detail: str = DEFAULT_IMAGE_DETAIL):
    try:
        parsed = json.loads(prompt)
    except json.JSONDecodeError:
        return prompt
    if not isinstance(parsed, list):
        return prompt
    if not parsed:
        raise ValueError("Prompt message list must not be empty")

    normalized = []
    for index, message in enumerate(parsed):
        if not isinstance(message, dict):
            raise ValueError(f"Prompt message {index} must be an object")
        if "content" not in message:
            raise ValueError(f"Prompt message {index} is missing content")
        content = message["content"]
        items = content if isinstance(content, list) else [content]
        if not items:
            raise ValueError(f"Prompt message {index} content must not be empty")
        normalized.append(
            {
                "role": str(message.get("role") or "user"),
                "content": [
                    _content_item_to_responses(item, image_detail) for item in items
                ],
            }
        )
    return normalized


def _build_body(prompt: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
    settings = _request_settings(options)
    reasoning = {"effort": settings["reasoning_effort"]}
    if settings["reasoning_mode"]:
        reasoning["mode"] = settings["reasoning_mode"]
    text = {"format": OUTPUT_CONTRACTS[settings["output_contract"]]}
    if settings["verbosity"]:
        text["verbosity"] = settings["verbosity"]
    return {
        "model": settings["model"],
        "input": _normalize_input(prompt, settings["image_detail"]),
        "reasoning": reasoning,
        "max_output_tokens": settings["max_output_tokens"],
        "store": settings["store"],
        "text": text,
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
    chunks = []
    for item in content:
        if isinstance(item, dict) and item.get("type") == "output_text":
            value = item.get("text")
            if isinstance(value, str):
                chunks.append(value)
    return "\n".join(chunks).strip()


def _token_usage(data: dict[str, Any]) -> dict[str, int] | None:
    usage = data.get("usage")
    if not isinstance(usage, dict):
        return None
    fields = {
        "prompt": usage.get("input_tokens"),
        "completion": usage.get("output_tokens"),
        "total": usage.get("total_tokens"),
    }
    details = usage.get("input_tokens_details")
    fields["cached"] = (
        details.get("cached_tokens", 0) if isinstance(details, dict) else 0
    )
    if fields["total"] is None and all(
        isinstance(fields[key], int) for key in ("prompt", "completion")
    ):
        fields["total"] = fields["prompt"] + fields["completion"]
    if any(
        not isinstance(value, int) or isinstance(value, bool) or value < 0
        for value in fields.values()
    ):
        return None
    return fields


def _env_float(name: str) -> float | None:
    value = os.environ.get(name)
    return float(value) if value else None


def _estimated_cost(token_usage: dict[str, int] | None) -> float | None:
    if token_usage is None:
        return None
    input_price = _env_float("OPENAI_RESPONSES_INPUT_PRICE_PER_1M")
    output_price = _env_float("OPENAI_RESPONSES_OUTPUT_PRICE_PER_1M")
    if input_price is None or output_price is None:
        return None
    cached_price = _env_float("OPENAI_RESPONSES_CACHED_INPUT_PRICE_PER_1M")
    if cached_price is None:
        cached_price = input_price
    cached = min(token_usage.get("cached", 0), token_usage["prompt"])
    uncached = token_usage["prompt"] - cached
    return (
        uncached * input_price
        + cached * cached_price
        + token_usage["completion"] * output_price
    ) / 1_000_000


def _contract_error(output: str, output_contract: str) -> str | None:
    try:
        payload = json.loads(output)
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        return f"invalid JSON: {type(exc).__name__}"
    if not isinstance(payload, dict):
        return "root must be an object"
    if output_contract == "crop_regions":
        if set(payload) != {"images"} or not isinstance(payload["images"], list):
            return "root must contain only an images array"
        for index, image in enumerate(payload["images"]):
            if not isinstance(image, dict) or set(image) != {"description", "bbox"}:
                return f"images[{index}] must contain exactly description and bbox"
            if not isinstance(image["description"], str):
                return f"images[{index}].description must be a string"
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
            if bbox[0] >= bbox[2] or bbox[1] >= bbox[3]:
                return f"images[{index}].bbox must have positive width and height"
        return None
    required = {"verdict", "has_page_text", "excessive_blank", "reason"}
    if set(payload) != required:
        return "page-context root fields do not match the strict contract"
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


def _response_metadata(
    body: dict[str, Any],
    data: dict[str, Any],
    response: httpx.Response,
    settings: dict[str, Any],
) -> dict[str, Any]:
    values = {
        "requested_model": body["model"],
        "expected_served_model": settings["expected_served_model"],
        "requested_reasoning_effort": settings["reasoning_effort"],
        "requested_reasoning_mode": settings["reasoning_mode"],
        "requested_output_contract": settings["output_contract"],
        "requested_max_output_tokens": settings["max_output_tokens"],
        "requested_image_detail": settings["image_detail"],
        "requested_store": settings["store"],
        "served_model": data.get("model"),
        "response_status": data.get("status"),
        "incomplete_details": data.get("incomplete_details"),
        "service_tier": data.get("service_tier"),
        "response_id": data.get("id"),
        "zero_data_retention": response.headers.get("x-zero-data-retention"),
    }
    return {key: value for key, value in values.items() if value is not None}


def call_api(prompt: str, options: dict[str, Any], context: dict[str, Any]):
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get(
        "DOC_WEB_OPENAI_API_KEY"
    )
    if not api_key:
        return {"error": "OPENAI_API_KEY is not configured"}

    try:
        settings = _request_settings(options)
        body = _build_body(prompt, options)
        response = httpx.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=float(
                os.environ.get(
                    "OPENAI_RESPONSES_TIMEOUT_SECONDS",
                    str(DEFAULT_TIMEOUT_SECONDS),
                )
            ),
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("OpenAI Responses API response JSON must be an object")
    except httpx.HTTPStatusError as exc:
        return {"error": f"API error: {exc.response.status_code} {exc.response.text}"}
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}

    result: dict[str, Any] = {
        "metadata": _response_metadata(body, data, response, settings)
    }
    token_usage = _token_usage(data)
    if token_usage is not None:
        result["tokenUsage"] = token_usage
        cost = _estimated_cost(token_usage)
        if cost is not None:
            result["cost"] = cost

    if data.get("error") is not None:
        result["error"] = (
            f"OpenAI Responses API returned provider error: {data['error']}"
        )
        return result
    if data.get("status") != "completed":
        result["error"] = (
            f"OpenAI Responses API did not complete: status={data.get('status')!r}"
        )
        return result
    if data.get("incomplete_details") is not None:
        result["error"] = "OpenAI Responses API returned incomplete details"
        return result
    if token_usage is None:
        result["error"] = "OpenAI Responses API returned invalid usage evidence"
        return result
    if data.get("model") != settings["expected_served_model"]:
        result["error"] = (
            "OpenAI Responses API served an unexpected model: "
            f"expected={settings['expected_served_model']!r}, "
            f"served={data.get('model')!r}"
        )
        return result

    output = _extract_output_text(data)
    if not output:
        result["error"] = "OpenAI Responses API returned no final output text"
        return result
    contract_error = _contract_error(output, settings["output_contract"])
    if contract_error is not None:
        result["metadata"]["contract_error"] = contract_error
        result["metadata"]["invalid_output_sha256"] = hashlib.sha256(
            output.encode("utf-8")
        ).hexdigest()
        result["error"] = (
            "OpenAI Responses API output violated the requested "
            f"{settings['output_contract']} contract: {contract_error}"
        )
        return result

    result["output"] = output
    return result
