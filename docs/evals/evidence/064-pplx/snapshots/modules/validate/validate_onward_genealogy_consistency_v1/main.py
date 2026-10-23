#!/usr/bin/env python3
"""
Read-only consistency report for Onward genealogy chapters.

The detector scores structural drift on final chapter HTML first, then narrows
flagged chapters back to source page HTML so later stories can target reruns.
"""
import argparse
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from bs4 import BeautifulSoup

from modules.common.utils import ProgressLogger, ensure_dir, read_jsonl, save_json, save_jsonl


EXPECTED_HEADERS = ("name", "born", "married", "spouse", "boy", "girl", "died")
GENEALOGY_SIGNATURES = {
    EXPECTED_HEADERS,
    ("name", "born", "married", "spouse", "boygirl", "died"),
}
CHAPTER_BASENAME_RE = re.compile(r"chapter-(\d+)\.html$", re.IGNORECASE)
FAMILY_HEADING_RE = re.compile(r"\b[A-Z][A-Z'’\-]+(?:\s+[A-Z][A-Z'’\-]+)*\s+FAMILY\b")
GENERATION_CONTEXT_RE = re.compile(r"\b(?:great\s+grandchildren|grandchildren|children)\b", re.IGNORECASE)


@dataclass
class ChapterMetrics:
    chapter_file: str
    chapter_basename: str
    chapter_number: Optional[int]
    chapter_title: str
    source_pages: List[int]
    source_printed_pages: List[int]
    source_page_count: int
    genealogy_table_count: int
    all_table_count: int
    subgroup_row_count: int
    external_family_heading_count: int
    residual_boygirl_header_count: int
    dominant_signature: Optional[str]
    signatures: List[str]
    drift_score: int
    confidence: float
    reasons: List[str]
    flagged: bool


@dataclass
class PageMetrics:
    page_number: Optional[int]
    printed_page_number: Optional[int]
    table_count: int
    subgroup_row_count: int
    external_family_heading_count: int
    residual_boygirl_header_count: int
    coarse_suspect: bool
    strong_rerun_candidate: bool
    reasons: List[str]


def _utc() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _normalize_token(text: str) -> str:
    return re.sub(r"[^a-z]", "", (text or "").lower())


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").replace("’", "'")).strip()


def _table_signature(table: Any) -> Optional[Tuple[str, ...]]:
    header_cells: List[str] = []
    thead = table.find("thead")
    if thead:
        header_cells = [cell.get_text(" ", strip=True) for cell in thead.find_all(["th", "td"])]
    if not header_cells:
        first_row = table.find("tr")
        if first_row:
            header_cells = [cell.get_text(" ", strip=True) for cell in first_row.find_all(["th", "td"])]
    normalized = tuple(token for token in (_normalize_token(cell) for cell in header_cells) if token)
    if normalized in GENEALOGY_SIGNATURES:
        return normalized
    return None


def _heading_has_genealogy_drift(text: str) -> bool:
    normalized = _normalize_text(text)
    if not normalized:
        return False
    return bool(FAMILY_HEADING_RE.search(normalized.upper()) or GENERATION_CONTEXT_RE.search(normalized))


def _chapter_number_from_path(path: str) -> Optional[int]:
    match = CHAPTER_BASENAME_RE.search(os.path.basename(path or ""))
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def _score_chapter(
    source_page_count: int,
    genealogy_table_count: int,
    subgroup_row_count: int,
    external_family_heading_count: int,
    residual_boygirl_header_count: int,
    flag_threshold: int,
) -> Tuple[int, List[str], bool, float]:
    reasons: List[str] = []
    score = 0

    if residual_boygirl_header_count > 0:
        score += 35 if residual_boygirl_header_count > 1 else 25
        reasons.append("residual_boygirl_headers")

    page_count = max(1, source_page_count)
    table_density = genealogy_table_count / page_count
    if genealogy_table_count >= 5 and table_density >= 1.25:
        score += 20
        reasons.append("fragmented_table_density")

    if genealogy_table_count >= 3 and subgroup_row_count == 0:
        score += 20
        reasons.append("missing_subgroup_rows")

    flagged = score >= flag_threshold
    confidence = min(0.99, round(0.50 + (score / 100.0), 2))
    return score, reasons, flagged, confidence


