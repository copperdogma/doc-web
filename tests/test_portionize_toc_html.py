import json
import subprocess
import sys
from pathlib import Path


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


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
