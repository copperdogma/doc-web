"""Explicit operator-owned review setup; never infer authority from a model."""

import json
import shutil
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
from modules.common.utils import read_jsonl, save_jsonl


def safe_root(root):
    root = Path(root).absolute()
    require(
        ".." not in root.parts
        and not any(p.is_symlink() for p in (root, *root.parents)),
        "Unsafe review custody root",
    )
    require(root.is_dir(), "Missing review custody")
    root = root.resolve()
    for path in root.rglob("*"):
        require(not path.is_symlink(), "Symlink inside review custody")
    for name in (
        "manifest.jsonl",
        "inventory.json",
        "pages.jsonl",
        "portions.jsonl",
        "decisions.jsonl",
    ):
        custody_path(root, name)
    for name in (
        "inventory.json",
        "decisions.jsonl",
        "authority.json",
        "proposals.jsonl",
    ):
        path = root / name
        require(
            not path.exists() or path.stat().st_nlink == 1,
            "Mutable review target has inode aliases",
        )
    return root


def atomic_json(path, value):
    temporary = path.with_suffix(".setup-tmp")
    require(
        not temporary.exists() and not temporary.is_symlink(),
        "Unsafe review temporary output",
    )
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def attach_proposals(root, path, run_id):
    root = safe_root(root)
    incoming = Path(path).absolute()
    require(
        ".." not in incoming.parts
        and incoming.is_file()
        and not any(p.is_symlink() for p in (incoming, *incoming.parents)),
        "Unsafe proposals attachment",
    )
    target = root / "proposals.jsonl"
    rows = list(read_jsonl(root / "manifest.jsonl"))
    byid = {
        b["candidate_id"]: b
        for b in [binding(r, root, run_id, root / "manifest.jsonl") for r in rows]
    }
    proposals = list(read_jsonl(incoming))
    require(
        len({p.get("candidate_id") for p in proposals}) == len(proposals),
        "Duplicate proposal attachment",
    )
    for proposal in proposals:
        require(
            proposal.get("candidate_id") in byid
            and proposal.get("binding") == byid[proposal["candidate_id"]],
            "Stale attached proposal",
        )
        read_bound(root, proposal["request"])
        if proposal.get("receipt"):
            read_bound(root, proposal["receipt"])
    if incoming != target:
        require(
            not target.exists() and not target.is_symlink(),
            "Proposal attachment overwrite denied",
        )
        shutil.copyfile(incoming, target)
        require(digest(incoming) == digest(target), "Proposal attachment changed")
    return target


def _new_evidence(root, path, name):
    path = Path(path).absolute()
    require(
        path.is_file() and not any(p.is_symlink() for p in (path, *path.parents)),
        "Unsafe operator input",
    )
    target = root / name
    require(
        not target.exists() and not target.is_symlink(),
        "Operator evidence overwrite denied",
    )
    shutil.copyfile(path, target)
    require(digest(target) == digest(path), "Operator evidence copy changed")
    return {"path": name, "sha256": digest(target)}


def write_templates(root, run_id):
    root = safe_root(root)
    inventory = json.loads((root / "inventory.json").read_text())
    rows = list(read_jsonl(root / "manifest.jsonl"))
    candidates = [binding(row, root, run_id, root / "manifest.jsonl") for row in rows]
    values = {
        "authority-template.json": {
            "run_id": run_id,
            "intent": "authorize_local_crop_review",
            "operator_id": None,
            "authority_ref": None,
            "reason": None,
            "synthetic_test": False,
        },
        "inventory-review-template.json": {
            "run_id": run_id,
            "operator_id": None,
            "authority_ref": None,
            "source_inventory_complete": False,
            "reason": None,
            "reviewed_at": None,
            "reviewed_pages": [
                {"source_page": p["source_page"], "source_sha256": p["source_sha256"]}
                for p in inventory["pages"]
            ],
            "visuals": inventory["visuals"],
            "decisions": [
                {
                    "candidate_id": b["candidate_id"],
                    "operator_id": None,
                    "action": "unresolved_ownership",
                    "reason": None,
                }
                for b in candidates
            ],
        },
    }
    for name, value in values.items():
        path = root / name
        require(not path.exists(), "Template overwrite denied")
        path.write_text(json.dumps(value, indent=2) + "\n")
    return {
        "candidate_count": len(candidates),
        "source_page_count": len(inventory["pages"]),
        "complete": False,
        "authority_created": False,
    }


def initialize(root, operator_input, run_id):
    root = safe_root(root)
    value = json.loads(Path(operator_input).read_text())
    require(
        value.get("run_id") == run_id
        and value.get("intent") == "authorize_local_crop_review",
        "Explicit operator authorization intent required",
    )
    require(
        all(
            isinstance(value.get(k), str) and value[k].strip()
            for k in ("operator_id", "authority_ref", "reason")
        ),
        "Operator identity/reference/reason required",
    )
    require(not (root / "authority.json").exists(), "Authority already initialized")
    evidence = _new_evidence(root, operator_input, "operator-authority-input.json")
    authority = {
        "run_id": run_id,
        "trust_boundary": "trusted_local_operator",
        "decision_log": "decisions.jsonl",
        "synthetic_test": value.get("synthetic_test") is True,
        "operators": [
            {
                "operator_id": value["operator_id"],
                "authority_ref": value["authority_ref"],
                "evidence": evidence,
            }
        ],
    }
    (root / "authority.json").write_text(json.dumps(authority, indent=2) + "\n")
    return authority


