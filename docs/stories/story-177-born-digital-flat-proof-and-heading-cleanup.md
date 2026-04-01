# Story 177 — Widen Flat Born-Digital Proof and Decide Oversized Heading Cleanup

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #1 (Ingest), Requirement #3 (Extract), Requirement #6 (Validate), Requirement #7 (Export), Zero configuration, Any format, any condition, Traceability is the Product
**Spec Refs**: spec:1 (spec:1.1, C2), spec:3 (spec:3.1, C3), spec:6, spec:7, spec:8 (B1)
**Build Map Refs**: Category 1 Intake & Format Routing (`exists`, C2 `climb`); Category 3 Layout & Structure Understanding (`exists`, C3 `climb`); Category 7 Graduation & Dossier Handoff (`partial`); Category 8 AI Harnesses & Tooling (`exists`, B1 `hold`); Input Coverage row `born-digital-pdf` (`has fixture`); Gap 2 — Born-digital PDF native text extraction; Gap 5 — Fixture breadth and graduation confidence
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/stories/story-168-marker-lite-maintained-born-digital-pdf-path.md`, `docs/stories/story-170-born-digital-pdf-native-text-widening-and-routing-decision.md`, `docs/stories/story-171-maintained-non-toc-born-digital-pdf-lane.md`, `docs/stories/story-173-dossier-doc-web-adoption-hardening.md`, `docs/stories/story-176-confirmed-intake-handoff-to-explicit-recipe-runs.md`, `docs/scout/scout-011-external-document-ingestion-systems.md`, `tests/fixtures/formats/_coverage-matrix.json`, `testdata/README.md`, `docs/build-map.md`, `None found after search in docs/decisions/ for flat-born-digital-polish-specific ADRs`
**Depends On**: Story 168, Story 171, Story 176

## Goal

Widen the current flat born-digital PDF proof surface beyond the repo-owned
2-page fixture plus the two shared local form examples, then use that wider
evidence to answer one concrete open question honestly: are the oversized
in-body headings seen on some form-heavy outputs a generic native-text cleanup
gap worth fixing now, or just a bounded rough edge that should stay as an
explicit follow-up? This story should leave the `born-digital-pdf` lane more
trustworthy, not just broader on paper.

## Acceptance Criteria

- [x] The flat born-digital proof surface is widened beyond the current minimal slice:
  - [x] at least one additional repo-owned or reproducibly generated flat born-digital PDF fixture is added, or the story explicitly records why the shipped support claim must remain bounded to the current fixture set
  - [x] fresh `driver.py` proofs exist for the maintained non-TOC lane on every fixture claimed as part of the widened proof surface
  - [x] manual inspection is recorded for representative `pages_html.jsonl`, portion artifact(s), `output/html/manifest.json`, `output/html/provenance/blocks.jsonl`, and final HTML outputs on the widened slice
- [x] The oversized-heading question is resolved with artifact evidence:
  - [x] widened proofs explicitly record whether oversized in-body headings appear, on which fixtures, and whether the issue is generic or fixture-specific
  - [x] if the issue is generic and fixable with a small deterministic change, the story either absorbs that fix and reruns proof or records the exact reason it must split before claiming broader polish
  - [x] not needed in this pass: widened proofs showed a bounded generic build-stage fix was enough on the proven slice, so no dedicated heading-cleanup follow-up story was required
- [x] Coverage and routing truth stay aligned with the evidence:
  - [x] `born-digital-pdf` remains only as broad as the widened proof justifies and does not silently jump to `passing`
  - [x] intake or handoff surfaces change only if the widened evidence justifies a different maintained recommendation
  - [x] `docs/build-map.md`, `tests/fixtures/formats/_coverage-matrix.json`, `testdata/README.md`, and any affected README or runbook guidance reflect the post-story state exactly
- [x] Repeatable proof remains after the story:
  - [x] focused tests or a maintained harness cover any new fixture generator and any heading-cleanup logic added in the story
  - [x] routing expectations did not change, so `benchmarks/scripts/run_auto_book_type_detection_eval.py` and `docs/evals/registry.yaml` remained untouched

## Out of Scope

- Claiming the full `born-digital-pdf` family is ready for graduation to Dossier
- Reopening the Marker versus `doc-web` boundary or replacing the Docker-backed Marker runtime
- Broad semantic form normalization, field extraction, or Dossier-side adapter work
- Hidden auto-routing beyond the explicit recipe compromise in `spec:1.1`
- Unrelated format-family work such as DOCX, XLSX, PPTX, EPUB, email, or web-page intake

## Approach Evaluation

- **Simplification baseline**: rerun the current maintained non-TOC lane unchanged on a wider flat born-digital slice and inspect real artifacts before changing code. This directly tests whether the current recipe already clears the bar and whether the oversized-heading issue is actually recurring.
- **AI-only**: use an LLM or VLM to rewrite heading levels or judge which extracted headings are too prominent. Low-value as the default because the problem is currently framed as proof and bounded cleanup, and AI-first normalization would make provenance/debugging less inspectable.
- **Hybrid**: deterministic fixture widening and artifact diffing first, with AI used only if the heading issue proves semantic rather than structural. Plausible if the issue cannot be fixed cleanly with simple deterministic rules.
- **Pure code**: plausible if the work stays inside fixture widening, deterministic heading normalization, proof harnesses, and truth-surface updates. This is the leading no-new-model path.
- **Repo constraints / prior decisions**: ADR-002 fixes the `doc-web` bundle boundary; Story 171 already proved the maintained non-TOC lane; Story 176 only proved confirmed handoff on the reviewed book-like born-digital slice; `docs/build-map.md` now names proof breadth plus oversized in-body headings as the live remaining gap. Do not widen claims faster than artifact evidence.
- **Existing patterns to reuse**: `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`, `modules/extract/extract_pdf_marker_lite_html_v1/main.py`, `modules/common/marker_page_html.py`, `modules/portionize/portionize_headings_html_v1/main.py`, `modules/build/build_chapter_html_v1/main.py`, `testdata/generate_flat_born_digital_fixture.py`, `tests/test_pdf_intake_recipe.py`, `tests/test_intake_plan_utils.py`, and Story 175's repo-owned fixture widening discipline.
- **Eval**: the deciding evidence is fresh `driver.py` proof on widened flat born-digital fixtures plus manual artifact inspection. Rerun `auto-book-type-detection` only if the maintained recommendation surface changes. No new compromise-detection eval is required unless the story changes the C2 routing claim materially.

## Tasks

- [x] Freeze the widened flat born-digital proof surface:
  - [x] audit the current born-digital fixtures and comparison assets
  - [x] add at least one additional repo-owned or reproducibly generated flat born-digital PDF fixture if the current 2-page repo-owned fixture is too narrow to answer the polish question honestly
  - [x] document the expected output shape and review dimensions per fixture
- [x] Measure the current maintained non-TOC lane unchanged:
  - [x] run `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml` through `driver.py` on the widened slice
  - [x] inspect `pages_html.jsonl`, portion artifacts, final bundle/provenance outputs, and representative HTML
  - [x] record exact oversized-heading cases, if any, with artifact paths and sample evidence
- [x] Decide and land the smallest evidence-backed action:
  - [x] if oversized in-body headings are a generic bounded defect, implement the narrowest deterministic cleanup at the appropriate seam and rerun proof
  - [x] not needed in this pass: the bounded build-stage polish closed the proven rough edge without a separate follow-up story
  - [x] touch intake recommendation or handoff surfaces only if the widened evidence changes what is honest to recommend
- [x] Leave repeatable proof behind:
  - [x] add focused tests for any new fixture generator or heading-cleanup logic
  - [x] extend `tests/test_pdf_intake_recipe.py`, `tests/test_intake_plan_utils.py`, `tests/test_extract_pdf_marker_lite_html_v1.py`, or `tests/test_build_chapter_html.py` if behavior changes
  - [x] routing expectations did not shift, so `benchmarks/scripts/run_auto_book_type_detection_eval.py` and `docs/evals/registry.yaml` were not touched
- [x] If this story changes documented format coverage or graduation reality: update `docs/build-map.md` and record the before/after state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [x] agent tooling unchanged; `make skills-check` not required
- [x] If evals or goldens changed: run `/improve-eval` and update `docs/evals/registry.yaml` (not needed; evals and goldens did not change)
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every output traces to source page, OCR engine, confidence, processing step
  - [x] T1 — AI-First: do not write code for a problem the current maintained lane already solves honestly
  - [x] T2 — Eval Before Build: widen and inspect the proof surface before adding cleanup logic
  - [x] T3 — Fidelity: source content remains faithful; heading cleanup must not flatten or silently rewrite meaning
  - [x] T4 — Modular: keep any cleanup scoped to the flat born-digital lane or a clearly reusable helper, not a format-specific maze
  - [x] T5 — Inspect Artifacts: validate real bundle/provenance outputs, not just tests or logs

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: the story sits on the flat born-digital non-TOC lane across repo-owned fixtures, the native-text normalization seam, the portionize/build handoff, and the intake truth surfaces that describe what the lane honestly supports.
- **Build-map reality**: Category 1 owns routing honesty, Category 3 owns any structure cleanup, Category 7 owns the final `doc-web` bundle truth, and Category 8 owns the proof surface. The relevant `born-digital-pdf` row is still `has fixture`, not `passing`, because breadth and polish remain open.
- **Substrate evidence**: `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml` already exists; `testdata/flat-born-digital-mini.pdf` plus `testdata/generate_flat_born_digital_fixture.py` already provide one repo-owned flat proof surface; `tests/test_pdf_intake_recipe.py` and `tests/test_intake_plan_utils.py` already cover recipe wiring and routing; `tests/fixtures/formats/_coverage-matrix.json` already records the oversized-heading rough edge explicitly. Story 171 proved the non-TOC lane itself, and Story 176 proved confirmed handoff only on the reviewed book-like born-digital slice.
- **Data contracts / schemas**: likely touched artifacts are `page_html_v1`, `portion_hyp_v1`, `doc_web_bundle_manifest_v1`, `doc_web_provenance_block_v1`, and `intake_plan_v1` if routing expectations change. If any new fields cross artifact boundaries, they must be added to `schemas.py` before relying on stamped output.
- **File sizes**: likely owner files are `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml` (47), `modules/intake/intake_plan_utils.py` (298), `modules/extract/extract_pdf_marker_lite_html_v1/main.py` (192), `modules/common/marker_page_html.py` (780), `modules/portionize/portionize_headings_html_v1/main.py` (228), `modules/build/build_chapter_html_v1/main.py` (1685), `tests/test_pdf_intake_recipe.py` (80), `tests/test_intake_plan_utils.py` (233), `tests/test_build_chapter_html.py` (1544), `tests/test_extract_pdf_marker_lite_html_v1.py` (142), `testdata/generate_flat_born_digital_fixture.py` (64), `testdata/README.md` (75), `docs/build-map.md` (582), `tests/fixtures/formats/_coverage-matrix.json` (393), `docs/evals/registry.yaml` (644), and `README.md` (248). `modules/common/marker_page_html.py`, `modules/build/build_chapter_html_v1/main.py`, `tests/test_build_chapter_html.py`, `docs/build-map.md`, and `docs/evals/registry.yaml` are already oversized, so prefer focused helpers and narrow truth-surface edits.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/build-map.md`, ADR-002, Stories 168/170/171/173/176, `docs/scout/scout-011-external-document-ingestion-systems.md`, `tests/fixtures/formats/_coverage-matrix.json`, and `testdata/README.md`. No flat-born-digital-polish ADR exists today; if the heading issue turns out to require a broader architecture decision, stop and open that explicitly rather than growing this story by inertia.

