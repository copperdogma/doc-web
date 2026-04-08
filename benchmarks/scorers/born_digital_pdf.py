from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from benchmarks.scorers.layout_section_splitting import score_bundle_case


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


def _score_minimal_bundle(case: dict[str, Any], bundle_dir: Path) -> dict[str, Any]:
    manifest_path = bundle_dir / "manifest.json"
    provenance_path = bundle_dir / "provenance" / "blocks.jsonl"
    checks: dict[str, bool] = {
        "manifest_exists": manifest_path.exists(),
        "provenance_exists": provenance_path.exists(),
    }
    details: dict[str, Any] = {
        "bundle_dir": str(bundle_dir),
        "html_assertions": [],
        "provenance_assertions": [],
    }
    actual: dict[str, Any] = {}

    if not all(checks.values()):
        passed = sum(1 for value in checks.values() if value)
        total = len(checks) or 1
        return {
            "pass": False,
            "score": passed / total,
            "checks": checks,
            "details": details,
            "actual": actual,
        }

    manifest = _load_json(manifest_path)
    provenance_rows = _load_jsonl(provenance_path)
    entries = manifest.get("entries") or []

    actual.update(
        {
            "entry_count": len(entries),
            "manifest_title": manifest.get("title"),
            "provenance_row_count": len(provenance_rows),
            "entry_titles": [entry.get("title") for entry in entries],
        }
    )

    if case.get("expected_manifest_title") is not None:
        checks["manifest_title"] = manifest.get("title") == case["expected_manifest_title"]
    if case.get("min_entry_count") is not None:
        checks["entry_min_count"] = len(entries) >= int(case["min_entry_count"])
    checks["reading_order"] = (manifest.get("reading_order") or []) == [
        entry.get("entry_id") for entry in entries
    ]
    if case.get("min_provenance_rows") is not None:
        checks["provenance_min_rows"] = len(provenance_rows) >= int(case["min_provenance_rows"])
    checks["provenance_source_ids_present"] = bool(provenance_rows) and all(
        row.get("source_element_ids") for row in provenance_rows
    )

    passed = sum(1 for value in checks.values() if value)
    total = len(checks) or 1
    return {
        "pass": passed == total,
        "score": passed / total,
        "checks": checks,
        "details": details,
        "actual": actual,
    }


def score_case(case: dict[str, Any], run_dir: str | Path) -> dict[str, Any]:
    run_root = Path(run_dir)
    pages_html_path = run_root / "01_extract_pdf_marker_lite_html_v1" / "pages_html.jsonl"
    portion_path = run_root / str(case["portion_artifact"])
    bundle_dir = run_root / "output" / "html"

    checks: dict[str, bool] = {
        "pages_html_exists": pages_html_path.exists(),
        "portion_exists": portion_path.exists(),
    }
    details: dict[str, Any] = {
        "pages_html_path": str(pages_html_path),
        "portion_path": str(portion_path),
        "bundle_dir": str(bundle_dir),
    }
    actual: dict[str, Any] = {}

    if pages_html_path.exists():
        page_rows = _load_jsonl(pages_html_path)
        page_numbers = [row.get("page_number") for row in page_rows]
        actual["pages_html_rows"] = len(page_rows)
        actual["page_numbers"] = page_numbers
        if case.get("expected_pages_html_rows") is not None:
            checks["pages_html_rows"] = len(page_rows) == int(case["expected_pages_html_rows"])
        if case.get("expected_page_numbers") is not None:
            checks["page_numbers"] = page_numbers == list(case["expected_page_numbers"])

    if portion_path.exists():
        portion_rows = _load_jsonl(portion_path)
        portion_titles = [row.get("title") for row in portion_rows]
        actual["portion_rows"] = len(portion_rows)
        actual["portion_titles"] = portion_titles
        if case.get("expected_portion_rows") is not None:
            checks["portion_rows"] = len(portion_rows) == int(case["expected_portion_rows"])
        if case.get("min_portion_rows") is not None:
            checks["portion_min_rows"] = len(portion_rows) >= int(case["min_portion_rows"])
        if case.get("expected_portion_titles") is not None:
            checks["portion_titles"] = portion_titles == list(case["expected_portion_titles"])

    if case.get("expected_entry_titles"):
        bundle_score = score_bundle_case(case, bundle_dir)
    else:
        bundle_score = _score_minimal_bundle(case, bundle_dir)

    checks.update(bundle_score["checks"])
    actual.update(bundle_score["actual"])
    details["bundle"] = bundle_score["details"]

    passed = sum(1 for value in checks.values() if value)
    total = len(checks) or 1
    return {
        "pass": passed == total,
        "score": passed / total,
        "checks": checks,
        "details": details,
        "actual": actual,
    }


def summarize_results(rows: list[dict[str, Any]]) -> dict[str, Any]:
    docs = len(rows)
    completed_rows = [row for row in rows if row.get("status") == "ok"]
    supported_rows = [row for row in rows if row.get("required")]
    comparison_rows = [row for row in rows if not row.get("required")]
    supported_passes = sum(
        1 for row in supported_rows if (row.get("score") or {}).get("pass")
    )
    comparison_completed = [row for row in comparison_rows if row.get("status") == "ok"]
    comparison_passes = sum(
        1 for row in comparison_completed if (row.get("score") or {}).get("pass")
    )

    overall = 0.0
    if completed_rows:
        overall = sum((row.get("score") or {}).get("score", 0.0) for row in completed_rows) / len(completed_rows)

    comparison_overall = 0.0
    if comparison_completed:
        comparison_overall = sum(
            (row.get("score") or {}).get("score", 0.0) for row in comparison_completed
        ) / len(comparison_completed)

    return {
        "docs": docs,
        "supported_docs": len(supported_rows),
        "comparison_docs": len(comparison_rows),
        "completed": len(completed_rows),
        "failed_runs": sum(1 for row in rows if row.get("status") == "failed"),
        "skipped_optional": sum(1 for row in rows if row.get("status") == "skipped"),
        "pass_rate": (supported_passes / len(supported_rows)) if supported_rows else 0.0,
        "overall": overall,
        "comparison_completed": len(comparison_completed),
        "comparison_pass_rate": (comparison_passes / len(comparison_completed)) if comparison_completed else 0.0,
        "comparison_overall": comparison_overall,
        "lanes": sorted({row.get("lane") for row in rows if row.get("lane")}),
        "classifications": sorted({row.get("classification") for row in rows if row.get("classification")}),
    }
