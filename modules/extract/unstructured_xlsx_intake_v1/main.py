#!/usr/bin/env python3
"""
Unstructured XLSX Intake Module v1

Partitions an XLSX workbook using the Unstructured library and serializes the
resulting elements to JSON with minimal transformation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List

from modules.common.utils import ProgressLogger, ensure_dir, save_json, save_jsonl
from modules.intake.unstructured_pdf_intake_v1.main import serialize_element
from modules.extract.unstructured_xlsx_intake_v1.source_features import inspect_xlsx_features


def partition_xlsx_with_unstructured(xlsx_path: str, *, infer_table_structure: bool) -> List:
    try:
        from unstructured.partition.xlsx import partition_xlsx
    except ImportError as exc:
        raise SystemExit(
            "Unstructured XLSX support is not installed. "
            "Run one of:\n"
            "  python -m pip install '.[driver,xlsx]'\n"
            "  python -m pip install -r requirements.txt\n"
            f"{exc}"
        )

    return partition_xlsx(filename=xlsx_path, infer_table_structure=infer_table_structure)


def main() -> None:
    parser = argparse.ArgumentParser(description="Partition XLSX with Unstructured into elements.jsonl")
    parser.add_argument("--xlsx", required=True, help="Path to input XLSX")
    parser.add_argument("--outdir", required=True, help="Output directory")
    parser.add_argument(
        "--infer-table-structure",
        "--infer_table_structure",
        dest="infer_table_structure",
        action="store_true",
        default=True,
        help="Preserve sheet tables as HTML when Unstructured exposes them",
    )
    parser.add_argument(
        "--no-infer-table-structure",
        dest="infer_table_structure",
        action="store_false",
        help="Disable Unstructured table HTML extraction",
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

    module_id = "unstructured_xlsx_intake_v1"
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
        message="Partitioning XLSX with Unstructured",
        module_id=module_id,
    )

    report_path = (Path(args.outdir) / "xlsx_source_features.json").resolve()
    feature_report = None

    def reject(message: str) -> None:
        save_json(str(report_path), feature_report)
        logger.log("extract", "failed", message=message, artifact=str(report_path), module_id=module_id)
        raise SystemExit(message)

    def require_unchanged_source() -> None:
        observed = hashlib.sha256(Path(args.xlsx).read_bytes()).hexdigest()
        if observed != feature_report["source_sha256"]:
            feature_report["disposition"] = "blocked_source_changed"
            feature_report["observed_source_sha256"] = observed
            reject(f"XLSX source changed after native inspection; see {report_path}")

    try:
        feature_report = inspect_xlsx_features(args.xlsx)
        if feature_report["disposition"] != "native_feature_gate_clear":
            reject(
                f'XLSX unsupported native features: {len(feature_report["formula_cells"])} formula cells, '
                f'{len(feature_report["merged_ranges"])} merged ranges; see {report_path}'
            )
        require_unchanged_source()
        elements = partition_xlsx_with_unstructured(
            args.xlsx,
            infer_table_structure=args.infer_table_structure,
        )
        require_unchanged_source()
        save_json(str(report_path), feature_report)
    except Exception as exc:
        logger.log(
            "extract",
            "failed",
            current=0,
            total=None,
            message=f"XLSX source inspection or partitioning failed: {exc}",
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
        with open(raw_path, "w", encoding="utf-8") as handle:
            json.dump(raw_rows, handle, indent=2, ensure_ascii=False, default=str)

    serialized_elements = []
    type_counts: Dict[str, int] = {}
    sheet_names = set()
    for idx, elem in enumerate(elements):
        serialized = serialize_element(
            element=elem,
            source_file=os.path.abspath(args.xlsx),
            sequence=idx,
            run_id=args.run_id,
            module_id=module_id,
        )
        serialized_elements.append(serialized)
        elem_type = serialized.get("type", "Unknown")
        type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
        page_name = serialized.get("metadata", {}).get("page_name")
        if page_name:
            sheet_names.add(str(page_name))

    elements_path = os.path.join(args.outdir, "elements.jsonl")
    save_jsonl(elements_path, serialized_elements)

    summary = ", ".join(f"{k}={v}" for k, v in sorted(type_counts.items()))
    location_note = (
        f"{len(sheet_names)} sheet anchors"
        if sheet_names
        else "workbook-level source anchors only"
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
