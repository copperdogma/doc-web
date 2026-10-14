# ruff: noqa: E402
"""Frozen effort-only calibration; explicit pair dispatch and preserved old ledger."""

import base64
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "benchmarks/providers"))
import argon_levels_guard as guard
from doc_web.literal_fidelity import SourcePageReview
from doc_web.literal_tables import compare_tables
from modules.common.literal_table_review import review_literal_tables
from benchmarks.scorers.image_crop_scorer import get_assert as crop_score

E = guard.EVIDENCE
R = guard.RESULTS
OLD = ROOT / "benchmarks/results/argon-20261013"
PAIRS = [
    ("table", "native-positive", ("low", "medium"), 4),
    ("table", "image-positive", ("medium", "low"), 6),
    ("table", "ambiguity-negative", ("low", "medium"), 8),
    ("crop", "Image037", ("high", "medium"), 32),
    ("crop", "Image001", ("medium", "high"), 18),
    ("crop", "Image011", ("high", "medium"), 24),
    ("crop-confirmation", "Image037", ("medium", "high"), 32),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def body_for(sequence, level):
    body = json.loads((OLD / f"request-{sequence:03d}.json").read_text())
    assert body["generationConfig"]["maxOutputTokens"] == 32768
    assert body["generationConfig"]["thinkingConfig"] == {"thinkingLevel": "medium"}
    body["generationConfig"]["thinkingConfig"] = {"thinkingLevel": level}
    return body


def preflight():
    if (E / "freeze.json").exists():
        raise RuntimeError("Frozen calibration already exists; never overwrite")
    old = json.loads(guard.OLD_LEDGER.read_text())
    assert old["closed"]
    prior = old["spent_usd"] + sum(
        c["reserved_usd"] for c in old["calls"] if c["cost_usd"] is None
    )
    matrix = []
    for lane, key, levels, original in PAIRS:
        bodies = [body_for(original, level) for level in levels]
        neutral = []
        for level, body in zip(levels, bodies):
            copy = json.loads(json.dumps(body))
            copy["generationConfig"]["thinkingConfig"] = {"thinkingLevel": "medium"}
            neutral.append(copy)
            parts = body["contents"][0]["parts"]
            assert len(body["contents"]) == 1 and len(parts) == 2
            assert "inlineData" in parts[1] and "text" in parts[0]
            assert not any(
                x in body["generationConfig"]
                for x in ["temperature", "topP", "topK", "cachedContent"]
            )
            matrix.append(
                {
                    "lane": lane,
                    "case": key,
                    "level": level,
                    "stage": f"{lane}-{key}-{level}",
                    "original_sequence": original,
                    "original_request_sha256": sha(
                        (OLD / f"request-{original:03d}.json").read_bytes()
                    ),
                    "request_sha256": sha(json.dumps(body, sort_keys=True).encode()),
                    "image_sha256": sha(
                        base64.b64decode(parts[1]["inlineData"]["data"])
                    ),
                    "semantic_text_sha256": sha(
                        json.dumps(
                            [body.get("systemInstruction"), parts[0]], sort_keys=True
                        ).encode()
                    ),
                    "schema_sha256": sha(
                        json.dumps(
                            body["generationConfig"].get("responseJsonSchema"),
                            sort_keys=True,
                        ).encode()
                    ),
                    "max_output_tokens": 32768,
                    "per_call_reservation_usd": 0.37968,
                    "conditional": lane == "crop-confirmation",
                }
            )
        assert neutral[0] == neutral[1], "Only thinking level may differ"
    sources = [
        "benchmarks/scripts/argon_levels.py",
        "benchmarks/providers/argon_levels_guard.py",
        "modules/common/literal_table_review.py",
        "doc_web/literal_tables.py",
        "benchmarks/scorers/image_crop_scorer.py",
        "benchmarks/golden/image-crops.json",
    ]
    sources += [
        f"testdata/literal-table-fidelity/confirmation-v2/{key}/golden.html"
        for key in ("native-positive", "image-positive", "ambiguity-negative")
    ]
    frozen = {
        "date": "2026-10-13",
        "incremental_cap_usd": 6,
        "cumulative_cap_usd": 15,
        "old_ledger_sha256": sha(guard.OLD_LEDGER.read_bytes()),
        "old_maximum_exposure_usd": prior,
        "maximum_selected_calls": 14,
        "maximum_selected_reservations_usd": 14 * 0.37968,
        "operational_balance_usd": 6 - 14 * 0.37968,
        "concurrency": 1,
        "cache": "no subject reuse or explicit cache; report implicit cache",
        "repeat": "one fresh matched pair per case; only final conditional pair permitted",
        "stops": "Source-backed low literal or high geometry failure stops affected lane; fresh medium paired output remains contrast, independent other lane continues",
        "judge": "independent source review plus original deterministic scorer; no paid API judge",
        "quality": "literal exact clear36cells/spans and hold both ambiguouscells; geometry source-complete eachcase, numericrange/edgeclipping explicit",
        "promotion": "effort calibration on exposed cases only; no incumbent superiority or promotion",
        "matrix": matrix,
        "sources": {p: sha((ROOT / p).read_bytes()) for p in sources},
    }
    save(E / "freeze.json", frozen)
    save(
        R / "ledger.json",
        {
            "cap_usd": 6,
            "spent_usd": 0,
            "calls": [],
            "closed": False,
            "original_exposure_usd": prior,
        },
    )
    for rel, digest in frozen["sources"].items():
        path = E / "execution-sources" / (digest + "-" + Path(rel).name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / rel).read_bytes())
    print(
        "Ready:", len(matrix), "frozen requests; incremental6; cumulative prior", prior
    )


