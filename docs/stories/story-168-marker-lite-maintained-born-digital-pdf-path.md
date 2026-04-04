---
title: Maintain a `Marker`-Lite Born-Digital PDF Path
status: Done
priority: High
ideal_refs:
- 'Requirement #1 (Ingest), Requirement #3 (Extract), Requirement #5 (Structure),
  Requirement #6 (Validate), Any format, any condition, Traceability is the Product'
spec_refs:
- spec:1
- spec:1.1
- spec:3
- spec:3.1
- spec:6
- spec:7
adr_refs: []
depends_on:
- '166'
category_refs:
- spec:1
- spec:3
- spec:6
- spec:7
compromise_refs:
- C2
- C3
input_coverage_refs:
- born-digital-pdf
architecture_domains: []
roadmap_tags: []
legacy_system: ''
---

# Story 168 — Maintain a `Marker`-Lite Born-Digital PDF Path

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #1 (Ingest), Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Any format, any condition, Traceability is the Product
**Spec Refs**: spec:1 (spec:1.1, C2), spec:3 (spec:3.1, C3), spec:6, spec:7
**Build Map Refs**: Category 1 Intake & Format Routing (`partial`, C2 `climb`); Category 3 Layout & Structure Understanding (`exists`, C3 `climb`); Category 7 Graduation & Dossier Handoff (`partial`); Input Coverage row `born-digital-pdf` remains `has-fixture`
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/scout/scout-011-external-document-ingestion-systems.md`, `docs/stories/story-165-marker-breadth-comparator-born-digital-pdf.md`, `docs/stories/story-166-marker-internals-born-digital-pdf-substrate.md`, `docs/build-map.md`
**Depends On**: Story 166

## Goal

Turn Story 166's bounded `Marker`-lite spike into a maintained born-digital PDF
path only if it can stay inside the accepted `doc-web` boundary. The work
should reuse the proven native-text seam, preserve contract-grade block
provenance, and fix the specific normalization defects that still block direct
runtime adoption: inconsistent heading levels and merged choice paragraphs on
the repo-owned `tbotb-mini.pdf` lane. The result should be a maintained
optional path, not stock `Marker` adoption.

## Acceptance Criteria

- [x] A maintained native-text path exists for `born-digital-pdf` on the active repo-owned fixture:
  - reuses the bounded `Marker`-lite internal seam rather than stock `Marker` CLI
  - runs through `driver.py` or a maintained recipe path, not only a story-local spike script
  - writes artifacts under `output/runs/` that validate against the accepted `doc-web` contract
- [x] The maintained path fixes the Story 166 normalization defects on `testdata/tbotb-mini.pdf`:
  - heading levels are normalized consistently across pages
  - page 3's choice prompt is split into two blocks rather than merged into one paragraph
  - no silent text loss is introduced while fixing those defects
- [x] The maintained path is compared honestly against the current OCR-routed baseline:
  - record what improves, what remains worse, and whether the maintained path is now strong enough to change the `born-digital-pdf` row in `docs/build-map.md`
  - preserve block-level provenance and processing-step traceability in an accepted `doc-web` surface
  - keep licensing/runtime constraints explicit instead of hiding them behind helper code

## Out of Scope

- Adopting stock `Marker` CLI into maintained operator workflows
- Claiming general `docx`, `pptx`, `xlsx`, or `epub` support from the `Marker` stack
- Reopening the negative `Docling` or `Surya` boundary decisions
- Broad model/license policy changes beyond the already documented `Marker` constraints

## Approach Evaluation

- **Simplification baseline**: the current maintained pagelines baseline already reaches `1.0` token coverage on `tbotb-mini.pdf`, so this story is only worth building if the `Marker` seam improves native-text routing and contract-grade provenance instead of just producing cleaner-looking HTML.
- **AI-only**: rejected as the primary path. A one-shot LLM rewrite could fix heading levels or choice splitting, but it would dodge the intake/runtime boundary question this story exists to answer.
- **Hybrid**: leading candidate. Keep Marker internals for native-text structure extraction, then use thin deterministic normalization inside the maintained path to reach the accepted `doc-web` contract.
- **Pure code**: fallback only if the current local PDFtext/OCR surfaces can now match Marker without the extra runtime burden. Story 166 evidence says that is not yet true on the repo-owned lane.
- **Repo constraints / prior decisions**: ADR-002 keeps `doc-web` as the runtime boundary; Story 165 rejected stock `Marker` adoption; Story 166 proved a contract-aligned spike but left the maintained path unbuilt.
- **Existing patterns to reuse**: `scripts/spikes/marker_breadth_benchmark.py`, `scripts/spikes/marker_page_html_prototype.py`, `doc_web/runtime_contract.py`, `modules/build/build_chapter_html_v1/main.py`, Story 157's maintained PDF-entry wiring, and the bundle/provenance contract tests.
- **Eval**: the deciding proof is a maintained run on `testdata/tbotb-mini.pdf` that emits accepted `doc-web` bundle/provenance artifacts and resolves Story 166's heading/paragraph defects without losing text or weakening provenance.

## Tasks

- [x] Reconfirm the bounded Marker runtime substrate and decide whether the maintained path should vendor the spike logic or extract a cleaner shared helper
- [x] Implement the smallest maintained born-digital PDF path that can reuse Marker-lite without violating ADR-002
- [x] Land deterministic heading-level and paragraph-splitting normalization for the known `tbotb-mini.pdf` defects without hardcoding book-specific text
- [x] Add focused regression coverage for the known `tbotb-mini.pdf` normalization defects so heading hierarchy and split-choice behavior stay guarded after the maintained path lands
- [x] Run a real maintained path through `driver.py`, inspect emitted `doc-web` bundle/provenance artifacts, and compare against the current OCR-routed baseline
- [x] If this story changes documented format coverage or graduation reality: update `docs/build-map.md` and record the before/after state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py` or `make smoke`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [x] If agent tooling changed: `make skills-check` (not needed; no agent tooling changes)
- [x] If evals or goldens changed: run `/improve-eval` and update `docs/evals/registry.yaml` (not needed; no eval or golden changes)
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every output traces to source page, OCR engine, confidence, processing step
  - [x] T1 — AI-First: didn't write code for a problem AI solves better
  - [x] T2 — Eval Before Build: measured SOTA before building complex logic
  - [x] T3 — Fidelity: source content preserved faithfully, no silent losses
  - [x] T4 — Modular: new recipe not new code; no hardcoded book assumptions
  - [x] T5 — Inspect Artifacts: visually verified outputs, not just checked logs

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: maintained PDF intake / transform / build surfaces that currently own `born-digital-pdf` routing, plus the `doc-web` bundle/provenance contract docs.
- **Build-map reality**: Category 1 is still `partial` / `climb`; Category 3 still owns structure normalization; `born-digital-pdf` now has an explicit maintained optional native-text path on one tiny fixture, but it is still not honest `passing` coverage.
- **Substrate evidence**: Story 166 proved repo-local spike artifacts under `output/runs/story166-marker-page-html-r2/` and `output/runs/story166-marker-probe-r2/` / `story166-marker-probe-r1`; contract tests in `tests/test_doc_web_bundle_contract.py` and `tests/test_doc_web_cli_contract.py` keep the boundary explicit; Story 157 preserves the maintained PDF entry path.
- **Data contracts / schemas**: the target is to reuse the existing `doc_web_bundle_manifest_v1` and `doc_web_provenance_block_v1` surfaces. Avoid schema changes unless the maintained path proves a real missing field.
- **File sizes**: likely touch points are already large (`modules/build/build_chapter_html_v1/main.py`, `schemas.py`, and intake/recipe surfaces), so the maintained integration should prefer small helpers or adapters over inflating giant files.
- **Decision context**: ADR-002, Scout 011, Story 165, and Story 166 are the primary constraints. No new ADR is needed unless the maintained integration forces a new runtime or licensing decision.

