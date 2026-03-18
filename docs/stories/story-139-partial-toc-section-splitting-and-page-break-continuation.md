# Story 139 — Partial-TOC Section Splitting and Page-Break Continuation

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Fidelity to Source
**Spec Refs**: spec:3.1 C3 (layout detection)
**Depends On**: Story 137 (content recovery + TOC-first baseline), Story 129 (HTML output polish)

## Goal

Fix the remaining structure defects in scanned genealogy-book HTML where a partial TOC is not enough: paragraphs split incorrectly across page breaks, separate family sections merged into one chapter, chapter titles chosen from the wrong heading, and cosmetic line breaks in headings preserved as semantic `<br>` elements.

The solution must stay general. Do not hard-code family names or page IDs. Use stronger structure signals: TOC anchors where available, internal heading candidates, continuation-risk signals, table/story ownership, and sentence-level continuation cues across page breaks.

## Acceptance Criteria

- [x] Reviewed page-break paragraphs in the current verification run no longer split mid-sentence when they are clearly one paragraph (for example the `After ... was this done` case and the two Pierre page-break cases)
- [x] Reviewed chapters no longer merge distinct families or sections into one HTML file when stronger structure signals indicate a split (for example `Veterans` + `Alma`, `Josephine` + `Paul`, `Roseanna` + `Antoinette` + `Emilie`)
- [x] Reviewed chapter titles and next/back labels match the visible owning family/section heading rather than a stale or neighboring title
- [x] Cosmetic line breaks inside reviewed headings are normalized unless the line break is clearly semantic
- [x] Manual verification of regenerated chapters confirms the reviewed structure defects are resolved without introducing new dropped-content regressions

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

- [x] Trace the reviewed structure defects through `portionize_toc_html_v1`, `build_chapter_html_v1`, and upstream page HTML to identify the exact failure stage
- [x] Diagnose whether the remaining errors are coarse-boundary errors, fine-grained section-splitting errors, title-selection errors, or page-break continuation errors
- [x] Implement the highest-leverage generic fix for partial-TOC section splitting and page-break paragraph continuation
- [x] Add regression coverage for the reviewed mis-split and mid-sentence page-break cases
- [x] Regenerate and manually verify the reviewed chapters
- [x] Run story-scoped required checks:
  - [x] `python -m pytest tests/test_build_chapter_html.py tests/test_load_artifact_v1.py tests/test_run_registry.py -q`
  - [x] `python -m ruff check modules/build/build_chapter_html_v1/main.py modules/common/load_artifact_v1/main.py modules/common/run_registry.py tools/run_registry.py tests/test_build_chapter_html.py tests/test_load_artifact_v1.py tests/test_run_registry.py`
  - [x] `python tools/run_registry.py check-reuse --run-id story139-onward-full127-composite-validate --scope page_presence`
  - [x] Document that repo-wide `python -m pytest tests -q` and `python -m ruff check modules tests` remain red on unrelated baseline failures outside this story's blast radius
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every output traces to source page, OCR engine, confidence, processing step
  - [x] T1 — AI-First: didn't write code for a problem AI solves better
  - [x] T2 — Eval Before Build: measured SOTA before building complex logic
  - [x] T3 — Fidelity: source content preserved faithfully, no silent losses
  - [x] T4 — Modular: new recipe not new code; no hardcoded book assumptions
  - [x] T5 — Inspect Artifacts: visually verified outputs, not just checked logs

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
- The residual `"I WISH"` nav/title mismatch is deferred behind Story 138 because the heading appears only after Antoine spill pages. If it still reproduces after Story 138 table cleanup, it should become a separate follow-up rather than reopening this story.

## Plan

### Exploration Findings

- `portionize_toc_html_v1` is only a coarse anchor pass. It extracts TOC-derived spans and emits one portion per entry, but it does not attempt any finer ownership split inside a span.
- `build_chapter_html_v1` currently trusts those coarse portions completely. It chooses the chapter title from `portion["title"]`, then concatenates all pages in the printed-page range after only applying image attachment, running-head stripping, and table-scope cleanup. There is no second-pass logic for:
  - reselecting the owning heading,
  - splitting one coarse TOC span into multiple family chapters,
  - normalizing cosmetic `<br>` breaks in headings,
  - merging obvious page-break paragraph continuations.
