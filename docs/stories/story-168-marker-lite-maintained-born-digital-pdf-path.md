# Story 168 — Maintain a `Marker`-Lite Born-Digital PDF Path

**Priority**: High
**Status**: Draft
**Ideal Refs**: Requirement #1 (Ingest), Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Any format, any condition, Traceability is the Product
**Spec Refs**: spec:1 (spec:1.1, C2), spec:3 (spec:3.1, C3), spec:6, spec:7
**Build Map Refs**: Category 1 Intake & Format Routing (`partial`, C2 `climb`); Category 3 Layout & Structure Understanding (`exists`, C3 `climb`); Category 7 Graduation & Dossier Handoff (`partial`); Input Coverage row `born-digital-pdf` remains `has-fixture`
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/scout/scout-011-external-document-ingestion-systems.md`, `docs/stories/story-165-marker-breadth-comparator-born-digital-pdf.md`, `docs/stories/story-166-marker-internals-born-digital-pdf-substrate.md`, `docs/build-map.md`
**Depends On**: Story 166

## Goal

Turn Story 166's bounded `Marker`-lite spike into a maintained born-digital PDF
path only if it can stay inside the accepted `doc-web` boundary. The work
should reuse the proven native-text seam, preserve contract-grade block
provenance, and fix the specific normalization defects that still block direct
runtime adoption: inconsistent heading levels and merged choice paragraphs on
the repo-owned `tbotb-mini.pdf` lane. The result should be a maintained
optional path, not stock `Marker` adoption.

## Acceptance Criteria

- [ ] A maintained native-text path exists for `born-digital-pdf` on the active repo-owned fixture:
  - reuses the bounded `Marker`-lite internal seam rather than stock `Marker` CLI
  - runs through `driver.py` or a maintained recipe path, not only a story-local spike script
  - writes artifacts under `output/runs/` that validate against the accepted `doc-web` contract
- [ ] The maintained path fixes the Story 166 normalization defects on `testdata/tbotb-mini.pdf`:
  - heading levels are normalized consistently across pages
  - page 3's choice prompt is split into two blocks rather than merged into one paragraph
  - no silent text loss is introduced while fixing those defects
- [ ] The maintained path is compared honestly against the current OCR-routed baseline:
  - record what improves, what remains worse, and whether the maintained path is now strong enough to change the `born-digital-pdf` row in `docs/build-map.md`
  - preserve block-level provenance and processing-step traceability in an accepted `doc-web` surface
  - keep licensing/runtime constraints explicit instead of hiding them behind helper code

## Out of Scope

- Adopting stock `Marker` CLI into maintained operator workflows
- Claiming general `docx`, `pptx`, `xlsx`, or `epub` support from the `Marker` stack
- Reopening the negative `Docling` or `Surya` boundary decisions
- Broad model/license policy changes beyond the already documented `Marker` constraints

## Approach Evaluation

- **Simplification baseline**: the current maintained pagelines baseline already reaches `1.0` token coverage on `tbotb-mini.pdf`, so this story is only worth building if the `Marker` seam improves native-text routing and contract-grade provenance instead of just producing cleaner-looking HTML.
- **AI-only**: rejected as the primary path. A one-shot LLM rewrite could fix heading levels or choice splitting, but it would dodge the intake/runtime boundary question this story exists to answer.
- **Hybrid**: leading candidate. Keep Marker internals for native-text structure extraction, then use thin deterministic normalization inside the maintained path to reach the accepted `doc-web` contract.
- **Pure code**: fallback only if the current local PDFtext/OCR surfaces can now match Marker without the extra runtime burden. Story 166 evidence says that is not yet true on the repo-owned lane.
- **Repo constraints / prior decisions**: ADR-002 keeps `doc-web` as the runtime boundary; Story 165 rejected stock `Marker` adoption; Story 166 proved a contract-aligned spike but left the maintained path unbuilt.
- **Existing patterns to reuse**: `scripts/spikes/marker_breadth_benchmark.py`, `scripts/spikes/marker_page_html_prototype.py`, `doc_web/runtime_contract.py`, `modules/build/build_chapter_html_v1/main.py`, Story 157's maintained PDF-entry wiring, and the bundle/provenance contract tests.
- **Eval**: the deciding proof is a maintained run on `testdata/tbotb-mini.pdf` that emits accepted `doc-web` bundle/provenance artifacts and resolves Story 166's heading/paragraph defects without losing text or weakening provenance.

## Tasks

- [ ] Reconfirm the bounded Marker runtime substrate and decide whether the maintained path should vendor the spike logic or extract a cleaner shared helper
- [ ] Implement the smallest maintained born-digital PDF path that can reuse Marker-lite without violating ADR-002
- [ ] Land deterministic heading-level and paragraph-splitting normalization for the known `tbotb-mini.pdf` defects without hardcoding book-specific text
- [ ] Run a real maintained path through `driver.py`, inspect emitted `doc-web` bundle/provenance artifacts, and compare against the current OCR-routed baseline
- [ ] If this story changes documented format coverage or graduation reality: update `docs/build-map.md` and record the before/after state honestly
- [ ] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [ ] Run required checks for touched scope:
  - [ ] Default Python checks: `make test`
  - [ ] Default Python lint: `make lint`
  - [ ] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py` or `make smoke`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [ ] If agent tooling changed: `make skills-check`
