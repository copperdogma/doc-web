#!/usr/bin/env python3
"""Build and run a bounded DiEm HTR benchmark for Story 212.

This is a story-local, comparison-only harness. The canonical decision surface
is the source-native image-entry OCR path; `--include-pdf` is available only
for extra PDF-entry stress. The helper expects `huggingface_hub`, `pandas`
plus a parquet engine such as `pyarrow`, `Pillow`, and `pypdf` to be
installed in the local environment.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from doc_web.env import build_child_env

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - exercised only in missing-dependency envs
    Image = None
    PIL_IMPORT_ERROR = exc
else:
    PIL_IMPORT_ERROR = None

try:
    from pypdf import PdfReader
except ImportError as exc:  # pragma: no cover - exercised only in missing-dependency envs
    PdfReader = None
    PYPDF_IMPORT_ERROR = exc
else:
    PYPDF_IMPORT_ERROR = None

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.scorers.handwritten_notes_transcription import score_page_html_artifact, score_text_pair  # noqa: E402
from benchmarks.scripts.run_handwritten_notes_eval import build_run_id, load_case_instrumentation  # noqa: E402


DATASET_REPO = "RA-Data-Science/DiEm_HTR"
DATASET_CARD_URL = "https://huggingface.co/datasets/RA-Data-Science/DiEm_HTR"
DATASET_LICENSE = "CC BY 4.0"
DATASET_LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
PARQUET_PATH_IN_REPO = "data/DiEm_GT_HTR.parquet"
README_PATH_IN_REPO = "README.md"
DEFAULT_OUT_ROOT = ROOT / "output" / "runs" / "story212-diem-htr-benchmark-r1"
DEFAULT_IMAGE_RECIPE = "configs/recipes/recipe-images-ocr-html-handwritten-notes-gemini-rescue.yaml"
DEFAULT_PDF_RECIPE = "configs/recipes/recipe-pdf-ocr-html-handwritten-notes-gemini-rescue.yaml"
DEFAULT_IMAGE_CASE_ID = "image-handwritten-rescue"
DEFAULT_PDF_CASE_ID = "pdf-handwritten-rescue"
PAGE_SEPARATOR = "===PAGE==="
PAGE_NS = {"p": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"}
ALTO_NS = {"a": "http://www.loc.gov/standards/alto/ns-v4#"}
CLI_EPILOG = (
    "Dependencies: huggingface_hub, pandas plus a parquet engine such as pyarrow, "
    "Pillow, and pypdf.\n"
    "Default behavior runs the image-entry comparison-only benchmark and leaves "
    "PDF-entry probes opt-in via --include-pdf."
)


@dataclass(frozen=True)
class DiemSlicePage:
    fixture_id: str
    doc_id: str
    sequence: int
    parish_name: str
    period: str
    events: str
    transcribed: str
    notes: str
    rationale: str
    physical_page_count: int = 2


STORY212_SLICE = (
    DiemSlicePage(
        fixture_id="diem-vinding-27",
        doc_id="8033700071-12391767",
        sequence=27,
        parish_name="Vinding Sogn (Vejle Amt)",
        period="1651-1749",
        events="Births and baptisms, Marriages, Burials",
        transcribed="Volunteers have manually transcribed the book.",
        notes=(
            "We only made parts of this book Ground Truth because of its bad condition and layout. "
            "Pages from 1657 up to and including 1735 is Ground Truth from this book."
        ),
        rationale="Hard-condition page chosen to pressure the line the dataset card explicitly calls out as layout-troublesome.",
    ),
    DiemSlicePage(
        fixture_id="diem-tranekaer-28",
        doc_id="8034392541-22064545",
        sequence=28,
        parish_name="Tranekær Sogn",
        period="1812-1818",
        events="Communion and Confirmations",
        transcribed="An early version of the DiEm project text recognition model recognised the book.",
        notes="Selected to add a narrow portrait-oriented list/index layout from the corrected-model subset.",
        rationale="Different geometry and content pattern than the denser baptism/marriage spreads.",
    ),
    DiemSlicePage(
        fixture_id="diem-jersie-76",
        doc_id="8010610941-6469506",
        sequence=76,
        parish_name="Jersie Sogn",
        period="1747-1814",
        events="Births and baptisms, Confirmations, Marriages, Burials",
        transcribed="Volunteers have manually transcribed the book.",
        notes="Selected to provide a wide dense marriage-record spread from the manual Ground Truth subset.",
        rationale="Wide spread with heavy cursive density to contrast against the portrait-oriented selections.",
    ),
)


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _require_pillow():
    if Image is None:
        raise RuntimeError("Pillow is required to materialize the DiEm benchmark artifacts") from PIL_IMPORT_ERROR
    return Image


def _require_pypdf():
    if PdfReader is None:
        raise RuntimeError("pypdf is required for optional PDF-entry DiEm benchmark probes") from PYPDF_IMPORT_ERROR
    return PdfReader


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _dataset_snapshot_id(path: Path) -> str:
    for parent in path.parents:
        if parent.parent.name == "snapshots":
            return parent.name
    raise ValueError(f"Could not infer snapshot id from path: {path}")


def load_diem_dataframe(parquet_path: Path):
    try:
        import pandas as pd
    except ImportError as exc:
        raise RuntimeError("pandas is required to load the DiEm parquet benchmark surface") from exc

    try:
        return pd.read_parquet(parquet_path)
    except ImportError as exc:
        raise RuntimeError(
            "Reading the DiEm parquet requires a parquet engine such as pyarrow. "
            "Install `pyarrow` locally before running this helper."
        ) from exc


def extract_page_lines(page_xml: str) -> list[str]:
    root = ET.fromstring(page_xml)
    region_map = {region.get("id"): region for region in root.findall(".//p:TextRegion", PAGE_NS) if region.get("id")}
    ordered_regions = []
    seen_ids: set[str] = set()
    refs = sorted(
        (
            int(ref.get("index", "0")),
            ref.get("regionRef"),
        )
        for ref in root.findall(".//p:RegionRefIndexed", PAGE_NS)
        if ref.get("regionRef")
    )
    for _, region_id in refs:
        region = region_map.get(region_id)
        if region is not None and region_id not in seen_ids:
            ordered_regions.append(region)
            seen_ids.add(region_id)
    for region_id, region in region_map.items():
        if region_id not in seen_ids:
            ordered_regions.append(region)

    lines: list[str] = []
    regions_to_scan = ordered_regions or root.findall(".//p:TextRegion", PAGE_NS)
    for region in regions_to_scan:
        for line in region.findall(".//p:TextLine", PAGE_NS):
            unicode_node = line.find(".//p:Unicode", PAGE_NS)
            text = (unicode_node.text or "").strip() if unicode_node is not None else ""
            if text:
                lines.append(text)

    if lines:
        return lines

    fallback_lines: list[str] = []
    for line in root.findall(".//p:TextLine", PAGE_NS):
        unicode_node = line.find(".//p:Unicode", PAGE_NS)
        text = (unicode_node.text or "").strip() if unicode_node is not None else ""
        if text:
            fallback_lines.append(text)
    return fallback_lines


def extract_alto_lines(alto_xml: str) -> list[str]:
    root = ET.fromstring(alto_xml)
    lines: list[str] = []
    for line in root.findall(".//a:TextLine", ALTO_NS):
        strings = [node.get("CONTENT", "").strip() for node in line.findall(".//a:String", ALTO_NS)]
        text = " ".join(part for part in strings if part).strip()
        if text:
            lines.append(text)
    return lines


def build_story212_transcript(pages: list[list[str]]) -> str:
    rendered_pages = ["\n".join(lines).strip() for lines in pages]
    return f"\n\n{PAGE_SEPARATOR}\n\n".join(rendered_pages).strip() + "\n"


def classify_geometry(width: int, height: int) -> str:
    ratio = width / height
    if ratio >= 1.2:
        return "landscape-spread"
    if ratio <= 0.8:
        return "portrait-spread"
    return "near-square-spread"


def _row_image_bytes(row_image: Any) -> bytes:
    if isinstance(row_image, (bytes, bytearray)):
        return bytes(row_image)
    if isinstance(row_image, dict):
        image_bytes = row_image.get("bytes")
        if isinstance(image_bytes, (bytes, bytearray)):
            return bytes(image_bytes)
    raise TypeError(f"Unsupported image payload type: {type(row_image).__name__}")


def _save_pdf(image_paths: list[Path], pdf_path: Path) -> None:
    image_lib = _require_pillow()
    converted = []
    try:
        for path in image_paths:
            with image_lib.open(path) as image:
                converted.append(image.convert("RGB"))
        first, *rest = converted
        first.save(pdf_path, save_all=True, append_images=rest)
    finally:
        for image in converted:
            image.close()


def should_retry_transient_eval_failure(stdout: str, stderr: str) -> bool:
    haystack = f"{stdout}\n{stderr}"
    return "503 UNAVAILABLE" in haystack and "currently experiencing high demand" in haystack


def _build_eval_env() -> dict[str, str]:
    env = build_child_env()
    env["PYTHONPATH"] = str(ROOT)
    return env


def materialize_story212_slice(out_root: Path) -> dict[str, Any]:
    image_lib = _require_pillow()
    try:
        from huggingface_hub import hf_hub_download
    except ImportError as exc:
        raise RuntimeError("huggingface_hub is required to fetch the DiEm snapshot") from exc

    parquet_path = Path(hf_hub_download(DATASET_REPO, PARQUET_PATH_IN_REPO, repo_type="dataset"))
    readme_path = Path(hf_hub_download(DATASET_REPO, README_PATH_IN_REPO, repo_type="dataset"))
    snapshot_id = _dataset_snapshot_id(parquet_path)
    dataframe = load_diem_dataframe(parquet_path)

    slice_root = _ensure_dir(out_root / "diem_slice")
    fixtures_root = _ensure_dir(slice_root / "fixtures")
    page_entries: list[dict[str, Any]] = []
    corpus_fixtures: list[dict[str, Any]] = []

    for index, spec in enumerate(STORY212_SLICE, start=1):
        rows = dataframe[(dataframe["doc_id"] == spec.doc_id) & (dataframe["sequence"] == spec.sequence)]
        if rows.empty:
            raise ValueError(f"Missing selected DiEm row: {spec.doc_id} sequence {spec.sequence}")
        row = rows.iloc[0]
        image_bytes = _row_image_bytes(row["image"])
        page_xml = row["page"]
        alto_xml = row["alto"]

        fixture_root = _ensure_dir(fixtures_root / spec.fixture_id)
        images_dir = _ensure_dir(fixture_root / "images")
        page_dir = _ensure_dir(fixture_root / "page")
        alto_dir = _ensure_dir(fixture_root / "alto")
        transcript_dir = _ensure_dir(fixture_root / "transcripts")

        image_path = images_dir / "page-001.jpg"
        image_path.write_bytes(image_bytes)

        page_xml_path = page_dir / "page-001.xml"
        page_xml_path.write_text(page_xml, encoding="utf-8")
        alto_xml_path = alto_dir / "page-001.xml"
        alto_xml_path.write_text(alto_xml, encoding="utf-8")

        with image_lib.open(io.BytesIO(image_bytes)) as image:
            width, height = image.size

        page_lines = extract_page_lines(page_xml)
        alto_lines = extract_alto_lines(alto_xml)

        transcript_path = fixture_root / "transcript.txt"
        transcript_path.write_text(build_story212_transcript([page_lines]), encoding="utf-8")
        page_transcript_path = transcript_dir / "page-001.txt"
        page_transcript_path.write_text("\n".join(page_lines) + "\n", encoding="utf-8")

        pdf_path = fixture_root / f"{spec.fixture_id}.pdf"
        _save_pdf([image_path], pdf_path)

        parity = score_text_pair("\n".join(page_lines), "\n".join(alto_lines))
        page_entries.append(
            {
                **asdict(spec),
                "slice_page_number": index,
                "fixture_root": str(fixture_root),
                "geometry": {
                    "width": width,
                    "height": height,
                    "label": classify_geometry(width, height),
                },
                "image_path": str(image_path),
                "images_dir": str(images_dir),
                "pdf_path": str(pdf_path),
                "page_xml_path": str(page_xml_path),
                "alto_xml_path": str(alto_xml_path),
                "transcript_path": str(transcript_path),
                "page_line_count": len(page_lines),
                "alto_line_count": len(alto_lines),
                "page_alto_text_ratio": parity["ratio"],
                "preview": page_lines[:5],
            }
        )
        corpus_fixtures.append(
            {
                "id": spec.fixture_id,
                "label": f"DiEm {spec.parish_name} sequence {spec.sequence}",
                "difficulty": "historical-handwriting-external",
                "source_type": "external-diem-htr",
                "transcript": str(transcript_path),
                "images": str(images_dir),
                "pdf": str(pdf_path),
            }
        )

    corpus_path = slice_root / "corpus.json"
    _write_json(corpus_path, {"fixtures": corpus_fixtures})

    manifest = {
        "story": "212",
        "kind": "comparison-only external benchmark slice",
        "dataset": {
            "repo": DATASET_REPO,
            "snapshot": snapshot_id,
            "dataset_card_url": DATASET_CARD_URL,
            "dataset_card_path": str(readme_path),
            "parquet_path": str(parquet_path),
            "license": DATASET_LICENSE,
            "license_url": DATASET_LICENSE_URL,
            "selection_basis": (
                "The DiEm dataset card says the books were selected to represent handwriting variance "
                "through 1650-1800 and multiple parish-register event types, and that each row may contain "
                "one or two physical pages."
            ),
        },
        "slice": {
            "corpus_path": str(corpus_path),
            "pages": page_entries,
        },
    }
    _write_json(slice_root / "slice_manifest.json", manifest)
    return manifest


def run_story212_eval(
    *,
    out_root: Path,
    slice_manifest: dict[str, Any],
    image_recipe: str,
    pdf_recipe: str,
    image_case_id: str,
    pdf_case_id: str,
    include_pdf: bool,
    max_attempts: int,
) -> dict[str, Any]:
    def run_driver_case_with_retries(
        *,
        fixture_id: str,
        transcript_path: str,
        case_id: str,
        recipe: str,
        input_flag: str,
        input_path: str,
    ) -> dict[str, Any]:
        env = _build_eval_env()
        run_id = build_run_id(fixture_id, case_id)
        case_attempts: list[dict[str, Any]] = []
        for attempt in range(1, max_attempts + 1):
            cmd = [
                sys.executable,
                "driver.py",
                "--recipe",
                recipe,
                input_flag,
                input_path,
                "--run-id",
                run_id,
                "--allow-run-id-reuse",
                "--force",
                "--end-at",
                "ocr_ai",
                "--instrument",
            ]
            result = subprocess.run(
                cmd,
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
            retryable = should_retry_transient_eval_failure(result.stdout, result.stderr)
            case_attempts.append(
                {
                    "attempt": attempt,
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "retryable": retryable,
                }
            )
            if result.returncode == 0:
                artifact_path = ROOT / "output" / "runs" / run_id / "02_ocr_ai_gpt51_v1" / "pages_html.jsonl"
                if not artifact_path.exists():
                    raise RuntimeError(f"Expected artifact missing after successful run: {artifact_path}")
                metrics = score_page_html_artifact(transcript_path, artifact_path)
                payload = {
                    "fixture_id": fixture_id,
                    "case_id": case_id,
                    "run_id": run_id,
                    "recipe": recipe,
                    "input_flag": input_flag,
                    "input_path": input_path,
                    "artifact_path": str(artifact_path),
                    "metrics": metrics,
                    "pass": metrics["overall_ratio"] >= 0.99 and metrics["page_min_ratio"] >= 0.99,
                    "attempts": case_attempts,
                }
                instrumentation = load_case_instrumentation(run_id)
                if instrumentation:
                    payload["instrumentation"] = instrumentation
                return payload
            if attempt >= max_attempts or not retryable:
                raise RuntimeError(f"Case {fixture_id}/{case_id} failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
        raise RuntimeError(f"Case {fixture_id}/{case_id} exhausted retries without producing an artifact")

    fixture_results = []
    scored_cases = []
    all_attempts: list[dict[str, Any]] = []

    for page in slice_manifest["slice"]["pages"]:
        image_case = run_driver_case_with_retries(
            fixture_id=page["fixture_id"],
            transcript_path=page["transcript_path"],
            case_id=image_case_id,
            recipe=image_recipe,
            input_flag="--input-images",
            input_path=page["images_dir"],
        )
        fixture_cases = [image_case]
        scored_cases.append(image_case)
        all_attempts.append({"fixture_id": page["fixture_id"], "case_id": image_case_id, "attempts": image_case["attempts"]})

        pdf_extract_lengths = None
        if include_pdf:
            pdf_reader_cls = _require_pypdf()
            pdf_case = run_driver_case_with_retries(
                fixture_id=page["fixture_id"],
                transcript_path=page["transcript_path"],
                case_id=pdf_case_id,
                recipe=pdf_recipe,
                input_flag="--input-pdf",
                input_path=page["pdf_path"],
            )
            fixture_cases.append(pdf_case)
            scored_cases.append(pdf_case)
            all_attempts.append({"fixture_id": page["fixture_id"], "case_id": pdf_case_id, "attempts": pdf_case["attempts"]})

            pdf_reader = pdf_reader_cls(page["pdf_path"])
            pdf_extract_lengths = [len((pdf_page.extract_text() or "").strip()) for pdf_page in pdf_reader.pages]
        fixture_results.append(
            {
                "fixture_id": page["fixture_id"],
                "label": f"DiEm {page['parish_name']} sequence {page['sequence']}",
                "difficulty": "historical-handwriting-external",
                "source_type": "external-diem-htr",
                "transcript_path": page["transcript_path"],
                "images_path": page["images_dir"],
                "pdf_path": page["pdf_path"],
                "pdf_extractable_text_lengths": pdf_extract_lengths,
                "cases": fixture_cases,
                "summary": {
                    "pass_rate": round(sum(1 for case in fixture_cases if case["pass"]) / len(fixture_cases), 6),
                    "overall_min_ratio": min(case["metrics"]["overall_ratio"] for case in fixture_cases),
                    "page_min_ratio": min(case["metrics"]["page_min_ratio"] for case in fixture_cases),
                    "cases_passing": sum(1 for case in fixture_cases if case["pass"]),
                    "cases_total": len(fixture_cases),
                },
            }
        )

    payload = {
        "measured_at": datetime.now().astimezone().date().isoformat(),
        "corpus_path": slice_manifest["slice"]["corpus_path"],
        "image_recipe": image_recipe,
        "pdf_recipe": pdf_recipe,
        "image_case_id": image_case_id,
        "pdf_case_id": pdf_case_id,
        "instrument": True,
        "fixtures": fixture_results,
        "cases": scored_cases,
        "summary": {
            "pass_rate": round(sum(1 for case in scored_cases if case["pass"]) / len(scored_cases), 6),
            "overall_min_ratio": min(case["metrics"]["overall_ratio"] for case in scored_cases),
            "page_min_ratio": min(case["metrics"]["page_min_ratio"] for case in scored_cases),
            "cases_passing": sum(1 for case in scored_cases if case["pass"]),
            "cases_total": len(scored_cases),
            "fixture_count": len(fixture_results),
            "fixtures_passing": sum(1 for fixture in fixture_results if fixture["summary"]["pass_rate"] == 1.0),
            "pdf_extractable_text_lengths": {
                fixture["fixture_id"]: fixture["pdf_extractable_text_lengths"]
                for fixture in fixture_results
                if fixture["pdf_extractable_text_lengths"] is not None
            },
        },
        "attempts": all_attempts,
    }
    output_path = out_root / "handwritten_eval.json"
    _write_json(output_path, payload)
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=CLI_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--out-root", default=str(DEFAULT_OUT_ROOT))
    parser.add_argument("--image-recipe", default=DEFAULT_IMAGE_RECIPE)
    parser.add_argument("--pdf-recipe", default=DEFAULT_PDF_RECIPE)
    parser.add_argument("--image-case-id", default=DEFAULT_IMAGE_CASE_ID)
    parser.add_argument("--pdf-case-id", default=DEFAULT_PDF_CASE_ID)
    parser.add_argument("--include-pdf", action="store_true")
    parser.add_argument("--max-attempts", type=int, default=2)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    out_root = Path(args.out_root)
    if not out_root.is_absolute():
        out_root = ROOT / out_root
    _ensure_dir(out_root)

    slice_manifest = materialize_story212_slice(out_root)
    eval_payload = run_story212_eval(
        out_root=out_root,
        slice_manifest=slice_manifest,
        image_recipe=args.image_recipe,
        pdf_recipe=args.pdf_recipe,
        image_case_id=args.image_case_id,
        pdf_case_id=args.pdf_case_id,
        include_pdf=args.include_pdf,
        max_attempts=args.max_attempts,
    )

    summary = {
        "story": "212",
        "out_root": str(out_root),
        "slice_manifest_path": str(out_root / "diem_slice" / "slice_manifest.json"),
        "benchmark_output_path": str(out_root / "handwritten_eval.json"),
        "recipes": {
            "image": args.image_recipe,
            "pdf": args.pdf_recipe,
            "image_case_id": args.image_case_id,
            "pdf_case_id": args.pdf_case_id,
            "include_pdf": args.include_pdf,
            "max_attempts": args.max_attempts,
            "env_policy": "map DOC_WEB_GEMINI_API_KEY for child provider clients",
        },
        "dataset": slice_manifest["dataset"],
        "slice": slice_manifest["slice"],
        "benchmark_summary": eval_payload["summary"],
        "attempts": eval_payload.get("attempts", []),
        "benchmark_cases": [
            {
                "fixture_id": case["fixture_id"],
                "case_id": case["case_id"],
                "run_id": case["run_id"],
                "artifact_path": case["artifact_path"],
                "overall_ratio": case["metrics"]["overall_ratio"],
                "page_min_ratio": case["metrics"]["page_min_ratio"],
            }
            for case in eval_payload["cases"]
        ],
    }
    _write_json(out_root / "benchmark_summary.json", summary)
    print(json.dumps(summary["benchmark_summary"], indent=2))
    print(f"RESULT_PATH {out_root / 'benchmark_summary.json'}")


if __name__ == "__main__":
    main()
