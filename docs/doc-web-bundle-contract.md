# `doc-web` Bundle Contract v1

**Status:** first formal contract frozen by Story 152  
**Decision source:** `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`  
**Golden baseline:** `benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/`

## Purpose

This document defines the first formal `doc-web` runtime boundary.

It does two things:

1. freezes the structural website bundle layout that downstream consumers can rely on; and
2. freezes the paragraph-level provenance sidecar contract required for citation and open-original behavior.

The contract intentionally keeps the existing flat HTML bundle shape where it already
works, and adds the missing machine-readable manifest and provenance sidecar rather
than inventing a completely different output layout.

## Scope

Included in the v1 contract:

- `index.html` as the human-readable entry point
- `chapter-*.html` and `page-*.html` content documents at bundle root
- machine-readable `manifest.json` as the canonical reading-order source of truth
- asset directories such as `images/`
- `provenance/blocks.jsonl` for paragraph/block-level source mapping

Explicitly out of scope for v1:

- presentation theming beyond minimal structural HTML
- Dossier-specific ingestion transforms
- sentence-level or token-level provenance by default
- codex-forge-internal planning metadata as part of the public runtime boundary

## Preview Mode Extension

Preview mode is a latency-bound extension of this bundle model, not a separate
JSON-only contract. A preview bundle still writes the normal required files:

- `manifest.json`
- `index.html`
- semantic HTML entries at bundle root
- `provenance/blocks.jsonl`

Preview mode adds these sidecars:

- `preview_metadata.json` (`doc_web_preview_metadata_v1`)
- `preview_status.jsonl`
- `preview_to_full_selectors.json` (`doc_web_preview_selector_map_v1`)
- `cache/cache_identity.json`
- `cache/parsed_units.jsonl`

Rules:

- preview HTML is explicitly non-final
- `coverage_state` must be one of `complete`, `sampled`, `partial`, or `deferred`
- scan-heavy inputs and image directories with no fast text layer should report
  deferred text/OCR need instead of inventing preview text
- preview source identity includes source SHA-256, `doc-web` version, parser
  settings, runtime options, and preview contract fingerprint
- `preview_metadata.json` may include a non-final `content_hint` with a title
  guess, document-kind hint, high-level summary, evidence snippets, quality
  status, and warnings; consumers must not treat it as extracted graph facts
- content hints may be produced by a bounded cheap-model pass over sampled text
  (`auto` / `ai`) or by deterministic fallback; `cache/cache_identity.json`
  records the mode, model, prompt version, sample hash, and cache key
- `cache/parsed_units.jsonl` is the reusable parsed-text cache payload for
  later compatible full processing jobs; consumers must gate reuse on
  `cache/cache_identity.json`
- `manifest.json` declares bundle-local `files` rows so consumers can persist
  only `safe_to_persist=true` / `privacy_class=portable` paths; safe file paths
  are relative to the bundle root and require no local source path to replay
- portable preview manifests use a privacy-safe `source_artifact` reference
  (`sha256:<source-hash>`), not a local filename/path, temp path, URI, or
  storage key
- preview/full selector continuity is represented by preserved block IDs when
  possible and by `preview_to_full_selectors.json` when a later full run needs
  mapping
- cache identity is privacy-safe: it uses a source hash/reference, page or unit
  count, `doc-web` version/ref, parser/OCR settings, runtime options, preview
  contract fingerprint, bundle fingerprint, content-hint identity/cache key,
  and an identity fingerprint, not a donor filename, local filename/path,
  storage key, or source hash used as a filename
- `preview_metadata.json.cache_identity` validates the same
  `doc_web_cache_identity_v1` shape as `cache/cache_identity.json`; source
  path/name data is allowed only in rewriteable display-label fields and must
  not participate in replay identity

## Compatibility Signaling

The bundle/provenance contract is exposed to downstream consumers through
`doc-web contract --json`.

Compatibility policy for that payload:

- `contract_version` is the coarse runtime-boundary family marker for `doc-web`
  v1.
- `supported_bundle_schema_versions` and `schema_fingerprint` are the
  consumer-facing compatibility gates for the manifest/provenance contract.
- `supported_preview_schema_versions` and `preview_contract_fingerprint` are the
  consumer-facing gates for preview metadata and selector continuity.
- `preview_status_stages` and `preview_coverage_states` enumerate the supported
  operator-facing preview vocabulary.
- A stable `contract_version` does not guarantee a stable schema fingerprint.
  Downstream adopters must treat fingerprint or supported-schema drift as a
  review-and-accept boundary even when `contract_version` is unchanged.

## Bundle Layout

The first contract keeps a flat bundle root:

