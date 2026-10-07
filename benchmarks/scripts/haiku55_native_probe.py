import base64
import io
import json
import os
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "benchmarks/providers"))
import haiku55_candidate as p  # noqa: E402
import haiku55_guard as g  # noqa: E402

if any(
    (g.RESULTS / f"native-{arm}.json").exists() for arm in ["medium", "low", "high"]
):
    raise RuntimeError(
        "Refuse to overwrite prior native evidence; use a separately authorized run identity"
    )

b = io.BytesIO()
Image.new("RGB", (32, 32), "black").save(b, format="PNG")
uri = "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
for arm, thinking in [
    ("medium", "adaptive"),
    ("low", "disabled"),
    ("high", "adaptive"),
]:
    os.environ["HAIKU55_STAGE"] = "native-" + arm
    os.environ["HAIKU55_CASE"] = "black-square"
    prompt = json.dumps(
        [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Find the single black square as one illustration, bbox integers 0-1000.",
                    },
                    {"type": "image_url", "image_url": {"url": uri}},
                ],
            }
        ]
    )
    r = p.call_api(
        prompt,
        {
            "config": {
                "model": "claude-haiku-5-5",
                "effort": arm,
                "thinking": thinking,
                "output_contract": "crop_regions_integer",
                "max_tokens": 4096,
            }
        },
        {},
    )
    (g.RESULTS / ("native-" + arm + ".json")).write_text(json.dumps(r, indent=2))
    print(arm, json.dumps(r), flush=True)
    if r.get("error"):
        break
