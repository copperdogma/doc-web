# Story 184 — Collapse Bounded Crop Runtime to Flash-First Simplification

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #4 (Illustrate), Requirement #6 (Validate), Fidelity to the source, Transparency over magic
**Spec Refs**: spec:4 (spec:4.1, spec:4.2, C4, C5), spec:8 (B1)
**Build Map Refs**: Category 4 Illustration Extraction (`exists`; C4 `converge`, C5 `climb`); Gap 1 “Illustration crop simplification and text-exclusion breadth”; Input Coverage rows `scanned-pdf-tables` and `image-directory-scans` now both inherit `illustration = 0.968`
**Decision Refs**: `docs/runbooks/crop-eval-workflow.md`, `docs/stories/story-133-gemini-flash-crop-detector.md`, `docs/stories/story-150-onward-full-run-audit-reconciliation.md`, `docs/stories/story-183-crop-benchmark-substrate-and-c5-validation-surface.md`, `None found after search in docs/decisions/` for a crop-specific ADR
**Depends On**: Story 133, Story 150, Story 183

## Goal

Collapse the maintained Onward crop runtime from the current detector+retry+validator production path to the bounded Flash-first seam that now clears the C4 deletion gate. The story keeps the currently needed C5 layout-text trim in place, removes the maintained recipe's retry/refine/validator loops, keeps only the caption-assist pass that the reviewed Onward slice still needs, and proves with a real resumed `driver.py` run plus manual artifact inspection that published crop and HTML quality stay clean.

## Acceptance Criteria

- [x] The maintained Onward recipe no longer depends on the validator / retry / refine loop to publish illustration crops on the bounded slice:
  - [x] `rescue_retry_on_overlap = false`
  - [x] `rescue_retry_on_missing = false`
  - [x] `rescue_retry_on_text = false`
  - [x] `rescue_refine_boxes = false`
  - [x] `rescue_validate_crops = false`
  - [x] the maintained path is Flash-first with only the bounded caption-assist pass plus current layout-text trim
- [x] Fresh real-run evidence exists from this pass using `driver.py` on the reviewed Onward run root, reusing existing OCR/table artifacts and rerunning the crop/build seam only:
  - [x] crop artifacts regenerate successfully,
  - [x] final HTML/image publication regenerates successfully,
  - [x] no new crop-count or obvious caption/text contamination regression is introduced on the inspected slice
- [x] Manual artifact inspection is recorded with exact artifact paths and sample observations for at least:
  - [x] the crop manifest,
  - [x] one published seal/text-bearing image case,
  - [x] one published cover/title-page case,
  - [x] and at least one final chapter HTML file that embeds refreshed illustration assets
- [x] Focused regression coverage or config-contract coverage exists so the maintained recipe does not silently drift back to the removed validator/retry settings
- [x] `docs/build-map.md` and any directly affected crop runtime docs describe the post-change reality honestly: C4 bounded simplification proof landed, C5 layout trim still active

## Out of Scope

- Deleting `trim_layout_text` or claiming `C5` is resolved
- Broadening the crop-validation corpus or reopening the model-selection benchmark
- Rewriting `crop_illustrations_guided_v1` architecture for other recipes or historical paths unless the real-run evidence exposes a small generic defect
- Fresh OCR reruns of the full Onward source set when the reviewed OCR artifacts are already reusable

## Approach Evaluation

- **Simplification baseline**: yes, this is now evidence-backed. `single-model-crop-detection` is `0.9678 / 1.0` on 2026-04-03, so the open question is runtime collapse, not detector capability.
- **AI-only**: low value. The missing work is not “can a model do it?” anymore; it is removing maintained runtime complexity and proving artifact quality survives.
- **Hybrid**: strongest candidate. Keep the Flash detector call, retain the bounded caption-assist pass and current layout-text trim, remove validator/retry/refine loops, and validate on the real Onward artifact seam.
- **Pure code**: plausible only if a recipe-only change is insufficient. Prefer config contraction over module surgery because the existing runtime already exposes the needed booleans.
- **Repo constraints / prior decisions**: Story 133 made Gemini 3 Flash the maintained detector and Story 150 documented real published-asset failure modes on the same Onward run root, including the need to refresh final HTML image assets after crop-stage changes. Story 183 repaired the benchmark substrate and promoted the C4/C5 truth surfaces. No crop-specific ADR exists.
- **Existing patterns to reuse**: recipe-level parameter control in `configs/recipes/recipe-onward-images-html-mvp.yaml`; the reviewed Onward run root `onward-full-audit-20260318-r1`; Story 150’s resume pattern that reruns only the affected downstream seam and then inspects both crop-stage and published HTML assets.
- **Eval**: the deciding proof is a narrow real `driver.py` resume using the existing reviewed Onward run artifacts, not another promptfoo sweep. The benchmark already says the single-stage detector clears the bounded bar.

