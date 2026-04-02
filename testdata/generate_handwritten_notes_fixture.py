#!/usr/bin/env python3
"""Generate a tiny synthetic handwritten-notes fixture from checked-in transcript text."""

from __future__ import annotations

import argparse
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
DEFAULT_TRANSCRIPT = ROOT / "handwritten-notes-mini.txt"
DEFAULT_IMAGES_DIR = ROOT / "handwritten-notes-mini-images"
DEFAULT_PDF = ROOT / "handwritten-notes-mini.pdf"

PAGE_WIDTH = 1700
PAGE_HEIGHT = 2200
MARGIN_X = 190
MARGIN_Y = 160
MAX_TEXT_WIDTH = PAGE_WIDTH - 2 * MARGIN_X
LINE_GAP = 22
BLANK_LINE_GAP = 34
FONT_SIZE = 62
BACKGROUND = 247
INK = 34
PAGE_SEPARATOR = "===PAGE==="

FONT_CANDIDATES = [
    "/System/Library/Fonts/Noteworthy.ttc",
    "/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf",
    "/Library/Fonts/Bradley Hand ITC TT-Bold",
    "/Library/Fonts/SchoolHouse Cursive B.suit",
    "/System/Library/Fonts/Supplemental/Comic Sans MS.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
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


def _parse_pages(text: str) -> list[list[str]]:
    pages: list[list[str]] = []
    for chunk in text.split(PAGE_SEPARATOR):
        lines = [line.rstrip() for line in chunk.strip().splitlines()]
        if lines:
            pages.append(lines)
    if not pages:
        raise ValueError("Transcript did not contain any pages")
    return pages


def _wrap_line(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    if not text:
        return [""]
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


def _render_page(lines: list[str], font: ImageFont.ImageFont, seed: int) -> Image.Image:
    rng = random.Random(seed)
    page = Image.new("L", (PAGE_WIDTH, PAGE_HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(page)
    y = MARGIN_Y
    line_height = _line_height(draw, font)

    for raw_line in lines:
        if not raw_line.strip():
            y += BLANK_LINE_GAP
            continue
        wrapped = _wrap_line(draw, raw_line, font, MAX_TEXT_WIDTH)
        for idx, segment in enumerate(wrapped):
            x_jitter = rng.randint(-10, 10)
            y_jitter = rng.randint(-3, 3)
            draw.text((MARGIN_X + x_jitter, y + y_jitter), segment, fill=INK, font=font)
            y += line_height + LINE_GAP + (2 if idx == len(wrapped) - 1 else 0)
        y += 6

    return page


def build_fixture(
    transcript_path: Path,
    images_dir: Path,
    pdf_path: Path,
    font_path: str | None = None,
) -> int:
    pages = _parse_pages(transcript_path.read_text(encoding="utf-8"))
    font = _load_font(FONT_SIZE, font_path)

    rendered_pages = []
    images_dir.mkdir(parents=True, exist_ok=True)
    for existing in images_dir.glob("*.png"):
        existing.unlink()

    for idx, lines in enumerate(pages, start=1):
        image = _render_page(lines, font, seed=idx)
        image_path = images_dir / f"page-{idx:03d}.png"
        image.save(image_path, "PNG")
        rendered_pages.append(image)

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    rendered_pages[0].save(
        pdf_path,
        "PDF",
        resolution=200.0,
        save_all=True,
        append_images=rendered_pages[1:],
    )
    return len(rendered_pages)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transcript", type=Path, default=DEFAULT_TRANSCRIPT)
    parser.add_argument("--images-dir", type=Path, default=DEFAULT_IMAGES_DIR)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--font-path", default=None)
    args = parser.parse_args()

    page_count = build_fixture(
        transcript_path=args.transcript,
        images_dir=args.images_dir,
        pdf_path=args.pdf,
        font_path=args.font_path,
    )
    print(f"Wrote {args.images_dir} and {args.pdf} ({page_count} pages)")


if __name__ == "__main__":
    main()
