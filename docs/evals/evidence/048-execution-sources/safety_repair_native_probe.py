"""One native two-image strict qualification request per declared arm."""

import json
import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "benchmarks/providers"))
import openai_responses_model as owner  # noqa: E402
import safety_repair_guard as guard  # noqa: E402


def main():
    arm = sys.argv[1]
    topology = json.loads(
        (ROOT / "docs/evals/evidence/048-safety-repair-topology.json").read_text()
    )
    row = next(x for x in topology["native"] if x["arm"] == arm)
    body = row["body"]
    os.environ["SAFETY_REPAIR_STAGE"] = "native-" + arm
    os.environ["SAFETY_REPAIR_CASE"] = "native-synthetic-squares"
    guard.install()
    response = httpx.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"],
            "Content-Type": "application/json",
        },
        json=body,
        timeout=180,
    )
    data = response.json()
    expected = "gpt-5.5-2026-04-23" if arm == "control" else body["model"]
    assert response.status_code == 200 and data.get("status") == "completed"
    assert (
        data.get("model") == expected
        and data.get("error") is None
        and data.get("incomplete_details") is None
    )
    assert owner._token_usage(data) is not None
    text = owner._extract_output_text(data)
    assert text and owner._contract_error(text, "page_context_validation") is None
    print(
        json.dumps(
            {
                "arm": arm,
                "served": data["model"],
                "status": data["status"],
                "usage": data["usage"],
                "output": text,
            }
        )
    )


if __name__ == "__main__":
    main()
