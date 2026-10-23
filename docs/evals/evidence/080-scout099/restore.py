"""Restore exact public/synthetic receipts offline; no inference or credentials."""
from pathlib import Path
import hashlib
import json
import re
import sys
import tarfile

base = Path(__file__).resolve().parent
manifest = json.loads((base / 'manifest.json').read_text())
archive = base / manifest['archive']
assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest['sha256']
destination = Path(sys.argv[1]).resolve()
with tarfile.open(archive) as source:
    blobs = {d: source.extractfile('blobs/' + d).read() for d in manifest['blob_hashes']}
    for entry in manifest['members']:
        raw = source.extractfile('templates/' + entry['path']).read()
        assert hashlib.sha256(raw).hexdigest() == entry['template_sha256']
        raw = re.sub(rb'@DOCWEB080_BLOB:([0-9a-f]{64})@', lambda match: blobs[match[1].decode()], raw)
        assert hashlib.sha256(raw).hexdigest() == entry['sha256'] and len(raw) == entry['bytes']
        target = destination / entry['path']
        assert target.is_relative_to(destination) and not target.exists()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
print('Verified and restored', len(manifest['members']), 'exact files')
