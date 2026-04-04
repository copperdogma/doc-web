import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.scorers.handwritten_notes_transcription import score_page_html_artifact  # noqa: E402


DEFAULT_TRANSCRIPT = ROOT / "testdata/handwritten-notes-mini.txt"
DEFAULT_IMAGES = ROOT / "testdata/handwritten-notes-mini-images"
DEFAULT_PDF = ROOT / "testdata/handwritten-notes-mini.pdf"
DEFAULT_CORPUS = ROOT / "benchmarks" / "golden" / "handwritten-notes" / "corpus.json"
DEFAULT_IMAGE_RECIPE = "configs/recipes/recipe-images-ocr-html-mvp.yaml"
DEFAULT_PDF_RECIPE = "configs/recipes/recipe-pdf-ocr-html-mvp.yaml"
DEFAULT_IMAGE_CASE_ID = "image-generic"
DEFAULT_PDF_CASE_ID = "pdf-generic"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "fixture"


def run_command(cmd: list[str]) -> tuple[subprocess.CompletedProcess[str], float]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    started = time.perf_counter()
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )
    return result, round(time.perf_counter() - started, 6)


def _resolve_path(path_str: str | Path) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        path = ROOT / path
    return path


def derive_single_fixture_id(
    transcript_path: str | Path,
    images_path: str | Path,
    pdf_path: str | Path,
    *,
    fixture_id: str | None = None,
) -> str:
    if fixture_id:
        return _slugify(fixture_id)

    transcript_resolved = _resolve_path(transcript_path)
    images_resolved = _resolve_path(images_path)
    pdf_resolved = _resolve_path(pdf_path)
    seed = f"{transcript_resolved}|{images_resolved}|{pdf_resolved}"
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:8]
    label = _slugify(images_resolved.name or pdf_resolved.stem or transcript_resolved.stem)
    return f"single-fixture-{label[:40]}-{digest}"


def build_run_id(fixture_id: str, case_id: str) -> str:
    return f"handwritten-{fixture_id}-{case_id}"


def load_case_instrumentation(run_id: str) -> dict[str, Any] | None:
    path = ROOT / "output" / "runs" / run_id / "instrumentation.json"
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


def load_fixture_specs(
    *,
    corpus_path: str | Path | None = None,
    transcript: str | None = None,
    images: str | None = None,
    pdf: str | None = None,
    fixture_id: str | None = None,
) -> list[dict[str, Any]]:
    if any(value is not None for value in (transcript, images, pdf)):
        if not all(value is not None for value in (transcript, images, pdf)):
            raise ValueError("Single-fixture mode requires --transcript, --images, and --pdf together")
        return [
            {
                "id": derive_single_fixture_id(
                    transcript,
                    images,
                    pdf,
                    fixture_id=fixture_id,
                ),
                "label": "Ad hoc handwritten fixture",
                "difficulty": "custom",
                "source_type": "custom",
                "transcript_path": _resolve_path(transcript),
                "images_path": _resolve_path(images),
                "pdf_path": _resolve_path(pdf),
            }
        ]

    resolved_corpus = _resolve_path(corpus_path or DEFAULT_CORPUS)
    payload = json.loads(resolved_corpus.read_text(encoding="utf-8"))
    fixtures = []
    seen_ids: set[str] = set()
    for fixture in payload.get("fixtures", []):
        fixture_id = fixture["id"]
        if fixture_id in seen_ids:
            raise ValueError(f"Duplicate handwritten fixture id: {fixture_id}")
        seen_ids.add(fixture_id)
        fixtures.append(
            {
                "id": fixture_id,
                "label": fixture.get("label", fixture_id),
                "difficulty": fixture.get("difficulty", "unknown"),
                "source_type": fixture.get("source_type", "unknown"),
                "transcript_path": _resolve_path(fixture["transcript"]),
                "images_path": _resolve_path(fixture["images"]),
                "pdf_path": _resolve_path(fixture["pdf"]),
            }
        )
    if not fixtures:
        raise ValueError(f"No fixtures defined in corpus: {resolved_corpus}")
    return fixtures