```text
bundle/
  manifest.json
  index.html
  chapter-001.html
  chapter-002.html
  page-001.html
  images/
    ...
  provenance/
    blocks.jsonl
```

Rules:

- `manifest.json` is the source of truth for reading order.
- Inline prev/next navigation in HTML is retained, but it is derived from `manifest.json` and is not the canonical contract source.
- Paths in the manifest are relative to the bundle root.
- Content document ids are the file stem without `.html` (`chapter-010`, `page-002`).

## Machine-Readable Schemas

### `doc_web_bundle_manifest_v1`

Serialized as `manifest.json`.

Required top-level fields:

- `schema_version`
- `document_id`
- `title`
- `source_artifact`
- `index_path`
- `entries`
- `reading_order`
- `provenance_path`
- `files` for preview bundles and whenever a bundle is intended to be persisted
  or replayed as a portable snapshot

Required per-entry fields:

- `entry_id`
- `kind` (`chapter` or `page`)
- `title`
- `path`
- `order`

Optional per-entry fields:

- `prev_entry_id`
- `next_entry_id`
- `source_pages`
- `printed_pages`
- `printed_page_start`
- `printed_page_end`

Contract rules:

- `reading_order` must list every entry exactly once in content order.
- `entry_id` must match the HTML filename stem.
- `path` must point to a content HTML file.
- `index_path` must point to an HTML file at bundle root.
- `provenance_path` must point to a JSONL sidecar.
- when `files` is present, `source_artifact` must be a privacy-safe
  `sha256:<source-hash>` reference rather than a source path, source filename,
  URI, or storage key because `manifest.json` is itself replay-required.
- when `run_id` is present in portable preview files, it must be a short
  portable identifier (`A-Z`, `a-z`, `0-9`, `_`, `.`, `-`) rather than a path,
  URI/storage ref, or source-derived filename.
- preview manifests (`module_id=doc_web_preview_v1`) must include `files`; they
  cannot omit the file contract to bypass portable replay checks.
- file rows must use non-empty POSIX bundle-relative paths; URI/storage keys,
  drive-prefixed paths, absolute paths, backslashes, and parent traversal are
  invalid in the portable contract.
- `asset_roots`, when present, must also use non-empty POSIX bundle-relative
  paths; URI/storage keys, drive-prefixed paths, absolute paths, backslashes,
  empty entries, and parent traversal are invalid.
- file rows marked safe to persist/replay must use `privacy_class=portable`;
  debug, private, and cache-local files must either be absent from the portable
  list or explicitly marked unsafe.
- rows with `role=debug`, `role=private`, or `role=cache_local` must use the
  matching non-portable `privacy_class` and must not be marked safe to persist,
  safe to replay, or required for replay.
- `required_for_replay=true` means the file is both `safe_to_persist=true` and
  `safe_to_replay=true`.
- when `files` is present, the replay-required core rows must include
  `manifest.json`, `index_path`, `provenance_path`, and every `entries[].path`;
  each of those rows must be portable, safe to persist, safe to replay, and
  marked `required_for_replay=true`.
- preview bundles (`module_id=doc_web_preview_v1`) and manifests containing any
  preview file rows must also include replay-required rows for
  `preview_metadata.json`, `preview_to_full_selectors.json`,
  `cache/cache_identity.json`, and `cache/parsed_units.jsonl`.

Required per-file fields when `files` is present:

- `path`
- `role`
- `safe_to_persist`
- `safe_to_replay`
- `privacy_class`
- `required_for_replay`

### `doc_web_cache_identity_v1`

Serialized as `cache/cache_identity.json` and embedded in
`preview_metadata.json.cache_identity`.

Required top-level fields:

- `identity_schema_version`
- `source_identity`
- `doc_web_version`
- `doc_web_ref`
- `parser_settings`
- `runtime_options`
- `preview_contract_fingerprint`
- `bundle_fingerprint`
- `reusable_artifacts`
- `content_hint`
- `identity_fingerprint`

Contract rules:

- `source_identity.source_ref` must be `sha256:<source-hash>` and must match
  `source_identity.source_sha256`
- `source_identity` records the hash algorithm/origin and page or unit count
  when known
- source names, donor filenames, source-hash filenames, local paths, temp
  paths, URIs, and storage keys must not appear in identity fields; source
  path/name data is allowed only as a rewriteable display label such as
  `source_display_label`
- `reusable_artifacts.parsed_units` and `reusable_artifacts.selector_map` are
  non-empty POSIX bundle-relative paths
- `preview_contract_fingerprint`, `bundle_fingerprint`, content-hint cache keys,
  and `identity_fingerprint` use `sha256:<hex>` values
- `identity_fingerprint` is the stable replay gate over source identity,
  runtime/parser options, preview contract fingerprint, bundle fingerprint, and
  content-hint identity; validation recomputes it and display labels must not
  change it
