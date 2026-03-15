import json
import sys
from pathlib import Path

from modules.validate.plan_onward_document_consistency_v1.main import (
    _row_semantic_note_reason,
    build_document_dossier,
    build_outputs,
    call_planning_model,
    main,
)


FRAGMENTED_HTML = """
<html><body>
  <table>
    <thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr></thead>
    <tbody><tr class="genealogy-subgroup-heading"><th colspan="7">ARTHUR'S FAMILY</th></tr></tbody>
  </table>
  <table>
    <thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr></thead>
    <tbody><tr class="genealogy-subgroup-heading"><th colspan="7">BERNICE'S FAMILY</th></tr></tbody>
  </table>
  <table><tbody><tr><th>TOTAL DESCENDANTS</th><td>10</td></tr></tbody></table>
</body></html>
"""

CONCATENATED_HTML = """
<html><body>
  <table>
    <thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr></thead>
    <tbody>
      <tr class="genealogy-subgroup-heading"><th colspan="7">Leonidas’ Great Great Grandchildren Alma’s Great Grandchildren Dolly’s Grandchildren SHARON’S FAMILY</th></tr>
      <tr><td>Alice</td><td></td><td></td><td></td><td>1</td><td>0</td><td></td></tr>
    </tbody>
  </table>
  <table><tbody><tr><th>TOTAL DESCENDANTS</th><td>20</td></tr></tbody></table>
</body></html>
"""

LEFT_COLUMN_BOYGIRL_HTML = """
<html><body>
  <table>
    <thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY/GIRL</th><th>DIED</th></tr></thead>
    <tbody>
      <tr><td>MATHILDA’S FAMILY</td></tr>
      <tr><td>Mathilda</td><td></td><td></td><td></td><td>1/1</td><td></td></tr>
    </tbody>
  </table>
  <table><tbody><tr><th>TOTAL DESCENDANTS</th><td>8</td></tr></tbody></table>
</body></html>
"""

ROW_SEMANTIC_HTML = """
<html><body>
  <table>
    <thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr></thead>
    <tbody>
      <tr><td>ALMA’S FAMILY</td></tr>
      <tr><td>Lana</td><td>May 16, 1968</td><td>Dave Berry</td><td></td><td>2 Boys Kevin Kristopher</td><td></td><td>1-Kassandra</td></tr>
      <tr><td>Michelle</td><td>Jan. 12, 1962</td><td>Gordon Frank</td><td></td><td></td><td></td><td>May 15 Chelsea was born to Michelle & McDonald</td></tr>
    </tbody>
  </table>
  <table><tbody><tr><th>TOTAL DESCENDANTS</th><td>30</td></tr></tbody></table>
</body></html>
"""

CLEAN_HTML = """
<html><body>
  <table>
    <thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr></thead>
    <tbody>
      <tr><td>Antoine</td><td>Apr. 13, 1903</td><td>Oct. 1, 1925</td><td>Delima Nolin</td><td>3</td><td>3</td><td>Aug. 16, 1983</td></tr>
      <tr class="genealogy-subgroup-heading"><th colspan="7">ANTOINE’S FAMILY</th></tr>
      <tr><td>Onil</td><td>June 14, 1926</td><td>Mar. 20, 1950</td><td>Dorothy Grist</td><td>0</td><td>2</td><td></td></tr>
    </tbody>
  </table>
  <table><tbody><tr><th>TOTAL DESCENDANTS</th><td>38</td></tr><tr><th>LIVING</th><td>36</td></tr><tr><th>DECEASED</th><td>2</td></tr></tbody></table>
</body></html>
"""


