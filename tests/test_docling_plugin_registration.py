from docling_plugins.onward_layout_plugin import (
    is_genealogy_marker_text,
    page_supports_genealogy_merge,
)
from docling_plugins.onward_table_structure_plugin import (
    canonical_family_heading,
    has_combined_boy_girl_header,
    should_promote_heading_cell,
)


def test_canonical_family_heading_prefers_last_family_label() -> None:
    text = "Leonidas' Great Grandchildren Alice's Grandchildren CLAIRE'S FAMILY"
    assert canonical_family_heading(text) == "CLAIRE'S FAMILY"


def test_combined_boy_girl_header_detection() -> None:
    assert has_combined_boy_girl_header("BOY/GIRL")
    assert has_combined_boy_girl_header("BOY / GIRL")
    assert not has_combined_boy_girl_header("BOY")


def test_should_promote_heading_cell_requires_heading_like_text_and_span() -> None:
    assert should_promote_heading_cell(
        text="PATRICIA'S FAMILY",
        start_col_offset_idx=0,
        end_col_offset_idx=6,
        row_cell_count=1,
        num_cols=6,
        row_section=False,
    )
    assert not should_promote_heading_cell(
        text="CLARENCE'S FAMILY Chuck Jones",
        start_col_offset_idx=3,
        end_col_offset_idx=4,
        row_cell_count=2,
        num_cols=6,
        row_section=False,
    )
    assert should_promote_heading_cell(
        text="Leonidas' Grandchildren ALICE'S FAMILY",
        start_col_offset_idx=0,
        end_col_offset_idx=7,
        row_cell_count=1,
        num_cols=7,
        row_section=False,
    )


def test_should_promote_heading_cell_accepts_single_narrow_heading_rows() -> None:
    assert should_promote_heading_cell(
        text="BERNADETTE'S FAMILY",
        start_col_offset_idx=2,
        end_col_offset_idx=3,
        row_cell_count=1,
        num_cols=7,
        row_section=False,
    )


def test_is_genealogy_marker_text_accepts_family_and_split_headers() -> None:
    assert is_genealogy_marker_text("CLAUDE'S FAMILY")
    assert is_genealogy_marker_text("BOY / GIRL")
    assert not is_genealogy_marker_text("TOTAL DESCENDANTS")


def test_page_supports_genealogy_merge_requires_markers_and_skips_summary() -> None:
    assert page_supports_genealogy_merge(
        table_cluster_count=2,
        marker_hits=1,
        has_summary_labels=False,
    )
    assert page_supports_genealogy_merge(
        table_cluster_count=1,
        marker_hits=2,
        has_summary_labels=False,
    )
    assert not page_supports_genealogy_merge(
        table_cluster_count=2,
        marker_hits=1,
        has_summary_labels=True,
    )
