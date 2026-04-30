import cv2
import json
import numpy as np
from PIL import Image

from modules.extract.crop_illustrations_guided_v1.main import (
    _apply_caption_box,
    _apply_rule_panel_child_metadata,
    _align_descriptions_to_detected_boxes,
    _expand_dense_boxes_with_upper_panels,
    _expand_integrated_callout_rule_example_box,
    _expand_player_mat_register_rule_example_box,
    _expand_rule_panel_placement_layout_box,
    _group_rule_panel_placement_layout,
    _is_text_only_rule_panel_split_box,
    _mask_rule_panel_placement_layout_prose,
    _split_mixed_rule_panel_visual_clusters,
    _should_mask_text_heavy_rule_panel,
    _merge_stacked_dense_components,
    _mask_detached_map_background,
    _should_split_card_reference_panel,
    _prune_stale_crop_images,
    _split_card_reference_panel_boxes,
    _split_dense_reference_boxes,
    _split_text_heavy_rule_panel_boxes,
    _trim_rule_panel_cost_reference_card,
    _trim_rule_example_bottom_prose_band,
    crop_illustrations_guided,
)


def test_apply_caption_box_keeps_partial_width_caption_from_clipping_irregular_image():
    box = {
        "x0": 602,
        "y0": 4300,
        "x1": 3723,
        "y1": 5900,
        "width": 3121,
        "height": 1600,
        "caption_box": {
            "x0": 2270,
            "y0": 5082,
            "x1": 3254,
            "y1": 5907,
        },
    }

    result = _apply_caption_box(box, margin_px=4, max_gap_ratio=0.15)

    assert result["y0"] == box["y0"]
    assert result["y1"] == box["y1"]
    assert result["height"] == box["height"]


def test_apply_caption_box_trims_when_caption_spans_most_of_crop_width():
    box = {
        "x0": 100,
        "y0": 200,
        "x1": 1100,
        "y1": 1200,
        "width": 1000,
        "height": 1000,
        "caption_box": {
            "x0": 150,
            "y0": 950,
            "x1": 1050,
            "y1": 1125,
        },
    }

    result = _apply_caption_box(box, margin_px=4, max_gap_ratio=0.15)

    assert result["y0"] == box["y0"]
    assert result["y1"] == 946
    assert result["height"] == 746
    assert result["_caption_applied"] is True


