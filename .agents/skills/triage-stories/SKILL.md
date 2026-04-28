---
name: triage-stories
description: Evaluate the story backlog and recommend what to work on next
user-invocable: true
---

# /triage-stories [story-number]

> Alignment check: Before choosing an approach, verify it aligns with `docs/ideal.md` and relevant decision records in `docs/decisions/`. If this work touches a known compromise in `docs/spec.md`, respect its limitation type and evolution path. If none apply, say so explicitly.

Canonical story-backlog triage leaf skill. Direct invocation is allowed, and
`/triage stories` routes here.

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

## What This Skill Produces

A short advisory report:
- ranked problem-line recommendations
- bottlenecks / concerns
- one recommended next command

This skill is read-only.

## Lane Packet Mode

When the full `/triage` orchestrator asks for a lane packet, stay read-only and
do not choose the repo-wide recommendation. Return up to three neutral story or
problem-line candidates from the story domain, including:

- candidate name and story ID or grouped problem line
- Ideal promise and spec/state/coverage refs
- evidence from `docs/methodology/graph.json`, the generated `docs/stories.md`
  projection, story files, state, coverage matrix, and recent work
- why now, including blocker or retry-trigger truth
- suggested action shape: `continue`, `reopen`, `expand`, `consolidate`,
  `promote`, `start`, or `health flag only`
- whether the candidate is story-worthy or too small for a new story
- validation or stop condition
- blockers, stale evidence, and reasons not to do it now

The main `/triage` thread owns cross-domain ranking. Do not over-focus on a
single broad gap supplied by the orchestrator if story evidence shows another
story-domain candidate is stronger. In lane-packet mode, return candidates and
stop conditions; reserve the direct `### Recommended Action` winner for direct
leaf invocation.

## Steps

1. **Read project state**
   Load `docs/methodology/graph.json` (and the generated `docs/stories.md` if
   helpful) and identify all stories by status:
   - In Progress
   - Pending
   - Draft
   - Blocked
   - Done

   Candidate work lines are not just backlog shells. Read:
   - active `In Progress` stories with unresolved work
   - `Pending` stories with met dependencies
   - `Draft` stories that appear detailed enough to be promoted soon
   - `Blocked` stories only when unblocking them may be the highest-leverage move

   Status and graph actionability make a story eligible for review; they do not
   prove that the story is a distinct problem line rather than a fragment of a
   recent same-line story.

   For `Blocked` stories, do not stop at the status label. Read the blocker
   summary, blocker evidence, and unblock condition. A blocked story only stays
   in the candidate set when the current pass has fresh evidence that the
   unblock condition is now met or is immediately satisfiable by the proposed
   next action. Otherwise treat it as a health flag, not as a ranked next move.

   Draft/Pending existence alone does not make a story high priority.

   If the backlog shells are quiet but the methodology state still has active
   `converge`, `climb`, or meaningful `hold` pressure, do not stop at "no open
   stories." Identify the strongest problem line and consider whether the
   honest recommendation is to create a new story shell for it.

2. **Read the Ideal**
   Load `docs/ideal.md` and score against what the system should become, not
   just what is locally convenient.

3. **Read candidate stories and graph/state context**
   For every candidate with met dependencies or strong continuity relevance,
   read the actual story file. Do not rank by title alone. When multiple recent
   stories touch the same subsystem, validation boundary, and success surface,
   treat them as one problem line first and ask whether the honest next move is
   to continue, reopen, expand, or consolidate that line instead of treating
   each story shell as a separate vote.

   Use concrete fragment checks, not just title similarity. If the work keeps
   the same owning module, fixture family, emitted artifact chain, and
   operator-facing outcome, then differences like entry-form parity, later-
   state progression, or tests/docs/truth-surface codification are usually
   still the same problem line.
   Treat pure input/container permutations the same way unless the container
   introduces a new routing/provenance seam, downstream continuation shape, or
   validation boundary.

   If the current problem line is `Blocked`, verify whether the blocker still
   stands. A stale implementation plan inside the story does not override newer
   blocker evidence or an unmet unblock condition.

   For each candidate, also read the matching graph/state category and note:
   - **Substrate status** (`exists`/`partial`/`missing`) — a story whose
     category substrate is `missing` should not be recommended unless the story
     itself creates that substrate
   - **Phase** (`climb`/`hold`/`converge`) — this determines what kind of work
     is highest leverage
   - **Coverage matrix** state when the story touches inputs, filetypes,
     artifacts, or channels
   If a candidate depends on upstream architecture, schema, runtime, or
   artifact substrate, inspect the repo to verify that substrate exists in code
   and is not just asserted in story text.

