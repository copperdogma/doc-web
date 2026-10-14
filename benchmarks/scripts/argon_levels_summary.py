"""Offline effort-calibration metrics; never dispatches or closes a ledger."""

import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / "benchmarks/results/argon-levels-20261013"
E = ROOT / "docs/evals/evidence/072-argon-levels"


def charges(usage):
    inp = usage["promptTokenCount"]
    visible = usage.get("candidatesTokenCount", 0)
    thoughts = usage.get("thoughtsTokenCount", 0)
    cached = usage.get("cachedContentTokenCount", 0)
    return {
        "input_tokens": inp,
        "visible_tokens": visible,
        "thinking_tokens": thoughts,
        "cached_input_tokens": cached,
        "actual_usd": ((inp - cached) * 2 + cached * 0.1 + (visible + thoughts) * 10)
        / 1e6,
        "cold_usd": (inp * 2 + (visible + thoughts) * 10) / 1e6,
        "december_actual_same_usage_usd": (
            (inp - cached) * 4 + cached * 0.2 + (visible + thoughts) * 20
        )
        / 1e6,
        "december_cold_same_usage_usd": (inp * 4 + (visible + thoughts) * 20) / 1e6,
    }


def collect():
    ledger = json.loads((R / "ledger.json").read_text())
    frozen = json.loads((E / "freeze.json").read_text())
    calls = []
    for record in ledger["calls"]:
        item = next(x for x in frozen["matrix"] if x["stage"] == record["stage"])
        result = {**record, "lane": item["lane"], "case": item["case"]}
        if record.get("usage"):
            result["metrics"] = charges(record["usage"])
        calls.append(result)
    groups = []
    for lane, level in sorted(set((x["lane"], x["level"]) for x in calls)):
        selected = [x for x in calls if x["lane"] == lane and x["level"] == level]
        settled = [x for x in selected if x.get("metrics")]
        latencies = [x["latency_ms"] for x in settled]
        sums = {
            key: sum(x["metrics"][key] for x in settled)
            for key in charges({"promptTokenCount": 0})
        }
        groups.append(
            {
                "lane": lane,
                "level": level,
                "calls": len(selected),
                "settled_calls": len(settled),
                **sums,
                "full_native_response_latency_sum_ms": sum(latencies),
                "full_native_response_latency_mean_ms": statistics.mean(latencies)
                if latencies
                else None,
                "full_native_response_latency_samples_ms": latencies,
            }
        )
    unknown = sum(c["reserved_usd"] for c in calls if c.get("cost_usd") is None)
    return {
        "incremental_cap_usd": 6,
        "cumulative_cap_usd": 15,
        "prior_maximum_exposure_usd": frozen["old_maximum_exposure_usd"],
        "settled_usd": ledger["spent_usd"],
        "unknown_usd": unknown,
        "cumulative_maximum_exposure_usd": frozen["old_maximum_exposure_usd"]
        + ledger["spent_usd"]
        + unknown,
        "ledger_closed": ledger["closed"],
        "cost_estimated": True,
        "sample_latency_is_descriptive": True,
        "groups": groups,
        "calls": calls,
    }


if __name__ == "__main__":
    (E / "metrics.json").write_text(json.dumps(collect(), indent=2) + "\n")
