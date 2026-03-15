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
    assert bad_external is not None and bad_external.flagged
    assert "external_family_headings" in bad_external.reasons
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
        flag_threshold=25,
        warning_band=0.25,
        redesign_band=0.30,
    )

    assert primary_report["summary"]["flagged_chapters"] == ["chapter-010.html", "chapter-013.html"]
    assert primary_report["summary"]["strong_rerun_candidate_page_count"] == 3
    assert primary_report["summary"]["recommendation"] == "targeted_reruns_justified"

    good_detail = next(chapter for chapter in detail_report["chapters"] if chapter["chapter_basename"] == "chapter-009.html")
    assert not good_detail["flagged"]
    assert good_detail["coarse_suspect_pages"] == []


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
    assert detail["summary"]["flagged_genealogy_chapters"] == 2
