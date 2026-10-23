"""Fresh DeepSeek V4.1 Flash campaign guard for 2026-10-14.

Uses the maintained OpenRouter owner adapter and frozen crop contract. The
serial ledger reserves worst-case input/output cost before every request,
retains complete response bodies before parsing, and holds a reservation when
usage is missing.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import openrouter_vision_chat as owner

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "deepseek-v41-fresh-20261014"
RESULTS = ROOT / "results" / RUN_ID
CAMPAIGN_CAP_USD = 0.50
PROTECTED_GEMINI_CONTROL_USD = 0.06
MAX_INPUT_TOKENS_PER_REQUEST = 50_000
INPUT_USD_PER_TOKEN = 0.0000002
OUTPUT_USD_PER_TOKEN = 0.0000006
EXPECTED_MODEL = "deepseek/deepseek-v4.1-flash"
EXPECTED_PROVIDER = "DeepInfra"
EXPECTED_ROUTE = "deepinfra/fp8"
OUTPUT_LIMIT = 16384
_REAL_POST = owner.httpx.post


def _reserve(body: dict[str, Any]) -> float:
    if body.get("model") != EXPECTED_MODEL:
        raise RuntimeError("budget guard rejected unexpected model")
    if body.get("max_tokens") != OUTPUT_LIMIT:
        raise RuntimeError("budget guard rejected changed output allowance")
    if body.get("reasoning") != {"exclude": True, "effort": "low"}:
        raise RuntimeError("budget guard rejected changed reasoning configuration")
    provider = body.get("provider")
    if not isinstance(provider, dict) or provider.get("order") != [EXPECTED_ROUTE]:
        raise RuntimeError("budget guard rejected changed provider route")
    if provider.get("allow_fallbacks") is not False or provider.get("require_parameters") is not True:
        raise RuntimeError("budget guard rejected fallback/parameter policy")
    messages = body.get("messages")
    if not isinstance(messages, list) or len(messages) != 1:
        raise RuntimeError("budget guard permits one independent user message")
    content = messages[0].get("content")
    if not isinstance(content, list):
        raise RuntimeError("budget guard expected image-bearing content blocks")
    images = [b for b in content if isinstance(b, dict) and b.get("type") == "image_url"]
    texts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
    if len(images) != 1 or len(texts) != 1 or len(texts[0].encode("utf-8")) > 10_000:
        raise RuntimeError("budget guard permits one image and <10,000 text bytes")
    image_url = images[0].get("image_url", {}).get("url", "")
    if not isinstance(image_url, str) or not image_url.startswith("data:image/"):
        raise RuntimeError("budget guard permits only embedded owner-approved image fixtures")
    if not isinstance(body.get("response_format"), dict):
        raise RuntimeError("budget guard requires the strict structured-output request")
    return (
        MAX_INPUT_TOKENS_PER_REQUEST * INPUT_USD_PER_TOKEN
        + OUTPUT_LIMIT * OUTPUT_USD_PER_TOKEN
    )


def recorded_post(url: str, **kwargs: Any):
    if url != "https://openrouter.ai/api/v1/chat/completions":
        raise RuntimeError("budget guard rejected unexpected endpoint")
    body = kwargs.get("json")
    if not isinstance(body, dict):
        raise RuntimeError("budget guard requires a JSON request body")
    reserve = _reserve(body)
    ledger_path = RESULTS / "ledger.json"
    ledger = json.loads(ledger_path.read_text())
    if ledger.get("closed"):
        raise RuntimeError("campaign closed; use the approved fresh run identity")
    held = float(ledger.get("unresolved_reserved_usd", 0.0))
    control = float(ledger.get("protected_comparator_reserve_usd", 0.0))
    spent = float(ledger.get("spent_usd", 0.0))
    if spent + held + reserve + control > CAMPAIGN_CAP_USD + 1e-12:
        raise RuntimeError("campaign hard-cap reserve does not fit")

    seq = len(ledger["calls"]) + 1
    request_text = json.dumps(body, sort_keys=True, separators=(",", ":"))
    request_sha = hashlib.sha256(request_text.encode()).hexdigest()
    request_path = RESULTS / f"request-{seq:03d}.json"
    request_path.write_text(request_text + "\n")
    request_path.chmod(0o600)
    ledger["unresolved_reserved_usd"] = held + reserve
    ledger["calls"].append({
        "sequence": seq,
        "request_path": str(request_path.relative_to(ROOT.parent)),
        "request_sha256": request_sha,
        "reserved_usd": reserve,
        "status": "request_sent_or_pending",
        "cost_usd": None,
    })
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n")

    start = time.monotonic()
    try:
        response = _REAL_POST(url, **kwargs)
    except Exception as exc:
        ledger = json.loads(ledger_path.read_text())
        ledger["calls"][-1].update({
            "status": "transport_exception",
            "latency_ms": round((time.monotonic() - start) * 1000),
            "exception_type": type(exc).__name__,
        })
        ledger_path.write_text(json.dumps(ledger, indent=2) + "\n")
        raise

    latency_ms = round((time.monotonic() - start) * 1000)
    raw_path = RESULTS / f"response-{seq:03d}.json"
    raw_path.write_text(json.dumps({
        "sequence": seq,
        "request_sha256": request_sha,
        "status_code": response.status_code,
        "latency_ms": latency_ms,
        "response_text": response.text,
    }, indent=2) + "\n")
    raw_path.chmod(0o600)

    try:
        data = response.json()
    except Exception:
        data = None
    usage = data.get("usage") if isinstance(data, dict) else None
    cost = usage.get("cost") if isinstance(usage, dict) else None
    known_cost = (
        isinstance(cost, (int, float))
        and not isinstance(cost, bool)
        and math.isfinite(cost)
        and cost >= 0
    )
    ledger = json.loads(ledger_path.read_text())
    call = ledger["calls"][-1]
    call.update({
        "response_path": str(raw_path.relative_to(ROOT.parent)),
        "status_code": response.status_code,
        "latency_ms": latency_ms,
        "cost_usd": float(cost) if known_cost else None,
        "response_sha256": hashlib.sha256(response.content).hexdigest(),
    })
    ledger["unresolved_reserved_usd"] = max(0.0, float(ledger["unresolved_reserved_usd"]) - reserve)
    if known_cost:
        ledger["spent_usd"] = spent + float(cost)
        call["status"] = "usage_known"
    else:
        ledger["unresolved_reserved_usd"] = float(ledger["unresolved_reserved_usd"]) + reserve
        call["status"] = "usage_unknown_reserved"
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n")
    return response


def call_api(prompt: str, options: dict[str, Any], context: dict[str, Any]):
    owner.httpx.post = recorded_post
    try:
        return owner.call_api(prompt, options, context)
    finally:
        owner.httpx.post = _REAL_POST
