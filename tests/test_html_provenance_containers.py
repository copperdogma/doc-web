"""Citation boundaries must survive ordinary authored HTML containers."""

import pytest
from bs4 import BeautifulSoup

from modules.build.build_chapter_html_v1.main import _tag_entry_body


STRUCTURED_CONTENT = (
    '<h2 id="arrival">Arrival</h2><p>Use the <em>north</em> entrance.</p>'
    '<ul><li>Compass</li><li><a href="#arrival">Water</a></li></ul>'
    '<table><tr><th>Station</th><th>Depth</th></tr>'
    '<tr><td>North Pier</td><td>8</td></tr></table>'
    '<figure><img src="harbor.png" alt="Harbor"/><figcaption>Harbor view</figcaption></figure>'
)


def _tag(html, *, source_html=None):
    return _tag_entry_body(
        {
            "filename": "chapter-001.html",
            "body_html": html,
            "source_pages": [7],
            "prepared_pages": [{
                "html": source_html if source_html is not None else html,
                "page_number": 7,
                "original_page_number": 42,
            }],
        },
        run_id="container-citation-test",
        created_at="2026-10-23T00:00:00Z",
    )


@pytest.mark.parametrize("wrapper", ["main", "div", "article", "section"])
def test_structured_wrapper_preserves_distinct_citation_units(wrapper):
    html = f'<{wrapper}><!-- source comment -->{STRUCTURED_CONTENT}</{wrapper}>'
    tagged, rows = _tag(html)

    assert [row["block_kind"] for row in rows] == [
        "heading", "paragraph", "list_item", "list_item", "table", "figure",
    ]
    assert [row["text_quote"] for row in rows] == [
        "Arrival", "Use the north entrance.", "Compass", "Water", None, None,
    ]
    assert [row["source_element_ids"] for row in rows] == [
        [f"p007-b{ordinal}"] for ordinal in range(1, 7)
    ]
    assert all(row["source_page_number"] == 7 for row in rows)
    assert all(row["source_original_page_number"] == 42 for row in rows)
    source = BeautifulSoup(html, "html.parser")
    final = BeautifulSoup(tagged, "html.parser")
    assert final.get_text(" ", strip=True) == source.get_text(" ", strip=True)
    assert [node.get_text() for node in final.select("th, td")] == [
        "Station", "Depth", "North Pier", "8",
    ]
    assert final.img["src"] == "harbor.png"
    assert final.a["href"] == "#arrival"
    assert all(final.find(id=row["block_id"]) is not None for row in rows)
    assert not final.find(wrapper).has_attr("id")
    # A table/figure remains one atomic citation, rather than overlapping rows.
    assert not final.select("td[id], th[id], figcaption[id]")


def test_source_ids_survive_main_to_section_wrapper_change():
    _, rows = _tag(
        f"<section>{STRUCTURED_CONTENT}</section>",
        source_html=f"<main>{STRUCTURED_CONTENT}</main>",
    )
    assert [row["source_element_ids"] for row in rows] == [
        [f"p007-b{ordinal}"] for ordinal in range(1, 7)
    ]
    assert all(row["source_original_page_number"] == 42 for row in rows)


@pytest.mark.parametrize("content", [
    "Unwrapped source text.",
    "Before <p>Separate paragraph.</p> After <em>inline text</em>.",
])
def test_unstructured_main_keeps_all_text_in_existing_coarse_citation(content):
    html = f"<main>{content}</main>"
    tagged, rows = _tag(html)
    expected = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
    assert len(rows) == 1
    assert rows[0]["block_kind"] == "other"
    assert rows[0]["text_quote"] == expected
    assert rows[0]["source_element_ids"] == ["p007-b1"]
    assert BeautifulSoup(tagged, "html.parser").get_text(" ", strip=True) == expected


def test_empty_main_does_not_invent_a_citation():
    _, rows = _tag("<main> \n <!-- comment only --> </main>")
    assert rows == []


@pytest.mark.parametrize("wrapper", ["div", "article", "section"])
def test_existing_wrapper_retains_explicit_child_figure_ownership(wrapper):
    html = (
        f'<{wrapper}>Introductory text.'
        '<figure data-doc-web-source-page-number="8" '
        'data-doc-web-source-crop-filename="page008.png">'
        '<img src="page008.png" alt="Harbor"/></figure>'
        f'</{wrapper}>'
    )
    _, rows = _tag_entry_body(
        {
            "filename": "chapter-001.html",
            "body_html": html,
            "source_pages": [7, 8],
            "prepared_pages": [
                {"html": "<p>Introductory text.</p>", "page_number": 7,
                 "original_page_number": 42},
                {"html": '<figure><img src="page008.png" alt="Harbor"/></figure>',
                 "page_number": 8, "original_page_number": 43},
            ],
        },
        run_id="container-citation-test",
        created_at="2026-10-23T00:00:00Z",
    )
    figure = next(row for row in rows if row["block_kind"] == "figure")
    assert figure["source_page_number"] == 8
    assert figure["source_original_page_number"] == 43
    assert figure["source_element_ids"] == ["p008-b1", "crop:page008.png"]
