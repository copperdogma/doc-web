# Story 148 — ADR-021 Migration: Dual-Ideal, Category Spec, Phase Governance

**Priority**: High
**Status**: In Progress
**Ideal Refs**: All requirements (R1-R7), all Vision-Level Preferences — this restructures how the project tracks progress toward the Ideal
**Spec Refs**: spec:1–spec:9 (all categories), all active compromises C1-C7, Non-Negotiable Design Principles, build-process compromises B1-B10
**Decision Refs**: ADR-001 (consistency strategy — will gain spec:N.N cross-ref), Storybook ADR-021 migration guide (`/Users/cam/Documents/Projects/Storybook/storybook/docs/decisions/adr-021-execution-ideal-build-constraints/migration.md`), Story 145 (ADR-019 convergence — established current build-map structure)
**Depends On**: Story 145 (build-map convergence must be done first — it is)

## Goal

Migrate codex-forge's project management docs to the ADR-021 structure from the Storybook AI: dual-ideal (product + execution), category-aligned spec with hierarchical `spec:N.N` section IDs and constraint blocks, phase-governed build map (climb/hold/converge), and execution compromise tracking. This gives the project stable cross-references, phase-aware triage, and explicit tracking of build-process compromises alongside product compromises.

This is a documentation reorganization — no code, no new evals, no new stories beyond this one. All existing content is preserved and reorganized with provenance. The migration guide is the authoritative playbook; this story adapts each phase to codex-forge's specific structure.

## Acceptance Criteria

- [ ] `docs/ideal.md` has a new `## The Execution Ideal` section after the product ideal, describing the zero-limitation build process
- [ ] `docs/spec.md` is reorganized into ~8-9 category sections with `spec:N` tags, hierarchical `spec:N.N` subsection IDs, and constraint blocks per category
- [ ] Every active compromise (C1-C7) appears in a constraint block with: limitation type, ideal, compromise, detection mechanism, and resolution path
- [ ] 1-2 build-process categories exist in spec.md with execution compromise tables (eval framework, prompt engineering, story infrastructure, etc.)
- [ ] `docs/build-map.md` is reorganized to match spec categories 1:1 — same names, same `spec:N` tags
- [ ] Every build-map category has: product need, tech need, substrate status (`exists`/`partial`/`missing`/`unplanned`), phase (`climb`/`hold`/`converge`/`unplanned`)
- [ ] Every old build-map system number (1-8) appears in exactly one category's `Absorbs` line for migration traceability
- [ ] Story Spec Refs in existing story files are updated from bare `C1`, `C2` etc. to include `spec:N.N` IDs where applicable
- [ ] Triage skills (`triage-stories`, `triage-evals`, `triage` orchestrator) are updated to consume substrate status and phase from build map
- [ ] `/align` skill references the new structure
- [ ] `AGENTS.md` methodology section mentions dual-ideal, unified spec with N categories, build map as central dashboard, and phase governance
- [ ] No content is lost — every section from old spec and build map has a home in the new structure
- [ ] All cross-references between spec, build map, stories, and ADR-001 use the new `spec:N.N` IDs

## Out of Scope

- Creating new evals or golden fixtures
- Creating new stories (beyond this one)
- Restructuring code, schemas, or pipeline modules
- Changing any ADR decisions — only adding cross-references
- Deleting any content — only reorganizing and adding provenance
- Creating a `docs/retrofit-gaps.md` (codex-forge never had one; compromises are already in spec.md)
- Creating a `docs/methodology-*.md` (codex-forge uses AGENTS.md for this)
- Creating a `docs/coverage.md` (codex-forge uses build-map Input Coverage instead)

## Approach Evaluation

- **Simplification baseline**: Not applicable — this is a structured document reorganization, not a generation task.
- **AI-only**: An LLM can draft category mappings and rewrite docs, but must preserve all content exactly. High risk of silent content loss on large docs.
- **Hybrid**: AI drafts each phase, human/validator verifies content preservation via diff review. Leading candidate — the migration guide provides deterministic structure, AI handles the mechanical reorganization.
- **Pure code**: Not applicable except for grep-based reference updates.
- **Repo constraints / prior decisions**: Story 145 established the current 8-system build map structure. ADR-001 established consistency planning as a named compromise. The migration guide is the authoritative playbook from the Storybook project.
- **Existing patterns to reuse**: Current spec compromise format (C1-C7 with Ideal/Compromise/Limitation/Detection/When it resolves), current build-map system format, current triage skill structure.
- **Eval**: Content preservation is the key validation. Diff review must show every line from old spec/build-map has a home in the new structure. No automated eval needed — manual diff review plus `/align` post-migration.

