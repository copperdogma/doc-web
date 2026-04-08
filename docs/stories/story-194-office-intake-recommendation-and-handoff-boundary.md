---
title: "Decide Maintained Office Intake Recommendation and Handoff Boundary"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #1 (Ingest), Requirement #2 (Detect), Zero configuration, Transparency over magic, Dossier-ready output"
spec_refs:
  - "spec:1"
  - "spec:1.1"
  - "spec:8"
  - "spec:9"
adr_refs: []
depends_on:
  - "169"
  - "175"
  - "176"
  - "178"
  - "180"
  - "193"
category_refs:
  - "spec:1"
  - "spec:8"
  - "spec:9"
compromise_refs:
  - "B1"
  - "B10"
  - "C2"
input_coverage_refs:
  - "docx"
  - "xlsx"
  - "pptx"
architecture_domains:
  - "intake_and_routing"
roadmap_tags:
  - "campaign:maintained-intake-honesty"
legacy_system: ""
---

# Story 194 — Decide Maintained Office Intake Recommendation and Handoff Boundary

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md`, `docs/stories/story-169-restore-contact-sheet-intake-and-benchmark-auto-book-type-detection.md`, `docs/stories/story-175-office-document-proof-widening-and-xlsx-pptx-lane-decision.md`, `docs/stories/story-176-confirmed-intake-handoff-to-explicit-recipe-runs.md`, `docs/stories/story-178-corpus-wide-approved-intake-handoff-benchmark.md`, `docs/stories/story-180-widen-approved-intake-handoff-image-directory-proof.md`, `docs/stories/story-193-widen-xlsx-proof-and-recheck-pptx-runtime-seam.md`, `tests/fixtures/formats/_coverage-matrix.json`, `benchmarks/golden/auto-book-type-detection/corpus.json`, `benchmarks/golden/approved-intake-handoff/corpus.json`, `docs/scout/scout-011-external-document-ingestion-systems.md` (stale benchmark context only), and `None found after search in docs/runbooks/ and docs/notes/ for a narrower office-intake routing ADR or runbook`
**Depends On**: Story 169, Story 175, Story 176, Story 178, Story 180, Story 193

## Goal

Resolve the remaining office-family intake honesty gap after the direct runtime proof line closed. The repo now owns maintained direct-entry `docx` and `xlsx` lanes, and it carries a fresh current-pass `pptx` blocker, but the recommendation-only intake and approved-handoff surfaces still stop at `pdf` and `images_dir`. This story should measure that boundary on current repo-owned office fixtures, then leave one honest maintained answer: either the smallest office family that is already real (`docx` and/or `xlsx`) gains repeatable recommendation and approved-handoff proof, or the repo explicitly records that maintained office lanes remain direct explicit-recipe entry points outside recommendation-only intake automation while keeping `pptx` blocked.

## Acceptance Criteria

- [x] A fresh current-pass baseline names the actual office-family intake gap from repo evidence:
  - [x] the current recommendation and approved-handoff corpora are inspected and shown to contain no office cases
  - [x] the current intake harnesses and `modules/intake/intake_plan_utils.py` are inspected and shown to handle only `pdf` and `images_dir`
  - [x] the work log cites the exact files and sampled result artifacts reviewed rather than relying on story titles alone
- [x] The story leaves one honest maintained policy for office-family intake automation:
  - [x] N/A by design in Story 194: office intake does not widen here, so no maintained office family was added to recommendation-only intake or approved handoff
  - [x] the repo explicitly records that maintained office lanes remain direct explicit-recipe entry points outside recommendation-only intake automation, and the limitation is inspectable rather than implicit
- [x] `auto-book-type-detection` and `approved-intake-handoff` remain coherent truth surfaces:
  - [x] N/A by design in Story 194: no office-family widening was added to the locked official corpora
  - [x] both surfaces explicitly retain their current `pdf` / `images_dir` scope instead of silently implying office support
- [x] `pptx` stays explicitly blocked unless the story produces fresh substrate evidence that surpasses Story 193's `ModuleNotFoundError: No module named 'pptx'` import blocker.
- [x] If shipped behavior or documented truth changes, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, and any touched story/methodology surfaces are updated honestly and cite the exact post-story boundary.

## Out of Scope

- Building full PPTX runtime support, slide-order recovery, or any PowerPoint provenance contract
- Reopening ADR-002 or ADR-003, or changing the accepted `doc-web` runtime boundary
- Hidden auto-routing, planner-style downstream dispatch, or office-to-PDF fallback that weakens provenance
- Broadening maintained office support beyond the already-proven direct-entry `docx` / `xlsx` slices unless fresh artifact evidence justifies it
- Creating new office fixtures unless `/build-story` finds a real coverage hole that the existing repo-owned fixtures cannot answer honestly

## Approach Evaluation

- **Simplification baseline**: before extending the current `pdf` / `images_dir` intake chain, measure whether one bounded office-family classifier over repo-owned office fixtures or minimal derived previews can already choose `configs/recipes/recipe-docx-html-mvp.yaml`, `configs/recipes/recipe-xlsx-html-mvp.yaml`, or an explicit unsupported / blocked outcome honestly. If that works, prefer it over new office-specific intake machinery.
- **AI-only**: possible for routing judgment, but only useful if the result stays inspectable and does not hide unsupported runtime seams behind confident guesses. AI should choose or decline explicit recipes, not invent support the runtime cannot back up.
- **Hybrid**: likely strongest. Keep deterministic corpus ownership, handoff plumbing, and source-input forwarding in code, and use AI only where the family-classification judgment is real. This could mean office-specific preview generation plus the existing intake scoring flow, or explicit exclusion if owning that preview substrate is not justified yet.
- **Pure code**: acceptable only for truth-surface alignment, explicit unsupported outcomes, corpus/history cleanup, and source-input plumbing. Pure code alone is not enough to honestly infer office-family routing policy without either a measured classifier or an explicit non-support decision.
- **Repo constraints / prior decisions**: `spec:1.1` keeps explicit recipes until C2 is honestly deleted; `C2` remains `climb` in `docs/methodology/state.yaml`; ADR-002 and ADR-003 keep the Dossier-facing runtime boundary explicit; Stories 169, 176, 178, and 180 established recommendation and approved-handoff proof only for `pdf` / `images_dir`; Stories 175 and 193 proved maintained `docx` / `xlsx` direct lanes while leaving `pptx` blocked.
- **Existing patterns to reuse**: `benchmarks/scripts/run_auto_book_type_detection_eval.py`, `benchmarks/scripts/run_approved_intake_handoff_eval.py`, `benchmarks/scorers/auto_book_type_detection.py`, `benchmarks/scorers/approved_intake_handoff.py`, `modules/intake/intake_plan_utils.py`, `modules/intake/contact_sheet_builder_v1/main.py`, `tests/test_approved_intake_handoff_benchmark.py`, `tests/test_docx_intake_recipe.py`, `tests/test_xlsx_intake_recipe.py`, and the office-fixture/runtime proof patterns from Stories 172, 175, and 193.
- **Eval**: the deciding surface is a fresh office-family decision proof, not a paperwork edit. A winning path must either:
  - add intentional office-family recommendation / approved-handoff proof with fresh artifacts and benchmark history, or
  - leave explicit exclusion evidence that proves the current recommendation-only and handoff surfaces remain `pdf` / `images_dir` by design.
  Any winning path must also leave `pptx` blocked unless fresh substrate evidence changes that result honestly.

## Tasks

- [x] Measure the simplification baseline before adding office-specific intake plumbing:
  - [x] test whether one bounded office-family classifier over repo-owned `docx` / `xlsx` fixtures and the `pptx` probe can choose the correct maintained recipe or explicit unsupported outcome more honestly than extending the current contact-sheet chain
  - [x] record cost, artifacts, and dominant failure modes in the work log
- [x] Measure the current maintained office-intake boundary from repo evidence:
  - [x] confirm the current recommendation and approved-handoff corpora contain no office cases
  - [x] confirm the current intake harnesses and `modules/intake/intake_plan_utils.py` only handle `pdf` and `images_dir`
  - [x] inspect the existing direct `docx` / `xlsx` proof surfaces and the refreshed `pptx` blocker so the story starts from current reality rather than stale assumptions
- [x] Choose and implement the smallest honest maintained boundary:
  - [x] N/A by design in Story 194: office intake does not widen, so no office-family recommendation / approved-handoff substrate was added
  - [x] if office intake does not widen, add explicit exclusion evidence, benchmark notes, or tests so the `pdf` / `images_dir` boundary is inspectable rather than implicit
  - [x] in both cases keep `pptx` explicitly blocked unless a fresh current-pass substrate result changes that status honestly
- [x] Leave repeatable proof behind:
  - [x] rerun the relevant benchmark or harness surface with fresh office-family evidence
  - [x] if pipeline or handoff behavior changes, inspect the exact result artifacts that now enforce explicit exclusion rather than a downstream launch path
  - [x] if the result is explicit exclusion, inspect and cite the exact code/corpus paths that enforce that boundary
- [x] Add or update focused coverage:
  - [x] `tests/test_approved_intake_handoff_benchmark.py` and a sibling benchmark test now cover office-family exclusions explicitly
  - [x] targeted intake helper tests now cover the direct-entry office recipe boundary in `prepare_confirmed_handoff(...)`
  - [x] reuse `tests/test_docx_intake_recipe.py` and `tests/test_xlsx_intake_recipe.py` instead of duplicating direct office runtime smoke coverage
- [x] If this story changes documented format coverage or graduation reality: verify whether `tests/fixtures/formats/_coverage-matrix.json` and methodology state need updates; no change was required because Story 194 only made the office automation boundary explicit
- [x] Check whether the chosen implementation makes any existing corpora, benchmark notes, helper paths, or docs redundant; keep the locked official corpora unchanged and add one explicit boundary probe corpus instead
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] No `driver.py` smoke rerun was required because Story 194 changed benchmark/handoff scope reporting rather than a maintained driver pipeline; manual artifact inspection covered the new boundary result files and dry-run handoff reasons instead
  - [x] Agent tooling unchanged; `make skills-check` not required
- [x] If evals or goldens changed: no locked official eval golden changed, so `/improve-eval` was not needed; `docs/evals/registry.yaml` was updated directly for the new boundary probe evidence
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every recommendation, exclusion, or handoff claim cites the exact corpus rows, result files, helper reasons, and code paths inspected
  - [x] T1 — AI-First: do not hardcode office routing if a measured classifier can already do the job honestly
  - [x] T2 — Eval Before Build: measure the simplification baseline and current office boundary before adding new intake plumbing
  - [x] T3 — Fidelity: do not hide unsupported office seams behind optimistic routing or fallback conversions
  - [x] T4 — Modular: keep explicit recipe ownership clear and avoid special-casing one workbook or one document
  - [x] T5 — Inspect Artifacts: verify benchmark artifacts and downstream outputs manually, not just summary scores

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Blocker Summary

N/A

## Blocker Evidence

N/A

## Unblock Condition

N/A

## Architectural Fit

- **Owning module / area**: the maintained intake benchmark and handoff surfaces (`benchmarks/` plus `modules/intake/intake_plan_utils.py` and any minimal preview/input plumbing) own this, not the direct office runtime modules themselves.
- **Methodology reality**: this belongs primarily to `spec:1`, `spec:8`, and `spec:9`. In `docs/methodology/state.yaml`, `spec:1` substrate exists and `C2` is in `climb`; `spec:8` exists with `B1` in `hold`; `spec:9` exists with `B10` in `climb`. `spec:7` remains `partial` and matters here only as upstream evidence that maintained direct office lanes already exist. Relevant coverage rows are `docx` (`passing`), `xlsx` (`passing`), and `pptx` (`has-fixture`).
- **Substrate evidence**: direct office entry already exists in `configs/recipes/recipe-docx-html-mvp.yaml`, `configs/recipes/recipe-xlsx-html-mvp.yaml`, `tests/test_docx_intake_recipe.py`, `tests/test_xlsx_intake_recipe.py`, and `driver.py --input-docx/--input-xlsx`. The current intake/handoff limitation is also explicit in repo code: `benchmarks/scripts/run_auto_book_type_detection_eval.py`, `benchmarks/scripts/run_approved_intake_handoff_eval.py`, and `modules/intake/intake_plan_utils.py` only branch on `pdf` and directory inputs, and the current corpora contain no office cases. Story 193's fresh PPTX probe still fails with `ModuleNotFoundError: No module named 'pptx'`.
- **Data contracts / schemas**: the current relevant contracts are `intake_plan_v1`, `intake_handoff_v1`, and `meta.source_input.input_kind`. If office-family input kinds, handoff fields, or benchmark artifacts cross stamped boundaries, the fields must be added to `schemas.py` before claiming them in generated artifacts.
- **File sizes**: likely touch points are `modules/intake/intake_plan_utils.py` (298 lines), `modules/intake/contact_sheet_builder_v1/main.py` (204), `benchmarks/scripts/run_auto_book_type_detection_eval.py` (211), `benchmarks/scripts/run_approved_intake_handoff_eval.py` (331), `benchmarks/scorers/auto_book_type_detection.py` (78), `benchmarks/scorers/approved_intake_handoff.py` (94), `benchmarks/golden/auto-book-type-detection/corpus.json` (82), `benchmarks/golden/approved-intake-handoff/corpus.json` (90), `tests/test_approved_intake_handoff_benchmark.py` (97), `tests/test_docx_intake_recipe.py` (114), `tests/test_xlsx_intake_recipe.py` (124), `README.md` (261), `docs/RUNBOOK.md` (409), `tests/fixtures/formats/_coverage-matrix.json` (483), `docs/evals/registry.yaml` (1530), and `driver.py` (2250). Files already over 500 lines: `docs/evals/registry.yaml` and `driver.py`; prefer surgical edits.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, ADR-003, Stories 169/175/176/178/180/193, the current coverage matrix, both intake corpora, both intake benchmark harnesses, and the office runtime proof stories. No narrower runbook or ADR for office-intake routing was found; `docs/scout/scout-011-external-document-ingestion-systems.md` only contains a stale note that `auto-book-type-detection` once lacked scores.

## Files to Modify

- `benchmarks/golden/auto-book-type-detection/corpus.json` — widen only if office cases intentionally join the recommendation-only surface (82 lines)
- `benchmarks/golden/approved-intake-handoff/corpus.json` — widen only if office cases intentionally join the approved-handoff surface (90 lines)
- `benchmarks/scripts/run_auto_book_type_detection_eval.py` — office-case handling or explicit scope notes for the recommendation surface (211 lines)
- `benchmarks/scripts/run_approved_intake_handoff_eval.py` — office-case handling or explicit scope notes for the handoff surface (331 lines)
- `benchmarks/scorers/auto_book_type_detection.py` — scoring changes only if office cases or explicit exclusions affect recommendation scoring (78 lines)
- `benchmarks/scorers/approved_intake_handoff.py` — scoring changes only if office cases or explicit exclusions affect handoff scoring (94 lines)
- `modules/intake/intake_plan_utils.py` — add office-family recipe/source-input handling only if office families enter the maintained handoff path (298 lines)
- `modules/intake/contact_sheet_builder_v1/main.py` — touch only if office-family preview generation becomes part of the maintained intake path (204 lines)
- `tests/test_approved_intake_handoff_benchmark.py` — office benchmark assertions or explicit exclusion coverage (97 lines)
- `tests/test_docx_intake_recipe.py` — reused direct-lane truth surface; touch only if shared fixture or office-boundary assertions belong here (114 lines)
- `tests/test_xlsx_intake_recipe.py` — reused direct-lane truth surface; touch only if shared fixture or office-boundary assertions belong here (124 lines)
- `docs/evals/registry.yaml` — align `auto-book-type-detection` / `approved-intake-handoff` truth with the post-story office boundary (1530 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — align `docx` / `xlsx` / `pptx` intake claims only if documented reality changes (483 lines)
- `README.md` — align user-facing office entry guidance and any recommendation-only intake claims (261 lines)
- `docs/RUNBOOK.md` — align verified office entry paths, intake limits, and proof commands (409 lines)

## Redundancy / Removal Targets

- Silent ambiguity between the direct office runtime lanes and the recommendation-only intake benchmark surfaces
- Representative or stale wording that implies office families are either fully inside or fully outside the maintained intake surface without measured evidence
- Any ad hoc office benchmark notes that become redundant once the maintained boundary is explicit in the corpus, registry, and runbook surfaces

## Notes

New story justification: reopening Story 193 would blur direct office runtime proof with intake automation policy, and reopening Stories 176/178/180 would blur the already-validated `pdf` / `images_dir` handoff surface with a new office-family question. This story is honest because the remaining gap sits between those closed lines: maintained office entry points now exist directly, but the recommendation and approved-handoff surfaces still do not say whether office belongs there.

## Plan

1. **Record the measured boundary and keep this story on the explicit-exclusion path (`S`)**
   - Evidence already gathered in this pass shows the maintained direct-entry office lanes are real, but the recommendation-only and approved-handoff surfaces are not missing one tiny branch; they are built around the contact-sheet preview chain and only support `pdf` / `images_dir`.
   - Fresh baseline commands on repo-owned office fixtures produced the deciding evidence:
     - a temporary 3-case office corpus (`docx-mini`, `xlsx-mini`, `pptx-mini`) run through `python benchmarks/scripts/run_auto_book_type_detection_eval.py --corpus /tmp/story194-office-intake-corpus.json --output /tmp/story194-office-intake-baseline.json --run-root output/runs/story194-office-intake-baseline` failed `3/3` at the builder step with `NotADirectoryError` from `modules/intake/contact_sheet_builder_v1/main.py` because the current recommendation harness assumes non-PDF inputs are image directories
     - a direct `prepare_confirmed_handoff(...)` probe on office-flavored plans blocked `docx` and `xlsx` with `unsupported_recommended_recipe:configs/recipes/recipe-*.yaml` and left `pptx` as `no_recipe_needed`, proving the current approved-handoff utilities do not own office direct-entry recipes
     - the simplest deterministic suffix check on the same repo fixtures already chooses the honest current boundary (`docx` -> direct DOCX recipe, `xlsx` -> direct XLSX recipe, `pptx` -> unsupported), so building office-preview intake machinery in this story would be larger than the measured truth gap
   - Decision: do **not** widen office-family recommendation-only intake or approved handoff in Story 194. Instead make the existing `pdf` / `images_dir` boundary explicit, inspectable, and tested while preserving the separately maintained direct-entry `docx` / `xlsx` lanes.

2. **Make the benchmark surfaces fail honestly instead of crashing (`S`)**
   - Files: `benchmarks/scripts/run_auto_book_type_detection_eval.py`, `benchmarks/scripts/run_approved_intake_handoff_eval.py`
   - Add explicit supported-input-kind declarations plus a small helper that blocks unsupported office cases with a stable boundary reason before the contact-sheet builder runs.
   - Expected post-change behavior:
     - `auto-book-type-detection` only accepts `pdf`
     - `approved-intake-handoff` only accepts `pdf` and `images_dir`
     - `docx`, `xlsx`, and `pptx` probes return explicit blocked rows that say these are outside recommendation-only / approved-handoff automation and remain direct explicit-recipe entry points (or blocked, for `pptx`)
   - Risk: changing row status/reason plumbing could affect summary math or existing benchmark expectations. Keep the existing locked corpora green and confine new behavior to unsupported input kinds only.
   - Done looks like: unsupported office probes produce inspectable `scope` failures instead of `NotADirectoryError`, and the current locked corpora still execute successfully.

3. **Make the handoff utility boundary explicit at the recipe seam (`S`)**
   - Files: `modules/intake/intake_plan_utils.py`, `tests/test_intake_plan_utils.py`
   - Add a named direct-entry office recipe boundary so `prepare_confirmed_handoff(...)` reports that the maintained DOCX/XLSX recipes are outside confirmed-handoff automation, instead of collapsing them into the generic `unsupported_recommended_recipe:*` bucket.
   - Keep `pptx` blocked; do not add source-input plumbing or recipe support for office families in this story.
   - Done looks like: tests cover `docx` and `xlsx` direct-entry recipe rejection explicitly, while the existing supported `pdf` / `images_dir` command construction stays unchanged.

4. **Add corpus/harness tests that keep the boundary honest (`S`)**
   - Files: `tests/test_approved_intake_handoff_benchmark.py` plus a new or nearby benchmark test for `auto-book-type-detection`
   - Add assertions that:
     - the locked recommendation corpus contains only `pdf`
     - the approved-handoff corpus contains only `pdf` and `images_dir`
     - unsupported office cases are reported with explicit boundary reasons by both harnesses
   - Reuse the existing direct-lane tests for `docx` / `xlsx`; do not duplicate runtime proof.
   - Done looks like: future accidental office additions to the corpora or regressions back to crashy behavior fail unit tests immediately.

5. **Align docs and eval history with the explicit boundary (`S`)**
   - Files: `README.md`, `docs/RUNBOOK.md`, `docs/evals/registry.yaml`
   - Document that maintained office support currently means direct explicit-recipe entry via `--input-docx` / `--input-xlsx`, while recommendation-only intake and approved handoff remain `pdf` / `images_dir` surfaces.
   - Update the eval registry attempts/notes with the Story 194 office-boundary baseline and the post-fix explicit-scope behavior. No coverage-matrix movement is expected because format support itself is not widening.
   - Done looks like: a reader can tell from the runbook/README/registry that office support exists directly but is intentionally outside the recommendation-only automation boundary.

6. **Fresh verification and artifact inspection (`M`)**
   - Targeted checks: benchmark-related pytest coverage, then fresh office-boundary probe runs for both harnesses using repo-owned `docx`, `xlsx`, and `pptx` fixtures.
   - Artifact inspection target:
     - the post-fix office-boundary result JSON under `output/runs/` or `benchmarks/results/`
     - representative blocked row(s) showing explicit scope reasons
     - existing supported-path tests still green
   - If the boundary probes still fail inside the contact-sheet builder, the implementation is wrong.
   - If the locked corpora regress, stop and fix before handing off.

## Work Log

20260407-2137 — create-story: created Story 194 after `/triage` recommended a new office-intake boundary story and the user approved that one next action. Evidence reviewed in this pass: `tests/fixtures/formats/_coverage-matrix.json` shows `docx` and `xlsx` as bounded `passing` direct-entry lanes while `pptx` remains `has-fixture`; `benchmarks/golden/auto-book-type-detection/corpus.json` and `benchmarks/golden/approved-intake-handoff/corpus.json` still contain no office cases; `benchmarks/scripts/run_auto_book_type_detection_eval.py`, `benchmarks/scripts/run_approved_intake_handoff_eval.py`, and `modules/intake/intake_plan_utils.py` still branch only on `pdf` and directory inputs. New-story justification is explicit in `Notes`: the remaining gap is not office runtime proof or `pdf` / `images_dir` handoff proof in isolation, but the boundary between those two already-closed lines. Next step: `/build-story` should measure the simplification baseline and decide whether to widen maintained office-family intake or explicitly lock the `pdf` / `images_dir` boundary.
20260407-2209 — build-story explore/plan: measured the current office-family seam and chose the explicit-exclusion path for this story. Fresh baseline evidence: `python benchmarks/scripts/run_auto_book_type_detection_eval.py --corpus /tmp/story194-office-intake-corpus.json --output /tmp/story194-office-intake-baseline.json --run-root output/runs/story194-office-intake-baseline` failed `3/3` office probes (`testdata/docx-mini.docx`, `testdata/xlsx-mini.xlsx`, `testdata/pptx-mini.pptx`) at `failure_step=builder` with `NotADirectoryError` from `modules/intake/contact_sheet_builder_v1/main.py`; a direct `prepare_confirmed_handoff(...)` probe blocked `docx` and `xlsx` with `unsupported_recommended_recipe:configs/recipes/recipe-*.yaml`; the minimal suffix-based baseline still chose the honest current boundary (`docx` -> direct DOCX recipe, `xlsx` -> direct XLSX recipe, `pptx` -> unsupported). Files confirmed as owning the gap: `benchmarks/scripts/run_auto_book_type_detection_eval.py`, `benchmarks/scripts/run_approved_intake_handoff_eval.py`, `modules/intake/intake_plan_utils.py`, `tests/test_intake_plan_utils.py`, `tests/test_approved_intake_handoff_benchmark.py`, `README.md`, `docs/RUNBOOK.md`, and `docs/evals/registry.yaml`. Files at risk: the locked benchmark corpora and summary math. Decision: Story 194 will not invent office-preview recommendation plumbing; it will make the existing `pdf` / `images_dir` boundary explicit in harness rows, handoff reasons, tests, and docs while keeping direct-entry `docx` / `xlsx` support and the existing `pptx` blocker unchanged. Next step: mark Story 194 `In Progress`, regenerate methodology surfaces, then implement the explicit boundary handling and rerun the office probes.
20260407-2317 — implement/verify: made the office automation boundary explicit instead of widening it. Code changes: added shared benchmark scope helpers in `benchmarks/scripts/intake_scope.py`; updated `benchmarks/scripts/run_auto_book_type_detection_eval.py` and `benchmarks/scripts/run_approved_intake_handoff_eval.py` to block unsupported office inputs with stable `failure_step = scope` rows; updated `modules/intake/intake_plan_utils.py` so maintained direct-entry DOCX/XLSX recipes now report `direct_entry_recipe_outside_confirmed_handoff_scope:*` instead of the generic `unsupported_recommended_recipe:*`; added focused coverage in `tests/test_auto_book_type_detection_benchmark.py`, `tests/test_approved_intake_handoff_benchmark.py`, and `tests/test_intake_plan_utils.py`; added the rerunnable probe corpus `benchmarks/input/office-intake-boundary-corpus.json`; and aligned `README.md`, `docs/RUNBOOK.md`, and `docs/evals/registry.yaml` with the explicit office boundary. Fresh artifact evidence inspected manually in this pass: `benchmarks/results/auto-book-type-detection-story194-office-boundary.json` now records three blocked `scope` rows (`docx`, `xlsx`, `pptx`) instead of crashing in the contact-sheet builder; `benchmarks/results/approved-intake-handoff-story194-office-boundary.json` records the same explicit boundary for approved handoff; a direct dry-run probe of `prepare_confirmed_handoff(...)` now prints `direct_entry_recipe_outside_confirmed_handoff_scope:docx` and `direct_entry_recipe_outside_confirmed_handoff_scope:xlsx`. Fresh checks: `pytest tests/test_auto_book_type_detection_benchmark.py tests/test_approved_intake_handoff_benchmark.py tests/test_intake_plan_utils.py`, `make lint`, and `make test` (`475 passed`, 4 pre-existing warnings in `modules/portionize/portionize_headers_numeric_v1/main.py`). No coverage-matrix or methodology-state change was required because Story 194 changed honesty and inspectability, not actual office runtime support. Next step: regenerate methodology surfaces, then hand off for `/validate`.
20260407-2324 — methodology refresh: reran `make methodology-compile && make methodology-check` after the story, registry, and docs updates. Evidence: `docs/methodology/graph.json` and `docs/stories.md` regenerated cleanly and `scripts/methodology_graph.py check` reported `Methodology graph is current: docs/methodology/graph.json`. Workflow result: `Build complete` is now checked; `Validation complete` and `/mark-story-done` remain intentionally open for the next step.
20260407-2346 — validate follow-through: normalized the Story 194 checklist to reflect the path actually shipped. Acceptance criteria and tasks now mark the widening branch as explicitly not applicable in this story, `Validation complete` is checked, and the fresh validation evidence from this pass is: `make lint`, `pytest tests/test_auto_book_type_detection_benchmark.py tests/test_approved_intake_handoff_benchmark.py tests/test_intake_plan_utils.py`, `make test`, `make methodology-check`, `python benchmarks/scripts/run_auto_book_type_detection_eval.py --corpus benchmarks/input/office-intake-boundary-corpus.json --output benchmarks/results/auto-book-type-detection-story194-office-boundary.json --run-root output/runs/story194-auto-book-type-detection-office-boundary`, `python benchmarks/scripts/run_approved_intake_handoff_eval.py --corpus benchmarks/input/office-intake-boundary-corpus.json --output benchmarks/results/approved-intake-handoff-story194-office-boundary.json --run-root output/runs/story194-approved-intake-handoff-office-boundary`, and a fresh `prepare_confirmed_handoff(...)` dry-run for `docx`/`xlsx`. Result: the story is implementation-complete and validation-complete; the only remaining close-out step is `/mark-story-done`.
20260407-2354 — mark-story-done: closed Story 194 after fresh close-out checks confirmed the explicit office automation boundary is the shipped result. Evidence carried into close-out from the current pass: `make lint`, `pytest tests/test_auto_book_type_detection_benchmark.py tests/test_approved_intake_handoff_benchmark.py tests/test_intake_plan_utils.py`, `make test` (`475 passed`, same 4 pre-existing warnings in `modules/portionize/portionize_headers_numeric_v1/main.py`), `make methodology-check`, `benchmarks/results/auto-book-type-detection-story194-office-boundary.json`, `benchmarks/results/approved-intake-handoff-story194-office-boundary.json`, and the fresh dry-run `prepare_confirmed_handoff(...)` results for `docx` / `xlsx`. Updated the story status to `Done`, checked the `/mark-story-done` gate, and queued the generated index/graph refresh plus changelog entry. Next step: `/check-in-diff`.
