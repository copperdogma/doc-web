import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.scorers.auto_book_type_detection import score_case, summarize_results
from benchmarks.scripts.intake_scope import build_scope_blocked_row


DEFAULT_CORPUS = ROOT / "benchmarks/golden/auto-book-type-detection/corpus.json"
SUPPORTED_INPUT_KINDS = frozenset({"pdf"})


def resolve_input_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return ROOT / path


def run_command(cmd):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    return subprocess.run(cmd, cwd=ROOT, env=env, text=True, capture_output=True)


def is_transient_failure(output: str) -> bool:
    markers = (
        "APIConnectionError",
        "Connection error",
        "timed out",
        "429",
        "Rate limit",
        "RateLimitError",
    )
    return any(marker in output for marker in markers)


def run_case(case: dict, run_root: Path) -> dict:
    input_path = resolve_input_path(case["path"])
    if case.get("input_kind") not in SUPPORTED_INPUT_KINDS:
        return build_scope_blocked_row(
            case,
            input_path,
            surface_key="recommendation_only_intake",
            surface_label="recommendation-only intake automation",
            supported_input_kinds=SUPPORTED_INPUT_KINDS,
        )
    if not input_path.exists():
        return {
            "id": case["id"],
            "status": "failed",
            "failure_step": "input",
            "error": f"Missing input: {input_path}",
        }

    case_dir = run_root / case["id"]
    sheets_dir = case_dir / "contact-sheets"
    manifest = case_dir / "build_contact_sheets.jsonl"
    overview = case_dir / "overview_plan.jsonl"
    zoom = case_dir / "overview_plan_zoom.jsonl"
    gap = case_dir / "overview_plan_gap.jsonl"
    final = case_dir / "overview_plan_final.jsonl"
    case_dir.mkdir(parents=True, exist_ok=True)

    builder_cmd = [
        sys.executable,
        "modules/intake/contact_sheet_builder_v1/main.py",
        "--output_dir",
        str(sheets_dir),
        "--out",
        str(manifest),
        "--max_width",
        "200",
        "--grid_cols",
        "5",
        "--grid_rows",
        "4",
    ]
    if case["input_kind"] == "pdf":
        builder_cmd.extend(["--pdf", str(input_path)])
    else:
        builder_cmd.extend(["--input_dir", str(input_path)])

    steps = [
        ("builder", builder_cmd),
        (
            "overview",
            [
                sys.executable,
                "modules/intake/contact_sheet_overview_v1/main.py",
                "--manifest",
                str(manifest),
                "--sheets_dir",
                str(sheets_dir),
                "--out",
                str(overview),
            ],
        ),
        (
            "zoom",
            [
                sys.executable,
                "modules/intake/zoom_refine_v1/main.py",
                "--plan_in",
                str(overview),
                "--out",
                str(zoom),
            ],
        ),
        (
            "gap",
            [
                sys.executable,
                "modules/intake/gap_analyzer_v1/main.py",
                "--plan_in",
                str(zoom),
                "--out",
                str(gap),
                "--catalog_path",
                "modules/module_catalog.yaml",
            ],
        ),
        (
            "confirm",
            [
                sys.executable,
                "modules/intake/confirm_plan_v1/main.py",
                "--plan",
                str(gap),
                "--out",
                str(final),
                "--auto-approve",
            ],
        ),
    ]

    row = {
        "id": case["id"],
        "input_kind": case["input_kind"],
        "path": str(input_path),
        "status": "ok",
    }
    for step_name, cmd in steps:
        attempts = 3 if step_name in {"overview", "zoom"} else 1
        result = None
        for attempt in range(1, attempts + 1):
            result = run_command(cmd)
            combined_output = (result.stderr or "") + "\n" + (result.stdout or "")
            if result.returncode == 0:
                break
            if attempt < attempts and is_transient_failure(combined_output):
                time.sleep(attempt * 2)
                continue
            row["status"] = "failed"
            row["failure_step"] = step_name
            row["error"] = combined_output[-1200:]
            return row

    plan = json.loads(final.read_text(encoding="utf-8").splitlines()[0])
    row["final_artifact"] = str(final)
    row["plan"] = {
        "book_type": plan.get("book_type"),
        "recommended_recipe": plan.get("recommended_recipe"),
        "signals": plan.get("signals", []),
        "signal_evidence_count": len(plan.get("signal_evidence", [])),
    }
    row["score"] = score_case(case, plan)
    return row


def main():
    parser = argparse.ArgumentParser(description="Run the auto-book-type-detection benchmark harness")
    parser.add_argument("--corpus", default=str(DEFAULT_CORPUS))
    parser.add_argument("--output", default=None)
    parser.add_argument("--run-root", default=str(ROOT / "output/runs/auto-book-type-detection"))
    args = parser.parse_args()

    corpus_path = Path(args.corpus)
    if not corpus_path.is_absolute():
        corpus_path = ROOT / corpus_path
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))

    run_root = Path(args.run_root)
    run_root.mkdir(parents=True, exist_ok=True)

    rows = []
    for case in corpus:
        row = run_case(case, run_root)
        rows.append(row)
        print(json.dumps(row))
        sys.stdout.flush()

    summary = summarize_results(rows)
    payload = {
        "measured_at": datetime.utcnow().date().isoformat(),
        "summary": summary,
        "rows": rows,
    }

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = ROOT / "benchmarks/results" / f"auto-book-type-detection-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("SUMMARY " + json.dumps(summary))
    print("RESULT_PATH " + str(output_path))


if __name__ == "__main__":
    main()
