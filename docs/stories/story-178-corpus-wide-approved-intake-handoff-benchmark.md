# Story 178 — Corpus-Wide Approved Intake Handoff Benchmark

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #1 (Ingest), Requirement #2 (Detect), Zero configuration, Transparency over magic
**Spec Refs**: spec:1 (spec:1.1, C2), spec:8 (B1), spec:9 (B10)
**Build Map Refs**: Category 1 Intake & Format Routing (`exists`, C2 `climb`); Category 8 AI Harnesses & Tooling (`exists`, B1 `hold`); Category 9 Planning Infrastructure (`exists`, B10 `climb`); Input Coverage rows `scanned-pdf-prose` (`passing`), `scanned-pdf-tables` (`passing`), `born-digital-pdf` (`has fixture`), and `image-directory-scans` (`passing`, representative proof only unless corpus widens)
**Decision Refs**: `docs/stories/story-011-ai-planner.md`, `docs/stories/story-027-contact-sheet-auto-intake.md`, `docs/stories/story-169-restore-contact-sheet-intake-and-benchmark-auto-book-type-detection.md`, `docs/stories/story-170-born-digital-pdf-native-text-widening-and-routing-decision.md`, `docs/stories/story-171-maintained-non-toc-born-digital-pdf-lane.md`, `docs/stories/story-176-confirmed-intake-handoff-to-explicit-recipe-runs.md`, `docs/stories/story-177-born-digital-flat-proof-and-heading-cleanup.md`, `benchmarks/golden/auto-book-type-detection/corpus.json`, `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower corpus-wide intake-handoff benchmark ADR
**Depends On**: Story 169, Story 170, Story 171, Story 176

## Goal

Turn the current C2 approved-handoff proof from a representative claim into corpus-wide measured evidence. The locked 10-document maintained intake corpus already proves recommendation quality at `intake_plan_v1`, and Story 176 proves approved handoff on one image-directory input plus two representative PDF inputs. This story should extend the maintained intake proof through `confirm_plan_v1` and `run_dispatch_v1` across the locked corpus, so every maintained launch case leaves an inspected `intake_handoff_v1` row plus first downstream stamped artifact, while every `no-recipe-needed` case leaves an explicit non-launch artifact instead of relying on console output or manual interpretation.

## Acceptance Criteria

- [x] A repeatable corpus-wide approved-handoff benchmark surface exists for the locked `benchmarks/golden/auto-book-type-detection/corpus.json` corpus, and it records per-case plan path, handoff artifact path, launch/non-launch outcome, and any first-downstream-artifact path without manual recipe edits.
- [x] All six locked-corpus cases whose `expected_recipe` is a maintained explicit recipe launch successfully through `run_dispatch_v1` with bounded downstream execution and produce inspectable `intake_handoff_v1` rows plus the first downstream stamped artifact under `output/runs/`.
- [x] All four locked-corpus cases whose `expected_recipe` is `no-recipe-needed` still run through `run_dispatch_v1` and produce inspectable `intake_handoff_v1` rows with explicit `terminal_outcome = skipped` and honest reason fields; no broken downstream run is launched for those cases.
- [x] Manual inspection is recorded for every launched case (`intake_handoff_v1` plus first downstream stamped artifact) and for representative non-launch cases (`intake_handoff_v1` only); the work log names artifact paths and sample fields checked.
- [x] `docs/evals/registry.yaml` and `docs/build-map.md` are updated honestly to reflect whether the approved-handoff proof surface is now corpus-wide, and any remaining image-directory or out-of-corpus residual gap is named explicitly instead of being implied away.

## Out of Scope

- Extending maintained intake coverage to DOCX, XLSX, PPTX, mixed archives, handwritten inputs, or any new family not already in the locked corpus or Story 176's representative proof
- Removing the human approval gate or bypassing `confirm_plan_v1`
- Full downstream validation of every launched run beyond the first stamped artifact needed to prove the handoff seam
- Reviving Story 011's rejected planner surface, hidden auto-routing, or editable pipeline assembly
- Arbitrary corpus expansion beyond the smallest honest coverage change needed for C2 measurement

## Approach Evaluation

- **Simplification baseline**: the current `benchmarks/scripts/run_auto_book_type_detection_eval.py` harness already builds contact sheets, runs overview/zoom/gap analysis, and writes approved `overview_plan_final.jsonl` rows for the locked 10-document corpus. The known gap is strictly post-confirmation: it never invokes `run_dispatch_v1`, and this worktree currently has no retained `benchmarks/results/auto-book-type-detection-story*.json` result files, so fresh reruns are required before any truth-surface claim changes.
- **AI-only**: low value and likely wrong for this seam. The corpus already uses AI where it belongs (overview + zoom classification). The remaining problem is benchmark orchestration, bounded dispatch, scoring, and artifact inspection.
- **Hybrid**: keep the current AI intake stages unchanged, then add deterministic approved-handoff execution and scoring on top of the approved plans. Candidate A is extending the existing benchmark harness with an optional dispatch phase. Candidate B is adding a sibling corpus-wide approved-handoff harness while leaving the classification harness readable and historically stable.
- **Pure code**: plausible and likely sufficient if first-downstream-artifact expectations can be derived from `recommended_recipe`, `input_kind`, and bounded `--downstream-end-at` settings without new model calls. This becomes less attractive only if the existing harness and scorer become too overloaded to keep honest.
- **Repo constraints / prior decisions**: Story 169 intentionally froze the maintained 10-document corpus as a recommendation-only C2 benchmark. Story 176 intentionally split representative approved handoff from that classification benchmark instead of overloading the existing eval immediately. Story 011 remains rejected, so this story cannot drift into a planner. `docs/build-map.md` still keeps C2 in `climb` specifically because the scored corpus stops at `intake_plan_v1` and the handoff proof is not corpus-wide. No new ADR is needed unless the benchmark change reopens planner semantics or broader input-family policy.
- **Existing patterns to reuse**: `benchmarks/scripts/run_auto_book_type_detection_eval.py`, `benchmarks/scorers/auto_book_type_detection.py`, `configs/recipes/recipe-intake-contact-sheet-confirmed-handoff.yaml`, `modules/intake/run_dispatch_v1/main.py`, `modules/intake/intake_plan_utils.py`, `modules/intake/tests/test_intake_chain_e2e.py`, `tests/test_intake_plan_utils.py`, and Story 176's bounded `--downstream-end-at` proof shape.
- **Eval**: the deciding evidence is a fresh driver-backed corpus-wide approved-handoff benchmark, not another classification-only prompt test. The story should choose the smallest honest truth surface:
  - widen `approved-intake-handoff` in place so it becomes the corpus-wide workflow proof, or
  - add a sibling corpus-wide proof surface and keep the current representative proof as a separate narrower signal.
  In either case, launched runs should stop at the first downstream stamped artifact to keep runtime and OCR costs bounded.

## Tasks

- [x] Measure the current corpus-wide baseline and document the exact gap:
  - [x] inventory the locked corpus into maintained-launch (`6`) versus `no-recipe-needed` (`4`) cases
  - [x] confirm that the current `run_auto_book_type_detection_eval.py` harness stops at `confirm_plan_v1` and leaves no corpus-wide `intake_handoff_v1` artifact set
  - [x] record whether any retained result JSONs or prior benchmark artifacts exist locally, or whether the story must rerun the full proof surface fresh
- [x] Decide and implement the smallest honest corpus-wide approved-handoff surface:
  - [x] extend `benchmarks/scripts/run_auto_book_type_detection_eval.py` with an optional dispatch phase, or add a sibling harness that reuses the locked corpus and current classifier outputs
  - [x] keep approval semantics explicit by still going through `confirm_plan_v1` with `--auto-approve`
  - [x] execute `no-recipe-needed` cases through `run_dispatch_v1` too, so they emit inspectable skipped handoff artifacts instead of disappearing from the workflow proof
- [x] Add scoring / reporting that distinguishes:
  - [x] correct launch versus correct explicit non-launch
  - [x] expected first downstream artifact or stage per maintained recipe
  - [x] per-case artifact paths needed for manual inspection and later registry/build-map notes
- [x] Add focused coverage:
  - [x] unit or harness tests for the new corpus-wide approved-handoff result semantics
  - [x] extend `modules/intake/tests/test_intake_chain_e2e.py` or add a sibling benchmark test for bounded launched/non-launch outcomes
  - [x] leave `tests/test_intake_plan_utils.py` unchanged because shared handoff/helper semantics did not change
- [x] Decide whether image-directory should stay outside the locked corpus:
  - [x] if yes, explicitly retain or refresh Story 176's representative image-directory proof in the truth surfaces
  - [ ] if no, add one repo-owned image-directory case and update the corpus plus expectations honestly
- [x] Run fresh driver-backed corpus-wide proofs:
  - [x] six maintained launch cases through `run_dispatch_v1` with bounded downstream `--end-at`
  - [x] four explicit non-launch cases through `run_dispatch_v1`
  - [x] inspect `intake_handoff_v1` for all ten cases and the first downstream stamped artifact for all launched cases
- [x] Decide whether `approved-intake-handoff` should be widened in place or split into representative proof plus corpus-wide proof; update `docs/evals/registry.yaml` accordingly
- [x] If this story changes documented format coverage or graduation reality: update `docs/build-map.md` and record the before/after state honestly
- [x] Check whether the chosen implementation makes any existing benchmark scripts, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [ ] If agent tooling changed: `make skills-check` (not expected for this story)
- [x] If evals or goldens changed: run `/improve-eval` behaviorally for the chosen approved-handoff surface and update `docs/evals/registry.yaml`
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every approved-handoff result traces to plan path, source input, downstream run id, and first stamped artifact
  - [x] T1 — AI-First: no new AI is added to a benchmark orchestration problem
  - [x] T2 — Eval Before Build: baseline handoff behavior is measured before altering the proof surface
  - [x] T3 — Fidelity: launch and non-launch outcomes are recorded honestly without silent substitutions or hidden skips
  - [x] T4 — Modular: benchmark work reuses maintained intake and explicit recipe seams instead of inventing a bespoke planner path
  - [x] T5 — Inspect Artifacts: launched and non-launch artifacts are manually checked, not just counted

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: the benchmark / truth-surface seam between maintained intake planning and approved downstream launch. Primary ownership is the corpus harness under `benchmarks/`, plus the intake handoff artifact surface and the eval/build-map docs that describe C2 honestly.
- **Build-map reality**: Category 1 owns the user-facing value and remains `climb` because the locked corpus still stops at `intake_plan_v1`. Category 8 matters because this is fundamentally an eval/harness story, not a new extraction lane. Category 9 matters because B10 tracks the remaining explicit YAML/config overlap once approved handoff moves beyond representative proof. The relevant input rows are the locked corpus families (`scanned-pdf-prose`, `scanned-pdf-tables`, `born-digital-pdf`) plus `image-directory-scans` if the story decides the current representative proof is insufficient.
- **Substrate evidence**: verified in code that the current benchmark harness already runs the locked corpus through `confirm_plan_v1` (`benchmarks/scripts/run_auto_book_type_detection_eval.py`, 211 lines), the scorer already summarizes per-case and aggregate results (`benchmarks/scorers/auto_book_type_detection.py`, 78 lines), the locked corpus is committed and still points at `6` maintained-launch cases plus `4` `no-recipe-needed` cases (`benchmarks/golden/auto-book-type-detection/corpus.json`, 82 lines), the maintained confirmed-handoff recipe exists (`configs/recipes/recipe-intake-contact-sheet-confirmed-handoff.yaml`, 59 lines), `run_dispatch_v1` already writes `intake_handoff_v1` and supports bounded downstream runs (`modules/intake/run_dispatch_v1/main.py`, 91 lines), and the current e2e/unit tests already cover dry-run handoff artifacts and maintained recipe selection (`modules/intake/tests/test_intake_chain_e2e.py`, 295 lines; `tests/test_intake_plan_utils.py`, 233 lines). This is why the story is `Pending`, not `Draft`: the missing slice is corpus-wide proof, not missing runtime substrate.
- **Data contracts / schemas**: likely touched surfaces are the benchmark result JSON payload, `intake_handoff_v1`, and the docs/eval truth surface. A new benchmark result format does not need `schemas.py` unless it crosses into stamped pipeline artifacts. If fresh corpus-wide evidence exposes missing handoff fields, those fields must be added to `schemas.py` before the story claims them in stamped artifacts.
- **File sizes**: the likely owner files are modest except for truth surfaces: `benchmarks/scripts/run_auto_book_type_detection_eval.py` (211), `benchmarks/scorers/auto_book_type_detection.py` (78), `benchmarks/golden/auto-book-type-detection/corpus.json` (82), `configs/recipes/recipe-intake-contact-sheet-confirmed-handoff.yaml` (59), `modules/intake/run_dispatch_v1/main.py` (91), `modules/intake/intake_plan_utils.py` (298), `modules/intake/tests/test_intake_chain_e2e.py` (295), `tests/test_intake_plan_utils.py` (233), `docs/evals/registry.yaml` (644), and `docs/build-map.md` (586). Keep `docs/evals/registry.yaml` and `docs/build-map.md` edits surgical because they are already large truth surfaces.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md` (`spec:1`, `spec:8`, `spec:9`), `docs/build-map.md`, Stories 011 / 027 / 169 / 170 / 171 / 176 / 177, the locked corpus, the current harness/scorer, and the current handoff/test substrate. No narrower ADR, runbook, scout doc, or note currently owns the corpus-wide approved-handoff benchmark semantics.

