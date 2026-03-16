# Story 135 — Onward Image Placement and Caption Fidelity

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #4 (Illustrate), Requirement #5 (Structure), Fidelity to Source
**Spec Refs**: C3 (layout detection), C4 (two-stage crop detection), C5 (layout text trim heuristics)
**Depends On**: Story 126 (crop detection pipeline), Story 129 (HTML output polish)

## Goal

Fix the remaining image-facing fidelity defects in the Onward HTML output after manual review of `onward-story009-full`: missing/broken image attachment, swapped captions, and image placement that violates single-column reading flow.

The guiding rule for this story is: **in single-column HTML, images should appear between paragraphs unless there is a strong, source-faithful reason to do otherwise.** Mid-sentence insertion is the exception, not the default.

## Acceptance Criteria

- [x] The reviewed page-21 image pair renders with no broken or unmatched `<figure>` elements, including the bottom "Ranch house and barn" image
- [x] The reviewed family-story chapters in the current verification run no longer place images mid-sentence; images render at block boundaries consistent with single-column reading flow
- [x] The reviewed swapped image/caption pair in the current verification run is assigned correctly
- [x] A placement policy is documented and enforced: default to paragraph-boundary image placement unless a stronger source-faithful interpretation is explicitly justified
- [x] Manual review of the fixed chapters confirms image attachment, caption pairing, and placement are accurate

## Out of Scope

- Missing prose pages or dropped table tails (tracked in follow-up stories)
- Genealogy table header/continuation regressions (tracked in follow-up stories)
- General crop-box precision improvements unrelated to the reviewed placement/caption defects

## Approach Evaluation

- **Simplification baseline**: First verify whether current code already fixes the historical page-21 crop miss and whether the remaining defects are now downstream attachment/placement issues rather than detector failures.
- **AI-only**: Re-ask a multimodal model to place figures/captions directly from the page image and OCR HTML for only the flagged pages. This may help on ambiguous two-column layouts, but should not be the default if deterministic block-boundary placement is sufficient.
- **Hybrid**: Use the existing OCR/crop outputs, add stronger paragraph-boundary placement rules in chapter assembly, and only escalate ambiguous pages or caption pairings with AI when deterministic ordering is insufficient.
- **Pure code**: If the reviewed defects reduce to crop ordering, caption ordering, or paragraph-boundary insertion, solve them in `build_chapter_html_v1` without adding new model calls.
- **Eval**: Rebuild the reviewed chapters and verify:
  - no `figure without img[src]` issues,
  - no reviewed image is inserted mid-sentence,
  - reviewed captions match the correct images.

## Tasks

- [x] Re-run the reviewed image chapters with current code and classify each defect as crop, caption pairing, or chapter-assembly placement
- [x] Verify whether the historical page-21 defect is already fixed in current crop output; if so, preserve that behavior with regression coverage rather than re-solving it
- [x] Implement paragraph-boundary placement rules so reviewed images are not inserted mid-sentence by default
- [x] Fix page-local image ordering/caption pairing for the reviewed Leonidas and Pierre image pairs in the current verification run
- [x] Rebuild and manually verify the reviewed verification titles, ending with the corrected review run `story135-onward-image-placement-r2`: `Farm Heritage Award`, `L’HEUREUX VETERANS OF WORLD WAR I & II`, `LEONIDAS L'HEUREUX`, `GEORGE L'HEUREUX`, `EMILIE (L'HEUREUX) NOLIN`, `PIERRE L'HEUREUX`, and `I WISH`
- [x] Run required checks:
  - [x] `python -m pytest tests/`
  - [x] `python -m ruff check modules/ tests/`
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability
  - [x] T1 — AI-First
  - [x] T2 — Eval Before Build
  - [x] T3 — Fidelity
  - [x] T4 — Modular
  - [x] T5 — Inspect Artifacts

## Files to Modify

- `modules/build/build_chapter_html_v1/main.py` — image placement, caption pairing, or block-boundary insertion rules
- `modules/extract/crop_illustrations_guided_v1/main.py` — only if current-code verification shows a real remaining crop-order issue
- `tests/test_build_chapter_html.py` — chapter-assembly regression coverage for placement/caption rules
- `tests/test_crop_illustrations_guided.py` — if page-21 crop-count regression coverage is still needed
- `benchmarks/scorers/layout_linearization_scorer.py` — only if a scorer update is needed to assert the reviewed placement invariants

