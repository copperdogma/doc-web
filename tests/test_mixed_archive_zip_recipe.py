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
from schemas import (
    ArchiveMemberManifest,
    ArchiveMemberRoute,
    DocWebBundleManifest,
    IntakeHandoff,
    IntakePlan,
)


ZIP_RECIPE = "configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml"
ZIP_FIXTURE = "testdata/mixed-archive-mini.zip"
PDF_ZIP_FIXTURE = "testdata/mixed-archive-pdf-mini.zip"
GROUPED_IMAGE_ZIP_FIXTURE = "testdata/mixed-archive-images-mini.zip"
GROUPED_IMAGE_ZIP_FIXTURE_META = "testdata/mixed-archive-images-mini.source.json"
FOLDER_PDF_FIXTURE = "testdata/mixed-folder-pdf-mini"
BORN_DIGITAL_NON_TOC_RECIPE = (
    "configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml"
)


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


def _fake_pdf_member_subprocess_runner(
    source_pdf: Path,
) -> tuple[callable, list[list[str]]]:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], cwd: str):
        assert cwd == str(archive_route_module.REPO_ROOT)
        calls.append(cmd)
        assert cmd[4] == "--input-pdf"
        assert cmd[5] == str(source_pdf)
        downstream_run_id = cmd[7]
        output_dir = Path(cmd[cmd.index("--output-dir") + 1])
        recipe_path = cmd[3]

        if recipe_path == archive_route_module.PDF_MEMBER_RECOMMENDATION_RECIPE:
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
                        "recommended_recipe": BORN_DIGITAL_NON_TOC_RECIPE,
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

        assert recipe_path == BORN_DIGITAL_NON_TOC_RECIPE
        launched_artifact = (
            output_dir
            / downstream_run_id
            / "01_extract_pdf_marker_lite_html_v1"
            / "pages_html.jsonl"
        )
        _write_jsonl(
            launched_artifact,
            [
                {
                    "schema_version": "pages_html_v1",
                    "source": [str(source_pdf)],
                    "html": "<p>Flat form fixture</p>",
                }
            ],
        )
        return subprocess.CompletedProcess(cmd, 0)

    return fake_run, calls


def _fake_grouped_image_subprocess_runner(
    source_dir: Path,
) -> tuple[callable, list[list[str]]]:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], cwd: str):
        assert cwd == str(archive_route_module.REPO_ROOT)
        calls.append(cmd)
        assert cmd[3] == archive_route_module.GROUPED_IMAGE_RECIPE
        assert cmd[4] == "--input-images"
        assert cmd[5] == str(source_dir)
        downstream_run_id = cmd[7]
        output_dir = Path(cmd[cmd.index("--output-dir") + 1])
        manifest_artifact = (
            output_dir
            / downstream_run_id
            / "01_images_dir_to_manifest_v1"
            / "pages_images_manifest.jsonl"
        )
        ocr_artifact = (
            output_dir / downstream_run_id / "02_ocr_ai_gpt51_v1" / "pages_html.jsonl"
        )
        _write_jsonl(
            manifest_artifact,
            [
                {
                    "schema_version": "page_image_v1",
                    "page": 1,
                    "page_number": 1,
                    "original_page_number": 1,
                    "image": str(source_dir / "page-001.png"),
                    "source": [str(source_dir)],
                },
                {
                    "schema_version": "page_image_v1",
                    "page": 2,
                    "page_number": 2,
                    "original_page_number": 2,
                    "image": str(source_dir / "page-002.png"),
                    "source": [str(source_dir)],
                },
            ],
        )
        _write_jsonl(
            ocr_artifact,
            [
                {
                    "schema_version": "page_html_v1",
                    "page": 1,
                    "page_number": 1,
                    "original_page_number": 1,
                    "source": [str(source_dir / "page-001.png")],
                    "html": "<p>March 3, 1985</p>",
                },
                {
                    "schema_version": "page_html_v1",
                    "page": 2,
                    "page_number": 2,
                    "original_page_number": 2,
                    "source": [str(source_dir / "page-002.png")],
                    "html": "<p>The letters from Aunt Elise are tied with green ribbon, not red.</p>",
                },
            ],
        )
        return subprocess.CompletedProcess(cmd, 0)

    return fake_run, calls


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
    assert data["stages"][1]["params"]["pdf_member_handoff_mode"] == "launch"
    assert data["stages"][1]["params"]["grouped_image_downstream_end_at"] == "ocr_ai"


