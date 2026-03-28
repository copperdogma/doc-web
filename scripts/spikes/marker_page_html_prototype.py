#!/usr/bin/env python3
"""
Normalize Marker lite-api JSON output into inspectable doc-web surfaces.

This remains a spike wrapper, but the real normalization logic now lives in
`modules.common.marker_page_html` so the maintained Story 168 module and this
prototype stay on the same code path.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from modules.common.marker_page_html import (
    normalize_marker_document,
    read_json,
    utc_now,
    write_marker_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-pdf", type=Path, required=True)
    parser.add_argument("--marker-json", type=Path, required=True)
    parser.add_argument("--marker-meta", type=Path)
    parser.add_argument("--pdftotext", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--run-id", default="story166-marker-page-html-r1")
    parser.add_argument("--module-id", default="marker_page_html_prototype")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    page_rows, block_rows, bundle, runtime_trace, summary, normalization_report = normalize_marker_document(
        read_json(args.marker_json),
        input_pdf=args.input_pdf,
        marker_json=args.marker_json,
        marker_meta=args.marker_meta,
        run_id=args.run_id,
        module_id=args.module_id,
        created_at=utc_now(),
        pdftotext_text=args.pdftotext.read_text(encoding="utf-8"),
        processing_step=f"{args.module_id}.page_html_v1",
    )
    write_marker_outputs(
        args.outdir,
        artifact_name="pages_html.jsonl",
        page_rows=page_rows,
        block_rows=block_rows,
        bundle=bundle,
        runtime_trace=runtime_trace,
        summary=summary,
        normalization_report=normalization_report,
    )
    print(json.dumps(summary["signals"], indent=2))
    print(f"Summary written to {args.outdir / 'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
