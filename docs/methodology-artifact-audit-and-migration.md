# Methodology Artifact Audit and Migration Record

> Story 187 audit artifact.
> Purpose: capture what the pre-migration methodology surfaces owned, define the
> graph+state replacement model that landed, and leave the certification matrix
> that drove the migration safely.

## Executive Summary

Doc-forge already had a strong authored methodology spine, but the historical
artifact model mixed canonical truth with mutable operational state:

- historical `docs/build-map.md` carried category taxonomy, substrate state, compromise
  phase, input-coverage reporting, gap prioritization, and skill-routing
  assumptions
- generated `docs/stories.md` mixed a generated-index role with mutable sequencing prose
  and a status registry
- the machine-readable coverage matrix already exists, but the live planning
  workflow at the time still taught humans and agents to read the historical
  historical markdown build map first
- skills, runbooks, and close-out guidance still depend on those drifting
  markdown surfaces as if they were canonical

The replacement model for doc-forge should be repo-specific rather than a blind
copy of Storybook:

1. keep the authored canon where it already belongs
2. add one small structured state file for mutable methodology state
3. treat `tests/fixtures/formats/_coverage-matrix.json` as the canonical
   machine-readable input-coverage source instead of duplicating it
4. compile a methodology graph from canonical sources plus state
5. generate the generated `docs/stories.md` view
6. archive the hand-authored build map and replace its path with a historical
   stub
7. add hard linting so old live surfaces cannot quietly drift back in
8. add an architecture-audit lane so structural cleanup gets a bounded,
   inspectable operating surface

## Non-Negotiable Canon

These remain canonical and hand-authored:

- `docs/ideal.md`
  - product ideal, execution ideal, mission, and vision-level preferences
- `docs/spec.md`
  - compromise definitions, category structure, and design principles
- `docs/decisions/**/adr.md`
  - hard-to-reverse decision rationale and integration notes
- `docs/stories/story-*.md`
  - canonical execution records, work logs, and acceptance criteria
- `docs/evals/registry.yaml`
  - canonical measured evidence and retry triggers
- `tests/fixtures/formats/_coverage-matrix.json`
  - canonical machine-readable input-coverage inventory

The migration must not create a parallel registry that duplicates those truths.

## Current Responsibility Matrix

| Artifact | Type Today | Responsibilities It Actually Owns | Migration Outcome |
|---|---|---|---|
| `docs/ideal.md` | Canonical authored source | Product ideal, execution ideal, mission, and vision-level preferences | Keep canonical. Parse requirements/preferences into the graph only. |
| `docs/methodology-ideal-spec-compromise.md` | Explanatory reference | Explained the methodology contract and taught the historical build-map-centered physical model | Keep, but rewrite around state + coverage matrix + compiled graph. |
| `docs/spec.md` | Canonical authored source | Category structure, constraint IDs, compromise semantics, and execution-compromise taxonomy | Keep canonical. Parse IDs/compromises into the graph. |
| historical `docs/build-map.md` | Hand-authored dashboard + mutable operational state | Category substrate status, phase governance, input-coverage reporting, gap prioritization, graduation notes, and workflow routing assumptions | Retire as a live authored surface. Archive the last hand-authored body and replace the path with a historical stub. Re-home mutable state into `docs/methodology/state.yaml`; keep input coverage canonical in the coverage matrix. |
| generated `docs/stories.md` | Manual index + sequencing prose | Story status registry, discovery/indexing, recommended-order narrative | Replace with a generated index. Move sequencing prose into structured methodology state. |
| Story files | Canonical authored source | Goal, ACs, work log, dependencies, decision links, validation evidence | Keep canonical. New stories should carry strict frontmatter; legacy stories remain readable with warnings until backfilled. |
| Story template + `/create-story` | Workflow substrate | Defines story metadata shape and previously assumed manual generated-`docs/stories.md` editing | Update to emit graph-friendly frontmatter and regenerate the index instead of editing it manually. |
| `docs/evals/registry.yaml` | Canonical authored source | Eval IDs, scores, compromise links, retry conditions | Keep canonical. Parse into the graph and lint for missing links. |
| `tests/fixtures/formats/_coverage-matrix.json` | Canonical machine-readable state | Input families, statuses, fixtures, scores, and known gaps | Keep canonical. Read directly from the compiler instead of restating its rows inside methodology state. |
| `docs/setup-checklist.md` | Generated working checklist | Current methodology-package working copy | Keep, but regenerate around the graph+state package. |
| `docs/runbooks/setup-methodology.md` + `/setup-methodology` | Bootstrap/runbook surface | Teaches the current package shape and public entrypoint | Keep, but rewrite around state/graph/coverage-matrix compilation and historical archived-build-map handling. |
| `/triage`, `/align`, `/build-story`, `/validate`, `/mark-story-done`, `/create-story`, `/triage-*` | Workflow surfaces | Consumed historical `build-map.md` and generated `docs/stories.md` as live planning truth | Migrate to `docs/methodology/state.yaml`, `docs/methodology/graph.json`, and the coverage matrix. |
| ADR tooling docs/templates | Workflow substrate | Taught cross-linking and post-decision propagation, still naming the historical build map | Keep, but point them at the compiled graph/state model. |
| `AGENTS.md` | Repo-wide operating contract | Taught the methodology hierarchy and planning workflow around the historical hand-authored build map | Keep canonical, but rewrite the operating rule around graph/state instead. |

