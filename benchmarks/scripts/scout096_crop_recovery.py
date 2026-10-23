"""Additive unchanged-contract continuation after independently observed route recovery."""

import json
import sys
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "benchmarks/scripts"))
import scout096_reading as s  # noqa: E402 - path is selected for this sealed eval

E = ROOT / "docs/evals/evidence/078-scout096/recovery-epoch1"
E.mkdir(exist_ok=True)
original = json.loads(
    (ROOT / "docs/evals/evidence/078-scout096/preflight.json").read_text()
)
keys = [x["key"] for x in original["crop"] if x["key"] != "Image011"]
if len(sys.argv) != 2 or sys.argv[1] not in keys:
    raise SystemExit(
        "Choose exactly one original remaining crop key; manually inspect source completeness before another case. Sealed ledger requires fresh authorized run identity."
    )
keys = [sys.argv[1]]
pre = {
    "reason": "Echo independently observed restored same Together model route after shared EngineCorewave; one further unchanged affectedcase retry then originalprogressive remainder",
    "original_Image011": "reused existing candidate/control output, no rerun",
    "keys": keys,
    "candidate": "unchanged Together reasoning.enabledtrue32768 strictcrop",
    "control": "unchanged fresh Gemini3Flashpreview16384",
    "cap": "original15 cumulative including oldknown+unknown",
    "hashes": {
        k: s.sha(json.dumps(s.render_crop(k), sort_keys=True).encode()) for k in keys
    },
}
s.save(E / "crop-recovery-preflight.json", pre)
results = []
for key in keys:
    parts = s.render_crop(key)[0]["parts"]
    image = base64.b64decode(parts[1]["inlineData"]["data"])
    mime = parts[1]["inlineData"]["mimeType"]
    for model, label in [
        ("nvidia/nemotron-3.5-super-vl", "candidate"),
        ("gemini-3-flash-preview", "control"),
    ]:
        stage = f"crop-epoch1-{key}-{label}"
        try:
            raw, d = s.google(
                model,
                "",
                parts[0]["text"],
                image,
                mime,
                schema=s.CROP_SCHEMA if label == "candidate" else None,
                stage=stage,
            )
            score = s.crop_score(raw, {"vars": {"golden_key": key}})
            row = {
                "key": key,
                "arm": label,
                "raw": raw,
                "score": score,
                "served": d["modelVersion"],
            }
        except Exception as exc:
            row = {
                "key": key,
                "arm": label,
                "error": type(exc).__name__,
                "capability": "not measured",
            }
            results.append(row)
            s.save(E / "crop-results.json", results)
            print(json.dumps(row), flush=True)
            raise
        results.append(row)
        s.save(E / "crop-results.json", results)
        print(json.dumps(row), flush=True)
    if not results[-2]["score"]["pass"]:
        print("STOP valid detector miss; source review required", flush=True)
        break
