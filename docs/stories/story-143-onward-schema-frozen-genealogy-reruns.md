# Story 143 — Onward Schema-Frozen Genealogy Reruns

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Fidelity to Source, Dossier-ready output
**Spec Refs**: C1 (Multi-Stage OCR Pipeline), C2 (Format-Specific Conversion Recipes), C6 (Expensive OCR for Quality)
**Decision Refs**: `docs/decisions/adr-001-source-aware-consistency-strategy/adr.md`, `docs/runbooks/golden-build.md`, Story 141 and Story 142 work logs
**Depends On**: Story 142

## Goal

Implement the first source-aware rerun slice under ADR-001 for the Onward genealogy converter: consume the chapter-first consistency signals from Story 142, selectively rerun only the strongest culprit pages with a frozen schema hypothesis and bounded context from source artifacts, accept reruns only when deterministic checks show structural improvement without content loss, and rebuild chapters to verify that the reviewed drift chapters improve without regressing the reviewed good references.

## Acceptance Criteria

- [x] In a fresh verification run reusing existing upstream artifacts where possible, the rerun path targets only the flagged strong-candidate pages or bounded adjacent context justified by Story 142's report, and records every rerun candidate, model call, schema hint, acceptance/rejection reason, and before/after artifact path
- [x] Rebuilt chapters materially improve the reviewed bad set from Story 142: `chapter-013.html`, `chapter-014.html`, and `chapter-015.html` are no longer flagged by `validate_onward_genealogy_consistency_v1`, and `chapter-010.html` is either no longer flagged or has a strictly lower drift score with its previous flagged reasons reduced
- [x] Manual inspection confirms no regression in the reviewed non-regression set, including `chapter-009.html`, `chapter-018.html`, and `chapter-020.html`
- [x] Original page HTML remains available alongside any rerun output, and rejected rerun candidates fall back cleanly to the original artifact without silent replacement

## Out of Scope

- Broader run-aware or chapter-aware extraction from the start
- A generic all-structure consistency framework beyond the Onward genealogy slice
- HTML-only normalization as the primary fix path
- Clearing every additional detector-flagged chapter outside the reviewed hand-validated target set from Story 142 (`chapter-016.html`, `chapter-017.html`, `chapter-021.html`, `chapter-022.html`) unless the bounded rerun slice fixes them incidentally
- Forcing the first rerun implementation into the single-pass main Onward recipe before the bounded validation loop proves the seam is correct
- Hand-editing generated HTML outside the pipeline
- Closing ADR-001 itself

## Approach Evaluation

- **Simplification baseline**: Before building a rerun loop, measure whether a single strong-model rerun over Story 142's strongest culprit pages and bounded context already repairs the reviewed drift signatures when guided by a frozen canonical header/schema hint.
- **AI-only**: Direct reruns may fix the pages, but they are not enough alone because provenance, acceptance/rejection, and fallback behavior still need deterministic orchestration.
- **Hybrid**: Leading candidate. Use deterministic logic from Story 142 for target selection and acceptance checks, and use AI only for the rerun extraction itself.
- **Pure code**: Not credible as the main repair engine. Story 141's AI-first baselines already showed broader source-aware extraction is stronger than more HTML-only heuristics for these drift cases.
- **Repo constraints / prior decisions**: ADR-001 settles the direction as `extract -> detect/cluster -> selective rerun -> light canonicalization`. Story 142 measured `strong_rerun_candidate_page_coverage=0.1607`, which keeps this recipe below the redesign threshold and justifies targeted reruns instead of broader extraction granularity.
- **Existing patterns to reuse**: `table_rescue_onward_tables_v1` targeted retry and candidate-acceptance patterns, Story 142's `validate_onward_genealogy_consistency_v1`, `load_artifact_v1` reuse flows, and the existing Onward resume/validation recipe structure.
- **Eval**: The deciding test is whether rerunning only the reviewed strong pages `[34,35,57,64,69]` or a slightly expanded bounded context clears the Story 142 drift signals on the rebuilt chapters without reopening `chapter-009`, `chapter-018`, or `chapter-020`.

