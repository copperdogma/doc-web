"""Metered native Gemini projection of maintained Promptfoo Google call shape."""

import json
import os
import sys
from pathlib import Path
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mistral4_guard as guard


def call_api(prompt, options, context):
    os.environ["MISTRAL_CASE"] = str(
        context.get("vars", {}).get("golden_key", "native")
    )
    guard.install()
    contents = json.loads(prompt)
    for message in contents:
        if "content" in message:
            parts = []
            for item in message.pop("content"):
                if item["type"] == "text":
                    parts.append({"text": item["text"]})
                else:
                    uri = item["image_url"]["url"]
                    header, data = uri.split(",", 1)
                    parts.append(
                        {
                            "inlineData": {
                                "mimeType": header.split(":")[1].split(";")[0],
                                "data": data,
                            }
                        }
                    )
            message["parts"] = parts
    model = "gemini-3-flash-preview"
    body = {
        "contents": contents,
        "generationConfig": {"temperature": 0, "maxOutputTokens": 16384},
    }
    response = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
        json=body,
        timeout=180,
    )
    response.raise_for_status()
    data = response.json()
    candidates = data.get("candidates", [])
    if (
        data.get("modelVersion") != model
        or len(candidates) != 1
        or candidates[0].get("finishReason") != "STOP"
    ):
        return {"error": "Gemini identity or terminal contract failed"}
    usage = data["usageMetadata"]
    output = "\n".join(
        p["text"]
        for p in candidates[0]["content"]["parts"]
        if "text" in p and not p.get("thought")
    )
    inp = usage["promptTokenCount"]
    out = usage.get("candidatesTokenCount", 0) + usage.get("thoughtsTokenCount", 0)
    return {
        "output": output,
        "tokenUsage": {"prompt": inp, "completion": out, "total": inp + out},
        "cost": (inp * 0.5 + out * 3) / 1e6,
        "metadata": {
            "served_model": data["modelVersion"],
            "response_id": data.get("responseId"),
        },
    }
