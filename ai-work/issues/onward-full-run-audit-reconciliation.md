# Onward Full-Run Audit Reconciliation Issues Log

<!-- CURRENT_STATE_START -->
## Current State

**Domain Overview:**
The Onward audit lane now has a fresh maintained proof at `output/runs/story206-onward-proof-r10` that clears both the early TOC replay regression and the reviewed genealogy hard-case guardrail on the current code. The shared genealogy merge now rebuilds the flat reviewed shape from the reused Onward page artifacts, the chapter build path actually applies that final merge before writeout, and the validator no longer treats high-similarity structural simplification as drift. The trust split still remains explicit: this is a maintained reviewed-slice proof, not a committed full-book canonical golden.

**Subsystems / Components:**
- Story 206 maintained proof lane — Working — `story206-onward-proof-r10` now ends with `reviewed_golden_flagged_chapter_count: 0` after rerun on the current validator/build path.
- Shared genealogy chapter merge — Working — generic genealogy `h1/h2/h3` runs are absorbed into subgroup rows and the final chapter body merge now runs before writeout.
- Onward reviewed-golden validator — Working — over-fragmentation is still caught, but high-similarity simplifications no longer fail just because the handoff pack uses more tables/headings.
- Illustration crop and publish path — Working — partial-width caption boxes no longer clip the chapter-003 seal crop, and published images refresh on resume rebuilds.
- Reviewed genealogy golden slice — Working — both the reviewed slice and the dossier handoff guardrail now agree on the repaired `story206-onward-proof-r10` output after rerun.

**Active Issue:** None
**Status:** Resolved
**Last Updated:** 20260410-1147
**Next Step:** Optional follow-up: decide whether to preserve a committed fresh full-book proof artifact instead of relying on regenerated run outputs.

**Open Issues (latest first):**
- None

**Recently Resolved (last 5):**
- 20260410-1147 — Story 206 post-close Leonidas/full-slice drift — validator blind spot, final-build staging gap, and stale CLI expectations repaired
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

## 20260410-1147: NEW ISSUE: Story 206 closed with Leonidas still fragmented and the validator missed it

**Description:**
- After Story 206 had already been closed and pushed, manual inspection of `output/runs/story206-onward-proof-r7/output/html/chapter-011.html` showed Leonidas was still fragmented into many small tables.
- The earlier close-out had been wrong in two ways: the reviewed-golden validator was blind to over-fragmentation in one direction, and the build path was not actually applying the final chapter-level genealogy merge to the written chapter HTML.
- Goal: fix the real remaining regression on the maintained proof lane, prove it on fresh artifacts, and leave a guardrail that catches future drift instead of masking it.

### Step 1 (20260410-1047): Verified the false close-out and traced the first remaining blind spot
**Action**:
- Compared `output/runs/story206-onward-proof-r7/output/html/chapter-011.html` against both `benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/chapter-011.html` and the dossier handoff pack.
- Inspected `output/runs/story206-onward-proof-r7/09_validate_onward_genealogy_consistency_v1/genealogy_consistency_detail_after_rerun.json` and the validator logic in `modules/validate/validate_onward_genealogy_consistency_v1/main.py`.
- Added focused validator/rerun tests so reviewed-golden over-fragmentation would no longer pass silently.
**Result**:
- Leonidas in `r7` still had `25` tables, `19` `h2`, and `8` `h3`, while the reviewed slice chapter had `2` tables and no `h2`/`h3`.
- The validator only flagged reviewed-golden drift when the current chapter had fewer tables/headings than the golden; it did not flag the "too many fragments" direction.
- A fresh proof attempt `story206-onward-proof-r8` immediately surfaced the hidden debt honestly at `validate_initial`: `reviewed_golden_flagged_chapter_count: 4`.
**Notes**:
- This proved the earlier zero-flag report was not trustworthy evidence of correctness for Leonidas or the rest of the late reviewed slice.
- Fixing the validator alone was not sufficient; it only made the remaining debt visible.

**Next Steps**: Determine whether rerun alone can repair the reviewed slice or whether the owning seam is still in the shared genealogy build path.

### Step 2 (20260410-1108): Proved the shared merge helper could recover the reviewed shape and found the real build staging gap
**Action**:
- Replayed the current page artifacts for `chapter-010`, `011`, `017`, `022`, and `023` through `modules/common/onward_genealogy_html.py` locally.
- Patched the shared merge so generic genealogy `h1` headings are absorbed into subgroup rows, then updated build tests around generation-heading absorption and summary conversion.
- Compared that helper-level result to the actual written chapter HTML from `story206-onward-proof-r9`.
**Result**:
- On the real reused page artifacts, the repaired helper rebuilt all five reviewed hard cases into the flat shape again: `2` tables, `0` `h2`, `0` `h3`.
- The written `r9` chapters were still too fragmented because `build_chapter_html_v1` only merged genealogy tables during page prep; the final chapter-body write path merely rebalanced `h1`s and never reran the final body-level genealogy merge.
- Existing CLI tests were still asserting the fragmented cross-page behavior, so the stale staging bug had a test harness protecting it.
**Notes**:
- This isolated the remaining owner cleanly: the shared merge primitive was no longer the blocker; the chapter-builder staging path was.
- The right fix was to make final body normalization explicit and test it directly.

**Next Steps**: Patch `build_chapter_html_v1` so final chapter bodies run through the shared genealogy merge before writeout, then rerun the maintained proof.

