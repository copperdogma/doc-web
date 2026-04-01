import json
import subprocess
import sys
import uuid
from pathlib import Path

import yaml

from schemas import DocWebBundleManifest, DocWebProvenanceBlock


XLSX_RECIPE = "configs/recipes/recipe-xlsx-html-mvp.yaml"
XLSX_FIXTURE = "testdata/xlsx-mini.xlsx"


def _load_jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_xlsx_recipe_wiring():
    data = yaml.safe_load(Path(XLSX_RECIPE).read_text(encoding="utf-8"))

    assert data["input"]["xlsx"] == XLSX_FIXTURE
    stages = data["stages"]
    assert [stage["module"] for stage in stages] == [
        "unstructured_xlsx_intake_v1",
        "xlsx_elements_to_bundle_v1",
    ]


def test_xlsx_recipe_smoke(tmp_path: Path):
    run_id = f"xlsx-intake-smoke-{uuid.uuid4().hex[:8]}"
    run_dir = tmp_path / run_id

    result = subprocess.run(
        [
            sys.executable,
            "driver.py",
            "--recipe",
            XLSX_RECIPE,
            "--input-xlsx",
            XLSX_FIXTURE,
            "--run-id",
            run_id,
            "--output-dir",
            str(run_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    report_path = run_dir / "02_xlsx_elements_to_bundle_v1" / "xlsx_bundle_report.json"
    manifest_path = run_dir / "output" / "html" / "manifest.json"
    blocks_path = run_dir / "output" / "html" / "provenance" / "blocks.jsonl"
    page_path = run_dir / "output" / "html" / "page-001.html"

    assert report_path.exists()
    assert manifest_path.exists()
    assert blocks_path.exists()
    assert page_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = DocWebBundleManifest(**json.loads(manifest_path.read_text(encoding="utf-8")))
    blocks = [DocWebProvenanceBlock(**row) for row in _load_jsonl(blocks_path)]
    page_html = page_path.read_text(encoding="utf-8")

    assert report["entry_count"] == 2
    assert report["provenance_row_count"] == 2
    assert manifest.reading_order == ["page-001", "page-002"]
    assert [entry.title for entry in manifest.entries] == ["Roster", "Visits"]
    assert all(block.source_page_number is None for block in blocks)
    assert all(block.source_element_ids for block in blocks)
    assert '<table id="blk-page-001-0001">' in page_html
    assert "Foothills County" in page_html
