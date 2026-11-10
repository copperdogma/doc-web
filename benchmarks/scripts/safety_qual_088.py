# ruff: noqa: E402
"""Approved USD60 native safety study. Fresh subjects, one combined custody ledger."""

from __future__ import annotations

if not __debug__:
    raise RuntimeError("Optimized Python cannot run qualification admission guards")
import base64
import fcntl
import hashlib
import io
import json
import math
import os
import shutil
import sys
import time
from pathlib import Path
import httpx
import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "benchmarks/providers"))
import openai_responses_model as sol_adapter
from modules.common.crop_safety import FORMAT

E = ROOT / "docs/evals/evidence/088-fable52-safety"
LEDGER = E / "ledger.json"
GOLDEN = (
    ROOT / "benchmarks/golden/crop-page-level-safety-repair-048-source-adjudicated.json"
)
GOLDEN_SHA = "6f32bc513494f1c4454b4c41e74186136212d477ff10c87ccb29244ca21aaa76"
MODELS = {"fable": "claude-fable-5-2", "sol": "gpt-6.1-sol"}
RESERVES = {"fable": 2.04672, "sol": 0.15596}
PRICES = {"fable": (8, 0.2, 16, 40), "sol": (2, 0.1, 2.5, 10)}
PROMPT = (ROOT / "modules/transform/propose_crop_safety_v1/prompt.txt").read_text()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    tmp.replace(path)


def matrix():
    task = yaml.safe_load(
        (
            ROOT / "benchmarks/tasks/safety-repair-048-sol-full-continuation1.yaml"
        ).read_text()
    )
    return [(t["vars"]["crop_key"], t["vars"]) for t in task["tests"]]


def inputs(key):
    v = dict(matrix())[key]
    parts = [{"type": "input_text", "text": PROMPT}]
    for field in ("page_image", "crop_image"):
        path = (ROOT / "benchmarks/tasks" / v[field].removeprefix("file://")).resolve()
        parts.append(
            {
                "type": "input_image",
                "image_url": path.read_text().strip(),
                "detail": "high",
            }
        )
    return parts


def body(arm, parts):
    if arm == "sol":
        b = sol_adapter._build_body(
            json.dumps([{"role": "user", "content": parts}]),
            {
                "config": {
                    "model": "gpt-6.1-sol",
                    "expected_served_model": "gpt-6.1-sol",
                    "reasoning_effort": "medium",
                    "max_output_tokens": 4096,
                    "image_detail": "high",
                    "output_contract": "page_context_validation",
                }
            },
        )
        b["service_tier"] = "default"
        return b
    contents = []
    for p in parts:
        if p["type"] == "input_text":
            contents.append({"type": "text", "text": p["text"]})
        else:
            header, data = p["image_url"].split(",", 1)
            contents.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": header.split(":")[1].split(";")[0],
                        "data": data,
                    },
                }
            )
    return {
        "model": MODELS[arm],
        "service_tier": "standard_only",
        "max_tokens": 32768,
        "output_config": {
            "effort": "xhigh",
            "format": {"type": "json_schema", "schema": FORMAT["schema"]},
        },
        "messages": [{"role": "user", "content": contents}],
    }


def image_bytes(b, arm):
    if arm == "fable":
        return [
            base64.b64decode(p["source"]["data"])
            for p in b["messages"][0]["content"]
            if p["type"] == "image"
        ]
    return [
        base64.b64decode(p["image_url"].split(",", 1)[1])
        for p in b["input"][0]["content"]
        if p["type"] == "input_image"
    ]


def text_parts(b, arm):
    return (
        [p["text"] for p in b["messages"][0]["content"] if p["type"] == "text"]
        if arm == "fable"
        else [p["text"] for p in b["input"][0]["content"] if p["type"] == "input_text"]
    )


def parse_payload(text):
    p = json.loads(text)
    assert isinstance(p, dict) and set(p) == {
        "verdict",
        "has_page_text",
        "excessive_blank",
        "reason",
    }
    assert (
        p["verdict"] in ("pass", "fail")
        and type(p["has_page_text"]) is bool
        and type(p["excessive_blank"]) is bool
        and isinstance(p["reason"], str)
        and p["reason"].strip()
    )
    return p


