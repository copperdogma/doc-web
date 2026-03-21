"""
Shared OpenAI vision OCR helper for the Onward genealogy seam.

This keeps the request-shaping logic in one place without claiming that the
larger HTML rescue/normalization stack is also generalized.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

try:
    from modules.common.openai_client import OpenAI
except Exception as exc:  # pragma: no cover - environment dependency
    OpenAI = None
    _OPENAI_IMPORT_ERROR = exc
else:
    _OPENAI_IMPORT_ERROR = None


def _supports_temperature(model: str) -> bool:
    return not (model or "").casefold().startswith("gpt-5")


def call_ocr(
    model: str,
    prompt: str,
    image_data: str,
    temperature: float,
    max_tokens: int,
    timeout_seconds: Optional[float],
    user_text: Optional[str] = None,
) -> Tuple[str, Optional[Any], Optional[str]]:
    if OpenAI is None:  # pragma: no cover
        raise RuntimeError("openai package required") from _OPENAI_IMPORT_ERROR
    client = OpenAI(timeout=timeout_seconds) if timeout_seconds else OpenAI()
    raw = ""
    usage = None
    request_id = None
    request_kwargs: Dict[str, Any] = {
        "model": model,
    }
    if _supports_temperature(model):
        request_kwargs["temperature"] = temperature
    user_text = (user_text or "Return only HTML.").strip()
    if hasattr(client, "responses"):
        resp = client.responses.create(
            **request_kwargs,
            max_output_tokens=max_tokens,
            input=[
                {"role": "system", "content": [{"type": "input_text", "text": prompt}]},
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": user_text},
                        {"type": "input_image", "image_url": image_data},
                    ],
                },
            ],
        )
        raw = resp.output_text or ""
        usage = getattr(resp, "usage", None)
        request_id = getattr(resp, "id", None)
    else:
        resp = client.chat.completions.create(
            **request_kwargs,
            max_completion_tokens=max_tokens,
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_text},
                        {"type": "image_url", "image_url": {"url": image_data}},
                    ],
                },
            ],
        )
        raw = resp.choices[0].message.content or ""
    return raw, usage, request_id
