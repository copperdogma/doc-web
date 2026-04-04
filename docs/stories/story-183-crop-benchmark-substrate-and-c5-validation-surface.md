---
title: Repair Crop Benchmark Substrate and Promote C5 Validation Surface
status: Done
priority: High
ideal_refs:
- 'Requirement #4 (Illustrate), Requirement #6 (Validate), Traceability is the product,
  Fidelity to the source, Transparency over magic'
spec_refs:
- spec:4
- spec:4.1
- spec:4.2
- spec:8
adr_refs: []
depends_on:
- '125'
- '126'
- '133'
category_refs:
- spec:4
- spec:8
compromise_refs:
- B1
- C4
- C5
input_coverage_refs:
- image-directory-scans
- scanned-pdf-tables
architecture_domains:
- document_structure_and_consistency
roadmap_tags: []
legacy_system: ''
---

# Story 183 — Repair Crop Benchmark Substrate and Promote C5 Validation Surface

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #4 (Illustrate), Requirement #6 (Validate), Traceability is the product, Fidelity to the source, Transparency over magic
**Spec Refs**: spec:4 (spec:4.1, spec:4.2, C4, C5), spec:8 (B1)
**Build Map Refs**: Category 4 Illustration Extraction (`exists`, C4/C5 `climb`); Category 8 AI Harnesses & Tooling (`exists`, B1 `hold`); Input Coverage rows `scanned-pdf-tables` and `image-directory-scans` (shared `illustration = 0.918` detector signal today; `crop-validation` is now the dedicated bounded C5-linked truth surface)
**Decision Refs**: `docs/runbooks/crop-eval-workflow.md`, `docs/stories/story-125-image-extraction-eval-promptfoo.md`, `docs/stories/story-126-crop-quality-text-validation-loop.md`, `docs/stories/story-133-gemini-flash-crop-detector.md`, `docs/stories/story-150-onward-full-run-audit-reconciliation.md`, `benchmarks/README.md`, `None found after search in docs/decisions/` for a crop-specific ADR
**Depends On**: Story 125, Story 126, Story 133

## Goal

Repair the crop benchmark surface so it is runnable and honest from this repo checkout, then promote the existing crop text-exclusion validation surface into the official truth surfaces for `C5`. At story creation, `docs/build-map.md` still said Category 4 had no dedicated text-exclusion eval even though `benchmarks/tasks/crop-validation.yaml` and `benchmarks/golden/crop-validation.json` already existed, while the main `image-crop-extraction` task depended on `benchmarks/input/` assets that were absent from this worktree and only recoverable from an older external checkout. This story repairs that substrate, updates the registry/build map to reflect the real C4/C5 surfaces, and records fresh current-pass evidence.

## Acceptance Criteria

- [x] `benchmarks/tasks/image-crop-extraction.yaml` and `benchmarks/tasks/crop-validation.yaml` can be invoked from this worktree without reaching into `/Users/cam/Documents/Projects/codex-forge/` or any other out-of-repo benchmark asset path. Required inputs are either checked in here or reproducibly generated from repo-local sources with documented commands.
- [x] The official truth surfaces distinguish the two crop questions honestly:
  - [x] `image-crop-extraction` remains or is refreshed as the direct detector quality surface for `C4`,
  - [x] `crop-validation` (or the chosen registry name) is registered and documented as the explicit crop text-exclusion / crop-quality surface for `C5`.
- [x] `docs/build-map.md` Category 4 and Gap 1 no longer say “No dedicated text-exclusion eval” if this story lands the registry-backed validation surface.
- [x] Fresh current-pass evidence exists after the substrate repair:
  - [x] at minimum a runnable config smoke from this checkout,
  - [x] and at least one fresh recorded benchmark result for the crop surfaces or, if provider/runtime behavior still blocks a full rerun, a clearly documented blocker with exact commands and bounded evidence.
- [x] `docs/runbooks/crop-eval-workflow.md` and `benchmarks/README.md` describe the real asset expectations and do not imply that `benchmarks/input/` is available in a clean checkout when it is not.
- [x] Focused integrity coverage exists so repo checks fail if the maintained crop benchmark tasks point at missing local assets or drift away from the checked-in golden keys.

## Out of Scope

- Reopening the crop detector model decision without first repairing the benchmark substrate
- Deleting `C4` or `C5` or claiming those compromises are ready to converge
- Broad new model sweeps unrelated to substrate repair or the missing C5 truth surface
- Depending on a temporary symlink into the older `codex-forge` checkout as the maintained solution
- Changing the crop production module unless the repaired benchmark exposes one small generic defect worth fixing immediately