def test_archive_route_output_path_resolution_handles_driver_relative_artifact():
    outdir = "output/runs/story205/02_archive_route_members_v1"
    artifact_path = "output/runs/story205/02_archive_route_members_v1/archive_member_routes.jsonl"

    assert _resolve_output_path(outdir, artifact_path) == Path(artifact_path)
    assert _resolve_output_path(outdir, "archive_member_routes.jsonl") == (
        Path(outdir) / "archive_member_routes.jsonl"
    )


def test_mixed_archive_grouped_image_fixture_shape():
    metadata = json.loads(Path(GROUPED_IMAGE_ZIP_FIXTURE_META).read_text(encoding="utf-8"))

    assert metadata["archive_format"] == "zip"
    assert [member["member_path"] for member in metadata["members"]] == [
        "pages/page-001.png",
        "pages/page-002.png",
        "notes/readme.txt",
    ]
    assert metadata["members"][0]["expected_route"] == "grouped-images-dir-launch"
    assert any(
        "grouped image-member route rows" in scope for scope in metadata["supported_scope"]
    )
    assert "No grouped image-member routing" not in metadata["known_gaps"]
    assert Path(GROUPED_IMAGE_ZIP_FIXTURE).exists()


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
        assert "--end-at" not in cmd
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
                    "recommended_recipe": BORN_DIGITAL_NON_TOC_RECIPE,
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
            "--grouped-image-downstream-end-at",
            "ocr_ai",
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
    assert row.recommended_recipe == BORN_DIGITAL_NON_TOC_RECIPE
    assert row.approval_mode == "confirm_plan_auto_approve"
    assert row.handoff_artifact_path is None
    assert row.launch_input_flag == "--input-pdf"
    assert row.launch_input_path == str(extracted_pdf)
    assert row.driver_command[3] == archive_route_module.PDF_MEMBER_RECOMMENDATION_RECIPE
    assert "--end-at" not in row.driver_command
    assert row.first_downstream_artifact
    assert row.first_downstream_artifact.endswith(
        "05_confirm_plan_v1/overview_plan_final.jsonl"
    )
    assert Path(row.first_downstream_artifact).exists()
    plan = IntakePlan(**_load_jsonl(Path(row.first_downstream_artifact))[0])
    assert plan.meta["source_input"]["source_pdf"] == str(extracted_pdf)
    assert plan.recommended_recipe == row.recommended_recipe


