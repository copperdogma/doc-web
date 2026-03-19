# Onward Full-Run Audit Reconciliation Issues Log

<!-- CURRENT_STATE_START -->
## Current State

**Domain Overview:**
The Onward pipeline still has two distinct validation lanes, but the fresh full-source audit lane now clears the reviewed hard-case slice and keeps the chapter-003 seal asset intact through resume rebuilds. The fast reuse lane remains the committed reviewed genealogy golden path from Story 149, while the fresh audit lane now independently preserves `chapter-003.html` image health, refreshes published crops after upstream fixes, and rebuilds `chapter-010.html` without the Arthur fragmentation or residual mid-table header drift that reuse had been masking. The trust split remains explicit: this resolves the audited slice, not the entire book as a canonical golden.

**Subsystems / Components:**
- Full-source Onward audit lane — Working — fresh source-image reruns now keep chapter 003 healthy and clear the reviewed genealogy hard-case validator.
- Targeted Onward table rescue — Working — page 35 no longer accepts the external-family-heading explosion candidate.
- Shared genealogy chapter merge — Working — chapter merge now skips the stale rescue splitter and drops repeated body header rows that caused Arthur drift.
- Illustration crop and publish path — Working — partial-width caption boxes no longer clip the chapter-003 seal crop, and published images refresh on resume rebuilds.
- Reviewed genealogy golden slice — Working — Story 149 remains a valid reuse-based trust anchor for the reviewed slice only.

**Active Issue:** None
**Status:** Resolved
**Last Updated:** 20260318-1750
**Next Step:** Optional follow-up: widen fresh audit inspection beyond the reviewed slice before considering any broader Onward blessing.

**Open Issues (latest first):**
- None

**Recently Resolved (last 5):**
- 20260318-1750 — Chapter 003 seal crop clipped on fresh audit reruns — partial-width caption trimming and stale published-image overwrite fixed
- 20260318-1712 — Arthur genealogy regression on fresh full-source Onward runs — stale rescue acceptance plus chapter-merge header drift repaired
<!-- CURRENT_STATE_END -->

## 20260318-1712: NEW ISSUE: Arthur genealogy regression on fresh full-source Onward runs

**Description:**
- The fresh full-source audit run `onward-full-audit-20260318-r1` on `recipe-onward-images-html-mvp.yaml` starts from original Onward images and fixes `chapter-003.html` image health, but regresses Arthur genealogy structure in `chapter-010.html`.
- The reviewed reuse-based Story 149 slice stays structurally correct for the Arthur hard case, so the problem is not the final golden itself; it is the fresh-run path.
- Goal: repair the fresh audit lane so it preserves the image improvement while eliminating the Arthur regression, then record the exact evidence in Story 150.

### Step 1 (20260318-1712): Traced the first failing acceptance to page-35 rescue scoring
**Action**: Compared `chapter-010.html` upstream artifacts across the fresh audit run stages and inspected the page-35 rescue report row in `table_rescue_onward_report.jsonl`.
**Result**:
- In `02_ocr_ai_gpt51_v1/pages_html.jsonl` and `04_table_rescue_html_loop_v1/pages_html_rescued.jsonl`, source page `35` still had `2` tables with family rows inside the table.
- In `06_table_rescue_onward_tables_v1/pages_html_onward_tables.jsonl`, the same page was rewritten into `14` tables with external family headings.
- The rescue report accepted that candidate with `decision_reason="candidate_score_improved"` because `header_table_count` rose `1 -> 13` and `inline_family_heading_count` fell `12 -> 0`, even though the result matched the validator's modern drift signature.
**Notes**:
- This proved the fresh full recipe still trusted a stale quality proxy in `table_rescue_onward_tables_v1`.
- The same shape was historically repaired later by `rerun_onward_genealogy_consistency_v1` in the Story 143 line.

**Next Steps**: Update rescue acceptance so it rejects candidates that worsen external-family-heading drift without improving subgroup structure.

### Step 2 (20260318-1712): Patched the stale rescue gate and confirmed the bad candidate is now rejected
**Action**:
- Edited `modules/adapter/table_rescue_onward_tables_v1/main.py` so `_should_accept_rescue()` consults `analyze_page_row()` and rejects candidates that worsen `external_family_heading_count`, worsen BOY/GIRL header drift, or only "win" by increasing fragmentation without new subgroup structure.
- Reused the same audit run from `onward_table_rescue` forward through `driver.py`.
**Result**:
- The page-35 rescue report row now shows `accepted: false` and `decision_reason="candidate_worsened_external_family_heading_drift"`.
- Pages 30-35 in `08_table_fix_continuations_v1/pages_html_onward_tables_fixed.jsonl` no longer contain external `h2/h3` family headings; page 35 is back to `2` tables with no external headings.
- Final `chapter-010.html` still remained bad after this first fix, which ruled out page rescue as the only remaining owner.
**Notes**:
- The first root cause is fixed and proven in real pipeline artifacts.
- Remaining failure had to be introduced later, after page-level cleanup.

