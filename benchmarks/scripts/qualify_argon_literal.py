# ruff: noqa: E402
"""Frozen pagewise native qualification and real-driver receipt consumption."""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from modules.common.google_table_source_review import google_request
from modules.common.table_source_review import astra_request
from modules.extract.ocr_ai_gpt51_v1.main import build_system_prompt
from doc_web.literal_tables import compare_tables

PANEL = ROOT / "benchmarks/fixtures/argon-literal-qualification-v1"
EVIDENCE = ROOT / "docs/evals/evidence/073-argon-literal-qualification"
RESULTS = ROOT / "benchmarks/results/argon-literal-qualification-20261013"
PYTHON = sys.executable
ORDER = ["N1", "A1", "N2", "N3", "R1", "R2", "R3", "A2"]
ASTRA_FIRST = {"N1", "N3", "R3", "A2"}
REPEATS = ["N3", "R1", "R3", "A1"]
MODELS = {"astra": "gpt-6-astra", "argon": "gemini-4-argon"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as out:
        out.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def pages():
    return {
        p["case_id"]: p
        for p in json.loads((PANEL / "manifest.json").read_text())["pages"]
    }


def ocr_body(image_path):
    data = Path(image_path).read_bytes()
    return {
        "model": "gpt-6-astra",
        "max_output_tokens": 8192,
        "store": False,
        "service_tier": "default",
        "reasoning": {"effort": "medium"},
        "input": [
            {
                "role": "system",
                "content": [
                    {"type": "input_text", "text": build_system_prompt(None, True)}
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": 'Return HTML only. FIRST line MUST be: <meta name="ocr-metadata" data-ocr-quality="0.0-1.0" data-ocr-integrity="0.0-1.0" data-continuation-risk="0.0-1.0">',
                    },
                    {
                        "type": "input_image",
                        "detail": "original",
                        "image_url": "data:image/png;base64,"
                        + base64.b64encode(data).decode(),
                    },
                ],
            },
        ],
    }


def request_body(case, arm, kind="reader"):
    image = PANEL / pages()[case]["render"]
    if kind == "ocr":
        return ocr_body(image)
    return google_request(image) if arm == "argon" else astra_request(image)


def stripped_body(body):
    body = copy.deepcopy(body)
    if "input" in body:
        for msg in body["input"]:
            for part in msg["content"]:
                if part["type"] == "input_image":
                    part["image_url"] = "<image-bytes-counted-separately>"
    else:
        for msg in body["contents"]:
            for part in msg["parts"]:
                if "inlineData" in part:
                    part["inlineData"]["data"] = "<image-bytes-counted-separately>"
    return body


def token_bound(case, body, google=False):
    width, height = pages()[case]["render_dimensions_px"]
    # Astra: original, 32px patches,1.2multiplier. Google documented768px/258 tiles.
    image = (
        math.ceil(math.ceil(width / 768) * math.ceil(height / 768) * 258)
        if google
        else math.ceil(math.ceil(width / 32) * math.ceil(height / 32) * 1.2) + 1
    )
    # UTF-8 bytes are a conservative bound for byte/BPE text+schema, plus4096 framing.
    framing = len(json.dumps(stripped_body(body), ensure_ascii=False).encode()) + 4096
    bound = image + framing
    if bound > 26000 or width > 65535 or height > 65535:
        raise RuntimeError("Full native input exceeds approved envelope")
    return {
        "image_tokens_upper": image,
        "text_schema_framing_upper": framing,
        "complete_input_upper": bound,
        "dimensions": [width, height],
        "admission_ceiling": 26000,
    }


