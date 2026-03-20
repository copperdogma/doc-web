# Scout 010 — dossier-storybook-upgrades

**Source:** `/Users/cam/Documents/Projects/dossier` and `/Users/cam/Documents/Projects/Storybook/storybook`
**Scouted:** 2026-03-20
**Scope:** Re-scout Dossier since 2026-03-18 and Storybook since 2026-03-15, focused on scout-skill changes, workflow hardening, and Storybook's methodology bootstrap package
**Previous:** Scouts 001, 003, 004, 006, 007, and 009
**Status:** Complete
**Alignment:** Reviewed local scout history plus decision-supporting docs before choosing an approach: `docs/scout.md`, `docs/scout/scout-001-dossier-patterns.md`, `docs/scout/scout-003-storybook-patterns.md`, `docs/scout/scout-004-dossier-triage-skills.md`, `docs/scout/scout-006-storybook-adr-skills.md`, `docs/scout/scout-007-storybook-adr-followups.md`, `docs/scout/scout-009-cross-repo-skill-sync.md`, `docs/notes/doc-web-dossier-readiness-gap-analysis.md`, `docs/runbooks/codebase-improvement-scout.md`, `docs/decisions/README.md`, and `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`.

## Findings

1. **Dossier's upgraded `/scout` pattern makes cross-repo ports auditable** — HIGH value
   What: Dossier's current `/scout` skill explicitly supports "gene transfusion" for real pattern transfers: capture the exemplar, invariant, local adaptation, and proof target only when a finding is an actual port candidate. Its scout template also adds dedicated `Verification` and `Evidence` sections so adopted items do not stop at "we changed something" without proof.
   Us: Doc-forge's current `/scout` surface is the older variant. It creates expedition docs, but it does not help future readers see which findings were concrete pattern ports versus inspiration, and the template does not reserve a consistent place for verification/evidence.
   Recommendation: Adopt inline. Keep doc-forge's stricter local decision-check preamble, but port the transfusion and proof-surface pieces from Dossier.
   Transfusion:
   Exemplar: Dossier's current `/scout` skill and expedition template, where real cross-repo ports carry explicit exemplar/invariant/adaptation/proof-target notes plus dedicated `Verification` and `Evidence` sections.
   Invariant: A scout record should make real pattern transfers auditable instead of collapsing them into a generic "looked at repo X" note.
   Adaptation: Keep doc-forge's stronger local decision-check framing and existing scout workflow, but add the transfusion and proof surfaces only where there is a real transfer.
   Proof target: Doc-forge's scout skill and expedition template support transfusion notes plus dedicated verification/evidence sections, and this scout uses that shape.

2. **Storybook now treats the build map as the mandatory planning surface, not optional context** — HIGH value
   What: Storybook's AGENTS and planning skills now make the methodology graph operational: planning/triage start from `docs/build-map.md`; `create-story` and `build-story` must read the relevant build-map category, capture current input-coverage stage when applicable, and verify critical substrate in code before treating `Pending` as honestly buildable.
   Us: Doc-forge already has the dual-ideal/build-map structure and phase-aware triage, but the core planning path is still weaker. `AGENTS.md` documents the build map, yet it does not state the build-map-first operating rule. `.agents/skills/build-story/SKILL.md` and `.agents/skills/create-story/SKILL.md` still anchor mainly on the story/spec/ADR surface and do not force a substrate reality check before assuming `Pending` means buildable in implemented reality.
   Recommendation: Adopt inline with a doc-forge-specific workflow update.
   Transfusion:
   Exemplar: Storybook's AGENTS plus `create-story` / `build-story` / `triage-stories` surfaces, where build-map-first planning and code-verified substrate reality are mandatory.
   Invariant: Build-map context and substrate reality must shape planning decisions before implementation starts; `Pending` alone is not enough.
   Adaptation: Keep the doc-forge pipeline-centric workflow and remove Storybook's app-specific UI gates, while carrying over build-map-first routing, input-coverage awareness, and substrate verification.
   Proof target: Doc-forge's AGENTS and planning skills now explicitly require build-map context and code-level substrate checks before recommending or building work.

3. **Storybook's `setup-methodology` package is the missing public bootstrap/refresh surface here** — HIGH value
   What: Storybook consolidated the methodology bootstrap into one public entrypoint: `.agents/skills/setup-methodology/` plus `docs/runbooks/setup-methodology.md`, `docs/setup-checklist.md`, and `docs/methodology-ideal-spec-compromise.md`. The package treats ideal/spec/build-map alignment, eval/golden baseline setup, story bootstrap, AGENTS wiring, and skill sync as one coherent install/refresh operation instead of scattered tribal knowledge.
   Us: Doc-forge already absorbed most of the underlying ADR-021 methodology shape, but it does not have a canonical refresh package. There is no `setup-methodology` skill, no methodology reference doc, no working `docs/setup-checklist.md`, and no local eval bootstrap doc surface like `docs/evals/README.md` / `docs/evals/attempt-template.md`. Porting this cleanly would require a doc-forge-specific adaptation, likely `refresh`-first rather than full greenfield bootstrap.
   Recommendation: Adopt inline with a doc-forge-specific package adaptation.
   Transfusion:
   Exemplar: Storybook's `setup-methodology` skill package plus methodology reference, setup runbook, and working checklist.
   Invariant: Methodology bootstrap and refresh should be a coherent package with one public surface, not scattered notes.
   Adaptation: Doc-forge's version uses the current repo mission and eval surface, does not advertise missing commands like `/create-eval`, and ties the package to benchmark/runbook surfaces that already exist here.
   Proof target: Doc-forge has a new `setup-methodology` skill, methodology reference doc, setup checklist, runbook, eval-surface docs, AGENTS wiring, and regenerated wrappers.

