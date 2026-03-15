import json
import sys
from pathlib import Path
from types import SimpleNamespace

from modules.adapter.rerun_onward_genealogy_consistency_v1.main import (
    _page_drift_gate,
    _retention_gate,
    RerunTarget,
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
