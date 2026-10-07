"""Scout088 item3: serial synthetic text-only campaign; default is zero-cost preflight."""

from __future__ import annotations
import argparse
import fcntl
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
OUT = ROOT / "docs/evals/evidence/064-pplx"
RAW = ROOT / "benchmarks/results/pplx-consistency-20261006"
CAP = 2.0
ARMS = ("pplx", "jev", "decisions", "gpt41")
MODELS = dict(
    pplx="pplx-decider-v1.1-27b",
    jev="jev-1.13.0",
    decisions="gpt-6-luna",
    gpt41="gpt-4.1-2025-04-14",
)
KEYS = dict(
    pplx="DOC_WEB_PERPLEXITY_API_KEY",
    jev="DOC_WEB_TYPESAFE_API_KEY",
    decisions="OPENAI_API_KEY",
    gpt41="OPENAI_API_KEY",
)
URLS = dict(
    pplx="https://api.perplexity.ai/v1/decisions",
    jev="https://api.typesafe.ai/v1/systemone",
    decisions="https://api.openai.com/v1/decisions",
    gpt41="https://api.openai.com/v1/chat/completions",
)
spec = importlib.util.spec_from_file_location("pplx_legacy", HERE / "run.py")
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")
    tmp.replace(path)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def body(arm, state):
    if arm in ("pplx", "jev"):
        b = legacy.payload("jev", state)
        b["model"] = MODELS[arm]
        return b
    if arm == "gpt41":
        return legacy.payload("gpt", state)
    return {
        "model": MODELS[arm],
        "input": json.dumps(state, ensure_ascii=False),
        "questions": [
            {
                "type": "choice",
                "name": "status",
                "instructions": legacy.INSTRUCTION,
                "choices": [
                    {"value": k, "description": v} for k, v in legacy.LABELS.items()
                ],
            }
        ],
    }


def parse(arm, raw):
    if arm == "gpt41":
        return legacy.parse("gpt", raw)
    if raw.get("model") != MODELS[arm] or raw.get("error") or "status" in raw:
        raise ValueError("identity/error/status")
    usage = raw.get("usage", {})
    for k in ("input_tokens", "output_tokens"):
        if type(usage.get(k)) is not int or usage[k] < 0:
            raise ValueError("usage")
    if arm == "decisions":
        answers = raw.get("answers", [])
        if len(answers) != 1 or answers[0].get("name") != "status":
            raise ValueError("answer count/name")
        a = answers[0]
        ps = a.get("probabilities", [])
        p = {v["value"]: v["probability"] for v in ps}
        if len(ps) != len(p):
            raise ValueError("duplicate probabilities")
    else:
        if set(raw.get("answers", {})) != {"status"}:
            raise ValueError("answer names")
        a = raw["answers"]["status"]
        p = a.get("probabilities", {})
    c = a.get("confidence")
    label = a.get("choice")
    if a.get("type") != "choice" or set(p) != set(legacy.LABELS) or label not in p:
        raise ValueError("choice contract/refusal")
    if any(
        type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1
        for v in [*p.values(), c]
    ):
        raise ValueError("probability/confidence")
    if abs(sum(p.values()) - 1) > 0.002 or p[label] < max(p.values()):
        raise ValueError("probability sum/argmax")
    return (
        label,
        c,
        usage["input_tokens"]
        * {"pplx": 0.02, "jev": 0.042, "decisions": 0.10}[arm]
        / 1e6,
    )


def reserve(arm, payload):
    # Native request byte length upper-bounds text tokens with 512 framing headroom.
    # One typed question; no images; enforce complete request+framing <=4096.
    bound = len(json.dumps(payload, ensure_ascii=False).encode()) + 512
    if bound > 4096:
        raise RuntimeError("text admission >4096; recheck reservation before spending")
    return (
        bound * {"pplx": 0.02, "jev": 0.042, "decisions": 0.1, "gpt41": 2}[arm]
        + (160 * 8 if arm == "gpt41" else 0)
    ) / 1e6


def fixtures():
    return json.loads((HERE / "fixtures.json").read_text())


