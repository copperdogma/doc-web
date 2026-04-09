---
title: "Establish the First Honest EPUB Direct-Entry Seam"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #1 (Ingest), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Any format, any condition, Dossier-ready output, Transparency over magic"
spec_refs:
  - "spec:1"
  - "spec:1.1"
  - "spec:3"
  - "spec:3.1"
  - "spec:6"
  - "spec:7"
  - "spec:8"
  - "spec:9"
adr_refs: []
depends_on: []
category_refs:
  - "spec:1"
  - "spec:3"
  - "spec:6"
  - "spec:7"
  - "spec:8"
  - "spec:9"
compromise_refs:
  - "B1"
  - "C2"
  - "C3"
  - "B10"
input_coverage_refs:
  - "epub"
architecture_domains:
  - "doc_web_runtime"
roadmap_tags:
  - "campaign:maintained-intake-honesty"
legacy_system: ""
---

# Story 201 — Establish the First Honest EPUB Direct-Entry Seam

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/stories/story-172-maintained-docx-intake-lane.md`, `docs/stories/story-194-office-intake-recommendation-and-handoff-boundary.md`, `docs/stories/story-197-establish-pptx-direct-entry-seam.md`, `docs/stories/story-200-web-page-direct-entry-seam.md`, `tests/fixtures/formats/_coverage-matrix.json`, `pyproject.toml`, `README.md`, `docs/RUNBOOK.md`, `benchmarks/scripts/intake_scope.py`, and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower EPUB-specific ADR or runbook
**Depends On**: None

## Goal

`epub` is now the smallest untested single-file format family with a callable parser in the current environment and reusable `doc-web` bundle substrate already in repo. The coverage matrix still marks it `untested`, there is no maintained direct-entry recipe or `input_epub` path, and the recommendation / handoff boundary helpers do not know how to classify it. This story should test the thinnest honest EPUB slice first: add one repo-owned reproducible EPUB fixture, measure a raw `partition_epub` baseline on it, and either land a bounded explicit-recipe direct-entry lane with fresh `driver.py` artifact proof or stop with a named blocker instead of leaving EPUB as an unowned format claim.

## Acceptance Criteria

- [x] A fresh current-pass baseline names the exact EPUB gap from repo evidence:
  - [x] `tests/fixtures/formats/_coverage-matrix.json` still marks `epub` as `untested`
  - [x] `schemas.py` / `driver.py` still expose no `input_epub` / `--input-epub`
  - [x] `pyproject.toml` still carries no maintained EPUB extra even though the current environment can import `unstructured.partition.epub`
  - [x] and the work log cites the verified absence of a maintained EPUB recipe/module pair in `configs/recipes/`, `modules/extract/`, and `modules/transform/`
- [x] If the bounded native seam reaches the accepted `doc-web` boundary, the repo lands one honest maintained EPUB direct-entry slice:
  - [x] one repo-owned EPUB fixture exists under `testdata/` with source metadata and any generation/capture note recorded in `testdata/README.md`
  - [x] a maintained direct-entry recipe completes through `driver.py` on that fixture
  - [x] and manual artifact inspection is recorded for the emitted `elements.jsonl`, bundle report, `output/html/manifest.json`, `output/html/provenance/blocks.jsonl`, and representative published HTML
- [x] EPUB provenance stays source-honest on the claimed slice:
  - [x] the story records the real anchor model exposed by the native parser and transform (for example spine/chapter grouping or element-id-only provenance)
  - [x] no fabricated printed-page guarantees or stronger citation claims are introduced
  - [x] and if new cross-artifact fields are needed, they are added to `schemas.py` before stamped outputs rely on them
- [x] Coverage, docs, and intake-boundary surfaces remain aligned with the outcome:
  - [x] `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, and `testdata/README.md` reflect the exact supported EPUB slice rather than a vague ebook promise
  - [x] if a maintained EPUB recipe lands, the direct-entry-only scope helpers and focused benchmark tests are updated so recommendation-only intake and approved handoff treat EPUB honestly
  - [x] and if the seam cannot honestly cross the accepted boundary on the chosen fixture, the story does not close `Done`; it converts to `Blocked` with explicit blocker evidence and an unblock condition

## Out of Scope

- Broad ebook support beyond the first bounded EPUB probe slice, including MOBI, AZW, or generic ebook-library ingestion
- Recommendation-only intake or approved-handoff automation expansion beyond explicit direct-entry scope reporting
- EPUB OCR fallback for image-only book pages or any scanned-epub recovery path before the native seam is measured honestly
- Claiming support for advanced embedded media, scripting, annotations, or every EPUB navigation/layout feature from one passing probe
- Reopening ADR-002 or changing the accepted `doc-web` runtime boundary

## Approach Evaluation

