#!/usr/bin/env python3
"""Build and run a bounded LOC George Washington Papers benchmark for Story 214.

This is a story-local, comparison-only harness. The canonical decision surface
is the source-native image-entry OCR path; `--include-pdf` adds PDF-entry
stress only. The helper uses simple local file/HTTP handling plus the existing
handwritten eval/scoring path for OCR comparison.
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
import time
import urllib.request
import zipfile
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

import yaml  # noqa: E402

from benchmarks.scorers.handwritten_notes_transcription import score_page_html_artifact  # noqa: E402
from benchmarks.scripts.run_handwritten_notes_eval import build_run_id  # noqa: E402
from modules.common.run_registry import resolve_output_root  # noqa: E402


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
DEFAULT_STORY_ID = "214"
DEFAULT_RETRY_SLEEP_SECONDS = 20
DEFAULT_CANDIDATE_MAX_OUTPUT_TOKENS = 16384
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
    env = build_child_env()
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
    haystack = f"{stdout}\n{stderr}".lower()
    if "insufficient_quota" in haystack:
        return False
    return (
        ("503 unavailable" in haystack and "currently experiencing high demand" in haystack)
        or ("rate limit" in haystack)
        or ("too many requests" in haystack)
    )


def _slugify(value: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "candidate"


def _shared_output_root() -> Path:
    return Path(resolve_output_root(cwd=str(ROOT))).resolve(strict=False)


def _load_case_instrumentation(run_dir: Path) -> dict[str, Any] | None:
    path = run_dir / "instrumentation.json"
    if not path.exists():
        return None

    payload = json.loads(path.read_text(encoding="utf-8"))
    ocr_stage = next((stage for stage in payload.get("stages", []) if stage.get("id") == "ocr_ai"), None)
    return {
        "path": str(path),
        "run_totals": payload.get("totals", {}),
        "ocr_stage": {
            "wall_seconds": (ocr_stage or {}).get("wall_seconds"),
            "llm_totals": (ocr_stage or {}).get("llm_totals", {}),
            "per_model": ((ocr_stage or {}).get("extra") or {}).get("per_model", {}),
        },
    }


def _load_jsonl_rows(path: str | Path) -> list[dict[str, Any]]:
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _load_pipeline_stage_status(run_dir: str | Path, stage_id: str) -> str | None:
    state_path = Path(run_dir) / "pipeline_state.json"
    if not state_path.exists():
        return None
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    return ((payload.get("stages") or {}).get(stage_id) or {}).get("status")


def summarize_case_failure(artifact_path: str | Path, metrics: dict[str, Any]) -> dict[str, Any]:
    if metrics["overall_ratio"] >= 0.99 and metrics["page_min_ratio"] >= 0.99:
        return {"dominant_failure_mode": "passing", "empty_reasons": [], "actual_preview": ""}

    rows = _load_jsonl_rows(artifact_path)
    empty_reasons = [row.get("ocr_empty_reason") for row in rows if row.get("ocr_empty_reason")]
    if empty_reasons:
        return {
            "dominant_failure_mode": "empty_html",
            "empty_reasons": empty_reasons,
            "actual_preview": metrics["pages"][0]["actual_preview"] if metrics.get("pages") else "",
        }

    page_scores = metrics.get("pages") or []
    if any(
        page.get("expected_length", 0) > 0
        and page.get("actual_length", 0) < max(1, int(page["expected_length"] * 0.6))
        for page in page_scores
    ):
        failure_mode = "partial_omission"
    else:
        failure_mode = "non_empty_wrong_text"
    return {
        "dominant_failure_mode": failure_mode,
        "empty_reasons": [],
        "actual_preview": page_scores[0]["actual_preview"] if page_scores else "",
    }


def _sleep_before_retry(attempt: int, retry_sleep_seconds: int) -> int:
    return retry_sleep_seconds * attempt


def _load_ocr_stage_params(recipe_path: str | Path) -> dict[str, Any]:
    recipe = yaml.safe_load(Path(recipe_path).read_text(encoding="utf-8")) or {}
    for stage in recipe.get("stages", []):
        if stage.get("id") == "ocr_ai" and stage.get("module") == "ocr_ai_gpt51_v1":
            return dict(stage.get("params") or {})
    raise ValueError(f"Recipe {recipe_path} does not define ocr_ai_gpt51_v1 stage params")


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
    story_id: str,
    image_recipe: str,
    pdf_recipe: str,
    image_case_id: str,
    pdf_case_id: str,
    include_pdf: bool,
    max_attempts: int,
    instrument: bool,
    retry_sleep_seconds: int,
) -> dict[str, Any]:
    shared_output_root = _shared_output_root()

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
        run_dir = shared_output_root / "runs" / run_id
        artifact_path = run_dir / "02_ocr_ai_gpt51_v1" / "pages_html.jsonl"
        if artifact_path.exists() and _load_pipeline_stage_status(run_dir, "ocr_ai") == "done":
            metrics = score_page_html_artifact(transcript_path, artifact_path)
            failure_summary = summarize_case_failure(artifact_path, metrics)
            payload = {
                "fixture_id": fixture_id,
                "case_id": case_id,
                "run_id": run_id,
                "run_dir": str(run_dir),
                "recipe": recipe,
                "input_flag": input_flag,
                "input_path": input_path,
                "artifact_path": str(artifact_path),
                "metrics": metrics,
                "pass": metrics["overall_ratio"] >= 0.99 and metrics["page_min_ratio"] >= 0.99,
                "failure_summary": failure_summary,
                "attempts": [],
                "reused_existing": True,
            }
            instrumentation = _load_case_instrumentation(run_dir)
            if instrumentation:
                payload["instrumentation"] = instrumentation
            return payload
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
                "--output-dir",
                str(run_dir),
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
                if not artifact_path.exists():
                    raise RuntimeError(f"Expected artifact missing after successful run: {artifact_path}")
                metrics = score_page_html_artifact(transcript_path, artifact_path)
                failure_summary = summarize_case_failure(artifact_path, metrics)
                payload = {
                    "fixture_id": fixture_id,
                    "case_id": case_id,
                    "run_id": run_id,
                    "run_dir": str(run_dir),
                    "recipe": recipe,
                    "input_flag": input_flag,
                    "input_path": input_path,
                    "artifact_path": str(artifact_path),
                    "metrics": metrics,
                    "pass": metrics["overall_ratio"] >= 0.99 and metrics["page_min_ratio"] >= 0.99,
                    "failure_summary": failure_summary,
                    "attempts": case_attempts,
                }
                instrumentation = _load_case_instrumentation(run_dir)
                if instrumentation:
                    payload["instrumentation"] = instrumentation
                return payload
            if attempt >= max_attempts or not retryable:
                raise RuntimeError(
                    f"Case {fixture_id}/{case_id} failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
                )
            sleep_seconds = _sleep_before_retry(attempt, retry_sleep_seconds)
            case_attempts[-1]["retry_sleep_seconds_before_next_attempt"] = sleep_seconds
            time.sleep(sleep_seconds)
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
                    "dominant_failure_modes": [case["failure_summary"]["dominant_failure_mode"] for case in fixture_cases],
                },
            }
        )

    payload = {
        "story": story_id,
        "measured_at": datetime.now().astimezone().date().isoformat(),
        "shared_output_root": str(shared_output_root),
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


def run_image_candidate_screen(
    *,
    out_root: Path,
    slice_manifest: dict[str, Any],
    story_id: str,
    baseline_eval: dict[str, Any],
    image_recipe: str,
    image_case_id: str,
    candidate_model: str,
    candidate_retry_model: str | None,
    candidate_max_output_tokens: int,
    max_attempts: int,
    retry_sleep_seconds: int,
) -> dict[str, Any]:
    shared_output_root = _shared_output_root()
    ocr_params = _load_ocr_stage_params(image_recipe)
    candidate_slug = _slugify(candidate_model)
    baseline_cases = {
        (case["fixture_id"], case["case_id"]): case
        for case in baseline_eval["cases"]
        if case["case_id"] == image_case_id
    }
    cases: list[dict[str, Any]] = []

    for page in slice_manifest["slice"]["pages"]:
        fixture_id = page["fixture_id"]
        baseline_run_id = build_run_id(fixture_id, image_case_id)
        manifest_path = (
            shared_output_root
            / "runs"
            / baseline_run_id
            / "01_images_dir_to_manifest_v1"
            / "pages_images_manifest.jsonl"
        )
        if not manifest_path.exists():
            raise RuntimeError(f"Baseline image manifest missing for candidate screen: {manifest_path}")

        run_id = f"story{story_id}-{fixture_id}-image-{candidate_slug}"
        run_dir = shared_output_root / "runs" / run_id
        outdir = run_dir / "01_ocr_ai_gpt51_v1"
        artifact_path = outdir / "pages_html.jsonl"
        case_attempts: list[dict[str, Any]] = []

        for attempt in range(1, max_attempts + 1):
            cmd = [
                sys.executable,
                "modules/extract/ocr_ai_gpt51_v1/main.py",
                "--pages",
                str(manifest_path),
                "--outdir",
                str(outdir),
                "--out",
                "pages_html.jsonl",
                "--run-id",
                run_id,
                "--force",
                "--model",
                candidate_model,
                "--max-output-tokens",
                str(candidate_max_output_tokens),
            ]
            if candidate_retry_model:
                cmd.extend(["--retry-model", candidate_retry_model])
            if ocr_params.get("ocr_hints"):
                cmd.extend(["--ocr-hints", str(ocr_params["ocr_hints"])])
            if ocr_params.get("max_long_side"):
                cmd.extend(["--max-long-side", str(ocr_params["max_long_side"])])
            if ocr_params.get("skip_blank_pages"):
                cmd.append("--skip-blank-pages")
            if "blank_threshold" in ocr_params:
                cmd.extend(["--blank-threshold", str(ocr_params["blank_threshold"])])

            result = subprocess.run(
                cmd,
                cwd=ROOT,
                env=_build_eval_env(),
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
                if not artifact_path.exists():
                    raise RuntimeError(f"Expected candidate artifact missing: {artifact_path}")
                metrics = score_page_html_artifact(page["transcript_path"], artifact_path)
                failure_summary = summarize_case_failure(artifact_path, metrics)
                baseline_case = baseline_cases[(fixture_id, image_case_id)]
                cases.append(
                    {
                        "fixture_id": fixture_id,
                        "asset_id": page["asset_id"],
                        "item_title": page["item_title"],
                        "case_id": candidate_slug,
                        "run_id": run_id,
                        "run_dir": str(run_dir),
                        "artifact_path": str(artifact_path),
                        "manifest_path": str(manifest_path),
                        "transcript_path": page["transcript_path"],
                        "model": candidate_model,
                        "retry_model": candidate_retry_model,
                        "max_output_tokens": candidate_max_output_tokens,
                        "metrics": metrics,
                        "pass": metrics["overall_ratio"] >= 0.99 and metrics["page_min_ratio"] >= 0.99,
                        "failure_summary": failure_summary,
                        "baseline_case": {
                            "run_id": baseline_case["run_id"],
                            "artifact_path": baseline_case["artifact_path"],
                            "overall_ratio": baseline_case["metrics"]["overall_ratio"],
                            "page_min_ratio": baseline_case["metrics"]["page_min_ratio"],
                            "failure_mode": baseline_case["failure_summary"]["dominant_failure_mode"],
                        },
                        "delta_overall_ratio": round(
                            metrics["overall_ratio"] - baseline_case["metrics"]["overall_ratio"], 6
                        ),
                        "delta_page_min_ratio": round(
                            metrics["page_min_ratio"] - baseline_case["metrics"]["page_min_ratio"], 6
                        ),
                        "attempts": case_attempts,
                    }
                )
                break
            if attempt >= max_attempts or not retryable:
                raise RuntimeError(
                    f"Candidate {candidate_model} failed for {fixture_id}:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
                )
            sleep_seconds = _sleep_before_retry(attempt, retry_sleep_seconds)
            case_attempts[-1]["retry_sleep_seconds_before_next_attempt"] = sleep_seconds
            time.sleep(sleep_seconds)

    summary = {
        "story": story_id,
        "measured_at": datetime.now().astimezone().date().isoformat(),
        "shared_output_root": str(shared_output_root),
        "candidate_model": candidate_model,
        "candidate_retry_model": candidate_retry_model,
        "candidate_slug": candidate_slug,
        "candidate_max_output_tokens": candidate_max_output_tokens,
        "image_recipe": image_recipe,
        "baseline_image_case_id": image_case_id,
        "cases": cases,
        "summary": {
            "fixture_count": len(cases),
            "pass_rate": round(sum(1 for case in cases if case["pass"]) / len(cases), 6),
            "overall_min_ratio": min(case["metrics"]["overall_ratio"] for case in cases),
            "page_min_ratio": min(case["metrics"]["page_min_ratio"] for case in cases),
            "cases_passing": sum(1 for case in cases if case["pass"]),
            "cases_total": len(cases),
            "receipt_sentinel_asset_id": "367466",
            "receipt_sentinel_cleared": any(
                case["asset_id"] == "367466" and case["metrics"]["overall_ratio"] > 0.0 for case in cases
            ),
            "material_improvements": [
                {
                    "fixture_id": case["fixture_id"],
                    "asset_id": case["asset_id"],
                    "delta_overall_ratio": case["delta_overall_ratio"],
                    "delta_page_min_ratio": case["delta_page_min_ratio"],
                }
                for case in cases
                if case["delta_overall_ratio"] > 0.05 or case["delta_page_min_ratio"] > 0.05
            ],
        },
    }
    output_path = out_root / f"candidate-screen-{candidate_slug}.json"
    _write_json(output_path, summary)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=CLI_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--story-id", default=DEFAULT_STORY_ID)
    parser.add_argument("--out-root", default=str(DEFAULT_OUT_ROOT))
    parser.add_argument("--zip-path", default=None, help="Optional local path to a previously downloaded LOC dataset ZIP")
    parser.add_argument("--image-recipe", default=DEFAULT_IMAGE_RECIPE)
    parser.add_argument("--pdf-recipe", default=DEFAULT_PDF_RECIPE)
    parser.add_argument("--image-case-id", default=DEFAULT_IMAGE_CASE_ID)
    parser.add_argument("--pdf-case-id", default=DEFAULT_PDF_CASE_ID)
    parser.add_argument("--include-pdf", action="store_true")
    parser.add_argument("--instrument", action="store_true")
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--retry-sleep-seconds", type=int, default=DEFAULT_RETRY_SLEEP_SECONDS)
    parser.add_argument("--candidate-model", default=None)
    parser.add_argument("--candidate-retry-model", default=None)
    parser.add_argument("--candidate-max-output-tokens", type=int, default=DEFAULT_CANDIDATE_MAX_OUTPUT_TOKENS)
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
        story_id=args.story_id,
        image_recipe=args.image_recipe,
        pdf_recipe=args.pdf_recipe,
        image_case_id=args.image_case_id,
        pdf_case_id=args.pdf_case_id,
        include_pdf=args.include_pdf,
        max_attempts=args.max_attempts,
        instrument=args.instrument,
        retry_sleep_seconds=args.retry_sleep_seconds,
    )

    candidate_summary = None
    if args.candidate_model:
        candidate_summary = run_image_candidate_screen(
            out_root=out_root,
            slice_manifest=slice_manifest,
            story_id=args.story_id,
            baseline_eval=eval_payload,
            image_recipe=args.image_recipe,
            image_case_id=args.image_case_id,
            candidate_model=args.candidate_model,
            candidate_retry_model=args.candidate_retry_model,
            candidate_max_output_tokens=args.candidate_max_output_tokens,
            max_attempts=args.max_attempts,
            retry_sleep_seconds=args.retry_sleep_seconds,
        )

    summary = {
        "story": args.story_id,
        "out_root": str(out_root),
        "shared_output_root": str(_shared_output_root()),
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
            "retry_sleep_seconds": args.retry_sleep_seconds,
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
    if candidate_summary:
        summary["candidate_screen_path"] = str(
            out_root / f"candidate-screen-{_slugify(args.candidate_model)}.json"
        )
        summary["candidate_screen_summary"] = candidate_summary["summary"]
    _write_json(out_root / "benchmark_summary.json", summary)
    print(json.dumps(summary["benchmark_summary"], indent=2))
    print(f"RESULT_PATH {out_root / 'benchmark_summary.json'}")


if __name__ == "__main__":
    main()
