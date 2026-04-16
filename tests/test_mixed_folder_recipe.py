import json
import subprocess
import sys
import uuid
from pathlib import Path

import pytest
import yaml

from schemas import ArchiveMemberManifest, ArchiveMemberRoute, DocWebBundleManifest


FOLDER_RECIPE = "configs/recipes/recipe-mixed-folder-routing-mvp.yaml"
FOLDER_FIXTURE = "testdata/mixed-folder-mini"
FOLDER_PDF_FIXTURE = "testdata/mixed-folder-pdf-mini"
FOLDER_PDF_FIXTURE_META = "testdata/mixed-folder-pdf-mini.source.json"


def _load_jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _skip_if_mixed_folder_support_missing() -> None:
    try:
        from unstructured.partition.docx import partition_docx  # noqa: F401
        from unstructured.partition.email import partition_email  # noqa: F401
    except ImportError:
        pytest.skip(
            "Mixed-folder smoke needs the optional DOCX and email unstructured extras."
        )


def test_mixed_folder_recipe_wiring():
    data = yaml.safe_load(Path(FOLDER_RECIPE).read_text(encoding="utf-8"))

    assert data["input"]["folder"] == FOLDER_FIXTURE
    assert [stage["module"] for stage in data["stages"]] == [
        "folder_members_manifest_v1",
        "archive_route_members_v1",
    ]


def test_mixed_folder_pdf_fixture_shape():
    metadata = json.loads(Path(FOLDER_PDF_FIXTURE_META).read_text(encoding="utf-8"))

    assert metadata["archive_format"] == "folder"
    assert [member["member_path"] for member in metadata["members"]] == [
        "docs/proposal.pdf",
        "mail/message.eml",
        "web/snapshot.html",
        "notes/readme.txt",
    ]
    assert metadata["members"][0]["expected_route"] == "recommendation-only"
    assert (Path(FOLDER_PDF_FIXTURE) / "docs" / "proposal.pdf").exists()
    assert (Path(FOLDER_PDF_FIXTURE) / "mail" / "message.eml").exists()
    assert (Path(FOLDER_PDF_FIXTURE) / "web" / "snapshot.html").exists()
    assert (Path(FOLDER_PDF_FIXTURE) / "notes" / "readme.txt").exists()


def test_mixed_folder_recipe_smoke(tmp_path: Path):
    _skip_if_mixed_folder_support_missing()

    run_id = f"mixed-folder-smoke-{uuid.uuid4().hex[:8]}"
    output_root = tmp_path / "runs"
    run_dir = output_root / run_id

    result = subprocess.run(
        [
            sys.executable,
            "driver.py",
            "--recipe",
            FOLDER_RECIPE,
            "--input-folder",
            FOLDER_FIXTURE,
            "--run-id",
            run_id,
            "--output-dir",
            str(output_root),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    manifest_path = (
        run_dir / "01_folder_members_manifest_v1" / "archive_members_manifest.jsonl"
    )
    routes_path = run_dir / "02_archive_route_members_v1" / "archive_member_routes.jsonl"

    assert manifest_path.exists()
    assert routes_path.exists()

    manifest_rows = [
        ArchiveMemberManifest(**row) for row in _load_jsonl(manifest_path)
    ]
    route_rows = [ArchiveMemberRoute(**row) for row in _load_jsonl(routes_path)]

    fixture_abs = str(Path(FOLDER_FIXTURE).resolve())
    assert all(row.archive_format == "folder" for row in manifest_rows)
    assert all(row.archive_path == fixture_abs for row in manifest_rows)
    assert [row.member_path for row in manifest_rows] == [
        "docs/reference.docx",
        "mail/message.eml",
        "notes/readme.txt",
        "web/snapshot.html",
    ]
    assert [row.detected_input_kind for row in manifest_rows] == [
        "docx",
        "email-eml",
        None,
        "web-page",
    ]
    assert all(Path(row.extracted_path).exists() for row in manifest_rows)
    assert all(
        str(Path(row.extracted_path).resolve()).startswith(fixture_abs)
        for row in manifest_rows
    )
    assert all(
        not str(Path(row.extracted_path).resolve()).startswith(str(run_dir.resolve()))
        for row in manifest_rows
    )

    by_member = {row.member_path: row for row in route_rows}
    assert all(row.archive_format == "folder" for row in route_rows)
    assert by_member["notes/readme.txt"].terminal_outcome == "blocked"
    assert (
        by_member["notes/readme.txt"].terminal_reason
        == "unsupported_archive_member_suffix:.txt"
    )
    assert by_member["notes/readme.txt"].downstream_run_id is None

    launched_members = [
        "docs/reference.docx",
        "mail/message.eml",
        "web/snapshot.html",
    ]
    for member_path in launched_members:
        row = by_member[member_path]
        assert row.terminal_outcome == "launched"
        assert row.recommended_recipe
        assert row.launch_input_flag
        assert row.downstream_run_id
        assert row.downstream_output_dir
        assert row.first_downstream_artifact
        assert Path(row.downstream_output_dir).exists()
        assert Path(row.first_downstream_artifact).exists()
        bundle_manifest_path = (
            Path(row.downstream_output_dir) / "output" / "html" / "manifest.json"
        )
        assert bundle_manifest_path.exists()
        manifest = DocWebBundleManifest(
            **json.loads(bundle_manifest_path.read_text(encoding="utf-8"))
        )
        if member_path == "docs/reference.docx":
            assert manifest.title == "DOCX Mini Fixture"
        if member_path == "mail/message.eml":
            assert manifest.title == "Fixture Subject"
        if member_path == "web/snapshot.html":
            assert manifest.entries[0].title == "Example Domain"
