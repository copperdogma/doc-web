#!/usr/bin/env python3
"""Run a bounded first-party GPT-6 Astra strict-contract qualification probe."""

from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path

import httpx

MODEL = "gpt-6-astra"
FORMAT = {
    "type": "json_schema",
    "name": "crop_regions",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "images": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "bbox": {
                            "type": "array",
                            "items": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
                            "minItems": 4,
                            "maxItems": 4,
                        },
                    },
                    "required": ["description", "bbox"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["images"],
        "additionalProperties": False,
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("text", "image"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--effort", default="low")
    parser.add_argument("--max-output-tokens", type=int, default=1024)
    return parser.parse_args()


def extract_text(data: dict) -> str:
    chunks = []
    for item in data.get("output", []):
        if isinstance(item, dict) and item.get("type") == "message":
            for content in item.get("content", []):
                if isinstance(content, dict) and content.get("type") == "output_text":
                    chunks.append(content.get("text", ""))
    return "\n".join(chunks).strip()


def main() -> int:
    args = parse_args()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is not configured")

    content = [
        {
            "type": "input_text",
            "text": "Return an empty images array because no document illustration is present.",
        }
    ]
    if args.mode == "image":
        blank_png = base64.b64encode(
            base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
            )
        ).decode("ascii")
        content.append(
            {
                "type": "input_image",
                "image_url": f"data:image/png;base64,{blank_png}",
                "detail": "high",
            }
        )

    body = {
        "model": MODEL,
        "input": [{"role": "user", "content": content}],
        "reasoning": {"effort": args.effort},
        "max_output_tokens": args.max_output_tokens,
        "store": False,
        "text": {"format": FORMAT},
    }
    response = httpx.post(
        "https://api.openai.com/v1/responses",
        headers={"Authorization": f"Bearer {api_key}"},
        json=body,
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    args.output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    args.output.write_text(json.dumps(data, indent=2) + "\n")
    args.output.chmod(0o600)

    usage = data.get("usage") or {}
    input_tokens = int(usage.get("input_tokens") or 0)
    cached_tokens = int(
        (usage.get("input_tokens_details") or {}).get("cached_tokens") or 0
    )
    output_tokens = int(usage.get("output_tokens") or 0)
    cost = (
        (input_tokens - cached_tokens) * 10 + cached_tokens * 1 + output_tokens * 50
    ) / 1_000_000
    output_text = extract_text(data)
    try:
        contract_valid = json.loads(output_text) == {"images": []}
    except (json.JSONDecodeError, TypeError, ValueError):
        contract_valid = False
    print(
        json.dumps(
            {
                "mode": args.mode,
                "status": data.get("status"),
                "served_model": data.get("model"),
                "incomplete_details": data.get("incomplete_details"),
                "input_tokens": input_tokens,
                "cached_input_tokens": cached_tokens,
                "output_tokens": output_tokens,
                "estimated_cost_usd": round(cost, 8),
                "contract_valid": contract_valid,
                "output": output_text,
            }
        )
    )
    return (
        0
        if (
            data.get("status") == "completed"
            and data.get("model") == MODEL
            and data.get("incomplete_details") is None
            and contract_valid
        )
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
