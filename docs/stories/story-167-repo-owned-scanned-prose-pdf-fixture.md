---
title: Repo-Owned Scanned-Prose PDF Fixture
status: Done
priority: High
ideal_refs:
- 'Requirement #1 (Ingest), Requirement #3 (Extract), Any format, any condition, Minimum
  Viable Floor'
spec_refs:
- spec:1
- spec:1.1
- spec:2
- spec:2.1
- spec:2.2
- spec:7
adr_refs: []
depends_on:
- '157'
category_refs:
- spec:1
- spec:2
- spec:7
compromise_refs:
- C1
- C2
- C6
input_coverage_refs:
- scanned-pdf-prose
architecture_domains: []
roadmap_tags: []
legacy_system: ''
---

# Story 167 — Repo-Owned Scanned-Prose PDF Fixture

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #1 (Ingest), Requirement #3 (Extract), Any format, any condition, Minimum Viable Floor
**Spec Refs**: spec:1 (spec:1.1, C2), spec:2 (spec:2.1, spec:2.2), spec:7
**Build Map Refs**: Category 1 Intake & Format Routing (`partial`, `climb`); Category 2 OCR & Text Extraction (`exists`, C1 `climb`, C6 `hold`); Input Coverage row `scanned-pdf-prose` now has repo-owned passing evidence on the maintained simple-prose PDF lane.
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/RUNBOOK.md`, `docs/build-map.md`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/stories/story-157-pdf-intake-parity-with-image-directory-inputs.md`
**Depends On**: Story 157

## Goal

Story 157 restored maintained PDF-backed intake, but the repo still has no honest checked-in fixture for the `scanned-pdf-prose` row. This story adds a tiny repo-owned rasterized prose PDF fixture, proves the maintained PDF path against it with a cheap repeatable smoke lane, and updates the build-map / coverage truth surfaces so `scanned-pdf-prose` no longer depends on a shared local asset or a story-local note.

## Acceptance Criteria

- [x] A small checked-in scanned-prose PDF fixture exists under `testdata/` and is reproducible from checked-in source text or a checked-in generation script:
  - the fixture is visually scanned or rasterized, not born-digital embedded text
  - fixture size stays small enough for routine repo-owned smoke use
- [x] The maintained generic PDF recipe has repo-owned proof on that fixture:
  - an automated test or narrow smoke lane exercises `configs/recipes/recipe-pdf-ocr-html-mvp.yaml`
  - the proof verifies stamped `page_image_v1` provenance back to the fixture PDF
  - if the story claims more than entry wiring, real `driver.py` artifacts under `output/runs/` are inspected and recorded
- [x] Documentation and format-tracking surfaces reflect the new reality honestly:
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

- [x] Add a tiny repo-owned scanned-prose fixture under `testdata/`:
  - prefer generating it from checked-in source text so provenance and licensing stay clear
  - keep it visually scanned/rasterized rather than born-digital text
  - prove the committed PDF is image-only (no embedded extractable text) so it is honest scanned evidence rather than a renamed born-digital smoke
- [x] Add or extend a repo-owned proof lane for the maintained generic PDF recipe:
  - reuse `tests/test_pdf_intake_recipe.py` or add a narrow sibling test if that keeps intent clearer
  - verify `page_image_v1` rows point back to the new fixture
- [x] Run a real `driver.py` proof at the narrowest honest scope and inspect artifacts in `output/runs/`
  - move `scanned-pdf-prose` only as far as the inspected artifacts justify: `has-fixture` by default, `passing` only if the fresh OCR output is clearly coherent against the checked-in source text
- [x] Update `testdata/README.md`, `docs/RUNBOOK.md`, `docs/build-map.md`, and `tests/fixtures/formats/_coverage-matrix.json` to reflect the exact new support level honestly
- [x] Check whether the chosen implementation makes any existing fixture wording or truth-surface notes redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: not applicable; pipeline code stayed unchanged, but a fresh `driver.py` proof and manual artifact inspection were still run for the support-level claim
  - [x] If agent tooling changed: not applicable unless this story changes skills or agent docs
- [x] If evals or goldens changed: not applicable unless this story adds or changes eval-backed quality claims
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: fixture-backed artifacts still trace to the source PDF
  - [x] T1 — AI-First: do not add code-first heuristics where the maintained OCR path already suffices
  - [x] T2 — Eval Before Build: prove the smallest fixture/proof lane before expanding quality claims
  - [x] T3 — Fidelity: do not overclaim prose quality beyond the inspected evidence
  - [x] T4 — Modular: reuse the maintained generic PDF recipe instead of adding a prose-only runtime path
  - [x] T5 — Inspect Artifacts: inspect real `output/runs/` artifacts, not just the test exit code

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

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

