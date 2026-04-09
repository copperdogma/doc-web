#!/usr/bin/env python3
"""Build a doc-web bundle directly from `.mbox` Unstructured elements."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Optional

from modules.common.office_native_bundle import (
    collapse_text,
    source_artifact,
    write_bundle,
)
from modules.common.utils import ProgressLogger, ensure_dir, read_jsonl, save_json


UPPERCASE_TOKENS = {"eml", "html", "mbox"}


def _metadata_text(elements: list[dict[str, Any]], key: str) -> str:
    for element in elements:
        metadata = element.get("metadata", {}) or {}
        value = metadata.get(key)
        if isinstance(value, list):
            for item in value:
                text = collapse_text(str(item))
                if text:
                    return text
            continue
        text = collapse_text(str(value or ""))
        if text:
            return text
    return ""


def _metadata_list(elements: list[dict[str, Any]], key: str) -> list[str]:
    values: list[str] = []
    for element in elements:
        metadata = element.get("metadata", {}) or {}
        raw_value = metadata.get(key)
        items = raw_value if isinstance(raw_value, list) else [raw_value]
        for item in items:
            text = collapse_text(str(item or ""))
            if text and text not in values:
                values.append(text)
    return values


def _metadata_int(element: dict[str, Any], key: str) -> Optional[int]:
    metadata = element.get("metadata", {}) or {}
    value = metadata.get(key)
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _fallback_document_title(elements: list[dict[str, Any]], fallback: str) -> str:
    source_path = source_artifact(elements, fallback)
    stem = Path(source_path).stem if source_path else fallback
    words = collapse_text(stem.replace("_", " ").replace("-", " ")).split()
    pretty_words = []
    for word in words:
        lowered = word.lower()
        if lowered in UPPERCASE_TOKENS:
            pretty_words.append(lowered.upper())
        elif word.islower():
            pretty_words.append(word.capitalize())
        else:
            pretty_words.append(word)
    return " ".join(pretty_words) or fallback


def _normalize_email_elements(elements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for element in elements:
        normalized_element = dict(element)
        metadata = dict(element.get("metadata", {}) or {})
        normalized_element["metadata"] = metadata
        if normalized_element.get("type") == "Title" and collapse_text(
            normalized_element.get("text", "")
        ):
            normalized_element["type"] = "NarrativeText"
        normalized.append(normalized_element)
    return normalized


def _group_by_message(elements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[int, dict[str, Any]] = {}
    for element in elements:
        message_index = _metadata_int(element, "archive_message_index")
        if message_index is None:
            raise SystemExit(
                "Element missing archive_message_index metadata; cannot build `.mbox` bundle honestly."
            )
        entry = grouped.get(message_index)
        if entry is None:
            entry = {
                "message_index": message_index,
                "entry_id": f"page-{message_index:03d}",
                "kind": "page",
                "title": "",
                "elements": [],
                "source_pages": [],
            }
            grouped[message_index] = entry
        entry["elements"].append(element)

    entry_specs: list[dict[str, Any]] = []
    for message_index in sorted(grouped):
        entry = grouped[message_index]
        entry_elements = _normalize_email_elements(entry["elements"])
        subject = _metadata_text(entry_elements, "subject")
        entry["title"] = subject or f"Message {message_index:03d}"
        entry["elements"] = entry_elements
        entry_specs.append(entry)
    return entry_specs


def _report_messages(entry_specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    for entry in entry_specs:
        entry_elements = entry["elements"]
        first_metadata = (
            (entry_elements[0].get("metadata", {}) or {}) if entry_elements else {}
        )
        messages.append(
            {
                "entry_id": entry["entry_id"],
                "message_index": entry["message_index"],
                "subject": _metadata_text(entry_elements, "subject") or entry["title"],
                "sent_from": _metadata_list(entry_elements, "sent_from"),
                "sent_to": _metadata_list(entry_elements, "sent_to"),
                "message_id": first_metadata.get("archive_message_id"),
                "date": first_metadata.get("archive_message_date"),
            }
        )
    return messages


def _creator_from_messages(messages: list[dict[str, Any]], override: str) -> str:
    if override.strip():
        return override.strip()
    unique_senders = []
    for message in messages:
        for sender in message.get("sent_from", []) or []:
            text = collapse_text(str(sender))
            if text and text not in unique_senders:
                unique_senders.append(text)
    return unique_senders[0] if len(unique_senders) == 1 else ""


def _build_bundle(
    elements: list[dict[str, Any]],
    *,
    out_path: Path,
    module_id: str,
    run_id: Optional[str],
    book_title: str,
    book_author: str,
) -> dict[str, Any]:
    entry_specs = _group_by_message(elements)
    messages = _report_messages(entry_specs)
    document_title = book_title.strip() or _fallback_document_title(
        elements, out_path.stem
    )
    report = write_bundle(
        entry_specs=entry_specs,
        source_elements=elements,
        out_path=out_path,
        module_id=module_id,
        run_id=run_id,
        document_title=document_title,
        creator=_creator_from_messages(messages, book_author),
    )
    report["archive_metadata"] = {
        "format": "mbox",
        "message_count": len(entry_specs),
    }
    report["messages"] = messages
    report["anchor_model"] = {
        "source_pages": "none",
        "provenance": "source_element_ids",
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", required=True, help="Input unstructured elements JSONL path"
    )
    parser.add_argument("--out", required=True, help="Output report JSON path")
    parser.add_argument(
        "--book-title", default="", help="Optional mailbox title override"
    )
    parser.add_argument(
        "--book-author", default="", help="Optional mailbox creator override"
    )
    parser.add_argument(
        "--run-id", dest="run_id", default=None, help="Driver compatibility"
    )
    parser.add_argument(
        "--state-file", dest="state_file", default=None, help="Driver compatibility"
    )
    parser.add_argument(
        "--progress-file",
        dest="progress_file",
        default=None,
        help="Driver compatibility",
    )
    args = parser.parse_args()

    module_id = "mbox_elements_to_bundle_v1"
    logger = ProgressLogger(
        state_path=args.state_file,
        progress_path=args.progress_file,
        run_id=args.run_id,
    )
    logger.log(
        "mbox_bundle", "running", message=f"Loading {args.input}", module_id=module_id
    )

    elements = list(read_jsonl(args.input))
    if not elements:
        raise SystemExit("No MBOX elements found; cannot build bundle")

    out_path = Path(args.out)
    ensure_dir(str(out_path.parent))
    report = _build_bundle(
        elements,
        out_path=out_path,
        module_id=module_id,
        run_id=args.run_id,
        book_title=args.book_title,
        book_author=args.book_author,
    )
    save_json(str(out_path), report)
    logger.log(
        "mbox_bundle",
        "done",
        current=report["entry_count"],
        total=report["entry_count"],
        message=(
            f"Built MBOX bundle with {report['entry_count']} entries and "
            f"{report['provenance_row_count']} provenance rows"
        ),
        artifact=str(out_path),
        module_id=module_id,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
