"""Losslessly restore campaign receipts offline; no credentials or inference."""

import argparse
import hashlib
import json
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def restore(value):
    if isinstance(value, dict):
        if set(value) == {"$uri_fixture"}:
            return (ROOT / value["$uri_fixture"]).read_text().strip()
        return {k: restore(v) for k, v in value.items()}
    if isinstance(value, list):
        return [restore(v) for v in value]
    return value


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    manifest = json.loads((HERE / "receipt-manifest.json").read_text())
    for row in manifest["fixture_uris"]:
        assert (
            hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
            == row["sha256"]
        )
    a.output.mkdir(parents=True, exist_ok=True)
    with tarfile.open(HERE / "receipts.tar.gz", "r:gz") as archive:
        for row in manifest["receipts"]:
            member = archive.getmember(row["archive_member"])
            data = archive.extractfile(member).read()
            if row["kind"] == "request-reference":
                data = json.dumps(
                    restore(json.loads(data)), ensure_ascii=False
                ).encode()
            assert len(data) == row["bytes"]
            assert hashlib.sha256(data).hexdigest() == row["sha256"]
            target = a.output / Path(row["name"]).name
            if target.exists() and target.read_bytes() != data:
                raise RuntimeError(
                    "Refusing to overwrite different receipt: " + str(target)
                )
            target.write_bytes(data)
    print(
        json.dumps(
            {
                "restored_verified_receipts": len(manifest["receipts"]),
                "output": str(a.output),
            }
        )
    )


if __name__ == "__main__":
    main()
