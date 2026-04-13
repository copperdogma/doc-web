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
            "email-eml",
            "testdata/email-eml-mini.eml",
            "outside_recommendation_only_intake:email-eml:direct_explicit_recipe_only",
            "direct_explicit_recipe_only",
        ),
        (
            "email-mbox",
            "testdata/email-mbox-mini.mbox",
            "outside_recommendation_only_intake:email-mbox:direct_explicit_recipe_only",
            "direct_explicit_recipe_only",
        ),
        (
            "mixed-archive",
            "testdata/mixed-archive-mini.zip",
            "outside_recommendation_only_intake:mixed-archive:direct_explicit_recipe_only",
            "direct_explicit_recipe_only",
        ),
        (
            "mixed-folder",
            "testdata/mixed-folder-mini",
            "outside_recommendation_only_intake:mixed-folder:direct_explicit_recipe_only",
            "direct_explicit_recipe_only",
        ),
        (
            "epub",
            "testdata/epub-mini.epub",
            "outside_recommendation_only_intake:epub:direct_explicit_recipe_only",
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
            "outside_recommendation_only_intake:pptx:direct_explicit_recipe_only",
            "direct_explicit_recipe_only",
        ),
        (
            "web-page",
            "testdata/web-page-mini.html",
            "outside_recommendation_only_intake:web-page:direct_explicit_recipe_only",
            "direct_explicit_recipe_only",
        ),
    ],
)
def test_auto_book_type_detection_blocks_direct_entry_only_inputs_with_explicit_scope_reason(
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
