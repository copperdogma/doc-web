"""Utilities for scoring handwritten-note transcription against a checked-in transcript."""

from __future__ import annotations

import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup


PAGE_SEPARATOR = "===PAGE==="


def load_transcript_pages(path: str | Path) -> list[str]:
    text = Path(path).read_text(encoding="utf-8")
    return [chunk.strip() for chunk in text.split(PAGE_SEPARATOR) if chunk.strip()]


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    text = soup.get_text("\n")
    text = text.replace("\xa0", " ")
    return text.strip()


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = (
        text.replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2013", "-")
        .replace("\u2014", "-")
    )
    return re.sub(r"\s+", " ", text.strip().lower())


def score_text_pair(expected: str, actual: str) -> dict[str, Any]:
    expected_norm = normalize_text(expected)
    actual_norm = normalize_text(actual)
    ratio = SequenceMatcher(None, expected_norm, actual_norm).ratio()
    return {
        "ratio": round(ratio, 6),
        "exact_match": expected_norm == actual_norm,
        "expected_length": len(expected_norm),
        "actual_length": len(actual_norm),
        "expected_preview": expected.strip()[:160],
        "actual_preview": actual.strip()[:160],
    }


def score_page_html_artifact(transcript_path: str | Path, artifact_path: str | Path) -> dict[str, Any]:
    transcript_pages = load_transcript_pages(transcript_path)
    rows = [
        json.loads(line)
        for line in Path(artifact_path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    pages: list[dict[str, Any]] = []
    actual_pages_text: list[str] = []
    for page_index, expected in enumerate(transcript_pages, start=1):
        row = next((row for row in rows if row.get("page_number") == page_index), None)
        actual_text = html_to_text(row.get("html", "")) if row else ""
        actual_pages_text.append(actual_text)
        score = score_text_pair(expected, actual_text)
        score["page_number"] = page_index
        score["artifact_page_found"] = row is not None
        if row is not None:
            score["artifact_metrics"] = {
                key: row.get(key)
                for key in ("ocr_quality", "ocr_integrity", "continuation_risk")
            }
        pages.append(score)

    overall = score_text_pair("\n\n".join(transcript_pages), "\n\n".join(actual_pages_text))
    missing_pages = [page["page_number"] for page in pages if not page["artifact_page_found"]]
    extra_pages = sorted(
        row.get("page_number")
        for row in rows
        if row.get("page_number") not in {page["page_number"] for page in pages}
    )

    return {
        "transcript_path": str(Path(transcript_path)),
        "artifact_path": str(Path(artifact_path)),
        "page_count": len(transcript_pages),
        "missing_pages": missing_pages,
        "extra_pages": extra_pages,
        "overall_ratio": overall["ratio"],
        "overall_exact_match": overall["exact_match"],
        "page_min_ratio": min((page["ratio"] for page in pages), default=0.0),
        "exact_page_matches": sum(1 for page in pages if page["exact_match"]),
        "pages": pages,
    }


def get_assert(output: str, context: dict[str, Any]) -> dict[str, Any]:
    vars_dict = context.get("vars", {})
    expected_text = vars_dict.get("expected_text")
    expected_path = vars_dict.get("expected_path")
    if expected_text is None and expected_path is None:
        return {"pass": False, "score": 0.0, "reason": "Missing expected_text or expected_path"}

    if expected_text is None:
        expected_text = Path(expected_path).read_text(encoding="utf-8")

    score = score_text_pair(expected_text, html_to_text(output))
    min_ratio = float(vars_dict.get("min_ratio", 0.99))
    passed = score["ratio"] >= min_ratio
    reason = (
        f"ratio={score['ratio']:.6f}, exact_match={score['exact_match']}, "
        f"expected_len={score['expected_length']}, actual_len={score['actual_length']}"
    )
    return {"pass": passed, "score": score["ratio"], "reason": reason}