- **Simplification baseline**: first test whether a single native `partition_epub` call on one repo-owned fixture plus a thin deterministic transform is already enough to reach the accepted `doc-web` boundary. That is the cheapest honest path and should be measured before any new cleanup logic or AI repair.
- **AI-only**: low-value default. A one-shot model pass could emit HTML, but it would throw away the native EPUB structure and provenance signals before the repo has even measured whether the parser already gives enough.
- **Hybrid**: plausible if raw EPUB elements are structurally close but still need bounded title/chapter normalization or grouping logic. In that case, keep native parsing and provenance as the backbone and use code only for grouping and bundle shaping.
- **Pure code**: likely strongest for the first slice. The main work is fixture generation/capture, direct-entry plumbing, a maintained intake module, a bundle transform, and focused scope/docs/test updates.
- **Repo constraints / prior decisions**: `spec:1.1` keeps recipe ownership explicit, `C2` and `C3` are both in `climb`, Story 194 keeps recommendation-only intake and approved handoff explicitly narrower than the direct-entry lanes, and ADR-002 says new families should land through the accepted `doc-web` bundle/provenance boundary rather than parallel output contracts.
- **Existing patterns to reuse**: `modules/extract/unstructured_docx_intake_v1/main.py`, `modules/extract/unstructured_pptx_intake_v1/main.py`, `modules/transform/docx_elements_to_bundle_v1/main.py`, `modules/transform/pptx_elements_to_bundle_v1/main.py`, `modules/common/office_native_bundle.py`, `tests/test_doc_web_cli_contract.py`, `tests/test_pptx_intake_recipe.py`, `tests/test_web_page_intake_recipe.py`, `modules/intake/intake_plan_utils.py`, and `benchmarks/scripts/intake_scope.py`
- **Eval**: the deciding proof surface is a fresh `driver.py` run on one repo-owned EPUB fixture plus manual inspection of the emitted bundle/provenance artifacts. If a maintained direct-entry recipe lands, focused scope tests should also prove EPUB is represented honestly as direct-entry-only outside recommendation-only intake and approved handoff.

## Tasks

- [x] Freeze the current EPUB seam from repo reality before changing code:
  - [x] verify the `epub` coverage row is still `untested`
  - [x] verify `schemas.py` / `driver.py` still have no `input_epub` / `--input-epub`
  - [x] verify `pyproject.toml` still has no maintained EPUB extra
  - [x] verify there is still no maintained EPUB recipe/module pair or checked-in EPUB fixture
- [x] Add one repo-owned reproducible EPUB fixture:
  - [x] check in one bounded EPUB plus source metadata under `testdata/`
  - [x] record how the fixture was generated or captured in `testdata/README.md`
  - [x] and keep future tests/reruns independent of live network access
- [x] Measure the smallest honest native baseline before adding cleanup logic:
  - [x] run a raw `partition_epub` probe on the checked-in fixture and inspect the emitted element metadata
  - [x] verify the maintained EPUB dependency/install path actually makes `partition_epub` runnable in repo reality instead of only importable
  - [x] determine whether the existing bundle helper can already support the claimed slice or whether a thin EPUB-specific grouping transform is required
  - [x] record the exact artifact paths and failure modes inspected for that before-state
- [x] If the bounded direct-entry seam is viable, land the smallest coherent EPUB lane:
  - [x] add a maintained EPUB dependency/install path (`unstructured[epub]` plus the exact `pandoc` precondition the runtime actually needs)
  - [x] add `input_epub` support in `schemas.py` / `driver.py`
  - [x] add `configs/recipes/recipe-epub-html-mvp.yaml`
  - [x] add an EPUB intake module and the smallest honest bundle/provenance transform, reusing existing helpers where possible
  - [x] ensure the EPUB transform does not reuse DOCX title-splitting logic in a way that drops the first chapter on chapter-first fixtures
- [x] Add focused fixture-backed coverage for the new seam:
  - [x] a direct-entry smoke test that runs `driver.py` on the checked-in EPUB fixture and asserts bundle/provenance outputs
  - [x] and, if a maintained EPUB extra lands, an isolated install-contract smoke similar to the existing DOCX/PPTX tests plus any `requirements.txt` / run-config truth checks needed to keep the documented install surface honest
- [x] Run real `driver.py` verification and artifact inspection if the lane lands:
  - [x] clear stale `*.pyc`
  - [x] run the maintained recipe through `driver.py`
  - [x] verify artifacts exist in `output/runs/`
  - [x] and manually inspect sample JSON/JSONL and published HTML data
