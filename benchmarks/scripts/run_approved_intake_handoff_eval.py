import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.scorers.approved_intake_handoff import score_case, summarize_results  # noqa: E402


DEFAULT_CORPUS = ROOT / "benchmarks/golden/auto-book-type-detection/corpus.json"


def resolve_input_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return ROOT / path


def run_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
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


def load_first_stage_spec(recipe_path: str) -> dict | None:
    if not recipe_path or recipe_path == "no-recipe-needed":
        return None
    resolved_path = resolve_input_path(recipe_path)
    data = yaml.safe_load(resolved_path.read_text(encoding="utf-8")) or {}
    stages = data.get("stages") or []
    if not stages:
        return None
    first_stage = stages[0]
    return {
        "stage_id": first_stage.get("id"),
        "module": first_stage.get("module"),
        "out": first_stage.get("out"),
    }


def build_first_downstream_artifact_path(downstream_run_id: str, first_stage_spec: dict | None) -> str | None:
    if not downstream_run_id or not first_stage_spec:
        return None
    module_id = str(first_stage_spec.get("module") or "").strip()
    out_name = str(first_stage_spec.get("out") or "").strip()
    if not module_id or not out_name:
        return None
    artifact_path = Path("output") / "runs" / downstream_run_id / f"01_{module_id}" / out_name
    return str(artifact_path)


def summarize_plan(plan: dict) -> dict:
    return {
        "book_type": plan.get("book_type"),
        "recommended_recipe": plan.get("recommended_recipe"),
        "signals": plan.get("signals", []),
        "signal_evidence_count": len(plan.get("signal_evidence", [])),
    }


def run_intake_steps(case: dict, case_dir: Path) -> tuple[dict, dict]:
    input_path = resolve_input_path(case["path"])
    sheets_dir = case_dir / "contact-sheets"
    manifest = case_dir / "build_contact_sheets.jsonl"
    overview = case_dir / "overview_plan.jsonl"
    zoom = case_dir / "overview_plan_zoom.jsonl"
    gap = case_dir / "overview_plan_gap.jsonl"
    final = case_dir / "overview_plan_final.jsonl"

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
            raise RuntimeError(f"{step_name}: {combined_output[-1200:]}")

    plan = json.loads(final.read_text(encoding="utf-8").splitlines()[0])
    artifacts = {
        "plan_artifact": str(final),
        "handoff_artifact": str(case_dir / "intake_handoff.jsonl"),
    }
    return plan, artifacts


def run_case(case: dict, run_root: Path) -> dict:
    input_path = resolve_input_path(case["path"])
    if not input_path.exists():
        return {
            "id": case["id"],
            "status": "failed",
            "failure_step": "input",
            "error": f"Missing input: {input_path}",
        }

    case_dir = run_root / case["id"]
    case_dir.mkdir(parents=True, exist_ok=True)

    row = {
        "id": case["id"],
        "input_kind": case["input_kind"],
        "path": str(input_path),
        "status": "ok",
        "recommended_recipe": None,
        "plan_artifact": None,
        "handoff_artifact": None,
        "terminal_outcome": None,
        "terminal_reason": None,
        "downstream_run_id": None,
        "first_downstream_stage": None,
        "first_downstream_module": None,
        "first_downstream_artifact": None,
    }

    try:
        plan, artifacts = run_intake_steps(case, case_dir)
    except Exception as exc:
        row["status"] = "failed"
        row["failure_step"] = "intake"
        row["error"] = str(exc)
        return row

    row["plan_artifact"] = artifacts["plan_artifact"]
    row["handoff_artifact"] = artifacts["handoff_artifact"]
    row["plan"] = summarize_plan(plan)
    row["recommended_recipe"] = plan.get("recommended_recipe")

    first_stage_spec = load_first_stage_spec(row["recommended_recipe"])
    if first_stage_spec:
        row["first_downstream_stage"] = first_stage_spec["stage_id"]
        row["first_downstream_module"] = first_stage_spec["module"]

    dispatch_cmd = [
        sys.executable,
        "modules/intake/run_dispatch_v1/main.py",
        "--plan",
        row["plan_artifact"],
        "--out",
        row["handoff_artifact"],
        "--run-id",
        f"{run_root.name}-{case['id']}",
    ]
    if first_stage_spec and first_stage_spec.get("stage_id"):
        dispatch_cmd.extend(["--downstream-end-at", first_stage_spec["stage_id"]])

    result = run_command(dispatch_cmd)
    combined_output = (result.stderr or "") + "\n" + (result.stdout or "")
    if result.returncode != 0:
        row["status"] = "failed"
        row["failure_step"] = "dispatch"
        row["error"] = combined_output[-1200:]
        return row

    handoff_path = Path(row["handoff_artifact"])
    if not handoff_path.exists():
        row["status"] = "failed"
        row["failure_step"] = "handoff_artifact"
        row["error"] = "run_dispatch_v1 completed without writing intake_handoff.jsonl"
        return row

    handoff = json.loads(handoff_path.read_text(encoding="utf-8").splitlines()[0])
    row["terminal_outcome"] = handoff.get("terminal_outcome")
    row["terminal_reason"] = handoff.get("terminal_reason")
    row["downstream_run_id"] = handoff.get("downstream_run_id")
    row["handoff"] = {
        "recommended_recipe": handoff.get("recommended_recipe"),
        "terminal_outcome": handoff.get("terminal_outcome"),
        "terminal_reason": handoff.get("terminal_reason"),
        "launch_input_flag": handoff.get("launch_input_flag"),
        "launch_input_path": handoff.get("launch_input_path"),
        "downstream_run_id": handoff.get("downstream_run_id"),
        "downstream_output_dir": handoff.get("downstream_output_dir"),
        "driver_command": handoff.get("driver_command"),
        "exit_code": handoff.get("exit_code"),
    }

    first_downstream_artifact = build_first_downstream_artifact_path(
        handoff.get("downstream_run_id"),
        first_stage_spec,
    )
    if first_downstream_artifact and Path(first_downstream_artifact).exists():
        row["first_downstream_artifact"] = first_downstream_artifact
    elif first_downstream_artifact:
        row["first_downstream_artifact"] = None
        row["first_downstream_artifact_expected"] = first_downstream_artifact

    row["score"] = score_case(case, row)
    return row


def main():
    parser = argparse.ArgumentParser(description="Run the approved intake handoff benchmark harness")
    parser.add_argument("--corpus", default=str(DEFAULT_CORPUS))
    parser.add_argument("--output", default=None)
    parser.add_argument("--run-root", default=str(ROOT / "output/runs/approved-intake-handoff"))
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
        output_path = ROOT / "benchmarks/results" / f"approved-intake-handoff-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("SUMMARY " + json.dumps(summary))
    print("RESULT_PATH " + str(output_path))


if __name__ == "__main__":
    main()
