from __future__ import annotations

import html
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from modules.build.build_chapter_html_v1.main import (
    _block_kind_for_tag,
    _iter_provenance_tags,
    _should_emit_provenance_tag,
    _text_quote_for_tag,
)
from modules.common.utils import save_json, save_jsonl
from schemas import DocWebBundleManifest, DocWebProvenanceBlock


CONTENT_REF_RE = re.compile(
    r"<content-ref[^>]*src=['\"]([^'\"]+)['\"][^>]*/?>\s*(?:</content-ref>)?",
    re.IGNORECASE,
)
TAG_RE = re.compile(r"<[^>]+>")
HEADING_TAG_RE = re.compile(r"^h[1-6]$")
HEADING_FAMILY_NUMBER_RE = re.compile(r"\b\d+\b")
CHOICE_PARAGRAPH_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=(?:If|When|Unless)\s+you\b)")
CHOICE_LEAD_RE = re.compile(r"^(?:if|when|unless)\s+you\b", re.IGNORECASE)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def html_to_text(value: str) -> str:
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", value or "")).strip()


def _text_identity(value: str) -> str:
    return re.sub(r"\s+", " ", html_to_text(value)).strip()


def _token_set(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9']+", (text or "").lower())
        if len(token) >= 3
    }


def token_coverage(source_text: str, output_text: str) -> float:
    source_tokens = _token_set(source_text)
    if not source_tokens:
        return 0.0
    output_tokens = _token_set(output_text)
    return round(len(source_tokens & output_tokens) / len(source_tokens), 4)


def _iter_blocks(block: dict[str, Any], *, parent_id: str | None = None):
    yield block, parent_id
    for child in block.get("children") or []:
        if isinstance(child, dict):
            yield from _iter_blocks(child, parent_id=block.get("id"))


def _page_blocks(document_payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        child
        for child in document_payload.get("children", [])
        if isinstance(child, dict) and child.get("block_type") == "Page"
    ]


def _build_block_index(page_block: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        block["id"]: block
        for block, _ in _iter_blocks(page_block)
        if isinstance(block.get("id"), str)
    }


def _page_stats_by_page_id(marker_meta: dict[str, Any] | None) -> dict[int, dict[str, Any]]:
    if not marker_meta:
        return {}
    stats = marker_meta.get("page_stats") or []
    return {
        int(row["page_id"]): row
        for row in stats
        if isinstance(row, dict) and isinstance(row.get("page_id"), int)
    }


def _render_block_html(block: dict[str, Any]) -> str:
    raw_html = block.get("html") or ""
    if raw_html.strip() and "<" not in raw_html:
        block_type = block.get("block_type") or "Text"
        raw_html = (
            f'<p block-type="{html.escape(str(block_type), quote=True)}">'
            f"{html.escape(raw_html.strip())}</p>"
        )
    return raw_html


def _has_structural_content(value: str) -> bool:
    lowered = (value or "").lower()
    return bool(html_to_text(value)) or any(tag in lowered for tag in ("<img", "<table", "<figure", "<li", "<h"))


def _annotate_source_html(
    rendered_html: str,
    *,
    block: dict[str, Any],
    page_number: int,
    extraction_method: str | None,
    processing_step: str,
    confidence: float | None,
) -> str:
    if not _has_structural_content(rendered_html):
        return rendered_html

    soup = BeautifulSoup(rendered_html, "html.parser")
    source_id = block.get("id")
    bbox = block.get("bbox")
    bbox_attr = json.dumps([round(float(value)) for value in bbox], separators=(",", ":")) if bbox else None

    for tag in soup.find_all(True):
        if source_id:
            tag["data-source-element-id"] = str(source_id)
        tag["data-source-page-number"] = str(page_number)
        if extraction_method:
            tag["data-extraction-method"] = extraction_method
        tag["data-processing-step"] = processing_step
        if confidence is not None:
            tag["data-source-confidence"] = str(confidence)
        if bbox_attr:
            tag["data-source-bbox"] = bbox_attr
    return soup.decode_contents()


