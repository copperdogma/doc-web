# Runbook: Setup Methodology

> Canonical prose front door for doc-forge's methodology package.
> Use this runbook together with `/setup-methodology`.

## Why This Exists

Doc-forge already has the authored methodology canon:

- dual ideal in `docs/ideal.md`
- category-aligned spec in `docs/spec.md`
- machine-readable coverage matrix in `tests/fixtures/formats/_coverage-matrix.json`

What this runbook now installs or refreshes is the graph+state package around
that canon:

- methodology reference doc
- structured methodology state
- compiled methodology graph
- generated story index
- working setup checklist
- eval-surface docs
- AGENTS wiring that treats state + graph + coverage matrix as the operating surface

This runbook exists so those pieces are installed and refreshed together
instead of drifting as tribal memory.

## Core Hierarchy

1. **Ideal** — product + execution north star
2. **Spec** — active product and build constraints
3. **Methodology State** — mutable planning truth
4. **Coverage Matrix** — canonical input-coverage truth
5. **Compiled Graph** — deterministic joins for AI consumers
6. **Stories** — implementation slices under graph/state goals
7. **Evals** — quality evidence and compromise-deletion signals

**Operating rule:** planning and triage start from
`docs/methodology/state.yaml`, `docs/methodology/graph.json`, and
`tests/fixtures/formats/_coverage-matrix.json`. Implementation starts from the
active story, but must read the relevant graph/state category and linked
`spec:N` sections first.

## Public Surface

### Bootstrap / Refresh

- `/setup-methodology` — the canonical setup or refresh entrypoint

Modes:

- `greenfield`
- `retrofit`
- `adr-021-migration`
- `refresh`

### Recurring Day-to-Day Surfaces

- `/improve-eval` — iterate on existing evals and record verified scores
- `/align` — sweep the methodology graph for drift after a meaningful change
- `/triage` — choose the next high-leverage move from stories, inbox, and evals
- normal story/build/validate/closeout skills

For new evals, follow the manual scaffolding and registry protocol in
`docs/evals/README.md` until a dedicated eval-creation skill exists.

## What `/setup-methodology` Installs or Refreshes

- `docs/methodology-ideal-spec-compromise.md`
- `docs/setup-checklist.md`
- `docs/evals/README.md`
- `docs/evals/attempt-template.md`
- `AGENTS.md` methodology guidance and public-surface wiring
- cross-CLI skill sync

It also audits that the existing repo surfaces still match reality:

- `docs/ideal.md`
- `docs/spec.md`
- `docs/methodology/state.yaml`
- `docs/methodology/graph.json`
- `tests/fixtures/formats/_coverage-matrix.json`
- `docs/RUNBOOK.md`
- `docs/runbooks/golden-build.md`
- benchmark and fixture guidance

## Baseline vs Day-to-Day

### Baseline setup / refresh

The package is not complete unless the repo has:

- methodology docs that agree with each other
- structured state and a compiled graph that agree with the authored canon
- a working checklist
- eval registry protocol docs
- honest benchmark / golden guidance
- AGENTS instructions that point at the graph/state package and current skill surface

### Day-to-day work

Once the package exists, ongoing work moves to:

- `/improve-eval`
- `/align`
- `/triage`
- normal story, ADR, build, validate, and closeout flows

## Recommended Flow By Mode

### Greenfield

1. Capture the ideal
2. Create the category-aligned spec and build map
3. Install the methodology reference and checklist
4. Install eval-surface docs
5. Normalize AGENTS and skill sync

### Retrofit

1. Read the repo first
2. Create or refresh the checklist
3. Add or refresh the methodology state + compiler
4. Refresh eval-surface docs to match actual practice
5. Replace stale planning guidance

### ADR-021 migration

1. Add the execution ideal
2. Align spec and methodology-state categories
3. Refresh AGENTS and methodology docs
4. Normalize the public setup surface around `/setup-methodology`

### Refresh

1. Regenerate or refresh the working checklist
2. Refresh AGENTS, runbook, and eval-surface docs
3. Refresh skill wrappers
4. Audit for stale setup language and planning drift

## Checklist Rule

Every `/setup-methodology` run should work from `docs/setup-checklist.md`.

That file is the active working copy. It prevents long refreshes from silently
dropping parts of the package.

## Related References

- `docs/methodology-ideal-spec-compromise.md`
- `docs/methodology/state.yaml`
- `docs/methodology/graph.json`
- `docs/ideal.md`
- `docs/spec.md`
- `tests/fixtures/formats/_coverage-matrix.json`
- `docs/evals/README.md`
- `docs/decisions/README.md`
