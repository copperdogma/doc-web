"""Publication controls for independently reviewed literal table text."""
import hashlib
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest
from PIL import Image

from doc_web.literal_tables import canonical_table_digest, compare_tables
from doc_web.literal_fidelity import SourcePageReview
from modules.common.table_source_review import POLICY
from modules.common.literal_fidelity_bundle import (
    finalize_literal_fidelity_bundle,
    validate_literal_fidelity_inputs,
)
from modules.build.build_chapter_html_v1.main import _tag_entry_body
from schemas import DocWebBundleManifest, DocWebProvenanceBlock, PageHtml, LiteralFidelityBundleQualification


HTML = "<table><tr><td>Literal r2l3</td><td>1+</td></tr></table>"


def digest(data):
    return hashlib.sha256(data).hexdigest()


@pytest.fixture
def evidence(tmp_path):
    image = tmp_path / "page.png"
    Image.new("RGB", (100, 80), "white").save(image)
    report_path = tmp_path / "review.json"
    report = {
        "schema_version": "literal_fidelity_report_v1", "run_id": "literal-test",
        "logical_page_number": 1, "original_page_number": 19, "source_pdf": None,
        "image_sha256": digest(image.read_bytes()), "image_dimensions": [100, 80],
        "initial_raw_html_sha256": digest(HTML.encode()),
        "reviewed_table_sequence_sha256": canonical_table_digest(HTML),
        "status": "verified", "table_count": 1, "unresolved_count": 0,
        "tables": [{"table": 0, "bbox": [10, 10, 90, 70], "initial_html": HTML,
                    "review": {"bbox": [10, 10, 90, 70], "html": HTML, "uncertain_cells": []},
                    "comparison": compare_tables(HTML, HTML),
                    "decision": "initial_agrees_B", "reason": "certain complete exact agreement"}],
        "errors": [], "requests": [],
    }
    row = {"page": 19, "page_number": 1, "original_page_number": 19,
           "printed_page_number": 19, "image": str(image), "html": HTML, "raw_html": HTML}
    receipt = {
        "schema_version": "literal_fidelity_receipt_v1", "status": "verified", "run_id": "literal-test",
        "logical_page_number": 1, "original_page_number": 19, "image_sha256": report["image_sha256"],
        "reviewed_table_sequence_sha256": report["reviewed_table_sequence_sha256"],
        "report_path": str(report_path), "report_sha256": "0" * 64,
        "table_count": 1, "unresolved_count": 0,
    }
    row["literal_fidelity"] = receipt

    def reseal():
        report_path.write_text(json.dumps(report), encoding="utf-8")
        receipt["report_sha256"] = digest(report_path.read_bytes())

    report["requests"] = [{"requested_model": "gpt-6-astra", "served_model": "gpt-6-astra",
                           "status": "completed", "image_detail": "original", "reasoning": {"effort": "medium"},
                           "submitted_image_sha256": report["image_sha256"], "prompt_sha256": digest(POLICY.encode()),
                           "response_schema_sha256": digest(json.dumps(SourcePageReview.model_json_schema(), sort_keys=True).encode()),
                           "raw_response": json.dumps({"source_table_count": 1, "tables": [report["tables"][0]["review"]]})}]
    reseal()
    return row, report, reseal


def qualify(row):
    return validate_literal_fidelity_inputs([row], run_id="literal-test", required=True)


def test_receipt_survives_stamping_and_physical_page_survives_provenance(evidence):
    row, _, _ = evidence
    stamped = PageHtml.model_validate(row).model_dump(exclude_none=True)
    assert stamped["literal_fidelity"]["original_page_number"] == 19
    assert qualify(stamped)
    entry = {"filename": "chapter-001.html", "body_html": HTML, "prepared_pages": [stamped],
             "source_pages": [1], "source_printed_pages": [19]}
    _, blocks = _tag_entry_body(entry, run_id="literal-test", created_at="test")
    block = DocWebProvenanceBlock.model_validate(blocks[0])
    assert block.source_page_number == 1
    assert block.source_original_page_number == 19
    assert block.source_printed_page_number == 19


