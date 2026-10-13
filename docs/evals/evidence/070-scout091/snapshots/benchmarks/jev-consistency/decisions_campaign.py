"""Scout086 owner campaign. Independent native requests, durable cap, no retries."""

from __future__ import annotations
import argparse
import base64
import hashlib
import importlib.util
import io
import json
import math
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/evals/evidence/063-decisions"
CAP = 10.0


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


legacy = load_module(
    "consistency_campaign_legacy", ROOT / "benchmarks/jev-consistency/run.py"
)
owner = load_module(
    "decisions_campaign_responses",
    ROOT / "benchmarks/providers/openai_responses_model.py",
)


def write(path, value):
    data = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(data)
    temp.replace(path)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decision_body(evidence, instruction, labels):
    return {
        "model": "gpt-6-luna",
        "input": evidence,
        "questions": [
            {
                "type": "choice",
                "name": "classification",
                "instructions": instruction,
                "choices": [{"value": k, "description": v} for k, v in labels.items()],
            }
        ],
    }


def parse_choice(raw, labels):
    if raw.get("model") != "gpt-6-luna" or raw.get("error"):
        raise ValueError("wrong served identity/error")
    usage = raw.get("usage", {})
    for key in ("input_tokens", "output_tokens", "total_tokens"):
        if type(usage.get(key)) is not int or usage[key] < 0:
            raise ValueError("invalid usage")
    if len(raw.get("answers", [])) != 1:
        raise ValueError("answer count")
    a = raw["answers"][0]
    if a.get("name") != "classification":
        raise ValueError("question name")
    if a.get("type") == "refusal":
        return "refusal", None, usage["input_tokens"] * 0.1 / 1e6
    if a.get("type") != "choice" or a.get("choice") not in labels:
        raise ValueError("invalid choice")
    probs = a.get("probabilities", [])
    p = {x["value"]: x["probability"] for x in probs}
    if len(probs) != len(labels) or set(p) != set(labels):
        raise ValueError("probability coverage")
    c = a.get("confidence")
    if any(
        type(x) not in (int, float) or not math.isfinite(x) or not 0 <= x <= 1
        for x in list(p.values()) + [c]
    ):
        raise ValueError("nonfinite probability/confidence")
    if abs(sum(p.values()) - 1) > 0.002 or p[a["choice"]] < max(p.values()):
        raise ValueError("invalid probability sum/argmax")
    return a["choice"], c, usage["input_tokens"] * 0.1 / 1e6


def parse(arm, raw, labels):
    if arm == "decisions":
        return parse_choice(raw, labels)
    if arm == "gpt41":
        return legacy.parse("gpt", raw)
    if (
        raw.get("model") != "gpt-5.5-2026-04-23"
        or raw.get("status") != "completed"
        or raw.get("error")
        or raw.get("incomplete_details")
    ):
        raise ValueError("invalid Responses terminal identity")
    usage = owner._token_usage(raw)
    if usage is None:
        raise ValueError("invalid usage")
    output = owner._extract_output_text(raw)
    if owner._contract_error(output, "page_context_validation"):
        raise ValueError("invalid strict page contract")
    obj = json.loads(output)
    return (
        obj["verdict"],
        None,
        (
            (usage["prompt"] - usage.get("cached", 0)) * 5
            + usage.get("cached", 0) * 0.5
            + usage["completion"] * 30
        )
        / 1e6,
    )


def reserve(arm, body, image=False):
    if image:
        return (
            46000 * 0.1 / 1e6 if arm == "decisions" else (46000 * 5 + 2048 * 30) / 1e6
        )
    b = len(json.dumps(body, ensure_ascii=False).encode()) + 512
    return b * 0.1 / 1e6 if arm == "decisions" else b * 2 / 1e6 + 160 * 8 / 1e6


