"""Offline real-driver proof of uncertainty retention and convention conflict guard."""

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.verify_jev_shadow import without_run_metadata  # noqa: E402

BASE = ROOT / "docs/evals/artifacts/story234-anonymized-observation"
OUT = ROOT / "output/runs/story234-evidence-contract-cohort-r5"


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    raw = json.loads((BASE / "run/planner.response.json").read_text())
    payload = OUT / "mock-planner-payload.json"
    payload.write_text(raw["choices"][0]["message"]["content"])
    chapter_manifest = OUT / "chapters.jsonl"
    rows = [json.loads(s) for s in (BASE / "chapters.jsonl").read_text().splitlines()]
    ordered = [rows[i] for i in [3, 5, 0, 1, 2, 4]]
    chapter_manifest.write_text("".join(json.dumps(r) + "\n" for r in ordered))
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
                            "chapters": str(chapter_manifest),
                            "pages": str(BASE / "pages.jsonl"),
                            "model": "gpt-4.1",
                        },
                    }
                ]
            }
        )
    )
    results = {}
    for mode in ["disabled", "enabled"]:
        env = {k: os.environ[k] for k in ["PATH", "HOME", "TMPDIR"] if k in os.environ}
        env.update(
            PYTHONPATH=str(ROOT / "tests/fixtures/jev_shadow/mock_provider")
            + os.pathsep
            + str(ROOT),
            OPENAI_API_KEY="offline-sentinel",
            DOC_WEB_TEST_PLANNER_PAYLOAD_PATH=str(payload),
        )
        if mode == "enabled":
            env.update(
                DOC_WEB_JEV_SHADOW="enabled",
                DOC_WEB_TYPESAFE_RUNTIME_API_KEY="offline-sentinel",
            )
        command = [
            sys.executable,
            str(ROOT / "driver.py"),
            "--recipe",
            str(recipe),
            "--input-html",
            str(BASE / "chapter-001.html"),
            "--run-id",
            "contract-" + mode,
            "--output-dir",
            str(OUT / mode),
        ]
        r = subprocess.run(
            command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=60
        )
        (OUT / (mode + ".log")).write_text(r.stdout + r.stderr)
        assert r.returncode == 0, mode
        stage = next((OUT / mode).rglob("conformance_report.json")).parent
        conformance = json.loads((stage / "conformance_report.json").read_text())
        assert conformance["chapters"][5]["status"] == "uncertain"
        assert conformance["chapters"][5]["issue_types"] == []
        assert "chapter-006.html" in conformance["summary"]["uncertain_chapters"]
        report = [
            json.loads(line)
            for line in (stage / "report.jsonl").read_text().splitlines()
        ]
        assert any(
            issue.get("status") == "uncertain"
            for row in report
            for issue in row["issues"]
        )
        results[mode] = stage
    for name in [
        "pattern_inventory.json",
        "consistency_plan.json",
        "conformance_report.json",
        "report.jsonl",
    ]:

        def read(mode):
            txt = (results[mode] / name).read_text()
            obj = (
                [json.loads(s) for s in txt.splitlines()]
                if name.endswith(".jsonl")
                else json.loads(txt)
            )
            return without_run_metadata(obj)

        assert read("disabled") == read("enabled"), name
    shadow = json.loads(
        (results["enabled"] / "jev_consistency_shadow.json").read_text()
    )
    assert shadow["chapters"][0]["reason"] == "conflicting_conventions"
    assert shadow["chapters"][1]["reason"] == "authoritative_uncertainty"
    assert shadow["chapters"][1]["shadow_status"] == "uncertain"
    # Also inspect the same conflict directly using actual pipeline artifacts.
    sys.path.insert(0, str(ROOT))
    from modules.validate.plan_onward_document_consistency_v1 import main as planner
    from modules.validate.plan_onward_document_consistency_v1 import jev_shadow

    stage = results["enabled"]
    def read(name):
        return json.loads((stage / name).read_text())
    chapters = planner._planner_input_from_dossier(
        read("document_consistency_dossier.json")
    )["chapters"]

    def no_request(*args):
        raise AssertionError("conflicting convention dispatched")

    guarded = jev_shadow.run_shadow(
        [next(c for c in chapters if c["chapter_basename"] == "chapter-004.html")],
        read("consistency_plan.json"),
        read("conformance_report.json"),
        env={
            "DOC_WEB_JEV_SHADOW": "enabled",
            "DOC_WEB_TYPESAFE_RUNTIME_API_KEY": "offline-sentinel",
        },
        request=no_request,
    )
    assert guarded["chapters"][0]["reason"] == "conflicting_conventions"
    (OUT / "guarded-conflict.json").write_text(json.dumps(guarded, indent=2))
    verification = {
        "provider_calls": 0,
        "uncertain_survives_driver_stamping": True,
        "authoritative_outputs_invariant": True,
        "conflicting_convention_calls": guarded["dispatched"],
        "normal_shadow_dispatches": shadow["dispatched"],
        "paths": {k: str(v) for k, v in results.items()},
    }
    (OUT / "verification.json").write_text(json.dumps(verification, indent=2))
    print(json.dumps(verification, indent=2))


if __name__ == "__main__":
    main()
