import json
from pathlib import Path

import yaml

from scripts.prepare_story231_crop_fixture import CASES, prepare


ROOT = Path(__file__).resolve().parents[1]
LUNA_RECIPE = ROOT / "configs/recipes/story-231-luna-crop-runtime-validate.yaml"
GEMINI_RECIPE = ROOT / "configs/recipes/story-231-gemini-crop-runtime-validate.yaml"
MAINTAINED_RECIPE = ROOT / "configs/recipes/recipe-onward-images-html-mvp.yaml"


def _crop_params(path: Path) -> dict:
    recipe = yaml.safe_load(path.read_text(encoding="utf-8"))
    stage = next(
        stage for stage in recipe["stages"] if stage["id"] == "crop_illustrations"
    )
    return stage["params"]


def test_story231_fixture_materializes_valid_distinct_pages(tmp_path):
    manifest = prepare(tmp_path)
    rows = [
        json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines()
    ]

    assert [row["page_number"] for row in rows] == [1, 12, 122, 125]
    assert len(rows) == len(CASES)
    assert all(row["schema_version"] == "page_html_v1" for row in rows)
    assert all(Path(row["image"]).is_file() for row in rows)
    assert [len(row["images"]) for row in rows] == [1, 4, 3, 1]
    assert rows[0]["images"] == CASES[0]["images"]
    assert rows[1]["images"] == CASES[1]["images"]
    assert rows[2]["images"] == CASES[2]["images"]
    assert rows[3]["images"] == CASES[3]["images"]


def test_story231_driver_recipes_differ_only_by_compared_model():
    luna = _crop_params(LUNA_RECIPE)
    gemini = _crop_params(GEMINI_RECIPE)

    assert luna["rescue_model"] == "gpt-5.6-luna"
    assert gemini["rescue_model"] == "gemini-3-flash-preview"
    assert {**luna, "rescue_model": None} == {**gemini, "rescue_model": None}
    assert luna["rescue_always"] is True
    assert luna["rescue_caption_second_pass"] is True
    assert luna["trim_layout_text"] is True


def test_story231_driver_recipes_match_maintained_runtime_except_whitelisted_keys():
    maintained = _crop_params(MAINTAINED_RECIPE)
    ignored = {"rescue_model", "rescue_max_pages"}
    maintained_contract = {
        key: value for key, value in maintained.items() if key not in ignored
    }

    for path in (LUNA_RECIPE, GEMINI_RECIPE):
        candidate = _crop_params(path)
        candidate_contract = {
            key: value for key, value in candidate.items() if key not in ignored
        }
        assert candidate_contract == maintained_contract

    assert maintained["rescue_max_pages"] == 20
    assert _crop_params(LUNA_RECIPE)["rescue_max_pages"] == len(CASES)
    assert _crop_params(GEMINI_RECIPE)["rescue_max_pages"] == len(CASES)
