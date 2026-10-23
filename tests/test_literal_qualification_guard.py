"""Offline native-transport custody tests; no provider or credential access."""

import hashlib
import importlib.util
import json
import sys
import threading
from datetime import datetime as RealDatetime, timezone
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest

SPEC = importlib.util.spec_from_file_location(
    "literal_guard",
    Path(__file__).resolve().parents[1]
    / "benchmarks/providers/literal_qualification_guard.py",
)
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)


def astra_body(maximum=8192):
    return {
        "model": "gpt-6-astra",
        "service_tier": "default",
        "store": False,
        "max_output_tokens": maximum,
        "input": [
            {"role": "user", "content": [{"type": "input_text", "text": "frozen"}]}
        ],
    }


def argon_body():
    return {
        "contents": [{"role": "user", "parts": [{"text": "frozen"}]}],
        "generationConfig": {
            "maxOutputTokens": 32768,
            "thinkingConfig": {"thinkingLevel": "HIGH"},
        },
    }


def entry(stage, *, model="gpt-6-astra", kind="ocr", body=None, **extra):
    body = body or (argon_body() if model == "gemini-4-argon" else astra_body())
    maximum = body.get(
        "max_output_tokens", body.get("generationConfig", {}).get("maxOutputTokens")
    )
    return {
        "stage": stage,
        "model": model,
        "kind": kind,
        "request_sha256": guard.request_sha256(body),
        "input_token_bound": 26000,
        "max_output_tokens": maximum,
        "reserved_usd": 0.37968
        if model == "gemini-4-argon"
        else (0.7346 if kind == "ocr" else 1.5),
        **extra,
    }


@pytest.fixture
def campaign(tmp_path, monkeypatch):
    class October(RealDatetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 10, 14, tzinfo=timezone.utc)

    monkeypatch.setattr(guard, "datetime", October)
    result = tmp_path / "receipts"
    old = tmp_path / "closed-ledger.json"
    old.write_text('{"closed":true}')
    config = {
        "result_dir": str(result),
        "cap_usd": 3,
        "prior_exposure_usd": 0.86667725,
        "owner_cap_usd": 15,
        "campaign_prior_exposure_usd": 3.877369745,
        "campaign_cap_usd": 35,
        "max_calls": 33,
        "old_ledger_sha256": {str(old): hashlib.sha256(old.read_bytes()).hexdigest()},
        "matrix": [
            entry("ocr-1"),
            entry("ocr-2"),
            entry("reader-1", kind="reader"),
            entry("argon-1", model="gemini-4-argon", kind="reader"),
        ],
    }
    path = tmp_path / "campaign.json"
    path.write_text(json.dumps(config))
    monkeypatch.setenv("DOC_WEB_LITERAL_CAMPAIGN_FILE", str(path))
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "ocr-1")
    # Patch through install, preserving Client.send's real transport dispatch.
    monkeypatch.setattr(httpx.Client, "send", httpx.Client.send)
    guard.install()
    return SimpleNamespace(
        result=result,
        config=config,
        path=path,
        old=old,
        ledger=lambda: json.loads((result / "ledger.json").read_text()),
    )


def send(handler, *, body=None, google=False, **client_options):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-4-argon:generateContent?key=never-retain"
        if google
        else "https://api.openai.com/v1/responses"
    )
    with httpx.Client(
        transport=httpx.MockTransport(handler), **client_options
    ) as client:
        return client.post(
            url,
            json=body or (argon_body() if google else astra_body()),
            headers={"Authorization": "never-retain"},
        )


def response(usage=None, google=False, status=200):
    data = (
        {"modelVersion": "gemini-4-argon", "usageMetadata": usage}
        if google
        else {"model": "gpt-6-astra", "service_tier": "default", "usage": usage}
    )
    return httpx.Response(status, json=data)


ASTRA_USAGE = {
    "input_tokens": 1000,
    "output_tokens": 100,
    "input_tokens_details": {"cached_tokens": 200, "cache_write_tokens": 300},
    "output_tokens_details": {"reasoning_tokens": 50},
}


