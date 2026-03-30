import json
import subprocess
import sys
import venv
from pathlib import Path

from doc_web.runtime_contract import build_runtime_contract


REPO_ROOT = Path(__file__).resolve().parents[1]


def _venv_bin(venv_dir: Path, name: str) -> Path:
    if sys.platform.startswith("win"):
        return venv_dir / "Scripts" / f"{name}.exe"
    return venv_dir / "bin" / name


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

    manifest_path = run_dir / "output" / "html" / "manifest.json"
    provenance_path = run_dir / "output" / "html" / "provenance" / "blocks.jsonl"
    assert manifest_path.exists(), smoke.stdout
    assert provenance_path.exists(), smoke.stdout

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
