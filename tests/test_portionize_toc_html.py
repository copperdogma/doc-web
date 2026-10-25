import json
import subprocess
import sys
from pathlib import Path

import pytest


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def _run_toc(tmp_path: Path, pages: list, *extra_args: str):
    pages_path = tmp_path / "input.jsonl"
    out_path = tmp_path / "output.jsonl"
    _write_jsonl(pages_path, pages)
    before = pages_path.read_bytes()
    result = subprocess.run(
        [sys.executable, "-m", "modules.portionize.portionize_toc_html_v1.main",
         "--pages", str(pages_path), "--out", str(out_path), *extra_args],
        capture_output=True, text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    assert pages_path.read_bytes() == before
    return result, out_path


def test_missing_toc_still_fails_by_default(tmp_path: Path) -> None:
    result, out = _run_toc(tmp_path, [{"page": 1, "html": "<h1>Overview</h1><p>Text.</p>"}])
    assert result.returncode != 0
    assert "No TOC entries found" in result.stderr
    assert not out.exists()


@pytest.mark.parametrize("headings", [False, True])
def test_opted_in_fallback_uses_all_source_pages_despite_print_labels(tmp_path: Path, headings: bool) -> None:
    prefix = "<h1>Overview</h1>" if headings else ""
    result, out = _run_toc(
        tmp_path,
        [{"page_number": 9, "page": 90, "printed_page_number": 1, "html": "<p>End.</p>"},
         {"page_number": 3, "page": 30, "printed_page_number": 1, "html": prefix + "<p>Start.</p>"},
         {"page": 6, "printed_page_number": None, "html": "<p>Middle.</p>"}],
        "--fallback-mode", "single-document", "--fallback-title", "Harbor Notes",
    )
    assert result.returncode == 0, result.stderr
    rows = [json.loads(line) for line in out.read_text().splitlines()]
    assert len(rows) == 1
    assert rows[0]["portion_id"] == "document"
    assert rows[0]["title"] == "Harbor Notes"
    assert rows[0]["notes"] == "single-document-fallback"
    assert rows[0]["source_pages"] == [3, 6, 9]
    assert (rows[0]["page_start"], rows[0]["page_end"]) == (3, 9)


def test_fallback_title_defaults_to_document(tmp_path: Path) -> None:
    result, out = _run_toc(
        tmp_path, [{"page": 7, "html": "<p>Text.</p>"}], "--fallback-mode", "single-document",
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(out.read_text())["title"] == "Document"


def test_ordinary_prose_ellipsis_is_not_toc_evidence(tmp_path: Path) -> None:
    result, out = _run_toc(
        tmp_path, [{"page": 1, "html": "<p>She paused... then continued.</p>"}],
        "--fallback-mode", "single-document",
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(out.read_text())["notes"] == "single-document-fallback"


@pytest.mark.parametrize("input_text", ["", '{"page": 1, invalid}\n'])
def test_fallback_does_not_catch_empty_or_malformed_input(tmp_path: Path, input_text: str) -> None:
    pages_path = tmp_path / "broken.jsonl"
    pages_path.write_text(input_text)
    out_path = tmp_path / "portions.jsonl"
    result = subprocess.run(
        [sys.executable, "-m", "modules.portionize.portionize_toc_html_v1.main",
         "--pages", str(pages_path), "--out", str(out_path), "--fallback-mode", "single-document"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    assert result.returncode != 0
    assert "Input is empty" in result.stderr or "JSONDecodeError" in result.stderr
    assert pages_path.read_text() == input_text
    assert not out_path.exists()


@pytest.mark.parametrize("html", [
    "<h1>CONTENTS</h1><p>Broken entries.</p>",
    "<p>Chapter One ........ 4</p>",
    "<p>Chapter One ........ unknown</p>",
    "<p>Chapter One ........ iv</p>",
    "<p>Chapter One ........ Appendix A</p>",
    "<h2>Table of Contents</h2><table><tr><td>Chapter One</td><td>4</td></tr></table>",
])
def test_fallback_refuses_sparse_or_malformed_toc_evidence(tmp_path: Path, html: str) -> None:
    result, out = _run_toc(
        tmp_path, [{"page": 1, "html": html}], "--fallback-mode", "single-document",
    )
    assert result.returncode != 0
    assert "TOC evidence" in result.stderr
    assert not out.exists()


@pytest.mark.parametrize("pages", [
    [{"html": "<p>Missing identity.</p>"}],
    [{"page": 0, "html": "<p>Zero.</p>"}],
    [{"page": -1, "html": "<p>Negative.</p>"}],
    [{"page": True, "html": "<p>Boolean.</p>"}],
    [{"page": "1", "html": "<p>String.</p>"}],
    [{"page": 1.5, "html": "<p>Fraction.</p>"}],
    [{"page_number": 0, "page": 1, "html": "<p>Invalid authoritative identity.</p>"}],
    [{"page": 1, "html": "<p>First.</p>"}, {"page_number": 1, "html": "<p>Duplicate.</p>"}],
    [None],
    [["not", "an", "object"]],
    [{"page": 1, "html": "<p>Failed.</p>", "error": "OCR failed"}],
])
def test_fallback_refuses_invalid_rows_or_source_identity(tmp_path: Path, pages: list) -> None:
    result, out = _run_toc(tmp_path, pages, "--fallback-mode", "single-document")
    assert result.returncode != 0
    assert any(message in result.stderr for message in [
        "source page identity", "must be an object", "contains a producer error",
    ])
    assert not out.exists()


def test_fallback_does_not_replace_valid_authored_toc(tmp_path: Path) -> None:
    pages = [
        {"page": 1, "html": "<h1>Contents</h1><p>Parent ........ 10</p><p>Next ........ 20</p>"},
        {"page": 2, "printed_page_number": 10, "html": "<h1>Parent</h1>"},
        {"page": 3, "printed_page_number": 15, "html": "<h1>Internal subsection</h1>"},
        {"page": 4, "printed_page_number": 20, "html": "<h1>Next</h1>"},
    ]
    result, out = _run_toc(tmp_path, pages, "--min-entries", "2", "--fallback-mode", "single-document")
    assert result.returncode == 0, result.stderr
    rows = [json.loads(line) for line in out.read_text().splitlines()]
    assert [row["title"] for row in rows] == ["Parent", "Next"]
    assert all(row["notes"] == "toc-derived" for row in rows)
    assert (rows[0]["page_start"], rows[0]["page_end"]) == (10, 19)


def test_toc_portionizer_uses_book_authored_boundaries(tmp_path: Path) -> None:
    pages_path = tmp_path / "pages.jsonl"
    out_path = tmp_path / "portions.jsonl"

    _write_jsonl(
        pages_path,
        [
            {
                "page_number": 8,
                "printed_page_number": None,
                "html": (
                    "<p>INDEX</p>"
                    "<p>Parent Chapter ................................ 26</p>"
                    "<p>Next Chapter .................................. 37</p>"
                ),
            },
            {
                "page_number": 26,
                "printed_page_number": 26,
                "html": "<h1>PARENT CHAPTER</h1><p>Start.</p>",
            },
            {
                "page_number": 32,
                "printed_page_number": 32,
                "html": "<h1>CHILD SUBSECTION</h1><p>Internal heading only.</p>",
            },
            {
                "page_number": 37,
                "printed_page_number": 37,
                "html": "<h1>NEXT CHAPTER</h1><p>Next start.</p>",
            },
            {
                "page_number": 40,
                "printed_page_number": 40,
                "html": "<p>Tail page.</p>",
            },
        ],
    )

    cmd = [
        sys.executable,
        "-m",
        "modules.portionize.portionize_toc_html_v1.main",
        "--pages",
        str(pages_path),
        "--out",
        str(out_path),
        "--min-entries",
        "2",
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    assert result.returncode == 0, result.stderr

    rows = [json.loads(line) for line in out_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert [row["title"] for row in rows] == ["Parent Chapter", "Next Chapter"]
    assert rows[0]["page_start"] == 26
    assert rows[0]["page_end"] == 36
    assert rows[1]["page_start"] == 37
    assert rows[1]["page_end"] == 40


def test_toc_portionizer_accepts_heading_plus_table_index(tmp_path: Path) -> None:
    pages_path = tmp_path / "pages-table.jsonl"
    out_path = tmp_path / "portions-table.jsonl"

    _write_jsonl(
        pages_path,
        [
            {
                "page_number": 8,
                "printed_page_number": None,
                "html": (
                    "<h1>INDEX</h1>"
                    "<table><tbody>"
                    "<tr><td>First Chapter</td><td>10</td></tr>"
                    "<tr><td>Second Chapter</td><td>20</td></tr>"
                    "</tbody></table>"
                ),
            },
            {
                "page_number": 10,
                "printed_page_number": 10,
                "html": "<h1>FIRST CHAPTER</h1><p>Start.</p>",
            },
            {
                "page_number": 20,
                "printed_page_number": 20,
                "html": "<h1>SECOND CHAPTER</h1><p>Next start.</p>",
            },
            {
                "page_number": 24,
                "printed_page_number": 24,
                "html": "<p>Tail page.</p>",
            },
        ],
    )

    cmd = [
        sys.executable,
        "-m",
        "modules.portionize.portionize_toc_html_v1.main",
        "--pages",
        str(pages_path),
        "--out",
        str(out_path),
        "--min-entries",
        "2",
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    assert result.returncode == 0, result.stderr

    rows = [json.loads(line) for line in out_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert [row["title"] for row in rows] == ["First Chapter", "Second Chapter"]
    assert rows[0]["page_start"] == 10
    assert rows[0]["page_end"] == 19
    assert rows[1]["page_start"] == 20
    assert rows[1]["page_end"] == 24


def test_toc_portionizer_rejects_non_toc_tables_without_heading(tmp_path: Path) -> None:
    pages_path = tmp_path / "pages-mixed.jsonl"
    out_path = tmp_path / "portions-mixed.jsonl"

    _write_jsonl(
        pages_path,
        [
            {
                "page_number": 8,
                "printed_page_number": None,
                "html": (
                    "<h1>INDEX</h1>"
                    "<table><tbody>"
                    "<tr><td>Arthur</td><td>26</td></tr>"
                    "<tr><td>Leonidas</td><td>37</td></tr>"
                    "</tbody></table>"
                ),
            },
            {
                "page_number": 26,
                "printed_page_number": 26,
                "html": (
                    "<h1>Arthur's Grandchildren</h1>"
                    "<table><tbody>"
                    "<tr><td>Crystal</td><td>Sept. 18, 1974</td></tr>"
                    "<tr><td>Michel</td><td>Apr. 28, 1976</td></tr>"
                    "<tr><td>Joel</td><td>Sept. 8, 1981</td></tr>"
                    "</tbody></table>"
                ),
            },
            {
                "page_number": 37,
                "printed_page_number": 37,
                "html": "<h1>LEONIDAS L'HEUREUX</h1><p>Next start.</p>",
            },
            {
                "page_number": 45,
                "printed_page_number": 45,
                "html": "<p>Tail page.</p>",
            },
        ],
    )

    cmd = [
        sys.executable,
        "-m",
        "modules.portionize.portionize_toc_html_v1.main",
        "--pages",
        str(pages_path),
        "--out",
        str(out_path),
        "--min-entries",
        "2",
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    assert result.returncode == 0, result.stderr

    rows = [json.loads(line) for line in out_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert [row["title"] for row in rows] == ["Arthur", "Leonidas"]
    assert all(row["page_start"] < 100 for row in rows)
