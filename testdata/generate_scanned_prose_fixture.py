#!/usr/bin/env python3
"""Generate repo-owned scanned prose PDF fixtures from checked-in source text."""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE = ROOT / "scanned-prose-mini.md"
DEFAULT_OUTPUTS = {
    "clean": ROOT / "scanned-prose-mini.pdf",
    "degraded": ROOT / "scanned-prose-degraded.pdf",
}

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
]


@dataclass(frozen=True)
class RenderPreset:
    name: str
    page_width: int = 1700
    page_height: int = 2200
    margin_x: int = 140
    margin_y: int = 140
    line_gap: int = 18
    paragraph_gap: int = 24
    title_size: int = 62
    heading_size: int = 50
    body_size: int = 44
    background: int = 250
    ink: int = 20
    rotate_fill: int = 250
    blur_radius: float = 0.0
    noise_alpha: float = 0.0
    noise_sigma: float = 12.0
    rotate_degrees: float = 0.0
    downsample_ratio: float = 1.0
    contrast: float = 1.0
    brightness: float = 1.0
    edge_shadow_alpha: float = 0.0

    @property
    def max_width(self) -> int:
        return self.page_width - 2 * self.margin_x


PRESETS = {
    "clean": RenderPreset(name="clean"),
    "degraded": RenderPreset(
        name="degraded",
        background=238,
        ink=56,
        rotate_fill=226,
        blur_radius=1.6,
        noise_alpha=0.16,
        rotate_degrees=1.8,
        downsample_ratio=0.58,
        contrast=0.86,
        brightness=0.97,
        edge_shadow_alpha=0.08,
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


def _new_page(preset: RenderPreset) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    page = Image.new("L", (preset.page_width, preset.page_height), preset.background)
    return page, ImageDraw.Draw(page)


def _apply_postprocessing(page: Image.Image, preset: RenderPreset, seed: int) -> Image.Image:
    rng = random.Random(seed)
    processed = page
    if preset.rotate_degrees > 0:
        angle = rng.uniform(-preset.rotate_degrees, preset.rotate_degrees)
        processed = processed.rotate(
            angle,
            resample=Image.Resampling.BICUBIC,
            fillcolor=preset.rotate_fill,
        )
    if preset.blur_radius > 0:
        processed = processed.filter(ImageFilter.GaussianBlur(preset.blur_radius))
    if 0 < preset.downsample_ratio < 1.0:
        down_width = max(1, int(processed.width * preset.downsample_ratio))
        down_height = max(1, int(processed.height * preset.downsample_ratio))
        processed = processed.resize((down_width, down_height), resample=Image.Resampling.BILINEAR)
        processed = processed.resize(page.size, resample=Image.Resampling.BICUBIC)
    if preset.noise_alpha > 0:
        noise = Image.effect_noise(processed.size, preset.noise_sigma).convert("L")
        processed = Image.blend(processed, noise, preset.noise_alpha)
    if preset.contrast != 1.0:
        processed = ImageEnhance.Contrast(processed).enhance(preset.contrast)
    if preset.brightness != 1.0:
        processed = ImageEnhance.Brightness(processed).enhance(preset.brightness)
    if preset.edge_shadow_alpha > 0:
        shadow = Image.new("L", processed.size, 255)
        shadow_draw = ImageDraw.Draw(shadow)
        inset = 90
        shadow_draw.rectangle(
            (inset, inset, processed.width - inset, processed.height - inset),
            fill=225,
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(90))
        processed = Image.blend(processed, shadow, preset.edge_shadow_alpha)
    return processed


def _render_pages(
    blocks: Iterable[tuple[str, str]],
    font_path: str | None,
    preset_name: str,
) -> list[Image.Image]:
    try:
        preset = PRESETS[preset_name]
    except KeyError as exc:
        raise ValueError(f"Unknown preset: {preset_name}") from exc

    title_font = _load_font(preset.title_size, font_path)
    heading_font = _load_font(preset.heading_size, font_path)
    body_font = _load_font(preset.body_size, font_path)

    pages: list[Image.Image] = []
    page, draw = _new_page(preset)
    y = preset.margin_y

    for kind, text in blocks:
        if kind == "title":
            font = title_font
            gap_after = preset.paragraph_gap + 8
        elif kind == "heading":
            font = heading_font
            gap_after = preset.paragraph_gap
        else:
            font = body_font
            gap_after = preset.paragraph_gap

        lines = _wrap_text(draw, text, font, preset.max_width)
        block_height = len(lines) * (_line_height(draw, font) + preset.line_gap) - preset.line_gap

        if y + block_height > preset.page_height - preset.margin_y:
            pages.append(_apply_postprocessing(page, preset, seed=len(pages) + 1))
            page, draw = _new_page(preset)
            y = preset.margin_y

        for line in lines:
            draw.text((preset.margin_x, y), line, fill=preset.ink, font=font)
            y += _line_height(draw, font) + preset.line_gap
        y += gap_after

    pages.append(_apply_postprocessing(page, preset, seed=len(pages) + 1))
    return pages


def build_fixture(
    source_path: Path,
    output_path: Path,
    font_path: str | None = None,
    preset_name: str = "clean",
) -> int:
    blocks = _parse_source(source_path.read_text(encoding="utf-8"))
    pages = _render_pages(blocks, font_path, preset_name)
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
    parser.add_argument("--output", type=Path, default=None, help="Output PDF path")
    parser.add_argument("--preset", choices=sorted(PRESETS), default="clean", help="Rendering preset")
    parser.add_argument("--font-path", help="Optional explicit font path")
    args = parser.parse_args()

    output_path = args.output or DEFAULT_OUTPUTS[args.preset]
    page_count = build_fixture(args.source, output_path, args.font_path, args.preset)
    print(f"Wrote {output_path} ({page_count} pages, preset={args.preset})")


if __name__ == "__main__":
    main()
