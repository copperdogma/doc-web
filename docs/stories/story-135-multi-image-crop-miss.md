# Story 135 — Multi-Image Page Crop Detection

**Priority**: Medium
**Status**: Draft
**Ideal Refs**: Requirement #4 (Illustrate — detect, crop, and catalog every illustration with precision)
**Spec Refs**: None
**Depends On**: Story 126 (crop detection pipeline)

## Goal

When a page contains multiple distinct photographs or illustrations, the crop detector should find all of them. Currently it can miss images when multiple appear on a single page. Observed on Onward page 21: two photographs ("Aerial photo of ranch buildings" + "Ranch house and barn") but only the top one was cropped. The OCR model correctly identified both, producing two `<figure>` elements, but the second has no `img[src]` because no crop exists for it.

## Acceptance Criteria

- [ ] Pages with 2+ distinct illustrations produce one crop per illustration
- [ ] Onward page 21 specifically produces 2 crops (aerial photo + ranch house)
- [ ] No regression on single-image pages (existing crop quality maintained)
- [ ] `build_chapter_html_v1` matches all OCR `<figure>` elements to crops (zero `figure without img[src]` issues in scorer)

## Out of Scope

- Overlapping/collaged images that share borders (these are arguably one illustration)
- Improving crop bounding box precision (that's Story 126 territory)

## Approach Evaluation

- **Simplification baseline**: The VLM detector already gets `expected_count` from the images manifest. When `crop_count != expected_count`, auto-retry fires. Need to check if the manifest correctly reports 2 images for page 21 — the miss may be in the manifest, not the detector.
- **AI-only**: VLM already does detection. May just need prompt tuning or retry logic for multi-image pages.
- **Hybrid**: CV pre-detection (contour/edge) could identify distinct image regions, then VLM confirms and refines.
- **Pure code**: CV-only detection for clearly separated images (large whitespace gap between them).
- **Eval**: Run crop detector on all Onward pages with 2+ images. Count pages where `crop_count < actual_count`. Baseline from onward-story009-full run.

## Tasks

- [ ] Identify all multi-image pages in Onward corpus (manual inspection or OCR figure count)
- [ ] Diagnose page 21 miss: is it manifest count, VLM detection, or post-processing?
- [ ] Fix the root cause
- [ ] Re-run crop detection on affected pages and verify
- [ ] Run required checks:
  - [ ] `python -m pytest tests/`
  - [ ] `python -m ruff check modules/ tests/`
- [ ] Search all docs and update any related to what we touched
- [ ] Verify Central Tenets:
  - [ ] T0 — Traceability
  - [ ] T1 — AI-First
  - [ ] T2 — Eval Before Build
  - [ ] T3 — Fidelity
  - [ ] T4 — Modular
  - [ ] T5 — Inspect Artifacts

## Files to Modify

- `modules/extract/crop_illustrations_guided_v1/main.py` — likely detection or retry logic
- Possibly `modules/extract/images_dir_to_manifest_v1/main.py` — if manifest undercounts

## Notes

- The OCR model (Gemini 3.1 Pro) correctly identifies multiple images per page — the gap is in crop extraction, not layout understanding.
- Page 21 has two clearly separated photographs with a caption line between them. This should be a straightforward detection case.
- The auto-retry mechanism (`rescue_model`) already exists for count mismatches — need to verify it's triggering correctly for this page.

## Plan

{Written by build-story Phase 2}

## Work Log

{Entries added during implementation}
