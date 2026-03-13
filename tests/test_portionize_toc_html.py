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