def _write_fixture_files(tmp_path: Path):
    chapter_dir = tmp_path / "output" / "html"
    chapter_dir.mkdir(parents=True, exist_ok=True)

    chapter_paths = {
        "chapter-010.html": chapter_dir / "chapter-010.html",
        "chapter-011.html": chapter_dir / "chapter-011.html",
        "chapter-016.html": chapter_dir / "chapter-016.html",
        "chapter-009.html": chapter_dir / "chapter-009.html",
        "chapter-023.html": chapter_dir / "chapter-023.html",
    }
    chapter_paths["chapter-010.html"].write_text(FRAGMENTED_HTML, encoding="utf-8")
    chapter_paths["chapter-011.html"].write_text(CONCATENATED_HTML, encoding="utf-8")
    chapter_paths["chapter-016.html"].write_text(LEFT_COLUMN_BOYGIRL_HTML, encoding="utf-8")
    chapter_paths["chapter-009.html"].write_text(ROW_SEMANTIC_HTML, encoding="utf-8")
    chapter_paths["chapter-023.html"].write_text(CLEAN_HTML, encoding="utf-8")

    manifest_rows = [
        {
            "kind": "chapter",
            "title": "Arthur",
            "file": str(chapter_paths["chapter-010.html"]),
            "source_pages": [30, 31],
            "source_printed_pages": [21, 22],
        },
        {
            "kind": "chapter",
            "title": "Leonidas",
            "file": str(chapter_paths["chapter-011.html"]),
            "source_pages": [32],
            "source_printed_pages": [23],
        },
        {
            "kind": "chapter",
            "title": "Mathilda",
            "file": str(chapter_paths["chapter-016.html"]),
            "source_pages": [56],
            "source_printed_pages": [47],
        },
        {
            "kind": "chapter",
            "title": "Alma",
            "file": str(chapter_paths["chapter-009.html"]),
            "source_pages": [24],
            "source_printed_pages": [15],
        },
        {
            "kind": "chapter",
            "title": "Antoine L'Heureux",
            "file": str(chapter_paths["chapter-023.html"]),
            "source_pages": [117],
            "source_printed_pages": [108],
        },
    ]

    pages = [
        {"schema_version": "page_html_v1", "page_number": 30, "printed_page_number": 21, "html": FRAGMENTED_HTML},
        {"schema_version": "page_html_v1", "page_number": 31, "printed_page_number": 22, "html": FRAGMENTED_HTML},
        {"schema_version": "page_html_v1", "page_number": 32, "printed_page_number": 23, "html": CONCATENATED_HTML},
        {"schema_version": "page_html_v1", "page_number": 56, "printed_page_number": 47, "html": LEFT_COLUMN_BOYGIRL_HTML},
        {"schema_version": "page_html_v1", "page_number": 24, "printed_page_number": 15, "html": ROW_SEMANTIC_HTML},
        {"schema_version": "page_html_v1", "page_number": 117, "printed_page_number": 108, "html": CLEAN_HTML},
    ]

    manifest_path = tmp_path / "chapters_manifest.jsonl"
    pages_path = tmp_path / "pages.jsonl"
    with manifest_path.open("w", encoding="utf-8") as handle:
        for row in manifest_rows:
            handle.write(json.dumps(row) + "\n")
    with pages_path.open("w", encoding="utf-8") as handle:
        for row in pages:
            handle.write(json.dumps(row) + "\n")
    return manifest_rows, {row["page_number"]: row for row in pages}, manifest_path, pages_path


def test_build_document_dossier_detects_main_failure_classes(tmp_path: Path):
    manifest_rows, pages_by_number, manifest_path, pages_path = _write_fixture_files(tmp_path)

    dossier = build_document_dossier(
        manifest_rows,
        pages_by_number,
        chapters_path=str(manifest_path),
        pages_path=str(pages_path),
        flag_threshold=25,
    )

    chapters = {chapter["chapter_basename"]: chapter for chapter in dossier["chapter_profiles"]}
    assert "fragmented_multi_table_chapter" in chapters["chapter-010.html"]["signals"]["suggested_issue_types"]
    assert "concatenated_subgroup_context_rows" in chapters["chapter-011.html"]["signals"]["suggested_issue_types"]
    assert "fused_boygirl_headers" in chapters["chapter-016.html"]["signals"]["suggested_issue_types"]
    assert "left_column_only_family_rows" in chapters["chapter-016.html"]["signals"]["suggested_issue_types"]
    assert "child_note_in_wrong_column" in chapters["chapter-009.html"]["signals"]["suggested_issue_types"]
    assert "chapter-009.html" in dossier["baseline"]["current_detector_unflagged_watchlist"]


