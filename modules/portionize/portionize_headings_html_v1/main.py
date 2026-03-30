#!/usr/bin/env python3
"""
Portionize chapters by detecting top-level HTML headings (e.g., <h1>) per page.
Uses printed page numbers when available and can opt into a single-document
fallback for flat/non-TOC inputs.
"""
import argparse
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from modules.common.utils import read_jsonl, save_jsonl, ProgressLogger


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _alpha_ratio(text: str) -> float:
    if not text:
        return 0.0
    letters = sum(1 for c in text if c.isalpha())
    return letters / max(1, len(text))


def _normalize_title(text: str) -> str:
    text = _normalize_ws(text).lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _slugify(text: str) -> str:
    text = _normalize_title(text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text or "chapter"


def _parse_heading_tags(raw: str) -> List[str]:
    if not raw:
        return ["h1"]
    tags = [t.strip().lower() for t in raw.split(",") if t.strip()]
    return tags or ["h1"]


def _source_page_number(row: Dict[str, Any], fallback: int) -> int:
    return int(row.get("page_number") or row.get("page") or fallback)


def _extract_heading(html: str, heading_tags: List[str], min_len: int, max_len: int, min_alpha: float) -> Optional[str]:
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(heading_tags):
        text = tag.get_text(" ", strip=True)
        text = _normalize_ws(text)
        if not text:
            continue
        if len(text) < min_len or len(text) > max_len:
            continue
        if _alpha_ratio(text) < min_alpha:
            continue
        return text
    return None


def _build_portion(
    *,
    rows: List[Dict[str, Any]],
    portion_id: str,
    title: str,
    run_id: Optional[str],
    created_at: str,
    notes: str,
) -> Dict[str, Any]:
    source_pages = [
        int(row.get("_source_page_number") or _source_page_number(row, idx + 1))
        for idx, row in enumerate(rows)
    ]
    printed_pages = [
        int(row["printed_page_number"])
        for row in rows
        if isinstance(row.get("printed_page_number"), int)
    ]
    page_start = printed_pages[0] if printed_pages else source_pages[0]
    page_end = printed_pages[-1] if printed_pages else source_pages[-1]
    return {
        "schema_version": "portion_hyp_v1",
        "module_id": "portionize_headings_html_v1",
        "run_id": run_id,
        "created_at": created_at,
        "portion_id": portion_id,
        "page_start": page_start,
        "page_end": page_end,
        "title": title,
        "type": "chapter",
        "confidence": 0.6,
        "notes": notes,
        "source_pages": source_pages,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Portionize chapters using HTML headings + printed page numbers.")
    parser.add_argument("--pages", required=True, help="page_html_v1 JSONL (with printed_page_number)")
    parser.add_argument("--out", required=True, help="Output portion_hyp_v1 JSONL")
    parser.add_argument("--heading-tags", default="h1", help="Comma-separated heading tags to scan (default: h1)")
    parser.add_argument("--min-printed-page", type=int, default=1, help="Minimum printed page number to start chapters")
    parser.add_argument("--allow-unnumbered", action="store_true",
                        help="Allow headings on pages without printed_page_number")
    parser.add_argument("--min-title-len", type=int, default=3, help="Minimum heading length")
    parser.add_argument("--max-title-len", type=int, default=140, help="Maximum heading length")
    parser.add_argument("--min-alpha", type=float, default=0.3, help="Minimum alpha ratio for heading text")
    parser.add_argument(
        "--fallback-mode",
        choices=["error", "single-document"],
        default="error",
        help="Behavior when no qualifying headings are found (default: error)",
    )
    parser.add_argument(
        "--fallback-title",
        default="Document",
        help="Title to use when --fallback-mode=single-document (default: Document)",
    )
    parser.add_argument("--run-id", dest="run_id", default=None, help="Ignored (driver compatibility)")
    parser.add_argument("--state-file", dest="state_file", default=None, help="Ignored (driver compatibility)")
    parser.add_argument("--progress-file", dest="progress_file", default=None, help="Ignored (driver compatibility)")
    args = parser.parse_args()

    rows = list(read_jsonl(args.pages))
    if not rows:
        raise SystemExit(f"Input is empty: {args.pages}")

    heading_tags = _parse_heading_tags(args.heading_tags)
    # Preserve stable order by image/page sequence.
    rows_sorted = sorted(rows, key=lambda r: int(r.get("page_number") or r.get("page") or 0))
    for idx, row in enumerate(rows_sorted, start=1):
        row["_source_page_number"] = _source_page_number(row, idx)
    row_index_by_source_page = {
        int(row["_source_page_number"]): idx
        for idx, row in enumerate(rows_sorted)
    }

    boundaries: List[Dict[str, Any]] = []
    for idx, row in enumerate(rows_sorted, start=1):
        printed = row.get("printed_page_number")
        if not isinstance(printed, int) and not args.allow_unnumbered:
            continue
        if isinstance(printed, int) and printed < args.min_printed_page:
            continue
        html = row.get("html") or row.get("raw_html") or ""
        heading = _extract_heading(html, heading_tags, args.min_title_len, args.max_title_len, args.min_alpha)
        if not heading:
            continue
        heading_norm = _normalize_title(heading)
        boundaries.append({
            "title": heading,
            "title_norm": heading_norm,
            "printed_page_number": printed,
            "source_page_number": _source_page_number(row, idx),
        })

    # Sort in source-page order so unnumbered flat documents remain stable.
    boundaries.sort(key=lambda b: int(b["source_page_number"]))

    portions: List[Dict[str, Any]] = []
    slug_counts: Dict[str, int] = {}
    created_at = datetime.utcnow().isoformat() + "Z"

    if boundaries:
        deduped_boundaries: List[Dict[str, Any]] = []
        for boundary in boundaries:
            if deduped_boundaries and boundary["title_norm"] == deduped_boundaries[-1]["title_norm"]:
                continue
            deduped_boundaries.append(boundary)

        for idx, boundary in enumerate(deduped_boundaries):
            source_start = int(boundary["source_page_number"])
            start_idx = row_index_by_source_page[source_start]
            if idx + 1 < len(deduped_boundaries):
                next_start = int(deduped_boundaries[idx + 1]["source_page_number"])
                end_idx = row_index_by_source_page[next_start] - 1
            else:
                end_idx = len(rows_sorted) - 1
            portion_rows = rows_sorted[start_idx : end_idx + 1]
            slug = _slugify(boundary["title"])
            slug_counts[slug] = slug_counts.get(slug, 0) + 1
            portion_id = slug if slug_counts[slug] == 1 else f"{slug}_{slug_counts[slug]}"
            printed_pages = [
                row.get("printed_page_number")
                for row in portion_rows
                if isinstance(row.get("printed_page_number"), int)
            ]
            notes = "heading-derived" if printed_pages else "heading-derived-source-pages"
            portions.append(
                _build_portion(
                    rows=portion_rows,
                    portion_id=portion_id,
                    title=boundary["title"],
                    run_id=args.run_id,
                    created_at=created_at,
                    notes=notes,
                )
            )
    elif args.fallback_mode == "single-document":
        portions.append(
            _build_portion(
                rows=rows_sorted,
                portion_id="document",
                title=args.fallback_title.strip() or "Document",
                run_id=args.run_id,
                created_at=created_at,
                notes="single-document-fallback",
            )
        )
    else:
        raise SystemExit("No headings found for chapter boundaries.")

    save_jsonl(args.out, portions)
    logger = ProgressLogger(state_path=args.state_file, progress_path=args.progress_file, run_id=args.run_id)
    logger.log("portionize", "done", current=len(portions), total=len(portions),
               message=f"Wrote {len(portions)} portions to {args.out}")


if __name__ == "__main__":
    main()
