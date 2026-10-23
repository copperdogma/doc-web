import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / "benchmarks/results/haiku55-20261007"
sys.path.insert(0, str(ROOT))
from benchmarks.scorers.handwritten_notes_transcription import score_page_html_artifact  # noqa: E402

if any(R.glob("haiku55-ocr-*.log")) or any(
    (ROOT / "output/runs").glob("haiku55-ocr-*")
):
    raise RuntimeError(
        "Refuse to overwrite prior OCR evidence; use a separately authorized run identity"
    )

for arm in ["medium", "low", "high", "control"]:
    name = f"haiku55-ocr-{arm}-barney-20261007" + (
        "-repair1" if arm == "medium" else ""
    )
    env = dict(
        os.environ,
        HAIKU55_ROOT=str(ROOT),
        HAIKU55_ARM=arm,
        HAIKU55_STAGE="ocr-" + arm,
        HAIKU55_CASE="barney",
        HAIKU55_RECOVERY="1" if arm == "medium" else "0",
        PYTHONPATH=str(R / "startup") + ":" + str(ROOT),
    )
    with (R / (name + ".log")).open("w") as log:
        code = subprocess.run(
            [
                sys.executable,
                "driver.py",
                "--recipe",
                f"configs/recipes/haiku55-ocr-{arm}-barney.yaml",
                "--run-id",
                name,
                "--end-at",
                "ocr_ai",
                "--instrument",
            ],
            cwd=ROOT,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        ).returncode
    artifact = ROOT / f"output/runs/{name}/02_ocr_ai_gpt51_v1/pages_html.jsonl"
    if artifact.exists():
        result = score_page_html_artifact(
            ROOT / "testdata/handwritten-notes-barney-real.txt", artifact
        )
        (R / f"ocr-{arm}-score.json").write_text(json.dumps(result, indent=2))
        print(arm, code, result["overall_ratio"], flush=True)
    else:
        print(arm, code, "no artifact", flush=True)
        raise RuntimeError("OCR harness failed")
