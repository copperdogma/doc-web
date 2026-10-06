from __future__ import annotations

from modules.transform.extract_page_numbers_html_v1.main import _extract_printed_page_number


def test_extract_page_number_prefers_logical_page_when_footer_is_spread_range() -> None:
    html = '<p>Rules continue.</p><p class="page-number">8-9</p>'

    assert _extract_printed_page_number(html, source_page_number=8)["printed_page_number"] == 8
    assert _extract_printed_page_number(html, source_page_number=9)["printed_page_number"] == 9


def test_extract_page_number_keeps_legacy_last_digit_when_no_source_match() -> None:
    html = '<p>Rules continue.</p><p class="page-number">8-9</p>'

    assert _extract_printed_page_number(html, source_page_number=10)["printed_page_number"] == 9


def test_labeled_current_total_footer_uses_current_page_and_preserves_label() -> None:
    from modules.transform.extract_page_numbers_html_v1.main import extract_page_numbers

    rows = [
        {"page": 19, "page_number": 1, "original_page_number": 19, "html": '<p class="page-number">Star smuggler rules p.19/24</p>'},
        {"page": 20, "page_number": 2, "html": '<p class="page-number">Page14/80</p>'},
    ]

    result = extract_page_numbers(rows)

    assert [row["printed_page_number"] for row in result] == [19, 14]
    assert [row["printed_page_number_text"] for row in result] == [
        "Star smuggler rules p.19/24",
        "Page14/80",
    ]
    assert [row["original_page_number"] for row in result[:1]] == [19]
    assert [row["page"] for row in result] == [19, 20]


def test_bare_fraction_is_not_treated_as_a_printed_page_number() -> None:
    html = '<p class="page-number">1/6</p>'

    result = _extract_printed_page_number(html, source_page_number=1)

    assert result["printed_page_number"] is None
    assert result["printed_page_number_text"] == "1/6"


def test_catalog_number_before_title_is_not_a_printed_folio() -> None:
    from modules.transform.extract_page_numbers_html_v1.main import extract_page_numbers
    rows = [{"page_number": 1, "html": "<p>8735</p><h1>Events booklet</h1><p>Rules continue.</p>"},
            {"page_number": 2, "html": "<p>Second page.</p>"}]
    result = extract_page_numbers(rows)
    assert [row["printed_page_number"] for row in result] == [None, None]
    assert [row["html"] for row in result] == [row["html"] for row in rows]
    assert [row["page_number"] for row in result] == [1, 2]


def test_catalog_cover_does_not_poison_corroborated_body_footers() -> None:
    from modules.transform.extract_page_numbers_html_v1.main import extract_page_numbers
    rows = [{"page_number": 1, "html": "<p>8735</p><h1>Booklet</h1>"}]
    rows.extend({"page_number": page, "html": f"<p>Body rules.</p><p>{page}</p>"} for page in range(2, 21))
    result = extract_page_numbers(rows)
    assert [row["printed_page_number"] for row in result[1:]] == list(range(2, 21))
    assert result[0]["printed_page_number"] != 8735
    assert result[0]["printed_page_number_inferred"] is True


def test_long_printed_folios_are_allowed_when_independently_corroborated() -> None:
    from modules.transform.extract_page_numbers_html_v1.main import extract_page_numbers
    rows = [{"page_number": page, "html": f"<p>Body.</p><p>{9000 + page}</p>"} for page in [1, 2]]
    rows.append({"page_number": 3, "html": "<p>Body.</p>"})
    result = extract_page_numbers(rows)
    assert [row["printed_page_number"] for row in result] == [9001, 9002, 9003]
    assert result[-1]["printed_page_number_inferred"] is True


def test_lone_terminal_outlier_never_numbers_the_remaining_book() -> None:
    from modules.transform.extract_page_numbers_html_v1.main import extract_page_numbers
    rows = [{"page_number": 1, "html": "<p>Body.</p><p>8735</p>"},
            {"page_number": 2, "html": "<p>Body.</p>"}]
    result = extract_page_numbers(rows)
    assert [row["printed_page_number"] for row in result] == [None, None]


def test_lone_explicit_folio_is_observed_without_extrapolation() -> None:
    from modules.transform.extract_page_numbers_html_v1.main import extract_page_numbers
    rows = [{"page_number": 1, "html": '<p>Body.</p><p class="page-number">100</p>'},
            {"page_number": 2, "html": "<p>Body.</p>"}]
    result = extract_page_numbers(rows)
    assert [row["printed_page_number"] for row in result] == [100, None]


def test_corroborated_labels_fill_an_internal_gap_and_preserve_imposed_ranges() -> None:
    from modules.transform.extract_page_numbers_html_v1.main import extract_page_numbers
    rows = [{"page_number": 8, "html": '<p class="page-number">8-9</p>'},
            {"page_number": 9, "html": '<p class="page-number">8-9</p>'},
            {"page_number": 10, "html": "<p>Body.</p>"},
            {"page_number": 11, "html": '<p class="page-number">11</p>'}]
    result = extract_page_numbers(rows)
    assert [row["printed_page_number"] for row in result] == [8, 9, 10, 11]
