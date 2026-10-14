"""Native Google source authority stays image-only, retained, and opt-in."""

import base64
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace

import httpx
from PIL import Image
import pytest

from doc_web.literal_fidelity import SourcePageReview
from modules.common.google_table_source_review import (
    ARGON, ASTRA, ASTRA_PROFILE, PROFILE, GoogleSourceOnlyReader, RetainedSourceOnlyReader,
    digest, native_google_output, validate_source_record,
)
from modules.common.literal_fidelity_bundle import validate_literal_fidelity_inputs
from modules.common.literal_table_review import review_literal_tables
from modules.common.table_source_review import POLICY, SourceOnlyReader


HTML = '<table><tr><td>Literal r2l3</td><td>1+</td></tr></table>'


def review_dict(*, uncertain=False):
    return {"source_table_count": 1, "tables": [{
        "bbox": [5.0, 5.0, 95.0, 55.0], "html": HTML,
        "uncertain_cells": ([{"row": 0, "cell": 0, "reason": "ambiguous glyph",
                              "alternatives": ["r2l3", "r213"]}] if uncertain else []),
    }]}


def envelope(*, review=None):
    return {"modelVersion": ARGON, "responseId": "native-response-test",
            "candidates": [{"finishReason": "STOP", "content": {"role": "model", "parts": [
                {"text": "private thought retained in envelope", "thought": True},
                {"text": json.dumps(review if review is not None else review_dict())},
            ]}}],
            "usageMetadata": {"promptTokenCount": 400, "candidatesTokenCount": 100,
                              "thoughtsTokenCount": 250, "cachedContentTokenCount": 0}}


@pytest.fixture
def image_path(tmp_path):
    image = tmp_path / "source.png"
    Image.new("RGB", (100, 60), "white").save(image)
    return image


def reader_for(payload, *, status=200, ledger_path=None, **kwargs):
    calls = []
    raw = payload if isinstance(payload, bytes) else json.dumps(payload).encode()

    def dispatch(request):
        calls.append(request)
        return httpx.Response(status, content=raw)

    client = httpx.Client(transport=httpx.MockTransport(dispatch))
    return GoogleSourceOnlyReader(client=client, api_key="fake-api-key-for-tests-only",
                                  ledger_path=ledger_path, **kwargs), calls, raw


def successful_record(image_path, *, review=None):
    reader, calls, raw = reader_for(envelope(review=review))
    records = []
    result = reader(image_path, records)
    assert len(calls) == 1
    return records[0], result, raw


def successful_astra_record(image_path):
    raw = json.dumps(review_dict())
    usage = {"input_tokens": 40, "output_tokens": 30, "total_tokens": 70,
             "input_tokens_details": {"cached_tokens": 0},
             "output_tokens_details": {"reasoning_tokens": 10}}
    native = {"id": "astra-test", "object": "response", "created_at": 0,
              "model": ASTRA, "status": "completed", "service_tier": "default",
              "error": None, "incomplete_details": None, "usage": usage,
              "output": [{"id": "message-test", "type": "message", "role": "assistant",
                          "status": "completed", "content": [{"type": "output_text",
                                                                "text": raw, "annotations": []}]}]}
    response = SimpleNamespace(output_text=raw, status="completed", model=ASTRA,
                               id=native["id"], usage=usage, service_tier="default")
    # Deliberately distinct HTTP serialization proves the saved bytes are not
    # a reconstructed SDK model dump. No dump method is provided by this fake.
    native_bytes = (json.dumps(native, indent=3) + "\n").encode()
    raw_response = SimpleNamespace(content=native_bytes, parse=lambda: response)
    client = SimpleNamespace(responses=SimpleNamespace(
        with_raw_response=SimpleNamespace(create=lambda **kwargs: raw_response)))
    records = []
    result = SourceOnlyReader(client=client)(image_path, records)
    assert records[0]["native_response_json"].encode() == native_bytes
    return records[0], result


