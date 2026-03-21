#!/usr/bin/env python3
"""
Generalize the Story 159 thin hybrid repair proof to a broader Onward slice.

This script starts from stock Docling `baseline-images` artifacts, finds suspect
page spans from page/block signals in the Docling JSON, reruns only those page
images, and emits inspectable repair plans plus repaired HTML candidates.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bs4 import BeautifulSoup, Tag

from modules.adapter.table_rescue_onward_tables_v1.main import (
    _call_ocr,
    _normalize_rescue_html,
)
from modules.common.onward_genealogy_html import merge_contiguous_genealogy_tables
from modules.extract.ocr_ai_gpt51_v1.main import (
    _extract_code_fence,
    _extract_ocr_metadata,
    build_system_prompt,
    sanitize_html,
)
from modules.validate.validate_onward_genealogy_consistency_v1.main import analyze_page_row


EXPECTED_HEADERS = ("name", "born", "married", "spouse", "boy", "girl", "died")
SUMMARY_LABELS = ("TOTAL DESCENDANTS", "LIVING", "DECEASED")
FAMILY_HEADING_RE = re.compile(r"\b[A-Z][A-Z'’\-]+(?:\s+[A-Z][A-Z'’\-]+)*\s+FAMILY\b")
GENERATION_CONTEXT_RE = re.compile(
    r"\b(?:great\s+grandchildren|grandchildren|children)\b",
    re.IGNORECASE,
)
COMBINED_BOY_GIRL_RE = re.compile(r"\bBOY\s*/?\s*GIRL\b", re.IGNORECASE)
NUMERIC_PAGE_RE = re.compile(r"^\d{1,3}$")

BASE_PROMPT_HINTS = """
- Return HTML only for the CURRENT page image.
- Preserve exact wording, names, dates, punctuation, and uncertain OCR
  spellings visible on the page.
- If the page contains genealogy rows, emit genealogy content as HTML
  <table> rows with the visible columns NAME, BORN, MARRIED, SPOUSE,
  BOY, GIRL, and DIED.
- If the page contains a short descendants summary such as TOTAL DESCENDANTS,
  LIVING, or DECEASED, emit that summary as its own simple <table> instead of
  loose paragraphs.
- Use subgroup rows for family headings and generation context instead of
  leaking those labels into ordinary cells or loose paragraphs.
- Emit subgroup rows as
  <tr class="genealogy-subgroup-heading"><th colspan="7">...</th></tr>
  when possible.
- One visible source line should map to one <tr> row.
- If a spouse or death continuation appears on a second visual line, keep it
  as a second row with blank leading cells.
- Do not invent rows from previous or next pages.
- Trust the image for final structure; the extracted clue may be structurally
  wrong.
