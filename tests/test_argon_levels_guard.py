"""Meaningful offline checks for native receipt collision and cap recovery."""

import importlib.util
import json
import multiprocessing
import time
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "argon_levels_guard_test", ROOT / "benchmarks/providers/argon_levels_guard.py"
)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def request():
    return httpx.Request(
        "POST",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-4-argon:generateContent",
        json={
            "contents": [
                {"parts": [{"inlineData": {"mimeType": "image/png", "data": "tiny"}}]}
            ],
            "generationConfig": {
                "maxOutputTokens": 32768,
                "thinkingConfig": {"thinkingLevel": "medium"},
            },
        },
    )


def fake_send(client, req, **kwargs):
    time.sleep(0.02)
    return httpx.Response(
        200,
        json={
            "modelVersion": "gemini-4-argon",
            "usageMetadata": {
                "promptTokenCount": 100,
                "candidatesTokenCount": 10,
                "thoughtsTokenCount": 10,
            },
        },
        request=req,
    )


def worker(root, stage):
    import os

    guard.RESULTS = Path(root)
    os.environ["ARGON_STAGE"] = stage
    guard.guarded_send(fake_send, None, request())


def init(tmp_path, cap=15):
    import hashlib

    guard.RESULTS = tmp_path
    guard.EVIDENCE = tmp_path / "evidence"
    guard.EVIDENCE.mkdir(exist_ok=True)
    guard.OLD_LEDGER = tmp_path / "old-ledger.json"
    guard.OLD_LEDGER.write_text('{"closed": true}')
    digest = hashlib.sha256(
        json.dumps(json.loads(request().content), sort_keys=True).encode()
    ).hexdigest()
    guard.write(
        guard.EVIDENCE / "freeze.json",
        {
            "old_ledger_sha256": hashlib.sha256(
                guard.OLD_LEDGER.read_bytes()
            ).hexdigest(),
            "old_maximum_exposure_usd": 0.78369925,
            "matrix": [
                {
                    "stage": stage,
                    "request_sha256": digest,
                    "lane": "table",
                    "level": "medium",
                }
                for stage in ("0", "1", "failed", "next", "same", "new")
            ],
        },
    )
    guard.write(
        tmp_path / "ledger.json",
        {"cap_usd": cap, "spent_usd": 0, "calls": [], "closed": False},
    )


def test_concurrent_calls_keep_distinct_receipts(tmp_path):
    init(tmp_path)
    ctx = multiprocessing.get_context("fork")
    workers = [
        ctx.Process(target=worker, args=(str(tmp_path), str(i))) for i in range(2)
    ]
    for p in workers:
        p.start()
    for p in workers:
        p.join(5)
        assert p.exitcode == 0
    ledger = json.loads((tmp_path / "ledger.json").read_text())
    assert len(ledger["calls"]) == 2
    assert {x["stage"] for x in ledger["calls"]} == {"0", "1"}
    assert sorted(x["sequence"] for x in ledger["calls"]) == [1, 2]
    assert len(list(tmp_path.glob("request-*.json"))) == 2
    assert len(list(tmp_path.glob("response-*.json"))) == 2
    assert ledger["spent_usd"] == pytest.approx(0.0008)


def test_unknown_exposure_blocks_next_dispatch(tmp_path, monkeypatch):
    init(tmp_path, cap=0.5)
    monkeypatch.setenv("ARGON_STAGE", "failed")

    def fail(*a, **kw):
        raise httpx.ReadTimeout("offline")

    with pytest.raises(httpx.ReadTimeout):
        guard.guarded_send(fail, None, request())
    monkeypatch.setenv("ARGON_STAGE", "next")
    with pytest.raises(RuntimeError, match="reserve"):
        guard.guarded_send(fake_send, None, request())
    ledger = json.loads((tmp_path / "ledger.json").read_text())
    assert len(ledger["calls"]) == 1 and ledger["calls"][0]["cost_usd"] is None
    assert ledger["calls"][0]["reserved_usd"] == pytest.approx(0.37968)


def test_duplicate_stage_cannot_overwrite_receipt(tmp_path, monkeypatch):
    init(tmp_path)
    monkeypatch.setenv("ARGON_STAGE", "same")
    guard.guarded_send(fake_send, None, request())
    original = (tmp_path / "response-001.json").read_bytes()
    request_before = (tmp_path / "request-001.json").read_bytes()
    with pytest.raises(RuntimeError, match="Duplicate"):
        guard.guarded_send(fake_send, None, request())
    assert (tmp_path / "response-001.json").read_bytes() == original
    assert (tmp_path / "request-001.json").read_bytes() == request_before


def test_existing_receipt_denies_before_dispatch_or_ledger_change(
    tmp_path, monkeypatch
):
    init(tmp_path)
    monkeypatch.setenv("ARGON_STAGE", "new")
    (tmp_path / "request-001.json").write_text("keep original")
    before = (tmp_path / "ledger.json").read_bytes()
    with pytest.raises(RuntimeError, match="collision"):
        guard.guarded_send(fake_send, None, request())
    assert (tmp_path / "request-001.json").read_text() == "keep original"
    assert (tmp_path / "ledger.json").read_bytes() == before
    assert not (tmp_path / "response-001.json").exists()


def test_original_ledger_change_fails_before_receipt(tmp_path, monkeypatch):
    init(tmp_path)
    monkeypatch.setenv("ARGON_STAGE", "new")
    guard.OLD_LEDGER.write_text("modified")
    with pytest.raises(RuntimeError, match="Original ledger changed"):
        guard.guarded_send(fake_send, None, request())
    assert not list(tmp_path.glob("request-*.json"))


def test_unfrozen_thinking_parameter_fails_before_receipt(tmp_path, monkeypatch):
    init(tmp_path)
    monkeypatch.setenv("ARGON_STAGE", "new")
    req = request()
    body = json.loads(req.content)
    body["generationConfig"]["thinkingConfig"] = {"thinkingLevel": "high"}
    req = httpx.Request("POST", str(req.url), json=body)
    with pytest.raises(RuntimeError, match="frozen effort-only matrix"):
        guard.guarded_send(fake_send, None, req)
    assert not list(tmp_path.glob("request-*.json"))


def test_stopped_arm_cannot_dispatch(tmp_path, monkeypatch):
    init(tmp_path)
    monkeypatch.setenv("ARGON_STAGE", "new")
    (guard.EVIDENCE / "stop-table-medium.json").write_text("source-backed failure")
    with pytest.raises(RuntimeError, match="arm stop"):
        guard.guarded_send(fake_send, None, request())
    assert not list(tmp_path.glob("request-*.json"))