def finalize(root, operator_input, proposals, run_id):
    root = safe_root(root)
    inventory = json.loads((root / "inventory.json").read_text())
    authority = json.loads((root / "authority.json").read_text())
    value = json.loads(Path(operator_input).read_text())
    require(
        inventory.get("complete") is False
        and not list(read_jsonl(root / "decisions.jsonl")),
        "Review finalization requires unreviewed draft",
    )
    require(
        value.get("run_id") == run_id
        and authority.get("run_id") == run_id
        and value.get("source_inventory_complete") is True,
        "Explicit complete-source assertion required",
    )
    operator = next(
        (
            x
            for x in authority["operators"]
            if x["operator_id"] == value.get("operator_id")
        ),
        None,
    )
    require(
        operator and value.get("authority_ref") == operator["authority_ref"],
        "Unauthorized inventory review",
    )
    read_bound(root, operator["evidence"])
    require(
        isinstance(value.get("reason"), str)
        and value["reason"].strip()
        and isinstance(value.get("reviewed_at"), str)
        and value["reviewed_at"].strip(),
        "Source-review reason/timestamp required",
    )
    for page in inventory["pages"]:
        read_bound(
            root, {"path": page["source_image"], "sha256": page["source_sha256"]}
        )
    pages = read_bound(root, inventory["pages_artifact"])
    read_bound(root, inventory["portions_artifact"])
    numbers = [p.get("page") if p.get("page_number") is None else p["page_number"] for p in read_jsonl(pages)]
    require(
        len(numbers) == len(set(numbers))
        and set(numbers) == {p["source_page"] for p in inventory["pages"]},
        "Incomplete source page inventory",
    )
    expected = [
        {"source_page": p["source_page"], "source_sha256": p["source_sha256"]}
        for p in inventory["pages"]
    ]
    require(
        value.get("reviewed_pages") == expected,
        "Source review must cover exact complete page inventory",
    )
    rows = list(read_jsonl(root / "manifest.jsonl"))
    bindings = [binding(r, root, run_id, root / "manifest.jsonl") for r in rows]
    actions = value.get("decisions", [])
    require(
        len(actions) == len(bindings)
        and {x.get("candidate_id") for x in actions}
        == {b["candidate_id"] for b in bindings},
        "Explicit decision required for every candidate",
    )
    byid = {b["candidate_id"]: b for b in bindings}
    visuals = value.get("visuals", [])
    visual_ids = [c for v in visuals for c in v["candidate_ids"]]
    require(
        all(v["candidate_ids"] for v in visuals)
        and len(visual_ids) == len(set(visual_ids))
        and set(visual_ids) == set(byid),
        "Incomplete visual inventory",
    )
    require(
        all(
            byid[c]["source_page"] == v["source_page"]
            for v in visuals
            for c in v["candidate_ids"]
        ),
        "Visual/source page mismatch",
    )
    for action in actions:
        require(
            action.get("operator_id") == value["operator_id"]
            and action.get("action")
            in ("approve_current_crop", "require_recrop", "unresolved_ownership")
            and isinstance(action.get("reason"), str)
            and action["reason"].strip(),
            "Incomplete/unauthorized human review action",
        )
    incoming = Path(proposals).absolute()
    require(
        incoming.is_file()
        and not any(p.is_symlink() for p in (incoming, *incoming.parents)),
        "Unsafe proposals attachment",
    )
    target = root / "proposals.jsonl"
    require(
        not target.exists() or incoming == target,
        "Proposal attachment overwrite denied",
    )
    native = list(read_jsonl(incoming))
    require(
        len(native) == len(bindings)
        and {x.get("candidate_id") for x in native} == set(byid),
        "Proposal inventory incomplete",
    )
    # Native failures remain a hold even when an operator approves the crop.
    from modules.common.crop_safety import validate_native_proposal

    for row, b in zip(rows, bindings):
        proposal = next(x for x in native if x["candidate_id"] == b["candidate_id"])
        require(proposal.get("binding") == b, "Stale proposal")
        validate_native_proposal(root, proposal, row, root / "manifest.jsonl")
    require(
        not (root / "pending-inventory.json").exists(), "Draft snapshot already exists"
    )
    evidence = _new_evidence(root, operator_input, "operator-source-review-input.json")
    if incoming != target:
        shutil.copyfile(incoming, target)
        require(digest(incoming) == digest(target), "Proposal attachment changed")
    shutil.copyfile(root / "inventory.json", root / "pending-inventory.json")
    inventory.update(
        complete=True,
        operator_id=value["operator_id"],
        authority_ref=value["authority_ref"],
        review_evidence=evidence,
        visuals=value["visuals"],
    )
    events = []
    for index, action in enumerate(actions, 1):
        human_path = root / f"human-review-{index:03d}.json"
        require(not human_path.exists(), "Human review overwrite denied")
        human_path.write_text(json.dumps(action, indent=2) + "\n")
        event = {
            **action,
            "binding": byid[action["candidate_id"]],
            "authority_ref": value["authority_ref"],
            "policy_version": "all-candidate-review-v1",
            "reviewed_at": value["reviewed_at"],
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "supersedes": None,
            "human_input": {"path": human_path.name, "sha256": digest(human_path)},
        }
        event["decision_id"] = object_digest(event)
        events.append(event)
    save_jsonl(root / "decisions.jsonl", events)
    atomic_json(root / "inventory.json", inventory)
    return {
        "run_id": run_id,
        "candidate_count": len(events),
        "source_page_count": len(expected),
        "synthetic_authority": authority.get("synthetic_test") is True,
    }
