#!/usr/bin/env python3
"""
Document-level consistency planning for Onward genealogy chapters.

This stage reads built chapter HTML plus page_html_v1 source pages, builds a
compact document dossier, asks an LLM to infer document-local pattern families
and consistency conventions, and emits inspectable sidecar artifacts:

- pattern_inventory.json
- consistency_plan.json
- conformance_report.json
- document_consistency_dossier.json

It keeps a stamped pipeline_issues_v1 summary for recipe integration while
preserving the plan as explicit document-local policy instead of hidden prompt
state.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from bs4 import BeautifulSoup

from modules.common.openai_client import OpenAI
from modules.common.run_registry import resolve_output_root
from modules.common.utils import ProgressLogger, ensure_dir, read_jsonl, save_json, save_jsonl
from modules.validate.validate_onward_genealogy_consistency_v1.main import analyze_chapter_row, analyze_page_row


EXPECTED_HEADERS = ("name", "born", "married", "spouse", "boy", "girl", "died")
FUSED_HEADERS = ("name", "born", "married", "spouse", "boygirl", "died")
SUMMARY_LABELS = ("TOTAL DESCENDANTS", "LIVING", "DECEASED")
FAMILY_HEADING_RE = re.compile(r"\b[A-Z][A-Z'’\\-]+(?:\s+[A-Z][A-Z'’\\-]+)*\s+FAMILY\b")
GENERATION_CONTEXT_RE = re.compile(
    r"\b(?:great\s+great\s+grandchildren|great\s+grandchildren|grandchildren|children)\b",
    re.IGNORECASE,
)
ROW_NOTE_HINT_RE = re.compile(
    r"\b(?:born|boys?|girls?|child(?:ren)?|was born|to\b|infants?\s+died)\b",
    re.IGNORECASE,
)
MONTH_HINT_RE = re.compile(
    r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\b",
    re.IGNORECASE,
)
DEATH_HINT_RE = re.compile(r"\b(?:died|deceased|death|buried|passed)\b", re.IGNORECASE)
PURE_DATE_RE = re.compile(
    r"^(?:"
    r"[A-Za-z]{3,9}\.?\s+\d{1,2}(?:/\d{2,4})?(?:,\s*\d{2,4})?"
    r"|[A-Za-z]{3,9}\.?\s+\d{4}"
    r"|\d{4}"
    r"|,\s*\d{4}"
    r")$",
    re.IGNORECASE,
)
FORMAT_ISSUE_TYPES = {
    "fragmented_multi_table_chapter",
    "concatenated_subgroup_context_rows",
    "fused_boygirl_headers",
    "left_column_only_family_rows",
    "external_family_headings",
    "unexpected_table_schema",
    "missing_subgroup_rows",
}
ROW_SEMANTIC_ISSUE_TYPES = {
    "child_note_in_wrong_column",
    "row_ownership_ambiguity",
    "marginal_note_attachment",
    "handwritten_annotation_interpretation",
}
SYSTEM_PROMPT = """You are a document-consistency planner for extracted genealogy HTML.

You are not applying a global house style. You are inferring document-local
pattern families and deciding how this specific document should stay internally
consistent.

Work from the compact dossier only. Use the provided chapter basenames and page
numbers exactly. Be conservative. If a chapter mostly matches the chosen plan
but still has obvious formatting drift, classify it as format_drift. If a
chapter has row/cell understanding problems (for example child-note or marginal
annotation content ending up in the wrong column), classify that as
row_semantic_issue or mixed, not pure format drift.

Genealogy-specific reminders:
- A separate totals/summary table can be legitimate and should not be treated as
  fragmentation by default.
- Fused BOY/GIRL headers are usually a format problem.
- Concatenated subgroup/context rows, left-column-only family rows, and many
  repeated full-header tables are strong format-consistency problems.
- Marginal or handwritten notes should be handled consistently, but they are a
  semantic placement problem when their meaning or attachment is wrong.

