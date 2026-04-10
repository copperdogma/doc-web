#!/usr/bin/env python3
"""Run a bounded GLM-OCR benchmark via local Ollama."""

from __future__ import annotations

import argparse
import base64
import io
import json
import platform
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_ROOT = ROOT / "output" / "runs" / "story208-glm-ocr-benchmark-r1"
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "glm-ocr"
ONWARD_INCUMBENT_ARTIFACT = (
    Path("/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1")
    / "02_ocr_ai_gpt51_v1"
    / "pages_html.jsonl"
)

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.scorers.handwritten_notes_transcription import score_page_html_artifact  # noqa: E402
from benchmarks.scorers.html_table_diff import get_assert as score_html_table_diff  # noqa: E402


@dataclass(frozen=True)
class HandwrittenCase:
    case_id: str
    transcript_path: Path
    image_path: Path
    pdf_path: Path


@dataclass(frozen=True)
class OnwardPage:
    page_number: int
    image_path: Path
    golden_path: Path


HANDWRITTEN_CASES = (
    HandwrittenCase(
        case_id="barney",
        transcript_path=ROOT / "testdata/handwritten-notes-barney-real.txt",
        image_path=ROOT / "testdata/handwritten-notes-barney-real-images/page-001.jpg",
        pdf_path=ROOT / "testdata/handwritten-notes-barney-real.pdf",
    ),
    HandwrittenCase(
        case_id="alverson",
        transcript_path=ROOT / "testdata/handwritten-notes-alverson-real.txt",
        image_path=ROOT / "testdata/handwritten-notes-alverson-real-images/page-001.jpg",
        pdf_path=ROOT / "testdata/handwritten-notes-alverson-real.pdf",
    ),
)

ONWARD_PAGES = tuple(
    OnwardPage(
        page_number=page_number,
        image_path=Path("/Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images-2048")
        / f"Image{page_number:03d}.jpg",
        golden_path=ROOT / "benchmarks" / "golden" / "onward" / "per_page" / f"page_{page_number:03d}.html",
    )
    for page_number in (80, 81, 82, 83)
)


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _embedded_pdf_image_bytes(pdf_path: Path) -> tuple[bytes, str]:
    reader = PdfReader(str(pdf_path))
    if len(reader.pages) != 1:
        raise ValueError(f"Expected one-page PDF fixture: {pdf_path}")
    images = list(reader.pages[0].images)
    if len(images) != 1:
        raise ValueError(f"Expected one embedded image in PDF fixture: {pdf_path}")
    image = images[0]
    name = image.name or "embedded-image"
    if hasattr(image, "data") and image.data:
        return image.data, name
    if not hasattr(image, "image"):
        raise ValueError(f"Could not extract embedded image bytes from: {pdf_path}")
    buffer = io.BytesIO()
    image.image.save(buffer, format="PNG")
    return buffer.getvalue(), f"{name}.png"


def _call_ollama(
    *,
    model: str,
    prompt: str,
    image_bytes: bytes,
    ollama_url: str,
) -> dict[str, Any]:
    payload = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "images": [base64.b64encode(image_bytes).decode("ascii")],
            "stream": False,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        ollama_url,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=900) as response:
        return json.loads(response.read())


def _ollama_model_details(model: str) -> dict[str, Any]:
    proc = subprocess.run(
        ["ollama", "show", model],
        cwd=ROOT,
        capture_output=True,
        check=True,
        text=True,
    )
    return {"show_output": proc.stdout}


def _write_page_artifact(path: Path, *, run_id: str, html: str, source: str) -> None:
    row = {
        "schema_version": "page_html_v1",
        "run_id": run_id,
        "page_number": 1,
        "html": html,
        "source": [source],
    }
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")


def run_handwritten_case(
    *,
    case: HandwrittenCase,
    source_kind: str,
    model: str,
    ollama_url: str,
    out_dir: Path,
) -> dict[str, Any]:
    if source_kind == "image":
        image_bytes = case.image_path.read_bytes()
        source_path = case.image_path
        extracted_image_path = None
    elif source_kind == "pdf":
        image_bytes, image_name = _embedded_pdf_image_bytes(case.pdf_path)
        extracted_image_path = out_dir / image_name
        extracted_image_path.write_bytes(image_bytes)
        source_path = case.pdf_path
    else:
        raise ValueError(f"Unsupported source kind: {source_kind}")

    response = _call_ollama(
        model=model,
        prompt="Text Recognition:",
        image_bytes=image_bytes,
        ollama_url=ollama_url,
    )

    raw_path = out_dir / "response.json"
    _write_json(raw_path, response)

    artifact_path = out_dir / "pages_html.jsonl"
    _write_page_artifact(
        artifact_path,
        run_id=out_dir.name,
        html=response.get("response", ""),
        source=str(source_path),
    )

    metrics = score_page_html_artifact(case.transcript_path, artifact_path)
    result = {
        "case_id": case.case_id,
        "source_kind": source_kind,
        "transcript_path": str(case.transcript_path),
        "source_path": str(source_path),
        "artifact_path": str(artifact_path),
        "response_path": str(raw_path),
        "response_char_count": len(response.get("response", "")),
        "metrics": metrics,
        "ollama": {
            key: response.get(key)
            for key in (
                "model",
                "created_at",
                "done",
                "done_reason",
                "total_duration",
                "load_duration",
                "prompt_eval_count",
                "prompt_eval_duration",
                "eval_count",
                "eval_duration",
            )
        },
    }
    if extracted_image_path is not None:
        result["extracted_image_path"] = str(extracted_image_path)
    return result


