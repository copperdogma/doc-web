# Story 144 — Onward Document-Level Genealogy Consistency Planning

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Fidelity to Source, Dossier-ready output
**Spec Refs**: spec:2.1 C1 (Multi-Stage OCR Pipeline), spec:1.1 C2 (Format-Specific Conversion Recipes), spec:2.2 C6 (Expensive OCR for Quality)
**Decision Refs**: `docs/decisions/adr-001-source-aware-consistency-strategy/adr.md`, Story 143 work log, manual artifact review of `story143-onward-genealogy-reruns-r1`
**Depends On**: Story 143

## Goal

Implement the first document-level consistency-planning slice under ADR-001 for the Onward genealogy corpus: analyze the whole extracted/built artifact set, discover repeated genealogy pattern families across the document, emit explicit `pattern_inventory`, `consistency_plan`, and `conformance_report` artifacts, and make the chosen document-local conventions inspectable before further repair automation widens.

## Acceptance Criteria

- [x] In a reused-artifact validation run, the pipeline emits inspectable document-level artifacts for the Onward genealogy slice: `pattern_inventory`, `consistency_plan`, and `conformance_report`, each with provenance back to chapters and source pages
- [x] Manual inspection confirms those artifacts capture the main consistency failure classes already seen in the current run, including fragmented multi-table chapters, concatenated subgroup/context headings, fused `BOY/GIRL` headers, and left-column-only family rows
- [x] The emitted `consistency_plan` records document-local conventions chosen for each detected pattern family, including subgroup/context-row treatment, table-fragmentation expectations, summary-row handling, and how marginal/handwritten note content should be represented when present
- [x] The emitted `conformance_report` distinguishes format-consistency violations from row-semantic extraction issues, so cases like `chapter-009.html` handwritten child-note placement are not silently conflated with pure table-format drift
- [x] In the reused-artifact validation run, the `conformance_report` surfaces the currently missed manual format failures in `chapter-011.html`, `chapter-012.html`, `chapter-013.html`, `chapter-014.html`, `chapter-018.html`, and `chapter-019.html`, while routing `chapter-009.html` into a mixed row-semantic-containing bucket instead of pure format drift

## Out of Scope

- A rigid cross-document genealogy formatting rulebook
- Repairing every flagged chapter in the same story
- Broader run-aware extraction redesign across the whole Onward recipe
- Hand-editing generated HTML outside the pipeline
- Closing ADR-001 itself

## Approach Evaluation

- **Simplification baseline**: Run a single whole-document AI analysis pass over the current extracted/built genealogy artifacts and ask it to identify repeated pattern families plus a proposed document-local consistency plan.
- **AI-only**: Plausible for `pattern_inventory` and `consistency_plan`, but insufficient alone because provenance linking, chapter/page membership, and conformance measurements still need deterministic support.
- **Hybrid**: Leading candidate. Use AI for whole-document pattern discovery and policy drafting, then deterministic code for membership mapping, metrics, provenance, and conformance checks.
- **Pure code**: Not credible as the main planning engine because the document-local conventions are not knowable ahead of time and should not be hardcoded from Onward-specific heuristics.
- **Repo constraints / prior decisions**: ADR-001 now treats chapter-level gating as an early seam only. Story 143 proved that targeted reruns can help, but manual inspection also showed that the current validator misses real document-level inconsistency classes.
- **Existing patterns to reuse**: `validate_onward_genealogy_consistency_v1`, `rerun_onward_genealogy_consistency_v1`, Story 143's validation recipe, and existing report-sidecar patterns.
- **Eval**: The deciding test is whether the emitted planning artifacts explain the manually observed failures across the document better than the current chapter-first detector does.

## Tasks

