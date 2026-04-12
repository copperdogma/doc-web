---
title: "Probe Receipt-Only Image-Entry Rescue on LOC Asset 367466"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #3 (Extract), Requirement #6 (Validate), Any format, any condition, Fidelity to the source, Traceability is the product"
spec_refs:
  - "spec:2"
  - "spec:2.1"
  - "spec:2.2"
  - "spec:8"
adr_refs: []
depends_on:
  - "216"
category_refs:
  - "spec:2"
  - "spec:8"
compromise_refs:
  - "C1"
  - "B1"
input_coverage_refs:
  - "handwritten-notes"
architecture_domains:
  - "ocr_and_extraction"
roadmap_tags:
  - "campaign:maintained-intake-honesty"
legacy_system: ""
---

# Story 217 — Probe Receipt-Only Image-Entry Rescue on LOC Asset 367466

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/scout/scout-014-degraded-handwriting-eval-sources.md`, `docs/stories/story-191-finish-real-handwritten-ocr-on-the-loc-fixture-pair.md`, `docs/stories/story-208-glm-ocr-benchmark-for-handwritten-and-table-heavy-seams.md`, `docs/stories/story-214-loc-george-washington-papers-benchmark-slice.md`, `docs/stories/story-215-washington-database-english-longhand-benchmark-slice.md`, `docs/stories/story-216-refresh-loc-gw-benchmark-proof-and-stronger-model-screen.md`, `scripts/spikes/loc_gw_benchmark.py`, and `None found after search in docs/decisions/`, `docs/runbooks/`, and `docs/notes/` for a narrower handwritten receipt-probe ADR/runbook beyond the recent handwriting story chain
**Depends On**: Story `216`

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

Story 216 closed the fixed LOC proof-refresh and bounded stronger-model screen
honestly on April 12, 2026: the maintained image-entry receipt sentinel on
asset `367466` still produced empty HTML, while the bounded `gpt-5.4`
challenger changed that one page from empty to non-empty but still weak text
and regressed the other two LOC assets. This story should isolate that single
receipt-only failure class, measure whether close prompt/entry variants can
turn the non-empty result into materially faithful receipt text on the same
source-native image surface, and end with one explicit decision: close the
seam negative, or name the exact next repo-owned verification move without
pretending the full LOC handwritten blocker is reopened.

## Acceptance Criteria

- [x] A fresh current-pass receipt-only baseline exists before any new variant claim:
  - [x] rerun the maintained image-entry receipt case for LOC asset `367466` on the same source-native image surface and reproduce the Story 216 empty-output sentinel
  - [x] rerun the bounded Story 216 `gpt-5.4` receipt case on the same asset and reproduce a non-empty comparison artifact
  - [x] manual inspection cites the exact `page_html_v1` artifact paths used for both the empty baseline and the best non-empty challenger
- [x] One bounded receipt-only candidate set is frozen and measured honestly:
  - [x] candidate scope stays receipt-only and image-entry only; no broader three-asset rerun or new source hunt occurs unless the first probe fails for a non-quality operational reason
  - [x] every candidate records exact OCR params, run ids, artifact paths, `overall_ratio`, `page_min_ratio`, and dominant failure mode against the same transcript
  - [x] helper-local code was not needed; the bounded matrix stayed manual/story-local and comparison-only
- [x] The story ends with one explicit decision instead of a vague handwriting claim:
  - [x] no candidate materially beat the Story 216 receipt result (`overall_ratio = 0.16971`), and manual inspection still showed semantically wrong receipt text, so the seam closes negative and Story 191 stays blocked
  - [x] no candidate materially improved receipt fidelity enough to justify naming a second repo-owned verification move
  - [x] `docs/evals/registry.yaml` and `tests/fixtures/formats/_coverage-matrix.json` stayed unchanged because durable tracked truth did not change

## Out of Scope

- Reopening Story 191 or changing the maintained handwritten rescue recipes in the same story
- Broadening back to the full three-asset LOC slice unless a receipt-only probe fails for a non-quality operational reason
- Washington Database access work, DiEm follow-up work, or any new source hunt
- PDF-entry receipt probes unless image-entry wins and `/build-story` explicitly expands scope
- Manual transcript edits or deterministic receipt parsing that hide OCR failures
- Any `doc-web` / Dossier runtime-boundary work

## Approach Evaluation

- **Simplification baseline**: Story 216 already showed that one direct image-entry `gpt-5.4` call changes asset `367466` from empty to non-empty on April 12, 2026. The first task is therefore to reproduce the unchanged maintained baseline and that exact challenger before adding helper glue or new variants.
- **AI-only**: plausible. The current gap is one page and one failure class, and a direct subject-model change already moved the result materially. Prompt/entry variants around a direct multimodal OCR call may be enough, and the cost surface stays bounded because the benchmark is a single receipt image.
- **Hybrid**: likely best. Use a story-local helper to freeze the source image, OCR params, and comparison summaries while AI performs the transcription. Code should only orchestrate variants, retries, and evidence packaging.
- **Pure code**: only appropriate for harnessing and comparison packaging. It cannot honestly recover the receipt text without AI.
- **Repo constraints / prior decisions**: Story 191 remains blocked on the full LOC handwritten pair; Story 208 already closed one broader stronger-model benchmark line negative; Story 214 fixed the public LOC source/harness seam; Story 215 remains explicitly blocked on Washington access; and Story 216 proved that `gpt-5.4` only improves the receipt sentinel while regressing the other two LOC assets. The `handwritten-notes-transcription` eval line still says retry only when a materially stronger subject-model or OCR substrate exists, so this story must stay narrow and comparison-only rather than pretending the broader retry gate is reopened. No narrower ADR or runbook currently governs this receipt-only seam.
- **Existing patterns to reuse**: `scripts/spikes/loc_gw_benchmark.py`, `tests/test_loc_gw_benchmark.py`, `benchmarks/scripts/run_handwritten_notes_eval.py`, `benchmarks/scorers/handwritten_notes_transcription.py`, `modules/extract/ocr_ai_gpt51_v1/main.py`, and the shared-root Story 216 artifacts under `/Users/cam/Documents/Projects/doc-web/output/runs/story216-loc-gw-proof-refresh-r1/`.
- **Eval**: the decisive comparison is on one asset. The maintained receipt baseline `367466` stays empty (`overall_ratio = 0.0`, `ocr_empty_reason = "Empty HTML output for page 1"`), while Story 216's bounded `gpt-5.4` receipt challenger is non-empty but still weak (`overall_ratio = 0.16971`). A winning receipt-only probe must materially exceed that score and, on manual artifact inspection, recover the visible receipt faithfully enough to justify a second repo-owned verification move. If it only produces non-empty but semantically wrong text, the story closes negative.

## Tasks

- [x] Reproduce the current receipt-only baseline and Story 216 `gpt-5.4` comparison on LOC asset `367466` before adding new variants:
  - [x] rerun the maintained image-entry receipt case and confirm the empty-output sentinel persists
  - [x] rerun the bounded `gpt-5.4` receipt case and confirm the current non-empty comparison artifact
  - [x] record exact artifact paths and baseline/challenger scores in the work log
- [x] Freeze the receipt-only candidate set and stop rule before changing code:
  - [x] limit the surface to receipt-only, image-entry variants around the existing `gpt-5.4` path
  - [x] do not widen to the full three-asset LOC slice, Washington, or DiEm unless the first probe fails for a non-quality operational reason
  - [x] stop and close negative because the best candidate did not materially beat `0.16971` and still read as semantically wrong on manual inspection
- [x] Implement the smallest story-local probe support only if the frozen candidate set needs it:
  - [x] the frozen matrix was small enough to stay manual/story-local, so no helper file was added
  - [x] output summaries, candidate metadata, and stop-rule evidence were captured in `output/runs/story217-loc-gw-receipts-367466-probe-summary.json`
  - [x] `scripts/spikes/loc_gw_benchmark.py` and `modules/extract/ocr_ai_gpt51_v1/main.py` stayed untouched
- [x] Run the bounded receipt-only screen, manually inspect artifacts, and publish one explicit decision: close negative and keep Story 191 blocked
- [x] No documented format coverage or graduation reality changed; left `tests/fixtures/formats/_coverage-matrix.json`, `docs/evals/registry.yaml`, and methodology state untouched
- [x] No new helper code or docs redundancy was introduced; nothing beyond this story record required removal in this pass
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] Reran the exact receipt-only probe commands, verified artifacts in `output/runs/`, and manually inspected the resulting JSON/JSONL data against the source image
  - [x] Agent tooling was unchanged, so `make skills-check` was not needed
- [x] Evals and goldens were unchanged, so `/improve-eval` was not needed
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every claim cites asset `367466`, exact run ids, model params, and inspected artifact paths
  - [x] T1 — AI-First: no deterministic parsing was added; the story only exercised bounded AI OCR variants
  - [x] T2 — Eval Before Build: the unchanged baseline and Story 216 candidate were reproduced before any new variant ran
  - [x] T3 — Fidelity: the probe judged fidelity honestly against the source image/transcript and did not promote low-fidelity text as success
  - [x] T4 — Modular: the work stayed a receipt-only story-local seam, not a silent expansion of the maintained handwritten runtime
  - [x] T5 — Inspect Artifacts: the receipt outputs were opened and checked against the source image, not just scored

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Blocker Summary

N/A

## Blocker Evidence

N/A

## Unblock Condition

N/A

## Architectural Fit

- **Owning module / area**: story-local external benchmark/probe harnessing around `scripts/spikes/loc_gw_benchmark.py` and the existing manifest-driven OCR entry path. This story should not mutate the maintained handwritten recipe by default.
- **Methodology reality**: this work belongs to `spec:2` and `spec:8`. In `docs/methodology/state.yaml`, both category substrates exist, `C1` remains in `climb`, `B1` remains in `hold`, and the relevant coverage row is `handwritten-notes`, which still sits at `has-fixture` because the maintained rescue seam fails the real LOC fixtures.
- **Substrate evidence**: verified in the current pass that `scripts/spikes/loc_gw_benchmark.py` already materializes the fixed LOC slice, supports `--candidate-model` and `--candidate-retry-model`, and records `receipt_sentinel_cleared` in the candidate summary; `tests/test_loc_gw_benchmark.py` already covers dataset parsing, helper defaults, and failure-mode classification; and `modules/extract/ocr_ai_gpt51_v1/main.py` exposes `--model`, `--retry-model`, `--ocr-hints`, and `--max-output-tokens` on the same manifest-driven image-entry path Story 216 used. Fresh shared-root artifacts also already prove the exact seam this story owns: the maintained receipt baseline is empty at `/Users/cam/Documents/Projects/doc-web/output/runs/handwritten-loc-gw-receipts-367466-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl`, while Story 216's bounded `gpt-5.4` receipt challenger is non-empty at `/Users/cam/Documents/Projects/doc-web/output/runs/story216-loc-gw-receipts-367466-image-gpt-5-4/01_ocr_ai_gpt51_v1/pages_html.jsonl`. Missing substrate is narrower: there is no receipt-only helper or prompt-variant matrix yet. That means the story is honestly `Pending`, not `Draft` or `Blocked`.
- **Data contracts / schemas**: prefer story-local JSON summaries plus existing `page_html_v1` artifacts. No shared schema change is expected. If any new fields need to cross artifact boundaries, they must be added to `schemas.py` explicitly first.
- **File sizes**: `scripts/spikes/loc_gw_benchmark.py` is `959` lines, `tests/test_loc_gw_benchmark.py` is `176`, `modules/extract/ocr_ai_gpt51_v1/main.py` is `758`, `benchmarks/scripts/run_handwritten_notes_eval.py` is `330`, `benchmarks/scorers/handwritten_notes_transcription.py` is `119`, `docs/evals/registry.yaml` is `2084`, `tests/fixtures/formats/_coverage-matrix.json` is `564`, and Story 216 is `467`. Keep edits especially surgical in `scripts/spikes/loc_gw_benchmark.py`, `modules/extract/ocr_ai_gpt51_v1/main.py`, `docs/evals/registry.yaml`, and the coverage matrix because those files are already large.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, Stories 191/208/214/215/216, Scout 014, `scripts/spikes/loc_gw_benchmark.py`, `tests/test_loc_gw_benchmark.py`, and `modules/extract/ocr_ai_gpt51_v1/main.py`. Search across `docs/decisions/`, `docs/runbooks/`, and `docs/notes/` found no narrower ADR or runbook for this receipt-only follow-on seam. ADR-002 and ADR-003 remain out of scope because this is comparison-only OCR evidence, not runtime-boundary work.

## Files to Modify

- `docs/stories/story-217-loc-gw-receipt-only-image-entry-rescue-probe.md` — keep the story record, plan, and close-out truth current
- `scripts/spikes/loc_gw_receipt_probe.py` — optional tiny sibling helper if the frozen receipt-only matrix becomes awkward to run or summarize by hand
- `tests/test_loc_gw_receipt_probe.py` — focused regression coverage if the optional receipt-only helper is added
- `scripts/spikes/loc_gw_benchmark.py` — receipt-only candidate orchestration or summary changes if helper-local support is needed (`959` lines)
- `tests/test_loc_gw_benchmark.py` — focused regression coverage if the helper changes (`176` lines)
- `modules/extract/ocr_ai_gpt51_v1/main.py` — only if `/build-story` proves a tiny CLI or prompt hook is unavoidable (`758` lines)
- `benchmarks/scripts/run_handwritten_notes_eval.py` — only if a tiny reusable receipt-only hook is cleaner than story-local duplication (`330` lines)
- `docs/evals/registry.yaml` — only if durable tracked truth changes (`2084` lines)
- `tests/fixtures/formats/_coverage-matrix.json` — only if the documented handwritten reality changes (`564` lines)

## Redundancy / Removal Targets

- Any vague receipt-only follow-on note left behind in Story 216 once this story becomes the owning seam
- Ad hoc one-off receipt prompt command notes if the helper gains bounded, tested receipt-only support
- Avoid pushing comparison-only receipt logic into the maintained handwritten recipes unless a later story earns that ownership

## Notes

- New story justification: Story 216 closed the fixed-slice proof refresh and one-candidate screen with fresh April 12, 2026 evidence. This follow-up has a narrower validation boundary: one asset, one failure class, one next decision. Reopening Story 216 would blur finished proof-refresh work with a new receipt-only experiment, and reopening Story 191 would overclaim that the full LOC pair is actionable again.
- Image-entry remains canonical. PDF stress is intentionally out of scope unless `/build-story` finds a strong reason to widen the seam.
- Even a positive receipt-only result does not move durable truth by itself; it only earns the next repo-owned verification move.

## Plan

1. Lock the current-pass receipt control and unchanged challenger before any new variants.
   Files: this story file only in planning; no code change is warranted yet.
   Change: treat the current-pass worktree-local baseline artifact at `output/runs/handwritten-loc-gw-receipts-367466-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl` and the unchanged direct challenger at `output/runs/story217-loc-gw-receipts-367466-image-gpt-5-4/01_ocr_ai_gpt51_v1/pages_html.jsonl` as the planning floor. Fresh measurements in this pass: maintained baseline is still `overall_ratio = 0.0` / `page_min_ratio = 0.0` with `dominant_failure_mode = empty_html`; unchanged `gpt-5.4` is non-empty but only `overall_ratio = 0.133043` / `page_min_ratio = 0.133043` with `dominant_failure_mode = non_empty_wrong_text`, which is worse than Story 216's shared-root `0.16971`.
   Impact/risk: direct `driver.py` runs from this worktree resolve to the worktree-local `output/` tree, not the shared project output root that Story 216 used. That is acceptable for the current-pass probe, but the story must cite those exact fresh artifact paths explicitly instead of implying that shared-root artifacts were regenerated.
   Done when the work log freezes the fresh baseline/challenger evidence and no later decision cites older artifacts as if they were the current pass.

2. Freeze the receipt-only candidate matrix and stop rule before any helper expansion.
   Files: this story file first; code stays untouched unless the matrix proves too awkward to execute consistently.
   Candidate list:
   - control: unchanged Story 216 path (`gpt-5.4`, `retry_model = gpt-5.2`, current handwritten-recipe hints, `max_long_side = 2048`, image-entry only)
   - entry variant: same prompt path but disable downsampling so the receipt runs at source resolution
   - prompt variant: same entry path but replace the generic handwritten-prose hints with receipt-specific structure hints that emphasize literal line order, payer/payee names, amounts, ditto marks, and totals without inventing substitutions
   - combined variant: receipt-specific hints plus source-resolution image entry
   Explicit exclusions: no full three-asset LOC rerun, no PDF-entry stress, no new source hunt, and no new subject-model family (`gpt-5.4-pro`, Gemini 3.x, GLM-OCR, etc.) in this story.
   Stop rule: after the frozen three new variants above, stop immediately and close negative unless at least one variant materially beats both the historical Story 216 receipt score (`0.16971`) and the current-pass unchanged rerun (`0.133043`) and manual artifact inspection shows materially more faithful receipt wording/numerics rather than merely non-empty text.
   Impact/risk: without the explicit exclusions, this story would silently drift back into the broader Story 191 comparison surface. The main false-positive risk is accepting a small score bump that still hallucinates names or account lines.
   Done when the candidate list and stop rule are recorded before any new variant command runs.

3. Add only the minimum orchestration needed to execute and summarize the frozen matrix, and prefer a new tiny helper over growing the existing benchmark helper.
   Files: prefer a new `scripts/spikes/loc_gw_receipt_probe.py` plus `tests/test_loc_gw_receipt_probe.py`; fall back to `scripts/spikes/loc_gw_benchmark.py` / `tests/test_loc_gw_benchmark.py` only if the new file would duplicate too much logic.
   Change: reuse the receipt transcript, the fresh baseline manifest, `score_page_html_artifact`, `summarize_case_failure`, and recipe-param loading from the existing helper. The helper, if needed, should only run the frozen matrix and write a compact JSON summary containing OCR params, run ids, artifact paths, ratios, and failure modes. No maintained recipe, runtime, schema, or coverage-truth change belongs here.
   Impact/risk: `scripts/spikes/loc_gw_benchmark.py` is already `959` lines and `modules/extract/ocr_ai_gpt51_v1/main.py` is `758`, so pushing this receipt-only probe into either file without need would increase blast radius for a comparison-only story. The one substrate surprise already found is operational rather than architectural: direct module calls need `PYTHONPATH` set, which the existing helper already handles.
   Done when either the manual command sequence is judged sufficient and this task is skipped explicitly, or one bounded helper command can reproduce the frozen matrix with the expected summary payload and focused test coverage.

4. Execute the frozen matrix, inspect the artifacts, and translate the outcome into one explicit repo-owned next move.
   Files: this story file first; `docs/evals/registry.yaml` and `tests/fixtures/formats/_coverage-matrix.json` should remain untouched unless the result changes durable tracked truth, which is unlikely for this comparison-only seam.
   Change: run the bounded variants, open the resulting `page_html_v1` artifacts against the receipt transcript/source image, and record one of two outcomes. Negative path: close the seam negative and keep Story 191 blocked. Positive path: do not reopen Story 191 yet; instead name one second verification move on the same receipt seam, likely a reproducibility rerun of the winning variant plus one additional repo-owned confirmation step, before any broader handwritten claim changes.
   Impact/risk: score deltas alone are not enough because this seam can improve from empty to non-empty while still being semantically wrong. The decision must stay anchored to literal receipt fidelity and inspectable artifact evidence.
   Done when the story records exact OCR params, run ids, artifact paths, ratios, dominant failure modes, and the resulting explicit decision.

Graph/state expectations:

- No category, compromise-phase, eval-registry, or coverage-matrix movement is expected from the bounded receipt-only probe unless a later runtime-owned story changes durable truth.
- `spec:2` and `spec:8` stay `exists`, `C1` stays `climb`, `B1` stays `hold`, and the `handwritten-notes` coverage row should remain `has-fixture` in this story.
- Human-approval blocker before implementation: whether to keep the execution manual/story-local first or add the optional tiny helper up front. No schema or maintained-runtime blocker is present today.

## Work Log

20260412-1029 — create-story: created Story 217 after `/triage` identified the receipt-only follow-on seam and the user approved it. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, Stories 191/208/214/215/216, Scout 014, `scripts/spikes/loc_gw_benchmark.py`, `tests/test_loc_gw_benchmark.py`, and `modules/extract/ocr_ai_gpt51_v1/main.py`. Result: a new `Pending` story is honest because Story 216 already closed the fixed-slice proof-refresh and stronger-model screen, while the remaining move is narrower: isolate asset `367466`, where `gpt-5.4` changed empty output to non-empty without reopening the full LOC pair. Fresh substrate evidence in the same pass confirmed that the LOC helper already supports candidate-model runs, the receipt baseline/challenger artifacts already exist under the shared project `output/` root, and the OCR module already exposes the model/prompt knobs a receipt-only probe would need. Next step: `/build-story` should reproduce the unchanged baseline and `gpt-5.4` receipt artifacts, freeze the candidate set and stop rule, and only then decide whether helper-local changes are warranted.
20260412-1046 — `/build-story` exploration + eval-first baseline: re-read `docs/ideal.md`, `docs/spec.md` (`spec:2`, `spec:2.1`, `spec:2.2`, `spec:8`), `docs/methodology/state.yaml`, `docs/methodology/graph.json`, the `handwritten-notes` coverage row, Stories 191 and 216, `benchmarks/scripts/run_handwritten_notes_eval.py`, `benchmarks/scorers/handwritten_notes_transcription.py`, `configs/recipes/recipe-images-ocr-html-handwritten-notes-gemini-rescue.yaml`, `scripts/spikes/loc_gw_benchmark.py`, `tests/test_loc_gw_benchmark.py`, `modules/extract/ocr_ai_gpt51_v1/main.py`, `driver.py --help`, and `modules/common/run_registry.py` before running the smallest current-pass receipt-only proof. Fresh eval-first evidence in this pass: (1) reran the maintained receipt baseline on the exact Story 216 source image directory with `python driver.py --recipe configs/recipes/recipe-images-ocr-html-handwritten-notes-gemini-rescue.yaml --input-images /Users/cam/Documents/Projects/doc-web/output/runs/story216-loc-gw-proof-refresh-r1/loc_gw_slice/fixtures/loc-gw-receipts-367466/images --run-id handwritten-loc-gw-receipts-367466-image-handwritten-rescue --allow-run-id-reuse --force --end-at ocr_ai`, which wrote fresh worktree-local artifacts under `output/runs/handwritten-loc-gw-receipts-367466-image-handwritten-rescue/` and reproduced the empty sentinel at `output/runs/handwritten-loc-gw-receipts-367466-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl` with `created_at = 2026-04-12T16:43:39.744888Z`, `overall_ratio = 0.0`, `page_min_ratio = 0.0`, and `dominant_failure_mode = empty_html`; (2) reran the unchanged direct `gpt-5.4` challenger from the fresh baseline manifest into `output/runs/story217-loc-gw-receipts-367466-image-gpt-5-4/01_ocr_ai_gpt51_v1/pages_html.jsonl` with `retry_model = gpt-5.2`, the existing handwritten-recipe hints, and `max_long_side = 2048`, producing `created_at = 2026-04-12T16:45:01.782271Z`, `overall_ratio = 0.133043`, `page_min_ratio = 0.133043`, and `dominant_failure_mode = non_empty_wrong_text`. Manual artifact inspection in the same pass confirms the semantic problem remains obvious even when the page is non-empty: the challenger begins `New york 16 Apri 1776`, `Mr Smith to Mr Wrayner Dr for washing 1s goods`, and `Chain 63 Dz at 96. £11.9.6`, which is visibly closer than the empty baseline but still wrong against the receipt transcript. Surprises found: direct `driver.py` runs from this worktree resolve to the worktree-local `output/` tree rather than the shared project output root Story 216 used, and direct `modules/extract/ocr_ai_gpt51_v1/main.py` invocations need `PYTHONPATH` set, but neither issue blocks the story. Decision from exploration: Story 217 remains honestly `Pending`, no maintained-runtime/schema substrate is missing, and the likely highest-value implementation path is still a bounded receipt-only prompt/entry matrix with an optional tiny helper rather than any reopen of Story 191. Next step: present the frozen candidate set and implementation plan for approval before writing code or changing story status.
20260412-1051 — implementation start: user approved the `/build-story` plan, so Story 217 moves to `In Progress`. Immediate next steps in this pass are to regenerate the compiled methodology views for the status change, run the frozen receipt-only variant matrix on the fresh baseline manifest, and decide whether the matrix can stay manual or actually needs a tiny story-local helper.
20260412-1107 — implementation + verification: kept the receipt-only matrix manual/story-local and did not add repo code. Recompiled methodology views with `make methodology-compile`, then ran the frozen receipt-only matrix against the fresh baseline manifest and wrote a story-local summary artifact at `output/runs/story217-loc-gw-receipts-367466-probe-summary.json`. Fresh manual/source inspection in the same pass used the source image at `/Users/cam/Documents/Projects/doc-web/output/runs/story216-loc-gw-proof-refresh-r1/loc_gw_slice/fixtures/loc-gw-receipts-367466/images/page-001.jpg`, the transcript at `/Users/cam/Documents/Projects/doc-web/output/runs/story216-loc-gw-proof-refresh-r1/loc_gw_slice/fixtures/loc-gw-receipts-367466/transcript.txt`, and the stamped/variant artifacts under worktree-local `output/runs/`. Candidate results: unchanged current-pass control `story217-loc-gw-receipts-367466-image-gpt-5-4` stayed at `0.133043`; source-resolution-only `story217-loc-gw-receipts-367466-image-gpt-5-4-source-res` scored `0.122538`; receipt-hints `story217-loc-gw-receipts-367466-image-gpt-5-4-receipt-hints` scored `0.158523`; and receipt-hints + source-resolution `story217-loc-gw-receipts-367466-image-gpt-5-4-receipt-hints-source-res` scored `0.161874`. None materially beat Story 216's `0.16971`, and manual artifact inspection confirms the best variants still misread core receipt content: for example, they turn `Mrs Harper` into `Mr Wagner`/`Mr Wayer`, `4 Counterpins` into `2 Counterpins`, `1 D° Callicoe` into `1 pr pillow case`, `Mrs. Kernekebocker` into `Mr Kemble barber`/`Mr Kermicke barker`, and `1.15.0` into `14.15.7`. Decision: the seam closes negative, Story 191 remains blocked, and no second verification move is warranted from this evidence. Fresh checks in the same pass: `make lint`, `make methodology-check`, `git diff --check`, and `make test` (`571 passed, 4 warnings in 647.38s`). No coverage-matrix, eval-registry, or methodology-state truth change was warranted because the result remained comparison-only negative evidence. Next step: `/validate 217` should recheck the story record, artifact evidence, and negative decision before any close-out attempt.
20260412-1131 — `/mark-story-done` close-out: revalidated Story 217 against `docs/ideal.md`, `spec:2`, `spec:8`, and the existing handwritten benchmark decision chain before closing it. Fresh close-out evidence in this pass: `python -m pytest tests/` (`571 passed, 4 warnings in 654.98s`), `python -m ruff check modules/ tests/` (`All checks passed!`), the probe summary at `output/runs/story217-loc-gw-receipts-367466-probe-summary.json`, the empty baseline artifact at `output/runs/handwritten-loc-gw-receipts-367466-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl`, the best bounded variant at `output/runs/story217-loc-gw-receipts-367466-image-gpt-5-4-receipt-hints-source-res/01_ocr_ai_gpt51_v1/pages_html.jsonl`, the source image at `/Users/cam/Documents/Projects/doc-web/output/runs/story216-loc-gw-proof-refresh-r1/loc_gw_slice/fixtures/loc-gw-receipts-367466/images/page-001.jpg`, and the transcript at `/Users/cam/Documents/Projects/doc-web/output/runs/story216-loc-gw-proof-refresh-r1/loc_gw_slice/fixtures/loc-gw-receipts-367466/transcript.txt`. Result: Story 217 is complete as a bounded negative receipt-only probe; the work stays comparison-only, Story 191 remains blocked, and no eval-registry or coverage-matrix truth change is warranted. Next step: `/check-in-diff`.
