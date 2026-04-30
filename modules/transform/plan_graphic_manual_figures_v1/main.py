#!/usr/bin/env python3
"""Build figure policy artifacts for graphics-heavy manuals.

The module classifies OCR-emitted figure placeholders by generic visual role and
records the preservation plan before final HTML assembly. It keeps title- or
page-specific knowledge out of production logic.
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from modules.common.utils import ProgressLogger, read_jsonl, save_json


MODULE_ID = "plan_graphic_manual_figures_v1"


ROLE_PATTERNS: list[tuple[str, tuple[str, ...]]] = [
    ("summary_reference", ("summary", "quick reference", "round summary", "turn summary", "reference summary")),
    ("setup_diagram", ("setup", "component", "components", "contents", "game contents", "place components")),
    ("rule_example_diagram", ("example", "priority", "activation order", "sequence", "movement example", "resolve")),
    ("card_or_reference", ("card index", "programming card", "upgrade card", "card ", "deck", "reference", "cost:", "effect:")),
    ("map_or_board", ("course", "map", "board layout", "game board", "track", "tile", "grid", "scenario")),
    ("icon_or_component_reference", ("icon", "token", "marker", "element", "space", "symbol")),
]


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _page_text(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    return _normalize_ws(soup.get_text(" ", strip=True))


def _heading_text(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    headings = [tag.get_text(" ", strip=True) for tag in soup.find_all(["h1", "h2", "h3"])]
    return _normalize_ws(" ".join(headings))


def _extract_figures(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html or "", "html.parser")
    figures: list[dict[str, Any]] = []
    for tag in soup.find_all("img"):
        count = 1
        try:
            count = max(1, int(tag.get("data-count") or 1))
        except (TypeError, ValueError):
            count = 1
        parent = tag.parent if getattr(tag, "parent", None) and tag.parent.name == "figure" else None
        caption = ""
        if parent:
            figcaption = parent.find("figcaption")
            if figcaption:
                caption = _normalize_ws(figcaption.get_text(" ", strip=True))
        for index in range(count):
            figures.append(
                {
                    "alt": _normalize_ws(tag.get("alt") or ""),
                    "caption": caption,
                    "placeholder_index": index + 1,
                    "placeholder_count": count,
                    "in_figure": bool(parent),
                }
            )
    return figures


def _infer_role(text: str) -> str:
    lowered = text.casefold()
    for role, patterns in ROLE_PATTERNS:
        if any(pattern in lowered for pattern in patterns):
            return role
    return "instructional_figure"


def _classify_figure(alt: str, caption: str, page_text: str, headings: str) -> tuple[str, str, str]:
    primary_evidence = " ".join(part for part in [alt, caption, headings] if part)
    role = _infer_role(primary_evidence)
    if role == "instructional_figure":
        role = _infer_role(page_text[:800])
    low_alt = alt.casefold()
    low_caption = caption.casefold()
    weak_descriptor = low_alt in {"", "image", "illustration", "figure", "diagram"} and not low_caption
    if weak_descriptor:
        return role, "uncertain", "generic or empty figure descriptor needs review"
    return role, "essential", "OCR emitted this placeholder under the recipe policy for instructionally relevant visuals"


def build_plan(pages: list[dict[str, Any]], *, run_id: str | None) -> dict[str, Any]:
    plan_items: list[dict[str, Any]] = []
    page_records: list[dict[str, Any]] = []

    for row in pages:
        page_number = row.get("page_number") or row.get("page")
        printed_page_number = row.get("printed_page_number")
        html = row.get("html") or row.get("raw_html") or ""
        text = _page_text(html)
        headings = _heading_text(html)
        figures = _extract_figures(html)
        page_roles = set()
        text_role = _infer_role(" ".join([headings, text[:1200]]))
        if text_role != "instructional_figure":
            page_roles.add(text_role)

        for fig_index, figure in enumerate(figures, start=1):
            role, classification, reason = _classify_figure(
                figure["alt"],
                figure["caption"],
                text,
                headings,
            )
            page_roles.add(role)
            figure_id = f"p{int(page_number or 0):03d}-fig{fig_index:02d}"
            plan_items.append(
                {
                    "figure_id": figure_id,
                    "source_page_number": page_number,
                    "source_printed_page_number": printed_page_number,
                    "role": role,
                    "classification": classification,
                    "preserve_as_figure": classification in {"essential", "uncertain"},
                    "needs_crop": True,
                    "alt": figure["alt"],
                    "caption": figure["caption"] or None,
                    "placeholder_index": figure["placeholder_index"],
                    "placeholder_count": figure["placeholder_count"],
                    "reason": reason,
                    "required_outputs": ["html_figure", "crop_or_source_bbox", "caption_or_alt", "source_provenance"],
                }
            )

        page_records.append(
            {
                "page_number": page_number,
                "printed_page_number": printed_page_number,
                "heading_text": headings or None,
                "figure_placeholder_count": len(figures),
                "page_roles": sorted(page_roles),
                "decorative_policy": (
                    "decorative backgrounds, layout chrome, and non-instructional art should remain out of plain HTML"
                ),
            }
        )

    role_counts = Counter(item["role"] for item in plan_items)
    classification_counts = Counter(item["classification"] for item in plan_items)
    preserve_count = sum(1 for item in plan_items if item.get("preserve_as_figure"))
    uncertain_count = classification_counts.get("uncertain", 0)

    return {
        "schema_version": "graphic_manual_essential_graphics_plan_v1",
        "module_id": MODULE_ID,
        "run_id": run_id,
        "created_at": _utc(),
        "scope": "graphics_heavy_manual_or_rulebook",
        "policy": {
            "preserve": [
                "setup diagrams",
                "rule-example diagrams",
                "board/map/course layouts",
                "component/icon references",
                "card/reference sheets",
                "quick-reference summaries when they carry rules",
            ],
            "suppress": [
                "decorative backgrounds",
                "layout chrome",
                "printer metadata",
                "pure logo marks unless identity is the only page content",
            ],
            "review": [
                "generic figure placeholders with weak alt text",
                "expected visual roles with no crop or source bbox",
            ],
        },
        "summary": {
            "pages_reviewed": len(pages),
            "figure_placeholder_count": len(plan_items),
            "preserve_as_figure_count": preserve_count,
            "uncertain_count": uncertain_count,
            "pages_with_figures": sorted(
                {
                    int(item["source_page_number"])
                    for item in plan_items
                    if isinstance(item.get("source_page_number"), int)
                }
            ),
            "role_counts": dict(sorted(role_counts.items())),
            "classification_counts": dict(sorted(classification_counts.items())),
        },
        "pages": page_records,
        "plan_items": plan_items,
    }


def _write_inventory(path: Path, plan: dict[str, Any]) -> None:
    save_json(
        str(path),
        {
            "schema_version": "graphic_role_inventory_v1",
            "module_id": MODULE_ID,
            "run_id": plan.get("run_id"),
            "created_at": plan.get("created_at"),
            "scope": plan.get("scope"),
            "summary": plan.get("summary"),
            "graphics": plan.get("plan_items", []),
            "page_policy": plan.get("pages", []),
        },
    )


def _write_report(path: Path, plan: dict[str, Any], inventory_name: str) -> None:
    summary = plan["summary"]
    lines = [
        "# Graphic Manual Figure Plan",
        "",
        f"- Scope: `{plan['scope']}`",
        f"- Pages reviewed: `{summary['pages_reviewed']}`",
        f"- Figure placeholders: `{summary['figure_placeholder_count']}`",
        f"- Preserve-as-figure items: `{summary['preserve_as_figure_count']}`",
        f"- Uncertain items: `{summary['uncertain_count']}`",
        f"- Inventory: `{inventory_name}`",
        "",
        "## Role Counts",
    ]
    for role, count in summary["role_counts"].items():
        lines.append(f"- `{role}`: {count}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plan essential figure preservation for graphics-heavy manuals.")
    parser.add_argument("--pages", required=True, help="page_html_v1 JSONL")
    parser.add_argument("--out", required=True, help="Output essential graphics plan JSON")
    parser.add_argument("--progress-file")
    parser.add_argument("--state-file")
    parser.add_argument("--run-id")
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pages = list(read_jsonl(args.pages))
    logger = ProgressLogger(state_path=args.state_file, progress_path=args.progress_file, run_id=args.run_id)
    logger.log("transform", "running", message="Planning manual figure policy", module_id=MODULE_ID)

    plan = build_plan(pages, run_id=args.run_id)
    save_json(str(out_path), plan)
    inventory_path = out_path.parent / "graphic_role_inventory.json"
    report_path = out_path.parent / "graphic_manual_figure_plan.md"
    _write_inventory(inventory_path, plan)
    _write_report(report_path, plan, inventory_path.name)

    logger.log(
        "transform",
        "done",
        current=plan["summary"]["figure_placeholder_count"],
        total=plan["summary"]["figure_placeholder_count"],
        message="Graphic manual figure plan complete",
        artifact=str(out_path),
        module_id=MODULE_ID,
        extra={"summary": plan["summary"], "inventory": str(inventory_path)},
    )


if __name__ == "__main__":
    main()