## Consumer Hotspots

These are the main migration-risk surfaces because they currently assume the
legacy markdown planning surfaces are live:

### Core methodology skills

- `.agents/skills/setup-methodology/SKILL.md`
- `.agents/skills/align/SKILL.md`
- `.agents/skills/triage/SKILL.md`
- `.agents/skills/triage-stories/SKILL.md`
- `.agents/skills/triage-evals/SKILL.md`
- `.agents/skills/triage-inbox/SKILL.md`
- `.agents/skills/build-story/SKILL.md`
- `.agents/skills/create-story/SKILL.md`
- `.agents/skills/mark-story-done/SKILL.md`
- `.agents/skills/validate/SKILL.md`

### Templates and setup surfaces

- `.agents/skills/create-story/templates/story.md`
- `.agents/skills/create-adr/templates/adr.md`
- `.agents/skills/setup-methodology/templates/setup-checklist.md`
- `docs/runbooks/setup-methodology.md`
- `docs/setup-checklist.md`
- `AGENTS.md`

### Additional consumer paths worth migrating in the same sweep

- `.agents/skills/format-gap-analysis/SKILL.md`
- `.agents/skills/codebase-improvement-scout/SKILL.md`
- `.agents/skills/finish-and-push/SKILL.md`
- `docs/decisions/README.md`
- `docs/runbooks/adr-creation.md`

## Key Findings

### 1. Historical `docs/build-map.md` was overloaded

It is not just a dashboard. Today it owns:

- category taxonomy
- category substrate truth
- compromise phase truth
- human-readable input-coverage rendering
- prioritized gap narrative
- graduation notes
- planning/triage routing language consumed by skills

Deleting it without re-homing each of those roles would definitely lose
responsibility.

### 2. Generated `docs/stories.md` was not honest as a hand-maintained source

The current file mixes:

- index/discovery
- story status registry
- sequencing narrative
- roadmap emphasis

Index data should be generated. Mutable sequencing bias should live in state.

### 3. Doc-forge already has one machine-readable planning surface

`tests/fixtures/formats/_coverage-matrix.json` is already the canonical
machine-readable input-coverage inventory. The correct migration is to elevate
it into the methodology graph rather than copying its rows into another
registry.

### 4. Legacy story metadata is inconsistent

Only a minority of story files carry modern `Spec Refs`; most older stories are
still valuable historical evidence but are not clean enough to drive strict
category grouping without fallback or warnings. The migration should preserve
them, keep warnings visible, and move new stories onto strict metadata rather
than pretending the backlog is already normalized.

### 5. Architecture cleanup currently has no durable operating lane

Doc-forge has strong product/eval/story discipline, but no durable place to
track structural simplification pressure. That should become explicit
methodology state plus a `/triage-architecture` lane.

## Replacement Model

