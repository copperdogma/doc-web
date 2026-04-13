#!/usr/bin/env python3
"""
Structured or row-oriented repair target for the maintained Onward genealogy seam.

This stage reuses the existing Story 146 planner target selection logic, but
asks the model for a structured genealogy representation instead of direct page
HTML. The structured response is rendered deterministically back into HTML,
evaluated against the existing page artifact, and written out as a new
page_html_v1 artifact plus inspectable structured sidecars and reports.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from copy import deepcopy
from html import escape as html_escape
from typing import Any, Dict, List, Optional

from modules.adapter.table_rescue_onward_tables_v1.main import _encode_image
from modules.adapter.rerun_onward_genealogy_consistency_v1.main import (
    _best_effort_normalize_html,
    _coerce_page_number,
    _evaluate_candidate,
    _load_pages,
    _parse_csv_ints,
    _parse_csv_strings,
    _report_path,
    _resolve_input_paths,
    _usage_to_dict,
    _utc,
    RerunTarget,
    UnresolvedChapter,
    load_targets,
)
from modules.common.onward_openai_ocr import call_ocr as _call_ocr
from modules.common.utils import ProgressLogger, ensure_dir, save_json, save_jsonl
from modules.extract.ocr_ai_gpt51_v1.main import (
    _extract_code_fence,
    build_system_prompt,
    extract_image_metadata,
)


EXPECTED_HEADERS = ("name", "born", "married", "spouse", "boy", "girl", "died")
SEGMENT_KIND_DATA_ROW = "data_row"
SEGMENT_KIND_SUBGROUP = "subgroup_heading"
SEGMENT_KIND_NOTE = "note_row"
SUMMARY_LABEL_RE = re.compile(r"\s+")
DEATH_HINT_RE = re.compile(r"\b(?:died|deceased|death|buried|passed)\b", re.IGNORECASE)
ROW_NOTE_HINT_RE = re.compile(r"\b(?:born|boys?|girls?|child(?:ren)?|was born|to\b|infants?\s+died)\b", re.IGNORECASE)
AGE_NOTE_HINT_RE = re.compile(r"\b(?:\d+\s+(?:months?|years?)\s+old|infant)\b", re.IGNORECASE)
COUNT_NAME_NOTE_RE = re.compile(r"^\d+\s*[-A-Za-z]")
PURE_DATE_RE = re.compile(
    r"^(?:"
    r"[A-Za-z]{3,9}\.?\s+\d{1,2}(?:/\d{2,4})?(?:,\s*\d{2,4})?"
    r"|[A-Za-z]{3,9}\.?\s+\d{4}"
    r"|[A-Za-z]{3,9}\.?,\s*\d{4}"
    r"|\d{4}"
    r"|,\s*\d{4}"
    r")$",
    re.IGNORECASE,
)

STRUCTURED_HINTS = """
- This is a targeted structured reread for an Onward genealogy page.
- Return JSON only for the CURRENT page image. Do not return HTML.
- Preserve exact wording, names, punctuation, dates, and uncertain OCR spellings visible on the target page image.
- Use the canonical cells NAME, BORN, MARRIED, SPOUSE, BOY, GIRL, and DIED.
- Output rows in visible top-to-bottom order.
- Use subgroup_heading segments for family labels and generation-context labels instead of burying them inside ordinary cells.
- One visible source line should map to one data_row segment.
- If a spouse or death continuation appears on a second visual line, emit another data_row with blank leading cells.
- Keep short summary rows such as TOTAL DESCENDANTS, LIVING, and DECEASED in summary_rows, not in loose_paragraphs.
- If you are unsure about a cell, leave it as an empty string rather than inventing text.
- Do not copy rows from neighbor pages; neighbors are hints only.
- JSON shape:
  {
    "canonical_headers": ["NAME", "BORN", "MARRIED", "SPOUSE", "BOY", "GIRL", "DIED"],
    "table_segments": [
      {"kind": "subgroup_heading", "text": "LAWRENCE'S FAMILY"},
      {
        "kind": "data_row",
        "cells": {
          "name": "Alice",
          "born": "Jan. 1, 1970",
          "married": "",
          "spouse": "",
          "boy": "1",
          "girl": "1",
          "died": ""
        }
      }
    ],
    "summary_rows": [{"label": "TOTAL DESCENDANTS", "value": "2"}],
    "loose_paragraphs": []
  }
