from __future__ import annotations

from typing import Any

from doc_web.preview_support import (
    PARSED_UNITS_PATH,
    SELECTOR_MAP_PATH,
    stable_fingerprint,
)


def _identity_stable_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    volatile_keys = {"created_at", "run_id"}
    return [
        {key: value for key, value in row.items() if key not in volatile_keys}
        for row in rows
    ]


def _identity_stable_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    display_keys = {"title", "printed_pages"}
    return [
        {key: value for key, value in entry.items() if key not in display_keys}
        for entry in entries
    ]


def bundle_fingerprint(
    *,
    manifest: dict[str, Any],
    provenance_rows: list[dict[str, Any]],
    selector_mappings: list[dict[str, Any]],
    parsed_units: list[dict[str, Any]],
) -> str:
    return stable_fingerprint(
        {
            "schema_version": manifest.get("schema_version"),
            "document_id": manifest.get("document_id"),
            "entries": _identity_stable_entries(manifest.get("entries", [])),
            "reading_order": manifest.get("reading_order"),
            "provenance_rows": _identity_stable_rows(provenance_rows),
            "selector_mappings": selector_mappings,
            "parsed_units": parsed_units,
        }
    )


def build_cache_identity(
    *,
    source_ref: str,
    source_sha256: str,
    facts: dict[str, Any],
    doc_web_version: str,
    doc_web_ref: str,
    parser_settings: dict[str, Any],
    runtime_options: dict[str, Any],
    preview_contract_fingerprint: str,
    bundle_fingerprint_value: str,
    content_hint_identity: dict[str, Any],
) -> dict[str, Any]:
    source_unit_count = (
        facts.get("page_count")
        if facts.get("page_count") is not None
        else facts.get("image_count")
    )
    cache_identity = {
        "identity_schema_version": "doc_web_cache_identity_v1",
        "source_identity": {
            "source_ref": source_ref,
            "source_sha256": source_sha256,
            "source_hash_algorithm": "sha256",
            "source_hash_origin": "doc-web-computed",
            "page_count": facts.get("page_count"),
            "source_unit_count": source_unit_count,
        },
        "doc_web_version": doc_web_version,
        "doc_web_ref": doc_web_ref,
        "parser_settings": parser_settings,
        "runtime_options": runtime_options,
        "preview_contract_fingerprint": preview_contract_fingerprint,
        "bundle_fingerprint": bundle_fingerprint_value,
        "reusable_artifacts": {
            "parsed_units": PARSED_UNITS_PATH,
            "selector_map": SELECTOR_MAP_PATH,
        },
        "content_hint": content_hint_identity,
    }
    cache_identity["identity_fingerprint"] = stable_fingerprint(
        {
            "source_identity": cache_identity["source_identity"],
            "doc_web_version": cache_identity["doc_web_version"],
            "doc_web_ref": cache_identity["doc_web_ref"],
            "parser_settings": cache_identity["parser_settings"],
            "runtime_options": cache_identity["runtime_options"],
            "preview_contract_fingerprint": cache_identity[
                "preview_contract_fingerprint"
            ],
            "bundle_fingerprint": cache_identity["bundle_fingerprint"],
            "content_hint": cache_identity["content_hint"],
        }
    )
    return cache_identity
