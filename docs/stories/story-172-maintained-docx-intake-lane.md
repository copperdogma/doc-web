---
title: Establish a Maintained DOCX Intake Lane
status: Done
priority: High
ideal_refs:
- 'Requirement #1 (Ingest), Requirement #5 (Structure), Requirement #6 (Validate),
  Requirement #7 (Export), Any format, any condition, Dossier-ready output, Traceability
  is the product'
spec_refs:
- spec:1
- spec:1.1
- spec:6
- spec:7
- spec:8
adr_refs: []
depends_on:
- '153'
- '154'
- '167'
- '169'
category_refs:
- spec:1
- spec:6
- spec:7
- spec:8
compromise_refs:
- B1
- C2
input_coverage_refs:
- docx
architecture_domains: []
roadmap_tags: []
legacy_system: ''
---

# Story 172 — Establish a Maintained DOCX Intake Lane

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #1 (Ingest), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Any format, any condition, Dossier-ready output, Traceability is the product
**Spec Refs**: spec:1 (spec:1.1, C2), spec:6, spec:7, spec:8 (B1)
**Build Map Refs**: Category 1 Intake & Format Routing (`exists`, C2 `climb`); Category 6 Validation, Provenance & Export (`exists`); Category 7 Graduation & Dossier Handoff (`partial`); Input Coverage row `docx` (`has fixture`); Gap 3 — Office document intake beyond the first DOCX slice
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/scout/scout-011-external-document-ingestion-systems.md`, `docs/build-map.md`, `docs/requirements.md`, `None found after search in docs/decisions/ for DOCX-specific ADRs`
**Depends On**: Story 153, Story 154, Story 167, Story 169

## Goal

Create the first honest maintained DOCX lane for `doc-web`: a repo-owned DOCX proof surface, a measured comparison of the real local extraction seams, and an explicit recipe that produces a final bundle plus block-level provenance without inventing fake page numbers. The story should move `docx` off the `untested` row only as far as the fresh artifact evidence justifies.

## Acceptance Criteria

- [x] A repo-owned or reproducibly generated DOCX fixture exists under `testdata/` and is explicit about the supported slice:
  - the fixture includes enough structure to test the chosen lane honestly (at minimum headings plus prose; simple lists/tables if the story wants to claim them)
  - the fixture source and generator are checked in so the lane does not depend on private local office files
- [x] The story measures the real local DOCX substrates before committing to one implementation path:
  - baseline artifact evidence is recorded for the available seams in this checkout (`unstructured.partition.docx`, `pandoc`, and any direct `python-docx` fallback the story chooses to test)
  - the work log names the observed failure modes and why the winning path is the smallest honest one
- [x] A maintained explicit DOCX recipe runs through `driver.py` on the supported slice and leaves inspectable final artifacts under `output/runs/`:
  - it produces an accepted final bundle (`output/html/manifest.json` or equivalent accepted `doc-web` surface)
  - it emits block-level provenance that references DOCX-native source structure (for example source element ids, block ordinals, or paragraph anchors) instead of fabricated printed-page metadata
  - manual artifact inspection is recorded for representative extraction, bundle, and provenance artifacts
- [x] The maintained lane is runnable without recipe-file edits for each document:
  - either a generic DOCX input override lands in `driver.py` / `RunConfig`, or the story documents and proves the maintained override/config path it uses
  - the path remains explicit-recipe and recommendation-only; it does not add hidden auto-dispatch
- [x] Support truth surfaces stay honest:
  - `tests/fixtures/formats/_coverage-matrix.json`, `docs/build-map.md`, and any affected runbook/testdata docs reflect the exact supported DOCX slice
  - the `docx` row moves from `untested` only as far as the evidence earns (`has fixture` by default; `passing` only if the story proves and inspects the claimed slice end-to-end)

## Out of Scope

- General office-suite support for `xlsx` or `pptx`
- Hidden DOCX auto-routing or planner/dispatch behavior beyond the current explicit-recipe compromise
- DOCX-to-PDF conversion as the maintained default if it weakens DOCX-native provenance or silently changes the product claim
- Full fidelity for tracked changes, comments, text boxes, SmartArt, embedded charts, or other advanced Word features unless the chosen substrate preserves them naturally and the story explicitly widens scope
- Solving every office-document provenance question for future `xlsx` / `pptx` lanes in one pass

## Approach Evaluation

- **Simplification baseline**: first test the local deterministic seams that already exist in this checkout. DOCX is structured XML, so the first question is not "can a model read it?" but "does `unstructured.partition.docx`, `pandoc`, or a minimal `python-docx` path already yield acceptable structure plus provenance with no new AI logic?"
- **AI-only**: possible fallback if deterministic conversion loses meaningful structure, but it should start from a deterministic DOCX extract rather than from rasterized screenshots. A model-only lane is expensive, weak on stable provenance, and likely unnecessary for the first DOCX slice.
- **Hybrid**: likely best if deterministic extraction gets most of the way there. Use DOCX-native parsing for headings/tables/list/item provenance, then reserve AI for bounded repair only if the inspected baseline shows a specific structure class that deterministic tools flatten.
- **Pure code**: plausible for the initial slice because Word already carries heading, paragraph, list, and table semantics. If the local deterministic tools preserve enough of that structure, code-first may be the honest minimal path here.
- **Repo constraints / prior decisions**: ADR-002 fixes the output boundary at `doc-web` bundle + block-level provenance. Story 169 keeps intake recommendation-only and rejects hidden dispatch. Build Map Gap 3 says there is no office pipeline family yet. Scout 011 notes that external systems like Marker claim DOCX support, but their licensing/runtime burden is materially heavier than the locally verified seams in this checkout.
- **Existing patterns to reuse**: `modules/intake/unstructured_pdf_intake_v1`, `modules/render/render_html_from_elements_v1`, `modules/normalize/reduce_ir_v1`, `modules/build/build_chapter_html_v1`, `tests/test_doc_web_bundle_contract.py`, `tests/test_pdf_intake_recipe.py`, Story 167's repo-owned fixture/proof pattern, and Story 169's maintained-lane truth-surface discipline.
- **Eval**: the deciding proof is a repo-owned DOCX fixture run through the candidate lanes, scored by artifact inspection and the smallest repeatable checks that distinguish them:
  - heading fidelity
  - list/table preservation for the claimed slice
  - final bundle validity
  - provenance honesty (no fake page numbers, stable source anchors)
  No DOCX-specific eval exists today, so this story should add only the smallest honest proof surface needed.

## Tasks

- [x] Freeze the supported DOCX proof surface:
  - [x] add a repo-owned DOCX fixture plus checked-in source/generator under `testdata/`
  - [x] choose and document the exact supported slice for Story 172 (for example headings + prose only, or headings + prose + simple tables/lists)
- [x] Measure the local DOCX baselines before implementing a maintained lane:
  - [x] run and inspect `unstructured.partition.docx`
  - [x] run and inspect `pandoc`
  - [x] inspect whether a minimal `python-docx` path is useful as a low-complexity control or fallback
  - [x] record the exact artifact-level failure modes before choosing the winner
- [x] Land the smallest maintained explicit DOCX lane the evidence supports:
  - [x] add `configs/recipes/recipe-docx-html-mvp.yaml` (or equivalent explicit maintained recipe)
  - [x] add a DOCX-native intake/extract seam, either as a new module or a shared helper extracted from `unstructured_pdf_intake_v1`
  - [x] add `driver.py` / `RunConfig` DOCX input override support if the maintained recipe otherwise requires per-run recipe edits
  - [x] evolve the `doc-web` contract/tests if the winning path needs pageless-source provenance rules
  - [x] keep final provenance honest; do not backfill printed-page fields for a pageless source unless the source truly provides them
- [x] Add repeatable proof and contract coverage:
  - [x] add focused tests for recipe wiring and maintained DOCX proof behavior
  - [x] extend bundle/provenance contract tests if DOCX-native anchors require new accepted fields or new edge-case assertions
  - [x] run a real `driver.py` proof and manually inspect output artifacts in `output/runs/`
- [x] Update truth surfaces only as far as the evidence justifies:
  - [x] `tests/fixtures/formats/_coverage-matrix.json`
  - [x] `docs/build-map.md`
  - [x] any affected testdata/runbook docs for the new fixture and proof command
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [x] If agent tooling changed: `make skills-check` (not needed; no agent tooling changed)
- [x] If evals or goldens changed: run `/improve-eval` and update `docs/evals/registry.yaml` (not needed; no eval or golden pack changed)
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every output traces to source block, extraction seam, and processing step
  - [x] T1 — AI-First: test whether AI adds real value after the deterministic DOCX baselines, not before
  - [x] T2 — Eval Before Build: measure the available seams before deepening the code path
  - [x] T3 — Fidelity: preserve DOCX structure without silent flattening or fake pagination
  - [x] T4 — Modular: add a recipe/lane, not a tangled office-specific side system
  - [x] T5 — Inspect Artifacts: review real bundle/provenance artifacts, not just conversion logs

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: Category 1 input normalization plus the `doc-web` bundle/provenance surfaces in Categories 6 and 7. The likely owners are a DOCX-native intake/extract seam, existing element-to-HTML rendering, and the final bundle contract tests.
- **Build-map reality**: Category 1 already exists and is in `climb`; the direct gap is the `docx` input-coverage row plus Gap 3 for office documents. Category 7 remains `partial`, so any new lane must preserve the accepted `doc-web` boundary rather than create an office-only side output.
- **Substrate evidence**: verified in this session that `unstructured.partition.docx` imports successfully, `python-docx` imports successfully, and `pandoc` is on `PATH`. Existing reusable seams are real in code: `modules/intake/unstructured_pdf_intake_v1` already emits `unstructured_element_v1`, `modules/render/render_html_from_elements_v1` can turn those elements into HTML, `modules/normalize/reduce_ir_v1` already reduces `unstructured_element_v1`, and `build_chapter_html_v1` plus bundle contract tests already enforce the accepted final output surface. Missing or partial substrate is also real: `driver.py` and `RunConfig` only expose `input_pdf` overrides today, `docling` is not importable in this checkout, and no DOCX-specific recipe/module/test surface exists yet.
- **Measured baseline surprises**: the existing PDF-oriented reuse path is not DOCX-safe as-is. On a fresh temporary DOCX fixture, `unstructured.partition.docx` preserved titles, list items, tables, stable hashed element ids, and `parent_id`, but it emitted no `page_number`. Reusing `serialize_element()` from `unstructured_pdf_intake_v1` converted every DOCX element to `type="Unknown"` because it reads `element.type` rather than the DOCX seam's `category`, and the downstream probes then flattened headings/lists/tables while synthesizing `Page 1` wrappers. `reduce_ir_v1` also defaults missing `page_number` to `1`, which would fabricate pageless provenance if reused unchanged.
- **Data contracts / schemas**: likely touched contracts are `unstructured_element_v1`, `doc_web_bundle_manifest_v1`, `doc_web_provenance_block_v1`, and `RunConfig` if a new DOCX override field lands. If the chosen implementation introduces DOCX-native provenance anchors that cross artifact boundaries, they must be added to `schemas.py` before relying on them.
- **File sizes**: likely large-file touch points are [driver.py](/Users/cam/.codex/worktrees/1f1d/doc-web/driver.py) at 2198 lines, [schemas.py](/Users/cam/.codex/worktrees/1f1d/doc-web/schemas.py) at 1215 lines, [build_chapter_html_v1/main.py](/Users/cam/.codex/worktrees/1f1d/doc-web/modules/build/build_chapter_html_v1/main.py) at 1686 lines, [test_build_chapter_html.py](/Users/cam/.codex/worktrees/1f1d/doc-web/tests/test_build_chapter_html.py) at 1544 lines, and [build-map.md](/Users/cam/.codex/worktrees/1f1d/doc-web/docs/build-map.md) at 584 lines. Prefer narrow helpers and new focused tests over inflating those files casually. Medium-size likely touch points are [unstructured_pdf_intake_v1/main.py](/Users/cam/.codex/worktrees/1f1d/doc-web/modules/intake/unstructured_pdf_intake_v1/main.py) at 344 lines, [render_html_from_elements_v1/main.py](/Users/cam/.codex/worktrees/1f1d/doc-web/modules/render/render_html_from_elements_v1/main.py) at 425 lines, [reduce_ir_v1/main.py](/Users/cam/.codex/worktrees/1f1d/doc-web/modules/normalize/reduce_ir_v1/main.py) at 240 lines, [test_doc_web_bundle_contract.py](/Users/cam/.codex/worktrees/1f1d/doc-web/tests/test_doc_web_bundle_contract.py) at 294 lines, and [tests/fixtures/formats/_coverage-matrix.json](/Users/cam/.codex/worktrees/1f1d/doc-web/tests/fixtures/formats/_coverage-matrix.json) at 348 lines.
- **Decision context**: reviewed `docs/ideal.md`, `docs/build-map.md`, `docs/requirements.md`, ADR-002, Scout 011, Story 167, Story 169, and Story 171; searched `docs/decisions/` and found no DOCX-specific ADR. A new ADR is only needed if the implementation discovers that pageless office provenance cannot fit the accepted bundle contract without a broader contract change.

## Files to Modify

- `configs/recipes/recipe-docx-html-mvp.yaml` — new maintained explicit DOCX recipe (new file)
- `modules/extract/unstructured_docx_intake_v1/main.py` — new DOCX-native intake/extract path, or a thin wrapper over shared unstructured helpers (new file)
- `modules/extract/unstructured_docx_intake_v1/module.yaml` — module contract for the new DOCX lane (new file)
- `modules/transform/docx_elements_to_bundle_v1/main.py` — emits the accepted bundle plus DOCX-native provenance directly from DOCX elements without forcing them through the page-oriented chapter builder (new file)
- `modules/transform/docx_elements_to_bundle_v1/module.yaml` — module contract for the DOCX bundle emitter (new file)
- `modules/intake/unstructured_pdf_intake_v1/main.py` — factor shared unstructured helper code only if it reduces drift between PDF and DOCX seams (344 lines)
- `modules/render/render_html_from_elements_v1/main.py` — only if the final plan still routes any DOCX proof through the existing unstructured renderer after fixing type serialization (425 lines)
- `modules/build/build_chapter_html_v1/main.py` — avoid touching unless extracting a narrowly reusable bundle/provenance helper is clearly cheaper than a DOCX-specific builder (1686 lines)
- `modules/common/marker_page_html.py` or a new shared bundle-emitter helper — possible reuse/extraction point for manifest/provenance writing so Story 172 does not duplicate contract emission logic
- `driver.py` — add generic DOCX input override support if the maintained recipe needs CLI parity with the PDF lane (2198 lines)
- `schemas.py` — add `RunConfig` or provenance fields only if the winning path requires them (1215 lines)
- `tests/test_docx_intake_recipe.py` — new focused recipe/driver smoke coverage (new file)
- `tests/test_doc_web_bundle_contract.py` — extend contract assertions if DOCX-native provenance fields or pageless-source rules change (294 lines)
- `docs/doc-web-bundle-contract.md` — make the pageless-source provenance rule explicit if Story 172 changes the accepted contract surface
- `testdata/` — repo-owned DOCX fixture plus source/generator and any fixture README updates (new files; [testdata/README.md](/Users/cam/.codex/worktrees/1f1d/doc-web/testdata/README.md) is 58 lines today)
- `tests/fixtures/formats/_coverage-matrix.json` — move the `docx` row only as far as the proof earns (348 lines)
- `docs/build-map.md` — update Gap 3 and the `docx` row honestly (584 lines)
- `docs/RUNBOOK.md` — publish the maintained proof command if the story lands a user-facing lane (245 lines)

## Redundancy / Removal Targets

- Any ad hoc DOCX-to-PDF proof script or scratch conversion path that would silently replace DOCX-native provenance instead of remaining explicit benchmark evidence
- Divergent duplicate unstructured intake helpers if PDF and DOCX can share one narrow internal helper honestly
- Stale docs that still describe office documents as completely unaddressed once the maintained DOCX lane lands

## Notes

- This story is intentionally DOCX-first. The build map already says to create the DOCX story before deciding whether `xlsx` and `pptx` stay grouped or split.
- The first supported DOCX slice does not need to solve every Word feature. It does need to keep the support claim precise.
- The biggest architectural risk is not extraction quality; it is provenance honesty for a source type that is not page-native. If the existing `doc-web` contract cannot express that cleanly, stop and open the ADR question instead of faking page metadata.

## Plan

### Exploration Summary

- **Ideal alignment:** this story closes a real Ideal gap. `docx` is still fully untested even though office documents are named as a high-value missing family in [build-map.md](/Users/cam/.codex/worktrees/1f1d/doc-web/docs/build-map.md).
- **Relevant build-map state:** Category 1 already has maintained intake/routing substrate and is ready for another explicit family. Category 6/7 already define the bundle/provenance bar that the DOCX lane must meet.
- **Critical substrate verified in code and runtime:** `unstructured.partition.docx` imports, `python-docx` imports, `pandoc` is installed, and an existing bundle/provenance emitter seam already exists in `modules/common/marker_page_html.py`. The missing substrate is a DOCX-specific maintained lane, generic DOCX input override support, and a pageless-source rule in the public provenance contract.
- **Measured baseline on a temporary fixture:** `unstructured.partition.docx` preserved headings/list items/tables and exposed stable element ids plus `parent_id`, but no `page_number`; `pandoc` preserved the cleanest structural HTML on the same fixture, but only gave consumer-side HTML/AST structure rather than source anchors; `python-docx` preserved explicit Word styles and table cells, but would require us to synthesize stable anchors ourselves. Reusing the current PDF serializer/renderer path is not viable for DOCX as-is because it flattened all element types to `Unknown` and emitted a synthetic single-page HTML wrapper.
- **Substrate reality check:** the story is still honestly buildable, but only if it absorbs a small coherent scope delta: evolve the `doc-web` provenance contract so pageless sources can omit `source_page_number` while still carrying non-empty DOCX-native `source_element_ids` / anchors. That looks like a schema + contract-test + doc update, not a new ADR yet.

### Eval-First Gate

- **Baseline first:** compare the locally real seams before building new abstractions:
  1. `unstructured.partition.docx`
  2. `pandoc`
  3. minimal `python-docx` extraction
- **Baseline evidence:** temporary artifacts live under `/var/folders/8f/3nlcf3sj1s5bbk1g_3dt3djm0000gn/T/story172-baseline-xjia5kt2/`. Key checks:
  - `summary.json` shows `unstructured` emitted 8 elements with `Title`, `NarrativeText`, `ListItem`, and `Table`, plus stable ids and `parent_id`, but null `page_number` throughout.
  - `pandoc.html` preserved `<h1>`, `<ul>`, and `<table>` cleanly for the tested slice.
  - `render-probe/document.html` emitted `Page 1` and flattened `Chapter One` / list/table structure after the current serializer dropped DOCX element types to `Unknown`.
  - `render-probe/elements_core.jsonl` assigned every block `page: 1`, proving the current reduction seam would fabricate page provenance for pageless DOCX.
- **Decision rule:** choose the smallest path that preserves headings and the claimed structure, produces an honest final bundle/provenance surface, and does not invent page metadata. Leading candidate after exploration: DOCX-specific intake over `unstructured.partition.docx` with corrected category serialization and DOCX-native anchors, using `python-docx` only if style/heading fidelity gaps appear during fixture implementation. `pandoc` remains a comparison baseline, not the primary provenance seam.
- **If all deterministic paths flatten the reviewed slice:** only then test a bounded AI repair follow-up instead of prematurely building a DOCX-specific AI layer.

### Implementation Outline

1. Add a repo-owned DOCX fixture and generator under `testdata/` that matches the supported slice the baseline already exercised: document title, heading-based sections, prose, simple bullet lists, and a simple table.
   - Done looks like: a stable fixture exists in-repo, the source/generator are checked in, and the story can point to exact supported features rather than generic “DOCX support.”
2. Land the contract delta first.
   - Update `schemas.py`, `tests/test_doc_web_bundle_contract.py`, and `docs/doc-web-bundle-contract.md` so pageless sources may omit `source_page_number` while still requiring non-empty `source_element_ids` / anchors.
   - Done looks like: the accepted `doc-web` contract can represent DOCX provenance honestly without fabricated page numbers.
3. Add the DOCX intake and bundle path.
   - Add `modules/extract/unstructured_docx_intake_v1/` with DOCX-safe element serialization.
   - Add `modules/transform/docx_elements_to_bundle_v1/` or extract a small shared bundle-emitter helper if that is cheaper than inflating `build_chapter_html_v1`.
   - Add `configs/recipes/recipe-docx-html-mvp.yaml`.
   - Add `driver.py` / `RunConfig` DOCX override support if recipe ergonomics otherwise require per-file edits.
   - Done looks like: `driver.py` can run an explicit DOCX recipe end-to-end on the checked-in fixture and leave a final bundle plus provenance sidecar.
4. Add proof coverage and run the real pipeline.
   - Add focused smoke tests for recipe wiring and the new contract behavior.
   - Clear stale `*.pyc`, run the narrowest real `driver.py` proof, and inspect extraction, manifest, and provenance artifacts under `output/runs/`.
   - Done looks like: the story can cite fresh artifact paths and representative block-level provenance rows from the current pass.
5. Update truth surfaces only as far as the proof earns.
   - Update the coverage matrix, build map, and runbook/testdata docs to the exact supported slice.
   - Done looks like: `docx` moves off `untested` no further than the fresh proof justifies.

### Impact Analysis

- **Primary blast radius:** new DOCX recipe/module surface, a likely new DOCX-specific builder, generic input override support, and the `doc-web` provenance contract for pageless sources.
- **Secondary blast radius:** coverage/build-map docs and any tests or helper code that currently assume page-number-centric provenance.
- **Main risks:** the current page-centric helpers may tempt a fake single-page fallback; the safer path is a narrower DOCX-native builder plus an explicit contract update. The story should bias toward “headings + prose + simple lists/tables only” rather than a broader but dishonest claim.
- **Structural health:** prefer new focused modules over enlarging [build_chapter_html_v1](/Users/cam/.codex/worktrees/1f1d/doc-web/modules/build/build_chapter_html_v1/main.py). If bundle-emission logic can be shared, extract a helper from the existing Marker path instead of duplicating manifest/provenance writing.
- **Human-approval blocker:** absorb the pageless provenance contract change into Story 172 instead of treating it as a separate prerequisite. Recommendation: yes, because the lane cannot honestly satisfy its own acceptance criteria without that delta, and the change appears tightly coupled and small.

### What Done Looks Like

- A user can point the maintained DOCX recipe at a DOCX file without editing the recipe itself.
- The run leaves final bundle/provenance artifacts in `output/runs/`, with DOCX-native anchors and no fabricated page numbers.
- The docs say exactly what the DOCX lane supports and what it still does not.

## Work Log

20260329-2038 — story created from triage: turned Build Map Gap 3 into a concrete next story after confirming that the local DOCX substrate is real but the maintained lane is missing. Evidence: `docs/build-map.md` still marks `docx` as `untested`; `unstructured.partition.docx` imports successfully; `python-docx` imports successfully; `pandoc` is installed; `driver.py` and `RunConfig` still expose only `input_pdf` overrides; and no DOCX recipe/module/test surface exists under `configs/recipes/` or `modules/`. Next step: `/build-story` should baseline the local DOCX seams on a repo-owned fixture, choose the smallest honest path, and only then implement the maintained lane.
20260329-2129 — exploration and planning: verified the cited context (`docs/ideal.md`, `docs/spec.md` `spec:1/spec:6/spec:7/spec:8`, `docs/build-map.md`, ADR-002, `docs/doc-web-bundle-contract.md`, Stories 153-154) and traced the actual runtime seams in `driver.py`, `schemas.py`, `modules/intake/unstructured_pdf_intake_v1/main.py`, `modules/render/render_html_from_elements_v1/main.py`, `modules/normalize/reduce_ir_v1/main.py`, `modules/build/build_chapter_html_v1/main.py`, and `modules/common/marker_page_html.py`. Baseline evidence came from a temporary synthetic DOCX fixture at `/var/folders/8f/3nlcf3sj1s5bbk1g_3dt3djm0000gn/T/story172-baseline-xjia5kt2/`: `summary.json` shows `unstructured.partition.docx` preserved `Title`, `NarrativeText`, `ListItem`, and `Table` elements with stable hashed ids plus `parent_id`, but emitted no `page_number`; `pandoc.html` preserved `<h1>`, `<ul>`, and `<table>` cleanly; `python-docx` preserved explicit `Title`, `Heading 1`, `List Bullet`, and table rows; and the current reuse probe under `render-probe/` exposed why the existing PDF path cannot be reused directly. `render-probe/elements.jsonl` serialized every DOCX element as `type="Unknown"` because `serialize_element()` reads `element.type` while DOCX extraction exposes `category`, `render-probe/document.html` flattened headings/lists/tables and emitted a synthetic `Page 1` wrapper, and `render-probe/elements_core.jsonl` assigned every block `page: 1` because `reduce_ir_v1` defaults missing page numbers to `1`. Substrate conclusion: Story 172 is buildable, but only if it absorbs a small coherent scope delta to evolve the public `doc-web` provenance contract for pageless sources. Recommended path: keep the lane deterministic, use a DOCX-specific intake/builder path with DOCX-native anchors, and treat `pandoc` as a comparison baseline rather than the maintained provenance source. Next: wait for human approval before implementation.
20260329-2149 — implementation landed: added repo-owned fixture inputs at `testdata/docx-mini.source.json`, `testdata/generate_docx_fixture.py`, and generated `testdata/docx-mini.docx`; added `unstructured_docx_intake_v1` plus `docx_elements_to_bundle_v1`; extended `driver.py` / `RunConfig` with `--input-docx` and `input_docx`; made `doc_web_provenance_block_v1` accept pageless blocks; and updated recipe/tests/docs truth surfaces for the maintained DOCX slice. Evidence: `make lint` passed; `make test` passed (`392 passed`); `python -m pytest tests/test_docx_intake_recipe.py tests/test_doc_web_bundle_contract.py -q` passed (`17 passed`); and the real driver proof `python driver.py --recipe configs/recipes/recipe-docx-html-mvp.yaml --input-docx testdata/docx-mini.docx --run-id story172-docx-lane-r1 --force` completed successfully. Manual artifact inspection from `output/runs/story172-docx-lane-r1/`:
- `01_unstructured_docx_intake_v1/elements.jsonl` preserves `Title`, `NarrativeText`, `ListItem`, and `Table` rows with stable hashed ids and `parent_id` links from the DOCX source.
- `02_docx_elements_to_bundle_v1/docx_bundle_report.json` reports `entry_count=2`, `provenance_row_count=7`, and the final bundle artifact paths.
- `output/html/manifest.json` validates as `doc_web_bundle_manifest_v1`, lists `chapter-001` and `chapter-002`, and keeps `source_pages=[]` / `printed_pages=[]` rather than faking pagination.
- `output/html/provenance/blocks.jsonl` validates as `doc_web_provenance_block_v1` with rows such as `blk-chapter-001-0003 -> ["d160add9df7fb60d3e5b6b9c1800b014"] "Parents: Ada and Lin"` and `blk-chapter-001-0005 -> ["407196643c26045788f93f280443744f"] "Name Role Ada Researcher Lin Archivist"`, all with no fabricated `source_page_number`.
- `output/html/chapter-001.html` renders the supported slice with block ids on the heading, paragraph, list items, and table (`blk-chapter-001-0001` through `blk-chapter-001-0005`). Result: the repo now has a maintained explicit DOCX lane for the narrow checked-in slice, and the public truth surfaces now honestly show `docx` as `has fixture`, not `passing`. Next: recommend `/validate` or `/mark-story-done` depending on whether the user wants a separate validation close-out pass.
20260329-2206 — story closed after fresh validation and close-out alignment. Evidence refreshed in this pass: `make lint` passed, `make test` passed (`392 passed`), `python -m pytest tests/test_docx_intake_recipe.py tests/test_doc_web_bundle_contract.py -q` passed (`17 passed`), and `python driver.py --recipe configs/recipes/recipe-docx-html-mvp.yaml --input-docx testdata/docx-mini.docx --run-id story172-validate-r1 --force` produced a fresh accepted bundle at `output/runs/story172-validate-r1/output/html/manifest.json` plus matching pageless provenance at `output/runs/story172-validate-r1/output/html/provenance/blocks.jsonl`. Manual inspection confirmed preserved `Title` / `NarrativeText` / `ListItem` / `Table` extraction in `01_unstructured_docx_intake_v1/elements.jsonl`, empty `source_pages` / `printed_pages` in the final manifest, and stable `source_element_ids` with no fabricated `source_page_number` in the provenance sidecar. The story record, story index, and changelog were updated to match the shipped slice. Next: `/check-in-diff`.
