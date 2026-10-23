import io

import fitz
from PIL import Image
import pytest

from modules.common.native_catalog_graphics import (
    POLICY_ID, associate_page, recover_native_graphics, register_page, validate_native_inventory,
)


def _png(color, size=(60, 90)):
    stream = io.BytesIO()
    Image.new("RGB", size, color).save(stream, format="PNG")
    return stream.getvalue()


def _fixture(tmp_path, *, duplicate_title=False, rotated=False, nested=False, split=False):
    pdf = tmp_path / "source.pdf"
    doc = fitz.open()
    page = doc.new_page(width=400, height=400)
    labels = ["ALPHA TOKEN", "ALPHA TOKEN" if duplicate_title else "BETA TOKEN"]
    shared_image = _png("red")
    for index, x in enumerate([30, 220]):
        if nested:
            page.insert_image(fitz.Rect(x - 4, 46, x + 64, 144), stream=_png("gray", (68, 98)))
        page.insert_image(fitz.Rect(x, 50, x + 60, 140), stream=shared_image,
                          rotate=90 if rotated else 0, keep_proportion=False)
        page.insert_text((x + 70, 60), labels[index], fontsize=10)
    doc.save(pdf)
    doc.close()
    with fitz.open(pdf) as doc:
        full = tmp_path / "physical.png"
        doc[0].get_pixmap(matrix=fitz.Matrix(2, 2)).save(full)
    logical = tmp_path / "logical.png"
    with Image.open(full) as image:
        if split:
            image.crop((0, 0, 400, 800)).save(logical)
        else:
            image.save(logical)
    html = "".join(f"<h2>{label}</h2><p>Keep all rules and exceptions.</p>" for label in labels)
    row = {"page_number": 1, "original_page_number": 1, "image": str(logical),
           "spread_side": "L" if split else None, "html": html}
    physical = {"page_number": 1, "image": str(full), "source": [str(pdf)]}
    retained = tmp_path / "retained" / "images"
    retained.mkdir(parents=True)
    return pdf, row, physical, retained


def _recover(tmp_path, fixture, crops=None):
    pdf, page, physical, retained = fixture
    return recover_native_graphics(pdf_path=pdf, pages=[page], physical_pages=[physical],
        existing_crops=crops or [], existing_images=retained,
        output_images=tmp_path / "derivative" / "images", inclusion_policy=POLICY_ID, run_id="synthetic")


def test_recovers_repeated_xref_occurrences_preserving_native_orientation_and_pixels(tmp_path):
    fixture = _fixture(tmp_path, rotated=True)
    rows, report = _recover(tmp_path, fixture)
    assert len(rows) == 2
    groups = [row["native_graphics_provenance"]["native_group"] for row in rows]
    assert groups[0]["occurrences"][0]["xref"] == groups[1]["occurrences"][0]["xref"]
    assert groups[0]["bbox_pdf"] != groups[1]["bbox_pdf"]
    assert any(abs(groups[0]["occurrences"][0]["transform"][i]) > 0 for i in (1, 2))
    assert report["validation"]["recovered_decoded_source_pixels"] == "equal"
    assert report["summary"]["provider_calls"] == 0


def test_groups_nested_native_layers_instead_of_emitting_two_images(tmp_path):
    rows, _ = _recover(tmp_path, _fixture(tmp_path, nested=True))
    assert len(rows) == 2
    assert all(len(row["native_graphics_provenance"]["native_group"]["occurrences"]) == 2 for row in rows)
    assert rows[0]["bbox"] == {"x0": 52, "y0": 92, "x1": 188, "y1": 288, "width": 136, "height": 196}


def test_preserves_existing_bytes_and_uses_occurrence_geometry_not_label_identity(tmp_path):
    fixture = _fixture(tmp_path)
    _, page, _, retained = fixture
    with Image.open(page["image"]) as image:
        image.crop((60, 100, 180, 280)).save(retained / "first.png")
        # Same identity/alt but a different enlarged occurrence must not cover
        # the second small native occurrence.
        image.crop((20, 400, 180, 640)).save(retained / "enlarged.png")
    original = (retained / "first.png").read_bytes()
    crops = [
        {"source_page": 1, "source_image": page["image"], "filename": "first.png",
         "bbox": {"x0": 60, "y0": 100, "x1": 180, "y1": 280}},
        {"source_page": 1, "source_image": page["image"], "filename": "enlarged.png", "alt": "BETA TOKEN",
         "bbox": {"x0": 20, "y0": 400, "x1": 180, "y1": 640}},
    ]
    rows, report = _recover(tmp_path, fixture, crops)
    assert rows[:2] == crops
    assert len(rows) == 3
    assert rows[2]["native_graphics_provenance"]["anchor"]["label"] == "BETA TOKEN"
    assert (tmp_path / "derivative/images/first.png").read_bytes() == original
    assert report["summary"]["represented_native_occurrences"] == 1


def test_duplicate_html_and_native_titles_are_held(tmp_path):
    rows, report = _recover(tmp_path, _fixture(tmp_path, duplicate_title=True))
    assert rows == []
    assert {d["reason"] for d in report["pages"][0]["decisions"]} == {"duplicate_html_catalog_label"}


