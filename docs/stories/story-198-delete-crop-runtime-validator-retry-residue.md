---
title: "Delete Retired Crop Retry/Validator Residue from Guided Runtime"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #4 (Illustrate), Requirement #6 (Validate), Fidelity to the source, Transparency over magic, Graduate, don't accumulate"
spec_refs:
  - "spec:4"
  - "spec:4.1"
  - "spec:4.2"
  - "spec:8"
adr_refs: []
depends_on:
  - "184"
category_refs:
  - "spec:4"
  - "spec:8"
compromise_refs:
  - "B1"
  - "C4"
  - "C5"
input_coverage_refs:
  - "image-directory-scans"
  - "scanned-pdf-tables"
architecture_domains:
  - "document_structure_and_consistency"
roadmap_tags:
  - "campaign:maintained-intake-honesty"
legacy_system: ""
---

# Story 198 — Delete Retired Crop Retry/Validator Residue from Guided Runtime

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/runbooks/crop-eval-workflow.md`, `docs/stories/story-133-gemini-flash-crop-detector.md`, `docs/stories/story-183-crop-benchmark-substrate-and-c5-validation-surface.md`, `docs/stories/story-184-collapse-bounded-crop-runtime-to-single-stage-flash.md`, `configs/recipes/recipe-onward-images-html-mvp.yaml`, `tests/test_crop_runtime_recipe_contract.py`, and `None found after search in docs/decisions/`, `docs/scout/`, and `docs/notes/` for a narrower crop-runtime deletion ADR
**Depends On**: Story 184

## Goal

Story 184 proved the maintained Onward lane can publish clean crops and final HTML with the Flash detector, bounded caption second pass, and `trim_layout_text`, while the old retry, refine, and validation loops stay disabled. Yet `crop_illustrations_guided_v1` and its `module.yaml` still expose that retired retry/refine/validate surface, and the maintained recipe still carries now-dead `rescue_retry_max` / `rescue_require_caption_schema` residue. This story should delete that retired surface from the shared guided-crop runtime, keep the currently needed caption-assist and layout-trim behavior, and re-prove the reviewed Onward crop/build seam so the code, CLI schema, tests, and docs all match the actual maintained runtime.

## Acceptance Criteria

- [x] `modules/extract/crop_illustrations_guided_v1/main.py` and `modules/extract/crop_illustrations_guided_v1/module.yaml` no longer expose or dispatch the retired retry/refine/validate parameter family:
  - [x] `rescue_retry_on_overlap`
  - [x] `rescue_retry_on_missing`
  - [x] `rescue_retry_max`
  - [x] `rescue_require_caption_schema`
  - [x] `rescue_retry_on_text`
  - [x] `rescue_refine_boxes`
  - [x] `rescue_refine_max_tokens`
  - [x] `rescue_refine_min_area_ratio`
  - [x] `rescue_validate_crops`
  - [x] `rescue_validate_model`
  - [x] `rescue_validate_max_tokens`
- [x] The maintained Onward recipe and contract tests no longer carry stale keys needed only by those removed branches, while the retained contract still explicitly keeps `rescue_model`, `rescue_always`, `rescue_caption_second_pass`, `rescue_caption_max_tokens`, and `trim_layout_text`
- [x] Fresh real-run evidence exists from this pass using `driver.py` on the reviewed Onward run root, reusing existing OCR/table artifacts and rerunning the crop/build seam only:
  - [x] crop artifacts regenerate successfully
  - [x] final HTML/image publication regenerates successfully
  - [x] no new crop-count, duplicate-text, or obvious caption/text contamination regression is introduced on the inspected slice
- [x] Manual artifact inspection is recorded with exact artifact paths and sample observations for at least:
  - [x] the crop manifest
  - [x] one published cover/title-page image
  - [x] one published seal/text-bearing image case
  - [x] one final chapter HTML file that embeds the refreshed illustration assets
- [x] `docs/spec.md` and `docs/runbooks/crop-eval-workflow.md` describe the post-deletion maintained runtime honestly, and no broader format coverage claim is widened just because dead code was removed

## Out of Scope

- Removing `rescue_caption_second_pass` or `trim_layout_text`, or claiming that `C5` is resolved
- Reopening prompt/model benchmarking, changing crop goldens, or widening the crop-validation corpus
- Adding new crop heuristics, format-specific branches, or a new crop architecture beyond deleting retired maintained-runtime residue
- Broad refactors of `layout`, `nonwhite`, `nontext`, or `auto` detection modes unless the deletion pass exposes a real generic defect

## Approach Evaluation

- **Simplification baseline**: this is not a single-call perception problem. The capability question was already answered by the existing crop evals and Story 184's real-run proof; the baseline here is code and CLI-surface deletion plus proof that the maintained artifacts stay clean.
- **AI-only**: low value. An LLM cannot delete stale runtime branches or keep the module contract honest on its own, and the work is structural rather than interpretive.
- **Hybrid**: useful only as verification discipline. Use the existing crop eval truth surface and a fresh driver-backed artifact proof while deleting the dead surface; do not introduce new model behavior.
- **Pure code**: likely strongest. Remove retired params and branches, tighten contract tests, and rerun the maintained seam.
- **Repo constraints / prior decisions**: Story 183 repaired the crop benchmark substrate and promoted the bounded C4/C5 truth surfaces. Story 184 deliberately stopped at recipe-level simplification after real-run evidence showed the caption second pass still mattered for fidelity. `docs/methodology/state.yaml` keeps `C4` in `converge`, `C5` in `climb`, and `B1` in `hold`. No crop-specific ADR narrows this deletion lane further.
- **Existing patterns to reuse**: `tests/test_crop_runtime_recipe_contract.py` for maintained-contract assertions, `tests/test_crop_illustrations_guided_v1.py` for focused crop-module regression coverage, the reviewed Onward run root under `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/`, and the execution/inspection discipline already recorded in Story 184 and `docs/runbooks/crop-eval-workflow.md`
- **Eval**: the deciding proof is targeted `pytest` / `ruff` plus a real resumed `driver.py` run and manual artifact inspection. A fresh promptfoo rerun is not the default path unless deletion unexpectedly changes detector-quality or crop-validation outputs.

## Tasks

- [x] Re-freeze the current usage of the retired parameter family across recipes, tests, and docs before deleting code so any surviving dependency is explicit
- [x] Delete the retired retry/refine/validate parameter family from `crop_illustrations_guided_v1` function signatures, CLI wiring, and `module.yaml`, and remove stale maintained-recipe keys that only existed to support those branches
- [x] Strengthen focused regression coverage so the maintained contract asserts the deleted keys stay gone and the retained caption-pass / layout-trim path remains explicit
- [x] Clear stale `*.pyc`, rerun the reviewed Onward crop/build seam on the shared run root, and manually inspect regenerated crop and HTML artifacts
- [x] Update `docs/spec.md` and `docs/runbooks/crop-eval-workflow.md` so they reflect the post-deletion runtime honestly
- [x] If this story changes documented format coverage or graduation reality: no change needed; coverage matrix and methodology state remain honest after this same-surface cleanup
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL/HTML data
  - [x] If agent tooling changed: not applicable; no agent tooling changed
- [x] If evals or goldens changed: not applicable; no eval or golden files changed, so `docs/evals/registry.yaml` stayed untouched
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every support claim names the exact run IDs and artifact paths inspected
  - [x] T1 — AI-First: use the existing model/eval win as permission to delete code, not to add more handcrafted logic
  - [x] T2 — Eval Before Build: rely on the verified crop evals and Story 184 proof before touching runtime structure
  - [x] T3 — Fidelity: keep crop/publication quality intact on the inspected Onward slice
  - [x] T4 — Modular: delete residue generically from the shared module surface instead of adding Onward-specific hacks
  - [x] T5 — Inspect Artifacts: manually inspect regenerated crop and HTML outputs, not just logs

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

- **Owning module / area**: the shared crop runtime under `modules/extract/crop_illustrations_guided_v1/`, plus the maintained Onward recipe, focused crop runtime tests, and crop runtime docs that describe the accepted maintained seam
- **Methodology reality**: this belongs to `spec:4` and `spec:8`. In `docs/methodology/state.yaml`, `spec:4` substrate is `exists`, `C4` is `converge`, `C5` is `climb`, and `spec:8` substrate is `exists` with `B1` in `hold`. The relevant coverage rows are `image-directory-scans` and `scanned-pdf-tables`, which are already passing and should not move from this cleanup alone.
- **Substrate evidence**: verified in this pass that `modules/extract/crop_illustrations_guided_v1/main.py` still exposes the full retired parameter family and the corresponding retry/refine/validate branches; `modules/extract/crop_illustrations_guided_v1/module.yaml` still publishes those params and command-line fragments; `configs/recipes/recipe-onward-images-html-mvp.yaml` still carries `rescue_retry_max: 1` and `rescue_require_caption_schema: true` even though retry is disabled; the other maintained crop recipes still share the same module but do not set the retired params explicitly; `tests/test_crop_runtime_recipe_contract.py` and `tests/test_crop_illustrations_guided_v1.py` already provide focused regression seams; and the reviewed shared-run artifacts still exist at `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/02_ocr_ai_gpt51_v1/pages_html.jsonl`, `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/illustration_manifest.jsonl`, and `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/chapter-003.html`
- **Data contracts / schemas**: no new schema or artifact contract is expected. `illustration_v1`, `doc_web_bundle_manifest_v1`, and the final published HTML surface should remain unchanged; if deletion requires a cross-artifact field change, stop and add that schema work explicitly instead of smuggling it through.
- **File sizes**: likely touch points are `modules/extract/crop_illustrations_guided_v1/main.py` (4155 lines), `modules/extract/crop_illustrations_guided_v1/module.yaml` (581), `configs/recipes/recipe-onward-images-html-mvp.yaml` (189), `tests/test_crop_illustrations_guided_v1.py` (48), `tests/test_crop_runtime_recipe_contract.py` (35), `docs/runbooks/crop-eval-workflow.md` (105), and `docs/spec.md` (198). The module file and module schema are already oversized, so changes should be especially surgical there.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/runbooks/crop-eval-workflow.md`, Stories 133/183/184, the current maintained Onward crop recipe, the current crop module, and the focused crop runtime tests. Search across `docs/decisions/`, `docs/scout/`, and `docs/notes/` found no narrower ADR or scout result that already settles this module-deletion move.

