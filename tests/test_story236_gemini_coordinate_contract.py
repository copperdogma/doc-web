"""Explicit crop box arrays use prompt x/y order, unlike native box_2d."""

from modules.extract.crop_illustrations_guided_v1 import main as crop


def test_explicit_gemini_image_and_caption_arrays_keep_xy_order(monkeypatch):
    class _Client:
        def generate_vision(self, **kwargs):
            return (
                '[{"image_box":[0.376,0.074,0.58,0.232],'
                '"caption_box":[0.444,0.771,0.637,0.8],'
                '"image_description":"logo"}]',
                None,
                "response-id",
            )

    monkeypatch.setattr(crop, "GeminiVisionClient", _Client)
    boxes, _, request_id, _ = crop._call_vlm_boxes(
        "gemini-3-flash-preview",
        "data:image/jpeg;base64,abc",
        1,
        None,
        0.0,
        8192,
        None,
    )

    assert request_id == "response-id"
    assert boxes[0]["x0"] == 0.376
    assert boxes[0]["y0"] == 0.074
    assert boxes[0]["caption_box"]["x0"] == 0.444
    assert boxes[0]["caption_box"]["y0"] == 0.771


def test_native_gemini_box_2d_keeps_yx_conversion():
    assert crop._parse_gemini_box({"box_2d": [74, 376, 232, 580]}) == {
        "x0": 0.376,
        "y0": 0.074,
        "x1": 0.58,
        "y1": 0.232,
    }


def test_gemini_array_with_caption_at_right_resolves_as_native_yx(monkeypatch):
    class _Client:
        def generate_vision(self, **kwargs):
            return (
                '[{"image_box":[0.058,0.091,0.406,0.908],'
                '"caption_box":[0.409,0.222,0.422,0.78],'
                '"image_description":"group photo"}]',
                None,
                "response-id",
            )

    monkeypatch.setattr(crop, "GeminiVisionClient", _Client)
    boxes, _, _, _ = crop._call_vlm_boxes(
        "gemini-3-flash-preview",
        "data:image/jpeg;base64,abc",
        1,
        None,
        0.0,
        8192,
        None,
    )

    assert boxes[0]["x0"] == 0.091
    assert boxes[0]["y0"] == 0.058
    assert boxes[0]["caption_box"]["x0"] == 0.222
    assert boxes[0]["caption_box"]["y0"] == 0.409


def test_gemini_array_without_caption_falls_back_instead_of_guessing(monkeypatch):
    class _Client:
        def generate_vision(self, **kwargs):
            return (
                '[{"image_box":[0.1,0.2,0.4,0.8],'
                '"caption_box":null,"image_description":"unplaced"}]',
                None,
                "response-id",
            )

    monkeypatch.setattr(crop, "GeminiVisionClient", _Client)
    boxes, _, request_id, raw = crop._call_vlm_boxes(
        "gemini-3-flash-preview",
        "data:image/jpeg;base64,abc",
        1,
        None,
        0.0,
        8192,
        None,
    )

    assert boxes == []
    assert request_id == "response-id"
    assert '"image_box"' in raw
