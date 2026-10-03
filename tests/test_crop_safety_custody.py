"""Actual-source custody preparation preserves bytes and keeps authority pending."""
import json
import os
from pathlib import Path

import pytest
from PIL import Image

from modules.common.crop_review import CropReviewError, digest
from modules.common.crop_safety_custody import prepare_custody
from modules.common.utils import read_jsonl, save_jsonl


@pytest.fixture
def inputs(tmp_path):
    sources = tmp_path / "sources"
    sources.mkdir()
    images = tmp_path / "crop-output" / "images"
    images.mkdir(parents=True)
    for number in (1, 2, 3):
        Image.new("RGB", (200, 160), (number * 30, 70, 120)).save(sources / f"native-{number}.png")
        Image.new("RGB", (100, 80), (number * 30, 70, 120)).save(sources / f"preview-{number}.png")
    rows = []
    for number in (1, 2):
        filename = f"crop-{number}.png"
        Image.new("RGBA", (75, 90), (1, 2, 3, 37)).save(images / filename)
        alpha = f"crop-{number}-alpha.png"
        Image.new("RGBA", (75, 90), (1, 2, 3, 17)).save(images / alpha)
        rows.append({
            "run_id": "actual-source-test", "source_page": number,
            "source_image": str(sources / f"native-{number}.png"),
            "source_dimensions": [200, 160], "coordinate_system": "source_pixels",
            "crop_transform": "rectangle_mask_and_encode", "filename": filename,
            "filename_alpha": alpha, "caption_box": {"x0": 1, "y0": 100, "x1": 100, "y1": 120},
            "caption_text": "Preserved nearby caption", "has_transparency": True,
            "bbox": {"x0": 10, "y0": 10, "x1": 85, "y1": 100},
        })
    manifest = images.parent / "manifest.jsonl"
    save_jsonl(manifest, rows)
    pages = tmp_path / "pages.jsonl"
    save_jsonl(pages, [{"page_number": number, "image": str(sources / f"preview-{number}.png")} for number in (1, 2, 3)])
    portions = tmp_path / "portions.jsonl"
    save_jsonl(portions, [{"page_start": 1, "page_end": 3, "title": "Native source fixture"}])
    source_map = tmp_path / "source-map.json"
    source_map.write_text(json.dumps([{"source_page": number, "source_image": str(sources / f"native-{number}.png")} for number in (1, 2, 3)]))
    return {
        "manifest_path": manifest, "pages_path": pages, "portions_path": portions,
        "source_map_path": source_map, "source_root": sources, "out_root": tmp_path / "custody",
        "run_id": "actual-source-test",
    }


def rewrite_rows(inputs, change):
    rows = list(read_jsonl(inputs["manifest_path"]))
    change(rows)
    save_jsonl(inputs["manifest_path"], rows)


def test_byte_exact_native_sources_alpha_and_pending_authority(inputs):
    originals = {path: digest(path) for path in inputs["out_root"].parent.rglob("*") if path.is_file()}
    paths = prepare_custody(**inputs)
    root = inputs["out_root"]
    assert set(paths) == {"manifest", "inventory", "proposals", "decisions", "authority"}
    assert not Path(paths["authority"]).exists() and not Path(paths["proposals"]).exists()
    assert Path(paths["decisions"]).read_text() == ""
    inventory = json.loads(Path(paths["inventory"]).read_text())
    assert inventory["complete"] is False
    assert "operator_id" not in inventory and "authority_ref" not in inventory
    assert {page["source_page"] for page in inventory["pages"]} == {1, 2, 3}
    assert len(inventory["visuals"]) == 2  # Page 3 remains explicitly inventoried despite no candidate.
    original_rows = list(read_jsonl(inputs["manifest_path"]))
    snapshot_rows = list(read_jsonl(paths["manifest"]))
    for original, snapshot in zip(original_rows, snapshot_rows):
        assert all(snapshot[key] == value for key, value in original.items() if key != "source_image")
        assert digest(root / snapshot["source_image"]) == digest(original["source_image"])
        for key in ("filename", "filename_alpha"):
            assert digest(root / "images" / original[key]) == digest(inputs["manifest_path"].parent / "images" / original[key])
        with Image.open(root / "images" / snapshot["filename"]) as image:
            assert image.mode == "RGBA" and image.getpixel((0, 0))[3] == 37
    assert (root / "originals" / "manifest.jsonl").read_bytes() == inputs["manifest_path"].read_bytes()
    assert all(path.is_file() and digest(path) == sha for path, sha in originals.items())


