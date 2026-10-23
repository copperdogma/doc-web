"""Synthetic-only Argon transport and frozen campaign admission checks."""

import hashlib
import json
import sys
from pathlib import Path

import httpx
import pytest
from jsonschema import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmarks/providers"))
import gemini4_argon as adapter
import mistral4_guard as guard


@pytest.fixture(autouse=True)
def restore_profile(monkeypatch):
    for name in ["PROFILE", "RESULTS", "PRICES"]:
        monkeypatch.setattr(guard, name, getattr(guard, name))
    monkeypatch.setattr(guard, "PROFILE", None)


def profile(tmp_path, cap=5):
    source = Path("benchmarks/providers/gemini4_argon.py")
    model = adapter.CANDIDATE
    data = {
        "results_dir": str(tmp_path),
        "cap_usd": cap,
        "max_calls": 36,
        "prices": {model: [2, 0.1, 2, 10]},
        "output_limits": {model: 32768},
        "endpoints": {
            model: f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        },
        "sources": {str(source): hashlib.sha256(source.read_bytes()).hexdigest()},
    }
    path = tmp_path / "profile.json"
    guard.write(path, data)
    guard.write(
        tmp_path / "ledger.json",
        {
            "cap_usd": cap,
            "spent_usd": 0,
            "calls": [],
            "closed": False,
            "campaign_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        },
    )
    return path


def prompt():
    return json.dumps(
        [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Test"},
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/png;base64,AA=="},
                    },
                ],
            }
        ]
    )


def envelope():
    return {
        "modelVersion": adapter.CANDIDATE,
        "responseId": "synthetic-response",
        "candidates": [
            {"finishReason": "STOP", "content": {"parts": [{"text": '{"images":[]}'}]}}
        ],
        "usageMetadata": {
            "promptTokenCount": 10,
            "candidatesTokenCount": 2,
            "thoughtsTokenCount": 3,
            "totalTokenCount": 15,
        },
    }


def test_native_body_preserves_semantics_and_declares_strict_contract():
    body = adapter.body(prompt())
    assert body["contents"][0]["parts"] == [
        {"text": "Test"},
        {"inlineData": {"mimeType": "image/png", "data": "AA=="}},
    ]
    config = body["generationConfig"]
    assert config["maxOutputTokens"] == 32768 and "temperature" not in config
    assert config["thinkingConfig"] == {"thinkingLevel": "medium"}
    assert config["responseJsonSchema"]["additionalProperties"] is False
    assert adapter.body(prompt(), adapter.CONTROL)["generationConfig"] == {
        "temperature": 0,
        "maxOutputTokens": 16384,
    }


@pytest.mark.parametrize(
    "defect",
    ["identity", "missing-id", "incomplete", "usage", "total", "schema", "geometry"],
)
def test_success_envelope_fails_closed(defect):
    data = envelope()
    if defect == "identity":
        data["modelVersion"] = "different-model"
    if defect == "missing-id":
        data.pop("responseId")
    if defect == "incomplete":
        data["candidates"][0]["finishReason"] = "MAX_TOKENS"
    if defect == "usage":
        data["usageMetadata"].pop("candidatesTokenCount")
    if defect == "total":
        data["usageMetadata"]["totalTokenCount"] = 999
    if defect in {"schema", "geometry"}:
        crop = {
            "description": "test",
            "bbox": [0, 0, 1001, 1000] if defect == "schema" else [100, 0, 0, 1000],
        }
        data["candidates"][0]["content"]["parts"][0]["text"] = json.dumps(
            {"images": [crop]}
        )
    with pytest.raises((ValueError, KeyError, ValidationError)):
        adapter.parse_response(data, adapter.CANDIDATE)


def test_complete_usage_includes_thinking():
    result = adapter.parse_response(envelope(), adapter.CANDIDATE)
    assert result["tokenUsage"] == {"prompt": 10, "completion": 5, "total": 15}
    assert result["cost"] == pytest.approx(0.00007)


def test_profile_allows_only_its_frozen_model_limit_and_binds_receipt(
    tmp_path, monkeypatch
):
    path = profile(tmp_path)
    guard.configure_campaign(path)
    monkeypatch.setenv("MISTRAL_STAGE", "offline")
    monkeypatch.setenv("MISTRAL_CASE", "synthetic")
    req = httpx.Request(
        "POST",
        guard.PROFILE["endpoints"][adapter.CANDIDATE],
        json=adapter.body(prompt()),
    )
    guard.guarded_send(
        lambda *a, **kw: httpx.Response(200, request=req, json=envelope()), None, req
    )
    ledger = json.loads((tmp_path / "ledger.json").read_text())
    assert ledger["spent_usd"] == pytest.approx(0.00007)
    record = ledger["calls"][0]
    assert record["reserved_usd"] == pytest.approx(0.37968)
    assert record["campaign_sha256"] == ledger["campaign_sha256"]
    assert "benchmarks/providers/gemini4_argon.py" in record["code_sha256"]


@pytest.mark.parametrize(
    "defect",
    [
        "profile-drift",
        "source-drift",
        "ledger-drift",
        "cap",
        "model",
        "endpoint",
        "limit",
    ],
)
def test_profile_drift_and_unapproved_dispatch_never_send(
    tmp_path, monkeypatch, defect
):
    path = profile(tmp_path, cap=0.001 if defect == "cap" else 5)
    guard.configure_campaign(path)
    monkeypatch.setenv("MISTRAL_STAGE", "offline")
    monkeypatch.setenv("MISTRAL_CASE", "synthetic")
    request_body = adapter.body(prompt())
    url = guard.PROFILE["endpoints"][adapter.CANDIDATE]
    if defect == "profile-drift":
        path.write_text(path.read_text() + " ")
    if defect == "source-drift":
        monkeypatch.setattr(guard, "ROOT", tmp_path)
    if defect == "ledger-drift":
        ledger = json.loads((tmp_path / "ledger.json").read_text())
        ledger["campaign_sha256"] = "wrong"
        guard.write(tmp_path / "ledger.json", ledger)
    if defect == "model":
        url = url.replace(adapter.CANDIDATE, adapter.CONTROL)
    if defect == "endpoint":
        url = url.replace("https://", "http://")
    if defect == "limit":
        request_body["generationConfig"]["maxOutputTokens"] += 1
    calls = []
    with pytest.raises((RuntimeError, KeyError, FileNotFoundError)):
        guard.guarded_send(
            lambda *a, **kw: calls.append(1),
            None,
            httpx.Request("POST", url, json=request_body),
        )
    assert not calls
