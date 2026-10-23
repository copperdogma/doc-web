import os
import json
import subprocess
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[2]
B = R / "benchmarks"
D = B / "results/haiku55-20261007"
for lane in ["detector", "safety"]:
    for arm in ["medium", "low", "high"]:
        name = f"{lane}-{arm}-calibration"
        if (D / (name + ".json")).exists():
            continue
        env = dict(
            os.environ,
            HAIKU55_STAGE=name,
            HAIKU55_CASE="calibration",
            PROMPTFOO_DISABLE_ADAPTIVE_SCHEDULER="true",
        )
        with (D / (name + ".log")).open("w") as log:
            code = subprocess.run(
                [
                    str(R / "scripts/run_with_doc_web_env.py"),
                    "promptfoo",
                    "eval",
                    "-c",
                    f"tasks/haiku55-{name}.yaml",
                    "--no-cache",
                    "-j",
                    "1",
                    "--output",
                    f"results/haiku55-20261007/{name}.json",
                ],
                cwd=B,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
            ).returncode
        f = D / (name + ".json")
        print(name, code, flush=True)
        if f.exists():
            d = json.loads(f.read_text())
            print(
                [
                    (
                        x.get("success"),
                        x.get("score"),
                        x.get("response", {}).get("error"),
                        (x.get("gradingResult") or {}).get("reason"),
                    )
                    for x in d["results"]["results"]
                ],
                flush=True,
            )
        if code not in [0, 100]:
            sys.exit(code)
