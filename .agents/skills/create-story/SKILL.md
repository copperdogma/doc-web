---
name: create-story
description: Scaffold a numbered story file and update the story index
user-invocable: true
---

# /create-story [title]

> Alignment check: Before choosing an approach, verify it aligns with `docs/ideal.md`, `docs/build-map.md`, and relevant decision records in `docs/decisions/`. If this work touches a known compromise in `docs/spec.md`, respect its limitation type and evolution path. If none apply, say so explicitly.

Create a new story in `docs/stories/` with consistent format.

## Inputs

- `title`: human-readable story title
- `slug`: kebab-case slug (derived from title if not provided)
- `priority`: High / Medium / Low (default: Medium)
- `ideal_refs`: ideal.md requirements this story serves
- `spec_refs`: relevant spec.md sections or compromise numbers
- `decision_refs`: relevant ADRs, runbooks, scout docs, notes, or other decision docs (or `None found after search`)
- `depends_on`: story IDs this depends on (if any)
- `status`: Draft or Pending (default: Draft)
  - **Draft** — skeleton with goal and notes but not ready to build
  - **Pending** — fully detailed ACs, tasks, workflow gates, and files to modify

## Steps

1. **Run the bootstrap script:**

   ```bash
   .agents/skills/create-story/scripts/start-story.sh <slug> [priority]
   ```

   This creates `docs/stories/story-NNN-<slug>.md` from the template with the next available number.

2. **Fill in the story file** — Replace all placeholder text (`{...}`) with real content:
   - Title (replace the slug with human-readable title)
   - Goal, acceptance criteria, out of scope, tasks, files to modify
   - Ideal refs, spec refs, decision refs, and dependencies
   - Build-map context: relevant category, current substrate, current phase,
     and any relevant `Input Coverage` rows if the story touches formats or artifacts
   - Approach evaluation: candidate approaches, repo constraints, existing patterns to reuse, and what eval distinguishes them
   - Workflow Gates
   - Redundancy or removal targets
   - Architectural Fit notes
   - For architecture-dependent work, inspect the relevant code, schema,
     runtime, or artifact substrate and record what was verified versus assumed.
     If the critical substrate is missing, either add the prerequisite explicitly
     or keep the story in `Draft` instead of promoting it to `Pending`

3. **Ideal alignment check** — Before writing the story, read `docs/ideal.md`:
   - Does this story close an Ideal gap? → proceed
   - Does it move AWAY from the Ideal? → STOP, push back, recommend alternative
   - Does it only optimize a compromise without closing a gap? → flag as low-value, confirm with user
   - If introducing a new AI compromise: note whether a detection eval exists

4. **Build-map reality check** — Before marking a story `Pending`:
   - Read the relevant category in `docs/build-map.md`
   - If the story touches formats or artifacts, read the relevant rows under
     `## Input Coverage`
   - Confirm whether the substrate the story depends on actually exists in the repo
   - If the substrate is unverified or missing, keep the story as `Draft` or
     add the prerequisite instead of treating paper readiness as real readiness

5. **Update story index** — Add a row to the story table in `docs/stories.md`:
   `| NNN | Title | Priority | Draft | /docs/stories/story-NNN-slug.md |`
   Match the existing table format and nearby ordering conventions. Do not rewrite the entire index.

6. **Verify** — Confirm the file exists, the new story ID is unique and uses
   the next available number (`max + 1`), and the `docs/stories.md` row is
   correct.

## Story Statuses

- **Draft** — Goal and notes exist, but acceptance criteria or tasks are still incomplete
- **Pending** — Fully detailed and ready for `/build-story`
- **In Progress** — Being built
- **Done** — Validated and closed
- **Blocked** — Waiting on dependency or decision

## Conventions

- Every story must trace to an Ideal requirement or spec compromise. Stories without lineage are untraceable scope.
- Acceptance criteria must be testable and concrete.
- Always include the Approach Evaluation section — list candidates without pre-deciding. Approach selection happens during `/build-story`.
- `Pending` means buildable in implemented reality, not just plausible on paper.
  If critical substrate is unverified or missing, use `Draft` or add an
  explicit prerequisite.
- **Simplification baseline gate**: Every story involving new logic must answer: "Can a single LLM call already do this?" If untested, first task = measure the baseline.
- Search `docs/build-map.md`, `docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for prior decisions or constraints while drafting. If none apply, say so explicitly.
- If the story raises a new unresolved architecture, workflow, or schema question, either cite the missing ADR need explicitly or recommend creating one before implementation starts.
- If the story touches input formats, format families, or output artifacts, use
  the current `docs/build-map.md` `Input Coverage` reality when writing the
  goal, acceptance criteria, tasks, and notes.
- Filetype-aware stories should usually include:
  - the current coverage row or gap they address
  - the target change in coverage or graduation readiness
  - a task to update `docs/build-map.md` if shipped behavior changes the documented reality
- If the story changes pipeline, module, driver, schema, or recipe behavior, include a task for real `driver.py` verification and artifact inspection in `output/runs/`.
- If the story changes agent tooling or project instructions, include `make skills-check` in the task list.
- If the story will run evals, include a task to run `/improve-eval` and update `docs/evals/registry.yaml`.
- Always include the Workflow Gates section. These gates enforce the handoff chain: `/build-story` → `/validate` → `/mark-story-done`.
- If the story supersedes existing code or docs, name likely removal targets up front instead of silently accumulating parallel paths.
- "Files to Modify" is gold for AI agents — fill it in when known.
- Story IDs are identifiers, not sequence numbers. New stories get max+1. Never use letter suffixes.

## Work Log Entry Format

```
YYYYMMDD-HHMM — action: result, evidence, next step
```

## Guardrails

- Never overwrite an existing story file — the script will error
- Never commit or push without explicit user request
- Story IDs are identifiers, not sequence numbers. Gaps are expected; use the
  next available id (`max + 1`), verify there are no duplicates, and never use
  letter suffixes
