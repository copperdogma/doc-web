from pathlib import Path

import yaml


RECIPE_PATH = Path("configs/recipes/recipe-onward-images-html-mvp.yaml")
MODULE_PATH = Path("modules/extract/crop_illustrations_guided_v1/module.yaml")

RETIRED_RECIPE_KEYS = {
    "rescue_retry_on_overlap",
    "rescue_retry_on_missing",
    "rescue_retry_max",
    "rescue_require_caption_schema",
    "rescue_retry_on_text",
    "rescue_refine_boxes",
    "rescue_refine_max_tokens",
    "rescue_refine_min_area_ratio",
    "rescue_validate_crops",
    "rescue_validate_model",
    "rescue_validate_max_tokens",
}

RETIRED_MODULE_FLAGS = {
    "--rescue-retry-on-overlap",
    "--rescue-retry-on-missing",
    "--rescue-retry-max",
    "--rescue-require-caption-schema",
    "--rescue-retry-on-text",
    "--rescue-refine-boxes",
    "--rescue-refine-max-tokens",
    "--rescue-refine-min-area-ratio",
    "--rescue-validate-crops",
    "--rescue-validate-model",
    "--rescue-validate-max-tokens",
}


def _crop_stage_params() -> dict:
    recipe = yaml.safe_load(RECIPE_PATH.read_text(encoding="utf-8"))
    for stage in recipe["stages"]:
        if stage["id"] == "crop_illustrations":
            return stage["params"]
    raise AssertionError("crop_illustrations stage not found in maintained Onward recipe")


def _crop_module_spec() -> dict:
    return yaml.safe_load(MODULE_PATH.read_text(encoding="utf-8"))


def test_onward_crop_recipe_uses_maintained_flash_caption_trim_contract():
    params = _crop_stage_params()

    assert params["rescue_model"] == "gemini-3-flash-preview"
    assert params["rescue_always"] is True
    assert params["rescue_caption_second_pass"] is True
    assert params["rescue_caption_max_tokens"] == 400
    assert params["trim_layout_text"] is True

    assert RETIRED_RECIPE_KEYS.isdisjoint(params)


def test_crop_module_contract_exposes_only_maintained_rescue_surface():
    module_spec = _crop_module_spec()
    param_names = {param["name"] for param in module_spec["parameters"]}

    assert "rescue_model" in param_names
    assert "rescue_always" in param_names
    assert "rescue_caption_second_pass" in param_names
    assert "rescue_caption_max_tokens" in param_names
    assert "trim_layout_text" in param_names

    assert RETIRED_RECIPE_KEYS.isdisjoint(param_names)

    command = module_spec["command"]
    for flag in RETIRED_MODULE_FLAGS:
        assert flag not in command
