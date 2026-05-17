from __future__ import annotations

import subprocess
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from pypdf import PdfReader

from doc_web.preview_support import (
    PreviewBlock,
    PreviewEntry,
    PreviewTimeout,
    collapse_text,
    paragraphs_from_text,
)


PDF_OCR_ENGINE = "tesseract"
PDF_OCR_RASTERIZER = "pdftoppm-singlefile"
PDF_OCR_RASTER_DPI = 200
PDF_OCR_TIMEOUT_SECONDS = 3.0
PDF_OCR_MAX_DIMENSION = 2200
PDF_OCR_MIN_PAGE_BUDGET_SECONDS = 1.0


class PdfRasterizationError(PreviewTimeout):
    """Raised when a PDF page cannot be rasterized for fallback OCR."""

    def __init__(
        self,
        message: str,
        *,
        failure_reason: str = "pdf_rasterization_failed",
    ) -> None:
        super().__init__(message)
        self.failure_reason = failure_reason


def _portable_ocr_error(exc: Exception) -> str:
    return f"{type(exc).__name__}: PDF OCR failed"


def _rasterize_pdf_page(
    source_path: Path,
    page_index: int,
    out_dir: Path,
    *,
    dpi: int = PDF_OCR_RASTER_DPI,
    timeout_seconds: float = PDF_OCR_TIMEOUT_SECONDS,
) -> Path:
    prefix = out_dir / f"page-{page_index:03d}"
    expected = prefix.with_suffix(".png")
    cmd = [
        "pdftoppm",
        "-png",
        "-r",
        str(dpi),
        "-f",
        str(page_index),
        "-l",
        str(page_index),
        "-singlefile",
        str(source_path),
        str(prefix),
    ]
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except OSError:
        raise PdfRasterizationError(
            f"pdftoppm could not be started while rasterizing PDF page {page_index}",
            failure_reason="pdf_rasterization_start_failed",
        ) from None
    except subprocess.TimeoutExpired:
        raise PdfRasterizationError(
            f"pdftoppm timed out while rasterizing PDF page {page_index}",
            failure_reason="pdf_rasterization_timeout",
        ) from None
    if proc.returncode != 0:
        raise PdfRasterizationError(
            "pdftoppm failed while rasterizing PDF page "
            f"{page_index} with exit code {proc.returncode}",
            failure_reason="pdf_rasterization_failed",
        )
    if not expected.exists():
        raise PdfRasterizationError(
            f"did not produce expected single-file raster for page {page_index}",
            failure_reason="pdf_rasterization_missing_output",
        )
    return expected


def _ocr_pdf_page(
    source_path: Path,
    page_index: int,
    *,
    timeout_seconds: float = PDF_OCR_TIMEOUT_SECONDS,
    max_dimension: int = PDF_OCR_MAX_DIMENSION,
) -> str:
    from PIL import Image, ImageOps
    import pytesseract

    with TemporaryDirectory(prefix="doc-web-preview-pdf-page-") as temp_dir:
        image_path = _rasterize_pdf_page(
            source_path,
            page_index,
            Path(temp_dir),
            timeout_seconds=timeout_seconds,
        )
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


