"""The serialized validator must retain source-row evidence for TOC links."""
import json

import pytest

from modules.validate.validate_semantic_manual_html_v1.main import build_report


def _write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))


def _report(tmp_path, case="valid"):
    toc = ('<table id="toc"><tr><td>Starting Out</td><td><a href="#2">2</a></td></tr>'
           '<tr><td>Equipment</td><td><a href="#3">3</a></td></tr></table>')
    pages = [
        {"page_number": number, "original_page_number": number, "printed_page_number": number,
         "html": html}
        for number, html in [
            (1, toc), (2, '<h2>STARTING OUT</h2>'), (3, '<h1>Equipment</h1>'),
            (4, '<h2>2 Workflow</h2><h2>3 Commitments</h2>')]
    ]
    contents = toc.replace('href="#2"', 'href="#first"').replace('href="#3"', 'href="guide.html#equipment"')
    contents += '<h2 id="first">STARTING OUT</h2>'
    guide = '<h1 id="equipment">Equipment</h1><h2 id="two">2 Workflow</h2><h2 id="three">3 Commitments</h2>'
    provenance = [
        {"block_id": block, "source_page_number": number, "source_original_page_number": number}
        for block, number in [("toc", 1), ("first", 2), ("equipment", 3), ("two", 4), ("three", 4)]
    ]
    if case == "wrong_target":
        contents = contents.replace('href="#first"', 'href="guide.html#two"')
    elif case == "wrong_cross_file_target":
        contents = contents.replace('href="guide.html#equipment"', 'href="guide.html#three"')
    elif case == "missing_fragment":
        contents = contents.replace('href="#first"', 'href="#absent"')
    elif case == "missing_file":
        contents = contents.replace('href="#first"', 'href="absent.html#first"')
    elif case == "duplicate_fragment":
        contents += '<p id="first">Duplicate destination</p>'
    elif case == "ambiguous_printed_label":
        pages[3]["printed_page_number"] = 2
    elif case == "ambiguous_heading":
        pages[1].pop("printed_page_number")
        pages[3].pop("printed_page_number")
        pages[3]["html"] += '<h2>STARTING OUT</h2>'
        guide += '<h2 id="duplicate-title">STARTING OUT</h2>'
        provenance.append({"block_id": "duplicate-title", "source_page_number": 4, "source_original_page_number": 4})
    elif case == "missing_row_provenance":
        provenance = [row for row in provenance if row["block_id"] != "toc"]
    elif case == "wrong_row_provenance":
        provenance[0]["source_original_page_number"] = 99
    elif case == "ordinary_numeric_reference":
        pages[0]["html"] += '<p>Consult section <a href="#2">2</a>.</p>'
        contents += '<p>Consult section <a href="#first">2</a>.</p>'

    html = tmp_path / "html"
    html.mkdir()
    (html / "contents.html").write_text("<article>" + contents + "</article>")
    (html / "guide.html").write_text("<article>" + guide + "</article>")
    (html / "manifest.json").write_text("{}")
    _write_rows(html / "provenance/blocks.jsonl", provenance)
    _write_rows(tmp_path / "pages.jsonl", pages)
    _write_rows(tmp_path / "chapters.jsonl", [
        {"file": str(html / "contents.html"), "source_pages": [1, 2], "title": "Contents"},
        {"file": str(html / "guide.html"), "source_pages": [3, 4], "title": "Equipment"},
    ])
    _write_rows(tmp_path / "logical/pages.jsonl", [{"page_number": number} for number in range(1, 5)])
    (tmp_path / "logical/logical_page_map.json").write_text(json.dumps({"summary": {
        "complete": True, "issues_count": 0, "inferred_logical_page_count": 4}}))
    (tmp_path / "plan.json").write_text("{}")
    (tmp_path / "crops.jsonl").write_text("")
    before = {str(path): path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}
    report = build_report(
        pages_path=tmp_path / "pages.jsonl", logical_pages_path=tmp_path / "logical/pages.jsonl",
        figure_plan_path=tmp_path / "plan.json", critical_graphics_manifest_path=None,
        crops_path=tmp_path / "crops.jsonl", chapters_path=tmp_path / "chapters.jsonl",
        run_id="navigation-context", min_figure_crop_ratio=.75, min_critical_target_crop_coverage=.5,
    )
    assert {str(path): path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()} == before
    return {check["id"]: check for check in report["checks"] if check["id"].startswith("local_navigation_")}


def test_serialized_validator_uses_title_and_page_for_same_and_cross_file_toc_links(tmp_path):
    checks = _report(tmp_path)
    assert checks["local_navigation_targets"]["status"] == "pass"
    assert checks["local_navigation_resolution"]["status"] == "pass"


@pytest.mark.parametrize("case,reason", [
    ("wrong_target", "source_toc_target_mismatch"),
    ("wrong_cross_file_target", "source_toc_target_mismatch"),
    ("missing_fragment", "missing_fragment"),
    ("missing_file", "missing_file"),
    ("duplicate_fragment", "duplicate_fragment"),
    ("ambiguous_printed_label", "duplicate_observed_printed_labels"),
    ("ambiguous_heading", "toc_duplicate_heading_targets"),
    ("missing_row_provenance", "toc_source_row_provenance_unavailable"),
    ("wrong_row_provenance", "toc_source_row_occurrence_ambiguous"),
    ("ordinary_numeric_reference", "source_heading_target_mismatch"),
])
def test_serialized_validator_keeps_fail_closed_navigation_checks(tmp_path, case, reason):
    check = _report(tmp_path, case)["local_navigation_targets"]
    assert check["status"] == "fail"
    assert reason in {issue["reason"] for issue in check["detail"]["issues"]}
