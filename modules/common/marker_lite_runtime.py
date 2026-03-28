from __future__ import annotations

import json
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKTREE_ID = REPO_ROOT.parent.name
DEFAULT_CONTAINER = f"story165-marker-cpu-{WORKTREE_ID}"
DEFAULT_BOOTSTRAP_FROM_CONTAINER = "story165-marker-cpu"
DEFAULT_BOOTSTRAP_REPOSITORY = "doc-web/story165-marker-cpu"
DEFAULT_BOOTSTRAP_IMAGE = f"{DEFAULT_BOOTSTRAP_REPOSITORY}:{WORKTREE_ID}"
DEFAULT_PIP_CACHE_DIR = REPO_ROOT / ".cache" / "marker-benchmark-pip"
DEFAULT_DATALAB_CACHE_DIR = REPO_ROOT / ".cache" / "marker-benchmark-datalab"
DEFAULT_TMP_DIR = REPO_ROOT / ".cache" / "marker-benchmark-tmp"
DEFAULT_BASE_IMAGE = "python:3.12-slim-bookworm"


@dataclass(frozen=True)
class FormatArtifact:
    output_format: str
    output_dir: Path
    main_output: Path
    meta_output: Path
    log_output: Path


def _run(cmd: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=True,
        text=True,
        capture_output=True,
    )


def _run_optional(
    cmd: list[str],
    *,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=False,
        text=True,
        capture_output=True,
    )


def _docker_inspect(name: str) -> dict[str, Any] | None:
    proc = _run_optional(["docker", "inspect", name])
    if proc.returncode != 0:
        return None
    payload = json.loads(proc.stdout)
    return payload[0] if payload else None


def _docker_image_exists(image: str) -> bool:
    return _run_optional(["docker", "image", "inspect", image]).returncode == 0


def _flattened_image_name(image: str) -> str:
    if ":" in image:
        repo, tag = image.rsplit(":", 1)
    else:
        repo, tag = image, "latest"
    return f"{repo}-flat:{tag}"


def _flatten_image(image: str, *, notes: list[str]) -> str:
    flattened_image = _flattened_image_name(image)
    if _docker_image_exists(flattened_image):
        notes.append(f"reused flattened cached image {flattened_image!r}")
        return flattened_image

    temp_container = f"marker-flat-{abs(hash((image, flattened_image))) % 1_000_000}"
    _run_optional(["docker", "rm", "-f", temp_container])
    try:
        _run(["docker", "create", "--name", temp_container, image, "sleep", "infinity"])
        proc = subprocess.run(
            [
                "bash",
                "-lc",
                f"docker export {temp_container} | docker import - {flattened_image}",
            ],
            check=False,
            text=True,
            capture_output=True,
        )
        if proc.returncode != 0 and not _docker_image_exists(flattened_image):
            raise RuntimeError(
                f"Flattening cached image {image!r} failed: {proc.stderr.strip() or proc.stdout.strip()}"
            )
        imported_ref = (proc.stdout.strip() or proc.stderr.strip() or flattened_image).splitlines()[-1]
        notes.append(
            f"flattened cached image {image!r} into {flattened_image!r} ({imported_ref}) to strip stale bind metadata"
        )
        return flattened_image
    finally:
        _run_optional(["docker", "rm", "-f", temp_container])


def _available_bootstrap_images(repository: str = DEFAULT_BOOTSTRAP_REPOSITORY) -> list[str]:
    proc = _run_optional(
        ["docker", "images", repository, "--format", "{{.Repository}}:{{.Tag}}"]
    )
    if proc.returncode != 0:
        return []
    images: list[str] = []
    for line in proc.stdout.splitlines():
        image = line.strip()
        if not image or image.endswith(":<none>"):
            continue
        images.append(image)
    return images


def _discover_cached_bootstrap_image(preferred_image: str) -> str | None:
    if _docker_image_exists(preferred_image):
        return preferred_image
    for candidate in _available_bootstrap_images():
        if candidate != preferred_image:
            return candidate
    return None


def _work_mount_source(container_info: dict[str, Any]) -> Path | None:
    for mount in container_info.get("Mounts", []):
        if mount.get("Destination") == "/work" and mount.get("Source"):
            return Path(str(mount["Source"])).resolve()
    return None


def _mount_source(container_info: dict[str, Any], destination: str) -> Path | None:
    for mount in container_info.get("Mounts", []):
        if mount.get("Destination") == destination and mount.get("Source"):
            return Path(str(mount["Source"])).resolve()
    return None