def pdf_preview(
    *,
    source_path: Path,
    max_sample_units: int,
    max_chars_per_block: int,
    ocr_deadline_at: float | None = None,
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
    metadata_title = collapse_text(str(metadata.get("/Title") or "")) or None

    entries: list[PreviewEntry] = []
    included_units: list[dict[str, Any]] = []
    skipped_units: list[dict[str, Any]] = []
    warnings: list[str] = []
    sample_chars = 0
    text_layer_chars = 0
    ocr_text_chars = 0
    text_layer_pages: list[int] = []
    ocr_pages: list[int] = []
    textless_sampled_pages: list[int] = []
    included_pages: set[int] = set()
    sampled_page_failures = False
    ocr_errors: list[dict[str, str]] = []

    for page_index in range(1, sample_count + 1):
        text = reader.pages[page_index - 1].extract_text() or ""
        paragraphs = paragraphs_from_text(text, max_chars_per_block=max_chars_per_block)
        paragraph_chars = sum(len(paragraph) for paragraph in paragraphs)
        sample_chars += paragraph_chars
        text_layer_chars += paragraph_chars
        if not paragraphs:
            textless_sampled_pages.append(page_index)
            page_ocr_timeout = PDF_OCR_TIMEOUT_SECONDS
            if ocr_deadline_at is not None:
                remaining_seconds = ocr_deadline_at - time.perf_counter()
                if remaining_seconds < PDF_OCR_MIN_PAGE_BUDGET_SECONDS:
                    sampled_page_failures = True
                    skipped_units.append(
                        {
                            "kind": "page",
                            "identifier": str(page_index),
                            "included": False,
                            "reason": "preview_ocr_budget_exhausted",
                        }
                    )
                    continue
                page_ocr_timeout = min(PDF_OCR_TIMEOUT_SECONDS, remaining_seconds / 2)
            try:
                text = _ocr_pdf_page(
                    source_path,
                    page_index,
                    timeout_seconds=page_ocr_timeout,
                )
            except PdfRasterizationError:
                raise
            except Exception as exc:  # pragma: no cover - depends on local OCR runtime
                sampled_page_failures = True
                ocr_errors.append(
                    {"page": str(page_index), "error": _portable_ocr_error(exc)}
                )
                skipped_units.append(
                    {
                        "kind": "page",
                        "identifier": str(page_index),
                        "included": False,
                        "reason": "preview_ocr_failed",
                    }
                )
                continue
            paragraphs = paragraphs_from_text(
                text, max_chars_per_block=max_chars_per_block
            )
            paragraph_chars = sum(len(paragraph) for paragraph in paragraphs)
            ocr_text_chars += paragraph_chars
            sample_chars += paragraph_chars
            if not paragraphs:
                sampled_page_failures = True
                skipped_units.append(
                    {
                        "kind": "page",
                        "identifier": str(page_index),
                        "included": False,
                        "reason": "no_preview_ocr_text",
                    }
                )
                continue
            source_kind = "ocr"
            confidence = None
            ocr_pages.append(page_index)
        else:
            source_kind = "text"
            confidence = 1.0
            text_layer_pages.append(page_index)
        included_pages.add(page_index)
        blocks = [
            PreviewBlock(
                kind="paragraph",
                text=paragraph,
                source_element_ids=[
                    f"pdf-page-{page_index}-{source_kind}-{ordinal:04d}"
                ],
                source_page_number=page_index,
                confidence=confidence,
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
        already_skipped_pages = {
            str(unit.get("identifier"))
            for unit in skipped_units
            if unit.get("kind") == "page"
        }
        skipped_units.extend(
            {
                "kind": "page",
                "identifier": str(page_index),
                "included": False,
                "reason": "no_text_layer",
            }
            for page_index in range(1, page_count + 1)
            if str(page_index) not in already_skipped_pages
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
        if len(included_pages) == page_count and not sampled_page_failures:
            coverage_state = "complete"
        elif any(
            unit.get("reason")
            in {
                "preview_ocr_failed",
                "no_preview_ocr_text",
                "preview_ocr_budget_exhausted",
            }
            for unit in skipped_units
        ):
            coverage_state = "partial"
        else:
            coverage_state = "sampled"
        if ocr_pages:
            warnings.append(
                f"Preview OCR fallback read {len(ocr_pages)} sampled PDF page(s)."
            )
        if ocr_errors:
            warnings.append("Some sampled PDF pages could not be OCRed during preview.")
        if any(
            unit.get("reason") == "preview_ocr_budget_exhausted"
            for unit in skipped_units
        ):
            warnings.append(
                "Preview OCR stopped early to preserve the hard preview timeout."
            )

    facts = {
        "format": "pdf",
        "page_count": page_count,
        "sampled_page_count": sample_count,
        "sample_text_chars": sample_chars,
        "text_layer_text_chars": text_layer_chars,
        "ocr_text_chars": ocr_text_chars,
        "text_layer_pages": text_layer_pages,
        "ocr_pages": ocr_pages,
        "textless_sampled_pages": textless_sampled_pages,
        "text_layer_available": bool(text_layer_chars),
        "ocr_needed": bool(textless_sampled_pages) or not bool(text_layer_chars),
        "ocr_engine": PDF_OCR_ENGINE if textless_sampled_pages else None,
        "ocr_rasterizer": PDF_OCR_RASTERIZER if textless_sampled_pages else None,
        "ocr_raster_dpi": PDF_OCR_RASTER_DPI if textless_sampled_pages else None,
        "ocr_timeout_seconds": (
            PDF_OCR_TIMEOUT_SECONDS if textless_sampled_pages else None
        ),
        "ocr_max_dimension": PDF_OCR_MAX_DIMENSION if textless_sampled_pages else None,
        "ocr_errors": ocr_errors,
        "metadata_title": metadata_title,
        "metadata_creator": str(metadata.get("/Creator") or "") or None,
    }
    return entries, facts, included_units, skipped_units, warnings, coverage_state
