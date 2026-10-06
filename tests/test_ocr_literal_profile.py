"""Paid-call-free proof of literal OCR prompt, transport and receipt contracts."""

import base64
import hashlib
import json
from types import SimpleNamespace

import pytest

from benchmarks.scorers.literal_table_diff import compare_tables
from modules.common.ocr_literal_policy import LITERAL_POLICY
from modules.common.ocr_request_receipt import require_completed_identity
from modules.extract.ocr_ai_gpt51_v1.main import (
    SYSTEM_PROMPT,
    _call_vision_model,
    _ocr_with_fallback,
    build_system_prompt,
    sanitize_html,
)

MODEL = "gpt-6-astra"
IMAGE_BYTES = b"submitted composited PNG bytes"
RAW_HTML = '<table><tr><th colspan="2">NAME</th></tr><tr><td>Al &amp; Nl</td><td>“O’Neil”</td></tr></table>'


def fake_client(*, model=MODEL, status="completed", output=RAW_HTML):
    captured = []
    response = SimpleNamespace(
        model=model, status=status, output_text=output, id="resp-test",
        usage=SimpleNamespace(model_dump=lambda: {"input_tokens": 100, "output_tokens": 30}),
    )

    def create(**kwargs):
        captured.append(kwargs)
        return response

    return SimpleNamespace(responses=SimpleNamespace(create=create)), captured


def call(client, records, *, image=IMAGE_BYTES):
    return _call_vision_model(
        MODEL, build_system_prompt(None, True), "Return HTML only.",
        "data:image/png;base64," + base64.b64encode(image).decode(),
        0, 32768, openai_client=client,
        request_options={"image_detail": "original", "reasoning_effort": "medium"},
        request_records=records,
    )


def test_candidate_prompt_is_baseline_plus_only_shared_policy():
    assert build_system_prompt(None, True) == SYSTEM_PROMPT + "\n\n" + LITERAL_POLICY
    assert build_system_prompt("", True) == SYSTEM_PROMPT + "\n\n" + LITERAL_POLICY
    assert "Recipe hints:" not in build_system_prompt(None, True)
    assert build_system_prompt(None, False) == SYSTEM_PROMPT


def test_request_options_and_raw_image_bytes_are_preserved():
    client, captured = fake_client()
    records = []
    raw, usage, response_id = call(client, records)
    assert raw == RAW_HTML
    assert usage.model_dump()["input_tokens"] == 100
    assert response_id == "resp-test"
    request = captured[0]
    assert request["model"] == MODEL
    assert request["reasoning"] == {"effort": "medium"}
    assert request["max_output_tokens"] == 32768
    assert request["store"] is False
    assert "temperature" not in request
    assert request["input"][0]["content"] == [
        {"type": "input_text", "text": SYSTEM_PROMPT + "\n\n" + LITERAL_POLICY},
    ]
    image = request["input"][1]["content"][1]
    assert image["detail"] == "original"
    assert base64.b64decode(image["image_url"].split(",", 1)[1]) == IMAGE_BYTES


def test_receipt_hashes_actual_submitted_prompt_and_image_without_payload():
    client, _ = fake_client()
    records = []
    call(client, records)
    receipt = records[0]
    assert receipt["schema_version"] == "ocr_request_receipt_v1"
    assert receipt["requested_model"] == receipt["served_model"] == MODEL
    assert receipt["response_id"] == "resp-test"
    assert receipt["status"] == "completed"
    assert receipt["image_detail"] == "original"
    assert receipt["reasoning"] == {"effort": "medium"}
    assert receipt["max_output_tokens"] == 32768
    assert receipt["usage"] == {"input_tokens": 100, "output_tokens": 30}
    assert receipt["elapsed_seconds"] >= 0
    assert receipt["prompt_sha256"] == hashlib.sha256((SYSTEM_PROMPT + "\n\n" + LITERAL_POLICY).encode()).hexdigest()
    assert receipt["submitted_image_sha256"] == hashlib.sha256(IMAGE_BYTES).hexdigest()
    serialized = json.dumps(receipt)
    assert "base64," not in serialized
    assert "image_url" not in serialized
    assert "Literal transcription policy:" not in serialized
    call(client, records, image=IMAGE_BYTES + b"changed")
    assert records[1]["submitted_image_sha256"] != receipt["submitted_image_sha256"]
    assert records[1]["prompt_sha256"] == receipt["prompt_sha256"]


@pytest.mark.parametrize("status", [None, "incomplete", "failed", "in_progress", "queued"])
def test_noncompleted_response_rejected_but_receipt_retained(status):
    client, captured = fake_client(status=status)
    records = []
    with pytest.raises(RuntimeError, match="incomplete or status unavailable"):
        call(client, records)
    assert len(captured) == 1
    assert len(records) == 1
    assert records[0]["status"] == status


@pytest.mark.parametrize("served", [None, "gpt-6.1-sol", "gpt-6-astra-other", "gpt-6-astraevil"])
def test_wrong_served_identity_rejected_but_receipt_retained(served):
    client, _ = fake_client(model=served)
    records = []
    with pytest.raises(RuntimeError, match="identity mismatch"):
        call(client, records)
    assert records[0]["served_model"] == served


