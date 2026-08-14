import json
from pathlib import Path

import pytest
import yaml

from benchmarks.scripts.regrade_crop_result import regrade


ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS_DIR = ROOT / "benchmarks"
TASKS_DIR = BENCHMARKS_DIR / "tasks"


def _load_task(task_name: str) -> dict:
    task_path = TASKS_DIR / task_name
    return yaml.safe_load(task_path.read_text(encoding="utf-8"))


def _load_provider(provider_name: str) -> dict:
    provider_path = BENCHMARKS_DIR / "providers" / provider_name
    providers = yaml.safe_load(provider_path.read_text(encoding="utf-8"))
    assert len(providers) == 1
    return providers[0]


def _resolve_task_file_ref(task_name: str, ref: str) -> Path:
    assert ref.startswith("file://"), f"{task_name}: expected file:// ref, got {ref!r}"
    rel_path = ref.removeprefix("file://")
    return (TASKS_DIR / rel_path).resolve()


def _load_json(rel_path: str) -> dict:
    return json.loads((BENCHMARKS_DIR / rel_path).read_text(encoding="utf-8"))


def _task_crop_keys(task_name: str) -> set[str]:
    return {case["vars"]["crop_key"] for case in _load_task(task_name)["tests"]}


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


def test_gemini_35_flash_lite_detector_uses_strict_bbox_schema():
    task = _load_task("image-crop-extraction.yaml")
    provider = next(
        provider
        for provider in task["providers"]
        if provider["id"] == "google:gemini-3.5-flash-lite"
    )

    schema = provider["config"]["responseSchema"]
    bbox = schema["properties"]["images"]["items"]["properties"]["bbox"]

    assert schema["required"] == ["images"]
    assert bbox["minItems"] == bbox["maxItems"] == 4
    assert bbox["items"] == {"type": "integer", "minimum": 0, "maximum": 1000}


def test_gemini_37_detector_provider_uses_low_thinking_and_strict_bbox_schema():
    provider = _load_provider("gemini37_low_crop_detector.yaml")

    assert provider["id"] == "google:gemini-3.7-flash"
    assert provider["config"]["generationConfig"]["thinkingConfig"] == {
        "thinkingLevel": "low"
    }
    bbox = provider["config"]["responseSchema"]["properties"]["images"]["items"][
        "properties"
    ]["bbox"]
    assert bbox["minItems"] == bbox["maxItems"] == 4
    assert bbox["items"] == {"type": "number", "minimum": 0, "maximum": 1}


def test_gemini_37_integer_detector_arm_uses_unambiguous_bbox_contract():
    provider = _load_provider("gemini37_low_crop_detector_integer.yaml")

    assert provider["id"] == "google:gemini-3.7-flash"
    assert provider["config"]["generationConfig"]["thinkingConfig"] == {
        "thinkingLevel": "low"
    }
    bbox = provider["config"]["responseSchema"]["properties"]["images"]["items"][
        "properties"
    ]["bbox"]
    assert bbox["minItems"] == bbox["maxItems"] == 4
    assert bbox["items"] == {"type": "integer", "minimum": 0, "maximum": 1000}


def test_gemini_37_validator_provider_uses_low_thinking_and_strict_verdict_schema():
    provider = _load_provider("gemini37_low_crop_validator.yaml")

    assert provider["id"] == "google:gemini-3.7-flash"
    assert provider["config"]["generationConfig"]["thinkingConfig"] == {
        "thinkingLevel": "low"
    }
    schema = provider["config"]["responseSchema"]
    assert schema["properties"]["verdict"] == {
        "type": "string",
        "enum": ["pass", "fail"],
    }
    assert schema["required"] == [
        "verdict",
        "has_page_text",
        "excessive_blank",
        "reason",
    ]


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


def test_crop_eval_provenance_partitions_are_complete_disjoint_and_selection_blocking():
    provenance = _load_json("golden/crop-eval-provenance.json")

    for surface_name in ("crop-validation", "crop-page-level-deletion-gate"):
        surface = provenance["surfaces"][surface_name]
        calibration = set(surface["calibration_keys"])
        held_out = set(surface["held_out_confirmation_keys"])

        assert calibration.isdisjoint(held_out)
        assert calibration | held_out == _task_crop_keys(f"{surface_name}.yaml")
        assert surface["model_selection_status"] == "blocked_pending_held_out_truth"
        assert not held_out
        assert "page-126-000" in calibration
        assert "page-126-000" in surface["known_tuning_cases"]

    assert provenance["policy"]["regression_veto_allowed"] is True
    assert provenance["policy"]["selection_veto_allowed_without_held_out"] is False

    creation = provenance["held_out_creation"]
    assert creation["status"] == "blocked_insufficient_unexposed_truth"
    contract = creation["minimum_confirmation_contract"]
    assert contract["case_count"] == 12
    assert contract["minimum_distinct_source_pages"] == 8
    assert contract["required_labels"] == {"pass": 6, "fail": 6}
    assert contract["source_page_overlap_with_calibration"] == 0
    assert contract["freeze_before_provider_calls"] is True


