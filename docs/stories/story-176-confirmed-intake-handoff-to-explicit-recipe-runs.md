---
title: Confirmed Intake Handoff to Explicit Recipe Runs
status: Done
priority: High
ideal_refs:
- 'Requirement #1 (Ingest), Requirement #2 (Detect), Zero configuration, Transparency
  over magic'
spec_refs:
- spec:1
- spec:1.1
- spec:8
- spec:9
adr_refs: []
depends_on:
- '027'
- '169'
- '170'
- '171'
category_refs:
- spec:1
- spec:8
- spec:9
compromise_refs:
- B1
- B10
- C2
input_coverage_refs:
- born-digital-pdf
- image-directory-scans
- scanned-pdf-prose
- scanned-pdf-tables
architecture_domains:
- intake_and_routing
roadmap_tags:
- campaign:maintained-intake-honesty
legacy_system: ''
---

# Story 176 — Confirmed Intake Handoff to Explicit Recipe Runs

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #1 (Ingest), Requirement #2 (Detect), Zero configuration, Transparency over magic
**Spec Refs**: spec:1 (spec:1.1, C2), spec:8 (B1), spec:9 (B10)
**Build Map Refs**: Category 1 Intake & Format Routing (`exists`, C2 `climb`); Category 8 AI Harnesses & Tooling (`exists`, B1 `hold`); Category 9 Planning Infrastructure (`exists`, B10 `climb`); Input Coverage rows `image-directory-scans` (`passing`), `scanned-pdf-prose` (`passing`), `scanned-pdf-tables` (`passing`), `born-digital-pdf` (`has fixture`)
**Decision Refs**: `docs/stories/story-011-ai-planner.md`, `docs/stories/story-027-contact-sheet-auto-intake.md`, `docs/stories/story-169-restore-contact-sheet-intake-and-benchmark-auto-book-type-detection.md`, `docs/stories/story-170-born-digital-pdf-native-text-widening-and-routing-decision.md`, `docs/stories/story-171-maintained-non-toc-born-digital-pdf-lane.md`, `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower intake-handoff ADR
**Depends On**: Story 027, Story 169, Story 170, Story 171

## Goal

Close the remaining C2 workflow gap after the now-passing intake benchmark: once `confirm_plan_v1` approves an `intake_plan_v1`, the repo should be able to launch the exact maintained explicit recipe without the operator manually retyping a recipe path or re-specifying the source input. The handoff must stay explicit, inspectable, and human-approved, not revive Story 011's rejected planner/product surface.

## Acceptance Criteria

- [x] A maintained confirmed-handoff path exists that consumes an approved `overview_plan_final.jsonl` (or a stamped derivative artifact) and launches the exact maintained explicit recipe for supported `images_dir` and `pdf` plans without asking the operator to manually choose a recipe path.
- [x] The handoff preserves approval and traceability: no downstream execution occurs before `confirm_plan_v1`; the launched run records the approved plan path, recommended recipe, source-input snapshot, downstream `run_id`, and terminal outcome (`launched`, `skipped`, `blocked`, or `failed`) in an inspectable artifact.
- [x] `no-recipe-needed`, missing `recommended_recipe`, unsupported input kinds, and missing source-input paths fail or skip explicitly with inspectable reasons instead of shelling a broken downstream run.
- [x] Fresh `driver.py` proofs exist for at least one image-directory input, one scanned PDF input, and one born-digital PDF input, each launched through the confirmed-handoff path and producing expected downstream artifacts in `output/runs/`; the work log names the inspected handoff artifact and first downstream stamped artifact for each.
- [x] `docs/evals/registry.yaml` and `docs/build-map.md` are updated honestly to reflect whether approved-plan handoff is now enough to say manual recipe selection is removed for C2, or whether a narrower residual manual seam remains.

## Out of Scope

- Reviving Story 011's AI planner, freeform pipeline assembly, or user-editable recipe selection surface
- Extending intake recommendation coverage to DOCX, XLSX, PPTX, mixed archives, or other input families not already owned by the maintained contact-sheet lane
- Re-running classification or adding a second AI routing pass after `confirm_plan_v1`
- Building a Dossier-facing approval/job-management product surface

## Approach Evaluation

- **Simplification baseline**: first test whether the current approved-plan substrate plus `run_dispatch_v1` already works on representative image-directory and PDF plans. Current repo evidence says it likely does not: `run_dispatch_v1` shells `driver.py --recipe <recommended_recipe>` only, which drops source-input forwarding and plan trace.
- **AI-only**: ask a model to emit a downstream `RunConfig` from the approved plan. This is low-value and higher-risk than necessary because the classification problem is already solved upstream and the remaining seam is reproducible launch plumbing.
- **Hybrid**: keep AI limited to the existing intake classification / zoom steps, then deterministically translate the approved plan into a downstream launch artifact plus `driver.py` invocation. This is the leading candidate because it preserves inspectability and minimizes new model behavior.
- **Pure code**: plausible if current plan metadata already carries the required source-input context. The remaining work would then be driver/config plumbing, explicit failure semantics, and tests.
- **Repo constraints / prior decisions**: Story 011 is `Won't Do` because auto-planning belongs in Dossier, not doc-forge. Story 169 intentionally made the maintained intake lane recommendation-only and treats silent dispatch as a regression. The build map now says the remaining C2 blocker is exactly that recommendation/confirmation stop. A new ADR is not needed unless the implementation grows into planner-style user choice or hidden auto-routing beyond an approved explicit recipe.
- **Existing patterns to reuse**: `modules/intake/confirm_plan_v1`, `modules/intake/dispatch_hint_v1`, `modules/intake/run_dispatch_v1`, `modules/intake/intake_plan_utils.py`, `modules/intake/contact_sheet_builder_v1` source-input metadata, `driver.py` explicit input override plumbing, `modules/intake/tests/test_intake_chain_e2e.py`, `tests/test_intake_plan_utils.py`, and the current `benchmarks/scripts/run_auto_book_type_detection_eval.py` harness.
- **Eval**: the deciding test is a driver-backed approved-plan handoff harness, not another classification-only prompt test. The story should choose the smallest honest surface:
  - extend `auto-book-type-detection` to score approved-plan handoff outcomes, or
  - add a sibling manual harness if overloading the existing eval would muddle history.

