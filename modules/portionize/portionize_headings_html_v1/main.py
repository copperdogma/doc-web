#!/usr/bin/env python3
"""
Portionize chapters by detecting top-level HTML headings (e.g., <h1>) per page.
Uses printed page numbers when available and can opt into a single-document
fallback for flat/non-TOC inputs.
"""
import argparse
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from modules.common.utils import read_jsonl, save_jsonl, ProgressLogger, utc_now


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


_CATEGORY_WORDS = {
    "actions",
    "catalog",
    "cards",
    "components",
    "contents",
    "courses",
    "elements",
    "examples",
    "index",
    "overview",
    "phase",
    "phases",
    "reference",
    "references",
    "route",
    "routes",
    "rules",
    "setup",
    "summary",
    "upgrades",
    "variants",
}

_CATALOG_PARENT_CUES = (
    "following page",
    "following pages",
    "list of",
    "detailed look",
    "different types",
    "types of",
    "description of each",
    "descriptions will",
    "reference",
)

_CATALOG_TOKEN_STOPWORDS = {
    "and",
    "card",
    "cards",
    "course",
    "courses",
    "index",
    "section",
    "sections",
    "the",
}

_PROCEDURAL_PARENT_TITLE_CUES = (
    "how to",
    "how-to",
    "playing",
    "play",
    "round",
    "rules",
    "turn",
)

_PROCEDURAL_PARENT_TEXT_CUES = (
    "following page",
    "following pages",
    "next page",
    "description of each",
    "full round",
    "phase",
    "phases",
)

_PROCEDURAL_CHILD_TERMS = {
    "activation",
    "activating",
    "order",
    "phase",
    "phases",
    "programming",
    "register",
    "round",
    "summary",
    "turn",
    "upgrade",
}


def _heading_level(tag_name: str) -> int:
    match = re.fullmatch(r"h([1-6])", (tag_name or "").lower())
    return int(match.group(1)) if match else 99


def _looks_like_category_heading(text: str) -> bool:
    normalized = _normalize_title(text)
    if not normalized:
        return False
    tokens = normalized.split()
    if any(token in _CATEGORY_WORDS for token in tokens):
        return True
    return bool(":" in text and any(token.rstrip(":") in _CATEGORY_WORDS for token in tokens[:3]))


def _singular_token(token: str) -> str:
    token = token.strip().casefold()
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 3 and token.endswith("s"):
        return token[:-1]
    return token


def _title_content_tokens(text: str) -> set[str]:
    tokens = set()
    for token in _normalize_title(text).split():
        singular = _singular_token(token)
        if len(singular) < 4 or singular in _CATALOG_TOKEN_STOPWORDS:
            continue
        tokens.add(singular)
    return tokens


def _title_category_tokens(text: str) -> set[str]:
    return {_singular_token(token) for token in _normalize_title(text).split() if token}


def _page_text(row: Dict[str, Any], *, prefer_raw: bool = False) -> str:
    html = (row.get("raw_html") if prefer_raw else None) or row.get("html") or row.get("raw_html") or ""
    soup = BeautifulSoup(html, "html.parser")
    return _normalize_ws(soup.get_text(" ", strip=True))


def _page_running_head(row: Dict[str, Any]) -> str:
    html = row.get("raw_html") or row.get("html") or ""
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find(class_="running-head")
    return _normalize_ws(tag.get_text(" ", strip=True)) if tag else ""


def _looks_like_catalog_parent(title: str, row: Dict[str, Any] | None) -> bool:
    if not row or not _looks_like_category_heading(title):
        return False
    text = _page_text(row, prefer_raw=True).casefold()
    return any(cue in text for cue in _CATALOG_PARENT_CUES)


def _catalog_parent_terms(title: str) -> set[str]:
    terms = _title_content_tokens(title)
    if "card" in _title_category_tokens(title):
        terms.add("card")
    if "course" in _title_category_tokens(title):
        terms.add("course")
    return terms


