"""Scout096 frozen page/crop safety screen; preflight is zero-cost by default.

The typed arms deliberately measure the finite verdict projection only. They do
not establish the runtime reason/observed-flag contract. No input resizing.
"""

from __future__ import annotations
import argparse
import base64
import hashlib
import importlib.util
import io
import json
import math
import os
import time
import httpx
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/evals/evidence/078-scout096"
MODELS = {
    "d1": "liquid/d1-ultra",
    "span": "respan/span-02",
    "nemotron": "nvidia/nemotron-3.5-super-vl",
    "control": "gpt-5.5",
}
CANONICAL = {k: v + "-20261015" for k, v in MODELS.items() if k != "control"}
CANONICAL["control"] = "gpt-5.5-2026-04-23"
GOLDEN = (
    ROOT / "benchmarks/golden/crop-page-level-safety-repair-048-source-adjudicated.json"
)


def load(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    sys.modules[name] = m
    s.loader.exec_module(m)
    return m


helper = load(
    "scout096_safety_helper", ROOT / "benchmarks/jev-consistency/decisions_campaign.py"
)


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


def body(key, arm):
    original = helper.image_body(key, "gpt55")
    if arm == "control":
        return original
    parts = original["input"][0]["content"]
    if arm in ("d1", "span"):
        state = [
            p["text"]
            if p["type"] == "input_text"
            else {"type": "image_url", "image_url": {"url": p["image_url"]}}
            for p in parts
        ]
        return {
            "model": MODELS[arm],
            "state": state,
            "questions": {
                "verdict": {
                    "type": "choice",
                    "instructions": "Select the verdict using all source-context rules supplied with the images. A fail verdict routes this crop for review; it never authorizes source deletion.",
                    "criteria": {
                        "pass": "The crop meets the supplied PASS rules and no FAIL condition applies.",
                        "fail": "A supplied FAIL condition applies, including unresolved source-boundary uncertainty; do not accept without review.",
                    },
                }
            },
        }
    assert arm == "nemotron"
    content = [
        {"type": "text", "text": p["text"]}
        if p["type"] == "input_text"
        else {"type": "image_url", "image_url": {"url": p["image_url"]}}
        for p in parts
    ]
    return {
        "model": MODELS[arm],
        "messages": [{"role": "user", "content": content}],
        "max_tokens": 32768,
        "reasoning": {"enabled": True},
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "page_context_validation",
                "strict": True,
                "schema": original["text"]["format"]["schema"],
            },
        },
        "provider": {
            "only": ["Together"],
            "allow_fallbacks": False,
            "require_parameters": True,
        },
    }


def parse(arm, raw):
    if arm == "control":
        verdict, _, cost = helper.parse("gpt55", raw, ["pass", "fail"])
        return verdict, cost
    if raw.get("model") not in (MODELS[arm], CANONICAL[arm]) or raw.get("error"):
        raise ValueError("served identity/error")
    u = raw.get("usage", {})
    cost = u.get("cost")
    if not isinstance(cost, (int, float)) or not math.isfinite(cost) or cost < 0:
        raise ValueError("missing cost")
    if arm in ("d1", "span"):
        answers = raw.get("answers", {})
        if set(answers) != {"verdict"}:
            raise ValueError("unexpected answer keys")
        a = answers["verdict"]
        probabilities = a.get("probabilities", {})
        if (
            a.get("type") != "choice"
            or a.get("choice") not in ("pass", "fail")
            or set(probabilities) != {"pass", "fail"}
        ):
            raise ValueError("choice contract")
        if (
            any(
                type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1
                for v in probabilities.values()
            )
            or abs(sum(probabilities.values()) - 1) > 0.002
        ):
            raise ValueError("probabilities")
        if probabilities[a["choice"]] < max(probabilities.values()):
            raise ValueError("choice is not argmax")
        return a["choice"], cost
    if raw.get("provider") != "Together":
        raise ValueError("wrong provider")
    choices = raw.get("choices", [])
    if len(choices) != 1 or choices[0].get("finish_reason") != "stop":
        raise ValueError("terminal status")
    text = choices[0]["message"].get("content")
    error = helper.owner._contract_error(text, "page_context_validation")
    if error:
        raise ValueError(error)
    return json.loads(text)["verdict"], cost


