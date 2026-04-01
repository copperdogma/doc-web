#!/usr/bin/env python3
"""Build a doc-web bundle directly from DOCX Unstructured elements."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Optional

from modules.common.office_native_bundle import collapse_text, write_bundle
from modules.common.utils import ProgressLogger, ensure_dir, read_jsonl, save_json


SENTENCE_END_RE = re.compile(r"[.!?](?:['\")\]]*)$")


def _looks_like_misclassified_paragraph(text: str) -> bool:
    stripped = collapse_text(text)
    if not stripped or not SENTENCE_END_RE.search(stripped):
        return False

    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", stripped)
    if len(words) < 3:
        return False

    lowercase_starts = sum(1 for word in words[1:] if word and word[0].islower())
    return lowercase_starts >= max(2, len(words) - 2)


def _normalize_docx_elements(elements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    top_level_title_count = 0

    for element in elements:
        normalized_element = dict(element)
        metadata = dict(element.get("metadata", {}) or {})
        normalized_element["metadata"] = metadata
        element_type = normalized_element.get("type")
        text = normalized_element.get("text", "") or ""

        if element_type == "Title" and not metadata.get("parent_id"):
            top_level_title_count += 1
            if top_level_title_count > 1 and _looks_like_misclassified_paragraph(text):
                normalized_element["type"] = "NarrativeText"

        normalized.append(normalized_element)

    return normalized


def _top_level_title_indexes(elements: list[dict[str, Any]]) -> list[int]:
    indexes = []
    for idx, element in enumerate(elements):
        metadata = element.get("metadata", {}) or {}
        if element.get("type") == "Title" and not metadata.get("parent_id"):
            if collapse_text(element.get("text", "")):
                indexes.append(idx)
    return indexes


def _entry_slices(elements: list[dict[str, Any]], fallback_title: str) -> tuple[str, list[dict[str, Any]]]:
    title_indexes = _top_level_title_indexes(elements)
    document_title = fallback_title
    entry_specs: list[dict[str, Any]] = []

    if title_indexes:
        document_title = collapse_text(elements[title_indexes[0]].get("text", "")) or fallback_title

    if len(title_indexes) >= 2:
        section_indexes = title_indexes[1:]
        for ordinal, start in enumerate(section_indexes, start=1):
            end = section_indexes[ordinal] if ordinal < len(section_indexes) else len(elements)
            entry_elements = elements[start:end]
            entry_title = collapse_text(entry_elements[0].get("text", "")) or f"Section {ordinal}"
            entry_specs.append(
                {
                    "entry_id": f"chapter-{ordinal:03d}",
                    "kind": "chapter",
                    "title": entry_title,
                    "elements": entry_elements,
                }
            )
    else:
        entry_specs.append(
            {
                "entry_id": "page-001",
                "kind": "page",
                "title": document_title,
                "elements": elements,
            }
        )

    return document_title, entry_specs


def _build_bundle(
    elements: list[dict[str, Any]],
    *,
    out_path: Path,
    module_id: str,
    run_id: Optional[str],
    book_title: str,
    book_author: str,
) -> dict[str, Any]:
    fallback_title = book_title.strip() or out_path.stem
    normalized_elements = _normalize_docx_elements(elements)
    document_title, entry_specs = _entry_slices(normalized_elements, fallback_title)
    if book_title.strip():
        document_title = book_title.strip()
    return write_bundle(
        entry_specs=entry_specs,
        source_elements=normalized_elements,
        out_path=out_path,
        module_id=module_id,
        run_id=run_id,
        document_title=document_title,
        creator=book_author,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Input unstructured elements JSONL path")
    parser.add_argument("--out", required=True, help="Output report JSON path")
    parser.add_argument("--book-title", default="", help="Optional document title override")
    parser.add_argument("--book-author", default="", help="Optional document author override")
    parser.add_argument("--run-id", dest="run_id", default=None, help="Driver compatibility")
    parser.add_argument("--state-file", dest="state_file", default=None, help="Driver compatibility")
    parser.add_argument("--progress-file", dest="progress_file", default=None, help="Driver compatibility")
    args = parser.parse_args()

    module_id = "docx_elements_to_bundle_v1"
    logger = ProgressLogger(
        state_path=args.state_file,
        progress_path=args.progress_file,
        run_id=args.run_id,
    )
    logger.log("docx_bundle", "running", message=f"Loading {args.input}", module_id=module_id)

    elements = list(read_jsonl(args.input))
    if not elements:
        raise SystemExit("No DOCX elements found; cannot build bundle")

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
        "docx_bundle",
        "done",
        current=report["entry_count"],
        total=report["entry_count"],
        message=f'Built DOCX bundle with {report["entry_count"]} entries and {report["provenance_row_count"]} provenance rows',
        artifact=str(out_path),
        module_id=module_id,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
