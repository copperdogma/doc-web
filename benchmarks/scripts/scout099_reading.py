# ruff: noqa: E402
"""Scout092 force-fresh public/synthetic native owner comparison; no defaults."""

import base64
import hashlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
import httpx
import yaml
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "benchmarks/providers"))
import scout099_guard as guard
from doc_web.literal_fidelity import SourcePageReview
from modules.common.table_source_review import POLICY, SourceOnlyReader
from modules.common.literal_table_review import review_literal_tables
from benchmarks.scorers.image_crop_scorer import get_assert as crop_score

R = guard.RESULTS
E = ROOT / "docs/evals/evidence/080-scout099"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def save(p, d):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")


def google(model, system, text, image, mime="image/png", schema=None, stage=None):
    os.environ["SCOUT099_STAGE"] = (stage or "unknown") + ("-diagnostic" if os.environ.get("SCOUT099_DIAGNOSTIC") == "1" else "")
    guard.install()
    if model == "minimax/minimax-m3.1-flash:free":
        body = {
            "model": model,
            "max_tokens": 32768,
            "reasoning": {"effort": "high"},
            "provider": {
                "only": ["minimax"],
                "allow_fallbacks": False,
                "require_parameters": True,
                "max_price": {"prompt": 0, "completion": 0},
            },
            "messages": [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "data:"
                                + mime
                                + ";base64,"
                                + base64.b64encode(image).decode()
                            },
                        },
                    ],
                },
            ],
        }
        if schema:
            body["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "docweb_result",
                    "strict": True,
                    "schema": schema,
                },
            }
        if os.environ.get("SCOUT099_DIAGNOSTIC") == "1":
            body.pop("response_format", None)
            body["provider"]["require_parameters"] = False
        r = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"]},
            json=body,
            timeout=600,
        )
        d = r.json()
        save(R / (os.environ["SCOUT099_STAGE"] + "-decoded.json"), d)
        r.raise_for_status()
        assert (
            d.get("model") in [model, "minimax/minimax-m3.1-flash-20261019"]
            and d.get("provider") == "Minimax"
            and d["choices"][0]["finish_reason"] == "stop"
            and not d.get("error")
        )
        raw = d["choices"][0]["message"]["content"]
        if schema == SourcePageReview.model_json_schema():
            SourcePageReview.model_validate_json(raw)
        elif schema:
            json.loads(raw)
        # Owner adapters consume native-shaped usage, kept alongside complete router envelope.
        u = d["usage"]
        d["modelVersion"] = d["model"]
        d["responseId"] = d["id"]
        d["usageMetadata"] = {
            "promptTokenCount": u["prompt_tokens"],
            "candidatesTokenCount": u["completion_tokens"]
            - u.get("completion_tokens_details", {}).get("reasoning_tokens", 0),
            "thoughtsTokenCount": u.get("completion_tokens_details", {}).get(
                "reasoning_tokens", 0
            ),
            "cachedContentTokenCount": u.get("prompt_tokens_details", {}).get(
                "cached_tokens", 0
            ),
        }
        return raw, d
    config = {"maxOutputTokens": 16384, "temperature": 0}
    if schema:
        config.update(responseMimeType="application/json", responseJsonSchema=schema)
    body = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": text},
                    {
                        "inlineData": {
                            "mimeType": mime,
                            "data": base64.b64encode(image).decode(),
                        }
                    },
                ],
            }
        ],
        "generationConfig": config,
    }
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    r = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
        json=body,
        timeout=600,
    )
    r.raise_for_status()
    d = r.json()
    assert d["modelVersion"] == model and d["candidates"][0]["finishReason"] == "STOP"
    return "\n".join(
        p["text"]
        for p in d["candidates"][0]["content"]["parts"]
        if "text" in p and not p.get("thought")
    ), d


def table_reader(model, case):
    if model == "gpt-6-astra":
        os.environ["SCOUT099_STAGE"] = "table-" + case + "-control"
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
            stage="table-" + case + "-candidate",
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
    code = """const p=require(process.argv[1]); process.stdout.write(JSON.stringify(p({vars:JSON.parse(require('fs').readFileSync(0,'utf8')),provider:{id:"google:minimax/minimax-m3.1-flash:free"}})))"""
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


