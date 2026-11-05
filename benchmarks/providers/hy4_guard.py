"""Hy4 owner serialized hard-cap ledger; exact raw bytes before parsing."""

import fcntl
import hashlib
import json
import math
import os
import shutil
import time
from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "benchmarks/results/hy4-20261105"
E = ROOT / "docs/evals/evidence/086-hy4"
PRICES = {
    "gpt-6-astra": (10, 1, 12.5, 50),
    "gpt-5.5": (5, 0.5, 5, 30),
    "gpt-5.5-2026-04-23": (5,.5,5,30),
    "gemini-3-flash-preview": (0.5, 0.05, 0.5, 3),
    "gemini-3.7-flash": (0.75, 0.075, 0.75, 3.75),
    "gemini-3.8-flash": (0.75, 0.075, 0.75, 3.75),
    "tencent/hy4": (0.417, 0.021, 0.417, 1.2505),
    "tencent/hy4-20261104": (0.417, 0.021, 0.417, 1.2505),
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
    if shutil.disk_usage(ROOT).free < 256 * 1024 * 1024:
        raise RuntimeError("disk below256MiB")
    host = request.url.host
    google = host == "generativelanguage.googleapis.com"
    router = host == "openrouter.ai"
    if host not in (
        "generativelanguage.googleapis.com",
        "api.openai.com",
        "openrouter.ai",
    ):
        raise RuntimeError("unapproved endpoint")
    b = json.loads(request.content)
    model = (
        request.url.path.split("/models/")[1].split(":")[0] if google else b["model"]
    )
    stage = os.environ["HY4_STAGE"]
    if model not in PRICES or model in ("gemini-3.8-flash", "tencent/hy4-20261104"):
        raise RuntimeError("unapproved requested model")
    maximum = (
        b["generationConfig"]["maxOutputTokens"]
        if google
        else b["max_tokens"]
        if router
        else b["max_output_tokens"]
    )
    if (
        not google
        and not router
        and (b.get("store") is not False or b.get("service_tier") != "default")
    ):
        raise RuntimeError("storage/service contract")
    if router:
        assert (
            model == "tencent/hy4"
            and maximum == 32768
            and b["reasoning"]["effort"] == "high"
        )
        assert b["provider"] == {
            "only": ["tencent"],
            "allow_fallbacks": False,
            "require_parameters": True,
            "max_price": {"prompt": 0.417, "completion": 1.2505},
        }
    prices = PRICES[model]
    encoded = json.dumps(b)
    count = (
        encoded.count('"input_image"')
        + encoded.count('"inlineData"')
        + encoded.count('"image_url": {')
    )
    bound = (100000 if router else 20000) * count + 6000
    reserve = max(
        1.5 if model == "gpt-6-astra" else 0,
        (bound * max(prices[:3]) + maximum * prices[3]) / 1e6,
    )
    RESULTS.mkdir(parents=True, exist_ok=True)
    with (RESULTS / "ledger.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        p = RESULTS / "ledger.json"
        ledger = json.loads(p.read_text())
        if (
            ledger["closed"]
            or ledger["spent_usd"]
            + sum(
                x["reserved_usd"] for x in ledger["calls"] if x.get("cost_usd") is None
            )
            + reserve
            > 5
        ):
            raise RuntimeError("hard5USD cap")
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
        try:
            d = r.json()
            u = d.get("usageMetadata", {}) if google else d.get("usage", {})
            served = d.get("modelVersion", d.get("model"))
            actual_prices = PRICES[served]
            if google:
                inp = u["promptTokenCount"]
                out = u.get("candidatesTokenCount", 0) + u.get("thoughtsTokenCount", 0)
                cached = u.get("cachedContentTokenCount", 0)
                write = 0
            elif router:
                inp = u["prompt_tokens"]
                out = u["completion_tokens"]
                cached = u.get("prompt_tokens_details", {}).get("cached_tokens", 0)
                write = 0
            else:
                inp = u["input_tokens"]
                out = u["output_tokens"]
                details = u.get("input_tokens_details", {})
                cached = details.get("cached_tokens", 0)
                write = details.get("cache_write_tokens", 0)
            cost = (
                u["cost"]
                if router
                else (
                    (inp - cached - write) * actual_prices[0]
                    + cached * actual_prices[1]
                    + write * actual_prices[2]
                    + out * actual_prices[3]
                )
                / 1e6
            )
            assert (
                type(inp) is int
                and type(out) is int
                and inp >= 0
                and out >= 0
                and isinstance(cost, (int, float))
                and math.isfinite(cost)
                and cost >= 0
            )
            rec.update(
                cost_usd=cost,
                usage=u,
                served_model=served,
                provider=d.get("provider")
                if router
                else "Google"
                if google
                else "OpenAI",
            )
            ledger["spent_usd"] += cost
            if inp > bound or out > maximum or cost > reserve:
                rec["bound_violation"] = True
                ledger["closed"] = True
        except (KeyError, TypeError, AssertionError, ValueError):
            rec["billing_unresolved"] = True
            if r.status_code in (400, 401, 402, 403, 404, 429) and not d.get(
                "usage", {}
            ):
                rec.update(
                    cost_usd=0, billing_unresolved=False, pre_inference_rejection=True
                )
        save(p, ledger)
        return r


def install():
    if getattr(httpx.Client.send, "_hy4", False):
        return
    original = httpx.Client.send

    def wrapped(c, r, **k):
        return send(original, c, r, **k)

    wrapped._hy4 = True
    httpx.Client.send = wrapped
