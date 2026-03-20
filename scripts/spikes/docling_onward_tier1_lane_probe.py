#!/usr/bin/env python3
"""
Run a bounded Tier 1 Docling probe on the Arthur hard-case lane using source images.

This script exists to close the remaining official-only question on the Arthur
lane before dropping to deeper repo-owned repair work. It only exercises
Docling surfaces that are both official and locally real in the current
runtime.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import time
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    OcrMacOptions,
    PdfPipelineOptions,
    VlmConvertOptions,
    VlmPipelineOptions,
)
from docling.datamodel.vlm_engine_options import TransformersVlmEngineOptions
from docling.document_converter import DocumentConverter, ImageFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline
from docling_core.types.doc import ImageRefMode


DEFAULT_IMAGES = [
    Path("/Users/cam/Documents/Projects/Onward to the Unknown Book Scan/Processed Pages/Image030.jpg"),
    Path("/Users/cam/Documents/Projects/Onward to the Unknown Book Scan/Processed Pages/Image031.jpg"),
]
DEFAULT_OUTPUT_ROOT = Path("output/runs/story158-docling-tier1-lane-r1")


@dataclass
class ProbeConfig:
    name: str
    description: str
    make_converter: Callable[[], DocumentConverter]
    metadata: dict[str, Any]


def _default_image_converter() -> DocumentConverter:
    return DocumentConverter(
        format_options={
            InputFormat.IMAGE: ImageFormatOption(),
        }
    )


def _ocrmac_image_converter() -> DocumentConverter:
    options = PdfPipelineOptions()
    options.ocr_options = OcrMacOptions(force_full_page_ocr=True)
    return DocumentConverter(
        format_options={
            InputFormat.IMAGE: ImageFormatOption(pipeline_options=options),
        }
    )


def _smoldocling_image_converter() -> DocumentConverter:
    vlm_options = VlmConvertOptions.from_preset(
        "smoldocling",
        engine_options=TransformersVlmEngineOptions(
            load_in_8bit=False,
            compile_model=False,
        ),
    )
    pipeline_options = VlmPipelineOptions(vlm_options=vlm_options)
    return DocumentConverter(
        format_options={
            InputFormat.IMAGE: ImageFormatOption(
                pipeline_cls=VlmPipeline,
                pipeline_options=pipeline_options,
            ),
        }
    )


CONFIGS: "OrderedDict[str, ProbeConfig]" = OrderedDict(
    [
        (
            "image-default",
            ProbeConfig(
                name="image-default",
                description="Direct source-image input with the default official image pipeline.",
                make_converter=_default_image_converter,
                metadata={"pipeline": "standard_image"},
            ),
        ),
        (
            "image-ocrmac",
            ProbeConfig(
                name="image-ocrmac",
                description="Direct source-image input plus OcrMac full-page OCR.",
                make_converter=_ocrmac_image_converter,
                metadata={
                    "pipeline": "standard_image",
                    "ocr_options": OcrMacOptions(force_full_page_ocr=True).model_dump(
                        mode="json", exclude_none=True
                    ),
                },
            ),
        ),
        (
            "image-smoldocling-transformers",
            ProbeConfig(
                name="image-smoldocling-transformers",
                description="Direct source-image input through the official SmolDocling Transformers VLM preset.",
                make_converter=_smoldocling_image_converter,
                metadata={
                    "pipeline": "vlm_image",
                    "preset_id": "smoldocling",
                    "engine": "transformers",
                },
            ),
        ),
    ]
)


def _strip_body(html: str) -> str:
    match = re.search(r"<body[^>]*>(.*)</body>", html, flags=re.IGNORECASE | re.DOTALL)
    if match is not None:
        return match.group(1).strip()
    return html.strip()


def _optional_backend_presence() -> dict[str, bool]:
    return {
        "rapidocr_onnxruntime": importlib.util.find_spec("rapidocr_onnxruntime") is not None,
        "easyocr": importlib.util.find_spec("easyocr") is not None,
        "torch": importlib.util.find_spec("torch") is not None,
        "transformers": importlib.util.find_spec("transformers") is not None,
    }


def _write_summary_markdown(summary: dict[str, Any], output_root: Path) -> None:
    lines = [
        "# Docling Tier 1 Arthur-Lane Image Probes",
        "",
        "This pass uses direct source-image input on the Arthur hard-case lane.",
        "It is intended to close the remaining official-only question before",
        "accepting deeper ownership tiers.",
        "",
        "## Optional Backend Presence",
    ]
    for name, present in summary["optional_backend_presence"].items():
        lines.append(f"- `{name}`: `{present}`")
    lines.extend(
        [
            "",
            "## Results",
        ]
    )
    for candidate in summary["candidates"]:
        lines.extend(
            [
                f"### `{candidate['config']}`",
                f"- description: {candidate['description']}",
                f"- seconds: `{candidate.get('seconds')}`",
                f"- status: `{candidate.get('status', 'error')}`",
            ]
        )
        if "error_type" in candidate:
            lines.append(
                f"- error: `{candidate['error_type']}` — `{candidate['error']}`"
            )
        else:
            lines.append(f"- merged html: `{candidate['artifacts']['merged_html']}`")
            lines.append(f"- merged markdown: `{candidate['artifacts']['merged_markdown']}`")
            for page in candidate["pages"]:
                lines.append(
                    "- "
                    f"`{page['source_image']}`: status `{page['status']}`, "
                    f"tables `{page['tables']}`, texts `{page['texts']}`, "
                    f"first table cell `{page['first_table_cell']}`"
                )
        lines.append("")
    (output_root / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def _run_probe(config: ProbeConfig, images: list[Path], output_root: Path) -> dict[str, Any]:
    outdir = output_root / config.name
    outdir.mkdir(parents=True, exist_ok=True)

    payload: dict[str, Any] = {
        "config": config.name,
        "description": config.description,
        "images": [str(path) for path in images],
        "metadata": config.metadata,
    }
    converter = config.make_converter()
    started = time.time()

    page_records: list[dict[str, Any]] = []
    body_fragments: list[str] = []
    markdown_fragments: list[str] = []

    try:
        for image_path in images:
            result = converter.convert(image_path)
            html = result.document.export_to_html(image_mode=ImageRefMode.REFERENCED)
            markdown = result.document.export_to_markdown(image_mode=ImageRefMode.REFERENCED)
            doc_json = result.document.model_dump_json(indent=2)

            stem = image_path.stem.lower()
            html_path = outdir / f"{stem}.html"
            md_path = outdir / f"{stem}.md"
            json_path = outdir / f"{stem}.json"
            html_path.write_text(html, encoding="utf-8")
            md_path.write_text(markdown, encoding="utf-8")
            json_path.write_text(doc_json, encoding="utf-8")

            first_table_cell = None
            if result.document.tables:
                for cell in result.document.tables[0].data.table_cells:
                    text = getattr(cell, "text", None)
                    if text:
                        first_table_cell = text
                        break

            page_records.append(
                {
                    "source_image": str(image_path),
                    "status": str(result.status),
                    "texts": len(result.document.texts),
                    "tables": len(result.document.tables),
                    "pictures": len(result.document.pictures),
                    "first_table_cell": first_table_cell,
                    "artifacts": {
                        "html": str(html_path),
                        "markdown": str(md_path),
                        "json": str(json_path),
                    },
                }
            )
            body_fragments.append(
                "\n".join(
                    [
                        f'<section data-source-image="{image_path.name}">',
                        _strip_body(html),
                        "</section>",
                    ]
                )
            )
            markdown_fragments.append(f"<!-- {image_path.name} -->\n{markdown.strip()}\n")

        merged_html_path = outdir / "merged.html"
        merged_md_path = outdir / "merged.md"
        merged_html_path.write_text(
            "<html><body>\n" + "\n".join(body_fragments) + "\n</body></html>\n",
            encoding="utf-8",
        )
        merged_md_path.write_text("\n".join(markdown_fragments), encoding="utf-8")

        payload.update(
            {
                "seconds": round(time.time() - started, 3),
                "status": "success",
                "pages": page_records,
                "artifacts": {
                    "merged_html": str(merged_html_path),
                    "merged_markdown": str(merged_md_path),
                },
            }
        )
    except Exception as exc:
        payload.update(
            {
                "seconds": round(time.time() - started, 3),
                "error_type": type(exc).__name__,
                "error": str(exc),
                "pages": page_records,
            }
        )

    (outdir / "meta.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a bounded Tier 1 Docling Arthur-lane image probe.")
    parser.add_argument(
        "--image",
        action="append",
        help="Explicit image path(s) to use. Defaults to Image030.jpg and Image031.jpg.",
    )
    parser.add_argument("--outdir", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument(
        "--config",
        action="append",
        choices=list(CONFIGS.keys()),
        help="Specific config(s) to run. Defaults to all.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    images = [Path(path) for path in args.image] if args.image else list(DEFAULT_IMAGES)
    output_root = Path(args.outdir)
    output_root.mkdir(parents=True, exist_ok=True)
    selected = args.config or list(CONFIGS.keys())

    summary = {
        "schema_version": "story158_docling_tier1_lane_probe_v1",
        "optional_backend_presence": _optional_backend_presence(),
        "candidates": [],
    }
    for name in selected:
        summary["candidates"].append(_run_probe(CONFIGS[name], images, output_root))

    (output_root / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    _write_summary_markdown(summary, output_root)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