## Tasks

- [x] Measure the bounded strongest-model rerun baseline on Story 142's strongest culprit pages, using a frozen genealogy schema hint and nearby context pages or exemplar HTML where needed
- [x] Choose and implement the smallest recipe-scoped rerun mechanism that preserves original page HTML, stores rerun outputs separately, and records acceptance/rejection decisions before any rebuilt chapter output consumes them
- [x] Add deterministic acceptance/rejection checks for rerun candidates, including schema/header conformance, content-retention guardrails, and fallback to the original artifact on rejection
- [x] Rebuild chapters from accepted reruns, rerun `validate_onward_genealogy_consistency_v1`, and record before/after metrics for the reviewed bad and good chapter set
- [x] Add focused regression coverage for rerun targeting, candidate acceptance/rejection, provenance/fallback behavior, and at least one chapter-level before/after success path
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test` (`594 passed, 5 skipped`)
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py` with artifact reuse, verify artifacts in `output/runs/`, and manually inspect rebuilt chapter HTML plus rerun decision reports
  - [x] If agent tooling changed: `make skills-check` (not needed; no agent tooling changed)
- [x] If evals or goldens changed: run `/verify-eval` and update `docs/evals/registry.yaml` (not needed; no eval or golden files changed)
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: accepted and rejected reruns trace back to source pages, original page HTML, model inputs, and decision reports
  - [x] T1 — AI-First: the rerun engine uses AI only where Story 142 proved deterministic detection alone is insufficient
  - [x] T2 — Eval Before Build: bounded strongest-model rerun baselines were measured first, then widened only when the strong-page loop proved too narrow
  - [x] T3 — Fidelity: accepted reruns preserved names, dates, totals, and subgroup context, and rejected page `32` fell back to the original HTML cleanly
  - [x] T4 — Modular: the rerun path remains recipe-scoped and avoids hardcoded family-name/page overrides inside generic code
  - [x] T5 — Inspect Artifacts: rerun outputs, rebuilt chapters, and acceptance reports were manually inspected alongside the validator reports

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: A new recipe-scoped adapter over `page_html_v1` now owns the rerun path: `rerun_onward_genealogy_consistency_v1`, driven by a bounded `build -> validate -> rerun -> rebuild -> revalidate` recipe loop instead of an early main-recipe insertion.
- **Data contracts / schemas**: The shipped slice preserves `page_html_v1` compatibility so existing builders can consume accepted reruns directly, while sidecar JSON/JSONL reports keep original vs candidate vs final HTML inspectable without introducing a new cross-stage schema.
- **File sizes**: `configs/recipes/recipe-onward-images-html-mvp.yaml` is 192 lines, `modules/validate/validate_onward_genealogy_consistency_v1/main.py` is 488 lines, `modules/adapter/table_rescue_onward_tables_v1/main.py` is 1400 lines, `modules/build/build_chapter_html_v1/main.py` is 1383 lines, `tests/test_validate_onward_genealogy_consistency_v1.py` is 191 lines, and `schemas.py` is 964 lines. Prefer a focused new stage and test file over further growth in the oversized rescue or build modules.
- **Decision context**: Reviewed `docs/ideal.md`, `docs/spec.md`, ADR-001, Story 141, and Story 142. The decision boundary is already set: targeted reruns are justified for this recipe, but only with deterministic gating and provenance.

## Files to Modify