Return strict JSON only.
"""


def _utc() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").replace("’", "'")).strip()


def _normalize_token(text: str) -> str:
    return re.sub(r"[^a-z]", "", (text or "").lower())


def _clean_text_list(values: Iterable[str], limit: int = 5) -> List[str]:
    cleaned: List[str] = []
    seen = set()
    for value in values:
        normalized = _normalize_text(value)
        if not normalized:
            continue
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(normalized)
        if len(cleaned) >= limit:
            break
    return cleaned


def _is_heading_like_text(text: str) -> bool:
    normalized = _normalize_text(text)
    if not normalized:
        return False
    return bool(FAMILY_HEADING_RE.search(normalized.upper()) or GENERATION_CONTEXT_RE.search(normalized))


def _heading_fragment_count(text: str) -> int:
    normalized = _normalize_text(text)
    if not normalized:
        return 0
    family_hits = len(FAMILY_HEADING_RE.findall(normalized.upper()))
    generation_hits = len(GENERATION_CONTEXT_RE.findall(normalized))
    return family_hits + generation_hits


def _table_header_signature(table: Any) -> Tuple[str, ...]:
    header_cells: List[str] = []
    thead = table.find("thead")
    if thead:
        header_cells = [cell.get_text(" ", strip=True) for cell in thead.find_all(["th", "td"])]
    if not header_cells:
        first_row = table.find("tr")
        if first_row:
            header_cells = [cell.get_text(" ", strip=True) for cell in first_row.find_all(["th", "td"])]
    return tuple(token for token in (_normalize_token(cell) for cell in header_cells) if token)


def _is_summary_row_text(text: str) -> bool:
    normalized = _normalize_text(text).upper()
    return any(label in normalized for label in SUMMARY_LABELS)


def _is_summary_table(table: Any) -> bool:
    rows = table.find_all("tr")
    if not rows:
        return False
    texts = [_normalize_text(row.get_text(" ", strip=True)).upper() for row in rows[:3]]
    if not any(texts):
        return False
    if any(_is_summary_row_text(text) for text in texts):
        signature = _table_header_signature(table)
        return not signature or signature not in {EXPECTED_HEADERS, FUSED_HEADERS}
    return False


def _row_cells(row: Any) -> List[str]:
    return [_normalize_text(cell.get_text(" ", strip=True)) for cell in row.find_all(["th", "td"])]


def _row_semantic_note_reason(cells: Sequence[str]) -> Optional[str]:
    if len(cells) < 7:
        return None
    died_cell = cells[-1]
    if not died_cell:
        return None
    normalized = _normalize_text(died_cell)
    if PURE_DATE_RE.fullmatch(normalized):
        return None
    if DEATH_HINT_RE.search(died_cell):
        return None
    if re.match(r"^\d+\s*[-A-Za-z]", normalized):
        return "child_note_in_wrong_column"
    if ROW_NOTE_HINT_RE.search(died_cell):
        return "child_note_in_wrong_column"
    alpha_tokens = re.findall(r"[A-Za-z]+", normalized)
    if (
        MONTH_HINT_RE.search(died_cell)
        and len(alpha_tokens) >= 4
        and ("born" in normalized.lower() or " to " in normalized.lower() or "&" in normalized)
    ):
        return "marginal_note_attachment"
    return None


def _resolve_artifact_path(path: str, *, run_dir: str, output_root: str) -> str:
    raw = Path(path)
    candidates: List[Path] = []
    if raw.is_absolute():
        candidates.append(raw)
    else:
        candidates.extend(
            [
                raw,
                Path(run_dir) / raw,
                Path(output_root) / raw,
                Path(output_root).parent / raw,
            ]
        )

    seen = set()
    for candidate in candidates:
        resolved = str(candidate.resolve(strict=False))
        if resolved in seen:
            continue
        seen.add(resolved)
        if os.path.exists(resolved):
            return resolved
    return str(raw)


def _load_page_rows(path: str) -> Dict[int, Dict[str, Any]]:
    page_rows: Dict[int, Dict[str, Any]] = {}
    for row in read_jsonl(path):
        page_number = row.get("page_number")
        try:
            page_rows[int(page_number)] = row
        except (TypeError, ValueError):
            continue
    return page_rows


def _page_profile(page_row: Dict[str, Any]) -> Dict[str, Any]:
    html = page_row.get("html") or page_row.get("raw_html") or ""
    soup = BeautifulSoup(html, "html.parser")
    metrics = analyze_page_row(page_row)

    signatures = Counter()
    external_headings: List[str] = []
    concatenated_subgroups: List[str] = []
    left_column_rows: List[str] = []
    suspicious_rows: List[Dict[str, Any]] = []

    for heading in soup.find_all(["h2", "h3"]):
        text = _normalize_text(heading.get_text(" ", strip=True))
        if _is_heading_like_text(text):
            external_headings.append(text)

    for table in soup.find_all("table"):
        signature = _table_header_signature(table)
        if signature:
            signatures["|".join(signature)] += 1
        for row in table.find_all("tr"):
            cells = _row_cells(row)
            if not cells:
                continue
            if "genealogy-subgroup-heading" in (row.get("class") or []):
                text = cells[0]
                if _heading_fragment_count(text) >= 2:
                    concatenated_subgroups.append(text)
            elif len(cells) == 1 and _is_heading_like_text(cells[0]):
                colspan = row.find(["th", "td"]).get("colspan") if row.find(["th", "td"]) else None
                try:
                    numeric_colspan = int(colspan) if colspan is not None else 1
                except (TypeError, ValueError):
                    numeric_colspan = 1
                if numeric_colspan <= 2:
                    left_column_rows.append(cells[0])

            reason = _row_semantic_note_reason(cells)
            if reason:
                suspicious_rows.append(
                    {
                        "reason": reason,
                        "row_preview": " | ".join(part for part in cells if part),
                        "died_cell": cells[-1],
                    }
                )

    suggested_issue_types = []
    if metrics.residual_boygirl_header_count > 0:
        suggested_issue_types.append("fused_boygirl_headers")
    if len(concatenated_subgroups) > 0:
        suggested_issue_types.append("concatenated_subgroup_context_rows")
    if len(left_column_rows) > 0:
        suggested_issue_types.append("left_column_only_family_rows")
    if metrics.external_family_heading_count > 0:
        suggested_issue_types.append("external_family_headings")
    if metrics.table_count >= 2 and signatures.get("|".join(EXPECTED_HEADERS), 0) + signatures.get("|".join(FUSED_HEADERS), 0) >= 2:
        suggested_issue_types.append("fragmented_multi_table_chapter")
    if suspicious_rows:
        suggested_issue_types.append("child_note_in_wrong_column")

    return {
        "page_number": page_row.get("page_number"),
        "printed_page_number": page_row.get("printed_page_number"),
        "image": page_row.get("image"),
        "signals": {
            "table_count": metrics.table_count,
            "subgroup_row_count": metrics.subgroup_row_count,
            "external_family_heading_count": metrics.external_family_heading_count,
            "residual_boygirl_header_count": metrics.residual_boygirl_header_count,
            "concatenated_subgroup_row_count": len(concatenated_subgroups),
            "left_column_only_family_row_count": len(left_column_rows),
            "suspicious_row_semantic_count": len(suspicious_rows),
            "header_signatures": dict(signatures),
            "suggested_issue_types": suggested_issue_types,
        },
        "signal_examples": {
            "external_headings": _clean_text_list(external_headings, limit=3),
            "concatenated_subgroups": _clean_text_list(concatenated_subgroups, limit=3),
            "left_column_family_rows": _clean_text_list(left_column_rows, limit=3),
            "suspicious_rows": suspicious_rows[:2],
        },
    }


def _chapter_profile(
    manifest_row: Dict[str, Any],
    *,
    page_rows_by_number: Dict[int, Dict[str, Any]],
    chapters_path: str,
    flag_threshold: int,
) -> Optional[Dict[str, Any]]:
    metrics = analyze_chapter_row(manifest_row, flag_threshold=flag_threshold)
    if metrics is None:
        return None

    output_root = resolve_output_root(run_dir=str(Path(chapters_path).parent))
    chapter_file = _resolve_artifact_path(metrics.chapter_file, run_dir=str(Path(chapters_path).parent), output_root=output_root)
    if not os.path.exists(chapter_file):
        return None

    soup = BeautifulSoup(Path(chapter_file).read_text(encoding="utf-8"), "html.parser")
    signatures = Counter()
    summary_table_count = 0
    external_headings: List[str] = []
    subgroup_examples: List[str] = []
    concatenated_subgroups: List[str] = []
    left_column_rows: List[str] = []
    summary_rows: List[str] = []
    suspicious_rows: List[Dict[str, Any]] = []

    for heading in soup.find_all(["h2", "h3"]):
        text = _normalize_text(heading.get_text(" ", strip=True))
        if _is_heading_like_text(text):
            external_headings.append(text)

    for table in soup.find_all("table"):
        if _is_summary_table(table):
            summary_table_count += 1
        signature = _table_header_signature(table)
        if signature:
            signatures["|".join(signature)] += 1
        for row in table.find_all("tr"):
            cells = _row_cells(row)
            if not cells:
                continue
            row_text = " ".join(part for part in cells if part)
            if _is_summary_row_text(row_text):
                summary_rows.append(row_text)
            if "genealogy-subgroup-heading" in (row.get("class") or []):
                subgroup_examples.append(cells[0])
                if _heading_fragment_count(cells[0]) >= 2:
                    concatenated_subgroups.append(cells[0])
            elif len(cells) == 1 and _is_heading_like_text(cells[0]):
                colspan = row.find(["th", "td"]).get("colspan") if row.find(["th", "td"]) else None
                try:
                    numeric_colspan = int(colspan) if colspan is not None else 1
                except (TypeError, ValueError):
                    numeric_colspan = 1
                if numeric_colspan <= 2:
                    left_column_rows.append(cells[0])

            reason = _row_semantic_note_reason(cells)
            if reason:
                suspicious_rows.append(
                    {
                        "reason": reason,
                        "row_preview": " | ".join(part for part in cells if part),
                        "died_cell": cells[-1],
                    }
                )

    suggested_issue_types: List[str] = []
    if metrics.genealogy_table_count >= 2:
        suggested_issue_types.append("fragmented_multi_table_chapter")
    if metrics.residual_boygirl_header_count > 0:
        suggested_issue_types.append("fused_boygirl_headers")
    if concatenated_subgroups:
        suggested_issue_types.append("concatenated_subgroup_context_rows")
    if left_column_rows:
        suggested_issue_types.append("left_column_only_family_rows")
    if external_headings:
        suggested_issue_types.append("external_family_headings")
    if metrics.genealogy_table_count >= 3 and metrics.subgroup_row_count == 0:
        suggested_issue_types.append("missing_subgroup_rows")
    if suspicious_rows:
        suggested_issue_types.append("child_note_in_wrong_column")

    page_profiles: List[Dict[str, Any]] = []
    for page_number in metrics.source_pages:
        page_row = page_rows_by_number.get(page_number)
        if not page_row:
            continue
        page_profile = _page_profile(page_row)
        if page_profile["signals"]["suggested_issue_types"] or not page_profiles:
            page_profiles.append(page_profile)
    page_profiles = page_profiles[:4]

    return {
        "chapter_basename": metrics.chapter_basename,
        "chapter_title": metrics.chapter_title,
        "chapter_file": metrics.chapter_file,
        "chapter_artifact_path": chapter_file,
        "source_pages": metrics.source_pages,
        "source_printed_pages": metrics.source_printed_pages,
        "current_detector": {
            "flagged": metrics.flagged,
            "drift_score": metrics.drift_score,
            "confidence": metrics.confidence,
            "reasons": metrics.reasons,
            "dominant_signature": metrics.dominant_signature,
        },
        "signals": {
            "genealogy_table_count": metrics.genealogy_table_count,
            "all_table_count": metrics.all_table_count,
            "summary_table_count": summary_table_count,
            "subgroup_row_count": metrics.subgroup_row_count,
            "external_family_heading_count": metrics.external_family_heading_count,
            "residual_boygirl_header_count": metrics.residual_boygirl_header_count,
            "concatenated_subgroup_row_count": len(concatenated_subgroups),
            "left_column_only_family_row_count": len(left_column_rows),
            "suspicious_row_semantic_count": len(suspicious_rows),
            "header_signatures": dict(signatures),
            "suggested_issue_types": suggested_issue_types,
        },
        "signal_examples": {
            "subgroup_rows": _clean_text_list(subgroup_examples, limit=5),
            "external_headings": _clean_text_list(external_headings, limit=4),
            "concatenated_subgroups": _clean_text_list(concatenated_subgroups, limit=4),
            "left_column_family_rows": _clean_text_list(left_column_rows, limit=4),
            "summary_rows": _clean_text_list(summary_rows, limit=4),
            "suspicious_rows": suspicious_rows[:4],
        },
        "page_profiles": page_profiles,
    }


def build_document_dossier(
    manifest_rows: Sequence[Dict[str, Any]],
    page_rows_by_number: Dict[int, Dict[str, Any]],
    *,
    chapters_path: str,
    pages_path: str,
    flag_threshold: int,
) -> Dict[str, Any]:
    chapter_profiles = [
        profile
        for profile in (
            _chapter_profile(
                row,
                page_rows_by_number=page_rows_by_number,
                chapters_path=chapters_path,
                flag_threshold=flag_threshold,
            )
            for row in manifest_rows
        )
        if profile
    ]

    header_counter = Counter()
    chapter_issue_counter = Counter()
    suggested_watchlist: List[str] = []
    for chapter in chapter_profiles:
        header_counter.update(chapter["signals"]["header_signatures"])
        issue_types = chapter["signals"]["suggested_issue_types"]
        chapter_issue_counter.update(issue_types)
        if issue_types and not chapter["current_detector"]["flagged"]:
            suggested_watchlist.append(chapter["chapter_basename"])

    return {
        "schema_version": "onward_document_consistency_dossier_v1",
        "created_at": _utc(),
        "document_label": "Onward genealogy consistency planning",
        "source_artifacts": {
            "chapters_artifact": chapters_path,
            "pages_artifact": pages_path,
        },
        "baseline": {
            "candidate_genealogy_chapters": len(chapter_profiles),
            "current_detector_flagged_chapters": [
                chapter["chapter_basename"]
                for chapter in chapter_profiles
                if chapter["current_detector"]["flagged"]
            ],
            "current_detector_unflagged_watchlist": sorted(suggested_watchlist),
            "issue_signal_counts": dict(chapter_issue_counter),
            "header_signature_counts": dict(header_counter),
        },
        "chapter_profiles": chapter_profiles,
    }


def _truncate(value: str, limit: int = 220) -> str:
    normalized = _normalize_text(value)
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def _compact_header_shapes(header_signatures: Dict[str, int]) -> Dict[str, Any]:
    recognized = {
        key: value
        for key, value in header_signatures.items()
        if key in {"|".join(EXPECTED_HEADERS), "|".join(FUSED_HEADERS), "totaldescendants"}
    }
    unexpected = sum(value for key, value in header_signatures.items() if key not in recognized)
    return {
        "recognized": recognized,
        "unexpected_shape_count": unexpected,
    }


def _planner_input_from_dossier(dossier: Dict[str, Any]) -> Dict[str, Any]:
    chapters: List[Dict[str, Any]] = []
    for chapter in dossier["chapter_profiles"]:
        chapters.append(
            {
                "chapter_basename": chapter["chapter_basename"],
                "chapter_title": chapter["chapter_title"],
                "source_pages": chapter["source_pages"],
                "source_printed_pages": chapter["source_printed_pages"],
                "current_detector": chapter["current_detector"],
                "signals": {
                    **{k: v for k, v in chapter["signals"].items() if k != "header_signatures"},
                    "header_shapes": _compact_header_shapes(chapter["signals"]["header_signatures"]),
                },
                "signal_examples": {
                    "subgroup_rows": [_truncate(value, 140) for value in (chapter["signal_examples"].get("subgroup_rows") or [])[:3]],
                    "external_headings": [_truncate(value, 160) for value in (chapter["signal_examples"].get("external_headings") or [])[:2]],
                    "concatenated_subgroups": [_truncate(value, 200) for value in (chapter["signal_examples"].get("concatenated_subgroups") or [])[:2]],
                    "left_column_family_rows": [_truncate(value, 160) for value in (chapter["signal_examples"].get("left_column_family_rows") or [])[:2]],
                    "summary_rows": [_truncate(value, 160) for value in (chapter["signal_examples"].get("summary_rows") or [])[:2]],
                    "suspicious_rows": [
                        {
                            "reason": item.get("reason"),
                            "row_preview": _truncate(item.get("row_preview") or "", 220),
                            "died_cell": _truncate(item.get("died_cell") or "", 140),
                        }
                        for item in (chapter["signal_examples"].get("suspicious_rows") or [])[:2]
                    ],
                },
                "page_profiles": [
                    {
                        "page_number": page["page_number"],
                        "printed_page_number": page["printed_page_number"],
                        "signals": {
                            **{k: v for k, v in page["signals"].items() if k != "header_signatures"},
                            "header_shapes": _compact_header_shapes(page["signals"]["header_signatures"]),
                        },
                        "signal_examples": {
                            "external_headings": [_truncate(value, 160) for value in (page["signal_examples"].get("external_headings") or [])[:2]],
                            "concatenated_subgroups": [_truncate(value, 180) for value in (page["signal_examples"].get("concatenated_subgroups") or [])[:2]],
                            "left_column_family_rows": [_truncate(value, 160) for value in (page["signal_examples"].get("left_column_family_rows") or [])[:2]],
                            "suspicious_rows": [
                                {
                                    "reason": item.get("reason"),
                                    "row_preview": _truncate(item.get("row_preview") or "", 220),
                                    "died_cell": _truncate(item.get("died_cell") or "", 140),
                                }
                                for item in (page["signal_examples"].get("suspicious_rows") or [])[:1]
                            ],
                        },
                    }
                    for page in (chapter.get("page_profiles") or [])[:2]
                ],
            }
        )

    return {
        "schema_version": "onward_document_consistency_planner_input_v1",
        "created_at": dossier["created_at"],
        "document_label": dossier["document_label"],
        "baseline": dossier["baseline"],
        "chapters": chapters,
    }


def _build_prompt(dossier: Dict[str, Any]) -> str:
    planner_input = _planner_input_from_dossier(dossier)
    compact = json.dumps(planner_input, ensure_ascii=False, indent=2)
    return f"""Analyze this compact dossier for one document's extracted genealogy HTML.