def test_relative_actual_source_refs_normalize_under_explicit_root(inputs):
    rewrite_rows(inputs, lambda rows: rows[0].update(source_image="native-1.png"))
    paths = prepare_custody(**inputs)
    assert list(read_jsonl(paths["manifest"]))[0]["source_image"] == "source-1.png"


@pytest.mark.parametrize("kind", ["outside", "traversal", "source_symlink", "source_parent_symlink", "root_symlink", "manifest_symlink", "crop_symlink", "alpha_symlink", "crop_traversal", "highres_override", "wrong_dimensions", "wrong_coords", "out_alias", "out_hardlink", "out_symlink", "existing_out"])
def test_unsafe_or_unproven_mapping_cannot_publish_custody(inputs, kind):
    base = inputs["out_root"].parent
    source = inputs["source_root"] / "native-1.png"
    if kind == "outside":
        outside = base / "outside.png"
        outside.write_bytes(source.read_bytes())
        rewrite_rows(inputs, lambda rows: rows[0].update(source_image=str(outside)))
    elif kind == "traversal":
        rewrite_rows(inputs, lambda rows: rows[0].update(source_image="../sources/native-1.png"))
    elif kind in ("source_symlink", "crop_symlink", "alpha_symlink"):
        target = source if kind == "source_symlink" else inputs["manifest_path"].parent / "images" / ("crop-1.png" if kind == "crop_symlink" else "crop-1-alpha.png")
        other = base / "retained-image.png"
        other.write_bytes(target.read_bytes())
        target.unlink()
        target.symlink_to(other)
    elif kind == "source_parent_symlink":
        alias = inputs["source_root"] / "alias"
        alias.symlink_to(inputs["source_root"], target_is_directory=True)
        rewrite_rows(inputs, lambda rows: rows[0].update(source_image=str(alias / "native-1.png")))
    elif kind in ("root_symlink", "manifest_symlink"):
        key = "source_root" if kind == "root_symlink" else "manifest_path"
        alias = base / "alias-input"
        alias.symlink_to(inputs[key], target_is_directory=kind == "root_symlink")
        inputs[key] = alias
    elif kind == "crop_traversal":
        rewrite_rows(inputs, lambda rows: rows[0].update(filename="../crop-1.png"))
    elif kind == "highres_override":
        rewrite_rows(inputs, lambda rows: rows[0].update(source_image=str(inputs["source_root"] / "preview-1.png")))
    elif kind == "wrong_dimensions":
        rewrite_rows(inputs, lambda rows: rows[0].update(source_dimensions=[100, 80]))
    elif kind == "wrong_coords":
        rewrite_rows(inputs, lambda rows: rows[0].update(coordinate_system="normalized_1000"))
    elif kind == "out_alias":
        inputs["out_root"] = inputs["source_root"] / "custody"
    elif kind == "out_hardlink":
        os.link(inputs["manifest_path"], inputs["out_root"])
    elif kind == "out_symlink":
        inputs["out_root"].symlink_to(inputs["source_root"], target_is_directory=True)
    else:
        inputs["out_root"].mkdir()
    before = {path: digest(path) for path in base.rglob("*") if path.is_file()}
    with pytest.raises(CropReviewError):
        prepare_custody(**inputs)
    assert {path: digest(path) for path in base.rglob("*") if path.is_file()} == before
    assert not list(base.glob(".crop-custody-*"))


@pytest.mark.parametrize("kind", ["missing_page", "duplicate_page", "extra_page", "bad_bbox", "empty_bbox", "nonfinite_bbox"])
def test_full_source_coverage_and_native_geometry_required(inputs, kind):
    if kind in ("missing_page", "duplicate_page", "extra_page"):
        path = inputs["source_map_path"]
        mapping = json.loads(path.read_text())
        if kind == "missing_page":
            mapping.pop()
        elif kind == "duplicate_page":
            mapping[-1] = mapping[0]
        else:
            mapping.append({"source_page": 4, "source_image": "native-3.png"})
        path.write_text(json.dumps(mapping))
    else:
        value = {"bad_bbox": 10**6, "empty_bbox": 10, "nonfinite_bbox": float("nan")}[kind]
        rewrite_rows(inputs, lambda rows: rows[0]["bbox"].update(x1=value))
    with pytest.raises(CropReviewError):
        prepare_custody(**inputs)
    assert not inputs["out_root"].exists()