## Notes

- Manual review findings currently grouped here:
  - `chapter-007.html` — missing/broken bottom image on page 21
  - `chapter-011.html` — image inserted mid-sentence and wrong single-column flow for a two-column source page
  - `chapter-028.html` — swapped captions on a reviewed image pair
- Round-2 verification findings that stay in this story:
  - `chapter-010.html` in `story137-onward-verify` still inserts an image mid-sentence (`...made into <img> colorful bedspreads.`)
  - `chapter-021.html` in `story137-onward-verify` still has the reviewed swapped image pair
 - `story139-onward-full127-composite-validate` review:
   - `chapter-003.html` is missing the `Celebrate Saskatchewan` logo at the top; the seal is placed at the top instead of below beside the signature
   - `chapter-011.html`, `chapter-014.html`, and `chapter-024.html` still place images mid-sentence in single-column reading order
   - `chapter-011.html` and `chapter-028.html` still show swapped image/caption pairing
- The historical page-21 crop miss may already be fixed in current code; if so, this story should focus on locking in the fix and addressing the remaining placement/caption defects.
- Placement policy for this story: prefer image blocks between paragraphs over literal cross-column interleaving when linearizing into single-column HTML.

## Plan

### Exploration Findings

- **Ideal alignment:** This story closes a live Fidelity to Source / Illustrate / Structure gap. The current reviewed run still mis-orders figures, inserts them mid-sentence, and misplaces frontmatter images even though upstream crops now exist.
- **ADRs / decisions consulted:** Searched `docs/decisions/` for image placement / chapter HTML guidance. No ADR specifically governs figure placement. `docs/decisions/adr-001-source-aware-consistency-strategy/adr.md` only reinforces that we should keep this fix narrowly about HTML linearization rather than absorbing unrelated normalization work.
- **Baseline artifact evidence:**
  - `story139-onward-full127-composite-validate/03_load_artifact_v1/illustration_manifest.jsonl` already contains both page-21 crops (`page-021-000.jpg`, `page-021-001.jpg`), so the historical crop miss is closed upstream.
  - `story139-onward-full127-composite-validate/output/html/chapter-011.html` and `chapter-024.html` still split prose around figures at sentence boundaries (`...made into` / `colorful bedspreads`, `...until they` / `could finally afford...`).
  - `story139-onward-full127-composite-validate/output/html/chapter-011.html`, `chapter-021.html`, and `chapter-028.html` still show swapped image/content pairing because the current build step matches sequentially by DOM order, not by the page's visual order.
  - `story139-onward-full127-composite-validate/output/html/chapter-003.html` still places the `Celebrate Saskatchewan` logo above the award heading while leaving the seal embedded in the table, which is source-faithful in raw OCR order but poor single-column linearization.
- **Root-cause split:**
  - Page-21 broken-image issue: no remaining crop bug in current code; regression coverage is the right response.
  - Mid-sentence defects: build-stage placement issue. `_attach_images()` wraps the OCR `<img>` exactly where OCR inserted it, so a placeholder inside interrupted prose becomes a block figure in the same bad location.
  - Swapped pairs: mixed ordering issue. On pages like 38 and 108 the OCR `<img>` placeholders follow reading order while the crop manifest is sorted by crop `bbox.y0`, so sequential matching swaps the visual identities.
  - Frontmatter page 12: special layout case. Two images exist in different structural contexts (top logo vs. seal in table cell), and the default sequential attach path does not express an explicit placement policy for frontmatter certificate layouts.
- **Files likely to change:** `modules/build/build_chapter_html_v1/main.py`, `tests/test_build_chapter_html.py`, and this story/doc trail. `modules/extract/crop_illustrations_guided_v1/main.py` is only at risk if artifact inspection later proves a remaining upstream ordering bug beyond build-time matching.
- **Scope delta folded into this story:** Added the current reviewed verification chapters (`chapter-003`, `010`, `014`, `021`, `024`) to the manual verification target list because they are the same subsystem and the same underlying placement/order policy. This is a small coherent expansion, not a separate story.