def test_page_126_fail_label_is_preserved_on_both_safety_surfaces():
    for golden_name in ("crop-validation.json", "crop-page-level-deletion-gate.json"):
        golden = _load_json(f"golden/{golden_name}")
        assert golden["page-126-000"]["verdict"] == "fail"
        assert "text_included" in golden["page-126-000"]["reasons"]


def test_regrade_refuses_partition_drift_and_never_claims_selection_without_held_out():
    payload = {
        "results": {
            "results": [
                {"vars": {"crop_key": "calibration-case"}, "success": True},
            ]
        }
    }
    surface = {
        "contract_role": "production_safety_regression",
        "model_selection_status": "blocked_pending_held_out_truth",
        "calibration_keys": ["calibration-case"],
        "held_out_confirmation_keys": [],
    }

    summary = regrade(payload, surface)
    assert summary["calibration"]["pass_rate"] == 1.0
    assert summary["held_out_confirmation"]["pass_rate"] is None
    assert summary["selection_claim_allowed"] is False

    surface["held_out_confirmation_keys"] = ["missing-held-out"]
    try:
        regrade(payload, surface)
    except ValueError as exc:
        assert "missing-held-out" in str(exc)
    else:
        raise AssertionError("partition/result drift must fail closed")

    surface["held_out_confirmation_keys"] = []
    payload["results"]["results"].append(
        {"vars": {"crop_key": "extra-case"}, "success": True}
    )
    with pytest.raises(ValueError, match="extra-case"):
        regrade(payload, surface)


def test_regrade_refuses_duplicate_result_crop_keys():
    payload = {
        "results": {
            "results": [
                {"vars": {"crop_key": "calibration-case"}, "success": True},
                {"vars": {"crop_key": "calibration-case"}, "success": True},
            ]
        }
    }
    surface = {
        "contract_role": "production_safety_regression",
        "model_selection_status": "blocked_pending_held_out_truth",
        "calibration_keys": ["calibration-case"],
        "held_out_confirmation_keys": [],
    }

    with pytest.raises(ValueError, match="Duplicate result crop_key rows.*calibration-case"):
        regrade(payload, surface)


def test_regrade_refuses_calibration_held_out_overlap():
    payload = {
        "results": {
            "results": [
                {"vars": {"crop_key": "shared-case"}, "success": True},
            ]
        }
    }
    surface = {
        "contract_role": "production_safety_regression",
        "model_selection_status": "eligible_held_out_confirmation",
        "calibration_keys": ["shared-case"],
        "held_out_confirmation_keys": ["shared-case"],
    }

    with pytest.raises(ValueError, match="partition overlap.*shared-case"):
        regrade(payload, surface)


def test_regrade_blocks_selection_when_status_is_blocked_despite_passing_held_out():
    payload = {
        "results": {
            "results": [
                {"vars": {"crop_key": "calibration-case"}, "success": True},
                {"vars": {"crop_key": "held-out-case"}, "success": True},
            ]
        }
    }
    surface = {
        "contract_role": "production_safety_regression",
        "model_selection_status": "blocked_pending_held_out_truth",
        "calibration_keys": ["calibration-case"],
        "held_out_confirmation_keys": ["held-out-case"],
    }

    summary = regrade(payload, surface)
    assert summary["held_out_confirmation"]["pass_rate"] == 1.0
    assert summary["selection_claim_allowed"] is False


def test_regrade_requires_all_held_out_cases_to_pass_for_selection():
    payload = {
        "results": {
            "results": [
                {"vars": {"crop_key": "calibration-case"}, "success": True},
                {"vars": {"crop_key": "held-out-pass"}, "success": True},
                {"vars": {"crop_key": "held-out-fail"}, "success": False},
            ]
        }
    }
    surface = {
        "contract_role": "production_safety_regression",
        "model_selection_status": "eligible_held_out_confirmation",
        "calibration_keys": ["calibration-case"],
        "held_out_confirmation_keys": ["held-out-pass", "held-out-fail"],
    }

    summary = regrade(payload, surface)
    assert summary["held_out_confirmation"]["pass_rate"] == 0.5
    assert summary["selection_claim_allowed"] is False

    payload["results"]["results"][2]["success"] = True
    summary = regrade(payload, surface)
    assert summary["held_out_confirmation"]["pass_rate"] == 1.0
    assert summary["selection_claim_allowed"] is True


def test_crop_page_level_deletion_gate_keeps_configured_regression_provider():
    task_name = "crop-page-level-deletion-gate.yaml"
    task = _load_task(task_name)

    provider_ids = [provider["id"] for provider in task["providers"]]

    assert provider_ids == ["openai:responses:gpt-5.5"]