def _container_mounts_match(
    container_info: dict[str, Any],
    *,
    datalab_cache_dir: Path,
    tmp_dir: Path,
    work_mount_source: Path | None = None,
    pip_cache_dir: Path | None = None,
) -> bool:
    work_ok = True
    pip_ok = True
    if work_mount_source is not None:
        work_ok = _work_mount_source(container_info) == work_mount_source.resolve()
    if pip_cache_dir is not None:
        pip_ok = _mount_source(container_info, "/root/.cache/pip") == pip_cache_dir.resolve()
    return (
        work_ok
        and pip_ok
        and _mount_source(container_info, "/root/.cache/datalab") == datalab_cache_dir.resolve()
        and _mount_source(container_info, "/tmp") == tmp_dir.resolve()
    )


def _marker_probe(container_name: str) -> subprocess.CompletedProcess[str]:
    return _run_optional(
        [
            "docker",
            "exec",
            container_name,
            "sh",
            "-lc",
            (
                "python - <<'PY'\n"
                "import importlib.metadata as m\n"
                "print(m.version('marker-pdf'))\n"
                "PY"
            ),
        ]
    )


def _seed_repo_local_cache_from_container(
    container_name: str,
    *,
    host_cache_dir: Path,
    notes: list[str],
) -> None:
    host_cache_dir.mkdir(parents=True, exist_ok=True)
    if any(host_cache_dir.iterdir()):
        return
    copy_proc = _run_optional(
        ["docker", "cp", f"{container_name}:/root/.cache/datalab/.", str(host_cache_dir)]
    )
    if copy_proc.returncode == 0:
        notes.append(f"seeded repo-local model cache from {container_name!r}")
        return
    stderr = copy_proc.stderr.strip() or copy_proc.stdout.strip()
    notes.append(
        f"repo-local model cache seed from {container_name!r} unavailable: {stderr or 'no datalab cache present'}"
    )


def _start_repo_local_container(
    container_name: str,
    *,
    image: str,
    pip_cache_dir: Path,
    datalab_cache_dir: Path,
    tmp_dir: Path,
) -> None:
    _run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            container_name,
            "--workdir",
            "/work",
            "--mount",
            f"type=bind,src={REPO_ROOT.resolve()},dst=/work",
            "--mount",
            f"type=bind,src={pip_cache_dir.resolve()},dst=/root/.cache/pip",
            "--mount",
            f"type=bind,src={datalab_cache_dir.resolve()},dst=/root/.cache/datalab",
            "--mount",
            f"type=bind,src={tmp_dir.resolve()},dst=/tmp",
            image,
            "sleep",
            "infinity",
        ]
    )


def _provision_repo_local_runtime(
    container_name: str,
    *,
    base_image: str,
    bootstrap_image: str,
    pip_cache_dir: Path,
    datalab_cache_dir: Path,
    tmp_dir: Path,
    notes: list[str],
) -> dict[str, Any]:
    pip_cache_dir.mkdir(parents=True, exist_ok=True)
    datalab_cache_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    if _docker_image_exists(base_image):
        notes.append(f"reused local base image {base_image!r}")
    else:
        _run(["docker", "pull", base_image])
    _start_repo_local_container(
        container_name,
        image=base_image,
        pip_cache_dir=pip_cache_dir,
        datalab_cache_dir=datalab_cache_dir,
        tmp_dir=tmp_dir,
    )
    install_proc = _run_optional(
        [
            "docker",
            "exec",
            container_name,
            "sh",
            "-lc",
            (
                "python -m pip install --disable-pip-version-check --root-user-action ignore "
                "--upgrade pip==26.0.1 && "
                "python -m pip install --disable-pip-version-check --root-user-action ignore "
                "--extra-index-url https://download.pytorch.org/whl/cpu "
                "'marker-pdf==1.10.2'"
            ),
        ]
    )
    if install_proc.returncode != 0:
        raise RuntimeError(
            "Fresh Marker runtime provisioning failed: "
            f"{install_proc.stderr.strip() or install_proc.stdout.strip()}"
        )
    commit_proc = _run_optional(["docker", "commit", container_name, bootstrap_image])
    if commit_proc.returncode == 0:
        notes.append(f"committed repo-local runtime snapshot to {bootstrap_image!r}")
    else:
        notes.append(
            "repo-local runtime snapshot commit skipped: "
            f"{commit_proc.stderr.strip() or commit_proc.stdout.strip()}"
        )
    return {
        "container_name": container_name,
        "action": "provisioned_from_base_image",
        "seed_container": None,
        "seed_image": base_image,
        "cached_image": bootstrap_image,
        "work_mount_source": str(REPO_ROOT.resolve()),
        "pip_cache_dir": str(pip_cache_dir.resolve()),
        "datalab_cache_dir": str(datalab_cache_dir.resolve()),
        "tmp_dir": str(tmp_dir.resolve()),
        "notes": notes,
    }


