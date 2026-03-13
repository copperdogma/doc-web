# Story 137 — Onward OCR Empty-Page Recovery and TOC Coarse Boundary Selection

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Fidelity to Source
**Spec Refs**: C3 (layout detection)
**Depends On**: Story 009 (layout linearization), Story 129 (HTML output polish)

## Goal

Recover reviewed OCR-empty nonblank pages and replace over-eager heading-only chapter splitting with a stronger TOC-derived coarse boundary source when the source book exposes one. The fix must be driven by general signals, not Onward-specific title rules: recover nonblank OCR-empty pages generically, and prefer parsed TOC boundaries over raw page-heading splits when the TOC is demonstrably stronger.

## Acceptance Criteria

- [x] Final HTML includes the reviewed missing content from printed pages 6 (`Image014.jpg`), 8 (`Image016.jpg`), and 101 (`Image109.jpg`); none of those source pages are silently dropped or emitted as empty chapter spans
- [x] The rebuilt chapter map no longer creates a standalone chapter solely from an internal subsection heading like "Sharon's Family" when the source TOC provides a stronger coarse chapter map
- [x] A page-to-chapter trace for the reviewed missing pages shows exactly where content disappeared in the failing run and confirms it is preserved after the fix
- [x] Manual verification of regenerated HTML confirms the reviewed missing pages are present and that the rebuilt navigation/index follows the TOC-authored coarse chapter sequence (`Arthur` → `Leonidas` → `Josephine`) with no standalone `Sharon's Family` chapter

## Out of Scope

- Image placement, broken image attachment, or swapped captions
- Fine-grained section ownership inside a TOC-derived chapter when multiple family subsections still need to be split more intelligently
- Genealogy table continuation, header/cell regressions, or cross-family table bleed when the content is already present
- Paragraph continuation across page breaks
- General website presentation work

## Approach Evaluation

- **Simplification baseline**: Trace the reviewed missing pages through the existing artifacts (`pages_html`, `pages_html_with_page_numbers`, rescued tables, portions, chapter manifest, final HTML). If content is already empty at OCR, fix OCR-stage recovery before touching chapter assembly.
- **AI-only**: Re-run only OCR-empty nonblank pages with a stronger OCR model, and prefer a TOC-derived chapter map when the source book exposes a reliable TOC. This stays general because both signals come from the source, not from book-specific string rules.
- **Hybrid**: Use deterministic tracing to classify failures, then apply targeted AI only to nonblank OCR-empty pages or ambiguous boundary-source selection.
- **Pure code**: Pure code is sufficient only for conservative blank-page detection and for choosing between existing boundary sources (for example, TOC vs heading spans) once baseline evidence shows which source is more reliable.
- **Eval**: The gate is reviewed-page coverage plus boundary correctness:
  - the three reviewed missing pages survive OCR and reach final HTML,
  - the spurious `Sharon's Family` chapter disappears,
  - coarse chapter boundaries follow the stronger source signal rather than every qualifying inline `<h1>`.

## Tasks

- [x] Trace reviewed missing pages (`Image014`, `Image016`, `Image109`) through the failing run artifacts and classify each as blank-skip, OCR-empty, or downstream-drop
- [x] Measure the simplest recovery path on the reviewed missing pages: same-model rerun without blank skipping, then stronger-model targeted reread only for nonblank pages that remain empty
- [x] Trace the reviewed bad internal-heading split through portions, chapter manifests, and the source TOC to identify whether headings or TOC are the more reliable coarse chapter-boundary source
- [x] Fix the root cause in OCR empty-page handling and coarse chapter-boundary source selection without hard-coding Onward titles or page IDs
- [x] Add regression coverage for reviewed OCR-empty pages and mis-boundary cases
- [x] Regenerate and manually verify the reviewed chapters
- [x] Run validation checks and record repo-wide baseline failures separately from story-scope verification:
  - [x] Targeted tests for changed areas
  - [x] `python -m pytest tests/` attempted and recorded
  - [x] `python -m ruff check modules/ tests/` attempted and recorded
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every output traces to source page, OCR engine, confidence, processing step
  - [x] T1 — AI-First: didn't write code for a problem AI solves better
  - [x] T2 — Eval Before Build: measured SOTA before building complex logic
  - [x] T3 — Fidelity: within this story’s slice, reviewed missing content is preserved and the bogus internal-heading chapter split is removed
  - [x] T4 — Modular: new recipe not new code; no hardcoded book assumptions
  - [x] T5 — Inspect Artifacts: visually verified outputs, not just checked logs