def test_build_outputs_distinguishes_format_vs_row_semantic(tmp_path: Path):
    manifest_rows, pages_by_number, manifest_path, pages_path = _write_fixture_files(tmp_path)
    dossier = build_document_dossier(
        manifest_rows,
        pages_by_number,
        chapters_path=str(manifest_path),
        pages_path=str(pages_path),
        flag_threshold=25,
    )
    planner_payload = {
        "analysis_summary": {
            "document_scope": "Onward genealogy",
            "default_note_policy": "Represent marginal child notes consistently as note/children content, not as DIED values.",
            "default_note_policy_rationale": "The document uses margin-like child notes that should not corrupt death data.",
            "overall_confidence": 0.88,
        },
        "pattern_families": [
            {
                "pattern_id": "pattern_main",
                "label": "Canonical seven-column genealogy tables",
                "description": "Main family genealogy tables with optional summary totals.",
                "member_chapters": [
                    "chapter-009.html",
                    "chapter-010.html",
                    "chapter-011.html",
                    "chapter-016.html",
                    "chapter-023.html",
                ],
                "baseline_chapters": ["chapter-023.html"],
                "canonical_signals": ["Single main seven-column genealogy table", "Optional separate totals table"],
                "canonical_headers": ["NAME", "BORN", "MARRIED", "SPOUSE", "BOY", "GIRL", "DIED"],
                "allowed_variants": ["Separate totals table"],
                "document_local_conventions": {
                    "subgroup_context_rows": "Use full-width subgroup/context rows inside the table.",
                    "table_fragmentation": "Avoid repeated full-header tables unless the source clearly restarts a new run.",
                    "summary_rows": "Allow a separate totals table at chapter end.",
                    "marginal_or_handwritten_notes": "Attach marginal child-note content to the row/children representation rather than the DIED column.",
                },
                "confidence": 0.9,
                "evidence": [{"chapter_basename": "chapter-011.html", "page_numbers": [32], "quote": "Leonidas’ Great Great Grandchildren Alma’s Great Grandchildren Dolly’s Grandchildren SHARON’S FAMILY"}],
            }
        ],
        "chapter_findings": [
            {
                "chapter_basename": "chapter-010.html",
                "pattern_id": "pattern_main",
                "status": "format_drift",
                "issue_types": ["fragmented_multi_table_chapter"],
                "why": "The chapter uses multiple repeated full-header tables before the totals table.",
                "relevant_pages": [30, 31],
                "repair_priority": "high",
                "evidence": [{"chapter_basename": "chapter-010.html", "page_number": 30, "quote": "ARTHUR'S FAMILY"}],
            },
            {
                "chapter_basename": "chapter-011.html",
                "pattern_id": "pattern_main",
                "status": "format_drift",
                "issue_types": ["concatenated_subgroup_context_rows"],
                "why": "Multiple subgroup/context labels are fused into one subgroup row.",
                "relevant_pages": [32],
                "repair_priority": "high",
                "evidence": [{"chapter_basename": "chapter-011.html", "page_number": 32, "quote": "Leonidas’ Great Great Grandchildren Alma’s Great Grandchildren Dolly’s Grandchildren SHARON’S FAMILY"}],
            },
            {
                "chapter_basename": "chapter-016.html",
                "pattern_id": "pattern_main",
                "status": "format_drift",
                "issue_types": ["fused_boygirl_headers", "left_column_only_family_rows"],
                "why": "The header collapses BOY/GIRL and family rows sit in the left column only.",
                "relevant_pages": [56],
                "repair_priority": "high",
                "evidence": [{"chapter_basename": "chapter-016.html", "page_number": 56, "quote": "MATHILDA’S FAMILY"}],
            },
            {
                "chapter_basename": "chapter-009.html",
                "pattern_id": "pattern_main",
                "status": "mixed",
                "issue_types": ["left_column_only_family_rows", "child_note_in_wrong_column"],
                "why": "The chapter has both malformed heading rows and child-note content in the DIED column.",
                "relevant_pages": [24],
                "repair_priority": "medium",
                "evidence": [{"chapter_basename": "chapter-009.html", "page_number": 24, "quote": "May 15 Chelsea was born to Michelle & McDonald"}],
            },
            {
                "chapter_basename": "chapter-023.html",
                "pattern_id": "pattern_main",
                "status": "format_drift",
                "issue_types": ["fused_boygirl_headers", "left_column_only_family_rows"],
                "why": "Hallucinated issue types should be discarded because the dossier shows a clean canonical table.",
                "relevant_pages": [117],
                "repair_priority": "low",
                "evidence": [{"chapter_basename": "chapter-023.html", "page_number": 117, "quote": "clean canonical table"}],
            },
        ],
    }

    primary_report, pattern_inventory, consistency_plan, conformance_report = build_outputs(
        dossier,
        planner_payload,
        chapters_path=str(manifest_path),
        pages_path=str(pages_path),
        run_id="story144-test",
    )

    assert primary_report["summary"]["newly_surfaced_format_drift_chapters"] == [
        "chapter-010.html",
        "chapter-011.html",
    ]
    assert primary_report["summary"]["format_drift_chapters"] == [
        "chapter-010.html",
        "chapter-011.html",
        "chapter-016.html",
    ]
    assert primary_report["summary"]["row_semantic_issue_chapters"] == []
    assert primary_report["summary"]["mixed_issue_chapters"] == ["chapter-009.html"]
    assert primary_report["summary"]["newly_surfaced_mixed_issue_chapters"] == ["chapter-009.html"]
    assert pattern_inventory["summary"]["pattern_family_count"] == 1
    assert "marginal child notes" in consistency_plan["summary"]["default_note_policy"]
    chapter_009 = next(chapter for chapter in conformance_report["chapters"] if chapter["chapter_basename"] == "chapter-009.html")
    assert chapter_009["status"] == "mixed"
    assert chapter_009["surfaced_new_vs_current_detector"] is True
    chapter_023 = next(chapter for chapter in conformance_report["chapters"] if chapter["chapter_basename"] == "chapter-023.html")
    assert chapter_023["status"] == "conformant"
    assert chapter_023["issue_types"] == []
    assert chapter_023["surfaced_new_vs_current_detector"] is False