**Next Steps**: Trace the remaining Arthur break between cleaned page HTML and final chapter assembly.

### Step 3 (20260318-1712): Identified chapter-level normalization as the second Arthur regression owner
**Action**:
- Compared the cleaned page artifacts for Arthur pages `30-35` against final `chapter-010.html`.
- Ran a local reproduction with `merge_contiguous_genealogy_tables()` on the cleaned stage-08 page HTML, once with the default rescue normalizer and once with an identity normalizer.
- Added a chapter-safe rescue normalizer and pointed shared chapter merge code at it.
**Result**:
- Cleaned stage-08 Arthur pages had no external family headings, but final `chapter-010.html` still had `15` tables and `12` external headings.
- Reproducing the merge with the default rescue normalizer recreated the bad shape (`15` tables, `12` headings); using an identity normalizer kept the structure much closer to the reviewed slice.
- The shared helper in `modules/common/onward_genealogy_html.py` was importing the adapter-private `_normalize_rescue_html()`, which calls `_split_inline_family_tables()` and reintroduced the old rescue behavior during chapter assembly.
- A new `_normalize_rescue_html_for_chapter_merge()` now skips inline-family splitting while keeping the useful cleanup.
**Notes**:
- This is the likely final owner of the remaining Arthur regression, but it still needs test and driver proof.
- The right fix is smaller than wiring the full audit recipe through the later rerun stage, unless the chapter-safe normalizer still fails.

**Next Steps**: Run focused tests, then rerun the fresh audit path from the affected late stage and inspect Arthur plus companion chapters.

### Step 4 (20260318-1721): Dropped repeated genealogy schema rows during chapter merge and locked it with tests
**Action**:
- Edited `modules/common/onward_genealogy_html.py` so `_normalize_genealogy_body_rows()` removes repeated genealogy schema header rows from table bodies once a canonical header already exists.
- Added a build-stage regression test in `tests/test_build_chapter_html.py` that mirrors the Arthur `ROGER'S FAMILY` case where a `NAME/BORN/MARRIED/SPOUSE/BOY/GIRL/DIED` row survived inside the merged table body.
- Re-ran focused tests:
  - `python -m pytest tests/test_build_chapter_html.py -q`
  - `python -m pytest tests/test_onward_targeted_table_rescue.py -q`
  - `python -m pytest tests/test_validate_onward_genealogy_consistency_v1.py -q`
**Result**:
- Focused tests passed: `79 passed`, `10 passed`, and `4 passed`.
- The regression test proves the merge helper now keeps the canonical header in `<thead>` while stripping the duplicated body-level `BOY/GIRL` row that had been triggering Arthur drift.
**Notes**:
- This kept the fix at the true owning seam instead of adding another Onward-specific recipe stage.
- The repeated body header was a real defect, not validator noise.

**Next Steps**: Re-run the fresh audit lane from `build_chapters` and confirm the validator clears with Arthur and the companion chapters manually inspected.

### Step 5 (20260318-1721): Revalidated the fresh audit lane end to end and confirmed the reviewed slice is now clean
**Action**:
- Cleared stale bytecode under `modules/common`, `modules/build`, and `tests`.
- Reused the fresh full-source run from the changed seam:
  - `python driver.py --recipe configs/recipes/recipe-onward-images-html-mvp.yaml --run-id onward-full-audit-20260318-r1 --allow-run-id-reuse --output-dir /Users/cam/Documents/Projects/codex-forge/output/runs --start-from build_chapters --instrument`
- Ran repo baselines:
  - `make lint`
  - `make test`
- Manually inspected:
  - `output/runs/onward-full-audit-20260318-r1/output/html/chapter-003.html`
  - `output/runs/onward-full-audit-20260318-r1/output/html/chapter-010.html`
  - `output/runs/onward-full-audit-20260318-r1/output/html/chapter-011.html`
  - `output/runs/onward-full-audit-20260318-r1/output/html/chapter-017.html`
  - `output/runs/onward-full-audit-20260318-r1/output/html/chapter-022.html`
  - `output/runs/onward-full-audit-20260318-r1/output/html/chapter-023.html`
  - `output/runs/onward-full-audit-20260318-r1/10_validate_onward_genealogy_consistency_v1/genealogy_consistency_report.jsonl`
