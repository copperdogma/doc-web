from bs4 import BeautifulSoup

from modules.transform.repair_docling_onward_genealogy_v1.main import (
    PageSignal,
    find_candidate_heading,
    replace_first_table_to_end,
    replace_heading_to_end,
    replace_onset_before_first_table,
    select_target_pages,
    summarize_html_signals,
)


def _signal(page_no: int, *, table_count: int, reasons: list[str]) -> PageSignal:
    return PageSignal(
        page_no=page_no,
        printed_page_number=None,
        text_count=0,
        table_count=table_count,
        baseline_text_refs=[],
        baseline_table_refs=[],
        text_samples=[],
        table_leak_samples=[],
        header_spill_count=0,
        heading_text_count=0,
        inline_heading_leak_count=0,
        combined_boy_girl_count=0,
        summary_label_count=0,
        reasons=reasons,
        signal_score=0,
    )


def test_select_target_pages_picks_onset_span() -> None:
    page_signals = [
        _signal(1, table_count=0, reasons=[]),
        _signal(2, table_count=0, reasons=["header_spill_without_table"]),
        _signal(3, table_count=1, reasons=[]),
        _signal(4, table_count=2, reasons=[]),
    ]

    assert select_target_pages("onset_before_first_table", page_signals) == [2, 3]


def test_select_target_pages_picks_trailing_spill_block() -> None:
    page_signals = [
        _signal(1, table_count=0, reasons=[]),
        _signal(2, table_count=1, reasons=[]),
        _signal(3, table_count=1, reasons=[]),
        _signal(4, table_count=0, reasons=["heading_spill_without_table"]),
    ]

    assert select_target_pages("later_spill_after_leaky_tables", page_signals) == [2, 3, 4]


def test_select_target_pages_picks_wide_genealogy_block_from_first_table() -> None:
    page_signals = [
        _signal(1, table_count=0, reasons=["heading_spill_without_table"]),
        _signal(2, table_count=1, reasons=["inline_heading_leaks_in_table"]),
        _signal(3, table_count=1, reasons=["inline_heading_leaks_in_table"]),
        _signal(4, table_count=1, reasons=["combined_boy_girl_header_in_table"]),
        _signal(5, table_count=0, reasons=[]),
    ]

    assert select_target_pages("wide_genealogy_block_from_first_table", page_signals) == [2, 3, 4]


def test_replace_onset_before_first_table_replaces_leaky_pretable_block() -> None:
    full_html = """
    <html><body>
      <h2>Arthur L'Heureux</h2>
      <p>NAME BORN MARRIED SPOUSE BOY GIRL DIED</p>
      <p>ARTHUR'S FAMILY Barbara leak</p>
      <table><tr><th>NAME</th></tr><tr><td>Old row</td></tr></table>
      <p>After table</p>
    </body></html>
    """
    merged_excerpt = """
    <h2>Arthur L'Heureux</h2>
    <table>
      <tr class="genealogy-subgroup-heading"><th colspan="7">ARTHUR'S FAMILY</th></tr>
      <tr><td>Barbara</td></tr>
    </table>
    """

    replaced = replace_onset_before_first_table(full_html, "Arthur L'Heureux", merged_excerpt)

    assert "Old row" not in replaced
    assert "NAME BORN MARRIED SPOUSE" not in replaced
    assert 'class="genealogy-subgroup-heading"' in replaced
    assert "Barbara" in replaced
    assert "After table" in replaced


def test_replace_first_table_to_end_replaces_trailing_spill_section() -> None:
    full_html = """
    <html><body>
      <h2>Pierre L'Heureux</h2>
      <table><tr><th>NAME</th></tr><tr><td>Old first block</td></tr></table>
      <p>JACQUELINE'S FAMILY leak</p>
      <p>TOTAL DESCENDANTS 101</p>
    </body></html>
    """
    merged_excerpt = """
    <table>
      <tr class="genealogy-subgroup-heading"><th colspan="7">JACQUELINE'S FAMILY</th></tr>
      <tr><td>Jacqueline</td></tr>
    </table>
    <table>
      <tr><th>TOTAL DESCENDANTS</th><th>101</th></tr>
    </table>
    """

    replaced = replace_first_table_to_end(full_html, "Pierre L'Heureux", merged_excerpt)

    assert "Old first block" not in replaced
    assert "TOTAL DESCENDANTS 101" not in replaced
    assert 'class="genealogy-subgroup-heading"' in replaced
    assert "Jacqueline" in replaced
    assert "<h2>Pierre L'Heureux</h2>" in replaced


def test_find_candidate_heading_accepts_punctuation_variant_near_first_table() -> None:
    html = """
    <html><body>
      <h2>Marie-Louise (L'Heureux) LaClare</h2>
      <p>Intro paragraph</p>
      <h2>Marie Louise L'Heureux LaClare</h2>
      <p>Mark</p>
      <table><tr><th>NAME</th></tr><tr><td>Old row</td></tr></table>
    </body></html>
    """

    heading = find_candidate_heading(BeautifulSoup(html, "html.parser"), "Marie-Louise (L'Heureux) LaClare")

    assert heading is not None
    assert heading.get_text(" ", strip=True) == "Marie Louise L'Heureux LaClare"


def test_replace_heading_to_end_preserves_intro_before_later_genealogy_heading() -> None:
    full_html = """
    <html><body>
      <h2>Marie-Louise (L'Heureux) LaClare</h2>
      <p>Intro paragraph</p>
      <h2>Marie Louise L'Heureux LaClare</h2>
      <p>Mark</p>
      <table><tr><th>NAME</th></tr><tr><td>Old row</td></tr></table>
    </body></html>
    """
    merged_excerpt = """
    <h2>Marie Louise L'Heureux LaClare</h2>
    <table>
      <tr class="genealogy-subgroup-heading"><th colspan="7">LEOPOLD'S FAMILY</th></tr>
      <tr><td>Clemence</td></tr>
    </table>
    """

    replaced = replace_heading_to_end(
        full_html,
        "Marie-Louise (L'Heureux) LaClare",
        merged_excerpt,
    )

    assert "Intro paragraph" in replaced
    assert "Mark" not in replaced
    assert "Old row" not in replaced
    assert "LEOPOLD'S FAMILY" in replaced


def test_summarize_html_signals_counts_subgroup_rows_and_leaks() -> None:
    html = """
    <html><body>
      <h2>Pierre L'Heureux</h2>
      <table>
        <tr><th>NAME</th><th>BOY/GIRL</th></tr>
        <tr><td>JACQUELINE'S FAMILY</td><td></td></tr>
      </table>
      <p>TOTAL DESCENDANTS 101</p>
    </body></html>
    """

    summary = summarize_html_signals(html, "Pierre L'Heureux")

    assert summary["table_heading_leak_count"] == 1
    assert summary["combined_boy_girl_header_count"] == 1
    assert summary["heading_like_block_count"] >= 1
    assert summary["subgroup_row_count"] == 0
