# Story 150 — Onward Full-Run Audit Reconciliation

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #3 (Extract), Requirement #4 (Illustrate), Requirement #5 (Structure), Requirement #6 (Validate), Fidelity to Source, Transparency over Magic
**Spec Refs**: spec:2.1 C1 (Multi-Stage OCR Pipeline), spec:3.1 C3 (Heuristic + AI Layout Detection), spec:5.1 C7 (Page-Scope Extraction with Document-Level Consistency Planning), spec:6
**Decision Refs**: `docs/build-map.md`, `docs/decisions/adr-001-source-aware-consistency-strategy/adr.md`, `docs/runbooks/golden-build.md`, Story 140 work log, Story 143 work log, Story 149 work log
**Depends On**: Story 149

## Goal

Reconcile the newly proven full-source Onward audit lane with the current reuse-based reviewed golden slice. Story 149 correctly blessed only a reviewed genealogy slice, but a fresh source-image run on `recipe-onward-images-html-mvp.yaml` showed that the full pipeline improves frontmatter image health (`chapter-003.html`) while regressing Arthur genealogy structure (`chapter-010.html`). This story must trace where that divergence enters, preserve the fresh-run gains, and either eliminate the `chapter-010.html` regression or tighten the trust model so the project stops confusing fast reuse checks with whole-book health.

## Acceptance Criteria

- [x] A real `driver.py` run starting from original Onward source images, not from `load_artifact_v1`, is recorded in the work log with concrete evidence from the run artifacts or recipe snapshot showing the fresh-start path. The story cites the exact run id and inspected artifact paths in `output/runs/`.
- [x] The maintained fresh-run path keeps `chapter-003.html` healthy: the reviewed frontmatter image tags have valid `src` values and no known broken-image regression survives in final HTML.
- [x] `chapter-010.html` on the fresh-run path is no longer materially worse than the current reviewed slice from `benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/`: Arthur-family fragmentation is removed or reduced to the accepted reviewed bar, and `validate_onward_genealogy_consistency_v1` no longer flags the chapter for the same `external_family_headings` failure mode.
- [x] The reviewed companion chapters `chapter-011.html`, `chapter-017.html`, `chapter-022.html`, and `chapter-023.html` are compared against the reviewed slice and their deltas are classified in the work log as `regression`, `improvement`, `semantic no-op`, or `accepted structural churn`; no unexplained drift remains in the reviewed set.
- [x] The build map, golden/runbook guidance, and any maintained recipe or registry surfaces clearly distinguish the fast reuse regression lane from the full source-image audit lane unless this story fully reunifies them under one trustworthy maintained path.

## Out of Scope

- Blessing the entire Onward book as a 100% cell-verified canonical golden
- Reopening unrelated historical Onward issues outside the fresh-run vs reuse-run divergence surfaced by `chapter-003.html` and `chapter-010.html`
- Generalizing this audit discipline to every converter family in the repo
- Running promptfoo benchmark work unless the chosen fix actually changes benchmark fixtures or eval scoring
- Deleting the fast reuse regression lane; it remains valuable unless the story proves one maintained path can cover both speed and full-run truth

## Approach Evaluation

