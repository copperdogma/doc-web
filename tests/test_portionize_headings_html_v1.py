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


def test_heading_portionizer_can_suppress_lower_catalog_item_boundaries(tmp_path: Path) -> None:
    rows = _run_portionizer(
        tmp_path,
        [
            {
                "page_number": 1,
                "printed_page_number": 1,
                "html": "<h1>CATALOG</h1><p>Intro.</p>",
            },
            {
                "page_number": 2,
                "printed_page_number": 2,
                "html": (
                    "<h2>ADVANCED COURSES</h2>"
                    "<p>FIRST ENTRY Game Length: Medium Boards: A Special Rules: None</p>"
                ),
            },
            {
                "page_number": 3,
                "printed_page_number": 3,
                "html": (
                    "<h2>EXTRA CRISPY</h2>"
                    "<p>Game Length: Short Boards: Start A Special Rules: Continue the previous category.</p>"
                    "<h2>BURN RUN</h2>"
                    "<p>Game Length: Long Boards: Start B Special Rules: None</p>"
                ),
            },
            {
                "page_number": 4,
                "printed_page_number": 4,
                "html": "<h1>CARD INDEX</h1><p>Next top-level section.</p>",
            },
        ],
        "--heading-tags",
        "h1,h2",
        "--suppress-lower-heading-item-boundaries",
    )

    assert [row["title"] for row in rows] == ["CATALOG", "ADVANCED COURSES", "CARD INDEX"]
    assert rows[1]["source_heading_tag"] == "h2"
    assert rows[1]["source_pages"] == [2, 3]
    assert rows[1]["page_start"] == 2
    assert rows[1]["page_end"] == 3


def test_heading_portionizer_can_merge_catalog_subsections(tmp_path: Path) -> None:
    rows = _run_portionizer(
        tmp_path,
        [
            {
                "page_number": 1,
                "printed_page_number": 1,
                "raw_html": (
                    "<h1>ROUTE CATALOG</h1>"
                    "<p>On the following pages, you will find a list of routes.</p>"
                ),
                "html": (
                    "<h1>ROUTE CATALOG</h1>"
                    "<p>On the following pages, you will find a list of routes.</p>"
                ),
            },
            {
                "page_number": 2,
                "printed_page_number": 2,
                "raw_html": "<p class='running-head'>ROUTE CATALOG</p><h1>EASY ROUTES</h1><h2>RIVER WALK</h2>",
                "html": "<h1>EASY ROUTES</h1><h2>RIVER WALK</h2>",
            },
            {
                "page_number": 3,
                "printed_page_number": 3,
                "raw_html": "<p class='running-head'>ROUTE CATALOG</p><h1>HARD ROUTES</h1><h2>RIDGE RUN</h2>",
                "html": "<h1>HARD ROUTES</h1><h2>RIDGE RUN</h2>",
            },
            {
                "page_number": 4,
                "printed_page_number": 4,
                "raw_html": "<h1>SAFETY NOTES</h1><p>Next section.</p>",
                "html": "<h1>SAFETY NOTES</h1><p>Next section.</p>",
            },
        ],
        "--heading-tags",
        "h1,h2",
        "--merge-catalog-subsections",
    )

    assert [row["title"] for row in rows] == ["ROUTE CATALOG", "SAFETY NOTES"]
    assert rows[0]["source_pages"] == [1, 2, 3]
    assert rows[0]["page_start"] == 1
    assert rows[0]["page_end"] == 3


def test_heading_portionizer_can_merge_procedural_subsections(tmp_path: Path) -> None:
    rows = _run_portionizer(
        tmp_path,
        [
            {
                "page_number": 1,
                "printed_page_number": 1,
                "raw_html": (
                    "<h1>HOW TO PLAY</h1>"
                    "<p>This section explains a full round. A detailed description of each phase "
                    "starts on the following pages.</p>"
                ),
                "html": (
                    "<h1>HOW TO PLAY</h1>"
                    "<p>This section explains a full round. A detailed description of each phase "
                    "starts on the following pages.</p>"
                ),
            },
            {
                "page_number": 2,
                "printed_page_number": 2,
                "raw_html": "<p class='running-head'>HOW TO PLAY</p><h1>PLAYING A ROUND</h1>",
                "html": "<h1>PLAYING A ROUND</h1>",
            },
            {
                "page_number": 3,
                "printed_page_number": 3,
                "raw_html": "<p class='running-head'>HOW TO PLAY</p><h2>The Programming Phase</h2>",
                "html": "<h2>The Programming Phase</h2>",
            },
            {
                "page_number": 4,
                "printed_page_number": 4,
                "raw_html": (
                    "<p class='running-head'>HOW TO PLAY</p>"
                    "<h2>Activation order for Board Elements and Robot Lasers</h2>"
                ),
                "html": "<h2>Activation order for Board Elements and Robot Lasers</h2>",
            },
            {
                "page_number": 5,
                "printed_page_number": 5,
                "raw_html": "<p class='running-head'>HOW TO PLAY</p><h2>Summary of a Round</h2>",
                "html": "<h2>Summary of a Round</h2>",
            },
            {
                "page_number": 6,
                "printed_page_number": 6,
                "raw_html": "<h1>MORE ON RACING THROUGH THE FACTORY</h1><p>New topic.</p>",
                "html": "<h1>MORE ON RACING THROUGH THE FACTORY</h1><p>New topic.</p>",
            },
        ],
        "--heading-tags",
        "h1,h2",
        "--merge-procedural-subsections",
    )

    assert [row["title"] for row in rows] == ["HOW TO PLAY", "MORE ON RACING THROUGH THE FACTORY"]
    assert rows[0]["source_pages"] == [1, 2, 3, 4, 5]
    assert rows[0]["page_start"] == 1
    assert rows[0]["page_end"] == 5
