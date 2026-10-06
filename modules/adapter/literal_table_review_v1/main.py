"""Qualify initial page HTML table text against source-only image review."""

import argparse
from pathlib import Path

from modules.common.literal_table_review import review_literal_tables
from modules.common.utils import ProgressLogger, read_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("--pages", help="page_html_v1 JSONL input")
    input_group.add_argument("--inputs", nargs="+", help="Driver-compatible page artifact inputs")
    parser.add_argument("--out", required=True, help="Output page_html_v1 JSONL path")
    parser.add_argument("--model", default="gpt-6-astra")
    parser.add_argument("--max-pages", type=int, default=3)
    parser.add_argument("--max-tables", type=int, default=8)
    parser.add_argument("--max-requests", type=int, default=10)
    parser.add_argument("--budget-usd", type=float, default=15.0)
    parser.add_argument("--run-id", required=True, help="Current driver run ID")
    parser.add_argument("--state-file")
    parser.add_argument("--progress-file")
    args = parser.parse_args()

    if args.inputs and len(args.inputs) != 1:
        parser.error("literal table review requires exactly one page artifact input")
    pages_path = args.pages or (args.inputs[0] if args.inputs else None)
    if not pages_path:
        parser.error("--pages or --inputs is required")
    logger = ProgressLogger(
        state_path=args.state_file,
        progress_path=args.progress_file,
        run_id=args.run_id,
    )
    logger.log("literal_table_review", "running", message=f"Reviewing {pages_path}")
    rows = list(read_jsonl(pages_path))
    reviewed = review_literal_tables(
        rows,
        out_path=Path(args.out),
        run_id=args.run_id,
        model=args.model,
        max_pages=args.max_pages,
        max_tables=args.max_tables,
        max_requests=args.max_requests,
        budget_usd=args.budget_usd,
    )
    unresolved = sum(
        row.get("literal_fidelity", {}).get("status") != "verified"
        for row in reviewed
    )
    if unresolved:
        logger.log(
            "literal_table_review",
            "failed",
            current=len(reviewed) - unresolved,
            total=len(reviewed),
            artifact=str(Path(args.out).resolve()),
            message=(
                f"Saved {len(reviewed)} page reviews; {unresolved} page(s) remain "
                "unresolved. Inspect the literal fidelity reports before continuing."
            ),
        )
        raise SystemExit(2)
    logger.log(
        "literal_table_review",
        "done",
        current=len(reviewed),
        total=len(reviewed),
        artifact=str(Path(args.out).resolve()),
        message=f"Verified complete source agreement for {len(reviewed)} page(s)",
    )


if __name__ == "__main__":
    main()
