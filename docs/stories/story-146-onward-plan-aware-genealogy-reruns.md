# Story 146 — Onward Plan-Aware Genealogy Selective Reruns

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Fidelity to Source, Transparency over Magic, Dossier-ready output
**Spec Refs**: C1 (Multi-Stage OCR Pipeline), C6 (Expensive OCR for Quality), C7 (Page-Scope Extraction with Document-Level Consistency Planning)
**Decision Refs**: `docs/decisions/adr-001-source-aware-consistency-strategy/adr.md`, `docs/runbooks/document-consistency-planning.md`, Story 143 work log, Story 144 work log, `docs/build-map.md`
**Depends On**: Story 144

## Goal

Implement the next ADR-001 repair slice for the Onward genealogy converter: consume Story 144's emitted `consistency_plan` and `conformance_report` to drive bounded, source-aware reruns of the chapters/pages that violate document-local policy, then rebuild and re-check conformance. This story should prove that the planner output is actionable, not just descriptive, while keeping direct HTML as the default repair target and preserving explicit provenance, fallback, and unresolved-issue reporting.

## Acceptance Criteria

- [x] A reused-artifact validation run consumes `pattern_inventory`, `consistency_plan`, and `conformance_report` from the same run or a clearly declared reused baseline, and the rerun decision artifacts cite the specific pattern family, plan rule, and conformance reason that justified each rerun target or fallback
- [x] The implemented rerun path derives target pages from planning artifacts and source provenance rather than embedding chapter/page allowlists in module code; if a temporary review allowlist is still needed for the first validation pass, it lives only in the validation recipe and is recorded explicitly in the output artifacts
- [x] In a fresh reused-artifact validation run, the post-rerun conformance output shows a strictly smaller pure-format-drift chapter set, or lower severity on the remaining pure-format chapters, than `story144-onward-document-consistency-plan-r7` while keeping `chapter-009.html` in a mixed-issue bucket and `chapter-023.html` conformant
- [x] Original page HTML, rerun candidates, acceptance/rejection decisions, rebuilt chapter outputs, and any unresolved plan violations remain inspectable in `output/runs/`; rejected reruns fall back explicitly instead of silently replacing prior artifacts
- [x] Manual inspection verifies the repaired artifacts against at least three reviewed chapters from the current pure-format baseline set (`chapter-010.html`, `chapter-011.html`, `chapter-012.html`, `chapter-013.html`, `chapter-014.html`, `chapter-015.html`, `chapter-016.html`, `chapter-017.html`, `chapter-018.html`, `chapter-019.html`, `chapter-020.html`, `chapter-021.html`) plus one unchanged reference chapter
- [x] For planner-flagged chapters that arrive without populated `relevant_pages`, the rerun path deterministically derives page targets from dossier-backed provenance or explicitly records why the chapter remained unresolved instead of silently skipping it

## Out of Scope

- Switching the repair target to a structured intermediate or row-oriented CSV/JSON representation on the first pass
- Generalizing the plan-aware rerun mechanism beyond the Onward genealogy recipe
- Deleting the document-consistency planning layer or claiming C7 is resolved
- Hand-editing generated HTML or JSON artifacts outside the pipeline
- Main-recipe linearization unless the bounded validation loop proves the seam is safe and materially simpler

## Approach Evaluation

