"""Maintained Attempt063 image helpers, ported for Scout091; no provider dispatch."""

from __future__ import annotations
import importlib.util
import json
import re
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


owner = load_module(
    "scout091_responses", ROOT / "benchmarks/providers/openai_responses_model.py"
)


def image_cases():
    task = yaml.safe_load(
        (
            ROOT / "benchmarks/tasks/safety-repair-048-control-full-continuation1.yaml"
        ).read_text()
    )
    return {x["vars"]["crop_key"]: x["vars"] for x in task["tests"]}


def image_body(key, arm):
    v = image_cases()[key]
    prompt_file = ROOT / "benchmarks/prompts/validate-page-level-crop.js"
    prompt = re.search(
        r"const PROMPT_TEXT = `(.*?)`;", prompt_file.read_text(), re.S
    ).group(1)
    parts = [{"type": "input_text", "text": prompt}]
    for k in ("page_image", "crop_image"):
        p = (ROOT / "benchmarks/tasks" / v[k].removeprefix("file://")).resolve()
        parts.append({"type": "input_image", "image_url": p.read_text().strip()})
    messages = [{"role": "user", "content": parts}]
    return owner._build_body(
        json.dumps(messages),
        {
            "config": {
                "model": "gpt-5.5",
                "expected_served_model": "gpt-5.5-2026-04-23",
                "reasoning_effort": "none",
                "max_output_tokens": 2048,
                "image_detail": "auto",
                "output_contract": "page_context_validation",
            }
        },
    )


def parse(arm, raw, labels):
    if arm != "gpt55":
        raise ValueError("image helper only handles maintained GPT5.5 reference")
    if (
        raw.get("model") != "gpt-5.5-2026-04-23"
        or raw.get("status") != "completed"
        or raw.get("error")
        or raw.get("incomplete_details")
    ):
        raise ValueError("invalid Responses terminal identity")
    usage = owner._token_usage(raw)
    if usage is None:
        raise ValueError("invalid usage")
    output = owner._extract_output_text(raw)
    if owner._contract_error(output, "page_context_validation"):
        raise ValueError("invalid strict page contract")
    obj = json.loads(output)
    return (
        obj["verdict"],
        None,
        (
            (usage["prompt"] - usage.get("cached", 0)) * 5
            + usage.get("cached", 0) * 0.5
            + usage["completion"] * 30
        )
        / 1e6,
    )
