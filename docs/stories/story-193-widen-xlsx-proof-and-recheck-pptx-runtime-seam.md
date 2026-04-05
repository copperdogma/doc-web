---
title: "Widen Maintained XLSX Proof and Recheck PPTX Runtime Seam"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #1 (Ingest), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Any format, any condition, Dossier-ready output, Traceability is the product"
spec_refs:
  - "spec:1"
  - "spec:1.1"
  - "spec:6"
  - "spec:7"
  - "spec:8"
adr_refs: []
depends_on:
  - "175"
category_refs:
  - "spec:1"
  - "spec:6"
  - "spec:7"
  - "spec:8"
compromise_refs:
  - "C2"
input_coverage_refs:
  - "xlsx"
  - "pptx"
architecture_domains:
  - "doc_web_runtime"
roadmap_tags:
  - "campaign:maintained-intake-honesty"
legacy_system: ""
---

# Story 193 — Widen Maintained XLSX Proof and Recheck PPTX Runtime Seam

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md`, `docs/stories/story-175-office-document-proof-widening-and-xlsx-pptx-lane-decision.md`, `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, `testdata/README.md`, and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower office-family residue ADR or runbook
**Depends On**: Story 175

## Goal

Story 175 proved one maintained XLSX slice and left PPTX as an explicit runtime defer. That first office-family decision is now closed, but the current runtime truth still has residue: the `xlsx` row rests on a single repo-owned workbook, while `pptx` still says only that the seam was blocked in an older checkout. This story widens the maintained XLSX proof surface beyond `xlsx-mini`, reruns the PPTX seam on the current checkout, and leaves one honest office-runtime answer: either XLSX earns broader confidence and PPTX stays explicitly blocked with fresh current-pass evidence, or the repo records the narrower supported slice and next blocker without vague office backlog residue. This is a new story instead of reopening Story 175 because the success surface is different: Story 175 decided whether XLSX could exist as a maintained lane at all, while this follow-up measures family breadth for that maintained lane and revalidates whether PPTX is still only a dependency/runtime block in the present repo state.

## Acceptance Criteria

- [x] The maintained XLSX proof surface widens beyond the single `xlsx-mini` workbook:
  - [x] at least two additional repo-owned or reproducibly generated XLSX fixtures exist, or the story records why broader fixture creation is not honest in the current substrate
  - [x] every XLSX fixture in the widened set is classified as `supported`, `bounded unsupported`, or `failed`
  - [x] if the widened fixture set clears one coherent supported slice with inspected outputs, the `xlsx` row can move beyond its current single-fixture claim; otherwise it stays bounded honestly with the exact failure boundary recorded
- [x] Fresh `driver.py` proof exists for every XLSX fixture claimed as supported:
  - [x] the maintained XLSX lane leaves inspectable artifacts in `output/runs/`
  - [x] manual inspection is recorded for `elements.jsonl`, `output/html/manifest.json`, `output/html/provenance/blocks.jsonl`, and representative rendered HTML
  - [x] provenance remains pageless-source honest and does not fabricate page numbers or stronger cell-level guarantees than the artifacts actually support
- [x] The PPTX seam is rechecked on the current checkout using the repo-owned probe fixture:
  - [x] the story records the exact current command and observed result for `unstructured.partition.pptx` or the closest maintained probe path
  - [x] if the seam is still blocked, the blocker is named concretely with fresh current-pass evidence and the `pptx` row/docs reflect that exact runtime state
  - [x] the seam stayed blocked, so the story records why absorbing PPTX would still cross a new runtime seam and stops there
