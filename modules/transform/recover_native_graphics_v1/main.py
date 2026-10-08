#!/usr/bin/env python3
"""Supplement retained crops with opt-in, source-native catalog occurrences."""
from __future__ import annotations

import argparse
from pathlib import Path

from modules.common.native_catalog_graphics import POLICY_ID, recover_native_graphics
from modules.common.utils import ProgressLogger, read_jsonl, save_json, save_jsonl

MODULE_ID = "recover_native_graphics_v1"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--pages", required=True)
    parser.add_argument("--physical-pages", required=True)
    parser.add_argument("--existing-crops", required=True)
    parser.add_argument("--inclusion-policy", required=True, choices=[POLICY_ID])
    parser.add_argument("--out", required=True)
    parser.add_argument("--run-id")
    parser.add_argument("--state-file")
    parser.add_argument("--progress-file")
    args = parser.parse_args()
    out = Path(args.out)
    if out.exists():
        raise ValueError("supplement manifest must be new; retained inputs are immutable")
    logger = ProgressLogger(state_path=args.state_file, progress_path=args.progress_file, run_id=args.run_id)
    logger.log("transform", "running", message="Recovering native catalog occurrences offline", module_id=MODULE_ID)
    rows, report = recover_native_graphics(
        pdf_path=args.pdf, pages=list(read_jsonl(args.pages)),
        physical_pages=list(read_jsonl(args.physical_pages)),
        existing_crops=list(read_jsonl(args.existing_crops)),
        existing_images=Path(args.existing_crops).parent / "images", output_images=out.parent / "images",
        inclusion_policy=args.inclusion_policy, run_id=args.run_id,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    save_jsonl(str(out), rows)
    report_path = out.with_name("native_graphics_inventory.json")
    save_json(str(report_path), report)
    logger.log("transform", "done", message="Offline native graphics supplement complete", artifact=str(out),
               module_id=MODULE_ID, extra={"inventory": str(report_path), "summary": report["summary"]})


if __name__ == "__main__":
    main()
