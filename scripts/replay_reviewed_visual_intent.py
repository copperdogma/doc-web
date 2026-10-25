"""Replay explicitly authored visual intent with existing modules, offline only.

No semantic inference, native response replay, credentials or automatic admission.
Inputs are source-reviewed authored test data, not model predictions or goldens.
"""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image
import yaml

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "scripts/reviewed_visual_intent_guard"
TEMPLATE = ROOT / "configs/recipes/recipe-reviewed-visual-intent-offline.yaml"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def read_rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def checked_file(root, relative, expected):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file() or sha(path) != expected:
        raise ValueError(f"Missing, outside-root or stale input: {relative}")
    return path


def validate_fixture(fixture):
    if (fixture.get("evidence_class") != "source-reviewed-authored-intent"
            or fixture.get("publication_status") != "review_hold"
            or not fixture.get("reviewer") or not fixture.get("policy")
            or not fixture.get("historical_run_unsafe")):
        raise ValueError("Explicit reviewed authorship, policy, hold and historical quarantine required")
    pages = set()
    ids = set()
    for case in fixture["cases"]:
        pn = case["page_number"]
        if type(pn) is not int or pn in pages or not isinstance(case.get("targets"), list):
            raise ValueError("Unique explicit pages and target lists required")
        pages.add(pn)
        if not case.get("derivation") or not case.get("mapping_review"):
            raise ValueError("Source derivation and coordinate mapping review required")
        width, height = case["dimensions"]
        for t in case["targets"]:
            if t["target_id"] in ids or t["importance"] not in {"useful", "essential"}:
                raise ValueError("Unique nondecorative reviewed targets required")
            ids.add(t["target_id"])
            b = t["bbox_pixels"]
            if not all(type(b[k]) is int for k in ("x0", "y0", "x1", "y1")):
                raise ValueError("Integer source-pixel coordinates required")
            if not (0 <= b["x0"] < b["x1"] <= width and 0 <= b["y0"] < b["y1"] <= height):
                raise ValueError("Target outside reviewed source")
            if any(k in t for k in ("model", "request_id", "detector_model", "detector_request_id")):
                raise ValueError("Authored intent cannot claim native model provenance")


