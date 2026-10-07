"""Story246 real-driver shadow campaign. Preflight is offline; live needs root freeze."""

from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import yaml
import runtime_support as support

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).parent
OUT = ROOT / "docs/evals/evidence/067-warning-integration"
RUNS = ROOT / "output/runs/pplx-warning-integration-20261006"
CANONICAL = [
    "document_consistency_report.jsonl",
    "pattern_inventory.json",
    "consistency_plan.json",
    "conformance_report.json",
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recipe(document):
    source = HERE / "corpus" / document
    return {
        "stages": [
            {
                "id": "pages",
                "stage": "extract",
                "module": "load_artifact_v1",
                "out": "pages.jsonl",
                "params": {
                    "path": str(source / "pages.jsonl"),
                    "out": "pages.jsonl",
                    "schema_version": "page_html_v1",
                },
            },
            {
                "id": "chapters",
                "stage": "extract",
                "module": "load_artifact_v1",
                "out": "chapters.jsonl",
                "params": {
                    "path": str(source / "chapters.jsonl"),
                    "out": "chapters.jsonl",
                    "schema_version": "chapter_html_manifest_v1",
                },
            },
            {
                "id": "planner",
                "stage": "validate",
                "module": "plan_onward_document_consistency_v1",
                "needs": ["pages", "chapters"],
                "inputs": {"pages": "pages", "chapters": "chapters"},
                "out": "document_consistency_report.jsonl",
                "params": {
                    "model": support.MODEL,
                    "retry_model": "",
                    "max_completion_tokens": 8000,
                    "timeout": 120,
                    "pattern_inventory": "pattern_inventory.json",
                    "consistency_plan": "consistency_plan.json",
                    "conformance_report": "conformance_report.json",
                    "dossier_report": "document_consistency_dossier.json",
                },
            },
        ]
    }


def driver(document, identity, offline=True, shadow=True, evidence=True, failure=None):
    directory = RUNS / identity
    if not offline and directory.exists():
        raise RuntimeError("Refuse existing live identity/output; no paid overwrite")
    config = OUT / "recipes" / (document + ".yaml")
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(yaml.safe_dump(recipe(document), sort_keys=False))
    env = dict(os.environ)
    env.update(
        PYTHONPATH=os.pathsep.join(
            [str(HERE / "mock_provider"), str(ROOT)]
            + [p for p in sys.path if p.endswith("site-packages")]
        ),
        PPLX_SHADOW_TRANSPORT_MODE="offline" if offline else "live",
        PPLX_SHADOW_RUN_ID=identity,
        DOC_WEB_PPLX_SHADOW_EVIDENCE="enabled" if evidence else "disabled",
        DOC_WEB_PPLX_SHADOW_EVAL="enabled" if shadow else "disabled",
        DOC_WEB_JEV_SHADOW="disabled",
    )
    if offline:
        env["DOC_WEB_PERPLEXITY_API_KEY"] = "offline-placeholder"
        env["OPENAI_API_KEY"] = "offline-placeholder"
    if failure:
        env["PPLX_SHADOW_OFFLINE_FAILURE"] = failure
    command = [
        sys.executable,
        "driver.py",
        "--recipe",
        str(config),
        "--run-id",
        identity,
        "--output-dir",
        str(directory),
    ]
    if offline:
        command.extend(["--allow-run-id-reuse", "--force"])
    started = time.monotonic()
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    (OUT / "driver-logs").mkdir(exist_ok=True)
    (
        OUT / "driver-logs" / (identity + ("-" + failure if failure else "") + ".log")
    ).write_text(result.stdout)
    if "[stamp-skip]" in result.stdout:
        raise RuntimeError("Driver dropped invalid rows during stamping")
    if result.returncode:
        raise RuntimeError("Driver failure: " + result.stdout[-3000:])
    folder = next(directory.glob("*_plan_onward_document_consistency_v1"))
    return {
        "run_id": identity,
        "document": document,
        "folder": str(folder.relative_to(ROOT)),
        "latency_ms": (time.monotonic() - started) * 1000,
        "command": command,
        "canonical_sha256": {name: sha(folder / name) for name in CANONICAL},
    }


def state_trace(record):
    from modules.validate.plan_onward_document_consistency_v1 import (
        main as planner,
        pplx_shadow as shadow,
    )

    from bs4 import BeautifulSoup
    from schemas import PageHtml
    from modules.validate.plan_onward_document_consistency_v1.pplx_evidence import (
        observed,
    )

    source = HERE / "corpus" / record["document"]
    inputs = [
        json.loads(line) for line in (source / "pages.jsonl").read_text().splitlines()
    ]
    for row in inputs:
        PageHtml.model_validate(row)
        assert (
            row["html"]
            == (source / f"source-{row['page_number']:03d}.html").read_text()
        )
    expected = {row["page_number"]: row for row in inputs}
    stamped_path = RUNS / record["run_id"] / "01_load_artifact_v1/pages.jsonl"
    stamped = [json.loads(line) for line in stamped_path.read_text().splitlines()]
    assert len(stamped) == len(expected) > 0
    assert {row["page_number"] for row in stamped} == set(expected)
    for row in stamped:
        assert row["html"] == expected[row["page_number"]]["html"]
    folder = ROOT / record["folder"]
    dossier = json.loads((folder / "document_consistency_dossier.json").read_text())
    plan = json.loads((folder / "consistency_plan.json").read_text())
    previous = os.environ.get("DOC_WEB_PPLX_SHADOW_EVIDENCE")
    os.environ["DOC_WEB_PPLX_SHADOW_EVIDENCE"] = "enabled"
    chapters = planner._planner_input_from_dossier(dossier)["chapters"]
    planner_prompt = planner._build_prompt(dossier)
    if previous is None:
        os.environ.pop("DOC_WEB_PPLX_SHADOW_EVIDENCE", None)
    else:
        os.environ["DOC_WEB_PPLX_SHADOW_EVIDENCE"] = previous
    states = [
        {
            "chapter_basename": c["chapter_basename"],
            "source_context": c["source_context"],
            "state": shadow.state_for(c, plan),
            "payload": shadow.request_payload(shadow.state_for(c, plan))
            if shadow.state_for(c, plan)
            else None,
        }
        for c in chapters
    ]
    assert len(chapters) == 3 and {x["chapter_basename"] for x in chapters} == {
        f"chapter-{j:03d}.html" for j in (1, 2, 3)
    }
    for c, s in zip(chapters, states):
        assert "runtime_evidence" in c
        membership = c["source_pages"]
        available = [n for n in membership if n in expected]
        missing = [n for n in membership if n not in expected]
        assert c["source_context"]["available_page_count"] == len(available)
        assert c["source_context"]["missing_pages"] == missing
        actual_sources = c["runtime_evidence"]["source_pages"]
        assert [page["page_number"] for page in actual_sources] == available
        for page in actual_sources:
            obs = observed(
                BeautifulSoup(expected[page["page_number"]]["html"], "html.parser")
            )
            assert page == {"page_number": page["page_number"], **obs}
            assert page["tables"] and page["tables"][0]["rows"]
            assert page["note_attachments"]
        chapter_source = (source / c["chapter_basename"]).read_text()
        assert c["runtime_evidence"]["chapter"] == observed(
            BeautifulSoup(chapter_source, "html.parser")
        )
        if s["state"]:
            assert "gold" not in s["state"] and "oracle_conventions" not in s["state"]
            assert (
                s["state"]["extracted_evidence"]["runtime_evidence"]
                == c["runtime_evidence"]
            )
    return {
        "record": record,
        "dossier": dossier,
        "compact_chapters": chapters,
        "rendered_planner_user_prompt": planner_prompt,
        "planner_prompt_sha256": hashlib.sha256(planner_prompt.encode()).hexdigest(),
        "states": states,
    }


def preflight():
    OUT.mkdir(parents=True, exist_ok=True)
    traces = []
    records = []
    for d in range(1, 7):
        document = f"doc-{d:02d}"
        record = driver(document, "offline-" + document)
        records.append(record)
        traces.append(state_trace(record))
    available = sum(
        c["source_context"]["available_page_count"]
        for t in traces
        for c in t["compact_chapters"]
    )
    missing = sum(
        len(c["source_context"]["missing_pages"])
        for t in traces
        for c in t["compact_chapters"]
    )
    assert available == 15 and missing == 3
    # Identical frozen planner response, time, runid and paths: exact canonical hashes.
    off = driver("doc-01", "offline-invariance", shadow=False)
    on = driver("doc-01", "offline-invariance", shadow=True)
    assert off["canonical_sha256"] == on["canonical_sha256"]
    failed = []
    for failure in ["timeout", "malformed"]:
        rec = driver("doc-01", "offline-invariance", failure=failure)
        assert rec["canonical_sha256"] == off["canonical_sha256"]
        failed.append(rec)
    support.write(OUT / "offline-lineage.json", traces)
    support.write(
        OUT / "offline-driver-proof.json",
        {
            "records": records,
            "invariance_disabled": off,
            "invariance_enabled": on,
            "failure_invariance": failed,
            "network_calls": 0,
            "chapter_denominator": 18,
            "available_source_pages": available,
            "missing_source_pages": missing,
            "critical_evidence_exact_observed_equality": True,
            "canonical_exact_hashes_equal": True,
            "configuration": "eval-only observed-evidence path; ordinary disabled path separately unit-verified",
        },
    )
    support.write(
        OUT / "preflight.json",
        {
            "cap_usd": 4,
            "max_planner": 12,
            "max_candidate": 36,
            "max_qualification": 2,
            "concurrency": 1,
            "hidden_sdk_retries": 0,
            "retry_model": "",
            "planner_id": support.MODEL,
            "candidate_id": support.PPLX,
            "planner_output_max": 8000,
            "input_byte_admission_max": 64000,
            "planned_reservation_usd": 12 * 0.192 + 36 * 0.00128 + 0.192 + 0.00128,
            "recovery_headroom_usd": 4 - (12 * 0.192 + 36 * 0.00128 + 0.192 + 0.00128),
            "cache": False,
            "judge": "source adjudication+frozen typed labels; no paidjudge",
            "screen_documents": ["doc-01", "doc-02"],
            "denominator": 18,
            "repetitions": 2,
            "source_gold_review": "benchmarks/pplx-shadow/root-source-review.json",
            "actual_runtime_dossier_prompt": "offline-lineage.json; observed features only; no oracle conventions",
            "max_native_candidate_state_bytes": 16384,
            "root_go_required": True,
        },
    )
    print(
        "Offline18chaptercoverage+canonicalhashinvariance pass; reservationUSD2.54336 headroom1.45664"
    )


def freeze():
    if not (HERE / "root-source-review.json").exists():
        raise RuntimeError("Independent root source review absent")
    files = (
        list((HERE / "corpus").rglob("*"))
        + list(HERE.glob("*.py"))
        + list((HERE / "mock_provider").glob("*.py"))
        + [
            ROOT / "modules/validate/plan_onward_document_consistency_v1" / p
            for p in ["main.py", "pplx_shadow.py", "pplx_evidence.py", "jev_shadow.py"]
        ]
        + [
            HERE / "root-source-review.json",
            ROOT / "driver.py",
            ROOT / "schemas.py",
            ROOT / "tests/test_pplx_consistency_shadow.py",
            ROOT / "tests/test_jev_consistency_shadow.py",
            ROOT / "tests/test_pplx_shadow_transport.py",
        ]
        + list(
            (ROOT / "modules/validate/plan_onward_document_consistency_v1").glob(
                "module.*"
            )
        )
        + list((OUT / "recipes").glob("*.yaml"))
    )
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in files if p.is_file()}
    support.write(
        OUT / "frozen-source-manifest.json",
        {
            "base_sha": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True, cwd=ROOT
            ).strip(),
            "branch": subprocess.check_output(
                ["git", "branch", "--show-current"], text=True, cwd=ROOT
            ).strip(),
            "sources": hashes,
        },
    )
    import shutil

    for name in hashes:
        dest = OUT / "snapshots" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, dest)
    print("Frozen", len(hashes), "sources; no paid calls")


