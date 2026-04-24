---
name: triage-evals
description: Diagnose which eval work is actually actionable now for the current repo gap
user-invocable: true
---

# /triage-evals [eval-id]

> Alignment check: Before choosing an approach, verify it aligns with `docs/ideal.md` and relevant decision records in `docs/decisions/`. If this work touches a known compromise in `docs/spec.md`, respect its limitation type and evolution path. If none apply, say so explicitly.

Canonical eval-health triage leaf skill. Direct invocation is allowed, and
`/triage evals` routes here.

## Eval Ladder Gate

For AI-capability work, identify the eval ladder before creating or prioritizing
implementation backlog:

- the root Ideal eval or full-path golden, or the explicit reason it is deferred
- the parent eval or latest higher-level result that shows the current failure
- the measured failure mode that makes decomposition necessary
- the child eval, failure-classification attempt, ADR/spec update, or story that
  advances the next unresolved ladder node

Prefer rerunning a root/parent eval when new models, provider changes, code
changes, scorer fixes, or changed constraints could collapse the current
decomposition. Prefer a child eval or failure-classification attempt when the
parent failure is still too vague to choose AI-only, multi-call AI, deterministic
code, or hybrid implementation honestly.

## Scope

- no argument: scan the full eval surface
- eval ID argument: assess one eval's health, staleness, and next action

This skill is read-only and advisory. It never runs evals automatically.

The core filter is actionability, not abstract importance. A red or stale eval
line is not recommendable unless the diagnosis can name why that line should be
revisited now.

## Read First

1. `docs/evals/registry.yaml`
2. `docs/spec.md`
3. `docs/methodology/state.yaml`
4. `docs/methodology/graph.json`
   - Prefer `graph["evals"][*]["actionability"]` and
     `graph["spec"]["compromises"][*]["actionability"]` for last-action,
     retry-posture, and "why now" reads before reconstructing them manually.
5. relevant ADRs under `docs/decisions/`
6. recent `git log --oneline -20`

If a recommendation depends on model availability, pricing, or a newly released
provider capability, verify it with current official docs or a fresh web search
before claiming the trigger is met.

## What To Evaluate

### 1. Eval class

Derive the triage class from registry context:

- **quality-runtime** — quality evals where latency or cost is part of the decision
- **quality-capability** — output-fidelity or behavior-quality gates
- **compromise-detection** — deletion gates for spec compromises

### 2. Rerun triggers

Check whether recorded `retry_when` conditions are now actionable:

- `new-worker-model`
- `new-subject-model`
- `cheaper-subject-model`
- `faster-subject-model`
- `new-approach`
- `golden-fix`
- `architecture-change`
- `dependency-available`

Use recent git history, current stories, current docs, and verified model
availability to judge whether the trigger is actually met. If the same trigger
was already exercised in the latest attempt and failed without changing the
decision surface, do not recommend the same rerun again until there is another
material trigger.

Also capture:
- the last meaningful action on the line
- the date of that action
- what materially changed since then

### 3. Phase-aware assessment

Read the methodology-state phase for each eval's compromise category:
- `converge` → default pressure to prove the compromise can be deleted or to
  remove the smallest remaining residue
- `climb` → default pressure to improve quality, widen proof, or test the next
  credible stronger approach until the line can move toward `hold`
- `hold` → lower but real pressure to make the current line cheaper, faster,
  thinner, or easier to operate when higher-pressure lines are not actionable

Phase is enough to justify an eval recommendation when there is a bounded,
falsifiable next move. A line does not need a new external announcement or a
fresh inbox item before it becomes worth improving again.

### 4. Deletion-gate health

For compromise-detection evals:

- is the last score close to the threshold?
- did it already pass while the compromise still lingers in docs?
- is a compromise missing an eval entirely?
- does `docs/methodology/state.yaml` still match the registry?
- does the compiled graph's category/compromise linkage match the eval's target?

### 5. General eval hygiene

Look for:

- active systems whose quality evals are stale after meaningful prompt/pipeline changes
- stale compromise-detection scores
- duplicate or confusing eval coverage
- missing evals for active compromises

## Report Format

```markdown
## Triage Evals

### Rerun Candidates
- {eval-id} — {why now}
  - Last relevant action: {date + attempt/story/evidence}

### Deletion Candidates
- {compromise / eval-id} — {why the compromise may now be deletable}

### Missing / Weak Coverage
- {gap}

### Recommended Action
- {one next eval action}

### Health Flags
- {stale score / missing eval / docs-registry drift}
```

## Follow-Through Guidance

Recommend the smallest correct next step:

- `/improve-eval <id>` when an eval should be investigated or rerun
- current model-availability research when the trigger depends on new releases
- `/create-story` when the issue is an implementation gap, not just eval staleness
- update `docs/methodology/state.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, or `docs/spec.md` when the truth surfaces drift from a passing gate

Prefer a concrete next move over `no action` whenever a phase-aligned,
bounded experiment or proof refresh still exists. Reserve `no action` for lines
that are truly blocked on external capability, just retried on the same
premise, or missing a falsifiable next experiment.

Do not auto-run expensive evals. Present cost/time implications and let the
user decide.

## Guardrails

- Read-only and advisory
- Be explicit when a recommendation depends on verified current model availability
- Do not confuse runtime benchmarks with capability gates or deletion gates
- Do not recommend the same retry trigger repeatedly when the latest recorded
  attempt already exercised it and no new model, approach, golden, or
  architecture change has appeared since
- Do not convert "big gap" or "red line" into "do this now" without naming a
  concrete why-now trigger or a genuinely new unanswered question.
- Do not treat "no newly released model" as sufficient reason for no action
  when a bounded prompt, golden, proof-refresh, or architecture-linked eval
  move still exists.
- If a `converge` or `climb` line still has a bounded falsifiable next move,
  prefer recommending it over `no action`.
- If no eval action is justified, say so clearly
- Keep the report compact enough for `/triage` to synthesize with other leaf reports
