---
name: triage-stories
description: Evaluate the story backlog and recommend what to work on next
user-invocable: true
---

# /triage-stories [story-number]

> Alignment check: Before choosing an approach, verify it aligns with `docs/ideal.md` and relevant decision records in `docs/decisions/`. If this work touches a known compromise in `docs/spec.md`, respect its limitation type and evolution path. If none apply, say so explicitly.

Canonical story-backlog triage leaf skill. Direct invocation is allowed, and
`/triage stories` routes here.

## What This Skill Produces

A short advisory report:
- ranked story recommendations
- bottlenecks / concerns
- one recommended next command

This skill is read-only.

## Steps

1. **Read project state**
   Load `docs/stories.md` and identify all stories by status:
   - Draft
   - Pending
   - In Progress
   - Done
   - Blocked

   Both Draft and Pending stories with met dependencies are candidates. Draft
   stories are recommendable but not yet buildable until promoted to `Pending`.

2. **Read the Ideal**
   Load `docs/ideal.md` and score against what the system should become, not
   just what is locally convenient.

3. **Read candidate stories and build-map context**
   For every candidate story with met dependencies, read the actual story file.
   Do not rank by title alone. For each candidate, also read the matching
   build-map category and note:
   - **Substrate status** (`exists`/`partial`/`missing`) — a story whose
     category substrate is `missing` should not be recommended unless the story
     itself creates that substrate
   - **Phase** (`climb`/`hold`/`converge`) — this determines what kind of work
     is highest leverage
   - **Input Coverage** state when the story touches inputs, filetypes,
     artifacts, or channels
   If a candidate depends on upstream architecture, schema, runtime, or
   artifact substrate, inspect the repo to verify that substrate exists in code
   and is not just asserted in story text.

4. **Score and rank**
   Evaluate each candidate on:
   - dependency readiness
   - blocking power
   - Ideal alignment
   - stage leverage
   - simplification leverage
   - **substrate readiness** — read the build-map category's substrate status;
     don't recommend stories when substrate is `missing` unless the story creates it.
     For architecture-dependent stories, prefer code-verified substrate over
     paper status alone
   - **phase coherence** — read the category's phase from the build map:
     - `climb`: recommend quality-improvement work
     - `hold`: recommend efficiency/simplification work
     - `converge`: recommend deletion work
     - Work that fights the phase is lower priority
   - momentum
   - convergence value
   - complexity vs payoff
   - user impact

5. **Flag concerns**
   Surface issues such as:
   - stories marked Draft/Pending that are actually blocked
   - stories whose documented prerequisites exist in build-map or decision docs
     but not yet in code, schemas, runtime wiring, tests, or artifacts
   - stale or superseded stories
   - claimed scope that disagrees with `docs/build-map.md`
   - bottlenecked dependency chains

6. **Return the report**

   Use this format:

   ```markdown
   ## Triage Stories

   ### Ranked Candidates
   - Story NNN — {title} ({Draft|Pending}) — {why}

   ### Bottlenecks / Concerns
   - {issue}

   ### Recommended Action
   - {one next story action}
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
- Do not recommend architecture-dependent stories as build-ready on story text
  alone when the critical substrate has not been verified in the repo
- Keep the report compact enough for `/triage` to synthesize with other leaf reports
