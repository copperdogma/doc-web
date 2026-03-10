# Scout 003 — storybook-patterns

**Source:** /Users/cam/Documents/Projects/Storybook/storybook
**Scouted:** 2026-03-10
**Scope:** Full project — skills, docs infrastructure, AGENTS.md, Ideal-First methodology, story discipline
**Previous:** Scouts 001-002 (dossier, cine-forge)
**Status:** Complete

## Findings

1. **Canonical Skills Architecture (28 skills)** — HIGH value
   What: `.agents/skills/` as single source of truth with symlinks from `.claude/skills`, `.cursor/skills`, `skills/`. Gemini wrappers auto-generated. Most mature implementation of the cross-CLI pattern.
   Us: Just installed this pattern. Need to migrate 8 existing `.claude/commands/` to `.agents/skills/`.
   Recommendation: Create story — migrate existing commands to canonical skills format

2. **AGENTS.md (339 lines) with AI Learning Log** — HIGH value
   What: Central Tenets (vision-level + compromise-level), model selection by task type, code conventions (200-600 line files, max 3 layers), session protocol, Known Pitfalls, AI Learning Log (Effective Patterns + Known Pitfalls discovered across sessions).
   Us: No AGENTS.md. The AI Learning Log is unique to storybook — institutional memory for AI sessions.
   Recommendation: Create story — use storybook's AI Learning Log pattern in codex-forge's AGENTS.md

3. **Ideal-First Methodology (most mature)** — HIGH value
   What: `docs/ideal.md` + `docs/retrofit-gaps.md` + `docs/methodology-ideal-spec-compromise.md`. Compromises have detection evals. `/retrofit-ideal` skill for bootstrapping.
   Us: No ideal/spec docs. Storybook has the most documented version of this methodology.
   Recommendation: Use storybook's methodology doc as reference; adapt ideal.md structure

4. **Central Tenet Verification in Stories** — HIGH value
   What: Every story includes a Central Tenets Verification checklist with evidence/reasoning per tenet.
   Us: No tenet verification in stories.
   Recommendation: Adopt inline — add tenet checklist to story template once tenets are defined

5. **CalVer CHANGELOG Enforcement** — MEDIUM value
   What: `## [YYYY-MM-DD-NN] - Summary`, Added/Changed/Fixed. `/check-in-diff` refuses commit without CHANGELOG.
   Us: Same as cine-forge finding.
   Recommendation: Port with check-in-diff skill

6. **Story Status Taxonomy** — MEDIUM value
   What: Draft (no ACs/tasks) → Pending (ready to build) → In Progress → Done → Blocked.
   Us: Status conventions informal.
   Recommendation: Adopt inline — document in AGENTS.md

7. **Work Log Discipline** — MEDIUM value
   What: Every story has `## Work Log` with dated entries: Completed, Blockers, Next.
   Us: Work logs vary in discipline.
   Recommendation: Adopt inline with mark-story-done port

8. **Story Numbering Rule** — LOW value
   What: IDs are identifiers not sequence numbers. max+1. No letter suffixes.
   Us: Already follows this implicitly.
   Recommendation: Adopt inline — document in AGENTS.md

9. **CLAUDE.md One-Liner** — LOW value
   What: Single line pointing to AGENTS.md.
   Us: No CLAUDE.md.
   Recommendation: Adopt inline — trivial after AGENTS.md exists

10. **GitHub Actions (Operational Only)** — SKIP
    What: Daily DB backups only. Explicitly not for CI.
    Us: Not needed.
    Recommendation: Skip

## Approved

- [x] 1. Migrate Commands to Canonical Skills — **Adopted** (Tier 1). All 8 commands migrated to `.agents/skills/`, synced via `sync-agent-skills.sh`.
- [x] 2. AGENTS.md with AI Learning Log — **Adopted** (Tier 1). Created AGENTS.md with Central Tenets (T0-T5), mandates, subagent strategy. AI Learning Log section included.
- [x] 3. Ideal-First Methodology — **Adopted** (Tier 1). Created `docs/ideal.md` and `docs/spec.md` using storybook's methodology as reference.
- [x] 4. Central Tenet Verification — **Adopted** (Tier 2). Story template includes T0-T5 verification checklist. `/build-story` and `/mark-story-done` enforce it.
- [x] 5. CHANGELOG Enforcement — **Adopted** (Tier 2). CalVer format in `/check-in-diff` and `/mark-story-done`.
- [x] 6. Story Status Taxonomy — **Adopted** (Tier 2). Draft→Pending→In Progress→Done→Blocked documented in AGENTS.md.
- [x] 7. Work Log Discipline — **Adopted** (Tier 2). Story template and `/build-story` enforce work log entries.
- [x] 8. Story Numbering Rule — **Adopted** (Tier 2). `/create-story` bootstrap script uses max+1.
- [x] 9. CLAUDE.md One-Liner — **Adopted** (Tier 1). Created `CLAUDE.md` pointing to `AGENTS.md`.

## Skipped / Rejected

- 10. GitHub Actions — Not needed
