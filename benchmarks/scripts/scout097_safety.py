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
import scout097_guard as guard
import scout096_safety as old
from scout097_reading import save

E = ROOT / "docs/evals/evidence/079-scout097"
MODEL = "deepseek/deepseek-v4.1-flash-1017"


def body(key, arm):
    b = old.body(key, "control")
    if arm == "control":
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
        "reasoning": {"effort": "high"},
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "page_context_validation",
                "strict": True,
                "schema": b["text"]["format"]["schema"],
            },
        },
        "provider": {
            "only": ["Cloudflare"],
            "allow_fallbacks": False,
            "require_parameters": True,
            "max_price": {"prompt": 0.30, "completion": 1.20},
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
    results = []
    golden = json.loads(old.GOLDEN.read_text())
    for arm in ["candidate", "control"]:
        b = body(key, arm)
        os.environ["SCOUT097_STAGE"] = f"safety-{key}-{arm}"
        if arm == "candidate":
            endpoint = "https://openrouter.ai/api/v1/chat/completions"
            secret = os.environ["OPENROUTER_API_KEY"]
        else:
            endpoint = "https://api.openai.com/v1/responses"
            secret = os.environ["OPENAI_API_KEY"]
        resp = httpx.post(
            endpoint, headers={"Authorization": "Bearer " + secret}, json=b, timeout=600
        )
        row = {"key": key, "arm": arm}
        try:
            resp.raise_for_status()
            d = resp.json()
            if arm == "control":
                verdict, cost = old.parse("control", d)
            else:
                assert (
                    d["model"] in [MODEL, "deepseek/deepseek-v4.1-flash-20261017"]
                    and d["provider"] == "Cloudflare"
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
