# Dossier `doc-web` Handoff Pack v1

This directory is the first committed Dossier contract-test pack for `doc-web`.

## Source Lineage

- Derived from the real Story 153 emitted `doc-web` bundle output and then
  narrowed into a committed consumer fixture pack for this repo
- Narrowed to the reviewed hard-case chapters used in the Onward genealogy HTML
  slice:
  - `chapter-010.html`
  - `chapter-011.html`
  - `chapter-017.html`
  - `chapter-022.html`
  - `chapter-023.html`

## Why This Pack Exists

The older reviewed slice under `reviewed_html_slice/` is a trusted quality golden,
but its `manifest.json` is review metadata rather than the final
`doc_web_bundle_manifest_v1` consumer surface. This pack closes that gap by
committing the actual runtime boundary Dossier should validate.

## Included Contract Surfaces

- `manifest.json`
- `index.html`
- five chapter HTML files with real `blk-*` DOM anchors
- `images/` with all image assets referenced by those chapters
- `provenance/blocks.jsonl`

## Expected Dossier Assertions

- `manifest.json` validates as `doc_web_bundle_manifest_v1`
- `provenance/blocks.jsonl` validates as `doc_web_provenance_block_v1`
- every `entries[].path` exists
- every provenance `block_id` exists in the referenced HTML
- every `images/...` reference resolves bundle-locally
- representative citation rows remain stable for:
  - `blk-chapter-010-0002`
  - `blk-chapter-011-0006`
  - `blk-chapter-022-0004`

## Intentional Narrowness

This is a compact hard-case compatibility pack, not a full archived run dump.
Navigation has been rewired to this subset so the bundle stays self-contained for
consumer tests.