- colon-form content-hint model IDs are allowed only in the content-hint model
  fields; colon-form source/storage refs remain invalid elsewhere

### `doc_web_provenance_block_v1`

Serialized as `provenance/blocks.jsonl`, one row per HTML block.

The v1 default citation unit is paragraph-level, but the schema also permits other
structural block kinds such as headings, figures, tables, captions, and list items.

Required fields:

- `schema_version`
- `block_id`
- `entry_id`
- `block_kind`
- `source_element_ids`

Optional fields:

- `source_page_number`
- `source_printed_page_number`
- `source_printed_page_label`
- `source_bbox`
- `confidence`
- `text_quote`

### Stable Block ID Format

The HTML block id and sidecar `block_id` use the same value:

```text
blk-<entry-id>-<4-digit ordinal>
```

Examples:

- `blk-chapter-010-0001`
- `blk-page-002-0003`

Rules:

- the `entry_id` segment must match the content document id
- the ordinal is 1-based within that content document
- the id must be stable across rebuilds that preserve the same block order

## Minimum Provenance Required for Citation / Open-Original

Required in v1:

- bundle-level `source_artifact` in `manifest.json`
- block-level `entry_id`
- block-level `source_element_ids`

Optional but recommended when available:

- `source_page_number` for page-native sources such as PDFs and image directories
- `source_printed_page_number` for user-facing labels
- `source_bbox` to highlight the exact region on open-original
- `confidence` for downstream ranking or audit surfaces
- `text_quote` for debug and review workflows

Why this split:

- page-level open-original is possible when `source_page_number` is available
- pageless sources such as DOCX still satisfy the contract via stable block anchors in `source_element_ids`
- region highlighting improves the experience, but Story 152 does not force fake
  coordinates where the current emitter does not yet produce them

## Current Codex-Forge Surface Mapping

### Files and Directories

| Current surface | Disposition | v1 contract mapping | Notes |
|---|---|---|---|
| `output/html/index.html` | kept | `index_path` / `index.html` | Human entry point remains part of the contract |
| `output/html/chapter-*.html` | kept | `entries[].path` with `kind=chapter` | Flat root layout preserved |
| `output/html/page-*.html` | kept | `entries[].path` with `kind=page` | Fallback/frontmatter pages stay first-class |
| `output/html/images/` | kept | `asset_roots` | Assets remain bundle-local |
| inline prev/next/index nav | kept, derived | derived from `reading_order` | Retained in HTML, but manifest is canonical |
| `chapters_manifest.jsonl` / `chapter_html_manifest_v1` | superseded transitional surface | `manifest.json` + `doc_web_bundle_manifest_v1` | Current codex-forge build artifact remains useful for migration/tests, but is not the final runtime boundary |
| block provenance in HTML | missing | `provenance/blocks.jsonl` + block DOM ids | Story 153 should emit this |

### Current Manifest Field Mapping

| `chapter_html_manifest_v1` field | v1 status | v1 contract field | Notes |
|---|---|---|---|
| `title` | kept | `entries[].title` | unchanged meaning |
| `kind` | kept | `entries[].kind` | unchanged meaning |
| `file` | renamed | `entries[].path` | relative bundle path in final contract |
| `chapter_index` | superseded | `entries[].order` | final contract uses content order rather than chapter-only numbering |
| `page_start` | renamed | `entries[].printed_page_start` | printed/document-facing page coverage |
| `page_end` | renamed | `entries[].printed_page_end` | printed/document-facing page coverage |
| `source_pages` | kept | `entries[].source_pages` | upstream source page coverage |
| `source_printed_pages` | renamed | `entries[].printed_pages` | list form remains useful |
| `source_portion_title` | superseded | not in public v1 bundle contract | codex-forge build-local provenance only |
| `source_portion_page_start` | superseded | not in public v1 bundle contract | codex-forge build-local provenance only |
| `source_portion_titles` | superseded | not in public v1 bundle contract | codex-forge build-local provenance only |
| `source_portion_page_starts` | superseded | not in public v1 bundle contract | codex-forge build-local provenance only |

## Golden Example

The initial contract golden is the committed reviewed Onward slice at:

- `benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/manifest.json`
- `benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/chapters_manifest_regression.jsonl`
- reviewed chapter HTML files in the same directory

What the golden proves today:

- the flat HTML bundle shape is real
- chapter/page reading order and coverage can be formalized
- `chapter_html_manifest_v1` can now be validated explicitly as a transitional surface

What it does not yet prove:

- real emitted block ids in HTML
- real emitted `provenance/blocks.jsonl`

Those missing pieces are intentional Story 153 work, not hand-waved contract gaps.
