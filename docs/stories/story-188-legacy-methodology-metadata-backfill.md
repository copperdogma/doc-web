---
title: "Legacy Methodology Metadata Backfill"
status: "Done"
priority: "High"
ideal_refs:
  - "The Execution Ideal"
  - "Traceability is the product."
  - "Transparency over magic."
spec_refs:
  - "spec:8"
  - "spec:9"
adr_refs: []
depends_on:
  - "187"
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

# Story 188 — Legacy Methodology Metadata Backfill

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/methodology-artifact-audit-and-migration.md`, Story 187, `/Users/cam/Documents/Projects/Storybook/storybook/docs/runbooks/migrate-methodology-to-graph-state.md`, `/Users/cam/Documents/Projects/Storybook/storybook/docs/stories/story-079-methodology-artifact-audit-and-graph-design.md`, `/Users/cam/Documents/Projects/Storybook/storybook/docs/stories/story-081-legacy-metadata-backfill.md`, `/Users/cam/Documents/Projects/Storybook/storybook/docs/methodology-ideal-spec-compromise.md`, `None found after search in docs/decisions/ for a repo-local ADR that already resolves the metadata backfill itself`
**Depends On**: Story 187

## Goal

Finish the remaining metadata half of doc-forge's methodology migration by
backfilling explicit frontmatter onto the remaining legacy story artifacts,
normalizing the oddball historical refs that still trigger graph warnings, and
removing doc-forge's local dependence on legacy story-header fallback where the
files themselves can now carry the truth. The result should be that the repo's
compiled methodology graph is driven by explicit metadata on the historical
artifacts themselves rather than by compatibility parsing that was only meant
to bridge the first migration pass.

## Acceptance Criteria

- [x] A repo-specific audit is recorded in this story's work log before the
      bulk edit, covering the exact current warning set, the count of remaining
      legacy story files, and whether any local ADR frontmatter debt remains.
- [x] Remaining legacy story files carry explicit frontmatter for
      `title`, `status`, `priority`, `ideal_refs`, `spec_refs`, `adr_refs`,
      `depends_on`, `category_refs`, `compromise_refs`,
      `input_coverage_refs`, `architecture_domains`, and `roadmap_tags`,
      with historical context preserved explicitly instead of through live
      header parsing.
- [x] The methodology graph no longer warns that stories are still on legacy
      metadata or that stories still use non-standard status strings, and the
      current one-off warning set is handled explicitly rather than left as
      permanent historical noise.
- [x] The current warning oddballs are resolved or intentionally reduced with
      evidence:
  - [x] Story 063 no longer warns about missing dependency `055`
  - [x] Stories 145 and 148 no longer warn about missing local ADR-019 /
        ADR-021 refs
  - [x] any remaining uncategorized historical stories are explicit repo truth,
        not legacy-parser fallout
- [x] The compiler no longer depends on legacy story or ADR header fallback
      when a file already has frontmatter, and the final story/audit log
      records exactly which warnings were eliminated and which, if any, remain.

## Out of Scope

- Reopening the graph/state architecture from Story 187
- Rewriting historical story prose beyond metadata and narrowly related
  historical-context cleanup
- Inventing fake category/spec mappings for stories where the honest answer is
  still "historical and uncategorized" without evidence
- Changing runtime pipeline behavior, schemas, or artifact contracts
- Creating new local ADRs unless the metadata work unexpectedly reveals a new
  hard-to-reverse methodology decision

## Approach Evaluation

- **Simplification baseline**: this is metadata normalization and compiler
  hygiene. A single LLM call can help plan mappings, but the reliable result is
  deterministic artifact editing driven by the current graph, current story
  bodies, and explicit local oddball fixes.
- **AI-only**: weak as the full solution. Freeform rewriting across 178
  historical stories risks silent metadata drift and would make it harder to
  preserve historical context precisely.
- **Hybrid**: likely winner. Use the current graph and legacy headers as the
  migration seed, apply bulk deterministic frontmatter insertion, then review
  the oddballs and any uncategorized residue manually.
- **Pure code**: plausible for a one-off migration helper or bounded backfill
  script, but avoid adding a permanent registry or a new long-lived metadata
  layer.
- **Repo constraints / prior decisions**: Story 187 already migrated the repo
  to the state+graph methodology and explicitly left legacy story metadata as
  non-blocking debt. No local ADR currently settles the bulk backfill itself.
- **Existing patterns to reuse**: the current story frontmatter template, the
  methodology compiler's parsed graph output, Story 187's audit artifact and
  certification loop, and Storybook Story 081's backfill shape as a reference
  rather than a schema to copy blindly.
- **Eval**: the proof surface is `make methodology-compile`,
  `make methodology-check`, targeted methodology tests, and inspection of the
  final warning set. Success means metadata-debt warning classes disappear
  without introducing new graph errors.

## Tasks

- [x] Audit the current graph/state warning set and classify remaining debt by
      type: legacy story metadata, category/taxonomy gaps, status normalization,
      and one-off broken refs
- [x] Backfill explicit frontmatter onto the remaining legacy story files using
      the current graph plus local story content as the migration seed
- [x] Confirm whether any local ADR backfill is still needed; if the audit
      finds none, record that explicitly and avoid churn
- [x] Resolve the current one-off oddballs in the warning set, especially Story
      063's missing dependency ref and Stories 145/148's external Storybook ADR
      references
- [x] Tighten the methodology compiler so frontmatter-bearing story/ADR files
      do not still depend on legacy header fallback for their live metadata
- [x] Regenerate `docs/methodology/graph.json` and `docs/stories.md`, rerun the
      methodology checks, and record exactly what warnings were eliminated and
      what warnings remain
- [x] Check whether the chosen implementation makes any fallback notes,
      overrides, or migration comments redundant; remove them or create a
      concrete follow-up
- [x] Run required checks for touched scope:
  - [x] `make methodology-compile`
  - [x] `make methodology-check`
  - [x] `python -m pytest tests/test_methodology_graph.py -q`
  - [x] `python -m ruff check scripts/methodology_graph.py tests/test_methodology_graph.py`
  - [x] No broader executable change beyond methodology compiler/test scope, so
        `make lint` was not required
  - [x] No broader executable change beyond methodology compiler/test scope, so
        `make test` was not required
  - [x] Agent tooling was unchanged, so `make skills-check` was not required
  - [x] `git diff --check`
- [x] Search all docs and update any related to the backfill or warning-class
      changes
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: historical methodology artifacts point at explicit
        refs instead of hidden parser behavior
  - [x] T1 — AI-First: use AI only for bounded mapping help, not as an excuse
        for uncontrolled document rewriting
  - [x] T2 — Eval Before Build: use the current graph warning set as the
        baseline before changing compiler behavior
  - [x] T3 — Fidelity: preserve historical story context and oddball notes
        rather than flattening or inventing new history
  - [x] T4 — Modular: prefer explicit metadata on the artifacts over another
        registry or another state override layer
  - [x] T5 — Inspect Artifacts: manually inspect the changed stories, compiled
        graph, and final warning output rather than trusting the bulk edit

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: methodology compiler and historical story metadata
  under `docs/stories/`
- **Methodology reality**: this lives in `spec:8` and `spec:9`, both currently
  `exists`, under the `methodology_tooling` architecture domain. No
  coverage-matrix row is directly affected.
- **Substrate evidence**: `scripts/methodology_graph.py`,
  `docs/methodology/graph.json`, `docs/methodology/state.yaml`, the story
  frontmatter template, and the existing graph warnings prove the repo already
  has the migration substrate and the remaining work is metadata cleanup rather
  than missing infrastructure. Current audit baseline: 178 legacy stories, 124
  stories with no derived category refs, 21 non-standard statuses, Story 063's
  missing `055`, and Story 145/148 external ADR refs; local ADR metadata debt is
  currently zero (`ADR-001` through `ADR-003` are already on frontmatter).
- **Data contracts / schemas**: no runtime product schema changes are expected.
  The contract here is the methodology graph/story metadata shape emitted by
  `scripts/methodology_graph.py`.
- **File sizes**: `scripts/methodology_graph.py` is 705 lines, so keep compiler
  changes narrow and tested. Bulk story edits will touch a large historical
  subset under `docs/stories/`; prefer deterministic edits over bespoke manual
  churn. `docs/methodology-artifact-audit-and-migration.md` is 390 lines and
  should only change if the final warning contract or certification record
  materially shifts.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`,
  `docs/methodology/state.yaml`, `docs/methodology/graph.json`, Story 187, the
  migration audit artifact, and the Storybook references named in the user
  prompt. No local ADR currently settles the historical metadata backfill.