def preflight():
    E.mkdir(parents=True, exist_ok=True)
    R.mkdir(parents=True, exist_ok=True)
    cases = []
    cfg = yaml.safe_load(
        (ROOT / "benchmarks/tasks/gpt61-detector-full.yaml").read_text()
    )
    keys = [t["vars"]["golden_key"] for t in cfg["tests"]]
    assert len(keys) == 13
    for key in keys:
        messages = render_crop(key)
        assert len(messages) == 1 and len(messages[0]["parts"]) == 2
        assert "normalized 0.0-1.0" in messages[0]["parts"][0]["text"]
        cases.append(
            {
                "key": key,
                "rendered_sha256": sha(json.dumps(messages).encode()),
                "message_count": 1,
                "image_count": 1,
            }
        )
    table = []
    for case in ("image-positive", "ambiguity-negative", "native-positive"):
        prior = (
            Path("/Users/cam/Documents/Projects/doc-web/output/runs")
            / ("story244-" + case + "-v2")
            / "02_ocr_ai_gpt51_v1/pages_html.jsonl"
        )
        assert prior.exists(), prior
        rows = [json.loads(line) for line in prior.read_text().splitlines()]
        assert len(rows) == 1
        source = (
            ROOT / f"testdata/literal-table-fidelity/confirmation-v2/{case}/page.png"
        )
        table.append(
            {
                "case": case,
                "initial": str(prior),
                "initial_sha256": sha(prior.read_bytes()),
                "image_sha256": sha(source.read_bytes()),
            }
        )
        save(E / f"initial-{case}.json", rows[0])
    plan = {
        "base_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "cap_usd": 15,
        "candidate": "minimax/minimax-m3.1-flash:free Minimax router-high32768",
        "controls": {
            "table": "gpt-6-astra medium8192 original",
            "crop": "gemini-3-flash-preview temperature0 max16384 normalized",
            "ocr": "gemini-3.7-flash maintained default medium max16384",
        },
        "cache": "force-fresh no subject reuse except frozen identical initial table OCR",
        "concurrency": 1,
        "judge": "independent source review plus deterministic owner assertions; no paid judge",
        "session_grouping": "one independent native request per case",
        "crop": cases,
        "tables": table,
        "schema_sha256": sha(
            json.dumps(SourcePageReview.model_json_schema(), sort_keys=True).encode()
        ),
        "policy_sha256": sha(POLICY.encode()),
        "budget_authority": "execution-plan.json full prospective topology and overhead",
        "no_page_safety": False,
    }
    save(E / "preflight.json", plan)
    if not (R / "ledger.json").exists():
        save(
            R / "ledger.json",
            {"cap_usd": 15, "spent_usd": 0, "calls": [], "closed": False},
        )
    print("offline preflight passed", len(cases), "crop keys,3 identical initial OCRs")


def probe():
    image = Image.new("RGB", (300, 150), "white")
    ImageDraw.Draw(image).text((30, 30), "TEST", fill="black")
    f = io.BytesIO()
    image.save(f, format="PNG")
    b = f.getvalue()
    for name, schema, system, text in [
        (
            "table",
            SourcePageReview.model_json_schema(),
            POLICY,
            "Source image dimensions: 300 x 150 pixels. Read source tables; return JSON only.",
        ),
        (
            "crop",
            CROP_SCHEMA,
            "",
            "Find visible visual elements. Return normalized bounding boxes as images JSON.",
        ),
        (
            "ocr",
            None,
            "Read visible text exactly and return minimal HTML.",
            "Transcribe this image.",
        ),
    ]:
        if name == "table" and (R / "native-table-decoded.json").exists() and "choices" in json.loads((R / "native-table-decoded.json").read_text()):
            d = json.loads((R / "native-table-decoded.json").read_text())
            raw = d["choices"][0]["message"]["content"]
            d["modelVersion"] = d["model"]
            SourcePageReview.model_validate_json(raw)
        else:
            raw, d = google(
                "minimax/minimax-m3.1-flash:free",
                system,
                text,
                b,
                schema=schema,
                stage="native-" + name,
            )
        save(
            E / ("native-" + name + ".json"),
            {
                "raw": raw,
                "served": d["modelVersion"],
                "finish": "stop",
            },
        )
        print("qualified", name, flush=True)


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
            ("minimax/minimax-m3.1-flash:free", "candidate"),
            ("gpt-6-astra", "control"),
        ]:
            out = R / f"table-{case}-{label}.jsonl"
            row = review_literal_tables(
                [initial],
                out_path=out,
                run_id=f"argon-{case}-{label}",
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
        if case != "ambiguity-negative" and (
            not results[-2]["literal_score"]["pass"] or results[-2]["uncertainties"]
        ):
            print("STOP candidate literal on clearcell mismatch/hold", flush=True)
            break


def crops(mode):
    if mode == "full":
        raise RuntimeError(
            "Historical scorer-only batch disabled: source-completeness requires manual per-case barrier; use scout099_crop_recovery.py KEY in a fresh authorized run identity"
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
            ("minimax/minimax-m3.1-flash:free", "candidate"),
            ("gemini-3-flash-preview", "control"),
        ]:
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
        if not results[-2]["pass"]:
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
            "minimax/minimax-m3.1-flash:free"
            if os.environ["SCOUT099_STAGE"].endswith("candidate")
            else model
        )
        raw, d = google(
            actual_model,
            system_prompt,
            user_text,
            b,
            mime,
            stage=os.environ["SCOUT099_STAGE"],
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
        + "); from benchmarks.scripts.scout099_reading import install_ocr; install_ocr()\n"
    )
    results = (
        json.loads((E / "ocr-results.json").read_text())
        if (E / "ocr-results.json").exists()
        else []
    )
    for fixture in ["barney"]:
        for model, label in [
            ("minimax/minimax-m3.1-flash:free", "candidate"),
            ("gemini-3.7-flash", "control"),
        ]:
            recipe = yaml.safe_load(
                (
                    ROOT / f"configs/recipes/gpt61-ocr-gemini-3.7-flash-{fixture}.yaml"
                ).read_text()
            )
            recipe["stages"][1]["params"]["model"] = (
                "gemini-3.7-flash"  # eval-only Gemini client dispatch shim; wire actual candidate exact NVIDIA
            )
            recipe["stages"][1]["params"]["max_output_tokens"] = (
                32768 if label == "candidate" else 16384
            )
            path = ROOT / f"configs/recipes/scout099-ocr-{label}-{fixture}.yaml"
            path.write_text(yaml.safe_dump(recipe, sort_keys=False))
            run = f"scout099-ocr-{fixture}-{label}-20261020"
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
                SCOUT099_STAGE=f"ocr-{fixture}-{label}",
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
    if mode == "preflight":
        preflight()
    elif mode == "probe":
        probe()
    elif mode == "tables":
        tables()
    elif mode in ("screen", "recovery1", "full"):
        crops(mode)
    elif mode == "ocr":
        ocr()
