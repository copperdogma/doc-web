# ruff: noqa: E402
"""Selected six source-adjudicated page-context cases only."""

import json
import os
import sys
from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "benchmarks/scripts"))
import carbon_native as native
import carbon_reading as reading
import scout096_safety as safety
from carbon_preflight import safety_body, KEYS

E = ROOT / "docs/evals/evidence/089-carbon"


def run(key, arm):
    if key not in KEYS or arm not in ["candidate", "control"]:
        raise ValueError("unselected case")
    stage = f"safety-{key}-{arm}"
    golden = json.loads(safety.GOLDEN.read_text())
    if arm == "candidate":
        raw, d = native.send("gemini-4-carbon", safety_body(key), stage)
        parsed = json.loads(raw)
    else:
        os.environ["CARBON_STAGE"] = stage
        native.guard.install()
        b = safety.body(key, "control")
        b.update(store=False, service_tier="default")
        r = httpx.post(
            "https://api.openai.com/v1/responses",
            headers={"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]},
            json=b,
            timeout=900,
        )
        r.raise_for_status()
        d = r.json()
        safety.parse("control", d)
        if (
            d.get("status") != "completed"
            or d.get("incomplete_details")
            or d.get("error")
        ):
            raise ValueError("control nonterminal")
        texts = [
            c["text"]
            for o in d["output"]
            if o.get("type") == "message"
            for c in o["content"]
            if c.get("type") == "output_text"
        ]
        if len(texts) != 1:
            raise ValueError("control final output")
        raw = texts[0]
        parsed = json.loads(raw)
    error = safety.helper.owner._contract_error(raw, "page_context_validation")
    if error:
        raise ValueError(error)
    rec = next(
        x
        for x in json.loads((native.guard.RESULTS / "ledger.json").read_text())["calls"]
        if x["stage"] == stage
    )
    row = {
        "key": key,
        "arm": arm,
        "raw": raw,
        "parsed": parsed,
        "verdict": parsed["verdict"],
        "golden": golden[key]["verdict"],
        "correct": parsed["verdict"] == golden[key]["verdict"],
        "false_safe": parsed["verdict"] == "pass" and golden[key]["verdict"] == "fail",
        "cost_usd": rec["cost_usd"],
        "latency_ms": rec["latency_ms"],
        "served": rec["served_model"],
        "native_contract": True,
        "rendered_payload_parity": True,
    }
    path = E / f"safety-{key}.json"
    rows = json.loads(path.read_text()) if path.exists() else []
    rows.append(row)
    reading.save(path, rows)
    print(json.dumps(row), flush=True)


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
