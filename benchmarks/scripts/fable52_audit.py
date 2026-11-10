# ruff: noqa: E402
"""Offline final native receipts/schema/cost audit; never dispatches inference."""

import hashlib
import json
import sys
import statistics
import shutil
from pathlib import Path
import jsonschema

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "benchmarks/scripts"))
from doc_web.literal_fidelity import SourcePageReview
from fable52_reading import CROP_SCHEMA
from benchmarks.providers.openrouter_vision_chat import PAGE_CONTEXT_SCHEMA

E = ROOT / "docs/evals/evidence/087-fable52"
R = ROOT / "benchmarks/results/fable52-20261109"


def save(p, d):
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")


def main():
    d = json.loads((R / "ledger.json").read_text())
    audit = []
    tot = 0
    for c in d["calls"]:
        for kind in ["request", "response"]:
            b = (ROOT / c[kind]).read_bytes()
            assert hashlib.sha256(b).hexdigest() == c[kind + "_sha256"]
            assert (E / Path(c[kind]).name).read_bytes() == b
        b = json.loads((ROOT / c["request"]).read_text())
        res = json.loads((ROOT / c["response"]).read_text())
        stage = c["stage"]
        valid = c.get("status_code") == 200
        if valid and c["model"] == "claude-fable-5-2":
            assert (
                res["model"] == "claude-fable-5-2"
                and res["stop_reason"] == "end_turn"
                and res["type"] == "message"
            )
            assert (
                b["max_tokens"] == 32768
                and b["output_config"]["effort"] == "xhigh"
                and "temperature" not in b
            )
            assert (
                res["usage"]["service_tier"] == "standard"
                and res["usage"]["speed"] == "standard"
            )
            texts = [p["text"] for p in res["content"] if p["type"] == "text"]
            assert len(texts) == 1
            raw = texts[0]
            if stage.startswith("table-"):
                SourcePageReview.model_validate_json(raw)
            if stage.startswith("crop-"):
                jsonschema.validate(json.loads(raw), CROP_SCHEMA)
            if stage.startswith("safety-"):
                jsonschema.validate(json.loads(raw), PAGE_CONTEXT_SCHEMA)
            u = res["usage"]
            cost = (u["input_tokens"] * 8 + u["output_tokens"] * 40) / 1e6
            assert abs(cost - c["cost_usd"]) < 1e-10
            c["thinking_tokens"] = u.get("output_tokens_details", {}).get(
                "thinking_tokens"
            )
            c["native_tier"] = "standard"
        if c["cost_usd"] is not None:
            tot += c["cost_usd"]
        audit.append(
            {
                "stage": stage,
                "http": c.get("status_code"),
                "served": c.get("served_model"),
                "semantic_eligible": valid and stage != "ocr-barney-control",
                "request_object_lossless": True,
                "complete_raw_response": True,
            }
        )
    assert abs(tot - d["spent_usd"]) < 1e-10
    unknown = sum(c["reserved_usd"] for c in d["calls"] if c["cost_usd"] is None)
    assert abs(unknown - 4.76416) < 1e-10 and tot + unknown < 30
    d.update(unknown_exposure_usd=unknown, closed=True)
    save(R / "ledger.json", d)
    save(E / "ledger.json", d)
    summary = {
        "base_sha": "5bd3ba777d70347eb8dd84b9aa18a6b3ba025193",
        "branch": "codex/fable52-20261109-doc-web",
        "worktree": str(ROOT),
        "owner": "Doc Web",
        "cap_usd": 30,
        "spent_usd": tot,
        "unknown_exposure_usd": unknown,
        "accounted_maximum_usd": tot + unknown,
        "posts": len(d["calls"]),
        "candidate_cases": 12,
        "valid_controls": 11,
        "quarantined_controls": 1,
        "judge_calls": 0,
        "route": "Direct Anthropic claude-fable-5-2 xhigh32768; coordinator-authorized recovery from OR402; no OpenRouter qualification",
        "native_standard": True,
        "effort_calibration": "max65536 not triggered: all36clear cells exact and2realambiguities held; lower levels unmeasured",
        "access": "direct available; selected OR account blocked",
        "transport": "native Messages structural API schema + documented SDK transform and original host schema validation; original OR and broad runtime integration unqualified",
        "reliability": "12/12 native subject responses terminal; pre-inference2OR402+1native400 retained; OCR shim importerror repaired before POST; population/concurrency unmeasured",
        "adoption": "Prioritize nativeFable safety for broader22case+consumer qualification; retain current defaults. Tablequalitytie withAstra but highercost/slower; cropsourcefailure and OCR.99miss forbid replacement.",
        "safety": {},
        "table": {
            "clear_cells": 36,
            "candidate_exact": 36,
            "control_exact": 36,
            "genuine_ambiguous_cells": 2,
            "candidate_holds": 2,
            "control_holds": 2,
            "accepted_wrong_cells": 0,
            "original_ambiguity_text_score": "7/8 both; raw placeholders differ from authored codepoints; both correcthold",
        },
        "crop": {
            "candidate_scores": {"Image011": 0.9478, "Image001": 0.7702},
            "control_scores": {"Image011": 0.9839, "Image001": 0.9829},
            "candidate_source_pass_cases": 0,
            "control_source_pass_cases": 1,
            "Image011": "Fabledate/sealrim preserved but12darkpixels at two integral baselineends clipped; Gemini16sealrimpixels clipped at source rows1374,1375,1790. Bothfailstrictfullsource.",
            "Image001": "Fableomitsentire1887-1987date; Geminipreservesfulltitle/date.",
            "coordinate_limit": "Maintained scorer uses golden-assisted axisoracle; not runtimecoordinate qualification",
        },
        "ocr": {
            "candidate_ratio": 0.981295,
            "threshold": 0.99,
            "candidate_source_review": "comrads→comrade and omittedit/our definite; no broad fabricatedpassage. Some smallgolden spelling/token ambiguities remain; no golden/scorer change or invented correctedscore.",
            "control_requested": "gemini-3.7-flash",
            "control_served": "gemini-3.8-flash",
            "control_quarantined": True,
            "relative_claim": False,
        },
        "credential_custody": "Existingownerwrapper preserved; central OR temporaryisolatedvar removed verifiedabsent; directexistingownerkey nevercopied/changed",
        "limits": [
            "Singleexposedresponsepercase,notproductionreliability",
            "No13crop/22safetyfullqualification",
            "No400pageOCR/C1deletion",
            "Nooriginalsizecaller/grouping/geometry consumerqualification",
            "NoOpenRouterservingproof",
            "No implementedruntime routing/default/deploy/commit/push",
        ],
    }
    for task in ["table", "crop", "safety", "ocr"]:
        summary[task]["economics"] = {}
        for arm in ["candidate", "control"]:
            cs = [
                c
                for c in d["calls"]
                if c["stage"].startswith(task + "-")
                and "-" + arm in c["stage"]
                and c["cost_usd"] is not None
            ]
            summary[task]["economics"][arm] = {
                "calls": len(cs),
                "cost_usd": sum(c["cost_usd"] for c in cs),
                "latency_ms": [c["latency_ms"] for c in cs],
                "mean_latency_ms": statistics.mean(c["latency_ms"] for c in cs),
                "thinking_tokens": sum(c.get("thinking_tokens", 0) or 0 for c in cs),
            }
    rows = []
    for p in sorted(E.glob("safety-page-*.json")):
        rows.extend(json.loads(p.read_text()))
    for arm in ["candidate", "control"]:
        rr = [r for r in rows if r["arm"] == arm]
        assert len(rr) == 6
        summary["safety"][arm] = {
            "cases": 6,
            "correct": sum(r.get("correct", False) for r in rr),
            "false_safe": sum(r.get("false_safe", False) for r in rr),
        }
    save(E / "summary.json", summary)
    save(E / "raw-audit.json", audit)
    for run in [
        "fable52-ocr-barney-candidate-20261109",
        "fable52-ocr-barney-control-20261109",
    ]:
        dest = E / "driver-artifacts" / run
        shutil.copytree(ROOT / "output/runs" / run, dest, dirs_exist_ok=True)
    for f in [
        "benchmarks/providers/fable52_guard.py",
        "benchmarks/scripts/fable52_reading.py",
        "benchmarks/scripts/fable52_safety.py",
        "benchmarks/scripts/fable52_native.py",
        "benchmarks/scripts/fable52_audit.py",
        "benchmarks/scripts/fable52_overlay.py",
        "tests/test_fable52_campaign.py",
        "modules/common/table_source_review.py",
        "modules/common/literal_table_review.py",
        "benchmarks/scorers/image_crop_scorer.py",
        "benchmarks/scorers/handwritten_notes_transcription.py",
        "benchmarks/prompts/crop-conservative-count.js",
        "benchmarks/golden/image-crops.json",
        "benchmarks/golden/crop-page-level-safety-repair-048-source-adjudicated.json",
        "testdata/handwritten-notes-barney-real.txt",
    ]:
        p = E / "source-snapshots" / f
        p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / f, p)
    save(
        E / "provenance.json",
        {
            "base": summary["base_sha"],
            "native_producing_epoch": "producing-epochs/direct1; finalimportpathfix only affectsOCRstartup; guardunknownaccountingcorrection no semanticpayloadchanges",
            "request_custody": "Complete JSONvalue reserializedwithsortedkeys; sourcebase64exact; notoriginallexicalwirebytes. FullHTTPresponsebytesexact. Noauthorizationheadersretained.",
            "semantics": "Maintainedpolicies/prompt/sourcepixels/goldens/scorers unchanged atbase; SDKschemaadaptation documented. Original SourcePageReviewandcrop+safetycontracts validatedoffline on rawoutputs.",
            "python": "Nativecandidate/controlmain python interpreter; primaryvenv lacksanthropic/pytest. python hasanthropic0.79.0. OCRdriveractualsitecustomize shim, notproductionmodelattribution.",
            "commands": [
                "DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/doc-web/.env FABLE52_ROUTE=direct python scripts/run_with_doc_web_env.py python benchmarks/scripts/fable52_reading.py tables CASE [ARM]",
                "... fable52_reading.py screen Image011/Image001",
                "... fable52_safety.py page-NNN-NNN",
                "... fable52_reading.py ocr",
                "python -m pytest tests/test_fable52_campaign.py -q",
                "python benchmarks/scripts/fable52_audit.py",
            ],
            "replay": "Auditonlyoffline; closedledger forbidsanyfreshinference underretainedrunidentity.",
        },
    )
    print("AUDIT PASS", len(audit), "rawreceipts; cost", tot, "unknown", unknown)


if __name__ == "__main__":
    main()
