"""Offline, lossless reconstruction of Attempt 046's deduplicated public receipts."""

import argparse
import hashlib
import io
import json
import tarfile
import tempfile
from pathlib import Path


def reconstruct(parts, destination):
    import re

    token = re.compile(rb"__DOCWEB046_B64_([0-9a-f]{64})__")
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    receipt = json.loads(
        (Path(parts[0]).parent / "046-reproducibility-index.json").read_text()
    )
    if [Path(p).name for p in parts] != [
        Path(p["path"]).name for p in receipt["parts"]
    ]:
        raise ValueError("Bundle parts missing or out of order")
    for part, expected in zip(parts, receipt["parts"]):
        data = Path(part).read_bytes()
        if (
            len(data) != expected["bytes"]
            or hashlib.sha256(data).hexdigest() != expected["sha256"]
        ):
            raise ValueError("Part integrity failure")
    packed = b"".join(Path(p).read_bytes() for p in parts)
    if hashlib.sha256(packed).hexdigest() != receipt["archive_sha256"]:
        raise ValueError("Archive integrity failure")
    with tempfile.TemporaryDirectory(prefix="docweb046-") as temporary:
        root = Path(temporary)
        with tarfile.open(fileobj=io.BytesIO(packed), mode="r:gz") as archive:
            for member in archive.getmembers():
                if (
                    not member.isfile()
                    or Path(member.name).is_absolute()
                    or ".." in Path(member.name).parts
                ):
                    raise ValueError("Unexpected archive member")
                target = root / member.name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.extractfile(member).read())
        index = json.loads((root / "ATTEMPT046-BUNDLE-INDEX.json").read_text())
        blobs = {}

        def replace(match):
            digest = match[1].decode()
            if digest not in blobs:
                data = (root / "blobs" / digest).read_bytes()
                if hashlib.sha256(data).hexdigest() != digest:
                    raise ValueError("Blob integrity failure")
                blobs[digest] = data
            return blobs[digest]

        for name, receipt in index["entries"].items():
            if Path(name).is_absolute() or ".." in Path(name).parts:
                raise ValueError("Unexpected reconstruction path")
            data = (root / "templates" / name).read_bytes()
            if hashlib.sha256(data).hexdigest() != receipt["template_sha256"]:
                raise ValueError("Template integrity failure: " + name)
            original = token.sub(replace, data)
            if (
                len(original) != receipt["bytes"]
                or hashlib.sha256(original).hexdigest() != receipt["sha256"]
            ):
                raise ValueError("Original integrity failure: " + name)
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(original)
            target.chmod(0o600)
    return index


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parts", nargs="+", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    args = parser.parse_args()
    index = reconstruct(args.parts, args.destination)
    print(
        f"Reconstructed and verified {len(index['entries'])} files; no provider calls."
    )
