from __future__ import annotations

import json

from benchmarks.providers import xai_grok_responses as provider


def test_build_body_normalizes_multimodal_prompt(monkeypatch):
    monkeypatch.setenv("XAI_GROK_REASONING_EFFORT", "medium")
    prompt = json.dumps(
        [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Inspect this image"},
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/png;base64,abc"},
                    },
                ],
            }
        ]
    )

    body = provider._build_body(prompt)

    assert body["model"] == "grok-4.5"
    assert body["reasoning"] == {"effort": "medium"}
    assert body["store"] is False
    assert body["input"][0]["content"] == [
        {"type": "input_text", "text": "Inspect this image"},
        {
            "type": "input_image",
            "image_url": "data:image/png;base64,abc",
            "detail": "high",
        },
    ]


def test_extracts_output_usage_and_reported_cost(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "output": [
                    {"type": "reasoning", "content": []},
                    {
                        "type": "message",
                        "content": [
                            {"type": "output_text", "text": '{"ok":true}'}
                        ],
                    },
                ],
                "usage": {
                    "input_tokens": 100,
                    "input_tokens_details": {"cached_tokens": 20},
                    "output_tokens": 10,
                    "total_tokens": 110,
                    "cost_in_usd_ticks": 2400000,
                },
            }

    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setattr(provider.httpx, "post", lambda *args, **kwargs: FakeResponse())

    result = provider.call_api("hello", {}, {})

    assert result == {
        "output": '{"ok":true}',
        "tokenUsage": {
            "prompt": 100,
            "completion": 10,
            "total": 110,
            "cached": 20,
        },
        "cost": 0.00024,
    }