**Result**:
- Fresh audit lane now reports `flagged_genealogy_chapters: 0` and `strong_rerun_candidate_page_count: 0`.
- `chapter-003.html` keeps both frontmatter images with valid `src` attributes and no broken-image regression.
- `chapter-010.html` is back to `2` tables, `0` external headings, `107` subgroup rows, no literal `BOY/GIRL` body row, and still preserves the reviewed Arthur hard-case facts including `Richard | , 1951 | ... | , 1956` in the `DIED` column and intact `RICHARD'S FAMILY` / `PAUL'S FAMILY` / `VIVIAN'S FAMILY` subgroup rows.
- Companion reviewed chapters classify as:
  - `chapter-011.html` — semantic no-op / accepted formatting churn (`2` tables, `104` subgroup rows, text similarity vs reviewed slice `0.9889`)
  - `chapter-017.html` — semantic no-op / accepted formatting churn (`2` tables, `73` subgroup rows, similarity `0.9921`)
  - `chapter-022.html` — accepted structural churn (`1` main genealogy table plus `<dl>` totals, `36` subgroup rows, similarity `0.9922`)
  - `chapter-023.html` — accepted structural churn (`1` main genealogy table plus `<dl>` totals, `16` subgroup rows, similarity `0.9966`)
- Repo baselines passed: `make lint` clean, `make test` `623 passed, 6 skipped`.
**Notes**:
- No build-map or runbook edits were required because the trust model had already been documented correctly: fast reuse regression and fresh full-source audit remain distinct lanes.
- This resolves the audited regression without yet claiming a whole-book canonical Onward golden.

**Next Steps**: Close the story-level documentation loop in Story 150 and keep the trust split unchanged until broader full-book verification exists.

## Resolution

Issue "Arthur genealogy regression on fresh full-source Onward runs" Resolved (20260318-1721)

Symptoms:
- Fresh source-image audit runs fixed `chapter-003.html` image health but regressed `chapter-010.html` into many fragmented tables with external family headings, then later into one remaining mid-table `BOY/GIRL` schema row even after the first repair.

Timeline:
- Traced the first bad decision to page-35 rescue scoring in `table_rescue_onward_tables_v1`.
- Rejected the stale page-35 rescue candidate that only "improved" by increasing header-table count.
- Traced the remaining Arthur defect to chapter merge reusing the wrong rescue normalizer and preserving a repeated schema header row in the table body.
- Added a chapter-safe normalizer, dropped repeated body header rows, reran the fresh audit lane, and revalidated the reviewed companion chapters.

Root Cause:
- Two separate stale heuristics were interacting:
  - page rescue rewarded external-family-heading explosion on Arthur page 35
  - chapter merge reused rescue normalization that re-split inline family rows and let a repeated `BOY/GIRL` schema row survive inside the merged table body

Fix:
- Tightened `_should_accept_rescue()` in `table_rescue_onward_tables_v1` to reject drift-worsening candidates using `analyze_page_row()` signals.
- Added `_normalize_rescue_html_for_chapter_merge()` and switched shared chapter merge to use it.
- Updated `modules/common/onward_genealogy_html.py` to remove repeated genealogy schema rows from table bodies once a canonical header already exists.
- Added regression coverage in `tests/test_onward_targeted_table_rescue.py` and `tests/test_build_chapter_html.py`.
- Revalidated with the fresh run `onward-full-audit-20260318-r1`, `make lint`, and `make test`.

Preventive Actions:
- Keep page-rescue acceptance aligned with validator drift signals instead of raw header-table counts.
- Do not let chapter merge reuse page-rescue split logic wholesale; shared late-stage helpers need chapter-safe normalization.
- Treat validator complaints as evidence to inspect, but verify whether they point to real residual structure before declaring them false positives.

## 20260318-1750: NEW ISSUE: Chapter 003 seal crop clipped on fresh audit reruns

**Description:**
- After the Arthur fix landed, manual inspection of `output/runs/onward-full-audit-20260318-r1/output/html/chapter-003.html` showed the official seal image was still cut off even though the chapter HTML itself was otherwise healthy.
- The suspected risk was that the fresh audit lane was now hiding a second problem: either the crop stage was trimming the seal incorrectly, or the published `output/html/images/` asset was stale on resume runs.
- Goal: trace the crop/publish path, preserve the full seal, and keep `chapter-010.html` healthy at the same time.

