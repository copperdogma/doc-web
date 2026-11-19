"""Exact native Google execution and independent Scout 119 wallets."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from benchmarks.scripts import hydrogen_native
from benchmarks.scripts.scout116_doc_web_score import score_ocr

RAW = ROOT / "output/fixtures/scout119-neon"
E = ROOT / "docs/evals/evidence/099-neon"
OLD = ROOT / "docs/evals/evidence/094-hydrogen/rendered"
HOST = "https://generativelanguage.googleapis.com/v1beta/models/"
NEON = "gemini-4-neon"
HYDROGEN = "gemini-4-hydrogen"
FLASH = "gemini-3-flash-preview"
CAPS = {"ocr": 4_000_000_000, "crop": 8_000_000_000}
CANDIDATE_MAX = {"ocr": 4, "crop": 5}
# USD nanounits per token, on standard foreground requests.
RATES = {NEON: (3000, 150, 15000), HYDROGEN: (1500, 75, 7500), FLASH: (500, 50, 3000)}
BOUND_INPUT = 106_000


def load(path):
    return json.loads(path.read_bytes())


def save(path, data):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    tmp.replace(path)


def wire(body):
    return json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def secure(path, raw):
    with path.open("xb") as stream:
        path.chmod(0o600)
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def modern(body):
    config = body["generationConfig"]
    for k in ("temperature", "topP", "topK"):
        config.pop(k, None)
    config.update(maxOutputTokens=32768, thinkingConfig={"thinkingLevel": "HIGH"})
    return body


def slot_reserve(model, body):
    # Gemini 4 foreground output includes thinking in its published bound.
    # Allow the Gemini 3 control its full 24,576 budget in addition to visible
    # output in case the older service interprets that limit separately.
    output = body["generationConfig"]["maxOutputTokens"]
    if model == FLASH:
        output += 24_576
    cold, _, out = RATES[model]
    return BOUND_INPUT * cold + output * out


def freeze():
    from tools import neon_detector_099_runtime as runtime

    RAW.mkdir(mode=0o700, parents=True)
    E.mkdir(parents=True)
    matrix = {}

    def put(name, lane, model, body, case):
        raw = wire(body)
        path = RAW / (name + ".request.json")
        secure(path, raw)
        matrix[name] = {
            "lane": lane, "case": case, "model": model,
            "request": str(path.relative_to(ROOT)), "sha256": digest(raw),
            "reserve_nanousd": slot_reserve(model, body),
        }

    for case in ("barney", "alverson"):
        original = load(OLD / f"ocr-{case}-candidate.json")
        for model in (NEON, HYDROGEN):
            put(f"ocr-{case}-{model}", "ocr", model, modern(original), case)
    for row in runtime.capture_matrix():
        body = load_bytes(row["body_bytes"])
        name = row["slot"]
        if row["role"] == "caption":
            body["generationConfig"]["maxOutputTokens"] = 8192
        model = NEON if row["arm"] == "candidate" else FLASH
        put(name, "crop", model, body, row["page"])
    producers = (
        "benchmarks/scripts/scout119_doc_web.py",
        "benchmarks/scripts/scout116_doc_web_score.py",
        "benchmarks/scorers/handwritten_notes_transcription.py",
        "tools/neon_detector_099_runtime.py",
        "tools/hydrogen_detector_094_runtime.py",
        "modules/common/google_client.py",
        "modules/extract/crop_illustrations_guided_v1/main.py",
        "scripts/prepare_story231_crop_fixture.py",
        "configs/recipes/story-231-gemini-crop-runtime-validate.yaml",
        "testdata/handwritten-notes-barney-real.txt",
        "testdata/handwritten-notes-alverson-real.txt",
    )
    save(E / "matrix.json", {
        "base": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=ROOT).strip(),
        "cases": matrix, "providers": "Google Developer API Standard paid",
        "concurrency": 1, "caps_nanousd": CAPS, "candidate_call_limits": CANDIDATE_MAX,
        "judge": None, "source_output_cache": False,
        "producer_sha256": {p: digest((ROOT / p).read_bytes()) for p in producers},
    })
    save(E / "ledger.json", {"closed": False, "calls": []})
    report = {}
    for lane in CAPS:
        rows = [r for r in matrix.values() if r["lane"] == lane]
        # Caption attempts are mutually exclusive by actual illustration count.
        # Reserve up to two per page if the arms need different counts.
        direct = [r["reserve_nanousd"] for r in rows if "-caption-" not in r["request"]]
        captions = {
            page: max(r["reserve_nanousd"] for r in rows if r["case"] == page and "-caption-" in r["request"])
            for page in {r["case"] for r in rows if "-caption-" in r["request"]}
        }
        recovery = max(r["reserve_nanousd"] for r in rows)
        planned = sum(direct) + 2 * sum(captions.values()) + recovery
        if planned > CAPS[lane]:
            raise ValueError(f"{lane} frozen current matrix exceeds approved cap")
        report[lane] = {"all_frozen_pairs_and_one_recovery_nanousd": planned,
                        "cap_nanousd": CAPS[lane]}
    save(E / "offline-reservation.json", report)
    print(json.dumps(report))


def load_bytes(raw):
    return json.loads(raw)


def body_for(slot):
    row = load(E / "matrix.json")["cases"][slot]
    raw = (ROOT / row["request"]).read_bytes()
    if digest(raw) != row["sha256"]:
        raise ValueError(f"{slot} immutable body mismatch")
    return row, load_bytes(raw), raw


def key_headers():
    if not os.environ.get("DOC_WEB_GEMINI_API_KEY") or not os.environ.get("GEMINI_API_KEY"):
        raise RuntimeError("missing owner DOC_WEB_GEMINI_API_KEY through owner wrapper")
    return {"x-goog-api-key": os.environ["GEMINI_API_KEY"]}


def safe_error(data):
    error = data.get("error", {})
    return {name: error[name] for name in ("code", "status") if name in error} | {
        "reason": [d.get("reason") for d in error.get("details", []) if isinstance(d, dict) and d.get("reason")]
    }


def admit():
    headers = key_headers()
    matrix = load(E / "matrix.json")["cases"]
    receipts = {}
    catalog = {}
    with httpx.Client(timeout=60, follow_redirects=False) as client:
        for model in (NEON, HYDROGEN, FLASH):
            response = client.get(HOST + model, headers=headers)
            data = response.json()
            catalog[model] = {"status": response.status_code, "identity": data.get("name"),
                             "methods": data.get("supportedGenerationMethods"), "error": safe_error(data)}
        save(E / "catalog.json", catalog)
        if catalog[NEON]["identity"] != f"models/{NEON}" or catalog[NEON]["status"] != 200:
            print(json.dumps(catalog[NEON]))
            return
        for slot in matrix:
            # Count every possible wire shape before any paid progressive work.
            row, body, _ = body_for(slot)
            model = row["model"]
            response = client.post(HOST + model + ":countTokens", headers=headers, json={
                "generateContentRequest": {"model": f"models/{model}", **body}
            })
            data = response.json()
            count = data.get("totalTokens")
            receipts[slot] = {"http": response.status_code, "count": count, "request_sha256": row["sha256"],
                              "admitted": response.is_success and type(count) is int and 0 < count <= BOUND_INPUT,
                              "error": safe_error(data)}
            save(E / "admission.json", receipts)
            print(slot, receipts[slot]["http"], count, flush=True)


def parse(model, body, data):
    schema = body["generationConfig"].get("responseJsonSchema")
    if model == NEON:
        # Reuse the owner exact Gemini 4 terminal/content/usage/schema checks.
        if data.get("modelVersion") != model:
            raise ValueError("Neon served identity mismatch")
        return hydrogen_native.parse(dict(data, modelVersion=HYDROGEN), HYDROGEN, schema)
    return hydrogen_native.parse(data, model, schema)


def rated_cost(model, body, data):
    usage = data.get("usageMetadata", {})
    prompt, visible = usage.get("promptTokenCount"), usage.get("candidatesTokenCount")
    thinking, cached = usage.get("thoughtsTokenCount", 0), usage.get("cachedContentTokenCount", 0)
    if any(type(n) is not int or n < 0 for n in (prompt, visible, thinking, cached)):
        return None
    max_out = body["generationConfig"]["maxOutputTokens"] + (24576 if model == FLASH else 0)
    if not 0 <= cached <= prompt <= BOUND_INPUT or visible + thinking > max_out:
        return None
    cold, cache, out = RATES[model]
    return ((prompt - cached) * cold + cached * cache + (visible + thinking) * out)


def send(slot, *, recover=False, injected_client=None):
    row, body, raw = body_for(slot)
    lane, model = row["lane"], row["model"]
    frozen = load(E / "matrix.json")
    if any(digest((ROOT / p).read_bytes()) != sha for p, sha in frozen["producer_sha256"].items()):
        raise ValueError("frozen producer changed")
    admission = load(E / "admission.json")[slot]
    if not admission["admitted"] or admission["request_sha256"] != row["sha256"]:
        raise ValueError("exact wire did not clear count admission")
    attempt = slot + ("-recovery" if recover else "")
    ledger_path = E / "ledger.json"
    with (RAW / "ledger.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        ledger = load(ledger_path)
        calls = ledger["calls"]
        if ledger["closed"] or any(c["in_flight"] for c in calls):
            raise ValueError("wallet closed or another request remains in flight")
        if any(c["attempt"] == attempt for c in calls):
            raise ValueError("duplicate attempt")
        if recover:
            prior = next((c for c in calls if c["attempt"] == slot), None)
            if not prior or prior.get("confidence") not in {"operational", "provider-transient"}:
                raise ValueError("operational failure must precede recovery")
            if any(c["lane"] == lane and c["attempt"].endswith("-recovery") for c in calls):
                raise ValueError("one operational recovery per lane")
        spent_or_reserved = sum(c["cost_nanousd"] if c["cost_nanousd"] is not None else c["reserve_nanousd"]
                                for c in calls if c["lane"] == lane)
        if spent_or_reserved + row["reserve_nanousd"] > CAPS[lane]:
            raise ValueError("wallet cap reached")
        if model == NEON and sum(c["lane"] == lane and c["model"] == NEON for c in calls) >= CANDIDATE_MAX[lane]:
            raise ValueError("finite candidate cap reached")
        if "-caption-" in slot and not recover and sum(
            c["lane"] == lane and c["case"] == row["case"] and "-caption-" in c["attempt"]
            and not c["attempt"].endswith("-recovery") for c in calls
        ) >= 2:
            raise ValueError("at most one different genuine caption per detector arm")
        receipt = {**row, "attempt": attempt, "cost_nanousd": None, "in_flight": True}
        calls.append(receipt)
        save(ledger_path, ledger)
        start = time.monotonic()
        try:
            client = injected_client or httpx
            response = client.post(HOST + model + ":generateContent", headers=key_headers(),
                                   content=raw, timeout=150, follow_redirects=False)
            path = RAW / (attempt + ".response.json")
            secure(path, response.content)
            data = response.json()
            receipt.update(http=response.status_code, response=str(path.relative_to(ROOT)),
                           response_sha256=digest(response.content), error=safe_error(data),
                           served_model=data.get("modelVersion"),
                           finish=[c.get("finishReason") for c in data.get("candidates", [])],
                           usage=data.get("usageMetadata"))
            receipt["cost_nanousd"] = rated_cost(model, body, data)
            if not response.is_success:
                receipt["confidence"] = "provider-transient" if response.status_code >= 500 else "provider-stop"
                return receipt
            if receipt["cost_nanousd"] is None:
                receipt["confidence"] = "invalid-accounting"
                return receipt
            if receipt["cost_nanousd"] > row["reserve_nanousd"]:
                ledger["closed"] = True
                raise ValueError("realized accounting exceeded reserved amount")
            try:
                text = parse(model, body, data)
            except (ValueError, hydrogen_native.jsonschema.ValidationError) as exc:
                receipt.update(confidence="contract-stop", contract_error=type(exc).__name__)
                return receipt
            secure(RAW / (attempt + ".answer.txt"), text.encode())
            receipt["confidence"] = "eligible"
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            receipt.update(confidence="operational", error_type=type(exc).__name__)
        finally:
            receipt.update(in_flight=False, latency_ms=round(1000 * (time.monotonic() - start)))
            save(ledger_path, ledger)
    return receipt


def ocr_score(slot):
    row, _, _ = body_for(slot)
    raw = (RAW / (slot + ".answer.txt")).read_text()
    score = score_ocr(row["case"], raw)
    save(E / (slot + ".score.json"), score)
    print(json.dumps({k: v for k, v in score.items() if k != "recognized_text"}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("freeze", "admit", "send", "score"))
    parser.add_argument("slot", nargs="?")
    parser.add_argument("--recover", action="store_true")
    args = parser.parse_args()
    if args.command == "send":
        print(json.dumps(send(args.slot, recover=args.recover)))
    elif args.command == "score":
        ocr_score(args.slot)
    else:
        globals()[args.command]()


if __name__ == "__main__":
    main()
