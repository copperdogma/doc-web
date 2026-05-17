from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from doc_web.preview_support import (
    PreviewBlock,
    PreviewEntry,
    collapse_text,
    paragraphs_from_text,
)


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".bmp"}


def _natural_key(path: Path) -> list[int | str]:
    parts: list[int | str] = []
    for piece in re.split(r"(\d+)", path.name.lower()):
        if piece.isdigit():
            parts.append(int(piece))
        elif piece:
            parts.append(piece)
    return parts


def _portable_ocr_error(exc: Exception) -> str:
    return f"{type(exc).__name__}: image OCR failed"


def image_directory_preview(
    *,
    source_path: Path,
    max_sample_units: int,
    max_chars_per_block: int,
    ocr_sample_limit: int | None = None,
    ocr_timeout_seconds: float = 2.0,
    ocr_max_dimension: int = 1600,
) -> tuple[
    list[PreviewEntry],
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[str],
    str,
]:
    image_paths = sorted(
        (
            path
            for path in source_path.iterdir()
            if path.suffix.lower() in IMAGE_SUFFIXES
        ),
        key=_natural_key,
    )
    sample_limit = (
        ocr_sample_limit if ocr_sample_limit is not None else max_sample_units
    )
    sample_count = min(max_sample_units, sample_limit, len(image_paths))
    total_bytes = sum(path.stat().st_size for path in image_paths)

    entries: list[PreviewEntry] = []
    included_units: list[dict[str, Any]] = []
    skipped_units: list[dict[str, Any]] = []
    ocr_errors: list[dict[str, str]] = []
    ocr_text_chars = 0
    attempted_pages: set[int] = set()
    included_pages: set[int] = set()

    candidate_indexes = list(range(sample_count))
    if len(candidate_indexes) > 1:
        candidate_indexes = [1, 0, *candidate_indexes[2:]]

    for candidate_index in candidate_indexes:
        page_index = candidate_index + 1
        image_path = image_paths[candidate_index]
        attempted_pages.add(page_index)
        try:
            text = _ocr_image(
                image_path,
                timeout_seconds=ocr_timeout_seconds,
                max_dimension=ocr_max_dimension,
            )
        except Exception as exc:  # pragma: no cover - depends on local OCR runtime
            text = ""
            ocr_errors.append(
                {"page": str(page_index), "error": _portable_ocr_error(exc)}
            )

        paragraphs = paragraphs_from_text(text, max_chars_per_block=max_chars_per_block)
        ocr_text_chars += sum(len(paragraph) for paragraph in paragraphs)
        if not paragraphs:
            continue

        included_pages.add(page_index)
        blocks = [
            PreviewBlock(
                kind="paragraph",
                text=paragraph,
                source_page_number=page_index,
                source_element_ids=[f"image-page-{page_index:03d}-ocr-{ordinal:04d}"],
            )
            for ordinal, paragraph in enumerate(paragraphs, start=1)
        ]
        entries.append(
            PreviewEntry(
                entry_id=f"page-{page_index:03d}",
                kind="page",
                title=f"Image {page_index}",
                blocks=blocks,
                source_pages=[page_index],
            )
        )
        included_units.append(
            {"kind": "page", "identifier": str(page_index), "included": True}
        )
        if ocr_text_chars >= 50:
            break

    for index in range(1, len(image_paths) + 1):
        if index in included_pages:
            continue
        reason = (
            "no_preview_ocr_text"
            if index in attempted_pages
            else "outside_preview_sample"
        )
        skipped_units.append(
            {
                "kind": "page",
                "identifier": str(index),
                "included": False,
                "reason": reason,
            }
        )

    warnings: list[str] = []
    if entries:
        coverage_state = "complete" if len(entries) == len(image_paths) else "sampled"
        if len(entries) != len(image_paths):
            warnings.append(
                f"Preview OCR sampled {len(attempted_pages)} of {len(image_paths)} images."
            )
    else:
        coverage_state = "deferred"
        warnings.append(
            "Image-directory preview OCR found no usable text inside the preview budget."
        )
        entries.append(
            PreviewEntry(
                entry_id="page-001",
                kind="page",
                title="Preview Deferred",
                blocks=[],
                source_pages=[1] if image_paths else [],
                status_message=(
                    "Preview text is deferred because this input is an image directory. "
                    "Run full processing to OCR the source images."
                ),
            )
        )
    if ocr_errors:
        warnings.append("Some sampled images could not be OCRed during preview.")

    facts = {
        "format": "image_directory",
        "image_count": len(image_paths),
        "sampled_image_count": len(attempted_pages),
        "ocr_sampled_image_count": len(attempted_pages),
        "ocr_text_chars": ocr_text_chars,
        "ocr_engine": "tesseract",
        "ocr_timeout_seconds": ocr_timeout_seconds,
        "ocr_max_dimension": ocr_max_dimension,
        "ocr_errors": ocr_errors,
        "total_image_bytes": total_bytes,
        "text_layer_available": False,
        "ocr_needed": True,
        "metadata_title": "Image Directory Preview",
    }
    return entries, facts, included_units, skipped_units, warnings, coverage_state


def _ocr_image(image_path: Path, *, timeout_seconds: float, max_dimension: int) -> str:
    from PIL import Image, ImageOps
    import pytesseract

    with Image.open(image_path) as image:
        image = ImageOps.grayscale(image)
        image.thumbnail((max_dimension, max_dimension))
        return collapse_text(
            pytesseract.image_to_string(
                image,
                timeout=timeout_seconds,
                config="--psm 6",
            )
        )