## Files to Modify

- `docs/stories/story-198-delete-crop-runtime-validator-retry-residue.md` — story plan, work log, and verification record
- `modules/extract/crop_illustrations_guided_v1/main.py` — remove retired retry/refine/validate branches and argument plumbing (4155 lines)
- `modules/build/build_chapter_html_v1/main.py` — prune published HTML image assets so reused run roots do not keep files outside the current illustration manifest
- `modules/extract/crop_illustrations_guided_v1/module.yaml` — prune retired params and CLI template fragments (581 lines)
- `configs/recipes/recipe-onward-images-html-mvp.yaml` — drop stale maintained keys that only existed for the removed branches (189 lines)
- `tests/test_crop_runtime_recipe_contract.py` — assert deleted keys stay absent and retained maintained flags remain explicit (35 lines)
- `tests/test_crop_illustrations_guided_v1.py` — cover full-rerun crop-image pruning so stale output files cannot survive outside the current manifest
- `tests/test_build_chapter_html.py` — cover published image-bundle pruning on resumed `build_chapters` runs
- `docs/runbooks/crop-eval-workflow.md` — remove stale auto-retry/validator references and align the maintained runtime note (105 lines)
- `docs/spec.md` — update C4/C5 wording if it still claims historical retry/validator/refine residue after the deletion lands (198 lines)

