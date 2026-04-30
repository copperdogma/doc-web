#!/usr/bin/env python3
"""
Build chapter HTML files from pages and portion hypotheses.

Produces proper HTML5 documents with embedded CSS, semantic structure
(<figure>/<figcaption>), chapter navigation, and responsive styling.
"""
import argparse
import re
import sys
from copy import deepcopy
from difflib import SequenceMatcher
from functools import lru_cache
from html import escape as html_escape
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from bs4 import BeautifulSoup

from modules.common.onward_genealogy_html import (
    merge_genealogy_tables_preserving_headings as _merge_genealogy_tables_preserving_headings,
    merge_contiguous_genealogy_tables as _merge_contiguous_genealogy_tables,  # noqa: F401
)
from modules.common.utils import read_jsonl, save_jsonl, save_json, ensure_dir, ProgressLogger, utc_now


def _utc() -> str:
    return utc_now()


def _resolve_run_dir(out_path: Path) -> Path:
    cur = out_path.parent
    for parent in [cur] + list(cur.parents):
        if (parent / "pipeline_state.json").exists():
            return parent
    return cur


def _coerce_int(value: Any) -> Optional[int]:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        cleaned = value.strip()
        if cleaned.isdigit():
            return int(cleaned)
    return None


def _source_page_number(row: Dict[str, Any]) -> Optional[int]:
    return _coerce_int(row.get("page_number") or row.get("page"))


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", (value or "").casefold()).strip("-")
    return normalized or "document"


def _display_path(path: str, run_dir: Path) -> str:
    raw = Path(path).resolve(strict=False)
    base = run_dir.resolve(strict=False)
    try:
        return str(raw.relative_to(base))
    except ValueError:
        return str(path)


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

_CSS = """
/* Reset */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

/* Typography */
:root {
  --font-body: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --font-serif: Georgia, "Times New Roman", serif;
  --max-width: 52rem;
  --color-bg: #fff;
  --color-text: #222;
  --color-muted: #666;
  --color-border: #ddd;
  --color-link: #1a5276;
  --color-nav-bg: #f8f8f8;
}

html { font-size: 100%; }
body {
  font-family: var(--font-serif);
  color: var(--color-text);
  background: var(--color-bg);
  line-height: 1.7;
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 1.5rem 1rem;
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-body);
  line-height: 1.3;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}
h1 { font-size: 1.8rem; }
h2 { font-size: 1.4rem; }
h3 { font-size: 1.2rem; }

p { margin-bottom: 0.8em; }
p.flattened-heading {
  font-family: var(--font-body);
  font-weight: 600;
}
a { color: var(--color-link); }

/* Navigation */
nav.chapter-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 0;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 1.5rem;
  font-family: var(--font-body);
  font-size: 0.9rem;
}
nav.chapter-nav.bottom {
  border-bottom: none;
  border-top: 1px solid var(--color-border);
  margin-top: 2rem;
  margin-bottom: 0;
}
nav.chapter-nav a { text-decoration: none; }
nav.chapter-nav .nav-placeholder { min-width: 4rem; }

/* Tables */
table {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
  font-size: 0.95rem;
  overflow-x: auto;
  display: block;
}
th, td {
  border: 1px solid var(--color-border);
  padding: 0.4rem 0.6rem;
  text-align: left;
  vertical-align: top;
}
th {
  background: var(--color-nav-bg);
  font-weight: 600;
  font-family: var(--font-body);
}
tr:nth-child(even) td { background: #fafafa; }

/* Images / Figures */
figure {
  margin: 1.5em 0;
  text-align: center;
}
figure img {
  max-width: 100%;
  height: auto;
  display: inline-block;
}
figcaption {
  font-family: var(--font-body);
  font-size: 0.85rem;
  color: var(--color-muted);
  margin-top: 0.4em;
  font-style: italic;
}
figure.inferred-essential-figure {
  text-align: left;
  margin: 0.8em 0 1em;
}
figure.inferred-essential-figure img {
  max-height: 18rem;
  width: auto;
}
li > figure.inferred-essential-figure,
dd > figure.inferred-essential-figure {
  margin-top: 0.2em;
}
li > figure.inferred-essential-figure img {
  max-height: 12rem;
}
aside.semantic-callout {
  border-left: 0.35rem solid #c9a227;
  margin: 1.5rem 0;
  padding: 0.75rem 1rem;
  background: #fff8dc;
}
aside.semantic-callout p {
  margin: 0;
}
img {
  max-width: 100%;
  height: auto;
}

/* Index page */
.book-header { margin-bottom: 2rem; }
.book-header h1 { margin-top: 0; }
.book-header .author { color: var(--color-muted); font-size: 1.1rem; }
.toc-list { list-style: none; padding: 0; }
.toc-list li {
  padding: 0.4rem 0;
  border-bottom: 1px solid var(--color-border);
}
.toc-list li:last-child { border-bottom: none; }
.toc-list a { text-decoration: none; font-family: var(--font-body); }
.toc-list .page-range {
  color: var(--color-muted);
  font-size: 0.85rem;
  margin-left: 0.5em;
}

/* Article */
article { margin-bottom: 2rem; }

/* Print */
@media print {
  body { max-width: none; padding: 0; }
  nav.chapter-nav { display: none; }
  table { display: table; }
  figure { break-inside: avoid; }
}
""".strip()


# ---------------------------------------------------------------------------
# HTML5 document wrapper
# ---------------------------------------------------------------------------

def _html5_wrap(body_html: str, title: str, nav_html_top: str = "",
                nav_html_bottom: str = "") -> str:
    """Wrap body content in a proper HTML5 document."""
    title_esc = html_escape(title)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_esc}</title>
<style>
{_CSS}
</style>
</head>
<body>
{nav_html_top}
<article>
{body_html}
</article>
{nav_html_bottom}
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

def _build_nav(prev_file: Optional[str], prev_title: Optional[str],
               next_file: Optional[str], next_title: Optional[str],
               is_bottom: bool = False) -> str:
    cls = 'chapter-nav bottom' if is_bottom else 'chapter-nav'
    prev_link = f'<a href="{prev_file}">&larr; {html_escape(prev_title or "Prev")}</a>' if prev_file else '<span class="nav-placeholder"></span>'
    next_link = f'<a href="{next_file}">{html_escape(next_title or "Next")} &rarr;</a>' if next_file else '<span class="nav-placeholder"></span>'
    return (
        f'<nav class="{cls}" aria-label="Document navigation" '
        f'data-doc-web-ui-chrome="navigation">'
        f'{prev_link}<a href="index.html">Index</a>{next_link}</nav>'
    )


# ---------------------------------------------------------------------------
# Post-processing helpers
# ---------------------------------------------------------------------------

