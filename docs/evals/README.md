# Eval Registry System

Central tracking for doc-forge's evaluation metrics, improvement attempts, and
compromise-deletion signals.

Baseline eval-surface setup now belongs to `/setup-methodology`. Once that
package exists:

- use `/improve-eval` to iterate on existing evals
- use this README plus the attempt template when a new eval must be scaffolded

## Structure

```text
docs/evals/
├── registry.yaml          # Source of truth — evals, scores, attempt summaries
├── attempt-template.md    # Template for new attempt notes
├── attempts/              # Optional markdown notes per improvement attempt
└── README.md              # This file
```

## Registry Protocol

### When to update `registry.yaml`

Always update the registry when you run an eval or materially verify an eval
result.

| Situation | Action |
|---|---|
| Ran an eval | Update the score entry with metrics, date, and `git_sha` |
| Completed an improvement attempt | Append an attempt summary and refresh scores |
| Added a new eval | Add the full eval entry |
| Added a new compromise gate | Add the compromise eval entry and target |
| Verified that a recorded score is stale | Re-run and update |

### Staleness

A score is stale if the code or benchmark surface changed materially after the
recorded `git_sha`. When in doubt, re-measure.

## Improvement Attempts

### Creating an attempt note

1. Copy `docs/evals/attempt-template.md` to `docs/evals/attempts/{NNN}-{eval-id}-{short-title}.md`
2. Number sequentially across all evals, not per-eval
3. Read the eval's prior attempts in `docs/evals/registry.yaml` before starting
4. Follow the Definition of Done checklist at the bottom of the template

Attempt notes are optional but recommended when the change is non-trivial,
especially for failed or ambiguous retries. Short successful runs can live only
in `registry.yaml` if the summary there is sufficient.

## New Evals

Doc-forge does not yet have a dedicated eval-creation skill. Until it does:

1. add the new benchmark assets and scorer/config in the repo
2. add the eval entry to `docs/evals/registry.yaml`
3. record the baseline score
4. reference the eval from the relevant story, spec compromise, or build-map gap

Use `/improve-eval` only after the eval already exists.

## Attempt Summary in the Registry

After completing an attempt, add a compact summary to the eval's `attempts`
list:

```yaml
attempts:
  - id: "001"
    date: 2026-03-20
    status: failed  # succeeded | failed | inconclusive
    approach: "Prompt-only retry with stronger table-shape instructions"
    score_before: 0.90
    score_after: 0.91
    retry_when:
      - condition: new-subject-model
        note: "Current model still misses dense genealogy edge cases"
```

## Retry Conditions

| Condition | Meaning | Recheck trigger |
|---|---|---|
| `new-worker-model` | Smarter AI might execute the same change better | New model release |
| `new-subject-model` | Better pipeline model may pass without code changes | New model release |
| `cheaper-subject-model` | Current quality works, but cost parity is missing | Pricing or model changes |
| `faster-subject-model` | Current quality works, but latency is too high | Pricing or model changes |
| `new-approach` | Current approaches exhausted | Fresh technique or new evidence |
| `golden-fix` | Golden reference or scorer may be wrong | Manual review |
| `architecture-change` | Upstream pipeline or artifact shape must change first | Pipeline refactor |
| `dependency-available` | Waiting on a library, tool, or API | Ecosystem change |

## Compromise Evals

Compromise evals test whether a spec compromise can be eliminated. They should
link back to the relevant spec section and build-map category.

When a compromise eval passes consistently, the compromise should be revisited
for simplification or deletion.

Failed compromise attempts are still valuable. They record where the frontier is
not yet good enough and make later retries evidence-based instead of repetitive.

## Speed and Cost

Speed and cost are first-class signals, not afterthoughts.

Doc-forge often runs expensive OCR or multimodal loops on large artifacts.
When choosing a model or prompt path, compare:

- quality
- cost per run
- latency / throughput
- how much artifact reuse the path requires

The right answer is usually the cheapest and fastest path that still clears the
quality bar for the current category and phase.