def analyze_chapter_row(manifest_row: Dict[str, Any], flag_threshold: int) -> Optional[ChapterMetrics]:
    if manifest_row.get("kind") != "chapter":
        return None
    chapter_file = manifest_row.get("file")
    if not chapter_file or not os.path.exists(chapter_file):
        return None

    html = Path(chapter_file).read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    signatures = [sig for sig in (_table_signature(table) for table in tables) if sig]
    if not signatures:
        return None

    subgroup_row_count = len(soup.select("tr.genealogy-subgroup-heading"))
    external_family_heading_count = sum(
        1 for heading in soup.find_all(["h2", "h3"]) if _heading_has_genealogy_drift(heading.get_text("\n", strip=True))
    )
    residual_boygirl_header_count = sum(
        1
        for cell in soup.find_all("th")
        if "BOY/GIRL" in cell.get_text(" ", strip=True).upper()
    )

    signature_counter = Counter("|".join(sig) for sig in signatures)
    dominant_signature = signature_counter.most_common(1)[0][0] if signature_counter else None
    source_pages = [int(page) for page in (manifest_row.get("source_pages") or [])]
    source_printed_pages = [int(page) for page in (manifest_row.get("source_printed_pages") or [])]
    drift_score, reasons, flagged, confidence = _score_chapter(
        source_page_count=len(source_pages),
        genealogy_table_count=len(signatures),
        subgroup_row_count=subgroup_row_count,
        external_family_heading_count=external_family_heading_count,
        residual_boygirl_header_count=residual_boygirl_header_count,
        flag_threshold=flag_threshold,
    )

    return ChapterMetrics(
        chapter_file=chapter_file,
        chapter_basename=os.path.basename(chapter_file),
        chapter_number=_chapter_number_from_path(chapter_file),
        chapter_title=manifest_row.get("title") or "",
        source_pages=source_pages,
        source_printed_pages=source_printed_pages,
        source_page_count=len(source_pages),
        genealogy_table_count=len(signatures),
        all_table_count=len(tables),
        subgroup_row_count=subgroup_row_count,
        external_family_heading_count=external_family_heading_count,
        residual_boygirl_header_count=residual_boygirl_header_count,
        dominant_signature=dominant_signature,
        signatures=sorted(signature_counter),
        drift_score=drift_score,
        confidence=confidence,
        reasons=reasons,
        flagged=flagged,
    )


def analyze_page_row(page_row: Dict[str, Any]) -> PageMetrics:
    html = page_row.get("html") or page_row.get("raw_html") or ""
    soup = BeautifulSoup(html, "html.parser")
    table_count = len(soup.find_all("table"))
    subgroup_row_count = len(soup.select("tr.genealogy-subgroup-heading"))
    external_family_heading_count = sum(
        1 for heading in soup.find_all(["h2", "h3"]) if _heading_has_genealogy_drift(heading.get_text("\n", strip=True))
    )
    residual_boygirl_header_count = sum(
        1
        for cell in soup.find_all("th")
        if "BOY/GIRL" in cell.get_text(" ", strip=True).upper()
    )

    reasons: List[str] = []
    if residual_boygirl_header_count > 0:
        reasons.append("residual_boygirl_headers")
    if table_count >= 2 and subgroup_row_count == 0:
        reasons.append("fragmented_multi_table_page")

    strong_rerun_candidate = "fragmented_multi_table_page" in reasons
    coarse_suspect = strong_rerun_candidate or "residual_boygirl_headers" in reasons

    return PageMetrics(
        page_number=page_row.get("page_number"),
        printed_page_number=page_row.get("printed_page_number"),
        table_count=table_count,
        subgroup_row_count=subgroup_row_count,
        external_family_heading_count=external_family_heading_count,
        residual_boygirl_header_count=residual_boygirl_header_count,
        coarse_suspect=coarse_suspect,
        strong_rerun_candidate=strong_rerun_candidate,
        reasons=reasons,
    )


def _load_page_rows(path: str) -> Dict[int, Dict[str, Any]]:
    page_rows: Dict[int, Dict[str, Any]] = {}
    for row in read_jsonl(path):
        page_number = row.get("page_number")
        try:
            page_rows[int(page_number)] = row
        except (TypeError, ValueError):
            continue
    return page_rows


