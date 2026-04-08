---
title: "Methodology Hardening Follow-up"
status: "Done"
priority: "High"
ideal_refs:
  - "The Execution Ideal"
  - "Transparency over magic."
spec_refs:
  - "spec:8"
  - "spec:9"
adr_refs: []
depends_on:
  - "188"
  - "195"
category_refs:
  - "spec:8"
  - "spec:9"
compromise_refs:
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

# Story 199 — Methodology Hardening Follow-up

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/methodology-artifact-audit-and-migration.md`, `docs/runbooks/setup-methodology.md`, `docs/runbooks/migrate-problem-first-triage-and-story-workflow.md`, `docs/scout/scout-012-dossier-methodology-hardening-audit.md`, Stories `187`, `188`, and `195`, and `None found after search in docs/decisions/ for a repo-local ADR that already resolves this post-migration hardening pass`
**Depends On**: Story `188`, Story `195`

## Goal

Finish the post-migration hardening that the first graph/state pass and the
legacy metadata backfill did not complete. The methodology package should have
one honest current model: explicit eval lineage in `docs/evals/registry.yaml`,
a compiler boundary that covers the real live methodology surfaces, and no
current-tense build-map-era guidance left in the active docs, wrappers,
decision workflow, or scout-history surfaces that live workflows still re-read.

## Acceptance Criteria

- [x] The methodology compiler and regression tests cover the real live
      methodology package rather than only the initial migration subset:
  - [x] `scripts/methodology_graph.py` audits the newly adopted live surface
        families needed by this story, including canonical docs and
        generated-wrapper/support surfaces the active workflows actually use
  - [x] targeted regressions land in `tests/test_methodology_graph.py` for the
        new stale-guidance / boundary rules
- [x] Eval lineage becomes explicit canonical metadata instead of heuristic
      prose scraping:
  - [x] `docs/evals/registry.yaml` carries explicit lineage fields on eval
        records
  - [x] `scripts/methodology_graph.py` consumes those explicit fields directly
  - [x] `docs/evals/README.md` and `docs/evals/attempt-template.md` teach the
        explicit registry contract rather than story/spec/build-map prose links
- [x] Live methodology docs, runbooks, wrappers, and support files stop
      teaching the retired build-map/manual-index model:
  - [x] canonical/docs workflow surfaces use `docs/methodology/state.yaml`,
        `docs/methodology/graph.json`, generated `docs/stories.md`, and the
        coverage matrix as the current planning model
  - [x] the audit artifact and Story `187` preserve historical migration
        evidence without overstating stale current state
  - [x] the ADR/scout/helper surfaces named in Scout 012 are either rewritten
        into explicit historical framing or updated to current truth
- [x] Fresh methodology verification passes for the touched scope:
  - [x] `make methodology-compile`
  - [x] `make methodology-check`
  - [x] `python -m pytest tests/test_methodology_graph.py -q`
  - [x] `python -m ruff check scripts/methodology_graph.py tests/test_methodology_graph.py`
  - [x] `make skills-check`
  - [x] `make lint`
  - [x] `make test`

## Out of Scope

- Reopening the graph/state architecture from Story `187`
- Changing runtime pipeline behavior, bundle schemas, or format-coverage truth
- Rewriting every historical scout document in the repo beyond the specific
  stale-current-state surfaces that live workflows still re-read
- Introducing a new local ADR unless implementation reveals a genuinely new
  hard-to-reverse methodology contract

## Approach Evaluation

- **Simplification baseline**: this is a repo-truth hardening pass, not a user
  feature. A one-off AI rewrite is not enough because the outcome must be
  embodied in deterministic compiler checks, explicit eval metadata, and stable
  active docs.
- **AI-only**: insufficient as the full solution. An LLM can help identify
  stale wording, but relying on repeated manual sweeps would preserve the exact
  class of drift the story is trying to remove.
- **Hybrid**: likely winner. Use the audit findings plus targeted repo search
  to identify the minimal surfaces that matter, then land deterministic
  compiler/test changes and bounded doc rewrites.
- **Pure code**: insufficient on its own. Compiler changes without doc/wrapper
  cleanup would leave the active methodology surface still teaching the wrong
  model.
- **Repo constraints / prior decisions**: Stories `187` and `188` already
  migrated the artifact model and removed legacy metadata warnings; Story `195`
  already cleaned stale active-story residue. The next honest step is
  hardening the long-tail methodology package around those surfaces rather than
  reopening the migration design itself.
- **Existing patterns to reuse**: `scripts/methodology_graph.py`,
  `tests/test_methodology_graph.py`, the explicit frontmatter contracts from
  Story `188`, and the focused audit bundle recorded in
  `docs/scout/scout-012-dossier-methodology-hardening-audit.md`.
- **Eval**: the proof surface is the methodology compiler/test suite plus
  targeted repo searches for stale guidance. Success means the compiler now
  encodes the new rules and the touched docs pass against those rules.

## Tasks

- [x] Expand `scripts/methodology_graph.py` so the stale-guidance audit covers
      the real live methodology surface set and add targeted regressions in
      `tests/test_methodology_graph.py`
- [x] Move eval lineage to explicit canonical fields in
      `docs/evals/registry.yaml`, teach that contract in the eval docs, and
      update the compiler to consume the explicit fields directly
- [x] Rewrite the stale current-tense build-map/manual-index guidance called
      out by Scout 012 across the live methodology docs, runbooks, wrappers,
      helper scripts, audit artifact, Story `187`, ADR `003`, and the named
      scout-history surfaces
- [x] N/A by design: this story does not change documented format coverage or
      graduation reality, so `tests/fixtures/formats/_coverage-matrix.json`
      should stay untouched
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] `make methodology-compile`
  - [x] `make methodology-check`
  - [x] `python -m pytest tests/test_methodology_graph.py -q`
  - [x] `python -m ruff check scripts/methodology_graph.py tests/test_methodology_graph.py`
  - [x] `make skills-check`
  - [x] `make lint`
  - [x] `make test`
- [x] Evals/goldens do not change, but the eval registry contract does, so
      update `docs/evals/registry.yaml` without running `/improve-eval`
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: methodology lineage and live planning guidance stay
        explicit and inspectable
  - [x] T1 — AI-First: use AI for bounded audit judgment, not as a substitute
        for explicit compiler contracts
  - [x] T2 — Eval Before Build: use the current audit findings and targeted
        searches as the before-state baseline before changing guardrails
  - [x] T3 — Fidelity: preserve historical migration/scout evidence while
        clearly separating it from current truth
  - [x] T4 — Modular: keep explicit ownership between canon, state, graph,
        generated views, and wrappers rather than adding another truth layer
  - [x] T5 — Inspect Artifacts: manually inspect the touched docs plus rebuilt
        `docs/methodology/graph.json` and `docs/stories.md`

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

- **Owning module / area**: methodology tooling under
  `scripts/methodology_graph.py`, `tests/test_methodology_graph.py`, the eval
  registry/docs, and the cross-cutting methodology docs/skills/runbooks they
  govern.
- **Methodology reality**: this belongs to `spec:8` and `spec:9`. Their
  substrates already exist in `docs/methodology/state.yaml`; the relevant
  execution compromises `B7`, `B8`, and `B9` are all active planning/process
  residue that should simplify rather than expand.
- **Substrate evidence**: the repo already has a functioning graph compiler,
  clean current methodology checks, explicit story/ADR frontmatter contracts,
  generated `docs/stories.md`, and a fresh audit of the remaining misses in
  `docs/scout/scout-012-dossier-methodology-hardening-audit.md`. The missing
  substrate is long-tail hardening coverage, not the migration foundation.
- **Data contracts / schemas**: no runtime/product schema changes are expected.
  The contract change in scope is the eval-registry lineage shape consumed by
  `scripts/methodology_graph.py` and surfaced in `docs/methodology/graph.json`.
- **File sizes**: likely touched files already above 500 lines are
  `scripts/methodology_graph.py` (764), `docs/evals/registry.yaml` (1694), and
  `docs/runbooks/migrate-problem-first-triage-and-story-workflow.md` (478,
  near-threshold). Keep compiler changes narrow and prefer focused doc rewrites
  over adding more prose to oversized files.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`,
  `docs/methodology/state.yaml`, `docs/methodology/graph.json`,
  `docs/methodology-artifact-audit-and-migration.md`,
  `docs/runbooks/setup-methodology.md`,
  `docs/runbooks/migrate-problem-first-triage-and-story-workflow.md`, Story
  `187`, Story `188`, Story `195`, and Scout `012`. No repo-local ADR currently
  settles this post-migration hardening bundle.

