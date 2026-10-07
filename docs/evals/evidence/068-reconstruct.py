"""Restore public/synthetic evidence offline into an empty directory; no inference."""

import re
import hashlib
import json
import sys
import tarfile
from pathlib import Path

base = Path(__file__).resolve().parent
manifest = json.loads((base / "068-haiku55-manifest.json").read_text())
archive = base / "068-haiku55-receipts.tar.gz"
assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest["archive"]["sha256"]
verify_only = sys.argv[1] == "--verify-only"
destination = Path(sys.argv[1]).resolve()
if not verify_only:
    destination.mkdir(parents=True, exist_ok=True)
if not verify_only and any(destination.iterdir()):
    raise RuntimeError("Refuse a nonempty destination")
with tarfile.open(archive, "r:gz") as tar:
    for entry in manifest["members"]:
        name = entry["path"]
        target = (destination / name).resolve()
        assert target.is_relative_to(destination)
        member = tar.getmember("templates/" + name)
        assert member.isfile()
        raw = tar.extractfile(member).read()
        assert hashlib.sha256(raw).hexdigest() == entry["template_sha256"]

        def restore(match):
            identity = match.group(1).decode()
            value = tar.extractfile("blobs/" + identity).read()
            assert hashlib.sha256(value).hexdigest() == identity
            return value

        raw = re.sub(rb"__HAIKU55_BLOB_([a-f0-9]{64})__", restore, raw)
        assert len(raw) == entry["bytes"]
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"]
        if not verify_only:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
print(f"Verified {len(manifest['members'])} exact files; restored={not verify_only}")
