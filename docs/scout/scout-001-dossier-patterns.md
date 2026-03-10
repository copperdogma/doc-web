# Scout 001 — dossier-patterns

**Source:** /Users/cam/Documents/Projects/dossier
**Scouted:** 2026-03-10
**Scope:** Full project — skills, docs infrastructure, AGENTS.md, runbooks, eval patterns
**Previous:** None
**Status:** Complete

## Findings

1. **AGENTS.md as Operational Codec** — HIGH value
   What: 266-line directive covering core mandates, eval-first discipline, architecture limits, subagent strategy, memory log. Living document updated as lessons accumulate.
   Us: No AGENTS.md. Institutional knowledge lives in sparse MEMORY.md only.
   Recommendation: Create story — adapt dossier's structure for codex-forge (4-5 hours)

2. **Ideal-First Methodology (ideal.md + spec.md)** — HIGH value
   What: `docs/ideal.md` (153 lines) defines "what would this be with perfect AI?", `docs/spec.md` (435 lines) tracks current compromises with detection evals that signal when compromises can be eliminated.
   Us: No ideal.md or spec.md. Compromises undocumented.
   Recommendation: Create story — draft ideal.md + spec.md for crop detection / OCR (6-8 hours)

3. **Eval Registry (docs/evals/registry.yaml)** — HIGH value
   What: Central YAML tracking every eval target, score history, attempt history with approach/result/retry conditions. Prevents re-trying failed approaches, enables structured improvement.
   Us: Eval scores scattered in MEMORY.md notes. No centralized registry, no attempt history.
   Recommendation: Create story — scaffold registry.yaml, migrate current scores (2-3 hours)

4. **Eval-First Gate in /build-story** — HIGH value
   What: Before implementing, establish baseline eval. Test simplest approach first. Record all attempts. Never conclude "AI can't do this" from a cheap model's failure.
   Us: VLM eval exists but not systematized as a build gate.
   Recommendation: Adopt inline when porting build-story skill

5. **Story Numbering + Index (docs/stories.md)** — MEDIUM value
   What: `docs/stories/story-NNN-slug.md` format with central index tracking ID/Title/Priority/Status. 60+ stories indexed.
   Us: Stories exist but no central numbered index.
   Recommendation: Create story — number existing stories, create index (2-3 hours)

6. **27 Skills Ecosystem** — MEDIUM value
   What: Full lifecycle skills: create-story, build-story, validate, mark-story-done, improve-eval, verify-eval, gap-analysis, golden-create, golden-verify, reflect, setup-*, triage-*.
   Us: 2 skills + 8 Claude-only commands.
   Recommendation: Create story — port highest-value skills (build-story, validate, mark-story-done, improve-eval, check-in-diff)

7. **Runbooks (docs/runbooks/)** — MEDIUM value
   What: Procedural guides for repeatable processes (golden-build, benchmark-gap-loop, etc.) with steps, boundaries, troubleshooting, lessons.
   Us: No runbooks directory. Process knowledge in memory only.
   Recommendation: Create story — start with crop eval and golden build runbooks

8. **Cross-CLI Skill Automation** — LOW value (already have it)
   What: `scripts/sync-agent-skills.sh` with symlinks + Gemini wrappers.
   Us: Already installed. Not yet in Makefile.
   Recommendation: Adopt inline — add `make skills-sync` and `make skills-check`

## Approved

- [x] 1. AGENTS.md — **Adopted** (Tier 1). Created `AGENTS.md` with Central Tenets, mandates, subagent strategy, story lifecycle.
- [x] 2. ideal.md + spec.md — **Adopted** (Tier 1). Created `docs/ideal.md` (58 lines) and `docs/spec.md` (87 lines, 8 compromises C1-C8).
- [x] 3. Eval Registry — **Adopted** (Tier 1). Created `docs/evals/registry.yaml` with 4 evals, score history, attempt tracking.
- [x] 4. Eval-First Gate — **Adopted** (Tier 2). Integrated into `/build-story` Phase 2, step 7.
- [x] 5. Story Numbering — **Adopted** (Tier 2). `/create-story` skill with `start-story.sh` bootstrap and story template.
- [x] 6. Port High-Value Skills — **Adopted** (Tiers 2-3). Ported: build-story, check-in-diff, mark-story-done, improve-eval, verify-eval, create-story.
- [x] 7. Runbooks — **Adopted** (Tier 3). Created `docs/runbooks/crop-eval-workflow.md` and `docs/runbooks/golden-build.md`.
- [x] 8. Makefile Integration — **Adopted** (Tier 3). Added `skills-sync`, `skills-check`, `check-size` targets to Makefile.

## Skipped / Rejected

(none)