## Tasks

- [x] Measure the current baseline on approved plans from representative image-directory, scanned-PDF, and born-digital-PDF cases; document exactly where the current dispatch seam loses source input, downstream run metadata, or clean failure semantics.
- [x] Decide and implement the smallest maintained confirmed-handoff surface:
  - [x] add a post-`confirm_plan_v1` maintained sibling recipe, `configs/recipes/recipe-intake-contact-sheet-confirmed-handoff.yaml`, that consumes the approved plan and launches the exact maintained explicit recipe
  - [x] preserve explicit human approval and avoid any second classification pass
  - [x] emit a stamped `intake_handoff_v1` artifact containing approved plan path, recommended recipe, source-input snapshot, downstream run id, and terminal outcome
- [x] Close driver/config substrate gaps required by maintained input families:
  - [x] forward `pdf` and `images_dir` source inputs from the approved plan into the downstream run without manual recipe edits
  - [x] add `RunConfig.input_images` plus `driver.py --input-images`, including override of the hardcoded image-manifest stage param
  - [x] keep `no-recipe-needed` and unsupported recommendations as explicit non-launch outcomes
- [x] Add focused coverage:
  - [x] unit tests for handoff artifact generation and failure modes
  - [x] intake-chain e2e coverage for approved image-directory and PDF plans launching the expected downstream recipe
  - [x] wire the new `intake_handoff_v1` artifact into `schemas.py` and `validate_artifact.py`
