"""Lightweight Google Gemini vision client with usage logging.

Mirrors the pattern in openai_client.py — centralizes API calls and
logs token usage via log_llm_usage().
"""

from __future__ import annotations

import base64
from typing import Any, Mapping, Optional, Tuple

from doc_web.env import build_doc_web_env, get_doc_web_api_key
from modules.common.utils import log_llm_usage

try:
    from google import genai
    from google.genai import types

    _GENAI_IMPORT_ERROR = None
except Exception as e:
    genai = None  # type: ignore[assignment]
    types = None  # type: ignore[assignment]
    _GENAI_IMPORT_ERROR = e


GEMINI_API_VERSION_ENV = "DOC_WEB_GEMINI_API_VERSION"
DEFAULT_GEMINI_API_VERSION = "v1beta"
SUPPORTED_GEMINI_API_VERSIONS = {"v1", "v1beta"}


def get_doc_web_gemini_api_version(env: Mapping[str, str] | None = None) -> str:
    """Return the explicit Gemini API version for official google-genai clients."""
    api_version = (
        build_doc_web_env(env=env).get(GEMINI_API_VERSION_ENV)
        or DEFAULT_GEMINI_API_VERSION
    ).strip()
    if api_version not in SUPPORTED_GEMINI_API_VERSIONS:
        raise ValueError(
            f"{GEMINI_API_VERSION_ENV} must be one of "
            f"{sorted(SUPPORTED_GEMINI_API_VERSIONS)}"
        )
    return api_version


def get_gemini_client_http_options(
    env: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Return google-genai client http_options with an explicit API version."""
    return {"api_version": get_doc_web_gemini_api_version(env=env)}


def _decode_data_uri(data_uri: str) -> Tuple[bytes, str]:
    """Extract raw bytes and mime type from a data URI."""
    if data_uri.startswith("data:"):
        header, b64_data = data_uri.split(",", 1)
        mime_type = header.split(":")[1].split(";")[0]
    else:
        b64_data = data_uri
        mime_type = "image/jpeg"
    return base64.b64decode(b64_data), mime_type


class GeminiVisionClient:
    """Stateless helper for Gemini vision calls with usage logging."""

    def __init__(self, api_key: Optional[str] = None):
        if genai is None:
            raise RuntimeError(
                "google-genai package not installed; pip install google-genai"
            ) from _GENAI_IMPORT_ERROR
        self._api_key = api_key or get_doc_web_api_key("gemini")
        if not self._api_key:
            raise RuntimeError(
                "DOC_WEB_GEMINI_API_KEY must be set in the environment"
            )
        self._client = genai.Client(
            api_key=self._api_key,
            http_options=get_gemini_client_http_options(),
        )

    def generate_vision(
        self,
        model: str,
        system_prompt: str,
        user_text: str,
        image_data: str,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> Tuple[str, Optional[Any], Optional[str]]:
        """Call Gemini with a vision prompt.

        Args:
            model: Gemini model ID (e.g. "gemini-3-pro-preview")
            system_prompt: System instruction text
            user_text: User message text
            image_data: Base64 data URI (data:image/jpeg;base64,...)
            temperature: Sampling temperature
            max_tokens: Max output tokens

        Returns:
            (raw_text, usage_metadata, response_id)
        """
        image_bytes, mime_type = _decode_data_uri(image_data)
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

        resp = self._client.models.generate_content(
            model=model,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=user_text),
                        image_part,
                    ],
                ),
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                max_output_tokens=max_tokens,
                response_mime_type="text/plain",
            ),
        )

        raw = resp.text or ""
        response_id = getattr(resp, "response_id", None)

        # Extract usage for logging
        usage_meta = getattr(resp, "usage_metadata", None)
        prompt_tokens = 0
        completion_tokens = 0
        if usage_meta:
            prompt_tokens = getattr(usage_meta, "prompt_token_count", 0) or 0
            completion_tokens = getattr(usage_meta, "candidates_token_count", 0) or 0

        log_llm_usage(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            provider="google",
        )

        return raw, usage_meta, response_id
