---
title: "Establish a Structured Onward Genealogy Repair Target"
status: "Blocked"
priority: "High"
ideal_refs:
  - "Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Fidelity to Source, Traceability is the product, Dossier-ready output"
spec_refs:
  - "spec:2.1"
  - "spec:3.1"
  - "spec:5.1"
adr_refs:
  - "ADR-001"
  - "ADR-002"
depends_on:
  - "146"
  - "206"
category_refs:
  - "spec:2"
  - "spec:3"
  - "spec:5"
  - "spec:6"
  - "spec:7"
compromise_refs:
  - "C1"
  - "C3"
  - "C7"
input_coverage_refs:
  - "scanned-pdf-tables"
architecture_domains:
  - "document_structure_and_consistency"
  - "doc_web_runtime"
roadmap_tags:
  - "campaign:maintained-intake-honesty"
legacy_system: ""
---

# Story 219 — Establish a Structured Onward Genealogy Repair Target

**Priority**: High
**Status**: Blocked
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/decisions/adr-001-source-aware-consistency-strategy/adr.md`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/runbooks/document-consistency-planning.md`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/stories/story-144-onward-document-level-genealogy-consistency-planning.md`, `docs/stories/story-146-onward-plan-aware-genealogy-reruns.md`, `docs/stories/story-206-onward-full-book-regression-recovery.md`, and `None found after search in docs/scout/ and docs/notes/ for a narrower structured-repair ADR or runbook beyond ADR-001 and the current Onward story chain`
**Depends On**: Stories `146` and `206`

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

Story 146 proved that plan-aware direct-HTML reruns on the Onward genealogy seam
are actionable but plateaued: the rerun loop reduced pure-format issue count
from `21` to `19`, but it did not shrink the pure-format chapter set. Story 206
later restored the maintained full-book lane and regression guardrails without
changing that C7 plateau. This story should land the first structured or
row-oriented repair target for the maintained Onward repeated-structure seam:
emit an inspectable intermediate for planner-selected pages or chapters, rebuild
HTML from that target, and re-measure whether the pure-format chapter set can
finally shrink while preserving the mixed/conformant guardrails (`chapter-009`
mixed, `chapter-023` conformant). If the structured target still fails to beat
the direct-HTML plateau, the story should close with explicit blocker evidence
instead of silently promoting more complexity.

## Acceptance Criteria

- [x] A fresh current-pass baseline records the exact direct-HTML plateau from repo evidence:
  - [x] the work log cites the Story 146 result that pure-format issue count dropped `21 -> 19` while the pure-format chapter set stayed unchanged
  - [x] the work log cites the current `onward-document-consistency-planning` retry posture in `docs/evals/registry.yaml`, including the named `new-approach` / `architecture-change` trigger
  - [x] the story names the exact remaining pure-format chapters and the mixed/conformant guardrails the new target must preserve, then records the fresh maintained-lane remeasure that found no remaining pure-format chapter set on `onward-book-r1`
- [x] The story lands one bounded structured or row-oriented repair target:
  - [x] the chosen target emits an inspectable intermediate artifact with source-page provenance, planner family/rule context, and deterministic ownership of how repaired HTML is rebuilt
  - [x] the structured target stays bounded to the maintained Onward genealogy seam; it does not widen into a new generic document-wide runtime
  - [x] if the target needs new stamped fields across artifact boundaries, `schemas.py` is updated first; otherwise the intermediate remains a story-scoped sidecar contract
- [x] A fresh reused-artifact `driver.py` validation run honestly measures the new target:
  - [x] the run reuses the existing Onward planner/rerun/build substrate instead of re-running upstream OCR by default
  - [x] the post-repair conformance output either shrinks the pure-format chapter set relative to the Story 144 / Story 146 baseline while preserving `chapter-009.html` as mixed and `chapter-023.html` as conformant, or records explicit blocker evidence and does not claim improvement
  - [ ] manual inspection cites exact structured sidecar paths and rebuilt chapter artifacts for at least three formerly pure-format chapters plus one unchanged guardrail chapter
- [x] Canonical truth surfaces stay aligned with the result:
  - [x] if the structured target materially changes the manual C7 decision surface, `docs/evals/registry.yaml` is updated for `onward-document-consistency-planning`
  - [x] `tests/fixtures/formats/_coverage-matrix.json` and methodology state remain unchanged unless the maintained `scanned-pdf-tables` support claim itself changes
  - [x] after `make methodology-compile`, generated `docs/stories.md` and `docs/methodology/graph.json` reflect the new story and stay consistent with authored truth

## Out of Scope

- Generalizing the structured repair target beyond the maintained Onward genealogy seam
- Deleting the document-consistency planning layer or claiming `C7` is resolved
- Reopening handwritten OCR, Washington access work, or unrelated intake-routing lines
- Manual edits to generated HTML, structured rows, or conformance artifacts outside the pipeline
- A broad whole-document re-extraction redesign if a bounded planner-selected structured target is sufficient
- Reopening the `Docling` replacement path or changing the accepted `doc-web` boundary from ADR-002

## Approach Evaluation

- **Simplification baseline**: already measured negatively at this validation boundary. Story 146 proved that direct-HTML plan-aware reruns can reduce issue severity but not shrink the pure-format chapter set, so this story should re-freeze that plateau rather than pretend a single direct-HTML LLM call is still an untested baseline.
- **AI-only**: a direct model call could emit a structured row representation for a bounded set of pages, but by itself it is too opaque on provenance, rebuild ownership, and acceptance/fallback discipline.
- **Hybrid**: likely strongest. Reuse the planner, rerun targeting, and maintained build path; let AI emit the structured or row-oriented repair target for selected pages; then use deterministic rebuild and conformance checks to decide whether the new target actually beats the plateau.
- **Pure code**: likely insufficient. HTML-only normalization already exists in bounded form and is part of the plateau; pure code risks repeating the same failure class without improving row semantics.
- **Repo constraints / prior decisions**: ADR-001 explicitly says the next experiment after direct-HTML plateau can be a structured or row-oriented repair target. Story 146 proved the planner-guided rerun seam but left the chapter set unchanged. Story 206 restored the maintained full-book proof and guardrails, so this story must stay bounded and honest on the maintained lane instead of becoming another speculative spike. ADR-002 keeps the `doc-web` bundle boundary inspectable and unchanged.
- **Existing patterns to reuse**: `modules/validate/plan_onward_document_consistency_v1`, `modules/adapter/rerun_onward_genealogy_consistency_v1`, `modules/adapter/table_rescue_onward_tables_v1`, `modules/common/onward_genealogy_html.py`, `modules/validate/validate_onward_genealogy_consistency_v1`, `configs/recipes/story-146-onward-plan-aware-genealogy-reruns-validate.yaml`, `configs/recipes/recipe-onward-pdf-html-mvp.yaml`, and the story-scoped repair-module pattern in `modules/transform/repair_docling_onward_genealogy_v1`
- **Eval**: the deciding proof is a fresh reused-artifact `driver.py` run on the same maintained Onward seam plus manual inspection of both the structured sidecars and rebuilt chapters. If the structured target materially changes the C7 decision surface, update `onward-document-consistency-planning` in `docs/evals/registry.yaml`.

## Tasks

- [x] Freeze the current plateau from repo evidence before adding new logic:
  - [x] inspect the Story 146 validation artifacts and record the exact remaining pure-format chapter set, mixed/conformant guardrails, and why direct-HTML reruns plateaued
  - [x] inspect the maintained Onward lane from Story 206 so the new target starts from the current guarded runtime rather than from stale story-local evidence
  - [x] record the exact `onward-document-consistency-planning` retry trigger and what this story is supposed to falsify
- [x] Define the smallest honest structured-target contract before implementation:
  - [x] choose whether the intermediate is row JSON, grouped row HTML fragments, or another bounded structured representation
  - [x] preserve source-page provenance, planner family IDs, issue classes, and deterministic rebuild ownership
  - [x] if the target must cross stage boundaries as a stamped artifact, add the schema to `schemas.py`; otherwise keep it as a story-scoped sidecar
- [x] Implement the smallest story-scoped structured repair lane:
  - [x] add a new bounded repair module and validation recipe that reuse the existing planner/rerun/build substrate
  - [x] keep the direct-HTML path available as the baseline or fallback instead of deleting it during the experiment
  - [x] emit explicit structured sidecars, repaired page/chapter outputs, and acceptance or fallback reports
- [x] Add focused regression coverage for the structured target:
  - [x] contract tests for the new intermediate artifact
  - [x] acceptance or fallback behavior when the structured target helps versus when it regresses
  - [x] before/after conformance checks proving the story shrinks the pure-format chapter set or records a blocker honestly
- [x] Run required real-pipeline verification:
  - [x] clear stale `*.pyc`
  - [x] run the story-scoped `driver.py` validation recipe
  - [x] verify artifacts in `output/runs/`
  - [x] manually inspect representative structured sidecars and rebuilt chapters
- [ ] If this story changes documented format coverage or graduation reality: update `tests/fixtures/formats/_coverage-matrix.json` and any relevant methodology state honestly
- [ ] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [ ] If agent tooling changed: `make skills-check`
- [x] If evals or goldens changed: update `docs/evals/registry.yaml` for `onward-document-consistency-planning`
- [ ] Search all docs and update any related to what we touched
- [ ] Verify Central Tenets:
  - [ ] T0 — Traceability: the structured target and rebuilt output trace to source pages, planner artifacts, and final acceptance decisions
  - [ ] T1 — AI-First: use AI for the row-aware extraction/repair judgment instead of hardcoding more brittle HTML rewrites
  - [ ] T2 — Eval Before Build: freeze the direct-HTML plateau before adding the structured target
  - [ ] T3 — Fidelity: preserve source wording, grouping, and table semantics without silently flattening rows
  - [ ] T4 — Modular: keep the new target recipe-scoped and bounded to the Onward seam instead of spreading assumptions through generic runtime code
  - [ ] T5 — Inspect Artifacts: manually inspect structured sidecars and rebuilt HTML, not just the conformance summary

## Workflow Gates

- [ ] Build complete: implementation finished, required checks run, and summary shared
- [ ] Validation complete or explicitly skipped by user
- [ ] Story marked done via `/mark-story-done`

## Blocker Summary

Fresh Story 219 validation on the maintained `onward-book-r1` seam no longer
exposes any `format_drift` chapters, so the new structured repair lane has zero
planner-selected pages to process. The current maintained truth is two
`row_semantic_issue` chapters (`chapter-009.html`, `chapter-022.html`) plus
`chapter-023.html` conformant, not the old Story 146 pure-format plateau.

## Blocker Evidence

- `output/runs/story219-onward-structured-repair-r1/05_plan_onward_document_consistency_v1/conformance_report_before.json`
  reports `format_drift_chapters: []`, `row_semantic_issue_chapters:
  ["chapter-009.html", "chapter-022.html"]`, and `chapter-023.html`
  conformant before any direct-HTML rerun.
- `output/runs/story219-onward-structured-repair-r1/06_rerun_onward_genealogy_consistency_v1/rerun_onward_genealogy_summary.json`
  reports `targeted_page_count: 0`, so the direct-HTML control path had no
  remaining planner-selected format-drift pages either.
- `output/runs/story219-onward-structured-repair-r1/09_repair_onward_genealogy_structured_v1/structured_onward_genealogy_summary.json`
  likewise reports `targeted_page_count: 0`, which means the new structured lane
  is implemented but cannot be exercised honestly on the current maintained seam.
- Manual artifact inspection confirms the planner's remaining issues are
  row-semantic, not pure-format:
  `output/runs/story219-onward-structured-repair-r1/output/html/chapter-022.html`
  still contains `Therese | , 1925 | ... | 6 months old`, and
  `output/runs/story219-onward-structured-repair-r1/output/html/chapter-009.html`
  still contains `Lana ... | 1-Kassandra`, while
  `output/runs/story219-onward-structured-repair-r1/output/html/chapter-023.html`
  remains a clean conformant reference chapter.

## Unblock Condition

Only resume this story if a maintained repeated-structure lane again exposes a
non-empty `format_drift` chapter set, or if a second repeated-structure
document is packaged with the same planner/conformance surface so the
structured repair target has a real C7 target to measure. If the next active
problem is row-semantic note placement instead, open a new story/eval for that
lane instead of forcing it through this C7 format-drift story.

## Architectural Fit

- **Owning module / area**: a new bounded repair module under `modules/transform/` or `modules/adapter/` is the likely owner for the structured target, with `modules/common/onward_genealogy_html.py` or `build_chapter_html_v1` only touched if the rebuilt HTML needs a small shared stitch hook. `plan_onward_document_consistency_v1` and `validate_onward_genealogy_consistency_v1` remain the conformance owners.
- **Methodology reality**: this story sits across `spec:2`, `spec:3`, `spec:5`, `spec:6`, and `spec:7`. In `docs/methodology/state.yaml`, those category substrates exist and `C1`, `C3`, and `C7` remain active `climb` seams. The relevant coverage row is `scanned-pdf-tables`, which currently remains `passing` on the maintained Onward lane (`structure_preservation = 0.95`, measured `2026-04-10`), so this story must not widen or narrow support claims by inertia.
- **Substrate evidence**: verified in this pass that the repo already has the document-level planner (`modules/validate/plan_onward_document_consistency_v1/main.py`), the plan-aware rerun adapter (`modules/adapter/rerun_onward_genealogy_consistency_v1/main.py`), deterministic genealogy normalization helpers (`modules/adapter/table_rescue_onward_tables_v1/main.py`, `modules/common/onward_genealogy_html.py`), the maintained Onward recipe (`configs/recipes/recipe-onward-pdf-html-mvp.yaml`), and the story-scoped validation recipe from Story 146 (`configs/recipes/story-146-onward-plan-aware-genealogy-reruns-validate.yaml`). During implementation this story added the missing structured target as `modules/transform/repair_onward_genealogy_structured_v1/` plus a Story 219 validation recipe and tests. The current blocker is no longer missing code substrate; it is missing maintained-lane `format_drift` targets to exercise against.
- **Data contracts / schemas**: current relevant contracts are `page_html_v1`, `chapter_html_manifest_v1`, `pipeline_issues_v1`, plus the planner sidecars `pattern_inventory`, `consistency_plan`, and `conformance_report`. No row-structured schema is verified in repo today. If the new intermediate crosses module boundaries as a stamped artifact, add it to `schemas.py` first; otherwise keep it as a story-scoped JSON sidecar.
- **File sizes**: `modules/adapter/rerun_onward_genealogy_consistency_v1/main.py` is `1770` lines, `modules/adapter/table_rescue_onward_tables_v1/main.py` is `1434`, `modules/common/onward_genealogy_html.py` is `705`, `modules/validate/plan_onward_document_consistency_v1/main.py` is `1225`, `modules/validate/validate_onward_genealogy_consistency_v1/main.py` is `772`, `tests/test_rerun_onward_genealogy_consistency_v1.py` is `1529`, `tests/test_build_chapter_html.py` is `2118`, `docs/evals/registry.yaml` is `2084`, and `tests/fixtures/formats/_coverage-matrix.json` is `570`. Prefer a new bounded module plus focused tests over further bloating the existing large files unless a small shared hook is clearly cleaner.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-001, ADR-002, `docs/runbooks/document-consistency-planning.md`, `docs/evals/registry.yaml`, Stories 144/146/206, the maintained `scanned-pdf-tables` coverage row, and the current Onward repair modules/recipes. Search across `docs/scout/` and `docs/notes/` found no narrower owner for this structured-repair follow-up beyond ADR-001 and the existing Onward story chain.

## Files to Modify

- `docs/stories/story-219-onward-structured-genealogy-repair-target.md` — story record, work log, and validation evidence
- `modules/transform/repair_onward_genealogy_structured_v1/main.py` — likely new bounded structured or row-oriented repair target for planner-selected Onward pages or chapters (new file)
- `modules/transform/repair_onward_genealogy_structured_v1/module.yaml` — module contract for the new structured repair target (new file)
- `configs/recipes/story-219-onward-structured-genealogy-repair-target-validate.yaml` — story-scoped validation recipe that reuses planner/rerun/build substrate and re-measures conformance (new file)
- `modules/adapter/rerun_onward_genealogy_consistency_v1/main.py` — only if the new target reuses or extends the existing planner-target selection / fallback reports (`1770` lines)
- `modules/common/onward_genealogy_html.py` — shared row-to-HTML stitch helpers if the new target emits a structured intermediate before rebuild (`705` lines)
- `modules/validate/plan_onward_document_consistency_v1/main.py` — only if the planner or conformance artifacts need a narrow hook for the new structured target (`1225` lines)
- `tests/test_repair_onward_genealogy_structured_v1.py` — focused coverage for the new structured-target contract and rebuild path (new file)
- `tests/test_rerun_onward_genealogy_consistency_v1.py` — extend only if target selection or fallback ownership changes (`1529` lines)
- `tests/test_build_chapter_html.py` or `tests/test_table_rescue_onward_tables_v1.py` — update only if shared rebuild behavior changes (`2118` / `518` lines)
- `docs/evals/registry.yaml` — update the manual C7 eval only if the story materially changes the decision surface (`2084` lines)
- `tests/fixtures/formats/_coverage-matrix.json` — update only if the maintained `scanned-pdf-tables` truth changes (`570` lines)

## Redundancy / Removal Targets

- The assumption that direct-HTML plan-aware reruns are the only honest repair target for the maintained Onward seam
- Duplicated row-heading or subgroup normalization logic split between `rerun_onward_genealogy_consistency_v1` and `table_rescue_onward_tables_v1` if the new structured target centralizes that ownership cleanly
- Any temporary story-scoped structured artifact contract that proves no better than the existing direct-HTML path

## Notes

- A new story ID is honest here. Story 146 already closed the planner-guided direct-HTML rerun line with a plateau, and Story 206 later restored the maintained full-book lane and guardrails on top of that result. This follow-up changes the repair target itself and introduces a new validation boundary, so expanding or reopening Story 146 would blur a completed proof line with a materially different experiment.
- The alternate C7 follow-up named in `docs/evals/registry.yaml` is a second repeated-structure document. This story chooses the structured repair target first because the necessary Onward substrate already exists in repo today, while a second-document path would first need new fixture, corpus, and validation packaging.
- The story should prefer a bounded story-scoped module and recipe first. Promotion into the main maintained recipe is a later decision unless the validation run proves the structured target is clearly better and operationally simple.

## Plan

The structured repair target has been implemented and validated, but the next
move is no longer immediate implementation work.

Current blocker truth:

1. Fresh maintained-lane measurement on `story219-onward-structured-repair-r1`
   shows `format_drift_chapters: []` before any direct-HTML rerun, so the old
   Story 146 plateau is not the active maintained-lane reality anymore.
2. Because both the direct-HTML control stage and the new structured stage
   receive `0` planner-selected format-drift pages, this story cannot honestly
   prove or disprove structured improvement on its intended seam.
3. The remaining maintained issues are row-semantic note-placement defects in
   `chapter-009.html` and `chapter-022.html`, which belong in a different story
   or eval lane.

Visible next move:

- Keep the implemented structured lane as a bounded story-scoped harness.
- Do not promote it into the maintained recipe while the current maintained seam
  has no format-drift target set.
- Only resume this story if a maintained repeated-structure seam regresses into
  `format_drift` again or a second repeated-structure document is packaged with
  the same planner surface.

## Work Log

20260412-1544 — create-story: created Story 219 after `/triage` identified the first still-actionable C7 follow-up and the user approved it. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-001, ADR-002, `docs/runbooks/document-consistency-planning.md`, `docs/evals/registry.yaml`, Stories 144/146/206, the maintained `scanned-pdf-tables` coverage row, `modules/validate/plan_onward_document_consistency_v1/main.py`, `modules/adapter/rerun_onward_genealogy_consistency_v1/main.py`, `modules/adapter/table_rescue_onward_tables_v1/main.py`, `modules/common/onward_genealogy_html.py`, and the Story 146 / maintained Onward recipes. Result: a new ID is honest instead of reopening Story 146 because the direct-HTML plan-aware rerun line already closed with a plateau, while this follow-up changes the repair target to a structured or row-oriented intermediate and introduces a new validation boundary. Verified substrate in repo: planner artifacts, rerun/build validation recipes, and maintained full-book guardrails all exist; missing substrate is only the new structured repair target itself, which makes the story concrete and honestly buildable now. Next step: `/build-story` should freeze the current plateau, choose the smallest structured artifact contract, and validate whether it can shrink the remaining pure-format chapter set.
20260412-1556 — build-story exploration: verified Story 219 remains honestly `Pending` after tracing the relevant maintained Onward seam in code and docs. Consulted `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-001, ADR-002, `docs/runbooks/document-consistency-planning.md`, `docs/evals/registry.yaml`, Stories 144/146/206, `tests/fixtures/formats/_coverage-matrix.json`, `configs/recipes/recipe-onward-pdf-html-mvp.yaml`, `configs/recipes/story-146-onward-plan-aware-genealogy-reruns-validate.yaml`, `modules/validate/plan_onward_document_consistency_v1/main.py`, `modules/adapter/rerun_onward_genealogy_consistency_v1/main.py`, `modules/adapter/table_rescue_onward_tables_v1/main.py`, `modules/common/onward_genealogy_html.py`, `modules/validate/validate_onward_genealogy_consistency_v1/main.py`, `modules/transform/repair_docling_onward_genealogy_v1/main.py`, and `schemas.py`. Files likely to change are this story, a new story-scoped structured repair module under `modules/transform/`, a new validation recipe, focused tests, and only narrow shared hooks if rebuild stitching needs them; high-risk existing files are the already-large rerun/table-rescue/planner modules and `schemas.py` because stamped fields can be dropped if the boundary is chosen incorrectly. Verified substrate: planner artifacts, plan-aware rerun wiring, deterministic genealogy HTML normalization helpers, and maintained Onward recipes all exist in repo; missing substrate: there is still no structured/row-oriented repair target for the maintained seam and no pre-existing stamped row schema to adopt. Relevant methodology state in this pass: `C7` remains active `climb`, `scanned-pdf-tables` stays `passing`, and the Story 146 / eval baseline is explicit (`12` pure-format chapters, `chapter-009.html` mixed, `chapter-023.html` conformant, issue count `21 -> 19` without chapter-set shrink). Patterns to follow: bounded story-scoped module + recipe first, reuse upstream artifacts instead of re-running OCR, keep direct HTML as the measured control path, and prefer inspectable sidecars over hidden prompt-only normalization. Surprise found: reusable Story 144 artifacts still exist under `/Users/cam/Documents/Projects/codex-forge/output/runs/`, but this worktree currently has no local `output/runs/` tree and the historical Story 206 proof-run paths cited in the story are no longer present, so the eventual validation path must make artifact bootstrap/reuse explicit. Next step: regenerate methodology views, present the written implementation plan, and stop at the approval gate before any code changes.
20260412-1744 — implementation and validation: switched the story to active work, added `modules/transform/repair_onward_genealogy_structured_v1/{module.yaml,main.py}`, added story-scoped recipe `configs/recipes/story-219-onward-structured-genealogy-repair-target-validate.yaml`, and added focused regressions in `tests/test_repair_onward_genealogy_structured_v1.py`. The new module reuses Story 146 planner target selection, asks the model for structured genealogy JSON, deterministically renders it back into page HTML, and writes inspectable sidecars/reports without creating a new stamped schema boundary. Verification in this pass: `python -m pytest tests/test_repair_onward_genealogy_structured_v1.py`, `python -m pytest tests/test_rerun_onward_genealogy_consistency_v1.py tests/test_repair_onward_genealogy_structured_v1.py`, `make lint`, `make test`, and fresh driver run `python driver.py --recipe configs/recipes/story-219-onward-structured-genealogy-repair-target-validate.yaml --run-id story219-onward-structured-repair-r1 --allow-run-id-reuse --force` after clearing stale `*.pyc`. Impact of the fresh driver run is blocker evidence, not improvement: `output/runs/story219-onward-structured-repair-r1/05_plan_onward_document_consistency_v1/conformance_report_before.json`, `.../08_plan_onward_document_consistency_v1/conformance_report_after_direct_rerun.json`, and `.../12_plan_onward_document_consistency_v1/conformance_report_after_structured_repair.json` all report `format_drift_chapters: []`, `row_semantic_issue_chapters: ["chapter-009.html", "chapter-022.html"]`, and `chapter-023.html` conformant. The direct-HTML control stage and the new structured stage both had `targeted_page_count: 0` (`.../06_rerun_onward_genealogy_consistency_v1/rerun_onward_genealogy_summary.json`, `.../09_repair_onward_genealogy_structured_v1/structured_onward_genealogy_summary.json`), so the current maintained seam no longer reproduces the old pure-format plateau this story was created to attack. Manual artifact inspection confirmed the remaining defects are row-semantic note-placement problems rather than pure-format drift: `output/runs/story219-onward-structured-repair-r1/output/html/chapter-022.html` contains `Therese | , 1925 |  |  |  |  | 6 months old`, `output/runs/story219-onward-structured-repair-r1/output/html/chapter-009.html` contains `Lana | May 16, 1968 |  | Dave Bury | 2 Boys Kevin, Kristopher |  | 1-Kassandra`, and `output/runs/story219-onward-structured-repair-r1/output/html/chapter-023.html` keeps `TOTAL DESCENDANTS | 38` as a clean conformant reference. Result: mark the story `Blocked` on stale premise / missing maintained-lane format-drift targets, update the eval registry, and only resume this lane if a maintained repeated-structure target reappears or a second repeated-structure document is packaged.