def parse_response(raw, arm):
    # Reuse the actual native caller parsers, not a weaker benchmark envelope parser.
    from modules.common import crop_safety as real
    from modules.common.crop_safety_fable_eval import (
        CONTRACT,
        ENV,
        parse_response as fable_parse,
    )

    previous = os.environ.pop(ENV, None)
    try:
        if arm == "fable":
            os.environ[ENV] = CONTRACT
            payload, data, _ = fable_parse(raw, 200, live=True)
        else:
            payload, data, _ = real.parse_response(raw, 200, live=True)
        return payload, data
    finally:
        os.environ.pop(ENV, None)
        if previous is not None:
            os.environ[ENV] = previous


def admission_body(b, arm, stage):
    assert set(b) == (
        {"model", "service_tier", "max_tokens", "output_config", "messages"}
        if arm == "fable"
        else {
            "model",
            "input",
            "reasoning",
            "max_output_tokens",
            "store",
            "text",
            "service_tier",
        }
    )
    assert len(b["messages"] if arm == "fable" else b["input"]) == 1
    assert (b["messages"] if arm == "fable" else b["input"])[0]["role"] == "user"
    assert len((b["messages"] if arm == "fable" else b["input"])[0]["content"]) == 3
    assert (
        b["model"] == MODELS[arm]
        and text_parts(b, arm) == [PROMPT]
        and len(image_bytes(b, arm)) == 2
    )
    assert not any(k in json.dumps(b) for k in ["cache_control", '"tools"'])
    if arm == "fable":
        assert (
            b["max_tokens"] == 32768
            and b["output_config"]
            == {
                "effort": "xhigh",
                "format": {"type": "json_schema", "schema": FORMAT["schema"]},
            }
            and "temperature" not in b
            and b.get("service_tier") == "standard_only"
        )
    else:
        assert (
            b["max_output_tokens"] == 4096
            and b["reasoning"] == {"effort": "medium"}
            and b["store"] is False
            and b["service_tier"] == "default"
            and b["text"]["format"] == FORMAT
        )
        assert all(
            p["detail"] == "high"
            for p in b["input"][0]["content"]
            if p["type"] == "input_image"
        )
    expected = json.loads((E / "preflight.json").read_text())["request_sources"][stage]
    assert [sha(x) for x in image_bytes(b, arm)] == expected