def _is_catalog_child_boundary(
    *,
    parent_title: str,
    parent_terms: set[str],
    child: Dict[str, Any],
    row_by_source_page: Dict[int, Dict[str, Any]],
) -> bool:
    child_title = child.get("title") or ""
    child_terms = _title_content_tokens(child_title) | _title_category_tokens(child_title)
    if parent_terms and parent_terms & child_terms:
        return True

    row = row_by_source_page.get(int(child.get("source_page_number") or 0))
    running_head = _page_running_head(row or {})
    if running_head:
        running_terms = _title_content_tokens(running_head) | _title_category_tokens(running_head)
        if parent_terms and parent_terms & running_terms:
            return True
        if _normalize_title(running_head) == _normalize_title(parent_title):
            return True
    return False


def _merge_catalog_subsection_boundaries(
    boundaries: List[Dict[str, Any]],
    *,
    row_by_source_page: Dict[int, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    idx = 0
    while idx < len(boundaries):
        boundary = boundaries[idx]
        merged.append(boundary)
        parent_title = boundary.get("title") or ""
        parent_page = int(boundary.get("source_page_number") or 0)
        parent_row = row_by_source_page.get(parent_page)
        if not _looks_like_catalog_parent(parent_title, parent_row):
            idx += 1
            continue

        parent_terms = _catalog_parent_terms(parent_title)
        idx += 1
        while idx < len(boundaries) and _is_catalog_child_boundary(
            parent_title=parent_title,
            parent_terms=parent_terms,
            child=boundaries[idx],
            row_by_source_page=row_by_source_page,
        ):
            idx += 1
        continue

    return merged


def _looks_like_procedural_parent(title: str, row: Dict[str, Any] | None) -> bool:
    if not row:
        return False
    normalized_title = _normalize_title(title)
    if not any(cue in normalized_title for cue in _PROCEDURAL_PARENT_TITLE_CUES):
        return False
    text = _page_text(row, prefer_raw=True).casefold()
    return any(cue in text for cue in _PROCEDURAL_PARENT_TEXT_CUES)


def _is_procedural_child_boundary(
    child: Dict[str, Any],
    *,
    row_by_source_page: Dict[int, Dict[str, Any]],
) -> bool:
    child_title = child.get("title") or ""
    child_terms = _title_category_tokens(child_title)
    if child_terms & _PROCEDURAL_CHILD_TERMS:
        return True
    row = row_by_source_page.get(int(child.get("source_page_number") or 0))
    running_head = _page_running_head(row or {})
    running_terms = _title_category_tokens(running_head)
    if running_terms & _PROCEDURAL_CHILD_TERMS:
        return True
    return False


def _merge_procedural_subsection_boundaries(
    boundaries: List[Dict[str, Any]],
    *,
    row_by_source_page: Dict[int, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    idx = 0
    while idx < len(boundaries):
        boundary = boundaries[idx]
        merged.append(boundary)
        parent_title = boundary.get("title") or ""
        parent_page = int(boundary.get("source_page_number") or 0)
        parent_row = row_by_source_page.get(parent_page)
        if not _looks_like_procedural_parent(parent_title, parent_row):
            idx += 1
            continue

        idx += 1
        while idx < len(boundaries) and _is_procedural_child_boundary(
            boundaries[idx],
            row_by_source_page=row_by_source_page,
        ):
            idx += 1
        continue

    return merged


def _next_text_until_heading(tag: Any, *, max_chars: int = 280) -> str:
    parts: List[str] = []
    for sibling in tag.next_siblings:
        name = getattr(sibling, "name", None)
        if name and re.fullmatch(r"h[1-6]", name.lower()):
            break
        text = _normalize_ws(
            sibling.get_text(" ", strip=True) if hasattr(sibling, "get_text") else str(sibling)
        )
        if text:
            parts.append(text)
        if sum(len(part) for part in parts) >= max_chars:
            break
    return _normalize_ws(" ".join(parts))[:max_chars]


def _looks_like_label_value_entry(text: str) -> bool:
    if not text:
        return False
    labels = re.findall(r"\b[A-Z][A-Za-z0-9 /&-]{1,28}:", text)
    if len(labels) < 2:
        return False
    distinct = {label.casefold() for label in labels}
    return len(distinct) >= 2


def _is_suppressed_lower_item_boundary(tag: Any) -> bool:
    tag_name = (getattr(tag, "name", "") or "").lower()
    if _heading_level(tag_name) <= 1:
        return False
    text = _normalize_ws(tag.get_text(" ", strip=True))
    if _looks_like_category_heading(text):
        return False
    return _looks_like_label_value_entry(_next_text_until_heading(tag))


def _extract_heading(
    html: str,
    heading_tags: List[str],
    min_len: int,
    max_len: int,
    min_alpha: float,
    *,
    suppress_lower_heading_item_boundaries: bool = False,
) -> Optional[Dict[str, str]]:
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
        if suppress_lower_heading_item_boundaries and _is_suppressed_lower_item_boundary(tag):
            continue
        return {"title": text, "tag": tag.name.lower()}
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
    parser.add_argument(
        "--suppress-lower-heading-item-boundaries",
        "--suppress_lower_heading_item_boundaries",
        action="store_true",
        help=(
            "When scanning h2+ headings, skip lower-level headings that look like "
            "catalog item entries with immediate label/value metadata rather than "
            "new top-level portions."
        ),
    )
    parser.add_argument(
        "--merge-catalog-subsections",
        "--merge_catalog_subsections",
        action="store_true",
        help=(
            "Merge subsection/category boundaries back under an earlier catalog/index "
            "parent when headings and running-head signals show they share the same "
            "catalog family."
        ),
    )
    parser.add_argument(
        "--merge-procedural-subsections",
        "--merge_procedural_subsections",
        action="store_true",
        help=(
            "Merge phase/round/procedure subsection headings under a broad "
            "procedural parent when the parent introduces details on following pages."
        ),
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
    row_by_source_page = {
        int(row["_source_page_number"]): row
        for row in rows_sorted
    }

    boundaries: List[Dict[str, Any]] = []
    for idx, row in enumerate(rows_sorted, start=1):
        printed = row.get("printed_page_number")
        if not isinstance(printed, int) and not args.allow_unnumbered:
            continue
        if isinstance(printed, int) and printed < args.min_printed_page:
            continue
        html = row.get("html") or row.get("raw_html") or ""
        heading = _extract_heading(
            html,
            heading_tags,
            args.min_title_len,
            args.max_title_len,
            args.min_alpha,
            suppress_lower_heading_item_boundaries=args.suppress_lower_heading_item_boundaries,
        )
        if not heading:
            continue
        heading_title = heading["title"]
        heading_norm = _normalize_title(heading_title)
        boundaries.append({
            "title": heading_title,
            "title_norm": heading_norm,
            "heading_tag": heading["tag"],
            "printed_page_number": printed,
            "source_page_number": _source_page_number(row, idx),
        })

    # Sort in source-page order so unnumbered flat documents remain stable.
    boundaries.sort(key=lambda b: int(b["source_page_number"]))

    portions: List[Dict[str, Any]] = []
    slug_counts: Dict[str, int] = {}
    created_at = utc_now()

    if boundaries:
        deduped_boundaries: List[Dict[str, Any]] = []
        for boundary in boundaries:
            if deduped_boundaries and boundary["title_norm"] == deduped_boundaries[-1]["title_norm"]:
                continue
            deduped_boundaries.append(boundary)

        if args.merge_catalog_subsections:
            deduped_boundaries = _merge_catalog_subsection_boundaries(
                deduped_boundaries,
                row_by_source_page=row_by_source_page,
            )
        if args.merge_procedural_subsections:
            deduped_boundaries = _merge_procedural_subsection_boundaries(
                deduped_boundaries,
                row_by_source_page=row_by_source_page,
            )

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
            portions[-1]["source_heading_tag"] = boundary.get("heading_tag")
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