- `modules/adapter/rerun_onward_genealogy_consistency_v1/module.yaml` — declare the recipe-scoped rerun stage (new file)
- `modules/adapter/rerun_onward_genealogy_consistency_v1/main.py` — target selection, schema-frozen rerun orchestration, candidate acceptance/rejection, and artifact emission (new file)
- `configs/recipes/story-143-onward-genealogy-reruns-validate.yaml` — reuse Story 142's artifact root for a bounded rerun validation path (new file)
- `tests/test_rerun_onward_genealogy_consistency_v1.py` — focused rerun targeting and acceptance/rejection coverage (new file)
- `docs/stories/story-143-onward-schema-frozen-genealogy-reruns.md` — work log and validation evidence
- `docs/decisions/adr-001-source-aware-consistency-strategy/adr.md` — update remaining work if the implementation seam changes materially
- `configs/recipes/recipe-onward-images-html-mvp.yaml` — optional follow-up only if the bounded rerun loop proves the seam is safe to linearize (192 lines)

## Redundancy / Removal Targets

- Temporary one-off rerun probes or prompts created during Story 141/143 experimentation once the rerun module owns the path
- Story 144 now captures the next document-level consistency-planning follow-up instead of leaving the remaining drift patterns implicit in Story 143's work log

## Notes

- Story 142 established the current target set and gating signal:
  - reviewed bad chapters still needing repair: `chapter-010.html`, `chapter-013.html`, `chapter-014.html`, `chapter-015.html`
  - reviewed good references to protect: `chapter-009.html`, `chapter-018.html`, `chapter-020.html`
  - strongest rerun pages from the validated report: `34`, `35`, `57`, `64`, `69`
  - current recommendation: `targeted_reruns_justified`
- The cheap validation path depends on the existing `page_html_v1` rows carrying valid `image` paths back to the source page images. If the reuse recipe cannot guarantee those paths remain valid, Story 143 needs an explicit image-manifest load step or a different reuse seam.
- The open implementation question is no longer seam choice; the shipped recipe proves the bounded rerun loop. The remaining question is how document-wide consistency planning should drive later repairs, especially for hard mixed-heading pages such as source page `32` where direct HTML reruns still underperform despite better-targeted context.
- This story should prefer bounded rerun context and strict fallback behavior over broad aggressive automation.
- Story 143 finished by widening from the original strong pages to the justified bounded coarse set `30,31,32,33,34,35,56,57,62,63,64,67,68,69`. That let cheap deterministic normalization land on most pages before OCR was spent on the harder cases.
- ADR-001 still leaves the representation target open. Story 143's outcome is that direct HTML reruns are good enough for most reviewed Onward genealogy pages, but the residual mixed-heading, fragmented-table, and fused-header cases should now be re-evaluated through document-wide planning artifacts rather than a single hard-page fix.

## Plan

### Exploration Findings

- Story 142's target-selection logic is chapter-first and post-build, not page-first. The validator that produced the rerun candidates runs after `build_chapters`, so the first rerun implementation cannot honestly be treated as a trivial single stage dropped before build.
- The existing Onward pipeline already carries source image paths forward in `page_html_v1`. The current `table_rescue_onward_tables_v1` adapter depends on `row["image"]` and uses the page image plus current HTML context for targeted reruns, so Story 143 should reuse that pattern instead of inventing new source-image plumbing.
- The cheap validation path can still stay artifact-reuse friendly. The shared `story140-onward-targeted-rescue-r19` `page_html_v1` artifact preserves absolute `image` paths into the Onward input image directory, which means a validation recipe can reuse current page HTML while still reading original source images for reruns.
- The main architectural risk is recipe shape, not model choice. Because target selection happens after build, the clean first slice is a bounded `build -> validate -> rerun -> rebuild -> revalidate` loop in a story-scoped validation recipe. Wiring the same logic into the single-pass main recipe should be deferred until that loop proves the seam is correct.
- The strongest reuse candidate is not a greenfield rerun engine. `table_rescue_onward_tables_v1` already has image encoding, OCR call wrappers, current-HTML context prompts, and conservative acceptance/rejection scoring. Story 143 should either extract those reusable parts cleanly or follow the same conventions in a new focused module.

### Ideal Alignment Gate

