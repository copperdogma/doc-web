import sys
from pathlib import Path

import pytest

from modules.intake.intake_plan_utils import (
    build_explicit_recipe_driver_command,
    choose_maintained_recipe,
    infer_archive_member_input_kind,
    prepare_confirmed_handoff,
)


def _plan(
    *,
    input_kind: str,
    has_extractable_text: bool | None = None,
    book_type: str = "other",
    signals: list[str] | None = None,
    tile_count: int = 0,
    recommended_recipe: str | None = None,
    source_images_dir: str | None = None,
    source_pdf: str | None = None,
):
    source_input = {
        "input_kind": input_kind,
        "has_extractable_text": has_extractable_text,
    }
    if source_images_dir:
        source_input["source_images_dir"] = source_images_dir
    if source_pdf:
        source_input["source_pdf"] = source_pdf
    return {
        "book_type": book_type,
        "signals": signals or [],
        "recommended_recipe": recommended_recipe,
        "meta": {
            "summary": {
                "tile_count": tile_count,
            },
            "source_input": source_input,
        },
    }


def test_choose_maintained_recipe_keeps_image_directory_lane():
    assert (
        choose_maintained_recipe(_plan(input_kind="images_dir"))
        == "configs/recipes/recipe-images-ocr-html-mvp.yaml"
    )


def test_choose_maintained_recipe_keeps_proven_born_digital_cyoa_lane():
    assert (
        choose_maintained_recipe(
            _plan(
                input_kind="pdf",
                has_extractable_text=True,
                book_type="cyoa",
                tile_count=3,
            )
        )
        == "configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml"
    )


def test_choose_maintained_recipe_routes_short_flat_born_digital_pdf_to_non_toc_lane():
    assert (
        choose_maintained_recipe(
            _plan(
                input_kind="pdf",
                has_extractable_text=True,
                book_type="other",
                tile_count=2,
            )
        )
        == "configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml"
    )


def test_choose_maintained_recipe_withholds_short_scanned_prose_pdf():
    assert (
        choose_maintained_recipe(
            _plan(
                input_kind="pdf",
                has_extractable_text=False,
                book_type="novel",
                tile_count=4,
            )
        )
        is None
    )


def test_choose_maintained_recipe_keeps_structured_scanned_pdf_lane():
    assert (
        choose_maintained_recipe(
            _plan(
                input_kind="pdf",
                has_extractable_text=False,
                book_type="other",
                signals=["tables", "images"],
                tile_count=6,
            )
        )
        == "configs/recipes/recipe-pdf-ocr-html-mvp.yaml"
    )


