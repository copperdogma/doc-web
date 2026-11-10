# ruff: noqa: E402
"""Offline Carbon qualification/custody guards; no inference."""

import hashlib
import json
import sys
from pathlib import Path
import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks/scripts"))
import carbon_native as native


def test_original_schema_and_source_kept():
    schema = {
        "type": "object",
        "properties": {"x": {"type": "string"}},
        "required": ["x"],
        "additionalProperties": False,
    }
    b = native.body(
        "gemini-4-carbon", "policy", "prompt", [(b"pixels", "image/png")], schema
    )
    assert b["generationConfig"] == {
        "maxOutputTokens": 32768,
        "thinkingConfig": {"thinkingLevel": "HIGH"},
        "responseMimeType": "application/json",
        "responseJsonSchema": schema,
    }
    assert b["systemInstruction"]["parts"][0]["text"] == "policy"
    assert b["contents"][0]["parts"][1]["inlineData"]["data"] == "cGl4ZWxz"


@pytest.mark.parametrize(
    "change",
    [
        {"modelVersion": "gemini-3.8-flash"},
        {"candidates": [{"finishReason": "MAX_TOKENS"}]},
        {"usageMetadata": {"promptTokenCount": 1}},
        {"error": {"code": 500}},
    ],
)
def test_fail_closed_before_semantics(change):
    d = {
        "modelVersion": "gemini-4-carbon",
        "candidates": [
            {
                "finishReason": "STOP",
                "content": {"role": "model", "parts": [{"text": "{}"}]},
            }
        ],
        "usageMetadata": {"promptTokenCount": 1, "candidatesTokenCount": 1},
    }
    d.update(change)
    with pytest.raises(ValueError):
        native.parse(d, "gemini-4-carbon")


def test_hard_cap_counts_unknown_and_prevents_network(tmp_path, monkeypatch):
    g = native.guard
    monkeypatch.setattr(g, "RESULTS", tmp_path / "raw")
    monkeypatch.setattr(g, "E", tmp_path / "durable")
    g.RESULTS.mkdir()
    (g.E / "rendered").mkdir(parents=True)
    b = native.body("gemini-4-carbon", "", "prompt", [(b"pixels", "image/png")])
    (g.E / "rendered/test.json").write_text(json.dumps(b))
    (g.E / "preflight.json").write_text(
        json.dumps(
            {
                "matrix": [
                    {
                        "stage": "test",
                        "model": "gemini-4-carbon",
                        "request_sha256": hashlib.sha256(
                            (g.E / "rendered/test.json").read_bytes()
                        ).hexdigest(),
                    }
                ]
            }
        )
    )
    monkeypatch.setenv("CARBON_STAGE", "test")
    (g.RESULTS / "ledger.json").write_text(
        json.dumps(
            {
                "spent_usd": 9.7,
                "closed": False,
                "calls": [{"stage": "unknown", "reserved_usd": 0.1, "cost_usd": None}],
            }
        )
    )
    with pytest.raises(RuntimeError, match="hard10USD"):
        g.send(
            lambda *a, **k: pytest.fail("network"),
            None,
            httpx.Request(
                "POST",
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-4-carbon:generateContent",
                json=b,
            ),
        )


def test_reject_payload_drift_before_network(tmp_path, monkeypatch):
    g = native.guard
    monkeypatch.setattr(g, "E", tmp_path)
    (tmp_path / "rendered").mkdir()
    monkeypatch.setenv("CARBON_STAGE", "test")
    (tmp_path / "rendered/test.json").write_text("{}")
    (tmp_path / "preflight.json").write_text(
        json.dumps(
            {
                "matrix": [
                    {
                        "stage": "test",
                        "model": "gemini-4-carbon",
                        "request_sha256": hashlib.sha256(b"{}").hexdigest(),
                    }
                ]
            }
        )
    )
    with pytest.raises(RuntimeError, match="differs"):
        g.send(
            lambda *a, **k: pytest.fail("network"),
            None,
            httpx.Request(
                "POST",
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-4-carbon:generateContent",
                json={"contents": []},
            ),
        )


def prepared_guard(tmp_path, monkeypatch):
    g = native.guard
    monkeypatch.setattr(g, "ROOT", tmp_path)
    monkeypatch.setattr(g, "RESULTS", tmp_path / "raw")
    monkeypatch.setattr(g, "E", tmp_path / "evidence")
    g.RESULTS.mkdir()
    (g.E / "rendered").mkdir(parents=True)
    b = native.body("gemini-4-carbon", "", "prompt", [(b"pixels", "image/png")])
    planned = g.E / "rendered/test.json"
    planned.write_text(json.dumps(b))
    (g.E / "preflight.json").write_text(
        json.dumps(
            {
                "matrix": [
                    {
                        "stage": "test",
                        "model": "gemini-4-carbon",
                        "request_sha256": hashlib.sha256(
                            planned.read_bytes()
                        ).hexdigest(),
                    }
                ]
            }
        )
    )
    (g.RESULTS / "ledger.json").write_text(
        json.dumps({"spent_usd": 0, "closed": False, "calls": []})
    )
    monkeypatch.setenv("CARBON_STAGE", "test")
    request = httpx.Request(
        "POST",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-4-carbon:generateContent",
        json=b,
    )
    return g, b, request


