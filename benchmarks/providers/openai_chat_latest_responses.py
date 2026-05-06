"""Promptfoo provider for the OpenAI `chat-latest` Responses API alias.

Promptfoo 0.121.1 classifies model capabilities from the model id string. The
bare `chat-latest` alias does not start with `gpt-5`, so the built-in OpenAI
providers send unsupported GPT-5 parameters. This provider keeps the request
body explicit for bounded alias challenger runs.

Usage from a config under `benchmarks/tasks/`:
  - id: "python:../providers/openai_chat_latest_responses.py"
    label: "OpenAI chat-latest Responses"

Usage as a CLI provider override from `benchmarks/`:
  --providers python:/absolute/path/to/benchmarks/providers/openai_chat_latest_responses.py
"""

from __future__ import annotations

import json
import os
from typing import Any

import httpx


DEFAULT_MODEL = "chat-latest"
DEFAULT_MAX_OUTPUT_TOKENS = 4096
GPT55_INPUT_PRICE_PER_1M = 5.0
GPT55_OUTPUT_PRICE_PER_1M = 30.0


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
            return {"type": "input_image", "image_url": str(image_url)}
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
        role = str(message.get("role") or "user")
        content = message.get("content")
        content_items = content if isinstance(content, list) else [content]
        normalized_content = [
            converted
            for item in content_items
            if (converted := _content_item_to_responses(item)) is not None
        ]
        normalized.append({"role": role, "content": normalized_content})
    return normalized or prompt


def _build_body(prompt: str) -> dict[str, Any]:
    return {
        "model": os.environ.get("OPENAI_CHAT_LATEST_MODEL", DEFAULT_MODEL),
        "input": _normalize_input(prompt),
        "max_output_tokens": int(
            os.environ.get(
                "OPENAI_CHAT_LATEST_MAX_OUTPUT_TOKENS",
                str(DEFAULT_MAX_OUTPUT_TOKENS),
            )
        ),
    }


def _extract_output_text(data: dict[str, Any]) -> str:
    output_text = data.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text

    chunks: list[str] = []
    for output_item in data.get("output", []):
        if not isinstance(output_item, dict):
            continue
        for content_item in output_item.get("content", []):
            if not isinstance(content_item, dict):
                continue
            if content_item.get("type") in {"output_text", "text"}:
                text = content_item.get("text")
                if isinstance(text, str):
                    chunks.append(text)
    return "\n".join(chunks).strip()


def _token_usage(data: dict[str, Any]) -> dict[str, int] | None:
    usage = data.get("usage")
    if not isinstance(usage, dict):
        return None
    prompt_tokens = int(usage.get("input_tokens") or usage.get("prompt_tokens") or 0)
    completion_tokens = int(
        usage.get("output_tokens") or usage.get("completion_tokens") or 0
    )
    total_tokens = int(usage.get("total_tokens") or prompt_tokens + completion_tokens)
    return {
        "prompt": prompt_tokens,
        "completion": completion_tokens,
        "total": total_tokens,
    }


def _estimated_cost(token_usage: dict[str, int] | None) -> float | None:
    if token_usage is None:
        return None
    return (
        token_usage["prompt"] * GPT55_INPUT_PRICE_PER_1M
        + token_usage["completion"] * GPT55_OUTPUT_PRICE_PER_1M
    ) / 1_000_000


def call_api(prompt: str, options: dict[str, Any], context: dict[str, Any]):
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get(
        "DOC_WEB_OPENAI_API_KEY"
    )
    if not api_key:
        return {"error": "OPENAI_API_KEY is not configured"}

    body = _build_body(prompt)
    timeout = float(os.environ.get("OPENAI_CHAT_LATEST_TIMEOUT_SECONDS", "120"))
    try:
        response = httpx.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
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
        return {"error": "OpenAI Responses API returned no output text"}

    token_usage = _token_usage(data)
    result: dict[str, Any] = {"output": output}
    if token_usage is not None:
        result["tokenUsage"] = token_usage
        cost = _estimated_cost(token_usage)
        if cost is not None:
            result["cost"] = cost
    return result
