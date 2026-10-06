"""Serial campaign guard, below adapters and SDKs, with durable intent receipts."""

import hashlib
import json
import os
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "benchmarks/results/mistral-large4-20261006"
PRICES = {
    "gemini-3.7-flash": (0.75, 0.075, 0.75, 3.75),
    "mistralai/mistral-large-4-0": (0.68, 0.07, 0.68, 2.09),
    "gpt-5.5": (5, 0.5, 5, 30),
    "gemini-3-flash-preview": (0.5, 0.05, 0.5, 3),
}


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2) + "\n")
    temp.chmod(0o600)
    temp.replace(path)


def _guarded_send_unlocked(original, client, request, **kwargs):
    if request.method != "POST":
        return original(client, request, **kwargs)
    body = json.loads(request.content)
    google = request.url.host == "generativelanguage.googleapis.com"
    if google:
        model = request.url.path.split("/models/")[1].split(":")[0]
        maximum = body["generationConfig"]["maxOutputTokens"]
        content = body.get("contents", [])
    elif request.url.host == "api.openai.com" and request.url.path == "/v1/responses":
        model = body["model"]
        maximum = body["max_output_tokens"]
        content = body["input"]
        if body.get("tools") or body.get("store") is not False:
            raise RuntimeError("Unapproved tool or storage contract")
    elif request.url.host == "openrouter.ai" and request.url.path == "/api/v1/chat/completions":
        model = body["model"]
        maximum = body["max_tokens"]
        content = body["messages"]
        if "reasoning" in body or body.get("tools") or body.get("provider", {}).get("max_price") != {"prompt": 0.68, "completion": 2.09}:
            raise RuntimeError("Invalid candidate price/reasoning contract")
    else:
        raise RuntimeError("Unmetered POST denied by image campaign")
    prices = PRICES[model]
    encoded = json.dumps(content)
    images = (
        encoded.count('"type": "image_url"')
        + encoded.count('"input_image"')
        + encoded.count('"inlineData"')
        + encoded.count('"inline_data"')
    )
    if images < 1 or images > 2:
        raise RuntimeError("Campaign requires one or two image inputs")
    # Fixed benchmark envelope: 20k/image plus 6k for text, instructions and schema.
    bound = images * 20000 + 6000
    reserve = (bound * max(prices[:3]) + maximum * prices[3]) / 1e6
    if maximum > (16384 if images == 1 else 4096):
        raise RuntimeError("Output exceeds frozen allowance")
    path = RESULTS / "ledger.json"
    ledger = json.loads(path.read_text())
    exposure = ledger["spent_usd"] + sum(
        c["reserved_usd"] for c in ledger["calls"] if c.get("cost_usd") is None
    )
    if ledger.get("closed") or exposure + reserve > ledger["cap_usd"]:
        raise RuntimeError(
            "Image campaign admission denied: reserve exceeds remaining cap"
        )
    stage = os.environ.get("MISTRAL_STAGE", "unknown")
    case = os.environ.get("MISTRAL_CASE", "unknown")
    recovery = os.environ.get("MISTRAL_RECOVERY") == "1"
    if any(c.get("stage")==stage and c.get("case_key")==case and c["model"]==model for c in ledger["calls"]) and not recovery:
        raise RuntimeError("Duplicate dispatch denied")
    if recovery and sum(c.get("recovery", False) for c in ledger["calls"]) >= 2:
        raise RuntimeError("Two operational recoveries exhausted")
    if len(ledger["calls"]) >= 86:
        raise RuntimeError("Finite campaign call ceiling reached")
    seq = len(ledger["calls"]) + 1
    raw_request = json.dumps(body, sort_keys=True).encode()
    (RESULTS / f"request-{seq:03d}.json").write_bytes(raw_request)
    (RESULTS / f"request-{seq:03d}.json").chmod(0o600)
    record = dict(
        sequence=seq, case_key=case, recovery=recovery,
        model=model,
        reserved_usd=reserve,
        cost_usd=None,
        request_sha256=hashlib.sha256(raw_request).hexdigest(),
        stage=os.environ.get("MISTRAL_STAGE"),
        code_sha256={
            str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest()
            for f in [
                Path(__file__),
                ROOT / "modules/common/openai_client.py",
                ROOT / "modules/common/google_client.py",
                ROOT / "modules/extract/ocr_ai_gpt51_v1/main.py",
            ]
        },
    )
    ledger["calls"].append(record)
    write(path, ledger)
    started = time.monotonic()
    try:
        response = original(client, request, **kwargs)
    except Exception as exc:
        record["transport_exception"] = type(exc).__name__
        write(path, ledger)
        raise
    response.read()
    raw = response.content
    destination = RESULTS / f"response-{seq:03d}.json"
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
        usage = data.get("usageMetadata", {}) if google else data.get("usage", {})
        if google:
            inp = usage["promptTokenCount"]
            out = usage.get("candidatesTokenCount", 0) + usage.get(
                "thoughtsTokenCount", 0
            )
            cache = usage.get("cachedContentTokenCount", 0)
            writes = 0
        elif model == "mistralai/mistral-large-4-0":
            inp, out = usage["prompt_tokens"], usage["completion_tokens"]
            details = usage.get("prompt_tokens_details", {})
            cache, writes = details.get("cached_tokens", 0), 0
        else:
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
            raise ValueError("invalid usage")
        cost = (
            (inp - cache - writes) * prices[0]
            + cache * prices[1]
            + writes * prices[2]
            + out * prices[3]
        ) / 1e6
        if model == "mistralai/mistral-large-4-0":
            cost = usage["cost"]
            if not isinstance(cost, (int,float)) or cost < 0:
                raise ValueError("Invalid router cost")
        record.update(
            cost_usd=cost,
            usage=usage,
            served_model=data.get("modelVersion", data.get("model")), served_provider=data.get("provider"),
            response_id=data.get("responseId", data.get("id")),
        )
        ledger["spent_usd"] += cost
        if inp > bound or out > maximum or cost > reserve:
            ledger["closed"] = True
            record["bound_violation"] = True
    except (KeyError, ValueError, TypeError):
        record["billing_unresolved"] = True
    ledger["calls"][-1] = record
    write(path, ledger)
    return response


def guarded_send(original, client, request, **kwargs):
    import fcntl
    RESULTS.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (RESULTS / "dispatch.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return _guarded_send_unlocked(original, client, request, **kwargs)


def install():
    libraries = [httpx]
    try:
        import httpx2

        libraries.append(httpx2)
    except ImportError:
        pass
    for library in libraries:
        if getattr(library.Client.send, "_image_guard", False):
            continue
        original = library.Client.send

        def send(client, request, _original=original, **kwargs):
            return guarded_send(_original, client, request, **kwargs)

        send._image_guard = True
        library.Client.send = send