## Files to Modify

- `benchmarks/scripts/run_approved_intake_handoff_eval.py` — new sibling harness for the corpus-wide approved-handoff proof surface (new file)
- `benchmarks/scorers/approved_intake_handoff.py` — new scorer/summary surface for launch versus explicit non-launch semantics (new file)
- `tests/test_approved_intake_handoff_benchmark.py` — focused benchmark coverage for first-stage derivation and launch/skip scoring (new file)
- `docs/evals/registry.yaml` — widened `approved-intake-handoff` truth surface to the locked 10-document corpus while keeping image-directory residual explicit
- `docs/build-map.md` — updated C2 wording from representative-only workflow proof to corpus-wide locked-corpus proof with an explicit image-directory residual
- `docs/stories/story-178-corpus-wide-approved-intake-handoff-benchmark.md` — implementation record, checks, and evidence
- `docs/stories.md` — story status updated to `In Progress`

## Redundancy / Removal Targets

- One-off manual shell loops for corpus-wide approved-handoff proof if a maintained harness lands
- Representative-only `approved-intake-handoff` wording if the story replaces it with a wider proof surface
- Duplicated per-recipe first-artifact expectation mapping across benchmark scripts, story notes, and docs if one shared source can own it honestly

## Notes

- The locked corpus is currently all PDFs: `6` maintained-launch cases and `4` explicit `no-recipe-needed` cases. Image-directory coverage currently comes from Story 176's representative proof, not from the locked corpus itself.
- Downstream runs should stay bounded to the first stamped artifact via `--downstream-end-at` so the story proves the handoff seam honestly without paying for unnecessary full pipelines or re-running expensive OCR work beyond the first needed stage.
- If fresh corpus-wide runs reveal that one or more local comparison PDFs are no longer available on this machine, the story must report that as corpus/harness scope drift and keep the truth surfaces honest instead of silently dropping cases.