4. **Score and rank**
   Evaluate each candidate on:
   - Ideal alignment
   - real problem pressure
   - dependency readiness
   - blocking power
   - stage leverage
   - simplification leverage
   - **substrate readiness** — read the graph/state category's substrate status;
     don't recommend stories when substrate is `missing` unless the story creates it.
     For architecture-dependent stories, prefer code-verified substrate over
     paper status alone
   - **phase coherence** — read the category's phase from methodology state:
     - `converge`: default pressure to delete, simplify, or collapse residue
     - `climb`: default pressure to improve quality, widen proof, or land the
       next advancement toward `hold`
     - `hold`: lower but still real pressure for efficiency, simplification,
       thinner ownership, or operational hardening when stronger lines are not
       actionable
     - Work that fights the phase is lower priority
     - Lack of a fresh bug report does not zero out a phase-aligned candidate
   - **blocked-state honesty** — a blocked line with an unmet unblock condition
     should lose to an actionable line even if continuity and problem pressure
     are high
   - momentum
   - continuity for active unresolved work lines
   - convergence value
   - complexity vs payoff
   - user impact
   - existing story-shell presence only as packaging / tie-break context

5. **Flag concerns**
   Surface issues such as:
   - same-surface work accidentally split across multiple stories that should
     likely stay one line
   - recent parity or later-state stories that should have been an
     expansion/reopen/consolidation of the prior line instead of a new ID
   - stories marked Draft/Pending that are actually blocked
   - blocked stories with weak or missing blocker evidence / unblock conditions
   - blocked stories whose older plan text or stale assumptions still imply a
     ready next move even though the current blocker says not to reopen yet
   - stories whose documented prerequisites exist in decision docs or older planning notes
     but not yet in code, schemas, runtime wiring, tests, or artifacts
   - stale or superseded stories
   - claimed scope that disagrees with the compiled graph/state reality
   - bottlenecked dependency chains

6. **Return the report**

   Use this format:

   ```markdown
   ## Triage Stories

   ### Ranked Problem Lines
   - Story NNN — {title} ({Status}) — recommended action: {continue|reopen|expand|consolidate|create} — {why}

   ### Bottlenecks / Concerns
   - {issue}

   ### Lane Packet
   - {candidate + Ideal/spec value + why now + action shape + stop condition}

   ### Recommended Action
   - {one next story action; direct leaf invocation only, omit in lane-packet mode}
   ```

7. **User decides**
   Wait for the user to pick a story or ask for more detail. Do not start
   building; that's `/build-story`.

## Arguments

If the user passes a story ID, evaluate only that story's readiness instead of
doing a full backlog scan. Report:
- dependency status
- blocking power
- build readiness
- verified substrate readiness where relevant
- concerns / missing prerequisites

## Guardrails

- Read-only and advisory — never modify files
- Always read the actual story files, not just the index titles
- If the backlog is empty or everything is blocked, say so clearly
- Do not recommend stories that depend on unfinished work unless the dependency
  is trivially close to done
- Do not recommend a new story when continuing, reopening, expanding, or
  consolidating the current problem line is the more honest move
- Treat entry-form parity, later-state progression, and tests/docs/truth-
  surface codification on the same module/artifact line as consolidation
  pressure by default, not as automatic new-story evidence
- Treat new `format × container × entry-surface` permutations on an already-
  supported module/artifact line as consolidation pressure by default too,
  unless the repo evidence shows that the container changes the behavior class
  or validation boundary
- Do not say the backlog is effectively empty when the methodology state still
  shows a bounded actionable `converge`/`climb` pressure line that simply lacks
  a story shell; recommend creating the story instead.
- Do not recommend architecture-dependent stories as build-ready on story text
  alone when the critical substrate has not been verified in the repo
- Treat `Blocked` stories as candidates only when the unblock path is itself the
  highest-leverage next move
- Do not recommend reopening a blocked story when the current pass only repeats
  previously failed evidence or when the story's own unblock condition is still
  unmet
- `No actionable story` is only honest when every plausible phase-aligned move
  is blocked, exhausted, or not yet specific enough to package as a bounded
  story.
- Keep the report compact enough for `/triage` to synthesize with other leaf reports
