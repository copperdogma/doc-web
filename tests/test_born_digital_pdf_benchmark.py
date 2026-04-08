import json
from pathlib import Path

from benchmarks.scorers.born_digital_pdf import score_case, summarize_results
from benchmarks.scripts.run_born_digital_pdf_eval import (
    DEFAULT_CORPUS,
    load_corpus,
    materialize_case_recipe,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def test_score_case_passes_for_supported_book_like_fixture(tmp_path: Path):
    run_dir = tmp_path / "run"
    _write_jsonl(
        run_dir / "01_extract_pdf_marker_lite_html_v1" / "pages_html.jsonl",
        [
            {"page_number": 1, "html": "<h1>Title</h1>"},
            {"page_number": 2, "html": "<h4>Preparing the interview kit</h4>"},
            {"page_number": 3, "html": "<h4>Publishing notes</h4>"},
        ],
    )
    _write_jsonl(
        run_dir / "03_portionize_toc_html_v1" / "portions_toc.jsonl",
        [
            {"title": "Preparing the interview kit"},
            {"title": "Publishing notes"},
        ],
    )
    bundle_dir = run_dir / "output" / "html"
    _write_json(
        bundle_dir / "manifest.json",
        {
            "title": "Book",
            "entries": [
                {"entry_id": "page-001", "title": "Image 1", "path": "page-001.html", "source_pages": [1]},
                {
                    "entry_id": "chapter-001",
                    "title": "Preparing the interview kit",
                    "path": "chapter-001.html",
                    "source_pages": [2],
                },
                {
                    "entry_id": "chapter-002",
                    "title": "Publishing notes",
                    "path": "chapter-002.html",
                    "source_pages": [3],
                },
            ],
            "reading_order": ["page-001", "chapter-001", "chapter-002"],
        },
    )
    (bundle_dir / "page-001.html").write_text(
        "<h1>Neighborhood Oral History Handbook -- Mini</h1><h3>Contents</h3><p>Preparing the interview kit ........ 2</p>",
        encoding="utf-8",
    )
    (bundle_dir / "chapter-001.html").write_text(
        "<h4>Preparing the interview kit</h4><p>Bring two pencils, not one.</p>",
        encoding="utf-8",
    )
    (bundle_dir / "chapter-002.html").write_text(
        "<h4>Publishing notes</h4><p>Repeatable close-out is not glamorous.</p>",
        encoding="utf-8",
    )
    _write_jsonl(
        bundle_dir / "provenance" / "blocks.jsonl",
        [
            {
                "entry_id": "page-001",
                "block_kind": "heading",
                "source_page_number": 1,
                "source_element_ids": ["p001-b4"],
                "text_quote": "Contents",
            },
            {
                "entry_id": "chapter-001",
                "block_kind": "heading",
                "source_page_number": 2,
                "source_element_ids": ["p002-b1"],
                "text_quote": "Preparing the interview kit",
            },
            {
                "entry_id": "chapter-002",
                "block_kind": "paragraph",
                "source_page_number": 3,
                "source_element_ids": ["p003-b2"],
                "text_quote": "Repeatable close-out is not glamorous.",
            },
        ],
    )

    result = score_case(
        {
            "portion_artifact": "03_portionize_toc_html_v1/portions_toc.jsonl",
            "expected_pages_html_rows": 3,
            "expected_page_numbers": [1, 2, 3],
            "expected_portion_rows": 2,
            "expected_portion_titles": ["Preparing the interview kit", "Publishing notes"],
            "expected_manifest_title": "Book",
            "expected_entry_titles": ["Image 1", "Preparing the interview kit", "Publishing notes"],
            "provenance_mode": "paged",
            "min_provenance_rows": 3,
            "html_assertions": [
                {"entry_title": "Image 1", "snippets": ["Contents", "Preparing the interview kit ........ 2"]},
                {"entry_title": "Preparing the interview kit", "snippets": ["Bring two pencils, not one."]},
                {"entry_title": "Publishing notes", "snippets": ["Repeatable close-out is not glamorous."]},
            ],
            "provenance_assertions": [
                {
                    "entry_title": "Image 1",
                    "block_kind": "heading",
                    "source_page_number": 1,
                    "source_element_prefix": "p001-",
                    "text_quote_contains": "Contents",
                },
                {
                    "entry_title": "Preparing the interview kit",
                    "block_kind": "heading",
                    "source_page_number": 2,
                    "source_element_prefix": "p002-",
                    "text_quote_contains": "Preparing the interview kit",
                },
                {
                    "entry_title": "Publishing notes",
                    "block_kind": "paragraph",
                    "source_page_number": 3,
                    "source_element_prefix": "p003-",
                    "text_quote_contains": "Repeatable close-out is not glamorous",
                },
            ],
        },
        run_dir,
    )

    assert result["pass"] is True
    assert result["checks"]["pages_html_rows"] is True
    assert result["checks"]["portion_titles"] is True


def test_score_case_passes_for_minimal_optional_comparison_case(tmp_path: Path):
    run_dir = tmp_path / "run"
    _write_jsonl(
        run_dir / "01_extract_pdf_marker_lite_html_v1" / "pages_html.jsonl",
        [{"page_number": 1, "html": "<p>One</p>"}, {"page_number": 2, "html": "<p>Two</p>"}],
    )
    _write_jsonl(
        run_dir / "03_portionize_headings_html_v1" / "portions_non_toc.jsonl",
        [{"title": "Flat section"}],
    )
    bundle_dir = run_dir / "output" / "html"
    _write_json(
        bundle_dir / "manifest.json",
        {
            "title": "Book",
            "entries": [{"entry_id": "chapter-001", "title": "Flat section", "path": "chapter-001.html", "source_pages": [1, 2]}],
            "reading_order": ["chapter-001"],
        },
    )
    (bundle_dir / "chapter-001.html").write_text("<p>Flat section body</p>", encoding="utf-8")
    _write_jsonl(
        bundle_dir / "provenance" / "blocks.jsonl",
        [
            {
                "entry_id": "chapter-001",
                "block_kind": "paragraph",
                "source_page_number": 1,
                "source_element_ids": ["p001-b1"],
                "text_quote": "Flat section body",
            }
        ],
    )

    result = score_case(
        {
            "portion_artifact": "03_portionize_headings_html_v1/portions_non_toc.jsonl",
            "expected_pages_html_rows": 2,
            "expected_page_numbers": [1, 2],
            "min_portion_rows": 1,
            "expected_manifest_title": "Book",
            "min_entry_count": 1,
            "min_provenance_rows": 1,
        },
        run_dir,
    )

    assert result["pass"] is True
    assert result["checks"]["entry_min_count"] is True
    assert result["checks"]["provenance_min_rows"] is True


def test_materialize_case_recipe_adds_unique_marker_container(tmp_path: Path):
    recipe_path = tmp_path / "recipe.yaml"
    recipe_path.write_text(
        "input:\n  pdf: test.pdf\nstages:\n  - id: marker_lite_html\n    stage: extract\n    module: extract_pdf_marker_lite_html_v1\n    out: pages_html.jsonl\n    params:\n      container_name: old-name\n",
        encoding="utf-8",
    )

    case = {
        "id": "born-digital-handbook-mini",
        "input_kind": "pdf",
        "recipe": str(recipe_path),
    }

    materialized_path, container_name = materialize_case_recipe(case, tmp_path / "story196-born-digital-benchmark")
    materialized = materialized_path.read_text(encoding="utf-8")

    assert container_name is not None
    assert len(container_name) <= 63
    assert container_name in materialized
    assert container_name.startswith("born-digital-bench-story196-born-digital-benchmark-born-digital")


def test_load_corpus_keeps_supported_and_comparison_rows():
    corpus = load_corpus(DEFAULT_CORPUS, None)

    supported = [case for case in corpus if case["classification"] == "supported"]
    comparison = [case for case in corpus if case["classification"] == "comparison-only"]

    assert {case["id"] for case in supported} == {
        "tbotb-mini",
        "born-digital-handbook-mini",
        "flat-born-digital-mini",
        "flat-born-digital-form-mini",
    }
    assert {case["id"] for case in comparison} == {"rfp", "release-forms"}


def test_summarize_results_tracks_supported_vs_comparison():
    summary = summarize_results(
        [
            {
                "status": "ok",
                "required": True,
                "classification": "supported",
                "lane": "book-like",
                "score": {"pass": True, "score": 1.0},
            },
            {
                "status": "ok",
                "required": True,
                "classification": "supported",
                "lane": "flat-non-toc",
                "score": {"pass": False, "score": 0.25},
            },
            {
                "status": "skipped",
                "required": False,
                "classification": "comparison-only",
                "lane": "flat-non-toc",
            },
        ]
    )

    assert summary["supported_docs"] == 2
    assert summary["comparison_docs"] == 1
    assert summary["skipped_optional"] == 1
    assert summary["pass_rate"] == 0.5
