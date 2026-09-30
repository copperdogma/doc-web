"""Resolve the selected Doc Web evaluation without provider calls."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
TASKS = [
    "gpt61-detector-screen.yaml",
    "gpt61-detector-full.yaml",
    "gpt61-detector-control.yaml",
    "gpt61-page-screen.yaml",
    "gpt61-page-full.yaml",
    "gpt61-page-control-screen.yaml",
    "gpt61-page-control-full.yaml",
]
PRICES = {
    "gpt-6.1-sol": (2, 0.1, 2.5, 10),
    "gpt-6-luna": (0.1, 0.01, 0.125, 0.5),
    "gpt-5.5": (5, 0.5, 5, 30),
    "gemini-3-flash-preview": (0.5, 0.05, 0.5, 3),
    "gemini-3.7-flash": (0.75, 0.075, 0.75, 3.75),
}
JS = r"""
const fs=require('fs'),crypto=require('crypto');
const data=JSON.parse(fs.readFileSync(0,'utf8'));
const prompt=require(data.prompt);
const rendered=prompt({vars:data.vars,provider:data.provider});
const messages=typeof rendered==='string'?JSON.parse(rendered):rendered;
const hash=x=>crypto.createHash('sha256').update(typeof x==='string'?x:JSON.stringify(x)).digest('hex');
const blocks=messages.flatMap(m=>m.content||m.parts||[]);
const texts=blocks.filter(x=>x.type==='text'||x.type==='input_text'||x.text).map(x=>x.text);
const images=blocks.filter(x=>x.type==='image_url'||x.type==='input_image'||x.inlineData||x.type==='image');
if(messages.length!==1||messages[0].role!=='user'||images.length!==data.image_count)throw Error('unexpected prompt topology');
console.log(JSON.stringify({message_count:messages.length,role:messages[0].role,image_count:images.length,texts:texts.map(x=>({sha256:hash(x),chars:x.length,content:x})),image_hashes:images.map(hash),rendered_sha256:hash(messages)}));
"""


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def one_task(name: str) -> dict:
    config_path = ROOT / "benchmarks/tasks" / name
    config = yaml.safe_load(config_path.read_text())
    assert len(config["prompts"]) == 1 and len(config["providers"]) == 1
    provider = config["providers"][0]
    prompt_path = (
        config_path.parent / config["prompts"][0]["id"].removeprefix("file://")
    ).resolve()
    cases = []
    for test in config["tests"]:
        variables = {}
        paths = {}
        for key, value in test["vars"].items():
            if isinstance(value, str) and value.startswith("file://"):
                source = (config_path.parent / value[7:]).resolve()
                variables[key] = source.read_text()
                paths[key] = {
                    "path": str(source.relative_to(ROOT)),
                    "sha256": sha(source),
                    "bytes": source.stat().st_size,
                }
            else:
                variables[key] = value
        image_count = sum(
            key in variables for key in ("image", "page_image", "crop_image")
        )
        payload = {
            "prompt": str(prompt_path),
            "vars": variables,
            "provider": provider,
            "image_count": image_count,
        }
        run = subprocess.run(
            ["node", "-e", JS],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=True,
        )
        rendered = json.loads(run.stdout)
        assert rendered["message_count"] == 1 and rendered["role"] == "user"
        assert rendered["image_count"] == image_count
        assert all(t["chars"] < 24000 for t in rendered["texts"])
        for t in rendered["texts"]:
            t["content_sha256"] = t.pop("sha256")
        case = {
            "key": variables.get("golden_key", variables.get("crop_key")),
            "rendered": rendered,
            "sources": paths,
            "assertions": test["assert"],
        }
        cases.append(case)
    model = provider.get("config", {}).get("model", "gemini-3-flash-preview")
    maximum = provider.get("config", {}).get(
        "max_output_tokens", provider.get("config", {}).get("maxOutputTokens", 16384)
    )
    prices = PRICES[model]
    per_call = (
        (max(1, max(c["rendered"]["image_count"] for c in cases)) * 20000 + 6000)
        * max(prices[:3])
        + maximum * prices[3]
    ) / 1e6
    return {
        "task": name,
        "task_sha256": sha(config_path),
        "prompt_sha256": sha(prompt_path),
        "provider": provider,
        "model": model,
        "max_output_tokens": maximum,
        "case_count": len(cases),
        "case_keys": [x["key"] for x in cases],
        "per_call_reservation_usd": per_call,
        "full_reservation_usd": per_call * len(cases),
        "cases": cases,
    }


def main():
    tasks = [
        one_task(n)
        for n in [
            "thinking-safety-luna-none-screen.yaml",
            "thinking-safety-luna-medium-screen.yaml",
            "thinking-safety-luna-medium-full.yaml",
            "thinking-safety-sol-low-screen.yaml",
            "thinking-safety-sol-medium-screen.yaml",
            "thinking-safety-sol-medium-full.yaml",
            "thinking-safety-control-screen.yaml",
            "thinking-safety-control-full.yaml",
        ]
    ]
    full = sum(t["full_reservation_usd"] for t in tasks if "-full." in t["task"])
    screens = sum(t["full_reservation_usd"] for t in tasks if "-screen." in t["task"])
    qualification = 2 * (0.15596 + 0.007798)
    assert full + screens + qualification < 14
    payload = {
        "base_sha": "58fa3d5f38d274fc702b45ed4161dec381fc24ec",
        "cap_usd": 14,
        "concurrency": 1,
        "cache": "disabled; --no-cache",
        "judge": "none; deterministic owner scorer plus source inspection",
        "full_matrix_reservation_usd": full,
        "screen_reservation_usd": screens,
        "qualification_reservation_usd": qualification,
        "recovery_usd": 14 - full - screens - qualification,
        "schema_provider_sha256": sha(
            ROOT / "benchmarks/providers/openai_responses_model.py"
        ),
        "scorer_sha256": sha(ROOT / "benchmarks/scorers/crop_validation_scorer.py"),
        "golden_sha256": sha(
            ROOT / "benchmarks/golden/crop-page-level-deletion-gate.json"
        ),
        "tasks": tasks,
    }
    (ROOT / "docs/evals/evidence/047-thinking-safety-topology.json").write_text(
        json.dumps(payload, indent=2) + "\n"
    )
    print(json.dumps({k: v for k, v in payload.items() if k != "tasks"}, indent=2))
    print([(t["task"], t["case_count"]) for t in tasks])


if __name__ == "__main__":
    main()