## Redundancy / Removal Targets

- The retired retry/refine/validate argument family in `crop_illustrations_guided_v1` and its `module.yaml` command surface
- The stale `rescue_retry_max` / `rescue_require_caption_schema` keys in the maintained Onward recipe if the retry path is fully deleted
- Runbook or spec language that still treats the retired retry/refine/validate branches as live maintained-runtime residue after the code is removed
- Reused crop/build image directories that retain files no longer present in the refreshed illustration manifest

## Notes

- New story justification: reopening Story 184 would blur an already validated recipe/output proof with a later structural cleanup of the shared module and CLI surface. This story has a different validation boundary: delete code and schema residue while preserving the already-proven maintained runtime behavior.
- No additional UI slice is needed. This is internal pipeline/runtime cleanup and remains honestly inspectable through `driver.py` artifacts plus the existing crop runtime test/eval surfaces.
- If any non-Onward or non-maintained recipe is still using the supposedly retired parameter family in a way current searches missed, stop and record that call site instead of deleting it on faith.

## Plan

### Exploration Summary

- **Ideal alignment**: proceed. This story moves toward the Ideal by deleting proven-dead runtime complexity after the maintained crop seam already cleared the bounded `C4` quality gate and real-run proof surface.
- **Relevant methodology state**: `spec:4` substrate exists with `C4 = converge` and `C5 = climb`; `spec:8` substrate exists with `B1 = hold`. The `document_structure_and_consistency` architecture audit in `docs/methodology/state.yaml` explicitly says the next look should target deletable residue.
- **Critical substrate verified in code**:
  - `modules/extract/crop_illustrations_guided_v1/main.py` still carries the retired parameter family in both the function surface and runtime branches
  - `modules/extract/crop_illustrations_guided_v1/module.yaml` still publishes those params and CLI template fragments
  - `configs/recipes/recipe-onward-images-html-mvp.yaml` still carries seven stale retired keys even though the maintained seam no longer uses them
  - the shared run root still exists and is inspectable at `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/`
