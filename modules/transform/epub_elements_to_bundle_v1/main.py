#!/usr/bin/env python3
"""Build a doc-web bundle directly from EPUB Unstructured elements."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Optional

from modules.common.office_native_bundle import collapse_text, source_artifact, write_bundle
from modules.common.utils import ProgressLogger, ensure_dir, read_jsonl, save_json


def _top_level_title_indexes(elements: list[dict[str, Any]]) -> list[int]:
    indexes = []
    for idx, element in enumerate(elements):
        metadata = element.get("metadata", {}) or {}
        if element.get("type") == "Title" and not metadata.get("parent_id"):
            if collapse_text(element.get("text", "")):
                indexes.append(idx)
    return indexes


def _has_renderable_content(elements: list[dict[str, Any]]) -> bool:
    for element in elements:
        if element.get("type") == "Table":
            return True
        if collapse_text(element.get("text", "")):
            return True
    return False


def _metadata_value(elements: list[dict[str, Any]], key: str) -> str:
    for element in elements:
        metadata = element.get("metadata", {}) or {}
        value = collapse_text(str(metadata.get(key, "")))
        if value:
            return value
    return ""


def _fallback_document_title(elements: list[dict[str, Any]], fallback: str) -> str:
    source_path = source_artifact(elements, fallback)
    stem = Path(source_path).stem if source_path else fallback
    return collapse_text(stem.replace("_", " ").replace("-", " ")) or fallback


def _entry_specs(elements: list[dict[str, Any]], fallback_title: str) -> list[dict[str, Any]]:
    title_indexes = _top_level_title_indexes(elements)
    entry_specs: list[dict[str, Any]] = []

    if title_indexes:
        first_title_index = title_indexes[0]
        if first_title_index > 0 and _has_renderable_content(elements[:first_title_index]):
            entry_specs.append(
                {
                    "entry_id": "page-001",
                    "kind": "page",
                    "title": "Front Matter",
                    "elements": elements[:first_title_index],
                }
            )

        for ordinal, start in enumerate(title_indexes, start=1):
            end = title_indexes[ordinal] if ordinal < len(title_indexes) else len(elements)
            entry_elements = elements[start:end]
            entry_title = collapse_text(entry_elements[0].get("text", "")) or f"Chapter {ordinal}"
            entry_specs.append(
                {
                    "entry_id": f"chapter-{ordinal:03d}",
                    "kind": "chapter",
                    "title": entry_title,
                    "elements": entry_elements,
                }
            )
        return entry_specs

    return [
        {
            "entry_id": "page-001",
            "kind": "page",
            "title": fallback_title,
            "elements": elements,
        }
    ]


def _build_bundle(
    elements: list[dict[str, Any]],
    *,
    out_path: Path,
    module_id: str,
    run_id: Optional[str],
    book_title: str,
    book_author: str,
) -> dict[str, Any]:
    package_title = _metadata_value(elements, "epub_title")
    package_creator = _metadata_value(elements, "epub_creator")
    document_title = book_title.strip() or package_title or _fallback_document_title(elements, out_path.stem)
    creator = book_author.strip() or package_creator
    entry_specs = _entry_specs(elements, document_title)
    return write_bundle(
        entry_specs=entry_specs,
        source_elements=elements,
        out_path=out_path,
        module_id=module_id,
        run_id=run_id,
        document_title=document_title,
        creator=creator,
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

    module_id = "epub_elements_to_bundle_v1"
    logger = ProgressLogger(
        state_path=args.state_file,
        progress_path=args.progress_file,
        run_id=args.run_id,
    )
    logger.log("epub_bundle", "running", message=f"Loading {args.input}", module_id=module_id)

    elements = list(read_jsonl(args.input))
    if not elements:
        raise SystemExit("No EPUB elements found; cannot build bundle")

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
        "epub_bundle",
        "done",
        current=report["entry_count"],
        total=report["entry_count"],
        message=(
            f'Built EPUB bundle with {report["entry_count"]} entries and '
            f'{report["provenance_row_count"]} provenance rows'
        ),
        artifact=str(out_path),
        module_id=module_id,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
