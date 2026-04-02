# Story 180 — Widen Approved Intake Handoff to Repo-Owned Image-Directory Proof

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #1 (Ingest), Requirement #2 (Detect), Zero configuration, Transparency over magic
**Spec Refs**: spec:1 (spec:1.1, C2), spec:8 (B1), spec:9 (B10)
**Build Map Refs**: Category 1 Intake & Format Routing (`exists`, C2 `climb`); Category 8 AI Harnesses & Tooling (`exists`, B1 `hold`); Category 9 Planning Infrastructure (`exists`, B10 `climb`); Input Coverage rows `image-directory-scans` (`passing`, approved-handoff surface now includes one repo-owned bounded case but broader family breadth remains unproven) and `handwritten-notes` (bounded synthetic `passing` on the maintained generic image-directory and PDF OCR lanes)
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/stories/story-176-confirmed-intake-handoff-to-explicit-recipe-runs.md`, `docs/stories/story-178-corpus-wide-approved-intake-handoff-benchmark.md`, `docs/stories/story-179-repo-owned-handwritten-notes-fixture-and-baseline-transcription.md`, `benchmarks/golden/approved-intake-handoff/corpus.json`, `benchmarks/golden/auto-book-type-detection/corpus.json`, `tests/fixtures/formats/_coverage-matrix.json`, `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower image-directory approved-handoff ADR or runbook
**Depends On**: Story 176, Story 178, Story 179

## Goal

Close the remaining C2 honesty gap after Story 178 by moving image-directory approved handoff from a representative proof to a repo-owned measured surface. The maintained intake chain already recommends `recipe-images-ocr-html-mvp.yaml` for approved image-directory plans, Story 176 proved that seam once on a local non-repo-owned directory, and Story 179 added a checked-in image-directory fixture (`testdata/handwritten-notes-mini-images`) plus bounded OCR proof. This story should use that repo-owned image-directory substrate to prove that `confirm_plan_v1` plus `run_dispatch_v1` can launch the maintained image-directory recipe without manual recipe or source-path retyping, then update the C2/B10 truth surfaces only as far as the fresh bounded evidence justifies.

## Acceptance Criteria

- [x] A repeatable approved-handoff proof surface exists for at least one repo-owned image-directory input, starting with `testdata/handwritten-notes-mini-images` unless `/build-story` finds a smaller or more representative repo-owned image-directory case.
- [x] The chosen proof runs through the maintained intake flow (`contact_sheet_builder_v1` -> `contact_sheet_overview_v1` -> `zoom_refine_v1` -> `gap_analyzer_v1` -> `confirm_plan_v1`) and then through `run_dispatch_v1`, writing an inspectable stamped `intake_handoff_v1` row with the approved plan path, `--input-images` launch metadata, and downstream `run_id`.
- [x] The launched downstream run stamps the expected first artifact for `configs/recipes/recipe-images-ocr-html-mvp.yaml` under `output/runs/` with no manual recipe edits or hand-entered image-directory path; manual inspection is recorded for both the handoff artifact and the first downstream artifact.
- [x] The story makes an explicit truth-surface decision: either widen `approved-intake-handoff` in place to include the repo-owned image-directory proof or add the smallest honest sibling surface, and update `docs/evals/registry.yaml` plus `docs/build-map.md` accordingly.
- [x] The proof-surface change does not silently widen the recommendation-only `auto-book-type-detection` benchmark: either that benchmark stays on its locked 10-document corpus, or any widening is intentional, freshly rerun, and documented for both surfaces.
- [x] Any remaining residual claim is explicit. If one repo-owned image-directory case is still too narrow to remove the residual caveat globally, the docs say so instead of implying broader image-directory closure.

## Out of Scope

- Broadening the locked maintained-intake corpus across multiple new image-directory families in one story
- New input families beyond the repo-owned image-directory slice already available in this checkout
- Removing the human approval gate or reviving Story 011's rejected planner behavior
- Full downstream validation past the first stamped artifact needed to prove the handoff seam
- Expanding the bounded synthetic handwritten-notes support claim beyond what Story 179 already proved