def send_native(b, arm, stage, *, recovery=False):
    """Only live boundary, callable by both benchmark and actual proposer wrapper."""
    assert arm in MODELS
    if shutil.disk_usage(ROOT).free < 512 * 1024 * 1024:
        raise RuntimeError("disk below512MiB")
    E.mkdir(parents=True, exist_ok=True)
    probe = E / "durable-write-check.tmp"
    probe.write_text("admission")
    probe.unlink()
    admission_body(b, arm, stage)
    # Serialize once: these exact bytes are sent and retained (excluding secret headers).
    wire = json.dumps(b, ensure_ascii=False, separators=(",", ":")).encode()
    with (E / "ledger.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        d = json.loads(LEDGER.read_text())
        assert not d["closed"], "ledgerclosed"
        planned = [c for c in d["calls"] if c["arm"] == arm and not c["recovery"]]
        recover = [c for c in d["calls"] if c["arm"] == arm and c["recovery"]]
        assert len(recover) < 2 if recovery else len(planned) < 24
        assert len(d["calls"]) < 52
        previous = [c for c in d["calls"] if c["stage"] == stage]
        assert not previous or recovery, "duplicate subject"
        if recovery:
            assert previous and not previous[-1].get("semantic_eligible", False), (
                "no retry of validqualityresult"
            )
        exposure = d["spent_usd"] + sum(
            c["reserved_usd"] for c in d["calls"] if c["cost_usd"] is None
        )
        assert exposure + RESERVES[arm] <= 60, "hard60cap"
        n = len(d["calls"]) + 1
        p = E / "raw"
        p.mkdir(exist_ok=True)
        req = p / f"{n:03d}-request.json"
        res = p / f"{n:03d}-response.json"
        with req.open("xb") as f:
            f.write(wire)
        snapshot = {}
        for file in [
            Path(__file__),
            ROOT / "benchmarks/providers/openai_responses_model.py",
            ROOT / "modules/common/crop_safety.py",
            ROOT / "modules/transform/propose_crop_safety_v1/main.py",
            ROOT / "modules/common/crop_safety_fable_eval.py",
            ROOT / "modules/common/crop_review.py",
            ROOT / "modules/common/crop_review_setup.py",
            ROOT / "tools/run_safety_qual_caller.py",
        ]:
            content = file.read_bytes()
            h = sha(content)
            dst = E / "code" / f"{h}-{file.name}"
            dst.parent.mkdir(exist_ok=True)
            if not dst.exists():
                dst.write_bytes(content)
            snapshot[
                str(file.relative_to(ROOT)) if file.is_relative_to(ROOT) else str(file)
            ] = h
        rec = {
            "stage": stage,
            "arm": arm,
            "model": MODELS[arm],
            "recovery": recovery,
            "reserved_usd": RESERVES[arm],
            "cost_usd": None,
            "request": str(req.relative_to(ROOT))
            if req.is_relative_to(ROOT)
            else str(req),
            "request_sha256": sha(wire),
            "code_sha256": snapshot,
        }
        d["calls"].append(rec)
        save(LEDGER, d)
        start = time.monotonic()
        try:
            if arm == "fable":
                endpoint = "https://api.anthropic.com/v1/messages"
                headers = {
                    "x-api-key": os.environ["ANTHROPIC_API_KEY"],
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                }
            else:
                endpoint = "https://api.openai.com/v1/responses"
                headers = {
                    "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"],
                    "content-type": "application/json",
                }
            r = httpx.post(endpoint, headers=headers, content=wire, timeout=900)
            raw = r.content
        except Exception as exc:
            rec.update(
                exception=type(exc).__name__,
                latency_ms=round((time.monotonic() - start) * 1000),
            )
            save(LEDGER, d)
            raise
        with res.open("xb") as f:
            f.write(raw)
        rec.update(
            response=str(res.relative_to(ROOT))
            if res.is_relative_to(ROOT)
            else str(res),
            response_sha256=sha(raw),
            http=r.status_code,
            latency_ms=round((time.monotonic() - start) * 1000),
        )
        try:
            env = json.loads(raw)
            assert env.get("model") == MODELS[arm]
            u = env["usage"]
            if arm == "fable":
                uncached = u["input_tokens"]
                cached = u.get("cache_read_input_tokens", 0)
                write = u.get("cache_creation_input_tokens", 0)
                inp = uncached + cached + write
                out = u["output_tokens"]
                think = u.get("output_tokens_details", {}).get("thinking_tokens")
            else:
                inp = u["input_tokens"]
                out = u["output_tokens"]
                details = u.get("input_tokens_details", {})
                cached = details.get("cached_tokens", 0)
                write = details.get("cache_write_tokens", 0)
                uncached = inp - cached - write
                think = u.get("output_tokens_details", {}).get("reasoning_tokens")
            assert all(
                type(x) is int and x >= 0 for x in [inp, out, cached, write, uncached]
            )
            prices = PRICES[arm]
            cost = (
                uncached * prices[0]
                + cached * prices[1]
                + write * prices[2]
                + out * prices[3]
            ) / 1e6
            assert math.isfinite(cost) and cost >= 0
            rec.update(
                cost_usd=cost,
                input_tokens=inp,
                output_tokens=out,
                thinking_tokens=think,
                usage=u,
                served_model=env.get("model"),
            )
            d["spent_usd"] += cost
            if (
                inp > 46000
                or out > (32768 if arm == "fable" else 4096)
                or cost > RESERVES[arm]
            ):
                rec["bound_violation"] = True
                d["closed"] = True
        except (KeyError, ValueError, TypeError, AssertionError):
            rec["billing_unresolved"] = True
        try:
            assert (
                r.status_code == 200
                and not rec.get("bound_violation")
                and not rec.get("billing_unresolved")
            )
            answer, env = parse_response(raw, arm)
            rec["semantic_eligible"] = True
        except Exception as exc:
            rec.update(
                semantic_eligible=False, contract_error=str(exc) or type(exc).__name__
            )
        save(LEDGER, d)
        return r.status_code, raw