## Files to Modify

- `modules/extract/ocr_ai_gpt51_v1/main.py` — conservative blank-page handling and targeted reread/escalation for nonblank OCR-empty pages
- `modules/portionize/portionize_toc_html_v1/main.py` — if TOC quality gating needs to be tightened before using it as the preferred boundary source
- `configs/recipes/recipe-onward-images-html-mvp.yaml` — boundary-source selection for the Onward recipe if the generic TOC module outperforms headings on the real book
- `modules/build/build_chapter_html_v1/main.py` — only if we need stronger page-to-chapter trace output in the manifest or HTML build diagnostics
- `tests/test_build_chapter_html.py` — chapter assembly regressions
- `tests/test_ocr_ai_gpt51_empty_page_recovery.py` — regression coverage for sparse-text pages that must not be dropped
- `tests/test_portionize_toc_html.py` — TOC-derived boundary regression coverage if TOC becomes the selected source

## Notes

- Manual review defects feeding this story:
  - `chapter-005.html` in the failing run appears to miss printed pages 6 and 8; artifact tracing shows those correspond to OCR-empty source pages `Image014.jpg` and `Image016.jpg`
  - `chapter-028.html` in the failing run appears to miss printed page 101; artifact tracing shows that corresponds to `Image109.jpg`, which was skipped as blank upstream
  - `chapter-011.html` / `chapter-012.html` / `chapter-013.html` — one family’s material split across three files, with the middle file mislabeled "Sharon's Family"
- This story is about missing content and coarse chapter-boundary source selection, not table-cell structure quality or fine-grained family subsection splitting by itself.
- Do not solve this by adding title-specific exclusions like `"Sharon's Family" is never a chapter`. The solution must use generic evidence such as OCR emptiness, blank-page confidence, TOC presence, or stronger boundary-source selection.

## Plan

### Exploration Findings

- **Missing-page root cause is upstream OCR, not chapter assembly.**
  - In `onward-story009-full`, the reviewed missing pages are already empty in `02_ocr_ai_gpt51_v1/pages_html.jsonl`:
    - page 15 / `Image014.jpg` / printed page 6 → `ocr_empty_reason="Empty HTML output for page 15"`
    - page 17 / `Image016.jpg` / printed page 8 → `ocr_empty_reason="Empty HTML output for page 17"`
    - page 110 / `Image109.jpg` / printed page 101 → `ocr_empty_reason="blank_page_detected"`
  - `extract_page_numbers_html_v1` then infers printed page numbers for those empty rows, which lets downstream stages include empty spans without surfacing the real coverage loss.

- **The simplest OCR recovery paths already work on the reviewed pages.**
  - Baseline: current failing run recovers `0/3` of the reviewed missing pages.
  - Same OCR module, same Gemini model, `skip_blank_pages=false` on the three-page fixture recovers `1/3`: `Image109.jpg` now produces HTML for printed page 101.
  - Stronger targeted reread (`gpt-5.1`) on the remaining two nonblank OCR-empty pages recovers `2/2`: `Image014.jpg` and `Image016.jpg` both produce full prose output.
  - This strongly suggests a generic detect → re-read loop is higher leverage than any Onward-specific content patch.

- **The current chapter-boundary source is wrong on the reviewed family span.**
  - `08_portionize_headings_html_v1/portions_headings.jsonl` creates a standalone chapter `"SHARON'S FAMILY"` at printed pages 32-33 because it treats every qualifying `<h1>` as a chapter boundary.
  - The source TOC on page image 8 (`Image007.jpg`, rendered in OCR HTML) lists `Arthur ... 26` and `Leonidas ... 37`, which contradicts the current heading-based split at printed page 29 and leaves no room for a standalone `Sharon's Family` chapter.
  - Running the generic `portionize_toc_html_v1` on the same artifact set removes the `Sharon's Family` chapter entirely and produces a chapter map aligned to the book-authored TOC.

