import json
import hashlib
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
import re

import pytest
from pydantic import ValidationError

from schemas import (
    ChapterHtmlManifestEntry,
    DocWebBundleManifest,
    DocWebPreviewContentHint,
    DocWebPreviewCacheIdentity,
    DocWebPreviewSelectorMap,
    DocWebProvenanceBlock,
)
from validate_artifact import SCHEMA_MAP


REPO_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_DIR = (
    REPO_ROOT
    / "benchmarks"
    / "golden"
    / "onward"
    / "reviewed_html_slice"
    / "story149-onward-build-regression-r1"
)
DOSSIER_HANDOFF_DIR = (
    REPO_ROOT
    / "benchmarks"
    / "golden"
    / "onward"
    / "dossier-doc-web-handoff-v1"
)
VALIDATOR = REPO_ROOT / "validate_artifact.py"


DOC_WEB_BUNDLE_MANIFEST_EXAMPLE = {
    "schema_version": "doc_web_bundle_manifest_v1",
    "document_id": "onward-to-the-unknown",
    "title": "Onward to the Unknown",
    "creator": "",
    "source_artifact": "input/onward-to-the-unknown-images",
    "index_path": "index.html",
    "entries": [
        {
            "entry_id": "chapter-010",
            "kind": "chapter",
            "title": "ARTHUR L'HEUREUX",
            "path": "chapter-010.html",
            "order": 1,
            "next_entry_id": "chapter-011",
            "source_pages": [28, 29, 30, 31, 32, 33, 34, 35, 36, 37],
            "printed_pages": [19, 20, 21, 22, 23, 24, 25, 26, 27, 28],
        },
        {
            "entry_id": "chapter-011",
            "kind": "chapter",
            "title": "LEONIDAS L'HEUREUX",
            "path": "chapter-011.html",
            "order": 2,
            "prev_entry_id": "chapter-010",
            "source_pages": [38, 39, 40, 41, 42, 43, 44, 45, 46, 47],
            "printed_pages": [29, 30, 31, 32, 33, 34, 35, 36, 37, 38],
        },
    ],
    "reading_order": ["chapter-010", "chapter-011"],
    "asset_roots": ["images"],
    "provenance_path": "provenance/blocks.jsonl",
}


DOC_WEB_PROVENANCE_BLOCK_EXAMPLE = [
    {
        "schema_version": "doc_web_provenance_block_v1",
        "block_id": "blk-chapter-010-0001",
        "entry_id": "chapter-010",
        "block_kind": "paragraph",
        "source_page_number": 28,
        "source_printed_page_number": 19,
        "source_element_ids": ["el-028-001"],
        "text_quote": "Although weddings are meant to be happy occasions...",
    },
    {
        "schema_version": "doc_web_provenance_block_v1",
        "block_id": "blk-chapter-010-0002",
        "entry_id": "chapter-010",
        "block_kind": "figure",
        "source_page_number": 28,
        "source_printed_page_number": 19,
        "source_element_ids": ["el-028-fig-001"],
        "confidence": 0.94,
    },
]


DOC_WEB_PROVENANCE_PAGELESS_BLOCK_EXAMPLE = {
    "schema_version": "doc_web_provenance_block_v1",
    "block_id": "blk-chapter-001-0001",
    "entry_id": "chapter-001",
    "block_kind": "heading",
    "source_element_ids": ["docx-paragraph-001"],
    "text_quote": "Family Snapshot",
}


