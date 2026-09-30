"""Serial campaign guard, below adapters and SDKs, with durable intent receipts."""

import hashlib
import json
import os
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "benchmarks/results/thinking-safety-20260929"
PRICES = {
    "gemini-3.7-flash": (0.75, 0.075, 0.75, 3.75),
    "gpt-6.1-sol": (2, 0.1, 2.5, 10),
    "gpt-6-luna": (0.1, 0.01, 0.125, 0.5),
    "gpt-5.5": (5, 0.5, 5, 30),
    "gemini-3-flash-preview": (0.5, 0.05, 0.5, 3),
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
    else:
        raise RuntimeError("Unmetered POST denied by image campaign")
    prices = PRICES[model]
    encoded = json.dumps(content)
    images = (
        encoded.count('"image"')
        + encoded.count('"input_image"')
        + encoded.count('"inlineData"')
        + encoded.count('"inline_data"')
    )
    if images < 1 or images > 2:
        raise RuntimeError("Campaign requires one or two image inputs")
    # Fixed benchmark envelope: 20k/image plus 6k for text, instructions and schema.
    bound = images * 20000 + 6000
    reserve = (bound * max(prices[:3]) + maximum * prices[3]) / 1e6
    path = RESULTS / "ledger.json"
    ledger = json.loads(path.read_text())
    exposure = ledger["spent_usd"] + sum(
        c["reserved_usd"] for c in ledger["calls"] if c.get("cost_usd") is None
    )
    if ledger.get("closed") or exposure + reserve > ledger["cap_usd"]:
        raise RuntimeError(
            "Image campaign admission denied: reserve exceeds remaining cap"
        )
    seq = len(ledger["calls"]) + 1
    raw_request = json.dumps(body, sort_keys=True).encode()
    (RESULTS / f"request-{seq:03d}.json").write_bytes(raw_request)
    (RESULTS / f"request-{seq:03d}.json").chmod(0o600)
    record = dict(
        sequence=seq,
        model=model,
        reserved_usd=reserve,
        cost_usd=None,
        request_sha256=hashlib.sha256(raw_request).hexdigest(),
        stage=os.environ.get("THINKING_SAFETY_STAGE"),
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
    response = original(client, request, **kwargs)
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
        record.update(
            cost_usd=cost,
            usage=usage,
            served_model=data.get("modelVersion", data.get("model")),
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