def _resolve_block_html(
    block: dict[str, Any],
    block_index: dict[str, dict[str, Any]],
    cache: dict[str, str],
    *,
    page_number: int,
    extraction_method: str | None,
    processing_step: str,
    confidence: float | None,
) -> str:
    block_id = block.get("id")
    if isinstance(block_id, str) and block_id in cache:
        return cache[block_id]

    own_html = _render_block_html(block)
    has_content_refs = bool(CONTENT_REF_RE.search(own_html))
    children = [child for child in block.get("children") or [] if isinstance(child, dict)]

    def _replace(match: re.Match[str]) -> str:
        ref_id = match.group(1)
        ref_block = block_index.get(ref_id)
        if ref_block is None:
            return ""
        return _resolve_block_html(
            ref_block,
            block_index,
            cache,
            page_number=page_number,
            extraction_method=extraction_method,
            processing_step=processing_step,
            confidence=confidence,
        )

    child_html = "".join(
        _resolve_block_html(
            child,
            block_index,
            cache,
            page_number=page_number,
            extraction_method=extraction_method,
            processing_step=processing_step,
            confidence=confidence,
        )
        for child in children
    )

    if has_content_refs:
        rendered = CONTENT_REF_RE.sub(_replace, own_html)
    else:
        rendered_self = (
            _annotate_source_html(
                own_html,
                block=block,
                page_number=page_number,
                extraction_method=extraction_method,
                processing_step=processing_step,
                confidence=confidence,
            )
            if _has_structural_content(own_html)
            else own_html
        )
        if child_html and not _has_structural_content(own_html):
            rendered = child_html
        elif child_html:
            rendered = f"{rendered_self}{child_html}"
        else:
            rendered = rendered_self

    if isinstance(block_id, str):
        cache[block_id] = rendered
    return rendered


def _block_inventory_rows(
    page_block: dict[str, Any],
    *,
    page_number: int,
    run_id: str,
    created_at: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for block, parent_id in _iter_blocks(page_block):
        rows.append(
            {
                "page": page_number,
                "page_number": page_number,
                "run_id": run_id,
                "created_at": created_at,
                "marker_block_id": block.get("id"),
                "marker_parent_id": parent_id,
                "marker_block_type": block.get("block_type"),
                "bbox": block.get("bbox"),
                "polygon": block.get("polygon"),
                "section_hierarchy": block.get("section_hierarchy"),
                "child_count": len(block.get("children") or []),
                "html": block.get("html"),
                "text_chars": len(html_to_text(block.get("html") or "")),
            }
        )
    return rows


def _bundle_document_title(page_rows: list[dict[str, Any]], input_pdf: Path) -> str:
    for row in page_rows:
        soup = BeautifulSoup(row["html"], "html.parser")
        heading = soup.find(HEADING_TAG_RE)
        if heading:
            text = html_to_text(str(heading))
            if text:
                return text
    return input_pdf.stem


def _page_title(page_html: str, page_number: int) -> str:
    soup = BeautifulSoup(page_html, "html.parser")
    heading = soup.find(HEADING_TAG_RE)
    if heading:
        text = html_to_text(str(heading))
        if text:
            return text
    return f"Page {page_number}"


def _bbox_from_attr(value: str | None) -> dict[str, int] | None:
    if not value:
        return None
    try:
        raw = json.loads(value)
    except json.JSONDecodeError:
        return None
    if not isinstance(raw, list) or len(raw) < 4:
        return None
    return {
        "x0": int(raw[0]),
        "y0": int(raw[1]),
        "x1": int(raw[2]),
        "y1": int(raw[3]),
    }


def _bundle_page_html(
    *,
    document_title: str,
    entry_title: str,
    body_html: str,
    prev_entry_id: str | None,
    next_entry_id: str | None,
) -> str:
    nav_parts = ['<a href="index.html">Index</a>']
    if prev_entry_id:
        nav_parts.append(f'<a href="{prev_entry_id}.html">Previous</a>')
    if next_entry_id:
        nav_parts.append(f'<a href="{next_entry_id}.html">Next</a>')
    nav_html = " | ".join(nav_parts)
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            f"  <title>{html.escape(entry_title)} | {html.escape(document_title)}</title>",
            "</head>",
            "<body>",
            f'  <nav aria-label="Document navigation">{nav_html}</nav>',
            "  <main>",
            f"    {body_html}",
            "  </main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def _bundle_index_html(
    *,
    document_title: str,
    entries: list[dict[str, Any]],
) -> str:
    list_items = "\n".join(
        f'      <li><a href="{html.escape(entry["path"])}">{html.escape(entry["title"])}</a></li>'
        for entry in entries
    )
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            f"  <title>{html.escape(document_title)}</title>",
            "</head>",
            "<body>",
            f"  <h1>{html.escape(document_title)}</h1>",
            "  <ol>",
            list_items,
            "  </ol>",
            "</body>",
            "</html>",
            "",
        ]
    )


