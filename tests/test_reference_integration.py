"""Final-emitter and real driver controls for optional reference resolution."""
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from bs4 import BeautifulSoup

from doc_web.runtime_contract import build_runtime_contract
from driver import apply_reference_resolution
from modules.common.office_native_bundle import write_bundle
from schemas import NavigationResolutionReport, RunConfig

ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args):
    return subprocess.run([sys.executable, *map(str, args)], cwd=ROOT, capture_output=True, text=True)


@pytest.fixture
def reference_recipe(tmp_path):
    pages = [
        {"page": 1, "page_number": 1, "original_page_number": 10,
         "printed_page_number": 12, "printed_page_number_text": "12",
         "html": '<h1 id="sec3">Section 3</h1><p>See page <em>12</em>, section 3, page iv, page 13 and https://example.org.</p><p><a href="#sec3">Section 3</a></p>'},
        {"page": 2, "page_number": 2, "original_page_number": 11,
         "printed_page_number_text": "iv", "html": '<h1>Appendix</h1><p>Observed Roman page.</p>'},
        {"page": 3, "page_number": 3, "original_page_number": 12,
         "printed_page_number": 13, "printed_page_number_text": "13", "printed_page_number_inferred": True,
         "html": '<h1>Details</h1><p>Inferred number cannot authorize page 13.</p>'},
    ]
    pages_path = tmp_path / "pages.jsonl"
    pages_path.write_text(''.join(json.dumps(row) + '\n' for row in pages))
    portions_path = tmp_path / "portions.jsonl"
    portions_path.write_text(json.dumps({"title": "Section 3", "page_start": 12, "page_end": 12}) + '\n')
    recipe = {"stages": [
        {"id": "pages", "stage": "extract", "module": "load_artifact_v1", "out": "pages.jsonl", "params": {"path": str(pages_path)}},
        {"id": "portions", "stage": "extract", "module": "load_artifact_v1", "out": "portions.jsonl", "params": {"path": str(portions_path)}},
        {"id": "html", "stage": "build", "module": "build_chapter_html_v1", "needs": ["pages", "portions"], "inputs": {"pages": "pages", "portions": "portions"}, "out": "chapters.jsonl", "params": {"book_title": "Reference controls"}},
    ]}
    path = tmp_path / "recipe.yaml"
    path.write_text(yaml.safe_dump(recipe))
    return path, recipe


@pytest.mark.parametrize("enable", ["off", "cli", "recipe", "config"])
def test_driver_final_build_flags_and_report(reference_recipe, tmp_path, enable):
    recipe_path, recipe = reference_recipe
    if enable == "recipe":
        recipe["stages"][-1]["params"]["resolve_references"] = True
        recipe_path.write_text(yaml.safe_dump(recipe))
    output_root = tmp_path / "runs"
    args = ["driver.py", "--recipe", recipe_path, "--run-id", f"references-{enable}", "--output-dir", output_root]
    if enable == "cli":
        args += ["--resolve-references"]
    if enable == "config":
        config = tmp_path / "config.yaml"
        config.write_text(yaml.safe_dump({"recipe": str(recipe_path), "run_id": "references-config", "output_dir": str(output_root), "options": {"resolve_references": True}}))
        args = ["driver.py", "--config", config]
    proc = run_cli(*args)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    html_dir = output_root / f"references-{enable}" / "output" / "html"
    report = json.loads((html_dir / "navigation_resolution_report.json").read_text())
    NavigationResolutionReport.model_validate(report)
    assert report["policy"]["resolve_references"] == (enable != "off")
    assert report["api_calls"] == report["cost_usd"] == 0
    assert report["final_validation"]["status"] == "passed"
    assert report["final_validation"]["issues"] == []
    references = report["references"]
    # A changed source heading ID is repaired even with plain discovery disabled.
    existing = [row for row in references if row.get("original_href") == "#sec3"]
    assert len(existing) == 1 and existing[0]["resolution_status"] == "resolved"
    assert existing[0]["target"]["id"].startswith("blk-")
    discovered = [row for row in references if row.get("kind")]
    if enable == "off":
        assert discovered == []
    else:
        page12 = next(row for row in discovered if row["original_text"] == "page 12")
        roman = next(row for row in discovered if row["original_text"] == "page iv")
        inferred = next(row for row in discovered if row["original_text"] == "page 13")
        assert page12["target"]["evidence"]["source_page_number"] == 1
        assert page12["target"]["evidence"]["original_page_number"] == 10
        assert roman["resolution_status"] == "resolved"
        assert inferred["resolution_status"] == "missing"
        assert inferred["reason"] == "inferred_printed_label"
    soup = BeautifulSoup(''.join(path.read_text() for path in html_dir.glob("*.html")), "html.parser")
    assert soup.find("em").get_text() == "12"
    assert not soup.select("a a")
    validation = run_cli("validate_artifact.py", "--schema", "manual_navigation_resolution_v1", "--file", html_dir / "navigation_resolution_report.json")
    assert validation.returncode == 0, validation.stdout + validation.stderr
    # The persisted execution plan records the effective option for resumption.
    plan_paths = list((output_root / f"references-{enable}" / "snapshots").glob("*plan*"))
    assert plan_paths
    snapshot = json.loads(plan_paths[0].read_text())
    assert snapshot["nodes"]["html"]["params"]["resolve_references"] == (enable != "off")


