"""Release only completely reviewed offline crop inventories; no model calls."""

import argparse
import json
import shutil
from pathlib import Path

from modules.common.crop_review import (
    bound_paths,
    digest,
    evaluate,
    protect_destinations,
    require,
)
from modules.common.utils import read_jsonl, save_jsonl


def release(root, named_paths, out, run_id):
    root = Path(root).resolve()
    out = Path(out).resolve()
    protect_destinations([root], [out.parent])
    require(
        not out.parent.exists() or not any(out.parent.iterdir()),
        "Release requires a new or empty output directory",
    )
    inputs = bound_paths(root, named_paths)
    reviewed = evaluate(root, inputs, run_id)
    out.parent.mkdir(parents=True, exist_ok=True)
    images = out.parent / "images"
    images.mkdir()
    for row in reviewed["rows"]:
        shutil.copyfile(
            Path(named_paths["manifest"]).parent / "images" / row["filename"],
            images / row["filename"],
        )
    save_jsonl(out, reviewed["rows"])
    receipt = {
        "schema_version": "crop_review_release_v1",
        "run_id": run_id,
        "custody_root": str(root),
        "inputs": inputs,
        "released_manifest": str(out),
        "released_manifest_sha256": digest(out),
        "synthetic_authority": reviewed["synthetic_authority"],
        "candidate_count": len(reviewed["rows"]),
    }
    (out.parent / "crop_review_release.json").write_text(
        json.dumps(receipt, indent=2) + "\n"
    )
    return receipt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--custody-root", required=True)
    for name in ("manifest", "inventory", "proposals", "decisions", "authority"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--run-id", required=True)
    p.add_argument("--state-file")
    p.add_argument("--progress-file")
    args = p.parse_args()
    try:
        release(
            args.custody_root,
            {
                k: getattr(args, k)
                for k in (
                    "manifest",
                    "inventory",
                    "proposals",
                    "decisions",
                    "authority",
                )
            },
            args.out,
            args.run_id,
        )
    except (ValueError, KeyError, TypeError, OSError) as exc:
        destination = Path(args.out).absolute().parent
        try:
            protect_destinations([Path(args.custody_root).resolve()], [destination])
            require(
                not destination.exists() or not any(destination.iterdir()),
                "Held diagnostic requires empty stage",
            )
            count = None
            try:
                count = len(list(read_jsonl(args.manifest)))
            except (ValueError, OSError):
                pass
            destination.mkdir(parents=True, exist_ok=True)
            (destination / "crop_review_held.json").write_text(
                json.dumps(
                    {
                        "schema_version": "crop_review_held_v1",
                        "run_id": args.run_id,
                        "disposition": "hold_publication",
                        "released_count": 0,
                        "candidate_count": count,
                        "held_count": count,
                        "reason": str(exc),
                        "source_deletion_authorized": False,
                    },
                    indent=2,
                )
                + "\n"
            )
        except (ValueError, OSError):
            pass
        p.error(str(exc))


if __name__ == "__main__":
    main()