## Plan

### Exploration Summary

- **Ideal alignment:** proceed. This story closes the exact remaining Ideal/spec gap named in the build map: the maintained intake corpus proves recommendation quality, and the repo has a real approved-handoff seam, but the corpus-wide workflow still is not measured end-to-end through that seam.
- **Relevant build-map state:** Category 1 is `exists` / `climb`, and its C2 note explicitly says the compromise remains because the scored 10-document corpus stops at `intake_plan_v1` while approved handoff is only representative. Categories 8 and 9 already have the harness/planning substrate needed to measure this honestly.
- **Critical substrate verified in code:** the harness, scorer, committed corpus, confirmed-handoff recipe, dispatch module, and targeted tests all exist. The missing substrate is narrow: corpus-wide bounded launch orchestration plus truthful scoring / documentation.
- **Fresh environment note:** this worktree has no retained `benchmarks/results/auto-book-type-detection-story*.json` outputs, so fresh reruns are required before changing `docs/evals/registry.yaml` or `docs/build-map.md`.
- **Fresh baseline:** `python benchmarks/scripts/run_auto_book_type_detection_eval.py --output benchmarks/results/story178-baseline-recommendation-only.json --run-root output/runs/story178-baseline-recommendation-only` completed `10/10` docs with `accuracy = 1.0`, `overall = 1.0`, and `pass_rate = 1.0`. Sample passing artifacts: `output/runs/story178-baseline-recommendation-only/tbotb-mini/overview_plan_final.jsonl`, `output/runs/story178-baseline-recommendation-only/rfp/overview_plan_final.jsonl`, and `output/runs/story178-baseline-recommendation-only/release-forms/overview_plan_final.jsonl`. The same run produced no `intake_handoff*.jsonl` artifacts, confirming that the current gap is strictly post-`confirm_plan_v1`.

