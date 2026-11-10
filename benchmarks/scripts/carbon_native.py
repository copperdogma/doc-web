# ruff: noqa: E402
"""Native Google GenerateContent eval adapter; no caching or model fallback."""

import base64
import json
import os
import sys
from pathlib import Path
import httpx
import jsonschema

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "benchmarks/providers"))
import carbon_guard as guard


def body(model, system, text, images, schema=None):
    config = (
        {"maxOutputTokens": 32768, "thinkingConfig": {"thinkingLevel": "HIGH"}}
        if model == "gemini-4-carbon"
        else {"maxOutputTokens": 16384, "temperature": 0}
    )
    if schema is not None:
        config.update(responseMimeType="application/json", responseJsonSchema=schema)
    b = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": text}]
                + [
                    {
                        "inlineData": {
                            "mimeType": mime,
                            "data": base64.b64encode(image).decode(),
                        }
                    }
                    for image, mime in images
                ],
            }
        ],
        "generationConfig": config,
    }
    if system:
        b["systemInstruction"] = {"parts": [{"text": system}]}
    return b


def parse(d, model, schema=None):
    if d.get("error") or d.get("modelVersion") != model:
        raise ValueError("provider error or exact model identity mismatch")
    candidates = d.get("candidates", [])
    if len(candidates) != 1 or candidates[0].get("finishReason") != "STOP":
        raise ValueError("nonterminal/incomplete output")
    c = candidates[0]
    if c.get("content", {}).get("role") != "model":
        raise ValueError("unexpected role")
    parts = c["content"].get("parts", [])
    if not parts or any(
        set(p) - {"text", "thought", "thoughtSignature"} for p in parts
    ):
        raise ValueError("unknown final output shape")
    final = [p["text"] for p in parts if "text" in p and not p.get("thought")]
    if not final:
        raise ValueError("missing visible output")
    raw = "\n".join(final)
    u = d["usageMetadata"]
    for name in ("promptTokenCount", "candidatesTokenCount"):
        if type(u.get(name)) is not int or u[name] < 0:
            raise ValueError("missing/invalid native usage")
    for name in ("thoughtsTokenCount", "cachedContentTokenCount"):
        if type(u.get(name, 0)) is not int or u.get(name, 0) < 0:
            raise ValueError("invalid native usage")
    if u.get("cachedContentTokenCount", 0) > u["promptTokenCount"]:
        raise ValueError("cache exceeds input")
    if u["candidatesTokenCount"] + u.get("thoughtsTokenCount", 0) > (
        32768 if model == "gemini-4-carbon" else 16384
    ):
        raise ValueError("output bound exceeded")
    if schema is not None:
        jsonschema.validate(json.loads(raw), schema)
    return raw


def send(model, b, stage):
    os.environ["CARBON_STAGE"] = stage
    guard.install()
    response = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
        json=b,
        timeout=900,
    )
    response.raise_for_status()
    d = response.json()
    raw = parse(d, model, b["generationConfig"].get("responseJsonSchema"))
    return raw, d


def generate(model, system, text, image, mime="image/png", schema=None, stage=None):
    return send(model, body(model, system, text, [(image, mime)], schema), stage)
