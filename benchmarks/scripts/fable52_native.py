# ruff: noqa: E402
"""Exact native Anthropic continuation; no remote fallback or semantic cleanup."""

import base64
import json
import os
import sys
from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "benchmarks/providers"))
import fable52_guard as guard

MODEL = "claude-fable-5-2"


def body(system, text, image, mime, schema):
    b = {
        "model": MODEL,
        "max_tokens": int(os.environ.get("FABLE52_MAX_TOKENS", "32768")),
        "output_config": {"effort": os.environ.get("FABLE52_EFFORT", "xhigh")},
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime,
                            "data": base64.b64encode(image).decode(),
                        },
                    },
                ],
            }
        ],
    }
    if system:
        b["system"] = system
    if schema:
        from anthropic import transform_schema

        b["output_config"]["format"] = {
            "type": "json_schema",
            "schema": transform_schema(schema),
        }
    return b


def send(b, stage):
    os.environ["FABLE52_STAGE"] = stage
    guard.install()
    r = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
        },
        json=b,
        timeout=900,
    )
    r.raise_for_status()
    d = r.json()
    assert (
        d["model"] == MODEL
        and d["type"] == "message"
        and d["stop_reason"] == "end_turn"
        and not d.get("error")
    )
    parts = [p["text"] for p in d["content"] if p["type"] == "text"]
    assert len(parts) == 1
    raw = parts[0]
    u = d["usage"]
    assert type(u["input_tokens"]) is int and type(u["output_tokens"]) is int
    return raw, d


def generate(system, text, image, mime, schema, stage):
    raw, d = send(body(system, text, image, mime, schema), stage)
    u = d["usage"]
    d["modelVersion"] = MODEL
    d["responseId"] = d["id"]
    d["usageMetadata"] = {
        "promptTokenCount": u["input_tokens"],
        "candidatesTokenCount": u["output_tokens"],
        "thoughtsTokenCount": 0,
        "cachedContentTokenCount": u.get("cache_read_input_tokens", 0),
    }
    if schema:
        json.loads(raw)
    return raw, d
