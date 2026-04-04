import json
import subprocess
import sys
import uuid
from pathlib import Path

from pypdf import PdfReader
import yaml

PDF_RECIPE = "configs/recipes/recipe-pdf-ocr-html-mvp.yaml"
BORN_DIGITAL_NON_TOC_RECIPE = "configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml"
BORN_DIGITAL_FIXTURE = "testdata/tbotb-mini.pdf"
FLAT_FORM_FIXTURE = "testdata/flat-born-digital-form-mini.pdf"
SCANNED_PROSE_FIXTURE = "testdata/scanned-prose-mini.pdf"
HANDWRITTEN_NOTES_FIXTURE = "testdata/handwritten-notes-mini.pdf"
HANDWRITTEN_FADED_FIXTURE = "testdata/handwritten-notes-faded.pdf"
HANDWRITTEN_ROUGH_FIXTURE = "testdata/handwritten-notes-rough.pdf"
HANDWRITTEN_BARNEY_REAL_FIXTURE = "testdata/handwritten-notes-barney-real.pdf"


def _run_pdf_recipe_extract_only_smoke(tmp_path, pdf_fixture: str):
    run_id = f"pdf-intake-smoke-{uuid.uuid4().hex[:8]}"
    run_dir = tmp_path / run_id

    result = subprocess.run(
        [
            sys.executable,
            "driver.py",
            "--recipe",
            PDF_RECIPE,
            "--input-pdf",
            pdf_fixture,
            "--run-id",
            run_id,
            "--output-dir",
            str(run_dir),
            "--end-at",
            "pdf_to_images",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    manifest_path = run_dir / "01_extract_pdf_images_fast_v1" / "pages_images_manifest.jsonl"
    assert manifest_path.exists()

    rows = [
        json.loads(line)
        for line in manifest_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert rows

    fixture_abs = str(Path(pdf_fixture).resolve())
    assert all(row["source"] == [fixture_abs] for row in rows)
    assert all(Path(row["image"]).exists() for row in rows)


def test_born_digital_pdf_recipe_extract_only_smoke(tmp_path):
    _run_pdf_recipe_extract_only_smoke(tmp_path, BORN_DIGITAL_FIXTURE)


def test_scanned_prose_pdf_recipe_extract_only_smoke(tmp_path):
    reader = PdfReader(SCANNED_PROSE_FIXTURE)
    assert all(len((page.extract_text() or "").strip()) == 0 for page in reader.pages)

    _run_pdf_recipe_extract_only_smoke(tmp_path, SCANNED_PROSE_FIXTURE)


def test_handwritten_notes_pdf_recipe_extract_only_smoke(tmp_path):
    reader = PdfReader(HANDWRITTEN_NOTES_FIXTURE)
    assert len(reader.pages) == 2
    assert all(len((page.extract_text() or "").strip()) == 0 for page in reader.pages)

    _run_pdf_recipe_extract_only_smoke(tmp_path, HANDWRITTEN_NOTES_FIXTURE)


def test_handwritten_faded_pdf_recipe_extract_only_smoke(tmp_path):
    reader = PdfReader(HANDWRITTEN_FADED_FIXTURE)
    assert len(reader.pages) == 2
    assert all(len((page.extract_text() or "").strip()) == 0 for page in reader.pages)

    _run_pdf_recipe_extract_only_smoke(tmp_path, HANDWRITTEN_FADED_FIXTURE)


def test_handwritten_rough_pdf_recipe_extract_only_smoke(tmp_path):
    reader = PdfReader(HANDWRITTEN_ROUGH_FIXTURE)
    assert len(reader.pages) == 3
    assert all(len((page.extract_text() or "").strip()) == 0 for page in reader.pages)

    _run_pdf_recipe_extract_only_smoke(tmp_path, HANDWRITTEN_ROUGH_FIXTURE)


def test_handwritten_barney_real_pdf_recipe_extract_only_smoke(tmp_path):
    reader = PdfReader(HANDWRITTEN_BARNEY_REAL_FIXTURE)
    assert len(reader.pages) == 1
    assert all(len((page.extract_text() or "").strip()) == 0 for page in reader.pages)

    _run_pdf_recipe_extract_only_smoke(tmp_path, HANDWRITTEN_BARNEY_REAL_FIXTURE)


def test_repo_owned_flat_form_fixture_has_extractable_text():
    reader = PdfReader(FLAT_FORM_FIXTURE)
    assert len(reader.pages) == 1
    assert any(len((page.extract_text() or "").strip()) > 0 for page in reader.pages)


def test_born_digital_non_toc_recipe_wiring():
    data = yaml.safe_load(Path(BORN_DIGITAL_NON_TOC_RECIPE).read_text(encoding="utf-8"))

    assert data["input"]["pdf"] == "testdata/flat-born-digital-mini.pdf"
    stages = data["stages"]
    assert [stage["module"] for stage in stages] == [
        "extract_pdf_marker_lite_html_v1",
        "extract_page_numbers_html_v1",
        "portionize_headings_html_v1",
        "build_chapter_html_v1",
    ]
    portionize_stage = stages[2]
    assert portionize_stage["params"]["allow_unnumbered"] is True
    assert portionize_stage["params"]["fallback_mode"] == "single-document"