## Tasks

- [x] Record exploration findings in the work log and keep the story honest about the available substrate:
  - [x] verified crop module config seam,
  - [x] verified reviewed Onward run root and reusable OCR/table artifacts,
  - [x] verified external Onward image source path used by the stamped manifests
- [x] Collapse the maintained crop runtime on the bounded Onward recipe by changing recipe config first, not module architecture
- [x] Add focused regression coverage for the maintained crop recipe contract so the removed validator/retry settings cannot silently drift back
- [x] Run fresh verification on the real runtime seam:
  - [x] clear stale crop module `*.pyc`
  - [x] rerun `crop_illustrations` on the reviewed Onward run root while reusing upstream OCR artifacts
  - [x] rerun `build_chapters` / downstream publication using the refreshed crop artifact without redoing expensive table stages if the driver substrate supports that honestly
  - [x] manually inspect regenerated crop and HTML artifacts
- [x] If this story changes documented format coverage or graduation reality: update `docs/build-map.md` and record the before/after state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: targeted pytest for touched scope, and widen only if needed
  - [x] Default Python lint: targeted ruff or repo lint for touched scope
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/` or the reused shared run root, and manually inspect sample JSON/JSONL/HTML data
  - [x] If agent tooling changed: not expected
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: refreshed artifacts still point back to source page/image and module lineage
  - [x] T1 — AI-First: remove code/loop complexity now that the model seam is good enough
  - [x] T2 — Eval Before Build: simplification is justified by the fresh 2026-04-03 bounded eval pass
  - [x] T3 — Fidelity: no new clipping, missing images, or text contamination regressions
  - [x] T4 — Modular: keep the change recipe-scoped; do not hardcode Onward into the module
  - [x] T5 — Inspect Artifacts: review regenerated crop and final HTML assets manually

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: maintained Category 4 crop runtime, owned primarily by `configs/recipes/recipe-onward-images-html-mvp.yaml` with verification through the existing `crop_illustrations_guided_v1` and `build_chapter_html_v1` seams
- **Build-map reality**: Category 4 is already at `C4 converge` because the bounded deletion gate passed. This story is the promised runtime proof that converts that eval success into actual simplification on the maintained image-directory proof lane while leaving `C5` layout trim in `climb`.
- **Substrate evidence**: verified in this pass that `modules/extract/crop_illustrations_guided_v1/main.py` already exposes booleans for `rescue_retry_on_overlap`, `rescue_retry_on_missing`, `rescue_retry_on_text`, `rescue_caption_second_pass`, `rescue_refine_boxes`, and `rescue_validate_crops`; `configs/recipes/recipe-onward-images-html-mvp.yaml` currently turns them on; `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/02_ocr_ai_gpt51_v1/pages_html.jsonl` and `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/illustration_manifest.jsonl` exist; and the stamped upstream artifacts reference the real external source directory `/Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images`.
- **Data contracts / schemas**: no schema change is expected if this remains a recipe/config contraction plus regression coverage. Published artifact schemas should remain unchanged.
- **File sizes**: `configs/recipes/recipe-onward-images-html-mvp.yaml` (192 lines), `docs/build-map.md` (595 lines), `docs/stories.md` (192 lines), `modules/extract/crop_illustrations_guided_v1/main.py` (4155 lines, avoid if possible), `modules/extract/crop_illustrations_guided_v1/module.yaml` (581 lines, avoid unless doc strings must change)
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md` (`spec:4`), `docs/build-map.md`, `docs/runbooks/crop-eval-workflow.md`, Story 133, Story 150, Story 183, the current recipe, the current crop module, and the reviewed Onward run root. No crop-specific ADR exists, which is acceptable here because this is bounded simplification of an existing maintained seam rather than a new cross-cutting architecture decision.

