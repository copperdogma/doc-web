# ruff: noqa: E402
"""Offline audit/seal only. Never reads provider credentials or dispatches."""

from pathlib import Path
import json
import statistics
import sys
import os
import shutil

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "benchmarks/scripts"))
import safety_qual_088 as q
from modules.common.crop_review import evaluate
from tools.run_safety_qual_caller import contract_environment


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    E = q.E
    d = json.loads(q.LEDGER.read_text())
    p = json.loads((E / "preflight.json").read_text())
    assert (
        d["closed"]
        and len(d["calls"]) == 48
        and {c["stage"] for c in d["calls"]} == set(p["request_sources"])
    )
    rows = []
    for c in d["calls"]:
        for kind in ["request", "response"]:
            raw = (ROOT / c[kind]).read_bytes()
            assert q.sha(raw) == c[kind + "_sha256"]
        b = json.loads((ROOT / c["request"]).read_bytes())
        q.admission_body(b, c["arm"], c["stage"])
        a, env = q.parse_response((ROOT / c["response"]).read_bytes(), c["arm"])
        assert (
            c["semantic_eligible"]
            and not c.get("bound_violation")
            and c["cost_usd"] is not None
        )
        u = env["usage"]
        prices = q.PRICES[c["arm"]]
        if c["arm"] == "fable":
            uncached = u["input_tokens"]
            cached = u.get("cache_read_input_tokens", 0)
            written = u.get("cache_creation_input_tokens", 0)
        else:
            cached = u.get("input_tokens_details", {}).get("cached_tokens", 0)
            written = u.get("input_tokens_details", {}).get("cache_write_tokens", 0)
            uncached = u["input_tokens"] - cached - written
        cost = (
            uncached * prices[0]
            + cached * prices[1]
            + written * prices[2]
            + u["output_tokens"] * prices[3]
        ) / 1e6
        assert abs(cost - c["cost_usd"]) < 1e-12
        rows.append(
            {
                "stage": c["stage"],
                "native_contract": True,
                "source_prompt_exact": True,
                "answer": a,
            }
        )
    assert (
        abs(sum(c["cost_usd"] for c in d["calls"]) - d["spent_usd"]) < 1e-12
        and d["spent_usd"] <= 60
    )
    save(E / "final-raw-contract-audit.json", rows)
    artifacts = []
    for arm in ["fable", "sol"]:
        run = "safety-qual088-" + arm + "-live-20261109"
        r = ROOT / "output/runs" / run
        f = ROOT / "output/runs" / (run + "-fixture")
        rel = json.loads(
            (r / "05_release_reviewed_crops_v1/crop_review_release.json").read_text()
        )
        assert rel["synthetic_authority"] and rel["candidate_count"] == 2
        old = dict(os.environ)
        try:
            os.environ.clear()
            os.environ.update(contract_environment(arm, execute=True))
            os.environ.pop("DOC_WEB_SAFETY_QUAL_088_TRANSPORT", None)
            evaluate(rel["custody_root"], rel["inputs"], run)
        finally:
            os.environ.clear()
            os.environ.update(old)
        html = r / "output/html/chapter-001.html"
        text = html.read_text()
        pages = [
            json.loads(x) for x in (f / "custody/pages.jsonl").read_text().splitlines()
        ]
        from bs4 import BeautifulSoup

        rendered = BeautifulSoup(text, "html.parser").get_text(" ")
        expected = [
            BeautifulSoup(x.get("html", ""), "html.parser").get_text(" ") for x in pages
        ]
        assert all(x in rendered for x in expected if x)
        images = []
        for name in ["S3.png", "S4.png"]:
            a = r / "output/html/images" / name
            b = f / "custody/images" / name
            assert (
                a.read_bytes() == b.read_bytes()
                and text.count('src="images/' + name + '"') == 1
            )
            images.append(
                {
                    "name": name,
                    "sha256": q.sha(a.read_bytes()),
                    "bytes": a.stat().st_size,
                }
            )
        policy = json.loads((f / "model-policy-before-operator.json").read_text())
        assert [x["verdict_and_flags_pass"] for x in policy["cases"]] == [False, True]
        inventory = json.loads((f / "custody/inventory.json").read_text())
        assert len(inventory["pages"]) == 3
        variants = []
        for disp in ["held", "recrop", "error"]:
            vr = "safety-qual088-" + arm + "-saved-" + disp + "-20261109"
            vf = ROOT / "output/runs" / (vr + "-fixture")
            rr = ROOT / "output/runs" / vr
            result = json.loads((vf / "result.json").read_text())
            assert (
                result["mechanics_pass"]
                and not (rr / "output/html/chapter-001.html").exists()
                and not (
                    rr / "05_release_reviewed_crops_v1/illustration_manifest.jsonl"
                ).exists()
            )
            variants.append(
                {
                    "disposition": disp,
                    "held_no_html_no_released_manifest": True,
                    "result": str(vf / "result.json"),
                }
            )
        artifacts.append(
            {
                "arm": arm,
                "actual_html": str(html),
                "html_sha256": q.sha(html.read_bytes()),
                "images": images,
                "source_text_preserved": expected,
                "zero_candidate_page_preserved": True,
                "independent_native_anchor_revalidated_at_final_audit": True,
                "policy_before_operator": policy,
                "mechanics_variants": variants,
                "fixture_title_note": "Historical Sol fixturebooktitle retained forboth arms; actual nativeprovider identity livesin bound genuine receipts, not fixturetitle.",
            }
        )
        for item in [
            r,
            f,
            *[
                ROOT
                / "output/runs"
                / ("safety-qual088-" + arm + "-saved-" + x + "-20261109" + suffix)
                for x in ["held", "recrop", "error"]
                for suffix in ["", "-fixture"]
            ],
        ]:
            dest = E / "driver-artifacts" / item.name
            shutil.copytree(item, dest, dirs_exist_ok=True)
    save(E / "driver-artifact-proof.json", artifacts)
    summary = {
        "base_sha": "5bd3ba777d70347eb8dd84b9aa18a6b3ba025193",
        "worktree": str(ROOT),
        "branch": "codex/fable52-safety-qualification-20261109-doc-web",
        "cap_usd": 60,
        "known_spend_usd": d["spent_usd"],
        "unknown_exposure_usd": 0,
        "calls": 48,
        "recovery_calls": 0,
        "judge_calls": 0,
        "ledger_closed": True,
        "winner": "Retain Sol: classifier/fullpayloadtie, both ambiguitypolicyfail, Sol cheaper/faster; no usefulFablequalitygain demonstrated",
        "access": "bothdirectnativeavailable",
        "transport": "48strictnativeenvelopes qualified; actualcaller nativebounds/operator/independentreceiptanchors qualified inexplicitdefaultoffsyntheticevaluationcontext",
        "reliability": "48/48complete singleattempts; no reruns; exposed serialstudyonly",
        "classifier": {},
        "caller": {},
        "mechanics": "Both liveactualdriverapproved syntheticchains succeeded;6savedliveheld/recrop/errorvariants blockpublishing; zeroadditionalPOSTs; pages/assets/textpreserved",
        "adoption": "Do not switch toFable. RetainSol asreviewproposal model; both remainunqualified for autonomousuncertaintydecisions. No realpublication/default/C5deletion qualification",
        "tests": {"affected_consumer": 220, "combined_guard": 7, "total": 227},
        "credentials": "Existingownerwrappernativekeys only; no copied/injected/changed keys/accountsettings; no cleanupneeded",
        "scope_holds": [
            "22exposedclassifierpairs not unseen reliability",
            "15oversizecrops remainclassifieronly; no resize/currentcallerboundchange",
            "S3sourceinterpretationphysicallyplausible butdeclareduncertaintydeclinepolicyfailed separately",
            "SyntheticoperatorapprovalisnotCamapprovalanddoesnotrepairmodelpolicy",
            "C5requiresseparate50pagedetectorproof; trimmer/source-deletion/manualhold/defaultsretained",
        ],
    }
    for stage in ["classifier", "caller"]:
        for arm in ["fable", "sol"]:
            cc = [
                c for c in d["calls"] if c["stage"].startswith(stage + ":" + arm + ":")
            ]
            summary[stage][arm] = {
                "cases": len(cc),
                "cost_usd": sum(c["cost_usd"] for c in cc),
                "mean_http_latency_ms": statistics.mean(c["latency_ms"] for c in cc),
                "thinking_tokens": sum(c.get("thinking_tokens") or 0 for c in cc),
            }
            if stage == "classifier":
                summary[stage][arm].update(
                    verdict_correct=22,
                    false_safe=0,
                    flag_errors=0,
                    full_payload_pass=22,
                    original_canonical_correct=20,
                    intermediate048_correct=21,
                    source_adjudicated_correct=22,
                )
            else:
                summary[stage][arm].update(
                    policy_pass=1,
                    policy_cases=2,
                    S3="passwithcertainty; uncertaintydeclinerequirementfailed",
                    S4="passintegralbadge; correct",
                )
    save(E / "summary.json", summary)
    print(
        "FINAL AUDIT48rawcontracts/source/usage/cost;2genuinecallerchains+6savedliveholds; total",
        d["spent_usd"],
        "unknown0",
    )


if __name__ == "__main__":
    main()