- [x] If EPUB direct-entry support changes documented reality:
  - [x] update `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, and `testdata/README.md`
  - [x] update `benchmarks/scripts/intake_scope.py`, `tests/test_auto_book_type_detection_benchmark.py`, `tests/test_approved_intake_handoff_benchmark.py`, and any direct-entry helper/tests that need EPUB to report as `direct_explicit_recipe_only`
  - [x] update `modules/intake/intake_plan_utils.py` and `tests/test_intake_plan_utils.py` only if a maintained EPUB recipe should change direct-entry boundary reasons there too
- [x] If the seam cannot honestly cross the accepted boundary on the chosen fixture, convert the story to `Blocked` with named blocker evidence instead of widening scope casually (not needed on this fixture because the seam crossed the accepted boundary with fresh driver proof)
- [x] If this story changes documented format coverage or graduation reality: update `tests/fixtures/formats/_coverage-matrix.json` and any relevant methodology state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; no redundant helper paths or docs were introduced by this bounded lane
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [x] If agent tooling changed: `make skills-check` (not applicable; no agent tooling changed in this story)
- [x] If evals or goldens changed: run `/improve-eval` and update `docs/evals/registry.yaml` (not applicable; no eval or golden files changed in this story)
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every support claim names the fixture, source metadata, run ID, and inspected artifact paths
  - [x] T1 — AI-First: do not add AI where the native EPUB seam and current `doc-web` runtime pattern are sufficient
  - [x] T2 — Eval Before Build: measure the raw native parser and direct-entry baseline before adding new EPUB logic
  - [x] T3 — Fidelity: EPUB structure and text survive extraction without silent omissions or fabricated page guarantees
  - [x] T4 — Modular: extend the existing explicit-recipe and bundle pattern instead of inventing a parallel EPUB runtime
  - [x] T5 — Inspect Artifacts: manually inspect EPUB outputs, not just import success or test logs

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

- **Owning module / area**: direct EPUB-native intake plus the accepted `doc-web` bundle/provenance boundary for pageless structured sources. Primary ownership should mirror the current DOCX/PPTX direct-entry seams rather than the recommendation-only intake automation.
- **Methodology reality**: this belongs to `spec:1`, `spec:3`, `spec:6`, `spec:7`, `spec:8`, and `spec:9`. In `docs/methodology/state.yaml`, `spec:1`, `spec:3`, `spec:6`, `spec:8`, and `spec:9` substrates exist, `spec:7` is still `partial`, and the relevant phases are `C2 = climb`, `C3 = climb`, `B10 = climb`, and `B1 = hold`. The relevant coverage row started this pass as `untested` and is now aligned to one bounded `passing` EPUB direct-entry slice backed by `testdata/epub-mini.epub`.
- **Substrate evidence**: the repo now owns the missing direct-entry seam: `pyproject.toml` exposes an `epub` extra pinned to `unstructured[epub]==0.16.9`, `requirements.txt` claims EPUB on the same maintained pin line, `schemas.py` / `driver.py` expose `input_epub` / `--input-epub`, the repo owns `testdata/epub-mini.md` / `epub-mini.source.json` / `generate_epub_fixture.py` / `epub-mini.epub`, `configs/recipes/recipe-epub-html-mvp.yaml` drives the bounded slice, `modules/extract/unstructured_epub_intake_v1/main.py` partitions EPUB through Unstructured with explicit `pandoc` preconditions, and `modules/transform/epub_elements_to_bundle_v1/main.py` groups every top-level EPUB title as content while keeping provenance pageless via `source_element_ids`. The baseline gap and the earlier missing-`pypandoc` / missing-recipe state are preserved in the work log below.
- **Data contracts / schemas**: likely touched contracts are `RunConfig` in `schemas.py`, `unstructured_element_v1`, `doc_web_bundle_manifest_v1`, and `doc_web_provenance_block_v1`. If EPUB grouping needs new cross-artifact provenance fields, they must be added to `schemas.py` before stamped outputs rely on them.
- **File sizes**: likely touch points are `pyproject.toml` (45 lines), `requirements.txt` (10), `schemas.py` (1239), `driver.py` (2298), `modules/extract/unstructured_docx_intake_v1/main.py` (215), `modules/extract/unstructured_pptx_intake_v1/main.py` (228), `modules/transform/docx_elements_to_bundle_v1/main.py` (170), `modules/transform/pptx_elements_to_bundle_v1/main.py` (181), `modules/common/office_native_bundle.py` (375), `modules/intake/intake_plan_utils.py` (309), `benchmarks/scripts/intake_scope.py` (47), `benchmarks/scripts/run_auto_book_type_detection_eval.py` (221), `benchmarks/scripts/run_approved_intake_handoff_eval.py` (341), `tests/test_doc_web_cli_contract.py` (416), `tests/test_run_config.py` (51), `tests/fixtures/formats/_coverage-matrix.json` (501), `README.md` (348), `docs/RUNBOOK.md` (570), and `testdata/README.md` (111). Oversized files to keep especially surgical are `schemas.py`, `driver.py`, `tests/fixtures/formats/_coverage-matrix.json`, and `docs/RUNBOOK.md`.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, Stories 172/194/197/200, `tests/fixtures/formats/_coverage-matrix.json`, `pyproject.toml`, `schemas.py`, `driver.py`, `modules/intake/intake_plan_utils.py`, `benchmarks/scripts/intake_scope.py`, `README.md`, and `docs/RUNBOOK.md`. No narrower EPUB-specific ADR, runbook, scout, or note was found after search.

## Files to Modify

- `pyproject.toml` — add a maintained EPUB optional dependency path only if the native seam requires one beyond the current environment (45 lines)
- `requirements.txt` — keep the documented repo install truth aligned if EPUB becomes a maintained supported lane (10 lines)
- `schemas.py` — add `input_epub` to `RunConfig` if a maintained direct-entry EPUB lane lands (1239 lines)
- `driver.py` — add `--input-epub` plumbing and recipe input override handling if the lane becomes maintained (2298 lines)
- `configs/recipes/recipe-epub-html-mvp.yaml` — maintained bounded EPUB direct-entry recipe reusing the accepted `doc-web` bundle/provenance boundary (new file)
- `modules/extract/unstructured_epub_intake_v1/main.py` and `modules/extract/unstructured_epub_intake_v1/module.yaml` — EPUB-native intake module patterned after the existing Unstructured direct-entry seams (new files)
- `modules/transform/epub_elements_to_bundle_v1/main.py` and `modules/transform/epub_elements_to_bundle_v1/module.yaml` — EPUB bundle/provenance transform or the smallest honest generalization of the existing helper pattern (new files)
- `modules/common/office_native_bundle.py` — extend only if the current helper is honestly the shared home for EPUB bundle rendering/provenance (375 lines)
- `tests/test_doc_web_cli_contract.py` — add isolated install/smoke coverage only if a maintained EPUB extra lands (416 lines)
- `tests/test_run_config.py` — add `input_epub` config coverage if the RunConfig surface grows (51 lines)
- `tests/test_epub_intake_recipe.py` — focused EPUB direct-entry smoke coverage on the checked-in fixture (new file)
- `modules/intake/intake_plan_utils.py` — add EPUB to the direct-entry-only boundary table only if a maintained EPUB recipe lands and the confirmed-handoff helper should classify it explicitly (309 lines)
- `benchmarks/scripts/intake_scope.py` — extend direct-entry-only scope handling if EPUB joins that boundary class (47 lines)
- `tests/test_auto_book_type_detection_benchmark.py` — keep recommendation-only boundary truth aligned if EPUB becomes explicit direct-entry-only scope (64 lines today in current repo usage)
- `tests/test_approved_intake_handoff_benchmark.py` — keep approved-handoff boundary truth aligned if EPUB becomes explicit direct-entry-only scope (157 lines today in current repo usage)
- `testdata/epub-mini.epub` / `testdata/epub-mini.md` / `testdata/epub-mini.source.json` / `testdata/generate_epub_fixture.py` — repo-owned bounded EPUB fixture and provenance metadata for the first maintained slice (new files)
- `testdata/README.md` — record fixture source, generation/capture note, and maintained scope (111 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — move the `epub` row only as far as fresh evidence justifies (501 lines)
- `README.md` — align user-facing format support wording with the actual EPUB seam (348 lines)
- `docs/RUNBOOK.md` — publish the verified bounded EPUB direct-entry command or the blocker if the seam cannot land (570 lines)

## Redundancy / Removal Targets

- Stale `epub` `untested` wording in coverage/docs once a maintained direct-entry slice exists
- Any ad hoc EPUB probe commands or notes that become redundant after a maintained recipe/test lane lands
- Any stale direct-entry boundary wording or helper omission that keeps EPUB outside the explicit-scope surfaces after support lands

## Notes

- New story justification: it would not be honest to reopen Story 197 or Story 200. Story 197 settled the first PPTX direct-entry seam, and Story 200 settled the first web-page HTML-snapshot seam. EPUB is a different file family with its own fixture, parser, grouping logic, and provenance model.
- The existing explicit-recipe operator surface is already the honest first slice here. Recommendation-only intake and approved handoff should change only enough to represent the direct-entry boundary truthfully if a maintained EPUB lane lands.
- Exploration surprise worth keeping explicit: `partition_epub(...)` is a `pandoc` conversion seam (`EPUB -> HTML -> partition_html`), not a bespoke structured parser. The maintained lane therefore needs honest install/runtime wording about `pypandoc` and `pandoc`, and the transform cannot just inherit DOCX title-splitting because a chapter-first probe causes `docx_elements_to_bundle_v1` to drop the first chapter entirely.
- If the raw native seam immediately exposes a larger chapter-grouping or provenance-contract question than this story can settle inside the current `doc-web` pattern, stop and record that blocker explicitly instead of widening scope by inertia.

## Plan

Alignment check:
- This story still moves toward `docs/ideal.md` rather than polishing a dead-end compromise: it widens explicit format coverage one bounded family at a time (`spec:1.1` / `C2`), keeps the `doc-web` bundle/provenance contract as the output bar (`spec:6` / `spec:7` and ADR-002), and preserves inspectable boundary truth for automation surfaces (`spec:8` / `spec:9`).
- No conflicting narrower ADR or runbook was found after the fresh decision-doc search in this pass.

Measured baseline from this `/build-story` exploration pass:
- **Current repo runtime baseline: 0/1 passing.** A live `partition_epub(...)` probe on a synthetic two-chapter EPUB fails immediately in the current repo environment because `pypandoc` is missing, even though `unstructured.partition.epub` imports.
- **Isolated substrate baseline: 1/1 passing.** In a clean temporary venv, `pip install 'unstructured[epub]==0.16.9'` plus the already-installed system `pandoc` successfully partitions the same probe EPUB into six pageless elements (`Title`, `NarrativeText`, `ListItem`) with `parent_id` and no `page_number`.
- **Existing transform reuse baseline: 0/1 passing.** Reusing `docx_elements_to_bundle_v1` unchanged on that raw EPUB element stream emits only one chapter entry and drops the first chapter entirely because the DOCX transform treats the first top-level title as document title rather than content.

Approach choice after the fresh baseline:
- **AI-only** remains the wrong first move. The hard facts are install/runtime truth and deterministic grouping, not semantic ambiguity.
- **Hybrid** is not needed yet. The native EPUB path already yields a clean enough bounded element stream on the probe once the dependency gap is repaired.
- **Pure code + native Unstructured partitioning** is the simplest honest first pass: own the missing EPUB dependency surface, add direct-entry plumbing, then add a thin EPUB-specific bundle transform that keeps pageless provenance explicit instead of fabricating pages.

Implementation order:

1. **Add a repo-owned reproducible EPUB fixture (`S`)**
   - Files: `testdata/epub-mini.md`, `testdata/epub-mini.source.json`, `testdata/generate_epub_fixture.py`, `testdata/epub-mini.epub`, `testdata/README.md`
   - Change: check in one tiny chapter-first EPUB fixture generated from repo-owned markdown via `pandoc`, plus source metadata describing its provenance and regeneration path.
   - Why first: the rest of the work should target one stable checked-in artifact, not a temporary probe.
   - Done looks like: the fixture is reproducible without network access and the story can cite the exact source/generator pair.

2. **Land maintained EPUB install truth (`S`)**
   - Files: `pyproject.toml`, `requirements.txt`, `tests/test_doc_web_cli_contract.py`
   - Change: add an `epub` extra using `unstructured[epub]==0.16.9`; decide whether `requirements.txt` should also claim EPUB once the lane is maintained; and add install-contract coverage that proves the repo-owned EPUB fixture can actually partition in a clean venv on the supported Python range.
   - Risk: the runtime depends on system `pandoc`, so docs and smoke coverage must make that precondition explicit rather than implying a Python-only install is sufficient.
   - Done looks like: the documented maintained install shape for EPUB is true in a fresh environment.

3. **Add direct-entry config and CLI support (`S`)**
   - Files: `schemas.py`, `driver.py`, `tests/test_run_config.py`
   - Change: add `input_epub` / `--input-epub` parallel to the existing DOCX/PPTX/HTML seams.
   - Risk: `driver.py` override logic is already crowded; keep the change surgical and symmetric with the existing direct-entry keys.
   - Done looks like: recipe runs and run-config YAML can both point at the checked-in EPUB fixture.

4. **Add the EPUB intake and bundle transform (`M`)**
   - Files: `modules/extract/unstructured_epub_intake_v1/*`, `modules/transform/epub_elements_to_bundle_v1/*`, optionally `modules/common/office_native_bundle.py`
   - Change: add a thin intake wrapper around `partition_epub(...)` + `serialize_element(...)`, then add an EPUB-specific transform that groups every top-level title as content, keeps provenance pageless via `source_element_ids`, and only includes `source_pages` if real page anchors exist (they likely will not on this first slice).
   - Risk: reusing the DOCX transform unchanged is already disproven by the baseline because it drops the first chapter; the EPUB transform must not repeat that bug.
   - Done looks like: the synthetic two-chapter baseline and the checked-in fixture both preserve the first chapter and emit a coherent bundle without fabricated printed-page claims.

5. **Add maintained recipe and focused smoke coverage (`S`)**
   - Files: `configs/recipes/recipe-epub-html-mvp.yaml`, `tests/test_epub_intake_recipe.py`
   - Change: add a direct-entry recipe and a focused driver smoke test that asserts emitted `elements.jsonl`, bundle report, manifest, provenance blocks, and representative chapter HTML on the repo-owned fixture.
   - Done looks like: one test can fail immediately if EPUB wiring, grouping, or provenance regresses.

6. **Align direct-entry boundary helpers and docs (`S`)**
   - Files: `modules/intake/intake_plan_utils.py`, `tests/test_intake_plan_utils.py`, `benchmarks/scripts/intake_scope.py`, `tests/test_auto_book_type_detection_benchmark.py`, `tests/test_approved_intake_handoff_benchmark.py`, `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, `testdata/README.md`, optionally `docs/evals/registry.yaml`
   - Change: if the maintained EPUB recipe lands, classify EPUB as `direct_explicit_recipe_only` outside recommendation-only intake and approved handoff, update the coverage row only as far as the fresh fixture-backed proof justifies, and document the exact install/runtime preconditions.
   - Done looks like: coverage, runbook, README, testdata notes, and automation-boundary tests all describe the same bounded EPUB outcome.

7. **Run real pipeline proof and inspect artifacts (`M`)**
   - Files: no new implementation files expected; this is the required proof pass
   - Change: clear stale `*.pyc`, run `driver.py` on the checked-in fixture, inspect `01_unstructured_epub_intake_v1/elements.jsonl`, the EPUB bundle report, `output/html/manifest.json`, `output/html/provenance/blocks.jsonl`, and representative chapter HTML, then record exact paths and sampled content in the work log.
   - Stop condition: if the real run cannot preserve first-chapter content or the provenance story is weaker than the claimed bounded slice, convert the story to `Blocked` instead of widening scope casually.

Expected coverage movement if the lane lands:
- `epub` can move from `untested` to a bounded maintained direct-entry slice backed by one repo-owned fixture.
- Recommendation-only intake and approved handoff should remain narrow; EPUB should join the explicit `direct_explicit_recipe_only` boundary class rather than widen those automation surfaces.

Small coherent scope delta absorbed during exploration:
- Add `requirements.txt`, `tests/test_run_config.py`, and fixture-generation files to keep the install/config truth honest.
- Record the `pandoc` precondition explicitly because the native Unstructured EPUB seam depends on it in repo reality.

Human-approval blockers before implementation:
- New maintained dependency surface: `.[driver,epub]` and possibly widening `requirements.txt`
- New explicit CLI / config surface: `input_epub` / `--input-epub`
- Maintained runtime precondition: the first EPUB lane will depend on system `pandoc` unless a bundled alternative is chosen

## Work Log

20260408-2315 — create-story: created Story 201 after `/triage` found no actionable `In Progress`, `Pending`, or `Draft` line beyond blocked Story 191 and the user approved opening the next honest format seam. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, Stories 172/194/197/200, `tests/fixtures/formats/_coverage-matrix.json`, `pyproject.toml`, `schemas.py`, `driver.py`, `modules/extract/unstructured_docx_intake_v1/main.py`, `modules/extract/unstructured_pptx_intake_v1/main.py`, `modules/transform/docx_elements_to_bundle_v1/main.py`, `modules/transform/pptx_elements_to_bundle_v1/main.py`, `modules/common/office_native_bundle.py`, `modules/intake/intake_plan_utils.py`, `benchmarks/scripts/intake_scope.py`, `README.md`, and `docs/RUNBOOK.md`. Fresh substrate evidence: the `epub` coverage row is still `untested`; the repo has no `input_epub`, no maintained EPUB recipe/module pair, and no checked-in EPUB fixture; `pyproject.toml` has no EPUB extra; but the current environment can import `unstructured.partition.epub`, and the repo already has reusable direct-entry and bundle/provenance patterns from DOCX, PPTX, and HTML-snapshot lanes. Result: a new `Pending` story is honest because the missing work is a bounded direct-entry seam with buildable substrate, not a blocked research question. Next step: `/build-story` should freeze the fixture plan, run the raw EPUB parser baseline, and decide the smallest honest maintained lane or blocker.
20260408-2322 — methodology compile: ran `make methodology-compile` after writing Story 201, which regenerated `docs/methodology/graph.json` and `docs/stories.md`. Verification in this pass: `docs/stories.md` now lists Story 201 as `Pending`, and `docs/methodology/graph.json` now includes the new story node at `docs/stories/story-201-epub-direct-entry-seam.md`. Impact: the story is now visible to graph-driven triage and backlog tooling instead of existing only as a standalone markdown file.
20260408-2357 — build-story explore/plan: re-read the governing context for this story in the current pass: `docs/ideal.md`; `docs/spec.md` (`spec:1`, `spec:1.1`, `spec:3`, `spec:3.1`, `spec:6`, `spec:7`, `spec:8`, `spec:9`); `docs/methodology/state.yaml`; `docs/methodology/graph.json`; ADR-002; Stories 194, 197, and 200; `tests/fixtures/formats/_coverage-matrix.json`; `pyproject.toml`; `requirements.txt`; `schemas.py`; `driver.py`; `modules/extract/unstructured_docx_intake_v1/main.py`; `modules/extract/unstructured_pptx_intake_v1/main.py`; `modules/transform/docx_elements_to_bundle_v1/main.py`; `modules/transform/pptx_elements_to_bundle_v1/main.py`; `modules/common/office_native_bundle.py`; `modules/intake/intake_plan_utils.py`; `benchmarks/scripts/intake_scope.py`; `tests/test_doc_web_cli_contract.py`; `tests/test_run_config.py`; `tests/test_pptx_intake_recipe.py`; `tests/test_web_page_intake_recipe.py`; `README.md`; `docs/RUNBOOK.md`; and `testdata/README.md`. Fresh baseline evidence: the `epub` coverage row is still `untested`; there is still no `input_epub` / `--input-epub`, no EPUB recipe/module pair, and no checked-in EPUB fixture; a live `partition_epub(...)` probe in the current repo environment fails immediately with `ImportError: Following dependencies are missing: pypandoc`; but an isolated clean venv with `unstructured[epub]==0.16.9` plus the already-installed system `pandoc` partitions a synthetic two-chapter probe EPUB successfully into six pageless `Title` / `NarrativeText` / `ListItem` elements. The crucial transform surprise is now verified too: reusing `docx_elements_to_bundle_v1` on that raw EPUB element stream emits only one chapter entry titled `Chapter Two` and drops the first chapter because the DOCX transform treats the first top-level title as document title instead of content. Result: Story 201 remains honestly buildable, but only as a thin EPUB-specific direct-entry lane with explicit install truth (`unstructured[epub]` + `pandoc`), a repo-owned generated fixture, and a dedicated EPUB grouping transform rather than blind DOCX-transform reuse. Small coherent scope delta absorbed into the plan: add `requirements.txt`, `tests/test_run_config.py`, and the EPUB fixture generator/source files so the documented install/config surface stays honest. Next step: wait for user approval before promoting the story to `In Progress` and touching implementation code.
20260409-0000 — implementation start: user approved the exploration plan, so Story 201 is now `In Progress`. Immediate next step: regenerate the compiled methodology surfaces so the generated backlog reflects the active implementation state, then land the repo-owned EPUB fixture and the missing runtime/install truth before touching the EPUB-specific transform.
20260409-0215 — implementation + docs alignment: landed the bounded maintained EPUB seam across the repo-owned fixture, runtime truth, recipe/module path, direct-entry boundary helpers, and public docs. Code/data added in this pass: `testdata/epub-mini.md`, `testdata/epub-mini.source.json`, `testdata/generate_epub_fixture.py`, and generated `testdata/epub-mini.epub`; `pyproject.toml` now exposes `epub = ["unstructured[epub]==0.16.9"]`; `requirements.txt` now claims `unstructured[docx,epub,pdf,pptx,xlsx]==0.16.9`; `schemas.py` / `driver.py` now expose `input_epub` / `--input-epub`; `configs/recipes/recipe-epub-html-mvp.yaml` defines the maintained direct-entry lane; `modules/extract/unstructured_epub_intake_v1/*` partitions EPUB with explicit `pandoc` checks plus package-title/package-author metadata capture; `modules/transform/epub_elements_to_bundle_v1/*` groups every top-level title as content so chapter-first fixtures keep the first chapter; `modules/intake/intake_plan_utils.py`, `benchmarks/scripts/intake_scope.py`, `tests/test_intake_plan_utils.py`, `tests/test_auto_book_type_detection_benchmark.py`, and `tests/test_approved_intake_handoff_benchmark.py` now classify EPUB as `direct_explicit_recipe_only`; and `README.md`, `docs/RUNBOOK.md`, `testdata/README.md`, and `tests/fixtures/formats/_coverage-matrix.json` now describe the same bounded supported slice. Impact: Story 201 now has a real maintained lane instead of a planning placeholder, and the automation-boundary surfaces no longer misclassify EPUB as missing/unknown. Evidence: `python -m pytest tests/test_run_config.py tests/test_intake_plan_utils.py tests/test_auto_book_type_detection_benchmark.py tests/test_approved_intake_handoff_benchmark.py` passed (`39 passed`); `python -m pytest tests/test_epub_intake_recipe.py tests/test_doc_web_cli_contract.py -k 'epub'` passed on Python 3.11 (`4 passed, 8 deselected`) and `pytest tests/test_epub_intake_recipe.py tests/test_doc_web_cli_contract.py -k 'epub'` now degrades honestly on the machine's Python 3.14 entrypoint (`1 passed, 3 skipped, 8 deselected`) because the maintained `unstructured==0.16.9` pin is supported on Python 3.11/3.12 only; `make lint` passed; a broader `make test` sweep was started but intentionally stopped after the changed-scope proofs were already complete because the repo-wide suite re-runs many unrelated clean-venv contract lanes. Next step: run `/validate`, then `/mark-story-done` if the validation pass agrees with the bounded EPUB support claim.
20260409-0224 — real driver proof + manual artifact inspection: cleared stale `*.pyc` under `modules/extract/unstructured_epub_intake_v1` and `modules/transform/epub_elements_to_bundle_v1`, then ran `python driver.py --recipe configs/recipes/recipe-epub-html-mvp.yaml --input-epub testdata/epub-mini.epub --run-id story201-epub-mini --allow-run-id-reuse --force`. Fresh artifact proof from this pass: `output/runs/story201-epub-mini/01_unstructured_epub_intake_v1/elements.jsonl` contains six pageless EPUB-native elements (`Title`, `NarrativeText`, `ListItem`) with `epub_title = "EPUB Mini Fixture"` and `epub_creator = "doc-web"` in metadata; `output/runs/story201-epub-mini/02_epub_elements_to_bundle_v1/epub_bundle_report.json` reports `entry_count = 2`, `provenance_row_count = 6`, and `reading_order = ["chapter-001", "chapter-002"]`; `output/runs/story201-epub-mini/output/html/manifest.json` records document title `EPUB Mini Fixture`, creator `doc-web`, two chapter entries, and empty `source_pages` arrays; `output/runs/story201-epub-mini/output/html/provenance/blocks.jsonl` contains six rows with `source_element_ids` populated and no `source_page_number`; `output/runs/story201-epub-mini/output/html/chapter-001.html` preserves the first chapter heading, the bounded prose paragraph, and both list items (`Ada keeps the research log.` / `Lin checks the archive notes.`); and `output/runs/story201-epub-mini/output/html/chapter-002.html` preserves the second chapter heading and paragraph. Impact: the bounded maintained EPUB claim is now backed by fresh driver execution plus manual artifact inspection, not just module tests or import success. Remaining gap: `/validate` still needs to review the final diff and decide whether the partial `make test` stop is acceptable for close-out versus requiring a full-suite rerun.
20260409-1454 — validation follow-through: tightened the EPUB support claim to the verified slice by removing the stray `illustrations` complexity tag from `tests/fixtures/formats/_coverage-matrix.json`, updated `docs/methodology/state.yaml` to mark the coverage matrix freshly reviewed on 2026-04-09, and completed the outstanding story housekeeping that was still part of implementation truth rather than close-out. I also confirmed there was no narrower EPUB-specific ADR/runbook after a fresh repo search, found no redundant helper path introduced by this lane, and the seam remained above the accepted `doc-web` boundary so blocker conversion was not needed. Fresh evidence from this pass: `python -m pytest tests/test_run_config.py tests/test_intake_plan_utils.py tests/test_auto_book_type_detection_benchmark.py tests/test_approved_intake_handoff_benchmark.py` passed (`39 passed`); `python -m pytest tests/test_epub_intake_recipe.py tests/test_doc_web_cli_contract.py -k 'epub'` passed (`4 passed, 8 deselected`); the checked-in `testdata/epub-mini.epub` archive contains the expected generated chapter files; and the existing `story201-epub-mini` run still shows two chapter entries, six provenance rows, pageless `source_element_ids`, and preserved first-chapter/list content in the final HTML bundle. Next step: rerun `make methodology-compile`, then finish the remaining `make test` gate so the story can move to `/mark-story-done`.
20260409-1515 — full-suite proof and generated-view refresh: ran `make test` successfully (`505 passed, 4 warnings in 587.02s`) and then reran `make methodology-compile` so the generated backlog/graph surfaces reflect the corrected EPUB coverage row. The only warnings in the full suite were existing `PydanticDeprecatedSince20` warnings from `modules/portionize/portionize_headers_numeric_v1/main.py`, unrelated to this story's EPUB seam. Fresh generated-surface verification after the compile: `docs/stories.md` still lists Story 201 under `spec:1`, `docs/methodology/state.yaml` now records the coverage matrix as reviewed on `2026-04-09`, and the compiled EPUB coverage node in `docs/methodology/graph.json` now matches the bounded `simple-prose` claim rather than carrying the earlier stray `illustrations` tag. Impact: the remaining implementation-validation gap from `/validate` is now closed, so only `/mark-story-done` bookkeeping remains before the story can leave `In Progress`.
20260409-1523 — mark-story-done: closed Story 201 after fresh close-out validation on the current tip. Completion evidence for this close-out pass: `make test` passed (`505 passed, 4 unrelated warnings`), `python -m ruff check modules/ tests/` passed (`All checks passed!`), the maintained EPUB focused checks stayed green (`39 passed` across run-config/intake-boundary tests and `4 passed, 8 deselected` across EPUB recipe/install-contract tests), and the checked `story201-epub-mini` driver proof still shows the bounded supported slice in the final bundle/provenance artifacts. Generated surfaces were refreshed after the status flip so `docs/stories.md` and `docs/methodology/graph.json` now reflect `Done`. Recommended next step: `/check-in-diff`.
