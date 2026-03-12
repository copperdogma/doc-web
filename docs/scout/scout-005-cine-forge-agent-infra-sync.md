# Scout 005 — cine-forge-agent-infra-sync

**Source:** /Users/cam/Documents/Projects/cine-forge
**Scouted:** 2026-03-12
**Scope:** Recent agent-infrastructure delta — shared skills, AGENTS hardening, wrapper generation, Cursor/Gemini support, and repo-hygiene scouting
**Previous:** Scout 002 (cine-forge-patterns)
**Status:** Complete

## Findings

1. **Gated story handoff across `/build-story`, `/validate`, and `/mark-story-done`** — HIGH value
   What: Cine hardened the story lifecycle so implementation, validation, and close-out are separate phases with explicit workflow gates.
   Us: Codex-forge had the lifecycle concept, but the skill text still let `/build-story` mark stories Done and did not enforce handoff state clearly.
   Recommendation: Adopt inline.

2. **Safer `/check-in-diff` landing flow for worktrees and `main` fallback** — HIGH value
   What: Cine expanded `/check-in-diff` from audit-only into a safer branch landing protocol that avoids resolving integration conflicts directly on `main`.
   Us: Codex-forge had audit guidance but not the safer landing path or companion runbook.
   Recommendation: Adopt inline.

3. **Stronger story scaffolding and planning prompts** — HIGH value
   What: Cine upgraded `/create-story` and the story template with workflow gates, redundancy planning, decision context, and structural-health prompts.
   Us: Codex-forge's story template was lighter and did not precompute as much planning context for future agents.
   Recommendation: Adopt inline, adapted to codex-forge's pipeline and `schemas.py` workflow.

4. **Re-scout-aware scout flow and sharper backlog triage** — MEDIUM value
   What: Cine taught `/scout`, `/triage-inbox`, and `/triage-stories` to reuse prior expeditions, treat shorthand sources intelligently, and force better prioritization questions.
   Us: Codex-forge's versions worked, but they lost useful history and had weaker re-scout ergonomics.
   Recommendation: Adopt inline.

5. **Eval verification cost discipline** — HIGH value
   What: Cine added explicit rerun-cost guidance to `/verify-eval` so score verification does not waste uncached model calls.
   Us: Codex-forge required mismatch classification but had no explicit rerun-cost protocol.
   Recommendation: Adopt inline.

6. **Repo-hygiene scout skill** — HIGH value
   What: Cine added `/codebase-improvement-scout`, templates, and a runbook for deterministic repo-hygiene scans that produce either a report, a story, or a narrow safe autofix.
   Us: Codex-forge had ad hoc improvement work but no dedicated recurring-hygiene skill.
   Recommendation: Adopt inline, adapted to codex-forge's `make` targets and `docs/reports/` layout.

7. **AGENTS hardening around approvals, decision context, prompt-first escalation, and architecture rules** — HIGH value
   What: Cine added stronger repo-level guidance about bundled approvals, prompt-first model escalation, decision lookup, and file-size hygiene.
   Us: Codex-forge already had strong pipeline mandates, but it lacked several of these workflow-level guardrails.
   Recommendation: Adopt inline.

8. **Cross-CLI support cleanup (`.cursor`, Gemini settings, generated wrappers)** — MEDIUM value
   What: Cine keeps Cursor and Gemini support explicit instead of relying entirely on convention.
   Us: Codex-forge generated Gemini wrappers already, but Cursor support was implicit and `.cursor/` was ignored.
   Recommendation: Adopt inline, with `.gitignore` narrowed so only the intended Cursor files are tracked.

9. **Raw `.claude/settings.local.json` permission allowlist copy** — LOW value
   What: Cine carries a Claude-specific local permission allowlist tailored to its exact skill set and shell workflow.
   Us: Codex-forge has a different skill surface and command set, and the file is intentionally git-ignored here.
   Recommendation: Skip raw port. The intent is covered by the repo-level instructions; copying the cine file blind would be wrong.

## Approved

- [x] 1. Story lifecycle hardening — **Adopted**
- [x] 2. Safer check-in landing flow — **Adopted**
- [x] 3. Story scaffolding and planning prompts — **Adopted**
- [x] 4. Scout and triage refinements — **Adopted**
- [x] 5. Eval verification cost discipline — **Adopted**
- [x] 6. Repo-hygiene scout skill — **Adopted**
- [x] 7. AGENTS hardening — **Adopted**
- [x] 8. Cursor and Gemini support cleanup — **Adopted**

## Skipped / Rejected

- 9. Raw `.claude/settings.local.json` port — Skip. Tool- and repo-specific allowlist; unsafe to copy without a codex-forge-specific redesign.
- ADR-only wording from cine skills was not copied verbatim. Instead, the intent was absorbed into generalized "decision check" language that points at codex-forge's existing `docs/runbooks/`, `docs/scout/`, and `docs/notes/` structure rather than inventing empty `docs/decisions/` scaffolding.