- **Current recipe reality**: all maintained crop recipes share the same module, but only `recipe-onward-images-html-mvp.yaml` still sets stale retired keys explicitly. `recipe-onward-pdf-html-mvp.yaml` keeps only `trim_layout_text`; the generic scan and handwritten recipes do not set the retired family.
- **Baseline evidence from this pass**:
  - `python -m pytest tests/test_crop_runtime_recipe_contract.py tests/test_crop_illustrations_guided_v1.py -q` → `3 passed in 2.02s`
  - current deletion-surface counts in `main.py`: retry params appear `4` times each, refine/validate params `4-5` times each
  - current maintained recipe still includes `rescue_retry_on_overlap`, `rescue_retry_on_missing`, `rescue_retry_max`, `rescue_require_caption_schema`, `rescue_retry_on_text`, `rescue_refine_boxes`, and `rescue_validate_crops`
  - current `module.yaml` still defines all 11 retired params
- **Patterns to follow**: Story 184's reviewed Onward resume commands and artifact inspection discipline; `tests/test_crop_runtime_recipe_contract.py` for maintained contract assertions; `tests/test_crop_illustrations_guided_v1.py` for focused behavior coverage
- **Files at risk**: the oversized shared module (`4155` lines) and module schema (`581` lines), plus any recipe smoke tests that depend on the module CLI surface indirectly
- **Potential redundant residue to remove**: the dead param family in `main.py` / `module.yaml`, the stale recipe keys in the maintained Onward recipe, and stale runbook/spec language that still treats auto-retry and validator branches as live maintained-runtime behavior

### Eval-First Gate

- **Success test**: this story succeeds when the retired param family is absent from the shared module surface while the retained caption-pass/layout-trim behavior still passes focused tests and the reviewed Onward crop/build seam still republishes clean artifacts.
- **Current baseline**:
  - structural baseline: `11` retired params still published in `module.yaml`
  - maintained recipe baseline: `7` stale retired keys still present in `recipe-onward-images-html-mvp.yaml`
  - focused behavior baseline: `3` targeted crop tests pass on current code
- **Approach comparison**:
  - AI-only is not relevant; the work is structural deletion
  - hybrid verification is enough: code deletion plus real crop/build proof
  - pure code is the honest implementation path because the model/eval question is already settled

### Recommended Implementation Plan

1. Freeze the shared usage surface (`XS`)
   - Files: `docs/stories/story-198-delete-crop-runtime-validator-retry-residue.md`
   - Change: keep the current baseline counts and shared-recipe usage recorded before any deletion so hidden dependencies become explicit if they appear during implementation
   - Risk: if another recipe or doc path still depends on the retired flags in a real way, deletion becomes a blocker instead of a cleanup
   - Done looks like: the story work log names the current recipe/test/doc usage and the expected delete set precisely

