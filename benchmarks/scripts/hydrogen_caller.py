# ruff: noqa: E402
"""Explicit child-only genuine proposer transport; no production activation."""

import os
import json
import sys
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from modules.common import crop_safety as safety
from benchmarks.scripts import hydrogen_native as native

ORIGINAL = safety.build_request


def google_body(body):
    parts = body["input"][0]["content"]
    images = []
    for p in parts[1:]:
        head, data = p["image_url"].split(",", 1)
        images.append((base64.b64decode(data), head.split(":")[1].split(";")[0]))
    return native.body(
        "gemini-4-hydrogen", "", parts[0]["text"], images, safety.FORMAT["schema"]
    )


def install():
    arm = os.environ["HYDROGEN_CALLER_ARM"]
    stage = "caller-S3-" + arm

    def build(source, crop, *, live=False):
        b = ORIGINAL(source, crop, live=live)
        if arm == "candidate":
            b["model"] = "gemini-4-hydrogen"
        return b

    def parse(raw, status_code=200, *, live=False):
        if arm == "control":
            return ORIGINAL_PARSE(raw, status_code, live=live)
        if status_code != 200:
            raise ValueError("native HTTP failure")
        d = json.loads(raw)
        visible = native.parse(d, "gemini-4-hydrogen", safety.FORMAT["schema"])
        u = d["usageMetadata"]
        row = next(
            x
            for x in json.loads((native.guard.RESULTS / "ledger.json").read_text())[
                "calls"
            ]
            if x["stage"] == stage
        )
        return (
            json.loads(visible),
            {
                "model": d["modelVersion"],
                "id": d["responseId"],
                "usage": u,
                "native_provider": "Google",
            },
            row["cost_usd"],
        )

    safety.build_request = build
    safety.parse_response = parse
    safety.reservation_usd = lambda: 0.31476 if arm == "candidate" else 0.15596
    # Patch the shared HTTP call boundary, which survives runpy's fresh __main__ namespace.
    import httpx

    original_post = httpx.post

    def post(url, **kwargs):
        b = kwargs.get("json", {})
        if url != "https://api.openai.com/v1/responses":
            raise ValueError("unexpected genuine caller endpoint")
        os.environ["HYDROGEN_STAGE"] = stage
        native.guard.install()
        if arm == "candidate":
            if b.get("model") != "gemini-4-hydrogen":
                raise ValueError("wrong caller model")
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-4-hydrogen:generateContent"
            kwargs["headers"] = {"x-goog-api-key": os.environ["GEMINI_API_KEY"]}
            kwargs["json"] = google_body(b)
        return original_post(url, **kwargs)

    httpx.post = post


ORIGINAL_PARSE = safety.parse_response