## Approach Evaluation

- **Simplification baseline**: the current approved-handoff harness already appears generic across input kinds. `benchmarks/scripts/run_approved_intake_handoff_eval.py` branches between `--pdf` and `--input_dir`, and `modules/intake/tests/test_intake_chain_e2e.py` already covers dry-run image-directory handoff rows with `--input-images`. Before adding new helpers or truth surfaces, first prove whether a one-case repo-owned image-directory corpus entry already works end to end.
- **AI-only**: low value and mis-scoped. The AI routing problem is already solved upstream by the existing contact-sheet overview/zoom flow. The remaining gap is benchmark orchestration, bounded launch proof, and truthful documentation.
- **Hybrid**: likely the right shape. Keep the current AI intake stages unchanged, then deterministically evaluate the approved handoff on a repo-owned image-directory case. Candidate A widens the current `approved-intake-handoff` harness/corpus in place. Candidate B adds a small sibling repo-owned image-directory handoff proof so the locked PDF corpus history stays intact.
- **Pure code**: plausible and likely sufficient if the current harness, scorer, and `intake_handoff_v1` fields already express everything needed for image-directory launch proof. This becomes less attractive only if the mixed-corpus semantics make the existing eval harder to interpret.
- **Repo constraints / prior decisions**: Story 176 intentionally kept image-directory proof representative. Story 178 intentionally widened the approved-handoff benchmark only across the locked PDF corpus and left image-directory as an explicit residual. Story 179 added the first repo-owned image-directory fixture and bounded OCR proof, which is the new evidence that makes this story worthwhile now. ADR-002 keeps the runtime boundary explicit and inspectable; this story should stay inside that seam rather than inventing new routing behavior.
- **Existing patterns to reuse**: `benchmarks/scripts/run_approved_intake_handoff_eval.py`, `benchmarks/scorers/approved_intake_handoff.py`, `benchmarks/golden/auto-book-type-detection/corpus.json`, `tests/test_approved_intake_handoff_benchmark.py`, `tests/test_image_directory_intake_recipe.py`, `modules/intake/tests/test_intake_chain_e2e.py`, `modules/intake/run_dispatch_v1/main.py`, and Story 176's bounded first-artifact inspection pattern.
- **Eval**: the deciding evidence is a fresh driver-backed repo-owned image-directory approved-handoff proof, not another recommendation-only benchmark. `/build-story` must choose whether the honest output is:
  - widening `approved-intake-handoff` in place with one repo-owned image-directory case, or
  - keeping the locked PDF corpus stable and adding the smallest sibling proof surface for repo-owned image-directory handoff.
  In either case, downstream execution should stop at the first stamped artifact (`images_to_manifest`) to keep runtime and OCR cost bounded.

## Tasks

- [x] Measure the current repo-owned image-directory baseline and document the real gap:
  - [x] confirm that the current approved-handoff harness can already accept `input_kind = images_dir` cases without runtime changes
  - [x] verify the expected first downstream artifact for `configs/recipes/recipe-images-ocr-html-mvp.yaml` is `01_images_dir_to_manifest_v1/pages_images_manifest.jsonl`
  - [x] record whether the current blocker is only truth-surface scope or whether mixed-corpus harness/readability issues justify a sibling proof
- [x] Decide and implement the smallest honest repo-owned image-directory proof surface:
  - [x] prefer a dedicated approved-handoff corpus path so `auto-book-type-detection` can stay on its locked 10-document recommendation-only surface; only widen `benchmarks/golden/auto-book-type-detection/corpus.json` if both benchmark surfaces are intentionally re-baselined
  - [x] keep approval semantics explicit by still going through `confirm_plan_v1` and `run_dispatch_v1`
  - [x] keep the starting repo-owned case bounded to `testdata/handwritten-notes-mini-images` unless a better repo-owned image-directory case is discovered during `/build-story`