- [ ] If evals or goldens changed: run `/improve-eval` and update `docs/evals/registry.yaml`
- [ ] Search all docs and update any related to what we touched
- [ ] Verify Central Tenets:
  - [ ] T0 — Traceability: every output traces to source page, OCR engine, confidence, processing step
  - [ ] T1 — AI-First: didn't write code for a problem AI solves better
  - [ ] T2 — Eval Before Build: measured SOTA before building complex logic
  - [ ] T3 — Fidelity: source content preserved faithfully, no silent losses
  - [ ] T4 — Modular: new recipe not new code; no hardcoded book assumptions
  - [ ] T5 — Inspect Artifacts: visually verified outputs, not just checked logs

## Workflow Gates

- [ ] Build complete: implementation finished, required checks run, and summary shared
- [ ] Validation complete or explicitly skipped by user
- [ ] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: maintained PDF intake / transform / build surfaces that currently own `born-digital-pdf` routing, plus the `doc-web` bundle/provenance contract docs.
- **Build-map reality**: Category 1 is still `partial` / `climb`; Category 3 still owns structure normalization; `born-digital-pdf` still has a fixture but no maintained native-text path.
- **Substrate evidence**: Story 166 proved repo-local spike artifacts under `output/runs/story166-marker-page-html-r2/` and `output/runs/story166-marker-probe-r2/` / `story166-marker-probe-r1`; contract tests in `tests/test_doc_web_bundle_contract.py` and `tests/test_doc_web_cli_contract.py` keep the boundary explicit; Story 157 preserves the maintained PDF entry path.
- **Data contracts / schemas**: the target is to reuse the existing `doc_web_bundle_manifest_v1` and `doc_web_provenance_block_v1` surfaces. Avoid schema changes unless the maintained path proves a real missing field.
- **File sizes**: likely touch points are already large (`modules/build/build_chapter_html_v1/main.py`, `schemas.py`, and intake/recipe surfaces), so the maintained integration should prefer small helpers or adapters over inflating giant files.
- **Decision context**: ADR-002, Scout 011, Story 165, and Story 166 are the primary constraints. No new ADR is needed unless the maintained integration forces a new runtime or licensing decision.

## Files to Modify

- `modules/` maintained intake/build surfaces for born-digital PDF routing — exact seam to be chosen during `/build-story`
- `configs/recipes/` maintained PDF recipe(s) — only if the native-text path earns a real maintained lane
- `docs/build-map.md` — update the `born-digital-pdf` row if the maintained path becomes honest coverage
- `docs/scout/scout-011-external-document-ingestion-systems.md` — update the Marker standing once the maintained decision is real
- `docs/stories/story-168-marker-lite-maintained-born-digital-pdf-path.md` — work log and plan

## Redundancy / Removal Targets

- Story-local Marker normalization glue in `scripts/spikes/marker_page_html_prototype.py` if the maintained path absorbs the same behavior cleanly
- Any stale born-digital PDF tracker language that still assumes the lane is only OCR-routed after the maintained path lands

## Notes

- Story 166 already answered the spike question positively enough to justify this story. The open question here is not "is Marker interesting?" but "can the useful seam be maintained honestly without pulling in the stock product surface?"
- Keep the follow-on narrow: repo-owned `tbotb-mini.pdf` first, maintained path second, broader born-digital widening only after that passes.

## Plan

Written by `/build-story` after substrate re-check.

## Work Log

20260327-2006 — story created as the exact maintained follow-on required by Story 166's boundary decision. Evidence: Story 166 now proves a contract-aligned spike under `output/runs/story166-marker-page-html-r2/` and a fresh current pagelines baseline under `output/runs/story166-docweb-pagelines-baseline-r1/`, but the maintained runtime path is still unbuilt. Next step: `/build-story` should verify the current maintained PDF substrate, freeze the exact integration seam, and decide whether this can honestly be promoted beyond `Draft`.
