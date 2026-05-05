from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from doc_web import __version__
from doc_web.preview_bundle import write_bundle
from doc_web.preview_content_hint import build_content_hint
from doc_web.preview_docx import docx_preview
from doc_web.preview_images import image_directory_preview
from doc_web.preview_pdf import pdf_preview
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
    utc_now,
)
from doc_web.runtime_contract import build_runtime_contract
from schemas import DocWebPreviewMetadata, DocWebPreviewSelectorMap


def _build_source_preview(
    *,
    source_path: Path,
    max_sample_units: int,
    max_chars_per_block: int,
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
        preview = pdf_preview(
            source_path=source_path,
            max_sample_units=max_sample_units,
            max_chars_per_block=max_chars_per_block,
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
    events: list[dict[str, Any]] = []
    source_path = input_path.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    created_at = utc_now()
    preview_fingerprint = build_runtime_contract()["preview_contract_fingerprint"]

    add_status(
        events,
        stage="accepted",
        started_at=started_at,
        message="Accepted preview request",
    )
    check_timeout(started_at, timeout_seconds)

    source_sha256 = sha256_source(source_path)
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
        )
    )

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
        document_title=facts.get("metadata_title") or source_path.stem,
        source_path=source_path,
        created_at=created_at,
        run_id=run_id,
    )
    save_jsonl(out_dir / PARSED_UNITS_PATH, parsed_units)

    selector_map = DocWebPreviewSelectorMap(
        schema_version="doc_web_preview_selector_map_v1",
        module_id=MODULE_ID,
        run_id=run_id,
        created_at=created_at,
        source_artifact=str(source_path),
        source_sha256=source_sha256,
        preview_contract_fingerprint=preview_fingerprint,
        mappings=selector_mappings,
    ).model_dump(exclude_none=True)
    save_json(out_dir / SELECTOR_MAP_PATH, selector_map)

    runtime_options = {
        "timeout_seconds": timeout_seconds,
        "usable_deadline_seconds": usable_deadline_seconds,
        "max_sample_units": max_sample_units,
        "max_chars_per_block": max_chars_per_block,
        "content_hint_mode": content_hint_mode,
        "content_hint_model": content_hint_model,
        "content_hint_timeout_seconds": content_hint_timeout_seconds,
    }
    cache_identity = {
        "source_artifact": str(source_path),
        "source_sha256": source_sha256,
        "doc_web_version": __version__,
        "parser_settings": parser_settings,
        "runtime_options": runtime_options,
        "preview_contract_fingerprint": preview_fingerprint,
        "reusable_artifacts": {
            "parsed_units": PARSED_UNITS_PATH,
            "selector_map": SELECTOR_MAP_PATH,
        },
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
    cache_identity["content_hint"] = {
        "mode": content_hint_mode,
        "effective_mode": effective_hint_mode,
        "provider": content_hint.get("summary_provider"),
        "model": content_hint.get("summary_model") or content_hint_model,
        "prompt_version": content_hint.get("summary_prompt_version"),
        "sample_sha256": content_hint.get("sample_sha256"),
        "cache_key": content_hint.get("cache_key"),
        "fallback_reason": content_hint.get("fallback_reason"),
        "requested_timeout_seconds": content_hint_timeout_seconds,
        "effective_timeout_seconds": round(effective_hint_timeout_seconds, 3),
    }
    save_json(out_dir / CACHE_IDENTITY_PATH, cache_identity)

    add_status(
        events,
        stage="preview_ready",
        started_at=started_at,
        message="Preview bundle ready",
        artifact=str((out_dir / "manifest.json").resolve()),
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
        source_artifact=str(source_path),
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


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a latency-bound doc-web preview bundle."
    )
    parser.add_argument("--input", required=True, help="Raw source document path")
    parser.add_argument(
        "--out-dir", required=True, help="Output preview bundle directory"
    )
    parser.add_argument(
        "--max-sample-units",
        type=int,
        default=3,
        help="Maximum pages/entries to sample",
    )
    parser.add_argument(
        "--timeout-seconds", type=float, default=8.0, help="Hard synchronous timeout"
    )
    parser.add_argument(
        "--usable-deadline-seconds",
        type=float,
        default=3.0,
        help="Target deadline for a usable preview or honest deferred response",
    )
    parser.add_argument("--max-chars-per-block", type=int, default=1200)
    parser.add_argument(
        "--content-hint-mode",
        choices=["auto", "ai", "deterministic"],
        default="auto",
        help=(
            "How to produce high-level content hints. 'auto' uses a bounded "
            "cheap-model pass when DOC_WEB_OPENAI_API_KEY is configured, then "
            "falls back to deterministic hints."
        ),
    )
    parser.add_argument(
        "--content-hint-model",
        default="gpt-4.1-nano",
        help="OpenAI model for ai/auto content hints",
    )
    parser.add_argument(
        "--content-hint-timeout-seconds",
        type=float,
        default=0.75,
        help="Timeout for the optional AI content-hint call",
    )
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--json", action="store_true", help="Emit JSON summary only")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    summary = build_preview(
        input_path=Path(args.input),
        out_dir=Path(args.out_dir),
        max_sample_units=args.max_sample_units,
        timeout_seconds=args.timeout_seconds,
        usable_deadline_seconds=args.usable_deadline_seconds,
        max_chars_per_block=args.max_chars_per_block,
        content_hint_mode=args.content_hint_mode,
        content_hint_model=args.content_hint_model,
        content_hint_timeout_seconds=args.content_hint_timeout_seconds,
        run_id=args.run_id,
    )
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
