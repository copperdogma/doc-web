# ruff: noqa: E402
"""Scout102 force-fresh public/synthetic native owner comparison; no defaults."""

import base64
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "benchmarks/providers"))
import carbon_guard as guard
from doc_web.literal_fidelity import SourcePageReview
from modules.common.table_source_review import POLICY, SourceOnlyReader
from modules.common.literal_table_review import review_literal_tables
from benchmarks.scorers.image_crop_scorer import get_assert as crop_score

R = guard.RESULTS
E = ROOT / "docs/evals/evidence/089-carbon"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def save(p, d):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")


def google(model, system, text, image, mime="image/png", schema=None, stage=None):
    from benchmarks.scripts.carbon_native import generate

    return generate(model, system, text, image, mime, schema, stage)


def table_reader(model, case):
    if model == "gpt-6-astra":
        os.environ["CARBON_STAGE"] = "table-" + case + "-control"
        guard.install()
        return SourceOnlyReader(max_requests=1, budget_usd=1.5)

    def reader(path, requests):
        b = Path(path).read_bytes()
        with Image.open(path) as im:
            w, h = im.size
        raw, d = google(
            model,
            POLICY,
            f"Source image dimensions: {w} x {h} pixels. Read source tables; return JSON only.",
            b,
            schema=SourcePageReview.model_json_schema(),
            stage="table-" + case + "-candidate" + os.environ.get("CARBON_SUFFIX", ""),
        )
        requests.append(
            {
                "requested_model": model,
                "served_model": d["modelVersion"],
                "response_id": d.get("responseId"),
                "status": "completed",
                "usage": d["usageMetadata"],
                "raw_response": raw,
                "submitted_image_sha256": sha(b),
            }
        )
        return SourcePageReview.model_validate_json(raw)

    return reader


def render_crop(key):
    image = (
        (ROOT / f"benchmarks/input/source-pages-b64/{key}.b64.txt").read_text().strip()
    )
    code = """const p=require(process.argv[1]); process.stdout.write(JSON.stringify(p({vars:JSON.parse(require('fs').readFileSync(0,'utf8')),provider:{id:"google:gemini-4-carbon"}})))"""
    out = subprocess.check_output(
        [
            "node",
            "-e",
            code,
            str(ROOT / "benchmarks/prompts/crop-conservative-count.js"),
        ],
        input=json.dumps({"image": image}),
        text=True,
    )
    return json.loads(out)


CROP_SCHEMA = {
    "type": "object",
    "properties": {
        "images": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "bbox": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 4,
                        "maxItems": 4,
                    },
                },
                "required": ["description", "bbox"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["images"],
    "additionalProperties": False,
}


def tables():
    from doc_web.literal_tables import compare_tables

    results = (
        json.loads((E / "table-results.json").read_text())
        if (E / "table-results.json").exists()
        else []
    )
    for case in (
        [sys.argv[2]]
        if len(sys.argv) > 2
        else ("image-positive", "ambiguity-negative", "native-positive")
    ):
        initial = json.loads((E / f"initial-{case}.json").read_text())
        source = (
            ROOT / f"testdata/literal-table-fidelity/confirmation-v2/{case}/page.png"
        )
        initial["image"] = str(source)
        initial["source"] = []
        for model, label in [
            ("gemini-4-carbon", "candidate"),
            ("gpt-6-astra", "control"),
        ]:
            if len(sys.argv) > 3 and sys.argv[3] != label:
                continue
            out = R / f"table-{case}-{label}{os.environ.get('CARBON_SUFFIX', '')}.jsonl"
            row = review_literal_tables(
                [initial],
                out_path=out,
                run_id=f"carbon-{case}-{label}",
                reader=table_reader(model, case),
            )[0]
            report = json.loads(
                Path(row["literal_fidelity"]["report_path"]).read_text()
            )
            golden = (source.parent / "golden.html").read_text()
            reviewed = report["tables"][0]["review"] if report["tables"] else {}
            quality = compare_tables(golden, reviewed.get("html", ""))
            result = {
                "case": case,
                "arm": label,
                "status": report["status"],
                "uncertainties": reviewed.get("uncertain_cells", []),
                "literal_score": quality,
                "report": str(
                    Path(row["literal_fidelity"]["report_path"]).relative_to(ROOT)
                ),
            }
            results.append(result)
            save(E / "table-results.json", results)
            print(case, label, report["status"], quality["pass"], flush=True)
        if (
            False
            and case != "ambiguity-negative"
            and (
                not results[-2]["literal_score"]["pass"] or results[-2]["uncertainties"]
            )
        ):
            print("STOP candidate literal on clearcell mismatch/hold", flush=True)
            break


