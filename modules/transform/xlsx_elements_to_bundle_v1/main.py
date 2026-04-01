#!/usr/bin/env python3
"""Build a doc-web bundle directly from XLSX Unstructured elements."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Optional

from modules.common.office_native_bundle import collapse_text, source_artifact, write_bundle
from modules.common.utils import ProgressLogger, ensure_dir, read_jsonl, save_json


UPPERCASE_TOKENS = {"docx", "html", "ocr", "pdf", "pptx", "xlsx"}


def _group_by_sheet(elements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: list[dict[str, Any]] = []
    by_sheet: dict[str, dict[str, Any]] = {}

    for element in elements:
        metadata = element.get("metadata", {}) or {}
        raw_title = metadata.get("page_name") or metadata.get("worksheet_name")
        title = collapse_text(str(raw_title)) if raw_title else ""
        if not title:
            title = f"Sheet {len(grouped) + 1}"
        if title not in by_sheet:
            entry = {
                "entry_id": f"page-{len(grouped) + 1:03d}",
                "kind": "page",
                "title": title,
                "elements": [],
            }
            grouped.append(entry)
            by_sheet[title] = entry
        by_sheet[title]["elements"].append(element)
    return grouped


def _default_workbook_title(elements: list[dict[str, Any]], fallback: str) -> str:
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


def _build_bundle(
    elements: list[dict[str, Any]],
    *,
    out_path: Path,
    module_id: str,
    run_id: Optional[str],
    book_title: str,
    book_author: str,
) -> dict[str, Any]:
    entry_specs = _group_by_sheet(elements)
    document_title = book_title.strip() or _default_workbook_title(elements, out_path.stem)
    return write_bundle(
        entry_specs=entry_specs,
        source_elements=elements,
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
    parser.add_argument("--book-title", default="", help="Optional workbook title override")
    parser.add_argument("--book-author", default="", help="Optional workbook author override")
    parser.add_argument("--run-id", dest="run_id", default=None, help="Driver compatibility")
    parser.add_argument("--state-file", dest="state_file", default=None, help="Driver compatibility")
    parser.add_argument("--progress-file", dest="progress_file", default=None, help="Driver compatibility")
    args = parser.parse_args()

    module_id = "xlsx_elements_to_bundle_v1"
    logger = ProgressLogger(
        state_path=args.state_file,
        progress_path=args.progress_file,
        run_id=args.run_id,
    )
    logger.log("xlsx_bundle", "running", message=f"Loading {args.input}", module_id=module_id)

    elements = list(read_jsonl(args.input))
    if not elements:
        raise SystemExit("No XLSX elements found; cannot build bundle")

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
        "xlsx_bundle",
        "done",
        current=report["entry_count"],
        total=report["entry_count"],
        message=f'Built XLSX bundle with {report["entry_count"]} entries and {report["provenance_row_count"]} provenance rows',
        artifact=str(out_path),
        module_id=module_id,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
