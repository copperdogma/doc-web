"""Package public/synthetic receipts, deduplicating original fixture URI strings."""

import hashlib
import io
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RAW = ROOT / "benchmarks/results/scout091-20261013"
manifest = {"receipts": [], "fixture_uris": []}
uris = {}
for r in json.loads((HERE / "image-eligibility.json").read_text())["bindings"]:
    for s in r["sources"]:
        p = ROOT / s["path"]
        uris[p.read_text().strip()] = s["path"]
for uri, path in uris.items():
    p = ROOT / path
    manifest["fixture_uris"].append(
        {"path": path, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
    )


def refs(v):
    if isinstance(v, str) and v in uris:
        return {"$uri_fixture": uris[v]}
    if isinstance(v, dict):
        return {k: refs(x) for k, x in v.items()}
    if isinstance(v, list):
        return [refs(x) for x in v]
    return v


with tarfile.open(HERE / "receipts.tar.gz", "w:gz") as archive:
    for p in sorted(RAW.glob("*.json")):
        data = p.read_bytes()
        kind = "raw"
        if p.name.endswith(".request.json"):
            packaged = json.dumps(refs(json.loads(data)), ensure_ascii=False).encode()
            kind = "request-reference"
        else:
            packaged = data
        info = tarfile.TarInfo(p.name)
        info.size = len(packaged)
        archive.addfile(info, io.BytesIO(packaged))
        manifest["receipts"].append(
            {
                "name": p.name,
                "archive_member": p.name,
                "kind": kind,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
(HERE / "receipt-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(
    json.dumps(
        {
            "receipt_count": len(manifest["receipts"]),
            "archive_bytes": (HERE / "receipts.tar.gz").stat().st_size,
        }
    )
)