def prepare():
    if (EVIDENCE / "freeze.json").exists():
        raise RuntimeError("Existing freeze is immutable")
    matrix, bounds = [], {}
    for case in ORDER:
        body = request_body(case, "astra", "ocr")
        bounds["ocr-" + case] = token_bound(case, body)
        matrix.append(
            {
                "stage": "ocr-" + case,
                "case": case,
                "kind": "ocr",
                "model": MODELS["astra"],
                "request_sha256": sha(json.dumps(body, sort_keys=True).encode()),
                "reserved_usd": 0.7346,
                "input_token_bound": 26000,
                "max_output_tokens": 8192,
            }
        )
        arms = ["astra", "argon"] if case in ASTRA_FIRST else ["argon", "astra"]
        for arm in arms:
            body = request_body(case, arm)
            stage = f"reader-{case}-{arm}"
            bounds[stage] = token_bound(case, body, arm == "argon")
            matrix.append(
                {
                    "stage": stage,
                    "case": case,
                    "arm": arm,
                    "kind": "reader",
                    "model": MODELS[arm],
                    "request_sha256": sha(json.dumps(body, sort_keys=True).encode()),
                    "reserved_usd": 0.37968 if arm == "argon" else 1.5,
                    "input_token_bound": 26000,
                    "max_output_tokens": 32768 if arm == "argon" else 8192,
                }
            )
    for case in REPEATS:
        arms = ["argon", "astra"] if case in ASTRA_FIRST else ["astra", "argon"]
        for arm in arms:
            source = next(x for x in matrix if x["stage"] == f"reader-{case}-{arm}")
            matrix.append(
                {
                    **source,
                    "stage": f"repeat-{case}-{arm}",
                    "conditional": True,
                    "required_gate": str(EVIDENCE / "panel-clearance.json"),
                }
            )
    for item in matrix:
        if item["case"] not in ("N1", "A1") and not item.get("conditional"):
            item["required_gate"] = str(EVIDENCE / "screen-clearance.json")
    oldroot = Path("/Users/cam/.codex/worktrees/scout092-argon-docweb-20261013")
    old = [
        oldroot / "benchmarks/results/argon-20261013/ledger.json",
        oldroot / "benchmarks/results/argon-levels-20261013/ledger.json",
    ]
    config = {
        "result_dir": str(RESULTS),
        "cap_usd": 3,
        "prior_exposure_usd": 0.86667725,
        "owner_cap_usd": 15,
        "campaign_prior_exposure_usd": 3.877369745,
        "campaign_cap_usd": 35,
        "max_calls": 33,
        "operational_recovery": True,
        "old_ledger_sha256": {str(p): sha(p.read_bytes()) for p in old},
        "matrix": matrix,
    }
    codes = [
        Path(__file__),
        ROOT / "benchmarks/providers/literal_qualification_guard.py",
        ROOT / "modules/common/google_table_source_review.py",
        ROOT / "modules/common/table_source_review.py",
        ROOT / "modules/common/literal_table_review.py",
        ROOT / "modules/common/literal_fidelity_bundle.py",
        ROOT / "modules/common/openai_client.py",
        ROOT / "modules/adapter/literal_table_review_v1/main.py",
        ROOT / "modules/build/build_chapter_html_v1/main.py",
        ROOT / "modules/build/build_chapter_html_v1/module.yaml",
        ROOT / "modules/adapter/literal_table_review_v1/module.yaml",
        ROOT / "modules/extract/ocr_ai_gpt51_v1/main.py",
        ROOT / "doc_web/literal_fidelity.py",
        ROOT / "doc_web/literal_tables.py",
        ROOT / "driver.py",
        ROOT / "modules/extract/extract_pdf_images_capped_v1/main.py",
        ROOT / "modules/common/ocr_request_receipt.py",
        ROOT / "modules/common/ocr_literal_policy.py",
        ROOT / "modules/common/utils.py",
        ROOT / "modules/common/load_artifact_v1/main.py",
        ROOT / "doc_web/env.py",
        ROOT / "schemas.py",
        ROOT / "configs/recipes/recipe-pdf-literal-tables-html.yaml",
        ROOT / "configs/recipes/recipe-pdf-literal-tables-html-argon.yaml",
    ]
    fixtures = [
        p
        for p in PANEL.rglob("*")
        if p.is_file()
        and "build" not in p.relative_to(PANEL).parts
        and p.suffix != ".pyc"
    ]
    freeze = {
        "base_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "config": config,
        "source_manifest_sha256": sha((PANEL / "manifest.json").read_bytes()),
        "bounds": bounds,
        "code_sha256": {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in codes},
        "fixture_sha256": {
            str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in fixtures
        },
        "live_authorization": "Root explicit clearance required after source and offline review",
        "opening": ["N1", "A1"],
        "repeats": REPEATS,
    }
    save(EVIDENCE / "freeze.json", freeze)
    save(EVIDENCE / "campaign.json", config)
    RESULTS.mkdir(parents=True, exist_ok=True)
    startup = RESULTS / "startup"
    startup.mkdir(exist_ok=True)
    (startup / "sitecustomize.py").write_text(
        f"import sys\nsys.path.insert(0,{str(ROOT)!r})\nfrom benchmarks.providers.literal_qualification_guard import install\ninstall()\n"
    )
    print(
        "Frozen",
        len(matrix),
        "scheduledPOSTs; input max",
        max(x["complete_input_upper"] for x in bounds.values()),
        ";0paidcalls",
    )


def check_freeze():
    frozen = json.loads((EVIDENCE / "freeze.json").read_text())
    for group in ("code_sha256", "fixture_sha256"):
        for path, digest in frozen[group].items():
            if sha((ROOT / path).read_bytes()) != digest:
                raise RuntimeError("Frozen producing/source code changed: " + path)
    return frozen