def test_row_semantic_signal_ignores_plain_death_dates():
    assert _row_semantic_note_reason(["Alice", "", "", "", "", "", "Apr. 1, 1964"]) is None
    assert _row_semantic_note_reason(["Bob", "", "", "", "", "", "Deceased"]) is None
    assert _row_semantic_note_reason(["Lana", "", "", "", "", "", "1-Kassandra"]) == "child_note_in_wrong_column"
    assert (
        _row_semantic_note_reason(
            ["Michelle", "", "", "", "", "", "May 15 Chelsea was born to Michelle & McDonald"]
        )
        == "child_note_in_wrong_column"
    )


def test_call_planning_model_retries_with_stable_json_model():
    class FakeResponses:
        def create(self, **kwargs):
            class Response:
                output_text = ""
                output = []
                id = "resp_fake"
                status = "completed"
                incomplete_details = {"reason": "max_output_tokens"}
                error = None

            return Response()

    class FakeChatCompletions:
        def create(self, **kwargs):
            class Message:
                content = '{"analysis_summary": {}, "pattern_families": [], "chapter_findings": []}'
                refusal = None

            class Choice:
                message = Message()
                finish_reason = "stop"

            class Completion:
                choices = [Choice()]

            return Completion()

    class FakeChat:
        def __init__(self):
            self.completions = FakeChatCompletions()

    class FakeClient:
        def __init__(self):
            self.responses = FakeResponses()
            self.chat = FakeChat()

    payload = call_planning_model(
        FakeClient(),
        model="gpt-5",
        retry_model="gpt-4.1",
        dossier={"schema_version": "x", "created_at": "now", "document_label": "doc", "baseline": {}, "chapter_profiles": []},
        max_completion_tokens=100,
        timeout=5.0,
    )

    assert payload == {"analysis_summary": {}, "pattern_families": [], "chapter_findings": []}