def verify_frozen():
    record = json.loads((OUT / "frozen-source-manifest.json").read_text())
    for name, h in record["sources"].items():
        if sha(ROOT / name) != h:
            raise RuntimeError("Frozen source changed:" + name)
    if os.environ.get("PPLX_SHADOW_ROOT_GO") != "enabled":
        raise RuntimeError("Root review/go absent")


def qualify():
    verify_frozen()
    support.send(
        {
            "model": support.MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": "Return JSON with the single field ready set to true.",
                }
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0,
            "max_tokens": 8000,
        },
        "planner",
        qualification=True,
    )
    from modules.validate.plan_onward_document_consistency_v1.pplx_shadow import (
        request_payload,
    )

    support.send(
        request_payload(
            {"text": "Synthetic qualification only. No source evidence is available."}
        ),
        "candidate",
        qualification=True,
    )
    support.write(
        OUT / "qualification.json",
        {"qualified": True, "models": [support.MODEL, support.PPLX]},
    )


def evaluate_record(rec):
    folder = ROOT / rec["folder"]
    raw = json.loads((folder / "conformance_report.json").read_text())
    side = json.loads((folder / "pplx_consistency_shadow_eval.json").read_text())
    gold = {
        c["chapter"]: c
        for c in json.loads((HERE / "corpus/reviewer-gold.json").read_text())
        if c["document"] == rec["document"]
    }
    assert len(side["chapters"]) == 3
    findings = {c["chapter_basename"]: c for c in raw["chapters"]}
    rows = []
    for i, row in enumerate(side["chapters"], 1):
        name = f"chapter-{i:03d}.html"
        g = gold[name]
        baseline = findings.get(name, {}).get("status", "uncertain")
        rows.append(
            {
                "run_id": rec["run_id"],
                "document": rec["document"],
                "chapter": name,
                "stratum": g["stratum"],
                "gold": g["gold"],
                "authoritative": baseline,
                "raw_candidate": row.get("pplx_status"),
                "guarded": row.get("shadow_status", "uncertain"),
                "route": row.get("route"),
                "reason": row.get("reason"),
                "confidence": row.get("confidence"),
                "unsafe_clean": row.get("shadow_status") == "conformant"
                and g["gold"] != "conformant",
                "introduced_unsafe_clean": row.get("shadow_status") == "conformant"
                and g["gold"] != "conformant"
                and baseline != "conformant",
            }
        )
    return rows