- **Simplification baseline**: First prove exactly where the fresh-run path diverges from the reviewed reuse slice by tracing `chapter-003.html` and `chapter-010.html` upstream through the staged artifacts. If a bounded reread or chapter-local rebuild already closes the gap, prefer that over broader architectural change.
- **AI-only**: Re-run Arthur pages with a stronger source-aware reread and accept whatever the full pipeline emits. This could fix `chapter-010.html`, but it does not by itself explain why the reuse path preserved better structure or why frontmatter image health drifted.
- **Hybrid**: Trace the stage boundary where fresh and reused artifacts diverge, keep the fresh source-image lane as the whole-book audit truth, and use targeted reruns / deterministic normalization only where the evidence shows they still improve fidelity. This is the leading candidate because it can preserve `chapter-003.html` while repairing `chapter-010.html` without pretending the trust split does not exist.
- **Pure code**: Patch build output or doc language without tracing the upstream divergence. This is the cheapest approach, but it risks fixing the symptom while leaving the full-run path unreliable and the trust surfaces misleading.
- **Repo constraints / prior decisions**: `docs/build-map.md` already says the full canonical Onward output is still `climb` while the reviewed genealogy slice is only `hold`. Story 149 intentionally blessed `onward_genealogy_reviewed_html_slice` as `known_good` and left generic `html` as `partial`. ADR-001 keeps direct HTML with explicit consistency artifacts as the default strategy; `docs/runbooks/golden-build.md` already distinguishes run-backed golden slices from whole-run goldens.
- **Existing patterns to reuse**: `configs/recipes/recipe-onward-images-html-mvp.yaml`, `configs/recipes/onward-genealogy-build-regression.yaml`, `modules/adapter/table_rescue_onward_tables_v1`, `modules/adapter/rerun_onward_genealogy_consistency_v1`, `modules/build/build_chapter_html_v1`, `modules/common/onward_genealogy_html.py`, `validate_onward_genealogy_consistency_v1`, and Story 140 / 143 / 149 run evidence.
- **Eval**: The deciding evidence is a fresh source-image run plus staged-artifact diff tracing on `chapter-003.html`, `chapter-010.html`, `chapter-011.html`, `chapter-017.html`, `chapter-022.html`, and `chapter-023.html`, backed by `validate_onward_genealogy_consistency_v1` and manual final-HTML inspection. If the story changes promptfoo fixtures or eval surfaces, run `/improve-eval` and update `docs/evals/registry.yaml`; otherwise document why no eval registry change was needed.

## Tasks

- [x] Reconfirm and document the fresh audit baseline:
  - verify the March 18 audit run started from original images and not `load_artifact_v1`
  - record the exact artifact evidence proving the fresh-start path
  - note why Story 149's reviewed slice remains valid but not whole-book-blessed
- [x] Trace the divergence stage-by-stage for the reviewed audit set:
  - `chapter-003.html` broken-vs-healthy image behavior
  - `chapter-010.html` Arthur fragmentation regression
  - structural drift on `chapter-011.html`, `chapter-017.html`, `chapter-022.html`, and `chapter-023.html`
- [x] Implement the smallest coherent fix that preserves the fresh-run gains while closing the Arthur regression:
  - recipe wiring
  - source-aware rerun targeting
  - deterministic genealogy normalization ownership
  - chapter-build assembly
  - or another evidence-backed seam discovered during tracing
- [x] Update focused tests and/or validator coverage at the seam that actually owns the divergence so the same full-run regression cannot quietly re-enter.
- [x] Run a real fresh source-image `driver.py` validation path, verify artifacts in `output/runs/`, and manually inspect the final HTML for `chapter-003.html`, `chapter-010.html`, `chapter-011.html`, `chapter-017.html`, `chapter-022.html`, and `chapter-023.html`.
- [x] If the trust model or maintained validation paths change, update the runbook/build-map/run-registry-facing docs so they explicitly distinguish:
  - fast scoped reuse regression
  - full source-image audit truth
  - any newly blessed broader Onward baseline
- [x] Check whether the chosen implementation makes any existing code, helper paths, recipes, or docs redundant; remove them or create a concrete follow-up.
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect the target HTML / JSONL data
  - [x] If agent tooling changed: not expected; run `make skills-check` only if tooling changes
