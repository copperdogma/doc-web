from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from doc_web import __version__
from doc_web.preview_bundle import write_bundle
from doc_web.preview_content_hint import build_content_hint
from doc_web.preview_docx import docx_preview
from doc_web.preview_identity import build_cache_identity, bundle_fingerprint
from doc_web.preview_images import image_directory_preview
from doc_web.preview_pdf import (
    PDF_OCR_ENGINE,
    PDF_OCR_MAX_DIMENSION,
    PDF_OCR_RASTER_DPI,
    PDF_OCR_RASTERIZER,
    PDF_OCR_TIMEOUT_SECONDS,
    pdf_preview,
)
from doc_web.preview_support import (
    CACHE_IDENTITY_PATH,
    INDEX_PATH,
    METADATA_PATH,
    MODULE_ID,
    PARSED_UNITS_PATH,
    PROVENANCE_PATH,
    SELECTOR_MAP_PATH,
    STATUS_PATH,
    add_status,
    check_timeout,
    save_json,
    save_jsonl,
    sha256_source,
    source_reference,
    portable_metadata_text,
    portable_run_id,
    utc_now,
)
from doc_web.runtime_contract import build_runtime_contract
from schemas import DocWebPreviewMetadata, DocWebPreviewSelectorMap


def _build_source_preview(
    *,
    source_path: Path,
    max_sample_units: int,
    max_chars_per_block: int,
    ocr_deadline_at: float | None,
) -> tuple[
    list[Any],
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[str],
    str,
    dict[str, Any],
]:
    suffix = source_path.suffix.lower()
    parser_settings: dict[str, Any] = {
        "max_sample_units": max_sample_units,
        "max_chars_per_block": max_chars_per_block,
    }
    if source_path.is_dir():
        parser_settings["parser"] = "image-directory"
        parser_settings["ocr_engine"] = "tesseract"
        parser_settings["ocr_timeout_seconds"] = 2.0
        parser_settings["ocr_max_dimension"] = 1600
        parser_settings["ocr_sample_limit"] = min(max_sample_units, 2)
        preview = image_directory_preview(
            source_path=source_path,
            max_sample_units=max_sample_units,
            max_chars_per_block=max_chars_per_block,
            ocr_sample_limit=min(max_sample_units, 2),
        )
    elif suffix == ".pdf":
        parser_settings["parser"] = "pypdf"
        parser_settings["ocr_engine"] = PDF_OCR_ENGINE
        parser_settings["ocr_rasterizer"] = PDF_OCR_RASTERIZER
        parser_settings["ocr_raster_dpi"] = PDF_OCR_RASTER_DPI
        parser_settings["ocr_timeout_seconds"] = PDF_OCR_TIMEOUT_SECONDS
        parser_settings["ocr_max_dimension"] = PDF_OCR_MAX_DIMENSION
        preview = pdf_preview(
            source_path=source_path,
            max_sample_units=max_sample_units,
            max_chars_per_block=max_chars_per_block,
            ocr_deadline_at=ocr_deadline_at,
        )
    elif suffix == ".docx":
        parser_settings["parser"] = "python-docx"
        preview = docx_preview(
            source_path=source_path,
            max_sample_units=max_sample_units,
        )
    else:
        raise SystemExit(f"Unsupported preview input type: {suffix or '<none>'}")
    return (*preview, parser_settings)


def _effective_content_hint_mode(content_hint: dict[str, Any]) -> str:
    if content_hint.get("summary_provider"):
        return "ai"
    return "deterministic"


def _source_private_identifiers(source_path: Path) -> tuple[str, str]:
    return (source_path.name, source_path.stem)


def _sanitize_metadata_facts(
    facts: dict[str, Any], *, source_path: Path
) -> dict[str, Any]:
    sanitized = dict(facts)
    private_identifiers = _source_private_identifiers(source_path)
    sanitized["metadata_title"] = portable_metadata_text(
        sanitized.get("metadata_title"),
        private_identifiers=private_identifiers,
    )
    sanitized["metadata_creator"] = portable_metadata_text(
        sanitized.get("metadata_creator"),
        private_identifiers=private_identifiers,
    )
    return sanitized


