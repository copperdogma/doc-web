"""Fail-closed table qualification at the HTML publication boundary."""
import hashlib
import json
from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image

from doc_web.literal_fidelity import LiteralFidelityReceipt, LiteralFidelityReport, SourcePageReview
from doc_web.literal_tables import _parse, canonical_table_digest, compare_tables
from modules.common.ocr_request_receipt import require_completed_identity
from modules.common.table_source_review import POLICY


def _require(condition, message):
    if not condition:
        raise ValueError(f"Literal fidelity: {message}")


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _read(path):
    path = Path(path)
    _require(path.is_file() and not path.is_symlink(), f"missing or symlinked evidence: {path}")
    return path.read_bytes()


def _certain_agreement(initial, review):
    return not review.uncertain_cells and compare_tables(initial, review.html)["pass"]


def _validate_report_authority(report, html):
    _require(report.policy_version == "source-only-table-review-v1", "unqualified source-review policy version")
    _require(len(report.requests) == 1, "exactly one independent source-read receipt required")
    request = report.requests[0]
    try:
        require_completed_identity(request)
    except (KeyError, TypeError, RuntimeError) as exc:
        raise ValueError("Literal fidelity: invalid source-read served identity/status") from exc
    _require(request.get("requested_model") == "gpt-6-astra"
             and request.get("image_detail") == "original"
             and request.get("reasoning") == {"effort": "medium"}, "unqualified source-read configuration")
    _require(request.get("submitted_image_sha256") == report.image_sha256, "source-read image identity mismatch")
    _require(request.get("prompt_sha256") == _digest(POLICY.encode("utf-8")), "source-read policy changed")
    schema_sha = _digest(json.dumps(SourcePageReview.model_json_schema(), sort_keys=True).encode("utf-8"))
    _require(request.get("response_schema_sha256") == schema_sha, "source-read schema changed")
    source_review = SourcePageReview.model_validate_json(request.get("raw_response") or "")
    _require(source_review.source_table_count == report.table_count
             and source_review.tables == [table.review for table in report.tables],
             "report differs from independent raw source response")
    initial = _parse(html)
    _require(not any(table["issues"] or table["parent_table"] is not None for table in initial),
             "invalid or nested table geometry")
    _require(report.status == "verified" and report.unresolved_count == 0 and not report.errors,
             "unresolved source review")
    _require(report.table_count == len(initial) == len(report.tables), "incomplete table inventory")
    _require([table.table for table in report.tables] == list(range(len(initial))),
             "table ordering differs from initial OCR")
    initial_html = "".join(table.initial_html for table in report.tables)
    _require(canonical_table_digest(initial_html) == canonical_table_digest(html),
             "reviewed initial table sequence changed")
    width, height = report.image_dimensions
    _require(width > 0 and height > 0, "invalid source image dimensions")
    for table in report.tables:
        x0, y0, x1, y1 = table.bbox
        _require(0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height, "invalid table source bbox")
        _require(table.bbox == table.review.bbox, "table/source-review bbox mismatch")
        _require(len(_parse(table.initial_html)) == 1, "table record is not one complete table")
        _require(table.comparison == compare_tables(table.initial_html, table.review.html),
                 "stored comparison differs from recomputed source agreement")
        if table.decision == "initial_agrees_B":
            _require(_certain_agreement(table.initial_html, table.review), "B lacks certain exact agreement")
        else:
            raise ValueError("Literal fidelity: unresolved table decision")


