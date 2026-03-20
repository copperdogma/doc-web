#!/usr/bin/env python3
"""
Thin hybrid repair proof for Story 159.

This script starts from the `baseline-images` Docling artifacts, applies two
targeted OCR rescues on the Arthur hard-case onset (pages 3 and 4 of the pinned
Onward slice), then merges the rescued fragments back into the full chapter
HTML. The goal is to prove that a page-scoped hybrid layer can fix the explicit
remaining failure class without rebuilding the whole runtime.
"""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bs4 import BeautifulSoup

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


PAGE3_PROMPT_HINTS = """
- Return HTML only for the CURRENT page image.
- Start with <h2>Arthur L'Heureux</h2>.
- Use a single genealogy <table> for the visible genealogy content on this page.
- Header columns must be NAME, BORN, MARRIED, SPOUSE, BOY, GIRL, DIED.
- Use full-width subgroup rows for ARTHUR'S FAMILY, Arthur's Grandchildren,
  DORILLA'S FAMILY, Arthur's Great Grandchildren, Dorilla's Grandchildren,
  IRENE'S FAMILY, RAYMOND'S FAMILY, THEODORE'S FAMILY, ODELIE'S FAMILY when visible.
- Emit subgroup rows as <tr class="genealogy-subgroup-heading"><th colspan="7">…</th></tr> when possible.
- Do not emit loose paragraphs for genealogy rows that are visibly tabular on the page.
- Do not invent rows from the next page.
- Preserve exact wording and dates from the image, including uncertain OCR spellings when visible.
- If a spouse death date appears on a second visual line, keep it as a second row with blank
  leading cells rather than merging it into the main row.
""".strip()


PAGE4_PROMPT_HINTS = """
- Return HTML only for the CURRENT page image.
- This page continues the Arthur L'Heureux genealogy table from the previous page.
- Return a genealogy <table> with header columns NAME, BORN, MARRIED, SPOUSE, BOY, GIRL, DIED.
- Use full-width subgroup rows instead of leaking family labels into ordinary cells.
- Visible subgroup/context rows on this page include Arthur's Great Grandchildren,
  Odelie's Grandchildren, ALICE'S FAMILY, PAUL'S FAMILY, YVETTE'S FAMILY,
  JOE'S FAMILY, ROBERT'S FAMILY, Arthur's Great Great Grandchildren,
  Odelie's Great Grandchildren, Alice's Grandchildren, JOSEPH'S FAMILY,
  ANTHONY'S FAMILY, GARY'S FAMILY, RONDALD'S FAMILY, Paul's Grandchildren,
  JEAN-PAUL'S FAMILY, ROLAND'S FAMILY, DONALD'S FAMILY when visible.
- Emit subgroup rows as <tr class="genealogy-subgroup-heading"><th colspan="7">…</th></tr> when possible.
- Do not invent rows from the next page.
- Preserve exact wording and dates from the image.
- Do not use loose paragraphs for visibly tabular content.
""".strip()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _usage_to_dict(usage: Any) -> Optional[Dict[str, Any]]:
    if usage is None:
        return None
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    if hasattr(usage, "dict"):
        return usage.dict()
    if hasattr(usage, "__dict__"):
        return dict(usage.__dict__)
    return {"value": str(usage)}