def manifest_for(tmp_path, record, *, model=ARGON):
    record_path = tmp_path / "source-record.json"
    record_path.write_text(json.dumps(record))
    manifest = {"schema_version": "retained_source_reviews_v1", "model": model, "records": [{
        "image_sha256": record["submitted_image_sha256"], "record_path": str(record_path),
        "record_sha256": digest(record_path.read_bytes()),
    }]}
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))
    return manifest_path, record_path, manifest


def reviewed_row(tmp_path, image_path, *, review=None):
    record, _, _ = successful_record(image_path, review=review)
    manifest, _, _ = manifest_for(tmp_path, record)
    source = tmp_path / "source.pdf"
    source.write_bytes(b"bounded source PDF identity")
    row = {"page": 19, "page_number": 1, "original_page_number": 19,
           "image": str(image_path), "source": [str(source)], "raw_html": HTML, "html": HTML}
    rows = review_literal_tables([row], out_path=tmp_path / "reviewed.jsonl", run_id="native-test",
                                model=ARGON, source_review_receipts=manifest)
    return rows[0]


def test_actual_native_post_is_lossless_image_only_with_strict_bounded_policy(image_path):
    reader, calls, _ = reader_for(envelope())
    records = []
    result = reader(image_path, records)
    assert isinstance(result, SourcePageReview)
    request = calls[0]
    assert request.method == "POST"
    assert str(request.url) == f"https://generativelanguage.googleapis.com/v1beta/models/{ARGON}:generateContent"
    assert request.headers["x-goog-api-key"] == "fake-api-key-for-tests-only"
    body = json.loads(request.content)
    assert set(body) == {"systemInstruction", "contents", "generationConfig"}
    assert body["systemInstruction"] == {"parts": [{"text": POLICY}]}
    assert len(body["contents"]) == 1
    assert body["contents"][0]["role"] == "user"
    parts = body["contents"][0]["parts"]
    assert parts[0] == {"text": "Source image dimensions: 100 x 60 pixels. Read source tables; return JSON only."}
    assert len(parts) == 2 and set(parts[1]) == {"inlineData"}
    assert parts[1]["inlineData"]["mimeType"] == "image/png"
    assert base64.b64decode(parts[1]["inlineData"]["data"]) == image_path.read_bytes()
    config = body["generationConfig"]
    assert config == {"maxOutputTokens": 32768, "thinkingConfig": {"thinkingLevel": "medium"},
                      "responseMimeType": "application/json",
                      "responseJsonSchema": SourcePageReview.model_json_schema()}
    assert config["responseJsonSchema"]["additionalProperties"] is False
    assert all(value["additionalProperties"] is False for value in config["responseJsonSchema"]["$defs"].values())
    request_text = body["systemInstruction"]["parts"][0]["text"] + parts[0]["text"]
    assert "r2l3" not in request_text and str(image_path) not in request_text
    assert "golden" not in request_text.lower()
    assert records[0]["request_sha256"] == digest(json.dumps(body, sort_keys=True).encode())
    assert records[0]["provider"] == "google" and records[0]["authority_profile"] == PROFILE


def invalid_responses():
    cases = [(b"not-json", 200), (b'{"error":{"message":"rejected"}}', 403)]
    for field, value in [("modelVersion", ASTRA), ("modelVersion", ARGON + "-alias")]:
        data = envelope()
        data[field] = value
        cases.append((data, 200))
    for status in ["MAX_TOKENS", "SAFETY", None]:
        data = envelope()
        data["candidates"][0]["finishReason"] = status
        cases.append((data, 200))
    for output in ["```json\n{}\n```", "{}", '{"source_table_count":"1","tables":[]}',
                   json.dumps({**review_dict(), "ocr_text": "forbidden extra field"})]:
        data = envelope()
        data["candidates"][0]["content"]["parts"][1]["text"] = output
        cases.append((data, 200))
    return cases


