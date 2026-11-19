"""Reuse the actual assisted crop driver and freeze its Neon and control wires."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from benchmarks.scripts import scout119_doc_web as owner
from benchmarks.scripts import hydrogen_runtime_transport
from tools import hydrogen_detector_094_runtime as prior

PAIR_PAGES = (12, 122)
prior.MODEL = owner.NEON
prior.MODELS["candidate"] = owner.NEON
prior.URLS["candidate"] = owner.HOST + owner.NEON + ":generateContent"
prior.FIXTURE = ROOT / "output/fixtures/neon-detector-099-runtime"
prior.LAYOUT_CACHE = prior.FIXTURE / "paddle-cache"


def configure_emitter():
    original_body = prior.ember_native.body
    original_parse = prior.ember_native.parse

    def build(model, *args, **kwargs):
        body = original_body(model, *args, **kwargs)
        return owner.modern(body) if model == owner.NEON else body

    def parse(data, model, schema):
        if model == owner.NEON and data.get("modelVersion") == owner.NEON:
            return original_parse(dict(data, modelVersion=owner.HYDROGEN), owner.HYDROGEN, schema)
        return original_parse(data, model, schema)

    prior.ember_native.body = build
    prior.ember_native.parse = parse


def capture_matrix():
    configure_emitter()
    rows = []

    def collect(row):
        rows.append(row)
        return json.dumps(prior.fake_google() if row["arm"] == "control" else {}).encode()

    for pipeline, model in prior.MODELS.items():
        with prior.emitter(pipeline, collect, capture=True):
            for case in prior.CASES:
                if case["page"] not in PAIR_PAGES:
                    continue
                image = prior.crop._encode_image(str(prior.HIGHRES / (case["key"] + ".jpg")))
                hints = [entry["alt"] for entry in case["images"]]
                prior.crop._call_vlm_boxes(model, image, len(hints), hints, 0.0,
                    32768 if model == owner.NEON else 8192, None,
                    reasoning_effort="high" if model == owner.NEON else "none")
                if pipeline == "control":
                    for count in range(1, len(hints) + 1):
                        prior.crop._call_vlm_caption_boxes(prior.GEMINI, image, count, hints, 0.0, 400, None)
    return rows


def send_runtime(slot, arm, url, raw):
    body = json.loads(raw)
    if "-caption-" in slot:
        # Prefix and count are preserved; both arms share a confirmed caption
        # for identical input and count, avoiding duplicate OCR hint calls.
        slot = slot.replace("-candidate-", "-control-")
        body["generationConfig"]["maxOutputTokens"] = 8192
    row, frozen, _ = owner.body_for(slot)
    if frozen != body or url != owner.HOST + row["model"] + ":generateContent":
        raise ValueError("real assisted caller drift from frozen request")
    ledger = owner.load(owner.E / "ledger.json")["calls"]
    recorded = next((r for r in ledger if r["attempt"] == slot), None)
    if recorded is None:
        recorded = owner.send(slot)
    elif recorded.get("confidence") in {"provider-transient", "operational"}:
        recovery = slot + "-recovery"
        recorded = next((r for r in ledger if r["attempt"] == recovery), None) or owner.send(slot, recover=True)
    if recorded.get("confidence") != "eligible":
        raise ValueError(f"{slot} lacks admitted complete native response")
    response = (ROOT / recorded["response"]).read_bytes()
    if owner.digest(response) != recorded["response_sha256"]:
        raise ValueError("native response custody mismatch")
    return response


def prepare():
    prior.prepare_driver()
    registry_path = prior.FIXTURE / "registry.yaml"
    registry = yaml.safe_load(registry_path.read_text())
    registry["modules"]["crop_illustrations_guided_v1"]["entrypoint"] = str(Path(__file__).relative_to(ROOT))
    registry_path.write_text(yaml.safe_dump(registry))


def main():
    args = sys.argv[1:]
    if args == ["prepare"]:
        prepare()
    elif len(args) == 4 and args[0] == "driver" and args[1] in prior.MODELS and int(args[3]) in PAIR_PAGES:
        prior.driver(args[1], args[2], args[3])
    elif "--ocr-manifest" in args:
        configure_emitter()
        if os.environ.get("HYDROGEN_094_RUNTIME_ARM") not in prior.MODELS:
            raise ValueError("invalid assisted pipeline")
        hydrogen_runtime_transport.send_runtime = send_runtime
        prior.stage()
    else:
        raise SystemExit("expected prepare or driver <control|candidate> <run id> <page>")


if __name__ == "__main__":
    main()
