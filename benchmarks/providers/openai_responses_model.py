"""Promptfoo provider for explicit OpenAI Responses model challenger runs.

The pinned promptfoo version can mis-normalize image prompts for new OpenAI
model ids. This provider keeps the Responses request body explicit and lets
eval commands select the model, reasoning effort, and token pricing through
environment variables.

Usage from ``benchmarks/``:
  OPENAI_RESPONSES_MODEL=gpt-5.6-sol \
  OPENAI_RESPONSES_REASONING_EFFORT=none \
  OPENAI_RESPONSES_INPUT_PRICE_PER_1M=5 \
  OPENAI_RESPONSES_OUTPUT_PRICE_PER_1M=30 \
  ../scripts/run_with_doc_web_env.py promptfoo eval \
    -c tasks/image-crop-extraction.yaml \
    --providers "python:$(pwd)/providers/openai_responses_model.py" ...
"""

from __future__ import annotations

import json
import os
from typing import Any

import httpx


DEFAULT_MODEL = "gpt-5.6-sol"
DEFAULT_MAX_OUTPUT_TOKENS = 4096
DEFAULT_TIMEOUT_SECONDS = 120.0


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


def _optional_int(name: str) -> int | None:
    value = os.environ.get(name)
    if not value:
        return None
    return int(value)


def _build_body(prompt: str) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": os.environ.get("OPENAI_RESPONSES_MODEL", DEFAULT_MODEL),
        "input": _normalize_input(prompt),
        "max_output_tokens": int(
            os.environ.get(
                "OPENAI_RESPONSES_MAX_OUTPUT_TOKENS",
                str(DEFAULT_MAX_OUTPUT_TOKENS),
            )
        ),
    }

    reasoning: dict[str, Any] = {}
    reasoning_effort = os.environ.get("OPENAI_RESPONSES_REASONING_EFFORT")
    if reasoning_effort:
        reasoning["effort"] = reasoning_effort
    reasoning_mode = os.environ.get("OPENAI_RESPONSES_REASONING_MODE")
    if reasoning_mode:
        reasoning["mode"] = reasoning_mode
    if reasoning:
        body["reasoning"] = reasoning

    verbosity = os.environ.get("OPENAI_RESPONSES_VERBOSITY")
    if verbosity:
        body["text"] = {"verbosity": verbosity}

    seed = _optional_int("OPENAI_RESPONSES_SEED")
    if seed is not None:
        body["seed"] = seed

    return body


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


def _env_float(name: str) -> float | None:
    value = os.environ.get(name)
    if not value:
        return None
    return float(value)


def _estimated_cost(token_usage: dict[str, int] | None) -> float | None:
    if token_usage is None:
        return None
    input_price = _env_float("OPENAI_RESPONSES_INPUT_PRICE_PER_1M")
    output_price = _env_float("OPENAI_RESPONSES_OUTPUT_PRICE_PER_1M")
    if input_price is None or output_price is None:
        return None
    return (
        token_usage["prompt"] * input_price
        + token_usage["completion"] * output_price
    ) / 1_000_000


def call_api(prompt: str, options: dict[str, Any], context: dict[str, Any]):
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get(
        "DOC_WEB_OPENAI_API_KEY"
    )
    if not api_key:
        return {"error": "OPENAI_API_KEY is not configured"}

    timeout = float(
        os.environ.get(
            "OPENAI_RESPONSES_TIMEOUT_SECONDS",
            str(DEFAULT_TIMEOUT_SECONDS),
        )
    )

    try:
        response = httpx.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=_build_body(prompt),
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
