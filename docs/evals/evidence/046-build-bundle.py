"""Pack exact public GPT-6.1 eval receipts with deduplicated image strings."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import re
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEST = Path(__file__).resolve().parent
RESULTS = ROOT / "benchmarks/results/gpt61-sol-20260929"
SOURCE_PATHS = sorted(p for p in RESULTS.rglob("*") if p.is_file())
for run in sorted((ROOT / "output/runs").glob("gpt61-*")):
    SOURCE_PATHS += sorted(p for p in run.rglob("*") if p.is_file())
SOURCE_PATHS.append(DEST / "046-gpt61-topology.json")
TOKEN = b"__DOCWEB046_B64_"
PATTERNS = [
    re.compile(rb"data:image/[A-Za-z0-9.+-]+;base64,[A-Za-z0-9+/_=-]{1024,}"),
    re.compile(rb'(?<="data":")[A-Za-z0-9+/_=-]{1024,}(?=")'),
    re.compile(rb'(?<="data": ")[A-Za-z0-9+/_=-]{1024,}(?=")'),
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main():
    blobs = {}
    entries = {}
    templates = {}
    for path in SOURCE_PATHS:
        name = str(path.relative_to(ROOT))
        original = path.read_bytes()
        if any(
            secret in original
            for secret in (b"Authorization", b"x-goog-api-key", b"Bearer ", b"sk-proj-")
        ):
            raise ValueError("Potential credential material in " + name)
        template = original
        if path.suffix in {".json", ".jsonl"}:

            def replace(match):
                value = match.group(0)
                key = digest(value)
                blobs[key] = value
                return TOKEN + key.encode() + b"__"

            for pattern in PATTERNS:
                template = pattern.sub(replace, template)
        entries[name] = {
            "bytes": len(original),
            "sha256": digest(original),
            "template_sha256": digest(template),
            "template_bytes": len(template),
        }
        templates[name] = template
    index = {
        "format": "docweb046-deduplicated-public-receipts",
        "base_sha": "5ca3711fb13b12b5b3e261438e7a00ffe450a647",
        "entry_count": len(entries),
        "blob_count": len(blobs),
        "entries": entries,
    }
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb", mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode="w") as tar:
            members = {
                "ATTEMPT046-BUNDLE-INDEX.json": json.dumps(index, indent=2).encode()
                + b"\n"
            }
            members.update(
                {"templates/" + name: data for name, data in templates.items()}
            )
            members.update({"blobs/" + key: data for key, data in blobs.items()})
            for name, data in sorted(members.items()):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o600
                tar.addfile(info, io.BytesIO(data))
    archive = buffer.getvalue()
    parts = []
    chunk = 45 * 1024 * 1024
    for i, start in enumerate(range(0, len(archive), chunk), 1):
        data = archive[start : start + chunk]
        path = DEST / f"046-reproducibility.tar.gz.part{i:02d}"
        path.write_bytes(data)
        parts.append(
            {
                "path": str(path.relative_to(ROOT)),
                "bytes": len(data),
                "sha256": digest(data),
            }
        )
    receipt = {
        "archive_sha256": digest(archive),
        "archive_bytes": len(archive),
        "parts": parts,
        "entries": len(entries),
        "blobs": len(blobs),
    }
    (DEST / "046-reproducibility-index.json").write_text(
        json.dumps(receipt, indent=2) + "\n"
    )
    print(
        json.dumps(
            {
                "archive_bytes": len(archive),
                "parts": len(parts),
                "entries": len(entries),
                "blobs": len(blobs),
            }
        )
    )


if __name__ == "__main__":
    main()
