"""Lightweight Anthropic vision client with usage logging.

Mirrors the pattern in google_client.py — centralizes API calls and
logs token usage via log_llm_usage().
"""

from __future__ import annotations

import base64
import os
from typing import Any, Optional, Tuple

from modules.common.utils import log_llm_usage

try:
    import anthropic

    _ANTHROPIC_IMPORT_ERROR = None
except Exception as e:
    anthropic = None  # type: ignore[assignment]
    _ANTHROPIC_IMPORT_ERROR = e


def _decode_data_uri(data_uri: str) -> Tuple[bytes, str]:
    """Extract raw bytes and mime type from a data URI."""
    if data_uri.startswith("data:"):
        header, b64_data = data_uri.split(",", 1)
        mime_type = header.split(":")[1].split(";")[0]
    else:
        b64_data = data_uri
        mime_type = "image/jpeg"
    return base64.b64decode(b64_data), mime_type


class AnthropicVisionClient:
    """Stateless helper for Claude vision calls with usage logging."""

    def __init__(self, api_key: Optional[str] = None):
        if anthropic is None:
            raise RuntimeError(
                "anthropic package not installed; pip install anthropic"
            ) from _ANTHROPIC_IMPORT_ERROR
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self._api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY must be set in the environment"
            )
        self._client = anthropic.Anthropic(api_key=self._api_key)

    def generate_vision(
        self,
        model: str,
        system_prompt: str,
        user_text: str,
        image_data: str,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> Tuple[str, Optional[Any], Optional[str]]:
        """Call Claude with a vision prompt.

        Args:
            model: Claude model ID (e.g. "claude-sonnet-4-6")
            system_prompt: System instruction text
            user_text: User message text
            image_data: Base64 data URI (data:image/jpeg;base64,...)
            temperature: Sampling temperature
            max_tokens: Max output tokens

        Returns:
            (raw_text, usage_metadata, response_id)
        """
        _image_bytes, media_type = _decode_data_uri(image_data)
        # Re-encode to base64 string for the API
        b64_str = base64.b64encode(_image_bytes).decode("utf-8")

        resp = self._client.messages.create(
            model=model,
            system=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_text},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": b64_str,
                            },
                        },
                    ],
                },
            ],
        )

        # Extract text from content blocks
        raw = ""
        for block in resp.content:
            if block.type == "text":
                raw += block.text

        response_id = getattr(resp, "id", None)

        # Extract usage for logging
        usage = getattr(resp, "usage", None)
        prompt_tokens = 0
        completion_tokens = 0
        if usage:
            prompt_tokens = getattr(usage, "input_tokens", 0) or 0
            completion_tokens = getattr(usage, "output_tokens", 0) or 0

        log_llm_usage(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            provider="anthropic",
        )

        return raw, usage, response_id