- **Files most likely to change**
  - `modules/extract/ocr_ai_gpt51_v1/main.py`
  - `configs/recipes/recipe-onward-images-html-mvp.yaml`
  - Possibly `modules/portionize/portionize_toc_html_v1/main.py`
  - Possibly `modules/build/build_chapter_html_v1/main.py` for trace output
  - New regression tests for OCR-empty recovery and TOC-driven chapter boundaries

### Eval-First Baseline

- **Missing-page coverage baseline**
  - Failing run: `0/3` reviewed pages preserved.
  - Same-model rerun without blank skipping: `1/3` preserved.
  - Stronger targeted reread on remaining nonblank empties: `3/3` preserved.

- **Boundary baseline**
  - Failing run: one confirmed spurious chapter (`"SHARON'S FAMILY"`) produced by heading-only portionization.
  - TOC-derived baseline: `0` standalone `Sharon's Family` chapters; boundary map aligns with the source TOC page.

### Implementation Plan

#### Task 1: Fix OCR-empty page handling generically
- **Files**: `modules/extract/ocr_ai_gpt51_v1/main.py`, `tests/test_ocr_ai_gpt51_empty_page_recovery.py`
- **Changes**:
  - Add a targeted reread path for pages that return empty HTML but are not confidently blank.
  - Add `retry_model` / capped retry parameters so OCR can escalate only the flagged pages instead of re-running the whole corpus with a stronger model.
  - Tighten blank-page handling so sparse-text pages with large white areas are not silently skipped; if the detector remains uncertain, prefer OCR over skipping.
- **Why this is general**: it relies on generic signals (`ocr_empty`, blank confidence, sparse-text layout), not book-specific page IDs.
- **Done when**: the reviewed empty pages survive OCR in a rerun, and regression tests prove sparse-text nonblank pages are not discarded.

#### Task 2: Use the stronger chapter-boundary source instead of every `<h1>`
- **Files**: `configs/recipes/recipe-onward-images-html-mvp.yaml`, optionally `modules/portionize/portionize_toc_html_v1/main.py`, `tests/test_portionize_toc_html.py`
- **Changes**:
  - Reintroduce TOC-derived chapter portionization for this TOC-bearing book using the existing generic module, or tighten its TOC-quality gate if needed before selecting it.
  - Keep the solution generic: use source TOC structure because it is the book-authored boundary signal, not because of any specific family title.
  - Only fall back to heading-derived chapter spans if the TOC parser fails its quality checks.
- **Why this is general**: `portionize_toc_html_v1` already exists as the generic TOC path and is used by the generic image-to-HTML recipe.
- **Done when**: the regenerated chapter map no longer emits a standalone `Sharon's Family` chapter and the reviewed family material follows the TOC-authored boundaries.

#### Task 3: Strengthen traceability for page-to-chapter coverage
- **Files**: `modules/build/build_chapter_html_v1/main.py`, `tests/test_build_chapter_html.py`
- **Changes**:
  - If needed, add source-page lists or equivalent coverage trace data to `chapters_manifest.jsonl` so reviewed missing-page investigations do not require manual reverse-engineering from page ranges alone.
- **Why this is general**: chapter-level provenance improves debugging and validation for any book.
- **Done when**: the rebuilt run makes it easy to show exactly which source pages landed in which HTML file.

### Impact Analysis

- **Most likely outcome**: Story 137 becomes a two-part fix:
  - OCR-empty recovery closes the reviewed missing-page defects.
  - TOC-first portionization closes the spurious chapter-boundary defects.
- **What could break**
  - OCR retries may increase cost slightly; the plan limits this by escalating only flagged pages.
  - Switching the boundary source may renumber chapter HTML files and change chapter titles broadly in the Onward run. This is acceptable if the new map matches the source TOC, but it is a user-visible change and should be treated as the main approval risk.
- **No blockers**: no new external dependencies or schema migrations expected.

### What Done Looks Like