@pytest.mark.parametrize("payload,status", invalid_responses())
def test_full_native_bytes_are_saved_before_http_identity_status_or_schema_rejection(
        image_path, tmp_path, payload, status):
    ledger = tmp_path / "ledger.json"
    reader, calls, raw = reader_for(payload, status=status, ledger_path=ledger)
    records = []
    with pytest.raises((RuntimeError, ValueError, httpx.HTTPStatusError)):
        reader(image_path, records)
    assert len(calls) == len(records) == 1
    assert Path(records[0]["native_response_path"]).read_bytes() == raw
    assert records[0]["native_response_json"].encode() == raw
    assert records[0]["native_response_sha256"] == digest(raw)
    saved = json.loads(ledger.read_text())
    assert saved["entries"][0] == records[0]
    assert records[0]["error_type"] and records[0]["elapsed_seconds"] >= 0
    assert saved["calls"] == 1 and saved["reserved_usd"] == pytest.approx(0.37968)


@pytest.mark.parametrize("name,value", [
    ("promptTokenCount", None), ("promptTokenCount", True), ("candidatesTokenCount", -1),
    ("candidatesTokenCount", 1.5), ("thoughtsTokenCount", "2"),
    ("thoughtsTokenCount", -1), ("cachedContentTokenCount", False),
    ("cachedContentTokenCount", 401), ("thoughtsTokenCount", 32768),
])
def test_native_usage_must_be_nonnegative_integers_with_valid_cache_and_output_bounds(name, value):
    data = envelope()
    data["usageMetadata"][name] = value
    with pytest.raises(RuntimeError):
        native_google_output(data)


def test_usage_allows_optional_zero_counts_and_exact_output_boundary():
    data = envelope()
    data["usageMetadata"] = {"promptTokenCount": 0, "candidatesTokenCount": 32768}
    assert json.loads(native_google_output(data)) == review_dict()


@pytest.mark.parametrize("mutation", ["two-candidates", "no-candidates", "no-visible", "binary-part", "extra-part-key"])
def test_ambiguous_or_absent_native_final_output_rejects(mutation):
    data = envelope()
    if mutation == "two-candidates":
        data["candidates"].append(deepcopy(data["candidates"][0]))
    elif mutation == "no-candidates":
        data["candidates"] = []
    elif mutation == "no-visible":
        data["candidates"][0]["content"]["parts"] = [{"text": "thought only", "thought": True}]
    elif mutation == "binary-part":
        data["candidates"][0]["content"]["parts"].append({"inlineData": {"data": "a"}})
    else:
        data["candidates"][0]["content"]["parts"][1]["unexpected"] = True
    with pytest.raises(RuntimeError):
        native_google_output(data)


def test_retained_manifest_consumes_hash_bound_native_receipt_without_post(image_path, tmp_path, monkeypatch):
    record, expected, _ = successful_record(image_path)
    manifest, _, _ = manifest_for(tmp_path, record)
    monkeypatch.setattr(httpx.Client, "post", lambda *args, **kwargs: pytest.fail("retained read must not POST"))
    retained = RetainedSourceOnlyReader(manifest, model=ARGON)
    records = []
    assert retained(image_path, records) == expected
    assert records == [record]
    with pytest.raises(ValueError, match="repeated"):
        retained(image_path, records)
    assert len(records) == 1


@pytest.mark.parametrize("mutation", ["missing", "tampered", "symlink", "duplicate", "model", "profile", "absent-image"])
def test_retained_manifest_rejects_missing_duplicate_tampered_or_foreign_evidence(image_path, tmp_path, mutation):
    record, _, _ = successful_record(image_path)
    manifest_path, record_path, manifest = manifest_for(tmp_path, record)
    if mutation == "missing":
        record_path.unlink()
    elif mutation == "tampered":
        record_path.write_text(record_path.read_text() + " ")
    elif mutation == "symlink":
        replacement = tmp_path / "replacement.json"
        record_path.rename(replacement)
        record_path.symlink_to(replacement)
    elif mutation == "duplicate":
        manifest["records"].append(deepcopy(manifest["records"][0]))
    elif mutation == "model":
        manifest["model"] = ASTRA
    elif mutation == "profile":
        record["authority_profile"] = "unqualified-profile"
        record_path.write_text(json.dumps(record))
        manifest["records"][0]["record_sha256"] = digest(record_path.read_bytes())
    else:
        manifest["records"] = []
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        retained = RetainedSourceOnlyReader(manifest_path, model=ARGON)
        retained(image_path, [])


