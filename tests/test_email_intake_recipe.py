import json
import subprocess
import sys
import uuid
from pathlib import Path

import yaml

from schemas import DocWebBundleManifest, DocWebProvenanceBlock


EML_RECIPE = "configs/recipes/recipe-email-eml-html-mvp.yaml"
EML_FIXTURE = "testdata/email-eml-mini.eml"


def _load_jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_email_recipe_wiring():
    data = yaml.safe_load(Path(EML_RECIPE).read_text(encoding="utf-8"))

    assert data["input"]["eml"] == EML_FIXTURE
    stages = data["stages"]
    assert [stage["module"] for stage in stages] == [
        "unstructured_email_intake_v1",
        "email_elements_to_bundle_v1",
    ]


def test_email_recipe_smoke(tmp_path: Path):
    run_id = f"email-intake-smoke-{uuid.uuid4().hex[:8]}"
    run_dir = tmp_path / run_id

    result = subprocess.run(
        [
            sys.executable,
            "driver.py",
            "--recipe",
            EML_RECIPE,
            "--input-eml",
            EML_FIXTURE,
            "--run-id",
            run_id,
            "--output-dir",
            str(run_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    elements_path = run_dir / "01_unstructured_email_intake_v1" / "elements.jsonl"
    report_path = run_dir / "02_email_elements_to_bundle_v1" / "email_bundle_report.json"
    manifest_path = run_dir / "output" / "html" / "manifest.json"
    blocks_path = run_dir / "output" / "html" / "provenance" / "blocks.jsonl"
    page_path = run_dir / "output" / "html" / "page-001.html"

    assert elements_path.exists()
    assert report_path.exists()
    assert manifest_path.exists()
    assert blocks_path.exists()
    assert page_path.exists()

    elements = _load_jsonl(elements_path)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = DocWebBundleManifest(**json.loads(manifest_path.read_text(encoding="utf-8")))
    blocks = [DocWebProvenanceBlock(**row) for row in _load_jsonl(blocks_path)]

    assert elements[0]["metadata"]["subject"] == "Fixture Subject"
    assert elements[0]["metadata"]["sent_from"] == ["Alice Example <alice@example.com>"]
    assert elements[0]["metadata"]["sent_to"] == ["Bob Example <bob@example.com>"]
    assert "sent_cc" not in elements[0]["metadata"]
    assert "sent_bcc" not in elements[0]["metadata"]

    assert report["entry_count"] == 1
    assert report["provenance_row_count"] == 4
    assert report["message_metadata"] == {
        "subject": "Fixture Subject",
        "sent_from": ["Alice Example <alice@example.com>"],
        "sent_to": ["Bob Example <bob@example.com>"],
    }
    assert report["anchor_model"] == {
        "source_pages": "none",
        "provenance": "source_element_ids",
    }
    assert manifest.title == "Fixture Subject"
    assert manifest.creator == "Alice Example <alice@example.com>"
    assert manifest.reading_order == ["page-001"]
    assert [entry.title for entry in manifest.entries] == ["Fixture Subject"]
    assert [entry.source_pages for entry in manifest.entries] == [[]]
    assert all(block.source_page_number is None for block in blocks)
    assert all(block.source_element_ids for block in blocks)

    page_html = page_path.read_text(encoding="utf-8")
    assert "This fixture exists to prove the first honest .eml direct-entry seam." in page_html
    assert ">Regards,<" in page_html
    assert ">Alice<" in page_html