## Files to Modify

- `modules/` maintained intake/build surfaces for born-digital PDF routing — exact seam to be chosen during `/build-story`
- `configs/recipes/` maintained PDF recipe(s) — only if the native-text path earns a real maintained lane
- `tests/` story-scoped regression coverage for the new maintained module/helper path and the known heading / choice-splitting defects
- `docs/build-map.md` — update the `born-digital-pdf` row if the maintained path becomes honest coverage
- `docs/scout/scout-011-external-document-ingestion-systems.md` — update the Marker standing once the maintained decision is real
- `docs/stories/story-168-marker-lite-maintained-born-digital-pdf-path.md` — work log and plan

## Redundancy / Removal Targets

- Story-local Marker normalization glue in `scripts/spikes/marker_page_html_prototype.py` if the maintained path absorbs the same behavior cleanly
- Any stale born-digital PDF tracker language that still assumes the lane is only OCR-routed after the maintained path lands

## Notes

- Story 166 already answered the spike question positively enough to justify this story. The open question here is not "is Marker interesting?" but "can the useful seam be maintained honestly without pulling in the stock product surface?"
- Keep the follow-on narrow: repo-owned `tbotb-mini.pdf` first, maintained path second, broader born-digital widening only after that passes.

## Plan

### Exploration Summary