- **Simplification baseline**: First measure whether a strong one-call rerun per plan-flagged page, using the existing direct-HTML target plus embedded `consistency_plan` guidance, already reduces conformance failures enough to justify automation. If this baseline fails, the story should surface why before adding more orchestration.
- **AI-only**: Let the model infer targets, pick conventions, and rewrite pages from source in one opaque step. Fastest to try, but too weak on provenance, fallback discipline, and explicit policy execution.
- **Hybrid**: Deterministically select and score rerun targets from `conformance_report` + `consistency_plan`, then use AI for the source-aware reread and deterministic checks for content retention, conformance delta, and fallback. This is the leading candidate because it matches ADR-001 and Story 144's artifact contracts.
- **Pure code**: Rewrite HTML to conform to the plan without returning to source. Lower cost, but ADR-001 and the runbook both treat HTML-only normalization as secondary to source-aware follow-up.
- **Repo constraints / prior decisions**: ADR-001 settles the next default as `consistency_plan -> selective rerun -> light canonicalization`, with direct HTML first and structured fallback only if plan-aware reruns fail. Story 143 already proved schema-frozen reruns can help, and Story 144 proved the planner surfaces better targets than the chapter-first detector alone. OCR remains expensive, so the loop must stay bounded and reuse artifacts aggressively.
- **Existing patterns to reuse**: `modules/adapter/rerun_onward_genealogy_consistency_v1`, `modules/validate/plan_onward_document_consistency_v1`, `modules/validate/validate_onward_genealogy_consistency_v1`, `configs/recipes/story-143-onward-genealogy-reruns-validate.yaml`, `configs/recipes/story-144-onward-document-consistency-plan-validate.yaml`, and the acceptance/fallback patterns inside `table_rescue_onward_tables_v1`
- **Eval**: The deciding test is a real `driver.py` run that compares the new post-rerun conformance output to `story144-onward-document-consistency-plan-r7`, plus manual inspection of rebuilt HTML and decision sidecars. If the story materially changes the planner/rerun validation contract, update the relevant manual eval notes in `docs/evals/registry.yaml`.

## Tasks

- [x] Measure the minimal plan-aware rerun baseline on Story 144's pure-format-drift chapter set using the current direct-HTML target and explicit `consistency_plan` guidance
- [x] Define the contract between planning artifacts and rerun orchestration: which pattern-family IDs, issue classes, rule summaries, exemplar snippets, chapter membership, and page provenance fields are consumed by the rerun stage
- [x] Handle planner findings that lack `relevant_pages` by deriving deterministic dossier-backed target pages or recording an explicit unresolved reason in the rerun reports
- [x] Implement the smallest plan-aware rerun stage or extension that consumes `page_html_v1` plus planning sidecars and emits explicit target-selection, acceptance/rejection, and fallback reports
- [x] Add deterministic acceptance/rejection checks keyed to content-retention guardrails and before/after plan conformance deltas, not just generic score gain
- [x] Build a story-scoped reused-artifact validation recipe that runs the bounded loop end-to-end: build/plan or load-plan -> plan-aware rerun -> rebuild -> re-plan/revalidate
- [x] Add focused regression coverage for plan-aware target selection, pattern-family reason mapping, fallback behavior, and at least one before/after success path on the reviewed chapter set
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL and rebuilt HTML data
  - [x] If agent tooling changed: `make skills-check` (not applicable; agent tooling unchanged)
