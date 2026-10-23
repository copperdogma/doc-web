"""Fresh native and owner-adapter qualification for the 2026-10-14 run."""

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
import deepseek_v41_fresh_20261014 as campaign  # noqa: E402
from openrouter_vision_chat import _body, _contract_error, _usage  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=["native", "parity"])
args = parser.parse_args()

image = Image.new("RGB", (128, 128), "white")
ImageDraw.Draw(image).rectangle((32, 32, 95, 95), fill="black")
buffer = io.BytesIO()
image.save(buffer, format="PNG")
uri = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
prompt = json.dumps([{
    "role": "user",
    "content": [
        {"type": "text", "text": "Identify the black square as one image. Return its normalized bbox in the crop_regions JSON schema. No other regions."},
        {"type": "image_url", "image_url": {"url": uri}},
    ],
}])
config = yaml.safe_load((ROOT / "tasks/image-crop-deepseek-v41-fresh-20261014.yaml").read_text())["providers"][0]["config"]
body = _body(prompt, {"config": config})
(campaign.RESULTS / f"{args.mode}-request-sha256.txt").write_text(
    __import__("hashlib").sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest() + "\n"
)

if args.mode == "native":
    response = campaign.recorded_post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
            "Content-Type": "application/json",
        },
        json=body,
        timeout=240,
    )
    response.raise_for_status()
    data = response.json()
    choice = data["choices"][0]
    output = choice["message"]["content"]
    _usage(data)
    assert data.get("model") == config["expected_served_model"]
    assert data.get("provider") == config["expected_served_provider"]
    assert choice.get("finish_reason") == "stop" and not data.get("error")
    assert _contract_error(output, "crop_regions") is None
    result = {"output": output, "model": data["model"], "provider": data["provider"], "cost_usd": data["usage"]["cost"]}
else:
    result = campaign.call_api(prompt, {"config": config}, {})

(campaign.RESULTS / f"{args.mode}-probe.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: v for k, v in result.items() if k != "output"}))
if "error" in result:
    raise SystemExit(1)
