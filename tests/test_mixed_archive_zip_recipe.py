import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import pytest
import yaml

import modules.intake.archive_route_members_v1.main as archive_route_module
from modules.intake.archive_route_members_v1.main import _resolve_output_path
from schemas import ArchiveMemberManifest, ArchiveMemberRoute, DocWebBundleManifest, IntakePlan


ZIP_RECIPE = "configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml"
ZIP_FIXTURE = "testdata/mixed-archive-mini.zip"
PDF_ZIP_FIXTURE = "testdata/mixed-archive-pdf-mini.zip"
FOLDER_PDF_FIXTURE = "testdata/mixed-folder-pdf-mini"


def _load_jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(json.dumps(row) + "\n" for row in rows)
    path.write_text(payload, encoding="utf-8")


def _skip_if_mixed_archive_support_missing() -> None:
    try:
        from unstructured.partition.docx import partition_docx  # noqa: F401
        from unstructured.partition.email import partition_email  # noqa: F401
    except ImportError:
        pytest.skip(
            "Mixed-archive smoke needs the optional DOCX and email unstructured extras."
        )


def test_mixed_archive_zip_recipe_wiring():
    data = yaml.safe_load(Path(ZIP_RECIPE).read_text(encoding="utf-8"))

    assert data["input"]["zip"] == ZIP_FIXTURE
    assert [stage["module"] for stage in data["stages"]] == [
        "archive_unpack_manifest_v1",
        "archive_route_members_v1",
    ]


def test_archive_route_output_path_resolution_handles_driver_relative_artifact():
    outdir = "output/runs/story205/02_archive_route_members_v1"
    artifact_path = "output/runs/story205/02_archive_route_members_v1/archive_member_routes.jsonl"

    assert _resolve_output_path(outdir, artifact_path) == Path(artifact_path)
    assert _resolve_output_path(outdir, "archive_member_routes.jsonl") == (
        Path(outdir) / "archive_member_routes.jsonl"
    )


def test_mixed_archive_zip_recipe_smoke(tmp_path: Path):
    _skip_if_mixed_archive_support_missing()

    run_id = f"mixed-archive-zip-smoke-{uuid.uuid4().hex[:8]}"
    output_root = tmp_path / "runs"
    run_dir = output_root / run_id

    result = subprocess.run(
        [
            sys.executable,
            "driver.py",
            "--recipe",
            ZIP_RECIPE,
            "--input-zip",
            ZIP_FIXTURE,
            "--run-id",
            run_id,
            "--output-dir",
            str(output_root),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    manifest_path = run_dir / "01_archive_unpack_manifest_v1" / "archive_members_manifest.jsonl"
    routes_path = run_dir / "02_archive_route_members_v1" / "archive_member_routes.jsonl"

    assert manifest_path.exists()
    assert routes_path.exists()

    manifest_rows = [ArchiveMemberManifest(**row) for row in _load_jsonl(manifest_path)]
    route_rows = [ArchiveMemberRoute(**row) for row in _load_jsonl(routes_path)]

    assert [row.member_path for row in manifest_rows] == [
        "docs/reference.docx",
        "mail/message.eml",
        "web/snapshot.html",
        "notes/readme.txt",
    ]
    assert [row.detected_input_kind for row in manifest_rows] == [
        "docx",
        "email-eml",
        "web-page",
        None,
    ]
    assert all(Path(row.extracted_path).exists() for row in manifest_rows)

    by_member = {row.member_path: row for row in route_rows}
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
        bundle_manifest_path = Path(row.downstream_output_dir) / "output" / "html" / "manifest.json"
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


def test_archive_route_zip_pdf_member_launches_recommendation_only_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    run_id = "mixed-archive-pdf-route"
    output_root = tmp_path / "runs"
    run_dir = output_root / run_id
    extracted_pdf = (
        run_dir
        / "01_archive_unpack_manifest_v1"
        / "extracted_members"
        / "docs"
        / "proposal.pdf"
    )
    extracted_pdf.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile("testdata/flat-born-digital-mini.pdf", extracted_pdf)

    manifest_path = (
        run_dir / "01_archive_unpack_manifest_v1" / "archive_members_manifest.jsonl"
    )
    _write_jsonl(
        manifest_path,
        [
            {
                "schema_version": "archive_member_manifest_v1",
                "archive_format": "zip",
                "archive_path": str(Path(PDF_ZIP_FIXTURE).resolve()),
                "member_id": "member-001",
                "member_index": 1,
                "member_path": "docs/proposal.pdf",
                "extracted_path": str(extracted_pdf),
                "filename": "proposal.pdf",
                "file_extension": ".pdf",
                "detected_input_kind": "pdf",
                "file_size_bytes": extracted_pdf.stat().st_size,
            }
        ],
    )

    route_outdir = run_dir / "02_archive_route_members_v1"
    route_outdir.mkdir(parents=True, exist_ok=True)

    def fake_run(cmd: list[str], cwd: str):
        assert cwd == str(archive_route_module.REPO_ROOT)
        assert cmd[3] == archive_route_module.PDF_MEMBER_RECOMMENDATION_RECIPE
        assert cmd[4] == "--input-pdf"
        assert cmd[5] == str(extracted_pdf)
        downstream_run_id = cmd[7]
        output_dir = Path(cmd[cmd.index("--output-dir") + 1])
        plan_artifact = (
            output_dir / downstream_run_id / "05_confirm_plan_v1" / "overview_plan_final.jsonl"
        )
        _write_jsonl(
            plan_artifact,
            [
                {
                    "schema_version": "intake_plan_v1",
                    "book_type": "other",
                    "recommended_recipe": "configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml",
                    "warnings": [],
                    "signals": ["forms"],
                    "capability_gaps": [],
                    "meta": {
                        "source_input": {
                            "input_kind": "pdf",
                            "source_pdf": str(extracted_pdf),
                            "has_extractable_text": True,
                        }
                    },
                }
            ],
        )
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(archive_route_module.subprocess, "run", fake_run)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "archive_route_members_v1",
            "--manifest",
            str(manifest_path),
            "--outdir",
            str(route_outdir),
            "--run-id",
            run_id,
            "--allow-run-id-reuse",
        ],
    )

    archive_route_module.main()

    routes_path = route_outdir / "archive_member_routes.jsonl"
    rows = [ArchiveMemberRoute(**row) for row in _load_jsonl(routes_path)]
    assert len(rows) == 1
    row = rows[0]
    assert row.archive_format == "zip"
    assert row.member_path == "docs/proposal.pdf"
    assert row.detected_input_kind == "pdf"
    assert row.terminal_outcome == "launched"
    assert row.terminal_reason == "pdf_member_recommendation_only"
    assert (
        row.recommended_recipe
        == "configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml"
    )
    assert row.launch_input_flag == "--input-pdf"
    assert row.launch_input_path == str(extracted_pdf)
    assert row.driver_command[3] == archive_route_module.PDF_MEMBER_RECOMMENDATION_RECIPE
    assert row.first_downstream_artifact
    assert row.first_downstream_artifact.endswith(
        "05_confirm_plan_v1/overview_plan_final.jsonl"
    )
    assert Path(row.first_downstream_artifact).exists()
    plan = IntakePlan(**_load_jsonl(Path(row.first_downstream_artifact))[0])
    assert plan.meta["source_input"]["source_pdf"] == str(extracted_pdf)
    assert plan.recommended_recipe == row.recommended_recipe