def preflight():
    cases = fixtures()
    review = json.loads(
        (ROOT / "docs/evals/artifacts/jev-consistency-20260921/review.json").read_text()
    )
    assert review["approved_fixture_sha256"] == sha(HERE / "fixtures.json")
    matrix = [
        {
            "id": f"r{rep}-{c['id']}",
            "requests": {a: body(a, c["input"]) for a in ARMS},
            "gold": c["gold"],
            "domain": c["domain"],
        }
        for rep in (1, 2)
        for c in cases
    ]
    total = sum(reserve(a, x["requests"][a]) for x in matrix for a in ARMS)
    total += sum(3 * reserve("gpt41", x["requests"]["gpt41"]) for x in matrix)
    probes = sum(reserve(a, body(a, cases[0]["input"])) for a in ARMS)
    assert total + probes < CAP
    sources = {}
    for path in [
        HERE / "fixtures.json",
        HERE / "run.py",
        HERE / "detector.py",
        HERE / "plan.md",
        Path(__file__),
        ROOT / "modules/validate/validate_onward_genealogy_consistency_v1/main.py",
    ]:
        relative = str(path.relative_to(ROOT))
        sources[relative] = sha(path)
        dest = OUT / "snapshots" / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
    proof = {
        "base_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "branch": subprocess.check_output(
            ["git", "branch", "--show-current"], cwd=ROOT, text=True
        ).strip(),
        "sources": sources,
        "unique_cases": 20,
        "sources_count": 2,
        "repeats": 2,
        "serial_independent_requests": 40,
        "candidate_calls": 120,
        "baseline_calls": 40,
        "maximum_real_fallback_calls": 120,
        "cache": False,
        "concurrency": 1,
        "judge": "maintained exact typed-label scorer plus independent source review; no paid judge",
        "fallback": "explicit uncertain remains review; otherwise confidence<0.8 real GPT4.1",
        "image_lane": "excluded",
        "payload_class": "synthetic",
        "cap_usd": CAP,
        "full_matrix_reservation_usd": total,
        "qualification_reservation_usd": probes,
        "recovery_headroom_usd": CAP - total - probes,
        "live_contract_qualified": False,
        "provider_sources": [
            "https://docs.perplexity.ai/api-reference/decisions-post",
            "https://docs.typesafe.ai/models",
            "https://developers.openai.com/api/docs/guides/decisions",
        ],
        "checked_date": "2026-10-06",
    }
    write(OUT / "rendered.json", matrix)
    write(OUT / "preflight.json", proof)
    write(
        OUT / "deterministic-reference.json",
        [
            {
                "id": c["id"],
                "gold": c["gold"],
                "structural": legacy.deterministic(c["input"]),
            }
            for c in cases
        ],
    )
    print(
        json.dumps(
            {
                "cases": 40,
                "reservation_usd": total + probes,
                "headroom_usd": CAP - total - probes,
                "live_contract": "unqualified",
            }
        )
    )


def ready():
    proof = json.loads((OUT / "preflight.json").read_text())
    for name, digest in proof["sources"].items():
        if sha(ROOT / name) != digest:
            raise RuntimeError("frozen source mismatch: " + name)
    missing = sorted({KEYS[a] for a in ARMS if not os.environ.get(KEYS[a])})
    if missing:
        raise RuntimeError("Missing configured owner variables: " + ", ".join(missing))


