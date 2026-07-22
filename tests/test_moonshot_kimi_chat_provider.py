import importlib.util
from pathlib import Path


PROVIDER_PATH = (
    Path(__file__).parents[1] / "benchmarks" / "providers" / "moonshot_kimi_chat.py"
)
SPEC = importlib.util.spec_from_file_location("moonshot_kimi_chat", PROVIDER_PATH)
assert SPEC and SPEC.loader
provider = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(provider)


def test_k3_body_uses_reasoning_effort_without_legacy_thinking(monkeypatch):
    monkeypatch.setenv("MOONSHOT_KIMI_MODEL", "kimi-k3")

    body = provider._build_body('[{"role":"user","content":"hello"}]')

    assert body["model"] == "kimi-k3"
    assert body["reasoning_effort"] == "max"
    assert "thinking" not in body
    assert "temperature" not in body
    assert "top_p" not in body


def test_k26_body_keeps_legacy_thinking_contract(monkeypatch):
    monkeypatch.setenv("MOONSHOT_KIMI_MODEL", "kimi-k2.6")
    monkeypatch.setenv("MOONSHOT_KIMI_THINKING", "enabled")

    body = provider._build_body("hello")

    assert body["thinking"] == {"type": "enabled"}
    assert "reasoning_effort" not in body


def test_k3_cost_uses_official_model_specific_prices():
    usage = {"prompt": 1_000_000, "cached": 250_000, "completion": 100_000}

    cost = provider._estimated_cost(usage, "kimi-k3")

    assert cost == 3.825


def test_unknown_model_cost_is_not_guessed():
    usage = {"prompt": 100, "cached": 0, "completion": 10}

    assert provider._estimated_cost(usage, "future-kimi") is None