def ensure_runtime_container(
    container_name: str = DEFAULT_CONTAINER,
    *,
    bootstrap_from_container: str = DEFAULT_BOOTSTRAP_FROM_CONTAINER,
    bootstrap_image: str = DEFAULT_BOOTSTRAP_IMAGE,
    pip_cache_dir: Path = DEFAULT_PIP_CACHE_DIR,
    datalab_cache_dir: Path = DEFAULT_DATALAB_CACHE_DIR,
    tmp_dir: Path = DEFAULT_TMP_DIR,
    base_image: str = DEFAULT_BASE_IMAGE,
    allow_bootstrap: bool = True,
) -> dict[str, Any]:
    target_info = _docker_inspect(container_name)
    bootstrap_notes: list[str] = []

    if target_info and not target_info.get("State", {}).get("Running"):
        _run(["docker", "start", container_name])
        target_info = _docker_inspect(container_name)
        bootstrap_notes.append("started existing target container")

    if target_info:
        mount_source = _work_mount_source(target_info)
        probe = _marker_probe(container_name)
        if (
            _container_mounts_match(
                target_info,
                datalab_cache_dir=datalab_cache_dir,
                tmp_dir=tmp_dir,
            )
            and probe.returncode == 0
        ):
            return {
                "container_name": container_name,
                "action": "reused_existing_container",
                "seed_container": None,
                "seed_image": target_info.get("Config", {}).get("Image"),
                "work_mount_source": None if mount_source is None else str(mount_source),
                "pip_cache_dir": str(pip_cache_dir.resolve()),
                "datalab_cache_dir": str(datalab_cache_dir.resolve()),
                "tmp_dir": str(tmp_dir.resolve()),
                "notes": bootstrap_notes,
            }
        bootstrap_notes.append("target container was present but not usable from this worktree")

    if not allow_bootstrap:
        raise RuntimeError(
            f"Container {container_name!r} is not usable from {REPO_ROOT} and --no-bootstrap was set."
        )

    if target_info:
        _seed_repo_local_cache_from_container(
            container_name,
            host_cache_dir=datalab_cache_dir,
            notes=bootstrap_notes,
        )

    seed_name = bootstrap_from_container
    if container_name == seed_name:
        seed_name = f"{bootstrap_from_container}-seed"
        bootstrap_notes.append(
            f"seed container name matched the target; using {seed_name!r} as the rebuilt target instead"
        )
        container_name = seed_name

    seed_info = _docker_inspect(bootstrap_from_container)
    if _docker_inspect(container_name):
        _run(["docker", "rm", "-f", container_name])
        bootstrap_notes.append("removed stale target container before rebuild")

    pip_cache_dir.mkdir(parents=True, exist_ok=True)
    datalab_cache_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    cached_bootstrap_image = _discover_cached_bootstrap_image(bootstrap_image)
    if cached_bootstrap_image:
        _start_repo_local_container(
            container_name,
            image=cached_bootstrap_image,
            pip_cache_dir=pip_cache_dir,
            datalab_cache_dir=datalab_cache_dir,
            tmp_dir=tmp_dir,
        )
        rebuilt_info = _docker_inspect(container_name)
        if rebuilt_info and not _container_mounts_match(
            rebuilt_info,
            datalab_cache_dir=datalab_cache_dir,
            tmp_dir=tmp_dir,
        ):
            _run(["docker", "rm", "-f", container_name])
            bootstrap_notes.append(
                f"cached image {cached_bootstrap_image!r} preserved stale bind mounts; falling back to fresh provisioning"
            )
        else:
            probe = _marker_probe(container_name)
            if probe.returncode != 0:
                raise RuntimeError(
                    "Rebuilt Marker runtime from cached image failed probe for "
                    f"{container_name!r}: {probe.stderr.strip() or probe.stdout.strip()}"
                )
            if cached_bootstrap_image != bootstrap_image:
                bootstrap_notes.append(
                    f"preferred cached image {bootstrap_image!r} was unavailable; reused {cached_bootstrap_image!r}"
                )
            else:
                bootstrap_notes.append(
                    f"recreated target container from cached image {cached_bootstrap_image!r}"
                )
            rebuilt_work_mount = _work_mount_source(rebuilt_info) if rebuilt_info else None
            return {
                "container_name": container_name,
                "action": "rebuilt_from_cached_image",
                "seed_container": None,
                "seed_image": cached_bootstrap_image,
                "cached_image": cached_bootstrap_image,
                "work_mount_source": None if rebuilt_work_mount is None else str(rebuilt_work_mount),
                "pip_cache_dir": str(pip_cache_dir.resolve()),
                "datalab_cache_dir": str(datalab_cache_dir.resolve()),
                "tmp_dir": str(tmp_dir.resolve()),
                "notes": bootstrap_notes,
            }

    if seed_info is None:
        return _provision_repo_local_runtime(
            container_name,
            base_image=base_image,
            bootstrap_image=bootstrap_image,
            pip_cache_dir=pip_cache_dir,
            datalab_cache_dir=datalab_cache_dir,
            tmp_dir=tmp_dir,
            notes=bootstrap_notes,
        )

    _seed_repo_local_cache_from_container(
        bootstrap_from_container,
        host_cache_dir=datalab_cache_dir,
        notes=bootstrap_notes,
    )
    bootstrap_notes.append(
        f"seed container {bootstrap_from_container!r} was used only for cache seeding; provisioning a clean repo-local runtime instead of reusing its bind metadata"
    )
    return _provision_repo_local_runtime(
        container_name,
        base_image=base_image,
        bootstrap_image=bootstrap_image,
        pip_cache_dir=pip_cache_dir,
        datalab_cache_dir=datalab_cache_dir,
        tmp_dir=tmp_dir,
        notes=bootstrap_notes,
    )