## Approach Evaluation

- **Simplification baseline**: first prove whether the existing crop eval surfaces can run honestly from this checkout without any new model or prompt work. No single LLM call solves “benchmark assets are missing.”
- **AI-only**: low value. The immediate problem is benchmark substrate, registry classification, and docs drift, not a reasoning gap in the crop module.
- **Hybrid**: likely best. Repair or restore the repo-local benchmark assets, then run the smallest honest fresh measurement and promote the already-existing `crop-validation` surface into the registry/build map.
- **Pure code**: plausible if the winning approach is bounded to asset restoration/generation, task-path cleanup, registry updates, and runbook/README fixes. Runtime code should only change if the repaired eval exposes a real new generic defect.
- **Repo constraints / prior decisions**: Story 125 created the promptfoo crop benchmark and expected `benchmarks/input/` plus `benchmarks/golden/crops/` assets. Story 126 created the validation loop and the `crop-validation` benchmark assets. Story 133 improved the detector prompt/model and notes that GPT-5.4 screening required reconstructing missing local benchmark inputs from an external scan set. Story 150 records a later crop-stage fix after the last recorded detector score. At story creation, `docs/build-map.md` still said C5 had no dedicated text-exclusion eval, so the truth surfaces disagreed with the repo contents.
- **Existing patterns to reuse**: `benchmarks/scripts/derive_golden_boxes.py`, `benchmarks/tasks/image-crop-extraction.yaml`, `benchmarks/tasks/crop-validation.yaml`, `benchmarks/scorers/image_crop_scorer.py`, `benchmarks/scorers/crop_validation_scorer.py`, `docs/runbooks/crop-eval-workflow.md`, and the maintained benchmark patterns from Stories 169, 180, 181, and 182.
- **Eval**: the deciding evidence is:
  - [x] a fresh runnable smoke from this checkout for the repaired crop tasks,
  - [x] a bounded fresh rerun of the crop detector and/or crop-validation surfaces,
  - [x] and synchronized registry/build-map/runbook state that reflects what the benchmark now really measures.

## Tasks

- [x] Measure and document the current broken state from a clean worktree:
  - [x] confirm the missing `benchmarks/input/` dependency for the crop tasks,
  - [x] record any other out-of-repo assumptions (for example restored local assets or older checkout paths),
  - [x] classify those failures explicitly as benchmark-surface defects rather than model failures.
- [x] Choose the smallest honest substrate repair:
  - [x] either check in the benchmark inputs needed for `image-crop-extraction` and `crop-validation`,
  - [ ] or add a reproducible repo-local generation path plus the minimum source assets needed to rebuild them,
  - [ ] or combine the two if that is the smallest reproducible solution.
- [x] Make the crop benchmark tasks runnable from this repo:
  - [x] verify `benchmarks/tasks/image-crop-extraction.yaml`,
  - [x] verify `benchmarks/tasks/crop-validation.yaml`,
  - [x] update `benchmarks/.gitignore` and task paths only as needed for the chosen substrate shape.
- [x] Add focused crop-benchmark integrity coverage:
  - [x] assert the maintained crop task configs resolve their local asset files from a clean checkout,
  - [x] assert the task keys stay aligned with `benchmarks/golden/image-crops.json` and `benchmarks/golden/crop-validation.json`,
  - [x] and fail repo checks before promptfoo reaches a provider when substrate drift recurs.
- [x] Land the explicit `C5` truth surface:
  - [x] add or update the crop-validation entry in `docs/evals/registry.yaml`,
  - [x] give it a clear target, classification, and retry conditions,
  - [x] and tie `docs/build-map.md` Category 4 / Gap 1 to that dedicated signal instead of the current “closest available” wording.
- [x] Run fresh current-pass evidence after the substrate repair:
  - [x] first a bounded config smoke (for example `--filter-first-n 1` or equivalent),
  - [x] then the smallest honest benchmark rerun that is feasible in this environment,
  - [ ] and if the full run is still blocked, record the exact provider/runtime blocker rather than leaving an implied live score.
- [x] If this story changes documented format coverage or graduation reality: update `docs/build-map.md` and record the before/after state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: not needed; this was benchmark substrate and docs work only
  - [x] If agent tooling changed: not needed; agent tooling did not change
