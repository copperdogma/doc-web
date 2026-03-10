# Scout 002 — cine-forge-patterns

**Source:** /Users/cam/Documents/Projects/cine-forge
**Scouted:** 2026-03-10
**Scope:** Full project — skills, docs infrastructure, AGENTS.md, eval patterns, story lifecycle
**Previous:** Scout 001 (dossier-patterns)
**Status:** Complete

## Findings

1. **AGENTS.md (400-500 lines)** — HIGH value
   What: Core directive with mandates, engineering principles, subagent strategy, definition of done, operational guide. More comprehensive than dossier's — includes model selection table, work log format, CLI invocation patterns.
   Us: No AGENTS.md. Same gap as dossier finding.
   Recommendation: Create story — use cine-forge's as primary template (more comprehensive than dossier's)

2. **Story Lifecycle System** — HIGH value
   What: Full pipeline: `create-story` → `build-story` → `validate` → `mark-story-done` with bootstrap scripts, numbered stories, status tracking (Draft/Pending/In Progress/Done/Blocked).
   Us: Have Claude commands for pieces (build-story, validate, mark-story-done) but not unified or cross-CLI.
   Recommendation: Create story — port create-story with bootstrap script, unify lifecycle

3. **Eval Registry (YAML format)** — HIGH value
   What: Same pattern as dossier but with richer structure: target metrics (value, latency_ms_max, cost_usd_max), worker vs subject model distinction, retry conditions.
   Us: Same gap as dossier finding.
   Recommendation: Adopt cine-forge's YAML format (richer than dossier's)

4. **CalVer CHANGELOG.md with Enforcement** — MEDIUM value
   What: Format: `## [YYYY-MM-DD-NN] - Summary`. Sections: Added/Changed/Fixed. `/check-in-diff` refuses commit if CHANGELOG.md not updated.
   Us: No CHANGELOG.md enforcement.
   Recommendation: Adopt inline with check-in-diff port

5. **docs/ideal.md + docs/spec.md** — HIGH value
   What: Same Ideal-First methodology as dossier, applied to film/cinema domain. Spec includes Ideal→Compromise traceability.
   Us: Same gap as dossier.
   Recommendation: Use dossier or storybook template — pattern is identical

6. **Runbook Conventions** — MEDIUM value
   What: 4 runbooks in `docs/runbooks/` with template: Context, Prerequisites, Steps (script vs judgment), Boundaries (always/ask/never), Troubleshooting, Lessons.
   Us: Same gap as dossier.
   Recommendation: Adopt cine-forge's runbook template format

7. **Makefile Targets** — LOW value
   What: `skills-sync`, `skills-check`, `check-size` targets.
   Us: No Makefile.
   Recommendation: Adopt inline — create minimal Makefile

8. **ADR System (docs/decisions/)** — LOW value
   What: Architectural Decision Records for documenting choices.
   Us: No ADRs. Decisions undocumented.
   Recommendation: Skip for now — AGENTS.md + spec.md cover most decision tracking

## Approved

- [x] 1. AGENTS.md — **Adopted** (Tier 1). Used cine-forge structure as primary template with codex-forge-specific tenets and mandates.
- [x] 2. Story Lifecycle — **Adopted** (Tier 2). Full `/create-story` → `/build-story` → `/mark-story-done` pipeline with bootstrap script.
- [x] 3. Eval Registry — **Adopted** (Tier 1). Used cine-forge's richer YAML format with target metrics, retry conditions.
- [x] 4. CHANGELOG Enforcement — **Adopted** (Tier 2). CalVer format enforced by `/check-in-diff` and `/mark-story-done`.
- [x] 5. ideal.md + spec.md — **Adopted** (Tier 1). Created both docs with 8 codex-forge-specific compromises.
- [x] 6. Runbook Template — **Adopted** (Tier 3). Created `docs/runbooks/` with crop-eval-workflow.md and golden-build.md.
- [x] 7. Makefile — **Adopted** (Tier 3). Added `skills-sync`, `skills-check`, `check-size` to existing Makefile.

## Skipped / Rejected

- 8. ADR System — Skip for now; AGENTS.md + spec.md sufficient
