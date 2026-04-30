#!/usr/bin/env python3
"""Normalize OCR HTML from graphics-heavy manuals before portioning/building."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from modules.common.utils import ProgressLogger, read_jsonl, save_json, save_jsonl


MODULE_ID = "normalize_graphic_manual_html_v1"


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _title_key(text: str) -> str:
    text = _normalize_ws(text).casefold()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _first_significant_tag(soup: BeautifulSoup):
    for child in soup.contents:
        name = getattr(child, "name", None)
        if name:
            return child
    return None


def _has_class(tag: Any, class_name: str) -> bool:
    return class_name in (tag.get("class") or [])


def _leading_running_head(soup: BeautifulSoup):
    tag = _first_significant_tag(soup)
    if tag and _has_class(tag, "running-head"):
        text = _normalize_ws(tag.get_text(" ", strip=True))
        if text:
            return tag, text
    return None, ""


def _all_heading_keys(rows: list[dict[str, Any]]) -> set[str]:
    keys: set[str] = set()
    for row in rows:
        soup = BeautifulSoup(row.get("html") or row.get("raw_html") or "", "html.parser")
        for tag in soup.find_all(["h1", "h2"]):
            key = _title_key(tag.get_text(" ", strip=True))
            if key:
                keys.add(key)
    return keys


def _running_head_counts(rows: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        soup = BeautifulSoup(row.get("html") or row.get("raw_html") or "", "html.parser")
        for tag in soup.find_all(class_="running-head"):
            key = _title_key(tag.get_text(" ", strip=True))
            if key:
                counts[key] += 1
    return counts


def _should_promote_running_head(
    *,
    soup: BeautifulSoup,
    text: str,
    heading_keys: set[str],
    running_head_counts: Counter[str],
    max_occurrences: int,
) -> tuple[bool, str]:
    key = _title_key(text)
    if not key:
        return False, "empty"
    if key in heading_keys:
        return False, "matches_existing_heading"
    if running_head_counts[key] > max_occurrences:
        return False, "repeated_running_head"
    if soup.find("h1"):
        return False, "page_already_has_h1"
    if soup.find("h3") and not soup.find("h2"):
        return False, "page_has_only_lower_headings"
    return True, "unique_leading_running_head"


def normalize_rows(
    rows: list[dict[str, Any]],
    *,
    run_id: str | None = None,
    max_promoted_running_head_occurrences: int = 2,
    strip_page_numbers: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    heading_keys = _all_heading_keys(rows)
    running_counts = _running_head_counts(rows)
    out_rows: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    promoted = 0
    removed = 0

    for index, row in enumerate(rows, start=1):
        new_row = deepcopy(row)
        html = row.get("html") or row.get("raw_html") or ""
        soup = BeautifulSoup(html, "html.parser")
        leading_tag, leading_text = _leading_running_head(soup)

        if strip_page_numbers:
            for tag in list(soup.find_all(class_="page-number")):
                tag.decompose()

        for tag in list(soup.find_all(class_="running-head")):
            text = _normalize_ws(tag.get_text(" ", strip=True))
            is_leading = tag is leading_tag
            if is_leading:
                promote, reason = _should_promote_running_head(
                    soup=soup,
                    text=text,
                    heading_keys=heading_keys,
                    running_head_counts=running_counts,
                    max_occurrences=max_promoted_running_head_occurrences,
                )
                if promote:
                    tag.name = "h1"
                    classes = [c for c in (tag.get("class") or []) if c != "running-head"]
                    classes.append("semantic-running-head")
                    tag["class"] = classes
                    tag["data-normalized-from"] = "running-head"
                    promoted += 1
                else:
                    tag.decompose()
                    removed += 1
                decisions.append(
                    {
                        "page_number": row.get("page_number") or row.get("page") or index,
                        "text": text,
                        "action": "promote_to_h1" if promote else "remove",
                        "reason": reason,
                    }
                )
                continue
            tag.decompose()
            removed += 1
            decisions.append(
                {
                    "page_number": row.get("page_number") or row.get("page") or index,
                    "text": text,
                    "action": "remove",
                    "reason": "non_leading_running_head",
                }
            )

        new_row["html"] = soup.decode_contents()
        out_rows.append(new_row)

    report = {
        "schema_version": "graphic_manual_html_normalization_report_v1",
        "module_id": MODULE_ID,
        "run_id": run_id,
        "created_at": _utc(),
        "summary": {
            "page_rows": len(rows),
            "promoted_running_heads": promoted,
            "removed_running_heads": removed,
            "running_head_occurrences": dict(running_counts),
        },
        "decisions": decisions,
    }
    return out_rows, report


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize OCR HTML for graphics-heavy manuals.")
    parser.add_argument("--pages", required=True, help="Input page_html_v1 JSONL")
    parser.add_argument("--out", required=True, help="Output normalized page_html_v1 JSONL")
    parser.add_argument("--max-promoted-running-head-occurrences", type=int, default=2)
    parser.add_argument("--strip-page-numbers", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--run-id")
    parser.add_argument("--state-file")
    parser.add_argument("--progress-file")
    args = parser.parse_args()

    logger = ProgressLogger(state_path=args.state_file, progress_path=args.progress_file, run_id=args.run_id)
    logger.log("transform", "running", message="Normalizing graphics-heavy manual HTML", module_id=MODULE_ID)

    rows = list(read_jsonl(args.pages))
    normalized_rows, report = normalize_rows(
        rows,
        run_id=args.run_id,
        max_promoted_running_head_occurrences=args.max_promoted_running_head_occurrences,
        strip_page_numbers=args.strip_page_numbers,
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    save_jsonl(str(out_path), normalized_rows)
    report_path = out_path.with_name("graphic_manual_html_normalization_report.json")
    save_json(str(report_path), report)

    logger.log(
        "transform",
        "done",
        current=len(normalized_rows),
        total=len(normalized_rows),
        message=(
            "Normalized manual HTML: "
            f"{report['summary']['promoted_running_heads']} promoted running heads, "
            f"{report['summary']['removed_running_heads']} removed"
        ),
        artifact=str(out_path),
        module_id=MODULE_ID,
        extra={"report": str(report_path), "summary": report["summary"]},
    )


if __name__ == "__main__":
    main()
