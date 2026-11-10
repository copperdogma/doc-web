"""Offline provider-state boundary; no API calls."""

import copy
import pytest
from benchmarks.scripts.carbon_state_custody import MARKER, redact


def test_state_redaction_preserves_output_usage_identity_and_terminal():
    original = {
        "modelVersion": "gemini-4-carbon",
        "candidates": [
            {
                "finishReason": "STOP",
                "content": {
                    "role": "model",
                    "parts": [
                        {
                            "text": "exact source text",
                            "thoughtSignature": "opaque signed state",
                        }
                    ],
                },
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 100,
            "candidatesTokenCount": 12,
            "thoughtsTokenCount": 500,
        },
    }
    before = copy.deepcopy(original)
    public, fields = redact(original)
    assert original == before
    assert fields == ["/candidates/0/content/parts/0/thoughtSignature"]
    assert public["candidates"][0]["content"]["parts"][0] == {
        "text": "exact source text",
        "thoughtSignature": MARKER,
    }
    assert public["usageMetadata"] == original["usageMetadata"]
    assert public["modelVersion"] == original["modelVersion"]
    assert public["candidates"][0]["finishReason"] == "STOP"
    assert redact(public) == (public, [])


def test_continuation_access_state_is_redacted_without_altering_text():
    original = {
        "continuationToken": "server cursor",
        "nested": [
            {
                "access_token": "credential",
                "text": "The word continuationToken is part of the source.",
            }
        ],
    }
    public, fields = redact(original)
    assert len(fields) == 2 and public["continuationToken"] == MARKER
    assert public["nested"][0]["access_token"] == MARKER
    assert public["nested"][0]["text"] == original["nested"][0]["text"]


def test_signed_url_requires_review_before_projection():
    with pytest.raises(ValueError, match="signed/auth URL"):
        redact({"uri": "https://example.test/resource?X-Goog-Signature=opaquevalue"})


def test_nested_encrypted_provider_response_is_projected_without_answer_change():
    import json

    native = {
        "model": "gpt-6-astra",
        "status": "completed",
        "usage": {"output_tokens": 12},
        "output": [
            {"type": "reasoning", "encrypted_content": "opaque encrypted state"},
            {
                "type": "message",
                "content": [{"type": "output_text", "text": "exact answer"}],
            },
        ],
    }
    original = {"requests": [{"native_response_json": json.dumps(native)}]}
    public, fields = redact(original)
    assert fields == [
        "/requests/0/native_response_json [nested-json]/output/0/encrypted_content"
    ]
    recovered = json.loads(public["requests"][0]["native_response_json"])
    assert recovered["output"][0]["encrypted_content"] == MARKER
    assert recovered["output"][1] == native["output"][1]
    assert (
        recovered["model"] == native["model"]
        and recovered["status"] == "completed"
        and recovered["usage"] == native["usage"]
    )
    assert redact(public) == (public, [])
