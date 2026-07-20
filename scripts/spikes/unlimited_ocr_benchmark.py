#!/usr/bin/env python3
"""Benchmark Unlimited-OCR without changing the maintained OCR pipeline.

The script has two deliberately separate responsibilities:

* deterministic parsing, normalization, scoring, and adoption logic that can
  be tested without the 6.7 GB model; and
* an opt-in local inference command for the pinned exact-weight Transformers
  runtime.

Raw model text is always written before any parsing or Markdown conversion.
The parser treats page and grounding metadata as transport evidence, not as
permission to repair OCR text.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import hashlib
import html
import io
import json
import math
import os
import platform
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_ROOT = ROOT / "output" / "runs" / "story230-unlimited-ocr-benchmark-r1"
MODEL_REVISION = "ee63731b6461c8afcdcc7b15352e7d2ffecc2ead"
UNIVERSAL_REVISION = "bc00ae36def7fe8d23980adf5a901125fe0040a2"
OFFICIAL_SPACE_REVISION = "fece8f832e1c8691b375da69f810191c67840a3d"
WEIGHT_SHA256 = "2bc48a7a110061ea58fff65d3169367eebe3aee371ca6968dc2219c1b2855fc6"
WEIGHT_SIZE_BYTES = 6_672_547_120
SINGLE_PROMPT = "<image>document parsing."
MULTI_PROMPT = "<image>Multi page parsing."
MODEL_LICENSE = "MIT"
MODULE_ID = "unlimited_ocr_benchmark"
EXPECTED_ONWARD_CASES = frozenset({"alma", "arthur", "marie_louise"})
EXPECTED_HANDWRITING_CASES = frozenset({"barney", "alverson"})

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.scorers.handwritten_notes_transcription import (  # noqa: E402
    score_page_html_artifact,
)
from benchmarks.scorers.html_table_diff import (  # noqa: E402
    get_assert as score_html_table_diff,
)
from schemas import PageHtml  # noqa: E402


@dataclass(frozen=True)
class OnwardCase:
    case_id: str
    source_pages: tuple[int, ...]
    golden_path: Path
    incumbent_score: float

    @property
    def image_paths(self) -> tuple[Path, ...]:
        return tuple(
            ROOT / "input" / "onward-to-the-unknown-images" / f"Image{page:03d}.jpg"
            for page in self.source_pages
        )


@dataclass(frozen=True)
class HandwritingCase:
    case_id: str
    source_page: int
    image_path: Path
    transcript_path: Path


ONWARD_CASES: dict[str, OnwardCase] = {
    "alma": OnwardCase(
        "alma",
        (22, 23, 24, 25),
        ROOT / "benchmarks" / "golden" / "onward" / "alma.html",
        0.923,
    ),
    "arthur": OnwardCase(
        "arthur",
        (29, 30, 31, 32, 33, 34),
        ROOT / "benchmarks" / "golden" / "onward" / "arthur.html",
        0.989,
    ),
    "marie_louise": OnwardCase(
        "marie_louise",
        (79, 80, 81, 82, 83),
        ROOT / "benchmarks" / "golden" / "onward" / "marie_louise.html",
        0.995,
    ),
}

HANDWRITING_CASES: dict[str, HandwritingCase] = {
    "barney": HandwritingCase(
        "barney",
        1,
        ROOT / "testdata" / "handwritten-notes-barney-real-images" / "page-001.jpg",
        ROOT / "testdata" / "handwritten-notes-barney-real.txt",
    ),
    "alverson": HandwritingCase(
        "alverson",
        1,
        ROOT / "testdata" / "handwritten-notes-alverson-real-images" / "page-001.jpg",
        ROOT / "testdata" / "handwritten-notes-alverson-real.txt",
    ),
}

GROUNDING_RE = re.compile(
    r"<\|ref\|>(?P<label>.*?)<\|/ref\|>\s*"
    r"<\|det\|>(?P<coordinates>.*?)<\|/det\|>",
    re.DOTALL,
)
DET_ONLY_RE = re.compile(
    r"<\|det\|>\s*(?P<label>[A-Za-z_][\w-]*)\s*"
    r"(?P<coordinates>.*?)\s*<\|/det\|>",
    re.DOTALL,
)
PAGE_MARKER = "<PAGE>"
END_TOKEN = "<｜end▁of▁sentence｜>"
MAX_COORDINATE_LITERAL_BYTES = 32_768
MAX_COORDINATE_NESTING_DEPTH = 4
MAX_GROUNDING_BOXES = 256


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, value: Any) -> None:
    _write_text(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    _write_text(
        path,
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
    )


def _coerce_boxes(value: Any) -> tuple[list[list[float]], str | None]:
    """Return safe coordinate boxes and an error; never execute model text."""

    if not isinstance(value, (list, tuple)):
        return [], "coordinates must be a list or tuple"
    if len(value) == 4 and not any(isinstance(item, (list, tuple)) for item in value):
        candidates: list[Any] = [value]
    else:
        candidates = list(value)
    if not candidates:
        return [], "coordinates must contain at least one box"
    if len(candidates) > MAX_GROUNDING_BOXES:
        return [], f"coordinates exceed the {MAX_GROUNDING_BOXES}-box safety limit"

    boxes: list[list[float]] = []
    for candidate in candidates:
        if not isinstance(candidate, (list, tuple)) or len(candidate) != 4:
            return [], "each coordinate box must contain exactly four values"
        box: list[float] = []
        for coordinate in candidate:
            if isinstance(coordinate, bool) or not isinstance(coordinate, (int, float)):
                return [], "coordinate values must be finite numbers"
            numeric = float(coordinate)
            if not math.isfinite(numeric):
                return [], "coordinate values must be finite numbers"
            box.append(numeric)
        boxes.append(box)
    return boxes, None


def _coordinate_nesting_error(raw_coordinates: str) -> str | None:
    stack: list[str] = []
    closing_to_opening = {"]": "[", ")": "("}
    for character in raw_coordinates:
        if character in "[(":
            stack.append(character)
            if len(stack) > MAX_COORDINATE_NESTING_DEPTH:
                return (
                    "coordinates exceed the "
                    f"{MAX_COORDINATE_NESTING_DEPTH}-level nesting safety limit"
                )
        elif character in "])":
            if not stack or stack.pop() != closing_to_opening[character]:
                return "coordinates contain mismatched brackets"
    if stack:
        return "coordinates contain unclosed brackets"
    return None


def _parse_coordinates(raw_coordinates: str) -> tuple[list[list[float]], str | None]:
    coordinate_bytes = len(raw_coordinates.encode("utf-8"))
    if coordinate_bytes > MAX_COORDINATE_LITERAL_BYTES:
        return [], (
            f"coordinates exceed the {MAX_COORDINATE_LITERAL_BYTES}-byte safety limit"
        )
    nesting_error = _coordinate_nesting_error(raw_coordinates)
    if nesting_error is not None:
        return [], nesting_error
    try:
        parsed = ast.literal_eval(raw_coordinates)
    except (SyntaxError, ValueError, TypeError, MemoryError, RecursionError) as exc:
        return [], f"coordinates are not a bounded Python literal: {type(exc).__name__}"
    return _coerce_boxes(parsed)


def _parse_page(
    page_text: str,
    *,
    page_number: int,
    source_page: int,
    source_path: str | None,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    blocks: list[dict[str, Any]] = []
    malformed: list[dict[str, Any]] = []
    out_of_range: list[dict[str, Any]] = []

    ref_matches = list(GROUNDING_RE.finditer(page_text))
    ref_spans = [match.span() for match in ref_matches]
    grounding_matches = [
        (match.start(), match.group("label"), match.group("coordinates"))
        for match in ref_matches
    ]
    # DET_ONLY_RE also sees the <|det|> half of an adjacent ref/det pair.
    # Keep only genuinely det-only records so each emitted grounding record
    # appears exactly once in the provenance sidecar.
    grounding_matches.extend(
        (match.start(), match.group("label"), match.group("coordinates"))
        for match in DET_ONLY_RE.finditer(page_text)
        if not any(
            start <= match.start() and match.end() <= end for start, end in ref_spans
        )
    )
    grounding_matches.sort(key=lambda item: item[0])

    for match_index, (_, label, coordinates) in enumerate(grounding_matches, start=1):
        raw_coordinates = coordinates.strip()
        boxes, error = _parse_coordinates(raw_coordinates)
        if error is not None:
            malformed.append(
                {
                    "page": page_number,
                    "source_page": source_page,
                    "match": match_index,
                    "raw": raw_coordinates,
                    "reason": error,
                }
            )
        else:
            for box_index, box in enumerate(boxes, start=1):
                if any(value < 0 or value > 1000 for value in box):
                    out_of_range.append(
                        {
                            "page": page_number,
                            "source_page": source_page,
                            "match": match_index,
                            "box": box_index,
                            "raw": raw_coordinates,
                            "reason": "coordinate lies outside the documented 0..1000 range",
                        }
                    )
        blocks.append(
            {
                "label": label,
                "raw_coordinates": raw_coordinates,
                "boxes": boxes,
            }
        )

    clean_markdown = GROUNDING_RE.sub(lambda match: match.group("label"), page_text)
    clean_markdown = DET_ONLY_RE.sub("", clean_markdown).strip()
    page = {
        "page": page_number,
        "source_page": source_page,
        "raw_markdown": page_text.strip(),
        "clean_markdown": clean_markdown,
        "blocks": blocks,
    }
    if source_path is not None:
        page["source_path"] = source_path
    return page, malformed, out_of_range


def parse_grounded_output(
    raw: str,
    *,
    source_pages: Sequence[int] | None = None,
    source_paths: Sequence[str | Path] | None = None,
    expected_pages: int | None = None,
) -> dict[str, Any]:
    """Parse model output while preserving verbatim text and diagnostics.

    Multi-page output must begin each page with ``<PAGE>``. A single-page arm
    may omit the marker because Baidu's single-image reference does so.
    """

    raw = raw or ""
    if PAGE_MARKER in raw:
        chunks = raw.split(PAGE_MARKER)
        preamble = chunks[0]
        page_chunks = chunks[1:]
    else:
        preamble = ""
        page_chunks = [raw] if raw else []

    source_page_values = list(source_pages or [])
    if expected_pages is None and source_page_values:
        expected_pages = len(source_page_values)
    if expected_pages is None:
        expected_pages = len(page_chunks)
    if not source_page_values:
        source_page_values = list(range(1, max(expected_pages, len(page_chunks)) + 1))
    source_path_values = [str(path) for path in (source_paths or [])]

    pages: list[dict[str, Any]] = []
    malformed: list[dict[str, Any]] = []
    out_of_range: list[dict[str, Any]] = []
    for index, page_text in enumerate(page_chunks, start=1):
        source_page = (
            source_page_values[index - 1] if index <= len(source_page_values) else index
        )
        source_path = (
            source_path_values[index - 1] if index <= len(source_path_values) else None
        )
        page, page_malformed, page_out_of_range = _parse_page(
            page_text,
            page_number=index,
            source_page=source_page,
            source_path=source_path,
        )
        pages.append(page)
        malformed.extend(page_malformed)
        out_of_range.extend(page_out_of_range)

    return {
        "pages": pages,
        "page_count": len(pages),
        "preamble": preamble,
        "expected_source_pages": source_page_values[:expected_pages],
        "malformed_coordinates": malformed,
        "out_of_range_coordinates": out_of_range,
        "raw": raw,
    }


def validate_transport(
    parsed: dict[str, Any],
    *,
    expected_pages: int | None = None,
    expected_source_pages: Sequence[int] | None = None,
    require_page_markers: bool | None = None,
    truncated: bool = False,
    finish_reason: str | None = None,
) -> dict[str, Any]:
    """Validate page/order/grounding transport without judging OCR quality."""

    pages = list(parsed.get("pages") or [])
    raw = str(parsed.get("raw") or "")
    expected_sources = list(
        expected_source_pages or parsed.get("expected_source_pages") or []
    )
    if expected_pages is None and expected_sources:
        expected_pages = len(expected_sources)
    if expected_pages is None:
        expected_pages = len(pages)
    if require_page_markers is None:
        require_page_markers = expected_pages > 1

    errors: list[str] = []
    warnings: list[str] = []
    if not raw.strip():
        errors.append("empty model output")
    if require_page_markers and not raw.lstrip().startswith(PAGE_MARKER):
        errors.append("multi-page output does not begin with <PAGE>")
    if str(parsed.get("preamble") or "").strip():
        errors.append("non-whitespace preamble appears before the first <PAGE>")
    if len(pages) != expected_pages:
        errors.append(
            f"page count mismatch: expected {expected_pages}, got {len(pages)}"
        )

    actual_sources = [page.get("source_page") for page in pages]
    if expected_sources and actual_sources != expected_sources:
        errors.append(
            f"source page order mismatch: expected {expected_sources}, got {actual_sources}"
        )
    for page in pages:
        if not str(page.get("raw_markdown") or "").strip():
            errors.append(f"empty output for source page {page.get('source_page')}")

    malformed = list(parsed.get("malformed_coordinates") or [])
    out_of_range = list(parsed.get("out_of_range_coordinates") or [])
    if malformed:
        errors.append(f"malformed grounding coordinates: {len(malformed)}")
    if out_of_range:
        errors.append(f"out-of-range grounding coordinates: {len(out_of_range)}")
    if truncated:
        errors.append("generation was reported as truncated")
    if finish_reason and finish_reason.lower() in {
        "length",
        "max_length",
        "max_tokens",
        "token_limit",
    }:
        errors.append(f"generation finish reason indicates truncation: {finish_reason}")
    if raw.rstrip().endswith(END_TOKEN):
        warnings.append("raw output still contains the model end token")
    if pages and not any(page.get("blocks") for page in pages):
        warnings.append("output contains no grounding blocks")
    return {"ok": not errors, "errors": errors, "warnings": warnings}


def _split_pipe_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if "|" not in stripped:
        return None
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    cells = [cell.strip() for cell in stripped.split("|")]
    return cells if len(cells) >= 2 else None


def _is_separator_row(cells: Sequence[str] | None) -> bool:
    return bool(cells) and all(
        re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells
    )


def _render_table(
    header_cells: Sequence[str], body_rows: Sequence[Sequence[str]]
) -> str:
    width = len(header_cells)

    def render_row(tag: str, cells: Sequence[str]) -> str:
        padded = list(cells[:width]) + [""] * max(0, width - len(cells))
        return (
            "<tr>"
            + "".join(f"<{tag}>{html.escape(cell)}</{tag}>" for cell in padded)
            + "</tr>"
        )

    lines = [
        "<table>",
        "<thead>",
        render_row("th", header_cells),
        "</thead>",
        "<tbody>",
    ]
    lines.extend(render_row("td", row) for row in body_rows)
    lines.extend(["</tbody>", "</table>"])
    return "\n".join(lines)


def markdown_to_html(markdown: str) -> str:
    """Convert common OCR Markdown to scoreable HTML without repairing text."""

    text = markdown or ""
    fence = re.fullmatch(
        r"\s*```(?:markdown|md|html)?\s*\n?(.*?)\n?```\s*", text, re.DOTALL | re.I
    )
    if fence:
        text = fence.group(1)
    lines = text.splitlines()
    rendered: list[str] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            rendered.append(
                f"<p>{html.escape(' '.join(part.strip() for part in paragraph))}</p>"
            )
            paragraph.clear()

    index = 0
    while index < len(lines):
        line = lines[index]
        cells = _split_pipe_row(line)
        next_cells = (
            _split_pipe_row(lines[index + 1]) if index + 1 < len(lines) else None
        )
        if (
            cells
            and _is_separator_row(next_cells)
            and len(cells) == len(next_cells or [])
        ):
            flush_paragraph()
            body: list[list[str]] = []
            index += 2
            while index < len(lines):
                body_cells = _split_pipe_row(lines[index])
                if body_cells is None:
                    break
                body.append(body_cells)
                index += 1
            rendered.append(_render_table(cells, body))
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
        if heading:
            flush_paragraph()
            level = len(heading.group(1))
            rendered.append(
                f"<h{level}>{html.escape(heading.group(2).strip())}</h{level}>"
            )
        elif not line.strip():
            flush_paragraph()
        elif line.lstrip().startswith("<"):
            flush_paragraph()
            rendered.append(line)
        else:
            paragraph.append(line)
        index += 1
    flush_paragraph()
    return "\n".join(rendered).strip()


def build_page_html_rows(
    parsed: dict[str, Any] | Sequence[dict[str, Any]],
    *,
    run_id: str = "story230-unlimited-ocr-benchmark",
    module_id: str = MODULE_ID,
    source_paths: Sequence[str | Path] | None = None,
    created_at: str | None = None,
) -> list[dict[str, Any]]:
    """Build and validate diagnostic ``page_html_v1`` rows."""

    explicit_sources = [str(path) for path in (source_paths or [])]
    rows: list[dict[str, Any]] = []
    timestamp = created_at or _utc_now()
    parsed_pages = (
        list(parsed.get("pages") or []) if isinstance(parsed, dict) else list(parsed)
    )
    for index, parsed_page in enumerate(parsed_pages, start=1):
        source_path = parsed_page.get("source_path")
        if source_path is None and index <= len(explicit_sources):
            source_path = explicit_sources[index - 1]
        source_page = int(parsed_page.get("source_page", index))
        row = {
            "schema_version": "page_html_v1",
            "module_id": module_id,
            "run_id": run_id,
            "source": [str(source_path)] if source_path else None,
            "created_at": timestamp,
            "page": source_page,
            "page_number": source_page,
            "original_page_number": source_page,
            "image": str(source_path) if source_path else None,
            "raw_html": parsed_page.get("raw_markdown", ""),
            "html": markdown_to_html(parsed_page.get("clean_markdown", "")),
        }
        validated = PageHtml.model_validate(row)
        rows.append(validated.model_dump(exclude_none=True))
    return rows


def _score_html(output_html: str, golden_path: Path) -> dict[str, Any]:
    result = score_html_table_diff(
        output_html,
        {"vars": {"golden_path": str(golden_path)}},
    )
    return {**result, "golden_path": str(golden_path)}


def score_onward_case(parsed: dict[str, Any], case: OnwardCase) -> dict[str, Any]:
    rows = build_page_html_rows(
        parsed,
        run_id=f"story230-{case.case_id}",
        source_paths=case.image_paths,
    )
    combined_html = "\n".join(row["html"] for row in rows)
    whole_case = _score_html(combined_html, case.golden_path)

    diagnostic_pages: list[dict[str, Any]] = []
    for source_page, row in zip(case.source_pages, rows):
        golden = (
            ROOT
            / "benchmarks"
            / "golden"
            / "onward"
            / "per_page"
            / f"page_{source_page:03d}.html"
        )
        if golden.exists():
            diagnostic_pages.append(
                {
                    "source_page": source_page,
                    "independent_golden": False,
                    "score": _score_html(row["html"], golden),
                }
            )
    return {
        "whole_case": whole_case,
        "diagnostic_pages": diagnostic_pages,
        "combined_html": combined_html,
        "page_rows": rows,
    }


def decide_adoption(
    case_results: Sequence[dict[str, Any]],
    *,
    handwriting_results: Sequence[dict[str, Any]] | None = None,
    handwriting_summary: dict[str, Any] | None = None,
    min_case_gain: float = 0.0,
    min_mean_gain: float = 0.01,
    required_case_wins: int = 2,
) -> dict[str, Any]:
    """Apply Story 230's precommitted breadth-versus-complexity gate."""

    normalized: list[dict[str, Any]] = []
    for result in case_results:
        incumbent = float(result.get("incumbent_score", 0.0))
        candidate = float(result.get("candidate_score", 0.0))
        transport_ok = bool(result.get("transport_ok", True))
        routeable = bool(result.get("routeable", True))
        page_loss = bool(
            result.get("material_page_loss", False)
            or result.get("material_page_fidelity_loss", False)
        )
        incumbent_exact = bool(result.get("incumbent_exact", incumbent >= 1.0))
        candidate_exact = bool(result.get("candidate_exact", candidate >= 1.0))
        gain = candidate - incumbent
        exact_conversion = candidate_exact and not incumbent_exact
        meaningful = (
            transport_ok
            and routeable
            and not page_loss
            and (gain > min_case_gain or exact_conversion)
        )
        normalized.append(
            {
                **result,
                "incumbent_score": incumbent,
                "candidate_score": candidate,
                "gain": round(gain, 6),
                "exact_conversion": exact_conversion,
                "meaningful_win": meaningful,
            }
        )

    meaningful = [result for result in normalized if result["meaningful_win"]]
    mean_incumbent = (
        sum(result["incumbent_score"] for result in normalized) / len(normalized)
        if normalized
        else 0.0
    )
    mean_candidate = (
        sum(result["candidate_score"] for result in normalized) / len(normalized)
        if normalized
        else 0.0
    )
    oracle = (
        sum(
            max(result["incumbent_score"], result["candidate_score"])
            for result in normalized
        )
        / len(normalized)
        if normalized
        else 0.0
    )
    selection_share = len(meaningful) / len(normalized) if normalized else 0.0
    exact_conversion = any(result["exact_conversion"] for result in normalized)
    no_transport_or_page_failures = all(
        bool(result.get("transport_ok", True))
        and not bool(result.get("material_page_loss", False))
        and not bool(result.get("material_page_fidelity_loss", False))
        for result in normalized
    )
    onward_case_ids = [str(result.get("case_id", "")) for result in normalized]
    complete_onward_evidence = (
        len(onward_case_ids) == len(EXPECTED_ONWARD_CASES)
        and set(onward_case_ids) == EXPECTED_ONWARD_CASES
    )
    onward_quality_gate_passes = (
        complete_onward_evidence
        and len(meaningful) >= required_case_wins
        and no_transport_or_page_failures
        and ((mean_candidate - mean_incumbent) >= min_mean_gain or exact_conversion)
    )

    handwriting = list(handwriting_results or [])
    if handwriting_summary is not None:
        summary_case_ids = [
            str(case_id) for case_id in handwriting_summary.get("case_ids", [])
        ]
        complete_handwriting_evidence = (
            len(summary_case_ids) == len(EXPECTED_HANDWRITING_CASES)
            and set(summary_case_ids) == EXPECTED_HANDWRITING_CASES
        )
        handwriting_clears = (
            complete_handwriting_evidence
            and float(handwriting_summary.get("overall_min_ratio", 0.0)) >= 0.99
            and float(handwriting_summary.get("page_min_ratio", 0.0)) >= 0.99
            and float(handwriting_summary.get("pass_rate", 0.0)) >= 1.0
        )
    else:
        handwriting_case_ids = [
            str(result.get("case_id", "")) for result in handwriting
        ]
        complete_handwriting_evidence = (
            len(handwriting_case_ids) == len(EXPECTED_HANDWRITING_CASES)
            and set(handwriting_case_ids) == EXPECTED_HANDWRITING_CASES
        )
        handwriting_clears = complete_handwriting_evidence and all(
            float(result.get("overall_ratio", 0.0)) >= 0.99
            and float(result.get("page_min_ratio", 0.0)) >= 0.99
            and float(result.get("pass_rate", 0.0)) >= 1.0
            for result in handwriting
        )

    broad_onward_win = onward_quality_gate_passes and complete_handwriting_evidence
    decision = (
        "conditional_adopt"
        if broad_onward_win or handwriting_clears
        else "do_not_adopt"
    )
    reasons: list[str] = []
    if broad_onward_win:
        reasons.append(
            f"candidate meaningfully wins {len(meaningful)}/{len(normalized)} Onward cases"
        )
    elif normalized:
        if not complete_onward_evidence:
            reasons.append(
                "positive Onward adoption requires exactly one result for Alma, Arthur, and Marie-Louise"
            )
        reasons.append(
            f"candidate meaningfully wins only {len(meaningful)}/{len(normalized)} Onward cases; two independent wins are required"
        )
        reasons.append(
            f"aggregate gain is {mean_candidate - mean_incumbent:+.4f}; gate requires +{min_mean_gain:.4f} or an exact-pass conversion"
        )
    if handwriting_clears:
        reasons.append("both real handwriting fixtures clear the 0.99/1.0 blocker")
    elif handwriting or handwriting_summary is not None:
        if not complete_handwriting_evidence:
            reasons.append(
                "positive adoption requires exactly one result for Barney and Alverson"
            )
        else:
            reasons.append(
                "the real handwriting pair does not clear the 0.99/1.0 blocker"
            )
    elif onward_quality_gate_passes:
        reasons.append(
            "positive adoption requires exactly one result for Barney and Alverson"
        )
    failed_transport = [
        result.get("case_id", "unknown")
        for result in normalized
        if not result.get("transport_ok", True)
    ]
    if failed_transport:
        reasons.append(f"transport failed for: {', '.join(failed_transport)}")
    page_losses = [
        result.get("case_id", "unknown")
        for result in normalized
        if result.get("material_page_loss", False)
        or result.get("material_page_fidelity_loss", False)
    ]
    if page_losses:
        reasons.append(
            f"material page fidelity loss was reported for: {', '.join(page_losses)}"
        )

    output: dict[str, Any] = {
        "decision": decision,
        "meaningful_wins": len(meaningful),
        "mean_incumbent_score": round(mean_incumbent, 6),
        "mean_candidate_score": round(mean_candidate, 6),
        "aggregate_gain": round(mean_candidate - mean_incumbent, 6),
        "oracle_hybrid_score": round(oracle, 6),
        "candidate_selection_share": round(selection_share, 6),
        "complete_onward_evidence": complete_onward_evidence,
        "complete_handwriting_evidence": complete_handwriting_evidence,
        "reasons": reasons,
        "cases": normalized,
    }
    if decision == "conditional_adopt":
        if broad_onward_win:
            signals = {
                str(result.get("routing_signal"))
                for result in meaningful
                if result.get("routing_signal")
            }
            output["winning_surface"] = (
                next(iter(signals))
                if len(signals) == 1
                else "flagged_genealogy_table_group"
            )
        else:
            output["winning_surface"] = "historical_handwriting"
    return output