@pytest.mark.parametrize("mutation", ["image", "report", "raw", "html", "run", "physical", "missing"])
def test_rejects_stale_or_missing_evidence(evidence, mutation):
    row, _, _ = evidence
    if mutation == "image":
        Image.new("RGB", (100, 80), "black").save(row["image"])
    elif mutation == "report":
        with open(row["literal_fidelity"]["report_path"], "a") as stream:
            stream.write(" ")
    elif mutation in {"raw", "html"}:
        key = "raw_html" if mutation == "raw" else "html"
        row[key] = HTML.replace("r2l3", "r213")
    elif mutation == "run":
        row["literal_fidelity"]["run_id"] = "stale"
    elif mutation == "physical":
        row["original_page_number"] = 1
    else:
        row.pop("literal_fidelity")
    with pytest.raises(ValueError):
        qualify(row)


@pytest.mark.parametrize("mutation", ["uncertain", "different", "missing_table", "error", "decision", "bbox"])
def test_report_status_alone_cannot_qualify(evidence, mutation):
    row, report, reseal = evidence
    table = report["tables"][0]
    if mutation == "uncertain":
        table["review"]["uncertain_cells"] = [{"row": 0, "cell": 0, "reason": "glyph", "alternatives": ["l", "1"]}]
    elif mutation == "different":
        table["review"]["html"] = HTML.replace("r2l3", "r213")
    elif mutation == "missing_table":
        report["tables"] = []
    elif mutation == "error":
        report["errors"] = ["independent source found omitted table"]
    elif mutation == "decision":
        table["decision"] = "unresolved"
    else:
        table["bbox"] = [0, 0, 101, 80]
    reseal()
    with pytest.raises(ValueError):
        qualify(row)


def test_declared_comparison_is_recomputed(evidence):
    row, report, reseal = evidence
    report["tables"][0]["comparison"]["pass"] = False
    reseal()
    with pytest.raises(ValueError, match="recomputed"):
        qualify(row)


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "served", "status", "prompt", "schema", "image", "raw"])
def test_independent_source_request_is_bound_and_complete(evidence, mutation):
    row, report, reseal = evidence
    request = report["requests"][0]
    if mutation == "missing":
        report["requests"] = []
    elif mutation == "duplicate":
        report["requests"].append(deepcopy(request))
    elif mutation == "served":
        request["served_model"] = "other-model"
    elif mutation == "status":
        request["status"] = "incomplete"
    elif mutation in {"prompt", "schema", "image"}:
        key = {"prompt": "prompt_sha256", "schema": "response_schema_sha256", "image": "submitted_image_sha256"}[mutation]
        request[key] = "0" * 64
    else:
        request["raw_response"] = json.dumps({"source_table_count": 0, "tables": []})
    reseal()
    with pytest.raises(ValueError):
        qualify(row)


def test_repaired_text_cannot_hide_original_ocr_disagreement(evidence):
    row, report, reseal = evidence
    row["raw_html"] = HTML.replace("r2l3", "r213")
    report["initial_raw_html_sha256"] = digest(row["raw_html"].encode())
    reseal()
    with pytest.raises(ValueError, match="initial raw OCR"):
        qualify(row)


def test_crop_decisions_are_not_production_authority(evidence):
    row, report, reseal = evidence
    table = report["tables"][0]
    table["review"]["html"] = HTML.replace("r2l3", "r213")
    table["decision"] = "initial_agrees_C"
    reseal()
    with pytest.raises(ValueError):
        qualify(row)


def test_source_identity_must_bind_actual_file(evidence, tmp_path):
    row, report, reseal = evidence
    source = tmp_path / "source.pdf"
    source.write_bytes(b"source bytes")
    report["source_pdf"] = {"name": source.name, "sha256": digest(source.read_bytes())}
    row["source"] = [str(source)]
    row["literal_fidelity"]["source_pdf_sha256"] = report["source_pdf"]["sha256"]
    reseal()
    assert qualify(row)
    source.write_bytes(b"different source")
    with pytest.raises(ValueError, match="PDF identity"):
        qualify(row)


