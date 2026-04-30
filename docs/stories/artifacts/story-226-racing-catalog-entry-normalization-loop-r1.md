# Story 226 - Racing Catalog Entry Normalization Loop R1

## Target

- Source: `output/runs/story226-driver-build-r1/manual-inspection-r8/racing-catalog-entries/source-pages-016-023-contact-sheet.jpg`
- Output: `output/runs/story226-driver-build-r1/manual-inspection-r8/racing-catalog-entries/after-racing-courses-chapter-012.png`
- Nearby output check: `output/runs/story226-driver-build-r1/manual-inspection-r8/racing-catalog-entries/after-card-index-chapter-013.png`
- Intermediates:
  - `output/runs/story226-driver-build-r1/output/html/chapter-012.html`
  - `output/runs/story226-driver-build-r1/output/html/chapter-013.html`
  - `output/runs/story226-driver-build-r1/12_validate_semantic_manual_html_v1/semantic_manual_html_conformance_report.json`

## What Looks Right

- The `RACING COURSES` chapter is now one parent chapter, with difficulty headings nested underneath it.
- The source pages present each course as a repeated catalog entry: title, board/course image, game length, boards, and special rules.
- The final HTML preserves source-pixel course maps and keeps the textual course metadata as HTML, not pixels.

## Problems Found

- The pre-fix Racing Courses output represented the same kind of course entry in three different ways:
  - `figure + h3 + p` for entries such as Risky Crossing.
  - `dl.semantic-entry-list + figure` for entries such as Burnout.
  - `p strong-title + figure + p` for entries such as Undertow.
- That was semantically noisy for an AI reader even though the text and figures were present.
- After adding the first grouping check, the validator also caught the same generic failure in the nearby `CARD INDEX` chapter for `h3 + figure + p` card entries.

## Expected Behavior

- In catalog/index chapters, a repeated entry with a figure, compact label, and label/value metadata should become one semantic block.
- The block should have a consistent structure: entry heading, source-pixel figure, then metadata/body text.
- This should apply to generic catalog/reference shapes, not to one document title or one exact page.

## Generic Failure Class

Graphics-heavy catalog pages often arrive from OCR/crop placement as adjacent sibling fragments rather than one semantic entry. The pipeline needs a class-based grouping pass for catalog entry fragments near essential figures.

## Fix Attempt

- Added recipe-scoped `normalize_catalog_entries` to `build_chapter_html_v1`.
- Added generic catalog-entry grouping for these observed patterns:
  - `figure + heading + metadata`
  - `heading + figure + metadata`
  - `definition-list entry + figure`
  - `strong-label paragraph + figure + metadata`
- Added `catalog_entries_group_figures_labels_and_metadata` to `validate_semantic_manual_html_v1`.
- Enabled the new builder knob in `recipe-graphics-heavy-imposed-pdf-html-mvp.yaml`.

## Rerun Evidence

- Driver rerun: `python driver.py --recipe configs/recipes/recipe-graphics-heavy-imposed-pdf-html-mvp.yaml --input-pdf input/f5-robo-rally-rulebook.pdf --run-id story226-driver-build-r1 --output-dir output/runs/story226-driver-build-r1 --start-from build_chapters --allow-run-id-reuse --instrument`
- Current Racing Courses structure: `chapter-012.html` has 18 `section.semantic-catalog-entry` blocks and 19 figures.
- Current Card Index nearby check: `chapter-013.html` has 25 `section.semantic-catalog-entry` blocks.
- Current conformance: 22 checks, 22 pass, 0 warn, 0 fail.

## Reinspection Result

- Reopened the source contact sheet and refreshed output screenshots after the final `build_chapters` rerun.
- Racing Courses now reads as a consistent catalog: each course entry from Risky Crossing through Burn Run has a heading, the correct source-pixel map, and metadata underneath.
- Card Index did not regress under the generic normalizer; the nearby output keeps card images and text entries attached, and the new validator check passes there too.

## Remaining Caveats

- The starter course remains a slightly richer setup entry with an introductory line and ordered setup steps. That is acceptable because it is not the same repeated catalog-entry shape as the later course entries.
- Some card-reference entries without individual source-pixel figures remain definition-list entries. The normalizer intentionally groups only entries with a nearby catalog figure, label, and metadata.