Goals:
1. Identify the repeated pattern families present in the document.
2. Choose document-local consistency conventions for each pattern family.
3. Classify every chapter as one of:
   - conformant
   - format_drift
   - row_semantic_issue
   - mixed
   - uncertain
4. Surface chapters whose format drift is not currently caught by the existing chapter-first detector.

Return JSON with this exact top-level shape:
{{
  "analysis_summary": {{
    "document_scope": "...",
    "default_note_policy": "...",
    "default_note_policy_rationale": "...",
    "overall_confidence": 0.0
  }},
  "pattern_families": [
    {{
      "pattern_id": "pattern_1",
      "label": "...",
      "description": "...",
      "member_chapters": ["chapter-009.html"],
      "baseline_chapters": ["chapter-009.html"],
      "canonical_signals": ["..."],
      "canonical_headers": ["NAME", "BORN", "MARRIED", "SPOUSE", "BOY", "GIRL", "DIED"],
      "allowed_variants": ["..."],
      "document_local_conventions": {{
        "subgroup_context_rows": "...",
        "table_fragmentation": "...",
        "summary_rows": "...",
        "marginal_or_handwritten_notes": "..."
      }},
      "confidence": 0.0,
      "evidence": [
        {{
          "chapter_basename": "chapter-009.html",
          "page_numbers": [22, 24],
          "quote": "..."
        }}
      ]
    }}
  ],
  "chapter_findings": [
    {{
      "chapter_basename": "chapter-009.html",
      "pattern_id": "pattern_1",
      "status": "row_semantic_issue",
      "issue_types": ["child_note_in_wrong_column"],
      "why": "...",
      "relevant_pages": [24],
      "repair_priority": "medium",
      "evidence": [
        {{
          "chapter_basename": "chapter-009.html",
          "page_number": 24,
          "quote": "..."
        }}
      ]
    }}
  ]
}}

