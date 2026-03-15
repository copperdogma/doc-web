#!/usr/bin/env python3
"""
Selective source-aware reruns for Onward genealogy consistency targets.

This module consumes a page_html_v1 artifact plus the chapter-first consistency
report from validate_onward_genealogy_consistency_v1. It reruns only the
selected culprit pages from source images, applies conservative acceptance
checks, and preserves the original page artifact as the fallback.
"""
import argparse
import os
import re
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from bs4 import BeautifulSoup

from modules.adapter.table_rescue_onward_tables_v1.main import (
    _call_ocr,
    _encode_image,
    _extract_family_labels,
    _is_generation_context_text,
    _normalize_rescue_html,
    _should_accept_rescue,
)
from modules.common.utils import ProgressLogger, ensure_dir, read_jsonl, save_json, save_jsonl
from modules.extract.ocr_ai_gpt51_v1.main import (
    _extract_code_fence,
    _extract_ocr_metadata,
    build_system_prompt,
    extract_image_metadata,
    sanitize_html,
)
from modules.validate.validate_onward_genealogy_consistency_v1.main import analyze_page_row


RERUN_HINTS = """
- This is a targeted source-aware rerun for an Onward genealogy page.
- Return HTML only for the CURRENT page image. Do not copy rows from neighbor pages.
- Use the provided schema hint and neighboring page snippets only to infer consistent structure.
- Preserve exact wording, names, punctuation, and dates from the source image.
- Use a genealogy table when the page shows genealogy rows.
- Preferred header order when visible or clearly implied: NAME, BORN, MARRIED, SPOUSE, BOY, GIRL, DIED.
- Do not merge BOY and GIRL into one column.
- Prefer subgroup labels as full-width table heading rows instead of loose paragraphs or separate mini-tables.
- Keep totals (`TOTAL DESCENDANTS`, `LIVING`, `DECEASED`) if visible on the page.
- One visual row in the source should map to one table row. Do not use <br> inside table cells for separate people.
""".strip()

SUMMARY_LABELS = ("TOTAL DESCENDANTS", "LIVING", "DECEASED")
STOP_TOKENS = {
    "THE",
    "AND",
    "NAME",
    "BORN",
    "MARRIED",
    "SPOUSE",
    "BOY",
    "GIRL",
    "DIED",
}


@dataclass
class RerunTarget:
    page_number: int
    chapter_basename: str
    chapter_title: str
    schema_hint: str
    issue_reasons: List[str]
    source_pages: List[int]
    context_pages: List[int]


@dataclass
class RetentionMetrics:
    token_recall: float
    existing_text_chars: int
    candidate_text_chars: int
    text_ratio: float
    family_labels_preserved: bool
    summary_preserved: bool


def _utc() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _parse_csv_ints(raw: str) -> Optional[Set[int]]:
    if not raw:
        return None
    values: Set[int] = set()
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        values.add(int(token))
    return values


def _parse_csv_strings(raw: str) -> Optional[Set[str]]:
    if not raw:
        return None
    values = {token.strip() for token in raw.split(",") if token.strip()}
    return values or None


def _jsonl_schema_version(path: str) -> Optional[str]:
    try:
        for row in read_jsonl(path):
            schema = row.get("schema_version")
            if schema:
                return str(schema)
    except Exception:
        return None
    return None


def _coerce_page_number(row: Dict[str, Any]) -> Optional[int]:
    for key in ("page_number", "page"):
        value = row.get(key)
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return None


def _load_pages(path: str) -> Tuple[List[Dict[str, Any]], Dict[int, Dict[str, Any]]]:
    rows = list(read_jsonl(path))
    page_map: Dict[int, Dict[str, Any]] = {}
    for row in rows:
        page_number = _coerce_page_number(row)
        if page_number is not None:
            page_map[page_number] = row
    return rows, page_map


