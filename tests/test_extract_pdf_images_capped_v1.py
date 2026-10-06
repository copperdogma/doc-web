import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from PIL import Image

from modules.extract.extract_pdf_images_capped_v1 import main as extractor


@pytest.mark.parametrize(
    "image_format,expected_format,extension",
    [("jpeg", "JPEG", "jpg"), ("png", "PNG", "png")],
)
def test_rendered_image_format_is_configurable_and_reported(
    tmp_path, monkeypatch, image_format, expected_format, extension
):
    page = SimpleNamespace(mediabox=SimpleNamespace(width=612, height=792))
    pixels = np.full((64, 48, 3), 127, dtype=np.uint8)
    rendered = Image.fromarray(pixels, mode="RGB")
    monkeypatch.setattr(
        extractor, "_load_pdf_reader", lambda _: SimpleNamespace(pages=[page])
    )
    monkeypatch.setattr(extractor, "_page_max_image_dpi", lambda _: 300)
    monkeypatch.setattr(
        extractor, "convert_from_path", lambda *args, **kwargs: [rendered.copy()]
    )

    argv = [
        "extract_pdf_images_capped_v1",
        "--pdf",
        str(tmp_path / "source.pdf"),
        "--outdir",
        str(tmp_path),
        "--image-format",
        image_format,
    ]
    monkeypatch.setattr(sys, "argv", argv)
    extractor.main()

    manifest = json.loads((tmp_path / "pages_rendered_manifest.jsonl").read_text())
    report = json.loads((tmp_path / "render_dpi_report.jsonl").read_text())
    image_path = Path(manifest["image"])
    assert image_path.name == f"page-001.{extension}"
    assert manifest["original_page_number"] == 1
    assert manifest["source"] == [str((tmp_path / "source.pdf").resolve())]
    with Image.open(image_path) as saved:
        assert saved.format == expected_format
        assert saved.size == rendered.size
    assert report["image_format"] == image_format
    assert report["image"] == str(image_path.resolve())


def test_rendered_image_format_defaults_to_jpeg(tmp_path, monkeypatch):
    page = SimpleNamespace(mediabox=SimpleNamespace(width=612, height=792))
    monkeypatch.setattr(
        extractor, "_load_pdf_reader", lambda _: SimpleNamespace(pages=[page])
    )
    monkeypatch.setattr(extractor, "_page_max_image_dpi", lambda _: 300)
    monkeypatch.setattr(
        extractor,
        "convert_from_path",
        lambda *args, **kwargs: [Image.new("RGB", (48, 64), "white")],
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["extract_pdf_images_capped_v1", "--pdf", str(tmp_path / "source.pdf"), "--outdir", str(tmp_path)],
    )

    extractor.main()

    manifest = json.loads((tmp_path / "pages_rendered_manifest.jsonl").read_text())
    assert Path(manifest["image"]).suffix == ".jpg"
    with Image.open(manifest["image"]) as saved:
        assert saved.format == "JPEG"
