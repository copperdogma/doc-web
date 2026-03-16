import json
import sys
from pathlib import Path
from types import SimpleNamespace

from bs4 import BeautifulSoup

from modules.adapter.rerun_onward_genealogy_consistency_v1.main import (
    _best_effort_normalize_html,
    _page_drift_gate,
    _retention_gate,
    RerunTarget,
    UnresolvedChapter,
    build_user_text,
    load_targets,
    run_reruns,
)


HEADER = (
    "<tr>"
    "<th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th>"
    "<th>BOY</th><th>GIRL</th><th>DIED</th>"
    "</tr>"
)

EXISTING_BAD_HTML = """
<h2>LAWRENCE'S FAMILY</h2>
<p>Alice Jan. 1, 1970</p>
<p>TOTAL DESCENDANTS 2</p>
<p>LIVING 2</p>
"""

ACCEPTED_CANDIDATE_HTML = f"""
<table>
  <thead>{HEADER}</thead>
  <tbody>
    <tr class="genealogy-subgroup-heading"><th colspan="7">LAWRENCE'S FAMILY</th></tr>
    <tr><td>Alice</td><td>Jan. 1, 1970</td><td></td><td></td><td>1</td><td>1</td><td></td></tr>
  </tbody>
</table>
<table>
  <tr><td>TOTAL DESCENDANTS</td><td>2</td></tr>
  <tr><td>LIVING</td><td>2</td></tr>
</table>
"""

LOW_RETENTION_CANDIDATE_HTML = f"""
<table>
  <thead>{HEADER}</thead>
  <tbody>
    <tr><td>Alice</td><td>Jan. 1, 1970</td><td></td><td></td><td>1</td><td>1</td><td></td></tr>
  </tbody>
</table>
"""

MIXED_CONTEXT_EXISTING_HTML = """
<h2>Arthur's Great Grandchildren<br/>Agnes' Grandchildren<br/>LAWRENCE'S FAMILY</h2>
<table><tbody><tr><td>Rene</td><td>Jan. 25, 1972</td></tr></tbody></table>
"""

SPLIT_CONTEXT_CANDIDATE_HTML = f"""
<h2>Arthur's Great Grandchildren<br/>Agnes' Grandchildren</h2>
<table>
  <thead>{HEADER}</thead>
  <tbody>
    <tr class="genealogy-subgroup-heading"><th colspan="7">LAWRENCE'S FAMILY</th></tr>
    <tr><td>Rene</td><td>Jan. 25, 1972</td><td></td><td></td><td></td><td></td><td></td></tr>
  </tbody>
</table>
"""

NORMALIZE_ONLY_EXISTING_HTML = """
<h1>Joe L'Heureux</h1>
<table>
  <thead>
    <tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY/GIRL</th><th>DIED</th></tr>
  </thead>
  <tbody>
    <tr><td>Joe</td><td>May 23, 1892</td><td>Oct. 6, 1914</td><td>Eva Carriere</td><td>2 5</td><td>May 21, 1985</td></tr>
    <tr><td><strong>JOE'S FAMILY</strong></td></tr>
    <tr><td>Fernand</td><td>July 3, 1915</td><td>Oct. 20, 1938</td><td>Corrine Regnier</td><td>1 1</td><td></td></tr>
    <tr><td>Ernest</td><td>Oct. 15, 1916</td><td>Oct. 28, 1940</td><td>Corrine Comeau</td><td>5 2</td><td></td></tr>
    <tr><td><strong>Joe's Grandchildren<br/>FERNAND'S FAMILY</strong></td></tr>
    <tr><td>Fernande</td><td>Nov. 12, 1939</td><td>June 8, 1961</td><td>Ray Swistun</td><td>1 2</td><td></td></tr>
  </tbody>
</table>
"""

NAME_LIST_EXISTING_HTML = f"""
<h1>Arthur's Grandchildren</h1>
<table>
  <thead>{HEADER}</thead>
  <tbody>
    <tr><td>Noel</td><td>Jan. 1, 1940</td><td></td><td></td><td>2</td><td>1</td><td></td></tr>
  </tbody>
</table>
<h2>ULRIC'S FAMILY</h2>
<p>Claire<br/>Duffy<br/>Robin</p>
<h2>RENE'S FAMILY</h2>
<table>
  <tbody>
    <tr><td>Barbara Jean</td><td>Sept. 28, 1949</td></tr>
  </tbody>
</table>
"""

EMBEDDED_FAMILY_HEADER_HTML = """
<table>
  <thead>
    <tr>
      <th>NAME</th><th>BORN</th><th colspan="2">SANDRA'S FAMILY</th><th>BOY/GIRL</th><th>DIED</th>
    </tr>
    <tr>
      <th></th><th></th><th>MARRIED</th><th>SPOUSE</th><th></th><th></th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Ryan</td><td>Aug. 21, 1982</td><td></td><td></td><td></td><td></td></tr>
    <tr><td>Frances</td><td>Nov. 9, 1956</td><td>, 1978</td><td>Mark Girard</td><td>0 2</td><td></td></tr>
  </tbody>
</table>
"""


