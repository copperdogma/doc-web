# Dossier `doc-web` Handoff v1

**Status:** first Dossier-facing handoff package published by Story 154  
**Decision source:** `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`  
**Contract source:** `docs/doc-web-bundle-contract.md`  
**Fixture pack:** `benchmarks/golden/onward/dossier-doc-web-handoff-v1/`

## Purpose

This document is the downstream handoff package for Dossier.

It translates the frozen `doc-web` runtime contract into the exact consumer-facing
expectations Dossier should implement against:

- which files are contract inputs;
- which manifest and provenance fields are mandatory;
- how Dossier should version-pin and upgrade-check `doc-web`;
- which committed fixture pack must stay green before Dossier adopts a new
  `doc-web` release.

This document is intentionally downstream-facing. Dossier should not have to
reconstruct its integration contract by reading ADR-002, Story 152, and Story 153
together.

## What Dossier Consumes

Dossier should treat the following bundle surfaces as the `doc-web` v1 contract:

- `manifest.json`
  Must validate as `doc_web_bundle_manifest_v1`.
- `index.html`
  Human-facing entry point for inspection and debugging. Not the canonical source
  of reading order.
- `chapter-*.html` and `page-*.html`
  Structural HTML content documents named by `entries[].path`.
- `images/`
  Bundle-local image assets referenced from the HTML documents.
- `provenance/blocks.jsonl`
  Must validate as `doc_web_provenance_block_v1`. This is the citation/open-original
  sidecar for block-level provenance.

Dossier should **not** treat the following as consumer contract inputs:

- `chapter_html_manifest_v1` / `chapters_manifest_regression.jsonl`
- review-pack metadata such as `onward_reviewed_html_slice_v1`
- story docs, ADR prose, or codex-forge run-registry files

## Mandatory Contract Checks

Before Dossier accepts a bundle, it should enforce all of the following:

- `manifest.json` validates as `doc_web_bundle_manifest_v1`.
- `provenance/blocks.jsonl` validates as `doc_web_provenance_block_v1`.
- `manifest.json` uses `index_path=index.html` and `provenance_path=provenance/blocks.jsonl`.
- every `entries[].path` exists as a bundle-local HTML file.
- `reading_order` and `prev_entry_id` / `next_entry_id` agree exactly.
- every provenance row `block_id` exists as a matching DOM `id` in the referenced
  HTML file.
- every provenance row contains at least:
  `block_id`, `entry_id`, `block_kind`, and `source_element_ids`.
- `source_page_number` remains required only for page-native sources that can
  honestly provide one; pageless sources such as DOCX may leave it `null`.
- every bundle-local image reference resolves inside `images/`.

Upgrade must be blocked if any of the following occur:

- `schema_version` changes away from `doc_web_bundle_manifest_v1` or
  `doc_web_provenance_block_v1` without explicit Dossier adapter work
- required files are missing
- manifest reading order drifts from HTML navigation assumptions
- `block_id` anchors disappear from the HTML
- provenance rows no longer identify source element lineage, or stop identifying
  source page for page-native sources that previously exposed it
- asset paths become absolute or escape the bundle root

## Versioning Expectations

`doc-web` release discipline for Dossier:

- Dossier pins an explicit tagged `doc-web` SemVer release.
- Every Dossier PR that upgrades the `doc-web` pin must run the committed handoff
  fixture pack.
- Major-version `doc-web` upgrades are presumed breaking until Dossier explicitly
  accepts them.
- Minor-version upgrades are acceptable only if this handoff pack still validates
  and Dossier does not need new required fields.
- Patch-version upgrades are acceptable only if this handoff pack stays green and
  no consumer-visible contract field changes.

`doc-web` now exposes the machine-readable preflight Dossier should use before a
pin bump proceeds:

```bash
python -m pip install .
doc-web contract --json
```

The payload includes:

- `runtime_version`
- `requires_python`
- `supported_bundle_schema_versions`
- `schema_fingerprint`
- `supported_preview_schema_versions`
- `preview_contract_fingerprint`
- `compatibility_policy`

Compatibility policy:

- `contract_version` is a coarse runtime-boundary family marker, not a
  stand-alone schema compatibility key.
- Treat a changed `schema_fingerprint` or changed supported schema version as an
  upgrade block until the Dossier adapter explicitly accepts the change.
- Treat a changed `preview_contract_fingerprint` or changed supported preview
  schema version as an upgrade block before using preview mode.
- Treat a changed `contract_version` as a broader boundary change, but do not
  treat an unchanged `contract_version` as proof that the manifest/provenance
  contract is unchanged.

## Preview Bundle Consumption

For real-time upload preview, Dossier and Storybook should call:

```bash
doc-web preview --input <raw-document> --out-dir <preview-bundle-dir> --json
```

The preview output is still a `doc-web` bundle. Dossier should validate the
normal bundle files plus the preview sidecars:

