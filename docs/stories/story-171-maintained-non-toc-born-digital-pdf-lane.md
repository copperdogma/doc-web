# Story 171 — Maintain a Non-TOC Born-Digital PDF Lane

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #1 (Ingest), Requirement #3 (Extract), Requirement #6 (Validate), Zero configuration, Any format, any condition, Traceability is the Product
**Spec Refs**: spec:1 (spec:1.1, C2), spec:3 (spec:3.1, C3), spec:6, spec:7, spec:8 (B1)
**Build Map Refs**: Category 1 Intake & Format Routing (`exists`, C2 `climb`); Category 3 Layout & Structure Understanding (`exists`, C3 `climb`); Category 7 Graduation & Dossier Handoff (`partial`); Category 8 AI Harnesses & Tooling (`exists`, B1 `hold`); Input Coverage row `born-digital-pdf` (`has fixture`); Gap 2 — Born-digital PDF native text extraction
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/stories/story-137-onward-missing-content-and-chapter-boundary-gaps.md`, `docs/stories/story-157-pdf-intake-parity-with-image-directory-inputs.md`, `docs/stories/story-168-marker-lite-maintained-born-digital-pdf-path.md`, `docs/stories/story-169-restore-contact-sheet-intake-and-benchmark-auto-book-type-detection.md`, `docs/stories/story-170-born-digital-pdf-native-text-widening-and-routing-decision.md`, `docs/scout/scout-011-external-document-ingestion-systems.md`, `docs/build-map.md`, `None found after search in docs/decisions/ for non-TOC-PDF-specific ADRs`
**Depends On**: Story 157, Story 168, Story 169, Story 170

## Goal

Story 170 made the current born-digital routing honest by returning `no-recipe-needed` for short flat PDFs whose maintained full HTML recipes still die at `portionize_toc`. This follow-up closes that remaining product gap by adding the smallest honest maintained non-TOC born-digital PDF lane, proving it on real `driver.py` runs, and updating intake so proven flat/non-book PDFs can recommend an explicit maintained recipe instead of stalling at `no-recipe-needed`.

## Acceptance Criteria

- [x] A maintained non-TOC born-digital PDF proof surface exists and is explicit:
  - at least one repo-owned or reproducibly generated flat/non-TOC born-digital PDF fixture is available under `testdata/`, or the story explicitly keeps shipped support bounded because repeatable proof would otherwise depend on local-only assets
  - Story 170 validation assets (`rfp`, `release-forms`) are reused as comparison evidence where licensing permits, but they are not the only proof behind a new maintained claim
- [x] A maintained explicit recipe runs through `driver.py` on the supported non-TOC slice without failing at portionization:
  - it produces stamped `page_html_v1`
  - it produces a non-empty portion artifact acceptable to the builder
  - it produces final `doc_web_bundle` / chapter outputs under `output/runs/`
  - manual artifact inspection is recorded for representative `pages_html.jsonl`, portion artifact(s), `output/html/manifest.json`, and `output/html/provenance/blocks.jsonl`
- [x] Intake routing becomes more capable without becoming dishonest:
  - `modules/intake/intake_plan_utils.py` recommends the new explicit maintained recipe only for the proven non-TOC slice
  - the existing book-like TOC path stays intact
  - unsupported flat PDFs still return `no-recipe-needed` rather than being silently over-promoted
- [x] Repeatable proof remains after the story:
  - narrow unit/smoke coverage exists for the chosen non-TOC portionization / build path
  - `tests/fixtures/formats/_coverage-matrix.json`, `docs/build-map.md`, and any affected intake docs reflect the new reality honestly
  - if the accepted maintained recommendation surface changes the Story 169 corpus expectations, rerun the `auto-book-type-detection` harness and update `docs/evals/registry.yaml`

## Out of Scope

- Claiming general support for `docx`, `xlsx`, `pptx`, `epub`, email, or web-page inputs
- Replacing the explicit-recipe compromise (`C2`) with hidden dispatch or silent auto-launch
- Reopening the Marker vs `doc-web` boundary decision from ADR-003 or the broader external-system benchmark question from Scout 011
- Replacing the existing TOC/book-like born-digital path with a heading-only strategy for documents that already expose a trustworthy TOC
- Solving all form semantics, table semantics, or downstream Dossier normalization in one pass if a page-level or shallow heading-based bundle is the honest supported slice

## Approach Evaluation

- **Simplification baseline**: first run the current flat/non-TOC `page_html_v1` outputs through existing substrate before adding new logic. The key check is whether `portionize_headings_html_v1`, `build_chapter_html_v1` fallback-page behavior, or the existing Marker sidecar bundle already clear the acceptance bar with only recipe wiring changes.
- **AI-only**: use a model to synthesize a chapter/section plan from `page_html_v1` for flat PDFs. This may rescue sparse-heading cases, but it would hide the new maintained lane inside another prompt layer before the repo has measured whether deterministic fallback is enough.
- **Hybrid**: likely strongest starting point. Keep deterministic extract/routing and a deterministic non-TOC fallback (heading-based, single-document, or page-level), and use AI only if the flat PDF still needs lightweight structure judgment after extraction.
- **Pure code**: plausible if the supported slice is limited to flat PDFs where extraction quality is already good and the real failure is just that the maintained recipes assume TOC-bearing structure. This can cover new portionizer fallback logic, recipe wiring, and honest routing docs.
- **Repo constraints / prior decisions**: Story 170 proved the current failure is downstream of extraction, not classification. Story 137 also proved heading-only splitting is unsafe when a reliable TOC exists, so any new heading-based reuse must stay explicitly scoped to the non-TOC lane. ADR-002 keeps the `doc-web` bundle boundary explicit, and Story 169 keeps intake recommendation-only.
- **Existing patterns to reuse**: `modules/extract/extract_pdf_marker_lite_html_v1`, `modules/portionize/portionize_headings_html_v1`, `modules/build/build_chapter_html_v1`, `configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml`, `configs/recipes/recipe-pdf-ocr-html-mvp.yaml`, `tests/test_extract_pdf_marker_lite_html_v1.py`, `tests/test_pdf_intake_recipe.py`, `tests/test_intake_plan_utils.py`, and Story 169's benchmark-harness pattern.
- **Eval**: the deciding proof is a fresh `driver.py` comparison on flat/non-TOC born-digital fixtures measuring whether the chosen maintained lane emits acceptable portion artifacts and final bundle/provenance outputs. If intake expectations change for the benchmark corpus, rerun `benchmarks/scripts/run_auto_book_type_detection_eval.py` and refresh `docs/evals/registry.yaml`.

## Tasks

- [x] Freeze the supported slice and proof surface:
  - [x] Reuse Story 170's `rfp` and `release-forms` assets as comparison evidence
  - [x] Add a repo-owned or reproducibly generated non-TOC born-digital fixture if the story wants to ship a maintained support claim beyond local evidence
  - [x] Record the intended output shape per fixture: heading-derived chapters, single-document output, or page-level fallback
- [x] Measure the current substrate before introducing new logic:
  - [x] Run the current extracted `page_html_v1` outputs through `portionize_headings_html_v1` and `build_chapter_html_v1` (or the smallest equivalent proof path)
  - [x] Record the exact current failure modes: no qualifying headings, empty portions rejected by build, bad splits, or insufficient bundle semantics
  - [x] Decide whether existing Marker `doc_web_bundle` sidecars are sufficient for the accepted slice or whether the maintained final build path must change
- [x] Implement only the smallest maintained non-TOC lane the evidence supports:
  - [x] Add a maintained explicit non-TOC recipe or variant
  - [x] Either extend `portionize_headings_html_v1`, add a sibling non-TOC portionizer, or relax `build_chapter_html_v1` so a non-TOC lane can reach final bundle output honestly
  - [x] Update `modules/intake/intake_plan_utils.py` only for the proven slice
- [x] Add repeatable proof:
  - [x] Add or extend unit tests for the chosen non-TOC portionization/build behavior
  - [x] Extend `tests/test_pdf_intake_recipe.py` and `tests/test_intake_plan_utils.py` for the new maintained path
  - [x] If benchmark expectations change, rerun `/improve-eval auto-book-type-detection` behaviorally via the maintained harness and update `docs/evals/registry.yaml`
- [x] If this story changes documented format coverage or graduation reality: update `docs/build-map.md` and record the before/after state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL/HTML data
  - [x] If agent tooling changed: `make skills-check` (not needed; agent tooling unchanged)
- [x] If evals or goldens changed: run `/improve-eval` and update `docs/evals/registry.yaml`
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every output traces to source page, OCR engine, confidence, processing step
  - [x] T1 — AI-First: didn't write code for a problem AI solves better
  - [x] T2 — Eval Before Build: measured SOTA before building complex logic
  - [x] T3 — Fidelity: source content preserved faithfully, no silent losses
  - [x] T4 — Modular: new recipe not new code; no hardcoded book assumptions
  - [x] T5 — Inspect Artifacts: visually verified outputs, not just checked logs

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: the non-TOC gap sits across intake recommendation, portionize, and build. Category 1 owns the routing claim; Category 3 owns the structure fallback; Category 7 owns the final `doc-web` bundle truth surface.
- **Build-map reality**: Category 1 is `exists` / `climb`, Category 3 is `exists` / `climb`, Category 7 is `partial`, and the relevant Input Coverage row is `born-digital-pdf` (`has fixture`). Gap 2 in `docs/build-map.md` already names this story shape explicitly.
- **Substrate evidence**: verified in code that `configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml` and `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` both reach `page_html_v1`; Story 170 proved they then fail at `portionize_toc` on flat PDFs. `modules/portionize/portionize_headings_html_v1/main.py` exists and emits `portion_hyp_v1`, but exits on zero headings. `modules/build/build_chapter_html_v1/main.py` can emit fallback page files for uncovered pages, but currently exits if the portions artifact is empty. `tests/test_extract_pdf_marker_lite_html_v1.py`, `tests/test_pdf_intake_recipe.py`, and `tests/test_intake_plan_utils.py` prove the extract and routing seams already exist.
- **Data contracts / schemas**: likely touched artifacts are `page_html_v1`, `portion_hyp_v1`, `doc_web_bundle_manifest_v1`, and `intake_plan_v1`. If the chosen path adds new stamped fields that cross artifact boundaries, update `schemas.py` before relying on them.
- **File sizes**: `modules/portionize/portionize_headings_html_v1/main.py` is 175 lines, `modules/build/build_chapter_html_v1/main.py` is 1626 lines, `configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml` is 42 lines, `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` is 88 lines, `modules/intake/intake_plan_utils.py` is 160 lines, `tests/test_pdf_intake_recipe.py` is 62 lines, `tests/test_intake_plan_utils.py` is 85 lines, `tests/test_build_chapter_html.py` is 1479 lines, `docs/build-map.md` is 584 lines, `tests/fixtures/formats/_coverage-matrix.json` is 340 lines, and `docs/evals/registry.yaml` is 537 lines. The builder, build map, and eval registry are already large, so prefer narrow helpers or new tests over bloating them casually.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/build-map.md`, ADR-002, Stories 137/157/168/169/170, and Scout 011. No non-TOC-PDF-specific ADR exists today, and a new ADR should only be created if this story discovers a broader architecture question than an explicit maintained lane.