## Files to Modify

- `scripts/methodology_graph.py` — expand the live-surface boundary, harden
  stale-guidance detection, and consume explicit eval lineage fields (764
  lines)
- `tests/test_methodology_graph.py` — add regression coverage for the new
  methodology hardening rules (243 lines)
- `docs/evals/registry.yaml` — add explicit eval lineage metadata to every eval
  record (1694 lines)
- `docs/evals/README.md` — teach the explicit eval-registry contract (121
  lines)
- `docs/evals/attempt-template.md` — align attempt scaffolding with the
  explicit lineage contract (56 lines)
- `docs/methodology-artifact-audit-and-migration.md` — rewrite the artifact as
  a completed contract record and align the lint contract with current
  compiler behavior (391 lines)
- `docs/methodology-ideal-spec-compromise.md` — remove build-map-era current
  framing from the methodology reference (307 lines)
- `docs/spec.md` — remove retired build-map framing and rename the `B8`
  planning compromise text (198 lines)
- `AGENTS.md` — remove the remaining Build Map graph framing from the active
  methodology instructions (453 lines)
- `docs/runbooks/setup-methodology.md` — update setup language to the
  graph/state model (157 lines)
- `docs/runbooks/deep-research.md` — replace build-map impact guidance with
  state/graph/generated-view guidance (163 lines)