- [x] If evals or goldens changed: updated `docs/evals/registry.yaml` for the `architecture-change` follow-up (manual eval note only; `/improve-eval` not applicable)
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every rerun decision traces to source page, planner artifact, rule family, and final acceptance path
  - [x] T1 — AI-First: use AI for the source-aware reread and policy execution decisions that code does not solve better
  - [x] T2 — Eval Before Build: measure the bounded direct-HTML baseline before widening the orchestration surface
  - [x] T3 — Fidelity: preserve names, subgroup context, tables, and summary rows without silent flattening or loss
  - [x] T4 — Modular: keep the work recipe-scoped and avoid baking Onward-only family names or page IDs into generic logic
  - [x] T5 — Inspect Artifacts: manually inspect rebuilt chapters and sidecar reports, not just validator output

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: Prefer a focused adapter seam next to `rerun_onward_genealogy_consistency_v1`, backed by a story-scoped validation recipe that can plan, rerun, rebuild, and re-check without re-running OCR. If extending the existing rerun module is cleaner, keep the planner-aware logic isolated instead of spreading it through recipe glue.
- **Data contracts / schemas**: `pattern_inventory`, `consistency_plan`, and `conformance_report` should remain explicit sidecar JSON/JSONL artifacts. The rerun stage should continue to emit `page_html_v1` plus decision sidecars. Do not add new stamped cross-stage fields unless `schemas.py` is updated first and the need is proven.
- **File sizes**: `modules/validate/plan_onward_document_consistency_v1/main.py` is 1225 lines, `modules/adapter/rerun_onward_genealogy_consistency_v1/main.py` is 870 lines, `modules/validate/validate_onward_genealogy_consistency_v1/main.py` is 488 lines, `tests/test_plan_onward_document_consistency_v1.py` is 468 lines, `tests/test_rerun_onward_genealogy_consistency_v1.py` is 444 lines, `configs/recipes/story-143-onward-genealogy-reruns-validate.yaml` is 103 lines, and `configs/recipes/story-144-onward-document-consistency-plan-validate.yaml` is 33 lines. Avoid pushing the two large `main.py` files much further without a clear refactor boundary.
- **Decision context**: Reviewed `docs/ideal.md`, `docs/spec.md`, `docs/build-map.md`, ADR-001, `docs/runbooks/document-consistency-planning.md`, `docs/evals/registry.yaml`, and the completed Story 143 / Story 144 documents. No other ADRs relevant to this seam were found after search.

## Files to Modify

- `modules/adapter/rerun_onward_genealogy_consistency_v1/main.py` — consume planner artifacts, derive plan-aware targets/context, and emit richer decision reports (870 lines)
- `modules/adapter/table_rescue_onward_tables_v1/main.py` — extend deterministic genealogy normalization to rewrite malformed table headers that embed family labels inside thead cells (1467 lines)
- `modules/adapter/rerun_onward_genealogy_consistency_v1/module.yaml` — add planner-artifact params or clarify the plan-aware contract if this module remains the seam (53 lines)
- `modules/validate/plan_onward_document_consistency_v1/main.py` — expose the minimum reusable helpers or artifact-contract changes needed for rerun targeting and before/after conformance comparison (1225 lines)
- `configs/recipes/story-146-onward-plan-aware-genealogy-reruns-validate.yaml` — new bounded validation recipe for build/plan/rerun/rebuild/re-plan (new file)
- `tests/test_rerun_onward_genealogy_consistency_v1.py` — extend focused coverage for plan-aware targeting, reason mapping, and fallback behavior (444 lines)
- `tests/test_table_rescue_onward_tables_v1.py` — lock the embedded-family-header normalization used by the rerun acceptance path (518 lines)
- `tests/test_plan_onward_document_consistency_v1.py` — update only if planner artifact contracts or conformance summaries change (468 lines)
- `docs/evals/registry.yaml` — update the manual planning/rerun eval notes if this story exercises the `architecture-change` follow-up (443 lines)
- `docs/stories/story-146-onward-plan-aware-genealogy-reruns.md` — work log and validation evidence

## Redundancy / Removal Targets

- Story 143's temporary page/chapter allowlist posture if planner-driven targeting fully replaces it in the validation loop
- Any duplicated ad hoc parsing of `consistency_plan` / `conformance_report` inside recipes instead of module code
- Narrow schema-hint-only targeting logic that becomes redundant once plan-family and issue-class guidance is the primary rerun signal

## Notes

- Story 144 already proved the planning layer explains the manual failures better than the chapter-first detector. This story exists to prove the planner can guide repair, not just reporting.
- Direct HTML remains the default repair target. The row-structured fallback experiment in `docs/inbox.md` stays explicitly out of scope unless this story shows that plan-aware direct-HTML reruns cannot reliably reduce the remaining conformance failures.
- The reviewed baseline for this story is `story144-onward-document-consistency-plan-r7`: pure-format drift currently includes `chapter-010.html`, `chapter-011.html`, `chapter-012.html`, `chapter-013.html`, `chapter-014.html`, `chapter-015.html`, `chapter-016.html`, `chapter-017.html`, `chapter-018.html`, `chapter-019.html`, `chapter-020.html`, and `chapter-021.html`; `chapter-009.html` and `chapter-022.html` are the current mixed-issue guardrails; `chapter-023.html` is the clean baseline.
- The story should prefer a bounded validation recipe first. Main-recipe adoption is a separate decision unless this pass proves there is no extra orchestration or validation complexity hiding in the seam.

