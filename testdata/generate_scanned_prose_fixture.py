#!/usr/bin/env python3
"""Generate the repo-owned scanned prose PDF fixture from checked-in source text."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE = ROOT / "scanned-prose-mini.md"
DEFAULT_OUTPUT = ROOT / "scanned-prose-mini.pdf"

PAGE_WIDTH = 1700
PAGE_HEIGHT = 2200
MARGIN_X = 140
MARGIN_Y = 140
LINE_GAP = 18
PARAGRAPH_GAP = 24

TITLE_SIZE = 62
HEADING_SIZE = 50
BODY_SIZE = 44

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
]


def _pick_font_path(override: str | None) -> str | None:
    if override:
        return override
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    return None


def _load_font(size: int, override: str | None = None) -> ImageFont.ImageFont:
    font_path = _pick_font_path(override)
    if font_path:
        return ImageFont.truetype(font_path, size)
    return ImageFont.load_default()


def _parse_source(text: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    paragraph_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph_lines:
            blocks.append(("paragraph", " ".join(paragraph_lines).strip()))
            paragraph_lines.clear()

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            flush_paragraph()
            continue
        if line.startswith("# "):
            flush_paragraph()
            blocks.append(("title", line[2:].strip()))
            continue
        if line.startswith("## "):
            flush_paragraph()
            blocks.append(("heading", line[3:].strip()))
            continue
        paragraph_lines.append(line)

    flush_paragraph()
    return blocks


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    lines = [words[0]]
    for word in words[1:]:
        candidate = f"{lines[-1]} {word}"
        if draw.textlength(candidate, font=font) <= max_width:
            lines[-1] = candidate
        else:
            lines.append(word)
    return lines


def _line_height(draw: ImageDraw.ImageDraw, font: ImageFont.ImageFont) -> int:
    _, top, _, bottom = draw.textbbox((0, 0), "Ag", font=font)
    return bottom - top


def _new_page() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    page = Image.new("L", (PAGE_WIDTH, PAGE_HEIGHT), 250)
    return page, ImageDraw.Draw(page)


def _render_pages(blocks: Iterable[tuple[str, str]], font_path: str | None) -> list[Image.Image]:
    title_font = _load_font(TITLE_SIZE, font_path)
    heading_font = _load_font(HEADING_SIZE, font_path)
    body_font = _load_font(BODY_SIZE, font_path)

    pages: list[Image.Image] = []
    page, draw = _new_page()
    y = MARGIN_Y
    max_width = PAGE_WIDTH - 2 * MARGIN_X

    for kind, text in blocks:
        if kind == "title":
            font = title_font
            gap_after = PARAGRAPH_GAP + 8
        elif kind == "heading":
            font = heading_font
            gap_after = PARAGRAPH_GAP
        else:
            font = body_font
            gap_after = PARAGRAPH_GAP

        lines = _wrap_text(draw, text, font, max_width)
        block_height = len(lines) * (_line_height(draw, font) + LINE_GAP) - LINE_GAP

        if y + block_height > PAGE_HEIGHT - MARGIN_Y:
            pages.append(page)
            page, draw = _new_page()
            y = MARGIN_Y

        for line in lines:
            draw.text((MARGIN_X, y), line, fill=20, font=font)
            y += _line_height(draw, font) + LINE_GAP
        y += gap_after

    pages.append(page)
    return pages


def build_fixture(source_path: Path, output_path: Path, font_path: str | None = None) -> int:
    blocks = _parse_source(source_path.read_text(encoding="utf-8"))
    pages = _render_pages(blocks, font_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pages[0].save(
        output_path,
        "PDF",
        resolution=200.0,
        save_all=True,
        append_images=pages[1:],
    )
    return len(pages)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Checked-in source text")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output PDF path")
    parser.add_argument("--font-path", help="Optional explicit font path")
    args = parser.parse_args()

    page_count = build_fixture(args.source, args.output, args.font_path)
    print(f"Wrote {args.output} ({page_count} pages)")


if __name__ == "__main__":
    main()
