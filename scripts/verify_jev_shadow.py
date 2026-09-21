#!/usr/bin/env python3
"""Run the real driver with synthetic inputs and mocked providers; no API calls."""

import json
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/runs/story234-jev-shadow-verification-r2"
MOCKS = ROOT / "tests/fixtures/jev_shadow/mock_provider"
HTML = """<html><body><table><thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr></thead><tbody><tr class="genealogy-subgroup-heading"><th colspan="7">SYNTHETIC FAMILY</th></tr><tr><td>Mira</td><td>1932</td><td>1955</td><td>Leon</td><td>1</td><td>1</td><td>2001</td></tr></tbody></table></body></html>"""


def without_run_metadata(value):
    if isinstance(value, dict):
        return {
            k: without_run_metadata(v)
            for k, v in value.items()
            if k not in {"run_id", "created_at"}
        }
    if isinstance(value, list):
        return [without_run_metadata(v) for v in value]
    return value


def main():
    global OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUT)
    OUT = parser.parse_args().output_dir.resolve()
    if OUT.exists():
        raise SystemExit("Refusing to overwrite previous verification output")
    OUT.mkdir(parents=True)
    chapter = OUT / "chapter-001.html"
    chapter.write_text(HTML)
    chapters = OUT / "chapters.jsonl"
    pages = OUT / "pages.jsonl"
    chapters.write_text(
        json.dumps(
            {
                "kind": "chapter",
                "file": str(chapter),
                "title": "Synthetic",
                "source_pages": [1],
            }
        )
        + "\n"
    )
    pages.write_text(
        json.dumps({"schema_version": "page_html_v1", "page_number": 1, "html": HTML})
        + "\n"
    )
    recipe = OUT / "recipe.json"
    recipe.write_text(
        json.dumps(
            {
                "stages": [
                    {
                        "id": "plan",
                        "stage": "validate",
                        "module": "plan_onward_document_consistency_v1",
                        "out": "report.jsonl",
                        "params": {
                            "chapters": str(chapters),
                            "pages": str(pages),
                            "model": "gpt-4.1",
                        },
                    }
                ]
            }
        )
    )
    modes = ("disabled", "enabled", "failure")
    runs = {}
    for mode in modes:
        # No inherited provider credentials; synthetic sentinel values only.
        env = {k: os.environ[k] for k in ("PATH", "HOME", "TMPDIR") if k in os.environ}
        env.update(
            PYTHONPATH=str(MOCKS) + os.pathsep + str(ROOT),
            OPENAI_API_KEY="offline-sentinel",
        )
        if mode != "disabled":
            env.update(
                DOC_WEB_JEV_SHADOW="enabled",
                DOC_WEB_TYPESAFE_RUNTIME_API_KEY="offline-sentinel",
            )
        if mode == "failure":
            env["DOC_WEB_TEST_SHADOW_FAILURE"] = "yes"
        command = [
            sys.executable,
            str(ROOT / "driver.py"),
            "--recipe",
            str(recipe),
            "--input-html",
            str(chapter),
            "--run-id",
            "story234-" + mode,
            "--output-dir",
            str(OUT / mode),
        ]
        result = subprocess.run(
            command, cwd=ROOT, env=env, text=True, capture_output=True, timeout=60
        )
        (OUT / (mode + ".log")).write_text(result.stdout + result.stderr)
        if result.returncode:
            raise SystemExit(
                f"Offline driver {mode} failed; inspect {OUT / (mode + '.log')}"
            )
        candidates = list((OUT / mode).rglob("conformance_report.json"))
        assert len(candidates) == 1, candidates
        runs[mode] = candidates[0].parent
    for filename in (
        "pattern_inventory.json",
        "consistency_plan.json",
        "conformance_report.json",
    ):
        reference = without_run_metadata(
            json.loads((runs["disabled"] / filename).read_text())
        )
        for mode in modes[1:]:
            assert (
                without_run_metadata(json.loads((runs[mode] / filename).read_text()))
                == reference
            ), (mode, filename)

    def primary_rows(mode):
        path = runs[mode] / "report.jsonl"
        return [
            without_run_metadata(json.loads(line))
            for line in path.read_text().splitlines()
            if line.strip()
        ]

    assert (
        primary_rows("disabled") == primary_rows("enabled") == primary_rows("failure")
    )
    assert not (runs["disabled"] / "jev_consistency_shadow.json").exists()
    enabled = json.loads((runs["enabled"] / "jev_consistency_shadow.json").read_text())
    failed = json.loads((runs["failure"] / "jev_consistency_shadow.json").read_text())
    assert enabled["chapters"][0]["route"] == "review"
    assert enabled["chapters"][0]["shadow_status"] == "uncertain"
    assert failed["chapters"][0]["route"] == "planner_fallback"
    assert failed["unknown_cost_reserved_usd"] > 0
    summary = {
        "provider_calls": 0,
        "modes": list(modes),
        "authoritative_artifacts_invariant": True,
        "paths": {k: str(v) for k, v in runs.items()},
    }
    (OUT / "verification.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
