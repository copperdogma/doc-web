from __future__ import annotations

from pathlib import Path
from typing import Any

from pypdf import PdfReader

from doc_web.preview_support import (
    PreviewBlock,
    PreviewEntry,
    collapse_text,
    paragraphs_from_text,
)


def pdf_preview(
    *,
    source_path: Path,
    max_sample_units: int,
    max_chars_per_block: int,
) -> tuple[
    list[PreviewEntry],
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[str],
    str,
]:
    reader = PdfReader(str(source_path))
    page_count = len(reader.pages)
    sample_count = min(max_sample_units, page_count)
    metadata = reader.metadata or {}
    metadata_title = (
        collapse_text(str(metadata.get("/Title") or ""))
        or source_path.stem.replace("-", " ").replace("_", " ").title()
    )

    entries: list[PreviewEntry] = []
    included_units: list[dict[str, Any]] = []
    skipped_units: list[dict[str, Any]] = []
    warnings: list[str] = []
    sample_chars = 0

    for page_index in range(1, sample_count + 1):
        text = reader.pages[page_index - 1].extract_text() or ""
        paragraphs = paragraphs_from_text(text, max_chars_per_block=max_chars_per_block)
        sample_chars += sum(len(paragraph) for paragraph in paragraphs)
        if not paragraphs:
            continue
        blocks = [
            PreviewBlock(
                kind="paragraph",
                text=paragraph,
                source_element_ids=[f"pdf-page-{page_index}-text-{ordinal:04d}"],
                source_page_number=page_index,
                confidence=1.0,
            )
            for ordinal, paragraph in enumerate(paragraphs, start=1)
        ]
        entries.append(
            PreviewEntry(
                entry_id=f"page-{page_index:03d}",
                kind="page",
                title=f"Page {page_index}",
                blocks=blocks,
                source_pages=[page_index],
            )
        )
        included_units.append(
            {"kind": "page", "identifier": str(page_index), "included": True}
        )

    if not entries:
        warnings.append(
            "No usable text layer was found inside the preview budget; OCR is deferred."
        )
        entries.append(
            PreviewEntry(
                entry_id="page-001",
                kind="page",
                title="Preview Deferred",
                blocks=[],
                source_pages=[1] if page_count else [],
                status_message=(
                    "Preview text is deferred because this PDF has no usable text layer. "
                    "Run full processing to OCR the source pages."
                ),
            )
        )
        skipped_units.extend(
            {
                "kind": "page",
                "identifier": str(page_index),
                "included": False,
                "reason": "no_text_layer",
            }
            for page_index in range(1, page_count + 1)
        )
        coverage_state = "deferred"
    else:
        skipped_units.extend(
            {
                "kind": "page",
                "identifier": str(page_index),
                "included": False,
                "reason": "outside_preview_sample",
            }
            for page_index in range(sample_count + 1, page_count + 1)
        )
        coverage_state = "complete" if not skipped_units else "sampled"

    facts = {
        "format": "pdf",
        "page_count": page_count,
        "sampled_page_count": sample_count,
        "sample_text_chars": sample_chars,
        "text_layer_available": bool(sample_chars),
        "ocr_needed": not bool(sample_chars),
        "metadata_title": metadata_title,
        "metadata_creator": str(metadata.get("/Creator") or "") or None,
    }
    return entries, facts, included_units, skipped_units, warnings, coverage_state
