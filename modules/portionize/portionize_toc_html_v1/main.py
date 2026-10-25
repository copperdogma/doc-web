#!/usr/bin/env python3
"""
Portionize chapters from HTML by parsing TOC entries.
Uses printed page numbers (from extract_page_numbers_html_v1) to set page ranges.
Can explicitly aggregate documents without TOC evidence using source identities.
"""
import argparse
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from modules.common.utils import read_jsonl, save_jsonl, ProgressLogger


TOC_TITLE_PATTERNS = {"index", "table of contents", "contents"}


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _looks_like_toc_entry(text: str) -> bool:
    t = _normalize_ws(text)
    if not t or len(t) > 160:
        return False
    if re.search(r"\.{3,}\s*\d+\s*$", t):
        return True
    if re.search(r"\s{2,}\d+\s*$", text) and re.search(r"[A-Za-z]", text):
        return True
    return False


def _extract_entry_from_line(text: str) -> Optional[Dict[str, Any]]:
    raw = text or ""
    if not raw.strip():
        return None
    m = re.match(r"^(.*?)\.{3,}\s*(\d{1,4})\s*$", raw)
    if not m:
        m = re.match(r"^(.*?\S)\s{2,}(\d{1,4})\s*$", raw)
    if not m:
        return None
    title = _normalize_ws(m.group(1))
    title = re.sub(r"\.{2,}", "", title).strip()
    if not title:
        return None
    page_num = int(m.group(2))
    return {"title": title, "page_start": page_num}


def _has_toc_title(lines: List[str]) -> bool:
    for line in lines[:5]:
        if _normalize_ws(line).lower() in TOC_TITLE_PATTERNS:
            return True
    return False


def _is_toc_page(lines: List[str], min_entries: int, table_entry_count: int = 0) -> bool:
    entry_count = sum(1 for line in lines if _looks_like_toc_entry(line))
    if _has_toc_title(lines):
        return entry_count + table_entry_count >= max(1, min_entries)
    return entry_count >= max(1, min_entries)


def _extract_table_entries(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    entries = []
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]
            if len(cells) < 2:
                continue
            title = _normalize_ws(cells[0])
            title = re.sub(r"\.{2,}", "", title).strip()
            if not title or title.lower() in {"children", "total"}:
                continue
            last = _normalize_ws(cells[-1])
            digits = re.findall(r"\d{1,4}", last)
            if not digits:
                continue
            page_num = int(digits[-1])
            entries.append({"title": title, "page_start": page_num})
    return entries


def _dedupe_entries(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = {}
    for ent in entries:
        key = ent["title"].lower()
        if key not in seen or ent["page_start"] < seen[key]["page_start"]:
            seen[key] = ent
    return list(seen.values())


def _slugify(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text or "chapter"


def _has_strong_toc_hint(soup: BeautifulSoup) -> bool:
    """Refuse to disguise an incomplete or malformed TOC as a flat document."""
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "td", "th"]):
        text = tag.get_text(" ", strip=True)
        if _normalize_ws(text).lower() in TOC_TITLE_PATTERNS:
            return True
        # A malformed destination may be Roman or named rather than numeric.
        # Require an actual leader run and a short destination, not prose ellipses.
        malformed_leader = re.fullmatch(
            r".{0,139}?\S\s*\.{4,}\s*(?:[\w?+-]{1,24}(?:\s+[\w?+-]{1,24})?)?\s*", text,
        )
        if _looks_like_toc_entry(text) or malformed_leader:
            return True
    return False