## Files to Modify

- `configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml` — keep the TOC/book-like lane explicit or factor shared extraction if the non-TOC lane becomes a sibling recipe (42 lines)
- `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml` — new maintained explicit non-TOC lane
- `modules/portionize/portionize_headings_html_v1/main.py` — extend heading-derived fallback only if this is the right base for the non-TOC lane (175 lines)
- `modules/build/build_chapter_html_v1/main.py` — support honest non-TOC/fallback bundle construction if the current empty-portions guard blocks the maintained lane (1626 lines)
- `modules/intake/intake_plan_utils.py` — recommend the new explicit lane only for the proven non-TOC slice (160 lines)
- `tests/test_pdf_intake_recipe.py` — add smoke coverage for the maintained non-TOC recipe (62 lines)
- `tests/test_intake_plan_utils.py` — update routing expectations for the proven slice (85 lines)
- `tests/test_build_chapter_html.py` — add non-TOC / fallback bundle coverage if build behavior changes (1479 lines)
- `tests/test_portionize_headings_html_v1.py` — new focused coverage if heading-derived fallback logic changes
- `testdata/` — add a repo-owned non-TOC born-digital fixture or generator if the story ships maintained support beyond local-only evidence
- `tests/fixtures/formats/_coverage-matrix.json` — move `born-digital-pdf` only as far as the new evidence justifies (340 lines)
- `docs/build-map.md` — update Gap 2, Next Actions, and the `born-digital-pdf` row honestly (584 lines)
- `docs/evals/registry.yaml` — refresh `auto-book-type-detection` only if the maintained recommendation surface changes (537 lines)

