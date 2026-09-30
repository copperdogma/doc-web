"""Derive the Attempt 046 evidence manifest from exact local artifacts."""

from __future__ import annotations
import hashlib
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEST = Path(__file__).resolve().parent
P = ROOT / "benchmarks/results/gpt61-sol-20260929"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {
        "path": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "sha256": sha(path),
    }


def rows(name):
    return json.loads((P / name).read_text())["results"]["results"]


def summary(name):
    rr = rows(name)
    return {
        "cases": len(rr),
        "passed": sum(bool(r["success"]) for r in rr),
        "mean_score": round(statistics.mean(r["score"] for r in rr), 6),
        "mean_promptfoo_latency_ms": round(
            statistics.mean(r["latencyMs"] for r in rr), 3
        ),
        "cost_usd": round(sum(r.get("cost") or 0 for r in rr), 9),
        "result": ref(P / name),
    }


ledger = json.loads((P / "ledger.json").read_text())
assert (
    ledger["closed"]
    and len(ledger["calls"]) == 36
    and all(c["cost_usd"] is not None for c in ledger["calls"])
)
assert abs(sum(c["cost_usd"] for c in ledger["calls"]) - ledger["spent_usd"]) < 1e-9
for c in ledger["calls"]:
    for kind in ("request", "response"):
        path = P / f"{kind}-{c['sequence']:03d}.json"
        assert path.exists() and sha(path) == c[f"{kind}_sha256"]
    assert c["status_code"] == 200 and c["served_model"] in {
        "gpt-6.1-sol",
        "gpt-5.5-2026-04-23",
        "gemini-3-flash-preview",
        "gemini-3.7-flash",
    }
source_files = []
for name in [
    "modules/extract/ocr_ai_gpt51_v1/main.py",
    "modules/common/openai_client.py",
    "modules/common/google_client.py",
    "benchmarks/providers/openai_responses_model.py",
    "benchmarks/providers/gpt61_guard.py",
    "benchmarks/providers/gpt61_openai.py",
    "benchmarks/providers/gpt61_gemini.py",
    "benchmarks/gpt61-bootstrap/sitecustomize.py",
    "benchmarks/scripts/gpt61_native_probe.py",
    "benchmarks/scripts/gpt61_preflight.py",
    "benchmarks/prompts/crop-conservative-count.js",
    "benchmarks/prompts/validate-page-level-crop.js",
    "benchmarks/scorers/image_crop_scorer.py",
    "benchmarks/scorers/crop_validation_scorer.py",
    "benchmarks/scorers/handwritten_notes_transcription.py",
    "benchmarks/golden/image-crops.json",
    "benchmarks/golden/crop-eval-provenance.json",
    "benchmarks/golden/crop-page-level-deletion-gate.json",
    "benchmarks/golden/handwritten-notes/corpus.json",
]:
    path = ROOT / name
    if path.exists():
        frozen = DEST / "046-execution-sources" / name
        entry = ref(frozen if frozen.exists() else path)
        if frozen.exists():
            entry["executed_path"] = name
        source_files.append(entry)
source_files += [
    ref(x) for x in sorted((ROOT / "benchmarks/tasks").glob("gpt61-*.yaml"))
]
source_files += [
    ref(x) for x in sorted((ROOT / "configs/recipes").glob("gpt61-ocr-*.yaml"))
]
for name in [
    "testdata/handwritten-notes-barney-real-images/page-001.jpg",
    "testdata/handwritten-notes-alverson-real-images/page-001.jpg",
    "testdata/handwritten-notes-barney-real.txt",
    "testdata/handwritten-notes-alverson-real.txt",
    "benchmarks/input/source-pages-b64/Image011.b64.txt",
    "benchmarks/input/source-pages-b64/Image121.b64.txt",
    "benchmarks/input/crop-validation-b64/page-122-001.b64.txt",
]:
    source_files.append(ref(ROOT / name))
