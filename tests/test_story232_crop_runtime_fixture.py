from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def _crop_params(path: str) -> dict:
    payload = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    return next(stage for stage in payload["stages"] if stage["id"] == "crop_illustrations")[
        "params"
    ]


def test_terra_runtime_fixture_matches_maintained_recipe_except_page_cap() -> None:
    maintained = _crop_params("configs/recipes/recipe-onward-images-html-mvp.yaml")
    terra = _crop_params("configs/recipes/story-232-terra-crop-runtime-validate.yaml")

    assert maintained["rescue_model"] == "gemini-3-flash-preview"
    assert terra["rescue_model"] == "gpt-5.6-terra"
    ignored = {"rescue_model", "rescue_max_pages"}
    assert {key: value for key, value in terra.items() if key not in ignored} == {
        key: value for key, value in maintained.items() if key not in ignored
    }
