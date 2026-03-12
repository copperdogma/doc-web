---
name: validate
description: Assess implementation quality against story requirements and local diffs
user-invocable: true
---

# /validate [story-number]

> Decision check: If this task affects architecture, workflow, schemas, or cross-cutting project behavior, read relevant runbooks, scout docs, or notes before choosing an approach. If none apply, say so explicitly.

Assess whether a story's implementation meets its requirements.

## Steps

1. **Collect local delta first:**
   - `git status --short`
   - `git diff --stat`
   - `git diff`
   - `git ls-files --others --exclude-standard`

2. **Read the story** — Load `docs/stories/story-{NNN}-*.md`. Note the acceptance criteria, tasks, workflow gates, and work-log evidence.

3. **Check workflow gates** — If the story is missing `Workflow Gates` because it predates the newer template, add equivalent gates before continuing so the handoff state is explicit.

4. **Read context** — Read `docs/ideal.md`, the story's spec refs, and any cited decision refs or relevant runbooks, scout docs, or notes.

5. **Run the full check suite for changed scope:**
   - Default Python checks:
     - `make test`
     - `make lint`
   - If agent tooling changed:
     - `make skills-check`
   - If modules, driver logic, schemas, or recipes changed:
     - Clear relevant `*.pyc`
     - Run `make smoke` or the narrowest real `driver.py` path that proves the change
     - Inspect the resulting artifacts in `output/runs/`
   - If a command is unavailable, report it explicitly

6. **Review acceptance criteria** — For each criterion:
   - **Met** — with evidence
   - **Partial** — what remains
   - **Unmet** — what is missing or broken

7. **Review approach quality and code health:**
   - Does the implementation follow repo patterns and prior guidance?
   - Is there evidence this was the right approach for this repo, or does the diff look generic?
   - Are there simpler helpers, modules, or docs that should have been reused?
   - Did the change leave redundant code or docs behind?
   - Were `schemas.py` changes made where new artifact fields were required?
   - If pipeline behavior changed, is there explicit artifact-inspection evidence?

8. **Eval mismatch investigation** — If the story touched an AI module, scorer, golden, or eval:
   - Run the relevant evals
   - Run `/verify-eval`
   - Unclassified mismatches are a finding and the grade cannot exceed `B`
   - Ensure `docs/evals/registry.yaml` was updated with verified scores, `git_sha`, and date

9. **Check Ideal alignment** — Does the implementation move toward the Ideal or entrench a compromise? If it entrenches a compromise, is the compromise justified and still measured?

10. **Update story handoff state:**
   - Check `Validation complete or explicitly skipped by user` when validation was actually run
   - Leave `Story marked done via /mark-story-done` unchecked
   - Add a work-log note summarizing the validation outcome and the recommended next step

11. **Produce report** — Findings must explicitly call out:
   - unmet acceptance criteria or failed checks
   - missing artifact inspection for pipeline work
   - weak or unproven approach selection
   - redundant code or docs left behind
   - missing eval verification or stale registry entries
   - recommended next step (`/mark-story-done` if clean, otherwise fix issues)
   - By default, stop after the report. If the user already explicitly approved the next step and validation is clean enough to proceed, continue to `/mark-story-done` inline instead of asking again

```
## Validation Report — Story {NNN}

### Findings
- [priority: high/medium/low] description

### Checks
- make test: PASS/FAIL/NOT RUN
- make lint: PASS/FAIL/NOT RUN
- make skills-check: PASS/FAIL/NOT RUN
- pipeline verification: PASS/FAIL/NOT RUN
- missing or unavailable checks: [list]

### Acceptance Criteria
- [criterion]: Met/Partial/Unmet — evidence

### Approach Review
- chosen approach appears justified: yes/no/partial
- evidence: [repo-specific evidence or lack thereof]

### Redundancy Review
- redundant code or docs left behind: yes/no
- details: [list]

### Ideal Alignment
- moves toward Ideal: yes/no/partial
- new compromises introduced: [list, with detection-eval status]

### Grade: A/B/C/D/F

### Next Steps
- [what needs to happen before this can be marked Done]
```

## Guardrails

- Never hide gaps or inflate the grade
- Always report unmet criteria clearly
- Always include evidence for `Met` ratings
- Never mark a story `Done` from `/validate`
- Never give an `A` to pipeline work without explicit artifact-inspection evidence
- Never ignore redundant code that the new implementation clearly supersedes
- If the grade is below `B`, list concrete remediation steps
- Prefer project-native checks over generic templates