## 1. Canonical Authored Sources

Keep these as the only hand-authored decision-bearing sources:

- `docs/ideal.md`
- `docs/spec.md`
- `docs/decisions/**/adr.md`
- `docs/stories/story-*.md`
- `docs/evals/registry.yaml`
- `tests/fixtures/formats/_coverage-matrix.json`

## 2. Structured Operational State

Add one small state file:

- `docs/methodology/state.yaml`

It should own only mutable methodology state that the canonical sources do not
already own:

- category substrate status
- compromise phase state
- roadmap focus and sequencing bias
- generated-story-index prose sections
- architecture-audit cadence and memory
- optional legacy/category overrides for stories that have not been fully
  backfilled yet
- archive pointers for retired live surfaces

It should explicitly not duplicate:

- historical build-map prose
- story work logs
- spec prose
- ADR rationale
- eval history
- coverage-matrix fixture rows or metrics

## 3. Coverage Matrix as Canonical Cross-Cutting State

Use the existing file directly:

- `tests/fixtures/formats/_coverage-matrix.json`

This repo already owns input-coverage state in a machine-readable surface. The
compiler should read it directly and expose it in the graph rather than
re-encoding it in `state.yaml`.

## 4. Compiled Methodology Graph

Add a compiled artifact:

- `docs/methodology/graph.json`

Compiler inputs:

- `docs/ideal.md`
- `docs/spec.md`
- `docs/methodology/state.yaml`
- `docs/decisions/**/adr.md`
- `docs/stories/story-*.md`
- `docs/evals/registry.yaml`
- `tests/fixtures/formats/_coverage-matrix.json`

Compiler outputs should include:

- category -> stories / ADRs / evals / state
- compromise -> category / phase / evals
- story -> spec refs / decision refs / dependencies / category refs / metadata health
- coverage row -> format family / scores / linked stories
- architecture domain -> cadence / recent stories / open findings
- validation warnings for missing refs, stale live-surface language, and
  legacy metadata

The graph is compiled only. It is never hand-edited.

## 5. Generated Views

Required generated view:

- generated `docs/stories.md`

Optional/historical view:

- historical `docs/build-map.md` becomes a short archived redirect, not a live source

## 6. Architecture-Audit Lane

Adopt the lane in this repo with bounded domains:

- `methodology_tooling`
- `intake_and_routing`
- `ocr_and_extraction`
- `document_structure_and_consistency`
- `doc_web_runtime`

State should remember:

- last audit date
- recent story refs
- open findings
- stories since audit
- manual priority
- short notes

`/triage` should route to `/triage-architecture` when a domain is due or
carrying open findings.

## Lint Contract

### Blocking lints

- invalid or missing `spec:*` refs
- state category/compromise keys that do not map to spec
- stories, ADRs, or coverage rows that reference missing linked artifacts
- stories still on legacy metadata only
- ADRs still on legacy metadata only
- generated `docs/stories.md` drift
- generated `docs/methodology/graph.json` drift
- live skill/runbook/AGENTS surfaces that still instruct agents to use
  historical `docs/build-map.md` as an active source
- active surfaces that still describe generated `docs/stories.md` as hand-maintained

### Warning lints

- stories with non-standard status values
- architecture domains that are overdue or carry open findings

### Ideal-centric lints

- story or ADR references to removed taxonomy with no legacy framing
- setup docs that advertise multiple competing methodology entrypoints
- planning guidance that duplicates canonical coverage-matrix truth instead of
  referencing it

## Migration Checklist

### Phase 0 — Audit and contract

- [x] Create the migration story
- [x] Create this audit artifact
- [x] Archive the final hand-authored `build-map.md` and `stories.md`

### Phase 1 — State and compiler foundation

- [x] Add `docs/methodology/state.yaml`
- [x] Add the methodology compiler/check command
- [x] Generate `docs/methodology/graph.json`

### Phase 2 — Generated index and templates

- [x] Generate generated `docs/stories.md`
- [x] Update story and ADR templates to emit strict metadata
- [x] Keep legacy-story support explicit via warnings rather than silent failure

### Phase 3 — Consumer migration