- **Ideal alignment:** proceed. This story closes a real Ideal gap: `born-digital-pdf` remains the highest-priority non-passing format row in `docs/build-map.md`, and the accepted `doc-web` contract already expects provenance-rich structural output rather than OCR-first HTML for every PDF.
- **Relevant build-map state:** Category 1 remains `partial` / `climb`; Category 3 remains `exists` / `climb`; Category 7 remains `partial`; Input Coverage still marks `born-digital-pdf` as `has-fixture`, not passing.
- **Critical substrate verified in code:**
  - `driver.py` already supports explicit PDF recipes and `--input-pdf` overrides.
  - `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` and `tools/run_manager.py` already provide the maintained OCR-backed PDF entry surface from Story 157.
  - `scripts/spikes/marker_breadth_benchmark.py` contains the real bounded Marker-lite runtime/bootstrap seam, including the repo-local container naming and the `LiteBornDigitalConverter` path.
  - `scripts/spikes/marker_page_html_prototype.py` already exposes reusable normalization logic via `normalize_marker_document(...)` for `page_html_v1` plus `doc_web_bundle_manifest_v1` / `doc_web_provenance_block_v1`.
  - `modules/build/build_chapter_html_v1/main.py` already accepts `--illustration-manifest` as optional, so a born-digital path can reuse the maintained bundle builder without forcing an illustration stage.
  - Fresh baseline checks in this checkout passed: `python -m pytest tests/test_marker_page_html_prototype.py tests/test_pdf_intake_recipe.py tests/test_doc_web_bundle_contract.py tests/test_doc_web_cli_contract.py -q` (`19 passed`).
- **Critical substrate still missing:** there is no maintained module or maintained recipe that runs the Marker-lite seam through `driver.py`. The prototype and benchmark logic live only under `scripts/spikes/`.
- **Current-pass surprise:** this checkout does not currently contain the cited `output/runs/story165-*` / `story166-*` artifacts or even an `output/runs/` tree, so implementation must regenerate fresh artifacts rather than relying on historical outputs.
- **Scope adjustment folded in automatically:** add focused regression coverage for the known page-2 heading hierarchy defect and page-3 split-choice defect. Current baseline tests validate the contract and PDF entry plumbing, but they do not yet lock these exact normalization cases.

### Eval-First Gate

