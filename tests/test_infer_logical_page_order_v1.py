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


def test_portrait_body_ranges_do_not_claim_physical_spreads_or_printed_labels(tmp_path: Path) -> None:
    labels = parse_spread_labels("On a roll of 1-6, choose an outcome.\n\fRoll 2-3 gives supplies.\n\f")
    rows = [{"page": page, "page_number": page, "original_page_number": page,
             "spread_side": None, "image": f"/tmp/page{page}.png", "source": ["portrait.pdf"]}
            for page in [1, 2]]
    page_map = build_logical_page_map(rows, labels, run_id="test", split_manifest=tmp_path / "split.jsonl",
                                      pdf=None, min_confidence=.7)
    assert page_map["summary"]["physical_spread_count"] == 0
    assert page_map["physical_spreads"] == []
    assert all(row["printed_spread_label"] is None and row["label_source_line"] is None
               for row in page_map["logical_pages"])
    assert [row["image"] for row in build_reordered_manifest(page_map, run_id="test")] == [row["image"] for row in rows]
    assert page_map["summary"]["complete"] is True


def test_unlabelled_physical_split_is_counted_without_inventing_a_label(tmp_path: Path) -> None:
    rows = [{"page": 1, "page_number": i, "original_page_number": 1,
             "spread_side": side, "image": f"/tmp/{side}.png"} for i, side in [(1, "L"), (2, "R")]]
    page_map = build_logical_page_map(rows, {}, run_id="test", split_manifest=tmp_path / "split.jsonl",
                                      pdf=None, min_confidence=.7)
    assert page_map["summary"]["physical_spread_count"] == 1
    assert page_map["physical_spreads"][0]["printed_spread_label"] is None
    assert page_map["summary"]["complete"] is False