### Eval-First Gate

- **Baseline first:** run or trace the current locked-corpus harness and confirm exactly where it stops, what artifacts it leaves, and how many cases would launch today.
- **What the baseline must answer:** can the existing classification harness be widened cleanly, or will a sibling approved-handoff harness be clearer and safer for historical eval readability?
- **Honesty gate:** if the locked corpus remains PDF-only after exploration, explicitly decide whether Story 176's image-directory proof is sufficient to keep that family honest or whether one repo-owned image-directory case must be added.

### Implementation Tasks

1. Freeze the proof shape and approval-sensitive decisions (`S`)
   - Keep `auto-book-type-detection` as the recommendation-only surface unless implementation proves a shared helper extraction is clearly smaller and keeps semantics unchanged.
   - Widen `approved-intake-handoff` in place from `3` representative proofs to the locked `10`-document corpus, because the eval ID already owns the workflow seam Story 176 introduced.
   - Treat image-directory as an explicit residual side proof by default; only widen the locked corpus if exploration turns up a repo-owned image-directory fixture that makes the claim materially more honest without opening a separate corpus-maintenance story.

2. Add a sibling corpus-wide approved-handoff harness (`M`)
   - Introduce a dedicated benchmark runner under `benchmarks/scripts/` for approved handoff rather than overloading the classification harness result payload.
   - Reuse the locked corpus, current contact-sheet intake stages, and `confirm_plan_v1 --auto-approve`.
   - Route every case through `run_dispatch_v1`, using bounded `--downstream-end-at` settings for launchable recipes and preserving explicit skipped outcomes for `no-recipe-needed`.
   - Emit a result row per case with `plan_artifact`, `handoff_artifact`, `terminal_outcome`, `terminal_reason`, `downstream_run_id`, and `first_downstream_artifact` when a launch occurs.

