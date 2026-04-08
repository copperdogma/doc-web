#!/usr/bin/env python3
"""Build a doc-web bundle directly from PPTX Unstructured elements."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Optional

from modules.common.office_native_bundle import collapse_text, source_artifact, write_bundle
from modules.common.utils import ProgressLogger, ensure_dir, read_jsonl, save_json


UPPERCASE_TOKENS = {"docx", "html", "ocr", "pdf", "pptx", "xlsx"}


def _normalize_pptx_elements(elements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []

    for element in elements:
        normalized_element = dict(element)
        metadata = dict(element.get("metadata", {}) or {})
        normalized_element["metadata"] = metadata

        element_type = normalized_element.get("type")
        category_depth = metadata.get("category_depth")
        if (
            element_type == "Title"
            and isinstance(category_depth, int)
            and category_depth > 0
            and metadata.get("parent_id")
        ):
            normalized_element["type"] = "ListItem"

        normalized.append(normalized_element)

    return normalized


def _fallback_deck_title(elements: list[dict[str, Any]], fallback: str) -> str:
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


def _slide_title(slide_number: int, elements: list[dict[str, Any]]) -> str:
    for element in elements:
        metadata = element.get("metadata", {}) or {}
        if (
            element.get("type") == "Title"
            and metadata.get("category_depth") == 0
            and collapse_text(element.get("text", ""))
        ):
            return collapse_text(element.get("text", ""))
    for element in elements:
        text = collapse_text(element.get("text", ""))
        if text:
            return text[:120]
    return f"Slide {slide_number}"


def _group_by_slide(elements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: list[dict[str, Any]] = []
    by_slide: dict[int, dict[str, Any]] = {}
    next_fallback_slide = 1

    for element in elements:
        metadata = element.get("metadata", {}) or {}
        raw_slide = metadata.get("page_number")
        slide_number = raw_slide if isinstance(raw_slide, int) and raw_slide >= 1 else next_fallback_slide
        next_fallback_slide = max(next_fallback_slide, slide_number + 1)

        if slide_number not in by_slide:
            entry = {
                "entry_id": f"page-{slide_number:03d}",
                "kind": "page",
                "title": "",
                "elements": [],
                "source_pages": [slide_number],
            }
            grouped.append(entry)
            by_slide[slide_number] = entry

        by_slide[slide_number]["elements"].append(element)

    for entry in grouped:
        slide_number = entry["source_pages"][0]
        entry["title"] = _slide_title(slide_number, entry["elements"])

    return grouped


def _build_bundle(
    elements: list[dict[str, Any]],
    *,
    out_path: Path,
    module_id: str,
    run_id: Optional[str],
    book_title: str,
    book_author: str,
) -> dict[str, Any]:
    normalized_elements = _normalize_pptx_elements(elements)
    entry_specs = _group_by_slide(normalized_elements)
    fallback_title = _fallback_deck_title(normalized_elements, out_path.stem)
    document_title = book_title.strip() or (
        entry_specs[0]["title"] if entry_specs and entry_specs[0]["title"] else fallback_title
    )
    return write_bundle(
        entry_specs=entry_specs,
        source_elements=normalized_elements,
        out_path=out_path,
        module_id=module_id,
        run_id=run_id,
        document_title=document_title,
        creator=book_author,
        include_source_page_numbers=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Input unstructured elements JSONL path")
    parser.add_argument("--out", required=True, help="Output report JSON path")
    parser.add_argument("--book-title", default="", help="Optional deck title override")
    parser.add_argument("--book-author", default="", help="Optional deck author override")
    parser.add_argument("--run-id", dest="run_id", default=None, help="Driver compatibility")
    parser.add_argument("--state-file", dest="state_file", default=None, help="Driver compatibility")
    parser.add_argument("--progress-file", dest="progress_file", default=None, help="Driver compatibility")
    args = parser.parse_args()

    module_id = "pptx_elements_to_bundle_v1"
    logger = ProgressLogger(
        state_path=args.state_file,
        progress_path=args.progress_file,
        run_id=args.run_id,
    )
    logger.log("pptx_bundle", "running", message=f"Loading {args.input}", module_id=module_id)

    elements = list(read_jsonl(args.input))
    if not elements:
        raise SystemExit("No PPTX elements found; cannot build bundle")

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
        "pptx_bundle",
        "done",
        current=report["entry_count"],
        total=report["entry_count"],
        message=(
            f'Built PPTX bundle with {report["entry_count"]} entries and '
            f'{report["provenance_row_count"]} provenance rows'
        ),
        artifact=str(out_path),
        module_id=module_id,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
