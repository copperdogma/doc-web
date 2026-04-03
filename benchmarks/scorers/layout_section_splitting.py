from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text:
            continue
        rows.append(json.loads(text))
    return rows


def _bundle_paths(bundle_dir: str | Path) -> tuple[Path, Path]:
    bundle_root = Path(bundle_dir)
    return bundle_root / "manifest.json", bundle_root / "provenance" / "blocks.jsonl"


def score_bundle_case(expected: dict[str, Any], bundle_dir: str | Path) -> dict[str, Any]:
    manifest_path, provenance_path = _bundle_paths(bundle_dir)
    checks: dict[str, bool] = {
        "manifest_exists": manifest_path.exists(),
        "provenance_exists": provenance_path.exists(),
    }
    details: dict[str, Any] = {
        "bundle_dir": str(Path(bundle_dir)),
        "html_assertions": [],
        "provenance_assertions": [],
    }

    if not all(checks.values()):
        passed_checks = sum(1 for value in checks.values() if value)
        total_checks = len(checks) or 1
        return {
            "pass": False,
            "score": passed_checks / total_checks,
            "checks": checks,
            "details": details,
            "actual": {},
        }

    manifest = _load_json(manifest_path)
    provenance_rows = _load_jsonl(provenance_path)
    entries = manifest.get("entries") or []
    entry_titles = [entry.get("title") for entry in entries]
    title_to_entry = {entry.get("title"): entry for entry in entries if entry.get("title")}
    expected_titles = expected.get("expected_entry_titles") or []

    checks["entry_count"] = len(entries) == len(expected_titles)
    checks["entry_titles"] = entry_titles == expected_titles
    checks["reading_order"] = (manifest.get("reading_order") or []) == [
        entry.get("entry_id") for entry in entries
    ]
    checks["provenance_source_ids_present"] = bool(provenance_rows) and all(
        row.get("source_element_ids") for row in provenance_rows
    )

    if expected.get("expected_manifest_title") is not None:
        checks["manifest_title"] = manifest.get("title") == expected.get("expected_manifest_title")

    provenance_mode = expected.get("provenance_mode")
    if provenance_mode == "pageless":
        checks["manifest_source_pages_pageless"] = all(not entry.get("source_pages") for entry in entries)
        checks["provenance_source_page_numbers_absent"] = all(
            row.get("source_page_number") in (None, "") for row in provenance_rows
        )
    elif provenance_mode == "paged":
        checks["manifest_source_pages_present"] = all(entry.get("source_pages") for entry in entries)
        checks["provenance_source_page_numbers_present"] = bool(provenance_rows) and all(
            row.get("source_page_number") not in (None, "") for row in provenance_rows
        )

    html_results: list[dict[str, Any]] = []
    for assertion in expected.get("html_assertions") or []:
        entry = title_to_entry.get(assertion["entry_title"])
        html_path = None if entry is None else Path(bundle_dir) / str(entry.get("path"))
        html = "" if html_path is None or not html_path.exists() else html_path.read_text(encoding="utf-8")
        missing = [snippet for snippet in assertion.get("snippets") or [] if snippet not in html]
        html_results.append(
            {
                "entry_title": assertion["entry_title"],
                "path": None if html_path is None else str(html_path),
                "missing_snippets": missing,
                "pass": not missing and html_path is not None and html_path.exists(),
            }
        )
    details["html_assertions"] = html_results
    checks["html_assertions"] = all(result["pass"] for result in html_results)

    provenance_results: list[dict[str, Any]] = []
    for assertion in expected.get("provenance_assertions") or []:
        entry_id = assertion.get("entry_id")
        entry_title = assertion.get("entry_title")
        if entry_id is None and entry_title is not None:
            entry = title_to_entry.get(entry_title)
            entry_id = None if entry is None else entry.get("entry_id")
        matched_row = None
        for row in provenance_rows:
            if entry_id is not None and row.get("entry_id") != entry_id:
                continue
            if assertion.get("block_kind") and row.get("block_kind") != assertion.get("block_kind"):
                continue
            if assertion.get("source_page_number") is not None and row.get("source_page_number") != assertion.get("source_page_number"):
                continue
            quote = row.get("text_quote") or ""
            if assertion.get("text_quote_contains") and assertion["text_quote_contains"] not in quote:
                continue
            prefix = assertion.get("source_element_prefix")
            if prefix:
                ids = row.get("source_element_ids") or []
                if not any(str(source_id).startswith(prefix) for source_id in ids):
                    continue
            matched_row = row
            break
        provenance_results.append(
            {
                "entry_title": entry_title,
                "entry_id": entry_id,
                "block_kind": assertion.get("block_kind"),
                "text_quote_contains": assertion.get("text_quote_contains"),
                "source_page_number": assertion.get("source_page_number"),
                "source_element_prefix": assertion.get("source_element_prefix"),
                "pass": matched_row is not None,
                "matched_row": matched_row,
            }
        )
    details["provenance_assertions"] = provenance_results
    checks["provenance_assertions"] = all(result["pass"] for result in provenance_results)

    passed_checks = sum(1 for value in checks.values() if value)
    total_checks = len(checks) or 1
    return {
        "pass": passed_checks == total_checks,
        "score": passed_checks / total_checks,
        "checks": checks,
        "details": details,
        "actual": {
            "entry_titles": entry_titles,
            "entry_count": len(entries),
            "manifest_title": manifest.get("title"),
            "provenance_row_count": len(provenance_rows),
        },
    }