## Files to Modify

- `testdata/generate_flat_born_digital_fixture.py` — add another reproducible flat born-digital proof fixture if the current repo-owned slice is too narrow (64 lines)
- `testdata/README.md` — document any widened flat born-digital proof surface and supported slice changes (75 lines)
- `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml` — adjust the maintained non-TOC lane only if the widened evidence supports a bounded recipe-level change (47 lines)
- `modules/extract/extract_pdf_marker_lite_html_v1/main.py` — apply extract-stage cleanup only if the widened evidence shows the issue belongs at normalized page HTML output (192 lines)
- `modules/common/marker_page_html.py` — likely normalization seam if oversized headings are generic and fixable before portionization (780 lines)
- `modules/portionize/portionize_headings_html_v1/main.py` — adjust portionize behavior only if widened proof shows the issue is downstream of page HTML normalization (228 lines)
- `modules/build/build_chapter_html_v1/main.py` — touch only if the widened evidence shows heading roughness is created or preserved at bundle-build time (1685 lines)
- `modules/intake/intake_plan_utils.py` — change maintained recommendation mapping only if the widened evidence makes a routing update honest (298 lines)
- `tests/test_pdf_intake_recipe.py` — widen born-digital proof coverage and recipe wiring checks (80 lines)
- `tests/test_intake_plan_utils.py` — update routing expectations only if maintained recommendation truth changes (233 lines)
- `tests/test_extract_pdf_marker_lite_html_v1.py` — add regression coverage if heading cleanup lands at extract/normalize seam (142 lines)
- `tests/test_build_chapter_html.py` — add regression coverage only if heading cleanup lands in bundle build behavior (1544 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — keep the `born-digital-pdf` row honest about breadth and polish after the story (393 lines)
- `docs/build-map.md` — update Gap 2, Gap 5, and Next Actions narrowly if the widened evidence changes them (582 lines)
- `docs/evals/registry.yaml` — rerun and update only if routing expectations or benchmark corpus truth change (644 lines)
- `README.md` — align operator guidance only if the widened evidence changes what is honest to recommend publicly (248 lines)

## Redundancy / Removal Targets

- Any stale documentation that implies the oversized-heading issue is either fully resolved or too vague to act on after widened proof exists
- Over-reliance on shared local flat PDFs as the primary proof surface if an additional repo-owned fixture lands successfully
- Any duplicate flat-born-digital cleanup branch created during implementation if the issue can live cleanly in one existing normalization seam

## Notes

- This story may end with no behavior change beyond widened proof and truth-surface updates if the evidence shows the current roughness is not generic enough to justify cleanup yet.
- Keep the book-like Marker lane and the flat/non-TOC lane distinct. The goal is not to blur them into one catch-all born-digital claim.
- If widened proof shows the flat lane is ready for broader confirmed handoff, that should be an explicit evidence-backed follow-up rather than an accidental side effect.

## Plan

### Exploration Summary

- **Ideal alignment:** proceed. This story closes a live gap in the active intake path, not a dead-end optimization. The build map explicitly names widened flat born-digital proof plus the oversized-heading decision as the next action.
- **Relevant build-map state:** the `born-digital-pdf` row is still `has fixture`, Gap 2 says the missing maintained path is no longer the blocker, and Gap 5 says fixture breadth still trails capability growth.
- **Critical substrate verified in code:** the maintained non-TOC recipe, repo-owned flat fixture generator, routing helper, and proof tests already exist, so the story is buildable in implemented reality. The remaining work is widening the proof surface and deciding whether a bounded cleanup belongs in this same slice.
- **Known open signal:** both `docs/build-map.md` and `tests/fixtures/formats/_coverage-matrix.json` already record that some form-heavy flat PDFs still surface oversized in-body headings from the native-text extractor.

### Eval-First Gate

- First rerun the current maintained non-TOC lane unchanged on a wider flat born-digital slice.
- Only after artifact inspection should the story decide whether the heading issue belongs in code now, in docs only, or in a separate follow-up.
- If maintained recommendation truth changes, rerun the locked `auto-book-type-detection` harness instead of assuming the benchmark still matches reality.

### Implementation Outline

1. Add or freeze the widened flat proof slice.
2. Run fresh `driver.py` proofs and inspect real artifacts.
3. Decide whether the oversized-heading issue is generic and bounded.
4. If yes, land the smallest deterministic cleanup and rerun proof.
5. If no, leave a named follow-up and update truth surfaces only.

### What Done Looks Like

- The repo has a wider, repeatable flat born-digital proof surface than it has today.
- The oversized-heading question is answered with concrete artifact evidence.
- The coverage matrix, build map, and any affected routing guidance tell the same story.

## Work Log

20260401-1810 — story created: converted the top triage recommendation into a real `Pending` story after verifying that the non-TOC born-digital recipe, repo-owned flat fixture generator, routing helper, and proof tests already exist in the repo. Evidence reviewed in this pass: `docs/build-map.md` names widened flat born-digital proof plus the oversized-heading decision as the current top next action; `tests/fixtures/formats/_coverage-matrix.json` already records oversized in-body headings as a known gap; `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`, `testdata/generate_flat_born_digital_fixture.py`, `tests/test_pdf_intake_recipe.py`, and `tests/test_intake_plan_utils.py` prove the base substrate exists. Next step: `/build-story` should freeze the widened flat proof slice, rerun the current maintained lane unchanged, and decide whether the heading issue is generic enough to absorb a bounded deterministic cleanup.
20260401-1608 — `/build-story` exploration completed and the implementation seam narrowed around fresh evidence instead of backlog prose. Alignment check: proceed. This closes a live Ideal gap in any-format ingest, fidelity, and traceability rather than widening a dead-end workaround. Context reviewed in this pass: `docs/ideal.md`, the cited `spec:1`, `spec:3`, `spec:6`, `spec:7`, and `spec:8` sections, the relevant Category 1 / 3 / 7 / 8 sections plus Input Coverage / Gap 2 / Gap 5 in `docs/build-map.md`, ADR-002, Stories 168 / 170 / 171 / 173 / 176, `benchmarks/golden/auto-book-type-detection/corpus.json`, `modules/common/marker_page_html.py`, `modules/build/build_chapter_html_v1/main.py`, `modules/portionize/portionize_headings_html_v1/main.py`, `testdata/generate_flat_born_digital_fixture.py`, `tests/test_build_chapter_html.py`, `tests/test_pdf_intake_recipe.py`, and `tests/test_intake_plan_utils.py`. Fresh baseline proof before code changes: `story177-flat-baseline-r1`, `story177-rfp-baseline-r1`, and `story177-release-forms-baseline-r1` all completed through `build_chapter_html_v1` and validated their bundle/provenance schemas. Manual artifact inspection showed the rough edge is generic on the proven flat slice but not identical on every fixture: `output/runs/story177-flat-baseline-r1/output/html/chapter-001.html` still rendered repeated short in-body labels (`Budget notes:`, `Review notes:`) as oversized `h1` headings; `output/runs/story177-rfp-baseline-r1/output/html/chapter-001.html` repeated short in-body titles as `h1`/`h2`; and `output/runs/story177-release-forms-baseline-r1/output/html/chapter-001.html` exposed the severe case, where a page-spanning warning/waiver block landed as one giant `h2`. Substrate verdict: the story is honestly buildable because the maintained non-TOC lane, repo-owned fixture generator, and bundle/provenance contract already exist. The bounded seam is final-HTML polish inside `build_chapter_html_v1`, not routing or a new model path. Next step: add a second repo-owned flat form-like fixture, implement a narrow build-stage heading-polish helper for source-page chapters, and rerun the widened proof surface.
20260401-1656 — implementation landed and fresh proof shows the dedicated heading-cleanup follow-up is not needed on the currently proven slice. Added the repo-owned reproducible form-like fixture pair `testdata/flat-born-digital-form-mini.md` / `testdata/flat-born-digital-form-mini.pdf`, documented regeneration in `testdata/README.md`, taught `modules/build/build_chapter_html_v1/main.py` to apply bounded heading polish only on source-page chapters without printed pages, and added regression coverage in `tests/test_build_chapter_html.py` plus fixture coverage in `tests/test_pdf_intake_recipe.py`. The build-stage polish is intentionally narrow: after the primary chapter heading, repeated short in-body `h1` / `h2` labels are demoted to calmer `h3` subheads, and pathological long heading blocks are flattened into a `p.flattened-heading` emphasis paragraph instead of remaining giant headings. Fresh focused verification passed: `pytest -q tests/test_build_chapter_html.py tests/test_pdf_intake_recipe.py` => `89 passed in 11.18s`. Fresh full verification also passed: `make lint` => pass and `make test` => `413 passed, 4 warnings`. Fresh real-pipeline proof after clearing stale bytecode (`find modules/build -name '*.pyc' -delete`) succeeded on the widened proof surface under `output/runs/story177-flat-proof-r2/`, `output/runs/story177-flat-form-proof-r1/`, `output/runs/story177-rfp-proof-r2/`, and `output/runs/story177-release-forms-proof-r2/`. Manual artifact inspection confirms the intended outcome: `output/runs/story177-flat-proof-r2/output/html/chapter-001.html` now keeps `Requested information:` as the chapter heading while demoting later `Budget notes:` / `Review notes:` headings to `h3`; `output/runs/story177-flat-form-proof-r1/output/html/chapter-001.html` keeps `Participant information:` as the first section while demoting `Accessibility checklist:`, `Required acknowledgments:`, and `Signature block:` to `h3`; `output/runs/story177-rfp-proof-r2/output/html/chapter-001.html` demotes repeated short in-body `h1`/`h2` labels to calmer `h3`; and `output/runs/story177-release-forms-proof-r2/output/html/chapter-001.html` converts the pathological page-spanning warning block into `p.flattened-heading` while preserving provenance and text. Schema validation also passed on the fresh reruns via `python validate_artifact.py --schema doc_web_bundle_manifest_v1 ...` and `python validate_artifact.py --schema doc_web_provenance_block_v1 ...` for all four proof runs. Truth surfaces are now aligned in `docs/build-map.md`, `tests/fixtures/formats/_coverage-matrix.json`, and `testdata/README.md`. Residual risk: the family still stays `has fixture`, not passing, because proof breadth is still only two repo-owned flat fixtures plus two local comparison PDFs and the native-text lane still carries a heavy cold-start/runtime burden (`story177-flat-baseline-r1` took `176.0s` for 2 pages after the worktree-local runtime rebuild). Next step: `/validate`, then `/mark-story-done` if the user wants this story formally closed.
20260401-1918 — `/mark-story-done` close-out completed on fresh evidence. Validation summary for the current tip: `pytest -q tests/test_build_chapter_html.py tests/test_pdf_intake_recipe.py` => `89 passed in 7.56s`, `make lint` => pass, `make test` => `413 passed, 4 warnings`, and `make skills-check` => pass for the accepted triage prompt change. Re-opened the current proof artifacts for `story177-flat-proof-r2`, `story177-flat-form-proof-r1`, `story177-rfp-proof-r2`, and `story177-release-forms-proof-r2`, revalidated their `doc_web_bundle_manifest_v1` / `doc_web_provenance_block_v1` outputs with `validate_artifact.py`, and confirmed the shipped HTML still matches the story claim: repeated short in-body flat headings are demoted while the pathological release-form warning block stays flattened into an emphasis paragraph. Added one fresh close-out smoke rerun on the repo-owned form fixture under `output/runs/story177-closeout-form-r2/`; it completed through `build_chapter_html_v1`, passed schema validation, and preserved the expected `Participant information:` / `Emergency contact:` / `Accessibility checklist:` heading structure with page-linked provenance. Story 177 is now implementation-complete and fully validated; next step: `/check-in-diff`.