def validate_literal_fidelity_inputs(pages, *, run_id, required=False):
    """Read and verify every receipt before the builder creates output files."""
    has_receipt = any(page.get("literal_fidelity") is not None for page in pages)
    if not required and not has_receipt:
        return None
    _require(bool(run_id), "qualification requires a run ID")
    qualified = []
    seen = set()
    for page in sorted(pages, key=lambda row: row.get("page_number") or row.get("page")):
        _require(page.get("literal_fidelity") is not None, "missing page receipt")
        receipt = LiteralFidelityReceipt.model_validate(page["literal_fidelity"])
        logical = page.get("page_number") or page.get("page")
        physical = page.get("original_page_number")
        _require(logical not in seen, "duplicate logical page")
        seen.add(logical)
        _require(receipt.run_id == run_id and receipt.logical_page_number == logical
                 and receipt.original_page_number == physical, "receipt page/run identity mismatch")
        _require(receipt.status == "verified" and receipt.unresolved_count == 0, "unresolved receipt")
        image_bytes = _read(page["image"])
        _require(_digest(image_bytes) == receipt.image_sha256, "source image changed")
        report_path = Path(receipt.report_path)
        _require(report_path.is_absolute(), "report path must be absolute")
        report_bytes = _read(report_path)
        _require(_digest(report_bytes) == receipt.report_sha256, "review report changed")
        report = LiteralFidelityReport.model_validate_json(report_bytes)
        for key in ("run_id", "logical_page_number", "original_page_number", "image_sha256",
                    "reviewed_table_sequence_sha256", "table_count", "unresolved_count", "status", "policy_version"):
            _require(getattr(report, key) == getattr(receipt, key), f"report/receipt {key} mismatch")
        with Image.open(page["image"]) as image:
            _require(list(image.size) == report.image_dimensions, "image dimensions changed")
        _require(_digest((page.get("raw_html") or "").encode("utf-8")) == report.initial_raw_html_sha256,
                 "initial OCR raw HTML changed")
        _require(canonical_table_digest(page.get("raw_html") or "") == receipt.reviewed_table_sequence_sha256,
                 "qualified tables differ from initial raw OCR")
        html = page.get("html") or ""
        _require(canonical_table_digest(html) == receipt.reviewed_table_sequence_sha256,
                 "current page table sequence differs from review")
        if report.source_pdf is not None:
            _require(receipt.source_pdf_sha256 == report.source_pdf.sha256, "source PDF receipt mismatch")
            source_paths = page.get("source") or []
            _require(any(Path(path).name == report.source_pdf.name
                         and _digest(_read(path)) == report.source_pdf.sha256 for path in source_paths),
                     "source PDF identity missing or changed")
        else:
            _require(receipt.source_pdf_sha256 is None, "source PDF receipt lacks report identity")
        _validate_report_authority(report, html)
        qualified.append({"receipt": receipt, "report_bytes": report_bytes, "html": html,
                          "image_path": page["image"], "report_path": str(report_path),
                          "source_pdf": report.source_pdf, "source_paths": page.get("source") or []})
    return qualified


def finalize_literal_fidelity_bundle(qualified, *, html_dir, entries, run_id):
    """Recheck final article tables, then copy bound immutable review reports."""
    if qualified is None:
        return None
    html_dir = Path(html_dir)
    expected_html = "".join(item["html"] for item in qualified)
    actual_parts, files = [], []
    for entry in entries:
        path = html_dir / entry["path"]
        data = _read(path)
        soup = BeautifulSoup(data.decode("utf-8"), "html.parser")
        article = soup.select_one("body > article")
        _require(article is not None, "missing final article body")
        actual_parts.append(str(article))
        files.append({"path": entry["path"], "sha256": _digest(data)})
    _require(canonical_table_digest("".join(actual_parts)) == canonical_table_digest(expected_html),
             "final table content/order/geometry differs from qualified initial OCR")
    root = html_dir / "provenance" / "literal-fidelity"
    root.mkdir(parents=True, exist_ok=True)
    reports = []
    for item in qualified:
        receipt = item["receipt"]
        _require(_digest(_read(item["image_path"])) == receipt.image_sha256, "image changed during build")
        _require(_read(item["report_path"]) == item["report_bytes"], "report changed during build")
        if item["source_pdf"] is not None:
            source_pdf = item["source_pdf"]
            _require(any(Path(path).name == source_pdf.name and _digest(_read(path)) == source_pdf.sha256
                         for path in item["source_paths"]), "source PDF changed during build")
        relative = f"provenance/literal-fidelity/page-{receipt.logical_page_number:04d}.json"
        (html_dir / relative).write_bytes(item["report_bytes"])
        reports.append({"path": relative, "sha256": receipt.report_sha256,
                        "logical_page_number": receipt.logical_page_number,
                        "original_page_number": receipt.original_page_number,
                        "table_count": receipt.table_count})
    relative = "provenance/literal-fidelity/qualification.json"
    payload = {"schema_version": "literal_fidelity_bundle_qualification_v1", "run_id": run_id,
               "scope": "table_literal_text", "status": "qualified", "reports": reports,
               "entries": files, "table_sequence_sha256": canonical_table_digest(expected_html)}
    data = (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    (html_dir / relative).write_bytes(data)
    return {"scope": "table_literal_text", "status": "qualified", "qualification_path": relative,
            "qualification_sha256": _digest(data), "reports": reports,
            "page_count": len(reports), "table_count": sum(report["table_count"] for report in reports)}