def test_reservation_and_exclusive_request_before_underlying_transport(campaign):
    def handler(request):
        call = campaign.ledger()["calls"][0]
        assert call["cost_usd"] is None and call["reserved_usd"] == 0.7346
        assert (campaign.result / "request-001.json").exists()
        assert not (campaign.result / "response-001.json").exists()
        return response(ASTRA_USAGE)

    send(handler)
    call = campaign.ledger()["calls"][0]
    assert call["cost_usd"] == pytest.approx(0.01395)
    assert call["cold_cost_usd"] == pytest.approx(0.015)
    assert call["december_cost_usd"] == call["cost_usd"]
    assert call["usage"]["thinking_tokens"] == 50
    assert "never-retain" not in (campaign.result / "ledger.json").read_text()
    assert "never-retain" not in (campaign.result / "request-001.json").read_text()


def test_google_thinking_cache_and_december_cost(campaign, monkeypatch):
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "argon-1")
    send(
        lambda req: response(
            {
                "promptTokenCount": 1000,
                "candidatesTokenCount": 100,
                "thoughtsTokenCount": 200,
                "cachedContentTokenCount": 500,
            },
            google=True,
        ),
        google=True,
    )
    call = campaign.ledger()["calls"][0]
    assert call["usage"]["output_tokens"] == 300
    assert call["cost_usd"] == pytest.approx(0.00405)
    assert call["cold_cost_usd"] == pytest.approx(0.005)
    assert call["december_cost_usd"] == pytest.approx(0.0081)
    assert call["december_cold_cost_usd"] == pytest.approx(0.01)
    assert "never-retain" not in (campaign.result / "request-001.json").read_text()


@pytest.mark.parametrize(
    "usage",
    [
        None,
        {},
        {"input_tokens": 1},
        {"input_tokens": -1, "output_tokens": 2},
        {"input_tokens": True, "output_tokens": 2},
        {"input_tokens": "10", "output_tokens": 2},
        {"input_tokens": 10, "output_tokens": 2.1},
        {"input_tokens": 10, "output_tokens": 2, "input_tokens_details": []},
        {
            "input_tokens": 10,
            "output_tokens": 2,
            "input_tokens_details": {"cached_tokens": 11},
        },
        {
            "input_tokens": 10,
            "output_tokens": 2,
            "input_tokens_details": {"cache_write_tokens": -1},
        },
        {
            "input_tokens": 10,
            "output_tokens": 2,
            "output_tokens_details": {"reasoning_tokens": 3},
        },
    ],
)
def test_malformed_missing_negative_usage_keeps_full_reservation(campaign, usage):
    send(lambda req: response(usage))
    ledger = campaign.ledger()
    assert ledger["spent_usd"] == 0
    assert ledger["calls"][0]["cost_usd"] is None
    assert ledger["calls"][0]["billing_unresolved"]
    assert (campaign.result / "response-001.json").exists()


@pytest.mark.parametrize(
    "usage",
    [
        {},
        {"promptTokenCount": 1},
        {"promptTokenCount": 10, "candidatesTokenCount": 1, "thoughtsTokenCount": -1},
        {
            "promptTokenCount": 10,
            "candidatesTokenCount": 1,
            "cachedContentTokenCount": 11,
        },
    ],
)
def test_google_incomplete_usage_keeps_full_reservation(campaign, monkeypatch, usage):
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "argon-1")
    send(lambda req: response(usage, google=True), google=True)
    assert campaign.ledger()["calls"][0]["cost_usd"] is None


def test_unknown_exposure_inclusive_budget_denies_before_any_new_receipt(
    campaign, monkeypatch
):
    # Unknown OCR + unknown reader + unknown OCR = 2.9692; another Argon is denied.
    for stage in ("ocr-1", "reader-1", "ocr-2"):
        monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", stage)
        send(lambda req: response(None))
    before = (campaign.result / "ledger.json").read_bytes()
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "argon-1")
    with pytest.raises(guard.AdmissionDenied, match="inclusive cap"):
        send(lambda req: pytest.fail("underlying transport invoked"), google=True)
    assert (campaign.result / "ledger.json").read_bytes() == before
    assert not (campaign.result / "request-004.json").exists()


def test_settled_actual_replaces_reservation_for_next_admission(campaign, monkeypatch):
    for stage in ("reader-1", "ocr-1", "ocr-2"):
        monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", stage)
        send(lambda req: response(ASTRA_USAGE))
    assert len(campaign.ledger()["calls"]) == 3
    assert campaign.ledger()["spent_usd"] == pytest.approx(0.04185)