@pytest.mark.parametrize("mutation", ["image", "prompt", "schema", "request", "native", "raw", "effort", "max", "detail", "usage", "response-id", "provider", "profile"])
def test_google_receipt_fields_and_native_envelope_cannot_be_mutated(image_path, mutation):
    record, _, _ = successful_record(image_path)
    fields = {"image": ("submitted_image_sha256", "0" * 64), "prompt": ("prompt_sha256", "0" * 64),
              "schema": ("response_schema_sha256", "0" * 64), "request": ("request_sha256", "0" * 64),
              "native": ("native_response_json", "{}"),
              "raw": ("raw_response", '{"source_table_count":0,"tables":[]}'),
              "effort": ("thinking_config", {"thinkingLevel": "high"}), "max": ("max_output_tokens", 8192),
              "detail": ("image_detail", "resized"), "usage": ("usage", {}),
              "response-id": ("response_id", "foreign-response"), "provider": ("provider", "openai"),
              "profile": ("authority_profile", "foreign-profile")}
    key, value = fields[mutation]
    record[key] = value
    with pytest.raises((ValueError, RuntimeError)):
        validate_source_record(record, model=ARGON, image_sha256=digest(image_path.read_bytes()), image_path=image_path)


def test_builder_google_authority_requires_explicit_selection_and_retained_review(image_path, tmp_path):
    row = reviewed_row(tmp_path, image_path)
    assert row["literal_fidelity"]["status"] == "verified"
    assert row["html"] == row["raw_html"] == HTML
    with pytest.raises(ValueError, match="identity/status"):
        validate_literal_fidelity_inputs([row], run_id="native-test", required=True)
    assert validate_literal_fidelity_inputs([row], run_id="native-test", required=True, reader_model=ARGON)


@pytest.mark.parametrize("mutation", ["source", "image", "prompt", "schema", "request", "native", "effort"])
def test_builder_rejects_bound_source_or_reader_mutations_even_with_resealed_report(image_path, tmp_path, mutation):
    row = reviewed_row(tmp_path, image_path)
    report_path = Path(row["literal_fidelity"]["report_path"])
    report = json.loads(report_path.read_text())
    if mutation == "source":
        Path(row["source"][0]).write_bytes(b"changed PDF")
    elif mutation == "image":
        Image.new("RGB", (100, 60), "black").save(image_path)
    else:
        record = report["requests"][0]
        key, value = {"prompt": ("prompt_sha256", "0" * 64), "schema": ("response_schema_sha256", "0" * 64),
                      "request": ("request_sha256", "0" * 64),
                      "native": ("native_response_json", "{}"), "effort": ("thinking_config", {"thinkingLevel": "high"})}[mutation]
        record[key] = value
        report_path.write_text(json.dumps(report))
        row["literal_fidelity"]["report_sha256"] = digest(report_path.read_bytes())
    with pytest.raises(ValueError):
        validate_literal_fidelity_inputs([row], run_id="native-test", required=True, reader_model=ARGON)


def test_native_uncertainty_is_retained_and_holds_builder_qualification(image_path, tmp_path):
    row = reviewed_row(tmp_path, image_path, review=review_dict(uncertain=True))
    assert row["literal_fidelity"]["status"] == "unresolved"
    report = json.loads(Path(row["literal_fidelity"]["report_path"]).read_text())
    assert report["tables"][0]["review"]["uncertain_cells"][0]["alternatives"] == ["r2l3", "r213"]
    assert row["html"] == HTML
    with pytest.raises(ValueError, match="unresolved receipt"):
        validate_literal_fidelity_inputs([row], run_id="native-test", required=True, reader_model=ARGON)

    # A forged green summary must not hide the raw native reader's uncertainty.
    report["status"] = "verified"
    report["unresolved_count"] = 0
    report["errors"] = []
    report["tables"][0]["decision"] = "initial_agrees_B"
    report_path = Path(row["literal_fidelity"]["report_path"])
    report_path.write_text(json.dumps(report))
    row["literal_fidelity"].update(status="verified", unresolved_count=0,
                                    report_sha256=digest(report_path.read_bytes()))
    with pytest.raises(ValueError, match="certain exact agreement"):
        validate_literal_fidelity_inputs([row], run_id="native-test", required=True, reader_model=ARGON)