def test_archive_route_zip_grouped_image_members_launch_shared_images_dir_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    run_id = "mixed-archive-images-launch"
    output_root = tmp_path / "runs"
    run_dir = output_root / run_id
    extracted_dir = (
        run_dir
        / "01_archive_unpack_manifest_v1"
        / "extracted_members"
        / "pages"
    )
    extracted_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile("testdata/handwritten-notes-mini-images/page-001.png", extracted_dir / "page-001.png")
    shutil.copyfile("testdata/handwritten-notes-mini-images/page-002.png", extracted_dir / "page-002.png")
    notes_dir = (
        run_dir
        / "01_archive_unpack_manifest_v1"
        / "extracted_members"
        / "notes"
    )
    notes_dir.mkdir(parents=True, exist_ok=True)
    (notes_dir / "readme.txt").write_text(
        "This unsupported text member proves explicit blocked routing.\n",
        encoding="utf-8",
    )

    manifest_path = (
        run_dir / "01_archive_unpack_manifest_v1" / "archive_members_manifest.jsonl"
    )
    _write_jsonl(
        manifest_path,
        [
            {
                "schema_version": "archive_member_manifest_v1",
                "archive_format": "zip",
                "archive_path": str(Path(GROUPED_IMAGE_ZIP_FIXTURE).resolve()),
                "member_id": "member-001",
                "member_index": 1,
                "member_path": "pages/page-002.png",
                "extracted_path": str(extracted_dir / "page-002.png"),
                "filename": "page-002.png",
                "file_extension": ".png",
                "detected_input_kind": None,
                "file_size_bytes": (extracted_dir / "page-002.png").stat().st_size,
            },
            {
                "schema_version": "archive_member_manifest_v1",
                "archive_format": "zip",
                "archive_path": str(Path(GROUPED_IMAGE_ZIP_FIXTURE).resolve()),
                "member_id": "member-002",
                "member_index": 2,
                "member_path": "pages/page-001.png",
                "extracted_path": str(extracted_dir / "page-001.png"),
                "filename": "page-001.png",
                "file_extension": ".png",
                "detected_input_kind": None,
                "file_size_bytes": (extracted_dir / "page-001.png").stat().st_size,
            },
            {
                "schema_version": "archive_member_manifest_v1",
                "archive_format": "zip",
                "archive_path": str(Path(GROUPED_IMAGE_ZIP_FIXTURE).resolve()),
                "member_id": "member-003",
                "member_index": 3,
                "member_path": "notes/readme.txt",
                "extracted_path": str(notes_dir / "readme.txt"),
                "filename": "readme.txt",
                "file_extension": ".txt",
                "detected_input_kind": None,
                "file_size_bytes": (notes_dir / "readme.txt").stat().st_size,
            },
        ],
    )

    route_outdir = run_dir / "02_archive_route_members_v1"
    route_outdir.mkdir(parents=True, exist_ok=True)

    fake_run, calls = _fake_grouped_image_subprocess_runner(extracted_dir)
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
            "--grouped-image-downstream-end-at",
            "ocr_ai",
            "--allow-run-id-reuse",
        ],
    )

    archive_route_module.main()

    routes_path = route_outdir / "archive_member_routes.jsonl"
    rows = [ArchiveMemberRoute(**row) for row in _load_jsonl(routes_path)]
    assert len(rows) == 3
    by_member = {row.member_path: row for row in rows}

    primary_row = by_member["pages/page-001.png"]
    secondary_row = by_member["pages/page-002.png"]
    blocked_row = by_member["notes/readme.txt"]

    assert primary_row.group_role == "primary"
    assert secondary_row.group_role == "secondary"
    assert primary_row.group_id == secondary_row.group_id == "images-dir:pages"
    assert primary_row.group_key == secondary_row.group_key == "pages"
    assert primary_row.group_size == secondary_row.group_size == 2
    assert primary_row.detected_input_kind == "images_dir"
    assert secondary_row.detected_input_kind == "images_dir"
    assert primary_row.recommended_recipe == archive_route_module.GROUPED_IMAGE_RECIPE
    assert secondary_row.recommended_recipe == archive_route_module.GROUPED_IMAGE_RECIPE
    assert primary_row.launch_input_flag == secondary_row.launch_input_flag == "--input-images"
    assert primary_row.launch_input_path == secondary_row.launch_input_path == str(extracted_dir)
    assert primary_row.downstream_run_id == secondary_row.downstream_run_id
    assert primary_row.first_downstream_artifact == secondary_row.first_downstream_artifact
    assert Path(primary_row.first_downstream_artifact).exists()
    launched_rows = _load_jsonl(Path(primary_row.first_downstream_artifact))
    assert [row["image"] for row in launched_rows] == [
        str(extracted_dir / "page-001.png"),
        str(extracted_dir / "page-002.png"),
    ]
    assert launched_rows[0]["source"] == [str(extracted_dir)]
    assert primary_row.terminal_outcome == secondary_row.terminal_outcome == "launched"
    assert (
        primary_row.terminal_reason
        == secondary_row.terminal_reason
        == "grouped_image_end_at:ocr_ai"
    )
    ocr_artifact = (
        Path(primary_row.downstream_output_dir) / "02_ocr_ai_gpt51_v1" / "pages_html.jsonl"
    )
    assert ocr_artifact.exists()
    ocr_rows = _load_jsonl(ocr_artifact)
    assert ocr_rows[0]["html"] == "<p>March 3, 1985</p>"
    assert "Aunt Elise" in ocr_rows[1]["html"]

    assert blocked_row.group_id is None
    assert blocked_row.group_key is None
    assert blocked_row.group_role is None
    assert blocked_row.group_size is None
    assert blocked_row.terminal_outcome == "blocked"
    assert blocked_row.terminal_reason == "unsupported_archive_member_suffix:.txt"

    assert len(calls) == 1
    assert calls[0][3] == archive_route_module.GROUPED_IMAGE_RECIPE
    assert calls[0][4] == "--input-images"
    assert calls[0][5] == str(extracted_dir)
    assert calls[0][-2:] == ["--end-at", "ocr_ai"]


