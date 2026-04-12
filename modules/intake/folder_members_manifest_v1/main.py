#!/usr/bin/env python3
"""
Folder Members Manifest Module v1

Inventories one bounded source-native folder tree into
archive_member_manifest_v1 rows without copying members into the run.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path, PurePosixPath

from modules.common.utils import ProgressLogger, ensure_dir, save_jsonl, utc_now
from modules.intake.intake_plan_utils import infer_archive_member_input_kind


MODULE_ID = "folder_members_manifest_v1"
SCHEMA_VERSION = "archive_member_manifest_v1"
DEFAULT_OUT = "archive_members_manifest.jsonl"


def _safe_member_path(raw_name: str) -> str:
    rendered = str(raw_name or "").replace("\\", "/").strip().lstrip("/")
    normalized = PurePosixPath(rendered)
    if not rendered:
        raise SystemExit(f"Folder member path is empty after normalization: {raw_name!r}")
    if normalized.is_absolute():
        raise SystemExit(f"Folder member path must be relative: {raw_name!r}")
    if any(part in {"..", "."} for part in normalized.parts):
        raise SystemExit(
            f"Folder member path must stay normalized under root: {raw_name!r}"
        )
    return str(normalized)


def _iter_member_paths(folder_path: Path) -> list[Path]:
    members = []
    for path in folder_path.rglob("*"):
        if path.is_symlink():
            raise SystemExit(
                f"Symlinked paths are outside the bounded mixed-folder slice: {path}"
            )
        if path.is_file():
            members.append(path)
    members.sort(key=lambda path: path.relative_to(folder_path).as_posix())
    return members


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", required=True, help="Path to the input folder tree")
    parser.add_argument("--outdir", required=True, help="Output directory")
    parser.add_argument("--out", default=DEFAULT_OUT, help="Output manifest filename")
    parser.add_argument("--progress-file", help="Path to pipeline_events.jsonl")
    parser.add_argument("--state-file", help="Path to pipeline_state.json")
    parser.add_argument("--run-id", help="Run identifier for logging")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logger = ProgressLogger(
        state_path=args.state_file,
        progress_path=args.progress_file,
        run_id=args.run_id,
    )

    folder_path = Path(args.folder).resolve()
    if not folder_path.exists():
        raise SystemExit(f"Input folder not found: {folder_path}")
    if not folder_path.is_dir():
        raise SystemExit(f"Input folder is not a directory: {folder_path}")

    outdir = Path(args.outdir).resolve()
    ensure_dir(str(outdir))
    out_path = outdir / args.out

    logger.log(
        "extract",
        "running",
        current=0,
        total=None,
        message=f"Inventorying bounded folder tree {folder_path.name}",
        module_id=MODULE_ID,
        schema_version=SCHEMA_VERSION,
    )

    members = _iter_member_paths(folder_path)
    if not members:
        raise SystemExit(f"No file members found in {folder_path}")

    rows: list[dict] = []
    seen_paths: set[str] = set()
    for member_index, member_path_abs in enumerate(members, start=1):
        member_path = _safe_member_path(
            member_path_abs.relative_to(folder_path).as_posix()
        )
        if member_path in seen_paths:
            raise SystemExit(
                f"Duplicate folder member path after normalization: {member_path}"
            )
        seen_paths.add(member_path)
        payload = member_path_abs.read_bytes()
        rows.append(
            {
                "schema_version": SCHEMA_VERSION,
                "archive_format": "folder",
                "archive_path": str(folder_path),
                "member_id": f"member-{member_index:03d}",
                "member_index": member_index,
                "member_path": member_path,
                "extracted_path": str(member_path_abs),
                "filename": member_path_abs.name,
                "file_extension": member_path_abs.suffix.lower() or None,
                "detected_input_kind": infer_archive_member_input_kind(member_path),
                "file_size_bytes": member_path_abs.stat().st_size,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "module_id": MODULE_ID,
                "run_id": args.run_id,
                "created_at": utc_now(),
            }
        )

    save_jsonl(str(out_path), rows)
    logger.log(
        "extract",
        "done",
        current=len(rows),
        total=len(rows),
        message=f"Inventoried {len(rows)} folder members into a stamped manifest",
        artifact=str(out_path),
        module_id=MODULE_ID,
        schema_version=SCHEMA_VERSION,
    )


if __name__ == "__main__":
    main()
