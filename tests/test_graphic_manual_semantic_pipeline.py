from __future__ import annotations

import json
from pathlib import Path

import yaml

from modules.transform.plan_graphic_manual_figures_v1.main import build_plan
from modules.validate.validate_semantic_manual_html_v1.main import build_report, _semantic_fidelity_checks


RECIPE = Path("configs/recipes/recipe-graphics-heavy-imposed-pdf-html-mvp.yaml")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def test_graphic_manual_plan_classifies_generic_rulebook_roles() -> None:
    plan = build_plan(
        [
            {
                "page": 1,
                "page_number": 1,
                "printed_page_number": 1,
                "html": '<h1>Setup</h1><p>Place components.</p><figure><img alt="Setup diagram for components"></figure>',
            },
            {
                "page": 2,
                "page_number": 2,
                "printed_page_number": 2,
                "html": '<h1>Card Reference</h1><figure><img alt="Card cost and effect reference" data-count="2"></figure>',
            },
            {
                "page": 3,
                "page_number": 3,
                "printed_page_number": 3,
                "html": "<h1>Summary of a Round</h1><p>Resolve the main phases in order.</p>",
            },
        ],
        run_id="test",
    )

    assert plan["summary"]["preserve_as_figure_count"] == 3
    roles = {item["role"] for item in plan["plan_items"]}
    assert {"setup_diagram", "card_or_reference"} <= roles
    summary_page = next(page for page in plan["pages"] if page["page_number"] == 3)
    assert summary_page["page_roles"] == ["summary_reference"]