2. Delete the retired runtime/CLI residue (`M`)
   - Files: `modules/extract/crop_illustrations_guided_v1/main.py`, `modules/extract/crop_illustrations_guided_v1/module.yaml`
   - Change: remove the retired retry/refine/validate parameters from the function signature, argparse surface, driver dispatch path, and `module.yaml` params/CLI template; delete the now-dead auto-retry, refine, and validate branches and remove helper functions that become unreachable
   - Impact: every recipe using `crop_illustrations_guided_v1` depends on this module surface, so any parser or module-template mistake can break image-directory, PDF, handwritten, and Onward crop stages
   - Structural health note: keep the patch surgical inside the oversized module; prefer deletion over reshuffling unrelated logic
   - Done looks like: the retired param family no longer appears in the module signature, parser, dispatch call, or `module.yaml`

3. Remove stale maintained recipe keys and tighten tests (`S`)
   - Files: `configs/recipes/recipe-onward-images-html-mvp.yaml`, `tests/test_crop_runtime_recipe_contract.py`, `tests/test_crop_illustrations_guided_v1.py`
   - Change: remove dead maintained keys from the Onward recipe and extend focused tests so they assert both:
     - the retained maintained contract stays explicit (`rescue_model`, `rescue_always`, `rescue_caption_second_pass`, `rescue_caption_max_tokens`, `trim_layout_text`)
     - the deleted keys stay absent from the maintained recipe and shared module surface
   - Small scope delta folded in: `tests/test_crop_runtime_recipe_contract.py` should inspect `module.yaml` as well as the recipe, because current coverage only protects the recipe surface
   - Done looks like: the focused crop tests fail if the deleted param family returns

4. Re-prove the reviewed Onward seam (`M`)
   - Files: shared run root under `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/`, `modules/build/build_chapter_html_v1/main.py`, `tests/test_build_chapter_html.py`
   - Change: clear stale crop `*.pyc`, rerun `crop_illustrations` on the reviewed Onward run root, then rerun `build_chapters` so published image assets and chapter HTML refresh from the new module surface and both image directories are pruned to the current illustration manifest
   - Preferred command shape:
     - `scripts/run_driver_monitored.sh --recipe configs/recipes/recipe-onward-images-html-mvp.yaml --run-id onward-full-audit-20260318-r1 --output-dir /Users/cam/Documents/Projects/codex-forge/output/runs -- --instrument --allow-run-id-reuse --input-images /Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images --start-from crop_illustrations --end-at crop_illustrations --keep-downstream`
     - `scripts/run_driver_monitored.sh --recipe configs/recipes/recipe-onward-images-html-mvp.yaml --run-id onward-full-audit-20260318-r1 --output-dir /Users/cam/Documents/Projects/codex-forge/output/runs -- --instrument --allow-run-id-reuse --input-images /Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images --start-from build_chapters`
   - Done looks like: refreshed crop and published HTML artifacts exist, stale `page-122-002.jpg` is gone from both `03_crop_illustrations_guided_v1/images/` and `output/html/images/`, and manual inspection confirms the known page-12 seal / chapter-003 case stays clean

5. Sync docs to the post-deletion truth (`S`)
   - Files: `docs/runbooks/crop-eval-workflow.md`, `docs/spec.md`
   - Change: remove stale references to auto-retry/validator/refine as active maintained-runtime behavior while preserving the explicit note that caption second pass and `trim_layout_text` remain needed residue
   - Done looks like: docs match the actual surviving crop runtime without widening `C5` claims

### Impact Analysis

- **Primary blast radius**: the shared crop module and its CLI schema, which are reused by six recipe files
- **Secondary blast radius**: the maintained Onward recipe and any tests or docs that still mention the retired parameter family
- **Most likely breakage**:
  - recipe execution failing because `module.yaml` and `main.py` drift out of sync
  - accidental deletion of logic still needed by `rescue_caption_second_pass`
  - story/docs claiming broader crop simplification than the reviewed Onward proof actually supports
