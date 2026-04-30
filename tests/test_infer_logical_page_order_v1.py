from __future__ import annotations

from pathlib import Path

from modules.extract.infer_logical_page_order_v1.main import (
    build_logical_page_map,
    build_reordered_manifest,
    parse_spread_labels,
)


def test_parse_spread_labels_prefers_footer_print_label() -> None:
    labels = parse_spread_labels(
        "body says steps 2-3 may repeat\nfooter sample.indd 4-1\n\f"
        "footer sample.indd 2-3\n\f"
    )

    assert labels[1].left_printed_page == 4
    assert labels[1].right_printed_page == 1
    assert labels[2].pair_label == "2-3"
    assert labels[1].confidence >= 0.7


def test_logical_page_map_sorts_split_halves_by_printed_reader_order(tmp_path: Path) -> None:
    labels = parse_spread_labels("footer sample.indd 4-1\n\ffooter sample.indd 2-3\n\f")
    split_rows = [
        {"page": 1, "original_page_number": 1, "page_number": 1, "spread_side": "L", "image": "/tmp/001L.png", "source": ["sample.pdf"]},
        {"page": 1, "original_page_number": 1, "page_number": 2, "spread_side": "R", "image": "/tmp/001R.png", "source": ["sample.pdf"]},
        {"page": 2, "original_page_number": 2, "page_number": 3, "spread_side": "L", "image": "/tmp/002L.png", "source": ["sample.pdf"]},
        {"page": 2, "original_page_number": 2, "page_number": 4, "spread_side": "R", "image": "/tmp/002R.png", "source": ["sample.pdf"]},
    ]

    page_map = build_logical_page_map(
        split_rows,
        labels,
        run_id="test",
        split_manifest=tmp_path / "split.jsonl",
        pdf=tmp_path / "sample.pdf",
        min_confidence=0.7,
    )
    ordered_manifest = build_reordered_manifest(page_map, run_id="test")

    ordered_sources = [
        (page["logical_page"], page["physical_sheet"], page["spread_side"])
        for page in page_map["logical_pages"]
    ]
    assert ordered_sources == [(1, 1, "R"), (2, 2, "L"), (3, 2, "R"), (4, 1, "L")]
    assert page_map["summary"]["complete"] is True
    assert ordered_manifest[0]["page_number"] == 1
    assert ordered_manifest[0]["original_page_number"] == 1
    assert ordered_manifest[-1]["spread_side"] == "L"


def test_logical_page_map_flags_missing_split_label(tmp_path: Path) -> None:
    page_map = build_logical_page_map(
        [{"page": 1, "original_page_number": 1, "page_number": 1, "spread_side": "L", "image": "/tmp/001L.png"}],
        {},
        run_id="test",
        split_manifest=tmp_path / "split.jsonl",
        pdf=None,
        min_confidence=0.7,
    )

    assert page_map["summary"]["complete"] is False
    assert page_map["issues"][0]["type"] == "missing_printed_page_label"
