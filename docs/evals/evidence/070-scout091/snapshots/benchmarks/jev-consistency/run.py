"""Eval-only native classifier comparison; no runtime imports or default edits."""

from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import statistics
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).parent
OUT = ROOT / "docs/evals/artifacts/jev-consistency-20260921"
LABELS = {
    "conformant": "The text and row ownership match source evidence and explicit document-local conventions; allowed layout variations are not defects.",
    "format_drift": "A documented table/header/layout convention is violated, but no row value, meaning or attachment contradicts source evidence.",
    "row_semantic_issue": "A row value, meaning or note attachment contradicts source evidence, while table/header/layout conventions are satisfied.",
    "mixed": "Both a table/header/layout convention violation and a source-supported row value, meaning or attachment defect are present.",
    "uncertain": "Evidence or explicit conventions are insufficient or ambiguous to establish whether this chapter is conformant or defective.",
}
INSTRUCTION = "Classify the extracted chapter tables or maintenance cards against the explicit conventions and source evidence. Evaluate meaning and attachment, not just structural validity. Use only supplied evidence. A fused header with correct paired values is format-only; wrong source values or attachments are semantic defects. Incomplete/ambiguous evidence without an established defect means uncertain. Return one class."
SCHEMA = {
    "type": "object",
    "properties": {"classification": {"type": "string", "enum": list(LABELS)}},
    "required": ["classification"],
    "additionalProperties": False,
}
MODEL = "gpt-4.1-2025-04-14"
CAP = 0.60


def payload(provider, state):
    if provider == "jev":
        return {
            "model": "jev-1.13.0",
            "state": state,
            "questions": {
                "status": {
                    "type": "choice",
                    "instructions": INSTRUCTION,
                    "criteria": LABELS,
                }
            },
        }
    return {
        "model": MODEL,
        "store": False,
        "temperature": 0,
        "max_completion_tokens": 160,
        "messages": [
            {"role": "system", "content": INSTRUCTION + "\n" + json.dumps(LABELS)},
            {"role": "user", "content": json.dumps(state, ensure_ascii=False)},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "consistency_classification",
                "strict": True,
                "schema": SCHEMA,
            },
        },
    }


def parse(provider, raw):
    usage = raw.get("usage", {})
    ik = "input_tokens" if provider == "jev" else "prompt_tokens"
    ok = "output_tokens" if provider == "jev" else "completion_tokens"
    if any(type(usage.get(k)) is not int or usage[k] < 0 for k in [ik, ok]):
        raise ValueError("Invalid usage")
    if provider == "jev":
        if raw.get("model") != "jev-1.13.0" or raw.get("error") or "status" in raw:
            raise ValueError("Invalid identity/status")
        a = raw["answers"]["status"]
        p = a["probabilities"]
        c = a["confidence"]
        if a["type"] != "choice" or set(p) != set(LABELS) or a["choice"] not in p:
            raise ValueError("Invalid choice contract")
        if (
            not all(
                type(x) in [int, float] and math.isfinite(x) and 0 <= x <= 1
                for x in p.values()
            )
            or abs(sum(p.values()) - 1) > 0.002
        ):
            raise ValueError("Invalid probabilities")
        if (
            not isinstance(c, (int, float))
            or not math.isfinite(c)
            or not 0 <= c <= 1
            or p[a["choice"]] < max(p.values())
        ):
            raise ValueError("Invalid confidence/choice")
        return a["choice"], c, usage[ik] * 0.042 / 1e6
    if (
        raw.get("model") != MODEL
        or raw.get("error")
        or len(raw.get("choices", [])) != 1
    ):
        raise ValueError("Invalid identity/envelope")
    ch = raw["choices"][0]
    if ch["finish_reason"] != "stop" or ch["message"].get("refusal"):
        raise ValueError("Incomplete/refused")
    obj = json.loads(ch["message"]["content"])
    if set(obj) != {"classification"} or obj["classification"] not in LABELS:
        raise ValueError("Invalid strict object")
    cached = usage.get("prompt_tokens_details", {}).get("cached_tokens", 0)
    if not isinstance(cached, int) or not 0 <= cached <= usage[ik]:
        raise ValueError("Invalid cache usage")
    return (
        obj["classification"],
        None,
        ((usage[ik] - cached) * 2 + cached * 0.5 + usage[ok] * 8) / 1e6,
    )


