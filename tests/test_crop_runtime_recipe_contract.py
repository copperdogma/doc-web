from pathlib import Path

import yaml


RECIPE_PATH = Path("configs/recipes/recipe-onward-images-html-mvp.yaml")


def _crop_stage_params() -> dict:
    recipe = yaml.safe_load(RECIPE_PATH.read_text(encoding="utf-8"))
    for stage in recipe["stages"]:
        if stage["id"] == "crop_illustrations":
            return stage["params"]
    raise AssertionError("crop_illustrations stage not found in maintained Onward recipe")


def test_onward_crop_recipe_uses_single_stage_detector_contract():
    params = _crop_stage_params()

    assert params["rescue_model"] == "gemini-3-flash-preview"
    assert params["rescue_always"] is True
    assert params["trim_layout_text"] is True

    assert params["rescue_retry_on_overlap"] is False
    assert params["rescue_retry_on_missing"] is False
    assert params["rescue_retry_on_text"] is False
    assert params["rescue_caption_second_pass"] is True
    assert params["rescue_caption_max_tokens"] == 400
    assert params["rescue_refine_boxes"] is False
    assert params["rescue_validate_crops"] is False

    assert "rescue_validate_model" not in params
    assert "rescue_validate_max_tokens" not in params
    assert "rescue_refine_max_tokens" not in params
    assert "rescue_refine_min_area_ratio" not in params
