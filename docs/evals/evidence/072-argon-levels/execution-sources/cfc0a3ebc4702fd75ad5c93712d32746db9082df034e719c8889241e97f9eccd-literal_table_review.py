"""Bounded, source-only review of page HTML tables against page images."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable

from bs4 import BeautifulSoup
from PIL import Image

from doc_web.literal_fidelity import (
    LiteralFidelityReceipt,
    LiteralFidelityReport,
    SourcePageReview,
    TableResolution,
)
from doc_web.literal_tables import _parse, canonical_table_digest, compare_tables
from modules.common.table_source_review import SourceOnlyReader


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _page_number(row: dict[str, Any], key: str, fallback: int) -> int:
    value = row.get(key)
    return value if type(value) is int and value >= 1 else fallback


def _initial_tables(html: str) -> list[str]:
    soup = BeautifulSoup(html or "", "html.parser")
    return [str(table) for table in soup.find_all("table")]


def _validate_table_html(html: str, expected_count: int, *, require_only_tables: bool = False) -> list[str]:
    parsed = _parse(html)
    errors = []
    if len(parsed) != expected_count:
        errors.append(f"table inventory count {len(parsed)} does not match expected {expected_count}")
    for index, table in enumerate(parsed):
        if table["parent_table"] is not None:
            errors.append(f"table {index} is nested")
        if table["issues"]:
            errors.append(f"table {index} has unsafe or incomplete geometry: {table['issues']}")
    if require_only_tables:
        soup = BeautifulSoup(html, "html.parser")
        for text in soup.find_all(string=True):
            if text.strip() and text.find_parent("table") is None:
                errors.append("source HTML contains text outside its table")
                break
    return errors


def _validate_bbox(bbox: list[float], width: int, height: int) -> bool:
    if len(bbox) != 4 or not all(math.isfinite(value) for value in bbox):
        return False
    left, top, right, bottom = bbox
    return 0 <= left < right <= width and 0 <= top < bottom <= height


def _validate_uncertain_cells(review, parsed_table: dict[str, Any]) -> list[str]:
    errors = []
    for uncertain in review.uncertain_cells:
        if uncertain.row >= len(parsed_table["rows"]):
            errors.append(f"uncertain cell row {uncertain.row} is outside reviewed table")
        elif uncertain.cell >= len(parsed_table["rows"][uncertain.row]):
            errors.append(f"uncertain cell {uncertain.row}:{uncertain.cell} is outside reviewed table")
    return errors


def _source_pdf_identity(row: dict[str, Any]):
    candidates = []
    declared_pdf_missing = False
    source_paths = row.get("source") or []
    if isinstance(source_paths, (str, Path)):
        source_paths = [source_paths]
    for raw_path in source_paths:
        try:
            path = Path(raw_path)
            if path.suffix.lower() == ".pdf":
                if path.is_file():
                    candidates.append(path)
                else:
                    declared_pdf_missing = True
        except (TypeError, OSError):
            continue
    if declared_pdf_missing:
        return None, "declared source PDF is missing"
    if not candidates:
        return None, None
    if len(candidates) != 1:
        return None, "multiple source PDFs are ambiguous"
    path = candidates[0]
    try:
        data = path.read_bytes()
    except OSError as exc:
        return None, f"source PDF identity unavailable: {type(exc).__name__}"
    return {"name": path.name, "sha256": _sha256(data)}, None


def _image_evidence(row: dict[str, Any]):
    raw_path = row.get("image")
    try:
        path = Path(raw_path)
        if not path.is_file() or path.is_symlink():
            raise ValueError("page image is missing or symlinked")
        data = path.read_bytes()
        with Image.open(path) as image:
            width, height = image.size
            image.verify()
        if width <= 0 or height <= 0:
            raise ValueError("page image dimensions are invalid")
        return _sha256(data), [width, height], path, None
    except Exception as exc:
        return _sha256(b""), [0, 0], None, f"page image unavailable: {type(exc).__name__}"


def _report_path(out_path: Path, index: int, logical_page: int, physical_page: int) -> Path:
    directory = out_path.parent / f"{out_path.stem}_reports"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"row-{index:05d}-page-{logical_page:05d}-original-{physical_page:05d}.json"


def review_literal_tables(
    rows: list[dict[str, Any]],
    *,
    out_path: str | Path,
    run_id: str,
    reader: Callable | None = None,
    model: str = "gpt-6-astra",
    max_pages: int = 3,
    max_tables: int = 8,
    max_requests: int = 10,
    budget_usd: float = 15.0,
) -> list[dict[str, Any]]:
    """Review bounded pages and write an immutable report/receipt per page.

    The input HTML is copied through unchanged. A page qualifies only when the
    independent source inventory is complete, safe, certain, and an exact
    text-and-structure match for every initial table.
    """
    if not run_id:
        raise ValueError("A current run ID is required for literal table review")
    if min(max_pages, max_tables, max_requests) < 1 or budget_usd <= 0:
        raise ValueError("Review caps and budget must be positive")
    out_path = Path(out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    reports_dir = out_path.parent / f"{out_path.stem}_reports"
    if out_path.exists() or reports_dir.exists():
        raise FileExistsError("Literal table review requires a fresh output and report directory")
    reader_init_error = None
    if reader is None:
        ledger = out_path.parent / "literal_table_review_ledger.json"
        try:
            reader = SourceOnlyReader(model=model, max_requests=max_requests,
                                      budget_usd=budget_usd, ledger_path=ledger)
        except Exception as exc:
            reader_init_error = f"source-only reader unavailable: {type(exc).__name__}"
            reader = None

    output = []
    reviewed_page_count = 0
    reviewed_table_count = 0
    request_count = 0
    for index, original in enumerate(rows):
        row = dict(original)
        html = row.get("html") or ""
        raw_html = row.get("raw_html") or ""
        logical = _page_number(row, "page_number", _page_number(row, "page", index + 1))
        physical = _page_number(row, "original_page_number", _page_number(row, "page", logical))
        image_sha, dimensions, image_path, image_error = _image_evidence(row)
        source_pdf, source_error = _source_pdf_identity(row)
        initial_tables = _initial_tables(html)
        initial_geometry_errors = _validate_table_html(html, len(initial_tables))
        errors = [message for message in (image_error, source_error, reader_init_error) if message]
        errors.extend(initial_geometry_errors)
        request_records: list[dict[str, Any]] = []

        source_review = None
        cap_error = None
        preflight_fatal = bool(image_error or source_error or initial_geometry_errors)
        if reviewed_page_count >= max_pages:
            cap_error = f"page review cap reached ({max_pages})"
        elif reviewed_table_count + len(initial_tables) > max_tables:
            cap_error = f"table review cap exceeded ({max_tables})"
        elif request_count >= max_requests:
            cap_error = f"request cap reached ({max_requests})"
        elif preflight_fatal:
            pass
        elif image_path is not None and reader is not None:
            try:
                reviewed_page_count += 1
                request_count += 1
                source_review = SourcePageReview.model_validate(reader(str(image_path), request_records))
            except Exception as exc:
                errors.append(f"source-only review failed: {type(exc).__name__}")
        elif image_path is not None:
            errors.append(reader_init_error or "source-only reader is unavailable")
        else:
            errors.append("source-only review skipped because the page image is unavailable")
        if cap_error:
            errors.append(cap_error)

        table_results = []
        if source_review is not None:
            source_reviews = source_review.tables
            if source_review.source_table_count != len(initial_tables):
                errors.append(
                    f"source table inventory mismatch: initial={len(initial_tables)}, "
                    f"source={source_review.source_table_count}"
                )
            for table_index in range(max(len(initial_tables), len(source_reviews))):
                initial = initial_tables[table_index] if table_index < len(initial_tables) else ""
                if table_index >= len(source_reviews):
                    errors.append(f"initial table {table_index} has no source review")
                    continue
                review = source_reviews[table_index]
                bbox = list(review.bbox)
                comparison = compare_tables(initial, review.html)
                table_errors = []
                if table_index >= len(initial_tables):
                    table_errors.append("source table has no corresponding initial table")
                if not _validate_bbox(bbox, dimensions[0], dimensions[1]):
                    table_errors.append("source table bbox is non-finite, empty, or outside the page image")
                source_html_errors = _validate_table_html(review.html, 1, require_only_tables=True)
                table_errors.extend(source_html_errors)
                source_parsed = _parse(review.html)
                if len(source_parsed) == 1:
                    table_errors.extend(_validate_uncertain_cells(review, source_parsed[0]))
                if review.uncertain_cells:
                    table_errors.append(f"source review reports {len(review.uncertain_cells)} uncertain cells")
                if not comparison["pass"]:
                    table_errors.append(
                        f"initial OCR differs from source review: text_mismatches="
                        f"{comparison['text_mismatch_count']}, structure_mismatches="
                        f"{comparison['structure_mismatch_count']}"
                    )
                decision = "initial_agrees_B" if not table_errors else "unresolved"
                reason = "complete certain exact source agreement" if not table_errors else "; ".join(table_errors)
                table_results.append(TableResolution(
                    table=table_index,
                    bbox=bbox,
                    initial_html=initial,
                    review=review,
                    comparison=comparison,
                    decision=decision,
                    reason=reason,
                ))
                if table_errors:
                    errors.extend(f"table {table_index}: {message}" for message in table_errors)
        elif cap_error is None and image_path is None:
            # Failed page-image validation still consumes its page slot.
            reviewed_page_count += 1
        observed_table_count = max(
            len(initial_tables),
            source_review.source_table_count if source_review is not None else 0,
        )
        if cap_error is None and reviewed_page_count <= max_pages:
            if reviewed_table_count + observed_table_count > max_tables:
                errors.append(f"source table inventory exceeds table review cap ({max_tables})")
            reviewed_table_count += observed_table_count
        unresolved_count = sum(table.decision == "unresolved" for table in table_results)
        if source_review is None:
            unresolved_count = len(initial_tables)
        if errors and unresolved_count == 0:
            unresolved_count = 1
        # A missing B row is also an unresolved initial table, even when no
        # SourceTableReview could be constructed for it.
        unresolved_count = max(unresolved_count, len(initial_tables) - len(table_results))
        status = "verified" if not errors and source_review is not None and unresolved_count == 0 else "unresolved"
        report = LiteralFidelityReport(
            run_id=run_id,
            upstream_run_id=row.get("run_id") if row.get("run_id") != run_id else None,
            logical_page_number=logical,
            original_page_number=physical,
            source_pdf=source_pdf,
            image_sha256=image_sha,
            image_dimensions=dimensions,
            initial_raw_html_sha256=_sha256(raw_html.encode("utf-8")),
            reviewed_table_sequence_sha256=canonical_table_digest(html),
            status=status,
            table_count=len(initial_tables),
            unresolved_count=unresolved_count,
            tables=table_results,
            errors=errors,
            requests=request_records,
        )
        report_path = _report_path(out_path, index, logical, physical)
        report_bytes = (json.dumps(report.model_dump(mode="json"), ensure_ascii=False,
                                   sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        report_path.write_bytes(report_bytes)
        receipt = LiteralFidelityReceipt(
            run_id=run_id,
            status=status,
            logical_page_number=logical,
            original_page_number=physical,
            image_sha256=image_sha,
            source_pdf_sha256=source_pdf["sha256"] if source_pdf else None,
            reviewed_table_sequence_sha256=report.reviewed_table_sequence_sha256,
            report_path=str(report_path.resolve()),
            report_sha256=_sha256(report_bytes),
            table_count=len(initial_tables),
            unresolved_count=unresolved_count,
        )
        row["run_id"] = run_id
        row["literal_fidelity"] = receipt.model_dump(mode="json")
        output.append(row)

    from modules.common.utils import save_jsonl

    save_jsonl(str(out_path), output)
    return output
