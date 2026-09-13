"""Reproducible synthetic native and owner-adapter qualification for Attempt036."""

import argparse
from datetime import datetime, timezone
import base64
import io
import json
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "providers"))
import deepseek_v41_budgeted as campaign  # noqa: E402
from openrouter_vision_chat import _body, _contract_error, _usage  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=["native", "parity"])
parser.add_argument("--run", required=True)
args = parser.parse_args()
if datetime.now(timezone.utc) >= datetime.fromisoformat("2026-09-13T23:54:06+00:00"):
    raise RuntimeError("Authorized retry deadline elapsed")
if not args.run.startswith("deepseek-v41-") or Path(args.run).name != args.run:
    raise ValueError("Invalid campaign run identity")
campaign.RESULTS = ROOT / "results" / args.run
image = Image.new("RGB", (128, 128), "white")
ImageDraw.Draw(image).rectangle((32, 32, 95, 95), fill="black")
buffer = io.BytesIO()
image.save(buffer, format="PNG")
uri = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
prompt = json.dumps(
    [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Identify the black square as one image. Return its normalized bbox in the crop_regions JSON schema. No other regions.",
                },
                {"type": "image_url", "image_url": {"url": uri}},
            ],
        }
    ]
)
config = yaml.safe_load((ROOT / "tasks/image-crop-deepseek-v41.yaml").read_text())[
    "providers"
][0]["config"]
config["max_tokens"] = 1024
body = _body(prompt, {"config": config})
if args.mode == "native":
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
    assert (
        data["model"] == config["expected_served_model"]
        and data["provider"] == "DeepInfra"
    )
    assert choice["finish_reason"] == "stop" and not data.get("error")
    assert _contract_error(output, "crop_regions") is None
    result = {
        "output": output,
        "cost": data["usage"]["cost"],
        "model": data["model"],
        "provider": data["provider"],
    }
else:
    result = campaign.call_api(prompt, {"config": config}, {})
(campaign.RESULTS / f"{args.mode}-probe.json").write_text(
    json.dumps(result, indent=2) + "\n"
)
print(json.dumps(result))
assert "error" not in result
