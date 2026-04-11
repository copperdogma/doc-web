#!/usr/bin/env python3
"""Build and run a bounded LOC George Washington Papers benchmark for Story 214.

This is a story-local, comparison-only harness. The canonical decision surface
is the source-native image-entry OCR path; `--include-pdf` adds PDF-entry
stress only. The helper uses the Python standard library for HTTP, ZIP, and
CSV handling and reuses the existing handwritten eval/scoring path for OCR
comparison.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import subprocess
import sys
import urllib.request
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

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

from benchmarks.scorers.handwritten_notes_transcription import score_page_html_artifact  # noqa: E402
from benchmarks.scripts.run_handwritten_notes_eval import build_run_id, load_case_instrumentation  # noqa: E402


DATASET_ITEM_URL = "https://www.loc.gov/item/2020446971/"
DATASET_ITEM_JSON_URL = "https://www.loc.gov/item/2020446971/?fo=json"
DATASET_ZIP_URL = "https://tile.loc.gov/storage-services/master/gdc/gdcdatasets/2020446971/2020446971.zip"
DATASET_RIGHTS_NOTE = "By the People volunteer text is released into the public domain."
DATASET_SOURCE_NOTE = (
    "The source images remain Library of Congress George Washington Papers assets surfaced via the "
    "dataset CSV's DownloadUrl field."
)
DEFAULT_OUT_ROOT = ROOT / "output" / "runs" / "story214-loc-gw-benchmark-r1"
DEFAULT_IMAGE_RECIPE = "configs/recipes/recipe-images-ocr-html-handwritten-notes-gemini-rescue.yaml"
DEFAULT_PDF_RECIPE = "configs/recipes/recipe-pdf-ocr-html-handwritten-notes-gemini-rescue.yaml"
DEFAULT_IMAGE_CASE_ID = "image-handwritten-rescue"
DEFAULT_PDF_CASE_ID = "pdf-handwritten-rescue"
DEFAULT_ZIP_NAME = "2020446971.zip"
USER_AGENT = "doc-forge-story214-loc-gw-benchmark/1.0"
CLI_EPILOG = (
    "Default behavior runs the image-entry comparison-only benchmark only. "
    "Pass --include-pdf to create one-page PDF wrappers and stress the PDF-entry OCR lane as well."
)


@dataclass(frozen=True)
class LocGwSliceAsset:
    fixture_id: str
    asset_id: str
    asset: str
    item_id: str
    project: str
    rationale: str


STORY214_SLICE = (
    LocGwSliceAsset(
        fixture_id="loc-gw-interrogations-367413",
        asset_id="367413",
        asset="mgw6a00007-4",
        item_id="mgw6a00007",
        project="Interrogations of British Deserters During the Revolutionary War, 1782-1783",
        rationale=(
            "Dense prose-plus-list military interrogation page chosen to keep pressure close to the "
            "blocked English historical-handwriting seam while avoiding a purely numeric ledger page."
        ),
    ),
    LocGwSliceAsset(
        fixture_id="loc-gw-receipts-367466",
        asset_id="367466",
        asset="mgw500029-9",
        item_id="mgw500029",
        project="Revolutionary War Receipts, 1776-1780",
        rationale=(
            "Semi-structured receipt page chosen because exploration showed it can collapse all the way "
            "to empty OCR output, which is useful negative evidence for the current handwritten rescue lane."
        ),
    ),
    LocGwSliceAsset(
        fixture_id="loc-gw-farm-780802",
        asset_id="780802",
        asset="mgw438393-1",
        item_id="mgw438393",
        project="Farm Reports, 1789-1798",
        rationale=(
            "Single-page farm/work record chosen as the strongest image-entry baseline in exploration; "
            "it is still wrong, but materially closer than the receipt page."
        ),
    ),
)


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _build_request(url: str) -> urllib.request.Request:
    return urllib.request.Request(url, headers={"User-Agent": USER_AGENT})


def _download_bytes(url: str) -> bytes:
    with urllib.request.urlopen(_build_request(url), timeout=60) as response:
        return response.read()


def _download_file(url: str, path: Path) -> Path:
    if path.exists():
        return path
    _ensure_dir(path.parent)
    data = _download_bytes(url)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_bytes(data)
    tmp_path.replace(path)
    return path


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _build_eval_env() -> dict[str, str]:
    env = dict(os.environ)
    if env.get("GEMINI_API_KEY") and env.get("GOOGLE_API_KEY"):
        env.pop("GOOGLE_API_KEY", None)
    env["PYTHONPATH"] = str(ROOT)
    return env


def _require_pillow():
    if Image is None:
        raise RuntimeError("Pillow is required to materialize optional PDF wrappers for Story 214") from PIL_IMPORT_ERROR
    return Image


def _require_pypdf():
    if PdfReader is None:
        raise RuntimeError("pypdf is required to inspect optional Story 214 PDF wrappers") from PYPDF_IMPORT_ERROR
    return PdfReader


def _save_pdf(image_path: Path, pdf_path: Path) -> None:
    image_lib = _require_pillow()
    with image_lib.open(image_path) as image:
        rgb = image.convert("RGB")
        try:
            rgb.save(pdf_path, "PDF")
        finally:
            rgb.close()


def should_retry_transient_eval_failure(stdout: str, stderr: str) -> bool:
    haystack = f"{stdout}\n{stderr}"
    return "503 UNAVAILABLE" in haystack and "currently experiencing high demand" in haystack


def normalize_transcript(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return ""
    return stripped + "\n"


def load_loc_dataset_bundle(zip_path: str | Path) -> dict[str, Any]:
    zip_path = Path(zip_path)
    with zipfile.ZipFile(zip_path) as archive:
        csv_name = next(name for name in archive.namelist() if name.endswith(".csv"))
        readme_name = next(name for name in archive.namelist() if "README" in name)
        rows = list(csv.DictReader(io.TextIOWrapper(archive.open(csv_name), encoding="utf-8-sig")))
        readme_text = archive.read(readme_name).decode("utf-8-sig")

    rows_with_transcription = sum(1 for row in rows if (row.get("Transcription") or "").strip())
    asset_status_counts: dict[str, int] = {}
    for row in rows:
        status = row.get("AssetStatus", "")
        asset_status_counts[status] = asset_status_counts.get(status, 0) + 1

    return {
        "zip_path": str(zip_path),
        "csv_name": csv_name,
        "readme_name": readme_name,
        "readme_text": readme_text,
        "rows": rows,
        "summary": {
            "rows_total": len(rows),
            "rows_with_transcription": rows_with_transcription,
            "rows_without_transcription": len(rows) - rows_with_transcription,
            "asset_status_counts": asset_status_counts,
        },
    }


def resolve_story214_slice_rows(rows: list[dict[str, str]]) -> list[tuple[LocGwSliceAsset, dict[str, str]]]:
    rows_by_asset_id = {row.get("AssetId"): row for row in rows}
    selected: list[tuple[LocGwSliceAsset, dict[str, str]]] = []
    for spec in STORY214_SLICE:
        row = rows_by_asset_id.get(spec.asset_id)
        if row is None:
            raise ValueError(f"Missing selected LOC row for AssetId {spec.asset_id}")
        if row.get("Asset") != spec.asset:
            raise ValueError(f"Asset mismatch for {spec.asset_id}: expected {spec.asset}, got {row.get('Asset')}")
        if row.get("ItemId") != spec.item_id:
            raise ValueError(f"ItemId mismatch for {spec.asset_id}: expected {spec.item_id}, got {row.get('ItemId')}")
        if row.get("Project") != spec.project:
            raise ValueError(f"Project mismatch for {spec.asset_id}: expected {spec.project}, got {row.get('Project')}")
        if not (row.get("Transcription") or "").strip():
            raise ValueError(f"Selected LOC row {spec.asset_id} has empty transcription")
        selected.append((spec, row))
    return selected


def _item_url(item_id: str) -> str:
    return f"https://www.loc.gov/item/{item_id}/"


def materialize_story214_slice(
    out_root: Path,
    *,
    include_pdf: bool,
    zip_path: str | Path | None = None,
) -> dict[str, Any]:
    dataset_root = _ensure_dir(out_root / "loc_dataset")
    local_zip_path = Path(zip_path) if zip_path else dataset_root / DEFAULT_ZIP_NAME
    if not local_zip_path.exists():
        _download_file(DATASET_ZIP_URL, local_zip_path)

    bundle = load_loc_dataset_bundle(local_zip_path)
    readme_path = dataset_root / bundle["readme_name"]
    if not readme_path.exists():
        readme_path.write_text(bundle["readme_text"], encoding="utf-8")

    slice_root = _ensure_dir(out_root / "loc_gw_slice")
    fixtures_root = _ensure_dir(slice_root / "fixtures")
    page_entries: list[dict[str, Any]] = []
    corpus_fixtures: list[dict[str, Any]] = []

    for spec, row in resolve_story214_slice_rows(bundle["rows"]):
        fixture_root = _ensure_dir(fixtures_root / spec.fixture_id)
        images_dir = _ensure_dir(fixture_root / "images")
        image_path = images_dir / "page-001.jpg"
        transcript_path = fixture_root / "transcript.txt"

        download_url = row.get("DownloadUrl") or row.get("DownloadURL")
        if not download_url:
            raise ValueError(f"Selected LOC row {spec.asset_id} is missing DownloadUrl")

        image_bytes = _download_bytes(download_url)
        image_path.write_bytes(image_bytes)
        transcript_text = normalize_transcript(row["Transcription"])
        transcript_path.write_text(transcript_text, encoding="utf-8")

        pdf_path: Path | None = None
        if include_pdf:
            pdf_path = fixture_root / f"{spec.fixture_id}.pdf"
            _save_pdf(image_path, pdf_path)

        preview = transcript_text.strip().splitlines()[:5]
        manifest_entry = {
            **asdict(spec),
            "item_title": row["Item"],
            "item_url": _item_url(spec.item_id),
            "download_url": download_url,
            "asset_status": row["AssetStatus"],
            "tags": [tag.strip() for tag in (row.get("Tags") or "").split(";") if tag.strip()],
            "fixture_root": str(fixture_root),
            "images_dir": str(images_dir),
            "image_path": str(image_path),
            "image_sha256": _sha256_bytes(image_bytes),
            "image_bytes": len(image_bytes),
            "transcript_path": str(transcript_path),
            "transcription_length": len(transcript_text.strip()),
            "transcription_preview": preview,
            "pdf_path": str(pdf_path) if pdf_path is not None else None,
        }
        page_entries.append(manifest_entry)

        fixture_record = {
            "id": spec.fixture_id,
            "label": f"LOC GW {spec.project} asset {spec.asset_id}",
            "difficulty": "historical-handwriting-external",
            "source_type": "external-loc-gw",
            "transcript": str(transcript_path),
            "images": str(images_dir),
        }
        if pdf_path is not None:
            fixture_record["pdf"] = str(pdf_path)
        corpus_fixtures.append(fixture_record)

    corpus_path = slice_root / "corpus.json"
    _write_json(corpus_path, {"fixtures": corpus_fixtures})

    manifest = {
        "story": "214",
        "kind": "comparison-only external benchmark slice",
        "dataset": {
            "item_url": DATASET_ITEM_URL,
            "item_json_url": DATASET_ITEM_JSON_URL,
            "dataset_zip_url": DATASET_ZIP_URL,
            "local_zip_path": str(local_zip_path),
            "readme_path": str(readme_path),
            "csv_name": bundle["csv_name"],
            "readme_name": bundle["readme_name"],
            "summary": bundle["summary"],
            "rights": {
                "text_rights_note": DATASET_RIGHTS_NOTE,
                "source_rights_note": DATASET_SOURCE_NOTE,
                "blank_transcription_note": (
                    "The README says blank Transcription cells mean volunteers marked the asset as "
                    "\"nothing to transcribe\"."
                ),
            },
        },
        "slice": {
            "selection_basis": (
                "One bounded asset from each of the campaign's three projects: interrogations, receipts, "
                "and farm reports. Image-entry remains canonical because DownloadUrl is the source-native "
                "surface, while PDF wrappers are optional stress only."
            ),
            "image_entry_canonical": True,
            "include_pdf": include_pdf,
            "corpus_path": str(corpus_path),
            "pages": page_entries,
        },
    }
    _write_json(slice_root / "slice_manifest.json", manifest)
    return manifest


def run_story214_eval(
    *,
    out_root: Path,
    slice_manifest: dict[str, Any],
    image_recipe: str,
    pdf_recipe: str,
    image_case_id: str,
    pdf_case_id: str,
    include_pdf: bool,
    max_attempts: int,
    instrument: bool,
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
            ]
            if instrument:
                cmd.append("--instrument")
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
                raise RuntimeError(
                    f"Case {fixture_id}/{case_id} failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
                )
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
            pdf_path = page["pdf_path"]
            if not pdf_path:
                raise RuntimeError(f"PDF benchmark requested but no pdf_path was materialized for {page['fixture_id']}")
            pdf_case = run_driver_case_with_retries(
                fixture_id=page["fixture_id"],
                transcript_path=page["transcript_path"],
                case_id=pdf_case_id,
                recipe=pdf_recipe,
                input_flag="--input-pdf",
                input_path=pdf_path,
            )
            fixture_cases.append(pdf_case)
            scored_cases.append(pdf_case)
            all_attempts.append({"fixture_id": page["fixture_id"], "case_id": pdf_case_id, "attempts": pdf_case["attempts"]})

            pdf_reader_cls = _require_pypdf()
            pdf_reader = pdf_reader_cls(pdf_path)
            pdf_extract_lengths = [len((pdf_page.extract_text() or "").strip()) for pdf_page in pdf_reader.pages]

        fixture_results.append(
            {
                "fixture_id": page["fixture_id"],
                "label": page["item_title"],
                "difficulty": "historical-handwriting-external",
                "source_type": "external-loc-gw",
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
        "include_pdf": include_pdf,
        "instrument": instrument,
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
    parser.add_argument("--zip-path", default=None, help="Optional local path to a previously downloaded LOC dataset ZIP")
    parser.add_argument("--image-recipe", default=DEFAULT_IMAGE_RECIPE)
    parser.add_argument("--pdf-recipe", default=DEFAULT_PDF_RECIPE)
    parser.add_argument("--image-case-id", default=DEFAULT_IMAGE_CASE_ID)
    parser.add_argument("--pdf-case-id", default=DEFAULT_PDF_CASE_ID)
    parser.add_argument("--include-pdf", action="store_true")
    parser.add_argument("--instrument", action="store_true")
    parser.add_argument("--max-attempts", type=int, default=2)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    out_root = Path(args.out_root)
    if not out_root.is_absolute():
        out_root = ROOT / out_root
    _ensure_dir(out_root)

    slice_manifest = materialize_story214_slice(
        out_root,
        include_pdf=args.include_pdf,
        zip_path=args.zip_path,
    )
    eval_payload = run_story214_eval(
        out_root=out_root,
        slice_manifest=slice_manifest,
        image_recipe=args.image_recipe,
        pdf_recipe=args.pdf_recipe,
        image_case_id=args.image_case_id,
        pdf_case_id=args.pdf_case_id,
        include_pdf=args.include_pdf,
        max_attempts=args.max_attempts,
        instrument=args.instrument,
    )

    summary = {
        "story": "214",
        "out_root": str(out_root),
        "slice_manifest_path": str(out_root / "loc_gw_slice" / "slice_manifest.json"),
        "benchmark_output_path": str(out_root / "handwritten_eval.json"),
        "recipes": {
            "image": args.image_recipe,
            "pdf": args.pdf_recipe,
            "image_case_id": args.image_case_id,
            "pdf_case_id": args.pdf_case_id,
            "include_pdf": args.include_pdf,
            "instrument": args.instrument,
            "max_attempts": args.max_attempts,
            "env_policy": "prefer GEMINI_API_KEY when both Gemini env vars are present",
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
