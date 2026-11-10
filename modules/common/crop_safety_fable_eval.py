"""Default-off native Fable contract for the bounded Scout107 evaluation only.

An external subprocess opt-in is required at every proposal/release/build read.
A proposal's own contract tag never authorizes its interpretation.
"""

import copy
import json
import os
from pathlib import Path

from modules.common.crop_review import require

ENV = "DOC_WEB_CROP_SAFETY_EVAL_CONTRACT"
CONTRACT = "fable52-safety-qualification-v1"
MODEL = "claude-fable-5-2"
RESERVE_USD = 2.04672
DISPATCH_LEDGER = (
    Path(__file__).resolve().parents[2]
    / "docs/evals/evidence/088-fable52-safety/ledger.json"
)


def active_contract():
    value = os.environ[ENV] if ENV in os.environ else None
    require(value in (None, "", CONTRACT), "Unknown crop safety evaluation contract")
    return CONTRACT if value == CONTRACT else None


def build_request(source, crop, image_uri, prompt, schema):
    require(active_contract() == CONTRACT, "Fable evaluation requires external opt-in")
    content = [{"type": "text", "text": prompt}]
    for path in (source, crop):
        # Reuse the existing PNG/JPEG and <=2048/native-byte admission function.
        uri = image_uri(path)
        header, data = uri.split(",", 1)
        content.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": header.split(":", 1)[1].split(";", 1)[0],
                    "data": data,
                },
            }
        )
    body = {
        "model": MODEL,
        "service_tier": "standard_only",
        "max_tokens": 32768,
        "output_config": {
            "effort": "xhigh",
            "format": {"type": "json_schema", "schema": copy.deepcopy(schema)},
        },
        "messages": [{"role": "user", "content": content}],
    }
    require(
        len((prompt + json.dumps(body["output_config"]["format"])).encode()) <= 6000,
        "Text/schema input bound exceeded",
    )
    return body


def parse_response(raw, status_code=200, *, live=False):
    require(active_contract() == CONTRACT, "Fable evaluation requires external opt-in")
    require(status_code == 200, "Native HTTP failure")
    data = json.loads(raw)
    require(isinstance(data, dict), "Native envelope must be an object")
    require(
        isinstance(data.get("id"), str) and data["id"].startswith("msg_"),
        "Missing native Anthropic response identity",
    )
    require(data.get("model") == MODEL, "Unexpected served model identity")
    require(
        data.get("type") == "message"
        and data.get("role") == "assistant"
        and data.get("stop_reason") == "end_turn"
        and not data.get("error"),
        "Native Anthropic response not complete",
    )
    if live:
        usage = data.get("usage")
        require(isinstance(usage, dict), "Native usage unavailable")
        require(
            usage.get("service_tier") == "standard"
            and usage.get("speed") == "standard",
            "Unexpected served pricing tier",
        )
    content = data.get("content")
    require(
        isinstance(content, list)
        and all(
            isinstance(x, dict)
            and x.get("type") in ("text", "thinking", "redacted_thinking")
            for x in content
        ),
        "Refusal or non-text native output",
    )
    texts = [x.get("text") for x in content if x["type"] == "text"]
    require(len(texts) == 1 and isinstance(texts[0], str), "Native output text missing")
    payload = json.loads(texts[0])
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
        and bool(payload["reason"].strip()),
        "Invalid page-safety field values",
    )
    usage = data.get("usage")
    require(isinstance(usage, dict), "Native usage unavailable")
    for key in ("input_tokens", "output_tokens"):
        require(
            type(usage.get(key)) is int and usage[key] >= 0, "Native usage unavailable"
        )
    cached = usage.get("cache_read_input_tokens", 0)
    written = usage.get("cache_creation_input_tokens", 0)
    require(
        type(cached) is int and cached >= 0 and type(written) is int and written >= 0,
        "Invalid detailed usage",
    )
    require(
        usage["input_tokens"] + cached + written <= 46000
        and usage["output_tokens"] <= 32768,
        "Native usage outside reservation contract",
    )
    details = usage.get("output_tokens_details", {})
    require(isinstance(details, dict), "Malformed native usage details")
    thinking = details.get("thinking_tokens", 0)
    require(
        type(thinking) is int and 0 <= thinking <= usage["output_tokens"],
        "Invalid detailed usage",
    )
    # This local custody ledger deliberately settles an upper bound. The parent
    # combined campaign ledger independently records exact native rate accounting.
    cost_upper = (
        (usage["input_tokens"] + written) * 16
        + cached * 0.2
        + usage["output_tokens"] * 40
    ) / 1e6
    return payload, data, cost_upper


