import json
import subprocess
import sys
import uuid
from pathlib import Path

import pytest
import yaml

from schemas import DocWebBundleManifest, DocWebProvenanceBlock


XLSX_RECIPE = "configs/recipes/recipe-xlsx-html-mvp.yaml"
XLSX_FIXTURE = "testdata/xlsx-mini.xlsx"
SUPPORTED_XLSX_FIXTURES = [
    {
        "fixture": "testdata/xlsx-mini.xlsx",
        "titles": ["Roster", "Visits"],
        "entry_count": 2,
        "provenance_row_count": 2,
        "page_checks": {
            "page-001.html": ['<table id="blk-page-001-0001">', "Foothills County"],
            "page-002.html": ['<table id="blk-page-002-0001">', ">2025<"],
        },
    },
    {
        "fixture": "testdata/xlsx-multi-sheet.xlsx",
        "titles": ["Summary", "Regions"],
        "entry_count": 2,
        "provenance_row_count": 2,
        "page_checks": {
            "page-001.html": ['<table id="blk-page-001-0001">', "Volunteers"],
            "page-002.html": ['<table id="blk-page-002-0001">', "Foothills"],
        },
    },
    {
        "fixture": "testdata/xlsx-two-tables.xlsx",
        "titles": ["Roster"],
        "entry_count": 1,
        "provenance_row_count": 2,
        "page_checks": {
            "page-001.html": [
                '<table id="blk-page-001-0001">',
                '<table id="blk-page-001-0002">',
                "Researcher",
                ">2025<",
            ],
        },
    },
]


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


@pytest.mark.parametrize(
    "fixture_spec",
    SUPPORTED_XLSX_FIXTURES,
    ids=[Path(spec["fixture"]).stem for spec in SUPPORTED_XLSX_FIXTURES],
)
def test_xlsx_recipe_smoke(tmp_path: Path, fixture_spec: dict):
    run_id = f"xlsx-intake-smoke-{uuid.uuid4().hex[:8]}"
    run_dir = tmp_path / run_id

    result = subprocess.run(
        [
            sys.executable,
            "driver.py",
            "--recipe",
            XLSX_RECIPE,
            "--input-xlsx",
            fixture_spec["fixture"],
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

    assert report_path.exists()
    assert manifest_path.exists()
    assert blocks_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = DocWebBundleManifest(**json.loads(manifest_path.read_text(encoding="utf-8")))
    blocks = [DocWebProvenanceBlock(**row) for row in _load_jsonl(blocks_path)]

    assert report["entry_count"] == fixture_spec["entry_count"]
    assert report["provenance_row_count"] == fixture_spec["provenance_row_count"]
    assert manifest.reading_order == [entry.entry_id for entry in manifest.entries]
    assert [entry.title for entry in manifest.entries] == fixture_spec["titles"]
    assert all(block.source_page_number is None for block in blocks)
    assert all(block.source_element_ids for block in blocks)

    for page_name, checks in fixture_spec["page_checks"].items():
        page_path = run_dir / "output" / "html" / page_name
        assert page_path.exists()
        page_html = page_path.read_text(encoding="utf-8")
        for needle in checks:
            assert needle in page_html
