"""Execute resolved one-case Promptfoo artifacts; pause on a mismatched saved answer."""

import json
import os
import subprocess
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / "benchmarks"
R = B / "results/mistral-large4-20261006"
lane = sys.argv[1]
cfg = yaml.safe_load((B / f"tasks/mistral4-{lane}-full.yaml").read_text())
collected = []
for idx, test in enumerate(cfg["tests"]):
    key = test["vars"].get("crop_key", test["vars"].get("golden_key"))
    task = B / f"tasks/mistral4-{lane}-case-{idx:02d}.yaml"
    task.write_text(yaml.safe_dump({**cfg, "tests": [test]}, sort_keys=False))
    out = R / f"{lane}-{key}.json"
    env = dict(
        os.environ,
        MISTRAL_STAGE=lane + "-full",
        PROMPTFOO_DISABLE_ADAPTIVE_SCHEDULER="true",
    )
    with (R / f"{lane}-{key}.log").open("w") as log:
        code = subprocess.run(
            [
                str(ROOT / "scripts/run_with_doc_web_env.py"),
                "promptfoo",
                "eval",
                "-c",
                str(task.relative_to(B)),
                "--no-cache",
                "-j",
                "1",
                "--output",
                str(out.relative_to(B)),
            ],
            cwd=B,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        ).returncode
    if not out.exists():
        raise RuntimeError("Harness failed before durable artifact: " + key)
    d = json.loads(out.read_text())
    row = d["results"]["results"][0]
    collected.append(row)
    (R / (lane + "-progressive.json")).write_text(
        json.dumps(collected, indent=2) + "\n"
    )
    print(key, row.get("success"), row.get("score"), flush=True)
    if not row.get("success") or code not in (0, 100):
        print(
            "Paused for source/operational adjudication; no further dispatch",
            flush=True,
        )
        break
