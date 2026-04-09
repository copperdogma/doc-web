#!/usr/bin/env python3
"""Build a doc-web bundle directly from `.eml` Unstructured elements."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Optional

from modules.common.office_native_bundle import collapse_text, source_artifact, write_bundle
from modules.common.utils import ProgressLogger, ensure_dir, read_jsonl, save_json


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


def _fallback_document_title(elements: list[dict[str, Any]], fallback: str) -> str:
    source_path = source_artifact(elements, fallback)
    stem = Path(source_path).stem if source_path else fallback
    words = collapse_text(stem.replace("_", " ").replace("-", " ")).split()
    pretty_words = ["EML" if word.lower() == "eml" else word.capitalize() for word in words]
    return " ".join(pretty_words) or fallback


def _normalize_email_elements(elements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for element in elements:
        normalized_element = dict(element)
        metadata = dict(element.get("metadata", {}) or {})
        normalized_element["metadata"] = metadata
        if normalized_element.get("type") == "Title" and collapse_text(normalized_element.get("text", "")):
            normalized_element["type"] = "NarrativeText"
        normalized.append(normalized_element)
    return normalized


def _build_bundle(
    elements: list[dict[str, Any]],
    *,
    out_path: Path,
    module_id: str,
    run_id: Optional[str],
    book_title: str,
    book_author: str,
) -> dict[str, Any]:
    subject = _metadata_text(elements, "subject")
    sent_from = _metadata_list(elements, "sent_from")
    sent_to = _metadata_list(elements, "sent_to")
    normalized_elements = _normalize_email_elements(elements)
    document_title = book_title.strip() or subject or _fallback_document_title(normalized_elements, out_path.stem)
    creator = book_author.strip() or (sent_from[0] if sent_from else "")
    entry_specs = [
        {
            "entry_id": "page-001",
            "kind": "page",
            "title": document_title,
            "elements": normalized_elements,
            "source_pages": [],
        }
    ]
    report = write_bundle(
        entry_specs=entry_specs,
        source_elements=normalized_elements,
        out_path=out_path,
        module_id=module_id,
        run_id=run_id,
        document_title=document_title,
        creator=creator,
    )
    report["message_metadata"] = {
        "subject": subject or document_title,
        "sent_from": sent_from,
        "sent_to": sent_to,
    }
    report["anchor_model"] = {
        "source_pages": "none",
        "provenance": "source_element_ids",
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Input unstructured elements JSONL path")
    parser.add_argument("--out", required=True, help="Output report JSON path")
    parser.add_argument("--book-title", default="", help="Optional email subject override")
    parser.add_argument("--book-author", default="", help="Optional sender override")
    parser.add_argument("--run-id", dest="run_id", default=None, help="Driver compatibility")
    parser.add_argument("--state-file", dest="state_file", default=None, help="Driver compatibility")
    parser.add_argument("--progress-file", dest="progress_file", default=None, help="Driver compatibility")
    args = parser.parse_args()

    module_id = "email_elements_to_bundle_v1"
    logger = ProgressLogger(
        state_path=args.state_file,
        progress_path=args.progress_file,
        run_id=args.run_id,
    )
    logger.log("email_bundle", "running", message=f"Loading {args.input}", module_id=module_id)

    elements = list(read_jsonl(args.input))
    if not elements:
        raise SystemExit("No email elements found; cannot build bundle")

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
        "email_bundle",
        "done",
        current=report["entry_count"],
        total=report["entry_count"],
        message=(
            f'Built email bundle with {report["entry_count"]} entries and '
            f'{report["provenance_row_count"]} provenance rows'
        ),
        artifact=str(out_path),
        module_id=module_id,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