def test_actual_encoded_source_format_not_filename_suffix(inputs):
    original = inputs["source_root"] / "native-1.png"
    Image.new("RGB", (200, 160), "white").save(original, format="JPEG")
    paths = prepare_custody(**inputs)
    row = list(read_jsonl(paths["manifest"]))[0]
    assert row["source_image"] == "source-1.jpg"
    assert digest(inputs["out_root"] / row["source_image"]) == digest(original)


@pytest.mark.parametrize("kind", ["wrong_primary_size", "wrong_alpha_size", "missing_transform", "missing_dimensions", "legacy_mask"])
def test_geometry_and_transformation_provenance_cannot_be_assumed(inputs, kind):
    if kind in ("wrong_primary_size", "wrong_alpha_size"):
        filename = "crop-1.png" if kind == "wrong_primary_size" else "crop-1-alpha.png"
        Image.new("RGBA", (20, 30)).save(inputs["manifest_path"].parent / "images" / filename)
    elif kind == "missing_transform":
        rewrite_rows(inputs, lambda rows: rows[0].pop("crop_transform"))
    elif kind == "missing_dimensions":
        rewrite_rows(inputs, lambda rows: rows[0].pop("source_dimensions"))
    else:
        def strip(rows):
            for key in ("source_dimensions", "coordinate_system", "crop_transform"):
                rows[0].pop(key)
        rewrite_rows(inputs, strip)
    with pytest.raises(CropReviewError):
        prepare_custody(**inputs)
    assert not inputs["out_root"].exists()


@pytest.mark.parametrize("changed_pixels", [False, True])
def test_legacy_requires_demonstrable_exact_source_rectangle(inputs, changed_pixels):
    rows = list(read_jsonl(inputs["manifest_path"]))[:1]
    row = rows[0]
    for key in ("coordinate_system", "source_dimensions", "crop_transform", "filename_alpha", "has_transparency"):
        row.pop(key)
    with Image.open(row["source_image"]) as source:
        crop = source.crop(tuple(row["bbox"][key] for key in ("x0", "y0", "x1", "y1")))
        if changed_pixels:
            crop.putpixel((0, 0), (255, 0, 0))
        crop.save(inputs["manifest_path"].parent / "images" / row["filename"])
    save_jsonl(inputs["manifest_path"], rows)
    if changed_pixels:
        with pytest.raises(CropReviewError):
            prepare_custody(**inputs)
        assert not inputs["out_root"].exists()
    else:
        assert Path(prepare_custody(**inputs)["manifest"]).is_file()


def test_hardlinked_input_assets_are_copied_without_mutation(inputs):
    assets = inputs["manifest_path"].parent / "images"
    alpha = assets / "crop-1-alpha.png"
    alpha.unlink()
    os.link(assets / "crop-1.png", alpha)
    sha = digest(alpha)
    paths = prepare_custody(**inputs)
    copied = Path(paths["manifest"]).parent / "images" / alpha.name
    assert digest(copied) == sha == digest(alpha)
    assert not copied.samefile(alpha)


def test_changed_source_while_copying_blocks_snapshot(inputs, monkeypatch):
    import modules.common.crop_safety_custody as custody

    original_copy = custody.shutil.copyfile
    source = inputs["source_root"] / "native-1.png"
    def change_after_copy(src, dst):
        result = original_copy(src, dst)
        if Path(src) == source:
            source.write_bytes(source.read_bytes() + b"changed-during-copy")
        return result
    monkeypatch.setattr(custody.shutil, "copyfile", change_after_copy)
    with pytest.raises(CropReviewError):
        prepare_custody(**inputs)
    assert source.exists()
    assert not inputs["out_root"].exists()
    assert not list(inputs["out_root"].parent.glob(".crop-custody-*"))


def test_guided_cover_records_actual_high_resolution_source(inputs):
    from modules.extract.crop_illustrations_guided_v1.main import crop_illustrations_guided

    native = inputs["source_root"] / "native-1.png"
    preview = inputs["source_root"] / "preview-1.png"
    pages = inputs["pages_path"]
    save_jsonl(pages, [{"page_number": 1, "image": str(preview), "image_native": str(native), "images": []}])
    output = inputs["out_root"].parent / "guided-cover"
    rows = crop_illustrations_guided(str(pages), str(output), run_id=inputs["run_id"], output_format="png", cover_pages="1", transparency=False)
    assert len(rows) == 1
    assert rows[0]["source_image"] == str(native)
    assert rows[0]["source_dimensions"] == [200, 160]
    assert rows[0]["coordinate_system"] == "source_pixels"
    assert rows[0]["crop_transform"] == "whitespace_trim_and_encode"


