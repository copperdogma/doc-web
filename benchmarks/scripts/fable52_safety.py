# ruff: noqa: E402
"""Independent Scout097 strict source/crop safety, exactly one case per invocation."""

import sys
import os
import json
import math
import hashlib
import base64
import io
from pathlib import Path
import httpx
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "benchmarks/providers"))
sys.path.insert(0, str(ROOT / "benchmarks/scripts"))
import fable52_guard as guard
import scout096_safety as old
from fable52_reading import save

E = ROOT / "docs/evals/evidence/087-fable52"
MODEL = "anthropic/claude-fable-5.2"


def body(key, arm):
    b = old.body(key, "control")
    if arm == "control":
        b["store"] = False
        b["service_tier"] = "default"
        return b
    parts = b["input"][0]["content"]
    return {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": p["text"]}
                    if p["type"] == "input_text"
                    else {"type": "image_url", "image_url": {"url": p["image_url"]}}
                    for p in parts
                ],
            }
        ],
        "max_tokens": 32768,
        "reasoning": {"effort": "xhigh"},
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "page_context_validation",
                "strict": True,
                "schema": b["text"]["format"]["schema"],
            },
        },
        "provider": {
            "only": ["anthropic"],
            "allow_fallbacks": False,
            "require_parameters": True,
            "max_price": {"prompt": 8, "completion": 40},
        },
    }


def preflight():
    rows = []
    for k in old.helper.image_cases():
        b = body(k, "control")
        imgs = []
        for p in b["input"][0]["content"][1:]:
            raw = base64.b64decode(p["image_url"].split(",", 1)[1])
            im = Image.open(io.BytesIO(raw))
            imgs.append(
                {"sha256": hashlib.sha256(raw).hexdigest(), "dimensions": im.size}
            )
        rows.append(
            {
                "key": k,
                "images": imgs,
                "request_sha256": {
                    a: old.digest(body(k, a)) for a in ["candidate", "control"]
                },
            }
        )
    save(
        E / "safety-preflight.json",
        {
            "cases": rows,
            "golden": str(old.GOLDEN.relative_to(ROOT)),
            "golden_sha256": hashlib.sha256(old.GOLDEN.read_bytes()).hexdigest(),
            "judge": "none/source review and deterministic verdict",
            "concurrency": 1,
        },
    )
    print([x["key"] for x in rows])


def run(key):
    guard.install()
    result_path = E / f"safety-{key}.json"
    results = json.loads(result_path.read_text()) if result_path.exists() else []
    golden = json.loads(old.GOLDEN.read_text())
    for arm in ["candidate", "control"]:
        if any(x["arm"] == arm for x in results):
            continue
        b = body(key, arm)
        if arm == "candidate" and os.environ.get("FABLE52_DIAGNOSTIC") == "1":
            b.pop("response_format", None)
            b["provider"]["require_parameters"] = False
        os.environ["FABLE52_STAGE"] = f"safety-{key}-{arm}" + (
            "-diagnostic"
            if arm == "candidate" and os.environ.get("FABLE52_DIAGNOSTIC") == "1"
            else ""
        )
        if arm == "candidate":
            endpoint = "https://openrouter.ai/api/v1/chat/completions"
            secret = os.environ["OPENROUTER_API_KEY"]
        else:
            endpoint = "https://api.openai.com/v1/responses"
            secret = os.environ["OPENAI_API_KEY"]
        direct = arm == "candidate" and os.environ.get("FABLE52_ROUTE") == "direct"
        if direct:
            from fable52_native import send as native_send

            original = old.body(key, "control")
            content = []
            for part in original["input"][0]["content"]:
                if part["type"] == "input_text":
                    content.append({"type": "text", "text": part["text"]})
                else:
                    url = part["image_url"]
                    header, data = url.split(",", 1)
                    content.append(
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": header.split(":")[1].split(";")[0],
                                "data": data,
                            },
                        }
                    )
            nb = {
                "model": "claude-fable-5-2",
                "max_tokens": 32768,
                "output_config": {
                    "effort": "xhigh",
                    "format": {
                        "type": "json_schema",
                        "schema": original["text"]["format"]["schema"],
                    },
                },
                "messages": [{"role": "user", "content": content}],
            }
            raw, d = native_send(nb, os.environ["FABLE52_STAGE"])
            resp = None
        else:
            resp = httpx.post(
                endpoint,
                headers={"Authorization": "Bearer " + secret},
                json=b,
                timeout=900,
            )
        row = {"key": key, "arm": arm}
        try:
            if resp is not None:
                resp.raise_for_status()
                d = resp.json()
            if arm == "control":
                verdict, cost = old.parse("control", d)
            elif direct:
                err = old.helper.owner._contract_error(raw, "page_context_validation")
                assert not err, err
                verdict = json.loads(raw)["verdict"]
                u = d["usage"]
                cost = (u["input_tokens"] * 8 + u["output_tokens"] * 40) / 1e6
            else:
                assert (
                    d["model"] in [MODEL, "anthropic/claude-fable-5.2-20261109"]
                    and d["provider"] == "Anthropic"
                    and d["choices"][0]["finish_reason"] == "stop"
                    and not d.get("error")
                )
                content = d["choices"][0]["message"]["content"]
                err = old.helper.owner._contract_error(
                    content, "page_context_validation"
                )
                assert not err, err
                verdict = json.loads(content)["verdict"]
                cost = d["usage"]["cost"]
                assert math.isfinite(cost)
            row.update(
                verdict=verdict,
                cost_usd=cost,
                golden=golden[key]["verdict"],
                false_safe=verdict == "pass" and golden[key]["verdict"] == "fail",
                correct=verdict == golden[key]["verdict"],
            )
        except Exception as exc:
            row.update(error=str(exc), capability="not measured")
        results.append(row)
        save(E / f"safety-{key}.json", results)
        print(json.dumps(row), flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "preflight":
        preflight()
    else:
        run(sys.argv[1])
