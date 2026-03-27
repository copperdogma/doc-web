# Story 167 — Repo-Owned Scanned-Prose PDF Fixture

**Priority**: High
**Status**: Pending
**Ideal Refs**: Requirement #1 (Ingest), Requirement #3 (Extract), Any format, any condition, Minimum Viable Floor
**Spec Refs**: spec:1 (spec:1.1, C2), spec:2 (spec:2.1, spec:2.2), spec:7
**Build Map Refs**: Category 1 Intake & Format Routing (`partial`, `climb`); Category 2 OCR & Text Extraction (`exists`, C1 `climb`, C6 `hold`); Input Coverage row `scanned-pdf-prose` is currently `untested` even though Story 157 restored maintained PDF entry wiring.
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/RUNBOOK.md`, `docs/build-map.md`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/stories/story-157-pdf-intake-parity-with-image-directory-inputs.md`
**Depends On**: Story 157

## Goal

Story 157 restored maintained PDF-backed intake, but the repo still has no honest checked-in fixture for the `scanned-pdf-prose` row. This story adds a tiny repo-owned rasterized prose PDF fixture, proves the maintained PDF path against it with a cheap repeatable smoke lane, and updates the build-map / coverage truth surfaces so `scanned-pdf-prose` no longer depends on a shared local asset or a story-local note.

## Acceptance Criteria

- [ ] A small checked-in scanned-prose PDF fixture exists under `testdata/` and is reproducible from checked-in source text or a checked-in generation script:
  - the fixture is visually scanned or rasterized, not born-digital embedded text
  - fixture size stays small enough for routine repo-owned smoke use
- [ ] The maintained generic PDF recipe has repo-owned proof on that fixture:
  - an automated test or narrow smoke lane exercises `configs/recipes/recipe-pdf-ocr-html-mvp.yaml`
  - the proof verifies stamped `page_image_v1` provenance back to the fixture PDF
  - if the story claims more than entry wiring, real `driver.py` artifacts under `output/runs/` are inspected and recorded
- [ ] Documentation and format-tracking surfaces reflect the new reality honestly:
  - `testdata/README.md`, `docs/RUNBOOK.md`, `docs/build-map.md`, and `tests/fixtures/formats/_coverage-matrix.json` describe the fixture and the exact new support level
  - `scanned-pdf-prose` only moves as far as the new evidence justifies (`has-fixture` or `passing`, not beyond)

## Out of Scope

- Native embedded-text handling for `born-digital-pdf`
- Handwritten-note coverage or any fixture for the `handwritten-notes` row
- Broad OCR-quality tuning outside what is required to prove the scanned-prose fixture lane honestly
- Any new hidden routing layer beyond the current explicit-recipe compromise

## Approach Evaluation

- **Simplification baseline**: This is not an AI-reasoning problem first. The simplest honest path is a tiny rasterized prose fixture plus a narrow proof run on the already-maintained PDF recipe.
- **AI-only**: Not appropriate. An LLM cannot replace a checked-in fixture or a repeatable smoke lane.
- **Hybrid**: Potentially useful only if we need a tiny helper script to rasterize checked-in source text into page images and package them as a PDF while reusing existing smoke-test structure.
- **Pure code**: Likely the best fit. This is fixture generation, smoke wiring, and truth-surface updates around an already-built maintained path.
- **Repo constraints / prior decisions**: `spec:1.1` still requires explicit recipes; `spec:2.1` and `spec:2.2` treat OCR as a real expensive seam, so the fixture should stay tiny; ADR-002 is unaffected because this is proof-surface work inside the current `doc-web` runtime boundary.
- **Existing patterns to reuse**: `testdata/tbotb-mini.md`, `testdata/tbotb-mini.pdf`, `tests/test_pdf_intake_recipe.py`, `configs/recipes/recipe-pdf-ocr-html-mvp.yaml`, Story 157’s PDF-entry proof flow, and the existing coverage-matrix/build-map wording for `born-digital-pdf`.
- **Eval**: The decision gate is operational:
  - can a checked-in rasterized prose PDF be generated or stored cheaply?
  - does the maintained PDF recipe produce the expected stamped extractor artifact from it?
  - after inspection, is the new evidence strong enough to move `scanned-pdf-prose` from `untested` to `has-fixture` or `passing`?

## Tasks

- [ ] Add a tiny repo-owned scanned-prose fixture under `testdata/`:
  - prefer generating it from checked-in source text so provenance and licensing stay clear
  - keep it visually scanned/rasterized rather than born-digital text
- [ ] Add or extend a repo-owned proof lane for the maintained generic PDF recipe:
  - reuse `tests/test_pdf_intake_recipe.py` or add a narrow sibling test if that keeps intent clearer
  - verify `page_image_v1` rows point back to the new fixture
- [ ] Run a real `driver.py` proof at the narrowest honest scope and inspect artifacts in `output/runs/`
- [ ] Update `testdata/README.md`, `docs/RUNBOOK.md`, `docs/build-map.md`, and `tests/fixtures/formats/_coverage-matrix.json` to reflect the exact new support level honestly
- [ ] Check whether the chosen implementation makes any existing fixture wording or truth-surface notes redundant; remove them or create a concrete follow-up
- [ ] Run required checks for touched scope:
  - [ ] Default Python checks: `make test`
  - [ ] Default Python lint: `make lint`
  - [ ] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [ ] If agent tooling changed: not applicable unless this story changes skills or agent docs
