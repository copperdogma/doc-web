# Story 155 — Repo Mission Alignment Cleanup and Legacy Surface Removal

**Priority**: High
**Status**: Pending
**Ideal Refs**: Requirement #1 (Ingest), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Dossier-ready output, Graduate, don't accumulate
**Spec Refs**: spec:6 (Validation, Provenance & Export), spec:7 (Graduation & Dossier Handoff), spec:8 (AI Harnesses & Tooling), spec:9 (Planning Infrastructure), Retired Compromises note
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/notes/standalone-dossier-intake-runtime-plan.md`, `docs/pipeline/ff-specificity-audit.md`, `README.md`, `docs/spec.md`
**Depends On**: Story 152

## Goal

Bring the repo back into alignment with the current mission by identifying and removing, archiving, or explicitly quarantining legacy surfaces that are no longer essential to intake R&D or the accepted `doc-web` graduation path. Fighting Fantasy processing is the clearest example, but the pass should cast wider: stale roadmap language, abandoned feature stubs, misleading active-looking recipes, obsolete validators, vendor payloads, and other architectural cruft that would confuse future extraction work or risk dragging the wrong baggage into `doc-web` and Dossier.

## Acceptance Criteria

- [ ] A repo-wide cleanup inventory classifies legacy surfaces across docs, recipes, modules, tests, tools, and vendored payloads into `keep`, `remove now`, `archive/reference only`, or `blocked`, with concrete dependency evidence for each class.
- [ ] Mission-facing docs no longer present Fighting Fantasy/gamebook work or other superseded product directions as active priorities for this repo, and they point clearly to the current intake + `doc-web` mission instead.
- [ ] At least one safe removal pass lands for surfaces proven non-essential to the current mission, and every risky or blocked candidate is turned into an explicit follow-up instead of remaining as undocumented drift.
- [ ] Validation proves the active repo path still works after cleanup: required tests and lint pass, and if current intake or `doc-web`-relevant pipeline behavior changes, a real `driver.py` or `make smoke` verification is run with manual artifact inspection.

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
- **Existing patterns to reuse**: Use the `keep` / `refactor before migrate` / `leave behind` / `archive only` classification pattern from `docs/notes/standalone-dossier-intake-runtime-plan.md`, the module inventory from `docs/pipeline/ff-specificity-audit.md`, and the contract-driven cleanup discipline now being applied in Story 152.
- **Eval**: The deciding evidence is a before/after inventory plus validation that the active mission path remains intact. Baseline signals already observed during story creation: `20` FF-named recipe files, `36` FF/gamebook-oriented module directories, and `2611` repo text hits for legacy mission markers (`Fighting Fantasy`, `gamebook`, `FF Engine`, `gamebook.json`, `recipe-ff`, `turn to`).

## Tasks

- [ ] Build the cleanup inventory:
  - audit docs, configs, modules, tests, tools, and vendored payloads
  - classify each candidate as `keep`, `remove now`, `archive/reference only`, or `blocked`
  - record the dependency evidence for each risky call
- [ ] Remove or quarantine safe legacy surfaces:
  - stale mission-facing docs and roadmap text
  - obviously obsolete FF/gamebook recipes, tools, or validators that are no longer part of the active mission
  - feature stubs or abandoned helper paths that still look active but are not part of the intake + `doc-web` direction
- [ ] For mixed or ambiguous surfaces, decide one of:
  - keep with explicit rationale
  - archive/reference only with clearer placement or labeling
  - create a concrete follow-up if deletion depends on later extraction work
- [ ] Update repo-facing documentation so future agents do not mistake archived FF/gamebook work for the active roadmap
- [ ] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [ ] Run required checks for touched scope:
  - [ ] Default Python checks: `make test`
  - [ ] Default Python lint: `make lint`
  - [ ] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py` or `make smoke`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [ ] If agent tooling changed: `make skills-check`
- [ ] If evals or goldens changed: run `/improve-eval` and update `docs/evals/registry.yaml`
- [ ] Search all docs and update any related to what we touched
- [ ] Verify Central Tenets:
  - [ ] T0 — Traceability: cleanup does not delete active provenance surfaces or evidence needed to explain current outputs
  - [ ] T1 — AI-First: use AI to help classify and prioritize, but do not let it guess deletions without repo evidence
  - [ ] T2 — Eval Before Build: measure the real legacy footprint before removing anything substantial
  - [ ] T3 — Fidelity: cleanup must not silently remove active document-quality logic still needed by the intake path
  - [ ] T4 — Modular: retained generic surfaces stay explicit, and archived legacy surfaces stop masquerading as active architecture
  - [ ] T5 — Inspect Artifacts: if current pipeline behavior changes, inspect artifacts rather than trusting green logs

## Workflow Gates

