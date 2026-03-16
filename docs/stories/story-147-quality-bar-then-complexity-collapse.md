# Story 147 — Quality Bar Then Complexity Collapse

**Priority**: High
**Status**: Pending
**Ideal Refs**: Requirement #3 (Extract), Requirement #6 (Validate), Fidelity to the source, Transparency over magic, Graduate, don't accumulate
**Spec Refs**: `docs/spec.md` intro (compromises get deleted when resolved), C1, C3, C7
**Decision Refs**: `docs/build-map.md`, `docs/spec.md`, `docs/ideal.md`, Story 145 work log, Story 146 work log, `docs/decisions/adr-001-source-aware-consistency-strategy/adr.md`
**Depends On**: Story 145, Story 146

## Goal

Turn the project instinct into an explicit operating rule: first push an active converter or repair seam to an acceptable manual-review quality bar, then open a simplification / complexity-collapse pass instead of indefinitely stacking more workaround logic. The story should place that mandate in the build map's operating-system layer, define what "acceptable quality" means in codex-forge terms, and use the Onward genealogy table path after Story 146 as the first concrete candidate for a collapse roadmap back toward the Ideal's simpler execution model.

## Acceptance Criteria

- [ ] `docs/build-map.md` has an explicit cross-cutting operating rule under `Project Operating System` that says quality comes first, but once a converter reaches an acceptable reviewed bar the next planned step is simplification / complexity collapse rather than another unbounded layer of repair logic
- [ ] The build-map rule defines an inspectable acceptable-quality bar in project terms: real `driver.py` validation, artifacts in `output/runs/`, manual inspection on the known hard cases, and no known reviewed defects in the active slice
- [ ] The build map names the first tracked candidate for this rule, using the Onward scanned genealogy table path after Story 146 / `story146-onward-build-stitch-r5`, and records at least a first-pass inventory of likely collapse targets or simplification questions
- [ ] The story and `docs/stories.md` make this mandate discoverable to future triage / align passes as a cross-cutting project direction rather than an Onward-only note
- [ ] The story explicitly distinguishes "codify the mandate and candidate inventory" from "actually simplify the pipeline", so future implementation work can be scoped cleanly

## Out of Scope

- Deleting or refactoring existing rescue / rerun / build stages yet
- Claiming any compromise is already eliminated
- Rewriting `docs/spec.md` or the Ideal beyond what the current documents already say
- Reprioritizing unrelated input-format gaps such as born-digital PDF or handwriting intake

## Approach Evaluation

- **Simplification baseline**: There is no single-call model shortcut here; this is a cross-cutting workflow / roadmap clarification problem grounded in existing evidence, not a fuzzy generation problem.
- **AI-only**: An LLM could draft the mandate text or candidate inventory, but the authoritative output still has to be deterministic project docs tied to real runs and stories.
- **Hybrid**: Use AI to synthesize current workaround layers and collapse candidates from Story 146 / build-map evidence, then lock the result into docs with explicit human-verifiable references. This is the leading candidate because it keeps the rule grounded in actual artifacts.
- **Pure code**: Not applicable except for doc scaffolding and index updates.
- **Repo constraints / prior decisions**: `docs/spec.md` already says compromises are temporary and should be deleted when the detection signal says they are no longer needed; Story 145 made `docs/build-map.md` the human-readable project map; ADR-001 explicitly frames document-consistency planning as a compromise that should collapse away once stronger extraction makes it unnecessary.
- **Existing patterns to reuse**: `docs/build-map.md` Compromise Progress sections, Story 145's build-map convergence pattern, Story 146's work log and validated runs, and the existing `Next Actions` section for surfacing cross-cutting priorities.
- **Eval**: The deciding check is whether a future reader can open the build map and find: the mandate, the quality bar definition, the first candidate system, and the linked story. Validation is manual doc inspection plus link/index correctness rather than a model benchmark.

## Tasks