def test_duplicate_stage_denied_without_overwrite(campaign):
    send(lambda req: response(ASTRA_USAGE))
    before = {p.name: p.read_bytes() for p in campaign.result.glob("*.json")}
    with pytest.raises(guard.AdmissionDenied, match="Duplicate"):
        send(lambda req: pytest.fail("underlying transport invoked"))
    assert before == {p.name: p.read_bytes() for p in campaign.result.glob("*.json")}


def test_response_collision_denied_before_ledger_or_request_write(campaign):
    campaign.result.mkdir()
    receipt = campaign.result / "response-001.json"
    receipt.write_bytes(b"preserve")
    with pytest.raises(guard.AdmissionDenied, match="namespace collision"):
        send(lambda req: pytest.fail("underlying transport invoked"))
    assert receipt.read_bytes() == b"preserve"
    assert not (campaign.result / "ledger.json").exists()
    assert not (campaign.result / "request-001.json").exists()


def test_raw_full_response_saved_before_usage_parse(campaign, monkeypatch):
    original = guard._usage

    def observe(data, google):
        assert (
            json.loads((campaign.result / "response-001.json").read_bytes())["usage"]
            == ASTRA_USAGE
        )
        assert campaign.ledger()["calls"][0]["cost_usd"] is None
        return original(data, google)

    monkeypatch.setattr(guard, "_usage", observe)
    send(lambda req: response(ASTRA_USAGE))


def test_invalid_response_json_retained_before_parsing(campaign):
    send(lambda req: httpx.Response(502, content=b"entire unknown native envelope\n"))
    assert (
        campaign.result / "response-001.json"
    ).read_bytes() == b"entire unknown native envelope\n"
    assert campaign.ledger()["calls"][0]["billing_unresolved"]


@pytest.mark.parametrize(
    "usage",
    [
        {"input_tokens": 26001, "output_tokens": 1},
        {"input_tokens": 1, "output_tokens": 8193},
    ],
)
def test_usage_bound_violation_settles_and_closes(campaign, monkeypatch, usage):
    send(lambda req: response(usage))
    ledger = campaign.ledger()
    assert ledger["closed"] and ledger["calls"][0]["bound_violation"]
    assert ledger["calls"][0]["cost_usd"] is not None
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "ocr-2")
    with pytest.raises(guard.AdmissionDenied, match="closed"):
        send(lambda req: pytest.fail("underlying transport invoked"))


def test_unknown_transport_failure_keeps_intent_and_disallows_sdk_retry(campaign):
    dispatched = []

    def handler(req):
        dispatched.append(req)
        raise httpx.ConnectError("offline test", request=req)

    with pytest.raises(httpx.ConnectError):
        send(handler)
    with pytest.raises(guard.AdmissionDenied, match="Duplicate"):
        send(handler)
    assert len(dispatched) == 1 and campaign.ledger()["calls"][0]["cost_usd"] is None


def test_actual_httptransport_pool_retries_denied_before_dispatch(campaign):
    with httpx.Client(transport=httpx.HTTPTransport(retries=1)) as client:
        with pytest.raises(guard.AdmissionDenied, match="retries"):
            client.post("https://api.openai.com/v1/responses", json=astra_body())
    assert not (campaign.result / "ledger.json").exists()


def test_redirecting_transport_denied(campaign):
    with pytest.raises(guard.AdmissionDenied, match="Redirecting"):
        send(
            lambda req: pytest.fail("underlying transport invoked"),
            follow_redirects=True,
        )


def test_stop_file_and_changed_closed_ledger_deny(campaign):
    campaign.result.mkdir()
    (campaign.result / "stop.json").write_text("stop")
    with pytest.raises(guard.AdmissionDenied, match="stop file"):
        send(lambda req: pytest.fail("underlying transport invoked"))
    (campaign.result / "stop.json").unlink()
    campaign.old.write_text("changed")
    with pytest.raises(guard.AdmissionDenied, match="prior ledger changed"):
        send(lambda req: pytest.fail("underlying transport invoked"))
    assert not (campaign.result / "ledger.json").exists()


