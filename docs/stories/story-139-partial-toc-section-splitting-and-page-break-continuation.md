# Story 139 — Partial-TOC Section Splitting and Page-Break Continuation

**Priority**: High
**Status**: Pending
**Ideal Refs**: Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Fidelity to Source
**Spec Refs**: C3 (layout detection)
**Depends On**: Story 137 (content recovery + TOC-first baseline), Story 129 (HTML output polish)

## Goal

Fix the remaining structure defects in scanned genealogy-book HTML where a partial TOC is not enough: paragraphs split incorrectly across page breaks, separate family sections merged into one chapter, chapter titles chosen from the wrong heading, and cosmetic line breaks in headings preserved as semantic `<br>` elements.

The solution must stay general. Do not hard-code family names or page IDs. Use stronger structure signals: TOC anchors where available, internal heading candidates, continuation-risk signals, table/story ownership, and sentence-level continuation cues across page breaks.

## Acceptance Criteria

- [ ] Reviewed page-break paragraphs in the current verification run no longer split mid-sentence when they are clearly one paragraph (for example the `After ... was this done` case and the two Pierre page-break cases)
- [ ] Reviewed chapters no longer merge distinct families or sections into one HTML file when stronger structure signals indicate a split (for example `Veterans` + `Alma`, `Josephine` + `Paul`, `Roseanna` + `Antoinette` + `Emilie`)
- [ ] Reviewed chapter titles and next/back labels match the visible owning family/section heading rather than a stale or neighboring title
- [ ] Cosmetic line breaks inside reviewed headings are normalized unless the line break is clearly semantic
- [ ] Manual verification of regenerated chapters confirms the reviewed structure defects are resolved without introducing new dropped-content regressions

## Out of Scope

- Image placement, image ordering, or swapped captions
- Genealogy table row/header fidelity once the correct family ownership is established
- OCR-empty page recovery (already addressed in Story 137)

## Approach Evaluation

- **Simplification baseline**: Trace the reviewed mis-splits through TOC portions, current chapter build, and page HTML to determine whether the failure is coarse boundary selection, title selection, or paragraph continuation stitching.
- **AI-only**: A multimodal model could propose section boundaries from page images plus OCR, but should be used only if deterministic signals are insufficient on the reviewed cases.
- **Hybrid**: Use TOC anchors for coarse chapter ranges, then apply a finer structure pass inside those ranges using headings, table ownership, and continuation-risk/page-break cues.
- **Pure code**: If the reviewed failures reduce to sentence continuation stitching, title selection, and heading normalization, solve them deterministically in portionization/build stages.
- **Eval**: The gate is reviewed structure fidelity:
  - page-break prose reads as coherent paragraphs,
  - distinct families are not merged,
  - chapter titles/navigation labels match the visible owning heading.

## Tasks

- [ ] Trace the reviewed structure defects through `portionize_toc_html_v1`, `build_chapter_html_v1`, and upstream page HTML to identify the exact failure stage
- [ ] Diagnose whether the remaining errors are coarse-boundary errors, fine-grained section-splitting errors, title-selection errors, or page-break continuation errors
- [ ] Implement the highest-leverage generic fix for partial-TOC section splitting and page-break paragraph continuation
- [ ] Add regression coverage for the reviewed mis-split and mid-sentence page-break cases
- [ ] Regenerate and manually verify the reviewed chapters
- [ ] Run required checks:
  - [ ] `python -m pytest tests/`
  - [ ] `python -m ruff check modules/ tests/`
- [ ] Search all docs and update any related to what we touched
- [ ] Verify Central Tenets:
  - [ ] T0 — Traceability: every output traces to source page, OCR engine, confidence, processing step
  - [ ] T1 — AI-First: didn't write code for a problem AI solves better
  - [ ] T2 — Eval Before Build: measured SOTA before building complex logic
  - [ ] T3 — Fidelity: source content preserved faithfully, no silent losses
  - [ ] T4 — Modular: new recipe not new code; no hardcoded book assumptions
  - [ ] T5 — Inspect Artifacts: visually verified outputs, not just checked logs

## Files to Modify

- `modules/portionize/portionize_toc_html_v1/main.py` — if coarse TOC anchoring needs additional quality signals or metadata
- `modules/build/build_chapter_html_v1/main.py` — if page-break paragraph stitching, title selection, or heading normalization belongs in chapter assembly
- `tests/test_build_chapter_html.py` — regression coverage for page-break continuation and chapter-title ownership
- `tests/test_portionize_toc_html.py` — regression coverage for partial-TOC internal splitting if applicable

## Notes

- Round-2 manual review defects feeding this story:
  - `chapter-005.html` — paragraph split mid-sentence across a page break (`After` / `was this done`)
  - `chapter-008.html` — merges `L'HEUREUX VETERANS OF WORLD WAR I & II` with `Alma Marie (L'Heureux) Alain`
  - `chapter-011.html` — merges `JOSEPHINE (L'HEUREUX) ALAIN` with `PAUL L'HEUREUX`, and preserves a cosmetic heading line break as `<h1>JOSEPHINE<br>(L'HEUREUX ) ALAIN</h1>`
  - `chapter-017.html` — merges `ROSEANNA`, `ANTOINETTE`, and `EMILIE`
  - `chapter-019.html` and `chapter-020.html` — split one family story halfway through prose
  - `chapter-021.html` — navigation/title says `Wilfred` while the visible owning heading is `PIERRE L'HEUREUX`; also splits prose mid-sentence across page breaks
- This story is about structure ownership and prose continuity. Table bleed between families belongs in Story 138; image placement belongs in Story 135.

## Plan

{Written by build-story Phase 2}

## Work Log

### 20260313-0905 — story created from round-2 manual review
- **Result:** Created a dedicated follow-up story for the remaining structure defects that were not solved by OCR-empty recovery plus TOC-first portionization.
- **Evidence:** User review of `output/runs/story137-onward-verify/output/html/` found repeated paragraph splits at page breaks, multiple-family merges inside one chapter, unstable chapter titles, and cosmetic heading line breaks preserved as semantic HTML.
- **Next:** Build-story should trace these reviewed failures through portionization and chapter assembly before deciding whether to solve them in portionization, build, or both.