def _resolve_input_paths(
    *,
    pages: Optional[str],
    consistency: Optional[str],
    inputs: Optional[List[str]],
) -> Tuple[Optional[str], Optional[str]]:
    resolved_pages = pages
    resolved_consistency = consistency
    extra_inputs = list(inputs or [])
    if resolved_pages and resolved_consistency:
        return resolved_pages, resolved_consistency

    for path in extra_inputs:
        schema = _jsonl_schema_version(path)
        if schema == "page_html_v1" and not resolved_pages:
            resolved_pages = path
        elif schema == "pipeline_issues_v1" and not resolved_consistency:
            resolved_consistency = path

    if resolved_pages and resolved_consistency:
        return resolved_pages, resolved_consistency

    remaining = [path for path in extra_inputs if path not in {resolved_pages, resolved_consistency}]
    if not resolved_pages and remaining:
        resolved_pages = remaining.pop(0)
    if not resolved_consistency and remaining:
        resolved_consistency = remaining.pop(0)
    return resolved_pages, resolved_consistency


def _iter_consistency_issues(report_path: str) -> Iterable[Dict[str, Any]]:
    for row in read_jsonl(report_path):
        if row.get("schema_version") != "pipeline_issues_v1":
            continue
        for issue in row.get("issues") or []:
            if issue.get("type") == "onward_genealogy_consistency_drift":
                yield issue


def _derive_context_pages(source_pages: List[int], page_number: int, window: int) -> List[int]:
    if window <= 0:
        return []
    return [
        candidate
        for candidate in source_pages
        if candidate != page_number and abs(candidate - page_number) <= window
    ]


def load_targets(
    report_path: str,
    *,
    target_mode: str,
    page_context_window: int,
    chapter_allowlist: Optional[Set[str]],
    page_allowlist: Optional[Set[int]],
    max_pages: int,
) -> List[RerunTarget]:
    targets: Dict[int, RerunTarget] = {}
    for issue in _iter_consistency_issues(report_path):
        chapter_basename = issue.get("chapter_basename") or ""
        if chapter_allowlist and chapter_basename not in chapter_allowlist:
            continue
        source_pages = [int(page) for page in (issue.get("source_pages") or [])]
        if target_mode == "coarse":
            candidate_pages = [int(page) for page in (issue.get("coarse_suspect_pages") or [])]
        else:
            candidate_pages = [int(page) for page in (issue.get("strong_rerun_candidate_pages") or [])]
        if page_allowlist is not None:
            candidate_pages = [page for page in candidate_pages if page in page_allowlist]

        for page_number in candidate_pages:
            context_pages = _derive_context_pages(source_pages, page_number, page_context_window)
            existing = targets.get(page_number)
            if existing is None:
                targets[page_number] = RerunTarget(
                    page_number=page_number,
                    chapter_basename=chapter_basename,
                    chapter_title=issue.get("chapter_title") or "",
                    schema_hint=issue.get("schema_hint") or "",
                    issue_reasons=list(issue.get("reasons") or []),
                    source_pages=source_pages,
                    context_pages=context_pages,
                )
                continue

            reasons = list(dict.fromkeys(existing.issue_reasons + list(issue.get("reasons") or [])))
            existing.issue_reasons = reasons
            existing.context_pages = sorted(set(existing.context_pages + context_pages))
            existing.source_pages = sorted(set(existing.source_pages + source_pages))
            if not existing.schema_hint and issue.get("schema_hint"):
                existing.schema_hint = issue["schema_hint"]

    target_list = sorted(targets.values(), key=lambda item: item.page_number)
    if max_pages > 0:
        target_list = target_list[:max_pages]
    return target_list