def test_concurrent_dispatches_serialized_and_second_stage_exclusive(
    campaign, monkeypatch
):
    entered, release = threading.Event(), threading.Event()
    observed = []

    def first(req):
        observed.append("first")
        entered.set()
        assert release.wait(3)
        return response(ASTRA_USAGE)

    def second(req):
        observed.append("second")
        assert campaign.ledger()["calls"][0]["cost_usd"] is not None
        return response(ASTRA_USAGE)

    with ThreadPoolExecutor(max_workers=3) as executor:
        one = executor.submit(send, first)
        assert entered.wait(3)
        monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "ocr-2")
        two = executor.submit(send, second)
        duplicate = executor.submit(send, second)
        release.set()
        one.result(timeout=3)
        outcomes = []
        for future in (two, duplicate):
            try:
                future.result(timeout=3)
                outcomes.append("ok")
            except guard.AdmissionDenied:
                outcomes.append("denied")
    assert sorted(outcomes) == ["denied", "ok"]
    assert observed == ["first", "second"]
    assert [call["sequence"] for call in campaign.ledger()["calls"]] == [1, 2]
    assert len(list(campaign.result.glob("request-*.json"))) == 2
    assert len(list(campaign.result.glob("response-*.json"))) == 2


def test_exact_native_route_and_frozen_body_required(campaign):
    with httpx.Client(
        transport=httpx.MockTransport(lambda req: pytest.fail("dispatch"))
    ) as client:
        with pytest.raises(guard.AdmissionDenied, match="Unmetered"):
            client.post("https://api.openai.com/v1/chat/completions", json=astra_body())
        with pytest.raises(guard.AdmissionDenied, match="frozen stage"):
            client.post(
                "https://api.openai.com/v1/responses",
                json={**astra_body(), "input": "changed"},
            )
    assert not (campaign.result / "ledger.json").exists()


def test_single_selected_recovery_preserves_request_and_33_call_ceiling(
    campaign, monkeypatch
):
    campaign.config["matrix"].append(entry("recovery", recovery_of="ocr-1"))
    campaign.path.write_text(json.dumps(campaign.config))
    send(lambda req: httpx.Response(502, content=b"unknown transient"))
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "recovery")
    send(lambda req: response(ASTRA_USAGE))
    with pytest.raises(guard.AdmissionDenied, match="Duplicate"):
        send(lambda req: pytest.fail("automatic second recovery"))
    campaign.config["max_calls"] = 34
    campaign.path.write_text(json.dumps(campaign.config))
    with pytest.raises(guard.AdmissionDenied, match="call ceiling"):
        send(lambda req: pytest.fail("ceiling bypass"))


def test_install_covers_both_httpx_and_httpx2_idempotently(campaign, monkeypatch):
    # Optional httpx2 is not installed in the owner environment. Exercise its
    # independent Client.send entry point with real httpx MockTransport dispatch.
    class SecondClient(httpx.Client):
        send = httpx.Client.send._literal_original

    SecondClient.__module__ = "httpx2"
    second = SimpleNamespace(
        Client=SecondClient,
        MockTransport=httpx.MockTransport,
        HTTPTransport=httpx.HTTPTransport,
    )
    monkeypatch.setitem(sys.modules, "httpx2", second)
    guard.install()
    first_send, second_send = httpx.Client.send, SecondClient.send
    guard.install()
    assert httpx.Client.send is first_send and SecondClient.send is second_send
    with SecondClient(
        transport=httpx.MockTransport(lambda req: response(ASTRA_USAGE))
    ) as client:
        client.post("https://api.openai.com/v1/responses", json=astra_body())
    assert len(campaign.ledger()["calls"]) == 1


@pytest.mark.parametrize(
    "cap_name,prior_name",
    [
        ("owner_cap_usd", "prior_exposure_usd"),
        ("campaign_cap_usd", "campaign_prior_exposure_usd"),
    ],
)
def test_original_owner_and_campaign_caps_are_inclusive(campaign, cap_name, prior_name):
    campaign.config[cap_name] = campaign.config[prior_name] + 0.7
    campaign.path.write_text(json.dumps(campaign.config))
    with pytest.raises(guard.AdmissionDenied, match="inclusive cap"):
        send(lambda req: pytest.fail("dispatch exceeds original cap"))
    assert not (campaign.result / "ledger.json").exists()


def test_pricing_expiry_requires_fresh_reservations(campaign, monkeypatch):
    class December(RealDatetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 12, 1, tzinfo=timezone.utc)

    monkeypatch.setattr(guard, "datetime", December)
    with pytest.raises(guard.AdmissionDenied, match="pricing expired"):
        send(lambda req: pytest.fail("expired price envelope dispatched"))
    assert not campaign.result.exists()


