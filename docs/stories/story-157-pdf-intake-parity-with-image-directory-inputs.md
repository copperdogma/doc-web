---
title: PDF Intake Parity with Image-Directory Inputs
status: Done
priority: High
ideal_refs:
- 'Requirement #1 (Ingest), Requirement #3 (Extract), Any format, any condition, Zero
  configuration, Minimum Viable Floor'
spec_refs:
- spec:1
- spec:1.1
- spec:2
- spec:2.1
- spec:2.2
- spec:7
adr_refs: []
depends_on:
- 084
- '102'
- '155'
- '156'
category_refs:
- spec:1
- spec:2
- spec:7
compromise_refs:
- C1
- C2
- C6
input_coverage_refs:
- born-digital-pdf
- image-directory-scans
- scanned-pdf-prose
- scanned-pdf-tables
architecture_domains: []
roadmap_tags: []
legacy_system: ''
---

# Story 157 — PDF Intake Parity with Image-Directory Inputs

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #1 (Ingest), Requirement #3 (Extract), Any format, any condition, Zero configuration, Minimum Viable Floor
**Spec Refs**: spec:1 (spec:1.1, C2), spec:2 (spec:2.1, spec:2.2), spec:7
**Build Map Refs**: Category 1 Intake & Format Routing (`partial`, `climb`); Category 2 OCR & Text Extraction (`exists`, C1 `climb`, C6 `hold`); Input Coverage rows `scanned-pdf-prose` (`untested`), `scanned-pdf-tables` (`passing`), `image-directory-scans` (`passing`), `born-digital-pdf` (`has-fixture`)
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/notes/repo-mission-alignment-cleanup-inventory.md`, `docs/RUNBOOK.md`, `docs/stories/story-084-fast-pdf-image-extraction.md`, `docs/stories/story-102-x-height-measurement-and-target-investigation.md`, `docs/stories/story-155-repo-mission-alignment-cleanup-and-legacy-surface-removal.md`
**Depends On**: Story 084, Story 102, Story 155, Story 156

## Goal

The active `doc-web` runtime path currently treats image directories as the maintained first-class input surface, while real PDF ingestion sits in an awkward middle state: the driver and extractors still support `input.pdf`, but the maintained recipes, run-manager defaults, and current verification lanes are image-first or fixture-reuse only. This story restores scanned-PDF intake as an equally maintained operator path so a user can point the runtime at a single PDF and reach the same `doc-web` bundle flow without manually pre-extracting images. It also makes the repo honest about what is and is not supported by adding durable PDF validation evidence and reconciling the current build-map versus coverage-matrix mismatch.

## Acceptance Criteria

- [x] A maintained scanned-PDF intake path exists under `configs/recipes/` (not only under `configs/recipes/legacy/`) that starts from a single `input.pdf`, normalizes into the existing `page_image_v1` / `page_html_v1` contracts, and reaches the same structural HTML bundle path used by the maintained image-directory recipes.
- [x] The maintained operator workflow makes running a PDF no harder than running an image directory:
  - a fresh run can be seeded from a single PDF path without manually pre-extracting page images
  - `tools/run_manager.py` or an equivalent maintained wrapper recognizes PDF-backed runs as a first-class case instead of always defaulting to image-directory recipes
  - the workflow stays within the current explicit-recipe compromise (`C2`) rather than introducing a vague hidden router
- [x] The active Onward genealogy path has a maintained scanned-PDF entry surface as well:
  - either a dedicated maintained Onward PDF recipe exists
  - or the chosen parity implementation proves that the generic maintained PDF path can feed the existing Onward-specific downstream stages without loss of functionality
- [x] Real pipeline verification is recorded for the shared Onward PDF at `/Users/cam/Documents/Projects/doc-web/input/Onward to the Unknown.pdf`:
  - a `driver.py` run produces artifacts under `output/runs/`
  - manual inspection is recorded for at least the PDF-to-page-image manifest, downstream page HTML, and final bundle outputs relevant to the chosen path
  - provenance still points back to the source PDF rather than silently degrading to image-only ancestry
- [x] The repo has durable PDF smoke coverage that does not depend on the shared Onward asset:
  - reuse `testdata/tbotb-mini.pdf` if it is sufficient, or add another small checked-in PDF fixture
  - wire that fixture into an automated test or repo-owned smoke lane for maintained PDF intake
- [x] Documentation and coverage truth are reconciled:
  - `README.md`, `docs/RUNBOOK.md`, `docs/build-map.md`, and `tests/fixtures/formats/_coverage-matrix.json` agree on scanned-PDF support
  - born-digital PDF remains explicitly separate and unclaimed until a native embedded-text path exists

## Out of Scope

- Solving born-digital PDF extraction or adding native embedded-text handling for `born-digital-pdf`
- Eliminating manual recipe selection across all formats or building a generalized auto-router beyond the current `C2` compromise
- Reworking OCR quality, table rescue, or illustration extraction beyond what is necessary to make maintained scanned-PDF intake reach the existing downstream path
- Committing the full Onward PDF into the repo if it remains available as a shared local validation asset
- Creating a new bundle schema if existing `page_image_v1`, `page_html_v1`, and `doc-web` bundle contracts remain sufficient

## Post-Validation Scope Expansion

Validation on 2026-03-27 showed that the core PDF-intake parity work is done, but it also exposed two tightly coupled issues in the exact run used to prove the story:

- `driver.py` leaves a stale top-level `status_reason` in `pipeline_state.json` after a later successful resume, which makes the validated PDF run look partially failed even when downstream artifacts are complete.
- The maintained Onward PDF lane still ends with 3 genealogy-consistency warnings (`chapter-010.html`, `chapter-011.html`, `chapter-015.html`) and 6 strong rerun candidate pages in the same real validation run.

These were folded into Story 157 because they directly affected the honesty and quality of the story's proof run. The third validation recommendation, repo-owned `scanned-pdf-prose` fixture coverage, was later split into Story 167 because it is format-coverage follow-up work rather than a blocker on maintained PDF-entry parity.

## Approach Evaluation

- **Simplification baseline**: First prove whether the existing substrate is already enough: `driver.py` accepts `input.pdf`, `RunConfig` already supports `input_pdf`, and `extract_pdf_images_fast_v1` already emits `page_image_v1`. If a maintained PDF recipe plus minor operator/docs updates is sufficient, do not add a new intake abstraction.
- **AI-only**: Not a fit. This problem is primarily operator plumbing, recipe maintenance, and verification surface. An LLM cannot replace the need for executable PDF entry points or honest coverage evidence.
- **Hybrid**: Keep recipe selection explicit, but add a thin helper in `tools/run_manager.py` or run-config generation so operators can hand it a PDF path and get the correct maintained recipe/config with minimal friction. This is viable if recipe-only parity still leaves PDF noticeably harder to run than images.
- **Pure code**: Add one or more maintained PDF recipes that reuse the current downstream image-based stages after a PDF-to-page-image normalization stage. This is the leading candidate if it achieves parity without introducing another routing layer.
- **Repo constraints / prior decisions**: `spec:1.1` explicitly prefers keeping the recipe surface explicit while expanding input coverage one format family at a time. Story 155 intentionally removed FF-era sample-PDF defaults and kept the active recipes image-first. ADR-002 settled the runtime boundary but did not settle scanned-PDF operator parity inside this repo.
- **Existing patterns to reuse**: `modules/extract/extract_pdf_images_fast_v1`, `configs/recipes/recipe-images-ocr-html-mvp.yaml`, `configs/recipes/recipe-onward-images-html-mvp.yaml`, `driver.py --input-pdf`, `schemas.RunConfig.input_pdf`, `testdata/tbotb-mini.pdf`, and the provenance expectations already enforced in the active bundle path.
- **Eval**: The deciding proof is operational, not prompt-based:
  - Can a fresh operator start from a single PDF path and reach the maintained bundle path with no manual PDF-to-image pre-step?
  - Does a real Onward PDF run produce the same downstream artifact classes as the image-backed path?
  - Does the repo retain a durable automated or cheap smoke lane for PDF intake afterward?
  If the recipe-only baseline passes all three, additional routing/helper work is unnecessary.

## Tasks

- [x] Confirm the smallest viable parity surface:
  - test whether a maintained PDF recipe plus the existing `driver.py` / `RunConfig.input_pdf` substrate is sufficient
  - only add wrapper/helper behavior if recipe-only parity still leaves PDF materially harder to run than image directories
- [x] Add a maintained scanned-PDF recipe surface under `configs/recipes/`:
  - generic scanned-PDF path for the active structural HTML bundle flow
  - Onward-specific scanned-PDF path if the genealogy stages still require a separate maintained entry surface
  - keep downstream artifact contracts aligned with the existing image-directory path
- [x] Add operator UX parity for PDF-backed runs:
  - update `tools/run_manager.py` so it can seed or recognize PDF-first runs cleanly
  - add/update tests for generated config behavior and execution wiring
  - avoid reintroducing stale sample-book defaults
- [x] Add durable PDF smoke coverage:
  - reuse `testdata/tbotb-mini.pdf` if suitable, or add a small checked-in PDF fixture
  - wire the fixture into an automated test or repo-owned smoke lane
  - keep the large shared Onward PDF as manual validation evidence, not as the only proof of support
- [x] Run real pipeline validation:
  - clear stale `*.pyc`
  - run the maintained PDF path through `driver.py`
  - run a real Onward validation using `/Users/cam/Documents/Projects/doc-web/input/Onward to the Unknown.pdf`
  - verify artifacts in `output/runs/`
  - manually inspect representative `page_image_v1`, `page_html_v1`, and final bundle outputs
- [x] Reconcile the documentation and coverage truth sources:
  - update `README.md`
  - update `docs/RUNBOOK.md`
  - update `docs/build-map.md`
  - update `tests/fixtures/formats/_coverage-matrix.json`
  - keep born-digital PDF explicitly separate until that path is truly built
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL/HTML data
  - [x] If agent tooling changed: not applicable in this story; no agent tooling changed
- [x] If evals or goldens changed materially: not applicable in this story; evals and goldens were unchanged
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: PDF-backed outputs still trace to the source PDF and downstream page/block artifacts
  - [x] T1 — AI-First: do not invent new deterministic routing logic where the existing OCR/runtime path already suffices
  - [x] T2 — Eval Before Build: prove the recipe-only baseline before adding helper abstractions
  - [x] T3 — Fidelity: PDF intake must preserve the same downstream text/layout quality bar as the maintained image path
  - [x] T4 — Modular: extend the existing page-image normalization seam instead of creating PDF-only downstream contracts
  - [x] T5 — Inspect Artifacts: inspect real outputs from maintained PDF runs, not just docs and unit tests
- [x] Clear stale resume status at the run level:
  - reproduce and fix the `pipeline_state.json` case where a previous failed attempt leaves `status_reason` behind after a successful resume
  - add a focused regression test in the `driver.py` test surface
- [x] Reduce or clearly explain the remaining Onward genealogy warnings from the maintained PDF proof run:
  - inspect the flagged chapter/page artifacts from `story157-onward-pdf-parity`
  - reuse existing rerun or consistency-planning substrate before inventing a new repair path
  - either land a measurable reduction in flagged chapters/pages or record fresh evidence for why the detector, not the extraction, is the remaining problem
- [x] Split the repo-owned scanned-prose coverage gap into Story 167:
  - verified `testdata/tbotb-mini.pdf` remains born-digital smoke only and is not honest `scanned-pdf-prose` evidence
  - follow-up fixture/proof work now lives in `docs/stories/story-167-repo-owned-scanned-prose-pdf-fixture.md`

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: Intake and operator ergonomics. The owning surfaces are the maintained recipe set, the PDF-to-page-image normalization seam, `tools/run_manager.py`, and the docs/truth sources that define what the active runtime supports.
- **Build-map reality**: Category 1 remains `partial` / `climb` because format routing is still manual. Category 2 substrate already exists. The immediate gap is not missing OCR capability; it is that scanned-PDF entry is not maintained and verified at the same level as image-directory entry.
- **Substrate evidence**: Verified in code and artifacts that `driver.py` injects `--pdf` for intake/extract stages and exposes `--input-pdf`; `schemas.py` supports `RunConfig.input_pdf`; `modules/extract/extract_pdf_images_fast_v1` emits the maintained `page_image_v1` seam; `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` and `configs/recipes/recipe-onward-pdf-html-mvp.yaml` are now maintained entry recipes; `tools/run_manager.py` can seed PDF-backed runs explicitly; the shared Onward PDF exists locally at `/Users/cam/Documents/Projects/doc-web/input/Onward to the Unknown.pdf`; this worktree still has no tracked `input/` directory, so repo-owned smoke lanes must rely on checked-in fixtures.
- **Data contracts / schemas**: No new downstream schema is expected if scanned-PDF intake normalizes to the existing `page_image_v1` and `page_html_v1` contracts. If new fields are needed for provenance or config/state propagation, they must be added to `schemas.py` before code emits them.
- **File sizes**: `driver.py` is 2171 lines and `modules/extract/extract_pdf_images_fast_v1/main.py` is 661 lines, so this story should avoid unnecessary edits there unless the existing substrate proves insufficient. `modules/intake/unstructured_pdf_intake_v1/main.py` is 344 lines, `tools/run_manager.py` is 110 lines, `tests/test_run_manager.py` is 66 lines, `configs/recipes/recipe-images-ocr-html-mvp.yaml` is 87 lines, `configs/recipes/recipe-onward-images-html-mvp.yaml` is 192 lines, `tests/fixtures/formats/_coverage-matrix.json` is 301 lines, `README.md` is 141 lines, `docs/build-map.md` is 461 lines, and `docs/RUNBOOK.md` is 206 lines.
- **Decision context**: Reviewed `docs/ideal.md`, `docs/spec.md`, `docs/build-map.md`, ADR-002, the mission-alignment cleanup inventory, and the active runbook. No newer ADR specifically on scanned-PDF parity was found. A new ADR is not needed if the solution stays within the existing recipe-plus-normalization model; create one only if the work expands into a new generic input contract or a broader routing architecture change.

## Files to Modify

- `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` — maintained generic scanned-PDF intake path for the active bundle flow (new file)
- `configs/recipes/recipe-onward-pdf-html-mvp.yaml` — maintained Onward scanned-PDF entry path if a specialized genealogy branch is still required (new file)
- `configs/recipes/recipe-images-ocr-html-mvp.yaml` — keep shared downstream stages aligned if common recipe fragments or conventions are extracted (87 lines)
- `configs/recipes/recipe-onward-images-html-mvp.yaml` — keep the image-backed Onward path aligned with any maintained PDF sibling path (192 lines)
- `tools/run_manager.py` — first-class PDF-backed run generation or dispatch parity (110 lines)
- `tests/test_run_manager.py` — PDF-aware run-manager coverage (66 lines)
- `testdata/README.md` — document the repo-owned PDF smoke fixture and its intended use relative to the shared Onward PDF (7 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — honest scanned-PDF versus image-directory coverage and measured evidence (301 lines)
- `docs/build-map.md` — reconcile input-coverage rows with shipped behavior (461 lines)
- `docs/RUNBOOK.md` — publish maintained PDF commands and smoke guidance (206 lines)
- `README.md` — make maintained scanned-PDF support explicit and current (141 lines)
- `driver.py` — only if the existing `input_pdf` plumbing proves insufficient for maintained parity (2171 lines)
- `modules/extract/extract_pdf_images_fast_v1/main.py` — only if maintained PDF runs expose page-image manifest or provenance gaps (661 lines)

## Redundancy / Removal Targets

- Any docs that still imply the active runtime only supports image-directory intake while separately claiming scanned-PDF support elsewhere
- Any run-manager defaults or sample configs that force operators toward image-directory inputs when a single PDF would suffice
- Any temporary or story-scoped PDF recipe variants that duplicate the maintained path without adding a distinct document-family need
- The current build-map versus coverage-matrix mismatch once the shipped behavior is verified

## Notes

- Verified local validation asset exists at `/Users/cam/Documents/Projects/doc-web/input/Onward to the Unknown.pdf`.
- Verified current worktree does not contain a tracked local `input/` directory, so automated tests and committed smoke lanes must rely on repo-owned fixtures rather than untracked shared inputs.
- Existing repo-owned PDF fixture candidate: `testdata/tbotb-mini.pdf` (documented in `testdata/README.md`).
- `testdata/tbotb-mini.pdf` is suitable for repo-owned PDF-entry smoke because it is a small checked-in PDF, but it is not evidence that `scanned-pdf-prose` is passing; it is a born-digital PDF routed through the OCR path.
- A handwritten journal/diary PDF would exercise the separate `handwritten-notes` coverage row, which remains untested today. That is a good follow-up fixture hunt, but it should not silently expand this story beyond scanned-PDF parity.
- This story should improve scanned-PDF parity only. The separate `born-digital-pdf` gap remains real and should stay documented as untested until embedded-text extraction is intentionally built.

## Plan

Completed — this story landed the maintained generic and Onward PDF entry recipes, PDF-aware run seeding, repo-owned PDF-entry smoke coverage, real Onward PDF artifact verification, and the two tightly coupled proof-run fixes discovered during validation. The remaining scanned-prose fixture gap was intentionally split into Story 167 so this story closes on the shipped maintained-PDF parity slice.

## Work Log

20260320-0940 — story created: scoped scanned-PDF intake parity as a maintained runtime gap, not a greenfield capability. Evidence: `driver.py` and `RunConfig` still support `input.pdf`, `extract_pdf_images_fast_v1` remains live, the maintained recipes and `tools/run_manager.py` are image-first, `docs/build-map.md` and `tests/fixtures/formats/_coverage-matrix.json` disagree about scanned-PDF support, and the shared Onward PDF exists locally at `/Users/cam/Documents/Projects/doc-web/input/Onward to the Unknown.pdf`. Next step: `/build-story` should prove the smallest viable parity path, add durable PDF verification, and reconcile the documented support surface.
20260326-0830 — exploration + planning: verified this story closes a real Ideal gap in Category 1 (`partial`, `climb`) rather than optimizing a dead-end compromise. Reviewed `docs/ideal.md`, `docs/spec.md` (`spec:1.1`, `spec:2.1`, `spec:2.2`, `spec:7`), `docs/build-map.md`, ADR-002, the repo mission-alignment notes, `docs/RUNBOOK.md`, and dependency Stories 084/102/155/156. Critical substrate verified in code: `schemas.RunConfig` already supports `input_pdf`; `driver.py` already exposes `--input-pdf` and injects `--pdf` into extract/intake stages; `modules/extract/extract_pdf_images_fast_v1` exists and emits the maintained `page_image_v1` seam. Critical missing slice also verified in code: the maintained recipes are still image-directory only, `tools/run_manager.py` always seeds `recipe-images-ocr-html-mvp.yaml`, and `tests/test_run_manager.py` currently asserts that image-only default. Baseline evidence: `python -m pytest tests/test_run_manager.py -q` passes (`2 passed in 1.42s`), while forcing `--input-pdf testdata/tbotb-mini.pdf` through `configs/recipes/recipe-images-ocr-html-mvp.yaml` fails immediately because `modules/extract/images_dir_to_manifest_v1/main.py` does not accept `--pdf` (`unrecognized arguments: --pdf testdata/tbotb-mini.pdf`). Relevant input-coverage rows checked: `scanned-pdf-prose` is still `untested` in `_coverage-matrix.json`, `image-directory-scans` is `passing`, `born-digital-pdf` is still `untested`, and `handwritten-notes` is also `untested`; this confirms the current build-map `scanned-pdf-prose` passing row is overstated. Patterns to follow: reuse maintained image-path downstream stages and only swap the PDF-to-page-image intake seam; keep recipe selection explicit per `spec:1.1`; use the shared Onward PDF for real scanned-PDF validation and `testdata/tbotb-mini.pdf` only for cheap repo-owned smoke wiring. Surprise found: the repo already has most of the substrate needed for PDF parity, but the maintained path is blocked by a single honest mismatch between driver-level PDF plumbing and image-only maintained recipes. Next step: wait for approval, then implement maintained PDF recipes, explicit run-manager PDF config support, smoke coverage, and truth-source reconciliation.
20260327-0205 — implementation + verification: shipped maintained PDF-entry parity without adding a hidden router. Added `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` and `configs/recipes/recipe-onward-pdf-html-mvp.yaml`, updated `tools/run_manager.py` so `create-run --pdf <file>` seeds `input_pdf` plus the maintained PDF recipe explicitly, and extended `tests/test_run_manager.py` with PDF config coverage. Added durable repo-owned smoke coverage in `tests/test_pdf_intake_recipe.py` using `testdata/tbotb-mini.pdf`; `python -m pytest tests/test_pdf_intake_recipe.py tests/test_run_manager.py tests/test_portionize_toc_html.py -q` passed (`6 passed in 4.59s`), then repo-wide checks passed with `make lint` and `make test` (`370 passed, 12 warnings in 37.24s`). Real pipeline proof came from `python driver.py --recipe configs/recipes/recipe-onward-pdf-html-mvp.yaml --input-pdf "/Users/cam/Documents/Projects/doc-web/input/Onward to the Unknown.pdf" --run-id story157-onward-pdf-parity --output-dir output/runs/story157-onward-pdf-parity --allow-run-id-reuse --start-from portionize_toc --force` after the initial full run exposed two real integration gaps: the PDF recipe needed `pdf_to_images.params.out: pages_images_manifest.jsonl` to match the maintained contract, and `modules/portionize/portionize_toc_html_v1/main.py` needed generic TOC detection widened from `<p>`-only content to heading-plus-table index pages. Manual artifact inspection: `output/runs/story157-onward-pdf-parity/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl` contains 127 rows with `source` pointing back to `/Users/cam/Documents/Projects/doc-web/input/Onward to the Unknown.pdf`; `output/runs/story157-onward-pdf-parity/02_ocr_ai_gpt51_v1/pages_html.jsonl` preserves real content such as the cover title on page 1, table HTML on pages 24 and 89, and plaque text on page 127; `output/runs/story157-onward-pdf-parity/05_extract_page_numbers_html_v1/pages_html_with_page_numbers.jsonl` now keeps the page-8 `<h1>INDEX</h1>` plus table TOC content parseable; `output/runs/story157-onward-pdf-parity/03_crop_illustrations_guided_v1/illustration_manifest.jsonl` contains 41 illustrations with page-linked provenance; `output/runs/story157-onward-pdf-parity/09_build_chapter_html_v1/chapters_manifest.jsonl` produced 35 entries backing `output/runs/story157-onward-pdf-parity/output/html/` (26 chapter files, 9 page files), and sampled outputs `chapter-001.html`, `chapter-002.html`, and `index.html` render expected titles. Coverage truth reconciled in `README.md`, `docs/RUNBOOK.md`, `docs/build-map.md`, `tests/fixtures/formats/_coverage-matrix.json`, and `testdata/README.md`: the repo now documents maintained scanned-PDF entry honestly, keeps `born-digital-pdf` separate, and stops overstating `scanned-pdf-prose` as passing. Impact: Story-scope acceptance criteria for maintained PDF recipes, operator parity, repo-owned smoke coverage, real Onward PDF validation, and doc/coverage reconciliation are now met. Pipeline-scope impact: a single PDF can enter the maintained bundle path with preserved provenance, and the real Onward PDF path uncovered and fixed a generic TOC detection bug that also benefits image-backed runs. Remaining note: `output/runs/story157-onward-pdf-parity/10_validate_onward_genealogy_consistency_v1/genealogy_consistency_report.jsonl` still flags 3 genealogy chapters (`chapter-010.html`, `chapter-011.html`, `chapter-015.html`) with 6 strong rerun candidate pages; that is downstream quality debt, not a PDF-entry plumbing failure. Also observed: `pipeline_state.json` ends with `status: done` but keeps a stale `status_reason` from the earlier failed portionize attempt after resume. Next step: run `/validate` for an independent close-out pass, then `/mark-story-done` if validation agrees.
20260327-0335 — validation follow-ups folded into Story 157 by user request. Added three new tasks to this story instead of splitting them out immediately: (1) fix the stale run-level `status_reason` left behind after a successful resume, because it makes the story's proof run look partially failed; (2) inspect and reduce the remaining genealogy-consistency warnings in the maintained Onward PDF proof run using the existing rerun substrate; (3) tighten the repo-owned `scanned-pdf-prose` fixture story so the current "maintained entry exists but prose is still unproven" state has a concrete closure path. Fresh evidence gathered before new edits: `make lint` and `make test` both passed again during `/validate`; `story157-onward-pdf-parity/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl` still shows 127 PDF-backed rows; `story157-onward-pdf-parity/output/html/chapter-010.html`, `chapter-011.html`, and `chapter-015.html` still contain family headings rendered outside the normalized subgroup-row pattern; and `story157-onward-pdf-parity/10_validate_onward_genealogy_consistency_v1/genealogy_consistency_detail.json` confirms the strongest remaining source-page culprits are pages 26, 30, 33, 34, 35, and 64. Next step: land the focused driver-state fix first, then run a targeted genealogy rerun loop against those pages and inspect whether the warnings drop enough to close the proof run cleanly.
20260327-0406 — driver-state follow-up landed and the maintained proof run is now honest after resume. Added `finalize_run_state(...)` in `driver.py` so successful completions clear stale top-level `status_reason` while preserving explicit validation-failure markers when needed, and added focused regression coverage in `tests/driver_resume_test.py`. Fresh check: `python -m pytest tests/driver_resume_test.py -q` passed (`4 passed in 0.53s`). Real-run verification: reran the maintained Onward PDF proof from `build_chapters` with `python driver.py --recipe configs/recipes/recipe-onward-pdf-html-mvp.yaml --input-pdf "/Users/cam/Documents/Projects/doc-web/input/Onward to the Unknown.pdf" --run-id story157-onward-pdf-parity --output-dir output/runs/story157-onward-pdf-parity --allow-run-id-reuse --start-from build_chapters --force` after clearing stale `*.pyc`. Manual artifact inspection: `output/runs/story157-onward-pdf-parity/pipeline_state.json` now ends with `status: "done"` and `status_reason: null`; `output/runs/story157-onward-pdf-parity/10_validate_onward_genealogy_consistency_v1/genealogy_consistency_report.jsonl` dropped from 3 flagged chapters / 6 strong rerun pages to 1 flagged chapter (`chapter-015.html`) / 1 strong rerun page (`64`) after the shared genealogy HTML normalization fixes already landed in this story. Impact: the story's proof run no longer misreports a stale failure state, and the residual genealogy problem is narrowed to a single chapter before any targeted rerun work.
20260327-0414 — story-scoped genealogy proof rerun cleared the last residual warning through `driver.py`, not just a scratch script. Added `configs/recipes/story-157-onward-pdf-genealogy-reruns-validate.yaml` to reuse the maintained PDF proof artifacts, rerun only the remaining flagged chapter's coarse suspect pages, rebuild chapters, and revalidate. Fresh real run: `python driver.py --recipe configs/recipes/story-157-onward-pdf-genealogy-reruns-validate.yaml --run-id story157-onward-pdf-rerun-r1 --force` completed successfully. Manual artifact inspection: `output/runs/story157-onward-pdf-rerun-r1/05_rerun_onward_genealogy_consistency_v1/rerun_onward_genealogy_summary.json` targeted only pages `62`, `63`, and `64` and accepted all 3; `output/runs/story157-onward-pdf-rerun-r1/07_validate_onward_genealogy_consistency_v1/genealogy_consistency_report_after_rerun.jsonl` now reports `flagged_genealogy_chapters: 0`; `output/runs/story157-onward-pdf-rerun-r1/output/html/chapter-015.html` now contains only the chapter-level `h1` titles and no loose family-heading `h3` blocks, while the rebuilt chapter still carries the expected genealogy tables. Fresh repo checks also passed after these code changes: `make lint` (`ruff check` clean) and `make test` (`375 passed, 12 warnings in 808.72s`). Remaining open scope: repo-owned `scanned-pdf-prose` coverage is still not solved; current evidence shows `testdata/tbotb-mini.pdf` remains born-digital smoke only, so the honest next closure path is a tiny checked-in rasterized prose PDF fixture rather than promoting the current fixture beyond what it proves.
20260327-1530 — rescope-and-close applied after fresh validation. Story 157's original acceptance criteria and the two tightly coupled proof-run follow-ups are complete on current-pass evidence: `make lint` passed, `make test` passed (`375 passed, 12 warnings in 1161.06s`), `output/runs/story157-onward-pdf-parity/pipeline_state.json` now ends `status: "done"` with `status_reason: null`, and the story-scoped rerun report at `output/runs/story157-onward-pdf-rerun-r1/07_validate_onward_genealogy_consistency_v1/genealogy_consistency_report_after_rerun.jsonl` reports `flagged_genealogy_chapters: 0`. The remaining scanned-prose fixture gap was split into Story 167 (`docs/stories/story-167-repo-owned-scanned-prose-pdf-fixture.md`) so this story can close on the shipped maintained PDF-entry slice without weakening its documented scope. Next step: `/check-in-diff`.