- **Validation stack expected after implementation**:
  - `python -m pytest tests/test_crop_runtime_recipe_contract.py tests/test_crop_illustrations_guided_v1.py -q`
  - likely widen to `tests/test_build_chapter_html.py`, and recipe smoke tests if the shared crop module surface breaks anything outside the Onward lane
  - `make lint`
  - `make test`
  - real resumed Onward crop/build proof with manual artifact inspection

### Human-Approval Blockers

- No new dependency, schema, or ADR blocker is visible
- The only operational risk worth explicit approval is that this is a shared-module deletion across all crop recipes, followed by a rerun against the reviewed external Onward run root under `/Users/cam/Documents/Projects/codex-forge/output/runs/`

### Recommended Scope

- **Already folded in**: tighten the existing crop runtime contract test so it covers `module.yaml` deletion, not just recipe params
- **Not folded in**: no promptfoo rerun by default. Only do `/improve-eval` if the deletion pass changes measured crop behavior rather than just deleting dead surface

### What Done Looks Like

- The retired retry/refine/validate parameter family is absent from the shared crop runtime and module schema
- The maintained Onward recipe no longer carries stale dead keys
- Focused crop tests still pass and protect the surviving maintained contract
- The reviewed Onward crop/build seam still republishes clean crop and chapter artifacts with fresh current-pass inspection
- The runbook/spec describe only the surviving maintained crop behavior

## Work Log

