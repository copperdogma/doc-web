"""GET-only reconciliation; immutable served checkpoint/cost, no inference."""

import json
import os
from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / "benchmarks/results/wonder-thinking-20261014"
E = ROOT / "docs/evals/evidence/075-wonder-thinking"
rows = []
for p in sorted(R.glob("response-*.json")):
    d = json.loads(p.read_text())
    if d.get("provider") != "Meta":
        continue
    r = httpx.get(
        "https://openrouter.ai/api/v1/generation",
        params={"id": d["id"]},
        headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"]},
        timeout=60,
    )
    if r.status_code != 200:
        raise RuntimeError(f"Generation receipt {r.status_code}, try later")
    receipt = r.json()["data"]
    assert (
        receipt["model"] == "meta/muse-wonder-20261012"
        and receipt["provider_name"] == "Meta"
    )
    out = R / (p.stem + "-generation.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n")
    rows.append(
        {
            "id": d["id"],
            "model": receipt["model"],
            "provider_name": receipt["provider_name"],
            "total_cost": receipt["total_cost"],
            "receipt": str(out.relative_to(ROOT)),
        }
    )
(E / "generation-summary.json").write_text(json.dumps(rows, indent=2) + "\n")
print(json.dumps(rows))
