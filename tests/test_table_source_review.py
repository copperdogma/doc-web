"""Source-only review uses bounded, inspectable requests and fails closed."""

import base64
import hashlib
import json
from types import SimpleNamespace

from PIL import Image
import pytest
from pydantic import ValidationError

from doc_web.literal_fidelity import SourcePageReview
from modules.common import table_source_review
from modules.common.table_source_review import POLICY, SourceOnlyReader


@pytest.fixture
def image_path(tmp_path):
    path = tmp_path / "source.png"
    Image.new("RGB", (16, 12), "white").save(path)
    return path


def review_dict():
    return {"source_table_count": 1, "tables": [
        {"bbox": [1.0, 2.0, 15.0, 11.0], "html": "<table><tr><td>Nl</td></tr></table>",
         "uncertain_cells": []},
    ]}


def fake_client(*, output=None, status="completed", model="gpt-6-astra", error=None):
    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        if error:
            raise error
        return SimpleNamespace(
            output_text=json.dumps(review_dict()) if output is None else output,
            status=status, model=model, id="source-test-response", usage=None,
        )

    return SimpleNamespace(responses=SimpleNamespace(create=create)), calls


def test_only_image_dimensions_and_generic_policy_are_submitted(image_path):
    client, calls = fake_client()
    records = []
    result = SourceOnlyReader(client=client)(image_path, records)
    assert isinstance(result, SourcePageReview)
    request = calls[0]
    assert request["model"] == "gpt-6-astra"
    assert request["store"] is False
    assert request["reasoning"] == {"effort": "medium"}
    assert request["max_output_tokens"] == 8192
    assert request["text"]["format"] == {
        "type": "json_schema", "name": "source_page_tables", "strict": True,
        "schema": SourcePageReview.model_json_schema(),
    }
    assert request["input"][0] == {
        "role": "system", "content": [{"type": "input_text", "text": POLICY}],
    }
    content = request["input"][1]["content"]
    assert len(content) == 2
    assert content[0] == {"type": "input_text", "text":
                          "Source image dimensions: 16 x 12 pixels. Read source tables; return JSON only."}
    assert content[1]["type"] == "input_image"
    assert content[1]["detail"] == "original"
    assert base64.b64decode(content[1]["image_url"].split(",", 1)[1]) == image_path.read_bytes()
    assert set(request) == {"model", "max_output_tokens", "store", "reasoning", "text", "input"}
    # Response/native/OCR tokens and paths never get inserted into request text.
    text = "\n".join(c["text"] for msg in request["input"] for c in msg["content"] if c["type"] == "input_text")
    assert "Nl" not in text
    assert str(image_path) not in text
    assert "golden" not in text.lower()


def test_sdk_retries_are_disabled_and_timeout_bounded(monkeypatch):
    client, _ = fake_client()
    kwargs_seen = []

    def constructor(**kwargs):
        kwargs_seen.append(kwargs)
        return client

    monkeypatch.setattr(table_source_review, "OpenAI", constructor)
    reader = SourceOnlyReader()
    assert reader.client is client
    assert kwargs_seen == [{"max_retries": 0, "timeout": 180}]


def test_success_receipt_hashes_request_and_preserves_raw_response(image_path, tmp_path):
    client, calls = fake_client()
    ledger_path = tmp_path / "nested" / "ledger.json"
    reader = SourceOnlyReader(client=client, ledger_path=ledger_path)
    records = []
    reader(image_path, records)
    record = records[0]
    assert record["submitted_image_sha256"] == hashlib.sha256(image_path.read_bytes()).hexdigest()
    assert record["prompt_sha256"] == hashlib.sha256(POLICY.encode()).hexdigest()
    schema = calls[0]["text"]["format"]["schema"]
    assert record["response_schema_sha256"] == hashlib.sha256(json.dumps(schema, sort_keys=True).encode()).hexdigest()
    assert json.loads(record["raw_response"]) == review_dict()
    assert record["served_model"] == record["requested_model"] == "gpt-6-astra"
    assert record["status"] == "completed"
    assert record["image_detail"] == "original"
    ledger = json.loads(ledger_path.read_text())
    assert ledger["calls"] == 1
    assert ledger["reserved_usd"] == 1.5
    assert ledger["entries"][0]["status"] == "completed"


@pytest.mark.parametrize("status", [None, "incomplete", "failed", "in_progress"])
def test_incomplete_status_fails_and_retains_raw(image_path, tmp_path, status):
    client, calls = fake_client(status=status)
    reader = SourceOnlyReader(client=client, ledger_path=tmp_path / "ledger.json")
    records = []
    with pytest.raises(RuntimeError):
        reader(image_path, records)
    assert len(calls) == 1
    assert records[0]["status"] == status
    assert json.loads(records[0]["raw_response"]) == review_dict()
    assert records[0]["error_type"] == "RuntimeError"
    assert reader.entries[0]["status"] == "failed"


@pytest.mark.parametrize("model", [None, "gpt-6.1-sol", "gpt-6-astraevil"])
def test_wrong_served_identity_fails_and_retains_raw(image_path, model):
    client, calls = fake_client(model=model)
    records = []
    with pytest.raises(RuntimeError, match="identity mismatch"):
        SourceOnlyReader(client=client)(image_path, records)
    assert len(calls) == 1
    assert records[0]["served_model"] == model
    assert "raw_response" in records[0]


