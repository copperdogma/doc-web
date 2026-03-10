---
name: mark-story-done
description: Validate a story is complete and update statuses safely
user-invocable: true
---

# /mark-story-done [story-number]

Close a completed story after validation.

## Inputs

- Story id, title, or path (optional if inferable from context)

## Validation Steps

1. **Resolve story file** — Read `docs/stories/story-{NNN}-*.md`.

2. **Validate completeness:**
   - [ ] All task checkboxes checked
   - [ ] All acceptance criteria met (with evidence)
   - [ ] Work log is current (no dangling "Next Steps" without resolution)
   - [ ] Dependencies addressed (if depends on other stories, are they done?)
   - [ ] Central Tenet verification checkboxes checked
   - [ ] Doc update checkbox checked
   - [ ] Project checks pass:
     - `python -m pytest tests/`
     - `python -m ruff check modules/ tests/`
   - [ ] If pipeline modules changed: tested through `driver.py` with artifacts inspected
   - [ ] If evals were run: mismatches classified, `docs/evals/registry.yaml` updated with verified scores

3. **Produce completion report:**

   **Story: [ID] - [Title]**
   - Tasks: [X/Y] complete
   - Acceptance Criteria: [X/Y] met
   - Tenets Verified: [Yes/No]
   - Evals Updated: [Yes/No/N/A]
   - Outstanding: [List items if any]

## Apply Completion

If complete (or user approves remaining gaps):

1. Set story file status to `Done`.
2. Update corresponding row in `docs/stories.md` to `Done`.
3. Append completion note to story work log with date and evidence.
4. Update CHANGELOG.md:
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

   - **CalVer**: `YYYY-MM-DD-NN` where `NN` is sequence for the day. Check previous entry to increment.
   - Only include subsections that apply.

If not complete, stop and list blockers.

## Guardrails

- Never hide gaps — always report unmet criteria explicitly
- Ask for confirmation when unresolved items remain
- Do not duplicate CHANGELOG.md entries — always check before writing
- Never mark Done without running the full check suite
- Never mark a Draft story as Done — it must be promoted to Pending and built via `/build-story` first
- If evals were run during the story: verified scores must be recorded in `docs/evals/registry.yaml` before closing
- Never commit or push without explicit user request