- [x] Run real `driver.py` verification on representative maintained inputs:
  - [x] one image-directory input through approved handoff
  - [x] one scanned PDF input through approved handoff
  - [x] one born-digital PDF input through approved handoff
  - [x] inspect the handoff artifact plus the first downstream stamped artifact under `output/runs/`
- [x] Decide whether `auto-book-type-detection` remains an honest C2 gate after the workflow change:
  - [x] keep `auto-book-type-detection` as the recommendation-only detection surface and add the smallest honest sibling proof surface in `docs/evals/registry.yaml` for approved-plan handoff
  - [x] update `docs/evals/registry.yaml` with the new manual `approved-intake-handoff` proof surface
- [x] If this story changes documented format coverage or graduation reality: update `docs/build-map.md` and record the before/after state honestly
- [x] Check whether the chosen implementation makes any existing dispatch stubs, docs, or helper paths redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [x] Agent tooling unchanged in this story slice; `make skills-check` not required
- [x] Eval registry changed only to add the new manual proof surface; no prompt/golden `/improve-eval` run was required in this slice
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: approved handoff now traces the downstream run back to the approved plan and source input via `intake_handoff_v1`
  - [x] T1 — AI-First: no new AI was added to a confirmed-launch plumbing problem
  - [x] T2 — Eval Before Build: the baseline dispatch seam was measured before implementation
  - [x] T3 — Fidelity: source input and recommended recipe are forwarded without silent substitution or hidden mutation
  - [x] T4 — Modular: the handoff launches existing maintained explicit recipes rather than embedding a new bespoke pipeline
  - [x] T5 — Inspect Artifacts: the handoff artifact and first downstream stamped artifact were manually inspected for all three proof runs

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: the intake handoff seam between `confirm_plan_v1` and downstream `driver.py` execution. Primary ownership is `modules/intake/` plus the driver/config and eval truth surfaces, not a Dossier-facing planner.
- **Build-map reality**: Category 1 still owns this story and still stays `climb`, but the reason narrowed. Story 176 removes manual recipe-path retyping on the supported image-directory/PDF slice via a maintained confirmed-handoff recipe and `intake_handoff_v1`; the remaining gap is proof breadth and unsupported-family coverage, not the absence of a maintained handoff seam. Category 8 still matters because the C2 proof surface now splits cleanly into recommendation detection plus approved-plan handoff, and Category 9 still matters because B10 tracks the remaining explicit YAML/config overlap.
- **Substrate evidence**: the maintained recommendation-only intake recipe still ends at `confirm_plan_v1`, and Story 176 adds the maintained sibling recipe `configs/recipes/recipe-intake-contact-sheet-confirmed-handoff.yaml` that runs `run_dispatch_v1` after approval. `contact_sheet_builder_v1` already writes `input_kind` plus source-path metadata into plan meta; `intake_plan_utils.py` now resolves the approved handoff deterministically; `run_dispatch_v1` now writes `intake_handoff_v1` and launches the approved explicit recipe with source-input forwarding; `driver.py` now supports explicit `input_images` override plumbing alongside the existing PDF/DOCX/XLSX surfaces; and the updated e2e/tests plus fresh driver proofs confirm the seam is real in code rather than only in story prose.
- **Data contracts / schemas**: likely touched surfaces are `intake_plan_v1`, a new or widened handoff artifact schema, and `RunConfig` if images-dir or plan-backed launch fields are required. If new fields cross artifact boundaries, they must be added to `schemas.py` before stamped artifacts rely on them.
- **File sizes**: `driver.py` is 2231 lines and `schemas.py` is 1217 lines, so keep edits narrow. `docs/build-map.md` is 582 lines and `docs/evals/registry.yaml` is 580 lines, so truth-surface edits should stay surgical. Likely owner files are otherwise small or moderate: `modules/intake/run_dispatch_v1/main.py` (35), `modules/intake/dispatch_hint_v1/main.py` (29), `modules/intake/confirm_plan_v1/main.py` (52), `configs/recipes/recipe-intake-contact-sheet.yaml` (53), `modules/intake/intake_plan_utils.py` (160), `modules/intake/contact_sheet_builder_v1/main.py` (204), `modules/intake/tests/test_intake_chain_e2e.py` (137), and `benchmarks/scripts/run_auto_book_type_detection_eval.py` (211).
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/build-map.md`, Story 011, Story 027, Stories 169-171, the current intake modules, and the existing C2 harness. No ADR, runbook, scout doc, or note currently owns the narrower confirmed-handoff semantics. A new ADR is only needed if the implementation grows beyond approved explicit recipe launch into planner-style user choice or hidden auto-routing.

## Files to Modify

- `modules/intake/run_dispatch_v1/main.py` — replace recipe-only shelling with approved-plan-to-launch handoff logic (35 lines)
- `modules/intake/intake_plan_utils.py` — shared helpers for source-input normalization and maintained handoff rules (160 lines)
- `configs/recipes/recipe-intake-contact-sheet-confirmed-handoff.yaml` — maintained explicit approval + launch path
- `driver.py` — add any missing explicit input override/config plumbing the chosen handoff path needs (2231 lines)
- `schemas.py` — add handoff artifact and/or `RunConfig` fields before stamped artifacts rely on them (1217 lines)
- `validate_artifact.py` — register any new handoff schema (112 lines)
- `modules/intake/tests/test_intake_chain_e2e.py` — e2e approved-plan launch coverage (137 lines)
- `tests/test_intake_plan_utils.py` — deterministic handoff-helper coverage (85 lines)
- `tests/test_run_config.py` — cover the new `RunConfig.input_images` field
- `docs/evals/registry.yaml` — update the C2 eval description, score notes, and retry conditions (580 lines)
- `docs/build-map.md` — update C2's post-story truth narrowly and honestly (582 lines)
- `docs/stories/story-027-contact-sheet-auto-intake.md` — align the maintained intake story with the new confirmed-handoff behavior if the story ships it (198 lines)

## Redundancy / Removal Targets

- `modules/intake/dispatch_hint_v1` as a separate tiny wrapper if a richer stamped handoff artifact makes it redundant
- The current dry-run-only / recipe-only semantics inside `run_dispatch_v1` if the real handoff path supersedes them
- Historical Story 027 wording that treats all dispatch behavior as purely legacy once a supported confirmed-handoff seam exists
- The ad hoc operator step of manually retyping a recipe path after inspecting `overview_plan_final.jsonl`

## Notes

- This story is about removing manual recipe selection, not about removing human approval. The user should still inspect and approve the plan at `confirm_plan_v1`.
- Prefer the smallest explicit launch surface that keeps reproducibility high. A config-backed downstream launch is attractive if it can carry every supported input kind honestly; otherwise a stamped handoff artifact plus direct driver invocation may be smaller.
- `images_dir` is the known substrate trap today because the current `RunConfig` surface is narrower than the driver/module substrate.
- If implementation pressure starts drifting toward editable planning, freeform branching, or non-explicit recipe choice, stop and reopen the architecture question instead of silently reintroducing Story 011 under a new name.

## Plan

1. Replace the recipe-only dispatch seam with a stamped approved-plan launch artifact (`M`)
   - Files: `modules/intake/run_dispatch_v1/main.py`, `modules/intake/intake_plan_utils.py`, `schemas.py`, `validate_artifact.py`, and the current `dispatch_hint_v1` surface if it survives.
   - Change: build one shared helper that reads an approved `intake_plan_v1`, resolves the exact maintained recipe plus source-input snapshot, and returns one of `launched`, `skipped`, `blocked`, or `failed` without making a second routing decision.
   - Artifact contract: emit a stamped handoff row that records the approved plan path, recommended recipe, source-input snapshot, exact downstream `driver.py` command, downstream `run_id`, and terminal outcome / reason.
   - Done when: supported `images_dir` and `pdf` plans produce inspectable handoff rows, and unsupported / missing-source cases write explicit non-launch outcomes instead of only printing to stdout.

2. Close the explicit `images_dir` override gap in the driver/config substrate (`S`)
   - Files: `driver.py` and `schemas.py`.
   - Change: add `--input-images` CLI support plus `RunConfig.input_images`, and apply it the same way existing PDF / DOCX / XLSX overrides already rewrite `recipe.input`.
   - Evidence to preserve: the existing driver stage wiring already passes `recipe.input.images` into extract and intake modules, so the missing slice appears to be override plumbing rather than deeper stage-command rewiring.
   - Done when: `driver.py` can launch `configs/recipes/recipe-images-ocr-html-mvp.yaml` against a non-default image directory without editing the recipe.

3. Collapse the stale two-step hint + runner surface into one clear maintained invocation path (`XS`)
   - Files: `modules/intake/dispatch_hint_v1/main.py`, `modules/intake/dispatch_hint_v1/module.yaml`, `modules/intake/run_dispatch_v1/module.yaml`, and `docs/stories/story-027-contact-sheet-auto-intake.md`.
   - Change: prefer one maintained post-confirm invocation surface. Either widen `dispatch_hint_v1` into the new stamped contract or retire it and let `run_dispatch_v1` consume the approved plan directly. Do not leave a stale tiny hint artifact plus a second opaque runner if they resolve the same data twice.
   - Structural note: `dispatch_hint_v1` currently advertises `output_schema: intake_plan_v1` while writing an ad hoc JSON blob, so schema truth needs cleanup in the same slice.
   - Done when: there is one documented maintained handoff path after `confirm_plan_v1`, not two partially overlapping seams.

4. Add focused tests and a truthful C2 proof surface (`M`)
   - Files: `tests/test_intake_plan_utils.py`, `modules/intake/tests/test_intake_chain_e2e.py`, and either `benchmarks/scripts/run_auto_book_type_detection_eval.py` or a small sibling harness with any scorer changes required.
   - Change: add unit coverage for plan-to-launch resolution and negative outcomes, then add intake-chain coverage that proves approved image-directory and PDF plans produce the expected launch recipe plus input overrides. Prefer subprocess mocking or narrow first-stage proofs in CI over running the full expensive downstream recipes there.
   - Baseline to beat: the current seam is `0/3` on representative approved plans for source-input forwarding, because every dry-run launch collapses to `python driver.py --recipe <recommended_recipe>`.
   - Done when: image-directory, scanned-PDF, and born-digital-PDF launch cases are covered honestly and the harness story for C2 is still readable.

5. Run fresh manual proofs and update truth surfaces narrowly (`M`)
   - Files: `docs/evals/registry.yaml`, `docs/build-map.md`, and this story's work log.
   - Change: run fresh approved-plan handoff proofs for one image-directory input, one scanned PDF input, and one born-digital PDF input. Inspect the stamped handoff artifact and the first downstream stamped artifact for each run under `output/runs/`.
   - Truth discipline: only promote C2 / B10 as far as the fresh evidence justifies. If any manual seam remains after approved handoff, record it explicitly instead of over-claiming.
   - Done when: the work log names the inspected artifact paths plus sample data, and the build-map / eval wording matches the real post-story state.

Approval and risk notes:
- No ADR is needed if the implementation stays inside approved-plan-to-explicit-recipe launch plumbing. Re-open the architecture question if the solution starts drifting toward planner-like user choice or hidden auto-routing.
- The main blast-radius risk is localized to `driver.py` and `schemas.py`; keep edits surgical and let new helpers absorb the plan-to-launch translation.
- Small scope expansion already folded into the story: add first-class `images_dir` override plumbing so the image-directory lane is honestly buildable through the same handoff path as PDF plans.

## Work Log

20260401-0906 — story created from `/triage`: scoped the missing C2 handoff seam between approved intake plans and downstream explicit recipe runs. Evidence reviewed in this pass: `docs/build-map.md` still says C2 remains `climb` because the workflow stops at recommendation / confirmation; `auto-book-type-detection` already passes; `configs/recipes/recipe-intake-contact-sheet.yaml` ends at `confirm_plan_v1`; `modules/intake/run_dispatch_v1/main.py` exists but only shells `driver.py --recipe <path>`; and `driver.py` / `schemas.py` expose only partial input-override substrate for this seam. Result: the story is `Pending`, not `Draft`, because the intake, recipe-selection, and driver substrates already exist in code and the remaining gap is a bounded confirmed-handoff implementation. Next step: `/build-story` should measure the current dispatch baseline on representative approved plans and choose the smallest honest handoff surface.
20260401-1026 — `/build-story` exploration completed and the implementation plan was tightened around the real missing seam instead of the imagined one. Alignment check: proceed. This closes a live Ideal gap in zero-config ingest and transparency rather than optimizing a stale compromise. Context reviewed in this pass: `docs/ideal.md`, `docs/spec.md` (`spec:1`, `spec:8`, `spec:9`), the relevant Category 1 / 8 / 9 sections plus Input Coverage rows in `docs/build-map.md`, Stories 011 / 027 / 169 / 170 / 171, `modules/intake/run_dispatch_v1/main.py`, `modules/intake/dispatch_hint_v1/main.py`, `modules/intake/confirm_plan_v1/main.py`, `modules/intake/intake_plan_utils.py`, `modules/intake/contact_sheet_builder_v1/main.py`, `modules/intake/tests/test_intake_chain_e2e.py`, `tests/test_intake_plan_utils.py`, `driver.py`, `schemas.py`, and `validate_artifact.py`. Fresh baseline evidence: representative approved-plan dry runs for an image-directory plan, a scanned-PDF plan, and a born-digital-PDF plan all collapsed to `python driver.py --recipe <recommended_recipe>` with no source-input forwarding, so the current source-forwarding baseline is `0/3`; `dispatch_hint_v1` preserved only `recommended_recipe`, `plan_path`, `capability_gaps`, and `warnings`, so the current handoff artifact baseline is `0/3` for source-input trace; and a missing-recipe case exited with status `3` plus a console message only, with no stamped terminal-outcome artifact. Critical substrate verified versus missing: the maintained recipe-selection logic and source-input metadata already exist (`modules/intake/intake_plan_utils.py`, `modules/intake/contact_sheet_builder_v1/main.py`), and `driver.py` already forwards `recipe.input.images` / `pdf` into extract and intake modules; the missing slice is the approved-plan-to-launch translation, an inspectable handoff artifact, and first-class `images_dir` override plumbing in `RunConfig` / CLI. Files likely to change remain the intake handoff modules, `driver.py`, `schemas.py`, focused tests, and the C2 truth surfaces; files at highest risk are `driver.py` and `schemas.py` because they are already large. Patterns to follow: keep `confirm_plan_v1` as the human approval boundary, reuse deterministic helper-based routing from `intake_plan_utils.py`, and keep downstream launch explicit and inspectable. Potential redundancy to remove: the current `dispatch_hint_v1` plus recipe-only `run_dispatch_v1` two-step if one stamped handoff surface can replace both honestly. Surprise found: `images_dir` is less blocked than first feared because the driver already threads `recipe.input.images` into stage commands; the real gap is override plumbing, not deep stage wiring. Next step: get approval on the plan, then move the story to `In Progress` and implement the narrow handoff + override slice.
20260401-1120 — implementation landed on the smallest maintained explicit seam: `run_dispatch_v1` now consumes the approved plan directly, `intake_plan_utils.py` deterministically resolves launch commands/outcomes, `schemas.py` / `validate_artifact.py` stamp `intake_handoff_v1`, `driver.py` gained `--input-images` plus `RunConfig.input_images`, and the stale `dispatch_hint_v1` module was removed. Focused verification passed fresh: `pytest -q tests/test_intake_plan_utils.py modules/intake/tests/test_intake_chain_e2e.py tests/test_run_config.py tests/test_pdf_intake_recipe.py` => `25 passed, 1 skipped`; `make lint` => pass; `make test` => `410 passed, 4 warnings`. Surprise found during implementation: the `images_dir` override seam was deeper than the first exploration pass suggested because `recipe-images-ocr-html-mvp.yaml` hardcoded the first stage's `params.input_dir`; the final fix therefore rewrites that stage param when `--input-images` / `input_images` is used instead of assuming the top-level recipe input alone is sufficient. Next step: run real confirmed-handoff proofs and inspect artifacts before touching build-map / eval truth.
20260401-1645 — fresh driver-backed confirmed-handoff proofs completed and truth surfaces updated. Evidence inspected manually: `output/runs/story176-image-proof/06_run_dispatch_v1/intake_handoff.jsonl` launched `configs/recipes/recipe-images-ocr-html-mvp.yaml` with `--input-images /Users/cam/Documents/Projects/doc-web/input/onward-to-the-unknown-images`, and `output/runs/story176-image-proof-recipe-images-ocr-html-mvp/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl` stamped `127` `page_image_v1` rows sourced from that image directory; `output/runs/story176-scanned-proof/06_run_dispatch_v1/intake_handoff.jsonl` launched `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` with `--input-pdf /Users/cam/Documents/Projects/doc-web/input/Onward to the Unknown.pdf`, and `output/runs/story176-scanned-proof-recipe-pdf-ocr-html-mvp/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl` stamped `127` `page_image_v1` rows sourced from that PDF; `output/runs/story176-born-proof/06_run_dispatch_v1/intake_handoff.jsonl` launched `configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml` with `--input-pdf /Users/cam/.codex/worktrees/6e2a/doc-web/testdata/tbotb-mini.pdf`, and `output/runs/story176-born-proof-recipe-born-digital-pdf-marker-lite-html-mvp/01_extract_pdf_marker_lite_html_v1/pages_html.jsonl` stamped `3` `page_html_v1` rows with reviewed Marker-lite HTML (`<h1 ...>The Brass Key</h1>` on the first page). Outcome: supported image-directory and PDF plans now have an explicit approved handoff with inspectable launch metadata, but C2/B10 stay `climb` because the broader 10-document corpus still stops at `intake_plan_v1` and unsupported/custom flows still require explicit YAML/config choices. Next step: `/validate` should review the changed files and proof artifacts for any missed regression before `/mark-story-done`.
20260401-1715 — `/mark-story-done` close-out completed after fresh validation confirmed the story is implementation-complete and ready to land. Fresh close-out evidence in this pass: `pytest -q tests/test_intake_plan_utils.py modules/intake/tests/test_intake_chain_e2e.py tests/test_run_config.py tests/test_pdf_intake_recipe.py` => `25 passed, 1 skipped`; `make lint` => pass; `make test` => `410 passed, 4 warnings`; and `python validate_artifact.py --schema intake_handoff_v1 --file output/runs/story176-image-proof/06_run_dispatch_v1/intake_handoff.jsonl`, `...story176-scanned-proof...`, and `...story176-born-proof...` => all passed. Manual artifact reinspection in this pass confirmed the stamped handoff rows still carry `plan_path`, `source_input`, and explicit downstream driver commands, and the inspected downstream artifacts remain `127` row image manifests for the image-directory/scanned-PDF proofs plus `3` `page_html_v1` rows for the born-digital proof. Close-out updates applied: acceptance criteria checked, workflow gates completed, story status moved to `Done`, `docs/stories.md` updated, and `CHANGELOG.md` refreshed. Next step: `/check-in-diff`.
