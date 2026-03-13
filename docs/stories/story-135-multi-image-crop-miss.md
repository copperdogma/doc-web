# Story 135 — Onward Image Placement and Caption Fidelity

**Priority**: High
**Status**: Pending
**Ideal Refs**: Requirement #4 (Illustrate), Requirement #5 (Structure), Fidelity to Source
**Spec Refs**: C3 (layout detection), C4 (two-stage crop detection), C5 (layout text trim heuristics)
**Depends On**: Story 126 (crop detection pipeline), Story 129 (HTML output polish)

## Goal

Fix the remaining image-facing fidelity defects in the Onward HTML output after manual review of `onward-story009-full`: missing/broken image attachment, swapped captions, and image placement that violates single-column reading flow.

The guiding rule for this story is: **in single-column HTML, images should appear between paragraphs unless there is a strong, source-faithful reason to do otherwise.** Mid-sentence insertion is the exception, not the default.

## Acceptance Criteria

- [ ] The reviewed page-21 image pair renders with no broken or unmatched `<figure>` elements, including the bottom "Ranch house and barn" image
- [ ] The reviewed family-story chapters in the current verification run no longer place images mid-sentence; images render at block boundaries consistent with single-column reading flow
- [ ] The reviewed swapped image/caption pair in the current verification run is assigned correctly
- [ ] A placement policy is documented and enforced: default to paragraph-boundary image placement unless a stronger source-faithful interpretation is explicitly justified
- [ ] Manual review of the fixed chapters confirms image attachment, caption pairing, and placement are accurate

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

- [ ] Re-run the reviewed image chapters with current code and classify each defect as crop, caption pairing, or chapter-assembly placement
- [ ] Verify whether the historical page-21 defect is already fixed in current crop output; if so, preserve that behavior with regression coverage rather than re-solving it
- [ ] Implement paragraph-boundary placement rules so reviewed images are not inserted mid-sentence by default
- [ ] Fix caption pairing for the reviewed `chapter-028.html` image pair
- [ ] Rebuild and manually verify `chapter-007.html`, `chapter-011.html`, and `chapter-028.html`
- [ ] Run required checks:
  - [ ] `python -m pytest tests/`
  - [ ] `python -m ruff check modules/ tests/`
- [ ] Search all docs and update any related to what we touched
- [ ] Verify Central Tenets:
  - [ ] T0 — Traceability
  - [ ] T1 — AI-First
  - [ ] T2 — Eval Before Build
  - [ ] T3 — Fidelity
  - [ ] T4 — Modular
  - [ ] T5 — Inspect Artifacts

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
- The historical page-21 crop miss may already be fixed in current code; if so, this story should focus on locking in the fix and addressing the remaining placement/caption defects.
- Placement policy for this story: prefer image blocks between paragraphs over literal cross-column interleaving when linearizing into single-column HTML.

## Plan

{Written by build-story Phase 2}

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
