"""Strict text, native image, and owner-adapter probes for Attempt 037."""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "providers"))
import qwen38_flash_budgeted as campaign  # noqa: E402
from openrouter_vision_chat import _body, _contract_error, _usage  # noqa: E402


def synthetic_prompt(integer_coordinates: bool) -> str:
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
                            + (
                                "as 0-1000 integers in the crop_regions_integer JSON schema. "
                                if integer_coordinates
                                else "normalized from 0 to 1 in the crop_regions JSON schema. "
                            )
                            + "No other regions."
                        ),
                    },
                    {"type": "image_url", "image_url": {"url": uri}},
                ],
            }
        ]
    )


def request_config(provider_name: str, integer_coordinates: bool) -> dict:
    config = yaml.safe_load((ROOT / "tasks/image-crop-qwen38-flash.yaml").read_text())
    providers = {row["label"]: row["config"] for row in config["providers"]}
    label = f"Qwen3.8 Flash {provider_name} low"
    if integer_coordinates:
        label += " strict integer crop schema"
    selected = dict(providers[label])
    selected["max_tokens"] = 1024
    return selected


def native(prompt: str, config: dict) -> dict:
    body = _body(prompt, {"config": config})
    response = campaign.recorded_post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
            "Content-Type": "application/json",
        },
        json=body,
        timeout=90,
    )
    response.raise_for_status()
    data = response.json()
    choice = data["choices"][0]
    output = choice["message"]["content"]
    _usage(data)
    assert data["model"] == config["expected_served_model"]
    assert data["provider"] == config["expected_served_provider"]
    assert choice["finish_reason"] == "stop" and not data.get("error")
    assert _contract_error(output, config["output_contract"]) is None
    return {
        "output": output,
        "cost": data["usage"]["cost"],
        "model": data["model"],
        "provider": data["provider"],
    }


parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=["text", "native", "parity"])
parser.add_argument("--provider", choices=["Alibaba", "Makora"], default="Alibaba")
parser.add_argument("--integer", action="store_true")
args = parser.parse_args()
config = request_config(args.provider, args.integer)
if args.mode == "text":
    prompt = "Return an empty images array in the required crop_regions schema."
else:
    prompt = synthetic_prompt(args.integer)
result = (
    native(prompt, config)
    if args.mode in {"text", "native"}
    else campaign.call_api(prompt, {"config": config}, {})
)
coordinate_label = "integer" if args.integer else "normalized"
output_path = ROOT / "results/qwen38-flash-20260913" / (
    f"{args.provider.lower()}-{coordinate_label}-{args.mode}-probe.json"
)
output_path.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
assert "error" not in result
