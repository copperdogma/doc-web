"""Promptfoo provider for direct xAI Responses API challenger evals.

The maintained crop prompts emit OpenAI-style multimodal chat messages. xAI's
Responses API accepts the same logical content after ``text`` / ``image_url``
blocks are normalized to ``input_text`` / ``input_image``.
"""

from __future__ import annotations

import json
import os
from typing import Any

import httpx


DEFAULT_MODEL = "grok-4.5"
DEFAULT_MAX_OUTPUT_TOKENS = 4096
DEFAULT_TIMEOUT_SECONDS = 180.0


def _content_item_to_responses(item: Any) -> dict[str, Any] | None:
    if isinstance(item, str):
        return {"type": "input_text", "text": item}
    if not isinstance(item, dict):
        return None

    item_type = item.get("type")
    if item_type in {"input_text", "input_image"}:
        return item
    if item_type == "text":
        return {"type": "input_text", "text": str(item.get("text") or "")}
    if item_type == "image_url":
        image_url = item.get("image_url")
        if isinstance(image_url, dict):
            image_url = image_url.get("url")
        if image_url:
            return {
                "type": "input_image",
                "image_url": str(image_url),
                "detail": os.environ.get("XAI_GROK_IMAGE_DETAIL", "high"),
            }
    return None


def _normalize_input(prompt: str) -> list[dict[str, Any]] | str:
    try:
        parsed = json.loads(prompt)
    except json.JSONDecodeError:
        return prompt
    if not isinstance(parsed, list):
        return prompt

    normalized: list[dict[str, Any]] = []
    for message in parsed:
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        content_items = content if isinstance(content, list) else [content]
        normalized_content = [
            converted
            for item in content_items
            if (converted := _content_item_to_responses(item)) is not None
        ]
        normalized.append(
            {
                "role": str(message.get("role") or "user"),
                "content": normalized_content,
            }
        )
    return normalized or prompt


def _build_body(prompt: str) -> dict[str, Any]:
    return {
        "model": os.environ.get("XAI_GROK_MODEL", DEFAULT_MODEL),
        "input": _normalize_input(prompt),
        "reasoning": {
            "effort": os.environ.get("XAI_GROK_REASONING_EFFORT", "low")
        },
        "max_output_tokens": int(
            os.environ.get(
                "XAI_GROK_MAX_OUTPUT_TOKENS", str(DEFAULT_MAX_OUTPUT_TOKENS)
            )
        ),
        # xAI recommends disabling storage for requests containing images.
        "store": False,
    }


def _extract_output_text(data: dict[str, Any]) -> str:
    output_text = data.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    chunks: list[str] = []
    for output_item in data.get("output", []):
        if not isinstance(output_item, dict):
            continue
        for content_item in output_item.get("content", []):
            if not isinstance(content_item, dict):
                continue
            if content_item.get("type") in {"output_text", "text"}:
                text_value = content_item.get("text")
                if isinstance(text_value, str):
                    chunks.append(text_value)
    return "\n".join(chunks).strip()


def _token_usage(data: dict[str, Any]) -> dict[str, int] | None:
    usage = data.get("usage")
    if not isinstance(usage, dict):
        return None
    prompt_tokens = int(usage.get("input_tokens") or 0)
    completion_tokens = int(usage.get("output_tokens") or 0)
    input_details = usage.get("input_tokens_details")
    cached_tokens = (
        int(input_details.get("cached_tokens") or 0)
        if isinstance(input_details, dict)
        else 0
    )
    return {
        "prompt": prompt_tokens,
        "completion": completion_tokens,
        "total": int(usage.get("total_tokens") or prompt_tokens + completion_tokens),
        "cached": cached_tokens,
    }


def _reported_cost(data: dict[str, Any]) -> float | None:
    usage = data.get("usage")
    if not isinstance(usage, dict):
        return None
    ticks = usage.get("cost_in_usd_ticks")
    if ticks is None:
        return None
    # xAI reports 1 USD as 10^10 cost ticks.
    return float(ticks) / 10_000_000_000


def call_api(prompt: str, options: dict[str, Any], context: dict[str, Any]):
    key_env = os.environ.get("XAI_API_KEY_ENV", "XAI_API_KEY")
    api_key = os.environ.get(key_env) or os.environ.get("XAI_API_KEY")
    if not api_key:
        return {"error": f"{key_env} is not configured"}

    try:
        response = httpx.post(
            "https://api.x.ai/v1/responses",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=_build_body(prompt),
            timeout=float(
                os.environ.get(
                    "XAI_GROK_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)
                )
            ),
        )
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPStatusError as exc:
        return {"error": f"API error: {exc.response.status_code} {exc.response.text}"}
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}

    output = _extract_output_text(data)
    if not output:
        return {"error": "xAI Responses API returned no output text"}

    result: dict[str, Any] = {"output": output}
    token_usage = _token_usage(data)
    if token_usage is not None:
        result["tokenUsage"] = token_usage
    cost = _reported_cost(data)
    if cost is not None:
        result["cost"] = cost
    return result