def deterministic(state):
    # Newly authored structural-only comparator, not the maintained genealogy detector.
    if "cards" in state:
        titles = [c["title"] for c in state["cards"]]
        return (
            "format_drift"
            if len(titles) != len(set(titles)) or any(" / " in t for t in titles)
            else "conformant"
        )
    expected = sorted(x.lower() for x in state["conventions"]["headers"])
    main = [t for t in state["tables"] if t["headers"] != ["Metric", "Count"]]
    if any(sorted(x.lower() for x in t["headers"]) != expected for t in main):
        return "format_drift"
    if any(not t["page_break_before"] for t in main[1:]):
        return "format_drift"
    return "conformant"


def call(provider, state, name):
    req = payload(provider, state)
    data = json.dumps(req, ensure_ascii=False).encode()
    ledger = json.loads((OUT / "ledger.json").read_text())
    # JEV documented maximum request context, independent of hidden serialization.
    # GPT-4.1: byte upper bound +256 framing and fixed nonreasoning output ceiling.
    reserve = (
        64000 * 0.042 / 1e6
        if provider == "jev"
        else (len(data) + 256) * 2 / 1e6 + 160 * 8 / 1e6
    )
    if ledger["spent_usd"] + ledger["reserved_unknown_usd"] + reserve > CAP:
        raise RuntimeError("Hard spend cap")
    if (
        any(c["name"] == name for c in ledger["calls"])
        or (OUT / f"{name}.request.json").exists()
        or (OUT / f"{name}.response.json").exists()
    ):
        raise RuntimeError("Refuse duplicate dispatch/overwrite")
    entry = {
        "name": name,
        "provider": provider,
        "reserve_usd": reserve,
        "status": "dispatched",
    }
    ledger["reserved_unknown_usd"] += reserve
    ledger["calls"].append(entry)
    (OUT / "ledger.json").write_text(json.dumps(ledger, indent=2) + "\n")
    (OUT / f"{name}.request.json").write_bytes(data)
    endpoint = (
        "https://api.typesafe.ai/v1/systemone"
        if provider == "jev"
        else "https://api.openai.com/v1/chat/completions"
    )
    key = os.environ[
        "DOC_WEB_TYPESAFE_API_KEY" if provider == "jev" else "OPENAI_API_KEY"
    ]
    started = time.monotonic()
    try:
        with urllib.request.urlopen(
            urllib.request.Request(
                endpoint,
                data=data,
                headers={
                    "Authorization": "Bearer " + key,
                    "Content-Type": "application/json",
                },
            ),
            timeout=45,
        ) as r:
            response = r.read()
            status = r.status
    except urllib.error.HTTPError as e:
        response = e.read()
        status = e.code
    except Exception:
        entry["status"] = "delivery_unknown"
        (OUT / "ledger.json").write_text(json.dumps(ledger, indent=2) + "\n")
        raise RuntimeError("Unknown delivery; inspect retained ledger") from None
    elapsed = (time.monotonic() - started) * 1000
    (OUT / f"{name}.response.json").write_bytes(response)
    entry.update(http_status=status, latency_ms=elapsed)
    if status != 200:
        entry["status"] = "http_error_unknown_billing"
        (OUT / "ledger.json").write_text(json.dumps(ledger, indent=2) + "\n")
        raise RuntimeError("Provider HTTP error retained")
    raw = json.loads(response)
    try:
        label, confidence, cost = parse(provider, raw)
    except Exception:
        entry["status"] = "contract_invalid_unknown_billing"
        (OUT / "ledger.json").write_text(json.dumps(ledger, indent=2) + "\n")
        raise
    entry.update(
        status="complete",
        cost_usd=cost,
        label=label,
        confidence=confidence,
        usage=raw["usage"],
        served_model=raw["model"],
    )
    ledger["reserved_unknown_usd"] -= reserve
    ledger["spent_usd"] += cost
    (OUT / "ledger.json").write_text(json.dumps(ledger, indent=2) + "\n")
    return entry