- [x] If evals or goldens changed materially: run `/improve-eval` and update `docs/evals/registry.yaml` only if promptfoo fixtures or benchmark scoring actually changed; otherwise document why no eval update was needed
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: the reconciliation shows exactly which stage/artifact introduced the divergence
  - [x] T1 — AI-First: prefer targeted rereads or stronger source-aware extraction before deepening deterministic workaround code
  - [x] T2 — Eval Before Build: measure the fresh-run and reuse-run delta before editing the seam
  - [x] T3 — Fidelity: preserve frontmatter image correctness and reviewed genealogy structure together
  - [x] T4 — Modular: keep fast-lane and audit-lane responsibilities explicit instead of hiding trust in ad hoc notes
  - [x] T5 — Inspect Artifacts: manually inspect the affected HTML, not just validator output

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: The likely ownership is the Onward source-image HTML path and its late genealogy seam: `recipe-onward-images-html-mvp.yaml`, `table_rescue_onward_tables_v1`, `rerun_onward_genealogy_consistency_v1`, `build_chapter_html_v1`, and `modules/common/onward_genealogy_html.py`, plus the trust-surface docs that describe how fresh audit runs differ from reuse-based regression runs.
- **Data contracts / schemas**: No schema change is expected unless the story decides to emit a new audit/diff sidecar or richer trust metadata. If any new fields cross artifact boundaries, add them to `schemas.py` before relying on stamped outputs.
- **File sizes**: Several likely owner files are already oversized and should not absorb diffuse new logic casually: `table_rescue_onward_tables_v1/main.py` (1467), `rerun_onward_genealogy_consistency_v1/main.py` (1663), `build_chapter_html_v1/main.py` (1344), `tests/test_table_rescue_onward_tables_v1.py` (518), `tests/test_rerun_onward_genealogy_consistency_v1.py` (1098), `tests/test_build_chapter_html.py` (1294). Prefer helper extraction, recipe/doc changes, or narrowly owned edits. `modules/common/onward_genealogy_html.py` is 489 lines and already near the soft limit.
- **Decision context**: Reviewed `docs/ideal.md`, `docs/spec.md`, `docs/build-map.md`, `docs/runbooks/golden-build.md`, ADR-001, and the work logs for Stories 140, 143, and 149. No other ADR was found that changes the recommended direction.

## Files to Modify

- `/Users/cam/.codex/worktrees/b0de/codex-forge/configs/recipes/recipe-onward-images-html-mvp.yaml` — keep or narrow the maintained fresh full-run audit path (192 lines)
- `/Users/cam/.codex/worktrees/b0de/codex-forge/configs/recipes/onward-genealogy-build-regression.yaml` — clarify or adjust the fast reuse regression lane if the trust split changes (60 lines)
- `/Users/cam/.codex/worktrees/b0de/codex-forge/modules/adapter/table_rescue_onward_tables_v1/main.py` — likely Arthur-fragmentation owner candidate during fresh-run tracing (1467 lines)
- `/Users/cam/.codex/worktrees/b0de/codex-forge/modules/adapter/rerun_onward_genealogy_consistency_v1/main.py` — likely source-aware rerun owner if the fix belongs in selective re-read policy (1663 lines)
- `/Users/cam/.codex/worktrees/b0de/codex-forge/modules/build/build_chapter_html_v1/main.py` — chapter assembly may still be where fresh vs reuse divergence becomes visible (1344 lines)
- `/Users/cam/.codex/worktrees/b0de/codex-forge/modules/common/onward_genealogy_html.py` — shared genealogy normalization/stitching helper if the retained logic needs to shift (489 lines)
- `/Users/cam/.codex/worktrees/b0de/codex-forge/tests/test_table_rescue_onward_tables_v1.py` — focused regression coverage if rescue logic changes (518 lines)
- `/Users/cam/.codex/worktrees/b0de/codex-forge/tests/test_rerun_onward_genealogy_consistency_v1.py` — targeted rerun coverage if rerun policy changes (1098 lines)
- `/Users/cam/.codex/worktrees/b0de/codex-forge/tests/test_build_chapter_html.py` — final assembly regression coverage for the reviewed chapters (1294 lines)
- `/Users/cam/.codex/worktrees/b0de/codex-forge/docs/build-map.md` — keep the Onward trust model honest if the full-run audit lane or blessing state changes (457 lines)
- `/Users/cam/.codex/worktrees/b0de/codex-forge/docs/runbooks/golden-build.md` — document how full-run audit baselines interact with scoped reviewed slices (80 lines)
- `/Users/cam/.codex/worktrees/b0de/codex-forge/docs/stories/story-150-onward-full-run-audit-reconciliation.md` — work log, plan, and closure evidence (this file)

## Redundancy / Removal Targets

