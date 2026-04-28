# Runbook: Triage Health

Use this runbook when `/triage` needs a read-only health/freshness lane for
this doc-web/doc-forge repo. This lane gathers evidence; it does not choose the
final next action.

## Direct Fact Command

Run:

```bash
python scripts/triage_facts.py --json
```

Use the output for branch/dirty status, generated wrapper drift, stories, evals,
coverage matrix rows, architecture-audit cadence, codebase-improvement
freshness, lane presence, and recent churn. If the command fails, report the
blocker and continue from the underlying files with lower confidence.

## Checks

- Coverage matrix: stale score dates, non-passing rows, broad known gaps, and
  proof claims that should stay bounded to representative fixtures.
- Codebase improvement: latest report age versus recent source churn.
- Eval/model/golden: stale scores, ready retry triggers, missing root/parent
  proof, and current model evidence already present in repo docs.
- Methodology/tooling: skill wrapper drift, graph drift, generated story-index
  drift, and setup checklist drift.
- Architecture audits: due domains, open findings, recent story references, and
  repeated drift signals.
- UI scout: absent unless a dedicated local UI-scout state surface exists.

## Pressure Gate

Health candidates are real pressure when stale evidence would make the next
feature, eval, or architecture story misleading. They are not automatic winners:
the main `/triage` thread must rank them against product capability, eval, story,
and architecture candidates.

## Output

Return up to three neutral health packets:

- candidate
- evidence
- why now
- suggested action
- validation or stop condition
- reasons not now

These packets feed the main `/triage` top-three shortlist and final
recommendation; the health lane does not choose the final repo-wide next action.

Keep the lane read-only. Do not run codebase scouts, architecture audits,
provider-backed evals, golden builds, dependency upgrades, or implementation
work during triage health.
