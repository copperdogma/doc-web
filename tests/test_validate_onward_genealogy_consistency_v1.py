import json
import sys
from pathlib import Path

from modules.validate.validate_onward_genealogy_consistency_v1.main import (
    analyze_chapter_row,
    analyze_page_row,
    build_report,
)


GOOD_CHAPTER_HTML = """
<html><body>
  <table>
    <thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr></thead>
    <tbody>
      <tr class="genealogy-subgroup-heading"><th colspan="7">PAUL'S FAMILY</th></tr>
      <tr><td>Alice</td><td>Jan. 1, 1970</td><td></td><td></td><td>1</td><td>0</td><td></td></tr>
    </tbody>
  </table>
  <table>
    <thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr></thead>
    <tbody>
      <tr class="genealogy-subgroup-heading"><th colspan="7">EMILIE'S GRANDCHILDREN</th></tr>
      <tr><td>Bob</td><td>Jan. 1, 1980</td><td></td><td></td><td>0</td><td>1</td><td></td></tr>
    </tbody>
  </table>
</body></html>
"""

BAD_EXTERNAL_CHAPTER_HTML = """
<html><body>
  <h2>ARTHUR'S GRANDCHILDREN<br/>LAWRENCE'S FAMILY</h2>
  <table><thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr></thead><tbody><tr><td>A</td><td></td><td></td><td></td><td></td><td></td><td></td></tr></tbody></table>
  <h2>BERNICE'S FAMILY</h2>
  <table><thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr></thead><tbody><tr><td>B</td><td></td><td></td><td></td><td></td><td></td><td></td></tr></tbody></table>
  <h2>RUSSEL'S FAMILY</h2>
  <table><thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr></thead><tbody><tr><td>C</td><td></td><td></td><td></td><td></td><td></td><td></td></tr></tbody></table>
  <h2>MORE FAMILY</h2>
  <table><thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr></thead><tbody><tr><td>D</td><td></td><td></td><td></td><td></td><td></td><td></td></tr></tbody></table>
  <h2>LAST FAMILY</h2>
  <table><thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr></thead><tbody><tr><td>E</td><td></td><td></td><td></td><td></td><td></td><td></td></tr></tbody></table>
</body></html>
"""

BAD_BOYGIRL_CHAPTER_HTML = """
<html><body>
  <table>
    <thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY/GIRL</th><th>DIED</th></tr></thead>
    <tbody>
      <tr class="genealogy-subgroup-heading"><th colspan="6">PAUL'S FAMILY</th></tr>
      <tr><td>Alice</td><td>Jan. 1, 1970</td><td></td><td></td><td>1/0</td><td></td></tr>
    </tbody>
  </table>
  <table>
    <thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr></thead>
    <tbody>
      <tr class="genealogy-subgroup-heading"><th colspan="7">OTHER FAMILY</th></tr>
      <tr><td>Bob</td><td>Jan. 1, 1980</td><td></td><td></td><td>0</td><td>1</td><td></td></tr>
    </tbody>
  </table>
</body></html>
"""


