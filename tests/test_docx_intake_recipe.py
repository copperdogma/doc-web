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
DOCX_CASES = (
    {
        "fixture": "testdata/docx-mini.docx",
        "title": "DOCX Mini Fixture",
        "reading_order": ["chapter-001", "chapter-002"],
        "expected_entry_count": 2,
        "expected_provenance_rows": 7,
        "required_html_snippets": [
            'id="blk-chapter-001-0003"',
            '<table id="blk-chapter-001-0005">',
        ],
    },
    {
        "fixture": "testdata/docx-structured.docx",
        "title": "DOCX Structured Fixture",
        "reading_order": ["chapter-001", "chapter-002", "chapter-003"],
        "expected_entry_count": 3,
        "expected_provenance_rows": 15,
        "required_html_snippets": [
            'id="blk-chapter-001-0002"',
            '<table id="blk-chapter-003-0006">',
        ],
    },
    {
        "fixture": "testdata/docx-page-break.docx",
        "title": "DOCX Page Break Fixture",
        "reading_order": ["chapter-001", "chapter-002"],
        "expected_entry_count": 2,
        "expected_provenance_rows": 6,
        "required_html_snippets": [
            'id="blk-chapter-001-0002"',
            'id="blk-chapter-002-0003"',
        ],
    },
)


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


@pytest.mark.parametrize("case", DOCX_CASES, ids=[case["title"] for case in DOCX_CASES])
def test_docx_recipe_smoke(tmp_path: Path, case: dict[str, object]):
    run_id = f"docx-intake-smoke-{uuid.uuid4().hex[:8]}"
    run_dir = tmp_path / run_id
    fixture = str(case["fixture"])

    result = subprocess.run(
        [
            sys.executable,
            "driver.py",
            "--recipe",
            DOCX_RECIPE,
            "--input-docx",
            fixture,
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
    all_html = "\n".join(
        (run_dir / "output" / "html" / entry.path).read_text(encoding="utf-8")
        for entry in manifest.entries
    )

    assert report["entry_count"] == case["expected_entry_count"]
    assert report["provenance_row_count"] == case["expected_provenance_rows"]
    assert manifest.title == case["title"]
    assert manifest.reading_order == case["reading_order"]
    assert manifest.entries[0].source_pages == []
    assert all(block.source_page_number is None for block in blocks)
    assert all(block.source_element_ids for block in blocks)
    for snippet in case["required_html_snippets"]:
        assert snippet in all_html
