---
title: "Methodology Graph + State Migration"
status: "Done"
priority: "High"
ideal_refs:
  - "Execution Ideal"
  - "Vision-Level Preferences"
spec_refs:
  - "spec:8"
  - "spec:9"
adr_refs: []
depends_on:
  - "148"
category_refs:
  - "spec:8"
  - "spec:9"
compromise_refs:
  - "B1"
  - "B7"
  - "B8"
  - "B9"
input_coverage_refs: []
architecture_domains:
  - "methodology_tooling"
roadmap_tags:
  - "campaign:methodology-graph-state-migration"
legacy_system: ""
---

# Story 187 — Methodology Graph + State Migration

**Priority**: High
**Status**: Done

## Goal

Migrate doc-forge from the older hand-authored methodology surface shape to a
graph+state model tailored to this repo. The migration must preserve the
canonical authored sources, keep `tests/fixtures/formats/_coverage-matrix.json`
as the canonical machine-readable input-coverage source, replace the live
hand-authored `build-map.md` with structured methodology state plus a compiled
graph, generate `docs/stories.md`, migrate the workflow surfaces that still
consume the legacy docs, and certify the result with at least one clean pass
after the last fix.

## Acceptance Criteria

- [x] A repo-specific audit artifact exists at
      `docs/methodology-artifact-audit-and-migration.md` with a no-loss
      responsibility matrix, replacement model, lint contract, migration
      checklist, and certification matrix
- [x] `docs/methodology/state.yaml` exists and owns mutable methodology state
      that no longer lives in the hand-authored build map
- [x] `tests/fixtures/formats/_coverage-matrix.json` is treated as the
      canonical machine-readable input-coverage source rather than copied into a
      second registry
- [x] A deterministic compiler builds `docs/methodology/graph.json` and the
      generated `docs/stories.md` from canonical sources plus methodology state
- [x] Core methodology consumers (`AGENTS.md`, setup/triage/alignment/story
      skills, and related templates/runbooks) use the graph/state model instead
      of the live hand-authored build map
- [x] The architecture-audit lane exists with repo-bounded domains and a
      `/triage-architecture` operating surface
- [x] `docs/build-map.md` is retired as a live authored source, with the final
      hand-authored body preserved under `docs/archive/`
- [x] Certification commands complete cleanly after the last detected issue:
  - [x] graph compile
  - [x] graph drift check
  - [x] skills sync check
  - [x] targeted methodology tests

## Out of Scope

- Rewriting the product ideal, mission, or accepted runtime ADRs
- Bulk-normalizing every historical story file onto frontmatter in this pass
- Changing runtime pipeline behavior, schemas, or document-conversion quality
- Deleting archived legacy surfaces

## Approach Evaluation

- **Simplification baseline**: stronger instructions alone are not enough here.
  The repo already has a machine-readable coverage matrix yet still relies on a
  hand-authored build map and story index for live planning truth, which has
  already drifted.
- **AI-only**: keep the current docs and rely on agents to infer joins from
  prose. Rejected; that preserves the current drift failure mode.
- **Hybrid**: canonical authored docs + structured state +
  coverage-matrix-as-canonical-state + compiled graph + generated views + hard
  linting. This is the target.
- **Pure code / registry-first**: rejected unless it duplicates less truth than
  it adds. A new hand-maintained master registry would be worse than the
  current problem.
- **Repo constraints / prior decisions**: Story 148 already moved doc-forge to
  the ADR-021-shaped category/spec model. The next honest step is changing the
  physical artifact model without losing those responsibilities. No current ADR
  settles the graph+state migration itself, so this story carries the local
  migration contract directly.
- **Existing patterns to reuse**: Storybook's migration runbook, Storybook's
  audit-artifact section structure, the local machine-readable coverage matrix,
  and the repo's existing skill-sync/check pattern.
- **Eval**: the migration passes when the compiler/check loop is clean, the
  generated index is stable, and no active methodology surface still teaches the
  retired live build-map model.

