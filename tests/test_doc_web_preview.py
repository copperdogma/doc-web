import json
import subprocess
import sys
from types import SimpleNamespace
from pathlib import Path

from doc_web.preview import build_preview
import doc_web.preview_content_hint as preview_content_hint
import doc_web.preview as preview_module
from doc_web.preview_content_hint import build_content_hint
from schemas import (
    DocWebBundleManifest,
    DocWebPreviewMetadata,
    DocWebPreviewSelectorMap,
    DocWebProvenanceBlock,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
BAD_SUMMARY_PHRASES = ("Likely", "likely", "titled or headed")


def _load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _load_preview(
    bundle_dir: Path,
) -> tuple[DocWebBundleManifest, DocWebPreviewMetadata, list[DocWebProvenanceBlock]]:
    manifest = DocWebBundleManifest(
        **json.loads((bundle_dir / "manifest.json").read_text(encoding="utf-8"))
    )
    metadata = DocWebPreviewMetadata(
        **json.loads((bundle_dir / "preview_metadata.json").read_text(encoding="utf-8"))
    )
    blocks = [
        DocWebProvenanceBlock(**row)
        for row in _load_jsonl(bundle_dir / "provenance" / "blocks.jsonl")
    ]
    return manifest, metadata, blocks


def _assert_direct_summary(summary: str) -> None:
    assert summary
    for phrase in BAD_SUMMARY_PHRASES:
        assert phrase not in summary


def test_cli_preview_help_is_supported():
    proc = subprocess.run(
        [sys.executable, "-m", "doc_web", "preview", "--help"],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert proc.returncode == 0, proc.stderr
    assert "--input" in proc.stdout
    assert "--out-dir" in proc.stdout
    assert "--content-hint-mode" in proc.stdout


def test_cli_preview_timeout_emits_failed_status(tmp_path: Path):
    bundle_dir = tmp_path / "timeout-preview"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "doc_web",
            "preview",
            "--input",
            "testdata/flat-born-digital-mini.pdf",
            "--out-dir",
            str(bundle_dir),
            "--timeout-seconds",
            "0.001",
            "--content-hint-mode",
            "deterministic",
            "--json",
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert proc.returncode == 1
    assert "Traceback" not in proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["status"] == "failed"
    status_rows = _load_jsonl(bundle_dir / "preview_status.jsonl")
    assert status_rows[-1]["stage"] == "failed"
    assert status_rows[-1]["detail"]["reason"] == "timeout"


def test_born_digital_pdf_preview_writes_valid_bundle(tmp_path: Path):
    bundle_dir = tmp_path / "flat-pdf-preview"
    summary = build_preview(
        input_path=REPO_ROOT / "testdata" / "flat-born-digital-mini.pdf",
        out_dir=bundle_dir,
        content_hint_mode="deterministic",
    )

    manifest, metadata, blocks = _load_preview(bundle_dir)
    selector_map = DocWebPreviewSelectorMap(
        **json.loads(
            (bundle_dir / "preview_to_full_selectors.json").read_text(encoding="utf-8")
        )
    )

    assert summary["coverage_state"] == "complete"
    assert manifest.reading_order == ["page-001", "page-002"]
    assert metadata.coverage_state == "complete"
    assert metadata.structural_facts["text_layer_available"] is True
    assert metadata.content_hint is not None
    assert metadata.content_hint.status == "available"
    _assert_direct_summary(metadata.content_hint.high_level_summary)
    assert metadata.timing_ms["first_status_ms"] <= 500
    assert metadata.timing_ms["preview_ready_ms"] <= 3000
    assert [event.stage for event in metadata.status_events] == [
        "accepted",
        "preparing_pages",
        "detecting_text_or_ocr_need",
        "reading_sample",
        "building_preview_html",
        "preview_ready",
    ]
    assert blocks
    assert all(block.source_page_number in {1, 2} for block in blocks)
    assert all(block.confidence == 1.0 for block in blocks)
    assert selector_map.mappings
    assert all(mapping.mapping_kind == "preserved" for mapping in selector_map.mappings)
    assert (bundle_dir / "cache" / "cache_identity.json").exists()
    parsed_units = _load_jsonl(bundle_dir / "cache" / "parsed_units.jsonl")
    assert len(parsed_units) == len(blocks)
    assert parsed_units[0]["block_id"] == blocks[0].block_id
    assert (
        metadata.cache_identity["reusable_artifacts"]["parsed_units"]
        == "cache/parsed_units.jsonl"
    )
    assert 'id="blk-page-001-0001"' in (bundle_dir / "page-001.html").read_text(
        encoding="utf-8"
    )


def test_scan_heavy_pdf_preview_is_honestly_deferred(tmp_path: Path):
    bundle_dir = tmp_path / "scanned-pdf-preview"
    summary = build_preview(
        input_path=REPO_ROOT / "testdata" / "scanned-prose-mini.pdf",
        out_dir=bundle_dir,
        content_hint_mode="deterministic",
    )

    manifest, metadata, blocks = _load_preview(bundle_dir)

    assert summary["coverage_state"] == "deferred"
    assert manifest.reading_order == ["page-001"]
    assert metadata.coverage_state == "deferred"
    assert metadata.structural_facts["text_layer_available"] is False
    assert metadata.structural_facts["ocr_needed"] is True
    assert metadata.content_hint is not None
    assert metadata.content_hint.status == "deferred"
    _assert_direct_summary(metadata.content_hint.high_level_summary)
    assert metadata.skipped_units
    assert not blocks
    html = (bundle_dir / "page-001.html").read_text(encoding="utf-8")
    assert "Preview text is deferred" in html
    assert "OCR is deferred" in " ".join(metadata.warnings)


def test_image_directory_preview_runs_bounded_ocr(tmp_path: Path):
    bundle_dir = tmp_path / "image-directory-preview"
    summary = build_preview(
        input_path=REPO_ROOT / "testdata" / "handwritten-notes-mini-images",
        out_dir=bundle_dir,
        content_hint_mode="deterministic",
    )

    manifest, metadata, blocks = _load_preview(bundle_dir)

    assert summary["coverage_state"] == "sampled"
    assert manifest.reading_order == ["page-002"]
    assert metadata.coverage_state == "sampled"
    assert metadata.structural_facts["format"] == "image_directory"
    assert metadata.structural_facts["image_count"] == 2
    assert metadata.structural_facts["sampled_image_count"] == 1
    assert metadata.structural_facts["ocr_engine"] == "tesseract"
    assert metadata.structural_facts["ocr_text_chars"] > 50
    assert metadata.structural_facts["text_layer_available"] is False
    assert metadata.structural_facts["ocr_needed"] is True
    assert metadata.skipped_units
    assert blocks
    assert metadata.content_hint is not None
    assert metadata.content_hint.status == "available"
    _assert_direct_summary(metadata.content_hint.high_level_summary)
    parsed_units = _load_jsonl(bundle_dir / "cache" / "parsed_units.jsonl")
    assert len(parsed_units) == len(blocks)
    html = (bundle_dir / "page-002.html").read_text(encoding="utf-8")
    assert "attic boxes" in html


def test_content_hint_summary_is_direct_and_strips_source_site():
    hint = build_content_hint(
        facts={
            "format": "pdf",
            "metadata_title": "Robo Rally Rulebook - 1jour-1jeu.com",
            "text_layer_available": True,
        },
        parsed_units=[
            {
                "text": (
                    "Game contents include robot figures, reboot tokens, "
                    "programming cards, checkpoints, and gameboards."
                )
            }
        ],
        coverage_state="sampled",
        warnings=[],
    )

    assert hint["status"] == "available"
    assert hint["title_guess"] == "Robo Rally Rulebook"
    assert hint["document_kind_hint"] == "game rulebook"
    assert hint["high_level_summary"] == (
        "Robo Rally Rulebook is a game rulebook covering components and "
        "robot programming."
    )
    _assert_direct_summary(hint["high_level_summary"])
    assert " or " not in hint["document_kind_hint"]


def test_content_hint_deterministic_family_history_title_summary():
    hint = build_content_hint(
        facts={"format": "image_directory"},
        parsed_units=[
            {"text": ("ONWARD TO THE UNKNOWN 1887 - 1987 Moise and Sophie L’Heureux")}
        ],
        coverage_state="sampled",
        warnings=[],
        mode="deterministic",
    )

    assert hint["document_kind_hint"] == "family history"
    assert hint["high_level_summary"] == (
        "ONWARD TO THE UNKNOWN 1887-1987 is a family history about "
        "Moise and Sophie L’Heureux."
    )


def test_content_hint_deterministic_family_subtitle_summary():
    hint = build_content_hint(
        facts={
            "format": "pdf",
            "metadata_title": (
                "Onward to the Unknown: A Genealogy and Biography of the "
                "L'Heureux Family"
            ),
        },
        parsed_units=[{"text": "genealogy biography family descendants"}],
        coverage_state="sampled",
        warnings=[],
        mode="deterministic",
    )

    assert hint["document_kind_hint"] == "family history"
    assert hint["high_level_summary"] == (
        "Onward to the Unknown is a family history about the L'Heureux family."
    )


def test_content_hint_ai_pass_uses_model_json(monkeypatch):
    calls: list[dict] = []
    clients: list[dict] = []

    class _DummyCompletions:
        def create(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content=json.dumps(
                                {
                                    "title_guess": "Onward to the Unknown",
                                    "document_kind_hint": "family history",
                                    "high_level_summary": (
                                        "The document traces the L'Heureux "
                                        "family history."
                                    ),
                                }
                            )
                        )
                    )
                ],
                usage=SimpleNamespace(prompt_tokens=100, completion_tokens=30),
            )

    def _dummy_openai_client(**kwargs):
        clients.append(kwargs)
        return SimpleNamespace(chat=SimpleNamespace(completions=_DummyCompletions()))

    monkeypatch.setattr(
        preview_content_hint, "_make_openai_client", _dummy_openai_client
    )
    monkeypatch.setattr(
        preview_content_hint,
        "get_doc_web_api_key",
        lambda provider, env=None: "test-key",
    )

    hint = build_content_hint(
        facts={
            "format": "pdf",
            "metadata_title": (
                "Onward to the Unknown: A Genealogy and Biography of the "
                "L'Heureux Family"
            ),
            "metadata_creator": "OCRmyPDF 16.6.2 / Tesseract OCR-hOCR 5.5.0",
        },
        parsed_units=[
            {
                "text": (
                    "Moise and Sophie L'Heureux family biography genealogy "
                    "children born married descendants."
                )
            }
        ],
        coverage_state="sampled",
        warnings=[],
        mode="ai",
        ai_model="test-cheap-model",
        ai_timeout_seconds=0.5,
        source_sha256="a" * 64,
    )

    assert hint["summary_provider"] == "openai"
    assert hint["summary_model"] == "test-cheap-model"
    assert hint["document_kind_hint"] == "family history"
    assert hint["high_level_summary"] == (
        "Onward to the Unknown traces the L'Heureux family history."
    )
    assert "ai_summary:openai:test-cheap-model" in hint["basis"]
    assert hint["cache_key"].startswith("sha256:")
    assert clients[0]["max_retries"] == 0
    assert calls[0]["model"] == "test-cheap-model"
    assert calls[0]["response_format"] == {"type": "json_object"}


