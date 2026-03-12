---
name: triage-inbox
description: Process inbox items into stories, research spikes, or spec updates
user-invocable: true
---

# /triage-inbox

Go through accumulated inbox items together with the user.

## Steps

1. **Read inbox** — Load `docs/inbox.md`. List all untriaged items. Also load
   `docs/ideal.md` and scan story statuses in `docs/stories.md` for context.

2. **Prioritize** — Evaluate the full inbox against current project state:
   - Group items by theme if natural clusters exist (shared prerequisites,
     same domain concern, same blocking story)
   - Recommend a **top 3-5** to triage first with rationale
   - Flag items that are probably defer/discard candidates
   - Let the user adjust before proceeding

3. **For each item (or batch of related items), discuss with the user:**
   - Does this move toward the Ideal (`docs/ideal.md`) or away from it?
     If it proposes infrastructure that serves a compromise, check whether the
     underlying detection eval still fails before investing.
   - **"What if we don't do this?"** — How hard is it for consumers to solve
     this themselves? If the answer is "20 lines of post-processing," it's
     probably not codex-forge's problem.
   - Is this a signal that a compromise can be deleted? (New model capability,
     ecosystem change.) If so, the first action is running the detection eval
     from `docs/spec.md`, not creating a story.
   - What should we do with it?
     - **Fold into existing story** → Check draft stories for natural homes first.
       Add as design notes in the story's Notes section — enriches scope without
       creating new artifacts. This is often the best outcome.
     - **New story** → Use `/create-story` to scaffold it. Only when the item
       represents distinct, actionable work that doesn't fit an existing story.
     - **Research spike** → Needs investigation before committing to a story
     - **Spec update** → Update `docs/spec.md` directly (read ideal.md first —
       if adding a compromise, it needs a detection mechanism)
     - **Ideal update** → Update `docs/ideal.md` (new requirement or preference discovered)
     - **Discard** → Remove from inbox (idea is not valuable or not our problem)

4. **Create artifacts** — For each decision, create the appropriate artifact immediately.

5. **Delete from inbox** — Every processed item is **removed** from `docs/inbox.md`.
   The inbox is a processing queue, not an archive. Once an item lands in a story,
   spec, or gets discarded, it has no purpose in the inbox. If an item can't be
   attached anywhere actionable yet, it stays with a clear revisit trigger
   (e.g., "revisit when Story 026 is active").

6. **Summarize** — Quick summary of what was processed and where each item landed.

## Guardrails

- Always discuss with the user before creating artifacts — don't auto-triage
- Batch-decide items with shared prerequisites or themes — don't force item-by-item
- Check existing draft stories before creating new ones — fold in when the fit is clean
- The inbox should be empty or near-empty after triage — if items linger, they need
  a clearer revisit trigger or should be discarded
- If an item needs investigation before triaging, say so and move on
