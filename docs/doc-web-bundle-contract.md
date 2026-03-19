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

### `doc_web_provenance_block_v1`

Serialized as `provenance/blocks.jsonl`, one row per HTML block.

The v1 default citation unit is paragraph-level, but the schema also permits other
structural block kinds such as headings, figures, tables, captions, and list items.

Required fields:

- `schema_version`
- `block_id`
- `entry_id`
- `block_kind`
- `source_page_number`
- `source_element_ids`

Optional fields:

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
- block-level `source_page_number`
- block-level `source_element_ids`

Optional but recommended when available:

- `source_printed_page_number` for user-facing labels
- `source_bbox` to highlight the exact region on open-original
- `confidence` for downstream ranking or audit surfaces
- `text_quote` for debug and review workflows

Why this split:

- page-level open-original is possible with the required fields
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