def preflight():
    assert sha(GOLDEN.read_bytes()) == GOLDEN_SHA
    truth = json.loads(GOLDEN.read_text())
    cases = []
    requests = {}
    for key, v in matrix():
        parts = inputs(key)
        images = []
        for arm in MODELS:
            b = body(arm, parts)
            bb = image_bytes(b, arm)
            assert len(bb) == 2
            requests[f"classifier:{arm}:{key}"] = [sha(x) for x in bb]
        for bb in image_bytes(body("fable", parts), "fable"):
            im = Image.open(io.BytesIO(bb))
            images.append({"bytes": len(bb), "sha256": sha(bb), "dimensions": im.size})
        cases.append(
            {
                "key": key,
                "verdict": truth[key]["verdict"],
                "golden_relpath": "golden/crop-page-level-safety-repair-048-source-adjudicated.json",
                "images": images,
            }
        )
    for arm in MODELS:
        for key in ["S3", "S4"]:
            f = ROOT / "tests/fixtures/crop_review_offline/approved"
            requests[f"caller:{arm}:{key}"] = [
                sha((f / f"{key}-source.png").read_bytes()),
                sha((f / "images" / f"{key}.png").read_bytes()),
            ]
    p = {
        "base_sha": __import__("subprocess")
        .check_output(["git", "rev-parse", "HEAD"], text=True, cwd=ROOT)
        .strip(),
        "approved": "Conductor Scout107 DocWeb safetyqualification USD60",
        "cap_usd": 60,
        "max_calls": 52,
        "planned_calls": 48,
        "recovery_calls": {"fable": 2, "sol": 2},
        "reserved_plan_usd": 57.26968,
        "case_matrix": cases,
        "caller": [
            "S3 uncertaintyfail beforeoperator",
            "S4 integralbadgepass beforeoperator",
            "zerocandidatepageinventory no paidcall",
        ],
        "request_sources": requests,
        "prompt_sha256": sha(PROMPT.encode()),
        "golden_sha256": sha(GOLDEN.read_bytes()),
        "schema": FORMAT,
        "native_fable_service_tier": "standard_only",
        "models": {
            "fable": "claude-fable-5-2 standard xhigh32768",
            "sol": "gpt-6.1-sol medium4096 high detail defaulttier storefalse",
        },
        "prices_usd_per_million": PRICES,
        "reservation_usd_per_dispatch": RESERVES,
        "judge": "none; deterministicverdict+originalpixel fullpayloadreview",
        "topology": "serial independentrequests no subjectcache",
        "privacy": "Only publicOnward and existing authoredsynthetic; standard30dayAnthropicretention disclosed; no privatepayload/accountchanges",
        "promotion": "classifier22/22pluszero false-safe/fullpayload; S3/S4modelpolicy separatefrom operatormechanics; all production/C5holds preserved",
        "sources": [
            "https://platform.claude.com/docs/en/models/fable-5-2/overview",
            "https://platform.openai.com/pricing",
        ],
        "maxeffort": "unmeasured/unauthorized no sweep",
    }
    E.mkdir(exist_ok=True, parents=True)
    if (E / "preflight.json").exists():
        assert json.loads((E / "preflight.json").read_text()) == p
    else:
        save(E / "preflight.json", p)
    if not LEDGER.exists():
        save(
            LEDGER,
            {
                "id": "088-fable52-safety-20261109",
                "cap_usd": 60,
                "spent_usd": 0,
                "closed": False,
                "calls": [],
            },
        )
    print("preflight22cases17pass5fail;48planned max52;57.26968/60")


def run_case(key, arm, recovery=False):
    stage = f"classifier:{arm}:{key}"
    b = body(arm, inputs(key))
    status, raw = send_native(b, arm, stage, recovery=recovery)
    entry = {"key": key, "arm": arm, "http": status}
    try:
        assert status == 200
        settled = next(
            c
            for c in reversed(json.loads(LEDGER.read_text())["calls"])
            if c["stage"] == stage and c.get("response_sha256") == sha(raw)
        )
        assert settled.get("semantic_eligible") is True, "quarantined usage/contract"
        payload, d = parse_response(raw, arm)
        gold = json.loads(GOLDEN.read_text())[key]["verdict"]
        entry.update(
            answer=payload,
            golden=gold,
            correct=payload["verdict"] == gold,
            false_safe=payload["verdict"] == "pass" and gold == "fail",
        )
    except Exception as exc:
        entry.update(error=str(exc) or type(exc).__name__, capability="notmeasured")
    path = E / "classifier-results.json"
    results = json.loads(path.read_text()) if path.exists() else []
    results.append(entry)
    save(path, results)
    print(json.dumps(entry), flush=True)
    return entry


if __name__ == "__main__":
    if sys.argv[1] == "preflight":
        preflight()
    elif sys.argv[1] == "case":
        run_case(sys.argv[2], sys.argv[3], recovery="--recovery" in sys.argv)
    elif sys.argv[1] == "panel":
        for key, _ in matrix():
            for arm in MODELS:
                stage = f"classifier:{arm}:{key}"
                d = json.loads(LEDGER.read_text())
                prev = [c for c in d["calls"] if c["stage"] == stage]
                if prev:
                    continue
                run_case(key, arm)
