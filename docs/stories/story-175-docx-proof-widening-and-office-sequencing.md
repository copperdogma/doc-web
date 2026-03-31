# Story 175 — Widen Maintained DOCX Proof and Decide Office Intake Sequencing

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #1 (Ingest), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Any format, any condition, Dossier-ready output, Traceability is the product
**Spec Refs**: spec:1 (spec:1.1, C2), spec:6, spec:7, spec:8 (B1, B5)
**Build Map Refs**: Category 1 Intake & Format Routing (`exists`, C2 `climb`); Category 6 Validation, Provenance & Export (`exists`); Category 7 Graduation & Dossier Handoff (`partial`); Input Coverage row `docx` (`has fixture`); Input Coverage rows `xlsx` / `pptx` (`untested`); Gap 3 — Office document intake beyond the widened DOCX slice; Gap 5 — Fixture breadth and graduation confidence
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/build-map.md`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/scout/scout-011-external-document-ingestion-systems.md`, `docs/stories/story-172-maintained-docx-intake-lane.md`, `docs/stories/story-174-docx-runtime-surface-and-contract-compatibility-signaling.md`, `testdata/README.md`, `None found after search in docs/decisions/ for a separate office-family routing ADR`
**Depends On**: Story 172, Story 174

## Goal

Widen the maintained DOCX lane beyond the single `docx-mini` fixture so the repo has honest evidence for more than one narrow Word slice, then use that fresh proof plus local substrate inspection to make the next office-family decision: should `xlsx` and `pptx` remain one combined office follow-up or split into separate stories? This story should improve real DOCX confidence and backlog honesty without over-claiming office support that the repo has not yet proven.

## Acceptance Criteria

- [x] The DOCX proof surface is materially wider than Story 172's first slice:
  - [x] at least two additional repo-owned or reproducibly generated DOCX fixtures exist beyond `testdata/docx-mini.docx`
  - [x] the widened fixture set covers distinct Word feature families and documents exactly which features are being claimed versus merely observed
- [x] The maintained DOCX lane is re-measured honestly on every claimed fixture:
  - [x] `configs/recipes/recipe-docx-html-mvp.yaml` runs through `driver.py` on each claimed supported fixture and leaves inspectable final bundle/provenance artifacts under `output/runs/`
  - [x] manual inspection is recorded for representative extraction, final manifest, and provenance artifacts for each fixture class
  - [x] if a widened fixture exposes a failing feature class, the story either lands the smallest honest DOCX fix or explicitly keeps that feature class outside the maintained claim
- [x] Truth surfaces reflect the widened evidence exactly:
  - [x] `tests/fixtures/formats/_coverage-matrix.json`, `docs/build-map.md`, and `testdata/README.md` describe the updated DOCX proof surface with no silent over-promotion
  - [x] the `docx` row only moves beyond `has fixture` if the fresh evidence truly earns it; otherwise the remaining gaps are tightened and made explicit
- [x] The office-family queue is no longer ambiguous:
  - [x] the story records an evidence-backed decision on whether `xlsx` and `pptx` should stay combined as one follow-up or split into separate follow-ups
  - [x] the chosen next-step shape is reflected in backlog/build-map planning surfaces so "office docs later" is no longer just an implied placeholder
- [x] Repeatable proof exists for the widened DOCX surface:
  - [x] focused tests or fixture-matrix coverage exist for the widened maintained lane
  - [x] the story documents the exact proof commands and checked artifacts needed to rerun the widened DOCX evidence

## Out of Scope

- Shipping maintained `xlsx` or `pptx` conversion lanes
- Hidden office auto-routing or planner-driven launch behavior beyond the current explicit-recipe compromise
- Claiming complete Word fidelity for tracked changes, comments, SmartArt, embedded charts, text boxes, or every Office feature in one pass
- Reopening ADR-002's accepted `doc-web` runtime boundary
- Dossier-side consumer changes or graduation mechanics beyond updating doc-forge's truth surfaces

## Approach Evaluation