- [x] `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, `testdata/README.md`, and any touched office-runtime docs reflect the exact post-story XLSX/PPTX reality with no stale “has fixture” or “blocked” wording from older checkout state

## Out of Scope

- Claiming full Excel or PowerPoint support across formulas, charts, merged cells, speaker notes, embedded media, comments, or complex slide-layout semantics in one pass
- Reopening the accepted `doc-web` runtime boundary from ADR-002 or the Docling boundary decision from ADR-003
- Hidden auto-routing, planner dispatch, or office-to-PDF fallback beyond the explicit-recipe compromise in `spec:1.1`
- AI-first slide repair or OCR-based office recovery before the current native seams are freshly measured
- General office-family cleanup outside the maintained XLSX lane and the explicit PPTX seam recheck

## Approach Evaluation

- **Simplification baseline**: start from the existing native office seams. A single LLM call is not the right first move here because XLSX already has working deterministic extraction and bundle emission, and PPTX first needs a current-checkout substrate answer before any AI repair would mean anything.
- **AI-only**: low-value default. AI could potentially reinterpret slide reading order later, but it would discard native office structure and provenance too early for the first proof-widening pass.
- **Hybrid**: plausible only if a fresh PPTX runtime probe becomes runnable but still needs bounded help on reading order or mixed-layout grouping. That decision should be based on current artifacts, not assumed up front.
- **Pure code**: likely strongest for the initial scope. XLSX widening is fixture generation, maintained recipe proof, and truth-surface updates. PPTX may remain a pure dependency/runtime classification story if the import path is still blocked.
- **Repo constraints / prior decisions**: `spec:1.1` keeps recipe ownership explicit. ADR-002 and ADR-003 keep `doc-web` as the accepted Dossier-facing runtime boundary. Story 175 already proved one maintained XLSX slice and made PPTX defer explicit; this follow-up should reuse that boundary instead of inventing a new office abstraction.
- **Existing patterns to reuse**: `configs/recipes/recipe-xlsx-html-mvp.yaml`, `modules/extract/unstructured_xlsx_intake_v1/main.py`, `modules/transform/xlsx_elements_to_bundle_v1/main.py`, `modules/common/office_native_bundle.py`, `tests/test_xlsx_intake_recipe.py`, `testdata/generate_xlsx_fixture.py`, `testdata/generate_pptx_fixture.py`, and Story 175's office-fixture discipline.
- **Eval**: the deciding proof is fresh `driver.py` artifact inspection on the widened XLSX fixture set plus a fresh current-pass PPTX seam probe. No dedicated promptfoo eval exists or is required unless the story starts changing AI behavior instead of runtime/fixture truth.

## Tasks

- [x] Freeze the widened office proof surface for this follow-up:
  - [x] add at least two additional repo-owned or reproducibly generated XLSX fixtures, or record why broader fixture generation is not yet honest
  - [x] keep the existing `pptx-mini` probe fixture current or regenerate it if the checked-in artifact no longer matches its markdown source
  - [x] document the intended supported slice for each widened XLSX fixture before changing implementation claims
- [x] Measure the current maintained XLSX lane unchanged on the widened fixture set:
  - [x] rerun `configs/recipes/recipe-xlsx-html-mvp.yaml` through `driver.py` on every widened XLSX fixture
  - [x] inspect extraction artifacts, final bundle/provenance outputs, and representative HTML before changing code
  - [x] classify each fixture against the supported slice instead of assuming the first maintained lane generalizes
- [x] Recheck the PPTX runtime seam on the current checkout before broadening implementation:
  - [x] rerun the current `unstructured.partition.pptx` probe or the closest maintained runtime path on `testdata/pptx-mini.pptx`
  - [x] if the seam still fails, capture the exact blocker and stop short of speculative PPTX glue
  - [x] the seam remained unrunnable, so the story records that no honest PPTX bundle/provenance inspection could happen without crossing a new dependency/runtime seam
- [x] Implement only the smallest coherent changes the fresh proof justifies:
  - [x] keep or adjust the maintained XLSX lane only where widened artifacts show generic gaps
  - [x] do not add PPTX runtime plumbing because the seam did not become runnable in this pass
  - [x] do not add AI or fallback conversions unless the native seam is freshly shown to be insufficient on the claimed slice
- [x] Leave repeatable proof behind:
  - [x] extend `tests/test_xlsx_intake_recipe.py` and any needed fixture generators for the widened XLSX slice
  - [x] keep PPTX as a repeatable import-seam recheck because the current checkout still exposes no runnable native path worth preserving as a recipe/test lane
  - [x] run real `driver.py` proofs for every lane claimed as maintained and manually inspect the resulting artifacts in `output/runs/`
- [x] Regenerate generated methodology views with `make methodology-compile` and confirm the story/index surfaces stay aligned
- [x] If this story changes documented format coverage or graduation reality: update `tests/fixtures/formats/_coverage-matrix.json` and any relevant methodology state honestly
- [x] Check whether the chosen implementation makes any existing office fixture notes, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] No pipeline-module behavior changed, but fresh `driver.py` proofs were rerun and the resulting artifacts were manually inspected in `output/runs/`
  - [x] Agent tooling did not change; `make skills-check` was not required
- [x] If evals or goldens changed: not applicable; no eval or golden surface changed in this pass
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every support claim traces back to named fixtures, run IDs, and inspected artifacts
  - [x] T1 — AI-First: do not write office-format logic for a problem the existing native seams already solve
  - [x] T2 — Eval Before Build: widen the proof surface and rerun the PPTX seam before changing runtime behavior
  - [x] T3 — Fidelity: workbook and slide content stay source-faithful, with no fabricated page/cell/slide guarantees
  - [x] T4 — Modular: prefer extending the existing office-native lane over creating a parallel office subsystem
  - [x] T5 — Inspect Artifacts: validate real bundle/provenance outputs and rendered HTML, not just logs or import checks

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

- **Owning module / area**: this story lives at the office-native intake seam plus the `doc-web` bundle/provenance boundary for non-page-native sources. Primary owners are the maintained XLSX path, the office fixture generators, and the PPTX seam-probe surface.
- **Methodology reality**: this belongs to `spec:1`, `spec:6`, `spec:7`, and `spec:8`. In `docs/methodology/state.yaml`, `spec:1` and `spec:6` substrates exist, `spec:7` is still `partial`, and `spec:8` exists. The relevant compromise is `C2` in `climb`: recipe-backed office support should widen only as explicit proof justifies. Post-story, the relevant coverage rows are `xlsx` (`passing` on a bounded slice) and `pptx` (`has-fixture`, still blocked at the import seam).
- **Substrate evidence**: verified in repo that `configs/recipes/recipe-xlsx-html-mvp.yaml`, `modules/extract/unstructured_xlsx_intake_v1/main.py`, `modules/transform/xlsx_elements_to_bundle_v1/main.py`, `modules/common/office_native_bundle.py`, `tests/test_xlsx_intake_recipe.py`, `testdata/generate_xlsx_fixture.py`, `testdata/xlsx-mini.source.json`, `testdata/xlsx-mini.xlsx`, `testdata/generate_pptx_fixture.py`, `testdata/pptx-mini.md`, and `testdata/pptx-mini.pptx` already exist. Fresh current-pass import checks in this checkout show `openpyxl` and `unstructured.partition.xlsx` import successfully, while `pptx` and `unstructured.partition.pptx` both fail with `ModuleNotFoundError: No module named 'pptx'`.
- **Data contracts / schemas**: the current maintained XLSX lane already writes `doc_web_bundle_manifest_v1` and `doc_web_provenance_block_v1` without page numbers. If widened XLSX proof or a revived PPTX seam needs stronger source anchors than current `source_element_ids`, add those fields to `schemas.py` before relying on stamped artifacts. `driver.py` already exposes `--input-xlsx`; there is no current `--input-pptx` override in code.
- **File sizes**: likely touched files are `testdata/generate_xlsx_fixture.py` (43 lines), `testdata/generate_pptx_fixture.py` (43), `testdata/README.md` (97), `README.md` (248), `docs/RUNBOOK.md` (395), `tests/fixtures/formats/_coverage-matrix.json` (465), `modules/extract/unstructured_xlsx_intake_v1/main.py` (166), `modules/transform/xlsx_elements_to_bundle_v1/main.py` (126), `modules/common/office_native_bundle.py` (359), `tests/test_xlsx_intake_recipe.py` (80), `pyproject.toml` (42), and `driver.py` (2250). `driver.py` is already well over 500 lines, so only touch it if the PPTX seam becomes real enough to justify explicit input plumbing.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, ADR-003, Story 175, `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, `testdata/README.md`, and the current office-native modules/tests. No narrower office-family residue ADR, runbook, scout, or note already resolves this follow-up.

