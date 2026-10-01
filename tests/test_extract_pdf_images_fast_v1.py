import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from PIL import Image

from modules.extract.extract_pdf_images_fast_v1 import main as extractor


@pytest.mark.parametrize("route", ["fast_extract", "render_fallback"])
@pytest.mark.parametrize("normalize", [False, True])
@pytest.mark.parametrize("mode,encoding,channels", [("RGB", "PNG", 3), ("CMYK", "TIFF", 4)])
def test_extraction_preserves_decoded_source_pixels(tmp_path, monkeypatch, route, normalize,
                                                  mode, encoding, channels):
    pixels = np.random.default_rng(29).integers(0, 256, (83, 97, channels), dtype=np.uint8)
    source = Image.fromarray(pixels, mode=mode)

    class Page(dict):
        mediabox = SimpleNamespace(width=72, height=72)

    monkeypatch.setattr(extractor, "_load_pdf_reader",
                        lambda _: SimpleNamespace(pages=[Page()]))
    monkeypatch.setattr(extractor, "_page_max_image_dpi", lambda _: 300)
    monkeypatch.setattr(extractor, "_extract_image_from_xobject",
                        lambda *_: (source.copy(), {}) if route == "fast_extract" else None)
    monkeypatch.setattr(extractor, "_render_page_fallback", lambda *_: source.copy())
    monkeypatch.setattr(extractor, "_measure_xheight_tesseract", lambda _: 80)
    args = ["extract", "--pdf", str(tmp_path / "source.pdf"), "--outdir", str(tmp_path)]
    if not normalize:
        args.append("--no-normalize")
    monkeypatch.setattr(sys, "argv", args)
    extractor.main()

    row = json.loads((tmp_path / "pages_rendered_manifest.jsonl").read_text())
    report = json.loads((tmp_path / "extraction_report.jsonl").read_text())
    assert report["extraction_method"] == route
    native_path = Path(row["image_native"] if normalize else row["image"])
    with Image.open(native_path) as native:
        assert native.format == encoding
        assert native.mode == mode
        assert np.array_equal(np.asarray(native), pixels)
    with Image.open(row["image"]) as output:
        assert output.format == encoding
        assert output.size == ((48, 42) if normalize else source.size)
    assert report["output_encoding"] == encoding.lower()
