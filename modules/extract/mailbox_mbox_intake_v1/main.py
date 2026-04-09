#!/usr/bin/env python3
"""
Mailbox MBOX Intake Module v1

Splits a bounded plain-text `.mbox` archive into ordered messages, partitions
each message with Unstructured, and serializes the resulting elements to JSONL
with archive/message metadata preserved in `metadata`.
"""

from __future__ import annotations

import argparse
import io
import json
import mailbox
import os
from pathlib import Path
from typing import Any, Dict, List

from modules.common.office_native_bundle import collapse_text
from modules.common.utils import ProgressLogger, ensure_dir, save_jsonl
from modules.intake.unstructured_pdf_intake_v1.main import serialize_element


def partition_email_with_unstructured(
    payload: bytes,
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
        file=io.BytesIO(payload),
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


def _normalize_metadata(
    metadata: Dict[str, Any], *, raw_metadata_obj: Any
) -> Dict[str, Any]:
    normalized = dict(metadata)

    raw_subject = getattr(raw_metadata_obj, "subject", None)
    subject = collapse_text(str(raw_subject or normalized.get("subject", "")))
    if subject:
        normalized["subject"] = subject
    else:
        normalized.pop("subject", None)

    for key in ("sent_from", "sent_to", "sent_cc", "sent_bcc"):
        values = _normalize_address_list(
            getattr(raw_metadata_obj, key, None) or normalized.get(key)
        )
        if values:
            normalized[key] = values
        else:
            normalized.pop(key, None)

    return normalized


def _archive_metadata(
    *,
    mbox_path: Path,
    message: mailbox.mboxMessage,
    message_index: int,
    message_count: int,
) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "file_directory": str(mbox_path.parent),
        "filename": mbox_path.name,
        "archive_source_format": "mbox",
        "archive_message_index": message_index,
        "archive_message_count": message_count,
        "archive_message_id": collapse_text(
            str(message.get("Message-ID") or f"message-{message_index:03d}")
        ),
    }
    raw_date = collapse_text(str(message.get("Date") or ""))
    if raw_date:
        metadata["archive_message_date"] = raw_date
    return metadata


def _scoped_element_id(*, message_index: int, element_sequence: int) -> str:
    # Unstructured email element IDs can repeat across different messages when the
    # text is identical. Scope IDs to the archive row so `source_element_ids`
    # remain unambiguous in downstream provenance.
    return f"mbox-message-{message_index:03d}-element-{element_sequence + 1:04d}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Partition plain-text `.mbox` with Unstructured into elements.jsonl"
    )
    parser.add_argument("--mbox", required=True, help="Path to input `.mbox` archive")
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

    module_id = "mailbox_mbox_intake_v1"
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
        message="Partitioning `.mbox` archive with stdlib mailbox.mbox + Unstructured",
        module_id=module_id,
    )

    mbox_path = Path(args.mbox).resolve()
    if not mbox_path.exists():
        raise SystemExit(f"MBOX archive not found: {mbox_path}")

    archive = mailbox.mbox(str(mbox_path), create=False)
    message_count = len(archive)
    if message_count == 0:
        raise SystemExit(f"No messages found in {mbox_path}")

    serialized_elements: list[dict[str, Any]] = []
    raw_rows: list[dict[str, Any]] = []
    type_counts: Dict[str, int] = {}
    element_sequence = 0

    for message_index, message in enumerate(archive, start=1):
        payload = message.as_bytes()
        try:
            elements = partition_email_with_unstructured(
                payload,
                content_source=args.content_source,
                process_attachments=args.process_attachments,
            )
        except Exception as exc:
            logger.log(
                "extract",
                "failed",
                current=message_index,
                total=message_count,
                message=f"Unstructured `.mbox` partitioning failed on message {message_index}: {exc}",
                module_id=module_id,
            )
            raise

        if not elements:
            raise SystemExit(
                f"Message {message_index} from {mbox_path} produced no elements; refusing to emit a partial archive seam."
            )

        archive_metadata = _archive_metadata(
            mbox_path=mbox_path,
            message=message,
            message_index=message_index,
            message_count=message_count,
        )
        normalized_subject = collapse_text(str(message.get("Subject") or ""))
        if normalized_subject:
            archive_metadata["archive_message_subject"] = normalized_subject

        if args.save_raw:
            raw_rows.append(
                {
                    "message_index": message_index,
                    "message_id": archive_metadata["archive_message_id"],
                    "subject": normalized_subject,
                    "elements": [
                        {
                            "id": getattr(elem, "id", None),
                            "category": getattr(elem, "category", None),
                            "type": getattr(elem, "type", None),
                            "text": getattr(elem, "text", None),
                            "metadata": {
                                key: str(value)
                                for key, value in vars(
                                    getattr(elem, "metadata", None) or {}
                                ).items()
                                if not key.startswith("_")
                            },
                        }
                        for elem in elements
                    ],
                }
            )

        for elem in elements:
            serialized = serialize_element(
                element=elem,
                source_file=str(mbox_path),
                sequence=element_sequence,
                run_id=args.run_id,
                module_id=module_id,
            )
            metadata = _normalize_metadata(
                serialized.get("metadata", {}) or {},
                raw_metadata_obj=getattr(elem, "metadata", None),
            )
            metadata.update(archive_metadata)
            native_element_id = collapse_text(str(serialized.get("id") or ""))
            if native_element_id:
                metadata["archive_native_element_id"] = native_element_id
            serialized["id"] = _scoped_element_id(
                message_index=message_index,
                element_sequence=element_sequence,
            )
            serialized["metadata"] = metadata
            serialized_elements.append(serialized)

            elem_type = serialized.get("type", "Unknown")
            type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
            element_sequence += 1

    if args.save_raw:
        raw_path = os.path.join(args.outdir, "unstructured_raw.json")
        with open(raw_path, "w", encoding="utf-8") as handle:
            json.dump(raw_rows, handle, indent=2, ensure_ascii=False, default=str)

    elements_path = os.path.join(args.outdir, "elements.jsonl")
    save_jsonl(elements_path, serialized_elements)

    summary = ", ".join(f"{key}={value}" for key, value in sorted(type_counts.items()))
    location_note = f"{message_count} ordered message anchors"
    logger.log(
        "extract",
        "done",
        current=message_count,
        total=message_count,
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
