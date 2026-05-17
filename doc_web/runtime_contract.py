import hashlib
import json
from typing import Any, Dict

from schemas import (
    DocWebBundleManifest,
    DocWebPreviewCacheIdentity,
    DocWebPreviewMetadata,
    DocWebPreviewSelectorMap,
    DocWebProvenanceBlock,
)

from doc_web import __version__


PACKAGE_NAME = "doc-web"
CONTRACT_NAME = "doc-web"
CONTRACT_VERSION = "1"
REQUIRES_PYTHON = ">=3.11"
FINGERPRINT_ALGORITHM = "sha256"
COMPATIBILITY_POLICY = {
    "contract_version_role": "coarse-runtime-boundary-family",
    "consumer_gate_fields": [
        "schema_fingerprint",
        "supported_bundle_schema_versions",
        "preview_contract_fingerprint",
        "supported_preview_schema_versions",
    ],
}
PREVIEW_STATUS_STAGES = [
    "accepted",
    "preparing_pages",
    "detecting_text_or_ocr_need",
    "reading_sample",
    "building_preview_html",
    "preview_ready",
    "continuing_full_processing",
    "ready",
    "failed",
]
PREVIEW_COVERAGE_STATES = ["complete", "sampled", "partial", "deferred"]
PREVIEW_CONTENT_HINT_MODES = ["auto", "ai", "deterministic"]
PREVIEW_CACHE_IDENTITY_SCHEMA_VERSION = "doc_web_cache_identity_v1"


def _schema_fingerprint() -> str:
    payload = {
        "contract_name": CONTRACT_NAME,
        "contract_version": CONTRACT_VERSION,
        "manifest_schema": DocWebBundleManifest.model_json_schema(mode="validation"),
        "provenance_schema": DocWebProvenanceBlock.model_json_schema(mode="validation"),
        "bundle_layout": {
            "index_path": "index.html",
            "provenance_path": "provenance/blocks.jsonl",
            "entry_path_pattern": "{entry_id}.html",
        },
    }
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return f"{FINGERPRINT_ALGORITHM}:{hashlib.sha256(encoded).hexdigest()}"


def _preview_contract_fingerprint() -> str:
    payload = {
        "contract_name": CONTRACT_NAME,
        "contract_version": CONTRACT_VERSION,
        "preview_metadata_schema": DocWebPreviewMetadata.model_json_schema(
            mode="validation"
        ),
        "preview_selector_map_schema": DocWebPreviewSelectorMap.model_json_schema(
            mode="validation"
        ),
        "preview_cache_identity_schema": DocWebPreviewCacheIdentity.model_json_schema(
            mode="validation"
        ),
        "preview_layout": {
            "metadata_path": "preview_metadata.json",
            "status_path": "preview_status.jsonl",
            "selector_map_path": "preview_to_full_selectors.json",
            "cache_identity_path": "cache/cache_identity.json",
            "parsed_units_path": "cache/parsed_units.jsonl",
        },
        "preview_status_stages": PREVIEW_STATUS_STAGES,
        "preview_coverage_states": PREVIEW_COVERAGE_STATES,
        "preview_content_hint_modes": PREVIEW_CONTENT_HINT_MODES,
    }
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return f"{FINGERPRINT_ALGORITHM}:{hashlib.sha256(encoded).hexdigest()}"


def build_runtime_contract() -> Dict[str, Any]:
    manifest_schema_version = DocWebBundleManifest.model_fields[
        "schema_version"
    ].default
    provenance_schema_version = DocWebProvenanceBlock.model_fields[
        "schema_version"
    ].default
    preview_metadata_schema_version = DocWebPreviewMetadata.model_fields[
        "schema_version"
    ].default
    preview_selector_map_schema_version = DocWebPreviewSelectorMap.model_fields[
        "schema_version"
    ].default
    return {
        "contract_name": CONTRACT_NAME,
        "contract_version": CONTRACT_VERSION,
        "package_name": PACKAGE_NAME,
        "runtime_version": __version__,
        "requires_python": REQUIRES_PYTHON,
        "schema_fingerprint": _schema_fingerprint(),
        "preview_contract_fingerprint": _preview_contract_fingerprint(),
        "supported_bundle_schema_versions": {
            "manifest": manifest_schema_version,
            "provenance": provenance_schema_version,
        },
        "supported_preview_schema_versions": {
            "metadata": preview_metadata_schema_version,
            "selector_map": preview_selector_map_schema_version,
            "cache_identity": PREVIEW_CACHE_IDENTITY_SCHEMA_VERSION,
        },
        "compatibility_policy": COMPATIBILITY_POLICY,
        "bundle_layout": {
            "index_path": "index.html",
            "provenance_path": "provenance/blocks.jsonl",
            "entry_path_pattern": "{entry_id}.html",
            "default_asset_roots": ["images"],
        },
        "preview_layout": {
            "metadata_path": "preview_metadata.json",
            "status_path": "preview_status.jsonl",
            "selector_map_path": "preview_to_full_selectors.json",
            "cache_identity_path": "cache/cache_identity.json",
            "parsed_units_path": "cache/parsed_units.jsonl",
        },
        "preview_status_stages": PREVIEW_STATUS_STAGES,
        "preview_coverage_states": PREVIEW_COVERAGE_STATES,
        "preview_content_hint_modes": PREVIEW_CONTENT_HINT_MODES,
    }
