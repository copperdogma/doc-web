# Story NNN — TITLE

**Priority**: PRIORITY
**Status**: Draft
**Ideal Refs**: {ideal.md requirements}
**Spec Refs**: {spec.md compromises}
**Depends On**: {story IDs}

## Goal

{One paragraph describing what this story accomplishes and why it matters.}

## Acceptance Criteria

- [ ] {Testable criterion 1}
- [ ] {Testable criterion 2}
- [ ] {Testable criterion 3}

## Out of Scope

- {Explicitly list what this story does NOT do}

## Approach Evaluation

{List candidate approaches — do NOT pre-decide. build-story's eval-first gate selects the winner with evidence.}

- **Simplification baseline**: {Can a single LLM call already do this? Evidence?}
- **AI-only**: {Could an LLM call handle this? Cost per run?}
- **Hybrid**: {Cheap detection + AI judgment? Where's the split?}
- **Pure code**: {Only if strictly orchestration/plumbing with no reasoning.}
- **Eval**: {What test distinguishes the approaches? Does it exist yet?}

## Tasks

- [ ] {Implementation task 1}
- [ ] {Implementation task 2}
- [ ] {Implementation task 3}
- [ ] Run required checks:
  - [ ] `python -m pytest tests/`
  - [ ] `python -m ruff check modules/ tests/`
- [ ] Search all docs and update any related to what we touched
- [ ] Verify Central Tenets:
  - [ ] T0 — Traceability: every output traces to source page, OCR engine, confidence, processing step
  - [ ] T1 — AI-First: didn't write code for a problem AI solves better
  - [ ] T2 — Eval Before Build: measured SOTA before building complex logic
  - [ ] T3 — Fidelity: author's words preserved faithfully, no silent losses
  - [ ] T4 — Modular: new recipe not new code; no hardcoded book assumptions
  - [ ] T5 — Inspect Artifacts: visually verified outputs, not just checked logs

## Files to Modify

- {path/to/file} — {what changes}

## Notes

{Design notes, open questions, references}

## Plan

{Written by build-story Phase 2 — per-task file changes, impact analysis, approval blockers}

## Work Log

{Entries added during implementation — YYYYMMDD-HHMM — action: result, evidence, next step}
