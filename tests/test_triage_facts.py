from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "scripts" / "triage_facts.py"
    spec = importlib.util.spec_from_file_location("triage_facts", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_collect_facts_core_doc_web_lanes(monkeypatch):
    monkeypatch.setenv("TRIAGE_FACTS_TODAY", "2026-04-26")
    module = load_module()
    module.TODAY = module.date.fromisoformat(os.environ["TRIAGE_FACTS_TODAY"])
    expected_lanes = {
        "triage-stories",
        "triage-inbox",
        "triage-evals",
        "triage-architecture",
        "triage-health",
        "codebase-improvement-scout",
        "discover-models",
        "loop-verify",
    }

    facts = module.collect_facts()

    assert facts["repo"] == "doc-web"
    assert set(module.LANE_SKILLS) == expected_lanes
    assert set(facts["lanes"]) == expected_lanes
    assert all(status == "present" for status in facts["lanes"].values())
    assert facts["coverage"]["path"] == "tests/fixtures/formats/_coverage-matrix.json"
    assert facts["coverage"]["total_formats"] > 0
    assert "passing" in facts["coverage"]["by_status"]
    assert facts["architecture"]["status"] == "present"
    assert facts["methodology_tooling"]["command_alias_status"] == "absent"
    assert facts["methodology_tooling"]["missing_command_aliases"] == []
    assert facts["methodology_tooling"]["extra_command_aliases"] == []


def test_cli_json_is_parseable():
    completed = subprocess.run(
        [sys.executable, "scripts/triage_facts.py", "--json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        encoding="utf-8",
    )

    parsed = json.loads(completed.stdout)
    assert parsed["repo"] == "doc-web"
    assert parsed["coverage"]["total_formats"] > 0
