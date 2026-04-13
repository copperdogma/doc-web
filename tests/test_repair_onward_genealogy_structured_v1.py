import json
from pathlib import Path

from modules.transform.repair_onward_genealogy_structured_v1.main import (
    _build_prompt,
    _normalize_payload,
    _parse_json_payload,
    _render_structured_html,
    build_structured_user_text,
    run_structured_repairs,
)
from modules.adapter.rerun_onward_genealogy_consistency_v1.main import RerunTarget


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


def test_parse_and_render_structured_payload_normalizes_rows():
    payload = _normalize_payload(
        _parse_json_payload(
            """
            ```json
            {
              "table_segments": [
                {"kind": "heading", "text": "LAWRENCE'S FAMILY"},
                {
                  "kind": "row",
                  "name": "Alice",
                  "born": "Jan. 1, 1970",
                  "boy_girl": "1 1"
                }
              ],
              "summary_rows": [{"label": "TOTAL DESCENDANTS", "value": "2"}]
            }
            ```
            """
        )
    )

    assert payload["table_segments"][0] == {"kind": "subgroup_heading", "text": "LAWRENCE'S FAMILY"}
    assert payload["table_segments"][1]["cells"]["boy"] == "1"
    assert payload["table_segments"][1]["cells"]["girl"] == "1"

    rendered = _render_structured_html(payload)
    assert "genealogy-subgroup-heading" in rendered
    assert "<td>Alice</td>" in rendered
    assert "TOTAL DESCENDANTS" in rendered


def test_parse_and_render_structured_payload_promotes_note_only_non_death_rows():
    payload = _normalize_payload(
        {
            "table_segments": [
                {
                    "kind": "data_row",
                    "cells": {
                        "name": "",
                        "born": "",
                        "married": "",
                        "spouse": "",
                        "boy": "",
                        "girl": "",
                        "died": "1-Kassandra",
                    },
                },
                {
                    "kind": "data_row",
                    "cells": {
                        "name": "",
                        "born": "",
                        "married": "",
                        "spouse": "",
                        "boy": "",
                        "girl": "",
                        "died": "born Dec 30/1999",
                    },
                },
                {
                    "kind": "data_row",
                    "cells": {
                        "name": "",
                        "born": "",
                        "married": "",
                        "spouse": "",
                        "boy": "",
                        "girl": "",
                        "died": "(4 infants died)",
                    },
                },
            ],
            "summary_rows": [],
            "loose_paragraphs": [],
        }
    )

    assert payload["table_segments"][0] == {"kind": "note_row", "text": "1-Kassandra"}
    assert payload["table_segments"][1] == {"kind": "note_row", "text": "born Dec 30/1999"}
    assert payload["table_segments"][2]["kind"] == "data_row"

    rendered = _render_structured_html(payload)
    assert '<tr class="genealogy-note-row"><td colspan="7">1-Kassandra</td></tr>' in rendered
    assert '<tr class="genealogy-note-row"><td colspan="7">born Dec 30/1999</td></tr>' in rendered
    assert "(4 infants died)" in rendered
    assert rendered.count('class="genealogy-note-row"') == 2


def test_parse_and_render_structured_payload_splits_embedded_child_notes_out_of_died():
    payload = _normalize_payload(
        {
            "table_segments": [
                {
                    "kind": "data_row",
                    "cells": {
                        "name": "Marcia",
                        "born": "Mar. 10, 1963",
                        "married": "",
                        "spouse": "married Gary Moss",
                        "boy": "",
                        "girl": "",
                        "died": "Tessa born June 2/91 May 15 Chelsea wa",
                    },
                },
                {
                    "kind": "data_row",
                    "cells": {
                        "name": "Melinda",
                        "born": "Apr. 21, 1964",
                        "married": "",
                        "spouse": "",
                        "boy": "",
                        "girl": "",
                        "died": "born to Michelle &",
                    },
                },
            ],
            "summary_rows": [],
            "loose_paragraphs": [],
        }
    )

    assert payload["table_segments"][0]["kind"] == "data_row"
    assert payload["table_segments"][0]["cells"]["died"] == ""
    assert payload["table_segments"][1] == {
        "kind": "note_row",
        "text": "Tessa born June 2/91 May 15 Chelsea wa",
    }
    assert payload["table_segments"][2]["kind"] == "data_row"
    assert payload["table_segments"][2]["cells"]["died"] == ""
    assert payload["table_segments"][3] == {"kind": "note_row", "text": "born to Michelle &"}

    rendered = _render_structured_html(payload)
    assert "<td>Marcia</td>" in rendered
    assert "<td>Melinda</td>" in rendered
    assert '<tr class="genealogy-note-row"><td colspan="7">Tessa born June 2/91 May 15 Chelsea wa</td></tr>' in rendered
    assert '<tr class="genealogy-note-row"><td colspan="7">born to Michelle &amp;</td></tr>' in rendered