- [x] Inspect the current Onward genealogy outputs and enumerate the main document-level consistency failure classes the planning artifacts must explain
- [x] Define the first artifact contracts for `pattern_inventory`, `consistency_plan`, and `conformance_report`, including provenance back to chapters, pages, and example snippets
- [x] Build a compact document-consistency dossier from chapter/page summaries and representative snippets so the AI planning pass can reason at document scope without consuming raw full-document HTML
- [x] Implement the smallest document-level planning pass that can emit those artifacts from reused Onward artifacts without re-running OCR
- [x] Add focused regression coverage for pattern-family detection, plan emission, conformance classification, and at least one distinction between format drift and row-semantic extraction errors
- [x] Run the reused-artifact validation path and manually inspect the emitted planning artifacts against the known chapter failures
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: cleared stale `*.pyc`, ran through `driver.py`, verified artifacts in `output/runs/`, and manually inspected sample JSON/JSONL data
  - [x] Agent tooling unchanged; `make skills-check` not needed
- [x] Evals/goldens unchanged; recorded the new manual planning eval in `docs/evals/registry.yaml`
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every detected pattern family and conformance failure traces back to chapters, pages, and source artifacts
  - [x] T1 — AI-First: the planning pass uses AI for document-local reasoning instead of hardcoding Onward-specific formatting rules
  - [x] T2 — Eval Before Build: the planning artifacts are measured against the observed Story 143 failures before broader repair automation changes again
  - [x] T3 — Fidelity: the plan preserves source meaning and does not normalize by deleting or flattening distinctions
  - [x] T4 — Modular: the planning pass is recipe-scoped and does not assume every future document has the same genealogy conventions
  - [x] T5 — Inspect Artifacts: manually inspect the planning artifacts and corresponding HTML chapters, not just the generated scores

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: Likely a new recipe-scoped validate/report stage after build, extending or eventually superseding the current chapter-first genealogy detector for this recipe.
- **Data contracts / schemas**: Prefer explicit sidecar JSON/JSONL artifacts for `pattern_inventory`, `consistency_plan`, and `conformance_report`, with a stamped summary artifact only if the existing report schemas remain useful.
- **File sizes**: `modules/validate/validate_onward_genealogy_consistency_v1/main.py` and `modules/adapter/rerun_onward_genealogy_consistency_v1/main.py` already carry narrow story-specific logic. Prefer a focused new planning module over further growth inside those files unless reuse is clearly cleaner.
- **Decision context**: Reviewed ADR-001, Story 143, and manual inspection findings from `story143-onward-genealogy-reruns-r1`. The key architectural change is moving from narrow hard-page follow-up to document-wide pattern discovery with explicit plan artifacts.

## Files to Modify

- `modules/validate/plan_onward_document_consistency_v1/module.yaml` — likely new document-level planning stage
- `modules/validate/plan_onward_document_consistency_v1/main.py` — likely new pattern discovery / plan / conformance stage
- `configs/recipes/story-144-onward-document-consistency-plan-validate.yaml` — likely reused-artifact validation recipe
- `tests/test_plan_onward_document_consistency_v1.py` — focused planning-artifact coverage
- `docs/stories/story-144-onward-document-level-genealogy-consistency-planning.md` — build/implementation work log
- `docs/decisions/adr-001-source-aware-consistency-strategy/adr.md` — update if the artifact contracts or workflow boundary tighten further

## Redundancy / Removal Targets

- Any temporary Story 143 inspection probes that remain once the document-level planning pass owns the consistency-analysis path
- Parts of the current chapter-first detector that become redundant if the document-level planning artifacts supersede its narrow drift report

## Notes

- Manual inspection of `story143-onward-genealogy-reruns-r1` showed broader format inconsistency than the current validator reports:
  - fragmented multi-table chapters in `chapter-010.html`, `chapter-012.html`, `chapter-013.html`, `chapter-014.html`, `chapter-018.html`, and `chapter-019.html`
  - concatenated subgroup/context headings in `chapter-011.html`
  - fused `BOY/GIRL` headers plus bad subgroup-row shape in `chapter-016.html`, `chapter-017.html`, `chapter-021.html`, and `chapter-022.html`
  - row-semantic handwritten-note placement issues in `chapter-009.html`, which likely belong to a different failure class than pure format consistency