- `docs/runbooks/migrate-problem-first-triage-and-story-workflow.md` — remove
  transitional `story index if present` / `current state/roadmap file` wording
  from the settled workflow runbook (478 lines)
- `.agents/skills/create-story/SKILL.md` — remove stale `update the story
  index` wording (161 lines)
- `.agents/skills/create-story/scripts/start-story.sh` — remove dead
  `docs/stories.md` helper residue (43 lines)
- `.agents/skills/setup-methodology/references/modes.md` — remove the retired
  build-map migration step (35 lines)
- `.gemini/commands/create-story.toml` — regenerated wrapper reflecting the
  updated skill description (8 lines)
- `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md` —
  historicalize the stale current-state build-map claim (283 lines)
- `docs/stories/story-187-methodology-graph-state-migration.md` — preserve the
  historical warning set without teaching it as the current graph state
- `docs/scout/scout-001-dossier-patterns.md` — historicalize obsolete
  missing-methodology-package claims (64 lines)
- `docs/scout/scout-003-storybook-patterns.md` — historicalize obsolete
  missing-methodology-package claims (75 lines)
- `docs/scout/scout-004-dossier-triage-skills.md` — historicalize obsolete
  triage/story-index-state claims (38 lines)
- `docs/scout/scout-010-dossier-storybook-upgrades.md` — historicalize stale
  build-map-first/current-skill claims (85 lines)
- `docs/scout/scout-011-external-document-ingestion-systems.md` —
  historicalize stale current-state build-map seam claims (176 lines)
- `docs/stories.md` — regenerated story index after the new story and any
  touched metadata compile through the graph