def qualification_send(body):
    """Fixed, opt-in combined-wallet transport for the two frozen caller pairs."""
    import base64
    import hashlib
    from pathlib import Path

    require(
        os.environ.get("DOC_WEB_SAFETY_QUAL_088_TRANSPORT") == "1",
        "Explicit qualification transport required",
    )
    from modules.common.crop_safety import (
        qualification_anchor_required,
        qualification_context,
    )

    require(
        qualification_anchor_required() and qualification_context(),
        "Explicit anchored qualification context required",
    )
    root = Path(__file__).resolve().parents[2]
    if body.get("model") == MODEL:
        require(
            active_contract() == CONTRACT, "Fable evaluation requires external opt-in"
        )
        arm = "fable"
        images = [
            base64.b64decode(x["source"]["data"], validate=True)
            for x in body["messages"][0]["content"]
            if x["type"] == "image"
        ]
    else:
        require(
            body.get("model") == "gpt-6.1-sol" and not active_contract(),
            "Unexpected qualification arm",
        )
        arm = "sol"
        images = [
            base64.b64decode(x["image_url"].split(",", 1)[1], validate=True)
            for x in body["input"][0]["content"]
            if x["type"] == "input_image"
        ]
    hashes = [hashlib.sha256(x).hexdigest() for x in images]
    source = root / "tests/fixtures/crop_review_offline/approved"
    matches = [
        case
        for case in ("S3", "S4")
        if hashes
        == [
            hashlib.sha256((source / (case + "-source.png")).read_bytes()).hexdigest(),
            hashlib.sha256(
                (source / "images" / (case + ".png")).read_bytes()
            ).hexdigest(),
        ]
    ]
    require(
        len(matches) == 1, "Qualification caller source/crop pair is not frozen S3/S4"
    )
    from benchmarks.scripts.safety_qual_088 import send_native

    return send_native(body, arm, "caller:" + arm + ":" + matches[0])


def validate_dispatch_anchor(body, response_bytes):
    """Bind a native caller receipt to the separate combined campaign dispatch.

    No proposal, operator approval, or recomputed local hashes may manufacture
    this record. The path is fixed; no environment-selectable trust store exists.
    """
    import base64
    import hashlib
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    ledger_path = DISPATCH_LEDGER
    require(
        ledger_path.is_file() and not ledger_path.is_symlink(),
        "Independent combined dispatch ledger unavailable",
    )
    ledger = json.loads(ledger_path.read_text())
    require(
        ledger.get("id") == "088-fable52-safety-20261109",
        "Unexpected combined dispatch identity",
    )
    arm = "fable" if body.get("model") == MODEL else "sol"
    require(
        body.get("model") in (MODEL, "gpt-6.1-sol"),
        "Unknown qualification receipt model",
    )
    if arm == "fable":
        images = [
            base64.b64decode(x["source"]["data"], validate=True)
            for x in body["messages"][0]["content"]
            if x["type"] == "image"
        ]
    else:
        images = [
            base64.b64decode(x["image_url"].split(",", 1)[1], validate=True)
            for x in body["input"][0]["content"]
            if x["type"] == "input_image"
        ]
    hashes = [hashlib.sha256(x).hexdigest() for x in images]
    source = root / "tests/fixtures/crop_review_offline/approved"
    cases = [
        case
        for case in ("S3", "S4")
        if hashes
        == [
            hashlib.sha256((source / (case + "-source.png")).read_bytes()).hexdigest(),
            hashlib.sha256(
                (source / "images" / (case + ".png")).read_bytes()
            ).hexdigest(),
        ]
    ]
    require(len(cases) == 1, "Receipt does not bind a frozen caller source/crop")
    stage = "caller:" + arm + ":" + cases[0]
    response_sha = hashlib.sha256(response_bytes).hexdigest()
    matches = [
        c
        for c in ledger["calls"]
        if c.get("stage") == stage
        and c.get("arm") == arm
        and c.get("model") == body["model"]
        and c.get("semantic_eligible") is True
        and c.get("response_sha256") == response_sha
    ]
    require(
        len(matches) == 1,
        "Native receipt is not anchored to an eligible combined dispatch",
    )
    record = matches[0]
    for kind in ("request", "response"):
        path = root / record[kind]
        require(
            path.is_file()
            and not path.is_symlink()
            and path.resolve().is_relative_to(ledger_path.parent / "raw"),
            "Unsafe combined dispatch receipt path",
        )
        require(
            hashlib.sha256(path.read_bytes()).hexdigest() == record[kind + "_sha256"],
            "Combined dispatch receipt hash mismatch",
        )
        if kind == "request":
            require(
                json.loads(path.read_bytes()) == body,
                "Caller request differs from genuine combined dispatch",
            )
        else:
            require(
                path.read_bytes() == response_bytes,
                "Caller response differs from genuine combined dispatch",
            )