def run_driver_case(
    fixture_id: str,
    case_id: str,
    recipe: str,
    input_flag: str,
    input_path: Path,
    *,
    instrument: bool = False,
    price_table: str | None = None,
) -> dict[str, Any]:
    run_id = build_run_id(fixture_id, case_id)
    cmd = [
        sys.executable,
        "driver.py",
        "--recipe",
        recipe,
        input_flag,
        str(input_path),
        "--run-id",
        run_id,
        "--allow-run-id-reuse",
        "--force",
        "--end-at",
        "ocr_ai",
    ]
    if instrument:
        cmd.append("--instrument")
    if price_table:
        cmd.extend(["--price-table", price_table])

    result, wall_seconds = run_command(cmd)
    if result.returncode != 0:
        raise RuntimeError(result.stdout + "\n" + result.stderr)
    artifact_path = ROOT / "output" / "runs" / run_id / "02_ocr_ai_gpt51_v1" / "pages_html.jsonl"
    if not artifact_path.exists():
        raise RuntimeError(f"Expected artifact missing: {artifact_path}")
    payload = {
        "fixture_id": fixture_id,
        "case_id": case_id,
        "recipe": recipe,
        "recipe_name": Path(recipe).name,
        "input_flag": input_flag,
        "input_path": str(input_path),
        "run_id": run_id,
        "artifact_path": str(artifact_path),
        "wall_seconds": wall_seconds,
        "stdout_tail": "\n".join((result.stdout or "").splitlines()[-20:]),
    }
    instrumentation = load_case_instrumentation(run_id)
    if instrumentation:
        payload["instrumentation"] = instrumentation
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the handwritten-notes baseline eval on the repo-owned fixture")
    parser.add_argument("--corpus", default=str(DEFAULT_CORPUS))
    parser.add_argument("--transcript", default=None)
    parser.add_argument("--images", default=None)
    parser.add_argument("--pdf", default=None)
    parser.add_argument("--fixture-id", default=None)
    parser.add_argument("--image-recipe", default=DEFAULT_IMAGE_RECIPE)
    parser.add_argument("--pdf-recipe", default=DEFAULT_PDF_RECIPE)
    parser.add_argument("--image-case-id", default=DEFAULT_IMAGE_CASE_ID)
    parser.add_argument("--pdf-case-id", default=DEFAULT_PDF_CASE_ID)
    parser.add_argument("--instrument", action="store_true")
    parser.add_argument("--price-table", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    fixtures = load_fixture_specs(
        corpus_path=args.corpus,
        transcript=args.transcript,
        images=args.images,
        pdf=args.pdf,
        fixture_id=args.fixture_id,
    )

    scored_cases = []
    fixture_results = []
    pdf_extract_lengths_by_fixture = {}

    for fixture in fixtures:
        cases = [
            run_driver_case(
                fixture["id"],
                args.image_case_id,
                args.image_recipe,
                "--input-images",
                fixture["images_path"],
                instrument=args.instrument,
                price_table=args.price_table,
            ),
            run_driver_case(
                fixture["id"],
                args.pdf_case_id,
                args.pdf_recipe,
                "--input-pdf",
                fixture["pdf_path"],
                instrument=args.instrument,
                price_table=args.price_table,
            ),
        ]
        for case in cases:
            metrics = score_page_html_artifact(fixture["transcript_path"], case["artifact_path"])
            case["metrics"] = metrics
            case["pass"] = metrics["overall_ratio"] >= 0.99 and metrics["page_min_ratio"] >= 0.99
            scored_cases.append(case)

        pdf_reader = PdfReader(str(fixture["pdf_path"]))
        pdf_extract_lengths = [len((page.extract_text() or "").strip()) for page in pdf_reader.pages]
        pdf_extract_lengths_by_fixture[fixture["id"]] = pdf_extract_lengths

        fixture_results.append(
            {
                "fixture_id": fixture["id"],
                "label": fixture["label"],
                "difficulty": fixture["difficulty"],
                "source_type": fixture["source_type"],
                "transcript_path": str(fixture["transcript_path"]),
                "images_path": str(fixture["images_path"]),
                "pdf_path": str(fixture["pdf_path"]),
                "pdf_extractable_text_lengths": pdf_extract_lengths,
                "cases": cases,
                "summary": {
                    "pass_rate": round(sum(1 for case in cases if case["pass"]) / len(cases), 6),
                    "overall_min_ratio": min(case["metrics"]["overall_ratio"] for case in cases),
                    "page_min_ratio": min(case["metrics"]["page_min_ratio"] for case in cases),
                    "cases_passing": sum(1 for case in cases if case["pass"]),
                    "cases_total": len(cases),
                },
            }
        )

    summary = {
        "pass_rate": round(sum(1 for case in scored_cases if case["pass"]) / len(scored_cases), 6),
        "overall_min_ratio": min(case["metrics"]["overall_ratio"] for case in scored_cases),
        "page_min_ratio": min(case["metrics"]["page_min_ratio"] for case in scored_cases),
        "cases_passing": sum(1 for case in scored_cases if case["pass"]),
        "cases_total": len(scored_cases),
        "fixture_count": len(fixture_results),
        "fixtures_passing": sum(1 for fixture in fixture_results if fixture["summary"]["pass_rate"] == 1.0),
        "pdf_extractable_text_lengths": pdf_extract_lengths_by_fixture,
    }

    local_now = datetime.now().astimezone()

    payload = {
        "measured_at": local_now.date().isoformat(),
        "corpus_path": str(_resolve_path(args.corpus)) if args.transcript is None else None,
        "image_recipe": args.image_recipe,
        "pdf_recipe": args.pdf_recipe,
        "image_case_id": args.image_case_id,
        "pdf_case_id": args.pdf_case_id,
        "instrument": args.instrument,
        "price_table": args.price_table,
        "fixtures": fixture_results,
        "cases": scored_cases,
        "summary": summary,
    }

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = ROOT / output_path
    else:
        output_path = ROOT / "benchmarks" / "results" / f"handwritten-notes-{local_now.strftime('%Y%m%d-%H%M%S')}.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("SUMMARY " + json.dumps(summary))
    print("RESULT_PATH " + str(output_path))


if __name__ == "__main__":
    main()