## Redundancy / Removal Targets

- Any lingering `no-recipe-needed` expectation for the now-proven flat born-digital slice in intake goldens or docs
- Any one-off local comparison harness or scratch recipe created during Story 170 if this story lands a real maintained non-TOC lane
- Any future duplicate flat-PDF recipe branch if the chosen maintained lane cleanly supersedes it

## Notes

- Story 137 is the main scope guard: heading-derived splitting is not a safe replacement for TOC-driven books. If reused here, it must stay explicitly limited to the non-TOC lane.
- The smallest honest supported slice may be page-level or single-document output for flat PDFs, not full semantic chapterization.
- If the story cannot leave repeatable proof without relying on local-only PDFs, it should keep the shipped support claim narrow instead of overpromoting the format row.

## Plan

### Exploration Summary

- **Ideal alignment:** proceed. This story closes the exact remaining gap left open intentionally by Story 170: the repo can now detect flat born-digital PDFs honestly, but it still cannot convert the proven flat slice through a maintained explicit lane.
- **Relevant build-map state:** Category 1 and Category 3 both have real substrate and are both still `climb`. Gap 2 and Next Action 1 in `docs/build-map.md` already call for a non-TOC born-digital follow-up.
- **Critical substrate verified in code:** extract substrate exists, intake routing exists, a heading-based portionizer exists, and the chapter builder already contains fallback-page logic. The missing substrate is the maintained non-TOC bridge between extracted `page_html_v1` and a final accepted bundle.
- **Measured failure already known:** Story 170 proved the current maintained recipes reach `page_html_v1` on `rfp` and `release-forms` and then fail at `portionize_toc`. That means this story should start at portionization/build, not re-litigate extraction or intake classification first.
- **Key repo-fit constraint:** `build_chapter_html_v1` currently rejects an empty portions file, and `portionize_headings_html_v1` rejects documents with no qualifying headings. One or both of those guards likely define the minimum implementation scope.