def test_native_timeout_preserves_unknown_and_closes_recovery(campaign, monkeypatch):
    campaign.config["matrix"].append(entry("recovery", recovery_of="ocr-1"))
    campaign.path.write_text(json.dumps(campaign.config))

    def timeout(req):
        raise httpx.ReadTimeout("offline deadline breach", request=req)

    with pytest.raises(httpx.ReadTimeout):
        send(timeout)
    assert campaign.ledger()["closed"]
    assert campaign.ledger()["calls"][0]["cost_usd"] is None
    assert campaign.ledger()["calls"][0]["latency_violation"]
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "recovery")
    with pytest.raises(guard.AdmissionDenied, match="closed"):
        send(lambda req: pytest.fail("deadline recovery attempted"))


def test_late_argon_response_is_retained_billed_and_closes(campaign, monkeypatch):
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "argon-1")
    times = iter([0, 181])
    monkeypatch.setattr(guard.time, "monotonic", lambda: next(times))
    send(
        lambda req: response(
            {"promptTokenCount": 1000, "candidatesTokenCount": 100}, google=True
        ),
        google=True,
    )
    ledger = campaign.ledger()
    assert ledger["closed"] and ledger["calls"][0]["latency_violation"]
    assert ledger["calls"][0]["cost_usd"] is not None
    assert (campaign.result / "response-001.json").exists()


def test_served_model_mismatch_settles_usage_and_stops(campaign):
    send(
        lambda req: httpx.Response(
            200,
            json={
                "model": "unselected-model",
                "service_tier": "default",
                "usage": ASTRA_USAGE,
            },
        )
    )
    ledger = campaign.ledger()
    assert ledger["closed"] and ledger["calls"][0]["served_model_violation"]
    assert ledger["calls"][0]["cost_usd"] == pytest.approx(0.01395)


def test_frozen_config_cannot_change_after_first_admission(campaign, monkeypatch):
    send(lambda req: response(ASTRA_USAGE))
    campaign.config["matrix"][1]["request_sha256"] = "changed"
    campaign.path.write_text(json.dumps(campaign.config))
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "reader-1")
    before = (campaign.result / "ledger.json").read_bytes()
    with pytest.raises(guard.AdmissionDenied, match="ledger mismatch"):
        send(lambda req: pytest.fail("changed frozen config dispatched"))
    assert (campaign.result / "ledger.json").read_bytes() == before


def test_recovery_after_semantic_success_or_non502_not_admitted(campaign, monkeypatch):
    campaign.config["matrix"].append(entry("recovery", recovery_of="ocr-1"))
    campaign.path.write_text(json.dumps(campaign.config))
    send(lambda req: response(None, status=503))
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "recovery")
    with pytest.raises(guard.AdmissionDenied, match="operational failure"):
        send(lambda req: pytest.fail("unselected failure recovery"))
    assert len(campaign.ledger()["calls"]) == 1


def test_partially_malformed_usage_with_observed_bound_violation_closes(campaign):
    send(lambda req: response({"input_tokens": 26001, "output_tokens": None}))
    ledger = campaign.ledger()
    assert ledger["closed"] and ledger["calls"][0]["bound_violation"]
    assert ledger["calls"][0]["cost_usd"] is None
    assert ledger["calls"][0]["billing_unresolved"]


@pytest.mark.parametrize(
    "state",
    [
        "missing",
        "symlink",
        "directory",
        "malformed",
        "false",
        "integer",
        "list",
        "relative",
    ],
)
def test_progressive_gate_denied_before_any_receipt_or_operational_write(
    campaign, state
):
    gate = campaign.path.parent / "screen-clearance.json"
    campaign.config["matrix"][0]["required_gate"] = str(gate)
    if state == "symlink":
        target = campaign.path.parent / "clearance-target.json"
        target.write_text('{"allowed":true}')
        gate.symlink_to(target)
    elif state == "directory":
        gate.mkdir()
    elif state == "malformed":
        gate.write_text("malformed")
    elif state in ("false", "integer", "list"):
        gate.write_text(
            {"false": '{"allowed":false}', "integer": '{"allowed":1}', "list": "[]"}[
                state
            ]
        )
    elif state == "relative":
        campaign.config["matrix"][0]["required_gate"] = "screen-clearance.json"
    campaign.path.write_text(json.dumps(campaign.config))
    with pytest.raises(guard.AdmissionDenied, match="gate"):
        send(lambda req: pytest.fail("uncleared stage dispatched"))
    assert not campaign.result.exists()