def _stem(path: Path) -> str:
    return path.stem


def _output_ext(output_format: str) -> str:
    return {"markdown": "md", "json": "json", "html": "html"}[output_format]


def _lite_api_script(*, input_pdf: str, output_dir: str, output_format: str) -> str:
    renderer_map = {
        "markdown": "MarkdownRenderer",
        "json": "JSONRenderer",
        "html": "HTMLRenderer",
    }
    renderer_cls = renderer_map[output_format]
    return f"""
from surya.foundation import FoundationPredictor
from surya.layout import LayoutPredictor
from surya.detection import DetectionPredictor
from surya.ocr_error import OCRErrorPredictor
from surya.settings import settings as surya_settings
from marker.builders.document import DocumentBuilder
from marker.builders.layout import LayoutBuilder
from marker.builders.line import LineBuilder
from marker.builders.structure import StructureBuilder
from marker.providers.registry import provider_from_filepath
from marker.converters import BaseConverter
from marker.output import save_output
from marker.renderers.markdown import MarkdownRenderer
from marker.renderers.json import JSONRenderer
from marker.renderers.html import HTMLRenderer
import os

class LiteBornDigitalConverter(BaseConverter):
    def __init__(self, artifact_dict, processor_list, renderer, config=None):
        super().__init__(config)
        self.artifact_dict = artifact_dict
        self.processor_list = self.initialize_processors(processor_list)
        self.renderer = renderer
        self.page_count = None

    def build_document(self, filepath):
        provider_cls = provider_from_filepath(filepath)
        provider = provider_cls(filepath, self.config)
        layout_builder = self.resolve_dependencies(LayoutBuilder)
        line_builder = self.resolve_dependencies(LineBuilder)
        document_builder = DocumentBuilder(self.config)
        document_builder.disable_ocr = True
        document = document_builder(provider, layout_builder, line_builder, None)
        structure_builder = self.resolve_dependencies(StructureBuilder)
        structure_builder(document)
        for processor in self.processor_list:
            processor(document)
        return document

    def __call__(self, filepath):
        document = self.build_document(filepath)
        self.page_count = len(document.pages)
        renderer = self.resolve_dependencies(self.renderer)
        return renderer(document)

artifact_dict = {{
    "layout_model": LayoutPredictor(
        FoundationPredictor(checkpoint=surya_settings.LAYOUT_MODEL_CHECKPOINT, device="cpu")
    ),
    "detection_model": DetectionPredictor(device="cpu"),
    "ocr_error_model": OCRErrorPredictor(device="cpu"),
}}

processor_classes = [
    __import__("marker.processors.order", fromlist=["OrderProcessor"]).OrderProcessor,
    __import__("marker.processors.block_relabel", fromlist=["BlockRelabelProcessor"]).BlockRelabelProcessor,
    __import__("marker.processors.line_merge", fromlist=["LineMergeProcessor"]).LineMergeProcessor,
    __import__("marker.processors.blockquote", fromlist=["BlockquoteProcessor"]).BlockquoteProcessor,
    __import__("marker.processors.document_toc", fromlist=["DocumentTOCProcessor"]).DocumentTOCProcessor,
    __import__("marker.processors.ignoretext", fromlist=["IgnoreTextProcessor"]).IgnoreTextProcessor,
    __import__("marker.processors.line_numbers", fromlist=["LineNumbersProcessor"]).LineNumbersProcessor,
    __import__("marker.processors.list", fromlist=["ListProcessor"]).ListProcessor,
    __import__("marker.processors.page_header", fromlist=["PageHeaderProcessor"]).PageHeaderProcessor,
    __import__("marker.processors.sectionheader", fromlist=["SectionHeaderProcessor"]).SectionHeaderProcessor,
    __import__("marker.processors.text", fromlist=["TextProcessor"]).TextProcessor,
    __import__("marker.processors.reference", fromlist=["ReferenceProcessor"]).ReferenceProcessor,
    __import__("marker.processors.blank_page", fromlist=["BlankPageProcessor"]).BlankPageProcessor,
]

converter = LiteBornDigitalConverter(
    artifact_dict=artifact_dict,
    processor_list=processor_classes,
    renderer={renderer_cls},
    config={{
        "disable_ocr": True,
        "extract_images": False,
        "pdftext_workers": 1,
        "output_dir": "{output_dir}",
        "debug_pdf_images": False,
        "debug_layout_images": False,
        "debug_json": False,
    }},
)
rendered = converter("{input_pdf}")
os.makedirs("{output_dir}", exist_ok=True)
save_output(rendered, "{output_dir}", "{Path(input_pdf).stem}")
print("pages", converter.page_count)
print("done")
""".strip()


