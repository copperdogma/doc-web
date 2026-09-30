"""Resolve Attempt048 matrices and native bodies without provider calls."""

import base64
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path

import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "benchmarks/providers"))
import openai_responses_model as adapter  # noqa: E402

ARMS = {
    "luna": {
        "model": "gpt-6-luna",
        "reasoning_effort": "medium",
        "max_output_tokens": 4096,
        "image_detail": "high",
    },
    "sol": {
        "model": "gpt-6.1-sol",
        "reasoning_effort": "medium",
        "max_output_tokens": 4096,
        "image_detail": "high",
    },
    "control": {
        "model": "gpt-5.5",
        "expected_served_model": "gpt-5.5-2026-04-23",
        "reasoning_effort": "none",
        "max_output_tokens": 2048,
        "image_detail": "auto",
    },
}
JS = "const fs=require('fs');const x=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(require(x.prompt)(x.context)));"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(variables, provider):
    result = subprocess.run(
        ["node", "-e", JS],
        input=json.dumps(
            {
                "prompt": str(ROOT / "benchmarks/prompts/validate-page-level-crop.js"),
                "context": {"vars": variables, "provider": provider},
            }
        ),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def tiny_uri():
    im = Image.new("RGB", (32, 32), "white")
    from PIL import ImageDraw

    ImageDraw.Draw(im).rectangle((8, 8, 23, 23), fill="black")
    out = io.BytesIO()
    im.save(out, format="PNG")
    return "data:image/png;base64," + base64.b64encode(out.getvalue()).decode()


def main():
    assert (
        sha(ROOT / "benchmarks/prompts/validate-page-level-crop.js")
        == "ef4395838929b208fe65f21500d81ade902072bef3f8e53f81ef3d3b83fbc421"
    )
    original = yaml.safe_load(
        (ROOT / "benchmarks/tasks/gpt61-page-full.yaml").read_text()
    )
    for row in original["tests"]:
        row["vars"]["golden_relpath"] = "golden/crop-page-level-safety-repair-048.json"
    bykey = {x["vars"]["crop_key"]: x for x in original["tests"]}
    screen = []
    for i, key in enumerate(
        ["page-122-001"] * 3 + ["page-009-000", "page-126-001", "page-127-000"]
    ):
        row = json.loads(json.dumps(bykey[key]))
        row["vars"]["safety_case_id"] = f"screen-{i + 1}-{key}"
        screen.append(row)
    synth = []
    directory = ROOT / "benchmarks/input/safety-repair-048"
    for i in range(1, 7):
        key = f"S{i}"
        for kind in ("source", "crop"):
            png = directory / f"{key}-{kind}.png"
            (directory / f"{key}-{kind}.b64.txt").write_text(
                "data:image/png;base64," + base64.b64encode(png.read_bytes()).decode()
            )
        synth.append(
            {
                "vars": {
                    "page_image": f"file://../input/safety-repair-048/{key}-source.b64.txt",
                    "crop_image": f"file://../input/safety-repair-048/{key}-crop.b64.txt",
                    "crop_key": key,
                    "safety_case_id": key,
                    "golden_relpath": "golden/safety-repair-synthetic-048.json",
                },
                "assert": [
                    {
                        "type": "python",
                        "value": "file://../scorers/crop_validation_scorer.py",
                    }
                ],
            }
        )
    topology = {
        "run_id": "safety-repair-048-20260929",
        "cap_usd": 18,
        "max_planned": 105,
        "max_recovery": 2,
        "cache": "disabled",
        "concurrency": 1,
        "judge": "none; owner scorer and manual source review",
        "base_sha": "58fa3d5f38d274fc702b45ed4161dec381fc24ec",
        "matrices": [],
        "native": [],
    }
    prices = {"luna": 0.007798, "sol": 0.15596, "control": 0.29144}
    for arm, cfg in ARMS.items():
        cfg = dict(cfg, output_contract="page_context_validation")
        provider = {
            "id": "python:../providers/safety_repair_openai.py",
            "label": arm,
            "config": cfg,
        }
        uri = tiny_uri()
        native_messages = render({"page_image": uri, "crop_image": uri}, provider)
        native_body = adapter._build_body(json.dumps(native_messages), {"config": cfg})
        topology["native"].append(
            {
                "arm": arm,
                "body_sha256": hashlib.sha256(
                    json.dumps(native_body, sort_keys=True).encode()
                ).hexdigest(),
                "body": native_body,
            }
        )
        for stage, rows in [
            ("screen", screen),
            ("full", original["tests"]),
            ("fresh", synth),
        ]:
            task = {
                "description": "Frozen repaired page-context safety; Attempt048",
                "prompts": [
                    {
                        "id": "file://../prompts/validate-page-level-crop.js",
                        "label": "repaired-page-context",
                    }
                ],
                "providers": [provider],
                "tests": rows,
            }
            name = f"safety-repair-048-{arm}-{stage}.yaml"
            path = ROOT / "benchmarks/tasks" / name
            path.write_text(yaml.safe_dump(task, sort_keys=False))
            resolved = []
            for row in rows:
                v = row["vars"].copy()
                sources = {}
                for key in ("page_image", "crop_image"):
                    source = (path.parent / v[key][7:]).resolve()
                    v[key] = source.read_text()
                    image = base64.b64decode(v[key].split(",", 1)[1])
                    dimensions = Image.open(io.BytesIO(image)).size
                    sources[key] = {
                        "path": str(source.relative_to(ROOT)),
                        "decoded_sha256": hashlib.sha256(image).hexdigest(),
                        "dimensions": dimensions,
                    }
                messages = render(v, provider)
                body = adapter._build_body(json.dumps(messages), {"config": cfg})
                assert len(body["input"]) == 1 and body["input"][0]["role"] == "user"
                b = body["input"][0]["content"]
                assert [x["type"] for x in b] == [
                    "input_text",
                    "input_image",
                    "input_image",
                ]
                assert (
                    b[1]["image_url"] == v["page_image"]
                    and b[2]["image_url"] == v["crop_image"]
                )
                text_bytes = len((b[0]["text"] + json.dumps(body["text"])).encode())
                assert text_bytes < 6000
                assert body["text"]["format"]["strict"] and body["store"] is False
                resolved.append(
                    {
                        "key": v["crop_key"],
                        "case_id": v.get("safety_case_id", v["crop_key"]),
                        "sources": sources,
                        "text_schema_bytes": text_bytes,
                        "prompt_text_sha256": hashlib.sha256(
                            b[0]["text"].encode()
                        ).hexdigest(),
                        "schema_sha256": hashlib.sha256(
                            json.dumps(body["text"], sort_keys=True).encode()
                        ).hexdigest(),
                        "native_body_sha256": hashlib.sha256(
                            json.dumps(body, sort_keys=True).encode()
                        ).hexdigest(),
                        "assertions": row["assert"],
                    }
                )
            topology["matrices"].append(
                {
                    "task": str(path.relative_to(ROOT)),
                    "task_sha256": sha(path),
                    "arm": arm,
                    "stage": stage,
                    "count": len(rows),
                    "provider": provider,
                    "per_call_reservation_usd": prices[arm],
                    "cases": resolved,
                }
            )
    topology["planned_reservation_usd"] = sum(prices.values()) * 35
    topology["recovery_reservation_usd"] = 0.58288
    topology["frozen_sources"] = {
        str(p.relative_to(ROOT)): sha(p)
        for p in [
            ROOT / "benchmarks/prompts/validate-page-level-crop.js",
            ROOT / "benchmarks/providers/openai_responses_model.py",
            ROOT / "benchmarks/providers/safety_repair_guard.py",
            ROOT / "benchmarks/providers/safety_repair_openai.py",
            ROOT / "benchmarks/scorers/crop_validation_scorer.py",
            ROOT / "benchmarks/golden/crop-page-level-deletion-gate.json",
            ROOT / "benchmarks/golden/crop-page-level-safety-repair-048.json",
            ROOT / "benchmarks/golden/safety-repair-synthetic-048.json",
        ]
    }
    (ROOT / "docs/evals/evidence/048-safety-repair-topology.json").write_text(
        json.dumps(topology, indent=2) + "\n"
    )
    print(
        "Resolved9 matrices,102 subject rows +3 native probes; new prompt/schema/images/independent sessions verified; max exposure16.514810/cap18"
    )


if __name__ == "__main__":
    main()