### Eval-First / Baseline

- **Eval type:** deterministic regression tests plus a targeted `driver.py --start-from build_chapters` rerun on the reviewed artifact set.
- **Baseline:**
  - Page-21 crop availability: pass upstream, not a current defect.
  - Placement baseline: current reviewed run still contains at least three mid-sentence figure insertions (`chapter-010`, `chapter-011`, `chapter-024`; `chapter-014` also remains flagged from manual review).
  - Pairing baseline: current reviewed run still swaps reviewed pairs on `chapter-011`, `chapter-021`, and `chapter-028`.
  - Frontmatter baseline: current reviewed run still linearizes page 12 poorly in `chapter-003`.
- **Why pure code first:** This defect is in deterministic chapter assembly over existing OCR/crop artifacts. There is no evidence yet that a new model call is needed; the simplest valid fix is to improve build-time placement and page-local matching rules, then verify against the current run.

### Implementation Plan

#### Task 1 — Lock in the current upstream truth
- **Files:** `tests/test_build_chapter_html.py` and possibly `tests/test_crop_illustrations_guided.py`
- **Change:** Add regression coverage proving that multi-image page 21 already has two crops and that build-time attachment does not emit unmatched/broken figures when both placeholder tags and crops exist.
- **Done when:** A test fails on broken/missing page-21 attachment and passes with current crop behavior preserved.

#### Task 2 — Enforce paragraph-boundary figure placement
- **Files:** `modules/build/build_chapter_html_v1/main.py`, `tests/test_build_chapter_html.py`
- **Change:** Teach `_attach_images()` to normalize bare OCR `<img>` placeholders to block-level figure placement instead of preserving interrupted prose literally. For single-column linearization, if an image/caption pair splits a paragraph or sits between a sentence fragment and its continuation, move the figure to the nearest safe paragraph boundary and rejoin the prose.
- **Patterns to follow:** keep this page-local and deterministic, consistent with existing `_stitch_page_breaks()` / BeautifulSoup-based HTML rewriting.
- **Risk:** Could accidentally reorder legitimate inline/frontmatter/table imagery. Tests need to cover both narrative pages and table-cell/frontmatter cases.
- **Done when:** Reviewed single-column chapters no longer split sentences around figures by default.

#### Task 3 — Fix page-local image ordering / caption pairing
- **Files:** `modules/build/build_chapter_html_v1/main.py`, `tests/test_build_chapter_html.py`
- **Change:** Replace pure sequential crop-to-`<img>` matching with a page-local ordering strategy that can reconcile OCR placeholder order with crop `bbox` order. Likely approach: detect page layout from existing DOM context and place figures according to visual block order rather than raw crop y-order alone, with explicit tie-breaking for mixed left/right or top/bottom pairs.
- **Evidence driving this:** page 38 and page 108 crop manifests have `image_description` values opposite the OCR `<img alt>` order, which is why current sequential matching swaps the reviewed pairs.
- **Done when:** `chapter-011`, `chapter-021`, and `chapter-028` attach the correct crop to the correct caption/image identity in the rebuilt run.

#### Task 4 — Handle the frontmatter certificate layout explicitly
- **Files:** `modules/build/build_chapter_html_v1/main.py`, `tests/test_build_chapter_html.py`
- **Change:** Add a narrow placement rule for frontmatter-like pages where a top-of-page logo should remain above the heading while seal/signature imagery embedded in a table or side-by-side block should stay in that local structure instead of being promoted or re-ordered generically.
- **Risk:** This is the one place where over-generalization would be dangerous. The rule must be expressed in terms of DOM context/layout structure, not page-number or book-specific text.
- **Done when:** `chapter-003` preserves the frontmatter reading flow without regressing normal narrative chapters.

#### Task 5 — Rebuild and manually inspect the reviewed run
- **Files/artifacts:** rerun `build_chapter_html_v1` through `driver.py` starting from `build_chapters`, inspect the rebuilt HTML under a new run in `output/runs/`
- **Change:** Update the recipe/run-local config as needed to reuse the safe upstream artifacts and only rebuild from the build stage.
- **Manual inspection set:** `chapter-003`, `chapter-007`, `chapter-010`, `chapter-011`, `chapter-014`, `chapter-021`, `chapter-024`, `chapter-028`
- **Done when:** The story work log records exact artifact paths plus the sample figures/captions manually checked.