def run_command(command, stage, *, live=True, namespace="live"):
    if live:
        check_freeze()
        if (
            os.environ.get("DOC_WEB_LITERAL_LIVE") != "1"
            or not (EVIDENCE / "clearance.json").exists()
        ):
            raise RuntimeError("Frozen source/offline/root clearance required")
        clearance = json.loads((EVIDENCE / "clearance.json").read_text())
        if clearance.get("allowed") is not True or clearance.get(
            "freeze_sha256"
        ) != sha((EVIDENCE / "freeze.json").read_bytes()):
            raise RuntimeError("Root clearance does not bind this frozen attempt")
    env = dict(os.environ)
    if live:
        env["DOC_WEB_LITERAL_CAMPAIGN_FILE"] = str(EVIDENCE / "campaign.json")
        env["DOC_WEB_LITERAL_STAGE"] = stage
        env["PYTHONPATH"] = str(RESULTS / "startup") + os.pathsep + str(ROOT)
    started = time.monotonic()
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    folder = RESULTS / namespace
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / (stage + ".log")).open("x") as out:
        out.write(result.stdout)
    save(
        folder / (stage + "-command.json"),
        {
            "command": command,
            "returncode": result.returncode,
            "wall_seconds": time.monotonic() - started,
        },
    )
    if result.returncode not in (0, 2):
        raise RuntimeError(f"Stage {stage} failed; inspect preserved log")
    return result.returncode


def common_path(case, namespace="live"):
    return (
        ROOT
        / f"output/runs/literal073-{namespace}-ocr-{case}/02_ocr_ai_gpt51_v1/pages_html.jsonl"
    )


def ocr_case(case, namespace="live"):
    row = pages()[case]
    stage = "ocr-" + case
    settings = RESULTS / namespace / (stage + "-settings.yaml")
    settings.parent.mkdir(parents=True, exist_ok=True)
    import yaml

    settings.write_text(
        yaml.safe_dump(
            {
                "stage_params": {
                    "pdf_to_images": {
                        "start": row["source_pdf_page"],
                        "end": row["source_pdf_page"],
                    }
                }
            }
        )
    )
    runid = "literal073-" + namespace + "-" + stage
    command = [
        PYTHON,
        "driver.py",
        "--recipe",
        "configs/recipes/recipe-pdf-literal-tables-html.yaml",
        "--settings",
        str(settings),
        "--input-pdf",
        str(PANEL / row["source_pdf"]),
        "--run-id",
        runid,
        "--output-dir",
        str(ROOT / "output/runs" / runid),
        "--end-at",
        "ocr_ai",
    ]
    code = run_command(command, stage, live=namespace == "live", namespace=namespace)
    rows = [
        json.loads(x) for x in common_path(case, namespace).read_text().splitlines()
    ]
    if (
        code
        or len(rows) != 1
        or sha(Path(rows[0]["image"]).read_bytes()) != row["render_sha256"]
    ):
        raise RuntimeError(
            "Actual driver OCR/render topology differs from frozen source"
        )
    return rows


def reader_case(case, arm, repeat=False, namespace="live"):
    stage = f"{'repeat' if repeat else 'reader'}-{case}-{arm}"
    out = RESULTS / namespace / stage / "pages_reviewed.jsonl"
    command = [
        PYTHON,
        "-m",
        "modules.adapter.literal_table_review_v1.main",
        "--pages",
        str(common_path(case, namespace)),
        "--out",
        str(out),
        "--model",
        MODELS[arm],
        "--max-pages",
        "1",
        "--max-requests",
        "1",
        "--budget-usd",
        "1.5",
        "--run-id",
        "literal073-" + namespace + "-" + stage,
    ]
    code = run_command(command, stage, live=namespace == "live", namespace=namespace)
    rows = [json.loads(x) for x in out.read_text().splitlines()]
    report = json.loads(Path(rows[0]["literal_fidelity"]["report_path"]).read_text())
    if len(report["requests"]) != 1:
        raise RuntimeError("No unique source-read receipt")
    save(out.parent / "native-record.json", report["requests"][0])
    gold = json.loads((PANEL / pages()[case]["gold"]).read_text())
    actual = "".join(x["review"]["html"] for x in report["tables"])
    expected = "".join(x["html"] for x in gold["tables"])
    comparison = compare_tables(expected, actual)
    result = {
        "case": case,
        "arm": arm,
        "stage": stage,
        "returncode": code,
        "review_status": report["status"],
        "source_exact": comparison["pass"],
        "comparison": comparison,
        "source_table_count": len(report["tables"]),
        "uncertain_cells": [
            c for t in report["tables"] for c in t["review"]["uncertain_cells"]
        ],
        "record_path": str(out.parent / "native-record.json"),
        "report_path": rows[0]["literal_fidelity"]["report_path"],
        "elapsed_seconds": report["requests"][0].get("elapsed_seconds"),
        "independent_source_review": "pending",
    }
    save(out.parent / "metrics.json", result)
    print(
        json.dumps(
            {
                k: result[k]
                for k in [
                    "case",
                    "arm",
                    "stage",
                    "review_status",
                    "source_exact",
                    "elapsed_seconds",
                ]
            }
        )
    )
    return result


