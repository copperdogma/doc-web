# Story 226 User Review Defect Loop R4

## Target

- Source page 5: `output/runs/story226-driver-build-r1/02_split_pages_from_manifest_v1/images/page-003R.png`
- Source page 6: `output/runs/story226-driver-build-r1/02_split_pages_from_manifest_v1/images/page-004L.png`
- Output chapter: `output/runs/story226-driver-build-r1/output/html/chapter-004.html`
- Affected crops:
  - `output/runs/story226-driver-build-r1/08_crop_illustrations_guided_v1/images/page-005-000.jpg`
  - `output/runs/story226-driver-build-r1/08_crop_illustrations_guided_v1/images/page-005-001.png`
  - `output/runs/story226-driver-build-r1/08_crop_illustrations_guided_v1/images/page-006-001.jpg`
- QA packet: `output/runs/story226-driver-build-r1/qa/user-review-defect-loop-r4/`

## What Looks Right

- The cost card, placement layout, and programming example are all attached to the correct semantic anchors in `chapter-004.html`.
- The placement layout correctly keeps the temporary card, installed upgrade cards, player mat, and connector lines as one relationship-preserving figure.
- The programming example correctly treats the yellow numbered callouts as integrated source-pixel diagram content.

## Problems Found

- The cost-card reference crop no longer carries prose, but it still shows a detached red callout tail running to the crop edge. Because the explanatory prose is semantic HTML, a callout tail with no target is visual noise.
- The placement-layout crop is semantically better, but the visible artifact is still a prose-erased rectangle with stair-stepped transparent/white holes. The figure should look like a clean source-pixel visual cluster, not a masked page excerpt.
- The programming example diagram now includes the full yellow callouts, but it over-expanded into decorative footer/hazard-tape chrome and still duplicates the spatial callout text as a figcaption.

## Expected Behavior

- Cost-reference children may preserve source-pixel card/cost highlighting, but detached guide-line tails that point to removed prose should be hidden.
- Sparse placement-layout children should preserve visual components and their spatial relationships while dropping ordinary surrounding prose/background bands.
- Integrated callout diagrams should expand only to the nearby callout panels, not to detached page decoration below the diagram.
- Spatial callout text that is already inside an integrated source-pixel diagram should not be duplicated as a figcaption.

## Generic Failure Classes

- **Detached guide-line tail after semantic extraction**: a line originally pointing from a visual to prose remains after the prose has moved to HTML.
- **Sparse layout cluster rendered as prose-erased page excerpt**: a relationship-preserving visual has non-rectangular content, but masking text inside a broad crop leaves visible artifact holes.
- **Detached decoration captured by callout expansion**: a saturated footer/chrome region below a diagram is mistaken for a continuation of the integrated callout panels.
- **Spatial callout caption duplication**: integrated diagram labels are preserved as source pixels and also emitted as a separate figcaption.

## Fix Attempt

- Added a cost-reference post-crop mask for thin red horizontal rules that touch the crop edge and sit below the cost-corner region.
- Reworked placement-layout masking to build a transparent visual-cluster image from detected visual components and grouped layout regions rather than only erasing OCR prose lines.
- Replaced row-projection integrated-callout expansion with connected-component expansion limited to nearby colored panels.
- Added HTML caption dedupe for numbered callout captions on `rule_example_diagram` figures when the text is already represented by integrated diagram metadata.

## Rerun Evidence

- Driver rerun: `scripts/run_with_doc_web_env.py python driver.py --recipe configs/recipes/recipe-graphics-heavy-imposed-pdf-html-mvp.yaml --input-pdf input/f5-robo-rally-rulebook.pdf --run-id story226-driver-build-r1 --output-dir output/runs/story226-driver-build-r1 --start-from crop_illustrations --allow-run-id-reuse --instrument`
- Pipeline state: `output/runs/story226-driver-build-r1/pipeline_state.json` marks `crop_illustrations`, `normalize_manual_html`, `portionize_headings`, `build_chapters`, and `validate_manual_html` as `done` after the rerun.
- Conformance: `output/runs/story226-driver-build-r1/12_validate_semantic_manual_html_v1/semantic_manual_html_conformance_report.json` reports `overall_status=pass`, 22 pass checks, 0 warnings, 0 failures, 32 logical pages, 127 crops, 120 HTML figures, and 495 provenance rows.
- Focused regression check: `python -m pytest tests/test_crop_illustrations_guided_v1.py tests/test_build_chapter_html.py -q` passed with `157 passed`.
- QA packet:
  - `output/runs/story226-driver-build-r1/qa/user-review-defect-loop-r4/source-and-current-crops-white.jpg`
  - `output/runs/story226-driver-build-r1/qa/user-review-defect-loop-r4/chapter-004-r4-upgrade.png`
  - `output/runs/story226-driver-build-r1/qa/user-review-defect-loop-r4/chapter-004-r4-programming.png`
  - `output/runs/story226-driver-build-r1/qa/user-review-defect-loop-r4/manifest-rows.json`

## Reinspection Result

- `page-005-000.jpg` is now a clean cost-reference crop focused on the card's cost corner and upper card art. It no longer carries the detached horizontal callout tail or surrounding prose.
- `page-005-001.png` now renders in HTML as a clean placement-layout cluster: temporary card, installed upgrade cards, red connector/label, and player mat remain spatially related, while the ordinary prose/note text is not part of the image.
- `page-006-001.jpg` keeps the full integrated yellow callout boxes and board diagram, but no longer includes the lower-left hazard-tape/footer decoration.
- `chapter-004-r4-upgrade.png` and `chapter-004-r4-programming.png` were opened after the rerun. The upgrade figures sit beside their relevant prose, and the programming diagram no longer has a duplicated figcaption below the image.

## Remaining Caveats

- `page-005-001.png` remains a sparse transparent layout figure, so it has source-relative empty space. That is an acceptable plain-HTML tradeoff because the spatial relation among the cards and mat is the rule-critical content.
- The driver summary still prints a stale `crop_illustrations` failure summary, but the current `pipeline_state.json`, refreshed artifacts, and conformance report show the rerun completed successfully. This stale summary is a separate reporting hygiene issue, not a crop-quality blocker for this loop.
