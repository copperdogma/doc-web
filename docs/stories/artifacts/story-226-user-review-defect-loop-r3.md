# Story 226 User Review Defect Loop R3

## Target

- Source page 5: `output/runs/story226-driver-build-r1/02_split_pages_from_manifest_v1/images/page-003R.png`
- Source page 6: `output/runs/story226-driver-build-r1/02_split_pages_from_manifest_v1/images/page-004L.png`
- Output chapter: `output/runs/story226-driver-build-r1/output/html/chapter-004.html`
- Affected crops:
  - `output/runs/story226-driver-build-r1/08_crop_illustrations_guided_v1/images/page-005-000.png`
  - `output/runs/story226-driver-build-r1/08_crop_illustrations_guided_v1/images/page-005-001.png`
  - `output/runs/story226-driver-build-r1/08_crop_illustrations_guided_v1/images/page-006-001.jpg`
- QA packet: `output/runs/story226-driver-build-r1/qa/user-review-defect-loop-r3/`

## What Looks Right

- The affected figures are in the correct chapter and generally near the correct semantic text.
- The placement-layout figure correctly attempts to preserve the relationship among the temporary card, installed upgrade cards, and player mat.
- The programming example diagram correctly keeps the yellow callout boxes as source-pixel figure content instead of converting them to detached prose.

## Problems Found

- `page-005-000.png` is a cost-card reference child, but the saved crop still carries detached prose/callout tail pixels. The explanatory prose is already represented as HTML, so it should not pollute the image.
- `page-005-001.png` preserves the spatial layout cluster, but surrounding semantic prose remains visible in the source-pixel crop. The prose belongs in HTML; the figure should preserve only the visual relationship.
- `page-006-001.jpg` cuts through the bottom of the integrated yellow callout boxes. Because those callouts are spatial labels pointing into the board diagram, they should be fully visible if kept as image pixels.

## Expected Behavior

- Cost-reference split children should trim to the source visual object while preserving useful internal visual highlights.
- Placement-layout split children should keep source-pixel spatial relationships but mask semantic prose that is merely adjacent to the visual cluster.
- Integrated callout diagrams should expand when the current bbox cuts through callout panels or their text.

## Generic Failure Classes

- **Detached-prose leakage in split rule-panel children**: a split visual child from a mixed prose+visual panel carries semantic prose into the image.
- **Sparse placement-layout prose leakage**: a rule-critical spatial layout has an irregular visual cluster, but plain instructional prose around it remains visible.
- **Integrated callout undercrop**: a VLM crop bbox cuts through callout panels whose text is part of the diagram.

## Fix Attempt

- Added a split cost-reference trim that uses the tall dark card-like body to remove detached prose/callout-tail pixels from mixed rule-panel children.
- Added a placement-layout lower safety margin and replaced broad placement-layout OCR masking with targeted upper-left prose-line masking that protects saturated visual objects.
- Added integrated-callout expansion for whole rule-example diagram targets whose colored callout panels continue below the VLM bbox.

## Rerun Evidence

- Driver rerun: `scripts/run_with_doc_web_env.py python driver.py --recipe configs/recipes/recipe-graphics-heavy-imposed-pdf-html-mvp.yaml --input-pdf input/f5-robo-rally-rulebook.pdf --run-id story226-driver-build-r1 --output-dir output/runs/story226-driver-build-r1 --start-from crop_illustrations --allow-run-id-reuse --instrument`
- Pipeline state: `output/runs/story226-driver-build-r1/pipeline_state.json` marks `crop_illustrations`, `normalize_manual_html`, `portionize_headings`, `build_chapters`, and `validate_manual_html` as `done`.
- Conformance: `output/runs/story226-driver-build-r1/12_validate_semantic_manual_html_v1/semantic_manual_html_conformance_report.json` reports 22 pass checks, 0 warnings, 0 failures, 32 logical pages, 127 crops, 120 HTML figures, and 495 provenance rows.
- Focused regression slice: `python -m pytest tests/test_plan_critical_graphics_vlm_v1.py tests/test_crop_illustrations_guided_v1.py tests/test_extract_page_numbers_html_v1.py tests/test_infer_logical_page_order_v1.py tests/test_normalize_graphic_manual_html_v1.py tests/test_portionize_headings_html_v1.py tests/test_graphic_manual_semantic_pipeline.py tests/test_build_chapter_html.py -q` passed with `179 passed`.
- Compile check: `python -m py_compile` passed for the touched runtime modules/tests.

## Reinspection Result

- `page-005-000.jpg` is now a tight card-reference crop with no detached prose. The card's source-pixel red highlight remains because it is part of the visual cue identifying the cost area.
- `page-005-001.png` keeps the temporary card, installed-upgrade cards, and player mat in one source-pixel spatial cluster. Browser-faithful rendering hides surrounding semantic prose while preserving the card/mat relationship.
- `page-006-001.jpg` now includes the full yellow callout boxes and their text; the bottom of the callouts is no longer cut off.
- `chapter-004-round3-upgrade.png` and `chapter-004-round3-programming.png` were manually opened after the rerun and match the expected semantic placement in `chapter-004.html`.

## Remaining Caveats

- The placement-layout figure remains an irregular transparent PNG because the rule-critical content is a sparse source layout rather than a rectangular figure. This is an acceptable plain-HTML tradeoff for this category.
- Full `make test` is still not freshly claimed for Story 226; the focused Story 226 regression slice and real driver/conformance path are freshly verified.
