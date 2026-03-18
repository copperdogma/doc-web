# Scout 009 — cross-repo-skill-sync

**Source:** /Users/cam/Documents/Projects/cine-forge and /Users/cam/Documents/Projects/dossier
**Scouted:** 2026-03-18
**Scope:** Re-scout sibling skills requested by the user: confirm whether `discover-models` from cine-forge still needs adoption, then import `finish-and-push` from dossier if it is still missing
**Previous:** Scout 001 (dossier-patterns), Scout 008 (cine-forge-model-skill)
**Status:** Complete

## Findings

1. **`discover-models` from cine-forge is already in sync for codex-forge's needs** — MEDIUM value
   What: Cine-forge's `discover-models` skill remains a single-file skill focused on `scripts/discover-models.py`.
   Us: Codex-forge already adopted it in Scout 008. The only current diff is intentional local adaptation: codex-forge-specific alignment wording, plain `python` commands instead of `.venv/bin/python`, and local punctuation/style normalization.
   Recommendation: Skip code changes and record that the requested source is already present.

2. **`finish-and-push` from dossier adds a missing workflow orchestrator** — HIGH value
   What: Dossier has a dedicated wrapper skill that sequences `/mark-story-done` and `/check-in-diff`, treats invocation as bundled approval for close-out plus landing, and preserves the guardrails from both leaf skills.
   Us: Codex-forge has the leaf skills and the landing runbook, but no top-level orchestrator for the common "close the story and land it" path.
   Recommendation: Adopt inline as a canonical project skill and regenerate the derived Gemini wrapper.

## Approved

- [x] 1. `discover-models` re-scout — Confirmed current local adoption; no additional code changes required
  Evidence: `diff -ru /Users/cam/Documents/Projects/cine-forge/.agents/skills/discover-models .agents/skills/discover-models` showed only intentional codex-forge-local adaptation in `SKILL.md` (alignment wording, plain `python` invocation, punctuation), with no missing source behavior to pull over.
- [x] 2. `finish-and-push` skill — Adopted inline
  Evidence: Added `.agents/skills/finish-and-push/SKILL.md`; regenerated `.gemini/commands/finish-and-push.toml`; validated with `scripts/sync-agent-skills.sh --check` and `make skills-check`, both passing after a clean sequential run.

## Skipped / Rejected

- None
