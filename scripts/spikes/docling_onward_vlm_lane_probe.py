#!/usr/bin/env python3
"""
Run narrow official Docling VLM probes on the Arthur hard-case lane.

This script intentionally targets a small page range so we can evaluate whether
official Docling VLM presets can improve the measured Arthur-lane parity gap
without widening back out to the full 40-page hard-case sweep.
"""

from __future__ import annotations

import argparse
import json
import time
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import VlmConvertOptions, VlmPipelineOptions
from docling.datamodel.vlm_engine_options import TransformersVlmEngineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline
from docling_core.types.doc import ImageRefMode


DEFAULT_SOURCE = Path(
    "output/runs/story157-docling-pilot-r1/input/onward-hardcase-slice-imageonly.pdf"
)
DEFAULT_OUTPUT_ROOT = Path("output/runs/story158-docling-vlm-lane-r1")


@dataclass
class ProbeConfig:
    name: str
    preset_id: str
    description: str
    make_engine: Callable[[], TransformersVlmEngineOptions]


def _default_engine() -> TransformersVlmEngineOptions:
    return TransformersVlmEngineOptions(
        load_in_8bit=False,
        compile_model=False,
    )


CONFIGS: "OrderedDict[str, ProbeConfig]" = OrderedDict(
    [
        (
            "smoldocling-transformers",
            ProbeConfig(
                name="smoldocling-transformers",
                preset_id="smoldocling",
                description="Small official Docling VLM preset on Transformers.",
                make_engine=_default_engine,
            ),
        ),
        (
            "granite-vision-transformers",
            ProbeConfig(
                name="granite-vision-transformers",
                preset_id="granite_vision",
                description="Stronger Granite Vision preset on Transformers.",
                make_engine=_default_engine,
            ),
        ),
    ]
)


def _run_probe(
    *,
    config: ProbeConfig,
    source: Path,
    page_range: tuple[int, int],
    output_root: Path,
) -> dict[str, Any]:
    outdir = output_root / config.name
    outdir.mkdir(parents=True, exist_ok=True)

    engine = config.make_engine()
    vlm_options = VlmConvertOptions.from_preset(
        config.preset_id,
        engine_options=engine,
    )
    pipeline_options = VlmPipelineOptions(vlm_options=vlm_options)
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=VlmPipeline,
                pipeline_options=pipeline_options,
            )
        }
    )

    started = time.time()
    payload: dict[str, Any] = {
        "config": config.name,
        "preset_id": config.preset_id,
        "description": config.description,
        "source": str(source),
        "page_range": list(page_range),
        "engine_options": engine.model_dump(mode="json", exclude_none=True),
        "output_root": str(outdir),
    }
    try:
        result = converter.convert(source, page_range=page_range)
        elapsed = time.time() - started
        html = result.document.export_to_html(image_mode=ImageRefMode.REFERENCED)
        markdown = result.document.export_to_markdown(image_mode=ImageRefMode.REFERENCED)
        doc_json = result.document.model_dump_json(indent=2)
        (outdir / "page-range.html").write_text(html, encoding="utf-8")
        (outdir / "page-range.md").write_text(markdown, encoding="utf-8")
        (outdir / "page-range.json").write_text(doc_json, encoding="utf-8")
        payload.update(
            {
                "seconds": elapsed,
                "status": str(result.status),
                "errors": [getattr(error, "error_message", str(error)) for error in result.errors],
                "artifacts": {
                    "html": str(outdir / "page-range.html"),
                    "markdown": str(outdir / "page-range.md"),
                    "json": str(outdir / "page-range.json"),
                },
            }
        )
    except Exception as exc:
        elapsed = time.time() - started
        payload.update(
            {
                "seconds": elapsed,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        )

    (outdir / "meta.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run narrow official Docling VLM Arthur-lane probes.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--outdir", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--page-start", type=int, default=3)
    parser.add_argument("--page-end", type=int, default=4)
    parser.add_argument(
        "--config",
        action="append",
        choices=list(CONFIGS.keys()),
        help="Specific config(s) to run. Defaults to all.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    source = Path(args.source)
    output_root = Path(args.outdir)
    output_root.mkdir(parents=True, exist_ok=True)
    selected = args.config or list(CONFIGS.keys())
    page_range = (args.page_start, args.page_end)

    summary: list[dict[str, Any]] = []
    for name in selected:
        summary.append(
            _run_probe(
                config=CONFIGS[name],
                source=source,
                page_range=page_range,
                output_root=output_root,
            )
        )

    (output_root / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