def crops(mode):
    if mode == "full":
        raise RuntimeError(
            "Historical scorer-only batch disabled: source-completeness requires manual per-case barrier; use carbon_reading.py screen KEY in a fresh authorized run identity"
        )
    keys = (
        [sys.argv[2]]
        if len(sys.argv) > 2
        else ["Image011"]
        + [
            c["key"]
            for c in json.loads((E / "preflight.json").read_text())["crop"]
            if c["key"] != "Image011"
        ]
    )
    if mode in ("screen", "recovery1") and len(sys.argv) <= 2:
        keys = ["Image011"]
    elif mode == "full":
        keys = [k for k in keys if k != "Image011"]
    results = []
    for key in keys:
        msgs = render_crop(key)
        parts = msgs[0]["parts"]
        image = base64.b64decode(parts[1]["inlineData"]["data"])
        mime = parts[1]["inlineData"]["mimeType"]
        for model, label in [
            ("gemini-4-carbon", "candidate"),
            ("gemini-3-flash-preview", "control"),
        ]:
            if len(sys.argv) > 3 and label != sys.argv[3]:
                continue
            raw, d = google(
                model,
                "",
                parts[0]["text"],
                image,
                mime,
                schema=CROP_SCHEMA if label == "candidate" else None,
                stage=f"crop-{mode}-{key}-{label}"
                + ("-recovery1" if key == "Image000" and label == "candidate" else ""),
            )
            score = crop_score(raw, {"vars": {"golden_key": key}})
            save(
                E / f"crop-{mode}-{key}-{label}.json",
                {"raw": raw, "score": score, "served": d["modelVersion"]},
            )
            results.append({"key": key, "arm": label, **score})
            save(E / f"crop-{mode}-results.json", results)
            print(key, label, score, flush=True)
        if False and len(results) >= 2 and not results[-2]["pass"]:
            print("STOP affected crop lane: source review required", flush=True)
            break


def install_ocr():
    from modules.common.google_client import GeminiVisionClient, _decode_data_uri

    def generate(
        self,
        model,
        system_prompt,
        user_text,
        image_data,
        temperature=0,
        max_tokens=4096,
    ):
        b, mime = _decode_data_uri(image_data)
        actual_model = (
            "gemini-4-carbon"
            if os.environ["CARBON_STAGE"].endswith("candidate")
            else model
        )
        raw, d = google(
            actual_model,
            system_prompt,
            user_text,
            b,
            mime,
            stage=os.environ["CARBON_STAGE"],
        )
        u = d["usageMetadata"]
        usage = SimpleNamespace(
            prompt_token_count=u["promptTokenCount"],
            candidates_token_count=u.get("candidatesTokenCount", 0),
            thoughts_token_count=u.get("thoughtsTokenCount", 0),
            cached_content_token_count=u.get("cachedContentTokenCount", 0),
        )
        return raw, usage, d.get("responseId")

    GeminiVisionClient.__init__ = lambda self, api_key=None: None
    GeminiVisionClient.generate_vision = generate


def ocr():
    from benchmarks.scorers.handwritten_notes_transcription import (
        score_page_html_artifact,
    )

    startup = R / "startup"
    startup.mkdir(exist_ok=True)
    (startup / "sitecustomize.py").write_text(
        "import sys;sys.path.insert(0,"
        + repr(str(ROOT))
        + "); from benchmarks.scripts.carbon_reading import install_ocr; install_ocr()\n"
    )
    results = (
        json.loads((E / "ocr-results.json").read_text())
        if (E / "ocr-results.json").exists()
        else []
    )
    for fixture in ["barney"]:
        for model, label in [
            ("gemini-4-carbon", "candidate"),
            ("gemini-3.8-flash", "control"),
        ]:
            recipe = yaml.safe_load(
                (
                    ROOT / f"configs/recipes/gpt61-ocr-gemini-3.7-flash-{fixture}.yaml"
                ).read_text()
            )
            recipe["stages"][1]["params"]["model"] = (
                "gemini-3.8-flash"  # eval-only Gemini client dispatch shim; actual wire model is explicit
            )
            recipe["stages"][1]["params"]["max_long_side"] = (
                0  # Scout102 approved original pixels for both arms
            )
            recipe["stages"][1]["params"]["max_output_tokens"] = (
                32768 if label == "candidate" else 16384
            )
            path = ROOT / f"configs/recipes/carbon-ocr-{label}-{fixture}.yaml"
            path.write_text(yaml.safe_dump(recipe, sort_keys=False))
            run = f"carbon-ocr-{fixture}-{label}-20261110"
            log = R / (
                run
                + ("-operational1" if (R / (run + ".log")).exists() else "")
                + ".log"
            )
            if log.exists():
                raise RuntimeError("fresh OCR invocation required")
            env = dict(
                os.environ,
                PYTHONPATH=str(startup) + ":" + str(ROOT),
                CARBON_STAGE=f"ocr-{fixture}-{label}",
            )
            with log.open("w") as f:
                rc = subprocess.run(
                    [
                        sys.executable,
                        "driver.py",
                        "--recipe",
                        str(path.relative_to(ROOT)),
                        "--run-id",
                        run,
                        "--allow-run-id-reuse",
                        "--end-at",
                        "ocr_ai",
                        "--instrument",
                    ],
                    cwd=ROOT,
                    env=env,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                ).returncode
            artifact = ROOT / f"output/runs/{run}/02_ocr_ai_gpt51_v1/pages_html.jsonl"
            if rc or not artifact.exists():
                raise RuntimeError("driver OCR operational failure: " + run)
            score = score_page_html_artifact(
                ROOT / f"testdata/handwritten-notes-{fixture}-real.txt", artifact
            )
            results.append(
                {"fixture": fixture, "arm": label, "driver_exit": rc, "score": score}
            )
            save(E / "ocr-results.json", results)
            print(fixture, label, score["overall_ratio"], flush=True)
        # Both approved fixtures remain measured independently; no same-case favorable repeat.


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "tables":
        tables()
    elif mode in ("screen", "recovery1", "full"):
        crops(mode)
    elif mode == "ocr":
        ocr()
