# ruff: noqa: E402
"""Network-denied actual SDK replay for opt-in native Hydrogen consumer recipes."""

import os
import json
import socket
import hashlib
import sys
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def install():
    fixture = os.environ["HYDROGEN_OCR_REPLAY_FIXTURE"]
    from modules.common import google_client
    import httpx
    from google import genai
    from google.genai import types

    ledger = json.loads(
        (ROOT / "benchmarks/results/hydrogen-20261115/ledger.json").read_text()
    )
    row = next(x for x in ledger["calls"] if x["stage"] == f"ocr-{fixture}-candidate")
    expected = json.loads((ROOT / row["request"]).read_text())
    raw = (ROOT / row["response"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == row["response_sha256"]
    seen = []

    def handler(request):
        assert request.url.host == "generativelanguage.googleapis.com"
        assert request.url.path.endswith("/models/gemini-4-hydrogen:generateContent")
        body = json.loads(request.content)
        explicit_mime = body["generationConfig"].pop("responseMimeType")
        (
            ROOT
            / f"benchmarks/results/hydrogen-20261115/ocr-replay-{fixture}-actual-body.json"
        ).write_text(json.dumps(body))
        role = body["systemInstruction"].pop("role", None)
        assert role in (None, "user", "system")
        a = body["contents"][0]["parts"][1]["inlineData"]
        e = expected["contents"][0]["parts"][1]["inlineData"]
        assert base64.b64decode(a["data"], altchars=b"-_") == base64.b64decode(
            e["data"]
        )
        a["data"] = e["data"]
        assert explicit_mime == "text/plain" and body == expected
        seen.append(1)
        assert len(seen) == 1
        p = (
            ROOT
            / f"docs/evals/evidence/094-hydrogen/consumer-ocr-{fixture}-replay.json"
        )
        p.write_text(
            json.dumps(
                {
                    "network_denied": True,
                    "actual_sdk": True,
                    "exact_native_model": "gemini-4-hydrogen",
                    "original_prompt_image_and_controls_equal": True,
                    "sdk_serialization_differences": [
                        "explicit text/plain",
                        "systemInstruction role " + str(role),
                        "equivalent URL-safe image base64",
                    ],
                    "original_response_sha256": row["response_sha256"],
                    "provider_calls": 0,
                    "sdk_mock_requests": len(seen),
                },
                indent=2,
            )
            + "\n"
        )
        return httpx.Response(
            200, content=raw, headers={"content-type": "application/json"}
        )

    original = genai.Client

    def factory(**kwargs):
        return original(
            api_key="offline-no-credentials",
            http_options=types.HttpOptions(
                api_version="v1beta",
                httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        )

    google_client.genai.Client = factory

    def deny(*a, **k):
        raise RuntimeError("network forbidden in native OCR consumer replay")

    socket.create_connection = deny
    socket.socket.connect = deny
    socket.socket.connect_ex = deny
