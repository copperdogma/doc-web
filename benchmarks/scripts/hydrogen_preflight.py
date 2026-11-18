# ruff: noqa: E402
import sys
import json
import base64
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from benchmarks.scripts import (
    hydrogen_native as native,
    hydrogen_reading as reading,
    hydrogen_caller as caller,
)
from modules.common import crop_safety
from benchmarks.providers.historical_literal_readers.table_source_review import POLICY, astra_request
from doc_web.literal_fidelity import SourcePageReview
from PIL import Image

E = native.guard.E
if (E / "preflight.json").exists():
    raise RuntimeError("Immutable run already exists; use a new authorized identity")
matrix = []


def add(stage, model, body):
    p = E / "rendered" / f"{stage}.json"
    reading.save(p, body)
    matrix.append(
        {
            "stage": stage,
            "model": model,
            "request_path": str(p.relative_to(ROOT)),
            "request_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "independent_session": True,
        }
    )


for arm in ["candidate", "control"]:
    b = crop_safety.build_request(
        ROOT / "tests/fixtures/crop_review_offline/approved/S3-source.png",
        ROOT / "tests/fixtures/crop_review_offline/approved/images/S3.png",
        live=True,
    )
    if arm == "candidate":
        b = caller.google_body(b)
    add(
        "caller-S3-" + arm,
        "gemini-4-hydrogen" if arm == "candidate" else "gpt-6.1-sol",
        b,
    )
for case in ["image-positive", "ambiguity-negative", "native-positive"]:
    p = ROOT / f"testdata/literal-table-fidelity/confirmation-v2/{case}/page.png"
    im = Image.open(p)
    add(
        "table-" + case + "-candidate",
        "gemini-4-hydrogen",
        native.body(
            "gemini-4-hydrogen",
            POLICY,
            f"Source image dimensions: {im.width} x {im.height} pixels. Read source tables; return JSON only.",
            [(p.read_bytes(), "image/png")],
            SourcePageReview.model_json_schema(),
        ),
    )
    add("table-" + case + "-control", "gpt-6-astra", astra_request(p))
    reading.save(
        E / f"initial-{case}.json",
        json.loads(
            (ROOT / f"docs/evals/evidence/087-fable52/initial-{case}.json").read_text()
        ),
    )
for key in ["Image011", "Image001"]:
    parts = reading.render_crop(key)[0]["parts"]
    im = parts[1]["inlineData"]
    images = [(base64.b64decode(im["data"]), im["mimeType"])]
    for model, arm in [
        ("gemini-4-hydrogen", "candidate"),
        ("gemini-3-flash-preview", "control"),
    ]:
        add(
            f"crop-screen-{key}-{arm}",
            model,
            native.body(
                model,
                "",
                parts[0]["text"],
                images,
                reading.CROP_SCHEMA if arm == "candidate" else None,
            ),
        )
# Original driver input prompt and image from maintained recipe, no resolution loss.
import yaml
from modules.extract.ocr_ai_gpt51_v1.main import build_system_prompt

params = yaml.safe_load(
    (ROOT / "configs/recipes/gpt61-ocr-gemini-3.7-flash-barney.yaml").read_text()
)["stages"][1]["params"]
system = build_system_prompt(params["ocr_hints"], False)
text = 'Return HTML only. FIRST line MUST be: <meta name="ocr-metadata" data-ocr-quality="0.0-1.0" data-ocr-integrity="0.0-1.0" data-continuation-risk="0.0-1.0">'
p = next((ROOT / "testdata/handwritten-notes-barney-real-images").glob("*"))
im = Image.open(p)
mime = Image.MIME[im.format]
for model, arm in [("gemini-4-hydrogen", "candidate"), ("gemini-3.8-flash", "control")]:
    add(
        "ocr-barney-" + arm,
        model,
        native.body(model, system, text, [(p.read_bytes(), mime)]),
    )
reading.save(
    E / "preflight.json",
    {
        "authority": "Scout111 allsix YES, DocWeb18USD, max40candidates",
        "matrix": matrix,
        "concurrency": 1,
        "judge": "none paid",
        "source_policy": "public Onward/public LOC/authored synthetic only",
        "conditional": "S3 first; failure stops safety only; independent other tasks continue; promising screen triggers bounded independent native consumer confirmation",
        "candidate": "gemini-4-hydrogen HIGH32768",
        "cache": "no subject outputs; implicit native usage recorded",
        "base": "c65346e4be7d757fa1130cb23fd8efc2fa41a191",
    },
)
print("Frozen", len(matrix), "initial rows; no inference")