## Files to Modify

- `docs/stories/story-184-collapse-bounded-crop-runtime-to-single-stage-flash.md` — story plan, work log, implementation evidence
- `docs/stories.md` — add Story 184 and keep status honest (192 lines)
- `configs/recipes/recipe-onward-images-html-mvp.yaml` — remove maintained validator/retry/refine settings from the bounded crop path (192 lines)
- `modules/build/build_chapter_html_v1/main.py` — suppress adjacent duplicate OCR paragraphs when a text-bearing crop already carries that text in the published figure
- `docs/spec.md` — align the C4 compromise description with the bounded maintained Flash-first runtime reality
- `docs/build-map.md` — update Category 4 / Gap 1 wording if the runtime simplification proof lands (595 lines)
- `docs/runbooks/crop-eval-workflow.md` — only if the maintained runtime description needs to change after the proof
- `tests/test_build_chapter_html.py` — regression coverage for duplicate-text suppression on text-bearing published crops
- `tests/test_crop_runtime_recipe_contract.py` — focused regression coverage for the maintained crop recipe contract (new file)

## Redundancy / Removal Targets

- Maintained-recipe use of `rescue_retry_on_overlap`, `rescue_retry_on_missing`, `rescue_retry_on_text`, `rescue_caption_second_pass`, `rescue_refine_boxes`, `rescue_validate_crops`, and `rescue_validate_model` if the real-run proof shows they are no longer required on the bounded slice
- Any build-map or runbook language that still implies the maintained Onward recipe requires the detector+validator runtime after the bounded C4 proof

## Notes

- The fresh eval work already answered the model question. This story exists to turn that answer into less runtime complexity without hiding fidelity regressions under a cleaner-looking recipe.
- The safest validation path is reuse, not re-OCR: the reviewed Onward run root already contains fresh-enough OCR/table artifacts and Story 150 documents how to inspect the same seam after crop-stage changes.
- Because the shared reviewed run root is outside this worktree, the work log must record the absolute artifact paths actually inspected.

## Plan

1. Contract the maintained recipe first.
   - Files: `configs/recipes/recipe-onward-images-html-mvp.yaml`
   - Change: disable retry, refine, and validate flags while keeping `rescue_always`, `rescue_model`, the caption-assist pass, and `trim_layout_text`.
   - Why first: this is the smallest change that tests the build-map thesis directly.
   - Done when: the recipe expresses the single-stage maintained path explicitly.

2. Add focused drift protection for the maintained recipe.
   - Files: `tests/test_crop_runtime_recipe_contract.py`
   - Change: assert the maintained Onward crop stage keeps the simplified flag set and still preserves the remaining needed trim/detector parameters.
   - Risk addressed: a later recipe edit silently reintroducing the removed loops.
   - Done when: targeted pytest fails if the old validator/retry contract reappears.

3. Re-run only the affected real seam.
   - Files: shared run root under `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/`
   - Change: clear stale crop `*.pyc`, rerun `crop_illustrations` on the shared reviewed run root, then rerun `build_chapters` and downstream validation while reusing existing OCR/table artifacts if the driver supports that honestly.
   - Preferred command shape:
     - first resume `crop_illustrations` only while keeping downstream artifacts intact,
     - then resume `build_chapters` so final HTML/image publication refreshes from the new crop artifact,
     - avoid rerunning table rescue unless the driver/runtime proves it is necessary.
   - Done when: refreshed crop and published HTML artifacts exist and are manually inspected.

4. Sync the planning docs to the measured runtime reality.
   - Files: `docs/build-map.md`, optionally `docs/runbooks/crop-eval-workflow.md`
   - Change: if the proof passes, update Category 4 / Gap 1 wording from “remaining work is simplification” to “bounded runtime simplification landed; broader C5 breadth remains.”
   - Done when: docs describe the new maintained runtime honestly.