### Eval-First Gate

- **Baseline first:** before adding a new module or recipe, run the current flat/non-TOC fixtures through the existing heading-based portionizer and the current builder path to see whether the gap is just recipe wiring plus a tiny fallback.
- **Fresh current-code baseline:** `pytest -q tests/test_intake_plan_utils.py tests/test_pdf_intake_recipe.py` => `7 passed in 2.73s`. This confirms the current routing narrowing from Story 170 and the extract-only PDF smokes still hold, but it also confirms the present test surface stops before the non-TOC portionize/build seam.
- **Fresh proof-surface baseline:** `rg --files testdata | rg '\.pdf$'` => only `testdata/tbotb-mini.pdf` and `testdata/scanned-prose-mini.pdf`. The repo still lacks a shipped flat/non-TOC born-digital PDF fixture, so shipping a maintained claim beyond local validation assets will require either adding a reproducible fixture/generator or keeping the supported slice explicitly bounded.
- **What the baseline must answer:** do the current extracted HTML pages already support an honest maintained output if we avoid `portionize_toc`, or do sparse-heading / no-heading PDFs need a new fallback structure strategy?
- **Chosen proof surface:** fresh `driver.py` runs on a repo-owned non-TOC born-digital fixture plus Story 170's local flat-PDF validation assets, followed by manual inspection of `page_html_v1`, portion outputs, and final bundle artifacts.