- Story 143's final reused-artifact run accepted `13/14` bounded coarse pages and materially improved the reviewed bad set, but that run also showed that the current validator can pass chapters whose format is still visibly inconsistent.
- The document-level planning artifacts should make it obvious whether the AI made a bad policy choice or made a good policy choice that later repair steps executed badly.
- A future user-guided loop should be able to revise the emitted `consistency_plan` and re-run using that updated plan instead of relying on hidden prompt changes.

## Plan

### Build-readiness note

- Story 144 was still marked `Draft`, but the acceptance criteria, tasks, and architectural fit were already detailed enough to build. This pass treats the `Draft` status as stale and promotes the story directly to active build planning.

### Baseline / success signal

- Current baseline from `story143-onward-genealogy-reruns-r1` shows why a new planning layer is needed instead of more threshold tuning:
  - the chapter-first validator flags only `5` chapters: `chapter-010.html`, `chapter-016.html`, `chapter-017.html`, `chapter-021.html`, `chapter-022.html`
  - manual review found `11` format-consistency failures plus `1` row-semantic issue
  - the current detector misses at least `6` manual format failures outright: `chapter-011.html`, `chapter-012.html`, `chapter-013.html`, `chapter-014.html`, `chapter-018.html`, `chapter-019.html`
- Story 144 succeeds when the emitted planning artifacts explain those misses better than the current chapter-first detector does, while keeping `chapter-009.html` in a non-format bucket.

### Task 1 — Freeze the planning artifact contract and baseline dossier

- **Files**: [story-144-onward-document-level-genealogy-consistency-planning.md](/Users/cam/.codex/worktrees/72eb/codex-forge/docs/stories/story-144-onward-document-level-genealogy-consistency-planning.md), likely [test_plan_onward_document_consistency_v1.py](/Users/cam/.codex/worktrees/72eb/codex-forge/tests/test_plan_onward_document_consistency_v1.py)
- **Change**:
  - Define the exact first-pass contracts for `pattern_inventory`, `consistency_plan`, and `conformance_report`.
  - Freeze the manual-review baseline chapters and failure classes into fixtures/assertions.
  - Define the compact dossier shape the AI planner will consume: per-chapter fingerprints, table/header counts, subgroup/context signals, representative snippets, source-page membership, and manually useful example paths.
- **Impact / risk**:
  - This is the key small scope expansion discovered during exploration. A single whole-document AI call over raw built HTML is too prompt-size fragile; the planner needs a compressed document dossier first.
  - If the dossier is too lossy, the AI planner will not see enough evidence to infer sane document-local conventions.
- **Done when**:
  - The story and tests agree on the artifact contracts and baseline failure corpus before implementation code starts.

### Task 2 — Implement the document-level planning module

- **Files**: [module.yaml](/Users/cam/.codex/worktrees/72eb/codex-forge/modules/validate/plan_onward_document_consistency_v1/module.yaml), [main.py](/Users/cam/.codex/worktrees/72eb/codex-forge/modules/validate/plan_onward_document_consistency_v1/main.py)
- **Change**:
  - Add a new validate/report stage that reads built chapter HTML plus the reused `page_html_v1` artifact.
  - Build the compact dossier deterministically.
  - Run one document-level AI planning pass over that dossier to propose pattern families and document-local conventions.
  - Normalize the result into explicit sidecar artifacts:
    - `pattern_inventory`
    - `consistency_plan`
    - `conformance_report`
  - Emit a stamped summary artifact only as needed for pipeline integration, ideally reusing `pipeline_issues_v1` instead of inventing a new shared schema.
- **Impact / risk**:
  - Main risk is not model quality but contract hygiene. If new fields are expected in stamped JSONL without schema support, they will be dropped.
  - This stage should stay recipe-scoped and report-only; it should not mutate page HTML or replace Story 143's rerun path yet.