## Files to Modify

- `docs/stories/story-188-legacy-methodology-metadata-backfill.md` — execution
  artifact for this work (new file)
- `docs/stories/story-*.md` (legacy subset) — add explicit frontmatter and
  normalize live metadata ownership
- `scripts/methodology_graph.py` — tighten frontmatter-vs-legacy parsing and
  validation behavior (705 lines)
- `tests/test_methodology_graph.py` — extend coverage for the new compiler
  behavior (31 lines)
- `docs/methodology/graph.json` — regenerated output
- `docs/stories.md` — regenerated output
- `docs/methodology-artifact-audit-and-migration.md` — only if the backfill
  changes the recorded warning contract or certification evidence

## Redundancy / Removal Targets

- Local dependence on legacy story-header parsing as live truth
- Local dependence on non-standard historical status strings
- Story-specific oddball warning residue that can be fixed explicitly instead of
  being carried forever

## Notes

- Current audited warning set at story creation time:
  - `story 063 depends_on missing story 055`
  - `story 145 references ADR with no local adr.md: ADR-019`
  - `story 148 references ADR with no local adr.md: ADR-019`
  - `story 148 references ADR with no local adr.md: ADR-021`
  - `stories still on legacy metadata: 178 (...)`
  - `stories with no derived category refs: 124 (...)`
  - `stories with non-standard statuses: 21 (...)`
