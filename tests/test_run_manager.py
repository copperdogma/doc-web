import os
import shutil
import subprocess
import uuid
import pytest
import yaml

RUN_MANAGER = "tools/run_manager.py"
RUNS_DIR = os.path.join("output", "runs")

@pytest.fixture
def cleanup_runs():
    created_paths = []
    yield created_paths
    for path in created_paths:
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.exists(path):
            os.remove(path)

def test_create_run(cleanup_runs):
    run_name = f"integration-test-run-{uuid.uuid4().hex[:8]}"
    subprocess.run(["python", RUN_MANAGER, "create-run", run_name], check=True)
    
    expected_path = os.path.join(RUNS_DIR, run_name, "config.yaml")
    cleanup_runs.append(os.path.join(RUNS_DIR, run_name))
    assert os.path.exists(expected_path)
    
    with open(expected_path, "r") as f:
        config_data = yaml.safe_load(f)
    assert config_data["recipe"] == "configs/recipes/recipe-images-ocr-html-mvp.yaml"
    assert config_data["run_id"] == run_name
    assert "input_pdf" not in config_data

def test_execute_run_dry_run(cleanup_runs, tmp_path):
    run_name = f"exec-test-{uuid.uuid4().hex[:8]}"
    
    # Create a dummy recipe so driver.py can load it
    dummy_recipe = tmp_path / "dummy.yaml"
    with open(dummy_recipe, "w") as f:
        f.write("name: dummy-recipe\n")
    
    subprocess.run(["python", RUN_MANAGER, "create-run", run_name], check=True)
    cleanup_runs.append(os.path.join(RUNS_DIR, run_name))
    
    # Update the created run config to point to our dummy recipe
    expected_path = os.path.join(RUNS_DIR, run_name, "config.yaml")
    with open(expected_path, "r") as f:
        config_data = yaml.safe_load(f)
    config_data["recipe"] = str(dummy_recipe)
    with open(expected_path, "w") as f:
        yaml.dump(config_data, f)

    # We use --dry-run so driver.py doesn't actually do anything 
    # and we can check if it invoked correctly.
    result = subprocess.run(
        ["python", RUN_MANAGER, "execute-run", run_name, "--dry-run"],
        capture_output=True,
        text=True
    )
    
    # Check if driver.py was called and recognized the config
    assert "Executing:" in result.stdout
    assert "driver.py --config" in result.stdout
    assert f"output/runs/{run_name}/config.yaml" in result.stdout
    assert "--dry-run" in result.stdout