def test_archive_route_zip_pdf_member_writes_handoff_artifact_in_dry_run_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    run_id = "mixed-archive-pdf-handoff"
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
                    "recommended_recipe": BORN_DIGITAL_NON_TOC_RECIPE,
                    "warnings": ["Missing capabilities: forms"],
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
            "--pdf-member-handoff-mode",
            "dry_run",
        ],
    )

    archive_route_module.main()

    routes_path = route_outdir / "archive_member_routes.jsonl"
    rows = [ArchiveMemberRoute(**row) for row in _load_jsonl(routes_path)]
    assert len(rows) == 1
    row = rows[0]
    assert row.archive_format == "zip"
    assert row.member_path == "docs/proposal.pdf"
    assert row.terminal_outcome == "skipped"
    assert row.terminal_reason == "pdf_member_approved_handoff_dry_run"
    assert row.approval_mode == "confirm_plan_auto_approve"
    assert row.handoff_artifact_path
    assert Path(row.handoff_artifact_path).exists()
    handoff = IntakeHandoff(**_load_jsonl(Path(row.handoff_artifact_path))[0])
    assert handoff.plan_path == row.first_downstream_artifact
    assert handoff.launch_input_flag == "--input-pdf"
    assert handoff.launch_input_path == str(extracted_pdf)
    assert handoff.terminal_outcome == "skipped"
    assert handoff.terminal_reason == "dry_run"
    assert handoff.downstream_output_dir == str(
        output_root
        / "mixed-archive-pdf-handoff-member-001-approved-handoff-recipe-born-digital-pdf-non-toc-html-mvp"
    )


def test_archive_route_zip_pdf_member_launches_from_approved_handoff(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    run_id = "mixed-archive-pdf-launch"
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

    fake_run, calls = _fake_pdf_member_subprocess_runner(extracted_pdf)
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
            "--pdf-member-handoff-mode",
            "launch",
        ],
    )

    archive_route_module.main()

    routes_path = route_outdir / "archive_member_routes.jsonl"
    rows = [ArchiveMemberRoute(**row) for row in _load_jsonl(routes_path)]
    assert len(rows) == 1
    row = rows[0]
    assert row.archive_format == "zip"
    assert row.member_path == "docs/proposal.pdf"
    assert row.terminal_outcome == "launched"
    assert row.terminal_reason == "pdf_member_launched_from_approved_plan"
    assert row.approval_mode == "confirm_plan_auto_approve"
    assert row.handoff_artifact_path
    assert Path(row.handoff_artifact_path).exists()
    handoff = IntakeHandoff(**_load_jsonl(Path(row.handoff_artifact_path))[0])
    assert handoff.plan_path == row.first_downstream_artifact
    assert handoff.recommended_recipe == BORN_DIGITAL_NON_TOC_RECIPE
    assert handoff.launch_input_path == str(extracted_pdf)
    assert handoff.terminal_outcome == "launched"
    assert handoff.terminal_reason is None
    assert handoff.exit_code == 0
    launched_artifact = (
        Path(handoff.downstream_output_dir)
        / "01_extract_pdf_marker_lite_html_v1"
        / "pages_html.jsonl"
    )
    assert launched_artifact.exists()
    launched_rows = _load_jsonl(launched_artifact)
    assert launched_rows[0]["source"] == [str(extracted_pdf)]
    assert calls[0][3] == archive_route_module.PDF_MEMBER_RECOMMENDATION_RECIPE
    assert calls[1][3] == BORN_DIGITAL_NON_TOC_RECIPE


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
                    "recommended_recipe": BORN_DIGITAL_NON_TOC_RECIPE,
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
    assert row.recommended_recipe == BORN_DIGITAL_NON_TOC_RECIPE
    assert row.downstream_run_id
    assert row.first_downstream_artifact
    assert row.first_downstream_artifact.endswith(
        "05_confirm_plan_v1/overview_plan_final.jsonl"
    )
    assert Path(row.first_downstream_artifact).exists()
    plan = IntakePlan(**_load_jsonl(Path(row.first_downstream_artifact))[0])
    assert plan.meta["source_input"]["source_pdf"] == str(source_pdf)
    assert plan.recommended_recipe == row.recommended_recipe