ocr = []
for arm, model, runprefix in [
    ("candidate", "gpt-6.1-sol", "gpt61-sol-{}-image"),
    ("control", "gemini-3.7-flash", "gpt61-control-gemini37-{}-image"),
]:
    for f in ("barney", "alverson"):
        score = json.loads(
            (
                P
                / f"ocr-{'gpt61' if arm == 'candidate' else 'gemini37'}-{f}-score.json"
            ).read_text()
        )
        run = ROOT / "output/runs" / runprefix.format(f)
        instrument = json.loads((run / "instrumentation.json").read_text())
        stage = next(s for s in instrument["stages"] if s["id"] == "ocr_ai")
        rec = next(
            c
            for c in ledger["calls"]
            if c["stage"] == f"ocr-{'gpt61' if arm == 'candidate' else 'gemini37'}-{f}"
        )
        ocr.append(
            {
                "arm": arm,
                "model": model,
                "fixture": f,
                "fidelity": score["overall_ratio"],
                "page_min_ratio": score["page_min_ratio"],
                "native_latency_ms": rec["latency_ms"],
                "ocr_stage_wall_seconds": stage["wall_seconds"],
                "cost_usd": rec["cost_usd"],
                "receipt_sequence": rec["sequence"],
                "artifact": ref(run / "02_ocr_ai_gpt51_v1/pages_html.jsonl"),
            }
        )
manifest = {
    "attempt": "046",
    "date": "2026-09-29",
    "repo": "doc-web",
    "base_sha": "5ca3711fb13b12b5b3e261438e7a00ffe450a647",
    "branch": "codex/gpt61-sol-eval-20260929",
    "worktree": "/Users/cam/.codex/worktrees/gpt61-sol-eval-20260929/doc-web",
    "decision_scope": "fresh bounded detector, conditional page safety, independent actual-driver public LOC handwriting",
    "privacy": "checked-in public Onward and LOC images plus synthetic probes only; Standard provider retention, no training by default; ZDR unverified",
    "provider_urls": [
        "https://developers.openai.com/api/docs/models/gpt-6.1-sol",
        "https://developers.openai.com/api/docs/models/gpt-5.5",
        "https://ai.google.dev/gemini-api/docs/pricing",
    ],
    "config": {
        "candidate": "gpt-6.1-sol low direct Responses Standard, strict schema detector/page, freeform OCR",
        "detector_control": "gemini-3-flash-preview maintained normalized prompt/config",
        "page_control": "gpt-5.5 none/2048 auto-detail Responses",
        "ocr_control": "gemini-3.7-flash maintained default medium",
        "cache": "no-cache Promptfoo, fresh driver run IDs",
        "concurrency": 1,
        "judge": "none; deterministic owner scorers",
        "initial_max_output": {"detector": 4096, "page": 4096, "ocr": 16384},
    },
    "detector": {
        "candidate": summary("detector-full13.json"),
        "control": summary("detector-gemini-control13.json"),
        "screen": summary("detector-image011.json"),
        "source_figure": ref(P / "image011-geometry.png"),
        "source_note": "Image011 lower box preserves seal and both signatures; printed officer text remains inside crop.",
    },
    "safety": {
        "candidate_screen": summary("page122-screen.json"),
        "gpt55_control_screen": summary("page122-gpt55-control.json"),
        "candidate_verdict": "false-safe pass on source-backed neighboring Sophie portrait; full22 not measured by progressive gate",
        "source_figure": ref(P / "page122-source-check.png"),
    },
    "ocr": ocr,
    "ledger": {
        "path": str((P / "ledger.json").relative_to(ROOT)),
        "sha256": sha(P / "ledger.json"),
        "known_settled_usd": ledger["spent_usd"],
        "unknown_reserved_usd": 0,
        "maximum_exposure_usd": ledger["spent_usd"],
        "cap_usd": ledger["cap_usd"],
        "closed": True,
        "calls": len(ledger["calls"]),
    },
    "topology": ref(DEST / "046-gpt61-topology.json"),
    "archive_index": ref(DEST / "046-reproducibility-index.json"),
    "source_files": source_files,
    "receipt_summary": [
        {
            "sequence": c["sequence"],
            "stage": c["stage"],
            "requested_model": c["model"],
            "served_model": c["served_model"],
            "response_id": c.get("response_id"),
            "latency_ms": c.get("latency_ms"),
            "cost_usd": c["cost_usd"],
            "request_sha256": c["request_sha256"],
            "response_sha256": c["response_sha256"],
        }
        for c in ledger["calls"]
    ],
    "reproduce": "python docs/evals/evidence/046-reconstruct.py --parts docs/evals/evidence/046-reproducibility.tar.gz.part01 --destination /tmp/doc-web-046-verify",
    "credential_custody": "Existing owner DOC_WEB_OPENAI_API_KEY and DOC_WEB_GEMINI_API_KEY through read-only wrapper; no injection/copy/cleanup needed.",
}
(DEST / "046-gpt61-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(
    "manifest",
    len(source_files),
    "source files",
    len(ocr),
    "OCR cases",
    len(ledger["calls"]),
    "receipts",
)