## Plan

### Exploration Findings

- Story 146 is aligned with the Ideal and ADR-001. It closes a real fidelity/traceability gap by turning document-level policy artifacts into an auditable repair loop rather than adding another hidden prompt layer.
- Current baseline from `story144-onward-document-consistency-plan-r7` is larger than the story stub initially recorded:
  - pure-format drift chapters: `chapter-010.html`, `chapter-011.html`, `chapter-012.html`, `chapter-013.html`, `chapter-014.html`, `chapter-015.html`, `chapter-016.html`, `chapter-017.html`, `chapter-018.html`, `chapter-019.html`, `chapter-020.html`, `chapter-021.html`
  - mixed-issue chapters: `chapter-009.html`, `chapter-022.html`
  - newly surfaced pure-format chapters vs the chapter-first detector: `chapter-011.html`, `chapter-012.html`, `chapter-013.html`, `chapter-014.html`, `chapter-015.html`, `chapter-018.html`, `chapter-019.html`, `chapter-020.html`
- The most important implementation seam is now explicit: `modules/adapter/rerun_onward_genealogy_consistency_v1/main.py` only derives targets from `pipeline_issues_v1` issues of type `onward_genealogy_consistency_drift`. Running its current `load_targets()` against Story 144's `document_consistency_report.jsonl` returns `0` targets.
- Planner outputs are usable but not yet sufficient on their own for targeting:
  - `document_consistency_report.jsonl` emits `document_consistency_planning_issue` items with `pattern_id`, `issue_types`, and `relevant_pages`
  - `conformance_report.json` carries chapter-level status and source-page provenance
  - some pure-format chapters in the real artifact set (`chapter-013.html`, `chapter-014.html`, `chapter-015.html`) have empty `relevant_pages` and empty `evidence`, so the rerun loop cannot rely on those fields alone
- The compact dossier still contains enough provenance to support a bounded fallback path, which makes this a small coherent scope expansion rather than a new story:
  - those empty-page chapters still carry `source_pages`
  - the dossier has chapter/page profiles and deterministic signals that can seed a conservative fallback derivation
- Existing patterns to follow are still the right ones:
  - keep the loop story-scoped and reuse upstream artifacts
  - preserve `page_html_v1` compatibility
  - keep direct HTML as the repair target unless evidence shows it is insufficient
  - avoid main-recipe wiring until the bounded validation loop proves the seam

### Eval / Baseline

- **Deterministic baseline metric:** parse `story144-onward-document-consistency-plan-r7/03_plan_onward_document_consistency_v1/conformance_report.json`
  - current counts: `12` pure-format drift, `2` mixed, `0` row-semantic-only, `8` newly surfaced pure-format, `1` newly surfaced mixed
- **Contract baseline:** run `load_targets()` from the current rerun adapter against Story 144's `document_consistency_report.jsonl`
  - current result: `0` targets
  - implication: current code cannot consume planning output at all, so no no-code or recipe-only solution exists
- **Story success metric:** after the bounded plan-aware rerun loop, reduce the pure-format baseline or materially lower severity on the repaired chapters while preserving `chapter-009.html` as mixed and `chapter-023.html` as conformant

### Recommended Implementation Shape

- Recommended seam: keep the existing rerun module as the execution engine, but add a planner-aware translation layer/helper rather than stuffing more policy-specific selection logic directly into the current `load_targets()` path.
- Recommended validation flow: story-scoped reuse recipe only
  - load reused pages/portions/crops
  - build chapters
  - run planner or load the current planner outputs from the same run
  - run the plan-aware rerun stage
  - rebuild chapters
  - re-run the planner to compare before/after conformance
