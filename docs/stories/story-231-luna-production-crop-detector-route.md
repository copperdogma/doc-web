---
title: "Integrate GPT-5.6 Luna into the Production Crop Detector Route"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #4 (Illustrate), Requirement #6 (Validate), AI-First, Fidelity to the source, Traceability is the product"
spec_refs:
  - "spec:4"
  - "spec:4.1"
  - "spec:4.2"
  - "spec:8"
adr_refs: []
depends_on:
  - "198"
  - "207"
  - "209"
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
roadmap_tags: []
legacy_system: ""
---

# Story 231 — Integrate GPT-5.6 Luna into the Production Crop Detector Route

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/registry.yaml`, `docs/evals/attempts/023-gpt56-luna-price-refresh.md`, `docs/runbooks/crop-eval-workflow.md`, Stories 184/198/207/209, `configs/recipes/recipe-onward-images-html-mvp.yaml`, `modules/extract/crop_illustrations_guided_v1/main.py`, `modules/common/openai_client.py`, `tests/test_crop_runtime_recipe_contract.py`, and `None found after search in docs/decisions/`, `docs/scout/`, or `docs/notes/` for a narrower crop-provider-routing ADR
**Depends On**: Stories 198, 207, 209

## Goal

Turn Luna's fresh detector-value evidence into an attributable production crop route without weakening the page-context safety boundary. Add a strict first-party OpenAI Responses path that the shared guided crop module can use for `gpt-5.6-luna`, select Luna for the maintained Onward detector only if a bounded real `driver.py` comparison preserves artifact quality, retain GPT-5.5 as the separate `crop-page-level-deletion-gate` validator, and leave an auditable rollback to Gemini 3 Flash if the runtime prompt/artifact seam regresses.

## Eval Ladder Context

- **Root/full-path proof**: a real `driver.py` crop-stage run producing the existing `illustration_manifest.jsonl` rows and image files under `output/runs/`, followed by manual inspection of the manifest and representative crops. Full 127-page publication rebuild is deferred unless the bounded runtime comparison exposes downstream ambiguity; the story does not change build-stage schemas.
- **Parent detector eval**: Attempt 023 measured exact first-party `gpt-5.6-luna` at `13/13`, `0.9650`, `2306 ms`, and `$0.00892992` total versus fresh Gemini 3 Flash at `13/13`, `0.9634`, `6355 ms`, and `$0.0483065`.
- **Maintained safety parent**: Story 209 / Attempt 015 keeps GPT-5.5 at `22/22` on `crop-page-level-deletion-gate`; Luna's existing `19/22` result is disqualifying for that distinct role.
- **Measured runtime gap**: the production `_call_vlm_boxes` OpenAI Responses branch passes `temperature=0.0` and requests loose prompt-only JSON. A fresh exact Luna probe on checked-in public `Image000` reached the provider but failed HTTP 400: `temperature` is unsupported. The production route is therefore not callable by model-name substitution today.
- **Child proof**: focused provider-contract tests plus a same-input `driver.py` comparison on representative cover, certificate/seal, multi-photo, and caption-bearing illustration pages. If Luna is promoted in the recipe, rerun the maintained detector benchmark only when the runtime prompt/schema is deliberately aligned with that benchmark; otherwise keep Attempt 023 as model evidence and record the driver artifact comparison separately.

## Acceptance Criteria

- [x] The production crop runtime can call exact `gpt-5.6-luna` through OpenAI Responses without unsupported sampling parameters, with `store=false`, strict task-appropriate JSON Schema, exact served-model verification, terminal `completed` verification, valid usage evidence, and local contract validation.
- [x] Gemini behavior remains unchanged and the generic crop module retains an explicit recipe/config rollback to `gemini-3-flash-preview`; no book-specific branch is introduced in shared code.
- [x] A bounded production-equivalent `driver.py` comparison, mechanically aligned with the maintained recipe except for the compared detector and bounded page cap, produces traceable crop manifests and image artifacts for both Gemini and Luna under separate run IDs.
- [x] Manual source/artifact inspection covers at least `Image000`, `Image011`, `Image121`, and `Image124`, preserves the maintained cover bypass and upstream image metadata, classifies any mismatch as model-wrong, golden/reference-wrong, prompt/pipeline-wrong, or ambiguous, and confirms no missing crop, material clipping, caption/body-text contamination, or broken provenance is hidden by a green run.
- [x] Luna is selected in `recipe-onward-images-html-mvp.yaml` only if the production-equivalent driver comparison preserves the maintained crop contract; otherwise the story records the rejection and leaves Gemini selected.
- [x] `crop-page-level-deletion-gate` remains on `openai:responses:gpt-5.5` with its `22/22` contract and receives a regression assertion if current coverage does not already prevent accidental coupling to the detector model.
- [x] Focused tests, `make lint`, `make test`, methodology checks, a production-equivalent driver run, and manual artifact inspection pass; the story records exact paths and inspected sample data.

## Out of Scope

- Replacing GPT-5.5 on the page-context validator or rerunning Luna's known-failing 22-case safety gate without new capability evidence
- Deleting caption assist or `trim_layout_text`; those remain C4/C5 residue governed by their own proof surfaces
- Re-running expensive OCR or table extraction when a bounded checked-in/public crop input can prove this provider seam
- Claiming broad format graduation or updating coverage scores from a four-page runtime integration slice
- Refactoring the 5,828-line crop module beyond the smallest generic provider-boundary extraction needed for attributable Luna calls

## Approach Evaluation

- **Simplification baseline**: the single-model capability is already measured and passes. Attempt 023 proves one Luna call can perform detector reasoning; the missing work is provider/runtime orchestration, not another AI decomposition.
- **AI-only**: required for visual grounding, but a bare model-name swap is invalid because the current production branch sends unsupported `temperature` and has no strict response contract.
- **Hybrid**: strongest candidate. Preserve the existing AI detector plus bounded caption/layout post-processing, and use deterministic code only for provider request construction, schema/status/identity validation, usage logging, and artifact verification.
- **Pure code**: unsuitable for illustration understanding; useful only for the narrow request/contract adapter and comparison harness.
- **Repo constraints / prior decisions**: C4 is `converge`, C5 is `climb`; Stories 184 and 198 intentionally removed retired retry/validator complexity. The new route must not reintroduce those loops. Story 209 makes page-context `22/22` absolute. No new artifact schema or dependency is expected, and no narrower crop-provider ADR exists.
- **Existing patterns to reuse**: `benchmarks/providers/openai_responses_model.py` for exact identity/status/schema/privacy checks; `modules/common/openai_client.py` for centralized usage logging; recipe-scoped `rescue_model`; Story 184's driver-backed crop artifact inspection; `load_artifact_v1` and story-specific validation recipes for bounded reusable proof.
- **Eval**: same-input incumbent/candidate driver runs are decisive. Unit tests prove transport invariants; source-to-crop visual inspection proves semantics. The existing 13-case benchmark remains the upstream capability evidence.

## Tasks

- [x] Extract or add the smallest reusable strict OpenAI Responses vision helper for crop bbox and caption contracts; reject unsupported/incomplete/wrong-model responses before parsing.
- [x] Route the crop module's OpenAI Responses detector and caption calls through that helper while preserving Gemini and legacy Chat fallback behavior.
- [x] Add focused tests for Luna no-temperature requests, `store=false`, strict schemas, exact served identity, terminal state, usage evidence, contract failures, and unchanged Gemini routing.
- [x] Repair the bounded story fixture to preserve the maintained upstream image descriptions/counts and high-resolution source mapping without duplicating large image fixtures or rerunning OCR.
- [x] Derive both validation recipes from the maintained crop parameters, including `cover_pages`, high-resolution input, caption/layout behavior, and current C5 residue; whitelist only the compared model and bounded page cap as differences.
- [x] Run incumbent Gemini and candidate Luna through `driver.py` under fresh separate run IDs, then manually inspect manifests and crop images against their source pages and maintained residuals.
- [x] If and only if the production-equivalent artifact gate passes, change the maintained Onward detector recipe to `gpt-5.6-luna`, keep caption assist/layout trim, retain easy rollback, and update its config-contract test and crop runbook/spec wording. If it fails, retain Gemini and record the source-backed rejection.
- [x] Assert that the page-context benchmark remains pinned to GPT-5.5 and is not coupled to the recipe detector selection.
- [x] If this story changes documented format coverage or graduation reality: update `tests/fixtures/formats/_coverage-matrix.json` and methodology state honestly; no score movement is expected from this bounded integration proof.
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove only directly superseded request-construction duplication.
- [x] Run required checks for touched scope:
  - [x] Focused provider/crop/recipe pytest and Ruff checks
  - [x] `make test`
  - [x] `make lint`
  - [x] Clear crop-module `*.pyc`, run through `driver.py`, verify artifacts under `output/runs/`, and manually inspect JSONL plus images
  - [x] `make methodology-compile` and `make methodology-check`
  - [x] `make skills-check` because the current dirty task also installs/updates the repo's `evaluate-model` skill
- [x] If evals or goldens change: run `/improve-eval` and update `docs/evals/registry.yaml`; not applicable because the runtime follow-on changed no eval task, prompt, scorer, or golden
- [x] Search all docs and update any related to what was touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: Luna call metadata and emitted crops remain attributable to source page, request/model, usage, and processing step
  - [x] T1 — AI-First: visual judgment stays model-owned; code only enforces transport and contracts
  - [x] T2 — Eval Before Build: Attempt 023 and the fresh failing runtime probe precede implementation
  - [x] T3 — Fidelity: the production decision rejects Luna's observed caption contamination rather than hiding it behind its better count
  - [x] T4 — Modular: provider behavior is generic and recipe-selectable, not Onward-hardcoded
  - [x] T5 — Inspect Artifacts: source pages, JSONL, and every produced crop image are manually reviewed

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

- **Owning module / area**: Category 4 crop runtime, primarily `crop_illustrations_guided_v1` plus a small `modules/common` OpenAI Responses boundary and recipe-level provider selection.
- **Methodology reality**: `spec:4` substrate exists; C4 is `converge` and C5 is `climb`. The relevant `image-directory-scans` and `scanned-pdf-tables` rows both record `illustration_extraction = 0.9703`; this integration does not itself warrant changing that score.
- **Substrate evidence**: `rescue_model` already selects Gemini versus OpenAI generically; `modules/common/openai_client.py` wraps Responses and usage logging; Attempt 023 supplies strict Luna capability evidence; the repo contains canonical b64 source pages for the proposed four-case driver slice. The missing slice is an attributable strict production Responses request and a bounded driver fixture path.
- **Data contracts / schemas**: no emitted artifact schema change is planned. Strict provider response schemas are internal request contracts that normalize into the existing box dictionaries and `illustration_manifest.jsonl` rows.
- **File sizes**: `crop_illustrations_guided_v1/main.py` 5,828 lines (structural-health risk; avoid growing inline), `modules/common/openai_client.py` 84 lines, maintained Onward recipe 182 lines, crop runtime contract test 76 lines, crop runbook 123 lines, spec 199 lines.
- **Decision context**: reviewed the Ideal, spec C4/C5, methodology state/graph, coverage rows, crop runbook, relevant completed stories, current recipe/module/client/tests, and decision/scout/note searches. No new ADR is warranted for adding a provider-compatible implementation behind the existing recipe-selectable model seam; a cross-module provider abstraction beyond crop would be a separate architecture decision.

## Files to Modify

- `docs/stories/story-231-luna-production-crop-detector-route.md` — plan and evidence
- `modules/common/openai_crop_vision.py` (candidate new helper) — strict Responses request/contract boundary
- `modules/extract/crop_illustrations_guided_v1/main.py` — call the shared helper instead of constructing loose Luna-incompatible requests
- `tests/test_crop_illustrations_guided_v1.py` and/or a focused new provider test — transport and parsing regressions
- `configs/recipes/story-231-luna-crop-runtime-validate.yaml` — bounded driver comparison surface
- `configs/recipes/recipe-onward-images-html-mvp.yaml` — conditional maintained detector selection
- `tests/test_crop_runtime_recipe_contract.py` — maintained detector and page-context separation contract
- `docs/runbooks/crop-eval-workflow.md` and `docs/spec.md` — only if Luna passes the driver artifact gate
- `docs/methodology/graph.json` and `docs/stories.md` — generated views

## Redundancy / Removal Targets

- Duplicate loose OpenAI Responses request construction in `_call_vlm_boxes` and `_call_vlm_caption_boxes`, if the shared strict helper covers both without changing Gemini or Chat fallback behavior
- Any runtime wording that calls Gemini the maintained detector if Luna actually passes and is selected
- No retry, refine, validator, caption-assist, or layout-trim logic is a removal target in this story

## Notes

- New-story justification: Stories 207 and 209 own model proof and page-context safety; both are Done. Story 198 owns the completed crop-runtime simplification. This work crosses a new provider/runtime contract seam and requires driver-produced artifacts, so reopening a proof-surface or deletion story would blur a materially different validation boundary.
- The first malformed Image000 diagnostic double-prefixed an already complete data URL and was discarded. Repeating with the fixture unchanged reached Luna and proved the actual production failure: unsupported `temperature`.
- The current local `onward-book-r1` and external reviewed Onward runs are unsafe for wholesale upstream reuse according to current `run_registry.py` health checks. The plan therefore uses a fresh bounded validation run from canonical public fixtures instead of claiming an old run is globally trusted.

## Plan

1. **Contract boundary (S)** — Add a small crop-specific OpenAI Responses helper with strict bbox/caption JSON Schemas and fail-closed served-model, terminal-status, usage, and local-output checks. Omit sampling fields for Luna and set `store=false`. Keep usage logging through the existing client wrapper.
2. **Runtime wiring (S)** — Replace only the duplicated Responses request construction in the two crop VLM call sites. Preserve Gemini routing and legacy Chat fallback. Normalize strict helper results into the existing box metadata so emitted artifacts do not change schema.
3. **Focused proof (S)** — Add unit tests for request shape and all hard failures, plus a portable bounded validation recipe/preparation path that derives four representative source images from existing checked-in b64 fixtures without committing duplicate binaries or reusing unsafe upstream artifacts.
4. **Driver comparison and decision (M)** — Run separate Gemini and Luna driver runs on Image000/Image011/Image121/Image124. Inspect manifest rows and every produced crop against source. Promote Luna in the maintained Onward recipe only if crop count, fidelity, text exclusion, provenance, and terminal/identity evidence remain acceptable; otherwise retain Gemini.
5. **Truth and regression surfaces (S)** — Pin the maintained detector decision and the independent GPT-5.5 page-context role in tests/docs, regenerate methodology views, and run focused checks, full lint/test, skill checks, and diff checks.

**Impact / risks**: the main risk is semantic mismatch between the benchmark prompt and the richer production prompt, especially the `Image011` certificate title. The structural risk is adding more code to a 5,828-line module, which is why the provider contract belongs in a small common helper. The operational risk is accidental coupling of detector selection to page-context safety; a direct config test will prevent that. No schema migration, new dependency, or broad format claim is planned.

**Approval boundary**: this plan authorizes a maintained Onward recipe switch only after the same-input driver artifact gate passes. A failure leaves Gemini selected and still counts as a completed, evidence-backed integration attempt.

### Validation Repair Plan

1. **Restore production parity (S)** — Replace the synthetic image descriptions/counts with the exact maintained upstream metadata for the four pages. Copy the maintained crop parameter block into both bounded recipes, preserving the deterministic page-1 cover bypass, high-resolution source directory, caption/layout settings, and absence of dense splitting. Permit only `rescue_model` and the non-behavior-changing bounded `rescue_max_pages` cap to differ.
2. **Add the missing guardrail (S)** — Extend the recipe contract test so both story recipes are compared mechanically with the maintained crop stage under an explicit difference whitelist. Keep the existing candidate-versus-incumbent equality assertion.
3. **Rerun the real seam (M)** — Materialize the repaired manifest, verify the high-resolution four-page mapping, clear crop-module bytecode, and run fresh Gemini and Luna driver IDs. Inspect the deterministic cover, page-12 logo/seal/signature behavior, page-122 known two-crop C5 residual, page-125 caption exclusion, provenance, latency, and manifest hashes.
4. **Repair truth surfaces and validate (S)** — Replace the invalid cover-based production conclusion in this story, Attempt 023, and the crop runbook with the production-equivalent result. Run focused checks, full lint/test, skill and methodology checks, then hand back to `/validate 231` without closing the story.

**Repair approval**: the user approved this validation-repair plan with `yes` after `/validate 231` recommended `Keep open`. No new dependency, schema migration, broader format claim, or page-context rerun is authorized.

## Work Log

20260803-1409 — create-story + build-story exploration/plan: user approved turning Attempt 023's Luna value result into a production detector route while retaining GPT-5.5 page-context safety. Read the Ideal, spec C4/C5, methodology state/graph, coverage rows, crop runbook, Stories 184/198/207/209, current Onward recipe, 5,828-line guided crop module, common OpenAI/Gemini clients, runtime contract tests, and decision/scout/note searches. A new story is honest because this crosses from model-proof ownership into the production provider/request seam and requires driver artifacts. Verified existing substrate: recipe-selectable `rescue_model`, Responses-capable usage-logging client, canonical public b64 fixtures, and upstream detector/safety evals. Verified the missing substrate with a live current-code baseline: the corrected public Image000 probe reached exact `gpt-5.6-luna` but failed HTTP 400 because production sends unsupported `temperature=0.0`; the first probe was discarded because the diagnostic itself double-prefixed the complete data URI. Also checked reuse health: local `onward-book-r1` and the external reviewed Onward run currently report unsafe global health, so the plan uses a fresh bounded driver fixture rather than silently trusting old upstream state. No crop-provider ADR exists; the existing recipe seam is sufficient. Next: human approval of this written plan, then set Story 231 In Progress and implement the strict provider boundary before any recipe switch.
20260803-1413 — build-story implementation started after explicit user approval of the written Story 231 plan. Status moved from Pending to In Progress before code changes. The maintained recipe remains on Gemini during implementation; Luna selection is conditional on the same-input driver artifact gate. Next: add the small strict OpenAI crop-vision boundary and focused contract coverage, then run the bounded comparison.
20260803 — strict provider route: added `modules/common/openai_crop_vision.py` with strict detector/caption JSON Schemas, `store=false`, `reasoning=none`, no unsupported sampling field, and fail-closed exact model, completed state, incomplete detail, request ID, usage, and local bbox checks. Routed only `gpt-5.6-*` Responses calls through it; Gemini and legacy OpenAI Chat paths remain unchanged. Added request/contract tests and propagated detector/caption model, provider, and request IDs through crop transformations into every final manifest row. A fresh direct Image000 call completed as exact `gpt-5.6-luna`, proving the repaired provider seam is live.
20260803 — bounded driver fixture and repair loop: added `scripts/prepare_story231_crop_fixture.py` and paired Gemini/Luna recipes derived from four canonical checked-in b64 pages. The first driver attempt failed before inference because the recipe used unsupported `fail_on_missing`; removed it from both arms. The first successful Luna run then exposed an explicit no-caption `[0,0,0,0]` response that the new local contract rejected; the production prompt documents that sentinel, so the caption schema was corrected to admit only that all-zero exception. Focused tests, fixture `page_html_v1` validation, and both recipe plan resolutions passed after repair.
20260803 — superseded driver/artifact decision: the `story231-gemini-crop-runtime-r3` / `story231-luna-crop-runtime-r4` conclusion was invalidated by `/validate 231`; those recipes omitted the maintained cover bypass, high-resolution mapping, exact upstream metadata, and production split behavior. Their Image000 difference is not production evidence and must not be used for adoption.
20260803 — superseded traceability evidence: invalid pre-parity Gemini manifest SHA-256 `9e20c9464fff4d35883ba91c5660078e9244c83ca0c40e3ac8d42a891b7a5eb9`; invalid pre-parity Luna manifest SHA-256 `4eae70cfb702c9254c33589e5bf8091709d5f952e36eb869c2a4f11a4165875c`. These hashes remain only as audit history and are not production-adoption evidence. `validate_artifact.py` validated that run's input manifest as `page_html_v1`, but could not validate its emitted manifest because the module declares `illustration_v1` while the validator exposes no such schema; `image_crop_v1` correctly rejected the different row contract. This pre-existing validator/schema gap remains a health flag rather than being hidden or expanded into this provider-integration story.
20260803 — build validation complete: focused provider/crop/recipe coverage passed `49` tests and focused Ruff checks passed. Removed an accidental whole-file formatter diff from the 5,828-line crop module, reducing that review surface from 1,404 changed lines to 63, then re-ran validation on the exact cleaned state. `make lint`, `make skills-check`, `make methodology-compile`, `make methodology-check`, and `git diff --check` passed. The final full suite passed `928` tests in `739.64 s`; its only output beyond passes was four existing Pydantic `dict` deprecation warnings in `portionize_headers_numeric_v1`. Updated the crop runbook and Attempt 023 with the production follow-on and retained-provider decision. Build complete is checked, but Story 231 remains In Progress with the independent validation and mark-done gates intentionally open for `/validate 231`.
20260803 — `/validate 231` reopened the build after finding a high-risk parity miss. The maintained recipe sets `cover_pages: "1"`, so page 1 bypasses both detectors and cannot support the recorded Luna rejection; the story recipes omitted that bypass, added dense splitting absent from production, omitted the high-resolution source directory, and changed page-12 upstream image intent from four descriptions to two. On page 122, the added dense split produced three clean crops instead of exercising the maintained two-crop C5 residual. The paired-recipe test only proved the two invalid arms matched each other. Fresh validation still passed 49 focused tests, lint, skill synchronization, methodology checks, fixture schema validation, run-state/hash/provenance checks, and visual contact-sheet inspection; the evidence failure is semantic parity, not transport or artifact absence. Closure recommendation: Keep open. User approved the repair plan. Next: restore exact production parameters and upstream metadata, add a maintained-parity regression test, then rerun both providers under fresh IDs before revising the adoption decision.
20260803 — production-parity repair and decision: repaired the four-page fixture to exact upstream image counts `{1: 1, 12: 4, 122: 3, 125: 1}`, restored the high-resolution directory, deterministic `cover_pages: "1"` bypass, maintained caption/layout parameters, and absence of dense splitting, then added a regression test that mechanically compares each challenger recipe with the maintained recipe while allowing only `rescue_model` and the four-page cap to differ. Fresh runs `story231-gemini-production-parity-r1` and `story231-luna-production-parity-r1` both completed. Gemini produced eight crops with counts `{1: 1, 12: 3, 122: 3, 125: 1}` in `107.42 s`; its page-12 VLM boxes were invalid, so CV fallback combined the two signatures. Luna produced all nine expected crops in `47.71 s`, with strict detector/caption model, provider, and request IDs on every non-cover row. Manual comparison of all 17 crops with all four sources confirmed the cover was identical and deterministic, Luna improved page-12 completeness, and both providers preserved the primary image content. Luna nevertheless included the printed captions under the page-122 reunion photo and Sophie portrait, while Gemini excluded them. This is a model-wrong C5 text-exclusion failure at the production artifact seam, so the maintained recipe remains `gemini-3-flash-preview`; Luna remains the frozen-benchmark value winner and an explicit callable challenger. Evidence: Gemini manifest SHA-256 `1b6a4a665ae72ea7599642819c70dae44006197748da50c54afbaad68894c137`; Luna manifest SHA-256 `c66f0901e79e1de64fd4d221d697b6e6bdd3ab5ee09a9e2aec725f86d219f08f`; contact sheets `output/inspection/story231/sources-production-parity.jpg`, `gemini-production-parity-r1.jpg`, and `luna-production-parity-r1.jpg`.
20260803 — repaired-state build validation complete: added the maintained-recipe parity regression and fail-closed positive-area bbox check, then passed `51` focused tests plus focused Ruff. `make lint`, `make skills-check`, `make methodology-compile`, `make methodology-check`, fixture `page_html_v1` validation, and `git diff --check` all passed. The fresh full suite passed `930` tests in `756.24 s`; the only warnings were the same four existing Pydantic `dict` deprecations in `portionize_headers_numeric_v1`. Story 231 remains `In Progress`; Build complete is checked, while independent validation and mark-done gates remain open for `/validate 231`.
20260803 — independent `/validate 231` repair audit: reviewed all tracked and untracked changes, the exact Story 231 requirements, Ideal/spec alignment, current recipe/provider safety boundaries, raw Attempt 023 artifacts, both repaired driver manifests/run states, and all three production-parity contact sheets. No material code, behavior, security, or artifact defect was found. Fresh checks passed: `51` focused tests, focused and full Ruff, fixture `page_html_v1` validation, skill synchronization, methodology check, `git diff --check`, and the full `930`-test suite in `756.24 s` with only four pre-existing Pydantic deprecation warnings. The configured `codex review --uncommitted` signal was unavailable because Codex CLI `0.143.0` cannot run its configured `gpt-5.6-sol` review model; no review finding was produced, so the manual findings-first pass remains authoritative. Corrected two documentation-only bookkeeping issues: checked the completed parent validation task and explicitly marked the invalid pre-parity manifest hashes as superseded. Overall grade: A. Closure recommendation: Close now via `/mark-story-done 231`; story status remains `In Progress` and the mark-done gate remains unchecked for that workflow.
20260803 — `/mark-story-done 231`: confirmed all seven acceptance criteria, all task and Central Tenet checks, Build and Validation gates, Done dependencies 198/207/209, Attempt 023 registry evidence, production-equivalent driver artifacts, and the source-backed decision to retain Gemini after Luna's page-122 caption contamination. Closed Story 231 as Done, regenerated the methodology views, and added the CalVer changelog entry. Final close-out checks passed: methodology compile/check, Ruff over `modules/` and `tests/`, and the full `930`-test suite in `745.73 s`; the only output beyond passes was four pre-existing Pydantic deprecation warnings. No code changed after that run. Next: `/check-in-diff`.
