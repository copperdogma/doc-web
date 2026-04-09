import json

import pytest

from benchmarks.scorers.approved_intake_handoff import score_case, summarize_results
from benchmarks.scripts.run_approved_intake_handoff_eval import (
    DEFAULT_CORPUS,
    SUPPORTED_INPUT_KINDS,
    build_first_downstream_artifact_path,
    load_first_stage_spec,
    run_case,
)


def test_load_first_stage_spec_for_pdf_ocr_recipe():
    stage = load_first_stage_spec("configs/recipes/recipe-pdf-ocr-html-mvp.yaml")

    assert stage == {
        "stage_id": "pdf_to_images",
        "module": "extract_pdf_images_fast_v1",
        "out": "pages_images_manifest.jsonl",
    }


def test_load_first_stage_spec_for_images_recipe():
    stage = load_first_stage_spec("configs/recipes/recipe-images-ocr-html-mvp.yaml")

    assert stage == {
        "stage_id": "images_to_manifest",
        "module": "images_dir_to_manifest_v1",
        "out": "pages_images_manifest.jsonl",
    }


def test_build_first_downstream_artifact_path_for_marker_recipe():
    stage = load_first_stage_spec("configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml")

    assert build_first_downstream_artifact_path("story178-born", stage) == (
        "output/runs/story178-born/01_extract_pdf_marker_lite_html_v1/pages_html.jsonl"
    )


def test_build_first_downstream_artifact_path_for_images_recipe():
    stage = load_first_stage_spec("configs/recipes/recipe-images-ocr-html-mvp.yaml")

    assert build_first_downstream_artifact_path("story180-images", stage) == (
        "output/runs/story180-images/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl"
    )


def test_score_case_requires_launched_artifact_for_launchable_recipe():
    result = score_case(
        {"expected_recipe": "configs/recipes/recipe-pdf-ocr-html-mvp.yaml"},
        {
            "recommended_recipe": "configs/recipes/recipe-pdf-ocr-html-mvp.yaml",
            "handoff_artifact": "output/runs/story178-scan/intake_handoff.jsonl",
            "terminal_outcome": "launched",
            "terminal_reason": None,
            "downstream_run_id": "story178-scan-recipe-pdf-ocr-html-mvp",
            "first_downstream_artifact": "output/runs/story178-scan-recipe-pdf-ocr-html-mvp/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl",
        },
    )

    assert result["pass"] is True
    assert result["checks"]["first_downstream_artifact"] is True


def test_score_case_requires_explicit_skip_for_no_recipe_needed():
    result = score_case(
        {"expected_recipe": "no-recipe-needed"},
        {
            "recommended_recipe": "no-recipe-needed",
            "handoff_artifact": "output/runs/story178-skip/intake_handoff.jsonl",
            "terminal_outcome": "skipped",
            "terminal_reason": "no_recipe_needed",
            "downstream_run_id": None,
            "first_downstream_artifact": None,
        },
    )

    assert result["pass"] is True
    assert result["checks"]["no_first_downstream_artifact"] is True


def test_summarize_results_counts_failed_runs_in_pass_rate_denominator():
    rows = [
        {
            "status": "ok",
            "terminal_outcome": "launched",
            "score": {"pass": True, "score": 1.0},
        },
        {
            "status": "failed",
            "terminal_outcome": None,
            "score": {"pass": False, "score": 0.0},
        },
    ]

    summary = summarize_results(rows)

    assert summary["docs"] == 2
    assert summary["completed"] == 1
    assert summary["failed_runs"] == 1
    assert summary["pass_rate"] == 0.5


def test_approved_intake_handoff_corpus_stays_within_supported_scope():
    corpus = json.loads(DEFAULT_CORPUS.read_text(encoding="utf-8"))

    assert {case["input_kind"] for case in corpus} == set(SUPPORTED_INPUT_KINDS)


@pytest.mark.parametrize(
    ("input_kind", "path", "boundary_reason", "scope_policy"),
    [
        (
            "docx",
            "testdata/docx-mini.docx",
            "outside_approved_intake_handoff:docx:direct_explicit_recipe_only",
            "direct_explicit_recipe_only",
        ),
        (
            "xlsx",
            "testdata/xlsx-mini.xlsx",
            "outside_approved_intake_handoff:xlsx:direct_explicit_recipe_only",
            "direct_explicit_recipe_only",
        ),
        (
            "pptx",
            "testdata/pptx-mini.pptx",
            "outside_approved_intake_handoff:pptx:direct_explicit_recipe_only",
            "direct_explicit_recipe_only",
        ),
        (
            "web-page",
            "testdata/web-page-mini.html",
            "outside_approved_intake_handoff:web-page:direct_explicit_recipe_only",
            "direct_explicit_recipe_only",
        ),
    ],
)
def test_approved_intake_handoff_blocks_direct_entry_only_inputs_with_explicit_scope_reason(
    tmp_path,
    input_kind,
    path,
    boundary_reason,
    scope_policy,
):
    row = run_case(
        {
            "id": f"scope-{input_kind}",
            "input_kind": input_kind,
            "path": path,
            "expected_recipe": "no-recipe-needed",
        },
        tmp_path,
    )

    assert row["status"] == "blocked"
    assert row["failure_step"] == "scope"
    assert row["boundary_reason"] == boundary_reason
    assert row["scope_policy"] == scope_policy
    assert row["supported_input_kinds"] == sorted(SUPPORTED_INPUT_KINDS)
