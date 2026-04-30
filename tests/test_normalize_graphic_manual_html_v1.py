from __future__ import annotations

from modules.transform.normalize_graphic_manual_html_v1.main import normalize_rows


def test_promotes_unique_leading_running_head_when_page_has_no_existing_title() -> None:
    rows = [
        {"page_number": 1, "html": '<h1>Intro</h1><p>Body</p>'},
        {"page_number": 2, "html": '<p class="running-head">SET UP</p><ol><li>Choose a course.</li></ol>'},
    ]

    normalized, report = normalize_rows(rows)

    assert '<h1 class="semantic-running-head" data-normalized-from="running-head">SET UP</h1>' in normalized[1]["html"]
    assert report["summary"]["promoted_running_heads"] == 1


def test_removes_running_head_that_matches_existing_heading_elsewhere() -> None:
    rows = [
        {"page_number": 1, "html": "<h1>HOW TO PLAY</h1><p>Overview.</p>"},
        {"page_number": 2, "html": '<p class="running-head">HOW TO PLAY</p><h2>The Programming Phase</h2><p>Rules.</p>'},
    ]

    normalized, report = normalize_rows(rows)

    assert "running-head" not in normalized[1]["html"]
    assert "HOW TO PLAY" not in normalized[1]["html"]
    assert "<h2>The Programming Phase</h2>" in normalized[1]["html"]
    assert report["decisions"][0]["reason"] == "matches_existing_heading"


def test_removes_repeated_running_head_chrome() -> None:
    rows = [
        {"page_number": 1, "html": '<p class="running-head">CARDS</p><h1>Card Index</h1>'},
        {"page_number": 2, "html": '<p class="running-head">CARDS</p><p>Continued entries.</p>'},
        {"page_number": 3, "html": '<p class="running-head">CARDS</p><p>More entries.</p>'},
    ]

    normalized, report = normalize_rows(rows, max_promoted_running_head_occurrences=2)

    assert all("running-head" not in row["html"] for row in normalized)
    assert report["summary"]["promoted_running_heads"] == 0
    assert report["summary"]["removed_running_heads"] == 3
