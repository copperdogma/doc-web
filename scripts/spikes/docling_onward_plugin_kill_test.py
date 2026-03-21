#!/usr/bin/env python3
"""
Run a narrow Docling plugin kill test on the reviewed Onward failure lanes.

This script must run in the isolated Docling runtime after installing the repo
editable into that environment so the external plugin entrypoint is visible.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.models.factories import get_layout_factory, get_table_structure_factory
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem

from docling_plugins.onward_layout_plugin import build_layout_options
from docling_plugins.onward_table_structure_plugin import build_table_structure_options

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_summarize_html_signals():
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from modules.transform.repair_docling_onward_genealogy_v1.main import (
        summarize_html_signals,
    )

    return summarize_html_signals


@dataclass(frozen=True)
class LaneConfig:
    lane_id: str
    document_title: str
    source_pdf: Path
    baseline_html: Path
    gold_html: Path


LANES: dict[str, LaneConfig] = {
    "leonidas": LaneConfig(
        lane_id="leonidas",
        document_title="Leonidas L'Heureux",
        source_pdf=Path(
            "/Users/cam/Documents/Projects/Onward to the Unknown Book Scan/Split Book/06 LEONIDAS L'HEUREUX.pdf"
        ),
        baseline_html=Path(
            "output/runs/story162-docling-baseline-leonidas-r1/docling/baseline-images/06 LEONIDAS L'HEUREUX.html"
        ),
        gold_html=Path(
            "benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/chapter-011.html"
        ),
    ),
    "marie-louise": LaneConfig(
        lane_id="marie-louise",
        document_title="Marie-Louise (L'Heureux) LaClare",
        source_pdf=Path(
            "/Users/cam/Documents/Projects/Onward to the Unknown Book Scan/Split Book/12 MARIE-LOUISE (L'HEUREUX) LaCLARE.pdf"
        ),
        baseline_html=Path(
            "output/runs/story162-docling-baseline-marie-louise-r1/docling/baseline-images/12 MARIE-LOUISE (L'HEUREUX) LaCLARE.html"
        ),
        gold_html=Path(
            "benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/chapter-017.html"
        ),
    ),
}


@dataclass(frozen=True)
class VariantConfig:
    variant_id: str
    use_layout_plugin: bool = False
    use_table_plugin: bool = False


VARIANTS: dict[str, VariantConfig] = {
    "table-only": VariantConfig(
        variant_id="plugin-onward-table-structure-v1",
        use_table_plugin=True,
    ),
    "layout-only": VariantConfig(
        variant_id="plugin-onward-layout-v1",
        use_layout_plugin=True,
    ),
    "layout-table": VariantConfig(
        variant_id="plugin-onward-layout-table-v1",
        use_layout_plugin=True,
        use_table_plugin=True,
    ),
}


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


def _table_count(html: str) -> int:
    return len(BeautifulSoup(html or "", "html.parser").find_all("table"))


def _summary_for_html(html: str, document_title: str) -> dict[str, Any]:
    summary = _load_summarize_html_signals()(html, document_title)
    summary["table_count"] = _table_count(html)
    return summary


def _make_converter(variant: VariantConfig) -> DocumentConverter:
    options = PdfPipelineOptions()
    options.allow_external_plugins = True
    options.generate_page_images = True
    options.generate_picture_images = True
    options.images_scale = 2.0
    if variant.use_layout_plugin:
        options.layout_options = build_layout_options()
    if variant.use_table_plugin:
        options.table_structure_options = build_table_structure_options()
    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=options),
        }
    )


def _assert_plugin_registered(variant: VariantConfig) -> dict[str, Any]:
    registration: dict[str, Any] = {}
    if variant.use_layout_plugin:
        disabled = get_layout_factory(allow_external_plugins=False)
        enabled = get_layout_factory(allow_external_plugins=True)
        disabled_kinds = sorted(disabled.registered_kind)
        enabled_kinds = sorted(enabled.registered_kind)
        if "onward_layout_v1" not in enabled_kinds:
            raise RuntimeError(
                "Repo-owned plugin kind onward_layout_v1 was not registered with allow_external_plugins=True"
            )
        if "onward_layout_v1" in disabled_kinds:
            raise RuntimeError(
                "Repo-owned plugin kind onward_layout_v1 should not load with allow_external_plugins=False"
            )
        registration["layout"] = {
            "enabled_kinds": enabled_kinds,
            "disabled_kinds": disabled_kinds,
        }
    if variant.use_table_plugin:
        disabled = get_table_structure_factory(allow_external_plugins=False)
        enabled = get_table_structure_factory(allow_external_plugins=True)
        disabled_kinds = sorted(disabled.registered_kind)
        enabled_kinds = sorted(enabled.registered_kind)
        if "onward_table_structure_v1" not in enabled_kinds:
            raise RuntimeError(
                "Repo-owned plugin kind onward_table_structure_v1 was not registered with allow_external_plugins=True"
            )
        if "onward_table_structure_v1" in disabled_kinds:
            raise RuntimeError(
                "Repo-owned plugin kind onward_table_structure_v1 should not load with allow_external_plugins=False"
            )
        registration["table_structure"] = {
            "enabled_kinds": enabled_kinds,
            "disabled_kinds": disabled_kinds,
        }
    return registration


def run_lane(lane: LaneConfig, variant: VariantConfig, out_root: Path) -> dict[str, Any]:
    out_dir = out_root / lane.lane_id / "docling" / variant.variant_id
    out_dir.mkdir(parents=True, exist_ok=True)

    converter = _make_converter(variant)
    started = time.time()
    conv_res = converter.convert(source=lane.source_pdf)
    elapsed = time.time() - started

    stem = lane.source_pdf.stem
    json_path = out_dir / f"{stem}.json"
    html_path = out_dir / f"{stem}.html"
    md_path = out_dir / f"{stem}.md"
    conv_res.document.save_as_json(json_path)
    conv_res.document.save_as_markdown(md_path, image_mode=ImageRefMode.REFERENCED)
    conv_res.document.save_as_html(html_path, image_mode=ImageRefMode.REFERENCED)
    image_counts = _save_page_and_element_images(conv_res, out_dir / "images")

    plugin_html = html_path.read_text(encoding="utf-8")
    baseline_html = lane.baseline_html.read_text(encoding="utf-8")
    gold_html = lane.gold_html.read_text(encoding="utf-8")

    summary = {
        "schema_version": "docling_onward_plugin_kill_test_v1",
        "lane_id": lane.lane_id,
        "variant_id": variant.variant_id,
        "document_title": lane.document_title,
        "source_pdf": str(lane.source_pdf),
        "baseline_html": str(lane.baseline_html),
        "gold_html": str(lane.gold_html),
        "output_dir": str(out_dir),
        "elapsed_seconds": round(elapsed, 3),
        "docling_version": version("docling"),
        "docling_parse_version": version("docling-parse"),
        "plugin_registration": _assert_plugin_registered(variant),
        "image_counts": image_counts,
        "baseline_signals": _summary_for_html(baseline_html, lane.document_title),
        "plugin_signals": _summary_for_html(plugin_html, lane.document_title),
        "gold_signals": _summary_for_html(gold_html, lane.document_title),
        "artifacts": {
            "json": str(json_path),
            "html": str(html_path),
            "markdown": str(md_path),
            "images": str(out_dir / "images"),
        },
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lanes",
        default="leonidas,marie-louise",
        help="Comma-separated lane ids to run.",
    )
    parser.add_argument(
        "--variants",
        default="table-only,layout-only,layout-table",
        help="Comma-separated variant ids to run.",
    )
    parser.add_argument(
        "--output-root",
        default="output/runs/story163-docling-plugin-killtest-r2",
        help="Output directory for kill-test artifacts.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    lanes = [LANES[name.strip()] for name in args.lanes.split(",") if name.strip()]
    variants = [VARIANTS[name.strip()] for name in args.variants.split(",") if name.strip()]
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    results = []
    for variant in variants:
        for lane in lanes:
            print(
                f"[story163-plugin] running {variant.variant_id} on {lane.lane_id}",
                file=sys.stderr,
            )
            results.append(run_lane(lane, variant, output_root))

    session_summary = {
        "schema_version": "docling_onward_plugin_kill_test_session_v1",
        "output_root": str(output_root),
        "results": results,
    }
    (output_root / "summary.json").write_text(json.dumps(session_summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