def score_docx_single_entry_challenger(expected: dict[str, Any], elements_path: str | Path) -> dict[str, Any]:
    rows = _load_jsonl(elements_path)
    title_rows = [row for row in rows if row.get("type") == "Title"]
    top_level_titles = [
        row.get("text")
        for row in title_rows
        if (row.get("metadata") or {}).get("category_depth", 0) == 0
    ]
    expected_manifest_title = expected.get("expected_manifest_title")
    content_titles = [title for title in top_level_titles if title and title != expected_manifest_title]
    predicted_titles = content_titles[:1] if content_titles else top_level_titles[:1]
    expected_titles = expected.get("expected_entry_titles") or []
    checks = {
        "source_rows_present": bool(rows),
        "first_section_title_match": bool(predicted_titles) and bool(expected_titles) and predicted_titles[0] == expected_titles[0],
        "all_expected_sections_present": predicted_titles == expected_titles,
        "accepted_final_surface": False,
    }
    passed_checks = sum(1 for value in checks.values() if value)
    total_checks = len(checks) or 1
    return {
        "pass": False,
        "score": passed_checks / total_checks,
        "checks": checks,
        "actual": {
            "predicted_entry_titles": predicted_titles,
            "top_level_titles": content_titles,
            "row_count": len(rows),
        },
        "honest_competitor": False,
        "competitor_reason": "Derived single-entry baseline is not an accepted final bundle surface and misses expected splits.",
    }


def score_case_challenger(case: dict[str, Any], run_dir: str | Path) -> dict[str, Any] | None:
    challenger = case.get("challenger") or {}
    kind = challenger.get("kind")
    if not kind:
        return None
    run_root = Path(run_dir)
    if kind == "extract_stage_doc_web_bundle":
        bundle_dir = run_root / str(challenger["bundle_subdir"])
        result = score_bundle_case(case, bundle_dir)
        result["honest_competitor"] = result["pass"]
        result["competitor_reason"] = (
            "Extract-stage direct emitter clears the same bounded benchmark."
            if result["pass"]
            else "Extract-stage direct emitter preserves page-level provenance but fails the checked-in section expectations."
        )
        return result
    if kind == "docx_first_title_only":
        return score_docx_single_entry_challenger(case, run_root / str(challenger["artifact"]))
    raise ValueError(f"Unsupported challenger kind: {kind}")


def summarize_results(rows: list[dict[str, Any]]) -> dict[str, Any]:
    docs = len(rows)
    completed = sum(1 for row in rows if row.get("status") == "ok")
    failed_runs = docs - completed
    overall = 0.0
    if docs:
        overall = sum((row.get("score") or {}).get("score", 0.0) for row in rows) / docs
    challenger_rows = [row for row in rows if row.get("challenger")]
    challenger_overall = 0.0
    if challenger_rows:
        challenger_overall = sum(
            (row.get("challenger") or {}).get("score", 0.0) for row in challenger_rows
        ) / len(challenger_rows)
    return {
        "docs": docs,
        "completed": completed,
        "failed_runs": failed_runs,
        "pass_rate": (sum(1 for row in rows if (row.get("score") or {}).get("pass")) / docs) if docs else 0.0,
        "overall": overall,
        "challenger_cases": len(challenger_rows),
        "challenger_real_competitors": sum(
            1 for row in challenger_rows if (row.get("challenger") or {}).get("honest_competitor")
        ),
        "challenger_overall": challenger_overall,
        "families": sorted({row.get("family") for row in rows if row.get("family")}),
    }
