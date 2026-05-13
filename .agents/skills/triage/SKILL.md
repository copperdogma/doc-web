---
name: triage
description: Orchestrate doc-web triage from Ideal/spec facts and neutral lane packets, then recommend the best next action
user-invocable: true
---

# /triage [stories|inbox|evals|architecture|health] [sub-arg]

> Alignment check: Before choosing an approach, verify it aligns with `docs/ideal.md` and relevant decision records in `docs/decisions/`. If this work touches a known compromise in `docs/spec.md`, respect its limitation type and evolution path. If none apply, say so explicitly.

`/triage` is the meta-skill. It does not own the backlog, inbox, eval,
architecture, or health logic itself. In full-sweep mode it starts from the
Ideal/spec/state/graph and coverage facts, gathers neutral lane packets, shows
the top three cross-domain candidates, then synthesizes one recommended next
action.

Important is not enough by itself. `/triage` must answer both:

- what gap matters most?
- why is this the right thing to do now?
- how close is the repo to the Ideal on today's technology, not just against
  the literal north-star?
- which top three cross-domain candidates are credible, and why did the final
  recommendation beat the other top-three candidates?

A primary gap can stay primary while still being the wrong recommended action
if nothing materially changed since the last attempt, recommendation, or
measurement pass.

## Worker Model Sizing

When full-sweep triage launches neutral lane packets with subagents, size each worker model and reasoning level to lane risk. Use cheaper or lower-reasoning workers for factual scans and mechanical packet gathering; keep stronger workers for semantic contracts, security, eval correctness, cross-repo decisions, or high-cost misses. Record any explicit override rationale in the triage report.

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
| `/triage health` | Delegate to `/triage-health` |
| `/triage health scan` | Delegate to `/triage-health scan` |

When a scope is provided, hand off completely to the leaf skill. Do not
maintain duplicate logic here.

## Leaf Skills

- `/triage-stories` — backlog prioritization, readiness, dependency bottlenecks
- `/triage-inbox` — inbox scan or processing
- `/triage-evals` — eval health, rerun candidates, compromise deletion signals
- `/triage-architecture` — bounded structural simplification / cleanup lane
- `/triage-health` — read-only freshness packet across coverage, codebase
  improvement, eval/model/golden, methodology/tooling, architecture-audit, and
  absent UI-scout truth
- `/codebase-improvement-scout` — report-first codebase hygiene follow-up when
  triage recommends it
- `/discover-models` — provider/model freshness follow-up when triage recommends it

When full-sweep `/triage` asks a leaf for input, request a compact lane packet
instead of a final repo-wide decision. Each lane packet should provide up to
three neutral candidates with:

- candidate name
- Ideal promise and spec refs
- evidence and source files
- why now
- suggested action shape
- whether it is story-worthy or too small
- validation or stop condition
- blockers, stale evidence, and reasons not to do it now

The main `/triage` thread owns cross-domain ranking. Do not preselect one
"largest gap" so narrowly that leaf lanes ignore stronger evidence in their own
domains.

## Completion Sanity Gate

Before accepting a "nothing ready", "maintenance only", or idle
recommendation, prove that the repo is not hiding undecomposed product scope.
Check the v1/MVP promise, input coverage, future/unplanned state lines, inbox
items, and recent stories/evals. If those surfaces show missing user-facing
capability, recommend creating, promoting, reshaping, or validating that work
before routing to routine maintenance. Never equate "no ready story" with
"feature-complete" without concrete evidence.

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
   - Goal: identify the broad candidate set of live gaps and simplification
     opportunities before reading stories as a backlog, without choosing the
     final winner yet.

2. **Start neutral lane evidence, then run the fact collector directly**
   - Unscoped `/triage` is a contracted fan-out command. Treat the user's
     invocation of unscoped `/triage` as explicit authorization to use the
     runtime's subagent/delegation tool for neutral lane packets when it is
     available and safe for the current checkout.
   - Immediately launch scoped lane packet requests after reading the shared
     frame. Keep packets neutral: ask each lane for its best candidates from the
     broad Ideal/spec/state/graph/coverage context, not for a final repo-wide
     pick and not for confirmation of one preselected gap.
   - Ask these lanes for packets:
     - `/triage-stories`
     - `/triage-inbox scan`
     - `/triage-evals`
     - `/triage-architecture`
     - `/triage-health scan`
   - In the main thread, while lane packets are running, run:

     ```bash
     python scripts/triage_facts.py --json
     ```

   - Use the facts for branch/dirty state, generated wrapper drift, story/eval
     recommendations, inbox counts, architecture-audit cadence, coverage matrix
     status, codebase-improvement freshness, lane presence, and recent churn.
   - If the script fails, say so explicitly and continue from the underlying
     docs with lower confidence. Do not pretend the fact pass happened.
   - If subagents/delegation are unavailable, unsafe for the current checkout,
     or the user explicitly asks not to use them, still run the direct fact
     collector here, then query the same neutral lane packet contracts
     sequentially later and state that fallback in the response.

