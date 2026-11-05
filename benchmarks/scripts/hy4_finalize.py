"""Seal completed Hy4 evidence offline; never dispatch inference."""

import hashlib
import json
import shutil
import statistics
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / "docs/evals/evidence/086-hy4"
R = ROOT / "benchmarks/results/hy4-20261105"


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def identity(path):
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def main():
    ledger = json.loads((R / "ledger.json").read_text())
    calls = ledger["calls"]
    assert all(c.get("cost_usd") is not None for c in calls), "inflight/unknown"
    assert abs(sum(c["cost_usd"] for c in calls) - ledger["spent_usd"]) < 1e-10
    assert ledger["spent_usd"] <= ledger["cap_usd"] == 5
    for c in calls:
        for kind in ("request", "response"):
            assert identity(ROOT / c[kind])["sha256"] == c[kind + "_sha256"]
    preflight = json.loads((E / "safety-preflight.json").read_text())
    rows = []
    for case in preflight["cases"]:
        p = E / ("safety-" + case["key"] + ".json")
        if p.exists():
            rr = json.loads(p.read_text())
            assert {r["arm"] for r in rr} == {"candidate", "control"}
            rows.extend(rr)
    candidate = [r for r in rows if r["arm"] == "candidate"]
    assert candidate
    failures = [r for r in candidate if not r.get("correct", False)]
    assert failures or len(candidate) == 22, "no decisive stop/full matrix"
    ledger.setdefault("prior_stop_reason", ledger.get("stop_reason"))
    ledger["stop_reason"] = (
        "First valid candidate safety/source-contract failure"
        if failures
        else "Completed selected 22-case maintained safety matrix"
    )
    ledger["closed"] = True
    save(R / "ledger.json", ledger)
    save(E / "ledger.json", ledger)
    save(E / "safety-results-all.json", rows)
    summary = {
        "base_sha": "5622d996961669b5254ff03a82b609a6fb3cf834",
        "branch": "codex/hy4-20261105-doc-web",
        "worktree": str(ROOT),
        "cap_usd": 5,
        "spent_usd": ledger["spent_usd"],
        "unknown_exposure_usd": 0,
        "dispatches": len(calls),
        "judge_cost_usd": 0,
        "safety": {},
        "table": {
            "candidate_exact": 22,
            "control_exact": 23,
            "cells": 23,
            "clear_holds": 4,
            "accepted_wrong_cells": 0,
        },
        "crop": {
            "cases": 1,
            "candidate_score": 0.9635,
            "control_score": 0.9854,
            "full_source_preservation": False,
            "clipped_integral_rows": 2,
            "coordinate_oracle": "unchanged golden-assisted axis selection",
        },
        "ocr": {
            "candidate_ratio": 0.852211,
            "threshold": 0.99,
            "control_requested": "gemini-3.7-flash",
            "control_served": "gemini-3.8-flash",
            "control_quarantined": True,
            "fresh_relative_claim": False,
        },
        "credential_custody": "Existing owner wrapper, no key copy/injection/change",
        "scope_holds": [
            "Safety verdict benchmark does not qualify full reason/flags semantics",
            "Attempt081 native source-size, identity and geometry admission gaps persist",
            "No production consumer/source-deletion/default qualification",
            "Crop golden-assisted geometry is not raw runtime coordinate parity",
            "OCR eval-only adapter is not production provider integration",
        ],
    }
    for arm in ("candidate", "control"):
        rr = [r for r in rows if r["arm"] == arm]
        cc = [
            c
            for c in calls
            if c["stage"].startswith("safety-") and c["stage"].endswith("-" + arm)
        ]
        assert len(rr) == len(cc)
        summary["safety"][arm] = {
            "cases": len(rr),
            "correct": sum(r.get("correct", False) for r in rr),
            "false_safe": sum(r.get("false_safe", False) for r in rr),
            "errors": sum("error" in r for r in rr),
            "cost_usd": sum(c["cost_usd"] for c in cc),
            "native_http_mean_ms": statistics.mean(c["latency_ms"] for c in cc),
            "native_http_median_ms": statistics.median(c["latency_ms"] for c in cc),
            "native_http_sum_ms": sum(c["latency_ms"] for c in cc),
        }
    for label in ("native", "table", "crop", "ocr", "safety"):
        cc = [c for c in calls if c["stage"].startswith(label + "-")]
        summary[label + "_cost_usd"] = sum(c["cost_usd"] for c in cc)
    summary["candidate_subject_cost_usd"] = sum(
        c["cost_usd"]
        for c in calls
        if c["model"] == "tencent/hy4" and not c["stage"].startswith("native-")
    )
    summary["control_subject_cost_usd"] = sum(
        c["cost_usd"] for c in calls if c["model"] != "tencent/hy4"
    )
    summary["quarantined_control_cost_usd"] = 0.02286675
    save(E / "summary.json", summary)

    frozen = json.loads((E / "producing-sources.json").read_text())
    extra = [
        "benchmarks/scripts/hy4_overlay.py",
        "benchmarks/scripts/hy4_finalize.py",
        "benchmarks/scripts/scout096_safety.py",
        "benchmarks/jev-consistency/decisions_campaign.py",
        "benchmarks/prompts/validate-page-level-crop.js",
        "benchmarks/providers/openai_responses_model.py",
        "benchmarks/tasks/safety-repair-048-control-full-continuation1.yaml",
        "configs/recipes/hy4-ocr-candidate-barney.yaml",
        "configs/recipes/hy4-ocr-control-barney.yaml",
        "tests/test_hy4_campaign.py",
    ]
    sources = {}
    for name in sorted(set(frozen) | set(extra)):
        src = ROOT / name
        dst = E / "source-snapshots" / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        sources[name] = identity(src)
        if name in frozen:
            sources[name]["prior_recorded_identity"] = frozen[name]
            sources[name]["matches_prior_record"] = (
                sources[name]["sha256"] == frozen[name]["sha256"]
            )
    save(E / "final-source-identities.json", sources)
    archive = E / "native-evidence.tar.gz"
    paths = sorted(
        p
        for folder in [
            R,
            ROOT / "output/runs/hy4-ocr-barney-candidate-20261105",
            ROOT / "output/runs/hy4-ocr-barney-control-20261105",
        ]
        for p in folder.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.name != "ledger.lock"
    )
    members = []
    with tarfile.open(archive, "w:gz") as tar:
        for p in paths:
            rel = str(p.relative_to(ROOT))
            tar.add(p, arcname=rel)
            members.append({"path": rel, **identity(p)})
    with tarfile.open(archive, "r:gz") as tar:
        for entry in members:
            raw = tar.extractfile(entry["path"]).read()
            assert len(raw) == entry["bytes"]
            assert hashlib.sha256(raw).hexdigest() == entry["sha256"]
    manifest = {
        "archive": str(archive.relative_to(ROOT)),
        **identity(archive),
        "members": members,
        "evidence_files": [
            {"path": str(p.relative_to(ROOT)), **identity(p)}
            for p in sorted(E.rglob("*"))
            if p.is_file() and p.name not in ("manifest.json", "native-evidence.tar.gz")
        ],
        "privacy": "public and authored synthetic only",
        "regeneration": "Offline: python benchmarks/scripts/hy4_finalize.py. Closed ledger denies inference; paid reproduction requires new authorization and campaign identity.",
    }
    save(E / "manifest.json", manifest)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
