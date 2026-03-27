from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path("scripts/spikes/marker_page_html_prototype.py")


def test_marker_page_html_prototype_resolves_content_refs(tmp_path: Path) -> None:
    marker_json = tmp_path / "marker.json"
    marker_meta = tmp_path / "marker_meta.json"
    pdftotext = tmp_path / "source.txt"
    input_pdf = tmp_path / "sample.pdf"
    outdir = tmp_path / "out"

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
                            "<content-ref src='/page/0/TableOfContents/1'></content-ref>"
                        ),
                        "bbox": [0, 0, 100, 100],
                        "polygon": [[0, 0], [100, 0], [100, 100], [0, 100]],
                        "children": [
                            {
                                "id": "/page/0/SectionHeader/0",
                                "block_type": "SectionHeader",
                                "html": "<h1>Title</h1>",
                                "bbox": [1, 1, 2, 2],
                                "polygon": [[1, 1], [2, 1], [2, 2], [1, 2]],
                                "children": None,
                                "section_hierarchy": {"1": "/page/0/SectionHeader/0"},
                            },
                            {
                                "id": "/page/0/TableOfContents/1",
                                "block_type": "TableOfContents",
                                "html": "<p></p>",
                                "bbox": [3, 3, 4, 4],
                                "polygon": [[3, 3], [4, 3], [4, 4], [3, 4]],
                                "children": [
                                    {
                                        "id": "/page/0/Line/2",
                                        "block_type": "Line",
                                        "html": "- Entry ..... 7",
                                        "bbox": [5, 5, 6, 6],
                                        "polygon": [[5, 5], [6, 5], [6, 6], [5, 6]],
                                        "children": None,
                                        "section_hierarchy": {"1": "/page/0/SectionHeader/0"},
                                    }
                                ],
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
    pdftotext.write_text("Title Entry", encoding="utf-8")
    input_pdf.write_bytes(b"%PDF-1.4\n")

    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--input-pdf",
            str(input_pdf),
            "--marker-json",
            str(marker_json),
            "--marker-meta",
            str(marker_meta),
            "--pdftotext",
            str(pdftotext),
            "--outdir",
            str(outdir),
            "--run-id",
            "marker-page-html-test",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert "Summary written to" in proc.stdout

    pages_path = outdir / "pages_html.jsonl"
    blocks_path = outdir / "marker_blocks.jsonl"
    summary_path = outdir / "summary.json"
    bundle_manifest_path = outdir / "doc_web_bundle" / "manifest.json"
    bundle_page_path = outdir / "doc_web_bundle" / "page-001.html"
    bundle_provenance_path = outdir / "doc_web_bundle" / "provenance" / "blocks.jsonl"
    runtime_trace_path = outdir / "runtime_trace.json"

    page_rows = [json.loads(line) for line in pages_path.read_text(encoding="utf-8").splitlines()]
    block_rows = [json.loads(line) for line in blocks_path.read_text(encoding="utf-8").splitlines()]
    bundle_manifest = json.loads(bundle_manifest_path.read_text(encoding="utf-8"))
    bundle_provenance = [
        json.loads(line) for line in bundle_provenance_path.read_text(encoding="utf-8").splitlines()
    ]
    runtime_trace = json.loads(runtime_trace_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert len(page_rows) == 1
    assert page_rows[0]["schema_version"] == "page_html_v1"
    assert "Title</h1>" in page_rows[0]["html"]
    assert "Entry" in page_rows[0]["html"]
    assert 'data-source-element-id="/page/0/SectionHeader/0"' in page_rows[0]["html"]
    assert page_rows[0]["raw_html"].startswith("<content-ref")

    assert len(block_rows) == 4
    assert {row["marker_block_type"] for row in block_rows} == {
        "Page",
        "SectionHeader",
        "TableOfContents",
        "Line",
    }
    assert any(row["marker_block_id"] == "/page/0/Line/2" for row in block_rows)

    assert summary["signals"]["page_count"] == 1
    assert summary["signals"]["token_coverage_vs_pdftotext"] == 1.0
    assert summary["output_artifacts"]["pages_html"] == str(pages_path)
    assert summary["signals"]["doc_web_bundle_entry_count"] == 1
    assert summary["signals"]["doc_web_provenance_block_count"] == 2

    assert bundle_manifest["schema_version"] == "doc_web_bundle_manifest_v1"
    assert bundle_manifest["reading_order"] == ["page-001"]
    assert bundle_manifest["entries"][0]["path"] == "page-001.html"
    assert "blk-page-001-0001" in bundle_page_path.read_text(encoding="utf-8")

    assert len(bundle_provenance) == 2
    assert bundle_provenance[0]["block_id"] == "blk-page-001-0001"
    assert bundle_provenance[0]["source_element_ids"] == ["/page/0/SectionHeader/0"]
    assert bundle_provenance[0]["confidence"] == 1.0

    assert runtime_trace[0]["text_extraction_method"] == "pdftext"