def export_group(group, arm, namespace="live", source_namespace=None):
    import yaml

    cases = [group + str(i) for i in (1, 2, 3)]
    source_namespace = source_namespace or namespace
    rows = []
    records = []
    for logical, case in enumerate(cases, 1):
        initial = json.loads(common_path(case, source_namespace).read_text().splitlines()[0])
        initial["page_number"] = logical
        rows.append(initial)
        record = RESULTS / source_namespace / f"reader-{case}-{arm}" / "native-record.json"
        records.append(
            {
                "image_sha256": sha(Path(initial["image"]).read_bytes()),
                "record_path": str(record),
                "record_sha256": sha(record.read_bytes()),
            }
        )
    folder = RESULTS / namespace / f"export-{group}-{arm}"
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / "common-pages.jsonl"
    with source.open("x") as out:
        for row in rows:
            out.write(json.dumps(row) + "\n")
    retained = folder / "retained.json"
    save(
        retained,
        {
            "schema_version": "retained_source_reviews_v1",
            "model": MODELS[arm],
            "records": records,
        },
    )
    recipe = yaml.safe_load(
        (ROOT / "configs/recipes/recipe-pdf-literal-tables-html.yaml").read_text()
    )
    recipe["stages"] = recipe["stages"][1:]
    recipe["stages"][0] = {
        "id": "ocr_ai",
        "stage": "extract",
        "module": "load_artifact_v1",
        "out": "pages_html.jsonl",
        "params": {"path": str(source), "out": "pages_html.jsonl", "schema_version": "page_html_v1"},
    }
    recipe["stages"][1]["params"].update(
        model=MODELS[arm], source_review_receipts=str(retained)
    )
    recipe["stages"][-1]["params"]["literal_reader_model"] = MODELS[arm]
    path = folder / "recipe.yaml"
    with path.open("x") as out:
        out.write(yaml.safe_dump(recipe, sort_keys=False))
    runid = f"literal073-{namespace}-export-{group}-{arm}"
    command = [
        PYTHON,
        "driver.py",
        "--recipe",
        str(path),
        "--run-id",
        runid,
        "--output-dir",
        str(ROOT / "output/runs" / runid),
    ]
    code = run_command(
        command,
        "export-" + group + "-" + arm,
        live=namespace == "live",
        namespace=namespace,
    )
    if code:
        raise RuntimeError("Real driver export failed")
    html = ROOT / "output/runs" / runid / "output/html"
    manifest = json.loads((html / "manifest.json").read_text())
    qualified = json.loads(
        (html / "provenance/literal-fidelity/qualification.json").read_text()
    )
    if len(qualified["reports"]) != 3:
        raise RuntimeError("Incomplete positive batch export")
    expected = "".join(
        t["html"]
        for c in cases
        for t in json.loads((PANEL / pages()[c]["gold"]).read_text())["tables"]
    )
    actual = "".join(p.read_text() for p in sorted(html.glob("chapter-*.html")))
    comparison = compare_tables(expected, actual)
    if not comparison["pass"]:
        raise RuntimeError("Final exported table differs from frozen source")
    save(
        folder / "export-proof.json",
        {
            "run_id": runid,
            "manifest": str(html / "manifest.json"),
            "qualification": qualified,
            "comparison": comparison,
            "manifest_sha256": sha((html / "manifest.json").read_bytes()),
            "source_cases": cases,
        },
    )
    print("Verified real driver", runid)
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "operation", choices=["prepare", "ocr", "reader", "repeat", "export"]
    )
    parser.add_argument("--case")
    parser.add_argument("--arm", choices=list(MODELS))
    parser.add_argument("--group", choices=["N", "R"])
    args = parser.parse_args()
    if args.operation == "prepare":
        prepare()
    elif args.operation == "ocr":
        ocr_case(args.case)
    elif args.operation in ("reader", "repeat"):
        reader_case(args.case, args.arm, args.operation == "repeat")
    else:
        export_group(args.group, args.arm)


if __name__ == "__main__":
    main()