def _score_onward_output(output_html: str, golden_path: Path) -> dict[str, Any]:
    score = score_html_table_diff(output_html, {"vars": {"golden_path": str(golden_path)}})
    score["golden_path"] = str(golden_path)
    return score


def run_onward_page(
    *,
    page: OnwardPage,
    model: str,
    ollama_url: str,
    out_dir: Path,
    incumbent_rows: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    response = _call_ollama(
        model=model,
        prompt="Table Recognition:",
        image_bytes=page.image_path.read_bytes(),
        ollama_url=ollama_url,
    )

    raw_path = out_dir / "response.json"
    _write_json(raw_path, response)
    output_path = out_dir / "glm_output.html"
    output_path.write_text(response.get("response", ""), encoding="utf-8")

    incumbent_row = incumbent_rows.get(page.page_number)
    if incumbent_row is None:
        raise ValueError(f"Missing incumbent row for page {page.page_number}")

    glm_score = _score_onward_output(response.get("response", ""), page.golden_path)
    incumbent_score = _score_onward_output(incumbent_row.get("html", ""), page.golden_path)

    return {
        "page_number": page.page_number,
        "image_path": str(page.image_path),
        "golden_path": str(page.golden_path),
        "glm_output_path": str(output_path),
        "response_path": str(raw_path),
        "glm_output_char_count": len(response.get("response", "")),
        "glm_score": glm_score,
        "incumbent_score": incumbent_score,
        "incumbent_html_char_count": len(incumbent_row.get("html", "")),
        "ollama": {
            key: response.get(key)
            for key in (
                "model",
                "created_at",
                "done",
                "done_reason",
                "total_duration",
                "load_duration",
                "prompt_eval_count",
                "prompt_eval_duration",
                "eval_count",
                "eval_duration",
            )
        },
    }


def _summarize_handwritten(results: list[dict[str, Any]]) -> dict[str, Any]:
    ratios = [result["metrics"]["overall_ratio"] for result in results]
    page_mins = [result["metrics"]["page_min_ratio"] for result in results]
    passes = [
        result["metrics"]["overall_ratio"] >= 0.99 and result["metrics"]["page_min_ratio"] >= 0.99
        for result in results
    ]
    return {
        "case_count": len(results),
        "cases_passing": sum(1 for passed in passes if passed),
        "pass_rate": round(sum(1 for passed in passes if passed) / len(passes), 6),
        "overall_min_ratio": min(ratios),
        "page_min_ratio": min(page_mins),
    }


def _summarize_onward(results: list[dict[str, Any]]) -> dict[str, Any]:
    glm_scores = [result["glm_score"]["score"] for result in results]
    incumbent_scores = [result["incumbent_score"]["score"] for result in results]
    glm_passes = [bool(result["glm_score"]["pass"]) for result in results]
    incumbent_passes = [bool(result["incumbent_score"]["pass"]) for result in results]
    return {
        "page_count": len(results),
        "glm_average_score": round(sum(glm_scores) / len(glm_scores), 6),
        "glm_min_score": min(glm_scores),
        "glm_pages_passing": sum(1 for passed in glm_passes if passed),
        "incumbent_average_score": round(sum(incumbent_scores) / len(incumbent_scores), 6),
        "incumbent_min_score": min(incumbent_scores),
        "incumbent_pages_passing": sum(1 for passed in incumbent_passes if passed),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Story 208 GLM-OCR benchmark via Ollama")
    parser.add_argument("--out-root", default=str(DEFAULT_OUT_ROOT))
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)
    args = parser.parse_args()

    out_root = _ensure_dir(Path(args.out_root))
    incumbent_rows = {
        row["page_number"]: row
        for row in _read_jsonl(ONWARD_INCUMBENT_ARTIFACT)
        if row.get("page_number") in {page.page_number for page in ONWARD_PAGES}
    }

    handwritten_results = []
    handwritten_root = _ensure_dir(out_root / "handwritten")
    for case in HANDWRITTEN_CASES:
        for source_kind in ("image", "pdf"):
            case_dir = _ensure_dir(handwritten_root / f"{case.case_id}-{source_kind}")
            handwritten_results.append(
                run_handwritten_case(
                    case=case,
                    source_kind=source_kind,
                    model=args.model,
                    ollama_url=args.ollama_url,
                    out_dir=case_dir,
                )
            )
    _write_json(handwritten_root / "results.json", handwritten_results)

    onward_results = []
    onward_root = _ensure_dir(out_root / "onward-marie-louise")
    for page in ONWARD_PAGES:
        page_dir = _ensure_dir(onward_root / f"page-{page.page_number:03d}")
        onward_results.append(
            run_onward_page(
                page=page,
                model=args.model,
                ollama_url=args.ollama_url,
                out_dir=page_dir,
                incumbent_rows=incumbent_rows,
            )
        )
    _write_json(onward_root / "results.json", onward_results)

    summary = {
        "model": args.model,
        "ollama_url": args.ollama_url,
        "runtime": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "ollama": _ollama_model_details(args.model),
        },
        "handwritten": {
            "baseline_reference": {
                "overall_min_ratio": 0.677267,
                "pass_rate": 0.6,
                "source_story": "191/192 maintained handwritten rescue baseline",
            },
            "summary": _summarize_handwritten(handwritten_results),
            "results_path": str(handwritten_root / "results.json"),
        },
        "onward_marie_louise": {
            "incumbent_artifact_path": str(ONWARD_INCUMBENT_ARTIFACT),
            "summary": _summarize_onward(onward_results),
            "results_path": str(onward_root / "results.json"),
        },
    }
    _write_json(out_root / "summary.json", summary)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