4. **Dossier hardened workflow trust by requiring fresh verification for success claims** — MEDIUM value
   What: Dossier recently tightened AGENTS plus close-out skills so "done", "fixed", or "passing" claims must be backed by fresh commands for the current state, or explicitly labeled as not freshly verified.
   Us: Doc-forge already has stronger-than-average artifact inspection and completion gates, but it still lacks a repo-wide status-trust rule. The current workflow docs say what "done" requires; they do not explicitly forbid optimistic intermediate claims when verification is stale.
   Recommendation: Adopt inline. This is a good fit for AGENTS plus the existing validation/close-out skills without introducing a new workflow.
   Transfusion:
   Exemplar: Dossier's fresh-verification requirement in AGENTS and close-out skills.
   Invariant: Status claims must be tied to current-pass evidence instead of memory or extrapolation.
   Adaptation: Apply the rule to doc-forge's story/build/validate/check-in flow and pipeline-artifact review discipline.
   Proof target: AGENTS and the relevant workflow skills explicitly require fresh verification or explicit "not freshly verified" labeling.

## Approved

- [x] 1. `/scout` transfusion + verification/evidence upgrade — Adopted inline
  Evidence: updated `.agents/skills/scout/SKILL.md` and `.agents/skills/scout/templates/scout-expedition.md` to add optional gene-transfusion capture plus dedicated `Verification` / `Evidence` sections.
- [x] 2. Build-map-first planning + substrate reality checks — Adopted inline
  Evidence: updated `AGENTS.md`, `.agents/skills/build-story/SKILL.md`, `.agents/skills/create-story/SKILL.md`, `.agents/skills/create-story/templates/story.md`, and `.agents/skills/triage-stories/SKILL.md`.
- [x] 3. `setup-methodology` package adaptation — Adopted inline
  Evidence: added `.agents/skills/setup-methodology/SKILL.md`, `.agents/skills/setup-methodology/references/modes.md`, `.agents/skills/setup-methodology/templates/setup-checklist.md`, `docs/runbooks/setup-methodology.md`, `docs/methodology-ideal-spec-compromise.md`, `docs/setup-checklist.md`, `docs/evals/README.md`, and `docs/evals/attempt-template.md`.
- [x] 4. Fresh-verification status-trust hardening — Adopted inline
  Evidence: updated `AGENTS.md`, `.agents/skills/build-story/SKILL.md`, `.agents/skills/validate/SKILL.md`, `.agents/skills/mark-story-done/SKILL.md`, and `.agents/skills/check-in-diff/SKILL.md`.

## Skipped / Rejected

- Pinned Dossier runtime packaging from Storybook — already materially reflected in doc-forge via ADR-002 and `docs/notes/doc-web-dossier-readiness-gap-analysis.md`; not a new methodology gain from this re-scout.
- Storybook's user-facing UI completeness gates — strong pattern for app work, but not a direct fit for doc-forge's mostly pipeline/story surfaces beyond the substrate-check pieces already captured in Finding 2.
- Dossier's `discover-models` refresh — local `discover-models` is already adapted and newer in places; no clear missing source behavior surfaced in this pass.

## Verification

- Re-read the modified workflow files and new setup-methodology package files after editing
- Compared the adopted surfaces against `/Users/cam/Documents/Projects/dossier` and `/Users/cam/Documents/Projects/Storybook/storybook`, then patched the remaining fidelity gaps (`create-story` story-id rule, `triage-stories` build-map read path, and workflow-gate checks in `AGENTS.md`, `mark-story-done`, and `validate`)
- Ran `./scripts/sync-agent-skills.sh`
- Ran `./scripts/sync-agent-skills.sh --check`
- Ran `make skills-check`
- Ran `rg -n "setup-methodology|methodology-ideal-spec-compromise|setup-checklist|Fresh Verification Required|Pending is not proof of buildability" AGENTS.md docs .agents/skills`
- Ran `rg -n "setup-ideal|setup-spec|setup-stories|setup-evals|setup-golden|retrofit-ideal" AGENTS.md docs .agents/skills .gemini/commands || true`
- Ran `git diff --check`

## Evidence

- Canonical methodology refresh surface now exists under `.agents/skills/setup-methodology/` and is wired into AGENTS plus `.gemini/commands/setup-methodology.toml`
- Build-map-first planning guidance now appears in `AGENTS.md`, `.agents/skills/build-story/SKILL.md`, `.agents/skills/create-story/SKILL.md`, and `.agents/skills/triage-stories/SKILL.md`, with `create-story` and `triage-stories` rechecked against Storybook's current source wording
- Eval bootstrap docs now exist at `docs/evals/README.md` and `docs/evals/attempt-template.md`, with `docs/setup-checklist.md` tracking the package state for refresh runs
- Fresh-verification trust language now exists in `AGENTS.md`, `.agents/skills/build-story/SKILL.md`, `.agents/skills/validate/SKILL.md`, `.agents/skills/mark-story-done/SKILL.md`, and `.agents/skills/check-in-diff/SKILL.md`, with workflow-gate checks tightened to match the Dossier close-out pattern more closely