- **Done when**:
  - A driver-run stage can emit the three document-level artifacts with provenance back to chapters and pages.

### Task 3 — Add story-scoped recipe wiring and focused regression coverage

- **Files**: [story-144-onward-document-consistency-plan-validate.yaml](/Users/cam/.codex/worktrees/72eb/codex-forge/configs/recipes/story-144-onward-document-consistency-plan-validate.yaml), [test_plan_onward_document_consistency_v1.py](/Users/cam/.codex/worktrees/72eb/codex-forge/tests/test_plan_onward_document_consistency_v1.py)
- **Change**:
  - Create a reused-artifact validation recipe that loads the existing Onward artifacts, builds chapters, and runs the new planning stage.
  - Add tests for:
    - dossier generation
    - plan artifact emission
    - conformance classification
    - distinction between format drift and row-semantic issues
    - at least one assertion covering the currently missed manual format chapters
- **Impact / risk**:
  - Without this recipe, the module will be easy to unit test but hard to validate against the real artifact set.
  - Without the chapter-009 distinction test, the planner can regress into “everything is format drift.”
- **Done when**:
  - The story-scoped recipe runs end-to-end and the tests lock in the baseline distinctions.

### Task 4 — Validate artifacts and decide what gets superseded

- **Files**: [story-144-onward-document-level-genealogy-consistency-planning.md](/Users/cam/.codex/worktrees/72eb/codex-forge/docs/stories/story-144-onward-document-level-genealogy-consistency-planning.md), [adr.md](/Users/cam/.codex/worktrees/72eb/codex-forge/docs/decisions/adr-001-source-aware-consistency-strategy/adr.md), possibly [docs/evals/registry.yaml](/Users/cam/.codex/worktrees/72eb/codex-forge/docs/evals/registry.yaml)
- **Change**:
  - Run `make test`, `make lint`, and a real `driver.py` validation run with artifact reuse.
  - Manually inspect the three planning artifacts against the known chapters.
  - Decide whether the current chapter-first validator is now only an upstream signal producer or still a necessary companion.
  - If the new artifact contract is stable enough, record the missing eval entry this story reveals.
- **Impact / risk**:
  - The planning artifacts are only valuable if they are more explanatory than the current detector and usable by future rerun stages.
  - If the artifacts are hand-wavy or too generic to map back to specific chapters/pages, the story has not actually advanced the architecture.
- **Done when**:
  - Artifact paths, inspected sample data, and the current supersession boundary are recorded in the work log.

### Scope adjustments folded into this build

- Small coherent expansion: add the compact dossier layer before the AI planning pass. This is necessary to make document-wide planning stable and inspectable.
- Small coherent deferral: do not wire the new planning stage into the main Onward recipe yet unless the story-scoped validation run proves the artifact contract is genuinely ready for that promotion.

### Human-approval blockers

- No new dependency is expected if the planner stays on existing AI/runtime surfaces.
- Avoid introducing a new stamped schema unless the summary artifact truly needs one; sidecar JSON/JSONL is the safer first slice.
- If implementation evidence shows the planner needs a structured intermediate representation instead of direct chapter/page dossier snippets, pause and surface that as a larger architectural expansion.

## Work Log