1. Fixture generation (`S`)
   Files: `testdata/` fixture assets plus `testdata/README.md`.
   Add a checked-in source-text file and a small reproduction helper that renders that text into page images and packages those images into a tiny image-only PDF. Reuse the existing `testdata/vendor/fpdf` pattern and keep the final artifact clearly distinct from `tbotb-mini.pdf`.
   Done when the fixture is small, reproducible, and blank under embedded-text extraction checks so it is honest scanned evidence.

2. Cheap proof lane (`S`)
   Files: `tests/test_pdf_intake_recipe.py`.
   Extend the maintained PDF smoke coverage with a scanned-prose case, but keep the automated lane extract-only so `make test` stays cheap: assert stamped `page_image_v1` rows point back to the scanned fixture PDF and emitted page images exist.
   Impact/risk: low blast radius in tests plus fixture docs only; no schema or runtime-boundary change expected.
   Done when the repo has separate cheap proof for the two distinct claims: born-digital PDF entry smoke and scanned-prose provenance smoke.

3. Real-run evidence and support-level gate (`S`)
   Files: story work log plus fresh `output/runs/<run_id>/...` artifacts.
   Run `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` through `ocr_ai` on the scanned fixture and inspect `01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl` and `02_ocr_ai_gpt51_v1/pages_html.jsonl` against the checked-in source text.
   Decision rule: if the PDF is image-only and the OCR artifact is coherent page-by-page, promote `scanned-pdf-prose` to `passing`; otherwise land `has-fixture` only.
   Small scope fold-in already identified: if a `passing` claim would otherwise feel subjective, add a tiny source-vs-output comparison helper or an explicit normalization note rather than overclaiming from visual inspection alone.