- Because the referenced `story137-onward-verify` run is not present locally, I generated a reproducible baseline from surviving artifacts instead of relying on stale log paths:
  - input pages: `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-story009-full/05_extract_page_numbers_html_v1/pages_html_with_page_numbers.jsonl`
  - input build pages: `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-story009-full/07_table_fix_continuations_v1/pages_html_onward_tables_fixed.jsonl`
  - current-code baseline outputs: `/tmp/story139-baseline/portions_toc.jsonl`, `/tmp/story139-baseline/chapters_manifest.jsonl`, `/tmp/story139-baseline/html/`
- That baseline reproduces the same class of defects this story exists to fix:
  - `/tmp/story139-baseline/html/chapter-011.html` is titled `Leonidas` but its body headings are `JOSEPHINE (L'HEUREUX) ALAIN` and `PAUL L'HEUREUX`
  - `/tmp/story139-baseline/html/chapter-017.html` is titled `Marie-Louise` but its body headings are `ROSEANNA`, `ANTOINETTE`, and `EMILIE`
  - `/tmp/story139-baseline/html/chapter-021.html` is titled/nav-labeled `Wilfred` while the visible body heading is `PIERRE L'HEUREUX`
  - printed page 99 ends a paragraph with `put up an addition to`, and printed page 100 starts with `be the store and post office.`, showing a clear page-break continuation that the builder currently leaves split across two paragraphs
- The surviving baseline likely still carries some older page-number skew from pre-Story-137 artifacts, so the final verification run for this story should be a fresh rerun with current code. The baseline is still good enough to prove where the current implementation fails.

### Eval-First Baseline

- Structural baseline with current code on the saved Onward artifacts:
  - 3/3 reviewed ownership/title defects reproduced in the generated baseline (`chapter-011`, `chapter-017`, `chapter-021`)
  - at least 1 concrete page-break continuation defect reproduced (printed pages 99 → 100 inside the baseline Pierre chapter)
- Candidate approaches:
  - **AI-only**: Ask a multimodal model to split each coarse TOC span into final family sections and join page-break continuations. This is flexible but adds model cost and new runtime dependence to a problem where the HTML already exposes strong heading and text-continuation signals.
  - **Hybrid**: Keep TOC as the coarse boundary source, then score internal headings plus page-break continuation signals inside each coarse span. Only add an AI fallback if the reviewed spans remain ambiguous after deterministic scoring.
  - **Pure code**: Add a fine-grained structure refinement pass in `build_chapter_html_v1` that splits coarse TOC spans, retitles chapters from the visible owning heading, normalizes cosmetic heading breaks, and stitches obvious page-break continuations.
- Recommendation: start with the hybrid/pure-code path. The current failures are already diagnosable from existing HTML structure, so adding a model call first is not yet justified.

### Implementation Plan

#### Task 1 — Lock the reviewed failures into regression fixtures (`S`)
- **Files**: `tests/test_build_chapter_html.py`, optionally `tests/test_portionize_toc_html.py`
- **Changes**:
  - Add focused fixtures derived from the reviewed coarse spans:
    - Josephine → Paul merge
    - Roseanna → Antoinette → Emilie merge
    - Wilfred → Pierre title/ownership mismatch
    - Pierre page-break continuation (`... addition to` / `be the store ...`)
  - Assert the fixed behavior, not the current broken behavior:
    - a refined chapter split at the right family heading,
    - nav/title follows the owning heading,
    - cosmetic `<br>` in headings normalizes to spaces when non-semantic,
    - continuation text merges when the boundary is clearly a page break, not a new paragraph.
- **Done when**: the new tests fail against current code for the intended reasons and provide a stable harness for the fix.

