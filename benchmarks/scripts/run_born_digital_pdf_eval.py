from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.scorers.born_digital_pdf import score_case, summarize_results  # noqa: E402


DEFAULT_CORPUS = ROOT / "benchmarks" / "golden" / "born-digital-pdf" / "corpus.json"
DEFAULT_RUN_ROOT = ROOT / "output" / "runs" / "story196-born-digital-benchmark"


def resolve_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return ROOT / path


def run_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    return subprocess.run(cmd, cwd=ROOT, env=env, text=True, capture_output=True)


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", value).strip("-").lower()


def materialize_case_recipe(case: dict[str, Any], run_root: Path) -> tuple[Path, str | None]:
    recipe_path = resolve_path(case["recipe"])
    if case.get("input_kind") != "pdf":
        return recipe_path, None

    container_name = _slug(f"born-digital-bench-{run_root.name}-{case['id']}")[:63]
    recipe_data = yaml.safe_load(recipe_path.read_text(encoding="utf-8")) or {}
    stage_params = dict(recipe_data.get("stage_params") or {})
    marker_params = dict(stage_params.get("marker_lite_html") or {})
    marker_params["container_name"] = container_name
    stage_params["marker_lite_html"] = marker_params
    recipe_data["stage_params"] = stage_params

    recipe_cache_dir = run_root / "_recipes"
    recipe_cache_dir.mkdir(parents=True, exist_ok=True)
    isolated_recipe = recipe_cache_dir / f"{case['id']}.yaml"
    isolated_recipe.write_text(yaml.safe_dump(recipe_data, sort_keys=False), encoding="utf-8")
    return isolated_recipe, container_name


def cleanup_container(container_name: str | None) -> None:
    if not container_name:
        return
    subprocess.run(
        ["docker", "rm", "-f", container_name],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def load_corpus(path: Path, selected_ids: set[str] | None) -> list[dict[str, Any]]:
    cases = json.loads(path.read_text(encoding="utf-8"))
    if not selected_ids:
        return cases
    return [case for case in cases if case["id"] in selected_ids]


def run_case(case: dict[str, Any], run_root: Path) -> dict[str, Any]:
    input_path = resolve_path(case["path"])
    row: dict[str, Any] = {
        "id": case["id"],
        "classification": case.get("classification"),
        "required": bool(case.get("required", True)),
        "lane": case.get("lane"),
        "input_kind": case.get("input_kind"),
        "path": str(input_path),
        "recipe": case["recipe"],
    }

    if not input_path.exists():
        if case.get("input_optional"):
            row["status"] = "skipped"
            row["failure_step"] = "input_optional"
            row["error"] = f"Optional comparison input missing: {input_path}"
            return row
        row["status"] = "failed"
        row["failure_step"] = "input"
        row["error"] = f"Missing input: {input_path}"
        return row

    run_id = f"{run_root.name}-{case['id']}"
    recipe_path, container_name = materialize_case_recipe(case, run_root)
    cmd = [
        sys.executable,
        "driver.py",
        "--recipe",
        str(recipe_path),
        "--input-pdf",
        str(input_path),
        "--run-id",
        run_id,
        "--allow-run-id-reuse",
        "--force",
    ]

    result = run_command(cmd)
    cleanup_container(container_name)

    row.update(
        {
            "run_id": run_id,
            "recipe_used": str(recipe_path.relative_to(ROOT)) if recipe_path.is_relative_to(ROOT) else str(recipe_path),
            "status": "ok" if result.returncode == 0 else "failed",
            "stdout_tail": "\n".join((result.stdout or "").splitlines()[-20:]),
            "stderr_tail": "\n".join((result.stderr or "").splitlines()[-20:]),
        }
    )
    if result.returncode != 0:
        row["failure_step"] = "driver"
        row["error"] = ((result.stderr or "") + "\n" + (result.stdout or "")).strip()[-2000:]
        return row

    run_dir = ROOT / "output" / "runs" / run_id
    row["bundle_dir"] = str(run_dir / "output" / "html")
    row["score"] = score_case(case, run_dir)
    return row


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the maintained born-digital PDF benchmark on the repo-owned supported slice plus optional comparison cases."
    )
    parser.add_argument("--corpus", default=str(DEFAULT_CORPUS))
    parser.add_argument("--output", default=None)
    parser.add_argument("--run-root", default=str(DEFAULT_RUN_ROOT))
    parser.add_argument("--case-id", action="append", default=None, help="Limit to one or more corpus case ids")
    args = parser.parse_args()

    corpus_path = resolve_path(args.corpus)
    run_root = resolve_path(args.run_root)
    run_root.mkdir(parents=True, exist_ok=True)
    selected_ids = set(args.case_id or [])
    cases = load_corpus(corpus_path, selected_ids)

    results = [run_case(case, run_root) for case in cases]
    summary = summarize_results(results)

    payload = {
        "measured_at": datetime.now().astimezone().date().isoformat(),
        "classification": "quality benchmark with supported slice plus optional comparison-only cases",
        "corpus": str(corpus_path.relative_to(ROOT)) if corpus_path.is_relative_to(ROOT) else str(corpus_path),
        "run_root": str(run_root.relative_to(ROOT)) if run_root.is_relative_to(ROOT) else str(run_root),
        "rows": results,
        "summary": summary,
    }

    if args.output:
        output_path = resolve_path(args.output)
    else:
        stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
        output_path = ROOT / "benchmarks" / "results" / f"born-digital-pdf-{stamp}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("SUMMARY " + json.dumps(summary, sort_keys=True))
    print("RESULT_PATH " + str(output_path))


if __name__ == "__main__":
    main()
