"""Offline crop custody and explicit trusted-local-operator release contracts.

Hashes prove identity, not remote authentication. The authority file is supplied
by the trusted local operator; model proposals never grant review authority.
"""

import hashlib
import json
import math
from pathlib import Path

from PIL import Image

from modules.common.utils import read_jsonl


class CropReviewError(ValueError):
    pass


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def object_digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def require(condition, message):
    if not condition:
        raise CropReviewError(message)


def custody_path(root, value):
    root = Path(root).resolve()
    value = Path(value)
    require(
        not value.is_absolute() and ".." not in value.parts,
        "Custody paths must be relative without traversal",
    )
    path = root / value
    current = root
    for part in value.parts:
        current /= part
        require(not current.is_symlink(), "Symlink in custody path")
    require(path.resolve().is_relative_to(root), "Custody path escape")
    require(path.is_file(), f"Missing custody file: {value}")
    return path


def read_bound(root, entry):
    path = custody_path(root, entry["path"])
    require(
        digest(path) == entry["sha256"], f"Changed custody evidence: {entry['path']}"
    )
    return path


def binding(row, root, run_id, manifest_path):
    require(row.get("run_id") == run_id, "Candidate run mismatch")
    filename = row.get("filename", "")
    require(
        filename and Path(filename).name == filename and filename not in (".", ".."),
        "Unsafe crop filename",
    )
    source = custody_path(root, row["source_image"])
    crop = custody_path(
        root,
        str((Path(manifest_path).parent / "images" / filename).relative_to(Path(root))),
    )
    bbox = row.get("bbox", {})
    require(
        all(type(bbox.get(k)) in (int, float) for k in ("x0", "y0", "x1", "y1")),
        "Invalid crop geometry",
    )
    require(bbox["x1"] > bbox["x0"] and bbox["y1"] > bbox["y0"], "Empty crop geometry")
    with Image.open(source) as image:
        width, height = image.size
    require(
        all(math.isfinite(bbox[k]) for k in ("x0", "y0", "x1", "y1")),
        "Nonfinite crop geometry",
    )
    require(
        0 <= bbox["x0"] < bbox["x1"] <= width
        and 0 <= bbox["y0"] < bbox["y1"] <= height,
        "Crop geometry outside source pixels",
    )
    bound = {
        "run_id": run_id,
        "source_page": row["source_page"],
        "source_image": row["source_image"],
        "source_sha256": digest(source),
        "crop_sha256": digest(crop),
        "bbox": bbox,
        "row_sha256": object_digest(row),
        "source_dimensions": [width, height],
        "coordinate_system": "source_pixels",
    }
    return {"candidate_id": object_digest(bound), **bound}