- [x] If evals or goldens changed: fresh bounded rerun completed and `docs/evals/registry.yaml` updated
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: benchmark assets and scores trace back to named source pages/crops and current commands, not hidden local directories
  - [x] T1 — AI-First: do not reopen detector logic before measuring the repaired benchmark
  - [x] T2 — Eval Before Build: benchmark-surface repair happens before any new crop logic or model churn
  - [x] T3 — Fidelity: no hidden out-of-repo inputs or silent benchmark substitutions
  - [x] T4 — Modular: repair the benchmark surface without baking benchmark-only assumptions into production runtime code
  - [x] T5 — Inspect Artifacts: manually inspect the repaired result JSON and representative failure cases, not just the promptfoo exit code

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: Category 4 Illustration Extraction benchmark surfaces in `benchmarks/` plus their registry/build-map/runbook truth surfaces.
- **Build-map reality**: Category 4 remains `exists` / `climb` because the crop production seam still needs the detector + trim architecture, but the truth surfaces are now aligned again: `image-crop-extraction` remains the page-level detector surface, `single-model-crop-detection` remains the stale C4 deletion gate, and `crop-validation` is now the dedicated bounded C5-linked text-exclusion / crop-quality signal. Category 8 matters because this was benchmark/tooling substrate repair before it was runtime work. Relevant input rows are `scanned-pdf-tables` and `image-directory-scans`, which now honestly inherit the refreshed `illustration = 0.918` detector signal while C5 points at its own dedicated bounded surface.
- **Substrate evidence**: verified in this pass that the repo contains `benchmarks/tasks/image-crop-extraction.yaml`, `benchmarks/tasks/crop-validation.yaml`, `benchmarks/scorers/image_crop_scorer.py`, `benchmarks/scorers/crop_validation_scorer.py`, `benchmarks/golden/image-crops.json`, `benchmarks/golden/crop-validation.json`, `benchmarks/input/source-pages-b64/` (13 tracked files), `benchmarks/input/crop-validation-b64/` (40 tracked files), `benchmarks/input/README.md`, and `tests/test_crop_benchmark_substrate.py`. The root `.gitignore` needed an explicit `!benchmarks/input/**` carveout because the repo-wide `input/` ignore pattern was swallowing the repaired benchmark assets.
- **Data contracts / schemas**: no pipeline schema change is expected unless the chosen substrate repair adds new checked-in metadata. The relevant contracts are promptfoo task vars and scorer JSON formats, plus the registry/build-map wording that classifies the crop surfaces.
- **File sizes**: likely touch points are `benchmarks/tasks/image-crop-extraction.yaml` (200), `benchmarks/tasks/crop-validation.yaml` (327), `benchmarks/scorers/image_crop_scorer.py` (312), `benchmarks/scorers/crop_validation_scorer.py` (136), `benchmarks/scripts/derive_golden_boxes.py` (278), `benchmarks/.gitignore` (9), `benchmarks/README.md` (115), `docs/runbooks/crop-eval-workflow.md` (58), `docs/evals/registry.yaml` (899), `docs/build-map.md` (588), and `docs/stories.md` (191). Keep `docs/evals/registry.yaml` and `docs/build-map.md` edits narrow because both are already large.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/build-map.md`, `docs/runbooks/crop-eval-workflow.md`, `benchmarks/README.md`, Story 125, Story 126, Story 133, and Story 150. No crop-specific ADR was found under `docs/decisions/`, so this stays below the ADR threshold unless the story uncovers a harder benchmark-ownership or eval-classification decision.

## Files to Modify

- `docs/stories/story-183-crop-benchmark-substrate-and-c5-validation-surface.md` — story implementation record and close-out evidence (new file)
- `docs/stories.md` — add Story 183 to the index (191 lines)
- `benchmarks/.gitignore` — stop hiding any benchmark assets that must be present in a clean checkout or narrow the ignore to the chosen generated-only paths (9 lines)
- `benchmarks/tasks/image-crop-extraction.yaml` — repair task assumptions if the input substrate layout changes (200 lines)
- `benchmarks/tasks/crop-validation.yaml` — repair task assumptions and keep the C5 surface runnable from this checkout (327 lines)
- `benchmarks/scorers/image_crop_scorer.py` — only if the detector benchmark contract or reporting needs a bounded fix (312 lines)
- `benchmarks/scorers/crop_validation_scorer.py` — only if the C5 validation contract or reporting needs a bounded fix (136 lines)
- `benchmarks/scripts/derive_golden_boxes.py` — reuse or extend only if the chosen substrate repair depends on reproducible local regeneration (278 lines)
- `benchmarks/README.md` — make benchmark asset expectations and setup truthful (115 lines)
- `docs/runbooks/crop-eval-workflow.md` — update the operational crop-eval guidance to match the repaired substrate and explicit C5 surface (58 lines)
- `docs/evals/registry.yaml` — add or refresh the crop-validation truth surface and refresh crop attempt notes (899 lines)
- `docs/build-map.md` — replace the current “no dedicated text-exclusion eval” wording with the repaired C5 truth surface (588 lines)
- `benchmarks/input/` — new or restored checked-in benchmark assets, or repo-local generator outputs if that is the chosen maintained shape
- `tests/test_crop_benchmark_substrate.py` — focused integrity coverage for crop benchmark assets and task/golden alignment (new file)

## Redundancy / Removal Targets

- Any temporary symlink- or external-checkout-based instructions for recovering crop benchmark inputs
- The current `docs/build-map.md` wording that says C5 has no dedicated text-exclusion eval
- Stale README/runbook language that implies `benchmarks/input/` exists in a clean checkout when it currently does not
- Any one-off local recovery steps from Story 133 that are better captured as a maintained benchmark-substrate path

## Notes

- The story should not assume that the right answer is “check in every old benchmark binary.” `/build-story` should compare the smallest honest checked-in asset set versus a reproducible local generator and choose the cheaper maintained shape.
- The current `crop-validation` surface already looks like the right C5 instrument: it has 40 crops with 4 explicit fail cases for `text_included`, `blank_space`, and `incomplete_crop`. The missing work is registry/build-map promotion and reproducible input substrate, not inventing a new eval from scratch.
- The current `image-crop-extraction` surface still matters for C4 because it measures direct detector box quality against the 13-page golden set.
- The current `.b64.txt` payloads are part of the benchmark contract, not a neutral encoding detail. Fresh exploration showed the historical benchmark inputs are downscaled data-URI fixtures rather than 1:1 wrappers around the old raw JPEGs, and `docs/ai-learning-log.md` already records that promptfoo `file://` corrupts binary image data. Switching the crop tasks to raw image files in this story would silently redefine the eval surface instead of repairing it.

