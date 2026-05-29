"""Promptfoo provider for bounded Claude Opus 4.8 Messages API evals.

The built-in promptfoo Anthropic provider in the repo's pinned version sends
`temperature`, which Opus 4.8 rejects. This provider keeps the request body
explicit for challenger runs and preserves the repo's existing multimodal
prompt shapes.

Usage from benchmarks/:
  ../scripts/run_with_doc_web_env.py promptfoo eval \
    -c tasks/image-crop-extraction.yaml \
    --providers python:$(pwd)/providers/anthropic_opus48_messages.py \
    --filter-prompts conservative-count --no-cache -j 1
"""

from __future__ import annotations

import base64
import json
import os
from typing import Any

import httpx


DEFAULT_MODEL = "claude-opus-4-8"
DEFAULT_MAX_TOKENS = 4096
OPUS48_INPUT_PRICE_PER_1M = 5.00
OPUS48_OUTPUT_PRICE_PER_1M = 25.00


def _decode_data_uri(data_uri: str) -> tuple[str, str] | None:
    if not data_uri.startswith("data:") or "," not in data_uri:
        return None
    header, data = data_uri.split(",", 1)
    if ";base64" not in header:
        return None
    media_type = header.removeprefix("data:").split(";", 1)[0] or "image/jpeg"
    try:
        base64.b64decode(data, validate=True)
    except Exception:
        return None
    return media_type, data


def _content_item_to_anthropic(item: Any) -> dict[str, Any] | None:
    if isinstance(item, str):
        return {"type": "text", "text": item}
    if not isinstance(item, dict):
        return None

    item_type = item.get("type")
    if item_type in {"text", "input_text"}:
        return {"type": "text", "text": str(item.get("text") or "")}

    if item_type == "image" and isinstance(item.get("source"), dict):
        return item

    data_uri: str | None = None
    if item_type == "image_url":
        image_url = item.get("image_url")
        if isinstance(image_url, dict):
            image_url = image_url.get("url")
        if isinstance(image_url, str):
            data_uri = image_url
    elif item_type == "input_image":
        image_url = item.get("image_url")
        if isinstance(image_url, str):
            data_uri = image_url

    if data_uri:
        decoded = _decode_data_uri(data_uri)
        if decoded is None:
            return None
        media_type, data = decoded
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": data,
            },
        }

    return None


def _normalize_messages(prompt: str) -> list[dict[str, Any]]:
    try:
        parsed = json.loads(prompt)
    except json.JSONDecodeError:
        return [{"role": "user", "content": [{"type": "text", "text": prompt}]}]

    if not isinstance(parsed, list):
        return [{"role": "user", "content": [{"type": "text", "text": prompt}]}]

    messages: list[dict[str, Any]] = []
    for message in parsed:
        if not isinstance(message, dict):
            continue
        role = str(message.get("role") or "user")
        content = message.get("content")
        content_items = content if isinstance(content, list) else [content]
        normalized = [
            converted
            for item in content_items
            if (converted := _content_item_to_anthropic(item)) is not None
        ]
        if normalized:
            messages.append({"role": role, "content": normalized})

    return messages or [{"role": "user", "content": [{"type": "text", "text": prompt}]}]


def _build_body(prompt: str) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": os.environ.get("ANTHROPIC_OPUS48_MODEL", DEFAULT_MODEL),
        "max_tokens": int(
            os.environ.get("ANTHROPIC_OPUS48_MAX_TOKENS", str(DEFAULT_MAX_TOKENS))
        ),
        "messages": _normalize_messages(prompt),
    }

    if os.environ.get("ANTHROPIC_OPUS48_THINKING", "adaptive") == "adaptive":
        body["thinking"] = {"type": "adaptive"}

    effort = os.environ.get("ANTHROPIC_OPUS48_EFFORT", "high")
    if effort:
        body["output_config"] = {"effort": effort}

    speed = os.environ.get("ANTHROPIC_OPUS48_SPEED")
    if speed:
        body["speed"] = speed

    return body


def _extract_output_text(data: dict[str, Any]) -> str:
    chunks: list[str] = []
    for item in data.get("content", []):
        if not isinstance(item, dict):
            continue
        if item.get("type") == "text" and isinstance(item.get("text"), str):
            chunks.append(item["text"])
    return "\n".join(chunks).strip()


def _token_usage(data: dict[str, Any]) -> dict[str, int] | None:
    usage = data.get("usage")
    if not isinstance(usage, dict):
        return None
    prompt_tokens = int(usage.get("input_tokens") or 0)
    completion_tokens = int(usage.get("output_tokens") or 0)
    return {
        "prompt": prompt_tokens,
        "completion": completion_tokens,
        "total": prompt_tokens + completion_tokens,
        "cached": int(usage.get("cache_read_input_tokens") or 0),
    }


def _estimated_cost(token_usage: dict[str, int] | None) -> float | None:
    if token_usage is None:
        return None
    return (
        token_usage["prompt"] * OPUS48_INPUT_PRICE_PER_1M
        + token_usage["completion"] * OPUS48_OUTPUT_PRICE_PER_1M
    ) / 1_000_000


def call_api(prompt: str, options: dict[str, Any], context: dict[str, Any]):
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get(
        "DOC_WEB_ANTHROPIC_API_KEY"
    )
    if not api_key:
        return {"error": "ANTHROPIC_API_KEY is not configured"}

    body = _build_body(prompt)
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
        data = response.json()
    except httpx.HTTPStatusError as exc:
        return {"error": f"API error: {exc.response.status_code} {exc.response.text}"}
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}

    output = _extract_output_text(data)
    if not output:
        return {"error": "Anthropic Messages API returned no text output"}

    token_usage = _token_usage(data)
    result: dict[str, Any] = {"output": output}
    if token_usage is not None:
        result["tokenUsage"] = token_usage
        cost = _estimated_cost(token_usage)
        if cost is not None:
            result["cost"] = cost
    return result
