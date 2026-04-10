---
title: "Restore Maintained Onward Full-Book Fidelity and Regression Guardrails"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Traceability is the product, Fidelity to source"
spec_refs:
  - "spec:2"
  - "spec:3"
  - "spec:5"
  - "spec:6"
  - "spec:7"
adr_refs:
  - "ADR-001"
  - "ADR-002"
depends_on:
  - "149"
  - "157"
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

# Story 206 — Restore Maintained Onward Full-Book Fidelity and Regression Guardrails

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/decisions/adr-001-source-aware-consistency-strategy/adr.md`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/runbooks/golden-build.md`, `docs/stories/story-149-onward-scanned-genealogy-collapse-implementation.md`, `docs/stories/story-154-dossier-doc-web-semantic-html-handoff.md`, `docs/stories/story-155-repo-mission-alignment-cleanup-and-legacy-surface-removal.md`, `docs/stories/story-157-pdf-intake-parity-with-image-directory-inputs.md`, `docs/notes/repo-mission-alignment-cleanup-inventory.md`, `tests/fixtures/formats/_coverage-matrix.json`, `benchmarks/golden/onward/reviewed_html_slice/README.md`, `benchmarks/golden/onward/dossier-doc-web-handoff-v1/README.md`, and `None found after search in docs/scout/ for a narrower maintained full-book Onward regression owner`
**Depends On**: 149, 157

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

Restore the maintained full-book `Onward to the Unknown` PDF lane so a fresh
`driver.py` run produces the same practical quality bar we previously treated as
the book's golden standard, and add regression guardrails that fail when that
quality slips again. Fresh evidence shows the current maintained run can finish
green while still duplicating early pages/chapters, replaying the same source
page across multiple TOC-derived chapters, and collapsing later genealogy table
shapes relative to the committed reviewed goldens. Because `doc-web` is the
Dossier-facing structural runtime, this story must both repair the real output
and make the maintained proof surface honest.

## Acceptance Criteria

- [x] A fresh current-pass baseline records the exact regression surface on the
      shared Onward PDF with artifact paths and concrete samples:
  - [x] the work log cites duplicate/replayed early output such as the front
        matter or early chapters
  - [x] the work log cites the same-page TOC explosion in
        `07_portionize_toc_html_v1/portions_toc.jsonl`
  - [x] the work log cites at least one later genealogy hard-case regression
        against the committed Onward goldens
- [x] The investigation traces each failure to the correct stage with repo-backed
      evidence rather than guesswork:
  - [x] OCR/page HTML is either cleared or named as the real culprit with
        evidence
  - [x] TOC portionization, chapter build, table rescue/continuation, and the
        current validator blind spot are each evaluated explicitly
  - [x] the story records which defects are deterministic replay/assembly bugs
        versus genuine extraction/table-quality regressions
- [x] A fresh `driver.py` run on the shared Onward PDF after the fix produces an
      honest maintained full-book result:
  - [x] early pages/chapters no longer replay the same source page because of
        same-page TOC leaf entries
  - [x] reviewed hard-case genealogy chapters are no worse than the committed
        blessed slice / handoff pack on the measured structural signals this
        story chooses
  - [x] manual inspection is recorded for specific artifact paths under
        `output/runs/` including early pages/chapters and later genealogy
        chapters
- [x] Regression guardrails are widened so this failure cannot silently pass
      again:
  - [x] focused unit/integration coverage exists for the dense same-page TOC
        case and the chapter-builder replay case
  - [x] maintained validation or comparison reporting fails when duplicate
        pages/replayed chapters or reviewed hard-case table collapse reappear
  - [x] `tests/fixtures/formats/_coverage-matrix.json` and any touched docs are
        updated honestly if the maintained `scanned-pdf-tables` claim changes

## Out of Scope

- Replacing `doc-web` with a different runtime or reopening the `Docling`
  replacement track
- Building a brand-new generic TOC architecture beyond the smallest honest fix
  required to keep the maintained Onward lane correct
- Committing the full shared Onward PDF into the repo if it remains a local-only
  validation asset
- Theme or presentation-only HTML polish once fidelity and regression coverage
  are restored