@pytest.mark.parametrize("max_requests,budget", [(1, 4.5), (3, 0.37968)])
def test_caps_prevent_second_post_even_after_failed_native_response(image_path, max_requests, budget):
    reader, calls, _ = reader_for(b"malformed", max_requests=max_requests, budget_usd=budget)
    records = []
    with pytest.raises(ValueError):
        reader(image_path, records)
    with pytest.raises(RuntimeError, match="cap reached"):
        reader(image_path, records)
    assert len(calls) == len(records) == len(reader.entries) == 1


def test_insufficient_reservation_and_existing_ledger_prevent_post(image_path, tmp_path):
    reader, calls, _ = reader_for(envelope(), budget_usd=0.37967)
    with pytest.raises(RuntimeError, match="cap reached"):
        reader(image_path, [])
    assert calls == reader.entries == []
    ledger = tmp_path / "ledger.json"
    ledger.write_text("prior receipt ledger")
    with pytest.raises(ValueError, match="Fresh source-review ledger"):
        reader_for(envelope(), ledger_path=ledger)
    assert ledger.read_text() == "prior receipt ledger"


def test_retained_request_hash_is_checked_against_image_at_consumption(image_path, tmp_path):
    record, _, _ = successful_record(image_path)
    record["request_sha256"] = "0" * 64
    manifest, _, _ = manifest_for(tmp_path, record)
    retained = RetainedSourceOnlyReader(manifest, model=ARGON)
    records = []
    with pytest.raises(ValueError, match="native request"):
        retained(image_path, records)
    assert records == []


def test_astra_and_google_cannot_impersonate_each_other_by_relabeling_model(image_path):
    google, _, _ = successful_record(image_path)
    google.update(requested_model=ASTRA, served_model=ASTRA, status="completed",
                  reasoning={"effort": "medium"}, image_detail="original")
    with pytest.raises(ValueError, match="authority profile"):
        validate_source_record(google, model=ASTRA, image_sha256=digest(image_path.read_bytes()), image_path=image_path)

    astra, _ = successful_astra_record(image_path)
    assert validate_source_record(astra, model=ASTRA, image_sha256=digest(image_path.read_bytes()), image_path=image_path)
    astra.update(requested_model=ARGON, served_model=ARGON, status="STOP")
    with pytest.raises(ValueError, match="Google source-read configuration"):
        validate_source_record(astra, model=ARGON, image_sha256=digest(image_path.read_bytes()), image_path=image_path)


def astra_reviewed_row(tmp_path, image_path):
    record, _ = successful_astra_record(image_path)
    manifest, _, _ = manifest_for(tmp_path, record, model=ASTRA)
    row = {"page": 19, "page_number": 1, "original_page_number": 19,
           "image": str(image_path), "raw_html": HTML, "html": HTML}
    rows = review_literal_tables([row], out_path=tmp_path / "astra-reviewed.jsonl",
                                run_id="astra-test", source_review_receipts=manifest)
    assert rows[0]["literal_fidelity"]["status"] == "verified"
    return rows[0]


def test_retained_native_astra_qualifies_default_builder_without_post(image_path, tmp_path, monkeypatch):
    monkeypatch.setattr(httpx.Client, "post", lambda *args, **kwargs: pytest.fail("retained read must not POST"))
    row = astra_reviewed_row(tmp_path, image_path)
    qualified = validate_literal_fidelity_inputs([row], run_id="astra-test", required=True)
    assert qualified
    report = json.loads(qualified[0]["report_bytes"])
    assert report["requests"][0]["provider"] == "openai"
    assert report["requests"][0]["authority_profile"] == ASTRA_PROFILE
    assert report["requests"][0]["service_tier"] == "default"
    with pytest.raises(ValueError):
        validate_literal_fidelity_inputs([row], run_id="astra-test", required=True, reader_model=ARGON)