#### Task 2 — Add fine-grained chapter refinement inside `build_chapter_html_v1` (`M`)
- **Files**: `modules/build/build_chapter_html_v1/main.py`, `tests/test_build_chapter_html.py`
- **Changes**:
  - Introduce a structure-refinement pass over the pages inside each coarse TOC portion.
  - Detect strong owner-heading candidates from page HTML (likely `h1` first, selective `h2` fallback), while rejecting table/subfamily headings that should stay inside the same chapter.
  - Split one coarse TOC portion into multiple emitted chapter files when a later page contains a stronger new owner heading.
  - Retitle each emitted chapter from the first owning heading in that refined segment instead of blindly using the coarse TOC title.
  - Normalize cosmetic heading `<br>` breaks to spaces unless the break is clearly semantic.
- **Done when**:
  - the reviewed merged-family chapters split into the expected chapter files,
  - `chapter-021`-style stale title/nav mismatches disappear,
  - the fix remains generic and does not hard-code family names or page IDs.

#### Task 3 — Add page-break continuation stitching in chapter assembly (`S-M`)
- **Files**: `modules/build/build_chapter_html_v1/main.py`, `tests/test_build_chapter_html.py`
- **Changes**:
  - Before concatenating page HTML, inspect the last narrative paragraph of page N and the first narrative paragraph of page N+1.
  - Merge them only when generic continuation signals agree, for example:
    - previous paragraph ends mid-sentence or with a dangling connector,
    - next paragraph starts lowercase or clearly continues the syntax,
    - no strong heading/table boundary/image-only boundary intervenes.
  - Keep the heuristic conservative so true paragraph boundaries are not collapsed.
- **Done when**: the reviewed continuation cases read as one coherent paragraph without introducing obvious false merges in the regression fixture set.

#### Task 4 — Only tighten `portionize_toc_html_v1` if the refined build pass is still starved of correct coarse anchors (`S`)
- **Files**: `modules/portionize/portionize_toc_html_v1/main.py`, `tests/test_portionize_toc_html.py`
- **Changes**:
  - Leave the TOC portionizer alone unless the fresh rerun proves the current coarse anchors are still materially wrong after Story 137’s OCR/page-number recovery.
  - If needed, add a narrow guard so TOC extraction prefers true TOC-entry rows over incidental non-TOC table content on the same page.
- **Done when**: either no change is needed, or the TOC parser becomes more robust without learning book-specific titles.

#### Task 5 — Driver validation and artifact inspection (`M`)
- **Files**: run-local config and generated artifacts only; update this story work log after verification
- **Changes**:
  - Reuse existing OCR/table artifacts where possible and rerun from the narrowest necessary stage:
    - `build_chapters` if the fix stays inside `build_chapter_html_v1`
    - `portionize_toc` if the TOC module changes
  - Inspect the regenerated HTML manually for the reviewed chapters and confirm the acceptance criteria against the fresh run output.
- **Done when**:
  - regenerated artifacts exist under `output/runs/<run_id>/`
  - reviewed chapters no longer merge distinct families,
  - title/nav ownership matches the visible heading,
  - page-break continuation samples read correctly,
  - no new dropped-content regressions appear in the checked chapters.

### Impact Analysis

- **Primary blast radius**: `build_chapter_html_v1`
  - This is where Story 130 reads its chapter HTML from, so chapter file counts/titles may change if the refined split produces more accurate chapter boundaries.
- **Secondary blast radius**: `portionize_toc_html_v1`
  - Only if a fresh rerun shows the coarse TOC anchors are still wrong enough that build-stage refinement cannot recover.
- **Tests at risk**:
  - `tests/test_build_chapter_html.py` will need new structure-aware coverage
  - `tests/test_portionize_toc_html.py` only if TOC parsing changes
- **Schema / dependency blockers**: none expected
- **Recommended scope adjustment folded into this story**:
  - Treat the implementation as a fine-grained refinement of coarse TOC spans, not a wholesale re-think of OCR or table rescue.
  - Validate against a fresh rerun because the originally referenced verification run is not locally available.

### What Done Looks Like

