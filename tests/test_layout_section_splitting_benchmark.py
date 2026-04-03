import json
from pathlib import Path

from benchmarks.scorers.layout_section_splitting import (
    score_bundle_case,
    score_case_challenger,
    summarize_results,
)
from benchmarks.scripts.run_layout_section_splitting_eval import materialize_case_recipe


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def test_score_bundle_case_passes_for_pageless_docx_bundle(tmp_path: Path):
    bundle_dir = tmp_path / "output" / "html"
    _write_json(
        bundle_dir / "manifest.json",
        {
            "entries": [
                {"entry_id": "chapter-001", "title": "Overview", "path": "chapter-001.html", "source_pages": []},
                {"entry_id": "chapter-002", "title": "Appendix", "path": "chapter-002.html", "source_pages": []},
            ],
            "reading_order": ["chapter-001", "chapter-002"],
            "title": "DOCX Nested Fixture",
        },
    )
    (bundle_dir / "chapter-001.html").write_text(
        "<h1>Overview</h1><h2>Subsection A</h2><p>First bullet</p>",
        encoding="utf-8",
    )
    (bundle_dir / "chapter-002.html").write_text(
        "<h1>Appendix</h1><p>Closing section.</p>",
        encoding="utf-8",
    )
    _write_jsonl(
        bundle_dir / "provenance" / "blocks.jsonl",
        [
            {
                "entry_id": "chapter-001",
                "block_kind": "heading",
                "source_element_ids": ["abc"],
                "source_page_number": None,
                "text_quote": "Subsection A",
            },
            {
                "entry_id": "chapter-002",
                "block_kind": "paragraph",
                "source_element_ids": ["def"],
                "source_page_number": None,
                "text_quote": "Closing section.",
            },
        ],
    )

    result = score_bundle_case(
        {
            "expected_manifest_title": "DOCX Nested Fixture",
            "provenance_mode": "pageless",
            "expected_entry_titles": ["Overview", "Appendix"],
            "html_assertions": [
                {"entry_title": "Overview", "snippets": ["Subsection A", "First bullet"]},
                {"entry_title": "Appendix", "snippets": ["Closing section."]},
            ],
            "provenance_assertions": [
                {"entry_title": "Overview", "block_kind": "heading", "text_quote_contains": "Subsection A"},
                {"entry_title": "Appendix", "block_kind": "paragraph", "text_quote_contains": "Closing section."},
            ],
        },
        bundle_dir,
    )

    assert result["pass"] is True
    assert result["checks"]["provenance_source_page_numbers_absent"] is True


def test_score_bundle_case_flags_missing_section_snippet(tmp_path: Path):
    bundle_dir = tmp_path / "output" / "html"
    _write_json(
        bundle_dir / "manifest.json",
        {
            "entries": [
                {"entry_id": "chapter-001", "title": "Participant information:", "path": "chapter-001.html", "source_pages": [1]},
            ],
            "reading_order": ["chapter-001"],
            "title": "Book",
        },
    )
    (bundle_dir / "chapter-001.html").write_text(
        "<h2>Participant information:</h2><p>Emergency contact:</p>",
        encoding="utf-8",
    )
    _write_jsonl(
        bundle_dir / "provenance" / "blocks.jsonl",
        [
            {
                "entry_id": "chapter-001",
                "block_kind": "heading",
                "source_element_ids": ["p001-b3"],
                "source_page_number": 1,
                "text_quote": "Participant information:",
            }
        ],
    )

    result = score_bundle_case(
        {
            "provenance_mode": "paged",
            "expected_entry_titles": ["Participant information:"],
            "html_assertions": [
                {
                    "entry_title": "Participant information:",
                    "snippets": ["Emergency contact:", "Required acknowledgments:"],
                }
            ],
            "provenance_assertions": [
                {
                    "entry_title": "Participant information:",
                    "block_kind": "heading",
                    "source_page_number": 1,
                    "source_element_prefix": "p001-",
                    "text_quote_contains": "Participant information:",
                }
            ],
        },
        bundle_dir,
    )

    assert result["pass"] is False
    assert result["checks"]["html_assertions"] is False


def test_score_case_challenger_marks_docx_single_entry_baseline_not_competitive(tmp_path: Path):
    run_dir = tmp_path / "run"
    _write_jsonl(
        run_dir / "01_unstructured_docx_intake_v1" / "elements.jsonl",
        [
            {"type": "Title", "text": "DOCX Nested Fixture", "metadata": {"category_depth": 0}, "id": "doc"},
            {"type": "Title", "text": "Overview", "metadata": {"category_depth": 0}, "id": "a"},
            {"type": "Title", "text": "Appendix", "metadata": {"category_depth": 0}, "id": "b"},
        ],
    )

    result = score_case_challenger(
        {
            "expected_manifest_title": "DOCX Nested Fixture",
            "expected_entry_titles": ["Overview", "Appendix"],
            "challenger": {
                "kind": "docx_first_title_only",
                "artifact": "01_unstructured_docx_intake_v1/elements.jsonl",
            },
        },
        run_dir,
    )

    assert result is not None
    assert result["pass"] is False
    assert result["honest_competitor"] is False
    assert result["actual"]["predicted_entry_titles"] == ["Overview"]


def test_materialize_case_recipe_adds_unique_marker_container(tmp_path: Path):
    recipe_path = tmp_path / "recipe.yaml"
    recipe_path.write_text(
        "input:\n  pdf: test.pdf\nstages:\n  - id: marker_lite_html\n    stage: extract\n    module: extract_pdf_marker_lite_html_v1\n    out: pages_html.jsonl\n    params:\n      container_name: old-name\n",
        encoding="utf-8",
    )

    case = {
        "id": "flat-born-digital-mini",
        "family": "born-digital-pdf",
        "recipe": str(recipe_path),
    }

    materialized_path, container_name = materialize_case_recipe(case, tmp_path / "story181-layout-benchmark")
    materialized = materialized_path.read_text(encoding="utf-8")

    assert container_name is not None
    assert "layout-bench-story181-layout-benchmark-flat-born-digital-mini" in materialized


def test_summarize_results_counts_challenger_signal():
    summary = summarize_results(
        [
            {
                "status": "ok",
                "family": "docx",
                "score": {"pass": True, "score": 1.0},
                "challenger": {"score": 0.25, "honest_competitor": False},
            },
            {
                "status": "failed",
                "family": "born-digital-pdf",
                "score": {"pass": False, "score": 0.0},
                "challenger": None,
            },
        ]
    )

    assert summary["docs"] == 2
    assert summary["failed_runs"] == 1
    assert summary["challenger_cases"] == 1
    assert summary["challenger_real_competitors"] == 0
