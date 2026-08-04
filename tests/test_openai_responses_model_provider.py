import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROVIDER_PATH = ROOT / "benchmarks" / "providers" / "openai_responses_model.py"


def _load_provider():
    spec = importlib.util.spec_from_file_location(
        "openai_responses_model", PROVIDER_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_openai_responses_model_normalizes_chat_image_prompt(monkeypatch):
    provider = _load_provider()
    monkeypatch.setenv("OPENAI_RESPONSES_MODEL", "gpt-5.6-terra")
    monkeypatch.setenv("OPENAI_RESPONSES_REASONING_EFFORT", "low")
    monkeypatch.setenv("OPENAI_RESPONSES_MAX_OUTPUT_TOKENS", "123")

    prompt = json.dumps(
        [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this crop."},
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/jpeg;base64,abc"},
                    },
                ],
            }
        ]
    )

    body = provider._build_body(prompt)

    assert body["model"] == "gpt-5.6-terra"
    assert body["max_output_tokens"] == 123
    assert body["reasoning"] == {"effort": "low"}
    assert body["store"] is False
    assert body["text"]["format"] == provider.CROP_RESPONSE_FORMAT
    assert body["text"]["format"]["strict"] is True
    assert body["input"] == [
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Describe this crop."},
                {
                    "type": "input_image",
                    "image_url": "data:image/jpeg;base64,abc",
                    "detail": "high",
                },
            ],
        }
    ]


def test_openai_responses_model_estimates_cost_from_env(monkeypatch):
    provider = _load_provider()
    monkeypatch.setenv("OPENAI_RESPONSES_INPUT_PRICE_PER_1M", "2.5")
    monkeypatch.setenv("OPENAI_RESPONSES_OUTPUT_PRICE_PER_1M", "15")

    cost = provider._estimated_cost(
        {"prompt": 1_000_000, "completion": 1_000_000, "total": 2_000_000}
    )

    assert cost == 17.5


def test_openai_responses_model_uses_cached_input_price(monkeypatch):
    provider = _load_provider()
    monkeypatch.setenv("OPENAI_RESPONSES_INPUT_PRICE_PER_1M", "0.20")
    monkeypatch.setenv("OPENAI_RESPONSES_CACHED_INPUT_PRICE_PER_1M", "0.02")
    monkeypatch.setenv("OPENAI_RESPONSES_OUTPUT_PRICE_PER_1M", "1.20")

    cost = provider._estimated_cost(
        {
            "prompt": 1_000_000,
            "completion": 1_000_000,
            "total": 2_000_000,
            "cached": 500_000,
        }
    )

    assert cost == 1.31


def test_openai_responses_model_rejects_lossy_prompt_normalization():
    provider = _load_provider()
    prompt = json.dumps(
        [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Inspect the required file"},
                    {"type": "input_file", "file_id": "file-required"},
                ],
            }
        ]
    )

    try:
        provider._build_body(prompt)
    except ValueError as exc:
        assert str(exc) == "Unsupported prompt content type: 'input_file'"
    else:
        raise AssertionError("unsupported content must fail before the API call")


def test_openai_responses_model_rejects_non_positive_crop_boxes():
    provider = _load_provider()

    error = provider._contract_error(
        '{"images":[{"description":"bad","bbox":[0.8,0.2,0.1,0.9]}]}',
        "crop_regions",
    )

    assert error == "images[0].bbox must have positive width and height"


def test_openai_responses_model_requires_completed_exact_contract_response(monkeypatch):
    provider = _load_provider()

    class FakeResponse:
        headers = {"x-zero-data-retention": "true"}

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "id": "resp-123",
                "model": "gpt-5.6-luna",
                "status": "completed",
                "service_tier": "default",
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {"type": "output_text", "text": '{"images":[]}'},
                        ],
                    }
                ],
                "usage": {
                    "input_tokens": 100,
                    "input_tokens_details": {"cached_tokens": 20},
                    "output_tokens": 10,
                    "total_tokens": 110,
                },
            }

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_RESPONSES_MODEL", "gpt-5.6-luna")
    monkeypatch.setattr(provider.httpx, "post", lambda *args, **kwargs: FakeResponse())

    result = provider.call_api("inspect", {}, {})

    assert result["output"] == '{"images":[]}'
    assert result["metadata"]["served_model"] == "gpt-5.6-luna"
    assert result["metadata"]["response_status"] == "completed"
    assert result["metadata"]["zero_data_retention"] == "true"
    assert result["tokenUsage"] == {
        "prompt": 100,
        "completion": 10,
        "total": 110,
        "cached": 20,
    }