- Reviewed source pages `Image014.jpg`, `Image016.jpg`, and `Image109.jpg` all survive OCR and appear in final HTML.
- The final chapter map no longer creates standalone chapters from internal family headings when the TOC indicates otherwise.
- The run artifacts include a clear page-to-chapter trace for the reviewed pages.
- Driver-based rerun succeeds, artifacts are manually inspected, and the work log records the verified output paths.

## Work Log

### 20260312-1710 — story created from manual review
- **Result:** Created a focused follow-up story for reviewed missing prose pages and bad chapter-boundary splits in `onward-story009-full`.
- **Evidence:** User review identified missing content on `chapter-005.html` (pages 6 and 8), missing page 101 content on `chapter-028.html`, and a bad family split across `chapter-011.html` through `chapter-013.html`.
- **Next:** Build-story should trace the reviewed pages through intermediate artifacts before changing code.

### 20260312-1700 — exploration: root causes split into OCR-empty coverage loss and wrong boundary source
- **Result:** Traced the reviewed defects through the real Onward artifacts and validated the simplest recovery/boundary alternatives before planning implementation.
- **Evidence:**
  - `02_ocr_ai_gpt51_v1/pages_html.jsonl` already contains empty output for the reviewed missing pages:
    - page 15 / `Image014.jpg` / printed page 6 → `ocr_empty_reason="Empty HTML output for page 15"`
    - page 17 / `Image016.jpg` / printed page 8 → `ocr_empty_reason="Empty HTML output for page 17"`
    - page 110 / `Image109.jpg` / printed page 101 → `ocr_empty_reason="blank_page_detected"`
  - Visual inspection of `/Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images/Image014.jpg`, `/Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images/Image016.jpg`, and `/Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images/Image109.jpg` confirmed all three images contain real source text.
  - Same-model rerun without blank skipping on the three-page fixture (`/tmp/story137-empty-ocr-gemini/pages_html.jsonl`) recovered `Image109.jpg` but not `Image014.jpg` or `Image016.jpg`.
  - Stronger targeted OCR (`/tmp/story137-empty-ocr-gpt51/pages_html.jsonl`) recovered the remaining two nonblank empty pages.
  - `08_portionize_headings_html_v1/portions_headings.jsonl` emits a standalone `SHARON'S FAMILY` chapter at printed pages 32-33.
  - The source TOC page in OCR HTML (page image 8) lists `Arthur ... 26` and `Leonidas ... 37`; running `portionize_toc_html_v1` on the same pages (`/tmp/story137-toc-portions.jsonl`) removes the standalone `Sharon's Family` chapter and produces TOC-aligned boundaries.
- **Decision:** The implementation should not try to "fix chapter-005" or "fix Sharon's Family" directly. It should:
  - add a generic OCR-empty recovery path for nonblank pages,
  - use the stronger generic chapter-boundary source (TOC) for this TOC-bearing book instead of over-trusting every inline `<h1>`.
- **Next:** Present the plan and approval gate before writing code.

### 20260312-1945 — implementation: generic OCR-empty recovery + TOC-first boundary source verified in driver run
- **Result:** Implemented a generic OCR escalation loop for nonblank empty pages, switched the Onward recipe from heading-based portionization to the existing TOC portionizer, added regression coverage, and verified the rebuilt HTML through `driver.py`.
- **Impact:**
  - Story-scope impact: the reviewed missing prose pages are no longer dropped upstream, and the spurious family split is removed without hard-coding any Onward title exclusions.
  - Pipeline-scope impact: sparse prose pages now prefer OCR over premature blank skipping, and chapter boundaries come from the stronger book-authored TOC signal instead of every qualifying inline `<h1>`.
  - Evidence:
    - `output/runs/story137-onward-verify/02_ocr_ai_gpt51_v1/pages_html.jsonl` now contains non-empty HTML for page 15 / `Image014.jpg`, page 17 / `Image016.jpg`, and page 110 / `Image109.jpg`
    - `output/runs/story137-onward-verify/07_portionize_toc_html_v1/portions_toc.jsonl` writes 23 TOC-derived portions, including `Arthur 26-36` and `Leonidas 37-47`, with no standalone `Sharon` portion
    - `output/runs/story137-onward-verify/output/html/chapter-005.html` contains recovered page-6/page-8 prose, and `output/runs/story137-onward-verify/output/html/chapter-021.html` contains the recovered page-101 prose
  - Next: hand the remaining genealogy-table fidelity issue on printed page 73 / source page 82 to Story 138 rather than expanding this story back into table-structure work