- Broad new format-family claims outside the existing `scanned-pdf-tables` lane

## Approach Evaluation

- **Simplification baseline**: Current evidence already says the first failure is
  not a weak OCR page. In `/Users/cam/Documents/Projects/doc-web/output/runs/onward-book-r1/02_ocr_ai_gpt51_v1/pages_html.jsonl`,
  page `11` contains one clean `The First L'Heureux's in Canada` block, while
  `/Users/cam/Documents/Projects/doc-web/output/runs/onward-book-r1/07_portionize_toc_html_v1/portions_toc.jsonl`
  emits `15` portions at printed page `1`, `9` at `2`, `2` at `3`, and `3` at
  `4`. The built bundle then turns that into `chapter-001.html` with `15`
  repeated table sections and `chapter-002.html` with the same title/body
  repeated `9` times. That makes “just rerun OCR with a stronger model” the
  wrong default.
- **AI-only**: Possible only as a bounded fallback for any later hard-case table
  pages that still regress after deterministic replay/boundary fixes. Using AI
  alone would hide a deterministic TOC/builder bug and still leave the
  maintained regression surface dishonest.
- **Hybrid**: Likely strongest if the story finds two classes of problems: a
  deterministic same-page TOC replay bug plus a smaller residue of later table
  pages that still need targeted reruns or Onward-specific repair logic.
- **Pure code**: Strong candidate for the front-matter/TOC replay failure and
  the validator blind spot. It may also be sufficient for the later table drift
  if the apparent hard-case regressions are downstream of wrong portion/chapter
  assembly rather than raw extraction.
- **Repo constraints / prior decisions**: ADR-001 says consistency should be
  treated as a document-wide conformance problem with inspectable artifacts;
  ADR-002 keeps the `doc-web` bundle contract honest; Story 149 only blessed a
  narrow reviewed genealogy slice; Story 155 explicitly noted the maintained
  Onward regression lane was no longer self-contained; Story 157 widened TOC
  parsing for PDF parity and is the clearest regression inflection point
  because it changed `portionize_toc_html_v1` from a narrower TOC surface to a
  heading-plus-table parser without adding full-book regression coverage.
- **Existing patterns to reuse**:
  `benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/`,
  `benchmarks/golden/onward/dossier-doc-web-handoff-v1/`,
  `modules/common/onward_genealogy_html.py`,
  `modules/validate/validate_onward_genealogy_consistency_v1/main.py`,
  `tests/test_portionize_toc_html.py`, `tests/test_build_chapter_html.py`,
  `tests/test_detect_duplicate_pages_v1.py`, and `docs/runbooks/golden-build.md`.
- **Eval**: The deciding proof is a fresh shared-PDF `driver.py` run plus manual
  inspection of early pages/chapters and later reviewed genealogy chapters,
  compared against the committed Onward goldens and against stronger duplicate
  / replay reporting. The winning approach is the one that removes same-page
  replay, restores later hard-case structure, and causes the maintained proof
  surface to fail loudly when those defects reappear.

## Tasks

- [x] Freeze the failing baseline on the shared Onward PDF and record exact
      artifact evidence from the current bad run or a fresh rerun:
  - [x] duplicate/replayed early chapters or pages
  - [x] same-page TOC over-segmentation in `portions_toc.jsonl`
  - [x] later hard-case genealogy regressions against committed goldens
- [x] Trace each failure to the owning stage and choose the smallest honest
      repair:
  - [x] TOC entry filtering or same-page boundary policy in
        `portionize_toc_html_v1`
  - [x] replay prevention / safer assembly in `build_chapter_html_v1`
  - [x] any remaining table-specific rescue or targeted rerun only if the
        deterministic fix is insufficient
- [x] Widen maintained Onward guardrails:
  - [x] focused TOC and chapter-builder regression tests
  - [x] stronger validation or comparison reporting for duplicate/replayed
        full-book chapters and later reviewed hard-case table collapse
