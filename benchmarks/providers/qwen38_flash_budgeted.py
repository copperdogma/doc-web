"""Campaign-only Qwen3.8 Flash spend guard and raw-envelope recorder."""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import openrouter_vision_chat as owner  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/qwen38-flash-20260913"
_REAL_POST = owner.httpx.post


def _reserve_usd(body: dict) -> float:
    """Conservatively reserve one public crop request before network use."""
    # The preflight limits requests to one downscaled checked-in image and less
    # than 10k prompt bytes. This deliberately reserves 50k input tokens at the
    # highest listed cache-write price plus the requested output limit at the
    # current completion price.
    return 50_000 * 0.0000002 + body["max_tokens"] * 0.00000047


def recorded_post(url, **kwargs):
    body = kwargs["json"]
    ledger_path = RESULTS / "ledger.json"
    ledger = json.loads(ledger_path.read_text())
    reserve = _reserve_usd(body)
    if ledger["spent_usd"] + reserve > ledger["cap_usd"]:
        raise RuntimeError("Campaign budget guard: conservative call reserve does not fit")
    if ledger.get("unresolved_cost"):
        raise RuntimeError("Campaign stopped: previous call cost unresolved")

    sequence = len(ledger["calls"]) + 1
    request_text = json.dumps(body, sort_keys=True)
    record = {
        "sequence": sequence,
        "request_sha256": hashlib.sha256(request_text.encode()).hexdigest(),
        "reserved_usd": reserve,
        "request": body,
    }
    ledger["unresolved_cost"] = True
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n")

    started = time.monotonic()
    response = _REAL_POST(url, **kwargs)
    data = response.json()
    record.update(
        status_code=response.status_code,
        latency_ms=round((time.monotonic() - started) * 1000),
        response=data,
    )
    raw_path = RESULTS / f"call-{sequence:03d}.json"
    raw_path.write_text(json.dumps(record, indent=2) + "\n")
    raw_path.chmod(0o600)

    usage = data.get("usage", {}) if isinstance(data, dict) else {}
    cost = usage.get("cost")
    if response.status_code >= 400 and not usage:
        cost = 0
    if (
        isinstance(cost, (int, float))
        and not isinstance(cost, bool)
        and math.isfinite(cost)
        and cost >= 0
    ):
        ledger["spent_usd"] += cost
        ledger["unresolved_cost"] = False
    ledger["calls"].append(
        {
            "sequence": sequence,
            "path": str(raw_path.relative_to(ROOT.parent)),
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