- This story closes a direct Ideal gap: the current pipeline can detect genealogy consistency drift, but it still cannot repair that drift from source in a traceable, bounded way.
- The story moves toward the Ideal by preferring source-aware reruns over HTML-only cleanup and by preserving fallback behavior when a rerun candidate is not trustworthy.
- No new project-level compromise is being introduced if the rerun loop stays selective and evidence-driven. Story 142 already supplied the detection mechanism that tells us when targeted reruns stop being the right answer.

### Eval / Baseline

- Current verified baseline comes from Story 142's validation run `story142-onward-genealogy-consistency-r1`:
  - reviewed bad set still flagged: `chapter-010.html`, `chapter-013.html`, `chapter-014.html`, `chapter-015.html`
  - reviewed good set still clean: `chapter-009.html`, `chapter-018.html`, `chapter-020.html`
  - strongest rerun pages: `34`, `35`, `57`, `64`, `69`
  - current recommendation: `targeted_reruns_justified`
- Simplest-first AI baseline already exists directionally from Story 141: bounded strong-model normalization over the relevant genealogy material materially beat the current deterministic cleanup. Story 143 therefore should begin by measuring the smallest source-aware rerun over the strong candidate pages before committing to a broader loop.
- The primary eval for this story is existing and reusable: rerun `validate_onward_genealogy_consistency_v1` after rebuilding chapters from accepted reruns, then manually inspect the reviewed chapter set.

### Implementation Plan

#### Task 1 — Measure the bounded rerun baseline

- Files: story work log plus either an isolated prototype script or the new rerun module in dry-run mode
- Change:
  - Use the strongest current culprit set from Story 142 (`34,35,57,64,69`) as the initial rerun scope.
  - Feed source image + current HTML + frozen schema hint/context to a strong model.
  - Inspect whether those pages can be repaired cleanly enough to justify automation.
- Risk:
  - If the bounded source-aware rerun still produces unstable HTML or drops content, the story may need to narrow to structured output or reduce scope further.
- Done when:
  - the work log records the bounded rerun baseline with concrete artifact paths and whether direct HTML reruns appear viable

#### Task 2 — Implement a provenance-preserving rerun adapter

- Files: `modules/adapter/rerun_onward_genealogy_consistency_v1/{module.yaml,main.py}` plus focused tests
- Change:
  - Build a focused rerun adapter over `page_html_v1` rows that selects only the requested page targets, calls the source-aware rerun model, and stores original vs candidate vs accepted output with decision metadata.
  - Reuse `table_rescue_onward_tables_v1` patterns for image loading, prompt construction, and acceptance scoring where they are still appropriate.
- Risk:
  - Blindly cloning rescue logic would re-import Arthur/Emilie-specific assumptions; shared logic should be generic and recipe-scoped.
- Done when:
  - the adapter can emit accepted rerun pages plus a decision report without mutating untouched pages

#### Task 3 — Build the bounded validation loop

- Files: `configs/recipes/story-143-onward-genealogy-reruns-validate.yaml`, optional small doc/config updates
- Change:
  - Create a story-scoped recipe that:
    - loads the current reused page artifacts
    - builds chapters
    - runs `validate_onward_genealogy_consistency_v1` to confirm or refresh targets
    - reruns only the bounded candidate set
    - rebuilds chapters from accepted reruns
    - re-runs the consistency validator
  - Keep this loop explicit instead of forcing it into the main recipe on the first pass.
- Risk:
  - If the loop is too awkward or duplicated to maintain, that is evidence the recipe needs a stronger native rerun orchestration seam before main-recipe adoption.
- Done when:
  - a fresh driver run can produce before/after artifacts and a final consistency report over the rebuilt chapters

#### Task 4 — Acceptance checks, regression coverage, and manual inspection

- Files: `tests/test_rerun_onward_genealogy_consistency_v1.py`, story work log, maybe small shared helpers if needed
- Change:
  - Add tests for target selection, `missing_image` / fallback behavior, acceptance/rejection scoring, and preservation of untouched pages.
  - Run the bounded validation recipe and manually inspect the rebuilt HTML chapters plus rerun decision reports.