- Recommended fallback behavior:
  - first preference: use `relevant_pages` from planner output
  - second preference: derive candidate pages from dossier/page-profile provenance for chapters with empty `relevant_pages`
  - final fallback: mark chapter unresolved with explicit reason if no bounded page target can be justified

### Task Plan

#### Task 1 — Normalize the plan-aware target contract

- **Files:** `modules/adapter/rerun_onward_genealogy_consistency_v1/main.py`, `modules/validate/plan_onward_document_consistency_v1/main.py`, `tests/test_rerun_onward_genealogy_consistency_v1.py`, `tests/test_plan_onward_document_consistency_v1.py`
- **Change:**
  - define a stable target-input contract from Story 144 artifacts
  - decide whether the rerun stage consumes:
    - `document_consistency_report.jsonl` plus `conformance_report.json`, or
    - `conformance_report.json` plus `document_consistency_dossier.json`
  - add deterministic fallback logic for chapters with empty `relevant_pages`
- **Impact / risk:**
  - this is the real blocker uncovered in exploration; without it, the rerun stage will silently do nothing
  - if the fallback derivation is too broad, OCR cost and blast radius will grow beyond the bounded seam
- **Done when:**
  - a fixture-backed target derivation path yields nonzero targets from planner artifacts and records whether each target came from explicit planner pages or dossier fallback

#### Task 2 — Implement the plan-aware rerun seam

- **Files:** `modules/adapter/rerun_onward_genealogy_consistency_v1/main.py`, `modules/adapter/rerun_onward_genealogy_consistency_v1/module.yaml`
- **Change:**
  - add planner-artifact inputs/params and a planner-aware target selection path
  - thread pattern-family IDs, issue classes, rule summaries, and provenance into the rerun decision reports
  - keep original-vs-normalized-vs-rerun acceptance/fallback behavior intact
- **Impact / risk:**
  - the file is already 870 lines, so blindly appending logic is risky
  - if the planner-aware layer is not isolated, Story 143's simpler validator-driven path becomes harder to reason about
- **Done when:**
  - the rerun engine can execute a bounded plan-aware page set and emit richer decision reports without breaking the existing validator-driven mode

#### Task 3 — Add bounded before/after conformance validation

- **Files:** `configs/recipes/story-146-onward-plan-aware-genealogy-reruns-validate.yaml`, optionally `docs/evals/registry.yaml`
- **Change:**
  - create a story-scoped recipe that reuses current Onward artifacts, runs planning, reruns, rebuilds, and re-plans
  - compare the final conformance summary directly against the Story 144 baseline
  - if the architecture-change follow-up is meaningfully exercised, update the manual eval notes
- **Impact / risk:**
  - without a same-run before/after comparison, the story could claim success from stale planner output
  - the loop must remain explicit and inspectable; no hidden in-place mutation of prior run artifacts
- **Done when:**
  - one driver run emits both the plan-aware rerun sidecars and a post-rerun conformance report suitable for direct comparison to `story144-onward-document-consistency-plan-r7`

#### Task 4 — Expand focused regression coverage

- **Files:** `tests/test_rerun_onward_genealogy_consistency_v1.py`, `tests/test_plan_onward_document_consistency_v1.py`
- **Change:**
  - cover planner-summary contract mismatch
  - cover `relevant_pages` present vs empty
  - cover unresolved-chapter reporting when fallback targeting cannot justify a page set
  - cover at least one accepted plan-aware rerun path and one explicit fallback/rejection path
- **Impact / risk:**
  - without this, the story could regress into allowlist-driven targeting again
- **Done when:**
  - the core plan-aware targeting and fallback decisions are fixture-locked

### Scope Adjustments Folded Into This Build

