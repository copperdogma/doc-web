import json
import subprocess
import sys
import uuid
from pathlib import Path

from pypdf import PdfReader

PDF_RECIPE = "configs/recipes/recipe-pdf-ocr-html-mvp.yaml"
BORN_DIGITAL_FIXTURE = "testdata/tbotb-mini.pdf"
SCANNED_PROSE_FIXTURE = "testdata/scanned-prose-mini.pdf"


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
