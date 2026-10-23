"""Native source readers retain raw bytes and count usage without reinference."""

import hashlib
import json

import httpx
from PIL import Image
import pytest

from modules.common.google_table_source_review import GoogleSourceOnlyReader
from modules.common.openai_client import OpenAI
from modules.common.table_source_review import SourceOnlyReader, astra_request


REVIEW = {"source_table_count": 1, "tables": [{
    "bbox": [1, 1, 15, 11], "html": "<table><tr><td>A</td></tr></table>",
    "uncertain_cells": [],
}]}


def astra_native():
    return {"id": "resp_offline_usage", "object": "response", "created_at": 0,
            "status": "completed", "model": "gpt-6-astra", "service_tier": "default",
            "error": None, "incomplete_details": None,
            "output": [{"id": "msg_offline_usage", "type": "message", "role": "assistant",
                        "status": "completed", "content": [{"type": "output_text",
                        "text": json.dumps(REVIEW), "annotations": []}]}],
            "usage": {"input_tokens": 40, "output_tokens": 30, "total_tokens": 70,
                      "input_tokens_details": {"cached_tokens": 0},
                      "output_tokens_details": {"reasoning_tokens": 10}}}


@pytest.fixture
def source_and_sink(tmp_path, monkeypatch):
    image = tmp_path / "source.png"
    Image.new("RGB", (16, 12), "white").save(image)
    sink = tmp_path / "instrument.jsonl"
    monkeypatch.setenv("INSTRUMENT_SINK", str(sink))
    monkeypatch.setenv("INSTRUMENT_STAGE", "literal_table_review")
    monkeypatch.delenv("DOC_WEB_LITERAL_CAMPAIGN_FILE", raising=False)
    return image, sink


def native_client(payload):
    raw = (json.dumps(payload, indent=3) + "\n").encode()
    calls = []

    def dispatch(request):
        calls.append(request)
        return httpx.Response(200, content=raw, headers={"content-type": "application/json"})

    client = OpenAI(api_key="offline-placeholder", max_retries=0,
                    http_client=httpx.Client(transport=httpx.MockTransport(dispatch)))
    return client, raw, calls


def test_raw_sdk_content_precedes_parse_and_cached_parse_logs_once(source_and_sink):
    image, sink = source_and_sink
    client, raw, calls = native_client(astra_native())
    native = client.responses.with_raw_response.create(**astra_request(image))
    assert native.content == raw
    assert native.http_response.content == raw
    assert not sink.exists()
    first = native.parse()
    assert native.parse() is first
    events = [json.loads(line) for line in sink.read_text().splitlines()]
    assert len(calls) == len(events) == 1
    assert events[0]["prompt_tokens"] == 40
    assert events[0]["completion_tokens"] == 30  # thinking is already inclusive
    assert events[0]["stage_id"] == "literal_table_review"
    assert events[0]["provider"] == "openai"


def test_source_reader_raw_authority_and_usage_sink_survive_together(source_and_sink, tmp_path):
    image, sink = source_and_sink
    client, raw, calls = native_client(astra_native())
    records = []
    result = SourceOnlyReader(client=client, ledger_path=tmp_path / "ledger.json")(image, records)
    assert result.source_table_count == 1
    assert records[0]["native_response_json"].encode() == raw
    assert records[0]["native_response_sha256"] == hashlib.sha256(raw).hexdigest()
    assert len(calls) == len(sink.read_text().splitlines()) == 1


@pytest.mark.parametrize("malformed_answer", [False, True])
def test_google_counts_visible_and_thinking_before_semantic_validation(
    source_and_sink, tmp_path, malformed_answer
):
    image, sink = source_and_sink
    data = {"modelVersion": "gemini-4-argon", "responseId": "google-offline-usage",
            "candidates": [{"finishReason": "STOP", "content": {"role": "model",
                "parts": [{"text": "{bad}" if malformed_answer else json.dumps(REVIEW)}]}}],
            "usageMetadata": {"promptTokenCount": 400, "candidatesTokenCount": 100,
                              "thoughtsTokenCount": 250, "cachedContentTokenCount": 0}}
    raw = json.dumps(data).encode()
    client = httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, content=raw)))
    records = []
    reader = GoogleSourceOnlyReader(client=client, api_key="offline-placeholder",
                                   ledger_path=tmp_path / "google-ledger.json")
    if malformed_answer:
        with pytest.raises(ValueError):
            reader(image, records)
    else:
        assert reader(image, records).source_table_count == 1
    event, = [json.loads(line) for line in sink.read_text().splitlines()]
    assert records[0]["native_response_json"].encode() == raw
    assert event["prompt_tokens"] == 400
    assert event["completion_tokens"] == 350
    assert event["provider"] == "google"
    assert event["request_id"] == "google-offline-usage"


@pytest.mark.parametrize("usage", [
    {"promptTokenCount": -1, "candidatesTokenCount": 2},
    {"promptTokenCount": 2},
    {"promptTokenCount": True, "candidatesTokenCount": 2},
    {"promptTokenCount": 2, "candidatesTokenCount": 2, "cachedContentTokenCount": 3},
])
def test_google_invalid_usage_preserves_raw_without_inventing_sink_counts(source_and_sink, usage):
    image, sink = source_and_sink
    data = {"modelVersion": "gemini-4-argon", "responseId": "invalid-native-usage",
            "candidates": [{"finishReason": "STOP", "content": {"role": "model",
                           "parts": [{"text": json.dumps(REVIEW)}]}}],
            "usageMetadata": usage}
    raw = json.dumps(data).encode()
    client = httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, content=raw)))
    records = []
    with pytest.raises(RuntimeError, match="usage"):
        GoogleSourceOnlyReader(client=client, api_key="offline-placeholder")(image, records)
    assert records[0]["native_response_json"].encode() == raw
    assert not sink.exists()
