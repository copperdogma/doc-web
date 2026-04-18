---
name: triage
description: Identify the highest-leverage repo gap, then recommend the strongest actionable next move
user-invocable: true
---

# /triage [stories|inbox|evals|architecture] [sub-arg]

> Alignment check: Before choosing an approach, verify it aligns with `docs/ideal.md` and relevant decision records in `docs/decisions/`. If this work touches a known compromise in `docs/spec.md`, respect its limitation type and evolution path. If none apply, say so explicitly.

`/triage` is the meta-skill. It does not own the backlog, inbox, or eval logic
itself. It routes to the leaf skills and, in full-sweep mode, synthesizes one
recommended next action.

Important is not enough by itself. `/triage` must answer both:

- what gap matters most?
- why is this the right thing to do now?
- how close is the repo to the Ideal on today's technology, not just against
  the literal north-star?

A primary gap can stay primary while still being the wrong recommended action
if nothing materially changed since the last attempt, recommendation, or
measurement pass.

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
   - Prefer the compiled actionability surfaces in
     `graph["spec"]["compromises"][*]["actionability"]`,
     `graph["stories"][*]["actionability"]`, and
     `graph["evals"][*]["actionability"]` before re-deriving the same facts
     from story prose and eval notes, but treat them as candidate signals
     rather than final permission to skip the anti-fragmentation review. A
     `Pending` or `recommended_now` story can still be the wrong vehicle if it
     is a same-line fragment.
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

4. **Run the why-now / actionability gate**
   Before recommending work under the strongest problem line, answer:
   - what was the last meaningful action on this line?
   - on what date did it happen?
   - what artifact, story, eval, or recommendation proves that?
   - what materially changed since then?

   Treat these as non-actionable until new evidence appears:
   - blocked stories whose unblock condition is still unmet
   - eval lines whose current retry trigger is exhausted or still missing
   - stale notes that still say "do this next" even though newer blocker or
     retry evidence says "not yet"

5. **Apply phase-pressure defaults**
   Phase is not tie-break metadata. It creates default pressure to keep moving
   the repo toward the Ideal:
   - `converge` → prefer the smallest honest deletion, simplification, or
     residue-removal move that could retire the compromise or prove why it
     cannot be retired yet
   - `climb` → prefer the strongest bounded improvement move that could
     advance the line toward `hold` (quality, proof widening, substrate
     hardening, or a more capable approach)
   - `hold` → prefer thinner / cheaper / faster / simpler / easier-to-operate
     work when no stronger actionable `converge` or `climb` line wins

   A line does not need a new bug report, inbox item, or external prompt to be
   actionable. If phase plus current repo evidence suggests a bounded,
   falsifiable next move, that is enough unless recent evidence says the same
   move is currently blocked, exhausted, or not worth repeating.

6. **Calibrate against the Ideal**
   - Add one short section that answers "how are we doing vs the Ideal?"
   - Keep this grounded in current repo evidence, not vibes
   - Distinguish:
     - literal north-star distance
     - current-tech progress
   - Keep it compact and decision-useful:
     - where the repo is already strong
     - where the biggest remaining gap still blocks a stronger "close to the
       Ideal" claim
     - whether the line of travel is improving, stalled, or blocked

7. **Synthesize one cross-domain recommendation**
   Rank the problem first, then choose the vehicle that best advances it
   (continue an active story, expand/reopen a story, create a story, run an
   eval, do architecture work, or no-op).

   Before recommending `create a story`, challenge that choice against the last
   2-4 stories on the same problem line. If the delta is mostly entry-form
   parity, progression to a later state on the same artifact chain, or
   tests/docs/truth-surface codification for behavior that already exists,
   prefer `continue`, `expand`, `reopen`, or `consolidate` instead.
   Treat pure input/container permutations the same way when the routing,
   owning module, artifact contract, and operator-facing outcome do not
   materially change; prefer representative probes or regression checks inside
   the current class over a new story shell.

   Choose the next action with the strongest combined signal across:
   - movement toward the Ideal
   - real problem pressure
   - phase pressure (`converge` > actionable `climb` > actionable `hold`,
     unless recency/blocker evidence says otherwise)
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

   `No-op` is the last resort, not the default safe answer. It is only honest
   when every plausible phase-aligned move is blocked by missing external
   capability, was just retried on the same premise without a new trigger, or
   lacks a bounded falsifiable next step.

   The recommended action must be phrased so it can be executed directly on the
   next turn. A bare `yes` from the user should be enough to authorize that one
   action without needing a follow-up clarification.

8. **Return the compact report**

```markdown
## Triage

### Actionability
- Last relevant action: {date + story/eval/artifact}
- Why now: {materially new trigger or "none"}
- If "none": {why the primary gap is not the recommended action today}

### Vs Ideal
- Literal north-star: {how far the repo still is from the true Ideal}
- Current-tech read: {how close the repo is to a strong present-day version of the Ideal}
- Direction: {getting closer | mixed | stalled | blocked} — {why}

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
- Always include a short `Vs Ideal` read in full-sweep mode.
- End with a clear acceptance prompt that the user can approve with `yes`.
- Respect leaf-skill boundaries: `/triage inbox` may modify files; unscoped
  `/triage` may not.
- Do not overweight `Draft` / `Pending` story presence. Story shells are
  packaging, not priority signals.
- Preserve continuity for active unresolved work lines when leverage is
  otherwise comparable.
- Do not recommend reopening a blocked line unless the current pass can point
  to fresh evidence that satisfies the story's unblock condition.
- Do not recommend repeating a line just because it is still the biggest open
  gap; cite the last attempt and the current why-now trigger explicitly.
- A primary gap with no materially new trigger may stay primary, but it should
  usually move to `Health Flags` or `Runner-Ups` rather than become the
  recommended action.
- Do not recommend a new story for same-line entry-form parity, same-line
  later-state progression, or tests/docs/truth-surface codification on current
  behavior unless the repo evidence shows that the runtime seam or validation
  boundary really changed.
- Do not recommend a new story just because an already-supported capability now
  appears through another container or entry permutation when the behavior
  class, routing/provenance seam, and downstream artifact contract are still
  the same.
- Do not treat lack of a fresh external trigger as sufficient reason for
  `no-op` when a bounded phase-aligned improvement move still exists.
- Prefer recommending the best next attempt, simplification, or new story shell
  over `no-op` unless the repo is genuinely out of actionable phase-aligned
  moves.
- `Converge` means "try to delete or collapse residue," not "wait until
  something else happens."
