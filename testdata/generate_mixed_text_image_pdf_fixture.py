#!/usr/bin/env python3
"""Generate a PDF with page 1 text-layer content and page 2 image-only content."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE = ROOT / "mixed-text-image-mini.source.json"
DEFAULT_OUTPUT = ROOT / "mixed-text-image-mini.pdf"
FIXTURE_CREATION_DATE = datetime(2026, 1, 1, tzinfo=timezone.utc)

sys.path.insert(0, str((ROOT / "vendor").resolve()))
from fpdf import FPDF  # noqa: E402


def _font(size: int) -> ImageFont.ImageFont:
    return ImageFont.load_default(size=size)


def _render_image_page(text: str, output_path: Path) -> None:
    image = Image.new("RGB", (1700, 2200), "white")
    draw = ImageDraw.Draw(image)
    title_font = _font(82)
    body_font = _font(58)
    draw.text((150, 180), "Image-Only Page Two", fill="black", font=title_font)

    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=body_font) <= 1350:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)

    y = 360
    for line in lines:
        draw.text((150, y), line, fill="black", font=body_font)
        y += 86
    image.save(output_path)


def build_fixture(source_path: Path, output_path: Path) -> int:
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    pages = payload["pages"]
    pdf = FPDF(format="letter")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_creation_date(FIXTURE_CREATION_DATE)
    pdf.set_title(payload["title"])
    pdf.set_author("doc-forge")

    pdf.add_page()
    pdf.set_font("Helvetica", size=13)
    pdf.multi_cell(0, 7, text=pages[0]["text"])

    with TemporaryDirectory(prefix="doc-web-mixed-pdf-") as temp_dir:
        image_path = Path(temp_dir) / "page-002.png"
        _render_image_page(pages[1]["text"], image_path)
        pdf.add_page()
        pdf.image(str(image_path), x=16, y=18, w=184)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    return pdf.page_no()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    page_count = build_fixture(args.source, args.output)
    print(f"Wrote {args.output} ({page_count} pages)")


if __name__ == "__main__":
    main()