def test_archive_route_folder_pdf_member_writes_handoff_artifact_in_dry_run_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    run_id = "mixed-folder-pdf-handoff"
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
                    "recommended_recipe": BORN_DIGITAL_NON_TOC_RECIPE,
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
            "--allow-run-id-reuse",
            "--pdf-member-handoff-mode",
            "dry_run",
        ],
    )

    archive_route_module.main()

    routes_path = route_outdir / "archive_member_routes.jsonl"
    rows = [ArchiveMemberRoute(**row) for row in _load_jsonl(routes_path)]
    assert len(rows) == 1
    row = rows[0]
    assert row.archive_format == "folder"
    assert row.member_path == "docs/proposal.pdf"
    assert row.terminal_outcome == "skipped"
    assert row.terminal_reason == "pdf_member_approved_handoff_dry_run"
    assert row.approval_mode == "confirm_plan_auto_approve"
    assert row.handoff_artifact_path
    assert Path(row.handoff_artifact_path).exists()
    handoff = IntakeHandoff(**_load_jsonl(Path(row.handoff_artifact_path))[0])
    assert handoff.plan_path == row.first_downstream_artifact
    assert handoff.launch_input_flag == "--input-pdf"
    assert handoff.launch_input_path == str(source_pdf)
    assert handoff.terminal_outcome == "skipped"
    assert handoff.terminal_reason == "dry_run"
    assert handoff.downstream_output_dir == str(
        output_root
        / "mixed-folder-pdf-handoff-member-001-approved-handoff-recipe-born-digital-pdf-non-toc-html-mvp"
    )


def test_archive_route_folder_pdf_member_launches_from_approved_handoff(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    run_id = "mixed-folder-pdf-launch"
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

    fake_run, calls = _fake_pdf_member_subprocess_runner(source_pdf)
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
            "--pdf-member-handoff-mode",
            "launch",
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
    assert row.terminal_reason == "pdf_member_launched_from_approved_plan"
    assert row.approval_mode == "confirm_plan_auto_approve"
    assert row.handoff_artifact_path
    assert Path(row.handoff_artifact_path).exists()
    handoff = IntakeHandoff(**_load_jsonl(Path(row.handoff_artifact_path))[0])
    assert handoff.plan_path == row.first_downstream_artifact
    assert handoff.recommended_recipe == BORN_DIGITAL_NON_TOC_RECIPE
    assert handoff.launch_input_path == str(source_pdf)
    assert handoff.terminal_outcome == "launched"
    assert handoff.terminal_reason is None
    assert handoff.exit_code == 0
    launched_artifact = (
        Path(handoff.downstream_output_dir)
        / "01_extract_pdf_marker_lite_html_v1"
        / "pages_html.jsonl"
    )
    assert launched_artifact.exists()
    launched_rows = _load_jsonl(launched_artifact)
    assert launched_rows[0]["source"] == [str(source_pdf)]
    assert calls[0][3] == archive_route_module.PDF_MEMBER_RECOMMENDATION_RECIPE
    assert calls[1][3] == BORN_DIGITAL_NON_TOC_RECIPE