20260314-2352 — story created: captured the residual follow-up after Story 143 proved selective reruns work for much of the reviewed genealogy slice but left clear consistency gaps
20260315-1027 — story reframed: manual inspection and architecture discussion widened this from a single hard-page fix to the first document-level consistency-planning slice, centered on `pattern_inventory`, `consistency_plan`, and `conformance_report`
20260315-1114 — build-story exploration: reviewed ADR-001, Story 143's final run artifacts, `validate_onward_genealogy_consistency_v1`, `rerun_onward_genealogy_consistency_v1`, and the reused validation recipe; found the current chapter-first validator flags only `5` chapters after Story 143 and misses `6` manually confirmed format failures (`011/012/013/014/018/019`), which proves Story 144 needs a new document-level planning stage rather than more threshold tuning
20260315-1114 — build-story plan: promoted the story to active planning, tightened acceptance around the currently missed manual-format chapters versus `chapter-009.html` row-semantic issues, and planned the first implementation slice around a compact document dossier plus a new recipe-scoped planning module and validation recipe
20260315-1348 — implementation landed: added `plan_onward_document_consistency_v1`, the story-scoped reuse recipe, and focused tests covering dossier generation, artifact emission, row-semantic heuristics, and stable-model fallback when the primary planner returns empty or malformed structured output
20260315-1758 — real-pipeline validation run `story144-onward-document-consistency-plan-r5`: `driver.py` completed with `make test`, `make lint`, and `git diff --check` green; the stage emitted [pattern_inventory.json](/Users/cam/Documents/Projects/codex-forge/output/runs/story144-onward-document-consistency-plan-r5/03_plan_onward_document_consistency_v1/pattern_inventory.json), [consistency_plan.json](/Users/cam/Documents/Projects/codex-forge/output/runs/story144-onward-document-consistency-plan-r5/03_plan_onward_document_consistency_v1/consistency_plan.json), [conformance_report.json](/Users/cam/Documents/Projects/codex-forge/output/runs/story144-onward-document-consistency-plan-r5/03_plan_onward_document_consistency_v1/conformance_report.json), and [document_consistency_dossier.json](/Users/cam/Documents/Projects/codex-forge/output/runs/story144-onward-document-consistency-plan-r5/03_plan_onward_document_consistency_v1/document_consistency_dossier.json)
20260315-1758 — manual artifact inspection: verified [conformance_report.json](/Users/cam/Documents/Projects/codex-forge/output/runs/story144-onward-document-consistency-plan-r5/03_plan_onward_document_consistency_v1/conformance_report.json) surfaces the previously missed manual format-failure chapters `011/012/013/014/018/019/020`, keeps `chapter-010.html` flagged for fragmentation/external headings, routes `chapter-009.html` into a mixed row-semantic-containing bucket with concrete evidence from pages `23/24`, and leaves [chapter-023.html](/Users/cam/Documents/Projects/codex-forge/output/runs/story143-onward-genealogy-reruns-r1/output/html/chapter-023.html) conformant as the clean baseline example
20260315-1758 — supersession boundary recorded: the chapter-first validator remains useful as a cheap upstream signal producer, but Story 144's document-level planning artifacts now own document-local policy discovery and explain the previously missed drift classes more effectively than threshold tuning alone
20260315-1231 — validate follow-up: `/validate` found that mixed chapters were still being counted in the pure/newly surfaced format-drift summary buckets, and a fresh rerun also exposed unsupported AI issue-type hallucinations on clean `chapter-023.html`; hardened summary bucketing plus dossier-supported issue-type normalization, and added regression coverage for both cases
20260315-1231 — corrected real-pipeline revalidation run `story144-onward-document-consistency-plan-r7`: `make test`, `make lint`, and `git diff --check` stayed green; updated [conformance_report.json](/Users/cam/Documents/Projects/codex-forge/output/runs/story144-onward-document-consistency-plan-r7/03_plan_onward_document_consistency_v1/conformance_report.json) now keeps `chapter-009.html` only in `mixed_issue_chapters` / `newly_surfaced_mixed_issue_chapters`, still surfaces the missed manual format-failure chapters `011/012/013/014/018/019/020`, and restores [chapter-023.html](/Users/cam/Documents/Projects/codex-forge/output/runs/story143-onward-genealogy-reruns-r1/output/html/chapter-023.html) to conformant baseline status in the planning artifacts
20260315-1242 — `/mark-story-done` validation passed: confirmed all tasks and acceptance criteria remain satisfied, ADR-001 follow-up status is correctly recorded, `python -m pytest tests/` passed (`598 passed, 6 skipped`), `python -m ruff check modules/ tests/` passed, and the corrected `story144-onward-document-consistency-plan-r7` artifacts remain the closure evidence for Story 144