def test_build_structured_user_text_includes_json_shape(tmp_path: Path):
    rows, page_map = _fixture_rows(tmp_path)
    target = RerunTarget(
        page_number=34,
        chapter_basename="chapter-010.html",
        chapter_title="Genealogy",
        schema_hint="name|born|married|spouse|boy|girl|died",
        issue_reasons=["external_family_headings"],
        source_pages=[33, 34, 35],
        context_pages=[35],
        target_source="planner_source_pages_fallback",
        issue_types=["fragmented_multi_table_chapter"],
        pattern_id="pattern_1",
        pattern_label="Main genealogy tables",
        planner_status="format_drift",
        planner_why="Two small fragments should be one continuous table.",
        target_selection_notes=["Planner omitted relevant_pages; derived from source page signals."],
        plan_rule_summary=["Canonical headers: NAME | BORN | MARRIED | SPOUSE | BOY | GIRL | DIED"],
    )

    user_text = build_structured_user_text(target, page_map, max_context_chars=1200)

    assert "Return JSON only" in user_text
    assert '"canonical_headers", "table_segments", "summary_rows", "loose_paragraphs"' in user_text
    assert "Pattern family: Main genealogy tables (pattern_1)" in user_text
    assert "Neighbor page context" in user_text
    assert "Current extracted HTML" in user_text
    assert rows[0]["html"].strip() in user_text


def test_build_prompt_appends_row_semantic_recipe_hints():
    prompt = _build_prompt(
        """
        - The active issue type is child_note_in_wrong_column.
        - Never leave child or infant-age notes in the DIED column unless the source explicitly states death.
        - Move child-related notes back into BOY or GIRL, or BORN/MARRIED when the source clearly presents them that way.
        """.strip()
    )

    assert "child_note_in_wrong_column" in prompt
    assert "Never leave child or infant-age notes in the DIED column" in prompt
    assert "Move child-related notes back into BOY or GIRL" in prompt


