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
    "argon_guard_test", ROOT / "benchmarks/providers/argon_guard.py"
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
            "generationConfig": {"maxOutputTokens": 32768},
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
    # Snapshot custody is exercised in a disposable owner tree, never in the
    # sealed historical evidence directory of the checkout running the test.
    source_root = tmp_path / "owner"
    for relative in (
        "benchmarks/providers/argon_guard.py", "benchmarks/scripts/argon_campaign.py",
        "modules/common/openai_client.py", "modules/common/google_client.py",
        "modules/extract/ocr_ai_gpt51_v1/main.py",
    ):
        target = source_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())
    guard.ROOT = source_root
    guard.__file__ = str(source_root / "benchmarks/providers/argon_guard.py")
    guard.RESULTS = tmp_path
    guard.write(
        tmp_path / "ledger.json",
        {"cap_usd": cap, "spent_usd": 0, "calls": [], "closed": False},
    )


def test_astra_cache_writes_settle_at_standard_rate(tmp_path, monkeypatch):
    init(tmp_path)
    monkeypatch.setenv("ARGON_STAGE", "astra-cache-write")
    req = httpx.Request("POST", "https://api.openai.com/v1/responses", json={
        "model": "gpt-6-astra", "store": False, "max_output_tokens": 8192,
        "input": [{"content": [{"type": "input_image", "image_url": "tiny"}]}],
    })

    def dispatch(client, request, **kwargs):
        return httpx.Response(200, request=request, json={
            "model": "gpt-6-astra", "service_tier": "default",
            "usage": {"input_tokens": 5017, "output_tokens": 307,
                      "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 5013}},
        })

    guard.guarded_send(dispatch, None, req)
    ledger = json.loads((tmp_path / "ledger.json").read_text())
    # Four ordinary input tokens, 5013 writes and 307 inclusive output tokens.
    assert ledger["spent_usd"] == pytest.approx(0.0780525)
    assert ledger["calls"][0]["reserved_usd"] == pytest.approx(0.7346)
    assert not ledger["closed"]


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
