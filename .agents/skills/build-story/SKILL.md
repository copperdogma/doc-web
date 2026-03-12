---
name: build-story
description: Execute a story from planning through implementation with gated handoff discipline
user-invocable: true
---

# /build-story [story-number]

> Decision check: If this task affects architecture, workflow, schemas, or cross-cutting agent behavior, read the relevant docs in `docs/runbooks/`, `docs/scout/`, `docs/notes/`, and any future decision-doc directories before choosing an approach. If none apply, say so explicitly.

Execute a development story through implementation, then hand it off cleanly to `/validate`.

## Phase 1 — Explore (story-file edits allowed, code changes forbidden)

1. **Resolve story** — Read `docs/stories/story-{NNN}-*.md` (or resolve from `docs/stories.md`). Verify status is `Pending` or `In Progress`. If status is `Draft`, STOP and tell the user it needs detailed acceptance criteria and tasks before it can be built.

2. **Verify required sections** — Ensure the story has usable:
   - Goal
   - Acceptance Criteria
   - Tasks
   - Workflow Gates
   - Work Log
   If tasks or workflow gates are missing, add actionable checkboxes without discarding existing intent.

3. **Read context** — Read `docs/ideal.md` first, then all spec refs, dependency stories, and referenced docs. If the story does not cite prior decisions but the work touches architecture, workflow, schemas, or agent behavior, search relevant runbooks, notes, and scout docs instead of assuming none exist.

4. **Ideal Alignment Gate** — Before exploring code, verify this story moves toward the Ideal:
   - Does this story close an Ideal gap? → proceed
   - Does it move AWAY from the Ideal? → STOP, tell user to re-evaluate
   - Does it optimize a compromise without closing a gap? → flag as potentially low-value
   - Does it optimize a limitation that may be shrinking on its own? → flag as potentially premature
   - If introducing a new AI compromise: note whether a detection eval exists or should be created

5. **Explore the codebase actively** — Don't just read what's listed. Trace the code:
   - Follow call graphs from every entry point the story touches
   - Find every file that will need to change
   - Find every file that could break
   - Identify existing patterns and conventions to match
   - Identify helpers, modules, or docs this change could make redundant
   - Note schema, config, or migration concerns

6. **Record exploration findings** — Write a brief `Exploration Notes` entry in the work log:
   - Files that will change
   - Files at risk of breaking
   - Patterns and prior docs to follow
   - Potential cleanup targets
   - Any surprises or risks found

## Phase 2 — Plan (produces a written artifact)

7. **Eval-first approach gate** — Before planning implementation, establish how success will be measured:
   - **What eval?** Identify or create a test that measures success. Even a minimal fixture plus assertion counts.
   - **What's the baseline?** Run the eval against current code. Document the number.
   - **What are the candidate approaches?** For tasks involving reasoning, language, or understanding: enumerate AI-only, hybrid, and pure code. If the story pre-decided an approach without evidence, challenge it.
   - **Test the simplest first.** Often a single model call. If it works, do not build orchestration for a solved problem.
   - For pure orchestration, storage, validation, or tooling: code is obviously simpler.

8. **Repo-fit gate** — Before writing the plan, prove the chosen approach fits this repo:
   - Cite project evidence from `docs/ideal.md`, `docs/spec.md`, prior stories, runbooks, scout findings, and existing code patterns
   - State why the main alternatives were rejected here
   - If you cannot produce repo-specific evidence, do more research instead of calling the plan optimal

9. **Structural health check** — Before writing the plan:
   - Run `make check-size` or `wc -l` on each file in `Files to Modify`
   - If any file is over 500 lines: note it explicitly in the plan and consider an extraction step first
   - If any function or method to be modified is over 100 lines: first task should be extracting it into a testable unit
   - If new data crosses an artifact boundary, add the schema task before the consuming code

10. **Write the implementation plan** — Add a `## Plan` section to the story with:
   - For each task: which files change, what changes, in what order
   - Impact analysis: what tests are affected, what could break
   - Repo-fit evidence
   - Structural health findings
   - Redundancy plan: what old code, helper paths, or docs should be removed if the new path lands
   - Human-approval blockers: new dependencies, schema changes, costful evals, or model choices requiring live verification
   - What "done" looks like for each task

11. **Human gate** — Present the plan to the user. Surface ambiguities and risks. Do not write implementation code until approved.

## Phase 3 — Implement

12. **Implement** — Work through tasks in order. For each task:
   - If the story status is `Pending`, set it to `In Progress` in both the story file and `docs/stories.md` before implementation starts
   - Mark the task as in progress in the story file
   - Do the work
   - Run relevant narrow checks after meaningful changes
   - Mark the task complete with brief evidence

13. **Static verification** — Run the project's native checks for changed scope:
   - Default Python checks: `make test` and `make lint`
   - If only agent tooling changed: also run `make skills-check`
   - Review each acceptance criterion: is it actually met?

14. **Eval mismatch investigation** — If the story touched an AI module, scorer, golden, or eval:
   - Run the relevant evals
   - Use `/verify-eval` to classify every mismatch as `model-wrong`, `golden-wrong`, or `ambiguous`
   - Re-assess acceptance criteria against verified scores
   - Update `docs/evals/registry.yaml` with verified scores, `git_sha`, and date

15. **Integration verification** — If modules, driver logic, schemas, recipes, or pipeline behavior changed:
   - Clear stale Python cache for touched modules: `find modules/<module-or-stage> -name "*.pyc" -delete`
   - Run through `driver.py` or `make smoke`, using the narrowest real pipeline path that proves the change
   - Verify artifacts exist in `output/runs/`
   - Manually inspect the produced JSON/JSONL artifacts for correctness and note concrete evidence in the work log
   - If the change is doc or skill-only, say so explicitly and skip this step

16. **Update docs** — Search all docs and update anything related to what was touched.

17. **Verify Central Tenets** — Check each tenet checkbox in the story:
   - T0 — Traceability
   - T1 — AI-First
   - T2 — Eval Before Build
   - T3 — Fidelity
   - T4 — Modular
   - T5 — Inspect Artifacts

18. **Update work log** — Add a dated entry: what was done, decisions made, evidence, blockers, and next step.

19. **Implementation handoff** — Do not close the story here:
   - Check `Build complete`
   - Leave `Validation complete or explicitly skipped by user` unchecked
   - Leave `Story marked done via /mark-story-done` unchecked
   - Leave the story status as `In Progress`
   - Give the user a concise implementation summary, note any residual risks, and recommend `/validate`
   - If the user already explicitly approved the next step and the work is ready, continue to `/validate` inline instead of stopping

## Work Log Format

```
YYYYMMDD-HHMM — action: result, evidence, next step
```

Entries should be verbose. Capture decisions, failures, solutions, and learnings. These are build artifacts — any future AI session should be able to pick up context from the log.

## Guardrails

- Never write implementation code before the human gate (step 11)
- Never skip acceptance criteria verification
- Never claim an approach is optimal without repo-specific evidence
- Never leave obvious redundant code or docs in place without either removing them or recording a concrete follow-up
- Never mark a story `Done` from `/build-story` — story closure belongs to `/mark-story-done`
- Never mark Build complete if relevant checks or artifact inspection were skipped
- Never proceed past eval work while mismatches remain unclassified
- Never commit without explicit user request
- Always update the work log, even for partial progress
- If blocked, record the blocker and stop — don't guess
