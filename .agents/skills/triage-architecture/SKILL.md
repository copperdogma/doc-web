---
name: triage-architecture
description: Audit a bounded architecture domain for cleanup pressure and record the next structural move
user-invocable: true
---

# /triage-architecture [domain-id]

> Alignment check: Before choosing an approach, verify it aligns with `docs/ideal.md`, `docs/methodology/state.yaml`, and relevant decision records in `docs/decisions/`. If this work touches a known compromise in `docs/spec.md`, respect its limitation type and evolution path. If none apply, say so explicitly.

Canonical architecture-audit leaf skill. Direct invocation is allowed, and
`/triage architecture` routes here.

## What This Skill Produces

A short advisory report:

- domain health
- structural cleanup signal
- one recommended next action

This skill is read-only unless the user explicitly asks to update the audit
state.

## Lane Packet Mode

When the full `/triage` orchestrator asks for a lane packet, stay read-only and
do not choose the repo-wide recommendation. Return up to three neutral
architecture-domain candidates, including:

- candidate domain and finding
- Ideal promise and spec/state refs
- evidence from `architecture_audits`, recent story refs, ADRs, state, graph,
  and relevant code or runbook surfaces
- why now, including cadence, open findings, recent churn, or repeated drift
- suggested action shape: no action, fold into existing story, create follow-up
  story, ADR/discussion, or health flag only
- whether the candidate is story-worthy or too small for a story
- validation or stop condition
- blockers, stale evidence, and reasons not to do it now

The main `/triage` thread owns final cross-domain ranking. Do not let an
overdue architecture cadence automatically outrank a stronger product/eval
candidate, but surface due architecture work as real pressure. In lane-packet
mode, return candidates and stop conditions; reserve the direct
`### Recommended Action` winner for direct leaf invocation.

## Read First

1. `docs/ideal.md`
2. `docs/spec.md`
3. `docs/methodology/state.yaml`
4. `docs/methodology/graph.json`
5. `docs/runbooks/triage-architecture.md`
6. relevant ADRs and recent story files for the chosen domain

## Steps

1. Resolve the domain
   - if no domain is supplied in direct leaf invocation, inspect
     `architecture_audits` in `docs/methodology/state.yaml` and pick the most
     due domain
   - in lane-packet mode, inspect `architecture_audits` for up to three
     candidate domains and do not collapse them to a single lane winner
   - if a domain is supplied, verify it exists in state

2. Read the domain state
   - last audit date
   - recent story refs
   - open findings
   - manual priority
   - notes

3. Inspect recent evidence
   - story files in `recent_story_refs`
   - recent validation or work-log drift signals
   - relevant ADR/spec slices

4. Judge whether an audit is due
   - high manual priority
   - open findings
   - overdue cadence
   - obvious repeated drift

5. Decide the output shape
   Direct leaf invocation chooses one architecture output:
   - no action
   - fold into existing story
   - create follow-up story
   - escalate to ADR/discussion

   Lane-packet mode returns neutral architecture candidates with stop
   conditions and reasons not now; it does not choose the architecture lane's
   final winner or the repo-wide recommendation.

## Report Format

```markdown
## Triage Architecture

### Domain
- `{domain-id}` — {short summary}

### Due Signals
- {signal or "None"}

### Findings
- {bounded structural issue or "No actionable drift found"}

### Lane Packet
- {candidate + Ideal/spec value + why now + action shape + stop condition}

### Recommended Action
- {one next architecture action; direct leaf invocation only, omit in lane-packet mode}
```

## Guardrails

- Read-only by default
- Keep audits bounded to one domain unless the evidence clearly spans two
- Prefer delete / merge / re-home over new abstraction
- If no action is the honest answer, say so explicitly