## Plan

### Exploration Summary

- **Ideal alignment:** proceed. This story closes a real Ideal gap in Requirement #4 (Illustrate) and Requirement #6 (Validate): the current crop truth surfaces are not reproducible from a clean checkout, so the project cannot honestly measure illustration crop quality or text-exclusion drift.
- **Relevant build-map state:** Category 4 remains `exists` / `climb` because `C4` and `C5` are still active. Category 8 (`B1`) already provides the benchmark framework, so the missing slice is crop-specific benchmark substrate and truth-surface alignment, not a new eval system.
- **Critical substrate verified in this pass:** `benchmarks/tasks/image-crop-extraction.yaml`, `benchmarks/tasks/crop-validation.yaml`, `benchmarks/scorers/image_crop_scorer.py`, `benchmarks/scorers/crop_validation_scorer.py`, `benchmarks/golden/image-crops.json`, `benchmarks/golden/crop-validation.json`, `benchmarks/prompts/_image-helpers.js`, and `docs/runbooks/crop-eval-workflow.md` all exist locally. The task → prompt helper → scorer path is intact in code.
- **Critical missing slice:** this checkout has no `benchmarks/input/source-pages-b64/` or `benchmarks/input/crop-validation-b64/`, and `benchmarks/.gitignore` still hides `input/source-pages-b64/`. Fresh baseline promptfoo smoke runs fail before any provider call because the task vars cannot resolve the required local files.
- **Current benchmark-contract reality:** the historical `.b64.txt` inputs are canonical benchmark fixtures, not a trivial encoding wrapper. Sampled evidence from the older checkout shows the benchmark page input for `Image000` is `1505x2000` while the old raw source page is `5096x6772`, and the benchmark crop input for `page-001-000` is `3786x4479` while the old raw crop is `5096x6772`. Repointing the tasks at raw JPEGs would silently change the measured surface.
- **Promptfoo constraint to preserve:** `docs/ai-learning-log.md` already records the relevant repo rule: promptfoo `file://` corrupts binary JPEG when interpolated into prompt templates, so maintained multi-provider vision evals should keep using pre-encoded data-URI text fixtures rather than raw binary file interpolation.
- **Broader drift found, kept out of scope:** this missing-input pattern is not unique to the crop seam; for example `benchmarks/tasks/ocr-genealogy-tables.yaml` also points at a missing `benchmarks/input/onward-pages-b64/` tree. Story 183 should stay crop-scoped and not quietly widen into repo-wide benchmark repair.

