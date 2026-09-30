"""Public offline native replay mechanics fixture; approvals explicitly synthetic."""

import argparse
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw

from modules.common.crop_review import binding, digest
from modules.common.crop_review_setup import write_templates
from modules.common.crop_safety_custody import prepare_custody
from modules.common.utils import read_jsonl, save_jsonl

REPO = Path(__file__).resolve().parents[1]


def prepare(root, run_id, *, disposition="approved"):
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    original = root / "input"
    original.mkdir()
    (original / "images").mkdir()
    old = REPO / "tests/fixtures/crop_review_offline/approved"
    rows = list(read_jsonl(old / "manifest.jsonl"))
    for row in rows:
        shutil.copyfile(old / row["source_image"], original / row["source_image"])
        shutil.copyfile(
            old / "images" / row["filename"], original / "images" / row["filename"]
        )
        row.update(
            source_image=str(original / row["source_image"]),
            run_id="original-guided-fixture",
            source_dimensions=[1000, 1000],
            coordinate_system="source_pixels",
            crop_transform="rectangle_and_encode",
        )
    save_jsonl(original / "manifest.jsonl", rows)
    source3 = original / "text-only-page.png"
    image = Image.new("RGB", (1000, 1000), "white")
    ImageDraw.Draw(image).text(
        (120, 120), "Text-only source page: no illustration", (0, 0, 0)
    )
    image.save(source3)
    source_map = [
        {"source_page": r["source_page"], "source_image": r["source_image"]}
        for r in rows
    ] + [{"source_page": 3, "source_image": str(source3)}]
    (original / "source-map.json").write_text(json.dumps(source_map, indent=2) + "\n")
    pages = list(read_jsonl(old / "pages.jsonl"))
    pages.append(
        {
            "schema_version": "page_html_v1",
            "page": 3,
            "page_number": 3,
            "html": "<p>Text-only source page: no illustration.</p>",
        }
    )
    save_jsonl(original / "pages.ndjson", pages)
    portions = list(read_jsonl(old / "portions.jsonl"))
    portions[0]["page_end"] = 3
    save_jsonl(original / "portions.ndjson", portions)
    custody = root / "custody"
    paths = prepare_custody(
        original / "manifest.jsonl",
        original / "pages.ndjson",
        original / "portions.ndjson",
        original / "source-map.json",
        original,
        custody,
        run_id,
    )
    write_templates(custody, run_id)
    replay = root / "replay"
    replay.mkdir()
    entries = []
    for index, row in enumerate(rows, 68):
        request = (
            REPO / f"tests/fixtures/crop_safety_runtime/native/request-{index:03d}.json"
        )
        response = (
            REPO
            / f"tests/fixtures/crop_safety_runtime/native/response-{index:03d}.json"
        )
        shutil.copyfile(request, replay / request.name)
        shutil.copyfile(response, replay / response.name)
        entries.append(
            {
                "filename": row["filename"],
                "request_path": request.name,
                "request_sha256": digest(request),
                "response_path": response.name,
                "response_sha256": digest(response),
                "status_code": 200,
            }
        )
    if disposition == "error":
        path = replay / entries[0]["response_path"]
        value = json.loads(path.read_text())
        value["status"] = "incomplete"
        value["incomplete_details"] = {"reason": "max_output_tokens"}
        path.write_text(json.dumps(value))
        entries[0]["response_sha256"] = digest(path)
    (replay / "mapping.json").write_text(
        json.dumps(
            {
                "mode": "mock" if disposition == "error" else "replay",
                "entries": entries,
            },
            indent=2,
        )
        + "\n"
    )
    identity = {
        "run_id": run_id,
        "intent": "authorize_local_crop_review",
        "operator_id": "synthetic-fixture-reviewer",
        "authority_ref": "synthetic-test-only",
        "reason": "Synthetic mechanics authority; not Cam approval",
        "synthetic_test": True,
    }
    (root / "synthetic-authority.json").write_text(
        json.dumps(identity, indent=2) + "\n"
    )
    inventory = json.loads((custody / "inventory.json").read_text())
    candidates = [
        binding(r, custody, run_id, custody / "manifest.jsonl")
        for r in read_jsonl(custody / "manifest.jsonl")
    ]
    assessment = {
        "run_id": run_id,
        "operator_id": identity["operator_id"],
        "authority_ref": identity["authority_ref"],
        "source_inventory_complete": True,
        "reason": "Synthetic source inspection: S3 coherent grouping plausible; S4 integral badge lettering; page3 text only, no missed visual.",
        "reviewed_at": "2026-09-30T00:00:00Z",
        "reviewed_pages": [
            {"source_page": p["source_page"], "source_sha256": p["source_sha256"]}
            for p in inventory["pages"]
        ],
        "visuals": inventory["visuals"],
        "decisions": [
            {
                "candidate_id": b["candidate_id"],
                "operator_id": identity["operator_id"],
                "action": "approve_current_crop",
                "reason": "Synthetic explicit source-reviewed approval; not Cam approval",
            }
            for b in candidates
        ],
    }
    if disposition == "held":
        assessment["decisions"][0].update(
            action="unresolved_ownership",
            reason="Synthetic unresolved current-crop ownership: hold publication",
        )
    (root / "synthetic-review.json").write_text(json.dumps(assessment, indent=2) + "\n")
    return {
        "root": str(root),
        "custody": str(custody),
        "replay_manifest": str(replay / "mapping.json"),
        "source_paths": paths,
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", required=True)
    p.add_argument("--run-id", required=True)
    p.add_argument(
        "--disposition", choices=("approved", "held", "error"), default="approved"
    )
    a = p.parse_args()
    print(json.dumps(prepare(a.root, a.run_id, disposition=a.disposition), indent=2))