- Any doc language that implies a reviewed reuse-based slice is equivalent to a whole-book Onward golden
- Any temporary audit recipe or one-off comparison notes that duplicate an established maintained audit lane
- Any duplicate late-stage genealogy repair responsibility that only exists because the fresh-run and reuse-run paths are drifting differently

## Notes

- The March 18 audit run `onward-full-audit-20260318-r1` was a true source-image run from `recipe-onward-images-html-mvp.yaml`. Its initial pass fixed `chapter-003.html` frontmatter images but regressed `chapter-010.html`; the maintained reruns in this story repaired that same run so the full audit lane now keeps `chapter-003.html` healthy and clears `chapter-010.html` with `flagged_genealogy_chapters: 0`.
- Compared with the Story 149 reviewed slice, the final fresh-audit outputs classify as: `chapter-011.html` and `chapter-017.html` semantic no-op / accepted formatting churn, `chapter-022.html` and `chapter-023.html` accepted structural churn (`<table>` genealogy + `<dl>` totals), and `chapter-010.html` no longer materially worse than the reviewed slice.
- Success does not require blessing the whole book. It does require making the audit lane trustworthy and making the trust boundary explicit.

## Plan

### Task 1 — Reproduce and localize the Arthur regression

- Files: story work log, fresh audit artifacts, regression artifacts
- Change:
  - Compare `onward-full-audit-20260318-r1` against the Story 149 reviewed slice at page and chapter level.
  - Identify the first stage where `chapter-010.html` diverges materially.
  - Confirm whether the failure comes from stale recipe wiring, stale rescue scoring, or build-stage inability to recover.
- Impact / risk:
  - No code change yet. The risk is misattributing the owner and fixing the wrong seam.
- Done when:
  - The work log names the first failing stage, the exact page(s), and the exact acceptance decision that let the bad shape through.

### Task 2 — Test the smallest coherent repair at the stale rescue seam

- Files: `/Users/cam/.codex/worktrees/b0de/codex-forge/modules/adapter/table_rescue_onward_tables_v1/main.py`, focused tests
- Change:
  - Update rescue scoring and/or acceptance logic so genealogy candidates that explode one coherent page into many header tables with external family headings stop counting as improvements.
  - Reuse the validator/rerun notion of drift where possible instead of inventing another quality proxy.
  - Prefer keeping the cleaner existing page HTML when the candidate only wins on header-table count.
- Impact / risk:
  - Smallest blast radius and likely enough to stop the Arthur regression before build.
  - Risk: some pages currently helped by the old rescue score may stop being rescued; tests and a fresh run must confirm net improvement.
- Done when:
  - The fresh full run no longer accepts the bad page-35 explosion and `chapter-010.html` materially improves.

### Task 3 — Escalate to full-audit rerun wiring only if the smaller seam is insufficient

- Files: `/Users/cam/.codex/worktrees/b0de/codex-forge/configs/recipes/recipe-onward-images-html-mvp.yaml`, maybe rerun/build docs/tests
- Change:
  - If fixing stale rescue acceptance alone does not recover the reviewed Arthur shape, extend the fresh source-image audit lane to include the later `rerun_onward_genealogy_consistency_v1` seam plus rebuild/revalidate, using Story 143 as the pattern.
  - Keep the fast reuse regression lane separate unless the full lane is proven stable enough to replace it.
- Impact / risk:
  - Larger blast radius, but it aligns the full-run audit lane with the seam that actually repaired Arthur historically.
  - Risk: recipe complexity grows and full-run cost/latency increase.
- Done when:
  - The full audit lane preserves `chapter-003.html` image health and clears the Arthur regression without reopening reviewed chapters.

### Task 4 — Verify end to end and update trust surfaces

- Files: touched tests plus `/Users/cam/.codex/worktrees/b0de/codex-forge/docs/build-map.md`, `/Users/cam/.codex/worktrees/b0de/codex-forge/docs/runbooks/golden-build.md`, story work log
- Change:
  - Run focused tests, then a real fresh source-image `driver.py` run.
  - Inspect final HTML for `chapter-003.html`, `chapter-010.html`, `chapter-011.html`, `chapter-017.html`, `chapter-022.html`, and `chapter-023.html`.
  - Update docs only if the fix changes how the fast lane and audit lane should be understood.