### Eval-First Gate

- **Fresh baseline:** from this clean checkout, both crop surfaces are currently non-runnable:
  - `cd benchmarks && promptfoo eval -c tasks/image-crop-extraction.yaml --no-cache --filter-first-n 1 -j 1` exits early with `No files found for variable image at path ../input/source-pages-b64/Image000.b64.txt`.
  - `cd benchmarks && promptfoo eval -c tasks/crop-validation.yaml --no-cache --filter-first-n 1 -j 1` exits early with `No files found for variable image at path ../input/crop-validation-b64/page-001-000.b64.txt`.
- **Candidate approaches:**
  - **AI-only:** reject. The failure is substrate and truth-surface drift, not a reasoning gap.
  - **Hybrid A — check in canonical `.b64.txt` fixtures and keep the current promptfoo contract** (`M`, recommended): restore the exact benchmark input shape that current tasks and prompt helpers expect, add integrity coverage, then rerun bounded fresh measurements and update registry/build-map truth surfaces.
  - **Hybrid B — check in raw images plus a deterministic encoder/generator** (`M/L`, not recommended for this story): would need a documented transform that reproduces the current downscaled benchmark inputs exactly; otherwise it changes the eval surface rather than repairing it.
  - **Pure code / harness migration** (`L`): migrate the crop seam to a new corpus-driven runner like the newer maintained benchmarks. Plausible as a later cleanup, but larger than needed to make Story 183 honest now.
- **Recommended classification choice:** promote `crop-validation` into the registry as the dedicated crop text-exclusion / crop-quality truth surface that pressures `C5`, but do not over-claim it as the full C5 deletion gate unless the measured semantics support that. `image-crop-extraction` remains the page-level detector-quality surface for `C4`.

### Recommended Implementation Plan

1. Freeze the maintained crop substrate in the current benchmark contract.
   - Files: `benchmarks/input/source-pages-b64/`, `benchmarks/input/crop-validation-b64/`, `benchmarks/.gitignore`
   - Change: add the missing canonical `.b64.txt` data-URI fixtures needed by the maintained crop tasks and stop ignoring the directories that must exist in a clean checkout.
   - Order: land the assets first so every later smoke/test step runs against the maintained local substrate.
   - Done when: the two maintained crop task configs resolve their local `file://` vars from a clean checkout without any symlink or external checkout path.

2. Add focused substrate-integrity coverage so this does not regress silently again.
   - Files: `tests/test_crop_benchmark_substrate.py`, optionally a tiny helper inside `benchmarks/` only if the assertions need shared parsing
   - Change: parse the maintained crop task configs, assert every referenced local asset file exists, and assert `golden_key` / `crop_key` coverage stays aligned with `benchmarks/golden/image-crops.json` and `benchmarks/golden/crop-validation.json`.
   - Impact / risk: low blast radius, high leverage. This turns the current ad-hoc runtime failure into a repo-check failure.
   - Done when: a focused pytest catches missing asset drift before promptfoo reaches any provider.

3. Update the crop truth surfaces and docs to match the real benchmark topology.
   - Files: `docs/evals/registry.yaml`, `docs/build-map.md`, `benchmarks/README.md`, `docs/runbooks/crop-eval-workflow.md`
   - Change:
     - add `crop-validation` to the registry with explicit score semantics, retry conditions, and its relationship to `C5`,
     - keep `image-crop-extraction` and `single-model-crop-detection` honest for `C4`,
     - replace the build-map “No dedicated text-exclusion eval” wording with the real dedicated surface and its limits,
     - document the checked-in asset expectation and the fact that `.b64.txt` fixtures are the maintained promptfoo input form.
   - Risk: classification drift. The docs should not imply `crop-validation` alone deletes `C5`; it is the dedicated text-exclusion truth surface, not necessarily the final deletion gate.
   - Done when: registry/build-map/runbook/README all describe the same crop surfaces and a clean-checkout operator would know exactly what assets must exist.

4. Rerun fresh bounded evidence on the repaired substrate.
   - Files: `benchmarks/results/` (untracked output), `docs/evals/registry.yaml`, story work log
   - Change:
     - first rerun the same clean-checkout smoke on both maintained crop tasks,
     - then run the smallest honest fresh measurement that creates or refreshes a real crop signal,
     - preferred first pass: single-provider fresh measurement for the new `crop-validation` registry entry and a bounded refresh of the current crop detector surface if provider/runtime budget allows.
   - Suggested order:
     - smoke `image-crop-extraction`,
     - smoke `crop-validation`,
     - fresh bounded `crop-validation` measurement,
     - then a fresh bounded detector refresh on `image-crop-extraction` or the focused `image-crop-g3flash-prompts` surface if still relevant.
   - Done when: the story records either a fresh real score on the repaired substrate or an exact current blocker after the substrate repair.

