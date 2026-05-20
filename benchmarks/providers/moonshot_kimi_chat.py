"""Promptfoo provider for direct Moonshot Kimi Chat Completions evals.

This intentionally uses Moonshot's first-party OpenAI-compatible endpoint
instead of a third-party router. The checked-in crop prompts already emit
OpenAI-style multimodal chat messages, which Kimi accepts for base64 images.

Usage from benchmarks/:
  DOC_WEB_ENV_FILE=/path/to/main/.env ../scripts/run_with_doc_web_env.py \
    promptfoo eval -c tasks/image-crop-extraction.yaml \
    --providers python:$(pwd)/providers/moonshot_kimi_chat.py \
    --filter-prompts conservative-count --no-cache -j 1
"""

from __future__ import annotations

import json
import os
from typing import Any

import httpx


DEFAULT_MODEL = "kimi-k2.6"
DEFAULT_MAX_COMPLETION_TOKENS = 4096
KIMI_K26_CACHE_HIT_PRICE_PER_1M = 0.16
KIMI_K26_INPUT_PRICE_PER_1M = 0.95
KIMI_K26_OUTPUT_PRICE_PER_1M = 4.00


def _normalize_messages(prompt: str) -> list[dict[str, Any]]:
    try:
        parsed = json.loads(prompt)
    except json.JSONDecodeError:
        return [{"role": "user", "content": prompt}]

    if not isinstance(parsed, list):
        return [{"role": "user", "content": prompt}]

    messages: list[dict[str, Any]] = []
    for item in parsed:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role") or "user")
        content = item.get("content")
        if isinstance(content, list):
            normalized_content = [
                block
                for block in content
                if isinstance(block, dict) and block.get("type") in {"text", "image_url"}
            ]
            messages.append({"role": role, "content": normalized_content})
        elif isinstance(content, str):
            messages.append({"role": role, "content": content})

    return messages or [{"role": "user", "content": prompt}]


def _build_body(prompt: str) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": os.environ.get("MOONSHOT_KIMI_MODEL", DEFAULT_MODEL),
        "messages": _normalize_messages(prompt),
        "max_completion_tokens": int(
            os.environ.get(
                "MOONSHOT_KIMI_MAX_COMPLETION_TOKENS",
                str(DEFAULT_MAX_COMPLETION_TOKENS),
            )
        ),
        "thinking": {
            "type": os.environ.get("MOONSHOT_KIMI_THINKING", "disabled"),
        },
        "response_format": {"type": "json_object"},
    }
    return body


def _extract_output_text(data: dict[str, Any]) -> str:
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        chunks = [
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and isinstance(block.get("text"), str)
        ]
        return "\n".join(chunks).strip()
    return ""


def _token_usage(data: dict[str, Any]) -> dict[str, int] | None:
    usage = data.get("usage")
    if not isinstance(usage, dict):
        return None
    prompt_tokens = int(usage.get("prompt_tokens") or 0)
    completion_tokens = int(usage.get("completion_tokens") or 0)
    total_tokens = int(usage.get("total_tokens") or prompt_tokens + completion_tokens)
    return {
        "prompt": prompt_tokens,
        "completion": completion_tokens,
        "total": total_tokens,
        "cached": int(usage.get("cached_tokens") or 0),
    }


def _estimated_cost(token_usage: dict[str, int] | None) -> float | None:
    if token_usage is None:
        return None
    prompt_tokens = max(0, token_usage["prompt"] - token_usage["cached"])
    cached_tokens = token_usage["cached"]
    return (
        prompt_tokens * KIMI_K26_INPUT_PRICE_PER_1M
        + cached_tokens * KIMI_K26_CACHE_HIT_PRICE_PER_1M
        + token_usage["completion"] * KIMI_K26_OUTPUT_PRICE_PER_1M
    ) / 1_000_000


def call_api(prompt: str, options: dict[str, Any], context: dict[str, Any]):
    api_key = os.environ.get("MOONSHOT_API_KEY") or os.environ.get(
        "DOC_WEB_MOONSHOT_API_KEY"
    )
    if not api_key:
        return {"error": "MOONSHOT_API_KEY is not configured"}

    body = _build_body(prompt)
    timeout = float(os.environ.get("MOONSHOT_KIMI_TIMEOUT_SECONDS", "180"))
    try:
        response = httpx.post(
            "https://api.moonshot.ai/v1/chat/completions",
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
        return {"error": "Moonshot API returned no output text"}

    token_usage = _token_usage(data)
    result: dict[str, Any] = {"output": output}
    if token_usage is not None:
        result["tokenUsage"] = token_usage
        cost = _estimated_cost(token_usage)
        if cost is not None:
            result["cost"] = cost
    return result
