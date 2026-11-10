"""Frozen remaining case pairs, maximum two independent jobs, no added calls."""

from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(args):
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def case(job):
    kind, key = job
    if kind == "current-control":
        run(["benchmarks/scripts/carbon_reading.py", "screen", key, "control"])
    elif kind == "crop":
        for arm in ["candidate", "control"]:
            run(["benchmarks/scripts/carbon_reading.py", "screen", key, arm])
    elif kind == "safety":
        for arm in ["candidate", "control"]:
            run(["benchmarks/scripts/carbon_safety.py", key, arm])
    elif kind == "ocr":
        run(["benchmarks/scripts/carbon_reading.py", "ocr"])
    return job


if __name__ == "__main__":
    jobs = (
        [("current-control", "Image011"), ("crop", "Image001")]
        + [
            ("safety", k)
            for k in [
                "page-001-000",
                "page-004-000",
                "page-009-000",
                "page-012-000",
                "page-122-001",
                "page-012-001",
            ]
        ]
        + [("ocr", "barney")]
    )
    errors = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(case, job) for job in jobs]
        for f in as_completed(futures):
            try:
                print("completed", f.result(), flush=True)
            except Exception as e:
                errors.append(repr(e))
                print("operational error", repr(e), flush=True)
    for key in ["Image011", "Image001"]:
        run(["benchmarks/scripts/carbon_overlay.py", key])
    if errors:
        raise RuntimeError(str(errors))
