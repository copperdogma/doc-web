---
name: scout
description: Research a source (repo, URL, article) for ideas to adopt, recommend changes, implement approved items, and self-verify.
user-invocable: true
---

# /scout [source]

Research external sources for patterns, ideas, and approaches worth adopting.

## Inputs

- **source** (required): Local repo path, GitHub URL, article URL, or file path
- **scope** (optional): Time range, branch, specific area to focus on

## Phase 0 — Bootstrap

```bash
.agents/skills/scout/scripts/start-scouting.sh <topic-slug>
```

Creates `docs/scout/scout-NNN-<slug>.md` from template.

## Phase 1 — Research

1. **Check history:** Read `docs/scout.md` for previous expeditions.
2. **Explore the source** based on type.
3. **Compare against the Ideal and spec:** Read `docs/ideal.md` and `docs/spec.md`. For each finding, assess: (a) Does it move toward the Ideal? (b) Does it eliminate or simplify a spec compromise? (c) Does it make a detection eval more likely to pass?
4. **Fill in the scout document** with findings.
5. **Present findings** with value ratings and effort estimates.
6. **Recommend** with clear approval prompt.

## Phase 2 — Approval

Wait for user to approve specific items.

## Phase 3 — Implementation

Implement approved items, create stories for large items.

## Phase 4 — Verification

Re-read modified files, fill in evidence, run checks, update scout doc and index.

## Guardrails

- Never implement without explicit user approval
- Always create the scout document before implementation
- Never skip the verification phase
- When in doubt about size, suggest a story rather than inline implementation
- Don't commit or push unless the user explicitly requests it