def test_unsupported_recipe_and_driver_flag_fail(tmp_path):
    recipe = {"stages": [{"stage": "extract", "module": "load_artifact_v1", "params": {"path": "absent.jsonl"}}]}
    path = tmp_path / "unsupported.yaml"
    path.write_text(yaml.safe_dump(recipe))
    result = run_cli("driver.py", "--recipe", path, "--dry-run", "--resolve-references")
    assert result.returncode != 0
    assert "supported final HTML emitter" in result.stdout + result.stderr
    recipe["stages"][0]["params"]["resolve_references"] = True
    with pytest.raises(SystemExit, match="unsupported"):
        apply_reference_resolution(recipe)


def test_cli_option_overrides_false_stage_params():
    recipe = {"stages": [{"id": "html", "stage": "build", "module": "build_chapter_html_v1"}], "stage_params": {"html": {"resolve_references": False}}}
    apply_reference_resolution(recipe, True)
    assert recipe["stage_params"]["html"]["resolve_references"] is True
    assert RunConfig(recipe="x", options={"resolve_references": True}).options.resolve_references


def test_office_shared_final_writer_discovers_only_when_enabled(tmp_path):
    elements = [{"id": "source-heading", "type": "Title", "text": "Section 3"}, {"id": "source-text", "type": "NarrativeText", "text": "See section 3 and page 1."}]
    for enabled in (False, True):
        run_dir = tmp_path / str(enabled)
        out = run_dir / "01_docx_elements_to_bundle_v1" / "report.json"
        result = write_bundle(entry_specs=[{"entry_id": "chapter-001", "title": "Section 3", "kind": "chapter", "elements": elements}], source_elements=elements, out_path=out, module_id="docx_elements_to_bundle_v1", run_id="office-references", document_title="Office reference", resolve_references=enabled)
        report = json.loads(Path(result["navigation_resolution_report_path"]).read_text())
        NavigationResolutionReport.model_validate(report)
        assert report["policy"]["resolve_references"] is enabled
        if enabled:
            section = next(row for row in report["references"] if row["original_text"] == "section 3")
            assert section["resolution_status"] == "resolved"
            page = next(row for row in report["references"] if row["original_text"] == "page 1")
            assert page["resolution_status"] == "missing"
        else:
            assert report["references"] == []


def test_contract_advertises_final_reference_report():
    contract = build_runtime_contract()
    assert contract["reference_resolution"]["discovery_default"] is False
    assert contract["reference_resolution"]["final_build_only"] is True
    assert contract["bundle_layout"]["navigation_resolution_path"] == "navigation_resolution_report.json"


def test_duplicate_printed_labels_do_not_drop_source_pages(tmp_path):
    output_root = tmp_path / "runs"
    proc = run_cli("driver.py", "--recipe", "configs/recipes/recipe-reference-resolution-smoke.yaml", "--run-id", "duplicate-pages", "--output-dir", output_root, "--resolve-references")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    html_dir = output_root / "duplicate-pages" / "output" / "html"
    manifest = json.loads((html_dir / "manifest.json").read_text())
    assert [page for entry in manifest["entries"] for page in entry["source_pages"]] == [1, 2, 3, 4, 5]
    text = ' '.join(BeautifulSoup(path.read_text(), "html.parser").get_text() for path in html_dir.glob("*.html"))
    assert "First repeated printed label." in text
    assert "Second repeated printed label." in text
    report = json.loads((html_dir / "navigation_resolution_report.json").read_text())
    duplicate = next(row for row in report["references"] if row["original_text"] == "page 22")
    assert duplicate["resolution_status"] == "ambiguous"
    assert duplicate["target"] is None


