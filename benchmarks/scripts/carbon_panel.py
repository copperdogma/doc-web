"""Serial selected campaign continuation; no semantic retries or extra fixtures."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / "docs/evals/evidence/089-carbon"


def run(args):
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


if __name__ == "__main__":
    # First image-positive candidate must already have terminal qualification.
    results = json.loads((E / "table-results.json").read_text())
    assert any(
        x["case"] == "image-positive" and x["arm"] == "candidate" for x in results
    )
    run(["benchmarks/scripts/carbon_reading.py", "tables", "image-positive", "control"])
    for case in ["ambiguity-negative", "native-positive"]:
        for arm in ["candidate", "control"]:
            run(["benchmarks/scripts/carbon_reading.py", "tables", case, arm])
    for key in ["Image011", "Image001"]:
        for arm in ["candidate", "control"]:
            run(["benchmarks/scripts/carbon_reading.py", "screen", key, arm])
        run(["benchmarks/scripts/carbon_overlay.py", key])
    for key in [
        "page-001-000",
        "page-004-000",
        "page-009-000",
        "page-012-000",
        "page-122-001",
        "page-012-001",
    ]:
        for arm in ["candidate", "control"]:
            run(["benchmarks/scripts/carbon_safety.py", key, arm])
    run(["benchmarks/scripts/carbon_reading.py", "ocr"])