def test_progressive_screen_and_panel_gates_are_stage_specific(campaign, monkeypatch):
    screen = campaign.path.parent / "screen-clearance.json"
    panel = campaign.path.parent / "panel-clearance.json"
    campaign.config["matrix"][1]["required_gate"] = str(screen)
    campaign.config["matrix"][2]["required_gate"] = str(panel)
    campaign.path.write_text(json.dumps(campaign.config))
    send(lambda req: response(ASTRA_USAGE))  # Opening stage has no prerequisite.
    before = (campaign.result / "ledger.json").read_bytes()
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "ocr-2")
    with pytest.raises(guard.AdmissionDenied, match="gate"):
        send(lambda req: pytest.fail("screen expansion before clearance"))
    assert (campaign.result / "ledger.json").read_bytes() == before
    screen.write_text('{"allowed":true}')
    send(lambda req: response(ASTRA_USAGE))
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "reader-1")
    with pytest.raises(guard.AdmissionDenied, match="gate"):
        send(lambda req: pytest.fail("panel/repeat before clearance"))
    panel.write_text('{"allowed":true}')
    send(lambda req: response(ASTRA_USAGE))
    assert len(campaign.ledger()["calls"]) == 3


def test_gate_rechecked_after_lock_and_stop_overrides_clearance(campaign, monkeypatch):
    gate = campaign.path.parent / "screen-clearance.json"
    gate.write_text('{"allowed":true}')
    campaign.config["matrix"][0]["required_gate"] = str(gate)
    campaign.path.write_text(json.dumps(campaign.config))
    original = guard._required_gate
    checks = []

    def revoke_after_precheck(selected):
        original(selected)
        checks.append(selected["stage"])
        if len(checks) == 1:
            gate.write_text('{"allowed":false}')

    monkeypatch.setattr(guard, "_required_gate", revoke_after_precheck)
    with pytest.raises(guard.AdmissionDenied, match="gate"):
        send(lambda req: pytest.fail("revoked clearance dispatched"))
    assert not (campaign.result / "ledger.json").exists()
    monkeypatch.setattr(guard, "_required_gate", original)
    gate.write_text('{"allowed":true}')
    (campaign.result / "stop.json").write_text("stop")
    with pytest.raises(guard.AdmissionDenied, match="stop file"):
        send(lambda req: pytest.fail("stop overridden by clearance"))
    assert not (campaign.result / "ledger.json").exists()


def test_production_openai_wrapper_builds_zero_retry_no_redirect_topology(campaign):
    from modules.common.openai_client import OpenAI

    wrapper = OpenAI(api_key="offline-test-key", max_retries=0)
    try:
        assert wrapper._client.max_retries == 0
        native_http = wrapper._client._client
        assert native_http.follow_redirects is False
        transport = native_http._transport_for_url(
            httpx.URL("https://api.openai.com/v1/responses")
        )
        assert isinstance(transport, httpx.HTTPTransport)
        assert transport._pool._retries == 0
        assert hasattr(wrapper, "responses")
    finally:
        wrapper._client.close()


@pytest.mark.parametrize("options", [{}, {"max_retries": 1}])
def test_production_openai_wrapper_requires_explicit_zero_sdk_retries(
    campaign, options
):
    from modules.common.openai_client import OpenAI

    with pytest.raises(ValueError, match="zero SDK retries"):
        OpenAI(api_key="offline-test-key", **options)