- A fresh rerun with current code produces reviewed HTML chapters where:
  - distinct families no longer share one coarse TOC chapter file when strong internal headings show a real split,
  - chapter titles and nav labels follow the visible owning heading,
  - cosmetic heading `<br>` breaks are normalized,
  - reviewed page-break prose reads as continuous paragraphs,
  - manual inspection confirms no new dropped-content regressions in the sampled chapters.

## Work Log

### 20260313-0905 — story created from round-2 manual review
- **Result:** Created a dedicated follow-up story for the remaining structure defects that were not solved by OCR-empty recovery plus TOC-first portionization.
- **Evidence:** User review of `output/runs/story137-onward-verify/output/html/` found repeated paragraph splits at page breaks, multiple-family merges inside one chapter, unstable chapter titles, and cosmetic heading line breaks preserved as semantic HTML.
- **Next:** Build-story should trace these reviewed failures through portionization and chapter assembly before deciding whether to solve them in portionization, build, or both.

### 20260313-1011 — exploration: current code reproduces the structure failures in a fresh baseline
- **Result:** Traced the story through the current portionize/build code, then generated a reproducible baseline from surviving Onward artifacts so the plan is tied to current behavior instead of stale log references.
- **Evidence:**
  - `modules/portionize/portionize_toc_html_v1/main.py` emits only coarse TOC spans; it does not split inside a TOC-owned range.
  - `modules/build/build_chapter_html_v1/main.py` currently titles chapters from the coarse portion title and concatenates all pages in that range without owner-heading re-selection or page-break continuation stitching.
  - Local baseline rerun:
    - `/tmp/story139-baseline/portions_toc.jsonl`
    - `/tmp/story139-baseline/chapters_manifest.jsonl`
    - `/tmp/story139-baseline/html/chapter-011.html` — title `Leonidas`, body headings `JOSEPHINE ...` and `PAUL L'HEUREUX`
    - `/tmp/story139-baseline/html/chapter-017.html` — title `Marie-Louise`, body headings `ROSEANNA`, `ANTOINETTE`, `EMILIE`
    - `/tmp/story139-baseline/html/chapter-021.html` — title/nav `Wilfred`, visible body heading `PIERRE L'HEUREUX`
  - Page-break continuation evidence from the same baseline:
    - printed page 99 ends a paragraph with `put up an addition to`
    - printed page 100 starts the next paragraph with `be the store and post office.`
- **Files likely to change:** `modules/build/build_chapter_html_v1/main.py`, `tests/test_build_chapter_html.py`, and only if needed after fresh rerun, `modules/portionize/portionize_toc_html_v1/main.py` plus `tests/test_portionize_toc_html.py`.
- **Surprises:** the story log references `output/runs/story137-onward-verify/...`, but that run is not present locally. I used a reproducible `/tmp` baseline from `onward-story009-full` artifacts for planning and will validate the actual fix against a fresh rerun.
- **Next:** Approval gate on the plan above. Implementation should start with regression fixtures and a build-stage structure-refinement pass, keeping TOC changes conditional on fresh-rerun evidence.

### 20260313-1048 — implementation + driver validation: generic chapter refinement landed and the reviewed structure defects were resolved in regenerated HTML
- **Result:** Implemented a build-stage refinement pass in `modules/build/build_chapter_html_v1/main.py` that treats TOC portions as coarse anchors, then generically:
  - normalizes cosmetic `<br>` breaks inside headings,
  - detects strong owner-heading changes inside a coarse span,
  - splits refined chapter segments when a later page clearly belongs to a new owner heading,
  - retitles each emitted chapter from the visible owning heading instead of blindly trusting the coarse TOC title,
  - stitches obvious page-break paragraph continuations when the prior page ends with a dangling continuation and the next page clearly continues the same sentence.
- **Regression coverage added:** `tests/test_build_chapter_html.py` now covers:
  - coarse-span splitting for `Josephine -> Paul`,
  - coarse-span splitting for `Roseanna -> Antoinette -> Emilie`,
  - stale coarse-title retitling from visible headings,
  - tolerant heading matching across minor spelling drift (`Wilfred` vs `Wilfrid`),
  - rejection of family-subheading false positives,
  - conservative page-break stitching,
  - non-stitching when a paragraph is already complete.
