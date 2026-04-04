#!/usr/bin/env python3
"""Generate a tiny synthetic handwritten-notes fixture from checked-in transcript text."""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


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


@dataclass(frozen=True)
class RenderPreset:
    name: str
    page_width: int = 1700
    page_height: int = 2200
    margin_x: int = 190
    margin_y: int = 160
    line_gap: int = 22
    blank_line_gap: int = 34
    font_size: int = 62
    background: int = 247
    ink: int = 34
    x_jitter: int = 10
    y_jitter: int = 3
    paragraph_gap: int = 6
    noise_alpha: float = 0.0
    blur_radius: float = 0.0
    rotate_degrees: float = 0.0

    @property
    def max_text_width(self) -> int:
        return self.page_width - 2 * self.margin_x


PRESETS = {
    "legible": RenderPreset(name="legible"),
    "faded": RenderPreset(
        name="faded",
        margin_x=165,
        margin_y=145,
        line_gap=10,
        blank_line_gap=18,
        font_size=50,
        background=232,
        ink=92,
        x_jitter=26,
        y_jitter=8,
        paragraph_gap=2,
        noise_alpha=0.08,
        blur_radius=0.7,
        rotate_degrees=1.8,
    ),
    "rough": RenderPreset(
        name="rough",
        margin_x=175,
        margin_y=150,
        line_gap=14,
        blank_line_gap=24,
        font_size=54,
        background=238,
        ink=52,
        x_jitter=22,
        y_jitter=7,
        paragraph_gap=4,
        noise_alpha=0.05,
        blur_radius=0.45,
        rotate_degrees=1.25,
    ),
}


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


def _apply_noise(page: Image.Image, preset: RenderPreset) -> Image.Image:
    if preset.noise_alpha <= 0:
        return page
    noise = Image.effect_noise(page.size, 14.0).convert("L")
    return Image.blend(page, noise, preset.noise_alpha)


def _render_page(lines: list[str], font: ImageFont.ImageFont, seed: int, preset: RenderPreset) -> Image.Image:
    rng = random.Random(seed)
    page = Image.new("L", (preset.page_width, preset.page_height), preset.background)
    draw = ImageDraw.Draw(page)
    y = preset.margin_y
    line_height = _line_height(draw, font)

    for raw_line in lines:
        if not raw_line.strip():
            y += preset.blank_line_gap
            continue
        wrapped = _wrap_line(draw, raw_line, font, preset.max_text_width)
        for idx, segment in enumerate(wrapped):
            x_jitter = rng.randint(-preset.x_jitter, preset.x_jitter)
            y_jitter = rng.randint(-preset.y_jitter, preset.y_jitter)
            draw.text(
                (preset.margin_x + x_jitter, y + y_jitter),
                segment,
                fill=preset.ink,
                font=font,
            )
            y += line_height + preset.line_gap + (2 if idx == len(wrapped) - 1 else 0)
        y += preset.paragraph_gap

    if preset.rotate_degrees > 0:
        angle = rng.uniform(-preset.rotate_degrees, preset.rotate_degrees)
        page = page.rotate(angle, resample=Image.Resampling.BICUBIC, fillcolor=preset.background)
    if preset.blur_radius > 0:
        page = page.filter(ImageFilter.GaussianBlur(preset.blur_radius))
    page = _apply_noise(page, preset)

    return page


def build_fixture(
    transcript_path: Path,
    images_dir: Path,
    pdf_path: Path,
    preset_name: str = "legible",
    font_path: str | None = None,
) -> int:
    pages = _parse_pages(transcript_path.read_text(encoding="utf-8"))
    try:
        preset = PRESETS[preset_name]
    except KeyError as exc:
        raise ValueError(f"Unknown preset: {preset_name}") from exc
    font = _load_font(preset.font_size, font_path)

    rendered_pages = []
    images_dir.mkdir(parents=True, exist_ok=True)
    for existing in images_dir.glob("*.png"):
        existing.unlink()

    for idx, lines in enumerate(pages, start=1):
        image = _render_page(lines, font, seed=idx, preset=preset)
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
    parser.add_argument("--preset", choices=sorted(PRESETS), default="legible")
    parser.add_argument("--font-path", default=None)
    args = parser.parse_args()

    page_count = build_fixture(
        transcript_path=args.transcript,
        images_dir=args.images_dir,
        pdf_path=args.pdf,
        preset_name=args.preset,
        font_path=args.font_path,
    )
    print(f"Wrote {args.images_dir} and {args.pdf} ({page_count} pages, preset={args.preset})")


if __name__ == "__main__":
    main()
