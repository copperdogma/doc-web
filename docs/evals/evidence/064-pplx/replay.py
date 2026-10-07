"""Offline exact receipts/parser/ledger reconciliation. Never makes network calls."""

import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
module_spec = importlib.util.spec_from_file_location(
    "replay_pplx", HERE / "snapshots/benchmarks/jev-consistency/pplx_campaign.py"
)
# Load current adapter only after confirming exact executed snapshot hash.
source = ROOT / "benchmarks/jev-consistency/pplx_campaign.py"
preflight = json.loads((HERE / "preflight.json").read_text())
assert (
    hashlib.sha256(source.read_bytes()).hexdigest()
    == preflight["sources"]["benchmarks/jev-consistency/pplx_campaign.py"]
)
module_spec = importlib.util.spec_from_file_location("replay_pplx", source)
module = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(module)
ledger = json.loads((HERE / "ledger.json").read_text())
manifest = json.loads((HERE / "raw-manifest.json").read_text())
with tempfile.TemporaryDirectory() as temporary:
    target = Path(temporary)
    with tarfile.open(HERE / "receipts.tar.gz", "r:gz") as archive:
        archive.extractall(target, filter="data")
    for name, record in manifest.items():
        data = (target / name).read_bytes()
        assert len(data) == record["bytes"]
        assert hashlib.sha256(data).hexdigest() == record["sha256"]
    settled = 0.0
    for c in ledger["calls"]:
        assert c["status"] == "complete"
        raw = json.loads((target / (c["name"] + ".response.json")).read_text())
        label, confidence, cost = module.parse(c["arm"], raw)
        assert (
            label == c["label"]
            and confidence == c["confidence"]
            and abs(cost - c["cost_usd"]) < 1e-12
        )
        settled += cost
    assert abs(settled - ledger["spent_usd"]) < 1e-12
    assert ledger["unknown_usd"] == 0
print(
    json.dumps(
        {
            "calls": len(ledger["calls"]),
            "receipts": len(manifest),
            "reconciled_spend_usd": settled,
            "unknown_usd": 0,
        }
    )
)
