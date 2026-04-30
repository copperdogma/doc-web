# Story 226 Page 022 Inspect/Fix/Rerun Loop R1

## Page Selection

- Selected logical page: `22`
- Reason: high-signal course-layout page with two large irregular board maps, nearby prose labels, decorative page chrome, and a different failure class from card faces or text-only callouts.
- Source authority: the page was located from PDF-derived logical-page artifacts and `chapter-017.html`, not from the pasted screenshot.

## QA Packet

- Original page: `output/runs/story226-driver-build-r1/manual-inspection-r5/page-022/source-page-022.jpg`
- Crop sheet before fix: `output/runs/story226-driver-build-r1/manual-inspection-r5/page-022/crop-sheet-page-022.jpg`
- Crop sheet after fix: `output/runs/story226-driver-build-r1/manual-inspection-r5/page-022/crop-sheet-page-022-after.png`
- Final HTML screenshot before fix: `output/runs/story226-driver-build-r1/manual-inspection-r5/page-022/chapter-017-before.png`
- Final HTML screenshot after fix: `output/runs/story226-driver-build-r1/manual-inspection-r5/page-022/chapter-017-after.png`
- Final HTML: `output/runs/story226-driver-build-r1/output/html/chapter-017.html`
- Critical graphics manifest excerpt: `output/runs/story226-driver-build-r1/manual-inspection-r5/page-022/critical-graphics-page-022.json`
- Crop manifest excerpt: `output/runs/story226-driver-build-r1/manual-inspection-r5/page-022/crop-manifest-page-022.json`
- Conformance report: `output/runs/story226-driver-build-r1/12_validate_semantic_manual_html_v1/semantic_manual_html_conformance_report.json`

## Manual Source-vs-Output Notes

- The two course maps are essential source-pixel figures. The text alone does not encode board placement, checkpoint positions, belts, pits, or start-board attachment.
- The visual planner correctly classified both targets as `map_or_board` and preserved board/map intent with target ids `p022-g01` and `p022-g02`.
- The pre-fix crops preserved the maps but also included nearby prose labels at the lower left: `PILGRIMAGE`, `GEAR STRIPPER`, and fragments of `Game Length`. Those labels are not integrated into the map graphic; they are already semantic headings/prose in the HTML.
- A simple rectangular crop cannot avoid all surrounding blank paper because the map shape is irregular: the lower start-board extension sits below the main map, while the label text sits in a different lower corner.
- Decorative hazard stripes, side tab, page gear, footer, and printer marks remain out of final semantic content.

## Generic Failure Class Found

Irregular map/board crops can require a rectangle that includes lower-corner prose labels. The labels should remain semantic HTML, but trimming the rectangle would cut off essential map extensions.

This is not Robo Rally-specific. It applies to game maps, floor plans, board layouts, route diagrams, and other irregular spatial graphics in heavily designed manuals.

## Code Change

- `crop_illustrations_guided_v1` now allows `map_or_board` crops to emit transparent PNG assets when detached lower-edge prose is detected inside the crop rectangle.
- The masking is conservative: it targets prose-like components in lower edge/corner regions and leaves retained board pixels unchanged.
- The cropper keeps the same source bbox/provenance and publishes PNG filenames for those map assets even when the recipe output format is JPEG.
- Focused regression tests cover the map masking helper and the end-to-end cropper path that emits a transparent PNG for a `map_or_board` crop with detached edge text.

## Rerun Evidence

- Cleared stale crop/build module pyc files.
- Reran:
  - `python driver.py --recipe configs/recipes/recipe-graphics-heavy-imposed-pdf-html-mvp.yaml --input-pdf input/f5-robo-rally-rulebook.pdf --run-id story226-driver-build-r1 --output-dir output/runs/story226-driver-build-r1 --start-from crop_illustrations --allow-run-id-reuse --instrument`
- Driver reused upstream page-map/OCR/critical-graphics artifacts and reran crop, normalize, portionize, build, and validate stages.
- Result: `Semantic manual conformance: pass`.
- Current conformance report: `19` pass checks, `0` warnings, `0` failures.
- Focused crop test evidence: `python -m pytest tests/test_crop_illustrations_guided_v1.py -q` passed with `12 passed`.

## Reinspection Result

- `chapter-017.html` now references `images/page-022-000.png` and `images/page-022-001.png`.
- Both page-22 map figures still carry `data-critical-graphics-role="map_or_board"`, `data-critical-graphics-importance="essential"`, and their planner target ids.
- The course labels are no longer readable inside the map figures; the corresponding `PILGRIMAGE` and `GEAR STRIPPER` headings/prose remain semantic HTML below each map.
- The central map content and lower start-board extensions remain visible after tightening the detector to avoid masking central map/checkpoint pixels.

## Remaining Caveats

- The transparent prose masks render as plain background patches where the source page had label text. This is preferable to duplicating prose inside the image, but a future visual-polish pass could replace rectangular word masks with cleaner background-aware clipping or a true polygonal crop.
- The QA packet is still a single-page proof for this failure class. Broader claims about arbitrary map documents still need maintained fixtures/evals.