- Small coherent expansion: handle planner findings with empty `relevant_pages` by consuming dossier-backed provenance or enriching the planner artifact contract
- Small coherence guardrail: do not widen this into the structured-intermediate experiment from `docs/inbox.md`; only surface that as a follow-up if direct HTML still fails after this bounded pass

### Human-Approval Blockers

- No new external dependency is expected
- No schema change is expected if planner/rerun coordination stays in sidecar JSON/JSONL and `page_html_v1`
- Main decision to confirm before implementation:
  - recommended: keep one rerun execution module and add a planner-aware helper/translation path around it
  - alternative: add a separate planner-aware adapter that translates Story 144 artifacts into the current rerun target contract
- Relative effort: `M`

### Done Criteria

- Story 146 is done only when the plan-aware rerun loop runs through `driver.py`, artifacts exist in `output/runs/`, the repaired chapters and sidecars are manually inspected, and the post-rerun conformance summary shows measurable improvement against the Story 144 baseline without regressing the mixed/conformant guardrails.

## Work Log

20260315-2205 — story created: captured the next concrete ADR-001 step after Story 144, framing it as a bounded plan-aware rerun loop rather than a speculative new representation; evidence is ADR-001 remaining work, the C7 optimize path in `docs/build-map.md`, and the `architecture-change` trigger recorded in `docs/evals/registry.yaml`; next step is `/build-story` on this pending story
20260315-2238 — build-story exploration: promoted Story 146 to active work after verifying it is `Pending` and fully specified; reviewed `docs/ideal.md`, `docs/spec.md`, `docs/build-map.md`, ADR-001, `docs/runbooks/document-consistency-planning.md`, Stories 143/144, the current rerun adapter, planner module, validation recipe wiring, and the real `story144-onward-document-consistency-plan-r7` artifacts; found the current rerun adapter returns `0` targets when pointed at the planner summary because it only understands `onward_genealogy_consistency_drift`, and found that some real pure-format chapters (`013/014/015`) have empty `relevant_pages`, so dossier-backed target derivation is necessary; next step is to write the implementation plan and approval gate
20260315-2244 — build-story baseline and scope correction: measured the current baseline directly from `story144-onward-document-consistency-plan-r7` (`12` pure-format drift chapters, `2` mixed chapters, `8` newly surfaced pure-format, `1` newly surfaced mixed) and corrected the story notes/ACs to match the actual artifact set; folded one small scope expansion into the story so plan-aware reruns must handle chapters with empty planner page targets explicitly instead of silently skipping them; next step is human approval on the written plan before implementation
20260315-2242 — implementation complete: extended `modules/adapter/rerun_onward_genealogy_consistency_v1/main.py` to consume Story 144 planner sidecars, thread pattern/rule/status context into prompts and reports, derive deterministic fallback targets for chapters with empty `relevant_pages`, and interleave planner targets by chapter before applying `max_pages`; updated `module.yaml`, added Story 146 validation recipe `configs/recipes/story-146-onward-plan-aware-genealogy-reruns-validate.yaml`, and expanded `tests/test_rerun_onward_genealogy_consistency_v1.py` to lock the new planner contract, fallback path, unresolved reporting, and bounded cap ordering; verification was `make lint`, `make test`, `python -m pytest tests/test_rerun_onward_genealogy_consistency_v1.py`, and `python -m pytest tests/test_plan_onward_document_consistency_v1.py`; next step was real pipeline validation and manual artifact inspection
20260315-2242 — validation and artifact review: ran `python driver.py --recipe configs/recipes/story-146-onward-plan-aware-genealogy-reruns-validate.yaml --run-id story146-onward-plan-aware-genealogy-reruns-r1 --allow-run-id-reuse --force` after clearing stale `*.pyc` and linking the reviewed Story 140 / Story 143 reuse runs into this worktree's ignored `output/runs/`; the live run consumed `pattern_inventory_before.json`, `consistency_plan_before.json`, and `conformance_report_before.json`, targeted `18` plan-selected pages across all `12` pure-format chapters, accepted `11/18`, and emitted inspectable decision reports in `output/runs/story146-onward-plan-aware-genealogy-reruns-r1/06_rerun_onward_genealogy_consistency_v1/`; the post-rerun chapter set stayed at `12` pure-format drift chapters, but remaining pure-format issue types dropped from `21` to `19`, removing `fragmented_multi_table_chapter` from `chapter-018.html` and `chapter-019.html` and removing `missing_subgroup_rows` from `chapter-017.html` while preserving `chapter-009.html` as mixed and `chapter-023.html` as conformant; manual inspection covered page HTML `80`, `88`, `93`, and `104` in the before/after page artifacts, the rebuilt HTML chapters `017`, `018`, `019`, and `023`, and the rerun decision rows for pages `54`, `80`, `88`, and `93`; the reviewed pages now show split `BOY`/`GIRL` headers plus full-width subgroup rows on the repaired pages, and `chapter-023.html` remains a clean single-table reference chapter; because the live planner output on this pass populated `relevant_pages` for `013/014/015`, I separately verified the fallback path against the original `story144-onward-document-consistency-plan-r7` artifacts with the shipped adapter, which deterministically derived `56-57`, `62-64`, and `67-69` for `chapter-013.html`, `chapter-014.html`, and `chapter-015.html` respectively with no unresolved chapters; next step is Story 147-level follow-up only if we want a stronger structured repair target after this direct-HTML plateau
20260315-2335 — post-review follow-up repair: after manual review showed that `chapter-022.html` still contained a malformed second genealogy table and upstream inspection traced the defect to page-level HTML on source page `112`, I expanded Story 146 modestly inside the same seam instead of creating a new story; patched `modules/adapter/table_rescue_onward_tables_v1/main.py` so deterministic normalization rewrites genealogy headers that embed a family label in thead cells into a canonical `NAME/BORN/MARRIED/SPOUSE/BOY/GIRL/DIED` header plus subgroup rows, and locked that shape with new regressions in `tests/test_table_rescue_onward_tables_v1.py` plus `tests/test_rerun_onward_genealogy_consistency_v1.py`; verification was `make lint`, `make test`, a direct acceptance-gate probe on page `112`, and focused driver run `story146-onward-plan-aware-genealogy-reruns-r2-page112-fast`; inspected artifacts were `output/runs/story146-onward-plan-aware-genealogy-reruns-r2-page112-fast/06_rerun_onward_genealogy_consistency_v1/rerun_onward_genealogy_summary.json`, `output/runs/story146-onward-plan-aware-genealogy-reruns-r2-page112-fast/output/html/chapter-022.html`, and `output/runs/story146-onward-plan-aware-genealogy-reruns-r2-page112-fast/08_validate_onward_genealogy_consistency_v1/genealogy_consistency_after.jsonl`; those artifacts show page `112` was accepted through deterministic normalization, `chapter-022.html` no longer contains a literal `BOY/GIRL` header, now carries subgroup rows such as `SANDRA’S FAMILY`, `CHRISTINE’S FAMILY`, and `THERESE’S FAMILY` inside the table, and is no longer flagged by the deterministic genealogy validator, leaving `chapter-010.html`, `chapter-016.html`, `chapter-017.html`, and `chapter-021.html` as the remaining flagged chapters in that focused validation slice
20260316-1028 — page-break continuation repair: after the next manual review showed the remaining defects across `chapter-010.html` through `chapter-015.html` were mostly physical page-break splits, not new OCR hallucinations, I expanded Story 146 one more notch inside `modules/build/build_chapter_html_v1/main.py`; added direct-adjacent same-schema genealogy table stitching with a summary-table guard, converted heading-followed name-list paragraphs such as `ULRIC'S FAMILY` tails into continuation tables before merge, and re-applied genealogy merging at final chapter write time because later carry-back stitching could reintroduce fragmentation after the earlier pass; locked the behavior with new build-stage regressions in `tests/test_build_chapter_html.py`; verification was `python -m pytest tests/test_build_chapter_html.py`, `make lint`, `make test`, and focused rebuild/validate run `story146-onward-build-stitch-r3`; inspected artifacts were `output/runs/story146-onward-build-stitch-r3/output/html/chapter-010.html`, `output/runs/story146-onward-build-stitch-r3/output/html/chapter-011.html`, `output/runs/story146-onward-build-stitch-r3/output/html/chapter-015.html`, and `output/runs/story146-onward-build-stitch-r3/05_validate_onward_genealogy_consistency_v1/genealogy_consistency_after.jsonl`; those artifacts show the reviewed chapters now collapse to one main genealogy table plus the totals table, subgroup rows like `ULRIC'S FAMILY`, `SHARON'S FAMILY`, and `JULLIETTE'S FAMILY` stay inside the main table, and the deterministic validator reports no remaining flagged genealogy chapters in this focused validation slice
20260316-1103 — subgroup-row normalization repair: after the next manual review surfaced the remaining post-stitch defects as row-shape problems instead of table continuity problems, I kept the work inside `modules/build/build_chapter_html_v1/main.py` and added a second deterministic cleanup pass over merged genealogy tables; the new pass converts left-column-only heading rows into true full-width subgroup rows, splits flattened multi-line generation context such as `Leonidas’ Great Great Grandchildren Alma’s Great Grandchildren Dolly’s Grandchildren SHARON’S FAMILY` into separate subgroup rows, and shifts death-looking values like `, 1956` out of the `GIRL` column into `DIED` when a combined `BOY/GIRL` source row was padded into a seven-column canonical table; locked the behavior with new build regressions in `tests/test_build_chapter_html.py`; verification was `python -m pytest tests/test_build_chapter_html.py`, `make lint`, `make test`, and focused rebuild/validate run `story146-onward-build-stitch-r5`; inspected artifacts were `output/runs/story146-onward-build-stitch-r5/output/html/chapter-010.html`, `output/runs/story146-onward-build-stitch-r5/output/html/chapter-011.html`, `output/runs/story146-onward-build-stitch-r5/output/html/chapter-017.html`, `output/runs/story146-onward-build-stitch-r5/output/html/chapter-022.html`, and `output/runs/story146-onward-build-stitch-r5/05_validate_onward_genealogy_consistency_v1/genealogy_consistency_after.jsonl`; those artifacts show Richard’s `, 1956` now lands in `DIED`, the reviewed Sharon heading is no longer emitted as one concatenated row, subgroup rows such as `CLEMENCE’S FAMILY` and `SANDRA’S FAMILY` now span the full table width, and the deterministic validator still reports zero flagged genealogy chapters in this focused validation slice
20260316-1224 — mark-story-done validation: re-ran the required close-out checks `python -m pytest tests/` and `python -m ruff check modules/ tests/` in the story worktree and both passed (`619 passed, 6 skipped`; Ruff clean); re-checked the Story 146 acceptance criteria against the shipped artifacts plus the reviewed follow-up outputs, including `output/runs/story146-onward-plan-aware-genealogy-reruns-r1/06_rerun_onward_genealogy_consistency_v1/rerun_onward_genealogy_report.jsonl`, `output/runs/story146-onward-plan-aware-genealogy-reruns-r1/08_plan_onward_document_consistency_v1/conformance_report_after.json`, `output/runs/story146-onward-build-stitch-r5/output/html/chapter-011.html`, `output/runs/story146-onward-build-stitch-r5/output/html/chapter-017.html`, and `output/runs/story146-onward-build-stitch-r5/output/html/chapter-022.html`; Story 144 dependency is done, all task / AC / tenet checkboxes remain satisfied, the rerun decision artifacts stay inspectable, the reviewed HTML defects are resolved, and Story 147 now holds the explicit simplification follow-up so Story 146 remains a clean `Done`
