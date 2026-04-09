#!/usr/bin/env python3
"""
Wrap a checked HTML snapshot into a single page_html_v1 row.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from schemas import PageHtml
from modules.common.utils import ProgressLogger, ensure_dir, save_jsonl, utc_now


MODULE_ID = "web_page_html_intake_v1"
SCHEMA_VERSION = "page_html_v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a checked HTML snapshot into a single page_html_v1 artifact."
    )
    parser.add_argument("--html", required=True, help="Path to the input HTML snapshot")
    parser.add_argument("--outdir", required=True, help="Output directory")
    parser.add_argument("--out", default="pages_html.jsonl", help="Output page_html_v1 artifact name")
    parser.add_argument(
        "--source-metadata",
        default=None,
        help="Optional JSON sidecar describing the captured source URL and notes",
    )
    parser.add_argument("--progress-file", help="Path to pipeline_events.jsonl")
    parser.add_argument("--state-file", help="Path to pipeline_state.json")
    parser.add_argument("--run-id", help="Run identifier for logging")
    return parser.parse_args()


def _load_source_metadata(html_path: Path, explicit_path: str | None) -> dict[str, Any]:
    if explicit_path:
        metadata_path = Path(explicit_path)
    else:
        metadata_path = html_path.with_suffix(".source.json")
    if not metadata_path.exists():
        return {}
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected object JSON in source metadata: {metadata_path}")
    return payload


def _extract_body_html(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html, "html.parser")
    root = soup.body if soup.body is not None else soup
    for tag in root.find_all(["script", "noscript", "template"]):
        tag.decompose()
    body_html = "".join(str(child) for child in root.contents).strip()
    return body_html or raw_html.strip()


def _build_sources(html_path: Path, metadata: dict[str, Any]) -> list[str]:
    sources: list[str] = [str(html_path.resolve())]
    source_url = str(metadata.get("source_url") or metadata.get("url") or "").strip()
    if source_url:
        sources.append(source_url)
    return sources


def main() -> None:
    args = parse_args()
    logger = ProgressLogger(
        state_path=args.state_file,
        progress_path=args.progress_file,
        run_id=args.run_id,
    )

    html_path = Path(args.html).resolve()
    if not html_path.exists():
        raise SystemExit(f"HTML snapshot not found: {html_path}")

    ensure_dir(args.outdir)
    logger.log(
        "extract",
        "running",
        message=f"Loading checked HTML snapshot {html_path.name}",
        module_id=MODULE_ID,
        schema_version=SCHEMA_VERSION,
    )

    raw_html = html_path.read_text(encoding="utf-8")
    html = _extract_body_html(raw_html)
    metadata = _load_source_metadata(html_path, args.source_metadata)

    row = PageHtml(
        module_id=MODULE_ID,
        run_id=args.run_id,
        source=_build_sources(html_path, metadata),
        created_at=utc_now(),
        page=1,
        page_number=1,
        original_page_number=1,
        raw_html=raw_html,
        html=html,
        printed_page_number=None,
        printed_page_number_text=None,
        printed_page_number_inferred=False,
    ).model_dump()

    out_path = Path(args.outdir) / args.out
    save_jsonl(str(out_path), [row])
    logger.log(
        "extract",
        "done",
        current=1,
        total=1,
        message=f"Wrote 1 checked HTML snapshot row to {out_path}",
        artifact=str(out_path),
        module_id=MODULE_ID,
        schema_version=SCHEMA_VERSION,
        extra={
            "input_html": str(html_path),
            "source_url": metadata.get("source_url") or metadata.get("url"),
        },
    )


if __name__ == "__main__":
    main()
