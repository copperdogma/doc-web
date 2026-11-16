# ruff: noqa: E402
"""Offline final native consumer source-pixel audit, no inferred intermediate verdict."""

from pathlib import Path
import json
import hashlib
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / "docs/evals/evidence/094-hydrogen"
manifest = (
    ROOT
    / "output/runs/hydrogen094-runtime-candidate-p12-transport2/02_crop_illustrations_guided_v1/illustration_manifest.jsonl"
)
rows = [
    json.loads(x)
    for x in manifest.read_text().splitlines()
    if json.loads(x)["source_page"] == 12
]
source = Path(rows[0]["source_image"])
im = Image.open(source).convert("L")
w, h = im.size
gray = np.asarray(im)
covered = np.zeros((h, w), dtype=bool)
for r in rows:
    b = r["bbox"]
    covered[b["y0"] : b["y1"], b["x0"] : b["x1"]] = True
old = json.loads(
    (ROOT / "docs/evals/evidence/089-carbon/source-review-crops.json").read_text()
)["cases"]["Image011"]["arms"]["candidate"]["rois"]
rois = []
for r in old:
    b = [
        round(v * (w / 1545 if i % 2 == 0 else h / 2000))
        for i, v in enumerate(r["roi_half_open_xyxy"])
    ]
    x0, y0, x1, y1 = b
    mask = gray[y0:y1, x0:x1] < 100
    lost = mask & ~covered[y0:y1, x0:x1]
    rois.append(
        {
            "name": r["name"],
            "source_roi_half_open_xyxy": b,
            "source_dark_pixels": int(mask.sum()),
            "lost_final_source_dark_pixels": int(lost.sum()),
        }
    )
result = {
    "actual_driver": True,
    "original_recipe_geometry_and_layout_model": True,
    "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "dimensions": [w, h],
    "manifest": str(manifest.relative_to(ROOT)),
    "source_roi_basis": "Existing source-reviewed ROI fractions mapped to genuine highresolution source, native darkpixels counted in fixed regions",
    "final_boxes": [r["bbox"] for r in rows],
    "rois": rois,
    "source_material_loss": sum(r["lost_final_source_dark_pixels"] for r in rois),
    "printed_caption_contamination": True,
    "visual_review": "Final page-012-002 contains printed Hon.Gordon MacMurchy/Minister of Agriculture, right-edge signature/underline cut; source image and crop visually reviewed. This is final assisted artifact, not bare-box failure.",
    "decision": "Reject tested assisted detector path; retain current detector/manual holds. No full13 or further detector semantic calls.",
}
(E / "final-crop-source-review.json").write_text(json.dumps(result, indent=2) + "\n")
print(
    json.dumps(
        {
            "loss": result["source_material_loss"],
            "rois": rois,
            "decision": result["decision"],
        }
    )
)
