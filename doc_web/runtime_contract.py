import hashlib
import json
from typing import Any, Dict

from schemas import DocWebBundleManifest, DocWebProvenanceBlock

from doc_web import __version__


PACKAGE_NAME = "doc-web"
CONTRACT_NAME = "doc-web"
CONTRACT_VERSION = "1"
REQUIRES_PYTHON = ">=3.11"
FINGERPRINT_ALGORITHM = "sha256"


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
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"{FINGERPRINT_ALGORITHM}:{hashlib.sha256(encoded).hexdigest()}"


def build_runtime_contract() -> Dict[str, Any]:
    manifest_schema_version = DocWebBundleManifest.model_fields["schema_version"].default
    provenance_schema_version = DocWebProvenanceBlock.model_fields["schema_version"].default
    return {
        "contract_name": CONTRACT_NAME,
        "contract_version": CONTRACT_VERSION,
        "package_name": PACKAGE_NAME,
        "runtime_version": __version__,
        "requires_python": REQUIRES_PYTHON,
        "schema_fingerprint": _schema_fingerprint(),
        "supported_bundle_schema_versions": {
            "manifest": manifest_schema_version,
            "provenance": provenance_schema_version,
        },
        "bundle_layout": {
            "index_path": "index.html",
            "provenance_path": "provenance/blocks.jsonl",
            "entry_path_pattern": "{entry_id}.html",
            "default_asset_roots": ["images"],
        },
    }
