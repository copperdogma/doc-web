"""Strict OpenAI Responses contracts for production crop vision calls."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any, Literal


ContractName = Literal["detector", "captions"]


_BOX_SCHEMA = {
    "type": "object",
    "properties": {
        "x0": {"type": "number", "minimum": 0, "maximum": 1},
        "y0": {"type": "number", "minimum": 0, "maximum": 1},
        "x1": {"type": "number", "minimum": 0, "maximum": 1},
        "y1": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "required": ["x0", "y0", "x1", "y1"],
    "additionalProperties": False,
}


DETECTOR_RESPONSE_FORMAT = {
    "type": "json_schema",
    "name": "crop_detector_regions",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "regions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "image_box": _BOX_SCHEMA,
                        "caption_box": {"anyOf": [_BOX_SCHEMA, {"type": "null"}]},
                        "image_description": {"type": "string"},
                        "contains_text": {"type": "boolean"},
                        "text_reason": {"type": ["string", "null"]},
                        "caption_text": {"type": ["string", "null"]},
                        "source_issues": {"type": ["string", "null"]},
                    },
                    "required": [
                        "image_box",
                        "caption_box",
                        "image_description",
                        "contains_text",
                        "text_reason",
                        "caption_text",
                        "source_issues",
                    ],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["regions"],
        "additionalProperties": False,
    },
}


CAPTION_RESPONSE_FORMAT = {
    "type": "json_schema",
    "name": "crop_caption_regions",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "boxes": {
                "type": "array",
                "items": _BOX_SCHEMA,
            }
        },
        "required": ["boxes"],
        "additionalProperties": False,
    },
}


@dataclass(frozen=True)
class OpenAICropVisionResult:
    """Validated crop response normalized for the existing crop parser."""

    raw_json_array: str
    usage: Any
    request_id: str
    served_model: str
    response_status: str


def uses_strict_crop_responses(model: str) -> bool:
    """Return whether this model uses the strict production crop contract."""

    return model.startswith("gpt-5.6-")


def _extract_output_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()
    for item in getattr(response, "output", None) or []:
        if getattr(item, "type", None) != "message":
            continue
        for content in getattr(item, "content", None) or []:
            if getattr(content, "type", None) == "output_text":
                text = getattr(content, "text", None)
                if isinstance(text, str) and text.strip():
                    return text.strip()
    raise RuntimeError("OpenAI crop response contained no final output text")


def _require_usage(usage: Any) -> None:
    if usage is None:
        raise RuntimeError("OpenAI crop response contained no usage evidence")
    input_tokens = getattr(usage, "input_tokens", None)
    output_tokens = getattr(usage, "output_tokens", None)
    if isinstance(usage, dict):
        input_tokens = usage.get("input_tokens")
        output_tokens = usage.get("output_tokens")
    for name, value in (
        ("input_tokens", input_tokens),
        ("output_tokens", output_tokens),
    ):
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise RuntimeError(f"OpenAI crop response has invalid {name} usage")


def _validate_box(box: Any, path: str, *, allow_zero_area: bool = False) -> None:
    if not isinstance(box, dict) or set(box) != {"x0", "y0", "x1", "y1"}:
        raise RuntimeError(f"{path} must contain exactly x0, y0, x1, y1")
    values = []
    for name in ("x0", "y0", "x1", "y1"):
        value = box[name]
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value < 0
            or value > 1
        ):
            raise RuntimeError(f"{path}.{name} must be a finite number from 0 to 1")
        values.append(float(value))
    if allow_zero_area and values == [0.0, 0.0, 0.0, 0.0]:
        return
    if values[0] >= values[2] or values[1] >= values[3]:
        raise RuntimeError(f"{path} coordinates must have x0 < x1 and y0 < y1")


def _normalize_contract(output: str, contract: ContractName) -> str:
    try:
        payload = json.loads(output)
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise RuntimeError("OpenAI crop response was not valid JSON") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("OpenAI crop response root must be an object")

    if contract == "captions":
        if set(payload) != {"boxes"} or not isinstance(payload["boxes"], list):
            raise RuntimeError(
                "OpenAI caption response must contain only a boxes array"
            )
        for index, box in enumerate(payload["boxes"]):
            _validate_box(box, f"boxes[{index}]", allow_zero_area=True)
        return json.dumps(payload["boxes"], separators=(",", ":"))

    if set(payload) != {"regions"} or not isinstance(payload["regions"], list):
        raise RuntimeError("OpenAI detector response must contain only a regions array")
    required = {
        "image_box",
        "caption_box",
        "image_description",
        "contains_text",
        "text_reason",
        "caption_text",
        "source_issues",
    }
    for index, region in enumerate(payload["regions"]):
        path = f"regions[{index}]"
        if not isinstance(region, dict) or set(region) != required:
            raise RuntimeError(f"{path} fields do not match the strict contract")
        _validate_box(region["image_box"], f"{path}.image_box")
        if region["caption_box"] is not None:
            _validate_box(region["caption_box"], f"{path}.caption_box")
        if not isinstance(region["image_description"], str):
            raise RuntimeError(f"{path}.image_description must be a string")
        if type(region["contains_text"]) is not bool:
            raise RuntimeError(f"{path}.contains_text must be a boolean")
        for name in ("text_reason", "caption_text", "source_issues"):
            if region[name] is not None and not isinstance(region[name], str):
                raise RuntimeError(f"{path}.{name} must be a string or null")
    return json.dumps(payload["regions"], separators=(",", ":"))


def call_openai_crop_vision(
    *,
    client: Any,
    model: str,
    system_prompt: str,
    user_text: str,
    image_data: str,
    max_output_tokens: int,
    contract: ContractName,
) -> OpenAICropVisionResult:
    """Call OpenAI Responses with a strict production crop contract."""

    response_format = (
        DETECTOR_RESPONSE_FORMAT if contract == "detector" else CAPTION_RESPONSE_FORMAT
    )
    response = client.responses.create(
        model=model,
        reasoning={"effort": "none"},
        max_output_tokens=max_output_tokens,
        store=False,
        text={"format": response_format},
        input=[
            {
                "role": "system",
                "content": [{"type": "input_text", "text": system_prompt}],
            },
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": user_text},
                    {"type": "input_image", "image_url": image_data, "detail": "high"},
                ],
            },
        ],
    )

    status = getattr(response, "status", None)
    served_model = getattr(response, "model", None)
    request_id = getattr(response, "id", None)
    if status != "completed":
        raise RuntimeError(f"OpenAI crop response did not complete: status={status!r}")
    if getattr(response, "incomplete_details", None) is not None:
        raise RuntimeError("OpenAI crop response included incomplete details")
    if served_model != model:
        raise RuntimeError(
            f"OpenAI crop response served {served_model!r}; expected exact {model!r}"
        )
    if not isinstance(request_id, str) or not request_id:
        raise RuntimeError("OpenAI crop response contained no request id")
    usage = getattr(response, "usage", None)
    _require_usage(usage)
    raw_json_array = _normalize_contract(_extract_output_text(response), contract)
    return OpenAICropVisionResult(
        raw_json_array=raw_json_array,
        usage=usage,
        request_id=request_id,
        served_model=served_model,
        response_status=status,
    )
