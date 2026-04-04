---
title: Restore Maintained Contact-Sheet Intake and Benchmark Auto Book-Type Detection
status: Done
priority: High
ideal_refs:
- 'Requirement #1 (Ingest), Requirement #2 (Detect), Zero configuration, Any format,
  any condition, Minimum Viable Floor'
spec_refs:
- spec:1
- spec:1.1
- spec:8
adr_refs: []
depends_on:
- '027'
- '157'
- '167'
- '168'
category_refs:
- spec:1
- spec:8
compromise_refs:
- B1
- B2
- C2
input_coverage_refs:
- born-digital-pdf
- image-directory-scans
- scanned-pdf-prose
- scanned-pdf-tables
architecture_domains: []
roadmap_tags: []
legacy_system: ''
---

# Story 169 — Restore Maintained Contact-Sheet Intake and Benchmark Auto Book-Type Detection

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #1 (Ingest), Requirement #2 (Detect), Zero configuration, Any format, any condition, Minimum Viable Floor
**Spec Refs**: spec:1 (spec:1.1, C2), spec:8 (B1, B2)
**Build Map Refs**: Category 1 Intake & Format Routing (`exists`, C2 `climb`); Category 8 AI Harnesses & Tooling (`exists`, B1 `hold`, B2 `hold`); Input Coverage rows `scanned-pdf-prose` (`passing`), `scanned-pdf-tables` (`passing`), `image-directory-scans` (`passing`), `born-digital-pdf` (`has fixture`)
**Decision Refs**: `docs/stories/story-011-ai-planner.md`, `docs/stories/story-027-contact-sheet-auto-intake.md`, `docs/stories/story-157-pdf-intake-parity-with-image-directory-inputs.md`, `docs/stories/story-168-marker-lite-maintained-born-digital-pdf-path.md`, `docs/scout/scout-011-external-document-ingestion-systems.md`, `None found after search in docs/decisions/ for intake-routing-specific ADRs`
**Depends On**: Story 027, Story 157, Story 167, Story 168

## Goal

Restore the contact-sheet intake path as a maintained active recipe instead of a legacy-only side lane, then turn `C2` from a planning claim into measured evidence by adding the first honest `auto-book-type-detection` benchmark. The work should keep the current explicit-recipe compromise intact: intake may recommend a recipe and surface capability gaps, but it must not silently dispatch downstream runs or reopen the rejected Story 011 planner direction.

## Acceptance Criteria

- [x] A maintained `configs/recipes/recipe-intake-contact-sheet.yaml` exists under active recipes, not only under `configs/recipes/legacy/`, and it ends at plan emission / confirmation rather than downstream dispatch.
- [x] The maintained intake chain runs through `driver.py` and writes valid `contact_sheet_manifest_v1` plus `intake_plan_v1` artifacts under `output/runs/` for at least:
  - one image-directory input
  - one scanned PDF input
  - the repo-owned `born-digital-pdf` fixture `testdata/tbotb-mini.pdf`
- [x] The current intake modules no longer rely on stale placeholder behavior:
  - `contact_sheet_overview_v1` no longer defaults to obsolete model choices or a fallback shape that collapses to `"mixed"` without scoring intent
  - `zoom_refine_v1` no longer recommends nonexistent or legacy placeholder recipes
  - the chain remains recommendation-only and does not auto-dispatch downstream recipes
- [x] A real benchmark surface exists for `auto-book-type-detection` with 10 documents and no metadata hints, scoring at least:
  - detected document family / book type
  - recommended maintained explicit recipe or `no-recipe-needed` outcome
  - major signal detection where that affects recipe choice
- [x] `docs/evals/registry.yaml` records the first `auto-book-type-detection` score and attempt history, and `docs/build-map.md` reflects the real maintained C2 substrate / benchmark state after the story lands.
- [x] Manual artifact inspection is recorded for at least one maintained intake run and one benchmark sample set, with the checked artifact paths named in the work log.

## Out of Scope

- Auto-running downstream recipes or reviving the Story 011 planner / dispatch direction
- Hidden routing that replaces the current explicit-recipe operator workflow
- Building new converters for `docx`, `xlsx`, `pptx`, `email`, `web-page`, or `mixed-archive`
- Solving general mixed-archive unpacking or multi-document archive routing
- Deleting `C2` outright unless the new benchmark actually proves the gate

