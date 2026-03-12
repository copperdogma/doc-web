---
name: triage-stories
description: Evaluate the story backlog and recommend what to work on next
user-invocable: true
---

# /triage-stories [story-number]

> Decision check: If this task affects backlog policy, workflow, or cross-cutting project behavior, read relevant runbooks, scout docs, or notes before choosing an approach. If none apply, say so explicitly.

Evaluate the story backlog and recommend the best next stories to work on.

## Arguments

- `[story-number]` — optional. If provided, assess that specific story's readiness instead of doing a full backlog scan.

## Steps

1. **Read project state** — Load `docs/stories.md`. Identify all stories by status:
   - **To Do / Draft** — scoped but may need detailed ACs and tasks before building
   - **Pending** — fully detailed, ready to build
   - **In Progress** — currently being worked on
   - **Done** — complete, validated
   - **Won't Do** — decided against
   - **Blocked** — waiting on dependency or decision

   Both **Draft/To Do** and **Pending** stories with all dependencies met are candidates for recommendation.

2. **Read the Ideal** — Load `docs/ideal.md`. This is the scoring rubric.

3. **Handle focused mode if requested** — If `[story-number]` was provided:
   - Read that story file
   - Assess whether it has clear acceptance criteria, tasks, workflow gates, and satisfied dependencies
   - Report whether it is ready for `/build-story`, needs promotion, or needs more scoping
   - Stop after the readiness assessment

4. **Read candidate stories** — For every candidate story, read the actual story file to understand its goal, acceptance criteria, dependencies, and scope. Do not rank by title alone.

5. **Ideal alignment check** — For each candidate, answer:
   - Does it close an Ideal gap?
   - Does it move away from the Ideal?
   - Does it optimize a limitation that may be shrinking on its own?
   - Is it building for stages or infrastructure that do not yet exist?

6. **Check spec compromises** — Read `docs/spec.md`. If a candidate story depends on a compromise persisting, consider whether the compromise's detection eval should be re-run before building the story.

7. **Score and rank** — Evaluate each surviving candidate on:
   - Ideal gap severity
   - Dependency readiness
   - Blocking power
   - Phase coherence
   - Momentum
   - Complexity versus payoff
   - Whether re-measurement should happen before implementation

8. **Present recommendations** — Ranked top 3-5 with rationale and caveats.

9. **Flag concerns** — Surface stale stories, missing dependencies, bottlenecked chains, and stories that probably should be discarded.

10. **User decides** — Wait for the user to pick. Do not start building.

## Guardrails

- This is a read-only, advisory skill — do not modify any files
- Always read the actual story files, not just the index titles
- If the backlog is empty or everything is blocked, say so clearly
- If a specific story ID was provided, answer that readiness question directly instead of forcing a full backlog scan