- [x] If this story changes documented format coverage or graduation reality: no coverage-matrix or methodology-state change was needed because the maintained `scanned-pdf-tables` claim was repaired rather than narrowed
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; no additional redundant seam remained after the TOC/build/validator/rerun fixes landed together
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through
        `driver.py`, verify artifacts in `output/runs/`, and manually inspect
        `portions_toc.jsonl`, `chapters_manifest.jsonl`, early `output/html`
        pages/chapters, and the reviewed genealogy hard-case outputs
  - [x] If agent tooling changed: `make skills-check` was not needed because no agent tooling changed
- [x] If evals or goldens changed: no eval or golden files changed, so `/improve-eval` and `docs/evals/registry.yaml` updates were not needed
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: repaired output and any new reports still trace back
        to source page ids and bundle/provenance surfaces
  - [x] T1 — AI-First: do not add new code for defects a stronger bounded AI
        rerun already solves more honestly
  - [x] T2 — Eval Before Build: baseline the bad run and current golden
        comparison before changing logic
  - [x] T3 — Fidelity: source content is not dropped or replayed under the
        wrong chapters
  - [x] T4 — Modular: keep the fix at the TOC/build/validation seam instead of
        hardcoding book text into generic stages
  - [x] T5 — Inspect Artifacts: manually open the repaired full-book artifacts,
        not just the logs or validator summary

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Blocker Summary

N/A

## Blocker Evidence

N/A

## Unblock Condition

N/A

## Architectural Fit

- **Owning module / area**: Primary likely owners are
  `modules/portionize/portionize_toc_html_v1/main.py` and
  `modules/build/build_chapter_html_v1/main.py`. The current validator
  `modules/validate/validate_onward_genealogy_consistency_v1/main.py` or a
  sibling regression report should own the guardrail expansion. The maintained
  proof path remains `configs/recipes/recipe-onward-pdf-html-mvp.yaml`.
- **Methodology reality**: This story sits across `spec:2`, `spec:3`,
  `spec:5`, `spec:6`, and `spec:7`. `docs/methodology/state.yaml` currently
  says the substrate for those categories exists, and the architecture audit
  notes no current open finding in `document_structure_and_consistency` or
  `doc_web_runtime`; this run proves a new live regression in that seam. The
  relevant coverage row is `scanned-pdf-tables`, which still claims
  `status: passing` and `structure_preservation: 0.95` measured `2026-03-11`.
- **Substrate evidence**: The failing maintained run already exists at
  `/Users/cam/Documents/Projects/doc-web/output/runs/onward-book-r1/` and
  points back to `configs/recipes/recipe-onward-pdf-html-mvp.yaml`. Fresh
  inspection shows page `11` is clean in
  `02_ocr_ai_gpt51_v1/pages_html.jsonl`, but
  `07_portionize_toc_html_v1/portions_toc.jsonl` emits `15` entries at page
  start `1`, `9` at `2`, `2` at `3`, `3` at `4`, and `11` at `0`; the built
  bundle then produces `chapter-001.html` with `15` heading/table repeats and
  `chapter-002.html` with the same title/body repeated `9` times. Current
  tests exist for TOC portionization and chapter building, but none verify an
  Onward-style dense same-page TOC leaf case.
- **Data contracts / schemas**: The main existing contracts are
  `page_html_v1`, `portion_hyp_v1`, `chapter_html_manifest_v1`,
  `doc_web_bundle_manifest_v1`, `doc_web_provenance_block_v1`, and
  `pipeline_issues_v1`. If the chosen guardrail path adds new report fields or
  artifact rows beyond current schemas, update `schemas.py` before relying on
  stamped output.
- **File sizes**: `modules/build/build_chapter_html_v1/main.py` is `1820`
  lines and `tests/test_build_chapter_html.py` is `1759` lines, so the story
  should prefer narrow helper extraction or very focused additions over more
  sprawl. `modules/portionize/portionize_toc_html_v1/main.py` is `168` lines,
  `modules/validate/validate_onward_genealogy_consistency_v1/main.py` is `488`
  lines, `tests/test_portionize_toc_html.py` is `140` lines, and
  `tests/fixtures/formats/_coverage-matrix.json` is `545` lines.