@pytest.mark.parametrize("mutation", [
    "missing-provider", "foreign-provider", "missing-profile", "foreign-profile",
    "missing-native", "foreign-native", "missing-native-hash", "foreign-native-hash",
    "missing-request-hash", "foreign-request-hash", "missing-tier", "foreign-tier",
    "missing-native-tier", "foreign-native-tier", "foreign-native-model", "foreign-native-id",
])
def test_default_builder_rejects_astra_metadata_or_native_mutation_in_resealed_report(image_path, tmp_path, mutation):
    row = astra_reviewed_row(tmp_path, image_path)
    report_path = Path(row["literal_fidelity"]["report_path"])
    report = json.loads(report_path.read_bytes())
    record = report["requests"][0]
    if mutation in {"missing-native-tier", "foreign-native-tier", "foreign-native-model", "foreign-native-id"}:
        native = json.loads(record["native_response_json"])
        if mutation == "missing-native-tier":
            native.pop("service_tier")
        elif mutation == "foreign-native-tier":
            native["service_tier"] = "priority"
        elif mutation == "foreign-native-model":
            native["model"] = ARGON
        else:
            native["id"] = "foreign-response"
        record["native_response_json"] = json.dumps(native)
        record["native_response_sha256"] = digest(record["native_response_json"].encode())
    else:
        field = {"provider": "provider", "profile": "authority_profile", "native": "native_response_json",
                 "native-hash": "native_response_sha256", "request-hash": "request_sha256",
                 "tier": "service_tier"}[mutation.split("-", 1)[1]]
        if mutation.startswith("missing-"):
            record.pop(field)
        else:
            record[field] = {"provider": "google", "authority_profile": PROFILE,
                             "native_response_json": "{}", "native_response_sha256": "0" * 64,
                             "request_sha256": "0" * 64, "service_tier": "priority"}[field]
    report_path.write_text(json.dumps(report))
    row["literal_fidelity"]["report_sha256"] = digest(report_path.read_bytes())
    with pytest.raises(ValueError):
        validate_literal_fidelity_inputs([row], run_id="astra-test", required=True)


def test_native_astra_actual_image_is_required_for_direct_validation(image_path):
    record, _ = successful_astra_record(image_path)
    with pytest.raises(ValueError, match="actual bound image"):
        validate_source_record(record, model=ASTRA, image_sha256=digest(image_path.read_bytes()))


@pytest.mark.parametrize("field,value", [("input_tokens", None), ("input_tokens", True),
                                        ("output_tokens", -1), ("output_tokens", 1.5),
                                        ("output_tokens", 8193)])
def test_native_astra_usage_rejects_invalid_or_exceeded_counts(image_path, field, value):
    record, _ = successful_astra_record(image_path)
    native = json.loads(record["native_response_json"])
    native["usage"][field] = value
    record["usage"] = native["usage"]
    record["native_response_json"] = json.dumps(native)
    record["native_response_sha256"] = digest(record["native_response_json"].encode())
    with pytest.raises(ValueError):
        validate_source_record(record, model=ASTRA, image_sha256=digest(image_path.read_bytes()), image_path=image_path)


def test_google_native_envelope_cannot_become_astra_authority_by_metadata_relabel(image_path):
    google, _, _ = successful_record(image_path)
    astra, _ = successful_astra_record(image_path)
    # Copy every Astra metadata claim and request digest while retaining the
    # actual Google HTTP envelope and visible text. The native provider fails.
    native, native_sha = google["native_response_json"], google["native_response_sha256"]
    google.update(astra)
    google.update(native_response_json=native, native_response_sha256=native_sha)
    with pytest.raises(ValueError, match="differs from native raw response"):
        validate_source_record(google, model=ASTRA, image_sha256=digest(image_path.read_bytes()), image_path=image_path)
