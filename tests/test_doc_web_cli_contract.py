import json
import shutil
import subprocess
import sys
import venv
from pathlib import Path

import pytest

from doc_web.runtime_contract import build_runtime_contract


REPO_ROOT = Path(__file__).resolve().parents[1]


def _venv_bin(venv_dir: Path, name: str) -> Path:
    if sys.platform.startswith("win"):
        return venv_dir / "Scripts" / f"{name}.exe"
    return venv_dir / "bin" / name


def _skip_if_office_runtime_pin_unsupported() -> None:
    if sys.version_info >= (3, 13):
        pytest.skip("Maintained unstructured runtime smokes are validated on Python 3.11/3.12.")


def _skip_if_pandoc_missing() -> None:
    if shutil.which("pandoc") is None:
        pytest.skip("Pandoc is required for maintained EPUB smokes.")


def _validate_bundle_outputs(python_bin: Path, run_dir: Path) -> None:
    manifest_path = run_dir / "output" / "html" / "manifest.json"
    provenance_path = run_dir / "output" / "html" / "provenance" / "blocks.jsonl"
    assert manifest_path.exists()
    assert provenance_path.exists()

    manifest_validation = subprocess.run(
        [
            str(python_bin),
            "validate_artifact.py",
            "--schema",
            "doc_web_bundle_manifest_v1",
            "--file",
            str(manifest_path),
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert manifest_validation.returncode == 0, manifest_validation.stdout

    provenance_validation = subprocess.run(
        [
            str(python_bin),
            "validate_artifact.py",
            "--schema",
            "doc_web_provenance_block_v1",
            "--file",
            str(provenance_path),
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert provenance_validation.returncode == 0, provenance_validation.stdout


def test_runtime_contract_payload_has_required_fields():
    payload = build_runtime_contract()

    assert payload["contract_name"] == "doc-web"
    assert payload["contract_version"] == "1"
    assert payload["package_name"] == "doc-web"
    assert payload["runtime_version"]
    assert payload["requires_python"] == ">=3.11"
    assert payload["supported_bundle_schema_versions"] == {
        "manifest": "doc_web_bundle_manifest_v1",
        "provenance": "doc_web_provenance_block_v1",
    }
    assert payload["schema_fingerprint"].startswith("sha256:")
    assert payload["compatibility_policy"] == {
        "contract_version_role": "coarse-runtime-boundary-family",
        "consumer_gate_fields": [
            "schema_fingerprint",
            "supported_bundle_schema_versions",
        ],
    }


def test_doc_web_module_cli_emits_machine_readable_contract_json():
    proc = subprocess.run(
        [sys.executable, "-m", "doc_web", "contract", "--json"],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload == build_runtime_contract()


def test_pip_install_exposes_doc_web_console_script(tmp_path: Path):
    venv_dir = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True, system_site_packages=False).create(venv_dir)
    python_bin = _venv_bin(venv_dir, "python")
    cli_bin = _venv_bin(venv_dir, "doc-web")

    install = subprocess.run(
        [
            str(python_bin),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            str(REPO_ROOT),
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert install.returncode == 0, install.stdout

    proc = subprocess.run(
        [str(cli_bin), "contract", "--json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload == build_runtime_contract()


def test_driver_extra_supports_repo_owned_doc_web_fixture_smoke(tmp_path: Path):
    venv_dir = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True, system_site_packages=False).create(venv_dir)
    python_bin = _venv_bin(venv_dir, "python")
    output_root = tmp_path / "runs"
    run_id = "venv-doc-web-fixture"
    run_dir = output_root / run_id

    install = subprocess.run(
        [
            str(python_bin),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            f"{REPO_ROOT}[driver]",
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert install.returncode == 0, install.stdout

    smoke = subprocess.run(
        [
            str(python_bin),
            "driver.py",
            "--recipe",
            "configs/recipes/doc-web-fixture-bundle-smoke.yaml",
            "--run-id",
            run_id,
            "--allow-run-id-reuse",
            "--force",
            "--output-dir",
            str(output_root),
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert smoke.returncode == 0, smoke.stdout

    _validate_bundle_outputs(python_bin, run_dir)

    manifest_path = run_dir / "output" / "html" / "manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["reading_order"] == ["chapter-001", "page-001"]


def test_docx_extra_supports_repo_owned_docx_smoke(tmp_path: Path):
    _skip_if_office_runtime_pin_unsupported()

    venv_dir = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True, system_site_packages=False).create(venv_dir)
    python_bin = _venv_bin(venv_dir, "python")
    output_root = tmp_path / "runs"
    run_id = "venv-docx-smoke"
    run_dir = output_root / run_id

    install = subprocess.run(
        [
            str(python_bin),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            f"{REPO_ROOT}[driver,docx]",
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert install.returncode == 0, install.stdout

    smoke = subprocess.run(
        [
            str(python_bin),
            "driver.py",
            "--recipe",
            "configs/recipes/recipe-docx-html-mvp.yaml",
            "--input-docx",
            "testdata/docx-mini.docx",
            "--run-id",
            run_id,
            "--allow-run-id-reuse",
            "--force",
            "--output-dir",
            str(output_root),
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert smoke.returncode == 0, smoke.stdout

    _validate_bundle_outputs(python_bin, run_dir)

    manifest_path = run_dir / "output" / "html" / "manifest.json"
    provenance_path = run_dir / "output" / "html" / "provenance" / "blocks.jsonl"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    blocks = [
        json.loads(line)
        for line in provenance_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert manifest["reading_order"] == ["chapter-001", "chapter-002"]
    assert blocks
    assert all(block.get("source_page_number") is None for block in blocks)


def test_email_extra_supports_repo_owned_eml_smoke(tmp_path: Path):
    _skip_if_office_runtime_pin_unsupported()

    venv_dir = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True, system_site_packages=False).create(venv_dir)
    python_bin = _venv_bin(venv_dir, "python")
    output_root = tmp_path / "runs"
    run_id = "venv-email-smoke"
    run_dir = output_root / run_id

    install = subprocess.run(
        [
            str(python_bin),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            f"{REPO_ROOT}[driver,email]",
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert install.returncode == 0, install.stdout

    smoke = subprocess.run(
        [
            str(python_bin),
            "driver.py",
            "--recipe",
            "configs/recipes/recipe-email-eml-html-mvp.yaml",
            "--input-eml",
            "testdata/email-eml-mini.eml",
            "--run-id",
            run_id,
            "--allow-run-id-reuse",
            "--force",
            "--output-dir",
            str(output_root),
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert smoke.returncode == 0, smoke.stdout

    _validate_bundle_outputs(python_bin, run_dir)

    manifest_path = run_dir / "output" / "html" / "manifest.json"
    report_path = run_dir / "02_email_elements_to_bundle_v1" / "email_bundle_report.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert manifest["reading_order"] == ["page-001"]
    assert report["message_metadata"]["subject"] == "Fixture Subject"
    assert report["message_metadata"]["sent_from"] == ["Alice Example <alice@example.com>"]
    assert report["message_metadata"]["sent_to"] == ["Bob Example <bob@example.com>"]


def test_xlsx_extra_supports_repo_owned_xlsx_smoke(tmp_path: Path):
    _skip_if_office_runtime_pin_unsupported()

    venv_dir = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True, system_site_packages=False).create(venv_dir)
    python_bin = _venv_bin(venv_dir, "python")
    output_root = tmp_path / "runs"
    run_id = "venv-xlsx-smoke"
    run_dir = output_root / run_id

    install = subprocess.run(
        [
            str(python_bin),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            f"{REPO_ROOT}[driver,xlsx]",
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert install.returncode == 0, install.stdout

    smoke = subprocess.run(
        [
            str(python_bin),
            "driver.py",
            "--recipe",
            "configs/recipes/recipe-xlsx-html-mvp.yaml",
            "--input-xlsx",
            "testdata/xlsx-mini.xlsx",
            "--run-id",
            run_id,
            "--allow-run-id-reuse",
            "--force",
            "--output-dir",
            str(output_root),
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert smoke.returncode == 0, smoke.stdout

    _validate_bundle_outputs(python_bin, run_dir)

    manifest_path = run_dir / "output" / "html" / "manifest.json"
    provenance_path = run_dir / "output" / "html" / "provenance" / "blocks.jsonl"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    blocks = [
        json.loads(line)
        for line in provenance_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert manifest["reading_order"] == ["page-001", "page-002"]
    assert [entry["title"] for entry in manifest["entries"]] == ["Roster", "Visits"]
    assert blocks
    assert all(block.get("source_page_number") is None for block in blocks)


def test_pptx_extra_supports_repo_owned_pptx_smoke(tmp_path: Path):
    _skip_if_office_runtime_pin_unsupported()

    venv_dir = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True, system_site_packages=False).create(venv_dir)
    python_bin = _venv_bin(venv_dir, "python")
    output_root = tmp_path / "runs"
    run_id = "venv-pptx-smoke"
    run_dir = output_root / run_id

    install = subprocess.run(
        [
            str(python_bin),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            f"{REPO_ROOT}[driver,pptx]",
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert install.returncode == 0, install.stdout

    smoke = subprocess.run(
        [
            str(python_bin),
            "driver.py",
            "--recipe",
            "configs/recipes/recipe-pptx-html-mvp.yaml",
            "--input-pptx",
            "testdata/pptx-mini.pptx",
            "--run-id",
            run_id,
            "--allow-run-id-reuse",
            "--force",
            "--output-dir",
            str(output_root),
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert smoke.returncode == 0, smoke.stdout

    _validate_bundle_outputs(python_bin, run_dir)

    manifest_path = run_dir / "output" / "html" / "manifest.json"
    provenance_path = run_dir / "output" / "html" / "provenance" / "blocks.jsonl"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    blocks = [
        json.loads(line)
        for line in provenance_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert manifest["reading_order"] == ["page-001", "page-002", "page-003"]
    assert [entry["source_pages"] for entry in manifest["entries"]] == [[1], [2], [3]]
    assert blocks
    assert all(block.get("source_page_number") in {1, 2, 3} for block in blocks)


def test_epub_extra_supports_repo_owned_epub_smoke(tmp_path: Path):
    _skip_if_office_runtime_pin_unsupported()
    _skip_if_pandoc_missing()

    venv_dir = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True, system_site_packages=False).create(venv_dir)
    python_bin = _venv_bin(venv_dir, "python")
    output_root = tmp_path / "runs"
    run_id = "venv-epub-smoke"
    run_dir = output_root / run_id

    install = subprocess.run(
        [
            str(python_bin),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            f"{REPO_ROOT}[driver,epub]",
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert install.returncode == 0, install.stdout

    smoke = subprocess.run(
        [
            str(python_bin),
            "driver.py",
            "--recipe",
            "configs/recipes/recipe-epub-html-mvp.yaml",
            "--input-epub",
            "testdata/epub-mini.epub",
            "--run-id",
            run_id,
            "--allow-run-id-reuse",
            "--force",
            "--output-dir",
            str(output_root),
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert smoke.returncode == 0, smoke.stdout

    _validate_bundle_outputs(python_bin, run_dir)

    manifest_path = run_dir / "output" / "html" / "manifest.json"
    provenance_path = run_dir / "output" / "html" / "provenance" / "blocks.jsonl"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    blocks = [
        json.loads(line)
        for line in provenance_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert manifest["title"] == "EPUB Mini Fixture"
    assert manifest["reading_order"] == ["chapter-001", "chapter-002"]
    assert [entry["title"] for entry in manifest["entries"]] == ["Chapter One", "Chapter Two"]
    assert [entry["source_pages"] for entry in manifest["entries"]] == [[], []]
    assert blocks
    assert all(block.get("source_page_number") is None for block in blocks)


def test_requirements_txt_supports_pptx_import_on_supported_python(tmp_path: Path):
    _skip_if_office_runtime_pin_unsupported()

    venv_dir = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True, system_site_packages=False).create(venv_dir)
    python_bin = _venv_bin(venv_dir, "python")

    install = subprocess.run(
        [
            str(python_bin),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "-r",
            "requirements.txt",
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert install.returncode == 0, install.stdout

    probe = subprocess.run(
        [
            str(python_bin),
            "-c",
            "from unstructured.partition.pptx import partition_pptx; print(partition_pptx.__name__)",
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert probe.returncode == 0, probe.stdout
    assert "partition_pptx" in probe.stdout


def test_requirements_txt_supports_epub_partition_on_supported_python(tmp_path: Path):
    _skip_if_office_runtime_pin_unsupported()
    _skip_if_pandoc_missing()

    venv_dir = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True, system_site_packages=False).create(venv_dir)
    python_bin = _venv_bin(venv_dir, "python")

    install = subprocess.run(
        [
            str(python_bin),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "-r",
            "requirements.txt",
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert install.returncode == 0, install.stdout

    probe = subprocess.run(
        [
            str(python_bin),
            "-c",
            (
                "from pathlib import Path; "
                "from unstructured.partition.epub import partition_epub; "
                "rows = partition_epub(filename=str(Path('testdata/epub-mini.epub').resolve())); "
                "print(len(rows))"
            ),
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert probe.returncode == 0, probe.stdout
    assert int(probe.stdout.strip()) >= 2