def test_content_hint_ai_trims_long_title_prefix(monkeypatch):
    class _DummyCompletions:
        def create(self, **kwargs):
            title = (
                "Onward to the Unknown: A Genealogy and Biography of the "
                "L'Heureux Family"
            )
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content=json.dumps(
                                {
                                    "title_guess": title,
                                    "document_kind_hint": "family history",
                                    "high_level_summary": (
                                        f"{title} is a family history detailing "
                                        "the genealogy and biography of the "
                                        "L'Heureux family."
                                    ),
                                }
                            )
                        )
                    )
                ],
                usage=SimpleNamespace(prompt_tokens=100, completion_tokens=30),
            )

    def _dummy_openai_client(**kwargs):
        return SimpleNamespace(chat=SimpleNamespace(completions=_DummyCompletions()))

    monkeypatch.setattr(
        preview_content_hint, "_make_openai_client", _dummy_openai_client
    )
    monkeypatch.setattr(
        preview_content_hint,
        "get_doc_web_api_key",
        lambda provider, env=None: "test-key",
    )

    hint = build_content_hint(
        facts={"format": "pdf"},
        parsed_units=[{"text": "family genealogy biography descendants"}],
        coverage_state="sampled",
        warnings=[],
        mode="ai",
        source_sha256="b" * 64,
    )

    assert hint["high_level_summary"] == (
        "A family history detailing the genealogy and biography of the "
        "L'Heureux family."
    )


