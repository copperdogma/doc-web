# ruff: noqa: E402
"""Freeze exact selected matrix before inference. countTokens has no generation."""

import base64
import hashlib
import io
import json
import os
import sys
from pathlib import Path
import httpx
import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "benchmarks/scripts"))
import carbon_reading as reading
import carbon_native as native
import scout096_safety as safety
from modules.common.table_source_review import POLICY, astra_request
from doc_web.literal_fidelity import SourcePageReview
from modules.extract.ocr_ai_gpt51_v1.main import build_system_prompt

E = ROOT / "docs/evals/evidence/089-carbon"
KEYS = [
    "page-001-000",
    "page-004-000",
    "page-009-000",
    "page-012-000",
    "page-122-001",
    "page-012-001",
]


def safety_body(key):
    b = safety.body(key, "control")
    parts = b["input"][0]["content"]
    text = parts[0]["text"]
    images = []
    for p in parts[1:]:
        head, data = p["image_url"].split(",", 1)
        images.append((base64.b64decode(data), head.split(":")[1].split(";")[0]))
    return native.body(
        "gemini-4-carbon", "", text, images, b["text"]["format"]["schema"]
    )


def main():
    E.mkdir(parents=True, exist_ok=True)
    native.guard.RESULTS.mkdir(parents=True, exist_ok=True)
    ledger = native.guard.RESULTS / "ledger.json"
    if not ledger.exists():
        native.guard.save(
            ledger, {"cap_usd": 10, "spent_usd": 0, "calls": [], "closed": False}
        )
    matrix = []
    for key in KEYS:
        control = safety.body(key, "control")
        control.update(store=False, service_tier="default")
        matrix += [
            (f"safety-{key}-candidate", "gemini-4-carbon", safety_body(key)),
            (f"safety-{key}-control", "gpt-5.5", control),
        ]
    for case in ["image-positive", "ambiguity-negative", "native-positive"]:
        p = ROOT / f"testdata/literal-table-fidelity/confirmation-v2/{case}/page.png"
        im = Image.open(p)
        text = f"Source image dimensions: {im.width} x {im.height} pixels. Read source tables; return JSON only."
        matrix += [
            (
                f"table-{case}-candidate",
                "gemini-4-carbon",
                native.body(
                    "gemini-4-carbon",
                    POLICY,
                    text,
                    [(p.read_bytes(), "image/png")],
                    SourcePageReview.model_json_schema(),
                ),
            ),
            (f"table-{case}-control", "gpt-6-astra", astra_request(p)),
        ]
        initial = ROOT / f"docs/evals/evidence/087-fable52/initial-{case}.json"
        reading.save(E / f"initial-{case}.json", json.loads(initial.read_text()))
    for key in ["Image011", "Image001"]:
        parts = reading.render_crop(key)[0]["parts"]
        im = parts[1]["inlineData"]
        images = [(base64.b64decode(im["data"]), im["mimeType"])]
        for model, label in [
            ("gemini-4-carbon", "candidate"),
            ("gemini-3-flash-preview", "control"),
        ]:
            matrix.append(
                (
                    f"crop-screen-{key}-{label}",
                    model,
                    native.body(
                        model,
                        "",
                        parts[0]["text"],
                        images,
                        reading.CROP_SCHEMA if label == "candidate" else None,
                    ),
                )
            )
    recipe = yaml.safe_load(
        (ROOT / "configs/recipes/gpt61-ocr-gemini-3.7-flash-barney.yaml").read_text()
    )
    params = recipe["stages"][1]["params"]
    system = build_system_prompt(params["ocr_hints"], False)
    text = 'Return HTML only. FIRST line MUST be: <meta name="ocr-metadata" data-ocr-quality="0.0-1.0" data-ocr-integrity="0.0-1.0" data-continuation-risk="0.0-1.0">'
    images = list((ROOT / "testdata/handwritten-notes-barney-real-images").glob("*"))
    assert len(images) == 1
    image = images[0].read_bytes()
    mime = Image.MIME[Image.open(io.BytesIO(image)).format]
    for model, label in [
        ("gemini-4-carbon", "candidate"),
        ("gemini-3.8-flash", "control"),
    ]:
        matrix.append(
            (
                f"ocr-barney-{label}",
                model,
                native.body(model, system, text, [(image, mime)]),
            )
        )
    frozen = []
    for stage, model, b in matrix:
        path = E / "rendered" / f"{stage}.json"
        reading.save(path, b)
        row = {
            "stage": stage,
            "model": model,
            "request_path": str(path.relative_to(ROOT)),
            "request_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "independent_session": True,
            "input_bound": 46000 if stage.startswith("safety") else 26000,
        }
        if model.startswith("gemini"):
            count_body = {"contents": b["contents"]}
            if "systemInstruction" in b:
                count_body = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": b["systemInstruction"]["parts"]
                            + b["contents"][0]["parts"],
                        }
                    ]
                }
            row["count_scope"] = (
                "contents plus system text serialized as user parts for counting only; excludes schema; +512 schema/role margin"
            )
            saved = E / "counts" / f"{stage}.json"
            response = (
                httpx.Response(
                    200,
                    json=json.loads(saved.read_text()),
                    request=httpx.Request("POST", "https://count-only-local.invalid"),
                )
                if saved.exists() and "totalTokens" in json.loads(saved.read_text())
                else httpx.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:countTokens",
                    headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
                    json=count_body,
                    timeout=60,
                )
            )
            reading.save(
                E / "counts" / f"{stage}.json",
                {"status_code": response.status_code, **response.json()},
            )
            response.raise_for_status()
            row["native_count"] = response.json()["totalTokens"]
            assert row["native_count"] + 512 <= row["input_bound"]
        frozen.append(row)
    files = [
        "benchmarks/scripts/carbon_native.py",
        "benchmarks/scripts/carbon_reading.py",
        "benchmarks/scripts/carbon_preflight.py",
        "benchmarks/providers/carbon_guard.py",
        "benchmarks/prompts/validate-page-level-crop.js",
        "benchmarks/prompts/crop-conservative-count.js",
        "benchmarks/golden/crop-page-level-safety-repair-048-source-adjudicated.json",
        "benchmarks/golden/image-crops.json",
        "modules/common/table_source_review.py",
        "modules/common/literal_table_review.py",
        "benchmarks/scorers/image_crop_scorer.py",
    ]
    reading.save(
        E / "preflight.json",
        {
            "authority": "Scout109 selected item3 USD10 inclusive; allsix YES",
            "base": "1c3f3e31158ec753e057e79839f438d021500214",
            "candidate": "native gemini-4-carbon HIGH32768 GenerateContent",
            "safety": KEYS,
            "matrix": frozen,
            "calls": 24,
            "candidate_cases": 12,
            "control_cases": 12,
            "reservation": {
                "candidate": 4.79616,
                "control_pool": 3,
                "qualification_recovery": 2.20384,
            },
            "cache": "no subject cache; no explicit caching; actual implicit hits recorded",
            "concurrency": 1,
            "judge": "none paid; source review + maintained deterministic assertions",
            "effort": "high only; no sweep or semantic repair",
            "qualification": "first real request per distinct schema doubles as native qualifier; raw native contract and lossless rendered input parity checked before scoring",
            "source_hashes": {
                p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in files
            },
        },
    )
    print(
        json.dumps(
            {
                "candidate": 12,
                "control": 12,
                "cap": 10,
                "counts": [(x["stage"], x.get("native_count")) for x in frozen],
            }
        )
    )


if __name__ == "__main__":
    main()