def _select_best_candidate(
    candidates: Sequence[dict[str, Any]],
) -> dict[str, Any] | None:
    """Return the highest-scoring eligible arm, or ``None`` if all arms fail."""

    def eligible(result: dict[str, Any]) -> bool:
        try:
            candidate_score = float(result.get("candidate_score", 0.0))
        except (TypeError, ValueError):
            return False
        return (
            math.isfinite(candidate_score)
            and bool(result.get("transport_ok", True))
            and bool(result.get("routeable", True))
            and not bool(result.get("material_page_loss", False))
            and not bool(result.get("material_page_fidelity_loss", False))
        )

    eligible_candidates = [result for result in candidates if eligible(result)]
    if not eligible_candidates:
        return None
    return max(
        eligible_candidates,
        key=lambda result: float(result.get("candidate_score", 0.0)),
    )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _verify_model_checkout(model_dir: Path) -> dict[str, Any]:
    """Verify pinned code and exact weights before executing remote model code."""

    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=model_dir,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status_lines = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=model_dir,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(
            f"model directory is not a readable pinned git checkout: {model_dir}"
        ) from exc

    if head != UNIVERSAL_REVISION:
        raise RuntimeError(
            f"runtime code revision mismatch: expected {UNIVERSAL_REVISION}, got {head}"
        )
    # Hugging Face materializes these LFS objects over the checkout's pointer
    # files. Every executable/configuration path must otherwise remain clean.
    allowed_materialized_paths = {
        "assets/baidu.png",
        "model-00001-of-000001.safetensors",
    }
    dirty_paths = {
        line[3:].strip().strip('"') for line in status_lines if len(line) >= 4
    }
    unexpected_dirty = sorted(dirty_paths - allowed_materialized_paths)
    if unexpected_dirty:
        raise RuntimeError(
            "runtime checkout contains unpinned changes: " + ", ".join(unexpected_dirty)
        )

    weight_path = model_dir / "model-00001-of-000001.safetensors"
    if not weight_path.is_file():
        raise RuntimeError(f"pinned model weight is missing: {weight_path}")
    weight_size = weight_path.stat().st_size
    if weight_size != WEIGHT_SIZE_BYTES:
        raise RuntimeError(
            f"model weight size mismatch: expected {WEIGHT_SIZE_BYTES}, got {weight_size}"
        )
    weight_sha256 = _sha256_file(weight_path)
    if weight_sha256 != WEIGHT_SHA256:
        raise RuntimeError(
            f"model weight hash mismatch: expected {WEIGHT_SHA256}, got {weight_sha256}"
        )
    return {
        "runtime_code_revision_verified": head,
        "unexpected_dirty_paths": unexpected_dirty,
        "weight_path": str(weight_path),
        "weight_size_bytes": weight_size,
        "weight_sha256_verified": weight_sha256,
    }


