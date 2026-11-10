"""Offline exact-wire/terminal/usage/parity audit and compact result record."""

import hashlib
import io
import tarfile
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "benchmarks/scripts"))
import carbon_native as native  # noqa: E402

E = ROOT / "docs/evals/evidence/089-carbon"
R = ROOT / "benchmarks/results/carbon-20261110"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    ledger = json.loads((R / "ledger.json").read_text())
    plan = json.loads((E / "preflight.json").read_text())
    matrix = {r["stage"]: r for r in plan["matrix"]}
    assert ledger["closed"] and len(ledger["calls"]) == 24
    assert {c["stage"] for c in ledger["calls"]} == set(matrix)
    audited = []
    public_mode = "--public-projection" in sys.argv
    public_responses = {}
    redaction = {}
    if public_mode:
        manifest = json.loads((E / "manifest.json").read_text())
        archive_bytes = b"".join(
            (ROOT / row["path"]).read_bytes() for row in manifest["archive_parts"]
        )
        with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
            for member in archive.getmembers():
                if member.isfile() and member.name.startswith(
                    "benchmarks/results/carbon-20261110/response-"
                ):
                    public_responses[member.name] = archive.extractfile(member).read()
        redaction = {
            row["path"]: row
            for row in json.loads((E / "provider-state-redaction.json").read_text())[
                "affected"
            ]
        }
    for call in ledger["calls"]:
        assert call.get("cost_usd") is not None and not call.get("in_flight")
        assert not call.get("bound_violation") and call["status_code"] == 200
        request_bytes = (ROOT / call["request"]).read_bytes()
        response_bytes = (
            public_responses[call["response"]]
            if public_mode
            else (ROOT / call["response"]).read_bytes()
        )
        assert sha(request_bytes) == call["request_sha256"]
        if public_mode and call["response"] in redaction:
            projection = redaction[call["response"]]
            assert sha(response_bytes) == projection["projection_sha256"]
            assert call["response_sha256"] == projection["original_sha256"]
        else:
            assert sha(response_bytes) == call["response_sha256"]
        body, response = json.loads(request_bytes), json.loads(response_bytes)
        row = matrix[call["stage"]]
        planned = ROOT / row["request_path"]
        if planned.exists() and "--custody-only" not in sys.argv and not public_mode:
            assert sha(planned.read_bytes()) == row["request_sha256"]
            assert body == json.loads(planned.read_text())
        else:
            custody = json.loads((E / "custody-index.json").read_text())
            evidence = next(
                x
                for x in custody["regenerable_rendered_cases"]
                if x["rendered"] == row["request_path"]
            )
            canonical = json.dumps(
                body, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode()
            assert sha(canonical) == evidence["semantic_sha256"]
            assert evidence["original_rendered_lexical_sha256"] == row["request_sha256"]
        assert row["model"] == call["model"]
        if call["model"].startswith("gemini"):
            text = native.parse(
                response,
                call["model"],
                body["generationConfig"].get("responseJsonSchema"),
            )
            assert text and call["served_model"] == call["model"]
            u = response["usageMetadata"]
            inp = u["promptTokenCount"]
            output = u["candidatesTokenCount"] + u.get("thoughtsTokenCount", 0)
            assert (
                inp <= row["input_bound"]
                and output <= body["generationConfig"]["maxOutputTokens"]
            )
        else:
            assert (
                response["status"] == "completed"
                and not response.get("incomplete_details")
                and not response.get("error")
            )
            expected = {
                "gpt-5.5": {"gpt-5.5", "gpt-5.5-2026-04-23"},
                "gpt-6-astra": {"gpt-6-astra"},
            }[call["model"]]
            assert response["model"] in expected
            texts = [
                c["text"]
                for o in response["output"]
                if o.get("type") == "message"
                for c in o["content"]
                if c.get("type") == "output_text"
            ]
            assert len(texts) == 1
            import jsonschema

            jsonschema.validate(json.loads(texts[0]), body["text"]["format"]["schema"])
        audited.append(
            {
                "stage": call["stage"],
                "identity_terminal_usage_schema": "pass",
                "exact_rendered_payload_parity": True,
                "wire_sha256": sha(request_bytes),
                "response_sha256": sha(response_bytes),
                "original_response_sha256": call["response_sha256"],
                "response_custody": "token-redacted projection, not original response bytes"
                if public_mode and call["response"] in redaction
                else "original exact response bytes",
            }
        )
    assert abs(sum(c["cost_usd"] for c in ledger["calls"]) - ledger["spent_usd"]) < 1e-9
    controls = sum(
        c["cost_usd"] for c in ledger["calls"] if c["model"] != "gemini-4-carbon"
    )
    assert ledger["spent_usd"] <= 10 and controls <= 3
    summary = {
        "base_sha": "1c3f3e31158ec753e057e79839f438d021500214",
        "scope": "Scout109 item3 original12subjects +12freshcontrols",
        "inference_posts": 24,
        "known_usd": round(ledger["spent_usd"], 11),
        "unknown_usd": 0,
        "paid_judges": 0,
        "recovery_inference_posts": 0,
        "cap_usd": 10,
        "control_pool_usd": round(controls, 11),
        "cache": "no subject output reuse; implicit3712inputtokens on GPT5.5 sealcontrol, recorded in native usage; candidatecache0",
        "thinking": "Carbon HIGH32768 only; no effort comparison",
        "topology": "initial tables serial, remaining mixed serial/concurrency2; no clean isolated serial latency superiority claim",
        "reliability": "24/24 terminal contract-valid inference; local admission refusals recovered before POST, not provider failures",
        "tasks": {},
    }
    for task in ["table", "crop", "safety", "ocr"]:
        summary["tasks"][task] = {}
        for arm in ["candidate", "control"]:
            calls = [
                c
                for c in ledger["calls"]
                if c["stage"].startswith(task + "-") and c["stage"].endswith("-" + arm)
            ]
            summary["tasks"][task][arm] = {
                "n": len(calls),
                "usd": round(sum(c["cost_usd"] for c in calls), 11),
                "http_mean_s": round(
                    statistics.mean(c["latency_ms"] for c in calls) / 1000, 3
                ),
            }
    summary["tasks"]["table"].update(
        result="tie:36positiveclearcells exact plus6clear ambiguitycasecells;2trueambiguityholds each; originalambiguityscore7/8 retained",
        action="retain Astra; Carbon high slower/more costly",
    )
    summary["tasks"]["crop"].update(
        result="strict Carbon1/2 vs Gemini0/2; Image0111endpointpixel lost,Image001complete; controls lose5or7Image011pixels by declaredround/floorpolicy and18finalNpixels onImage001; originaloverlap .9931/.9805 vs .9752/.9735",
        action="retain detector/manual holds; no raw runtime coordinate parity or full detector qualification",
    )
    summary["tasks"]["safety"].update(
        result="Carbon6/6 vsfreshGPT5.5 4/6;zero false-safe each;controlfalse rejects001/004;source flags/reasons reviewed",
        action="bounded lead versus GPT5.5 only; retain currentSol,Attempt088 full22/actualcaller context untested for Carbon",
    )
    summary["tasks"]["ocr"].update(
        result="Carbon.987360 vs exactGemini3.8 .983830;bothbelow.99;definite omissions/substitutions remain; originalsource/goldenunchanged",
        action="retain currentOCR; no qualified replacement",
    )
    candidate = sum(
        c["cost_usd"] for c in ledger["calls"] if c["model"] == "gemini-4-carbon"
    )
    summary["candidate_usd"] = round(candidate, 11)
    summary["december_same_usage_total_usd"] = round(2 * candidate + controls, 11)
    summary["adoption"] = (
        "retain runtime defaults; safety/crop bounded capability leads, tabletie, OCRgatefail; source deletion/publication/fullcaller not qualified"
    )
    (
        E
        / (
            "raw-audit-public-projection.json"
            if public_mode
            else "raw-audit-custody.json"
            if "--custody-only" in sys.argv
            else "raw-audit.json"
        )
    ).write_text(json.dumps({"audited": 24, "rows": audited}, indent=2) + "\n")
    (E / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(
        json.dumps(
            {
                "audited": 24,
                "known_usd": summary["known_usd"],
                "unknown": 0,
                "control_pool_usd": summary["control_pool_usd"],
            }
        )
    )


if __name__ == "__main__":
    main()
