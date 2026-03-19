# Story 155 — Repo Mission Alignment Cleanup and Legacy Surface Removal

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #1 (Ingest), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Dossier-ready output, Graduate, don't accumulate
**Spec Refs**: spec:6 (Validation, Provenance & Export), spec:7 (Graduation & Dossier Handoff), spec:8 (AI Harnesses & Tooling), spec:9 (Planning Infrastructure), Retired Compromises note
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/notes/standalone-dossier-intake-runtime-plan.md`, `docs/notes/repo-mission-alignment-cleanup-inventory.md`, `README.md`, `docs/spec.md`
**Depends On**: Story 152

## Goal

Bring the repo back into alignment with the current mission by identifying and removing, archiving, or explicitly quarantining legacy surfaces that are no longer essential to intake R&D or the accepted `doc-web` graduation path. Fighting Fantasy processing is the clearest example, but the pass should cast wider: stale roadmap language, abandoned feature stubs, misleading active-looking recipes, obsolete validators, vendor payloads, and other architectural cruft that would confuse future extraction work or risk dragging the wrong baggage into `doc-web` and Dossier.

## Acceptance Criteria

- [x] A repo-wide cleanup inventory classifies legacy surfaces across docs, recipes, modules, tests, tools, and vendored payloads into `keep`, `remove now`, `archive/reference only`, or `blocked`, with concrete dependency evidence for each class.
- [x] Mission-facing docs no longer present Fighting Fantasy/gamebook work or other superseded product directions as active priorities for this repo, and they point clearly to the current intake + `doc-web` mission instead.
- [x] At least one safe removal pass lands for surfaces proven non-essential to the current mission, and every risky or blocked candidate is turned into an explicit follow-up instead of remaining as undocumented drift.
- [x] Validation proves the active repo path still works after cleanup: required tests and lint pass, and if current intake or `doc-web`-relevant pipeline behavior changes, a real `driver.py` or `make smoke` verification is run with manual artifact inspection.

## Out of Scope

- Creating the standalone `doc-web` repo itself
- Dossier-side implementation work
- Blind deletion of historical evidence, goldens, or generic pipeline modules just because they were once used by FF
- Rewriting mixed generic/legacy modules unless removal, archival, or profile-gating is necessary to keep the active mission coherent
- Product redesign or new feature work unrelated to cleanup, boundary clarity, or deprecation/removal

## Approach Evaluation

- **Simplification baseline**: First measure the real footprint with cheap repo inventory (`rg`, file counts, dependency traces) and ask whether that evidence already makes the highest-confidence removals obvious. If the baseline cleanly separates safe vs risky surfaces, do not build elaborate tooling.
- **AI-only**: An LLM can cluster likely cruft and suggest candidates, but it cannot safely decide deletions from names alone. Useful for triage summaries, unsafe as the sole decision-maker.
- **Hybrid**: Inventory with deterministic repo search and dependency checks, then use AI judgment to group candidates, spot mission drift, and prioritize removals. This is the leading candidate because the work is partly mechanical and partly architectural.
- **Pure code**: Aggressively delete everything matching `ff`, `gamebook`, or similar naming patterns. Fastest path, but too risky because some generic pieces were built in that era and some legacy surfaces may still be needed as archive/reference.
- **Repo constraints / prior decisions**: ADR-002 settled that `doc-web` is the reusable runtime boundary and that FF/gamebook-specific logic should not move forward. The extraction-plan note already says FF-specific logic stays behind, but it does not yet define what should be deleted vs archived vs kept as cold reference. `docs/spec.md` also explicitly says the retired FF-specific compromises are no longer part of the active mission.
- **Existing patterns to reuse**: Use the `keep` / `refactor before migrate` / `leave behind` / `archive only` classification pattern from `docs/notes/standalone-dossier-intake-runtime-plan.md`, the explicit keep/remove/archive inventory in `docs/notes/repo-mission-alignment-cleanup-inventory.md`, and the contract-driven cleanup discipline now being applied in Story 152.
- **Eval**: The deciding evidence is a before/after inventory plus validation that the active mission path remains intact. Baseline signals already observed during story creation: `20` FF-named recipe files, `36` FF/gamebook-oriented module directories, and `2611` repo text hits for legacy mission markers (`Fighting Fantasy`, `gamebook`, `FF Engine`, `gamebook.json`, `recipe-ff`, `turn to`).

## Tasks

- [x] Build the cleanup inventory:
  - audit docs, configs, modules, tests, tools, and vendored payloads
  - classify each candidate as `keep`, `remove now`, `archive/reference only`, or `blocked`
  - record the dependency evidence for each risky call
- [x] Remove or quarantine safe legacy surfaces:
  - stale mission-facing docs and roadmap text
  - stale Ideal / story-index / developer-entrypoint language that still presents FF/gamebook work as the active repo path
  - obviously obsolete FF/gamebook recipes, tools, or validators that are no longer part of the active mission
  - feature stubs, examples, or abandoned helper paths that still look active but are not part of the intake + `doc-web` direction
- [x] For mixed or ambiguous surfaces, decide one of:
  - keep with explicit rationale
  - archive/reference only with clearer placement or labeling
  - create a concrete follow-up if deletion depends on later extraction work
- [x] Update repo-facing documentation so future agents do not mistake archived FF/gamebook work for the active roadmap
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] Smoke/developer entrypoint behavior changed: ran `make smoke-legacy-ff`, then manually inspected `output/runs/smoke-legacy-ff/output/validation_report.json`, `output/runs/smoke-legacy-ff/output/gamebook.json`, and `output/runs/smoke-legacy-ff/16_report_pipeline_issues_v1/issues_report.jsonl`
  - [x] Post-removal active bundle verification: ran a real `driver.py` fixture-backed build through `load_artifact_v1` + `build_chapter_html_v1`, validated `04_build_chapter_html_v1/chapters_manifest_fixture.jsonl` against `chapter_html_manifest_v1`, and manually inspected the emitted `output/html/index.html`, `page-001.html`, and `page-002.html`
  - [x] Agent tooling did not change materially, so `make skills-check` was not required
- [x] Evals and goldens were not changed materially enough to require `/improve-eval` or `docs/evals/registry.yaml` updates
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: cleanup removed stale defaults without deleting active provenance contracts, and preserved FF reference surfaces remain explicitly classified in the inventory
  - [x] T1 — AI-First: AI helped group likely cruft, but every keep/remove/archive/blocked call was backed by concrete repo evidence
  - [x] T2 — Eval Before Build: the story began with repo-wide inventory counts and dependency traces rather than blind deletion
  - [x] T3 — Fidelity: the cleanup did not remove active intake or `doc-web` logic still needed by the current mission
  - [x] T4 — Modular: active `doc-web` / intake surfaces remain explicit, while retained FF surfaces are now labeled as legacy/reference-only
  - [x] T5 — Inspect Artifacts: manually inspected the renamed retained FF smoke artifacts after validation instead of trusting green logs alone

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: This is a repo-boundary and mission-alignment story spanning docs, recipes, modules, tests, tools, and archive/reference placement. No single pipeline stage owns it; the primary owner is the repo’s active mission surface.
- **Data contracts / schemas**: No schema change is intended by default. If cleanup removes or renames any still-active artifact surface, the story must update `schemas.py`, validator wiring, and dependent docs/tests explicitly rather than letting the boundary drift silently.
- **File sizes**: Active owner files are already large enough that cleanup should prefer deletion and relabeling over opportunistic rewrites: `modules/build/build_chapter_html_v1/main.py`, `docs/build-map.md`, `docs/RUNBOOK.md`, and the large historical story corpus under `docs/stories/`. Treat those as evidence or ownership surfaces first, not casual refactor targets.
- **Decision context**: Reviewed `docs/ideal.md`, `docs/spec.md`, ADR-002, the standalone extraction-plan note, and the cleanup inventory. No scout doc directly settles this cleanup boundary; the relevant guidance is architectural and mission-level, not a prior scout recommendation.

## Files Modified

- `docs/notes/repo-mission-alignment-cleanup-inventory.md` — new keep/remove/archive/blocked inventory plus explicit follow-ups
- `docs/reports/codebase-improvement/20260319-1528.md` — retained as a historical resolved scan so future audits do not misread mid-story findings as current cleanup guidance
- `README.md` — active mission/default-path framing aligned to intake + `doc-web`
- `docs/ideal.md` — Minimum Viable Floor generalized away from FF/gamebook output
- `docs/stories.md` — stale FF-first roadmap intro removed; story status updated
- `AGENTS.md` — generic smoke guidance replaced with recipe-specific validation guidance
- `docs/RUNBOOK.md` — legacy FF defaults removed from canonical execution guidance
- `docs/runbooks/check-in-worktree-landing.md` — validation guidance updated away from generic `make smoke`
- `Makefile` — generic `smoke` retired; no legacy FF smoke entrypoint remains
- `scripts/run_driver_monitored.sh` — usage example updated to an active structural-HTML recipe
- `scripts/smoke-ff-engine.sh` — deleted because it pointed at missing `recipe-ff-engine.yaml`
- `tests/fixtures/formats/_coverage-matrix.json` — legacy FF recipe reference clarified as non-default roadmap evidence
- `configs/recipes/onward-genealogy-build-regression.yaml`, `docs/RUNBOOK.md`, and `docs/build-map.md` — clarified that the maintained Onward regression lane reuses historical shared-output artifacts and is not a fresh-worktree smoke path
- `docs/notes/standalone-dossier-intake-runtime-plan.md` — archive-only guidance clarified for retained FF top-level surfaces
- `ai-work/issues/repo-baseline-cleanup.md` — deleted obsolete FF smoke-path issue log
- `docs/stories/story-155-repo-mission-alignment-cleanup-and-legacy-surface-removal.md` — updated plan, evidence, and completion state
- `tools/run_manager.py`, `tests/test_run_manager.py`, `Makefile`, `README.md`, `AGENTS.md`, `docs/RUNBOOK.md`, `docs/requirements.md`, `docs/document-ir.md`, `docs/pipeline-visibility.html`, `docs/runbooks/check-in-worktree-landing.md`, `settings.example.yaml`, and `tests/fixtures/formats/_coverage-matrix.json` — second-tranche mission/default-path cleanup
- `configs/recipes/recipe-ff*.yaml`, the FF legacy recipe family under `configs/recipes/legacy/`, and the FF export/validator/edgecase modules under `modules/` — deleted as no-longer-required legacy runtime surfaces
- FF-only scripts, tools, docs, examples, tests, and fixture packs — deleted with the runtime so the repo no longer carries dead gamebook/sample-book residue as current assets
- `driver.py`, `schemas.py`, `prompts/ocr_line_reconcile.md`, `modules/common/escalation_cache.py`, `modules/extract/extract_ocr_ensemble_v1/main.py`, `modules/portionize/detect_boundaries_html_v1/main.py`, `modules/adapter/pick_best_engine_v1/main.py`, and `modules/module_catalog.yaml` — final runtime seam cleanup and wording generalization after validation surfaced remaining live gamebook assumptions
- `modules/adapter/report_pipeline_issues_v1`, `modules/adapter/context_aware_post_process_v1`, `modules/adapter/context_aware_t5_v1`, and `tests/test_context_aware_post_process.py` — deleted because they were dead legacy adapters with no maintained recipe path

## Redundancy / Removal Targets

- Legacy mission framing that still presents Fighting Fantasy/gamebook processing as the active roadmap
- Ideal / story-index / smoke-entrypoint text that still treats FF as the default success path
- FF-only recipes under `configs/recipes/recipe-ff*.yaml` and related legacy recipe surfaces that no longer represent the current mission
- FF/gamebook export and validator paths that are no longer needed for active intake R&D
- Obsolete tools that only operate on `gamebook.json` or FF-specific combat/choice outputs
- Vendored validator payloads and other large legacy assets that are kept only by inertia
- Feature stubs, abandoned helper paths, broken smoke scripts, and old docs that still look active enough to mislead future agents

## Notes

- This story should cast a wider net than FF-only deletion. The real goal is mission alignment and architectural clarity, not aesthetic cleanup.
- If a legacy surface is still useful as cold reference, move it behind explicit archive/reference labeling rather than leaving it mixed into the active path.
- Prefer two passes: inventory first, then safe removals. If the audit reveals a larger archive strategy question, record it explicitly instead of improvising a repo-wide purge.

## Plan

### Baseline / Eval

- Use a repo-wide dependency inventory rather than name-based deletion. Baseline evidence from exploration:
  - `docs/stories.md` still says "Finish Fighting Fantasy to 100% game-ready" in the recommended-order header.
  - `docs/ideal.md` still defines the Minimum Viable Floor as a scanned PDF gamebook-to-JSON success path.
  - `Makefile` hard-wires `make smoke` to `configs/recipes/recipe-ff-smoke.yaml`.
  - `scripts/smoke-ff-engine.sh` points to missing `configs/recipes/recipe-ff-engine.yaml`, making it a broken active-looking helper.
  - top-level FF recipes plus `build_ff_engine_v1` / `validate_ff_engine_*` still have live references in tests, package helpers, recipes, and docs, so they are not safe blind-deletion candidates.
- Success test for Story 155: a written cleanup inventory lands with evidence-backed `keep` / `remove now` / `archive/reference only` / `blocked` classifications, the first safe removal tranche eliminates misleading mission/default-path surfaces, and validation proves the remaining active repo path still works.

### Implementation Order

1. Freeze the cleanup inventory in `docs/notes/repo-mission-alignment-cleanup-inventory.md`.
   - Cover docs, recipes, modules, tests, tools, and vendored payloads.
   - Record dependency evidence for every non-obvious call, especially FF recipes and validator/export surfaces.
   - Done looks like: every candidate is classified as `keep`, `remove now`, `archive/reference only`, or `blocked`, with a concrete reason and any required follow-up called out explicitly.
2. Land the highest-confidence mission-facing cleanup pass.
   - Update `README.md`, `docs/ideal.md`, `docs/stories.md`, and related notes so the active repo mission is intake R&D plus `doc-web` graduation, not FF/gamebook completion.
   - Keep historical evidence and archive/reference docs, but stop presenting them as the recommended roadmap.
   - Done looks like: a future reader opening the README, Ideal, or story index would not mistake FF/gamebook work for the active north star.
3. Land the highest-confidence developer-surface cleanup pass.
   - Remove or quarantine broken/stale entrypoints such as `scripts/smoke-ff-engine.sh`, stale `settings.smoke.yaml` comments, and any default smoke wiring that currently advertises FF as the canonical active path.
   - Prefer relabeling or quarantining over inventing a brand-new generic smoke path unless an existing active verification loop already exists.
   - Done looks like: no top-level helper points to missing `recipe-ff-engine.yaml`, and repo-default developer instructions stop implying the FF smoke path is the active mission baseline.
4. Decide mixed legacy surfaces and turn the risky ones into explicit follow-ups.
   - Classify top-level `recipe-ff*.yaml`, `build_ff_engine_v1`, `validate_ff_engine_node_v1`, `validate_ff_engine_v2`, `validate_gamebook_smoke_v1`, and related tests/examples as `keep`, `archive/reference only`, or `blocked`.
   - If they stay for now, label them clearly or create follow-up stories instead of leaving them as ambient drift.
   - Done looks like: the repo no longer has ambiguous legacy surfaces that appear active only because nobody classified them.
5. Run touched-scope validation and complete the doc sweep.
   - Required baseline: `make test`, `make lint`.
   - Run `make skills-check` if agent-tooling surfaces change.
   - Run `make smoke` or a replacement verification loop only if the smoke/developer path changes materially, and inspect output artifacts manually if a pipeline run occurs.
   - Done looks like: cleanup passes are validated, any changed smoke path is exercised honestly, and artifact inspection is recorded when pipeline behavior changes.

### Impact / Risk

- Highest-risk surfaces: `configs/recipes/recipe-ff*.yaml`, `modules/export/build_ff_engine_v1`, `modules/validate/validate_ff_engine_node_v1`, `modules/validate/validate_ff_engine_v2`, and tests that still assert `gamebook.json` behavior. Exploration found active references across recipes, package helpers, docs, and tests, so these are not safe first-pass deletions.
- Small scope expansion folded into this story: `docs/ideal.md`, `Makefile`, `settings.smoke.yaml`, and `scripts/smoke-ff-engine.sh`. Rationale: leaving them unchanged would keep the repo-default mission and verification path misaligned even if the README and inventory were cleaned up.
- Recommended decision for the first tranche: quarantine or relabel legacy FF smoke surfaces before attempting to replace them with a new generic smoke path. That keeps the story focused on mission alignment instead of inventing new pipeline behavior under cleanup cover.

## Work Log

20260319-1149 — story created: captured the repo-wide cleanup pass needed after the mission shift to intake R&D plus `doc-web` graduation. Evidence gathered during creation shows this is not speculative drift: `20` FF-named recipe files, `36` FF/gamebook-oriented module directories, and `2611` repo text hits for legacy mission markers still remain. Decision context reviewed: ADR-002, `docs/spec.md` retired-compromise note, the standalone extraction-plan note, and the FF-specificity audit. Next step: `/build-story` should turn this into an inventory-first removal plan, starting with mission-facing docs and other highest-confidence legacy surfaces.
20260319-1344 — exploration and planning: traced `docs/ideal.md`, `docs/spec.md`, Story 152, ADR-002, `docs/notes/standalone-dossier-intake-runtime-plan.md`, `docs/pipeline/ff-specificity-audit.md`, `README.md`, `docs/stories.md`, `Makefile`, `settings.smoke.yaml`, `scripts/smoke-ff-engine.sh`, `modules/validate/validate_ff_engine_v2/main.py`, `modules/validate/validate_gamebook_smoke_v1/main.py`, `tests/test_output_directory_structure.py`, `tests/test_validate_ff_engine_v2_node_integration.py`, and repo-wide `rg` inventories. Result: the highest-confidence first tranche is mission-facing docs plus broken/stale developer entrypoints; the FF export/validator stack is still live enough that it must be classified explicitly rather than deleted on sight. Evidence: `docs/stories.md` still says "Finish Fighting Fantasy to 100% game-ready", `docs/ideal.md` still makes a scanned PDF gamebook the Minimum Viable Floor, `Makefile` hard-wires `recipe-ff-smoke.yaml`, and `scripts/smoke-ff-engine.sh` points to missing `configs/recipes/recipe-ff-engine.yaml`. ADRs consulted: ADR-002 plus the extraction-plan note and FF-specificity audit; no additional ADR directly settles the cleanup boundary. Patterns to follow: inventory-first classification, safe removal of broken/misleading entrypoints before mixed legacy code, and explicit follow-up stories for blocked FF surfaces. Surprise: the story's original file list used stale worktree-specific absolute paths, and the repo rename did not fully propagate to the story index or default smoke path. Next: present the inventory-first plan for approval before implementation.
20260319-2234 — second-tranche validation and portability check: reran `make lint` and `make test` after the larger removal pass; both passed (`551 passed`). Attempted the maintained reuse recipe `configs/recipes/onward-genealogy-build-regression.yaml`, but it failed immediately in this workspace because the referenced Story 140 / 143 artifacts are not present under the local shared `output/` root. Rather than hide that gap, relabeled the recipe and docs as an artifact-reuse lane. To keep the active `doc-web` seam validation real, created a fixture-backed `driver.py` recipe that exercised `load_artifact_v1` + `build_chapter_html_v1` and wrote `output/runs/story155-docweb-fixture-build/`; `python validate_artifact.py --schema chapter_html_manifest_v1 --file output/runs/story155-docweb-fixture-build/04_build_chapter_html_v1/chapters_manifest_fixture.jsonl` reported `Validation OK: 2 rows match chapter_html_manifest_v1`, and manual inspection confirmed `output/runs/story155-docweb-fixture-build/output/html/index.html` renders the book title and contents, `page-001.html` contains the expected H1 + navigation shell, and `page-002.html` preserves the inline image as a `<figure>` with copied `images/photo.jpg`, VLM-style alt text, and `The fixture family` figcaption. Search follow-up: `deathtrap dungeon` is gone from live repo surfaces and `robot commando` now appears only in historical story titles. Next: if we want a self-contained maintained Onward regression lane, create a follow-up that vendors or regenerates the Story 140 / 143 artifact set instead of depending on ambient `output/runs/`.
20260319-2248 — final legacy-runtime seam removal after validation feedback: removed the last live gamebook/runtime branches from `driver.py`, deleted dead legacy adapters (`report_pipeline_issues_v1`, `context_aware_post_process_v1`, `context_aware_t5_v1`) plus their last direct test, removed the stale `associate_illustrations_to_sections_v1` catalog entry, and generalized the surviving numbered-section prompts/schema comments so they no longer present FF/gamebook semantics as active defaults. Validation rerun: `make lint` passed, `make test` passed (`350 passed` after the deletion-heavy suite trim), and a fresh fixture-backed `driver.py` run wrote `output/runs/story155-docweb-fixture-build-r2/`. `python validate_artifact.py --schema chapter_html_manifest_v1 --file output/runs/story155-docweb-fixture-build-r2/04_build_chapter_html_v1/chapters_manifest_fixture.jsonl` reported `Validation OK: 2 rows match chapter_html_manifest_v1`. Manual inspection confirmed `output/runs/story155-docweb-fixture-build-r2/output/html/index.html` renders the title, author, and contents; `output/runs/story155-docweb-fixture-build-r2/output/html/page-001.html` contains the expected H1 content for the first fixture page; and `output/runs/story155-docweb-fixture-build-r2/output/html/page-002.html` preserves the inline image as `<figure><img ... alt="A family portrait from the fixture set">...<figcaption>The fixture family</figcaption></figure>` with the copied `output/runs/story155-docweb-fixture-build-r2/output/html/images/photo.jpg` asset. Search follow-up: remaining `Fighting Fantasy`, `gamebook`, `Robot Commando`, and `Deathtrap Dungeon` hits outside `output/` are now limited to intentional historical/decision records and story titles.
20260319-2251 — closeout documentation polish after `/validate`: tightened `docs/notes/repo-mission-alignment-cleanup-inventory.md` so the final-state note explicitly names the intentional remaining historical/decision surfaces (`docs/spec.md`, the standalone runtime plan note, and ADR-002 decision/research docs), and rewrote `docs/reports/codebase-improvement/20260319-1528.md` as a historical resolved scan instead of a stale current-state recommendation. No runtime behavior changed; this closed the remaining Story 155 validation nits without reopening scope.
20260319-2208 — second removal tranche landed: replaced the remaining FF default in `tools/run_manager.py` with the active image-to-HTML recipe, removed the retained FF recipe family and the FF export/validator/edgecase packaging stack, deleted the attached regression scripts/tests/fixture packs, and scrubbed current docs/tests of the sample-book references that were still leaking into live repo surfaces. Next: rerun repo checks, try the maintained no-AI regression lane, and fall back to a real fixture-backed bundle build if the reuse recipe still depends on missing historical artifacts in this workspace.
20260319-2135 — cleanup tranche shipped and story closed: added `docs/notes/repo-mission-alignment-cleanup-inventory.md` with explicit `keep` / `remove now` / `archive/reference only` / `blocked` classifications across docs, recipes, modules, tests, tools, and vendored validator payloads; updated mission/default-path docs (`README.md`, `docs/ideal.md`, `docs/stories.md`, `AGENTS.md`, `docs/RUNBOOK.md`, `docs/runbooks/check-in-worktree-landing.md`) so they now center intake + `doc-web` instead of FF/gamebook completion; renamed the retained FF smoke path to `make smoke-legacy-ff`; deleted broken `scripts/smoke-ff-engine.sh`; relabeled top-level FF recipes and the FF example JSON as legacy/reference-only. Validation: `make lint` passed, `make test` passed (`639 passed, 6 skipped`), `make smoke-legacy-ff` passed, and manual artifact inspection confirmed `output/runs/smoke-legacy-ff/output/validation_report.json` is `is_valid: true` with `0` errors / `0` warnings, `output/runs/smoke-legacy-ff/output/gamebook.json` contains sections `3`-`8` with populated `presentation_html` and gameplay sequences, and `output/runs/smoke-legacy-ff/16_report_pipeline_issues_v1/issues_report.jsonl` reports `issue_count: 0`. Remaining FF archive/removal work was not hidden; it was moved into the new inventory as explicit blocked follow-ups (notably `tools/run_manager.py`, top-level `recipe-ff*.yaml` relocation, and the FF export/validator stack). Next: none in this story; future cleanup should start from the explicit follow-up list in `docs/notes/repo-mission-alignment-cleanup-inventory.md`.
