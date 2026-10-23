from bs4 import BeautifulSoup
import pytest

from modules.build.build_chapter_html_v1 import main as build


def _crop(name="ALPHA TOKEN", *, native=False):
    row = {"filename": "alpha.png", "source_page": 4, "nearby_text": name + " — Cost: 2",
           "image_description": f"{name} illustration — {name} — component reference",
           "critical_graphics_role": "component_reference", "critical_graphics_importance": "useful"}
    if native:
        row.update(contains_text=True, native_graphics_provenance={
            "inclusion_policy": "source-associated-catalog-illustrations-v1", "anchor": {"label": name},
            "source_pdf_sha256": "0" * 64, "preserve_transcribed_text": True})
    return row


def _text(html):
    soup = BeautifulSoup(html, "html.parser")
    for figure in soup.find_all("figure"):
        figure.decompose()
    return soup.get_text(" ", strip=True)


def test_existing_useful_crop_attaches_inside_unique_table_label_cell_without_text_changes():
    html = "<table><thead><tr><th>Item</th><th>Cost</th><th>Effect</th></tr></thead><tbody>" \
           "<tr><td>ALPHA TOKEN</td><td>2</td><td>Choose one: turn; or move. Keep the exception.</td></tr>" \
           "<tr><td>BETA TOKEN</td><td>4</td><td>After the first action, draw again.</td></tr></tbody></table>"
    result = build._attach_images(html, [_crop()], "images")
    soup = BeautifulSoup(result, "html.parser")
    assert soup.select_one("tbody tr td figure img")["src"] == "images/alpha.png"
    assert len(soup.select("tbody tr")) == 2
    assert _text(result) == _text(html)
    assert build._attach_images(result, [_crop()], "images") == result


@pytest.mark.parametrize("label", ["ALPHA TOKEN", "Alpha Token"])
def test_duplicate_table_labels_abstain(label):
    html = f"<table><tr><td>ALPHA TOKEN</td><td>2</td></tr><tr><td>{label}</td><td>3</td></tr></table>"
    assert not BeautifulSoup(build._attach_images(html, [_crop()], "images"), "html.parser").find("img")


def test_description_cell_cannot_steal_table_figure():
    html = "<table><tr><td>BETA TOKEN</td><td>ALPHA TOKEN</td></tr></table>"
    assert not BeautifulSoup(build._attach_images(html, [_crop()], "images"), "html.parser").find("img")


def test_native_supplement_preserves_all_text_and_bypasses_ocr_dedup(monkeypatch):
    html = "<h2>ALPHA TOKEN</h2><figure><img alt='Alpha token source picture'></figure>" \
           "<p>ALPHA TOKEN</p><p>Choose one: turn left; turn right; move.</p><p>Unless blocked, do both.</p>"
    monkeypatch.setattr(build, "_ocr_crop_text", lambda *args: pytest.fail("native supplement must not OCR/dedup text"))
    result = build._attach_images(html, [_crop(native=True)], "images")
    soup = BeautifulSoup(result, "html.parser")
    assert len(soup.find_all("img")) == 1
    assert soup.img["data-native-graphics-anchor"] == "ALPHA TOKEN"
    assert soup.img["data-doc-web-source-page-number"] == "4"
    assert _text(result) == _text(html)
    assert build._attach_images(result, [_crop(native=True)], "images") == result


def test_native_exact_label_contract_abstains_on_heading_and_table_collision():
    html = "<h2>ALPHA TOKEN</h2><table><tr><td>ALPHA TOKEN</td><td>2</td></tr></table>"
    assert not BeautifulSoup(build._attach_images(html, [_crop(native=True)], "images"), "html.parser").find("img")


def test_supplement_figures_preserve_later_nonfigure_source_joins_and_emit_crop_provenance():
    before = "<h2>ALPHA TOKEN</h2><p>First exact instruction.</p><h2>BETA TOKEN</h2><p>Later exact exception.</p>"
    after = build._attach_images(before, [_crop(native=True)], "images")

    def tag(html):
        return build._tag_entry_body({"filename": "chapter-1.html", "body_html": html,
            "source_pages": [4], "source_printed_pages": [12],
            "prepared_pages": [{"html": html, "page_number": 4, "original_page_number": 3,
                                "printed_page_number": 12}]}, run_id="synthetic", created_at="test")[1]

    baseline, candidate = tag(before), tag(after)
    def keep(rows):
        return [{k: row[k] for k in ("block_kind", "source_page_number", "source_original_page_number",
                 "source_printed_page_number", "source_element_ids", "text_quote")}
                for row in rows if row["block_kind"] != "figure"]
    assert keep(baseline) == keep(candidate)
    figures = [r for r in candidate if r["block_kind"] == "figure"]
    assert len(figures) == 1
    assert figures[0]["source_element_ids"] == ["crop:alpha.png"]
    assert figures[0]["source_page_number"] == 4


def test_table_nested_figure_gets_its_own_source_provenance():
    before = "<table><tr><td>ALPHA TOKEN</td><td>2</td></tr></table><p>Keep following text.</p>"
    after = build._attach_images(before, [_crop()], "images")
    _, rows = build._tag_entry_body({"filename": "chapter-1.html", "body_html": after,
        "source_pages": [4], "prepared_pages": [{"html": after, "page_number": 4}]},
        run_id="synthetic", created_at="test")
    assert [r["block_kind"] for r in rows] == ["table", "figure", "paragraph"]
    assert rows[1]["source_element_ids"] == ["crop:alpha.png"]
    assert rows[2]["source_element_ids"] == ["p004-b2"]
