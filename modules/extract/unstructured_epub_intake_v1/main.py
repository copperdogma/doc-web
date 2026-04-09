#!/usr/bin/env python3
"""
Unstructured EPUB Intake Module v1

Partitions an EPUB using Unstructured and serializes the resulting elements
to JSON with minimal transformation.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import zipfile
from typing import Any, Dict, List
from xml.etree import ElementTree as ET

from modules.common.utils import ProgressLogger, ensure_dir, save_jsonl
from modules.intake.unstructured_pdf_intake_v1.main import serialize_element


def read_epub_package_metadata(epub_path: str) -> Dict[str, Any]:
    try:
        with zipfile.ZipFile(epub_path) as archive:
            container_root = ET.fromstring(archive.read("META-INF/container.xml"))
            rootfile = container_root.find(".//{*}rootfile")
            if rootfile is None:
                return {}
            opf_path = (rootfile.attrib or {}).get("full-path")
            if not opf_path:
                return {}

            opf_root = ET.fromstring(archive.read(opf_path))
            metadata = opf_root.find(".//{*}metadata")
            if metadata is None:
                return {}

            title = ""
            creators: list[str] = []
            languages: list[str] = []
            for child in metadata:
                name = child.tag.rsplit("}", 1)[-1]
                text = (child.text or "").strip()
                if not text:
                    continue
                if name == "title" and not title:
                    title = text
                elif name == "creator":
                    creators.append(text)
                elif name == "language":
                    languages.append(text)

            payload: Dict[str, Any] = {}
            if title:
                payload["title"] = title
            if creators:
                payload["creator"] = ", ".join(dict.fromkeys(creators))
            if languages:
                payload["languages"] = list(dict.fromkeys(languages))
            return payload
    except (ET.ParseError, KeyError, OSError, zipfile.BadZipFile):
        return {}


def partition_epub_with_unstructured(epub_path: str) -> List:
    try:
        from unstructured.partition.epub import partition_epub
    except ImportError as exc:
        raise SystemExit(
            "Unstructured EPUB support is not installed. "
            "Run one of:\n"
            "  python -m pip install '.[driver,epub]'\n"
            "  python -m pip install -r requirements.txt\n"
            f"{exc}"
        )

    if not shutil.which("pandoc"):
        raise SystemExit(
            "Pandoc is required for EPUB partitioning. Install pandoc and rerun the EPUB lane."
        )

    try:
        return partition_epub(filename=epub_path)
    except ImportError as exc:
        raise SystemExit(
            "Unstructured EPUB support is incomplete in this environment. "
            "Run one of:\n"
            "  python -m pip install '.[driver,epub]'\n"
            "  python -m pip install -r requirements.txt\n"
            f"{exc}"
        )


def _augment_metadata(serialized: Dict[str, Any], package_metadata: Dict[str, Any]) -> Dict[str, Any]:
    metadata = dict(serialized.get("metadata", {}) or {})
    if package_metadata.get("title"):
        metadata["epub_title"] = package_metadata["title"]
    if package_metadata.get("creator"):
        metadata["epub_creator"] = package_metadata["creator"]
    if package_metadata.get("languages") and not metadata.get("languages"):
        metadata["languages"] = package_metadata["languages"]
    serialized["metadata"] = metadata
    return serialized


def main() -> None:
    parser = argparse.ArgumentParser(description="Partition EPUB with Unstructured into elements.jsonl")
    parser.add_argument("--epub", required=True, help="Path to input EPUB")
    parser.add_argument("--outdir", required=True, help="Output directory")
    parser.add_argument(
        "--save-raw",
        "--save_raw",
        dest="save_raw",
        action="store_true",
        default=False,
        help="Save raw Unstructured output for debugging",
    )
    parser.add_argument("--progress-file", help="Path to pipeline_events.jsonl")
    parser.add_argument("--state-file", help="Path to pipeline_state.json")
    parser.add_argument("--run-id", help="Run identifier for logging")
    args = parser.parse_args()

    module_id = "unstructured_epub_intake_v1"
    logger = ProgressLogger(
        state_path=args.state_file,
        progress_path=args.progress_file,
        run_id=args.run_id,
    )

    ensure_dir(args.outdir)
    logger.log(
        "extract",
        "running",
        current=0,
        total=None,
        message="Partitioning EPUB with Unstructured",
        module_id=module_id,
    )

    package_metadata = read_epub_package_metadata(args.epub)

    try:
        elements = partition_epub_with_unstructured(args.epub)
    except Exception as exc:
        logger.log(
            "extract",
            "failed",
            current=0,
            total=None,
            message=f"Unstructured EPUB partitioning failed: {exc}",
            module_id=module_id,
        )
        raise

    if args.save_raw:
        raw_path = os.path.join(args.outdir, "unstructured_raw.json")
        raw_rows = []
        for elem in elements:
            metadata_obj = getattr(elem, "metadata", None)
            raw_rows.append(
                {
                    "id": getattr(elem, "id", None),
                    "category": getattr(elem, "category", None),
                    "type": getattr(elem, "type", None),
                    "text": getattr(elem, "text", None),
                    "metadata": {
                        key: str(value)
                        for key, value in vars(metadata_obj).items()
                        if not key.startswith("_")
                    }
                    if metadata_obj is not None
                    else {},
                }
            )
        with open(raw_path, "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "package_metadata": package_metadata,
                    "elements": raw_rows,
                },
                handle,
                indent=2,
                ensure_ascii=False,
                default=str,
            )

    serialized_elements = []
    type_counts: Dict[str, int] = {}
    page_numbers = set()
    for idx, elem in enumerate(elements):
        serialized = serialize_element(
            element=elem,
            source_file=os.path.abspath(args.epub),
            sequence=idx,
            run_id=args.run_id,
            module_id=module_id,
        )
        serialized = _augment_metadata(serialized, package_metadata)
        serialized_elements.append(serialized)
        elem_type = serialized.get("type", "Unknown")
        type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
        page_number = serialized.get("metadata", {}).get("page_number")
        if isinstance(page_number, int):
            page_numbers.add(page_number)

    elements_path = os.path.join(args.outdir, "elements.jsonl")
    save_jsonl(elements_path, serialized_elements)

    summary = ", ".join(f"{key}={value}" for key, value in sorted(type_counts.items()))
    location_note = (
        f"{len(page_numbers)} explicit pages"
        if page_numbers
        else "pageless source anchors only"
    )
    logger.log(
        "extract",
        "done",
        current=1,
        total=1,
        message=f"Elements: {len(serialized_elements)} ({location_note}; {summary})",
        artifact=elements_path,
        module_id=module_id,
        schema_version="unstructured_element_v1",
    )

    print(f"✓ Wrote {len(serialized_elements)} elements to {elements_path}")
    print(f"  Location model: {location_note}")
    print(f"  Types: {summary}")


if __name__ == "__main__":
    main()
