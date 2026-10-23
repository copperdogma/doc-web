"""Detect stale archive/folder inventory immediately before dispatch.

These checks do not provide an execution snapshot or prevent later mutation.
"""

from __future__ import annotations

import hashlib
import json
import re
import stat
from pathlib import Path, PurePosixPath

from modules.extract.images_dir_to_manifest_v1.main import _iter_images


def _member_error(code: str, row: dict, manifest: str, **observed) -> str:
    return code + ":" + json.dumps({
        "manifest": str(manifest), "member_id": row.get("member_id"),
        "member_path": row.get("member_path"), "source_path": row.get("extracted_path"),
        "expected_sha256": row.get("sha256"), "expected_bytes": row.get("file_size_bytes"),
        **observed,
    }, sort_keys=True)


def member_identity_error(row: dict, manifest: str) -> str | None:
    """Return an inspectable failure without refreshing the expected identity."""
    digest = row.get("sha256")
    size = row.get("file_size_bytes")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        return _member_error("member_identity_invalid_sha256", row, manifest)
    if type(size) is not int or size < 0:
        return _member_error("member_identity_invalid_size", row, manifest)

    name = str(row.get("member_path") or "")
    relative = PurePosixPath(name)
    path = Path(str(row.get("extracted_path") or ""))
    if (not name or relative.is_absolute() or ".." in relative.parts
            or "\\" in name or str(relative) != name or not path.is_absolute()):
        return _member_error("member_identity_invalid_path", row, manifest)
    archive_format = str(row.get("archive_format") or "zip").lower()
    if archive_format == "folder":
        root = Path(str(row.get("archive_path") or ""))
    elif archive_format == "zip" and len(path.parents) >= len(relative.parts):
        # Extracted files can be reused from an older run. Do not infer their
        # root from the current manifest's location.
        root = path.parents[len(relative.parts) - 1]
    else:
        return _member_error("member_identity_invalid_root", row, manifest)
    if not root.is_absolute() or root / Path(name) != path:
        return _member_error("member_identity_path_mismatch", row, manifest)

    try:
        if root.resolve() != root:
            return _member_error("member_identity_symlink", row, manifest)
        candidate = root
        for part in relative.parts:
            candidate = candidate / part
            if candidate.is_symlink():
                return _member_error("member_identity_symlink", row, manifest)
        if not stat.S_ISREG(path.lstat().st_mode):
            return _member_error("member_identity_not_regular", row, manifest)
        observed_digest = hashlib.sha256()
        observed_size = 0
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                observed_digest.update(chunk)
                observed_size += len(chunk)
    except (OSError, RuntimeError) as error:
        return _member_error("member_identity_unavailable", row, manifest, error=str(error))
    actual_digest = observed_digest.hexdigest()
    if observed_size != size or actual_digest != digest:
        return _member_error(
            "member_identity_mismatch", row, manifest,
            observed_sha256=actual_digest, observed_bytes=observed_size,
        )
    return None


def grouped_image_identity_error(group: dict, manifest: str) -> str | None:
    directory = Path(group["launch_input_path"])
    if any(Path(row["extracted_path"]).parent != directory for row in group["rows"]):
        return "grouped_image_membership_path_mismatch:" + json.dumps({
            "manifest": str(manifest), "directory": str(directory),
            "member_paths": [row["extracted_path"] for row in group["rows"]],
        }, sort_keys=True)
    for row in group["rows"]:
        error = member_identity_error(row, manifest)
        if error:
            return error
    expected = sorted(Path(row["extracted_path"]).name for row in group["rows"])
    try:
        # Reuse the consumer's exact immediate-file predicate, including hidden
        # images and case-insensitive suffixes, without recursive enumeration.
        observed = sorted(path.name for path in _iter_images(directory))
    except OSError as error:
        return "grouped_image_membership_unavailable:" + json.dumps({
            "manifest": str(manifest), "directory": str(directory), "error": str(error),
        }, sort_keys=True)
    if observed != expected:
        return "grouped_image_membership_mismatch:" + json.dumps({
            "manifest": str(manifest), "directory": str(directory),
            "expected_names": expected, "observed_names": observed,
            "missing": sorted(set(expected) - set(observed)),
            "extra": sorted(set(observed) - set(expected)),
        }, sort_keys=True)
    return None
