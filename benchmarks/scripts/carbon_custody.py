"""Seal public/synthetic owner evidence; raw bodies contain no credential headers."""

import hashlib
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / "docs/evals/evidence/089-carbon"
R = ROOT / "benchmarks/results/carbon-20261110"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    archive = E.parent / "089-carbon-custody.tar.gz"
    assert not archive.exists() and not list(
        E.parent.glob("089-carbon-custody.tar.gz.part*")
    )
    files = []
    for directory in [R, E] + [
        ROOT / f"output/runs/carbon-ocr-barney-{arm}-20261110"
        for arm in ["candidate", "control"]
    ]:
        for path in directory.rglob("*"):
            if (
                not path.is_file()
                or "__pycache__" in path.parts
                or path.suffix == ".pyc"
                or path.name.endswith(".lock")
            ):
                continue
            if directory == E and (
                path.name.startswith(("request-", "response-"))
                or "rendered" in path.relative_to(E).parts
                or path.name in ["manifest.json", "custody-index.json"]
            ):
                continue
            files.append(path)
    files = sorted(set(files))
    entries = []
    with tarfile.open(archive, "w:gz", compresslevel=6) as tar:
        for path in files:
            relative = str(path.relative_to(ROOT))
            data = path.read_bytes()
            entries.append(
                {
                    "path": relative,
                    "bytes": len(data),
                    "sha256": sha(data),
                    "privacy": "public/authored-synthetic evidence; no credential headers",
                }
            )
            tar.add(path, arcname=relative, recursive=False)
    expected = {r["path"]: r for r in entries}
    with tarfile.open(archive, "r:gz") as tar:
        members = [m for m in tar.getmembers() if m.isfile()]
        assert {m.name for m in members} == set(expected)
        for member in members:
            data = tar.extractfile(member).read()
            assert (
                len(data) == expected[member.name]["bytes"]
                and sha(data) == expected[member.name]["sha256"]
            )
    data = archive.read_bytes()
    pieces = []
    for number, start in enumerate(range(0, len(data), 8 * 1024 * 1024), 1):
        part = archive.with_name(archive.name + f".part{number:02}")
        part.write_bytes(data[start : start + 8 * 1024 * 1024])
        pieces.append(
            {
                "path": str(part.relative_to(ROOT)),
                "bytes": part.stat().st_size,
                "sha256": sha(part.read_bytes()),
            }
        )
    assert b"".join((ROOT / r["path"]).read_bytes() for r in pieces) == data
    archive.unlink()  # Task-owned transient monolith; verified identical sealed parts remain.
    ledger = json.loads((E / "ledger.json").read_text())
    regenerable = []
    for row in json.loads((E / "preflight.json").read_text())["matrix"]:
        call = next(c for c in ledger["calls"] if c["stage"] == row["stage"])
        body = json.loads((ROOT / call["request"]).read_text())
        planned = json.loads((ROOT / row["request_path"]).read_text())
        assert body == planned
        canonical = json.dumps(
            body, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
        regenerable.append(
            {
                "rendered": row["request_path"],
                "original_rendered_lexical_sha256": row["request_sha256"],
                "semantic_sha256": sha(canonical),
                "from_wire": call["request"],
                "method": "Parse exact wire JSON: semantic body equals original; pretty whitespace/object-key order may differ. Arrays/source/prompt exact.",
            }
        )
    index = {
        "archive_sha256": sha(data),
        "archive_bytes": len(data),
        "parts": pieces,
        "files": entries,
        "regenerable_rendered_cases": regenerable,
        "verified": "all archived member hashes/sizes verified by reading the sealed tar; all part bytes reassembled identically; rendered JSON semantic equality verified",
        "excluded": "duplicate E request/response copies omitted; rendered semantic objects reconstruct from exact archived wire, pretty whitespace/object-key order may differ; regenerable Python bytecode and lock files not archived; all originals retained in worktree",
        "recovery": "From an empty approved destination, concatenate parts in lexical order and tar -xz -C DESTINATION. Restore entries by owner-relative paths; preserve existing files before restore.",
    }
    (E / "custody-index.json").write_text(json.dumps(index, indent=2) + "\n")
    manifest = {
        "base_sha": "1c3f3e31158ec753e057e79839f438d021500214",
        "worktree": str(ROOT),
        "branch": "codex/carbon-20261110-doc-web",
        "owner": "DocWeb / Story267 / Scout109item3",
        "retained": "uncommitted for review; no cleanup/commit/push/default/deploy/accountchange",
        "archive_parts": pieces,
        "custody_index": "docs/evals/evidence/089-carbon/custody-index.json",
        "raw_requests": 24,
        "raw_responses": 24,
        "actual_driver_runs": [
            f"output/runs/carbon-ocr-barney-{a}-20261110"
            for a in ["candidate", "control"]
        ],
        "producing_sources": "provenance.json plus archived producing-sources*,dispatch-code,pre-format-sources; final-sources explicitly postinference",
        "regenerate": "Inference is closed; use sealed parts for offline recovery. A live rerun requires new approved run identity/budget, owner wrapper, original preflight/matrix and same eligibility; never replay this closed wallet. Offline audit: python benchmarks/scripts/carbon_audit.py after restore.",
    }
    (E / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        json.dumps(
            {
                "files": len(entries),
                "archive_bytes": len(data),
                "parts": len(pieces),
                "verified": True,
            }
        )
    )


if __name__ == "__main__":
    main()
