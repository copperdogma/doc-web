"""Restore exact Attempt063 public receipts offline; no credentials/provider calls."""
import hashlib
import json
from pathlib import Path
import sys
import tarfile

base = Path(__file__).resolve().parent
manifest = json.loads((base / "063-gemini4-argon-manifest.json").read_text())
archive = base / Path(manifest["archive"]["path"]).name
raw_archive = archive.read_bytes()
assert hashlib.sha256(raw_archive).hexdigest() == manifest["archive"]["sha256"]
destination = Path(sys.argv[1]).resolve()
if destination.exists() and any(destination.iterdir()):
    raise SystemExit(f"Destination must be absent or empty: {destination}")
destination.mkdir(parents=True, exist_ok=True)
with tarfile.open(archive) as source:
    blobs = {
        digest: source.extractfile("blobs/" + digest).read()
        for digest in manifest["archive"]["blob_hashes"]
    }
    assert all(hashlib.sha256(value).hexdigest() == digest for digest, value in blobs.items())
    for item in manifest["artifacts"]:
        name = item["path"]
        path = Path(name)
        assert not path.is_absolute() and ".." not in path.parts
        template = source.extractfile("artifacts/" + name).read()
        assert hashlib.sha256(template).hexdigest() == item["template_sha256"]
        raw = template
        for digest, value in blobs.items():
            raw = raw.replace(("@DOCWEB063_IMAGE:" + digest + "@").encode(), value)
        assert len(raw) == item["bytes"]
        assert hashlib.sha256(raw).hexdigest() == item["sha256"]
        out = destination / name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(raw)
        out.chmod(0o600)
print("Restored and verified", len(manifest["artifacts"]), "exact files; no provider calls")
