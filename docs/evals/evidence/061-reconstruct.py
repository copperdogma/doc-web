"""Restore exact Attempt061 public receipts offline; no credentials/provider calls."""

import hashlib
import json
from pathlib import Path
import sys
import tarfile

base = Path(__file__).resolve().parent
manifest = json.loads((base / "061-mistral4-manifest.json").read_text())
archive = base / Path(manifest["archive"]["path"]).name
assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest["archive"]["sha256"]
destination = Path(sys.argv[1]).resolve()
destination.mkdir(parents=True, exist_ok=True)
with tarfile.open(archive) as source:
    blobs = {
        digest: source.extractfile("blobs/" + digest).read()
        for digest in manifest["archive"]["blob_hashes"]
    }
    assert all(
        hashlib.sha256(raw).hexdigest() == digest for digest, raw in blobs.items()
    )
    for item in manifest["artifacts"]:
        name = item["path"]
        assert not Path(name).is_absolute() and ".." not in Path(name).parts
        raw = source.extractfile("artifacts/" + name).read()
        assert hashlib.sha256(raw).hexdigest() == item["template_sha256"]
        for digest, value in blobs.items():
            raw = raw.replace(("@DOCWEB061_IMAGE:" + digest + "@").encode(), value)
        assert (
            len(raw) == item["bytes"]
            and hashlib.sha256(raw).hexdigest() == item["sha256"]
        )
        out = destination / name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(raw)
        out.chmod(0o600)
print(
    "Restored and verified",
    len(manifest["artifacts"]),
    "exact files; no provider calls",
)