def evaluate(root, paths, run_id):
    root = Path(root).resolve()
    require(root.is_dir(), "Missing custody root")
    files = {key: read_bound(root, entry) for key, entry in paths.items()}
    require(
        set(files) == {"manifest", "inventory", "proposals", "decisions", "authority"},
        "Incomplete review contract",
    )
    authority = json.loads(files["authority"].read_text())
    require(authority.get("run_id") == run_id, "Authority run mismatch")
    require(
        authority.get("trust_boundary") == "trusted_local_operator",
        "Explicit local operator authority required",
    )
    require(
        authority.get("decision_log") == paths["decisions"]["path"],
        "Decision log differs from operator authority designation",
    )
    operators = authority.get("operators", [])
    require(
        operators and len({x["operator_id"] for x in operators}) == len(operators),
        "Invalid operator authority",
    )
    byoperator = {x["operator_id"]: x for x in operators}
    for op in operators:
        require(op.get("authority_ref"), "Missing authority reference")
        read_bound(root, op["evidence"])
    inventory = json.loads(files["inventory"].read_text())
    require(
        inventory.get("run_id") == run_id and inventory.get("complete") is True,
        "Source inventory not explicitly complete",
    )
    op = byoperator.get(inventory.get("operator_id"))
    require(
        op is not None and inventory.get("authority_ref") == op["authority_ref"],
        "Unauthorized inventory assertion",
    )
    read_bound(root, inventory["review_evidence"])
    pages_path = read_bound(root, inventory["pages_artifact"])
    portions_path = read_bound(root, inventory["portions_artifact"])
    pages = list(read_jsonl(pages_path))
    actual_page_numbers = [x.get("page_number", x.get("page")) for x in pages]
    require(
        len(actual_page_numbers) == len(set(actual_page_numbers)),
        "Duplicate source pages",
    )
    source_pages = inventory["pages"]
    require(
        len(source_pages) == len({x["source_page"] for x in source_pages}),
        "Duplicate inventory pages",
    )
    require(
        set(actual_page_numbers) == {x["source_page"] for x in source_pages},
        "Incomplete source page inventory",
    )
    for page in source_pages:
        read_bound(
            root, {"path": page["source_image"], "sha256": page["source_sha256"]}
        )
    rows = list(read_jsonl(files["manifest"]))
    require(rows, "Empty candidate manifest cannot release")
    bindings = [binding(row, root, run_id, files["manifest"]) for row in rows]
    ids = [x["candidate_id"] for x in bindings]
    require(
        len(ids) == len(set(ids)) and len({r["filename"] for r in rows}) == len(rows),
        "Duplicate candidates/filenames",
    )
    visuals = inventory["visuals"]
    require(
        len(visuals) == len({x["visual_id"] for x in visuals}),
        "Duplicate visual inventory",
    )
    inventory_ids = [c for v in visuals for c in v["candidate_ids"]]
    require(
        all(v["candidate_ids"] for v in visuals)
        and len(inventory_ids) == len(set(inventory_ids))
        and set(inventory_ids) == set(ids),
        "Incomplete visual/candidate inventory",
    )
    pages_by_number = {x["source_page"]: x for x in source_pages}
    visual_by_id = {c: v for v in visuals for c in v["candidate_ids"]}
    for b in bindings:
        page = pages_by_number.get(b["source_page"])
        require(
            page is not None
            and b["source_image"] == page["source_image"]
            and b["source_sha256"] == page["source_sha256"],
            "Candidate source outside reviewed inventory",
        )
        require(
            visual_by_id[b["candidate_id"]]["source_page"] == b["source_page"],
            "Visual/page binding mismatch",
        )
    proposals = list(read_jsonl(files["proposals"]))
    require(
        len(proposals) == len(ids)
        and {x.get("candidate_id") for x in proposals} == set(ids),
        "Incomplete/duplicate proposal inventory",
    )
    expected = {x["candidate_id"]: x for x in bindings}
    for proposal in proposals:
        require(
            proposal.get("binding") == expected[proposal["candidate_id"]],
            "Stale model proposal binding",
        )
        require(proposal.get("verdict") in ("pass", "fail"), "Invalid proposal verdict")
        require(
            proposal.get("origin") in ("saved_evaluation_replay", "synthetic_test"),
            "Offline proposal origin required",
        )
        read_bound(root, proposal["receipt"])
    decisions = list(read_jsonl(files["decisions"]))
    require(
        {x.get("candidate_id") for x in decisions} == set(ids),
        "Missing/unknown review decision",
    )
    latest = {}
    event_ids = set()
    for decision in decisions:
        event_id = decision.get("decision_id")
        require(event_id and event_id not in event_ids, "Duplicate review event")
        event_ids.add(event_id)
        previous = latest.get(decision["candidate_id"])
        require(
            decision.get("supersedes")
            == (previous.get("decision_id") if previous else None),
            "Conflicting review requires explicit supersession",
        )
        latest[decision["candidate_id"]] = decision
        require(
            decision.get("binding") == expected[decision["candidate_id"]],
            "Stale reviewer decision",
        )
        op = byoperator.get(decision.get("operator_id"))
        require(
            op is not None and decision.get("authority_ref") == op["authority_ref"],
            "Unauthorized reviewer",
        )
        require(
            decision.get("reason")
            and decision.get("reviewed_at")
            and decision.get("policy_version") == "all-candidate-review-v1",
            "Incomplete review evidence",
        )
        evidence = read_bound(root, decision["human_input"])
        human = json.loads(evidence.read_text())
        require(
            all(
                human.get(k) == decision.get(k)
                for k in ("candidate_id", "operator_id", "action", "reason")
            ),
            "Human input/event mismatch",
        )
    for decision in latest.values():
        require(
            decision.get("action") == "approve_current_crop",
            "Candidate held: recrop or unresolved ownership",
        )
    return {
        "rows": rows,
        "bindings": bindings,
        "inventory": inventory,
        "synthetic_authority": authority.get("synthetic_test") is True,
        "expected_filenames": [r["filename"] for r in rows],
        "pages_path": str(pages_path),
        "portions_path": str(portions_path),
    }


