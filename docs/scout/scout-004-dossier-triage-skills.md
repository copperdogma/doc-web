# Scout 004 — dossier-triage-skills

**Source:** /Users/cam/Documents/Projects/dossier/.agents/skills/triage-inbox/ and triage-stories/
**Scouted:** 2026-03-12
**Scope:** Dossier's two triage skills — inbox processing and story backlog prioritization
**Previous:** Scout 001 (noted triage-* skills existed but didn't deep-dive)
**Status:** Complete

## Findings

1. **`/triage-inbox` — Process Inbox Items** — HIGH value
   What: Interactive skill that reads `docs/inbox.md`, groups items by theme, evaluates each against `docs/ideal.md`, and routes to: fold into existing story, new story, research spike, ADR, spec update, ideal update, or discard. Deletes processed items (inbox is a queue, not an archive). Key patterns: batch-decide related items, check existing drafts before creating new stories, require clear revisit triggers for items that can't be actioned yet.
   Us: We have `docs/inbox.md` with 2 substantial items (OCR two-step strategy, input sanitization). No skill to process them — triage happens ad-hoc in conversation.
   Recommendation: Adopt inline — port the skill, adapting references to match codex-forge's doc structure.

2. **`/triage-stories` — Evaluate Story Backlog** — HIGH value
   What: Read-only advisory skill that loads the full story index + `docs/ideal.md`, reads all Draft/Pending candidate stories, scores each on Ideal gap severity, dependency readiness, blocking power, phase coherence, momentum, and complexity vs. payoff. Flags stories that move AWAY from the Ideal for trashing. Presents ranked top 3-5 with rationale. User picks, then runs `/build-story`. Key patterns: Draft stories are candidates too (build-story fleshes them out), measure-first for recently-completed work, check for new SOTA models that may obsolete workarounds.
   Us: We have `docs/stories.md` with 130+ stories and `docs/ideal.md`. Story selection is ad-hoc — no structured evaluation against Ideal alignment, no systematic flagging of stale/misaligned stories.
   Recommendation: Adopt inline — port the skill, adapting for codex-forge's story statuses and structure.

3. **Ideal Alignment Gate** — HIGH value (comes free with both skills)
   What: Both triage skills enforce a mandatory Ideal alignment check. Stories that optimize compromises rather than closing Ideal gaps are flagged for trashing. Items that build for stages that don't exist yet are flagged as premature.
   Us: We have ideal.md and spec.md but no systematic enforcement. Easy to drift toward compromise-entrenching work.
   Recommendation: Included in both skill ports — no separate effort needed.

4. **Inbox-as-Queue Pattern** — MEDIUM value
   What: Dossier treats inbox.md as a processing queue — every item is either routed to an artifact or discarded. Items that can't be actioned get explicit revisit triggers. Inbox should be empty or near-empty after triage.
   Us: Our inbox.md has items that have been sitting there without clear disposition.
   Recommendation: Adopt as part of triage-inbox — no separate effort. May want to restructure inbox.md with an "Untriaged" section header.

## Approved

- [x] 1. `/triage-inbox` — **Adopted**. Ported to `.agents/skills/triage-inbox/SKILL.md`, synced to all CLIs.
- [x] 2. `/triage-stories` — **Adopted**. Ported to `.agents/skills/triage-stories/SKILL.md`, synced to all CLIs.

## Skipped / Rejected

(none)
