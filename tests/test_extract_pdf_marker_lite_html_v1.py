from __future__ import annotations

import json
import sys
from pathlib import Path

from modules.extract.extract_pdf_marker_lite_html_v1 import main as module_main


def _write_marker_fixture(base: Path) -> tuple[Path, Path, Path]:
    marker_json = base / "sample.json"
    marker_meta = base / "sample_meta.json"
    pdftotext = base / "sample.pdftotext.txt"

    marker_json.write_text(
        json.dumps(
            {
                "block_type": "Document",
                "children": [
                    {
                        "id": "/page/0/Page/1",
                        "block_type": "Page",
                        "html": (
                            "<content-ref src='/page/0/SectionHeader/0'></content-ref>"
                            "<content-ref src='/page/0/Text/1'></content-ref>"
                        ),
                        "bbox": [0, 0, 100, 100],
                        "children": [
                            {
                                "id": "/page/0/SectionHeader/0",
                                "block_type": "SectionHeader",
                                "html": "<h2>Section 1</h2>",
                                "bbox": [1, 1, 10, 10],
                                "children": None,
                                "section_hierarchy": {"1": "/page/0/SectionHeader/0"},
                            },
                            {
                                "id": "/page/0/Text/1",
                                "block_type": "Text",
                                "html": "<p>If you <strong>go left</strong>, turn to <strong>2</strong>.</p>",
                                "bbox": [11, 11, 20, 20],
                                "children": None,
                                "section_hierarchy": {"1": "/page/0/SectionHeader/0"},
                            },
                        ],
                        "section_hierarchy": {},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    marker_meta.write_text(
        json.dumps(
            {
                "page_stats": [
                    {
                        "page_id": 0,
                        "text_extraction_method": "pdftext",
                        "block_metadata": {"llm_request_count": 0},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    pdftotext.write_text("Section 1 If you go left turn to 2", encoding="utf-8")
    return marker_json, marker_meta, pdftotext


def test_extract_pdf_marker_lite_html_writes_contract_sidecars(tmp_path: Path, monkeypatch) -> None:
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n")
    marker_json, marker_meta, pdftotext = _write_marker_fixture(tmp_path)
    outdir = tmp_path / "out"

    class FakeArtifact:
        def __init__(self, main_output: Path, meta_output: Path) -> None:
            self.main_output = main_output
            self.meta_output = meta_output
            self.log_output = tmp_path / "marker.log"
            self.log_output.write_text("ok", encoding="utf-8")

    monkeypatch.setattr(
        module_main,
        "ensure_runtime_container",
        lambda **_: {"container_name": "story168-marker-test", "action": "rebuilt_from_cached_image", "notes": []},
    )
    monkeypatch.setattr(
        module_main,
        "extract_pdftotext_source",
        lambda pdf_path, out_dir, progress=None: pdftotext,
    )
    monkeypatch.setattr(
        module_main,
        "run_lite_api",
        lambda **_: FakeArtifact(marker_json, marker_meta),
    )
    monkeypatch.setattr(
        module_main,
        "runtime_metadata",
        lambda container_name: {"container_name": container_name, "packages": {"marker-pdf": {"version": "1.10.2"}}},
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "extract_pdf_marker_lite_html_v1",
            "--pdf",
            str(pdf_path),
            "--outdir",
            str(outdir),
            "--run-id",
            "marker-lite-module-test",
        ],
    )

    module_main.main()

    pages_path = outdir / "pages_html.jsonl"
    runtime_path = outdir / "marker_runtime.json"
    summary_path = outdir / "summary.json"
    normalization_report_path = outdir / "normalization_report.json"
    bundle_manifest_path = outdir / "doc_web_bundle" / "manifest.json"
    bundle_provenance_path = outdir / "doc_web_bundle" / "provenance" / "blocks.jsonl"

    assert pages_path.exists()
    assert runtime_path.exists()
    assert summary_path.exists()
    assert normalization_report_path.exists()
    assert bundle_manifest_path.exists()
    assert bundle_provenance_path.exists()

    page_rows = [json.loads(line) for line in pages_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    runtime_report = json.loads(runtime_path.read_text(encoding="utf-8"))

    assert len(page_rows) == 1
    assert page_rows[0]["schema_version"] == "page_html_v1"
    assert summary["runtime"]["bootstrap_action"] == "rebuilt_from_cached_image"
    assert summary["output_artifacts"]["normalization_report"] == str(normalization_report_path)
    assert runtime_report["raw_artifacts"]["marker_json"] == str(marker_json)
