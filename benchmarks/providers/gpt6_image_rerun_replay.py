"""Caption-only recovery: replay exactly matched, already paid r2 detector."""

import hashlib
import json
import os

import httpx

import gpt6_image_rerun_guard as guard


def install():
    original = httpx.Client.send

    def send(client, request, **kwargs):
        if request.method != "POST":
            return original(client, request, **kwargs)
        body = json.loads(request.content)
        ledger_path = guard.RESULTS / "ledger.json"
        ledger = json.loads(ledger_path.read_text())
        subject_calls = [
            c for c in ledger["calls"] if str(c.get("stage", "")).endswith("page12-r2")
        ]
        subjects = []
        for call in subject_calls:
            prior = json.loads(
                (guard.RESULTS / f"request-{call['sequence']:03d}.json").read_text()
            )
            limit = prior.get(
                "max_output_tokens",
                prior.get("generationConfig", {}).get("maxOutputTokens"),
            )
            if limit == 8192:
                subjects.append((call, prior))
        is_detector = (
            body.get("text", {}).get("format", {}).get("name")
            == "crop_detector_regions"
        )
        is_detector |= any(
            "generationConfig" in prior
            and body.get("systemInstruction") == prior.get("systemInstruction")
            for _, prior in subjects
        )
        if not is_detector:
            return original(client, request, **kwargs)
        digest = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        matches = [
            call
            for call, _ in subjects
            if call["request_sha256"] == digest and call.get("cost_usd") is not None
        ]
        if len(matches) != 1:
            raise RuntimeError(
                "Caption recovery detector payload changed; duplicate paid subject blocked"
            )
        call = matches[0]
        raw = (guard.RESULTS / f"response-{call['sequence']:03d}.json").read_bytes()
        if hashlib.sha256(raw).hexdigest() != call["response_sha256"]:
            raise RuntimeError("Frozen detector envelope hash mismatch")
        ledger.setdefault("replays", []).append(
            {
                "stage": os.environ.get("GPT6_IMAGE_STAGE"),
                "source_call": call["sequence"],
                "request_sha256": digest,
                "response_sha256": call["response_sha256"],
                "fresh_inference": False,
                "incremental_cost_usd": 0,
            }
        )
        guard.write(ledger_path, ledger)
        return httpx.Response(
            call["status_code"],
            content=raw,
            request=request,
            headers={"content-type": "application/json"},
        )

    httpx.Client.send = send