def run_lite_api(
    *,
    container_name: str,
    input_pdf: Path,
    output_dir: Path,
    output_format: str = "json",
) -> FormatArtifact:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    base = _stem(input_pdf)
    ext = _output_ext(output_format)
    main_output = output_dir / f"{base}.{ext}"
    meta_output = output_dir / f"{base}_meta.json"
    log_output = output_dir / "marker.log"
    session_id = uuid4().hex[:12]
    container_root = f"/tmp/marker-lite-{session_id}"
    container_input_dir = f"{container_root}/input"
    container_output_dir = f"{container_root}/output"
    container_input_pdf = f"{container_input_dir}/{input_pdf.name}"

    mkdir_proc = _run_optional(
        [
            "docker",
            "exec",
            container_name,
            "sh",
            "-lc",
            (
                f"rm -rf {shlex.quote(container_root)} && "
                f"mkdir -p {shlex.quote(container_input_dir)} {shlex.quote(container_output_dir)}"
            ),
        ]
    )
    if mkdir_proc.returncode != 0:
        raise RuntimeError(
            "Marker lite_api could not create container temp directories: "
            f"{mkdir_proc.stderr.strip() or mkdir_proc.stdout.strip()}"
        )

    copy_in_proc = _run_optional(
        ["docker", "cp", str(input_pdf), f"{container_name}:{container_input_pdf}"]
    )
    if copy_in_proc.returncode != 0:
        _run_optional(["docker", "exec", container_name, "rm", "-rf", container_root])
        raise RuntimeError(
            "Marker lite_api could not copy input PDF into the runtime container: "
            f"{copy_in_proc.stderr.strip() or copy_in_proc.stdout.strip()}"
        )

    script = _lite_api_script(
        input_pdf=container_input_pdf,
        output_dir=container_output_dir,
        output_format=output_format,
    )
    proc = subprocess.run(
        ["docker", "exec", "-i", container_name, "python", "-"],
        input=script,
        text=True,
        capture_output=True,
    )
    copy_out_proc: subprocess.CompletedProcess[str] | None = None
    if proc.returncode == 0:
        copy_out_proc = _run_optional(
            ["docker", "cp", f"{container_name}:{container_output_dir}/.", str(output_dir)]
        )
    log_output.write_text(
        "\n".join(
            [
                f"exit_code={proc.returncode}",
                f"container_name={container_name}",
                f"container_root={container_root}",
                f"container_input_pdf={container_input_pdf}",
                f"container_output_dir={container_output_dir}",
                "",
                "=== docker cp input ===",
                copy_in_proc.stdout,
                copy_in_proc.stderr,
                "",
                "=== stdout ===",
                proc.stdout,
                "",
                "=== stderr ===",
                proc.stderr,
                "",
                "=== docker cp output ===",
                "" if copy_out_proc is None else copy_out_proc.stdout,
                "" if copy_out_proc is None else copy_out_proc.stderr,
            ]
        ),
        encoding="utf-8",
    )
    _run_optional(["docker", "exec", container_name, "rm", "-rf", container_root])
    if proc.returncode != 0:
        raise RuntimeError(f"Marker lite_api failed for format={output_format}; see log at {log_output}")
    if copy_out_proc is None or copy_out_proc.returncode != 0:
        raise RuntimeError(
            f"Marker lite_api output copy failed for format={output_format}; see log at {log_output}"
        )
    if not main_output.exists():
        raise FileNotFoundError(f"Expected Marker output missing: {main_output}")
    if not meta_output.exists():
        raise FileNotFoundError(f"Expected Marker metadata missing: {meta_output}")
    return FormatArtifact(
        output_format=output_format,
        output_dir=output_dir,
        main_output=main_output,
        meta_output=meta_output,
        log_output=log_output,
    )