- **Driver validation run 1 (current recipe, reused artifacts):**
  - `python driver.py --recipe configs/recipes/recipe-onward-images-html-mvp.yaml --run-id onward-story009-full --allow-run-id-reuse --start-from portionize_toc`
  - `output/runs/onward-story009-full/07_portionize_toc_html_v1/portions_toc.jsonl` now writes 23 coarse TOC portions with `Josephine`, `Paul`, `Roseanna`, `Antoinette`, `Emilie`, `Wilfred`, and `Pierre` all broken out as independent anchors.
  - `output/runs/onward-story009-full/09_build_chapter_html_v1/chapters_manifest.jsonl` now writes 39 chapter rows instead of collapsing the reviewed families into shared files. The added trace fields (`source_pages`, `source_printed_pages`, `source_portion_title`, `source_portion_page_start`) survived stamping and let us see which refined chapters came from stale coarse spans.
  - Reviewed HTML evidence:
    - `output/runs/onward-story009-full/output/html/chapter-008.html` stays `L'HEUREUX VETERANS OF WORLD WAR I & II` and links forward to `chapter-009.html` (`Alma Marie (L'Heureux) Alain`) instead of merging both sections.
    - `output/runs/onward-story009-full/output/html/chapter-011.html` is now `LEONIDAS L'HEUREUX`; `chapter-012.html` is `JOSEPHINE (L'HEUREUX ) ALAIN`; `chapter-013.html` is `PAUL L'HEUREUX`. The old Josephine `<br>` heading is normalized to one line in the emitted chapter title/heading.
    - `output/runs/onward-story009-full/output/html/chapter-022.html`, `chapter-023.html`, and `chapter-024.html` are now separately titled `ROSEANNA`, `ANTOINETTE`, and `EMILIE` chapters, with navigation labels matching the visible owning headings.
    - `output/runs/onward-story009-full/output/html/chapter-027.html` is `Wilfrid L’Heureux` and `chapter-028.html` is `PIERRE L'HEUREUX`, fixing the stale-title/nav mismatch seen in the baseline.
    - `output/runs/onward-story009-full/output/html/chapter-028.html` contains the previously split Pierre sentence as one paragraph: `...put up an addition to be the store and post office...`
- **Driver validation run 2 (fresh run-local load-artifact recipe, needed because the `After ... was this done` page is blank in `onward-story009-full` but present in `onward-canonical`):**
  - temp recipe: `/tmp/story139-onward-canonical-validate.yaml`
  - command: `python driver.py --recipe /tmp/story139-onward-canonical-validate.yaml --run-id story139-onward-canonical-validate --force`
  - artifact evidence:
    - `/Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-canonical-validate/output/html/chapter-005.html` now contains the formerly split sentence as one paragraph: `...fed a ration of oats at 5:00 a.m. After this was done, the horses were watered...`
    - `/Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-canonical-validate/06_build_chapter_html_v1/chapters_manifest.jsonl` confirms the rebuilt chapter came from printed pages `5-8` and source pages `[14, 15, 16, 17]`, so the repaired paragraph still retains page traceability.
- **Checks run:**
  - `python -m pytest tests/test_build_chapter_html.py -q` → `55 passed`
  - `python -m ruff check modules/build/build_chapter_html_v1/main.py tests/test_build_chapter_html.py` → clean
  - `python -m pytest tests` → `11 failed, 526 passed, 5 skipped`; failures are outside this story's blast radius (`tests/driver_integration_test.py`, `tests/test_extract_choices_relaxed_orphan_reocr.py`, `tests/test_extract_combat_v1.py`, `tests/test_run_manager.py`, `tests/test_validate_ff_engine_v2_navigation.py`, `tests/test_validate_ff_engine_v2_node_integration.py`)
  - `python -m ruff check modules tests` → repo baseline still red with 306 unrelated lint violations outside Story 139 files
