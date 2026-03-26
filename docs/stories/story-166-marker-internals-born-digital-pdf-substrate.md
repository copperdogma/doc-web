# Story 166 — Use Marker Internals as a Thin Born-Digital PDF Substrate

**Priority**: High
**Status**: Draft
**Ideal Refs**: Requirement #1 (Ingest), Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Any format, any condition, Traceability is the Product
**Spec Refs**: spec:1 (spec:1.1, C2), spec:3 (spec:3.1, C3), spec:6, spec:7
**Build Map Refs**: Category 1 Intake & Format Routing (`partial`, C2 `climb`); Category 3 Layout & Structure Understanding (`exists`, C3 `climb`); Category 7 Graduation & Dossier Handoff (`partial`); Input Coverage row `born-digital-pdf` remains high-priority untested
**Decision Refs**: `docs/scout/scout-011-external-document-ingestion-systems.md`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/stories/story-157-pdf-intake-parity-with-image-directory-inputs.md`, `docs/stories/story-165-marker-breadth-comparator-born-digital-pdf.md`, `docs/build-map.md`
**Depends On**: Story 157, Story 165

## Goal

Story 165 answered the broad comparator question: stock `Marker` is too heavy
and awkward to adopt as a product-level converter here, but the thinner
Marker-internals path preserved born-digital PDF structure more usefully than
the current local OCR-routed baseline on `testdata/tbotb-mini.pdf`. This story
should determine whether that thinner internal seam can become a real upstream
substrate for `born-digital-pdf` intake inside `doc-web`, without adopting the
stock Marker CLI and without violating the repo's traceability-first runtime
boundary. The output should answer one question: can selected Marker internals
feed a thin, inspectable born-digital path that reduces pressure on Story 157's
PDF intake gap while keeping `doc-web` as the canonical boundary?

## Acceptance Criteria

- [ ] The exact seam is frozen before any maintained integration claim:
  - stock `Marker` CLI remains explicitly out of scope for adoption
  - the specific Marker internal classes/processors to reuse are named
  - code-license and model-license posture are summarized against the proposed ownership boundary
- [ ] A thin prototype exists on the active `born-digital-pdf` seam:
  - uses the repo-owned `tbotb-mini.pdf` fixture first
  - writes inspectable artifacts under `output/runs/`
  - proves whether Marker internals can be normalized into an existing `doc-web`-useful artifact surface instead of remaining a standalone export
- [ ] The prototype is compared honestly against the current local baseline:
  - compare against the current OCR-routed/pagelines baseline from Story 165
  - explicitly record what gets better, what provenance gets worse, and what remains missing
  - do not count cosmetic markdown improvements as a win if the normalized artifact surface is still unusable downstream
- [ ] The story ends with a single boundary decision:
  - if the thin seam wins cleanly, name the exact maintained integration story or ADR follow-up
  - if it does not, park Marker as a parts-bin reference and stop

## Out of Scope

- Adopting stock `Marker` CLI into the maintained runtime
- Claiming `born-digital-pdf` is shipped or passing before a real maintained path exists
- Reopening the closed Onward `Docling` or `Surya` seams
- Claiming multi-format `Marker` breadth beyond the explicitly tested PDF lane
- Quietly accepting GPL or model-license constraints into the maintained boundary without an explicit decision

## Approach Evaluation

- **Simplification baseline**: the current local baseline already exists and is cheap enough to measure: Story 165's `story165-docweb-baseline-r1` still OCR-routes a born-digital PDF even when `pdftext` covers every page. This story is only worth building if the thin Marker seam beats that baseline on structure quality, not just presentation.
- **AI-only**: not sufficient. A one-shot LLM rewrite of PDF text would not answer the ownership/runtime/provenance question and would bypass the very substrate this story is evaluating.
- **Hybrid**: the leading candidate. Reuse the proven Marker internals seam from Story 165, then normalize it into an existing `doc-web`-useful artifact surface while keeping `doc-web` in control of downstream ownership and provenance reporting.
- **Pure code**: viable fallback only if Story 165's Marker result turns out to be mostly reproducible with lighter local embedded-text plus deterministic structuring. Do not assume that without measurement.
- **Repo constraints / prior decisions**: ADR-002 keeps `doc-web` as the runtime boundary. Story 157 keeps scanned-PDF parity separate from born-digital PDF. Story 165 already said "no" to stock Marker adoption and "maybe" to a thin internal substrate. Scout 011 now tracks Marker as a scoped follow-on candidate, not a broad product adoption path.
- **Existing patterns to reuse**: `scripts/spikes/marker_breadth_benchmark.py`, Story 165 benchmark artifacts, Story 157's PDF-intake framing, `tests/fixtures/doc_web_bundle_smoke/`, the `doc_web` bundle contract, and the lessons from the closed `Docling` chain about keeping external tools outside the accepted runtime boundary until they earn it.
- **Eval**: the deciding proof is a normalized born-digital substrate comparison:
  - can the thin Marker seam preserve embedded-text structure better than the current OCR-routed baseline?
  - can it emit an artifact shape that is actually useful to `doc-web` or Dossier-facing export work?
  - are the license/runtime/provenance costs still acceptable after inspection?
  If the answer is only "Marker markdown looks nicer," the story should stop.

## Tasks

- [ ] Verify the exact reusable seam before promotion out of `Draft`:
  - record the specific internal Marker classes/processors that Story 165 proved locally
  - record the license/runtime constraints that still block stock CLI adoption
  - keep the story `Draft` if the thin internal seam cannot be reproduced cleanly outside the Story 165 spike harness
- [ ] Freeze the prototype surface before coding:
  - mandatory first lane is `testdata/tbotb-mini.pdf`
  - define the exact normalized artifact target (`page_html_v1`, bundle-adjacent HTML, or another existing surface)
  - define the stop rule if provenance loss or licensing awkwardness makes the seam not worth integrating
- [ ] Implement the smallest honest prototype:
  - keep it isolated to a story-local spike or clearly optional adapter seam
  - do not wire stock Marker CLI into recipes or operator workflows
  - prefer proving the normalization path before touching maintained runtime surfaces
- [ ] Compare the prototype against the Story 165 local baseline and manually inspect representative outputs
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

- **Owning module / area**: born-digital intake/adaptation and external benchmark transfer. The likely owners are a story-local spike or optional adapter seam plus the tracker docs; the maintained runtime should stay untouched until the thin seam actually wins.
- **Build-map reality**: Category 1 is still `partial` / `climb`, Category 3 still owns structure extraction, and `born-digital-pdf` remains unshipped. This story exists because Story 165 produced enough evidence to justify a narrower substrate experiment without claiming coverage.
- **Substrate evidence**: Story 165 already proved the local Docker runtime, the Marker internals path in `scripts/spikes/marker_breadth_benchmark.py`, the benchmark artifacts in `output/runs/story165-marker-benchmark-r1/`, and the current local baseline in `output/runs/story165-docweb-baseline-r1/`. What does not exist yet is any maintained normalization from Marker internals into an accepted `doc-web` artifact surface.
- **Data contracts / schemas**: expected to reuse existing artifact contracts if possible. If the prototype needs new cross-artifact fields, they must be added to `schemas.py` before code emits them.
- **File sizes**: `scripts/spikes/marker_breadth_benchmark.py` is already a live story-local harness and should stay the main reuse point. `docs/build-map.md` is large, so only touch it if this story materially changes coverage or next-step reality. Any new adapter code should stay small and bounded until the seam is proven.
- **Decision context**: reviewed `docs/ideal.md`, `docs/build-map.md`, Scout 011, ADR-002, Story 157, and Story 165. No new ADR is required at creation time because this is still a bounded spike, not an accepted runtime-boundary change.

## Files to Modify

- `docs/stories/story-166-marker-internals-born-digital-pdf-substrate.md` — this story file and work log (new file)
- `docs/stories.md` — story index row for Story 166
- `scripts/spikes/marker_breadth_benchmark.py` — likely reuse or extension point for the thin-seam prototype
- `docs/scout/scout-011-external-document-ingestion-systems.md` — update only if the result changes Marker's tracked standing again
- `docs/build-map.md` — update only if the story materially changes born-digital next-step reality
- optional new spike or adapter file under `scripts/spikes/` or `modules/` — only if the prototype surface is actually proven

## Redundancy / Removal Targets

- the idea that `Marker` must be treated only as a full-converter product rather than a parts-bin source
- any temporary story-local normalization glue if the thin seam proves out and moves into a cleaner maintained surface
- any premature stock-CLI adoption notes that survive after the thin-seam result is known

## Notes

- Story 165 already answered the first useful question. This story exists only because the answer was mixed, not cleanly negative.
- The most important open question is boundary honesty: can we steal the useful structure-preserving part of Marker without taking on an ugly runtime/license/provenance burden?
- If the answer is "only by effectively embedding Marker as a hidden second runtime," the story should stop.

## Plan

Pending — `/build-story` should first verify that the Story 165 thin seam can be
reproduced cleanly enough to prototype without inheriting the stock CLI's
multi-gigabyte warmup behavior. Keep this story in `Draft` until that substrate
is explicit and the normalized artifact target is frozen.

## Work Log

20260326-1241 — story created: Story 165 closed the broad comparator question
enough to justify a narrower follow-on around Marker internals, not stock
Marker adoption. Evidence: `output/runs/story165-marker-benchmark-r1/tbotb-mini/marker-v1102/summary.json`
shows `1.0` heading coverage and `1.0` token coverage for the `lite_api` path,
while `output/runs/story165-docweb-baseline-r1/ocr_ensemble/ocr_source_histogram.json`
still routes all pages through `tesseract` despite full `pdftext` coverage.
Next step: `/build-story` should verify the exact reusable seam and freeze the
normalized artifact target before promoting this story out of `Draft`.