def test_auto_content_hint_respects_preview_deadline(tmp_path: Path, monkeypatch):
    calls: list[dict] = []

    def _fake_content_hint(**kwargs):
        calls.append(kwargs)
        return {
            "status": "available",
            "title_guess": "Acme Community Arts Initiative",
            "document_kind_hint": "report",
            "high_level_summary": "Acme Community Arts Initiative is a report.",
            "basis": ["test"],
            "evidence": [],
            "warnings": [],
            "text_quality_score": 1.0,
            "coverage_state": "complete",
        }

    monkeypatch.setattr(preview_module, "build_content_hint", _fake_content_hint)

    build_preview(
        input_path=REPO_ROOT / "testdata" / "flat-born-digital-mini.pdf",
        out_dir=tmp_path / "deadline-preview",
        usable_deadline_seconds=0.001,
        content_hint_mode="auto",
    )

    assert calls[0]["mode"] == "deterministic"


def test_auto_content_hint_skips_ai_for_image_directory(tmp_path: Path, monkeypatch):
    calls: list[dict] = []

    def _fake_content_hint(**kwargs):
        calls.append(kwargs)
        return {
            "status": "available",
            "title_guess": "Handwritten Notes",
            "document_kind_hint": "notes",
            "high_level_summary": "Handwritten Notes is a notes collection.",
            "basis": ["test"],
            "evidence": [],
            "warnings": [],
            "text_quality_score": 1.0,
            "coverage_state": "sampled",
        }

    monkeypatch.setattr(preview_module, "build_content_hint", _fake_content_hint)

    build_preview(
        input_path=REPO_ROOT / "testdata" / "handwritten-notes-mini-images",
        out_dir=tmp_path / "image-auto-preview",
        content_hint_mode="auto",
    )

    assert calls[0]["mode"] == "deterministic"


