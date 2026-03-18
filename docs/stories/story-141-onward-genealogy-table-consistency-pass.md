# Story 141 — Onward Genealogy Consistency Investigation and ADR Handoff

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Fidelity to Source, Dossier-ready output
**Spec Refs**: spec:2.1 C1 (Multi-Stage OCR Pipeline), spec:1.1 C2 (Format-Specific Conversion Recipes), spec:2.2 C6 (Expensive OCR for Quality)
**Decision Refs**: `docs/decisions/adr-001-source-aware-consistency-strategy/adr.md`, `docs/runbooks/golden-build.md`, `docs/scout/scout-003-storybook-patterns.md`, Story 140 work log and `story140-onward-targeted-rescue-r19` review evidence
**Depends On**: Story 140

## Goal

Investigate the remaining Onward genealogy consistency failures after Story 140, measure whether a bounded strong-model baseline can repair them, and decide whether the next step should remain a narrow genealogy-table implementation or be reframed as a broader architectural decision. This story closes around that investigation and handoff work; implementation moved to Story 142 under ADR-001.

## Acceptance Criteria

- [x] Manually inspect the reviewed `story140-onward-targeted-rescue-r19` artifacts and record the chapter-level inconsistency signatures with concrete evidence
- [x] Measure bounded AI-first baselines on representative page runs and at least one full problematic chapter, then record the results and artifact paths
- [x] Decide whether the remaining work is a local table-only fix or a broader consistency strategy question, and capture that decision in an ADR
- [x] Protect Story 140's wins by recording the minimum non-regression chapters and explicitly moving implementation follow-up into a new story instead of stretching Story 141 into a hidden architecture rewrite

## Out of Scope

- Shipping the actual consistency implementation
- Adding a new adapter stage, recipe wiring, tests, or `driver.py` validation for a new consistency path
- Resolving ADR-001 research or accepting the final architecture
- Solving generic heading/list consistency beyond the Onward evidence that triggered the investigation

## Approach Evaluation

The original framing for Story 141 assumed the next move was a recipe-scoped genealogy-table consistency pass. Investigation showed that assumption was too narrow.

- **Simplification baseline**: Tested bounded top-tier AI baselines before writing new code. The strongest local result (`gpt-5` over the problematic `chapter-014.html`) materially outperformed the current deterministic glue.
- **AI-only**: Viable on a bounded slice and strong enough to prove the remaining issue is not just a rendering quirk. However, that alone does not answer where canonicalization belongs architecturally.
- **Hybrid**: The investigation outcome points here for future implementation: deterministic/statistical detection and acceptance around a stronger source-aware rerun path.
- **Pure code**: Rejected as the primary next move. The open failures are semantic enough that more HTML-only heuristics risk local overfitting.
- **Repo constraints / prior decisions**: OCR/source reads are expensive, Story 140 is the stable rescue baseline, and codex-forge should prefer source-aware quality over downstream cleanup when evidence supports it.
- **Existing patterns to reuse**: `load_artifact_v1` reuse flows, Story 140 artifact review workflow, `table_rescue_onward_tables_v1`, `build_chapter_html_v1`, and the genealogy promptfoo tasks as evidence sources only.
- **Eval**: The decisive evidence was artifact inspection plus bounded AI-first baselines on the reviewed `r19` chapters and upstream page HTML, not a new implementation run.

## Tasks

- [x] Inspect the reviewed `r19` chapters and upstream page HTML to classify the remaining inconsistency signatures
- [x] Run bounded AI-first baselines on representative page runs and a full problematic chapter
- [x] Determine whether the issue is still a local genealogy-table implementation or a broader consistency/canonicalization decision
- [x] Create and reframe ADR-001 around source-aware consistency alignment and selective re-extraction
- [x] Create a follow-up implementation story for the first concrete Onward slice under ADR-001
- [x] Update related docs and story links so future work points at the ADR + follow-up story instead of the old local-optimum framing
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: all findings point back to concrete artifacts and run outputs
  - [x] T1 — AI-First: measured strong-model capability before proposing new deterministic code
  - [x] T2 — Eval Before Build: bounded baselines were run and recorded before further implementation
  - [x] T3 — Fidelity: the investigation preferred source-aware strategies over HTML-only repair because local evidence showed better fidelity
  - [x] T4 — Modular: implementation was explicitly split into a new follow-up story instead of silently expanding this one
  - [x] T5 — Inspect Artifacts: reviewed live `output/runs/` artifacts, not just logs

## Workflow Gates

- [x] Build complete: the investigation/handoff slice is complete
- [x] Validation complete or explicitly skipped by user
- [x] Story rescope and closure applied

## Architectural Fit