@pytest.mark.parametrize("selected_index", range(32))
def test_one_operational_recovery_slot_can_select_any_frozen_32_stage(
    campaign, monkeypatch, selected_index
):
    campaign.config["operational_recovery"] = True
    campaign.config["matrix"] = [entry(f"initial-{index:02d}") for index in range(32)]
    campaign.path.write_text(json.dumps(campaign.config))
    stage = f"initial-{selected_index:02d}"
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", stage)
    send(lambda req: httpx.Response(502, content=b"preserved operational failure"))
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "recovery-" + stage)
    send(lambda req: response(ASTRA_USAGE))
    ledger = campaign.ledger()
    assert ledger["calls"][1]["recovery_of"] == stage
    for field in (
        "model",
        "kind",
        "request_sha256",
        "input_token_bound",
        "max_output_tokens",
        "reserved_usd",
    ):
        assert ledger["calls"][0][field] == ledger["calls"][1][field]
    other = f"initial-{(selected_index + 1) % 32:02d}"
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", other)
    send(lambda req: httpx.Response(502, content=b"second operational failure"))
    before = (campaign.result / "ledger.json").read_bytes()
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "recovery-" + other)
    with pytest.raises(guard.AdmissionDenied, match="slot already consumed"):
        send(lambda req: pytest.fail("second recovery dispatched"))
    assert (campaign.result / "ledger.json").read_bytes() == before
    assert len(campaign.ledger()["calls"]) == 3


@pytest.mark.parametrize(
    "model,kind", [("gpt-6-astra", "reader"), ("gemini-4-argon", "reader")]
)
def test_dynamic_recovery_preserves_native_model_contract(
    campaign, monkeypatch, model, kind
):
    campaign.config["operational_recovery"] = True
    campaign.config["matrix"] = [entry("chosen", model=model, kind=kind)]
    campaign.path.write_text(json.dumps(campaign.config))
    google = model == "gemini-4-argon"
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "chosen")
    send(lambda req: httpx.Response(502, content=b"operational"), google=google)
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "recovery-chosen")
    usage = (
        {"promptTokenCount": 1, "candidatesTokenCount": 1} if google else ASTRA_USAGE
    )
    send(lambda req: response(usage, google=google), google=google)
    assert campaign.ledger()["calls"][1]["model"] == model


def test_dynamic_recovery_rejects_changed_body_before_receipts(campaign, monkeypatch):
    campaign.config["operational_recovery"] = True
    campaign.path.write_text(json.dumps(campaign.config))
    send(lambda req: httpx.Response(502, content=b"operational"))
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "recovery-ocr-1")
    before = (campaign.result / "ledger.json").read_bytes()
    with pytest.raises(guard.AdmissionDenied, match="frozen stage"):
        send(
            lambda req: pytest.fail("changed semantic request"),
            body={**astra_body(), "input": "changed"},
        )
    assert (campaign.result / "ledger.json").read_bytes() == before
    assert not (campaign.result / "request-002.json").exists()


@pytest.mark.parametrize("failure", ["normal", "semantic", "latency"])
def test_dynamic_recovery_cannot_recover_normal_semantic_or_latency_failure(
    campaign, monkeypatch, failure
):
    campaign.config["operational_recovery"] = True
    campaign.path.write_text(json.dumps(campaign.config))
    if failure == "latency":

        def deadline(req):
            raise httpx.ReadTimeout("offline latency", request=req)

        with pytest.raises(httpx.ReadTimeout):
            send(deadline)
    else:
        send(lambda req: response(ASTRA_USAGE))
        if failure == "semantic":
            ledger = campaign.ledger()
            ledger["calls"][0].update(
                semantic_failure=True, harness_repair_authorized=True
            )
            (campaign.result / "ledger.json").write_text(json.dumps(ledger))
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "recovery-ocr-1")
    with pytest.raises(guard.AdmissionDenied, match="operational failure|closed"):
        send(lambda req: pytest.fail("invalid recovery"))
    assert len(campaign.ledger()["calls"]) == 1


def test_dynamic_recovery_requires_explicit_boolean_selection(campaign, monkeypatch):
    for invalid in (1, "true", None):
        campaign.config["operational_recovery"] = invalid
        campaign.path.write_text(json.dumps(campaign.config))
        with pytest.raises(guard.AdmissionDenied, match="boolean"):
            send(lambda req: pytest.fail("invalid selection dispatched"))
    campaign.config["operational_recovery"] = False
    campaign.path.write_text(json.dumps(campaign.config))
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "recovery-ocr-1")
    with pytest.raises(guard.AdmissionDenied, match="frozen stage"):
        send(lambda req: pytest.fail("unselected recovery"))
    assert not campaign.result.exists()


