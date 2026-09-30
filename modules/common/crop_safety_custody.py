"""Snapshot actual crop/source bytes for review without inventing authority."""
import json
import math
import shutil
import tempfile
from pathlib import Path

from PIL import Image

from modules.common.crop_review import binding, digest, object_digest, require
from modules.common.utils import read_jsonl, save_jsonl


def _input(path):
    path = Path(path).absolute()
    require(".." not in path.parts, "Input path traversal")
    require(not any(part.is_symlink() for part in [path, *path.parents]), "Symlinked input evidence")
    require(path.is_file(), f"Missing input evidence: {path}")
    return path


def _source(root, value):
    path = Path(value)
    require(".." not in path.parts, "Source path traversal")
    path = path if path.is_absolute() else root / path
    require(path.absolute().is_relative_to(root), "Source outside explicit source root")
    return _input(path)


def _image_metadata(path):
    with Image.open(path) as image:
        image.load()
        return {"dimensions": list(image.size), "format": image.format, "mode": image.mode}


def _write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def prepare_custody(manifest_path, pages_path, portions_path, source_map_path, source_root, out_root, run_id):
    """Create a fresh byte-exact snapshot and a pending, operator-owned inventory.

    The explicit source map is a JSON list of source_page/source_image records.
    Candidate source references must already identify those exact files. This
    operation never repairs ambiguous low-resolution/high-resolution mappings.
    """
    require(isinstance(run_id, str) and bool(run_id.strip()), "Missing custody run ID")
    root_arg = Path(source_root).absolute()
    require(not any(p.is_symlink() for p in [root_arg, *root_arg.parents]), "Symlinked source root")
    root = root_arg.resolve()
    require(root.is_dir(), "Missing source root")
    originals = {name: _input(value) for name, value in {
        "manifest": manifest_path, "pages": pages_path, "portions": portions_path, "source_map": source_map_path,
    }.items()}
    original_hashes = {path: digest(path) for path in originals.values()}
    out = Path(out_root).absolute()
    require(".." not in out.parts and not any(p.is_symlink() for p in [out, *out.parents]), "Unsafe custody output path")
    require(not out.exists(), "Custody output must be fresh")
    crops_root = originals["manifest"].parent / "images"
    protected = [root, crops_root, *originals.values()]
    for retained in protected:
        retained = retained.resolve()
        require(not out.resolve().is_relative_to(retained) and not retained.is_relative_to(out.resolve()), "Custody output aliases retained inputs")
    pages = list(read_jsonl(originals["pages"]))
    numbers = [page.get("page_number") if page.get("page_number") is not None else page.get("page") for page in pages]
    require(numbers and all(type(n) is int and n > 0 for n in numbers), "Invalid source page numbers")
    require(len(numbers) == len(set(numbers)), "Duplicate source pages")
    source_map = json.loads(originals["source_map"].read_text())
    require(isinstance(source_map, list), "Source map must be an explicit list")
    require(all(isinstance(entry, dict) and type(entry.get("source_page")) is int for entry in source_map), "Invalid source map")
    require(len(source_map) == len(numbers) and {entry["source_page"] for entry in source_map} == set(numbers), "Source map must cover every page exactly once")
    mapped = {entry["source_page"]: _source(root, entry["source_image"]) for entry in source_map}
    original_hashes.update({path: digest(path) for path in mapped.values()})
    metadata = {number: _image_metadata(path) for number, path in mapped.items()}
    rows = list(read_jsonl(originals["manifest"]))
    original_run_ids = {row.get("run_id") for row in rows}
    require(len(original_run_ids) <= 1 and all(isinstance(value, str) and value.strip() for value in original_run_ids), "Missing or conflicting original manifest run IDs")
    original_run_id = next(iter(original_run_ids), None)
    filenames = []
    assets = {}
    for row in rows:
        number = row.get("source_page")
        require(type(number) is int and number in mapped and _source(root, row["source_image"]) == mapped[number], "Candidate source differs from explicit source map")
        dimensions = metadata[number]["dimensions"]
        bbox = row["bbox"]
        require(all(type(bbox.get(k)) in (int, float) and math.isfinite(bbox[k]) for k in ("x0", "y0", "x1", "y1")), "Invalid native crop geometry")
        require(0 <= bbox["x0"] < bbox["x1"] <= dimensions[0] and 0 <= bbox["y0"] < bbox["y1"] <= dimensions[1], "Crop geometry outside mapped source")
        rounded = [round(bbox[key]) for key in ("x0", "y0", "x1", "y1")]
        crop_dimensions = [rounded[2] - rounded[0], rounded[3] - rounded[1]]
        for key in ("filename", "filename_alpha"):
            filename = row.get(key)
            if not filename:
                require(key != "filename", "Missing crop filename")
                continue
            require(isinstance(filename, str) and Path(filename).name == filename and filename not in (".", ".."), "Unsafe crop filename")
            asset = _input(crops_root / filename)
            original_hashes[asset] = digest(asset)
            crop_metadata = _image_metadata(asset)
            require(crop_metadata["dimensions"] == crop_dimensions, "Encoded crop dimensions differ from native bbox")
            require(filename not in assets, "Duplicate crop asset filename")
            assets[filename] = asset
        provenance_fields = ("coordinate_system", "source_dimensions", "crop_transform")
        if any(key in row for key in provenance_fields):
            require(row.get("coordinate_system") == "source_pixels", "Unproven crop coordinate system")
            require(row.get("source_dimensions") == dimensions, "Candidate native dimensions mismatch")
            require(row.get("crop_transform") in ("rectangle_and_encode", "rectangle_mask_and_encode", "whitespace_trim_and_encode"), "Explicit crop transformation provenance required")
        else:
            require(not row.get("filename_alpha") and not row.get("has_transparency"), "Legacy transformed crop requires explicit provenance")
            with Image.open(mapped[number]) as source, Image.open(assets[row["filename"]]) as crop:
                expected = source.crop(tuple(rounded)).convert("RGBA")
                actual = crop.convert("RGBA")
                require(expected.size == actual.size and expected.tobytes() == actual.tobytes(), "Legacy bbox is not a pixel-exact source rectangle")
        filenames.append(row["filename"])
    require(len(filenames) == len(set(filenames)), "Duplicate candidate filenames")
    # Validate everything first; a failed preparation never publishes a snapshot.
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".crop-custody-", dir=out.parent) as temporary:
        stage = Path(temporary) / "snapshot"
        stage.mkdir()
        (stage / "originals").mkdir()
        (stage / "images").mkdir()
        provenance = {}
        for name, original in originals.items():
            target = stage / "originals" / (name + original.suffix)
            shutil.copyfile(original, target)
            provenance[name] = {"original_path": str(original), "path": str(target.relative_to(stage)), "sha256": digest(target)}
        shutil.copyfile(originals["pages"], stage / "pages.jsonl")
        shutil.copyfile(originals["portions"], stage / "portions.jsonl")
        sources = []
        for number in numbers:
            info = metadata[number]
            suffix = {"PNG": "png", "JPEG": "jpg", "TIFF": "tiff", "WEBP": "webp"}.get(info["format"], mapped[number].suffix.lstrip(".") or "image")
            filename = f"source-{number}.{suffix}"
            shutil.copyfile(mapped[number], stage / filename)
            sources.append({"source_page": number, "source_image": filename, "source_sha256": digest(stage / filename), "original_source_image": str(mapped[number]), **info})
        bynumber = {entry["source_page"]: entry for entry in sources}
        for filename, original in assets.items():
            shutil.copyfile(original, stage / "images" / filename)
        normalized = [{**row, "run_id": run_id, "source_image": bynumber[row["source_page"]]["source_image"], "custody_original_run_id": row["run_id"], "custody_original_row_sha256": object_digest(row), "custody_original_source_image": row["source_image"]} for row in rows]
        save_jsonl(stage / "manifest.jsonl", normalized)
        bindings = [binding(row, stage, run_id, stage / "manifest.jsonl") for row in normalized]
        inventory = {
            "run_id": run_id, "complete": False, "status": "pending_operator_inventory",
            "original_manifest_run_id": original_run_id,
            "pages": sources,
            "pages_artifact": {"path": "pages.jsonl", "sha256": digest(stage / "pages.jsonl")},
            "portions_artifact": {"path": "portions.jsonl", "sha256": digest(stage / "portions.jsonl")},
            "original_artifacts": provenance,
            "visuals": [{"visual_id": f"candidate-visual-{index}", "source_page": row["source_page"], "candidate_ids": [bound["candidate_id"]]} for index, (row, bound) in enumerate(zip(normalized, bindings), 1)],
            "operator_note": "Inspect every source page, including zero-candidate pages; identify missed visuals and assert complete inventory with explicit authority before release.",
        }
        _write(stage / "inventory.json", inventory)
        (stage / "decisions.jsonl").write_text("")
        _write(stage / "custody_provenance.json", {"run_id": run_id, "original_manifest_run_id": original_run_id, "original_artifacts": provenance, "pages": sources, "crops": [{"filename": name, "sha256": digest(stage / "images" / name), "original_path": str(original), **_image_metadata(original)} for name, original in assets.items()]})
        for original, sha256 in original_hashes.items():
            require(digest(original) == sha256, "Original evidence changed during custody preparation")
        for name, original in originals.items():
            require(provenance[name]["sha256"] == original_hashes[original], "Original artifact copy changed")
        for page in sources:
            require(page["source_sha256"] == original_hashes[mapped[page["source_page"]]], "Source image copy changed")
        for filename, original in assets.items():
            require(digest(stage / "images" / filename) == original_hashes[original], "Crop asset copy changed")
        require(not out.exists(), "Custody output appeared during preparation")
        stage.rename(out)
    return {key: str(out / filename) for key, filename in {
        "manifest": "manifest.jsonl", "inventory": "inventory.json", "proposals": "proposals.jsonl", "decisions": "decisions.jsonl", "authority": "authority.json",
    }.items()}