- **Decision context**: Reviewed `docs/ideal.md`, `docs/spec.md`,
  `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-001,
  ADR-002, Story 149, Story 154, Story 155, Story 157,
  `docs/runbooks/golden-build.md`, the Onward golden READMEs, and the current
  failing artifacts. `docs/scout/` has no narrower owner than the general
  external-ingestion benchmark notes, so this is now a local maintained-lane
  regression story.

## Files to Modify

- `modules/portionize/portionize_toc_html_v1/main.py` — filter or group
  same-page TOC leaf entries so one printed page does not explode into replayed
  chapters (`168` lines)
- `modules/build/build_chapter_html_v1/main.py` — prevent same-page portion
  replay and keep chapter assembly / source-portion lineage honest (`1820`
  lines)
- `modules/validate/validate_onward_genealogy_consistency_v1/main.py` — catch
  or surface regression classes the current report misses, or become the
  decision point for keeping this validator genealogy-only and adding a sibling
  regression report (`488` lines)
- `tests/test_portionize_toc_html.py` — regression coverage for dense
  Onward-style TOC leaves and same-page entries (`140` lines)
- `tests/test_build_chapter_html.py` — regression coverage for repeated
  same-page TOC portions not replaying the same source page body (`1759`
  lines)
- `tests/fixtures/formats/_coverage-matrix.json` — refresh the
  `scanned-pdf-tables` truth surface if the fresh proof changes the maintained
  claim or date (`545` lines)
- `docs/stories/story-206-onward-full-book-regression-recovery.md` — story work
  log and validation evidence
- `docs/stories.md` and `docs/methodology/graph.json` — generated view refresh
  after story creation and later status changes

## Redundancy / Removal Targets

- Same-page TOC leaf portions that only replay a parent page and do not
  represent real chapter boundaries
- The assumption that `validate_onward_genealogy_consistency_v1` is sufficient
  to keep the maintained Onward lane honest
- Stale `scanned-pdf-tables` support claims if fresh full-book evidence no
  longer supports them

## Notes

- New story is the honest move rather than reopening an old one. Story 149 and
  Story 154 prove only the narrow reviewed hard-case slice and handoff pack;
  Story 157 restored the maintained PDF entry seam; Story 155 explicitly noted
  that the maintained Onward regression lane was not self-contained anymore.
  None of those stories owns fresh full-book regression recovery on the
  maintained PDF lane.
- Initial root-cause hypothesis: the biggest current breakage is deterministic,
  not OCR-quality drift. Story 157 widened TOC parsing so PDF runs could read
  heading-plus-table index pages. Current `portionize_toc_html_v1` now emits
  every leaf from the dense Onward index as its own portion even when many
  share the same printed page, and `build_chapter_html_v1` then replays the
  same source page once per portion. The later genealogy-table regressions may
  be a second issue, but the early duplicate/replayed chapters already prove
  the current maintained support claim is stale.
- Hard evidence from the current bad run:
  - `02_ocr_ai_gpt51_v1/pages_html.jsonl` page `11` has one clean
    `The First L'Heureux's in Canada` block.
  - `07_portionize_toc_html_v1/portions_toc.jsonl` yields `15` entries at page
    `1`, `9` at page `2`, `2` at page `3`, `3` at page `4`, and `11` at page
    `0`.
  - `output/html/chapter-001.html` contains `15` `<h1>` blocks and `15`
    tables, matching the `15` page-`1` TOC entries.
  - `output/html/chapter-002.html` repeats `The First L'Heureux's in Canada`
    `9` times, matching the `9` page-`2` TOC entries.
  - `output/html/chapter-003.html` and `chapter-004.html` both render source
    page `12` content under different titles because page `3` has two TOC
    entries (`Farm Heritage Award`, `Yvonne`).
  - Current `PIERRE L'HEUREUX` and `ANTOINE L'HEUREUX` later collapse from the
    committed handoff golden's `4→1` and `2→1` table shapes.
- If the fresh repaired run cannot honestly defend the March 11
  `structure_preservation: 0.95` claim in `_coverage-matrix.json`, update the
  row honestly instead of preserving the old score by inertia.

## Plan

### Baseline / Eval

- Reuse `onward-book-r1` as the first failing baseline, then decide whether a
  fresh rerun is needed immediately or only after the first deterministic fix.
- Compare three proof surfaces instead of trusting one validator:
  - early full-book pages/chapters (`page-001`, `page-002`, `chapter-001`
    through `chapter-004`)
  - committed reviewed genealogy hard-case goldens
    (`benchmarks/golden/onward/reviewed_html_slice/` and
    `benchmarks/golden/onward/dossier-doc-web-handoff-v1/`, mapped by title
    when file numbers differ)
  - current validator/report output, to document exactly what it misses

### Implementation Order

1. Add focused failing tests for the dense same-page TOC leaf case and the
   repeated-page chapter-build case.
2. Fix TOC portionization and/or chapter-build handling so same-page leaf
   entries do not turn one source page into repeated chapters or repeated body
   blocks.
3. Re-run the maintained Onward PDF lane and inspect whether later reviewed
   genealogy chapters still regress; if they do, fix the smallest remaining
   table-specific seam or targeted rerun logic.
4. Strengthen maintained validation or comparison reporting so duplicate
   pages/replayed chapters and reviewed hard-case table collapse fail fast in
   future runs.
5. Reconcile docs and coverage truth with the fresh proof run.

### Impact / Risk

- Highest risk is silent scope creep inside `build_chapter_html_v1`, because it
  is already `1820` lines and mixes generic bundle behavior with some
  Onward-specific table normalization.
- The shared Onward PDF is still a local validation asset, not a repo-owned
  fixture, so the story must keep portability and maintained-proof claims
  explicit.
- If the repair needs new comparison artifacts or broader reporting than the
  current genealogy-only validator, prefer an inspectable report over hidden
  heuristics.

## Work Log

20260410-0845 — story created: a new story is warranted because the maintained
full-book Onward PDF lane regressed outside the narrow reviewed genealogy slice
and current guardrails did not catch it. Fresh evidence from
`/Users/cam/Documents/Projects/doc-web/output/runs/onward-book-r1/` shows OCR
page `11` is clean in `02_ocr_ai_gpt51_v1/pages_html.jsonl`, but
`07_portionize_toc_html_v1/portions_toc.jsonl` now emits `15` entries at
printed page `1`, `9` at `2`, `2` at `3`, `3` at `4`, and `11` at `0`; the
built bundle then replays source pages into `output/html/chapter-001.html`
(`15` headings / `15` tables), `chapter-002.html` (`The First L'Heureux's in
Canada` repeated `9` times), and near-duplicate `chapter-003.html` /
`chapter-004.html` from the same source page. Hard-case comparison against the
committed handoff goldens also shows later regression: current `PIERRE
L'HEUREUX` collapses from golden `4` tables to `1`, and current `ANTOINE
L'HEUREUX` from golden `2` to `1`. Current validator blind spot is explicit:
`10_validate_onward_genealogy_consistency_v1/genealogy_consistency_report.jsonl`
reports `flagged_genealogy_chapters: 0` despite the visible breakage. Reviewed
decision context: `docs/ideal.md`, `docs/spec.md`,
`docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-001,
ADR-002, Story 149, Story 154, Story 155, Story 157,
`docs/runbooks/golden-build.md`, the Onward golden READMEs, and
`tests/fixtures/formats/_coverage-matrix.json`. Next step: `/build-story`
should turn this into a focused repair plan centered on TOC portionization,
chapter-build replay prevention, and honest maintained regression coverage.

20260410-0948 — exploration + substrate check: confirmed the primary live
regression is deterministic TOC-page misclassification inside
`modules/portionize/portionize_toc_html_v1/main.py`, not weak OCR on the early
book pages. Using the current module logic against
`/Users/cam/Documents/Projects/doc-web/output/runs/onward-book-r1/05_extract_page_numbers_html_v1/pages_html_with_page_numbers.jsonl`
shows source page `8` is the real TOC (`<h1>INDEX</h1>` plus a descendants
table), while normal genealogy/content pages such as source page `10`
(`printed_page_number: 1`), `35` (`26`), `41` (`32`), and `105` (`96`) are
also treated as TOC pages solely because `_extract_table_entries()` harvests
years/count cells from ordinary family tables and `_is_toc_page()` currently
accepts `table_entry_count >= min_entries` even without any TOC heading. That
produces the bogus `page_start 0/1/2/3/4` and `1974+` entries already visible
in `07_portionize_toc_html_v1/portions_toc.jsonl`, and `build_chapter_html_v1`
then faithfully replays those same source pages once per bad portion into
`output/html/chapter-001.html` through `chapter-004.html`. Files to change are
still the story's predicted narrow seam: `modules/portionize/portionize_toc_html_v1/main.py`,
`tests/test_portionize_toc_html.py`, likely `tests/test_build_chapter_html.py`,
and story/generated methodology docs. Decision context remains aligned with the
Ideal/spec/ADR slice already cited; no new narrower ADR owner was found.
Next step: add failing regression tests that prove real heading-plus-table TOCs
still work while non-TOC genealogy tables no longer create portions or replayed
chapters.

20260410-1038 — implementation + validation: fixed the live early-book replay
regression and made the maintained proof surface honest about the remaining
late-table debt. Changes landed in
`modules/portionize/portionize_toc_html_v1/main.py`,
`modules/build/build_chapter_html_v1/main.py`,
`modules/validate/validate_onward_genealogy_consistency_v1/main.py`,
`configs/recipes/recipe-onward-pdf-html-mvp.yaml`,
`tests/test_portionize_toc_html.py`,
`tests/test_build_chapter_html.py`, and
`tests/test_validate_onward_genealogy_consistency_v1.py`. Fresh targeted checks
passed: `python -m pytest tests/test_portionize_toc_html.py tests/test_validate_onward_genealogy_consistency_v1.py tests/test_build_chapter_html.py -q -k 'portionizer or replayed_same_page_portions or stale_duplicate_tail or same_family_prefix or validate_onward_genealogy_consistency'`
(`11 passed`) and `python -m ruff check ...` on the touched Python files. Real
pipeline proof came from `python driver.py --recipe configs/recipes/recipe-onward-pdf-html-mvp.yaml --input-pdf '/Users/cam/Documents/Projects/doc-web/input/Onward to the Unknown.pdf' --run-id onward-book-r1 --allow-run-id-reuse --output-dir /Users/cam/Documents/Projects/doc-web/output/runs/onward-book-r1 --start-from portionize_toc`, followed by a validator-only rerun from `validate_genealogy_consistency`.
Fresh artifact inspection shows the deterministic TOC failure is fixed:
`/Users/cam/Documents/Projects/doc-web/output/runs/onward-book-r1/07_portionize_toc_html_v1/portions_toc.jsonl`
now writes `23` portions with no duplicate `page_start` values instead of `149`
rows with the bogus `0/1/2/3/4` and `1974+` starts; early output is clean again
in `/Users/cam/Documents/Projects/doc-web/output/runs/onward-book-r1/output/html/chapter-001.html`,
`chapter-002.html`, `chapter-003.html`, and `chapter-004.html`, each now backed
by one source page and one source portion title instead of replaying the same
page under many TOC leaf titles. The widened validator now records the truth
that the late reviewed-golden lane is still not recovered: `/Users/cam/Documents/Projects/doc-web/output/runs/onward-book-r1/10_validate_onward_genealogy_consistency_v1/genealogy_consistency_detail.json`
reports `duplicate_portion_page_start_count: 0` but
`reviewed_golden_flagged_chapter_count: 4`, naming `ARTHUR L'HEUREUX`,
`MARIE-LOUISE (L'HEUREUX) LaCLARE`, `PIERRE L'HEUREUX`, and
`ANTOINE L'HEUREUX` as structurally worse than the committed handoff goldens.
Examples from the same fresh run: current `chapter-010.html` has `2` tables vs
golden `5`; current `chapter-017.html` has `1` table / `0` `h2` / `0` `h3` vs
golden `8` / `3` / `2`; current `chapter-022.html` has `1` table vs golden `4`;
current `chapter-023.html` has `1` table vs golden `2`. Impact: the user-facing
new-project regression that duplicated early chapters is actually fixed and now
guarded, but this story remains `In Progress` because the late genealogy-table
collapse still needs a separate repair pass rather than another silent green
run.

