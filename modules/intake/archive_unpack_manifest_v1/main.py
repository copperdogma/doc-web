#!/usr/bin/env python3
"""
Archive Unpack Manifest Module v1

Unpacks a bounded ZIP archive into the current run and emits one
archive_member_manifest_v1 row per member.
"""

from __future__ import annotations

import argparse
import hashlib
import posixpath
import zipfile
from pathlib import Path, PurePosixPath

from modules.common.utils import ProgressLogger, ensure_dir, save_jsonl, utc_now
from modules.intake.intake_plan_utils import infer_archive_member_input_kind


MODULE_ID = "archive_unpack_manifest_v1"
SCHEMA_VERSION = "archive_member_manifest_v1"
DEFAULT_OUT = "archive_members_manifest.jsonl"


def _safe_member_path(raw_name: str) -> str:
    normalized = posixpath.normpath(str(raw_name or "").replace("\\", "/")).lstrip("/")
    if not normalized or normalized == ".":
        raise SystemExit(f"Archive member path is empty after normalization: {raw_name!r}")
    parts = PurePosixPath(normalized).parts
    if any(part == ".." for part in parts):
        raise SystemExit(f"Archive member path escapes root: {raw_name!r}")
    return str(PurePosixPath(*parts))


def _extract_member(archive: zipfile.ZipFile, member_info: zipfile.ZipInfo, extracted_root: Path) -> tuple[str, str]:
    member_path = _safe_member_path(member_info.filename)
    destination = extracted_root / Path(member_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = archive.read(member_info)
    destination.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    return member_path, digest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", required=True, help="Path to the input ZIP archive")
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

    zip_path = Path(args.zip).resolve()
    if not zip_path.exists():
        raise SystemExit(f"ZIP archive not found: {zip_path}")

    outdir = Path(args.outdir).resolve()
    ensure_dir(str(outdir))
    extracted_root = outdir / "extracted_members"
    extracted_root.mkdir(parents=True, exist_ok=True)
    out_path = outdir / args.out

    logger.log(
        "extract",
        "running",
        current=0,
        total=None,
        message=f"Unpacking bounded ZIP archive {zip_path.name}",
        module_id=MODULE_ID,
        schema_version=SCHEMA_VERSION,
    )

    rows: list[dict] = []
    seen_paths: set[str] = set()

    with zipfile.ZipFile(zip_path) as archive:
        members = [info for info in archive.infolist() if not info.is_dir()]
        if not members:
            raise SystemExit(f"No file members found in {zip_path}")

        for member_index, member_info in enumerate(members, start=1):
            member_path, digest = _extract_member(archive, member_info, extracted_root)
            if member_path in seen_paths:
                raise SystemExit(f"Duplicate archive member path after normalization: {member_path}")
            seen_paths.add(member_path)
            extracted_path = extracted_root / Path(member_path)
            rows.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "archive_format": "zip",
                    "archive_path": str(zip_path),
                    "member_id": f"member-{member_index:03d}",
                    "member_index": member_index,
                    "member_path": member_path,
                    "extracted_path": str(extracted_path),
                    "filename": extracted_path.name,
                    "file_extension": extracted_path.suffix.lower() or None,
                    "detected_input_kind": infer_archive_member_input_kind(member_path),
                    "file_size_bytes": member_info.file_size,
                    "sha256": digest,
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
        message=f"Unpacked {len(rows)} ZIP members into a stamped manifest",
        artifact=str(out_path),
        module_id=MODULE_ID,
        schema_version=SCHEMA_VERSION,
    )


if __name__ == "__main__":
    main()