def bound_paths(root, named_paths):
    root = Path(root).resolve()
    result = {}
    for key, value in named_paths.items():
        path = Path(value).absolute()
        require(path.is_relative_to(root), "Input evidence outside custody")
        relative = str(path.relative_to(root))
        custody_path(root, relative)
        result[key] = {"path": relative, "sha256": digest(path)}
    return result


def protect_destinations(protected, destinations):
    for value in destinations:
        if value is None:
            continue
        dest = Path(value).resolve()
        for retained in protected:
            retained = Path(retained).resolve()
            require(
                not dest.is_relative_to(retained) and not retained.is_relative_to(dest),
                "Output aliases protected custody/release",
            )
            if dest.exists() and dest.is_file():
                for original in retained.rglob("*"):
                    require(
                        not original.is_file() or not dest.samefile(original),
                        "Output inode aliases protected evidence",
                    )


def validate_release_for_build(
    manifest_path,
    receipt_path,
    expected_run_id=None,
    *,
    output_dir=None,
    images_dir=None,
    output_manifest_path=None,
    pages_path=None,
    portions_path=None,
    state_file=None,
    progress_file=None,
):
    receipt_path = Path(receipt_path)
    require(
        receipt_path.is_file() and not receipt_path.is_symlink(),
        "Missing or symlinked release receipt",
    )
    receipt = json.loads(receipt_path.read_text())
    require(
        expected_run_id and receipt.get("run_id") == expected_run_id,
        "Release run mismatch",
    )
    root = Path(receipt["custody_root"]).resolve()
    verified = evaluate(root, receipt["inputs"], expected_run_id)
    manifest = Path(manifest_path).resolve()
    require(
        str(manifest) == receipt["released_manifest"]
        and digest(manifest) == receipt["released_manifest_sha256"],
        "Released manifest mismatch",
    )
    require(
        list(read_jsonl(manifest)) == verified["rows"],
        "Released candidate rows changed",
    )
    for row, b in zip(verified["rows"], verified["bindings"]):
        asset = manifest.parent / "images" / row["filename"]
        require(
            asset.is_file()
            and not asset.is_symlink()
            and digest(asset) == b["crop_sha256"],
            "Released crop bytes changed",
        )
    require(not (manifest.parent / "images").is_symlink(), "Symlinked release images")
    if pages_path is not None:
        require(
            digest(pages_path) == digest(verified["pages_path"]),
            "Builder pages outside reviewed source scope",
        )
    if portions_path is not None:
        require(
            digest(portions_path) == digest(verified["portions_path"]),
            "Builder portions outside reviewed scope",
        )
    protected = [root, manifest.parent]
    protect_destinations(
        protected,
        [output_dir, images_dir, output_manifest_path, state_file, progress_file],
    )
    if output_dir is not None and images_dir is not None:
        require(
            Path(images_dir).resolve().is_relative_to(Path(output_dir).resolve())
            and Path(images_dir).resolve() != Path(output_dir).resolve(),
            "Images output escapes HTML directory",
        )
    return {**verified, "protected_roots": [str(x) for x in protected]}
