# Story 226 Card Index Visual Inspect Loop R1

## Target
- Source: `output/runs/story226-driver-build-r1/manual-inspection-r9/card-index/source-pages-024-031-contact-sheet.jpg`
- Output before: `output/runs/story226-driver-build-r1/manual-inspection-r9/card-index/chapter-013-before-full.png`
- Output after: `output/runs/story226-driver-build-r1/manual-inspection-r9/card-index/chapter-013-after-full.png`
- Segmented after screenshots: `output/runs/story226-driver-build-r1/manual-inspection-r9/card-index/chapter-013-after-segment-01.png` through `chapter-013-after-segment-17.png`
- Final HTML: `output/runs/story226-driver-build-r1/output/html/chapter-013.html`
- Intermediates: `output/runs/story226-driver-build-r1/06_plan_critical_graphics_vlm_v1/critical_graphics_manifest.json`, `output/runs/story226-driver-build-r1/08_crop_illustrations_guided_v1/illustration_manifest.jsonl`, and `output/runs/story226-driver-build-r1/12_validate_semantic_manual_html_v1/semantic_manual_html_conformance_report.json`

## What Looks Right
- `CARD INDEX` now stays one parent chapter for logical pages 24-31, with `PROGRAMMING CARDS`, `SPECIAL PROGRAMMING CARDS`, `UPGRADE CARDS`, `PERMANENT UPGRADES`, and `TEMPORARY UPGRADES` as nested headings.
- The logical page 24 programming-card reference panel is no longer a single mixed image containing prose. It is split into source-pixel card-face crops for `MOVE 1`, `MOVE 2`, `MOVE 3`, `TURN RIGHT`, `TURN LEFT`, `U-TURN`, `BACK UP`, `POWER UP`, and `AGAIN`.
- The first Card Index entries are grouped as semantic catalog entries. `MOVE 1, MOVE 2, MOVE 3` contains the three matching card-face figures and one text description; single-card entries contain one matching figure plus semantic text.
- Special programming-card entries are grouped consistently, including `ENERGY ROUTINE`, `SANDBOX ROUTINE`, `WEASEL ROUTINE`, `SPEED ROUTINE`, `SPAM FOLDER`, and `REPEAT ROUTINE`.
- Upgrade-card entries on logical pages 26-31 still use source-pixel card crops, and the annotated `Cost` / `Effect` reference card remains a category-level `card_reference` figure rather than being mistaken for a catalog item.

## Problems Found
- The visual planner correctly identified the page 24 programming-card reference panel, but the first crop was one large mixed text+image panel.
- The first attempted generic fix masked detected prose inside that panel. Visual reinspection showed this produced large white holes through the source crop, which was worse than the original mixed crop.
- Once the panel was split into individual card-face crops, the builder exposed a second class of bugs: figures matched from a multi-image OCR placeholder could remain in OCR visual order instead of semantic label order.
- Definition-list and label-before-figure catalog entries were only partially normalized, which could attach the next card face to the previous entry.
- The validator counted only tables and definition lists as structured reference entries, so it did not recognize the newer `section.semantic-catalog-entry` shape.

## Expected Behavior
- Mixed reference panels should become semantic text plus source-pixel visual sub-crops when the visual planner gives enough compact labels to split them safely.
- Source-pixel crops should preserve visual card/component identity, while explanatory prose belongs in HTML unless it is integrated into the graphic itself.
- Multiple figures belonging to one compound label should stay with that entry and preserve label order.
- A following figure that already belongs to the next label must not be absorbed into the previous catalog entry.

## Generic Failure Class
- Multi-item reference panel: one visual-planner target contains repeated source-pixel components plus surrounding prose.
- Multi-image OCR placeholder ordering: OCR gives one placeholder with `data-count`, but the semantic labels are later in reading order.
- Catalog-entry grouping: repeated catalog entries can appear as `label before figure`, `figure before label`, `definition list followed by figures`, or `heading + figure + metadata`.
- Validator shape drift: the conformance check must understand the semantic structures the builder now emits.

## Fix Attempt
- Added generic card-reference panel splitting in `crop_illustrations_guided_v1`: when a `card_reference` target has compact nearby labels and dense repeated visual blocks, emit one `card_face` source-pixel crop per block instead of a mixed panel crop.
- Removed the unsafe card-reference prose-masking path; it remains limited to detached edge/corner prose on map/board crops.
- Improved builder label matching for short/numeric labels such as `U-TURN`, `MOVE 1`, and `MOVE 2`.
- Repositioned labeled catalog figures from OCR image order to their semantic anchors, sorted repeated figure runs by label position, and grouped multi-figure definition-list entries without absorbing the next entry's figure.
- Extended label-before-figure reference-entry normalization and taught the validator that `section.semantic-catalog-entry` is a structured reference-entry shape.
- Updated critical-graphics crop coverage validation so split child crops can satisfy a multi-item reference target without requiring one crop to cover surrounding prose.

## Rerun Evidence
- Driver rerun from crop stage: `scripts/run_with_doc_web_env.py python driver.py --recipe configs/recipes/recipe-graphics-heavy-imposed-pdf-html-mvp.yaml --input-pdf input/f5-robo-rally-rulebook.pdf --run-id story226-driver-build-r1 --output-dir output/runs/story226-driver-build-r1 --start-from crop_illustrations --allow-run-id-reuse --instrument`
- Final driver rerun from build stage completed after the builder/validator fixes and reported `Semantic manual conformance: pass`.
- Current conformance report: `overall_status=pass`, `22` pass, `0` warn, `0` fail, `126` crops, `113` final HTML figures, and `488` provenance rows.
- Focused tests: `python -m pytest tests/test_build_chapter_html.py tests/test_graphic_manual_semantic_pipeline.py tests/test_crop_illustrations_guided_v1.py -q` passed with `142` tests during the loop; the final broader focused story slice is recorded in the story work log.

## Reinspection Result
- Reopened the source contact sheet and refreshed final screenshots after the last `build_chapters` rerun.
- `chapter-013-after-segment-01.png` and `chapter-013-after-segment-02.png` show programming cards as individual source-pixel card faces with semantic descriptions, not one large crop with prose or white masks.
- `chapter-013-after-segment-03.png` and `chapter-013-after-segment-04.png` show special programming cards grouped under the correct labels, including `SPAM FOLDER` no longer being absorbed by `SPEED ROUTINE`.
- `chapter-013-after-segment-08.png` shows later permanent upgrade card entries still carrying source-pixel card figures and semantic `Cost` / `Effect` text.

## Remaining Caveats
- The current plain HTML is intentionally linear and utilitarian, not a visual recreation of the printed card grids.
- This is category evidence for short, graphics-heavy manuals with repeated reference panels; it does not widen canonical born-digital PDF coverage without a maintained fixture/eval.
- Full `make test` remains not freshly proven in this story pass because of the earlier unrelated EPUB subprocess stall.