def metrics(rows):
    n = len(rows)
    correct = sum(r["label"] == r["gold"] for r in rows)
    recalls = {
        k: sum(r["label"] == k and r["gold"] == k for r in rows)
        / max(1, sum(r["gold"] == k for r in rows))
        for k in LABELS
    }
    f1 = []
    for k in LABELS:
        tp = sum(r["label"] == k and r["gold"] == k for r in rows)
        fp = sum(r["label"] == k and r["gold"] != k for r in rows)
        fn = sum(r["label"] != k and r["gold"] == k for r in rows)
        f1.append(2 * tp / max(1, 2 * tp + fp + fn))
    defect = {"format_drift", "row_semantic_issue", "mixed"}
    lat = sorted(r["latency_ms"] for r in rows)
    return {
        "n": n,
        "correct": correct,
        "accuracy": correct / n,
        "macro_f1": sum(f1) / 5,
        "recall": recalls,
        "defects_called_clean": sum(
            r["gold"] in defect and r["label"] == "conformant" for r in rows
        ),
        "clean_flagged_defect": sum(
            r["gold"] == "conformant" and r["label"] in defect for r in rows
        ),
        "cost_usd": sum(r["cost_usd"] for r in rows),
        "median_ms": statistics.median(lat),
        "p95_ms": lat[math.ceil(0.95 * n) - 1],
        "misses": [
            {"id": r["id"], "gold": r["gold"], "predicted": r["label"]}
            for r in rows
            if r["label"] != r["gold"]
        ],
    }


def report():
    rows = json.loads((OUT / "results.json").read_text())
    summary = {
        arm: metrics([r for r in rows if r["arm"] == arm])
        for arm in sorted(set(r["arm"] for r in rows))
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--repeats", type=int, default=2)
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    if a.report:
        report()
        return
    cases = json.loads((HERE / "fixtures.json").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    if not a.run:
        rendered = [
            {
                "id": c["id"],
                "jev": payload("jev", c["input"]),
                "gpt": payload("gpt", c["input"]),
            }
            for c in cases
        ]
        (OUT / "rendered.json").write_text(json.dumps(rendered, indent=2) + "\n")
        print(
            {
                "cases": len(cases),
                "labels": list(LABELS),
                "cache": False,
                "concurrency": 1,
            }
        )
        return
    if not (OUT / "review.json").exists():
        raise RuntimeError("Independent review required")
    manifest = json.loads((OUT / "source-manifest.json").read_text())
    for path, expected in manifest["sources"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise RuntimeError("Frozen source mismatch: " + path)
    review = json.loads((OUT / "review.json").read_text())
    if (
        review.get("approved_fixture_sha256")
        != hashlib.sha256((HERE / "fixtures.json").read_bytes()).hexdigest()
    ):
        raise RuntimeError("Review hash mismatch")
    if not (OUT / "ledger.json").exists():
        (OUT / "ledger.json").write_text(
            json.dumps(
                {
                    "cap_usd": CAP,
                    "spent_usd": 0,
                    "reserved_unknown_usd": 0,
                    "calls": [],
                },
                indent=2,
            )
            + "\n"
        )
    rows = (
        json.loads((OUT / "results.json").read_text())
        if (OUT / "results.json").exists()
        else []
    )
    for rep in range(a.repeats):
        for c in cases[: a.limit]:
            identity = f"r{rep + 1}-{c['id']}"
            if any(r["id"] == identity and r["arm"] == "cascade" for r in rows):
                continue
            # Single native request function is also harness adapter: exact lossless parity.
            j = call("jev", c["input"], identity + "-jev")
            if j["confidence"] < 0.8 and j["label"] != "uncertain":
                fallback = call("gpt", c["input"], identity + "-fallback")
                casc = {
                    **fallback,
                    "cost_usd": j["cost_usd"] + fallback["cost_usd"],
                    "latency_ms": j["latency_ms"] + fallback["latency_ms"],
                    "fallback": True,
                }
            else:
                casc = {**j, "fallback": False}
            g = call("gpt", c["input"], identity + "-gpt")
            for arm, result in [
                ("jev", j),
                ("gpt", g),
                ("cascade", casc),
                (
                    "structural",
                    {
                        "label": deterministic(c["input"]),
                        "cost_usd": 0,
                        "latency_ms": 0,
                    },
                ),
            ]:
                rows.append(
                    {
                        "id": identity,
                        "gold": c["gold"],
                        "domain": c["domain"],
                        "arm": arm,
                        **result,
                    }
                )
            (OUT / "results.json").write_text(json.dumps(rows, indent=2) + "\n")
            print(
                identity,
                j["label"],
                g["label"],
                "fallback=" + str(casc["fallback"]),
                flush=True,
            )
    report()


if __name__ == "__main__":
    main()
