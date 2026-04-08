import json
import subprocess
import sys
import uuid
from pathlib import Path

import yaml

from schemas import DocWebBundleManifest, DocWebProvenanceBlock


PPTX_RECIPE = "configs/recipes/recipe-pptx-html-mvp.yaml"
PPTX_FIXTURE = "testdata/pptx-mini.pptx"


def _load_jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_pptx_recipe_wiring():
    data = yaml.safe_load(Path(PPTX_RECIPE).read_text(encoding="utf-8"))

    assert data["input"]["pptx"] == PPTX_FIXTURE
    stages = data["stages"]
    assert [stage["module"] for stage in stages] == [
        "unstructured_pptx_intake_v1",
        "pptx_elements_to_bundle_v1",
    ]


def test_pptx_recipe_smoke(tmp_path: Path):
    run_id = f"pptx-intake-smoke-{uuid.uuid4().hex[:8]}"
    run_dir = tmp_path / run_id

    result = subprocess.run(
        [
            sys.executable,
            "driver.py",
            "--recipe",
            PPTX_RECIPE,
            "--input-pptx",
            PPTX_FIXTURE,
            "--run-id",
            run_id,
            "--output-dir",
            str(run_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    report_path = run_dir / "02_pptx_elements_to_bundle_v1" / "pptx_bundle_report.json"
    manifest_path = run_dir / "output" / "html" / "manifest.json"
    blocks_path = run_dir / "output" / "html" / "provenance" / "blocks.jsonl"
    cover_path = run_dir / "output" / "html" / "page-001.html"
    slide_one_path = run_dir / "output" / "html" / "page-002.html"
    slide_two_path = run_dir / "output" / "html" / "page-003.html"

    assert report_path.exists()
    assert manifest_path.exists()
    assert blocks_path.exists()
    assert cover_path.exists()
    assert slide_one_path.exists()
    assert slide_two_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = DocWebBundleManifest(**json.loads(manifest_path.read_text(encoding="utf-8")))
    blocks = [DocWebProvenanceBlock(**row) for row in _load_jsonl(blocks_path)]

    assert report["entry_count"] == 3
    assert report["provenance_row_count"] == 6
    assert manifest.title == "Office Probe Slides"
    assert manifest.reading_order == ["page-001", "page-002", "page-003"]
    assert [entry.title for entry in manifest.entries] == [
        "Office Probe Slides",
        "Slide One",
        "Slide Two",
    ]
    assert [entry.source_pages for entry in manifest.entries] == [[1], [2], [3]]
    assert [block.source_page_number for block in blocks] == [1, 2, 2, 2, 3, 3]
    assert all(block.source_element_ids for block in blocks)

    cover_html = cover_path.read_text(encoding="utf-8")
    slide_one_html = slide_one_path.read_text(encoding="utf-8")
    slide_two_html = slide_two_path.read_text(encoding="utf-8")

    assert "Office Probe Slides" in cover_html
    assert "<ul>" in slide_one_html
    assert ">Ada<" in slide_one_html
    assert ">Lin<" in slide_one_html
    assert "This probe exists to make the PPTX seam decision explicit in Story 175." in slide_two_html