- [x] Add focused coverage for the image-directory handoff slice:
  - [x] extend `tests/test_approved_intake_handoff_benchmark.py` or a sibling benchmark test with image-directory first-artifact expectations
  - [x] extend the approved-handoff harness/scorer only where non-PDF semantics actually differ
  - [x] keep `tests/test_image_directory_intake_recipe.py` as the cheap stage smoke unless broader integration risk appears
- [x] Run fresh driver-backed approved-handoff proof for the repo-owned image-directory case:
  - [x] inspect the stamped `intake_handoff_v1` row
  - [x] inspect the first downstream stamped artifact under `output/runs/`
  - [x] record specific artifact paths and sample fields in the work log
- [x] Decide whether the new proof is enough to remove the image-directory residual from the C2 note, or whether the residual should remain but be narrowed to broader image-directory-family breadth rather than total absence of repo-owned proof
- [x] If this story changes documented format coverage or graduation reality: update `docs/build-map.md` and record the before/after state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [x] If agent tooling changed: `make skills-check` (not expected for this story)
- [x] If evals or goldens changed: run `/improve-eval` behaviorally for the chosen approved-handoff surface and update `docs/evals/registry.yaml`
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: the repo-owned image-directory proof traces plan path, handoff artifact, launch input, downstream run, and first stamped artifact
  - [x] T1 — AI-First: no new AI is added to a benchmark/truth-surface widening problem
  - [x] T2 — Eval Before Build: the current harness and fixture substrate are measured before any structural benchmark changes
  - [x] T3 — Fidelity: the approved image-directory handoff launches the maintained recipe without hidden path mutation or silent fallback
  - [x] T4 — Modular: this widens an existing proof surface and reuses existing maintained intake/dispatch seams instead of inventing a new path
  - [x] T5 — Inspect Artifacts: the handoff row and first downstream artifact are manually inspected, not just counted

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: the benchmark / truth-surface seam between maintained intake confirmation and approved downstream launch for repo-owned image-directory inputs. Primary ownership should stay in `benchmarks/`, intake test coverage, and the docs that describe C2/B10 honestly.
- **Build-map reality**: Category 1 owns the user-facing value and remains `climb` because C2 still has explicit residual manual/config coverage. Category 8 matters because this is an eval/harness truth-surface story, not a new extraction lane. Category 9 matters because B10 tracks the remaining explicit YAML/config overlap. The relevant input rows are `image-directory-scans` and `handwritten-notes`.
- **Substrate evidence**: verified in code that `benchmarks/scripts/run_approved_intake_handoff_eval.py` (331 lines) already branches between `--pdf` and `--input_dir`, `benchmarks/scorers/approved_intake_handoff.py` (94 lines) scores launched/non-launch outcomes generically, `tests/test_approved_intake_handoff_benchmark.py` (79 lines) already verifies first-stage artifact mapping, `modules/intake/tests/test_intake_chain_e2e.py` already asserts `--input-images` launch metadata for image-directory plans, and `tests/test_image_directory_intake_recipe.py` (49 lines) already proves the repo-owned `testdata/handwritten-notes-mini-images` fixture can stamp `page_image_v1` rows. This is why the story is `Pending`, not `Draft`: the missing slice is bounded proof and truthful documentation, not missing runtime substrate.
- **Data contracts / schemas**: no schema change is expected if the current `intake_handoff_v1` fields and benchmark result payload already cover image-directory proof. If the widened proof exposes a missing artifact field, update `schemas.py` before claiming the new field in stamped artifacts.
- **File sizes**: likely owner files are `benchmarks/scripts/run_approved_intake_handoff_eval.py` (331), `benchmarks/scorers/approved_intake_handoff.py` (94), `tests/test_approved_intake_handoff_benchmark.py` (79), `tests/test_image_directory_intake_recipe.py` (49), `benchmarks/golden/approved-intake-handoff/corpus.json` (91), `docs/evals/registry.yaml` (730), `docs/build-map.md` (586), and `docs/stories.md` (188). Keep `docs/evals/registry.yaml` and `docs/build-map.md` edits surgical because both are already >500 lines.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md` (`spec:1.1`, `spec:8`, `spec:9`), the C2/input-coverage sections of `docs/build-map.md`, ADR-002, Stories 176/178/179, `benchmarks/golden/auto-book-type-detection/corpus.json`, `benchmarks/scripts/run_approved_intake_handoff_eval.py`, `benchmarks/scorers/approved_intake_handoff.py`, `modules/intake/tests/test_intake_chain_e2e.py`, and `tests/test_image_directory_intake_recipe.py`. Search across `docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` found no narrower image-directory handoff decision doc.

## Files to Modify

- `benchmarks/golden/approved-intake-handoff/corpus.json` — dedicated approved-handoff corpus widened to 11 cases without changing the locked recommendation-only corpus (91 lines)
- `benchmarks/scripts/run_approved_intake_handoff_eval.py` — support the chosen repo-owned image-directory proof shape and result metadata (331 lines)
- `benchmarks/scorers/approved_intake_handoff.py` — adjust mixed-corpus or sibling-surface scoring only if the image-directory case needs explicit new checks (94 lines)
- `tests/test_approved_intake_handoff_benchmark.py` — add image-directory first-artifact expectation coverage (79 lines)
- `tests/test_image_directory_intake_recipe.py` — keep or extend the cheap repo-owned image-directory smoke proof where needed (49 lines)
- `docs/evals/registry.yaml` — update the approved-handoff truth surface and residual wording if the new proof lands (730 lines)
- `docs/build-map.md` — update the C2 note if the image-directory residual changes from representative-only to repo-owned measured proof (586 lines)
- `docs/stories.md` — keep Story 180 indexed and in sync with its `In Progress` status (188 lines)
- `docs/stories/story-180-widen-approved-intake-handoff-image-directory-proof.md` — record implementation evidence and close-out decisions

## Redundancy / Removal Targets

- The current representative-only image-directory residual wording in `docs/build-map.md` and `docs/evals/registry.yaml` if repo-owned proof makes it obsolete
- One-off manual image-directory handoff references when the benchmark harness can own the proof surface directly
- Duplicate first-stage artifact expectation logic across story notes and tests if one shared benchmark helper can own it cleanly

## Notes

- The default starting case should be `testdata/handwritten-notes-mini-images` because it is repo-owned, already proven through the maintained generic OCR seam, and small enough to keep the handoff proof cheap and inspectable.
- The first downstream artifact for the maintained image-directory recipe should stay bounded at `images_to_manifest` / `01_images_dir_to_manifest_v1/pages_images_manifest.jsonl`; this story does not need to rerun OCR to prove the handoff seam honestly.
- Before implementation, `benchmarks/golden/auto-book-type-detection/corpus.json` fed both `run_auto_book_type_detection_eval.py` and `run_approved_intake_handoff_eval.py`. That shared-corpus coupling was the main structural risk discovered during `/build-story`; this story removes it by moving approved handoff onto `benchmarks/golden/approved-intake-handoff/corpus.json` and leaving the recommendation-only benchmark unchanged.
- If widening `approved-intake-handoff` in place would make the current locked PDF corpus harder to interpret or maintain, a sibling repo-owned image-directory proof surface is acceptable as long as the docs stay explicit about what each surface proves.
- This story is about repo-owned approved-handoff evidence, not about broad handwritten support. Story 179's bounded synthetic caveat still applies.

## Plan

### Exploration Summary

- **Ideal alignment:** proceed. This story closes the exact remaining C2 honesty gap called out in `docs/build-map.md`: image-directory no longer needs to rely solely on Story 176's representative proof now that a repo-owned image-directory fixture exists.
- **Relevant build-map state:** Category 1 remains `exists` / `climb`; Category 8 remains `exists` / `hold`; Category 9 remains `exists` / `climb`. The current C2 note explicitly says image-directory is outside the locked corpus-wide handoff surface even after Story 178.
- **Critical substrate verified in code:** the approved-handoff harness, scorer, image-directory launch metadata, and repo-owned fixture smoke coverage already exist. The missing slice is fresh repo-owned driver-backed proof plus an honest truth-surface decision; no runtime hole was found in `run_dispatch_v1` or `intake_plan_utils.py`.
- **Starting repo-owned case:** `testdata/handwritten-notes-mini-images` is already checked in and already exercised by `tests/test_image_directory_intake_recipe.py` and Story 179's OCR proof. No new fixture-creation story is needed first.
- **Fresh baseline:** `python benchmarks/scripts/run_approved_intake_handoff_eval.py --corpus /tmp/story180-imagedir-corpus.json --output /tmp/story180-imagedir-result.json --run-root output/runs/story180-imagedir-baseline` completed successfully on April 1, 2026 local time with `docs = 1`, `launched = 1`, `pass_rate = 1.0`, and `overall = 1.0`. Manual artifact inspection confirmed:
  - `output/runs/story180-imagedir-baseline/handwritten-notes-mini-images/overview_plan_final.jsonl` recommended `configs/recipes/recipe-images-ocr-html-mvp.yaml` from `input_kind = images_dir`
  - `output/runs/story180-imagedir-baseline/handwritten-notes-mini-images/intake_handoff.jsonl` stamped `launch_input_flag = --input-images`, the repo-owned `launch_input_path`, and `terminal_outcome = launched`
  - `output/runs/story180-imagedir-baseline-handwritten-notes-mini-images-recipe-images-ocr-html-mvp/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl` stamped two `page_image_v1` rows sourcing the checked-in image directory
- **Scope delta folded into this story:** because the current code already passes the repo-owned image-directory baseline, the likely implementation is narrower than the original story wording implied. The preferred path is a benchmark-shape change, not runtime work: add an approved-handoff-specific corpus file so the locked recommendation-only corpus can stay stable.

### Eval-First Gate

- **Baseline first:** run or trace the current approved-handoff harness on a repo-owned image-directory case and confirm whether the existing corpus/result shape is already sufficient.
- **Baseline outcome:** current code already passes the repo-owned image-directory case with no runtime changes. That eliminates the pure runtime branch from consideration for this story.
- **What the baseline now answers:** the real decision is corpus ownership. Adding the image-directory case directly to `benchmarks/golden/auto-book-type-detection/corpus.json` would silently widen `auto-book-type-detection` as well as `approved-intake-handoff`, because both harnesses currently default to the same corpus file.
- **Honesty gate:** if one repo-owned image-directory case is still too narrow to remove the residual globally, keep the residual but narrow it to proof breadth rather than the absence of repo-owned evidence.

### Recommended Implementation Plan

- **Recommended path:** widen `approved-intake-handoff` in place, but do it through a dedicated approved-handoff corpus file rather than by mutating the shared recommendation-only corpus. Relative effort: `S`.

1. Add an approved-handoff-specific corpus file (`XS`)
   - Files: new `benchmarks/golden/approved-intake-handoff/corpus.json`
   - Change: copy the existing locked 10-document approved-handoff cases into a dedicated corpus file and add the repo-owned image-directory case (`handwritten-notes-mini-images`) as case 11.
   - Why this order: it removes the main structural risk first and keeps the recommendation-only benchmark stable.
   - Done when: approved-handoff has its own corpus and `auto-book-type-detection` still points at the existing locked 10-document file.

2. Point the approved-handoff harness and tests at the new corpus shape (`XS`)
   - Files: `benchmarks/scripts/run_approved_intake_handoff_eval.py`, `tests/test_approved_intake_handoff_benchmark.py`
   - Change: either update the harness default corpus to the new approved-handoff path or keep the default and make the registry command explicit with `--corpus`; add/adjust a benchmark test so image-directory first-stage expectations are covered.
   - Files at risk: low. No runtime modules should change unless the rerun falsifies the baseline unexpectedly.
   - Done when: the harness has one canonical approved-handoff corpus path and benchmark tests cover the image-directory recipe's first-stage artifact.

3. Re-run the full approved-handoff proof on the dedicated corpus (`S`)
   - Files: no code changes expected; produces fresh artifacts under `output/runs/` and a fresh result JSON under `benchmarks/results/`
   - Change: run the approved-handoff harness on the dedicated corpus, inspect the new image-directory row plus representative existing PDF rows, and confirm the mixed corpus stays readable.
   - Artifact checks:
     - `.../handwritten-notes-mini-images/intake_handoff.jsonl`
     - `...-recipe-images-ocr-html-mvp/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl`
     - one representative launched PDF row
     - one representative skipped row
   - Done when: the widened proof surface has fresh current-pass evidence, not just the one-off baseline.

4. Update truth surfaces narrowly (`XS`)
   - Files: `docs/evals/registry.yaml`, `docs/build-map.md`, `docs/stories/story-180-widen-approved-intake-handoff-image-directory-proof.md`
   - Change: update `approved-intake-handoff` to reference the dedicated corpus and the repo-owned image-directory evidence; narrow or remove the image-directory residual only as far as the fresh mixed-corpus proof justifies.
   - Structural note: `docs/evals/registry.yaml` (730 lines) and `docs/build-map.md` (586 lines) are the largest files in scope, so edits should stay surgical and evidence-backed.
   - Done when: the docs say exactly what the widened proof covers and what it still does not cover.

5. Leave runtime seams untouched unless falsified (`XS`)
   - Files intentionally not planned for change: `modules/intake/run_dispatch_v1/main.py`, `modules/intake/intake_plan_utils.py`, `tests/test_image_directory_intake_recipe.py`
   - Rationale: the baseline already proved the repo-owned image-directory case launches correctly with `--input-images` and stamps the expected first artifact.
   - Done when: implementation does not grow into unnecessary runtime work.

### Impact Analysis

- **Primary blast radius:** approved-handoff benchmark semantics and C2/B10 truth wording.
- **Secondary blast radius:** default corpus ownership for `run_approved_intake_handoff_eval.py`.
- **What could break:** accidental drift in `auto-book-type-detection` semantics if the shared corpus is edited; benchmark test assumptions around first-stage artifact mapping; docs overstating one narrow image-directory case as broad image-directory closure.
- **Redundancy plan:** remove the representative-only wording only if the fresh widened proof makes it obsolete; do not create parallel ad hoc proof commands in docs when the harness can own the result.
- **Schema / boundary risk:** low. Current `intake_handoff_v1` fields are sufficient; no schema change is planned.
- **Structural health note:** because the runtime substrate already passes, any change to `run_dispatch_v1` or `intake_plan_utils.py` should be treated as a smell and justified with fresh failure evidence.

### Human-Approval Gate

- **Recommended implementation:** add a dedicated approved-handoff corpus file, widen `approved-intake-handoff` in place via that corpus, rerun the mixed proof, and update docs. Relative effort: `S`.
- **Alternative:** add a sibling eval ID or separate proof surface just for repo-owned image-directory handoff. This is also viable, but it adds another truth surface to maintain. Relative effort: `S-M`.
- **Approval blocker:** whether you want `approved-intake-handoff` to widen in place using a dedicated corpus file, or whether you prefer a separate sibling proof surface for repo-owned image-directory evidence.

### What Done Looks Like

- The repo has a fresh approved-handoff proof on at least one repo-owned image-directory case inside the maintained benchmark surface.
- The proof records an inspectable `intake_handoff_v1` row plus the bounded first downstream artifact.
- The recommendation-only `auto-book-type-detection` surface remains honest and explicit about whether it did or did not widen.
- The C2 note no longer depends solely on a non-repo-owned representative image-directory proof.
- Any residual breadth gap stays explicit.

## Work Log

20260401-2305 — story created from `/triage`: scoped the remaining repo-owned image-directory handoff honesty gap after Stories 176, 178, and 179. Evidence reviewed in this pass: `docs/build-map.md` still says C2 remains `climb` because image-directory is outside the corpus-wide approved-handoff surface; `benchmarks/scripts/run_approved_intake_handoff_eval.py` already branches between `--pdf` and `--input_dir`; `modules/intake/tests/test_intake_chain_e2e.py` already covers dry-run image-directory handoff launch metadata; `tests/test_image_directory_intake_recipe.py` proves the checked-in `testdata/handwritten-notes-mini-images` fixture can stamp `page_image_v1` rows; and Story 179 already proved that same repo-owned image-directory slice through the maintained generic OCR lane. Result: the story is `Pending`, not `Draft`, because the harness, fixture, and test substrate already exist in code and the missing slice is bounded proof plus truth-surface updates. Next step: `/build-story` should decide whether to widen `approved-intake-handoff` in place or add a sibling repo-owned image-directory proof surface, then rerun fresh bounded handoff evidence.
20260401-2312 — `/build-story` exploration and eval-first baseline: verified that Story 180 is honestly buildable without runtime prerequisite work. Context reviewed in this pass: `docs/ideal.md`, `docs/spec.md` (`spec:1.1`, `spec:8`, `spec:9`), the C2 and input-coverage sections of `docs/build-map.md`, ADR-002, Stories 176 / 178 / 179, `benchmarks/scripts/run_approved_intake_handoff_eval.py`, `benchmarks/scripts/run_auto_book_type_detection_eval.py`, `benchmarks/scorers/approved_intake_handoff.py`, `modules/intake/run_dispatch_v1/main.py`, `modules/intake/intake_plan_utils.py`, `modules/intake/tests/test_intake_chain_e2e.py`, and `tests/test_image_directory_intake_recipe.py`. Files likely to change based on exploration: a new approved-handoff-specific corpus file under `benchmarks/golden/`, `benchmarks/scripts/run_approved_intake_handoff_eval.py` or its registry command, `tests/test_approved_intake_handoff_benchmark.py`, `docs/evals/registry.yaml`, and `docs/build-map.md`; files at risk only if the baseline failed would have been `modules/intake/run_dispatch_v1/main.py` and `modules/intake/intake_plan_utils.py`, but the baseline did not justify touching them. Fresh baseline evidence: `python benchmarks/scripts/run_approved_intake_handoff_eval.py --corpus /tmp/story180-imagedir-corpus.json --output /tmp/story180-imagedir-result.json --run-root output/runs/story180-imagedir-baseline` completed with `docs = 1`, `launched = 1`, `pass_rate = 1.0`, and `overall = 1.0` on the repo-owned `testdata/handwritten-notes-mini-images` case. Manual inspection confirmed `output/runs/story180-imagedir-baseline/handwritten-notes-mini-images/overview_plan_final.jsonl` recommended `configs/recipes/recipe-images-ocr-html-mvp.yaml`, `output/runs/story180-imagedir-baseline/handwritten-notes-mini-images/intake_handoff.jsonl` stamped `launch_input_flag = --input-images` and the repo-owned image-directory path, and `output/runs/story180-imagedir-baseline-handwritten-notes-mini-images-recipe-images-ocr-html-mvp/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl` stamped two `page_image_v1` rows sourcing the checked-in fixture. Patterns to follow: reuse the existing approved-handoff harness and scorer, keep downstream execution bounded at `images_to_manifest`, and avoid touching runtime seams that already pass. Surprise found: the story's likely work is narrower than first described; the real risk is benchmark-shape drift because both `run_approved_intake_handoff_eval.py` and `run_auto_book_type_detection_eval.py` currently default to `benchmarks/golden/auto-book-type-detection/corpus.json`. Small coherent scope delta folded into the story: prefer an approved-handoff-specific corpus file so the locked 10-document recommendation-only benchmark stays stable while `approved-intake-handoff` widens in place. Next step: present the plan and get approval before implementation.
20260401-2358 — implementation completed on the benchmark/docs seam with no runtime intake changes. Added `benchmarks/golden/approved-intake-handoff/corpus.json` as the dedicated 11-case approved-handoff corpus (locked 10-document PDF surface plus repo-owned `testdata/handwritten-notes-mini-images`), pointed `benchmarks/scripts/run_approved_intake_handoff_eval.py` at that corpus by default, and extended `tests/test_approved_intake_handoff_benchmark.py` with image-directory first-stage expectations (`images_to_manifest` / `images_dir_to_manifest_v1` / `pages_images_manifest.jsonl`). Fresh focused check: `python -m pytest tests/test_approved_intake_handoff_benchmark.py -q` passed `7/7`. Fresh driver-backed proof: `python benchmarks/scripts/run_approved_intake_handoff_eval.py --output benchmarks/results/approved-intake-handoff-story180.json --run-root output/runs/story180-approved-intake-handoff` completed `11/11` cases with `pass_rate = 1.0`, `overall = 1.0`, `launched = 7`, `skipped = 4`, and `failed_runs = 0`. Manual artifact inspection in this pass confirmed the new repo-owned image-directory handoff at `output/runs/story180-approved-intake-handoff/handwritten-notes-mini-images/intake_handoff.jsonl` stamped `recommended_recipe = configs/recipes/recipe-images-ocr-html-mvp.yaml`, `launch_input_flag = --input-images`, the repo-owned `launch_input_path`, and a bounded downstream `run_id`; the first downstream artifact at `output/runs/story180-approved-intake-handoff-handwritten-notes-mini-images-recipe-images-ocr-html-mvp/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl` stamped two `page_image_v1` rows sourcing `page-001.png` and `page-002.png`; a representative launched PDF row at `output/runs/story180-approved-intake-handoff/tbotb-mini/intake_handoff.jsonl` still stamped `--input-pdf` into `recipe-born-digital-pdf-marker-lite-html-mvp.yaml` and its first downstream artifact at `output/runs/story180-approved-intake-handoff-tbotb-mini-recipe-born-digital-pdf-marker-lite-html-mvp/01_extract_pdf_marker_lite_html_v1/pages_html.jsonl`; and a representative skip at `output/runs/story180-approved-intake-handoff/scanned-prose-mini/intake_handoff.jsonl` still stamped `terminal_outcome = skipped` with `terminal_reason = no_recipe_needed`. Truth surfaces updated narrowly in `docs/evals/registry.yaml` and `docs/build-map.md`: the residual claim now says the remaining gap is image-directory-family breadth rather than absence of repo-owned image-directory proof, and `auto-book-type-detection` remains locked to its original 10-case recommendation-only PDF corpus. Repo checks after the edits: `make lint` passed and `make test` passed (`422 passed, 4 warnings in 191.56s`). No change was needed in `modules/intake/run_dispatch_v1/main.py`, `modules/intake/intake_plan_utils.py`, or `tests/test_image_directory_intake_recipe.py`; the runtime seam already held.
20260402-0008 — `/mark-story-done` close-out: revalidated the story against the current diff, `docs/ideal.md`, `docs/spec.md` (`spec:1.1`, `spec:8`, `spec:9`), and ADR-002 before closing. Fresh close-out evidence in this pass: `make lint` passed, `python -m pytest tests/test_approved_intake_handoff_benchmark.py -q` passed `7/7`, `make test` passed (`422 passed, 4 warnings in 230.18s`), and `python benchmarks/scripts/run_approved_intake_handoff_eval.py --output benchmarks/results/approved-intake-handoff-story180-validation.json --run-root output/runs/story180-approved-intake-handoff-validation` completed `11/11` cases with `pass_rate = 1.0`, `launched = 7`, `skipped = 4`, `failed_runs = 0`, and the repo-owned image-directory row still launching `recipe-images-ocr-html-mvp.yaml` with `--input-images` into `01_images_dir_to_manifest_v1/pages_images_manifest.jsonl`. Manual artifact inspection in the same close-out pass confirmed `output/runs/story180-approved-intake-handoff-validation/handwritten-notes-mini-images/intake_handoff.jsonl`, `output/runs/story180-approved-intake-handoff-validation-handwritten-notes-mini-images-recipe-images-ocr-html-mvp/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl`, and `benchmarks/results/approved-intake-handoff-story180-validation.json`. ADR-002 remains `ACCEPTED` with no status change from this story; Story 180 closes the repo-owned approved-handoff honesty gap but does not resolve ADR-002 Remaining Work. Story status set to `Done`, workflow gates completed, `docs/stories.md` updated, and CHANGELOG entry added. Next step: `/check-in-diff`.