""".strip()


@dataclass(frozen=True)
class LaneConfig:
    lane_id: str
    document_title: str
    profile: str
    baseline_summary: Path
    baseline_html: Path
    baseline_json: Path
    page_image_dir: Path
    gold_html: Optional[Path] = None


@dataclass
class PageSignal:
    page_no: int
    printed_page_number: Optional[int]
    text_count: int
    table_count: int
    baseline_text_refs: list[str]
    baseline_table_refs: list[str]
    text_samples: list[str]
    table_leak_samples: list[str]
    header_spill_count: int
    heading_text_count: int
    inline_heading_leak_count: int
    combined_boy_girl_count: int
    summary_label_count: int
    reasons: list[str]
    signal_score: int


def _default_lanes() -> dict[str, LaneConfig]:
    return {
        "arthur": LaneConfig(
            lane_id="arthur",
            document_title="Arthur L'Heureux",
            profile="onset_before_first_table",
            baseline_summary=Path("output/runs/story160-docling-baseline-arthur-r1/summary.json"),
            baseline_html=Path(
                "output/runs/story160-docling-baseline-arthur-r1/docling/baseline-images/"
                "05 ARTHUR L'HEUREUX.html"
            ),
            baseline_json=Path(
                "output/runs/story160-docling-baseline-arthur-r1/docling/baseline-images/"
                "05 ARTHUR L'HEUREUX.json"
            ),
            page_image_dir=Path(
                "output/runs/story160-docling-baseline-arthur-r1/docling/baseline-images/images"
            ),
            gold_html=Path("benchmarks/golden/onward/arthur.html"),
        ),
        "pierre": LaneConfig(
            lane_id="pierre",
            document_title="Pierre L'Heureux",
            profile="later_spill_after_leaky_tables",
            baseline_summary=Path("output/runs/story160-docling-baseline-pierre-r1/summary.json"),
            baseline_html=Path(
                "output/runs/story160-docling-baseline-pierre-r1/docling/baseline-images/"
                "17 PIERRE L'HEUREUX.html"
            ),
            baseline_json=Path(
                "output/runs/story160-docling-baseline-pierre-r1/docling/baseline-images/"
                "17 PIERRE L'HEUREUX.json"
            ),
            page_image_dir=Path(
                "output/runs/story160-docling-baseline-pierre-r1/docling/baseline-images/images"
            ),
            gold_html=Path(
                "benchmarks/golden/onward/reviewed_html_slice/"
                "story149-onward-build-regression-r1/chapter-022.html"
            ),
        ),
    }


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _normalize_text(text: str | None) -> str:
    return re.sub(r"\s+", " ", (text or "").replace("’", "'")).strip()


def _normalize_key(text: str | None) -> str:
    return _normalize_text(text).casefold()


def _normalize_token(text: str | None) -> str:
    return re.sub(r"[^a-z]", "", (text or "").lower())


def _extract_family_labels(text: str) -> list[str]:
    normalized = _normalize_text(text).upper()
    return list(dict.fromkeys(FAMILY_HEADING_RE.findall(normalized)))


def _is_generation_context_text(text: str) -> bool:
    normalized = _normalize_text(text)
    if not normalized or len(normalized) > 160:
        return False
    if _extract_family_labels(normalized):
        return False
    if any(label in normalized.upper() for label in SUMMARY_LABELS):
        return False
    return bool(GENERATION_CONTEXT_RE.search(normalized))


def _summary_label_count(text: str) -> int:
    upper = _normalize_text(text).upper()
    return sum(1 for label in SUMMARY_LABELS if label in upper)


def _header_token_hits(text: str) -> list[str]:
    normalized = _normalize_text(text)
    upper = normalized.upper()
    hits = [token for token in EXPECTED_HEADERS if token.upper() in upper]
    if COMBINED_BOY_GIRL_RE.search(normalized):
        for token in ("boy", "girl"):
            if token not in hits:
                hits.append(token)
    return sorted(set(hits))


def _usage_to_dict(usage: Any) -> Optional[dict[str, Any]]:
    if usage is None:
        return None
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    if hasattr(usage, "dict"):
        return usage.dict()
    if hasattr(usage, "__dict__"):
        return dict(usage.__dict__)
    return {"value": str(usage)}


def _encode_image(path: Path) -> str:
    image_b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
    suffix = path.suffix.lower().lstrip(".") or "png"
    return f"data:image/{suffix};base64,{image_b64}"


def _clean_raw_html(raw_html: str) -> str:
    raw_html = _extract_code_fence(raw_html or "")
    cleaned_raw, _, _, _ = _extract_ocr_metadata(raw_html)
    cleaned = sanitize_html(cleaned_raw)
    return _normalize_rescue_html(cleaned).strip()


def _table_rows_from_block(table_block: dict[str, Any]) -> list[list[dict[str, Any]]]:
    rows: dict[int, dict[int, dict[str, Any]]] = {}
    for cell in table_block.get("data", {}).get("table_cells", []):
        text = _normalize_text(cell.get("text"))
        if not text:
            continue
        row_idx = int(cell.get("start_row_offset_idx", 0))
        col_idx = int(cell.get("start_col_offset_idx", 0))
        rows.setdefault(row_idx, {})[col_idx] = {
            "text": text,
            "is_header": bool(cell.get("column_header")),
            "row_span": int(cell.get("row_span") or 1),
            "col_span": int(cell.get("col_span") or 1),
        }
    ordered_rows: list[list[dict[str, Any]]] = []
    for row_idx in sorted(rows):
        ordered_rows.append([rows[row_idx][col_idx] for col_idx in sorted(rows[row_idx])])
    return ordered_rows


def _render_table_clue(table_block: dict[str, Any]) -> str:
    rows = _table_rows_from_block(table_block)
    parts = ["<table>"]
    for row in rows:
        parts.append("<tr>")
        for cell in row:
            tag = "th" if cell["is_header"] else "td"
            attrs = ""
            if cell["col_span"] > 1:
                attrs += f' colspan="{cell["col_span"]}"'
            if cell["row_span"] > 1:
                attrs += f' rowspan="{cell["row_span"]}"'
            parts.append(f"<{tag}{attrs}>{cell['text']}</{tag}>")
        parts.append("</tr>")
    parts.append("</table>")
    return "\n".join(parts)


def _page_clue_html(page_no: int, page_bucket: dict[str, Any]) -> str:
    parts = [f"<!-- baseline clue for page {page_no} -->"]
    for text_block in page_bucket.get("texts", []):
        text = _normalize_text(text_block.get("text"))
        if text:
            parts.append(f"<p>{text}</p>")
    for table_block in page_bucket.get("tables", []):
        parts.append(_render_table_clue(table_block))
    return "\n".join(parts)


def _build_page_buckets(doc: dict[str, Any]) -> dict[int, dict[str, Any]]:
    page_buckets: dict[int, dict[str, Any]] = {}

    def ensure_page(page_no: int) -> dict[str, Any]:
        bucket = page_buckets.setdefault(page_no, {"texts": [], "tables": []})
        return bucket

    for raw_page_no in doc.get("pages", {}).keys():
        ensure_page(int(raw_page_no))

    for text_block in doc.get("texts", []):
        prov = text_block.get("prov") or []
        page_no = prov[0].get("page_no") if prov else None
        if page_no is None:
            continue
        ensure_page(int(page_no))["texts"].append(text_block)

    for table_block in doc.get("tables", []):
        prov = table_block.get("prov") or []
        page_no = prov[0].get("page_no") if prov else None
        if page_no is None:
            continue
        ensure_page(int(page_no))["tables"].append(table_block)

    return page_buckets


def _scan_page(page_no: int, page_bucket: dict[str, Any]) -> PageSignal:
    printed_page_number: Optional[int] = None
    text_refs: list[str] = []
    table_refs: list[str] = []
    text_samples: list[str] = []
    table_leak_samples: list[str] = []
    header_spill_count = 0
    heading_text_count = 0
    combined_boy_girl_count = 0
    summary_label_count = 0
    inline_heading_leak_count = 0

    for text_block in page_bucket.get("texts", []):
        text = _normalize_text(text_block.get("text"))
        if not text:
            continue
        text_refs.append(str(text_block.get("self_ref") or ""))
        if NUMERIC_PAGE_RE.fullmatch(text):
            printed_page_number = int(text)
        else:
            text_samples.append(text[:220])
        header_hits = _header_token_hits(text)
        if len(header_hits) >= 3:
            header_spill_count += 1
        if _extract_family_labels(text) or _is_generation_context_text(text):
            heading_text_count += 1
        if COMBINED_BOY_GIRL_RE.search(text):
            combined_boy_girl_count += 1
        summary_label_count += _summary_label_count(text)

    for table_block in page_bucket.get("tables", []):
        table_refs.append(str(table_block.get("self_ref") or ""))
        for row in _table_rows_from_block(table_block):
            row_texts = [_normalize_text(cell["text"]) for cell in row if _normalize_text(cell["text"])]
            if not row_texts:
                continue
            joined = " | ".join(row_texts)
            marker_hit = any(
                _extract_family_labels(text) or _is_generation_context_text(text)
                for text in row_texts
            )
            if marker_hit:
                inline_heading_leak_count += 1
                if len(table_leak_samples) < 8:
                    table_leak_samples.append(joined[:240])
            if COMBINED_BOY_GIRL_RE.search(joined):
                combined_boy_girl_count += 1
            summary_label_count += _summary_label_count(joined)

    reasons: list[str] = []
    if page_bucket.get("tables"):
        if inline_heading_leak_count > 0:
            reasons.append("inline_heading_leaks_in_table")
        if combined_boy_girl_count > 0:
            reasons.append("combined_boy_girl_header_in_table")
    else:
        if header_spill_count > 0:
            reasons.append("header_spill_without_table")
        if heading_text_count > 0:
            reasons.append("heading_spill_without_table")
        if summary_label_count > 0:
            reasons.append("summary_labels_without_table")

    signal_score = (
        header_spill_count * 5
        + heading_text_count * 4
        + inline_heading_leak_count * 3
        + combined_boy_girl_count * 2
        + summary_label_count
    )

    return PageSignal(
        page_no=page_no,
        printed_page_number=printed_page_number,
        text_count=len(page_bucket.get("texts", [])),
        table_count=len(page_bucket.get("tables", [])),
        baseline_text_refs=text_refs,
        baseline_table_refs=table_refs,
        text_samples=text_samples[:8],
        table_leak_samples=table_leak_samples,
        header_spill_count=header_spill_count,
        heading_text_count=heading_text_count,
        inline_heading_leak_count=inline_heading_leak_count,
        combined_boy_girl_count=combined_boy_girl_count,
        summary_label_count=summary_label_count,
        reasons=reasons,
        signal_score=signal_score,
    )


def _select_target_pages(config: LaneConfig, page_signals: list[PageSignal]) -> list[int]:
    if config.profile == "onset_before_first_table":
        for idx, signal in enumerate(page_signals[:-1]):
            next_signal = page_signals[idx + 1]
            if signal.table_count != 0:
                continue
            if "header_spill_without_table" not in signal.reasons:
                continue
            if next_signal.table_count > 0:
                return [signal.page_no, next_signal.page_no]
        raise ValueError(f"{config.lane_id}: no onset spill span found from page signals")

    if config.profile == "later_spill_after_leaky_tables":
        for idx in range(len(page_signals) - 1, -1, -1):
            signal = page_signals[idx]
            if signal.table_count != 0:
                continue
            if not (
                "header_spill_without_table" in signal.reasons
                or "heading_spill_without_table" in signal.reasons
                or "summary_labels_without_table" in signal.reasons
            ):
                continue
            start_idx = idx
            while start_idx > 0 and page_signals[start_idx - 1].table_count > 0:
                start_idx -= 1
            if start_idx != idx:
                return [page_signals[pos].page_no for pos in range(start_idx, idx + 1)]
        raise ValueError(f"{config.lane_id}: no trailing spill span found from page signals")

    raise ValueError(f"Unsupported lane profile: {config.profile}")


def _ocr_page(
    *,
    model: str,
    image_path: Path,
    clue_html: str,
    max_output_tokens: int,
    timeout_seconds: float,
    is_first_target_page: bool,
) -> dict[str, Any]:
    profile_hint = (
        "- Include the genealogy section heading if it is visibly present.\n"
        if is_first_target_page
        else "- This page may continue a genealogy table from the previous page.\n"
    )
    prompt = build_system_prompt(f"{BASE_PROMPT_HINTS}\n{profile_hint}")
    user_text = (
        "Return only HTML for the current page image. The extracted blocks below are a "
        "clue for wording but may be structurally wrong.\n"
        "<current-page>\n"
        f"{clue_html}\n"
        "</current-page>"
    )
    raw_html, usage, request_id = _call_ocr(
        model,
        prompt,
        _encode_image(image_path),
        0.0,
        max_output_tokens,
        timeout_seconds,
        user_text=user_text,
    )
    clean_html = _clean_raw_html(raw_html)
    return {
        "raw_html": raw_html,
        "clean_html": clean_html,
        "usage": _usage_to_dict(usage),
        "request_id": request_id,
        "image_path": str(image_path),
    }


def _insert_fragment_before(anchor: Any, fragment_html: str) -> None:
    fragment_soup = BeautifulSoup(fragment_html or "", "html.parser")
    for node in list(fragment_soup.contents):
        anchor.insert_before(node)


def _insert_fragment_after(anchor: Any, fragment_html: str) -> None:
    fragment_soup = BeautifulSoup(fragment_html or "", "html.parser")
    last = anchor
    for node in list(fragment_soup.contents):
        last.insert_after(node)
        last = node


def _heading_matches_document(tag: Tag, document_title: str) -> bool:
    if tag.name not in {"h1", "h2"}:
        return False
    normalized = _normalize_key(tag.get_text(" ", strip=True))
    title_key = _normalize_key(document_title)
    title_no_apostrophe = title_key.replace("'", "")
    return normalized in {title_key, title_no_apostrophe}


def _find_candidate_heading(soup: BeautifulSoup, document_title: str) -> Optional[Tag]:
    candidates: list[tuple[int, int, Tag]] = []
    for index, tag in enumerate(soup.find_all(["h1", "h2"])):
        if not _heading_matches_document(tag, document_title):
            continue
        cursor = tag.find_next_sibling()
        paragraph_count = 0
        table_found = False
        while cursor is not None:
            if getattr(cursor, "name", None) == "table":
                table_found = True
                break
            if getattr(cursor, "name", None) == "p":
                text = _normalize_text(cursor.get_text(" ", strip=True))
                if text:
                    paragraph_count += 1
            cursor = cursor.find_next_sibling()
        if table_found:
            candidates.append((paragraph_count, index, tag))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[:2])
    return candidates[0][2]


def _ensure_heading(fragment_html: str, document_title: str) -> str:
    soup = BeautifulSoup(fragment_html or "", "html.parser")
    first_heading = soup.find(["h1", "h2"])
    if first_heading is not None and _heading_matches_document(first_heading, document_title):
        return str(soup)
    heading = soup.new_tag("h2")
    heading.string = document_title
    if soup.contents:
        soup.insert(0, heading)
    else:
        soup.append(heading)
    return str(soup)


def _replace_onset_before_first_table(full_html: str, document_title: str, merged_excerpt_html: str) -> str:
    soup = BeautifulSoup(full_html or "", "html.parser")
    heading = _find_candidate_heading(soup, document_title)
    if heading is None:
        raise ValueError(f"{document_title}: candidate genealogy heading not found")
    first_table = heading.find_next("table")
    if first_table is None:
        raise ValueError(f"{document_title}: first genealogy table not found")

    node: Any = heading
    while node is not None and node is not first_table:
        next_node = node.next_sibling
        node.extract()
        node = next_node

    _insert_fragment_before(first_table, _ensure_heading(merged_excerpt_html, document_title))
    first_table.extract()
    return str(soup)


def _replace_first_table_to_end(full_html: str, document_title: str, merged_excerpt_html: str) -> str:
    soup = BeautifulSoup(full_html or "", "html.parser")
    heading = _find_candidate_heading(soup, document_title)
    if heading is None:
        raise ValueError(f"{document_title}: candidate genealogy heading not found")
    first_table = heading.find_next("table")
    if first_table is None:
        raise ValueError(f"{document_title}: first genealogy table not found")

    container = first_table.parent
    node: Any = first_table
    while node is not None:
        next_node = node.next_sibling
        node.extract()
        node = next_node

    _insert_fragment_after(heading, merged_excerpt_html)
    if container is not None and container.name in {"body", "div", "article"}:
        return str(soup)
    return str(soup)


def _heading_like_paragraphs(soup: BeautifulSoup) -> list[str]:
    hits: list[str] = []
    for tag in soup.find_all(["h1", "h2", "h3", "p"]):
        if tag.find_parent("table") is not None:
            continue
        text = _normalize_text(tag.get_text(" ", strip=True))
        if not text:
            continue
        if _extract_family_labels(text) or _is_generation_context_text(text):
            hits.append(text)
            continue
        header_hits = _header_token_hits(text)
        if len(header_hits) >= 3 or _summary_label_count(text) > 0:
            hits.append(text)
    return hits


def _table_heading_leaks(soup: BeautifulSoup) -> list[str]:
    leaks: list[str] = []
    for row in soup.find_all("tr"):
        if "genealogy-subgroup-heading" in (row.get("class") or []):
            continue
        cell_texts = [
            _normalize_text(cell.get_text(" ", strip=True))
            for cell in row.find_all(["th", "td"], recursive=False)
            if _normalize_text(cell.get_text(" ", strip=True))
        ]
        if not cell_texts:
            continue
        if any(_extract_family_labels(text) or _is_generation_context_text(text) for text in cell_texts):
            leaks.append(" | ".join(cell_texts))
    return leaks


def _combined_header_hits(soup: BeautifulSoup) -> list[str]:
    hits: list[str] = []
    for cell in soup.find_all(["th", "td"]):
        text = _normalize_text(cell.get_text(" ", strip=True))
        if text and COMBINED_BOY_GIRL_RE.search(text):
            hits.append(text)
    return hits


def _summarize_html_signals(html: str, document_title: str) -> dict[str, Any]:
    soup = BeautifulSoup(html or "", "html.parser")
    candidate_heading = _find_candidate_heading(soup, document_title)
    pretable_paragraphs: list[str] = []
    if candidate_heading is not None:
        cursor = candidate_heading.find_next_sibling()
        while cursor is not None and getattr(cursor, "name", None) != "table":
            if getattr(cursor, "name", None) == "p":
                text = _normalize_text(cursor.get_text(" ", strip=True))
                if text:
                    pretable_paragraphs.append(text)
            cursor = cursor.find_next_sibling()
    heading_paragraphs = _heading_like_paragraphs(soup)
    table_leaks = _table_heading_leaks(soup)
    combined_headers = _combined_header_hits(soup)
    return {
        "pretable_paragraph_count": len(pretable_paragraphs),
        "pretable_paragraph_samples": pretable_paragraphs[:6],
        "heading_like_block_count": len(heading_paragraphs),
        "heading_like_block_samples": heading_paragraphs[:10],
        "table_heading_leak_count": len(table_leaks),
        "table_heading_leak_samples": table_leaks[:10],
        "combined_boy_girl_header_count": len(combined_headers),
        "combined_boy_girl_header_samples": combined_headers[:10],
        "subgroup_row_count": len(soup.select("tr.genealogy-subgroup-heading")),
    }


def _lane_markdown(summary: dict[str, Any]) -> str:
    baseline = summary["baseline_signals"]
    repaired = summary["repaired_signals"]
    lines = [
        f"# {summary['document_title']} Hybrid Generalization",
        "",
        "## Selection",
        f"- profile: `{summary['profile']}`",
        f"- target pages: `{summary['target_pages']}`",
        f"- source pdf: `{summary['source_pdf']}`",
        "",
        "## Before vs After",
        f"- pre-table paragraphs: `{baseline['pretable_paragraph_count']}` -> `{repaired['pretable_paragraph_count']}`",
        f"- heading-like loose blocks: `{baseline['heading_like_block_count']}` -> `{repaired['heading_like_block_count']}`",
        f"- table heading leaks: `{baseline['table_heading_leak_count']}` -> `{repaired['table_heading_leak_count']}`",
        f"- subgroup rows: `{baseline['subgroup_row_count']}` -> `{repaired['subgroup_row_count']}`",
        f"- combined BOY/GIRL headers: `{baseline['combined_boy_girl_header_count']}` -> `{repaired['combined_boy_girl_header_count']}`",
        "",
        "## Artifacts",
        f"- merged excerpt: `{summary['artifacts']['merged_excerpt_html']}`",
    ]
    full_candidate = summary["artifacts"].get("full_candidate_html")
    if full_candidate:
        lines.append(f"- full candidate: `{full_candidate}`")
    if summary.get("gold_html"):
        lines.append(f"- incumbent reviewed html: `{summary['gold_html']}`")
    lines.append("")
    return "\n".join(lines)


def _run_lane(
    *,
    config: LaneConfig,
    lane_outdir: Path,
    model: str,
    max_output_tokens: int,
    timeout_seconds: float,
) -> dict[str, Any]:
    baseline_summary = _read_json(config.baseline_summary)
    baseline_doc = _read_json(config.baseline_json)
    baseline_html = config.baseline_html.read_text(encoding="utf-8")
    source_pdf = baseline_summary["input_pdf"]
    page_buckets = _build_page_buckets(baseline_doc)

    page_signals = [_scan_page(page_no, page_buckets[page_no]) for page_no in sorted(page_buckets)]
    target_pages = _select_target_pages(config, page_signals)
    lane_outdir.mkdir(parents=True, exist_ok=True)
    _write_json(lane_outdir / "page-signals.json", [asdict(signal) for signal in page_signals])

    clue_artifacts: dict[int, str] = {}
    page_requests: list[dict[str, Any]] = []
    clean_fragments: list[str] = []

    for index, page_no in enumerate(target_pages):
        page_clue = _page_clue_html(page_no, page_buckets[page_no])
        clue_path = lane_outdir / f"page-{page_no:03d}-clue.html"
        _write_text(clue_path, page_clue)
        clue_artifacts[page_no] = str(clue_path)

        image_path = config.page_image_dir / f"page-{page_no:03d}.png"
        page_result = _ocr_page(
            model=model,
            image_path=image_path,
            clue_html=page_clue,
            max_output_tokens=max_output_tokens,
            timeout_seconds=timeout_seconds,
            is_first_target_page=index == 0,
        )
        raw_path = lane_outdir / f"page-{page_no:03d}-raw.html"
        clean_path = lane_outdir / f"page-{page_no:03d}-clean.html"
        _write_text(raw_path, page_result["raw_html"])
        _write_text(clean_path, page_result["clean_html"])
        clean_fragments.append(page_result["clean_html"])
        page_requests.append(
            {
                "page_no": page_no,
                "image_path": page_result["image_path"],
                "request_id": page_result["request_id"],
                "usage": page_result["usage"],
                "clue_html": str(clue_path),
                "raw_html": str(raw_path),
                "clean_html": str(clean_path),
                "baseline_text_refs": next(
                    signal.baseline_text_refs for signal in page_signals if signal.page_no == page_no
                ),
                "baseline_table_refs": next(
                    signal.baseline_table_refs for signal in page_signals if signal.page_no == page_no
                ),
            }
        )

    raw_excerpt = "\n".join(clean_fragments)
    merged_excerpt = merge_contiguous_genealogy_tables(
        raw_excerpt,
        rescue_normalizer=sanitize_html,
    )
    if config.profile == "onset_before_first_table":
        merged_excerpt = _ensure_heading(merged_excerpt, config.document_title)

    merged_excerpt_path = lane_outdir / "merged-excerpt.html"
    _write_text(merged_excerpt_path, merged_excerpt)

    full_candidate_html: Optional[str] = None
    full_candidate_path: Optional[Path] = None
    if config.profile == "onset_before_first_table":
        full_candidate_html = _replace_onset_before_first_table(
            baseline_html,
            config.document_title,
            merged_excerpt,
        )
    elif config.profile == "later_spill_after_leaky_tables":
        full_candidate_html = _replace_first_table_to_end(
            baseline_html,
            config.document_title,
            merged_excerpt,
        )

    if full_candidate_html is not None:
        full_candidate_path = lane_outdir / "full-candidate.html"
        _write_text(full_candidate_path, full_candidate_html)

    baseline_metrics = analyze_page_row({"html": baseline_html}).__dict__
    merged_excerpt_metrics = analyze_page_row({"html": merged_excerpt}).__dict__
    baseline_signals = _summarize_html_signals(baseline_html, config.document_title)
    repaired_signals = _summarize_html_signals(
        full_candidate_html or merged_excerpt,
        config.document_title,
    )

    gold_metrics = None
    gold_signals = None
    if config.gold_html is not None and config.gold_html.exists():
        gold_html = config.gold_html.read_text(encoding="utf-8")
        gold_metrics = analyze_page_row({"html": gold_html}).__dict__
        gold_signals = _summarize_html_signals(gold_html, config.document_title)

    lane_summary = {
        "schema_version": "story160_docling_hybrid_generalization_v1",
        "lane_id": config.lane_id,
        "document_title": config.document_title,
        "profile": config.profile,
        "source_pdf": source_pdf,
        "baseline_summary": str(config.baseline_summary),
        "baseline_html": str(config.baseline_html),
        "baseline_json": str(config.baseline_json),
        "gold_html": str(config.gold_html) if config.gold_html is not None else None,
        "target_pages": target_pages,
        "page_signals": [asdict(signal) for signal in page_signals],
        "page_requests": page_requests,
        "baseline_metrics": baseline_metrics,
        "merged_excerpt_metrics": merged_excerpt_metrics,
        "full_candidate_metrics": analyze_page_row({"html": full_candidate_html}).__dict__
        if full_candidate_html is not None
        else None,
        "gold_metrics": gold_metrics,
        "baseline_signals": baseline_signals,
        "repaired_signals": repaired_signals,
        "gold_signals": gold_signals,
        "artifacts": {
            "merged_excerpt_html": str(merged_excerpt_path),
            "full_candidate_html": str(full_candidate_path) if full_candidate_path is not None else None,
            "page_clues": clue_artifacts,
        },
    }
    _write_json(lane_outdir / "summary.json", lane_summary)
    _write_text(lane_outdir / "summary.md", _lane_markdown(lane_summary))
    return lane_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generalize the Docling Tier 2 hybrid repair proof on Arthur and Pierre."
    )
    parser.add_argument("--outdir", default="output/runs/story160-docling-generalization-r1")
    parser.add_argument("--model", default="gpt-5")
    parser.add_argument("--max-output-tokens", type=int, default=12000)
    parser.add_argument("--timeout-seconds", type=float, default=180.0)
    parser.add_argument(
        "--lane",
        action="append",
        choices=sorted(_default_lanes()),
        help="Lane to run. Defaults to all configured lanes.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    lane_configs = _default_lanes()
    selected_lane_ids = args.lane or list(lane_configs.keys())
    summaries: list[dict[str, Any]] = []
    for lane_id in selected_lane_ids:
        lane_summary = _run_lane(
            config=lane_configs[lane_id],
            lane_outdir=outdir / lane_id,
            model=args.model,
            max_output_tokens=args.max_output_tokens,
            timeout_seconds=args.timeout_seconds,
        )
        summaries.append(lane_summary)

    summary = {
        "schema_version": "story160_docling_hybrid_generalization_run_v1",
        "model": args.model,
        "outdir": str(outdir),
        "lanes": summaries,
    }
    _write_json(outdir / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
