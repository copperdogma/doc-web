from types import SimpleNamespace

import pytest

from modules.common import google_client


def test_gemini_client_defaults_to_explicit_v1beta(monkeypatch):
    calls = []

    def fake_client(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace()

    monkeypatch.setenv("DOC_WEB_GEMINI_API_KEY", "gemini-key")
    monkeypatch.delenv(google_client.GEMINI_API_VERSION_ENV, raising=False)
    monkeypatch.setattr(
        google_client,
        "genai",
        SimpleNamespace(Client=fake_client),
    )
    monkeypatch.setattr(google_client, "_GENAI_IMPORT_ERROR", None)

    google_client.GeminiVisionClient()

    assert calls == [
        {
            "api_key": "gemini-key",
            "http_options": {"api_version": "v1beta"},
        }
    ]


def test_gemini_client_honors_api_version_override(monkeypatch):
    calls = []

    def fake_client(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace()

    monkeypatch.setenv("DOC_WEB_GEMINI_API_KEY", "gemini-key")
    monkeypatch.setenv(google_client.GEMINI_API_VERSION_ENV, "v1")
    monkeypatch.setattr(
        google_client,
        "genai",
        SimpleNamespace(Client=fake_client),
    )
    monkeypatch.setattr(google_client, "_GENAI_IMPORT_ERROR", None)

    google_client.GeminiVisionClient()

    assert calls[0]["http_options"] == {"api_version": "v1"}


def test_gemini_api_version_rejects_unknown_value():
    with pytest.raises(ValueError, match="DOC_WEB_GEMINI_API_VERSION"):
        google_client.get_doc_web_gemini_api_version(
            env={google_client.GEMINI_API_VERSION_ENV: "v2"}
        )


@pytest.mark.parametrize("finish_reason", ["STOP", "MAX_TOKENS"])
def test_gemini_crop_response_retains_raw_and_rejects_truncation(
    monkeypatch, tmp_path, finish_reason
):
    response = SimpleNamespace(
        text="[]",
        response_id="gemini-response-1",
        model_version="gemini-3-flash-preview",
        usage_metadata=SimpleNamespace(prompt_token_count=100, candidates_token_count=2),
        candidates=[SimpleNamespace(finish_reason=SimpleNamespace(value=finish_reason))],
        model_dump_json=lambda: '{"response_id":"gemini-response-1"}',
    )
    calls = []
    models = SimpleNamespace(generate_content=lambda **kwargs: calls.append(kwargs) or response)
    monkeypatch.setattr(
        google_client,
        "genai",
        SimpleNamespace(Client=lambda **kwargs: SimpleNamespace(models=models)),
    )
    # Keep this offline contract independent of an ambient optional SDK. The
    # client and its request types are one test-double boundary.
    monkeypatch.setattr(
        google_client,
        "types",
        SimpleNamespace(
            Part=SimpleNamespace(
                from_bytes=lambda **kwargs: SimpleNamespace(**kwargs),
                from_text=lambda **kwargs: SimpleNamespace(**kwargs),
            ),
            Content=lambda **kwargs: SimpleNamespace(**kwargs),
            GenerateContentConfig=lambda **kwargs: SimpleNamespace(**kwargs),
        ),
    )
    monkeypatch.setattr(google_client, "log_llm_usage", lambda **kwargs: None)
    monkeypatch.setenv("GEMINI_CROP_RAW_ENVELOPE_DIR", str(tmp_path))

    client = google_client.GeminiVisionClient(api_key="dummy")
    def call():
        return client.generate_vision(
            "gemini-3-flash-preview",
            "detect",
            "one box",
            "data:image/jpeg;base64,YWJj",
            max_tokens=2048,
        )
    if finish_reason == "MAX_TOKENS":
        with pytest.raises(RuntimeError, match="did not finish normally"):
            call()
    else:
        assert call()[2] == "gemini-response-1"
    assert calls[0]["contents"][0].parts[1].data == b"abc"
    assert calls[0]["contents"][0].parts[1].mime_type == "image/jpeg"
    assert len(list(tmp_path.glob("*.json"))) == 1