def _runtime_metadata(
    model_dir: Path,
    device: str,
    dtype: str,
    verification: dict[str, Any],
) -> dict[str, Any]:
    dependency_versions: dict[str, str] = {}
    for package in ("torch", "transformers", "tokenizers", "PIL", "safetensors"):
        try:
            module = __import__(package)
            dependency_versions[package] = str(
                getattr(module, "__version__", "unknown")
            )
        except ImportError:
            dependency_versions[package] = "not-installed"
    git_revision = None
    try:
        git_revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=model_dir,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        pass
    return {
        "captured_at": _utc_now(),
        "official_model_revision": MODEL_REVISION,
        "runtime_code_revision": git_revision or UNIVERSAL_REVISION,
        "weight_sha256": WEIGHT_SHA256,
        "weight_size_bytes": WEIGHT_SIZE_BYTES,
        "model_license": MODEL_LICENSE,
        "model_dir": str(model_dir),
        "device": device,
        "dtype": dtype,
        "python": sys.version,
        "platform": platform.platform(),
        "dependency_versions": dependency_versions,
        "source_code_patch_status": (
            "exact official weight object; community Universal code patch changes device/dtype/MPS handling"
        ),
        "verification": verification,
    }


def _space_event_payload(event: Any) -> dict[str, Any] | None:
    if isinstance(event, dict):
        return event
    if isinstance(event, tuple) and len(event) == 1 and isinstance(event[0], dict):
        return event[0]
    return None