- **Code Changes:**
  - `modules/extract/ocr_ai_gpt51_v1/main.py`
    - made blank-page detection more conservative for sparse-text pages
    - added `_ocr_with_fallback()` and model-aware retry support so empty nonblank pages can escalate to a stronger OCR model
  - `modules/extract/ocr_ai_gpt51_v1/module.yaml`
    - added the `retry_model` parameter to the module contract
  - `configs/recipes/recipe-onward-images-html-mvp.yaml`
    - set `retry_model: gpt-5.1`
    - replaced `portionize_headings_html_v1` with `portionize_toc_html_v1`
    - wired `build_chapters` to the TOC-derived portions
  - `tests/test_ocr_ai_gpt51_empty_page_recovery.py`
    - added regression coverage for conservative blank detection and stronger-model empty-page retry
  - `tests/test_portionize_toc_html.py`
    - added regression coverage proving TOC boundaries outrank internal headings when the TOC is available
- **Checks:**
  - Targeted tests passed:
    - `python -m pytest tests/test_ocr_ai_gpt51_empty_page_recovery.py tests/test_portionize_toc_html.py tests/test_ocr_ai_gpt51_sanitize.py tests/test_ocr_ai_gpt51_schema.py`
    - `python -m ruff check modules/extract/ocr_ai_gpt51_v1/main.py tests/test_ocr_ai_gpt51_empty_page_recovery.py tests/test_portionize_toc_html.py`
  - Full integration run passed:
    - `python driver.py --recipe configs/recipes/recipe-onward-images-html-mvp.yaml --run-id story137-onward-verify --allow-run-id-reuse --output-dir output/runs/story137-onward-verify --instrument`
  - Repo-wide baselines are still not green:
    - `python -m pytest tests/` → 10 unrelated failures in existing driver/choice/combat/run-manager/navigation tests
    - `python -m ruff check modules/ tests/` → broad pre-existing lint debt outside this change set
- **Manual Verification:**
  - Opened `output/runs/story137-onward-verify/output/html/index.html` and verified `Arthur` and `Leonidas` are present while `Sharon` is not listed as a chapter.
  - Opened `output/runs/story137-onward-verify/output/html/chapter-005.html` and confirmed the recovered prose snippets `"George was born in 1891"` and `"Our haying machinery was overhauled and ready to go"` are present.
  - Opened `output/runs/story137-onward-verify/output/html/chapter-021.html` and confirmed the recovered page-101 prose snippets `"children in the western provinces"` and `"He lost his last fight with death at the age of 82 in 1983"` are present.
  - Opened `output/runs/story137-onward-verify/output/html/chapter-010.html` and `chapter-011.html` and confirmed the rebuilt navigation now flows `Arthur -> Leonidas -> Josephine` with no standalone `Sharon's Family` chapter file.
- **Residual Risk:**
  - `output/runs/story137-onward-verify/06_table_rescue_onward_tables_v1/pages_html_onward_tables.jsonl` still has one unresolved genealogy-table page (`page_number=82`, printed page 73). That is a Story 138 table-fidelity issue, not a missing-content or chapter-boundary regression.

### 20260313-0905 — round-2 manual review: content recovery succeeded, but broader fine-grained structure defects remain
- **Result:** Manual review of `story137-onward-verify` confirms the dropped-content problem is materially improved, but it also exposes a broader class of remaining structure defects that the TOC-first change did not solve.
- **Evidence:**
  - `chapter-005.html` and `chapter-021.html` now contain the previously missing prose, but both still split paragraphs mid-sentence across page breaks
  - `chapter-008.html`, `chapter-011.html`, `chapter-017.html`, `chapter-019.html`, and `chapter-020.html` still show bad family/section grouping that a coarse TOC map alone does not resolve
  - The next/back labels in `chapter-021.html` do not match the visible family heading, showing that current title selection is still unstable
