"""Scout096 serialized owner ledger with durable lossless receipts."""

import fcntl
import hashlib
import json
import os
import time
import re
from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / os.environ.get(
    "SCOUT099_RESULTS", "benchmarks/results/scout099-20261020"
)
E = ROOT / os.environ.get("SCOUT099_EVIDENCE", "docs/evals/evidence/080-scout099")
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
        if model != "minimax/minimax-m3.1-flash:free":
            raise RuntimeError("unapproved model")
        routing = b.get("provider", {})
        if (routing.get("only") != ["minimax"]
            or routing.get("allow_fallbacks") is not False
            or routing.get("max_price") != {"prompt": 0, "completion": 0}):
            raise RuntimeError("free exact-provider price/fallback contract absent")
        maximum = b.get("max_tokens", 0)
        encoded = json.dumps(b)
        count = encoded.count('"image_url": {')
        bound = 20000 * count + 6000
        reserve = 0.0  # Exact pinned free endpoint; nonzero price forbidden in payload
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
        reserve = max(
            1.5 if model == "gpt-6-astra" else 0,
            (bound * max(prices[:3]) + maximum * prices[3]) / 1e6,
        )
    RESULTS.mkdir(parents=True, exist_ok=True)
    lockpath = (
        RESULTS / "router.lock"
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
            stage = os.environ["SCOUT099_STAGE"]

            # An explicit, persisted owner review is required before advancing a
            # progressive crop/safety case. Scorer success cannot bypass this.
            def review_key(value):
                if value.startswith("crop-"):
                    match = re.search(r"Image[0-9]+", value)
                    return "crop-" + match.group() if match else None
                if value.startswith("safety-"):
                    match = re.search(r"page-[0-9]+-[0-9]+", value)
                    return "safety-" + match.group() if match else None
                return None

            current_review = review_key(stage)
            if current_review:
                review_path = E / "source-review.json"
                reviews = (
                    json.loads(review_path.read_text()) if review_path.exists() else {}
                )
                for prior in ledger["calls"]:
                    previous = review_key(prior["stage"])
                    if (
                        previous
                        and previous != current_review
                        and previous.split("-", 1)[0] == current_review.split("-", 1)[0]
                    ):
                        if reviews.get(previous, {}).get("status") != "pass":
                            raise RuntimeError(
                                "source-review barrier denies next progressive case"
                            )
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
            if router:
                stamp = RESULTS / "last-router-start.txt"
                wait = max(0.0, 10.0 - (time.time() - float(stamp.read_text()))) if stamp.exists() else 0.0
                if wait:
                    time.sleep(wait)
                rec["admission_wait_ms"] = round(wait * 1000)
                stamp.write_text(str(time.time()))
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
                # Router reasoning is a breakdown of completion, not additive.
                # Preserve the raw envelope and reported charge before rejecting.
                if router:
                    reasoning = u.get("completion_tokens_details", {}).get(
                        "reasoning_tokens", 0
                    )
                    total = u.get("total_tokens")
                    if (
                        type(reasoning) is not int
                        or reasoning < 0
                        or reasoning > out
                        or (total is not None and total != inp + out)
                    ):
                        rec["accounting_valid"] = False
                        rec["accounting_error"] = (
                            "reasoning/completion breakdown or total contradiction"
                        )
                        ledger["closed"] = True
                        save(p, ledger)
                        raise RuntimeError(
                            "router usage accounting invalid; raw preserved, response quarantined"
                        )
                    rec["accounting_valid"] = True
                if inp > bound or (maximum and out > maximum) or cost > reserve:
                    rec["bound_violation"] = True
                    ledger["closed"] = True
            except (KeyError, AssertionError, TypeError):
                rec["billing_unresolved"] = True
            save(p, ledger)
            return r


def install():
    if getattr(httpx.Client.send, "_scout099", False):
        return
    original = httpx.Client.send

    def wrapped(c, r, **k):
        return send(original, c, r, **k)

    wrapped._scout099 = True
    httpx.Client.send = wrapped
