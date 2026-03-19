# Story 153 — Extract `doc-web` Bundle Emitter

**Priority**: High
**Status**: Pending
**Ideal Refs**: Requirement #5 (Structure), Requirement #7 (Export), Dossier-ready output, Graduate, don't accumulate
**Spec Refs**: spec:6 (Validation, Provenance & Export), spec:7 (Graduation & Dossier Handoff)
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/notes/standalone-dossier-intake-runtime-plan.md`, Story 152
**Depends On**: Story 152

## Goal

Extract the first real `doc-web` code seam from codex-forge by splitting the generic bundle-emission path out of `build_chapter_html_v1`. The current builder already proves the output shape, but it still mixes structural website emission with embedded CSS, image publishing details, and document-specific output shaping. This story should isolate the generic emitter so that later extraction into `doc-web` is a clean move rather than a blind copy of a large mixed-responsibility module.

## Acceptance Criteria

- [ ] A generic bundle-emission seam is extracted from the current `build_chapter_html_v1` path, with responsibilities clearly separated between structural output and optional presentation wrapper behavior.
- [ ] The accepted `doc-web` contract from Story 152 is implemented or enforced at the seam so the emitter is no longer relying on undocumented manifest/output behavior.
- [ ] A real `driver.py` run proves the refactored codex-forge path still emits healthy Onward structural website artifacts in `output/runs/`, and those artifacts are manually inspected.
- [ ] The story names what should move directly into the future `doc-web` repo versus what should remain temporarily in codex-forge.

## Out of Scope

- Building the full standalone `doc-web` repo
- Dossier-side integration code
- Themed website styling or publish UX
- Reworking unrelated OCR or Onward consistency logic unless the emitter seam exposes a contract bug

## Approach Evaluation

- **Simplification baseline**: Check whether the current builder can already be split by extracting pure helper functions and wrapper boundaries, without moving files across repos yet. If so, prefer seam extraction over an immediate repo bootstrap.
- **AI-only**: An LLM can suggest refactor boundaries, but the actual seam must be proven against the real recipe outputs and schema stamping rules.
- **Hybrid**: Use AI to propose ownership boundaries inside `build_chapter_html_v1`, then verify them against the real emitted artifacts and the accepted contract. This is the leading candidate.
- **Pure code**: Copy the current builder wholesale into `doc-web` and sort it out later. Fastest mechanically, but directly contradicts the accepted seam-first extraction strategy.
- **Repo constraints / prior decisions**: ADR-002 explicitly rejected a big-bang repo move. Story 152 should freeze the contract first. `build_chapter_html_v1` is 1345 lines and already mixes structural and wrapper responsibilities.
- **Existing patterns to reuse**: current HTML builder helpers, current image/manifest publishing flow, and the contract schema from Story 152.
- **Eval**: The deciding evidence is a real Onward build after the refactor, plus manual comparison showing no semantic regression in the structural website artifacts.

## Tasks

- [ ] Identify and document the responsibility split inside `build_chapter_html_v1`:
  - generic bundle emission
  - nav/read-order wiring
  - asset publishing
  - optional wrapper/presentation behavior
- [ ] Refactor the current builder so the generic emitter seam is isolated behind stable inputs and outputs
- [ ] Align the refactored seam with the Story 152 contract schemas
- [ ] Prove the seam with a real `driver.py` run and manual artifact inspection
- [ ] Record what code is now ready to move into `doc-web` directly versus what still requires refactor
- [ ] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [ ] Run required checks for touched scope:
  - [ ] Default Python checks: `make test`
  - [ ] Default Python lint: `make lint`
  - [ ] Clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect the emitted structural website bundle
  - [ ] If agent tooling changed: `make skills-check`
- [ ] If evals or goldens changed materially: run `/improve-eval` and update `docs/evals/registry.yaml`
- [ ] Search all docs and update any related to what we touched
- [ ] Verify Central Tenets:
  - [ ] T0 — Traceability: refactor preserves provenance fields and does not make the final contract more opaque
  - [ ] T1 — AI-First: do not replace AI extraction with deterministic overfit while isolating the emitter seam
  - [ ] T2 — Eval Before Build: compare refactored outputs against the known good structural website artifacts
  - [ ] T3 — Fidelity: no semantic regression in the emitted website bundle
  - [ ] T4 — Modular: seam extraction reduces coupling instead of moving a monolith unchanged
  - [ ] T5 — Inspect Artifacts: manually inspect the rebuilt HTML and manifest outputs

## Workflow Gates

- [ ] Build complete: implementation finished, required checks run, and summary shared
- [ ] Validation complete or explicitly skipped by user
- [ ] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: `modules/build/build_chapter_html_v1` is the primary seam owner, with `schemas.py` and current recipe wiring as contract surfaces.
- **Data contracts / schemas**: Any new bundle/provenance fields must be added to `schemas.py` before the stamped artifacts can preserve them.
- **File sizes**: `modules/build/build_chapter_html_v1/main.py` is 1345 lines and `schemas.py` is 964 lines. Keep edits surgical and resist expanding the builder while trying to extract it.
- **Decision context**: ADR-002 settled seam-first extraction. Story 152 should define the contract before this story starts implementation.

## Files to Modify

- /Users/cam/.codex/worktrees/cdb6/codex-forge/modules/build/build_chapter_html_v1/main.py — extract the generic bundle-emission seam from the mixed builder (1345 lines)
- /Users/cam/.codex/worktrees/cdb6/codex-forge/schemas.py — preserve any newly formalized bundle/provenance fields during stamping (964 lines)
- /Users/cam/.codex/worktrees/cdb6/codex-forge/configs/recipes/recipe-onward-images-html-mvp.yaml — update wiring only if the seam extraction changes stage parameters or outputs (192 lines)
- /Users/cam/.codex/worktrees/cdb6/codex-forge/docs/stories/story-153-extract-doc-web-bundle-emitter.md — keep the story current as the seam lands

## Redundancy / Removal Targets

- Any mixed helper inside `build_chapter_html_v1` that only exists because structural and presentation responsibilities are coupled
- Any doc text claiming the current builder is ready to copy wholesale into `doc-web`

## Notes

- The goal is not "extract a pretty HTML generator." The goal is "extract the structural website emitter seam."
- Keep the codex-forge path working while the seam is isolated; `doc-web` repo creation can happen afterward.

## Plan

Pending — `/build-story` should map the current builder into pure emitter core, wrapper shell, and recipe-specific glue before code changes begin.

## Work Log

20260318-2337 — story created: captured the first real code-move seam implied by ADR-002. Story 152 should freeze the contract first, then this story can isolate the emitter without guessing at field names or output responsibilities.