def test_cli_smoke_writes_sidecar_artifacts(tmp_path: Path, monkeypatch):
    _, _, manifest_path, pages_path = _write_fixture_files(tmp_path)
    out_path = tmp_path / "document_consistency_report.jsonl"
    dossier_path = tmp_path / "document_consistency_dossier.json"
    pattern_inventory_path = tmp_path / "pattern_inventory.json"
    consistency_plan_path = tmp_path / "consistency_plan.json"
    conformance_report_path = tmp_path / "conformance_report.json"

    planner_payload = {
        "analysis_summary": {
            "document_scope": "Onward genealogy",
            "default_note_policy": "Keep marginal child-note content out of DIED unless the source explicitly marks a death.",
            "default_note_policy_rationale": "Consistency should not corrupt row meaning.",
            "overall_confidence": 0.82,
        },
        "pattern_families": [
            {
                "pattern_id": "pattern_main",
                "label": "Main genealogy tables",
                "description": "Seven-column genealogy tables with subgroup rows.",
                "member_chapters": ["chapter-009.html", "chapter-010.html", "chapter-011.html", "chapter-016.html"],
                "baseline_chapters": ["chapter-009.html"],
                "canonical_signals": ["Seven-column genealogy table"],
                "canonical_headers": ["NAME", "BORN", "MARRIED", "SPOUSE", "BOY", "GIRL", "DIED"],
                "allowed_variants": ["Separate totals table"],
                "document_local_conventions": {
                    "subgroup_context_rows": "Use full-width subgroup/context rows.",
                    "table_fragmentation": "Minimize repeated full-header tables.",
                    "summary_rows": "Keep totals at chapter end.",
                    "marginal_or_handwritten_notes": "Treat marginal child-note content as note/children information.",
                },
                "confidence": 0.85,
                "evidence": [],
            }
        ],
        "chapter_findings": [
            {
                "chapter_basename": "chapter-010.html",
                "pattern_id": "pattern_main",
                "status": "format_drift",
                "issue_types": ["fragmented_multi_table_chapter"],
                "why": "Repeated full-header tables suggest fragmentation.",
                "relevant_pages": [30, 31],
                "repair_priority": "high",
                "evidence": [],
            },
            {
                "chapter_basename": "chapter-009.html",
                "pattern_id": "pattern_main",
                "status": "row_semantic_issue",
                "issue_types": ["child_note_in_wrong_column"],
                "why": "Child notes sit in DIED.",
                "relevant_pages": [24],
                "repair_priority": "medium",
                "evidence": [],
            },
        ],
    }

    monkeypatch.setattr(
        "modules.validate.plan_onward_document_consistency_v1.main.OpenAI",
        lambda: object(),
    )
    monkeypatch.setattr(
        "modules.validate.plan_onward_document_consistency_v1.main.call_planning_model",
        lambda *args, **kwargs: planner_payload,
    )

    old_argv = sys.argv
    sys.argv = [
        "plan_onward_document_consistency_v1",
        "--chapters",
        str(manifest_path),
        "--pages",
        str(pages_path),
        "--out",
        str(out_path),
        "--dossier-report",
        str(dossier_path),
        "--pattern-inventory",
        str(pattern_inventory_path),
        "--consistency-plan",
        str(consistency_plan_path),
        "--conformance-report",
        str(conformance_report_path),
        "--run-id",
        "story144-test",
    ]
    try:
        main()
    finally:
        sys.argv = old_argv

    summary_rows = [json.loads(line) for line in out_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    dossier = json.loads(dossier_path.read_text(encoding="utf-8"))
    pattern_inventory = json.loads(pattern_inventory_path.read_text(encoding="utf-8"))
    conformance_report = json.loads(conformance_report_path.read_text(encoding="utf-8"))

    assert summary_rows[0]["schema_version"] == "pipeline_issues_v1"
    assert dossier["schema_version"] == "onward_document_consistency_dossier_v1"
    assert pattern_inventory["schema_version"] == "document_pattern_inventory_v1"
    assert conformance_report["summary"]["row_semantic_issue_chapters"] == ["chapter-009.html"]
    assert conformance_report["summary"]["mixed_issue_chapters"] == []