20260410-1608 — maintained genealogy recovery completed on a fresh partial
driver proof run that reuses the shared OCR/table artifacts and exercises the
real downstream runtime from `table_fix_continuations` onward. Code changes in
`modules/common/onward_genealogy_html.py`,
`modules/build/build_chapter_html_v1/main.py`,
`modules/adapter/rerun_onward_genealogy_consistency_v1/main.py`, and
`modules/validate/validate_onward_genealogy_consistency_v1/main.py` did three
things together: (1) moved genealogy-table condensation to per-page prep so the
builder still merges oversplit family tables inside a page but no longer
collapses distinct tables across page boundaries; (2) stopped the validator and
rerun selector from treating preserved external genealogy headings as drift by
default; and (3) prevented untargeted deterministic normalization plus OCR
quota fallback from flattening pages that are already structurally correct for
the reviewed golden shape. Fresh focused coverage now passes with
`python -m pytest tests/test_build_chapter_html.py tests/test_rerun_onward_genealogy_consistency_v1.py tests/test_validate_onward_genealogy_consistency_v1.py tests/test_pdf_intake_recipe.py -q`
(`134 passed`) plus fresh `python -m ruff check` on the touched Python files.
Fresh real-pipeline evidence came from
`python driver.py --recipe /tmp/story206-onward-proof.yaml --run-id story206-onward-proof-r7 --force`.
That run produced zero maintained genealogy drift and zero reviewed-golden
regression in both
`/Users/cam/.codex/worktrees/c67b/doc-web/output/runs/story206-onward-proof-r7/06_validate_onward_genealogy_consistency_v1/genealogy_consistency_report_initial.jsonl`
and
`/Users/cam/.codex/worktrees/c67b/doc-web/output/runs/story206-onward-proof-r7/09_validate_onward_genealogy_consistency_v1/genealogy_consistency_report_after_rerun.jsonl`
(`flagged_genealogy_chapters: 0`, `reviewed_golden_flagged_chapter_count: 0`,
`duplicate_portion_page_start_count: 0`). Manual artifact inspection confirms
the early replay surface stays fixed in
`/Users/cam/.codex/worktrees/c67b/doc-web/output/runs/story206-onward-proof-r7/08_build_chapter_html_v1/chapters_manifest_after_rerun.jsonl`
and the generated HTML: `chapter-001.html` maps only to source page `10`,
`chapter-002.html` only to `11`, `chapter-003.html` only to `12`, and
`chapter-004.html` only to `13`; the rendered files no longer repeat the same
source page/body across many TOC leaf titles. Manual late-chapter inspection
also confirms the reviewed hard cases are back in family-table shape:
`chapter-010.html` renders `27` tables with preserved multi-generation heading
structure and no `<dl>`, `chapter-017.html` renders `11` tables with preserved
`h2`/`h3` structure and no `<dl>`, `chapter-022.html` now renders `4` tables
matching the reviewed-golden count, and `chapter-023.html` renders `2` tables
with no `<dl>`. The rerun lane stayed honest in the same proof:
`/Users/cam/.codex/worktrees/c67b/doc-web/output/runs/story206-onward-proof-r7/07_rerun_onward_genealogy_consistency_v1/rerun_onward_genealogy_summary.json`
shows `targeted_page_count: 0` and only conservative untargeted
deterministic-normalization cleanup on pages that no longer threaten the
reviewed-golden structure. Remaining close-out debt is procedural, not product:
`make test`, `make lint`, and final story-status/graph sync are still open.
20260410-1949 — `/mark-story-done` close-out: revalidated Story 206 on the
exact post-fix tree before closing it. Fresh project checks in this close-out
sequence both passed: `make test` completed with `544 passed, 4 warnings in
681.41s`, and `make lint` passed cleanly. The only warnings were the existing
Pydantic `dict()` deprecation notices in
`modules/portionize/portionize_headers_numeric_v1/main.py`, unrelated to this
story's seam. Fresh current-pass proof remains
`/Users/cam/.codex/worktrees/c67b/doc-web/output/runs/story206-onward-proof-r7/`
from the real downstream runtime at `table_fix_continuations` onward:
`06_validate_onward_genealogy_consistency_v1/genealogy_consistency_report_initial.jsonl`
and
`09_validate_onward_genealogy_consistency_v1/genealogy_consistency_report_after_rerun.jsonl`
both still report `flagged_genealogy_chapters: 0`,
`reviewed_golden_flagged_chapter_count: 0`, and
`duplicate_portion_page_start_count: 0`. Manual artifact inspection in this
close-out sequence reconfirmed
`08_build_chapter_html_v1/chapters_manifest_after_rerun.jsonl` maps
`chapter-001.html` only to source page `10`, `chapter-002.html` only to `11`,
`chapter-003.html` only to `12`, and `chapter-004.html` only to `13`, and
reopened the repaired hard cases in `output/html/chapter-010.html`,
`chapter-017.html`, `chapter-022.html`, and `chapter-023.html` to confirm the
reviewed-golden structure still holds with no `<dl>` regressions. No extra
coverage-matrix downgrade, methodology-state change, or eval update was needed
because the story repaired the maintained `scanned-pdf-tables` claim instead of
changing the claimed support surface. Result: Story 206 now closes honestly as
the maintained Onward full-book regression recovery plus widened guardrail
surface. Next step: `/check-in-diff`.