### Impact / Risk Analysis

- **Story-scope impact:** This directly addresses the remaining image-facing fidelity defects that blocked Story 135 from closing even after Stories 137/139 repaired missing pages and boundary handling.
- **Pipeline-scope impact:** A correct build-stage placement policy reduces downstream manual cleanup and prevents HTML output from misrepresenting source reading flow even when OCR emits placeholders in awkward positions.
- **Primary risks:** over-correcting legitimate inline structures, breaking table-cell images, or masking an upstream crop-order defect that really belongs elsewhere.
- **Human-approval blockers:** None expected for dependencies or schema. The only decision to confirm is strategy: keep this deterministic in `build_chapter_html_v1` unless implementation proves the source ambiguity really requires an AI escalation.

### Done Looks Like

- The current reviewed verification run rebuilds without broken page-21 figures.
- Reviewed narrative chapters no longer insert figures between sentence fragments.
- Reviewed swapped pairs are correctly attached.
- The frontmatter certificate page follows a documented placement policy that preserves source fidelity in single-column HTML.
- Tests cover the regression patterns, and manual artifact inspection confirms the fix on the rebuilt run.

## Work Log

### 20260312-1702 — exploration: historical failure reproduced, current code verified as already fixed
- **Result:** Promoted the story into active work after validating that it targets a real Ideal gap, then traced the failure through both historical artifacts and current code.
- **Evidence:** 
  - Historical failing run: `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-story009-full/03_crop_illustrations_guided_v1/illustration_manifest.jsonl` contains only one page-21 crop (`page-021-000.jpg`).
  - Historical downstream symptom: `python benchmarks/scorers/layout_linearization_scorer.py --chapters-dir /Users/cam/Documents/Projects/codex-forge/output/runs/onward-story009-full/output/html` returns `PARTIAL` with one issue: `chapter-007.html: figure without img[src]`.
  - Current-code targeted rerun: `PYTHONPATH=. python modules/extract/crop_illustrations_guided_v1/main.py ... --only-pages 21` wrote `/tmp/story135-page21-current/illustration_manifest.jsonl` with two validated crops: `page-021-000.jpg` and `page-021-001.jpg`.
  - Rebuilt downstream proof: merging those page-21 rows into the old manifest and rebuilding chapters to `/tmp/story135-build/html/` yields `chapter-007.html` with both images attached; `python benchmarks/scorers/layout_linearization_scorer.py --chapters-dir /tmp/story135-build/html` returns `PASS`.
- **Patterns found:** the current crop module already contains the likely fix (`expected_count = len(ocr_images)` when multiple OCR `<img>` tags exist), but there is no dedicated regression test locking that behavior in.
- **Decision:** Treat Story 135 as a regression-verification story unless a fresh rerun uncovers another multi-image page that still fails. The implementation plan focuses on test coverage plus artifact regeneration, not a speculative cropper rewrite.
- **Next:** Add test coverage for multi-image expected-count handling, rerun the targeted artifact path through current code, then verify the acceptance criteria against regenerated outputs.

### 20260312-1710 — repurposed story around manual-review image defects
- **Result:** Re-scoped the story from the narrow historical page-21 crop miss to the broader set of image-facing fidelity issues found during manual review of `onward-story009-full`.
- **Scope now includes:** broken/missing page-21 bottom image, reviewed mid-sentence image placement on `chapter-011.html`, and swapped captions on `chapter-028.html`.
- **Scope explicitly excludes:** missing prose pages, chapter boundary defects, and genealogy table regressions; those now have separate follow-up stories.
- **Decision:** Keep the earlier page-21 investigation in the work log as baseline evidence, but make the story’s actual next work about image placement and caption fidelity in the final HTML output.

### 20260313-0905 — round-2 manual verification confirms image placement story still open
- **Result:** The rerun that fixed dropped content did not fix the image-placement and image-pairing defects.
- **Evidence:**
  - `output/runs/story137-onward-verify/output/html/chapter-010.html` still places the reviewed image inside the sentence `...made into <img> colorful bedspreads.`
  - `output/runs/story137-onward-verify/output/html/chapter-021.html` still has the reviewed swapped image pair