def _write_jsonl(path: Path, rows):
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def _fixture_rows(tmp_path: Path):
    image_34 = tmp_path / "34.jpg"
    image_35 = tmp_path / "35.jpg"
    image_40 = tmp_path / "40.jpg"
    image_34.write_bytes(b"fake-image-34")
    image_35.write_bytes(b"fake-image-35")
    image_40.write_bytes(b"fake-image-40")

    rows = [
        {
            "schema_version": "page_html_v1",
            "page": 34,
            "page_number": 34,
            "image": str(image_34),
            "printed_page_number": 25,
            "html": EXISTING_BAD_HTML,
        },
        {
            "schema_version": "page_html_v1",
            "page": 35,
            "page_number": 35,
            "image": str(image_35),
            "printed_page_number": 26,
            "html": "<table><tr><td>Neighbor context</td></tr></table>",
        },
        {
            "schema_version": "page_html_v1",
            "page": 40,
            "page_number": 40,
            "image": str(image_40),
            "printed_page_number": 31,
            "html": "<p>Untouched page</p>",
        },
    ]
    page_map = {row["page_number"]: row for row in rows}
    return rows, page_map


def _fixture_report(tmp_path: Path) -> Path:
    report_path = tmp_path / "consistency.jsonl"
    _write_jsonl(
        report_path,
        [
            {
                "schema_version": "pipeline_issues_v1",
                "module_id": "validate_onward_genealogy_consistency_v1",
                "summary": {},
                "issues": [
                    {
                        "type": "onward_genealogy_consistency_drift",
                        "chapter_basename": "chapter-010.html",
                        "chapter_title": "Genealogy",
                        "schema_hint": "name|born|married|spouse|boy|girl|died",
                        "reasons": ["external_family_headings"],
                        "source_pages": [33, 34, 35],
                        "coarse_suspect_pages": [34, 35],
                        "strong_rerun_candidate_pages": [34],
                    }
                ],
            }
        ],
    )
    return report_path


def _fixture_planner_pages(tmp_path: Path) -> Path:
    rows = []
    for page_number, html in [
        (54, "<p>Lead-in prose</p>"),
        (55, "<p>Still prose</p>"),
        (56, "<table><tr><td>Cluster A</td></tr></table>"),
        (57, "<table><tr><td>Cluster B1</td></tr></table><table><tr><td>Cluster B2</td></tr></table>"),
        (58, "<p>Trailing prose</p>"),
        (59, "<p>More prose</p>"),
    ]:
        image_path = tmp_path / f"{page_number}.jpg"
        image_path.write_bytes(f"fake-image-{page_number}".encode("utf-8"))
        rows.append(
            {
                "schema_version": "page_html_v1",
                "page": page_number,
                "page_number": page_number,
                "printed_page_number": page_number - 9,
                "image": str(image_path),
                "html": html,
            }
        )
    pages_path = tmp_path / "planner_pages.jsonl"
    _write_jsonl(pages_path, rows)
    return pages_path


