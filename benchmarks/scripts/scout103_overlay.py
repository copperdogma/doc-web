"""Offline source overlay only; never alters subject coordinates."""

import base64
import io
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from benchmarks.scorers.image_crop_scorer import _parse_json, _auto_normalize_boxes  # noqa: E402

key = sys.argv[1]
p = ROOT / "docs/evals/evidence/085-scout103"
s = (
    (ROOT / f"benchmarks/input/source-pages-b64/{key}.b64.txt")
    .read_text()
    .strip()
    .split(",")[-1]
)
im = Image.open(io.BytesIO(base64.b64decode(s))).convert("RGB")
w, h = im.size
for arm, color in [("candidate", "red"), ("control", "blue")]:
    d = _parse_json(
        json.loads((p / f"crop-screen-{key}-{arm}.json").read_text())["raw"]
    )
    out = im.copy()
    draw = ImageDraw.Draw(out)
    gold = json.loads((ROOT / "benchmarks/golden/image-crops.json").read_text())
    if isinstance(gold, dict):
        gold = gold.get(key, gold.get("images", {}).get(key, {}))
    boxes = [o["bbox"] for o in d["images"]]
    gb = [o["bbox_normalized"] for o in gold["crops"]]
    normalized = _auto_normalize_boxes(boxes, gb)
    (p / f"{key}-{arm}-normalization.json").write_text(
        json.dumps(
            {
                "raw_boxes": boxes,
                "scorer_normalized_boxes": normalized,
                "uses_golden_axis_oracle": True,
                "runtime_parity": False,
                "source_image_dimensions": [w, h],
            },
            indent=2,
        )
        + "\n"
    )
    for i, coords in enumerate(normalized):
        box = [
            round(x * w) if j % 2 == 0 else round(x * h) for j, x in enumerate(coords)
        ]
        draw.rectangle(box, outline=color, width=3)
        draw.text((box[0], max(0, box[1] - 15)), str(i), fill=color)
    out.save(p / f"{key}-{arm}-overlay.jpg")