20260408-1423 — create-story: created Story 198 after `/triage` identified the C4 crop module as the highest-leverage deletion lane and the user approved proceeding. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/runbooks/crop-eval-workflow.md`, Stories 133/183/184, `configs/recipes/recipe-onward-images-html-mvp.yaml`, `modules/extract/crop_illustrations_guided_v1/main.py`, `modules/extract/crop_illustrations_guided_v1/module.yaml`, `tests/test_crop_runtime_recipe_contract.py`, and the shared Onward artifacts under `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/`. Result: a new story is honest instead of reopening Story 184 because the runtime-proof story is already validated and closed, while the current work is a distinct structural deletion pass on the shared module and CLI surface. The story is `Pending`, not `Draft`, because the substrate and real-run verification seam already exist in repo today. Next step: `/build-story` should confirm no hidden recipe still depends on the retired parameter family, then delete the dead surface and rerun the maintained crop/build seam.
20260408-1432 — /build-story exploration+plan: verified the story remains honestly buildable with no hidden substrate blocker. Context re-read in this pass: `docs/ideal.md`, `docs/spec.md` (`spec:4`, `spec:4.1`, `spec:4.2`, `spec:8`), `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/runbooks/crop-eval-workflow.md`, and Story 184. Code traced in this pass: `modules/extract/crop_illustrations_guided_v1/main.py`, `modules/extract/crop_illustrations_guided_v1/module.yaml`, `configs/recipes/recipe-onward-images-html-mvp.yaml`, `tests/test_crop_runtime_recipe_contract.py`, and `tests/test_crop_illustrations_guided_v1.py`, plus a repo-wide usage search across recipes/tests/docs. Relevant methodology reality: `spec:4` substrate `exists`, `C4 = converge`, `C5 = climb`, `spec:8` substrate `exists`, `B1 = hold`, and the `document_structure_and_consistency` audit note now explicitly says the next move should target deletable residue. Fresh baseline in this pass: `python -m pytest tests/test_crop_runtime_recipe_contract.py tests/test_crop_illustrations_guided_v1.py -q` passed (`3 passed in 2.02s`); the shared module still publishes all 11 retired params in `module.yaml`; the maintained Onward recipe still carries 7 stale retired keys; and `main.py` still references each retired param 4-5 times across signature, runtime branches, and dispatch. Verified substrate that keeps the story `Pending`: the shared reviewed Onward seam is still present at `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/02_ocr_ai_gpt51_v1/pages_html.jsonl`, `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/illustration_manifest.jsonl`, and `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/chapter-003.html`. Small coherent scope delta folded in: the existing recipe-contract test should also inspect `module.yaml`, because current coverage only guards the maintained recipe surface. No larger prerequisite or schema blocker appeared. Next step: wait for human approval before setting the story `In Progress` and deleting the retired surface.
20260408-1438 — implementation started: promoted Story 198 from `Pending` to `In Progress` after the user approved the plan. Next step: recompile the methodology views so `docs/stories.md` and `docs/methodology/graph.json` match the active build state, then delete the retired crop runtime surface.
20260408-1502 — implementation and fresh proof completed for the build pass. Removed the retired retry/refine/validate surface from `modules/extract/crop_illustrations_guided_v1/main.py` (deleted the dead helper functions, function arguments, argparse flags, dispatch args, internal `_caption_schema` retry-only state, and the runtime retry/refine/validate branches), pruned the same retired parameter family from `modules/extract/crop_illustrations_guided_v1/module.yaml`, removed the stale maintained keys from `configs/recipes/recipe-onward-images-html-mvp.yaml`, rewrote `tests/test_crop_runtime_recipe_contract.py` so it now protects both the maintained recipe and the shared module contract, and updated `docs/spec.md` plus `docs/runbooks/crop-eval-workflow.md` to describe the surviving caption-assist/layout-trim runtime honestly. Fresh checks in this pass: `python -m py_compile modules/extract/crop_illustrations_guided_v1/main.py`, `python -m pytest tests/test_crop_runtime_recipe_contract.py tests/test_crop_illustrations_guided_v1.py -q` (`4 passed in 1.49s`), `make lint` (`All checks passed!`), and `make test` (`486 passed, 4 warnings in 391.01s`). Fresh real-run proof in this pass on the shared reviewed run root: `scripts/run_driver_monitored.sh --recipe configs/recipes/recipe-onward-images-html-mvp.yaml --run-id onward-full-audit-20260318-r1 --output-dir /Users/cam/Documents/Projects/codex-forge/output/runs -- --instrument --allow-run-id-reuse --input-images /Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images --start-from crop_illustrations --end-at crop_illustrations --keep-downstream` completed successfully (`crop_illustrations` done at `2026-04-08T20:59:48Z`, `40` illustrations from `29` pages), then `scripts/run_driver_monitored.sh --recipe configs/recipes/recipe-onward-images-html-mvp.yaml --run-id onward-full-audit-20260318-r1 --output-dir /Users/cam/Documents/Projects/codex-forge/output/runs -- --instrument --allow-run-id-reuse --input-images /Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images --start-from build_chapters` completed successfully (`build_chapters` done at `2026-04-08T21:01:04Z`, `33` chapters written; `validate_genealogy_consistency` reported `flagged=0, strong_pages=0`). Manual artifact inspection in this pass:
- crop manifest: `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/illustration_manifest.jsonl` now has `40` rows; sampled pages `1`, `12`, `21`, and `122`. Page `12` still publishes the two expected crops, including `page-012-001.jpg` with bbox `{x0: 602, y0: 4521, x1: 3723, y1: 5907}`; page `21` still carries caption boxes and caption text for both ranch photos; page `122` now has `2` manifest entries even though the reused run directory still contains an unreferenced stale `page-122-002.jpg`.
- cover/title-page image: `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/images/page-001-000.jpg` is a full-page cover crop at `5096x6772` and remains the published title image.
- seal/text-bearing image case: opened `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/images/page-012-001.jpg`; the seal plus signatures stay tightly cropped with no widened surrounding certificate text, which is the specific maintained Story 184 seam this deletion must preserve.
- late multi-image residual check: opened `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/images/page-122-000.jpg` and `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/images/page-122-001.jpg`. `page-122-001.jpg` is clean; `page-122-000.jpg` still contains printed caption text inside the crop. That is not a new regression from this story: the dedicated `crop-validation` truth surface already tracks `page-122-000` as an explicit fail case in `docs/evals/registry.yaml`, so this remains known `C5` residue rather than a new `C4` deletion failure.
- final HTML seam: `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/chapter-003.html` still embeds `page-012-000.jpg` and `page-012-001.jpg`, and `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/chapter-024.html` embeds `page-122-000.jpg` and `page-122-001.jpg` but does **not** reference the stale unmanifested `page-122-002.jpg`. Validation later showed that this was still insufficient for closure because the reused crop and published image directories themselves retained stale files outside the current manifest.
20260408-1512 — validation gap confirmed: `/validate` re-opened the reviewed Onward seam and found stale `page-122-002.jpg` surviving in both `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/images/` and `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/images/` even though the refreshed `illustration_manifest.jsonl` and `chapter-024.html` no longer referenced it. Decision: keep Story 198 open, treat stale-image pruning on full reruns and published HTML image bundles as same-seam required work, and add regression coverage instead of closing on manifest-only cleanliness. Evidence: `/validate` review plus fresh checks on the run-root artifact directories. Next: prune stale crop files after full reruns, prune stale published HTML images to the current manifest, rerun the seam, and confirm the extras are gone.
20260408-1545 — stale-image seam fix implemented and reproved: added full-rerun crop-image pruning in `modules/extract/crop_illustrations_guided_v1/main.py`, added published-image pruning in `modules/build/build_chapter_html_v1/main.py`, and widened regression coverage in `tests/test_crop_illustrations_guided_v1.py` plus `tests/test_build_chapter_html.py` so reused run roots cannot silently keep files outside the current manifest. Fresh local checks in this pass: `python -m py_compile modules/extract/crop_illustrations_guided_v1/main.py modules/build/build_chapter_html_v1/main.py`, `python -m pytest tests/test_crop_runtime_recipe_contract.py tests/test_crop_illustrations_guided_v1.py tests/test_build_chapter_html.py -q` (`93 passed in 15.78s`), `make lint` (`All checks passed!`), and `make test` (`488 passed, 4 warnings in 380.78s`). Fresh driver-backed proof in this pass on the reviewed Onward run root: `scripts/run_driver_monitored.sh --recipe configs/recipes/recipe-onward-images-html-mvp.yaml --run-id onward-full-audit-20260318-r1 --output-dir /Users/cam/Documents/Projects/codex-forge/output/runs -- --instrument --allow-run-id-reuse --input-images /Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images --start-from crop_illustrations --end-at crop_illustrations --keep-downstream` completed with `Cropped 40 illustration(s) from 29 pages` and logged `Removed 1 stale crop images not present in the refreshed manifest`; then `scripts/run_driver_monitored.sh --recipe configs/recipes/recipe-onward-images-html-mvp.yaml --run-id onward-full-audit-20260318-r1 --output-dir /Users/cam/Documents/Projects/codex-forge/output/runs -- --instrument --allow-run-id-reuse --input-images /Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images --start-from build_chapters` rebuilt `33` chapters and re-ran genealogy validation (`flagged=0, strong_pages=0`). Fresh artifact inspection in this pass: `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/illustration_manifest.jsonl` still has `40` rows with page `122` now limited to `page-122-000.jpg` and `page-122-001.jpg`; `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/images/page-122-002.jpg` and `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/images/page-122-002.jpg` are both gone; `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/chapter-024.html` references only `page-122-000.jpg` and `page-122-001.jpg`; `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/chapter-003.html` still references `page-012-000.jpg` and `page-012-001.jpg`; visual inspection of `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/images/page-001-000.jpg`, `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/images/page-012-001.jpg`, `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/images/page-021-000.jpg`, and `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/images/page-122-000.jpg` confirms the cover/title image, the page-12 seal/signature crop, and the page-21 ranch photo all remain clean while the known page-122 caption leak remains the same explicit `C5` residual rather than a new regression. Next: rerun `/validate`; if it agrees the stale-file seam is now clean, Story 198 can close.
20260408-1552 — /mark-story-done closeout: revalidated the finished story against the current diff, acceptance criteria, and fresh verification evidence from this pass; no remaining same-surface implementation gaps remain. Updated the story to `Done`, checked the validation and closeout workflow gates, and marked the non-applicable coverage / eval / agent-tooling tasks explicitly complete so the checklist matches reality. Remaining known residual is unchanged bounded `C5` caption leakage on `page-122-000.jpg`, which is already tracked in `docs/evals/registry.yaml` and outside this story’s resolved stale-file seam. Next: `/check-in-diff`.
