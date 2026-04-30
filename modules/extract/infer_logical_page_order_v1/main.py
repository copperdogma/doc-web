#!/usr/bin/env python3
"""Infer reader-order page images from split spread manifests.

This module is intentionally generic for imposed, print-ready PDFs. It uses
printed spread-label signals from the source PDF text layer when available,
then emits both an ordered page_image_v1 manifest and an inspectable page-map
sidecar. It does not encode document titles or one-off page moves.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from modules.common.utils import ProgressLogger, save_json, save_jsonl


MODULE_ID = "infer_logical_page_order_v1"
DEFAULT_LABEL_RE = r"(?P<left>\d{1,4})\s*-\s*(?P<right>\d{1,4})"


@dataclass(frozen=True)
class SpreadLabel:
    physical_sheet: int
    pair_label: str
    left_printed_page: int
    right_printed_page: int
    source_line: str
    confidence: float
    reason: str


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _layout_text_from_pdf(pdf_path: Path | None) -> str:
    if not pdf_path:
        return ""
    if not pdf_path.exists():
        return ""
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return result.stdout


def _score_candidate(line_index: int, line_count: int, line: str) -> tuple[float, str]:
    normalized = line.casefold()
    footer_band = line_index >= max(0, line_count - 12)
    score = 0.0
    reasons: list[str] = []
    if footer_band:
        score += 0.40
        reasons.append("footer-band")
    if any(token in normalized for token in ("indd", "page", "sheet", "spread")):
        score += 0.35
        reasons.append("print-label-context")
    if len(line.strip()) <= 120:
        score += 0.15
        reasons.append("short-label-line")
    # Later labels are usually more likely to be footer/page metadata than body
    # prose cross-references when all other evidence is equal.
    score += min(0.10, line_index / max(1, line_count) * 0.10)
    return min(score, 0.98), ",".join(reasons) or "weak-text-match"


def parse_spread_labels(layout_text: str, label_regex: str = DEFAULT_LABEL_RE) -> dict[int, SpreadLabel]:
    pattern = re.compile(label_regex, re.IGNORECASE)
    labels: dict[int, SpreadLabel] = {}

    for physical_sheet, page_text in enumerate(layout_text.split("\f"), start=1):
        lines = [line.rstrip() for line in page_text.splitlines() if line.strip()]
        if not lines:
            continue

        candidates: list[tuple[float, int, re.Match[str], str, str]] = []
        for line_index, line in enumerate(lines):
            for match in pattern.finditer(line):
                try:
                    left_page = int(match.group("left"))
                    right_page = int(match.group("right"))
                except (IndexError, ValueError):
                    continue
                if left_page == right_page:
                    continue
                confidence, reason = _score_candidate(line_index, len(lines), line)
                # Reject very weak body-text page ranges unless no stronger
                # candidate exists. The caller will still see low confidence.
                if confidence < 0.25:
                    continue
                candidates.append((confidence, line_index, match, line.strip(), reason))

        if not candidates:
            continue

        confidence, _line_index, match, source_line, reason = sorted(
            candidates,
            key=lambda item: (item[0], item[1]),
        )[-1]
        left_page = int(match.group("left"))
        right_page = int(match.group("right"))
        labels[physical_sheet] = SpreadLabel(
            physical_sheet=physical_sheet,
            pair_label=f"{left_page}-{right_page}",
            left_printed_page=left_page,
            right_printed_page=right_page,
            source_line=source_line,
            confidence=round(confidence, 3),
            reason=reason,
        )

    return labels


def _coerce_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def build_logical_page_map(
    split_rows: list[dict[str, Any]],
    labels: dict[int, SpreadLabel],
    *,
    run_id: str | None,
    split_manifest: Path,
    pdf: Path | None,
    min_confidence: float,
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []

    for physical_order_index, row in enumerate(split_rows, start=1):
        physical_sheet = _coerce_int(row.get("original_page_number")) or _coerce_int(row.get("page")) or physical_order_index
        spread_side = row.get("spread_side")
        label = labels.get(physical_sheet)
        logical_page = None
        confidence = 0.35
        reason = "unresolved: no printed label matched this page"

        if label and spread_side == "L":
            logical_page = label.left_printed_page
            confidence = label.confidence
            reason = f"printed spread label mapped left half ({label.reason})"
        elif label and spread_side == "R":
            logical_page = label.right_printed_page
            confidence = label.confidence
            reason = f"printed spread label mapped right half ({label.reason})"
        elif not spread_side:
            logical_page = _coerce_int(row.get("page_number")) or physical_order_index
            confidence = 0.75
            reason = "single page or unsplit page preserved in physical order"

        if logical_page is None:
            issues.append(
                {
                    "type": "missing_printed_page_label",
                    "physical_sheet": physical_sheet,
                    "spread_side": spread_side,
                    "message": "No printed page label could be mapped to this split half.",
                }
            )
        elif confidence < min_confidence:
            issues.append(
                {
                    "type": "low_confidence_mapping",
                    "logical_page": logical_page,
                    "physical_sheet": physical_sheet,
                    "spread_side": spread_side,
                    "confidence": confidence,
                    "message": "Mapping exists but is below the configured confidence threshold.",
                }
            )

        entries.append(
            {
                "logical_page": logical_page,
                "physical_order_index": physical_order_index,
                "physical_sheet": physical_sheet,
                "spread_side": spread_side,
                "split_manifest_page_number": row.get("page_number"),
                "source_page_image": row.get("image"),
                "source_pdf": (row.get("source") or [str(pdf) if pdf else None])[0],
                "printed_spread_label": label.pair_label if label else None,
                "label_source_line": label.source_line if label else None,
                "confidence": confidence,
                "reason": reason,
                "source_manifest_row": row,
            }
        )

    entries.sort(
        key=lambda entry: (
            entry["logical_page"] is None,
            entry["logical_page"] if entry["logical_page"] is not None else 999999,
            entry["physical_sheet"],
            entry.get("spread_side") or "",
        )
    )

    seen_pages = [entry["logical_page"] for entry in entries if isinstance(entry["logical_page"], int)]
    duplicate_pages = sorted(page for page, count in Counter(seen_pages).items() if count > 1)
    if seen_pages and min(seen_pages) == 1:
        expected_pages = list(range(1, max(seen_pages) + 1))
        missing_pages = sorted(set(expected_pages) - set(seen_pages))
    else:
        expected_pages = sorted(seen_pages)
        missing_pages = []

    for page in duplicate_pages:
        issues.append(
            {
                "type": "duplicate_logical_page",
                "logical_page": page,
                "message": "Multiple split halves claim the same logical page.",
            }
        )
    if missing_pages:
        issues.append(
            {
                "type": "missing_logical_pages",
                "pages": missing_pages,
                "message": "Printed labels did not produce a continuous logical page set.",
            }
        )

    for order_index, entry in enumerate(entries, start=1):
        entry["logical_order_index"] = order_index

    physical_spreads = [
        {
            "physical_sheet": label.physical_sheet,
            "printed_spread_label": label.pair_label,
            "left_printed_page": label.left_printed_page,
            "right_printed_page": label.right_printed_page,
            "is_cover_or_back_imposition_signal": label.left_printed_page > label.right_printed_page,
            "confidence": label.confidence,
            "source_line": label.source_line,
            "reason": label.reason,
        }
        for label in sorted(labels.values(), key=lambda item: item.physical_sheet)
    ]

    complete = bool(seen_pages) and not missing_pages and not duplicate_pages and len(seen_pages) == len(split_rows)
    return {
        "schema_version": "logical_page_map_v1",
        "module_id": MODULE_ID,
        "run_id": run_id,
        "created_at": _utc(),
        "source": {
            "pdf": str(pdf) if pdf else None,
            "split_manifest": str(split_manifest),
        },
        "summary": {
            "physical_spread_count": len(physical_spreads),
            "split_page_count": len(split_rows),
            "inferred_logical_page_count": len(seen_pages),
            "expected_logical_page_count": len(expected_pages),
            "missing_logical_pages": missing_pages,
            "duplicate_logical_pages": duplicate_pages,
            "complete": complete,
            "confidence": round(min((entry["confidence"] for entry in entries), default=0.0), 3),
            "issues_count": len(issues),
        },
        "physical_spreads": physical_spreads,
        "logical_pages": entries,
        "issues": issues,
    }


def build_reordered_manifest(page_map: dict[str, Any], *, run_id: str | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    pages = page_map["logical_pages"]
    continuous_labels = (
        page_map["summary"].get("complete") is True
        and all(entry.get("logical_page") == idx for idx, entry in enumerate(pages, start=1))
    )
    for index, entry in enumerate(pages, start=1):
        source_row = entry["source_manifest_row"]
        logical_page = entry.get("logical_page")
        output_page = logical_page if continuous_labels and isinstance(logical_page, int) else index
        rows.append(
            {
                "schema_version": "page_image_v1",
                "module_id": MODULE_ID,
                "run_id": run_id,
                "source": source_row.get("source"),
                "created_at": _utc(),
                "page": output_page,
                "page_number": output_page,
                "original_page_number": entry.get("physical_sheet"),
                "image": source_row.get("image"),
                "spread_side": entry.get("spread_side"),
            }
        )
    return rows


def _write_report(path: Path, page_map: dict[str, Any], ordered_manifest_path: Path) -> None:
    summary = page_map["summary"]
    lines = [
        "# Logical Page Order Report",
        "",
        f"- Ordered manifest: `{ordered_manifest_path.name}`",
        f"- Split pages: `{summary['split_page_count']}`",
        f"- Inferred logical pages: `{summary['inferred_logical_page_count']}`",
        f"- Complete: `{summary['complete']}`",
        f"- Minimum confidence: `{summary['confidence']}`",
        f"- Issues: `{summary['issues_count']}`",
        "",
    ]
    if page_map["issues"]:
        lines.append("## Issues")
        lines.extend(f"- `{issue['type']}`: {issue.get('message', '')}" for issue in page_map["issues"])
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Infer logical page order from a split page_image_v1 manifest.")
    parser.add_argument("--pages", required=True, help="Split page_image_v1 manifest JSONL")
    parser.add_argument("--pdf", help="Source PDF. Used only for generic printed-label detection.")
    parser.add_argument("--outdir", required=True, help="Output directory")
    parser.add_argument("--out", default="pages_logical_manifest.jsonl", help="Ordered page_image_v1 manifest filename")
    parser.add_argument("--label-regex", default=DEFAULT_LABEL_RE, help="Regex with named groups 'left' and 'right'")
    parser.add_argument("--min-confidence", type=float, default=0.70, help="Minimum mapping confidence before review flagging")
    parser.add_argument("--fail-on-uncertain", action="store_true", help="Exit nonzero when any mapping issue is detected")
    parser.add_argument("--progress-file")
    parser.add_argument("--state-file")
    parser.add_argument("--run-id")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    out_path = outdir / args.out
    map_path = outdir / "logical_page_map.json"
    report_path = outdir / "logical_page_order_report.md"

    logger = ProgressLogger(state_path=args.state_file, progress_path=args.progress_file, run_id=args.run_id)
    logger.log("extract", "running", message="Inferring logical page order", module_id=MODULE_ID)

    split_manifest = Path(args.pages)
    rows = _read_jsonl(split_manifest)
    pdf_path = Path(args.pdf) if args.pdf else None
    labels = parse_spread_labels(_layout_text_from_pdf(pdf_path), args.label_regex)
    page_map = build_logical_page_map(
        rows,
        labels,
        run_id=args.run_id,
        split_manifest=split_manifest,
        pdf=pdf_path,
        min_confidence=args.min_confidence,
    )
    ordered_rows = build_reordered_manifest(page_map, run_id=args.run_id)

    # Remove bulky source rows from the public page-map sidecar after the ordered
    # manifest has been built.
    for entry in page_map["logical_pages"]:
        entry.pop("source_manifest_row", None)

    save_jsonl(str(out_path), ordered_rows)
    save_json(str(map_path), page_map)
    _write_report(report_path, page_map, out_path)

    logger.log(
        "extract",
        "done",
        current=len(ordered_rows),
        total=len(ordered_rows),
        message=f"Inferred {len(ordered_rows)} logical pages; issues={page_map['summary']['issues_count']}",
        artifact=str(out_path),
        module_id=MODULE_ID,
        schema_version="page_image_v1",
        extra={"logical_page_map": str(map_path), "summary": page_map["summary"]},
    )

    if args.fail_on_uncertain and page_map["issues"]:
        raise SystemExit(f"Logical page order has {len(page_map['issues'])} issue(s); see {map_path}")


if __name__ == "__main__":
    main()
