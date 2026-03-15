# Scout 007 — storybook-adr-followups

**Source:** /Users/cam/Documents/Projects/Storybook/storybook
**Scouted:** 2026-03-15
**Scope:** Follow-up pass on Storybook's ADR workflow surface after Scout 006, specifically to find reusable ADR-adjacent pieces that were missed in the first adaptation
**Previous:** Scout 006 (storybook-adr-skills, 2026-03-14)
**Status:** Complete

## Findings

1. **`reflect` is a missing ADR-adjacent closure tool** — HIGH value
   What: Storybook has a read-only `/reflect` skill that traces a change across ideal/spec/stories/evals so downstream docs and backlog implications do not get missed.
   Us: codex-forge had ADR creation and lifecycle docs, but no lightweight impact-tracing skill to propagate accepted decisions or major findings.
   Recommendation: Adopt inline, adapted to codex-forge's doc surface (`ideal`, `spec`, `requirements`, stories, ADRs, eval registry, AGENTS).

2. **The deep-research workflow should be a first-class runbook** — HIGH value
   What: Storybook documents a repeatable multi-provider research process, including provider split, recency rules, synthesis expectations, and manual-provider handling.
   Us: codex-forge already used this workflow in practice for ADR-001, but it only existed as tribal memory plus scattered ADR artifacts.
   Recommendation: Adopt inline as `docs/runbooks/deep-research.md`, but adapt it to codex-forge's existing ADR research-file naming convention instead of Storybook's default stub/report names.

3. **ADR lifecycle docs should explicitly point to research and reflection** — MEDIUM value
   What: Storybook's ADR materials tie creation, deep research, discussion, and later propagation together more tightly than our first adaptation did.
   Us: codex-forge's `create-adr` skill and ADR runbook covered the core lifecycle, but they did not explicitly point users toward a standard deep-research flow or a post-decision reflection sweep.
   Recommendation: Adopt inline by wiring `create-adr`, `adr-creation.md`, and `docs/decisions/README.md` to `deep-research` and `reflect`.

4. **No other standalone ADR package pieces were materially missing** — LOW value
   What: The remaining Storybook ADR search hits were either already adopted in Scout 006 or were Storybook-specific integrations (`setup.md`, `feature-map.md`, product-specific ADR cross-linking).
   Us: codex-forge does not need those surfaces and would only gain accidental complexity from copying them.
   Recommendation: Skip.

## Approved

- [x] 1. `reflect` skill — **Adopted inline.** Added `.agents/skills/reflect/SKILL.md` adapted to codex-forge's doc surface and impact-report needs.
- [x] 2. Deep research runbook — **Adopted inline.** Added `docs/runbooks/deep-research.md` with codex-forge ADR research conventions and provider guidance.
- [x] 3. ADR lifecycle wiring — **Adopted inline.** Updated `create-adr`, `docs/runbooks/adr-creation.md`, and `docs/decisions/README.md` so the new pieces are discoverable and part of the normal ADR flow.

## Verification

- Manual readback: `/Users/cam/.codex/worktrees/72eb/codex-forge/.agents/skills/reflect/SKILL.md`
- Manual readback: `/Users/cam/.codex/worktrees/72eb/codex-forge/docs/runbooks/deep-research.md`
- Manual readback: `/Users/cam/.codex/worktrees/72eb/codex-forge/.agents/skills/create-adr/SKILL.md`
- Manual readback: `/Users/cam/.codex/worktrees/72eb/codex-forge/docs/runbooks/adr-creation.md`
- Manual readback: `/Users/cam/.codex/worktrees/72eb/codex-forge/docs/decisions/README.md`
- `scripts/sync-agent-skills.sh`
- `scripts/sync-agent-skills.sh --check`
- `make skills-check`

## Skipped / Rejected

- 4. Storybook-specific ADR integrations (`setup.md`, `feature-map.md`, product-level cross-link surfaces) — skipped because codex-forge does not have equivalent docs and the existing adaptation already points decisions at the right local surfaces.
