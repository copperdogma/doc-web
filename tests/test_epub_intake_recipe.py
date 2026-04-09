import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import pytest
import yaml

from schemas import DocWebBundleManifest, DocWebProvenanceBlock


EPUB_RECIPE = "configs/recipes/recipe-epub-html-mvp.yaml"
EPUB_FIXTURE = "testdata/epub-mini.epub"


def _load_jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _skip_if_pandoc_missing() -> None:
    if shutil.which("pandoc") is None:
        pytest.skip("Pandoc is required for maintained EPUB smokes.")


def _skip_if_runtime_pin_unsupported() -> None:
    if sys.version_info >= (3, 13):
        pytest.skip("Maintained EPUB smokes are validated on Python 3.11/3.12.")


def test_epub_recipe_wiring():
    data = yaml.safe_load(Path(EPUB_RECIPE).read_text(encoding="utf-8"))

    assert data["input"]["epub"] == EPUB_FIXTURE
    stages = data["stages"]
    assert [stage["module"] for stage in stages] == [
        "unstructured_epub_intake_v1",
        "epub_elements_to_bundle_v1",
    ]


def test_epub_recipe_smoke(tmp_path: Path):
    _skip_if_runtime_pin_unsupported()
    _skip_if_pandoc_missing()

    run_id = f"epub-intake-smoke-{uuid.uuid4().hex[:8]}"
    run_dir = tmp_path / run_id

    result = subprocess.run(
        [
            sys.executable,
            "driver.py",
            "--recipe",
            EPUB_RECIPE,
            "--input-epub",
            EPUB_FIXTURE,
            "--run-id",
            run_id,
            "--output-dir",
            str(run_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    elements_path = run_dir / "01_unstructured_epub_intake_v1" / "elements.jsonl"
    report_path = run_dir / "02_epub_elements_to_bundle_v1" / "epub_bundle_report.json"
    manifest_path = run_dir / "output" / "html" / "manifest.json"
    blocks_path = run_dir / "output" / "html" / "provenance" / "blocks.jsonl"
    chapter_one_path = run_dir / "output" / "html" / "chapter-001.html"
    chapter_two_path = run_dir / "output" / "html" / "chapter-002.html"

    assert elements_path.exists()
    assert report_path.exists()
    assert manifest_path.exists()
    assert blocks_path.exists()
    assert chapter_one_path.exists()
    assert chapter_two_path.exists()

    elements = _load_jsonl(elements_path)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = DocWebBundleManifest(**json.loads(manifest_path.read_text(encoding="utf-8")))
    blocks = [DocWebProvenanceBlock(**row) for row in _load_jsonl(blocks_path)]

    assert elements
    assert elements[0]["metadata"]["epub_title"] == "EPUB Mini Fixture"
    assert elements[0]["metadata"]["epub_creator"] == "doc-web"

    assert report["entry_count"] == 2
    assert report["provenance_row_count"] == 6
    assert manifest.title == "EPUB Mini Fixture"
    assert manifest.creator == "doc-web"
    assert manifest.reading_order == ["chapter-001", "chapter-002"]
    assert [entry.title for entry in manifest.entries] == ["Chapter One", "Chapter Two"]
    assert [entry.source_pages for entry in manifest.entries] == [[], []]
    assert blocks
    assert all(block.source_page_number is None for block in blocks)
    assert all(block.source_element_ids for block in blocks)

    chapter_one_html = chapter_one_path.read_text(encoding="utf-8")
    chapter_two_html = chapter_two_path.read_text(encoding="utf-8")

    assert "Ada keeps the research log." in chapter_one_html
    assert "Lin checks the archive notes." in chapter_one_html
    assert "chapter grouping resumes correctly" in chapter_two_html