def build_preview(
    *,
    input_path: Path,
    out_dir: Path,
    max_sample_units: int = 3,
    timeout_seconds: float = 8.0,
    usable_deadline_seconds: float = 3.0,
    max_chars_per_block: int = 1200,
    content_hint_mode: str = "auto",
    content_hint_model: str = "gpt-4.1-nano",
    content_hint_timeout_seconds: float = 0.75,
    run_id: str | None = None,
) -> dict[str, Any]:
    started_at = time.perf_counter()
    timeout_seconds = float(timeout_seconds)
    usable_deadline_seconds = float(usable_deadline_seconds)
    content_hint_timeout_seconds = float(content_hint_timeout_seconds)
    events: list[dict[str, Any]] = []
    source_path = input_path.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    created_at = utc_now()
    run_id = portable_run_id(run_id)
    runtime_contract = build_runtime_contract()
    preview_fingerprint = runtime_contract["preview_contract_fingerprint"]

    add_status(
        events,
        stage="accepted",
        started_at=started_at,
        message="Accepted preview request",
    )
    check_timeout(started_at, timeout_seconds)

    source_sha256 = sha256_source(source_path)
    source_ref = source_reference(source_sha256)
    add_status(
        events,
        stage="preparing_pages",
        started_at=started_at,
        message="Prepared source identity",
        detail={"source_sha256": source_sha256},
    )
    check_timeout(started_at, timeout_seconds)

    add_status(
        events,
        stage="detecting_text_or_ocr_need",
        started_at=started_at,
        message=f"Detected {'image-directory' if source_path.is_dir() else source_path.suffix.lower()}",
    )
    entries, facts, included, skipped, warnings, coverage_state, parser_settings = (
        _build_source_preview(
            source_path=source_path,
            max_sample_units=max_sample_units,
            max_chars_per_block=max_chars_per_block,
            ocr_deadline_at=started_at + max(0.0, timeout_seconds - 0.75),
        )
    )
    facts = _sanitize_metadata_facts(facts, source_path=source_path)

    add_status(
        events,
        stage="reading_sample",
        started_at=started_at,
        message="Read preview sample",
        detail={"coverage_state": coverage_state, "entry_count": len(entries)},
    )
    check_timeout(started_at, timeout_seconds)

    add_status(
        events,
        stage="building_preview_html",
        started_at=started_at,
        message="Building preview bundle",
    )
    manifest, provenance_rows, selector_mappings, parsed_units = write_bundle(
        out_dir=out_dir,
        entries=entries,
        document_title=facts.get("metadata_title") or "Document Preview",
        source_path=source_path,
        source_ref=source_ref,
        document_id=f"doc-{source_sha256[:12]}",
        created_at=created_at,
        run_id=run_id,
    )
    save_jsonl(out_dir / PARSED_UNITS_PATH, parsed_units)

    selector_map = DocWebPreviewSelectorMap(
        schema_version="doc_web_preview_selector_map_v1",
        module_id=MODULE_ID,
        run_id=run_id,
        created_at=created_at,
        source_artifact=source_ref,
        source_sha256=source_sha256,
        preview_contract_fingerprint=preview_fingerprint,
        mappings=selector_mappings,
    ).model_dump(exclude_none=True)
    save_json(out_dir / SELECTOR_MAP_PATH, selector_map)

    bundle_fingerprint_value = bundle_fingerprint(
        manifest=manifest,
        provenance_rows=provenance_rows,
        selector_mappings=selector_mappings,
        parsed_units=parsed_units,
    )

    runtime_options = {
        "timeout_seconds": timeout_seconds,
        "usable_deadline_seconds": usable_deadline_seconds,
        "max_sample_units": max_sample_units,
        "max_chars_per_block": max_chars_per_block,
        "content_hint_mode": content_hint_mode,
        "content_hint_model": content_hint_model,
        "content_hint_timeout_seconds": content_hint_timeout_seconds,
    }
    elapsed_before_hint = time.perf_counter() - started_at
    remaining_hint_budget = max(
        0.0, usable_deadline_seconds - elapsed_before_hint - 0.5
    )
    effective_hint_mode = content_hint_mode
    if content_hint_mode == "auto" and facts.get("format") == "image_directory":
        effective_hint_mode = "deterministic"
        effective_hint_timeout_seconds = 0.0
    elif (
        content_hint_mode == "auto"
        and remaining_hint_budget < content_hint_timeout_seconds
    ):
        effective_hint_mode = "deterministic"
        effective_hint_timeout_seconds = 0.0
    else:
        effective_hint_timeout_seconds = min(
            content_hint_timeout_seconds, remaining_hint_budget
        )
    if effective_hint_timeout_seconds < 0.25 and effective_hint_mode == "ai":
        effective_hint_timeout_seconds = 0.25
    content_hint = build_content_hint(
        facts=facts,
        parsed_units=parsed_units,
        coverage_state=coverage_state,
        warnings=warnings,
        mode=effective_hint_mode,
        ai_model=content_hint_model,
        ai_timeout_seconds=effective_hint_timeout_seconds,
        source_sha256=source_sha256,
    )
    content_hint_identity = {
        "mode": content_hint_mode,
        "effective_mode": _effective_content_hint_mode(content_hint),
        "provider": content_hint.get("summary_provider"),
        "model": content_hint.get("summary_model") or content_hint_model,
        "prompt_version": content_hint.get("summary_prompt_version"),
        "sample_sha256": content_hint.get("sample_sha256"),
        "cache_key": content_hint.get("cache_key"),
        "fallback_reason": content_hint.get("fallback_reason"),
        "requested_timeout_seconds": float(content_hint_timeout_seconds),
    }
    cache_identity = build_cache_identity(
        source_ref=source_ref,
        source_sha256=source_sha256,
        facts=facts,
        doc_web_version=__version__,
        doc_web_ref=runtime_contract["runtime_version"],
        parser_settings=parser_settings,
        runtime_options=runtime_options,
        preview_contract_fingerprint=preview_fingerprint,
        bundle_fingerprint_value=bundle_fingerprint_value,
        content_hint_identity=content_hint_identity,
    )
    save_json(out_dir / CACHE_IDENTITY_PATH, cache_identity)

    add_status(
        events,
        stage="preview_ready",
        started_at=started_at,
        message="Preview bundle ready",
        artifact="manifest.json",
        detail={"provenance_rows": len(provenance_rows)},
    )
    timing = {
        "first_status_ms": events[0]["elapsed_ms"],
        "preview_ready_ms": events[-1]["elapsed_ms"],
    }
    if (
        timing["preview_ready_ms"] > usable_deadline_seconds * 1000
        and coverage_state != "deferred"
    ):
        warnings.append("Preview exceeded the usable-preview latency target.")

    metadata = DocWebPreviewMetadata(
        schema_version="doc_web_preview_metadata_v1",
        module_id=MODULE_ID,
        run_id=run_id,
        created_at=created_at,
        status="preview_ready",
        coverage_state=coverage_state,
        source_artifact=source_ref,
        source_sha256=source_sha256,
        doc_web_version=__version__,
        preview_contract_fingerprint=preview_fingerprint,
        parser_settings=parser_settings,
        runtime_options=runtime_options,
        structural_facts=facts,
        content_hint=content_hint,
        included_units=included,
        skipped_units=skipped,
        warnings=warnings,
        unsupported_inferences=[
            "Preview text is non-final and must not be treated as extracted graph facts.",
            "OCR quality is not claimed unless confidence metadata is present for source text blocks.",
        ],
        status_events=events,
        timing_ms=timing,
        cache_identity=cache_identity,
        artifacts={
            "manifest": "manifest.json",
            "index": INDEX_PATH,
            "provenance": PROVENANCE_PATH,
            "metadata": METADATA_PATH,
            "status": STATUS_PATH,
            "selector_map": SELECTOR_MAP_PATH,
            "cache_identity": CACHE_IDENTITY_PATH,
            "parsed_units": PARSED_UNITS_PATH,
        },
    ).model_dump(exclude_none=True)
    save_json(out_dir / METADATA_PATH, metadata)
    save_jsonl(out_dir / STATUS_PATH, events)

    return {
        "bundle_dir": str(out_dir.resolve()),
        "manifest_path": str((out_dir / "manifest.json").resolve()),
        "metadata_path": str((out_dir / METADATA_PATH).resolve()),
        "provenance_path": str((out_dir / PROVENANCE_PATH).resolve()),
        "selector_map_path": str((out_dir / SELECTOR_MAP_PATH).resolve()),
        "cache_identity_path": str((out_dir / CACHE_IDENTITY_PATH).resolve()),
        "coverage_state": coverage_state,
        "entry_count": len(manifest["entries"]),
        "provenance_row_count": len(provenance_rows),
        "timing_ms": timing,
        "warnings": warnings,
        "content_hint": content_hint,
    }
