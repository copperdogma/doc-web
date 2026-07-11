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
    assert body["input"] == [
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Describe this crop."},
                {"type": "input_image", "image_url": "data:image/jpeg;base64,abc"},
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
