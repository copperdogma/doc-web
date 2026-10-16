"""Scout096 serialized owner ledger with durable lossless receipts."""

import fcntl
import hashlib
import json
import os
import time
from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / os.environ.get(
    "SCOUT096_RESULTS", "benchmarks/results/scout096-20261016"
)
E = ROOT / os.environ.get("SCOUT096_EVIDENCE", "docs/evals/evidence/078-scout096")
PRICES = {
    "gpt-6-astra": (10, 1, 12.5, 50),
    "gpt-5.5": (5, 0.5, 5, 30),
    "gemini-3-flash-preview": (0.5, 0.05, 0.5, 3),
    "gemini-3.7-flash": (0.75, 0.075, 0.75, 3.75),
}


def save(p, d):
    p.parent.mkdir(parents=True, exist_ok=True)
    t = p.with_suffix(p.suffix + ".tmp")
    t.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    t.replace(p)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def send(original, client, request, **kwargs):
    if request.method != "POST":
        return original(client, request, **kwargs)
    b = json.loads(request.content)
    router = request.url.host == "openrouter.ai"
    google = request.url.host == "generativelanguage.googleapis.com"
    model = (
        request.url.path.split("/models/")[1].split(":")[0] if google else b["model"]
    )
    if router:
        if model not in [
            "nvidia/nemotron-3.5-super-vl",
            "liquid/d1-ultra",
            "respan/span-02",
        ]:
            raise RuntimeError("unapproved model")
        maximum = b.get("max_tokens", 0)
        bound = (
            262144
            if model.startswith("nvidia")
            else (32768 if model.startswith("liquid") else 131072)
        )
        rate = (
            0.15
            if model.startswith("nvidia")
            else (0.042 if model.startswith("liquid") else 0.01)
        )
        reserve = (bound * rate + maximum * 0.5) / 1e6
    else:
        prices = PRICES[model]
        maximum = (
            b["generationConfig"]["maxOutputTokens"]
            if google
            else b["max_output_tokens"]
        )
        count = json.dumps(b).count('"input_image"') + json.dumps(b).count(
            '"inlineData"'
        )
        bound = 20000 * count + 6000
        reserve = (bound * max(prices[:3]) + maximum * prices[3]) / 1e6
    RESULTS.mkdir(parents=True, exist_ok=True)
    lockpath = (
        Path("/Users/cam/.local/share/conductor-evals/scout096-router.lock")
        if router
        else RESULTS / "dispatch.lock"
    )
    lockpath.parent.mkdir(parents=True, exist_ok=True)
    with lockpath.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        # Local ledger lock also serializes router and native calls from separate workers.
        with (RESULTS / "ledger.lock").open("a") as local:
            fcntl.flock(local, fcntl.LOCK_EX)
            p = RESULTS / "ledger.json"
            ledger = json.loads(p.read_text())
            stage = os.environ["SCOUT096_STAGE"]
            if (
                ledger["closed"]
                or ledger["spent_usd"]
                + sum(
                    x["reserved_usd"]
                    for x in ledger["calls"]
                    if x.get("cost_usd") is None
                )
                + reserve
                > 15
            ):
                raise RuntimeError("cap admission denied")
            if any(x["stage"] == stage for x in ledger["calls"]):
                raise RuntimeError("duplicate stage")
            n = len(ledger["calls"]) + 1
            raw = json.dumps(b, sort_keys=True).encode()
            req = RESULTS / f"request-{n:03}.json"
            res = RESULTS / f"response-{n:03}.json"
            with req.open("xb") as f:
                f.write(raw)
            rec = {
                "stage": stage,
                "model": model,
                "reserved_usd": reserve,
                "cost_usd": None,
                "request": str(req.relative_to(ROOT)),
                "request_sha256": sha(raw),
            }
            ledger["calls"].append(rec)
            save(p, ledger)
            start = time.monotonic()
            try:
                r = original(client, request, **kwargs)
                r.read()
            except Exception as exc:
                rec["exception"] = type(exc).__name__
                save(p, ledger)
                raise
            with res.open("xb") as f:
                f.write(r.content)
            rec.update(
                response=str(res.relative_to(ROOT)),
                response_sha256=sha(r.content),
                status_code=r.status_code,
                latency_ms=round((time.monotonic() - start) * 1000),
            )
            d = r.json()
            u = d.get("usageMetadata", {}) if google else d.get("usage", {})
            try:
                if router:
                    inp, out, cost = (
                        u.get("prompt_tokens", u.get("input_tokens")),
                        u.get("completion_tokens", u.get("output_tokens", 0)),
                        u["cost"],
                    )
                elif google:
                    inp = u["promptTokenCount"]
                    out = u.get("candidatesTokenCount", 0) + u.get(
                        "thoughtsTokenCount", 0
                    )
                    cached = u.get("cachedContentTokenCount", 0)
                    cost = (
                        (inp - cached) * prices[0]
                        + cached * prices[1]
                        + out * prices[3]
                    ) / 1e6
                else:
                    inp, out = u["input_tokens"], u["output_tokens"]
                    det = u.get("input_tokens_details", {})
                    c, w = det.get("cached_tokens", 0), det.get("cache_write_tokens", 0)
                    cost = (
                        (inp - c - w) * prices[0]
                        + c * prices[1]
                        + w * prices[2]
                        + out * prices[3]
                    ) / 1e6
                assert (
                    type(inp) is int
                    and type(out) is int
                    and type(cost) in (float, int)
                    and cost >= 0
                )
                rec.update(
                    cost_usd=cost,
                    usage=u,
                    served_model=d.get("modelVersion", d.get("model")),
                    provider=d.get("provider", "Google" if google else "OpenAI"),
                )
                ledger["spent_usd"] += cost
                if inp > bound or (maximum and out > maximum) or cost > reserve:
                    rec["bound_violation"] = True
                    ledger["closed"] = True
            except (KeyError, AssertionError, TypeError):
                rec["billing_unresolved"] = True
            save(p, ledger)
            return r


def install():
    if getattr(httpx.Client.send, "_scout096", False):
        return
    original = httpx.Client.send

    def wrapped(c, r, **k):
        return send(original, c, r, **k)

    wrapped._scout096 = True
    httpx.Client.send = wrapped
