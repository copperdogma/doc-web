"""Offline safety receipt normalization and paired-prefix summary, no calls."""

import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / "docs/evals/evidence/078-scout096"
ledger = json.loads(
    (ROOT / "benchmarks/results/scout096-20261016/ledger.json").read_text()
)
summary = {
    "latency_basis": "guard HTTP send latency excludes queue lock waiting",
    "quality": "frozen Attempt048 source-adjudicated verdict; manual uncertainty veto remains mandatory",
    "arms": {},
}
rows = {}
for arm in ("d1", "span", "nemotron", "control"):
    p = E / f"safety-{arm}-results.json"
    if not p.exists():
        continue
    values = json.loads(p.read_text())
    seen = {}
    for row in values:
        nth = seen.get(row["key"], 0)
        seen[row["key"]] = nth + 1
        stage = f"safety-{arm}-{row['key']}"
        if nth:
            stage += "-recovery1"
        receipt = next(x for x in ledger["calls"] if x["stage"] == stage)
        if "elapsed_including_queue_ms" not in row:
            row["elapsed_including_queue_ms"] = row["latency_ms"]
        row["latency_ms"] = receipt["latency_ms"]
        row["receipt_response"] = receipt["response"]
    p.write_text(json.dumps(values, indent=2) + "\n")
    valid = [x for x in values if "verdict" in x]
    rows[arm] = {x["key"]: x for x in valid}
    calls = [x for x in ledger["calls"] if x["stage"].startswith(f"safety-{arm}-")]
    summary["arms"][arm] = {
        "valid_cases": len(valid),
        "exact": sum(x["correct"] for x in valid),
        "false_safe": sum(x["false_safe"] for x in valid),
        "safe_accepted": sum(
            x["verdict"] == "pass" and x["golden"] == "pass" for x in valid
        ),
        "cost_usd": sum(x.get("cost_usd") or 0 for x in calls),
        "unresolved_reservation_usd": sum(
            x["reserved_usd"] for x in calls if x.get("cost_usd") is None
        ),
        "median_latency_ms": statistics.median(x["latency_ms"] for x in valid)
        if valid
        else None,
        "unmeasured_remainder": 22 - len(valid),
    }
summary["paired_prefix"] = {}
for arm in ("span", "nemotron"):
    common = sorted(set(rows.get(arm, {})) & set(rows.get("control", {})))
    summary["paired_prefix"][arm] = {
        "n": len(common),
        "candidate_exact": sum(rows[arm][k]["correct"] for k in common),
        "control_exact": sum(rows["control"][k]["correct"] for k in common),
        "keys": common,
    }
(E / "safety-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
