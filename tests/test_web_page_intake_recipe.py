import json
import subprocess
import sys
import uuid
from pathlib import Path

import yaml

from schemas import DocWebBundleManifest, DocWebProvenanceBlock


WEB_PAGE_RECIPE = "configs/recipes/recipe-web-page-html-mvp.yaml"
WEB_PAGE_FIXTURE = "testdata/web-page-mini.html"


def _load_jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_web_page_recipe_wiring():
    data = yaml.safe_load(Path(WEB_PAGE_RECIPE).read_text(encoding="utf-8"))

    assert data["input"]["html"] == WEB_PAGE_FIXTURE
    stages = data["stages"]
    assert [stage["module"] for stage in stages] == [
        "web_page_html_intake_v1",
        "extract_page_numbers_html_v1",
        "portionize_headings_html_v1",
        "build_chapter_html_v1",
    ]
    portionize_stage = stages[2]
    assert portionize_stage["params"]["allow_unnumbered"] is True
    assert portionize_stage["params"]["fallback_mode"] == "single-document"


def test_web_page_recipe_smoke(tmp_path: Path):
    run_id = f"web-page-intake-smoke-{uuid.uuid4().hex[:8]}"
    run_dir = tmp_path / run_id

    result = subprocess.run(
        [
            sys.executable,
            "driver.py",
            "--recipe",
            WEB_PAGE_RECIPE,
            "--input-html",
            WEB_PAGE_FIXTURE,
            "--run-id",
            run_id,
            "--output-dir",
            str(run_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    pages_path = run_dir / "01_web_page_html_intake_v1" / "pages_html.jsonl"
    manifest_path = run_dir / "output" / "html" / "manifest.json"
    blocks_path = run_dir / "output" / "html" / "provenance" / "blocks.jsonl"
    chapter_path = run_dir / "output" / "html" / "chapter-001.html"

    assert pages_path.exists()
    assert manifest_path.exists()
    assert blocks_path.exists()
    assert chapter_path.exists()

    page_rows = _load_jsonl(pages_path)
    assert len(page_rows) == 1
    page = page_rows[0]
    assert page["schema_version"] == "page_html_v1"
    assert page["source"] == [
        str(Path(WEB_PAGE_FIXTURE).resolve()),
        "https://example.com/",
    ]
    assert page["html"].startswith("<div><h1>Example Domain</h1>")
    assert page["raw_html"].startswith("<!doctype html>")
    assert page["printed_page_number"] is None

    manifest = DocWebBundleManifest(**json.loads(manifest_path.read_text(encoding="utf-8")))
    blocks = [DocWebProvenanceBlock(**row) for row in _load_jsonl(blocks_path)]
    chapter_html = chapter_path.read_text(encoding="utf-8")

    assert manifest.reading_order == ["chapter-001"]
    assert [entry.title for entry in manifest.entries] == ["Example Domain"]
    assert [entry.source_pages for entry in manifest.entries] == [[1]]
    assert blocks
    assert "Example Domain" in chapter_html
    assert "Learn more" in chapter_html