- Current audited ADR state at story creation time: all 3 local ADRs already
  carry frontmatter and no ADR warning class is active.
- Historical stories that truly do not map cleanly to the current doc-forge
  taxonomy should be marked explicitly as historical, not silently forced into a
  fake current category.

## Plan

1. Use the current compiled graph as the migration seed to snapshot every
   legacy story's current parsed status, refs, dependencies, and any currently
   derived categories.
2. Bulk-insert explicit frontmatter onto the legacy story set, normalizing
   status values and preserving any needed historical context explicitly.
3. Fix the one-off graph oddballs directly in their story metadata rather than
   leaving them as permanent warnings.
4. Tighten the compiler so frontmatter-bearing files no longer fall back to
   legacy header parsing for live metadata, then rebuild the graph/index.
5. Inspect the final warning set and record exactly what moved, what remains,
   and whether any remaining uncategorized stories are honest historical truth
   or need another bounded follow-up.

## Work Log

20260404-1235 — story creation: audited the post-Story-187 graph before any
backfill work. Current debt is now concentrated in historical story metadata
rather than live methodology architecture: 178 stories still rely on legacy
headers, 124 of those still have no explicit category mapping, 21 still use
non-standard historical status strings, Story 063 still references missing
story `055`, and Stories 145/148 still point at external Storybook ADR-019 /
ADR-021 through live metadata. Local ADR debt is already zero: `ADR-001`
through `ADR-003` all carry frontmatter with no missing keys. Next step: build
the migration seed from the current graph, then bulk-backfill story frontmatter
with explicit one-off fixes for the remaining oddballs.

20260404-1325 — audit refinement before bulk edit: tightened the baseline so
the migration is measured against repo-owned canonical artifacts instead of raw
globs. The current compiler is incorrectly parsing five companion docs as live
stories (`story-062-ocr-content-type-detection.research.md` plus four
`story-084-*` validation/deployment summaries), which inflates the warning set
to 178 legacy stories and 21 non-standard statuses. Restricting the audit to
canonical story files leaves 173 real legacy stories and 16 real non-standard
status cases. The remaining one-off graph oddballs are still Story 063's
historical `055` dependency mention and Stories 145/148 deriving local ADR refs
from Storybook migration-guide prose. Local ADR metadata debt remains zero.
Next step: ignore companion docs in the compiler, then bulk-backfill explicit
frontmatter onto the 173 canonical legacy story files using the current graph
as the migration seed.

20260404-1415 — implementation and certification: completed the follow-on
legacy metadata cleanup pass after Story 187. Added explicit frontmatter to all
173 remaining canonical legacy stories, normalized the 16 non-standard status
cases, fixed Story 063's structured dependency to `065`, filtered frontmatter
ADR refs to local ADR ids so Stories 145/148 no longer treat Storybook
migration guides as missing local ADR files, and changed the compiler so
frontmatter-bearing stories/ADRs no longer fall back to legacy body metadata.
The compiler now ignores the five non-canonical companion docs
(`story-062-ocr-content-type-detection.research.md` and the four
`story-084-*` deployment/validation summaries) when building the live story
graph.

- **Warnings eliminated**
  - `story 063 depends_on missing story 055`
  - `story 145 references ADR with no local adr.md: ADR-019`
  - `story 148 references ADR with no local adr.md: ADR-019`
  - `story 148 references ADR with no local adr.md: ADR-021`
  - `stories still on legacy metadata: 178 (...)`
  - `stories with no derived category refs: 124 (...)`
  - `stories with non-standard statuses: 21 (...)`
- **Warnings remaining**
  - none; current graph validation is `errors = []`, `warnings = []`
- **Residual historical truth**
  - 119 stories still have empty `category_refs`, but that is now explicit
    authored metadata rather than a live migration-warning class
  - local ADR backfill remained unnecessary because `ADR-001` through
    `ADR-003` were already on full frontmatter
- **Verification**
  - `make methodology-compile`
  - `make methodology-check`
  - `python -m pytest tests/test_methodology_graph.py -q`
  - `python -m ruff check scripts/methodology_graph.py tests/test_methodology_graph.py`
- `git diff --check`

20260404-1458 — close-out validation and mark done: re-ran the full close-out
suite required by `/mark-story-done` on the current tip. `python -m pytest
tests/` passed fresh with `448 passed, 4 warnings`; `python -m ruff check
modules/ tests/` passed; `make methodology-check` still reports the generated
graph current; and the rebuilt methodology graph still returns `errors = []`
and `warnings = []`. Story 188 is now closed as the follow-on cleanup pass for
Story 187 rather than leaving the repo on perpetual legacy metadata fallback.
Next step: `/check-in-diff`.