### Impact Analysis

- **Primary blast radius:** the maintained Onward image-directory proof recipe and the shared reviewed Onward run root used for runtime verification
- **Secondary blast radius:** crop runtime docs and any recipe-contract tests that now encode the simplified maintained path
- **Structural health note:** avoid changing `modules/extract/crop_illustrations_guided_v1/main.py` unless the real-run proof exposes a genuine residual defect; that file is already 4155 lines and not the right first simplification lever
- **Approval blocker:** none beyond the user’s explicit “go ahead”; the main operational risk is mutating the shared reviewed run root, which is acceptable here because the project already uses same-run resume flows for downstream validation and the story will record the exact commands and paths

### What Done Looks Like

- The maintained recipe stops paying the validator/retry/refine runtime tax on the bounded slice.
- A fresh real resumed run proves crop publication still works on the reviewed Onward seam.
- Manual inspection confirms no obvious regression on the checked artifact set.
- The build map stops treating this specific runtime simplification as merely pending.

## Work Log

20260403-2210 — story created and promoted directly to `Pending` because the critical substrate is implemented, not hypothetical. Verified in this pass: `docs/build-map.md` now marks C4 `converge` and explicitly calls runtime simplification the next step; `modules/extract/crop_illustrations_guided_v1/main.py` already exposes recipe-level booleans for retry, caption second pass, refine, and validation; `configs/recipes/recipe-onward-images-html-mvp.yaml` currently enables those loops on the maintained path; `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/02_ocr_ai_gpt51_v1/pages_html.jsonl` and `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/illustration_manifest.jsonl` exist; and the stamped upstream artifacts point at the real external source directory `/Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images`. Result: this is honestly buildable as a bounded recipe simplification plus shared-run validation story, not a new-architecture draft. Next step: set the story `In Progress`, contract the maintained recipe, and rerun the crop/build seam on the reviewed Onward run root with manual artifact inspection.
20260403-2222 — implementation started. Contracted the maintained crop recipe in `configs/recipes/recipe-onward-images-html-mvp.yaml` so the bounded path keeps `rescue_always` plus `trim_layout_text` but disables retry-on-overlap, retry-on-missing, retry-on-text, VLM refine, and VLM crop validation. Added `tests/test_crop_runtime_recipe_contract.py` to fail if those loops drift back into the maintained recipe or if the simplified detector contract disappears. Next step: run the targeted test, then execute the real resumed crop/build proof on the shared Onward run root and inspect the regenerated artifacts.
20260403-2338 — first runtime proof exposed an important scope correction instead of a finish line. Fresh resumed runs completed successfully from `crop_illustrations` and then `build_chapters`, but manual inspection of `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/images/page-012-001.jpg` and `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/chapter-003.html` showed a real regression: removing the caption second pass widened the seal crop to include the minister text lines while those same lines still appeared as HTML paragraphs, duplicating content in the published chapter. Decision: narrow the simplification target honestly. Keep the validator/retry/refine loops removed, but restore the bounded caption-assist pass because the reviewed Onward slice still needs it for fidelity. Next step: rerun the targeted test, rerun the crop/build seam with caption assist restored, and confirm the duplication disappears while the rest of the simplification holds.
20260403-2352 — final implementation proof completed with the narrower honest target. Fresh checks in this pass: `python -m pytest tests/test_crop_runtime_recipe_contract.py -q` (`1 passed`), `python -m ruff check tests/test_crop_runtime_recipe_contract.py` (`All checks passed!`), and `python -m pytest tests/test_crop_illustrations_guided_v1.py tests/test_build_chapter_html.py -q` (`87 passed`). Fresh real-run evidence on the reviewed shared run root:
- `scripts/run_driver_monitored.sh --recipe configs/recipes/recipe-onward-images-html-mvp.yaml --run-id onward-full-audit-20260318-r1 --output-dir /Users/cam/Documents/Projects/codex-forge/output/runs -- --instrument --allow-run-id-reuse --input-images /Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images --start-from crop_illustrations --end-at crop_illustrations --keep-downstream` completed with `crop_illustrations.wall_seconds = 376.87` and regenerated `03_crop_illustrations_guided_v1/`.
- `scripts/run_driver_monitored.sh --recipe configs/recipes/recipe-onward-images-html-mvp.yaml --run-id onward-full-audit-20260318-r1 --output-dir /Users/cam/Documents/Projects/codex-forge/output/runs -- --instrument --allow-run-id-reuse --input-images /Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images --start-from build_chapters` completed with `build_chapters.wall_seconds = 8.06`, rewrote 33 chapters, and reran genealogy validation with `flagged=0`.
Manual artifact inspection in the same pass:
- Cover/title-page case: `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/images/page-001-000.jpg` stayed full-page at `5096x6772`; `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/page-001.html` still embeds `page-001-000.jpg` under the `ONWARD / TO THE UNKNOWN` headings.
- Seal/text-bearing case: `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/images/page-012-001.jpg` settled at `3121x1386`, which is back at the pre-regression baseline width class rather than the widened `3860x1373` crop from the over-aggressive simplification attempt. Visual inspection confirmed the seal and signatures remain intact.
- Final HTML case: `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/chapter-003.html` embeds `page-012-000.jpg` and `page-012-001.jpg` while still keeping the minister lines as structured HTML paragraphs below the figure block; `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/10_validate_onward_genealogy_consistency_v1/genealogy_consistency_report.jsonl` reports `flagged_genealogy_chapters = 0`.
One more proof point on the removed loops: scanning the latest crop-run slice of `driver.log` from the last `Found 29 pages with images out of 127 total` marker produced `COUNT 0` for `Auto-retry`, `VLM refine`, `Validation:`, `Validation fallback`, and `VLM validate failed`, so the maintained lane is no longer exercising the removed validator/retry/refine path. Result: the implementation is complete and the docs now reflect the honest bounded state. Next step: `/validate`, then `/mark-story-done` if no wider concerns appear.
20260403-2359 — close-out completed after validation exposed one stale methodology source. `docs/spec.md` still described the old `Gemini 3 Pro -> Gemini 2.5 Flash validator` C4 compromise at `0.856 / 0.77`, so this pass aligned it with the current bounded maintained state: Flash-first on the maintained slice, `0.9678 / 1.0` on 2026-04-03, validator/retry/refine removed on the maintained recipe, and caption/layout assist retained as honest residue pending broader C5 proof. Fresh close-out checks in this pass: `python -m ruff check modules/ tests/` (`All checks passed!`) and `python -m pytest tests/` (`437 passed, 4 warnings in 184.25s`). No crop-specific ADR was needed after rechecking `docs/decisions/`; this remains a bounded simplification of the maintained lane rather than a new cross-cutting architecture decision. Result: Story 184 is now closed honestly with validation complete and the methodology graph aligned. Next step: `/check-in-diff`.
20260404-0036 — landing validation exposed one more honest residue on the reviewed page-12 seal case. The crop itself still contains the minister lines because there is no clean rectangular crop that keeps both signatures while excluding the printed signatory text, and the fresh build rerun therefore duplicated those same lines as adjacent HTML paragraphs. Instead of pretending the crop was clean, this pass fixed the published-output seam directly in `build_chapter_html_v1`: when a text-bearing crop's own OCR already covers the immediately following paragraphs, the builder now suppresses those duplicate paragraphs and marks the figure with `data-text-dedup-source="crop-ocr"`. Fresh evidence on the branch tip: `python -m pytest tests/test_build_chapter_html.py -q` (`87 passed`), `python -m ruff check modules/build/build_chapter_html_v1/main.py tests/test_build_chapter_html.py` (`All checks passed!`), `scripts/run_driver_monitored.sh ... --start-from build_chapters` rewrote 33 chapters on the reviewed Onward run root, `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/chapter-003.html` now keeps the `page-012-001.jpg` figure but no longer emits the duplicate `Hon. Gordon MacMurchy` / `Hon. Ed Tchorzewski` paragraphs, and `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/10_validate_onward_genealogy_consistency_v1/genealogy_consistency_report.jsonl` remains fresh with `flagged_genealogy_chapters = 0`. Result: the published artifact surface is clean again on the reviewed maintained slice. Next step: `/check-in-diff`.