def extract_pdftotext_source(pdf_path: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{pdf_path.stem}.pdftotext.txt"
    _run(["pdftotext", str(pdf_path), str(out_path)])
    return out_path


def runtime_metadata(container_name: str) -> dict[str, Any]:
    inspect_proc = _run(
        [
            "docker",
            "inspect",
            container_name,
            "--format",
            "{{json .Config.Image}}",
        ]
    )
    image = json.loads(inspect_proc.stdout)
    package_proc = _run(
        [
            "docker",
            "exec",
            container_name,
            "sh",
            "-lc",
            (
                "python - <<'PY'\n"
                "import importlib.metadata as m\n"
                "import json\n"
                "payload = {}\n"
                "for name in ('marker-pdf', 'surya-ocr', 'torch'):\n"
                "  dist = m.distribution(name)\n"
                "  payload[name] = {\n"
                "    'version': dist.version,\n"
                "    'license': dist.metadata.get('License', ''),\n"
                "    'summary': dist.metadata.get('Summary', ''),\n"
                "  }\n"
                "print(json.dumps(payload))\n"
                "PY"
            ),
        ]
    )
    cache_proc = _run(
        [
            "docker",
            "exec",
            container_name,
            "sh",
            "-lc",
            (
                "python - <<'PY'\n"
                "from pathlib import Path\n"
                "import json\n"
                "payload = {\n"
                "  'layout_model_bytes': None,\n"
                "  'text_recognition_model_bytes': None,\n"
                "  'tmp_model_files': [],\n"
                "}\n"
                "layout = Path('/root/.cache/datalab/models/layout/2025_09_23/model.safetensors')\n"
                "if layout.exists():\n"
                "  payload['layout_model_bytes'] = layout.stat().st_size\n"
                "text_model = Path('/root/.cache/datalab/models/text_recognition/2025_09_23/model.safetensors')\n"
                "if text_model.exists():\n"
                "  payload['text_recognition_model_bytes'] = text_model.stat().st_size\n"
                "for path in sorted(Path('/tmp').glob('tmp*/model.safetensors')):\n"
                "  payload['tmp_model_files'].append({'path': str(path), 'bytes': path.stat().st_size})\n"
                "print(json.dumps(payload))\n"
                "PY"
            ),
        ]
    )
    return {
        "container_name": container_name,
        "image": image,
        "packages": json.loads(package_proc.stdout),
        "cache_signals": json.loads(cache_proc.stdout),
        "stock_cli_model_factory": {
            "loads_predictors": [
                "layout_model",
                "recognition_model",
                "table_rec_model",
                "detection_model",
                "ocr_error_model",
            ]
        },
    }
