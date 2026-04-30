# Story 226 User Review Defect Loop R2

## Target

- Source PDF: `input/f5-robo-rally-rulebook.pdf`
- Current output under review: `output/runs/story226-driver-build-r1/output/html/chapter-004.html`
- Source/crop QA packet: `output/runs/story226-driver-build-r1/qa/user-review-defect-loop-r2/page-004-source-and-crops.jpg`, `page-005-source-and-crops.jpg`, and `page-009-source-and-crops.jpg`
- Render QA packet: `output/runs/story226-driver-build-r1/qa/user-review-defect-loop-r2/chapter-004-render-upgrade.png`, `chapter-004-render-activation.png`, and `chapter-004-render-full.png`

## Problems Found From Review

- `page-004-000.jpg` is cut too close and loses part of board squares/elements. Generic class: useful/component-reference crops from visual-planner boxes need enough source-pixel margin to preserve the whole referenced component while still trimming detached prose.
- `page-005-000.png` is the upgrade-cost card example, but it is not placed next to the paragraph that explains using the top-left card number to pay energy cubes. Generic class: split children of a mixed visual/prose panel need child-specific semantic anchors, not inherited broad panel text.
- The player mat, installed-upgrade cards, and red temporary card were split apart even though their spatial relationship is the rule-critical content. Generic class: when a mixed panel's split children form one placement/layout relationship, the cropper should keep that relation as a single source-pixel cluster instead of atomizing every colored component.
- In the activation example, the middle player pair is ordered game-board then player-board while the source and the other pairs use player-board then game-board. Generic class: multiple figures inserted at the same semantic anchor should preserve manifest/source reading order rather than reversing due to repeated `insert_after` calls.

## Expected Behavior

- Component-reference crops keep a small visual safety margin but do not include detached explanatory prose.
- Cost-card visuals anchor near the cost/payment explanation.
- Placement/layout visuals stay grouped when their spatial relationship is part of the instruction.
- Figure runs that share an anchor keep the source/manifest order.

## Status

- Resolved after generic crop and HTML assembly fixes, driver rerun, and visual reinspection.

## Fix Attempt

- Added a small, role-based safety margin for `component_reference` planner crops so useful component examples do not get clipped by edge/prose trimming.
- Added child-specific context selection for split text-heavy rule panels so cost-card children anchor to cost/payment text while placement-layout children anchor to placement text.
- Added a placement-layout grouping pass for text-heavy rule panels so related card/mat pieces remain one source-pixel visual when their spatial relationship carries the rule meaning.
- Added same-anchor figure insertion ordering and multi-paragraph nearby-text anchor extension so repeated example figures preserve source/manifest order and layout figures land after the full text run they illustrate.
- Added sparse placement-layout prose masking so grouped layout crops suppress detached semantic prose while keeping the card/mat relationship visible.

## Rerun Evidence

- Driver rerun: `scripts/run_with_doc_web_env.py python driver.py --recipe configs/recipes/recipe-graphics-heavy-imposed-pdf-html-mvp.yaml --input-pdf input/f5-robo-rally-rulebook.pdf --run-id story226-driver-build-r1 --output-dir output/runs/story226-driver-build-r1 --start-from crop_illustrations --allow-run-id-reuse --instrument`
- Pipeline state: `output/runs/story226-driver-build-r1/pipeline_state.json` marks `crop_illustrations`, `normalize_manual_html`, `portionize_headings`, `build_chapters`, and `validate_manual_html` as `done`.
- Conformance: `output/runs/story226-driver-build-r1/12_validate_semantic_manual_html_v1/semantic_manual_html_conformance_report.json` reports `overall_status=pass`, `22` pass checks, `0` warnings, `0` failures, `32` logical pages, `127` crops, `120` HTML figures, and `495` provenance rows.
- Focused tests: `python -m pytest tests/test_crop_illustrations_guided_v1.py tests/test_build_chapter_html.py -q` passed (`151 passed`).

## Reinspection Result

- `page-004-000.jpg` is visually complete again: the component-reference crop includes the whole small priority board component and does not include detached bottom prose.
- `page-005-000.png` now appears immediately after the cost/payment paragraph explaining the top-left card number and energy-cube payment.
- `page-005-001.png` now keeps the temporary card, installed-upgrade cards, and player mat as one source-pixel layout figure after both permanent and temporary placement paragraphs; detached prose is masked out instead of duplicated as readable crop text.
- The activation example now preserves pair order for Amanda, Luis, and Chris: each player mat crop precedes its game-board crop, including the middle Luis pair.

## Remaining Caveats

- The placement-layout crop is a transparent/masked source-pixel composite from one rectangular source crop, so it looks like a plain-HTML artifact rather than a print-layout replica. The rule-critical spatial relationship is preserved, and the surrounding prose remains semantic HTML.