def live():
    verify_frozen()
    assert json.loads((OUT / "qualification.json").read_text())["qualified"]
    records = []
    rows = []
    # Screen two complete documents first; no second paid repeat before safety screen.
    schedule = (
        [(1, d) for d in (1, 2)]
        + [(1, d) for d in (3, 4, 5, 6)]
        + [(2, d) for d in range(1, 7)]
    )
    for rep, d in schedule:
        rec = driver(f"doc-{d:02d}", f"live-r{rep}-doc-{d:02d}", offline=False)
        records.append(rec)
        new = evaluate_record(rec)
        rows.extend(new)
        support.write(OUT / "live-records.json", records)
        support.write(OUT / "results.json", rows)
        # Must adjudicate source/request/guard before treating this as model safety failure.
        if any(x["unsafe_clean"] for x in new):
            support.write(
                OUT / "stop.json",
                {
                    "reason": "guarded_clean_on_defect_or_unknown_requires_source_adjudication",
                    "run_id": rec["run_id"],
                    "rows": [x for x in new if x["unsafe_clean"]],
                },
            )
            print("Stopped expansion at predeclared safety gate")
            return
    print("Completed12driver runs")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["preflight", "freeze", "qualify", "live"])
    a = p.parse_args()
    globals()[a.mode]()


if __name__ == "__main__":
    main()