- [ ] Build complete: implementation finished, required checks run, and summary shared
- [ ] Validation complete or explicitly skipped by user
- [ ] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: This is a repo-boundary and mission-alignment story spanning docs, recipes, modules, tests, tools, and archive/reference placement. No single pipeline stage owns it; the primary owner is the repo’s active mission surface.
- **Data contracts / schemas**: No schema change is intended by default. If cleanup removes or renames any still-active artifact surface, the story must update `schemas.py`, validator wiring, and dependent docs/tests explicitly rather than letting the boundary drift silently.
- **File sizes**: `README.md` is 72 lines, `docs/spec.md` is 198 lines, `docs/stories.md` is 177 lines, `docs/notes/standalone-dossier-intake-runtime-plan.md` is 88 lines, `docs/pipeline/ff-specificity-audit.md` is 144 lines, `configs/recipes/recipe-ff.yaml` is 523 lines, `configs/recipes/recipe-ff-smoke.yaml` is 232 lines, `modules/export/build_ff_engine_v1/main.py` is 1275 lines, and `modules/validate/validate_ff_engine_node_v1/main.py` is 99 lines. Treat large legacy files as inventory/removal candidates first, not eager refactor targets.
- **Decision context**: Reviewed `docs/ideal.md`, `docs/spec.md`, ADR-002, the standalone extraction-plan note, and the FF-specificity audit. No scout doc directly settles this cleanup boundary; the relevant guidance is architectural and mission-level, not a prior scout recommendation.

## Files to Modify

- /Users/cam/.codex/worktrees/adef/doc-web/docs/notes/repo-mission-alignment-cleanup-inventory.md — record the repo-wide keep/remove/archive/blocked classification (new file)
- /Users/cam/.codex/worktrees/adef/doc-web/README.md — remove stale FF/gamebook mission framing and align examples with the active intake + `doc-web` direction (72 lines)
- /Users/cam/.codex/worktrees/adef/doc-web/docs/spec.md — reconcile active mission language with the retired FF-specific compromise note if cleanup exposes additional drift (198 lines)
- /Users/cam/.codex/worktrees/adef/doc-web/docs/stories.md — remove stale roadmap notes or active-priority framing that still centers FF work, and add this story row correctly (177 lines)
- /Users/cam/.codex/worktrees/adef/doc-web/docs/notes/standalone-dossier-intake-runtime-plan.md — align `leave behind` / `archive only` guidance with the cleanup inventory (88 lines)
- /Users/cam/.codex/worktrees/adef/doc-web/docs/pipeline/ff-specificity-audit.md — reuse or update the audit so it serves current cleanup decisions instead of only reuse analysis (144 lines)
- /Users/cam/.codex/worktrees/adef/doc-web/configs/recipes/recipe-ff.yaml — delete, archive, or clearly quarantine only if dependency analysis proves it is not part of the active mission (523 lines)
- /Users/cam/.codex/worktrees/adef/doc-web/configs/recipes/recipe-ff-smoke.yaml — same as above for the lingering FF smoke path (232 lines)
- /Users/cam/.codex/worktrees/adef/doc-web/modules/export/build_ff_engine_v1/main.py — remove or quarantine only if the inventory proves it is purely legacy and not serving an active archive/reference obligation (1275 lines)
- /Users/cam/.codex/worktrees/adef/doc-web/modules/validate/validate_ff_engine_node_v1/main.py — same for the node validator wrapper and related payloads (99 lines)
- /Users/cam/.codex/worktrees/adef/doc-web/docs/stories/story-155-repo-mission-alignment-cleanup-and-legacy-surface-removal.md — keep the story current as the cleanup plan lands

## Redundancy / Removal Targets

- Legacy mission framing that still presents Fighting Fantasy/gamebook processing as the active roadmap
- FF-only recipes under `configs/recipes/recipe-ff*.yaml` and related legacy recipe surfaces that no longer represent the current mission
- FF/gamebook export and validator paths that are no longer needed for active intake R&D
- Obsolete tools that only operate on `gamebook.json` or FF-specific combat/choice outputs
- Vendored validator payloads and other large legacy assets that are kept only by inertia
- Feature stubs, abandoned helper paths, and old docs that still look active enough to mislead future agents

## Notes

- This story should cast a wider net than FF-only deletion. The real goal is mission alignment and architectural clarity, not aesthetic cleanup.
- If a legacy surface is still useful as cold reference, move it behind explicit archive/reference labeling rather than leaving it mixed into the active path.
- Prefer two passes: inventory first, then safe removals. If the audit reveals a larger archive strategy question, record it explicitly instead of improvising a repo-wide purge.

## Plan

Pending — `/build-story` should first freeze the inventory and identify the highest-confidence removal tranche before editing large legacy codepaths.

## Work Log

20260319-1149 — story created: captured the repo-wide cleanup pass needed after the mission shift to intake R&D plus `doc-web` graduation. Evidence gathered during creation shows this is not speculative drift: `20` FF-named recipe files, `36` FF/gamebook-oriented module directories, and `2611` repo text hits for legacy mission markers still remain. Decision context reviewed: ADR-002, `docs/spec.md` retired-compromise note, the standalone extraction-plan note, and the FF-specificity audit. Next step: `/build-story` should turn this into an inventory-first removal plan, starting with mission-facing docs and other highest-confidence legacy surfaces.