- [x] Move skills, AGENTS, runbooks, and checklist language onto state + graph + coverage matrix
- [x] Add `/triage-architecture`

### Phase 4 — Hard linting and active-surface cleanup

- [x] Block active-surface references to the retired live build-map model
- [x] Keep archive/historical references explicit and allowed

### Phase 5 — Legacy live-surface retirement

- [x] Replace `docs/build-map.md` with an archival stub
- [x] Keep the archived hand-authored body under `docs/archive/`
- [x] Re-run certification until a fully clean pass exists after the last fix

## Rollback / Safety Rules

- Do not delete the archived hand-authored build map or story index.
- Do not duplicate the coverage matrix inside `state.yaml`.
- Do not require bulk backfill of 178 historical story files before the graph
  can compile; warn instead.
- Do not silently re-activate historical `docs/build-map.md` while claiming the
  migration is complete.

## Certification Matrix

| Phase | Contract | Positive Proof | Negative Proof | If Changed, Re-run |
|---|---|---|---|---|
| 0. Audit | Story + audit artifact exist and match repo reality | Story 187 + this file present | No ownerless responsibility remains in the matrix | All phases |
| 1. State | `state.yaml` exists and maps current mutable state | Compiler reads valid state | No duplicate coverage truth added to state | Phases 1-5 |
| 2. Graph | `graph.json` compiles cleanly | `make methodology-compile` writes graph | No validation errors | Phases 2-5 |
| 3. Views | generated `docs/stories.md` is current | Compiler writes the index | `make methodology-check` reports no drift | Phases 3-5 |
| 4. Consumers | Skills/runbooks/AGENTS use graph/state/coverage matrix | Target files updated, skill sync passes | No active-surface build-map language remains without legacy framing | Phases 4-5 |
| 5. Retirement | build-map path is archival only | `docs/build-map.md` becomes a redirect stub | No active consumer still depends on it | Phase 5 + end-to-end sweep |

## Certification Log

- 20260404-archive — archived the final hand-authored legacy surfaces to
  `docs/archive/build-map-hand-authored-2026-04-04.md` and
  `docs/archive/stories-index-hand-authored-2026-04-04.md` before replacing
  anything.
- 20260404-phase1 — added `docs/methodology/state.yaml` and seeded the initial
  category, compromise, roadmap, archive-pointer, and architecture-audit state
  without duplicating the coverage-matrix rows inside `state.yaml`.
- 20260404-phase2 — added `scripts/methodology_graph.py` and
  `tests/test_methodology_graph.py`, generated the first
  `docs/methodology/graph.json` and generated `docs/stories.md`, and updated the story
  and ADR templates so new metadata is graph-friendly while legacy stories stay
  explicit warning cases instead of silent failures.
- 20260404-phase3 — migrated AGENTS, setup docs, planning skills, and related
  templates/runbooks onto `docs/methodology/state.yaml`,
  `docs/methodology/graph.json`, and the coverage matrix, and added the
  `/triage-architecture` lane plus `docs/runbooks/triage-architecture.md`.
- 20260404-phase4 — enforced hard active-surface linting in the methodology
  compiler and widened the checked surface set to cover the extra consumer
  hotspots identified in this audit, including `finish-and-push`,
  `codebase-improvement-scout`, the ADR README, and the scout runbook.
- 20260404-phase5 — retired the live `docs/build-map.md` body behind an
  archival stub and preserved the final hand-authored dashboard at
  `docs/archive/build-map-hand-authored-2026-04-04.md`.
- 20260404-clean-pass — fresh verification completed after the last detected
  issue:
  - `make methodology-compile`
  - `make methodology-check`
  - `make skills-check`
  - `python -m ruff check scripts/methodology_graph.py tests/test_methodology_graph.py`
  - `make lint`
  - `python -m pytest tests/test_methodology_graph.py -q`
  - `python -m pytest tests/`
  Remaining graph warnings are explicit legacy debt rather than migration
  failures: historical story metadata/status backfill, Story 063's missing
  legacy dependency ref, and Storybook ADR-019/ADR-021 references in Stories
  145/148.
