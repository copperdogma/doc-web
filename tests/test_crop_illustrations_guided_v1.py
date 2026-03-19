from modules.extract.crop_illustrations_guided_v1.main import _apply_caption_box


def test_apply_caption_box_keeps_partial_width_caption_from_clipping_irregular_image():
    box = {
        "x0": 602,
        "y0": 4300,
        "x1": 3723,
        "y1": 5900,
        "width": 3121,
        "height": 1600,
        "caption_box": {
            "x0": 2270,
            "y0": 5082,
            "x1": 3254,
            "y1": 5907,
        },
    }

    result = _apply_caption_box(box, margin_px=4, max_gap_ratio=0.15)

    assert result["y0"] == box["y0"]
    assert result["y1"] == box["y1"]
    assert result["height"] == box["height"]


def test_apply_caption_box_trims_when_caption_spans_most_of_crop_width():
    box = {
        "x0": 100,
        "y0": 200,
        "x1": 1100,
        "y1": 1200,
        "width": 1000,
        "height": 1000,
        "caption_box": {
            "x0": 150,
            "y0": 950,
            "x1": 1050,
            "y1": 1125,
        },
    }

    result = _apply_caption_box(box, margin_px=4, max_gap_ratio=0.15)

    assert result["y0"] == box["y0"]
    assert result["y1"] == 946
    assert result["height"] == 746
    assert result["_caption_applied"] is True
