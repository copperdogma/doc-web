"""Resume only selected stages rejected locally before any POST during topology transition."""

from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / "docs/evals/evidence/089-carbon"


def run(args):
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def pair(key):
    for arm in ["candidate", "control"]:
        ledger = json.loads(
            (ROOT / "benchmarks/results/carbon-20261110/ledger.json").read_text()
        )
        stage = f"safety-{key}-{arm}"
        if any(x["stage"] == stage for x in ledger["calls"]):
            raise RuntimeError("already dispatched selected stage")
        run(["benchmarks/scripts/carbon_safety.py", key, arm])
    return key


if __name__ == "__main__":
    # First restore the missing Image011 control; its candidate is already terminal.
    run(["benchmarks/scripts/carbon_reading.py", "screen", "Image011", "control"])
    keys = [
        "page-001-000",
        "page-004-000",
        "page-009-000",
        "page-012-000",
        "page-122-001",
        "page-012-001",
    ]
    with ThreadPoolExecutor(max_workers=2) as pool:
        for future in as_completed([pool.submit(pair, k) for k in keys]):
            print("completed missing selected pair", future.result(), flush=True)
    for key in ["Image011", "Image001"]:
        run(["benchmarks/scripts/carbon_overlay.py", key])