### Implementation Tasks

#### Task 1 — Freeze the supported non-TOC slice (`S`)

- Reuse Story 170's `rfp` and `release-forms` as comparison assets.
- Add a repo-owned flat/non-TOC born-digital fixture if shipping maintained support beyond local evidence.
- Record expected output shape per fixture: heading-derived chapter(s), single-document output, or page-level fallback.

#### Task 2 — Probe current non-TOC substrate (`S`)

- Run the existing extracted `page_html_v1` artifacts through `portionize_headings_html_v1` and `build_chapter_html_v1`.
- Confirm whether current failure is:
  - zero headings
  - headings that exist but split badly
  - empty portions rejected by build
  - bundle output that is structurally honest but still below the bar

#### Task 3 — Land the smallest maintained non-TOC lane (`M`)

- Add a maintained non-TOC recipe or variant.
- Implement only the minimum structure fallback the measured failures require.
- Keep the existing TOC/book-like lane unchanged.
- Update intake recommendation logic only for the proven supported slice.

#### Task 4 — Leave repeatable proof and honest docs (`S-M`)

- Add targeted tests for the chosen non-TOC structure path.
- Extend recipe/routing smokes.
- Re-run the intake benchmark if its expected maintained recommendation changes.
- Update `docs/build-map.md` and `tests/fixtures/formats/_coverage-matrix.json` to the exact proven state.

### Impact Analysis

- **Primary blast radius:** born-digital recipe selection, portionize fallback behavior, and final bundle construction.
- **Secondary blast radius:** intake routing expectations, format coverage truth surfaces, and the Story 169 benchmark if the recommended explicit recipe changes.
- **Main risk:** shipping a maintained lane that only works on one ad hoc PDF shape and then overstating the support level. The story must optimize for honesty before convenience.

### What Done Looks Like

- At least one flat/non-TOC born-digital PDF can go through a maintained explicit recipe and finish with inspected final outputs.
- Intake recommends that recipe for the proven slice instead of `no-recipe-needed`.
- The repo keeps the TOC/book-like path separate and honest.
- The build map, coverage matrix, and benchmark surfaces all agree on what is now actually supported.

## Work Log

