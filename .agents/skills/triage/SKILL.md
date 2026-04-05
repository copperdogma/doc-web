---
name: triage
description: Orchestrate the triage leaf skills and synthesize the highest-value next action
user-invocable: true
---

# /triage [stories|inbox|evals|architecture] [sub-arg]

> Alignment check: Before choosing an approach, verify it aligns with `docs/ideal.md` and relevant decision records in `docs/decisions/`. If this work touches a known compromise in `docs/spec.md`, respect its limitation type and evolution path. If none apply, say so explicitly.

`/triage` is the meta-skill. It does not own the backlog, inbox, or eval logic
itself. It routes to the leaf skills and, in full-sweep mode, synthesizes one
recommended next action.

## Routing

| Invocation | Behavior |
|---|---|
| `/triage` | Full-sweep orchestrator mode |
| `/triage stories` | Delegate to `/triage-stories` |
| `/triage stories 145` | Delegate to `/triage-stories 145` |
| `/triage inbox` | Delegate to `/triage-inbox` (processing mode) |
| `/triage inbox scan` | Delegate to `/triage-inbox scan` (read-only mode) |
| `/triage evals` | Delegate to `/triage-evals` |
| `/triage evals image-crop-extraction` | Delegate to `/triage-evals image-crop-extraction` |
| `/triage architecture` | Delegate to `/triage-architecture` |
| `/triage architecture methodology_tooling` | Delegate to `/triage-architecture methodology_tooling` |

When a scope is provided, hand off completely to the leaf skill. Do not
maintain duplicate logic here.

## Leaf Skills

- `/triage-stories` — backlog prioritization, readiness, dependency bottlenecks
- `/triage-inbox` — inbox scan or processing
- `/triage-evals` — eval health, rerun candidates, compromise deletion signals
- `/triage-architecture` — bounded structural simplification / cleanup lane

## Full-Sweep Mode

When invoked with no scope:

1. **Read the shared frame**
   - `docs/ideal.md`
   - `docs/spec.md`
   - `docs/methodology/state.yaml`
   - `docs/methodology/graph.json`
   - `tests/fixtures/formats/_coverage-matrix.json`
   - relevant ADRs under `docs/decisions/`
   - recent `git log --oneline -20`

2. **Run leaf sweeps in parallel**
   - `/triage-stories`
   - `/triage-inbox scan`
   - `/triage-evals`
   - `/triage-architecture`

3. **Collect leaf reports**
   Each report should return:
   - one top recommendation
   - 1-3 supporting reasons
   - health flags / bottlenecks
   - whether the recommendation is read-only or action-taking

4. **Synthesize one cross-domain recommendation**
   Rank the problem first, then choose the vehicle that best advances it
   (continue an active story, expand/reopen a story, create a story, run an
   eval, do architecture work, or no-op).

   Choose the next action with the strongest combined signal across:
   - movement toward the Ideal
   - real problem pressure
   - blocking power / dependency leverage
   - compromise-elimination leverage
   - phase coherence (climb/hold/converge alignment across categories)
   - substrate readiness
   - continuity from active or recently advanced unresolved work lines
   - urgency / staleness
   - operator cost
   - existing story shells only as packaging / tie-break context, not as value by themselves

   If the strongest problem line is explicitly `Blocked`, verify whether its
   unblock condition is actually met in the current pass. If not, surface that
   line as a health flag and recommend a different actionable move or an honest
   `no-op`; do not turn blocked continuity into a reopen recommendation.

   The recommended action must be phrased so it can be executed directly on the
   next turn. A bare `yes` from the user should be enough to authorize that one
   action without needing a follow-up clarification.

5. **Return the compact report**

```markdown
## Triage

### Recommended Action
- {one next action}

### Why
- {2-3 strongest reasons}

### Runner-Ups
- {alternate action}
- {alternate action}

### Domain Notes
- Stories: {summary}
- Inbox: {summary}
- Evals: {summary}

### Health Flags
- {blocked story / stale inbox / stale eval / pending ADR}

### Decision
- Reply `yes` to proceed with: {repeat the one recommended action verbatim}
```

## Guardrails

- Scoped invocations delegate; do not duplicate leaf logic here.
- Full-sweep mode is read-only.
- Use parallel leaf sweeps when feasible.
- Return one recommendation, not a vague list.
- End with a clear acceptance prompt that the user can approve with `yes`.
- Respect leaf-skill boundaries: `/triage inbox` may modify files; unscoped
  `/triage` may not.
- Do not overweight `Draft` / `Pending` story presence. Story shells are
  packaging, not priority signals.
- Preserve continuity for active unresolved work lines when leverage is
  otherwise comparable.
- Do not recommend reopening a blocked line unless the current pass can point
  to fresh evidence that satisfies the story's unblock condition.
