---
type: synthesis-report
topic: "doclingdocument-doc-web-boundary"
synthesis-model: ""
source-reports:
  - "docs/scout/scout-011-external-document-ingestion-systems.md"
  - "local-pilot-scorecard.md"
  - "local-pilot-findings.md"
  - "onward-tuning-matrix.md"
  - "onward-tuning-findings.md"
  - "openai-research-report.md"
  - "gemini-research-report.md"
  - "opus-research-stub.md"
  - "xai-research-stub.md"
synthesized: ""
---

# Final Synthesis

## Recommended Choice

Pursue `hybrid` first.

Current evidence says `Docling` is strong enough to justify ownership as an
upstream intake substrate, but not yet strong enough to replace the current
`doc-web` Dossier boundary with its native exports.

## Ownership Ladder

The recommended path is tiered, not flat:

1. Tier 1: official `Docling` surfaces only
   - stock configuration
   - built-in OCR / VLM / export options
   - documented plugin / serializer / extension seams
   - ideal because it keeps future `Docling` upgrades cheap: pull a new
     version, rerun a narrow smoke/parity lane, and promote if it still passes
2. Tier 2: upstream-compatible deeper ownership
   - thin repo-owned repair or adaptation layer
   - upstream PRs
   - replayable local patches that do not require a permanent fork
   - only justified when Tier 1 is falsified with measured quality or
     operational evidence
3. Tier 3: source-divergent ownership
   - maintained fork
   - invasive long-lived patch stack
   - only justified when lower tiers cannot honestly reach the bar

## Why

- The local pilot shows real value on hard documents without repo-specific
  tuning: the image-only Onward slice produced readable narrative extraction, a
  page-aware native IR, `20` recovered tables, and `7` detected pictures.
- Story 159's stock-tuning sweep narrows one earlier concern: image export is
  largely a configuration issue. When page/picture image generation is enabled,
  `Docling` emits HTML `<img>` tags and saves page, picture, and table images.
- Story 159's thin hybrid proof is the first direct evidence that the remaining
  Onward gap is repairable without recreating the whole runtime. On top of the
  `baseline-images` substrate, a two-page OCR rescue removed the flattened
  Arthur pre-table onset and the page-4 `ALICE'S FAMILY Barbara Hodges` leak
  while preserving the surrounding genealogy-table run.
- The same pilot and tuning sweep still show concrete native-surface gaps against the accepted
  `doc-web` bar:
  - no stable block anchors in HTML;
  - image export exists, but not yet in a Storybook-specific citation/bundle layout;
  - repeated-structure subgroup headings leaking into table cells.
- The OCR-backed Arthur follow-up and later stock-tuning sweep did not rescue
  the main genealogy-table onset, which weakens the claim that trivial OCR or
  table-option changes alone make native `DoclingDocument` immediately
  Dossier-ready.

## Runner-Up

Keep `doc-web` as the incumbent boundary while treating `Docling` as a benchmark
and upstream research substrate.

Choose this if the next hybrid proof shows that preserving provenance, stable
anchors, and image export would force an adapter that is effectively as large as
the current `doc-web` surface.

## Avoid

Do not recommend native `DoclingDocument` replacement today.

The current pilot does not justify superseding ADR-002 because the built-in
consumer surface still misses contract features Dossier already relies on.

## Next Step

The direct source-image Tier 1 closure pass is now negative. In this local
environment:

- raw source-image `image-default` and `image-ocrmac` fail on the actual Onward
  page scale before usable output is emitted;
- the surviving source-image official VLM candidate scores `15.0 / 100`, which
  is worse than the already-poor stock PDF baseline and far below the current
  `89.0 / 100` hybrid control.

That means the default next move is now Tier 2, not another broad Tier 1
probe. Only reopen Tier 1 if a concrete documented `Docling` extension seam
appears that is materially different from the seams already tested.

The next question is therefore whether the now-proven hybrid shape generalizes
cleanly:

- can the page-local repair-target selection be derived from inspectable signals
  instead of being hard-coded to Arthur pages 3-4;
- can the same repair path preserve provenance/citation requirements cleanly;
- can the adapter stay thin once stable anchors and Storybook-facing packaging
  are added.

If that generalized path stays thin, `hybrid` becomes the serious replacement
path. If it starts recreating most of `doc-web`, keep `doc-web` as the accepted
boundary and record `Docling` as a strong upstream benchmark rather than a
replacement.