3. Add focused scoring and coverage (`S`)
   - Add a handoff-specific scorer/summary surface instead of stretching `benchmarks/scorers/auto_book_type_detection.py` beyond classification semantics.
   - Add one focused benchmark/unit test for the new per-case result semantics and extend the intake e2e coverage only where real dispatch behavior is at risk.
   - Reuse the existing `prepare_confirmed_handoff()` test pattern unless a fresh corpus proof exposes a missing shared helper.

4. Refresh the truth surfaces with fresh inspected evidence (`M`)
   - Run the new corpus-wide handoff harness across all `10` locked cases.
   - Inspect `intake_handoff_v1` for all `10` cases and the first downstream stamped artifact for all `6` launches.
   - Update `docs/evals/registry.yaml` and `docs/build-map.md` only as far as the fresh manual inspection justifies.

5. Close redundancy honestly (`XS`)
   - Remove or supersede any manual shell-loop proof recipe that becomes redundant once the harness lands.
   - Keep representative-only wording only where image-directory still remains outside the locked corpus.

### Impact Analysis

- **Primary blast radius:** benchmark harness behavior, approved-handoff proof semantics, and the C2 truth wording in the eval registry and build map.
- **Secondary blast radius:** image-directory honesty if the story decides the current representative proof is insufficient for the widened claim.
- **Structural health note:** `benchmarks/scripts/run_auto_book_type_detection_eval.py` and `benchmarks/scorers/auto_book_type_detection.py` are still small and readable; keeping workflow-proof logic in a sibling harness/scorer is the lowest-risk way to preserve that clarity.
- **Human-approval blockers:** whether image-directory should remain a representative side proof for this story, and whether widening `approved-intake-handoff` in place is preferred over creating a second corpus-wide workflow eval ID.
- **Main risk:** over-claiming corpus-wide coverage while image-directory remains representative only, or discovering that the current `intake_handoff_v1` row lacks enough first-artifact metadata to make the corpus proof inspectable without a small shared-helper/schema adjustment.