def test_final_bundle_binds_report_and_rejects_changes_or_duplicates(evidence, tmp_path):
    row, _, _ = evidence
    qualified = qualify(row)
    output = tmp_path / "html"
    output.mkdir()
    entry_path = output / "chapter-001.html"
    entries = [{"path": entry_path.name}]
    entry_path.write_text(f"<html><body><article>{HTML}</article></body></html>")
    metadata = finalize_literal_fidelity_bundle(qualified, html_dir=output, entries=entries, run_id="literal-test")
    LiteralFidelityBundleQualification.model_validate(metadata)
    copied = output / metadata["reports"][0]["path"]
    assert copied.read_bytes() == open(row["literal_fidelity"]["report_path"], "rb").read()
    qualification = json.loads((output / metadata["qualification_path"]).read_text())
    assert qualification["entries"][0]["sha256"] == digest(entry_path.read_bytes())
    for content in [HTML.replace("r2l3", "r213"), HTML + HTML, "<p>missing</p>"]:
        entry_path.write_text(f"<html><body><article>{content}</article></body></html>")
        with pytest.raises(ValueError, match="final table"):
            finalize_literal_fidelity_bundle(qualified, html_dir=output, entries=entries, run_id="literal-test")


def test_no_table_receipt_still_requires_clean_independent_review(evidence):
    row, report, reseal = evidence
    row["html"] = row["raw_html"] = "<p>Only prose</p>"
    report.update({"tables": [], "table_count": 0, "reviewed_table_sequence_sha256": canonical_table_digest(row["html"]),
                   "initial_raw_html_sha256": digest(row["raw_html"].encode())})
    report["requests"][0]["raw_response"] = json.dumps({"source_table_count": 0, "tables": []})
    row["literal_fidelity"].update({"table_count": 0, "reviewed_table_sequence_sha256": report["reviewed_table_sequence_sha256"]})
    reseal()
    assert qualify(row)
    report["errors"] = ["B table inventory disagrees"]
    reseal()
    with pytest.raises(ValueError):
        qualify(row)


def test_partial_receipts_cannot_qualify_whole_input(evidence):
    row, _, _ = evidence
    missing = deepcopy(row)
    missing["page_number"] = 2
    missing.pop("literal_fidelity")
    with pytest.raises(ValueError, match="missing page receipt"):
        validate_literal_fidelity_inputs([row, missing], run_id="literal-test")


def test_builder_cli_publishes_only_verified_fresh_bundle(evidence, tmp_path):
    row, _, _ = evidence
    pages = tmp_path / "pages.jsonl"
    portions = tmp_path / "portions.jsonl"
    pages.write_text(json.dumps(row) + "\n")
    portions.write_text(json.dumps({"title": "Document", "page_start": 19,
                                   "page_end": 19, "source_pages": [1]}) + "\n")
    output, manifest = tmp_path / "html", tmp_path / "chapters.jsonl"
    command = [sys.executable, "-m", "modules.build.build_chapter_html_v1.main",
               "--pages", str(pages), "--portions", str(portions), "--out", str(manifest),
               "--output-dir", str(output), "--run-id", "literal-test", "--require-literal-fidelity"]
    result = subprocess.run(command, capture_output=True, text=True, cwd=Path(__file__).resolve().parents[1])
    assert result.returncode == 0, result.stderr
    bundle = DocWebBundleManifest.model_validate_json((output / "manifest.json").read_bytes())
    assert bundle.literal_fidelity.table_count == 1
    final = (output / bundle.entries[0].path).read_text()
    assert "r2l3" in final and "r213" not in final
    blocks = [json.loads(line) for line in (output / bundle.provenance_path).read_text().splitlines()]
    assert blocks[0]["source_page_number"] == 1
    assert blocks[0]["source_original_page_number"] == 19
    portable = bundle.model_dump()
    portable["source_artifact"] = "sha256:" + digest(pages.read_bytes())
    file_roles = {"manifest.json": "manifest", bundle.index_path: "index",
                  bundle.provenance_path: "provenance", **{entry.path: "entry" for entry in bundle.entries}}
    portable["files"] = [{"path": path, "role": role, "safe_to_persist": True, "safe_to_replay": True,
                          "privacy_class": "portable", "required_for_replay": True}
                         for path, role in file_roles.items()]
    with pytest.raises(ValueError, match="missing required replay paths"):
        DocWebBundleManifest.model_validate(portable)
    for path in [bundle.literal_fidelity.qualification_path,
                 *[report.path for report in bundle.literal_fidelity.reports]]:
        portable["files"].append({"path": path, "role": "asset", "safe_to_persist": True,
                                  "safe_to_replay": True, "privacy_class": "portable",
                                  "required_for_replay": True})
    DocWebBundleManifest.model_validate(portable)
    original_manifest = (output / "manifest.json").read_bytes()
    result = subprocess.run(command, capture_output=True, text=True, cwd=Path(__file__).resolve().parents[1])
    assert result.returncode != 0 and "fresh output paths" in result.stderr
    assert (output / "manifest.json").read_bytes() == original_manifest