20260410-1147 — post-close correction + fresh proof: Story 206 had been closed
too early. Manual inspection after close-out proved
`output/runs/story206-onward-proof-r7/output/html/chapter-011.html` was still
fragmented, and the then-current validator had masked that debt by only
flagging reviewed-golden drift in the "fewer tables/headings" direction.
Follow-up work fixed three coupled seams: `modules/common/onward_genealogy_html.py`
now absorbs generic genealogy `h1/h2/h3` runs into subgroup rows, 
`modules/build/build_chapter_html_v1/main.py` now finalizes chapter bodies
through that shared genealogy merge before writeout (the real staging gap that
left written chapter HTML more fragmented than helper-level results), and
`modules/validate/validate_onward_genealogy_consistency_v1/main.py` now still
catches over-fragmentation but no longer flags high-similarity structural
simplification against the dossier handoff pack as drift. Regression coverage
expanded in `tests/test_build_chapter_html.py`,
`tests/test_validate_onward_genealogy_consistency_v1.py`,
`tests/test_rerun_onward_genealogy_consistency_v1.py`, and
`tests/test_pdf_intake_recipe.py`. Fresh targeted validation now passes with
`python -m pytest tests/test_build_chapter_html.py tests/test_validate_onward_genealogy_consistency_v1.py tests/test_rerun_onward_genealogy_consistency_v1.py tests/test_pdf_intake_recipe.py -q`
(`139 passed`) plus fresh `python -m ruff check` on the touched files. Fresh
real-pipeline evidence is the maintained proof
`output/runs/story206-onward-proof-r10/`: a resumed current-code
`validate_final` pass via
`python driver.py --recipe /tmp/story206-onward-proof.yaml --run-id story206-onward-proof-r10 --allow-run-id-reuse --start-from validate_final --force`
reports `flagged_genealogy_chapters: 0`,
`reviewed_golden_flagged_chapter_count: 0`, and
`duplicate_portion_page_start_count: 0` in
`09_validate_onward_genealogy_consistency_v1/genealogy_consistency_report_after_rerun.jsonl`.
Manual artifact inspection on the same fresh proof reconfirms the early replay
surface stays fixed in
`08_build_chapter_html_v1/chapters_manifest_after_rerun.jsonl`
(`chapter-001.html` -> `[10]`, `chapter-002.html` -> `[11]`,
`chapter-003.html` -> `[12]`, `chapter-004.html` -> `[13]`) and that the
reviewed hard cases now render as coherent flat tables rather than broken
multi-table fragments:
`chapter-010.html` -> `2` tables / `107` subgroup rows,
`chapter-011.html` -> `2` / `104`,
`chapter-017.html` -> `2` / `73`,
`chapter-022.html` -> `2` / `37`,
`chapter-023.html` -> `2` / `16`.
Result: the user-visible Leonidas/full-slice regression is now actually fixed
on current code, not just papered over by the earlier validator.
