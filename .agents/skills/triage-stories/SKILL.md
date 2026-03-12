---
name: triage-stories
description: Evaluate the story backlog and recommend what to work on next
user-invocable: true
---

# /triage-stories

Evaluate the story backlog and recommend the best next stories to work on.

## Steps

1. **Read project state** — Load `docs/stories.md` (the full story index). Identify all stories by status:
   - **To Do / Draft** — scoped but may need detailed ACs and tasks before building
   - **Pending** — fully detailed, ready to build
   - **In Progress** — currently being worked on
   - **Done** — complete, validated
   - **Won't Do** — decided against
   - **Blocked** — waiting on dependency or decision

   Both **Draft/To Do** and **Pending** stories with all dependencies met are candidates
   for recommendation. Do not treat incomplete scoping as a disqualifier — priority and
   Ideal alignment matter more. `/build-story` will flesh out ACs and tasks before
   touching code regardless of starting status.

2. **Read the Ideal** — Load `docs/ideal.md`. Identify the concrete requirements and
   vision-level preferences. These are the scoring rubric — every story is evaluated
   against them.

3. **Read candidate stories** — For every candidate story, read the actual story file
   to understand its goal, acceptance criteria, dependencies, and scope. Don't just go
   by titles.

4. **Ideal alignment check (mandatory)** — For each candidate story, answer:
   - **Does it close an Ideal gap?** Compare current pipeline capabilities against
     Ideal requirements. Stories that close a gap rank highest.
   - **Does it move AWAY from the Ideal?** Stories that reduce completeness, add
     complexity the Ideal wants eliminated, or optimize a compromise rather than
     closing a gap should be flagged for trashing. A story that entrenches a
     compromise (e.g., "extract less to save money" when the Ideal says "fidelity
     to source") is moving the wrong direction regardless of its priority label.
   - **Does it optimize a limitation that's shrinking on its own?** Model costs
     drop, context windows grow, capabilities improve. If a story builds machinery
     to work around a limitation that may resolve itself, flag it as premature.
   - **Is it building for stages that don't exist yet?** Optimizing downstream
     processing that hasn't been built is speculative engineering. Flag as premature.

5. **Check spec compromises** — Read `docs/spec.md`. For each active compromise, check
   if any candidate story's value proposition depends on the compromise persisting. If
   the compromise's detection eval might now pass (new models, recent improvements),
   recommend re-running the eval before building the story.

6. **Score and rank** — Evaluate each surviving candidate on:
   - **Ideal gap severity**: How far is the current pipeline from the Ideal on this dimension?
   - **Dependency readiness**: Are all upstream stories Done?
   - **Blocking power**: How many other stories depend on this one?
   - **Phase coherence**: Does it continue the current phase or require a context switch?
   - **Momentum**: Does it build on recently completed work?
   - **Complexity vs. payoff**: Is the effort proportional to the value?
   - **Measure-first candidates**: Stories addressing problems that may already be solved
     by recent work should recommend re-measurement before building.

7. **Present recommendations** — Ranked top 3-5 with rationale and caveats.

8. **Flag concerns** — Stale stories, missing dependencies, bottlenecked chains.
   Explicitly recommend trashing stories that move away from the Ideal.

9. **User decides** — Wait for the user to pick. Do NOT start building.

## Guardrails

- This is a read-only, advisory skill — do not modify any files
- Always read the actual story files, not just the index titles
- If the backlog is empty or everything is blocked, say so clearly