20260329-0037 — story created from triage: turned Build Map Next Action 1 into a concrete follow-up after verifying the real substrate in code. Evidence: `docs/build-map.md` still names the non-TOC born-digital lane as the next gap, Story 170 already proved the current maintained recipes reach `page_html_v1` and then die at `portionize_toc` on flat PDFs, `modules/portionize/portionize_headings_html_v1/main.py` already exists as a possible fallback seam, and `modules/build/build_chapter_html_v1/main.py` already contains fallback-page logic but still rejects empty portions. Next step: `/build-story` should run the current non-TOC baseline through the existing heading/fallback substrate before deciding whether to extend that path or add a new sibling portionizer/recipe.
20260329-1015 — explored Story 171 buildability and refined the implementation gate: reviewed `docs/ideal.md`, `docs/spec.md` (`spec:1`, `spec:3`, `spec:6`, `spec:7`, `spec:8`), the relevant `docs/build-map.md` categories and input-coverage row, ADR-002, Stories 137/157/168/169/170, Scout 011, `modules/intake/intake_plan_utils.py`, `modules/portionize/portionize_headings_html_v1/main.py`, `modules/build/build_chapter_html_v1/main.py`, `tests/test_intake_plan_utils.py`, `tests/test_pdf_intake_recipe.py`, and `tests/test_build_chapter_html.py`. Fresh baseline checks passed: `pytest -q tests/test_intake_plan_utils.py tests/test_pdf_intake_recipe.py` => `7 passed in 2.73s`. Substrate verdict: the story is honestly buildable because the maintained extract lane, routing seam, heading-based portionizer, and builder fallback-page path all exist in code today; the missing slice is tight and local to the non-TOC bridge, because `portionize_headings_html_v1` still exits on zero headings and `build_chapter_html_v1` still exits on empty portions. Files likely to change remain the non-TOC recipe/routing/portionize/build/test/docs surfaces already listed in this story; files at highest risk are `modules/build/build_chapter_html_v1/main.py`, `docs/build-map.md`, and `docs/evals/registry.yaml` because they are already large truth surfaces. Pattern to follow: keep the TOC/book-like lane untouched, add the smallest explicit sibling path, and let bundle/provenance contracts stay inside existing `doc-web` build patterns rather than inventing a new output shape casually. Surprise found: the repo-owned proof surface is narrower than the product gap; `rg --files testdata | rg '\.pdf$'` shows only `testdata/tbotb-mini.pdf` and `testdata/scanned-prose-mini.pdf`, so there is still no shipped flat/non-TOC born-digital fixture. That means the implementation pass must either add a reproducible flat fixture/generator or keep the shipped maintained claim bounded to local validation assets instead of over-promoting the `born-digital-pdf` row. Next step: get approval on the implementation plan, then move the story to `In Progress` and run the real non-TOC baseline through `driver.py` before changing code.
20260329-1407 — implemented the maintained non-TOC born-digital lane and left repeatable proof: added `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`, taught `modules/portionize/portionize_headings_html_v1/main.py` an opt-in single-document fallback plus source-page-aware portions, taught `modules/build/build_chapter_html_v1/main.py` to consume source-page-based portions when printed page numbers are absent, updated `modules/intake/intake_plan_utils.py` so flat extractable born-digital PDFs can recommend the new explicit recipe while the book-like lane stays intact, and added the repo-owned reproducible fixture pair `testdata/flat-born-digital-mini.md` / `testdata/flat-born-digital-mini.pdf` plus generator `testdata/generate_flat_born_digital_fixture.py`. Fresh focused verification passed: `pytest -q tests/test_portionize_headings_html_v1.py tests/test_build_chapter_html.py tests/test_intake_plan_utils.py tests/test_pdf_intake_recipe.py` => `93 passed, 2 warnings`; full repo verification also passed: `make lint` => pass and `make test` => `388 passed, 12 warnings`. Fresh pipeline proof after clearing stale bytecode (`find modules/build modules/portionize modules/intake -name '*.pyc' -delete`) succeeded on the repo-owned fixture under `output/runs/story171-flat-fixture-r3/`, plus comparison reruns under `output/runs/story171-rfp-r2/` and `output/runs/story171-release-forms-r2/`. Manual artifact inspection confirms the new lane leaves real bundle/provenance outputs instead of stopping at portionization: `output/runs/story171-flat-fixture-r3/01_extract_pdf_marker_lite_html_v1/pages_html.jsonl` carries source-linked native-text HTML across 2 pages; `output/runs/story171-flat-fixture-r3/03_portionize_headings_html_v1/portions_non_toc.jsonl` emits 2 non-empty source-page-based portions (`Requested information:` on page 1, `Accessibility notes:` on page 2); `output/runs/story171-flat-fixture-r3/output/html/manifest.json` and `output/runs/story171-flat-fixture-r3/output/html/provenance/blocks.jsonl` show a 2-entry bundle with block-level page provenance. Comparison artifacts also validate the widened flat-PDF slice: `output/runs/story171-rfp-r2/output/html/manifest.json` is a single-document chapter over source pages `[1, 2]` with provenance rows starting from `REQUEST FOR PROPOSAL: WEBSITE DEVELOPMENT`, and `output/runs/story171-release-forms-r2/output/html/manifest.json` is a single-document chapter over source pages `[1, 2]` with provenance rows starting from `ACKNOWLEDGMENT OF RISK AND RELEASE OF LIABILITY (AR-0103)`. Eval surface changed and was refreshed honestly: the first rerun `benchmarks/results/auto-book-type-detection-story171-preupdate.json` dropped to `accuracy = 0.8` because only the corpus expectations were stale (**golden-wrong** for `rfp` and `release-forms`), then `benchmarks/results/auto-book-type-detection-story171.json` returned to `accuracy = 1.0`, `overall = 1.0`, `pass_rate = 1.0` after updating those locked expectations. Related truth surfaces are now aligned in `docs/build-map.md`, `tests/fixtures/formats/_coverage-matrix.json`, and `docs/evals/registry.yaml`. Residual risk: the lane is functionally maintained but still narrow; proof breadth is small and form-heavy outputs can surface oversized in-body headings from Marker extraction. Next step: `/validate`, then `/mark-story-done` if no further artifact-quality issues are found.
20260329-1508 — closed the validation-found honesty gap in the non-TOC bundle output: `modules/build/build_chapter_html_v1/main.py` now leaves `doc_web_bundle_manifest_v1.printed_page_start` / `printed_page_end` null when a flat document has no printed pages instead of copying source-page fallback values into printed-page fields, and the index page now suppresses fake `(p. N)` ranges for those unnumbered chapters. `tests/test_build_chapter_html.py` now asserts that source-page fallback chapters keep `printed_pages == []`, `printed_page_start is None`, `printed_page_end is None`, and that the index omits misleading printed-page labels. Fresh verification passed after the fix: `pytest -q tests/test_build_chapter_html.py` => `83 passed, 2 warnings`; `make lint` => pass; `make test` => `388 passed, 12 warnings`. Fresh real-pipeline proof also passed after clearing stale bytecode: `python driver.py --recipe configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml --run-id validate-story171-flat-r2 --force`. Manual artifact inspection on the fresh rerun confirms the bundle is now structurally and semantically honest: `output/runs/validate-story171-flat-r2/output/html/manifest.json` contains `printed_pages: []` with `printed_page_start: null` / `printed_page_end: null` for both entries, `output/runs/validate-story171-flat-r2/output/html/index.html` lists `Requested information:` and `Accessibility notes:` without fake `(p. 1)` / `(p. 2)` labels, and `output/runs/validate-story171-flat-r2/output/html/provenance/blocks.jsonl` still validates with page-linked provenance. Schema validation also passed on the fresh rerun via `python validate_artifact.py --schema doc_web_bundle_manifest_v1 --file output/runs/validate-story171-flat-r2/output/html/manifest.json` and `python validate_artifact.py --schema doc_web_provenance_block_v1 --file output/runs/validate-story171-flat-r2/output/html/provenance/blocks.jsonl`. Next step: `/mark-story-done`.
20260329-1907 — marked Story 171 done after fresh close-out validation. Current-state evidence passed in this close-out pass: `python -m ruff check modules/ tests/` => pass; `python -m pytest tests/` => `388 passed, 12 warnings`; and fresh real-pipeline proof via `python driver.py --recipe configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml --run-id finish-story171-flat-r1 --force`. Manual artifact inspection on `output/runs/finish-story171-flat-r1/output/html/manifest.json`, `output/runs/finish-story171-flat-r1/output/html/index.html`, and `output/runs/finish-story171-flat-r1/output/html/provenance/blocks.jsonl` confirms the maintained non-TOC lane now ships honest final bundle metadata (`printed_page_start` / `printed_page_end` null when no printed pages exist), clean contents output without fake printed-page labels, and validated page-linked provenance. Schema validation also passed on the same rerun via `python validate_artifact.py --schema doc_web_bundle_manifest_v1 --file output/runs/finish-story171-flat-r1/output/html/manifest.json` and `python validate_artifact.py --schema doc_web_provenance_block_v1 --file output/runs/finish-story171-flat-r1/output/html/provenance/blocks.jsonl`. Next step: `/check-in-diff`.
