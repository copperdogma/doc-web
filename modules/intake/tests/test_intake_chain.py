import json
import importlib.util
import sys
import subprocess
from pathlib import Path

import yaml


def load_validate_artifact():
    sys.path.append(str(Path(".").resolve()))
    spec = importlib.util.spec_from_file_location("validate_artifact", Path("validate_artifact.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_schema_map_has_intake(plan_schema_map=Path("validate_artifact.py")):
    text = plan_schema_map.read_text()
    assert "intake_plan_v1" in text
    assert "contact_sheet_manifest_v1" in text


def test_contact_sheet_manifest_shape(fixtures_dir=Path("modules/intake/tests/fixtures")):
    manifest = fixtures_dir / "contact_sheet_manifest_sample.jsonl"
    va = load_validate_artifact()
    model = va.SCHEMA_MAP["contact_sheet_manifest_v1"]
    for line in manifest.read_text().strip().splitlines():
        model(**json.loads(line))


def test_intake_plan_schema(fixtures_dir=Path("modules/intake/tests/fixtures")):
    plan = fixtures_dir / "plan_sample.json"
    va = load_validate_artifact()
    model = va.SCHEMA_MAP["intake_plan_v1"]
    model(**json.loads(plan.read_text()))


def test_validate_artifact_cli_manifest(fixtures_dir=Path("modules/intake/tests/fixtures")):
    manifest = fixtures_dir / "contact_sheet_manifest_sample.jsonl"
    cmd = [sys.executable, "validate_artifact.py", "--schema", "contact_sheet_manifest_v1", "--file", str(manifest)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_validate_artifact_cli_plan(fixtures_dir=Path("modules/intake/tests/fixtures")):
    plan = fixtures_dir / "plan_sample.jsonl"
    cmd = [sys.executable, "validate_artifact.py", "--schema", "intake_plan_v1", "--file", str(plan)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_active_contact_sheet_recipe_exists():
    recipe_path = Path("configs/recipes/recipe-intake-contact-sheet.yaml")
    assert recipe_path.exists()
    recipe = yaml.safe_load(recipe_path.read_text())
    assert [stage["id"] for stage in recipe["stages"]] == [
        "build_contact_sheets",
        "overview_plan",
        "zoom_refine",
        "gap_analysis",
        "confirm_plan",
    ]
