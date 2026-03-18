# Scout 008 — cine-forge-model-skill

**Source:** /Users/cam/Documents/Projects/cine-forge
**Scouted:** 2026-03-18
**Scope:** Re-scout since 2026-03-12, focused on the `discover-models` skill and its backing provider-query script
**Previous:** Scout 005 (cine-forge-agent-infra-sync)
**Status:** Complete

## Findings

1. **`discover-models` skill plus `scripts/discover-models.py`** — HIGH value
   What: Cine-forge has a dedicated skill that queries OpenAI, Anthropic, and Google model APIs, filters to chat-capable models, compares discoveries against `docs/evals/registry.yaml`, and can optionally cache a machine-readable snapshot for other skills.
   Us: Codex-forge had no equivalent skill or utility. Fresh model discovery depended on manual provider checks or ad hoc web research, which is slower and harder to reuse during eval triage.
   Recommendation: Adopt inline with codex-forge's standard alignment-check wording, local command paths, and stricter registry matching so narrative score labels do not over-report variants as already tested.

## Approved

- [x] 1. `discover-models` skill plus backing script — **Adopted**
  Evidence: Added `.agents/skills/discover-models/SKILL.md` and `scripts/discover-models.py`; generated `.gemini/commands/discover-models.toml`; adapted the registry matcher to canonicalize model-family tokens from codex-forge's human-readable score labels; verified with `scripts/sync-agent-skills.sh --check`, `python scripts/discover-models.py --summary`, and `python scripts/discover-models.py --check-new`, which discovered 71 models across OpenAI, Anthropic, and Google in this workspace and flagged 49 as untested against `docs/evals/registry.yaml`.

## Skipped / Rejected

- Wider provider coverage beyond OpenAI, Anthropic, and Google — Skip for now. The source skill is scoped to the providers used in this repo's eval workflow; broadening that scope is a separate follow-up.
