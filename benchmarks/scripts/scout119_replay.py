"""Verify the committed Scout 119 scoring evidence locally without a provider."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from benchmarks.scripts.scout116_doc_web_score import score_ocr

EVIDENCE = ROOT / "docs/evals/evidence/099-neon"
# Standard foreground pricing in integer USD nanounits per token.
RATES = {
    "gemini-4-neon": (3000, 150, 15000),
    "gemini-4-hydrogen": (1500, 75, 7500),
    "gemini-3-flash-preview": (500, 50, 3000),
}


def load(name):
    return json.loads((EVIDENCE / name).read_bytes())


def check(condition, message):
    if not condition:
        raise ValueError(message)


def sum_tiles(region, boxes):
    """An edge partition lets integer dark-pixel counts reproduce union coverage."""
    covered = 0
    total = 0
    x0, y0, x1, y1 = region["bounds"]
    for left, top, right, bottom, dark in region["tiles"]:
        check(
            x0 <= left < right <= x1 and y0 <= top < bottom <= y1
            and 0 <= dark <= (right - left) * (bottom - top),
            "invalid source pixel tile",
        )
        total += dark
        for bx0, by0, bx1, by1 in boxes:
            intersects = left < bx1 and bx0 < right and top < by1 and by0 < bottom
            if intersects:
                check(
                    bx0 <= left < right <= bx1 and by0 <= top < bottom <= by1,
                    "tile cuts through a final crop edge",
                )
                covered += dark
                break
    return total, covered


def main():
    projected = load("replay-inputs.json")
    ledger = load("ledger.json")
    manifest = load("manifest.json")
    published = manifest["published_replay"]
    check(
        hashlib.sha256((EVIDENCE / "replay-inputs.json").read_bytes()).hexdigest()
        == published["input_projection_sha256"]
        and hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        == published["replay_source_sha256"],
        "published replay files changed",
    )
    check(set(projected["final_boxes_xyxy"]) == {"candidate", "control"},
          "expected two assisted arms")
    provenance = {x["path"]: x["sha256"] for x in manifest["native_artifacts_ignored"]}
    matrix = load("matrix.json")
    for filename, sha256 in matrix["producer_sha256"].items():
        check(hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() == sha256,
              f"recorded producer differs: {filename}")
    check(ledger["closed"] and len(ledger["calls"]) == 5, "unsettled request matrix")
    costs = {"ocr": 0, "crop": 0}
    for call in ledger["calls"]:
        check(not call["in_flight"] and call["confidence"] == "eligible"
              and call["model"] == call["served_model"] and call["finish"] == ["STOP"],
              f"invalid native receipt: {call['attempt']}")
        check(call["response_sha256"] == provenance[call["response"]]
              and call["sha256"] == provenance[call["request"]],
              f"unbound native receipt: {call['attempt']}")
        usage = call["usage"]
        cold, cache, out = RATES[call["model"]]
        cached = usage.get("cachedContentTokenCount", 0)
        cost = ((usage["promptTokenCount"] - cached) * cold + cached * cache
                + (usage["candidatesTokenCount"] + usage.get("thoughtsTokenCount", 0)) * out)
        check(cost == call["cost_nanousd"] and cost <= call["reserve_nanousd"],
              f"invalid cost: {call['attempt']}")
        costs[call["lane"]] += cost
        if call["lane"] == "ocr":
            visible = projected["ocr_visible_text"][call["attempt"]]
            answer_path = f"output/fixtures/scout119-neon/{call['attempt']}.answer.txt"
            check(hashlib.sha256(visible.encode()).hexdigest() == provenance[answer_path],
                  f"visible OCR changed: {call['attempt']}")
            score = score_ocr("barney", visible)
            check(score == load(f"{call['attempt']}.score.json") and score["ratio"] < .99,
                  f"changed OCR result: {call['attempt']}")
    check(costs == {"ocr": 236_692_500, "crop": 113_988_500}
          and sum(costs.values()) / 1e9 == ledger["known_cost_usd"]
          and ledger["unknown_exposure_usd"] == 0, "invalid closed wallet totals")

    for arm, boxes in projected["final_boxes_xyxy"].items():
        audit = load(f"neon099-p12-{arm}-pixels.json")
        check(audit["source_sha256"] == projected["source_sha256"], "crop source changed")
        width, height = audit["dimensions"]
        check([[round(x * (width if idx % 2 == 0 else height)) for idx, x in enumerate(box)]
               for box in audit["boxes_normalized_xyxy"]] == boxes, "final crop boxes changed")
        loss = {}
        leaked = {}
        for name, region in projected["source_regions"].items():
            total, covered = sum_tiles(region, boxes)
            if region["kind"] == "integral":
                loss[name] = total - covered
            else:
                leaked[name] = covered
        check(loss == audit["integral_roi_loss"] and leaked == audit["nonintegral_caption_pixels_inside"],
              f"changed crop audit: {arm}")
        check(sum(loss.values()) > 0 and sum(leaked.values()) > 0, f"changed crop gate: {arm}")
    print("Reproduced two OCR scores, both final crop pixel audits and five native charges. Zero provider calls.")


if __name__ == "__main__":
    main()
