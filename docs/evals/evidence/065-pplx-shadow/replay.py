"""Offline receipt/guard replay. No credential loading or provider calls."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from modules.validate.plan_onward_document_consistency_v1 import pplx_shadow as shadow


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable(value):
    if isinstance(value, dict):
        return {k: stable(v) for k, v in value.items() if k not in {"created_at", "latency_ms"}}
    if isinstance(value, list):
        return [stable(v) for v in value]
    return value


def main():
    frozen = read(HERE / "frozen-source-manifest.json")
    for name, expected in frozen["sources"].items():
        assert digest(ROOT / name) == expected, name
    ledger = read(HERE / "ledger.json")
    assert ledger["unknown_usd"] == 0
    assert all(c["status"] == "complete" for c in ledger["calls"])
    assert abs(sum(c["cost_usd"] for c in ledger["calls"]) - ledger["spent_usd"]) < 1e-12
    for call in ledger["calls"]:
        for suffix in ["request", "response"]:
            assert digest(HERE / "native" / (call["name"] + "." + suffix + ".json")) == call[suffix + "_sha256"]
    traces = read(HERE / "live-lineage.json")
    replayed = 0
    for trace in traces:
        rec = trace["record"]
        folder = HERE / "paid-artifacts" / rec["run_id"]
        for name, expected in rec["canonical_sha256"].items():
            assert digest(folder / name) == expected, name
        calls = iter(c for c in ledger["calls"] if c["kind"] == "candidate" and c["run_id"] == rec["run_id"])
        def replay_request(payload, key):
            nonlocal replayed
            call = next(calls)
            encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode()
            assert hashlib.sha256(encoded).hexdigest() == call["request_sha256"]
            replayed += 1
            return read(HERE / "native" / (call["name"] + ".response.json"))
        result = shadow.run_shadow(
            trace["compact_chapters"], read(folder / "consistency_plan.json"),
            read(folder / "conformance_report.json"),
            env={"DOC_WEB_PPLX_SHADOW_EVAL": "enabled", "DOC_WEB_PERPLEXITY_API_KEY": "offline-placeholder"},
            request=replay_request,
        )
        assert next(calls, None) is None
        assert stable(result) == stable(read(folder / "pplx_consistency_shadow_eval.json"))
    print(f"PASS: {len(frozen['sources'])} frozen source hashes, {len(ledger['calls']) * 2} native receipt hashes, {replayed} candidate guard replays, exact canonical hashes; zero network calls")


if __name__ == "__main__":
    main()