def test_semantic_manual_conformance_report_surfaces_figure_and_provenance_coverage(tmp_path: Path) -> None:
    logical_pages_path = tmp_path / "01_order" / "pages_logical_manifest.jsonl"
    logical_map_path = logical_pages_path.parent / "logical_page_map.json"
    pages_path = tmp_path / "pages_html.jsonl"
    plan_path = tmp_path / "plan.json"
    critical_path = tmp_path / "critical_graphics_manifest.json"
    crops_path = tmp_path / "crops.jsonl"
    chapters_path = tmp_path / "chapters.jsonl"
    html_dir = tmp_path / "output" / "html"
    html_dir.mkdir(parents=True)

    _write_jsonl(logical_pages_path, [{"page": 1, "page_number": 1, "image": "/tmp/page1.png"}])
    logical_map_path.write_text(
        json.dumps({"summary": {"complete": True, "issues_count": 0, "inferred_logical_page_count": 1}}),
        encoding="utf-8",
    )
    _write_jsonl(pages_path, [{"page": 1, "page_number": 1, "html": "<h1>Setup</h1><figure><img alt='Setup diagram'></figure>"}])
    plan_path.write_text(
        json.dumps(
            {
                "summary": {"preserve_as_figure_count": 1},
                "plan_items": [{"role": "setup_diagram", "source_page_number": 1}],
                "pages": [{"page_number": 1, "page_roles": ["summary_reference"]}],
            }
        ),
        encoding="utf-8",
    )
    critical_path.write_text(
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
                                "bbox_pixels": {"x0": 0, "y0": 0, "x1": 10, "y1": 10, "width": 10, "height": 10},
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    _write_jsonl(crops_path, [{"filename": "crop.png", "source_page": 1, "bbox": {"x0": 0, "y0": 0, "x1": 10, "y1": 10}}])
    html_file = html_dir / "chapter-001.html"
    html_file.write_text("<html><body><figure><img src='images/crop.png' alt='Setup diagram'></figure></body></html>", encoding="utf-8")
    (html_dir / "manifest.json").write_text("{}", encoding="utf-8")
    provenance_path = html_dir / "provenance" / "blocks.jsonl"
    _write_jsonl(provenance_path, [{"block_id": "blk-1"}])
    _write_jsonl(chapters_path, [{"file": str(html_file), "title": "Setup"}])

    report = build_report(
        pages_path=pages_path,
        logical_pages_path=logical_pages_path,
        figure_plan_path=plan_path,
        critical_graphics_manifest_path=critical_path,
        crops_path=crops_path,
        chapters_path=chapters_path,
        run_id="test",
        min_figure_crop_ratio=0.75,
        min_critical_target_crop_coverage=0.5,
    )

    assert report["overall_status"] == "pass"
    assert report["summary"]["crop_count"] == 1
    assert report["summary"]["html_figure_count"] == 1
    assert report["review_samples"]["summary"] == 1


def test_semantic_manual_conformance_fails_when_essential_source_pixel_crop_is_unused(tmp_path: Path) -> None:
    logical_pages_path = tmp_path / "01_order" / "pages_logical_manifest.jsonl"
    logical_map_path = logical_pages_path.parent / "logical_page_map.json"
    pages_path = tmp_path / "pages_html.jsonl"
    plan_path = tmp_path / "plan.json"
    critical_path = tmp_path / "critical_graphics_manifest.json"
    crops_path = tmp_path / "crops.jsonl"
    chapters_path = tmp_path / "chapters.jsonl"
    html_dir = tmp_path / "output" / "html"
    html_dir.mkdir(parents=True)

    _write_jsonl(logical_pages_path, [{"page": 1, "page_number": 1, "image": "/tmp/page1.png"}])
    logical_map_path.write_text(
        json.dumps({"summary": {"complete": True, "issues_count": 0, "inferred_logical_page_count": 1}}),
        encoding="utf-8",
    )
    _write_jsonl(pages_path, [{"page": 1, "page_number": 1, "html": "<h1>Board Elements</h1>"}])
    plan_path.write_text(
        json.dumps(
            {
                "summary": {"preserve_as_figure_count": 1},
                "plan_items": [{"role": "board_element", "source_page_number": 1}],
                "pages": [{"page_number": 1, "page_roles": ["board_element"]}],
            }
        ),
        encoding="utf-8",
    )
    critical_path.write_text(
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
                                "role": "board_element",
                                "description": "Blue conveyor belt icon",
                                "bbox_pixels": {"x0": 0, "y0": 0, "x1": 10, "y1": 10, "width": 10, "height": 10},
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    _write_jsonl(
        crops_path,
        [
            {
                "filename": "belt.png",
                "source_page": 1,
                "bbox": {"x0": 0, "y0": 0, "x1": 10, "y1": 10},
                "critical_graphics_importance": "essential",
                "critical_graphics_role": "board_element",
                "image_description": "Blue conveyor belt icon",
            }
        ],
    )
    html_file = html_dir / "chapter-001.html"
    html_file.write_text("<html><body><h1>Board Elements</h1></body></html>", encoding="utf-8")
    (html_dir / "manifest.json").write_text("{}", encoding="utf-8")
    provenance_path = html_dir / "provenance" / "blocks.jsonl"
    _write_jsonl(provenance_path, [{"block_id": "blk-1"}])
    _write_jsonl(chapters_path, [{"file": str(html_file), "title": "Board Elements"}])

    report = build_report(
        pages_path=pages_path,
        logical_pages_path=logical_pages_path,
        figure_plan_path=plan_path,
        critical_graphics_manifest_path=critical_path,
        crops_path=crops_path,
        chapters_path=chapters_path,
        run_id="test",
        min_figure_crop_ratio=0.75,
        min_critical_target_crop_coverage=0.5,
    )

    usage_check = next(check for check in report["checks"] if check["id"] == "essential_source_pixel_crops_referenced_in_html")
    assert report["overall_status"] == "fail"
    assert usage_check["status"] == "fail"
    assert usage_check["detail"]["missing"][0]["filename"] == "belt.png"


def test_semantic_fidelity_flags_lower_item_heading_chapter_boundaries(tmp_path: Path) -> None:
    html_dir = tmp_path / "html"
    html_dir.mkdir()
    parent_file = html_dir / "chapter-001.html"
    item_file = html_dir / "chapter-002.html"
    parent_file.write_text("<html><body><h1>DIFFICULT COURSES</h1></body></html>", encoding="utf-8")
    item_file.write_text("<html><body><h1>EXTRA CRISPY</h1></body></html>", encoding="utf-8")

    checks = _semantic_fidelity_checks(
        pages=[
            {
                "page_number": 1,
                "html": "<h1>DIFFICULT COURSES</h1><p>First category page.</p>",
            },
            {
                "page_number": 2,
                "html": (
                    "<h2>EXTRA CRISPY</h2>"
                    "<p>Game Length: Short Boards: Start A Special Rules: Continue the category.</p>"
                ),
            },
        ],
        chapters=[
            {"title": "DIFFICULT COURSES", "source_pages": [1], "file": str(parent_file)},
            {"title": "EXTRA CRISPY", "source_pages": [2], "file": str(item_file)},
        ],
        html_files=[parent_file, item_file],
    )

    item_check = next(check for check in checks if check["id"] == "lower_item_headings_do_not_start_chapters")
    assert item_check["status"] == "fail"
    assert item_check["detail"]["issues"][0]["reason"] == "lower_level_item_heading_started_chapter"


def test_semantic_fidelity_flags_catalog_subsection_sibling_chapters(tmp_path: Path) -> None:
    html_dir = tmp_path / "html"
    html_dir.mkdir()
    parent_file = html_dir / "chapter-001.html"
    child_file = html_dir / "chapter-002.html"
    parent_file.write_text("<html><body><h1>ROUTE CATALOG</h1></body></html>", encoding="utf-8")
    child_file.write_text("<html><body><h1>EASY ROUTES</h1></body></html>", encoding="utf-8")

    checks = _semantic_fidelity_checks(
        pages=[
            {
                "page_number": 1,
                "html": "<h1>ROUTE CATALOG</h1><p>On the following pages, find a list of routes.</p>",
            },
            {
                "page_number": 2,
                "html": "<h1>EASY ROUTES</h1><h2>River Walk</h2>",
            },
        ],
        chapters=[
            {"title": "ROUTE CATALOG", "source_pages": [1], "file": str(parent_file)},
            {"title": "EASY ROUTES", "source_pages": [2], "file": str(child_file)},
        ],
        html_files=[parent_file, child_file],
    )

    catalog_check = next(check for check in checks if check["id"] == "catalog_subsections_stay_with_parent")
    assert catalog_check["status"] == "fail"
    assert catalog_check["detail"]["issues"][0]["reason"] == "catalog_subsection_promoted_to_sibling_chapter"


def test_semantic_fidelity_allows_procedural_subheadings_inside_parent_chapter(tmp_path: Path) -> None:
    html_dir = tmp_path / "html"
    html_dir.mkdir()
    chapter_file = html_dir / "chapter-001.html"
    chapter_file.write_text(
        "<html><body><h1>HOW TO PLAY</h1><h2>PLAYING A ROUND</h2></body></html>",
        encoding="utf-8",
    )

    checks = _semantic_fidelity_checks(
        pages=[
            {
                "page_number": 1,
                "html": (
                    "<h1>HOW TO PLAY</h1>"
                    "<p>A detailed description of each phase starts on the following pages.</p>"
                ),
            },
            {
                "page_number": 2,
                "html": '<h1 data-normalized-from="running-head">PLAYING A ROUND</h1><p>Round details.</p>',
            },
        ],
        chapters=[
            {"title": "HOW TO PLAY", "source_pages": [1, 2], "file": str(chapter_file)},
        ],
        html_files=[chapter_file],
    )

    boundary_check = next(check for check in checks if check["id"] == "promoted_running_heads_become_boundaries")
    assert boundary_check["status"] == "pass"


def test_semantic_fidelity_flags_ungrouped_catalog_entry_figures(tmp_path: Path) -> None:
    html_dir = tmp_path / "html"
    html_dir.mkdir()
    chapter_file = html_dir / "chapter-001.html"
    chapter_file.write_text(
        (
            "<html><body><h1>ROUTE CATALOG</h1>"
            '<figure data-critical-graphics-role="map_or_board"><img data-crop-filename="route-a.png" src="images/route-a.png"></figure>'
            "<h3>RIVER WALK</h3>"
            "<p><strong>Distance:</strong> Short<br><strong>Difficulty:</strong> Easy</p>"
            "</body></html>"
        ),
        encoding="utf-8",
    )

    checks = _semantic_fidelity_checks(
        pages=[
            {
                "page_number": 1,
                "html": "<h1>ROUTE CATALOG</h1><p>On the following pages, find a list of routes.</p>",
            }
        ],
        chapters=[{"title": "ROUTE CATALOG", "source_pages": [1], "file": str(chapter_file)}],
        html_files=[chapter_file],
    )

    grouping_check = next(check for check in checks if check["id"] == "catalog_entries_group_figures_labels_and_metadata")
    assert grouping_check["status"] == "fail"
    assert grouping_check["detail"]["issues"][0]["reason"] == "catalog_entry_figure_not_grouped_with_label_and_metadata"


def test_semantic_fidelity_flags_catalog_figures_embedded_in_definition_lists(tmp_path: Path) -> None:
    html_dir = tmp_path / "html"
    html_dir.mkdir()
    chapter_file = html_dir / "chapter-001.html"
    chapter_file.write_text(
        (
            "<html><body><h1>ROUTE CATALOG</h1>"
            "<dl>"
            "<dt>RIVER WALK</dt>"
            "<dd>"
            '<figure data-critical-graphics-role="map_or_board"><img data-crop-filename="route-a.png" src="images/route-a.png"></figure>'
            "<strong>Distance:</strong> Short<br><strong>Difficulty:</strong> Easy"
            "</dd>"
            "</dl>"
            "</body></html>"
        ),
        encoding="utf-8",
    )

    checks = _semantic_fidelity_checks(
        pages=[
            {
                "page_number": 1,
                "html": "<h1>ROUTE CATALOG</h1><p>On the following pages, find a list of routes.</p>",
            }
        ],
        chapters=[{"title": "ROUTE CATALOG", "source_pages": [1], "file": str(chapter_file)}],
        html_files=[chapter_file],
    )

    grouping_check = next(check for check in checks if check["id"] == "catalog_entries_group_figures_labels_and_metadata")
    assert grouping_check["status"] == "fail"
    assert grouping_check["detail"]["issues"][0]["reason"] == "catalog_entry_figure_embedded_in_definition_list"


def test_graphics_heavy_imposed_pdf_recipe_wiring() -> None:
    data = yaml.safe_load(RECIPE.read_text(encoding="utf-8"))
    modules = [stage["module"] for stage in data["stages"]]

    assert modules == [
        "extract_pdf_images_fast_v1",
        "split_pages_from_manifest_v1",
        "infer_logical_page_order_v1",
        "ocr_ai_gpt51_v1",
        "plan_graphic_manual_figures_v1",
        "plan_critical_graphics_vlm_v1",
        "crop_illustrations_guided_v1",
        "extract_page_numbers_html_v1",
        "normalize_graphic_manual_html_v1",
        "portionize_headings_html_v1",
        "build_chapter_html_v1",
        "validate_semantic_manual_html_v1",
    ]
    order_stage = data["stages"][2]
    assert order_stage["params"]["fail_on_uncertain"] is True
    critical_stage = data["stages"][5]
    assert critical_stage["inputs"]["pages"] == "infer_logical_pages"
    assert critical_stage["inputs"]["page_html"] == "ocr_ai"
    crop_stage = data["stages"][6]
    assert crop_stage["inputs"]["critical_graphics_manifest"] == "plan_critical_graphics"
    assert crop_stage["params"]["dense_split_when_missing"] is True
    assert crop_stage["params"]["dense_split_min_expected_count"] == 3
    normalize_stage = data["stages"][8]
    assert normalize_stage["params"]["max_promoted_running_head_occurrences"] == 2
    portion_stage = data["stages"][9]
    assert portion_stage["params"]["suppress_lower_heading_item_boundaries"] is True
    assert portion_stage["params"]["merge_catalog_subsections"] is True
    assert portion_stage["params"]["merge_procedural_subsections"] is True
    build_stage = data["stages"][10]
    assert "suppress_navigation" not in build_stage["params"]
    assert build_stage["params"]["normalize_reference_entries"] is True
    assert build_stage["params"]["normalize_catalog_entries"] is True
    assert "graphics-heavy manual" in data["stages"][3]["params"]["ocr_hints"]
