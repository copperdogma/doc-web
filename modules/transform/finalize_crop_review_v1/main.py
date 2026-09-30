"""Consume explicit operator-authored inputs; never manufacture source approval."""

import argparse
import json
from pathlib import Path

from modules.common.crop_review import require
from modules.common.crop_review_setup import finalize, initialize


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in (
        "custody-root",
        "operator-authority-input",
        "operator-review-input",
        "proposals",
        "out",
        "run-id",
    ):
        p.add_argument("--" + name, required=True)
    p.add_argument("--state-file")
    p.add_argument("--progress-file")
    a = p.parse_args()
    try:
        out = Path(a.out).absolute()
        require(
            not out.exists()
            and ".." not in out.parts
            and not any(p.is_symlink() for p in (out, *out.parents))
            and not out.resolve().is_relative_to(Path(a.custody_root).resolve()),
            "Unsafe finalization output",
        )
        initialize(a.custody_root, a.operator_authority_input, a.run_id)
        result = finalize(
            a.custody_root, a.operator_review_input, a.proposals, a.run_id
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2) + "\n")
    except (ValueError, KeyError, TypeError, OSError) as exc:
        p.error(str(exc))


if __name__ == "__main__":
    main()