- **Baseline eval:** the current story-specific contract + PDF-entry baseline is `19 passed` on the focused pytest set above.
- **What the baseline proves:** the accepted `doc-web` contract is stable, the prototype script still works, and maintained PDF entry already exists for OCR-backed recipes.
- **What the baseline does not prove:** the current codebase has no maintained native-text route and no automated regression that captures the two Story 166 normalization defects. The implementation should add that coverage before or alongside the fix.
- **Candidate approaches:**
  - **AI-only:** rejected. An LLM rewrite could patch headings or split paragraphs, but it would bypass the story's core requirement: a maintained native-text path inside the accepted runtime boundary.
  - **Hybrid:** recommended. Reuse Marker internals for born-digital structure extraction, then apply thin deterministic normalization and reuse the existing `doc-web` contract/bundle machinery.
  - **Pure code:** fallback only if the current `pdftext` / OCR path can now meet the same native-text and provenance bar without Marker. Story 166 evidence says it cannot yet.

### Implementation Tasks

#### Task 1 — Extract the reusable Marker-lite seams out of the story-local spikes (`M`)

- **Files:** likely a new helper under `modules/common/` for the repo-local Docker/runtime bootstrap and a new helper under `modules/common/` or `modules/extract/` for page-html normalization; `scripts/spikes/marker_breadth_benchmark.py`; `scripts/spikes/marker_page_html_prototype.py`.
- **Change:** move the real reusable logic out of the spike-only scripts:
  - repo-local Marker-lite runtime/bootstrap logic now embedded in `marker_breadth_benchmark.py`
  - `normalize_marker_document(...)` and related bundle/provenance builders now embedded in `marker_page_html_prototype.py`
- **Why first:** the maintained module should import stable helpers, not shell out to story-specific scripts or duplicate them.
- **Done when:** the maintained path can call shared helper functions directly, and the spike scripts become thin wrappers over the same logic instead of the only implementation.

#### Task 2 — Add a maintained extract module for born-digital Marker-lite HTML (`M`)

- **Files:** new module directory under `modules/extract/` with `main.py` and `module.yaml`; possibly shared helper imports from Task 1.
- **Change:** create an explicit extract-stage module that:
  - accepts `--pdf`, `--outdir`, progress/state flags, and recipe params
  - runs the bounded Marker-lite seam in the repo-local container/runtime
  - writes stamped `page_html_v1` as the stage artifact
  - preserves inspectable sidecars such as runtime trace and raw Marker metadata in the stage output directory
- **Decision guard:** keep this as an explicit born-digital module, not a replacement for the existing OCR-backed PDF path.
- **Done when:** `driver.py` can execute the new module directly and produce a real stage artifact under `output/runs/<run_id>/01_<module_id>/`.

#### Task 3 — Land deterministic normalization for the known heading + choice defects (`S-M`)

- **Files:** the new maintained module/helper from Tasks 1-2; likely tests under `tests/`.
- **Change:** normalize the two known Story 166 defects without hardcoding `tbotb-mini` text:
  - consistent heading hierarchy across pages when Marker emits the same structural family at mixed heading depths
  - split the page-3 choice prompt into two blocks/paragraphs instead of one merged paragraph
- **Constraint:** preserve source text exactly; the fix must be structural only, with no silent text loss.
- **Done when:** the maintained path no longer reproduces those defects on the fixture and still validates against the current contract.

#### Task 4 — Add explicit regression coverage for the maintained path (`S`)

- **Files:** likely a new focused test file under `tests/` plus updates to `tests/test_marker_page_html_prototype.py` only if reuse is cleaner.
- **Change:** add fixture-backed assertions for:
  - heading-level normalization on the reviewed page-2 shape
  - split-choice behavior on the reviewed page-3 shape
  - contract/stamping survival for the maintained module output
- **Why separate from Task 3:** current baseline tests do not protect these exact failure modes, so the story would otherwise regress silently after landing.
- **Done when:** the new regression test fails against the pre-fix behavior and passes with the maintained implementation.

#### Task 5 — Add an explicit maintained recipe and validate against the OCR baseline (`M`)