def run_space(args: argparse.Namespace) -> int:
    """Capture an official BF16 single-page control from Baidu's Space."""

    if not args.allow_public_upload:
        raise ValueError(
            "run-space uploads the image to a public Hugging Face Space; "
            "pass --allow-public-upload only for an explicitly public sample"
        )
    try:
        from gradio_client import Client, handle_file
    except ImportError as exc:
        raise RuntimeError("run-space requires gradio_client") from exc

    image_path = Path(args.image).resolve()
    out_dir = Path(args.out_dir).resolve()
    started = time.monotonic()
    client = Client(args.space)
    job = client.submit(
        handle_file(str(image_path)),
        args.mode,
        "document parsing.",
        api_name="/run_ocr",
    )
    events: list[dict[str, Any]] = []
    for event in job:
        payload = _space_event_payload(event)
        if payload is not None:
            events.append(payload)
    if not events:
        payload = _space_event_payload(job.result(timeout=args.timeout))
        if payload is not None:
            events.append(payload)
    if not events:
        raise RuntimeError("official Space returned no structured OCR events")
    final = next((event for event in reversed(events) if event.get("done")), events[-1])
    raw = str(final.get("text") or "")
    runtime = {
        "provider": f"Hugging Face Space {args.space}",
        "official_space_revision": OFFICIAL_SPACE_REVISION,
        "official_model_revision": MODEL_REVISION,
        "device": "ZeroGPU NVIDIA",
        "dtype": "bfloat16",
        "mode": args.mode,
        "prompt": SINGLE_PROMPT,
        "max_length": 8192,
        "no_repeat_ngram_size": 35,
        "ngram_window": 128,
        "temperature": 0.0,
        "wall_seconds": round(time.monotonic() - started, 3),
        "output_char_count": len(raw),
        "output_tokens": None,
        "finish_reason": "space_done_event"
        if final.get("done")
        else "space_stream_ended",
        "truncated": None,
        "limitations": "official Space exposes single-page inference only and uses max_length=8192",
    }
    parsed, transport, rows = _persist_arm(
        out_dir=out_dir,
        raw=raw,
        source_pages=[args.source_page],
        source_paths=[image_path],
        runtime=runtime,
        require_page_markers=False,
    )
    _write_json(out_dir / "space_events.json", events)
    result: dict[str, Any] = {
        "source_page": args.source_page,
        "image_path": str(image_path),
        "transport": transport,
        "runtime": runtime,
        "artifact_dir": str(out_dir),
    }
    diagnostic_golden = (
        ROOT
        / "benchmarks"
        / "golden"
        / "onward"
        / "per_page"
        / f"page_{args.source_page:03d}.html"
    )
    if diagnostic_golden.exists() and rows:
        result["diagnostic_score"] = {
            **_score_html(rows[0]["html"], diagnostic_golden),
            "independent_golden": False,
        }
    _write_json(out_dir / "result.json", result)
    print(json.dumps(result, indent=2))
    return 0 if transport["ok"] else 2


