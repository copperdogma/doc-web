"""Prepare native crop proposals for explicit local source review (offline by default)."""

import argparse
import json

from modules.common.crop_review_setup import (
    attach_proposals,
    finalize,
    initialize,
    write_templates,
)
from modules.common.crop_safety_custody import prepare_custody
from tools.crop_review import show_html


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("prepare", "initialize", "finalize", "show"))
    p.add_argument("--custody-root", required=True)
    p.add_argument("--run-id", required=True)
    for name in (
        "manifest",
        "pages",
        "portions",
        "source-map",
        "source-root",
        "operator-input",
        "proposals",
        "html-out",
    ):
        p.add_argument("--" + name)
    a = p.parse_args()
    try:
        if a.command == "prepare":
            result = prepare_custody(
                a.manifest,
                a.pages,
                a.portions,
                a.source_map,
                a.source_root,
                a.custody_root,
                a.run_id,
            )
            result.update(write_templates(a.custody_root, a.run_id))
        elif a.command == "initialize":
            result = initialize(a.custody_root, a.operator_input, a.run_id)
        elif a.command == "finalize":
            result = finalize(a.custody_root, a.operator_input, a.proposals, a.run_id)
        else:
            if a.proposals:
                attach_proposals(a.custody_root, a.proposals, a.run_id)
            result = {"display": str(show_html(a.custody_root, a.manifest, a.html_out))}
        print(json.dumps(result, indent=2))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        p.error(str(exc))


if __name__ == "__main__":
    main()
