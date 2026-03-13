import io

import pytest

from modules.extract.ocr_ai_gpt51_v1.main import _is_blank_page, _ocr_with_fallback


def _image_bytes(draw_fn=None) -> bytes:
    try:
        from PIL import Image, ImageDraw
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"PIL not available: {exc}")

    img = Image.new("RGB", (1200, 1600), "white")
    if draw_fn is not None:
        draw = ImageDraw.Draw(img)
        draw_fn(draw, img.size)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _sparse_text_page(draw, size) -> None:
    width, height = size
    for y in (90, 135, 180, 225, 270):
        draw.rectangle((80, y, width - 140, y + 12), fill="black")
    draw.rectangle((width // 2 - 18, height - 120, width // 2 + 18, height - 100), fill="black")


def test_blank_page_detection_accepts_true_blank_page() -> None:
    assert _is_blank_page(_image_bytes(), 0.99) is True


def test_blank_page_detection_rejects_sparse_text_page() -> None:
    assert _is_blank_page(_image_bytes(_sparse_text_page), 0.99) is False


def test_ocr_with_fallback_uses_retry_model_after_empty_primary(monkeypatch) -> None:
    calls = []

    def fake_call(model, *args, **kwargs):
        calls.append(model)
        if model == "gemini-3.1-pro-preview":
            return "", None, None
        return (
            '<meta name="ocr-metadata" data-ocr-quality="1.0" '
            'data-ocr-integrity="1.0" data-continuation-risk="0.2">\n'
            "<p>Recovered content.</p>",
            None,
            None,
        )

    monkeypatch.setattr(
        "modules.extract.ocr_ai_gpt51_v1.main._call_vision_model",
        fake_call,
    )

    raw, cleaned, meta, _meta_tag, _meta_warning, model_used = _ocr_with_fallback(
        _image_bytes(_sparse_text_page),
        "page.jpg",
        model="gemini-3.1-pro-preview",
        retry_model="gpt-5.1",
        system_prompt="system",
        user_text="user",
        temperature=0.0,
        max_output_tokens=512,
    )

    assert calls == ["gemini-3.1-pro-preview", "gpt-5.1"]
    assert "<p>Recovered content.</p>" in raw
    assert "<p>Recovered content.</p>" in cleaned
    assert meta["ocr_quality"] == 1.0
    assert model_used == "gpt-5.1"


def test_ocr_with_fallback_stops_after_first_nonempty_result(monkeypatch) -> None:
    calls = []

    def fake_call(model, *args, **kwargs):
        calls.append(model)
        return "<p>Primary content.</p>", None, None

    monkeypatch.setattr(
        "modules.extract.ocr_ai_gpt51_v1.main._call_vision_model",
        fake_call,
    )

    raw, cleaned, meta, meta_tag, meta_warning, model_used = _ocr_with_fallback(
        _image_bytes(_sparse_text_page),
        "page.jpg",
        model="gpt-5.1",
        retry_model="gpt-5.2",
        system_prompt="system",
        user_text="user",
        temperature=0.0,
        max_output_tokens=512,
    )

    assert calls == ["gpt-5.1"]
    assert "<p>Primary content.</p>" in raw
    assert "<p>Primary content.</p>" in cleaned
    assert meta == {}
    assert meta_tag is None
    assert meta_warning is None
    assert model_used == "gpt-5.1"
