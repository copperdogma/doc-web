"""Reproducible native and adapter qualification for Grok 4.7's crop contract."""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "providers"))
import xai_grok_responses as provider  # noqa: E402


def synthetic_prompt() -> str:
    image = Image.new("RGB", (128, 128), "white")
    ImageDraw.Draw(image).rectangle((32, 32, 95, 95), fill="black")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    uri = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
    return json.dumps(
        [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Identify the black square as one image. Return its bbox "
                            "as 0-1000 integers in the crop_regions JSON schema. "
                            "No other regions."
                        ),
                    },
                    {"type": "image_url", "image_url": {"url": uri}},
                ],
            }
        ]
    )


def native(prompt: str) -> dict:
    settings = provider._request_settings()
    body = provider._build_body(prompt)
    key = os.environ[os.environ.get("XAI_API_KEY_ENV", "XAI_API_KEY")]
    response = provider.httpx.post(
        "https://api.x.ai/v1/responses",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json=body,
        timeout=90,
    )
    raw_http = provider._retain_raw_http_response(response)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError("xAI Responses API response JSON must be an object")
    retained = {**raw_http, **provider._retain_raw_envelope(data)}
    output = provider._extract_output_text(data)
    if data.get("status") != "completed" or data.get("incomplete_details") is not None:
        raise AssertionError(f"nonterminal xAI status: {data.get('status')!r}")
    if data.get("model") != settings["expected_served_model"]:
        raise AssertionError(
            f"served model mismatch: {data.get('model')!r} != {settings['expected_served_model']!r}"
        )
    if provider._provider_error(data) is not None or not output:
        raise AssertionError("xAI returned an error or no output text")
    contract_error = provider._contract_error(output, settings["output_contract"])
    if contract_error is not None:
        raise AssertionError(f"strict schema failure: {contract_error}")
    usage_error = provider._usage_evidence_error(data)
    if usage_error is not None:
        raise AssertionError(f"usage evidence failure: {usage_error}")
    return {
        "requested_model": settings["model"],
        "served_model": data["model"],
        "status": data["status"],
        "output_contract": settings["output_contract"],
        "output_sha256": provider.hashlib.sha256(output.encode("utf-8")).hexdigest(),
        "usage": provider._token_usage(data),
        "cost": provider._reported_cost(data),
        "raw_envelope": retained,
    }


parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=["native", "parity"])
args = parser.parse_args()
prompt = synthetic_prompt()
if args.mode == "native":
    result = native(prompt)
else:
    result = provider.call_api(prompt, {}, {})
    if "error" in result:
        raise AssertionError(result["error"])
    result = {
        "requested_model": result["metadata"]["requested_model"],
        "served_model": result["metadata"]["served_model"],
        "status": result["metadata"]["response_status"],
        "output_contract": result["metadata"]["requested_output_contract"],
        "output_sha256": provider.hashlib.sha256(result["output"].encode("utf-8")).hexdigest(),
        "usage": result.get("tokenUsage"),
        "cost": result.get("cost"),
        "raw_envelope": {
            key: value
            for key, value in result["metadata"].items()
            if key.startswith("raw_envelope_")
        },
    }

print(json.dumps(result, sort_keys=True))
