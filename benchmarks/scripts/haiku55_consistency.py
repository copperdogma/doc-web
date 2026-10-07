"""Frozen Story233 native projection: one independent request per judgment."""

import importlib.util
import json
import os
import sys
from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / "benchmarks"
R = B / "results/haiku55-20261007"
sys.path.insert(0, str(B / "providers"))
import haiku55_guard as guard  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "maintained", B / "jev-consistency/run.py"
)
owner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(owner)
CASES = json.loads((B / "jev-consistency/fixtures.json").read_text())


def call(arm, c, rep, stage):
    os.environ["HAIKU55_STAGE"] = stage + "-" + arm
    os.environ["HAIKU55_CASE"] = f"r{rep}-{c['id']}"
    guard.install()
    if arm == "gpt":
        body = owner.payload("gpt", c["input"])
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]}
    else:
        body = {
            "model": "claude-haiku-5-5",
            "max_tokens": 1024,
            "system": owner.INSTRUCTION + "\n" + json.dumps(owner.LABELS),
            "messages": [
                {"role": "user", "content": json.dumps(c["input"], ensure_ascii=False)}
            ],
            "thinking": {"type": "disabled" if arm == "low" else "adaptive"},
            "output_config": {
                "effort": arm,
                "format": {"type": "json_schema", "schema": owner.SCHEMA},
            },
        }
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
        }
    r = httpx.post(url, headers=headers, json=body, timeout=180)
    r.raise_for_status()
    d = r.json()
    if arm == "gpt":
        if d.get("model") != owner.MODEL or d["choices"][0]["finish_reason"] != "stop":
            raise RuntimeError("GPT identity/terminal invalid")
        output = d["choices"][0]["message"]["content"]
    else:
        if d.get("model") != "claude-haiku-5-5" or d.get("stop_reason") != "end_turn":
            raise RuntimeError("Haiku identity/terminal invalid")
        text = [x["text"] for x in d["content"] if x["type"] == "text"]
        assert len(text) == 1
        output = text[0]
    parsed = json.loads(output)
    assert (
        set(parsed) == {"classification"} and parsed["classification"] in owner.LABELS
    )
    ledger = json.loads((R / "ledger.json").read_text())
    receipt = ledger["calls"][-1]
    row = {
        "id": f"r{rep}-{c['id']}",
        "domain": c["domain"],
        "gold": c["gold"],
        "arm": arm,
        "label": parsed["classification"],
        "cost_usd": receipt["cost_usd"],
        "latency_ms": receipt["latency_ms"],
        "sequence": receipt["sequence"],
        "configuration_selection": stage == "consistency-calibration",
    }
    return row


def save(rows):
    (R / "consistency-results.json").write_text(json.dumps(rows, indent=2) + "\n")


def main():
    if (R / "consistency-results.json").exists():
        raise RuntimeError(
            "Refuse to overwrite prior consistency evidence; use a separately authorized run identity"
        )
    rows = []
    # Zero-cost rendered matrix preflight includes only inputs, never golden in payload.
    pre = {
        "fixture_sha256": __import__("hashlib")
        .sha256((B / "jev-consistency/fixtures.json").read_bytes())
        .hexdigest(),
        "cases": 40,
        "unique": 20,
        "arms": ["medium", "low", "high"],
        "calibration_ids": [c["id"] for c in CASES[:5]],
        "instruction": owner.INSTRUCTION,
        "labels": owner.LABELS,
        "schema": owner.SCHEMA,
        "cache": False,
        "concurrency": 1,
        "conversation": "independent system/user",
        "judge": None,
        "max_tokens": 1024,
        "gpt_max_completion_tokens": 160,
    }
    (R / "consistency-preflight.json").write_text(json.dumps(pre, indent=2))
    for arm in ["medium", "low", "high"]:
        for c in CASES[:5]:
            rows.append(call(arm, c, 1, "consistency-calibration"))
            save(rows)
            print(arm, c["id"], rows[-1]["label"], flush=True)
    score = {
        a: owner.metrics([r for r in rows if r["arm"] == a])
        for a in ["medium", "low", "high"]
    }
    winner = min(
        score,
        key=lambda a: (
            score[a]["defects_called_clean"],
            -score[a]["accuracy"],
            score[a]["cost_usd"],
        ),
    )
    (R / "consistency-frozen-selection.json").write_text(
        json.dumps(
            {
                "selected": winner,
                "rule": "fewest dangerous false-clean then highest accuracy then lowest cost",
                "calibration": score,
                "confirmation": "remaining15 plus predeclared repeat20",
            },
            indent=2,
        )
    )
    print("frozen", winner, flush=True)
    for c in CASES[5:]:
        rows.append(call(winner, c, 1, "consistency-confirmation"))
        save(rows)
    for c in CASES:
        rows.append(call(winner, c, 2, "consistency-confirmation"))
        save(rows)
    for rep in [1, 2]:
        for c in CASES:
            rows.append(call("gpt", c, rep, "consistency-control"))
            save(rows)
            print("gpt", rep, c["id"], rows[-1]["label"], flush=True)
    summary = {
        a: owner.metrics([r for r in rows if r["arm"] == a])
        for a in sorted(set(r["arm"] for r in rows))
    }
    summary["selected"] = winner
    summary["confirmation"] = owner.metrics(
        [r for r in rows if r["arm"] == winner and not r["configuration_selection"]]
    )
    (R / "consistency-summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
