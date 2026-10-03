"""Color metadata describes visible source channels, without removing chroma."""
import json

import numpy as np
import pytest
from PIL import Image, ImageCms

from modules.extract.crop_illustrations_guided_v1.main import (
    _is_bw_image,
    crop_illustrations_guided,
)


def _balanced_color_image():
    pixels = np.zeros((96, 96, 3), dtype=np.uint8)
    for index, color in enumerate(((255, 0, 0), (0, 255, 0), (0, 0, 255))):
        pixels[:, index * 32:(index + 1) * 32] = color
    return Image.fromarray(pixels)


def test_balanced_saturated_colors_do_not_cancel_to_grayscale():
    assert not _is_bw_image(_balanced_color_image())


def test_sparse_colored_accent_is_not_diluted_by_neutral_background():
    image = Image.new("RGB", (96, 96), (128, 128, 128))
    image.putpixel((48, 48), (255, 0, 0))
    assert not _is_bw_image(image)


def test_source_paper_tint_remains_color():
    assert not _is_bw_image(Image.new("RGB", (96, 96), (240, 235, 225)))


@pytest.mark.parametrize("mode,value", [("RGB", (128, 128, 128)), ("L", 128), ("1", 1)])
def test_neutral_source_channels_are_black_and_white(mode, value):
    assert _is_bw_image(Image.new(mode, (96, 96), value))


def test_hidden_transparent_chroma_does_not_color_visible_neutral_pixels():
    image = Image.new("RGBA", (96, 96), (255, 0, 0, 0))
    image.paste((128, 128, 128, 255), (40, 40, 56, 56))
    assert _is_bw_image(image)


def test_partly_visible_chroma_still_counts_as_color():
    image = Image.new("RGBA", (96, 96), (128, 128, 128, 255))
    image.putpixel((48, 48), (255, 0, 0, 1))
    assert not _is_bw_image(image)


def test_optional_transparency_preserves_colored_source_without_grayscale_derivative(tmp_path):
    image = _balanced_color_image()
    profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    source = tmp_path / "source.png"
    image.save(source, icc_profile=profile)
    pages = tmp_path / "pages.jsonl"
    pages.write_text(json.dumps({"page_number": 1, "image": str(source), "images": []}) + "\n")
    planner = tmp_path / "critical.json"
    planner.write_text(json.dumps({"pages": [{"page_number": 1, "targets": [{
        "target_id": "synthetic-color", "importance": "essential", "role": "photo",
        "description": "Source channel preservation control",
        "bbox_pixels": {"x0": 0, "y0": 0, "x1": 96, "y1": 96, "width": 96, "height": 96},
    }]}]}))
    output = tmp_path / "out"
    rows = crop_illustrations_guided(str(pages), str(output), output_format="png",
        critical_graphics_manifest=str(planner), padding_percent=0, transparency=True)
    assert len(rows) == 1
    row = rows[0]
    saved = Image.open(output / "images" / row["filename"])
    assert np.array_equal(np.asarray(saved.convert("RGBA")), np.asarray(image.convert("RGBA")))
    assert saved.info["icc_profile"] == profile
    assert row["bbox"] == {"x0": 0, "y0": 0, "x1": 96, "y1": 96, "width": 96, "height": 96}
    assert row["is_color"] is True
    assert row["filename_alpha"] is None
    assert row["has_transparency"] is False
    assert not list((output / "images").glob("*-alpha.png"))