def prepare(fixture_path, owner_root, result):
    from schemas import PageHtml

    fixture = json.loads(fixture_path.read_text())
    validate_fixture(fixture)
    frozen = result / "inputs"
    frozen.mkdir(parents=True, exist_ok=False)
    shutil.copy2(fixture_path, frozen / "reviewed-intent.json")
    ocr = checked_file(owner_root, fixture["ocr_artifact"], fixture["ocr_artifact_sha256"])
    shutil.copy2(ocr, frozen / "historical-ocr-native.jsonl")
    lines = {json.loads(line)["page_number"]: line for line in ocr.read_text().splitlines() if line.strip()}
    selected = []
    plan = {"schema_version": "critical_graphics_manifest_v1",
            "producer": "source-reviewed-authored-intent", "pages": []}
    highres = []
    mappings = []
    for case in fixture["cases"]:
        pn = case["page_number"]
        line = lines[pn]
        row = json.loads(line)
        if hashlib.sha256(line.encode()).hexdigest() != case["ocr_row_sha256"]:
            raise ValueError(f"Stale complete OCR row {pn}")
        PageHtml.model_validate(row)
        original = checked_file(owner_root, case["source"], case["sha256"])
        historical = checked_file(owner_root, case["historical_source"], case["historical_sha256"])
        if Path(row["image"]).resolve() != historical:
            raise ValueError("Historical OCR image binding differs from reviewed coordinate basis")
        with Image.open(original) as src, Image.open(historical) as old:
            if list(src.size) != case["dimensions"] or src.size != old.size:
                raise ValueError("Reviewed 1:1 coordinate mapping dimensions changed")
            a, b = np.asarray(src.convert("L")), np.asarray(old.convert("L"))
            overlap = float(np.logical_and(a < 100, b < 100).sum() / np.logical_or(a < 100, b < 100).sum())
            if overlap < .995:
                raise ValueError("Source registration no longer supports reviewed 1:1 mapping")
        dest = frozen / original.name
        if dest.exists():
            raise ValueError("Frozen source basename collision")
        shutil.copy2(original, dest)
        shutil.copy2(historical, frozen / ("historical-" + historical.name))
        selected.append(line)
        targets = deepcopy(case["targets"])
        for target in targets:
            target.update(source_page_number=pn, source_image=str(historical))
        plan["pages"].append({"page_number": pn, "source_image": str(historical),
                              "image_width": case["dimensions"][0],
                              "image_height": case["dimensions"][1], "targets": targets})
        highres.append({"page_number": pn, "image": str(dest)})
        mappings.append({"page_number": pn, "historical_source": str(historical),
                         "historical_sha256": sha(historical), "selected_source": str(dest),
                         "selected_sha256": sha(dest), "dimensions": case["dimensions"],
                         "coordinate_mapping": "reviewed 1:1; distinct byte identities",
                         "dark_mask_iou": overlap, "mapping_review": case["mapping_review"],
                         "target_ids": [t["target_id"] for t in targets]})
    (frozen / "selected-ocr-native.jsonl").write_text("\n".join(selected) + "\n")
    write(frozen / "critical-graphics-authored.json", plan)
    (frozen / "selected-source-manifest.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in highres))
    write(result / "coordinate-mapping.json", mappings)
    recipe = yaml.safe_load(TEMPLATE.read_text())
    recipe["stages"][0]["params"]["path"] = str(frozen / "selected-ocr-native.jsonl")
    recipe["stages"][1]["params"]["path"] = str(frozen / "critical-graphics-authored.json")
    recipe["stages"][2]["params"]["highres_manifest"] = str(frozen / "selected-source-manifest.jsonl")
    (result / "recipe.yaml").write_text(yaml.safe_dump(recipe, sort_keys=False))
    return fixture, mappings


def environment(audit):
    env = {k: os.environ[k] for k in ("PATH", "HOME", "TMPDIR", "LANG", "LC_ALL", "SYSTEMROOT") if k in os.environ}
    env.update(PYTHONPATH=str(GUARD) + os.pathsep + str(ROOT),
               REVIEWED_REPLAY_AUDIT=str(audit), PYTHONDONTWRITEBYTECODE="1")
    dependency = Path(importlib.util.find_spec("urllib3").origin).parent / "util/connection.py"
    env.update(REVIEWED_REPLAY_PROBE_SOURCE=str(dependency),
               REVIEWED_REPLAY_PROBE_SHA256=sha(dependency))
    return env


def compare_ocr_rows(before, after):
    removed = set(before) - set(after)
    added = set(after) - set(before)
    changed = {k for k in set(before) & set(after) if before[k] != after[k]}
    if (removed or changed - {"run_id", "created_at"}
            or added - {"literal_fidelity"}
            or ("literal_fidelity" in added and after["literal_fidelity"] is not None)):
        raise ValueError("Complete OCR content/presence changed beyond declared envelope/schema default")
    return {"page_number": before["page_number"], "envelope_changes": sorted(changed),
            "schema_defaults_added": {k: after[k] for k in sorted(added)},
            "html_exact": before["html"] == after["html"], "all_original_fields_retained": True}


def verify(result, run, fixture, mappings, *, proof_path=None):
    state = json.loads((run / "pipeline_state.json").read_text())
    # Resolve actual producing artifacts from the driver's durable state.
    stages = state.get("stages", state)
    ocr_path = Path(stages["reviewed_ocr"]["artifact"])
    crops_path = Path(stages["crop_reviewed"]["artifact"])
    native = read_rows(result / "inputs/selected-ocr-native.jsonl")
    copied = read_rows(ocr_path)
    if len(native) != len(copied):
        raise ValueError("OCR row coverage changed")
    changes = []
    for before, after in zip(native, copied):
        changes.append(compare_ocr_rows(before, after))
    crops = read_rows(crops_path)
    expected = {t["target_id"]: (c, t) for c in fixture["cases"] for t in c["targets"]}
    if len(crops) != len(expected) or {c.get("critical_graphics_target_id") for c in crops} != set(expected):
        raise ValueError("Crop coverage/target identity differs from reviewed intent")
    mapping = {m["page_number"]: m for m in mappings}
    pixel_checks = []
    for crop in crops:
        case, target = expected[crop["critical_graphics_target_id"]]
        validate_crop_intent(crop, case, target)
        source = Path(mapping[case["page_number"]]["selected_source"])
        if (Path(crop["source_image"]) != source or crop["source_dimensions"] != case["dimensions"]
                or crop["coordinate_system"] != "source_pixels"
                or crop["detection_method"] != "critical_graphics_manifest"
                or any(k in crop for k in ("detector_model", "detector_provider", "detector_request_id",
                                           "caption_model", "caption_provider", "caption_request_id"))):
            raise ValueError("Wrong source/geometry or fabricated model provenance")
        bbox = target["bbox_pixels"]
        if any(crop["bbox"][k] != bbox[k] for k in bbox):
            raise ValueError("Reviewed rectangle changed")
        asset = crops_path.parent / "images" / crop["filename"]
        with Image.open(source) as src, Image.open(asset) as img:
            desired = src.convert("RGB").crop(tuple(bbox[k] for k in ("x0", "y0", "x1", "y1")))
            if img.format != "PNG" or not np.array_equal(np.asarray(desired), np.asarray(img.convert("RGB"))):
                raise ValueError("Crop is not a lossless source rectangle")
        pixel_checks.append({"target_id": target["target_id"], "asset": str(asset),
                             "sha256": sha(asset), "exact_rgb": True, "bbox": crop["bbox"]})
    events = read_rows(result / "guard-audit.jsonl")
    if any(e["event"] == "denied" for e in events) or len({e["pid"] for e in events if e["event"] == "guard-installed"}) < 4:
        raise ValueError("Guard denial or missing inherited driver child guard")
    destination = proof_path or result / "proof.json"
    correction = {} if proof_path is None else {
        "verification_revision": 2, "supersedes_proof_sha256": sha(result / "proof.json"),
        "unchanged_producing_freeze_sha256": sha(result / "freeze.json"),
        "verifier_sha256": sha(Path(__file__)),
        "revision_reason": "Presence-aware OCR schema-default accounting; no driver/crop rerun"}
    write(destination, {"status": "pass", "evidence_class": "source-reviewed-authored-intent driver replay",
          "driver_run": str(run), "illustration_manifest": str(crops_path), "ocr_artifact": str(ocr_path),
          "spend_usd": 0, "provider_calls": 0, "publication_status": "review_hold",
          "historical_run_unsafe": True, "automatic_admission_proven": False,
          "detector_qualification": False, "renderer_or_text_deletion_exercised": False,
          "ocr_content_comparisons": changes, "pixel_checks": pixel_checks,
          "blocked_local_capability_probes": len([e for e in events if e["event"] == "blocked-local-capability-probe"]),
          "successful_network_connections": 0,
          "network_boundary": "CPython guard in actual driver/module children; not an OS sandbox",
          "guarded_processes": len({e["pid"] for e in events if e["event"] == "guard-installed"}), **correction})


def validate_crop_intent(crop, case, target):
    required = {"source_page": case["page_number"],
                "critical_graphics_target_id": target["target_id"],
                "critical_graphics_importance": target["importance"],
                "critical_graphics_role": target["role"],
                "critical_graphics_reason": target["reason"],
                "contains_text": target["contains_text"],
                "expected_visual_contents": target["expected_visual_contents"]}
    if any(key not in crop or crop[key] != value for key, value in required.items()):
        raise ValueError("Crop source-page/declared intent metadata mismatch")
    # The existing consumer omits optional empty nearby text; that is lossless.
    if crop.get("nearby_text", "") != target.get("nearby_text", ""):
        raise ValueError("Crop nearby source text mismatch")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--owner-source-root", type=Path, required=True)
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", args.run_id):
        raise ValueError("Safe new run ID required")
    result = args.result_dir.resolve()
    run = ROOT / "output/runs" / args.run_id
    if result.exists() or run.exists():
        raise ValueError("Replay identities must be new; reuse/force is forbidden")
    result.mkdir(parents=True)
    fixture, mappings = prepare(args.fixture.resolve(), args.owner_source_root.resolve(), result)
    code = ["driver.py", "schemas.py", "validate_artifact.py", str(TEMPLATE.relative_to(ROOT)),
            "scripts/replay_reviewed_visual_intent.py", "scripts/reviewed_visual_intent_guard/sitecustomize.py",
            "modules/common/load_artifact_v1/main.py", "modules/extract/crop_illustrations_guided_v1/main.py"]
    frozen_hashes = {str(p.relative_to(result)): sha(p) for p in (result / "inputs").iterdir()}
    write(result / "freeze.json", {"code_sha256": {p: sha(ROOT / p) for p in code},
          "inputs_sha256": frozen_hashes, "recipe_sha256": sha(result / "recipe.yaml"),
          "fixture_sha256": sha(args.fixture), "run_id": args.run_id,
          "urllib3_probe_source": environment(result / "guard-audit.jsonl")["REVIEWED_REPLAY_PROBE_SOURCE"],
          "urllib3_probe_sha256": environment(result / "guard-audit.jsonl")["REVIEWED_REPLAY_PROBE_SHA256"],
          "review_hold": True, "no_automatic_semantic_claim": True})
    command = [sys.executable, str(ROOT / "driver.py"), "--recipe", str(result / "recipe.yaml"),
               "--run-id", args.run_id, "--output-dir", str(ROOT / "output/runs")]
    write(result / "invocation.json", {"argv": command, "environment_names": sorted(environment(result / "guard-audit.jsonl")),
                                      "credential_variables": [], "environment_files": []})
    with (result / "driver.log").open("w") as log:
        completed = subprocess.run(command, cwd=ROOT, env=environment(result / "guard-audit.jsonl"),
                                   stdout=log, stderr=subprocess.STDOUT, timeout=300, check=False)
    if completed.returncode:
        raise RuntimeError(f"Driver failed ({completed.returncode}); retained {result / 'driver.log'}")
    for p, digest in frozen_hashes.items():
        if sha(result / p) != digest:
            raise ValueError("Frozen input changed during replay")
    for case in fixture["cases"]:
        checked_file(args.owner_source_root, case["source"], case["sha256"])
        checked_file(args.owner_source_root, case["historical_source"], case["historical_sha256"])
    verify(result, run, fixture, mappings)
    print(result / "proof.json")


if __name__ == "__main__":
    main()