def call(item):
    if os.environ.get("ARGON_LEVELS_LIVE") != "1":
        raise RuntimeError("Preparation only; root dispatch gate required")
    body = body_for(item["original_sequence"], item["level"])
    assert sha(json.dumps(body, sort_keys=True).encode()) == item["request_sha256"]
    os.environ["ARGON_STAGE"] = item["stage"]
    guard.install()
    response = httpx.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-4-argon:generateContent",
        headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
        json=body,
        timeout=1200,
    )
    response.raise_for_status()
    data = response.json()
    candidates = data.get("candidates", [])
    assert (
        data["modelVersion"] == "gemini-4-argon"
        and len(candidates) == 1
        and candidates[0]["finishReason"] == "STOP"
    )
    raw = "\n".join(
        p["text"]
        for p in candidates[0]["content"]["parts"]
        if "text" in p and not p.get("thought")
    )
    if item["lane"] == "table":
        SourcePageReview.model_validate_json(raw)
    else:
        parsed = json.loads(raw)
        assert set(parsed) == {"images"}
        for row in parsed["images"]:
            assert (
                set(row) == {"description", "bbox"}
                and len(row["bbox"]) == 4
                and all(type(x) in (int, float) for x in row["bbox"])
            )
    return raw, data


def run_pair(lane, key):
    frozen = json.loads((E / "freeze.json").read_text())
    for rel, digest in frozen["sources"].items():
        assert sha((ROOT / rel).read_bytes()) == digest, rel
    items = [x for x in frozen["matrix"] if x["lane"] == lane and x["case"] == key]
    assert len(items) == 2
    started = time.monotonic()
    results = []
    for item in items:
        path = E / (item["stage"] + ".json")
        if path.exists():
            raise RuntimeError("Fresh result required")
        if lane == "table":
            initial = json.loads(
                (ROOT / f"docs/evals/evidence/071-argon/initial-{key}.json").read_text()
            )
            source = (
                ROOT / f"testdata/literal-table-fidelity/confirmation-v2/{key}/page.png"
            )
            initial["image"] = str(source)
            initial["source"] = []

            def reader(image_path, requests):
                assert sha(Path(image_path).read_bytes()) == item["image_sha256"]
                raw, data = call(item)
                requests.append(
                    {
                        "requested_model": "gemini-4-argon",
                        "served_model": data["modelVersion"],
                        "response_id": data.get("responseId"),
                        "status": "completed",
                        "raw_response": raw,
                        "usage": data["usageMetadata"],
                        "submitted_image_sha256": sha(source.read_bytes()),
                    }
                )
                return SourcePageReview.model_validate_json(raw)

            row = review_literal_tables(
                [initial],
                out_path=R / (item["stage"] + ".jsonl"),
                run_id="argon-levels-" + item["stage"],
                reader=reader,
            )[0]
            report = json.loads(
                Path(row["literal_fidelity"]["report_path"]).read_text()
            )
            reviewed = report["tables"][0]["review"] if report["tables"] else {}
            score = compare_tables(
                (source.parent / "golden.html").read_text(), reviewed.get("html", "")
            )
            result = {
                **item,
                "status": report["status"],
                "uncertainties": reviewed.get("uncertain_cells", []),
                "score": score,
                "report": str(
                    Path(row["literal_fidelity"]["report_path"]).relative_to(ROOT)
                ),
            }
        else:
            raw, data = call(item)
            score = crop_score(raw, {"vars": {"golden_key": key}})
            result = {
                **item,
                "raw": raw,
                "score": score,
                "served_model": data["modelVersion"],
            }
        save(path, result)
        results.append(result)
        print(item["stage"], result.get("status"), result["score"], flush=True)
    save(
        E / (f"{lane}-{key}-pair.json"),
        {
            "results": results,
            "pair_wall_seconds": time.monotonic() - started,
            "order": [x["level"] for x in items],
        },
    )


if __name__ == "__main__":
    if sys.argv[1] == "preflight":
        preflight()
    elif sys.argv[1] == "pair":
        run_pair(sys.argv[2], sys.argv[3])