def preflight():
    cases = helper.image_cases()
    assert len(cases) == 22
    assert GOLDEN.exists()
    golden = json.loads(GOLDEN.read_text())
    topology = {
        "subject_cache": "disabled",
        "concurrency": 1,
        "judge": "none; frozen deterministic verdict scorer plus source uncertainty veto",
        "cases": [],
        "arms": MODELS,
        "canonical_ids": CANONICAL,
        "golden_sha256": hashlib.sha256(GOLDEN.read_bytes()).hexdigest(),
        "typed_contract": "finite verdict projection only; runtime flags/reason unqualified",
        "frozen_sources": {},
    }
    for key in cases:
        images = []
        native = body(key, "control")
        for part in native["input"][0]["content"][1:]:
            pixels = base64.b64decode(part["image_url"].split(",", 1)[1])
            dimensions = Image.open(io.BytesIO(pixels)).size
            images.append(
                {"sha256": hashlib.sha256(pixels).hexdigest(), "dimensions": dimensions}
            )
        topology["cases"].append(
            {
                "key": key,
                "golden": golden[key]["verdict"],
                "images_ordered_source_then_crop": images,
                "request_sha256": {a: digest(body(key, a)) for a in MODELS},
            }
        )
    for p in [
        Path(__file__),
        ROOT / "benchmarks/jev-consistency/decisions_campaign.py",
        ROOT / "benchmarks/prompts/validate-page-level-crop.js",
        ROOT / "benchmarks/scorers/crop_validation_scorer.py",
        ROOT / "benchmarks/providers/openai_responses_model.py",
    ]:
        topology["frozen_sources"][str(p.relative_to(ROOT))] = hashlib.sha256(
            p.read_bytes()
        ).hexdigest()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "safety-preflight.json").write_text(json.dumps(topology, indent=2) + "\n")
    print(
        json.dumps(
            {
                "cases": len(cases),
                "arms": list(MODELS),
                "paid_calls": 0,
                "preflight": str(OUT / "safety-preflight.json"),
            }
        )
    )


def run(arm, limit, recover=False):
    sys.path.insert(0, str(ROOT / "benchmarks/providers"))
    import scout096_guard as guard

    guard.install()
    results = []
    path = OUT / f"safety-{arm}-results.json"
    if path.exists():
        results = json.loads(path.read_text())
    golden = json.loads(GOLDEN.read_text())
    completed = {x["key"] for x in results if not (recover and x.get("error"))}
    for key in helper.image_cases():
        if key in completed:
            continue
        payload = body(key, arm)
        os.environ["SCOUT096_STAGE"] = f"safety-{arm}-{key}" + (
            "-recovery1" if recover else ""
        )
        if arm == "control":
            endpoint = "https://api.openai.com/v1/responses"
            secret = os.environ.get("DOC_WEB_OPENAI_API_KEY") or os.environ.get(
                "OPENAI_API_KEY"
            )
        else:
            endpoint = (
                "https://openrouter.ai/api/alpha/decisions"
                if arm in ("d1", "span")
                else "https://openrouter.ai/api/v1/chat/completions"
            )
            secret = os.environ.get("DOC_WEB_OPENROUTER_API_KEY") or os.environ.get(
                "OPENROUTER_API_KEY"
            )
        if not secret:
            raise RuntimeError("missing owner credential")
        start = time.monotonic()
        with httpx.Client(timeout=180) as client:
            response = client.post(
                endpoint, json=payload, headers={"Authorization": "Bearer " + secret}
            )
        ledger = json.loads(
            (ROOT / "benchmarks/results/scout096-20261016/ledger.json").read_text()
        )
        receipt = next(
            x for x in ledger["calls"] if x["stage"] == os.environ["SCOUT096_STAGE"]
        )
        row = {
            "key": key,
            "status_code": response.status_code,
            "latency_ms": receipt.get("latency_ms"),
            "elapsed_including_queue_ms": round((time.monotonic() - start) * 1000),
            "request_sha256": digest(payload),
        }
        try:
            response.raise_for_status()
            raw = response.json()
            verdict, cost = parse(arm, raw)
            row.update(
                verdict=verdict,
                cost_usd=cost,
                correct=verdict == golden[key]["verdict"],
                false_safe=verdict == "pass" and golden[key]["verdict"] == "fail",
                golden=golden[key]["verdict"],
                served_model=raw.get("model"),
                provider=raw.get("provider", "OpenAI"),
            )
        except Exception as exc:
            row.update(error=str(exc)[:600], semantic="unmeasured")
        results.append(row)
        path.write_text(json.dumps(results, indent=2) + "\n")
        print(json.dumps(row), flush=True)
        if row.get("false_safe") or row.get("error"):
            break
        limit -= 1
        if limit <= 0:
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run", choices=list(MODELS))
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--recover", action="store_true")
    args = parser.parse_args()
    if args.run:
        run(args.run, args.limit, args.recover)
    else:
        preflight()
