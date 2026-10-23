"""Offline durable custody and inclusive cost summary. Never makes provider calls."""

import hashlib
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / "benchmarks/results/scout097-20261017"
E = ROOT / "docs/evals/evidence/079-scout097"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def seal():
    ledger = json.loads((R / "ledger.json").read_text())
    # Seal only once the operator has completed source review and stopped dispatch.
    assert (E / "campaign-complete.json").exists()
    ledger["closed"] = True
    save(R / "ledger.json", ledger)
    save(E / "ledger.json", ledger)
    calls = ledger["calls"]
    assert abs(sum(c.get("cost_usd") or 0 for c in calls) - ledger["spent_usd"]) < 1e-10
    unknown = sum(c["reserved_usd"] for c in calls if c.get("cost_usd") is None)
    groups = {
        "qualification": [],
        "candidate_subjects": [],
        "valid_controls": [],
        "quarantined_controls": [],
    }
    for call in calls:
        if call["stage"].startswith("native-"):
            group = "qualification"
        elif call["stage"] == "ocr-barney-control":
            group = "quarantined_controls"
        elif call["stage"].endswith("candidate"):
            group = "candidate_subjects"
        else:
            group = "valid_controls"
        groups[group].append(call)
    summary = {
        "cap_usd": 15,
        "settled_usd": ledger["spent_usd"],
        "unknown_reserved_usd": unknown,
        "conservative_exposure_usd": ledger["spent_usd"] + unknown,
        "calls": len(calls),
        "groups": {
            k: {
                "calls": len(v),
                "settled_usd": sum(c.get("cost_usd") or 0 for c in v),
                "latency_sum_ms": sum(c.get("latency_ms", 0) for c in v),
            }
            for k, v in groups.items()
        },
        "credentials": "existing owner variables preserved; no injection/copy/temporary credential created; cleanup not applicable",
        "billing": "native usage estimates/router reported cost; not provider invoices",
        "queue": "HTTP latency excludes shared global lock queue",
        "no_defaults_or_paid_judge": True,
    }
    assert summary["conservative_exposure_usd"] <= 15
    save(E / "summary.json", summary)
    files = sorted(
        p
        for p in R.rglob("*")
        if p.is_file() and p.suffix != ".lock" and "__pycache__" not in p.parts
    )
    for name in [
        "scout097-ocr-barney-candidate-20261017",
        "scout097-ocr-barney-control-20261017",
    ]:
        files += sorted(
            p for p in (ROOT / "output/runs" / name).rglob("*") if p.is_file()
        )
    paths = json.loads((E / "current-sources.json").read_text())
    source_files = [ROOT / p for p in paths if isinstance(paths[p], dict)]
    source_files += [
        Path(__file__),
        ROOT / "configs/recipes/scout097-ocr-candidate-barney.yaml",
        ROOT / "configs/recipes/scout097-ocr-control-barney.yaml",
    ]
    sources = {
        str(p.relative_to(ROOT)): {
            "sha256": sha(p.read_bytes()),
            "bytes": p.stat().st_size,
        }
        for p in source_files
    }
    save(
        E / "current-sources.json",
        {
            "files": sources,
            "provenance_note": "Closeout code includes sourcebarrier, bookkeeping, token-category mapping and formatting after early calls. Preformat sources/bootstrap and exact lossless wire receipts preserve producingepochs. No claim that later code produced earlieroutput.",
        },
    )
    files += source_files
    files = sorted(set(files))
    archive = E / "native-evidence.tar.gz"
    assert not archive.exists(), "sealed archive must not be overwritten"
    with tarfile.open(archive, "w:gz") as tf:
        for p in files:
            tf.add(p, arcname=str(p.relative_to(ROOT)))
    manifest = {
        "archive": archive.name,
        "archive_sha256": sha(archive.read_bytes()),
        "archive_bytes": archive.stat().st_size,
        "base_sha": "bceb2956da594d6a895f0ddad2f38a5d9a3a78e3",
        "files": [
            {
                "path": str(p.relative_to(ROOT)),
                "sha256": sha(p.read_bytes()),
                "bytes": p.stat().st_size,
            }
            for p in files
        ],
        "regeneration": "New authorized run identity required; sealed ledger denies paid replay. See Attempt079 commands; frozen sources and complete requests permit offline parsing/scoring replay.",
        "privacy": "synthetic/public owner-cleared; no authorizationheaders, keys or private sources retained",
    }
    save(E / "manifest.json", manifest)
    with tarfile.open(archive, "r:gz") as tf:
        for row in manifest["files"]:
            assert sha(tf.extractfile(row["path"]).read()) == row["sha256"]
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    seal()