def _cache_identity_fingerprint(payload: dict) -> str:
    source_identity = {
        key: value
        for key, value in payload["source_identity"].items()
        if key != "source_display_label"
    }
    fingerprint_payload = {
        "source_identity": source_identity,
        "doc_web_version": payload["doc_web_version"],
        "doc_web_ref": payload["doc_web_ref"],
        "parser_settings": payload["parser_settings"],
        "runtime_options": payload["runtime_options"],
        "preview_contract_fingerprint": payload["preview_contract_fingerprint"],
        "bundle_fingerprint": payload["bundle_fingerprint"],
        "content_hint": {
            "mode": payload["content_hint"]["mode"],
            "effective_mode": payload["content_hint"]["effective_mode"],
            "provider": payload["content_hint"].get("provider"),
            "model": payload["content_hint"].get("model"),
            "prompt_version": payload["content_hint"].get("prompt_version"),
            "sample_sha256": payload["content_hint"].get("sample_sha256"),
            "cache_key": payload["content_hint"].get("cache_key"),
            "fallback_reason": payload["content_hint"].get("fallback_reason"),
            "requested_timeout_seconds": payload["content_hint"][
                "requested_timeout_seconds"
            ],
        },
    }
    encoded = json.dumps(
        fingerprint_payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _doc_web_cache_identity_example():
    source_sha256 = "a" * 64
    payload = {
        "identity_schema_version": "doc_web_cache_identity_v1",
        "source_identity": {
            "source_ref": f"sha256:{source_sha256}",
            "source_sha256": source_sha256,
            "source_hash_algorithm": "sha256",
            "source_hash_origin": "doc-web-computed",
            "page_count": 2,
            "source_unit_count": 2,
        },
        "doc_web_version": "0.1.0",
        "doc_web_ref": "git-abcdef0",
        "parser_settings": {
            "parser": "pypdf",
            "ocr_engine": "tesseract",
            "ocr_rasterizer": "pdftoppm-singlefile",
        },
        "runtime_options": {"max_sample_units": 2},
        "preview_contract_fingerprint": "sha256:" + ("b" * 64),
        "bundle_fingerprint": "sha256:" + ("c" * 64),
        "reusable_artifacts": {
            "parsed_units": "cache/parsed_units.jsonl",
            "selector_map": "preview_to_full_selectors.json",
        },
        "content_hint": {
            "mode": "deterministic",
            "effective_mode": "deterministic",
            "sample_sha256": "d" * 64,
            "cache_key": "sha256:" + ("e" * 64),
            "fallback_reason": "content-hint-disabled",
            "requested_timeout_seconds": 0.0,
        },
    }
    payload["identity_fingerprint"] = _cache_identity_fingerprint(payload)
    return payload


def _doc_web_preview_manifest_example():
    source_sha256 = "a" * 64
    manifest = deepcopy(DOC_WEB_BUNDLE_MANIFEST_EXAMPLE)
    manifest.update(
        {
            "module_id": "doc_web_preview_v1",
            "document_id": "doc-aaaaaaaaaaaa",
            "source_artifact": f"sha256:{source_sha256}",
            "entries": [
                {
                    "entry_id": "page-001",
                    "kind": "page",
                    "title": "Page 1",
                    "path": "page-001.html",
                    "order": 1,
                    "source_pages": [1],
                    "printed_pages": [],
                }
            ],
            "reading_order": ["page-001"],
            "asset_roots": [],
            "files": [
                {
                    "path": "manifest.json",
                    "role": "manifest",
                    "safe_to_persist": True,
                    "safe_to_replay": True,
                    "privacy_class": "portable",
                    "required_for_replay": True,
                },
                {
                    "path": "index.html",
                    "role": "index",
                    "safe_to_persist": True,
                    "safe_to_replay": True,
                    "privacy_class": "portable",
                    "required_for_replay": True,
                },
                {
                    "path": "provenance/blocks.jsonl",
                    "role": "provenance",
                    "safe_to_persist": True,
                    "safe_to_replay": True,
                    "privacy_class": "portable",
                    "required_for_replay": True,
                },
                {
                    "path": "preview_metadata.json",
                    "role": "preview_metadata",
                    "safe_to_persist": True,
                    "safe_to_replay": True,
                    "privacy_class": "portable",
                    "required_for_replay": True,
                },
                {
                    "path": "preview_status.jsonl",
                    "role": "preview_status",
                    "safe_to_persist": True,
                    "safe_to_replay": False,
                    "privacy_class": "portable",
                    "required_for_replay": False,
                },
                {
                    "path": "preview_to_full_selectors.json",
                    "role": "selector_map",
                    "safe_to_persist": True,
                    "safe_to_replay": True,
                    "privacy_class": "portable",
                    "required_for_replay": True,
                },
                {
                    "path": "cache/cache_identity.json",
                    "role": "cache_identity",
                    "safe_to_persist": True,
                    "safe_to_replay": True,
                    "privacy_class": "portable",
                    "required_for_replay": True,
                },
                {
                    "path": "cache/parsed_units.jsonl",
                    "role": "parsed_units",
                    "safe_to_persist": True,
                    "safe_to_replay": True,
                    "privacy_class": "portable",
                    "required_for_replay": True,
                },
                {
                    "path": "page-001.html",
                    "role": "entry",
                    "safe_to_persist": True,
                    "safe_to_replay": True,
                    "privacy_class": "portable",
                    "required_for_replay": True,
                },
            ],
        }
    )
    return manifest


def _load_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_chapter_html_manifest_schema_validates_committed_golden_slice():
    rows = _load_jsonl(GOLDEN_DIR / "chapters_manifest_regression.jsonl")

    parsed = [ChapterHtmlManifestEntry(**row) for row in rows]

    assert len(parsed) == 33
    assert sum(1 for row in parsed if row.kind == "chapter") == 24
    assert sum(1 for row in parsed if row.kind == "page") == 9
    assert parsed[9].title == "The Ancestral Lineage of Moïse and Sophie"


def test_doc_web_bundle_manifest_roundtrip_via_schema_map():
    model_cls = SCHEMA_MAP["doc_web_bundle_manifest_v1"]
    manifest = model_cls(**DOC_WEB_BUNDLE_MANIFEST_EXAMPLE)

    assert isinstance(manifest, DocWebBundleManifest)
    assert manifest.reading_order == ["chapter-010", "chapter-011"]
    assert manifest.entries[0].path == "chapter-010.html"
    assert manifest.entries[0].printed_page_start == 19
    assert manifest.provenance_path == "provenance/blocks.jsonl"


def test_doc_web_cache_identity_roundtrip_via_schema_map():
    model_cls = SCHEMA_MAP["doc_web_cache_identity_v1"]
    cache_identity = model_cls(**_doc_web_cache_identity_example())

    assert isinstance(cache_identity, DocWebPreviewCacheIdentity)
    assert cache_identity.reusable_artifacts.parsed_units == "cache/parsed_units.jsonl"
    assert cache_identity.identity_fingerprint == _cache_identity_fingerprint(
        _doc_web_cache_identity_example()
    )


def test_doc_web_cache_identity_allows_rewriteable_display_label():
    payload = _doc_web_cache_identity_example()
    before = DocWebPreviewCacheIdentity(**payload)
    payload["source_identity"]["source_display_label"] = (
        "/private/client/renamed-donor-source.pdf"
    )
    after = DocWebPreviewCacheIdentity(**payload)

    assert before.identity_fingerprint == after.identity_fingerprint
    assert after.source_identity.source_display_label.endswith("renamed-donor-source.pdf")


def test_doc_web_cache_identity_allows_sha256_identity_values_outside_source_ref():
    payload = _doc_web_cache_identity_example()
    payload["runtime_options"]["upstream_identity"] = "sha256:" + ("1" * 64)
    payload["identity_fingerprint"] = _cache_identity_fingerprint(payload)

    cache_identity = DocWebPreviewCacheIdentity(**payload)

    assert cache_identity.runtime_options["upstream_identity"] == "sha256:" + (
        "1" * 64
    )


def test_doc_web_cache_identity_rejects_stale_identity_fingerprint():
    payload = _doc_web_cache_identity_example()
    payload["runtime_options"]["max_sample_units"] = 3

    with pytest.raises(ValidationError, match="identity_fingerprint must match"):
        DocWebPreviewCacheIdentity(**payload)


def test_doc_web_cache_identity_allows_colon_model_ids():
    payload = _doc_web_cache_identity_example()
    model_id = "ft:gpt-4.1-nano:org:custom:abc"
    payload["runtime_options"]["content_hint_model"] = model_id
    payload["content_hint"]["model"] = model_id
    payload["identity_fingerprint"] = _cache_identity_fingerprint(payload)

    cache_identity = DocWebPreviewCacheIdentity(**payload)

    assert cache_identity.runtime_options["content_hint_model"] == model_id
    assert cache_identity.content_hint.model == model_id


@pytest.mark.parametrize(
    "field_path",
    [
        ("source_identity", "source_ref"),
        ("preview_contract_fingerprint",),
        ("bundle_fingerprint",),
        ("content_hint", "cache_key"),
        ("identity_fingerprint",),
    ],
)
def test_doc_web_cache_identity_rejects_malformed_sha256_refs(
    field_path: tuple[str, ...],
):
    payload = _doc_web_cache_identity_example()
    target = payload
    for key in field_path[:-1]:
        target = target[key]
    target[field_path[-1]] = "sha256:" + ("1" * 63)

    with pytest.raises(ValidationError, match="sha256"):
        DocWebPreviewCacheIdentity(**payload)


@pytest.mark.parametrize(
    "field_path, unsafe_value, match",
    [
        (
            ("parser_settings", "source_name"),
            "client-donor-source.pdf",
            "donor filenames",
        ),
        (
            ("parser_settings", "source_name"),
            "client-donor-source.pdf-v1",
            "donor filenames",
        ),
        (
            ("parser_settings", "source_name"),
            "client-donor-source.pdf.backup",
            "donor filenames",
        ),
        (
            ("runtime_options", "source_display_label"),
            "/private/client/source.pdf",
            "local source paths",
        ),
        (
            ("runtime_options", "source_path"),
            "tmp/client-donor-source.pdf",
            "relative source paths",
        ),
        (
            ("runtime_options", "source_hash_file"),
            ("a" * 64) + ".jsonl",
            "source hashes as filenames",
        ),
        (
            ("doc_web_ref",),
            "azure://private-container/client-donor-source.pdf",
            "URI/storage paths",
        ),
        (
            ("runtime_options", "source_storage_key"),
            "s3:private-bucket-client-donor-source",
            "URI/storage paths",
        ),
        (
            ("runtime_options", "source_ref"),
            "source:private-client-donor-source",
            "URI/storage paths",
        ),
    ],
)
def test_doc_web_cache_identity_rejects_private_source_identifiers(
    field_path: tuple[str, ...], unsafe_value: str, match: str
):
    payload = _doc_web_cache_identity_example()
    target = payload
    for key in field_path[:-1]:
        target = target[key]
    target[field_path[-1]] = unsafe_value

    with pytest.raises(ValidationError, match=match):
        DocWebPreviewCacheIdentity(**payload)


@pytest.mark.parametrize(
    "field_path, unsafe_key, unsafe_value",
    [
        ((), "source_path", "/private/client-donor-source.pdf"),
        (("source_identity",), "donor_filename", "client-donor-source.pdf"),
    ],
)
def test_doc_web_cache_identity_rejects_extra_private_source_identifiers(
    field_path: tuple[str, ...], unsafe_key: str, unsafe_value: str
):
    payload = _doc_web_cache_identity_example()
    target = payload
    for key in field_path:
        target = target[key]
    target[unsafe_key] = unsafe_value

    with pytest.raises(ValidationError, match=unsafe_key):
        DocWebPreviewCacheIdentity(**payload)


def test_doc_web_preview_contract_fingerprints_require_full_sha256_hex():
    source_sha256 = "a" * 64
    with pytest.raises(ValidationError, match="preview_contract_fingerprint"):
        DocWebPreviewSelectorMap(
            source_artifact=f"sha256:{source_sha256}",
            source_sha256=source_sha256,
            preview_contract_fingerprint="sha256:not-a-hex-digest",
        )


def test_doc_web_preview_content_hint_cache_key_requires_full_sha256_hex():
    with pytest.raises(ValidationError, match="cache_key"):
        DocWebPreviewContentHint(
            status="available",
            high_level_summary="Fixture summary.",
            cache_key="sha256:not-a-hex-digest",
        )


def test_doc_web_bundle_manifest_rejects_non_bundle_local_paths():
    manifest_data = deepcopy(DOC_WEB_BUNDLE_MANIFEST_EXAMPLE)
    manifest_data["index_path"] = "/abs/index.html"
    manifest_data["entries"][0]["path"] = "/abs/chapter-010.html"
    manifest_data["provenance_path"] = "/abs/blocks.jsonl"

    with pytest.raises(ValueError):
        DocWebBundleManifest(**manifest_data)


def test_doc_web_preview_manifest_requires_portable_file_contract():
    manifest = DocWebBundleManifest(**_doc_web_preview_manifest_example())

    assert manifest.source_artifact == "sha256:" + ("a" * 64)
    assert {file.path for file in manifest.files} >= {
        "manifest.json",
        "index.html",
        "page-001.html",
        "provenance/blocks.jsonl",
        "preview_metadata.json",
        "preview_to_full_selectors.json",
        "cache/cache_identity.json",
        "cache/parsed_units.jsonl",
    }


def test_doc_web_preview_manifest_rejects_non_sha_source_artifact():
    manifest_data = _doc_web_preview_manifest_example()
    manifest_data["source_artifact"] = "s3:private-bucket-client-donor-source"

    with pytest.raises(ValueError, match="source_artifact"):
        DocWebBundleManifest(**manifest_data)


def test_doc_web_preview_manifest_rejects_storage_key_file_paths():
    manifest_data = _doc_web_preview_manifest_example()
    manifest_data["files"][0]["path"] = "s3:private-bucket/manifest.json"

    with pytest.raises(ValidationError, match="storage-key"):
        DocWebBundleManifest(**manifest_data)


def test_doc_web_preview_manifest_rejects_non_portable_run_id():
    manifest_data = _doc_web_preview_manifest_example()
    manifest_data["run_id"] = "/private/client/secret-source.pdf"

    with pytest.raises(ValidationError, match="run_id"):
        DocWebBundleManifest(**manifest_data)


def test_doc_web_preview_manifest_rejects_source_filename_run_id():
    manifest_data = _doc_web_preview_manifest_example()
    manifest_data["run_id"] = "secret-family-source.pdf"

    with pytest.raises(ValidationError, match="run_id"):
        DocWebBundleManifest(**manifest_data)


@pytest.mark.parametrize(
    "run_id",
    ["secret-family-source.pdf-v1", "secret-family-source.pdf.backup"],
)
def test_doc_web_preview_manifest_rejects_embedded_source_filename_run_id(
    run_id: str,
):
    manifest_data = _doc_web_preview_manifest_example()
    manifest_data["run_id"] = run_id

    with pytest.raises(ValidationError, match="run_id"):
        DocWebBundleManifest(**manifest_data)


@pytest.mark.parametrize(
    "asset_root",
    [
        "",
        "/private/assets",
        "../assets",
        "assets//images",
        r"assets\images",
        "file://assets",
        "s3:private-bucket/assets",
        "C:/private/assets",
    ],
)
def test_doc_web_preview_manifest_rejects_non_portable_asset_roots(
    asset_root: str,
):
    manifest_data = _doc_web_preview_manifest_example()
    manifest_data["asset_roots"] = [asset_root]

    with pytest.raises(ValidationError, match="asset_roots"):
        DocWebBundleManifest(**manifest_data)


def test_doc_web_preview_manifest_rejects_extra_private_file_metadata():
    manifest_data = _doc_web_preview_manifest_example()
    manifest_data["files"][0]["local_source_path"] = "/private/source.pdf"

    with pytest.raises(ValidationError, match="local_source_path"):
        DocWebBundleManifest(**manifest_data)


@pytest.mark.parametrize(
    "file_path, wrong_role, match",
    [
        ("manifest.json", "asset", "manifest"),
        ("index.html", "asset", "index"),
        ("page-001.html", "asset", "entry"),
        ("provenance/blocks.jsonl", "asset", "provenance"),
        ("preview_metadata.json", "asset", "preview_metadata"),
        ("preview_to_full_selectors.json", "asset", "selector_map"),
        ("cache/cache_identity.json", "asset", "cache_identity"),
        ("cache/parsed_units.jsonl", "asset", "parsed_units"),
    ],
)
def test_doc_web_preview_manifest_rejects_required_file_role_mismatches(
    file_path: str, wrong_role: str, match: str
):
    manifest_data = _doc_web_preview_manifest_example()
    for file in manifest_data["files"]:
        if file["path"] == file_path:
            file["role"] = wrong_role
            break

    with pytest.raises(ValueError, match=match):
        DocWebBundleManifest(**manifest_data)


@pytest.mark.parametrize(
    "extra_path, role, match",
    [
        ("extra-manifest.json", "manifest", "role/path pairing"),
        ("extra-page.html", "entry", "role/path pairing"),
        ("debug/status.jsonl", "preview_status", "role/path pairing"),
        ("cache/other_identity.json", "cache_identity", "role/path pairing"),
    ],
)
def test_doc_web_preview_manifest_rejects_extra_known_roles_at_wrong_paths(
    extra_path: str, role: str, match: str
):
    manifest_data = _doc_web_preview_manifest_example()
    manifest_data["files"].append(
        {
            "path": extra_path,
            "role": role,
            "safe_to_persist": True,
            "safe_to_replay": False,
            "privacy_class": "portable",
            "required_for_replay": False,
        }
    )

    with pytest.raises(ValueError, match=match):
        DocWebBundleManifest(**manifest_data)


def test_doc_web_preview_manifest_allows_optional_preview_status_row_to_be_absent():
    manifest_data = _doc_web_preview_manifest_example()
    manifest_data["files"] = [
        file for file in manifest_data["files"] if file["path"] != "preview_status.jsonl"
    ]

    manifest = DocWebBundleManifest(**manifest_data)

    assert "preview_status.jsonl" not in {file.path for file in manifest.files}


def test_doc_web_bundle_manifest_rejects_non_contiguous_order():
    manifest_data = deepcopy(DOC_WEB_BUNDLE_MANIFEST_EXAMPLE)
    manifest_data["entries"][0]["order"] = 2
    manifest_data["entries"][1]["order"] = 3

    with pytest.raises(ValueError):
        DocWebBundleManifest(**manifest_data)


def test_doc_web_bundle_manifest_rejects_navigation_that_disagrees_with_reading_order():
    manifest_data = deepcopy(DOC_WEB_BUNDLE_MANIFEST_EXAMPLE)
    manifest_data["entries"][1]["next_entry_id"] = "chapter-010"

    with pytest.raises(ValueError):
        DocWebBundleManifest(**manifest_data)


def test_doc_web_provenance_blocks_roundtrip_via_schema_map():
    model_cls = SCHEMA_MAP["doc_web_provenance_block_v1"]
    blocks = [model_cls(**row) for row in DOC_WEB_PROVENANCE_BLOCK_EXAMPLE]

    assert all(isinstance(block, DocWebProvenanceBlock) for block in blocks)
    assert blocks[0].block_id == "blk-chapter-010-0001"
    assert blocks[1].confidence == pytest.approx(0.94)


def test_doc_web_provenance_allows_pageless_source_blocks():
    block = DocWebProvenanceBlock(**DOC_WEB_PROVENANCE_PAGELESS_BLOCK_EXAMPLE)

    assert block.source_page_number is None
    assert block.source_element_ids == ["docx-paragraph-001"]


def test_doc_web_provenance_rejects_invalid_block_id():
    with pytest.raises(ValueError):
        DocWebProvenanceBlock(
            block_id="chapter-010-0001",
            entry_id="chapter-010",
            block_kind="paragraph",
            source_page_number=28,
            source_element_ids=["el-028-001"],
        )


def test_validate_artifact_cli_accepts_json_manifest(tmp_path: Path):
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(DOC_WEB_BUNDLE_MANIFEST_EXAMPLE, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), "--schema", "doc_web_bundle_manifest_v1", "--file", str(manifest_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    assert proc.returncode == 0, proc.stdout
    assert "Validation OK" in proc.stdout


def test_validate_artifact_cli_accepts_cache_identity_json(tmp_path: Path):
    cache_identity_path = tmp_path / "cache_identity.json"
    cache_identity_path.write_text(
        json.dumps(_doc_web_cache_identity_example(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--schema",
            "doc_web_cache_identity_v1",
            "--file",
            str(cache_identity_path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    assert proc.returncode == 0, proc.stdout
    assert "Validation OK" in proc.stdout


def test_validate_artifact_cli_rejects_invalid_json_manifest(tmp_path: Path):
    manifest_path = tmp_path / "invalid-manifest.json"
    invalid_manifest = deepcopy(DOC_WEB_BUNDLE_MANIFEST_EXAMPLE)
    invalid_manifest["entries"][1]["next_entry_id"] = "chapter-010"
    manifest_path.write_text(
        json.dumps(invalid_manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), "--schema", "doc_web_bundle_manifest_v1", "--file", str(manifest_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    assert proc.returncode == 1, proc.stdout
    assert "Validation finished with 1 errors out of 1 rows." in proc.stdout


def test_validate_artifact_cli_accepts_jsonl_provenance_blocks(tmp_path: Path):
    blocks_path = tmp_path / "blocks.jsonl"
    with blocks_path.open("w", encoding="utf-8") as f:
        for row in DOC_WEB_PROVENANCE_BLOCK_EXAMPLE:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), "--schema", "doc_web_provenance_block_v1", "--file", str(blocks_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    assert proc.returncode == 0, proc.stdout
    assert "Validation OK" in proc.stdout


def test_validate_artifact_cli_accepts_pageless_jsonl_provenance_blocks(tmp_path: Path):
    blocks_path = tmp_path / "docx-blocks.jsonl"
    blocks_path.write_text(
        json.dumps(DOC_WEB_PROVENANCE_PAGELESS_BLOCK_EXAMPLE, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), "--schema", "doc_web_provenance_block_v1", "--file", str(blocks_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    assert proc.returncode == 0, proc.stdout
    assert "Validation OK" in proc.stdout


def test_dossier_handoff_pack_validates_against_frozen_contract():
    manifest = DocWebBundleManifest(**_load_json(DOSSIER_HANDOFF_DIR / "manifest.json"))
    blocks = [
        DocWebProvenanceBlock(**row)
        for row in _load_jsonl(DOSSIER_HANDOFF_DIR / "provenance" / "blocks.jsonl")
    ]

    assert manifest.document_id == "onward-to-the-unknown-hardcase-slice"
    assert manifest.reading_order == [
        "chapter-010",
        "chapter-011",
        "chapter-017",
        "chapter-022",
        "chapter-023",
    ]
    assert len(manifest.entries) == 5
    assert len(blocks) == 134


def test_dossier_handoff_pack_html_and_assets_match_manifest_and_provenance():
    manifest = _load_json(DOSSIER_HANDOFF_DIR / "manifest.json")
    blocks = _load_jsonl(DOSSIER_HANDOFF_DIR / "provenance" / "blocks.jsonl")
    blocks_by_entry = {}
    for row in blocks:
        blocks_by_entry.setdefault(row["entry_id"], []).append(row)

    for entry in manifest["entries"]:
        html_path = DOSSIER_HANDOFF_DIR / entry["path"]
        assert html_path.exists(), entry["path"]

        html_text = html_path.read_text(encoding="utf-8")
        dom_ids = set(re.findall(r'id="([^"]+)"', html_text))
        block_ids = {row["block_id"] for row in blocks_by_entry[entry["entry_id"]]}
        assert block_ids <= dom_ids

        image_refs = set(re.findall(r'src="(images/[^"]+)"', html_text))
        for image_ref in image_refs:
            assert (DOSSIER_HANDOFF_DIR / image_ref).exists(), image_ref


def test_dossier_handoff_pack_preserves_sample_citation_mappings():
    rows = {
        row["block_id"]: row
        for row in _load_jsonl(DOSSIER_HANDOFF_DIR / "provenance" / "blocks.jsonl")
    }

    assert rows["blk-chapter-010-0002"] == {
        "schema_version": "doc_web_provenance_block_v1",
        "module_id": "build_chapter_html_v1",
        "run_id": "story154-dossier-doc-web-handoff-v1",
        "created_at": rows["blk-chapter-010-0002"]["created_at"],
        "block_id": "blk-chapter-010-0002",
        "entry_id": "chapter-010",
        "block_kind": "paragraph",
        "source_page_number": 28,
        "source_element_ids": ["p028-b2"],
        "source_printed_page_number": 19,
        "source_printed_page_label": "19",
        "text_quote": "Although weddings are meant to be happy occasions, Arthur's marriage to Lucille Lambert on May 29, 1906 in Jackfish Lake, Saskatchewan was marred by the fact that Arthur was very ill and had recieved the Last Sacrament of the Roman Catholic Faith. However, he recovered and raised a family of fifteen.",
    }
    assert rows["blk-chapter-011-0006"]["block_kind"] == "figure"
    assert rows["blk-chapter-011-0006"]["source_element_ids"] == ["p038-b6"]
    assert rows["blk-chapter-017-0003"]["source_page_number"] == 78
    assert rows["blk-chapter-017-0003"]["source_printed_page_number"] == 69
    assert rows["blk-chapter-022-0004"]["source_element_ids"] == ["p108-b4"]
    assert rows["blk-chapter-023-0001"]["text_quote"] == "ANTOINE L'HEUREUX"
