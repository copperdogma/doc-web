# Story 226 User Review Defect Loop R1

## Target

- Source PDF: `input/f5-robo-rally-rulebook.pdf`
- Current output under review: `output/runs/story226-driver-build-r1/output/html/`
- Chapters called out by review: `chapter-002.html`, `chapter-003.html`, `chapter-004.html`, `chapter-005.html`, `chapter-006.html`, `chapter-007.html`

## Problems Found From Review

- `chapter-002.html` includes a full-page image even though the page's information is already represented as extracted text. Generic class: redundant page-snapshot figures should be suppressed when they do not add rule-bearing visual information.
- `chapter-003.html` puts the `starting positions` graphic at the bottom instead of attaching it near the setup step it illustrates. Generic class: figure placement should follow local semantic anchors, not page-end fallback order.
- `chapter-004.html` has board/priority example crops with text still attached at the bottom. Generic class: source-pixel figures should exclude nearby prose when that prose is already available as semantic text.
- `chapter-004.html` groups priority example prose after the final board image even though the first paragraph belongs with the first board image and the remaining paragraph belongs with the second board image. Generic class: columnar figure+caption/prose pairings need local interleaving.
- `chapter-005.html` preserves a `Purchasing Upgrades` text-heavy panel as an image even though the text is extracted, causing duplicated semantic content. Generic class: text-heavy instructional panels should be semantic HTML unless they contain rule-bearing visual structure.
- `chapter-005.html` includes crops such as `page-009-002.jpg` and `page-009-004.jpg` with text at the bottom that should be removed. Generic class: bottom-text contamination needs crop trimming when the adjacent text is already extracted.
- `chapter-006.html` and `chapter-007.html` split one semantic topic only because of a page break. Generic class: chapter boundaries should ignore physical/logical page breaks and prefer semantic headings, with either one `How To Play` chapter or separate `Upgrade Phase`, `Programming Phase`, `Activation Phase`, and `Summary of a Round` chapters.

## Expected Behavior

- Keep output plain semantic HTML.
- Preserve source-pixel figures only when visual information is needed to understand rules or components.
- Keep figure crops free of duplicated prose unless the prose is spatially integrated into the diagram.
- Attach figures and local explanatory text near the rule step or heading they clarify.
- Split chapters by semantic sections, not source page breaks.

## Status

- Resolved in the 20260430 rerun.

## Fix Attempt

- Redundant page snapshots: `build_chapter_html_v1` skips large source-pixel page snapshots when the page already has substantial semantic text.
- Local figure placement: `build_chapter_html_v1` uses crop `nearby_text` / planner metadata to move figures beside their semantic anchors, including list items and explanatory paragraphs.
- Multi-image metadata: after moving one image out of a multi-image OCR figure, the remaining figure wrapper is re-annotated from the remaining image so figure-level provenance stays correct.
- Bottom prose trimming: `crop_illustrations_guided_v1` trims low-saturation bottom prose bands from rule-example and component-reference crops.
- Text-heavy panel splitting: `crop_illustrations_guided_v1` splits overbroad rule panels into visual clusters, drops split children that are only prominent prose, and only masks true edge prose rather than text inside card/mat pixels.
- Sectioning: `portionize_headings_html_v1` uses the recipe-scoped procedural merge policy so `HOW TO PLAY` owns the upgrade, programming, activation, and round-summary pages instead of splitting at page breaks.

## Rerun Evidence

- Driver rerun: `scripts/run_with_doc_web_env.py python driver.py --recipe configs/recipes/recipe-graphics-heavy-imposed-pdf-html-mvp.yaml --input-pdf input/f5-robo-rally-rulebook.pdf --run-id story226-driver-build-r1 --output-dir output/runs/story226-driver-build-r1 --start-from crop_illustrations --allow-run-id-reuse --instrument`
- Pipeline state: `output/runs/story226-driver-build-r1/pipeline_state.json` marks `crop_illustrations`, `normalize_manual_html`, `portionize_headings`, `build_chapters`, and `validate_manual_html` as `done`.
- Conformance: `output/runs/story226-driver-build-r1/12_validate_semantic_manual_html_v1/semantic_manual_html_conformance_report.json` passes 22 checks with 0 warnings/failures, 32 logical pages, 129 crops, 122 HTML figures, and 497 provenance rows.
- QA packet: `output/runs/story226-driver-build-r1/qa/user-review-defect-loop-r1/page-003-source-and-crops.jpg`, `page-004-source-and-crops.jpg`, `page-005-source-and-crops.jpg`, and `page-009-source-and-crops.jpg`.

## Reinspection Result

- `chapter-002.html`: no longer references the redundant `page-002-000` full-page image.
- `chapter-003.html`: `page-003-000.jpg` is inside setup item 9; the two-player setup overview remains with the two-player callout and has correct figure-level metadata.
- `chapter-004.html`: `HOW TO PLAY` now spans logical pages 4-11. The priority board examples are interleaved with their explanatory prose rather than dumping all text after the figures.
- Page 4 crops: `page-004-000.jpg`, `page-004-001.jpg`, and `page-004-002.jpg` no longer include the detached bottom prose that triggered the review note.
- Page 5 purchasing-upgrades panel: the large mixed text/image panel is replaced by four visual crops for the card/mat content; the pure text callout is semantic text, not an image crop.
- Page 9 crops: `page-009-002.jpg` and `page-009-004.jpg` no longer carry detached bottom prose.

## Remaining Caveats

- The result is still plain linear HTML, not a print-layout replica.
- Some source-pixel figures retain text that is part of a card face, player mat, or integrated label. That is intentional for rule-critical visual artifacts and different from duplicated explanatory prose.
- Full `make test` remains unclaimed for Story 226 because the earlier unrelated EPUB subprocess stall still needs separate validation disposition.
