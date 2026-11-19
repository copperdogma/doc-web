"""Audit stamped actual-driver crop pixels against source-first ROIs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from benchmarks.scorers.image_crop_scorer import get_assert

E = ROOT / "docs/evals/evidence/099-neon"
PRIOR = ROOT / "docs/evals/evidence/094-hydrogen/final-crop-source-review.json"
# The interior text-only regions were frozen from the two captions visually
# delimited beneath (outside) the signatures on native Image011.
CAPTIONS_011 = {
    "printed_minister_caption": [2290, 5130, 3240, 5262],
    "printed_minister_in_charge_caption": [2310, 5660, 3240, 5870],
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    parser.add_argument("page", type=int)
    args = parser.parse_args()
    folder = ROOT / "output/runs" / args.run_id / "02_crop_illustrations_guided_v1"
    manifest = folder / "illustration_manifest.jsonl"
    rows = [json.loads(line) for line in manifest.read_text().splitlines()]
    rows = [row for row in rows if row["source_page"] == args.page]
    if not rows:
        raise ValueError("no final source crops")
    source = Path(rows[0]["source_image"])
    with Image.open(source) as image:
        w, h = image.size
        luma = np.asarray(image.convert("L"))
    dark = luma < 100
    covered = np.zeros(dark.shape, dtype=bool)
    boxes = []
    for r in rows:
        if r["source_image"] != str(source):
            raise ValueError("crop source identity drift")
        b = r["bbox"]
        x0, y0, x1, y1 = [b[k] for k in ("x0", "y0", "x1", "y1")]
        if not (0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h):
            raise ValueError("crop box outside native source")
        boxes.append([x0 / w, y0 / h, x1 / w, y1 / h])
        covered[y0:y1, x0:x1] = True
    sha = hashlib.sha256(source.read_bytes()).hexdigest()
    result = {
        "manifest": str(manifest.relative_to(ROOT)), "source_sha256": sha,
        "dimensions": [w, h], "boxes_normalized_xyxy": boxes,
        "final_crop_geometry": get_assert(
            json.dumps({"images": [{"bbox": b, "description": "final source crop"} for b in boxes]}),
            {"vars": {"golden_key": f"Image{args.page-1:03}"}},
        ),
        "geometry_limit": "Descriptive only: maintained no-hints benchmark grouping differs from assisted final crop count.",
    }
    if args.page == 12:
        prior = json.loads(PRIOR.read_text())
        if sha != prior["source_sha256"]:
            raise ValueError("frozen Image011 source bytes changed")

        def count(roi, cover):
            x0, y0, x1, y1 = roi
            region = np.s_[y0:y1, x0:x1]
            return int((dark[region] & cover[region]).sum())

        result["integral_roi_loss"] = {
            r["name"]: count(r["source_roi_half_open_xyxy"], ~covered)
            for r in prior["rois"]
        }
        result["nonintegral_caption_pixels_inside"] = {
            name: count(rect, covered) for name, rect in CAPTIONS_011.items()
        }
    target = E / (args.run_id + "-pixels.json")
    target.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