def _load_optional_jsonl(path: Optional[str]) -> List[Dict[str, Any]]:
    if not path or not os.path.exists(path):
        return []
    return list(read_jsonl(path))


def _chapter_structure_snapshot(html_path: str) -> Optional[Dict[str, Any]]:
    if not html_path or not os.path.exists(html_path):
        return None
    soup = BeautifulSoup(Path(html_path).read_text(encoding="utf-8"), "html.parser")
    title_tag = soup.find("h1")
    return {
        "title": title_tag.get_text(" ", strip=True) if title_tag else "",
        "table_count": len(soup.find_all("table")),
        "h2_count": len(soup.find_all("h2")),
        "h3_count": len(soup.find_all("h3")),
    }


def _chapter_structure_text(html_path: str) -> str:
    if not html_path or not os.path.exists(html_path):
        return ""
    soup = BeautifulSoup(Path(html_path).read_text(encoding="utf-8"), "html.parser")
    article = soup.find("article") or soup
    return _normalize_text(article.get_text(" ", strip=True))


def _structure_text_similarity(current_path: str, golden_path: str) -> Optional[float]:
    current_text = _chapter_structure_text(current_path)
    golden_text = _chapter_structure_text(golden_path)
    if not current_text or not golden_text:
        return None
    sequence_ratio = SequenceMatcher(a=current_text, b=golden_text).ratio()
    current_tokens = set(current_text.split())
    golden_tokens = set(golden_text.split())
    token_overlap = 0.0
    if current_tokens and golden_tokens:
        token_overlap = len(current_tokens & golden_tokens) / max(len(current_tokens), len(golden_tokens))
    return round(max(sequence_ratio, token_overlap), 4)


def _should_accept_simplified_reviewed_shape(
    reasons: List[str],
    *,
    text_similarity: Optional[float],
) -> bool:
    if not reasons or text_similarity is None or text_similarity < 0.98:
        return False
    return all(reason.startswith("fewer_") for reason in reasons)


def _load_reviewed_golden_snapshots(golden_dir: Optional[str]) -> Dict[str, Dict[str, Any]]:
    if not golden_dir or not os.path.isdir(golden_dir):
        return {}
    snapshots: Dict[str, Dict[str, Any]] = {}
    for path in sorted(Path(golden_dir).glob("chapter-*.html")):
        snapshot = _chapter_structure_snapshot(str(path))
        if not snapshot or not snapshot["title"]:
            continue
        snapshot["html_path"] = str(path)
        snapshots[snapshot["title"]] = snapshot
    return snapshots


def _load_reviewed_golden_focus_pages(golden_dir: Optional[str]) -> Dict[str, List[int]]:
    if not golden_dir or not os.path.isdir(golden_dir):
        return {}

    manifest_path = Path(golden_dir) / "manifest.json"
    provenance_path = Path(golden_dir) / "provenance" / "blocks.jsonl"
    if not manifest_path.exists() or not provenance_path.exists():
        return {}

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    title_by_entry: Dict[str, str] = {}
    for entry in manifest.get("entries") or []:
        title = str(entry.get("title") or "").strip()
        if not title:
            continue
        entry_id = str(entry.get("entry_id") or "").strip()
        if entry_id:
            title_by_entry[entry_id] = title
        entry_path = str(entry.get("path") or "").strip()
        if entry_path:
            title_by_entry[Path(entry_path).stem] = title

    counts_by_title: Dict[str, Dict[int, Counter[str]]] = defaultdict(lambda: defaultdict(Counter))
    for row in read_jsonl(str(provenance_path)):
        entry_id = str(row.get("entry_id") or "").strip()
        chapter_title = title_by_entry.get(entry_id)
        if not chapter_title:
            continue
        try:
            source_page_number = int(row.get("source_page_number"))
        except (TypeError, ValueError):
            continue
        block_kind = str(row.get("block_kind") or "").strip()
        if block_kind not in {"heading", "table"}:
            continue
        counts_by_title[chapter_title][source_page_number][block_kind] += 1

    focus_pages_by_title: Dict[str, List[int]] = {}
    for chapter_title, page_counts in counts_by_title.items():
        focus_pages = [
            page_number
            for page_number, counts in sorted(page_counts.items())
            if counts["table"] > 1 or counts["heading"] > 1
        ]
        if not focus_pages:
            focus_pages = [
                page_number
                for page_number, counts in sorted(page_counts.items())
                if counts["table"] > 0 and counts["heading"] > 0 and (counts["table"] + counts["heading"]) >= 3
            ]
        if focus_pages:
            focus_pages_by_title[chapter_title] = focus_pages

    return focus_pages_by_title