def run_local_single(args: argparse.Namespace) -> int:
    """Run one local image for public-sample parity or bounded transport proof."""

    model_dir = Path(args.model_dir).resolve()
    image_path = Path(args.image).resolve()
    out_dir = Path(args.out_dir).resolve()
    tokenizer, model, device, dtype, verification = _load_local_model(
        model_dir, args.device
    )
    metadata = _runtime_metadata(model_dir, device, dtype, verification)
    raw, runtime = _infer_single(
        model,
        tokenizer,
        image_path,
        args.mode,
        out_dir / "model_scratch",
    )
    _, transport, _ = _persist_arm(
        out_dir=out_dir,
        raw=raw,
        source_pages=[args.source_page],
        source_paths=[image_path],
        runtime={**runtime, "environment": metadata},
        require_page_markers=False,
    )
    result = {
        "source_page": args.source_page,
        "image_path": str(image_path),
        "transport": transport,
        "runtime": runtime,
        "environment": metadata,
        "artifact_dir": str(out_dir),
    }
    _write_json(out_dir / "result.json", result)
    print(json.dumps(result, indent=2))
    return 0 if transport["ok"] else 2


def compare_parity(args: argparse.Namespace) -> int:
    reference_path = Path(args.reference).resolve()
    candidate_path = Path(args.candidate).resolve()
    reference = reference_path.read_text(encoding="utf-8").replace("\r\n", "\n").strip()
    candidate = candidate_path.read_text(encoding="utf-8").replace("\r\n", "\n").strip()
    result = {
        "reference_path": str(reference_path),
        "candidate_path": str(candidate_path),
        "exact_match": reference == candidate,
        "sequence_ratio": round(SequenceMatcher(None, reference, candidate).ratio(), 6),
        "reference_char_count": len(reference),
        "candidate_char_count": len(candidate),
    }
    _write_json(Path(args.out).resolve(), result)
    print(json.dumps(result, indent=2))
    return 0


