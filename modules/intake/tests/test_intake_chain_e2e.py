import json
import os
import subprocess
from pathlib import Path
import uuid

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


@pytest.mark.parametrize(
    ("recipe_path", "plan_payload"),
    [
        (
            "configs/recipes/recipe-images-ocr-html-mvp.yaml",
            lambda source: {
                "schema_version": "intake_plan_v1",
                "book_type": "genealogy",
                "signals": ["tables", "images"],
                "recommended_recipe": "configs/recipes/recipe-images-ocr-html-mvp.yaml",
                "capability_gaps": [],
                "warnings": [],
                "meta": {
                    "source_input": {
                        "input_kind": "images_dir",
                        "source_images_dir": str(source),
                    }
                },
            },
        ),
        (
            "configs/recipes/recipe-pdf-ocr-html-mvp.yaml",
            lambda source: {
                "schema_version": "intake_plan_v1",
                "book_type": "textbook",
                "signals": ["tables"],
                "recommended_recipe": "configs/recipes/recipe-pdf-ocr-html-mvp.yaml",
                "capability_gaps": [],
                "warnings": [],
                "meta": {
                    "source_input": {
                        "input_kind": "pdf",
                        "source_pdf": str(source),
                        "has_extractable_text": False,
                    }
                },
            },
        ),
        (
            "configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml",
            lambda source: {
                "schema_version": "intake_plan_v1",
                "book_type": "other",
                "signals": [],
                "recommended_recipe": "configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml",
                "capability_gaps": [],
                "warnings": [],
                "meta": {
                    "source_input": {
                        "input_kind": "pdf",
                        "source_pdf": str(source),
                        "has_extractable_text": True,
                    }
                },
            },
        ),
    ],
)
def test_run_dispatch_dry_run_writes_handoff_artifact(tmp_path, recipe_path, plan_payload):
    source = tmp_path / "source-pages"
    if "images-ocr" in recipe_path:
        make_test_images(source)
    else:
        fixture_name = "flat-born-digital-mini.pdf" if "non-toc" in recipe_path else "scanned-prose-mini.pdf"
        source = Path("testdata") / fixture_name

    plan_path = tmp_path / "overview_plan_final.jsonl"
    plan_path.write_text(json.dumps(plan_payload(source)) + "\n", encoding="utf-8")
    handoff_path = tmp_path / "intake_handoff.jsonl"
    downstream_run_id = f"handoff-{uuid.uuid4().hex[:8]}"

    code, out, err = run([
        "python",
        "modules/intake/run_dispatch_v1/main.py",
        "--plan",
        str(plan_path),
        "--out",
        str(handoff_path),
        "--dry-run",
        "--downstream-run-id",
        downstream_run_id,
    ])
    assert code == 0, out + err

    handoff = json.loads(handoff_path.read_text(encoding="utf-8").splitlines()[0])
    assert handoff["schema_version"] == "intake_handoff_v1"
    assert handoff["recommended_recipe"] == recipe_path
    assert handoff["downstream_run_id"] == downstream_run_id
    assert handoff["terminal_outcome"] == "skipped"
    assert handoff["terminal_reason"] == "dry_run"
    assert Path(handoff["driver_command"][0]).name.startswith("python")
    assert handoff["driver_command"][1].endswith("/driver.py")
    assert handoff["driver_command"][3] == recipe_path
    if "images-ocr" in recipe_path:
        assert handoff["launch_input_flag"] == "--input-images"
        assert handoff["launch_input_path"] == str(source.resolve())
    else:
        assert handoff["launch_input_flag"] == "--input-pdf"
        assert handoff["launch_input_path"] == str(source.resolve())


def test_driver_input_images_override_extract_smoke(tmp_path):
    source_dir = tmp_path / "source-pages"
    make_test_images(source_dir)

    run_id = f"images-override-{uuid.uuid4().hex[:8]}"
    run_dir = tmp_path / "driver-run" / run_id

    code, _out, err = run([
        "python",
        "driver.py",
        "--recipe",
        "configs/recipes/recipe-images-ocr-html-mvp.yaml",
        "--input-images",
        str(source_dir),
        "--run-id",
        run_id,
        "--output-dir",
        str(run_dir),
        "--end-at",
        "images_to_manifest",
    ])
    assert code == 0, err

    manifest_path = run_dir / "01_images_dir_to_manifest_v1" / "pages_images_manifest.jsonl"
    assert manifest_path.exists()
    rows = [
        json.loads(line)
        for line in manifest_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert rows
    assert all(row["source"] == [str(source_dir.resolve())] for row in rows)


def test_confirmed_handoff_recipe_wiring():
    data = yaml.safe_load(
        Path("configs/recipes/recipe-intake-contact-sheet-confirmed-handoff.yaml").read_text(encoding="utf-8")
    )

    stages = data["stages"]
    assert [stage["module"] for stage in stages] == [
        "contact_sheet_builder_v1",
        "contact_sheet_overview_v1",
        "zoom_refine_v1",
        "gap_analyzer_v1",
        "confirm_plan_v1",
        "run_dispatch_v1",
    ]
    confirm_stage = stages[4]
    assert confirm_stage["module"] == "confirm_plan_v1"
    assert confirm_stage.get("params", {}).get("auto_approve") is not True
    dispatch_stage = stages[5]
    assert dispatch_stage["inputs"]["plan"] == "confirm_plan"
    assert dispatch_stage["out"] == "intake_handoff.jsonl"


@pytest.mark.skip(reason="requires network/vision model; integration path")
def test_overview_live_call():
    pass
