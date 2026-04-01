import json
import subprocess
import sys
import uuid
from pathlib import Path

import pytest
import yaml

from schemas import DocWebBundleManifest, DocWebProvenanceBlock


DOCX_RECIPE = "configs/recipes/recipe-docx-html-mvp.yaml"
DOCX_FIXTURE = "testdata/docx-mini.docx"
DOCX_FIXTURES = [
    {
        "fixture": "testdata/docx-mini.docx",
        "title": "DOCX Mini Fixture",
        "reading_order": ["chapter-001", "chapter-002"],
        "entry_titles": ["Family Snapshot", "Notes"],
        "provenance_rows": 7,
    },
    {
        "fixture": "testdata/docx-sections-mini.docx",
        "title": "DOCX Sections Fixture",
        "reading_order": ["chapter-001", "chapter-002"],
        "entry_titles": ["Overview", "Roster"],
        "provenance_rows": 6,
    },
    {
        "fixture": "testdata/docx-nested-mini.docx",
        "title": "DOCX Nested Fixture",
        "reading_order": ["chapter-001", "chapter-002"],
        "entry_titles": ["Overview", "Appendix"],
        "provenance_rows": 8,
    },
]


def _load_jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_docx_recipe_wiring():
    data = yaml.safe_load(Path(DOCX_RECIPE).read_text(encoding="utf-8"))

    assert data["input"]["docx"] == DOCX_FIXTURE
    stages = data["stages"]
    assert [stage["module"] for stage in stages] == [
        "unstructured_docx_intake_v1",
        "docx_elements_to_bundle_v1",
    ]


@pytest.mark.parametrize("case", DOCX_FIXTURES, ids=lambda case: Path(case["fixture"]).stem)
def test_docx_recipe_smoke(tmp_path: Path, case: dict):
    run_id = f"docx-intake-smoke-{uuid.uuid4().hex[:8]}"
    run_dir = tmp_path / run_id

    result = subprocess.run(
        [
            sys.executable,
            "driver.py",
            "--recipe",
            DOCX_RECIPE,
            "--input-docx",
            case["fixture"],
            "--run-id",
            run_id,
            "--output-dir",
            str(run_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    report_path = run_dir / "02_docx_elements_to_bundle_v1" / "docx_bundle_report.json"
    manifest_path = run_dir / "output" / "html" / "manifest.json"
    blocks_path = run_dir / "output" / "html" / "provenance" / "blocks.jsonl"
    chapter_path = run_dir / "output" / "html" / "chapter-001.html"

    assert report_path.exists()
    assert manifest_path.exists()
    assert blocks_path.exists()
    assert chapter_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = DocWebBundleManifest(**json.loads(manifest_path.read_text(encoding="utf-8")))
    blocks = [DocWebProvenanceBlock(**row) for row in _load_jsonl(blocks_path)]
    chapter_html = chapter_path.read_text(encoding="utf-8")

    assert report["entry_count"] == len(case["reading_order"])
    assert report["provenance_row_count"] == case["provenance_rows"]
    assert manifest.title == case["title"]
    assert manifest.reading_order == case["reading_order"]
    assert [entry.title for entry in manifest.entries] == case["entry_titles"]
    assert manifest.entries[0].source_pages == []
    assert all(block.source_page_number is None for block in blocks)
    assert all(block.source_element_ids for block in blocks)
    assert 'id="blk-chapter-001-0001"' in chapter_html

    if case["fixture"].endswith("docx-mini.docx"):
        assert '<table id="blk-chapter-001-0005">' in chapter_html
    if case["fixture"].endswith("docx-sections-mini.docx"):
        assert "The wider proof should keep both paragraphs inside the same section" in chapter_html
    if case["fixture"].endswith("docx-nested-mini.docx"):
        assert "Subsection A" in chapter_html
        assert "Top-level context paragraph." in chapter_html
