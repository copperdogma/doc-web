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
    tasks = [one_task(x) for x in TASKS]
    assert [x["case_count"] for x in tasks] == [1, 13, 13, 1, 22, 1, 22]
    assert tasks[0]["case_keys"] == ["Image011"]
    assert tasks[3]["case_keys"] == ["page-122-001"]
    assert tasks[1]["case_keys"] == tasks[2]["case_keys"]
    assert tasks[4]["case_keys"] == tasks[6]["case_keys"]
    # Screen calls are calibration; the full sets are separately fresh.
    full = sum(tasks[i]["full_reservation_usd"] for i in (1, 2, 4, 6))
    ocr = 2 * ((26000 * 2.5 + 16384 * 10) / 1e6 + (26000 * 0.75 + 16384 * 3.75) / 1e6)
    qualification = 4 * ((26000 * 2.5 + 4096 * 10) / 1e6)
    assert full + ocr + qualification < 14
    import sys

    sys.path.insert(0, str(ROOT))
    from modules.extract.ocr_ai_gpt51_v1.main import build_system_prompt

    ocr_inputs = []
    user_text = 'Return HTML only. FIRST line MUST be: <meta name="ocr-metadata" data-ocr-quality="0.0-1.0" data-ocr-integrity="0.0-1.0" data-continuation-risk="0.0-1.0">'
    for model in ("gpt-6.1-sol", "gemini-3.7-flash"):
        for fixture in ("barney", "alverson"):
            recipe = ROOT / f"configs/recipes/gpt61-ocr-{model}-{fixture}.yaml"
            parsed = yaml.safe_load(recipe.read_text())
            params = parsed["stages"][1]["params"]
            system = build_system_prompt(params["ocr_hints"])
            image = (
                ROOT / f"testdata/handwritten-notes-{fixture}-real-images/page-001.jpg"
            )
            assert image.stat().st_size > 0 and params["max_output_tokens"] == 16384
            ocr_inputs.append(
                {
                    "model": model,
                    "fixture": fixture,
                    "recipe": str(recipe.relative_to(ROOT)),
                    "recipe_sha256": sha(recipe),
                    "image": str(image.relative_to(ROOT)),
                    "image_sha256": sha(image),
                    "image_bytes": image.stat().st_size,
                    "system_prompt_sha256": hashlib.sha256(system.encode()).hexdigest(),
                    "system_prompt_chars": len(system),
                    "user_prompt_sha256": hashlib.sha256(
                        user_text.encode()
                    ).hexdigest(),
                    "user_prompt_chars": len(user_text),
                    "image_count": 1,
                    "request_roles": ["system", "user"],
                    "max_output_tokens": 16384,
                    "input_bound_tokens": 26000,
                    "reasoning": (
                        "low" if model == "gpt-6.1-sol" else "maintained default medium"
                    ),
                    "schema": "freeform HTML; owner sanitizer and page_html_v1 scorer",
                }
            )
    payload = {
        "base_sha": "5ca3711fb13b12b5b3e261438e7a00ffe450a647",
        "cap_usd": 14,
        "concurrency": 1,
        "cache": "disabled",
        "judge": "none; deterministic Python assertions",
        "full_matrix_reservation_usd": full + ocr,
        "qualification_reserve_usd": qualification,
        "remaining_after_full_and_qualification_usd": 14 - full - ocr - qualification,
        "ocr_cases": ocr_inputs,
        "tasks": tasks,
    }
    out = ROOT / "docs/evals/evidence/046-gpt61-topology.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(
        json.dumps(
            {k: v for k, v in payload.items() if k != "tasks" and k != "ocr_cases"},
            indent=2,
        )
    )
    print("task counts:", [(x["task"], x["case_count"]) for x in tasks])


if __name__ == "__main__":
    main()