### What Done Looks Like

- The repo has one honest corpus-wide approved-handoff proof surface for the locked maintained intake corpus.
- Six maintained cases launch and leave inspected first-stage artifacts.
- Four `no-recipe-needed` cases leave explicit skipped handoff rows.
- The build map and eval registry no longer rely on a representative-only handoff note for the locked corpus.
- Any residual image-directory gap is explicit, not accidental.

## Work Log

20260401-1835 — story created from `/triage`: scoped the remaining C2 honesty gap after Story 176. Evidence reviewed in this pass: `docs/build-map.md` still says C2 remains `climb` because the scored 10-document corpus stops at `intake_plan_v1` and approved handoff is only representative; `benchmarks/golden/auto-book-type-detection/corpus.json` is still the locked 10-document corpus with `6` maintained-launch and `4` `no-recipe-needed` cases; `benchmarks/scripts/run_auto_book_type_detection_eval.py` still stops at `confirm_plan_v1`; `configs/recipes/recipe-intake-contact-sheet-confirmed-handoff.yaml` and `modules/intake/run_dispatch_v1/main.py` prove the handoff seam exists in code; and this worktree currently has no retained `benchmarks/results/auto-book-type-detection-story*.json` outputs, so fresh reruns are required. Result: the story is `Pending`, not `Draft`, because the harness, dispatch, and test substrate already exist and the missing slice is bounded corpus-wide proof plus truth-surface updates. Next step: `/build-story` should measure the current harness baseline and choose whether to extend the existing classification harness or add a sibling approved-handoff harness.
20260401-2110 — `/build-story` exploration and eval-first baseline: verified that Story 178 is honestly buildable as a narrow benchmark/evidence slice, not blocked by missing runtime substrate. Files likely to change: a new approved-handoff benchmark runner/scorer under `benchmarks/`, targeted intake benchmark tests, and the C2 truth surfaces in `docs/evals/registry.yaml` / `docs/build-map.md`; files at risk are `modules/intake/run_dispatch_v1/main.py`, `modules/intake/intake_plan_utils.py`, and the existing classification harness if we overload it. Decision docs and planning context rechecked in this pass: `docs/ideal.md`, `docs/spec.md` (`spec:1.1`, `spec:8`, `spec:9`), `docs/build-map.md`, Stories 011 / 027 / 169 / 170 / 171 / 176 / 177, and no narrower ADR in `docs/decisions/`, `docs/runbooks/`, `docs/scout/`, or `docs/notes/`. Relevant build-map/input rows remain Category 1 `exists` / C2 `climb`, Category 8 `exists` / B1 `hold`, Category 9 `exists` / B10 `climb`, with `scanned-pdf-prose` and `scanned-pdf-tables` marked `passing`, `born-digital-pdf` marked `has fixture`, and `image-directory-scans` still only representative at the corpus-wide handoff layer. Critical substrate verified versus missing: `benchmarks/golden/auto-book-type-detection/corpus.json` still resolves locally and contains `6` launchable maintained cases plus `4` `no-recipe-needed` cases; `benchmarks/scripts/run_auto_book_type_detection_eval.py` clearly runs `builder -> overview -> zoom -> gap -> confirm` and stops at `overview_plan_final.jsonl`; `find output/runs/story178-baseline-recommendation-only -name 'intake_handoff*.jsonl'` returned nothing; `modules/intake/run_dispatch_v1/main.py` plus `prepare_confirmed_handoff()` in `modules/intake/intake_plan_utils.py` already support launched, skipped, blocked, and bounded `--downstream-end-at` semantics; and `modules/intake/tests/test_intake_chain_e2e.py` / `tests/test_intake_plan_utils.py` already cover dry-run handoff rows, `no_recipe_needed`, unsupported input kinds, and forwarded `--end-at`. Patterns to follow: keep `auto-book-type-detection` recommendation-only, reuse Story 176's bounded first-artifact inspection shape, and prefer a sibling workflow-proof harness over mutating the classification scorer into a mixed semantic surface. Potential redundancy/removal: manual shell loops or representative-only wording once the corpus-wide harness lands. Surprises found: no retained Story 169/170/171 benchmark JSONs are present in this worktree, the locked corpus is still PDF-only, and the fresh rerun `python benchmarks/scripts/run_auto_book_type_detection_eval.py --output benchmarks/results/story178-baseline-recommendation-only.json --run-root output/runs/story178-baseline-recommendation-only` still finished `10/10` docs with `accuracy = 1.0`, `overall = 1.0`, and `pass_rate = 1.0`, confirming that the remaining gap is strictly the post-confirm handoff seam. Next step: stop at the approval gate and, if approved, implement a sibling corpus-wide `approved-intake-handoff` harness while keeping image-directory honesty explicit.
20260401-2134 — implemented the sibling corpus-wide proof surface and refreshed the C2 truth surfaces. Code/files changed: added `benchmarks/scripts/run_approved_intake_handoff_eval.py`, `benchmarks/scorers/approved_intake_handoff.py`, and `tests/test_approved_intake_handoff_benchmark.py`; updated `docs/evals/registry.yaml`, `docs/build-map.md`, `docs/stories.md`, and this story file; no runtime/seam changes were required in `modules/intake/run_dispatch_v1/main.py` or `modules/intake/intake_plan_utils.py`, because the existing handoff substrate was already sufficient. Fresh proof run: `python benchmarks/scripts/run_approved_intake_handoff_eval.py --output benchmarks/results/approved-intake-handoff-story178.json --run-root output/runs/story178-approved-intake-handoff` completed `10/10` cases with `pass_rate = 1.0`, `overall = 1.0`, `launched = 6`, `skipped = 4`, and `failed_runs = 0`. Manual inspection for all 10 handoff rows confirmed explicit outcomes and downstream IDs/paths: launched rows at `output/runs/story178-approved-intake-handoff/tbotb-mini/intake_handoff.jsonl`, `output/runs/story178-approved-intake-handoff/onward-unknown/intake_handoff.jsonl`, `output/runs/story178-approved-intake-handoff/astrosmash-manual/intake_handoff.jsonl`, `output/runs/story178-approved-intake-handoff/rfp/intake_handoff.jsonl`, `output/runs/story178-approved-intake-handoff/release-forms/intake_handoff.jsonl`, and `output/runs/story178-approved-intake-handoff/collection-checklist/intake_handoff.jsonl` all stamped `terminal_outcome = launched` with the expected recipe/input flag/path; explicit non-launch rows at `output/runs/story178-approved-intake-handoff/scanned-prose-mini/intake_handoff.jsonl`, `output/runs/story178-approved-intake-handoff/button-instructions/intake_handoff.jsonl`, `output/runs/story178-approved-intake-handoff/libin-letter/intake_handoff.jsonl`, and `output/runs/story178-approved-intake-handoff/memorial-card/intake_handoff.jsonl` all stamped `terminal_outcome = skipped` with `terminal_reason = no_recipe_needed`. Manual inspection for all 6 launched first downstream artifacts also passed: `output/runs/story178-approved-intake-handoff-tbotb-mini-recipe-born-digital-pdf-marker-lite-html-mvp/01_extract_pdf_marker_lite_html_v1/pages_html.jsonl` stamped `3` page rows and the first page text begins `To Be or Not To Be -- Mini...`; `output/runs/story178-approved-intake-handoff-onward-unknown-recipe-pdf-ocr-html-mvp/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl` stamped `127` `page_image_v1` rows with page `1` sourcing `Onward to the Unknown.pdf` and image `page-001.jpg`; `output/runs/story178-approved-intake-handoff-astrosmash-manual-recipe-pdf-ocr-html-mvp/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl` stamped `6` rows with page `1` sourcing `Astrosmash_-_Manual_-_INT.pdf`; `output/runs/story178-approved-intake-handoff-rfp-recipe-born-digital-pdf-non-toc-html-mvp/01_extract_pdf_marker_lite_html_v1/pages_html.jsonl` stamped `2` rows and the first page text begins `REQUEST FOR PROPOSAL: WEBSITE DEVELOPMENT...`; `output/runs/story178-approved-intake-handoff-release-forms-recipe-born-digital-pdf-non-toc-html-mvp/01_extract_pdf_marker_lite_html_v1/pages_html.jsonl` stamped `2` rows and the first page text begins `ACKNOWLEDGMENT OF RISK AND RELEASE OF LIABILITY...`; and `output/runs/story178-approved-intake-handoff-collection-checklist-recipe-pdf-ocr-html-mvp/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl` stamped `12` rows with page `1` sourcing `CollectionChecklist.pdf` and image `page-001.jpg`. Focused tests passed via `pytest -q tests/test_approved_intake_handoff_benchmark.py modules/intake/tests/test_intake_chain_e2e.py tests/test_intake_plan_utils.py` (`23 passed, 1 skipped`); repo checks passed via `make lint` and `make test` (`418 passed, 4 warnings`); and direct benchmark-file lint passed via `python -m ruff check benchmarks/scorers/approved_intake_handoff.py benchmarks/scripts/run_approved_intake_handoff_eval.py tests/test_approved_intake_handoff_benchmark.py`. Docs/truth-surface decision: widened `approved-intake-handoff` in place to the locked 10-document maintained intake PDF corpus, but kept image-directory explicit as a representative residual from Story 176 rather than silently claiming it as part of the locked corpus-wide proof. Outcome: Build complete for Story 178; next step is `/validate`, not `/mark-story-done`.
20260401-2155 — `/mark-story-done` close-out pass completed with fresh evidence. Workflow gates now reflect the current state: build complete, validation complete, and story marked done. Fresh checks in this pass: `python -m pytest tests/` passed (`418 passed, 4 warnings`), `python -m ruff check modules/ tests/` passed, and representative artifact reinspection reconfirmed the launched handoff row at `output/runs/story178-approved-intake-handoff/tbotb-mini/intake_handoff.jsonl`, the skipped handoff row at `output/runs/story178-approved-intake-handoff/scanned-prose-mini/intake_handoff.jsonl`, the bounded PDF first-stage artifact at `output/runs/story178-approved-intake-handoff-onward-unknown-recipe-pdf-ocr-html-mvp/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl`, and the bounded born-digital first-stage artifact at `output/runs/story178-approved-intake-handoff-rfp-recipe-born-digital-pdf-non-toc-html-mvp/01_extract_pdf_marker_lite_html_v1/pages_html.jsonl`. Story status and index row were moved to `Done`, and a Story 178 changelog entry was added. Recommended next step: `/check-in-diff`.
