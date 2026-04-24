# Triage Runbook

This is the operational companion to `/triage`. Use it for full-sweep
methodology triage before treating stories as a flat backlog.

## Completion Sanity Gate

Before accepting a "nothing ready", "maintenance only", or idle
recommendation, inspect the v1/MVP promise, input coverage, future/unplanned
state lines, inbox items, and recent stories/evals. If those surfaces show
missing user-facing capability, recommend creating, promoting, reshaping, or
validating that work before routing to routine maintenance. Never equate "no
ready story" with "feature-complete" without concrete evidence.

## Eval Ladder Gate

For AI-capability work, name the root/parent/child eval placement before
recommending implementation work. Prefer a root or parent eval rerun when new
models, provider changes, code changes, scorer fixes, or changed constraints
could collapse the current decomposition. Prefer a child eval or
failure-classification attempt when the parent failure is too vague to choose an
implementation path honestly.

## Triage Shape

1. Read `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, and
   `docs/methodology/graph.json`.
2. Name the primary unmet Ideal/spec/state gap.
3. Run completion sanity before accepting maintenance-only work.
4. Run the eval-ladder gate for AI-capability gaps.
5. Check existing stories, inbox items, evals, and ADRs for the same gap.
6. Recommend one next action and state why it is the right move now.

## Guardrails

- Do not let a smaller ready story outrank the chosen Ideal/spec/state gap just
  because it is easier to start.
- Do not create implementation backlog when a parent eval failure is still too
  vague to classify.
- Do not force exact wording from another repo when the local product surface
  needs different examples or validation paths.
