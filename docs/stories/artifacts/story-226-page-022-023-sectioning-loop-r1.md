# Story 226 Page 022-023 Sectioning Inspect/Fix/Rerun Loop R1

## Target

- Source pages: logical pages `22` and `23`
- Source authority: PDF-derived logical-page artifacts, not the user screenshot.
- Output under inspection: the course-catalog chapters in `output/runs/story226-driver-build-r1/output/html/`.

## QA Packet

- Source page 22: `output/runs/story226-driver-build-r1/manual-inspection-r6/page-022-023/source-page-022.png`
- Source page 23: `output/runs/story226-driver-build-r1/manual-inspection-r6/page-022-023/source-page-023.png`
- Pre-fix reconstructed portions: `output/runs/story226-driver-build-r1/manual-inspection-r6/page-022-023/portions-before.jsonl`
- Pre-fix reconstructed HTML screenshots:
  - `output/runs/story226-driver-build-r1/manual-inspection-r6/page-022-023/before-chapter-017.png`
  - `output/runs/story226-driver-build-r1/manual-inspection-r6/page-022-023/before-chapter-018.png`
- Post-fix screenshots:
  - `output/runs/story226-driver-build-r1/manual-inspection-r6/page-022-023/after-chapter-017.png`
  - `output/runs/story226-driver-build-r1/manual-inspection-r6/page-022-023/after-chapter-018.png`
- Post-fix HTML:
  - `output/runs/story226-driver-build-r1/output/html/chapter-017.html`
  - `output/runs/story226-driver-build-r1/output/html/chapter-018.html`
- Current conformance report: `output/runs/story226-driver-build-r1/12_validate_semantic_manual_html_v1/semantic_manual_html_conformance_report.json`

## What Looks Right

- The source pages clearly present one `ROBOTS. MUST. DIE. COURSES` difficulty section spread across pages 22 and 23.
- Page 22 contains the section heading plus `Pilgrimage` and `Gear Stripper`.
- Page 23 continues the same difficulty section with `Extra Crispy` and `Burn Run`; it does not introduce a new top-level section before `Card Index`.
- Keeping the broader `RACING COURSES` material split by difficulty category remains reasonable for now: the source has explicit difficulty headings and the resulting chunks are navigable. The defect was not "all course pages must be one chapter"; it was a lower-level course entry being promoted to a chapter.

## Problems Found

- The pre-fix chapter manifest split `ROBOTS. MUST. DIE. COURSES` as only page 22.
- `EXTRA CRISPY` became its own top-level chapter on page 23 because the recipe scans both `h1` and `h2` headings for heavily designed manuals.
- That made the top/bottom navigation misleading: `ROBOTS. MUST. DIE. COURSES` linked next to `EXTRA CRISPY`, then `EXTRA CRISPY` linked next to `CARD INDEX`.
- The conformance report did not catch the sectioning defect before this loop.

## Expected Behavior

- Category-like lower headings such as `INTERMEDIATE COURSES` may start a top-level output chunk when the source omits an `h1`.
- Lower-level catalog/reference item headings followed by label/value metadata such as `Game Length`, `Boards`, and `Special Rules` should remain inside their parent category section.
- A validator should flag this failure class if it recurs.

## Generic Failure Class

When a recipe scans lower-level headings to recover section boundaries in a graphic-designed manual, repeated catalog item headings can look like chapter starts. The generic signal is not a title string; it is a lower-level heading followed immediately by repeated label/value metadata.

This applies to course catalogs, card indexes, parts catalogs, quick-reference manuals, gear lists, spell/item references, and other designed reference sections.

## Fix Attempt

- Added `suppress_lower_heading_item_boundaries` to `portionize_headings_html_v1`.
- Enabled that knob only for the graphics-heavy imposed-PDF recipe.
- The policy keeps category-like lower headings as section boundaries but suppresses lower-level item headings with immediate label/value metadata.
- Added `source_heading_tag` to emitted portion rows so the boundary source remains inspectable.
- Added `lower_item_headings_do_not_start_chapters` to `validate_semantic_manual_html_v1` so this class cannot silently pass conformance.

## Rerun Evidence

- Reran:
  - `python driver.py --recipe configs/recipes/recipe-graphics-heavy-imposed-pdf-html-mvp.yaml --input-pdf input/f5-robo-rally-rulebook.pdf --run-id story226-driver-build-r1 --output-dir output/runs/story226-driver-build-r1 --start-from portionize_headings --allow-run-id-reuse --instrument`
  - `python driver.py --recipe configs/recipes/recipe-graphics-heavy-imposed-pdf-html-mvp.yaml --input-pdf input/f5-robo-rally-rulebook.pdf --run-id story226-driver-build-r1 --output-dir output/runs/story226-driver-build-r1 --start-from validate_manual_html --allow-run-id-reuse --instrument`
- Current portions:
  - `ROBOTS. MUST. DIE. COURSES` now covers source pages `[22, 23]`.
  - `CARD INDEX` starts at source page `[24]`.
- Current conformance report: `20` pass checks, `0` warnings, `0` failures.
- Focused tests:
  - `python -m pytest tests/test_portionize_headings_html_v1.py tests/test_graphic_manual_semantic_pipeline.py -q` passed with `8 passed`.
  - `python -m py_compile modules/portionize/portionize_headings_html_v1/main.py modules/validate/validate_semantic_manual_html_v1/main.py` passed.

## Reinspection Result

- `after-chapter-017.png` shows one `ROBOTS. MUST. DIE. COURSES` chapter containing `Pilgrimage`, `Gear Stripper`, `Extra Crispy`, and `Burn Run`.
- `after-chapter-018.png` is now `CARD INDEX`, with back navigation to `ROBOTS. MUST. DIE. COURSES`.
- The fix preserved the difficulty-level split for `RACING COURSES`, including `INTERMEDIATE COURSES` as an `h2`-derived category section, while suppressing the `EXTRA CRISPY` item boundary.

## Remaining Caveats

- Whether `RACING COURSES` should be a single larger chapter or split by difficulty remains a product/navigation choice. This loop only fixes the objectively wrong split inside one difficulty section.
- The policy is intentionally conservative and recipe-scoped. Broader claims should come from maintained fixtures/evals across more graphic-designed reference catalogs.
