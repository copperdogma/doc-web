import json
import subprocess
import sys
import uuid
from pathlib import Path


IMAGE_RECIPE = "configs/recipes/recipe-images-ocr-html-mvp.yaml"
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
