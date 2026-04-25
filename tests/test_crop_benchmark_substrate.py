import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS_DIR = ROOT / "benchmarks"
TASKS_DIR = BENCHMARKS_DIR / "tasks"


def _load_task(task_name: str) -> dict:
    task_path = TASKS_DIR / task_name
    return yaml.safe_load(task_path.read_text(encoding="utf-8"))


def _resolve_task_file_ref(task_name: str, ref: str) -> Path:
    assert ref.startswith("file://"), f"{task_name}: expected file:// ref, got {ref!r}"
    rel_path = ref.removeprefix("file://")
    return (TASKS_DIR / rel_path).resolve()


def _load_json(rel_path: str) -> dict:
    return json.loads((BENCHMARKS_DIR / rel_path).read_text(encoding="utf-8"))


def test_image_crop_extraction_task_assets_exist_and_match_golden_keys():
    task_name = "image-crop-extraction.yaml"
    task = _load_task(task_name)
    golden = _load_json("golden/image-crops.json")

    seen_keys = []
    for test_case in task["tests"]:
        image_ref = test_case["vars"]["image"]
        asset_path = _resolve_task_file_ref(task_name, image_ref)
        assert asset_path.exists(), f"{task_name}: missing benchmark asset {asset_path}"

        golden_key = test_case["vars"]["golden_key"]
        assert golden_key in golden, f"{task_name}: missing golden key {golden_key}"
        seen_keys.append(golden_key)

    assert len(seen_keys) == len(set(seen_keys)), f"{task_name}: duplicate golden keys"
    assert sorted(seen_keys) == sorted(golden.keys())


def test_image_crop_extraction_task_keeps_conservative_count_prompt():
    task_name = "image-crop-extraction.yaml"
    task = _load_task(task_name)

    prompt_labels = {prompt["label"] for prompt in task["prompts"]}
    assert "conservative-count" in prompt_labels, (
        f"{task_name}: maintained detector surface drifted; missing conservative-count prompt"
    )


def test_crop_validation_task_assets_exist_and_match_golden_keys():
    task_name = "crop-validation.yaml"
    task = _load_task(task_name)
    golden = _load_json("golden/crop-validation.json")
    golden_keys = sorted(key for key in golden if key != "_meta")

    seen_keys = []
    for test_case in task["tests"]:
        image_ref = test_case["vars"]["image"]
        asset_path = _resolve_task_file_ref(task_name, image_ref)
        assert asset_path.exists(), f"{task_name}: missing benchmark asset {asset_path}"

        crop_key = test_case["vars"]["crop_key"]
        assert crop_key in golden, f"{task_name}: missing golden key {crop_key}"
        seen_keys.append(crop_key)

    assert len(seen_keys) == len(set(seen_keys)), f"{task_name}: duplicate crop keys"
    assert sorted(seen_keys) == golden_keys


def test_crop_page_level_deletion_gate_assets_exist_and_match_golden_keys():
    task_name = "crop-page-level-deletion-gate.yaml"
    task = _load_task(task_name)
    golden = _load_json("golden/crop-page-level-deletion-gate.json")
    golden_keys = sorted(key for key in golden if key != "_meta")

    seen_keys = []
    for test_case in task["tests"]:
        page_image_ref = test_case["vars"]["page_image"]
        crop_image_ref = test_case["vars"]["crop_image"]

        page_asset_path = _resolve_task_file_ref(task_name, page_image_ref)
        crop_asset_path = _resolve_task_file_ref(task_name, crop_image_ref)

        assert page_asset_path.exists(), f"{task_name}: missing page benchmark asset {page_asset_path}"
        assert crop_asset_path.exists(), f"{task_name}: missing crop benchmark asset {crop_asset_path}"

        crop_key = test_case["vars"]["crop_key"]
        assert crop_key in golden, f"{task_name}: missing golden key {crop_key}"
        seen_keys.append(crop_key)

    assert len(seen_keys) == len(set(seen_keys)), f"{task_name}: duplicate crop keys"
    assert sorted(seen_keys) == golden_keys


def test_crop_page_level_deletion_gate_uses_current_winner():
    task_name = "crop-page-level-deletion-gate.yaml"
    task = _load_task(task_name)

    provider_ids = [provider["id"] for provider in task["providers"]]

    assert provider_ids == ["openai:responses:gpt-5.5"], (
        f"{task_name}: maintained page-context validator should run the "
        "current corrected-golden winner by default"
    )