- **Decision:** Keep this story focused on the paragraph-boundary image-placement rule plus image/caption pairing. Do not bury these defects inside section-splitting or table stories.
- **Next:** Build this story against the current `story137-onward-verify` artifacts rather than the older `onward-story009-full` run.

### 20260313-1238 — Story 139 review confirms image-order and placement defects persist on the safe artifact set
- **Result:** Manual review of the page-safe `story139-onward-full127-composite-validate` run shows the image story is still open even after the Story 139 boundary repair and the validation-asset copy fix.
- **Evidence:**
  - `/Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-full127-composite-validate/output/html/chapter-003.html` still mis-orders the frontmatter logo/seal imagery
  - `/Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-full127-composite-validate/output/html/chapter-011.html`, `chapter-014.html`, and `chapter-024.html` still inject figures into the middle of sentences
  - `/Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-full127-composite-validate/output/html/chapter-011.html` and `chapter-028.html` still appear to have swapped image/caption pairing
- **Important distinction:** the earlier broken-image issue in this run was fixed by improving `load_artifact_v1` to copy sibling `images/` directories during artifact reuse. That validation plumbing issue is closed; the remaining defects are true placement/order/caption problems and belong in this story.
- **Next:** When building Story 135, use `story139-onward-full127-composite-validate` as the primary reviewed artifact set instead of the older unsafe `onward-story009-full` run.

### 20260315-1919 — build-story exploration: current scope narrowed to build-stage placement/order fixes, story promoted to active work
- **Result:** Promoted Story 135 to `In Progress`, confirmed it still closes a real Ideal gap, and traced the remaining failures to the build stage rather than reopening the solved historical crop detector bug.
- **Evidence:**
  - `/Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-full127-composite-validate/03_load_artifact_v1/illustration_manifest.jsonl` already includes both reviewed page-21 crops (`page-021-000.jpg`, `page-021-001.jpg`), so the old missing-bottom-image problem is upstream-fixed and now needs regression protection rather than detector changes.
  - `/Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-full127-composite-validate/output/html/chapter-011.html` and `/Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-full127-composite-validate/output/html/chapter-024.html` still split sentence fragments around figures, proving `_attach_images()` currently preserves bad placeholder placement instead of normalizing to paragraph boundaries.
  - `/Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-full127-composite-validate/05_table_fix_continuations_v1/pages_html_onward_tables_fixed.jsonl` for pages 38 and 108 shows OCR `<img alt>` placeholders in one order while the reused crop manifest rows are sorted by page bbox order in the opposite visual order; this explains the reviewed swaps in `chapter-011.html`, `chapter-021.html`, and `chapter-028.html`.
  - `/Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-full127-composite-validate/output/html/chapter-003.html` still linearizes the certificate frontmatter awkwardly, so the placement policy needs to cover non-narrative layouts too.
- **Files likely to change:** `modules/build/build_chapter_html_v1/main.py`, `tests/test_build_chapter_html.py`, and story docs. `modules/extract/crop_illustrations_guided_v1/main.py` remains out of scope unless implementation uncovers a real upstream ordering bug.
- **ADRs / decisions checked:** searched `docs/decisions/`; no dedicated ADR for figure placement was found. `adr-001-source-aware-consistency-strategy` only adds a guardrail against stuffing unrelated normalization logic into the build module.
- **Patterns to follow:** keep the fix deterministic and page-local using the existing BeautifulSoup rewrite pattern in `build_chapter_html_v1`, then validate via targeted `driver.py --start-from build_chapters` reuse instead of re-running expensive upstream OCR/crop stages.
- **Scope change folded in:** expanded manual verification from the older three chapters to the current reviewed verification set (`chapter-003`, `007`, `010`, `011`, `014`, `021`, `024`, `028`) because they are all manifestations of the same placement/order policy.
- **Next:** wait for approval on the written plan, then implement placement/order regressions in the build module, rerun from `build_chapters`, and inspect the rebuilt HTML artifacts manually.

