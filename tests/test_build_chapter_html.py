"""Tests for build_chapter_html_v1 — HTML5 structure, image integration, navigation."""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import modules.build.build_chapter_html_v1.main as build_main
from bs4 import BeautifulSoup
from schemas import DocWebBundleManifest, DocWebProvenanceBlock

from modules.build.build_chapter_html_v1.main import (
    _attach_images,
    _finalize_genealogy_body_html,
    _group_manifest_by_page,
    _is_likely_caption,
    _html5_wrap,
    _add_table_scope,
    _build_nav,
    _merge_genealogy_tables_preserving_headings,
    _merge_contiguous_genealogy_tables,
    _normalize_heading_breaks,
    _normalize_catalog_entries,
    _polish_flat_chapter_headings,
    _normalize_reference_entries,
    _promote_text_callout_paragraphs,
    _rebalance_repeated_generation_h1s,
    _refine_chapter_segments,
    _strip_headers_and_numbers,
    _stitch_page_breaks,
    _tag_entry_body,
    _titles_related,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_PAGE_HTML = '<p>Some text.</p><img alt="Photo"><p>More text.</p>'
SAMPLE_PAGE_HTML_MULTI = '<p>Text.</p><img alt="A"><img alt="B"><p>End.</p>'
SAMPLE_PAGE_HTML_NO_IMG = '<p>Just text, no images here.</p>'
SAMPLE_PAGE_HTML_COUNTED = '<img alt="Two photographs" data-count="2"><p>More text.</p>'
SAMPLE_PAGE_HTML_SWAPPED = (
    "<p>The ten pound bags were dyed into different colors which were then cut "
    "into squares and made into</p>"
    "<img alt=\"Photo of Leonidas and Josephine L'Heureux seated together\">"
    "<p><em>Leonidas and Josephine (second wife) L'Heureux.</em></p>"
    "<img alt=\"Oval portrait of Laetitia L'Heureux\">"
    "<p><em>Mrs. Leonidas L'Heureux (Laetitia - first wife).</em></p>"
    "<p>colorful bedspreads.</p>"
)


def _crop(filename: str, alt: str = "", image_description: str = "",
          caption_text: str = None) -> dict:
    """Helper to build a minimal crop record."""
    return {
        "filename": filename,
        "alt": alt,
        "image_description": image_description,
        "caption_text": caption_text,
        "bbox": {"x0": 0, "y0": 0, "x1": 100, "y1": 100},
        "source_page": 1,
    }


# ---------------------------------------------------------------------------
# T4: Rich alt text
# ---------------------------------------------------------------------------

class TestRichAltText:
    def test_prefers_image_description_over_alt(self):
        crops = [_crop("img.jpg", alt="Photo", image_description="Portrait of a man in uniform")]
        result = _attach_images(SAMPLE_PAGE_HTML, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        img = soup.find("img")
        assert img["alt"] == "Portrait of a man in uniform"

    def test_falls_back_to_alt_when_no_description(self):
        crops = [_crop("img.jpg", alt="Photo", image_description="")]
        result = _attach_images(SAMPLE_PAGE_HTML, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        img = soup.find("img")
        assert img["alt"] == "Photo"

    def test_empty_alt_when_nothing_available(self):
        crops = [_crop("img.jpg")]
        result = _attach_images(SAMPLE_PAGE_HTML, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        img = soup.find("img")
        assert img["alt"] == ""

    def test_integrated_diagram_callout_caption_is_not_duplicated(self):
        html = (
            '<figure><img alt="Board movement plan">'
            "<figcaption>1. Start here.<br>2. Turn right.<br>3. Move ahead.</figcaption>"
            "</figure>"
        )
        crops = [
            {
                **_crop(
                    "diagram.jpg",
                    image_description=(
                        "Board movement plan with numbered callout boxes. "
                        "1. Start here. 2. Turn right. 3. Move ahead."
                    ),
                ),
                "critical_graphics_role": "rule_example_diagram",
                "critical_graphics_importance": "essential",
                "nearby_text": "1. Start here. 2. Turn right. 3. Move ahead.",
            }
        ]

        result = _attach_images(html, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        figure = soup.find("figure")

        assert figure is not None
        assert figure.get("data-caption-deduped") == "integrated-diagram-callouts"
        assert figure.find("figcaption") is None


# ---------------------------------------------------------------------------
# T5: <figure>/<figcaption> wrapping
# ---------------------------------------------------------------------------

class TestFigureWrapping:
    def test_img_wrapped_in_figure(self):
        crops = [_crop("img.jpg")]
        result = _attach_images(SAMPLE_PAGE_HTML, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        figures = soup.find_all("figure")
        assert len(figures) == 1
        assert figures[0].find("img") is not None

    def test_figcaption_when_caption_text_present(self):
        crops = [_crop("img.jpg", caption_text="Arthur L'Heureux, circa 1942")]
        result = _attach_images(SAMPLE_PAGE_HTML, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        figcaption = soup.find("figcaption")
        assert figcaption is not None
        assert figcaption.string == "Arthur L'Heureux, circa 1942"

    def test_no_figcaption_when_no_caption(self):
        crops = [_crop("img.jpg")]
        result = _attach_images(SAMPLE_PAGE_HTML, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        assert soup.find("figcaption") is None

    def test_crop_figure_provenance_uses_crop_source_page_not_chapter_fallback(self):
        html = _attach_images(
            "<h1>Catalog</h1><p>Intro.</p><h2>Course B</h2>",
            [
                {
                    **_crop("page-002-000.jpg", alt="Course B map"),
                    "source_page": 2,
                    "critical_graphics_role": "map_or_board",
                    "importance": "essential",
                }
            ],
            "images",
        )
        body_html, rows = _tag_entry_body(
            {
                "filename": "chapter-001.html",
                "body_html": html,
                "source_pages": [1, 2],
                "source_printed_pages": [1, 2],
                "prepared_pages": [
                    {
                        "page_number": 1,
                        "printed_page_number": 1,
                        "html": "<h1>Catalog</h1><p>Intro.</p>",
                    },
                    {
                        "page_number": 2,
                        "printed_page_number": 2,
                        "html": "<h2>Course B</h2>",
                    },
                ],
            },
            run_id="test-run",
            created_at="2026-04-29T00:00:00Z",
        )

        soup = BeautifulSoup(body_html, "html.parser")
        assert soup.find("figure") is not None
        figure_row = next(row for row in rows if row["block_kind"] == "figure")
        assert figure_row["source_page_number"] == 2
        assert figure_row["source_printed_page_number"] == 2
        assert "crop:page-002-000.jpg" in figure_row["source_element_ids"]

    def test_multiple_images_each_get_figure(self):
        crops = [_crop("a.jpg", caption_text="Cap A"), _crop("b.jpg")]
        result = _attach_images(SAMPLE_PAGE_HTML_MULTI, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        figures = soup.find_all("figure")
        assert len(figures) == 2
        # First has caption, second doesn't
        captions = soup.find_all("figcaption")
        assert len(captions) == 1
        assert captions[0].string == "Cap A"


def test_split_labeled_multi_image_figures_uses_nearby_text_anchors() -> None:
    soup = BeautifulSoup(
        """
        <article>
          <ol>
            <li><p>Each player takes a figure and places that robot on one of the starting positions.</p></li>
          </ol>
          <figure>
            <img src="images/page-003-001.jpg" data-crop-filename="page-003-001.jpg"
                 data-critical-graphics-role="setup_diagram"
                 data-critical-graphics-importance="essential"
                 data-critical-graphics-nearby-text="For a two-player game, place the boards as shown in this diagram."
                 alt="Two player setup diagram"/>
            <img src="images/page-003-000.jpg" data-crop-filename="page-003-000.jpg"
                 data-critical-graphics-role="setup_diagram"
                 data-critical-graphics-importance="essential"
                 data-critical-graphics-nearby-text="Each player takes a figure and places that robot on one of the starting positions."
                 alt="Starting positions graphic"/>
          </figure>
          <p>For a two-player game, place the boards as shown in this diagram.</p>
        </article>
        """,
        "html.parser",
    )

    assert build_main._split_labeled_multi_image_figures(soup) == 2

    starting_img = soup.find("img", {"data-crop-filename": "page-003-000.jpg"})
    setup_img = soup.find("img", {"data-crop-filename": "page-003-001.jpg"})
    list_item = soup.find("li")
    setup_text = soup.find("p", string=re.compile("For a two-player game"))
    assert starting_img.find_parent("li") is list_item
    assert setup_img.find_parent("figure") is setup_text.find_previous_sibling("figure")
    assert not any(len(fig.find_all("img", recursive=False)) > 1 for fig in soup.find_all("figure"))


def test_split_labeled_multi_image_figures_refreshes_remaining_figure_metadata() -> None:
    soup = BeautifulSoup(
        """
        <article>
          <p>Place robots on the starting positions.</p>
          <figure data-doc-web-source-crop-filename="start.jpg" data-critical-graphics-target-id="start">
            <img src="images/start.jpg" data-crop-filename="start.jpg"
                 data-critical-graphics-target-id="start"
                 data-critical-graphics-role="board_element"
                 data-critical-graphics-importance="essential"
                 data-critical-graphics-nearby-text="Place robots on the starting positions."
                 alt="Starting positions"/>
            <img src="images/setup.jpg" data-crop-filename="setup.jpg"
                 data-critical-graphics-target-id="setup"
                 data-critical-graphics-role="setup_diagram"
                 data-critical-graphics-importance="essential"
                 data-critical-graphics-nearby-text="Two-player setup overview."
                 alt="Setup overview"/>
          </figure>
        </article>
        """,
        "html.parser",
    )

    assert build_main._split_labeled_multi_image_figures(soup) == 1

    remaining = soup.find("img", {"data-crop-filename": "setup.jpg"}).find_parent("figure")
    assert remaining["data-doc-web-source-crop-filename"] == "setup.jpg"
    assert remaining["data-critical-graphics-target-id"] == "setup"
    assert remaining["data-critical-graphics-role"] == "setup_diagram"


def test_split_labeled_multi_image_figure_extends_anchor_through_nearby_text_run() -> None:
    soup = BeautifulSoup(
        """
        <article>
          <p>To purchase an upgrade, look at the number in the top left-hand corner of the card.</p>
          <p>If you've purchased a permanent upgrade, place it on one of the upgrade slots on your player mat.</p>
          <p>If you've purchased a temporary upgrade, place it in front of your player mat.</p>
          <figure>
            <img src="images/cost.png" data-crop-filename="cost.png"
                 data-critical-graphics-role="rule_example_diagram"
                 data-critical-graphics-importance="essential"
                 data-critical-graphics-nearby-text="To purchase an upgrade, look at the number in the top left-hand corner of the card."
                 alt="Cost reference card"/>
            <img src="images/layout.png" data-crop-filename="layout.png"
                 data-critical-graphics-role="rule_example_diagram"
                 data-critical-graphics-importance="essential"
                 data-critical-graphics-nearby-text="If you've purchased a permanent upgrade, place it on one of the upgrade slots on your player mat. If you've purchased a temporary upgrade, place it in front of your player mat."
                 alt="Card placement layout visual"/>
          </figure>
        </article>
        """,
        "html.parser",
    )

    assert build_main._split_labeled_multi_image_figures(soup) == 2

    layout = soup.find("img", {"data-crop-filename": "layout.png"}).find_parent("figure")
    previous = layout.find_previous_sibling("p")

    assert "temporary upgrade" in previous.get_text(" ", strip=True)


def test_redundant_page_snapshot_crop_is_skipped_when_page_text_is_semantic() -> None:
    soup = BeautifulSoup(
        "<article><p>"
        + " ".join(f"semantic token {idx}" for idx in range(60))
        + "</p></article>",
        "html.parser",
    )
    crop = {
        "filename": "page-002-000.jpg",
        "area_ratio": 0.99,
        "image_description": "Large page snapshot",
    }

    assert build_main._should_skip_source_pixel_crop(crop, soup)


def test_multiple_figures_inserted_at_same_anchor_keep_manifest_order() -> None:
    html = "<article><p>Luis programmed a card and moves forward one space.</p></article>"
    crops = [
        {
            **_crop(
                "mat.jpg",
                image_description="Luis player mat showing the programmed card",
            ),
            "critical_graphics_role": "rule_example_diagram",
            "critical_graphics_importance": "essential",
            "nearby_text": "Luis programmed a card and moves forward one space.",
        },
        {
            **_crop(
                "board.jpg",
                image_description="Luis board position showing the move",
            ),
            "critical_graphics_role": "rule_example_diagram",
            "critical_graphics_importance": "essential",
            "nearby_text": "Luis programmed a card and moves forward one space.",
        },
    ]

    result = _attach_images(html, crops, "images")
    soup = BeautifulSoup(result, "html.parser")

    assert [img["src"] for img in soup.find_all("img")] == ["images/mat.jpg", "images/board.jpg"]


def test_orphan_crop_covering_contiguous_paragraphs_inserts_after_text_run() -> None:
    html = """
    <article>
      <p>To purchase an upgrade, look at the number in the top left-hand corner of the card.</p>
      <p>If you've purchased a permanent upgrade, place it on one of the upgrade slots on your player mat.</p>
      <p>If you've purchased a temporary upgrade, place it in front of your player mat.</p>
      <p>Then continue with the next phase.</p>
    </article>
    """
    result = _attach_images(
        html,
        [
            {
                **_crop("layout.png", image_description="Card placement layout visual"),
                "critical_graphics_role": "card_reference",
                "critical_graphics_importance": "essential",
                "nearby_text": (
                    "If you've purchased a permanent upgrade, place it on one of the upgrade slots on your player mat. "
                    "If you've purchased a temporary upgrade, place it in front of your player mat."
                ),
            }
        ],
        "images",
    )
    soup = BeautifulSoup(result, "html.parser")

    figure = soup.find("img", {"data-crop-filename": "layout.png"}).find_parent("figure")
    previous = figure.find_previous_sibling("p")
    following = figure.find_next_sibling("p")

    assert "temporary upgrade" in previous.get_text(" ", strip=True)
    assert "Then continue" in following.get_text(" ", strip=True)


def test_candidate_titles_for_refinement_excludes_future_duplicate_boundaries() -> None:
    portions = [
        {"title": "HOW TO PLAY", "page_start": 4, "page_end": 11},
        {"title": "MORE ON RACING THROUGH THE FACTORY", "page_start": 12, "page_end": 13},
        {"title": "SUMMARY OF A ROUND", "page_start": 32, "page_end": 32},
    ]

    assert build_main._candidate_titles_for_refinement(portions, 0, 11) == ["HOW TO PLAY"]


# ---------------------------------------------------------------------------
# Caption heuristic detection (Story 009)
# ---------------------------------------------------------------------------

class TestCaptionHeuristic:
    """Test _is_likely_caption for identifying caption text near images."""

    def test_name_with_date(self):
        assert _is_likely_caption("Moise and Sophie L'Heureux about 1910")

    def test_anniversary_caption(self):
        assert _is_likely_caption("Henry and Alma Alain on their 50th wedding anniversary in 1957.")

    def test_family_name(self):
        assert _is_likely_caption("Moise and Sophie's Family")

    def test_row_label(self):
        assert _is_likely_caption("Back Row: George, Marie Louise, Father Cochin")

    def test_circa(self):
        assert _is_likely_caption("Arthur L'Heureux, circa 1942")

    def test_left_to_right(self):
        assert _is_likely_caption("Left to right: Arthur, Marie, Sophie")

    def test_generic_prose_rejected(self):
        assert not _is_likely_caption("More text.")

    def test_narrative_opener_rejected(self):
        assert not _is_likely_caption("The family moved west in the spring of that year.")

    def test_long_text_rejected(self):
        assert not _is_likely_caption("This is a very long paragraph that goes on and on "
                                      "and on with many many words exceeding the caption limit "
                                      "which should not be treated as a caption")

    def test_empty_string(self):
        assert not _is_likely_caption("")

    def test_single_lowercase_word(self):
        assert not _is_likely_caption("hello")


class TestCaptionAbsorption:
    """Test that _attach_images absorbs adjacent caption <p> tags."""

    def test_absorbs_caption_with_date(self):
        html = '<img alt="Photo"><p>Moise and Sophie about 1910</p><p>Regular paragraph.</p>'
        crops = [_crop("img.jpg")]
        result = _attach_images(html, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        figcaption = soup.find("figcaption")
        assert figcaption is not None
        assert "1910" in figcaption.get_text()
        # Regular paragraph should NOT be absorbed
        remaining_p = soup.find_all("p")
        assert any("Regular paragraph" in p.get_text() for p in remaining_p)

    def test_does_not_absorb_narrative(self):
        html = '<img alt="Photo"><p>The family moved west after the war.</p>'
        crops = [_crop("img.jpg")]
        result = _attach_images(html, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        assert soup.find("figcaption") is None

    def test_crop_caption_takes_priority(self):
        """When crop pipeline provides caption_text, use it over heuristic."""
        html = '<img alt="Photo"><p>Moise L\'Heureux 1910</p>'
        crops = [_crop("img.jpg", caption_text="VLM-provided caption")]
        result = _attach_images(html, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        figcaption = soup.find("figcaption")
        assert figcaption is not None
        assert figcaption.string == "VLM-provided caption"

    def test_existing_figure_preserved(self):
        """New OCR format: <figure> already wraps <img>. Don't double-wrap."""
        html = '<figure><img alt="Photo"><figcaption>Existing caption</figcaption></figure>'
        crops = [_crop("img.jpg")]
        result = _attach_images(html, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        figures = soup.find_all("figure")
        assert len(figures) == 1
        figcaption = soup.find("figcaption")
        assert figcaption is not None
        assert "Existing caption" in figcaption.get_text()

    def test_existing_figure_gets_crop_caption(self):
        """<figure> without <figcaption> gets caption from crop pipeline."""
        html = '<figure><img alt="Photo"></figure>'
        crops = [_crop("img.jpg", caption_text="From crop pipeline")]
        result = _attach_images(html, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        figcaption = soup.find("figcaption")
        assert figcaption is not None
        assert figcaption.string == "From crop pipeline"

    def test_existing_figure_gets_critical_graphics_metadata(self):
        html = '<figure><img alt="Upgrade card"></figure>'
        crops = [{
            **_crop("card.jpg", image_description="Upgrade card face for Test Card"),
            "critical_graphics_role": "card_face",
            "critical_graphics_importance": "essential",
            "critical_graphics_target_id": "p001-g01",
        }]

        result = _attach_images(html, crops, "images")
        soup = BeautifulSoup(result, "html.parser")

        figure = soup.find("figure")
        assert figure["data-critical-graphics-role"] == "card_face"
        assert figure["data-critical-graphics-importance"] == "essential"
        assert figure["data-critical-graphics-target-id"] == "p001-g01"

    def test_removes_unmatched_image_placeholders(self):
        html = '<figure><img alt="Diagram"><img alt="Duplicate placeholder"></figure>'
        crops = [_crop("img.jpg", image_description="Diagram crop")]

        result = _attach_images(html, crops, "images")
        soup = BeautifulSoup(result, "html.parser")

        imgs = soup.find_all("img")
        assert len(imgs) == 1
        assert imgs[0]["src"] == "images/img.jpg"

    def test_dedupes_caption_matching_adjacent_heading(self):
        html = (
            '<figure><img alt="Priority antenna"><figcaption>Determining Priority</figcaption></figure>'
            '<p><strong>Determining Priority</strong><br>Priority determines the next player.</p>'
        )
        crops = [_crop("img.jpg", image_description="Priority antenna")]

        result = _attach_images(html, crops, "images")
        soup = BeautifulSoup(result, "html.parser")

        assert soup.find("figcaption") is None
        assert soup.find("figure")["data-caption-deduped"] == "adjacent-text"

    def test_suppresses_adjacent_duplicate_paragraphs_for_text_bearing_crop(self, monkeypatch):
        html = (
            '<figure><img alt="Official Seal"></figure>'
            '<p>Hon. Gordon MacMurchy<br>Minister of Agriculture</p>'
            '<p>Hon. Ed Tchorzewski<br>Minister-in-charge of<br>Celebrate Saskatchewan</p>'
            '<p>Regular paragraph.</p>'
        )
        crops = [{
            **_crop("img.jpg", alt="Official Seal"),
            "contains_text": True,
            "_source_path": "/tmp/fake-crop.jpg",
        }]
        monkeypatch.setattr(
            build_main,
            "_ocr_crop_text",
            lambda _: (
                "Hon. Gordon MacMurchy Minister of Agriculture "
                "Hon. Ed Tchorzewski Minister-in-charge of Celebrate Saskatchewan"
            ),
        )
        result = _attach_images(html, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        assert paragraphs == ["Regular paragraph."]
        figure = soup.find("figure")
        assert figure is not None
        assert figure["data-text-dedup-source"] == "crop-ocr"

    def test_keeps_adjacent_paragraph_when_crop_ocr_does_not_match(self, monkeypatch):
        html = '<figure><img alt="Official Seal"></figure><p>Hon. Gordon MacMurchy<br>Minister of Agriculture</p>'
        crops = [{
            **_crop("img.jpg", alt="Official Seal"),
            "contains_text": True,
            "_source_path": "/tmp/fake-crop.jpg",
        }]
        monkeypatch.setattr(build_main, "_ocr_crop_text", lambda _: "Official seal only")
        result = _attach_images(html, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        assert paragraphs == ["Hon. Gordon MacMurchy Minister of Agriculture"]


def test_normalize_reference_entries_converts_card_like_strong_paragraphs() -> None:
    html = (
        "<p><strong>CACHE MEMORY</strong><br>"
        "<strong>Cost:</strong> 4<br>"
        "<strong>Effect:</strong> You may discard cards.</p>"
    )

    result = _normalize_reference_entries(html, enabled=True)
    soup = BeautifulSoup(result, "html.parser")

    assert soup.find("dl", class_="semantic-entry-list") is not None
    assert soup.find("dt").get_text(" ", strip=True) == "CACHE MEMORY"
    assert "Effect:" in soup.find("dd").get_text(" ", strip=True)


def test_normalize_reference_entries_rejects_phase_label_paragraph() -> None:
    html = "<p><strong>The Upgrade Phase:</strong> Use energy cubes.</p>"

    assert _normalize_reference_entries(html, enabled=True) == html


def test_normalize_reference_entries_converts_figure_labeled_card_entries() -> None:
    html = (
        '<figure><img src="images/card.jpg" alt="Energy Routine"></figure>'
        "<p>ENERGY ROUTINE</p>"
        "<p>Take one energy cube, and place it on your player mat.</p>"
    )

    result = _normalize_reference_entries(html, enabled=True)
    soup = BeautifulSoup(result, "html.parser")

    assert soup.find("figure") is not None
    assert soup.find("dt").get_text(" ", strip=True) == "ENERGY ROUTINE"
    assert "Take one energy cube" in soup.find("dd").get_text(" ", strip=True)


def test_normalize_reference_entries_converts_label_before_figure_card_entries() -> None:
    html = (
        "<p>ENERGY ROUTINE</p>"
        '<figure><img src="images/card.jpg" alt="Energy Routine"></figure>'
        "<p>Take one energy cube, and place it on your player mat.</p>"
        "<p>SANDBOX ROUTINE</p>"
    )

    result = _normalize_reference_entries(html, enabled=True)
    soup = BeautifulSoup(result, "html.parser")

    assert soup.find("dt").get_text(" ", strip=True) == "ENERGY ROUTINE"
    assert "Take one energy cube" in soup.find("dd").get_text(" ", strip=True)
    assert soup.find("p", string="SANDBOX ROUTINE") is not None


def test_normalize_catalog_entries_groups_mixed_figure_label_metadata_patterns() -> None:
    html = (
        "<h1>ROUTE CATALOG</h1>"
        "<p>On the following pages, find a list of routes.</p>"
        "<h2>EASY ROUTES</h2>"
        '<figure data-critical-graphics-role="map_or_board"><img src="images/a.jpg" alt="River Walk — Game Length: Short; Boards: A"></figure>'
        "<h3>RIVER WALK</h3>"
        "<p><strong>Game Length:</strong> Short<br><strong>Boards:</strong> A</p>"
        "<dl class=\"semantic-entry-list\"><dt>RIDGE WALK</dt><dd><strong>Game Length:</strong> Long<br><strong>Boards:</strong> B</dd></dl>"
        '<figure data-critical-graphics-role="map_or_board"><img src="images/b.jpg" alt="Ridge Walk"></figure>'
        "<p><strong>CLIFF LOOP</strong></p>"
        '<figure data-critical-graphics-role="map_or_board"><img src="images/c.jpg" alt="Cliff Loop"></figure>'
        "<p><strong>Game Length:</strong> Medium<br><strong>Boards:</strong> C</p>"
        "<h3>PEAK PASS</h3>"
        '<figure data-critical-graphics-role="map_or_board"><img src="images/d.jpg" alt="Peak Pass"></figure>'
        "<p><strong>Game Length:</strong> Short<br><strong>Boards:</strong> D</p>"
    )

    result = _normalize_catalog_entries(html, title="ROUTE CATALOG", enabled=True)
    soup = BeautifulSoup(result, "html.parser")
    entries = soup.find_all("section", class_="semantic-catalog-entry")

    assert [entry.find("h3").get_text(" ", strip=True) for entry in entries] == [
        "RIVER WALK",
        "RIDGE WALK",
        "CLIFF LOOP",
        "PEAK PASS",
    ]
    assert [entry.find("img")["src"] for entry in entries] == [
        "images/a.jpg",
        "images/b.jpg",
        "images/c.jpg",
        "images/d.jpg",
    ]
    assert all("Game Length:" in entry.get_text(" ", strip=True) for entry in entries)
    assert not soup.find("dt", string="RIDGE WALK")


def test_normalize_catalog_entries_keeps_reference_panel_at_category_level() -> None:
    html = (
        "<h1>CARD INDEX</h1>"
        "<h2>PROGRAMMING CARDS</h2>"
        '<figure data-critical-graphics-role="card_reference">'
        '<img src="images/cards.jpg" alt="Reference images of nine card faces: Move 1, Move 2, Move 3, Turn Right, Turn Left"></figure>'
        "<h3>MOVE 1, MOVE 2, MOVE 3</h3>"
        "<p>Move your robot in the direction it is facing.</p>"
        "<dl class=\"semantic-entry-list\"><dt>TURN RIGHT</dt><dd>Turn your robot 90 degrees right.</dd></dl>"
    )

    result = _normalize_catalog_entries(html, title="CARD INDEX", enabled=True)
    soup = BeautifulSoup(result, "html.parser")

    assert soup.find("figure", attrs={"data-critical-graphics-role": "card_reference"}) is not None
    assert not soup.find("section", class_="semantic-catalog-entry")


def test_attach_images_inserts_useful_catalog_card_crops_with_exact_label_anchors() -> None:
    html = (
        "<h1>CARD INDEX</h1>"
        "<h2>UPGRADE CARDS</h2>"
        "<dl>"
        "<dt>ADMIN PRIVILEGE</dt><dd><strong>Cost:</strong> 3<br><strong>Effect:</strong> Give priority.</dd>"
        "<dt>CORRUPTION WAVE</dt><dd><strong>Cost:</strong> 4<br><strong>Effect:</strong> Move damage cards.</dd>"
        "</dl>"
    )
    crops = [
        {
            "filename": "admin.jpg",
            "image_description": "Admin Privilege permanent upgrade card face — ADMIN PRIVILEGE Cost: 3 Effect: Give priority. — card face",
            "critical_graphics_role": "card_face",
            "critical_graphics_importance": "useful",
            "critical_graphics_target_id": "p001-g01",
        },
        {
            "filename": "corruption.jpg",
            "image_description": "Corruption Wave permanent upgrade card face — CORRUPTION WAVE Cost: 4 Effect: Move damage cards. — card face",
            "critical_graphics_role": "card_face",
            "critical_graphics_importance": "useful",
            "critical_graphics_target_id": "p001-g02",
        },
    ]

    result = _attach_images(html, crops, "images")
    soup = BeautifulSoup(result, "html.parser")

    assert [img["data-crop-filename"] for img in soup.find_all("img")] == ["admin.jpg", "corruption.jpg"]
    assert soup.find("dt", string="ADMIN PRIVILEGE").find_next_sibling("dd").find("figure") is not None


def test_normalize_catalog_entries_groups_definition_list_entries_with_embedded_figures() -> None:
    html = (
        "<h1>ROUTE CATALOG</h1>"
        "<h2>EASY ROUTES</h2>"
        "<dl>"
        "<dt>RIVER WALK</dt>"
        "<dd>"
        '<figure data-critical-graphics-role="map_or_board"><img src="images/river.jpg" alt="River Walk"></figure>'
        "<strong>Distance:</strong> Short<br><strong>Difficulty:</strong> Easy"
        "</dd>"
        "<dt>RIDGE WALK</dt>"
        "<dd>"
        '<figure data-critical-graphics-role="map_or_board"><img src="images/ridge.jpg" alt="Ridge Walk"></figure>'
        "<strong>Distance:</strong> Long<br><strong>Difficulty:</strong> Medium"
        "</dd>"
        "</dl>"
    )

    result = _normalize_catalog_entries(html, title="ROUTE CATALOG", enabled=True)
    soup = BeautifulSoup(result, "html.parser")
    entries = soup.find_all("section", class_="semantic-catalog-entry")

    assert [entry["data-catalog-entry-title"] for entry in entries] == ["RIVER WALK", "RIDGE WALK"]
    assert [entry.find("img")["src"] for entry in entries] == ["images/river.jpg", "images/ridge.jpg"]
    assert all(entry.find("p") is not None for entry in entries)
    assert "Distance: Short" in entries[0].find("p").get_text(" ", strip=True)
    assert soup.find("dl") is None


def test_catalog_entry_provenance_survives_dt_dd_to_heading_paragraph_normalization() -> None:
    body_html = (
        "<section class=\"semantic-catalog-entry\" data-catalog-entry-title=\"ADMIN PRIVILEGE\">"
        "<h3>ADMIN PRIVILEGE</h3>"
        "<p><strong>Cost:</strong> 3<br><strong>Effect:</strong> Give priority.</p>"
        "</section>"
        "<section class=\"semantic-catalog-entry\" data-catalog-entry-title=\"CACHE MEMORY\">"
        "<h3>CACHE MEMORY</h3>"
        "<p><strong>Cost:</strong> 4<br><strong>Effect:</strong> Put cards on top of your deck.</p>"
        "</section>"
    )
    _, rows = _tag_entry_body(
        {
            "filename": "chapter-001.html",
            "body_html": body_html,
            "source_pages": [5, 6],
            "source_printed_pages": [5, 6],
            "prepared_pages": [
                {
                    "page_number": 5,
                    "printed_page_number": 5,
                    "html": (
                        "<dl>"
                        "<dt>ADMIN PRIVILEGE</dt>"
                        "<dd><strong>Cost:</strong> 3<br><strong>Effect:</strong> Give priority.</dd>"
                        "</dl>"
                    ),
                },
                {
                    "page_number": 6,
                    "printed_page_number": 6,
                    "html": "<p>CACHE MEMORY Cost: 4 Effect: Put cards on top of your deck.</p>",
                },
            ],
        },
        run_id="test-run",
        created_at="2026-04-29T00:00:00Z",
    )

    by_text = {row["text_quote"]: row for row in rows if row.get("text_quote")}
    assert by_text["ADMIN PRIVILEGE"]["source_page_number"] == 5
    assert by_text["Cost: 3 Effect: Give priority."]["source_page_number"] == 5
    assert by_text["CACHE MEMORY"]["source_page_number"] == 6
    assert by_text["Cost: 4 Effect: Put cards on top of your deck."]["source_page_number"] == 6


def test_normalize_catalog_entries_keeps_multi_figures_with_preceding_definition_entry() -> None:
    html = (
        "<h1>CARD INDEX</h1>"
        "<h2>PROGRAMMING CARDS</h2>"
        '<dl class="semantic-entry-list"><dt>MOVE 1, MOVE 2, MOVE 3</dt>'
        "<dd>Move your robot in the direction it is facing.</dd></dl>"
        '<figure data-critical-graphics-role="card_face"><img src="images/move1.jpg" alt="Card face titled MOVE 1"></figure>'
        '<figure data-critical-graphics-role="card_face"><img src="images/move2.jpg" alt="Card face titled MOVE 2"></figure>'
        '<figure data-critical-graphics-role="card_face"><img src="images/move3.jpg" alt="Card face titled MOVE 3"></figure>'
        '<dl class="semantic-entry-list"><dt>TURN RIGHT</dt><dd>Turn right.</dd></dl>'
        '<figure data-critical-graphics-role="card_face"><img src="images/right.jpg" alt="Card face titled TURN RIGHT"></figure>'
        '<figure data-critical-graphics-role="card_face"><img src="images/left.jpg" alt="Card face titled TURN LEFT"></figure>'
        '<dl class="semantic-entry-list"><dt>TURN LEFT</dt><dd>Turn left.</dd></dl>'
        "<h3>TURN LEFT</h3><p>Turn left.</p>"
        "<h3>U-TURN</h3><p>Turn around.</p>"
    )

    result = _normalize_catalog_entries(html, title="CARD INDEX", enabled=True)
    soup = BeautifulSoup(result, "html.parser")
    entries = soup.find_all("section", class_="semantic-catalog-entry")

    assert [entry["data-catalog-entry-title"] for entry in entries] == [
        "MOVE 1, MOVE 2, MOVE 3",
        "TURN RIGHT",
        "TURN LEFT",
    ]
    assert [img["src"] for img in entries[0].find_all("img")] == [
        "images/move1.jpg",
        "images/move2.jpg",
        "images/move3.jpg",
    ]
    assert [img["src"] for img in entries[1].find_all("img")] == ["images/right.jpg"]
    assert [img["src"] for img in entries[2].find_all("img")] == ["images/left.jpg"]


def test_polish_flat_chapter_headings_suppresses_redundant_catalog_marker_headings() -> None:
    html = (
        "<h1>CARD INDEX</h1>"
        "<h1>PROGRAMMING CARDS</h1>"
        "<h1>CARDS</h1>"
        "<dl><dt>MOVE 1</dt><dd>Move one space.</dd><dt>TURN RIGHT</dt><dd>Turn right.</dd></dl>"
        "<h1>UPGRADE CARDS</h1>"
    )

    result = _polish_flat_chapter_headings(html, "CARD INDEX")
    soup = BeautifulSoup(result, "html.parser")
    headings = [tag.get_text(" ", strip=True) for tag in soup.find_all(re.compile(r"^h[1-6]$"))]

    assert headings == ["CARD INDEX", "PROGRAMMING CARDS", "UPGRADE CARDS"]


# ---------------------------------------------------------------------------
# T3: Robust image matching
# ---------------------------------------------------------------------------

class TestImageMatching:
    def test_more_tags_than_crops(self):
        """Extra OCR placeholders should be removed so final HTML has no broken images."""
        crops = [_crop("img.jpg")]
        result = _attach_images(SAMPLE_PAGE_HTML_MULTI, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        imgs = soup.find_all("img")
        assert len(imgs) == 1
        assert imgs[0].get("src") == "images/img.jpg"

    def test_more_crops_than_tags(self):
        """Extra crops should be ignored, not crash."""
        crops = [_crop("a.jpg"), _crop("b.jpg"), _crop("c.jpg")]
        result = _attach_images(SAMPLE_PAGE_HTML, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        imgs = soup.find_all("img")
        assert len(imgs) == 1
        assert imgs[0].get("src") == "images/a.jpg"

    def test_no_crops_returns_html_unchanged(self):
        result = _attach_images(SAMPLE_PAGE_HTML, [], "images")
        assert result == SAMPLE_PAGE_HTML

    def test_no_html_returns_empty(self):
        result = _attach_images("", [_crop("img.jpg")], "images")
        assert result == ""

    def test_sets_src_and_data_attribute(self):
        crops = [_crop("photo.jpg")]
        result = _attach_images(SAMPLE_PAGE_HTML, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        img = soup.find("img")
        assert img["src"] == "images/photo.jpg"
        assert img["data-crop-filename"] == "photo.jpg"

    def test_expands_data_count_placeholders(self):
        crops = [_crop("a.jpg"), _crop("b.jpg")]
        result = _attach_images(SAMPLE_PAGE_HTML_COUNTED, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        imgs = soup.find_all("img")
        assert len(imgs) == 2
        assert imgs[0]["src"] == "images/a.jpg"
        assert imgs[1]["src"] == "images/b.jpg"

    def test_matches_crops_by_descriptor_not_manifest_order(self):
        crops = [
            _crop(
                "single.jpg",
                alt="Photo of Leonidas and Josephine L'Heureux seated together",
                image_description="Oval portrait of Laetitia L'Heureux",
            ),
            _crop(
                "couple.jpg",
                alt="Oval portrait of Laetitia L'Heureux",
                image_description="Photo of Leonidas and Josephine L'Heureux seated together",
            ),
        ]
        result = _attach_images(SAMPLE_PAGE_HTML_SWAPPED, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        figures = soup.find_all("figure")
        assert len(figures) == 2
        assert figures[0].find("img")["src"] == "images/couple.jpg"
        assert "Leonidas and Josephine" in figures[0].find("figcaption").get_text()
        assert figures[1].find("img")["src"] == "images/single.jpg"
        assert "Laetitia" in figures[1].find("figcaption").get_text()

    def test_descriptor_matching_skips_decorative_placeholder_on_dense_page(self):
        html = "".join(
            f'<figure><img alt="Upgrade card titled {name}"></figure>'
            for name in [
                "Cache Memory",
                "Defrag Gizmo",
                "Double Barrel Laser",
                "Modular Chassis",
                "Firewall",
                "Pressor Beam",
                "Rogue Code",
                "Hover Unit",
                "Rail Gun",
            ]
        )
        crops = [
            _crop("cache.jpg", image_description="Upgrade card face for Cache Memory"),
            _crop("defrag.jpg", image_description="Upgrade card face for Defrag Gizmo"),
            _crop("double.jpg", image_description="Upgrade card face for Double Barrel Laser"),
            _crop("modular.jpg", image_description="Upgrade card face for Modular Chassis"),
            _crop("firewall.jpg", image_description="Upgrade card face for Firewall"),
            _crop("pressor.jpg", image_description="Upgrade card face for Pressor Beam"),
            _crop("hover.jpg", image_description="Upgrade card face for Hover Unit"),
            _crop("rail.jpg", image_description="Upgrade card face for Rail Gun"),
        ]

        result = _attach_images(html, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        srcs = [img["src"] for img in soup.find_all("img")]

        assert "images/hover.jpg" in srcs
        assert "images/rail.jpg" in srcs
        assert all("Rogue Code" not in img.get("alt", "") for img in soup.find_all("img"))

    def test_text_only_callout_placeholder_becomes_semantic_aside_not_unrelated_crop(self):
        html = (
            '<figure><img alt="Circular reminder graphic about upgrades">'
            "<figcaption>Don’t forget! You can use upgrades during activation.</figcaption>"
            "</figure>"
        )
        crops = [_crop("belt.jpg", image_description="Blue conveyor belt board space icon")]

        result = _attach_images(html, crops, "images")
        soup = BeautifulSoup(result, "html.parser")

        assert soup.find("img") is None
        assert soup.find("figure") is None
        aside = soup.find("aside", attrs={"data-doc-web-semantic": "text-callout"})
        assert aside is not None
        assert aside["data-callout-kind"] == "reminder"
        assert aside.get_text(" ", strip=True) == "Don’t forget! You can use upgrades during activation."

    def test_text_only_callout_placeholder_uses_alt_cue_for_semantic_aside(self):
        html = (
            '<figure><img alt="Callout labeled conflict rule">'
            "<figcaption>Special Rule<br>Specific card rules override the general rules.</figcaption>"
            "</figure>"
        )
        crops = [_crop("card.jpg", image_description="Upgrade card face")]

        result = _attach_images(html, crops, "images")
        soup = BeautifulSoup(result, "html.parser")

        assert soup.find("img") is None
        assert soup.find("figure") is None
        aside = soup.find("aside", attrs={"data-doc-web-semantic": "text-callout"})
        assert aside is not None
        assert aside["data-callout-kind"] == "reminder"
        assert aside.get_text(" ", strip=True) == "Special Rule Specific card rules override the general rules."

    def test_fully_emphasized_text_callout_paragraph_becomes_semantic_aside(self):
        html = (
            "<p><strong>After the fifth register is complete, players take the programming cards "
            "in their registers and place them in their discard piles. Then play returns to the "
            "upgrade phase.</strong></p>"
        )

        soup = BeautifulSoup(html, "html.parser")
        _promote_text_callout_paragraphs(soup)

        aside = soup.find("aside", attrs={"data-doc-web-semantic": "text-callout"})
        assert aside is not None
        assert aside["data-callout-kind"] == "important"
        assert soup.find("p").get_text(" ", strip=True).startswith("After the fifth register")

    def test_text_represented_summary_reference_is_not_attached_as_image(self):
        html = (
            "<h1>Summary of a Round</h1>"
            "<ol><li>The Upgrade Phase</li><li>The Programming Phase</li>"
            "<li>The Activation Phase</li></ol>"
            '<figure><img alt="Summary panel"></figure>'
        )
        crops = [
            {
                **_crop(
                    "summary.jpg",
                    image_description=(
                        "Quick-reference panel summarizing the sequence of a round — "
                        "Summary of a Round; The Upgrade Phase; The Programming Phase; "
                        "The Activation Phase — summary reference"
                    ),
                ),
                "critical_graphics_role": "summary_reference",
                "critical_graphics_importance": "useful",
            }
        ]

        result = _attach_images(html, crops, "images")
        soup = BeautifulSoup(result, "html.parser")

        assert soup.find("img") is None
        assert soup.find("figure") is None
        assert "The Activation Phase" in soup.get_text(" ", strip=True)

    def test_unused_essential_card_crop_is_inserted_into_matching_definition(self):
        html = "<dl><dt>MEMORY STICK</dt><dd>Cost: 3<br>Effect: Draw one additional card.</dd></dl>"
        crops = [
            {
                **_crop(
                    "memory-stick.jpg",
                    image_description=(
                        "Memory Stick upgrade card face — MEMORY STICK Cost: 3 "
                        "Effect: Draw one additional card. — card face"
                    ),
                ),
                "critical_graphics_role": "card_face",
                "critical_graphics_importance": "essential",
            }
        ]

        result = _attach_images(html, crops, "images")
        soup = BeautifulSoup(result, "html.parser")

        dd = soup.find("dd")
        figure = dd.find("figure")
        assert figure is not None
        assert figure["data-placement"] == "inferred-essential"
        assert figure.find("img")["src"] == "images/memory-stick.jpg"

    def test_unused_essential_board_element_crop_is_inserted_into_matching_list_item(self):
        html = (
            "<ol>"
            "<li><p><strong>Blue conveyor belts</strong> move robots two spaces.</p></li>"
            "<li><p><strong>Green conveyor belts</strong> move robots one space.</p></li>"
            "</ol>"
        )
        crops = [
            {
                **_crop(
                    "green-belt.jpg",
                    image_description=(
                        "Green conveyor belt board space icon with activation-order marker 2 "
                        "— Green conveyor belts move robots one space. — board element"
                    ),
                ),
                "critical_graphics_role": "board_element",
                "critical_graphics_importance": "essential",
            }
        ]

        result = _attach_images(html, crops, "images")
        soup = BeautifulSoup(result, "html.parser")

        list_items = soup.find_all("li")
        assert list_items[0].find("img") is None
        assert list_items[1].find("img")["src"] == "images/green-belt.jpg"

    def test_unused_useful_crop_is_not_inserted_without_placeholder(self):
        html = "<p>Damage card text is already represented semantically.</p>"
        crops = [
            {
                **_crop("spam.jpg", image_description="SPAM damage card face — SPAM — card face"),
                "critical_graphics_role": "card_face",
                "critical_graphics_importance": "useful",
            }
        ]

        result = _attach_images(html, crops, "images")
        soup = BeautifulSoup(result, "html.parser")

        assert soup.find("img") is None

    def test_labeled_multi_image_figure_is_split_to_matching_following_entries(self):
        html = (
            '<figure><img alt="Gears"><img alt="Board lasers"></figure>'
            "<p><strong>Gears</strong><br>Gears rotate robots.</p>"
            "<p><strong>Board Lasers</strong><br>Board lasers fire at robots.</p>"
        )
        crops = [
            {
                **_crop(
                    "gears.jpg",
                    image_description="Two gear board-space examples — Gears rotate robots. — component reference",
                ),
                "critical_graphics_role": "component_reference",
                "critical_graphics_importance": "essential",
            },
            {
                **_crop(
                    "lasers.jpg",
                    image_description="Board laser space examples — Board Lasers fire at robots. — component reference",
                ),
                "critical_graphics_role": "component_reference",
                "critical_graphics_importance": "essential",
            },
        ]

        result = _attach_images(html, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        figures = soup.find_all("figure")
        paragraphs = soup.find_all("p")

        assert len(figures) == 2
        assert paragraphs[0].find_next_sibling("figure").find("img")["src"] == "images/gears.jpg"
        assert paragraphs[1].find_next_sibling("figure").find("img")["src"] == "images/lasers.jpg"

    def test_group_manifest_sorts_crops_by_visual_rows(self, tmp_path):
        manifest = tmp_path / "illustration_manifest.jsonl"
        rows = [
            {
                "source_page": 1,
                "filename": "right.jpg",
                "bbox": {"x0": 140, "y0": 28, "x1": 200, "y1": 88, "height": 60},
            },
            {
                "source_page": 1,
                "filename": "left.jpg",
                "bbox": {"x0": 20, "y0": 30, "x1": 80, "y1": 90, "height": 60},
            },
        ]
        manifest.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

        grouped = _group_manifest_by_page(str(manifest))

        assert [row["filename"] for row in grouped[1]] == ["left.jpg", "right.jpg"]

    def test_group_manifest_sorts_top_aligned_different_height_crops_left_to_right(self, tmp_path):
        manifest = tmp_path / "illustration_manifest.jsonl"
        rows = [
            {
                "source_page": 1,
                "filename": "right-tall.jpg",
                "bbox": {"x0": 140, "y0": 20, "x1": 220, "y1": 180, "height": 160},
            },
            {
                "source_page": 1,
                "filename": "left-short.jpg",
                "bbox": {"x0": 20, "y0": 24, "x1": 100, "y1": 84, "height": 60},
            },
        ]
        manifest.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

        grouped = _group_manifest_by_page(str(manifest))

        assert [row["filename"] for row in grouped[1]] == ["left-short.jpg", "right-tall.jpg"]


class TestFigurePlacementNormalization:
    def test_stitches_sentence_split_by_figure_run(self):
        crops = [
            _crop(
                "single.jpg",
                alt="Photo of Leonidas and Josephine L'Heureux seated together",
                image_description="Oval portrait of Laetitia L'Heureux",
            ),
            _crop(
                "couple.jpg",
                alt="Oval portrait of Laetitia L'Heureux",
                image_description="Photo of Leonidas and Josephine L'Heureux seated together",
            ),
        ]
        result = _attach_images(SAMPLE_PAGE_HTML_SWAPPED, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        paragraphs = soup.find_all("p")
        assert paragraphs[0].get_text(" ", strip=True) == (
            "The ten pound bags were dyed into different colors which were then "
            "cut into squares and made into colorful bedspreads."
        )
        assert len(paragraphs) == 1

    def test_keeps_figure_between_complete_paragraphs(self):
        crops = [_crop("photo.jpg")]
        result = _attach_images(SAMPLE_PAGE_HTML, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        paragraphs = soup.find_all("p")
        assert len(paragraphs) == 2
        assert paragraphs[0].get_text(" ", strip=True) == "Some text."
        assert paragraphs[1].get_text(" ", strip=True) == "More text."


# ---------------------------------------------------------------------------
# T6: HTML5 document wrapper
# ---------------------------------------------------------------------------

class TestHtml5Wrapper:
    def test_has_doctype(self):
        html = _html5_wrap("<p>Hello</p>", "Test Page")
        assert html.startswith("<!DOCTYPE html>")

    def test_has_charset_and_viewport(self):
        html = _html5_wrap("<p>Hello</p>", "Test Page")
        assert '<meta charset="utf-8">' in html
        assert 'name="viewport"' in html

    def test_has_title(self):
        html = _html5_wrap("<p>Hello</p>", "My Chapter")
        assert "<title>My Chapter</title>" in html

    def test_escapes_title(self):
        html = _html5_wrap("<p>Hello</p>", "A & B <script>")
        assert "A &amp; B &lt;script&gt;" in html

    def test_has_embedded_css(self):
        html = _html5_wrap("<p>Hello</p>", "Test")
        assert "<style>" in html
        assert "max-width" in html

    def test_wraps_in_article(self):
        html = _html5_wrap("<p>Content</p>", "Test")
        soup = BeautifulSoup(html, "html.parser")
        assert soup.find("article") is not None
        assert soup.find("article").find("p") is not None

    def test_includes_nav(self):
        nav = _build_nav("prev.html", "Prev", "next.html", "Next")
        html = _html5_wrap("<p>Body</p>", "Test", nav_html_top=nav)
        soup = BeautifulSoup(html, "html.parser")
        assert soup.find("nav") is not None

    def test_no_external_urls(self):
        """Output must be self-contained — no http:// or https:// in CSS or HTML."""
        html = _html5_wrap("<p>Hello</p>", "Test")
        assert "http://" not in html
        assert "https://" not in html


# ---------------------------------------------------------------------------
# T8: Navigation
# ---------------------------------------------------------------------------

class TestNavigation:
    def test_prev_and_next(self):
        nav = _build_nav("ch1.html", "Ch 1", "ch3.html", "Ch 3")
        assert 'href="ch1.html"' in nav
        assert 'href="ch3.html"' in nav
        assert 'href="index.html"' in nav
        assert 'data-doc-web-ui-chrome="navigation"' in nav
        assert 'aria-label="Document navigation"' in nav

    def test_no_prev(self):
        nav = _build_nav(None, None, "ch2.html", "Ch 2")
        assert "nav-placeholder" in nav
        assert 'href="ch2.html"' in nav

    def test_no_next(self):
        nav = _build_nav("ch1.html", "Ch 1", None, None)
        assert 'href="ch1.html"' in nav
        assert "nav-placeholder" in nav

    def test_bottom_nav_class(self):
        nav = _build_nav("a.html", "A", "b.html", "B", is_bottom=True)
        assert "bottom" in nav


# ---------------------------------------------------------------------------
# T10: Table scope attributes
# ---------------------------------------------------------------------------

class TestTableScope:
    def test_adds_scope_col_to_header_row(self):
        html = "<table><tr><th>Name</th><th>Age</th></tr><tr><td>A</td><td>1</td></tr></table>"
        result = _add_table_scope(html)
        soup = BeautifulSoup(result, "html.parser")
        ths = soup.find_all("th")
        assert all(th.get("scope") == "col" for th in ths)

    def test_adds_scope_row_to_first_col(self):
        html = "<table><tr><th>H1</th><th>H2</th></tr><tr><th>Row1</th><td>Val</td></tr></table>"
        result = _add_table_scope(html)
        soup = BeautifulSoup(result, "html.parser")
        body_th = soup.find_all("tr")[1].find("th")
        assert body_th.get("scope") == "row"

    def test_no_tables_returns_unchanged(self):
        html = "<p>No tables here</p>"
        assert _add_table_scope(html) == html

    def test_preserves_existing_scope(self):
        html = '<table><tr><th scope="colgroup">X</th></tr></table>'
        result = _add_table_scope(html)
        soup = BeautifulSoup(result, "html.parser")
        th = soup.find("th")
        assert th.get("scope") == "colgroup"


# ---------------------------------------------------------------------------
# Strip headers
# ---------------------------------------------------------------------------

class TestStripHeaders:
    def test_removes_page_numbers(self):
        html = '<p>Text</p><span class="page-number">42</span>'
        result = _strip_headers_and_numbers(html)
        assert "42" not in result
        assert "Text" in result

    def test_removes_running_heads(self):
        html = '<div class="running-head">CHAPTER 1</div><p>Body</p>'
        result = _strip_headers_and_numbers(html)
        assert "CHAPTER 1" not in result
        assert "Body" in result

    def test_empty_html(self):
        assert _strip_headers_and_numbers("") == ""


# ---------------------------------------------------------------------------
# Structure refinement
# ---------------------------------------------------------------------------

class TestStructureRefinement:
    def test_normalizes_cosmetic_heading_breaks(self):
        html = "<h1>JOSEPHINE<br>(L'HEUREUX ) ALAIN</h1>"
        result = _normalize_heading_breaks(html)
        assert "<br" not in result
        assert "JOSEPHINE (L'HEUREUX ) ALAIN" in result

    def test_title_matching_does_not_confuse_single_letter_last_name_tokens(self):
        assert _titles_related("Wilfrid L'Heureux", "Wilfred")
        assert not _titles_related("LEONIDAS L'HEUREUX", "ARTHUR L'HEUREUX")

    def test_refines_coarse_span_into_multiple_owner_segments(self):
        pages = [
            {
                "html": "<h1>JOSEPHINE (L'HEUREUX ) ALAIN</h1><p>Josephine text.</p>",
                "page_number": 48,
                "printed_page_number": 48,
                "owner_heading": "JOSEPHINE (L'HEUREUX ) ALAIN",
            },
            {
                "html": "<h1>Josephine L'Heureux Alain</h1><p>More Josephine.</p>",
                "page_number": 49,
                "printed_page_number": 49,
                "owner_heading": "Josephine L'Heureux Alain",
            },
            {
                "html": "<h1>PAUL L'HEUREUX</h1><p>Paul text.</p>",
                "page_number": 50,
                "printed_page_number": 50,
                "owner_heading": "PAUL L'HEUREUX",
            },
        ]
        segments = _refine_chapter_segments("Leonidas", 37, pages, ["Leonidas", "Josephine", "Paul", "George"])
        assert [segment["title"] for segment in segments] == [
            "JOSEPHINE (L'HEUREUX ) ALAIN",
            "PAUL L'HEUREUX",
        ]
        assert segments[0]["page_start"] == 48
        assert segments[0]["page_end"] == 49
        assert segments[1]["page_start"] == 50

    def test_marks_leading_pages_for_carry_back_when_stale_span_reaches_new_owner(self):
        pages = [
            {
                "html": "<p>Blank spacer page.</p>",
                "page_number": 107,
                "printed_page_number": 98,
                "owner_heading": None,
            },
            {
                "html": "<h1>PIERRE L'HEUREUX</h1><p>Pierre text.</p>",
                "page_number": 108,
                "printed_page_number": 99,
                "owner_heading": "PIERRE L'HEUREUX",
            },
        ]
        segments = _refine_chapter_segments(
            "Wilfred",
            98,
            pages,
            ["Wilfred", "Pierre", "Antoine"],
            stale_portion=True,
        )
        assert len(segments) == 2
        assert segments[0]["carry_back"] is True
        assert segments[0]["title"] == "Wilfred"
        assert segments[0]["page_start"] == 98
        assert segments[0]["page_end"] == 98
        assert segments[1]["title"] == "PIERRE L'HEUREUX"
        assert segments[1]["page_start"] == 99
        assert segments[1]["page_end"] == 99

    def test_accepts_minor_title_spelling_drift(self):
        pages = [
            {
                "html": "<h1>Wilfrid L'Heureux</h1><p>Wilfrid text.</p>",
                "page_number": 102,
                "printed_page_number": 93,
                "owner_heading": "Wilfrid L'Heureux",
            },
        ]
        segments = _refine_chapter_segments("Wilfred", 93, pages, ["Wilfred", "Pierre", "Antoine"])
        assert len(segments) == 1
        assert segments[0]["title"] == "Wilfrid L'Heureux"

    def test_carry_backs_entire_stale_anonymous_span(self):
        pages = [
            {
                "html": "<table><tr><td>Tail rows.</td></tr></table>",
                "page_number": 98,
                "printed_page_number": 89,
                "owner_heading": None,
            },
        ]
        segments = _refine_chapter_segments(
            "Roseanna",
            89,
            pages,
            ["Roseanna", "Antoinette", "Emilie"],
            stale_portion=True,
        )
        assert len(segments) == 1
        assert segments[0]["carry_back"] is True
        assert segments[0]["title"] == "Roseanna"
        assert segments[0]["page_start"] == 89
        assert segments[0]["page_end"] == 89

    def test_carry_backs_prefix_when_first_heading_matches_previous_chapter(self):
        pages = [
            {
                "html": "<h1>George L'Heureux</h1><p>George genealogy starts.</p>",
                "page_number": 62,
                "printed_page_number": 53,
                "owner_heading": "George L'Heureux",
            },
            {
                "html": "<table><tr><td>George continuation.</td></tr></table>",
                "page_number": 63,
                "printed_page_number": 54,
                "owner_heading": None,
            },
            {
                "html": "<h1>JOE (JOSEPH) L'HEUREUX</h1><p>Joe intro.</p>",
                "page_number": 66,
                "printed_page_number": 57,
                "owner_heading": "JOE (JOSEPH) L'HEUREUX",
            },
        ]
        segments = _refine_chapter_segments(
            "Paul",
            53,
            pages,
            ["Paul", "George", "Joe"],
            previous_title="GEORGE L'HEUREUX",
        )
        assert len(segments) == 2
        assert segments[0]["carry_back"] is True
        assert segments[0]["title"] == "GEORGE L'HEUREUX"
        assert segments[0]["page_start"] == 53
        assert segments[0]["page_end"] == 54
        assert segments[1]["title"] == "JOE (JOSEPH) L'HEUREUX"
        assert segments[1]["page_start"] == 57

    def test_previous_title_does_not_swallow_late_new_owner_after_anonymous_prefix(self):
        pages = [
            {
                "html": "<table><tr><td>Arthur genealogy tail.</td></tr></table>",
                "page_number": 35,
                "printed_page_number": 26,
                "owner_heading": None,
            },
            {
                "html": "<table><tr><td>More Arthur genealogy.</td></tr></table>",
                "page_number": 36,
                "printed_page_number": 27,
                "owner_heading": None,
            },
            {
                "html": "<h1>LEONIDAS L'HEUREUX</h1><p>Leonidas intro.</p>",
                "page_number": 38,
                "printed_page_number": 29,
                "owner_heading": "LEONIDAS L'HEUREUX",
            },
        ]
        segments = _refine_chapter_segments(
            "Arthur",
            26,
            pages,
            ["Arthur", "Leonidas", "Josephine"],
            previous_title="ARTHUR L'HEUREUX",
            stale_portion=True,
        )
        assert len(segments) == 2
        assert segments[0]["carry_back"] is True
        assert segments[0]["title"] == "Arthur"
        assert segments[0]["page_start"] == 26
        assert segments[0]["page_end"] == 27
        assert segments[1]["title"] == "LEONIDAS L'HEUREUX"
        assert segments[1]["page_start"] == 29

    def test_carry_backs_entire_portion_when_first_heading_matches_previous_chapter(self):
        pages = [
            {
                "html": "<h1>Marie Louise L'Heureux LaClare</h1><p>Marie-Louise genealogy.</p>",
                "page_number": 80,
                "printed_page_number": 71,
                "owner_heading": "Marie Louise L'Heureux LaClare",
            },
            {
                "html": "<table><tr><td>More genealogy.</td></tr></table>",
                "page_number": 81,
                "printed_page_number": 72,
                "owner_heading": None,
            },
        ]
        segments = _refine_chapter_segments(
            "Mathilda",
            71,
            pages,
            ["Mathilda", "Marie-Louise", "Roseanna"],
            previous_title="MARIE-LOUISE (L'HEUREUX) LaCLARE",
        )
        assert len(segments) == 1
        assert segments[0]["carry_back"] is True
        assert segments[0]["title"] == "MARIE-LOUISE (L'HEUREUX) LaCLARE"
        assert segments[0]["page_start"] == 71
        assert segments[0]["page_end"] == 72

    def test_retitles_from_first_page_heading_even_when_not_in_toc(self):
        pages = [
            {
                "html": "<h1><strong><em>I WISH</em></strong></h1><p>Closing page.</p>",
                "page_number": 118,
                "printed_page_number": 109,
                "owner_heading": "I WISH",
            },
        ]
        segments = _refine_chapter_segments("Antoine", 109, pages, ["Antoine"])
        assert len(segments) == 1
        assert segments[0]["title"] == "I WISH"

    def test_allows_late_non_toc_heading_after_stale_leading_pages(self):
        pages = [
            {
                "html": "<p>109</p>",
                "page_number": 118,
                "printed_page_number": 109,
                "owner_heading": None,
            },
            {
                "html": "<p>110</p>",
                "page_number": 119,
                "printed_page_number": 110,
                "owner_heading": None,
            },
            {
                "html": "<h1><strong><em>I WISH</em></strong></h1><p>Closing page.</p>",
                "page_number": 120,
                "printed_page_number": 111,
                "owner_heading": "I WISH",
            },
        ]
        segments = _refine_chapter_segments(
            "Antoine",
            109,
            pages,
            ["Antoine"],
            stale_portion=True,
        )
        assert len(segments) == 2
        assert segments[0]["carry_back"] is True
        assert segments[0]["page_start"] == 109
        assert segments[0]["page_end"] == 110
        assert segments[1]["title"] == "I WISH"
        assert segments[1]["page_start"] == 111

    def test_does_not_split_on_non_toc_family_heading(self):
        pages = [
            {
                "html": "<h1>ARTHUR L'HEUREUX</h1><p>Arthur text.</p>",
                "page_number": 26,
                "printed_page_number": 26,
                "owner_heading": "ARTHUR L'HEUREUX",
            },
            {
                "html": "<h1>NOEL'S FAMILY</h1><p>Subfamily table.</p>",
                "page_number": 27,
                "printed_page_number": 27,
                "owner_heading": "NOEL'S FAMILY",
            },
        ]
        segments = _refine_chapter_segments("Arthur", 26, pages, ["Arthur", "Leonidas", "Josephine"])
        assert len(segments) == 1
        assert segments[0]["title"] == "ARTHUR L'HEUREUX"

    def test_stitches_page_break_continuations(self):
        result = _stitch_page_breaks([
            "<p>Dad sold the land and put up an addition to</p>",
            "<p>be the store and post office.</p>",
        ])
        soup = BeautifulSoup(result, "html.parser")
        paragraphs = soup.find_all("p")
        assert len(paragraphs) == 1
        assert "addition to be the store and post office." in paragraphs[0].get_text(" ", strip=True)

    def test_keeps_distinct_paragraphs_when_sentence_is_complete(self):
        result = _stitch_page_breaks([
            "<p>Dad sold the land and moved home.</p>",
            "<p>He later opened the store.</p>",
        ])
        soup = BeautifulSoup(result, "html.parser")
        assert len(soup.find_all("p")) == 2

    def test_stitches_page_break_when_figure_run_ends_page(self):
        result = _stitch_page_breaks([
            (
                "<p>In 1931, after his father passed away, George bought his ranch "
                "and used his Twin City tractor and 51</p>"
                "<figure><img alt=\"Mrs. George\"></figure>"
            ),
            "<p>steel wheels. Around 1940, a salesman came by.</p>",
        ])
        soup = BeautifulSoup(result, "html.parser")
        paragraphs = soup.find_all("p")
        assert "Twin City tractor and 51 steel wheels." in paragraphs[0].get_text(" ", strip=True)


class TestGenealogyMerging:
    def test_merge_contiguous_genealogy_tables_preserves_existing_image_attrs(self):
        html = """
        <h1>ALMA</h1>
        <figure data-placement="ocr-inline" data-caption-source="heuristic">
          <img src="images/page-022-000.jpg" alt="Portrait" data-crop-filename="page-022-000.jpg"/>
          <figcaption><strong><em>Henry and Alma Alain on their 50th wedding anniversary in 1957.</em></strong></figcaption>
        </figure>
        <table>
          <thead>
            <tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY/GIRL</th><th>DIED</th></tr>
          </thead>
          <tbody>
            <tr><td>Alma</td><td>July 31, 1883</td><td>Apr. 8, 1907</td><td>Henry Alain</td><td>4 4</td><td>Dec. 15, 1982</td></tr>
          </tbody>
        </table>
        <h2>Alma's Grandchildren</h2>
        <h3>MARY PAULE'S FAMILY</h3>
        <table>
          <tbody>
            <tr><td>Ronald</td><td>Jan. 24, 1933</td><td>July 20, 1963</td><td>Jean Bailey</td><td>1</td><td>1</td></tr>
          </tbody>
        </table>
        """

        result = _merge_contiguous_genealogy_tables(html)
        soup = BeautifulSoup(result, "html.parser")
        figure = soup.find("figure")
        img = soup.find("img")

        assert figure is not None
        assert img is not None
        assert figure["data-placement"] == "ocr-inline"
        assert figure["data-caption-source"] == "heuristic"
        assert img["src"] == "images/page-022-000.jpg"
        assert img["data-crop-filename"] == "page-022-000.jpg"
        assert img["alt"] == "Portrait"

    def test_merge_contiguous_genealogy_tables_splits_flattened_context_headings(self):
        html = """
        <h1>ALMA</h1>
        <table>
          <thead>
            <tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY/GIRL</th><th>DIED</th></tr>
          </thead>
          <tbody>
            <tr><td>Wayne</td><td>Aug. 23, 1946</td><td>Dec., 1966</td><td>Lynn LeBlue</td><td>2</td><td></td></tr>
          </tbody>
        </table>
        <h2>Alma's Grandchildren BERTHA'S FAMILY</h2>
        <table>
          <tbody>
            <tr><td>Norbert</td><td>July 3, 1939</td><td>Apr. 15, 1961</td><td>Shirley Allen</td><td>4</td><td></td></tr>
          </tbody>
        </table>
        <h2>Alma's Great Grandchildren Bertha's Grandchildren NORBERT'S FAMILY</h2>
        <table>
          <tbody>
            <tr><td>Michelle</td><td>Jan. 12, 1962</td></tr>
          </tbody>
        </table>
        """

        result = _merge_contiguous_genealogy_tables(html)
        soup = BeautifulSoup(result, "html.parser")
        subgroup_rows = [
            row.get_text(" ", strip=True)
            for row in soup.find_all("tr", class_="genealogy-subgroup-heading")
        ]

        assert subgroup_rows == [
            "Alma's Grandchildren",
            "BERTHA'S FAMILY",
            "Alma's Great Grandchildren",
            "Bertha's Grandchildren",
            "NORBERT'S FAMILY",
        ]

    def test_merge_contiguous_genealogy_tables_absorbs_leading_headings_before_first_table(self):
        html = """
        <h1>ALMA</h1>
        <h2>Edithe's Great Grandchildren</h2>
        <h3>Wayne's Grandchildren</h3>
        SHONNA'S FAMILY
        <table>
          <thead>
            <tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr>
          </thead>
          <tbody>
            <tr><td>Nicole</td><td>Jan. 18, 1983</td><td></td><td></td><td></td><td></td><td></td></tr>
          </tbody>
        </table>
        """

        result = _merge_contiguous_genealogy_tables(html)
        soup = BeautifulSoup(result, "html.parser")

        assert [h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2", "h3"])] == ["ALMA"]
        subgroup_rows = [
            row.get_text(" ", strip=True)
            for row in soup.find("tbody").find_all("tr", class_="genealogy-subgroup-heading", recursive=False)
        ]
        assert subgroup_rows[:3] == [
            "Edithe's Great Grandchildren",
            "Wayne's Grandchildren",
            "SHONNA'S FAMILY",
        ]

    def test_merge_contiguous_genealogy_tables_absorbs_generation_h1_runs(self):
        html = """
        <h1>LEONIDAS</h1>
        <table>
          <thead>
            <tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr>
          </thead>
          <tbody>
            <tr><td>Leonidas</td><td>1885</td><td></td><td></td><td></td><td></td><td></td></tr>
          </tbody>
        </table>
        <h1>Leonidas' Great Grandchildren</h1>
        <h2>Alma's Grandchildren</h2>
        <h3>SHARON'S FAMILY</h3>
        <table>
          <tbody>
            <tr><td>Blaine</td><td>Aug. 16, 1971</td><td></td><td></td><td></td><td></td><td></td></tr>
          </tbody>
        </table>
        <table>
          <tbody>
            <tr><td>TOTAL DESCENDANTS</td><td>280</td></tr>
          </tbody>
        </table>
        """

        result = _merge_contiguous_genealogy_tables(html)
        soup = BeautifulSoup(result, "html.parser")
        tables = soup.find_all("table")

        assert len(tables) == 2
        assert [h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2", "h3"])] == ["LEONIDAS"]
        subgroup_rows = [
            row.get_text(" ", strip=True)
            for row in tables[0].find("tbody").find_all("tr", class_="genealogy-subgroup-heading", recursive=False)
        ]
        assert subgroup_rows == [
            "Leonidas' Great Grandchildren",
            "Alma's Grandchildren",
            "SHARON'S FAMILY",
        ]
        assert "TOTAL DESCENDANTS" in tables[1].get_text(" ", strip=True)

    def test_merge_contiguous_genealogy_tables_collapses_heading_table_runs(self):
        html = """
        <h1>ALMA</h1>
        <p>Intro paragraph.</p>
        <table>
          <thead>
            <tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY/GIRL</th><th>DIED</th></tr>
          </thead>
          <tbody>
            <tr><td>Alma</td><td>July 31, 1883</td><td>Apr. 8, 1907</td><td>Henry Alain</td><td>4 4</td><td>Dec. 15, 1982</td></tr>
          </tbody>
        </table>
        <h2>Alma's Grandchildren</h2>
        <h3>MARY PAULE'S FAMILY</h3>
        <table>
          <tbody>
            <tr><td>Ronald</td><td>Jan. 24, 1933</td><td>July 20, 1963</td><td>Jean Bailey</td><td>1</td><td>1</td></tr>
          </tbody>
        </table>
        <p><strong>Alma's Great Grandchildren<br/>Mary Paule's Grandchildren<br/>RONALD'S FAMILY</strong></p>
        <table>
          <tbody>
            <tr><td>Kari Lou</td><td>Oct. 30, 1964</td></tr>
          </tbody>
        </table>
        <table>
          <tbody>
            <tr><td>TOTAL DESCENDANTS</td><td>83</td></tr>
            <tr><td>LIVING</td><td>78</td></tr>
            <tr><td>DECEASED</td><td>5</td></tr>
          </tbody>
        </table>
        """

        result = _merge_contiguous_genealogy_tables(html)
        soup = BeautifulSoup(result, "html.parser")
        tables = soup.find_all("table")

        assert len(tables) == 2
        assert [h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2", "h3"])] == ["ALMA"]

        main_rows = tables[0].find("tbody").find_all("tr", recursive=False)
        subgroup_rows = [
            row.get_text(" ", strip=True)
            for row in main_rows
            if "genealogy-subgroup-heading" in (row.get("class") or [])
        ]
        assert subgroup_rows == [
            "Alma's Grandchildren",
            "MARY PAULE'S FAMILY",
            "Alma's Great Grandchildren",
            "Mary Paule's Grandchildren",
            "RONALD'S FAMILY",
        ]
        assert "Kari Lou" in tables[0].get_text(" ", strip=True)
        assert "TOTAL DESCENDANTS" in tables[1].get_text(" ", strip=True)

    def test_merge_contiguous_genealogy_tables_converts_name_list_paragraphs(self):
        html = """
        <h1>ARTHUR</h1>
        <table>
          <thead>
            <tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY/GIRL</th><th>DIED</th></tr>
          </thead>
          <tbody>
            <tr><td>Noel</td><td>Jan. 1, 1940</td><td></td><td></td><td>2 1</td><td></td></tr>
          </tbody>
        </table>
        <h2>ULRIC'S FAMILY</h2>
        <p>Claire<br/>Duffy<br/>Robin</p>
        <h2>RENE'S FAMILY</h2>
        <table>
          <tbody>
            <tr><td>Barbara Jean</td><td>Sept. 28, 1949</td></tr>
          </tbody>
        </table>
        """

        result = _merge_contiguous_genealogy_tables(html)
        soup = BeautifulSoup(result, "html.parser")
        tables = soup.find_all("table")

        assert len(tables) == 1
        assert not any("Claire" in paragraph.get_text(" ", strip=True) for paragraph in soup.find_all("p"))
        subgroup_rows = [
            row.get_text(" ", strip=True)
            for row in tables[0].find("tbody").find_all("tr", recursive=False)
            if "genealogy-subgroup-heading" in (row.get("class") or [])
        ]
        assert "ULRIC'S FAMILY" in subgroup_rows
        assert "RENE'S FAMILY" in subgroup_rows

    def test_merge_contiguous_genealogy_tables_stitches_direct_adjacent_continuations(self):
        html = """
        <h1>ARTHUR</h1>
        <table>
          <thead>
            <tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr>
          </thead>
          <tbody>
            <tr><td>Alice</td><td>Jan. 1, 1930</td><td></td><td></td><td>1</td><td>0</td><td></td></tr>
          </tbody>
        </table>
        <table>
          <thead>
            <tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr>
          </thead>
          <tbody>
            <tr><td>Bob</td><td>Feb. 2, 1932</td><td></td><td></td><td>0</td><td>1</td><td></td></tr>
          </tbody>
        </table>
        <table>
          <tbody>
            <tr><td>TOTAL DESCENDANTS</td><td>2</td></tr>
          </tbody>
        </table>
        """

        result = _merge_contiguous_genealogy_tables(html)
        soup = BeautifulSoup(result, "html.parser")
        tables = soup.find_all("table")

        assert len(tables) == 2
        main_rows = tables[0].find("tbody").find_all("tr", recursive=False)
        assert [row.get_text(" ", strip=True) for row in main_rows] == [
            "Alice Jan. 1, 1930 1 0",
            "Bob Feb. 2, 1932 0 1",
        ]
        assert "TOTAL DESCENDANTS" in tables[1].get_text(" ", strip=True)

    def test_merge_contiguous_genealogy_tables_rewrites_left_column_heading_rows(self):
        html = """
        <table>
          <thead>
            <tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr>
          </thead>
          <tbody>
            <tr><td>Alice</td><td>Jan. 1, 1930</td><td></td><td></td><td>1</td><td>0</td><td></td></tr>
            <tr><th><strong>Leonidas’ Great Great Grandchildren<br/>Alma’s Great Grandchildren<br/>Dolly’s Grandchildren<br/>SHARON’S FAMILY</strong></th><td></td><td></td><td></td><td></td><td></td><td></td></tr>
            <tr><td>Blaine</td><td>Aug. 16, 1971</td><td></td><td></td><td></td><td></td><td></td></tr>
          </tbody>
        </table>
        """

        result = _merge_contiguous_genealogy_tables(html)
        soup = BeautifulSoup(result, "html.parser")
        rows = soup.find("tbody").find_all("tr", recursive=False)

        assert [row.get_text(" ", strip=True) for row in rows[1:5]] == [
            "Leonidas’ Great Great Grandchildren",
            "Alma’s Great Grandchildren",
            "Dolly’s Grandchildren",
            "SHARON’S FAMILY",
        ]
        for row in rows[1:5]:
            assert "genealogy-subgroup-heading" in (row.get("class") or [])
            cells = row.find_all(["th", "td"], recursive=False)
            assert len(cells) == 1
            assert cells[0].get("colspan") == "7"

    def test_merge_contiguous_genealogy_tables_splits_flattened_generation_context_rows(self):
        html = """
        <table>
          <thead>
            <tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr>
          </thead>
          <tbody>
            <tr><th>Leonidas’ Great Great Grandchildren Alma’s Great Grandchildren Dolly’s Grandchildren SHARON’S FAMILY</th><td></td><td></td><td></td><td></td><td></td><td></td></tr>
            <tr><td>Blaine</td><td>Aug. 16, 1971</td><td></td><td></td><td></td><td></td><td></td></tr>
          </tbody>
        </table>
        """

        result = _merge_contiguous_genealogy_tables(html)
        soup = BeautifulSoup(result, "html.parser")
        rows = soup.find("tbody").find_all("tr", recursive=False)

        assert [row.get_text(" ", strip=True) for row in rows[:4]] == [
            "Leonidas’ Great Great Grandchildren",
            "Alma’s Great Grandchildren",
            "Dolly’s Grandchildren",
            "SHARON’S FAMILY",
        ]
        assert rows[4].get_text(" ", strip=True) == "Blaine Aug. 16, 1971"

    def test_merge_contiguous_genealogy_tables_moves_death_value_out_of_girl_column(self):
        html = """
        <table>
          <thead>
            <tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr>
          </thead>
          <tbody>
            <tr><td>Richard</td><td>, 1951</td><td></td><td></td><td></td><td>, 1956</td><td></td></tr>
          </tbody>
        </table>
        """

        result = _merge_contiguous_genealogy_tables(html)
        soup = BeautifulSoup(result, "html.parser")
        cells = soup.find("tbody").find("tr").find_all("td", recursive=False)
        assert [cell.get_text(" ", strip=True) for cell in cells] == [
            "Richard",
            ", 1951",
            "",
            "",
            "",
            "",
            ", 1956",
        ]

    def test_merge_contiguous_genealogy_tables_drops_repeated_body_header_rows(self):
        html = """
        <table>
          <thead>
            <tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY</th><th>GIRL</th><th>DIED</th></tr>
          </thead>
          <tbody>
            <tr><td>Reginald</td><td>Apr. 3, 1953</td><td>June 29, 1974</td><td>Judy O'Keefe</td><td>2</td><td></td><td></td></tr>
          </tbody>
        </table>
        <table>
          <tbody>
            <tr><td><strong>Arthur's Great Grandchildren<br/>Alphonse's Grandchildren<br/>ROGER'S FAMILY</strong></td></tr>
            <tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY/GIRL</th><th>DIED</th><td></td></tr>
            <tr><td>Danial</td><td>Mar. 3, 1973</td><td></td><td></td><td></td><td></td><td></td></tr>
            <tr><td>Diane</td><td>July 19, 1976</td><td></td><td></td><td></td><td></td><td></td></tr>
          </tbody>
        </table>
        """

        result = _merge_contiguous_genealogy_tables(html)
        soup = BeautifulSoup(result, "html.parser")
        tables = soup.find_all("table")

        assert len(tables) == 1
        assert result.count("BOY/GIRL") == 0
        assert result.count("BOY</th><th>GIRL") == 1

        repeated_headers = [
            row
            for row in tables[0].find("tbody").find_all("tr", recursive=False)
            if [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"], recursive=False)][:6]
            == ["NAME", "BORN", "MARRIED", "SPOUSE", "BOY/GIRL", "DIED"]
        ]
        assert repeated_headers == []

        subgroup_rows = [
            row.get_text(" ", strip=True)
            for row in tables[0].find("tbody").find_all("tr", class_="genealogy-subgroup-heading", recursive=False)
        ]
        assert subgroup_rows == [
            "Arthur's Great Grandchildren",
            "Alphonse's Grandchildren",
            "ROGER'S FAMILY",
        ]
        assert "Danial" in tables[0].get_text(" ", strip=True)
        assert "Diane" in tables[0].get_text(" ", strip=True)

    def test_merge_contiguous_genealogy_tables_normalizes_thead_heading_rows(self):
        html = """
        <table>
          <thead>
            <tr><th><strong>Arthur's Great Grandchildren</strong><br/><strong>Agnes' Grandchildren</strong><br/><strong>LAWRENCE'S FAMILY</strong></th></tr>
            <tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY/GIRL</th><th>DIED</th></tr>
          </thead>
          <tbody>
            <tr><td>Rene</td><td>Jan. 25, 1972</td><td></td><td></td><td></td><td></td></tr>
            <tr><th><strong>BERNICE'S FAMILY</strong></th></tr>
            <tr><td>Susan</td><td>Sept. 5, 1968</td><td></td><td></td><td></td><td></td></tr>
          </tbody>
        </table>
        """

        result = _merge_contiguous_genealogy_tables(html)
        soup = BeautifulSoup(result, "html.parser")
        table = soup.find("table")
        assert table is not None
        assert "BOY/GIRL" not in result

        header_row = table.find("thead").find("tr")
        assert [cell.get_text(" ", strip=True) for cell in header_row.find_all("th", recursive=False)] == [
            "NAME",
            "BORN",
            "MARRIED",
            "SPOUSE",
            "BOY",
            "GIRL",
            "DIED",
        ]

        subgroup_rows = [
            row.get_text(" ", strip=True)
            for row in table.find("tbody").find_all("tr", class_="genealogy-subgroup-heading", recursive=False)
        ]
        assert subgroup_rows[:4] == [
            "Arthur's Great Grandchildren",
            "Agnes' Grandchildren",
            "LAWRENCE'S FAMILY",
            "BERNICE'S FAMILY",
        ]

    def test_merge_genealogy_tables_preserving_headings_absorbs_generation_headings_and_converts_summary_dl(self):
        html = """
        <h1>MARIE LOUISE</h1>
        <h1>Marie Louise's Great Grandchildren</h1>
        <h2>Mabel's Grandchildren</h2>
        <h3>CLEMENCE'S FAMILY</h3>
        <table>
          <thead>
            <tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY/GIRL</th><th>DIED</th></tr>
          </thead>
          <tbody>
            <tr><td>Shelly</td><td>Dec. 14, 1966</td><td></td><td></td><td></td><td></td></tr>
          </tbody>
        </table>
        <h3>BERNADETTE'S FAMILY</h3>
        <table>
          <tbody>
            <tr><td>Leanne</td><td>Apr. 2, 1967</td><td></td><td></td><td></td><td></td></tr>
          </tbody>
        </table>
        <h1>Marie Louise's Grandchildren</h1>
        <h3>GILBERT'S FAMILY</h3>
        <table>
          <tbody>
            <tr><td>Laurent</td><td>July 30, 1948</td><td>July 18, 1970</td><td>Sharon Moore</td><td>1</td><td>1</td></tr>
          </tbody>
        </table>
        <h1>Marie Louise's Great Grandchildren</h1>
        <h2>Gilbert's Grandchildren</h2>
        <h3>LAURENT'S FAMILY</h3>
        <table>
          <tbody>
            <tr><td>Shane</td><td>Oct. 29, 1971</td><td></td><td></td><td></td><td></td></tr>
          </tbody>
        </table>
        <dl>
          <dt>TOTAL DESCENDANTS</dt><dd>215</dd>
          <dt>LIVING</dt><dd>209</dd>
          <dt>DECEASED</dt><dd>6</dd>
        </dl>
        """

        result = _merge_genealogy_tables_preserving_headings(html)
        soup = BeautifulSoup(result, "html.parser")
        headings = [heading.get_text(" ", strip=True) for heading in soup.find_all(["h1", "h2", "h3"])]
        tables = soup.find_all("table")

        assert headings == ["MARIE LOUISE"]
        assert len(tables) == 2
        subgroup_rows = [
            row.get_text(" ", strip=True)
            for row in tables[0].find("tbody").find_all("tr", class_="genealogy-subgroup-heading", recursive=False)
        ]
        assert subgroup_rows == [
            "Marie Louise's Great Grandchildren",
            "Mabel's Grandchildren",
            "CLEMENCE'S FAMILY",
            "BERNADETTE'S FAMILY",
            "Marie Louise's Grandchildren",
            "GILBERT'S FAMILY",
            "Marie Louise's Great Grandchildren",
            "Gilbert's Grandchildren",
            "LAURENT'S FAMILY",
        ]
        assert "TOTAL DESCENDANTS" in tables[-1].get_text(" ", strip=True)

    def test_finalize_genealogy_body_html_merges_cross_page_genealogy_runs(self):
        body_html = _stitch_page_breaks([
            (
                "<h1>ALMA</h1>"
                "<table><thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY/GIRL</th><th>DIED</th></tr></thead>"
                "<tbody><tr><td>Alma</td><td>July 31, 1883</td><td>Apr. 8, 1907</td><td>Henry Alain</td><td>4 4</td><td>Dec. 15, 1982</td></tr></tbody></table>"
            ),
            (
                "<h1>Alma's Grandchildren</h1><h2>MARY PAULE'S FAMILY</h2>"
                "<table><tbody><tr><td>Ronald</td><td>Jan. 24, 1933</td><td>July 20, 1963</td><td>Jean Bailey</td><td>1</td><td>1</td></tr></tbody></table>"
                "<p><strong>Alma's Great Grandchildren<br/>Mary Paule's Grandchildren<br/>RONALD'S FAMILY</strong></p>"
                "<table><tbody><tr><td>Kari Lou</td><td>Oct. 30, 1964</td></tr></tbody></table>"
                "<table><tbody><tr><td>TOTAL DESCENDANTS</td><td>83</td></tr></tbody></table>"
            ),
        ])

        result = _finalize_genealogy_body_html(body_html, enabled=True)
        soup = BeautifulSoup(result, "html.parser")
        article_bits = [heading.get_text(" ", strip=True) for heading in soup.find_all(["h1", "h2", "h3"])]
        tables = soup.find_all("table")

        assert article_bits == ["ALMA"]
        assert len(tables) == 2
        subgroup_rows = [
            row.get_text(" ", strip=True)
            for row in tables[0].find("tbody").find_all("tr", class_="genealogy-subgroup-heading", recursive=False)
        ]
        assert subgroup_rows == [
            "Alma's Grandchildren",
            "MARY PAULE'S FAMILY",
            "Alma's Great Grandchildren",
            "Mary Paule's Grandchildren",
            "RONALD'S FAMILY",
        ]
        assert "TOTAL DESCENDANTS" in tables[1].get_text(" ", strip=True)

    def test_rebalance_repeated_generation_h1s_demotes_later_generation_headings(self):
        html = """
        <h1>MARIE-LOUISE</h1>
        <h1>Marie Louise L'Heureux LaClare</h1>
        <h1>Marie Louise's Great Grandchildren</h1>
        <h1>Marie Louise's Grandchildren</h1>
        <h1>Marie Louise's Great Grandchildren</h1>
        """

        result = _rebalance_repeated_generation_h1s(html)
        soup = BeautifulSoup(result, "html.parser")

        assert [heading.name for heading in soup.find_all(["h1", "h2"])] == ["h1", "h1", "h1", "h2", "h2"]


# ---------------------------------------------------------------------------
# Integration: full pipeline via CLI
# ---------------------------------------------------------------------------

class TestCLIIntegration:
    """Run the module as a subprocess with fixture data and validate output."""

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        # Create fake pipeline_state.json so _resolve_run_dir works
        (self.tmpdir / "pipeline_state.json").write_text("{}")

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_jsonl(self, path: Path, rows: list):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")

    def test_produces_valid_html5_output(self):
        pages_path = self.tmpdir / "pages.jsonl"
        portions_path = self.tmpdir / "portions.jsonl"
        out_path = self.tmpdir / "manifest.jsonl"
        html_dir = self.tmpdir / "html"

        self._write_jsonl(pages_path, [
            {"page_number": 1, "printed_page_number": 1, "html": "<p>Page one content.</p>"},
            {"page_number": 2, "printed_page_number": 2, "html": '<p>Page two.</p><img alt="Photo">'},
        ])
        self._write_jsonl(portions_path, [
            {"title": "Introduction", "page_start": 1, "page_end": 2},
        ])

        # Create a minimal illustration manifest
        illust_dir = self.tmpdir / "illustrations"
        illust_images_dir = illust_dir / "images"
        illust_images_dir.mkdir(parents=True)
        # Create a tiny fake image
        (illust_images_dir / "photo.jpg").write_bytes(b"\xff\xd8\xff\xe0")
        illust_path = illust_dir / "illustration_manifest.jsonl"
        self._write_jsonl(illust_path, [
            {
                "source_page": 2,
                "filename": "photo.jpg",
                "alt": "Photo",
                "image_description": "A family portrait from 1920",
                "caption_text": "The L'Heureux family",
                "bbox": {"x0": 100, "y0": 200, "x1": 400, "y1": 500},
            },
        ])

        cmd = [
            sys.executable, "-m", "modules.build.build_chapter_html_v1.main",
            "--pages", str(pages_path),
            "--portions", str(portions_path),
            "--out", str(out_path),
            "--output-dir", str(html_dir),
            "--illustration-manifest", str(illust_path),
            "--book-title", "Test Book",
            "--book-author", "Test Author",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).resolve().parent.parent))
        assert result.returncode == 0, f"STDERR: {result.stderr}"

        # Validate index.html
        index_html = (html_dir / "index.html").read_text()
        assert "<!DOCTYPE html>" in index_html
        assert "Test Book" in index_html
        assert "Test Author" in index_html
        assert "Contents" in index_html

        # Validate chapter HTML
        chapter = (html_dir / "chapter-001.html").read_text()
        soup = BeautifulSoup(chapter, "html.parser")

        # HTML5 structure
        assert "<!DOCTYPE html>" in chapter
        assert soup.find("meta", attrs={"charset": "utf-8"}) is not None

        # Navigation
        navs = soup.find_all("nav")
        assert len(navs) >= 1
        assert any("index.html" in str(n) for n in navs)

        # Image with figure/figcaption
        figure = soup.find("figure")
        assert figure is not None, "Expected <figure> wrapping for image"
        img = figure.find("img")
        assert img is not None
        assert img["alt"] == "A family portrait from 1920"  # VLM description
        figcaption = figure.find("figcaption")
        assert figcaption is not None
        assert figcaption.string == "The L'Heureux family"

        # Image file was copied
        assert (html_dir / "images" / "photo.jpg").exists()

        # Self-contained: no external URLs
        assert "http://" not in chapter
        assert "https://" not in chapter

        # Manifest output
        manifest = [json.loads(line) for line in out_path.read_text().strip().split("\n")]
        assert len(manifest) >= 1
        assert manifest[0]["kind"] == "chapter"
        assert manifest[0]["title"] == "Introduction"

        bundle_manifest = DocWebBundleManifest.model_validate_json((html_dir / "manifest.json").read_text())
        provenance_rows = [
            DocWebProvenanceBlock.model_validate_json(line)
            for line in (html_dir / "provenance" / "blocks.jsonl").read_text().strip().splitlines()
        ]
        assert bundle_manifest.entries[0].entry_id == "chapter-001"
        assert bundle_manifest.reading_order == ["chapter-001"]
        assert bundle_manifest.asset_roots == ["images"]
        assert provenance_rows[0].block_id == "blk-chapter-001-0001"
        assert provenance_rows[0].block_kind == "paragraph"
        assert provenance_rows[-1].block_kind == "figure"
        dom_ids = set(re.findall(r'id="([^"]+)"', chapter))
        assert {row.block_id for row in provenance_rows} <= dom_ids

    def test_overwrites_stale_published_image_on_rerun(self):
        pages_path = self.tmpdir / "pages.jsonl"
        portions_path = self.tmpdir / "portions.jsonl"
        out_path = self.tmpdir / "manifest.jsonl"
        html_dir = self.tmpdir / "html"

        self._write_jsonl(pages_path, [
            {"page_number": 1, "printed_page_number": 1, "html": '<p>Page one.</p><img alt="Photo">'},
        ])
        self._write_jsonl(portions_path, [
            {"title": "Introduction", "page_start": 1, "page_end": 1},
        ])

        illust_dir = self.tmpdir / "illustrations"
        illust_images_dir = illust_dir / "images"
        illust_images_dir.mkdir(parents=True)
        source_bytes = b"fresh-image-bytes"
        stale_bytes = b"stale-image-bytes"
        (illust_images_dir / "photo.jpg").write_bytes(source_bytes)
        illust_path = illust_dir / "illustration_manifest.jsonl"
        self._write_jsonl(illust_path, [
            {
                "source_page": 1,
                "filename": "photo.jpg",
                "alt": "Photo",
                "image_description": "Fresh image",
                "caption_text": None,
                "bbox": {"x0": 100, "y0": 200, "x1": 400, "y1": 500},
            },
        ])

        (html_dir / "images").mkdir(parents=True)
        (html_dir / "images" / "photo.jpg").write_bytes(stale_bytes)

        cmd = [
            sys.executable, "-m", "modules.build.build_chapter_html_v1.main",
            "--pages", str(pages_path),
            "--portions", str(portions_path),
            "--out", str(out_path),
            "--output-dir", str(html_dir),
            "--illustration-manifest", str(illust_path),
            "--book-title", "Test Book",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).resolve().parent.parent))
        assert result.returncode == 0, f"STDERR: {result.stderr}"

        assert (html_dir / "images" / "photo.jpg").read_bytes() == source_bytes

    def test_removes_stale_published_image_not_in_current_manifest(self):
        pages_path = self.tmpdir / "pages.jsonl"
        portions_path = self.tmpdir / "portions.jsonl"
        out_path = self.tmpdir / "manifest.jsonl"
        html_dir = self.tmpdir / "html"

        self._write_jsonl(pages_path, [
            {"page_number": 1, "printed_page_number": 1, "html": '<p>Page one.</p><img alt="Photo">'},
        ])
        self._write_jsonl(portions_path, [
            {"title": "Introduction", "page_start": 1, "page_end": 1},
        ])

        illust_dir = self.tmpdir / "illustrations"
        illust_images_dir = illust_dir / "images"
        illust_images_dir.mkdir(parents=True)
        (illust_images_dir / "photo.jpg").write_bytes(b"fresh-image-bytes")
        illust_path = illust_dir / "illustration_manifest.jsonl"
        self._write_jsonl(illust_path, [
            {
                "source_page": 1,
                "filename": "photo.jpg",
                "alt": "Photo",
                "image_description": "Fresh image",
                "caption_text": None,
                "bbox": {"x0": 100, "y0": 200, "x1": 400, "y1": 500},
            },
        ])

        (html_dir / "images").mkdir(parents=True)
        (html_dir / "images" / "photo.jpg").write_bytes(b"stale-current-bytes")
        stale_extra = html_dir / "images" / "page-122-002.jpg"
        stale_extra.write_bytes(b"stale-extra-bytes")

        cmd = [
            sys.executable, "-m", "modules.build.build_chapter_html_v1.main",
            "--pages", str(pages_path),
            "--portions", str(portions_path),
            "--out", str(out_path),
            "--output-dir", str(html_dir),
            "--illustration-manifest", str(illust_path),
            "--book-title", "Test Book",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).resolve().parent.parent))
        assert result.returncode == 0, f"STDERR: {result.stderr}"

        assert (html_dir / "images" / "photo.jpg").read_bytes() == b"fresh-image-bytes"
        assert not stale_extra.exists()

    def test_merges_stale_duplicate_tail_into_previous_chapter(self):
        pages_path = self.tmpdir / "pages.jsonl"
        portions_path = self.tmpdir / "portions.jsonl"
        out_path = self.tmpdir / "manifest.jsonl"
        html_dir = self.tmpdir / "html"

        self._write_jsonl(pages_path, [
            {"page_number": 1, "printed_page_number": 1, "html": "<h1>ALMA</h1><p>Alma intro.</p>"},
            {"page_number": 2, "printed_page_number": 2, "html": "<table><tr><td>Arthur tail rows.</td></tr></table>"},
            {"page_number": 3, "printed_page_number": 3, "html": "<h1>ARTHUR</h1><p>Arthur intro.</p>"},
            {"page_number": 4, "printed_page_number": 4, "html": "<p>More Arthur.</p>"},
        ])
        self._write_jsonl(portions_path, [
            {"title": "Veterans", "page_start": 1, "page_end": 1},
            {"title": "Alma", "page_start": 2, "page_end": 3},
            {"title": "Arthur", "page_start": 4, "page_end": 4},
        ])

        cmd = [
            sys.executable, "-m", "modules.build.build_chapter_html_v1.main",
            "--pages", str(pages_path),
            "--portions", str(portions_path),
            "--out", str(out_path),
            "--output-dir", str(html_dir),
            "--book-title", "Test Book",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).resolve().parent.parent))
        assert result.returncode == 0, f"STDERR: {result.stderr}"

        manifest = [json.loads(line) for line in out_path.read_text().strip().split("\n")]
        chapters = [row for row in manifest if row["kind"] == "chapter"]
        assert len(chapters) == 2
        assert chapters[0]["title"] == "ALMA"
        assert chapters[0]["page_start"] == 1
        assert chapters[0]["page_end"] == 2
        assert chapters[0]["source_portion_titles"] == ["Veterans", "Alma"]
        assert chapters[1]["title"] == "ARTHUR"
        assert chapters[1]["page_start"] == 3
        assert chapters[1]["page_end"] == 4
        assert chapters[1]["source_portion_titles"] == ["Alma", "Arthur"]

        chapter_one = (html_dir / "chapter-001.html").read_text()
        chapter_two = (html_dir / "chapter-002.html").read_text()
        assert "Arthur tail rows." in chapter_one
        assert "Arthur intro." in chapter_two

    def test_cli_merges_contiguous_genealogy_tables_when_enabled(self):
        pages_path = self.tmpdir / "pages.jsonl"
        portions_path = self.tmpdir / "portions.jsonl"
        out_path = self.tmpdir / "manifest.jsonl"
        html_dir = self.tmpdir / "html"

        self._write_jsonl(pages_path, [
            {
                "page_number": 1,
                "printed_page_number": 1,
                "html": (
                    "<h1>ALMA</h1>"
                    "<table><thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY/GIRL</th><th>DIED</th></tr></thead>"
                    "<tbody><tr><td>Alma</td><td>July 31, 1883</td><td>Apr. 8, 1907</td><td>Henry Alain</td><td>4 4</td><td>Dec. 15, 1982</td></tr></tbody></table>"
                ),
            },
            {
                "page_number": 2,
                "printed_page_number": 2,
                "html": (
                    "<h2>Alma's Grandchildren</h2><h3>MARY PAULE'S FAMILY</h3>"
                    "<table><tbody><tr><td>Ronald</td><td>Jan. 24, 1933</td><td>July 20, 1963</td><td>Jean Bailey</td><td>1</td><td>1</td></tr></tbody></table>"
                    "<p><strong>Alma's Great Grandchildren<br/>Mary Paule's Grandchildren<br/>RONALD'S FAMILY</strong></p>"
                    "<table><tbody><tr><td>Kari Lou</td><td>Oct. 30, 1964</td></tr></tbody></table>"
                ),
            },
        ])
        self._write_jsonl(portions_path, [
            {"title": "Alma", "page_start": 1, "page_end": 2},
        ])

        cmd = [
            sys.executable, "-m", "modules.build.build_chapter_html_v1.main",
            "--pages", str(pages_path),
            "--portions", str(portions_path),
            "--out", str(out_path),
            "--output-dir", str(html_dir),
            "--book-title", "Test Book",
            "--merge-contiguous-genealogy-tables",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).resolve().parent.parent))
        assert result.returncode == 0, f"STDERR: {result.stderr}"

        chapter = (html_dir / "chapter-001.html").read_text()
        soup = BeautifulSoup(chapter, "html.parser")
        article = soup.find("article")
        tables = article.find_all("table")
        assert len(tables) == 1
        assert [heading.get_text(" ", strip=True) for heading in article.find_all(["h1", "h2", "h3"])] == [
            "ALMA",
        ]
        subgroup_rows = [
            row.get_text(" ", strip=True)
            for row in tables[0].find("tbody").find_all("tr", class_="genealogy-subgroup-heading", recursive=False)
        ]
        assert subgroup_rows == [
            "Alma's Grandchildren",
            "MARY PAULE'S FAMILY",
            "Alma's Great Grandchildren",
            "Mary Paule's Grandchildren",
            "RONALD'S FAMILY",
        ]

    def test_cli_merges_cross_page_genealogy_continuations_when_enabled(self):
        pages_path = self.tmpdir / "pages.jsonl"
        portions_path = self.tmpdir / "portions.jsonl"
        out_path = self.tmpdir / "manifest.jsonl"
        html_dir = self.tmpdir / "html"

        self._write_jsonl(pages_path, [
            {
                "page_number": 1,
                "printed_page_number": 1,
                "html": (
                    "<h1>PIERRE</h1>"
                    "<table><thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY/GIRL</th><th>DIED</th></tr></thead>"
                    "<tbody><tr><td>Pierre</td><td>1901</td><td></td><td></td><td>1 1</td><td></td></tr></tbody></table>"
                ),
            },
            {
                "page_number": 2,
                "printed_page_number": 2,
                "html": (
                    "<table><thead><tr><th>NAME</th><th>BORN</th><th>MARRIED</th><th>SPOUSE</th><th>BOY/GIRL</th><th>DIED</th></tr></thead>"
                    "<tbody><tr><td><strong>SANDRA'S FAMILY</strong></td></tr><tr><td>Ryan</td><td>1982</td><td></td><td></td><td></td><td></td></tr></tbody></table>"
                ),
            },
        ])
        self._write_jsonl(portions_path, [
            {"title": "Pierre", "page_start": 1, "page_end": 2},
        ])

        cmd = [
            sys.executable, "-m", "modules.build.build_chapter_html_v1.main",
            "--pages", str(pages_path),
            "--portions", str(portions_path),
            "--out", str(out_path),
            "--output-dir", str(html_dir),
            "--book-title", "Test Book",
            "--merge-contiguous-genealogy-tables",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).resolve().parent.parent))
        assert result.returncode == 0, f"STDERR: {result.stderr}"

        chapter = (html_dir / "chapter-001.html").read_text()
        soup = BeautifulSoup(chapter, "html.parser")
        tables = soup.find("article").find_all("table")

        assert len(tables) == 1
        subgroup_rows = [
            row.get_text(" ", strip=True)
            for row in tables[0].find("tbody").find_all("tr", class_="genealogy-subgroup-heading", recursive=False)
        ]
        assert subgroup_rows == ["SANDRA'S FAMILY"]

    def test_merges_same_family_prefix_into_previous_chapter(self):
        pages_path = self.tmpdir / "pages.jsonl"
        portions_path = self.tmpdir / "portions.jsonl"
        out_path = self.tmpdir / "manifest.jsonl"
        html_dir = self.tmpdir / "html"

        self._write_jsonl(pages_path, [
            {"page_number": 1, "printed_page_number": 1, "html": "<h1>GEORGE L'HEUREUX</h1><p>George intro.</p>"},
            {"page_number": 2, "printed_page_number": 2, "html": "<p>George prose continues.</p>"},
            {"page_number": 3, "printed_page_number": 3, "html": "<h1>George L'Heureux</h1><table><tr><td>George genealogy.</td></tr></table>"},
            {"page_number": 4, "printed_page_number": 4, "html": "<p>More George genealogy.</p>"},
            {"page_number": 5, "printed_page_number": 5, "html": "<h1>JOE (JOSEPH) L'HEUREUX</h1><p>Joe intro.</p>"},
        ])
        self._write_jsonl(portions_path, [
            {"title": "Josephine", "page_start": 1, "page_end": 2},
            {"title": "Paul", "page_start": 3, "page_end": 5},
        ])

        cmd = [
            sys.executable, "-m", "modules.build.build_chapter_html_v1.main",
            "--pages", str(pages_path),
            "--portions", str(portions_path),
            "--out", str(out_path),
            "--output-dir", str(html_dir),
            "--book-title", "Test Book",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).resolve().parent.parent))
        assert result.returncode == 0, f"STDERR: {result.stderr}"

        manifest = [json.loads(line) for line in out_path.read_text().strip().split("\n")]
        chapters = [row for row in manifest if row["kind"] == "chapter"]
        assert len(chapters) == 2
        assert chapters[0]["title"] == "GEORGE L'HEUREUX"
        assert chapters[0]["page_start"] == 1
        assert chapters[0]["page_end"] == 4
        assert chapters[0]["source_portion_titles"] == ["Josephine", "Paul"]
        assert chapters[1]["title"] == "JOE (JOSEPH) L'HEUREUX"
        assert chapters[1]["page_start"] == 5
        assert chapters[1]["page_end"] == 5

    def test_skips_replayed_same_page_portions_once_page_is_already_covered(self):
        pages_path = self.tmpdir / "pages.jsonl"
        portions_path = self.tmpdir / "portions.jsonl"
        out_path = self.tmpdir / "manifest.jsonl"
        html_dir = self.tmpdir / "html"

        self._write_jsonl(pages_path, [
            {
                "page_number": 10,
                "printed_page_number": 1,
                "html": "<h1>The Ancestral Lineage of Moïse and Sophie</h1><p>One clean source page.</p>",
            },
            {
                "page_number": 11,
                "printed_page_number": 2,
                "html": "<h1>The First L'Heureux's in Canada</h1><p>Next chapter.</p>",
            },
        ])
        self._write_jsonl(portions_path, [
            {"title": "Ancestral Lineage", "page_start": 1, "page_end": 1},
            {"title": "Lawrence", "page_start": 1, "page_end": 1},
            {"title": "Edith", "page_start": 1, "page_end": 1},
            {"title": "The First L'Heureux's in Canada", "page_start": 2, "page_end": 2},
        ])

        cmd = [
            sys.executable, "-m", "modules.build.build_chapter_html_v1.main",
            "--pages", str(pages_path),
            "--portions", str(portions_path),
            "--out", str(out_path),
            "--output-dir", str(html_dir),
            "--book-title", "Test Book",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).resolve().parent.parent))
        assert result.returncode == 0, f"STDERR: {result.stderr}"

        manifest = [json.loads(line) for line in out_path.read_text().strip().split("\n")]
        chapters = [row for row in manifest if row["kind"] == "chapter"]
        assert len(chapters) == 2
        assert [row["title"] for row in chapters] == [
            "The Ancestral Lineage of Moïse and Sophie",
            "The First L'Heureux's in Canada",
        ]
        assert chapters[0]["source_pages"] == [10]
        assert chapters[0]["source_portion_titles"] == ["Ancestral Lineage"]

        chapter_one = (html_dir / "chapter-001.html").read_text()
        assert chapter_one.count("One clean source page.") == 1
        assert "Lawrence" not in chapter_one
        assert "Edith" not in chapter_one

    def test_builds_chapter_from_source_page_portion_when_printed_numbers_missing(self):
        pages_path = self.tmpdir / "pages.jsonl"
        portions_path = self.tmpdir / "portions.jsonl"
        out_path = self.tmpdir / "manifest.jsonl"
        html_dir = self.tmpdir / "html"

        self._write_jsonl(
            pages_path,
            [
                {"page_number": 1, "printed_page_number": None, "html": "<p>Flat page one.</p>"},
                {"page_number": 2, "printed_page_number": None, "html": "<p>Flat page two.</p>"},
            ],
        )
        self._write_jsonl(
            portions_path,
            [
                {
                    "title": "Document",
                    "page_start": 1,
                    "page_end": 2,
                    "source_pages": [1, 2],
                }
            ],
        )

        cmd = [
            sys.executable,
            "-m",
            "modules.build.build_chapter_html_v1.main",
            "--pages",
            str(pages_path),
            "--portions",
            str(portions_path),
            "--out",
            str(out_path),
            "--output-dir",
            str(html_dir),
            "--book-title",
            "Flat Document",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).resolve().parent.parent))
        assert result.returncode == 0, f"STDERR: {result.stderr}"

        manifest = [json.loads(line) for line in out_path.read_text().strip().split("\n")]
        assert [row["kind"] for row in manifest] == ["chapter"]
        assert manifest[0]["title"] == "Document"
        assert manifest[0]["page_start"] == 1
        assert manifest[0]["page_end"] == 2
        assert manifest[0]["source_pages"] == [1, 2]

        chapter = (html_dir / "chapter-001.html").read_text()
        index_html = (html_dir / "index.html").read_text()
        assert "Flat page one." in chapter
        assert "Flat page two." in chapter
        assert "Document" in index_html
        assert "(p. 1)" not in index_html
        assert not (html_dir / "page-001.html").exists()

        bundle_manifest = DocWebBundleManifest.model_validate_json((html_dir / "manifest.json").read_text())
        assert bundle_manifest.reading_order == ["chapter-001"]
        assert bundle_manifest.entries[0].printed_pages == []
        assert bundle_manifest.entries[0].printed_page_start is None
        assert bundle_manifest.entries[0].printed_page_end is None
        assert bundle_manifest.entries[0].source_pages == [1, 2]

    def test_leaves_source_only_front_matter_as_fallback_when_paginated_chapter_starts_at_same_number(self):
        pages_path = self.tmpdir / "pages.jsonl"
        portions_path = self.tmpdir / "portions.jsonl"
        out_path = self.tmpdir / "manifest.jsonl"
        html_dir = self.tmpdir / "html"

        self._write_jsonl(
            pages_path,
            [
                {
                    "page_number": 1,
                    "printed_page_number": None,
                    "html": "<h1>Memoires de Rolland Alain</h1>",
                },
                {
                    "page_number": 2,
                    "printed_page_number": 1,
                    "html": (
                        "<p>March 7th 1985</p>"
                        "<h1>Memoires of Rolland Alain from birth 1913 to 71st year 1985</h1>"
                        "<p>I was born in Delmas Sask.</p>"
                    ),
                },
                {
                    "page_number": 3,
                    "printed_page_number": 2,
                    "html": "<p>A few miles south of Delmas lived a bachelor.</p>",
                },
            ],
        )
        self._write_jsonl(
            portions_path,
            [
                {
                    "title": "Memoires de Rolland Alain",
                    "page_start": 1,
                    "page_end": 1,
                    "source_pages": [1],
                    "notes": "heading-derived-source-pages",
                },
                {
                    "title": "Memoires of Rolland Alain from birth 1913 to 71st year 1985",
                    "page_start": 1,
                    "page_end": 2,
                    "source_pages": [2, 3],
                    "notes": "heading-derived",
                },
            ],
        )

        cmd = [
            sys.executable, "-m", "modules.build.build_chapter_html_v1.main",
            "--pages", str(pages_path),
            "--portions", str(portions_path),
            "--out", str(out_path),
            "--output-dir", str(html_dir),
            "--book-title", "Test Book",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).resolve().parent.parent))
        assert result.returncode == 0, f"STDERR: {result.stderr}"

        manifest = [json.loads(line) for line in out_path.read_text().strip().split("\n")]
        entries = [(row["kind"], row["title"]) for row in manifest]
        assert entries == [
            ("page", "Image 1"),
            ("chapter", "Memoires of Rolland Alain from birth 1913 to 71st year 1985"),
        ]

        page_one = (html_dir / "page-001.html").read_text()
        assert "Memoires de Rolland Alain" in page_one

        chapter_one = (html_dir / "chapter-001.html").read_text()
        soup = BeautifulSoup(chapter_one, "html.parser")
        article = soup.find("article")
        assert article is not None
        article_html = article.decode_contents()
        assert article_html.count("March 7th 1985") == 1
        assert article_html.count("Memoires of Rolland Alain from birth 1913 to 71st year 1985") == 1
        assert article_html.count("I was born in Delmas Sask.") == 1
        assert "A few miles south of Delmas lived a bachelor." in chapter_one

    def test_demotes_in_body_heading_levels_for_source_page_chapter(self):
        pages_path = self.tmpdir / "pages.jsonl"
        portions_path = self.tmpdir / "portions.jsonl"
        out_path = self.tmpdir / "manifest.jsonl"
        html_dir = self.tmpdir / "html"

        self._write_jsonl(
            pages_path,
            [
                {
                    "page_number": 1,
                    "printed_page_number": None,
                    "html": (
                        "<h2>Packet title</h2>"
                        "<h1>Document</h1>"
                        "<p>Lead paragraph.</p>"
                        "<h1>Budget notes:</h1>"
                        "<p>Budget paragraph.</p>"
                        "<h2>Signature block:</h2>"
                        "<p>Signature paragraph.</p>"
                    ),
                }
            ],
        )
        self._write_jsonl(
            portions_path,
            [
                {
                    "title": "Document",
                    "page_start": 1,
                    "page_end": 1,
                    "source_pages": [1],
                }
            ],
        )

        cmd = [
            sys.executable,
            "-m",
            "modules.build.build_chapter_html_v1.main",
            "--pages",
            str(pages_path),
            "--portions",
            str(portions_path),
            "--out",
            str(out_path),
            "--output-dir",
            str(html_dir),
            "--book-title",
            "Flat Document",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).resolve().parent.parent))
        assert result.returncode == 0, f"STDERR: {result.stderr}"

        soup = BeautifulSoup((html_dir / "chapter-001.html").read_text(), "html.parser")
        headings = [(tag.name, tag.get_text(" ", strip=True)) for tag in soup.find_all(re.compile(r"^h[1-6]$"))]
        assert ("h2", "Packet title") in headings
        assert ("h1", "Document") in headings
        assert ("h3", "Budget notes:") in headings
        assert ("h3", "Signature block:") in headings
        assert ("h1", "Budget notes:") not in headings
        assert ("h2", "Signature block:") not in headings

    def test_flattens_oversized_flat_heading_block_into_emphasis_paragraph(self):
        pages_path = self.tmpdir / "pages.jsonl"
        portions_path = self.tmpdir / "portions.jsonl"
        out_path = self.tmpdir / "manifest.jsonl"
        html_dir = self.tmpdir / "html"

        self._write_jsonl(
            pages_path,
            [
                {
                    "page_number": 1,
                    "printed_page_number": None,
                    "html": (
                        "<h2>Document</h2>"
                        "<h2>WARNING: THIS AGREEMENT WILL AFFECT YOUR LEGAL RIGHTS. "
                        "READ IT CAREFULLY! Every person must read and understand this waiver "
                        "before participating in riding activities.</h2>"
                        "<p>Body paragraph.</p>"
                    ),
                }
            ],
        )
        self._write_jsonl(
            portions_path,
            [
                {
                    "title": "Document",
                    "page_start": 1,
                    "page_end": 1,
                    "source_pages": [1],
                }
            ],
        )

        cmd = [
            sys.executable,
            "-m",
            "modules.build.build_chapter_html_v1.main",
            "--pages",
            str(pages_path),
            "--portions",
            str(portions_path),
            "--out",
            str(out_path),
            "--output-dir",
            str(html_dir),
            "--book-title",
            "Flat Document",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).resolve().parent.parent))
        assert result.returncode == 0, f"STDERR: {result.stderr}"

        soup = BeautifulSoup((html_dir / "chapter-001.html").read_text(), "html.parser")
        flattened = soup.find("p", class_="flattened-heading")
        assert flattened is not None
        assert "WARNING: THIS AGREEMENT WILL AFFECT YOUR LEGAL RIGHTS." in flattened.get_text(" ", strip=True)
        assert not any(
            tag.name == "h2" and "WARNING: THIS AGREEMENT WILL AFFECT YOUR LEGAL RIGHTS." in tag.get_text(" ", strip=True)
            for tag in soup.find_all(re.compile(r"^h[1-6]$"))
        )

    def test_preserves_nested_heading_levels_for_catalog_chapters(self):
        html = (
            "<h1>ROUTE CATALOG</h1>"
            "<p>On the following pages, find a list of routes.</p>"
            "<h1>EASY ROUTES</h1>"
            "<h2>RIVER WALK</h2>"
            "<p><strong>Distance:</strong> Short<br><strong>Difficulty:</strong> Easy</p>"
            "<h2>RIDGE WALK</h2>"
            "<p><strong>Distance:</strong> Long<br><strong>Difficulty:</strong> Medium</p>"
            "<h1>HARD. ROUTE. CATALOG</h1>"
            "<h2>CLIFF LOOP</h2>"
            "<p><strong>Distance:</strong> Long<br><strong>Difficulty:</strong> Hard</p>"
        )

        soup = BeautifulSoup(_polish_flat_chapter_headings(html, "ROUTE CATALOG"), "html.parser")
        headings = [(tag.name, tag.get_text(" ", strip=True)) for tag in soup.find_all(re.compile(r"^h[1-6]$"))]

        assert headings == [
            ("h1", "ROUTE CATALOG"),
            ("h2", "EASY ROUTES"),
            ("h3", "RIVER WALK"),
            ("h3", "RIDGE WALK"),
            ("h2", "HARD. ROUTE. CATALOG"),
            ("h3", "CLIFF LOOP"),
        ]
