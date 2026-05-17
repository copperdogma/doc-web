from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


MODULE_ID = "doc_web_preview_v1"
METADATA_PATH = "preview_metadata.json"
STATUS_PATH = "preview_status.jsonl"
SELECTOR_MAP_PATH = "preview_to_full_selectors.json"
CACHE_IDENTITY_PATH = "cache/cache_identity.json"
PARSED_UNITS_PATH = "cache/parsed_units.jsonl"
PROVENANCE_PATH = "provenance/blocks.jsonl"
INDEX_PATH = "index.html"


class PreviewTimeout(RuntimeError):
    """Raised when the synchronous preview path exceeds its hard timeout."""


@dataclass
class PreviewBlock:
    kind: str
    text: str
    source_element_ids: list[str]
    source_page_number: int | None = None
    confidence: float | None = None
    html_text: str | None = None


@dataclass
class PreviewEntry:
    entry_id: str
    kind: str
    title: str
    blocks: list[PreviewBlock] = field(default_factory=list)
    source_pages: list[int] = field(default_factory=list)
    status_message: str | None = None


def elapsed_ms(started_at: float) -> float:
    return round((time.perf_counter() - started_at) * 1000, 3)


def utc_now(*, timespec: str | None = None) -> str:
    now = datetime.now(timezone.utc)
    rendered = now.isoformat(timespec=timespec) if timespec else now.isoformat()
    return rendered.replace("+00:00", "Z")


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def save_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def check_timeout(started_at: float, timeout_seconds: float) -> None:
    if time.perf_counter() - started_at > timeout_seconds:
        raise PreviewTimeout(f"Preview exceeded hard timeout of {timeout_seconds:.3f}s")


def add_status(
    events: list[dict[str, Any]],
    *,
    stage: str,
    started_at: float,
    message: str,
    artifact: str | None = None,
    detail: dict[str, Any] | None = None,
) -> None:
    events.append(
        {
            "stage": stage,
            "elapsed_ms": elapsed_ms(started_at),
            "message": message,
            "artifact": artifact,
            "detail": detail or {},
        }
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_source(path: Path) -> str:
    if path.is_file():
        return sha256_file(path)
    if not path.is_dir():
        raise FileNotFoundError(path)

    digest = hashlib.sha256()
    for child in sorted(p for p in path.rglob("*") if p.is_file()):
        relative = child.relative_to(path).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        with child.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        digest.update(b"\0")
    return digest.hexdigest()


def stable_fingerprint(payload: Any) -> str:
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def source_reference(source_sha256: str) -> str:
    return f"sha256:{source_sha256}"


_SOURCE_FILE_EXTENSIONS = (
    "csv",
    "doc",
    "docx",
    "epub",
    "heic",
    "htm",
    "html",
    "jpeg",
    "jpg",
    "json",
    "jsonl",
    "md",
    "pdf",
    "png",
    "rtf",
    "tif",
    "tiff",
    "txt",
    "webp",
    "xls",
    "xlsx",
    "xml",
    "zip",
)


def portable_run_id(value: Any) -> str | None:
    if value is None:
        return None
    text = collapse_text(str(value))
    if not text:
        return None
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", text):
        raise ValueError("run_id must be a portable identifier")
    if Path(text).suffix.lower().lstrip(".") in _SOURCE_FILE_EXTENSIONS:
        raise ValueError("run_id must be a portable identifier")
    if _looks_like_private_source_identifier(text):
        raise ValueError("run_id must be a portable identifier")
    return text


def collapse_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def portable_metadata_text(
    value: Any,
    *,
    fallback: str | None = None,
    private_identifiers: Iterable[str] | None = None,
) -> str | None:
    text = collapse_text(str(value or ""))
    if not text:
        return fallback
    if _matches_private_identifier(text, private_identifiers or ()):
        return fallback
    if _looks_like_private_source_identifier(text):
        return fallback
    return text


def _matches_private_identifier(text: str, private_identifiers: Iterable[str]) -> bool:
    text_lower = text.lower()
    for identifier in private_identifiers:
        normalized = collapse_text(str(identifier or "")).lower()
        if not normalized:
            continue
        if text_lower == normalized:
            return True
        if re.search(
            rf"(?<![A-Za-z0-9_-]){re.escape(normalized)}(?![A-Za-z0-9_-])",
            text_lower,
        ):
            return True
    return False


def _looks_like_private_source_identifier(text: str) -> bool:
    if "://" in text:
        return True
    if "\\" in text:
        return True
    if text.startswith("/") or re.search(r"\b[A-Za-z]:[\\/]", text):
        return True
    if re.search(r"\b(?:s3|azure|gs|file):", text, re.IGNORECASE):
        return True
    extensions = "|".join(re.escape(ext) for ext in _SOURCE_FILE_EXTENSIONS)
    return bool(
        re.search(
            rf"(?i)(?<![A-Za-z0-9._-])[A-Za-z0-9][A-Za-z0-9._-]*"
            rf"\.(?:{extensions})(?![A-Za-z0-9])",
            text,
        )
    )


def paragraphs_from_text(value: str, *, max_chars_per_block: int) -> list[str]:
    chunks = [
        collapse_text(part)
        for part in re.split(r"(?:\r?\n){2,}|\r?\n", value or "")
        if collapse_text(part)
    ]
    paragraphs: list[str] = []
    for chunk in chunks:
        if len(chunk) <= max_chars_per_block:
            paragraphs.append(chunk)
            continue
        for start in range(0, len(chunk), max_chars_per_block):
            paragraphs.append(chunk[start : start + max_chars_per_block].strip())
    return [paragraph for paragraph in paragraphs if paragraph]