def _heading_family_key(text: str) -> str | None:
    normalized = re.sub(r"\s+", " ", text.strip())
    if not normalized or not HEADING_FAMILY_NUMBER_RE.search(normalized):
        return None
    family = HEADING_FAMILY_NUMBER_RE.sub("#", normalized).casefold().strip(" .:-")
    if "#" not in family or not re.search(r"[a-z]", family):
        return None
    return family


def _apply_heading_level_normalization(page_rows: list[dict[str, Any]]) -> tuple[list[BeautifulSoup], dict[str, Any]]:
    soups = [BeautifulSoup(row["html"], "html.parser") for row in page_rows]
    family_groups: dict[str, list[dict[str, Any]]] = {}

    for page_index, soup in enumerate(soups, start=1):
        for heading in soup.find_all(HEADING_TAG_RE):
            text = html_to_text(str(heading))
            family_key = _heading_family_key(text)
            if not family_key:
                continue
            family_groups.setdefault(family_key, []).append(
                {
                    "heading": heading,
                    "level": int(heading.name[1]),
                    "text": text,
                    "page_number": page_index,
                }
            )

    families_report: list[dict[str, Any]] = []
    adjusted_heading_count = 0

    for family_key, entries in family_groups.items():
        levels = [entry["level"] for entry in entries]
        unique_levels = sorted(set(levels))
        if len(entries) < 3 or len(unique_levels) <= 1:
            continue
        level_counts = Counter(levels)
        max_count = max(level_counts.values())
        canonical_level = min(
            level for level, count in level_counts.items() if count == max_count
        )
        family_adjustments = 0
        for entry in entries:
            if entry["level"] == canonical_level:
                continue
            entry["heading"].name = f"h{canonical_level}"
            family_adjustments += 1
        if family_adjustments == 0:
            continue
        adjusted_heading_count += family_adjustments
        families_report.append(
            {
                "family_key": family_key,
                "canonical_level": canonical_level,
                "levels_seen": unique_levels,
                "pages": sorted({entry["page_number"] for entry in entries}),
                "sample_headings": [entry["text"] for entry in entries[:5]],
                "adjusted_heading_count": family_adjustments,
            }
        )

    return soups, {
        "families": families_report,
        "families_touched": len(families_report),
        "adjusted_heading_count": adjusted_heading_count,
    }


def _build_choice_paragraph(soup: BeautifulSoup, tag, segment_html: str):
    fragment = BeautifulSoup(segment_html, "html.parser")
    new_tag = soup.new_tag(tag.name)
    for key, value in tag.attrs.items():
        new_tag[key] = value
    for child in list(fragment.contents):
        new_tag.append(child)
    return new_tag


