#!/usr/bin/env python3
"""
Unstructured DOCX Intake Module v1

Partitions a DOCX using the Unstructured library and serializes elements
to JSON with minimal transformation, preserving Unstructured's native
element categories and metadata.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Dict, List, Optional

from modules.common.utils import ProgressLogger, ensure_dir, save_jsonl
from modules.intake.unstructured_pdf_intake_v1.main import serialize_element


def partition_docx_with_unstructured(
    docx_path: str,
    *,
    infer_table_structure: bool,
    include_page_breaks: bool,
    starting_page_number: int,
    strategy: Optional[str],
) -> List:
    try:
        from unstructured.partition.docx import partition_docx
    except ImportError as e:
        raise SystemExit(
            "Unstructured DOCX support is not installed. "
            "Run one of:\n"
            "  python -m pip install '.[driver,docx]'\n"
            "  python -m pip install -r requirements.txt\n"
            f"{e}"
        )

    kwargs = {
        "filename": docx_path,
        "infer_table_structure": infer_table_structure,
        "include_page_breaks": include_page_breaks,
        "starting_page_number": starting_page_number,
    }
    if strategy:
        kwargs["strategy"] = strategy

    return partition_docx(**kwargs)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Partition DOCX with Unstructured into elements.jsonl"
    )
    parser.add_argument("--docx", required=True, help="Path to input DOCX")
    parser.add_argument("--outdir", required=True, help="Output directory")
    parser.add_argument(
        "--infer-table-structure",
        "--infer_table_structure",
        dest="infer_table_structure",
        action="store_true",
        default=True,
        help="Infer table structure and extract HTML",
    )
    parser.add_argument(
        "--no-infer-table-structure",
        dest="infer_table_structure",
        action="store_false",
        help="Disable table structure inference",
    )
    parser.add_argument(
        "--include-page-breaks",
        "--include_page_breaks",
        dest="include_page_breaks",
        action="store_true",
        default=True,
        help="Preserve DOCX page-break markers when Unstructured exposes them",
    )
    parser.add_argument(
        "--no-include-page-breaks",
        dest="include_page_breaks",
        action="store_false",
        help="Drop explicit page-break markers",
    )
    parser.add_argument(
        "--starting-page-number",
        "--starting_page_number",
        dest="starting_page_number",
        type=int,
        default=1,
        help="Starting page number for explicit page-break markers if present",
    )
    parser.add_argument(
        "--strategy",
        default=None,
        help="Optional Unstructured DOCX partition strategy",
    )
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

    module_id = "unstructured_docx_intake_v1"
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
        message="Partitioning DOCX with Unstructured",
        module_id=module_id,
    )

    try:
        elements = partition_docx_with_unstructured(
            args.docx,
            infer_table_structure=args.infer_table_structure,
            include_page_breaks=args.include_page_breaks,
            starting_page_number=args.starting_page_number,
            strategy=args.strategy,
        )
    except Exception as exc:
        logger.log(
            "extract",
            "failed",
            current=0,
            total=None,
            message=f"Unstructured DOCX partitioning failed: {exc}",
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
                        k: str(v)
                        for k, v in vars(metadata_obj).items()
                        if not k.startswith("_")
                    }
                    if metadata_obj is not None
                    else {},
                }
            )
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(raw_rows, f, indent=2, ensure_ascii=False, default=str)

    serialized_elements = []
    type_counts: Dict[str, int] = {}
    page_numbers = set()
    for idx, elem in enumerate(elements):
        serialized = serialize_element(
            element=elem,
            source_file=os.path.abspath(args.docx),
            sequence=idx,
            run_id=args.run_id,
            module_id=module_id,
        )
        serialized_elements.append(serialized)
        elem_type = serialized.get("type", "Unknown")
        type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
        page_number = serialized.get("metadata", {}).get("page_number")
        if isinstance(page_number, int):
            page_numbers.add(page_number)

    elements_path = os.path.join(args.outdir, "elements.jsonl")
    save_jsonl(elements_path, serialized_elements)

    summary = ", ".join(f"{k}={v}" for k, v in sorted(type_counts.items()))
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