def _fixture_planner_artifacts(tmp_path: Path, *, relevant_pages, source_pages) -> Path:
    report_path = tmp_path / "document_consistency_report.jsonl"
    pattern_inventory_path = tmp_path / "pattern_inventory.json"
    consistency_plan_path = tmp_path / "consistency_plan.json"
    conformance_report_path = tmp_path / "conformance_report.json"

    _write_jsonl(
        report_path,
        [
            {
                "schema_version": "pipeline_issues_v1",
                "module_id": "plan_onward_document_consistency_v1",
                "summary": {},
                "issues": [
                    {
                        "type": "document_consistency_planning_issue",
                        "chapter_basename": "chapter-013.html",
                        "chapter_title": "Frank's Family",
                        "status": "format_drift",
                        "pattern_id": "pattern_1",
                        "issue_types": ["fragmented_multi_table_chapter"],
                        "relevant_pages": list(relevant_pages),
                        "surfaced_new_vs_current_detector": True,
                        "evidence": [],
                    }
                ],
            }
        ],
    )
    pattern_inventory_path.write_text(
        json.dumps(
            {
                "schema_version": "document_pattern_inventory_v1",
                "pattern_families": [
                    {
                        "pattern_id": "pattern_1",
                        "label": "Main genealogy tables",
                        "description": "Seven-column tables with subgroup rows.",
                        "baseline_chapters": ["chapter-009.html"],
                        "canonical_headers": ["NAME", "BORN", "MARRIED", "SPOUSE", "BOY", "GIRL", "DIED"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    consistency_plan_path.write_text(
        json.dumps(
            {
                "schema_version": "document_consistency_plan_v1",
                "pattern_conventions": [
                    {
                        "pattern_id": "pattern_1",
                        "label": "Main genealogy tables",
                        "canonical_headers": ["NAME", "BORN", "MARRIED", "SPOUSE", "BOY", "GIRL", "DIED"],
                        "canonical_signals": ["single continuous genealogy table"],
                        "allowed_variants": ["separate totals table"],
                        "document_local_conventions": {
                            "subgroup_context_rows": "Use full-width subgroup rows.",
                            "table_fragmentation": "Prefer one continuous table per chapter whenever the scan supports it.",
                            "summary_rows": "Keep totals after the genealogy table.",
                            "marginal_or_handwritten_notes": "Keep notes out of DIED unless the source marks a death.",
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    conformance_report_path.write_text(
        json.dumps(
            {
                "schema_version": "document_conformance_report_v1",
                "summary": {},
                "chapters": [
                    {
                        "chapter_basename": "chapter-013.html",
                        "chapter_title": "Frank's Family",
                        "pattern_id": "pattern_1",
                        "status": "format_drift",
                        "issue_types": ["fragmented_multi_table_chapter"],
                        "why": "Two full genealogy tables plus a separate totals table indicate fragmentation rather than one continuous canonical table.",
                        "relevant_pages": list(relevant_pages),
                        "repair_priority": "high",
                        "evidence": [],
                        "source_pages": list(source_pages),
                        "source_printed_pages": list(source_pages),
                        "surfaced_new_vs_current_detector": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return report_path


def _fixture_multichapter_planner_artifacts(tmp_path: Path) -> Path:
    report_path = tmp_path / "document_consistency_report.jsonl"
    pattern_inventory_path = tmp_path / "pattern_inventory.json"
    consistency_plan_path = tmp_path / "consistency_plan.json"
    conformance_report_path = tmp_path / "conformance_report.json"

    _write_jsonl(
        report_path,
        [
            {
                "schema_version": "pipeline_issues_v1",
                "module_id": "plan_onward_document_consistency_v1",
                "summary": {},
                "issues": [
                    {
                        "type": "document_consistency_planning_issue",
                        "chapter_basename": "chapter-013.html",
                        "chapter_title": "Frank's Family",
                        "status": "format_drift",
                        "pattern_id": "pattern_1",
                        "issue_types": ["fragmented_multi_table_chapter"],
                        "relevant_pages": [56, 57],
                        "surfaced_new_vs_current_detector": True,
                        "evidence": [],
                    },
                    {
                        "type": "document_consistency_planning_issue",
                        "chapter_basename": "chapter-014.html",
                        "chapter_title": "George's Family",
                        "status": "format_drift",
                        "pattern_id": "pattern_1",
                        "issue_types": ["fragmented_multi_table_chapter"],
                        "relevant_pages": [62, 63, 64],
                        "surfaced_new_vs_current_detector": True,
                        "evidence": [],
                    },
                ],
            }
        ],
    )
    payload = {
        "schema_version": "document_pattern_inventory_v1",
        "pattern_families": [
            {
                "pattern_id": "pattern_1",
                "label": "Main genealogy tables",
                "description": "Seven-column tables with subgroup rows.",
                "baseline_chapters": ["chapter-009.html"],
                "canonical_headers": ["NAME", "BORN", "MARRIED", "SPOUSE", "BOY", "GIRL", "DIED"],
            }
        ],
    }
    pattern_inventory_path.write_text(json.dumps(payload), encoding="utf-8")
    consistency_plan_path.write_text(
        json.dumps(
            {
                "schema_version": "document_consistency_plan_v1",
                "pattern_conventions": [
                    {
                        "pattern_id": "pattern_1",
                        "label": "Main genealogy tables",
                        "canonical_headers": ["NAME", "BORN", "MARRIED", "SPOUSE", "BOY", "GIRL", "DIED"],
                        "canonical_signals": ["single continuous genealogy table"],
                        "allowed_variants": ["separate totals table"],
                        "document_local_conventions": {
                            "subgroup_context_rows": "Use full-width subgroup rows.",
                            "table_fragmentation": "Prefer one continuous table per chapter whenever the scan supports it.",
                            "summary_rows": "Keep totals after the genealogy table.",
                            "marginal_or_handwritten_notes": "Keep notes out of DIED unless the source marks a death.",
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    conformance_report_path.write_text(
        json.dumps(
            {
                "schema_version": "document_conformance_report_v1",
                "summary": {},
                "chapters": [
                    {
                        "chapter_basename": "chapter-013.html",
                        "chapter_title": "Frank's Family",
                        "pattern_id": "pattern_1",
                        "status": "format_drift",
                        "issue_types": ["fragmented_multi_table_chapter"],
                        "why": "Fragmented.",
                        "relevant_pages": [56, 57],
                        "repair_priority": "high",
                        "evidence": [],
                        "source_pages": [54, 55, 56, 57, 58, 59],
                        "source_printed_pages": [54, 55, 56, 57, 58, 59],
                        "surfaced_new_vs_current_detector": True,
                    },
                    {
                        "chapter_basename": "chapter-014.html",
                        "chapter_title": "George's Family",
                        "pattern_id": "pattern_1",
                        "status": "format_drift",
                        "issue_types": ["fragmented_multi_table_chapter"],
                        "why": "Fragmented.",
                        "relevant_pages": [62, 63, 64],
                        "repair_priority": "high",
                        "evidence": [],
                        "source_pages": [60, 61, 62, 63, 64, 65],
                        "source_printed_pages": [60, 61, 62, 63, 64, 65],
                        "surfaced_new_vs_current_detector": True,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return report_path


def test_load_targets_uses_validator_pages_and_context(tmp_path: Path):
    report_path = _fixture_report(tmp_path)

    targets = load_targets(
        str(report_path),
        target_mode="strong",
        page_context_window=1,
        chapter_allowlist={"chapter-010.html"},
        page_allowlist=None,
        max_pages=10,
    )

    assert [target.page_number for target in targets] == [34]
    assert targets[0].context_pages == [33, 35]
    assert targets[0].schema_hint == "name|born|married|spouse|boy|girl|died"


def test_load_targets_can_expand_to_coarse_pages_with_allowlist(tmp_path: Path):
    report_path = _fixture_report(tmp_path)

    targets = load_targets(
        str(report_path),
        target_mode="coarse",
        page_context_window=1,
        chapter_allowlist={"chapter-010.html"},
        page_allowlist={33, 34, 35},
        max_pages=10,
    )

    assert [target.page_number for target in targets] == [34, 35]
    assert targets[0].context_pages == [33, 35]
    assert targets[1].context_pages == [34]


def test_load_targets_can_consume_planner_relevant_pages(tmp_path: Path):
    pages_path = _fixture_planner_pages(tmp_path)
    report_path = _fixture_planner_artifacts(tmp_path, relevant_pages=[56, 57], source_pages=[54, 55, 56, 57, 58, 59])
    page_rows = {
        row["page_number"]: row
        for row in (json.loads(line) for line in pages_path.read_text(encoding="utf-8").splitlines() if line.strip())
    }

    selection = load_targets(
        str(report_path),
        page_rows=page_rows,
        target_mode="strong",
        page_context_window=1,
        chapter_allowlist=None,
        page_allowlist=None,
        max_pages=10,
        return_selection=True,
    )

    assert selection.selection_mode == "planner"
    assert [target.page_number for target in selection.targets] == [56, 57]
    assert selection.targets[0].target_source == "planner_relevant_pages"
    assert selection.targets[0].pattern_label == "Main genealogy tables"
    assert "Canonical headers: NAME | BORN | MARRIED | SPOUSE | BOY | GIRL | DIED" in selection.targets[0].plan_rule_summary


def test_load_targets_augments_planner_relevant_pages_with_source_signals(tmp_path: Path):
    pages_path = _fixture_planner_pages(tmp_path)
    report_path = _fixture_planner_artifacts(tmp_path, relevant_pages=[54], source_pages=[54, 55, 56, 57, 58, 59])
    page_rows = {
        row["page_number"]: row
        for row in (json.loads(line) for line in pages_path.read_text(encoding="utf-8").splitlines() if line.strip())
    }

    selection = load_targets(
        str(report_path),
        page_rows=page_rows,
        target_mode="strong",
        page_context_window=1,
        chapter_allowlist=None,
        page_allowlist=None,
        max_pages=10,
        return_selection=True,
    )

    assert [target.page_number for target in selection.targets] == [54, 56, 57]
    assert selection.targets[0].target_source == "planner_relevant_pages_augmented"
    assert "augmented with source-page signals" in " ".join(selection.targets[0].target_selection_notes)


def test_load_targets_derives_fragment_cluster_when_planner_omits_pages(tmp_path: Path):
    pages_path = _fixture_planner_pages(tmp_path)
    report_path = _fixture_planner_artifacts(tmp_path, relevant_pages=[], source_pages=[54, 55, 56, 57, 58, 59])
    page_rows = {
        row["page_number"]: row
        for row in (json.loads(line) for line in pages_path.read_text(encoding="utf-8").splitlines() if line.strip())
    }

    selection = load_targets(
        str(report_path),
        page_rows=page_rows,
        target_mode="strong",
        page_context_window=1,
        chapter_allowlist=None,
        page_allowlist=None,
        max_pages=10,
        return_selection=True,
    )

    assert [target.page_number for target in selection.targets] == [56, 57]
    assert selection.targets[0].target_source == "planner_source_pages_fallback"
    assert selection.targets[0].surfaced_new_vs_current_detector is True
    assert selection.unresolved_chapters == []
    assert "derived rerun targets from chapter source_pages plus current page_html metrics" in " ".join(
        selection.targets[0].target_selection_notes
    )


def test_load_targets_records_unresolved_planner_chapter_when_fallback_has_no_candidate_pages(tmp_path: Path):
    pages_path = _fixture_planner_pages(tmp_path)
    report_path = _fixture_planner_artifacts(tmp_path, relevant_pages=[], source_pages=[54, 55])
    page_rows = {
        row["page_number"]: row
        for row in (json.loads(line) for line in pages_path.read_text(encoding="utf-8").splitlines() if line.strip())
    }

    selection = load_targets(
        str(report_path),
        page_rows=page_rows,
        target_mode="strong",
        page_context_window=1,
        chapter_allowlist=None,
        page_allowlist=None,
        max_pages=10,
        return_selection=True,
    )

    assert selection.targets == []
    assert len(selection.unresolved_chapters) == 1
    assert selection.unresolved_chapters[0].target_source == "planner_fallback_no_candidate_pages"
    assert selection.unresolved_chapters[0].chapter_basename == "chapter-013.html"


def test_load_targets_interleaves_planner_pages_before_max_page_cap(tmp_path: Path):
    pages_path = _fixture_planner_pages(tmp_path)
    for page_number in (60, 61, 62, 63, 64, 65):
        image_path = tmp_path / f"{page_number}.jpg"
        image_path.write_bytes(f"fake-image-{page_number}".encode("utf-8"))
        with pages_path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "schema_version": "page_html_v1",
                        "page": page_number,
                        "page_number": page_number,
                        "printed_page_number": page_number - 9,
                        "image": str(image_path),
                        "html": "<table><tr><td>Cluster</td></tr></table>",
                    }
                )
                + "\n"
            )
    report_path = _fixture_multichapter_planner_artifacts(tmp_path)
    page_rows = {
        row["page_number"]: row
        for row in (json.loads(line) for line in pages_path.read_text(encoding="utf-8").splitlines() if line.strip())
    }

    selection = load_targets(
        str(report_path),
        page_rows=page_rows,
        target_mode="strong",
        page_context_window=1,
        chapter_allowlist=None,
        page_allowlist=None,
        max_pages=3,
        return_selection=True,
    )

    assert [(target.chapter_basename, target.page_number) for target in selection.targets] == [
        ("chapter-013.html", 56),
        ("chapter-014.html", 62),
        ("chapter-013.html", 57),
    ]


def test_build_user_text_includes_schema_reasons_and_neighbor_context(tmp_path: Path):
    rows, page_map = _fixture_rows(tmp_path)
    del rows  # only page_map is needed here
    report_path = _fixture_report(tmp_path)
    target = load_targets(
        str(report_path),
        target_mode="strong",
        page_context_window=1,
        chapter_allowlist=None,
        page_allowlist=None,
        max_pages=10,
    )[0]

    prompt_text = build_user_text(target, page_map, max_context_chars=2000)

    assert "Frozen schema hint: name|born|married|spouse|boy|girl|died" in prompt_text
    assert "Consistency reasons: external_family_headings" in prompt_text
    assert "Neighbor page context:" in prompt_text
    assert "Page 35 (printed 26):" in prompt_text


def test_build_user_text_includes_planner_guidance(tmp_path: Path):
    pages_path = _fixture_planner_pages(tmp_path)
    page_rows = {
        row["page_number"]: row
        for row in (json.loads(line) for line in pages_path.read_text(encoding="utf-8").splitlines() if line.strip())
    }
    target = RerunTarget(
        page_number=56,
        chapter_basename="chapter-013.html",
        chapter_title="Frank's Family",
        schema_hint="name|born|married|spouse|boy|girl|died",
        issue_reasons=["fragmented_multi_table_chapter"],
        source_pages=[54, 55, 56, 57, 58, 59],
        context_pages=[57],
        target_source="planner_source_pages_fallback",
        issue_types=["fragmented_multi_table_chapter"],
        pattern_id="pattern_1",
        pattern_label="Main genealogy tables",
        planner_status="format_drift",
        planner_why="Two full genealogy tables plus a separate totals table indicate fragmentation.",
        plan_rule_summary=[
            "Canonical headers: NAME | BORN | MARRIED | SPOUSE | BOY | GIRL | DIED",
            "Table fragmentation: Prefer one continuous table per chapter whenever the scan supports it.",
        ],
        target_selection_notes=["Planner omitted relevant_pages; derived rerun targets from source pages."],
    )

    prompt_text = build_user_text(target, page_rows, max_context_chars=2000)

    assert "Pattern family: Main genealogy tables (pattern_1)" in prompt_text
    assert "Planner conformance reason: Two full genealogy tables plus a separate totals table indicate fragmentation." in prompt_text
    assert "Consistency plan guidance:" in prompt_text
    assert "Target selection notes:" in prompt_text


def test_retention_gate_rejects_candidate_that_drops_family_and_summary():
    accepted, reason, metrics = _retention_gate(
        EXISTING_BAD_HTML,
        LOW_RETENTION_CANDIDATE_HTML,
        min_token_recall=0.75,
        min_text_ratio=0.65,
    )

    assert accepted is False
    assert reason == "candidate_lost_summary_labels"
    assert metrics.summary_preserved is False


def test_retention_gate_accepts_split_context_when_family_label_is_preserved():
    accepted, reason, metrics = _retention_gate(
        MIXED_CONTEXT_EXISTING_HTML,
        SPLIT_CONTEXT_CANDIDATE_HTML,
        min_token_recall=0.75,
        min_text_ratio=0.65,
    )

    assert accepted is True
    assert reason == "candidate_content_retained"
    assert metrics.family_labels_preserved is True


def test_page_drift_gate_accepts_less_fragmented_candidate():
    accepted, reason, existing_metrics, candidate_metrics = _page_drift_gate(
        MIXED_CONTEXT_EXISTING_HTML,
        SPLIT_CONTEXT_CANDIDATE_HTML,
    )

    assert accepted is True
    assert reason in {"candidate_drift_reduced", "candidate_drift_not_worsened"}
    assert existing_metrics["external_family_heading_count"] >= candidate_metrics["external_family_heading_count"]


def test_best_effort_normalize_html_converts_name_list_paragraphs_into_table_rows():
    normalized = _best_effort_normalize_html(NAME_LIST_EXISTING_HTML)
    soup = BeautifulSoup(normalized, "html.parser")

    assert "Claire" in soup.get_text(" ", strip=True)
    assert not any("Claire" in paragraph.get_text(" ", strip=True) for paragraph in soup.find_all("p"))
    subgroup_rows = [
        row.get_text(" ", strip=True)
        for row in soup.find_all("tr", class_="genealogy-subgroup-heading")
    ]
    assert "ULRIC'S FAMILY" in subgroup_rows


def test_best_effort_normalize_html_rewrites_embedded_family_header_tables():
    normalized = _best_effort_normalize_html(EMBEDDED_FAMILY_HEADER_HTML)
    soup = BeautifulSoup(normalized, "html.parser")

    table = soup.find("table")
    assert table is not None
    header_cells = table.find("thead").find("tr", recursive=False).find_all("th", recursive=False)
    assert [cell.get_text(" ", strip=True) for cell in header_cells] == [
        "NAME",
        "BORN",
        "MARRIED",
        "SPOUSE",
        "BOY",
        "GIRL",
        "DIED",
    ]
    subgroup_rows = [
        row.get_text(" ", strip=True)
        for row in table.find("tbody").find_all("tr", class_="genealogy-subgroup-heading", recursive=False)
    ]
    assert subgroup_rows == ["SANDRA'S FAMILY"]


def test_run_reruns_accepts_candidate_and_preserves_untouched_pages(tmp_path: Path, monkeypatch):
    rows, page_map = _fixture_rows(tmp_path)
    report_path = _fixture_report(tmp_path)
    targets = load_targets(
        str(report_path),
        target_mode="strong",
        page_context_window=1,
        chapter_allowlist=None,
        page_allowlist=None,
        max_pages=10,
    )

    monkeypatch.setattr(
        "modules.adapter.rerun_onward_genealogy_consistency_v1.main._encode_image",
        lambda path: f"encoded:{Path(path).name}",
    )
    monkeypatch.setattr(
        "modules.adapter.rerun_onward_genealogy_consistency_v1.main._call_ocr",
        lambda *args, **kwargs: (
            ACCEPTED_CANDIDATE_HTML,
            SimpleNamespace(prompt_tokens=11, completion_tokens=22),
            "req_accept",
        ),
    )

    out_path = tmp_path / "pages_rerun.jsonl"
    report_out = tmp_path / "rerun_report.jsonl"
    summary_out = tmp_path / "rerun_summary.json"

    run_reruns(
        rows,
        page_map,
        targets,
        report_path=str(report_out),
        summary_path=str(summary_out),
        pages_artifact_path=str(tmp_path / "pages.jsonl"),
        consistency_report_path=str(report_path),
        out_path=str(out_path),
        model="gpt-5",
        temperature=0.0,
        max_output_tokens=32000,
        timeout_seconds=30.0,
        max_context_chars=4000,
        min_score_gain=15,
        min_token_recall=0.75,
        min_text_ratio=0.65,
        prompt="prompt",
        run_id="story143-test",
        progress_file=None,
        state_file=None,
    )

    out_rows = [json.loads(line) for line in out_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    report_rows = [json.loads(line) for line in report_out.read_text(encoding="utf-8").splitlines() if line.strip()]
    summary = json.loads(summary_out.read_text(encoding="utf-8"))

    rerun_row = next(row for row in out_rows if row["page_number"] == 34)
    untouched_row = next(row for row in out_rows if row["page_number"] == 40)
    report_row = report_rows[0]

    assert "genealogy-subgroup-heading" in rerun_row["html"]
    assert untouched_row["html"] == "<p>Untouched page</p>"
    assert report_row["accepted"] is True
    assert report_row["decision_reason"] == "candidate_accepted"
    assert report_row["existing_html"] == EXISTING_BAD_HTML
    assert "LAWRENCE'S FAMILY" in report_row["candidate_html"]
    assert summary["accepted_page_count"] == 1


def test_run_reruns_applies_deterministic_normalization_to_untargeted_pages(tmp_path: Path):
    image_path = tmp_path / "120.jpg"
    image_path.write_bytes(b"fake-image-120")
    rows = [
        {
            "schema_version": "page_html_v1",
            "page": 120,
            "page_number": 120,
            "image": str(image_path),
            "printed_page_number": 111,
            "html": NORMALIZE_ONLY_EXISTING_HTML,
        }
    ]
    page_map = {120: rows[0]}
    out_path = tmp_path / "pages_rerun.jsonl"
    report_out = tmp_path / "rerun_report.jsonl"
    summary_out = tmp_path / "rerun_summary.json"

    run_reruns(
        rows,
        page_map,
        [],
        report_path=str(report_out),
        summary_path=str(summary_out),
        pages_artifact_path=str(tmp_path / "pages.jsonl"),
        consistency_report_path=str(tmp_path / "consistency.jsonl"),
        out_path=str(out_path),
        model="gpt-5",
        temperature=0.0,
        max_output_tokens=32000,
        timeout_seconds=30.0,
        max_context_chars=4000,
        min_score_gain=15,
        min_token_recall=0.75,
        min_text_ratio=0.65,
        prompt="prompt",
        run_id="story146-test",
        progress_file=None,
        state_file=None,
    )

    out_rows = [json.loads(line) for line in out_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    report_rows = [json.loads(line) for line in report_out.read_text(encoding="utf-8").splitlines() if line.strip()]
    summary = json.loads(summary_out.read_text(encoding="utf-8"))

    assert out_rows[0]["html"] != NORMALIZE_ONLY_EXISTING_HTML
    assert report_rows[0]["targeted"] is False
    assert report_rows[0]["decision_reason"] == "deterministic_normalization_accepted"
    assert summary["deterministic_normalized_page_count"] == 1
    assert summary["deterministic_normalized_pages"] == [120]


def test_run_reruns_records_planner_context_and_unresolved_chapters(tmp_path: Path, monkeypatch):
    pages_path = _fixture_planner_pages(tmp_path)
    rows = [json.loads(line) for line in pages_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    page_map = {row["page_number"]: row for row in rows}
    target = RerunTarget(
        page_number=56,
        chapter_basename="chapter-013.html",
        chapter_title="Frank's Family",
        schema_hint="name|born|married|spouse|boy|girl|died",
        issue_reasons=["fragmented_multi_table_chapter"],
        source_pages=[54, 55, 56, 57, 58, 59],
        context_pages=[57],
        target_source="planner_source_pages_fallback",
        issue_types=["fragmented_multi_table_chapter"],
        pattern_id="pattern_1",
        pattern_label="Main genealogy tables",
        planner_status="format_drift",
        planner_why="Two full genealogy tables plus a separate totals table indicate fragmentation.",
        repair_priority="high",
        target_selection_notes=["Planner omitted relevant_pages; derived rerun targets from source pages."],
        plan_rule_summary=["Canonical headers: NAME | BORN | MARRIED | SPOUSE | BOY | GIRL | DIED"],
        plan_rule_details={"document_local_conventions": {"table_fragmentation": "Prefer one continuous table."}},
        surfaced_new_vs_current_detector=True,
    )
    unresolved = [
        UnresolvedChapter(
            chapter_basename="chapter-014.html",
            chapter_title="Another Family",
            source_pages=[60, 61],
            issue_reasons=["fragmented_multi_table_chapter"],
            issue_types=["fragmented_multi_table_chapter"],
            pattern_id="pattern_1",
            pattern_label="Main genealogy tables",
            planner_status="format_drift",
            planner_why="No bounded target pages could be justified.",
            target_source="planner_fallback_no_candidate_pages",
            target_selection_notes=["No source page retained any table or issue signal."],
            plan_rule_summary=["Canonical headers: NAME | BORN | MARRIED | SPOUSE | BOY | GIRL | DIED"],
        )
    ]

    monkeypatch.setattr(
        "modules.adapter.rerun_onward_genealogy_consistency_v1.main._encode_image",
        lambda path: f"encoded:{Path(path).name}",
    )
    monkeypatch.setattr(
        "modules.adapter.rerun_onward_genealogy_consistency_v1.main._call_ocr",
        lambda *args, **kwargs: (
            ACCEPTED_CANDIDATE_HTML,
            SimpleNamespace(prompt_tokens=11, completion_tokens=22),
            "req_accept",
        ),
    )

    out_path = tmp_path / "pages_rerun.jsonl"
    report_out = tmp_path / "rerun_report.jsonl"
    summary_out = tmp_path / "rerun_summary.json"

    run_reruns(
        rows,
        page_map,
        [target],
        unresolved_chapters=unresolved,
        selection_mode="planner",
        planner_artifact_paths={
            "pattern_inventory": str(tmp_path / "pattern_inventory.json"),
            "consistency_plan": str(tmp_path / "consistency_plan.json"),
            "conformance_report": str(tmp_path / "conformance_report.json"),
        },
        report_path=str(report_out),
        summary_path=str(summary_out),
        pages_artifact_path=str(pages_path),
        consistency_report_path=str(tmp_path / "document_consistency_report.jsonl"),
        out_path=str(out_path),
        model="gpt-5",
        temperature=0.0,
        max_output_tokens=32000,
        timeout_seconds=30.0,
        max_context_chars=4000,
        min_score_gain=15,
        min_token_recall=0.75,
        min_text_ratio=0.65,
        prompt="prompt",
        run_id="story146-test",
        progress_file=None,
        state_file=None,
    )

    report_rows = [json.loads(line) for line in report_out.read_text(encoding="utf-8").splitlines() if line.strip()]
    summary = json.loads(summary_out.read_text(encoding="utf-8"))

    unresolved_row = next(row for row in report_rows if row["chapter_basename"] == "chapter-014.html")
    targeted_row = next(row for row in report_rows if row["page_number"] == 56)

    assert unresolved_row["unresolved"] is True
    assert unresolved_row["decision_reason"] == "planner_fallback_no_candidate_pages"
    assert targeted_row["pattern_label"] == "Main genealogy tables"
    assert targeted_row["target_source"] == "planner_source_pages_fallback"
    assert targeted_row["selection_mode"] == "planner"
    assert summary["selection_mode"] == "planner"
    assert summary["unresolved_chapter_count"] == 1
    assert summary["target_sources"]["planner_source_pages_fallback"] == 1


def test_cli_smoke_keeps_original_html_when_image_is_missing(tmp_path: Path):
    pages_path = tmp_path / "pages.jsonl"
    report_path = _fixture_report(tmp_path)
    out_path = tmp_path / "pages_rerun.jsonl"
    summary_path = tmp_path / "rerun_summary.json"
    report_out = tmp_path / "rerun_report.jsonl"

    _write_jsonl(
        pages_path,
        [
            {
                "schema_version": "page_html_v1",
                "page": 34,
                "page_number": 34,
                "image": str(tmp_path / "missing.jpg"),
                "printed_page_number": 25,
                "html": EXISTING_BAD_HTML,
            }
        ],
    )

    from modules.adapter.rerun_onward_genealogy_consistency_v1.main import main

    old_argv = sys.argv
    sys.argv = [
        "rerun_onward_genealogy_consistency_v1",
        "--pages",
        str(pages_path),
        "--consistency",
        str(report_path),
        "--out",
        str(out_path),
        "--report",
        str(report_out),
        "--summary-report",
        str(summary_path),
        "--chapter-allowlist",
        "chapter-010.html",
        "--page-allowlist",
        "34",
    ]
    try:
        main()
    finally:
        sys.argv = old_argv

    out_rows = [json.loads(line) for line in out_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    report_rows = [json.loads(line) for line in report_out.read_text(encoding="utf-8").splitlines() if line.strip()]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert out_rows[0]["html"] == EXISTING_BAD_HTML
    assert report_rows[0]["decision_reason"] == "missing_image"
    assert report_rows[0]["accepted"] is False
    assert summary["targeted_pages"] == [34]
    assert summary["rejected_page_count"] == 1


def test_run_reruns_accepts_normalized_existing_without_ocr(tmp_path: Path, monkeypatch):
    image_path = tmp_path / "67.jpg"
    image_path.write_bytes(b"fake-image-67")
    rows = [
        {
            "schema_version": "page_html_v1",
            "page": 67,
            "page_number": 67,
            "image": str(image_path),
            "printed_page_number": 58,
            "html": NORMALIZE_ONLY_EXISTING_HTML,
        }
    ]
    page_map = {67: rows[0]}
    targets = [
        RerunTarget(
            page_number=67,
            chapter_basename="chapter-015.html",
            chapter_title="Joe",
            schema_hint="name|born|married|spouse|boygirl|died",
            issue_reasons=["residual_boygirl_headers"],
            source_pages=[67, 68, 69],
            context_pages=[68],
        )
    ]

    def _unexpected_call(*args, **kwargs):
        raise AssertionError("OCR should not run when normalized existing is accepted")

    monkeypatch.setattr(
        "modules.adapter.rerun_onward_genealogy_consistency_v1.main._call_ocr",
        _unexpected_call,
    )

    out_path = tmp_path / "pages_rerun.jsonl"
    report_out = tmp_path / "rerun_report.jsonl"
    summary_out = tmp_path / "rerun_summary.json"

    run_reruns(
        rows,
        page_map,
        targets,
        report_path=str(report_out),
        summary_path=str(summary_out),
        pages_artifact_path=str(tmp_path / "pages.jsonl"),
        consistency_report_path=str(tmp_path / "consistency.jsonl"),
        out_path=str(out_path),
        model="gpt-5",
        temperature=0.0,
        max_output_tokens=32000,
        timeout_seconds=30.0,
        max_context_chars=4000,
        min_score_gain=15,
        min_token_recall=0.75,
        min_text_ratio=0.65,
        prompt="prompt",
        run_id="story143-test",
        progress_file=None,
        state_file=None,
    )

    out_rows = [json.loads(line) for line in out_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    report_rows = [json.loads(line) for line in report_out.read_text(encoding="utf-8").splitlines() if line.strip()]

    assert out_rows[0]["html"] != NORMALIZE_ONLY_EXISTING_HTML
    assert "genealogy-subgroup-heading" in out_rows[0]["html"]
    assert report_rows[0]["decision_reason"] == "normalized_existing_accepted"
    assert report_rows[0]["accepted"] is True
    assert report_rows[0]["normalized_existing_accepted"] is True
