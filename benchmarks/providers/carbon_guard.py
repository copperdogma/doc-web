"""Carbon owner atomic hard-cap ledger; exact raw bytes before parsing."""

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
LOADED_SOURCE = Path(__file__).read_bytes()
RESULTS = ROOT / "benchmarks/results/carbon-20261110"
E = ROOT / "docs/evals/evidence/089-carbon"
PRICES = {
    "gpt-6-astra": (10, 1, 12.5, 50),
    "gpt-5.5": (5, 0.5, 5, 30),
    "gpt-5.5-2026-04-23": (5, 0.5, 5, 30),
    "gemini-3-flash-preview": (0.5, 0.05, 0.5, 3),
    "gemini-3.7-flash": (0.75, 0.075, 0.75, 3.75),
    "gemini-3.8-flash": (0.75, 0.075, 0.75, 3.75),
    "gemini-4-carbon": (2, 0.1, 2, 10),
    "claude-fable-5-2": (8, 0.2, 16, 40),
    "anthropic/claude-fable-5.2": (8, 0.8, 8, 40),
    "anthropic/claude-fable-5.2-20261110": (8, 0.8, 8, 40),
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
    if shutil.disk_usage(ROOT).free < 512 * 1024 * 1024:
        raise RuntimeError("disk below512MiB")
    host = request.url.host
    google = host == "generativelanguage.googleapis.com"
    router = host == "openrouter.ai"
    native = host == "api.anthropic.com"
    if host not in (
        "generativelanguage.googleapis.com",
        "api.openai.com",
        "api.anthropic.com",
        "openrouter.ai",
    ):
        raise RuntimeError("unapproved endpoint")
    b = json.loads(request.content)
    model = (
        request.url.path.split("/models/")[1].split(":")[0] if google else b["model"]
    )
    stage = os.environ["CARBON_STAGE"]
    matrix = json.loads((E / "preflight.json").read_text())["matrix"]
    selected = next((x for x in matrix if x["stage"] == stage), None)
    if selected is None or selected["model"] != model:
        raise RuntimeError("stage model differs from frozen matrix")
    planned = E / "rendered" / (stage + ".json")
    if not planned.exists() or sha(planned.read_bytes()) != selected["request_sha256"]:
        raise RuntimeError("frozen rendered case hash mismatch")
    if not planned.exists() or json.loads(planned.read_text()) != b:
        raise RuntimeError("outgoing request differs from frozen rendered case")
    if model not in {
        "gemini-4-carbon",
        "gemini-3-flash-preview",
        "gemini-3.8-flash",
        "gpt-6-astra",
        "gpt-5.5",
    } or model in ("anthropic/claude-fable-5.2-20261110",):
        raise RuntimeError("unapproved requested model")
    maximum = (
        b["generationConfig"]["maxOutputTokens"]
        if google
        else b["max_tokens"]
        if router or native
        else b["max_output_tokens"]
    )
    if (
        not google
        and not router
        and not native
        and (b.get("store") is not False or b.get("service_tier") != "default")
    ):
        raise RuntimeError("storage/service contract")
    if router:
        assert (
            model == "anthropic/claude-fable-5.2"
            and maximum in (32768, 65536)
            and b["reasoning"]["effort"] in ("xhigh", "max")
        )
        assert b["provider"] == {
            "only": ["anthropic"],
            "allow_fallbacks": False,
            "require_parameters": True,
            "max_price": {"prompt": 8, "completion": 40},
        }
    if native:
        assert model == "claude-fable-5-2" and maximum in (32768, 65536)
        assert b["output_config"]["effort"] in ("xhigh", "max")
        assert "temperature" not in b and "service_tier" not in b
    if model == "gemini-4-carbon":
        if maximum != 32768 or b["generationConfig"].get("thinkingConfig") != {
            "thinkingLevel": "HIGH"
        }:
            raise RuntimeError("selected Carbon controls required")
        if any(x in b["generationConfig"] for x in ("temperature", "topP", "topK")):
            raise RuntimeError("ignored sampling must be absent")
    prices = PRICES[model]
    encoded = json.dumps(b)
    count = (
        encoded.count('"input_image"')
        + encoded.count('"type": "image"')
        + encoded.count('"inlineData"')
        + encoded.count('"image_url": {')
    )
    bound = 20000 * count + 6000
    reserve = max(
        0,
        (bound * max(prices[:3]) + maximum * prices[3]) / 1e6,
    )
    E.mkdir(parents=True, exist_ok=True)
    (E / "write-check.tmp").write_text("durable write admission")
    (E / "write-check.tmp").unlink()
    RESULTS.mkdir(parents=True, exist_ok=True)
    with (RESULTS / "ledger.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        p = RESULTS / "ledger.json"
        ledger = json.loads(p.read_text())
        waiting_started = time.monotonic()
        while (
            sum(
                bool(
                    x.get(
                        "in_flight",
                        x.get("cost_usd") is None
                        and not x.get("status_code")
                        and not x.get("exception"),
                    )
                )
                for x in ledger["calls"]
            )
            >= 2
        ):
            fcntl.flock(lock, fcntl.LOCK_UN)
            if time.monotonic() - waiting_started > 900:
                raise RuntimeError("local admission wait expired before network")
            time.sleep(0.2)
            fcntl.flock(lock, fcntl.LOCK_EX)
            ledger = json.loads(p.read_text())
        if (
            ledger["closed"]
            or ledger["spent_usd"]
            + sum(
                x["reserved_usd"] for x in ledger["calls"] if x.get("cost_usd") is None
            )
            + reserve
            > 10
        ):
            raise RuntimeError("hard10USD cap")
        if model != "gemini-4-carbon":
            exposure = sum(
                (x["cost_usd"] if x.get("cost_usd") is not None else x["reserved_usd"])
                for x in ledger["calls"]
                if x["model"] != "gemini-4-carbon"
            )
            if exposure + reserve > 3:
                raise RuntimeError("hard3USD control pool")
        active = sum(
            bool(
                x.get(
                    "in_flight",
                    x.get("cost_usd") is None
                    and not x.get("status_code")
                    and not x.get("exception"),
                )
            )
            for x in ledger["calls"]
        )
        if active >= 2:
            raise RuntimeError("admission slot lost under exclusive lock")
        if len(ledger["calls"]) >= 28:
            raise RuntimeError("finite28POST maximum")
        if any(x["stage"] == stage for x in ledger["calls"]):
            raise RuntimeError("duplicate stage")
        n = len(ledger["calls"]) + 1
        raw = request.content
        req = RESULTS / f"request-{n:03}.json"
        res = RESULTS / f"response-{n:03}.json"
        with req.open("xb") as f:
            f.write(raw)
        code = E / "dispatch-code" / (sha(LOADED_SOURCE) + "-carbon_guard.py")
        code.parent.mkdir(parents=True, exist_ok=True)
        if not code.exists():
            code.write_bytes(LOADED_SOURCE)
        rec = {
            "producing_guard_sha256": sha(LOADED_SOURCE),
            "stage": stage,
            "model": model,
            "reserved_usd": reserve,
            "cost_usd": None,
            "in_flight": True,
            "request": str(req.relative_to(ROOT)),
            "request_sha256": sha(raw),
        }
        ledger["calls"].append(rec)
        save(p, ledger)
        fcntl.flock(lock, fcntl.LOCK_UN)
        start = time.monotonic()
        try:
            r = original(client, request, **kwargs)
            r.read()
        except Exception as exc:
            fcntl.flock(lock, fcntl.LOCK_EX)
            ledger = json.loads(p.read_text())
            rec = next(x for x in ledger["calls"] if x["stage"] == stage)
            rec.update(exception=type(exc).__name__, in_flight=False)
            save(p, ledger)
            raise
        with res.open("xb") as f:
            f.write(r.content)
        (E / res.name).write_bytes(r.content)
        (E / req.name).write_bytes(raw)
        fcntl.flock(lock, fcntl.LOCK_EX)
        ledger = json.loads(p.read_text())
        rec = next(x for x in ledger["calls"] if x["stage"] == stage)
        rec.update(
            in_flight=False,
            request_url=str(request.url.copy_with(query=None)),
            response=str(res.relative_to(ROOT)),
            response_sha256=sha(r.content),
            status_code=r.status_code,
            latency_ms=round((time.monotonic() - start) * 1000),
        )
        d = {}
        try:
            d = r.json()
            u = d.get("usageMetadata", {}) if google else d.get("usage", {})
            served = d.get("modelVersion", d.get("model"))
            actual_prices = PRICES[served]
            if google:
                inp = u["promptTokenCount"]
                visible = u["candidatesTokenCount"]
                thinking = u.get("thoughtsTokenCount", 0)
                if any(type(v) is not int or v < 0 for v in (inp, visible, thinking)):
                    raise ValueError("invalid native usage")
                out = visible + thinking
                cached = u.get("cachedContentTokenCount", 0)
                write = 0
            elif router:
                inp = u["prompt_tokens"]
                out = u["completion_tokens"]
                cached = u.get("prompt_tokens_details", {}).get("cached_tokens", 0)
                write = 0
            elif native:
                inp = u["input_tokens"]
                out = u["output_tokens"]
                cached = u.get("cache_read_input_tokens", 0)
                write = u.get("cache_creation_input_tokens", 0)
                inp += cached + write
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
                and type(cached) is int
                and 0 <= cached <= inp
                and type(write) is int
                and 0 <= write <= inp - cached
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
                else "Anthropic"
                if native
                else "OpenAI",
            )
            ledger["spent_usd"] += cost
            rec["output_tokens_including_thinking"] = out
            rec["input_tokens"] = inp
            rec["december_cost_usd"] = cost * 2 if model == "gemini-4-carbon" else cost
            if inp > bound or out > maximum or cost > reserve:
                rec["bound_violation"] = True
                ledger["closed"] = True
        except (KeyError, TypeError, AssertionError, ValueError):
            rec["billing_unresolved"] = True
            if r.status_code in (400, 401, 402, 403, 404, 429) and not d.get(
                "usage", {}
            ):
                rec.update(
                    cost_usd=None, billing_unresolved=True, pre_inference_rejection=True
                )
        save(p, ledger)
        return r


def install():
    if getattr(httpx.Client.send, "_carbon", False):
        return
    original = httpx.Client.send

    def wrapped(c, r, **k):
        return send(original, c, r, **k)

    wrapped._carbon = True
    httpx.Client.send = wrapped