- **Owning module / area**: Docs and decision framing only. No pipeline module ownership remains in this story.
- **Data contracts / schemas**: None changed. The story is intentionally closing before implementation.
- **File sizes**: N/A for implementation. This story closes specifically to avoid pushing more scope into oversized modules before the architecture settles.
- **Decision context**: Reviewed `docs/ideal.md`, `docs/spec.md`, `docs/runbooks/golden-build.md`, `docs/scout/scout-003-storybook-patterns.md`, Story 140, live `story140-onward-targeted-rescue-r19` artifacts, and ADR-001.

## Files to Modify

- `docs/stories/story-141-onward-genealogy-table-consistency-pass.md` — rescope to the delivered investigation and handoff slice
- `docs/decisions/adr-001-source-aware-consistency-strategy/adr.md` — capture the broader architecture question raised by this investigation
- `docs/stories/story-142-onward-source-aware-genealogy-consistency-first-slice.md` — hold the actual implementation follow-up
- `docs/stories.md` — update story titles/statuses and add the new follow-up story

## Redundancy / Removal Targets

- The original Story 141 implementation scope. It is now superseded by Story 142 plus ADR-001.

## Notes

- The key shift locked in here is strategic: the remaining problem is not best described as "HTML normalization." The stronger local question is how to achieve consistency through source-aware reruns and only use HTML normalization as a secondary tool when justified.
- The implementation follow-up should stay concrete and recipe-scoped even though the ADR is broader. Onward genealogy remains the best first validation slice because the repeated structure is obvious and measurable.

## Plan

Completed. No further build plan belongs in this story; implementation moved to Story 142.

## Work Log

20260314-1058 — story created: split chapter-level genealogy consistency normalization out of Story 140 after manual review of `story140-onward-targeted-rescue-r19` showed that page rescue recovered data but not chapter-wide structural consistency; next step is `/build-story` to evaluate AI-first normalization against the reviewed Arthur/Paul/George/Joe chapters
20260314-1511 — exploration + AI-first baseline grounded the problem in live artifacts and showed the next move was larger than a local table pass
- **Result:** Verified that the reviewed inconsistency is already present upstream in `pages_html_onward_tables_fixed.jsonl`, quantified the current chapter-level failure signatures, and measured bounded one-shot AI normalization on both contiguous page runs and a full problematic chapter. The strongest measured baseline (`gpt-5` on `chapter-014.html`) collapsed the mixed structure into one canonical genealogy table plus a separate summary table.
- **Impact:**
  - **Story-scope impact:** The original implementation seam was no longer trustworthy. This stopped Story 141 from silently becoming a larger architecture change hidden behind a table-specific title.
  - **Pipeline-scope impact:** The evidence showed a strong model over a broader scope can restore consistency better than current deterministic glue, which pushed the project toward a source-aware rerun strategy.
  - **Evidence:** `/Users/cam/Documents/Projects/codex-forge/output/runs/story140-onward-targeted-rescue-r19/01_load_artifact_v1/pages_html_onward_tables_fixed.jsonl`, `/Users/cam/Documents/Projects/codex-forge/output/runs/story140-onward-targeted-rescue-r19/output/html/chapter-010.html`, `/Users/cam/Documents/Projects/codex-forge/output/runs/story140-onward-targeted-rescue-r19/output/html/chapter-014.html`, `/tmp/story141_ai_baseline_pages40_41_gpt41.html`, `/tmp/story141_ai_baseline_pages40_45_gpt41.html`, `/tmp/story141_ai_baseline_ch14.html`
  - **Next:** Reframe the architecture question before building.
20260314-1840 — ADR kickoff: created `ADR-001` to frame this as a broader consistency decision, not just a genealogy-table tactic; next step is external research before deciding whether Story 141 stays open or closes around the investigation slice
20260314-1938 — rescope then close: user approved closing Story 141 around the delivered investigation and handoff work
- **Result:** Narrowed Story 141 to the slice it actually delivered: artifact investigation, AI-first baseline measurement, architectural reframing into ADR-001, and follow-up implementation split to Story 142.
- **Impact:**
  - **Story-scope impact:** Story 141 is now truthfully closed without pretending the implementation shipped.
  - **Pipeline-scope impact:** Future work now points at a source-aware consistency path instead of a premature HTML-repair local optimum.
  - **Evidence:** `docs/decisions/adr-001-source-aware-consistency-strategy/adr.md`, `docs/stories/story-142-onward-source-aware-genealogy-consistency-first-slice.md`, `/Users/cam/Documents/Projects/codex-forge/output/runs/story140-onward-targeted-rescue-r19/output/html/chapter-014.html`
  - **Next:** Research ADR-001, then build Story 142 against the accepted direction.
