# Story 157 — PDF Intake Parity with Image-Directory Inputs

**Priority**: High
**Status**: Pending
**Ideal Refs**: Requirement #1 (Ingest), Requirement #3 (Extract), Any format, any condition, Zero configuration, Minimum Viable Floor
**Spec Refs**: spec:1 (spec:1.1, C2), spec:2 (spec:2.1, spec:2.2), spec:7
**Build Map Refs**: Category 1 Intake & Format Routing (`partial`, `climb`); Category 2 OCR & Text Extraction (`exists`, C1 `climb`, C6 `hold`); Input Coverage rows `scanned-pdf-prose`, `scanned-pdf-tables`, `image-directory-scans`, `born-digital-pdf`. Current documented reality is inconsistent: `docs/build-map.md` lists a passing scanned-PDF prose path while `tests/fixtures/formats/_coverage-matrix.json` marks `scanned-pdf-prose` untested.
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/notes/repo-mission-alignment-cleanup-inventory.md`, `docs/RUNBOOK.md`, `docs/stories/story-084-fast-pdf-image-extraction.md`, `docs/stories/story-102-x-height-measurement-and-target-investigation.md`, `docs/stories/story-155-repo-mission-alignment-cleanup-and-legacy-surface-removal.md`
**Depends On**: Story 084, Story 102, Story 155, Story 156

## Goal

The active `doc-web` runtime path currently treats image directories as the maintained first-class input surface, while real PDF ingestion sits in an awkward middle state: the driver and extractors still support `input.pdf`, but the maintained recipes, run-manager defaults, and current verification lanes are image-first or fixture-reuse only. This story restores scanned-PDF intake as an equally maintained operator path so a user can point the runtime at a single PDF and reach the same `doc-web` bundle flow without manually pre-extracting images. It also makes the repo honest about what is and is not supported by adding durable PDF validation evidence and reconciling the current build-map versus coverage-matrix mismatch.

## Acceptance Criteria

- [ ] A maintained scanned-PDF intake path exists under `configs/recipes/` (not only under `configs/recipes/legacy/`) that starts from a single `input.pdf`, normalizes into the existing `page_image_v1` / `page_html_v1` contracts, and reaches the same structural HTML bundle path used by the maintained image-directory recipes.
- [ ] The maintained operator workflow makes running a PDF no harder than running an image directory:
  - a fresh run can be seeded from a single PDF path without manually pre-extracting page images
  - `tools/run_manager.py` or an equivalent maintained wrapper recognizes PDF-backed runs as a first-class case instead of always defaulting to image-directory recipes
  - the workflow stays within the current explicit-recipe compromise (`C2`) rather than introducing a vague hidden router
- [ ] The active Onward genealogy path has a maintained scanned-PDF entry surface as well:
  - either a dedicated maintained Onward PDF recipe exists
  - or the chosen parity implementation proves that the generic maintained PDF path can feed the existing Onward-specific downstream stages without loss of functionality
- [ ] Real pipeline verification is recorded for the shared Onward PDF at `/Users/cam/Documents/Projects/doc-web/input/Onward to the Unknown.pdf`:
  - a `driver.py` run produces artifacts under `output/runs/`
  - manual inspection is recorded for at least the PDF-to-page-image manifest, downstream page HTML, and final bundle outputs relevant to the chosen path
  - provenance still points back to the source PDF rather than silently degrading to image-only ancestry
- [ ] The repo has durable PDF smoke coverage that does not depend on the shared Onward asset:
  - reuse `testdata/tbotb-mini.pdf` if it is sufficient, or add another small checked-in PDF fixture
  - wire that fixture into an automated test or repo-owned smoke lane for maintained PDF intake
- [ ] Documentation and coverage truth are reconciled:
  - `README.md`, `docs/RUNBOOK.md`, `docs/build-map.md`, and `tests/fixtures/formats/_coverage-matrix.json` agree on scanned-PDF support
  - born-digital PDF remains explicitly separate and unclaimed until a native embedded-text path exists

## Out of Scope

- Solving born-digital PDF extraction or adding native embedded-text handling for `born-digital-pdf`
- Eliminating manual recipe selection across all formats or building a generalized auto-router beyond the current `C2` compromise
- Reworking OCR quality, table rescue, or illustration extraction beyond what is necessary to make maintained scanned-PDF intake reach the existing downstream path
- Committing the full Onward PDF into the repo if it remains available as a shared local validation asset
- Creating a new bundle schema if existing `page_image_v1`, `page_html_v1`, and `doc-web` bundle contracts remain sufficient

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

- [ ] Confirm the smallest viable parity surface:
  - test whether a maintained PDF recipe plus the existing `driver.py` / `RunConfig.input_pdf` substrate is sufficient
  - only add wrapper/helper behavior if recipe-only parity still leaves PDF materially harder to run than image directories
- [ ] Add a maintained scanned-PDF recipe surface under `configs/recipes/`:
  - generic scanned-PDF path for the active structural HTML bundle flow
  - Onward-specific scanned-PDF path if the genealogy stages still require a separate maintained entry surface
  - keep downstream artifact contracts aligned with the existing image-directory path
- [ ] Add operator UX parity for PDF-backed runs:
  - update `tools/run_manager.py` so it can seed or recognize PDF-first runs cleanly
  - add/update tests for generated config behavior and execution wiring
  - avoid reintroducing stale sample-book defaults
- [ ] Add durable PDF smoke coverage:
  - reuse `testdata/tbotb-mini.pdf` if suitable, or add a small checked-in PDF fixture
  - wire the fixture into an automated test or repo-owned smoke lane
  - keep the large shared Onward PDF as manual validation evidence, not as the only proof of support
- [ ] Run real pipeline validation:
  - clear stale `*.pyc`
  - run the maintained PDF path through `driver.py`
  - run a real Onward validation using `/Users/cam/Documents/Projects/doc-web/input/Onward to the Unknown.pdf`
  - verify artifacts in `output/runs/`
  - manually inspect representative `page_image_v1`, `page_html_v1`, and final bundle outputs
- [ ] Reconcile the documentation and coverage truth sources:
  - update `README.md`
  - update `docs/RUNBOOK.md`
  - update `docs/build-map.md`
  - update `tests/fixtures/formats/_coverage-matrix.json`
  - keep born-digital PDF explicitly separate until that path is truly built
- [ ] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [ ] Run required checks for touched scope:
  - [ ] Default Python checks: `make test`
  - [ ] Default Python lint: `make lint`
  - [ ] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL/HTML data
  - [ ] If agent tooling changed: `make skills-check`
- [ ] If evals or goldens changed materially: run `/improve-eval` and update `docs/evals/registry.yaml`
- [ ] Search all docs and update any related to what we touched
- [ ] Verify Central Tenets:
  - [ ] T0 — Traceability: PDF-backed outputs still trace to the source PDF and downstream page/block artifacts
  - [ ] T1 — AI-First: do not invent new deterministic routing logic where the existing OCR/runtime path already suffices
  - [ ] T2 — Eval Before Build: prove the recipe-only baseline before adding helper abstractions
  - [ ] T3 — Fidelity: PDF intake must preserve the same downstream text/layout quality bar as the maintained image path
  - [ ] T4 — Modular: extend the existing page-image normalization seam instead of creating PDF-only downstream contracts
  - [ ] T5 — Inspect Artifacts: inspect real outputs from maintained PDF runs, not just docs and unit tests

## Workflow Gates

- [ ] Build complete: implementation finished, required checks run, and summary shared
- [ ] Validation complete or explicitly skipped by user
- [ ] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: Intake and operator ergonomics. The owning surfaces are the maintained recipe set, the PDF-to-page-image normalization seam, `tools/run_manager.py`, and the docs/truth sources that define what the active runtime supports.
- **Build-map reality**: Category 1 remains `partial` / `climb` because format routing is still manual. Category 2 substrate already exists. The immediate gap is not missing OCR capability; it is that scanned-PDF entry is not maintained and verified at the same level as image-directory entry.
- **Substrate evidence**: Verified in code that `driver.py` injects `--pdf` for intake/extract stages and exposes `--input-pdf`; `schemas.py` already supports `RunConfig.input_pdf`; `modules/extract/extract_pdf_images_fast_v1` exists and is still live; `modules/intake/unstructured_pdf_intake_v1` exists but is not part of the maintained active path; the current maintained recipes are image-directory only; `tools/run_manager.py` still seeds `recipe-images-ocr-html-mvp.yaml`; the shared Onward PDF exists locally at `/Users/cam/Documents/Projects/doc-web/input/Onward to the Unknown.pdf`; this worktree currently has no local `input/` directory, so automated proof cannot rely on untracked local assets.
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
- This story should improve scanned-PDF parity only. The separate `born-digital-pdf` gap remains real and should stay documented as untested until embedded-text extraction is intentionally built.

## Plan

Pending — `/build-story` should first prove the recipe-only baseline using the existing `input_pdf` and `extract_pdf_images_fast_v1` substrate. If that already makes PDF runs operationally equivalent to image-directory runs, keep the change set to maintained recipes, operator docs, and verification surfaces. Only add run-manager helper behavior if the baseline still leaves meaningful operator friction. Implementation should finish by reconciling the repo’s truth sources so the shipped support level is documented honestly.

## Work Log

20260320-0940 — story created: scoped scanned-PDF intake parity as a maintained runtime gap, not a greenfield capability. Evidence: `driver.py` and `RunConfig` still support `input.pdf`, `extract_pdf_images_fast_v1` remains live, the maintained recipes and `tools/run_manager.py` are image-first, `docs/build-map.md` and `tests/fixtures/formats/_coverage-matrix.json` disagree about scanned-PDF support, and the shared Onward PDF exists locally at `/Users/cam/Documents/Projects/doc-web/input/Onward to the Unknown.pdf`. Next step: `/build-story` should prove the smallest viable parity path, add durable PDF verification, and reconcile the documented support surface.
