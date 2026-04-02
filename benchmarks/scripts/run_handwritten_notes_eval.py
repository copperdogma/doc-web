import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.scorers.handwritten_notes_transcription import score_page_html_artifact


DEFAULT_TRANSCRIPT = ROOT / "testdata/handwritten-notes-mini.txt"
DEFAULT_IMAGES = ROOT / "testdata/handwritten-notes-mini-images"
DEFAULT_PDF = ROOT / "testdata/handwritten-notes-mini.pdf"
DEFAULT_IMAGE_RECIPE = "configs/recipes/recipe-images-ocr-html-mvp.yaml"
DEFAULT_PDF_RECIPE = "configs/recipes/recipe-pdf-ocr-html-mvp.yaml"


def run_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    return subprocess.run(
        cmd,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )


def run_driver_case(case_id: str, recipe: str, input_flag: str, input_path: Path) -> dict:
    run_id = f"handwritten-notes-{case_id}"
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
    result = run_command(cmd)
    if result.returncode != 0:
        raise RuntimeError(result.stdout + "\n" + result.stderr)
    artifact_path = ROOT / "output" / "runs" / run_id / "02_ocr_ai_gpt51_v1" / "pages_html.jsonl"
    if not artifact_path.exists():
        raise RuntimeError(f"Expected artifact missing: {artifact_path}")
    return {
        "case_id": case_id,
        "recipe": recipe,
        "input_flag": input_flag,
        "input_path": str(input_path),
        "run_id": run_id,
        "artifact_path": str(artifact_path),
        "stdout_tail": "\n".join((result.stdout or "").splitlines()[-20:]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the handwritten-notes baseline eval on the repo-owned fixture")
    parser.add_argument("--transcript", default=str(DEFAULT_TRANSCRIPT))
    parser.add_argument("--images", default=str(DEFAULT_IMAGES))
    parser.add_argument("--pdf", default=str(DEFAULT_PDF))
    parser.add_argument("--image-recipe", default=DEFAULT_IMAGE_RECIPE)
    parser.add_argument("--pdf-recipe", default=DEFAULT_PDF_RECIPE)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    transcript_path = Path(args.transcript)
    if not transcript_path.is_absolute():
        transcript_path = ROOT / transcript_path
    images_path = Path(args.images)
    if not images_path.is_absolute():
        images_path = ROOT / images_path
    pdf_path = Path(args.pdf)
    if not pdf_path.is_absolute():
        pdf_path = ROOT / pdf_path

    cases = [
        run_driver_case("image-generic", args.image_recipe, "--input-images", images_path),
        run_driver_case("pdf-generic", args.pdf_recipe, "--input-pdf", pdf_path),
    ]

    scored_cases = []
    for case in cases:
        metrics = score_page_html_artifact(transcript_path, case["artifact_path"])
        case["metrics"] = metrics
        case["pass"] = metrics["overall_ratio"] >= 0.99 and metrics["page_min_ratio"] >= 0.99
        scored_cases.append(case)

    pdf_reader = PdfReader(str(pdf_path))
    pdf_extract_lengths = [len((page.extract_text() or "").strip()) for page in pdf_reader.pages]

    summary = {
        "pass_rate": round(sum(1 for case in scored_cases if case["pass"]) / len(scored_cases), 6),
        "overall_min_ratio": min(case["metrics"]["overall_ratio"] for case in scored_cases),
        "page_min_ratio": min(case["metrics"]["page_min_ratio"] for case in scored_cases),
        "cases_passing": sum(1 for case in scored_cases if case["pass"]),
        "cases_total": len(scored_cases),
        "pdf_extractable_text_lengths": pdf_extract_lengths,
    }

    local_now = datetime.now().astimezone()

    payload = {
        "measured_at": local_now.date().isoformat(),
        "transcript_path": str(transcript_path),
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
