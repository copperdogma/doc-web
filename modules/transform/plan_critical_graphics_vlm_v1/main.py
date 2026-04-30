#!/usr/bin/env python3
"""Plan rule-critical graphics for short graphics-heavy manuals.

This module uses a strong multimodal model for semantic visual judgment, then
keeps all downstream work deterministic: final image assets remain source-pixel
crops with provenance, not generated images.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import re
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from PIL import Image

from modules.common.utils import ProgressLogger, append_jsonl, read_jsonl, save_json

try:
    from modules.common.openai_client import OpenAI
except Exception as exc:  # pragma: no cover - environment dependency
    OpenAI = None
    _OPENAI_IMPORT_ERROR = exc
else:
    _OPENAI_IMPORT_ERROR = None

try:
    import json_repair
except Exception:  # pragma: no cover - optional dependency
    json_repair = None


MODULE_ID = "plan_critical_graphics_vlm_v1"
SCHEMA_VERSION = "critical_graphics_manifest_v1"

IMPORTANCE_VALUES = {"essential", "useful", "decorative", "uncertain"}
ROLE_VALUES = {
    "setup_diagram",
    "rule_example_diagram",
    "map_or_board",
    "card_face",
    "card_reference",
    "component_reference",
    "icon_reference",
    "board_element",
    "summary_reference",
    "cover_identity",
    "decorative_art",
    "other",
}

SYSTEM_PROMPT = """
You are the visual-planning stage of a document processor.

Input: one page image from a graphics-heavy manual/rulebook plus OCR context.
Task: decide which visible graphics should be preserved as separate source-pixel
figures in a strongly semantic plain-HTML manual.

Preserve visuals when the reader needs the visual appearance to understand the
rules or instructions: setup diagrams, rule examples, board/map/course layouts,
component or icon references, card faces/reference sheets, diagrams showing
spatial relationships, and quick-reference summaries that carry rules.
Use "essential" for visuals that should appear as figures in the plain-HTML
manual. Use "useful" only for optional visuals that are helpful but not needed
for comprehension.

Suppress decorative backgrounds, texture, non-instructional art, printer marks,
layout chrome, repeated branding, and visuals that are fully redundant with
nearby transcribed text.

Return ONLY a JSON object with this shape:
{
  "page_role": "short page role",
  "visual_density": "none|low|medium|high",
  "targets": [
    {
      "importance": "essential|useful|decorative|uncertain",
      "role": "setup_diagram|rule_example_diagram|map_or_board|card_face|card_reference|component_reference|icon_reference|board_element|summary_reference|cover_identity|decorative_art|other",
      "description": "what the visual is",
      "reason": "why to preserve or suppress it",
      "nearby_text": "nearby label/rule text, if visible",
      "expected_visual_contents": ["brief content checklist"],
      "bbox": {"x0": 0.0, "y0": 0.0, "x1": 1.0, "y1": 1.0},
      "confidence": 0.0
    }
  ],
  "decorative_or_redundant_notes": ["suppressed visuals and why"],
  "uncertainties": ["anything that should be reviewed"]
}