def test_docx_preview_is_pageless_and_selector_stable(tmp_path: Path):
    bundle_dir = tmp_path / "docx-preview"
    summary = build_preview(
        input_path=REPO_ROOT / "testdata" / "docx-sections-mini.docx",
        out_dir=bundle_dir,
        content_hint_mode="deterministic",
    )

    manifest, metadata, blocks = _load_preview(bundle_dir)
    selector_map = DocWebPreviewSelectorMap(
        **json.loads(
            (bundle_dir / "preview_to_full_selectors.json").read_text(encoding="utf-8")
        )
    )

    assert summary["coverage_state"] == "complete"
    assert manifest.reading_order == ["chapter-001", "chapter-002"]
    assert [entry.title for entry in manifest.entries] == ["Overview", "Roster"]
    assert metadata.structural_facts["pageless"] is True
    assert metadata.structural_facts["paragraph_count"] == 7
    assert blocks
    assert all(block.source_page_number is None for block in blocks)
    assert all(block.source_element_ids[0].startswith("docx-") for block in blocks)
    assert selector_map.mappings
    assert all(
        mapping.preview_block_id == mapping.full_block_id
        for mapping in selector_map.mappings
    )
    parsed_units = _load_jsonl(bundle_dir / "cache" / "parsed_units.jsonl")
    assert parsed_units[2]["source_element_ids"] == ["docx-paragraph-0004"]
    assert "The wider proof should keep both paragraphs" in (
        bundle_dir / "chapter-001.html"
    ).read_text(encoding="utf-8")


def test_preview_artifacts_validate_with_schema_cli(tmp_path: Path):
    bundle_dir = tmp_path / "cli-preview"
    build_preview(
        input_path=REPO_ROOT / "testdata" / "flat-born-digital-mini.pdf",
        out_dir=bundle_dir,
        content_hint_mode="deterministic",
    )

    for schema, filename in [
        ("doc_web_bundle_manifest_v1", "manifest.json"),
        ("doc_web_provenance_block_v1", "provenance/blocks.jsonl"),
        ("doc_web_preview_metadata_v1", "preview_metadata.json"),
        ("doc_web_preview_selector_map_v1", "preview_to_full_selectors.json"),
    ]:
        proc = subprocess.run(
            [
                sys.executable,
                "validate_artifact.py",
                "--schema",
                schema,
                "--file",
                str(bundle_dir / filename),
            ],
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        assert proc.returncode == 0, proc.stdout