def test_dynamic_recovery_inherits_required_gate_and_stop(campaign, monkeypatch):
    campaign.config["operational_recovery"] = True
    gate = campaign.path.parent / "screen-clearance.json"
    gate.write_text('{"allowed":true}')
    campaign.config["matrix"][0]["required_gate"] = str(gate)
    campaign.path.write_text(json.dumps(campaign.config))
    send(lambda req: httpx.Response(502, content=b"operational"))
    gate.write_text('{"allowed":false}')
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "recovery-ocr-1")
    with pytest.raises(guard.AdmissionDenied, match="gate"):
        send(lambda req: pytest.fail("recovery bypassed inherited gate"))
    gate.write_text('{"allowed":true}')
    (campaign.result / "stop.json").write_text("semantic stop")
    with pytest.raises(guard.AdmissionDenied, match="stop file"):
        send(lambda req: pytest.fail("recovery bypassed stop"))
    assert len(campaign.ledger()["calls"]) == 1


@pytest.mark.parametrize("requested_tier", [None, "auto", "fast", "priority"])
def test_astra_request_requires_explicit_default_tier_before_post(
    campaign, requested_tier
):
    body = astra_body()
    if requested_tier is None:
        body.pop("service_tier")
    else:
        body["service_tier"] = requested_tier
    campaign.config["matrix"][0]["request_sha256"] = guard.request_sha256(body)
    campaign.path.write_text(json.dumps(campaign.config))
    with pytest.raises(guard.AdmissionDenied, match="native service"):
        send(
            lambda req: pytest.fail("unbounded project/fast service dispatched"),
            body=body,
        )
    assert not (campaign.result / "ledger.json").exists()
    assert not (campaign.result / "request-001.json").exists()


@pytest.mark.parametrize("returned_tier", [None, "fast", "auto", "priority"])
def test_successful_astra_missing_or_nondefault_tier_keeps_full_unknown_and_stops(
    campaign, monkeypatch, returned_tier
):
    data = {"model": "gpt-6-astra", "usage": ASTRA_USAGE}
    if returned_tier is not None:
        data["service_tier"] = returned_tier
    send(lambda req: httpx.Response(200, json=data))
    ledger = campaign.ledger()
    call = ledger["calls"][0]
    assert ledger["closed"] and ledger["spent_usd"] == 0
    assert call["reserved_usd"] == 0.7346 and call["cost_usd"] is None
    assert call["billing_unresolved"] and call["service_tier_violation"]
    assert call["served_service_tier"] == returned_tier
    assert "cold_cost_usd" not in call
    assert json.loads((campaign.result / "response-001.json").read_bytes()) == data
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "ocr-2")
    with pytest.raises(guard.AdmissionDenied, match="closed"):
        send(lambda req: pytest.fail("unproved returned service expanded spending"))


def test_502_without_returned_tier_keeps_operational_recovery_eligible(
    campaign, monkeypatch
):
    campaign.config["operational_recovery"] = True
    campaign.path.write_text(json.dumps(campaign.config))
    send(
        lambda req: httpx.Response(
            502, json={"error": {"message": "offline transient"}}
        )
    )
    ledger = campaign.ledger()
    assert not ledger["closed"] and ledger["calls"][0]["cost_usd"] is None
    assert not ledger["calls"][0].get("service_tier_violation")
    monkeypatch.setenv("DOC_WEB_LITERAL_STAGE", "recovery-ocr-1")
    send(lambda req: response(ASTRA_USAGE))
    assert len(campaign.ledger()["calls"]) == 2
    assert campaign.ledger()["calls"][1]["served_service_tier"] == "default"


def test_raw_request_receipt_is_exact_wire_bytes_with_separate_canonical_hash(campaign):
    body = astra_body()
    wire_body = json.dumps(body, indent=3, ensure_ascii=False).encode() + b"\n"
    assert wire_body != json.dumps(body, sort_keys=True).encode()

    def handler(req):
        assert req.content == wire_body
        assert (campaign.result / "request-001.json").read_bytes() == wire_body
        return response(ASTRA_USAGE)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        client.post(
            "https://api.openai.com/v1/responses",
            content=wire_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "never-retain",
            },
        )
    call = campaign.ledger()["calls"][0]
    assert call["request_sha256"] == guard.request_sha256(body)
    assert call["native_request_bytes_sha256"] == hashlib.sha256(wire_body).hexdigest()
    assert call["native_request_bytes"] == len(wire_body)
    assert call["request_sha256"] != call["native_request_bytes_sha256"]
