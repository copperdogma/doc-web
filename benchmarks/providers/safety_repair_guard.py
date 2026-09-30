"""Serial Attempt048 guard: new run identity, raw receipts, money/call admission."""

import hashlib
import json
import os
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
RUN_ID = os.environ.get("SAFETY_REPAIR_RUN_ID", "safety-repair-048-20260929")
if not RUN_ID.replace("-", "").isalnum() or RUN_ID == "thinking-safety-20260929":
    raise RuntimeError("Invalid or historical run identity")
RESULTS = ROOT / "benchmarks/results" / RUN_ID
PRICES = {
    "gpt-6-luna": (0.1, 0.01, 0.125, 0.5),
    "gpt-6.1-sol": (2, 0.1, 2.5, 10),
    "gpt-5.5": (5, 0.5, 5, 30),
}
SETTINGS = {
    "gpt-6-luna": ("medium", 4096, "high"),
    "gpt-6.1-sol": ("medium", 4096, "high"),
    "gpt-5.5": ("none", 2048, "auto"),
}


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2) + "\n")
    temp.chmod(0o600)
    temp.replace(path)


def guarded_send(original, client, request, **kwargs):
    if request.method != "POST":
        return original(client, request, **kwargs)
    if request.url.host != "api.openai.com" or request.url.path != "/v1/responses":
        raise RuntimeError("Unmetered endpoint denied")
    if (
        "continuation" in RUN_ID
        and os.environ.get("PROMPTFOO_DISABLE_ADAPTIVE_SCHEDULER") != "true"
    ):
        raise RuntimeError("Continuation requires disabled adaptive scheduler")
    body = json.loads(request.content)
    model = body["model"]
    if (
        hashlib.sha256(
            (ROOT / "benchmarks/prompts/validate-page-level-crop.js").read_bytes()
        ).hexdigest()
        != "ef4395838929b208fe65f21500d81ade902072bef3f8e53f81ef3d3b83fbc421"
    ):
        raise RuntimeError("Frozen repaired prompt changed")
    effort, maximum, detail = SETTINGS[model]
    if (
        body.get("tools")
        or body.get("store") is not False
        or body.get("reasoning", {}).get("effort") != effort
        or body["max_output_tokens"] != maximum
    ):
        raise RuntimeError("Unapproved arm contract")
    messages = body["input"]
    blocks = messages[0]["content"]
    images = [x for x in blocks if x["type"] == "input_image"]
    if (
        len(messages) != 1
        or messages[0]["role"] != "user"
        or len(images) != 2
        or any(x["detail"] != detail for x in images)
    ):
        raise RuntimeError("Invalid two-image topology/detail")
    texts = [x["text"] for x in blocks if x["type"] == "input_text"]
    text_bytes = len(("".join(texts) + json.dumps(body["text"])).encode())
    if text_bytes > 6000 or body["text"]["format"].get("strict") is not True:
        raise RuntimeError("Text/schema token bound or strict contract invalid")
    bound = 46000
    prices = PRICES[model]
    reserve = (bound * max(prices[:3]) + maximum * prices[3]) / 1e6
    path = RESULTS / "ledger.json"
    ledger = json.loads(path.read_text())
    recovery = os.environ.get("SAFETY_REPAIR_RECOVERY") == "1"
    if not recovery and any(
        c.get("model") == model
        and c.get("stage") == os.environ.get("SAFETY_REPAIR_STAGE")
        and c.get("case_key") == os.environ.get("SAFETY_REPAIR_CASE")
        for c in ledger["calls"]
    ):
        raise RuntimeError(
            "Duplicate subject dispatch denied; explicit recovery required"
        )
    if (
        not recovery
        and sum(
            c.get("model") == model and not c.get("recovery") for c in ledger["calls"]
        )
        >= 35
    ):
        raise RuntimeError("Per-arm admission denied before transport")
    count = sum(bool(c.get("recovery")) == recovery for c in ledger["calls"])
    if count >= (2 if recovery else 105) or len(ledger["calls"]) >= 107:
        raise RuntimeError("Call/recovery admission denied before transport")
    exposure = ledger["spent_usd"] + sum(
        c["reserved_usd"] for c in ledger["calls"] if c.get("cost_usd") is None
    )
    if ledger.get("closed") or exposure + reserve > ledger["cap_usd"]:
        raise RuntimeError("Dollar admission denied before transport")
    sequence = len(ledger["calls"]) + 1
    raw_request = json.dumps(body, sort_keys=True).encode()
    record = {
        "sequence": sequence,
        "model": model,
        "effort": effort,
        "recovery": recovery,
        "stage": os.environ.get("SAFETY_REPAIR_STAGE"),
        "case_key": os.environ.get("SAFETY_REPAIR_CASE"),
        "reserved_usd": reserve,
        "cost_usd": None,
        "request_sha256": hashlib.sha256(raw_request).hexdigest(),
        "code_sha256": {
            str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest()
            for f in [
                Path(__file__),
                ROOT / "benchmarks/providers/openai_responses_model.py",
                ROOT / "benchmarks/providers/safety_repair_openai.py",
                ROOT / "benchmarks/prompts/validate-page-level-crop.js",
                ROOT / "benchmarks/scorers/crop_validation_scorer.py",
            ]
        },
    }
    intent = RESULTS / f"request-{sequence:03d}.json"
    intent.write_bytes(raw_request)
    intent.chmod(0o600)
    ledger["calls"].append(record)
    write(path, ledger)
    started = time.monotonic()
    try:
        response = original(client, request, **kwargs)
        response.read()
    except Exception as exc:
        record.update(
            transport_exception=type(exc).__name__,
            latency_ms=round((time.monotonic() - started) * 1000),
        )
        write(path, ledger)
        raise
    raw = response.content
    destination = RESULTS / f"response-{sequence:03d}.json"
    destination.write_bytes(raw)
    destination.chmod(0o600)
    record.update(
        response_sha256=hashlib.sha256(raw).hexdigest(),
        response_bytes=len(raw),
        status_code=response.status_code,
        latency_ms=round((time.monotonic() - started) * 1000),
    )
    try:
        data = json.loads(raw)
        error = data.get("error", {})
        if isinstance(error, dict) and (
            error.get("type") == "insufficient_quota"
            or error.get("code") == "credit_balance_exhausted"
        ):
            ledger["closed"] = True
            ledger["stop_reason"] = "Provider account quota exhausted"
        usage = data["usage"]
        inp, out = usage["input_tokens"], usage["output_tokens"]
        details = usage.get("input_tokens_details", {})
        cache, writes = (
            details.get("cached_tokens", 0),
            details.get("cache_write_tokens", 0),
        )
        if (
            any(type(x) is not int or x < 0 for x in (inp, out, cache, writes))
            or cache + writes > inp
        ):
            raise ValueError("Invalid usage")
        cost = (
            (inp - cache - writes) * prices[0]
            + cache * prices[1]
            + writes * prices[2]
            + out * prices[3]
        ) / 1e6
        record.update(
            cost_usd=cost,
            usage=usage,
            served_model=data.get("model"),
            response_id=data.get("id"),
            response_status=data.get("status"),
        )
        ledger["spent_usd"] += cost
        if inp > bound or out > maximum or cost > reserve:
            ledger["closed"] = True
            record["bound_violation"] = True
    except (KeyError, ValueError, TypeError):
        record["billing_unresolved"] = True
    write(path, ledger)
    return response


def install():
    libraries = [httpx]
    try:
        import httpx2

        libraries.append(httpx2)
    except ImportError:
        pass
    for library in libraries:
        if getattr(library.Client.send, "_safety_repair_guard", False):
            continue
        original = library.Client.send

        def send(client, request, _original=original, **kwargs):
            return guarded_send(_original, client, request, **kwargs)

        send._safety_repair_guard = True
        library.Client.send = send
