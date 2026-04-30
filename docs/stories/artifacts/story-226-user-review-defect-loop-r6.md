# Story 226 User Review Defect Loop R6

## Target

- Source page: `output/runs/story226-driver-build-r1/02_split_pages_from_manifest_v1/images/page-005R.png`
- Output chapter: `output/runs/story226-driver-build-r1/output/html/chapter-004.html`
- Rejected crop: `output/runs/story226-driver-build-r1/output/html/images/page-009-000.jpg`
- QA packet: `output/runs/story226-driver-build-r1/qa/user-review-defect-loop-r6/`

## What Looks Right

- The Amanda register figure is correctly anchored beside the Amanda activation prose.
- The figure should include the Hammer Bot player mat identity, the register row, the Move 3 card, discard area, energy reserve, and remaining register cards.

## Problems Found

- `page-009-000.jpg` had a leftover prose line at the top: the introductory sentence above the first player mat was captured as image pixels.
- The defect was caused by the generic player-mat top expansion rule added for lower examples. It treated dark prose fragments above the first mat as candidate components for upward expansion.

## Expected Behavior

- Player-mat/register examples may expand upward to preserve mat identity/header components, but should ignore text-like dark rows above the figure.
- If prose has already been extracted semantically, it should not remain embedded in a source-pixel figure unless it is integrated diagram text.

## Generic Failure Class

- Top-edge player-mat expansion captured introductory prose instead of only visual mat/header components.

## Fix Attempt

- Tightened `_expand_player_mat_register_rule_example_box` to classify low-saturation, dark, wide/short components above the figure as text-like and exclude them from top-expansion candidates.
- Added a synthetic regression test where introductory prose sits above a player mat while a visual header still needs to be recovered.

## Rerun Evidence

- Driver rerun: `python driver.py --recipe configs/recipes/recipe-graphics-heavy-imposed-pdf-html-mvp.yaml --run-id story226-driver-build-r1 --allow-run-id-reuse --start-from crop_illustrations --force`
- Pipeline state: `output/runs/story226-driver-build-r1/pipeline_state.json` marks `crop_illustrations`, `build_chapters`, and `validate_manual_html` as `done` after the rerun.
- Conformance: `output/runs/story226-driver-build-r1/12_validate_semantic_manual_html_v1/semantic_manual_html_conformance_report.json` reports 22 pass checks, 0 warnings, 0 failures, 32 logical pages, 127 crops, 120 HTML figures, and 495 provenance rows.
- Crop manifest rows:
  - `page-009-000.jpg`: bbox changed from the rejected `y0=515,height=717` to `y0=596,height=636`, removing the prose line while preserving the Hammer Bot mat identity.
  - `page-009-004.jpg`: remains `y0=2410,height=644`, preserving the Twonky top mat identity from the prior fix.

## Reinspection Result

- Opened `output/runs/story226-driver-build-r1/output/html/images/page-009-000.jpg`: the introductory prose line is gone; the mat identity, installed-upgrade line, discard area, energy reserve, and register cards remain visible.
- Opened `output/runs/story226-driver-build-r1/output/html/images/page-009-004.jpg`: the prior Twonky/player-mat fix still holds.
- Opened browser-rendered figure screenshots:
  - `output/runs/story226-driver-build-r1/qa/user-review-defect-loop-r6/chapter-004-r6-amanda-register-figure.png`
  - `output/runs/story226-driver-build-r1/qa/user-review-defect-loop-r6/chapter-004-r6-chris-register-figure.png`

## Remaining Caveats

- Full `make test` remains unclaimed; this loop refreshed the real driver path, crop-specific tests, and visual inspection evidence.