5. Keep the slice narrow and create follow-up debt only where the evidence says it belongs.
   - Files at risk but likely not needed: `benchmarks/scripts/derive_golden_boxes.py`, other non-crop benchmark tasks that still depend on missing `benchmarks/input/*`
   - Change: only touch these if the repaired crop benchmark can’t be documented honestly without clarifying them. Broader missing-input drift should become a separate follow-up rather than a hidden scope blow-up.
   - Done when: Story 183 repairs the crop seam end-to-end without pretending the rest of `benchmarks/input/` is solved.

### Impact Analysis

- **Primary blast radius:** `benchmarks/input/`, crop benchmark task integrity coverage, and crop truth-surface docs.
- **Secondary blast radius:** sibling crop task configs that share `source-pages-b64` will benefit automatically once the canonical page fixtures exist. Non-crop promptfoo tasks remain out of scope.
- **Structural health note:** `docs/evals/registry.yaml` and `docs/build-map.md` are already large, so the implementation should keep those edits narrow and evidence-led.
- **Human-approval blocker:** the smallest honest repair likely adds about `134M` of tracked benchmark assets (`source-pages-b64` is about `9.1M` across 13 files; `crop-validation-b64` is about `125M` across 40 files). That is the explicit tradeoff for preserving the current promptfoo benchmark surface rather than redefining it.
- **Small coherent scope expansion folded into the story:** add the focused crop benchmark integrity test. This is necessary to keep the repaired substrate from drifting back into an untracked local-only dependency.

### What Done Looks Like

- The maintained crop tasks run from this checkout without any external checkout or symlink.
- Repo checks include at least one focused crop benchmark substrate assertion.
- `crop-validation` is visible in the registry/build map as the dedicated crop text-exclusion truth surface, with wording that stays honest about what it does and does not prove.
- Fresh current-pass smoke and at least one bounded fresh measurement exist on the repaired substrate, or a precisely documented blocker remains.

## Work Log