Coordinates are normalized floats relative to the full page image. Use tight
boxes around the visual to crop. If a target is important but the exact box is
unclear, include the target with no bbox and confidence below 0.55.
Do not invent visuals that are not visible.
""".strip()


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _openai_supports_temperature(model: str) -> bool:
    return not (model or "").casefold().startswith("gpt-5")


def _strip_code_fence(text: str) -> str:
    raw = (text or "").strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\s*```$", "", raw)
    return raw.strip()


def extract_json_object(text: str) -> dict[str, Any]:
    """Parse a JSON object from raw model text."""
    raw = _strip_code_fence(text)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start < 0 or end < start:
            raise
        raw_object = raw[start : end + 1]
        try:
            data = json.loads(raw_object)
        except json.JSONDecodeError:
            if json_repair is None:
                raise
            data = json_repair.repair_json(raw_object, return_objects=True)
    if not isinstance(data, dict):
        raise ValueError("critical graphics planner response must be a JSON object")
    return data


def _coerce_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _coerce_bbox(raw: Any, *, image_width: int, image_height: int) -> tuple[dict[str, float], dict[str, int]] | None:
    if raw is None:
        return None
    if isinstance(raw, (list, tuple)) and len(raw) == 4:
        raw = {"x0": raw[0], "y0": raw[1], "x1": raw[2], "y1": raw[3]}
    if not isinstance(raw, dict):
        return None

    if {"x", "y", "width", "height"} <= set(raw):
        x = _coerce_float(raw.get("x"))
        y = _coerce_float(raw.get("y"))
        width = _coerce_float(raw.get("width"))
        height = _coerce_float(raw.get("height"))
        if None in {x, y, width, height}:
            return None
        raw = {"x0": x, "y0": y, "x1": x + width, "y1": y + height}

    vals = [_coerce_float(raw.get(key)) for key in ("x0", "y0", "x1", "y1")]
    if any(val is None for val in vals):
        return None
    x0, y0, x1, y1 = [float(val) for val in vals if val is not None]

    def normalize_axis(v0: float, v1: float, dim: int) -> tuple[float, float]:
        max_abs = max(abs(v0), abs(v1))
        if max_abs <= 1.0:
            return v0, v1
        if max_abs <= 1000.0:
            return v0 / 1000.0, v1 / 1000.0
        return v0 / float(max(1, dim)), v1 / float(max(1, dim))

    x0, x1 = normalize_axis(x0, x1, image_width)
    y0, y1 = normalize_axis(y0, y1, image_height)
    if x0 > x1:
        x0, x1 = x1, x0
    if y0 > y1:
        y0, y1 = y1, y0
    x0 = max(0.0, min(1.0, x0))
    y0 = max(0.0, min(1.0, y0))
    x1 = max(0.0, min(1.0, x1))
    y1 = max(0.0, min(1.0, y1))
    if x1 <= x0 or y1 <= y0:
        return None

    px0 = max(0, min(image_width - 1, int(round(x0 * image_width))))
    py0 = max(0, min(image_height - 1, int(round(y0 * image_height))))
    px1 = max(0, min(image_width, int(round(x1 * image_width))))
    py1 = max(0, min(image_height, int(round(y1 * image_height))))
    if px1 <= px0 or py1 <= py0:
        return None

    bbox_norm = {"x0": round(x0, 5), "y0": round(y0, 5), "x1": round(x1, 5), "y1": round(y1, 5)}
    bbox_pixels = {
        "x0": px0,
        "y0": py0,
        "x1": px1,
        "y1": py1,
        "width": px1 - px0,
        "height": py1 - py0,
    }
    return bbox_norm, bbox_pixels


def _normalize_importance(raw: Any) -> str:
    value = _normalize_ws(str(raw or "")).casefold().replace("-", "_").replace(" ", "_")
    aliases = {
        "critical": "essential",
        "required": "essential",
        "important": "essential",
        "preserve": "essential",
        "optional": "useful",
        "helpful": "useful",
        "redundant": "decorative",
        "decoration": "decorative",
        "background": "decorative",
        "unknown": "uncertain",
        "review": "uncertain",
    }
    value = aliases.get(value, value)
    return value if value in IMPORTANCE_VALUES else "uncertain"


def _normalize_role(raw: Any) -> str:
    value = _normalize_ws(str(raw or "")).casefold().replace("-", "_").replace(" ", "_")
    aliases = {
        "setup": "setup_diagram",
        "diagram": "rule_example_diagram",
        "example": "rule_example_diagram",
        "rule_example": "rule_example_diagram",
        "map": "map_or_board",
        "board": "map_or_board",
        "course": "map_or_board",
        "card": "card_face",
        "card_grid": "card_reference",
        "card_sheet": "card_reference",
        "reference_card": "card_reference",
        "component": "component_reference",
        "token": "component_reference",
        "icon": "icon_reference",
        "quick_reference": "summary_reference",
        "summary": "summary_reference",
        "cover": "cover_identity",
        "decorative": "decorative_art",
        "background": "decorative_art",
    }
    value = aliases.get(value, value)
    return value if value in ROLE_VALUES else "other"


def _as_string_list(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [_normalize_ws(str(item)) for item in raw if _normalize_ws(str(item))]
    text = _normalize_ws(str(raw))
    return [text] if text else []


def _page_context(html: str, *, max_context_chars: int) -> dict[str, Any]:
    soup = BeautifulSoup(html or "", "html.parser")
    headings = [_normalize_ws(tag.get_text(" ", strip=True)) for tag in soup.find_all(["h1", "h2", "h3"])]
    figures = []
    for idx, img in enumerate(soup.find_all("img"), start=1):
        parent = img.parent if getattr(img, "parent", None) and img.parent.name == "figure" else None
        caption = ""
        if parent:
            figcaption = parent.find("figcaption")
            if figcaption:
                caption = _normalize_ws(figcaption.get_text(" ", strip=True))
        figures.append(
            {
                "index": idx,
                "alt": _normalize_ws(img.get("alt") or ""),
                "count": img.get("data-count") or "1",
                "caption": caption,
            }
        )
    text = _normalize_ws(soup.get_text(" ", strip=True))
    if len(text) > max_context_chars:
        text = text[:max_context_chars].rsplit(" ", 1)[0] + " ..."
    return {"headings": headings, "ocr_text": text, "ocr_figure_placeholders": figures}


def _encode_image_data_uri(image_path: Path, *, max_long_side: int) -> tuple[str, dict[str, Any]]:
    image = Image.open(image_path)
    width, height = image.size
    sent_width, sent_height = width, height
    mime = "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"
    out_image = image
    resized = False
    if max_long_side > 0 and max(width, height) > max_long_side:
        scale = max_long_side / float(max(width, height))
        sent_width = max(1, int(round(width * scale)))
        sent_height = max(1, int(round(height * scale)))
        out_image = image.resize((sent_width, sent_height), Image.LANCZOS)
        mime = "image/jpeg"
        resized = True
    buf = io.BytesIO()
    if mime == "image/jpeg":
        if out_image.mode not in {"RGB", "L"}:
            out_image = out_image.convert("RGB")
        out_image.save(buf, format="JPEG", quality=88, optimize=True)
    else:
        out_image.save(buf, format="PNG")
    data_uri = f"data:{mime};base64,{base64.b64encode(buf.getvalue()).decode('ascii')}"
    return data_uri, {
        "image_width": width,
        "image_height": height,
        "sent_width": sent_width,
        "sent_height": sent_height,
        "sent_mime": mime,
        "resized": resized,
    }


def _usage_dict(usage: Any) -> dict[str, int]:
    if usage is None:
        return {}
    if isinstance(usage, dict):
        return {str(k): int(v) for k, v in usage.items() if isinstance(v, (int, float))}
    keys = ("input_tokens", "output_tokens", "total_tokens", "prompt_tokens", "completion_tokens")
    out = {}
    for key in keys:
        value = getattr(usage, key, None)
        if isinstance(value, (int, float)):
            out[key] = int(value)
    return out


def _call_openai_page(
    *,
    model: str,
    image_data_uri: str,
    context: dict[str, Any],
    temperature: float,
    max_output_tokens: int,
    timeout_seconds: float | None,
) -> tuple[str, dict[str, int], str | None]:
    if OpenAI is None:  # pragma: no cover
        raise RuntimeError("openai package required") from _OPENAI_IMPORT_ERROR
    client = OpenAI(timeout=timeout_seconds) if timeout_seconds else OpenAI()
    user_text = (
        "Return the JSON object for this page.\n\n"
        "OCR context:\n"
        f"{json.dumps(context, ensure_ascii=False, indent=2)}"
    )
    request_kwargs: dict[str, Any] = {
        "model": model,
        "max_output_tokens": max_output_tokens,
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": SYSTEM_PROMPT}]},
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": user_text},
                    {"type": "input_image", "image_url": image_data_uri},
                ],
            },
        ],
    }
    if _openai_supports_temperature(model):
        request_kwargs["temperature"] = temperature
    resp = client.responses.create(**request_kwargs)
    return resp.output_text or "", _usage_dict(getattr(resp, "usage", None)), getattr(resp, "id", None)


def normalize_page_plan(
    data: dict[str, Any],
    *,
    page_number: int,
    source_image: str,
    image_width: int,
    image_height: int,
    raw_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    raw_targets = data.get("targets") or data.get("critical_graphics") or data.get("graphics") or []
    if not isinstance(raw_targets, list):
        raw_targets = []

    targets: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_targets, start=1):
        if not isinstance(raw, dict):
            continue
        importance = _normalize_importance(raw.get("importance") or raw.get("classification"))
        role = _normalize_role(raw.get("role") or raw.get("type"))
        bbox_raw = (
            raw.get("bbox")
            or raw.get("bbox_norm")
            or raw.get("image_box")
            or raw.get("box")
            or raw.get("box_2d")
        )
        coerced_bbox = _coerce_bbox(bbox_raw, image_width=image_width, image_height=image_height)
        confidence = _coerce_float(raw.get("confidence"))
        if confidence is None:
            confidence = 0.5 if importance == "uncertain" else 0.7
        confidence = max(0.0, min(1.0, confidence))
        target: dict[str, Any] = {
            "target_id": f"p{page_number:03d}-g{index:02d}",
            "source_page_number": page_number,
            "source_image": source_image,
            "importance": importance,
            "role": role,
            "description": _normalize_ws(str(raw.get("description") or raw.get("label") or "")),
            "reason": _normalize_ws(str(raw.get("reason") or "")),
            "nearby_text": _normalize_ws(str(raw.get("nearby_text") or raw.get("text") or "")),
            "expected_visual_contents": _as_string_list(raw.get("expected_visual_contents") or raw.get("contents")),
            "confidence": round(confidence, 3),
        }
        if coerced_bbox:
            bbox_norm, bbox_pixels = coerced_bbox
            target["bbox_norm"] = bbox_norm
            target["bbox_pixels"] = bbox_pixels
            target["area_ratio"] = round((bbox_pixels["width"] * bbox_pixels["height"]) / float(image_width * image_height), 5)
        targets.append(target)

    targets.sort(
        key=lambda target: (
            (target.get("bbox_norm") or {}).get("y0", 9.0),
            (target.get("bbox_norm") or {}).get("x0", 9.0),
            target["target_id"],
        )
    )
    for index, target in enumerate(targets, start=1):
        target["target_id"] = f"p{page_number:03d}-g{index:02d}"

    decorative_notes = _as_string_list(
        data.get("decorative_or_redundant_notes")
        or data.get("decorative_notes")
        or data.get("suppressed")
    )
    uncertainties = _as_string_list(data.get("uncertainties") or data.get("warnings"))
    return {
        "page_number": page_number,
        "source_image": source_image,
        "image_width": image_width,
        "image_height": image_height,
        "page_role": _normalize_ws(str(data.get("page_role") or "")) or None,
        "visual_density": _normalize_ws(str(data.get("visual_density") or "")) or None,
        "targets": targets,
        "decorative_or_redundant_notes": decorative_notes,
        "uncertainties": uncertainties,
        "ocr_context": raw_context or {},
    }


def _fallback_page_plan_from_ocr(
    *,
    page_number: int,
    source_image: str,
    image_width: int,
    image_height: int,
    context: dict[str, Any],
) -> dict[str, Any]:
    targets = []
    for idx, placeholder in enumerate(context.get("ocr_figure_placeholders") or [], start=1):
        count = 1
        try:
            count = max(1, int(placeholder.get("count") or 1))
        except (TypeError, ValueError):
            count = 1
        for _ in range(count):
            label = _normalize_ws(placeholder.get("alt") or placeholder.get("caption") or "OCR image placeholder")
            targets.append(
                {
                    "importance": "uncertain",
                    "role": "other",
                    "description": label,
                    "reason": "Fallback target from OCR figure placeholder; no VLM judgment was used.",
                    "nearby_text": "",
                    "expected_visual_contents": [label] if label else [],
                    "confidence": 0.35,
                }
            )
    return normalize_page_plan(
        {"page_role": "fallback_from_ocr", "visual_density": "uncertain", "targets": targets},
        page_number=page_number,
        source_image=source_image,
        image_width=image_width,
        image_height=image_height,
        raw_context=context,
    )


def _page_lookup(rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    lookup = {}
    for row in rows:
        page = row.get("page_number") or row.get("page")
        if isinstance(page, int):
            lookup[page] = row
    return lookup


def _parse_pages_filter(only_pages: str) -> set[int]:
    pages = set()
    for token in (only_pages or "").split(","):
        token = token.strip()
        if not token:
            continue
        pages.add(int(token))
    return pages


def _summary(page_records: list[dict[str, Any]], *, model: str) -> dict[str, Any]:
    target_count = sum(len(page.get("targets") or []) for page in page_records)
    importance_counts = Counter(
        target.get("importance")
        for page in page_records
        for target in (page.get("targets") or [])
    )
    role_counts = Counter(
        target.get("role")
        for page in page_records
        for target in (page.get("targets") or [])
    )
    bbox_count = sum(1 for page in page_records for target in (page.get("targets") or []) if target.get("bbox_pixels"))
    return {
        "model": model,
        "page_count": len(page_records),
        "target_count": target_count,
        "essential_count": int(importance_counts.get("essential", 0)),
        "useful_count": int(importance_counts.get("useful", 0)),
        "decorative_count": int(importance_counts.get("decorative", 0)),
        "uncertain_count": int(importance_counts.get("uncertain", 0)),
        "targets_with_bbox_count": bbox_count,
        "importance_counts": dict(sorted(importance_counts.items())),
        "role_counts": dict(sorted(role_counts.items())),
        "pages_with_essential_targets": [
            page["page_number"]
            for page in page_records
            if any(target.get("importance") == "essential" for target in page.get("targets") or [])
        ],
    }


def build_manifest(
    *,
    page_rows: list[dict[str, Any]],
    html_rows: list[dict[str, Any]],
    model: str,
    run_id: str | None,
    max_context_chars: int,
    max_long_side: int,
    max_output_tokens: int,
    temperature: float,
    concurrency: int,
    timeout_seconds: float | None,
    only_pages: set[int] | None = None,
    fallback_from_ocr: bool = False,
    raw_out_path: Path | None = None,
    logger: ProgressLogger | None = None,
) -> dict[str, Any]:
    html_by_page = _page_lookup(html_rows)
    filtered_pages = []
    for row in page_rows:
        page = row.get("page_number") or row.get("page")
        if not isinstance(page, int):
            continue
        if only_pages and page not in only_pages:
            continue
        filtered_pages.append(row)

    page_records: list[dict[str, Any]] = []
    raw_rows: list[dict[str, Any]] = []
    raw_lock = threading.Lock()
    if raw_out_path and raw_out_path.exists():
        raw_out_path.unlink()

    def record_raw(raw_row: dict[str, Any]) -> None:
        raw_rows.append(raw_row)
        if raw_out_path:
            with raw_lock:
                append_jsonl(str(raw_out_path), raw_row)

    def process_page(page_row: dict[str, Any]) -> tuple[int, dict[str, Any], dict[str, Any]]:
        page_number = int(page_row.get("page_number") or page_row.get("page"))
        image_path = Path(str(page_row.get("image") or ""))
        if not image_path.exists():
            raise FileNotFoundError(f"Missing logical page image for page {page_number}: {image_path}")
        context = _page_context((html_by_page.get(page_number) or {}).get("html") or "", max_context_chars=max_context_chars)
        data_uri, image_meta = _encode_image_data_uri(image_path, max_long_side=max_long_side)
        if fallback_from_ocr:
            record = _fallback_page_plan_from_ocr(
                page_number=page_number,
                source_image=str(image_path),
                image_width=int(image_meta["image_width"]),
                image_height=int(image_meta["image_height"]),
                context=context,
            )
            raw_row = {"page_number": page_number, "fallback_from_ocr": True}
            record_raw(raw_row)
            return page_number, record, raw_row
        raw, usage, request_id = _call_openai_page(
            model=model,
            image_data_uri=data_uri,
            context=context,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            timeout_seconds=timeout_seconds,
        )
        parsed = extract_json_object(raw)
        record = normalize_page_plan(
            parsed,
            page_number=page_number,
            source_image=str(image_path),
            image_width=int(image_meta["image_width"]),
            image_height=int(image_meta["image_height"]),
            raw_context=context,
        )
        raw_row = {
            "page_number": page_number,
            "request_id": request_id,
            "usage": usage,
            "raw": raw,
            "image_meta": image_meta,
        }
        record_raw(raw_row)
        return page_number, record, raw_row

    total = len(filtered_pages)
    if total == 0:
        raise ValueError("No pages selected for critical graphics planning")

    completed = 0
    if concurrency <= 1:
        for row in filtered_pages:
            page_number, record, raw_row = process_page(row)
            page_records.append(record)
            raw_rows.append(raw_row)
            completed += 1
            if logger:
                logger.log("transform", "running", current=completed, total=total, message=f"Planned critical graphics for page {page_number}", module_id=MODULE_ID)
    else:
        with ThreadPoolExecutor(max_workers=max(1, concurrency)) as executor:
            futures = {executor.submit(process_page, row): row for row in filtered_pages}
            for future in as_completed(futures):
                page_number, record, raw_row = future.result()
                page_records.append(record)
                raw_rows.append(raw_row)
                completed += 1
                if logger:
                    logger.log("transform", "running", current=completed, total=total, message=f"Planned critical graphics for page {page_number}", module_id=MODULE_ID)

    page_records.sort(key=lambda row: row["page_number"])
    raw_rows.sort(key=lambda row: row.get("page_number", 0))
    return {
        "schema_version": SCHEMA_VERSION,
        "module_id": MODULE_ID,
        "run_id": run_id,
        "created_at": _utc(),
        "scope": "graphics_heavy_manual_or_rulebook",
        "policy": {
            "final_asset_policy": "Use this manifest as crop intent and validation evidence; final figure assets must be deterministic crops from source page images.",
            "generated_image_policy": "Generated grids/contact sheets may be QA artifacts only and must not replace source-pixel manual figures.",
            "category": "short graphics-heavy manuals/rulebooks with dense designed pages and essential explanatory graphics",
        },
        "summary": _summary(page_records, model=model),
        "pages": page_records,
    }


def _write_report(path: Path, manifest: dict[str, Any], raw_path: Path | None) -> None:
    summary = manifest["summary"]
    lines = [
        "# Critical Graphics Manifest",
        "",
        f"- Scope: `{manifest['scope']}`",
        f"- Model: `{summary['model']}`",
        f"- Pages reviewed: `{summary['page_count']}`",
        f"- Targets: `{summary['target_count']}`",
        f"- Essential: `{summary['essential_count']}`",
        f"- Useful: `{summary['useful_count']}`",
        f"- Decorative: `{summary['decorative_count']}`",
        f"- Uncertain: `{summary['uncertain_count']}`",
        f"- Targets with bbox: `{summary['targets_with_bbox_count']}`",
    ]
    if raw_path:
        lines.append(f"- Raw model responses: `{raw_path.name}`")
    lines.extend(["", "## Role Counts"])
    for role, count in summary["role_counts"].items():
        lines.append(f"- `{role}`: {count}")
    lines.extend(["", "## Essential Target Pages"])
    for page in summary["pages_with_essential_targets"]:
        lines.append(f"- page `{page}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plan critical graphics from logical page images and OCR context.")
    parser.add_argument("--pages", required=True, help="Ordered page_image_v1 JSONL")
    parser.add_argument("--page-html", dest="page_html", required=True, help="OCR page_html_v1 JSONL")
    parser.add_argument("--out", required=True, help="Output critical graphics manifest JSON")
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--max-output-tokens", dest="max_output_tokens", type=int, default=4096)
    parser.add_argument("--max_output_tokens", dest="max_output_tokens", type=int, default=4096)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-long-side", dest="max_long_side", type=int, default=1600)
    parser.add_argument("--max_long_side", dest="max_long_side", type=int, default=1600)
    parser.add_argument("--max-context-chars", dest="max_context_chars", type=int, default=3000)
    parser.add_argument("--max_context_chars", dest="max_context_chars", type=int, default=3000)
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--timeout-seconds", dest="timeout_seconds", type=float, default=None)
    parser.add_argument("--timeout_seconds", dest="timeout_seconds", type=float, default=None)
    parser.add_argument("--only-pages", dest="only_pages", default="")
    parser.add_argument("--only_pages", dest="only_pages", default="")
    parser.add_argument("--fallback-from-ocr", dest="fallback_from_ocr", action="store_true")
    parser.add_argument("--fallback_from_ocr", dest="fallback_from_ocr", action="store_true")
    parser.add_argument("--progress-file")
    parser.add_argument("--state-file")
    parser.add_argument("--run-id")
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path = out_path.with_name("critical_graphics_model_responses.jsonl")
    logger = ProgressLogger(state_path=args.state_file, progress_path=args.progress_file, run_id=args.run_id)
    logger.log("transform", "running", current=0, total=None, message="Planning critical graphics with VLM", artifact=str(out_path), module_id=MODULE_ID)
    only_pages = _parse_pages_filter(args.only_pages)
    manifest = build_manifest(
        page_rows=list(read_jsonl(args.pages)),
        html_rows=list(read_jsonl(args.page_html)),
        model=args.model,
        run_id=args.run_id,
        max_context_chars=args.max_context_chars,
        max_long_side=args.max_long_side,
        max_output_tokens=args.max_output_tokens,
        temperature=args.temperature,
        concurrency=max(1, args.concurrency),
        timeout_seconds=args.timeout_seconds,
        only_pages=only_pages or None,
        fallback_from_ocr=args.fallback_from_ocr,
        raw_out_path=raw_path,
        logger=logger,
    )
    save_json(str(out_path), manifest)
    _write_report(out_path.with_suffix(".md"), manifest, raw_path)
    logger.log(
        "transform",
        "done",
        current=manifest["summary"]["page_count"],
        total=manifest["summary"]["page_count"],
        message=f"Critical graphics plan complete: {manifest['summary']['essential_count']} essential targets",
        artifact=str(out_path),
        module_id=MODULE_ID,
        extra={"summary": manifest["summary"]},
    )


if __name__ == "__main__":
    main()