def test_run_structured_repairs_accepts_candidate_and_writes_sidecar(tmp_path: Path, monkeypatch):
    rows, page_map = _fixture_rows(tmp_path)
    out_path = tmp_path / "out.jsonl"
    report_path = tmp_path / "report.jsonl"
    summary_path = tmp_path / "summary.json"
    sidecar_path = tmp_path / "sidecar.jsonl"

    target = RerunTarget(
        page_number=34,
        chapter_basename="chapter-010.html",
        chapter_title="Genealogy",
        schema_hint="name|born|married|spouse|boy|girl|died",
        issue_reasons=["external_family_headings"],
        source_pages=[33, 34, 35],
        context_pages=[35],
        target_source="planner_source_pages_fallback",
        issue_types=["fragmented_multi_table_chapter"],
        pattern_id="pattern_1",
        pattern_label="Main genealogy tables",
        planner_status="format_drift",
        planner_why="Two fragments should be one continuous table.",
        repair_priority="high",
        target_selection_notes=["Planner omitted relevant_pages; derived from source page signals."],
        plan_rule_summary=["Canonical headers: NAME | BORN | MARRIED | SPOUSE | BOY | GIRL | DIED"],
    )

    response = json.dumps(
        {
            "canonical_headers": ["NAME", "BORN", "MARRIED", "SPOUSE", "BOY", "GIRL", "DIED"],
            "table_segments": [
                {"kind": "subgroup_heading", "text": "LAWRENCE'S FAMILY"},
                {
                    "kind": "data_row",
                    "cells": {
                        "name": "Alice",
                        "born": "Jan. 1, 1970",
                        "married": "",
                        "spouse": "",
                        "boy": "1",
                        "girl": "1",
                        "died": "",
                    },
                },
            ],
            "summary_rows": [{"label": "TOTAL DESCENDANTS", "value": "2"}, {"label": "LIVING", "value": "2"}],
            "loose_paragraphs": [],
        }
    )

    monkeypatch.setattr(
        "modules.transform.repair_onward_genealogy_structured_v1.main._call_ocr",
        lambda *args, **kwargs: (response, {"output_tokens": 123}, "req-structured-1"),
    )

    run_structured_repairs(
        rows,
        page_map,
        [target],
        unresolved_chapters=[],
        selection_mode="planner",
        planner_artifact_paths={"pattern_inventory": "/tmp/pattern_inventory.json"},
        report_path=str(report_path),
        summary_path=str(summary_path),
        sidecar_path=str(sidecar_path),
        pages_artifact_path="/tmp/pages.jsonl",
        consistency_report_path="/tmp/report.jsonl",
        out_path=str(out_path),
        model="gpt-5",
        temperature=0.0,
        max_output_tokens=4096,
        timeout_seconds=30.0,
        max_context_chars=1200,
        min_score_gain=5,
        min_token_recall=0.75,
        min_text_ratio=0.65,
        prompt="structured prompt",
        run_id="story219-test",
        progress_file=None,
        state_file=None,
    )

    out_rows = [json.loads(line) for line in out_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    report_rows = [json.loads(line) for line in report_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    sidecar_rows = [json.loads(line) for line in sidecar_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    repaired_row = next(row for row in out_rows if row["page_number"] == 34)
    untouched_row = next(row for row in out_rows if row["page_number"] == 40)
    targeted_report = next(row for row in report_rows if row.get("page_number") == 34)

    assert "genealogy-subgroup-heading" in repaired_row["html"]
    assert "TOTAL DESCENDANTS" in repaired_row["html"]
    assert untouched_row["html"] == "<p>Untouched page</p>"
    assert targeted_report["accepted"] is True
    assert targeted_report["decision_reason"] in {"candidate_accepted", "candidate_drift_reduced"}
    assert sidecar_rows[0]["accepted"] is True
    assert sidecar_rows[0]["rebuild_owner_module"] == "repair_onward_genealogy_structured_v1"
    assert sidecar_rows[0]["pattern_id"] == "pattern_1"
    assert summary["accepted_page_count"] == 1
    assert summary["structured_sidecar_artifact_path"] == str(sidecar_path)


def test_run_structured_repairs_rejects_low_retention_candidate(tmp_path: Path, monkeypatch):
    rows, page_map = _fixture_rows(tmp_path)
    out_path = tmp_path / "out.jsonl"
    report_path = tmp_path / "report.jsonl"
    summary_path = tmp_path / "summary.json"
    sidecar_path = tmp_path / "sidecar.jsonl"

    target = RerunTarget(
        page_number=34,
        chapter_basename="chapter-010.html",
        chapter_title="Genealogy",
        schema_hint="name|born|married|spouse|boy|girl|died",
        issue_reasons=["external_family_headings"],
        source_pages=[33, 34, 35],
        context_pages=[35],
    )

    response = json.dumps(
        {
            "table_segments": [
                {
                    "kind": "data_row",
                    "cells": {
                        "name": "Alice",
                        "born": "Jan. 1, 1970",
                        "married": "",
                        "spouse": "",
                        "boy": "1",
                        "girl": "1",
                        "died": "",
                    },
                }
            ],
            "summary_rows": [],
            "loose_paragraphs": [],
        }
    )

    monkeypatch.setattr(
        "modules.transform.repair_onward_genealogy_structured_v1.main._call_ocr",
        lambda *args, **kwargs: (response, {"output_tokens": 77}, "req-structured-2"),
    )

    run_structured_repairs(
        rows,
        page_map,
        [target],
        unresolved_chapters=[],
        selection_mode="planner",
        planner_artifact_paths={},
        report_path=str(report_path),
        summary_path=str(summary_path),
        sidecar_path=str(sidecar_path),
        pages_artifact_path="/tmp/pages.jsonl",
        consistency_report_path="/tmp/report.jsonl",
        out_path=str(out_path),
        model="gpt-5",
        temperature=0.0,
        max_output_tokens=4096,
        timeout_seconds=30.0,
        max_context_chars=1200,
        min_score_gain=5,
        min_token_recall=0.75,
        min_text_ratio=0.65,
        prompt="structured prompt",
        run_id="story219-test",
        progress_file=None,
        state_file=None,
    )

    out_rows = [json.loads(line) for line in out_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    report_rows = [json.loads(line) for line in report_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    sidecar_rows = [json.loads(line) for line in sidecar_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    repaired_row = next(row for row in out_rows if row["page_number"] == 34)
    targeted_report = next(row for row in report_rows if row.get("page_number") == 34)

    assert repaired_row["html"] == EXISTING_BAD_HTML
    assert targeted_report["accepted"] is False
    assert targeted_report["decision_reason"] in {
        "candidate_lost_summary_labels",
        "candidate_lost_family_labels",
        "candidate_token_recall_too_low",
    }
    assert sidecar_rows[0]["accepted"] is False