20260403-1032 — story created from `/improve-eval image-crop-extraction`: converted the benchmark-surface diagnosis into a build-ready follow-up instead of leaving the crop seam blocked on implicit local context. Evidence reviewed in this pass: `benchmarks/tasks/image-crop-extraction.yaml` and `benchmarks/tasks/image-crop-g3flash-prompts.yaml` require `benchmarks/input/source-pages-b64/...`; `benchmarks/tasks/crop-validation.yaml` requires `benchmarks/input/crop-validation-b64/...`; this worktree has no `benchmarks/input/`; `benchmarks/.gitignore` excludes `input/source-pages-b64/`; `docs/build-map.md` still says Category 4 has no dedicated text-exclusion eval even though `benchmarks/tasks/crop-validation.yaml` and `benchmarks/golden/crop-validation.json` already exist; and Story 133 records that later GPT-5.4 screening had to reconstruct missing local crop benchmark inputs from an external Onward scan set. Result: the story is honestly `Pending`, not `Draft`, because the benchmark/config/registry substrate already exists and the missing slice is bounded substrate repair plus truth-surface alignment. Next step: `/build-story` should choose the smallest maintained benchmark-asset strategy, then rerun the repaired crop surfaces from this checkout.
20260403-1058 — `/build-story` exploration and eval-first baseline completed with no implementation changes. Ideal-alignment result: proceed. Context reviewed in this pass: `docs/ideal.md`; `docs/spec.md` (`spec:4`, `spec:8`); Category 4, Category 8, Gap 1, and the `scanned-pdf-tables` / `image-directory-scans` rows in `docs/build-map.md`; Story 125, Story 126, Story 133, Story 150; `docs/runbooks/crop-eval-workflow.md`; `benchmarks/README.md`; `docs/ai-learning-log.md`; and a search of `docs/decisions/` that confirmed no crop-specific ADR exists. Code/path tracing in this pass walked `benchmarks/tasks/image-crop-extraction.yaml`, `benchmarks/tasks/crop-validation.yaml`, sibling crop task configs sharing `source-pages-b64`, `benchmarks/prompts/_image-helpers.js`, `benchmarks/scorers/image_crop_scorer.py`, `benchmarks/scorers/crop_validation_scorer.py`, `benchmarks/.gitignore`, and `benchmarks/scripts/derive_golden_boxes.py`. Fresh baseline evidence from a clean checkout: `cd benchmarks && promptfoo eval -c tasks/image-crop-extraction.yaml --no-cache --filter-first-n 1 -j 1` exited before any provider call with `No files found for variable image at path ../input/source-pages-b64/Image000.b64.txt`, and `cd benchmarks && promptfoo eval -c tasks/crop-validation.yaml --no-cache --filter-first-n 1 -j 1` failed the same way for `../input/crop-validation-b64/page-001-000.b64.txt`. Critical substrate verified versus missing: the scorers and checked-in goldens exist, but this checkout has no `benchmarks/input/source-pages-b64/` or `benchmarks/input/crop-validation-b64/`, and `benchmarks/.gitignore` still hides `input/source-pages-b64/`. Important surprise that changes the implementation plan: the historical `.b64.txt` inputs are downscaled canonical benchmark fixtures rather than 1:1 wrappers around raw JPEGs (`Image000` old raw `5096x6772` vs benchmark input `1505x2000`; `page-001-000` old raw `5096x6772` vs benchmark input `3786x4479`), and `docs/ai-learning-log.md` already records that promptfoo `file://` corrupts binary image interpolation, so repointing the crop tasks at raw images would silently redefine the eval surface instead of repairing it. Asset-sizing evidence from the older checkout makes the substrate repair bounded but explicit: `source-pages-b64` is 13 files / `9.1M`, `crop-validation-b64` is 40 files / `125M`, old raw source pages are `44M`, and old raw crop images are about `100M`. Small coherent scope delta folded into the story: add focused crop benchmark integrity coverage so missing assets fail in repo checks instead of only at ad-hoc promptfoo runtime. Broader missing-input drift was also found (`benchmarks/tasks/ocr-genealogy-tables.yaml` still points at missing `benchmarks/input/onward-pages-b64/`) but is intentionally left out of Story 183 scope. Next step: implement the narrow repair by restoring the canonical crop `.b64.txt` substrate, adding integrity coverage, promoting `crop-validation` into the official C5-linked truth surfaces, and rerunning bounded fresh crop evidence.
20260403-1143 — implementation completed on the benchmark/docs seam with no production runtime changes. Changed files: `.gitignore`, `benchmarks/.gitignore`, `benchmarks/README.md`, `benchmarks/input/README.md`, `docs/build-map.md`, `docs/evals/registry.yaml`, `docs/runbooks/crop-eval-workflow.md`, `tests/test_crop_benchmark_substrate.py`, `docs/stories.md`, and this story file. The maintained crop substrate is now repo-local and tracked: restored `benchmarks/input/source-pages-b64/` (13 `.b64.txt` page fixtures) and `benchmarks/input/crop-validation-b64/` (40 `.b64.txt` crop fixtures), then added a root `.gitignore` carveout (`!benchmarks/input/**`) because the repo-wide `input/` ignore pattern was silently swallowing the repair. Focused integrity coverage landed in `tests/test_crop_benchmark_substrate.py`; fresh checks passed via `python -m pytest tests/test_crop_benchmark_substrate.py -q` (`2 passed`) and `python -m ruff check tests/test_crop_benchmark_substrate.py` (`All checks passed!`). Fresh clean-checkout smoke evidence after the substrate repair: `cd benchmarks && promptfoo eval -c tasks/crop-validation.yaml --no-cache --filter-first-n 1 -j 1 --no-write` completed `24` prompt/provider combinations on the first crop with `21` passes, `3` fails, `0` errors in `2m47s`, proving the task now executes from local fixtures instead of dying on missing files; and `cd benchmarks && promptfoo eval -c tasks/image-crop-g3flash-prompts.yaml --no-cache --filter-prompts 'conservative-count' --filter-first-n 1 -j 1 --no-write` completed `1/1` pass in `8s`, proving the restored `source-pages-b64` fixtures drive the focused detector path too. Fresh recorded benchmark result for the dedicated C5-linked surface: `cd benchmarks && promptfoo eval -c tasks/crop-validation.yaml --no-cache --filter-providers 'google:gemini-3.1-flash-lite-preview' --filter-prompts 'caption-focus' --output results/crop-validation-story183-g31-caption-focus.json -j 1` completed the full checked-in 40-crop corpus with `40/40` passes, `0` failures, `0` errors, `120833 ms` total duration, and `59087` total tokens. Manual inspection in the same pass covered `benchmarks/results/crop-validation-story183-g31-caption-focus.json`: the 4 explicit fail cases (`page-018-000`, `page-092-000`, `page-122-000`, `page-126-000`) each returned `{"verdict": "fail", ...}` with the expected page-text / blank-space reasoning, while integral-text pass case `page-012-000` still returned `{"verdict": "pass", ...}`. Truth surfaces now match reality: `crop-validation` is registered as the dedicated bounded C5-linked signal, the build map no longer says C5 lacks a dedicated text-exclusion eval, and the README/runbook now describe the checked-in `.b64.txt` fixture contract explicitly. Fresh repo checks after the edits: `make lint` passed (`ruff check doc_web/ modules/ tests/`) and `make test` passed (`435 passed, 4 warnings in 180.70s`). Residual note kept explicit rather than blocking build completion: the broad multi-provider `image-crop-extraction` matrix was not rerun for a fresh comparable leaderboard score in this pass; the fresh recorded score landed on the dedicated `crop-validation` surface while `image-crop-extraction` received a repaired substrate plus smoke proof instead.
20260403-1200 — `/mark-story-done` close-out completed after `/validate` confirmed there are no remaining implementation gaps. Updated the story metadata and stale background wording to reflect the shipped state, checked the validation and done workflow gates, updated `docs/stories.md`, and added `CHANGELOG.md` entry `2026-04-03-02`. Fresh close-out evidence from the validation/close-out passes: reopened `benchmarks/results/crop-validation-story183-g31-caption-focus.json` and reconfirmed the 4 checked fail cases plus pass case `page-012-000`; reran `python -m pytest tests/test_crop_benchmark_substrate.py -q` (`2 passed`); reran `python -m ruff check modules/ tests/` (`All checks passed!`); and relied on the immediately preceding full-suite validation pass where `make lint` passed and `make test` completed `435 passed, 4 warnings in 207.71s`. Clean-checkout `crop-validation` smoke in that same validation pass completed `23` passes, `1` failure, and `0` errors on the first-case cross-provider slice, which reconfirmed local substrate operability while matching the runbook’s non-determinism warning. Next step: `/check-in-diff`.
20260403-2115 — follow-up `/improve-eval image-crop-extraction` closed the remaining detector truth-surface drift instead of changing crop runtime logic. Fresh measured evidence first classified the mismatch as task-config wrong: the maintained `benchmarks/tasks/image-crop-extraction.yaml` had drifted to a three-prompt surface even though the registry and runbook still claimed the winning Gemini 3 Flash `conservative-count` prompt was current. On the drifted task, fresh Gemini 3 Flash baseline results from `benchmarks/results/image-crop-extraction-g3flash-baseline-20260403.json` were `baseline = 0.848 / 0.769`, `strict-exclude = 0.915 / 0.846`, and `two-step = 0.827 / 0.769` (overall / pass_rate), with the misses concentrated on `Image000`, `Image001`, and `Image011`. The minimal fix was to restore `conservative-count` to the maintained task rather than invent a new prompt. Fresh maintained-task reruns on 2026-04-03 reached `13/13` passes, `0` failures, `0` errors, and a best current-pass aggregate of `0.918` overall / `1.0` pass rate on the 13-page corpus. Manual inspection in the same pass covered the maintained-task result files: `Image000` returned one full-cover crop instead of splitting decorative elements, `Image001` returned the stylized title text region as the lone major visual element, and `Image011` grouped the seal plus signatures while keeping the logo/title crops bounded. Touched files in this follow-up: `benchmarks/tasks/image-crop-extraction.yaml`, `benchmarks/README.md`, `docs/runbooks/crop-eval-workflow.md`, `docs/evals/registry.yaml`, `docs/build-map.md`, and this story file. Next step: no new crop-eval story is needed immediately; the remaining blocker is still the broader C4 deletion gate at `single-model-crop-detection`, not prompt-surface honesty.
20260403-2130 — immediate cleanup landed after the detector truth-surface repair: `tests/test_crop_benchmark_substrate.py` now explicitly fails if the maintained `image-crop-extraction` task drops the `conservative-count` prompt again. Fresh verification in the same pass: `python -m pytest tests/test_crop_benchmark_substrate.py -q` completed `3 passed in 0.07s`. This keeps the exact drift fixed by the follow-up eval repair from silently recurring in a later docs-only or benchmark-only edit.
