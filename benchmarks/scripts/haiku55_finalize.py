"""Offline receipt verification, archive and safe owner summary. No inference."""

import io
import re
import hashlib
import json
import statistics
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / "benchmarks/results/haiku55-20261007"
E = ROOT / "docs/evals/evidence"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    ledger = json.loads((R / "ledger.json").read_text())
    calls = ledger["calls"]
    assert len(calls) == 110
    ids = [c["response_id"] for c in calls if c.get("response_id")]
    assert len(ids) == len(set(ids)) == 109
    assert abs(sum(c.get("cost_usd") or 0 for c in calls) - ledger["spent_usd"]) < 1e-10
    for c in calls:
        for kind in ["request", "response"]:
            assert (
                sha((R / f"{kind}-{c['sequence']:03d}.json").read_bytes())
                == c[kind + "_sha256"]
            )
    ledger["closed"] = True
    ledger["stop_reason"] = (
        "Predeclared progressive decisions reached; no more inference authorized by this run identity"
    )
    (R / "ledger.json").write_text(json.dumps(ledger, indent=2) + "\n")
    summary = {}
    for f in sorted(R.glob("*calibration.json")):
        if f.name.startswith("ocr"):
            continue
        d = json.loads(f.read_text())
        summary[f.stem] = [
            {
                "vars": x["vars"],
                "success": x["success"],
                "score": x.get("score"),
                "error": x.get("error"),
                "response": x.get("response"),
            }
            for x in d["results"]["results"]
        ]
    for arm in ["medium", "low", "high", "control"]:
        summary["ocr-" + arm] = json.loads((R / f"ocr-{arm}-score.json").read_text())
    summary["consistency"] = json.loads((R / "consistency-summary.json").read_text())
    stage = {}
    for s in sorted(set(c["stage"] for c in calls)):
        cs = [c for c in calls if c["stage"] == s]
        lat = [c["latency_ms"] for c in cs if c.get("cost_usd") is not None]
        stage[s] = {
            "calls": len(cs),
            "settled_usd": sum(c.get("cost_usd") or 0 for c in cs),
            "unknown_reserved_usd": sum(
                c["reserved_usd"] for c in cs if c.get("cost_usd") is None
            ),
            "median_ms": statistics.median(lat) if lat else None,
        }
    files = [
        p
        for p in R.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.name != "dispatch.lock"
    ]
    for run in sorted((ROOT / "output/runs").glob("haiku55-ocr-*")):
        files.extend(
            p for p in run.rglob("*") if p.is_file() and "__pycache__" not in p.parts
        )
    entries = []
    blobs = {}
    templates = {}
    token = re.compile(rb"[A-Za-z0-9+/_=-]{512,}")
    for p in files:
        raw = p.read_bytes()
        assert b"sk-ant-api" not in raw and b"sk-proj-" not in raw

        def replace(match):
            data = match.group(0)
            identity = sha(data)
            blobs[identity] = data
            return ("__HAIKU55_BLOB_" + identity + "__").encode()

        template = token.sub(replace, raw)
        name = str(p.relative_to(ROOT))
        templates[name] = template
        entries.append(
            {
                "path": name,
                "sha256": sha(raw),
                "bytes": len(raw),
                "template_sha256": sha(template),
                "classification": "public/synthetic evaluation or code; no secrets",
            }
        )
    archive = E / "068-haiku55-receipts.tar.gz"
    with tarfile.open(archive, "w:gz") as t:
        for name, data in [("templates/" + k, v) for k, v in templates.items()] + [
            ("blobs/" + k, v) for k, v in blobs.items()
        ]:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o600
            t.addfile(info, io.BytesIO(data))
    manifest = {
        "attempt": "068",
        "date": "2026-10-07",
        "base_sha": "cff6771a01ba202b8eb39e13a604a932708e2278",
        "branch": "codex/haiku55-eval-20261007",
        "model": "claude-haiku-5-5",
        "route": "direct api.anthropic.com Messages",
        "cap_usd": 10,
        "settled_usd": ledger["spent_usd"],
        "unknown_reserved_usd": sum(
            c["reserved_usd"] for c in calls if c.get("cost_usd") is None
        ),
        "calls": calls,
        "stage_metrics": stage,
        "outcomes": summary,
        "archive": {
            "path": str(archive.relative_to(ROOT)),
            "sha256": sha(archive.read_bytes()),
            "bytes": archive.stat().st_size,
        },
        "members": entries,
        "paid_source": "benchmarks/results/haiku55-20261007/paid-source-manifest.json",
        "commands": [
            "DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/doc-web/.env python scripts/run_with_doc_web_env.py python benchmarks/scripts/haiku55_native_probe.py",
            "DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/doc-web/.env python scripts/run_with_doc_web_env.py python benchmarks/scripts/haiku55_calibration.py",
            "DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/doc-web/.env python scripts/run_with_doc_web_env.py python benchmarks/scripts/haiku55_ocr_calibration.py",
            "DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/doc-web/.env python scripts/run_with_doc_web_env.py python benchmarks/scripts/haiku55_consistency.py",
        ],
        "credential_cleanup": "No injection/copy; owner .env unchanged",
        "limits": "Calibration firstfive omits mixed/uncertain; selection exploratory; no fresh Jev/fallback, full13/22 or Alverson; no runtime default/promotion change",
    }
    (E / "068-haiku55-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        json.dumps(
            {k: manifest[k] for k in ["settled_usd", "unknown_reserved_usd", "archive"]}
        )
    )


if __name__ == "__main__":
    main()
