"""Tests for build_chapter_html_v1 — HTML5 structure, image integration, navigation."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from bs4 import BeautifulSoup

from modules.build.build_chapter_html_v1.main import (
    _attach_images,
    _is_likely_caption,
    _html5_wrap,
    _add_table_scope,
    _build_nav,
    _strip_headers_and_numbers,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_PAGE_HTML = '<p>Some text.</p><img alt="Photo"><p>More text.</p>'
SAMPLE_PAGE_HTML_MULTI = '<p>Text.</p><img alt="A"><img alt="B"><p>End.</p>'
SAMPLE_PAGE_HTML_NO_IMG = '<p>Just text, no images here.</p>'


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


# ---------------------------------------------------------------------------
# T3: Robust image matching
# ---------------------------------------------------------------------------

class TestImageMatching:
    def test_more_tags_than_crops(self):
        """Extra <img> tags should be left alone, not crash."""
        crops = [_crop("img.jpg")]
        result = _attach_images(SAMPLE_PAGE_HTML_MULTI, crops, "images")
        soup = BeautifulSoup(result, "html.parser")
        imgs = soup.find_all("img")
        assert len(imgs) == 2
        assert imgs[0].get("src") == "images/img.jpg"
        assert imgs[1].get("src") is None  # unmatched

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
