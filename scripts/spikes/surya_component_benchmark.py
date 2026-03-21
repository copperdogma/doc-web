#!/usr/bin/env python3
"""
Run a bounded Surya component benchmark on repo-local Onward artifacts.

The current local Surya substrate is intentionally narrow:
- verified working runtime: .venv-story164-surya-045 with surya-ocr==0.4.5
- verified CLI surface: layout / detect / ocr / order
- unverified here: current upstream surya_table on a runnable runtime

This spike therefore benchmarks page-level layout/table detection signals first,
using reviewed Onward artifacts already present in the repo and output/runs/.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LAYOUT_BIN = REPO_ROOT / ".venv-story164-surya-045" / "bin" / "surya_layout"
DEFAULT_RUNTIME_PYTHON = REPO_ROOT / ".venv-story164-surya-045" / "bin" / "python"
DEFAULT_OUT_ROOT = REPO_ROOT / "output" / "runs" / "story164-surya-benchmark-r1"

FAMILY_HEADING_RE = re.compile(
    r"(?:\bgrandchildren\b|\bchildren\b|\b[A-Z][A-Z' -]+FAMILY\b)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class LanePage:
    image_name: str
    gold_page_html: Path
    gold_page_label: str


@dataclass(frozen=True)
class LaneConfig:
    lane_id: str
    document_title: str
    image_dir: Path
    pages: tuple[LanePage, ...]
    gold_lane_html: Path
    reviewed_lane_html: Path
    incumbent_summary: Path
    mapping_note: str


LANES: dict[str, LaneConfig] = {
    "marie-louise": LaneConfig(
        lane_id="marie-louise",
        document_title="Marie-Louise (L'Heureux) LaClare",
        image_dir=REPO_ROOT
        / "output/runs/story163-docling-plugin-killtest-r2/marie-louise/docling/"
        / "plugin-onward-layout-table-v1/images",
        pages=(
            LanePage("page-001.png", REPO_ROOT / "benchmarks/golden/onward/per_page/page_079.html", "page_079"),
            LanePage("page-002.png", REPO_ROOT / "benchmarks/golden/onward/per_page/page_080.html", "page_080"),
            LanePage("page-003.png", REPO_ROOT / "benchmarks/golden/onward/per_page/page_081.html", "page_081"),
            LanePage("page-004.png", REPO_ROOT / "benchmarks/golden/onward/per_page/page_082.html", "page_082"),
            LanePage("page-005.png", REPO_ROOT / "benchmarks/golden/onward/per_page/page_083.html", "page_083"),
        ),
        gold_lane_html=REPO_ROOT / "benchmarks/golden/onward/marie_louise.html",
        reviewed_lane_html=REPO_ROOT
        / "benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/chapter-017.html",
        incumbent_summary=REPO_ROOT
        / "output/runs/story163-docling-plugin-killtest-r2/marie-louise/docling/"
        / "plugin-onward-layout-table-v1/summary.json",
        mapping_note=(
            "Uses the first five extracted page images from the split Marie-Louise PDF "
            "as the overlapping subset for committed gold pages 079-083. This is an "
            "explicit sequential-page assumption tied to the split-PDF lane."
        ),
    )
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> Any:
    return json.loads(_read_text(path))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _table_area_ratio(box: dict[str, Any], image_bbox: list[float]) -> float:
    x1, y1, x2, y2 = box["bbox"]
    ix1, iy1, ix2, iy2 = image_bbox
    box_area = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    image_area = max(1.0, ix2 - ix1) * max(1.0, iy2 - iy1)
    return box_area / image_area


def _gold_page_signals(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    heading_rows = 0
    data_rows = 0
    for tr in soup.find_all("tr"):
        text = " ".join(part.strip() for part in tr.stripped_strings).strip()
        cells = tr.find_all(["td", "th"])
        if not cells or not text:
            continue
        if FAMILY_HEADING_RE.search(text) and len(cells) <= 2:
            heading_rows += 1
        if len(tr.find_all("td")) >= 2:
            data_rows += 1
    return {
        "has_table": bool(tables),
        "table_count": len(tables),
        "heading_like_row_count": heading_rows,
        "data_row_count": data_rows,
    }


def _page_summary(page_output: dict[str, Any], gold_page_html: Path) -> dict[str, Any]:
    gold_signals = _gold_page_signals(_read_text(gold_page_html))
    image_bbox = page_output.get("image_bbox") or [0.0, 0.0, 1.0, 1.0]
    bboxes = page_output.get("bboxes", [])
    label_counts = Counter(box.get("label", "UNKNOWN") for box in bboxes)
    table_boxes = [box for box in bboxes if box.get("label") == "Table"]
    largest_table_ratio = max(
        (_table_area_ratio(box, image_bbox) for box in table_boxes),
        default=0.0,
    )
    return {
        "gold": gold_signals,
        "surya": {
            "bbox_count": len(bboxes),
            "label_counts": dict(sorted(label_counts.items())),
            "table_box_count": len(table_boxes),
            "has_table_box": bool(table_boxes),
            "largest_table_area_ratio": round(largest_table_ratio, 4),
            "boxes": bboxes,
        },
    }


def _runtime_metadata(runtime_python: Path, layout_bin: Path) -> dict[str, Any]:
    cmd = [
        str(runtime_python),
        "-c",
        (
            "import importlib.metadata as m, json;"
            "dist=m.distribution('surya-ocr');"
            "print(json.dumps({'version': dist.version, 'license': dist.metadata.get('License', ''),"
            "'summary': dist.metadata.get('Summary', '')}))"
        ),
    ]
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    package_meta = json.loads(proc.stdout)
    return {
        "layout_bin": str(layout_bin),
        "runtime_python": str(runtime_python),
        "package": package_meta,
        "supported_cli_surface": [
            name
            for name in ("surya_detect", "surya_gui", "surya_layout", "surya_ocr", "surya_order")
            if (layout_bin.parent / name).exists()
        ],
        "missing_current_cli_surface": [
            name
            for name in ("surya_table", "surya_latex_ocr")
            if not (layout_bin.parent / name).exists()
        ],
    }


def _prepare_input_dir(lane: LaneConfig, out_dir: Path) -> Path:
    input_dir = out_dir / "input-pages"
    if input_dir.exists():
        shutil.rmtree(input_dir)
    input_dir.mkdir(parents=True, exist_ok=True)
    for lane_page in lane.pages:
        src = lane.image_dir / lane_page.image_name
        if not src.exists():
            raise FileNotFoundError(f"Missing lane image: {src}")
        target = input_dir / lane_page.image_name
        target.symlink_to(src.resolve())
    return input_dir


def _run_layout(layout_bin: Path, input_dir: Path, out_dir: Path) -> tuple[Path, dict[str, str]]:
    cmd = [str(layout_bin), str(input_dir), "--results_dir", str(out_dir)]
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    stdout_path = out_dir / "surya_layout.stdout.log"
    stderr_path = out_dir / "surya_layout.stderr.log"
    stdout_path.write_text(proc.stdout, encoding="utf-8")
    stderr_path.write_text(proc.stderr, encoding="utf-8")
    results_path = out_dir / input_dir.name / "results.json"
    if not results_path.exists():
        raise FileNotFoundError(f"Surya results missing: {results_path}")
    return results_path, {"stdout": str(stdout_path), "stderr": str(stderr_path)}


def _decision(page_summaries: dict[str, Any]) -> dict[str, Any]:
    overlap_pages = 0
    gold_table_pages = 0
    detected_table_pages = 0
    false_positive_pages = 0
    large_table_pages = 0
    for summary in page_summaries.values():
        gold = summary["gold"]
        surya = summary["surya"]
        overlap_pages += 1
        if gold["has_table"]:
            gold_table_pages += 1
            if surya["has_table_box"]:
                detected_table_pages += 1
                if surya["largest_table_area_ratio"] >= 0.35:
                    large_table_pages += 1
        elif surya["has_table_box"]:
            false_positive_pages += 1

    table_recall = detected_table_pages / gold_table_pages if gold_table_pages else 0.0
    large_table_recall = large_table_pages / gold_table_pages if gold_table_pages else 0.0
    if table_recall >= 0.95 and false_positive_pages == 0 and large_table_recall >= 0.75:
        decision = "positive_for_table_page_detection_only"
        pressure_read = (
            "Surya layout is strong enough to propose as an upstream table-page or crop-routing "
            "signal, but not strong enough yet to claim pressure relief on row/group reconstruction."
        )
        next_step = (
            "Only justify a follow-on if the repo wants a narrow routing-only probe. "
            "Do not treat this as a table-structure replacement."
        )
    else:
        decision = "negative_for_immediate_adoption"
        pressure_read = (
            "Surya layout does not show a clean enough page-routing win to justify even a narrow "
            "integration probe on this seam."
        )
        next_step = "Stop after updating scout/build-map surfaces."
    return {
        "decision": decision,
        "table_page_recall": round(table_recall, 4),
        "large_table_recall": round(large_table_recall, 4),
        "false_positive_pages": false_positive_pages,
        "pressure_read": pressure_read,
        "next_step": next_step,
    }


def run_lane(lane: LaneConfig, layout_bin: Path, runtime_python: Path, out_root: Path) -> dict[str, Any]:
    out_dir = out_root / lane.lane_id / "surya-layout-v045"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    input_dir = _prepare_input_dir(lane, out_dir)
    results_path, log_paths = _run_layout(layout_bin, input_dir, out_dir)
    results = _read_json(results_path)

    page_summaries: dict[str, Any] = {}
    for lane_page in lane.pages:
        key = Path(lane_page.image_name).stem
        page_output = results[key][0]
        page_summaries[lane_page.gold_page_label] = {
            "image_name": lane_page.image_name,
            "results_key": key,
            **_page_summary(page_output, lane_page.gold_page_html),
        }

    incumbent = _read_json(lane.incumbent_summary)
    decision = _decision(page_summaries)
    summary = {
        "schema_version": "story164_surya_component_benchmark_v1",
        "lane_id": lane.lane_id,
        "document_title": lane.document_title,
        "mapping_note": lane.mapping_note,
        "runtime": _runtime_metadata(runtime_python, layout_bin),
        "input_artifacts": {
            "image_dir": str(lane.image_dir),
            "selected_images": [page.image_name for page in lane.pages],
            "gold_lane_html": str(lane.gold_lane_html),
            "reviewed_lane_html": str(lane.reviewed_lane_html),
            "incumbent_summary": str(lane.incumbent_summary),
        },
        "artifacts": {
            "results_json": str(results_path),
            "stdout_log": log_paths["stdout"],
            "stderr_log": log_paths["stderr"],
            "input_pages_dir": str(input_dir),
        },
        "page_summaries": page_summaries,
        "incumbent_snapshot": {
            "plugin_signals": incumbent.get("plugin_signals"),
            "gold_signals": incumbent.get("gold_signals"),
        },
        "decision": decision,
    }
    _write_json(out_dir / "summary.json", summary)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", choices=sorted(LANES), default="marie-louise")
    parser.add_argument("--layout-bin", type=Path, default=DEFAULT_LAYOUT_BIN)
    parser.add_argument("--runtime-python", type=Path, default=DEFAULT_RUNTIME_PYTHON)
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = run_lane(
        lane=LANES[args.lane],
        layout_bin=args.layout_bin,
        runtime_python=args.runtime_python,
        out_root=args.out_root,
    )
    print(json.dumps(summary["decision"], indent=2))
    print(f"Summary written to {args.out_root / args.lane / 'surya-layout-v045' / 'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
