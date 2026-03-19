# Story 153 — Extract `doc-web` Bundle Emitter

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #5 (Structure), Requirement #7 (Export), Dossier-ready output, Graduate, don't accumulate
**Spec Refs**: spec:6 (Validation, Provenance & Export), spec:7 (Graduation & Dossier Handoff)
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/doc-web-bundle-contract.md`, `docs/notes/standalone-dossier-intake-runtime-plan.md`, Story 152
**Depends On**: Story 152

## Goal

Extract the first real `doc-web` code seam from codex-forge by splitting the generic bundle-emission path out of `build_chapter_html_v1`. The current builder already proves the output shape, but it still mixes structural website emission with embedded CSS, image publishing details, and document-specific output shaping. This story should isolate the generic emitter so that later extraction into `doc-web` is a clean move rather than a blind copy of a large mixed-responsibility module.

## Acceptance Criteria

- [x] A generic bundle-emission seam is extracted from the current `build_chapter_html_v1` path, with responsibilities clearly separated between structural output and presentation-wrapper helper behavior.
- [x] The accepted `doc-web` contract from Story 152 is implemented or enforced at the seam so the emitter is no longer relying on undocumented manifest/output behavior.
- [x] A real `driver.py` run proves the refactored codex-forge path still emits the current maintained Onward structural website bundle behavior in `output/runs/` without introducing emitter-specific regressions, and those artifacts are manually inspected.
- [x] The story names what should move directly into the future `doc-web` repo versus what should remain temporarily in codex-forge.

## Out of Scope

- Building the full standalone `doc-web` repo
- Dossier-side integration code
- Themed website styling or publish UX
- Reworking unrelated OCR or Onward consistency logic unless the emitter seam exposes a contract bug

## Approach Evaluation

- **Simplification baseline**: Check whether the current builder can already be split by extracting pure helper functions and wrapper boundaries, without moving files across repos yet. If so, prefer seam extraction over an immediate repo bootstrap.
- **AI-only**: An LLM can suggest refactor boundaries, but the actual seam must be proven against the real recipe outputs and schema stamping rules.
- **Hybrid**: Use AI to propose ownership boundaries inside `build_chapter_html_v1`, then verify them against the real emitted artifacts and the accepted contract. This is the leading candidate.
- **Pure code**: Copy the current builder wholesale into `doc-web` and sort it out later. Fastest mechanically, but directly contradicts the accepted seam-first extraction strategy.
- **Repo constraints / prior decisions**: ADR-002 explicitly rejected a big-bang repo move. Story 152 should freeze the contract first. `build_chapter_html_v1` is 1345 lines and already mixes structural and wrapper responsibilities.
- **Existing patterns to reuse**: current HTML builder helpers, current image/manifest publishing flow, and the contract schema from Story 152.
- **Eval**: The deciding evidence is a real Onward build after the refactor, plus manual comparison showing no new emitter-specific regression within the current maintained reuse-based lane.

## Tasks

- [x] Identify and document the responsibility split inside `build_chapter_html_v1`:
  - generic bundle emission
  - nav/read-order wiring
  - asset publishing
  - presentation-wrapper helper behavior
- [x] Refactor the current builder so the generic emitter seam is isolated behind stable inputs and outputs
- [x] Align the refactored seam with the Story 152 contract schemas
- [x] Prove the seam with a real `driver.py` run and manual artifact inspection
- [x] Record what code is now ready to move into `doc-web` directly versus what still requires refactor
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] Clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect the emitted structural website bundle
  - [x] If agent tooling changed: `make skills-check` (not needed; no agent tooling changed)
- [x] If evals or goldens changed materially: run `/improve-eval` and update `docs/evals/registry.yaml` (not needed; no eval or golden contract changed materially)
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: refactor preserves provenance fields and does not make the final contract more opaque
  - [x] T1 — AI-First: do not replace AI extraction with deterministic overfit while isolating the emitter seam
  - [x] T2 — Eval Before Build: compare refactored outputs against the reviewed structural website slice and the current maintained reuse-lane validator band
  - [x] T3 — Fidelity: no new emitter-specific semantic regression in the emitted website bundle relative to the current maintained reuse lane
  - [x] T4 — Modular: seam extraction reduces coupling instead of moving a monolith unchanged
  - [x] T5 — Inspect Artifacts: manually inspect the rebuilt HTML and manifest outputs

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done after validation follow-up narrowed the claim to the maintained no-emitter-regression slice that was actually proven

## Architectural Fit

- **Owning module / area**: `modules/build/build_chapter_html_v1` is the primary seam owner, with `schemas.py` and current recipe wiring as contract surfaces.
- **Data contracts / schemas**: Any new bundle/provenance fields must be added to `schemas.py` before the stamped artifacts can preserve them.
- **File sizes**: `modules/build/build_chapter_html_v1/main.py` is 1345 lines and `schemas.py` is 964 lines. Keep edits surgical and resist expanding the builder while trying to extract it.
- **Decision context**: ADR-002 settled seam-first extraction. Story 152 should define the contract before this story starts implementation.

## Files to Modify

- /Users/cam/.codex/worktrees/cdb6/codex-forge/modules/build/build_chapter_html_v1/main.py — extract the generic bundle-emission seam from the mixed builder (1345 lines)
- /Users/cam/.codex/worktrees/cdb6/codex-forge/schemas.py — preserve any newly formalized bundle/provenance fields during stamping (964 lines)
- /Users/cam/.codex/worktrees/cdb6/codex-forge/configs/recipes/recipe-onward-images-html-mvp.yaml — update wiring only if the seam extraction changes stage parameters or outputs (192 lines)
- /Users/cam/.codex/worktrees/cdb6/codex-forge/docs/stories/story-153-extract-doc-web-bundle-emitter.md — keep the story current as the seam lands

## Redundancy / Removal Targets

- Any mixed helper inside `build_chapter_html_v1` that only exists because structural and presentation responsibilities are coupled
- Any doc text claiming the current builder is ready to copy wholesale into `doc-web`

## Notes

- The goal is not "extract a pretty HTML generator." The goal is "extract the structural website emitter seam."
- Keep the codex-forge path working while the seam is isolated; `doc-web` repo creation can happen afterward.

## Plan

### Baseline / Eval

- Use the maintained regression recipe in `/Users/cam/.codex/worktrees/cdb6/codex-forge/configs/recipes/onward-genealogy-build-regression.yaml` as the primary seam proof, because it reuses the known-good Story 140 / 143 artifacts and already has a blessed reviewed slice to compare against.
- Baseline result from exploration:
  - `build_chapter_html_v1` currently emits only the transitional `chapter_html_manifest_v1` rows plus wrapped HTML files under `output/html/`; it does **not** emit `manifest.json` or `provenance/blocks.jsonl`.
  - `build_chapter_html_v1` still mixes at least four concerns in one file: page preparation, chapter segmentation, asset publishing, and final bundle writing/presentation wrapping.
  - `page_html_v1` inputs do not carry real upstream `element_ids`, so honest block provenance cannot be passed through directly; the existing `html_to_blocks_v1` parser pattern is the best local source for stable block ordinals at the current seam.
  - `validate_artifact.py` and `schemas.py` in the target `codex-forge` worktree still do not define the Story 152 contract schemas, so the current seam remains undocumented in code.
  - The maintained reuse-based regression lane has moved on since Story 149. For the current codebase, Story 144 documents the chapter-first validator's expected band as `flagged_genealogy_chapters=5` and `strong_rerun_candidate_page_count=6`; Story 153's job is to preserve that current behavior while adding the explicit bundle/provenance contract, not to force this older reuse lane back to the historical Story 149 `0`-flag slice.
- Success test for Story 153:
  - a refactored emitter path writes the transitional chapter manifest **and** the first `doc-web` runtime bundle surfaces (`manifest.json`, `provenance/blocks.jsonl`, stable block ids in emitted HTML),
  - those new surfaces validate against the Story 152 contract schemas in `codex-forge`,
  - and the maintained Onward regression run still matches the current maintained structural HTML bar for this recipe without introducing emitter-specific failures.

### Implementation Order

1. Extract the generic bundle-emission owner in `/Users/cam/.codex/worktrees/cdb6/codex-forge/modules/common/` and narrow `/Users/cam/.codex/worktrees/cdb6/codex-forge/modules/build/build_chapter_html_v1/main.py` to chapter assembly plus build-local glue.
   - Introduce a shared helper for bundle entries, navigation wiring, index generation, HTML wrapping hooks, bundle-manifest writing, and provenance sidecar writing.
   - Keep recipe-specific preparation in the builder: chapter segmentation, image attachment, Onward genealogy merge knob, and any build-local fallback-page logic that is not part of the reusable emitter contract.
   - Done looks like: the builder no longer hand-builds manifest rows, index entries, and file writes inline; those move behind a stable emitter call with explicit inputs.
2. Preserve source-block provenance through the seam instead of inventing it after the fact.
   - Annotate prepared page-level blocks with stable source block ids using the existing `html_to_blocks_v1` ordinal pattern (`p{page_number:03d}-b{order}` or equivalent), carry those ids across page-break paragraph stitching, and emit final block ids (`blk-<entry-id>-<4-digit ordinal>`) plus `provenance/blocks.jsonl`.
   - Keep inline HTML hooks light: final emitted blocks keep stable `id=` anchors, while heavy provenance stays in the sidecar.
   - Done looks like: each emitted chapter/page document has stable block ids and the sidecar rows name the matching `entry_id`, `block_id`, source page, source printed page when available, and source block ids used to derive the output block.
3. Adopt and enforce the canonical `doc-web` contract at the current `codex-forge` seam in `/Users/cam/.codex/worktrees/cdb6/codex-forge/schemas.py` and `/Users/cam/.codex/worktrees/cdb6/codex-forge/validate_artifact.py`.
   - Add `chapter_html_manifest_v1`, `doc_web_bundle_manifest_v1`, and `doc_web_provenance_block_v1` schema classes and validator wiring in `codex-forge`, reusing the accepted contract semantics from this `doc-web` repo instead of inventing a second variant.
   - `doc-web` remains the canonical contract owner; `codex-forge` only implements a compatible transitional seam while the live emitter still lives there.
   - Decide whether `/Users/cam/.codex/worktrees/cdb6/codex-forge/modules/build/build_chapter_html_v1/module.yaml` should now declare the transitional row schema explicitly; only do that if stamping does not interfere with the refactored output path.
   - Done looks like: the new bundle surfaces can be validated mechanically in `codex-forge`, and the seam no longer relies on prose-only expectations.
4. Add focused regression coverage in `/Users/cam/.codex/worktrees/cdb6/codex-forge/tests/`.
   - Extend `/Users/cam/.codex/worktrees/cdb6/codex-forge/tests/test_build_chapter_html.py` or add a dedicated emitter test file to assert:
     - manifest/index/provenance sidecars are written,
     - block ids land in emitted HTML,
     - navigation/reading order stay aligned,
     - page-break paragraph stitching preserves combined source ids,
     - and the transitional `chapter_html_manifest_v1` output still reflects the same chapter/page ordering.
   - Add contract-validator tests for the new schema classes if they are not already covered by the builder tests.
   - Done looks like: targeted pytest catches both seam regressions and contract drift without requiring a full driver run for every iteration.
5. Run the maintained regression path and inspect real artifacts.
   - Clear stale `*.pyc`, run `python driver.py --recipe configs/recipes/onward-genealogy-build-regression.yaml --run-id <story153-run> --allow-run-id-reuse --force` in `/Users/cam/.codex/worktrees/cdb6/codex-forge`, then inspect the resulting `output/runs/<story153-run>/output/html/`, `manifest.json`, `provenance/blocks.jsonl`, and `04_build_chapter_html_v1/chapters_manifest_regression.jsonl`.
   - Compare reviewed hard-case chapters against `benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/`.
   - Done looks like: reviewed chapters remain healthy, the recipe stays within its current maintained validator band (`flagged_genealogy_chapters=5`, `strong_rerun_candidate_page_count=6`) rather than introducing new emitter-specific failures, and the new bundle/provenance artifacts are present and logically correct.
6. Update the migration documentation and this story with the new move/leave-behind split.
   - Record which helper/module code is now ready to move directly into `doc-web` and which builder-local logic remains temporarily in `codex-forge`.
   - Update the extraction inventory note if the seam changes what is considered ready-to-migrate.

### Impact / Risk

- **Small scope expansion folded into this story:** preserve source-block lineage through page-break stitching. Rationale: without this, Story 153 could emit `manifest.json` but still fake or omit the block provenance that ADR-002 and Story 152 explicitly require for the seam.
- **Files expected to change:** `/Users/cam/.codex/worktrees/cdb6/codex-forge/modules/build/build_chapter_html_v1/main.py`, a new shared emitter helper under `/Users/cam/.codex/worktrees/cdb6/codex-forge/modules/common/`, `/Users/cam/.codex/worktrees/cdb6/codex-forge/tests/test_build_chapter_html.py`, `/Users/cam/.codex/worktrees/cdb6/codex-forge/schemas.py`, `/Users/cam/.codex/worktrees/cdb6/codex-forge/validate_artifact.py`, and this story/doc trail.
- **Files at risk:** `/Users/cam/.codex/worktrees/cdb6/codex-forge/configs/recipes/onward-genealogy-build-regression.yaml`, `/Users/cam/.codex/worktrees/cdb6/codex-forge/configs/recipes/recipe-onward-images-html-mvp.yaml`, and any downstream validators or docs that still assume only `chapters_manifest.jsonl` exists.
- **Human-approval blocker:** none on architecture. The main execution risk is provenance correctness: success is falsified if the new sidecar cannot be explained from real source-page blocks or if the regression run reopens reviewed HTML failures.

## Move / Leave-Behind Split

- **Ready to move directly into `doc-web` later:** `/Users/cam/.codex/worktrees/cdb6/codex-forge/modules/common/doc_web_bundle_emitter.py` now owns the reusable structural bundle seam: HTML wrapping, navigation wiring, stable emitted block ids, bundle manifest writing, provenance sidecar writing, and the synthetic source-block annotation/restore helpers that make the current seam honest.
- **Temporary `codex-forge` glue that should stay here for now:** `/Users/cam/.codex/worktrees/cdb6/codex-forge/modules/build/build_chapter_html_v1/main.py` still owns chapter segmentation, page preparation, illustration attachment, page-break paragraph stitching, and recipe-local assembly.
- **Temporary `codex-forge` format logic that should stay here for now:** `/Users/cam/.codex/worktrees/cdb6/codex-forge/modules/common/onward_genealogy_html.py` remains an Onward-specific continuity/normalization helper, not part of the generic `doc-web` seam.
- **Current limitation that blocks a cleaner move:** the seam still synthesizes `source_element_ids` from top-level page HTML ordinals because `page_html_v1` does not yet carry canonical upstream element ids. That provenance strategy is honest and inspectable, but it is still build-local glue rather than the final ideal contract.

## Work Log

20260318-2337 — story created: captured the first real code-move seam implied by ADR-002. Story 152 should freeze the contract first, then this story can isolate the emitter without guessing at field names or output responsibilities.
20260319-1348 — exploration and planning: traced `docs/ideal.md`, `docs/spec.md` (`spec:6`, `spec:7`), ADR-002, Story 152, the extraction-plan note, the local Story 152 contract tests, and the target `codex-forge` seams in `modules/build/build_chapter_html_v1/main.py`, `tests/test_build_chapter_html.py`, `configs/recipes/onward-genealogy-build-regression.yaml`, `schemas.py`, and `validate_artifact.py`. Result: the structural seam is real, but `codex-forge` still emits only the transitional row manifest plus wrapped HTML; the accepted canonical `doc-web` manifest/provenance contract is defined here in `doc-web` but is not yet enforced at the current `codex-forge` seam, and current `page_html_v1` inputs do not carry real `element_ids`, so Story 153 needs a small coherent scope expansion to preserve synthetic source-block ids through build-time stitching instead of faking block provenance after the fact. Evidence: `build_chapter_html_v1` writes `chapter_html_manifest_v1` rows inline and no `manifest.json` / `provenance/blocks.jsonl`; `validate_artifact.py` in `codex-forge` has no `doc_web_*` schemas; the maintained regression recipe already exists and the committed reviewed slice at `benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/` remains the best baseline for post-refactor comparison. Patterns to follow: reuse the `html_to_blocks_v1` ordinal pattern for source block ids, keep the reusable emitter in a shared helper instead of enlarging the 1300+ line builder, and validate via the maintained regression recipe rather than fresh OCR. Surprise: the local `doc-web` repo has the accepted contract implementation, but the target `codex-forge` worktree still lacks those schema/validator surfaces, so the seam work must adopt that canonical contract there rather than redefining it. Next: human approval on the plan, especially the bundled scope expansion to preserve source-block lineage through page-break stitching.
20260319-1456 — implementation landed in `/Users/cam/.codex/worktrees/cdb6/codex-forge`: extracted `/Users/cam/.codex/worktrees/cdb6/codex-forge/modules/common/doc_web_bundle_emitter.py`, rewired `/Users/cam/.codex/worktrees/cdb6/codex-forge/modules/build/build_chapter_html_v1/main.py` to delegate bundle/index/provenance writing, added Story 152 schema/validator surfaces in `/Users/cam/.codex/worktrees/cdb6/codex-forge/schemas.py` and `/Users/cam/.codex/worktrees/cdb6/codex-forge/validate_artifact.py`, and extended regression coverage in `/Users/cam/.codex/worktrees/cdb6/codex-forge/tests/test_build_chapter_html.py` plus `/Users/cam/.codex/worktrees/cdb6/codex-forge/tests/test_doc_web_bundle_contract.py`. A real bug surfaced during validation: the genealogy merge path could preserve figure attrs while dropping caption provenance because `restore_top_level_source_block_ids` never advanced past already-preserved figure/table blocks. Fixed that ordering bug and added a CLI regression test for the exact `chapter-008.html` caption case (`Aerial photo of ranch buildings`, `Ranch house and barn`). Evidence: `python -m pytest tests/test_build_chapter_html.py tests/test_doc_web_bundle_contract.py tests/test_rerun_onward_genealogy_consistency_v1.py tests/test_table_rescue_onward_tables_v1.py -q` → `124 passed`; `make lint` → clean; `make test` → `638 passed, 6 skipped`.
20260319-2059 — real recipe validation and manual artifact inspection complete in `/Users/cam/.codex/worktrees/cdb6/codex-forge/output/runs/story153-doc-web-bundle-emitter-r1/`: `python driver.py --recipe configs/recipes/onward-genealogy-build-regression.yaml --run-id story153-doc-web-bundle-emitter-r1 --force` rebuilt `33` bundle entries and wrote the new runtime artifacts. Mechanical contract proof: `python validate_artifact.py --schema chapter_html_manifest_v1 --file .../04_build_chapter_html_v1/chapters_manifest_regression.jsonl` → `33 rows match`; `--schema doc_web_bundle_manifest_v1 --file .../output/html/manifest.json` → `1 rows match`; `--schema doc_web_provenance_block_v1 --file .../output/html/provenance/blocks.jsonl` → `557 rows match`. Manual inspection: [manifest.json](/Users/cam/.codex/worktrees/cdb6/codex-forge/output/runs/story153-doc-web-bundle-emitter-r1/output/html/manifest.json) contains `33` ordered entries from `page-001` through `chapter-024`; [blocks.jsonl](/Users/cam/.codex/worktrees/cdb6/codex-forge/output/runs/story153-doc-web-bundle-emitter-r1/output/html/provenance/blocks.jsonl) maps `blk-chapter-008-0004 -> ["p021-b2"] "Aerial photo of ranch buildings"` and `blk-chapter-008-0006 -> ["p021-b4"] "Ranch house and barn"`; [chapter-011.html](/Users/cam/.codex/worktrees/cdb6/codex-forge/output/runs/story153-doc-web-bundle-emitter-r1/output/html/chapter-011.html) and [chapter-023.html](/Users/cam/.codex/worktrees/cdb6/codex-forge/output/runs/story153-doc-web-bundle-emitter-r1/output/html/chapter-023.html) remain text-identical to the committed Story 149 reviewed slice; [chapter-010.html](/Users/cam/.codex/worktrees/cdb6/codex-forge/output/runs/story153-doc-web-bundle-emitter-r1/output/html/chapter-010.html), [chapter-017.html](/Users/cam/.codex/worktrees/cdb6/codex-forge/output/runs/story153-doc-web-bundle-emitter-r1/output/html/chapter-017.html), and [chapter-022.html](/Users/cam/.codex/worktrees/cdb6/codex-forge/output/runs/story153-doc-web-bundle-emitter-r1/output/html/chapter-022.html) keep the expected current recipe-level structural churn while preserving narrative openings, figures, summary tables, and stable block/provenance ids. The current maintained reuse-based validator band also held exactly as expected from Story 144: [genealogy_consistency_report_regression.jsonl](/Users/cam/.codex/worktrees/cdb6/codex-forge/output/runs/story153-doc-web-bundle-emitter-r1/05_validate_onward_genealogy_consistency_v1/genealogy_consistency_report_regression.jsonl) reports `flagged_genealogy_chapters=5`, `flagged_chapters=["chapter-010.html","chapter-016.html","chapter-017.html","chapter-021.html","chapter-022.html"]`, and `strong_rerun_candidate_page_count=6`, which confirms the emitter extraction added contract surfaces without changing the recipe's existing consistency profile.
20260319-2214 — validation follow-up and close-out: narrowed Story 153's acceptance/eval/tenet wording from the stronger "healthy / no semantic regression" claim to the proof the run actually delivered: the extracted seam now enforces the canonical Story 152 contract at the live `codex-forge` boundary, preserves the reviewed hard-case bundle behavior, and introduces no new emitter-specific regression while the maintained Story 144 reuse-lane consistency band stays unchanged. With the dependency already satisfied by local completed Story 152, the story is now closed.