- Risk:
  - Tests that only validate isolated page acceptance without the rebuild/revalidate loop would miss the story's real goal.
- Done when:
  - the rerun path is fixture-covered, the reused driver run succeeds, and the reviewed bad/good chapter set is manually rechecked

#### Task 5 — Decide whether main-recipe wiring belongs in this story

- Files: optionally `configs/recipes/recipe-onward-images-html-mvp.yaml`
- Change:
  - Only wire the rerun adapter into the main recipe if the bounded validation loop proves the seam is linearizable without a second build/validate cycle or hidden duplication.
  - Otherwise, leave main-recipe adoption for an explicit follow-up after the bounded story succeeds.
- Risk:
  - Forcing production wiring too early would make this story larger and muddier than the evidence supports.
- Done when:
  - the story explicitly records whether main-recipe wiring was absorbed or deferred, with rationale

### Scope Adjustment

- Small coherent scope contraction: do not treat immediate main-recipe wiring as mandatory. The first objective is to prove the rerun loop on a bounded validation recipe.
- Small coherent scope expansion: the story must explicitly verify source-image availability in the reused validation path, because without valid `image` fields the rerun mechanism cannot actually be source-aware.

### Human Approval Gate

- Recommended implementation direction: build a bounded `build -> validate -> rerun -> rebuild -> revalidate` loop first, backed by a focused rerun adapter and Story 142's existing validator.
- Main open question: whether direct HTML reruns are stable enough, or whether the first rerun slice should switch to a more structured intermediate. The bounded baseline in Task 1 should answer that before the adapter grows too much.
- No new dependencies are expected.
- Success is falsified if:
  - the bounded rerun baseline cannot improve the reviewed strong pages without content loss
  - the validation loop cannot access real source images for rerun targets
  - the rebuilt chapters do not materially improve the reviewed bad set or regress the reviewed good set

## Work Log

20260314-2147 — story created: follow-up story split from ADR-001 remaining work after Story 142 proved targeted reruns are justified and the next implementation move should be schema-frozen selective reruns, not broader extraction redesign
20260314-2232 — build-story exploration: traced the rerun seam through the main Onward recipe, Story 142's post-build validator, and `table_rescue_onward_tables_v1`; found that source-image access already exists via `page_html_v1.image`, but the first clean implementation seam is a bounded `build -> validate -> rerun -> rebuild -> revalidate` loop, not a naive pre-build insertion
20260314-2238 — build-story plan: narrowed Story 143 around a validation-first rerun loop, explicitly deferred mandatory main-recipe wiring, and added the source-image prerequisite plus the still-open direct-HTML-vs-structured-output decision from ADR-001
20260314-2316 — first rerun slice shipped: implemented `rerun_onward_genealogy_consistency_v1`, the story-scoped validation recipe, and focused regression tests; the initial strong-page-only run accepted `4/5` pages but left all `8` previously flagged chapters still flagged, which proved the original strong-page set was too narrow for chapter-level success
20260314-2342 — coarse-page expansion: widened the validation recipe to the justified bounded coarse set `30,31,32,33,34,35,56,57,62,63,64,67,68,69`, added deterministic normalization acceptance before OCR, and locked the new target-selection behavior into test coverage
20260314-2348 — verification complete: fresh reused-artifact run `story143-onward-genealogy-reruns-r1` targeted `14` pages and accepted `13` (`30,31,33,34,56,62,63,64,67,69` via normalized-existing; `35,57,68` via OCR), rejected `32` back to the original HTML, cleared `chapter-013.html`, `chapter-014.html`, and `chapter-015.html`, reduced `chapter-010.html` from drift score `45` to `25`, and preserved `chapter-009.html`, `chapter-018.html`, and `chapter-020.html` as clean references
20260314-2352 — closeout: completed `make test`, `make lint`, `git diff --check`, updated ADR-001 with the direct-HTML-vs-structured-output evidence, and created Story 144 for the next document-level consistency-planning follow-up