def _single_document_portion(rows: List[Dict[str, Any]], title: str) -> Dict[str, Any]:
    source_pages = []
    seen = set()
    for row_number, row in enumerate(rows, 1):
        source_page = row.get("page_number")
        if source_page is None:
            source_page = row.get("page")
        if type(source_page) is not int or source_page <= 0:
            raise SystemExit(f"Invalid source page identity in row {row_number}: {source_page!r}")
        if source_page in seen:
            raise SystemExit(f"Duplicate source page identity in row {row_number}: {source_page}")
        seen.add(source_page)
        source_pages.append(source_page)
    source_pages.sort()
    return {
        "schema_version": "portion_hyp_v1",
        "module_id": "portionize_toc_html_v1",
        "portion_id": "document",
        "page_start": source_pages[0],
        "page_end": source_pages[-1],
        "title": title.strip() or "Document",
        "type": "chapter",
        "confidence": 0.5,
        "notes": "single-document-fallback",
        "source_pages": source_pages,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Portionize chapters using TOC entries from HTML pages.")
    parser.add_argument("--pages", required=True, help="page_html_v1 JSONL (with printed_page_number)")
    parser.add_argument("--out", required=True, help="Output portion_hyp_v1 JSONL")
    parser.add_argument("--min-entries", type=int, default=3, help="Minimum TOC-like lines to treat a page as TOC")
    parser.add_argument("--fallback-mode", choices=["error", "single-document"], default="error",
                        help="Opt into source-page aggregation only when no TOC evidence exists")
    parser.add_argument("--fallback-title", default="Document", help="Title for single-document fallback")
    parser.add_argument("--run-id", dest="run_id", default=None, help="Ignored (driver compatibility)")
    parser.add_argument("--state-file", dest="state_file", default=None, help="Ignored (driver compatibility)")
    parser.add_argument("--progress-file", dest="progress_file", default=None, help="Ignored (driver compatibility)")
    args = parser.parse_args()

    rows = list(read_jsonl(args.pages))
    if not rows:
        raise SystemExit(f"Input is empty: {args.pages}")
    for row_number, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise SystemExit(f"Input row {row_number} must be an object")
        if row.get("error"):
            raise SystemExit(f"Input row {row_number} contains a producer error")

    max_printed = max((r.get("printed_page_number") for r in rows if isinstance(r.get("printed_page_number"), int)), default=None)
    entries: List[Dict[str, Any]] = []
    has_toc_evidence = False

    for row in rows:
        html = row.get("html") or row.get("raw_html") or ""
        soup = BeautifulSoup(html, "html.parser")
        has_toc_evidence = has_toc_evidence or _has_strong_toc_hint(soup)
        lines = [tag.get_text(" ", strip=True) for tag in soup.find_all(["h1", "h2", "h3", "p"])]
        table_entries = _extract_table_entries(soup)
        if not _is_toc_page(lines, args.min_entries, table_entry_count=len(table_entries)):
            continue
        for line in lines:
            ent = _extract_entry_from_line(line)
            if ent:
                entries.append(ent)
        entries.extend(table_entries)

    entries = _dedupe_entries(entries)
    entries = [e for e in entries if isinstance(e.get("page_start"), int)]
    entries.sort(key=lambda e: e["page_start"])

    portions = []
    if not entries:
        if args.fallback_mode != "single-document":
            raise SystemExit("No TOC entries found; cannot build chapters.")
        if has_toc_evidence:
            raise SystemExit("TOC evidence is present but no entries were admitted; cannot use single-document fallback.")
        portions.append(_single_document_portion(rows, args.fallback_title))

    for idx, ent in enumerate(entries):
        page_start = ent["page_start"]
        page_end = None
        if idx + 1 < len(entries):
            next_start = entries[idx + 1]["page_start"]
            if next_start > page_start:
                page_end = next_start - 1
        elif isinstance(max_printed, int) and max_printed >= page_start:
            page_end = max_printed
        if page_end is None:
            page_end = page_start
        title = ent.get("title")
        portion_id = _slugify(title)
        portions.append({
            "schema_version": "portion_hyp_v1",
            "module_id": "portionize_toc_html_v1",
            "portion_id": portion_id,
            "page_start": page_start,
            "page_end": page_end,
            "title": title,
            "type": "chapter",
            "confidence": 0.7,
            "notes": "toc-derived",
            "source_pages": list(range(page_start, page_end + 1)),
        })

    save_jsonl(args.out, portions)
    logger = ProgressLogger(state_path=args.state_file, progress_path=args.progress_file, run_id=args.run_id)
    logger.log("portionize", "done", current=len(portions), total=len(portions),
               message=f"Wrote {len(portions)} portions to {args.out}")


if __name__ == "__main__":
    main()