### 20260315-2041 — implementation + validation: build-stage image matching and paragraph-boundary placement shipped
- **Result:** Story 135 is complete. `build_chapter_html_v1` now (1) expands OCR `data-count` image placeholders into multiple attachment slots, (2) matches crops to OCR image/caption blocks by descriptor text instead of raw order, and (3) stitches prose back together when a figure run interrupts a sentence within a page or across a page break.
- **Code changed:**
  - `modules/build/build_chapter_html_v1/main.py`
    - Added descriptor-based crop matching using crop `image_description` / `caption_text` against OCR image alt/caption text.
    - Added paragraph-boundary stitching for figure interruptions both within a page (`_stitch_figure_interruptions`) and across page breaks (`_stitch_page_breaks` + trailing-figure support).
    - Added `data-count` placeholder expansion so pages like source page 127 no longer silently drop one of multiple crops.
  - `tests/test_build_chapter_html.py`
    - Added regressions for swapped-pair matching, sentence-stitching around figure runs, cross-page figure interruption stitching, and multi-count placeholder expansion.
- **Validation run:** `python driver.py --recipe /Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-full127-composite-validate/snapshots/recipe.yaml --run-id story135-onward-image-placement-r1 --force`
- **Produced artifacts:** `output/runs/story135-onward-image-placement-r1/06_build_chapter_html_v1/chapters_manifest.jsonl` and rebuilt HTML under `output/runs/story135-onward-image-placement-r1/output/html/`
- **Manual artifact inspection (required):**
  - `output/runs/story135-onward-image-placement-r1/output/html/chapter-008.html`
    - Verified both page-21 figures attach cleanly with `page-021-000.jpg` (`Aerial view of ranch buildings and surrounding landscape`) and `page-021-001.jpg` (`Ranch house and barn with cattle in the foreground`); no broken/unmatched figure remains for the historical page-21 case.
  - `output/runs/story135-onward-image-placement-r1/output/html/chapter-011.html`
    - Verified the interrupted sewing paragraph now reads `...made into colorful bedspreads...` as a single paragraph.
    - Verified the first figure uses `page-038-001.jpg` with caption `Leonidas and Josephine (second wife) L'Heureux.` and the second uses `page-038-000.jpg` with caption `Mrs. Leonidas L'Heureux (Laetitia - first wife).`
  - `output/runs/story135-onward-image-placement-r1/output/html/chapter-014.html`
    - Verified the previous page-break split now reads `...Twin City tractor and 51 steel wheels...` as a single paragraph before the Emilienne figure.
  - `output/runs/story135-onward-image-placement-r1/output/html/chapter-020.html`
    - Verified the Isidore figure no longer splits `...until they could finally afford their own cow...`
  - `output/runs/story135-onward-image-placement-r1/output/html/chapter-022.html`
    - Verified the Pierre chapter pairing is corrected: `page-108-001.jpg` renders with `Pierre and Selina (second wife) L'Heureux, 1961.` and `page-108-000.jpg` renders with `Mrs. Pierre L'Heureux (Annie - first wife).`
  - `output/runs/story135-onward-image-placement-r1/output/html/chapter-003.html`
    - Initial DOM inspection looked correct, but later manual image review found the reused page-12 crops were stale: `page-012-000.jpg` still contained the seal crop and `page-012-001.jpg` still contained the signatures crop from `onward-full-127-table-fidelity`. The corrected review run below supersedes `r1` for this chapter.
  - `output/runs/story135-onward-image-placement-r1/output/html/chapter-024.html`
    - Verified the former page-127 mismatch is gone: both `page-127-000.jpg` and `page-127-001.jpg` attach in the rebuilt output.
- **Checks run:**
  - `python -m pytest tests/` → `603 passed, 6 skipped`
  - `python -m ruff check modules/ tests/` → clean
- **Central tenets verification:**
  - **T0 Traceability:** output figures retain source crop filenames (`data-crop-filename`) tied to the illustration manifest rows in `03_load_artifact_v1/illustration_manifest.jsonl`.
  - **T1 AI-First:** no new model call was added; the defect was deterministic build orchestration over existing OCR/crop artifacts.
  - **T2 Eval Before Build:** baseline defects were classified from the reviewed run before editing, targeted regressions were added first, and the fix was revalidated through `driver.py`.
  - **T3 Fidelity:** corrected image/caption pairing and restored paragraph continuity reduce source distortion instead of papering over it.
  - **T4 Modular:** the fix stays inside the generic build module and page-local matching helpers; no Onward page IDs or hardcoded title strings entered pipeline logic.
  - **T5 Inspect Artifacts:** verified directly in rebuilt HTML artifacts listed above, plus crop images reviewed during implementation for pages 38 and 108.
