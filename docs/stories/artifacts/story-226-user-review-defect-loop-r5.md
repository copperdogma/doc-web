# Story 226 User Review Defect Loop R5

## Target

- Source page for cost-card crop: `output/runs/story226-driver-build-r1/02_split_pages_from_manifest_v1/images/page-003R.png`
- Source page for activation/register crop: `output/runs/story226-driver-build-r1/02_split_pages_from_manifest_v1/images/page-005R.png`
- Current output: `output/runs/story226-driver-build-r1/output/html/chapter-004.html`
- Current crops:
  - `output/runs/story226-driver-build-r1/08_crop_illustrations_guided_v1/images/page-005-000.jpg`
  - `output/runs/story226-driver-build-r1/08_crop_illustrations_guided_v1/images/page-009-004.jpg`
- QA packet: `output/runs/story226-driver-build-r1/qa/user-review-defect-loop-r5/`

## What Looks Right

- The surrounding `chapter-004.html` structure is now good enough that the user called out only two crop defects in this review round.
- The cost-card crop is correctly anchored beside the purchase-cost prose and correctly removes the detached right-side prose.
- The Chris register example is correctly placed in the activation sequence and preserves the lower register cards, discard area, and energy reserve.

## Problems Found

- `page-005-000.jpg` is materially overcropped vertically. It shows only the top/art portion of the upgrade card and cuts off the bottom half of the card. This happened because the cost-reference cleanup treated a horizontal annotation tail as permission to trim the crop height.
- `page-009-004.jpg` cuts off the top of the Twonky player mat. The crop includes most of the mat but loses the robot/name marker and part of the top mat outline, which are source-pixel visual content for identifying the example.

## Expected Behavior

- A split cost-reference crop may trim detached prose to the right of the visual object, but it should not shorten the visual object vertically. A visible annotation line inside the source object is preferable to mutilating the object.
- A player-mat/register example should expand upward when the crop boundary intersects or nearly intersects colored/dark mat components immediately above it.

## Generic Failure Class

- Object-preserving crop cleanup: when a cleanup signal conflicts with source-object completeness, preserve the complete object and only trim detached text/prose outside the object bounds.
- Top-edge undercrop on register/player-mat rule examples: use generic visual continuity near the top edge, plus semantic cues such as player mat/register/discard/energy reserve, to expand the bbox.

## Fix Attempt

- Changed `crop_illustrations_guided_v1` so cost-reference children trim the detached right-side prose but no longer trim vertically based on annotation tails.
- Removed the cost-reference callout-tail masking path from the crop save sequence. It was trying to improve a cosmetic annotation artifact after the real semantic need had already been met by preserving the source object.
- Added a generic player-mat/register top expansion pass for rule-example diagrams whose expected contents mention player mats, registers, discard areas, or energy reserves.
- Added focused crop tests for both behavior classes.

## Rerun Evidence

- Driver rerun: `python driver.py --recipe configs/recipes/recipe-graphics-heavy-imposed-pdf-html-mvp.yaml --run-id story226-driver-build-r1 --allow-run-id-reuse --start-from crop_illustrations --force`
- Pipeline state: `output/runs/story226-driver-build-r1/pipeline_state.json` marks `crop_illustrations`, `normalize_manual_html`, `portionize_headings`, `build_chapters`, and `validate_manual_html` as `done` after the rerun.
- Conformance: `output/runs/story226-driver-build-r1/12_validate_semantic_manual_html_v1/semantic_manual_html_conformance_report.json` reports 22 pass checks, 0 warnings, 0 failures, 32 logical pages, 127 crops, 120 HTML figures, and 495 provenance rows.
- Crop manifest rows:
  - `page-005-000.jpg`: bbox changed from the rejected `300x242` vertical undercrop to `300x433` (`x0=300,y0=1710,x1=600,y1=2143`).
  - `page-009-004.jpg`: bbox expanded upward from `y0=2494` to `y0=2410`, producing `963x644` and preserving the top player-mat identity area.
- Focused checks: `python -m pytest tests/test_crop_illustrations_guided_v1.py tests/test_build_chapter_html.py -q` passed with `157 passed`; `python -m py_compile modules/extract/crop_illustrations_guided_v1/main.py tests/test_crop_illustrations_guided_v1.py` passed; `make lint`, `make methodology-compile`, `make methodology-check`, `make skills-check`, and `git diff --check` passed.

## Reinspection Result

- Opened the regenerated crop `output/runs/story226-driver-build-r1/08_crop_illustrations_guided_v1/images/page-005-000.jpg`: the full card object is present, including the bottom half and rounded card bottom. The source red annotation line remains, but it no longer caused destructive cropping.
- Opened the regenerated crop `output/runs/story226-driver-build-r1/08_crop_illustrations_guided_v1/images/page-009-004.jpg`: the Twonky identity marker, top mat border, installed-upgrades label area, discard area, energy reserve, and register cards are all visible.
- Opened browser-rendered figure screenshots:
  - `output/runs/story226-driver-build-r1/qa/user-review-defect-loop-r5/chapter-004-r5-cost-card-figure.png`
  - `output/runs/story226-driver-build-r1/qa/user-review-defect-loop-r5/chapter-004-r5-chris-register-figure.png`
  Both rendered figures now preserve the called-out visual content in the final HTML.

## Remaining Caveats

- The cost-card crop may still include the red source annotation line that crosses the card. That is acceptable if removing it would damage the source object; the semantic text remains outside the image.
- Full `make test` remains unclaimed in this story pass; focused Story 226 crop/build regression and the real driver rerun were refreshed.