def _write_manifest_and_pages(tmp_path: Path):
    good_path = tmp_path / "chapter-009.html"
    bad_external_path = tmp_path / "chapter-010.html"
    bad_boygirl_path = tmp_path / "chapter-013.html"
    good_path.write_text(GOOD_CHAPTER_HTML, encoding="utf-8")
    bad_external_path.write_text(BAD_EXTERNAL_CHAPTER_HTML, encoding="utf-8")
    bad_boygirl_path.write_text(BAD_BOYGIRL_CHAPTER_HTML, encoding="utf-8")

    manifest_rows = [
        {
            "kind": "chapter",
            "title": "Good",
            "file": str(good_path),
            "source_pages": [22, 23, 24, 25, 26, 27],
            "source_printed_pages": [13, 14, 15, 16, 17, 18],
        },
        {
            "kind": "chapter",
            "title": "Bad External",
            "file": str(bad_external_path),
            "source_pages": [28, 29, 30, 31, 32, 33, 34, 35, 36, 37],
            "source_printed_pages": [19, 20, 21, 22, 23, 24, 25, 26, 27, 28],
        },
        {
            "kind": "chapter",
            "title": "Bad BoyGirl",
            "file": str(bad_boygirl_path),
            "source_pages": [54, 55, 56, 57, 58, 59],
            "source_printed_pages": [45, 46, 47, 48, 49, 50],
        },
    ]
    pages = [
        {"schema_version": "page_html_v1", "page_number": 24, "printed_page_number": 15, "html": "<h2>MESSY FAMILY</h2><table><thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY/GIRL</th><th>DIED</th></tr></thead></table><table></table>"},
        {"schema_version": "page_html_v1", "page_number": 25, "printed_page_number": 16, "html": "<table><thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY/GIRL</th><th>DIED</th></tr></thead></table><table></table>"},
        {"schema_version": "page_html_v1", "page_number": 34, "printed_page_number": 25, "html": "<h2>LAWRENCE'S FAMILY</h2><table></table><table></table>"},
        {"schema_version": "page_html_v1", "page_number": 35, "printed_page_number": 26, "html": "<h2>BERNICE'S FAMILY</h2><table></table><table></table>"},
        {"schema_version": "page_html_v1", "page_number": 56, "printed_page_number": 47, "html": "<table><thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY/GIRL</th><th>DIED</th></tr></thead></table>"},
        {"schema_version": "page_html_v1", "page_number": 57, "printed_page_number": 48, "html": "<table></table><table></table>"},
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


def test_analyze_chapter_row_distinguishes_good_and_bad(tmp_path: Path):
    manifest_rows, _, _, _ = _write_manifest_and_pages(tmp_path)
    good = analyze_chapter_row(manifest_rows[0], flag_threshold=25)
    bad_external = analyze_chapter_row(manifest_rows[1], flag_threshold=25)
    bad_boygirl = analyze_chapter_row(manifest_rows[2], flag_threshold=25)

    assert good is not None and not good.flagged
    assert bad_external is not None and not bad_external.flagged
    assert "missing_subgroup_rows" in bad_external.reasons
    assert bad_boygirl is not None and bad_boygirl.flagged
    assert "residual_boygirl_headers" in bad_boygirl.reasons


def test_page_anomalies_only_narrow_flagged_chapters():
    good_page = analyze_page_row({"html": "<h2>MESSY FAMILY</h2><table></table><table></table>"})
    strong_page = analyze_page_row({"html": "<h2>LAWRENCE'S FAMILY</h2><table></table><table></table>"})
    boygirl_page = analyze_page_row({"html": "<table><thead><tr><th>BOY/GIRL</th></tr></thead></table>"})

    assert good_page.coarse_suspect
    assert strong_page.strong_rerun_candidate
    assert boygirl_page.coarse_suspect
    assert not boygirl_page.strong_rerun_candidate


def test_build_report_keeps_good_chapter_unflagged_even_with_messy_pages(tmp_path: Path):
    manifest_rows, page_rows_by_number, manifest_path, pages_path = _write_manifest_and_pages(tmp_path)

    primary_report, detail_report = build_report(
        manifest_rows,
        page_rows_by_number,
        chapters_path=str(manifest_path),
        pages_path=str(pages_path),
        portions_path=None,
        reviewed_golden_dir=None,
        flag_threshold=25,
        warning_band=0.25,
        redesign_band=0.30,
    )

    assert primary_report["summary"]["flagged_chapters"] == ["chapter-013.html"]
    assert primary_report["summary"]["strong_rerun_candidate_page_count"] == 1
    assert primary_report["summary"]["recommendation"] == "targeted_reruns_justified"

    good_detail = next(chapter for chapter in detail_report["chapters"] if chapter["chapter_basename"] == "chapter-009.html")
    assert not good_detail["flagged"]
    assert good_detail["coarse_suspect_pages"] == []


def test_build_report_flags_duplicate_portion_starts_and_reviewed_golden_regressions(tmp_path: Path):
    manifest_rows, page_rows_by_number, manifest_path, pages_path = _write_manifest_and_pages(tmp_path)

    portions_path = tmp_path / "portions.jsonl"
    portions_rows = [
        {"title": "One", "page_start": 12, "page_end": 12},
        {"title": "Two", "page_start": 12, "page_end": 12},
        {"title": "Three", "page_start": 20, "page_end": 20},
    ]
    with portions_path.open("w", encoding="utf-8") as handle:
        for row in portions_rows:
            handle.write(json.dumps(row) + "\n")

    golden_dir = tmp_path / "golden"
    golden_dir.mkdir()
    (golden_dir / "chapter-001.html").write_text(
        (
            "<html><body><h1>Good</h1>"
            "<h2>Expected heading</h2>"
            "<table></table><table></table><table></table>"
            "</body></html>"
        ),
        encoding="utf-8",
    )
    (golden_dir / "manifest.json").write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "entry_id": "chapter-001",
                        "title": "Good",
                        "path": "chapter-001.html",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    provenance_dir = golden_dir / "provenance"
    provenance_dir.mkdir()
    with (provenance_dir / "blocks.jsonl").open("w", encoding="utf-8") as handle:
        for row in [
            {
                "entry_id": "chapter-001",
                "source_page_number": 24,
                "block_kind": "heading",
            },
            {
                "entry_id": "chapter-001",
                "source_page_number": 24,
                "block_kind": "table",
            },
            {
                "entry_id": "chapter-001",
                "source_page_number": 25,
                "block_kind": "table",
            },
            {
                "entry_id": "chapter-001",
                "source_page_number": 25,
                "block_kind": "table",
            },
        ]:
            handle.write(json.dumps(row) + "\n")

    primary_report, detail_report = build_report(
        manifest_rows,
        page_rows_by_number,
        chapters_path=str(manifest_path),
        pages_path=str(pages_path),
        portions_path=str(portions_path),
        reviewed_golden_dir=str(golden_dir),
        flag_threshold=25,
        warning_band=0.25,
        redesign_band=0.30,
    )

    assert primary_report["summary"]["duplicate_portion_page_start_count"] == 1
    assert primary_report["summary"]["duplicate_portion_page_starts"] == [12]
    assert primary_report["summary"]["reviewed_golden_flagged_chapter_count"] == 1
    assert primary_report["summary"]["reviewed_golden_flagged_chapters"] == ["Good"]
    issues_by_type = {issue["type"]: issue for issue in primary_report["issues"]}
    issue_types = set(issues_by_type)
    assert "onward_duplicate_portion_page_start" in issue_types
    assert "onward_reviewed_golden_structure_regression" in issue_types
    golden_issue = issues_by_type["onward_reviewed_golden_structure_regression"]
    assert golden_issue["source_pages"] == [22, 23, 24, 25, 26, 27]
    assert golden_issue["coarse_suspect_pages"] == [25]
    assert golden_issue["strong_rerun_candidate_pages"] == [25]
    assert golden_issue["target_selection_basis"] == "reviewed_golden_provenance_focus_pages"
    assert detail_report["duplicate_portion_page_starts"][0]["page_start"] == 12
    assert detail_report["reviewed_golden_comparisons"][0]["flagged"]


def test_build_report_flags_over_fragmented_reviewed_golden_regressions(tmp_path: Path):
    header = (
        "<thead><tr>"
        "<th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th>"
        "</tr></thead>"
    )
    chapter_path = tmp_path / "chapter-011.html"
    chapter_path.write_text(
        (
            "<html><body><h1>LEONIDAS L'HEUREUX</h1><h2>Leonidas' Grandchildren</h2>"
            "<h3>SHARON'S FAMILY</h3>"
            f"<table>{header}<tbody><tr><td>A</td><td></td><td></td><td></td><td></td><td></td><td></td></tr></tbody></table>"
            f"<table>{header}<tbody><tr><td>B</td><td></td><td></td><td></td><td></td><td></td><td></td></tr></tbody></table>"
            f"<table>{header}<tbody><tr><td>C</td><td></td><td></td><td></td><td></td><td></td><td></td></tr></tbody></table>"
            "</body></html>"
        ),
        encoding="utf-8",
    )
    manifest_rows = [
        {
            "kind": "chapter",
            "title": "LEONIDAS L'HEUREUX",
            "file": str(chapter_path),
            "source_pages": [41, 43, 45],
            "source_printed_pages": [32, 34, 36],
        }
    ]
    page_rows_by_number = {
        41: {"schema_version": "page_html_v1", "page_number": 41, "printed_page_number": 32, "html": f"<table>{header}<tbody><tr><td>A</td><td></td><td></td><td></td><td></td><td></td><td></td></tr></tbody></table><table><tbody><tr><td>B</td><td></td></tr></tbody></table>"},
        43: {"schema_version": "page_html_v1", "page_number": 43, "printed_page_number": 34, "html": f"<table>{header}<tbody><tr><td>C</td><td></td><td></td><td></td><td></td><td></td><td></td></tr></tbody></table><table><tbody><tr><td>D</td><td></td></tr></tbody></table>"},
        45: {"schema_version": "page_html_v1", "page_number": 45, "printed_page_number": 36, "html": f"<table>{header}<tbody><tr><td>E</td><td></td><td></td><td></td><td></td><td></td><td></td></tr></tbody></table>"},
    }
    manifest_path = tmp_path / "manifest.jsonl"
    pages_path = tmp_path / "pages.jsonl"
    with manifest_path.open("w", encoding="utf-8") as handle:
        for row in manifest_rows:
            handle.write(json.dumps(row) + "\n")
    with pages_path.open("w", encoding="utf-8") as handle:
        for row in page_rows_by_number.values():
            handle.write(json.dumps(row) + "\n")

    golden_dir = tmp_path / "golden"
    golden_dir.mkdir()
    (golden_dir / "chapter-011.html").write_text(
        (
            "<html><body><h1>LEONIDAS L'HEUREUX</h1>"
            f"<table>{header}<tbody><tr><td>A</td><td></td><td></td><td></td><td></td><td></td><td></td></tr></tbody></table>"
            "<table><tbody><tr><td>TOTAL DESCENDANTS</td><td>10</td></tr></tbody></table>"
            "</body></html>"
        ),
        encoding="utf-8",
    )
    (golden_dir / "manifest.json").write_text(
        json.dumps({"entries": [{"entry_id": "chapter-011", "title": "LEONIDAS L'HEUREUX", "path": "chapter-011.html"}]}),
        encoding="utf-8",
    )

    primary_report, detail_report = build_report(
        manifest_rows,
        page_rows_by_number,
        chapters_path=str(manifest_path),
        pages_path=str(pages_path),
        portions_path=None,
        reviewed_golden_dir=str(golden_dir),
        flag_threshold=25,
        warning_band=0.25,
        redesign_band=0.30,
    )

    assert primary_report["summary"]["reviewed_golden_flagged_chapter_count"] == 1
    issue = next(item for item in primary_report["issues"] if item["type"] == "onward_reviewed_golden_structure_regression")
    assert "more_tables_than_reviewed_golden" in issue["reasons"]
    assert "more_h2_than_reviewed_golden" in issue["reasons"]
    assert "more_h3_than_reviewed_golden" in issue["reasons"]
    detail = detail_report["reviewed_golden_comparisons"][0]
    assert detail["flagged"] is True
    assert "more_tables_than_reviewed_golden" in detail["reasons"]


def test_build_report_accepts_high_similarity_simplified_reviewed_golden_shapes(tmp_path: Path):
    chapter_path = tmp_path / "chapter-017.html"
    chapter_path.write_text(
        (
            "<html><body><h1>MARIE-LOUISE</h1>"
            "<p>Shared narrative text for the genealogy chapter.</p>"
            "<h1>Marie Louise L'Heureux LaClare</h1>"
            "<table><thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr></thead>"
            "<tbody>"
            "<tr><td>Marie Louise</td><td>1893</td><td>1917</td><td>George LaClare</td><td>4</td><td>4</td><td>1985</td></tr>"
            "<tr class=\"genealogy-subgroup-heading\"><th colspan=\"7\">Mabel's Grandchildren</th></tr>"
            "<tr class=\"genealogy-subgroup-heading\"><th colspan=\"7\">CLEMENCE'S FAMILY</th></tr>"
            "<tr><td>Shelly</td><td>1966</td><td></td><td></td><td></td><td></td><td></td></tr>"
            "</tbody></table>"
            "<table><tbody><tr><td>TOTAL DESCENDANTS</td><td>215</td></tr></tbody></table>"
            "</body></html>"
        ),
        encoding="utf-8",
    )
    manifest_rows = [
        {
            "kind": "chapter",
            "title": "MARIE-LOUISE",
            "file": str(chapter_path),
            "source_pages": [81, 84],
            "source_printed_pages": [72, 75],
        }
    ]
    page_rows_by_number = {
        81: {"schema_version": "page_html_v1", "page_number": 81, "printed_page_number": 72, "html": "<table></table>"},
        84: {"schema_version": "page_html_v1", "page_number": 84, "printed_page_number": 75, "html": "<table></table>"},
    }
    manifest_path = tmp_path / "manifest.jsonl"
    pages_path = tmp_path / "pages.jsonl"
    with manifest_path.open("w", encoding="utf-8") as handle:
        for row in manifest_rows:
            handle.write(json.dumps(row) + "\n")
    with pages_path.open("w", encoding="utf-8") as handle:
        for row in page_rows_by_number.values():
            handle.write(json.dumps(row) + "\n")

    golden_dir = tmp_path / "golden"
    golden_dir.mkdir()
    (golden_dir / "chapter-017.html").write_text(
        (
            "<html><body><h1>MARIE-LOUISE</h1>"
            "<p>Shared narrative text for the genealogy chapter.</p>"
            "<h1>Marie Louise L'Heureux LaClare</h1>"
            "<table><thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr></thead>"
            "<tbody><tr><td>Marie Louise</td><td>1893</td><td>1917</td><td>George LaClare</td><td>4</td><td>4</td><td>1985</td></tr></tbody></table>"
            "<h2>Mabel's Grandchildren</h2>"
            "<h3>CLEMENCE'S FAMILY</h3>"
            "<table><thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr></thead>"
            "<tbody><tr><td>Shelly</td><td>1966</td><td></td><td></td><td></td><td></td><td></td></tr></tbody></table>"
            "<table><tbody><tr><td>TOTAL DESCENDANTS</td><td>215</td></tr></tbody></table>"
            "</body></html>"
        ),
        encoding="utf-8",
    )
    (golden_dir / "manifest.json").write_text(
        json.dumps({"entries": [{"entry_id": "chapter-017", "title": "MARIE-LOUISE", "path": "chapter-017.html"}]}),
        encoding="utf-8",
    )

    primary_report, detail_report = build_report(
        manifest_rows,
        page_rows_by_number,
        chapters_path=str(manifest_path),
        pages_path=str(pages_path),
        portions_path=None,
        reviewed_golden_dir=str(golden_dir),
        flag_threshold=25,
        warning_band=0.25,
        redesign_band=0.30,
    )

    assert primary_report["summary"]["reviewed_golden_flagged_chapter_count"] == 0
    assert not any(issue["type"] == "onward_reviewed_golden_structure_regression" for issue in primary_report["issues"])
    detail = detail_report["reviewed_golden_comparisons"][0]
    assert detail["flagged"] is False
    assert detail["reviewed_text_similarity"] is not None
    assert detail["reviewed_text_similarity"] >= 0.98


def test_cli_smoke_writes_summary_and_detail_report(tmp_path: Path):
    _, _, manifest_path, pages_path = _write_manifest_and_pages(tmp_path)
    out_path = tmp_path / "genealogy_consistency_report.jsonl"
    detail_path = tmp_path / "genealogy_consistency_detail.json"

    from modules.validate.validate_onward_genealogy_consistency_v1.main import main

    old_argv = sys.argv
    sys.argv = [
        "validate_onward_genealogy_consistency_v1",
        "--chapters",
        str(manifest_path),
        "--pages",
        str(pages_path),
        "--out",
        str(out_path),
        "--detail-report",
        str(detail_path),
    ]
    try:
        main()
    finally:
        sys.argv = old_argv

    summary_rows = [json.loads(line) for line in out_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    detail = json.loads(detail_path.read_text(encoding="utf-8"))

    assert len(summary_rows) == 1
    assert summary_rows[0]["schema_version"] == "pipeline_issues_v1"
    assert detail["schema_version"] == "onward_genealogy_consistency_report_v1"
    assert detail["summary"]["flagged_genealogy_chapters"] == 1
