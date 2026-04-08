import json

import pytest

from benchmarks.scripts.run_auto_book_type_detection_eval import (
    DEFAULT_CORPUS,
    SUPPORTED_INPUT_KINDS,
    run_case,
)


def test_auto_book_type_detection_corpus_stays_pdf_only():
    corpus = json.loads(DEFAULT_CORPUS.read_text(encoding="utf-8"))

    assert {case["input_kind"] for case in corpus} == set(SUPPORTED_INPUT_KINDS)


@pytest.mark.parametrize(
    ("input_kind", "path", "boundary_reason", "scope_policy"),
    [
        (
            "docx",
            "testdata/docx-mini.docx",
            "outside_recommendation_only_intake:docx:direct_explicit_recipe_only",
            "direct_explicit_recipe_only",
        ),
        (
            "xlsx",
            "testdata/xlsx-mini.xlsx",
            "outside_recommendation_only_intake:xlsx:direct_explicit_recipe_only",
            "direct_explicit_recipe_only",
        ),
        (
            "pptx",
            "testdata/pptx-mini.pptx",
            "outside_recommendation_only_intake:pptx:runtime_blocked",
            "runtime_blocked",
        ),
    ],
)
def test_auto_book_type_detection_blocks_office_inputs_with_explicit_scope_reason(
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
            "expected_book_type": "other",
            "expected_recipe": "no-recipe-needed",
            "expected_major_signals": [],
        },
        tmp_path,
    )

    assert row["status"] == "blocked"
    assert row["failure_step"] == "scope"
    assert row["boundary_reason"] == boundary_reason
    assert row["scope_policy"] == scope_policy
    assert row["supported_input_kinds"] == sorted(SUPPORTED_INPUT_KINDS)