def call(arm, body, name, labels, image=False, recovery=False):
    path = OUT / "ledger.json"
    ledger = json.loads(path.read_text())
    if ledger.get("closed"):
        raise RuntimeError("campaign ledger closed")
    if any(x["name"] == name for x in ledger["calls"]):
        raise RuntimeError("duplicate send denied")
    if recovery and sum(x.get("recovery", False) for x in ledger["calls"]) >= 2:
        raise RuntimeError("recovery budget exhausted")
    amount = reserve(arm, body, image)
    if ledger["spent_usd"] + ledger["unknown_usd"] + amount > CAP:
        raise RuntimeError("hard dollar cap")
    encoded = json.dumps(body, ensure_ascii=False).encode()
    entry = {
        "name": name,
        "arm": arm,
        "reserve_usd": amount,
        "recovery": recovery,
        "status": "dispatched",
        "request_bytes": len(encoded),
        "request_sha256": hashlib.sha256(encoded).hexdigest(),
    }
    ledger["calls"].append(entry)
    ledger["unknown_usd"] += amount
    write(path, ledger)
    request_path = OUT / "raw" / (name + ".request.json")
    request_path.write_bytes(encoded)
    endpoint = {
        "decisions": "decisions",
        "gpt41": "chat/completions",
        "gpt55": "responses",
    }[arm]
    t = time.monotonic()
    try:
        req = urllib.request.Request(
            "https://api.openai.com/v1/" + endpoint,
            data=encoded,
            headers={
                "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"],
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                response, status = r.read(), r.status
                request_id = r.headers.get("x-request-id")
        except urllib.error.HTTPError as e:
            response, status, request_id = (
                e.read(),
                e.code,
                e.headers.get("x-request-id"),
            )
    except Exception as exc:
        entry.update(
            status="delivery_unknown",
            exception_type=type(exc).__name__,
            latency_ms=(time.monotonic() - t) * 1000,
        )
        write(path, ledger)
        raise RuntimeError("delivery unknown; retained conservative reserve") from None
    entry.update(
        http_status=status,
        latency_ms=(time.monotonic() - t) * 1000,
        request_id=request_id,
        response_sha256=hashlib.sha256(response).hexdigest(),
        response_bytes=len(response),
    )
    (OUT / "raw" / (name + ".response.json")).write_bytes(response)
    entry["status"] = "http_error_unknown_billing"
    write(path, ledger)
    if status != 200:
        raise RuntimeError("HTTP failure retained: " + str(status))
    raw = json.loads(response)
    try:
        label, confidence, cost = parse(arm, raw, labels)
    except Exception:
        entry.update(
            status="contract_invalid_unknown_billing",
            served_model=raw.get("model"),
            usage=raw.get("usage"),
        )
        write(path, ledger)
        raise
    if cost > amount + 1e-9:
        raise RuntimeError("reservation violated; stop campaign")
    entry.update(
        status="complete",
        label=label,
        confidence=confidence,
        cost_usd=cost,
        served_model=raw["model"],
        usage=raw["usage"],
    )
    ledger["spent_usd"] += cost
    ledger["unknown_usd"] -= amount
    write(path, ledger)
    return entry


def cases():
    return json.loads((ROOT / "benchmarks/jev-consistency/fixtures.json").read_text())


def image_cases():
    task = yaml.safe_load(
        (
            ROOT / "benchmarks/tasks/safety-repair-048-control-full-continuation1.yaml"
        ).read_text()
    )
    return {x["vars"]["crop_key"]: x["vars"] for x in task["tests"]}


def image_body(key, arm):
    v = image_cases()[key]
    prompt_file = ROOT / "benchmarks/prompts/validate-page-level-crop.js"
    prompt = re.search(
        r"const PROMPT_TEXT = `(.*?)`;", prompt_file.read_text(), re.S
    ).group(1)
    parts = [{"type": "input_text", "text": prompt}]
    for k in ("page_image", "crop_image"):
        p = (ROOT / "benchmarks/tasks" / v[k].removeprefix("file://")).resolve()
        parts.append({"type": "input_image", "image_url": p.read_text().strip()})
    messages = [{"role": "user", "content": parts}]
    if arm == "decisions":
        return decision_body(
            messages,
            "Select the verdict using all source-context rules supplied with the images. A fail verdict routes this crop for review; it never authorizes source deletion.",
            {
                "pass": "The crop meets the supplied PASS rules and no FAIL condition applies.",
                "fail": "A supplied FAIL condition applies, including unresolved source-boundary uncertainty; do not accept without review.",
            },
        )
    return owner._build_body(
        json.dumps(messages),
        {
            "config": {
                "model": "gpt-5.5",
                "expected_served_model": "gpt-5.5-2026-04-23",
                "reasoning_effort": "none",
                "max_output_tokens": 2048,
                "image_detail": "auto",
                "output_contract": "page_context_validation",
            }
        },
    )


def preflight():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "raw").mkdir(exist_ok=True)
    (OUT / "snapshots").mkdir(exist_ok=True)
    frozen = [
        "benchmarks/jev-consistency/run.py",
        "benchmarks/jev-consistency/detector.py",
        "benchmarks/jev-consistency/fixtures.json",
        "benchmarks/jev-consistency/plan.md",
        "benchmarks/jev-consistency/decisions_campaign.py",
        "benchmarks/providers/openai_responses_model.py",
        "benchmarks/prompts/validate-page-level-crop.js",
        "benchmarks/golden/crop-page-level-safety-repair-048-source-adjudicated.json",
        "benchmarks/scorers/crop_validation_scorer.py",
        "scripts/run_with_doc_web_env.py",
        "doc_web/env.py",
        "modules/validate/validate_onward_genealogy_consistency_v1/main.py",
    ]
    snapshots = {}
    for p in frozen:
        dst = OUT / "snapshots" / p
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / p, dst)
        snapshots[p] = {"sha256": sha(ROOT / p), "snapshot": str(dst.relative_to(ROOT))}
    assert (
        sha(ROOT / "benchmarks/jev-consistency/fixtures.json")
        == "88994b8cd7c75d832114f33e613c3b2d8656b737f53962292ee34c4e81b128ab"
    )
    assert (
        sha(ROOT / "benchmarks/prompts/validate-page-level-crop.js")
        == "ef4395838929b208fe65f21500d81ade902072bef3f8e53f81ef3d3b83fbc421"
    )
    rendered = []
    for c in cases():
        rendered.append(
            {
                "id": c["id"],
                "decisions": decision_body(
                    json.dumps(c["input"], ensure_ascii=False),
                    legacy.INSTRUCTION,
                    legacy.LABELS,
                ),
                "gpt41": legacy.payload("gpt", c["input"]),
            }
        )
    write(OUT / "text-rendered.json", rendered)
    max_text = {
        arm: max(len(json.dumps(x[arm], ensure_ascii=False).encode()) for x in rendered)
        for arm in ("decisions", "gpt41")
    }
    images = []
    for key, v in image_cases().items():
        sources = []
        for field in ("page_image", "crop_image"):
            p = (ROOT / "benchmarks/tasks" / v[field].removeprefix("file://")).resolve()
            decoded = base64.b64decode(p.read_text().split(",", 1)[1])
            im = Image.open(io.BytesIO(decoded))
            sources.append(
                {
                    "path": str(p.relative_to(ROOT)),
                    "uri_sha256": sha(p),
                    "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
                    "dimensions": im.size,
                }
            )
        body = image_body(key, "gpt55")
        images.append(
            {
                "key": key,
                "sources": sources,
                "gpt55_request_bytes": len(json.dumps(body).encode()),
                "gpt55_body_sha256": hashlib.sha256(
                    json.dumps(body, sort_keys=True).encode()
                ).hexdigest(),
                "gpt55_reserve": reserve("gpt55", body, True),
                "decisions_reserve": 0.0046,
            }
        )
    write(OUT / "image-topology.json", images)
    max_total = (
        22 * 0.29144
        + 22 * 0.0046
        + 40
        * reserve(
            "gpt41", max(rendered, key=lambda x: len(json.dumps(x["gpt41"])))["gpt41"]
        )
        * 2
        + 40
        * reserve(
            "decisions",
            max(rendered, key=lambda x: len(json.dumps(x["decisions"])))["decisions"],
        )
    )
    proof = {
        "base_sha": "19b30b1d0db4a7f3b2e31614ba9846dfdb93355c",
        "branch": "codex/decisions-docweb-20261006",
        "primary_dirty": [],
        "sources": snapshots,
        "text_unique": 20,
        "text_repeats": 2,
        "independent_source_documents": 2,
        "cache": "none; every call sent fresh; provider reported cache separately",
        "concurrency": 1,
        "sessions": "independent request per case; no conversation chain",
        "judges": "none; closed typed scorer plus source review",
        "max_text_request_bytes": max_text,
        "image_count": len(images),
        "max_complete_matrix_reservation_usd": max_total,
        "cap_usd": CAP,
        "remaining_for_probes_recovery_usd": CAP - max_total,
        "recovery_allowance": 2,
        "automatic_retries": 0,
        "image_input_reservation_tokens": 46000,
        "image_settings": "fresh GPT5.5 none/2048/auto/strict; Decisions choice no unsupported controls",
        "privacy": "text synthetic; images maintained public Onward benchmark bound to048 source hashes; private/unclear excluded",
        "fallback": "if candidate is explicit uncertain, preserve review; otherwise confidence<0.8 invokes real fresh GPT4.1 fallback; no threshold tuning",
        "safety_stop": "stop candidate image lane on first source-confirmed unsafe acceptance, independent text continues",
    }
    assert max_total < CAP
    write(OUT / "preflight.json", proof)
    if not (OUT / "ledger.json").exists():
        write(
            OUT / "ledger.json",
            {"cap_usd": CAP, "spent_usd": 0, "unknown_usd": 0, "calls": []},
        )
    print(
        json.dumps(
            {
                k: proof[k]
                for k in (
                    "text_unique",
                    "text_repeats",
                    "max_text_request_bytes",
                    "image_count",
                    "max_complete_matrix_reservation_usd",
                    "remaining_for_probes_recovery_usd",
                )
            },
            indent=2,
        )
    )