## Approach Evaluation

- **Simplification baseline**: first measure the current intake chain as-is on a 10-document corpus. If the current contact-sheet prompts already classify and recommend the right explicit recipe with acceptable accuracy, the story should collapse to maintained-recipe restoration, benchmark wiring, and docs cleanup.
- **AI-only**: benchmark the existing overview / zoom LLM chain on contact sheets alone and use prompt / model changes if they already clear most of the gap. This is plausible because `C2` is fundamentally an AI-capability question, but it still needs deterministic artifact plumbing and scoring.
- **Hybrid**: likely best fit. Keep deterministic contact-sheet generation, manifest normalization, and benchmark scoring in code; let multimodal models classify from the contact sheets and optional zoom pages; keep the output as an inspectable `intake_plan_v1`.
- **Pure code**: only appropriate for recipe restoration, scorer construction, and docs / registry reconciliation. It is not enough for the document-family classification itself.
- **Repo constraints / prior decisions**: Story 011 explicitly rejects auto-planning / dispatch as a product concern that belongs in Dossier, not doc-forge. Story 027 landed the substrate but drifted into legacy-only recipe wiring. Stories 157 and 168 widened the maintained input families, which makes a 10-document C2 benchmark more meaningful now than when Story 027 was closed. Scout 011 still calls `contact_sheet_overview_v1` a stub, so this story should assume the current surface is not yet honest proof.
- **Existing patterns to reuse**: `configs/recipes/legacy/recipe-intake-contact-sheet.yaml`, `modules/intake/contact_sheet_builder_v1`, `modules/intake/contact_sheet_overview_v1`, `modules/intake/zoom_refine_v1`, `modules/intake/gap_analyzer_v1`, `modules/intake/tests/test_intake_chain.py`, `modules/intake/tests/test_intake_chain_e2e.py`, the schema/validator hooks in `schemas.py` and `validate_artifact.py`, and the maintained PDF-entry patterns from Story 157 / Story 168.
- **Eval**: the story must choose and implement the smallest honest benchmark surface for `auto-book-type-detection`:
  - either a promptfoo task over the contact-sheet prompts
  - or a repo-owned harness that runs the maintained intake recipe and scores the final `intake_plan_v1`
  The deciding metric is benchmark honesty, not tool preference.

## Tasks

- [x] Reproduce the current C2 baseline on a 10-document corpus and record exact failure modes before changing code:
  - missing maintained recipe path
  - wrong `book_type` / `recommended_recipe`
  - legacy or nonexistent recipe suggestions
  - missing or misleading `signal_evidence`
- [x] Add a maintained `configs/recipes/recipe-intake-contact-sheet.yaml` under active recipes and keep the chain recommendation-only:
  - `contact_sheet_builder_v1`
  - `contact_sheet_overview_v1`
  - `zoom_refine_v1`
  - `gap_analyzer_v1`
  - `confirm_plan_v1`
- [x] Reconcile module defaults and outputs with the current mission:
  - remove legacy placeholder recipe suggestions from `zoom_refine_v1`
  - update stale model defaults where needed
  - keep output focused on explicit recipe recommendation and gap surfacing, not dispatch
- [x] Repair the current intake test surface so it proves the maintained lane honestly:
  - stop relying on the missing repo-local `input/onward-to-the-unknown-images`
  - remove dispatch-era expectations from `modules/intake/tests/test_intake_chain_e2e.py`
  - assert recommendation-only maintained behavior instead of nonexistent genealogy recipe dispatch
- [x] Decide and implement the smallest honest `auto-book-type-detection` benchmark surface:
  - curate 10 documents with expected document family / recipe outcomes
  - add scorer + golden expectations
  - document why the chosen eval surface is the honest one for C2
- [x] Run the chosen `auto-book-type-detection` harness and update `docs/evals/registry.yaml` with the first score, attempt log, and retry conditions.
- [x] Run real `driver.py` intake verification on representative maintained inputs:
  - one image-directory input
  - one scanned PDF input
  - `testdata/tbotb-mini.pdf`
  - inspect generated contact sheets and final `intake_plan_v1` artifacts under `output/runs/`