3. **Open candidate gaps without picking a winner yet**
   - State 2-4 plausible unmet Ideal promises or overscaffolded compromises in
     plain language.
   - Map each to owning spec section(s), methodology category, phase, coverage
     matrix row if relevant, and known evidence.
   - Do not pick the final winner before lane packets report.

4. **Run the why-now / actionability gate for plausible winners**
   Before recommending work under a candidate problem line, answer:
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

6. **Read decision and architecture constraints for plausible winners**
   - Open relevant ADRs and architecture-audit state for candidate gaps.
   - If none apply, say so explicitly.
   - Do not recommend work that fights a settled boundary such as the doc-web
     runtime boundary or the maintained intake contract.

7. **Collect lane packets**
   - If subagents were used, collect their lane reports here.
   - If using the sequential fallback, run the same scoped contracts now and
     state that no subagents were used.
   - Keep `scripts/triage_facts.py` as a direct main-thread fact source, not a
     delegated lane and not a substitute for lane judgment.

8. **Calibrate against the Ideal**
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

9. **Build the top-three shortlist**
   Merge lane candidates into the top three cross-domain recommendations. Each
   item must include:
   - recommendation
   - Ideal/spec value
   - why now
   - action shape
   - validation or stop condition
   - why it ranked above or below the other two

   Do not hide the other top-three candidates. Cam may choose recommendation 2
   or 3 when human context changes the call.

10. **Synthesize one cross-domain recommendation**
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
   When a new story is still the right vehicle, do not default to a few-minute
   slice. If adjacent work shares the same artifact chain, owning module,
   validation boundary, or operator-facing outcome, expand the boundary toward
   roughly one focused AI hour of implementation plus validation, or longer
   when that is the smallest coherent milestone. Treat that as a sizing
   heuristic, not a quota; keep tiny stories only for genuine high-risk
   unknowns, blockers, or indivisible proof boundaries.

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

11. **Return the compact report**

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

### Top Three Recommendations
1. {recommendation}
   - Ideal/spec value: ...
   - Why now: ...
   - Action shape: ...
   - Validation/stop condition: ...
   - Why this rank: ...
2. {recommendation}
   - Ideal/spec value: ...
   - Why now: ...
   - Action shape: ...
   - Validation/stop condition: ...
   - Why this rank: ...
3. {recommendation}
   - Ideal/spec value: ...
   - Why now: ...
   - Action shape: ...
   - Validation/stop condition: ...
   - Why this rank: ...

### Domain Notes
- Stories: {summary}
- Inbox: {summary}
- Evals: {summary}
- Architecture: {summary}
- Health/freshness: {coverage/codebase/methodology/model signals}

### Health Flags
- {blocked story / stale inbox / stale eval / pending ADR}

### Recommended Action
- {one next action}
- Why: {2-3 strongest reasons}

Reply yes to proceed with: {exact next command or concrete action}.
```

## Guardrails

- Scoped invocations delegate; do not duplicate leaf logic here.
- Full-sweep mode is read-only.
- Unscoped `/triage` explicitly authorizes subagent lane fan-out when the
  runtime exposes it and the checkout is safe for read-only delegation; otherwise
  keep the same lane-packet contracts sequentially and state the fallback.
- Return one recommendation, not a vague list.
- Always show the top three cross-domain recommendations before choosing the
  final recommendation.
- Always include a short `Vs Ideal` read in full-sweep mode.
- Run `python scripts/triage_facts.py --json` directly in the main thread
  during full-sweep mode unless blocked, and report the blocker if it is
  blocked.
- End with the exact `Reply yes to proceed with: ...` handoff for the chosen
  recommendation.
- Treat `doc-web` as the checkout, package, and fact JSON identity. Do not
  rewrite intentional `doc-forge` product-doc wording when it is describing the
  product surface rather than the repo/package.
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
  usually move to `Health Flags` or a lower-ranked top-three entry rather than
  become the recommended action.
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

## npm Supply-Chain Incidents

If triage involves an npm/package/dependency/CI supply-chain incident, inspect
`docs/runbooks/npm-supply-chain-hardening.md` and run the repo-local scanner:

```bash
python3 scripts/npm_supply_chain_scan.py
```

For unrelated product triage, do not run the scanner just because it exists.