- `manifest.json` as `doc_web_bundle_manifest_v1`
- `provenance/blocks.jsonl` as `doc_web_provenance_block_v1`
- `preview_metadata.json` as `doc_web_preview_metadata_v1`
- `preview_to_full_selectors.json` as `doc_web_preview_selector_map_v1`
- `cache/cache_identity.json` as the reuse gate
- `cache/parsed_units.jsonl` as the reusable parsed-text cache payload

Preview metadata tells the consumer whether coverage is `complete`, `sampled`,
`partial`, or `deferred`. It may also include a non-final `content_hint` with a
title guess, document-kind hint, high-level summary, evidence snippets, and
quality warnings. Dossier may show or summarize preview text, but it must not
treat preview text or `content_hint` as extracted graph facts and must not infer
OCR quality or page counts beyond the emitted metadata. Image-directory previews
use bounded preview OCR when available; otherwise they should be shown as
OCR-deferred until a full `doc-web` processing job emits real text.
When `DOC_WEB_OPENAI_API_KEY` is configured, `doc-web` may use a bounded
cheap-model pass to turn the sampled preview text into one direct summary
sentence. Dossier should display the emitted `status`, `basis`, `warnings`, and
cache identity with the hint rather than re-summarizing raw files itself.

Dossier remains responsible for preserving the preview bundle and later choosing
whether to run a full `doc-web` processing job. A compatible full job may reuse
`cache/parsed_units.jsonl` only after matching `cache/cache_identity.json`. When
full processing regenerates content, Dossier should use
`preview_to_full_selectors.json` or preserved `entry_id` / `block_id` values to
keep citations stable.

## Recommended Pinned Consumer Shape

Mirror Storybook's pinned-Dossier model in Dossier with a repo-owned manifest
such as `doc-web-runtime.json`:

```json
{
  "repoUrl": "<doc-web git url>",
  "ref": "<exact tag or commit>",
  "packageVersion": "0.1.0",
  "pythonVersion": "3.11",
  "requiresPython": ">=3.11",
  "runtimeRoot": ".runtime/doc-web-pinned"
}
```

Recommended downstream commands:

- `doc-web:install`
- `doc-web:check-upstream`
- `doc-web:bump`

Recommended policy:

- pinned install is the default runtime source
- local checkout use is allowed only behind an explicit override for
  co-development
- use `python -m pip install .` for compatibility preflight and add
  `python -m pip install '.[driver]'` only when Dossier wants to run the
  repo-owned `driver.py` smoke lanes from a checkout
- Docker/deploy builds rebuild from a pinned source snapshot, not a fresh git
  clone at image-build time
- every bump reruns both `doc-web contract --json` and this handoff pack
  validation before merge

## First Compatibility-Test Pack

The first Dossier contract-test pack is:

- `benchmarks/golden/onward/dossier-doc-web-handoff-v1/`

What this pack is:

- a real emitted `doc_web_bundle_manifest_v1`
- a real emitted `provenance/blocks.jsonl`
- five hard-case HTML chapters with real `blk-*` DOM anchors
- seven bundle-local image assets referenced by those chapters

What this pack is not:

- a full archived run dump
- the original Story 149 review-pack metadata format
- a synthetic toy example with invented provenance

Representative citation rows in the pack:

- `blk-chapter-010-0002` -> source page `28`, printed page `19`,
  source element `p028-b2`
- `blk-chapter-011-0006` -> figure on source page `38`, printed page `29`,
  source element `p038-b6`
- `blk-chapter-022-0004` -> source page `108`, printed page `99`,
  source element `p108-b4`

## Responsibilities Split

- **codex-forge R&D**
  Discover and validate extraction patterns, quality gates, and future graduation
  candidates. It should not be Dossier's runtime dependency.
- **`doc-web` runtime**
  Own the versioned structural website bundle contract: semantic HTML, manifest,
  bundle-local assets, and provenance sidecars.
- **Dossier consumer**
  Validate the incoming bundle, pin compatible `doc-web` releases, expose the
  semantic HTML stop-point, and build downstream semantic/product behavior on top
  of the preserved bundle contract.

## First Dossier-Side Implementation Slice

The first concrete Dossier follow-up should be named:

- **Implement `doc_web_bundle_v1` intake adapter and `semantic_html` stop-point**

That slice should do exactly this:

- accept a `doc-web` bundle directory as input
- validate `manifest.json` and `provenance/blocks.jsonl`
- load `entries[].path` HTML files into a bundle-local index keyed by `entry_id`
- expose citation lookup by `{entry_id, block_id}` using `provenance/blocks.jsonl`
- preserve HTML unchanged so downstream Dossier code can stop at
  `semantic_html` before any deeper semantic normalization

## Notes for Future Packs

- This first pack is intentionally a hard-case reviewed subset, not a whole-book
  acceptance corpus.
- Future packs can broaden coverage, but they should extend this handoff contract
  rather than replace it with ad hoc fixtures.