- [x] Update stale truth surfaces:
  - `docs/stories/story-027-contact-sheet-auto-intake.md`
  - `docs/build-map.md`
  - `docs/stories.md`
  - any runbook or README references that still point to the missing active recipe or imply dispatch behavior
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up.
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [x] If agent tooling changed: `make skills-check` (not required; agent tooling did not change in this story)
- [x] Search all docs and update any related to what we touched.
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every intake recommendation still traces to contact-sheet tiles, source images/pages, and emitted `signal_evidence`
  - [x] T1 — AI-First: use multimodal classification where it is the real capability question; do not replace it with brittle rule routing
  - [x] T2 — Eval Before Build: measure the existing intake prompts before deepening the code path
  - [x] T3 — Fidelity: the benchmark and artifacts must not silently invent document families or signals unsupported by the source pages
  - [x] T4 — Modular: keep intake, gap analysis, and downstream recipe execution separate
  - [x] T5 — Inspect Artifacts: review emitted contact sheets and plans, not just scores and logs

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: Category 1 intake routing plus the eval surface that measures `C2`. The natural owners are the maintained intake recipe, the contact-sheet intake modules, and the eval / benchmark artifacts rather than downstream pipeline stages.
- **Build-map reality**: Category 1 now has a maintained recommendation-only intake recipe and a passing `auto-book-type-detection` benchmark, so the substrate moved to `exists`. The compromise stays `climb` because the workflow still stops at recommendation / confirmation instead of replacing manual recipe selection. Relevant input-coverage rows are the passing `scanned-pdf-prose`, `scanned-pdf-tables`, `image-directory-scans`, and the bounded `born-digital-pdf` fixture lane. Untested families such as `docx`, `xlsx`, and `mixed-archive` remain out of scope for this story.
- **Substrate evidence**: verified in code and fresh close-out runs that `contact_sheet_manifest_v1` and `intake_plan_v1` are emitted by the maintained recipe, `driver.py` now wires intake-stage `pdf` / `images` / artifact inputs correctly, `contact_sheet_overview_v1` and `zoom_refine_v1` now recommend maintained explicit recipes instead of legacy placeholders, and the intake test surface no longer depends on the missing repo-local `input/` tree.
- **Data contracts / schemas**: the current contracts are `contact_sheet_manifest_v1` and `intake_plan_v1`. If the benchmark requires new plan fields, recipe enums, or stronger signal typing, those fields must be added to `schemas.py` before modules emit them so driver stamping does not drop them.
- **File sizes**: most likely touch points are modest, but two truth surfaces are already large: `schemas.py` is 1215 lines and `docs/build-map.md` is 584 lines. Prefer new benchmark files and focused helper changes over further bloating those files. `docs/evals/registry.yaml` is 469 lines and should stay append-only and surgical.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/build-map.md`, Story 011, Story 027, Story 157, Story 168, and Scout 011. No intake-routing-specific ADR exists under `docs/decisions/`. A new ADR is not needed unless the work tries to change the explicit-recipe compromise or reintroduce downstream dispatch as a repo-owned product surface.

## Files to Modify

- `configs/recipes/recipe-intake-contact-sheet.yaml` — add the maintained non-legacy intake recipe (new file)
- `configs/recipes/legacy/recipe-intake-contact-sheet.yaml` — keep as a thin legacy alias or document it honestly if superseded (55 lines)
- `modules/intake/contact_sheet_overview_v1/main.py` — replace stub-like defaults and make output benchmarkable (175 lines)
- `modules/intake/zoom_refine_v1/main.py` — remove placeholder legacy recipe mapping and align with the no-dispatch handoff (169 lines)
- `modules/intake/gap_analyzer_v1/main.py` — keep capability-gap output compatible with maintained plans and benchmark expectations (94 lines)
- `modules/module_catalog.yaml` — keep capability mapping honest for gap analysis and scoring (42 lines)
- `modules/intake/tests/test_intake_chain.py` — maintained-path schema / CLI coverage (48 lines)
- `modules/intake/tests/test_intake_chain_e2e.py` — remove nonexistent recipe expectations and assert maintained recommendation-only behavior (99 lines)
- `benchmarks/tasks/auto-book-type-detection.yaml` — benchmark task definition (new file)
- `benchmarks/prompts/auto-book-type-detection.txt` — benchmark prompt template or harness prompt notes (new file)
- `benchmarks/scorers/auto_book_type_detection.py` — scorer for document family / recipe accuracy (new file)
- `benchmarks/golden/auto-book-type-detection/` — curated benchmark corpus expectations (new files)
- `docs/evals/registry.yaml` — first `auto-book-type-detection` score and attempt history (469 lines)
- `docs/build-map.md` — reconcile C2 substrate and benchmark status after the story lands (584 lines)
- `docs/stories/story-027-contact-sheet-auto-intake.md` — remove stale usage / behavior claims and capture maintained truth (191 lines)
- `docs/stories.md` — add or adjust any related story-index truth if the status surface changes (177 lines)
- `schemas.py` — only if new `intake_plan_v1` fields are required by the maintained surface or benchmark (1215 lines)
- `validate_artifact.py` — only if new schema wiring is required (112 lines)

## Redundancy / Removal Targets

- `configs/recipes/legacy/recipe-intake-contact-sheet.yaml` if the maintained recipe fully replaces it
- Placeholder recipe selection inside `modules/intake/zoom_refine_v1/main.py`
- Nonexistent recipe expectations in `modules/intake/tests/test_intake_chain_e2e.py`
- Stale Story 027 usage text that points to a missing active recipe path or implies planner-style dispatch
- Any lingering intake dispatch helpers if they are no longer part of the maintained recommendation-only story

## Notes

- The benchmark corpus should prefer repo-owned fixtures or already-validated local assets and should avoid metadata hints in filenames or prompts.
- This story is about making `C2` measurable and the intake substrate honest, not about proving full autonomous planning.
- If the current multimodal contact-sheet flow already performs well, the implementation should bias toward simplification: restore the maintained recipe, add the benchmark, and avoid unnecessary prompt / module churn.

## Plan

### Exploration Summary

- **Ideal alignment:** this story closes a real Category 1 Ideal gap. The repo can ingest several formats now, but it still cannot honestly measure whether intake can detect document type and recommend the right maintained explicit recipe with zero metadata hints.
- **Relevant build-map state:** Category 1 is `partial` / `climb`, and its named deletion gate is `auto-book-type-detection` with no scores. Category 8 already has a working eval/tooling substrate, so the benchmark gap is not a missing framework problem.
- **Critical substrate verified in code:**
  - `contact_sheet_manifest_v1` and `intake_plan_v1` exist and validate.
  - The intake modules exist and already emit inspectable plan artifacts.
  - The only recipe wiring still lives under `configs/recipes/legacy/`.
  - The active recipe path documented in Story 027 is missing.
  - The current overview / zoom modules still carry stale defaults and placeholder recipe mapping.
- **Critical missing slice:** the repo lacks a maintained active intake recipe plus a scored benchmark surface for `C2`.
- **Measured baseline before implementation:** the current chain was run on 10 PDFs spanning repo fixtures plus local maintained inputs. Result: `10/10` completed, `10/10` returned `book_type: "mixed"`, `10/10` recommended `configs/recipes/legacy/recipe-ocr.yaml`, `0/10` produced a maintained recipe or `no-recipe-needed`, and `4/10` emitted no `signal_evidence` at all. Evidence: `output/runs/story169-baseline-current-chain/baseline_summary.json`.
- **Current test-surface drift:** `python -m pytest modules/intake/tests/test_intake_chain.py modules/intake/tests/test_intake_chain_e2e.py -q` fails because the e2e test still depends on the missing repo-local `input/onward-to-the-unknown-images` path before it even reaches its stale genealogy / dispatch assertions.
- **Scope adjustment folded in automatically:** keep the chain recommendation-only. Do not reopen Story 011 or add downstream dispatch as part of making `C2` measurable.
- **Additional small scope adjustment folded in automatically:** repairing the intake tests now includes removing the dead `input/` dependency so the maintained lane can be verified in-repo without hidden local setup.

### Eval-First Gate

- **Baseline first:** before changing prompts or code deeply, run the current intake chain on the benchmark corpus and record exactly how it fails.
- **Baseline result:** the current chain clears plumbing but fails the actual `C2` job. The dominant failure mode is not runtime instability; it is semantic collapse into `"mixed"` plus a legacy placeholder recipe across the whole 10-document baseline.
- **What the baseline should score:** correct document family, correct maintained explicit recipe recommendation or `no-recipe-needed`, and meaningful `signal_evidence` when signals drive recipe choice.
- **Candidate eval surfaces:**
  - a promptfoo task focused on overview / zoom outputs
  - a driver-backed benchmark harness that scores final `intake_plan_v1`
- **Chosen eval surface:** a repo-owned harness that scores final `intake_plan_v1` artifacts is the smallest honest surface. Prompt-only evaluation would miss the current failure that matters most here: downstream code still rewrites successful signal detection into legacy placeholder recipe recommendations.

### Implementation Tasks

#### Task 1 — Reproduce the current drift and freeze the benchmark corpus (`S`)

- Assemble the 10-document corpus and expected outcomes.
- Run the current intake chain and record where it fails today.
- Lock those expectations into goldens before changing behavior.

#### Task 2 — Restore the maintained intake recipe (`S-M`)

- Add `configs/recipes/recipe-intake-contact-sheet.yaml` under active recipes.
- Keep the recipe recommendation-only and stop at confirmation / final plan emission.
- Decide whether the legacy recipe should become an alias, a shim, or a documented legacy-only file.
- Repair intake tests to use maintained-path fixtures and remove hidden dependence on the missing repo-local `input/` tree.

#### Task 3 — Harden overview / zoom outputs against legacy drift (`M`)

- Remove placeholder recipe mapping and nonexistent recipe references.
- Align model defaults and output fields with the current repo mission.
- Keep gap analysis explicit and inspectable in `intake_plan_v1`.

#### Task 4 — Add the honest C2 benchmark (`M`)

- Implement the chosen eval surface, scorer, and goldens.
- Record the first score and attempt history in `docs/evals/registry.yaml`.
- Update `docs/build-map.md` only to the level the measured evidence earns.

#### Task 5 — Revalidate with real driver runs and update docs (`S-M`)

- Run representative `driver.py` intake proofs through the maintained recipe.
- Inspect emitted contact sheets and final plans in `output/runs/`.
- Update Story 027 and any stale references so the repo tells one consistent story.

### Impact Analysis

- **Primary blast radius:** intake recipe and intake modules only. Downstream OCR / build stages should remain untouched unless a benchmark input exposes a real upstream contract mismatch.
- **Secondary blast radius:** eval / docs truth surfaces (`registry.yaml`, `build-map.md`, Story 027, story index).
- **Main risk:** accidentally drifting back into planner / dispatch behavior that Story 011 already rejected. The story should treat that as a regression, not a feature.

### What Done Looks Like

- The repo has an active maintained contact-sheet intake recipe again.
- The intake modules no longer suggest nonexistent or legacy placeholder recipes.
- `auto-book-type-detection` has a real benchmark, a first recorded score, and explicit next-step evidence.
- Manual inspection confirms the maintained intake artifacts are useful and traceable.

## Work Log

20260328-0705 — story created: scoped restoration of the maintained contact-sheet intake lane plus the first honest `C2` benchmark after triage found Category 1 still `partial` / `climb`, `auto-book-type-detection` still unscored, and the active recipe path from Story 027 missing. Evidence: `docs/build-map.md` still lists `auto-book-type-detection` with no score; `docs/evals/registry.yaml` has empty scores / attempts for that eval; `configs/recipes/recipe-intake-contact-sheet.yaml` is absent while `configs/recipes/legacy/recipe-intake-contact-sheet.yaml` remains; `modules/intake/contact_sheet_overview_v1/main.py` still defaults to `gpt-4o`; `modules/intake/zoom_refine_v1/main.py` still maps to legacy / nonexistent recipes; and `modules/intake/tests/test_intake_chain_e2e.py` still expects `configs/recipes/recipe-genealogy.yaml`. Next step: `/build-story` should confirm the current baseline on a 10-document corpus, choose the honest benchmark surface, and restore the maintained intake recipe without reviving auto-dispatch.
20260328-0722 — build-story exploration: verified the code substrate and captured the current C2 baseline before any implementation. Evidence: `python -m pytest modules/intake/tests/test_intake_chain.py modules/intake/tests/test_intake_chain_e2e.py -q` currently fails in `modules/intake/tests/test_intake_chain_e2e.py` because `input/onward-to-the-unknown-images` is missing in-repo; `output/runs/story169-baseline-current-chain/baseline_summary.json` shows the live 10-document baseline finished `10/10` times but returned `book_type: "mixed"` and `configs/recipes/legacy/recipe-ocr.yaml` on all 10 documents; `output/runs/story169-baseline-current-chain/onward-unknown/overview_plan_final.jsonl` shows the chain can emit rich `signal_evidence` and `capability_gaps` while still collapsing to the wrong legacy recommendation; and `output/runs/story169-baseline-current-chain/onward-unknown/build_contact_sheets.jsonl` confirms the traceability substrate is already present in the manifest. Decision: use a repo-owned benchmark harness that scores final `intake_plan_v1` artifacts rather than a prompt-only eval, because the current failure lives in the end-to-end recommendation surface, not just the prompt output. Scope adjustment: absorb intake-test repair so the maintained lane can be proven without hidden local `input/` dependencies. Next step: present the plan and approval gate before changing recipe/module/test code.
20260328-1550 — implementation landed: restored the maintained intake recipe, added shared intake-plan helpers, removed legacy placeholder recipe mapping, and repaired the intake tests so they use repo-owned temp fixtures instead of the missing local `input/` tree. Evidence: `configs/recipes/recipe-intake-contact-sheet.yaml` now ends at `confirm_plan_v1`; `modules/intake/contact_sheet_overview_v1/main.py` now normalizes `book_type` and selects maintained recipes instead of collapsing to legacy OCR placeholders; `modules/intake/zoom_refine_v1/main.py` now derives maintained recommendations from source-input metadata rather than stale hardcoded mappings; `modules/intake/intake_plan_utils.py` centralizes recipe selection / signal normalization; and `modules/intake/tests/test_intake_chain_e2e.py` now asserts recommendation-only maintained behavior. Fresh checks: `python -m pytest modules/intake/tests/test_intake_chain.py modules/intake/tests/test_intake_chain_e2e.py -q` => `8 passed, 1 skipped`; `python -m pytest tests/driver_integration_test.py -q` => `6 passed`.
20260328-1615 — benchmark and driver verification completed: the new repo-owned `auto-book-type-detection` harness now passes `10/10`, and the maintained intake recipe has fresh `driver.py` proofs on image-directory, scanned-PDF, and born-digital-PDF inputs. Evidence: `benchmarks/results/auto-book-type-detection-story169.json` records `accuracy = 1.0`, `overall = 1.0`, and `pass_rate = 1.0`; sample benchmark artifacts inspected manually include `output/runs/auto-book-type-detection/tbotb-mini/overview_plan_final.jsonl` (`cyoa` -> `configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml`), `output/runs/auto-book-type-detection/onward-unknown/overview_plan_final.jsonl` (`genealogy` + `tables/images` -> `configs/recipes/recipe-pdf-ocr-html-mvp.yaml`), and `output/runs/auto-book-type-detection/rfp/overview_plan_final.jsonl` (`other` -> `configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml`). Fresh maintained-run artifacts inspected manually: `output/runs/story169-intake-images/01_contact_sheet_builder_v1/build_contact_sheets.jsonl` plus `output/runs/story169-intake-images/05_confirm_plan_v1/overview_plan_final.jsonl` (127-page image-directory run classified as `genealogy`, recommended `configs/recipes/recipe-images-ocr-html-mvp.yaml`, signals `tables/images`), `output/runs/story169-intake-scanned-pdf/05_confirm_plan_v1/overview_plan_final.jsonl` (`novel` -> `configs/recipes/recipe-pdf-ocr-html-mvp.yaml`, `has_extractable_text: false`), and `output/runs/story169-intake-born-digital/05_confirm_plan_v1/overview_plan_final.jsonl` (`cyoa` -> `configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml`, `has_extractable_text: true`, `signal_evidence` on pages `2/3`). Truth surfaces updated: `docs/evals/registry.yaml`, `docs/build-map.md`, `docs/stories/story-027-contact-sheet-auto-intake.md`, and the legacy recipe alias now reflect the maintained recommendation-only lane. Final repo checks: `make lint` passed; `make test` passed (`379 passed`).
20260328-0935 — story closed via /mark-story-done: fresh close-out revalidated the shipped slice and flipped the workflow gate to Done. Evidence: `make lint` passed; `make test` passed (`379 passed`); fresh maintained-lane runs under `output/runs/validate169-images/`, `output/runs/validate169-scanned/`, and `output/runs/validate169-born/` emitted stamped `contact_sheet_manifest_v1` and `intake_plan_v1` artifacts with the expected maintained recipe recommendations. Recommended next step: `/check-in-diff`.