def test_prune_stale_crop_images_removes_unmanifested_files_on_full_rerun(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    keep = images_dir / "page-122-000.jpg"
    stale = images_dir / "page-122-002.jpg"
    keep.write_bytes(b"keep")
    stale.write_bytes(b"stale")

    removed = _prune_stale_crop_images(
        str(images_dir),
        keep_filenames={"page-122-000.jpg"},
    )

    assert removed == 1
    assert keep.exists()
    assert not stale.exists()


def test_split_dense_reference_boxes_recovers_repeated_visual_blocks(tmp_path):
    page_path = tmp_path / "dense-reference.png"
    canvas = np.full((1000, 800, 3), 238, dtype=np.uint8)
    colors = [
        (30, 80, 220),
        (30, 180, 40),
        (200, 60, 60),
        (180, 140, 20),
        (120, 60, 180),
        (20, 170, 190),
    ]
    positions = [(80, 100), (430, 100), (80, 390), (430, 390), (80, 680), (430, 680)]
    for (x, y), color in zip(positions, colors):
        cv2.rectangle(canvas, (x, y), (240 + x, 230 + y), color, thickness=-1)
        cv2.rectangle(canvas, (x, y), (240 + x, 230 + y), (10, 10, 10), thickness=8)
        for line_idx in range(3):
            yy = y + 255 + line_idx * 22
            cv2.line(canvas, (x, yy), (x + 230, yy), (30, 30, 30), thickness=3)
    cv2.imwrite(str(page_path), canvas)

    boxes = _split_dense_reference_boxes(
        str(page_path),
        [
            {
                "x0": 0,
                "y0": 0,
                "x1": 800,
                "y1": 1000,
                "width": 800,
                "height": 1000,
                "area_ratio": 1.0,
            }
        ],
        expected_count=6,
        min_expected_count=3,
        min_overbroad_area_ratio=0.35,
        saturation_threshold=35,
        min_component_area_ratio=0.01,
        max_component_area_ratio=0.2,
        padding_percent=0.01,
    )

    assert len(boxes) == 6
    assert {box["_detection_method"] for box in boxes} == {"cv_guided_dense_split"}
    assert boxes[0]["x0"] < boxes[1]["x0"]
    assert boxes[0]["y0"] < boxes[2]["y0"]
    assert boxes[-1]["x0"] > boxes[-2]["x0"]


def test_align_descriptions_skips_text_callout_when_crop_detector_found_visuals_only():
    descriptions = [
        "Card face A",
        "Callout labeled Important Note",
        "Card face B",
    ]
    boxes = [
        {"x0": 0, "y0": 0, "x1": 10, "y1": 20},
        {"x0": 20, "y0": 0, "x1": 30, "y1": 20},
    ]

    assert _align_descriptions_to_detected_boxes(descriptions, boxes) == [
        "Card face A",
        "Card face B",
    ]


def test_merge_stacked_dense_components_combines_card_title_and_body_panels():
    boxes = [
        {"x0": 100, "y0": 100, "x1": 260, "y1": 150, "width": 160, "height": 50, "area": 8000},
        {"x0": 100, "y0": 158, "x1": 260, "y1": 330, "width": 160, "height": 172, "area": 27520},
        {"x0": 100, "y0": 430, "x1": 260, "y1": 480, "width": 160, "height": 50, "area": 8000},
        {"x0": 100, "y0": 488, "x1": 260, "y1": 660, "width": 160, "height": 172, "area": 27520},
    ]

    merged = _merge_stacked_dense_components(boxes, img_w=800, img_h=1000)

    assert len(merged) == 2
    assert merged[0]["y0"] == 100
    assert merged[0]["y1"] == 330
    assert merged[0]["_dense_component_merge_count"] == 2
    assert merged[1]["y0"] == 430
    assert merged[1]["y1"] == 660


def test_expand_dense_boxes_with_upper_panels_includes_card_header():
    canvas = np.full((400, 300, 3), 240, dtype=np.uint8)
    cv2.rectangle(canvas, (80, 60), (210, 105), (20, 20, 20), thickness=-1)
    cv2.rectangle(canvas, (80, 120), (210, 260), (25, 25, 25), thickness=-1)
    box = {"x0": 80, "y0": 120, "x1": 210, "y1": 260, "width": 130, "height": 140, "area": 18200}

    expanded = _expand_dense_boxes_with_upper_panels(canvas, [box])

    assert expanded[0]["y0"] <= 60
    assert expanded[0]["y1"] == 260
    assert expanded[0]["_dense_upper_panel_expanded"] is True


def test_cropper_uses_critical_graphics_manifest_as_source_pixel_crop_intent(tmp_path):
    page_path = tmp_path / "page-001.png"
    canvas = np.full((120, 160, 3), 245, dtype=np.uint8)
    cv2.rectangle(canvas, (20, 30), (110, 95), (20, 80, 220), thickness=-1)
    cv2.imwrite(str(page_path), canvas)
    ocr_manifest = tmp_path / "pages_html.jsonl"
    ocr_manifest.write_text(
        json.dumps({"page_number": 1, "image": str(page_path), "html": "<h1>Setup</h1>"}) + "\n",
        encoding="utf-8",
    )
    critical_manifest = tmp_path / "critical_graphics_manifest.json"
    critical_manifest.write_text(
        json.dumps(
            {
                "schema_version": "critical_graphics_manifest_v1",
                "summary": {"essential_count": 1},
                "pages": [
                    {
                        "page_number": 1,
                        "targets": [
                            {
                                "target_id": "p001-g01",
                                "importance": "essential",
                                "role": "setup_diagram",
                                "description": "Setup diagram",
                                "reason": "Shows component placement.",
                                "bbox_pixels": {"x0": 20, "y0": 30, "x1": 110, "y1": 95, "width": 90, "height": 65},
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    manifest = crop_illustrations_guided(
        ocr_manifest=str(ocr_manifest),
        output_dir=str(tmp_path / "out"),
        output_format="png",
        critical_graphics_manifest=str(critical_manifest),
        detection_mode="auto",
        padding_percent=0.2,
    )

    assert len(manifest) == 1
    record = manifest[0]
    assert record["bbox"] == {"x0": 20, "y0": 30, "x1": 110, "y1": 95, "width": 90, "height": 65}
    assert record["detection_method"] == "critical_graphics_manifest"
    assert record["critical_graphics_target_id"] == "p001-g01"
    assert (tmp_path / "out" / "images" / record["filename"]).exists()


def test_cropper_does_not_mask_integrated_callout_rule_diagrams():
    assert _should_mask_text_heavy_rule_panel(
        {
            "_critical_graphics_role": "rule_example_diagram",
            "area_ratio": 0.32,
            "_description": "Purchasing upgrades example panel with cards and upgrade mat.",
        }
    )
    assert not _should_mask_text_heavy_rule_panel(
        {
            "_critical_graphics_role": "rule_example_diagram",
            "area_ratio": 0.32,
            "_description": "Board example with yellow callout boxes pointing to the spaces.",
        }
    )
    assert not _should_mask_text_heavy_rule_panel(
        {
            "_critical_graphics_role": "rule_example_diagram",
            "area_ratio": 0.08,
            "_description": "Small rule example diagram.",
        }
    )


def test_split_text_heavy_rule_panel_boxes_keeps_visual_children_without_prose_panel(tmp_path):
    page_path = tmp_path / "rule-panel.png"
    canvas = np.full((900, 900, 3), 238, dtype=np.uint8)
    for idx in range(5):
        y = 80 + idx * 48
        cv2.line(canvas, (260, y), (830, y), (25, 25, 25), thickness=4)
    cv2.rectangle(canvas, (70, 80), (210, 300), (40, 190, 230), thickness=-1)
    cv2.rectangle(canvas, (600, 390), (760, 650), (60, 210, 80), thickness=-1)
    cv2.rectangle(canvas, (95, 620), (250, 835), (230, 60, 60), thickness=-1)
    cv2.rectangle(canvas, (350, 610), (830, 835), (70, 170, 220), thickness=-1)
    cv2.imwrite(str(page_path), canvas)

    boxes = _split_text_heavy_rule_panel_boxes(
        str(page_path),
        [
            {
                "x0": 0,
                "y0": 0,
                "x1": 900,
                "y1": 900,
                "width": 900,
                "height": 900,
                "area_ratio": 1.0,
                "_critical_graphics_role": "rule_example_diagram",
                "_critical_graphics_importance": "essential",
                "_critical_graphics_target_id": "p001-g01",
                "_description": "Purchasing upgrades example panel with cards and player mat.",
                "_nearby_text": (
                    "To purchase an upgrade, look at the number in the top left-hand corner of the card. "
                    "If you've purchased a permanent upgrade, place it on one of the upgrade slots on your player mat. "
                    "If you've purchased a temporary upgrade, place it in front of your player mat."
                ),
                "_expected_visual_contents": ["yellow card", "green card", "red card", "player mat"],
            }
        ],
        saturation_threshold=35,
        min_component_area_ratio=0.005,
        max_component_area_ratio=0.25,
        padding_percent=0.01,
    )

    assert len(boxes) >= 2
    assert {box["_detection_method"] for box in boxes} == {"cv_guided_rule_panel_split"}
    assert all(str(box["_critical_graphics_target_id"]).startswith("p001-g01-part-") for box in boxes)
    assert all(box["area_ratio"] < 0.6 for box in boxes)


def test_rule_panel_split_skips_text_only_prominence_box():
    canvas = np.full((360, 440, 3), 238, dtype=np.uint8)
    for idx, text in enumerate(["Once all players", "finish purchasing", "proceed to the", "programming phase"]):
        cv2.putText(canvas, text, (28, 70 + idx * 62), cv2.FONT_HERSHEY_SIMPLEX, 1.15, (120, 45, 35), 4)

    assert _is_text_only_rule_panel_split_box(
        canvas,
        {"x0": 0, "y0": 0, "x1": 440, "y1": 360, "width": 440, "height": 360},
    )


def test_rule_panel_split_refines_mixed_visual_cluster_with_empty_prose_corner():
    canvas = np.full((850, 1200, 3), 238, dtype=np.uint8)
    for idx in range(5):
        cv2.line(canvas, (20, 60 + idx * 42), (520, 60 + idx * 42), (40, 40, 40), thickness=3)
    cv2.rectangle(canvas, (640, 35), (850, 420), (40, 185, 220), thickness=-1)
    cv2.rectangle(canvas, (890, 35), (1100, 420), (40, 210, 90), thickness=-1)
    cv2.rectangle(canvas, (35, 460), (260, 820), (220, 65, 65), thickness=-1)
    cv2.rectangle(canvas, (300, 600), (1125, 810), (70, 170, 220), thickness=-1)

    refined = _split_mixed_rule_panel_visual_clusters(
        canvas,
        {"x0": 0, "y0": 0, "x1": 1200, "y1": 850, "width": 1200, "height": 850},
    )

    assert len(refined) == 2
    assert refined[0]["x0"] > 600
    assert refined[0]["y1"] < 450
    assert refined[1]["x0"] < 80
    assert refined[1]["y0"] > 430


def test_rule_panel_placement_layout_groups_spatially_related_children():
    canvas = np.full((1000, 1000, 3), 238, dtype=np.uint8)
    original = {
        "x0": 100,
        "y0": 100,
        "x1": 900,
        "y1": 900,
        "width": 800,
        "height": 800,
        "_description": "Upgrade purchase and placement example.",
        "_nearby_text": (
            "To purchase an upgrade, look at the number in the top left-hand corner of the card. "
            "If you've purchased a permanent upgrade, place it on one of the upgrade slots on your player mat. "
            "If you've purchased a temporary upgrade, place it in front of your player mat."
        ),
        "_expected_visual_contents": ["cost card", "installed upgrade cards", "temporary card", "player mat"],
    }
    boxes = [
        {"x0": 140, "y0": 160, "x1": 280, "y1": 420, "width": 140, "height": 260, "area": 36400},
        {"x0": 610, "y0": 520, "x1": 850, "y1": 710, "width": 240, "height": 190, "area": 45600},
        {"x0": 300, "y0": 700, "x1": 430, "y1": 870, "width": 130, "height": 170, "area": 22100},
        {"x0": 460, "y0": 705, "x1": 850, "y1": 880, "width": 390, "height": 175, "area": 68250},
    ]

    grouped = _group_rule_panel_placement_layout(original, boxes, canvas)

    assert len(grouped) == 2
    assert grouped[0]["_rule_panel_child_kind"] == "cost_reference"
    assert grouped[1]["_rule_panel_child_kind"] == "placement_layout"
    assert grouped[1]["x0"] == 300
    assert grouped[1]["x1"] == 850
    assert grouped[1]["y0"] == 520
    assert grouped[1]["y1"] == 880


def test_rule_panel_cost_child_context_avoids_placement_sentences():
    original = {
        "_nearby_text": (
            "To purchase an upgrade, look at the number in the top left-hand corner of the card. "
            "This is the number of energy cubes you must pay to purchase the card. "
            "If you've purchased a permanent upgrade, place it on one of the upgrade slots on your player mat. "
            "If you've purchased a temporary upgrade, place it in front of your player mat."
        )
    }
    child = {"_rule_panel_child_kind": "cost_reference"}

    _apply_rule_panel_child_metadata(child, original)

    assert "top left-hand corner" in child["_nearby_text"]
    assert "pay to purchase" in child["_nearby_text"]
    assert "permanent upgrade" not in child["_nearby_text"]
    assert "temporary upgrade" not in child["_nearby_text"]


def test_cost_reference_child_trims_right_prose_without_vertical_cropping(tmp_path):
    page_path = tmp_path / "cost-reference.png"
    canvas = np.full((420, 520, 3), 238, dtype=np.uint8)
    cv2.rectangle(canvas, (20, 12), (260, 405), (15, 15, 15), thickness=-1)
    cv2.rectangle(canvas, (42, 34), (238, 382), (40, 190, 220), thickness=-1)
    cv2.circle(canvas, (72, 58), 34, (25, 25, 25), thickness=-1)
    cv2.line(canvas, (72, 58), (72, 285), (20, 20, 230), thickness=4)
    cv2.line(canvas, (72, 285), (480, 285), (20, 20, 230), thickness=4)
    cv2.putText(canvas, "To purchase an upgrade", (300, 305), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (30, 30, 30), 2)
    cv2.imwrite(str(page_path), canvas)

    trimmed = _trim_rule_panel_cost_reference_card(
        str(page_path),
        {
            "x0": 0,
            "y0": 0,
            "x1": 520,
            "y1": 420,
            "width": 520,
            "height": 420,
            "_rule_panel_child_kind": "cost_reference",
        },
    )

    assert trimmed["x1"] < 300
    assert trimmed["y1"] == 420
    assert trimmed["_trimmed_rule_panel_cost_reference"] is True


def test_placement_layout_expands_bottom_and_masks_upper_prose(tmp_path):
    page_path = tmp_path / "placement-layout.png"
    canvas = np.full((760, 900, 3), 238, dtype=np.uint8)
    for idx in range(4):
        cv2.line(canvas, (20, 50 + idx * 34), (500, 50 + idx * 34), (35, 35, 35), thickness=3)
    cv2.rectangle(canvas, (590, 20), (720, 250), (35, 210, 220), thickness=-1)
    cv2.rectangle(canvas, (55, 360), (210, 710), (50, 70, 210), thickness=-1)
    cv2.rectangle(canvas, (260, 330), (850, 700), (80, 180, 220), thickness=-1)
    cv2.imwrite(str(page_path), canvas)

    box = {
        "x0": 0,
        "y0": 0,
        "x1": 900,
        "y1": 700,
        "width": 900,
        "height": 700,
        "_rule_panel_child_kind": "placement_layout",
    }
    expanded = _expand_rule_panel_placement_layout_box(str(page_path), box)
    assert expanded["y1"] > box["y1"]
    not_callout_expanded = _expand_integrated_callout_rule_example_box(
        str(page_path),
        {
            **box,
            "_critical_graphics_role": "rule_example_diagram",
            "_description": "Card placement layout with yellow cards and red callout lines.",
        },
    )
    assert not_callout_expanded["y1"] == box["y1"]

    cropped = Image.fromarray(cv2.cvtColor(canvas[:700, :900], cv2.COLOR_BGR2RGB))
    masked = _mask_rule_panel_placement_layout_prose(cropped, box)
    assert masked is not None
    alpha = np.asarray(masked)[:, :, 3]
    assert masked.width < cropped.width
    assert float(np.mean(alpha > 0)) < 0.9
    assert np.any(alpha[:, -160:] == 255)
    assert np.any(alpha[-160:, :] == 255)


def test_player_mat_register_target_expands_up_to_nearby_header(tmp_path):
    page_path = tmp_path / "player-mat-register.png"
    canvas = np.full((760, 1000, 3), 238, dtype=np.uint8)
    cv2.rectangle(canvas, (90, 118), (190, 218), (15, 80, 210), thickness=-1)
    cv2.rectangle(canvas, (210, 150), (370, 190), (30, 30, 170), thickness=-1)
    cv2.rectangle(canvas, (90, 220), (930, 650), (205, 205, 205), thickness=-1)
    cv2.rectangle(canvas, (105, 300), (250, 520), (40, 170, 230), thickness=-1)
    cv2.rectangle(canvas, (280, 500), (420, 690), (45, 45, 45), thickness=-1)
    cv2.rectangle(canvas, (450, 500), (590, 690), (45, 45, 45), thickness=-1)
    cv2.imwrite(str(page_path), canvas)

    expanded = _expand_player_mat_register_rule_example_box(
        str(page_path),
        {
            "x0": 70,
            "y0": 230,
            "x1": 950,
            "y1": 700,
            "width": 880,
            "height": 470,
            "_critical_graphics_role": "rule_example_diagram",
            "_description": "Player mat showing the first register programmed with a card.",
            "_expected_visual_contents": ["player mat", "first register", "energy reserve"],
        },
    )

    assert expanded["y0"] < 125
    assert expanded["_expanded_player_mat_register_top"] is True


def test_player_mat_register_expansion_ignores_introductory_prose(tmp_path):
    page_path = tmp_path / "player-mat-with-prose-above.png"
    canvas = np.full((760, 1000, 3), 238, dtype=np.uint8)
    cv2.putText(
        canvas,
        "Take a look at how players programmed their robots",
        (20, 185),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (35, 35, 35),
        3,
    )
    cv2.rectangle(canvas, (90, 272), (930, 650), (205, 205, 205), thickness=-1)
    cv2.line(canvas, (210, 245), (930, 245), (35, 35, 210), thickness=4)
    cv2.rectangle(canvas, (90, 232), (210, 282), (35, 80, 210), thickness=-1)
    cv2.rectangle(canvas, (105, 350), (250, 540), (40, 170, 230), thickness=-1)
    cv2.rectangle(canvas, (280, 520), (420, 700), (45, 45, 45), thickness=-1)
    cv2.rectangle(canvas, (450, 520), (590, 700), (45, 45, 45), thickness=-1)
    cv2.imwrite(str(page_path), canvas)

    expanded = _expand_player_mat_register_rule_example_box(
        str(page_path),
        {
            "x0": 70,
            "y0": 290,
            "x1": 950,
            "y1": 710,
            "width": 880,
            "height": 420,
            "_critical_graphics_role": "rule_example_diagram",
            "_description": "Player mat showing the first register programmed with a card.",
            "_expected_visual_contents": ["player mat", "first register", "energy reserve"],
        },
    )

    assert expanded["y0"] >= 200
    assert expanded["y0"] < 260
    assert expanded["_expanded_player_mat_register_top"] is True


def test_integrated_callout_rule_example_expands_when_cutting_colored_panel(tmp_path):
    page_path = tmp_path / "integrated-callout.png"
    canvas = np.full((760, 900, 3), 238, dtype=np.uint8)
    cv2.rectangle(canvas, (100, 100), (800, 430), (170, 170, 170), thickness=-1)
    cv2.rectangle(canvas, (145, 440), (760, 650), (0, 230, 245), thickness=-1)
    cv2.putText(canvas, "1. Integrated callout text", (170, 540), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (25, 25, 25), 3)
    cv2.imwrite(str(page_path), canvas)

    expanded = _expand_integrated_callout_rule_example_box(
        str(page_path),
        {
            "x0": 100,
            "y0": 100,
            "x1": 800,
            "y1": 500,
            "width": 700,
            "height": 400,
            "_critical_graphics_role": "rule_example_diagram",
            "_description": "Board diagram with yellow callout boxes and numbered steps.",
        },
    )

    assert expanded["y1"] > 640
    assert expanded["_expanded_integrated_callouts"] is True


def test_integrated_callout_expansion_ignores_detached_page_decoration(tmp_path):
    page_path = tmp_path / "integrated-callout-with-footer.png"
    canvas = np.full((900, 900, 3), 238, dtype=np.uint8)
    cv2.rectangle(canvas, (100, 100), (800, 430), (170, 170, 170), thickness=-1)
    cv2.rectangle(canvas, (145, 440), (760, 650), (0, 230, 245), thickness=-1)
    cv2.rectangle(canvas, (0, 820), (220, 890), (0, 230, 245), thickness=-1)
    cv2.imwrite(str(page_path), canvas)

    expanded = _expand_integrated_callout_rule_example_box(
        str(page_path),
        {
            "x0": 100,
            "y0": 100,
            "x1": 800,
            "y1": 500,
            "width": 700,
            "height": 400,
            "_critical_graphics_role": "rule_example_diagram",
            "_description": "Board diagram with yellow callout boxes and numbered steps.",
        },
    )

    assert expanded["y1"] < 720
    assert expanded["_expanded_integrated_callouts"] is True


def test_trim_bottom_prose_band_handles_component_reference_and_tiny_text_strip(tmp_path):
    page_path = tmp_path / "component-with-bottom-prose.png"
    canvas = np.full((420, 520, 3), 238, dtype=np.uint8)
    cv2.rectangle(canvas, (90, 60), (430, 310), (60, 180, 210), thickness=-1)
    cv2.rectangle(canvas, (90, 60), (430, 310), (30, 30, 30), thickness=6)
    cv2.putText(canvas, "Here are two examples", (22, 404), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (25, 25, 25), 3)
    cv2.imwrite(str(page_path), canvas)

    trimmed = _trim_rule_example_bottom_prose_band(
        str(page_path),
        {
            "x0": 0,
            "y0": 0,
            "x1": 520,
            "y1": 420,
            "width": 520,
            "height": 420,
            "_critical_graphics_role": "component_reference",
        },
    )

    assert trimmed["y1"] < 404
    assert trimmed["_trimmed_rule_example_bottom_prose"] is True


def test_cropper_preserves_critical_target_descriptions_after_reading_order_sort(tmp_path):
    page_path = tmp_path / "page-001.png"
    canvas = np.full((120, 220, 3), 245, dtype=np.uint8)
    cv2.rectangle(canvas, (20, 30), (80, 90), (20, 80, 220), thickness=-1)
    cv2.rectangle(canvas, (140, 28), (200, 88), (220, 80, 20), thickness=-1)
    cv2.imwrite(str(page_path), canvas)
    ocr_manifest = tmp_path / "pages_html.jsonl"
    ocr_manifest.write_text(
        json.dumps({"page_number": 1, "image": str(page_path), "html": "<h1>Reference</h1>"}) + "\n",
        encoding="utf-8",
    )
    critical_manifest = tmp_path / "critical_graphics_manifest.json"
    # The right-hand target starts two pixels higher. A naive y/x sort of target
    # descriptions would place it before the left target, while reading-order
    # row sorting correctly emits the left crop first.
    critical_manifest.write_text(
        json.dumps(
            {
                "schema_version": "critical_graphics_manifest_v1",
                "summary": {"essential_count": 2},
                "pages": [
                    {
                        "page_number": 1,
                        "targets": [
                            {
                                "target_id": "p001-g01",
                                "importance": "essential",
                                "role": "card_face",
                                "description": "Right card",
                                "reason": "Shows the right card.",
                                "bbox_pixels": {"x0": 140, "y0": 28, "x1": 200, "y1": 88, "width": 60, "height": 60},
                            },
                            {
                                "target_id": "p001-g02",
                                "importance": "essential",
                                "role": "card_face",
                                "description": "Left card",
                                "reason": "Shows the left card.",
                                "bbox_pixels": {"x0": 20, "y0": 30, "x1": 80, "y1": 90, "width": 60, "height": 60},
                            },
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    manifest = crop_illustrations_guided(
        ocr_manifest=str(ocr_manifest),
        output_dir=str(tmp_path / "out"),
        output_format="png",
        critical_graphics_manifest=str(critical_manifest),
        detection_mode="auto",
        padding_percent=0.0,
    )

    assert [record["bbox"]["x0"] for record in manifest] == [20, 140]
    assert [record["critical_graphics_target_id"] for record in manifest] == ["p001-g02", "p001-g01"]
    assert manifest[0]["alt"].startswith("Left card")
    assert manifest[1]["alt"].startswith("Right card")


def test_cropper_keeps_critical_manifest_bboxes_tight_even_when_detector_padding_is_enabled(tmp_path):
    page_path = tmp_path / "page-001.png"
    canvas = np.full((200, 200, 3), 245, dtype=np.uint8)
    cv2.rectangle(canvas, (50, 80), (150, 140), (20, 80, 220), thickness=-1)
    cv2.imwrite(str(page_path), canvas)
    ocr_manifest = tmp_path / "pages_html.jsonl"
    ocr_manifest.write_text(
        json.dumps({"page_number": 1, "image": str(page_path), "html": "<h1>Example</h1>"}) + "\n",
        encoding="utf-8",
    )
    critical_manifest = tmp_path / "critical_graphics_manifest.json"
    critical_manifest.write_text(
        json.dumps(
            {
                "schema_version": "critical_graphics_manifest_v1",
                "summary": {"essential_count": 1},
                "pages": [
                    {
                        "page_number": 1,
                        "targets": [
                            {
                                "target_id": "p001-g01",
                                "importance": "essential",
                                "role": "rule_example_diagram",
                                "description": "Diagram with integrated callouts",
                                "reason": "Shows spatial relation.",
                                "bbox_pixels": {"x0": 50, "y0": 80, "x1": 150, "y1": 140, "width": 100, "height": 60},
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    manifest = crop_illustrations_guided(
        ocr_manifest=str(ocr_manifest),
        output_dir=str(tmp_path / "out"),
        output_format="png",
        critical_graphics_manifest=str(critical_manifest),
        detection_mode="auto",
        padding_percent=0.1,
    )

    assert manifest[0]["bbox"] == {"x0": 50, "y0": 80, "x1": 150, "y1": 140, "width": 100, "height": 60}


def test_cropper_adds_small_safety_margin_for_component_reference_targets(tmp_path):
    page_path = tmp_path / "page-001.png"
    canvas = np.full((200, 200, 3), 245, dtype=np.uint8)
    cv2.rectangle(canvas, (50, 50), (100, 100), (20, 80, 220), thickness=-1)
    cv2.imwrite(str(page_path), canvas)
    ocr_manifest = tmp_path / "pages_html.jsonl"
    ocr_manifest.write_text(
        json.dumps({"page_number": 1, "image": str(page_path), "html": "<h1>Reference</h1>"}) + "\n",
        encoding="utf-8",
    )
    critical_manifest = tmp_path / "critical_graphics_manifest.json"
    critical_manifest.write_text(
        json.dumps(
            {
                "schema_version": "critical_graphics_manifest_v1",
                "summary": {"essential_count": 1},
                "pages": [
                    {
                        "page_number": 1,
                        "targets": [
                            {
                                "target_id": "p001-g01",
                                "importance": "useful",
                                "role": "component_reference",
                                "description": "Small component reference",
                                "reason": "Shows the component.",
                                "bbox_pixels": {"x0": 50, "y0": 50, "x1": 100, "y1": 100, "width": 50, "height": 50},
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    manifest = crop_illustrations_guided(
        ocr_manifest=str(ocr_manifest),
        output_dir=str(tmp_path / "out"),
        output_format="png",
        critical_graphics_manifest=str(critical_manifest),
        detection_mode="auto",
        padding_percent=0.0,
    )

    assert manifest[0]["bbox"] == {"x0": 47, "y0": 47, "x1": 103, "y1": 103, "width": 56, "height": 56}


def test_mask_detached_map_background_removes_corner_text_but_keeps_map_pixels():
    canvas = np.full((420, 520, 3), 235, dtype=np.uint8)
    # Main irregular board component.
    cv2.rectangle(canvas, (10, 20), (510, 165), (190, 195, 195), thickness=-1)
    for x in range(10, 510, 35):
        cv2.line(canvas, (x, 20), (x, 165), (105, 105, 105), thickness=2)
    for y in range(20, 165, 35):
        cv2.line(canvas, (10, y), (510, y), (105, 105, 105), thickness=2)
    cv2.rectangle(canvas, (70, 45), (360, 70), (20, 20, 20), thickness=-1)
    cv2.rectangle(canvas, (130, 185), (390, 290), (190, 195, 195), thickness=-1)
    for x in range(130, 390, 35):
        cv2.line(canvas, (x, 185), (x, 290), (105, 105, 105), thickness=2)
    cv2.rectangle(canvas, (215, 205), (245, 235), (30, 160, 60), thickness=-1)
    # Detached prose label in the lower-left empty corner.
    cv2.putText(canvas, "COURSE NAME", (8, 345), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (20, 20, 120), 3)
    cv2.putText(canvas, "Game Length", (8, 385), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (20, 20, 20), 2)

    masked = _mask_detached_map_background(
        Image.fromarray(canvas),
        {"_critical_graphics_role": "map_or_board"},
    )

    assert masked is not None
    assert masked.mode == "RGBA"
    alpha = np.asarray(masked)[:, :, 3]
    assert alpha[355, 35] == 0
    assert alpha[215, 230] == 255
    assert np.asarray(masked)[215, 230, :3].tolist() == canvas[215, 230].tolist()


def test_reference_panel_splitting_is_limited_to_unannotated_card_grids():
    assert _should_split_card_reference_panel(
        {
            "_critical_graphics_role": "card_reference",
            "_description": "Reference images of the nine programming card faces",
        }
    )
    assert not _should_split_card_reference_panel(
        {
            "_critical_graphics_role": "card_reference",
            "_description": "Annotated example upgrade card showing where the Cost and Effect appear",
        }
    )
    assert not _should_split_card_reference_panel(
        {
            "_critical_graphics_role": "map_or_board",
            "_description": "Reference images of map boards",
        }
    )


def test_split_card_reference_panel_boxes_emits_individual_card_faces(tmp_path):
    page_path = tmp_path / "card-reference.png"
    canvas = np.full((720, 640, 3), 238, dtype=np.uint8)
    positions = [(60, 80), (380, 80), (60, 380), (380, 380)]
    labels = ["MOVE 1", "TURN RIGHT", "POWER UP", "AGAIN"]
    for (x, y), label in zip(positions, labels):
        cv2.rectangle(canvas, (x, y), (240 + x, 250 + y), (215, 215, 215), thickness=-1)
        cv2.rectangle(canvas, (x + 15, y + 15), (x + 225, y + 70), (25, 30, 90), thickness=-1)
        cv2.rectangle(canvas, (x + 15, y + 85), (x + 225, y + 235), (30, 70, 170), thickness=-1)
        cv2.putText(canvas, label, (x + 28, y + 52), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
    cv2.putText(canvas, "Move your robot in the direction shown.", (248, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 2)
    cv2.putText(canvas, "Take one energy cube.", (248, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 2)
    cv2.imwrite(str(page_path), canvas)

    split = _split_card_reference_panel_boxes(
        str(page_path),
        [
            {
                "x0": 35,
                "y0": 45,
                "x1": 610,
                "y1": 675,
                "width": 575,
                "height": 630,
                "_critical_graphics_role": "card_reference",
                "_description": "Reference images of the programming card faces",
                "_nearby_text": "PROGRAMMING CARDS; MOVE 1; TURN RIGHT; POWER UP; AGAIN",
                "_critical_graphics_target_id": "p001-g01",
                "_critical_graphics_importance": "essential",
            }
        ],
        min_expected_count=3,
        saturation_threshold=35,
        min_component_area_ratio=0.01,
        max_component_area_ratio=0.2,
        padding_percent=0.01,
    )

    assert len(split) == 4
    assert {box["_critical_graphics_role"] for box in split} == {"card_face"}
    assert [box["_description"] for box in split] == [f"Card face titled {label}" for label in labels]
    assert [box["_critical_graphics_target_id"] for box in split] == [
        "p001-g01-card-01",
        "p001-g01-card-02",
        "p001-g01-card-03",
        "p001-g01-card-04",
    ]


def test_cropper_emits_transparent_png_for_map_crop_with_detached_edge_text(tmp_path):
    page_path = tmp_path / "page-001.png"
    canvas = np.full((260, 360, 3), 235, dtype=np.uint8)
    cv2.rectangle(canvas, (20, 20), (340, 130), (190, 195, 195), thickness=-1)
    for x in range(20, 340, 32):
        cv2.line(canvas, (x, 20), (x, 130), (105, 105, 105), thickness=2)
    cv2.rectangle(canvas, (145, 145), (255, 205), (190, 195, 195), thickness=-1)
    cv2.rectangle(canvas, (175, 160), (205, 190), (30, 160, 60), thickness=-1)
    cv2.putText(canvas, "COURSE", (12, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (20, 20, 120), 3)
    cv2.imwrite(str(page_path), canvas)
    ocr_manifest = tmp_path / "pages_html.jsonl"
    ocr_manifest.write_text(
        json.dumps({"page_number": 1, "image": str(page_path), "html": "<h1>Course</h1>"}) + "\n",
        encoding="utf-8",
    )
    critical_manifest = tmp_path / "critical_graphics_manifest.json"
    critical_manifest.write_text(
        json.dumps(
            {
                "schema_version": "critical_graphics_manifest_v1",
                "summary": {"essential_count": 1},
                "pages": [
                    {
                        "page_number": 1,
                        "targets": [
                            {
                                "target_id": "p001-g01",
                                "importance": "essential",
                                "role": "map_or_board",
                                "description": "Course map",
                                "reason": "Defines board layout.",
                                "bbox_pixels": {"x0": 0, "y0": 0, "x1": 360, "y1": 260, "width": 360, "height": 260},
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    manifest = crop_illustrations_guided(
        ocr_manifest=str(ocr_manifest),
        output_dir=str(tmp_path / "out"),
        output_format="jpeg",
        critical_graphics_manifest=str(critical_manifest),
        detection_mode="auto",
        padding_percent=0.0,
    )

    assert manifest[0]["filename"].endswith(".png")
    assert manifest[0]["has_transparency"] is True
    image = Image.open(tmp_path / "out" / "images" / manifest[0]["filename"]).convert("RGBA")
    alpha = np.asarray(image)[:, :, 3]
    assert alpha[230, 30] == 0
    assert alpha[170, 190] == 255
