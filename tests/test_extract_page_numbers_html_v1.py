from __future__ import annotations

from modules.transform.extract_page_numbers_html_v1.main import _extract_printed_page_number


def test_extract_page_number_prefers_logical_page_when_footer_is_spread_range() -> None:
    html = '<p>Rules continue.</p><p class="page-number">8-9</p>'

    assert _extract_printed_page_number(html, source_page_number=8)["printed_page_number"] == 8
    assert _extract_printed_page_number(html, source_page_number=9)["printed_page_number"] == 9


def test_extract_page_number_keeps_legacy_last_digit_when_no_source_match() -> None:
    html = '<p>Rules continue.</p><p class="page-number">8-9</p>'

    assert _extract_printed_page_number(html, source_page_number=10)["printed_page_number"] == 9