## Tasks

### Phase 1: Add Execution Ideal to `docs/ideal.md`

- [ ] Add `## The Execution Ideal` section after the product ideal section and before `## Mission`
- [ ] Use the universal execution ideal text from the migration guide (describes the ideal process of building any product with AI)
- [ ] Verify the product ideal, mission, vision-level preferences, requirements, and minimum viable floor are untouched

### Phase 2: Define Category Structure

- [ ] Analyze current spec.md (7 active compromises C1-C7) and build-map.md (8 systems) to determine natural category groupings
- [ ] Proposed initial mapping (to be confirmed during `/build-story`):

  | Cat | Name | Absorbs (old system #) | Spec compromises |
  |-----|------|----------------------|-----------------|
  | 1 | Intake & Format Routing | old 1 | C2 |
  | 2 | OCR & Text Extraction | old 2 | C1, C6 |
  | 3 | Layout & Structure Understanding | old 3 | C3 |
  | 4 | Illustration Extraction | old 4 | C4, C5 |
  | 5 | Document Consistency Planning | old 5 | C7 |
  | 6 | Validation, Provenance & Export | old 6 | (Non-Negotiable Principles) |
  | 7 | Graduation & Dossier Handoff | old 7 | (Mission-level) |
  | 8 | AI Harnesses & Tooling | (new — split from old 8) | Build-process compromises |
  | 9 | Planning Infrastructure | (new — split from old 8) | Build-process compromises |

- [ ] Verify every old system (1-8) maps to exactly one category
- [ ] Verify every active compromise (C1-C7) maps to exactly one category
- [ ] Decide whether old system 8 ("Project Operating System") should split into two build-process categories (AI Harnesses vs Planning Infrastructure) or stay as one. The migration guide recommends 1-2 build-process categories.

### Phase 3: Reorganize `docs/spec.md`

- [ ] **3a — Add header metadata**: Add organization note explaining the category structure, `spec:N` tags, and hierarchical IDs
- [ ] **3b — Create category sections**: Each category becomes a `## spec:N — Category Name` heading with a one-line product need + tech substrate description
- [ ] **3c — Assign hierarchical section IDs**: Every subsection gets a `### spec:N.N — Name` ID. Current spec sections to map:
  - Non-Negotiable Design Principles → stay as preamble above categories (they're permanent, not compromises)
  - C1 (Multi-Stage OCR Pipeline) → `spec:2.1`
  - C2 (Format-Specific Conversion Recipes) → `spec:1.1`
  - C3 (Heuristic + AI Layout Detection) → `spec:3.1`
  - C4 (Two-Stage Image Crop Detection) → `spec:4.1`
  - C5 (Layout Text Trim Heuristics) → `spec:4.2`
  - C6 (Expensive OCR for Quality) → `spec:2.2`
  - C7 (Page-Scope Extraction) → `spec:5.1`
  - Retired Compromises → stay as a section below categories
  - Compromise-Level Preferences → dissolve into each category's constraint block
- [ ] **3d — Move content into categories**: For each current spec section, move it under the appropriate category heading. Preserve ALL content — do not summarize or cut. The current spec is only 88 lines so this is manageable.
- [ ] **3e — Add constraint blocks**: Convert each compromise into the constraint block format:
  ```
  **C1: Multi-Stage OCR Pipeline** [AI capability → deletion]
  *Ideal:* ... *Compromise:* ... *Detection:* ... *Resolves:* ...
  ```
  Each constraint block must include: limitation type (`AI capability`, `Ecosystem`, `Economics`), residual form (`deletion`, `evolution`), and the full detection/resolution text from the current spec.
- [ ] **3f — Add build-process categories**: Create 1-2 categories for execution compromises using the table format. Inventory codex-forge's build-process compromises:
  - B1: Eval framework (promptfoo) — AI can't self-assess output quality → deletion when reliable self-assessment
  - B2: Prompt engineering — models need carefully designed prompts → deletion when robust to naive prompts
  - B3: Story/backlog infrastructure — AI can't autonomously scope and sequence work → deletion when autonomous project planning
  - B4: Pipeline orchestration (driver.py) — AI can't compose reliable multi-step pipelines → deletion when single-call pipeline composition
  - B5: Schema stamping — AI outputs need structural validation → deletion when outputs are structurally guaranteed
  - B6: Manual artifact inspection — AI can't reliably self-verify output quality → deletion when reliable self-verification
  - B7: YAML recipe system — AI can't auto-configure processing → partial deletion (C2 product compromise also covers this)
  - Decide which of these are worth tracking explicitly vs. which are too granular
- [ ] **3g — Absorb retrofit-gaps.md**: N/A — codex-forge has no `retrofit-gaps.md`. All compromises are already in spec.md. Note this explicitly in the work log.
- [ ] **3h — Verify completeness**:
  - [ ] Every section from old spec has a home in the new structure
  - [ ] Every compromise ID (C1-C7) is present in a constraint block
  - [ ] No content was lost or summarized away (diff review)
  - [ ] Non-Negotiable Design Principles preserved as preamble
  - [ ] Retired Compromises preserved below categories
  - [ ] Hierarchical section IDs are consistent (no gaps, no duplicates)

### Phase 4: Consolidate `docs/build-map.md`

- [ ] **4a — Add header and reading guide**: Update the header to explain the new structure:
  - Central dashboard organized by category matching `spec.md` (`spec:1` through `spec:N`)
  - Each category tracks: product need, tech need, substrate status, story coverage, compromise phase
  - Reading guide defining: Product need, Tech need, Substrate (`exists`/`partial`/`missing`/`unplanned`), Phase (`climb`/`hold`/`converge`)
- [ ] **4b — Create category entries**: Rewrite each system entry to match the new template:
  ```
  ## N. Category Name                                                   `spec:N`

  **Product need:** ...
  **Tech need:** ...
  **Substrate:** exists / partial / missing / unplanned

  **Story coverage:** ...
  **Spec:** spec:N (spec:N.1, spec:N.2, ...)
  **ADR Refs:** ...
  **Absorbs:** Old System Name (old N)

  ### Compromise Progress
  - **C1: Name** (limitation type) — **phase**
    - Current: ...
    - Target/Eliminate: ...
    - Eval: ... — last run date, scores. **PASS/FAIL.**
  ```
- [ ] **4c — Assign phases** to each compromise:
  - C1 (Multi-Stage OCR): **climb** — substrate partial, eval scores below target (0.97 vs 0.99)
  - C2 (Format-Specific Recipes): **climb** — substrate exists but no auto-detect eval passes
  - C3 (Heuristic + AI Layout): **climb** — substrate exists but no dedicated deletion eval
  - C4 (Two-Stage Crop Detection): **climb** — substrate exists, eval 0.856 vs 0.95 target
  - C5 (Layout Text Trim): **climb** — substrate exists, no dedicated eval
  - C6 (Expensive OCR): **hold** — acceptable cost for now, waiting on economics
  - C7 (Document Consistency Planning): **climb** — substrate exists, planning layer works but not yet deletable
- [ ] **4d — Absorbs traceability**: Every old system number (1-8) must appear in exactly one category's `Absorbs` line:
  - `Absorbs: Intake & Format Routing (old 1)`
  - `Absorbs: OCR & Text Extraction (old 2)`
  - `Absorbs: Layout & Structure Understanding (old 3)`
  - `Absorbs: Illustration Extraction (old 4)`
  - `Absorbs: Document Consistency Planning (old 5)`
  - `Absorbs: Validation, Provenance & Export (old 6)`
  - `Absorbs: Graduation & Dossier Handoff (old 7)`
  - `Absorbs: Project Operating System (old 8)` — split across categories 8 and 9
- [ ] **4e — Fold special sections**: Move Input Coverage, Accuracy Dimensions, Known Gaps, Resolved Gaps, and Graduation Criteria into the appropriate categories or keep as cross-cutting sections below the categories. Decide during `/build-story`:
  - Input Coverage → likely stays as cross-cutting (spans all intake categories)
  - Accuracy Dimensions → likely stays as cross-cutting
  - Known Gaps → fold each gap into its owning category, or keep as cross-cutting
  - Graduation Criteria → fold into Graduation & Dossier Handoff category
  - Next Actions → keep as cross-cutting
  - Operating Rule (Quality First, Then Complexity Collapse) → keep under Planning Infrastructure or as cross-cutting
- [ ] **4f — Verify build-map ↔ spec alignment**:
  - [ ] Same number of categories in both docs
  - [ ] Category names match 1:1
  - [ ] Every `spec:N` tag in build map has a matching `## spec:N` in spec
  - [ ] Every compromise ID in build map appears in spec constraint blocks
  - [ ] No stale system names or old numbering remains (except in Absorbs lines)

### Phase 5: Migrate References

- [ ] **5a — Story files**: Search all story files for spec references using bare `C1`, `C2`, etc. and update Spec Refs lines to include the new `spec:N.N` ID alongside the compromise name. Format: `C1 → spec:2.1 (Multi-Stage OCR Pipeline)`. Stories to update (found via grep):
  - `story-131` — C1
  - `story-132` — Non-Negotiable Design Principle #1
  - `story-133` — None (keep as-is)
  - `story-134` — C1
  - `story-135` — C3, C4, C5
  - `story-136` — None
  - `story-137` — C3
  - `story-138` — C1, C3
  - `story-139` — C3
  - `story-140` — C1, C3, C6
  - `story-141` — C1, C2, C6
  - `story-142` — C1, C2, C6
  - `story-143` — C1, C2, C6
  - `story-144` — C1, C2, C6
  - `story-145` — C1-C7
  - `story-146` — C1, C6, C7
  - `story-147` — C1, C3, C7
  - Earlier stories (pre-130) likely have spec refs too — do a full grep and update all
- [ ] **5b — Coverage docs**: N/A — codex-forge has no `docs/coverage.md`. Input Coverage is in build-map.md and will be updated in Phase 4.
- [ ] **5c — ADR files**: Check `docs/decisions/adr-001-source-aware-consistency-strategy/adr.md` for spec references. Update any `C7` references to include `spec:5.1`. Add an ADR-021 cross-reference note if ADR-001 mentions the spec or build-map structure.
- [ ] **5d — Verify no stale references remain**: Grep all `docs/` for bare compromise references that lack `spec:N.N` IDs. Intentional exceptions: this story's migration notes, retired compromise descriptions.

### Phase 6: Update Triage/Planning Skills

- [ ] **6a — `/triage-stories` skill** (`.agents/skills/triage-stories/SKILL.md`):
  - Add **substrate readiness** to scoring criteria in Step 4: read the build-map category's substrate status; don't recommend stories when substrate is `missing` unless the story creates it
  - Add **phase coherence** detail to the existing "phase coherence" scoring criterion:
    - `climb`: recommend quality-improvement work
    - `hold`: recommend efficiency/simplification work
    - `converge`: recommend deletion work
    - Work that fights the phase is lower priority
  - Update Step 3 to reference `spec:N` category tags when reading build-map
- [ ] **6b — `/triage-evals` skill** (`.agents/skills/triage-evals/SKILL.md`):
  - Add a phase-aware assessment step: read the build-map phase for each eval's compromise
    - `climb` → focus on quality (better prompts, better golden fixtures)
    - `hold` → focus on efficiency (cheaper, faster, simpler)
    - `converge` → recommend deleting the compromise
  - Update "Deletion-gate health" section to reference `spec:N.N` constraint blocks
- [ ] **6c — `/triage` orchestrator** (`.agents/skills/triage/SKILL.md`):
  - Add phase coherence to the cross-domain synthesis criteria in Step 4
  - Update "Read the shared frame" to mention the category/phase structure
- [ ] **6d — `/align` skill** (`.agents/skills/align/SKILL.md`):
  - Update "Spec / Requirements" check to reference `spec:N.N` hierarchical IDs
  - Update "Build Map" check to reference phase governance (climb/hold/converge)
  - Add dual-ideal check: did this reveal an execution-ideal gap?
- [ ] **6e — Run `make skills-check`** after all skill updates

### Phase 7: Update Supporting Docs

- [ ] **7a — `AGENTS.md`**: Update the Docs section and any methodology references to mention:
  - Dual-ideal structure (product + execution) in `docs/ideal.md`
  - Unified spec with ~N categories and hierarchical `spec:N.N` IDs in `docs/spec.md`
  - Build map as central triage dashboard with substrate status and phase governance
  - Phase governance: climb / hold / converge
  - Do NOT rewrite the whole file — surgical additions only
- [ ] **7b — Methodology doc**: N/A — codex-forge doesn't have a standalone methodology doc. AGENTS.md serves this purpose.
- [ ] **7c — Cross-references**: Add ADR-021 cross-reference in ADR-001's adr.md (ADR-001 established consistency planning; ADR-021 restructures how compromises are tracked). Note: codex-forge doesn't have its own ADR-021 — this migration implements the Storybook's ADR-021 structure locally.
- [ ] **7d — Consider creating a local ADR**: Decide whether codex-forge needs its own ADR documenting the adoption of the dual-ideal/category/phase structure, or whether a work-log entry citing the Storybook ADR-021 is sufficient. Recommendation: a brief ADR or decision note is appropriate since this changes how all future triage, stories, and specs are written.

### Phase 8: Final Audit

- [ ] `ideal.md` has both product and execution ideals
- [ ] `spec.md` has N categories with `spec:N` tags and hierarchical section IDs
- [ ] Every compromise has a constraint block with ID, limitation, detection, resolution
- [ ] Build-process categories contain execution compromise tables
- [ ] `build-map.md` has same N categories with matching names and `spec:N` tags
- [ ] Every category has product need, tech need, substrate status
- [ ] Every compromise in build map has a phase (climb/hold/converge/unplanned)
- [ ] Old system numbers (1-8) all appear in Absorbs lines
- [ ] No stale references remain in stories or ADRs (except intentional migration notes)
- [ ] Triage skills consume substrate status and phase
- [ ] AGENTS.md updated
- [ ] Run `/align ADR-021 migration` to verify full methodology graph coherence

### Standard Checks

- [ ] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [ ] Run required checks for touched scope:
  - [ ] If agent tooling changed: `make skills-check`
  - [ ] Docs/index hygiene: `git diff --check`
  - [ ] Verify story numbering, story index row, and build-map references resolve correctly
- [ ] Search all docs and update any related to what we touched
- [ ] Verify Central Tenets:
  - [ ] T0 — Traceability: every spec section and compromise has a stable ID; every build-map entry traces to spec
  - [ ] T1 — AI-First: this is documentation work, no code involved
  - [ ] T2 — Eval Before Build: not applicable (no new logic)
  - [ ] T3 — Fidelity: all existing content preserved, reorganized with provenance
  - [ ] T4 — Modular: category structure is modular by design
  - [ ] T5 — Inspect Artifacts: manual diff review confirms no content loss

## Workflow Gates

- [ ] Build complete: implementation finished, required checks run, and summary shared
- [ ] Validation complete or explicitly skipped by user
- [ ] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: `docs/` — project management documentation layer
- **Data contracts / schemas**: No schema changes. No code changes. Pure documentation reorganization.
- **File sizes**: `docs/ideal.md` (62 lines), `docs/spec.md` (88 lines → will grow to ~200-250 with constraint blocks and build-process tables), `docs/build-map.md` (380 lines → will change shape but stay similar size), `AGENTS.md` (400 lines — surgical additions only), triage skills (~100 lines each — surgical additions)
- **Decision context**: Reviewed Storybook ADR-021 migration guide, ADR-001, Story 145 (established current build-map), Story 147 (quality-bar-then-collapse rule in build map). No existing codex-forge ADR covers documentation structure — this migration establishes the pattern.

## Files to Modify

- `docs/ideal.md` — add Execution Ideal section (62 lines)
- `docs/spec.md` — full reorganization into categories with hierarchical IDs and constraint blocks (88 lines → ~200-250)
- `docs/build-map.md` — consolidate to match spec categories, add substrate/phase governance (380 lines)
- `docs/stories/story-131-*.md` through `story-147-*.md` — update Spec Refs to include `spec:N.N` IDs (~17 files, one-line changes each)
- Earlier story files with Spec Refs — grep and update (one-line changes each)
- `docs/decisions/adr-001-source-aware-consistency-strategy/adr.md` — add ADR-021 cross-reference
- `.agents/skills/triage-stories/SKILL.md` — add substrate readiness and phase coherence detail (~104 lines)
- `.agents/skills/triage-evals/SKILL.md` — add phase-aware assessment step (~116 lines)
- `.agents/skills/triage/SKILL.md` — add phase coherence to synthesis criteria (~100 lines)
- `.agents/skills/align/SKILL.md` — update checks for new structure (~98 lines)
- `AGENTS.md` — update Docs section with new structure references (400 lines)
- `docs/stories.md` — add Story 148 row (170 lines)

## Redundancy / Removal Targets

- Current `Optimize` / `Eliminate` dual-tracking in build-map compromise progress → replaced by phase governance (`climb`/`hold`/`converge`)
- Current flat `Spec Sections: C1, C6` references in build-map → replaced by `Spec: spec:N (spec:N.1, spec:N.2, ...)` with hierarchical IDs
- Current `Compromise-Level Preferences` section in spec.md → dissolved into per-category constraint blocks
- Bare `C1`, `C2` spec refs in story files → enriched with `spec:N.N` IDs

## Notes

- **Content preservation is the #1 risk.** The spec is only 88 lines and the build map is 380 lines, so manual diff review is feasible. But the build map has extensive prose in compromise progress sections that must not be lost.
- **The category structure maps nearly 1:1 to the existing 8 systems.** The main structural change is splitting "Project Operating System" (old 8) into AI Harnesses & Tooling + Planning Infrastructure, and adding the new build-process compromise tables.
- **No retrofit-gaps.md exists.** Codex-forge tracks compromises directly in spec.md. Phase 3g of the migration guide is N/A.
- **No methodology doc exists.** AGENTS.md serves this purpose. Phase 7 methodology updates go into AGENTS.md.
- **No coverage.md exists.** Input Coverage is tracked in build-map.md and stays there.
- **No old-style L### line-number references exist in stories.** Phase 5 is about enriching existing `C1`-style refs with `spec:N.N` IDs, not replacing line numbers.
- **This story should be done in a single focused session** with careful diff review at each phase boundary. The migration guide recommends 8 phases; they should be executed sequentially since each depends on the previous.
- **Consider creating a local ADR** (`adr-002-adr-021-adoption` or similar) to document the decision to adopt this structure. This is a hard-to-reverse organizational change.

## Plan

To be written during `/build-story` — will detail exact file changes per phase, confirm category mapping, and identify any content that needs special handling during reorganization.

## Work Log

20260317-2100 — story created: analyzed Storybook ADR-021 migration guide against codex-forge's current docs structure (ideal.md 62L, spec.md 88L with 7 compromises, build-map.md 380L with 8 systems, 4 triage skills, 1 ADR); confirmed no retrofit-gaps.md, no methodology doc, no coverage.md, no L### refs in stories; proposed 9-category mapping that splits old system 8 into AI Harnesses + Planning Infrastructure; next step is `/build-story 148` when ready to execute

20260317-2130 — migration executed across all 8 phases:
  - Phase 1: Added Execution Ideal to `docs/ideal.md` (universal build-process ideal text)
  - Phase 2: Confirmed 9-category mapping — old systems 1-7 map 1:1, old system 8 splits into AI Harnesses (spec:8) + Planning Infrastructure (spec:9)
  - Phase 3: Reorganized `docs/spec.md` from 88L flat list → 9 categories with `spec:N.N` hierarchical IDs, 7 constraint blocks (C1-C7 with limitation type, ideal, compromise, detection, resolution, preference), 2 build-process categories with B1-B10 execution compromise tables. Non-Negotiable Principles preserved as preamble. Retired Compromises preserved below categories. Compromise-Level Preferences dissolved into constraint blocks.
  - Phase 4: Consolidated `docs/build-map.md` — 8 old systems → 9 categories matching spec 1:1. Added substrate status, phase governance (6 climb, 1 hold), product/tech need, Absorbs traceability (all old 1-8 accounted for). Replaced Optimize/Eliminate dual-tracking with phase assignments. Preserved Input Coverage, Accuracy Dimensions, Known Gaps, Resolved Gaps, Graduation Criteria, Operating Rule, Next Actions as cross-cutting sections.
  - Phase 5: Updated 15 story files (131-148) with `spec:N.N` IDs in Spec Refs. Updated ADR-001 with ADR-021 cross-reference. Story 132 updated to reference spec:6 for provenance principle.
  - Phase 6: Updated 4 skills — triage-stories (substrate readiness + phase coherence detail), triage-evals (phase-aware assessment step), triage orchestrator (phase coherence in synthesis), align (execution ideal check, substrate/phase checks, build-process compromise awareness). `make skills-check` passes (20 skills, 20 gemini wrappers).
  - Phase 7: Updated AGENTS.md Docs section with dual-ideal, unified spec, phase governance descriptions.
  - Phase 8: Final audit — 9 spec categories, 9 build-map categories, names match 1:1, all 7 C-constraints present, all old systems absorbed, all phases assigned, all story refs updated, skills-check passes.
  - Evidence: `grep '^## spec:' docs/spec.md` → 9 categories. `grep '^## [0-9]\.' docs/build-map.md` → 9 categories. `grep 'Absorbs:' docs/build-map.md` → all old 1-8 present. All story Spec Refs contain `spec:N.N` IDs.
  - Decision: deferred local ADR creation (adr-002) — the migration is documented in this story's work log and the Storybook ADR-021 is the authoritative source. Can create if future sessions need a local decision record.
