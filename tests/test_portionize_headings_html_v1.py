import json
import subprocess
import sys
from pathlib import Path


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def _run_portionizer(tmp_path: Path, pages: list[dict], *extra_args: str) -> list[dict]:
    pages_path = tmp_path / "pages.jsonl"
    out_path = tmp_path / "portions.jsonl"
    _write_jsonl(pages_path, pages)

    cmd = [
        sys.executable,
        "-m",
        "modules.portionize.portionize_headings_html_v1.main",
        "--pages",
        str(pages_path),
        "--out",
        str(out_path),
        *extra_args,
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    assert result.returncode == 0, result.stderr
    return [
        json.loads(line)
        for line in out_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_heading_portionizer_emits_source_page_ranges_for_unnumbered_boundaries(tmp_path: Path) -> None:
    rows = _run_portionizer(
        tmp_path,
        [
            {"page_number": 1, "printed_page_number": None, "html": "<h1>Overview</h1><p>Start.</p>"},
            {"page_number": 2, "printed_page_number": None, "html": "<p>More overview.</p>"},
            {"page_number": 3, "printed_page_number": None, "html": "<h1>Details</h1><p>Detail page.</p>"},
        ],
        "--allow-unnumbered",
    )

    assert [row["title"] for row in rows] == ["Overview", "Details"]
    assert rows[0]["page_start"] == 1
    assert rows[0]["page_end"] == 2
    assert rows[0]["source_pages"] == [1, 2]
    assert rows[0]["notes"] == "heading-derived-source-pages"
    assert rows[1]["page_start"] == 3
    assert rows[1]["page_end"] == 3
    assert rows[1]["source_pages"] == [3]


def test_heading_portionizer_can_fallback_to_single_document(tmp_path: Path) -> None:
    rows = _run_portionizer(
        tmp_path,
        [
            {"page_number": 1, "printed_page_number": None, "html": "<p>Letter opening.</p>"},
            {"page_number": 2, "printed_page_number": None, "html": "<p>Letter closing.</p>"},
        ],
        "--allow-unnumbered",
        "--fallback-mode",
        "single-document",
        "--fallback-title",
        "Flat Document",
    )

    assert len(rows) == 1
    assert rows[0]["portion_id"] == "document"
    assert rows[0]["title"] == "Flat Document"
    assert rows[0]["page_start"] == 1
    assert rows[0]["page_end"] == 2
    assert rows[0]["source_pages"] == [1, 2]
    assert rows[0]["notes"] == "single-document-fallback"
