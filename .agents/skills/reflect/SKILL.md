---
name: reflect
description: Trace the downstream implications of a change across codex-forge's core docs, ADRs, stories, and evals
user-invocable: true
---

# /reflect [what-changed]

Trace the implications of a change across codex-forge's source-of-truth documents.
Read-only and advisory. This skill surfaces what likely needs attention; it does not rewrite files.

## When To Use

Use this after any change that may ripple beyond one file or one story:

- an ADR moves from research to a settled direction;
- a story or manual artifact review reveals a new architectural lesson;
- `docs/ideal.md`, `docs/spec.md`, or `docs/requirements.md` change;
- an eval or external research result suggests a compromise can be removed;
- a new model, tool, or workflow shift might invalidate older decisions;
- a pipeline slice succeeds or fails in a way that changes future planning.

`/create-adr` and ADR follow-up work should usually end with a `/reflect` pass before calling the decision fully integrated.

## What This Skill Produces

A short impact report for the user or for a work log, covering:

- vision and compromise impact;
- story and ADR impact;
- eval impact;
- concrete recommended actions.

No files are modified.

## Steps

1. **Identify the change**
   - Use the user-provided change description when available.
   - Otherwise inspect the latest relevant diff, story note, ADR note, or artifact review outcome.

2. **Read the current state**
   - `docs/ideal.md`
   - `docs/spec.md`
   - `docs/requirements.md`
   - `docs/stories.md` plus any directly affected story files
   - `docs/decisions/` for relevant ADRs
   - `docs/evals/registry.yaml`
   - `AGENTS.md` if the change might affect workflow or agent guardrails
   - optionally `docs/format-registry.md` or `docs/ai-learning-log.md` when the change affects format coverage or reusable lessons

3. **Trace implications**

   **Ideal impact**
   - Does this reveal a new ideal that is not yet explicit?
   - Does it sharpen an existing central tenet or desired end state?

   **Spec / requirements impact**
   - Does this add, remove, or change a compromise in `docs/spec.md`?
   - Does it change a requirement or detection mechanism in `docs/requirements.md`?
   - Is there now evidence that an existing compromise should be re-evaluated?

   **Story impact**
   - Are any `Draft`, `Pending`, or `In Progress` stories affected?
   - Are any `Done` stories now incomplete or mis-scoped in hindsight?
   - Should any new stories likely exist? Flag them; do not create them unless the user asks.

   **ADR / runbook / guardrail impact**
   - Does an existing ADR need discussion notes, integration updates, or closure work?
   - Does a reusable workflow need to be captured in a runbook or skill?
   - Does `AGENTS.md` need stronger or updated guidance?

   **Eval impact**
   - Should any evals be re-run, added, or removed?
   - Does this reveal a missing benchmark or detection loop?

4. **Produce the impact report**

```markdown
## Reflect — {what changed}

### Ideal
- {impact or "No change needed"}

### Spec / Requirements
- {impact or "No change needed"}

### Stories
- {affected stories, with IDs and why}

### ADRs / Runbooks / AGENTS
- {affected decision docs or operational docs}

### Evals
- {evals to re-run, create, or retire}

### Recommended Actions
- [ ] {specific action in priority order}
```

5. **Point to the next tool**
   - new or unresolved hard-to-reverse decision: `/create-adr`
   - multi-provider external research needed: `docs/runbooks/deep-research.md`
   - backlog realignment needed: `/triage-stories` or `/triage-inbox`
   - spec/ideal/requirements edits needed: update those docs directly

## Guardrails

- Read the actual docs; do not reason from memory alone.
- Keep the output short and actionable.
- If there is no meaningful downstream impact, say so explicitly.
- Do not silently create stories, ADRs, or evals while using this skill in advisory mode.
- When a change affects a settled ADR, check whether the issue is:
  - the decision itself was wrong;
  - the implementation drifted from the decision;
  - or the decision is still right but needs clearer operational guidance.
