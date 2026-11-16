# ruff: noqa: E402
"""Frozen source ROI exact dark-pixel preservation; tolerant scorer separate."""

import base64
import hashlib
import io
import json
import sys
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from benchmarks.scorers.image_crop_scorer import _parse_json

E = ROOT / "docs/evals/evidence/094-hydrogen"


def run(key):
    raw = base64.b64decode(
        (ROOT / f"benchmarks/input/source-pages-b64/{key}.b64.txt")
        .read_text()
        .strip()
        .split(",")[-1]
    )
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    w, h = im.size
    gray = np.array(im.convert("L"))
    dark = gray < 100
    old = json.loads(
        (ROOT / "docs/evals/evidence/089-carbon/source-review-crops.json").read_text()
    )
    rois = old["cases"][key]["arms"]["candidate"]["rois"]
    report = {
        "source_decoded_sha256": hashlib.sha256(raw).hexdigest(),
        "dimensions": [w, h],
        "frozen_rois_from": "089-carbon/source-review-crops.json",
        "uses_golden_axis_oracle": False,
        "runtime_coordinate_parity": "fixed prompt-declared normalized XYXY; downstream cleanup not inferred",
        "arms": {},
    }
    for arm in ["candidate", "control"]:
        result = json.loads((E / f"crop-screen-{key}-{arm}.json").read_text())
        parsed = _parse_json(result["raw"])
        boxes = [x["bbox"] for x in parsed["images"]]
        norm = boxes
        if any(
            len(b) != 4
            or not all(0 <= v <= 1 for v in b)
            or not (b[0] < b[2] and b[1] < b[3])
            for b in norm
        ):
            raise ValueError(
                "native fixed XYXY normalized contract failed; no golden axis rescue"
            )
        by_policy = {}
        for policy, converter in [("int", int), ("round", round)]:
            pixels = [
                [converter(x * (w if j % 2 == 0 else h)) for j, x in enumerate(b)]
                for b in norm
            ]
            covered = np.zeros((h, w), dtype=bool)
            for x0, y0, x1, y1 in pixels:
                covered[max(y0, 0) : min(y1, h), max(x0, 0) : min(x1, w)] = True
            losses = []
            for roi in rois:
                x0, y0, x1, y1 = roi["roi_half_open_xyxy"]
                ys, xs = np.where(dark[y0:y1, x0:x1] & ~covered[y0:y1, x0:x1])
                losses.append(
                    {
                        "name": roi["name"],
                        "roi_half_open_xyxy": [x0, y0, x1, y1],
                        "excluded_dark_pixels": len(xs),
                        "excluded_extent_inclusive_xyxy": [
                            int(xs.min() + x0),
                            int(ys.min() + y0),
                            int(xs.max() + x0),
                            int(ys.max() + y0),
                        ]
                        if len(xs)
                        else None,
                    }
                )
            by_policy[policy] = {
                "pixel_boxes": pixels,
                "rois": losses,
                "total_excluded": sum(x["excluded_dark_pixels"] for x in losses),
                "strict_preservation_pass": all(
                    x["excluded_dark_pixels"] == 0 for x in losses
                ),
            }
            if policy == "int":
                for n, b in enumerate(pixels):
                    im.crop(b).save(E / f"{key}-{arm}-source-crop-{n}.png")
        report["arms"][arm] = {
            "raw_boxes": boxes,
            "normalized_boxes": norm,
            "maintained_scorer": result["score"],
            "policies": by_policy,
        }
    (E / f"source-pixels-{key}.json").write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                a: {
                    "loss": v["policies"]["int"]["total_excluded"],
                    "pass": v["policies"]["int"]["strict_preservation_pass"],
                }
                for a, v in report["arms"].items()
            }
        )
    )


if __name__ == "__main__":
    run(sys.argv[1])
