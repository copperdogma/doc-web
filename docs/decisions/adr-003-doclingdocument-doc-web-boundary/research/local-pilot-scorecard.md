---
type: local-pilot-scorecard
topic: "doclingdocument-doc-web-boundary"
created: "2026-03-20"
pilot-run-id: "story157-docling-pilot-r1"
---

# Local Pilot Corpus And Scorecard

This scorecard defines the minimum local evidence required to judge whether
`DoclingDocument` can keep, thin, or replace the current `doc-web` boundary.

## Corpus

- Control PDF: [`testdata/tbotb-mini.pdf`](/Users/cam/.codex/worktrees/eb88/doc-web/testdata/tbotb-mini.pdf)
  Purpose: verify `Docling` install, CLI/API behavior, and export surfaces on a
  small born-digital baseline before interpreting hard-case failures.
- Onward full image-only PDF: `/Users/cam/Documents/Projects/Onward to the Unknown Book Scan/Optimized Image Output.pdf`
  Purpose: prove `Docling` against a real scanned source without an embedded OCR
  text layer.
- Onward hard-case slice image-only PDF: [onward-hardcase-slice-imageonly.pdf](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story157-docling-pilot-r1/input/onward-hardcase-slice-imageonly.pdf)
  Purpose: match the incumbent Dossier hard-case handoff slice exactly.
- Onward Arthur split PDF: `/Users/cam/Documents/Projects/Onward to the Unknown Book Scan/Split Book/05 ARTHUR L'HEUREUX.pdf`
  Purpose: narrower repeated-structure follow-up if the image-only slice needs
  chapter-level diagnosis.
- Onward page-image directory: `/Users/cam/Documents/Projects/Onward to the Unknown Book Scan/Processed Pages`
  Purpose: direct image-directory fallback if the PDF path hides an issue.

The run-local corpus manifest is at [source_manifest.json](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story157-docling-pilot-r1/input/source_manifest.json).

## Incumbent Baseline

- Current Dossier-facing hard-case pack: [dossier-doc-web-handoff-v1](/Users/cam/.codex/worktrees/eb88/doc-web/benchmarks/golden/onward/dossier-doc-web-handoff-v1)
- Current hard-case source page ranges: `28-47`, `78-85`, `108-119`
- Representative incumbent provenance anchors:
  - `blk-chapter-010-0002`
  - `blk-chapter-011-0006`
  - `blk-chapter-022-0004`

## Questions To Answer

1. Can stock `Docling` emit a native document representation that preserves
   source-to-output traceability well enough for Dossier citations and "open
   original" behavior?
2. Is reading order on the Onward hard-case slice at least coherent enough that
   a thin adapter could preserve the narrative and table sequence without
   recreating `doc-web` complexity?
3. Are tables and repeated genealogical structures materially usable, or does
   stock `Docling` collapse them in ways that would force major custom repair?
4. Does `Docling` lower total system complexity relative to the current
   `doc-web` boundary after accounting for dependency weight, installation
   burden, and required wrapper code?

## Scoring Dimensions

- `P0 Traceability`
  Pass if the native output exposes page-level provenance and enough local item
  identity to support citation back to source pages or page elements.
  Fail if provenance is missing, too coarse, or only reconstructable through a
  second opaque pipeline.
- `P1 Reading Order`
  Pass if the hard-case slice reads in a human-correct order through narrative,
  figures, and genealogy sections.
  Fail if section order, table order, or figure placement is obviously broken.
- `P2 Repeated-Structure Fidelity`
  Pass if genealogy tables remain grouped and legible enough that a human can
  follow the family structure without major reconstruction.
  Fail if rows collapse into prose soup, duplicate headings explode, or family
  grouping is materially lost.
- `P3 Export Fit`
  Pass if the native `DoclingDocument` plus built-in exports are already close
  to a Dossier-facing intake contract.
  Fail if a wrapper would need to recreate large portions of `doc-web`.
- `P4 Operational Burden`
  Pass if version pinning and runtime dependencies are acceptable for the value
  gained.
  Fail if the install/runtime model is so heavy or brittle that the replacement
  only moves complexity around.

## Decision Thresholds

- `Replace`
  Requires passing `P0`, `P1`, and `P3`, with no catastrophic failure on `P2`.
  `P4` must be acceptable enough that Dossier can reasonably own the native
  intake dependency.
- `Hybrid`
  Requires passing `P0` and substantial progress on `P1` and `P2`, but with a
  clear thin-adapter story that does not recreate `doc-web`.
- `Keep doc-web`
  Chosen if stock `Docling` fails `P0`, or if fixing `P1`/`P2` would obviously
  require a heavy wrapper that preserves most current `doc-web` complexity.

## Manual Inspection Checklist

- Open the emitted native JSON / `DoclingDocument` artifact and confirm the top
  level contains page-aware structure, not just flattened markdown text.
- Open at least one built-in export surface for the control PDF and the Onward
  hard-case slice.
- Search the Onward artifact for `ARTHUR L'HEUREUX` and inspect the immediately
  surrounding blocks/items.
- Inspect at least one repeated-structure region from the `78-85` and
  `108-119` ranges because those are current incumbent hard cases.
- Record exact artifact paths and representative snippets in Story 158 and
  ADR-003 before making any keep / hybrid / replace claim.
