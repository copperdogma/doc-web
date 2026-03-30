from __future__ import annotations

import argparse
from pathlib import Path

from modules.common.marker_lite_runtime import (
    DEFAULT_BASE_IMAGE,
    DEFAULT_BOOTSTRAP_FROM_CONTAINER,
    DEFAULT_BOOTSTRAP_IMAGE,
    DEFAULT_CONTAINER,
    ensure_runtime_container,
    extract_pdftotext_source,
    run_lite_api,
    runtime_metadata,
)
from modules.common.marker_page_html import (
    normalize_marker_document,
    read_json,
    utc_now,
    write_marker_outputs,
)
from modules.common.utils import ProgressLogger, save_json


MODULE_ID = "extract_pdf_marker_lite_html_v1"
SCHEMA_VERSION = "page_html_v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract born-digital PDF HTML through the bounded Marker-lite runtime."
    )
    parser.add_argument("--pdf", required=True, help="Path to input PDF")
    parser.add_argument("--outdir", required=True, help="Output directory")
    parser.add_argument("--out", default="pages_html.jsonl", help="Output page_html_v1 artifact name")
    parser.add_argument("--container-name", default=DEFAULT_CONTAINER, help="Docker container name for the Marker-lite runtime")
    parser.add_argument(
        "--bootstrap-from-container",
        default=DEFAULT_BOOTSTRAP_FROM_CONTAINER,
        help="Existing container name to use as a bootstrap seed when the target runtime is missing",
    )
    parser.add_argument(
        "--bootstrap-image",
        default=DEFAULT_BOOTSTRAP_IMAGE,
        help="Preferred cached Docker image for the repo-local Marker-lite runtime",
    )
    parser.add_argument(
        "--base-image",
        default=DEFAULT_BASE_IMAGE,
        help="Base image to pull only when no cached Marker runtime is available",
    )
    parser.add_argument(
        "--no-bootstrap",
        dest="allow_bootstrap",
        action="store_false",
        default=True,
        help="Fail instead of rebuilding the Marker-lite runtime when the target container is unusable",
    )
    parser.add_argument("--progress-file", help="Path to pipeline_events.jsonl")
    parser.add_argument("--state-file", help="Path to pipeline_state.json")
    parser.add_argument("--run-id", help="Run identifier for logging")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logger = ProgressLogger(state_path=args.state_file, progress_path=args.progress_file, run_id=args.run_id)
    outdir = Path(args.outdir)
    pdf_path = Path(args.pdf).resolve()

    def emit_progress(message: str, extra: dict[str, object]) -> None:
        logger.log(
            "extract",
            "running",
            message=message,
            module_id=MODULE_ID,
            schema_version=SCHEMA_VERSION,
            extra=extra,
        )

    logger.log(
        "extract",
        "running",
        message="Preparing repo-local Marker-lite runtime for born-digital PDF extraction",
        module_id=MODULE_ID,
        schema_version=SCHEMA_VERSION,
    )

    try:
        runtime_bootstrap = ensure_runtime_container(
            container_name=args.container_name,
            bootstrap_from_container=args.bootstrap_from_container,
            bootstrap_image=args.bootstrap_image,
            base_image=args.base_image,
            allow_bootstrap=args.allow_bootstrap,
            progress=emit_progress,
        )
        container_name = str(runtime_bootstrap["container_name"])
        marker_raw_dir = outdir / "marker_raw" / "json"
        pdftotext_dir = outdir / "marker_raw"
        pdftotext_path = extract_pdftotext_source(
            pdf_path,
            pdftotext_dir,
            progress=emit_progress,
        )
        marker_artifact = run_lite_api(
            container_name=container_name,
            input_pdf=pdf_path,
            output_dir=marker_raw_dir,
            output_format="json",
            progress=emit_progress,
        )
        created_at = utc_now()
        emit_progress(
            "Normalizing Marker-lite output into page_html rows and provenance blocks",
            {"substep": "normalize", "marker_json": str(marker_artifact.main_output)},
        )
        page_rows, block_rows, bundle, runtime_trace, summary, normalization_report = normalize_marker_document(
            read_json(marker_artifact.main_output),
            input_pdf=pdf_path,
            marker_json=marker_artifact.main_output,
            marker_meta=marker_artifact.meta_output,
            run_id=args.run_id,
            module_id=MODULE_ID,
            created_at=created_at,
            pdftotext_text=pdftotext_path.read_text(encoding="utf-8"),
            processing_step=f"{MODULE_ID}.page_html_v1",
        )

        emit_progress(
            "Writing normalized Marker-lite artifacts and runtime metadata",
            {"substep": "write", "output_dir": str(outdir)},
        )
        output_artifacts = write_marker_outputs(
            outdir,
            artifact_name=args.out,
            page_rows=page_rows,
            block_rows=block_rows,
            bundle=bundle,
            runtime_trace=runtime_trace,
            summary=summary,
            normalization_report=normalization_report,
        )
        runtime_path = outdir / "marker_runtime.json"
        runtime_payload = {
            "bootstrap": runtime_bootstrap,
            "metadata": runtime_metadata(container_name),
            "raw_artifacts": {
                "marker_json": str(marker_artifact.main_output),
                "marker_meta": str(marker_artifact.meta_output),
                "marker_log": str(marker_artifact.log_output),
                "pdftotext": str(pdftotext_path),
            },
        }
        save_json(str(runtime_path), runtime_payload)
        summary["runtime"] = {
            "runtime_report": str(runtime_path),
            "bootstrap_action": runtime_bootstrap.get("action"),
            "container_name": container_name,
        }
        save_json(str(outdir / "summary.json"), summary)

        logger.log(
            "extract",
            "done",
            artifact=output_artifacts["pages_html"],
            message=(
                "Marker-lite born-digital extraction completed with "
                f"{normalization_report['heading_level_normalization']['adjusted_heading_count']} heading adjustments "
                f"and {normalization_report['choice_paragraph_split']['paragraphs_split']} split paragraphs"
            ),
            module_id=MODULE_ID,
            schema_version=SCHEMA_VERSION,
            extra={
                "runtime_report": str(runtime_path),
                "bootstrap_action": runtime_bootstrap.get("action"),
                "normalization_report": output_artifacts["normalization_report"],
            },
        )
    except Exception as exc:
        logger.log(
            "extract",
            "error",
            message=f"Marker-lite born-digital extraction failed: {exc}",
            module_id=MODULE_ID,
            schema_version=SCHEMA_VERSION,
        )
        raise


if __name__ == "__main__":
    main()