def test_builder_cli_rejects_before_any_published_output(evidence, tmp_path):
    row, report, reseal = evidence
    report["tables"][0]["review"]["html"] = HTML.replace("r2l3", "r213")
    reseal()
    pages, portions = tmp_path / "pages.jsonl", tmp_path / "portions.jsonl"
    pages.write_text(json.dumps(row) + "\n")
    portions.write_text(json.dumps({"title": "Document", "page_start": 19, "page_end": 19}) + "\n")
    output, manifest = tmp_path / "html", tmp_path / "chapters.jsonl"
    command = [sys.executable, "-m", "modules.build.build_chapter_html_v1.main",
               "--pages", str(pages), "--portions", str(portions), "--out", str(manifest),
               "--output-dir", str(output), "--run-id", "literal-test", "--require-literal-fidelity"]
    result = subprocess.run(command, capture_output=True, text=True, cwd=Path(__file__).resolve().parents[1])
    assert result.returncode != 0 and "source response" in result.stderr
    assert not output.exists() and not manifest.exists()


@pytest.mark.parametrize("collision", ["out", "state", "progress", "state_progress_overlap"])
def test_literal_only_build_cannot_overwrite_validated_bundle_files(evidence, tmp_path, collision):
    row, _, _ = evidence
    pages, portions = tmp_path / "pages.jsonl", tmp_path / "portions.jsonl"
    pages.write_text(json.dumps(row) + "\n")
    portions.write_text(json.dumps({"title": "Document", "page_start": 19, "page_end": 19}) + "\n")
    output, manifest = tmp_path / "html", tmp_path / "chapters.jsonl"
    if collision == "out":
        manifest = output / "chapter-001.html"
    command = [sys.executable, "-m", "modules.build.build_chapter_html_v1.main",
               "--pages", str(pages), "--portions", str(portions), "--out", str(manifest),
               "--output-dir", str(output), "--run-id", "literal-test", "--require-literal-fidelity"]
    if collision == "state":
        command.extend(["--state-file", str(output / "manifest.json")])
    elif collision == "progress":
        command.extend(["--progress-file", str(output / "provenance/literal-fidelity/qualification.json")])
    elif collision == "state_progress_overlap":
        command.extend(["--state-file", str(tmp_path / "shared.json"),
                        "--progress-file", str(tmp_path / "shared.json")])
    result = subprocess.run(command, capture_output=True, text=True, cwd=Path(__file__).resolve().parents[1])
    assert result.returncode != 0 and "Reviewed build paths blocked" in result.stderr
    assert not output.exists() and not manifest.exists()
    assert not (tmp_path / "shared.json").exists()
