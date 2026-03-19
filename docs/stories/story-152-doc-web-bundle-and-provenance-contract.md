# Story 152 — `doc-web` Bundle and Provenance Contract

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Traceability is the Product, Dossier-ready output
**Spec Refs**: spec:6 (Validation, Provenance & Export), spec:7 (Graduation & Dossier Handoff)
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/notes/standalone-dossier-intake-runtime-plan.md`, `README.md`, `docs/spec.md`
**Depends On**: Story 151

## Goal

Define the first formal `doc-web` bundle contract so the runtime boundary stops being implicit. The current Onward HTML output proves that codex-forge can emit a structural website, but the final contract is still too loose: `chapter_html_manifest_v1` is not formalized in `schemas.py`, and provenance is too coarse for Dossier's citation requirement. This story should define the bundle layout, manifest schema, provenance sidecar schema, and the default paragraph-level block contract that later extraction and Dossier integration work can implement against.

## Acceptance Criteria

- [x] A build-ready contract document or schema package defines the first `doc-web` bundle layout, including reading order, chapter/page files, assets, and machine-readable manifests.
- [x] A provenance contract is defined for paragraph-level default blocks, including stable block IDs and the minimum required source mapping fields needed for Dossier citation/open-original behavior.
- [x] The current codex-forge output surfaces are mapped clearly into `kept`, `renamed`, `superseded`, or `missing` relative to the new `doc-web` contract, including the fate of `chapter_html_manifest_v1`.
- [x] At least one real Onward output slice or fixture is identified as the initial golden example for validating the contract.

## Out of Scope

- Big-bang extraction of the full codex-forge pipeline into this repo
- Dossier implementation work
- Themed website presentation, editorial polish, or publish UX
- Reworking unrelated OCR or genealogy extraction logic unless contract gaps demand it

## Approach Evaluation

- **Simplification baseline**: First inspect whether the current Onward HTML plus manifest already satisfy most of the contract with only schema formalization and a provenance sidecar addition. If so, prefer formalizing the existing shape over inventing a fresh bundle unnecessarily.
- **AI-only**: An LLM can draft candidate schema names and field groupings, but it cannot decide the contract responsibly without checking the real emitted artifacts and current schema stamping behavior.
- **Hybrid**: Inspect the current outputs and schemas, then use AI to synthesize the cleanest bundle/provenance contract with explicit migration notes. This is the leading candidate because the work is part artifact analysis and part contract design.
- **Pure code**: Define schemas directly in `schemas.py` without first writing down the contract and mapping current fields to their future names. Fastest path to code, but risks baking in a sloppy first contract.
- **Repo constraints / prior decisions**: ADR-002 already settled the boundary: structural website bundle, block-level provenance, paragraph-level default citation unit, and no codex-forge-as-runtime dependency. The new contract must support tagged release pins and downstream contract tests.
- **Existing patterns to reuse**: `modules/build/build_chapter_html_v1`, current `chapters_manifest.jsonl` output, `schemas.py`, `UnstructuredElement` provenance patterns, and the extraction inventory in `docs/notes/standalone-dossier-intake-runtime-plan.md`.
- **Eval**: The deciding evidence is whether a real Onward output slice can be losslessly described by the proposed bundle/provenance schema without hand-waving missing fields or relying on chapter-only provenance.

## Tasks

- [x] Inspect the current HTML output bundle and list the exact fields/files that already align with the accepted `doc-web` contract.
- [x] Define the first `doc-web` bundle schema:
  - bundle layout
  - manifest fields
  - reading-order/navigation representation
  - assets expectations
- [x] Define the first provenance schema:
  - paragraph-level default blocks
  - stable block ID format
  - required source reference fields
  - optional location/confidence fields
- [x] Decide what happens to current codex-forge surfaces:
  - `chapter_html_manifest_v1`
  - inline nav
  - any inline provenance or page-range fields
- [x] Select or create the first golden fixture set for validating the contract in later `doc-web` and Dossier work
- [x] Add machine-readable contract validation for the frozen v1 shape:
  - schema classes and validator wiring
  - focused contract tests and/or example fixture assertions against the chosen golden slice
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] This remained docs/schema-first, so referenced output artifacts and schema mappings were verified manually against the committed Onward reviewed slice
  - [x] `schemas.py` changed, and `make test` plus `make lint` both passed
  - [x] Pipeline behavior did not change, so no `driver.py` rerun was required for Story 152
  - [x] Agent tooling did not change, so `make skills-check` was not required
- [x] Evals and goldens were reused rather than changed materially, so `/improve-eval` and `docs/evals/registry.yaml` updates were not required
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: contract carries enough provenance for Dossier citation and open-original behavior
  - [x] T1 — AI-First: formalize the smallest contract that matches real outputs instead of overbuilding a speculative schema
  - [x] T2 — Eval Before Build: validate the contract against real emitted artifacts before freezing it
  - [x] T3 — Fidelity: no required source-location signal is dropped for convenience
  - [x] T4 — Modular: contract is generic enough for `doc-web`, not Onward-only
  - [x] T5 — Inspect Artifacts: manually inspect real HTML and manifest outputs while designing the contract

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story status updated to Done with evidence recorded in the work log

## Architectural Fit

- **Owning module / area**: Contract/schema layer first. `modules/build/build_chapter_html_v1` and the committed Story 149 reviewed slice are reference surfaces for this story, not the intended primary edit targets unless schema feasibility proves otherwise.
- **Data contracts / schemas**: This story should formalize dedicated `doc-web` bundle/provenance schema classes and explicitly mark the fate of the implicit `chapter_html_manifest_v1` shape (`kept`, `renamed`, `superseded`, or `missing` by field/surface).
- **File sizes**: `schemas.py` is 964 lines, `validate_artifact.py` is small, and `modules/build/build_chapter_html_v1/main.py` is 1345 lines. Keep Story 152 contract-focused and avoid pulling emitter changes forward from Story 153.
- **Decision context**: ADR-002 is the authoritative boundary decision. Story 151, the extraction-plan note, and the committed Story 149 reviewed slice provide the local migration and validation context.

## Files to Modify

- /Users/cam/.codex/worktrees/adef/doc-web/docs/doc-web-bundle-contract.md — freeze the human-readable v1 bundle/provenance contract and current-surface mapping (new file)
- /Users/cam/.codex/worktrees/adef/doc-web/schemas.py — add explicit `doc-web` bundle/provenance schema classes and transitional manifest status notes
- /Users/cam/.codex/worktrees/adef/doc-web/validate_artifact.py — wire the new contract schemas into artifact validation
- /Users/cam/.codex/worktrees/adef/doc-web/tests/test_doc_web_bundle_contract.py — assert the committed Onward golden slice and contract examples map cleanly to the frozen v1 contract (new file)
- /Users/cam/.codex/worktrees/adef/doc-web/docs/notes/standalone-dossier-intake-runtime-plan.md — update extraction inventory with the final `kept` / `renamed` / `superseded` / `missing` mapping
- /Users/cam/.codex/worktrees/adef/doc-web/docs/stories/story-152-doc-web-bundle-and-provenance-contract.md — keep the story current as the contract decisions land

## Redundancy / Removal Targets

- Implicit use of `chapter_html_manifest_v1` as an undocumented final contract
- Any future docs that describe `doc-web` as "just HTML" without the manifest/provenance bundle
- Any stale note that keeps provenance at chapter-only granularity after this contract lands

## Notes

- Default first citation unit: paragraph-level block provenance, not sentence-level by default.
- Navigation is part of the structural contract, not an optional presentation flourish.
- Favor sidecar provenance for heavy fields and keep inline HTML provenance hooks light.
- Use `benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/` as the baseline golden slice unless exploration during implementation proves it cannot exercise the contract honestly.

## Plan

### Baseline / Eval

- Use the committed Story 149 reviewed slice as the first contract golden: `benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/manifest.json`, `chapters_manifest_regression.jsonl`, and selected reviewed chapter HTML files.
- Baseline result from exploration:
  - current structural bundle shape is real (`33` manifest rows = `24` chapters + `9` fallback pages)
  - formal schema coverage for `chapter_html_manifest_v1` is `0`, because `schemas.py` and `validate_artifact.py` do not define it
  - paragraph-level provenance coverage is `0`, because the reviewed HTML has no stable block IDs or source mapping fields
- Success test for Story 152: the frozen v1 contract can describe the reviewed slice without ambiguous `TBD` gaps, and the machine-readable schemas/tests make the missing provenance surfaces explicit instead of implicit.

### Implementation Order

1. Freeze the human-readable v1 contract in `/Users/cam/.codex/worktrees/adef/doc-web/docs/doc-web-bundle-contract.md`.
   - Define bundle layout, required files, reading-order source of truth, asset expectations, paragraph-level block unit, and inline-vs-sidecar provenance policy.
   - Done looks like: the committed Onward slice maps file-by-file and field-by-field to the contract with no hand-waving.
2. Formalize the machine-readable contract in `/Users/cam/.codex/worktrees/adef/doc-web/schemas.py` and `/Users/cam/.codex/worktrees/adef/doc-web/validate_artifact.py`.
   - Add dedicated schema classes for the bundle manifest, content-entry rows or equivalent, and paragraph-level provenance sidecars.
   - Decide the fate of `chapter_html_manifest_v1` explicitly instead of silently treating it as the final contract.
   - Done looks like: validator support exists for the new schemas, and the transitional status of the current manifest is documented.
3. Add focused contract tests and fixture assertions in `/Users/cam/.codex/worktrees/adef/doc-web/tests/test_doc_web_bundle_contract.py`.
   - Validate the frozen contract against the committed Story 149 slice plus any tiny example provenance fixtures needed to exercise the new sidecar schema before emitter work lands.
   - Done looks like: tests prove the reviewed slice satisfies the frozen surfaces that already exist and clearly identify the missing provenance surfaces Story 153 must emit.
4. Update migration and story tracking docs.
   - Update `/Users/cam/.codex/worktrees/adef/doc-web/docs/notes/standalone-dossier-intake-runtime-plan.md`, this story, and `/Users/cam/.codex/worktrees/adef/doc-web/docs/stories.md`.
   - Done looks like: `kept` / `renamed` / `superseded` / `missing` mappings, golden fixture path, and current status all match the contract.

### Impact / Risk

- Files at risk once the contract lands: `/Users/cam/.codex/worktrees/adef/doc-web/modules/build/build_chapter_html_v1/main.py`, `/Users/cam/.codex/worktrees/adef/doc-web/tests/test_run_registry.py`, `/Users/cam/.codex/worktrees/adef/doc-web/modules/validate/validate_onward_genealogy_consistency_v1/main.py`, and follow-up Stories 153-154, because they currently assume the implicit row-based manifest and chapter/page provenance fields.
- No new dependency or repo-boundary blocker is expected. The main approval choice is whether v1 should keep the current flat bundle layout (`index.html`, `chapter-*.html`, `page-*.html`, `images/`) and treat `chapter_html_manifest_v1` as a superseded transitional surface instead of renaming it in place.
- Small scope expansion folded into this story: add explicit schema validation and focused contract tests alongside the contract document. Rationale: a docs-only contract would not protect against schema stamping or later drift.

## Work Log

20260318-2337 — story created: captured the first implementation slice implied by ADR-002. The contract is the next hard dependency because extraction and Dossier integration both need a stable bundle/provenance shape before code can move safely.
20260319-1130 — exploration and planning: traced `docs/ideal.md`, `docs/spec.md` (`spec:6`, `spec:7`), Story 151, ADR-002, the extraction-plan note, `schemas.py`, `validate_artifact.py`, `modules/build/build_chapter_html_v1/main.py`, builder tests, and the committed Story 149 reviewed slice. Result: the current output already proves a structural bundle (`index.html`, chapter/page HTML, nav shell, images, row manifest), but the runtime boundary is still implicit because `chapter_html_manifest_v1` has no schema class/validator wiring and the reviewed HTML has no stable paragraph/block provenance hooks. Evidence: `benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/chapters_manifest_regression.jsonl` shows `33` entries with chapter/page coverage, while `validate_artifact.py` contains no `chapter_html_manifest_v1` mapping and reviewed chapter HTML files contain no stable block IDs or source references. Patterns to follow: formalize the existing shape where possible, use the committed reviewed slice as the first golden, and keep Story 152 contract-focused rather than pulling emitter changes forward. Surprise: the story still had stale worktree-specific file paths, the local worktree has no live `output/runs/`, and the committed reviewed slice is therefore the reliable baseline for this planning pass. Next: human approval on the contract-first plan, especially the decision to keep the flat bundle layout and supersede rather than rename `chapter_html_manifest_v1` in place.
20260319-1149 — contract package implemented: added `docs/doc-web-bundle-contract.md`, formalized transitional schema `chapter_html_manifest_v1`, added new contract schemas `doc_web_bundle_manifest_v1` and `doc_web_provenance_block_v1`, extended `validate_artifact.py` to validate JSON as well as JSONL, and added focused tests in `tests/test_doc_web_bundle_contract.py`. Updated related docs (`README.md`, `docs/notes/standalone-dossier-intake-runtime-plan.md`, Stories 153-154) so the frozen contract is now the explicit reference point for the next seam and handoff stories. Manual artifact inspection still grounded the contract in the committed Onward reviewed slice: `chapters_manifest_regression.jsonl` row 19 shows `ARTHUR L'HEUREUX` covering printed pages `19-28` with `source_pages` `28-37`, while reviewed HTML files `chapter-010.html` and `chapter-022.html` confirm that inline navigation already exists but stable `id=` anchors do not, which is why the new block-sidecar contract remains Story 153 work rather than a fake emitted surface today. Verification: targeted pytest (`tests/test_doc_web_bundle_contract.py`, `tests/test_run_registry.py`, `tests/test_instrumentation_schema.py`) passed; `make lint` passed; `make test` passed (`632 passed, 6 skipped`). No pipeline behavior changed, so a `driver.py` rerun was not required for this docs/schema-only story. Result: Story 152 is complete, and the runtime boundary is now explicit enough for Story 153 to implement against and Story 154 to hand off.
20260319-1230 — validation follow-up: `/validate` caught that the new bundle schema still accepted manifests that violated the written contract, including absolute paths, non-contiguous `order` values, and prev/next links that did not match `reading_order`. Tightened `DocWebBundleManifest` and `DocWebBundleEntry` so the contract now enforces bundle-root HTML paths, exact `index.html` and `provenance/blocks.jsonl` locations, contiguous `1..N` entry order, and reading-order-adjacent navigation links. Added negative tests plus a failing-CLI assertion in `tests/test_doc_web_bundle_contract.py` so the validator now rejects these malformed manifests instead of only covering happy paths. Next: rerun targeted pytest, `make lint`, and `make test`, then keep Story 152 closed only if those checks stay green.
20260319-1237 — post-validation hardening verified: reran targeted contract/schema checks (`20 passed`), `make lint`, and the full pytest suite (`636 passed, 6 skipped`). The originally reported hole is now closed: local repro manifests with absolute paths, off-sequence `order`, or non-adjacent/self-looping navigation now fail schema validation instead of passing silently. This restores alignment between the written contract in `docs/doc-web-bundle-contract.md` and the machine-readable enforcement in `schemas.py` / `validate_artifact.py`, so Story 152 can stay `Done` with evidence.