def call(arm, payload, name):
    path = OUT / "ledger.json"
    ledger = (
        json.loads(path.read_text())
        if path.exists()
        else {"cap_usd": CAP, "spent_usd": 0.0, "unknown_usd": 0.0, "calls": []}
    )
    prior = next((x for x in ledger["calls"] if x["name"] == name), None)
    if prior:
        if prior["status"] == "complete":
            return prior
        raise RuntimeError(
            "Unresolved prior dispatch; inspect raw evidence before bounded recovery"
        )
    if ledger["unknown_usd"]:
        raise RuntimeError("Unresolved exposure; no additional dispatch")
    amount = reserve(arm, payload)
    if ledger["spent_usd"] + ledger["unknown_usd"] + amount > CAP:
        raise RuntimeError("Hard USD2 cap")
    encoded = json.dumps(payload, ensure_ascii=False).encode()
    entry = {
        "name": name,
        "arm": arm,
        "reserve_usd": amount,
        "status": "dispatched",
        "request_sha256": hashlib.sha256(encoded).hexdigest(),
    }
    ledger["calls"].append(entry)
    ledger["unknown_usd"] += amount
    write(path, ledger)
    RAW.mkdir(parents=True, exist_ok=True, mode=0o700)
    RAW.chmod(0o700)
    (RAW / (name + ".request.json")).write_bytes(encoded)
    started = time.monotonic()
    req = urllib.request.Request(
        URLS[arm],
        data=encoded,
        headers={
            "Authorization": "Bearer " + os.environ[KEYS[arm]],
            "Content-Type": "application/json",
        },
    )
    try:
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                content, status = response.read(), response.status
        except urllib.error.HTTPError as err:
            content, status = err.read(), err.code
        entry["latency_ms"] = (time.monotonic() - started) * 1000
        (RAW / (name + ".response.json")).write_bytes(content)
        entry.update(
            response_sha256=hashlib.sha256(content).hexdigest(),
            response_bytes=len(content),
            http_status=status,
        )
        write(path, ledger)
        if status != 200:
            raise ValueError("HTTP failure retained; unknown billing reserved")
        raw = json.loads(content)
        label, confidence, cost = parse(arm, raw)
        if cost > amount:
            raise ValueError("usage exceeds reservation; fail closed")
        entry.update(
            status="complete",
            label=label,
            confidence=confidence,
            cost_usd=cost,
            usage=raw["usage"],
            served_model=raw["model"],
        )
        ledger["unknown_usd"] -= amount
        ledger["spent_usd"] += cost
        write(path, ledger)
        return entry
    except Exception as exc:
        entry.update(status="unresolved", error_type=type(exc).__name__)
        write(path, ledger)
        raise RuntimeError(
            "Provider/contract failure; retained raw, unknown reserve and source; inspect before recovery"
        ) from None


def qualify():
    ready()
    for arm in ARMS:
        call(arm, body(arm, fixtures()[0]["input"]), "qualification-" + arm)
    write(
        OUT / "qualification.json",
        {
            "qualified": list(ARMS),
            "adapter_parity": "native body and parser are same function used by campaign",
            "served_identity_limit": "model echo is not cryptographic checkpoint verification",
        },
    )


def run():
    ready()
    q = json.loads((OUT / "qualification.json").read_text())
    assert q["qualified"] == list(ARMS)
    rows = []
    for rep in (1, 2):
        for c in fixtures():
            identity = f"r{rep}-{c['id']}"
            g = call("gpt41", body("gpt41", c["input"]), identity + "-gpt41")
            rows.append(dict(g, id=identity, gold=c["gold"], arm="gpt41"))
            for arm in ARMS[:3]:
                r = call(arm, body(arm, c["input"]), identity + "-" + arm)
                rows.append(dict(r, id=identity, gold=c["gold"], arm=arm))
                if r["label"] != "uncertain" and r["confidence"] < 0.8:
                    fallback = call(
                        "gpt41",
                        body("gpt41", c["input"]),
                        identity + "-" + arm + "-fallback",
                    )
                    casc = dict(
                        fallback,
                        cost_usd=r["cost_usd"] + fallback["cost_usd"],
                        latency_ms=r["latency_ms"] + fallback["latency_ms"],
                        fallback=True,
                    )
                else:
                    casc = dict(r, fallback=False)
                rows.append(
                    dict(casc, id=identity, gold=c["gold"], arm=arm + "-cascade")
                )
            write(OUT / "results.json", rows)
    summary = {}
    for arm in sorted({x["arm"] for x in rows}):
        chosen = [x for x in rows if x["arm"] == arm]
        summary[arm] = dict(
            legacy.metrics(chosen),
            review_count=sum(x["label"] == "uncertain" for x in chosen),
            fallback_count=sum(x.get("fallback", False) for x in chosen),
        )
    write(OUT / "summary.json", summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["preflight", "qualify", "run"])
    args = parser.parse_args()
    if args.mode == "preflight":
        preflight()
    else:
        RAW.mkdir(parents=True, exist_ok=True, mode=0o700)
        RAW.chmod(0o700)
        with (RAW / "dispatch.lock").open("w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            (qualify if args.mode == "qualify" else run)()


if __name__ == "__main__":
    main()