def text_run(limit):
    path = OUT / "text-results.json"
    rows = json.loads(path.read_text()) if path.exists() else []
    for rep in (1, 2):
        for c in cases()[:limit]:
            identity = f"r{rep}-{c['id']}"
            if any(x["id"] == identity for x in rows):
                continue
            d = call(
                "decisions",
                decision_body(
                    json.dumps(c["input"], ensure_ascii=False),
                    legacy.INSTRUCTION,
                    legacy.LABELS,
                ),
                identity + "-decisions",
                legacy.LABELS,
            )
            if d["label"] == "refusal":
                raise RuntimeError("refusal requires lane review")
            if d["label"] != "uncertain" and d["confidence"] < 0.8:
                f = call(
                    "gpt41",
                    legacy.payload("gpt", c["input"]),
                    identity + "-fallback",
                    legacy.LABELS,
                )
                cascade = dict(
                    f,
                    cost_usd=d["cost_usd"] + f["cost_usd"],
                    latency_ms=d["latency_ms"] + f["latency_ms"],
                    fallback=True,
                )
            else:
                cascade = dict(d, fallback=False)
            g = call(
                "gpt41",
                legacy.payload("gpt", c["input"]),
                identity + "-gpt41",
                legacy.LABELS,
            )
            rows.append(
                {
                    "id": identity,
                    "case": c["id"],
                    "gold": c["gold"],
                    "domain": c["domain"],
                    "decisions": d,
                    "gpt41": g,
                    "cascade": cascade,
                    "structural": legacy.deterministic(c["input"]),
                }
            )
            write(path, rows)
            print(
                identity,
                d["label"],
                g["label"],
                "fallback",
                cascade["fallback"],
                flush=True,
            )
    summary = {}
    for arm in ("decisions", "gpt41", "cascade"):
        rr = [dict(r[arm], id=r["id"], gold=r["gold"]) for r in rows]
        summary[arm] = legacy.metrics(rr)
        summary[arm]["review_routed"] = sum(x["label"] == "uncertain" for x in rr)
        summary[arm]["defects_sent_to_review"] = sum(
            x["gold"] in {"format_drift", "row_semantic_issue", "mixed"}
            and x["label"] == "uncertain"
            for x in rr
        )
    summary["fallback_calls"] = sum(x["cascade"]["fallback"] for x in rows)
    write(OUT / "text-summary.json", summary)
    print(json.dumps(summary, indent=2))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["preflight", "probe", "text", "image"])
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--key")
    p.add_argument("--arm", default="decisions")
    a = p.parse_args()
    if a.mode == "preflight":
        return preflight()
    if a.mode == "text":
        return text_run(a.limit)
    if a.mode == "image":
        result = call(
            a.arm,
            image_body(a.key, a.arm),
            "image-" + a.key + "-" + a.arm,
            {"pass": "", "fail": ""},
            True,
        )
        print(json.dumps(result, indent=2))
        return
    if a.mode == "probe":
        body = decision_body(
            "The package is broken.",
            "Classify the reported package state.",
            {"damaged": "The item is broken.", "intact": "The item is intact."},
        )
        print(
            json.dumps(
                call("decisions", body, "probe-choice", {"damaged": "", "intact": ""}),
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
