"""Campaign-only serial spend guard and full-envelope recorder; no prompt changes."""

import hashlib
import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import openrouter_vision_chat as owner

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/qwen0902-20260906"
_REAL_POST = owner.httpx.post


def recorded_post(url, **kwargs):
    body = kwargs["json"]
    ledger_path = RESULTS / "ledger.json"
    ledger = json.loads(ledger_path.read_text())
    # Preflight restricts <=2 downscaled images and <10k text bytes per request.
    # 50k input tokens at the highest published input price incl cache writes,
    # plus the hard completion limit, deliberately overbounds this small lane.
    reserve = 50000 * 0.0000025 + body["max_tokens"] * 0.000006
    if ledger["spent_usd"] + reserve > ledger["cap_usd"]:
        raise RuntimeError(
            "Campaign budget guard: conservative call reserve does not fit"
        )
    if ledger.get("unresolved_cost"):
        raise RuntimeError("Campaign stopped: previous call cost unresolved")
    seq = len(ledger["calls"]) + 1
    start = time.monotonic()
    request = json.dumps(body, sort_keys=True)
    record = {
        "sequence": seq,
        "request_sha256": hashlib.sha256(request.encode()).hexdigest(),
        "reserved_usd": reserve,
    }
    # Write intent before network; unknown costs fail closed on the next call.
    ledger["unresolved_cost"] = True
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n")
    response = _REAL_POST(url, **kwargs)
    data = response.json()
    record.update(
        status_code=response.status_code,
        latency_ms=round((time.monotonic() - start) * 1000),
        response=data,
    )
    raw = RESULTS / f"call-{seq:03d}.json"
    raw.write_text(json.dumps(record, indent=2) + "\n")
    raw.chmod(0o600)
    usage = data.get("usage", {})
    cost = usage.get("cost")
    if response.status_code >= 400 and not usage:
        cost = 0
    if (
        isinstance(cost, (float, int))
        and not isinstance(cost, bool)
        and math.isfinite(cost)
        and cost >= 0
    ):
        ledger["spent_usd"] += cost
        ledger["unresolved_cost"] = False
    ledger["calls"].append(
        {
            "sequence": seq,
            "path": str(raw.relative_to(ROOT.parent)),
            "cost_usd": cost,
            "status_code": response.status_code,
            "latency_ms": record["latency_ms"],
        }
    )
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n")
    return response


def call_api(prompt, options, context):
    owner.httpx.post = recorded_post
    try:
        return owner.call_api(prompt, options, context)
    finally:
        owner.httpx.post = _REAL_POST
