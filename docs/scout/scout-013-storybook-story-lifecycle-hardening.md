# Scout 013 — storybook-story-lifecycle-hardening

**Source:** `/Users/cam/Documents/Projects/Storybook/storybook`
**Scouted:** 2026-04-09
**Scope:** Re-scout Storybook since 2026-03-20, focused on commits `6d1b5a6` and `ccdda3f` touching `create-story`, the story template, and `build-story` lifecycle requirements
**Previous:** Scout 010 (`dossier + storybook upgrades`, 2026-03-20)
**Status:** Complete

## Findings

1. **Blocked stories need current plan truth, not stale implementation prose** — HIGH value
   What: Storybook commit `ccdda3f` hardened both `create-story` and the story template so a blocked story's visible `## Plan` must describe the unblock path or blocker reassessment work rather than stale "proceed now" implementation steps.
   Us: Doc-web already requires canonical blocker sections, but the active `create-story` skill and story template did not explicitly require the visible plan text to track blocker truth.
   Recommendation: Adopt inline.
   Transfusion:
   Exemplar: Storybook's `create-story` convention plus its `story.md` plan placeholder and blocked-story note after `ccdda3f`.
   Invariant: A blocked story must stay readable and honest in the artifact an agent opens first; blocker truth cannot live only in side sections while the visible plan still says "build now."
   Adaptation: Keep doc-web's blocker sections in the markdown body because `scripts/methodology_graph.py` already parses and validates them there; port only the lifecycle requirement, not Storybook's frontmatter migration.
   Proof target: The local `create-story` skill and story template both tell agents to rewrite the visible plan around the unblock path whenever the story is blocked.

2. **`/build-story` should treat already-blocked stories as reassessment lines, not ordinary build candidates** — HIGH value
   What: Across `6d1b5a6` and `ccdda3f`, Storybook taught `build-story` to read blocker truth first, stop on blocked stories unless the user explicitly wants reassessment, and rewrite stale plan text when the unblock condition is still unmet.
   Us: Doc-web could mark a story `Blocked` during exploration, but it did not tell agents what to do when the selected story was already blocked or how to handle stale pre-block plans.
   Recommendation: Adopt inline.
   Transfusion:
   Exemplar: Storybook's `build-story` resolve-story and substrate-check rules after `6d1b5a6` and `ccdda3f`.
   Invariant: Blocked status is lifecycle truth, not a soft warning; build flow must require fresh unblock evidence before resuming work.
   Adaptation: Use doc-web's existing `Blocker Summary` / `Blocker Evidence` / `Unblock Condition` body sections instead of Storybook's frontmatter fields, and keep the repo's graph/state framing intact.
   Proof target: The local `build-story` skill now handles `Blocked` as a first-class state, rewrites stale blocked plans when necessary, and records the unmet line as a health flag instead of continuing blindly.

3. **Storybook's blocker frontmatter fields are not an inline fit here** — LOW value
   What: Commit `6d1b5a6` moved `blocker_summary`, `blocker_evidence`, and `unblock_condition` into Storybook story frontmatter.
   Us: Doc-web's compiler already parses and validates blocker truth from the markdown body sections, and the existing story corpus uses that contract.
   Recommendation: Skip for now.

## Approved

- [x] 1. Blocked stories need current plan truth, not stale implementation prose — Adopted inline
- [x] 2. `/build-story` should treat already-blocked stories as reassessment lines, not ordinary build candidates — Adopted inline

## Skipped / Rejected

- 3. Storybook blocker frontmatter fields — skipped because doc-web's current compiler and story corpus already use canonical blocker body sections; porting the lifecycle requirement did not require a schema migration.

## Verification

- `make methodology-compile`
- `make methodology-check`
- `make skills-check`
- `python -m pytest tests/test_methodology_graph.py -q`
- `git diff --check`

## Evidence

- [create-story skill](/Users/cam/.codex/worktrees/73ab/doc-web/.agents/skills/create-story/SKILL.md) now requires blocked stories to keep the visible `## Plan` aligned with the unblock path or reassessment work.
- [build-story skill](/Users/cam/.codex/worktrees/73ab/doc-web/.agents/skills/build-story/SKILL.md) now treats `Blocked` as a first-class entry state, requires fresh unblock evidence before continuing, and tells agents to rewrite stale blocked plans when blocker truth changes.
- [story template](/Users/cam/.codex/worktrees/73ab/doc-web/.agents/skills/create-story/templates/story.md) now teaches blocked-story lifecycle truth directly in the template note and `## Plan` placeholder without changing doc-web's existing blocker-section parser contract.