def test_protected_existing_rectangles_pass_through_and_partial_overlap_holds(tmp_path):
    fixture = _fixture(tmp_path)
    _, page, _, retained = fixture
    with Image.open(page["image"]) as image:
        image.crop((65, 110, 175, 270)).save(retained / "protected.png")
    protected = {"source_page": 1, "source_image": page["image"], "filename": "protected.png",
                 "bbox": {"x0": 65, "y0": 110, "x1": 175, "y1": 270},
                 "critical_graphics_target_id": "protected-1", "critical_graphics_importance": "essential"}
    rows, report = _recover(tmp_path, fixture, [protected])
    assert rows[0] == protected
    assert len(rows) == 2  # the other disjoint occurrence can still recover
    assert any(d["reason"] == "existing_crop_partially_overlaps_native_occurrence"
               for d in report["pages"][0]["decisions"])
    rows[0]["bbox"]["x0"] += 1
    with pytest.raises(ValueError, match="rectangles or metadata"):
        validate_native_inventory(rows, report, tmp_path / "derivative/images")


def test_missing_native_title_does_not_trigger_cv_or_ocr_fallback(tmp_path):
    fixture = _fixture(tmp_path)
    fixture[1]["html"] = "<h2>UNRELATED NAME</h2><h2>ANOTHER NAME</h2>"
    rows, report = _recover(tmp_path, fixture)
    assert rows == []
    assert {d["reason"] for d in report["pages"][0]["decisions"]} == {"native_title_missing_or_nonunique"}


def test_ambiguous_spatial_neighbor_is_held(tmp_path):
    pdf, row, physical, _ = _fixture(tmp_path)
    with fitz.open(pdf) as doc:
        mapping = register_page(row, physical, doc[0])
        # A second same-row compact title also claiming the first image creates
        # conflicting ownership, even though each title is unique.
        doc[0].insert_text((100, 64), "GAMMA TOKEN", fontsize=10)
        decisions = associate_page(doc[0], row["html"] + "<h2>GAMMA TOKEN</h2>", mapping)
    assert not any(d["status"] == "associated" for d in decisions)
    assert any(d["reason"] == "native_occurrence_has_multiple_html_owners" for d in decisions)


def test_exact_split_registration_refuses_changed_pixels_and_wrong_side(tmp_path):
    fixture = _fixture(tmp_path, split=True)
    pdf, row, physical, _ = fixture
    with fitz.open(pdf) as doc:
        assert register_page(row, physical, doc[0])["split_origin_pixels"] == [0, 0]
        with pytest.raises(ValueError, match="exact declared physical slice"):
            register_page({**row, "spread_side": "R"}, physical, doc[0])
        with Image.open(row["image"]) as image:
            image.putpixel((10, 10), (1, 2, 3))
            image.save(row["image"])
        with pytest.raises(ValueError, match="exact declared physical slice"):
            register_page(row, physical, doc[0])


def test_outside_split_occurrences_cannot_be_associated(tmp_path):
    rows, report = _recover(tmp_path, _fixture(tmp_path, split=True))
    assert rows == []  # only one source-associated entry remains: catalog gate holds it
    assert any(d["reason"] == "insufficient_repeated_catalog_entries" for d in report["pages"][0]["decisions"])


def test_sidecar_validator_rejects_crop_and_receipt_tampering(tmp_path):
    rows, report = _recover(tmp_path, _fixture(tmp_path))
    images = tmp_path / "derivative/images"
    rows[0]["bbox"]["x0"] += 1
    with pytest.raises(ValueError, match="geometry"):
        validate_native_inventory(rows, report, images)


def test_sidecar_validator_rejects_source_identity_tampering(tmp_path):
    rows, report = _recover(tmp_path, _fixture(tmp_path))
    rows[0]["source_page"] = 999
    with pytest.raises(ValueError, match="source coordinates"):
        validate_native_inventory(rows, report, tmp_path / "derivative/images")


def test_reusing_supplement_manifest_preserves_every_occurrence_without_duplication(tmp_path):
    fixture = _fixture(tmp_path)
    rows, _ = _recover(tmp_path, fixture)
    pdf, page, physical, _ = fixture
    reused_rows, report = recover_native_graphics(
        pdf_path=pdf, pages=[page], physical_pages=[physical], existing_crops=rows,
        existing_images=tmp_path / "derivative/images", output_images=tmp_path / "reused/images",
        inclusion_policy=POLICY_ID, run_id="reused")
    assert reused_rows == rows
    assert report["summary"]["recovered_occurrences"] == 0
    assert report["summary"]["represented_native_occurrences"] == 2
    for row in rows:
        assert (tmp_path / "reused/images" / row["filename"]).read_bytes() == (
            tmp_path / "derivative/images" / row["filename"]).read_bytes()


def test_rejects_implicit_policy_and_retained_output_alias(tmp_path):
    pdf, page, physical, retained = _fixture(tmp_path)
    args = dict(pdf_path=pdf, pages=[page], physical_pages=[physical], existing_crops=[],
                existing_images=retained, output_images=retained)
    with pytest.raises(ValueError, match="explicit inclusion policy"):
        recover_native_graphics(**args, inclusion_policy="")
    with pytest.raises(ValueError, match="disjoint"):
        recover_native_graphics(**args, inclusion_policy=POLICY_ID)