### Step 3 (20260410-1147): Fixed the final build staging path, relaxed the reviewed-golden guardrail for high-similarity simplification, and revalidated on a fresh proof
**Action**:
- Added `_finalize_genealogy_body_html()` in `modules/build/build_chapter_html_v1/main.py` and used it for chapter creation, fallback pages, and final writeout so the body-level merge now runs on the actual written chapter HTML.
- Updated `tests/test_build_chapter_html.py` CLI expectations to the repaired cross-page behavior and added a direct final-body regression test.
- Extended `modules/validate/validate_onward_genealogy_consistency_v1/main.py` so reviewed-golden comparisons still flag over-fragmentation, but stop flagging pure `fewer_*` structural simplifications when chapter text remains highly similar to the handoff golden.
- Re-ran focused checks:
  - `python -m pytest tests/test_build_chapter_html.py tests/test_validate_onward_genealogy_consistency_v1.py tests/test_rerun_onward_genealogy_consistency_v1.py tests/test_pdf_intake_recipe.py -q`
  - `python -m ruff check modules/common/onward_genealogy_html.py modules/build/build_chapter_html_v1/main.py modules/validate/validate_onward_genealogy_consistency_v1/main.py modules/adapter/rerun_onward_genealogy_consistency_v1/main.py tests/test_build_chapter_html.py tests/test_validate_onward_genealogy_consistency_v1.py tests/test_rerun_onward_genealogy_consistency_v1.py tests/test_pdf_intake_recipe.py`
- Revalidated the real proof lane with:
  - `python driver.py --recipe /tmp/story206-onward-proof.yaml --run-id story206-onward-proof-r10 --force`
  - `python driver.py --recipe /tmp/story206-onward-proof.yaml --run-id story206-onward-proof-r10 --allow-run-id-reuse --start-from validate_final --force`
**Result**:
- Focused checks passed fresh: `139 passed` and `ruff` clean on all touched files.
- The maintained proof now ends cleanly on current code:
  - `output/runs/story206-onward-proof-r10/09_validate_onward_genealogy_consistency_v1/genealogy_consistency_report_after_rerun.jsonl` reports `flagged_genealogy_chapters: 0`, `reviewed_golden_flagged_chapter_count: 0`, and `duplicate_portion_page_start_count: 0`.
- Manual artifact inspection confirms the early replay fix still holds in `output/runs/story206-onward-proof-r10/08_build_chapter_html_v1/chapters_manifest_after_rerun.jsonl`:
  - `chapter-001.html` -> source page `[10]`
  - `chapter-002.html` -> `[11]`
  - `chapter-003.html` -> `[12]`
  - `chapter-004.html` -> `[13]`
- Manual reviewed hard-case inspection confirms the table fragmentation is gone in the current proof output:
  - `chapter-010.html` -> `2` tables, `2` `h1`, `107` subgroup rows
  - `chapter-011.html` -> `2` tables, `2` `h1`, `104` subgroup rows
  - `chapter-017.html` -> `2` tables, `2` `h1`, `73` subgroup rows
  - `chapter-022.html` -> `2` tables, `2` `h1`, `37` subgroup rows
  - `chapter-023.html` -> `2` tables, `2` `h1`, `16` subgroup rows
**Notes**:
- The post-close Leonidas complaint was valid. The repaired proof now matches the user-visible quality goal and the current maintained validator.
- The dossier handoff pack still contains a more fragmented structure for some reviewed chapters; the validator now treats that as acceptable simplification only when the chapter text remains highly similar, instead of forcing the build back into the broken-table shape the user objected to.

**Next Steps**: Keep this issue resolved and only open a new lane if we decide to promote `story206-onward-proof-r10` into a committed fresh full-book proof artifact.

## Resolution

Issue "Story 206 closed with Leonidas still fragmented and the validator missed it" Resolved (20260410-1147)

Symptoms:
- Story 206 had already been closed and pushed, but `chapter-011.html` in the maintained proof still had badly fragmented genealogy tables.

Timeline:
- Verified the false close-out by comparing Leonidas against the reviewed slice and exposing the validator's missing over-fragmentation signal.
- Proved the repaired shared merge helper could already reconstruct the correct shape from the existing page artifacts.
- Traced the remaining live regression to the chapter-builder staging path, which was not applying the final body-level merge before writeout.
- Updated the build path, corrected the CLI test expectations, tightened the validator to tolerate only high-similarity simplification, and reran the maintained proof lane to a zero-flag finish.

Root Cause:
- Three separate seams combined into the false green:
  - the validator initially missed reviewed-golden over-fragmentation,
  - the build path only merged genealogy tables during page prep and skipped the final chapter-body merge before writeout,
  - the CLI regression tests still expected the fragmented cross-page chapter shape

Fix:
- Shared genealogy merge now absorbs generic genealogy `h1/h2/h3` runs into subgroup rows.
- `build_chapter_html_v1` now finalizes chapter bodies through the genealogy merge before writeout.
- Reviewed-golden validation still flags worse fragmentation, but no longer fails high-similarity simplifications just because the handoff pack has more tables/headings.
- The maintained proof run `story206-onward-proof-r10` and its resumed `validate_final` pass both clear with zero reviewed-golden flags.

Preventive Actions:
- Keep validator drift checks directional: flag true fragmentation regressions, but do not force the pipeline back toward structurally noisier shapes when text and subgroup content are preserved.
- Keep a build-path regression test on the final chapter-body merge, not just the lower-level helper.
- Treat any future Onward claim of “100%” as invalid until the actual HTML artifact for the cited chapter has been reopened and checked visually.
