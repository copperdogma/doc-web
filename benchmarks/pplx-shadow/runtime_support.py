"""Eval-only native transport boundary: captures real runtime requests, caps every send."""

from __future__ import annotations
import fcntl
import hashlib
import io
import json
import os
from pathlib import Path
import time
import threading
from types import SimpleNamespace
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/evals/evidence/067-warning-integration"
RAW = ROOT / "benchmarks/results/pplx-warning-integration-20261006"
CAP = 4.0
MODEL = "gpt-4.1-2025-04-14"
PPLX = "pplx-decider-v1.1-27b"
REAL_OPEN = urllib.request.OpenerDirector.open
PENDING_THREADS = []


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")
    temp.replace(path)


def native_mock(payload):
    labels = payload["questions"]["status"]["criteria"]
    return {
        "model": PPLX,
        "usage": {"input_tokens": 500, "output_tokens": 1},
        "answers": {
            "status": {
                "type": "choice",
                "choice": "conformant",
                "confidence": 0.95,
                "probabilities": {k: float(k == "conformant") for k in labels},
            }
        },
    }


def planner_mock():
    return {
        "analysis_summary": {
            "default_note_policy": "Preserve source-supported note ownership"
        },
        "pattern_families": [
            {
                "pattern_id": "observed",
                "member_chapters": [f"chapter-{j:03d}.html" for j in range(1, 4)],
                "canonical_headers": [
                    "NAME",
                    "BORN",
                    "MARRIED",
                    "SPOUSE",
                    "BOY",
                    "GIRL",
                    "DIED",
                ],
                "document_local_conventions": {
                    "table_fragmentation": "Follow source page breaks",
                    "marginal_or_handwritten_notes": "Preserve source attachment",
                },
                "allowed_variants": ["Capitalization only"],
            }
        ],
        "chapter_findings": [
            {
                "chapter_basename": f"chapter-{j:03d}.html",
                "pattern_id": "observed",
                "status": "conformant",
                "issue_types": [],
            }
            for j in range(1, 4)
        ],
    }


