# ruff: noqa: E402
import os
import json
import httpx
import hashlib
from benchmarks.scripts import hydrogen_native as native


def send_runtime(slot, arm, url, raw):
    if "-caption-" in slot:
        slot += "-adequate8192"
        b = json.loads(raw)
        b["generationConfig"]["maxOutputTokens"] = 8192
        raw = json.dumps(b, separators=(",", ":"), ensure_ascii=False).encode()
    ledger = json.loads((native.guard.RESULTS / "ledger.json").read_text())
    prior = next((r for r in ledger["calls"] if r["stage"] == slot), None)
    if prior:
        request = native.ROOT / prior["request"]
        response = native.ROOT / prior["response"]
        assert prior["status_code"] == 200 and prior.get("cost_usd") is not None
        assert json.loads(request.read_bytes()) == json.loads(raw)
        assert (
            hashlib.sha256(response.read_bytes()).hexdigest()
            == prior["response_sha256"]
        )
        return (
            response.read_bytes()
        )  # Reuse exact subject for caller/cleanup recovery, never retry semantics.
    os.environ["HYDROGEN_STAGE"] = slot
    native.guard.install()
    r = httpx.post(
        url,
        headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
        content=raw,
        timeout=900,
    )
    r.raise_for_status()
    d = r.json()
    model = "gemini-4-hydrogen" if arm == "candidate" else "gemini-3-flash-preview"
    native.parse(
        d, model, json.loads(raw).get("generationConfig", {}).get("responseJsonSchema")
    )
    return r.content
