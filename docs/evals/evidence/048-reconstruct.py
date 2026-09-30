"""Offline lossless receipt reconstruction; no inference or credentials."""
import hashlib
import json
import sys
import tarfile
from pathlib import Path
base = Path(__file__).resolve().parent
manifest = json.loads((base / "048-safety-repair-manifest.json").read_text())
destination = Path(sys.argv[1]).resolve()
archive = base / Path(manifest["archive"]["path"]).name
assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest["archive"]["sha256"]
with tarfile.open(archive) as source:
    blobs = {h: source.extractfile("blobs/" + h).read() for h in manifest["archive"]["blob_hashes"]}
    for entry in manifest["files"]:
        raw = source.extractfile("artifacts/" + entry["path"]).read()
        for digest, image in blobs.items():
            raw = raw.replace(("@DOCWEB_PUBLIC_IMAGE:" + digest + "@").encode(), image)
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"]
        path = destination / entry["path"]
        assert path.is_relative_to(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
print("Verified and restored", len(manifest["files"]), "exact files")