## Tasks

- [x] Create the repo-specific migration story + audit artifact first
- [x] Add `docs/methodology/state.yaml` seeded from the current mutable
      methodology state
- [x] Implement the methodology compiler/check command and generate
      `docs/methodology/graph.json`
- [x] Generate `docs/stories.md` from graph/state inputs
- [x] Update story and ADR templates for strict graph-friendly metadata
- [x] Migrate the core methodology skills, runbooks, checklist, and `AGENTS.md`
      to the new graph/state model
- [x] Add the architecture-audit lane and `/triage-architecture`
- [x] Archive the final hand-authored `build-map.md` and retire the live path
- [x] Run certification until there is a completely clean pass after the last
      fix
- [x] Search related docs and update any that still teach the retired live
      build-map flow
- [x] Run required checks for touched scope:
  - [x] `make methodology-compile`
  - [x] `make methodology-check`
  - [x] `make skills-check`
  - [x] `python -m pytest tests/test_methodology_graph.py -q`
  - [x] `python -m ruff check scripts/methodology_graph.py tests/test_methodology_graph.py`
  - [x] `python -m pytest tests/`
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: the compiled graph and generated index preserve explicit links back to canonical sources, state, ADRs, evals, and archived legacy surfaces
  - [x] T1 — AI-First: the migration improves methodology orchestration and planning truth without introducing extra deterministic process layers to fake understanding
  - [x] T2 — Eval Before Build: the repo-specific audit and certification loop measured current drift and consumer behavior before retiring live legacy surfaces
  - [x] T3 — Fidelity: the migration preserves authored canon and historical planning bodies instead of silently deleting or flattening them
  - [x] T4 — Modular: mutable methodology state, compiled graph, generated views, and workflow consumers now have explicit bounded ownership instead of one overloaded markdown dashboard
  - [x] T5 — Inspect Artifacts: the generated graph, generated story index, archived legacy surfaces, and lint outputs were manually opened and re-checked during certification

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning area**: repo methodology tooling and AI workflow surfaces
- **Category ownership**: `spec:8` (tooling) and `spec:9` (planning
  infrastructure)
- **Substrate evidence**: `docs/ideal.md`, `docs/spec.md`, `docs/build-map.md`,
  `docs/stories.md`, `docs/evals/registry.yaml`, and
  `tests/fixtures/formats/_coverage-matrix.json` already exist; the missing
  substrate is the compiled graph/state layer plus migrated consumers
- **Data contracts / schemas**: new methodology-state and graph contracts live
  under `docs/methodology/`; no product-runtime schema changes are expected
- **Decision context**: read the local methodology spine plus the Storybook
  migration runbook/audit/story templates. No existing local ADR resolves this
  migration shape.

## Files to Modify

- `docs/methodology-artifact-audit-and-migration.md` — audit artifact
- `docs/methodology/state.yaml` — structured methodology state
- `docs/methodology/graph.json` — compiled methodology graph
- `scripts/methodology_graph.py` — compiler/check command
- `docs/stories.md` — generated story index
- `docs/build-map.md` — archival redirect stub
- `docs/archive/build-map-hand-authored-2026-04-04.md` — preserved legacy body
- `docs/archive/stories-index-hand-authored-2026-04-04.md` — preserved legacy index
- `AGENTS.md` and methodology skills/runbooks/templates — consumer migration

## Redundancy / Removal Targets

- Live hand-authored `docs/build-map.md` planning truth
- Manual `docs/stories.md` editing
- Skill language that still treats the build map as the active central source

## Notes

- Use Storybook's migration artifacts as templates only.
- Keep the migration repo-specific: doc-forge already has a canonical
  coverage-matrix JSON, so the replacement model should use it instead of
  cloning Storybook's exact state schema.

## Plan

1. Create the audit artifact and long-running migration story.
2. Add state + compiler + generated story index without cutting over consumers
   prematurely.
3. Migrate active methodology consumers and add linting/architecture-audit
   support.
