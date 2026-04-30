# Story 226 Page 027 Inspect/Fix/Rerun Loop R1

## Page Selection

- Selected logical page: `27`
- Reason: high-signal dense upgrade-card reference page with repeated card faces, semantic cost/effect entries, a decorative text-only callout, and high risk of image/text duplication or missing semantic prominence.
- Source authority: the page was located from PDF-derived logical-page artifacts, not from the pasted screenshot.

## QA Packet

- Original page: `output/runs/story226-driver-build-r1/manual-inspection-r4/page-027/source-page-027.jpg`
- Crop sheet: `output/runs/story226-driver-build-r1/manual-inspection-r4/page-027/crop-sheet-page-027.jpg`
- Final HTML screenshot before fix: `output/runs/story226-driver-build-r1/manual-inspection-r4/page-027/chapter-021-before.png`
- Final HTML screenshot after fix: `output/runs/story226-driver-build-r1/manual-inspection-r4/page-027/chapter-021-after.png`
- Final HTML: `output/runs/story226-driver-build-r1/output/html/chapter-021.html`
- Critical graphics manifest excerpt: `output/runs/story226-driver-build-r1/manual-inspection-r4/page-027/critical-graphics-page-027.json`
- Crop manifest excerpt: `output/runs/story226-driver-build-r1/manual-inspection-r4/page-027/crop-manifest-page-027.json`
- Conformance report: `output/runs/story226-driver-build-r1/12_validate_semantic_manual_html_v1/semantic_manual_html_conformance_report.json`

## Manual Source-vs-Output Notes

- The source page contains eight upgrade-card faces. These are rule-useful source-pixel references because players need to visually identify the card, its cost badge, title, and card face. The final HTML correctly preserves them as cropped source images beside semantic `dt`/`dd` cost/effect entries.
- The `Rogue Code` gear is a text-only visual callout. The visual planner correctly classifies its source-pixel gear styling as decorative/redundant if the rule text is retained.
- The pre-fix HTML retained the `Rogue Code` text but flattened it to an ordinary paragraph, losing the semantic prominence the source page gives that rule note.
- The pre-fix matched card figures displayed the correct images, but figures matched to existing OCR placeholders did not carry `data-critical-graphics-role`, `data-critical-graphics-importance`, or target-id metadata. Inferred/orphan figures did carry those fields, so traceability was inconsistent across placement paths.
- Decorative page chrome, side rails, hazard stripes, footer marks, and page badge remain absent from final semantic content.

## Generic Failure Classes Found

1. Text-only callout placeholders can be skipped as source-pixel figures but demoted to ordinary paragraphs when the callout cue exists in the placeholder alt text rather than the caption text.
2. Source-pixel figures matched to existing OCR `<figure>` placeholders can lose critical-graphics metadata even when the same crop rows contain role, importance, and target-id fields.

Neither failure is Robo Rally-specific. Both apply to graphics-heavy manuals where OCR emits visual placeholder structure and a later crop/manifest stage supplies semantic visual intent.

## Code Change

- `build_chapter_html_v1` now carries unresolved placeholder alt-text cues into cleanup, so a text-only callout placeholder such as `alt="Callout labeled ..."` becomes `<aside role="note" data-doc-web-semantic="text-callout">` even when the caption itself does not contain words like `note` or `remember`.
- `build_chapter_html_v1` now applies critical-graphics role, importance, and target-id metadata to matched OCR figures as well as inferred/orphan figures.
- Focused regression tests cover both generic cases.

## Rerun Evidence

- Cleared stale build-module pyc files.
- Reran:
  - `python driver.py --recipe configs/recipes/recipe-graphics-heavy-imposed-pdf-html-mvp.yaml --input-pdf input/f5-robo-rally-rulebook.pdf --run-id story226-driver-build-r1 --output-dir output/runs/story226-driver-build-r1 --start-from build_chapters --allow-run-id-reuse --instrument`
- Driver reused upstream page-map/OCR/critical-graphics/crop artifacts and reran `build_chapters` plus `validate_manual_html`.
- Result: `Semantic manual conformance: pass`.
- Current conformance report: `19` pass checks, `0` warnings, `0` failures.
- Focused test evidence: `python -m pytest tests/test_build_chapter_html.py -q` passed with `112 passed`.

## Reinspection Result

- `chapter-021.html` now contains a semantic aside for `Rogue Code Some upgrade cards have special rules...`.
- The after screenshot shows the `Rogue Code` note as a highlighted semantic callout, not a source-pixel gear image and not a plain paragraph.
- All eight page-27 upgrade-card figures remain present as source-pixel crops.
- Each page-27 card figure now carries `data-critical-graphics-role="card_face"`, `data-critical-graphics-importance="essential"`, and the corresponding planner target id such as `p027-g02`.

## Remaining Caveats

- This page is semantically strong but still plain-HTML linearized: it intentionally does not recreate the two-column print layout.
- The QA crop sheet captions overlap in the debug sheet, but the emitted crops and final HTML are inspectable; improving contact-sheet layout is a separate QA-artifact polish issue rather than a manual-output correctness issue.