Important:
- Use only chapter basenames and page numbers present in the dossier.
- If a chapter has multiple full genealogy tables plus a separate totals table,
  decide whether that is legitimate or fragmentation from the dossier evidence.
- If child-note or marginal-note content appears in the DIED column, do not call
  that pure format drift.

Dossier:
{compact}
"""


def call_planning_model(
    client: OpenAI,
    *,
    model: str,
    retry_model: Optional[str],
    dossier: Dict[str, Any],
    max_completion_tokens: int,
    timeout: float,
) -> Dict[str, Any]:
    prompt = _build_prompt(dossier)
    errors: List[str] = []

    def _extract_response_text(response: Any) -> str:
        text = getattr(response, "output_text", None) or ""
        if text:
            return text
        chunks: List[str] = []
        for item in getattr(response, "output", None) or []:
            if getattr(item, "type", None) != "message":
                continue
            for content in getattr(item, "content", None) or []:
                if getattr(content, "type", None) == "output_text" and getattr(content, "text", None):
                    chunks.append(str(content.text))
        return "".join(chunks)

    def _parse_json_payload(response_text: str) -> Dict[str, Any]:
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise

    def _call_once(selected_model: str) -> Dict[str, Any]:
        if selected_model.startswith("gpt-5") and hasattr(client, "responses"):
            response = client.responses.create(
                model=selected_model,
                max_output_tokens=max_completion_tokens,
                reasoning={"effort": "low"},
                input=[
                    {"role": "system", "content": [{"type": "input_text", "text": SYSTEM_PROMPT}]},
                    {"role": "user", "content": [{"type": "input_text", "text": prompt}]},
                ],
                timeout=timeout,
            )
            response_text = _extract_response_text(response)
            response_id = getattr(response, "id", None)
            if not response_text:
                status = getattr(response, "status", None)
                incomplete = getattr(response, "incomplete_details", None)
                error = getattr(response, "error", None)
                raise ValueError(
                    "Empty response from document consistency planner "
                    f"(model={selected_model}, response_id={response_id}, status={status}, "
                    f"incomplete_details={incomplete}, error={error})"
                )
            return _parse_json_payload(response_text)

        kwargs: Dict[str, Any] = {
            "model": selected_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
        }
        if selected_model.startswith("gpt-5"):
            kwargs["max_completion_tokens"] = max_completion_tokens
        else:
            kwargs["max_tokens"] = max_completion_tokens
            kwargs["temperature"] = 0.0

        completion = client.chat.completions.create(timeout=timeout, **kwargs)
        message = completion.choices[0].message
        response_text = message.content
        if isinstance(response_text, list):
            joined: List[str] = []
            for item in response_text:
                if isinstance(item, dict):
                    if item.get("type") == "text" and item.get("text"):
                        joined.append(str(item["text"]))
                elif isinstance(item, str):
                    joined.append(item)
            response_text = "".join(joined)
        if not response_text:
            finish_reason = getattr(completion.choices[0], "finish_reason", None)
            refusal = getattr(message, "refusal", None)
            raise ValueError(
                f"Empty response from document consistency planner (model={selected_model}, "
                f"finish_reason={finish_reason}, refusal={refusal})"
            )
        return _parse_json_payload(response_text)

    for selected_model in [model] + ([retry_model] if retry_model and retry_model != model else []):
        try:
            if errors:
                print(
                    f"[plan_onward_document_consistency_v1] retrying with {selected_model} "
                    f"after: {errors[-1]}"
                )
            return _call_once(selected_model)
        except Exception as exc:
            errors.append(f"{selected_model}: {exc}")

    raise RuntimeError("Document consistency planner failed: " + " | ".join(errors))


def _normalize_evidence(evidence: Sequence[Dict[str, Any]], valid_chapters: set[str]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for item in evidence or []:
        chapter_basename = item.get("chapter_basename")
        if chapter_basename not in valid_chapters:
            continue
        page_numbers = []
        for value in item.get("page_numbers") or [item.get("page_number")]:
            try:
                page_numbers.append(int(value))
            except (TypeError, ValueError):
                continue
        normalized.append(
            {
                "chapter_basename": chapter_basename,
                "page_numbers": sorted(set(page_numbers)),
                "quote": _normalize_text(item.get("quote") or ""),
            }
        )
    return normalized[:4]


def _status_from_issue_types(issue_types: Sequence[str]) -> str:
    issues = set(issue_types or [])
    has_format = bool(issues & FORMAT_ISSUE_TYPES)
    has_row = bool(issues & ROW_SEMANTIC_ISSUE_TYPES)
    if has_format and has_row:
        return "mixed"
    if has_format:
        return "format_drift"
    if has_row:
        return "row_semantic_issue"
    return "uncertain"


def _default_evidence_for_issue_types(chapter_profile: Dict[str, Any], issue_types: Sequence[str]) -> List[Dict[str, Any]]:
    examples = chapter_profile["signal_examples"]
    page_profiles = chapter_profile.get("page_profiles") or []
    evidence: List[Dict[str, Any]] = []

    if "concatenated_subgroup_context_rows" in issue_types:
        for quote in examples.get("concatenated_subgroups") or []:
            evidence.append({"chapter_basename": chapter_profile["chapter_basename"], "page_numbers": [], "quote": quote})
    if "left_column_only_family_rows" in issue_types:
        for quote in examples.get("left_column_family_rows") or []:
            evidence.append({"chapter_basename": chapter_profile["chapter_basename"], "page_numbers": [], "quote": quote})
    if "external_family_headings" in issue_types:
        for quote in examples.get("external_headings") or []:
            evidence.append({"chapter_basename": chapter_profile["chapter_basename"], "page_numbers": [], "quote": quote})
    if any(issue in issue_types for issue in ROW_SEMANTIC_ISSUE_TYPES):
        for item in examples.get("suspicious_rows") or []:
            evidence.append(
                {
                    "chapter_basename": chapter_profile["chapter_basename"],
                    "page_numbers": [],
                    "quote": item.get("row_preview") or item.get("died_cell") or "",
                }
            )

    for page_profile in page_profiles:
        relevant = set(issue_types) & set(page_profile["signals"]["suggested_issue_types"])
        if not relevant:
            continue
        quotes = (
            page_profile["signal_examples"].get("concatenated_subgroups")
            or page_profile["signal_examples"].get("left_column_family_rows")
            or page_profile["signal_examples"].get("external_headings")
            or [item.get("row_preview") for item in page_profile["signal_examples"].get("suspicious_rows") or [] if item.get("row_preview")]
        )
        if quotes:
            evidence.append(
                {
                    "chapter_basename": chapter_profile["chapter_basename"],
                    "page_numbers": [page_profile["page_number"]],
                    "quote": quotes[0],
                }
            )
    deduped: List[Dict[str, Any]] = []
    seen = set()
    for item in evidence:
        key = (item["chapter_basename"], tuple(item["page_numbers"]), item["quote"])
        if key in seen or not item["quote"]:
            continue
        seen.add(key)
        deduped.append(item)
        if len(deduped) >= 3:
            break
    return deduped


def build_outputs(
    dossier: Dict[str, Any],
    planner_payload: Dict[str, Any],
    *,
    chapters_path: str,
    pages_path: str,
    run_id: Optional[str],
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    chapter_profiles = {chapter["chapter_basename"]: chapter for chapter in dossier["chapter_profiles"]}
    valid_chapters = set(chapter_profiles)

    pattern_families: List[Dict[str, Any]] = []
    for index, family in enumerate(planner_payload.get("pattern_families") or [], start=1):
        member_chapters = [value for value in family.get("member_chapters") or [] if value in valid_chapters]
        if not member_chapters:
            continue
        baseline_chapters = [value for value in family.get("baseline_chapters") or [] if value in valid_chapters]
        normalized = {
            "pattern_id": family.get("pattern_id") or f"pattern_{index}",
            "label": _normalize_text(family.get("label") or f"Pattern {index}"),
            "description": _normalize_text(family.get("description") or ""),
            "member_chapters": member_chapters,
            "baseline_chapters": baseline_chapters or member_chapters[:1],
            "canonical_signals": _clean_text_list(family.get("canonical_signals") or [], limit=8),
            "canonical_headers": [str(value) for value in (family.get("canonical_headers") or [])][:8],
            "allowed_variants": _clean_text_list(family.get("allowed_variants") or [], limit=6),
            "document_local_conventions": {
                "subgroup_context_rows": _normalize_text(
                    (family.get("document_local_conventions") or {}).get("subgroup_context_rows") or ""
                ),
                "table_fragmentation": _normalize_text(
                    (family.get("document_local_conventions") or {}).get("table_fragmentation") or ""
                ),
                "summary_rows": _normalize_text(
                    (family.get("document_local_conventions") or {}).get("summary_rows") or ""
                ),
                "marginal_or_handwritten_notes": _normalize_text(
                    (family.get("document_local_conventions") or {}).get("marginal_or_handwritten_notes") or ""
                ),
            },
            "confidence": float(family.get("confidence") or 0.0),
            "evidence": _normalize_evidence(family.get("evidence") or [], valid_chapters),
        }
        pattern_families.append(normalized)

    pattern_by_id = {family["pattern_id"]: family for family in pattern_families}
    chapter_findings_by_chapter: Dict[str, Dict[str, Any]] = {}
    for finding in planner_payload.get("chapter_findings") or []:
        chapter_basename = finding.get("chapter_basename")
        if chapter_basename not in valid_chapters:
            continue
        chapter_profile = chapter_profiles[chapter_basename]
        suggested_issue_types = chapter_profile["signals"]["suggested_issue_types"]
        requested_issue_types = [str(value) for value in (finding.get("issue_types") or []) if value]
        issue_types = [value for value in requested_issue_types if value in suggested_issue_types]
        if not issue_types and suggested_issue_types:
            issue_types = suggested_issue_types
        status = _status_from_issue_types(issue_types)
        if not issue_types:
            status = "conformant"
        evidence = _normalize_evidence(finding.get("evidence") or [], valid_chapters)
        if not evidence and issue_types:
            evidence = _default_evidence_for_issue_types(chapter_profile, issue_types)
        page_numbers: List[int] = []
        for value in finding.get("relevant_pages") or []:
            try:
                page_numbers.append(int(value))
            except (TypeError, ValueError):
                continue
        if not page_numbers:
            for item in evidence:
                page_numbers.extend(item.get("page_numbers") or [])
        page_numbers = sorted(set(page_numbers))
        chapter_findings_by_chapter[chapter_basename] = {
            "chapter_basename": chapter_basename,
            "chapter_title": chapter_profile["chapter_title"],
            "pattern_id": finding.get("pattern_id") if finding.get("pattern_id") in pattern_by_id else None,
            "status": status,
            "issue_types": issue_types,
            "why": _normalize_text(finding.get("why") or ""),
            "relevant_pages": page_numbers,
            "repair_priority": _normalize_text(finding.get("repair_priority") or "medium").lower() or "medium",
            "evidence": evidence,
            "current_detector": chapter_profile["current_detector"],
            "source_pages": chapter_profile["source_pages"],
            "source_printed_pages": chapter_profile["source_printed_pages"],
            "suggested_issue_types": suggested_issue_types,
        }

    conformance_chapters: List[Dict[str, Any]] = []
    for chapter_basename, chapter_profile in sorted(chapter_profiles.items()):
        finding = chapter_findings_by_chapter.get(chapter_basename)
        if finding is None:
            inferred_issue_types = chapter_profile["signals"]["suggested_issue_types"]
            inferred_status = "conformant" if not inferred_issue_types else _status_from_issue_types(inferred_issue_types)
            finding = {
                "chapter_basename": chapter_basename,
                "chapter_title": chapter_profile["chapter_title"],
                "pattern_id": None,
                "status": inferred_status,
                "issue_types": inferred_issue_types,
                "why": "Filled from deterministic dossier because the AI response omitted this chapter.",
                "relevant_pages": [],
                "repair_priority": "medium" if inferred_issue_types else "none",
                "evidence": _default_evidence_for_issue_types(chapter_profile, inferred_issue_types),
                "current_detector": chapter_profile["current_detector"],
                "source_pages": chapter_profile["source_pages"],
                "source_printed_pages": chapter_profile["source_printed_pages"],
                "suggested_issue_types": chapter_profile["signals"]["suggested_issue_types"],
            }
        finding["surfaced_new_vs_current_detector"] = (
            finding["status"] in {"format_drift", "mixed"} and not finding["current_detector"]["flagged"]
        )
        conformance_chapters.append(finding)

    format_drift_chapters = [
        chapter["chapter_basename"] for chapter in conformance_chapters if chapter["status"] == "format_drift"
    ]
    row_semantic_chapters = [
        chapter["chapter_basename"] for chapter in conformance_chapters if chapter["status"] == "row_semantic_issue"
    ]
    mixed_issue_chapters = [
        chapter["chapter_basename"] for chapter in conformance_chapters if chapter["status"] == "mixed"
    ]
    newly_surfaced = [
        chapter["chapter_basename"]
        for chapter in conformance_chapters
        if chapter["surfaced_new_vs_current_detector"] and chapter["status"] == "format_drift"
    ]
    newly_surfaced_mixed = [
        chapter["chapter_basename"]
        for chapter in conformance_chapters
        if chapter["surfaced_new_vs_current_detector"] and chapter["status"] == "mixed"
    ]

    summary = {
        "chapters_artifact": chapters_path,
        "pages_artifact": pages_path,
        "candidate_genealogy_chapters": len(conformance_chapters),
        "pattern_family_count": len(pattern_families),
        "format_drift_chapters": format_drift_chapters,
        "row_semantic_issue_chapters": row_semantic_chapters,
        "mixed_issue_chapters": mixed_issue_chapters,
        "newly_surfaced_format_drift_chapters": newly_surfaced,
        "newly_surfaced_mixed_issue_chapters": newly_surfaced_mixed,
        "current_detector_flagged_chapters": dossier["baseline"]["current_detector_flagged_chapters"],
        "default_note_policy": _normalize_text((planner_payload.get("analysis_summary") or {}).get("default_note_policy") or ""),
    }

    pattern_inventory = {
        "schema_version": "document_pattern_inventory_v1",
        "created_at": _utc(),
        "run_id": run_id,
        "document_label": dossier["document_label"],
        "source_artifacts": dossier["source_artifacts"],
        "summary": {
            "pattern_family_count": len(pattern_families),
            "candidate_genealogy_chapters": len(conformance_chapters),
        },
        "pattern_families": pattern_families,
    }
    consistency_plan = {
        "schema_version": "document_consistency_plan_v1",
        "created_at": _utc(),
        "run_id": run_id,
        "document_label": dossier["document_label"],
        "summary": {
            "document_scope": _normalize_text((planner_payload.get("analysis_summary") or {}).get("document_scope") or dossier["document_label"]),
            "default_note_policy": summary["default_note_policy"],
            "default_note_policy_rationale": _normalize_text((planner_payload.get("analysis_summary") or {}).get("default_note_policy_rationale") or ""),
            "overall_confidence": float((planner_payload.get("analysis_summary") or {}).get("overall_confidence") or 0.0),
        },
        "pattern_conventions": [
            {
                "pattern_id": family["pattern_id"],
                "label": family["label"],
                "member_chapters": family["member_chapters"],
                "canonical_headers": family["canonical_headers"],
                "canonical_signals": family["canonical_signals"],
                "allowed_variants": family["allowed_variants"],
                "document_local_conventions": family["document_local_conventions"],
                "confidence": family["confidence"],
            }
            for family in pattern_families
        ],
    }
    conformance_report = {
        "schema_version": "document_conformance_report_v1",
        "created_at": _utc(),
        "run_id": run_id,
        "document_label": dossier["document_label"],
        "summary": summary,
        "chapters": conformance_chapters,
    }

    primary_report = {
        "schema_version": "pipeline_issues_v1",
        "module_id": "plan_onward_document_consistency_v1",
        "run_id": run_id,
        "created_at": _utc(),
        "summary": summary,
        "issues": [
            {
                "type": "document_consistency_planning_issue",
                "severity": "warning",
                "chapter_basename": chapter["chapter_basename"],
                "chapter_title": chapter["chapter_title"],
                "status": chapter["status"],
                "pattern_id": chapter.get("pattern_id"),
                "issue_types": chapter["issue_types"],
                "relevant_pages": chapter["relevant_pages"],
                "surfaced_new_vs_current_detector": chapter["surfaced_new_vs_current_detector"],
                "evidence": chapter["evidence"],
            }
            for chapter in conformance_chapters
            if chapter["status"] != "conformant"
        ],
    }
    return primary_report, pattern_inventory, consistency_plan, conformance_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Plan document-level consistency for Onward genealogy chapters.")
    parser.add_argument("--chapters", required=True, help="chapters_manifest.jsonl from build_chapter_html_v1")
    parser.add_argument("--pages", required=True, help="page_html_v1 JSONL used to build the chapters")
    parser.add_argument("--out", required=True, help="Output JSONL path for pipeline_issues_v1 summary")
    parser.add_argument("--pattern-inventory", dest="pattern_inventory", default="pattern_inventory.json")
    parser.add_argument("--pattern_inventory", dest="pattern_inventory", default="pattern_inventory.json")
    parser.add_argument("--consistency-plan", dest="consistency_plan", default="consistency_plan.json")
    parser.add_argument("--consistency_plan", dest="consistency_plan", default="consistency_plan.json")
    parser.add_argument("--conformance-report", dest="conformance_report", default="conformance_report.json")
    parser.add_argument("--conformance_report", dest="conformance_report", default="conformance_report.json")
    parser.add_argument("--dossier-report", dest="dossier_report", default="document_consistency_dossier.json")
    parser.add_argument("--dossier_report", dest="dossier_report", default="document_consistency_dossier.json")
    parser.add_argument("--model", default="gpt-5")
    parser.add_argument("--retry-model", dest="retry_model", default="gpt-4.1")
    parser.add_argument("--retry_model", dest="retry_model", default="gpt-4.1")
    parser.add_argument("--flag-threshold", dest="flag_threshold", type=int, default=25)
    parser.add_argument("--flag_threshold", dest="flag_threshold", type=int, default=25)
    parser.add_argument("--max-completion-tokens", dest="max_completion_tokens", type=int, default=8000)
    parser.add_argument("--max_completion_tokens", dest="max_completion_tokens", type=int, default=8000)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--progress-file")
    parser.add_argument("--state-file")
    parser.add_argument("--run-id")
    args = parser.parse_args()

    if not os.path.exists(args.chapters):
        raise SystemExit(f"Missing chapters manifest: {args.chapters}")
    if not os.path.exists(args.pages):
        raise SystemExit(f"Missing pages artifact: {args.pages}")

    out_path = os.path.abspath(args.out)
    ensure_dir(os.path.dirname(out_path) or ".")

    def _sidecar_path(raw: str) -> str:
        return raw if os.path.isabs(raw) else os.path.join(os.path.dirname(out_path), raw)

    pattern_inventory_path = _sidecar_path(args.pattern_inventory)
    consistency_plan_path = _sidecar_path(args.consistency_plan)
    conformance_report_path = _sidecar_path(args.conformance_report)
    dossier_path = _sidecar_path(args.dossier_report)

    logger = ProgressLogger(state_path=args.state_file, progress_path=args.progress_file, run_id=args.run_id)
    logger.log(
        "validate",
        "running",
        current=0,
        total=3,
        message="Building document-level consistency dossier",
        artifact=out_path,
        module_id="plan_onward_document_consistency_v1",
        schema_version="pipeline_issues_v1",
    )

    manifest_rows = list(read_jsonl(args.chapters))
    page_rows_by_number = _load_page_rows(args.pages)
    dossier = build_document_dossier(
        manifest_rows,
        page_rows_by_number,
        chapters_path=args.chapters,
        pages_path=args.pages,
        flag_threshold=args.flag_threshold,
    )
    save_json(dossier_path, dossier)

    logger.log(
        "validate",
        "running",
        current=1,
        total=3,
        message="Running document-level consistency planner",
        artifact=out_path,
        module_id="plan_onward_document_consistency_v1",
        schema_version="pipeline_issues_v1",
        extra={"dossier_report": dossier_path},
    )

    client = OpenAI()
    planner_payload = call_planning_model(
        client,
        model=args.model,
        retry_model=args.retry_model,
        dossier=dossier,
        max_completion_tokens=args.max_completion_tokens,
        timeout=args.timeout,
    )

    primary_report, pattern_inventory, consistency_plan, conformance_report = build_outputs(
        dossier,
        planner_payload,
        chapters_path=args.chapters,
        pages_path=args.pages,
        run_id=args.run_id,
    )
    save_json(pattern_inventory_path, pattern_inventory)
    save_json(consistency_plan_path, consistency_plan)
    save_json(conformance_report_path, conformance_report)
    save_jsonl(out_path, [primary_report])

    logger.log(
        "validate",
        "done",
        current=3,
        total=3,
        message=(
            "Document-level consistency planning complete: "
            f"patterns={pattern_inventory['summary']['pattern_family_count']}, "
            f"newly_surfaced={len(conformance_report['summary']['newly_surfaced_format_drift_chapters'])}"
        ),
        artifact=out_path,
        module_id="plan_onward_document_consistency_v1",
        schema_version="pipeline_issues_v1",
        extra={
            "pattern_inventory": pattern_inventory_path,
            "consistency_plan": consistency_plan_path,
            "conformance_report": conformance_report_path,
            "dossier_report": dossier_path,
        },
    )


if __name__ == "__main__":
    main()
