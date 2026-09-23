"""Campaign-only MiMo 2.6 spend guard and raw-envelope recorder."""

from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path

import openrouter_vision_chat as owner

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/mimo26-20260922"
_REAL_POST = owner.httpx.post


def _reserve_usd(body: dict) -> float:
    # Each bound covers 50k image/input tokens plus a 2048-token response at
    # the more expensive selected candidate's public rate.
    return 50_000 * 0.000000435 + body["max_tokens"] * 0.00000087


def recorded_post(url, **kwargs):
    body = kwargs["json"]
    ledger_path = RESULTS / "ledger.json"
    ledger = json.loads(ledger_path.read_text())
    reserve = _reserve_usd(body)
    if ledger["spent_usd"] + reserve > ledger["cap_usd"]:
        raise RuntimeError("Campaign budget guard: conservative call reserve does not fit")
    if ledger.get("unresolved_cost") or ledger.get("terminal_stop"):
        raise RuntimeError("Campaign stopped: previous call cost unresolved")
    sequence = len(ledger["calls"]) + 1
    request = json.dumps(body, sort_keys=True)
    record = {"sequence": sequence, "request_sha256": hashlib.sha256(request.encode()).hexdigest(), "reserved_usd": reserve, "request": body}
    ledger["unresolved_cost"] = True
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n")
    started = time.monotonic()
    try:
        response = _REAL_POST(url, **kwargs)
    except Exception as exc:
        record.update(status_code=None, latency_ms=round((time.monotonic() - started) * 1000), error=f"{type(exc).__name__}: {exc}")
        raw_path = RESULTS / f"call-{sequence:03d}.json"
        raw_path.write_text(json.dumps(record, indent=2) + "\n")
        raw_path.chmod(0o600)
        ledger["reserved_unresolved_usd"] = ledger.get("reserved_unresolved_usd", 0) + reserve
        ledger["calls"].append({"sequence": sequence, "path": str(raw_path.relative_to(ROOT.parent)), "cost_usd": None, "status_code": None, "latency_ms": record["latency_ms"], "reserved_unresolved_usd": reserve})
        ledger_path.write_text(json.dumps(ledger, indent=2) + "\n")
        raise
    try:
        data = response.json()
    except Exception:
        data = {"_unparseable": response.text}
    record.update(status_code=response.status_code, latency_ms=round((time.monotonic() - started) * 1000), response=data)
    raw_path = RESULTS / f"call-{sequence:03d}.json"
    raw_path.write_text(json.dumps(record, indent=2) + "\n")
    raw_path.chmod(0o600)
    usage = data.get("usage", {}) if isinstance(data, dict) else {}
    cost = usage.get("cost")
    if isinstance(cost, (int, float)) and not isinstance(cost, bool) and math.isfinite(cost) and cost >= 0:
        ledger["spent_usd"] += cost
        ledger["unresolved_cost"] = False
    else:
        ledger["reserved_unresolved_usd"] = ledger.get("reserved_unresolved_usd", 0) + reserve
        ledger["terminal_stop"] = "missing attributable usage/cost"
    ledger["calls"].append({"sequence": sequence, "path": str(raw_path.relative_to(ROOT.parent)), "cost_usd": cost, "status_code": response.status_code, "latency_ms": record["latency_ms"], "reserved_unresolved_usd": 0 if isinstance(cost, (int, float)) and not isinstance(cost, bool) and math.isfinite(cost) and cost >= 0 else reserve})
    if response.status_code >= 400:
        ledger["terminal_stop"] = f"HTTP {response.status_code} without retry authorization"
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n")
    return response


def call_api(prompt, options, context):
    owner.httpx.post = recorded_post
    try:
        return owner.call_api(prompt, options, context)
    finally:
        owner.httpx.post = _REAL_POST
