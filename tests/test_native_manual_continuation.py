"""Preparation retains paid artifacts and cannot replace/reorder the original graph."""
import json
from pathlib import Path
import shlex

import pytest
import yaml

from driver import build_plan, load_registry
from scripts.prepare_native_manual_continuation import ROOT, canonical_hash, prepare, sha


@pytest.fixture
def parent(tmp_path):
    run = tmp_path / "parent"
    snapshots = run / "snapshots"
    snapshots.mkdir(parents=True)
    pdf = tmp_path / "source.pdf"
    pdf.write_bytes(b"synthetic source PDF")
    recipe = yaml.safe_load((ROOT / "configs/recipes/recipe-graphics-heavy-imposed-pdf-html-mvp.yaml").read_text())
    recipe["input"]["pdf"] = str(pdf)
    recipe["stage_params"] = {"ocr_ai": {"model": "retained-paid-model"},
                              "build_chapters": {"resolve_references": True}}
    plan = build_plan(recipe, load_registry(str(ROOT / "modules"))["modules"])
    state = {"run_id": "paid-parent", "status": "done", "ended_at": "2026-01-01T00:00:00Z", "stages": {}}
    for index, sid in enumerate(plan["topo"], 1):
        node = plan["nodes"][sid]
        artifact = run / f"{index:02d}_{node['module']}" / node["artifact_name"]
        artifact.parent.mkdir()
        artifact.write_text(json.dumps({"run_id": "paid-parent", "created_at": "paid-timestamp",
                                        "image_native": str(run / "immutable-source.png")}) + "\n")
        state["stages"][sid] = {"status": "done", "module_id": node["module"],
                                "artifact": str(artifact), "updated_at": "paid-stage-timestamp"}
    (snapshots / "recipe.yaml").write_text(yaml.safe_dump(recipe, sort_keys=False))
    (snapshots / "plan.json").write_text(json.dumps(plan))
    (run / "pipeline_state.json").write_text(json.dumps(state))
    (run / "pipeline_events.jsonl").write_text('{"timestamp":"paid-event"}\n')
    (run / "output/html").mkdir(parents=True)
    (run / "output/html/index.html").write_text("original published HTML")
    return run


def test_append_only_offline_preparation_preserves_paid_data(parent, tmp_path):
    before = {p.relative_to(parent): p.read_bytes() for p in parent.rglob("*") if p.is_file()}
    destination = tmp_path / "new-continuation"
    command = shlex.split(prepare(parent, destination, "new-continuation"))
    recipe = yaml.safe_load((destination / "source-fidelity-continuation.yaml").read_text())
    original = yaml.safe_load((parent / "snapshots/recipe.yaml").read_text())
    saved = json.loads((parent / "snapshots/plan.json").read_text())
    planned = build_plan(recipe, load_registry(str(ROOT / "modules"))["modules"])
    assert recipe["stages"][:len(original["stages"])] == original["stages"]
    assert recipe["stage_params"] == original["stage_params"]
    assert planned["topo"] == saved["topo"] + ["source_fidelity_recover", "source_fidelity_build", "source_fidelity_validate"]
    assert {sid: planned["nodes"][sid] for sid in saved["topo"]} == saved["nodes"]
    assert recipe["stages"][-3]["needs"][0] == "validate_manual_html"
    params = recipe["stages"][-2]["params"]
    assert params["resolve_references"] is True
    assert params["normalize_reference_entries"] is False and params["normalize_catalog_entries"] is False
    assert params["output_dir"] == str(destination / "output/source-fidelity/html")
    state = json.loads((destination / "pipeline_state.json").read_text())
    expected = json.loads(before[Path("pipeline_state.json")])
    for record in expected["stages"].values():
        record["artifact"] = str(destination / Path(record["artifact"]).relative_to(parent))
    assert state == expected
    for relative, content in before.items():
        assert (parent / relative).read_bytes() == content
        if relative != Path("pipeline_state.json"):
            assert (destination / relative).read_bytes() == content
    assert (destination / "continuation_parent/pipeline_state.json").read_bytes() == before[Path("pipeline_state.json")]
    receipt = json.loads((destination / "native_manual_continuation.json").read_text())
    assert receipt["parent_graph_canonical_sha256"] == canonical_hash(saved)
    assert receipt["parent_recipe_snapshot_sha256"] == sha(parent / "snapshots/recipe.yaml")
    assert receipt["parent_plan_snapshot_sha256"] == sha(parent / "snapshots/plan.json")
    assert receipt["parent_required"] is True
    assert command[command.index("--start-from") + 1] == "source_fidelity_recover"
    assert command[command.index("--output-dir") + 1] == str(destination)
    assert "--allow-run-id-reuse" in command
    assert not (destination / "output/source-fidelity").exists()  # Preparation never executes.


