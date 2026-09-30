"""Pinned Sol page-safety native contract. No network or credentials on import."""

import base64
import copy
import json
from pathlib import Path

from PIL import Image

from modules.common.crop_review import digest, require

ROOT = Path(__file__).resolve().parents[2]
PROMPT_PATH = ROOT / "modules/transform/propose_crop_safety_v1/prompt.txt"
PROMPT_SHA = "9931ded6b7e732687b0889e6959ef9a873e6f459a292c132443db0f6bc9a7371"
MEASURED_JS_SHA = "ef4395838929b208fe65f21500d81ade902072bef3f8e53f81ef3d3b83fbc421"
MODEL = "gpt-6.1-sol"
RESERVE_USD = 0.155960
FORMAT = {
    "type": "json_schema",
    "name": "page_context_validation",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": ["pass", "fail"]},
            "has_page_text": {"type": "boolean"},
            "excessive_blank": {"type": "boolean"},
            "reason": {"type": "string"},
        },
        "required": ["verdict", "has_page_text", "excessive_blank", "reason"],
        "additionalProperties": False,
    },
}


def image_uri(path):
    with Image.open(path) as image:
        require(image.format in ("PNG", "JPEG"), "Only native PNG/JPEG are supported")
        require(
            image.width <= 2048 and image.height <= 2048,
            "Image exceeds frozen pilot input bound; no implicit resize",
        )
        mime = "image/png" if image.format == "PNG" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(Path(path).read_bytes()).decode()


def build_request(source, crop, *, live=False):
    require(digest(PROMPT_PATH) == PROMPT_SHA, "Measured safety prompt changed")
    text = PROMPT_PATH.read_text()
    require("${" not in text, "Unsupported prompt interpolation")
    body = {
        "model": MODEL,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": text},
                    {
                        "type": "input_image",
                        "image_url": image_uri(source),
                        "detail": "high",
                    },
                    {
                        "type": "input_image",
                        "image_url": image_uri(crop),
                        "detail": "high",
                    },
                ],
            }
        ],
        "reasoning": {"effort": "medium"},
        "max_output_tokens": 4096,
        "store": False,
        "text": {"format": copy.deepcopy(FORMAT)},
    }
    require(
        len((text + json.dumps(body["text"])).encode()) <= 6000,
        "Text/schema input bound exceeded",
    )
    if live:
        # Disclosed operational difference: paid runtime pins Standard/default
        # instead of inheriting an account's auto tier as the benchmark did.
        body["service_tier"] = "default"
    return body


def parse_response(raw, status_code=200, *, live=False):
    require(status_code == 200, "Native HTTP failure")
    data = json.loads(raw)
    require(isinstance(data, dict), "Native envelope must be an object")
    require(
        isinstance(data.get("id"), str) and data["id"].startswith("resp_"),
        "Missing native response identity",
    )
    require(data.get("model") == MODEL, "Unexpected served model identity")
    require(
        data.get("status") == "completed"
        and data.get("error") is None
        and data.get("incomplete_details") is None,
        "Native response not complete",
    )
    if live:
        require(data.get("service_tier") == "default", "Unexpected served pricing tier")
    output = data.get("output")
    require(
        isinstance(output, list)
        and all(
            isinstance(x, dict) and x.get("type") in ("reasoning", "message")
            for x in output
        ),
        "Missing or malformed native output",
    )
    messages = [x for x in output if x.get("type") == "message"]
    require(
        len(messages) == 1
        and messages[0].get("role") == "assistant"
        and messages[0].get("status") == "completed",
        "Invalid native assistant terminal message",
    )
    content = messages[0].get("content")
    require(
        isinstance(content, list)
        and len(content) == 1
        and isinstance(content[0], dict)
        and content[0].get("type") == "output_text",
        "Refusal or non-text native output",
    )
    require(isinstance(content[0].get("text"), str), "Native output text missing")
    payload = json.loads(content[0]["text"])
    require(
        isinstance(payload, dict)
        and set(payload) == {"verdict", "has_page_text", "excessive_blank", "reason"},
        "Strict page-safety fields mismatch",
    )
    require(
        payload["verdict"] in ("pass", "fail")
        and type(payload["has_page_text"]) is bool
        and type(payload["excessive_blank"]) is bool
        and isinstance(payload["reason"], str)
        and payload["reason"].strip(),
        "Invalid page-safety field values",
    )
    usage = data.get("usage")
    require(
        isinstance(usage, dict)
        and all(
            type(usage.get(k)) is int and usage[k] >= 0
            for k in ("input_tokens", "output_tokens", "total_tokens")
        ),
        "Native usage unavailable",
    )
    require(
        usage["input_tokens"] + usage["output_tokens"] == usage["total_tokens"]
        and usage["input_tokens"] <= 46000
        and usage["output_tokens"] <= 4096,
        "Native usage outside reservation contract",
    )
    require(
        isinstance(usage.get("input_tokens_details", {}), dict)
        and isinstance(usage.get("output_tokens_details", {}), dict),
        "Malformed native usage details",
    )
    cached = usage.get("input_tokens_details", {}).get("cached_tokens", 0)
    reasoning = usage.get("output_tokens_details", {}).get("reasoning_tokens", 0)
    require(
        type(cached) is int
        and 0 <= cached <= usage["input_tokens"]
        and type(reasoning) is int
        and 0 <= reasoning <= usage["output_tokens"],
        "Invalid detailed usage",
    )
    cost = (
        (usage["input_tokens"] - cached) * 2.5
        + cached * 0.1
        + usage["output_tokens"] * 10
    ) / 1e6
    return payload, data, cost


def validate_native_proposal(root, proposal, row, manifest):
    """Recheck exact native receipts at release/build; verdict is only a proposal."""
    from modules.common.crop_review import custody_path, read_bound

    expected_origin = {
        "live": "native_crop_safety",
        "replay": "replayed_crop_safety",
        "mock": "mock_crop_safety",
    }
    mode = proposal.get("mode")
    require(
        mode in expected_origin and proposal.get("origin") == expected_origin[mode],
        "Native proposal mode/origin mismatch",
    )
    require(proposal.get("status") == "completed", "Native proposal unavailable")
    request = read_bound(root, proposal["request"])
    response = read_bound(root, proposal["receipt"])
    body = json.loads(request.read_bytes())
    expected = build_request(
        custody_path(root, row["source_image"]),
        Path(manifest).parent / "images" / row["filename"],
        live=mode == "live",
    )
    require(
        body == expected and proposal.get("prompt_sha256") == PROMPT_SHA,
        "Native request is not the frozen source/crop contract",
    )
    answer, data, _ = parse_response(
        response.read_bytes(), proposal["status_code"], live=mode == "live"
    )
    require(
        proposal.get("answer") == answer
        and proposal.get("verdict") == answer["verdict"]
        and proposal.get("served_model") == data["model"]
        and proposal.get("response_id") == data["id"]
        and proposal.get("usage") == data["usage"],
        "Native proposal does not match raw receipt",
    )
