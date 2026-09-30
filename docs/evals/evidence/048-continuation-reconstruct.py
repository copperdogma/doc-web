"""Restore exact public receipts offline; no provider access or credentials."""

import hashlib
import json
import sys
import tarfile
from pathlib import Path

base = Path(__file__).resolve().parent
root = base.parents[2]
m = json.loads((base / "048-continuation-manifest.json").read_text())
archive = base / Path(m["archive"]["path"]).name
assert hashlib.sha256(archive.read_bytes()).hexdigest() == m["archive"]["sha256"]
destination = Path(sys.argv[1]).resolve()
images = {}
for h, reference in m["canonical_image_uri_references"].items():
    path = (root / reference["path"]).resolve()
    assert path.is_relative_to(root)
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == reference["file_sha256"]
    uri = raw.strip()
    assert hashlib.sha256(uri).hexdigest() == h
    images[h] = uri
with tarfile.open(archive) as source:
    for h in m["archive"]["blob_hashes"]:
        images[h] = source.extractfile("blobs/" + h).read()
        assert hashlib.sha256(images[h]).hexdigest() == h
    for entry in m["continuation_files"]:
        raw = source.extractfile("artifacts/" + entry["path"]).read()
        for h, uri in images.items():
            raw = raw.replace(("@DOCWEB_PUBLIC_IMAGE:" + h + "@").encode(), uri)
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"]
        path = destination / entry["path"]
        assert path.is_relative_to(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
print("Verified and restored", len(m["continuation_files"]), "exact continuation files")
