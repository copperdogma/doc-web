import json
import os
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw
import pytest
import yaml

FIXTURES = Path("modules/intake/tests/fixtures")


def run(cmd):
    env = dict(**{k: v for k, v in dict(**os.environ).items()})
    env["PYTHONPATH"] = str(Path(".").resolve())
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return result.returncode, result.stdout, result.stderr


def make_test_images(images_dir: Path):
    images_dir.mkdir(parents=True, exist_ok=True)
    labels = [
        "Family Table",
        "Descendants Grid",
        "Portrait",
        "Narrative Notes",
    ]
    for index, label in enumerate(labels, start=1):
        image = Image.new("RGB", (800, 1000), color=(245, 245, 240))
        draw = ImageDraw.Draw(image)
        draw.rectangle([40, 40, 760, 960], outline=(40, 40, 40), width=4)
        draw.text((80, 120), f"Page {index}", fill=(0, 0, 0))
        draw.text((80, 180), label, fill=(0, 0, 0))
        image.save(images_dir / f"Image{index:03d}.jpg", quality=85)


def test_intake_chain_with_mocks(tmp_path):
    source_dir = tmp_path / "source-pages"
    make_test_images(source_dir)

    out_dir = tmp_path / "run"
    out_dir.mkdir(parents=True, exist_ok=True)

    code, _, err = run([
        "python", "modules/intake/contact_sheet_builder_v1/main.py",
        "--input_dir", str(source_dir),
        "--output_dir", str(out_dir / "contact-sheets"),
        "--max_width", "200",
        "--grid_cols", "5",
        "--grid_rows", "4",
    ])
    assert code == 0, err

    manifest = out_dir / "contact-sheets" / "contact_sheet_manifest.jsonl"
    assert manifest.exists()

    code, _out, err = run([
        "python", "modules/intake/contact_sheet_overview_v1/main.py",
        "--manifest", str(manifest),
        "--sheets_dir", str(out_dir / "contact-sheets"),
        "--out", str(out_dir / "plan.json"),
        "--mock_output", str(FIXTURES / "overview_mock.json"),
    ])
    assert code == 0, err

    code, _out, err = run([
        "python", "modules/intake/zoom_refine_v1/main.py",
        "--plan_in", str(out_dir / "plan.json"),
        "--out", str(out_dir / "plan.json"),
        "--mock_output", str(FIXTURES / "zoom_mock.json"),
        "--source_images_dir", str(source_dir),
    ])
    assert code == 0, err

    code, _out, err = run([
        "python", "modules/intake/gap_analyzer_v1/main.py",
        "--plan_in", str(out_dir / "plan.json"),
        "--out", str(out_dir / "plan.json"),
        "--catalog_path", "modules/module_catalog.yaml",
    ])
    assert code == 0, err

    code, _out, err = run([
        "python", "modules/intake/confirm_plan_v1/main.py",
        "--plan", str(out_dir / "plan.json"),
        "--out", str(out_dir / "plan.json"),
        "--auto-approve",
    ])
    assert code == 0, err

    plan = json.loads(Path(out_dir / "plan.json").read_text().splitlines()[0])
    assert plan.get("recommended_recipe") == "configs/recipes/recipe-images-ocr-html-mvp.yaml"
    assert plan.get("meta", {}).get("source_input", {}).get("input_kind") == "images_dir"
    assert "tables" in plan.get("signals", [])
    assert plan.get("capability_gaps") == []


def test_intake_recipe_driver_smoke_with_mocks(tmp_path):
    source_dir = tmp_path / "source-pages"
    make_test_images(source_dir)

    recipe = yaml.safe_load(Path("configs/recipes/recipe-intake-contact-sheet.yaml").read_text())
    run_id = "intake-driver-smoke"
    run_dir = tmp_path / "driver-run" / run_id
    recipe["run_id"] = run_id
    recipe["input"] = {"images": str(source_dir)}
    recipe["output_dir"] = str(run_dir)
    recipe["stage_params"] = {
        "overview_plan": {"mock_output": str(FIXTURES / "overview_mock.json")},
        "zoom_refine": {"mock_output": str(FIXTURES / "zoom_mock.json")},
    }

    recipe_path = tmp_path / "recipe.json"
    recipe_path.write_text(json.dumps(recipe), encoding="utf-8")

    code, _out, err = run([
        "python",
        "driver.py",
        "--recipe",
        str(recipe_path),
        "--registry",
        "modules",
        "--force",
        "--allow-run-id-reuse",
    ])
    assert code == 0, err

    final_plan_path = run_dir / "05_confirm_plan_v1" / "overview_plan_final.jsonl"
    assert final_plan_path.exists()
    plan = json.loads(final_plan_path.read_text().splitlines()[0])
    assert plan.get("recommended_recipe") == "configs/recipes/recipe-images-ocr-html-mvp.yaml"
    assert plan.get("meta", {}).get("source_input", {}).get("input_kind") == "images_dir"


@pytest.mark.skip(reason="requires network/vision model; integration path")
def test_overview_live_call():
    pass