@pytest.mark.parametrize(
    "usage",
    [
        {"promptTokenCount": 100},
        {
            "promptTokenCount": 100,
            "candidatesTokenCount": 10,
            "cachedContentTokenCount": 101,
        },
    ],
)
def test_invalid_usage_preserves_full_unknown_reservation(tmp_path, monkeypatch, usage):
    g, b, req = prepared_guard(tmp_path, monkeypatch)
    response = httpx.Response(
        200,
        json={"modelVersion": "gemini-4-carbon", "usageMetadata": usage},
        request=req,
    )
    g.send(lambda *a, **k: response, None, req)
    d = json.loads((g.RESULTS / "ledger.json").read_text())
    assert d["spent_usd"] == 0
    assert d["calls"][0]["cost_usd"] is None and d["calls"][0]["billing_unresolved"]
    assert Path(g.ROOT / d["calls"][0]["response"]).read_bytes() == response.content


def test_nonjson_failure_preserves_raw_and_unknown(tmp_path, monkeypatch):
    g, b, req = prepared_guard(tmp_path, monkeypatch)
    response = httpx.Response(502, content=b"upstream unavailable", request=req)
    g.send(lambda *a, **k: response, None, req)
    d = json.loads((g.RESULTS / "ledger.json").read_text())
    assert d["calls"][0]["billing_unresolved"]
    assert d["calls"][0]["cost_usd"] is None


def test_model_in_endpoint_is_bound_to_selected_stage(tmp_path, monkeypatch):
    g, b, req = prepared_guard(tmp_path, monkeypatch)
    wrong = httpx.Request(
        "POST",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent",
        json=b,
    )
    with pytest.raises(RuntimeError, match="stage model"):
        g.send(lambda *a, **k: pytest.fail("network"), None, wrong)


def _two_process_worker(stage, entered, release):
    import os
    import carbon_native as module

    os.environ["CARBON_STAGE"] = stage
    b = json.loads((module.guard.E / "rendered" / f"{stage}.json").read_text())
    req = httpx.Request(
        "POST",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-4-carbon:generateContent",
        json=b,
    )

    def transport(*args, **kwargs):
        entered.put(stage)
        if not release.wait(5):
            raise RuntimeError("test barrier timeout")
        return httpx.Response(
            200,
            json={
                "modelVersion": "gemini-4-carbon",
                "usageMetadata": {"promptTokenCount": 100, "candidatesTokenCount": 10},
            },
            request=req,
        )

    module.guard.send(transport, None, req)


def test_two_process_reservations_and_custody_are_unique(tmp_path, monkeypatch):
    import multiprocessing

    g, b, req = prepared_guard(tmp_path, monkeypatch)
    (g.E / "rendered/other.json").write_text(json.dumps(b))
    plan = json.loads((g.E / "preflight.json").read_text())
    plan["matrix"].append(
        {
            "stage": "other",
            "model": "gemini-4-carbon",
            "request_sha256": hashlib.sha256(
                (g.E / "rendered/other.json").read_bytes()
            ).hexdigest(),
        }
    )
    (g.E / "preflight.json").write_text(json.dumps(plan))
    ctx = multiprocessing.get_context("fork")
    entered = ctx.Queue()
    release = ctx.Event()
    workers = [
        ctx.Process(target=_two_process_worker, args=(stage, entered, release))
        for stage in ["test", "other"]
    ]
    for w in workers:
        w.start()
    try:
        assert {entered.get(timeout=5), entered.get(timeout=5)} == {"test", "other"}
        interim = json.loads((g.RESULTS / "ledger.json").read_text())
        assert len(interim["calls"]) == 2 and all(
            x["in_flight"] and x["cost_usd"] is None for x in interim["calls"]
        )
    finally:
        release.set()
        for w in workers:
            w.join(5)
    assert [w.exitcode for w in workers] == [0, 0]
    d = json.loads((g.RESULTS / "ledger.json").read_text())
    assert len(d["calls"]) == 2
    assert (
        len({x["request"] for x in d["calls"]}) == 2
        and len({x["response"] for x in d["calls"]}) == 2
    )
    assert all(not x["in_flight"] and x["cost_usd"] is not None for x in d["calls"])
    assert d["spent_usd"] == pytest.approx(sum(x["cost_usd"] for x in d["calls"]))