- **Simplification baseline**: first rerun the current maintained DOCX lane on a broader fixture matrix and inspect the artifacts before adding new code. The first question is whether the existing DOCX path already handles more of Word than the current docs claim.
- **AI-only**: low-value default. Rasterizing or re-reading DOCX with a model weakens provenance and hides whether the native DOCX substrate is already sufficient.
- **Hybrid**: acceptable only if the widened fixtures expose one or two bounded Word feature classes where native extraction is close but not reviewable. Any AI repair must remain explicitly scoped and preserve DOCX-native provenance anchors.
- **Pure code**: likely correct for the first widened proof surface and for the `xlsx` / `pptx` sequencing decision. OOXML already carries structure; the job is fixture widening, deterministic extraction proof, and honest planning.
- **Repo constraints / prior decisions**: ADR-002 fixes the output boundary at `doc-web` bundle + provenance. Story 172 created the first honest DOCX lane and Story 174 hardened its runtime/contract surface. The build map still marks `docx` only as `has fixture` and `xlsx` / `pptx` as `untested`, so this story must widen proof before the backlog jumps ahead to new office families.
- **Existing patterns to reuse**: `testdata/generate_docx_fixture.py`, `testdata/README.md`, `configs/recipes/recipe-docx-html-mvp.yaml`, `modules/extract/unstructured_docx_intake_v1`, `modules/transform/docx_elements_to_bundle_v1`, `tests/test_docx_intake_recipe.py`, `tests/test_doc_web_cli_contract.py`, Story 167's repo-owned fixture pattern, Story 171's widened proof + honest docs pattern, and Scout 011's external-system posture for office-like inputs.
- **Eval**: the deciding proof is a widened DOCX fixture matrix run through the maintained lane with manual artifact inspection. No dedicated DOCX eval exists today, so the first task is evidence expansion, not prompt tuning or benchmark churn. For the `xlsx` / `pptx` decision, the gate is verified local substrate inspection plus documented provenance/structure prospects, not a hand-wavy preference.

## Tasks

- [x] Freeze the widened DOCX proof surface before changing logic:
  - [x] choose at least two additional DOCX feature slices beyond `docx-mini`
  - [x] include at least one likely-supported structural slice and at least one likely-boundary slice so the maintained claim line becomes explicit instead of optimistic
  - [x] add repo-owned or reproducibly generated fixtures plus source/generator docs under `testdata/`
  - [x] document the candidate supported slice per fixture before implementation starts
- [x] Measure the current maintained DOCX lane on the widened fixture set before adding new code:
  - [x] run `configs/recipes/recipe-docx-html-mvp.yaml` through `driver.py` on each widened fixture
  - [x] inspect `elements.jsonl`, final `manifest.json`, `provenance/blocks.jsonl`, and representative HTML entries
  - [x] classify each feature class as `supported-now`, `needs-fix`, or `not-yet-supported`
- [x] Land only the smallest honest DOCX changes required by the widened supported slice:
  - [x] keep fixes local to DOCX intake, bundle emission, fixture generation, or docs/tests when possible
  - [x] if widened features require new provenance or bundle semantics, update `schemas.py` before relying on them (not needed; Story 174 contracts already covered the widened slice)
  - [x] avoid inflating the maintained DOCX claim to cover feature classes that still fail review
- [x] Add repeatable proof coverage for the widened DOCX lane:
  - [x] extend `tests/test_docx_intake_recipe.py` or add a narrow fixture-matrix companion test
  - [x] extend `tests/test_doc_web_cli_contract.py` or `tests/test_doc_web_bundle_contract.py` only if runtime-contract or bundle semantics change (not needed; runtime contract unchanged beyond fresh smoke rerun)
  - [x] record exact rerun commands for every widened fixture path
- [x] Resolve the office-family planning ambiguity explicitly:
  - [x] inspect real local substrate options for `xlsx` and `pptx` (import/runtime seams, likely provenance shape, and whether the substrate is shared or divergent)
  - [x] decide whether the next office follow-up should stay combined or split
  - [x] if the decision changes the backlog shape materially, update the planning surfaces or create explicit follow-up story stubs instead of leaving the queue implicit
