# Runbook: Codebase Improvement Scout

## Context

Use this runbook when you want a recurring or on-demand repo-hygiene scan that finds high-value cleanup work without turning into noisy autonomous refactoring.

The companion skill is `/codebase-improvement-scout`.

## Prerequisites

- Repo root available and readable
- Project-native checks available: `make test`, `make lint`, `make skills-check`, and `make check-size`
- Understanding that the default mode is report-first, not auto-fix-first
- Read `AGENTS.md`, especially the story execution protocol

## Steps

1. **[script] Bootstrap the scan**
   - Run `.agents/skills/codebase-improvement-scout/scripts/start-scan.sh`
   - This creates the dated report file and initializes `docs/reports/codebase-improvement/_state.yaml` if needed

2. **[judgment] Decide the operating mode**
   - Default: report-only
   - Use `--create-story` when the goal is to turn the best finding into tracked work
   - Use `--autofix` only for narrow, behavior-preserving cleanup on a side branch
   - If the worktree is dirty and edits were not explicitly authorized, stay report-only

3. **[script] Run deterministic discovery**
   - Run repo-native checks first
   - Run optional tools only if they are already installed or configured
   - Use hotspot history and marker scans before AI judgment

4. **[judgment] Classify findings**
   - Auto-fix only if the change is mechanical, small, and verifiable
   - Draft a story for structural or architectural issues
   - Suppress or ignore low-value or intentionally accepted findings
   - Rank by leverage, not issue count

5. **[judgment] Produce the scan artifact**
   - Fill the report with top findings, evidence, and one recommended next step
   - Update `docs/reports/codebase-improvement/_state.yaml` so recurring runs do not rediscover the same accepted exceptions forever

6. **[script] Optional execution**
   - If `--create-story`: create or link one best-fit story, then follow the normal story chain
   - If `--autofix`: create a side branch, apply only narrow safe cleanup, run checks, and stop at `/check-in-diff`

## Boundaries

Always do:
- Use deterministic detectors before AI judgment
- Prefer report plus story over speculative edits
- Keep summaries short and high-signal

Ask first:
- Installing new hygiene tooling
- Editing on top of a dirty worktree
- Broad auto-fix passes
- Structural cleanup that spans multiple subsystems

Never do:
- Unconstrained "make the repo better" refactors
- Cosmetic churn
- More than 5 changed files in one auto-fix cluster
- Commit or push without explicit permission