- **Docs sweep:** searched docs for `build_chapter_html_v1`, `portionize_toc_html_v1`, and Story 139 references; only this story file plus `docs/stories.md` needed updates for this work.
- **Tenet verification:**
  - **T0 Traceability:** added per-chapter source-page/source-portion fields to the manifest and confirmed them in `chapters_manifest.jsonl`
  - **T1 AI-First:** explicitly evaluated AI-only vs hybrid vs pure-code and stayed deterministic because existing HTML already exposed strong structural signals
  - **T2 Eval Before Build:** recorded a reproducible failing baseline in `/tmp/story139-baseline`, then validated behavior in two driver runs
  - **T3 Fidelity:** verified no reviewed content was dropped while boundaries/titles improved
  - **T4 Modular:** no family names, page IDs, or book-specific hard-codes were added; the refinement is driven by generic heading/continuation signals
  - **T5 Inspect Artifacts:** manually opened the regenerated HTML/manifest artifacts listed above
- **Blocker to `Done`:** build-story requires repo-wide `pytest` and `ruff` to pass before the story can be marked Done. Both remain red on pre-existing failures outside the touched files, so the story stays **In Progress** even though the reviewed acceptance criteria and driver/artifact validation for Story 139 are satisfied.
- **Next:** either accept this as implemented-and-validated pending project-baseline cleanup, or explicitly scope follow-up work for the unrelated failing global checks before `/mark-story-done`.

### 20260313-1104 — review correction: the cited `onward-story009-full` validation run is not a safe fidelity-review artifact set
- **Result:** User review correctly found a catastrophic page-loss regression in `output/runs/onward-story009-full/output/html/chapter-005.html`. I traced it upstream and confirmed the loss predates `build_chapter_html_v1`.
- **Evidence:**
  - `output/runs/onward-story009-full/09_build_chapter_html_v1/chapters_manifest.jsonl` says chapter 5 was built from source pages `[14, 15, 16, 17]` / printed pages `[5, 6, 7, 8]`.
  - `output/runs/onward-story009-full/07_table_fix_continuations_v1/pages_html_onward_tables_fixed.jsonl` shows page 15 (printed 6) has `html_len == 0`.
  - The same artifact file shows page 17 (printed 8) has `html_len == 0`.
  - `output/runs/onward-story009-full/05_extract_page_numbers_html_v1/pages_html_with_page_numbers.jsonl` and `02_ocr_ai_gpt51_v1/pages_html.jsonl` already have those same two pages empty, so the builder did not newly drop them.
  - Cross-run comparison: every local 127-page Onward OCR artifact set I checked (`onward-story009-full`, `onward-full-127-table-fidelity`, `onward-gemini3pro-001`, `onward-s134-optimized`) already has page 15 and page 17 empty. The only local run with those pages present is `onward-canonical`, but that artifact set only contains 60 OCR page rows and cannot replace a full-book validation run.
- **Decision:** Retract `onward-story009-full` as a valid full-book review path for Story 139. It was still useful for proving the generic chapter-splitting/title-selection behavior, but it is not acceptable evidence for fidelity/no-loss claims.
- **Impact:** Acceptance criteria tied to page-presence fidelity are reopened until validation is repeated on a non-regressed artifact set. This does **not** change the code-level finding that the Story 139 builder logic fixed the reviewed structure ownership/title issues; it changes the validity of the run I cited for final review.
- **Next:** Re-run Story 139 validation on a trustworthy artifact set: either recover the missing `story137-onward-verify` artifacts or run fresh OCR/page extraction before rechecking the full-book HTML.