def test_guided_regular_crop_records_actual_high_resolution_source(inputs):
    from modules.extract.crop_illustrations_guided_v1.main import crop_illustrations_guided

    native = inputs["source_root"] / "native-1.png"
    preview = inputs["source_root"] / "preview-1.png"
    pages = inputs["pages_path"]
    save_jsonl(pages, [{"page_number": 1, "image": str(preview), "image_native": str(native), "images": []}])
    critical = inputs["out_root"].parent / "critical.json"
    with Image.open(preview) as preview_image:
        basis_width, basis_height = preview_image.size
    # The planner sees the half-size preview. Its bbox maps to the same
    # native (10, 10, 85, 100) rectangle used by this source-custody fixture.
    critical.write_text(json.dumps({
        "schema_version": "critical_graphics_manifest_v1", "pages": [{
            "page_number": 1, "image_width": basis_width, "image_height": basis_height,
            "source_image": str(preview), "targets": [{
                "target_id": "fixture-native", "source_page_number": 1,
                "source_image": str(preview), "importance": "essential", "role": "photo",
                "description": "Offline source mapping fixture",
                "bbox_pixels": {"x0": 5, "y0": 5, "x1": 42.5, "y1": 50, "width": 37.5, "height": 45},
            }],
        }],
    }))
    rows = crop_illustrations_guided(str(pages), str(inputs["out_root"].parent / "guided-regular"), run_id=inputs["run_id"], output_format="png", transparency=False, detection_mode="auto", critical_graphics_manifest=str(critical), padding_percent=0)
    assert len(rows) == 1
    assert rows[0]["source_image"] == str(native)
    assert rows[0]["source_dimensions"] == [200, 160]
    assert rows[0]["coordinate_system"] == "source_pixels"
    assert rows[0]["crop_transform"] == "rectangle_and_encode"


def test_existing_source_run_normalizes_new_review_run_without_rewriting_originals(inputs):
    from modules.common.crop_review import binding, object_digest

    original_rows = list(read_jsonl(inputs["manifest_path"]))
    original_bytes = inputs["manifest_path"].read_bytes()
    inputs["run_id"] = "new-live-review-run"
    paths = prepare_custody(**inputs)
    root = inputs["out_root"]
    normalized = list(read_jsonl(paths["manifest"]))
    for old, new in zip(original_rows, normalized):
        assert new["run_id"] == "new-live-review-run"
        assert new["custody_original_run_id"] == old["run_id"] == "actual-source-test"
        assert new["custody_original_row_sha256"] == object_digest(old)
        assert binding(new, root, inputs["run_id"], paths["manifest"])["run_id"] == "new-live-review-run"
    assert inputs["manifest_path"].read_bytes() == original_bytes
    assert (root / "originals" / "manifest.jsonl").read_bytes() == original_bytes
    inventory = json.loads(Path(paths["inventory"]).read_text())
    assert inventory["run_id"] == "new-live-review-run"
    assert inventory["original_manifest_run_id"] == "actual-source-test"


@pytest.mark.parametrize("invalid_run_id", ["", None, "another-original-run"])
def test_original_manifest_run_identity_must_be_present_and_coherent(inputs, invalid_run_id):
    rewrite_rows(inputs, lambda rows: rows[0].update(run_id=invalid_run_id))
    with pytest.raises(CropReviewError):
        prepare_custody(**inputs)
    assert not inputs["out_root"].exists()


def test_all_zero_candidate_pages_remain_pending_inventory(inputs):
    save_jsonl(inputs["manifest_path"], [])
    paths = prepare_custody(**inputs)
    inventory = json.loads(Path(paths["inventory"]).read_text())
    assert inventory["complete"] is False and inventory["visuals"] == []
    assert len(inventory["pages"]) == 3
    assert Path(paths["manifest"]).read_text() == ""


def test_stamped_page_html_none_page_number_falls_back_to_page(inputs):
    save_jsonl(inputs["pages_path"], [{"page_number": None, "page": number, "html": "<p>Stamped page fixture</p>"} for number in (1, 2, 3)])
    paths = prepare_custody(**inputs)
    inventory = json.loads(Path(paths["inventory"]).read_text())
    assert [page["source_page"] for page in inventory["pages"]] == [1, 2, 3]


def test_explicit_invalid_zero_page_number_does_not_fall_back(inputs):
    save_jsonl(inputs["pages_path"], [{"page_number": 0, "page": 1}, {"page_number": 2, "page": 2}, {"page_number": 3, "page": 3}])
    with pytest.raises(CropReviewError):
        prepare_custody(**inputs)
    assert not inputs["out_root"].exists()