def invalid_outputs():
    extra_root = review_dict()
    extra_root["ocr_text"] = "leak"
    extra_table = review_dict()
    extra_table["tables"][0]["confidence"] = 1
    incomplete = review_dict()
    incomplete["source_table_count"] = 2
    wrong_type = review_dict()
    wrong_type["source_table_count"] = "1"
    extra_uncertain = review_dict()
    extra_uncertain["tables"][0]["uncertain_cells"] = [
        {"row": 0, "cell": 0, "reason": "ambiguous", "alternatives": ["Nl", "N1"], "verified": True},
    ]
    return ["not JSON", "```json\n{}\n```", "{}", "[]", *map(json.dumps,
            [extra_root, extra_table, incomplete, wrong_type, extra_uncertain])]


@pytest.mark.parametrize("output", invalid_outputs())
def test_invalid_json_or_contract_is_rejected_and_retained(image_path, output):
    client, calls = fake_client(output=output)
    reader = SourceOnlyReader(client=client)
    records = []
    with pytest.raises(ValidationError):
        reader(image_path, records)
    assert len(calls) == 1
    assert records[0]["raw_response"] == output
    assert records[0]["error_type"] == "ValidationError"
    assert reader.entries[0]["status"] == "failed"


def test_complete_inventory_and_uncertainty_are_typed():
    data = review_dict()
    data["tables"][0]["uncertain_cells"] = [
        {"row": 0, "cell": 0, "reason": "glyph ambiguous", "alternatives": ["Nl", "N1"]},
    ]
    review = SourcePageReview.model_validate(data)
    assert review.tables[0].uncertain_cells[0].alternatives == ["Nl", "N1"]
    assert SourcePageReview.model_validate({"source_table_count": 0, "tables": []}).tables == []
    with pytest.raises(ValidationError, match="Incomplete source table inventory"):
        SourcePageReview.model_validate({"source_table_count": 1, "tables": []})
    data["tables"][0]["uncertain_cells"][0]["row"] = -1
    with pytest.raises(ValidationError):
        SourcePageReview.model_validate(data)


@pytest.mark.parametrize("max_requests,budget", [(1, 15), (10, 1.5)])
def test_no_dispatch_after_request_or_reservation_cap(image_path, max_requests, budget):
    client, calls = fake_client()
    reader = SourceOnlyReader(client=client, max_requests=max_requests, budget_usd=budget)
    records = []
    reader(image_path, records)
    with pytest.raises(RuntimeError, match="cap reached"):
        reader(image_path, records)
    assert len(calls) == len(records) == len(reader.entries) == 1


def test_insufficient_reservation_budget_prevents_any_attempt(image_path):
    client, calls = fake_client()
    records = []
    reader = SourceOnlyReader(client=client, budget_usd=1.49)
    with pytest.raises(RuntimeError, match="cap reached"):
        reader(image_path, records)
    assert calls == records == reader.entries == []


def test_failed_dispatch_still_consumes_reservation_and_request_cap(image_path):
    client, calls = fake_client(error=ConnectionError("transport failure"))
    reader = SourceOnlyReader(client=client, max_requests=1)
    records = []
    with pytest.raises(ConnectionError):
        reader(image_path, records)
    assert records[0]["error_type"] == "ConnectionError"
    with pytest.raises(RuntimeError, match="cap reached"):
        reader(image_path, records)
    assert len(calls) == len(records) == len(reader.entries) == 1


def test_existing_ledger_cannot_reset_spend_or_resume_silently(image_path, tmp_path):
    ledger = tmp_path / "ledger.json"
    client, calls = fake_client()
    SourceOnlyReader(client=client, ledger_path=ledger)(image_path, [])
    with pytest.raises(ValueError, match="Fresh source-review ledger required"):
        SourceOnlyReader(client=client, ledger_path=ledger)
    assert len(calls) == 1
    assert json.loads(ledger.read_text())["reserved_usd"] == 1.5


@pytest.mark.parametrize("model", ["gpt-6.1-sol", "gpt-6-astra-2026-10-06", "unknown"])
def test_unknown_or_unevaluated_model_rejected_before_client_creation(monkeypatch, model):
    def forbidden(**kwargs):
        pytest.fail("client should not be constructed for unevaluated model")

    monkeypatch.setattr(table_source_review, "OpenAI", forbidden)
    with pytest.raises(ValueError, match="requires gpt-6-astra"):
        SourceOnlyReader(model=model)


def test_oversized_input_rejected_before_request_or_reservation(image_path):
    # Valid small PNG with trailing bytes exercises the byte bound without a
    # decompression bomb or a huge pixel allocation.
    with image_path.open("ab") as file:
        file.write(b"x" * (20 * 1024 * 1024))
    client, calls = fake_client()
    reader = SourceOnlyReader(client=client)
    records = []
    with pytest.raises(ValueError, match="bounded review size"):
        reader(image_path, records)
    assert calls == records == reader.entries == []
