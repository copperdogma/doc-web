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