### 20260313-1205 — clean composite validation: Story 139 reviewed targets now pass on a page-safe 127-page artifact set
- **Result:** Revalidated Story 139 on a new 127-page composite run that patches the only two missing early pages in `onward-full-127-table-fidelity` with the corresponding clean rows from `onward-canonical`. This produced a trustworthy downstream run for the reviewed Story 139 targets without changing the implementation again.
- **Composite inputs created for validation only:**
  - `/Users/cam/Documents/Projects/codex-forge/output/support/story139-onward-composite/pages_html_with_page_numbers.composite.jsonl`
  - `/Users/cam/Documents/Projects/codex-forge/output/support/story139-onward-composite/pages_html_onward_tables.composite.jsonl`
  - both use `onward-full-127-table-fidelity` as the 127-page base and replace source pages `15` / `17` (printed pages `6` / `8`) with the populated rows from `onward-canonical`
- **Fresh validation run:**
  - recipe: `/tmp/story139-onward-full127-composite-validate.yaml`
  - run: `/Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-full127-composite-validate/`
  - registry evidence:
    - `/Users/cam/Documents/Projects/codex-forge/output/run_health.jsonl`
    - `/Users/cam/Documents/Projects/codex-forge/output/run_assessments.jsonl`
  - `python tools/run_registry.py check-reuse --output-root /Users/cam/Documents/Projects/codex-forge/output --run-id story139-onward-full127-composite-validate --scope page_presence` now returns `recommendation: safe`
- **Manual artifact verification:**
  - `/Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-full127-composite-validate/06_build_chapter_html_v1/chapters_manifest.jsonl`
    - chapter 5 traces to source pages `[14, 15, 16, 17]` / printed pages `[5, 6, 7, 8]`
    - reviewed split targets are separate chapters: `008/009`, `011/012/013`, `022/023/024`, `027/028`
  - `/Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-full127-composite-validate/output/html/chapter-005.html`
    - contains page-6 content: `George was born in 1891 ... By 1894 ... St. Michael's School ...`
    - contains the repaired continuation from page 8: `After this was done, the horses were watered ...`
  - `/Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-full127-composite-validate/output/html/chapter-011.html`
    - `LEONIDAS L'HEUREUX` chapter body contains no nested `<h1>`/`<h2>` for `JOSEPHINE` or `PAUL`
  - `/Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-full127-composite-validate/output/html/chapter-022.html`
    - `ROSEANNA` chapter body contains no nested `<h1>`/`<h2>` for `ANTOINETTE` or `EMILIE`
  - `/Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-full127-composite-validate/output/html/chapter-028.html`
    - contains the repaired Pierre continuation: `put up an addition to be the store and post office`
- **Assessments recorded in the shared registry:**
  - `page_presence: known_good`
  - `chapter_structure_story139_targets: known_good`
  - `page_break_stitching: known_good`
- **Checks rerun for this pass:**
  - `python -m pytest tests/test_run_registry.py -q` → `6 passed`
  - `python -m pytest tests/test_build_chapter_html.py -q` had already passed in the implementation pass
  - `python -m ruff check modules/common/run_registry.py tools/run_registry.py tests/test_run_registry.py` → clean
- **Current blocker:** Story 139 is now validated on a safe artifact set for the reviewed targets, but repo-wide `python -m pytest tests/` and `python -m ruff check modules/ tests/` still fail on unrelated pre-existing issues outside this story's blast radius, so status remains **In Progress**.

### 20260313-1212 — validation asset reuse fix: copied sibling crop images so the review HTML is visually usable
- **Result:** User review caught that the safe composite validation run still had broken images. The cause was generic reuse infrastructure, not Story 139 chapter logic: `load_artifact_v1` copied `illustration_manifest.jsonl` but not its sibling `images/` directory, so the generated HTML referenced `images/*.jpg` files that were never loaded into the validation run.
- **Implementation:** Added an opt-in `--copy-sibling-dir` parameter to `modules/common/load_artifact_v1/main.py` and documented it in `modules/common/load_artifact_v1/module.yaml`. Added focused coverage in `tests/test_load_artifact_v1.py`.
- **Checks:**
  - `python -m pytest tests/test_load_artifact_v1.py -q` → `2 passed`
  - `python -m ruff check modules/common/load_artifact_v1/main.py tests/test_load_artifact_v1.py` → clean