def _load_local_model(
    model_dir: Path,
    requested_device: str | None = None,
) -> tuple[Any, Any, str, str, dict[str, Any]]:
    verification = _verify_model_checkout(model_dir)
    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
    os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    os.environ.setdefault("HF_HOME", "/tmp/doc-web-unlimited-ocr-hf")
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/doc-web-unlimited-ocr-matplotlib")
    try:
        import torch
        from transformers import AutoModel, AutoTokenizer
    except ImportError as exc:
        raise RuntimeError(
            "Local inference dependencies are absent; install the pinned benchmark environment first"
        ) from exc

    if requested_device:
        device = requested_device
    elif torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"
    dtype_obj = torch.bfloat16 if device == "cuda" else torch.float32
    dtype = "bfloat16" if device == "cuda" else "float32"
    tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
    model = AutoModel.from_pretrained(
        model_dir,
        trust_remote_code=True,
        use_safetensors=True,
        torch_dtype=dtype_obj,
        attn_implementation="eager",
    )
    return tokenizer, model.eval().to(device), device, dtype, verification


def _generation_cap_assessment(
    output_tokens: int | None,
    max_length: int,
) -> dict[str, Any]:
    if output_tokens is None:
        return {
            "finish_reason": "not_exposed_by_transformers_helper",
            "truncated": None,
            "truncation_assessment": "unknown_without_output_token_count",
            "output_token_margin_to_total_max_length": None,
        }
    reached_total_cap = output_tokens >= max_length
    return {
        "finish_reason": (
            "length" if reached_total_cap else "not_exposed_by_transformers_helper"
        ),
        "truncated": True if reached_total_cap else None,
        "truncation_assessment": (
            "hard_failure_output_tokens_reached_total_max_length"
            if reached_total_cap
            else "indeterminate_helper_omits_input_length_and_stop_reason"
        ),
        "output_token_margin_to_total_max_length": max_length - output_tokens,
        "max_length_semantics": "Transformers total input-plus-output sequence length",
    }


def _infer_single(
    model: Any,
    tokenizer: Any,
    image_path: Path,
    mode: str,
    scratch_dir: Path,
) -> tuple[str, dict[str, Any]]:
    mode_args = (
        {"base_size": 1024, "image_size": 640, "crop_mode": True}
        if mode == "gundam"
        else {"base_size": 1024, "image_size": 1024, "crop_mode": False}
    )
    started = time.monotonic()
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
        raw = model.infer(
            tokenizer,
            prompt=SINGLE_PROMPT,
            image_file=str(image_path),
            output_path=str(scratch_dir),
            max_length=32768,
            no_repeat_ngram_size=35,
            ngram_window=128,
            temperature=0.0,
            save_results=False,
            eval_mode=True,
            **mode_args,
        )
    elapsed = time.monotonic() - started
    raw = str(raw or "")
    try:
        output_tokens = len(tokenizer.encode(raw, add_special_tokens=False))
    except (AttributeError, TypeError, ValueError):
        output_tokens = None
    cap_assessment = _generation_cap_assessment(output_tokens, 32768)
    return raw, {
        "mode": mode,
        "prompt": SINGLE_PROMPT,
        "max_length": 32768,
        "no_repeat_ngram_size": 35,
        "ngram_window": 128,
        "temperature": 0.0,
        "wall_seconds": round(elapsed, 3),
        "output_char_count": len(raw),
        "output_tokens": output_tokens,
        **cap_assessment,
        "captured_console": stream.getvalue(),
    }


def _infer_multi(
    model: Any,
    tokenizer: Any,
    image_paths: Sequence[Path],
    scratch_dir: Path,
) -> tuple[str, dict[str, Any]]:
    started = time.monotonic()
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
        raw, output_tokens = model.infer_multi(
            tokenizer,
            prompt=MULTI_PROMPT,
            image_files=[str(path) for path in image_paths],
            output_path=str(scratch_dir),
            image_size=1024,
            max_length=32768,
            no_repeat_ngram_size=35,
            ngram_window=1024,
            temperature=0.0,
            save_results=False,
        )
    elapsed = time.monotonic() - started
    raw = str(raw or "")
    output_token_count = int(output_tokens)
    cap_assessment = _generation_cap_assessment(output_token_count, 32768)
    return raw, {
        "mode": "multi_base",
        "prompt": MULTI_PROMPT,
        "max_length": 32768,
        "no_repeat_ngram_size": 35,
        "ngram_window": 1024,
        "temperature": 0.0,
        "wall_seconds": round(elapsed, 3),
        "output_char_count": len(raw),
        "output_tokens": output_token_count,
        **cap_assessment,
        "captured_console": stream.getvalue(),
    }