def test_archive_route_folder_pdf_member_launches_recommendation_only_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    run_id = "mixed-folder-pdf-route"
    output_root = tmp_path / "runs"
    run_dir = output_root / run_id
    source_pdf = Path(FOLDER_PDF_FIXTURE).resolve() / "docs" / "proposal.pdf"
    assert source_pdf.exists()

    manifest_path = (
        run_dir / "01_folder_members_manifest_v1" / "archive_members_manifest.jsonl"
    )
    _write_jsonl(
        manifest_path,
        [
            {
                "schema_version": "archive_member_manifest_v1",
                "archive_format": "folder",
                "archive_path": str(Path(FOLDER_PDF_FIXTURE).resolve()),
                "member_id": "member-001",
                "member_index": 1,
                "member_path": "docs/proposal.pdf",
                "extracted_path": str(source_pdf),
                "filename": "proposal.pdf",
                "file_extension": ".pdf",
                "detected_input_kind": "pdf",
                "file_size_bytes": source_pdf.stat().st_size,
            }
        ],
    )

    route_outdir = run_dir / "02_archive_route_members_v1"
    route_outdir.mkdir(parents=True, exist_ok=True)

    def fake_run(cmd: list[str], cwd: str):
        assert cwd == str(archive_route_module.REPO_ROOT)
        assert cmd[3] == archive_route_module.PDF_MEMBER_RECOMMENDATION_RECIPE
        assert cmd[4] == "--input-pdf"
        assert cmd[5] == str(source_pdf)
        downstream_run_id = cmd[7]
        output_dir = Path(cmd[cmd.index("--output-dir") + 1])
        plan_artifact = (
            output_dir
            / downstream_run_id
            / "05_confirm_plan_v1"
            / "overview_plan_final.jsonl"
        )
        _write_jsonl(
            plan_artifact,
            [
                {
                    "schema_version": "intake_plan_v1",
                    "book_type": "other",
                    "recommended_recipe": "configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml",
                    "warnings": ["Missing capabilities: forms"],
                    "signals": ["forms"],
                    "capability_gaps": [],
                    "meta": {
                        "source_input": {
                            "input_kind": "pdf",
                            "source_pdf": str(source_pdf),
                            "has_extractable_text": True,
                        }
                    },
                }
            ],
        )
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(archive_route_module.subprocess, "run", fake_run)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "archive_route_members_v1",
            "--manifest",
            str(manifest_path),
            "--outdir",
            str(route_outdir),
            "--run-id",
            run_id,
        ],
    )

    archive_route_module.main()

    routes_path = route_outdir / "archive_member_routes.jsonl"
    rows = [ArchiveMemberRoute(**row) for row in _load_jsonl(routes_path)]
    assert len(rows) == 1
    row = rows[0]
    assert row.archive_format == "folder"
    assert row.member_path == "docs/proposal.pdf"
    assert row.terminal_outcome == "launched"
    assert row.terminal_reason == "pdf_member_recommendation_only"
    assert (
        row.recommended_recipe
        == "configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml"
    )
    assert row.downstream_run_id
    assert row.first_downstream_artifact
    assert row.first_downstream_artifact.endswith(
        "05_confirm_plan_v1/overview_plan_final.jsonl"
    )
    assert Path(row.first_downstream_artifact).exists()
    plan = IntakePlan(**_load_jsonl(Path(row.first_downstream_artifact))[0])
    assert plan.meta["source_input"]["source_pdf"] == str(source_pdf)
    assert plan.recommended_recipe == row.recommended_recipe
