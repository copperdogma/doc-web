---
name: mark-story-done
description: Validate a story is complete and update statuses safely
user-invocable: true
---

# /mark-story-done [story-number]

> Decision check: If this task affects release workflow, schema compatibility, or cross-cutting project behavior, read relevant runbooks, scout docs, or notes before choosing an approach. If none apply, say so explicitly.

Close a completed story after validation.

## Inputs

- Story id, title, or path (optional if inferable from context)

## Validation Steps

1. **Resolve story file** — Read `docs/stories/story-{NNN}-*.md`.

2. **Check workflow gates first:**
   - [ ] `Build complete` is checked
   - [ ] `Validation complete or explicitly skipped by user` is checked, or the user explicitly instructed you to skip validation in this close-out request
   - [ ] `Story marked done via /mark-story-done` is still unchecked

3. **Validate completeness:**
   - [ ] All task checkboxes checked
   - [ ] All acceptance criteria met (with evidence)
   - [ ] Work log is current
   - [ ] Dependencies addressed
   - [ ] Required docs-update and tenet checkboxes checked
   - [ ] Required checks passed for changed scope:
     - `make test`
     - `make lint`
     - `make skills-check` when agent tooling changed
   - [ ] If pipeline behavior changed: `driver.py` or `make smoke` verification was run and artifacts were manually inspected
   - [ ] If evals were run: `/verify-eval` output exists in the work log and `docs/evals/registry.yaml` was updated with verified scores, `git_sha`, and date

4. **Produce completion report** — List any remaining gaps:

   **Story: [ID] - [Title]**
   - Tasks: [X/Y] complete
   - Acceptance Criteria: [X/Y] met
   - Workflow Gates: [state]
   - Tenets Verified: [Yes/No/N/A]
   - Registry Updated: [Yes/No/N/A]
   - Outstanding: [List items if any]

## Apply Completion

If complete (or user approves remaining gaps):

1. Set story file status to `Done`.
2. Check `Story marked done via /mark-story-done`.
3. If validation was explicitly skipped by the user, record that decision in the work log and check `Validation complete or explicitly skipped by user`.
4. Update corresponding row in `docs/stories.md` to `Done`.
5. Append completion note to story work log with date and evidence. End the note with the recommended next step: `/check-in-diff`.
6. Update CHANGELOG.md:
   - Search CHANGELOG.md for the story number (e.g., `Story 001`)
   - If an entry already exists, skip — do not duplicate
   - If no entry exists, prepend a new entry:

     ```
     ## [YYYY-MM-DD-NN] - Short summary (Story NNN)

     ### Added
     - ...

     ### Changed
     - ...

     ### Fixed
     - ...
     ```

   - Use today's date and derive the summary from the story goal
   - **CalVer**: `YYYY-MM-DD-NN` where `NN` is the sequence for the day. Check the previous entry to increment.
   - Only include subsections that apply.

If not complete, stop and list blockers.

## Guardrails

- Never hide gaps — always report unmet criteria explicitly
- Ask for confirmation when unresolved items remain
- Do not duplicate CHANGELOG.md entries — always check before writing
- Never mark Done without running the full check suite
- Never mark Done if pipeline work lacks explicit artifact-inspection evidence
- Never mark Done if evals were run without verified scores and mismatch classification
- Never mark a Draft story as Done — it must be promoted to Pending and built via `/build-story` first
- End with a concise summary and recommend `/check-in-diff` as the next step unless the user already approved later steps
- Never commit or push without explicit user request