- [x] If this story changes documented format coverage or graduation reality: update `docs/build-map.md` and record the before/after state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [x] If agent tooling changed: `make skills-check` (not needed; agent tooling unchanged)
- [x] If evals or goldens changed: run `/improve-eval` and update `docs/evals/registry.yaml` (not needed; no eval or golden assets changed)
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: DOCX outputs still trace to source anchors or other accepted source structure with no fabricated pagination
  - [x] T1 — AI-First: only add AI if widened fixtures prove the native DOCX path is insufficient on a bounded seam
  - [x] T2 — Eval Before Build: widen the fixture matrix and inspect baseline artifacts before writing new logic
  - [x] T3 — Fidelity: do not broaden supported DOCX claims past what the inspected artifacts actually preserve
  - [x] T4 — Modular: keep DOCX widening, fixture generation, and office-family planning explicit instead of hiding them in generic office abstractions too early
  - [x] T5 — Inspect Artifacts: verify real `output/runs/` artifacts for each widened fixture, not just tests or logs

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: Category 1 office-input proof surfaces centered on `unstructured_docx_intake_v1`, `docx_elements_to_bundle_v1`, fixture generators under `testdata/`, and the planning/docs surfaces that define honest office-family sequencing.
- **Build-map reality**: Category 1 is `exists` and still in `climb`; the maintained DOCX lane exists but only as `has fixture`, while `xlsx` and `pptx` remain `untested`. Category 7 is still `partial`, so any widened proof must stay inside the accepted `doc-web` boundary rather than inventing an office-only side output.
- **Substrate evidence**: verified in this pass that `configs/recipes/recipe-docx-html-mvp.yaml`, `modules/extract/unstructured_docx_intake_v1/main.py`, `modules/transform/docx_elements_to_bundle_v1/main.py`, `driver.py --input-docx`, `tests/test_docx_intake_recipe.py`, and `tests/test_doc_web_cli_contract.py` already provide a maintained DOCX lane with runtime proof. Also verified that `tests/fixtures/formats/_coverage-matrix.json` still lists `docx` as `has-fixture` and `xlsx` / `pptx` as `untested`, with no recipe/module/test surface for either spreadsheet or slide inputs yet. That missing `xlsx` / `pptx` substrate is acceptable because this story only needs to decide their sequencing, not ship them.
- **Data contracts / schemas**: current accepted contracts are `doc_web_bundle_manifest_v1` and `doc_web_provenance_block_v1`; Story 174 already hardened the pageless DOCX semantics. No new schema change is assumed, but any widened DOCX feature that requires new block kinds, source anchors, or bundle metadata must be added to `schemas.py` before the stamped artifacts can claim it.
- **File sizes**: likely large-file touch points are `driver.py` (2212 lines), `schemas.py` (1216 lines), and `docs/build-map.md` (581 lines). Near-limit or medium files are `modules/transform/docx_elements_to_bundle_v1/main.py` (446 lines), `tests/fixtures/formats/_coverage-matrix.json` (359 lines), `tests/test_doc_web_bundle_contract.py` (329 lines), `tests/test_doc_web_cli_contract.py` (243 lines), `modules/extract/unstructured_docx_intake_v1/main.py` (215 lines), and `docs/stories.md` (183 lines). Prefer new focused fixture generators/tests over inflating the builder or contract surfaces casually.
- **Decision context**: reviewed `docs/ideal.md`, `docs/build-map.md`, ADR-002, Scout 011, Story 172, Story 174, `tests/fixtures/formats/_coverage-matrix.json`, and `testdata/README.md`. No separate ADR currently governs office-family split logic, which is why this story must make that planning decision explicit.

## Files to Modify