def _strip_page_number_paragraphs(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    for paragraph in soup.find_all("p", class_="page-number"):
        paragraph.decompose()
    return str(soup)


def _encode_image(path: Path) -> str:
    image_b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
    suffix = path.suffix.lower().lstrip(".") or "png"
    return f"data:image/{suffix};base64,{image_b64}"


def _clean_raw_html(raw_html: str) -> str:
    raw_html = _extract_code_fence(raw_html or "")
    cleaned_raw, _, _, _ = _extract_ocr_metadata(raw_html)
    cleaned = sanitize_html(cleaned_raw)
    return _strip_page_number_paragraphs(cleaned).strip()


def _ocr_fragment(
    *,
    model: str,
    image_path: Path,
    current_html: str,
    prompt_hints: str,
    max_output_tokens: int,
    timeout_seconds: float,
) -> Dict[str, Any]:
    prompt = build_system_prompt(prompt_hints)
    user_text = (
        "Return only HTML. Current extracted HTML/text is below as a clue for wording; "
        "it is structurally wrong. Trust the image for the final structure.\n"
        "<current-html>\n"
        f"{current_html}\n"
        "</current-html>"
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
    return {
        "raw_html": raw_html,
        "request_id": request_id,
        "usage": _usage_to_dict(usage),
        "model": model,
        "image_path": str(image_path),
    }


def _extract_page3_fragment(full_html: str) -> str:
    start = full_html.find("<h2>Arthur L'Heureux</h2>")
    if start == -1:
        raise ValueError("Arthur heading not found in baseline HTML")
    first_table = full_html.find("<table", start)
    if first_table == -1:
        raise ValueError("First Arthur continuation table not found in baseline HTML")
    return full_html[start:first_table]


def _extract_page4_fragment(full_html: str) -> str:
    start = full_html.find("<h2>Arthur L'Heureux</h2>")
    if start == -1:
        raise ValueError("Arthur heading not found in baseline HTML")
    first_table = full_html.find("<table", start)
    second_table = full_html.find("<table", first_table + 1)
    if first_table == -1 or second_table == -1:
        raise ValueError("Arthur continuation tables not found in baseline HTML")
    return full_html[first_table:second_table]


def _insert_fragment_before(anchor: Any, fragment_html: str) -> None:
    fragment_soup = BeautifulSoup(fragment_html or "", "html.parser")
    for node in list(fragment_soup.contents):
        anchor.insert_before(node)


def _splice_rescues(full_html: str, *, page3_html: str, page4_html: str) -> str:
    soup = BeautifulSoup(full_html or "", "html.parser")

    arthur_heading = next(
        (tag for tag in soup.find_all("h2") if tag.get_text(" ", strip=True) == "Arthur L'Heureux"),
        None,
    )
    if arthur_heading is None:
        raise ValueError("Arthur heading not found during splice")

    first_table = arthur_heading.find_next_sibling("table")
    if first_table is None:
        raise ValueError("Arthur page-4 baseline table not found during splice")

    node = arthur_heading
    while node is not None and node is not first_table:
        next_node = node.next_sibling
        node.extract()
        node = next_node

    _insert_fragment_before(first_table, page4_html)
    first_table.extract()

    insertion_anchor = soup.find("table")
    if insertion_anchor is None:
        raise ValueError("No table found after inserting page-4 rescue")
    _insert_fragment_before(insertion_anchor, page3_html)
    return str(soup)


def _normalized_text(text: str) -> str:
    return " ".join((text or "").split())


def _collect_subgroup_rows(table: Any) -> List[str]:
    if table is None:
        return []
    rows = table.find_all("tr", class_="genealogy-subgroup-heading")
    return [_normalized_text(row.get_text(" ", strip=True)) for row in rows]


def _arthur_excerpt_summary(html: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html or "", "html.parser")
    heading = next(
        (tag for tag in soup.find_all("h2") if _normalized_text(tag.get_text(" ", strip=True)) == "Arthur L'Heureux"),
        None,
    )
    if heading is None:
        return {
            "found_heading": False,
            "pretable_paragraph_count": 0,
            "subgroup_rows": [],
            "leak_alice_family_barbara_hodges": False,
        }

    pretable_paragraphs: List[str] = []
    cursor = heading.find_next_sibling()
    first_table = None
    while cursor is not None:
        if getattr(cursor, "name", None) == "table":
            first_table = cursor
            break
        if getattr(cursor, "name", None) == "p":
            text = _normalized_text(cursor.get_text(" ", strip=True))
            if text:
                pretable_paragraphs.append(text)
        cursor = cursor.find_next_sibling()

    subgroup_rows = _collect_subgroup_rows(first_table)
    table_text = _normalized_text(first_table.get_text(" ", strip=True)) if first_table is not None else ""
    excerpt_html = ""
    if first_table is not None:
        excerpt_html = str(heading) + str(first_table)
    else:
        excerpt_html = str(heading)

    return {
        "found_heading": True,
        "pretable_paragraph_count": len(pretable_paragraphs),
        "pretable_paragraph_samples": pretable_paragraphs[:3],
        "subgroup_rows": subgroup_rows,
        "subgroup_row_count": len(subgroup_rows),
        "leak_alice_family_barbara_hodges": "ALICE'S FAMILY Barbara Hodges" in table_text,
        "excerpt_html": excerpt_html,
    }


def _summary_markdown(summary: Dict[str, Any]) -> str:
    baseline = summary["baseline_excerpt"]
    final = summary["final_excerpt"]
    return "\n".join(
        [
            "# Docling Onward Hybrid Repair Proof",
            "",
            "## Run",
            f"- model: `{summary['model']}`",
            f"- baseline html: `{summary['baseline_html']}`",
            f"- page 3 image: `{summary['page3_image']}`",
            f"- page 4 image: `{summary['page4_image']}`",
            "",
            "## Before vs After",
            f"- pre-table paragraph count: `{baseline['pretable_paragraph_count']}` -> `{final['pretable_paragraph_count']}`",
            f"- Arthur excerpt subgroup rows: `{baseline['subgroup_row_count']}` -> `{final['subgroup_row_count']}`",
            f"- leaked `ALICE'S FAMILY Barbara Hodges`: `{baseline['leak_alice_family_barbara_hodges']}` -> `{final['leak_alice_family_barbara_hodges']}`",
            "",
            "## Final Arthur Subgroup Rows",
            *[f"- `{row}`" for row in final["subgroup_rows"]],
            "",
            "## Full-Document Metrics",
            f"- baseline: `{summary['baseline_metrics']}`",
            f"- final: `{summary['final_metrics']}`",
            "",
            "## Artifacts",
            f"- final merged html: `{summary['artifacts']['final_html']}`",
            f"- page 3 cleaned rescue: `{summary['artifacts']['page3_clean_html']}`",
            f"- page 4 cleaned rescue: `{summary['artifacts']['page4_clean_html']}`",
        ]
    ) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Story 159 thin hybrid repair proof.")
    parser.add_argument(
        "--baseline-html",
        default="output/runs/story158-docling-tuning-r1/docling/baseline-images/onward-hardcase-slice-imageonly.html",
    )
    parser.add_argument(
        "--page3-image",
        default="output/runs/story158-docling-tuning-r1/docling/baseline-images/images/page-003.png",
    )
    parser.add_argument(
        "--page4-image",
        default="output/runs/story158-docling-tuning-r1/docling/baseline-images/images/page-004.png",
    )
    parser.add_argument(
        "--outdir",
        default="output/runs/story158-docling-hybrid-proof-r1",
    )
    parser.add_argument("--model", default="gpt-4.1")
    parser.add_argument("--max-output-tokens", type=int, default=8000)
    parser.add_argument("--timeout-seconds", type=float, default=120.0)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    baseline_html_path = Path(args.baseline_html)
    page3_image_path = Path(args.page3_image)
    page4_image_path = Path(args.page4_image)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    baseline_html = _read_text(baseline_html_path)
    page3_current_html = _extract_page3_fragment(baseline_html)
    page4_current_html = _extract_page4_fragment(baseline_html)

    _write_text(outdir / "page3-current-fragment.html", page3_current_html)
    _write_text(outdir / "page4-current-fragment.html", page4_current_html)

    page3_result = _ocr_fragment(
        model=args.model,
        image_path=page3_image_path,
        current_html=page3_current_html,
        prompt_hints=PAGE3_PROMPT_HINTS,
        max_output_tokens=args.max_output_tokens,
        timeout_seconds=args.timeout_seconds,
    )
    _write_text(outdir / "page3-raw.html", page3_result["raw_html"])
    page3_clean_html = _clean_raw_html(page3_result["raw_html"])
    _write_text(outdir / "page3-clean.html", page3_clean_html)

    page4_result = _ocr_fragment(
        model=args.model,
        image_path=page4_image_path,
        current_html=page4_current_html,
        prompt_hints=PAGE4_PROMPT_HINTS,
        max_output_tokens=args.max_output_tokens,
        timeout_seconds=args.timeout_seconds,
    )
    _write_text(outdir / "page4-raw.html", page4_result["raw_html"])
    page4_clean_html = _normalize_rescue_html(_clean_raw_html(page4_result["raw_html"]))
    _write_text(outdir / "page4-clean.html", page4_clean_html)

    spliced_html = _splice_rescues(
        baseline_html,
        page3_html=page3_clean_html,
        page4_html=page4_clean_html,
    )
    _write_text(outdir / "spliced-two-page.html", spliced_html)

    final_html = merge_contiguous_genealogy_tables(
        spliced_html,
        rescue_normalizer=sanitize_html,
    )
    _write_text(outdir / "merged-two-page.html", final_html)

    baseline_excerpt = _arthur_excerpt_summary(baseline_html)
    final_excerpt = _arthur_excerpt_summary(final_html)
    _write_text(outdir / "arthur-before.html", baseline_excerpt.pop("excerpt_html"))
    _write_text(outdir / "arthur-after.html", final_excerpt.pop("excerpt_html"))

    baseline_metrics = analyze_page_row({"html": baseline_html})
    final_metrics = analyze_page_row({"html": final_html})

    summary = {
        "schema_version": "story158_docling_hybrid_proof_v1",
        "model": args.model,
        "baseline_html": str(baseline_html_path),
        "page3_image": str(page3_image_path),
        "page4_image": str(page4_image_path),
        "page3_request": {
            "request_id": page3_result["request_id"],
            "usage": page3_result["usage"],
        },
        "page4_request": {
            "request_id": page4_result["request_id"],
            "usage": page4_result["usage"],
        },
        "baseline_metrics": baseline_metrics.__dict__,
        "final_metrics": final_metrics.__dict__,
        "baseline_excerpt": baseline_excerpt,
        "final_excerpt": final_excerpt,
        "artifacts": {
            "page3_raw_html": str(outdir / "page3-raw.html"),
            "page3_clean_html": str(outdir / "page3-clean.html"),
            "page4_raw_html": str(outdir / "page4-raw.html"),
            "page4_clean_html": str(outdir / "page4-clean.html"),
            "spliced_html": str(outdir / "spliced-two-page.html"),
            "final_html": str(outdir / "merged-two-page.html"),
            "arthur_before_html": str(outdir / "arthur-before.html"),
            "arthur_after_html": str(outdir / "arthur-after.html"),
        },
    }

    with (outdir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)
    _write_text(outdir / "summary.md", _summary_markdown(summary))

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