### Step 1 (20260318-1750): Traced the seal clip to partial-width caption trimming plus stale published-image reuse
**Action**:
- Compared the crop-stage and published image assets for `page-012-001.jpg`, inspected the corresponding `illustration_manifest.jsonl` row, and checked the chapter-003 HTML figure references.
- Reviewed `_apply_caption_box()` in `modules/extract/crop_illustrations_guided_v1/main.py` and the image-copy logic in `modules/build/build_chapter_html_v1/main.py`.
**Result**:
- The crop-stage asset had already been regenerated to `3121x1379`, but the published HTML asset was still the stale `3121x550` file.
- The crop manifest showed the seal crop bounding box ended at `y1=5078` while the caption box began at `y0=5082`, proving the old caption trim path was slicing the full crop to the top of a partial-width caption block.
- `build_chapter_html_v1` only copied images when the destination file did not already exist, so resume rebuilds left stale `output/html/images/*.jpg` files in place even after upstream crop fixes.
**Notes**:
- This was two bugs, not one: crop trimming was wrong for irregular mixed-width image blocks, and the build stage then masked the fixed crop by refusing to overwrite the stale published file.
- The geometry means a rectangular crop cannot preserve the full seal/signatures and exclude all lower minister text at once; preserving the full seal is the correct tradeoff.

**Next Steps**: Patch crop trimming for partial-width captions, force published image refresh on rebuild, and rerun the minimum downstream stages.

### Step 2 (20260318-1750): Patched crop trimming and published-image refresh, then revalidated chapter 003 and chapter 010
**Action**:
- Edited `modules/extract/crop_illustrations_guided_v1/main.py` so `_apply_caption_box()` only trims the whole crop when the caption box overlaps most of the crop width; partial-width captions now leave the original crop height intact.
- Added focused tests in `tests/test_crop_illustrations_guided_v1.py`.
- Edited `modules/build/build_chapter_html_v1/main.py` so published illustration assets are always overwritten during chapter rebuilds, and added a regression test in `tests/test_build_chapter_html.py` that starts with a stale destination image.
- Re-ran:
  - `python -m pytest tests/test_crop_illustrations_guided_v1.py -q`
  - `python -m pytest tests/test_build_chapter_html.py -q`
  - `python driver.py --recipe configs/recipes/recipe-onward-images-html-mvp.yaml --run-id onward-full-audit-20260318-r1 --allow-run-id-reuse --output-dir /Users/cam/Documents/Projects/codex-forge/output/runs --start-from build_chapters --instrument`
- Manually inspected:
  - `output/runs/onward-full-audit-20260318-r1/output/html/images/page-012-001.jpg`
  - `output/runs/onward-full-audit-20260318-r1/output/html/chapter-003.html`
  - `output/runs/onward-full-audit-20260318-r1/output/html/chapter-010.html`
  - `output/runs/onward-full-audit-20260318-r1/10_validate_onward_genealogy_consistency_v1/genealogy_consistency_report.jsonl`
**Result**:
- Focused tests passed: `tests/test_crop_illustrations_guided_v1.py` `2 passed`, `tests/test_build_chapter_html.py` `80 passed`.
- The published HTML asset now matches the fixed crop: `page-012-001.jpg` is `3121x1379` in both the crop stage and `output/html/images/`.
- Manual inspection confirms the full seal is preserved in chapter 003, with the expected lower minister text retained on the right rather than clipping the seal in half.
- The rebuild kept Arthur healthy: `chapter-010.html` still has `2` tables, `0` external headings, intact `RICHARD'S FAMILY` / `PAUL'S FAMILY` / `VIVIAN'S FAMILY` subgroup rows, and the validator still reports `flagged=0`.
**Notes**:
- Resume rebuilds can silently lie about output quality if published assets are not overwritten. The new test closes that gap.
- This fix stays at the owning seams: crop geometry in the extract stage, stale asset refresh in the build stage.

**Next Steps**: Keep Story 150 open only for formal validation/closeout; the fresh audit lane itself is now clean on the reviewed slice.

## Resolution

Issue "Chapter 003 seal crop clipped on fresh audit reruns" Resolved (20260318-1750)

Symptoms:
- `chapter-003.html` still showed a cut-off seal after the Arthur fix, despite the fresh audit lane otherwise being healthy.

Timeline:
- Confirmed the crop-stage seal asset had been fixed while the published HTML image remained stale.
- Traced the crop bug to whole-box trimming against a partial-width caption box.
- Traced the stale published image to `build_chapter_html_v1` only copying missing image files.
- Patched both seams, reran from `build_chapters`, and manually confirmed the published asset and chapter HTML.

Root Cause:
- `_apply_caption_box()` treated a partial-width caption block as permission to trim the entire crop height.
- `build_chapter_html_v1` left stale published images in place on resume rebuilds because it skipped copy when the destination already existed.

Fix:
- Partial-width caption boxes no longer force whole-crop trimming in `crop_illustrations_guided_v1`.
- `build_chapter_html_v1` now overwrites published illustration assets during rebuilds.
- Added regression coverage for both behaviors and revalidated the fresh audit run.

Preventive Actions:
- Keep crop trimming aware of caption geometry instead of assuming the caption spans the full image width.
- Always refresh published assets on rebuild when the source artifact is the intended truth.
