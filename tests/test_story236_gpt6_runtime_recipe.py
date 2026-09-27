"""Story 236 keeps detector-only challenger comparison on the owner recipe."""

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def _params(name):
    recipe = yaml.safe_load((ROOT / "configs/recipes" / name).read_text())
    return next(s for s in recipe["stages"] if s["id"] == "crop_illustrations")["params"]


def test_gpt6_detector_only_candidate_preserves_caption_assist_and_runtime_contract():
    maintained = _params("recipe-onward-images-html-mvp.yaml")
    incumbent = _params("story-236-gemini-crop-runtime-validate.yaml")
    challenger = _params("story-236-gpt6-luna-detector-runtime-validate.yaml")

    assert incumbent == {**maintained, "rescue_max_pages": 4}
    assert challenger == {
        **incumbent,
        "rescue_model": "gpt-6-luna",
        "rescue_reasoning_effort": "medium",
        "rescue_caption_model": "gemini-3-flash-preview",
    }
    assert incumbent["trim_layout_text"] is True
    assert challenger["rescue_caption_second_pass"] is True


def test_caption_budget_recovery_changes_only_shared_output_bound():
    for arm in (
        "gemini-crop-runtime-validate",
        "gpt6-luna-detector-runtime-validate",
    ):
        original = _params(f"story-236-{arm}.yaml")
        recovered = _params(f"story-236-{arm}-caption2048.yaml")
        assert recovered == {**original, "rescue_caption_max_tokens": 2048}