- **Decision:** Treat Story 137 as the proof that OCR-empty recovery works and that TOC-first boundaries help, but move the remaining fine-grained section-splitting and page-break continuation defects into a dedicated follow-up story rather than silently broadening this one again.
- **Next:** Open a dedicated story for hybrid section splitting and page-break continuation on partial-TOC genealogy books.

### 20260313-0935 — validation reopened boundary/fidelity checkboxes
- **Result:** Revalidated the story against the current `story137-onward-verify` HTML and reopened the boundary/fidelity checkboxes that were overstated.
- **Evidence:**
  - `output/runs/story137-onward-verify/output/html/chapter-008.html` still merges `L'HEUREUX VETERANS OF WORLD WAR I & II` with `Alma Marie (L'Heureux) Alain`
  - `output/runs/story137-onward-verify/output/html/chapter-011.html` still combines `JOSEPHINE` and `PAUL L'HEUREUX`
  - `output/runs/story137-onward-verify/output/html/chapter-021.html` still carries the wrong chapter ownership signal (`Wilfred` in navigation/title while rendering `Pierre L'Heureux`)
- **Decision:** Acceptance criteria 2 and 4, plus Tenet `T3`, remain open. Story 137 stays `In Progress`; the residual defects are now tracked explicitly in Stories 138 and 139.
- **Next:** Do not mark this story `Done` until the fine-grained section-splitting and family-ownership defects are fixed and revalidated.

### 20260313-1035 — rescope for closure: shipped slice isolated from follow-up structure work
- **Result:** Narrowed Story 137 to the slice it actually delivered: generic OCR empty-page recovery plus TOC-first coarse chapter-boundary selection. Removed the broader claim that it solved fine-grained family ownership inside every TOC-derived chapter.
- **Evidence:**
  - `output/runs/story137-onward-verify/02_ocr_ai_gpt51_v1/pages_html.jsonl` contains recovered HTML for `Image014.jpg`, `Image016.jpg`, and `Image109.jpg`
  - `output/runs/story137-onward-verify/07_portionize_toc_html_v1/portions_toc.jsonl` eliminates the standalone `Sharon's Family` chapter and restores the coarse `Arthur` → `Leonidas` → `Josephine` sequence
  - Remaining fine-grained structure defects are tracked in Story 139, and table-continuation/header defects are tracked in Story 138
- **Decision:** Story 137 should be validated and closed on the shipped slice rather than kept artificially open for follow-up work that is now explicitly tracked elsewhere.
- **Next:** Re-run the close-out validation against the rescoped story, then update story status/index/changelog if the revised acceptance criteria are satisfied.

### 20260313-1048 — close-out validation: rescoped story satisfied; baseline repo failures remain unrelated
- **Result:** Re-ran the repo-wide checks, confirmed the same unrelated baseline failures remain, and closed Story 137 on the rescoped slice with user-approved follow-up stories handling the remaining defects.
- **Evidence:**
  - `python -m pytest tests/` still reports the same 10 failing baseline tests outside Story 137 scope:
    - `tests/driver_integration_test.py` (4)
    - `tests/test_extract_choices_relaxed_orphan_reocr.py` (1)
    - `tests/test_extract_combat_v1.py` (1)
    - `tests/test_run_manager.py` (2)
    - `tests/test_validate_ff_engine_v2_navigation.py` (2)
  - `python -m ruff check modules/ tests/` still reports broad pre-existing repo lint debt (`306` findings) outside this change set
  - Story-scope evidence remains green in `output/runs/story137-onward-verify/02_ocr_ai_gpt51_v1/pages_html.jsonl`, `output/runs/story137-onward-verify/07_portionize_toc_html_v1/portions_toc.jsonl`, and `output/runs/story137-onward-verify/output/html/index.html`
- **Decision:** With the story narrowed to OCR empty-page recovery and TOC coarse boundary selection, all acceptance criteria for this slice are satisfied. Residual fine-grained structure defects stay in Story 139, table continuation/header defects stay in Story 138, and image placement/caption defects stay in Story 135.
- **Next:** Build Story 139 next, then re-evaluate how much residual table drift remains for Story 138.
