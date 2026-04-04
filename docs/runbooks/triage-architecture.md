# Architecture Triage

Use this runbook when the question is whether doc-forge needs a bounded
structural simplification pass rather than a new feature or eval iteration.

This is the operational companion to `/triage-architecture`.

## Why This Exists

Feature work naturally accumulates architecture drift:

- wrappers instead of deletion
- duplicate ownership instead of re-homing
- stale compatibility paths that survive too long
- large files or helper seams that stop matching the real ownership boundary

The architecture-audit lane gives that drift a cadence, memory, and bounded
domains. It is not a repo-wide "clean things up" ritual.

## Inputs

- `docs/methodology/state.yaml` `architecture_audits`
- `docs/methodology/graph.json`
- recent story churn
- recent validation/work-log drift signals
- relevant ADRs/spec slices for the chosen domain

## Due Signals

Treat an architecture audit as due when one or more of these hold:

- `manual_priority` is high
- `open_findings` already exist for the domain
- `stories_since_audit` meets or exceeds the target cadence
- the domain has recent churn but no prior audit
- validation keeps surfacing the same drift pattern
- performance pain or repeated bug-fix churn points back to structure

If none apply strongly, a no-op audit is acceptable. The lane should stay
honest, not busy.

## Domain Selection

Doc-forge's seeded domains are bounded ownership surfaces:

- `methodology_tooling`
- `intake_and_routing`
- `ocr_and_extraction`
- `document_structure_and_consistency`
- `doc_web_runtime`

Do not expand this list casually. New domains should correspond to real
ownership boundaries.

## Audit Procedure

1. Read the methodology frame
   - `docs/ideal.md`
   - `docs/spec.md`
   - `docs/methodology/state.yaml`
   - `docs/methodology/graph.json`

2. Read the chosen domain state
   - last audit date
   - open findings
   - recent story refs
   - notes / manual priority

3. Read recent evidence
   - recent story files in `recent_story_refs`
   - recent validation notes if they flagged drift
   - relevant ADRs/spec slices

4. Inspect current code reality
   - hotspot files
   - churn concentration
   - duplicate ownership
   - stale wrappers/shims
   - structural causes of performance or complexity pain

5. Decide one output
   - no action
   - fold into existing story
   - follow-up story
   - decision escalation

6. Record the result
   - update `docs/methodology/state.yaml`
   - rerun `make methodology-compile`
   - do not create implementation artifacts unless explicitly approved

## Validation Feed

`/validate` is the main feeder into this lane.

When validation finds medium/high drift signals that do not belong to the
current story's shipping slice, it should:

- map the signal to a best-fit `architecture_audits` domain
- cite the story/work-log source
- recommend `/triage architecture <domain-id>` when the issue is real but not
  in scope to fix immediately

## Boundaries

### Always do

- prefer delete / merge / re-home / simplify
- keep audits bounded to 1-2 domains
- record a no-op when that is the honest answer

### Ask first

- before creating a new story from the audit
- before changing audit domains materially
- before escalating to a new ADR

### Never do

- never do repo-wide undirected audits
- never propose a new architecture just because refactoring sounds nice
- never keep stale findings alive after they were disproven
- never use this lane to justify speculative churn