def test_marker_final_writer_uses_stamped_ids_and_raw_print_labels(tmp_path):
    from modules.common.marker_page_html import write_marker_outputs
    body = '<html><body><h1 id="blk-page-001-0001">Section 3</h1><p id="blk-page-001-0002">See section 3, page iv and page 9.</p><p><a href="#old-section">Section 3</a></p></body></html>'
    entry = {"entry_id": "page-001", "path": "page-001.html", "title": "Section 3", "source_pages": [1]}
    provenance = [{"block_id": "blk-page-001-0001", "entry_id": "page-001", "source_page_number": 1}, {"block_id": "blk-page-001-0002", "entry_id": "page-001", "source_page_number": 1}]
    bundle = {"manifest": {"entries": [entry]}, "provenance_rows": provenance, "page_files": {"page-001": body}, "document_title": "Marker references"}
    pages = [{"page": 1, "page_number": 1, "original_page_number": 42, "printed_page_number_text": "iv", "html": '<h1 id="old-section">Section 3</h1><p>See section 3, page iv and page 9.</p><p><a href="#old-section">Section 3</a></p>'}]
    trace = [{"entry_id": "page-001", "navigation_id_aliases": {"old-section": ["blk-page-001-0001"]}}]
    result = write_marker_outputs(tmp_path, artifact_name="pages.jsonl", page_rows=pages, block_rows=[], bundle=bundle, runtime_trace=trace, summary={}, normalization_report={}, resolve_references=True)
    report = json.loads(Path(result["navigation_resolution_report"]).read_text())
    NavigationResolutionReport.model_validate(report)
    assert report["final_validation"]["status"] == "passed"
    existing = next(row for row in report["references"] if row.get("original_href") == "#old-section")
    assert existing["target"]["id"] == "blk-page-001-0001"
    roman = next(row for row in report["references"] if row["original_text"] == "page iv")
    assert roman["target"]["evidence"]["original_page_number"] == 42
    assert next(row for row in report["references"] if row["original_text"] == "page 9")["resolution_status"] == "missing"


def test_office_preserves_changed_table_id_and_checks_generated_index(tmp_path):
    elements = [{"id": "source-table", "type": "Table", "text": "See table.", "metadata": {"text_as_html": '<table id="old-table"><tr><td><a href="#old-table">See table.</a></td></tr></table>'}}]
    result = write_bundle(entry_specs=[{"entry_id": "chapter-001", "title": "Tables", "kind": "chapter", "elements": elements}], source_elements=elements, out_path=tmp_path / "run" / "01_docx" / "report.json", module_id="docx_elements_to_bundle_v1", run_id="office-table", document_title="Tables")
    report = json.loads(Path(result["navigation_resolution_report_path"]).read_text())
    assert report["references"][0]["target"]["id"] == "blk-chapter-001-0001"
    assert report["final_validation"]["status"] == "passed"
    assert report["final_validation"]["issues"] == []


@pytest.mark.parametrize("format_name", ["docx", "xlsx", "pptx", "epub", "email", "mbox"])
def test_every_native_emitter_forwards_discovery_flag(tmp_path, monkeypatch, format_name):
    import importlib
    module = importlib.import_module(f"modules.transform.{format_name}_elements_to_bundle_v1.main")
    captured = {}

    def capture_bundle(**kwargs):
        captured.update(kwargs)
        return {}

    monkeypatch.setattr(module, "write_bundle", capture_bundle)
    elements = [{"id": "heading", "type": "Title", "text": "Section 3", "metadata": {"page_number": 1, "sheet_name": "Sheet1", "email_message_id": "message1", "archive_message_index": 1, "epub_spine_index": 0}}]
    module._build_bundle(elements, out_path=tmp_path / "01_bundle" / "report.json", module_id=f"{format_name}_elements_to_bundle_v1", run_id="forwarding", book_title="Fixture", book_author="", resolve_references=True)
    assert captured["resolve_references"] is True