- [ ] If evals or goldens changed: not applicable unless this story adds or changes eval-backed quality claims
- [ ] Search all docs and update any related to what we touched
- [ ] Verify Central Tenets:
  - [ ] T0 — Traceability: fixture-backed artifacts still trace to the source PDF
  - [ ] T1 — AI-First: do not add code-first heuristics where the maintained OCR path already suffices
  - [ ] T2 — Eval Before Build: prove the smallest fixture/proof lane before expanding quality claims
  - [ ] T3 — Fidelity: do not overclaim prose quality beyond the inspected evidence
  - [ ] T4 — Modular: reuse the maintained generic PDF recipe instead of adding a prose-only runtime path
  - [ ] T5 — Inspect Artifacts: inspect real `output/runs/` artifacts, not just the test exit code

## Workflow Gates

- [ ] Build complete: implementation finished, required checks run, and summary shared
- [ ] Validation complete or explicitly skipped by user
- [ ] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: Repo-owned fixture + proof-surface work around the maintained generic PDF recipe and the format-tracking docs.
- **Build-map reality**: Category 1 owns the format-coverage truth gap; Category 2 owns the OCR proof seam but already has the substrate. The `scanned-pdf-prose` row is the direct target.
- **Substrate evidence**: Story 157 already proved `configs/recipes/recipe-pdf-ocr-html-mvp.yaml`, `tools/run_manager.py --pdf`, and `tests/test_pdf_intake_recipe.py` work for PDF entry. The missing substrate is only the scanned/rasterized prose fixture itself.
- **Data contracts / schemas**: No new schema is expected. The proof should stay inside existing `page_image_v1` and `page_html_v1` artifacts.
- **File sizes**: [testdata/README.md](/Users/cam/.codex/worktrees/5a50/doc-web/testdata/README.md) is 39 lines, [tests/fixtures/formats/_coverage-matrix.json](/Users/cam/.codex/worktrees/5a50/doc-web/tests/fixtures/formats/_coverage-matrix.json) is 308 lines, [docs/build-map.md](/Users/cam/.codex/worktrees/5a50/doc-web/docs/build-map.md) is 569 lines, [docs/RUNBOOK.md](/Users/cam/.codex/worktrees/5a50/doc-web/docs/RUNBOOK.md) is 231 lines, [README.md](/Users/cam/.codex/worktrees/5a50/doc-web/README.md) is 165 lines, and [tests/test_pdf_intake_recipe.py](/Users/cam/.codex/worktrees/5a50/doc-web/tests/test_pdf_intake_recipe.py) is 49 lines. Avoid growing the larger docs casually.
- **Decision context**: Reviewed ADR-002, `docs/build-map.md`, the coverage matrix, and Story 157. No new ADR is needed because this story does not change architecture or the runtime boundary.

## Files to Modify

- `testdata/` — add the tiny scanned-prose PDF fixture and any reproducible source/generation helper needed
- `tests/test_pdf_intake_recipe.py` — add or extend repo-owned proof coverage (49 lines)
- `testdata/README.md` — document the new scanned-prose fixture and its intended proof level (39 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — move `scanned-pdf-prose` to the honest new state (308 lines)
- `docs/build-map.md` — update the `scanned-pdf-prose` row and notes (569 lines)
- `docs/RUNBOOK.md` — publish the narrow proof command if needed (231 lines)
- `README.md` — only if the maintained intake-recipe section needs an explicit scanned-prose fixture mention (165 lines)

## Redundancy / Removal Targets

- Any leftover wording that implies `testdata/tbotb-mini.pdf` proves `scanned-pdf-prose`
- Any stale `scanned-pdf-prose` note that still points to Story 157 after this fixture story lands

## Notes

- The smallest likely fixture path is to reuse checked-in prose source text and rasterize it into page images before packaging those images as a PDF.
- This story should not claim `passing` unless fresh artifact inspection justifies actual prose-quality confidence, not just fixture existence.
- Story 157 intentionally split this work out during close-out so the maintained PDF-entry parity story could close on its shipped slice.

## Plan

Pending — `/build-story` should first confirm the lightest honest fixture shape: either add a new tiny rasterized prose PDF directly under `testdata/` or generate it reproducibly from checked-in text with a short helper. The build should stay narrow: fixture, proof lane, fresh `driver.py` artifact inspection, then truth-surface updates only as far as the evidence supports.

## Work Log

20260327-1520 — story created during Story 157 close-out: split the residual `scanned-pdf-prose` fixture gap into a dedicated follow-up so Story 157 could close on maintained PDF-entry parity without silently weakening the documented format-coverage debt. Evidence: `docs/build-map.md` and `tests/fixtures/formats/_coverage-matrix.json` still mark `scanned-pdf-prose` as lacking a repo-owned fixture, while Story 157 proved only maintained PDF entry plus an Onward table-heavy validation lane. Next step: `/build-story` should add the tiny rasterized prose fixture, prove the maintained generic PDF recipe against it, and update the truth surfaces honestly.
