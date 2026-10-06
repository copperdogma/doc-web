"""Freeze public receipts and deterministic scoring without inference."""

from pathlib import Path
import base64
import hashlib
import io
import json
import re
import statistics
import tarfile
import sys

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / "benchmarks"
R = B / "results/mistral-large4-20261006"
E = ROOT / "docs/evals/evidence"
sys.path.insert(0, str(B / "scorers"))
import handwritten_notes_transcription as ocr  # noqa: E402
import crop_validation_scorer as safety  # noqa: E402


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    ledger = json.loads((R / "ledger.json").read_text())
    ids = [c["response_id"] for c in ledger["calls"]]
    assert len(ids) == len(set(ids)) == 40
    assert all(c["cost_usd"] is not None for c in ledger["calls"])
    assert (
        abs(sum(c["cost_usd"] for c in ledger["calls"]) - ledger["spent_usd"]) < 1e-10
    )
    for c in ledger["calls"]:
        if c["sequence"] == 16:
            continue
        for kind in ["request", "response"]:
            raw = (R / f"{kind}-{c['sequence']:03d}.json").read_bytes()
            assert sha(raw) == c[kind + "_sha256"]
    ledger["closed"] = True
    ledger["stop_reason"] = (
        "Independent detector/safety/OCR decisions reached; no further calls"
    )
    (R / "ledger.json").write_text(json.dumps(ledger, indent=2) + "\n")
    results = {}
    for stage in sorted({c["stage"] for c in ledger["calls"]}):
        calls = [c for c in ledger["calls"] if c["stage"] == stage]
        lat = [c["latency_ms"] for c in calls if c.get("latency_ms") is not None]
        results[stage] = {
            "calls": len(calls),
            "cost_usd": sum(c["cost_usd"] for c in calls),
            "mean_latency_ms": statistics.mean(lat) if lat else None,
            "p50_latency_ms": statistics.median(lat) if lat else None,
            "latency_ms": lat,
        }
    for stage in ["detector-full", "detector-control-full"]:
        rows = json.loads((R / (stage + ".json")).read_text())["results"]["results"]
        results[stage]["rows"] = [
            {
                "case": x["vars"]["golden_key"],
                "pass": x["success"],
                "score": x["score"],
                "reason": x["gradingResult"]["reason"],
                "output": x["response"]["output"],
            }
            for x in rows
        ]
        results[stage]["mean_score"] = statistics.mean(x["score"] for x in rows)
        results[stage]["passing"] = sum(x["success"] for x in rows)
    for stage in ["safety", "safety-control"]:
        rows = json.loads((R / (stage + "-progressive.json")).read_text())
        both = []
        for x in rows:
            v = {
                **x["vars"],
                "golden_relpath": "golden/crop-page-level-safety-repair-048.json",
            }
            frozen = safety.get_assert(x["response"]["output"], {"vars": v})
            both.append(
                {
                    "case": x["vars"]["crop_key"],
                    "source_adjudicated_pass": x["success"],
                    "frozen_primary_pass": frozen["pass"],
                    "output": x["response"]["output"],
                    "source_reason": x["gradingResult"]["reason"],
                }
            )
        results[stage + "-full"]["rows"] = both
        results[stage + "-full"]["source_adjudicated_correct"] = sum(
            x["source_adjudicated_pass"] for x in both
        )
        results[stage + "-full"]["frozen_correct"] = sum(
            x["frozen_primary_pass"] for x in both
        )
        results[stage + "-full"]["unrun"] = 22 - len(rows)
    for arm in ["candidate", "control"]:
        suffix = "-recovery1" if arm == "control" else ""
        artifact = (
            ROOT
            / f"output/runs/mistral4-ocr-{arm}-barney-20261006{suffix}/02_ocr_ai_gpt51_v1/pages_html.jsonl"
        )
        results["ocr-" + arm]["score"] = ocr.score_page_html_artifact(
            ROOT / "testdata/handwritten-notes-barney-real.txt", artifact
        )
        results["ocr-" + arm]["alverson"] = "not measured; clear Barney lane failure"
    c39 = json.loads((R / "request-039.json").read_text())
    c40 = json.loads((R / "request-040.json").read_text())
    subject_system = c39["messages"][0]["content"]
    control_system = "".join(
        x["text"]
        for x in c40.get("systemInstruction", c40.get("system_instruction"))["parts"]
    )
    subject_user = c39["messages"][1]["content"][0]["text"]
    control_user = c40["contents"][0]["parts"][0]["text"]
    subject_uri = c39["messages"][1]["content"][1]["image_url"]["url"]
    part = c40["contents"][0]["parts"][1].get(
        "inlineData", c40["contents"][0]["parts"][1].get("inline_data")
    )
    assert subject_system == control_system and subject_user == control_user
    raw = base64.b64decode(subject_uri.split(",")[1])
    assert (
        raw
        == base64.urlsafe_b64decode(part["data"])
        == (
            ROOT / "testdata/handwritten-notes-barney-real-images/page-001.jpg"
        ).read_bytes()
    )
    parity = {
        "ocr_system_text_sha256": sha(subject_system.encode()),
        "ocr_user_text_sha256": sha(subject_user.encode()),
        "ocr_image_sha256": sha(raw),
        "image_bytes": len(raw),
        "candidate_roles": ["system", "user"],
        "control_roles": "systemInstruction plus independent user contents",
        "matching": True,
    }
    files = [p for p in R.rglob("*") if p.is_file() and p.name != "dispatch.lock"]
    for arm, suffix in [("candidate", ""), ("control", ""), ("control", "-recovery1")]:
        run = ROOT / f"output/runs/mistral4-ocr-{arm}-barney-20261006{suffix}"
        files.extend(
            p for p in run.rglob("*") if p.is_file() and "__pycache__" not in p.parts
        )
    token = re.compile(rb'data:image/[^;"\\\s]+;base64,[A-Za-z0-9+/=]+')
    blobs = {}
    entries = []
    archive_path = E / "061-mistral4-receipts.tar.gz"
    with tarfile.open(archive_path, "w:gz") as archive:

        def add(name, data):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o600
            archive.addfile(info, io.BytesIO(data))

        for p in sorted(set(files)):
            raw = p.read_bytes()

            def replace(match):
                value = match[0]
                digest = sha(value)
                blobs[digest] = value
                return ("@DOCWEB061_IMAGE:" + digest + "@").encode()

            template = token.sub(replace, raw)
            name = str(p.relative_to(ROOT))
            add("artifacts/" + name, template)
            entries.append(
                {
                    "path": name,
                    "sha256": sha(raw),
                    "bytes": len(raw),
                    "template_sha256": sha(template),
                }
            )
        for digest, raw in blobs.items():
            add("blobs/" + digest, raw)
    sources = [p for p in (E / "061-execution-sources").rglob("*") if p.is_file()]
    sources += (
        list((B / "tasks").glob("mistral4*.yaml"))
        + list((ROOT / "configs/recipes").glob("mistral4*.yaml"))
        + [
            B / "golden/crop-page-level-safety-repair-048.json",
            B / "golden/crop-page-level-safety-repair-048-source-adjudicated.json",
            ROOT / "testdata/handwritten-notes-barney-real.txt",
            ROOT / "testdata/handwritten-notes-alverson-real.txt",
        ]
    )
    manifest = {
        "attempt": "061",
        "story": "244",
        "base_sha": "fc558e2e924d0d598f31c69ee86fd5255f696f86",
        "requested_model": "mistralai/mistral-large-4-0",
        "served_model": "mistralai/mistral-large-4-0",
        "served_provider": "Mistral",
        "dated_catalog": "20261006; alias not an immutable snapshot proof",
        "privacy": "public Onward/public LOC/synthetic qualification only; route retention/training unverified disclosed; no private payload",
        "cap_usd": 11,
        "settled_usd": ledger["spent_usd"],
        "unknown_usd": 0,
        "unique_calls": 40,
        "judge": "none; deterministic scorer and independent source review",
        "configuration": "Candidate no unsupported reasoning; pin mistral/no fallback, max_price0.68input/2.09outputUSD/M;4096 detector/safety16384OCR. Controls maintained Gemini3 Flash temperature0/16384, GPT5.5 none2048auto, Gemini3.7 default thinking16384",
        "results": results,
        "ocr_parity": parity,
        "ledger": ledger,
        "artifacts": entries,
        "archive": {
            "path": str(archive_path.relative_to(ROOT)),
            "bytes": archive_path.stat().st_size,
            "sha256": sha(archive_path.read_bytes()),
            "blob_hashes": sorted(blobs),
        },
        "sources": {
            str(p.relative_to(ROOT)): {
                "bytes": p.stat().st_size,
                "sha256": sha(p.read_bytes()),
            }
            for p in sources
        },
        "provenance_limits": [
            "Native safety overlapped final detector requests despite plannedserial; ledger/numbered native files overwritten. Surviving full native-safety response settles exactcost. Deterministic reconstructed request is explicitly reconstructed, originalledgerbytes absent and latencylost. Production safety screen request-030/response-030 captured actual strictflag proof; native mini excluded from semantic scores.",
            "Detector latency descriptive5.137vs6.739s, partially overlapped one qualificationcall; not controlledconcurrency/variance proof.",
            "OCR control first Python3.14venv driver start missinggoogleSDK beforeHTTP($0). ExistingPython3.11SDK restored actualdriver control with newrunid; failed run/log retained. CandidatePython3.14/controlPython3.11; exact system/user/imagebytes match.",
            "Executed source snapshots preserved before formatting-only lint corrections; originalguard bytes reconstructed and hash verified against original paid receipts.",
        ],
        "verdict": {
            "detector": "Do not adopt now: numeric13/13>=.95 and lowercost, but source-visible critical logo clipping; retain Gemini until heldout/sourcefaithfulness and retainedsafetydriver proof.",
            "safety": "Do not adopt: valid false-safe incomplete seal under source-adjudicated truth; full22 notpassed, later17 unrun. FreshGPT5.5 false-rejectcover also stops independently.",
            "ocr": "Do not adopt: Barney.939957 worse than freshGemini.978830; both<.99. Alversonsourcegoldvalidprechecked but notmeasured.",
        },
        "validation": {
            "command": "python -m pytest tests/test_mistral4_guard.py tests/test_openrouter_vision_chat_provider.py tests/test_openai_responses_model_provider.py tests/test_handwritten_notes_eval.py -q",
            "result": "33 passed before formatting; final revalidation follows",
            "scope": "budget/duplicate/unknown/no-reasoning/crossprocess actual HTTP dispatch, owner adapter and transcription scorer; actual driver candidate/control Barney outputs opened",
        },
    }
    (E / "061-mistral4-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (E / "061-stage-summary.json").write_text(json.dumps(results, indent=2) + "\n")
    print(
        json.dumps(
            {
                "files": len(entries),
                "archive_bytes": archive_path.stat().st_size,
                "calls": 40,
                "settled": ledger["spent_usd"],
                "parity": parity,
            }
        )
    )


if __name__ == "__main__":
    main()