def _split_choice_paragraphs(soups: list[BeautifulSoup]) -> dict[str, Any]:
    split_pages: list[dict[str, Any]] = []
    paragraphs_split = 0
    segments_emitted = 0

    for page_index, soup in enumerate(soups, start=1):
        page_split_count = 0
        page_segment_count = 0
        for paragraph in list(soup.find_all("p")):
            text = html_to_text(str(paragraph))
            if text.lower().count("turn to") < 2:
                continue
            inner_html = "".join(str(child) for child in paragraph.contents).strip()
            segments = [
                segment.strip()
                for segment in CHOICE_PARAGRAPH_SPLIT_RE.split(inner_html)
                if segment.strip()
            ]
            if len(segments) < 2:
                continue
            if not all(
                CHOICE_LEAD_RE.search(html_to_text(segment)) and "turn to" in html_to_text(segment).lower()
                for segment in segments
            ):
                continue
            for segment in segments:
                paragraph.insert_before(_build_choice_paragraph(soup, paragraph, segment))
            paragraph.extract()
            page_split_count += 1
            page_segment_count += len(segments)
        if page_split_count:
            paragraphs_split += page_split_count
            segments_emitted += page_segment_count
            split_pages.append(
                {
                    "page_number": page_index,
                    "paragraphs_split": page_split_count,
                    "segments_emitted": page_segment_count,
                }
            )

    return {
        "pages": split_pages,
        "pages_touched": [row["page_number"] for row in split_pages],
        "paragraphs_split": paragraphs_split,
        "segments_emitted": segments_emitted,
    }


def _apply_html_normalization(page_rows: list[dict[str, Any]]) -> dict[str, Any]:
    soups, heading_report = _apply_heading_level_normalization(page_rows)
    choice_report = _split_choice_paragraphs(soups)

    changed_pages: list[int] = []
    text_mismatch_pages: list[int] = []
    for row, soup in zip(page_rows, soups, strict=True):
        original_html = row["html"]
        normalized_html = soup.decode_contents()
        if _text_identity(original_html) != _text_identity(normalized_html):
            text_mismatch_pages.append(row["page_number"])
            continue
        if normalized_html != original_html:
            row["html"] = normalized_html
            changed_pages.append(row["page_number"])

    return {
        "heading_level_normalization": heading_report,
        "choice_paragraph_split": choice_report,
        "pages_changed": changed_pages,
        "text_mismatch_pages": text_mismatch_pages,
    }


def _build_doc_web_bundle(
    page_contexts: list[dict[str, Any]],
    *,
    input_pdf: Path,
    run_id: str,
    module_id: str,
    created_at: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, str], list[dict[str, Any]]]:
    page_rows = [context["page_row"] for context in page_contexts]
    document_title = _bundle_document_title(page_rows, input_pdf)
    entries: list[dict[str, Any]] = []
    provenance_rows: list[dict[str, Any]] = []
    page_files: dict[str, str] = {}
    runtime_trace: list[dict[str, Any]] = []

    entry_ids = [f"page-{index:03d}" for index in range(1, len(page_contexts) + 1)]
    confidence_policy = (
        "confidence=1.0 when Marker page_stats report direct pdftext extraction with zero LLM requests; "
        "otherwise confidence=null."
    )

    for index, context in enumerate(page_contexts, start=1):
        page_row = context["page_row"]
        page_stats = context["page_stats"]
        entry_id = entry_ids[index - 1]
        prev_entry_id = entry_ids[index - 2] if index > 1 else None
        next_entry_id = entry_ids[index] if index < len(entry_ids) else None
        extraction_method = page_stats.get("text_extraction_method")
        llm_request_count = (page_stats.get("block_metadata") or {}).get("llm_request_count", 0)

        soup = BeautifulSoup(page_row["html"], "html.parser")
        tags = [tag for tag in _iter_provenance_tags(soup) if _should_emit_provenance_tag(tag)]
        for ordinal, tag in enumerate(tags, start=1):
            block_id = f"blk-{entry_id}-{ordinal:04d}"
            tag["id"] = block_id
            source_element_id = tag.get("data-source-element-id") or f"{entry_id}-dom-{ordinal:04d}"
            confidence = float(tag.get("data-source-confidence")) if tag.get("data-source-confidence") else None
            provenance_row = DocWebProvenanceBlock(
                schema_version="doc_web_provenance_block_v1",
                module_id=module_id,
                run_id=run_id,
                created_at=created_at,
                block_id=block_id,
                entry_id=entry_id,
                block_kind=_block_kind_for_tag(tag.name),
                source_page_number=int(tag.get("data-source-page-number") or page_row["page_number"]),
                source_element_ids=[source_element_id],
                source_printed_page_number=page_row.get("printed_page_number"),
                source_printed_page_label=page_row.get("printed_page_number_text"),
                source_bbox=_bbox_from_attr(tag.get("data-source-bbox")),
                confidence=confidence,
                text_quote=_text_quote_for_tag(tag, _block_kind_for_tag(tag.name)),
            )
            provenance_rows.append(provenance_row.model_dump(exclude_none=True))

        entry_title = _page_title(page_row["html"], page_row["page_number"])
        entries.append(
            {
                "entry_id": entry_id,
                "kind": "page",
                "title": entry_title,
                "path": f"{entry_id}.html",
                "order": index,
                "prev_entry_id": prev_entry_id,
                "next_entry_id": next_entry_id,
                "source_pages": [page_row["page_number"]],
                "printed_pages": (
                    [page_row["printed_page_number"]]
                    if isinstance(page_row.get("printed_page_number"), int)
                    else []
                ),
            }
        )
        page_files[entry_id] = _bundle_page_html(
            document_title=document_title,
            entry_title=entry_title,
            body_html=soup.decode_contents(),
            prev_entry_id=prev_entry_id,
            next_entry_id=next_entry_id,
        )
        runtime_trace.append(
            {
                "entry_id": entry_id,
                "page_number": page_row["page_number"],
                "source_element_count": len(
                    [tag for tag in tags if tag.get("data-source-element-id")]
                ),
                "text_extraction_method": extraction_method,
                "llm_request_count": llm_request_count,
                "processing_step": tags[0].get("data-processing-step") if tags else module_id,
                "confidence_policy": confidence_policy,
            }
        )

    manifest = DocWebBundleManifest(
        schema_version="doc_web_bundle_manifest_v1",
        module_id=module_id,
        run_id=run_id,
        created_at=created_at,
        document_id=input_pdf.stem,
        title=document_title,
        creator="",
        source_artifact=str(input_pdf),
        entries=entries,
        reading_order=entry_ids,
        asset_roots=[],
        provenance_path="provenance/blocks.jsonl",
    ).model_dump(exclude_none=True)
    return manifest, provenance_rows, page_files, runtime_trace


