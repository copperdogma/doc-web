"""Combined campaign admission and raw custody tests; never real inference."""

import json
from pathlib import Path
import pytest
import httpx
from benchmarks.scripts import safety_qual_088 as q


@pytest.fixture
def campaign(tmp_path, monkeypatch):
    monkeypatch.setattr(q, "E", tmp_path)
    monkeypatch.setattr(q, "LEDGER", tmp_path / "ledger.json")
    monkeypatch.setattr(q, "ROOT", Path(__file__).resolve().parents[1])
    monkeypatch.setattr(q, "admission_body", lambda *a: None)
    q.save(q.LEDGER, {"spent_usd": 0, "closed": False, "calls": []})
    return tmp_path


def test_unknown_exposure_blocks_dispatch(campaign, monkeypatch):
    q.save(
        q.LEDGER,
        {
            "spent_usd": 58,
            "closed": False,
            "calls": [
                {
                    "arm": "fable",
                    "stage": "prior",
                    "recovery": False,
                    "reserved_usd": 2,
                    "cost_usd": None,
                }
            ],
        },
    )
    monkeypatch.setattr(q.httpx, "post", lambda *a, **k: pytest.fail("network"))
    with pytest.raises(AssertionError, match="hard60cap"):
        q.send_native({"model": q.MODELS["fable"]}, "fable", "new")


def test_valid_quality_result_cannot_be_retried(campaign, monkeypatch):
    q.save(
        q.LEDGER,
        {
            "spent_usd": 1,
            "closed": False,
            "calls": [
                {
                    "arm": "fable",
                    "stage": "case",
                    "recovery": False,
                    "reserved_usd": 2,
                    "cost_usd": 1,
                    "semantic_eligible": True,
                }
            ],
        },
    )
    monkeypatch.setattr(q.httpx, "post", lambda *a, **k: pytest.fail("network"))
    with pytest.raises(AssertionError, match="no retry"):
        q.send_native({"model": q.MODELS["fable"]}, "fable", "case", recovery=True)


def test_exact_wire_and_raw_retained_before_invalid_parse(campaign, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "synthetic-placeholder")
    sent = []

    def post(url, **kw):
        sent.append(kw["content"])
        return httpx.Response(402, content=b'{"error":{"type":"billing"}}')

    monkeypatch.setattr(q.httpx, "post", post)
    status, raw = q.send_native({"model": q.MODELS["fable"]}, "fable", "case")
    ledger = json.loads(q.LEDGER.read_text())
    r = ledger["calls"][0]
    assert status == 402 and r["cost_usd"] is None and r["semantic_eligible"] is False
    assert (q.ROOT / r["request"]).read_bytes() == sent[0]
    assert (q.ROOT / r["response"]).read_bytes() == raw


def test_standard_native_tier_is_required_before_dispatch():
    key = q.matrix()[0][0]
    b = q.body("fable", q.inputs(key))
    assert b["service_tier"] == "standard_only"
    q.admission_body(b, "fable", f"classifier:fable:{key}")
    b.pop("service_tier")
    with pytest.raises(AssertionError):
        q.admission_body(b, "fable", f"classifier:fable:{key}")


def test_bound_invalid_usage_is_quarantined(campaign, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "synthetic-placeholder")
    payload = {
        "verdict": "pass",
        "has_page_text": False,
        "excessive_blank": False,
        "reason": "synthetic",
    }
    d = {
        "id": "msg_offline",
        "type": "message",
        "model": q.MODELS["fable"],
        "stop_reason": "end_turn",
        "content": [{"type": "text", "text": json.dumps(payload)}],
        "usage": {
            "input_tokens": 46001,
            "output_tokens": 10,
            "service_tier": "standard",
            "speed": "standard",
        },
    }
    monkeypatch.setattr(q.httpx, "post", lambda *a, **kw: httpx.Response(200, json=d))
    q.send_native({"model": q.MODELS["fable"]}, "fable", "case")
    ledger = json.loads(q.LEDGER.read_text())
    r = ledger["calls"][0]
    assert ledger["closed"] and r["bound_violation"] and not r["semantic_eligible"]
    assert r["cost_usd"] > 0 and (q.ROOT / r["response"]).exists()


def test_optimized_python_cannot_disable_admission():
    import subprocess
    import sys

    p = subprocess.run(
        [sys.executable, "-O", "-c", "from benchmarks.scripts import safety_qual_088"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )
    assert p.returncode != 0 and "Optimized Python cannot run" in p.stderr


def test_case_matches_own_receipt_not_unrelated_last_row(campaign, monkeypatch):
    key = q.matrix()[0][0]
    arm = "fable"
    stage = f"classifier:{arm}:{key}"
    raw = b"captured-case"

    def fake_send(*a, **kw):
        q.save(
            q.LEDGER,
            {
                "calls": [
                    {
                        "stage": stage,
                        "response_sha256": q.sha(raw),
                        "semantic_eligible": True,
                    },
                    {
                        "stage": "unrelated",
                        "response_sha256": "other",
                        "semantic_eligible": False,
                    },
                ]
            },
        )
        return 200, raw

    monkeypatch.setattr(q, "send_native", fake_send)
    answer = {
        "verdict": "pass",
        "has_page_text": False,
        "excessive_blank": False,
        "reason": "offlinefixture",
    }
    monkeypatch.setattr(q, "parse_response", lambda *args: (answer, {}))
    assert q.run_case(key, arm)["correct"] is True