def send(payload, arm, qualification=False, opener=None, request=None):
    RAW.mkdir(parents=True, exist_ok=True, mode=0o700)
    RAW.chmod(0o700)
    kind = "qualification" if qualification else arm
    encoded = (
        request.data
        if request is not None
        else json.dumps(payload, ensure_ascii=False, allow_nan=False).encode()
    )
    if json.loads(encoded) != payload:
        raise RuntimeError("Wire/body mismatch")
    if len(encoded) + 512 > 64000:
        raise RuntimeError("Input reservation admission exceeds64000")
    if arm == "planner":
        if (
            payload["model"] != MODEL
            or not any(k in payload for k in ("max_tokens", "max_completion_tokens"))
            or any(
                type(payload[k]) is not int or not 1 <= payload[k] <= 8000
                for k in ("max_tokens", "max_completion_tokens")
                if k in payload
            )
            or payload.get("response_format") != {"type": "json_object"}
            or payload.get("stream", False)
            or payload.get("n", 1) != 1
        ):
            raise RuntimeError("Planner model/output reservation mismatch")
        amount = 0.192
    else:
        if payload["model"] != PPLX:
            raise RuntimeError("Candidate identity mismatch")
        amount = 0.00128
    with (RAW / "ledger.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        lp = EVIDENCE / "ledger.json"
        ledger = (
            json.loads(lp.read_text())
            if lp.exists()
            else {"cap_usd": CAP, "spent_usd": 0.0, "unknown_usd": 0.0, "calls": []}
        )
        if ledger.get("closed"):
            raise RuntimeError("Ledger closed")
        if ledger["unknown_usd"]:
            raise RuntimeError("Prior unknown delivery; stop before another dispatch")
        limits = {"planner": 12, "candidate": 36, "qualification": 2}
        if sum(c["kind"] == kind for c in ledger["calls"]) >= limits[kind]:
            raise RuntimeError("Hard request count gate")
        if ledger["spent_usd"] + ledger["unknown_usd"] + amount > CAP:
            raise RuntimeError("HardUSD4 gate")
        name = f"{len(ledger['calls']) + 1:03d}-{arm}"
        entry = {
            "name": name,
            "arm": arm,
            "kind": kind,
            "run_id": os.environ.get("PPLX_SHADOW_RUN_ID"),
            "reserve_usd": amount,
            "status": "dispatched",
            "request_sha256": hashlib.sha256(encoded).hexdigest(),
            "request_bytes": len(encoded),
        }
        ledger["calls"].append(entry)
        ledger["unknown_usd"] += amount
        write(lp, ledger)
        (RAW / (name + ".request.json")).write_bytes(encoded)
        started = time.monotonic()
        if request is None:
            key = os.environ[
                "OPENAI_API_KEY" if arm == "planner" else "DOC_WEB_PERPLEXITY_API_KEY"
            ]
            url = (
                "https://api.openai.com/v1/chat/completions"
                if arm == "planner"
                else "https://api.perplexity.ai/v1/decisions"
            )
            request = urllib.request.Request(
                url,
                data=encoded,
                headers={
                    "Authorization": "Bearer " + key,
                    "Content-Type": "application/json",
                },
            )
        try:
            response = REAL_OPEN(
                opener or urllib.request.build_opener(),
                request,
                timeout=120 if arm == "planner" else 2.0,
            )
            with response:
                content = response.read(65_537 if arm == "candidate" else 2_000_001)
                if len(content) > (65_536 if arm == "candidate" else 2_000_000):
                    raise ValueError("Native response byte limit")
                status = response.status
            (RAW / (name + ".response.json")).write_bytes(content)
            entry.update(
                latency_ms=(time.monotonic() - started) * 1000,
                http_status=status,
                response_sha256=hashlib.sha256(content).hexdigest(),
                response_bytes=len(content),
            )
            raw = json.loads(content)
            if (
                status != 200
                or raw.get("error")
                or raw.get("model") != (MODEL if arm == "planner" else PPLX)
            ):
                raise ValueError("Native status/identity")
            usage = raw.get("usage", {})
            if arm == "planner":
                if (
                    len(raw.get("choices", [])) != 1
                    or raw["choices"][0].get("finish_reason") != "stop"
                    or raw["choices"][0]["message"].get("refusal")
                ):
                    raise ValueError("Incomplete/refusal")
                for k in ["prompt_tokens", "completion_tokens"]:
                    if type(usage.get(k)) is not int or usage[k] < 0:
                        raise ValueError("Usage")
                cached = usage.get("prompt_tokens_details", {}).get("cached_tokens", 0)
                if type(cached) is not int or not 0 <= cached <= usage["prompt_tokens"]:
                    raise ValueError("Cachedusage")
                cost = (
                    (usage["prompt_tokens"] - cached) * 2
                    + cached * 0.5
                    + usage["completion_tokens"] * 8
                ) / 1e6
                json.loads(raw["choices"][0]["message"]["content"])
            else:
                from modules.validate.plan_onward_document_consistency_v1.pplx_shadow import (
                    parse_response,
                )

                judgment = parse_response(raw)
                cost = judgment.cost_usd
            if cost > amount:
                raise ValueError("Exceeded reservation")
            ledger["unknown_usd"] -= amount
            ledger["spent_usd"] += cost
            entry.update(
                status="complete", cost_usd=cost, usage=usage, served_model=raw["model"]
            )
            write(lp, ledger)
            return raw
        except urllib.error.HTTPError as err:
            content = err.read()
            (RAW / (name + ".response.json")).write_bytes(content)
            entry.update(
                status="http_error",
                http_status=err.code,
                response_sha256=hashlib.sha256(content).hexdigest(),
                response_bytes=len(content),
                latency_ms=(time.monotonic() - started) * 1000,
            )
            write(lp, ledger)
            raise RuntimeError("HTTP failure retained with unknown reserve") from None
        except Exception as exc:
            entry.update(
                status="unresolved",
                exception_type=type(exc).__name__,
                latency_ms=(time.monotonic() - started) * 1000,
            )
            write(lp, ledger)
            raise RuntimeError("Native failure retained with unknown reserve") from None


class EvalOpenAI:
    def __init__(self, *args, **kwargs):
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        kwargs.pop("timeout", None)
        if os.environ.get("PPLX_SHADOW_TRANSPORT_MODE") == "offline":
            payload = planner_mock()
            raw = {
                "model": kwargs["model"],
                "usage": {"prompt_tokens": 100, "completion_tokens": 100},
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {"content": json.dumps(payload)},
                    }
                ],
            }
        else:
            raw = send(kwargs, "planner")
        return SimpleNamespace(
            model=raw["model"],
            usage=SimpleNamespace(**raw["usage"]),
            choices=[
                SimpleNamespace(
                    finish_reason=x["finish_reason"],
                    message=SimpleNamespace(**x["message"]),
                )
                for x in raw["choices"]
            ],
        )


def candidate_open(self, request, *args, **kwargs):
    if request.full_url != "https://api.perplexity.ai/v1/decisions":
        raise RuntimeError("Eval transport forbids unexpected network")
    payload = json.loads(request.data)
    if os.environ.get("PPLX_SHADOW_TRANSPORT_MODE") == "offline":
        failure = os.environ.get("PPLX_SHADOW_OFFLINE_FAILURE")
        if failure == "timeout":
            raise TimeoutError("offline timeout")
        raw = {} if failure == "malformed" else native_mock(payload)
        if failure == "disagreement":
            answer = raw["answers"]["status"]
            answer.update(choice="row_semantic_issue", confidence=0.42,
                          probabilities={k: float(k == "row_semantic_issue") for k in payload["questions"]["status"]["criteria"]})
    else:
        PENDING_THREADS.append(threading.current_thread())
        raw = send(payload, "candidate", opener=self, request=request)
    response = io.BytesIO(json.dumps(raw).encode())
    response.status = 200
    return response


def settle_threads():
    for worker in PENDING_THREADS:
        if worker is not threading.current_thread() and worker.is_alive():
            worker.join(timeout=5.0)