def normalize_marker_document(
    document_payload: dict[str, Any],
    *,
    input_pdf: Path,
    marker_json: Path,
    marker_meta: Path | None,
    run_id: str,
    module_id: str,
    created_at: str,
    pdftotext_text: str,
    processing_step: str = "marker_lite_api.page_html_v1",
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
    list[dict[str, Any]],
    dict[str, Any],
    dict[str, Any],
]:
    page_rows: list[dict[str, Any]] = []
    page_contexts: list[dict[str, Any]] = []
    block_rows: list[dict[str, Any]] = []
    page_texts: list[str] = []
    page_blocks = _page_blocks(document_payload)
    marker_meta_payload = read_json(marker_meta) if marker_meta else None
    page_stats_map = _page_stats_by_page_id(marker_meta_payload)

    for page_index, page_block in enumerate(page_blocks, start=1):
        page_stats = page_stats_map.get(page_index - 1, {})
        extraction_method = page_stats.get("text_extraction_method")
        llm_request_count = (page_stats.get("block_metadata") or {}).get("llm_request_count", 0)
        block_confidence = 1.0 if extraction_method == "pdftext" and llm_request_count == 0 else None
        block_index = _build_block_index(page_block)
        resolved_html = _resolve_block_html(
            page_block,
            block_index,
            {},
            page_number=page_index,
            extraction_method=extraction_method,
            processing_step=processing_step,
            confidence=block_confidence,
        )
        page_row = {
            "schema_version": "page_html_v1",
            "module_id": module_id,
            "run_id": run_id,
            "source": [str(marker_json), str(input_pdf)] + ([str(marker_meta)] if marker_meta else []),
            "created_at": created_at,
            "page": page_index,
            "page_number": page_index,
            "original_page_number": page_index,
            "raw_html": page_block.get("html") or "",
            "html": resolved_html,
        }
        page_rows.append(page_row)
        page_contexts.append({"page_row": page_row, "page_stats": page_stats})
        block_rows.extend(
            _block_inventory_rows(
                page_block,
                page_number=page_index,
                run_id=run_id,
                created_at=created_at,
            )
        )

    normalization_report = _apply_html_normalization(page_rows)
    page_texts = [html_to_text(row["html"]) for row in page_rows]
    manifest, provenance_rows, page_files, runtime_trace = _build_doc_web_bundle(
        page_contexts,
        input_pdf=input_pdf,
        run_id=run_id,
        module_id=module_id,
        created_at=created_at,
    )
    combined_text = "\n".join(page_texts)
    summary = {
        "schema_version": "story168_marker_page_html_v1",
        "story_id": 168,
        "module_id": module_id,
        "run_id": run_id,
        "input_artifacts": {
            "input_pdf": str(input_pdf),
            "marker_json": str(marker_json),
            "marker_meta": str(marker_meta) if marker_meta else None,
        },
        "signals": {
            "page_count": len(page_rows),
            "block_inventory_count": len(block_rows),
            "doc_web_bundle_entry_count": len(manifest["entries"]),
            "doc_web_provenance_block_count": len(provenance_rows),
            "nonempty_html_pages": sum(1 for row in page_rows if html_to_text(row["html"])),
            "token_coverage_vs_pdftotext": token_coverage(pdftotext_text, combined_text),
            "pages_with_section_headers": sum(
                1
                for row in page_rows
                if any(tag in row["html"] for tag in ("<h1", "<h2", "<h3"))
            ),
        },
        "provenance_notes": [
            "pages_html.jsonl stays page-level for direct surface comparison.",
            "doc_web_bundle/provenance/blocks.jsonl carries contract-aligned block provenance using Marker block ids and bboxes.",
            "Confidence is policy-derived as 1.0 only for direct pdftext pages with zero Marker LLM requests; otherwise it remains null.",
        ],
    }
    bundle = {
        "manifest": manifest,
        "provenance_rows": provenance_rows,
        "page_files": page_files,
        "runtime_trace": runtime_trace,
        "document_title": manifest["title"],
    }
    return page_rows, block_rows, bundle, runtime_trace, summary, normalization_report