4. Truth-surface updates and redundancy cleanup (`XS`)
   Files: `docs/build-map.md`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/RUNBOOK.md`, `testdata/README.md`, and `README.md` only if the maintained fixture list needs it.
   Update the input-coverage counts and row notes to the exact proven level, and remove any leftover wording that implies `tbotb-mini.pdf` proves scanned prose.
   Expected movement: at minimum `scanned-pdf-prose` leaves `untested`; best case it moves to `passing` with fresh inspected evidence, otherwise it moves to `has-fixture`.

5. Verification (`S`)
   Run targeted proof first (`python -m pytest tests/test_pdf_intake_recipe.py -q`), then the story-required defaults `make lint` and `make test`.
   If the final support claim depends on OCR quality rather than extractor provenance alone, clear stale `*.pyc`, run the narrow `driver.py` proof, and record the specific inspected artifact paths plus sample text quality in the work log.

## Work Log

20260327-1520 — story created during Story 157 close-out: split the residual `scanned-pdf-prose` fixture gap into a dedicated follow-up so Story 157 could close on maintained PDF-entry parity without silently weakening the documented format-coverage debt. Evidence: `docs/build-map.md` and `tests/fixtures/formats/_coverage-matrix.json` still mark `scanned-pdf-prose` as lacking a repo-owned fixture, while Story 157 proved only maintained PDF entry plus an Onward table-heavy validation lane. Next step: `/build-story` should add the tiny rasterized prose fixture, prove the maintained generic PDF recipe against it, and update the truth surfaces honestly.
20260327-0809 — exploration + baseline probe: verified this story closes a real Ideal gap in Category 1 (`partial`, `climb`) without changing the current recipe-selection compromise in `spec:1.1`, and that Category 2 already has the required OCR substrate (`exists`, C1 `climb`, C6 `hold`). Reviewed `docs/ideal.md`, `docs/spec.md` (`spec:1.1`, `spec:2.1`, `spec:2.2`, `spec:7`), `docs/build-map.md`, ADR-002, `docs/RUNBOOK.md`, Story 157, `tests/test_pdf_intake_recipe.py`, `testdata/README.md`, and searched `docs/decisions/` for any newer PDF/fixture decision; none changed the approach, so no new ADR is needed. Critical substrate verified in code: `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` already drives the maintained PDF path, `tests/test_pdf_intake_recipe.py` already proves extractor provenance for `tbotb-mini.pdf`, `extract_pdf_images_fast_v1` stamps `page_image_v1.source` from the input PDF, and both `pypdf` and `PIL` are available locally for a reproducible image-only fixture flow. Baseline evidence: `tbotb-mini.pdf` is definitively born-digital (`pdffonts` shows `Helvetica`; `pdftotext` extracts coherent text), so it cannot honestly back `scanned-pdf-prose`. Two scratch fixture probes show the real decision gate. A naive bitmap/blurred image-only PDF proved the format distinction but not prose quality (`pdftotext` blank, `pypdf` extract text length `0`, and `ocr_quality 0.63` in `output/runs/story167-probe-ocr-1774623976/02_ocr_ai_gpt51_v1/pages_html.jsonl`). A higher-resolution rasterized image-only PDF generated from checked-in text stayed honest scanned evidence (`pypdf` extract text length `0` on all 4 pages under `/tmp/story167_probe_ttf/probe-scanned-ttf.pdf`) and the maintained recipe produced coherent OCR with `ocr_quality 0.96-0.98` across `output/runs/story167-probe-ttf-1774624057/02_ocr_ai_gpt51_v1/pages_html.jsonl`. Files likely to change: new fixture assets under `testdata/`, `tests/test_pdf_intake_recipe.py`, `testdata/README.md`, `docs/RUNBOOK.md`, `docs/build-map.md`, `tests/fixtures/formats/_coverage-matrix.json`, and maybe `README.md`. Files at risk: low; no schema or runtime-boundary changes are expected. Surprise: the missing substrate is not PDF-entry wiring anymore, it is only the quality of the repo-owned scanned fixture and the honesty of the support-level claim. Next step: implement the repo-owned image-only fixture, extend the cheap provenance smoke, and only move `scanned-pdf-prose` beyond `has-fixture` if fresh OCR artifacts justify it.
20260327-0831 — implementation + verification: added the repo-owned scanned-prose fixture set under `testdata/`: original source text `scanned-prose-mini.md`, generator `generate_scanned_prose_fixture.py`, and generated image-only PDF `scanned-prose-mini.pdf` (4 pages, 1.4 MB). Verified the committed PDF is honest scanned evidence rather than embedded text: `pdftotext` outputs blank pages and `pypdf` reports extract-text lengths `[0, 0, 0, 0]`. Extended `tests/test_pdf_intake_recipe.py` with a second maintained smoke lane for the scanned fixture; `python -m pytest tests/test_pdf_intake_recipe.py -q` passed (`2 passed in 86.76s`). Ran a fresh real proof through `driver.py`: `python driver.py --recipe configs/recipes/recipe-pdf-ocr-html-mvp.yaml --input-pdf testdata/scanned-prose-mini.pdf --run-id story167-scanned-prose-proof --output-dir output/runs/story167-scanned-prose-proof --allow-run-id-reuse --force --end-at ocr_ai` completed successfully. Manual artifact inspection: `output/runs/story167-scanned-prose-proof/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl` contains 4 stamped `page_image_v1` rows, all pointing back to `/Users/cam/.codex/worktrees/8496/doc-web/testdata/scanned-prose-mini.pdf`; `output/runs/story167-scanned-prose-proof/02_ocr_ai_gpt51_v1/pages_html.jsonl` contains 4 stamped `page_html_v1` rows with `ocr_quality` `0.98`, `0.98`, `0.98`, and `0.99`; page 1 preserves the title plus `Morning Light`, page 2 preserves `The Stack Room`, page 3 preserves `The Index Table`, and page 4 preserves `Closing the Shutters`. A normalized comparison against the checked-in source text matched exactly (`SequenceMatcher ratio 1.0`, identical normalized character and token counts), which is strong enough to move the repo-owned `simple-prose` scanned lane to `passing` while still documenting that degraded/noisy scanned prose remains unmeasured. Updated `testdata/README.md`, `docs/RUNBOOK.md`, `docs/build-map.md`, and `tests/fixtures/formats/_coverage-matrix.json` to remove any implication that `tbotb-mini.pdf` proves scanned prose and to record the new passing evidence honestly. Fresh repo checks passed: `make lint` clean; `make test` passed (`376 passed, 12 warnings in 305.98s`). Impact: Story-scope gap closed; the repo now owns and proves a real scanned-prose PDF lane instead of relying on a story note. Pipeline-scope impact: the maintained generic PDF recipe now has repo-owned, image-only, provenance-rich proof on both born-digital entry smoke and scanned simple-prose OCR. Next step: `/validate` for an independent close-out pass, then `/mark-story-done` if validation agrees.
20260327-0840 — story marked done after fresh validation. Re-ran the close-out checks in the validation pass: `make lint` passed cleanly, `make test` passed (`376 passed, 12 warnings in 177.35s`), `testdata/scanned-prose-mini.pdf` still reports extract-text lengths `[0, 0, 0, 0]`, `output/runs/story167-scanned-prose-proof/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl` still contains 4 stamped rows sourced from the committed fixture, and `output/runs/story167-scanned-prose-proof/02_ocr_ai_gpt51_v1/pages_html.jsonl` still matches the checked-in source text exactly after normalization (`SequenceMatcher ratio 1.0`). Closed the workflow gates, updated the story index, and confirmed no ADR follow-up was needed because this story stayed within the existing runtime boundary and recipe-selection compromise. Next step: `/check-in-diff`.