- **Files:** likely a new recipe under `configs/recipes/`; possibly `docs/build-map.md`, `docs/scout/scout-011-external-document-ingestion-systems.md`, and truth-surface docs if the support read changes.
- **Change:** create a dedicated maintained born-digital recipe that reuses the new extract module and existing downstream maintained stages where they still fit.
  - Prefer an explicit born-digital recipe such as `recipe-born-digital-pdf-marker-lite-html-mvp.yaml`.
  - Do **not** change `tools/run_manager.py` to silently swap the default PDF recipe; scanned PDFs still need the OCR-backed route, and `spec:1.1` still prefers explicit recipes over hidden routing.
- **Validation path:** after implementation, run:
  - the new born-digital Marker-lite recipe on `testdata/tbotb-mini.pdf`
  - the current OCR baseline recipe on the same fixture
  - compare resulting `page_html_v1` and `doc-web` bundle/provenance artifacts honestly
- **Done when:** the maintained path has fresh artifact proof under `output/runs/`, the comparison is recorded, and the build-map row is updated only as far as the evidence justifies.

### Impact Analysis

- **Primary blast radius:** new maintained extract module + recipe only. This should avoid changing the current scanned-PDF OCR path from Story 157.
- **Secondary blast radius:** shared helper extraction from the spike scripts. If done carefully, this reduces duplication without changing existing spike behavior.
- **Large files to avoid inflating:** `modules/build/build_chapter_html_v1/main.py` and `schemas.py`. Current exploration found no reason to change either unless implementation proves a real contract gap.
- **Tests at risk:** contract tests and PDF smoke tests are the guardrails; new focused normalization tests should be added instead of widening repo-wide test assumptions.
- **Expected build-map movement:** likely the `born-digital-pdf` row note changes from "prototype only" to "maintained native-text path exists on the repo-owned fixture," but it may still remain short of broad `passing` / graduation claims because the family still has one tiny fixture and no widened coverage.

### Structural Health Notes

- Keep recipe selection explicit. This story should add a new maintained born-digital recipe, not an implicit PDF router.
- Keep the current `doc-web` contract frozen unless implementation proves a real missing field. Right now the existing bundle/provenance schemas appear sufficient.
- Prefer extracting small helpers from `scripts/spikes/` over importing whole scripts from production code or copying code into the new module.
- If the maintained module still requires Docker and a repo-local cached Marker runtime, surface that explicitly in docs and error messages. Do not hide heavyweight runtime bootstrapping behind a silent default path.

### Human-Approval Blockers / Risks

- **Runtime/operator risk:** the maintained path will likely depend on Docker plus the repo-local Marker runtime/bootstrap seam. That is consistent with Story 166, but it is still a meaningful operator dependency that should remain explicit.
- **Routing risk:** switching the default PDF recipe to Marker-lite would be a larger product decision and is **not** recommended in this story.
- **Schema risk:** none expected. If implementation reveals a real schema gap, stop and get approval before changing the contract.

### What Done Looks Like

- A fresh `driver.py` run on `testdata/tbotb-mini.pdf` through an explicit maintained born-digital recipe produces:
  - stage artifacts under `output/runs/`
  - `page_html_v1` that no longer shows the known heading / merged-choice defects
  - an accepted `doc-web` bundle + provenance surface
- The comparison against the current OCR-backed baseline is written down with honest tradeoffs.
- The story remains inside ADR-002's accepted `doc-web` boundary and does not silently expand into stock Marker adoption or hidden PDF auto-routing.

## Work Log

