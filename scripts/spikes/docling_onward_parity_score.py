#!/usr/bin/env python3
"""
Score the current Docling Arthur-lane output against the incumbent Onward gold.

This is intentionally a spike-local scorer. It does not claim full-Onward
parity; it freezes the currently accepted Arthur hard-case lane so future
Docling experiments have a concrete target before any methodology realignment
is considered.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter, OrderedDict
from html import escape
from pathlib import Path
from typing import Any, Iterable

from bs4 import BeautifulSoup, Tag


DEFAULT_GOLD = Path("benchmarks/golden/onward/arthur.html")
DEFAULT_OUTDIR = Path("output/runs/story158-docling-parity-r1")
DEFAULT_CANDIDATES = OrderedDict(
    [
        (
            "baseline-images",
            Path(
                "output/runs/story158-docling-tuning-r1/docling/baseline-images/"
                "onward-hardcase-slice-imageonly.html"
            ),
        ),
        (
            "hybrid-two-page",
            Path("output/runs/story158-docling-hybrid-proof-r1/merged-two-page.html"),
        ),
    ]
)

EXPECTED_HEADERS = ["NAME", "BORN", "MARRIED", "SPOUSE", "BOY", "GIRL", "DIED"]
LANE_SUBGROUP_LIMIT = 30
LEAK_SCORE_CAP = 5
PRETABLE_PARAGRAPH_CAP = 8
CHECKPOINTS = [
    ("Arthur", "Lucille Lambert"),
    ("Dorilla", "David Gelinas"),
    ("Alice", "Joseph Landis"),
    ("Joseph", "Barbara Hodges"),
    ("Paul", "Jeannine Turcotte"),
    ("Yvette", "Conrad Pretts"),
    ("Joe", "Frances Averyon"),
]
SCORE_WEIGHTS = OrderedDict(
    [
        ("header_exact", 10.0),
        ("pretable_onset", 15.0),
        ("subgroup_lcs", 25.0),
        ("subgroup_position", 15.0),
        ("leak_hygiene", 15.0),
        ("checkpoint_pairs", 20.0),
    ]
)


def _normalize_text(text: str | None) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = text.replace("\u2019", "'").replace("\u2018", "'").replace("`", "'")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _normalize_key(text: str | None) -> str:
    return _normalize_text(text).casefold()


def _is_arthur_heading(tag: Tag) -> bool:
    return tag.name in {"h1", "h2"} and _normalize_key(tag.get_text(" ", strip=True)) in {
        "arthur l'heureux",
        "arthur lheureux",
    }


def _find_candidate_heading(soup: BeautifulSoup) -> Tag | None:
    candidates: list[tuple[int, int, int, Tag]] = []
    for index, tag in enumerate(soup.find_all(["h2", "h1"])):
        if not _is_arthur_heading(tag):
            continue
        cursor = tag.find_next_sibling()
        paragraph_count = 0
        table_found = False
        while cursor is not None:
            if getattr(cursor, "name", None) == "table":
                table_found = True
                break
            if getattr(cursor, "name", None) == "p":
                text = _normalize_text(cursor.get_text(" ", strip=True))
                if text:
                    paragraph_count += 1
            cursor = cursor.find_next_sibling()
        if table_found:
            heading_priority = 0 if tag.name == "h2" else 1
            candidates.append((paragraph_count, heading_priority, index, tag))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[:3])
    return candidates[0][3]


def _cell_texts(row: Tag) -> list[str]:
    return [
        _normalize_text(cell.get_text(" ", strip=True))
        for cell in row.find_all(["td", "th"])
        if _normalize_text(cell.get_text(" ", strip=True))
    ]


def _is_subgroup_row(row: Tag) -> bool:
    cells = _cell_texts(row)
    if not cells:
        return False
    joined = " ".join(cells)
    has_marker = "FAMILY" in joined or "Grandchildren" in joined
    return bool(has_marker and (len(cells) == 1 or "genealogy-subgroup-heading" in (row.get("class") or [])))


def _extract_candidate_context(path: Path) -> dict[str, Any]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    heading = _find_candidate_heading(soup)
    if heading is None:
        table = soup.find("table")
        if table is None:
            raise ValueError(f"Arthur heading or fallback table not found in {path}")
        return {
            "soup": soup,
            "heading_text": "Arthur L'Heureux",
            "table": table,
            "pretable_paragraphs": [],
        }

    table = heading.find_next("table")
    if table is None:
        raise ValueError(f"Arthur table not found in {path}")

    pretable_paragraphs: list[str] = []
    cursor = heading.find_next_sibling()
    while cursor is not None and cursor is not table:
        if getattr(cursor, "name", None) == "p":
            text = _normalize_text(cursor.get_text(" ", strip=True))
            if text:
                pretable_paragraphs.append(text)
        cursor = cursor.find_next_sibling()

    return {
        "soup": soup,
        "heading_text": _normalize_text(heading.get_text(" ", strip=True)),
        "table": table,
        "pretable_paragraphs": pretable_paragraphs,
    }


def _extract_gold_context(path: Path) -> dict[str, Any]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    table = soup.find("table")
    if table is None:
        raise ValueError(f"Arthur gold table not found in {path}")
    return {
        "heading_text": "Arthur L'Heureux",
        "table": table,
        "pretable_paragraphs": [],
    }


def _extract_lane_rows(table: Tag, subgroup_limit: int) -> list[Tag]:
    rows: list[Tag] = []
    subgroup_count = 0
    for row in table.find_all("tr"):
        rows.append(row)
        if _is_subgroup_row(row):
            subgroup_count += 1
            if subgroup_count >= subgroup_limit:
                break
    return rows


def _header_signature(rows: Iterable[Tag]) -> list[str]:
    for row in list(rows)[:6]:
        cells = [text.upper() for text in _cell_texts(row)]
        if "NAME" in cells or "BORN" in cells:
            return cells
    return []


def _subgroup_sequence(rows: Iterable[Tag]) -> list[str]:
    return [" ".join(_cell_texts(row)) for row in rows if _is_subgroup_row(row)]


def _row_texts(rows: Iterable[Tag]) -> list[str]:
    return [" | ".join(_cell_texts(row)) for row in rows if _cell_texts(row)]


def _heading_like_leaks(rows: Iterable[Tag]) -> list[str]:
    leaks: list[str] = []
    for row in rows:
        if _is_subgroup_row(row):
            continue
        for text in _cell_texts(row):
            if text.upper() in EXPECTED_HEADERS:
                continue
            if "FAMILY" in text or "Grandchildren" in text:
                leaks.append(text)
    return leaks


def _checkpoint_results(rows: Iterable[Tag]) -> dict[str, bool]:
    row_texts = [_normalize_key(text) for text in _row_texts(rows)]
    results: dict[str, bool] = {}
    for left, right in CHECKPOINTS:
        label = f"{left} + {right}"
        left_key = _normalize_key(left)
        right_key = _normalize_key(right)
        results[label] = any(left_key in row and right_key in row for row in row_texts)
    return results


def _lcs_len(expected: list[str], actual: list[str]) -> int:
    dp = [[0] * (len(actual) + 1) for _ in range(len(expected) + 1)]
    for i, left in enumerate(expected, start=1):
        for j, right in enumerate(actual, start=1):
            if left == right:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[-1][-1]


def _first_divergence(expected: list[str], actual: list[str]) -> dict[str, Any] | None:
    limit = max(len(expected), len(actual))
    for index in range(limit):
        left = expected[index] if index < len(expected) else None
        right = actual[index] if index < len(actual) else None
        if left != right:
            return {
                "index_1_based": index + 1,
                "expected": left,
                "actual": right,
            }
    return None


def _counter_delta(left: list[str], right: list[str]) -> tuple[list[str], list[str]]:
    left_counter = Counter(left)
    right_counter = Counter(right)
    missing = list((left_counter - right_counter).elements())
    extra = list((right_counter - left_counter).elements())
    return missing, extra


def _render_lane_html(heading_text: str, rows: Iterable[Tag]) -> str:
    rows_html = "".join(str(row) for row in rows)
    return f"<h2>{escape(heading_text)}</h2>\n<table>\n{rows_html}\n</table>\n"


def _score_candidate(
    *,
    label: str,
    path: Path,
    gold_header: list[str],
    gold_subgroups: list[str],
    outdir: Path,
) -> dict[str, Any]:
    context = _extract_candidate_context(path)
    lane_rows = _extract_lane_rows(context["table"], LANE_SUBGROUP_LIMIT)
    lane_html_path = outdir / f"{label}-arthur-lane.html"
    lane_html_path.write_text(
        _render_lane_html(context["heading_text"], lane_rows),
        encoding="utf-8",
    )

    header = _header_signature(lane_rows)
    subgroups = _subgroup_sequence(lane_rows)
    subgroups_window = subgroups[: len(gold_subgroups)]
    position_matches = sum(
        1 for expected, actual in zip(gold_subgroups, subgroups_window) if expected == actual
    )
    subgroup_lcs = _lcs_len(gold_subgroups, subgroups_window)
    subgroup_missing, subgroup_extra = _counter_delta(gold_subgroups, subgroups_window)
    leaks = _heading_like_leaks(lane_rows)
    checkpoint_results = _checkpoint_results(lane_rows)

    scores = OrderedDict(
        [
            ("header_exact", SCORE_WEIGHTS["header_exact"] if header == gold_header else 0.0),
            (
                "pretable_onset",
                SCORE_WEIGHTS["pretable_onset"]
                * max(
                    0.0,
                    1.0
                    - min(len(context["pretable_paragraphs"]), PRETABLE_PARAGRAPH_CAP)
                    / PRETABLE_PARAGRAPH_CAP,
                ),
            ),
            (
                "subgroup_lcs",
                SCORE_WEIGHTS["subgroup_lcs"]
                * (subgroup_lcs / len(gold_subgroups) if gold_subgroups else 0.0),
            ),
            (
                "subgroup_position",
                SCORE_WEIGHTS["subgroup_position"]
                * (position_matches / len(gold_subgroups) if gold_subgroups else 0.0),
            ),
            (
                "leak_hygiene",
                SCORE_WEIGHTS["leak_hygiene"]
                * max(0.0, 1.0 - min(len(leaks), LEAK_SCORE_CAP) / LEAK_SCORE_CAP),
            ),
            (
                "checkpoint_pairs",
                SCORE_WEIGHTS["checkpoint_pairs"]
                * (sum(checkpoint_results.values()) / len(checkpoint_results) if checkpoint_results else 0.0),
            ),
        ]
    )
    overall = round(sum(scores.values()), 1)

    return {
        "label": label,
        "path": str(path),
        "lane_html": str(lane_html_path),
        "overall_score": overall,
        "score_out_of": 100.0,
        "scores": scores,
        "pretable_paragraph_count": len(context["pretable_paragraphs"]),
        "pretable_paragraph_samples": context["pretable_paragraphs"][:3],
        "header_signature": header,
        "header_exact": header == gold_header,
        "subgroup_count_in_lane": len(subgroups),
        "subgroup_window_expected_count": len(gold_subgroups),
        "subgroup_window_actual_count": len(subgroups_window),
        "subgroup_window_exact": subgroups_window == gold_subgroups,
        "subgroup_lcs_len": subgroup_lcs,
        "subgroup_position_matches": position_matches,
        "first_divergence": _first_divergence(gold_subgroups, subgroups_window),
        "missing_subgroups_in_window": subgroup_missing,
        "extra_subgroups_in_window": subgroup_extra,
        "leak_count_in_lane": len(leaks),
        "leak_samples": leaks[:10],
        "specific_leak_alice_family_barbara_hodges": any(
            "alice's family barbara hodges" in _normalize_key(text) for text in leaks
        ),
        "checkpoint_results": checkpoint_results,
    }


def _summary_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Docling Arthur-Lane Parity Score",
        "",
        "This score is lane-scoped. It compares the currently accepted Arthur",
        "hard-case lane against repo-owned Onward goldens. It does not claim",
        "full-Onward parity or justify a methodology shift on its own.",
        "",
        "## Gold",
        f"- source: `{summary['gold']['path']}`",
        f"- subgroup window size: `{summary['gold']['subgroup_window_size']}`",
        f"- expected header: `{summary['gold']['header_signature']}`",
        "",
        "## Scores",
        "| Candidate | Overall | Pretable | Header | LCS | Position | Leaks | Checkpoints |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for candidate in summary["candidates"]:
        scores = candidate["scores"]
        lines.append(
            "| "
            f"`{candidate['label']}` | "
            f"`{candidate['overall_score']}` | "
            f"`{scores['pretable_onset']:.1f}` | "
            f"`{scores['header_exact']:.1f}` | "
            f"`{scores['subgroup_lcs']:.1f}` | "
            f"`{scores['subgroup_position']:.1f}` | "
            f"`{scores['leak_hygiene']:.1f}` | "
            f"`{scores['checkpoint_pairs']:.1f}` |"
        )
    lines.extend(
        [
            "",
            "## Candidate Notes",
        ]
    )
    for candidate in summary["candidates"]:
        lines.extend(
            [
                f"### `{candidate['label']}`",
                f"- input: `{candidate['path']}`",
                f"- lane html: `{candidate['lane_html']}`",
                f"- pre-table paragraphs: `{candidate['pretable_paragraph_count']}`",
                f"- header exact: `{candidate['header_exact']}`",
                f"- subgroup LCS: `{candidate['subgroup_lcs_len']}` / `{summary['gold']['subgroup_window_size']}`",
                f"- subgroup position matches: `{candidate['subgroup_position_matches']}` / `{summary['gold']['subgroup_window_size']}`",
                f"- leak count in lane: `{candidate['leak_count_in_lane']}`",
                f"- `ALICE'S FAMILY Barbara Hodges` leak still present: `{candidate['specific_leak_alice_family_barbara_hodges']}`",
            ]
        )
        divergence = candidate["first_divergence"]
        if divergence is not None:
            lines.append(
                "- first subgroup divergence: "
                f"`#{divergence['index_1_based']}` expected `{divergence['expected']}` "
                f"vs actual `{divergence['actual']}`"
            )
        if candidate["missing_subgroups_in_window"]:
            lines.append(
                "- missing subgroup markers in window: "
                + ", ".join(f"`{item}`" for item in candidate["missing_subgroups_in_window"][:10])
            )
        if candidate["extra_subgroups_in_window"]:
            lines.append(
                "- extra subgroup markers in window: "
                + ", ".join(f"`{item}`" for item in candidate["extra_subgroups_in_window"][:10])
            )
        failed_checkpoints = [
            label for label, ok in candidate["checkpoint_results"].items() if not ok
        ]
        if failed_checkpoints:
            lines.append(
                "- failed checkpoint pairs: "
                + ", ".join(f"`{item}`" for item in failed_checkpoints)
            )
        if candidate["leak_samples"]:
            lines.append(
                "- leak samples: "
                + ", ".join(f"`{item}`" for item in candidate["leak_samples"][:5])
            )
        lines.append("")

    winner = max(summary["candidates"], key=lambda item: item["overall_score"])
    lines.extend(
        [
            "## Read",
            f"- Current best candidate: `{winner['label']}` at `{winner['overall_score']}` / `100`.",
            "- A methodology shift is still blocked until the score reaches the incumbent bar on this lane and broader non-Onward checks still look thinner than the current workaround stack.",
            "",
        ]
    )
    return "\n".join(lines)


def _parse_candidates(raw_values: list[str] | None) -> OrderedDict[str, Path]:
    if not raw_values:
        return DEFAULT_CANDIDATES.copy()
    parsed: OrderedDict[str, Path] = OrderedDict()
    for raw in raw_values:
        if "=" not in raw:
            raise ValueError(f"Candidate must use label=path format: {raw}")
        label, raw_path = raw.split("=", 1)
        parsed[label.strip()] = Path(raw_path.strip())
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Score Arthur-lane parity against incumbent Onward gold.")
    parser.add_argument("--gold-html", default=str(DEFAULT_GOLD))
    parser.add_argument("--outdir", default=str(DEFAULT_OUTDIR))
    parser.add_argument(
        "--candidate",
        action="append",
        help="Candidate in label=path form. Defaults to baseline-images and hybrid-two-page.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    gold_path = Path(args.gold_html)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    candidates = _parse_candidates(args.candidate)
    gold_context = _extract_gold_context(gold_path)
    gold_lane_rows = _extract_lane_rows(gold_context["table"], LANE_SUBGROUP_LIMIT)
    gold_lane_path = outdir / "gold-arthur-lane.html"
    gold_lane_path.write_text(
        _render_lane_html(gold_context["heading_text"], gold_lane_rows),
        encoding="utf-8",
    )
    gold_header = _header_signature(gold_lane_rows)
    gold_subgroups = _subgroup_sequence(gold_lane_rows)[:LANE_SUBGROUP_LIMIT]

    summary = {
        "schema_version": "story158_docling_arthur_lane_parity_v1",
        "gold": {
            "path": str(gold_path),
            "lane_html": str(gold_lane_path),
            "header_signature": gold_header,
            "subgroup_window_size": len(gold_subgroups),
            "subgroup_window": gold_subgroups,
            "checkpoint_pairs": [f"{left} + {right}" for left, right in CHECKPOINTS],
        },
        "weights": SCORE_WEIGHTS,
        "candidates": [],
    }

    for label, path in candidates.items():
        summary["candidates"].append(
            _score_candidate(
                label=label,
                path=path,
                gold_header=gold_header,
                gold_subgroups=gold_subgroups,
                outdir=outdir,
            )
        )

    summary_path = outdir / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown_path = outdir / "summary.md"
    markdown_path.write_text(_summary_markdown(summary), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