def _persist_arm(
    *,
    out_dir: Path,
    raw: str,
    source_pages: Sequence[int],
    source_paths: Sequence[Path],
    runtime: dict[str, Any],
    require_page_markers: bool,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    # The raw write intentionally precedes all parser/normalizer work.
    _write_text(out_dir / "raw.txt", raw)
    parsed = parse_grounded_output(
        raw,
        source_pages=source_pages,
        source_paths=source_paths,
        expected_pages=len(source_pages),
    )
    transport = validate_transport(
        parsed,
        expected_pages=len(source_pages),
        expected_source_pages=source_pages,
        require_page_markers=require_page_markers,
        truncated=bool(runtime.get("truncated")),
        finish_reason=runtime.get("finish_reason"),
    )
    rows = build_page_html_rows(
        parsed,
        run_id=out_dir.parent.name,
        source_paths=source_paths,
    )
    _write_json(out_dir / "parsed.json", parsed)
    _write_json(out_dir / "transport.json", transport)
    _write_json(out_dir / "runtime.json", runtime)
    _write_text(
        out_dir / "clean.md",
        "\n\n".join(page["clean_markdown"] for page in parsed["pages"]),
    )
    _write_jsonl(out_dir / "pages_html.jsonl", rows)
    _write_text(out_dir / "normalized.html", "\n".join(row["html"] for row in rows))
    return parsed, transport, rows


def run_local(args: argparse.Namespace) -> int:
    model_dir = Path(args.model_dir).resolve()
    out_root = Path(args.out_root).resolve()
    case_ids = args.case or list(ONWARD_CASES)
    invalid = sorted(set(case_ids) - set(ONWARD_CASES))
    if invalid:
        raise ValueError(f"Unknown Onward cases: {', '.join(invalid)}")
    arms = args.arm or ["single_gundam", "single_base", "multi_base"]
    valid_arms = {"single_gundam", "single_base", "multi_base"}
    if not set(arms) <= valid_arms:
        raise ValueError(f"Unknown arms: {', '.join(sorted(set(arms) - valid_arms))}")

    tokenizer, model, device, dtype, verification = _load_local_model(
        model_dir, args.device
    )
    metadata = _runtime_metadata(model_dir, device, dtype, verification)
    prior_runtime_path = out_root / "runtime.json"
    if args.resume and prior_runtime_path.exists():
        prior_runtime = json.loads(prior_runtime_path.read_text(encoding="utf-8"))
        fingerprint_keys = (
            "official_model_revision",
            "runtime_code_revision",
            "weight_sha256",
            "device",
            "dtype",
        )
        mismatches = [
            key
            for key in fingerprint_keys
            if prior_runtime.get(key) != metadata.get(key)
        ]
        if mismatches:
            raise RuntimeError(
                "--resume runtime differs from existing artifacts for: "
                + ", ".join(mismatches)
            )
    _write_json(prior_runtime_path, metadata)
    all_results: list[dict[str, Any]] = []
    if args.resume and (out_root / "onward_results.json").exists():
        existing_payload = json.loads(
            (out_root / "onward_results.json").read_text(encoding="utf-8")
        )
        all_results = (
            existing_payload
            if isinstance(existing_payload, list)
            else existing_payload["results"]
        )
    completed = {
        (str(result.get("case_id")), str(result.get("arm"))) for result in all_results
    }

    for case_id in case_ids:
        case = ONWARD_CASES[case_id]
        for arm in arms:
            if (case_id, arm) in completed:
                continue
            arm_dir = out_root / "onward" / case_id / arm
            arm_dir.mkdir(parents=True, exist_ok=True)
            if arm == "multi_base":
                raw, runtime = _infer_multi(
                    model,
                    tokenizer,
                    case.image_paths,
                    arm_dir / "model_scratch",
                )
                parsed, transport, rows = _persist_arm(
                    out_dir=arm_dir,
                    raw=raw,
                    source_pages=case.source_pages,
                    source_paths=case.image_paths,
                    runtime={**runtime, "environment": metadata},
                    require_page_markers=True,
                )
            else:
                mode = "gundam" if arm == "single_gundam" else "base"
                raw_pages: list[str] = []
                page_runtimes: list[dict[str, Any]] = []
                for source_page, image_path in zip(case.source_pages, case.image_paths):
                    raw_page, page_runtime = _infer_single(
                        model,
                        tokenizer,
                        image_path,
                        mode,
                        arm_dir / "model_scratch" / f"page_{source_page:03d}",
                    )
                    raw_pages.append(raw_page)
                    page_runtimes.append(page_runtime)
                # Add explicit page markers only in the benchmark transport
                # envelope; every original page response remains in raw_pages/.
                raw = "\n".join(f"{PAGE_MARKER}\n{page}" for page in raw_pages)
                for source_page, raw_page in zip(case.source_pages, raw_pages):
                    _write_text(
                        arm_dir / "raw_pages" / f"page_{source_page:03d}.txt", raw_page
                    )
                runtime = {
                    "mode": mode,
                    "prompt": SINGLE_PROMPT,
                    "max_length": 32768,
                    "no_repeat_ngram_size": 35,
                    "ngram_window": 128,
                    "temperature": 0.0,
                    "page_calls": page_runtimes,
                    "wall_seconds": round(
                        sum(item["wall_seconds"] for item in page_runtimes), 3
                    ),
                    "output_char_count": len(raw),
                    "output_tokens": sum(
                        int(item["output_tokens"])
                        for item in page_runtimes
                        if item.get("output_tokens") is not None
                    ),
                    "finish_reason": (
                        "length"
                        if any(item.get("truncated") is True for item in page_runtimes)
                        else "not_exposed_by_transformers_helper"
                    ),
                    "truncated": (
                        True
                        if any(item.get("truncated") is True for item in page_runtimes)
                        else None
                    ),
                    "truncation_assessment": (
                        "one_or_more_page_calls_reached_total_max_length"
                        if any(item.get("truncated") is True for item in page_runtimes)
                        else "indeterminate_page_helpers_omit_input_length_and_stop_reason"
                    ),
                }
                parsed, transport, rows = _persist_arm(
                    out_dir=arm_dir,
                    raw=raw,
                    source_pages=case.source_pages,
                    source_paths=case.image_paths,
                    runtime={**runtime, "environment": metadata},
                    require_page_markers=True,
                )

            scoring = score_onward_case(parsed, case)
            _write_text(arm_dir / "normalized.html", scoring["combined_html"])
            _write_json(
                arm_dir / "score.json",
                {
                    key: value
                    for key, value in scoring.items()
                    if key not in {"combined_html", "page_rows"}
                },
            )
            result = {
                "case_id": case.case_id,
                "arm": arm,
                "incumbent_score": case.incumbent_score,
                "candidate_score": float(scoring["whole_case"]["score"]),
                "candidate_exact": bool(scoring["whole_case"]["pass"]),
                "transport_ok": bool(transport["ok"]),
                "material_page_loss": not bool(transport["ok"]),
                "routeable": True,
                "wall_seconds": runtime["wall_seconds"],
                "artifact_dir": str(arm_dir),
            }
            all_results.append(result)
            _write_json(arm_dir / "result.json", result)

    handwriting_results: list[dict[str, Any]] = []
    if args.resume and (out_root / "handwriting_results.json").exists():
        handwriting_results = json.loads(
            (out_root / "handwriting_results.json").read_text(encoding="utf-8")
        )
    if not args.skip_handwriting:
        for case in HANDWRITING_CASES.values():
            if any(
                result.get("case_id") == case.case_id for result in handwriting_results
            ):
                continue
            case_dir = out_root / "handwriting" / case.case_id / "single_gundam"
            raw, runtime = _infer_single(
                model,
                tokenizer,
                case.image_path,
                "gundam",
                case_dir / "model_scratch",
            )
            parsed, transport, rows = _persist_arm(
                out_dir=case_dir,
                raw=raw,
                source_pages=[case.source_page],
                source_paths=[case.image_path],
                runtime={**runtime, "environment": metadata},
                require_page_markers=False,
            )
            artifact_path = case_dir / "pages_html.jsonl"
            metrics = score_page_html_artifact(case.transcript_path, artifact_path)
            metrics["pass_rate"] = (
                1.0
                if (
                    metrics["overall_ratio"] >= 0.99
                    and metrics["page_min_ratio"] >= 0.99
                    and transport["ok"]
                )
                else 0.0
            )
            result = {
                "case_id": case.case_id,
                "source_path": str(case.image_path),
                "transcript_path": str(case.transcript_path),
                "transport": transport,
                **metrics,
                "artifact_dir": str(case_dir),
            }
            handwriting_results.append(result)
            _write_json(case_dir / "score.json", result)

    selected: list[dict[str, Any]] = []
    for case_id in ONWARD_CASES:
        candidates = [result for result in all_results if result["case_id"] == case_id]
        if candidates:
            selected_candidate = _select_best_candidate(candidates)
            if selected_candidate is not None:
                selected.append(selected_candidate)
    decision = decide_adoption(selected, handwriting_results=handwriting_results)
    _write_json(out_root / "onward_results.json", all_results)
    _write_json(out_root / "handwriting_results.json", handwriting_results)
    _write_json(out_root / "decision.json", decision)
    _write_json(
        out_root / "run_manifest.json",
        {
            "runtime": metadata,
            "results": all_results,
            "handwriting_results": handwriting_results,
            "decision": decision,
        },
    )
    return 0


def score_existing(args: argparse.Namespace) -> int:
    raw_path = Path(args.raw).resolve()
    case = ONWARD_CASES[args.case]
    out_dir = Path(args.out_dir).resolve()
    runtime = {
        "mode": args.arm,
        "prompt": MULTI_PROMPT if args.arm == "multi_base" else SINGLE_PROMPT,
        "wall_seconds": args.wall_seconds,
        "output_char_count": raw_path.stat().st_size,
        "output_tokens": args.output_tokens,
        "finish_reason": args.finish_reason,
        "truncated": args.truncated,
    }
    parsed, transport, _ = _persist_arm(
        out_dir=out_dir,
        raw=raw_path.read_text(encoding="utf-8"),
        source_pages=case.source_pages,
        source_paths=case.image_paths,
        runtime=runtime,
        require_page_markers=args.arm == "multi_base" or len(case.source_pages) > 1,
    )
    scoring = score_onward_case(parsed, case)
    _write_text(out_dir / "normalized.html", scoring["combined_html"])
    _write_json(
        out_dir / "score.json",
        {
            key: value
            for key, value in scoring.items()
            if key not in {"combined_html", "page_rows"}
        },
    )
    result = {
        "case_id": case.case_id,
        "arm": args.arm,
        "incumbent_score": case.incumbent_score,
        "candidate_score": float(scoring["whole_case"]["score"]),
        "candidate_exact": bool(scoring["whole_case"]["pass"]),
        "transport_ok": bool(transport["ok"]),
        "material_page_loss": not bool(transport["ok"]),
        "routeable": True,
        "artifact_dir": str(out_dir),
    }
    _write_json(out_dir / "result.json", result)
    print(json.dumps(result, indent=2))
    return 0 if transport["ok"] else 2


def summarize(args: argparse.Namespace) -> int:
    results_path = Path(args.results).resolve()
    payload = json.loads(results_path.read_text(encoding="utf-8"))
    results = payload if isinstance(payload, list) else payload["results"]
    handwriting_results = (
        []
        if isinstance(payload, list)
        else list(payload.get("handwriting_results") or [])
    )
    if args.handwriting_results:
        handwriting_payload = json.loads(
            Path(args.handwriting_results).resolve().read_text(encoding="utf-8")
        )
        handwriting_results = (
            handwriting_payload
            if isinstance(handwriting_payload, list)
            else list(handwriting_payload.get("results") or [])
        )
    selected: list[dict[str, Any]] = []
    for case_id in ONWARD_CASES:
        candidates = [result for result in results if result.get("case_id") == case_id]
        if not candidates:
            continue
        selected_candidate = _select_best_candidate(candidates)
        if selected_candidate is not None:
            selected.append(selected_candidate)
    decision = decide_adoption(
        selected,
        handwriting_results=handwriting_results,
    )
    out_path = Path(args.out).resolve()
    _write_json(out_path, decision)
    print(json.dumps(decision, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    local = subparsers.add_parser(
        "run-local", help="run the exact-weight local Transformers benchmark"
    )
    local.add_argument("--model-dir", required=True)
    local.add_argument("--out-root", default=str(DEFAULT_OUT_ROOT))
    local.add_argument("--device", choices=["cuda", "mps", "cpu"])
    local.add_argument("--case", action="append", choices=sorted(ONWARD_CASES))
    local.add_argument(
        "--arm",
        action="append",
        choices=["single_gundam", "single_base", "multi_base"],
    )
    local.add_argument(
        "--skip-handwriting",
        action="store_true",
        help="skip the opportunistic Story 191 real-handwriting screen",
    )
    local.add_argument(
        "--resume",
        action="store_true",
        help="reuse already packaged case/arm results under the same output root",
    )
    local.set_defaults(func=run_local)

    space = subparsers.add_parser(
        "run-space",
        help="capture an official Baidu BF16 single-page parity control",
    )
    space.add_argument("--image", required=True)
    space.add_argument("--source-page", type=int, required=True)
    space.add_argument("--mode", choices=["gundam", "base"], default="gundam")
    space.add_argument("--out-dir", required=True)
    space.add_argument("--space", default="baidu/Unlimited-OCR")
    space.add_argument("--timeout", type=float, default=900.0)
    space.add_argument(
        "--allow-public-upload",
        action="store_true",
        help="acknowledge that --image is public and may be uploaded to Hugging Face",
    )
    space.set_defaults(func=run_space)

    single = subparsers.add_parser(
        "run-local-single",
        help="run one local image for parity or bounded transport proof",
    )
    single.add_argument("--model-dir", required=True)
    single.add_argument("--image", required=True)
    single.add_argument("--source-page", type=int, required=True)
    single.add_argument("--mode", choices=["gundam", "base"], default="gundam")
    single.add_argument("--out-dir", required=True)
    single.add_argument("--device", choices=["cuda", "mps", "cpu"])
    single.set_defaults(func=run_local_single)

    parity = subparsers.add_parser(
        "compare-parity",
        help="compare captured official and local raw text without repair",
    )
    parity.add_argument("--reference", required=True)
    parity.add_argument("--candidate", required=True)
    parity.add_argument("--out", required=True)
    parity.set_defaults(func=compare_parity)

    existing = subparsers.add_parser(
        "score-existing", help="package and score a captured raw response"
    )
    existing.add_argument("--raw", required=True)
    existing.add_argument("--case", required=True, choices=sorted(ONWARD_CASES))
    existing.add_argument("--arm", required=True)
    existing.add_argument("--out-dir", required=True)
    existing.add_argument("--wall-seconds", type=float)
    existing.add_argument("--output-tokens", type=int)
    existing.add_argument("--finish-reason", default="unknown")
    existing.add_argument("--truncated", action="store_true")
    existing.set_defaults(func=score_existing)

    summary = subparsers.add_parser(
        "summarize", help="apply the precommitted decision gate"
    )
    summary.add_argument("--results", required=True)
    summary.add_argument(
        "--handwriting-results",
        help="optional handwriting result list when --results is not a run manifest",
    )
    summary.add_argument("--out", required=True)
    summary.set_defaults(func=summarize)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