- [ ] Add a `Project Operating System` subsection in `docs/build-map.md` that codifies the quality-bar-then-collapse rule and defines the acceptable-quality gate
- [ ] Record the first tracked candidate in the build map using the Onward genealogy table path after Story 146, including the evidence run and first-pass collapse questions / likely deletion targets
- [ ] Make the mandate discoverable in `docs/stories.md` and this story file so future triage / align passes can treat it as project direction rather than a buried work-log note
- [ ] Decide whether the build map should also surface a reusable "collapse candidate" slot for other systems once they hit the same bar, and document that decision
- [ ] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [ ] Run required checks for touched scope:
  - [ ] Docs/index hygiene: `git diff --check`
  - [ ] Verify story numbering, story index row, and build-map references resolve correctly
  - [ ] If implementation expands beyond docs into executable behavior, run the relevant `make test` / `make lint` / `driver.py` checks then
- [ ] If evals or goldens changed: update `docs/evals/registry.yaml` only if the implementation creates or changes a formal detection signal
- [ ] Search all docs and update any related to what we touched
- [ ] Verify Central Tenets:
  - [ ] T0 — Traceability: the mandate points to real runs / stories instead of vague simplification aspirations
  - [ ] T1 — AI-First: no code-heavy solution is invented for what is fundamentally a project-direction clarification
  - [ ] T2 — Eval Before Build: the mandate is grounded in measured quality evidence, not intuition alone
  - [ ] T3 — Fidelity: the rule preserves "quality first" instead of allowing premature simplification to reintroduce extraction defects
  - [ ] T4 — Modular: simplification targets are named as collapse candidates, not hidden in ad hoc edits
  - [ ] T5 — Inspect Artifacts: the first candidate is backed by manually reviewed artifacts, not just green logs

## Workflow Gates

- [ ] Build complete: implementation finished, required checks run, and summary shared
- [ ] Validation complete or explicitly skipped by user
- [ ] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: `docs/build-map.md` under `Project Operating System`, with the story backlog as the execution surface
- **Data contracts / schemas**: No schema changes expected; this is documentation / roadmap work unless the eventual build opens a new machine-readable collapse-candidate inventory
- **File sizes**: `docs/build-map.md` is 380 lines, `docs/stories.md` is 170 lines, `docs/stories/story-147-quality-bar-then-complexity-collapse.md` is 96 lines; no size risk
- **Decision context**: Reviewed `docs/ideal.md`, `docs/spec.md`, `docs/build-map.md`, ADR-001, Story 145 context, and Story 146 evidence. No separate ADR currently owns this cross-cutting workflow rule; the build map is the right human-readable home unless future implementation reveals a harder-to-reverse governance decision.

## Files to Modify

- `docs/build-map.md` — add the quality-first then collapse mandate and first candidate placement (380 lines)
- `docs/stories.md` — add Story 147 index row (170 lines)
- `docs/stories/story-147-quality-bar-then-complexity-collapse.md` — flesh out the pending story (96 lines)

## Redundancy / Removal Targets

- Implicit "simplify later" guidance that currently lives only in story work logs
- Ad hoc future collapse decisions that would otherwise be invisible to build-map triage

## Notes

This is intentionally more than an Onward follow-up. The build-map mandate should apply to any compromise-bearing system: reach reviewed quality first, then deliberately collapse the workaround stack toward the Ideal's simpler shape instead of treating every successful workaround as permanent architecture.

## Plan

To be written during `/build-story` after the codebase/docs exploration confirms
the exact build-map shape, candidate inventory, and whether the mandate needs a
separate reusable template for future collapse candidates.

## Work Log

20260316-1110 — story created: promoted the user's "quality first, then simplify" direction into a pending cross-cutting story instead of burying it in Story 146 notes; evidence is `docs/spec.md`'s compromise-deletion rule, Story 145's build-map convergence, and Story 146's manually accepted `story146-onward-build-stitch-r5` baseline; next step is to place the mandate explicitly in `docs/build-map.md` under `Project Operating System`
20260316-1123 — mandate placed: added the operating rule to `docs/build-map.md` under `Project Operating System`, named the Onward genealogy scanned-table path as the first tracked collapse candidate, surfaced "Build Story 147" in `Next Actions`, and added the story row to `docs/stories.md`; evidence is the new build-map subsection plus the Story 147 index row; next step is `/build-story 147` when we want to turn the mandate into a concrete collapse roadmap
