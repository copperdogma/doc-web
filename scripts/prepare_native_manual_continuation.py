#!/usr/bin/env python3
"""Prepare (never execute) an append-only, offline continuation of a completed manual."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import shlex
import shutil
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from driver import build_plan, load_registry  # noqa: E402

STANDARD_MODULES = dict(zip(
    ("pdf_to_images", "split_spreads", "infer_logical_pages", "ocr_ai", "plan_figures",
     "plan_critical_graphics", "crop_illustrations", "extract_page_numbers",
     "normalize_manual_html", "portionize_headings", "build_chapters", "validate_manual_html"),
    ("extract_pdf_images_fast_v1", "split_pages_from_manifest_v1", "infer_logical_page_order_v1",
     "ocr_ai_gpt51_v1", "plan_graphic_manual_figures_v1", "plan_critical_graphics_vlm_v1",
     "crop_illustrations_guided_v1", "extract_page_numbers_html_v1", "normalize_graphic_manual_html_v1",
     "portionize_headings_html_v1", "build_chapter_html_v1", "validate_semantic_manual_html_v1")))


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def prepare(parent: Path, destination: Path, run_id: str):
    parent, destination = parent.resolve(), destination.resolve()
    if parent == destination or parent in destination.parents or destination in parent.parents:
        raise ValueError("parent and destination must be disjoint")
    if destination.exists():
        raise ValueError("destination must not exist")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", run_id):
        raise ValueError("run ID must be a simple new identifier")
    if destination.name != run_id:
        raise ValueError("destination directory name must equal the new run ID")
    snapshots = parent / "snapshots"
    recipe = yaml.safe_load((snapshots / "recipe.yaml").read_text())
    saved_plan = json.loads((snapshots / "plan.json").read_text())
    state = json.loads((parent / "pipeline_state.json").read_text())
    if state.get("status") != "done":
        raise ValueError("parent run must be completed")
    if run_id == state.get("run_id"):
        raise ValueError("continuation needs a new run ID")
    if any((parent / name).exists() for name in (
            "continuation_parent", "native_manual_continuation.json", "source-fidelity-continuation.yaml")):
        raise ValueError("parent must be an original standard run")
    stages = recipe["stages"]
    if {s["id"]: s["module"] for s in stages} != STANDARD_MODULES or len(stages) != len(STANDARD_MODULES):
        raise ValueError("requires the complete standard imposed-manual stage IDs/modules")
    if set(state.get("stages", {})) != set(STANDARD_MODULES):
        raise ValueError("parent state must contain exactly the original standard stages")
    registry = load_registry(str(ROOT / "modules"))["modules"]
    original_plan = build_plan(recipe, registry)
    if original_plan != saved_plan or original_plan["topo"][-1] != "validate_manual_html":
        raise ValueError("parent snapshot graph differs from current driver graph")
    pdf = Path(recipe.get("input", {}).get("pdf", ""))
    if not pdf.is_absolute() or not pdf.is_file():
        raise ValueError("parent recipe must retain an accessible absolute PDF path")
    rebased = copy.deepcopy(state)
    path_changes = {}
    for sid, module in STANDARD_MODULES.items():
        record = state.get("stages", {}).get(sid, {})
        artifact = Path(record.get("artifact", ""))
        if record.get("status") != "done" or record.get("module_id") != module or not artifact.is_file():
            raise ValueError(f"missing completed {sid} artifact/module")
        if not artifact.is_absolute() or not artifact.resolve().is_relative_to(parent):
            raise ValueError(f"{sid} artifact must be inside the parent run")
        target = destination / artifact.resolve().relative_to(parent)
        rebased["stages"][sid]["artifact"] = str(target)
        path_changes[sid] = {"before": record["artifact"], "after": str(target)}
    overlay_path = ROOT / "configs/recipes/overlays/native-manual-source-fidelity.yaml"
    appended = yaml.safe_load(overlay_path.read_text())["stages"]
    if [(s["id"], s["module"]) for s in appended] != [
            ("source_fidelity_recover", "recover_native_graphics_v1"),
            ("source_fidelity_build", "build_chapter_html_v1"),
            ("source_fidelity_validate", "validate_semantic_manual_html_v1")]:
        raise ValueError("overlay must append only offline recover/build/validate")
    if any(s["id"] in recipe.get("stage_params", {}) for s in appended):
        raise ValueError("parent must not override continuation stages")
    appended[0]["params"]["pdf"] = str(pdf)
    build_params = appended[1]["params"]
    original_build = original_plan["nodes"]["build_chapters"]["params"]
    for key in ("book_title", "book_author", "include_navigation", "suppress_navigation",
                "no_include_navigation"):
        if key in original_build:
            build_params[key] = original_build[key]
    build_params["output_dir"] = str(destination / "output/source-fidelity/html")
    validation_params = original_plan["nodes"]["validate_manual_html"]["params"]
    appended[2]["params"] = {key: validation_params[key] for key in (
        "min_figure_crop_ratio", "min_critical_target_crop_coverage", "fail_on_blocking")
        if key in validation_params}
    continuation = copy.deepcopy(recipe)
    continuation["stages"].extend(appended)
    planned = build_plan(continuation, registry)
    prefix = saved_plan["topo"]
    if planned["topo"][:len(prefix)] != prefix or any(
            planned["nodes"][sid] != saved_plan["nodes"][sid] for sid in prefix):
        raise ValueError("continuation changed the original graph prefix")
    if continuation["stages"][:len(stages)] != stages or continuation.get("stage_params") != recipe.get("stage_params"):
        raise ValueError("continuation changed original recipe stages/overrides")
    for node in (planned["nodes"][s["id"]] for s in appended):
        entrypoint = ROOT / node["entrypoint"].split(":")[0]
        if not entrypoint.is_file():
            raise ValueError(f"missing continuation module entrypoint: {entrypoint}")
        if Path(node["artifact_name"]).name != node["artifact_name"]:
            raise ValueError("continuation artifact output must be a simple filename")
        for key in ("out", "state_file", "progress_file", "run_id", "images_subdir"):
            if key in node["params"] and not (key == "images_subdir" and node["params"][key] == "images"):
                raise ValueError(f"unsafe continuation output override: {key}")
        if node["params"].get("output_dir", build_params["output_dir"]) != build_params["output_dir"]:
            raise ValueError("continuation HTML output must stay inside the clone")
    # Check all copied paths before creating anything; never retain writable source symlinks.
    files = sorted(parent.rglob("*"))
    if any(path.is_symlink() for path in files):
        raise ValueError("parent run must not contain symlinks")
    if (parent / "output/source-fidelity").exists():
        raise ValueError("parent already contains a source-fidelity output")
    if any((parent / f"{index:02d}_{planned['nodes'][sid]['module']}").exists()
           for index, sid in enumerate(planned["topo"], 1) if sid not in prefix):
        raise ValueError("parent already contains continuation stage directories")
    hashes = {str(path.relative_to(parent)): sha(path) for path in files if path.is_file()}
    receipt = {
        "parent": str(parent), "destination": str(destination), "run_id": run_id,
        "parent_required": True, "original_topo": prefix,
        "parent_graph_canonical_sha256": canonical_hash(saved_plan),
        "parent_recipe_canonical_sha256": canonical_hash(recipe),
        "parent_recipe_snapshot_sha256": sha(snapshots / "recipe.yaml"),
        "parent_plan_snapshot_sha256": sha(snapshots / "plan.json"),
        "overlay_sha256": sha(overlay_path), "artifact_path_changes": path_changes,
        "original_file_sha256": hashes,
    }
    shutil.copytree(parent, destination)
    archive = destination / "continuation_parent"
    shutil.copytree(destination / "snapshots", archive / "snapshots")
    shutil.copy2(destination / "pipeline_state.json", archive / "pipeline_state.json")
    (destination / "pipeline_state.json").write_text(json.dumps(rebased, indent=2) + "\n")
    recipe_path = destination / "source-fidelity-continuation.yaml"
    recipe_path.write_text(yaml.safe_dump(continuation, sort_keys=False))
    (destination / "native_manual_continuation.json").write_text(json.dumps(receipt, indent=2) + "\n")
    command = [sys.executable, str(ROOT / "driver.py"), "--recipe", str(recipe_path),
               "--start-from", "source_fidelity_recover", "--allow-run-id-reuse",
               "--run-id", run_id, "--output-dir", str(destination)]
    return shlex.join(command)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-run", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    try:
        print(prepare(args.parent_run, args.destination, args.run_id))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