- **Decision:** mark Story 135 `Done`. No extractor/schema change was needed.

### 20260315-2058 — manual review reopened page-12 certificate imagery; corrected review run supersedes `r1`
- **Result:** Story 135 remains `Done`, but `story135-onward-image-placement-r2` is the final review artifact for `chapter-003.html`. The remaining issue was not a new build-module bug; it was stale reused crop data for source page 12 inside `story135-onward-image-placement-r1`.
- **Root cause:** `story135-onward-image-placement-r1` loaded page-12 crops from `onward-full-127-table-fidelity/03_crop_illustrations_guided_v1/illustration_manifest.jsonl`, where the manifest rows were mislabeled for this certificate page:
  - `page-012-000.jpg` carried alt text `Celebrate Saskatchewan 1905-1980 Logo` but its bbox (`x0=611, y0=4517, x1=1986, y1=5911`) was actually the lower-left seal.
  - `page-012-001.jpg` carried alt text `Official Seal of Saskatchewan` but its bbox (`x0=2200, y0=4751, x1=3700, y1=5606`) was actually the lower-right signatures block.
- **Correction path:**
  - Re-ran `crop_illustrations_guided_v1` for source page 12 only and confirmed the current cropper returns the correct top logo plus a bottom crop that combines the seal and signatures.
  - Built a targeted merged illustration manifest that replaced only the page-12 rows and images, then reran `driver.py` with a four-stage load-pages/load-portions/load-crops/build recipe to produce `story135-onward-image-placement-r2`.
- **Validation reference recipe:** `python driver.py --recipe /Users/cam/.codex/worktrees/831e/codex-forge/output/runs/story135-onward-image-placement-r2/snapshots/recipe.yaml --run-id <fresh-run-id> --force`
- **Produced artifacts:** `output/runs/story135-onward-image-placement-r2/04_build_chapter_html_v1/chapters_manifest.jsonl` and corrected HTML under `output/runs/story135-onward-image-placement-r2/output/html/`
- **Manual artifact inspection:**
  - `output/runs/story135-onward-image-placement-r2/output/html/images/page-012-000.jpg`
    - Verified the actual image content is the `Celebrate Saskatchewan 1905-1980` logo.
  - `output/runs/story135-onward-image-placement-r2/output/html/images/page-012-001.jpg`
    - Verified the actual image content is the bottom certificate block with the Saskatchewan seal beside the signatures.
  - `output/runs/story135-onward-image-placement-r2/output/html/chapter-003.html`
    - Verified the chapter now places the correct logo at the top and the seal/signature imagery in the bottom table cell, matching the intended certificate layout.
- **Impact:** `story135-onward-image-placement-r2` supersedes `r1` as the manual-review run for Story 135. The build-module code from the 2041 entry stands; only the reused page-12 crop artifact needed correction.

### 20260315-2106 — validate follow-up closed metadata drift in the Story 135 closeout trail
- **Result:** Corrected the remaining provenance/documentation gaps called out by `/validate` without changing Story 135 behavior.
- **Docs corrected:**
  - `CHANGELOG.md` now identifies `story135-onward-image-placement-r2` as the final validation artifact set for the story closeout.
  - This work log now cites the preserved run snapshot under `output/runs/story135-onward-image-placement-r2/snapshots/recipe.yaml` instead of the ephemeral `/tmp` recipe path used during the targeted rebuild.
  - `modules/build/build_chapter_html_v1/main.py` now documents descriptor-based image matching with positional fallback so the code comments match the implementation.
- **Smoke verification:** Re-opened `output/runs/story135-onward-image-placement-r2/output/html/chapter-003.html`, `output/runs/story135-onward-image-placement-r2/output/html/images/page-012-000.jpg`, and `output/runs/story135-onward-image-placement-r2/output/html/images/page-012-001.jpg`; the top logo and bottom seal/signature block remain correct.
- **Decision:** Story 135 closeout metadata is now consistent with the actual final reviewed artifacts.