@pytest.mark.parametrize("enabled", [False, True])
def test_driver_chapter_preserves_source_order_when_print_labels_reset(reference_recipe, tmp_path, enabled):
    from schemas import DocWebBundleManifest

    recipe_path, recipe = reference_recipe
    pages_path = Path(recipe["stages"][0]["params"]["path"])
    pages = [
        {"page": 1, "page_number": 1, "printed_page_number": 12, "printed_page_number_text": "12", "printed_page_number_inferred": False,
         "html": '<p>First logical page. See page 1.</p>'},
        {"page": 2, "page_number": 2, "printed_page_number": 1, "printed_page_number_text": "1", "printed_page_number_inferred": False,
         "html": '<p>Second logical page. See page 12.</p>'},
    ]
    pages_path.write_text(''.join(json.dumps(row) + '\n' for row in pages))
    portions_path = Path(recipe["stages"][1]["params"]["path"])
    portions_path.write_text(json.dumps({"title": "Logical source order", "page_start": 1, "page_end": 2, "source_pages": [1, 2], "notes": "heading-derived-source-pages"}) + '\n')
    recipe["stages"][-1]["params"]["resolve_references"] = enabled
    recipe_path.write_text(yaml.safe_dump(recipe))
    output_root = tmp_path / "runs"
    result = run_cli("driver.py", "--recipe", recipe_path, "--run-id", "source-order", "--output-dir", output_root)
    assert result.returncode == 0, result.stdout + result.stderr
    html_dir = output_root / "source-order" / "output" / "html"
    manifest = DocWebBundleManifest.model_validate_json((html_dir / "manifest.json").read_text())
    assert len(manifest.entries) == 1
    assert manifest.entries[0].source_pages == [1, 2]
    assert manifest.entries[0].printed_pages == [12, 1]
    assert (manifest.entries[0].printed_page_start, manifest.entries[0].printed_page_end) == (1, 12)
    soup = BeautifulSoup((html_dir / manifest.entries[0].path).read_text(), "html.parser")
    text = soup.find("article").get_text()
    assert text.index("First logical page.") < text.index("Second logical page.")
    provenance = [json.loads(line) for line in (html_dir / "provenance" / "blocks.jsonl").read_text().splitlines()]
    assert [row["source_page_number"] for row in provenance] == [1, 2]
    assert [row["source_printed_page_label"] for row in provenance] == ["12", "1"]
    if enabled:
        report = json.loads((html_dir / "navigation_resolution_report.json").read_text())
        first = next(row for row in report["references"] if row["original_text"] == "page 1")
        second = next(row for row in report["references"] if row["original_text"] == "page 12")
        assert first["target"]["evidence"]["source_page_number"] == 2
        assert second["target"]["evidence"]["source_page_number"] == 1


def test_reviewed_crop_recipe_plan_accepts_existing_input_params():
    from driver import build_plan, load_recipe, load_registry

    recipe = load_recipe(str(ROOT / "configs/recipes/story-241-reviewed-crop-offline.yaml"))
    plan = build_plan(recipe, load_registry(str(ROOT / "modules"))["modules"])
    params = plan["nodes"]["build_reviewed"]["params"]
    assert params["pages"] == "tests/fixtures/crop_review_offline/approved/pages.jsonl"
    assert params["portions"] == "tests/fixtures/crop_review_offline/approved/portions.jsonl"
    assert params["resolve_references"] is False


@pytest.mark.parametrize("module_path", ["build/build_chapter_html_v1", "extract/extract_pdf_marker_lite_html_v1"])
def test_reference_emitter_schema_accepts_actual_parser_flags(module_path):
    import ast
    from driver import _validate_params

    module_dir = ROOT / "modules" / module_path
    metadata = yaml.safe_load((module_dir / "module.yaml").read_text())
    parser_flags = {}
    for node in ast.walk(ast.parse((module_dir / "main.py").read_text())):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute) or node.func.attr != "add_argument":
            continue
        keywords = {arg.arg: arg.value for arg in node.keywords}
        action = keywords.get("action")
        is_boolean = isinstance(action, ast.Constant) and action.value in {"store_true", "store_false"}
        has_negative_form = isinstance(action, ast.Attribute) and action.attr == "BooleanOptionalAction"
        for flag in node.args:
            if not isinstance(flag, ast.Constant) or not isinstance(flag.value, str) or not flag.value.startswith("--"):
                continue
            key = flag.value[2:].replace("-", "_")
            parser_flags[key] = True if is_boolean or has_negative_form else "fixture-value"
            if has_negative_form:
                parser_flags[f"no_{key}"] = True
    _validate_params(parser_flags, metadata["param_schema"], "parser-surface", metadata["module_id"])
    with pytest.raises(SystemExit, match="Unknown param"):
        _validate_params({"not_a_real_parser_flag": True}, metadata["param_schema"], "parser-surface", metadata["module_id"])


def test_tracked_reference_emitter_recipe_params_validate():
    from driver import _validate_params, load_registry

    registry = load_registry(str(ROOT / "modules"))["modules"]
    tracked = subprocess.check_output(["git", "ls-files", "configs/recipes"], cwd=ROOT, text=True).splitlines()
    checked = set()
    for rel in tracked:
        if not rel.endswith((".yaml", ".yml")):
            continue
        recipe = yaml.safe_load((ROOT / rel).read_text()) or {}
        for stage in recipe.get("stages") or []:
            module_id = stage.get("module")
            if module_id not in {"build_chapter_html_v1", "extract_pdf_marker_lite_html_v1"}:
                continue
            stage_id = stage.get("id") or stage.get("stage")
            params = {**(stage.get("params") or {}), **(recipe.get("stage_params") or {}).get(stage_id, {})}
            _validate_params(params, registry[module_id]["param_schema"], stage_id, module_id)
            checked.add(module_id)
    assert checked == {"build_chapter_html_v1", "extract_pdf_marker_lite_html_v1"}