20260327-2006 — story created as the exact maintained follow-on required by Story 166's boundary decision. Evidence: Story 166 now proves a contract-aligned spike under `output/runs/story166-marker-page-html-r2/` and a fresh current pagelines baseline under `output/runs/story166-docweb-pagelines-baseline-r1/`, but the maintained runtime path is still unbuilt. Next step: `/build-story` should verify the current maintained PDF substrate, freeze the exact integration seam, and decide whether this can honestly be promoted beyond `Draft`.
20260327-1729 — promoted to Pending: user approved moving Story 168 out of `Draft` so `/build-story` can do the substrate reality check and write the implementation plan. No code changes are authorized in this phase; next step is to verify the maintained PDF substrate, re-read the build-map / ADR context, and decide whether the story is honestly build-ready or needs scope adjustment before implementation.
20260327-1734 — explored substrate and wrote implementation plan: reviewed `docs/ideal.md`, `docs/spec.md` (`spec:1.1`, `spec:3.1`, `spec:6`, `spec:7`), the `born-digital-pdf` row and Gap 2 in `docs/build-map.md`, ADR-002, Story 166, Story 157, and Scout 011. Critical substrate is real in code: `driver.py` already accepts explicit PDF recipes and `--input-pdf`, the maintained OCR-backed PDF path from Story 157 still exists, `scripts/spikes/marker_breadth_benchmark.py` contains the bounded repo-local Marker-lite runtime/bootstrap seam, and `scripts/spikes/marker_page_html_prototype.py` already exposes reusable normalization logic that emits `page_html_v1` plus `doc_web_bundle_manifest_v1` / `doc_web_provenance_block_v1`. Fresh baseline checks in this checkout passed: `python -m pytest tests/test_marker_page_html_prototype.py tests/test_pdf_intake_recipe.py tests/test_doc_web_bundle_contract.py tests/test_doc_web_cli_contract.py -q` (`19 passed`). Main missing slice: there is still no maintained module or maintained recipe that runs the Marker-lite seam through `driver.py`; the logic lives only under `scripts/spikes/`. Surprise: this checkout currently has no `output/runs/` tree, so the Story 165/166 artifact paths cited in the docs are historical references rather than live local artifacts. Small scope delta absorbed: add focused regression coverage for the page-2 heading hierarchy defect and page-3 merged-choice defect, because the current passing baseline does not guard those exact failure modes yet. Next step: wait for approval on the written plan before implementing the shared helpers, maintained extract module, explicit recipe, and fresh artifact comparison.
20260327-1831 — implementation started: user approved building the maintained path, so Story 168 is now `In Progress` and the first task is active. The implementation will start by extracting the real reusable Marker-lite runtime/bootstrap and normalization seams out of the spike scripts so the maintained module can import stable helpers instead of shelling out to story-local code. Next step: land the shared helper slice, then wire a maintained extract module and explicit born-digital recipe through `driver.py`.
20260327-1846 — shared helper and maintained-lane implementation landed: extracted the reusable runtime/bootstrap seam into `modules/common/marker_lite_runtime.py`, moved the Marker JSON -> `page_html_v1` + `doc_web_bundle` / provenance normalizer into `modules/common/marker_page_html.py`, added the maintained extract module under `modules/extract/extract_pdf_marker_lite_html_v1/`, reduced `scripts/spikes/marker_page_html_prototype.py` to a thin wrapper, and added the explicit maintained recipe `configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml`. Focused regression coverage now lives in `tests/test_extract_pdf_marker_lite_html_v1.py` plus updated `tests/test_marker_page_html_prototype.py`. Evidence: `python -m py_compile modules/common/marker_lite_runtime.py modules/extract/extract_pdf_marker_lite_html_v1/main.py` passed; `python -m pytest tests/test_extract_pdf_marker_lite_html_v1.py tests/test_marker_page_html_prototype.py -q` passed (`3 passed`). Next step: prove the path through `driver.py` and inspect real artifacts.
20260327-1907 — first maintained proof exposed the real runtime/operator failure and the fix: `output/runs/story168-marker-lite-proof-r1/01_extract_pdf_marker_lite_html_v1/marker_raw/json/marker.log` showed Surya layout-model download failing with `OSError: [Errno 28] No space left on device` because the cached Marker image still inherited stale `/work` and pip bind metadata from another worktree while using the container `/tmp` for large model files. Fresh `docker inspect` on the rebuilt runtime confirmed that `doc-web/story165-marker-cpu:9f4f` preserved stale `/work` and `/root/.cache/pip` binds, but current repo-local datalab and tmp binds were still correct. Decision: stop relying on mounted host input/output paths, keep the cached runtime image, and change `run_lite_api(...)` to copy PDFs into `/tmp/marker-lite-*` inside the container and copy outputs back out with `docker cp`, while reusing containers only when current datalab/tmp mounts plus a Marker package probe are valid. Next step: rerun the maintained recipe with the transport fix and inspect the generated artifacts manually.
20260327-1932 — maintained proof, baseline comparison, doc updates, and final checks all passed. Fresh maintained run: `python driver.py --recipe configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml --input-pdf testdata/tbotb-mini.pdf --run-id story168-marker-lite-proof-r4 --output-dir output/runs/story168-marker-lite-proof-r4 --allow-run-id-reuse --force` completed end-to-end. Manual artifact inspection on `output/runs/story168-marker-lite-proof-r4/01_extract_pdf_marker_lite_html_v1/pages_html.jsonl` confirmed the Story 166 defects are fixed: page 2 now keeps `Section 1`-`Section 7` at consistent `h3`, and page 3 splits the previously merged choice prompt into two paragraph blocks before `Section 8`. `output/runs/story168-marker-lite-proof-r4/01_extract_pdf_marker_lite_html_v1/normalization_report.json` records `4` heading adjustments, `1` split paragraph, and no `text_mismatch_pages`; `summary.json` reports `token_coverage_vs_pdftotext = 1.0`; `doc_web_bundle/manifest.json` plus `doc_web_bundle/provenance/blocks.jsonl` prove the accepted contract surface with `51` provenance blocks carrying source page, Marker element id, bbox, confidence, and processing-step traceability. Fresh OCR comparison run: `python driver.py --recipe configs/recipes/recipe-pdf-ocr-html-mvp.yaml --input-pdf testdata/tbotb-mini.pdf --run-id story168-ocr-baseline-r1 --output-dir output/runs/story168-ocr-baseline-r1 --allow-run-id-reuse --force` also reached `1.0` token coverage on the fixture and already had clean heading / split-choice structure, but it still routes through image extraction + OCR and does not emit the extract-stage `doc_web_bundle` / block-provenance surface that the maintained Marker lane now does. Honest tradeoff: Marker now wins the story-specific question (maintained native-text routing plus contract-grade provenance), while OCR remains materially lighter and faster on this repo today (`521.44s` cold Marker extract versus `11.84s` OCR stage on the same 3-page fixture) and therefore should remain the default general PDF lane. Updated truth surfaces: `docs/build-map.md` and `docs/scout/scout-011-external-document-ingestion-systems.md` now record that the maintained optional path exists but is still bounded to one tiny fixture and explicit runtime constraints. Final repo checks passed fresh after the implementation/docs updates: `make lint` (`All checks passed!`) and `make test` (`379 passed, 12 warnings`). Next step: run `/validate` before any attempt to mark the story done or widen the `born-digital-pdf` claim further.
20260327-2347 — story closed via `/mark-story-done`: fresh close-out validation reconfirmed the Story 168 slice with `make lint` (`All checks passed!`), `make test` (`379 passed, 12 warnings`), and renewed artifact inspection on `output/runs/story168-marker-lite-proof-r4/01_extract_pdf_marker_lite_html_v1/`. Acceptance criteria are now checked from current-pass evidence: the maintained native-text recipe exists, the page-2 heading and page-3 split-choice defects remain fixed with `text_mismatch_pages = []`, and the OCR comparison remains honestly recorded in the build map and Scout 011. Story status is now `Done`, the validation and story-done workflow gates are checked, and the story index/changelog are aligned with the shipped slice. Next step: `/check-in-diff`.