- `docs/methodology/graph.json` — regenerated graph output after the contract
  changes land

## Redundancy / Removal Targets

- Heuristic eval-lineage scraping as the live source of story/spec/compromise
  links
- Dead `docs/stories.md` helper ballast in `/create-story`
- Remaining current-tense build-map/manual-index guidance in active
  methodology docs and wrappers
- Audit-artifact language that still describes the migration as pending when
  the repo already runs on graph/state surfaces

## Notes

- New story justification: this should not reopen Story `187` or Story `188`.
  Those stories migrated the artifact model and removed the first warning set.
  This follow-up has a different success surface: harden the live methodology
  package against the long-tail drift Dossier only found on repeated sweeps.

## Plan

### Exploration Summary

- **Ideal alignment:** proceed. This story removes stale planning guidance and
  heuristic lineage from the live methodology package, which directly supports
  the Execution Ideal and the preference for transparency over magic.
- **Current baseline:** Scout `012` found 20 real misses. Fresh baseline in
  this pass still confirms the main structural ones:
  - `ACTIVE_SURFACE_PATHS` still has only `25` entries
  - `docs/evals/registry.yaml` still has `0` eval records with explicit
    `story_refs`, `category_refs`, `compromise_refs`, or `spec_refs`
  - current clean checks (`python scripts/methodology_graph.py check`,
    `python -m pytest tests/test_methodology_graph.py -q`) still pass despite
    those misses, which proves the missing guardrails are real
- **Critical substrate verified versus missing:**
  - verified: the compiler/test substrate already exists and is easy to extend
  - verified: the stale-guidance targets are present in the current tree
  - missing: direct guardrails for the wider methodology package and explicit
    eval lineage
- **Patterns to follow:** prefer explicit metadata and narrow deterministic
  lint/test rules over more prose-only guidance.

### Implementation Order

1. **Compiler + test hardening** (`M`)
   - widen the active-surface audit to the real live methodology package
   - add explicit generated-view framing checks and explicit-lineage parsing
   - land focused regressions in `tests/test_methodology_graph.py`

2. **Eval contract hardening** (`M`)
   - add explicit lineage fields to every eval record
   - rewrite `docs/evals/README.md` and `docs/evals/attempt-template.md`
   - ensure the compiler consumes the explicit fields directly

3. **Live docs / runbooks / wrappers / helper cleanup** (`L`)
   - rewrite the active methodology docs and runbooks away from build-map-era
     framing
   - update the create-story short-description layer and remove helper-script
     residue
   - historicalize the specific ADR and scout docs that live workflows still
     re-read
   - rewrite the migration audit artifact and Story `187` closeout wording so
     current-state claims are honest

4. **Recompile and verify** (`M`)
   - regenerate graph/index/wrappers
   - run methodology/lint/test checks
   - inspect the rebuilt methodology outputs and the rewritten live docs

### Approval / Risk Notes

- No new dependency is expected.
- No runtime or pipeline schema change is expected.
- Main risk is broadening the lint boundary too aggressively and tripping on
  intentionally historical references. Mitigation: prefer explicit historical
  framing where needed and add tests for the new intended behavior.

## Work Log