def test_explicit_dated_snapshot_identity_is_permitted():
    require_completed_identity({"requested_model": MODEL,
                                "served_model": MODEL + "-2026-10-06", "status": "completed"})


def test_incomplete_response_cannot_fall_back_to_hide_failure():
    client, captured = fake_client(status="incomplete")
    records = []
    with pytest.raises(RuntimeError, match="OCR failed on page image source.png"):
        _ocr_with_fallback(
            IMAGE_BYTES, "source.png", model=MODEL, retry_model="gpt-6.1-sol",
            system_prompt=build_system_prompt(None, True), user_text="Return HTML only.",
            temperature=0, max_output_tokens=32768, openai_client=client,
            request_options={"image_detail": "original", "reasoning_effort": "medium"},
            request_records=records,
        )
    assert len(captured) == 1
    assert len(records) == 1


def test_kept_raw_and_sanitized_html_preserve_literals_spans_and_ownership():
    raw = ('<table><tr><th colspan="3">“NAME”</th></tr>'
           '<tr><td rowspan="2">Al &amp; Nl &lt; l</td><td></td><td>—</td></tr>'
           '<tr><td>O’Neil</td><td>1l</td></tr></table>')
    client, _ = fake_client(output=raw)
    records = []
    kept_raw, cleaned, _, _, _, model = _ocr_with_fallback(
        IMAGE_BYTES, "source.png", model=MODEL, retry_model=None,
        system_prompt=build_system_prompt(None, True), user_text="Return HTML only.",
        temperature=0, max_output_tokens=32768, openai_client=client,
        request_options={"image_detail": "original", "reasoning_effort": "medium"},
        request_records=records,
    )
    assert kept_raw == raw
    assert model == MODEL
    assert compare_tables(raw, cleaned)["pass"]
    assert 'rowspan="2"' in cleaned
    assert 'colspan="3"' in cleaned
    assert "&lt; l" in cleaned
    assert "<td></td>" in cleaned
    assert "<td>—</td>" in cleaned


@pytest.mark.parametrize("tag", ["td", "th"])
def test_sanitizer_retains_span_limits_for_both_cell_types(tag):
    html = f'<table><tr><{tag} rowspan="65534" colspan="1000">Nl</{tag}></tr></table>'
    cleaned = sanitize_html(html)
    assert f'<{tag} rowspan="65534" colspan="1000">Nl</{tag}>' in cleaned


@pytest.mark.parametrize("attr,value", [("rowspan", "65535"), ("colspan", "1001"),
                                        ("rowspan", "0"), ("colspan", "-1"),
                                        ("rowspan", "2x")])
def test_sanitizer_does_not_retain_invalid_span_attributes(attr, value):
    cleaned = sanitize_html(f'<table><tr><td {attr}="{value}">Nl</td></tr></table>')
    assert attr not in cleaned
    assert "Nl" in cleaned


@pytest.mark.parametrize("model", ["gemini-3-pro", "claude-opus-4-6"])
def test_openai_transport_settings_cannot_silently_use_other_provider(model):
    with pytest.raises(ValueError, match="require OpenAI Responses"):
        _call_vision_model(model, "system", "user", "data:image/png;base64,YQ==",
                           0, 10, request_options={"image_detail": "original"})


@pytest.mark.parametrize("model", ["gemini-3-pro", "claude-opus-4-6"])
def test_receipt_only_literal_profile_cannot_bypass_provider_guard(model):
    with pytest.raises(ValueError, match="require OpenAI Responses"):
        _call_vision_model(model, "system", "user", "data:image/png;base64,YQ==",
                           0, 10, request_records=[])


def test_legacy_chat_cannot_bypass_literal_profile_settings_or_receipts():
    with pytest.raises(RuntimeError, match="requires the Responses API"):
        call(SimpleNamespace(chat=None), [])


def test_malformed_snapshot_suffix_is_not_a_served_model_identity():
    with pytest.raises(RuntimeError, match="identity mismatch"):
        require_completed_identity({"requested_model": MODEL,
                                    "served_model": MODEL + "-20anything", "status": "completed"})


def test_one_attempt_cap_stops_after_empty_response():
    client, captured = fake_client(output="")
    result = _ocr_with_fallback(
        IMAGE_BYTES, "page.png", model=MODEL, retry_model=None,
        system_prompt=build_system_prompt(None, True), user_text="Return HTML only.",
        temperature=0, max_output_tokens=8192, openai_client=client,
        request_records=[], max_attempts=1,
    )
    assert not result[1].strip()
    assert len(captured) == 1


def test_resized_jpeg_mime_survives_original_png_filename():
    client, captured = fake_client()
    _ocr_with_fallback(
        IMAGE_BYTES, "original.png", model=MODEL, retry_model=None,
        system_prompt="OCR", user_text="HTML", temperature=0, max_output_tokens=8192,
        openai_client=client, max_attempts=1, image_mime="image/jpeg",
    )
    assert captured[0]["input"][1]["content"][1]["image_url"].startswith("data:image/jpeg;base64,")