4. Retire the live build-map path, then re-run the full certification loop
   until a clean pass exists after the last issue.

## Work Log

20260404-archive — preserved the final hand-authored legacy planning surfaces
at `docs/archive/build-map-hand-authored-2026-04-04.md` and
`docs/archive/stories-index-hand-authored-2026-04-04.md` before replacing
anything, so the migration can re-home responsibilities without deleting
history. Evidence: clean copies created in `docs/archive/`. Next: land the
audit artifact, state file, and compiler foundation.
20260404-graph-foundation — added `docs/methodology/state.yaml`,
`scripts/methodology_graph.py`, `tests/test_methodology_graph.py`, and the first
compiled `docs/methodology/graph.json`. The compiler now reads the authored
canon plus the existing coverage matrix and generates `docs/stories.md` instead
of relying on a hand-maintained story index. Evidence: `make
methodology-compile`, `python -m pytest tests/test_methodology_graph.py -q`.
Next: migrate the consumer docs/skills and retire the live build-map path.
20260404-consumer-cutover — rewrote `AGENTS.md`, the methodology reference,
setup runbook/checklist, story/ADR templates, and the main planning skills to
use `docs/methodology/state.yaml`, `docs/methodology/graph.json`, and
`tests/fixtures/formats/_coverage-matrix.json` as the live planning surfaces.
Added the bounded `/triage-architecture` lane plus its runbook/skill. Evidence:
consumer docs under `.agents/skills/`, `docs/runbooks/`, and `AGENTS.md`; skill
sync via `./scripts/sync-agent-skills.sh` and `make skills-check`. Next:
archive the live build map and run the certification loop.
20260404-certification — replaced `docs/build-map.md` with an archival stub,
frontmatter-migrated ADR-001 through ADR-003, reran the graph compiler/check,
and verified the final migration with fresh checks: `make methodology-compile`,
`make methodology-check`, `make skills-check`, `python -m ruff check
scripts/methodology_graph.py tests/test_methodology_graph.py`, `make lint`,
`python -m pytest tests/test_methodology_graph.py -q`, and `python -m pytest
tests/` (`445 passed, 4 warnings`). Remaining non-blocking graph warnings are
explicit legacy debt rather than migration failures: 178 historical story files
still use legacy metadata, 124 of those still lack derived category refs, 21
have non-standard historical statuses, Story 063 still names missing legacy
dependency `055`, and Stories 145/148 still cite external Storybook ADR-019 /
ADR-021 with no local ADR file. Next: `/mark-story-done` if you want the
migration story itself closed formally.
20260404-phase-sweep — re-ran the migration phase certification against the
runbook instead of trusting the earlier summary. Found and fixed two contract
gaps: the methodology compiler's active-surface lint scope did not yet cover
every consumer hotspot named in the audit artifact, and the audit artifact's
phase checklist/log had drifted from the actual phase structure. Evidence:
`scripts/methodology_graph.py`, `docs/methodology-artifact-audit-and-migration.md`,
`make methodology-check`, and `make skills-check`. Next: rerun the fresh
compile/test sweep, then `/mark-story-done` if you want formal close-out.
20260404-closeout — `/mark-story-done` validation completed on the current tip.
Fresh project checks passed: `python -m pytest tests/` (`445 passed, 4 warnings
in 183.96s`) and `python -m ruff check modules/ tests/` (`All checks passed!`).
Fresh agent-tooling validation passed: `make skills-check`. I re-read the
migration outputs and contracts in `docs/methodology-artifact-audit-and-migration.md`,
`docs/methodology/state.yaml`, `docs/build-map.md`, `docs/stories.md`, and
`scripts/methodology_graph.py`; the only remaining graph warnings are the
documented non-blocking historical debt items already called out in the story
and audit artifact. Result: acceptance criteria, tasks, workflow gates, and
central-tenet checks are all complete, and the story is now formally closed.
Next: `/check-in-diff`.
