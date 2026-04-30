# Story 226 Manual Inspection R2

## Scope

Manual source/crop/HTML inspection for the graphics-heavy manual category candidate in:

- Final HTML: `output/runs/story226-driver-build-r1/output/html/index.html`
- HTML screenshots: `output/runs/story226-driver-build-r1/manual-inspection-r2/html-screenshots/`
- Source/crop contact sheets: `output/runs/story226-driver-build-r1/manual-inspection-r2/page-*-sheet.jpg`
- Conformance report: `output/runs/story226-driver-build-r1/12_validate_semantic_manual_html_v1/semantic_manual_html_conformance_report.json`

This inspection treats the local Robo Rally PDF as a hard-case representative of short, graphics-heavy manuals/rulebooks. The notes below are category observations, not title-specific production rules.

## Inspection Policy

- If text is directly integrated into an explanatory graphic, such as callout boxes pointing to board spaces or movement paths, keep the source-pixel crop intact. The text is contextual and may become confusing if detached.
- If text is only visually emphasized for a human reader, such as a reminder badge, warning banner, or summary panel, prefer semantic HTML and do not force the highlighted panel into the final manual as an image.
- For icons, board elements, course maps, card faces, and diagrams whose visual form carries rule meaning, preserve source-pixel crops with nearby semantic text.
- For reference pages, use semantic entries for the readable rules and attach only the card/icon/source visual that helps identify the component.

## Pages Inspected

- Page 6 source/crops: `page-006-sheet.jpg`
  - The programming-card row and the integrated programming example board are preserved as separate essential crops.
  - The programming example crop includes the yellow numbered callouts because the callouts point into the board diagram and are not useful as detached prose alone.
  - The previous bottom clipping risk is resolved; all callout text remains inside the crop.
- Page 8 source/crops plus `chapter-007.png`
  - Board-element icons are clean source-pixel crops attached to the numbered semantic list.
  - The `Don't forget!` badge and `After the fifth register...` banner are represented as semantic text callout asides in HTML, not as extracted image figures.
  - The top and bottom navigation controls are present and are generated UI chrome outside the semantic article.
- Page 10 source/crops plus `chapter-010.png`
  - Conveyor, rotating conveyor, and board-element examples retain their essential diagrams.
  - Component-reference images for gears, lasers, pits, energy spaces, checkpoints, walls, and priority antenna are attached after the matching semantic text instead of being omitted or lumped together.
  - The output is semantic/plain rather than a layout clone, which is intentional for this story.
- Page 11 source/crops plus `chapter-009.png`
  - The blue summary blocks are pure text/reference panels. The source crop exists for audit, but the final HTML uses headings/ordered text instead of embedding that panel image.
- Page 12 and page 13 source/crops plus `chapter-010.png`
  - Multi-image board-element references were split into individual source-pixel crops and reattached near matching labels.
  - Row ordering is preserved for top-aligned, different-height crop groups.
- Page 15 plus `chapter-012.png`
  - Damage/rebooting prose remains semantic.
  - Rebooting examples and reboot token visuals are preserved where they carry board-state meaning.
- Page 22 source/crops
  - Racing-course board layouts remain source-pixel figures because course geometry is rule content.
- Pages 27-30 source/crops plus `chapter-021.png`
  - Dense upgrade/card reference pages use semantic entries and attach full card/source visuals where the card face matters.
  - Pure callout prose, such as reminder/variant text, remains plain HTML rather than image-only content.
- Page 32 source/crops
  - The back-page summary panel is treated like the page 11 summary: useful as a QA crop, but final output should prefer semantic summary text unless the panel carries non-text rule meaning.

## Fixes Driven By This Inspection

- Text-only callout placeholders are now allowed to collapse to semantic paragraphs instead of unresolved or redundant figures.
- `summary_reference` crops are skipped in final HTML when the same content is already represented semantically.
- Visual-planner essential crops for source-pixel-required roles are inserted into HTML even when the OCR placeholder stream omitted them.
- Essential source-pixel crop usage is now a conformance check, not just a manual convention.
- Multi-image OCR figure runs can split into individual figures and match following labeled entries.
- Crop descriptions now survive reading-order sorting so source images do not attach to the wrong semantic entry.

## Current Result

- Conformance is passing with `19/19` checks and `0` warnings/failures.
- The validator reports `101/101` required source-pixel essential crops referenced in final HTML.
- The visual planner found `123` targets: `102` essential, `15` useful, and `6` decorative.
- The final HTML has `95` figure elements and `456` provenance rows.

## Remaining Caveats

- This is not a pixel-faithful page reconstruction. It is intentionally a semantic, plain HTML manual with essential source-pixel figures.
- The category proof is still one local, gitignored hard-case input. It should not widen canonical born-digital PDF coverage without a repo-owned fixture or maintained eval.
- Some useful-but-nonessential card faces remain omitted unless OCR or the critical-graphics manifest gives a source-pixel reason to include them. That is currently deliberate so the output does not become a full visual clone.
- Full `make test` is still not freshly proven in this story pass because the earlier run stalled in an unrelated EPUB temp-venv subprocess. Focused checks and driver-backed artifact inspection are the current proof surface.
