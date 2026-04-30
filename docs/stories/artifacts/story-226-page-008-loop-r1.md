# Story 226 Page 008 Inspect/Fix/Rerun Loop R1

## Page Selection

- Selected logical page: `8`
- Reason: high-signal page with mixed board-element visuals, numbered activation order, explanatory text, bullet notes, and two pure text-only emphasis blocks.
- Source authority: the page was located from the PDF-derived artifacts, not from the pasted screenshot.

## QA Packet

- Original page: `output/runs/story226-driver-build-r1/manual-inspection-r3/page-008/source-page-008.jpg`
- Crop sheet: `output/runs/story226-driver-build-r1/manual-inspection-r3/page-008/crop-sheet-page-008.jpg`
- Final HTML screenshot after fix: `output/runs/story226-driver-build-r1/manual-inspection-r3/page-008/chapter-007-after.png`
- Final HTML: `output/runs/story226-driver-build-r1/output/html/chapter-007.html`
- Critical graphics manifest: `output/runs/story226-driver-build-r1/06_plan_critical_graphics_vlm_v1/critical_graphics_manifest.json`, page entry `page_number=8`
- Crop manifest: `output/runs/story226-driver-build-r1/08_crop_illustrations_guided_v1/illustration_manifest.jsonl`, rows with `source_page=8`
- Conformance report: `output/runs/story226-driver-build-r1/12_validate_semantic_manual_html_v1/semantic_manual_html_conformance_report.json`

## Manual Source-vs-Output Notes

- The eight numbered board-element/reference visuals are rule-essential and should remain as source-pixel figures. They are not decorative because the tile appearance, activation marker, direction arrows, or laser geometry carries rule meaning.
- The plain rule text beside each visual is correctly represented as semantic ordered-list text in the HTML. A one-column list is acceptable because the target is semantic plain HTML, not a layout clone.
- The yellow `Don't forget!` badge is pure reminder text. It should not be emitted as an image because no non-text visual information is needed for understanding the rule.
- The blue `After the fifth register...` banner is also pure text, but it is visually promoted in the source. The previous output kept the text but flattened it into an ordinary paragraph, losing semantic prominence.
- The bottom `Repeat "Activating your robots"...` paragraph is also emphasized in the source, but the current OCR did not preserve enough structured emphasis for a safe generic promotion in this pass. This remains a lower-priority follow-up candidate rather than a page-specific fix.
- Decorative side rails, rivets, page footer, and hazard-stripe chrome should stay out of final semantic content.

## Generic Failure Class Found

Text-only visual emphasis blocks can be correctly rejected as image crops but still lose semantic prominence when converted to plain paragraphs.

This is not a Robo Rally-specific failure. It applies to graphics-heavy manuals that use badges, banners, reminder bubbles, or note panels as visual emphasis around text-only rules.

## Code Change

- `build_chapter_html_v1` now converts text-only callout image placeholders with captions into semantic `<aside role="note" data-doc-web-semantic="text-callout">` blocks instead of ordinary paragraphs.
- It also promotes standalone fully emphasized long paragraphs with instructional/reminder cues into semantic callout asides.
- Source-pixel figures remain unchanged for the eight board-element visuals.

## Rerun Evidence

- Cleared stale build-module pyc files.
- Reran:
  - `scripts/run_with_doc_web_env.py python driver.py --recipe configs/recipes/recipe-graphics-heavy-imposed-pdf-html-mvp.yaml --input-pdf input/f5-robo-rally-rulebook.pdf --run-id story226-driver-build-r1 --output-dir output/runs/story226-driver-build-r1 --start-from build_chapters --allow-run-id-reuse --instrument`
- Driver reused upstream OCR/page-map/critical-graphics/crop artifacts and reran `build_chapters` plus `validate_manual_html`.
- Result: `Semantic manual conformance: pass`.

## Reinspection Result

- Page 8 HTML now contains two semantic text callouts:
  - `data-callout-kind="important"` for `After the fifth register is complete...`
  - `data-callout-kind="reminder"` for `Don't forget! You can use permanent or temporary upgrades...`
- The final page screenshot shows those as highlighted semantic note boxes rather than source-pixel images.
- The eight essential board-element visuals remain attached as source-pixel figures.
- The conformance report remains passing with `19/19` checks, `0` warnings/failures, and `101/101` required source-pixel essential crops referenced.

## Loop Assessment

The loop was useful. The automated report already passed before this run, but manual visual inspection still found a real semantic-quality gap: text-only emphasis was preserved as text but not as semantic prominence. The fix is generic enough to keep and small enough to cover with focused regression tests.