def write_marker_outputs(
    outdir: Path,
    *,
    artifact_name: str,
    page_rows: list[dict[str, Any]],
    block_rows: list[dict[str, Any]],
    bundle: dict[str, Any],
    runtime_trace: list[dict[str, Any]],
    summary: dict[str, Any],
    normalization_report: dict[str, Any],
) -> dict[str, str]:
    pages_path = outdir / artifact_name
    blocks_path = outdir / "marker_blocks.jsonl"
    summary_path = outdir / "summary.json"
    runtime_trace_path = outdir / "runtime_trace.json"
    normalization_report_path = outdir / "normalization_report.json"
    bundle_dir = outdir / "doc_web_bundle"
    bundle_manifest_path = bundle_dir / "manifest.json"
    bundle_index_path = bundle_dir / "index.html"
    bundle_provenance_path = bundle_dir / "provenance" / "blocks.jsonl"

    save_jsonl(str(pages_path), page_rows)
    save_jsonl(str(blocks_path), block_rows)
    save_json(str(runtime_trace_path), runtime_trace)
    save_json(str(normalization_report_path), normalization_report)
    save_json(str(bundle_manifest_path), bundle["manifest"])
    save_jsonl(str(bundle_provenance_path), bundle["provenance_rows"])
    write_text(
        bundle_index_path,
        _bundle_index_html(
            document_title=bundle["document_title"],
            entries=bundle["manifest"]["entries"],
        ),
    )
    for entry_id, page_html in bundle["page_files"].items():
        write_text(bundle_dir / f"{entry_id}.html", page_html)

    output_artifacts = {
        "pages_html": str(pages_path),
        "marker_blocks": str(blocks_path),
        "runtime_trace": str(runtime_trace_path),
        "normalization_report": str(normalization_report_path),
        "doc_web_bundle_manifest": str(bundle_manifest_path),
        "doc_web_bundle_provenance": str(bundle_provenance_path),
        "summary": str(summary_path),
    }
    summary["output_artifacts"] = output_artifacts
    save_json(str(summary_path), summary)
    return output_artifacts
