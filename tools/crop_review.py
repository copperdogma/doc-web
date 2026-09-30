"""Inspect bound crops and record explicit trusted-local human input (offline).

The caller supplies local operator authority and human-authored input. This tool
has no model/API adapter and does not claim secure external authentication.
Recrops belong in a new active custody bundle; retain the previous bundle.
"""

import argparse
import base64
import html
import json
from datetime import datetime, timezone
from pathlib import Path

from modules.common.crop_review import (
    binding,
    custody_path,
    digest,
    object_digest,
    read_bound,
    require,
)
from modules.common.utils import read_jsonl


def record(root, manifest, authority, decisions, human_input, run_id, supersedes=None):
    root = Path(root).resolve()
    for path in (manifest, authority, decisions, human_input):
        require(
            Path(path).absolute().is_relative_to(root),
            "Review inputs must remain in custody",
        )
        custody_path(root, str(Path(path).absolute().relative_to(root)))
    human = json.loads(Path(human_input).read_text())
    require(
        human.get("action")
        in ("approve_current_crop", "require_recrop", "unresolved_ownership"),
        "Invalid review action",
    )
    require(bool(human.get("reason")), "Source-grounded reason required")
    authorized = json.loads(Path(authority).read_text())
    require(
        authorized.get("run_id") == run_id
        and authorized.get("trust_boundary") == "trusted_local_operator",
        "Invalid local authority",
    )
    require(
        authorized.get("decision_log")
        == str(Path(decisions).absolute().relative_to(root)),
        "Decision target must equal explicit authority log designation",
    )
    operator = next(
        (
            x
            for x in authorized.get("operators", [])
            if x["operator_id"] == human.get("operator_id")
        ),
        None,
    )
    require(operator is not None, "Unauthorized operator")
    read_bound(root, operator["evidence"])
    candidates = [binding(r, root, run_id, manifest) for r in read_jsonl(manifest)]
    candidate = next(
        (b for b in candidates if b["candidate_id"] == human.get("candidate_id")), None
    )
    require(candidate is not None, "Human input refers to stale/unknown candidate")
    target = Path(decisions).resolve()
    for original in root.rglob("*"):
        if original.is_file() and original.resolve() != target:
            require(
                not target.samefile(original), "Decision log aliases retained evidence"
            )
    require(
        target
        not in {
            Path(manifest).resolve(),
            Path(authority).resolve(),
            Path(human_input).resolve(),
        },
        "Decision log aliases review inputs",
    )
    events = list(read_jsonl(decisions))
    previous = [x for x in events if x.get("candidate_id") == candidate["candidate_id"]]
    require(
        supersedes == (previous[-1]["decision_id"] if previous else None),
        "Explicit supersession of latest event required",
    )
    event = {
        **{k: human[k] for k in ("candidate_id", "operator_id", "action", "reason")},
        "binding": candidate,
        "authority_ref": operator["authority_ref"],
        "policy_version": "all-candidate-review-v1",
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        "supersedes": supersedes,
        "human_input": {
            "path": str(Path(human_input).absolute().relative_to(root)),
            "sha256": digest(human_input),
        },
    }
    event["decision_id"] = object_digest(event)
    with Path(decisions).open("a") as stream:
        stream.write(json.dumps(event) + "\n")
    return event


def show_html(root, manifest, output):
    root = Path(root).resolve()
    output = Path(output).absolute()
    require(
        not output.resolve().is_relative_to(root) and not output.exists(),
        "Review HTML must be new and outside custody",
    )
    proposals = (
        list(read_jsonl(root / "proposals.jsonl"))
        if (root / "proposals.jsonl").exists()
        else []
    )
    decisions = (
        list(read_jsonl(root / "decisions.jsonl"))
        if (root / "decisions.jsonl").exists()
        else []
    )
    sections = []
    for row in read_jsonl(manifest):
        source = custody_path(root, row["source_image"])
        crop = custody_path(
            root,
            str(
                (
                    Path(manifest).absolute().parent / "images" / row["filename"]
                ).relative_to(root)
            ),
        )
        bound = binding(row, root, row["run_id"], Path(manifest).absolute())
        width, height = bound["source_dimensions"]
        box = bound["bbox"]

        def uri(path):
            return (
                "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()
            )

        overlay = f'<svg viewBox="0 0 {width} {height}" width="100%"><image href="{uri(source)}" width="{width}" height="{height}"/><rect x="{box["x0"]}" y="{box["y0"]}" width="{box["x1"] - box["x0"]}" height="{box["y1"] - box["y0"]}" fill="none" stroke="red" stroke-width="3"/></svg>'
        metadata = {
            "binding": bound,
            "proposal": [
                x for x in proposals if x.get("candidate_id") == bound["candidate_id"]
            ],
            "review_events": [
                x for x in decisions if x.get("candidate_id") == bound["candidate_id"]
            ],
        }
        sections.append(
            "<section><h2>"
            + html.escape(row["filename"])
            + '</h2><p>Inspect full source boundaries/captions and exact crop. Components or absent captions alone do not establish uncertainty.</p><div style="display:grid;grid-template-columns:1fr 1fr;gap:24px">'
            + overlay
            + '<img style="width:100%" src="'
            + uri(crop)
            + '"></div><pre>'
            + html.escape(json.dumps(metadata, indent=2))
            + "</pre></section>"
        )
    inventory_path = root / "inventory.json"
    if inventory_path.exists():
        inventory = json.loads(inventory_path.read_text())
        candidate_pages = {row["source_page"] for row in read_jsonl(manifest)}
        for page in inventory.get("pages", []):
            if page["source_page"] in candidate_pages:
                continue
            source = read_bound(
                root, {"path": page["source_image"], "sha256": page["source_sha256"]}
            )
            source_uri = (
                "data:image/png;base64,"
                + base64.b64encode(source.read_bytes()).decode()
            )
            sections.append(
                "<section><h2>Source page "
                + html.escape(str(page["source_page"]))
                + ' — no detected candidate</h2><p>Inspect the entire source for missed visuals. No detected candidate does not establish completeness. Operator inventory review must identify every intended visual before release.</p><img style="max-width:100%" src="'
                + source_uri
                + '"></section>'
            )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        '<!doctype html><meta charset="utf-8"><title>Local crop source review</title><h1>All-candidate source review</h1><p>Model verdicts do not authorize publication. Record approve_current_crop, require_recrop, or unresolved_ownership through explicit operator input.</p>'
        + "".join(sections)
    )
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("show", "record"))
    parser.add_argument("--custody-root", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--authority")
    parser.add_argument("--decisions")
    parser.add_argument("--human-input")
    parser.add_argument("--supersedes")
    parser.add_argument(
        "--html-out", help="New local full-resolution review HTML outside custody"
    )
    args = parser.parse_args()
    try:
        if args.command == "show":
            result = [
                binding(
                    row,
                    Path(args.custody_root).resolve(),
                    args.run_id,
                    Path(args.manifest).absolute(),
                )
                for row in read_jsonl(args.manifest)
            ]
            if args.html_out:
                show_html(args.custody_root, args.manifest, args.html_out)
        else:
            require(
                all((args.authority, args.decisions, args.human_input)),
                "record needs authority, decisions, and human input",
            )
            result = record(
                args.custody_root,
                args.manifest,
                args.authority,
                args.decisions,
                args.human_input,
                args.run_id,
                args.supersedes,
            )
        print(json.dumps(result, indent=2))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