def test_prepare_confirmed_handoff_builds_launchable_images_command(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    plan = _plan(
        input_kind="images_dir",
        recommended_recipe="configs/recipes/recipe-images-ocr-html-mvp.yaml",
        source_images_dir=str(images_dir),
    )

    row, command, should_launch = prepare_confirmed_handoff(
        plan,
        plan_path=tmp_path / "overview_plan_final.jsonl",
        upstream_run_id="story176-images",
        dry_run=True,
    )

    assert should_launch is False
    assert row["terminal_outcome"] == "skipped"
    assert row["terminal_reason"] == "dry_run"
    assert row["launch_input_flag"] == "--input-images"
    assert row["launch_input_path"] == str(images_dir)
    assert row["downstream_run_id"] == "story176-images-recipe-images-ocr-html-mvp"
    assert command == row["driver_command"]
    assert "--input-images" in command
    assert str(images_dir) in command


def test_prepare_confirmed_handoff_builds_launchable_pdf_command(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n% story176\n")
    plan = _plan(
        input_kind="pdf",
        has_extractable_text=False,
        recommended_recipe="configs/recipes/recipe-pdf-ocr-html-mvp.yaml",
        source_pdf=str(pdf_path),
    )

    row, command, should_launch = prepare_confirmed_handoff(
        plan,
        plan_path=tmp_path / "overview_plan_final.jsonl",
        upstream_run_id="story176-pdf",
        dry_run=True,
    )

    assert should_launch is False
    assert row["terminal_outcome"] == "skipped"
    assert row["terminal_reason"] == "dry_run"
    assert row["launch_input_flag"] == "--input-pdf"
    assert row["launch_input_path"] == str(pdf_path)
    assert "--input-pdf" in command
    assert str(pdf_path) in command


def test_prepare_confirmed_handoff_forwards_downstream_end_at(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    plan = _plan(
        input_kind="images_dir",
        recommended_recipe="configs/recipes/recipe-images-ocr-html-mvp.yaml",
        source_images_dir=str(images_dir),
    )

    row, command, should_launch = prepare_confirmed_handoff(
        plan,
        plan_path=tmp_path / "overview_plan_final.jsonl",
        upstream_run_id="story176-end-at",
        downstream_end_at="images_to_manifest",
        dry_run=True,
    )

    assert should_launch is False
    assert row["terminal_reason"] == "dry_run"
    assert command[-2:] == ["--end-at", "images_to_manifest"]


def test_prepare_confirmed_handoff_skips_no_recipe_needed(tmp_path):
    plan = _plan(
        input_kind="pdf",
        has_extractable_text=False,
        recommended_recipe="no-recipe-needed",
        source_pdf=str(tmp_path / "missing.pdf"),
    )

    row, command, should_launch = prepare_confirmed_handoff(
        plan,
        plan_path=tmp_path / "overview_plan_final.jsonl",
        upstream_run_id="story176-skip",
    )

    assert should_launch is False
    assert command == []
    assert row["terminal_outcome"] == "skipped"
    assert row["terminal_reason"] == "no_recipe_needed"


def test_prepare_confirmed_handoff_blocks_missing_source_input(tmp_path):
    missing_images_dir = tmp_path / "missing-images"
    plan = _plan(
        input_kind="images_dir",
        recommended_recipe="configs/recipes/recipe-images-ocr-html-mvp.yaml",
        source_images_dir=str(missing_images_dir),
    )

    row, command, should_launch = prepare_confirmed_handoff(
        plan,
        plan_path=tmp_path / "overview_plan_final.jsonl",
        upstream_run_id="story176-blocked",
    )

    assert should_launch is False
    assert command == []
    assert row["terminal_outcome"] == "blocked"
    assert row["terminal_reason"] == f"source_input_not_found:{missing_images_dir}"


def test_prepare_confirmed_handoff_blocks_unsupported_input_kind(tmp_path):
    source_docx = tmp_path / "sample.docx"
    source_docx.write_text("stub", encoding="utf-8")
    plan = _plan(
        input_kind="docx",
        recommended_recipe="configs/recipes/recipe-images-ocr-html-mvp.yaml",
    )
    plan["meta"]["source_input"]["source_docx"] = str(source_docx)

    row, command, should_launch = prepare_confirmed_handoff(
        plan,
        plan_path=tmp_path / "overview_plan_final.jsonl",
        upstream_run_id="story176-docx",
    )

    assert should_launch is False
    assert command == []
    assert row["terminal_outcome"] == "blocked"
    assert row["terminal_reason"] == "unsupported_input_kind:docx"


@pytest.mark.parametrize(
    ("input_kind", "recipe", "filename"),
    [
        ("docx", "configs/recipes/recipe-docx-html-mvp.yaml", "sample.docx"),
        ("email-eml", "configs/recipes/recipe-email-eml-html-mvp.yaml", "sample.eml"),
        (
            "email-mbox",
            "configs/recipes/recipe-email-mbox-html-mvp.yaml",
            "sample.mbox",
        ),
        ("epub", "configs/recipes/recipe-epub-html-mvp.yaml", "sample.epub"),
        ("pptx", "configs/recipes/recipe-pptx-html-mvp.yaml", "sample.pptx"),
        ("web-page", "configs/recipes/recipe-web-page-html-mvp.yaml", "sample.html"),
        ("xlsx", "configs/recipes/recipe-xlsx-html-mvp.yaml", "sample.xlsx"),
    ],
)
def test_prepare_confirmed_handoff_blocks_direct_entry_only_recipes_with_explicit_reason(
    tmp_path,
    input_kind,
    recipe,
    filename,
):
    source_path = tmp_path / filename
    source_path.write_text("stub", encoding="utf-8")
    plan = _plan(
        input_kind=input_kind,
        recommended_recipe=recipe,
    )
    plan["meta"]["source_input"][f"source_{input_kind}"] = str(source_path)

    row, command, should_launch = prepare_confirmed_handoff(
        plan,
        plan_path=tmp_path / "overview_plan_final.jsonl",
        upstream_run_id=f"story194-{input_kind}",
    )

    assert should_launch is False
    assert command == []
    assert row["terminal_outcome"] == "blocked"
    assert (
        row["terminal_reason"]
        == f"direct_entry_recipe_outside_confirmed_handoff_scope:{input_kind}"
    )


@pytest.mark.parametrize(
    ("member_path", "expected_kind"),
    [
        ("nested/document.docx", "docx"),
        ("mail/message.eml", "email-eml"),
        ("site/page.html", "web-page"),
        ("site/page.htm", "web-page"),
        ("slides/deck.pptx", "pptx"),
        ("tables/workbook.xlsx", "xlsx"),
        ("books/mini.epub", "epub"),
        ("mail/archive.mbox", "email-mbox"),
        ("pdf/source.pdf", "pdf"),
        ("notes/readme.txt", None),
    ],
)
def test_infer_archive_member_input_kind_routes_by_suffix(member_path, expected_kind):
    assert infer_archive_member_input_kind(member_path) == expected_kind


def test_build_explicit_recipe_driver_command_for_web_page(tmp_path):
    source_path = tmp_path / "snapshot.html"
    source_path.write_text("<html><body><h1>Example</h1></body></html>", encoding="utf-8")
    output_root = tmp_path / "runs"

    command = build_explicit_recipe_driver_command(
        "configs/recipes/recipe-web-page-html-mvp.yaml",
        input_kind="web-page",
        source_path=source_path,
        downstream_run_id="mixed-archive-member-001",
        downstream_output_dir=output_root,
        allow_run_id_reuse=True,
    )

    assert command[:6] == [
        sys.executable,
        str((Path(__file__).resolve().parents[1] / "driver.py")),
        "--recipe",
        "configs/recipes/recipe-web-page-html-mvp.yaml",
        "--input-html",
        str(source_path),
    ]
    assert command[-3:] == ["--output-dir", str(output_root), "--allow-run-id-reuse"]
