from __future__ import annotations

from typing import Any

from .utils import (
    load_settings,
    ensure_dir,
    save_json,
    save_jsonl,
    append_jsonl,
    read_jsonl,
    ProgressLogger,
    PROGRESS_EVENT_SCHEMA,
    PROGRESS_STATUS_VALUES,
    validate_progress_event,
)

_OCR_EXPORTS = {
    "render_pdf",
    "run_ocr",
    "run_ocr_with_word_data",
}


def __getattr__(name: str) -> Any:
    if name in _OCR_EXPORTS:
        from . import ocr as _ocr

        value = getattr(_ocr, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "load_settings",
    "ensure_dir",
    "save_json",
    "save_jsonl",
    "append_jsonl",
    "read_jsonl",
    "ProgressLogger",
    "PROGRESS_EVENT_SCHEMA",
    "PROGRESS_STATUS_VALUES",
    "validate_progress_event",
    "render_pdf",
    "run_ocr",
    "run_ocr_with_word_data",
]