def _html_text(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    return re.sub(r"\s+", " ", soup.get_text(" ", strip=True)).strip()


def _family_labels_from_html(html: str) -> Set[str]:
    soup = BeautifulSoup(html or "", "html.parser")
    labels: Set[str] = set()
    for tag in soup.find_all(["h1", "h2", "h3", "p", "th", "td", "li"]):
        for fragment in tag.stripped_strings:
            text = re.sub(r"\s+", " ", fragment).strip()
            if not text:
                continue
            labels.update(_extract_family_labels(text.upper()))
    return labels


def _table_column_count(table: Any) -> int:
    max_cols = 0
    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"], recursive=False)
        max_cols = max(max_cols, len(cells))
    return max_cols or 1


def _restore_subgroup_row_markers(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    for table in soup.find_all("table"):
        colspan = _table_column_count(table)
        tbody = table.find("tbody", recursive=False)
        if tbody is not None:
            rows = tbody.find_all("tr", recursive=False)
        else:
            rows = table.find_all("tr", recursive=False)[1:]

        for row in rows:
            if "genealogy-subgroup-heading" in (row.get("class") or []):
                continue
            cells = row.find_all(["th", "td"], recursive=False)
            if len(cells) != 1:
                continue
            text = re.sub(r"\s+", " ", cells[0].get_text(" ", strip=True)).strip()
            if not text:
                continue
            if not (_extract_family_labels(text.upper()) or _is_generation_context_text(text)):
                continue
            row["class"] = "genealogy-subgroup-heading"
            cells[0].name = "th"
            cells[0]["colspan"] = str(colspan)
    return str(soup)


def _text_tokens(text: str) -> List[str]:
    tokens = [
        token.upper()
        for token in re.findall(r"[A-Za-z0-9']+", text or "")
        if len(token) > 1
    ]
    return [token for token in tokens if token not in STOP_TOKENS]


def _content_retention_metrics(existing_html: str, candidate_html: str) -> RetentionMetrics:
    existing_text = _html_text(existing_html)
    candidate_text = _html_text(candidate_html)
    existing_tokens = _text_tokens(existing_text)
    candidate_token_set = set(_text_tokens(candidate_text))
    if existing_tokens:
        matched = sum(1 for token in existing_tokens if token in candidate_token_set)
        token_recall = round(matched / len(existing_tokens), 4)
    else:
        token_recall = 1.0

    existing_upper = existing_text.upper()
    candidate_upper = candidate_text.upper()
    existing_family_labels = _family_labels_from_html(existing_html)
    candidate_family_labels = _family_labels_from_html(candidate_html)
    existing_summary = {label for label in SUMMARY_LABELS if label in existing_upper}
    candidate_summary = {label for label in SUMMARY_LABELS if label in candidate_upper}

    existing_chars = len(existing_text)
    candidate_chars = len(candidate_text)
    text_ratio = round(candidate_chars / existing_chars, 4) if existing_chars else 1.0

    return RetentionMetrics(
        token_recall=token_recall,
        existing_text_chars=existing_chars,
        candidate_text_chars=candidate_chars,
        text_ratio=text_ratio,
        family_labels_preserved=existing_family_labels.issubset(candidate_family_labels),
        summary_preserved=existing_summary.issubset(candidate_summary),
    )


def _retention_gate(
    existing_html: str,
    candidate_html: str,
    *,
    min_token_recall: float,
    min_text_ratio: float,
) -> Tuple[bool, str, RetentionMetrics]:
    metrics = _content_retention_metrics(existing_html, candidate_html)
    if not metrics.summary_preserved:
        return False, "candidate_lost_summary_labels", metrics
    if not metrics.family_labels_preserved:
        return False, "candidate_lost_family_labels", metrics
    if metrics.token_recall < min_token_recall:
        return False, "candidate_token_recall_too_low", metrics
    if metrics.existing_text_chars >= 120 and metrics.text_ratio < min_text_ratio:
        return False, "candidate_text_ratio_too_low", metrics
    return True, "candidate_content_retained", metrics


def _page_drift_penalty(metrics: Any) -> int:
    penalty = 0
    penalty += metrics.residual_boygirl_header_count * 40
    penalty += metrics.external_family_heading_count * 25
    if metrics.table_count >= 2:
        penalty += max(metrics.table_count - 1, 0) * 5
        if metrics.subgroup_row_count == 0:
            penalty += 15
    return penalty


def _page_drift_gate(existing_html: str, candidate_html: str) -> Tuple[bool, str, Dict[str, Any], Dict[str, Any]]:
    existing_metrics = analyze_page_row({"html": existing_html})
    candidate_metrics = analyze_page_row({"html": candidate_html})
    existing_dict = asdict(existing_metrics)
    candidate_dict = asdict(candidate_metrics)

    if candidate_metrics.residual_boygirl_header_count > existing_metrics.residual_boygirl_header_count:
        return False, "candidate_worsened_boygirl_headers", existing_dict, candidate_dict
    if candidate_metrics.external_family_heading_count > existing_metrics.external_family_heading_count:
        return False, "candidate_worsened_external_family_headings", existing_dict, candidate_dict

    existing_penalty = _page_drift_penalty(existing_metrics)
    candidate_penalty = _page_drift_penalty(candidate_metrics)
    if candidate_penalty < existing_penalty:
        return True, "candidate_drift_reduced", existing_dict, candidate_dict
    if candidate_penalty > existing_penalty:
        return False, "candidate_drift_worsened", existing_dict, candidate_dict
    return True, "candidate_drift_not_worsened", existing_dict, candidate_dict


def _evaluate_candidate(
    existing_html: str,
    candidate_html: str,
    *,
    min_score_gain: int,
    min_token_recall: float,
    min_text_ratio: float,
) -> Dict[str, Any]:
    accepted_page, page_reason, existing_quality, candidate_quality = _should_accept_rescue(
        existing_html,
        candidate_html,
        0.8,
        min_score_gain,
    )
    retention_ok, retention_reason, retention_metrics = _retention_gate(
        existing_html,
        candidate_html,
        min_token_recall=min_token_recall,
        min_text_ratio=min_text_ratio,
    )
    drift_ok, drift_reason, existing_page_metrics, candidate_page_metrics = _page_drift_gate(
        existing_html,
        candidate_html,
    )
    accepted = retention_ok and drift_ok and (accepted_page or drift_reason == "candidate_drift_reduced")
    if accepted:
        decision_reason = "candidate_accepted" if accepted_page else "candidate_drift_reduced"
    else:
        if not retention_ok:
            decision_reason = retention_reason
        elif not drift_ok:
            decision_reason = drift_reason
        else:
            decision_reason = page_reason
    return {
        "accepted": accepted,
        "decision_reason": decision_reason,
        "existing_quality": asdict(existing_quality),
        "candidate_quality": asdict(candidate_quality),
        "retention_metrics": asdict(retention_metrics),
        "existing_page_metrics": existing_page_metrics,
        "candidate_page_metrics": candidate_page_metrics,
        "page_drift_reason": drift_reason,
    }


def _context_snippet(page_row: Dict[str, Any]) -> str:
    page_number = _coerce_page_number(page_row)
    printed = page_row.get("printed_page_number")
    html = page_row.get("html") or page_row.get("raw_html") or ""
    snippet = html.strip()
    if len(snippet) > 1400:
        snippet = snippet[:1400].rstrip() + "\n..."
    return (
        f"Page {page_number}"
        f"{f' (printed {printed})' if printed is not None else ''}:\n"
        f"{snippet}"
    )


def build_user_text(
    target: RerunTarget,
    page_rows: Dict[int, Dict[str, Any]],
    *,
    max_context_chars: int,
) -> str:
    current_row = page_rows[target.page_number]
    current_html = (current_row.get("html") or current_row.get("raw_html") or "").strip()
    parts = [
        "Return HTML for the CURRENT target page image only.",
        "Use neighboring snippets only as a consistency hint. Do not copy rows that are not visible on the target page image.",
        f"Target page: {target.page_number}",
    ]
    if current_row.get("printed_page_number") is not None:
        parts.append(f"Printed page number: {current_row['printed_page_number']}")
    if target.chapter_basename:
        parts.append(f"Chapter artifact: {target.chapter_basename}")
    if target.chapter_title:
        parts.append(f"Chapter title: {target.chapter_title}")
    if target.schema_hint:
        parts.append(f"Frozen schema hint: {target.schema_hint}")
    if target.issue_reasons:
        parts.append(f"Consistency reasons: {', '.join(target.issue_reasons)}")

    parts.append("\nCurrent extracted HTML for the target page (may be structurally wrong):\n")
    parts.append(current_html[:max_context_chars])

    remaining = max(0, max_context_chars - len(current_html))
    if target.context_pages and remaining > 200:
        parts.append("\nNeighbor page context:\n")
        for page_number in target.context_pages:
            page_row = page_rows.get(page_number)
            if not page_row:
                continue
            snippet = _context_snippet(page_row)
            if len(snippet) > remaining:
                snippet = snippet[:remaining].rstrip() + "\n..."
            parts.append(snippet)
            remaining -= len(snippet)
            if remaining <= 0:
                break

    return "\n".join(parts)


def _build_prompt(extra_hints: Optional[str]) -> str:
    hints = RERUN_HINTS
    if extra_hints:
        hints += "\n" + extra_hints.strip()
    return build_system_prompt(hints)


def _report_path(base_out: str, raw_path: str) -> str:
    if os.path.isabs(raw_path) or os.path.sep in raw_path:
        candidate = Path(raw_path)
        if not candidate.is_absolute():
            candidate = (Path.cwd() / raw_path).resolve()
        return str(candidate)
    return str(Path(base_out).resolve().parent / raw_path)


def _apply_candidate(
    row: Dict[str, Any],
    raw_response: str,
    normalized_html: str,
    meta: Optional[Dict[str, Any]],
    meta_tag: Optional[str],
    meta_warning: Optional[str],
) -> None:
    meta = meta or {}
    if meta:
        row.update({key: value for key, value in meta.items() if value is not None})
    if meta_warning:
        row["ocr_metadata_warning"] = meta_warning
    if meta_tag and not all(value is not None for value in meta.values()):
        row["ocr_metadata_tag"] = meta_tag
    if not meta_tag:
        row["ocr_metadata_missing"] = True
    row["raw_html"] = raw_response
    row["html"] = normalized_html
    images = extract_image_metadata(normalized_html)
    if images:
        row["images"] = images


def _usage_to_dict(usage: Any) -> Any:
    if usage is None:
        return None
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    if hasattr(usage, "dict"):
        return usage.dict()
    if hasattr(usage, "__dict__"):
        return usage.__dict__
    return usage


def run_reruns(
    rows: List[Dict[str, Any]],
    page_rows: Dict[int, Dict[str, Any]],
    targets: List[RerunTarget],
    *,
    report_path: str,
    summary_path: str,
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
    report_rows: List[Dict[str, Any]] = []
    out_rows: List[Dict[str, Any]] = []

    logger = ProgressLogger(state_path=state_file, progress_path=progress_file, run_id=run_id)
    logger.log(
        "adapter",
        "running",
        current=0,
        total=max(1, len(target_map)),
        message="Running Onward genealogy source-aware reruns",
        artifact=out_path,
        module_id="rerun_onward_genealogy_consistency_v1",
        schema_version="page_html_v1",
        extra={"consistency_report": consistency_report_path},
    )

    processed_targets = 0
    accepted_count = 0
    rejection_reasons: Dict[str, int] = {}

    for row in rows:
        page_number = _coerce_page_number(row)
        new_row = deepcopy(row)
        new_row["module_id"] = "rerun_onward_genealogy_consistency_v1"
        if run_id:
            new_row["run_id"] = run_id
        new_row["created_at"] = _utc()
        target = target_map.get(page_number or -1)
        if target is None:
            out_rows.append(new_row)
            continue

        processed_targets += 1
        image_path = row.get("image")
        report_record: Dict[str, Any] = {
            "page_number": page_number,
            "chapter_basename": target.chapter_basename,
            "chapter_title": target.chapter_title,
            "schema_hint": target.schema_hint,
            "issue_reasons": target.issue_reasons,
            "source_pages": target.source_pages,
            "context_pages": target.context_pages,
            "source_image": image_path,
            "input_pages_artifact_path": pages_artifact_path,
            "output_pages_artifact_path": out_path,
            "consistency_report_artifact_path": consistency_report_path,
            "model": model,
            "existing_html": row.get("html") or row.get("raw_html") or "",
        }

        logger.log(
            "adapter",
            "running",
            current=processed_targets,
            total=max(1, len(target_map)),
            message=f"Rerunning genealogy page {page_number}",
            artifact=out_path,
            module_id="rerun_onward_genealogy_consistency_v1",
            schema_version="page_html_v1",
        )

        if not image_path or not os.path.exists(image_path):
            report_record.update({
                "targeted": True,
                "accepted": False,
                "decision_reason": "missing_image",
            })
            rejection_reasons["missing_image"] = rejection_reasons.get("missing_image", 0) + 1
            report_rows.append(report_record)
            out_rows.append(new_row)
            continue

        existing_html = row.get("html") or row.get("raw_html") or ""
        normalized_existing = _restore_subgroup_row_markers(_normalize_rescue_html(existing_html))
        report_record["normalized_existing_html"] = normalized_existing
        report_record["normalized_existing_changed"] = normalized_existing != existing_html
        if normalized_existing != existing_html:
            normalized_eval = _evaluate_candidate(
                existing_html,
                normalized_existing,
                min_score_gain=min_score_gain,
                min_token_recall=min_token_recall,
                min_text_ratio=min_text_ratio,
            )
            report_record.update({
                "normalized_existing_accepted": normalized_eval["accepted"],
                "normalized_existing_decision_reason": normalized_eval["decision_reason"],
                "normalized_existing_quality": normalized_eval["candidate_quality"],
                "normalized_existing_retention_metrics": normalized_eval["retention_metrics"],
                "normalized_existing_page_metrics": normalized_eval["candidate_page_metrics"],
            })
            if normalized_eval["accepted"]:
                accepted_count += 1
                new_row["html"] = normalized_existing
                report_record.update({
                    "targeted": True,
                    "accepted": True,
                    "decision_reason": "normalized_existing_accepted",
                    "request_id": None,
                    "usage": None,
                    "existing_quality": normalized_eval["existing_quality"],
                    "candidate_quality": normalized_eval["candidate_quality"],
                    "retention_metrics": normalized_eval["retention_metrics"],
                    "existing_page_metrics": normalized_eval["existing_page_metrics"],
                    "candidate_page_metrics": normalized_eval["candidate_page_metrics"],
                    "page_drift_reason": normalized_eval["page_drift_reason"],
                    "candidate_html": normalized_existing,
                    "final_html": new_row.get("html") or new_row.get("raw_html") or "",
                })
                report_rows.append(report_record)
                out_rows.append(new_row)
                continue

        image_data = _encode_image(image_path)
        user_text = build_user_text(target, page_rows, max_context_chars=max_context_chars)

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
        except Exception as exc:  # pragma: no cover - network/environment dependent
            report_record.update({
                "targeted": True,
                "accepted": False,
                "decision_reason": "ocr_error",
                "error": str(exc),
            })
            rejection_reasons["ocr_error"] = rejection_reasons.get("ocr_error", 0) + 1
            report_rows.append(report_record)
            out_rows.append(new_row)
            continue

        raw_response = _extract_code_fence(raw_response)
        cleaned_raw, meta, meta_tag, meta_warning = _extract_ocr_metadata(raw_response)
        normalized_candidate = _restore_subgroup_row_markers(
            _normalize_rescue_html(sanitize_html(cleaned_raw))
        )
        candidate_eval = _evaluate_candidate(
            existing_html,
            normalized_candidate,
            min_score_gain=min_score_gain,
            min_token_recall=min_token_recall,
            min_text_ratio=min_text_ratio,
        )
        accepted = candidate_eval["accepted"]
        if accepted:
            accepted_count += 1
            _apply_candidate(new_row, raw_response, normalized_candidate, meta, meta_tag, meta_warning)
            decision_reason = candidate_eval["decision_reason"]
        else:
            decision_reason = candidate_eval["decision_reason"]
            rejection_reasons[decision_reason] = rejection_reasons.get(decision_reason, 0) + 1

        report_record.update({
            "targeted": True,
            "accepted": accepted,
            "decision_reason": decision_reason,
            "request_id": request_id,
            "usage": _usage_to_dict(usage),
            "existing_quality": candidate_eval["existing_quality"],
            "candidate_quality": candidate_eval["candidate_quality"],
            "retention_metrics": candidate_eval["retention_metrics"],
            "existing_page_metrics": candidate_eval["existing_page_metrics"],
            "candidate_page_metrics": candidate_eval["candidate_page_metrics"],
            "page_drift_reason": candidate_eval["page_drift_reason"],
            "candidate_html": normalized_candidate,
            "final_html": new_row.get("html") or new_row.get("raw_html") or "",
        })
        report_rows.append(report_record)
        out_rows.append(new_row)

    summary = {
        "schema_version": "onward_genealogy_rerun_summary_v1",
        "module_id": "rerun_onward_genealogy_consistency_v1",
        "created_at": _utc(),
        "run_id": run_id,
        "input_pages_artifact_path": pages_artifact_path,
        "consistency_report_artifact_path": consistency_report_path,
        "output_pages_artifact_path": out_path,
        "targeted_page_count": len(target_map),
        "targeted_pages": sorted(target_map),
        "accepted_page_count": accepted_count,
        "rejected_page_count": len(target_map) - accepted_count,
        "rejection_reasons": rejection_reasons,
        "chapters": sorted({target.chapter_basename for target in targets}),
    }

    save_jsonl(out_path, out_rows)
    save_jsonl(report_path, report_rows)
    save_json(summary_path, summary)

    logger.log(
        "adapter",
        "done",
        current=len(target_map),
        total=max(1, len(target_map)),
        message=f"Onward genealogy reruns complete: accepted={accepted_count}/{len(target_map)}",
        artifact=out_path,
        module_id="rerun_onward_genealogy_consistency_v1",
        schema_version="page_html_v1",
        extra={"report": report_path, "summary_report": summary_path},
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Selective source-aware reruns for Onward genealogy consistency targets.")
    parser.add_argument("--pages", help="Input page_html_v1 JSONL")
    parser.add_argument("--consistency", help="pipeline_issues_v1 JSONL from validate_onward_genealogy_consistency_v1")
    parser.add_argument("--inputs", nargs="*", help="Driver compatibility: pages JSONL plus consistency JSONL")
    parser.add_argument("--out", required=True, help="Output page_html_v1 JSONL path")
    parser.add_argument("--report", default="rerun_onward_genealogy_report.jsonl")
    parser.add_argument("--summary-report", dest="summary_report", default="rerun_onward_genealogy_summary.json")
    parser.add_argument("--summary_report", dest="summary_report", default="rerun_onward_genealogy_summary.json")
    parser.add_argument("--model", default="gpt-5")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-output-tokens", dest="max_output_tokens", type=int, default=32768)
    parser.add_argument("--max_output_tokens", dest="max_output_tokens", type=int, default=32768)
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
    parser.add_argument("--rescue-hints", dest="rescue_hints", default=None)
    parser.add_argument("--rescue_hints", dest="rescue_hints", default=None)
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

    rows, page_rows = _load_pages(pages_path)
    targets = load_targets(
        consistency_path,
        target_mode=args.target_mode,
        page_context_window=args.page_context_window,
        chapter_allowlist=_parse_csv_strings(args.chapter_allowlist),
        page_allowlist=_parse_csv_ints(args.page_allowlist),
        max_pages=args.max_pages,
    )
    prompt = _build_prompt(args.rescue_hints)

    run_reruns(
        rows,
        page_rows,
        targets,
        report_path=report_path,
        summary_path=summary_path,
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
