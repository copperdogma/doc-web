# Runbook: Setup Methodology

> Canonical prose front door for doc-forge's methodology package.
> Use this runbook together with `/setup-methodology`.

## Why This Exists

Doc-forge already has the core ADR-021-shaped methodology surfaces:

- dual ideal in `docs/ideal.md`
- category-aligned spec in `docs/spec.md`
- build-map dashboard in `docs/build-map.md`

What used to be missing was the refresh package around them:

- methodology reference doc
- working setup checklist
- eval-surface docs
- AGENTS wiring that treats the build map as the operating surface

This runbook exists so those pieces are installed and refreshed together
instead of drifting as tribal memory.

## Core Hierarchy

1. **Ideal** — product + execution north star
2. **Spec** — active product and build constraints
3. **Build Map** — central planning / triage dashboard
4. **Stories** — implementation slices under build-map goals
5. **Evals** — quality evidence and compromise-deletion signals

**Operating rule:** planning and triage start from `docs/build-map.md`.
Implementation starts from the active story, but must read the relevant
build-map category and linked `spec:N` sections first.

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
- `docs/build-map.md`
- `docs/RUNBOOK.md`
- `docs/runbooks/golden-build.md`
- benchmark and fixture guidance

## Baseline vs Day-to-Day

### Baseline setup / refresh

The package is not complete unless the repo has:

- methodology docs that agree with each other
- a working checklist
- eval registry protocol docs
- honest benchmark / golden guidance
- AGENTS instructions that point at the build map and current skill surface

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
3. Normalize docs to the package hierarchy
4. Refresh eval-surface docs to match actual practice
5. Replace stale planning guidance

### ADR-021 migration

1. Add the execution ideal
2. Align spec and build-map categories
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
- `docs/ideal.md`
- `docs/spec.md`
- `docs/build-map.md`
- `docs/evals/README.md`
- `docs/decisions/README.md`
