# Story 226 - Racing Courses Catalog Sectioning Loop R1

## Target

- Source: `output/runs/story226-driver-build-r1/manual-inspection-r7/racing-courses/source-pages-016-023-contact-sheet.jpg`
- Output: `output/runs/story226-driver-build-r1/manual-inspection-r7/racing-courses/after-racing-courses-chapter-012.png`
- Nearby output check: `output/runs/story226-driver-build-r1/manual-inspection-r7/racing-courses/after-card-index-chapter-013.png`
- Intermediates:
  - `output/runs/story226-driver-build-r1/10_portionize_headings_html_v1/portions_headings.jsonl`
  - `output/runs/story226-driver-build-r1/11_build_chapter_html_v1/chapters_manifest.jsonl`
  - `output/runs/story226-driver-build-r1/12_validate_semantic_manual_html_v1/semantic_manual_html_conformance_report.json`

## What Looks Right

- The source contact sheet shows `RACING COURSES` as the parent section starting on logical page 16 and continuing through the course catalog on logical pages 17-23.
- The difficulty bands are source subsections of that parent section: starter, beginner, intermediate, advanced, and robots-must-die courses.
- Logical page 23 continues the robots-must-die difficulty band with `EXTRA CRISPY` and `BURN RUN`; it is not a new top-level manual chapter.
- The table-of-contents/source hierarchy also makes `CARD INDEX` a parent catalog section across logical pages 24-31, with programming/special/upgrade/card categories nested underneath it.

## Problems Found

- The earlier page-22/23 fix prevented low-level course names from becoming top-level chapters, but it still treated source category headings such as `BEGINNER COURSES`, `INTERMEDIATE COURSES`, and `ROBOTS. MUST. DIE. COURSES` as sibling chapters instead of nested subsections under `RACING COURSES`.
- After merging catalog subsections, one category heading with sentence-like punctuation was visually present but flattened to `<p class="flattened-heading">ROBOTS. MUST. DIE. COURSES</p>` instead of remaining an actual subsection heading.

## Expected Behavior

- A catalog/index parent heading should own the related catalog pages when later page-level headings share the same catalog family and the source hierarchy implies a continued catalog.
- Difficulty/category bands inside a catalog should remain nested subsections.
- Individual catalog entries should remain inside the parent catalog section rather than splitting into separate manual chapters.
- Oversized-warning flattening should still protect true prose warnings, but it should not flatten short catalog category headings just because the title contains punctuation.

## Generic Failure Class

Page-local OCR heading tags over-fragment catalog/index sections in graphics-heavy manuals. The pipeline needs a generic catalog-parent merge and polish pass that uses catalog-family terms, label/value metadata, and source-heading hierarchy instead of trusting every page-local `h1`/`h2` as a chapter boundary.

## Fix Attempt

- Added the recipe-scoped `merge_catalog_subsections` option to `portionize_headings_html_v1`.
- Added generic catalog-parent detection and subsection-boundary merging for catalog/index/reference/course/card-style parents.
- Extended `build_chapter_html_v1` so catalog chapters preserve nested category headings and demote item headings followed by label/value metadata.
- Adjusted heading polishing so short catalog category headings with punctuation are recognized before the oversized-heading flattening safeguard.
- Added validator coverage with `catalog_subsections_stay_with_parent`, while preserving the earlier `lower_item_headings_do_not_start_chapters` check.

## Rerun Evidence

- Driver rerun: `python driver.py --recipe configs/recipes/recipe-graphics-heavy-imposed-pdf-html-mvp.yaml --input-pdf input/f5-robo-rally-rulebook.pdf --run-id story226-driver-build-r1 --output-dir output/runs/story226-driver-build-r1 --start-from build_chapters --allow-run-id-reuse --instrument`
- Current portions:
  - `RACING COURSES` -> source pages `[16, 17, 18, 19, 20, 21, 22, 23]`
  - `CARD INDEX` -> source pages `[24, 25, 26, 27, 28, 29, 30, 31]`
  - `SUMMARY OF A ROUND` -> source page `[32]`
- Current semantic conformance: 21 checks, 21 pass, 0 warn, 0 fail.
- Focused checks passed before final documentation:
  - `python -m pytest tests/test_build_chapter_html.py -k 'catalog_chapters or oversized' -q`
  - `python -m py_compile modules/build/build_chapter_html_v1/main.py`

## Reinspection Result

- Reopened the source contact sheet and refreshed output screenshots after the final `build_chapters` rerun.
- `chapter-012.html` now has one `h1 RACING COURSES` containing:
  - `h2 STARTER COURSE: DIZZY HIGHWAY`
  - `h2 BEGINNER COURSES`
  - `h2 INTERMEDIATE COURSES`
  - `h2 ADVANCED COURSES`
  - `h2 ROBOTS. MUST. DIE. COURSES`
- The robots-must-die pages are no longer split from the parent racing-course chapter, and `ROBOTS. MUST. DIE. COURSES` is a real `h2`, not a flattened paragraph.
- `chapter-013.html` is now one `CARD INDEX` chapter spanning the card reference pages, matching the same catalog-parent policy.

## Remaining Caveats

- This loop fixed section hierarchy, not all catalog-entry presentation. Racing-course entries are semantically present, but the builder still represents some entries as `h3` headings and some as `<dl class="semantic-entry-list">` terms depending on OCR shape. A later catalog-entry normalization pass could make that representation more consistent.
- Some individual course-map crops still include masked whitespace from text-removal around irregular board shapes. The source-pixel figures are rule-useful, but a later crop-placement/order loop should inspect the whole racing-course catalog if this section becomes the next quality target.