- `testdata/README.md` — document the widened DOCX fixture set and regeneration commands (63 lines)
- `testdata/generate_docx_fixture.py` — extend or refactor the existing DOCX fixture generator if the widened surface can reuse it (57 lines)
- `testdata/` new source and generated fixture files — add broader repo-owned or reproducible DOCX proof inputs (new files)
- `configs/recipes/recipe-docx-html-mvp.yaml` — only if widened fixtures expose a real recipe-parameter or wiring gap (25 lines)
- `modules/extract/unstructured_docx_intake_v1/main.py` — only if widened fixtures expose a DOCX intake gap that remains inside the maintained claim (215 lines)
- `modules/transform/docx_elements_to_bundle_v1/main.py` — only if widened fixtures expose a bundle/provenance rendering gap that the story chooses to support now (446 lines)
- `tests/test_docx_intake_recipe.py` — widen recipe proof coverage beyond `docx-mini` (81 lines)
- `tests/test_doc_web_cli_contract.py` — extend clean-env DOCX smoke only if the widened fixture matrix needs runtime-surface proof (243 lines)
- `tests/test_doc_web_bundle_contract.py` — extend only if widened DOCX features force contract changes (329 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — update DOCX / office-family truth surfaces honestly (359 lines)
- `docs/build-map.md` — update Gap 3, Gap 5, and the explicit office next-action wording after the sequencing decision lands (581 lines)
- `docs/stories.md` — keep the story index and any newly created follow-up story references aligned (183 lines)

## Redundancy / Removal Targets

- Ambiguous build-map wording that treats "office documents" as one vague future area after this story makes the split/stay-together decision explicit
- Any widened DOCX claim in docs that still implies `docx-mini` alone is sufficient evidence
- Temporary exploratory fixture notes or ad hoc comparison commands if the widened proof surface lands as reproducible checked-in generators/tests

## Notes

- The natural widened target is not "all of Word." It is "enough diverse repo-owned DOCX evidence to know what the maintained lane really supports today."
- Prefer repo-owned or reproducibly generated DOCX fixtures over local-only office documents so widened proof can be rerun in future checkouts.
- The `xlsx` / `pptx` decision should stay evidence-backed. If the local substrate and provenance shape are clearly divergent, split them. If they share one realistic intake/provenance seam, keep them combined. Do not pick based on naming aesthetics alone.
- This story does not assume DOCX can move to `passing`. It may stay `has fixture` if the widened proof still shows major unsupported feature classes or insufficient breadth for a passing claim.

### Proof Commands

- `python testdata/generate_docx_fixture.py --source testdata/docx-structured.source.json --output testdata/docx-structured.docx`
- `python testdata/generate_docx_fixture.py --source testdata/docx-page-break.source.json --output testdata/docx-page-break.docx`
- `python -m pytest tests/test_docx_intake_recipe.py -q`
- `python -m pytest tests/test_doc_web_cli_contract.py -q -k docx_extra_supports_repo_owned_docx_smoke`
- `python driver.py --recipe configs/recipes/recipe-docx-html-mvp.yaml --input-docx testdata/docx-mini.docx --run-id story175-docx-mini-r1 --force`
- `python driver.py --recipe configs/recipes/recipe-docx-html-mvp.yaml --input-docx testdata/docx-structured.docx --run-id story175-docx-structured-r1 --force`
- `python driver.py --recipe configs/recipes/recipe-docx-html-mvp.yaml --input-docx testdata/docx-page-break.docx --run-id story175-docx-page-break-r1 --force`

## Plan

### Substrate Conclusion

- This story is buildable now.
- The maintained DOCX lane already exists in code and docs:
  - `configs/recipes/recipe-docx-html-mvp.yaml`
  - `modules/extract/unstructured_docx_intake_v1/main.py`
  - `modules/transform/docx_elements_to_bundle_v1/main.py`
  - `driver.py --input-docx`
  - `tests/test_docx_intake_recipe.py`
  - `tests/test_doc_web_cli_contract.py`
- The missing `xlsx` / `pptx` substrate is explicit and acceptable:
  - coverage matrix rows exist
  - no recipe/module/test surface exists yet
  - this story only needs a measured sequencing decision, not implementation

### Baseline (Current Pass)

- `python -m pytest tests/test_docx_intake_recipe.py -q` → `2 passed in 4.92s`
- `python -m pytest tests/test_doc_web_cli_contract.py -q -k docx_extra_supports_repo_owned_docx_smoke` → `1 passed, 4 deselected in 50.71s`
- `rg -n 'openpyxl|python-pptx|pptx|xlsx|unstructured\.partition\.(pptx|xlsx)' ...` over repo code/docs shows `xlsx` / `pptx` only in build-map, coverage-matrix, and story/planning docs. No maintained recipe, module, dependency declaration, or test surface exists yet for either format family.

### Eval-First Gate

1. Expand the DOCX fixture matrix before changing code.
2. Run the current maintained DOCX lane on every widened fixture.
3. Inspect extraction, bundle, and provenance artifacts for each feature class.
4. Only then decide whether the widened supported slice needs code changes or just truth-surface updates.
5. Separately inspect the real local `xlsx` / `pptx` substrate and record whether their likely seams are shared or divergent.

### Exploration Findings

- The current DOCX seam is still intentionally narrow, and the temporary richer DOCX probe exposed real boundary behavior:
  - ordered list items remain promising: `partition_docx()` emits them as `ListItem`
  - explicit page breaks are currently risky: a paragraph containing a page break was emitted as a top-level `Title`
  - embedded figure + caption behavior is not yet trustworthy for the maintained claim: the probe emitted the caption as `Title` and did not emit a `Figure` element for the inserted image
  - tables remain promising: the probe still emitted a `Table` with `text_as_html`
- Spreadsheet and slide substrate are materially divergent today:
  - `openpyxl` imports successfully and `unstructured.partition.xlsx` is available in the current environment
  - a minimal XLSX probe produced one `Table` element with `text_as_html`, which is a real downstream seam candidate
  - `python-pptx` is missing and `unstructured.partition.pptx` currently fails with `ModuleNotFoundError: No module named 'pptx'`
- Planning implication: the likely honest next office shape is **split follow-ups**, not one combined `xlsx`/`pptx` story, unless implementation uncovers a stronger shared seam than the current environment suggests.

### Implementation Outline

1. Add the widened DOCX proof fixtures and regeneration docs.
   - Recommended fixture matrix discovered during exploration:
     - a likely-supported slice: repeated heading-based sections, longer prose, simple bullet lists, and repeated simple tables that should stay inside the current maintained claim
     - a likely-boundary slice: explicit manual page breaks, expected to tighten the claim boundary even if the story chooses not to support page-linked semantics now
   - Done looks like: at least three diverse DOCX fixtures total exist, including `docx-mini`.

2. Re-measure the current maintained DOCX lane with no code changes first.
   - Done looks like: each fixture has fresh artifact evidence under `output/runs/` plus manual inspection notes.

3. Land only the smallest honest DOCX fixes needed for the supported-now subset.
   - Done looks like: failing feature classes are either fixed locally or explicitly excluded from the maintained claim.

4. Add focused proof coverage.
   - Done looks like: the widened DOCX matrix can be rerun through targeted tests and narrow driver proofs without relying on memory.

5. Record the office-family sequencing decision and align planning surfaces.
   - Current recommendation from exploration: split the next office follow-up into `xlsx` and `pptx` stories unless a stronger shared seam is discovered during implementation.
   - Done looks like: the build map and backlog clearly say whether `xlsx` / `pptx` remain one follow-up or split into separate ones.

### Impact Analysis

- **Primary blast radius:** DOCX fixture generation, DOCX proof tests, DOCX bundle/intake modules, and planning truth surfaces.
- **Secondary blast radius:** `schemas.py` and runtime-contract tests only if widened DOCX features truly need new stamped fields or bundle semantics.
- **Main risks:** over-claiming DOCX support after widening only slightly; conflating DOCX proof expansion with `xlsx` / `pptx` implementation; or inflating `docx_elements_to_bundle_v1` past a maintainable size when a narrower helper/test would suffice.
- **Structural health:** keep the maintained DOCX lane explicit and bounded. Use the widened fixture matrix to learn where the line is, not to justify a generic "office docs" abstraction before the repo has evidence.
- **Human-approval blocker:** none. The user explicitly approved the widened recommendation.
- **Relative effort:** M

### What Done Looks Like

- The repo has more than one narrow DOCX proof point, and the claimed DOCX slice is explicit.
- Every widened DOCX feature class is either supported with fresh artifacts or explicitly excluded from the maintained claim.
- The build map and backlog no longer leave `xlsx` / `pptx` sequencing implicit.

## Work Log

20260331-0758 — story created from triage: turned Build Map Next Action 1 into a buildable `Pending` story after verifying the current office-input substrate. Evidence: `docs/build-map.md` still calls for widening DOCX proof and deciding whether `xlsx` / `pptx` should split; `tests/fixtures/formats/_coverage-matrix.json` still lists `docx` as `has-fixture` and `xlsx` / `pptx` as `untested`; `configs/recipes/recipe-docx-html-mvp.yaml`, `modules/extract/unstructured_docx_intake_v1/main.py`, `modules/transform/docx_elements_to_bundle_v1/main.py`, `driver.py --input-docx`, and the DOCX smoke tests prove the maintained DOCX lane already exists; and no recipe/module/test substrate exists yet for `xlsx` or `pptx`. Next step: `/build-story` should choose the widened DOCX fixture matrix, rerun the current lane on it before writing code, and then decide the explicit office-family follow-up shape from measured local evidence.
20260331-0805 — build-story exploration and baseline: kept the widened scope because the current-pass substrate check still supports it. Evidence: `python -m pytest tests/test_docx_intake_recipe.py -q` returned `2 passed in 4.92s`; `python -m pytest tests/test_doc_web_cli_contract.py -q -k docx_extra_supports_repo_owned_docx_smoke` returned `1 passed, 4 deselected in 50.71s`; and a repo-wide `rg` for `xlsx` / `pptx` seams found only build-map / coverage / story mentions, with no maintained recipe, module, dependency, or test surface for either family. Result: the story remains honestly `Pending` because the DOCX widening path is real, while the `xlsx` / `pptx` portion remains a sequencing decision rather than a hidden implementation promise. Next step: human gate on the plan, then implementation can start by choosing the widened DOCX fixture matrix.
20260331-0815 — deeper code and substrate tracing: refined the likely proof matrix and office sequencing recommendation from temporary format probes. Evidence: `testdata/generate_docx_fixture.py` and `docx-mini.source.json` still generate only headings, paragraphs, bullets, and one simple table; a temporary richer DOCX probe run through `unstructured.partition.docx` emitted `ListItem` correctly for numbered items, but also misclassified a paragraph containing an explicit page break as `Title`, emitted the figure caption as `Title`, and did not emit a `Figure` element for the inserted image; the same probe still emitted a usable `Table`. Separate environment checks showed `openpyxl` and `unstructured.partition.xlsx` import successfully, and a minimal XLSX workbook probe emitted one `Table` element with `text_as_html`, while `python-pptx` and `unstructured.partition.pptx` both fail with `ModuleNotFoundError`. Result: the widened DOCX story should intentionally include one likely-supported fixture and one likely-boundary fixture, and the current evidence favors splitting `xlsx` and `pptx` into separate follow-up stories rather than keeping one combined office story. Next step: present the plan and this sequencing recommendation to the user for approval before any implementation code.
20260331-0833 — implemented the widened DOCX proof surface and made the office split explicit without changing the maintained runtime contract. Evidence: added repo-owned reproducible fixtures `testdata/docx-structured.source.json` / `testdata/docx-structured.docx` and `testdata/docx-page-break.source.json` / `testdata/docx-page-break.docx`, widened `testdata/generate_docx_fixture.py` to cover repeated simple tables plus explicit page-break authoring, expanded `tests/test_docx_intake_recipe.py` into a three-fixture matrix, updated truth surfaces in `testdata/README.md`, `tests/fixtures/formats/_coverage-matrix.json`, and `docs/build-map.md`, and created explicit split follow-up drafts at `docs/stories/story-176-maintained-xlsx-intake-lane.md` and `docs/stories/story-177-pptx-runtime-substrate-and-slide-intake-path.md`. Fresh focused verification passed: `python -m pytest tests/test_docx_intake_recipe.py -q` → `4 passed in 9.75s`; `python -m pytest tests/test_doc_web_cli_contract.py -q -k docx_extra_supports_repo_owned_docx_smoke` → `1 passed, 4 deselected in 51.00s`; `make lint` → pass; `make test` → `396 passed, 4 warnings in 106.87s`. Fresh driver proof after clearing stale bytecode succeeded for the widened matrix: `story175-docx-mini-r1`, `story175-docx-structured-r1`, and `story175-docx-page-break-r1` each produced final bundle outputs under `output/runs/`. Manual artifact inspection confirms the maintained slice widened honestly: `output/runs/story175-docx-structured-r1/01_unstructured_docx_intake_v1/elements.jsonl` carries `Title=4`, `NarrativeText=4`, `ListItem=6`, and `Table=2`; `output/runs/story175-docx-structured-r1/output/html/manifest.json` lists three chapter entries with `source_pages=[]` / `printed_pages=[]`; and `output/runs/story175-docx-page-break-r1/01_unstructured_docx_intake_v1/elements.jsonl` contains no `PageBreak` rows despite the authored manual break, while `output/runs/story175-docx-page-break-r1/output/html/provenance/blocks.jsonl` still anchors every block to stable `source_element_ids` with no fabricated page numbers. Result: the claimed maintained DOCX slice is now broader but still bounded to heading-based sections, longer prose, simple bullet lists, and simple tables; explicit page breaks are recorded as observed-only and remain outside the maintained claim. Schema checks also passed on the fresh artifacts via `python validate_artifact.py --schema doc_web_bundle_manifest_v1 --file output/runs/story175-docx-mini-r1/output/html/manifest.json`, `python validate_artifact.py --schema doc_web_provenance_block_v1 --file output/runs/story175-docx-mini-r1/output/html/provenance/blocks.jsonl`, `python validate_artifact.py --schema doc_web_bundle_manifest_v1 --file output/runs/story175-docx-structured-r1/output/html/manifest.json`, and `python validate_artifact.py --schema doc_web_provenance_block_v1 --file output/runs/story175-docx-page-break-r1/output/html/provenance/blocks.jsonl`. Next step: `/validate`, then `/mark-story-done` if the widened truth surfaces and artifact quality still look right on review.
20260331-0932 — story closed via `/mark-story-done` after fresh close-out validation. Evidence: this close-out pass re-ran `python -m pytest tests/test_docx_intake_recipe.py -q` (`4 passed in 11.32s`), `python -m pytest tests/test_doc_web_cli_contract.py -q -k docx_extra_supports_repo_owned_docx_smoke` (`1 passed, 4 deselected in 50.94s`), `make lint`, and `make test` (`396 passed, 4 warnings in 105.62s`). Fresh validation driver proofs also completed under `output/runs/validate-story175-docx-mini-r1/`, `output/runs/validate-story175-docx-structured-r1/`, and `output/runs/validate-story175-docx-page-break-r1/`. Manual inspection reconfirmed the widened maintained slice and the bounded page-break claim: `output/runs/validate-story175-docx-structured-r1/output/html/manifest.json` lists three chapter entries with empty `source_pages` / `printed_pages`, `output/runs/validate-story175-docx-page-break-r1/01_unstructured_docx_intake_v1/elements.jsonl` still contains no `PageBreak` rows, and `output/runs/validate-story175-docx-page-break-r1/output/html/provenance/blocks.jsonl` still carries stable `source_element_ids` with no fabricated page numbers. Schema validation passed again via `python validate_artifact.py --schema doc_web_bundle_manifest_v1 --file output/runs/validate-story175-docx-structured-r1/output/html/manifest.json` and `python validate_artifact.py --schema doc_web_provenance_block_v1 --file output/runs/validate-story175-docx-page-break-r1/output/html/provenance/blocks.jsonl`. Next step: `/check-in-diff`.