## Files to Modify

- `testdata/generate_xlsx_fixture.py` — extend fixture generation only if widened XLSX proof needs new workbook shapes (43 lines)
- `testdata/*.source.json` / `testdata/*.xlsx` — add repo-owned or reproducible XLSX fixtures for the widened proof surface
- `tests/test_xlsx_intake_recipe.py` — widen maintained XLSX recipe coverage across the new fixture set (80 lines)
- `modules/extract/unstructured_xlsx_intake_v1/main.py` — adjust XLSX extraction only if widened artifacts expose a generic gap (166 lines)
- `modules/transform/xlsx_elements_to_bundle_v1/main.py` — adjust bundle shaping only if widened XLSX proof shows a reusable issue (126 lines)
- `modules/common/office_native_bundle.py` — reuse or narrow shared office-native bundle behavior if widened artifacts expose a cross-fixture issue (359 lines)
- `testdata/generate_pptx_fixture.py` — refresh the probe fixture only if the markdown and checked-in PPTX drifted (43 lines)
- `pyproject.toml` — touch only if a fresh PPTX seam requires an explicit dependency declaration for an honestly maintained probe or lane (42 lines)
- `driver.py` — add explicit PPTX input plumbing only if the seam becomes runnable and the story honestly absorbs it (2250 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — update `xlsx` and `pptx` rows to the exact post-story truth (465 lines)
- `testdata/README.md` — document widened XLSX fixtures and the fresh PPTX runtime state (97 lines)
- `README.md` — keep user-facing office-runtime claims aligned with the new proof surface (248 lines)
- `docs/RUNBOOK.md` — publish verified XLSX proof commands and the exact PPTX runtime state if it changes (395 lines)

## Redundancy / Removal Targets

- The current single-workbook implication in the `xlsx` coverage row and fixture docs if wider proof lands successfully
- Any stale wording that says PPTX is blocked only because of Story 175-era evidence once a fresh current-checkout seam probe exists
- Any scratch one-off office probe notes or commands that become redundant once widened fixtures and repeatable tests are committed

## Notes

- New story justification: reopening Story 175 would blur a validated first-lane decision with a new family-breadth proof surface. Story 175 answered whether XLSX could exist as a maintained lane and whether PPTX was an honest defer at that time; this follow-up asks whether XLSX can widen beyond one workbook and whether PPTX is still blocked in the current checkout.
- Bias toward explicit proof over office-family optimism. If widened XLSX artifacts expose a narrower supported slice than expected, keep the row bounded honestly instead of promoting it because the first mini workbook passed.
- If the fresh PPTX seam becomes runnable but immediately raises a new provenance or slide-order contract question broader than this story's runtime boundary, stop and record that ADR-sized question instead of widening the scope by inertia.

## Plan

### Exploration Summary

- **Ideal alignment:** proceed. This story closes an active Ideal gap in
  office-document ingest and Dossier-ready export without widening claims
  faster than artifact evidence supports.
- **Methodology state:** `spec:1`, `spec:6`, and `spec:8` substrates are
  `exists`; `spec:7` remains `partial`; `C2` is in `climb`; active roadmap
  focus still includes `spec:7`. At exploration start the relevant coverage
  rows were `xlsx` and `pptx`, both `has-fixture`; post-story, `xlsx` moved to
  bounded `passing` while `pptx` remains `has-fixture`.
- **Critical substrate verified in code:** the maintained XLSX lane is real in
  `configs/recipes/recipe-xlsx-html-mvp.yaml`,
  `modules/extract/unstructured_xlsx_intake_v1/main.py`,
  `modules/transform/xlsx_elements_to_bundle_v1/main.py`,
  `modules/common/office_native_bundle.py`, and
  `tests/test_xlsx_intake_recipe.py`. `driver.py` already supports
  `--input-xlsx`. The repo also already has generic fixture generators for XLSX
  and PPTX.
- **Critical substrate missing or partial:** fresh current-pass import checks in
  this checkout still fail for `pptx` and `unstructured.partition.pptx` with
  `ModuleNotFoundError: No module named 'pptx'`. `driver.py` has no current
  `--input-pptx` override, no maintained PPTX recipe exists, and no PPTX
  bundle/provenance mapping exists yet.
- **Patterns to follow:** keep using the generic office-native bundle helper,
  widen proof with repo-owned source JSON plus generated fixtures, and keep the
  supported slice explicit rather than writing new office-specific logic by
  default.
- **Potential redundancy to remove:** stale docs that still describe PPTX only
  via Story 175-era evidence, and the current implicit claim that XLSX proof is
  only one workbook if wider maintained proof lands.

### Eval-First Gate

- **Baseline eval surface:** real `driver.py` proofs plus manual artifact
  inspection on maintained XLSX fixtures, and a fresh current-pass PPTX import
  / probe command.
- **Current maintained baseline:** `buildstory193-xlsx-baseline-bce2ea34`
  succeeded on `testdata/xlsx-mini.xlsx` with `entry_count = 2`,
  `provenance_row_count = 2`, reading order `["page-001", "page-002"]`, and
  the expected `Roster` / `Visits` pages under
  `output/runs/buildstory193-xlsx-baseline-bce2ea34/output/html/`.
- **Current widened temporary probes:**
  - `story193-probe-multi_sheet-18e70e` succeeded with two maintained pages
    (`Summary`, `Regions`) and clean table-only provenance rows.
  - `story193-probe-two_tables_one_sheet-edd73f` succeeded with one page,
    two separate table blocks on the same sheet, and two provenance rows,
    which is good evidence that the current lane already handles multiple table
    regions on one sheet.
  - `story193-probe-merged_formula-e5ab57` also ran, but the workbook is not an
    honest supported-slice win: Unstructured split the merged title into a
    heading, emitted the main table, then promoted the `Total` formula row to a
    heading block instead of preserving it as table data. That makes it a good
    bounded-unsupported probe rather than a supported fixture candidate.
- **Current PPTX seam:** `python - <<'PY' ... from unstructured.partition.pptx
  import partition_pptx ... PY` fails immediately in this checkout with
  `ModuleNotFoundError: No module named 'pptx'`.
- **Candidate approaches:** pure code / fixture work is the correct first step.
  No AI comparison is needed yet because the maintained XLSX lane is already
  native-structure based and PPTX still lacks a runnable native substrate.

### Implementation Order

1. **Commit widened XLSX fixtures on the currently supported slice** (`S`)
   - **Files**:
     - `testdata/*.source.json`
     - `testdata/*.xlsx`
     - `testdata/README.md`
   - **What changes**:
     - add at least two repo-owned XLSX fixtures based on the current passing
       probe shapes
       - recommended supported fixtures: a multi-sheet simple-table workbook
         and a two-tables-on-one-sheet workbook
       - recommended bounded-unsupported probe fixture: a merged-title/formula
         workbook to make the current failure edge inspectable
     - keep using `testdata/generate_xlsx_fixture.py` unless the source format
       itself needs a small extension
   - **Done looks like**:
     - the repo has a widened, reproducible XLSX fixture surface with one
       explicit support boundary instead of a single passing mini workbook

2. **Widen automated proof for the supported XLSX slice** (`S`)
   - **Files**:
     - `tests/test_xlsx_intake_recipe.py`
     - possibly `modules/common/office_native_bundle.py`
     - possibly `modules/extract/unstructured_xlsx_intake_v1/main.py`
     - possibly `modules/transform/xlsx_elements_to_bundle_v1/main.py`
   - **What changes**:
     - extend recipe smoke coverage across the widened supported fixtures
     - only change runtime code if the checked-in supported fixtures reveal a
       real generic defect that the temporary probes did not expose
     - do not “fix” the merged/formula probe by broadening the supported slice
       unless fresh artifact evidence shows the result is actually honest
   - **Done looks like**:
     - supported fixtures pass through `driver.py` and tests, while the
       unsupported boundary remains explicit instead of accidentally promoted

3. **Recheck PPTX honestly on the current checkout** (`XS`)
   - **Files**:
     - `testdata/README.md`
     - `tests/fixtures/formats/_coverage-matrix.json`
     - `README.md`
     - `docs/RUNBOOK.md`
     - optionally `pyproject.toml`
     - optionally `driver.py`
   - **What changes**:
     - rerun the probe on `testdata/pptx-mini.pptx`
     - if it is still blocked, update the truth surfaces with fresh evidence
       and stop there
     - if making it runnable requires adding a new dependency and explicit
       `driver.py` input plumbing, treat that as a conditional scope expansion,
       not an automatic part of this pass
   - **Done looks like**:
     - PPTX is either freshly blocked with exact evidence or elevated into an
       explicitly approved maintained follow-up seam

4. **Sync truth surfaces** (`S`)
   - **Files**:
     - `tests/fixtures/formats/_coverage-matrix.json`
     - `README.md`
     - `docs/RUNBOOK.md`
     - `testdata/README.md`
   - **What changes**:
     - reflect the widened supported XLSX slice and the exact current PPTX
       runtime state
   - **Done looks like**:
     - docs, coverage, and maintained smoke guidance all tell the same office
       story

### Impact Analysis

- **Files most likely to change:** fixture JSON/XLSX assets, XLSX smoke tests,
  coverage/docs. Runtime code may not need to change at all if the temporary
  supported probes remain representative.
- **Files at risk:** `modules/common/office_native_bundle.py`,
  `modules/extract/unstructured_xlsx_intake_v1/main.py`, and
  `modules/transform/xlsx_elements_to_bundle_v1/main.py` if widened checked-in
  fixtures expose a generic issue. `driver.py` is at risk only if PPTX becomes
  runnable enough to justify explicit input plumbing.
- **What could break:** widened XLSX fixtures could reveal title/paragraph
  promotion issues similar to DOCX, or they could show that the current lane
  overstates support for formulas / merged cells. PPTX could pull in a new
  dependency without yielding a coherent maintained lane.

### Structural Health Notes

- Prefer extending the existing generic XLSX generator with more source JSON
  files over adding a second fixture-generation path.
- Do not add PPTX runtime code just because the dependency can be installed;
  the seam must first prove it can reach the accepted bundle/provenance boundary
  honestly.
- `driver.py` is already very large, so avoid touching it unless the PPTX seam
  becomes a real maintained candidate.

### Scope Adjustments

- **Folded in automatically:** add one bounded-unsupported XLSX probe fixture
  so the support edge is inspectable in the repo, not just described in prose.
  This is tightly coupled to widening the maintained XLSX proof and does not
  change the story’s goal.
- **Approval-sensitive expansion:** if PPTX becomes runnable only after adding a
  new dependency plus explicit `driver.py` / recipe plumbing, that is a scope
  expansion from “fresh seam recheck” into “new maintained lane work” and
  should be confirmed before landing.

### Human-Approval Blockers

- Conditional PPTX adoption work, if any, needs approval before implementation
  because it could introduce new dependencies and touch oversized runtime files.
- Everything else in the current plan is within the existing story scope and is
  supported by verified local substrate.

## Work Log

20260404-2239 — create-story: created Story 193 after `/triage` confirmed there was no actionable categorized story left except blocked Story 191, while the office-runtime residue still sat in the `xlsx` and `pptx` coverage rows. Evidence reviewed in this pass: `docs/methodology/state.yaml` shows `spec:7` still `partial`; Story 175 already closed the first office-family slice; `configs/recipes/recipe-xlsx-html-mvp.yaml`, `modules/extract/unstructured_xlsx_intake_v1/main.py`, `modules/transform/xlsx_elements_to_bundle_v1/main.py`, `modules/common/office_native_bundle.py`, `tests/test_xlsx_intake_recipe.py`, `testdata/generate_xlsx_fixture.py`, and the current `xlsx-mini` fixture prove the maintained XLSX substrate exists now; fresh current-pass import checks show `openpyxl` and `unstructured.partition.xlsx` are available while `pptx` / `unstructured.partition.pptx` still fail with `ModuleNotFoundError`. Result: a new `Pending` story is honest because the next work is a new proof surface and a fresh runtime recheck, not a reopen of Story 175's already-validated first-lane decision. Next step: `/build-story` should add or classify widened XLSX fixtures, rerun the maintained XLSX lane on them, and remeasure the PPTX seam on the current checkout before choosing any implementation change.
20260404-2247 — /build-story exploration: verified that Story 193 is honestly buildable without reopening Story 175. Context rechecked in this pass: `docs/ideal.md`; `docs/spec.md` (`spec:1`, `spec:1.1`, `spec:6`, `spec:7`, `spec:8`); `docs/methodology/state.yaml`; `docs/methodology/graph.json`; ADR-002; ADR-003; Story 175; `tests/fixtures/formats/_coverage-matrix.json`; `README.md`; `docs/RUNBOOK.md`; `testdata/README.md`; `pyproject.toml`; `configs/recipes/recipe-xlsx-html-mvp.yaml`; `modules/extract/unstructured_xlsx_intake_v1/main.py`; `modules/transform/xlsx_elements_to_bundle_v1/main.py`; `modules/common/office_native_bundle.py`; and `tests/test_xlsx_intake_recipe.py`. Fresh baseline proof: `buildstory193-xlsx-baseline-bce2ea34` succeeded on `testdata/xlsx-mini.xlsx` with `entry_count = 2`, `provenance_row_count = 2`, and the expected `Roster` / `Visits` pages. Fresh temporary widened probes showed the current maintained lane already handles two important workbook shapes with no code change: `story193-probe-multi_sheet-18e70e` produced clean `Summary` / `Regions` pages, and `story193-probe-two_tables_one_sheet-edd73f` preserved two separate table blocks on one sheet. The main surprise is the current explicit boundary candidate: `story193-probe-merged_formula-e5ab57` ran structurally, but Unstructured promoted `Budget Notes` and the `Total` row to heading blocks and dropped the formula summary out of the table, which makes that workbook a good bounded-unsupported fixture rather than a supported one. Fresh current-pass PPTX probe still fails immediately with `ModuleNotFoundError: No module named 'pptx'`, and `driver.py` still has no `--input-pptx` path, so the story is buildable for XLSX widening and truth-surface repair now while PPTX remains only a recheck / possible approval-gated expansion. Next step: user approval on the plan, then move Story 193 to `In Progress` and implement the widened XLSX fixtures/tests first; stop for confirmation before any new PPTX dependency or runtime-plumbing work.
20260404-2334 — implementation: widened the checked-in XLSX fixture/test surface, refreshed the repo truth surfaces, and revalidated the maintained boundary without expanding PPTX runtime scope. Added `testdata/xlsx-multi-sheet.source.json`, `testdata/xlsx-two-tables.source.json`, and `testdata/xlsx-merged-formula.source.json` plus their generated `.xlsx` artifacts; extended `testdata/generate_xlsx_fixture.py` to support `merged_ranges`; and widened `tests/test_xlsx_intake_recipe.py` so the maintained smoke lane now covers three supported fixtures (`xlsx-mini`, `xlsx-multi-sheet`, `xlsx-two-tables`) while leaving `xlsx-merged-formula` as an explicit boundary probe instead of silently claiming it. Fresh proof runs in `output/runs/`: `story193-xlsx-mini-proof-20260404`, `story193-xlsx-multi-sheet-proof-20260404`, and `story193-xlsx-two-tables-proof-20260404` all completed through `driver.py` and left inspected `01_unstructured_xlsx_intake_v1/elements.jsonl`, `output/html/manifest.json`, `output/html/provenance/blocks.jsonl`, and rendered HTML. Manual inspection confirmed the supported slice is honest and pageless-source bounded: `story193-xlsx-mini-proof-20260404/output/html/page-001.html` preserves the `Roster` table with `Foothills County`; `story193-xlsx-multi-sheet-proof-20260404/output/html/page-002.html` preserves the `Regions` table with `Foothills` / `Harbor`; `story193-xlsx-two-tables-proof-20260404/output/html/page-001.html` preserves two separate table blocks in one sheet-named entry; all inspected provenance rows carry `source_element_ids` and omit any page-number field. The bounded unsupported probe `story193-xlsx-merged-formula-probe-20260404` also completed, but inspected `elements.jsonl` and `output/html/page-001.html` confirm the current edge: Unstructured emits `Title`, `Table`, `Title` and renders `<h1>Budget Notes</h1> ... <h2>Total</h2>` around the main table, so merged-title / formula-summary structure is still outside the maintained slice. Fresh PPTX recheck remained blocked with the exact command `python - <<'PY' ... from unstructured.partition.pptx import partition_pptx ... PY` producing `ModuleNotFoundError: No module named 'pptx'`, so no honest PPTX recipe or bundle/provenance proof could be absorbed in this pass. Truth surfaces updated in `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, and `testdata/README.md`; `xlsx` now records a bounded `passing` slice and `pptx` cites the fresh blocker. Verification in this pass: `python -m pytest tests/test_xlsx_intake_recipe.py -q` → `4 passed in 12.43s`; `make lint` → pass; `make test` → `465 passed, 4 warnings`. Next step: regenerate methodology views, then hand off for `/validate`.
20260404-2336 — methodology compile: reran `make methodology-compile` after the Story 193, coverage-matrix, and docs updates so the generated methodology surfaces match the new office-runtime truth. Result: `docs/methodology/graph.json` and `docs/stories.md` were rebuilt successfully and now reflect Story 193 as an `In Progress` implementation with the widened XLSX proof slice and refreshed PPTX blocker wording. Next step: `/validate`.
20260404-2346 — validation follow-up: addressed the two `/validate` findings from the previous pass and reran fresh checks. First, fixed `testdata/generate_xlsx_fixture.py` so merged ranges are applied after rows are appended, then regenerated `testdata/xlsx-merged-formula.xlsx` and re-opened it directly with `openpyxl`: the checked-in probe now correctly places `Budget Notes` in merged `A1:C1` with the header row starting immediately below it. Second, refreshed the stale methodology wording in this story so the post-story state now says `xlsx` is bounded `passing` and `pptx` remains `has-fixture`. Fresh proof remained stable after the fixture correction: rerunning `story193-xlsx-merged-formula-probe-20260404` through `driver.py` still produced `Title`, `Table`, `Title`, and inspected `output/html/page-001.html` still renders `<h1>Budget Notes</h1>`, the main table, and `<h2>Total</h2>`, so the unsupported-boundary conclusion did not depend on the earlier malformed workbook. Fresh validation in this pass: `make lint` → pass; `make test` → `465 passed, 4 warnings`; PPTX import probe still fails with `ModuleNotFoundError: No module named 'pptx'`. Result: the prior validation findings are resolved and the validation gate is now checked. Next step: `/mark-story-done`.
20260404-2353 — mark-story-done: closed Story 193 after fresh close-out validation confirmed the widened XLSX proof slice and refreshed PPTX blocker are stable on the current tip. Fresh close-out evidence in this pass: `python -m pytest tests/` → `465 passed, 4 warnings`; `python -m ruff check modules/ tests/` → pass; `story193-xlsx-merged-formula-probe-20260404` rerun after the generator fix still produced `Title`, `Table`, `Title` with inspected `Budget Notes` / table / `Total` HTML, confirming the bounded unsupported edge remains honest on the corrected checked-in fixture. Story status is now `Done`, the workflow gate for `/mark-story-done` is checked, and the next step is `/check-in-diff`.
