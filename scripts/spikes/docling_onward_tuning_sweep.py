#!/usr/bin/env python3
"""
Run a bounded Docling tuning sweep on the pinned Onward hard-case slice.

This script is intentionally repo-local and experiment-oriented. It does not
touch the main pipeline; it produces inspectable Docling artifacts plus compact
run summaries under output/runs/.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import OrderedDict
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path
from typing import Any, Callable

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    OcrMacOptions,
    PdfPipelineOptions,
    TableFormerMode,
    TesseractCliOcrOptions,
    VlmConvertOptions,
    VlmPipelineOptions,
)
from docling.datamodel.vlm_engine_options import MlxVlmEngineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem


DEFAULT_INPUT = Path(
    "output/runs/story157-docling-pilot-r1/input/onward-hardcase-slice-imageonly.pdf"
)
DEFAULT_OUTPUT_ROOT = Path("output/runs/story158-docling-tuning-r1")


@dataclass
class SweepConfig:
    name: str
    description: str
    make_converter: Callable[[], DocumentConverter]
    metadata: dict[str, Any]


def _pdf_converter(
    pipeline_options: PdfPipelineOptions | None = None,
) -> DocumentConverter:
    if pipeline_options is None:
        return DocumentConverter()
    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
        }
    )


def _pdf_options() -> PdfPipelineOptions:
    return PdfPipelineOptions()


def config_baseline_auto() -> SweepConfig:
    return SweepConfig(
        name="baseline-auto",
        description="Story 158 baseline with default PDF pipeline settings.",
        make_converter=lambda: _pdf_converter(None),
        metadata={
            "pipeline": "standard_pdf",
            "pipeline_options": None,
        },
    )


def config_baseline_images() -> SweepConfig:
    options = _pdf_options()
    options.generate_page_images = True
    options.generate_picture_images = True
    options.images_scale = 2.0
    return SweepConfig(
        name="baseline-images",
        description="Baseline PDF pipeline plus picture/page image generation for export inspection.",
        make_converter=lambda: _pdf_converter(options),
        metadata={
            "pipeline": "standard_pdf",
            "pipeline_options": options.model_dump(mode="json", exclude_none=True),
        },
    )


def config_ocrmac_fullpage() -> SweepConfig:
    options = _pdf_options()
    options.ocr_options = OcrMacOptions(force_full_page_ocr=True)
    return SweepConfig(
        name="ocrmac-fullpage",
        description="Use macOS Vision OCR with full-page OCR enabled.",
        make_converter=lambda: _pdf_converter(options),
        metadata={
            "pipeline": "standard_pdf",
            "pipeline_options": options.model_dump(mode="json", exclude_none=True),
        },
    )


def config_tesseract_fullpage() -> SweepConfig:
    options = _pdf_options()
    options.ocr_options = TesseractCliOcrOptions(force_full_page_ocr=True)
    return SweepConfig(
        name="tesseract-fullpage",
        description="Use Tesseract CLI OCR with full-page OCR enabled.",
        make_converter=lambda: _pdf_converter(options),
        metadata={
            "pipeline": "standard_pdf",
            "pipeline_options": options.model_dump(mode="json", exclude_none=True),
        },
    )


def config_table_nocellmatch() -> SweepConfig:
    options = _pdf_options()
    options.table_structure_options.do_cell_matching = False
    options.table_structure_options.mode = TableFormerMode.ACCURATE
    return SweepConfig(
        name="table-nocellmatch",
        description="Disable cell matching so table text comes from structure prediction rather than PDF cell mapping.",
        make_converter=lambda: _pdf_converter(options),
        metadata={
            "pipeline": "standard_pdf",
            "pipeline_options": options.model_dump(mode="json", exclude_none=True),
        },
    )


def config_combo_ocrmac_nocellmatch_images() -> SweepConfig:
    options = _pdf_options()
    options.ocr_options = OcrMacOptions(force_full_page_ocr=True)
    options.table_structure_options.do_cell_matching = False
    options.table_structure_options.mode = TableFormerMode.ACCURATE
    options.generate_page_images = True
    options.generate_picture_images = True
    options.images_scale = 2.0
    return SweepConfig(
        name="combo-ocrmac-nocellmatch-images",
        description="Best realistic stock combo: macOS full-page OCR, no cell matching, and image-preserving export.",
        make_converter=lambda: _pdf_converter(options),
        metadata={
            "pipeline": "standard_pdf",
            "pipeline_options": options.model_dump(mode="json", exclude_none=True),
        },
    )


def config_vlm_granite() -> SweepConfig:
    vlm_options = VlmConvertOptions.from_preset(
        "granite_docling",
        engine_options=MlxVlmEngineOptions(),
    )
    options = VlmPipelineOptions(vlm_options=vlm_options)
    return SweepConfig(
        name="vlm-granite",
        description="Granite Docling VLM pipeline using MLX runtime when available.",
        make_converter=lambda: DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_cls=VlmPipeline,
                    pipeline_options=options,
                ),
            }
        ),
        metadata={
            "pipeline": "vlm_granite",
            "pipeline_options": options.model_dump(mode="json", exclude_none=True),
        },
    )


CONFIGS: "OrderedDict[str, Callable[[], SweepConfig]]" = OrderedDict(
    [
        ("baseline-auto", config_baseline_auto),
        ("baseline-images", config_baseline_images),
        ("ocrmac-fullpage", config_ocrmac_fullpage),
        ("tesseract-fullpage", config_tesseract_fullpage),
        ("table-nocellmatch", config_table_nocellmatch),
        ("combo-ocrmac-nocellmatch-images", config_combo_ocrmac_nocellmatch_images),
        ("vlm-granite", config_vlm_granite),
    ]
)


def _save_page_and_element_images(conv_res: Any, image_dir: Path) -> dict[str, int]:
    image_dir.mkdir(parents=True, exist_ok=True)
    page_count = 0
    picture_count = 0
    table_count = 0

    for page_no, page in conv_res.document.pages.items():
        page_image = getattr(page, "image", None)
        pil_image = getattr(page_image, "pil_image", None)
        if pil_image is None:
            continue
        with (image_dir / f"page-{page_no:03d}.png").open("wb") as fp:
            pil_image.save(fp, format="PNG")
        page_count += 1

    for element, _level in conv_res.document.iterate_items():
        if isinstance(element, PictureItem):
            image = element.get_image(conv_res.document)
            if image is not None:
                picture_count += 1
                with (image_dir / f"picture-{picture_count:03d}.png").open("wb") as fp:
                    image.save(fp, format="PNG")
        if isinstance(element, TableItem):
            image = element.get_image(conv_res.document)
            if image is not None:
                table_count += 1
                with (image_dir / f"table-{table_count:03d}.png").open("wb") as fp:
                    image.save(fp, format="PNG")

    return {
        "page_images": page_count,
        "picture_images": picture_count,
        "table_images": table_count,
    }


def _summarize_document(doc_json_path: Path, html_path: Path, md_path: Path) -> dict[str, Any]:
    doc = json.loads(doc_json_path.read_text())
    html = html_path.read_text() if html_path.exists() else ""
    md = md_path.read_text() if md_path.exists() else ""
    first_text = next((t for t in doc.get("texts", []) if t.get("text")), None)
    first_table = doc.get("tables", [{}])[0] if doc.get("tables") else None
    first_table_cell = None
    first_table_page = None
    if first_table:
        first_table_page = (first_table.get("prov") or [{}])[0].get("page_no")
        for cell in first_table.get("data", {}).get("table_cells", []):
            if cell.get("text"):
                first_table_cell = cell["text"]
                break

    return {
        "document_name": doc.get("name"),
        "origin": doc.get("origin"),
        "counts": {
            "pages": len(doc.get("pages", [])),
            "texts": len(doc.get("texts", [])),
            "tables": len(doc.get("tables", [])),
            "pictures": len(doc.get("pictures", [])),
        },
        "export_counts": {
            "html_img_tags": html.count("<img"),
            "html_id_attrs": html.count(" id="),
            "markdown_image_placeholders": md.count("<!-- image -->"),
        },
        "first_text": {
            "self_ref": first_text.get("self_ref") if first_text else None,
            "label": first_text.get("label") if first_text else None,
            "page_no": ((first_text.get("prov") or [{}])[0].get("page_no") if first_text else None),
            "text": (first_text.get("text", "")[:300] if first_text else None),
        },
        "first_table": {
            "page_no": first_table_page,
            "first_cell": first_table_cell,
        },
    }


def run_one(config: SweepConfig, input_pdf: Path, output_root: Path) -> dict[str, Any]:
    out_dir = output_root / config.name
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = input_pdf.stem

    converter = config.make_converter()
    started_at = time.time()
    try:
        conv_res = converter.convert(source=input_pdf)
        elapsed = time.time() - started_at

        json_path = out_dir / f"{stem}.json"
        html_path = out_dir / f"{stem}.html"
        md_path = out_dir / f"{stem}.md"

        conv_res.document.save_as_json(json_path)
        conv_res.document.save_as_markdown(md_path, image_mode=ImageRefMode.REFERENCED)
        conv_res.document.save_as_html(html_path, image_mode=ImageRefMode.REFERENCED)
        image_counts = _save_page_and_element_images(conv_res, out_dir / "images")

        summary = {
            "status": "success",
            "config_name": config.name,
            "description": config.description,
            "elapsed_seconds": round(elapsed, 3),
            "docling_version": version("docling"),
            "docling_parse_version": version("docling-parse"),
            "input_pdf": str(input_pdf),
            "output_dir": str(out_dir),
            "config": config.metadata,
            "image_counts": image_counts,
            **_summarize_document(json_path, html_path, md_path),
        }
    except Exception as exc:  # pragma: no cover - experiment harness
        elapsed = time.time() - started_at
        summary = {
            "status": "error",
            "config_name": config.name,
            "description": config.description,
            "elapsed_seconds": round(elapsed, 3),
            "docling_version": version("docling"),
            "docling_parse_version": version("docling-parse"),
            "input_pdf": str(input_pdf),
            "output_dir": str(out_dir),
            "config": config.metadata,
            "error": {
                "type": type(exc).__name__,
                "message": str(exc),
            },
        }

    (out_dir / "conversion_summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-pdf",
        default=str(DEFAULT_INPUT),
        help="Path to the pinned Onward hard-case PDF slice.",
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Output directory for sweep artifacts.",
    )
    parser.add_argument(
        "--configs",
        default="baseline-auto,baseline-images,ocrmac-fullpage,tesseract-fullpage,table-nocellmatch,combo-ocrmac-nocellmatch-images",
        help="Comma-separated config names or 'all'.",
    )
    parser.add_argument(
        "--allow-vlm",
        action="store_true",
        help="Allow running VLM configs when explicitly named or when using --configs all.",
    )
    return parser.parse_args()


def resolve_configs(configs_arg: str, allow_vlm: bool) -> list[SweepConfig]:
    if configs_arg == "all":
        names = list(CONFIGS)
    else:
        names = [name.strip() for name in configs_arg.split(",") if name.strip()]

    resolved: list[SweepConfig] = []
    for name in names:
        if name not in CONFIGS:
            raise SystemExit(f"Unknown config: {name}")
        if name.startswith("vlm-") and not allow_vlm:
            raise SystemExit(
                f"Config {name} requires --allow-vlm because model downloads/runtime cost may be significant."
            )
        resolved.append(CONFIGS[name]())
    return resolved


def main() -> int:
    args = parse_args()
    input_pdf = Path(args.input_pdf)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    if not input_pdf.exists():
        raise SystemExit(f"Input PDF not found: {input_pdf}")

    configs = resolve_configs(args.configs, args.allow_vlm)
    results = []
    for config in configs:
        print(f"[docling-sweep] running {config.name}", file=sys.stderr)
        results.append(run_one(config, input_pdf, output_root / "docling"))

    session_summary = {
        "schema_version": "docling_onward_tuning_sweep_v1",
        "input_pdf": str(input_pdf),
        "output_root": str(output_root / "docling"),
        "results": results,
    }
    (output_root / "summary.json").write_text(json.dumps(session_summary, indent=2))

    lines = [
        "# Docling Onward Tuning Sweep",
        "",
        f"- Input: `{input_pdf}`",
        f"- Output root: `{output_root / 'docling'}`",
        "",
        "| Config | Status | Seconds | Pages | Texts | Tables | Pictures | HTML `<img>` | HTML `id=` | MD image placeholders |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for result in results:
        counts = result.get("counts", {})
        export = result.get("export_counts", {})
        lines.append(
            "| {config} | {status} | {secs} | {pages} | {texts} | {tables} | {pictures} | {imgs} | {ids} | {mdimgs} |".format(
                config=result["config_name"],
                status=result["status"],
                secs=result.get("elapsed_seconds", ""),
                pages=counts.get("pages", ""),
                texts=counts.get("texts", ""),
                tables=counts.get("tables", ""),
                pictures=counts.get("pictures", ""),
                imgs=export.get("html_img_tags", ""),
                ids=export.get("html_id_attrs", ""),
                mdimgs=export.get("markdown_image_placeholders", ""),
            )
        )
    (output_root / "summary.md").write_text("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