- **Validation rerun:** regenerated `/Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-full127-composite-validate/` with `copy_sibling_dir: images` on the `load_crops` stage in `/tmp/story139-onward-full127-composite-validate.yaml`.
- **Evidence:**
  - `/Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-full127-composite-validate/output/html/images/page-001-000.jpg` now exists
  - `/Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-full127-composite-validate/output/html/images/page-092-000.jpg` now exists
  - `/Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-full127-composite-validate/output/html/page-001.html` references `images/page-001-000.jpg`, which now resolves
- **Impact:** The Story 139 validation run is now both page-safe and visually reviewable, so the file paths cited for manual inspection are finally reliable for both text and images.

### 20260313-1238 — post-review classification: remaining major defects map to Stories 138 and 135, with one residual title edge case to revisit later
- **Result:** User review of the now-usable `story139-onward-full127-composite-validate` run found many remaining defects, but the majority are outside Story 139 scope and belong exactly where expected: Story 138 for genealogy-table spill/headers and Story 135 for image order/placement/caption issues.
- **Story 139 conclusion:** The chapter-boundary/title work remains valid for the reviewed family-split targets (`Veterans/Alma`, `Leonidas/Josephine/Paul`, `Roseanna/Antoinette/Emilie`, `Wilfrid/Pierre`) and the page-break continuation cases. The review did not uncover a broad new chapter-boundary failure.
- **Residual edge case:** the `"I WISH"` section still renders inside `chapter-030.html` with a stale coarse title/nav label (`Antoine`). Tracing showed why the current generic fix misses it:
  - the visible `I WISH` `<h1>` does **not** begin the Antoine coarse segment; it appears later, after unheaded overflow pages from the preceding family/table span
  - a first-page non-TOC `<h1>` retitle safeguard was added and regression-tested in `tests/test_build_chapter_html.py`, but it does not apply here because the heading starts later in the segment
- **Decision:** Do **not** silently expand Story 139 into the table/image stories. Revisit the `I WISH` nav/title case after Story 138 fixes the Antoine table spill; if it still reproduces on a clean table-owned chapter, then it becomes a genuine follow-up title-selection story rather than a table-side effect.

### 20260313-1418 — closure rescope: story-scoped validation is complete, global baseline failures are explicitly left outside this story
- **Result:** Accepted the validation recommendation to close Story 139 around the slice it actually shipped: generic chapter refinement, page-break stitching, safe-run validation, and the review-path infrastructure needed to inspect that slice reliably from a worktree.
- **Evidence:**
  - `python -m pytest tests/test_build_chapter_html.py tests/test_load_artifact_v1.py tests/test_run_registry.py -q` → `64 passed`
  - `python -m ruff check modules/build/build_chapter_html_v1/main.py modules/common/load_artifact_v1/main.py modules/common/run_registry.py tools/run_registry.py tests/test_build_chapter_html.py tests/test_load_artifact_v1.py tests/test_run_registry.py` → clean
  - `python tools/run_registry.py check-reuse --run-id story139-onward-full127-composite-validate --scope page_presence` now resolves the shared project output root correctly from this worktree and returns `recommendation: safe`
  - `/Users/cam/Documents/Projects/codex-forge/output/runs/story139-onward-full127-composite-validate/output/html/chapter-005.html`, `chapter-011.html`, `chapter-022.html`, and `chapter-028.html` remain the reviewed acceptance-criteria evidence
- **Rescope/closure decision:** Story 139 is **Done**. Remaining genealogy-table defects stay in Story 138, remaining image-order/placement defects stay in Story 135, and the residual `I WISH` title/nav mismatch stays deferred until after Story 138 removes the Antoine spill context.
- **Known unrelated baseline failures left outside this story:** `python -m pytest tests -q` still fails in `driver_integration_test`, `test_extract_choices_relaxed_orphan_reocr.py`, `test_extract_combat_v1.py`, `test_run_manager.py`, and `test_validate_ff_engine_v2_navigation.py`; `python -m ruff check modules tests` still reports repo-wide pre-existing lint errors.
- **Next:** Build Story 138 next, then only reopen title-selection work if a clean post-table run still mislabels `I WISH`.
