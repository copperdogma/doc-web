#!/usr/bin/env python3
"""
Unstructured EML Intake Module v1

Partitions a plain-text `.eml` message using the Unstructured library and
serializes elements to JSON with light email-specific metadata normalization.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict, List

from modules.common.office_native_bundle import collapse_text
from modules.common.utils import ProgressLogger, ensure_dir, save_jsonl
from modules.intake.unstructured_pdf_intake_v1.main import serialize_element


def partition_email_with_unstructured(
    eml_path: str,
    *,
    content_source: str,
    process_attachments: bool,
) -> List:
    try:
        from unstructured.partition.email import partition_email
    except ImportError as exc:
        raise SystemExit(
            "Unstructured email support is not installed. "
            "Run one of:\n"
            "  python -m pip install '.[driver,email]'\n"
            "  python -m pip install -r requirements.txt  # supported on Python 3.11/3.12\n"
            f"{exc}"
        )

    return partition_email(
        filename=eml_path,
        content_source=content_source,
        process_attachments=process_attachments,
    )


def _normalize_address_list(raw_value: Any) -> list[str]:
    if raw_value is None:
        return []
    values = raw_value if isinstance(raw_value, (list, tuple, set)) else [raw_value]
    normalized: list[str] = []
    for item in values:
        if item is None:
            continue
        text = collapse_text(str(item))
        if text and text not in normalized:
            normalized.append(text)
    return normalized


def _normalize_metadata(metadata: Dict[str, Any], *, raw_metadata_obj: Any) -> Dict[str, Any]:
    normalized = dict(metadata)

    raw_subject = getattr(raw_metadata_obj, "subject", None)
    subject = collapse_text(str(raw_subject or normalized.get("subject", "")))
    if subject:
        normalized["subject"] = subject
    else:
        normalized.pop("subject", None)

    for key in ("sent_from", "sent_to", "sent_cc", "sent_bcc"):
        values = _normalize_address_list(getattr(raw_metadata_obj, key, None) or normalized.get(key))
        if values:
            normalized[key] = values
        else:
            normalized.pop(key, None)

    return normalized


def main() -> None:
    parser = argparse.ArgumentParser(description="Partition plain-text `.eml` with Unstructured into elements.jsonl")
    parser.add_argument("--eml", required=True, help="Path to input `.eml` message")
    parser.add_argument("--outdir", required=True, help="Output directory")
    parser.add_argument(
        "--content-source",
        "--content_source",
        dest="content_source",
        default="text/plain",
        help="Preferred body representation (`text/plain` for the maintained plain-text lane)",
    )
    parser.add_argument(
        "--process-attachments",
        "--process_attachments",
        dest="process_attachments",
        action="store_true",
        default=False,
        help="Recurse into attachments",
    )
    parser.add_argument(
        "--no-process-attachments",
        dest="process_attachments",
        action="store_false",
        help="Ignore attachments",
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

    module_id = "unstructured_email_intake_v1"
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
        message="Partitioning `.eml` with Unstructured",
        module_id=module_id,
    )

    try:
        elements = partition_email_with_unstructured(
            args.eml,
            content_source=args.content_source,
            process_attachments=args.process_attachments,
        )
    except Exception as exc:
        logger.log(
            "extract",
            "failed",
            current=0,
            total=None,
            message=f"Unstructured `.eml` partitioning failed: {exc}",
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
            json.dump(raw_rows, handle, indent=2, ensure_ascii=False, default=str)

    serialized_elements = []
    type_counts: Dict[str, int] = {}
    for idx, elem in enumerate(elements):
        serialized = serialize_element(
            element=elem,
            source_file=os.path.abspath(args.eml),
            sequence=idx,
            run_id=args.run_id,
            module_id=module_id,
        )
        serialized["metadata"] = _normalize_metadata(
            serialized.get("metadata", {}) or {},
            raw_metadata_obj=getattr(elem, "metadata", None),
        )
        serialized_elements.append(serialized)
        elem_type = serialized.get("type", "Unknown")
        type_counts[elem_type] = type_counts.get(elem_type, 0) + 1

    elements_path = os.path.join(args.outdir, "elements.jsonl")
    save_jsonl(elements_path, serialized_elements)

    summary = ", ".join(f"{key}={value}" for key, value in sorted(type_counts.items()))
    location_note = "pageless message anchors only"
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

    print(f"OK Wrote {len(serialized_elements)} elements to {elements_path}")
    print(f"  Location model: {location_note}")
    print(f"  Types: {summary}")


if __name__ == "__main__":
    main()