- Impact / risk:
  - Ensures we do not claim more trust than the repaired lane actually deserves.
- Done when:
  - Tests are green, artifacts are inspected, and the work log records the final trust conclusion.

## Work Log

20260318-1649 — story created: captured the newly proven split between the fresh source-image audit lane (`onward-full-audit-20260318-r1`) and the reviewed reuse-based golden slice from Story 149. The story is intentionally build-ready (`Pending`): it requires tracing where `chapter-003.html` image health improves while `chapter-010.html` regresses, then reconciling or explicitly codifying that trust boundary with real `driver.py` evidence
20260318-1657 — Arthur upstream trace: located the first material regression for `chapter-010.html` in the fresh full run at `06_table_rescue_onward_tables_v1` on source page `35` (`Image034.jpg`). Evidence chain: in `02_ocr_ai_gpt51_v1/pages_html.jsonl` and `04_table_rescue_html_loop_v1/pages_html_rescued.jsonl`, page `35` still has `2` tables with inline family rows (`RICHARD'S FAMILY`, `PAUL'S FAMILY`, `VIVIAN'S FAMILY`) inside the table; `06_table_rescue_onward_tables_v1/pages_html_onward_tables.jsonl` rewrites that same page into `14` tables with external family headings, and `08_table_fix_continuations_v1` preserves the same shape unchanged. The stage report at `output/runs/onward-full-audit-20260318-r1/table_rescue_onward_tables_v1/table_rescue_onward_report.jsonl` shows why: page `35` was explicitly targeted by the stale full recipe (`pages_list: 24,25,35,89,97,98`), the `gpt-4.1` rescue candidate was accepted with `decision_reason="candidate_score_improved"`, and the scoring considered the exploded shape "better" because `header_table_count` rose from `1` to `13` and `inline_family_heading_count` fell from `12` to `0` (`score 310 -> 2330`). That is the wrong proxy for the modern quality bar because the validator now treats those external headings as drift. Story 143 confirms the same bad page-level artifact was historically repaired later, not earlier: its rerun report shows page `35` entered `rerun_onward_genealogy_consistency_v1` with the same `14`-table / `13` external-heading shape and was accepted only after the rerun stage reduced drift (`decision_reason="candidate_drift_reduced"`) to `4` tables with `12` subgroup rows. Conclusion: the fresh full recipe is failing because it still stops on the older table-rescue seam and never invokes the later source-aware rerun path that Story 143/149 rely on. The first concrete fix target is therefore the stale full-run recipe/stage boundary around `table_rescue_onward_tables_v1`, not `build_chapter_html_v1`
20260318-1721 — targeted repair landed and validated: fixed the Arthur regression in two places. First, `modules/adapter/table_rescue_onward_tables_v1/main.py` now rejects rescue candidates that worsen `external_family_heading_count`, worsen BOY/GIRL drift, or only "improve" by increasing fragmentation without new subgroup structure, using `analyze_page_row()` to align acceptance with the validator's actual drift signals. Re-running `python driver.py --recipe configs/recipes/recipe-onward-images-html-mvp.yaml --run-id onward-full-audit-20260318-r1 --allow-run-id-reuse --output-dir /Users/cam/Documents/Projects/codex-forge/output/runs --start-from onward_table_rescue --instrument` proved the page-35 candidate was no longer accepted and restored Arthur page artifacts to `2` tables with no external family headings. Second, `modules/common/onward_genealogy_html.py` now uses the chapter-safe rescue normalizer and drops repeated genealogy schema rows from table bodies once a canonical header already exists, which removed the surviving mid-table `NAME/BORN/MARRIED/SPOUSE/BOY/GIRL/DIED` row inside Arthur's `ROGER'S FAMILY` section. Coverage: `python -m pytest tests/test_onward_targeted_table_rescue.py -q` (`10 passed`), `python -m pytest tests/test_build_chapter_html.py -q` (`79 passed`), `python -m pytest tests/test_validate_onward_genealogy_consistency_v1.py -q` (`4 passed`), `make lint` (clean), and `make test` (`623 passed, 6 skipped`).
20260318-1721 — fresh audit lane revalidated from the changed seam: `python driver.py --recipe configs/recipes/recipe-onward-images-html-mvp.yaml --run-id onward-full-audit-20260318-r1 --allow-run-id-reuse --output-dir /Users/cam/Documents/Projects/codex-forge/output/runs --start-from build_chapters --instrument` rebuilt the final HTML and cleared the validator (`output/runs/onward-full-audit-20260318-r1/10_validate_onward_genealogy_consistency_v1/genealogy_consistency_report.jsonl` now reports `flagged_genealogy_chapters: 0`, `flagged_chapters: []`, `strong_rerun_candidate_page_count: 0`). Manual inspection confirmed `output/runs/onward-full-audit-20260318-r1/output/html/chapter-003.html` keeps both frontmatter images with valid `src`, `output/runs/onward-full-audit-20260318-r1/output/html/chapter-010.html` is back to `2` tables / `0` external headings / `107` subgroup rows with `Richard | , 1951 | ... | , 1956` preserved in `DIED` and intact `RICHARD'S FAMILY` / `PAUL'S FAMILY` / `VIVIAN'S FAMILY` subgroup rows, and the reviewed companion chapters classify as `chapter-011.html` semantic no-op / formatting churn, `chapter-017.html` semantic no-op / formatting churn, `chapter-022.html` accepted structural churn (`<dl>` totals), and `chapter-023.html` accepted structural churn (`<dl>` totals). No build-map or runbook updates were required because the fast reuse lane vs fresh audit lane trust split was already documented correctly; this story repaired the audit lane without collapsing that distinction.
20260318-1750 — chapter-003 seal crop follow-up fixed: manual review caught that the published seal image in `output/runs/onward-full-audit-20260318-r1/output/html/chapter-003.html` was still clipped even though the crop stage had already been repaired. Root cause was two-part. First, `modules/extract/crop_illustrations_guided_v1/main.py` was trimming whole crops against partial-width caption boxes; for `page-012-001.jpg` that turned the published asset into a `3121x550` crop that cut the seal in half. Second, `modules/build/build_chapter_html_v1/main.py` only copied illustration assets when the destination did not already exist, so resume rebuilds left stale `output/html/images/page-012-001.jpg` in place after the crop-stage fix. The repair now preserves full-height crops when the caption overlaps only part of the image width and always refreshes published illustration assets during chapter rebuilds. Coverage: `python -m pytest tests/test_crop_illustrations_guided_v1.py -q` (`2 passed`) and `python -m pytest tests/test_build_chapter_html.py -q` (`80 passed`). Re-running `python driver.py --recipe configs/recipes/recipe-onward-images-html-mvp.yaml --run-id onward-full-audit-20260318-r1 --allow-run-id-reuse --output-dir /Users/cam/Documents/Projects/codex-forge/output/runs --start-from build_chapters --instrument` refreshed the final asset so both the crop-stage file and `output/html/images/page-012-001.jpg` are now `3121x1379`. Manual inspection confirmed chapter 003 preserves the full seal, and chapter 010 stayed healthy at `2` tables / `0` external headings with the validator still reporting `flagged=0`.
20260318-1750 — final repo checks after the seal-publish fix: reran `make lint` (`ruff check modules/ tests/` clean), reran `make test` (`626 passed, 6 skipped`), and confirmed `git diff --check` is clean. This closes the verification gap introduced by landing the image-publish overwrite fix after the earlier Arthur validation pass.
20260318-1802 — `/validate` and `/mark-story-done` closeout: final validation found no blocking defects in the shipped slice. Closure-only follow-up applied here: Story 150 status set to `Done`, workflow gates marked complete, `docs/stories.md` updated to `Done`, and `CHANGELOG.md` updated with the shipped summary. No additional code or artifact changes were required beyond the already-validated patch set.
