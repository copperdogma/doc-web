"""Offline provider-state redaction; exact originals stay in protected custody."""

import copy
import hashlib
import io
import json
import math
import re
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / "docs/evals/evidence/089-carbon"
PROTECTED = Path(
    "/Users/cam/.codex/archives/carbon-20261110/doc-web/provider-state-originals"
)
MARKER = "[REDACTED_PROVIDER_STATE]"
STATE_KEYS = {
    "continuation_token",
    "continuationToken",
    "access_token",
    "accessToken",
    "refresh_token",
    "refreshToken",
    "id_token",
    "idToken",
    "thoughtSignature",
    "thought_signature",
    "encrypted_content",
    "encryptedContent",
}
SIGNED_URL = re.compile(
    r'https?://[^\s"<>]+[?&](?:X-Amz-Signature|X-Goog-Signature|Signature|sig|token|access_token)=[^\s"<>]+',
    re.I,
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def redact(value, path=""):
    """Preserve semantic content and usage; redact only explicit provider state."""
    fields = []
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            location = path + "/" + key
            if key in STATE_KEYS and item:
                out[key] = MARKER
                if item != MARKER:
                    fields.append(location)
            else:
                out[key], nested = redact(item, location)
                fields.extend(nested)
        return out, fields
    if isinstance(value, list):
        out = []
        for number, item in enumerate(value):
            clean, nested = redact(item, path + "/" + str(number))
            out.append(clean)
            fields.extend(nested)
        return out, fields
    if isinstance(value, str):
        if SIGNED_URL.search(value):
            raise ValueError(
                "signed/auth URL requires separately reviewed projection; no value emitted"
            )
        try:
            nested = json.loads(value)
        except (ValueError, TypeError):
            return value, fields
        if isinstance(nested, (dict, list)):
            clean, nested_fields = redact(nested, path + " [nested-json]")
            if nested_fields:
                return json.dumps(
                    clean, ensure_ascii=False, separators=(",", ":")
                ), nested_fields
    return value, fields


def build():
    assert PROTECTED.stat().st_mode & 0o777 == 0o700
    original_index = json.loads((PROTECTED / "custody-index.json").read_text())
    original_manifest = json.loads((PROTECTED / "manifest.json").read_text())
    original_parts = []
    for row in original_manifest["archive_parts"]:
        path = PROTECTED / Path(row["path"]).name
        assert path.stat().st_mode & 0o777 == 0o600
        raw = path.read_bytes()
        assert sha(raw) == row["sha256"]
        original_parts.append(raw)
    original = b"".join(original_parts)
    assert sha(original) == original_index["archive_sha256"]
    expected = {r["path"]: r for r in original_index["files"]}
    stream = io.BytesIO()
    entries = []
    projections = []
    with (
        tarfile.open(fileobj=io.BytesIO(original), mode="r:gz") as source,
        tarfile.open(fileobj=stream, mode="w:gz", compresslevel=6) as target,
    ):
        for member in source.getmembers():
            assert member.isfile()
            raw = source.extractfile(member).read()
            assert sha(raw) == expected[member.name]["sha256"]
            clean = raw
            fields = []
            try:
                obj = json.loads(raw)
            except (UnicodeDecodeError, ValueError):
                if SIGNED_URL.search(raw.decode("utf8", "ignore")):
                    raise ValueError("signed URL in nonJSON member")
            else:
                projected, fields = redact(obj)
                if fields:
                    clean = (
                        json.dumps(projected, ensure_ascii=False, separators=(",", ":"))
                        + "\n"
                    ).encode()
                    assert redact(obj)[0] == redact(json.loads(clean))[0]
                    projections.append(
                        {
                            "path": member.name,
                            "original_sha256": sha(raw),
                            "original_bytes": len(raw),
                            "projection_sha256": sha(clean),
                            "projection_bytes": len(clean),
                            "redacted_fields": fields,
                            "class": "Google thoughtSignature or OpenAI encrypted_content providerstate",
                            "projection": "not exact original response bytes; semantic/output/usage/model/finish fields preserved",
                        }
                    )
            info = copy.copy(member)
            info.size = len(clean)
            target.addfile(info, io.BytesIO(clean))
            row = {
                "path": member.name,
                "bytes": len(clean),
                "sha256": sha(clean),
                "privacy": "public/synthetic; provider state redacted where indexed",
            }
            if fields:
                row.update(
                    original_sha256=sha(raw),
                    redacted_fields=fields,
                    projection="provider-state-redacted; not exact original response bytes",
                )
            entries.append(row)
    assert len(entries) == 209 and len(projections) == 19
    public = stream.getvalue()
    part_rows = []
    size = math.ceil(len(public) / 6)
    for number in range(6):
        path = E.parent / f"089-carbon-custody.tar.gz.part{number + 1:02}"
        data = public[number * size : (number + 1) * size]
        path.write_bytes(data)
        part_rows.append(
            {
                "path": str(path.relative_to(ROOT)),
                "bytes": len(data),
                "sha256": sha(data),
            }
        )
    assert b"".join((ROOT / r["path"]).read_bytes() for r in part_rows) == public
    expected_public = {r["path"]: r for r in entries}
    with tarfile.open(fileobj=io.BytesIO(public), mode="r:gz") as source:
        for member in source.getmembers():
            raw = source.extractfile(member).read()
            assert sha(raw) == expected_public[member.name]["sha256"]
            try:
                obj = json.loads(raw)
            except (UnicodeDecodeError, ValueError):
                continue
            assert not redact(obj)[1]
    report = {
        "classification": "15Google thoughtSignature and4OpenAI encrypted_content occurrences redacted (2responses+2nestedreportcopies); no continuation_token/continuationToken/access/refresh/id-token/signedURL matches",
        "originals": {
            "directory": str(PROTECTED),
            "permissions": "directory0700/files0600",
            "archive_sha256": sha(original),
            "index": "protected-index.json",
            "members": 209,
        },
        "public_archive": {
            "kind": "token-redacted projection; not exact original response bytes for19indexed members (17responses+2nestedreportcopies)",
            "members": 209,
            "archive_sha256": sha(public),
            "archive_bytes": len(public),
            "parts": part_rows,
        },
        "affected": projections,
        "proof": "all190unaffectedmembers byte-identical; affected19objects equal originals afteronlyexplicitstatefieldredaction; outputtext/usage/model/finish/source/producerepoch unchanged",
        "inference": "none; original ledger and producingbase unchanged",
        "history": "supersedes unpublishedlocal9cc5551; do not push that ancestor",
    }
    (E / "provider-state-redaction.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    index = original_index.copy()
    index.update(
        archive_kind="public token-redacted projection; 19members are not exact original bytes",
        archive_sha256=sha(public),
        archive_bytes=len(public),
        parts=part_rows,
        files=entries,
        original_protected_custody=report["originals"],
        provider_state_redaction="provider-state-redaction.json",
        verified=report["proof"],
    )
    (E / "custody-index.json").write_text(json.dumps(index, indent=2) + "\n")
    manifest = original_manifest.copy()
    manifest.update(
        archive_kind="public projection;17responseenvelopes+2nestedreportcopies token-redacted, notexactoriginalbytes",
        archive_parts=part_rows,
        retained="committedcandidate pendingcoordinatorLANDGO; alltreesretained; no runtime/default/deploy/accountchanges",
        original_protected_custody=report["originals"],
        provider_state_redaction="docs/evals/evidence/089-carbon/provider-state-redaction.json",
        regenerate="Recover publicparts and run carbon_audit.py --public-projection. Exact originals remain externalprotected0700/0600 custody; no inference authorized.",
    )
    (E / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        json.dumps(
            {
                "public_members": 209,
                "redacted_members": 19,
                "parts": 6,
                "public_bytes": len(public),
                "originals_protected": True,
            }
        )
    )


if __name__ == "__main__":
    build()
