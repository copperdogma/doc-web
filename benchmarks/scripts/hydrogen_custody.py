"""Seal protected native originals and verify retained request/response custody."""

import hashlib
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / "docs/evals/evidence/094-hydrogen"
R = ROOT / "benchmarks/results/hydrogen-20261115"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ledger = json.loads((R / "ledger.json").read_text())
    plan = {
        r["stage"]: r for r in json.loads((E / "preflight.json").read_text())["matrix"]
    }
    audited = []
    for call in ledger["calls"]:
        request = ROOT / call["request"]
        response = ROOT / call["response"]
        if call["stage"].endswith("misrouted-infrastructure"):
            assert (
                json.loads(response.read_text())["error"]["code"] == "model_not_found"
            )
            assert call["reserved_usd"] == 0.31476 and call["cost_usd"] is None
        else:
            assert digest(request) == call["request_sha256"]
            assert digest(response) == call["response_sha256"]
            row = plan[call["stage"]]
            assert json.loads(request.read_text()) == json.loads(
                (ROOT / row["request_path"]).read_text()
            )
            assert call["served_model"] == call["model"]
            assert call["cost_usd"] is not None and not call.get("bound_violation")
        audited.append(
            {
                "stage": call["stage"],
                "request_sha256": digest(request),
                "response_sha256": digest(response),
                "cost_usd": call.get("cost_usd"),
            }
        )
    assert (
        ledger["closed"]
        and len(audited) == 14
        and not any(x.get("in_flight") for x in ledger["calls"])
    )
    (E / "native-custody-audit.json").write_text(
        json.dumps(
            {
                "calls": audited,
                "wire_matrix_parity": True,
                "provider_calls": 0,
                "complete_originals_protected": True,
            },
            indent=2,
        )
        + "\n"
    )
    files = [p for p in R.rglob("*") if p.is_file() and "__pycache__" not in str(p)]
    for run in (ROOT / "output/runs").glob("hydrogen*"):
        files += [p for p in run.rglob("*") if p.is_file()]
    fixture = ROOT / "output/fixtures/hydrogen-detector-094-runtime"
    files += [
        p
        for p in fixture.rglob("*")
        if p.is_file() and "paddle-cache" not in str(p) and "__pycache__" not in str(p)
    ]
    files = sorted(set(files))
    for p in R.rglob("*"):
        p.chmod(0o700 if p.is_dir() else 0o600)
    R.chmod(0o700)
    archive_dir = ROOT / "output/eval-custody/hydrogen-094"
    archive_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    archive = archive_dir / "native-originals.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        for p in files:
            tar.add(p, arcname=str(p.relative_to(ROOT)), recursive=False)
    archive.chmod(0o600)
    records = [
        {
            "path": str(p.relative_to(ROOT)),
            "sha256": digest(p),
            "bytes": p.stat().st_size,
        }
        for p in files
    ]
    source_files = [
        ROOT / "modules/common/google_client.py",
        ROOT / "configs/pricing.default.yaml",
        *ROOT.glob("benchmarks/scripts/hydrogen*.py"),
        ROOT / "benchmarks/providers/hydrogen_guard.py",
        ROOT / "tools/hydrogen_detector_094_runtime.py",
        ROOT / "tests/test_google_client.py",
        *ROOT.glob("configs/recipes/hydrogen-ocr-*.yaml"),
    ]
    manifest = {
        "scope": "protected originals including provider state; manifest is safe paths/hashes/sizes only",
        "originals": records,
        "archive": {
            "path": str(archive.relative_to(ROOT)),
            "sha256": digest(archive),
            "bytes": archive.stat().st_size,
            "mode": "0600 parent0700",
        },
        "recovery": "Verify archive hash, then tar -xzf native-originals.tar.gz in a new protected owner recovery directory. Do not publish provider state or overwrite originals. Reconstruct public source images from exact saved wire inlineData if necessary. Existing retained worktree is authoritative.",
        "final_code_epoch": [
            {
                "path": str(p.relative_to(ROOT)),
                "sha256": digest(p),
                "bytes": p.stat().st_size,
            }
            for p in sorted(set(source_files))
        ],
        "producer_epochs": "Original dispatch guard sources saved under dispatch-code before each valid live request. Exact original wire/native receipts authoritative; final formatting/accounting/recipe additions are later epochs, not retroactively producer claims.",
        "layout_weights": {
            "path": str(
                fixture
                / "paddle-cache/official_models/PP-DocLayout_plus-L/inference.pdiparams"
            ),
            "sha256": digest(
                fixture
                / "paddle-cache/official_models/PP-DocLayout_plus-L/inference.pdiparams"
            ),
            "retention": "local checked weights; not duplicated in archive",
        },
        "privacy": "public Onward/public LOC/authored synthetic only; raw provider state remains protected; no keys/headers recorded",
        "no_new_provider_calls": True,
    }
    (E / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        "Verified",
        len(audited),
        "original POST pairs;",
        len(records),
        "protected files sealed;",
        archive.stat().st_size,
        "archive bytes",
    )


if __name__ == "__main__":
    main()