def _group_runs(chapters: Iterable[ChapterMetrics]) -> List[Dict[str, Any]]:
    grouped: Dict[str, List[ChapterMetrics]] = {}
    for chapter in chapters:
        signature = chapter.dominant_signature or "unknown"
        grouped.setdefault(signature, []).append(chapter)

    runs: List[Dict[str, Any]] = []
    for signature, members in sorted(grouped.items(), key=lambda item: item[0]):
        members_sorted = sorted(members, key=lambda chapter: (chapter.chapter_number or 0, chapter.chapter_basename))
        baseline = min(members_sorted, key=lambda chapter: (chapter.drift_score, chapter.chapter_number or 0))
        runs.append(
            {
                "run_id": f"onward-genealogy::{signature}",
                "schema_hint": signature,
                "chapter_count": len(members_sorted),
                "baseline_chapter": baseline.chapter_basename,
                "baseline_score": baseline.drift_score,
                "members": [chapter.chapter_basename for chapter in members_sorted],
                "flagged_members": [chapter.chapter_basename for chapter in members_sorted if chapter.flagged],
            }
        )
    return runs


def _issue_for_chapter(run_lookup: Dict[str, Dict[str, Any]], chapter: ChapterMetrics, detail: Dict[str, Any]) -> Dict[str, Any]:
    run_id = detail["run_id"]
    run = run_lookup[run_id]
    return {
        "type": "onward_genealogy_consistency_drift",
        "severity": "warning",
        "chapter_file": chapter.chapter_file,
        "chapter_basename": chapter.chapter_basename,
        "chapter_title": chapter.chapter_title,
        "run_id": run_id,
        "schema_hint": run["schema_hint"],
        "drift_score": chapter.drift_score,
        "confidence": chapter.confidence,
        "reasons": chapter.reasons,
        "source_pages": chapter.source_pages,
        "coarse_suspect_pages": detail["coarse_suspect_pages"],
        "strong_rerun_candidate_pages": detail["strong_rerun_candidate_pages"],
    }


def _issue_for_reviewed_golden_regression(
    chapter: ChapterMetrics,
    current_snapshot: Dict[str, Any],
    golden_snapshot: Dict[str, Any],
    reasons: List[str],
    *,
    coarse_suspect_pages: List[int],
    strong_rerun_candidate_pages: List[int],
    target_selection_basis: str,
) -> Dict[str, Any]:
    return {
        "type": "onward_reviewed_golden_structure_regression",
        "severity": "warning",
        "chapter_file": chapter.chapter_file,
        "chapter_basename": chapter.chapter_basename,
        "chapter_title": chapter.chapter_title,
        "schema_hint": chapter.dominant_signature or "",
        "reasons": reasons,
        "source_pages": chapter.source_pages,
        "coarse_suspect_pages": coarse_suspect_pages,
        "strong_rerun_candidate_pages": strong_rerun_candidate_pages,
        "target_selection_basis": target_selection_basis,
        "current_table_count": current_snapshot["table_count"],
        "golden_table_count": golden_snapshot["table_count"],
        "current_h2_count": current_snapshot["h2_count"],
        "golden_h2_count": golden_snapshot["h2_count"],
        "current_h3_count": current_snapshot["h3_count"],
        "golden_h3_count": golden_snapshot["h3_count"],
    }


def _issue_for_duplicate_portion_page_start(
    page_start: int,
    titles: List[str],
    portions_path: str,
) -> Dict[str, Any]:
    return {
        "type": "onward_duplicate_portion_page_start",
        "severity": "warning",
        "page_start": page_start,
        "portion_titles": titles,
        "artifact_path": portions_path,
    }


