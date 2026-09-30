"""Prepare an offline mechanics fixture. All approvals are synthetic test inputs."""

import argparse
import json
import shutil
from pathlib import Path

from modules.common.crop_review import binding, digest
from modules.common.utils import save_jsonl

REPO = Path(__file__).resolve().parents[1]


def prepare(root, run_id):
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    (root / "images").mkdir(exist_ok=True)

    def write(name, value):
        path = root / name
        path.write_text(json.dumps(value, indent=2) + "\n")
        return {"path": name, "sha256": digest(path)}

    def evidence(name, text):
        (root / name).write_text(text + "\n")
        return {"path": name, "sha256": digest(root / name)}

    authority_evidence = evidence(
        "authority.txt",
        "Synthetic fixture-reviewer only. Not Cam approval. Trusted local test authority.",
    )
    inventory_evidence = evidence(
        "inventory-review.txt",
        "Synthetic source inspection: exactly two source pages, one intended visual each. S3 grouping is plausible; S4 text is integral badge artwork. All candidate decisions must be reviewed.",
    )
    rows = []
    for page, case in enumerate(("S3", "S4"), 1):
        for kind in ("source", "crop"):
            destination = root / (
                f"{case}-source.png" if kind == "source" else f"images/{case}.png"
            )
            shutil.copyfile(
                REPO / f"benchmarks/input/safety-repair-048/{case}-{kind}.png",
                destination,
            )
        x0, y0, x1, y1 = (220, 200, 780, 700) if case == "S3" else (250, 220, 750, 720)
        rows.append(
            {
                "schema_version": "illustration_v1",
                "module_id": "synthetic_fixture",
                "run_id": run_id,
                "created_at": "2026-09-30T00:00:00Z",
                "source_page": page,
                "source_image": f"{case}-source.png",
                "filename": f"{case}.png",
                "bbox": {"x0": x0, "y0": y0, "x1": x1, "y1": y1},
                "alt": "Abstract coherent grouping"
                if case == "S3"
                else "FIELD STATION badge",
                "image_description": "Reviewed abstract grouping"
                if case == "S3"
                else "Badge with integral lettering",
            }
        )
    save_jsonl(root / "manifest.jsonl", rows)
    save_jsonl(
        root / "pages.jsonl",
        [
            {
                "schema_version": "page_html_v1",
                "module_id": "fixture",
                "run_id": run_id,
                "created_at": "2026-09-30T00:00:00Z",
                "page": i,
                "page_number": i,
                "html": f'<h1>Offline review fixture</h1><img alt="{r["alt"]}">',
            }
            for i, r in enumerate(rows, 1)
        ],
    )
    save_jsonl(
        root / "portions.jsonl",
        [
            {
                "schema_version": "portion_hypothesis_v1",
                "module_id": "fixture",
                "run_id": run_id,
                "created_at": "2026-09-30T00:00:00Z",
                "title": "Offline review fixture",
                "page_start": 1,
                "page_end": 2,
            }
        ],
    )
    shutil.copyfile(root / "pages.jsonl", root / "pages.ndjson")
    shutil.copyfile(root / "portions.jsonl", root / "portions.ndjson")
    bindings = [binding(r, root, run_id, root / "manifest.jsonl") for r in rows]
    write(
        "authority.json",
        {
            "run_id": run_id,
            "trust_boundary": "trusted_local_operator",
            "decision_log": "decisions.jsonl",
            "synthetic_test": True,
            "operators": [
                {
                    "operator_id": "fixture-reviewer",
                    "authority_ref": "synthetic-test-authority",
                    "evidence": authority_evidence,
                }
            ],
        },
    )
    write(
        "inventory.json",
        {
            "run_id": run_id,
            "complete": True,
            "operator_id": "fixture-reviewer",
            "authority_ref": "synthetic-test-authority",
            "review_evidence": inventory_evidence,
            "pages_artifact": {
                "path": "pages.jsonl",
                "sha256": digest(root / "pages.jsonl"),
            },
            "portions_artifact": {
                "path": "portions.jsonl",
                "sha256": digest(root / "portions.jsonl"),
            },
            "pages": [
                {
                    "source_page": r["source_page"],
                    "source_image": r["source_image"],
                    "source_sha256": b["source_sha256"],
                }
                for r, b in zip(rows, bindings)
            ],
            "visuals": [
                {
                    "visual_id": f"visual-{i}",
                    "source_page": r["source_page"],
                    "candidate_ids": [b["candidate_id"]],
                }
                for i, (r, b) in enumerate(zip(rows, bindings), 1)
            ],
        },
    )
    shutil.copyfile(
        REPO
        / "benchmarks/results/safety-repair-048-20260929-continuation1/response-068.json",
        root / "saved-S3-pass.json",
    )
    write(
        "synthetic-S4-fail.json",
        {
            "synthetic_test": True,
            "verdict": "fail",
            "reason": "Synthetic false rejection for mechanics testing; not a measured model output.",
        },
    )
    save_jsonl(
        root / "proposals.jsonl",
        [
            {
                "candidate_id": b["candidate_id"],
                "binding": b,
                "verdict": "pass" if i == 0 else "fail",
                "origin": "saved_evaluation_replay" if i == 0 else "synthetic_test",
                "receipt": {
                    "path": "saved-S3-pass.json"
                    if i == 0
                    else "synthetic-S4-fail.json",
                    "sha256": digest(
                        root
                        / ("saved-S3-pass.json" if i == 0 else "synthetic-S4-fail.json")
                    ),
                },
            }
            for i, b in enumerate(bindings)
        ],
    )
    decisions = []
    for i, b in enumerate(bindings, 1):
        human = {
            "candidate_id": b["candidate_id"],
            "operator_id": "fixture-reviewer",
            "action": "approve_current_crop",
            "reason": "Synthetic source-reviewed approval; coherent grouping allowed"
            if i == 1
            else "Synthetic source-reviewed approval; integral badge text is allowed",
        }
        human_input = write(f"human-{i}.json", human)
        decisions.append(
            {
                **human,
                "decision_id": f"synthetic-approval-{i}",
                "binding": b,
                "authority_ref": "synthetic-test-authority",
                "policy_version": "all-candidate-review-v1",
                "reviewed_at": "2026-09-30T00:00:00Z",
                "supersedes": None,
                "human_input": human_input,
            }
        )
    save_jsonl(root / "decisions.jsonl", decisions)
    return {
        k: str(
            root
            / (
                "manifest.jsonl"
                if k == "manifest"
                else "proposals.jsonl"
                if k == "proposals"
                else "decisions.jsonl"
                if k == "decisions"
                else f"{k}.json"
            )
        )
        for k in ("manifest", "inventory", "proposals", "decisions", "authority")
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.root, args.run_id), indent=2))
