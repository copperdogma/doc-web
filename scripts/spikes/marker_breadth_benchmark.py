#!/usr/bin/env python3
"""
Run the Story 165 Marker breadth benchmark in the proven Docker runtime.

This script deliberately targets a single repo-owned born-digital PDF fixture
and the bounded container runtime proven during Story 165. It can benchmark two
runtime profiles:

- `stock_cli`: the official `marker_single` CLI path
- `lite_api`: a thinner Marker-internals path that skips `OcrBuilder` and the
  table/LLM processors for born-digital PDFs while still using Marker's own
  provider, layout, line, structure, and renderer classes

In both modes, it runs Marker in three output modes (markdown/json/html),
captures logs, and summarizes the result against the source text layer
extracted directly from the PDF.

The script does not try to own Marker installation. It assumes the named
container already exists and has `marker-pdf` installed, because Story 165 is
still deciding whether that runtime/model footprint is acceptable at all.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTAINER = "story165-marker-cpu"
DEFAULT_INPUT_PDF = REPO_ROOT / "testdata" / "tbotb-mini.pdf"
DEFAULT_OUT_ROOT = REPO_ROOT / "output" / "runs" / "story165-marker-benchmark-r1"
DEFAULT_DOCWEB_BASELINE_ROOT = REPO_ROOT / "output" / "runs" / "story165-docweb-baseline-r1"
DEFAULT_FORMATS = ("markdown", "json", "html")
SOURCE_MARKDOWN = REPO_ROOT / "testdata" / "tbotb-mini.md"
DEFAULT_MODE = "stock_cli"


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


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _stem(path: Path) -> str:
    return path.stem


def _output_ext(output_format: str) -> str:
    return {"markdown": "md", "json": "json", "html": "html"}[output_format]


def _container_path(path: Path) -> str:
    rel = path.resolve().relative_to(REPO_ROOT.resolve())
    return f"/work/{rel.as_posix()}"


def _extract_headings() -> list[str]:
    headings: list[str] = []
    for line in _read_text(SOURCE_MARKDOWN).splitlines():
        if line.startswith("## "):
            headings.append(line[3:].strip())
    return headings


def _pdftotext_source(pdf_path: Path, out_dir: Path) -> Path:
    out_path = out_dir / f"{pdf_path.stem}.pdftotext.txt"
    _run(["pdftotext", str(pdf_path), str(out_path)])
    return out_path


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _token_set(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9']+", _normalize_text(text))
        if len(token) >= 3
    }


def _token_coverage(source_text: str, output_text: str) -> float:
    source_tokens = _token_set(source_text)
    if not source_tokens:
        return 0.0
    output_tokens = _token_set(output_text)
    return round(len(source_tokens & output_tokens) / len(source_tokens), 4)


def _extract_text_from_json(value: Any) -> list[str]:
    texts: list[str] = []
    if isinstance(value, str):
        texts.append(value)
    elif isinstance(value, dict):
        for inner in value.values():
            texts.extend(_extract_text_from_json(inner))
    elif isinstance(value, list):
        for inner in value:
            texts.extend(_extract_text_from_json(inner))
    return texts


def _html_to_text(text: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(re.sub(r"\s+", " ", without_tags)).strip()


def _artifact_text(output_format: str, main_output: Path) -> str:
    raw = _read_text(main_output)
    if output_format == "json":
        payload = json.loads(raw)
        return " ".join(_extract_text_from_json(payload))
    if output_format == "html":
        return _html_to_text(raw)
    return raw


def _heading_hits(text: str, headings: list[str]) -> dict[str, bool]:
    lowered = _normalize_text(text)
    return {heading: _normalize_text(heading) in lowered for heading in headings}


def _runtime_metadata(container_name: str) -> dict[str, Any]:
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


def _run_stock_cli(
    *,
    container_name: str,
    input_pdf: Path,
    output_dir: Path,
    output_format: str,
    page_range: str | None,
) -> FormatArtifact:
    output_dir.mkdir(parents=True, exist_ok=True)
    base = _stem(input_pdf)
    ext = _output_ext(output_format)
    main_output = output_dir / f"{base}.{ext}"
    meta_output = output_dir / f"{base}_meta.json"
    log_output = output_dir / "marker.log"
    if main_output.exists():
        main_output.unlink()
    if meta_output.exists():
        meta_output.unlink()
    if log_output.exists():
        log_output.unlink()

    cmd = [
        "docker",
        "exec",
        container_name,
        "sh",
        "-lc",
        " ".join(
            [
                "cd /work &&",
                "marker_single",
                _container_path(input_pdf),
                "--output_dir",
                _container_path(output_dir),
                "--output_format",
                output_format,
                "--disable_ocr",
                "--disable_multiprocessing",
                "--disable_tqdm",
                *(["--page_range", page_range] if page_range else []),
            ]
        ),
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    log_output.write_text(
        "\n".join(
            [
                f"exit_code={proc.returncode}",
                "",
                "=== stdout ===",
                proc.stdout,
                "",
                "=== stderr ===",
                proc.stderr,
            ]
        ),
        encoding="utf-8",
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"Marker failed for format={output_format}; see log at {log_output}"
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


def _run_lite_api(
    *,
    container_name: str,
    input_pdf: Path,
    output_dir: Path,
    output_format: str,
) -> FormatArtifact:
    output_dir.mkdir(parents=True, exist_ok=True)
    base = _stem(input_pdf)
    ext = _output_ext(output_format)
    main_output = output_dir / f"{base}.{ext}"
    meta_output = output_dir / f"{base}_meta.json"
    log_output = output_dir / "marker.log"
    if main_output.exists():
        main_output.unlink()
    if meta_output.exists():
        meta_output.unlink()
    if log_output.exists():
        log_output.unlink()

    script = _lite_api_script(
        input_pdf=_container_path(input_pdf),
        output_dir=_container_path(output_dir),
        output_format=output_format,
    )
    proc = subprocess.run(
        ["docker", "exec", "-i", container_name, "python", "-"],
        input=script,
        text=True,
        capture_output=True,
    )
    log_output.write_text(
        "\n".join(
            [
                f"exit_code={proc.returncode}",
                "",
                "=== stdout ===",
                proc.stdout,
                "",
                "=== stderr ===",
                proc.stderr,
            ]
        ),
        encoding="utf-8",
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"Marker lite-api failed for format={output_format}; see log at {log_output}"
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


def _format_summary(
    *,
    artifact: FormatArtifact,
    headings: list[str],
    source_text: str,
) -> dict[str, Any]:
    text = _artifact_text(artifact.output_format, artifact.main_output)
    meta = json.loads(_read_text(artifact.meta_output))
    hits = _heading_hits(text, headings)
    image_files = [
        path.name
        for path in sorted(artifact.output_dir.iterdir())
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    ]
    return {
        "artifacts": {
            "main_output": str(artifact.main_output),
            "meta_output": str(artifact.meta_output),
            "log_output": str(artifact.log_output),
            "image_files": image_files,
        },
        "signals": {
            "main_output_bytes": artifact.main_output.stat().st_size,
            "meta_output_bytes": artifact.meta_output.stat().st_size,
            "text_chars": len(text),
            "token_coverage_vs_pdftotext": _token_coverage(source_text, text),
            "heading_hits": hits,
            "heading_hit_count": sum(1 for hit in hits.values() if hit),
            "heading_hit_ratio": round(sum(1 for hit in hits.values() if hit) / len(headings), 4),
            "meta_top_level_keys": sorted(meta.keys()) if isinstance(meta, dict) else [],
            "meta_page_like_keys": sorted(
                key for key in (meta.keys() if isinstance(meta, dict) else []) if "page" in key.lower()
            ),
        },
    }


def _docweb_baseline_summary(
    baseline_root: Path,
    *,
    headings: list[str],
    source_text: str,
) -> dict[str, Any] | None:
    pages_dir = baseline_root / "ocr_ensemble" / "pages"
    page_paths = sorted(pages_dir.glob("page-*.json"))
    if not page_paths:
        return None

    page_payloads = [json.loads(_read_text(path)) for path in page_paths]
    combined_text = "\n".join(
        "\n".join(
            line.get("text", "")
            for line in payload.get("lines", [])
            if isinstance(line.get("text"), str) and line.get("text").strip()
        )
        for payload in page_payloads
    )
    hits = _heading_hits(combined_text, headings)
    quality_path = baseline_root / "ocr_ensemble" / "ocr_quality_report.json"
    histogram_path = baseline_root / "ocr_ensemble" / "ocr_source_histogram.json"
    quality_rows = json.loads(_read_text(quality_path)) if quality_path.exists() else []
    histogram = json.loads(_read_text(histogram_path)) if histogram_path.exists() else {}
    escalated_pages = [
        row.get("page")
        for row in quality_rows
        if isinstance(row, dict) and row.get("needs_escalation")
    ]
    line_bbox_count = sum(
        1
        for payload in page_payloads
        for line in payload.get("lines", [])
        if line.get("bbox")
    )
    return {
        "artifacts": {
            "artifact_root": str(baseline_root),
            "pages_dir": str(pages_dir),
            "quality_report": str(quality_path) if quality_path.exists() else None,
            "source_histogram": str(histogram_path) if histogram_path.exists() else None,
        },
        "signals": {
            "page_count": len(page_payloads),
            "line_count": sum(len(payload.get("lines", [])) for payload in page_payloads),
            "token_coverage_vs_pdftotext": _token_coverage(source_text, combined_text),
            "heading_hits": hits,
            "heading_hit_count": sum(1 for hit in hits.values() if hit),
            "heading_hit_ratio": round(
                sum(1 for hit in hits.values() if hit) / len(headings), 4
            ),
            "pages_needing_escalation": escalated_pages,
            "engine_coverage": histogram.get("engine_coverage", {})
            if isinstance(histogram, dict)
            else {},
            "source_histogram": histogram.get("histogram", {})
            if isinstance(histogram, dict)
            else {},
            "has_line_level_bboxes": line_bbox_count > 0,
            "line_bbox_count": line_bbox_count,
            "surface_type": "pagelines_v1",
        },
    }


def _decision(
    format_summaries: dict[str, Any],
    runtime: dict[str, Any],
    mode: str,
    docweb_baseline: dict[str, Any] | None,
) -> dict[str, Any]:
    heading_ratios = [
        details["signals"]["heading_hit_ratio"] for details in format_summaries.values()
    ]
    token_coverages = [
        details["signals"]["token_coverage_vs_pdftotext"]
        for details in format_summaries.values()
    ]
    meta_page_signal = any(
        details["signals"]["meta_page_like_keys"] for details in format_summaries.values()
    )
    tmp_files = runtime["cache_signals"]["tmp_model_files"]
    layout_bytes = runtime["cache_signals"]["layout_model_bytes"] or 0
    text_bytes = runtime["cache_signals"]["text_recognition_model_bytes"] or 0
    weight_bytes = layout_bytes + text_bytes + sum(item["bytes"] for item in tmp_files)
    baseline_signals = (docweb_baseline or {}).get("signals", {})
    baseline_histogram = baseline_signals.get("source_histogram", {})
    baseline_engine_coverage = baseline_signals.get("engine_coverage", {})
    baseline_is_still_ocr_routed = (
        baseline_histogram.get("tesseract") == baseline_signals.get("page_count")
        and baseline_engine_coverage.get("pdftext_text_pct") == 1.0
    )
    adoption_blockers = [
        "GPL-3.0-or-later code license",
        "restricted commercial model-license posture",
        "stock CLI eagerly loads multi-gigabyte model weights",
        "Marker outputs still stop short of doc-web-grade block provenance and stable anchors",
    ]

    if min(heading_ratios, default=0.0) >= 0.9 and min(token_coverages, default=0.0) >= 0.9 and meta_page_signal:
        if baseline_is_still_ocr_routed:
            status = "candidate_for_follow_on_story"
            read = (
                "Marker's thinner internals path preserved born-digital text and document structure "
                "more usefully than the current local baseline, which still routed all pages through "
                "tesseract despite full embedded-text coverage."
            )
            next_step = (
                "Create a follow-on story for a thin Marker-internals born-digital substrate, while "
                "keeping stock Marker CLI adoption off the table."
            )
        else:
            status = "candidate_for_follow_on_story"
            read = (
                "Marker preserved most of the born-digital text and headings while also exposing "
                "page-like metadata, so it earns a closer adoption decision."
            )
            next_step = (
                "Compare against the incumbent OCR-routed baseline and decide whether integration is "
                "worth GPL/model-license tradeoffs."
            )
    else:
        status = "negative_or_incomplete_for_immediate_adoption"
        read = (
            "Marker did not yet clear the combined fidelity/provenance bar cleanly enough to "
            "justify a follow-on adoption story from this lane alone."
        )
        next_step = "Manually inspect the emitted artifacts before widening beyond tbotb-mini.pdf."
    return {
        "mode": mode,
        "status": status,
        "read": read,
        "next_step": next_step,
        "weight_footprint_bytes_observed": weight_bytes,
        "meta_page_signal_present": meta_page_signal,
        "min_heading_hit_ratio": min(heading_ratios, default=0.0),
        "min_token_coverage_vs_pdftotext": min(token_coverages, default=0.0),
        "current_local_baseline_is_still_ocr_routed": baseline_is_still_ocr_routed,
        "adoption_blockers": adoption_blockers,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--container-name", default=DEFAULT_CONTAINER)
    parser.add_argument("--input-pdf", type=Path, default=DEFAULT_INPUT_PDF)
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    parser.add_argument("--docweb-baseline-root", type=Path, default=DEFAULT_DOCWEB_BASELINE_ROOT)
    parser.add_argument(
        "--mode",
        choices=("stock_cli", "lite_api"),
        default=DEFAULT_MODE,
        help="Which Marker runtime profile to benchmark.",
    )
    parser.add_argument("--page-range", default=None)
    parser.add_argument(
        "--formats",
        default=",".join(DEFAULT_FORMATS),
        help="Comma-separated output formats to run. Default: markdown,json,html",
    )
    parser.add_argument(
        "--skip-run",
        action="store_true",
        help="Do not invoke Marker; summarize already-emitted artifacts only.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    formats = tuple(part.strip() for part in args.formats.split(",") if part.strip())
    if not args.input_pdf.exists():
        raise FileNotFoundError(f"Missing benchmark input: {args.input_pdf}")

    out_dir = args.out_root / args.input_pdf.stem / "marker-v1102"
    if not args.skip_run and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    headings = _extract_headings()
    pdftotext_path = _pdftotext_source(args.input_pdf, out_dir)
    source_text = _read_text(pdftotext_path)

    runtime = _runtime_metadata(args.container_name)
    docweb_baseline = _docweb_baseline_summary(
        args.docweb_baseline_root,
        headings=headings,
        source_text=source_text,
    )
    format_summaries: dict[str, Any] = {}
    mode_dir = args.mode.replace("_", "-")
    for output_format in formats:
        ext = _output_ext(output_format)
        fmt_dir = out_dir / mode_dir / output_format
        artifact = FormatArtifact(
            output_format=output_format,
            output_dir=fmt_dir,
            main_output=fmt_dir / f"{args.input_pdf.stem}.{ext}",
            meta_output=fmt_dir / f"{args.input_pdf.stem}_meta.json",
            log_output=fmt_dir / "marker.log",
        )
        if not args.skip_run:
            if args.mode == "stock_cli":
                artifact = _run_stock_cli(
                    container_name=args.container_name,
                    input_pdf=args.input_pdf,
                    output_dir=fmt_dir,
                    output_format=output_format,
                    page_range=args.page_range,
                )
            else:
                artifact = _run_lite_api(
                    container_name=args.container_name,
                    input_pdf=args.input_pdf,
                    output_dir=fmt_dir,
                    output_format=output_format,
                )
        format_summaries[output_format] = _format_summary(
            artifact=artifact,
            headings=headings,
            source_text=source_text,
        )

    summary = {
        "schema_version": "story165_marker_benchmark_v1",
        "story_id": 165,
        "input_artifacts": {
            "input_pdf": str(args.input_pdf),
            "source_markdown": str(SOURCE_MARKDOWN),
            "pdftotext_output": str(pdftotext_path),
            "headings": headings,
            "page_range": args.page_range,
        },
        "mode": args.mode,
        "runtime": runtime,
        "docweb_baseline": docweb_baseline,
        "formats": format_summaries,
        "decision": _decision(format_summaries, runtime, args.mode, docweb_baseline),
    }
    summary_path = out_dir / "summary.json"
    _write_json(summary_path, summary)
    print(json.dumps(summary["decision"], indent=2))
    print(f"Summary written to {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
