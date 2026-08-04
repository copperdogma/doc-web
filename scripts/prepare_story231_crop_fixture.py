#!/usr/bin/env python3
"""Materialize Story 231's bounded crop fixture from canonical b64 sources."""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schemas import PageHtml  # noqa: E402


SOURCE_DIR = ROOT / "benchmarks" / "input" / "source-pages-b64"
DEFAULT_OUTPUT_DIR = ROOT / "output" / "fixtures" / "story231-crop-runtime"

CASES = (
    {
        "key": "Image000",
        "page": 1,
        "images": [
            {
                "alt": "Gold foil illustration of a covered wagon traveling across a prairie landscape with rolling hills, clouds, and a tree",
                "count": 1,
            }
        ],
    },
    {
        "key": "Image011",
        "page": 12,
        "images": [
            {"alt": "Celebrate Saskatchewan 1905-1980 logo", "count": 1},
            {"alt": "Official Seal", "count": 1},
            {"alt": "Signature of Gordon MacMurchy", "count": 1},
            {"alt": "Signature of Ed Tchorzewski", "count": 1},
        ],
    },
    {
        "key": "Image121",
        "page": 122,
        "images": [
            {"alt": "Large group of people outdoors", "count": 1},
            {"alt": "Two men standing", "count": 1},
            {"alt": "Woman seated", "count": 1},
        ],
    },
    {
        "key": "Image124",
        "page": 125,
        "images": [
            {
                "alt": "Line drawing of a covered wagon pulled by two oxen, with two people sitting at the front.",
                "count": 1,
            },
        ],
    },
)


def _decode_data_uri(value: str) -> bytes:
    header, encoded = value.strip().split(",", 1)
    if not header.startswith("data:image/") or ";base64" not in header:
        raise ValueError("fixture must be an image base64 data URI")
    return base64.b64decode(encoded, validate=True)


def prepare(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for case in CASES:
        source = SOURCE_DIR / f"{case['key']}.b64.txt"
        image_path = (output_dir / f"{case['key']}.jpg").resolve()
        image_path.write_bytes(_decode_data_uri(source.read_text(encoding="utf-8")))
        page = int(case["page"])
        row = PageHtml(
            module_id="story231_fixture",
            source=[str(source.relative_to(ROOT))],
            page=page,
            page_number=page,
            original_page_number=page,
            image=str(image_path),
            ocr_quality=1.0,
            ocr_integrity=1.0,
            html="".join(
                f'<figure><img alt="{item["alt"]}"></figure>\n'
                for item in case["images"]
            ),
            images=case["images"],
        )
        rows.append(row.model_dump(exclude_none=True))

    manifest = output_dir / "pages_html.jsonl"
    manifest.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    print(f"Prepared {len(rows)} Story 231 crop pages at {manifest}")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    prepare(args.output_dir.resolve())


if __name__ == "__main__":
    main()