20260408-1703 — create-story: created Story 199 as a new follow-up instead of
reopening Stories 187/188 because the remaining work has a different success
surface: long-tail methodology-package hardening rather than initial migration
or metadata backfill. Context reviewed in this pass: `docs/ideal.md`,
`docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`,
`docs/methodology-artifact-audit-and-migration.md`,
`docs/runbooks/setup-methodology.md`,
`docs/runbooks/migrate-problem-first-triage-and-story-workflow.md`, Stories
`187`, `188`, `195`, and Scout `012`. Fresh baseline evidence: the compiler
still reports current graph output clean, `tests/test_methodology_graph.py`
still passes (`7 passed`), `ACTIVE_SURFACE_PATHS` still has only `25` paths,
and `docs/evals/registry.yaml` still has `0/11` eval records with explicit
lineage keys. Result: `Pending` is honest because the substrate exists and the
missing work is a bounded hardening sweep, not an unverified prerequisite.
Next step: implement the compiler/test hardening and explicit eval-lineage
contract first, then rewrite the stale live docs around those rules.
20260408-1716 — implementation: hardened the compiler/test surface and rewrote
the long-tail methodology package to the explicit state/graph contract.
Expanded `ACTIVE_SURFACE_PATHS`, added regression coverage for explicit eval
lineage and generated-view/build-map framing, moved all 11 current evals onto
explicit lineage fields, rewrote the eval docs, updated active skills/runbooks
and wrappers, removed dead `docs/stories.md` helper residue, historicalized
the migration audit record plus Story 187 closeout context, and corrected stale
current-state claims in ADRs 001-003 and the named scout-history surfaces.
Same-pass evidence: `scripts/methodology_graph.py`,
`tests/test_methodology_graph.py`, `docs/evals/registry.yaml`,
`docs/methodology-artifact-audit-and-migration.md`,
`docs/stories/story-187-methodology-graph-state-migration.md`,
`docs/scout/scout-001-dossier-patterns.md`,
`docs/scout/scout-010-dossier-storybook-upgrades.md`, and
`scripts/spikes/surya_component_benchmark.py`. Result: the methodology package
now has one honest current model instead of relying on prose scraping and stale
build-map/manual-index guidance. Next: rerun compile/check/test and close out
the story with fresh evidence.
20260408-1716 — validation/closeout: fresh verification passed after the last
story-scope change. Commands: `./scripts/sync-agent-skills.sh`, `make
methodology-compile`, `make methodology-check`, `python -m pytest
tests/test_methodology_graph.py -q` (`12 passed in 0.78s`), `python -m ruff
check scripts/methodology_graph.py tests/test_methodology_graph.py`, `make
skills-check`, `git diff --check`, `make lint`, and `make test`
(`493 passed, 4 warnings in 418.94s`). Manual artifact inspection in the same
pass re-opened `docs/methodology/graph.json`, `docs/stories.md`,
`docs/evals/registry.yaml`, `docs/methodology-artifact-audit-and-migration.md`,
and the rewritten scout/ADR surfaces to confirm the graph now compiles cleanly
and the remaining historical references are explicitly framed as historical.
Residual warning only: the pre-existing Pydantic deprecation warning in
`modules/portionize/portionize_headers_numeric_v1/main.py:96` still appears in
`make test`; it is unrelated to this story. Result: Story 199 is done and the
next step is `/check-in-diff` if the user wants to review or land the diff.
20260408-1732 — post-closeout re-audit: validated the full Scout 012 list item
by item instead of trusting the earlier implementation summary. Found one real
residual miss: the published lint contract in
`docs/methodology-artifact-audit-and-migration.md` still described legacy
story/ADR metadata and missing-category behavior differently from the current
compiler. Fixed that mismatch, updated
`docs/scout/scout-012-dossier-methodology-hardening-audit.md` to record the
post-implementation re-audit, and reran `make methodology-compile`, `make
methodology-check`, `python -m pytest tests/test_methodology_graph.py -q`, and
`git diff --check`. Result: the full 20-item Scout 012 list is now verified
implemented in this worktree, with the audit doc itself updated from
before-state to after-state evidence.
20260408-1811 — finish-and-push validation: reran the current-tip landing
checks after the final audit-doc fix and before check-in. Commands: `make
lint`, `make skills-check`, `make methodology-check`, `make
methodology-compile`, `git diff --check`, and `make test` (`493 passed, 4
warnings in 483.74s`). Same residual warning only: the pre-existing Pydantic
deprecation in
`modules/portionize/portionize_headers_numeric_v1/main.py:96`. Result: Story
199 still closes cleanly on the current tree and is ready for `/check-in-diff`
landing.