""".strip()


def _normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _json_candidate_from_text(raw: str) -> str:
    text = (_extract_code_fence(raw or "") or "").strip()
    if not text:
        return text
    if text.startswith("{") and text.endswith("}"):
        return text
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start : end + 1]
    return text


def _parse_json_payload(raw: str) -> Dict[str, Any]:
    candidate = _json_candidate_from_text(raw)
    if not candidate:
        raise ValueError("Empty structured response")
    payload = json.loads(candidate)
    if not isinstance(payload, dict):
        raise ValueError("Structured response must be a JSON object")
    for key in ("structured_page", "page"):
        nested = payload.get(key)
        if isinstance(nested, dict):
            payload = nested
            break
    return payload


def _normalize_boy_girl_fields(cells: Dict[str, str]) -> Dict[str, str]:
    combined = cells.get("boygirl") or cells.get("boy_girl") or cells.get("boys_girls")
    if (cells.get("boy") or cells.get("girl")) or not combined:
        return cells
    parts = re.split(r"\s*/\s*|\s{2,}|\s+", combined.strip())
    if len(parts) >= 2:
        cells["boy"] = parts[0]
        cells["girl"] = parts[1]
    elif len(parts) == 1:
        cells["boy"] = parts[0]
        cells["girl"] = ""
    return cells


def _normalize_cells(raw: Any) -> Dict[str, str]:
    source = raw or {}
    if not isinstance(source, dict):
        raise ValueError("data_row cells must be a JSON object")
    normalized = {header: "" for header in EXPECTED_HEADERS}
    extras: Dict[str, str] = {}
    for key, value in source.items():
        token = re.sub(r"[^a-z]", "", str(key or "").lower())
        text = _normalize_text(value)
        if token in normalized:
            normalized[token] = text
        elif token:
            extras[token] = text
    normalized.update({key: value for key, value in extras.items() if key not in normalized})
    normalized = _normalize_boy_girl_fields(normalized)
    return {header: _normalize_text(normalized.get(header, "")) for header in EXPECTED_HEADERS}


def _looks_like_death_value(text: str) -> bool:
    normalized = _normalize_text(text)
    if not normalized:
        return False
    if PURE_DATE_RE.fullmatch(normalized):
        return True
    return bool(DEATH_HINT_RE.search(normalized))


def _semantic_note_text_from_died_cell(cells: Dict[str, str]) -> Optional[str]:
    died_text = _normalize_text(cells.get("died", ""))
    if not died_text or _looks_like_death_value(died_text):
        return None
    if COUNT_NAME_NOTE_RE.match(died_text):
        return died_text
    if ROW_NOTE_HINT_RE.search(died_text):
        return died_text
    if AGE_NOTE_HINT_RE.search(died_text):
        return died_text
    return None


def _note_row_text_from_cells(cells: Dict[str, str]) -> Optional[str]:
    if any(_normalize_text(cells.get(header, "")) for header in EXPECTED_HEADERS[:-1]):
        return None
    return _semantic_note_text_from_died_cell(cells) or (
        _normalize_text(cells.get("died", "")) if not _looks_like_death_value(cells.get("died", "")) else None
    )


def _split_embedded_note_row(segment: Dict[str, Any]) -> List[Dict[str, Any]]:
    if segment.get("kind") != SEGMENT_KIND_DATA_ROW:
        return [segment]
    cells = dict(segment.get("cells") or {})
    note_text = _semantic_note_text_from_died_cell(cells)
    if not note_text:
        return [segment]
    if not any(_normalize_text(cells.get(header, "")) for header in EXPECTED_HEADERS[:-1]):
        return [segment]
    cells["died"] = ""
    return [
        {"kind": SEGMENT_KIND_DATA_ROW, "cells": cells},
        {"kind": SEGMENT_KIND_NOTE, "text": note_text},
    ]


def _normalize_summary_rows(raw_rows: Any) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for raw in raw_rows or []:
        if isinstance(raw, str):
            label = _normalize_text(raw)
            if label:
                rows.append({"label": label, "value": ""})
            continue
        if not isinstance(raw, dict):
            continue
        label = _normalize_text(raw.get("label") or raw.get("name") or raw.get("text"))
        value = _normalize_text(raw.get("value") or raw.get("count") or raw.get("total"))
        if label:
            rows.append({"label": label, "value": value})
    return rows


def _normalize_loose_paragraphs(raw_rows: Any) -> List[str]:
    paragraphs: List[str] = []
    for raw in raw_rows or []:
        text = _normalize_text(raw)
        if text:
            paragraphs.append(text)
    return paragraphs


def _normalize_segment(raw: Any) -> Optional[Dict[str, Any]]:
    if isinstance(raw, str):
        text = _normalize_text(raw)
        if text:
            return {"kind": SEGMENT_KIND_SUBGROUP, "text": text}
        return None
    if not isinstance(raw, dict):
        return None

    kind_token = re.sub(r"[^a-z]", "", str(raw.get("kind") or raw.get("type") or "").lower())
    if kind_token in {"subgroupheading", "heading", "context", "family", "familyheading"}:
        text = _normalize_text(raw.get("text") or raw.get("label") or raw.get("heading"))
        if text:
            return {"kind": SEGMENT_KIND_SUBGROUP, "text": text}
        return None

    cells = raw.get("cells")
    if isinstance(cells, dict):
        normalized_cells = _normalize_cells(cells)
        note_text = _note_row_text_from_cells(normalized_cells)
        if note_text:
            return {"kind": SEGMENT_KIND_NOTE, "text": note_text}
        return {"kind": SEGMENT_KIND_DATA_ROW, "cells": normalized_cells}

    if kind_token in {"datarow", "row", "person", "continuation"}:
        normalized_cells = _normalize_cells(raw)
        note_text = _note_row_text_from_cells(normalized_cells)
        if note_text:
            return {"kind": SEGMENT_KIND_NOTE, "text": note_text}
        return {"kind": SEGMENT_KIND_DATA_ROW, "cells": normalized_cells}

    if any(key in raw for key in EXPECTED_HEADERS):
        normalized_cells = _normalize_cells(raw)
        note_text = _note_row_text_from_cells(normalized_cells)
        if note_text:
            return {"kind": SEGMENT_KIND_NOTE, "text": note_text}
        return {"kind": SEGMENT_KIND_DATA_ROW, "cells": normalized_cells}

    text = _normalize_text(raw.get("text") or raw.get("label"))
    if text:
        return {"kind": SEGMENT_KIND_SUBGROUP, "text": text}
    return None


def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    raw_segments = (
        payload.get("table_segments")
        or payload.get("segments")
        or payload.get("rows")
        or []
    )
    segments: List[Dict[str, Any]] = []
    for raw in raw_segments:
        normalized = _normalize_segment(raw)
        if normalized is not None:
            segments.extend(_split_embedded_note_row(normalized))

    canonical_headers = [
        _normalize_text(value).upper()
        for value in (payload.get("canonical_headers") or [])
        if _normalize_text(value)
    ] or [header.upper() for header in EXPECTED_HEADERS]

    return {
        "canonical_headers": canonical_headers,
        "table_segments": segments,
        "summary_rows": _normalize_summary_rows(payload.get("summary_rows")),
        "loose_paragraphs": _normalize_loose_paragraphs(payload.get("loose_paragraphs") or payload.get("paragraphs")),
    }


def _render_structured_html(payload: Dict[str, Any]) -> str:
    parts: List[str] = []

    segments = payload.get("table_segments") or []
    if segments:
        parts.append("<table>")
        parts.append("<thead><tr>")
        for header in payload.get("canonical_headers") or [header.upper() for header in EXPECTED_HEADERS]:
            parts.append(f"<th>{html_escape(str(header))}</th>")
        parts.append("</tr></thead>")
        parts.append("<tbody>")
        for segment in segments:
            if segment.get("kind") == SEGMENT_KIND_SUBGROUP:
                text = _normalize_text(segment.get("text"))
                if not text:
                    continue
                parts.append(
                    '<tr class="genealogy-subgroup-heading">'
                    f'<th colspan="{len(EXPECTED_HEADERS)}">{html_escape(text)}</th>'
                    "</tr>"
                )
                continue

            if segment.get("kind") == SEGMENT_KIND_NOTE:
                text = _normalize_text(segment.get("text"))
                if not text:
                    continue
                parts.append(
                    '<tr class="genealogy-note-row">'
                    f'<td colspan="{len(EXPECTED_HEADERS)}">{html_escape(text)}</td>'
                    "</tr>"
                )
                continue

            cells = segment.get("cells") or {}
            row_html = "".join(
                f"<td>{html_escape(_normalize_text(cells.get(header, '')))}</td>"
                for header in EXPECTED_HEADERS
            )
            parts.append(f"<tr>{row_html}</tr>")
        parts.append("</tbody>")
        parts.append("</table>")

    summary_rows = payload.get("summary_rows") or []
    if summary_rows:
        parts.append("<table>")
        parts.append("<tbody>")
        for row in summary_rows:
            label = html_escape(_normalize_text(row.get("label")))
            value = html_escape(_normalize_text(row.get("value")))
            parts.append(f"<tr><td>{label}</td><td>{value}</td></tr>")
        parts.append("</tbody>")
        parts.append("</table>")

    for paragraph in payload.get("loose_paragraphs") or []:
        text = _normalize_text(paragraph)
        if text:
            parts.append(f"<p>{html_escape(text)}</p>")

    return "\n".join(parts).strip()


def build_structured_user_text(
    target: RerunTarget,
    page_rows: Dict[int, Dict[str, Any]],
    *,
    max_context_chars: int,
) -> str:
    current_row = page_rows[target.page_number]
    current_html = (current_row.get("html") or current_row.get("raw_html") or "").strip()
    parts = [
        "Return JSON only for the CURRENT target page image.",
        "Use neighboring snippets only as consistency hints. Do not copy rows not visible on the target page image.",
        f"Target page: {target.page_number}",
    ]
    if current_row.get("printed_page_number") is not None:
        parts.append(f"Printed page number: {current_row['printed_page_number']}")
    if target.chapter_basename:
        parts.append(f"Chapter artifact: {target.chapter_basename}")
    if target.chapter_title:
        parts.append(f"Chapter title: {target.chapter_title}")
    if target.pattern_label:
        pattern_text = target.pattern_label
        if target.pattern_id:
            pattern_text += f" ({target.pattern_id})"
        parts.append(f"Pattern family: {pattern_text}")
    if target.planner_status:
        parts.append(f"Planner status: {target.planner_status}")
    if target.issue_types:
        parts.append(f"Planner issue types: {', '.join(target.issue_types)}")
    if target.planner_why:
        parts.append(f"Planner conformance reason: {target.planner_why}")
    if target.plan_rule_summary:
        parts.append("Consistency plan guidance:")
        parts.extend(f"- {rule}" for rule in target.plan_rule_summary[:6])
    if target.target_selection_notes:
        parts.append(f"Target selection notes: {' | '.join(target.target_selection_notes[:3])}")

    parts.append(
        '\nRequired JSON keys: "canonical_headers", "table_segments", "summary_rows", "loose_paragraphs".'
    )
    parts.append(
        'Allowed table segment kinds: "subgroup_heading" and "data_row".'
    )

    parts.append("\nCurrent extracted HTML for the target page (may be structurally wrong):\n")
    parts.append(current_html[:max_context_chars])

    remaining = max(0, max_context_chars - len(current_html))
    if target.context_pages and remaining > 200:
        parts.append("\nNeighbor page context:\n")
        for page_number in target.context_pages:
            page_row = page_rows.get(page_number)
            if not page_row:
                continue
            snippet = (page_row.get("html") or page_row.get("raw_html") or "").strip()
            if len(snippet) > 1200:
                snippet = snippet[:1200].rstrip() + "\n..."
            printed_page = page_row.get("printed_page_number")
            printed_suffix = f" (printed {printed_page})" if printed_page is not None else ""
            block = (
                f"Page {page_number}"
                f"{printed_suffix}:\n"
                f"{snippet}"
            )
            if len(block) > remaining:
                block = block[:remaining].rstrip() + "\n..."
            parts.append(block)
            remaining -= len(block)
            if remaining <= 0:
                break

    return "\n".join(parts)


def _build_prompt(extra_hints: Optional[str]) -> str:
    hints = STRUCTURED_HINTS
    if extra_hints:
        hints += "\n" + extra_hints.strip()
    return build_system_prompt(hints)


def _apply_structured_candidate(
    row: Dict[str, Any],
    *,
    rendered_html: str,
) -> None:
    row["raw_html"] = rendered_html
    row["html"] = rendered_html
    images = extract_image_metadata(rendered_html)
    if images:
        row["images"] = images
    else:
        row.pop("images", None)


def run_structured_repairs(
    rows: List[Dict[str, Any]],
    page_rows: Dict[int, Dict[str, Any]],
    targets: List[RerunTarget],
    *,
    unresolved_chapters: Optional[List[UnresolvedChapter]] = None,
    selection_mode: str = "planner",
    planner_artifact_paths: Optional[Dict[str, str]] = None,
    report_path: str,
    summary_path: str,
    sidecar_path: str,
    pages_artifact_path: str,
    consistency_report_path: str,
    out_path: str,
    model: str,
    temperature: float,
    max_output_tokens: int,
    timeout_seconds: Optional[float],
    max_context_chars: int,
    min_score_gain: int,
    min_token_recall: float,
    min_text_ratio: float,
    prompt: str,
    run_id: Optional[str],
    progress_file: Optional[str],
    state_file: Optional[str],
) -> None:
    target_map = {target.page_number: target for target in targets}
    unresolved_chapters = list(unresolved_chapters or [])
    planner_artifact_paths = dict(planner_artifact_paths or {})

    report_rows: List[Dict[str, Any]] = []
    sidecar_rows: List[Dict[str, Any]] = []
    out_rows: List[Dict[str, Any]] = []

    logger = ProgressLogger(state_path=state_file, progress_path=progress_file, run_id=run_id)
    logger.log(
        "transform",
        "running",
        current=0,
        total=max(1, len(target_map)),
        message="Running structured Onward genealogy repairs",
        artifact=out_path,
        module_id="repair_onward_genealogy_structured_v1",
        schema_version="page_html_v1",
        extra={
            "consistency_report": consistency_report_path,
            "selection_mode": selection_mode,
            "structured_sidecar": sidecar_path,
            **planner_artifact_paths,
        },
    )

    accepted_count = 0
    processed_targets = 0
    rejection_reasons: Dict[str, int] = {}
    target_sources: Dict[str, int] = {}

    for unresolved in unresolved_chapters:
        report_rows.append(
            {
                "page_number": None,
                "chapter_basename": unresolved.chapter_basename,
                "chapter_title": unresolved.chapter_title,
                "schema_hint": "",
                "issue_reasons": unresolved.issue_reasons,
                "issue_types": unresolved.issue_types,
                "pattern_id": unresolved.pattern_id or None,
                "pattern_label": unresolved.pattern_label or None,
                "planner_status": unresolved.planner_status or None,
                "planner_why": unresolved.planner_why or None,
                "repair_priority": unresolved.repair_priority or None,
                "plan_rule_summary": unresolved.plan_rule_summary,
                "plan_rule_details": unresolved.plan_rule_details,
                "source_pages": unresolved.source_pages,
                "context_pages": [],
                "target_source": unresolved.target_source,
                "target_selection_notes": unresolved.target_selection_notes,
                "surfaced_new_vs_current_detector": unresolved.surfaced_new_vs_current_detector,
                "targeted": False,
                "accepted": False,
                "decision_reason": unresolved.target_source,
                "unresolved": True,
                "input_pages_artifact_path": pages_artifact_path,
                "output_pages_artifact_path": out_path,
                "consistency_report_artifact_path": consistency_report_path,
                "structured_sidecar_artifact_path": sidecar_path,
                "selection_mode": selection_mode,
                **planner_artifact_paths,
            }
        )

    for row in rows:
        page_number = _coerce_page_number(row)
        new_row = deepcopy(row)
        new_row["module_id"] = "repair_onward_genealogy_structured_v1"
        if run_id:
            new_row["run_id"] = run_id
        new_row["created_at"] = _utc()

        target = target_map.get(page_number or -1)
        if target is None:
            out_rows.append(new_row)
            continue

        processed_targets += 1
        target_sources[target.target_source] = target_sources.get(target.target_source, 0) + 1
        image_path = row.get("image")
        existing_html = row.get("html") or row.get("raw_html") or ""

        report_record: Dict[str, Any] = {
            "page_number": page_number,
            "chapter_basename": target.chapter_basename,
            "chapter_title": target.chapter_title,
            "schema_hint": target.schema_hint,
            "issue_reasons": target.issue_reasons,
            "issue_types": target.issue_types,
            "pattern_id": target.pattern_id or None,
            "pattern_label": target.pattern_label or None,
            "planner_status": target.planner_status or None,
            "planner_why": target.planner_why or None,
            "repair_priority": target.repair_priority or None,
            "plan_rule_summary": target.plan_rule_summary,
            "plan_rule_details": target.plan_rule_details,
            "source_pages": target.source_pages,
            "context_pages": target.context_pages,
            "target_source": target.target_source,
            "target_selection_notes": target.target_selection_notes,
            "surfaced_new_vs_current_detector": target.surfaced_new_vs_current_detector,
            "source_image": image_path,
            "input_pages_artifact_path": pages_artifact_path,
            "output_pages_artifact_path": out_path,
            "consistency_report_artifact_path": consistency_report_path,
            "structured_sidecar_artifact_path": sidecar_path,
            "selection_mode": selection_mode,
            "model": model,
            "existing_html": existing_html,
            **planner_artifact_paths,
        }

        logger.log(
            "transform",
            "running",
            current=processed_targets,
            total=max(1, len(target_map)),
            message=f"Running structured genealogy repair for page {page_number}",
            artifact=out_path,
            module_id="repair_onward_genealogy_structured_v1",
            schema_version="page_html_v1",
        )

        if not image_path or not os.path.exists(image_path):
            report_record.update({"targeted": True, "accepted": False, "decision_reason": "missing_image"})
            rejection_reasons["missing_image"] = rejection_reasons.get("missing_image", 0) + 1
            report_rows.append(report_record)
            out_rows.append(new_row)
            continue

        image_data = _encode_image(image_path)
        user_text = build_structured_user_text(
            target,
            page_rows,
            max_context_chars=max_context_chars,
        )

        request_id = None
        usage = None
        raw_response = ""
        normalized_payload: Optional[Dict[str, Any]] = None
        rendered_html = ""
        decision_reason = "candidate_not_evaluated"
        candidate_eval: Optional[Dict[str, Any]] = None

        try:
            raw_response, usage, request_id = _call_ocr(
                model,
                prompt,
                image_data,
                temperature,
                max_output_tokens,
                timeout_seconds,
                user_text=user_text,
            )
            normalized_payload = _normalize_payload(_parse_json_payload(raw_response))
            rendered_html = _best_effort_normalize_html(_render_structured_html(normalized_payload))
            candidate_eval = _evaluate_candidate(
                existing_html,
                rendered_html,
                min_score_gain=min_score_gain,
                min_token_recall=min_token_recall,
                min_text_ratio=min_text_ratio,
            )
            accepted = bool(candidate_eval["accepted"])
            decision_reason = str(candidate_eval["decision_reason"])
        except Exception as exc:  # pragma: no cover - network/environment dependent
            accepted = False
            decision_reason = "structured_response_error"
            report_record["error"] = str(exc)
            rejection_reasons[decision_reason] = rejection_reasons.get(decision_reason, 0) + 1
            report_record.update(
                {
                    "targeted": True,
                    "accepted": False,
                    "decision_reason": decision_reason,
                    "request_id": request_id,
                    "usage": _usage_to_dict(usage),
                }
            )
            report_rows.append(report_record)
            out_rows.append(new_row)
            continue

        sidecar_record = {
            "schema_version": "structured_onward_genealogy_page_repair_v1",
            "module_id": "repair_onward_genealogy_structured_v1",
            "created_at": _utc(),
            "run_id": run_id,
            "page_number": page_number,
            "printed_page_number": row.get("printed_page_number"),
            "chapter_basename": target.chapter_basename,
            "chapter_title": target.chapter_title,
            "source_image": image_path,
            "source_pages": target.source_pages,
            "context_pages": target.context_pages,
            "target_source": target.target_source,
            "selection_mode": selection_mode,
            "pattern_id": target.pattern_id or None,
            "pattern_label": target.pattern_label or None,
            "planner_status": target.planner_status or None,
            "planner_why": target.planner_why or None,
            "repair_priority": target.repair_priority or None,
            "issue_types": target.issue_types,
            "issue_reasons": target.issue_reasons,
            "target_selection_notes": target.target_selection_notes,
            "plan_rule_summary": target.plan_rule_summary,
            "plan_rule_details": target.plan_rule_details,
            "rebuild_owner_module": "repair_onward_genealogy_structured_v1",
            "raw_response": _json_candidate_from_text(raw_response),
            "structured_payload": normalized_payload,
            "rendered_html": rendered_html,
            "accepted": accepted,
            "decision_reason": decision_reason,
            "request_id": request_id,
            "usage": _usage_to_dict(usage),
            **planner_artifact_paths,
        }
        sidecar_rows.append(sidecar_record)

        if accepted:
            accepted_count += 1
            _apply_structured_candidate(new_row, rendered_html=rendered_html)
        else:
            rejection_reasons[decision_reason] = rejection_reasons.get(decision_reason, 0) + 1

        report_record.update(
            {
                "targeted": True,
                "accepted": accepted,
                "decision_reason": decision_reason,
                "request_id": request_id,
                "usage": _usage_to_dict(usage),
                "candidate_html": rendered_html,
                "final_html": new_row.get("html") or new_row.get("raw_html") or "",
                "structured_payload": normalized_payload,
            }
        )
        if candidate_eval is not None:
            report_record.update(
                {
                    "existing_quality": candidate_eval["existing_quality"],
                    "candidate_quality": candidate_eval["candidate_quality"],
                    "retention_metrics": candidate_eval["retention_metrics"],
                    "existing_page_metrics": candidate_eval["existing_page_metrics"],
                    "candidate_page_metrics": candidate_eval["candidate_page_metrics"],
                    "page_drift_reason": candidate_eval["page_drift_reason"],
                }
            )
        report_rows.append(report_record)
        out_rows.append(new_row)

    summary = {
        "schema_version": "structured_onward_genealogy_summary_v1",
        "module_id": "repair_onward_genealogy_structured_v1",
        "created_at": _utc(),
        "run_id": run_id,
        "input_pages_artifact_path": pages_artifact_path,
        "consistency_report_artifact_path": consistency_report_path,
        "output_pages_artifact_path": out_path,
        "structured_sidecar_artifact_path": sidecar_path,
        "targeted_page_count": len(target_map),
        "targeted_pages": sorted(target_map),
        "selection_mode": selection_mode,
        "target_sources": target_sources,
        "accepted_page_count": accepted_count,
        "rejected_page_count": len(target_map) - accepted_count,
        "rejection_reasons": rejection_reasons,
        "chapters": sorted({target.chapter_basename for target in targets}),
        "unresolved_chapter_count": len(unresolved_chapters),
        "unresolved_chapters": [chapter.chapter_basename for chapter in unresolved_chapters],
        **planner_artifact_paths,
    }

    save_jsonl(out_path, out_rows)
    save_jsonl(report_path, report_rows)
    save_jsonl(sidecar_path, sidecar_rows)
    save_json(summary_path, summary)

    logger.log(
        "transform",
        "done",
        current=len(target_map),
        total=max(1, len(target_map)),
        message=f"Structured Onward genealogy repairs complete: accepted={accepted_count}/{len(target_map)}",
        artifact=out_path,
        module_id="repair_onward_genealogy_structured_v1",
        schema_version="page_html_v1",
        extra={"report": report_path, "summary_report": summary_path, "structured_sidecar": sidecar_path},
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Structured Onward genealogy repair target")
    parser.add_argument("--pages", help="Input page_html_v1 JSONL")
    parser.add_argument("--consistency", help="pipeline_issues_v1 JSONL from plan_onward_document_consistency_v1")
    parser.add_argument("--inputs", nargs="*", help="Driver compatibility: pages JSONL plus consistency JSONL")
    parser.add_argument("--out", required=True, help="Output page_html_v1 JSONL path")
    parser.add_argument("--report", default="structured_onward_genealogy_report.jsonl")
    parser.add_argument("--summary-report", dest="summary_report", default="structured_onward_genealogy_summary.json")
    parser.add_argument("--summary_report", dest="summary_report", default="structured_onward_genealogy_summary.json")
    parser.add_argument("--structured-sidecar", dest="structured_sidecar", default="structured_onward_genealogy_sidecar.jsonl")
    parser.add_argument("--structured_sidecar", dest="structured_sidecar", default="structured_onward_genealogy_sidecar.jsonl")
    parser.add_argument("--pattern-inventory", dest="pattern_inventory", default="pattern_inventory.json")
    parser.add_argument("--pattern_inventory", dest="pattern_inventory", default="pattern_inventory.json")
    parser.add_argument("--consistency-plan", dest="consistency_plan", default="consistency_plan.json")
    parser.add_argument("--consistency_plan", dest="consistency_plan", default="consistency_plan.json")
    parser.add_argument("--conformance-report", dest="conformance_report", default="conformance_report.json")
    parser.add_argument("--conformance_report", dest="conformance_report", default="conformance_report.json")
    parser.add_argument("--planner-status-allowlist", dest="planner_status_allowlist", default="format_drift")
    parser.add_argument("--planner_status_allowlist", dest="planner_status_allowlist", default="format_drift")
    parser.add_argument("--model", default="gpt-5")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-output-tokens", dest="max_output_tokens", type=int, default=16384)
    parser.add_argument("--max_output_tokens", dest="max_output_tokens", type=int, default=16384)
    parser.add_argument("--timeout-seconds", dest="timeout_seconds", type=float, default=120.0)
    parser.add_argument("--timeout_seconds", dest="timeout_seconds", type=float, default=120.0)
    parser.add_argument("--max-context-chars", dest="max_context_chars", type=int, default=6000)
    parser.add_argument("--max_context_chars", dest="max_context_chars", type=int, default=6000)
    parser.add_argument("--page-context-window", dest="page_context_window", type=int, default=1)
    parser.add_argument("--page_context_window", dest="page_context_window", type=int, default=1)
    parser.add_argument("--min-score-gain", dest="min_score_gain", type=int, default=15)
    parser.add_argument("--min_score_gain", dest="min_score_gain", type=int, default=15)
    parser.add_argument("--min-token-recall", dest="min_token_recall", type=float, default=0.75)
    parser.add_argument("--min_token_recall", dest="min_token_recall", type=float, default=0.75)
    parser.add_argument("--min-text-ratio", dest="min_text_ratio", type=float, default=0.65)
    parser.add_argument("--min_text_ratio", dest="min_text_ratio", type=float, default=0.65)
    parser.add_argument("--target-mode", dest="target_mode", choices=("strong", "coarse"), default="strong")
    parser.add_argument("--target_mode", dest="target_mode", choices=("strong", "coarse"), default="strong")
    parser.add_argument("--chapter-allowlist", dest="chapter_allowlist", default="")
    parser.add_argument("--chapter_allowlist", dest="chapter_allowlist", default="")
    parser.add_argument("--page-allowlist", dest="page_allowlist", default="")
    parser.add_argument("--page_allowlist", dest="page_allowlist", default="")
    parser.add_argument("--max-pages", dest="max_pages", type=int, default=10)
    parser.add_argument("--max_pages", dest="max_pages", type=int, default=10)
    parser.add_argument("--structured-hints", dest="structured_hints", default=None)
    parser.add_argument("--structured_hints", dest="structured_hints", default=None)
    parser.add_argument("--progress-file")
    parser.add_argument("--state-file")
    parser.add_argument("--run-id")
    args = parser.parse_args()

    pages_path, consistency_path = _resolve_input_paths(
        pages=args.pages,
        consistency=args.consistency,
        inputs=args.inputs,
    )
    if not pages_path:
        raise SystemExit("Missing --pages/--inputs page_html_v1 artifact")
    if not consistency_path:
        raise SystemExit("Missing --consistency/--inputs pipeline_issues_v1 artifact")
    if not os.path.exists(pages_path):
        raise SystemExit(f"Missing pages artifact: {pages_path}")
    if not os.path.exists(consistency_path):
        raise SystemExit(f"Missing consistency report: {consistency_path}")

    out_path = os.path.abspath(args.out)
    ensure_dir(os.path.dirname(out_path) or ".")
    report_path = _report_path(out_path, args.report)
    summary_path = _report_path(out_path, args.summary_report)
    sidecar_path = _report_path(out_path, args.structured_sidecar)

    rows, page_rows = _load_pages(pages_path)
    selection = load_targets(
        consistency_path,
        page_rows=page_rows,
        target_mode=args.target_mode,
        page_context_window=args.page_context_window,
        chapter_allowlist=_parse_csv_strings(args.chapter_allowlist),
        page_allowlist=_parse_csv_ints(args.page_allowlist),
        max_pages=args.max_pages,
        pattern_inventory_path=args.pattern_inventory,
        consistency_plan_path=args.consistency_plan,
        conformance_report_path=args.conformance_report,
        planner_status_allowlist=_parse_csv_strings(args.planner_status_allowlist),
        return_selection=True,
    )
    prompt = _build_prompt(args.structured_hints)

    run_structured_repairs(
        rows,
        page_rows,
        selection.targets,
        unresolved_chapters=selection.unresolved_chapters,
        selection_mode=selection.selection_mode,
        planner_artifact_paths=selection.artifact_paths,
        report_path=report_path,
        summary_path=summary_path,
        sidecar_path=sidecar_path,
        pages_artifact_path=pages_path,
        consistency_report_path=consistency_path,
        out_path=out_path,
        model=args.model,
        temperature=args.temperature,
        max_output_tokens=args.max_output_tokens,
        timeout_seconds=args.timeout_seconds,
        max_context_chars=args.max_context_chars,
        min_score_gain=args.min_score_gain,
        min_token_recall=args.min_token_recall,
        min_text_ratio=args.min_text_ratio,
        prompt=prompt,
        run_id=args.run_id,
        progress_file=args.progress_file,
        state_file=args.state_file,
    )


if __name__ == "__main__":
    main()