def build_report(
    manifest_rows: List[Dict[str, Any]],
    page_rows_by_number: Dict[int, Dict[str, Any]],
    *,
    chapters_path: str,
    pages_path: str,
    portions_path: Optional[str],
    reviewed_golden_dir: Optional[str],
    flag_threshold: int,
    warning_band: float,
    redesign_band: float,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    chapter_metrics = [metric for metric in (analyze_chapter_row(row, flag_threshold) for row in manifest_rows) if metric]
    portions_rows = _load_optional_jsonl(portions_path)
    reviewed_golden_snapshots = _load_reviewed_golden_snapshots(reviewed_golden_dir)
    reviewed_golden_focus_pages = _load_reviewed_golden_focus_pages(reviewed_golden_dir)
    run_summaries = _group_runs(chapter_metrics)
    run_lookup = {run["run_id"]: run for run in run_summaries}
    run_id_by_chapter = {
        chapter_basename: run["run_id"]
        for run in run_summaries
        for chapter_basename in run["members"]
    }

    chapter_details: List[Dict[str, Any]] = []
    issues: List[Dict[str, Any]] = []
    total_candidate_pages = sum(chapter.source_page_count for chapter in chapter_metrics)
    total_flagged_pages = 0
    total_coarse_pages = 0
    total_strong_pages = 0
    reviewed_golden_details: List[Dict[str, Any]] = []

    for chapter in sorted(chapter_metrics, key=lambda item: (item.chapter_number or 0, item.chapter_basename)):
        source_page_details: List[Dict[str, Any]] = []
        coarse_pages: List[int] = []
        strong_pages: List[int] = []
        golden_snapshot = reviewed_golden_snapshots.get(chapter.chapter_title)
        if chapter.flagged or golden_snapshot is not None:
            for page_number in chapter.source_pages:
                page_row = page_rows_by_number.get(page_number)
                if not page_row:
                    continue
                page_metrics = analyze_page_row(page_row)
                if page_metrics.coarse_suspect:
                    coarse_pages.append(page_number)
                if page_metrics.strong_rerun_candidate:
                    strong_pages.append(page_number)
                source_page_details.append(
                    {
                        "page_number": page_number,
                        "printed_page_number": page_metrics.printed_page_number,
                        "artifact_path": pages_path,
                        "metrics": asdict(page_metrics),
                    }
                )

        if chapter.flagged:
            total_flagged_pages += chapter.source_page_count
            total_coarse_pages += len(coarse_pages)
            total_strong_pages += len(strong_pages)

        detail = {
            **asdict(chapter),
            "run_id": run_id_by_chapter.get(chapter.chapter_basename, "onward-genealogy::unknown"),
            "chapter_artifact_path": chapter.chapter_file,
            "source_pages_artifact_path": pages_path,
            "coarse_suspect_pages": coarse_pages,
            "strong_rerun_candidate_pages": strong_pages,
            "source_page_details": source_page_details,
        }
        chapter_details.append(detail)
        if chapter.flagged:
            issues.append(_issue_for_chapter(run_lookup, chapter, detail))

        if golden_snapshot:
            current_snapshot = _chapter_structure_snapshot(chapter.chapter_file)
            reasons: List[str] = []
            reviewed_text_similarity = None
            if current_snapshot is not None:
                if current_snapshot["table_count"] < golden_snapshot["table_count"]:
                    reasons.append("fewer_tables_than_reviewed_golden")
                if current_snapshot["table_count"] > golden_snapshot["table_count"]:
                    reasons.append("more_tables_than_reviewed_golden")
                if current_snapshot["h2_count"] < golden_snapshot["h2_count"]:
                    reasons.append("fewer_h2_than_reviewed_golden")
                if current_snapshot["h2_count"] > golden_snapshot["h2_count"]:
                    reasons.append("more_h2_than_reviewed_golden")
                if current_snapshot["h3_count"] < golden_snapshot["h3_count"]:
                    reasons.append("fewer_h3_than_reviewed_golden")
                if current_snapshot["h3_count"] > golden_snapshot["h3_count"]:
                    reasons.append("more_h3_than_reviewed_golden")
                reviewed_text_similarity = _structure_text_similarity(
                    chapter.chapter_file,
                    golden_snapshot.get("html_path") or "",
                )
                if _should_accept_simplified_reviewed_shape(
                    reasons,
                    text_similarity=reviewed_text_similarity,
                ):
                    reasons = []
            golden_focus_pages = [
                page_number
                for page_number in reviewed_golden_focus_pages.get(chapter.chapter_title, [])
                if page_number in chapter.source_pages
            ]
            rerun_pages = golden_focus_pages or coarse_pages
            strong_rerun_pages = golden_focus_pages or strong_pages or rerun_pages
            reviewed_detail = {
                "chapter_title": chapter.chapter_title,
                "chapter_file": chapter.chapter_file,
                "golden_dir": reviewed_golden_dir,
                "current": current_snapshot,
                "golden": golden_snapshot,
                "reasons": reasons,
                "flagged": bool(reasons),
                "reviewed_text_similarity": reviewed_text_similarity,
                "source_pages": chapter.source_pages,
                "coarse_suspect_pages": rerun_pages,
                "strong_rerun_candidate_pages": strong_rerun_pages,
                "target_selection_basis": (
                    "reviewed_golden_provenance_focus_pages"
                    if golden_focus_pages
                    else "current_page_signals_fallback"
                ),
            }
            reviewed_golden_details.append(reviewed_detail)
            if reasons and current_snapshot is not None:
                issues.append(
                    _issue_for_reviewed_golden_regression(
                        chapter,
                        current_snapshot,
                        golden_snapshot,
                        reasons,
                        coarse_suspect_pages=rerun_pages,
                        strong_rerun_candidate_pages=strong_rerun_pages,
                        target_selection_basis=reviewed_detail["target_selection_basis"],
                    )
                )

    duplicate_portion_page_starts: List[Dict[str, Any]] = []
    if portions_rows and portions_path:
        titles_by_start: Dict[int, List[str]] = defaultdict(list)
        for row in portions_rows:
            page_start = row.get("page_start")
            if isinstance(page_start, int):
                titles_by_start[page_start].append(row.get("title") or row.get("portion_id") or "")
        for page_start, titles in sorted(titles_by_start.items()):
            if len(titles) <= 1:
                continue
            duplicate_portion_page_starts.append(
                {
                    "page_start": page_start,
                    "titles": titles,
                    "count": len(titles),
                }
            )
            issues.append(_issue_for_duplicate_portion_page_start(page_start, titles, portions_path))

    flagged_chapter_count = sum(1 for chapter in chapter_metrics if chapter.flagged)
    reviewed_golden_flagged = [detail for detail in reviewed_golden_details if detail["flagged"]]
    strong_coverage = (total_strong_pages / total_flagged_pages) if total_flagged_pages else 0.0
    coarse_coverage = (total_coarse_pages / total_flagged_pages) if total_flagged_pages else 0.0
    candidate_coverage = (total_strong_pages / total_candidate_pages) if total_candidate_pages else 0.0

    if duplicate_portion_page_starts:
        recommendation = "portion_replay_regression_detected"
    elif reviewed_golden_flagged:
        recommendation = "reviewed_golden_structure_regression"
    elif strong_coverage >= redesign_band:
        recommendation = "broader_extraction_granularity"
    elif strong_coverage >= warning_band:
        recommendation = "targeted_reruns_warning_band"
    else:
        recommendation = "targeted_reruns_justified"

    summary = {
        "chapters_artifact": chapters_path,
        "pages_artifact": pages_path,
        "candidate_genealogy_chapters": len(chapter_metrics),
        "flagged_genealogy_chapters": flagged_chapter_count,
        "flagged_chapters": [chapter["chapter_basename"] for chapter in chapter_details if chapter["flagged"]],
        "run_count": len(run_summaries),
        "flag_threshold": flag_threshold,
        "warning_band": warning_band,
        "redesign_band": redesign_band,
        "flagged_chapter_page_count": total_flagged_pages,
        "coarse_suspect_page_count": total_coarse_pages,
        "strong_rerun_candidate_page_count": total_strong_pages,
        "coarse_suspect_page_coverage": round(coarse_coverage, 4),
        "strong_rerun_candidate_page_coverage": round(strong_coverage, 4),
        "candidate_genealogy_page_coverage": round(candidate_coverage, 4),
        "duplicate_portion_page_start_count": len(duplicate_portion_page_starts),
        "duplicate_portion_page_starts": [detail["page_start"] for detail in duplicate_portion_page_starts],
        "reviewed_golden_chapter_count": len(reviewed_golden_details),
        "reviewed_golden_flagged_chapter_count": len(reviewed_golden_flagged),
        "reviewed_golden_flagged_chapters": [detail["chapter_title"] for detail in reviewed_golden_flagged],
        "recommendation": recommendation,
    }

    primary_report = {
        "schema_version": "pipeline_issues_v1",
        "module_id": "validate_onward_genealogy_consistency_v1",
        "created_at": _utc(),
        "summary": summary,
        "issues": issues,
    }
    detail_report = {
        "schema_version": "onward_genealogy_consistency_report_v1",
        "created_at": _utc(),
        "summary": summary,
        "runs": run_summaries,
        "chapters": chapter_details,
        "duplicate_portion_page_starts": duplicate_portion_page_starts,
        "reviewed_golden_comparisons": reviewed_golden_details,
    }
    return primary_report, detail_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate structural consistency of Onward genealogy chapters.")
    parser.add_argument("--chapters", required=True, help="chapters_manifest.jsonl from build_chapter_html_v1")
    parser.add_argument("--pages", required=True, help="page_html_v1 JSONL used to build the chapters")
    parser.add_argument("--portions", help="Optional portion_hyp_v1 JSONL for duplicate page-start checks")
    parser.add_argument("--out", required=True, help="Output JSONL path for pipeline_issues_v1 summary")
    parser.add_argument("--detail-report", dest="detail_report", default="genealogy_consistency_detail.json")
    parser.add_argument("--detail_report", dest="detail_report", default="genealogy_consistency_detail.json")
    parser.add_argument(
        "--reviewed-golden-dir",
        dest="reviewed_golden_dir",
        default="benchmarks/golden/onward/dossier-doc-web-handoff-v1",
        help="Optional reviewed-golden HTML directory to compare against by chapter title",
    )
    parser.add_argument(
        "--reviewed_golden_dir",
        dest="reviewed_golden_dir",
        default="benchmarks/golden/onward/dossier-doc-web-handoff-v1",
    )
    parser.add_argument("--flag-threshold", dest="flag_threshold", type=int, default=25)
    parser.add_argument("--flag_threshold", dest="flag_threshold", type=int, default=25)
    parser.add_argument("--warning-band", dest="warning_band", type=float, default=0.25)
    parser.add_argument("--warning_band", dest="warning_band", type=float, default=0.25)
    parser.add_argument("--redesign-band", dest="redesign_band", type=float, default=0.30)
    parser.add_argument("--redesign_band", dest="redesign_band", type=float, default=0.30)
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
    detail_path = args.detail_report
    if not os.path.isabs(detail_path):
        detail_path = os.path.join(os.path.dirname(out_path), detail_path)

    logger = ProgressLogger(state_path=args.state_file, progress_path=args.progress_file, run_id=args.run_id)
    logger.log(
        "validate",
        "running",
        current=0,
        total=1,
        message="Scoring Onward genealogy consistency",
        artifact=out_path,
        module_id="validate_onward_genealogy_consistency_v1",
        schema_version="pipeline_issues_v1",
    )

    manifest_rows = list(read_jsonl(args.chapters))
    page_rows_by_number = _load_page_rows(args.pages)
    primary_report, detail_report = build_report(
        manifest_rows,
        page_rows_by_number,
        chapters_path=args.chapters,
        pages_path=args.pages,
        portions_path=args.portions,
        reviewed_golden_dir=args.reviewed_golden_dir,
        flag_threshold=args.flag_threshold,
        warning_band=args.warning_band,
        redesign_band=args.redesign_band,
    )

    if args.run_id:
        primary_report["run_id"] = args.run_id

    save_jsonl(out_path, [primary_report])
    save_json(detail_path, detail_report)

    logger.log(
        "validate",
        "done",
        current=1,
        total=1,
        message=(
            f"Onward genealogy consistency report complete: "
            f"flagged={primary_report['summary']['flagged_genealogy_chapters']}, "
            f"golden_flags={primary_report['summary']['reviewed_golden_flagged_chapter_count']}, "
            f"duplicate_portion_starts={primary_report['summary']['duplicate_portion_page_start_count']}"
        ),
        artifact=out_path,
        module_id="validate_onward_genealogy_consistency_v1",
        schema_version="pipeline_issues_v1",
        extra={"detail_report": detail_path},
    )


if __name__ == "__main__":
    main()