def _strip_headers_and_numbers(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(class_="page-number"):
        tag.decompose()
    for tag in soup.find_all(class_="running-head"):
        tag.decompose()
    return soup.decode_contents()


def _add_table_scope(html: str) -> str:
    """Add scope attributes to <th> elements for accessibility."""
    if "<th" not in html:
        return html
    soup = BeautifulSoup(html, "html.parser")
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows:
            continue
        # First row with <th> gets scope="col"
        first_row = rows[0]
        for th in first_row.find_all("th"):
            if not th.get("scope"):
                th["scope"] = "col"
        # Remaining rows: first <th> in each row gets scope="row"
        for row in rows[1:]:
            ths = row.find_all("th")
            if ths and not ths[0].get("scope"):
                ths[0]["scope"] = "row"
    return soup.decode_contents()


_PROVENANCE_TEXT_KINDS = {"heading", "paragraph", "list_item", "caption", "page_marker", "other"}


def _block_kind_for_tag(tag_name: str) -> str:
    lowered = (tag_name or "").lower()
    if lowered in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        return "heading"
    if lowered == "p":
        return "paragraph"
    if lowered == "li":
        return "list_item"
    if lowered == "table":
        return "table"
    if lowered == "figure":
        return "figure"
    if lowered in {"caption", "figcaption"}:
        return "caption"
    if lowered == "span":
        return "page_marker"
    return "other"


def _iter_provenance_tags(node):
    for child in getattr(node, "children", []):
        name = getattr(child, "name", None)
        if not name:
            continue
        lowered = name.lower()
        if lowered in {"figure", "table", "p", "li", "caption", "figcaption", "blockquote", "pre"}:
            yield child
            continue
        if lowered in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            yield child
            continue
        if lowered in {"article", "section", "div", "ul", "ol", "dl", "tbody", "thead", "tfoot", "tr"}:
            yield from _iter_provenance_tags(child)
            continue
        if child.get_text(" ", strip=True):
            yield child


def _text_quote_for_tag(tag, block_kind: str) -> Optional[str]:
    if block_kind not in _PROVENANCE_TEXT_KINDS:
        return None
    text = _normalize_ws(tag.get_text(" ", strip=True))
    return text or None


def _should_emit_provenance_tag(tag) -> bool:
    kind = _block_kind_for_tag(tag.name)
    if kind in _PROVENANCE_TEXT_KINDS:
        return bool(_text_quote_for_tag(tag, kind))
    return True


def _build_source_descriptors(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    descriptors: List[Dict[str, Any]] = []
    for page in pages:
        soup = BeautifulSoup(page.get("html") or "", "html.parser")
        page_number = _coerce_int(page.get("page_number") or page.get("page"))
        printed_page_number = _coerce_int(page.get("printed_page_number"))
        printed_page_label = page.get("printed_page_number_text") or (
            str(printed_page_number) if printed_page_number is not None else None
        )
        ordinal = 0
        for tag in _iter_provenance_tags(soup):
            if not _should_emit_provenance_tag(tag):
                continue
            ordinal += 1
            block_kind = _block_kind_for_tag(tag.name)
            descriptors.append(
                {
                    "block_kind": block_kind,
                    "page_number": page_number or 1,
                    "printed_page_number": printed_page_number,
                    "printed_page_label": printed_page_label,
                    "element_id": f"p{(page_number or 0):03d}-b{ordinal}",
                    "text_quote": _text_quote_for_tag(tag, block_kind),
                }
            )
    return descriptors


def _match_source_descriptor(tag, source_descriptors: List[Dict[str, Any]], start_idx: int):
    if not source_descriptors:
        return None, start_idx

    final_kind = _block_kind_for_tag(tag.name)
    final_text = _text_quote_for_tag(tag, final_kind) or ""

    if final_text:
        text_match, consumed_end = _match_source_descriptor_by_text(
            final_kind,
            final_text,
            source_descriptors,
            start_idx,
        )
        if text_match is not None:
            return text_match, consumed_end

    if start_idx >= len(source_descriptors):
        return None, start_idx

    found_idx = start_idx
    window_end = min(len(source_descriptors), start_idx + 8)
    while found_idx < window_end and source_descriptors[found_idx]["block_kind"] != final_kind:
        found_idx += 1
    if found_idx >= len(source_descriptors):
        return None, start_idx
    if found_idx >= window_end:
        found_idx = start_idx

    matched = dict(source_descriptors[found_idx])
    consumed_end = found_idx + 1
    source_element_ids = [matched["element_id"]]

    if final_kind in _PROVENANCE_TEXT_KINDS and final_text:
        combined_text = matched.get("text_quote") or ""
        while (
            combined_text
            and final_text != combined_text
            and final_text.startswith(combined_text)
            and consumed_end < len(source_descriptors)
            and source_descriptors[consumed_end]["block_kind"] == final_kind
        ):
            next_descriptor = source_descriptors[consumed_end]
            next_text = next_descriptor.get("text_quote") or ""
            candidate_text = _normalize_ws(f"{combined_text} {next_text}")
            if not candidate_text or not final_text.startswith(candidate_text):
                break
            combined_text = candidate_text
            source_element_ids.append(next_descriptor["element_id"])
            consumed_end += 1
        matched["text_quote"] = final_text

    matched["source_element_ids"] = source_element_ids
    return matched, consumed_end


def _source_descriptor_text_score(final_kind: str, final_text: str, descriptor: Dict[str, Any]) -> float:
    descriptor_text = descriptor.get("text_quote") or ""
    final_norm = _normalize_ws(final_text).casefold()
    descriptor_norm = _normalize_ws(descriptor_text).casefold()
    if not final_norm or not descriptor_norm:
        return 0.0
    final_numbers = set(re.findall(r"\b\d+\b", final_norm))
    descriptor_numbers = set(re.findall(r"\b\d+\b", descriptor_norm))
    numbers_conflict = bool(final_numbers and descriptor_numbers and final_numbers.isdisjoint(descriptor_numbers))
    if final_norm == descriptor_norm:
        base = 1.0
    elif descriptor_norm.startswith(final_norm + " ") or descriptor_norm.startswith(final_norm + ":"):
        base = 0.94
    elif final_norm.startswith(descriptor_norm + " ") or final_norm.startswith(descriptor_norm + ":"):
        base = 0.9
    elif len(final_norm) >= 8 and final_norm in descriptor_norm:
        base = 0.86
    elif len(descriptor_norm) >= 8 and descriptor_norm in final_norm:
        base = 0.84
    else:
        base = _descriptor_similarity(final_text, descriptor_text)
    if numbers_conflict:
        base = min(base, 0.35)
    if descriptor.get("block_kind") == final_kind:
        base += 0.04
    return min(base, 1.0)


def _match_source_descriptor_by_text(
    final_kind: str,
    final_text: str,
    source_descriptors: List[Dict[str, Any]],
    start_idx: int,
):
    search_start = 0
    search_end = len(source_descriptors)
    best_idx = None
    best_score = 0.0
    for idx in range(search_start, search_end):
        descriptor = source_descriptors[idx]
        score = _source_descriptor_text_score(final_kind, final_text, descriptor)
        if score < 0.78:
            continue
        distance = abs(idx - start_idx)
        adjusted = score - (distance * 0.001)
        if adjusted > best_score:
            best_score = adjusted
            best_idx = idx
    if best_idx is None:
        return None, start_idx
    matched = dict(source_descriptors[best_idx])
    matched["text_quote"] = final_text
    matched["source_element_ids"] = [matched["element_id"]]
    return matched, max(start_idx, best_idx + 1)


def _tag_entry_body(entry: Dict[str, Any], *, run_id: Optional[str], created_at: str):
    entry_id = Path(entry["filename"]).stem
    soup = BeautifulSoup(entry["body_html"] or "", "html.parser")
    source_descriptors = _build_source_descriptors(entry.get("prepared_pages") or [])
    page_metadata: Dict[int, Dict[str, Any]] = {}
    for page in entry.get("prepared_pages") or []:
        page_number = _coerce_int(page.get("page_number") or page.get("page"))
        if page_number is None:
            continue
        printed_page_number = _coerce_int(page.get("printed_page_number"))
        page_metadata[page_number] = {
            "printed_page_number": printed_page_number,
            "printed_page_label": page.get("printed_page_number_text")
            or (str(printed_page_number) if printed_page_number is not None else None),
        }
    source_idx = 0
    provenance_rows: List[Dict[str, Any]] = []

    final_tags = [tag for tag in _iter_provenance_tags(soup) if _should_emit_provenance_tag(tag)]
    fallback_source_page = (
        entry.get("source_pages", [None])[0]
        if entry.get("source_pages")
        else _coerce_int(entry.get("page_number"))
    )
    fallback_printed_page = (
        entry.get("source_printed_pages", [None])[0]
        if entry.get("source_printed_pages")
        else _coerce_int(entry.get("page_start"))
    )
    fallback_printed_label = str(fallback_printed_page) if fallback_printed_page is not None else None

    for ordinal, tag in enumerate(final_tags, start=1):
        block_id = f"blk-{entry_id}-{ordinal:04d}"
        tag["id"] = block_id
        matched, source_idx = _match_source_descriptor(tag, source_descriptors, source_idx)
        override_page = _coerce_int(tag.get("data-doc-web-source-page-number"))
        override_crop = _normalize_ws(tag.get("data-doc-web-source-crop-filename") or "")
        block_kind = _block_kind_for_tag(tag.name)
        text_quote = _text_quote_for_tag(tag, block_kind)
        if matched is None:
            matched = {
                "page_number": fallback_source_page or 1,
                "printed_page_number": fallback_printed_page,
                "printed_page_label": fallback_printed_label,
                "source_element_ids": [f"{entry_id}-b{ordinal:04d}"],
            }
        if override_page is not None:
            page_meta = page_metadata.get(override_page, {})
            source_element_ids = list(matched.get("source_element_ids") or [])
            if override_crop:
                crop_element_id = f"crop:{override_crop}"
                if crop_element_id not in source_element_ids:
                    source_element_ids.append(crop_element_id)
            matched["page_number"] = override_page
            matched["printed_page_number"] = page_meta.get("printed_page_number")
            matched["printed_page_label"] = page_meta.get("printed_page_label")
            matched["source_element_ids"] = source_element_ids or [f"{entry_id}-b{ordinal:04d}"]

        provenance_rows.append(
            {
                "schema_version": "doc_web_provenance_block_v1",
                "module_id": "build_chapter_html_v1",
                "run_id": run_id,
                "created_at": created_at,
                "block_id": block_id,
                "entry_id": entry_id,
                "block_kind": block_kind,
                "source_page_number": matched["page_number"],
                "source_element_ids": matched["source_element_ids"],
                "source_printed_page_number": matched.get("printed_page_number"),
                "source_printed_page_label": matched.get("printed_page_label"),
                "text_quote": text_quote,
            }
        )

    return soup.decode_contents(), provenance_rows


# ---------------------------------------------------------------------------
# Image attachment (T3, T4, T5)
# ---------------------------------------------------------------------------

def _page_sort_key(row: Dict[str, Any]) -> tuple:
    page_num = _source_page_number(row) or 0
    printed_num = _coerce_int(row.get("printed_page_number"))
    if printed_num is None:
        printed_num = page_num
    return (printed_num, page_num)


def _select_pages_for_portion(portion: Dict[str, Any], pages_sorted: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    page_start = _coerce_int(portion.get("page_start"))
    page_end = _coerce_int(portion.get("page_end")) or page_start
    source_pages = {
        page_num
        for page_num in (
            _coerce_int(value)
            for value in (portion.get("source_pages") or [])
        )
        if page_num is not None
    }
    source_matches = [page for page in pages_sorted if _source_page_number(page) in source_pages]

    # Source-only heading portions carry source-page coordinates, not printed-page ones.
    if portion.get("notes") == "heading-derived-source-pages" and source_matches:
        return source_matches

    if isinstance(page_start, int):
        printed_matches = [
            page
            for page in pages_sorted
            if isinstance(_coerce_int(page.get("printed_page_number")), int)
            and page_start <= _coerce_int(page.get("printed_page_number")) <= page_end
        ]
        if printed_matches:
            return printed_matches

    if source_matches:
        return source_matches

    if isinstance(page_start, int):
        return [
            page
            for page in pages_sorted
            if isinstance(_source_page_number(page), int)
            and page_start <= _source_page_number(page) <= page_end
        ]
    return []


def _page_already_covered(
    page: Dict[str, Any],
    *,
    covered_printed_pages: set[int],
    covered_source_pages: set[int],
) -> bool:
    printed_number = _coerce_int(page.get("printed_page_number"))
    source_number = _source_page_number(page)
    return (
        (printed_number is not None and printed_number in covered_printed_pages)
        or (source_number is not None and source_number in covered_source_pages)
    )


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _title_tokens(text: str) -> List[str]:
    normalized = _normalize_ws(text).casefold()
    normalized = normalized.replace("’", "'").replace("`", "'")
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    return [tok for tok in normalized.split() if tok]


def _titles_related(a: Optional[str], b: Optional[str]) -> bool:
    tokens_a = _title_tokens(a or "")
    tokens_b = _title_tokens(b or "")
    if not tokens_a or not tokens_b:
        return False

    def _tokens_match(left: str, right: str) -> bool:
        if left == right:
            return True
        if min(len(left), len(right)) <= 1:
            return False
        if left.startswith(right) or right.startswith(left):
            return True
        return SequenceMatcher(a=left, b=right).ratio() >= 0.83

    def _all_tokens_match(shorter: List[str], longer: List[str]) -> bool:
        return all(any(_tokens_match(token, candidate) for candidate in longer) for token in shorter)

    if len(tokens_a) <= len(tokens_b):
        return _all_tokens_match(tokens_a, tokens_b)
    return _all_tokens_match(tokens_b, tokens_a)


_NON_OWNER_HEADING_MARKERS = (
    "family",
    "grandchildren",
    "great grandchildren",
    "great great grandchildren",
    "descendants",
)


def _is_strong_owner_heading(text: str) -> bool:
    normalized = _normalize_ws(text)
    if not normalized or len(normalized) < 3 or len(normalized) > 160:
        return False
    lowered = normalized.casefold()
    if any(marker in lowered for marker in _NON_OWNER_HEADING_MARKERS):
        return False
    letters = sum(1 for ch in normalized if ch.isalpha())
    if letters / max(1, len(normalized)) < 0.3:
        return False
    return True


def _normalize_heading_breaks(html: str) -> str:
    if "<br" not in html:
        return html
    soup = BeautifulSoup(html, "html.parser")
    for heading in soup.find_all(re.compile(r"^h[1-6]$")):
        if not heading.find("br"):
            continue
        text = _normalize_ws(heading.get_text(" ", strip=True))
        heading.clear()
        heading.append(text)
    return soup.decode_contents()


_FLAT_HEADING_SENTENCE_RE = re.compile(r"[.!?](?=\s|$)")


def _looks_oversized_flat_heading(text: str) -> bool:
    normalized = _normalize_ws(text)
    if not normalized:
        return False
    if len(normalized) >= 180:
        return True
    if len(_FLAT_HEADING_SENTENCE_RE.findall(normalized)) >= 2:
        return True
    return False


_CATALOG_HEADING_WORDS = {
    "actions",
    "catalog",
    "card",
    "cards",
    "component",
    "components",
    "contents",
    "course",
    "courses",
    "element",
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
    "upgrade",
    "upgrades",
    "variants",
}


def _singular_heading_token(token: str) -> str:
    token = token.strip().casefold()
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 3 and token.endswith("s"):
        return token[:-1]
    return token


def _looks_catalog_category_heading(text: str) -> bool:
    normalized_tokens = [_singular_heading_token(token) for token in _title_tokens(text)]
    if any(token in _CATALOG_HEADING_WORDS for token in normalized_tokens):
        return True
    return ":" in text and any(token in _CATALOG_HEADING_WORDS for token in normalized_tokens[:3])


def _looks_redundant_catalog_marker_heading(text: str, title: str) -> bool:
    tokens = [_singular_heading_token(token) for token in _title_tokens(text)]
    if len(tokens) != 1:
        return False
    token = tokens[0]
    if token not in _CATALOG_HEADING_WORDS:
        return False
    title_tokens = {_singular_heading_token(title_token) for title_token in _title_tokens(title)}
    return token in title_tokens


def _text_until_next_heading(tag: Any, *, max_chars: int = 280) -> str:
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


def _looks_label_value_metadata(text: str) -> bool:
    labels = re.findall(r"\b[A-Z][A-Za-z0-9 /&-]{1,28}:", text or "")
    return len({label.casefold() for label in labels}) >= 2


def _heading_followed_by_label_values(tag: Any) -> bool:
    return _looks_label_value_metadata(_text_until_next_heading(tag))


def _looks_like_catalog_chapter(soup: BeautifulSoup, title: str) -> bool:
    if not _looks_catalog_category_heading(title):
        return False
    headings = soup.find_all(re.compile(r"^h[1-6]$"))
    if len(headings) < 4:
        return False
    label_value_runs = sum(1 for heading in headings if _heading_followed_by_label_values(heading))
    definition_terms = len(soup.find_all("dt"))
    return (label_value_runs + definition_terms) >= 2


def _polish_flat_chapter_headings(html: str, title: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    primary_heading_seen = False
    catalog_chapter = _looks_like_catalog_chapter(soup, title)

    for heading in soup.find_all(re.compile(r"^h[1-6]$")):
        text = _normalize_ws(heading.get_text(" ", strip=True))
        if not text:
            continue
        if not primary_heading_seen and _titles_related(text, title):
            primary_heading_seen = True
            continue
        if primary_heading_seen and catalog_chapter and _looks_redundant_catalog_marker_heading(text, title):
            heading.decompose()
            continue
        if primary_heading_seen and catalog_chapter and _looks_catalog_category_heading(text):
            heading.name = "h2"
            continue
        if _looks_oversized_flat_heading(text):
            heading.name = "p"
            classes = list(heading.get("class") or [])
            if "flattened-heading" not in classes:
                classes.append("flattened-heading")
            heading["class"] = classes
            continue
        if primary_heading_seen and heading.name in {"h1", "h2"}:
            if catalog_chapter:
                if _heading_followed_by_label_values(heading):
                    heading.name = "h3"
                elif heading.name == "h1":
                    heading.name = "h2"
                else:
                    heading.name = "h3"
            else:
                heading.name = "h3"

    return soup.decode_contents()


def _rebalance_repeated_generation_h1s(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    generation_h1_seen = False
    for heading in soup.find_all("h1"):
        text = _normalize_ws(heading.get_text(" ", strip=True))
        if not text or _is_strong_owner_heading(text):
            continue
        lowered = text.casefold()
        if not any(marker in lowered for marker in _NON_OWNER_HEADING_MARKERS):
            continue
        if not generation_h1_seen:
            generation_h1_seen = True
            continue
        heading.name = "h2"
    return soup.decode_contents()


def _first_strong_owner_heading(html: str) -> Optional[str]:
    soup = BeautifulSoup(html or "", "html.parser")
    for heading in soup.find_all("h1"):
        text = _normalize_ws(heading.get_text(" ", strip=True))
        if _is_strong_owner_heading(text):
            return text
    return None


def _starts_with_strong_h1(html: str, heading: Optional[str]) -> bool:
    if not heading:
        return False
    soup = BeautifulSoup(html or "", "html.parser")
    first = _first_significant_tag(soup)
    if not first or first.name != "h1":
        return False
    text = _normalize_ws(first.get_text(" ", strip=True))
    return text == heading


def _first_significant_tag(soup: BeautifulSoup):
    for child in soup.contents:
        name = getattr(child, "name", None)
        if name:
            return child
    return None


def _last_significant_tag(soup: BeautifulSoup):
    for child in reversed(soup.contents):
        name = getattr(child, "name", None)
        if name:
            return child
    return None


_DANGLING_END_WORDS = {
    "a", "after", "and", "as", "at", "be", "because", "before", "for", "from",
    "if", "in", "into", "near", "of", "on", "or", "our", "the", "their", "to",
    "was", "with",
}
_SENTENCE_END_RE = re.compile(r"[.!?\"')\]]$")


def _should_stitch_page_break(prev_text: str, next_text: str) -> bool:
    prev_norm = _normalize_ws(prev_text)
    next_norm = _normalize_ws(next_text)
    if not prev_norm or not next_norm:
        return False
    if _SENTENCE_END_RE.search(prev_norm):
        return False
    if next_norm[:1].islower():
        return True
    prev_tokens = _title_tokens(prev_norm)
    if prev_tokens and prev_tokens[-1] in _DANGLING_END_WORDS:
        return True
    return False


def _append_paragraph_children(dst, src) -> None:
    dst.append(" ")
    while src.contents:
        dst.append(src.contents[0].extract())


def _trailing_paragraph_before_figures(soup) -> Optional[Any]:
    last = _last_significant_tag(soup)
    if not last or last.name != "figure":
        return None
    first = last
    prev = _previous_significant_tag(first)
    while getattr(prev, "name", None) == "figure":
        first = prev
        prev = _previous_significant_tag(first)
    if getattr(prev, "name", None) == "p":
        return prev
    return None


def _stitch_page_breaks(page_htmls: List[str]) -> str:
    soups = [BeautifulSoup(html or "", "html.parser") for html in page_htmls if html]
    if not soups:
        return ""
    for idx in range(1, len(soups)):
        prev = soups[idx - 1]
        current = soups[idx]
        prev_last = _last_significant_tag(prev)
        current_first = _first_significant_tag(current)
        if not current_first or current_first.name != "p":
            continue
        prev_anchor = None
        if prev_last and prev_last.name == "p":
            prev_anchor = prev_last
        elif prev_last and prev_last.name == "figure":
            prev_anchor = _trailing_paragraph_before_figures(prev)
        if not prev_anchor:
            continue
        prev_text = prev_anchor.get_text(" ", strip=True)
        current_text = current_first.get_text(" ", strip=True)
        if _should_stitch_page_break(prev_text, current_text):
            _append_paragraph_children(prev_anchor, current_first)
            current_first.decompose()
    return "\n".join(soup.decode_contents() for soup in soups if soup.decode_contents().strip())


def _finalize_genealogy_body_html(html: str, *, enabled: bool) -> str:
    if not enabled:
        return html
    html = _merge_genealogy_tables_preserving_headings(html)
    html = _rebalance_repeated_generation_h1s(html)
    return html


def _related_title_index(heading: Optional[str], titles: List[str]) -> Optional[int]:
    if not heading:
        return None
    for idx, title in enumerate(titles):
        if _titles_related(heading, title):
            return idx
    return None


def _build_segment(
    title: str,
    portion_title: str,
    portion_page_start: int,
    pages: List[Dict[str, Any]],
    *,
    carry_back: bool = False,
) -> Dict[str, Any]:
    source_pages = [p["page_number"] for p in pages if isinstance(p.get("page_number"), int)]
    source_printed_pages = [
        p["printed_page_number"]
        for p in pages
        if isinstance(p.get("printed_page_number"), int)
    ]
    page_start = source_printed_pages[0] if source_printed_pages else (source_pages[0] if source_pages else None)
    page_end = source_printed_pages[-1] if source_printed_pages else (source_pages[-1] if source_pages else page_start)
    return {
        "title": title,
        "page_start": page_start,
        "page_end": page_end,
        "source_pages": source_pages,
        "source_printed_pages": source_printed_pages,
        "body_html": _stitch_page_breaks([p["html"] for p in pages]),
        "source_portion_title": portion_title,
        "source_portion_page_start": portion_page_start,
        "source_portion_titles": [portion_title],
        "source_portion_page_starts": [portion_page_start],
        "prepared_pages": [dict(page) for page in pages],
        "carry_back": carry_back,
    }


def _refine_chapter_segments(
    portion_title: str,
    portion_page_start: int,
    prepared_pages: List[Dict[str, Any]],
    candidate_titles: List[str],
    *,
    previous_title: Optional[str] = None,
    stale_portion: bool = False,
) -> List[Dict[str, Any]]:
    if not prepared_pages:
        return []

    segments: List[Dict[str, Any]] = []
    remaining_pages = list(prepared_pages)
    current_title = portion_title
    current_heading = None

    if previous_title:
        first_prev_heading_idx = None
        next_owner_idx = None

        for idx, page in enumerate(remaining_pages):
            heading = page.get("owner_heading")
            if not heading:
                continue

            heading_matches_prev = _titles_related(heading, previous_title)
            heading_matches_known_title = _related_title_index(heading, candidate_titles) is not None
            heading_starts_page = _starts_with_strong_h1(page.get("html") or "", heading)

            if first_prev_heading_idx is None:
                if heading_matches_prev:
                    first_prev_heading_idx = idx
                    continue
                break

            if not heading_matches_prev and (heading_matches_known_title or heading_starts_page):
                next_owner_idx = idx
                break

        if first_prev_heading_idx is not None:
            if next_owner_idx is None:
                return [
                    _build_segment(
                        previous_title,
                        portion_title,
                        portion_page_start,
                        remaining_pages,
                        carry_back=True,
                    )
                ]

            carry_back_pages = remaining_pages[:next_owner_idx]
            segments.append(
                _build_segment(
                    previous_title,
                    portion_title,
                    portion_page_start,
                    carry_back_pages,
                    carry_back=True,
                )
            )
            remaining_pages = remaining_pages[next_owner_idx:]
            next_heading = remaining_pages[0].get("owner_heading")
            current_title = next_heading or portion_title
            current_heading = next_heading

    if stale_portion:
        same_title_idx = None
        first_new_heading_idx = None
        first_new_heading = None

        for idx, page in enumerate(remaining_pages):
            heading = page.get("owner_heading")
            if not heading:
                continue

            if same_title_idx is None and _titles_related(heading, portion_title):
                same_title_idx = idx

            if first_new_heading_idx is not None:
                continue

            heading_matches_known_title = _related_title_index(heading, candidate_titles) is not None
            heading_starts_page = _starts_with_strong_h1(page.get("html") or "", heading)
            if not _titles_related(heading, portion_title) and (heading_matches_known_title or heading_starts_page):
                first_new_heading_idx = idx
                first_new_heading = heading

        if first_new_heading_idx is not None and (
            same_title_idx is None or first_new_heading_idx < same_title_idx
        ):
            carry_back_pages = remaining_pages[:first_new_heading_idx]
            if carry_back_pages:
                segments.append(
                    _build_segment(
                        portion_title,
                        portion_title,
                        portion_page_start,
                        carry_back_pages,
                        carry_back=True,
                    )
                )
            remaining_pages = remaining_pages[first_new_heading_idx:]
            current_title = first_new_heading or portion_title
            current_heading = first_new_heading
        elif same_title_idx is None:
            return [
                _build_segment(
                    portion_title,
                    portion_title,
                    portion_page_start,
                    remaining_pages,
                    carry_back=True,
                )
            ]

    if not remaining_pages:
        return segments

    current_pages: List[Dict[str, Any]] = []

    for page in remaining_pages:
        heading = page.get("owner_heading")
        heading_matches_known_title = bool(
            heading and any(_titles_related(heading, title) for title in candidate_titles)
        )
        heading_starts_page = _starts_with_strong_h1(page.get("html") or "", heading)
        if (
            heading
            and heading_matches_known_title
            and current_pages
            and current_heading
            and not _titles_related(heading, current_heading)
        ):
            segments.append(_build_segment(current_title, portion_title, portion_page_start, current_pages))
            current_pages = []
            current_title = heading
            current_heading = heading

        if heading and current_heading is None and (heading_matches_known_title or (not current_pages and heading_starts_page)):
            current_title = heading
            current_heading = heading

        current_pages.append(page)

    if current_pages:
        segments.append(_build_segment(current_title, portion_title, portion_page_start, current_pages))

    return segments


def _candidate_titles_for_refinement(
    portions: List[Dict[str, Any]],
    portion_idx: int,
    current_page_end: Optional[int],
) -> List[str]:
    """Return titles that can start within the current portion's page range."""
    titles: List[str] = []
    for idx, portion in enumerate(portions[portion_idx:], start=portion_idx):
        title = portion.get("title") or portion.get("portion_id") or ""
        if not title:
            continue
        start = _coerce_int(portion.get("page_start"))
        if idx == portion_idx or current_page_end is None or start is None or start <= current_page_end:
            titles.append(title)
    return titles


def _extend_unique(existing: Optional[List[Any]], new_values: Optional[List[Any]]) -> List[Any]:
    merged = list(existing or [])
    for value in new_values or []:
        if value not in merged:
            merged.append(value)
    return merged


def _merge_carry_back_segment(entry: Dict[str, Any], segment: Dict[str, Any]) -> None:
    entry["body_html"] = _stitch_page_breaks([entry.get("body_html") or "", segment.get("body_html") or ""])
    if segment.get("page_end") is not None:
        entry["page_end"] = segment["page_end"]
    entry["prepared_pages"] = list(entry.get("prepared_pages") or []) + list(segment.get("prepared_pages") or [])
    entry["source_pages"] = _extend_unique(entry.get("source_pages"), segment.get("source_pages"))
    entry["source_printed_pages"] = _extend_unique(
        entry.get("source_printed_pages"),
        segment.get("source_printed_pages"),
    )
    entry["source_portion_titles"] = _extend_unique(
        entry.get("source_portion_titles") or [entry.get("source_portion_title")],
        segment.get("source_portion_titles") or [segment.get("source_portion_title")],
    )
    entry["source_portion_page_starts"] = _extend_unique(
        entry.get("source_portion_page_starts") or [entry.get("source_portion_page_start")],
        segment.get("source_portion_page_starts") or [segment.get("source_portion_page_start")],
    )


def _group_manifest_by_page(manifest_path: str) -> Dict[int, List[Dict[str, Any]]]:
    grouped: Dict[int, List[Dict[str, Any]]] = {}
    for row in read_jsonl(manifest_path):
        page = row.get("source_page")
        if not isinstance(page, int):
            continue
        grouped.setdefault(page, []).append(row)
    for rows in grouped.values():
        rows[:] = _sort_crop_rows_reading_order(rows)
    return grouped


def _sort_crop_rows_reading_order(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort crop records by visual rows, then x-position within each row."""
    if not rows:
        return rows

    def _bbox(row: Dict[str, Any]) -> Dict[str, Any]:
        return row.get("bbox") or {}

    heights = []
    for row in rows:
        bbox = _bbox(row)
        height = _coerce_int(bbox.get("height"))
        if height is None:
            y0 = _coerce_int(bbox.get("y0")) or 0
            y1 = _coerce_int(bbox.get("y1")) or y0
            height = max(1, y1 - y0)
        heights.append(max(1, height))
    median_height = sorted(heights)[len(heights) // 2]
    row_tolerance = max(20, int(median_height * 0.35))

    def _center_y(row: Dict[str, Any]) -> float:
        bbox = _bbox(row)
        y0 = _coerce_int(bbox.get("y0")) or 0
        y1 = _coerce_int(bbox.get("y1")) or y0
        return (y0 + y1) / 2.0

    def _top_y(row: Dict[str, Any]) -> int:
        return _coerce_int(_bbox(row).get("y0")) or 0

    def _x0(row: Dict[str, Any]) -> int:
        return _coerce_int(_bbox(row).get("x0")) or 0

    rows_by_center = sorted(rows, key=lambda row: (_center_y(row), _x0(row), row.get("filename") or ""))
    visual_rows: List[List[Dict[str, Any]]] = []
    for row in rows_by_center:
        center_y = _center_y(row)
        top_y = _top_y(row)
        for visual_row in visual_rows:
            row_center = sum(_center_y(item) for item in visual_row) / float(len(visual_row))
            row_top = min(_top_y(item) for item in visual_row)
            if abs(center_y - row_center) <= row_tolerance or abs(top_y - row_top) <= row_tolerance:
                visual_row.append(row)
                break
        else:
            visual_rows.append([row])

    visual_rows.sort(key=lambda visual_row: min(_coerce_int(_bbox(row).get("y0")) or 0 for row in visual_row))
    sorted_rows: List[Dict[str, Any]] = []
    for visual_row in visual_rows:
        sorted_rows.extend(sorted(visual_row, key=lambda row: (_x0(row), row.get("filename") or "")))
    return sorted_rows


def _refresh_published_illustration_images(
    crops_by_page: Dict[int, List[Dict[str, Any]]],
    crops_dir: Path,
    images_dir: Path,
) -> Set[str]:
    """Copy current illustration assets and prune files not in the current manifest."""
    ensure_dir(str(images_dir))
    copied_filenames: Set[str] = set()
    for rows in crops_by_page.values():
        for row in rows:
            filename = row.get("filename")
            if not filename:
                continue
            src_path = crops_dir / filename
            if not src_path.exists():
                row.pop("_source_path", None)
                continue
            row["_source_path"] = str(src_path)
            dst_path = images_dir / filename
            dst_path.write_bytes(src_path.read_bytes())
            copied_filenames.add(filename)

    for old_path in images_dir.iterdir():
        if not old_path.is_file():
            continue
        if old_path.name in copied_filenames:
            continue
        old_path.unlink()

    return copied_filenames


_MAX_CAPTION_WORDS = 30

# Patterns that strongly suggest a caption (names, dates, descriptive labels)
_CAPTION_PATTERNS = re.compile(
    r"""
    \b\d{4}\b                              # year (1920, 2024)
    | \b[Cc]irca\b                         # "circa 1920"
    | \b[Aa]bout\s+\d{4}\b                # "about 1910"
    | \b(?:[Bb]ack|[Ff]ront|[Ll]eft|[Rr]ight)\s+[Rr]ow\b  # "Back Row:"
    | \b[Ll]eft\s+to\s+[Rr]ight\b         # "Left to right:"
    """,
    re.VERBOSE,
)


def _is_likely_caption(text: str) -> bool:
    """Heuristic: short text near an image is likely a caption.

    Captions typically contain proper nouns (names), dates, or descriptive labels.
    Generic short prose ("More text.", "He walked on.") should not be absorbed.
    """
    text = text.strip()
    if not text:
        return False
    words = text.split()
    if len(words) > _MAX_CAPTION_WORDS:
        return False
    # Must have caption-like content (names, dates, descriptive labels)
    if _CAPTION_PATTERNS.search(text):
        return True
    # Short text with multiple capitalized words (proper nouns, not sentence-start)
    # e.g., "Moise and Sophie's Family" but not "More text."
    if len(words) <= 8:
        caps = [w for w in words if w and w[0].isupper() and len(w) > 1]
        if len(caps) >= 2:
            return True
    return False


def _peek_caption_siblings(node) -> List[str]:
    """Return caption-like <p> sibling text without mutating the tree."""
    from bs4 import NavigableString

    texts: List[str] = []
    sibling = node.next_sibling

    while isinstance(sibling, NavigableString) and not sibling.strip():
        sibling = sibling.next_sibling

    for _ in range(2):
        if sibling is None or sibling.name != "p":
            break
        text = sibling.get_text(" ", strip=True)
        if not _is_likely_caption(text):
            break
        texts.append(text)
        sibling = sibling.next_sibling
        while isinstance(sibling, NavigableString) and not sibling.strip():
            sibling = sibling.next_sibling

    return texts


def _crop_match_texts(crop: Dict[str, Any]) -> List[str]:
    """Prefer crop-pipeline descriptions; fall back to OCR alt only if needed."""
    texts = []
    image_description = _normalize_ws(crop.get("image_description") or "")
    caption_text = _normalize_ws(crop.get("caption_text") or "")
    alt = _normalize_ws(crop.get("alt") or "")
    if image_description:
        texts.append(image_description)
    if caption_text:
        texts.append(caption_text)
    if not texts and alt:
        texts.append(alt)
    return texts


def _crop_nearby_texts(crop: Dict[str, Any]) -> List[str]:
    texts: List[str] = []
    for key in ("nearby_text", "expected_visual_contents"):
        value = crop.get(key)
        if isinstance(value, (list, tuple)):
            raw_text = " ".join(str(item) for item in value)
        elif isinstance(value, dict):
            raw_text = " ".join(str(item) for item in value.values())
        else:
            raw_text = str(value or "")
        text = _normalize_ws(raw_text)
        if text:
            texts.append(text)
    for text in _crop_match_texts(crop):
        segments = [
            _normalize_ws(segment)
            for segment in re.split(r"\s+[—–]\s+", text)
            if _normalize_ws(segment)
        ]
        if len(segments) >= 3:
            texts.extend(segments[1:-1])
        elif len(segments) == 2:
            texts.append(segments[1])
    deduped: List[str] = []
    seen: Set[str] = set()
    for text in texts:
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(text)
    return deduped


_TEXT_SEMANTIC_CROP_ROLES = {"summary_reference"}
_ORPHAN_INSERTABLE_CROP_ROLES = {
    "board_element",
    "card_face",
    "card_reference",
    "component_reference",
    "icon_reference",
    "map_or_board",
    "rule_example_diagram",
    "setup_diagram",
}


def _role_from_crop(crop: Dict[str, Any]) -> str:
    role = crop.get("critical_graphics_role") or crop.get("role") or ""
    if role:
        return str(role)
    text = " ".join(_crop_match_texts(crop)).casefold()
    if "summary reference" in text:
        return "summary_reference"
    if "card face" in text:
        return "card_face"
    if "map or board" in text:
        return "map_or_board"
    if "rule example diagram" in text:
        return "rule_example_diagram"
    if "component reference" in text:
        return "component_reference"
    if "board element" in text:
        return "board_element"
    return ""


def _importance_from_crop(crop: Dict[str, Any]) -> str:
    return str(crop.get("critical_graphics_importance") or crop.get("importance") or "").casefold()


def _semantic_text_contains_crop(crop: Dict[str, Any], soup) -> bool:
    """Return true when a text-heavy crop is already represented in page HTML."""
    page_text_tokens = {
        token
        for token in _title_tokens(soup.get_text(" ", strip=True))
        if len(token) > 2
    }
    if not page_text_tokens:
        return False
    crop_tokens = {
        token
        for text in _crop_match_texts(crop)
        for token in _title_tokens(text)
        if len(token) > 2 and token not in _DESCRIPTOR_GENERIC_TOKENS
    }
    if not crop_tokens:
        return False
    return len(crop_tokens & page_text_tokens) / len(crop_tokens) >= 0.6


def _is_redundant_page_snapshot_crop(crop: Dict[str, Any], soup) -> bool:
    if _role_from_crop(crop) or _importance_from_crop(crop) or crop.get("critical_graphics_target_id"):
        return False
    try:
        area_ratio = float(crop.get("area_ratio") or 0.0)
    except (TypeError, ValueError):
        area_ratio = 0.0
    if area_ratio < 0.85:
        return False
    page_tokens = [
        token
        for token in _title_tokens(soup.get_text(" ", strip=True))
        if len(token) > 2
    ]
    return len(page_tokens) >= 40


def _should_skip_source_pixel_crop(crop: Dict[str, Any], soup) -> bool:
    if _is_redundant_page_snapshot_crop(crop, soup):
        return True
    role = _role_from_crop(crop)
    if role not in _TEXT_SEMANTIC_CROP_ROLES:
        return False
    if _importance_from_crop(crop) != "essential":
        return True
    return _semantic_text_contains_crop(crop, soup)


def _block_match_texts(tag) -> List[str]:
    texts = []
    alt = _normalize_ws(tag.get("alt") or "")
    if alt:
        texts.append(alt)
    parent = tag.parent
    if parent and parent.name == "figure":
        figcaption = parent.find("figcaption")
        if figcaption:
            caption = _normalize_ws(figcaption.get_text(" ", strip=True))
            if caption:
                texts.append(caption)
    else:
        texts.extend(_peek_caption_siblings(tag))
    return texts


_TEXT_ONLY_CALLOUT_RE = re.compile(
    r"\b(?:callout|don['’]?t\s+forget|important|note|reminder|remember|warning)\b",
    re.IGNORECASE,
)
_STRONG_CALLOUT_CUE_RE = re.compile(
    r"\b(?:after|before|complete|must|remember|warning|important|note|players?|turn|phase|return|discard)\b",
    re.IGNORECASE,
)


def _is_text_only_callout_placeholder(tag) -> bool:
    """Detect OCR image placeholders that are actually styled text callouts."""
    alt = _normalize_ws(tag.get("alt") or "")
    parent = tag.parent
    caption = ""
    if parent and parent.name == "figure":
        figcaption = parent.find("figcaption")
        if figcaption:
            caption = _normalize_ws(figcaption.get_text(" ", strip=True))
    if not caption:
        return False
    combined = f"{alt} {caption}"
    return bool(_TEXT_ONLY_CALLOUT_RE.search(combined))


def _build_semantic_callout(soup, text: str, *, kind: str = "note"):
    aside = soup.new_tag("aside")
    aside["class"] = ["semantic-callout", f"semantic-callout-{kind}"]
    aside["role"] = "note"
    aside["data-doc-web-semantic"] = "text-callout"
    aside["data-callout-kind"] = kind
    paragraph = soup.new_tag("p")
    paragraph.string = text
    aside.append(paragraph)
    return aside


def _paragraph_is_fully_strong(tag) -> bool:
    if getattr(tag, "name", None) != "p":
        return False
    if tag.find_parent(["figure", "figcaption", "li", "dd", "table", "nav"]):
        return False
    text = _normalize_ws(tag.get_text(" ", strip=True))
    if len(text) < 60:
        return False
    strong_text = _normalize_ws(" ".join(strong.get_text(" ", strip=True) for strong in tag.find_all("strong")))
    if not strong_text:
        return False
    return text == strong_text and bool(_STRONG_CALLOUT_CUE_RE.search(text))


def _promote_text_callout_paragraphs(soup) -> int:
    promoted = 0
    for paragraph in list(soup.find_all("p")):
        if not _paragraph_is_fully_strong(paragraph):
            continue
        text = _normalize_ws(paragraph.get_text(" ", strip=True))
        paragraph.replace_with(_build_semantic_callout(soup, text, kind="important"))
        promoted += 1
    return promoted


def _text_overlap_ratio(text: str, crop_tokens: set[str]) -> float:
    tokens = [
        token
        for token in _title_tokens(text)
        if len(token) > 1
    ]
    if not tokens or not crop_tokens:
        return 0.0
    matched = sum(1 for token in tokens if token in crop_tokens)
    return matched / float(len(tokens))


@lru_cache(maxsize=256)
def _ocr_crop_text(image_path: str) -> str:
    if not image_path:
        return ""
    try:
        import pytesseract
        from PIL import Image
    except Exception:
        return ""
    try:
        with Image.open(image_path) as img:
            return _normalize_ws(pytesseract.image_to_string(img))
    except Exception:
        return ""


def _suppress_duplicate_text_after_figure(figure, crop: Dict[str, Any]) -> bool:
    if not crop.get("contains_text"):
        return False
    image_path = crop.get("_source_path") or ""
    crop_text = _ocr_crop_text(str(image_path))
    crop_tokens = {
        token
        for token in _title_tokens(crop_text)
        if len(token) > 1
    }
    if not crop_tokens:
        return False

    removed_any = False
    sibling = _next_significant_tag(figure)
    while getattr(sibling, "name", None) == "p":
        paragraph_text = _normalize_ws(sibling.get_text(" ", strip=True))
        paragraph_lines = [
            _normalize_ws(line)
            for line in sibling.get_text("\n", strip=True).split("\n")
            if _normalize_ws(line)
        ]
        if not paragraph_text or not paragraph_lines:
            break
        overall_overlap = _text_overlap_ratio(paragraph_text, crop_tokens)
        line_overlaps = [_text_overlap_ratio(line, crop_tokens) for line in paragraph_lines]
        if overall_overlap < 0.6 or min(line_overlaps) < 0.5 or max(line_overlaps) < 0.8:
            break
        next_sibling = _next_significant_tag(sibling)
        sibling.decompose()
        sibling = next_sibling
        removed_any = True

    if removed_any:
        figure["data-text-dedup-source"] = "crop-ocr"
    return removed_any


def _descriptor_similarity(a: str, b: str) -> float:
    a_norm = _normalize_ws(a).casefold()
    b_norm = _normalize_ws(b).casefold()
    if not a_norm or not b_norm:
        return 0.0
    if a_norm == b_norm:
        return 1.0
    ratio = SequenceMatcher(None, a_norm, b_norm).ratio()
    tokens_a = set(_title_tokens(a_norm))
    tokens_b = set(_title_tokens(b_norm))
    overlap = 0.0
    if tokens_a and tokens_b:
        overlap = len(tokens_a & tokens_b) / max(len(tokens_a), len(tokens_b))
    base = max(ratio, overlap)

    label_a = _descriptor_label_tokens(a)
    label_b = _descriptor_label_tokens(b)
    if label_a and label_b:
        label_overlap = len(label_a & label_b) / max(len(label_a), len(label_b))
        if label_overlap > 0:
            return max(base, 0.75 + (0.25 * label_overlap))
        return min(base, 0.12)
    return base


_DESCRIPTOR_LABEL_RE = re.compile(
    r"\b(?:titled|title|named|labeled|labelled|for)\s+([A-Z][A-Za-z0-9'’ -]{1,60})"
)
_DESCRIPTOR_LABEL_STOP_RE = re.compile(r"\s+(?:cost|effect|shows?|with|on|in|from)\b", re.IGNORECASE)
_DESCRIPTOR_GENERIC_TOKENS = {
    "a",
    "an",
    "and",
    "art",
    "card",
    "cards",
    "component",
    "components",
    "course",
    "diagram",
    "element",
    "elements",
    "face",
    "figure",
    "graphic",
    "graphics",
    "image",
    "images",
    "icon",
    "icons",
    "line",
    "of",
    "order",
    "labeled",
    "labelled",
    "layout",
    "layouts",
    "marker",
    "reference",
    "references",
    "space",
    "spaces",
    "sight",
    "temporary",
    "reference",
    "titled",
    "upgrade",
    "upgrades",
    "visual",
    "with",
}


def _descriptor_label_tokens(text: str) -> set[str]:
    """Extract explicit labels like "titled X" or "face for X" for matching."""
    raw = _normalize_ws(text)
    for match in _DESCRIPTOR_LABEL_RE.finditer(raw):
        candidate = match.group(1)
        candidate = re.split(r"\s+[—–-]\s+|[.:;,|]", candidate, maxsplit=1)[0]
        candidate = _DESCRIPTOR_LABEL_STOP_RE.split(candidate, maxsplit=1)[0]
        tokens = {
            token
            for token in _title_tokens(candidate)
            if _is_label_token(token)
        }
        if tokens:
            return tokens
    return set()


def _token_key(token: str) -> str:
    token = token.casefold().replace("’", "'")
    if len(token) > 3 and token.endswith("s"):
        return token[:-1]
    return token


def _is_label_token(token: str) -> bool:
    if token in _DESCRIPTOR_GENERIC_TOKENS:
        return False
    return len(token) > 1 or token.isdigit() or (len(token) == 1 and token.isalpha())


def _normalized_token_set(text: str) -> set[str]:
    return {
        _token_key(token)
        for token in _title_tokens(text)
        if _is_label_token(token)
    }


_LABEL_START_STOP_WORDS = {
    "Add",
    "Choose",
    "Cost",
    "Deal",
    "Draw",
    "Effect",
    "End",
    "Execute",
    "Get",
    "If",
    "Move",
    "Repeat",
    "Replace",
    "Robots",
    "Take",
    "When",
    "You",
}


def _leading_title_tokens(text: str) -> set[str]:
    words: List[str] = []
    for raw in _normalize_ws(text).split():
        cleaned = raw.strip("()[]{}.,:;\"'“”‘’")
        if not cleaned:
            break
        if cleaned in _LABEL_START_STOP_WORDS:
            break
        if cleaned[0].isupper() or cleaned.isupper():
            words.append(cleaned)
            continue
        break
    if not words or len(words) > 4:
        return set()
    return _normalized_token_set(" ".join(words))


def _crop_label_tokens(crop: Dict[str, Any]) -> set[str]:
    """Infer the compact subject label for matching orphan crops to text blocks."""
    role = _role_from_crop(crop)
    for text in _crop_match_texts(crop):
        if role in {"board_element", "card_face", "card_reference", "component_reference", "icon_reference"}:
            for segment in re.split(r"\s+[—–]\s+", text)[1:]:
                leading = _leading_title_tokens(segment)
                if leading:
                    return leading
        explicit = {_token_key(token) for token in _descriptor_label_tokens(text)}
        if explicit:
            return explicit
        head = re.split(r"\s+[—–]\s+|;|\bCost:\b|\bEffect:\b", text, maxsplit=1)[0]
        head = re.sub(r"\bboard\s+elements?\b", " ", head, flags=re.IGNORECASE)
        head = re.sub(r"\bboard\s+space\b", "space", head, flags=re.IGNORECASE)
        head = re.sub(r"\bwith\s+activation[- ]order\s+marker\s+\d+\b", " ", head, flags=re.IGNORECASE)
        head = re.sub(
            r"\b(?:upgrade|temporary|special|programming|damage|space|reference|"
            r"image|icon|diagram|example|layout|course|card|face|component|marker|activation[- ]order)\b",
            " ",
            head,
            flags=re.IGNORECASE,
        )
        tokens = _normalized_token_set(head)
        if tokens:
            return tokens
    return set()


def _anchor_text(tag) -> str:
    if getattr(tag, "name", None) == "dt":
        return _normalize_ws(tag.get_text(" ", strip=True))
    if getattr(tag, "name", None) == "li":
        return _normalize_ws(tag.get_text(" ", strip=True))
    if getattr(tag, "name", None) == "p":
        return _normalize_ws(tag.get_text(" ", strip=True))
    if getattr(tag, "name", None) in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        return _normalize_ws(tag.get_text(" ", strip=True))
    return ""


def _anchor_label_text(tag) -> str:
    if getattr(tag, "name", None) == "dt":
        return _normalize_ws(tag.get_text(" ", strip=True))
    if getattr(tag, "name", None) == "li":
        strong = tag.find("strong")
        if strong:
            return _normalize_ws(strong.get_text(" ", strip=True))
    if getattr(tag, "name", None) == "p":
        strong = tag.find("strong")
        if strong:
            return _normalize_ws(strong.get_text(" ", strip=True))
    if getattr(tag, "name", None) in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        return _normalize_ws(tag.get_text(" ", strip=True))
    return ""


def _orphan_anchor_score(crop: Dict[str, Any], tag) -> float:
    anchor = _anchor_text(tag)
    if not anchor:
        return 0.0
    best = max(
        (_descriptor_similarity(text, anchor) for text in _crop_match_texts(crop)),
        default=0.0,
    )
    crop_label = _crop_label_tokens(crop)
    anchor_label_tokens = _normalized_token_set(_anchor_label_text(tag))
    label_conflict = False
    if crop_label and anchor_label_tokens:
        label_overlap = len(crop_label & anchor_label_tokens) / len(crop_label)
        label_conflict = label_overlap < 0.75
        if label_overlap < 0.75:
            best = min(best, 0.6 + (0.2 * label_overlap))
        if label_overlap >= 0.999:
            best = max(best, 0.98)
        elif label_overlap:
            best = max(best, 0.64 + (0.24 * label_overlap))
    anchor_tokens = _normalized_token_set(anchor)
    if crop_label and anchor_tokens and not anchor_label_tokens:
        overlap = len(crop_label & anchor_tokens) / len(crop_label)
        if overlap:
            best = max(best, 0.72 + (0.28 * overlap))
    if crop_label and not anchor_label_tokens:
        best = min(best, 0.6)
    anchor_tokens = _normalized_token_set(anchor)
    if anchor_tokens and not label_conflict:
        for nearby_text in _crop_nearby_texts(crop):
            nearby_tokens = _normalized_token_set(nearby_text)
            if not nearby_tokens:
                continue
            overlap = len(anchor_tokens & nearby_tokens)
            if overlap < 3:
                continue
            compact_coverage = overlap / float(max(1, min(len(anchor_tokens), len(nearby_tokens))))
            if overlap >= 4 and compact_coverage >= 0.65:
                best = max(best, 0.96)
            elif compact_coverage >= 0.5:
                best = max(best, 0.82)
    return best


def _anchor_priority(tag) -> int:
    name = getattr(tag, "name", None)
    if name in {"dt", "li", "p"}:
        return 3
    if name in {"h2", "h3", "h4", "h5", "h6"}:
        return 2
    if name == "h1":
        return 1
    return 0


def _best_anchor_for_orphan_crop(soup, crop: Dict[str, Any]):
    best_tag = None
    best_score = 0.0
    best_priority = 0
    candidates = soup.find_all(["dt", "h1", "h2", "h3", "h4", "h5", "h6", "li", "p"])
    for tag in candidates:
        if tag.find_parent("figure"):
            continue
        score = _orphan_anchor_score(crop, tag)
        priority = _anchor_priority(tag)
        if score > best_score + 0.02 or (abs(score - best_score) <= 0.02 and priority > best_priority):
            best_score = score
            best_tag = tag
            best_priority = priority
    if best_score >= 0.34:
        return best_tag
    return None


def _extend_anchor_through_nearby_text_run(anchor, crop: Dict[str, Any]):
    if getattr(anchor, "name", None) != "p":
        return anchor
    if getattr(anchor.parent, "name", None) in {"li", "dd"}:
        return anchor

    nearby_tokens: Set[str] = set()
    for text in _crop_nearby_texts(crop):
        nearby_tokens.update(_normalized_token_set(text))
    if len(nearby_tokens) < 5:
        return anchor

    current = anchor
    for _ in range(4):
        sibling = _next_significant_tag(current)
        if getattr(sibling, "name", None) != "p":
            break
        sibling_tokens = _normalized_token_set(sibling.get_text(" ", strip=True))
        if len(sibling_tokens) < 3:
            break
        overlap = len(sibling_tokens & nearby_tokens)
        coverage = overlap / float(max(1, len(sibling_tokens)))
        if not ((overlap >= 4 and coverage >= 0.5) or (overlap >= 3 and coverage >= 0.75)):
            break
        current = sibling
    return current


def _build_crop_figure(soup, crop: Dict[str, Any], rel_src: str):
    filename = crop.get("filename")
    if not filename:
        return None
    figure = soup.new_tag("figure")
    figure["data-placement"] = "inferred-essential"
    figure["class"] = ["inferred-essential-figure"]
    img = soup.new_tag("img")
    img["src"] = f"{rel_src}/{filename}"
    img["alt"] = crop.get("image_description") or crop.get("alt") or ""
    img["data-crop-filename"] = filename
    _annotate_img_from_crop(img, crop)
    figure.append(img)
    _annotate_figure_from_crop(figure, crop)
    return figure


def _annotate_img_from_crop(img, crop: Dict[str, Any]) -> None:
    source_page = _coerce_int(crop.get("source_page"))
    filename = crop.get("filename")
    if source_page is not None:
        img["data-doc-web-source-page-number"] = str(source_page)
    if filename:
        img["data-doc-web-source-crop-filename"] = str(filename)
    role = _role_from_crop(crop)
    importance = _importance_from_crop(crop)
    target_id = crop.get("critical_graphics_target_id")
    nearby_text = _normalize_ws(crop.get("nearby_text") or "")
    if role:
        img["data-critical-graphics-role"] = role
    if importance:
        img["data-critical-graphics-importance"] = importance
    if target_id:
        img["data-critical-graphics-target-id"] = str(target_id)
    if nearby_text:
        img["data-critical-graphics-nearby-text"] = nearby_text


def _annotate_figure_from_crop(figure, crop: Dict[str, Any]) -> None:
    role = _role_from_crop(crop)
    importance = _importance_from_crop(crop)
    source_page = _coerce_int(crop.get("source_page"))
    filename = crop.get("filename")
    if source_page is not None:
        figure["data-doc-web-source-page-number"] = str(source_page)
    if filename:
        figure["data-doc-web-source-crop-filename"] = str(filename)
    if role:
        figure["data-critical-graphics-role"] = role
    if importance:
        figure["data-critical-graphics-importance"] = importance
    target_id = crop.get("critical_graphics_target_id")
    if target_id:
        figure["data-critical-graphics-target-id"] = str(target_id)


def _insert_figure_near_anchor(figure, anchor) -> None:
    if anchor is None:
        return

    def insert_after_existing_figure_run(base) -> None:
        sibling = _next_significant_tag(base)
        last_figure = None
        while getattr(sibling, "name", None) == "figure":
            last_figure = sibling
            sibling = _next_significant_tag(sibling)
        if last_figure is not None:
            last_figure.insert_after(figure)
        else:
            base.insert_after(figure)

    name = getattr(anchor, "name", None)
    if name == "dt":
        dd = _next_significant_tag(anchor)
        if getattr(dd, "name", None) == "dd":
            dd.insert(0, figure)
        else:
            anchor.insert_before(figure)
        return
    if name == "dd":
        anchor.insert(0, figure)
        return
    if name == "li":
        first_paragraph = anchor.find("p", recursive=False)
        if first_paragraph:
            first_paragraph.insert_after(figure)
        else:
            anchor.append(figure)
        return
    if name == "p" and getattr(anchor.parent, "name", None) in {"li", "dd"}:
        if anchor.parent.name == "li":
            insert_after_existing_figure_run(anchor)
        else:
            anchor.parent.insert(0, figure)
        return
    if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        insert_after_existing_figure_run(anchor)
        return
    if name == "p":
        insert_after_existing_figure_run(anchor)
        return
    anchor.insert_before(figure)


def _append_orphan_figure(soup, figure) -> None:
    container = soup.find(["article", "body"]) or soup
    container.append(figure)


def _node_appears_after(anchor, node) -> bool:
    for candidate in node.next_elements:
        if candidate is anchor:
            return True
    return False


def _insert_split_figure_near_anchor(figure, anchor, original_figure) -> None:
    if anchor is None:
        return
    if getattr(anchor, "name", None) == "p" and _node_appears_after(anchor, original_figure):
        anchor.insert_before(figure)
        return
    _insert_figure_near_anchor(figure, anchor)


def _crop_from_img_tag(img) -> Dict[str, Any]:
    parent = img.find_parent("figure") if img is not None else None
    source_page = _coerce_int(
        img.get("data-doc-web-source-page-number")
        or (parent.get("data-doc-web-source-page-number") if parent else None)
    )
    filename = img.get("data-crop-filename") or img.get("data-doc-web-source-crop-filename")
    return {
        "filename": filename,
        "image_description": img.get("alt") or "",
        "alt": img.get("alt") or "",
        "source_page": source_page,
        "nearby_text": img.get("data-critical-graphics-nearby-text") or "",
        "critical_graphics_role": (
            img.get("data-critical-graphics-role")
            or (parent.get("data-critical-graphics-role") if parent else None)
            or _role_from_crop({"image_description": img.get("alt") or ""})
        ),
        "critical_graphics_importance": (
            img.get("data-critical-graphics-importance")
            or (parent.get("data-critical-graphics-importance") if parent else None)
            or "essential"
        ),
        "critical_graphics_target_id": (
            img.get("data-critical-graphics-target-id")
            or (parent.get("data-critical-graphics-target-id") if parent else None)
        ),
    }


def _split_labeled_multi_image_figures(soup) -> int:
    """Move multi-image placeholder runs to nearby semantic labels when possible."""
    moved = 0
    for figure in list(soup.find_all("figure")):
        imgs = [img for img in figure.find_all("img", recursive=False) if img.get("src")]
        if len(imgs) < 2:
            continue
        for img in list(imgs):
            crop = _crop_from_img_tag(img)
            if not crop.get("filename"):
                continue
            anchor = _best_anchor_for_orphan_crop(soup, crop)
            if anchor is None:
                continue
            if _orphan_anchor_score(crop, anchor) < 0.72:
                continue
            new_figure = soup.new_tag("figure")
            new_figure["data-placement"] = "repositioned-essential"
            new_figure["class"] = ["inferred-essential-figure"]
            img.extract()
            new_figure.append(img)
            _annotate_figure_from_crop(new_figure, crop)
            extended_anchor = _extend_anchor_through_nearby_text_run(anchor, crop)
            if extended_anchor is not anchor:
                _insert_figure_near_anchor(new_figure, extended_anchor)
            else:
                _insert_split_figure_near_anchor(new_figure, anchor, figure)
            moved += 1
        if not figure.find("img", src=True):
            figure.decompose()
            continue
        remaining_imgs = [img for img in figure.find_all("img", recursive=False) if img.get("src")]
        if len(remaining_imgs) == 1:
            _annotate_figure_from_crop(figure, _crop_from_img_tag(remaining_imgs[0]))
    return moved


def _figure_current_catalog_anchor(figure):
    sibling = _previous_significant_tag(figure)
    while getattr(sibling, "name", None) == "figure":
        sibling = _previous_significant_tag(sibling)
    if _anchor_label_text(sibling):
        return sibling
    return None


def _reposition_labeled_catalog_figures(soup) -> int:
    """Move labeled catalog figures from OCR order to their semantic label."""
    moved = 0
    for figure in list(soup.find_all("figure")):
        if figure.find_parent("section", class_="semantic-catalog-entry"):
            continue
        if not _is_catalog_entry_figure(figure):
            continue
        img = figure.find("img")
        if img is None:
            continue
        crop = _crop_from_img_tag(img)
        anchor = _best_anchor_for_orphan_crop(soup, crop)
        if anchor is None or _orphan_anchor_score(crop, anchor) < 0.95:
            continue
        if _figure_current_catalog_anchor(figure) is anchor:
            continue
        figure.extract()
        _insert_figure_near_anchor(figure, anchor)
        moved += 1
    return moved


def _catalog_figure_order_key(anchor_text: str, figure) -> tuple[int, str]:
    img = figure.find("img") if getattr(figure, "name", None) == "figure" else None
    crop = _crop_from_img_tag(img) if img else {}
    crop_tokens = _crop_label_tokens(crop)
    anchor_tokens = [_token_key(token) for token in _title_tokens(anchor_text) if _is_label_token(token)]
    if crop_tokens and anchor_tokens:
        counts = {token: anchor_tokens.count(token) for token in set(anchor_tokens)}
        unique_positions = [
            idx for idx, token in enumerate(anchor_tokens)
            if token in crop_tokens and counts.get(token) == 1
        ]
        if unique_positions:
            return (min(unique_positions), str(img.get("data-crop-filename") or ""))
        positions = [idx for idx, token in enumerate(anchor_tokens) if token in crop_tokens]
        if positions:
            return (min(positions), str(img.get("data-crop-filename") or ""))
    return (10_000, str(img.get("data-crop-filename") or "") if img else "")


def _sort_catalog_figure_runs(soup) -> int:
    sorted_runs = 0
    for anchor in list(soup.find_all(["dt", "h1", "h2", "h3", "h4", "h5", "h6", "li", "p"])):
        label = _anchor_label_text(anchor) or _anchor_text(anchor)
        if not label:
            continue
        figures = []
        sibling = _next_significant_tag(anchor)
        while getattr(sibling, "name", None) == "figure" and _is_catalog_entry_figure(sibling):
            figures.append(sibling)
            sibling = _next_significant_tag(sibling)
        if len(figures) < 2:
            continue
        ordered = sorted(figures, key=lambda fig: _catalog_figure_order_key(label, fig))
        if ordered == figures:
            continue
        cursor = anchor
        for figure in ordered:
            figure.extract()
            cursor.insert_after(figure)
            cursor = figure
        sorted_runs += 1
    return sorted_runs


_ORPHAN_OPTIONAL_CATALOG_CROP_ROLES = {
    "card_face",
    "card_reference",
    "component_reference",
    "icon_reference",
}


def _is_high_confidence_catalog_anchor(crop: Dict[str, Any], anchor) -> bool:
    label = _anchor_label_text(anchor) or _anchor_text(anchor)
    if not _compact_catalog_label(label):
        return False
    return _orphan_anchor_score(crop, anchor) >= 0.95


def _should_insert_orphan_crop(crop: Dict[str, Any], anchor) -> bool:
    role = _role_from_crop(crop)
    if role not in _ORPHAN_INSERTABLE_CROP_ROLES:
        return False
    importance = _importance_from_crop(crop)
    if importance == "essential":
        return True
    return bool(
        importance == "useful"
        and role in _ORPHAN_OPTIONAL_CATALOG_CROP_ROLES
        and anchor is not None
        and _is_high_confidence_catalog_anchor(crop, anchor)
    )


def _insert_orphan_essential_crops(
    soup,
    crops: List[Dict[str, Any]],
    used_crop_indices: Set[int],
    rel_src: str,
) -> int:
    inserted = 0
    for crop_idx, crop in enumerate(crops):
        if crop_idx in used_crop_indices:
            continue
        figure = _build_crop_figure(soup, crop, rel_src)
        if figure is None:
            continue
        anchor = _best_anchor_for_orphan_crop(soup, crop)
        if not _should_insert_orphan_crop(crop, anchor):
            continue
        if anchor is None:
            _append_orphan_figure(soup, figure)
        else:
            anchor = _extend_anchor_through_nearby_text_run(anchor, crop)
            _insert_figure_near_anchor(figure, anchor)
        inserted += 1
    return inserted


def _match_crops_to_img_tags(img_tags, crops: List[Dict[str, Any]]) -> Dict[int, int]:
    """Match crops to OCR image/caption blocks using descriptor similarity."""
    n_tags = len(img_tags)
    n_crops = len(crops)
    if not n_tags or not n_crops:
        return {}
    if max(n_tags, n_crops) > 12:
        return {idx: idx for idx in range(min(n_tags, n_crops))}

    block_texts = [_block_match_texts(tag) for tag in img_tags]
    crop_texts = [_crop_match_texts(crop) for crop in crops]
    scores: List[List[float]] = []
    for crop_idx, texts in enumerate(crop_texts):
        row = []
        for block_idx, block in enumerate(block_texts):
            best = 0.0
            for crop_text in texts:
                for block_text in block:
                    best = max(best, _descriptor_similarity(crop_text, block_text))
            if crop_idx == block_idx:
                best += 0.05
            row.append(best)
        scores.append(row)

    @lru_cache(maxsize=None)
    def solve(block_idx: int, used_mask: int):
        if block_idx >= n_tags:
            return 0.0, ()
        best_score, best_assignment = solve(block_idx + 1, used_mask)
        best_tuple = (-1,) + best_assignment
        for crop_idx in range(n_crops):
            if used_mask & (1 << crop_idx):
                continue
            score = scores[crop_idx][block_idx]
            tail_score, tail_assignment = solve(block_idx + 1, used_mask | (1 << crop_idx))
            total = score + tail_score
            if total > best_score:
                best_score = total
                best_tuple = (crop_idx,) + tail_assignment
        return best_score, best_tuple

    _, assignment = solve(0, 0)
    return {
        block_idx: crop_idx
        for block_idx, crop_idx in enumerate(assignment)
        if isinstance(crop_idx, int) and 0 <= crop_idx < n_crops
    }


def _previous_significant_tag(node):
    from bs4 import NavigableString

    sibling = node.previous_sibling
    while sibling is not None:
        if isinstance(sibling, NavigableString):
            if sibling.strip():
                return None
            sibling = sibling.previous_sibling
            continue
        return sibling
    return None


def _next_significant_tag(node):
    from bs4 import NavigableString

    sibling = node.next_sibling
    while sibling is not None:
        if isinstance(sibling, NavigableString):
            if sibling.strip():
                return None
            sibling = sibling.next_sibling
            continue
        return sibling
    return None


def _stitch_figure_interruptions(soup) -> None:
    """Merge prose fragments split only by a run of figures."""
    for figure in list(soup.find_all("figure")):
        if not figure.parent:
            continue
        prev_sig = _previous_significant_tag(figure)
        if getattr(prev_sig, "name", None) == "figure":
            continue
        last = figure
        next_sig = _next_significant_tag(last)
        while getattr(next_sig, "name", None) == "figure":
            last = next_sig
            next_sig = _next_significant_tag(last)
        if getattr(prev_sig, "name", None) != "p" or getattr(next_sig, "name", None) != "p":
            continue
        prev_text = prev_sig.get_text(" ", strip=True)
        next_text = next_sig.get_text(" ", strip=True)
        if not _should_stitch_page_break(prev_text, next_text):
            continue
        _append_paragraph_children(prev_sig, next_sig)
        next_sig.decompose()


def _remove_unresolved_image_placeholders(soup) -> None:
    for tag in list(soup.find_all("img")):
        if tag.attrs is None:
            continue
        if tag.get("src"):
            continue
        alt_text = _normalize_ws(tag.get("alt") or "")
        parent = tag.parent
        tag.decompose()
        if parent and parent.name == "figure" and not parent.find("img", src=True):
            caption = parent.find("figcaption")
            caption_text = _normalize_ws(caption.get_text(" ", strip=True)) if caption else ""
            if caption_text:
                if _TEXT_ONLY_CALLOUT_RE.search(f"{alt_text} {caption_text}"):
                    replacement = _build_semantic_callout(soup, caption_text, kind="reminder")
                else:
                    replacement = soup.new_tag("p")
                    replacement.string = caption_text
                parent.replace_with(replacement)
            else:
                parent.decompose()


def _leading_label_text(tag) -> str:
    if getattr(tag, "name", None) in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        return _normalize_ws(tag.get_text(" ", strip=True))
    if getattr(tag, "name", None) == "p":
        first_strong = tag.find("strong")
        if first_strong:
            return _normalize_ws(first_strong.get_text(" ", strip=True))
        return _normalize_ws(tag.get_text(" ", strip=True)).split(".", 1)[0]
    return ""


def _dedupe_figure_captions_against_adjacent_text(soup) -> None:
    for figure in list(soup.find_all("figure")):
        caption = figure.find("figcaption")
        caption_text = _normalize_ws(caption.get_text(" ", strip=True)) if caption else ""
        if not caption_text:
            continue
        caption_key = set(_title_tokens(caption_text))
        if not caption_key:
            continue
        prev_label = _leading_label_text(_previous_significant_tag(figure))
        next_label = _leading_label_text(_next_significant_tag(figure))
        for label in (prev_label, next_label):
            label_key = set(_title_tokens(label))
            if label_key and caption_key <= label_key:
                caption.decompose()
                figure["data-caption-deduped"] = "adjacent-text"
                break


def _dedupe_integrated_diagram_callout_captions(soup) -> None:
    """Remove figcaptions that duplicate spatial callout text inside diagrams."""
    for figure in list(soup.find_all("figure")):
        role = _normalize_ws(figure.get("data-critical-graphics-role") or "").casefold()
        if role != "rule_example_diagram":
            continue
        caption = figure.find("figcaption")
        caption_text = _normalize_ws(caption.get_text(" ", strip=True)) if caption else ""
        if not caption_text:
            continue
        numbered_items = re.findall(r"(?:^|\s)\d+[\.)]\s+\S+", caption_text)
        if len(numbered_items) < 2:
            continue
        img = figure.find("img")
        meta_text = " ".join(
            _normalize_ws(value)
            for value in (
                figure.get("data-critical-graphics-nearby-text") or "",
                img.get("data-critical-graphics-nearby-text") if img else "",
                img.get("alt") if img else "",
            )
            if value
        ).casefold()
        if not any(cue in meta_text for cue in ("callout", "numbered", "movement plan", "green path")):
            continue
        caption_tokens = {
            token
            for token in _title_tokens(caption_text)
            if len(token) > 2 and token not in _DESCRIPTOR_GENERIC_TOKENS
        }
        meta_tokens = set(_title_tokens(meta_text))
        if not caption_tokens:
            continue
        if len(caption_tokens & meta_tokens) / float(len(caption_tokens)) < 0.6:
            continue
        caption.decompose()
        figure["data-caption-deduped"] = "integrated-diagram-callouts"


def _expand_multi_count_img_tags(soup) -> None:
    """Expand OCR placeholders like <img data-count="2"> into multiple tags."""
    for tag in list(soup.find_all("img")):
        try:
            count = int(tag.get("data-count") or 1)
        except (TypeError, ValueError):
            count = 1
        if count <= 1:
            tag.attrs.pop("data-count", None)
            continue
        tag.attrs.pop("data-count", None)
        anchor = tag
        for _ in range(count - 1):
            clone = deepcopy(tag)
            clone.attrs.pop("src", None)
            clone.attrs.pop("data-crop-filename", None)
            anchor.insert_after(clone)
            anchor = clone


def _attach_images(html: str, crops: List[Dict[str, Any]], rel_src: str) -> str:
    """Attach cropped images to <img> placeholders with <figure>/<figcaption> wrapping.

    Handles two OCR output formats:
    - New format: <figure><img alt="..."><figcaption>...</figcaption></figure>
      → just sets src/alt/data-crop-filename on the existing structure.
    - Old format: <img alt="..."> followed optionally by a caption <p>
      → wraps in <figure>, detects adjacent caption <p> and converts to <figcaption>.

    Matching: descriptor-based against OCR alt/caption context, with positional
    fallback when the page is too large or descriptors are insufficient.
    """
    if not html or not crops:
        return html
    soup = BeautifulSoup(html, "html.parser")
    _expand_multi_count_img_tags(soup)
    candidate_crops = [
        crop
        for crop in crops
        if not _should_skip_source_pixel_crop(crop, soup)
    ]
    img_tags = [tag for tag in soup.find_all("img") if not _is_text_only_callout_placeholder(tag)]
    crop_matches = _match_crops_to_img_tags(img_tags, candidate_crops)
    used_crop_indices: Set[int] = set()

    n_tags = len(img_tags)
    n_crops = len(candidate_crops)
    if n_tags != n_crops:
        print(f"  [build] Warning: {n_tags} <img> tags vs {n_crops} crops on page — matching by descriptors with fallback",
              file=sys.stderr)

    for idx, tag in enumerate(img_tags):
        crop_idx = crop_matches.get(idx)
        if crop_idx is None:
            continue
        crop = candidate_crops[crop_idx]
        filename = crop.get("filename")
        if not filename:
            continue
        used_crop_indices.add(crop_idx)

        # Rich alt text — prefer VLM image_description over OCR alt
        alt = crop.get("image_description") or crop.get("alt") or ""
        tag["src"] = f"{rel_src}/{filename}"
        tag["alt"] = alt
        tag["data-crop-filename"] = filename
        _annotate_img_from_crop(tag, crop)

        parent = tag.parent
        already_in_figure = parent and parent.name == "figure"

        if already_in_figure:
            # New OCR format: <figure> already wraps the <img>.
            # Add crop metadata; leave existing <figcaption> intact.
            figure = parent
            figure["data-placement"] = "ocr-figure"
            _annotate_figure_from_crop(figure, crop)
            existing_figcap = figure.find("figcaption")
            caption_text = crop.get("caption_text")
            if existing_figcap:
                figure["data-caption-source"] = "ocr"
            elif caption_text:
                figcaption = soup.new_tag("figcaption")
                figcaption.string = caption_text
                figure.append(figcaption)
                figure["data-caption-source"] = "crop-pipeline"
        else:
            # Old OCR format: bare <img> — wrap in <figure>.
            figure = soup.new_tag("figure")
            tag.wrap(figure)
            figure["data-placement"] = "ocr-inline"
            _annotate_figure_from_crop(figure, crop)

            # Try to find a caption: crop pipeline caption or adjacent <p>
            caption_text = crop.get("caption_text")
            if caption_text:
                figcaption = soup.new_tag("figcaption")
                figcaption.string = caption_text
                figure.append(figcaption)
                figure["data-caption-source"] = "crop-pipeline"
            else:
                # Heuristic: check next sibling(s) for caption-like <p> tags
                if _absorb_caption_siblings(figure, soup):
                    figure["data-caption-source"] = "heuristic"

        _suppress_duplicate_text_after_figure(figure, crop)

    _insert_orphan_essential_crops(soup, candidate_crops, used_crop_indices, rel_src)
    _split_labeled_multi_image_figures(soup)
    _reposition_labeled_catalog_figures(soup)
    _sort_catalog_figure_runs(soup)
    _stitch_figure_interruptions(soup)
    _remove_unresolved_image_placeholders(soup)
    _promote_text_callout_paragraphs(soup)
    _dedupe_figure_captions_against_adjacent_text(soup)
    _dedupe_integrated_diagram_callout_captions(soup)
    return soup.decode_contents()


def _absorb_caption_siblings(figure, soup) -> bool:
    """Move short caption-like <p> siblings after a <figure> into <figcaption>.

    Absorbs one or two consecutive short <p> tags (e.g., a title line
    followed by a "Back Row: ..." list). Stops at the first non-caption.

    Returns True if any captions were absorbed.
    """
    from bs4 import NavigableString

    absorbed = []
    sibling = figure.next_sibling

    # Skip whitespace text nodes
    while isinstance(sibling, NavigableString) and not sibling.strip():
        sibling = sibling.next_sibling

    # Check up to 2 consecutive caption-like <p> tags
    for _ in range(2):
        if sibling is None or sibling.name != "p":
            break
        text = sibling.get_text(strip=True)
        if not _is_likely_caption(text):
            break
        absorbed.append(sibling)
        next_sib = sibling.next_sibling
        # Skip whitespace
        while isinstance(next_sib, NavigableString) and not next_sib.strip():
            next_sib = next_sib.next_sibling
        sibling = next_sib

    if not absorbed:
        return False

    figcaption = soup.new_tag("figcaption")
    for p_tag in absorbed:
        # Move content into figcaption (preserve <br> etc.)
        for child in list(p_tag.children):
            figcaption.append(child.extract())
        # Add line break between absorbed paragraphs
        if p_tag is not absorbed[-1]:
            figcaption.append(soup.new_tag("br"))
        p_tag.decompose()

    figure.append(figcaption)
    return True


def _reference_entry_parts(paragraph) -> Optional[tuple[str, list[Any]]]:
    children = list(paragraph.contents)
    first_strong_idx = None
    for idx, child in enumerate(children):
        name = getattr(child, "name", None)
        if name == "strong":
            first_strong_idx = idx
            break
        if name is None and not str(child).strip():
            continue
        return None
    if first_strong_idx is None:
        return None
    strong = children[first_strong_idx]
    term = _normalize_ws(strong.get_text(" ", strip=True))
    if not term or len(term) > 80 or term.endswith(":"):
        return None
    tokens = _title_tokens(term)
    if not tokens or len(tokens) > 6:
        return None
    uppercase_letters = sum(1 for char in term if char.isalpha() and char.isupper())
    letters = sum(1 for char in term if char.isalpha())
    if letters and uppercase_letters / letters < 0.7:
        return None

    remainder = children[first_strong_idx + 1 :]
    while remainder:
        first = remainder[0]
        if getattr(first, "name", None) == "br" or (getattr(first, "name", None) is None and not str(first).strip()):
            remainder = remainder[1:]
            continue
        break
    remainder_text = _normalize_ws(" ".join(getattr(child, "get_text", lambda *_: str(child))(" ", strip=True) for child in remainder))
    if len(remainder_text) < 8:
        return None
    return term, remainder


def _is_uppercase_reference_label(text: str) -> bool:
    text = _normalize_ws(text)
    if not text or len(text) > 80 or text.endswith(":"):
        return False
    tokens = _title_tokens(text)
    if not tokens or len(tokens) > 6:
        return False
    letters = [char for char in text if char.isalpha()]
    if not letters:
        return False
    return sum(1 for char in letters if char.isupper()) / len(letters) >= 0.7


def _normalize_figure_labeled_entries(soup) -> int:
    converted = 0
    for paragraph in list(soup.find_all("p")):
        if not paragraph.parent:
            continue
        label = _normalize_ws(paragraph.get_text(" ", strip=True))
        if not _is_uppercase_reference_label(label):
            continue
        prev_sig = _previous_significant_tag(paragraph)
        next_sig = _next_significant_tag(paragraph)
        figure_before_label = getattr(prev_sig, "name", None) == "figure"
        figure_after_label = getattr(next_sig, "name", None) == "figure"
        if not figure_before_label and not figure_after_label:
            continue
        desc_nodes = []
        sibling = _next_significant_tag(next_sig if figure_after_label else paragraph)
        while getattr(sibling, "name", None) == "p":
            sibling_text = _normalize_ws(sibling.get_text(" ", strip=True))
            if _is_uppercase_reference_label(sibling_text):
                break
            desc_nodes.append(sibling)
            sibling = _next_significant_tag(sibling)
            if len(desc_nodes) >= 3:
                break
        if not desc_nodes:
            continue
        dl = soup.new_tag("dl")
        dl["class"] = ["semantic-entry-list"]
        dt = soup.new_tag("dt")
        dt.string = label
        dd = soup.new_tag("dd")
        for idx, node in enumerate(desc_nodes):
            if idx:
                dd.append(soup.new_tag("br"))
            for child in list(node.children):
                dd.append(deepcopy(child))
        dl.append(dt)
        dl.append(dd)
        paragraph.replace_with(dl)
        for node in desc_nodes:
            node.decompose()
        converted += 1
    return converted


def _normalize_reference_entries(html: str, *, enabled: bool) -> str:
    if not enabled or "<strong" not in html:
        soup = BeautifulSoup(html or "", "html.parser")
        converted = _normalize_figure_labeled_entries(soup) if enabled else 0
        return soup.decode_contents() if converted else html
    soup = BeautifulSoup(html or "", "html.parser")
    converted = 0
    for paragraph in list(soup.find_all("p")):
        parts = _reference_entry_parts(paragraph)
        if not parts:
            continue
        term, remainder = parts
        dl = soup.new_tag("dl")
        dl["class"] = ["semantic-entry-list"]
        dt = soup.new_tag("dt")
        dt.string = term
        dd = soup.new_tag("dd")
        for child in remainder:
            dd.append(deepcopy(child))
        dl.append(dt)
        dl.append(dd)
        paragraph.replace_with(dl)
        converted += 1
    converted += _normalize_figure_labeled_entries(soup)
    if converted:
        return soup.decode_contents()
    return html


_CATALOG_ENTRY_FIGURE_ROLES = {
    "card_face",
    "component_reference",
    "icon_reference",
    "map_or_board",
    "setup_diagram",
}


def _figure_role(tag: Any) -> str:
    return str(tag.get("data-critical-graphics-role") or "")


def _is_catalog_entry_figure(tag: Any) -> bool:
    if getattr(tag, "name", None) != "figure":
        return False
    role = _figure_role(tag)
    if role == "card_reference":
        return False
    if role in _CATALOG_ENTRY_FIGURE_ROLES:
        return True
    img = tag.find("img")
    alt = img.get("alt") if img else ""
    lowered = str(alt or "").casefold()
    return bool(
        _looks_label_value_metadata(str(alt or ""))
        and any(word in lowered for word in ("card", "course", "map", "reference", "component"))
    )


def _compact_catalog_label(text: str) -> bool:
    text = _normalize_ws(text)
    if not text or len(text) > 90 or text.endswith(":"):
        return False
    if _looks_label_value_metadata(text):
        return False
    if len(_title_tokens(text)) > 8:
        return False
    if re.search(r"[.!?]", text):
        return False
    letters = [char for char in text if char.isalpha()]
    return bool(letters and len(letters) / max(1, len(text)) >= 0.45)


def _catalog_label_key(text: str) -> str:
    return " ".join(_title_tokens(text))


def _catalog_entry_title_from_node(tag: Any) -> Optional[str]:
    name = getattr(tag, "name", None)
    if name in {"h3", "h4", "h5", "h6"}:
        text = _normalize_ws(tag.get_text(" ", strip=True))
        return text if _compact_catalog_label(text) else None
    if name == "p":
        text = _normalize_ws(tag.get_text(" ", strip=True))
        strong = tag.find("strong", recursive=False)
        strong_text = _normalize_ws(strong.get_text(" ", strip=True)) if strong else ""
        if strong_text and _catalog_label_key(text) == _catalog_label_key(strong_text) and _compact_catalog_label(strong_text):
            return strong_text
        if _is_uppercase_reference_label(text):
            return text
        return None
    if name == "dl" and "semantic-entry-list" in (tag.get("class") or []):
        dt = tag.find("dt", recursive=False)
        if not dt:
            return None
        text = _normalize_ws(dt.get_text(" ", strip=True))
        return text if _compact_catalog_label(text) else None
    return None


def _catalog_entry_metadata_from_dl(soup: BeautifulSoup, dl: Any):
    dd = dl.find("dd", recursive=False)
    if not dd:
        return None
    paragraph = soup.new_tag("p")
    for child in list(dd.contents):
        paragraph.append(child.extract())
    return paragraph if _normalize_ws(paragraph.get_text(" ", strip=True)) else None


def _is_catalog_entry_metadata_node(tag: Any) -> bool:
    name = getattr(tag, "name", None)
    if name == "p":
        return _looks_label_value_metadata(tag.get_text(" ", strip=True))
    if name == "dl" and "semantic-entry-list" in (tag.get("class") or []):
        dd = tag.find("dd", recursive=False)
        return bool(dd and _looks_label_value_metadata(dd.get_text(" ", strip=True)))
    return False


def _metadata_node_for_entry(soup: BeautifulSoup, tag: Any):
    if getattr(tag, "name", None) == "dl":
        return _catalog_entry_metadata_from_dl(soup, tag)
    return tag


def _dl_catalog_pairs(dl: Any) -> list[tuple[Any, Any]]:
    pairs = []
    children = [child for child in dl.children if getattr(child, "name", None)]
    idx = 0
    while idx < len(children):
        dt = children[idx]
        dd = children[idx + 1] if idx + 1 < len(children) else None
        if getattr(dt, "name", None) == "dt" and getattr(dd, "name", None) == "dd":
            pairs.append((dt, dd))
            idx += 2
            continue
        return []
    return pairs


def _dd_contains_catalog_metadata(dd: Any) -> bool:
    text = _normalize_ws(dd.get_text(" ", strip=True))
    return _looks_label_value_metadata(text)


_CATALOG_METADATA_BLOCK_TAGS = {
    "blockquote",
    "div",
    "dl",
    "ol",
    "p",
    "pre",
    "section",
    "table",
    "ul",
}


def _append_dd_metadata(section: Any, dd: Any, soup: BeautifulSoup) -> bool:
    moved_children = []
    for child in list(dd.contents):
        if getattr(child, "name", None) == "figure":
            child.extract()
            continue
        if getattr(child, "name", None) is None and not str(child).strip():
            child.extract()
            continue
        moved_children.append(child.extract())
    if moved_children:
        paragraph = None
        for child in moved_children:
            child_name = getattr(child, "name", None)
            if child_name in _CATALOG_METADATA_BLOCK_TAGS:
                if paragraph and _normalize_ws(paragraph.get_text(" ", strip=True)):
                    section.append(paragraph)
                paragraph = None
                section.append(child)
                continue
            if paragraph is None:
                paragraph = soup.new_tag("p")
            paragraph.append(child)
        if paragraph and _normalize_ws(paragraph.get_text(" ", strip=True)):
            section.append(paragraph)
        return True
    text = _normalize_ws(dd.get_text(" ", strip=True))
    if not text:
        return False
    paragraph = soup.new_tag("p")
    paragraph.string = text
    section.append(paragraph)
    return True


def _normalize_embedded_dl_catalog_entries(soup: BeautifulSoup) -> int:
    converted = 0
    for dl in list(soup.find_all("dl")):
        if dl.find_parent("section", class_="semantic-catalog-entry"):
            continue
        pairs = _dl_catalog_pairs(dl)
        if not pairs:
            continue
        sections = []
        for dt, dd in pairs:
            title = _normalize_ws(dt.get_text(" ", strip=True))
            figure = next((fig for fig in dd.find_all("figure") if _is_catalog_entry_figure(fig)), None)
            if not title or not _compact_catalog_label(title) or figure is None or not _dd_contains_catalog_metadata(dd):
                sections = []
                break
            section = soup.new_tag("section")
            section["class"] = ["semantic-catalog-entry"]
            section["data-doc-web-semantic"] = "catalog-entry"
            section["data-catalog-entry-title"] = title
            heading = soup.new_tag("h3")
            heading.string = title
            section.append(heading)
            section.append(figure.extract())
            if not _append_dd_metadata(section, dd, soup):
                sections = []
                break
            sections.append(section)
        if not sections:
            continue
        for section in sections:
            dl.insert_before(section)
            converted += 1
        dl.decompose()
    return converted


def _looks_like_catalog_entry_fragment(soup: BeautifulSoup, title: str) -> bool:
    if not _looks_catalog_category_heading(title):
        return False
    figures = [tag for tag in soup.find_all("figure") if _is_catalog_entry_figure(tag)]
    metadata_nodes = [tag for tag in soup.find_all(["p", "dl"]) if _is_catalog_entry_metadata_node(tag)]
    return len(figures) >= 2 and len(metadata_nodes) >= 2


def _wrap_catalog_entry(
    soup: BeautifulSoup,
    *,
    title: str,
    figure: Any,
    title_node: Any,
    metadata_node: Any,
    insert_before: Any,
    figures: Optional[list[Any]] = None,
) -> bool:
    if not title or not figure or not title_node or not metadata_node or not insert_before:
        return False
    if figure.find_parent("section", class_="semantic-catalog-entry"):
        return False

    metadata = _metadata_node_for_entry(soup, metadata_node)
    if not metadata:
        return False

    section = soup.new_tag("section")
    section["class"] = ["semantic-catalog-entry"]
    section["data-doc-web-semantic"] = "catalog-entry"
    section["data-catalog-entry-title"] = title
    insert_before.insert_before(section)
    heading = soup.new_tag("h3")
    heading.string = title
    section.append(heading)
    entry_figures = figures or [figure]
    for entry_figure in entry_figures:
        if getattr(entry_figure, "parent", None):
            section.append(entry_figure.extract())
    section.append(metadata.extract() if getattr(metadata, "parent", None) else metadata)
    if getattr(title_node, "parent", None):
        title_node.decompose()
    if metadata_node is not title_node and metadata_node is not metadata and getattr(metadata_node, "parent", None):
        metadata_node.decompose()
    return True


def _catalog_figure_matches_title(figure: Any, title: str) -> bool:
    if not title:
        return True
    img = figure.find("img") if getattr(figure, "name", None) == "figure" else None
    if img is None:
        return True
    crop_tokens = _crop_label_tokens(_crop_from_img_tag(img))
    title_tokens = _normalized_token_set(title)
    if not crop_tokens or not title_tokens:
        return True
    return len(crop_tokens & title_tokens) / float(len(crop_tokens)) >= 0.75


def _catalog_figure_run_after(figure: Any, *, title: str = "") -> tuple[list[Any], Any]:
    figures = [figure]
    sibling = _next_significant_tag(figure)
    while getattr(sibling, "name", None) == "figure" and _is_catalog_entry_figure(sibling):
        if title and not _catalog_figure_matches_title(sibling, title):
            break
        figures.append(sibling)
        sibling = _next_significant_tag(sibling)
    return figures, sibling


def _normalize_catalog_entries(html: str, *, title: str, enabled: bool) -> str:
    if not enabled:
        return html
    soup = BeautifulSoup(html or "", "html.parser")
    if not (_looks_like_catalog_chapter(soup, title) or _looks_like_catalog_entry_fragment(soup, title)):
        if _looks_catalog_category_heading(title):
            converted = _normalize_embedded_dl_catalog_entries(soup)
            return soup.decode_contents() if converted else html
        return html

    converted = _normalize_embedded_dl_catalog_entries(soup)
    for figure in list(soup.find_all("figure")):
        if not _is_catalog_entry_figure(figure):
            continue

        prev_tag = _previous_significant_tag(figure)
        next_tag = _next_significant_tag(figure)
        prev_title = _catalog_entry_title_from_node(prev_tag)
        next_title = _catalog_entry_title_from_node(next_tag)

        if prev_title and getattr(prev_tag, "name", None) == "dl":
            figure_run, _ = _catalog_figure_run_after(figure, title=prev_title)
            converted += int(
                _wrap_catalog_entry(
                    soup,
                    title=prev_title,
                    figure=figure,
                    figures=figure_run,
                    title_node=prev_tag,
                    metadata_node=prev_tag,
                    insert_before=prev_tag,
                )
            )
            continue

        if prev_title and getattr(prev_tag, "name", None) == "p":
            metadata = _next_significant_tag(figure)
            if _is_catalog_entry_metadata_node(metadata):
                converted += int(
                    _wrap_catalog_entry(
                        soup,
                        title=prev_title,
                        figure=figure,
                        title_node=prev_tag,
                        metadata_node=metadata,
                        insert_before=prev_tag,
                    )
                )
                continue

        if prev_title and getattr(prev_tag, "name", None) in {"h3", "h4", "h5", "h6"}:
            figure_run, metadata = _catalog_figure_run_after(figure, title=prev_title)
            if _is_catalog_entry_metadata_node(metadata):
                converted += int(
                    _wrap_catalog_entry(
                        soup,
                        title=prev_title,
                        figure=figure,
                        figures=figure_run,
                        title_node=prev_tag,
                        metadata_node=metadata,
                        insert_before=prev_tag,
                    )
                )
                continue

        if next_title:
            if getattr(next_tag, "name", None) == "dl":
                converted += int(
                    _wrap_catalog_entry(
                        soup,
                        title=next_title,
                        figure=figure,
                        title_node=next_tag,
                        metadata_node=next_tag,
                        insert_before=figure,
                    )
                )
                continue
            metadata = _next_significant_tag(next_tag)
            if _is_catalog_entry_metadata_node(metadata):
                converted += int(
                    _wrap_catalog_entry(
                        soup,
                        title=next_title,
                        figure=figure,
                        title_node=next_tag,
                        metadata_node=metadata,
                        insert_before=figure,
                    )
                )

    return soup.decode_contents() if converted else html


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Build per-chapter HTML files from pages + portions.")
    parser.add_argument("--pages", required=True, help="page_html_v1 JSONL (with printed_page_number)")
    parser.add_argument("--portions", required=True, help="portion_hyp_v1 JSONL")
    parser.add_argument("--out", required=True, help="Output manifest JSONL path")
    parser.add_argument("--output-dir", dest="output_dir", default=None,
                        help="Directory to write HTML files (default: output/html under run dir)")
    parser.add_argument("--illustration-manifest", dest="illustration_manifest", default=None,
                        help="Optional illustration_manifest.jsonl to attach img src tags")
    parser.add_argument("--images-subdir", dest="images_subdir", default="images",
                        help="Subdir under output/html for cropped images (default: images)")
    parser.add_argument("--book-title", dest="book_title", default="",
                        help="Book title for index page and HTML <title>")
    parser.add_argument("--book-author", dest="book_author", default="",
                        help="Book author for index page")
    parser.add_argument(
        "--merge-contiguous-genealogy-tables",
        dest="merge_contiguous_genealogy_tables",
        action="store_true",
        default=False,
        help="Collapse contiguous same-schema genealogy tables into one table with subgroup heading rows.",
    )
    parser.add_argument(
        "--include-navigation",
        dest="include_navigation",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include previous/index/next navigation chrome in generated chapter files.",
    )
    parser.add_argument(
        "--suppress-navigation",
        dest="suppress_navigation",
        action="store_true",
        default=False,
        help="Suppress previous/index/next navigation chrome in generated chapter files.",
    )
    parser.add_argument(
        "--normalize-reference-entries",
        dest="normalize_reference_entries",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Convert repeated <strong>term</strong><br> paragraphs into definition-list entries.",
    )
    parser.add_argument(
        "--normalize-catalog-entries",
        dest="normalize_catalog_entries",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Group catalog/index entry figures, labels, and metadata into semantic entry sections.",
    )
    parser.add_argument("--run-id", dest="run_id", default=None, help="Run ID for progress logging")
    parser.add_argument("--state-file", dest="state_file", default=None, help="Pipeline state JSON path")
    parser.add_argument("--progress-file", dest="progress_file", default=None, help="Pipeline progress JSONL path")
    args = parser.parse_args()

    pages = list(read_jsonl(args.pages))
    portions = list(read_jsonl(args.portions))
    if not pages:
        raise SystemExit(f"Input pages empty: {args.pages}")
    if not portions:
        raise SystemExit(f"Input portions empty: {args.portions}")

    book_title = args.book_title or "Book"
    book_author = args.book_author or ""

    out_path = Path(args.out)
    run_dir = _resolve_run_dir(out_path)
    html_dir = Path(args.output_dir) if args.output_dir else (run_dir / "output" / "html")
    ensure_dir(str(html_dir))
    images_dir = html_dir / args.images_subdir
    emitted_asset_roots: List[str] = []

    # Load illustration manifest and copy image files
    crops_by_page: Dict[int, List[Dict[str, Any]]] = {}
    if args.illustration_manifest:
        crops_by_page = _group_manifest_by_page(args.illustration_manifest)
        manifest_dir = Path(args.illustration_manifest).parent
        crops_dir = manifest_dir / "images"
        copied_filenames = _refresh_published_illustration_images(crops_by_page, crops_dir, images_dir)
        if copied_filenames:
            emitted_asset_roots = [args.images_subdir.rstrip("/")]

    pages_sorted = sorted(pages, key=_page_sort_key)
    pages_scan = sorted(pages, key=lambda r: _coerce_int(r.get("page_number") or r.get("page")) or 0)
    document_has_printed_pages = any(
        isinstance(_coerce_int(page.get("printed_page_number")), int)
        for page in pages_sorted
    )
    manifest_rows = []
    bundle_entries = []
    provenance_rows = []
    toc_entries = []
    covered_printed_pages = set()
    covered_source_pages = set()
    chapters_by_start = {}
    # ── Build chapters ──────────────────────────────────────────────────
    chapter_files: List[Dict[str, Any]] = []  # For navigation pass

    chapter_counter = 0
    for portion_idx, portion in enumerate(portions):
        page_start = _coerce_int(portion.get("page_start"))
        page_end = _coerce_int(portion.get("page_end")) or page_start
        title = portion.get("title") or portion.get("portion_id") or f"Chapter {portion_idx + 1}"
        if not isinstance(page_start, int):
            continue
        if not isinstance(page_end, int):
            page_end = page_start

        chapter_pages = _select_pages_for_portion(portion, pages_sorted)
        if (
            document_has_printed_pages
            and portion.get("notes") == "heading-derived-source-pages"
            and chapter_pages
            and not any(
                isinstance(_coerce_int(page.get("printed_page_number")), int)
                for page in chapter_pages
            )
        ):
            continue
        if chapter_pages and all(
            _page_already_covered(
                page,
                covered_printed_pages=covered_printed_pages,
                covered_source_pages=covered_source_pages,
            )
            for page in chapter_pages
        ):
            continue
        for p in chapter_pages:
            printed_number = _coerce_int(p.get("printed_page_number"))
            if printed_number is not None:
                covered_printed_pages.add(printed_number)
            source_number = _source_page_number(p)
            if source_number is not None:
                covered_source_pages.add(source_number)

        prepared_pages = []
        for page in chapter_pages:
            html = page.get("html") or page.get("raw_html") or ""
            page_num = _coerce_int(page.get("page_number") or page.get("page"))
            printed_page_number = _coerce_int(page.get("printed_page_number"))
            crops = crops_by_page.get(page_num, []) if isinstance(page_num, int) else []
            if crops:
                html = _attach_images(html, crops, args.images_subdir.rstrip("/"))
            html = _strip_headers_and_numbers(html)
            html = _add_table_scope(html)
            html = _normalize_heading_breaks(html)
            if args.merge_contiguous_genealogy_tables:
                html = _merge_genealogy_tables_preserving_headings(html)
            prepared_pages.append({
                "html": html,
                "page_number": page_num,
                "printed_page_number": printed_page_number,
                "printed_page_number_text": page.get("printed_page_number_text") or (
                    str(printed_page_number) if printed_page_number is not None else None
                ),
                "owner_heading": _first_strong_owner_heading(html),
            })

        candidate_titles = _candidate_titles_for_refinement(portions, portion_idx, page_end)
        stale_portion = any(
            entry.get("kind") == "chapter" and _titles_related(title, entry.get("title"))
            for entry in chapter_files
        )
        refined_segments = _refine_chapter_segments(
            title,
            page_start,
            prepared_pages,
            candidate_titles,
            previous_title=chapter_files[-1]["title"] if chapter_files else None,
            stale_portion=stale_portion,
        )

        for segment in refined_segments:
            if segment.get("carry_back") and chapter_files:
                prev_entry = chapter_files[-1]
                _merge_carry_back_segment(prev_entry, segment)
                prev_toc = chapters_by_start.get(prev_entry["page_start"])
                if prev_toc:
                    prev_toc["page_end"] = prev_entry["page_end"]
                    prev_toc["source_printed_pages"] = prev_entry.get("source_printed_pages") or []
                if toc_entries:
                    toc_entries[-1]["page_end"] = prev_entry["page_end"]
                continue

            chapter_counter += 1
            filename = f"chapter-{chapter_counter:03d}.html"
            body_html = segment["body_html"]
            body_html = _finalize_genealogy_body_html(
                body_html,
                enabled=args.merge_contiguous_genealogy_tables,
            )
            body_html = _normalize_reference_entries(
                body_html,
                enabled=args.normalize_reference_entries,
            )
            toc_entries.append({
                "title": segment["title"],
                "file": filename,
                "page_start": segment["page_start"],
                "page_end": segment["page_end"],
            })
            if segment["page_start"] is not None:
                chapters_by_start[segment["page_start"]] = {
                    "title": segment["title"],
                    "file": filename,
                    "page_start": segment["page_start"],
                    "page_end": segment["page_end"],
                    "source_printed_pages": segment["source_printed_pages"],
                }

            chapter_files.append({
                "filename": filename,
                "title": segment["title"],
                "body_html": body_html,
                "prepared_pages": segment.get("prepared_pages") or [],
                "page_start": segment["page_start"],
                "page_end": segment["page_end"],
                "kind": "chapter",
                "chapter_index": chapter_counter,
                "source_pages": segment["source_pages"],
                "source_printed_pages": segment["source_printed_pages"],
                "source_portion_title": segment["source_portion_title"],
                "source_portion_page_start": segment["source_portion_page_start"],
                "source_portion_titles": segment.get("source_portion_titles") or [segment["source_portion_title"]],
                "source_portion_page_starts": segment.get("source_portion_page_starts") or [segment["source_portion_page_start"]],
            })

    # ── Build fallback pages (uncovered by chapters) ────────────────────
    fallback_entries = []
    fallback_page_files: List[Dict[str, Any]] = []
    fallback_count = 0
    for page in pages_sorted:
        printed_num = _coerce_int(page.get("printed_page_number"))
        printed_text = page.get("printed_page_number_text")
        page_num = _source_page_number(page)
        if (isinstance(printed_num, int) and printed_num in covered_printed_pages) or (
            isinstance(page_num, int) and page_num in covered_source_pages
        ):
            continue
        fallback_count += 1
        filename = f"page-{fallback_count:03d}.html"
        if printed_text:
            title = f"Page {printed_text}"
        elif isinstance(printed_num, int):
            title = f"Page {printed_num}"
        elif page_num is not None:
            title = f"Image {page_num}"
        else:
            title = "Page"
        html = page.get("html") or page.get("raw_html") or ""
        page_num = page.get("page_number") or page.get("page")
        crops = crops_by_page.get(page_num, []) if isinstance(page_num, int) else []
        if crops:
            html = _attach_images(html, crops, args.images_subdir.rstrip("/"))
        body_html = _strip_headers_and_numbers(html)
        body_html = _add_table_scope(body_html)
        body_html = _finalize_genealogy_body_html(
            body_html,
            enabled=args.merge_contiguous_genealogy_tables,
        )

        fallback_entries.append({
            "title": title,
            "file": filename,
            "page_number": page_num,
            "printed_page_number": printed_num,
            "printed_page_number_text": printed_text,
        })

        fallback_page_files.append({
            "filename": filename,
            "title": title,
            "body_html": body_html,
            "prepared_pages": [
                {
                    "html": body_html,
                    "page_number": page_num,
                    "printed_page_number": printed_num,
                    "printed_page_number_text": printed_text or (
                        str(printed_num) if printed_num is not None else None
                    ),
                }
            ],
            "page_start": printed_num if isinstance(printed_num, int) else None,
            "page_end": printed_num if isinstance(printed_num, int) else None,
            "kind": "page",
            "chapter_index": None,
            "page_number": page_num,
            "source_pages": [page_num] if isinstance(page_num, int) else [],
            "source_printed_pages": [printed_num] if isinstance(printed_num, int) else [],
        })

    chapter_files = sorted(
        fallback_page_files + chapter_files,
        key=lambda entry: (
            _coerce_int(entry.get("page_start"))
            if _coerce_int(entry.get("page_start")) is not None
            else (_coerce_int((entry.get("source_pages") or [None])[0]) or 0),
            0 if entry.get("kind") == "page" else 1,
        ),
    )
    bundle_created_at = _utc()

    # ── Write all files with navigation ─────────────────────────────────
    for i, entry in enumerate(chapter_files):
        prev_file = chapter_files[i - 1]["filename"] if i > 0 else None
        prev_title = chapter_files[i - 1]["title"] if i > 0 else None
        next_file = chapter_files[i + 1]["filename"] if i < len(chapter_files) - 1 else None
        next_title = chapter_files[i + 1]["title"] if i < len(chapter_files) - 1 else None

        include_navigation = args.include_navigation and not args.suppress_navigation
        nav_top = _build_nav(prev_file, prev_title, next_file, next_title) if include_navigation else ""
        nav_bottom = _build_nav(prev_file, prev_title, next_file, next_title, is_bottom=True) if include_navigation else ""
        page_title = f"{entry['title']} — {book_title}" if book_title else entry["title"]
        body_html = entry["body_html"]
        body_html = _finalize_genealogy_body_html(
            body_html,
            enabled=args.merge_contiguous_genealogy_tables,
        )
        body_html = _normalize_reference_entries(
            body_html,
            enabled=args.normalize_reference_entries,
        )
        entry["body_html"] = body_html
        should_polish_headings = False
        if entry.get("kind") == "chapter" and (entry.get("source_pages") or []):
            if not (entry.get("source_printed_pages") or []):
                should_polish_headings = True
            else:
                should_polish_headings = _looks_like_catalog_chapter(
                    BeautifulSoup(body_html or "", "html.parser"),
                    entry["title"],
                )
        if should_polish_headings:
            body_html = _polish_flat_chapter_headings(body_html, entry["title"])
            entry["body_html"] = body_html
        body_html = _normalize_catalog_entries(
            body_html,
            title=entry["title"],
            enabled=args.normalize_catalog_entries and entry.get("kind") == "chapter",
        )
        entry["body_html"] = body_html
        body_html, entry_provenance_rows = _tag_entry_body(entry, run_id=args.run_id, created_at=bundle_created_at)
        entry["body_html"] = body_html

        full_html = _html5_wrap(body_html, page_title, nav_top, nav_bottom)
        file_path = html_dir / entry["filename"]
        file_path.write_text(full_html, encoding="utf-8")
        provenance_rows.extend(entry_provenance_rows)

        printed_pages = entry.get("source_printed_pages") or []

        manifest_rows.append({
            "schema_version": "chapter_html_manifest_v1",
            "module_id": "build_chapter_html_v1",
            "run_id": args.run_id,
            "created_at": bundle_created_at,
            "chapter_index": entry["chapter_index"],
            "title": entry["title"],
            "page_start": entry["page_start"],
            "page_end": entry["page_end"],
            "file": str(file_path),
            "kind": entry["kind"],
            "source_pages": entry.get("source_pages"),
            "source_printed_pages": entry.get("source_printed_pages"),
            "source_portion_title": entry.get("source_portion_title"),
            "source_portion_page_start": entry.get("source_portion_page_start"),
            "source_portion_titles": entry.get("source_portion_titles"),
            "source_portion_page_starts": entry.get("source_portion_page_starts"),
        })
        bundle_entries.append(
            {
                "entry_id": Path(entry["filename"]).stem,
                "kind": entry["kind"],
                "title": entry["title"],
                "path": entry["filename"],
                "order": i + 1,
                "prev_entry_id": Path(prev_file).stem if prev_file else None,
                "next_entry_id": Path(next_file).stem if next_file else None,
                "source_pages": entry.get("source_pages") or [],
                "printed_pages": printed_pages,
                "printed_page_start": printed_pages[0] if printed_pages else None,
                "printed_page_end": printed_pages[-1] if printed_pages else None,
            }
        )

    # ── Build index page ────────────────────────────────────────────────
    index_entries = []
    emitted_chapters = set()
    fallback_by_page = {}
    for entry in fallback_entries:
        key = entry.get("page_number")
        if key is not None and key not in fallback_by_page:
            fallback_by_page[key] = entry

    for page in pages_scan:
        printed_num = _coerce_int(page.get("printed_page_number"))
        page_num = _coerce_int(page.get("page_number") or page.get("page"))
        anchor_page = printed_num if isinstance(printed_num, int) else page_num
        if isinstance(anchor_page, int) and anchor_page in chapters_by_start and anchor_page not in emitted_chapters:
            entry = chapters_by_start[anchor_page]
            label = entry["title"]
            chapter_printed_pages = entry.get("source_printed_pages") or []
            if chapter_printed_pages:
                page_start = chapter_printed_pages[0]
                page_end = chapter_printed_pages[-1]
                page_range = f"p. {page_start}" if page_start == page_end else f"p. {page_start}&ndash;{page_end}"
            else:
                page_range = ""
            index_entries.append({"label": label, "file": entry["file"], "page_range": page_range})
            emitted_chapters.add(anchor_page)
        if not (
            (isinstance(printed_num, int) and printed_num in covered_printed_pages)
            or (isinstance(page_num, int) and page_num in covered_source_pages)
        ):
            fe = fallback_by_page.get(page_num)
            if fe:
                index_entries.append({"label": fe["title"], "file": fe["file"], "page_range": ""})

    # Build index body
    author_line = f'<p class="author">{html_escape(book_author)}</p>' if book_author else ""
    toc_items = []
    for entry in index_entries:
        range_span = f' <span class="page-range">({entry["page_range"]})</span>' if entry.get("page_range") else ""
        toc_items.append(f'  <li><a href="{entry["file"]}">{html_escape(entry["label"])}</a>{range_span}</li>')
    index_body = f"""<div class="book-header">
<h1>{html_escape(book_title)}</h1>
{author_line}
</div>
<h2>Contents</h2>
<ul class="toc-list">
{chr(10).join(toc_items)}
</ul>
"""
    index_html = _html5_wrap(index_body, book_title or "Index")
    index_path = html_dir / "index.html"
    index_path.write_text(index_html, encoding="utf-8")

    provenance_path = html_dir / "provenance" / "blocks.jsonl"
    save_jsonl(str(provenance_path), provenance_rows)
    save_json(
        str(html_dir / "manifest.json"),
        {
            "schema_version": "doc_web_bundle_manifest_v1",
            "module_id": "build_chapter_html_v1",
            "run_id": args.run_id,
            "created_at": bundle_created_at,
            "document_id": _slugify(book_title),
            "title": book_title,
            "creator": book_author or None,
            "source_artifact": _display_path(args.pages, run_dir),
            "index_path": "index.html",
            "entries": bundle_entries,
            "reading_order": [entry["entry_id"] for entry in bundle_entries],
            "asset_roots": emitted_asset_roots,
            "provenance_path": "provenance/blocks.jsonl",
        },
    )

    save_jsonl(args.out, manifest_rows)
    logger = ProgressLogger(state_path=args.state_file, progress_path=args.progress_file, run_id=args.run_id)
    logger.log("build", "done", current=len(manifest_rows), total=len(manifest_rows),
               message=f"Wrote {len(manifest_rows)} chapters to {html_dir}")


if __name__ == "__main__":
    main()
