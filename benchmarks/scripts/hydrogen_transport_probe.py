# ruff: noqa: E402
import os
import sys
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from benchmarks.scripts import hydrogen_native as n
from modules.common import crop_safety

b = crop_safety.build_request(
    ROOT / "tests/fixtures/crop_review_offline/approved/S3-source.png",
    ROOT / "tests/fixtures/crop_review_offline/approved/images/S3.png",
    live=True,
)
b["model"] = "gemini-4-hydrogen"
# No credentials or network: actual entrypoint's live_send reaches mock only.
import httpx

seen = []


def fake(url, **kwargs):
    seen.append(
        {"url": url, "body": kwargs["json"], "header_names": list(kwargs["headers"])}
    )
    return httpx.Response(200, json={"mock": True})


httpx.post = fake
n.guard.install = lambda: None
os.environ["HYDROGEN_CALLER_ARM"] = "candidate"
os.environ["GEMINI_API_KEY"] = "synthetic-never-a-real-secret"
os.environ["OPENAI_API_KEY"] = "synthetic-never-a-real-secret"
from benchmarks.scripts.hydrogen_caller import install

install()
g = runpy.run_module(
    "modules.transform.propose_crop_safety_v1.main", run_name="probe_no_main"
)
g["live_send"](b)
expected = json.loads((n.guard.E / "rendered/caller-S3-candidate.json").read_text())
assert (
    len(seen) == 1
    and seen[0]["url"]
    == "https://generativelanguage.googleapis.com/v1beta/models/gemini-4-hydrogen:generateContent"
)
assert seen[0]["body"] == expected and seen[0]["header_names"] == ["x-goog-api-key"]
print(
    "PASS network-denied fresh-runpy actual live_send exact native endpoint/body/header isolation"
)
