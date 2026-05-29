from types import SimpleNamespace

from modules.common import anthropic_client
from modules.common.anthropic_client import AnthropicVisionClient


class _FakeMessages:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text="<p>ok</p>")],
            usage=SimpleNamespace(input_tokens=1, output_tokens=2),
            id="msg_test",
        )


class _FakeAnthropicModule:
    def __init__(self):
        self.messages = _FakeMessages()

    def Anthropic(self, api_key):
        assert api_key == "test-key"
        return self


def _client_call(model: str, monkeypatch):
    fake = _FakeAnthropicModule()
    monkeypatch.setattr(anthropic_client, "anthropic", fake)

    client = AnthropicVisionClient(api_key="test-key")
    raw, usage, response_id = client.generate_vision(
        model=model,
        system_prompt="system",
        user_text="user",
        image_data="data:image/png;base64,WA==",
        temperature=0.0,
    )

    assert raw == "<p>ok</p>"
    assert usage.input_tokens == 1
    assert response_id == "msg_test"
    return fake.messages.calls[0]


def test_anthropic_vision_client_omits_sampling_params_for_opus48(monkeypatch):
    call = _client_call("claude-opus-4-8", monkeypatch)

    assert "temperature" not in call
    assert call["thinking"] == {"type": "adaptive"}
    assert call["output_config"] == {"effort": "high"}


def test_anthropic_vision_client_keeps_temperature_for_older_claude(monkeypatch):
    call = _client_call("claude-opus-4-6", monkeypatch)

    assert call["temperature"] == 0.0
    assert "thinking" not in call
    assert "output_config" not in call