def test_parent_directory_alias_preserves_original_path_spelling(parent, tmp_path):
    alias = tmp_path / "parent-alias"
    alias.symlink_to(parent, target_is_directory=True)
    state_path = parent / "pipeline_state.json"
    original_state = json.loads(state_path.read_text())
    for record in original_state["stages"].values():
        record["artifact"] = str(alias / Path(record["artifact"]).relative_to(parent))
    state_path.write_text(json.dumps(original_state))
    before = state_path.read_bytes()
    source_artifact = Path(original_state["stages"]["ocr_ai"]["artifact"])
    source_bytes = source_artifact.read_bytes()
    destination = tmp_path / "alias-continuation"

    prepare(alias, destination, "alias-continuation")

    state = json.loads((destination / "pipeline_state.json").read_text())
    receipt = json.loads((destination / "native_manual_continuation.json").read_text())
    assert receipt["parent"] == str(parent.resolve())
    for sid, record in original_state["stages"].items():
        target = destination.resolve() / Path(record["artifact"]).relative_to(alias)
        assert state["stages"][sid] == {**record, "artifact": str(target)}
        assert receipt["artifact_path_changes"][sid] == {"before": record["artifact"], "after": str(target)}
    assert state_path.read_bytes() == before
    assert (destination / "continuation_parent/pipeline_state.json").read_bytes() == before
    assert Path(state["stages"]["ocr_ai"]["artifact"]).read_bytes() == source_bytes
    assert source_artifact.read_bytes() == source_bytes


@pytest.mark.parametrize("kind", ["child", "ancestor", "same", "exists", "missing-state", "not-done", "graph-change", "missing-artifact", "unsafe-output", "mismatched-id"])
def test_refuses_before_cloning(parent, tmp_path, kind):
    destination = tmp_path / "new-continuation"
    if kind == "child":
        destination = parent / "child"
    elif kind == "ancestor":
        destination = parent.parent
    elif kind == "same":
        destination = parent
    elif kind == "exists":
        destination.mkdir()
    elif kind == "mismatched-id":
        destination = tmp_path / "different-name"
    elif kind == "missing-state":
        (parent / "pipeline_state.json").unlink()
    elif kind == "not-done":
        path = parent / "pipeline_state.json"
        state = json.loads(path.read_text())
        state["stages"]["ocr_ai"]["status"] = "failed"
        path.write_text(json.dumps(state))
    elif kind == "graph-change":
        path = parent / "snapshots/plan.json"
        plan = json.loads(path.read_text())
        plan["topo"] = list(reversed(plan["topo"]))
        path.write_text(json.dumps(plan))
    elif kind == "unsafe-output":
        path = parent / "snapshots/recipe.yaml"
        recipe = yaml.safe_load(path.read_text())
        recipe["stage_params"]["source_fidelity_build"] = {"output_dir": str(parent / "output/html")}
        path.write_text(yaml.safe_dump(recipe))
    else:
        state = json.loads((parent / "pipeline_state.json").read_text())
        Path(state["stages"]["ocr_ai"]["artifact"]).unlink()
    existed = destination.exists()
    with pytest.raises((ValueError, OSError)):
        prepare(parent, destination, "new-continuation")
    assert destination.exists() == existed
