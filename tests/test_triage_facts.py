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


def test_graph_facts_preserves_compiler_recommendations_and_score_dates():
    module = load_module()
    module.TODAY = module.date(2026, 10, 23)
    graph = json.loads((ROOT / "docs/methodology/graph.json").read_text())

    facts = module.graph_facts(graph)

    for source, result in (
        (graph["stories"], facts["stories"]),
        (graph["evals"], facts["evals"]),
        (graph["spec"]["compromises"], facts["compromises"]),
    ):
        expected = {
            item["id"]: item["actionability"]["why_now"]
            for item in source
            if (item.get("actionability") or {}).get("recommended_now")
        }
        assert {
            row["id"]: row["why_now"] for row in result["recommended_now"]
        } == expected
    expected_stale = {
        item["id"]: (item.get("latest_score") or {}).get("measured")
        for item in graph["evals"]
        if not (item.get("latest_score") or {}).get("measured")
        or module.days_since(item["latest_score"]["measured"]) > 30
    }
    assert {
        row["id"]: row["measured"] for row in facts["evals"]["stale_scores"]
    } == dict(list(expected_stale.items())[:20])


def test_graph_facts_reports_retry_posture_without_inventing_readiness():
    module = load_module()
    facts = module.graph_facts(
        {
            "evals": [
                {
                    "id": "waiting",
                    "actionability": {
                        "recommended_now": True,
                        "why_now": "Changed workflow requires measurement",
                        "retry_trigger_status": "waiting",
                        "retry_when": ["workflow-change"],
                    },
                },
                {
                    "id": "exhausted",
                    "actionability": {"retry_trigger_status": "exhausted"},
                },
                {"id": "unknown"},
            ],
        }
    )

    assert facts["evals"]["recommended_now"] == [
        {
            "id": "waiting",
            "name": None,
            "posture": None,
            "why_now": "Changed workflow requires measurement",
            "retry_trigger_status": "waiting",
        }
    ]
    assert facts["evals"]["by_retry_trigger_status"] == {
        "waiting": 1,
        "exhausted": 1,
        "unavailable": 1,
    }
    assert "retry_ready" not in facts["evals"]


def test_graph_facts_distinguishes_recent_stale_and_unavailable_scores():
    module = load_module()
    module.TODAY = module.date(2026, 10, 23)
    facts = module.graph_facts(
        {
            "evals": [
                {"id": "recent", "latest_score": {"measured": "2026-10-06"}},
                {"id": "stale", "latest_score": {"measured": "2026-09-01"}},
                {"id": "missing"},
            ]
        }
    )

    assert facts["evals"]["stale_scores"] == [
        {"id": "stale", "measured": "2026-09-01", "days_since": 52},
        {"id": "missing", "measured": None, "days_since": None},
    ]
