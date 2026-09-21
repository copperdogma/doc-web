"""One-shot observation: existing full planner + two bounded native shadow batches."""

import hashlib
import json
import os
import sys
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from modules.validate.plan_onward_document_consistency_v1 import main as planner  # noqa: E402
from modules.validate.plan_onward_document_consistency_v1 import jev_shadow as shadow  # noqa: E402

BASE = ROOT / "docs/evals/artifacts/story234-evidence-contract-recheck"
CAP = 0.15


def save(path, value):
    with path.open("x") as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write("\n")


class Custody:
    def __init__(self, directory):
        self.directory = directory
        directory.mkdir(exist_ok=False)
        self.used = 0.0
        self.names = set()

    def dispatch(self, name, payload, reserve):
        if name in self.names or (self.directory / (name + ".request.json")).exists():
            raise ValueError("duplicate_attempt")
        if self.used + reserve > CAP or len(self.names) >= 7:
            raise ValueError("spend_or_call_cap")
        save(self.directory / (name + ".request.json"), payload)
        self.used += reserve
        self.names.add(name)
        with (self.directory / "ledger.jsonl").open("a") as f:
            f.write(
                json.dumps({"event": "dispatch", "id": name, "reserved_usd": reserve})
                + "\n"
            )

    def response(self, name, raw):
        save(self.directory / (name + ".response.json"), raw)


class AttemptNames:
    def __init__(self):
        self.entries = {}
        self.ordinal = 0

    def register(self, payload):
        self.ordinal += 1
        name = f"jev-{self.ordinal}"
        if id(payload) in self.entries:
            raise ValueError("payload_object_reused")
        self.entries[id(payload)] = (payload, name)
        return name

    def lookup(self, payload):
        held, name = self.entries[id(payload)]
        assert held is payload
        return name


def verify_planner(raw, input_cap):
    assert raw.model == "gpt-4.1-2025-04-14", "served_identity"
    assert len(raw.choices) == 1 and raw.choices[0].finish_reason == "stop", (
        "completion_status"
    )
    assert raw.usage is not None, "usage_missing"
    for field, cap in [("prompt_tokens", input_cap), ("completion_tokens", 6000)]:
        value = getattr(raw.usage, field, None)
        assert type(value) is int and 0 <= value <= cap, "usage_bounds"


def main():
    manifest = json.loads((BASE / "freeze.json").read_text())
    for rel, digest in manifest.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest, rel
    assert json.loads((BASE / "review.json").read_text())["status"] == "CLEAR"
    assert os.environ.get("OPENAI_API_KEY") and os.environ.get(
        "DOC_WEB_TYPESAFE_RUNTIME_API_KEY"
    )
    payload = json.loads((BASE / "planner.request.json").read_text())
    dossier = json.loads((BASE / "dossier.json").read_text())
    reserve = (
        len(json.dumps(payload, ensure_ascii=False).encode()) + 2048
    ) * 2 / 1e6 + payload["max_tokens"] * 8 / 1e6
    assert reserve + 6 * shadow.RESERVE_USD <= CAP
    custody = Custody(BASE / "run")
    from openai import OpenAI

    client = OpenAI(max_retries=0, base_url="https://api.openai.com/v1")

    def create(**kwargs):
        request = {k: v for k, v in kwargs.items() if k != "timeout"}
        assert request == payload, "planner_request_changed"
        custody.dispatch("planner", request, reserve)
        raw = client.chat.completions.create(**kwargs)
        custody.response("planner", raw.model_dump(mode="json"))
        verify_planner(
            raw, len(json.dumps(payload, ensure_ascii=False).encode()) + 2048
        )
        return raw

    proxy = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )
    started = time.monotonic()
    try:
        result = planner.call_planning_model(
            proxy,
            model="gpt-4.1",
            retry_model=None,
            dossier=dossier,
            max_completion_tokens=6000,
            timeout=60,
        )
    except Exception:
        save(
            custody.directory / "stop.json",
            {"reason": "planner_failure", "reserved_usd": custody.used},
        )
        return 1
    planner_ms = (time.monotonic() - started) * 1000
    outputs = planner.build_outputs(
        dossier,
        result,
        chapters_path=dossier["source_artifacts"]["chapters_artifact"],
        pages_path=dossier["source_artifacts"]["pages_artifact"],
        run_id="story234-evidence-contract-recheck",
    )
    for name, value in zip(["primary", "patterns", "plan", "conformance"], outputs):
        save(custody.directory / (name + ".json"), value)
    chapters = planner._planner_input_from_dossier(dossier)["chapters"]
    primary_hashes = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in custody.directory.glob("*.json")
        if p.stem in {"primary", "patterns", "plan", "conformance"}
    }
    names = AttemptNames()
    http = shadow._native_http

    def captured_http(request, key):
        name = names.lookup(request)
        raw = http(request, key)
        custody.response(
            name, raw
        )  # Before strict Choice parser, including rejected distributions.
        return raw

    shadow._native_http = captured_http

    def request(payload, key):
        name = names.register(payload)
        custody.dispatch(name, payload, shadow.RESERVE_USD)
        return shadow.native_request(payload, key)

    reports = []
    for index in range(0, len(chapters), 3):
        report = shadow.run_shadow(
            chapters[index : index + 3],
            outputs[2],
            outputs[3],
            env={**os.environ, "DOC_WEB_JEV_SHADOW": "enabled"},
            request=request,
        )
        save(custody.directory / f"shadow-{index // 3 + 1}.json", report)
        reports.append(report)
    assert all(
        hashlib.sha256((custody.directory / name).read_bytes()).hexdigest() == digest
        for name, digest in primary_hashes.items()
    ), "authoritative_artifacts_changed"
    raw = json.loads((custody.directory / "planner.response.json").read_text())
    usage = raw.get("usage") or {}
    known_planner = (
        (usage["prompt_tokens"] * 2 + usage["completion_tokens"] * 8) / 1e6
        if all(k in usage for k in ["prompt_tokens", "completion_tokens"])
        else None
    )
    save(
        custody.directory / "summary.json",
        {
            "authoritative_artifact_sha256_unchanged": primary_hashes,
            "planner_latency_ms": planner_ms,
            "planner_known_cost_usd": known_planner,
            "maximum_reserved_usd": custody.used,
            "dispatched": len(custody.names),
            "jev_known_cost_usd": sum(r["known_cost_usd"] for r in reports),
            "jev_unknown_reserved_usd": sum(
                r["unknown_cost_reserved_usd"] for r in reports
            ),
            "scope": "Added shadow cost alongside full planner; not savings or production traffic.",
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
