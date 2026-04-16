#!/usr/bin/env python3
"""
Archive Route Members Module v1

Routes bounded archive or folder members into existing maintained direct-entry
recipes, reuses the maintained recommendation-only PDF intake seam for bounded
PDF members, and records one archive_member_route_v1 row per member.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Optional

import yaml

from modules.common.utils import ProgressLogger, read_jsonl, save_jsonl, utc_now
from modules.intake.intake_plan_utils import (
    archive_member_recipe_for_input_kind,
    build_explicit_recipe_driver_command,
    default_downstream_run_id,
    load_artifact_row,
    prepare_confirmed_handoff,
)


MODULE_ID = "archive_route_members_v1"
SCHEMA_VERSION = "archive_member_route_v1"
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUT = "archive_member_routes.jsonl"
PDF_MEMBER_RECOMMENDATION_RECIPE = "configs/recipes/recipe-intake-contact-sheet.yaml"
PDF_MEMBER_APPROVAL_MODE = "confirm_plan_auto_approve"
PDF_MEMBER_HANDOFF_MODES = {"recommendation_only", "dry_run", "launch"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="Input archive member manifest JSONL")
    parser.add_argument("--folder", default=None, help="Optional original folder path for driver compatibility")
    parser.add_argument("--zip", default=None, help="Optional original ZIP path for backward compatibility")
    parser.add_argument("--outdir", required=True, help="Output directory")
    parser.add_argument("--out", default=DEFAULT_OUT, help="Output route artifact path")
    parser.add_argument("--downstream-end-at", dest="downstream_end_at", default=None)
    parser.add_argument(
        "--pdf-member-handoff-mode",
        dest="pdf_member_handoff_mode",
        default="recommendation_only",
        choices=sorted(PDF_MEMBER_HANDOFF_MODES),
        help="How PDF members should continue after the nested approved plan is emitted.",
    )
    parser.add_argument("--allow-run-id-reuse", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--progress-file", help="Path to pipeline_events.jsonl")
    parser.add_argument("--state-file", help="Path to pipeline_state.json")
    parser.add_argument("--run-id", help="Run identifier for logging")
    return parser.parse_args()


def _load_stage_specs(recipe_path: str) -> list[dict]:
    data = yaml.safe_load((REPO_ROOT / recipe_path).read_text(encoding="utf-8")) or {}
    stages = data.get("stages") or []
    stage_specs = []
    for ordinal, stage in enumerate(stages, start=1):
        stage_specs.append(
            {
                "ordinal": ordinal,
                "module": stage.get("module"),
                "out": stage.get("out"),
            }
        )
    return stage_specs


def _downstream_artifact(
    output_root: Path,
    downstream_run_id: str,
    recipe_path: str,
    *,
    stage_position: str = "first",
) -> Optional[str]:
    stage_specs = _load_stage_specs(recipe_path)
    if not stage_specs:
        return None
    if stage_position == "first":
        stage_spec = stage_specs[0]
    elif stage_position == "last":
        stage_spec = stage_specs[-1]
    else:
        raise ValueError(f"Unsupported stage_position: {stage_position}")
    module_id = str(stage_spec.get("module") or "").strip()
    out_name = str(stage_spec.get("out") or "").strip()
    if not module_id or not out_name:
        return None
    ordinal = int(stage_spec["ordinal"])
    return str(output_root / downstream_run_id / f"{ordinal:02d}_{module_id}" / out_name)


def _blocked_reason_for_member(row: dict) -> str:
    kind = row.get("detected_input_kind")
    if kind == "pdf":
        return "pdf_member_outside_bounded_mixed_archive_slice"
    extension = str(row.get("file_extension") or "").strip() or "missing"
    if kind:
        return f"archive_member_input_kind_outside_bounded_slice:{kind}"
    return f"unsupported_archive_member_suffix:{extension}"


def _resolve_output_path(outdir: str, out: str) -> Path:
    out_path = Path(out)
    if out_path.is_absolute():
        return out_path
    if out_path.parent != Path("."):
        return out_path
    return Path(outdir) / out_path.name


def _uses_pdf_member_recommendation(row: dict) -> bool:
    archive_format = str(row.get("archive_format") or "zip").strip().lower()
    return archive_format in {"zip", "folder"} and row.get("detected_input_kind") == "pdf"


def _handoff_artifact_path(outdir: str | Path, member_id: str) -> Path:
    return Path(outdir) / "pdf_member_handoffs" / member_id / "intake_handoff.jsonl"


def _apply_pdf_member_handoff(
    route_row: dict,
    *,
    plan: dict,
    plan_path: str,
    member_id: str,
    args: argparse.Namespace,
    output_root: Path,
) -> bool:
    emitted_recipe = str(plan.get("recommended_recipe") or "").strip()
    downstream_run_id = default_downstream_run_id(
        emitted_recipe or "approved-handoff",
        f"{args.run_id or 'mixed-archive'}-{member_id}-approved-handoff",
    )
    handoff_path = _handoff_artifact_path(args.outdir, member_id).resolve()
    handoff_row, handoff_command, should_launch = prepare_confirmed_handoff(
        plan,
        plan_path=plan_path,
        upstream_run_id=args.run_id,
        downstream_run_id=downstream_run_id,
        downstream_output_dir=output_root,
        downstream_end_at=args.downstream_end_at,
        dry_run=args.pdf_member_handoff_mode == "dry_run",
        allow_run_id_reuse=args.allow_run_id_reuse,
    )
    handoff_row["module_id"] = MODULE_ID
    route_row["handoff_artifact_path"] = str(handoff_path)
    save_jsonl(str(handoff_path), [handoff_row])

    if handoff_row["terminal_outcome"] == "blocked":
        route_row["terminal_outcome"] = "blocked"
        route_row["terminal_reason"] = (
            f"pdf_member_handoff_blocked:{handoff_row['terminal_reason']}"
        )
        return False

    if not should_launch:
        route_row["terminal_outcome"] = handoff_row["terminal_outcome"]
        if handoff_row["terminal_reason"] == "dry_run":
            route_row["terminal_reason"] = "pdf_member_approved_handoff_dry_run"
        else:
            route_row["terminal_reason"] = (
                f"pdf_member_handoff_{handoff_row['terminal_outcome']}:"
                f"{handoff_row['terminal_reason']}"
            )
        return True

    result = subprocess.run(handoff_command, cwd=str(REPO_ROOT))
    handoff_row["exit_code"] = result.returncode
    if result.returncode != 0:
        handoff_row["terminal_outcome"] = "failed"
        handoff_row["terminal_reason"] = f"downstream_exit_{result.returncode}"
        route_row["terminal_outcome"] = "failed"
        route_row["terminal_reason"] = (
            f"pdf_member_handoff_downstream_exit_{result.returncode}"
        )
        save_jsonl(str(handoff_path), [handoff_row])
        return False

    handoff_row["terminal_outcome"] = "launched"
    handoff_row["terminal_reason"] = None
    route_row["terminal_outcome"] = "launched"
    route_row["terminal_reason"] = "pdf_member_launched_from_approved_plan"
    save_jsonl(str(handoff_path), [handoff_row])
    return True


def main() -> None:
    args = parse_args()
    logger = ProgressLogger(
        state_path=args.state_file,
        progress_path=args.progress_file,
        run_id=args.run_id,
    )

    manifest_rows = list(read_jsonl(args.manifest))
    if not manifest_rows:
        raise SystemExit("No archive member manifest rows found; cannot route archive members")

    out_path = _resolve_output_path(args.outdir, args.out)
    output_root = Path(args.outdir).resolve().parent.parent

    logger.log(
        "archive_route",
        "running",
        current=0,
        total=len(manifest_rows),
        message=f"Routing {len(manifest_rows)} bounded mixed-input members",
        module_id=MODULE_ID,
        schema_version=SCHEMA_VERSION,
    )

    route_rows: list[dict] = []
    failed_launches = 0

    for row in manifest_rows:
        member_id = str(row["member_id"])
        input_kind = row.get("detected_input_kind")
        use_pdf_member_recommendation = _uses_pdf_member_recommendation(row)
        recipe_path = (
            PDF_MEMBER_RECOMMENDATION_RECIPE
            if use_pdf_member_recommendation
            else archive_member_recipe_for_input_kind(input_kind)
        )
        extracted_path = Path(str(row["extracted_path"]))
        route_row = {
            "schema_version": SCHEMA_VERSION,
            "archive_format": row.get("archive_format") or "zip",
            "archive_path": row["archive_path"],
            "member_id": member_id,
            "member_index": row["member_index"],
            "member_path": row["member_path"],
            "extracted_path": str(extracted_path),
            "filename": row["filename"],
            "file_extension": row.get("file_extension"),
            "detected_input_kind": input_kind,
            "recommended_recipe": None if use_pdf_member_recommendation else recipe_path,
            "launch_input_flag": None,
            "launch_input_path": None,
            "driver_command": [],
            "downstream_run_id": None,
            "downstream_output_dir": None,
            "first_downstream_artifact": None,
            "approval_mode": None,
            "handoff_artifact_path": None,
            "terminal_outcome": "blocked",
            "terminal_reason": None,
            "exit_code": None,
            "module_id": MODULE_ID,
            "run_id": args.run_id,
            "created_at": utc_now(),
        }

        if not extracted_path.exists():
            route_row["terminal_reason"] = f"extracted_member_not_found:{extracted_path}"
            route_rows.append(route_row)
            failed_launches += 1
            continue

        if not recipe_path:
            route_row["terminal_reason"] = _blocked_reason_for_member(row)
            route_rows.append(route_row)
            continue

        downstream_run_id = default_downstream_run_id(
            recipe_path,
            f"{args.run_id or 'mixed-archive'}-{member_id}",
        )
        downstream_output_dir = output_root / downstream_run_id
        first_downstream_artifact = _downstream_artifact(
            output_root,
            downstream_run_id,
            recipe_path,
            stage_position="last" if use_pdf_member_recommendation else "first",
        )
        command = build_explicit_recipe_driver_command(
            recipe_path,
            input_kind=input_kind,
            source_path=extracted_path,
            downstream_run_id=downstream_run_id,
            downstream_output_dir=output_root,
            downstream_end_at=args.downstream_end_at,
            allow_run_id_reuse=args.allow_run_id_reuse,
        )

        route_row["launch_input_flag"] = command[4]
        route_row["launch_input_path"] = str(extracted_path)
        route_row["driver_command"] = command
        route_row["downstream_run_id"] = downstream_run_id
        route_row["downstream_output_dir"] = str(downstream_output_dir)
        route_row["first_downstream_artifact"] = first_downstream_artifact

        if args.dry_run:
            route_row["terminal_outcome"] = "skipped"
            route_row["terminal_reason"] = "dry_run"
            route_rows.append(route_row)
            continue

        result = subprocess.run(command, cwd=str(REPO_ROOT))
        route_row["exit_code"] = result.returncode
        if result.returncode != 0:
            route_row["terminal_outcome"] = "failed"
            route_row["terminal_reason"] = f"downstream_exit_{result.returncode}"
            route_rows.append(route_row)
            failed_launches += 1
            continue

        if first_downstream_artifact and not Path(first_downstream_artifact).exists():
            route_row["terminal_outcome"] = "failed"
            route_row["terminal_reason"] = "first_downstream_artifact_missing"
            route_rows.append(route_row)
            failed_launches += 1
            continue

        if use_pdf_member_recommendation:
            plan = load_artifact_row(first_downstream_artifact)
            emitted_recipe = str(plan.get("recommended_recipe") or "").strip()
            route_row["recommended_recipe"] = emitted_recipe or None
            route_row["approval_mode"] = PDF_MEMBER_APPROVAL_MODE
            if args.pdf_member_handoff_mode != "recommendation_only":
                continuation_ok = _apply_pdf_member_handoff(
                    route_row,
                    plan=plan,
                    plan_path=first_downstream_artifact,
                    member_id=member_id,
                    args=args,
                    output_root=output_root,
                )
                route_rows.append(route_row)
                if not continuation_ok:
                    failed_launches += 1
                continue
            route_row["terminal_reason"] = "pdf_member_recommendation_only"

        route_row["terminal_outcome"] = "launched"
        route_rows.append(route_row)

    save_jsonl(str(out_path), route_rows)

    launched = sum(1 for row in route_rows if row["terminal_outcome"] == "launched")
    blocked = sum(1 for row in route_rows if row["terminal_outcome"] == "blocked")
    skipped = sum(1 for row in route_rows if row["terminal_outcome"] == "skipped")
    failed = sum(1 for row in route_rows if row["terminal_outcome"] == "failed")
    logger.log(
        "archive_route",
        "done" if failed == 0 else "failed",
        current=len(route_rows),
        total=len(route_rows),
        message=(
            f"Archive routing complete: launched={launched}, blocked={blocked}, "
            f"skipped={skipped}, failed={failed}"
        ),
        artifact=str(out_path),
        module_id=MODULE_ID,
        schema_version=SCHEMA_VERSION,
    )

    if failed_launches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
