import json
import subprocess
import sys
import uuid
from pathlib import Path

import yaml


IMAGE_RECIPE = "configs/recipes/recipe-images-ocr-html-mvp.yaml"
HANDWRITTEN_RESCUE_IMAGE_RECIPE = "configs/recipes/recipe-images-ocr-html-handwritten-notes-gemini-rescue.yaml"
HANDWRITTEN_IMAGES_FIXTURE = "testdata/handwritten-notes-mini-images"
HANDWRITTEN_FADED_IMAGES_FIXTURE = "testdata/handwritten-notes-faded-images"
HANDWRITTEN_ROUGH_IMAGES_FIXTURE = "testdata/handwritten-notes-rough-images"
HANDWRITTEN_BARNEY_REAL_IMAGES_FIXTURE = "testdata/handwritten-notes-barney-real-images"


def test_handwritten_notes_image_recipe_extract_only_smoke(tmp_path):
    run_id = f"image-intake-smoke-{uuid.uuid4().hex[:8]}"
    run_dir = tmp_path / run_id

    result = subprocess.run(
        [
            sys.executable,
            "driver.py",
            "--recipe",
            IMAGE_RECIPE,
            "--input-images",
            HANDWRITTEN_IMAGES_FIXTURE,
            "--run-id",
            run_id,
            "--output-dir",
            str(run_dir),
            "--end-at",
            "images_to_manifest",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    manifest_path = run_dir / "01_images_dir_to_manifest_v1" / "pages_images_manifest.jsonl"
    assert manifest_path.exists()

    rows = [
        json.loads(line)
        for line in manifest_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(rows) == 2

    fixture_abs = str(Path(HANDWRITTEN_IMAGES_FIXTURE).resolve())
    assert all(row["source"] == [fixture_abs] for row in rows)
    assert all(Path(row["image"]).exists() for row in rows)


def test_handwritten_rough_notes_image_recipe_extract_only_smoke(tmp_path):
    run_id = f"image-intake-smoke-{uuid.uuid4().hex[:8]}"
    run_dir = tmp_path / run_id

    result = subprocess.run(
        [
            sys.executable,
            "driver.py",
            "--recipe",
            IMAGE_RECIPE,
            "--input-images",
            HANDWRITTEN_ROUGH_IMAGES_FIXTURE,
            "--run-id",
            run_id,
            "--output-dir",
            str(run_dir),
            "--end-at",
            "images_to_manifest",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    manifest_path = run_dir / "01_images_dir_to_manifest_v1" / "pages_images_manifest.jsonl"
    assert manifest_path.exists()

    rows = [
        json.loads(line)
        for line in manifest_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(rows) == 3

    fixture_abs = str(Path(HANDWRITTEN_ROUGH_IMAGES_FIXTURE).resolve())
    assert all(row["source"] == [fixture_abs] for row in rows)
    assert all(Path(row["image"]).exists() for row in rows)


def test_handwritten_faded_notes_image_recipe_extract_only_smoke(tmp_path):
    run_id = f"image-intake-smoke-{uuid.uuid4().hex[:8]}"
    run_dir = tmp_path / run_id

    result = subprocess.run(
        [
            sys.executable,
            "driver.py",
            "--recipe",
            IMAGE_RECIPE,
            "--input-images",
            HANDWRITTEN_FADED_IMAGES_FIXTURE,
            "--run-id",
            run_id,
            "--output-dir",
            str(run_dir),
            "--end-at",
            "images_to_manifest",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    manifest_path = run_dir / "01_images_dir_to_manifest_v1" / "pages_images_manifest.jsonl"
    assert manifest_path.exists()

    rows = [
        json.loads(line)
        for line in manifest_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(rows) == 2

    fixture_abs = str(Path(HANDWRITTEN_FADED_IMAGES_FIXTURE).resolve())
    assert all(row["source"] == [fixture_abs] for row in rows)
    assert all(Path(row["image"]).exists() for row in rows)


def test_handwritten_barney_real_image_recipe_extract_only_smoke(tmp_path):
    run_id = f"image-intake-smoke-{uuid.uuid4().hex[:8]}"
    run_dir = tmp_path / run_id

    result = subprocess.run(
        [
            sys.executable,
            "driver.py",
            "--recipe",
            IMAGE_RECIPE,
            "--input-images",
            HANDWRITTEN_BARNEY_REAL_IMAGES_FIXTURE,
            "--run-id",
            run_id,
            "--output-dir",
            str(run_dir),
            "--end-at",
            "images_to_manifest",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    manifest_path = run_dir / "01_images_dir_to_manifest_v1" / "pages_images_manifest.jsonl"
    assert manifest_path.exists()

    rows = [
        json.loads(line)
        for line in manifest_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(rows) == 1

    fixture_abs = str(Path(HANDWRITTEN_BARNEY_REAL_IMAGES_FIXTURE).resolve())
    assert all(row["source"] == [fixture_abs] for row in rows)
    assert all(Path(row["image"]).exists() for row in rows)


def test_handwritten_rescue_image_recipe_extract_only_smoke(tmp_path):
    run_id = f"image-intake-smoke-{uuid.uuid4().hex[:8]}"
    run_dir = tmp_path / run_id

    result = subprocess.run(
        [
            sys.executable,
            "driver.py",
            "--recipe",
            HANDWRITTEN_RESCUE_IMAGE_RECIPE,
            "--input-images",
            HANDWRITTEN_BARNEY_REAL_IMAGES_FIXTURE,
            "--run-id",
            run_id,
            "--output-dir",
            str(run_dir),
            "--end-at",
            "images_to_manifest",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    manifest_path = run_dir / "01_images_dir_to_manifest_v1" / "pages_images_manifest.jsonl"
    assert manifest_path.exists()

    rows = [
        json.loads(line)
        for line in manifest_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(rows) == 1

    fixture_abs = str(Path(HANDWRITTEN_BARNEY_REAL_IMAGES_FIXTURE).resolve())
    assert all(row["source"] == [fixture_abs] for row in rows)
    assert all(Path(row["image"]).exists() for row in rows)


def test_handwritten_rescue_image_recipe_wiring():
    data = yaml.safe_load(Path(HANDWRITTEN_RESCUE_IMAGE_RECIPE).read_text(encoding="utf-8"))

    assert data["input"]["images"] == HANDWRITTEN_BARNEY_REAL_IMAGES_FIXTURE
    stages = data["stages"]
    assert [stage["module"] for stage in stages] == [
        "images_dir_to_manifest_v1",
        "ocr_ai_gpt51_v1",
        "crop_illustrations_guided_v1",
        "table_rescue_html_loop_v1",
        "extract_page_numbers_html_v1",
        "portionize_toc_html_v1",
        "build_chapter_html_v1",
    ]
    ocr_stage = stages[1]
    assert ocr_stage["params"]["model"] == "gemini-2.5-pro"
    assert ocr_stage["params"]["concurrency"] == 2
    assert "handwritten historical correspondence" in ocr_stage["params"]["ocr_hints"]
