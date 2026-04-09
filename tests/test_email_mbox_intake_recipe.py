import json
import subprocess
import sys
import uuid
from pathlib import Path

import pytest
import yaml

from schemas import DocWebBundleManifest, DocWebProvenanceBlock


MBOX_RECIPE = "configs/recipes/recipe-email-mbox-html-mvp.yaml"
MBOX_FIXTURE = "testdata/email-mbox-mini.mbox"


def _load_jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _skip_if_unstructured_email_missing() -> None:
    try:
        from unstructured.partition.email import partition_email  # noqa: F401
    except ImportError:
        pytest.skip(
            "Unstructured email support is not installed in this test environment."
        )


def test_email_mbox_recipe_wiring():
    data = yaml.safe_load(Path(MBOX_RECIPE).read_text(encoding="utf-8"))

    assert data["input"]["mbox"] == MBOX_FIXTURE
    stages = data["stages"]
    assert [stage["module"] for stage in stages] == [
        "mailbox_mbox_intake_v1",
        "mbox_elements_to_bundle_v1",
    ]


def test_email_mbox_recipe_smoke(tmp_path: Path):
    _skip_if_unstructured_email_missing()

    run_id = f"email-mbox-intake-smoke-{uuid.uuid4().hex[:8]}"
    run_dir = tmp_path / run_id

    result = subprocess.run(
        [
            sys.executable,
            "driver.py",
            "--recipe",
            MBOX_RECIPE,
            "--input-mbox",
            MBOX_FIXTURE,
            "--run-id",
            run_id,
            "--output-dir",
            str(run_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    elements_path = run_dir / "01_mailbox_mbox_intake_v1" / "elements.jsonl"
    report_path = (
        run_dir / "02_mbox_elements_to_bundle_v1" / "email_archive_bundle_report.json"
    )
    manifest_path = run_dir / "output" / "html" / "manifest.json"
    blocks_path = run_dir / "output" / "html" / "provenance" / "blocks.jsonl"
    first_page_path = run_dir / "output" / "html" / "page-001.html"
    second_page_path = run_dir / "output" / "html" / "page-002.html"

    assert elements_path.exists()
    assert report_path.exists()
    assert manifest_path.exists()
    assert blocks_path.exists()
    assert first_page_path.exists()
    assert second_page_path.exists()

    elements = _load_jsonl(elements_path)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = DocWebBundleManifest(
        **json.loads(manifest_path.read_text(encoding="utf-8"))
    )
    blocks = [DocWebProvenanceBlock(**row) for row in _load_jsonl(blocks_path)]

    assert elements[0]["metadata"]["archive_source_format"] == "mbox"
    assert elements[0]["metadata"]["archive_message_index"] == 1
    assert elements[4]["metadata"]["archive_message_index"] == 2
    assert elements[0]["id"] == "mbox-message-001-element-0001"
    assert elements[4]["id"] == "mbox-message-002-element-0005"
    assert len({element["id"] for element in elements}) == len(elements)
    assert elements[2]["id"] != elements[6]["id"]
    assert elements[0]["metadata"]["archive_native_element_id"]
    assert elements[4]["metadata"]["archive_native_element_id"]
    assert elements[0]["metadata"]["subject"] == "Fixture Subject"
    assert elements[4]["metadata"]["subject"] == "Fixture Follow-up"
    assert elements[0]["metadata"]["sent_from"] == ["Alice Example <alice@example.com>"]
    assert elements[4]["metadata"]["sent_from"] == ["Carol Example <carol@example.com>"]
    assert elements[0]["metadata"]["sent_to"] == ["Bob Example <bob@example.com>"]
    assert elements[4]["metadata"]["sent_to"] == ["Dana Example <dana@example.com>"]

    assert report["entry_count"] == 2
    assert report["provenance_row_count"] == 8
    assert report["reading_order"] == ["page-001", "page-002"]
    assert report["archive_metadata"] == {"format": "mbox", "message_count": 2}
    assert report["messages"] == [
        {
            "entry_id": "page-001",
            "message_index": 1,
            "subject": "Fixture Subject",
            "sent_from": ["Alice Example <alice@example.com>"],
            "sent_to": ["Bob Example <bob@example.com>"],
            "message_id": "<email-mbox-mini-001@example.com>",
            "date": "Mon, 01 Jan 2024 08:00:00 -0700",
        },
        {
            "entry_id": "page-002",
            "message_index": 2,
            "subject": "Fixture Follow-up",
            "sent_from": ["Carol Example <carol@example.com>"],
            "sent_to": ["Dana Example <dana@example.com>"],
            "message_id": "<email-mbox-mini-002@example.com>",
            "date": "Tue, 02 Jan 2024 09:15:00 -0700",
        },
    ]
    assert report["anchor_model"] == {
        "source_pages": "none",
        "provenance": "source_element_ids",
    }
    assert manifest.title == "Email MBOX Mini"
    assert manifest.creator is None
    assert manifest.reading_order == ["page-001", "page-002"]
    assert [entry.title for entry in manifest.entries] == [
        "Fixture Subject",
        "Fixture Follow-up",
    ]
    assert [entry.source_pages for entry in manifest.entries] == [[], []]
    assert all(block.source_page_number is None for block in blocks)
    assert all(block.source_element_ids for block in blocks)
    source_rows = {element["id"]: element for element in elements}
    assert len(source_rows) == len(elements)
    for block in blocks:
        assert len(block.source_element_ids) == 1
        assert block.source_element_ids[0] in source_rows

    first_page_html = first_page_path.read_text(encoding="utf-8")
    second_page_html = second_page_path.read_text(encoding="utf-8")
    assert (
        "This fixture exists to prove the first honest .mbox direct-entry seam."
        in first_page_html
    )
    assert (
        "This companion message exists to prove archive ordering without widening the claim"
        in second_page_html
    )
