"""Frozen, metered Google detector qualification; no runtime default mutation."""

import hashlib
import json
import os
import sys
from pathlib import Path

import httpx
from jsonschema import validate

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mistral4_guard as guard
from openrouter_vision_chat import CROP_INTEGER_SCHEMA, _contract_error


CANDIDATE = "gemini-4-argon"
CONTROL = "gemini-3-flash-preview"


def body(prompt, model=CANDIDATE):
    if model not in {CANDIDATE, CONTROL}:
        raise ValueError("Unapproved detector model")
    messages = json.loads(prompt)
    if (
        not isinstance(messages, list)
        or len(messages) != 1
        or messages[0].get("role") != "user"
    ):
        raise ValueError("Expected one maintained user message")
    message = messages[0]
    parts = message.get("parts")
    if parts is None:
        parts = []
        for item in message["content"]:
            if item["type"] == "text":
                parts.append({"text": item["text"]})
            elif item["type"] == "image_url":
                header, payload = item["image_url"]["url"].split(",", 1)
                if not header.startswith("data:image/") or not header.endswith(
                    ";base64"
                ):
                    raise ValueError("Expected inline image")
                parts.append(
                    {
                        "inlineData": {
                            "mimeType": header[5:].split(";")[0],
                            "data": payload,
                        }
                    }
                )
            else:
                raise ValueError("Unsupported detector content")
    if model == CANDIDATE:
        config = {
            "maxOutputTokens": 32768,
            "thinkingConfig": {"thinkingLevel": "medium"},
            "responseMimeType": "application/json",
            "responseJsonSchema": CROP_INTEGER_SCHEMA,
        }
    else:
        config = {"temperature": 0, "maxOutputTokens": 16384}
    return {"contents": [{"role": "user", "parts": parts}], "generationConfig": config}


def parse_response(data, model):
    candidates = data.get("candidates")
    if (
        data.get("modelVersion") != model
        or not isinstance(data.get("responseId"), str)
        or not data["responseId"]
    ):
        raise ValueError("Google identity contract failed")
    if (
        not isinstance(candidates, list)
        or len(candidates) != 1
        or candidates[0].get("finishReason") != "STOP"
    ):
        raise ValueError("Google terminal contract failed")
    parts = candidates[0]["content"]["parts"]
    output = "\n".join(
        part["text"] for part in parts if "text" in part and not part.get("thought")
    )
    if not output.strip():
        raise ValueError("Google visible output missing")
    usage = data["usageMetadata"]
    inp, visible, total = (
        usage[key]
        for key in ["promptTokenCount", "candidatesTokenCount", "totalTokenCount"]
    )
    thoughts, cached = (
        usage.get("thoughtsTokenCount", 0),
        usage.get("cachedContentTokenCount", 0),
    )
    if any(
        type(value) is not int or value < 0
        for value in (inp, visible, total, thoughts, cached)
    ):
        raise ValueError("Google usage contract failed")
    generated = visible + thoughts
    if total != inp + generated or cached > inp or not visible:
        raise ValueError("Google usage contract failed")
    if generated > (32768 if model == CANDIDATE else 16384):
        raise ValueError("Google output allowance exceeded")
    if model == CANDIDATE:
        validate(json.loads(output), CROP_INTEGER_SCHEMA)
        if _contract_error(output, "crop_regions_integer"):
            raise ValueError("Google crop geometry contract failed")
    rates = (2, 0.1, 10) if model == CANDIDATE else (0.5, 0.05, 3)
    return {
        "output": output,
        "tokenUsage": {"prompt": inp, "completion": generated, "total": total},
        "cost": ((inp - cached) * rates[0] + cached * rates[1] + generated * rates[2])
        / 1e6,
        "metadata": {
            "served_model": model,
            "response_id": data["responseId"],
            "usage": usage,
            "strict_schema": model == CANDIDATE,
        },
    }


def call_api(prompt, options, context):
    model = options.get("config", {}).get("model", CANDIDATE)
    request_body = body(prompt, model)
    guard.configure_campaign(os.environ["DOC_WEB_CROP_CAMPAIGN_PROFILE"])
    os.environ["MISTRAL_CASE"] = str(
        context.get("vars", {}).get("golden_key", "native")
    )
    guard.install()
    response = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
        json=request_body,
        timeout=180,
    )
    if response.status_code != 200:
        return {
            "error": f"Google catalog candidate request HTTP {response.status_code}"
        }
    try:
        result = parse_response(response.json(), model)
    except Exception:
        return {
            "error": "Google identity, terminal, schema or usage contract failed; inspect retained receipt"
        }
    result["metadata"]["request_sha256"] = hashlib.sha256(
        json.dumps(request_body, sort_keys=True).encode()
    ).hexdigest()
    return result
