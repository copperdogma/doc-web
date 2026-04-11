---
title: "Establish a Bounded LOC George Washington Papers Benchmark Slice"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #2 (Detect), Requirement #3 (Extract), Requirement #6 (Validate), Any format, any condition, Fidelity to the source, Traceability is the product"
spec_refs:
  - "spec:2"
  - "spec:2.1"
  - "spec:2.2"
  - "spec:8"
adr_refs: []
depends_on:
  - "212"
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

# Story 214 — Establish a Bounded LOC George Washington Papers Benchmark Slice

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, `docs/scout/scout-014-degraded-handwriting-eval-sources.md`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/stories/story-191-finish-real-handwritten-ocr-on-the-loc-fixture-pair.md`, `docs/stories/story-211-scout-degraded-handwriting-and-historical-script-eval-sources.md`, `docs/stories/story-212-diem-htr-historical-handwriting-benchmark-slice.md`, `docs/stories/story-215-washington-database-english-longhand-benchmark-slice.md`, and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower ADR or runbook governing LOC benchmark adoption beyond the current scout/story chain
**Depends On**: Story `212`

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

Story 212 proved that a bounded external benchmark can add real pressure to the
blocked handwritten OCR line, but DiEm is still a weaker language and document
match than the Library of Congress handwritten seam that blocks Story 191.
Story 215 then showed that the Washington Database path is externally blocked
for this repo right now. The Library of Congress `By the People` George
Washington dataset is the next honest alternative because it is publicly
reachable in the current environment, packages 593 transcribed assets in one
official ZIP, and exposes direct image URLs plus reviewed volunteer
transcriptions. This story should turn that public LOC dataset into one bounded
comparison-only benchmark slice, write inspectable artifacts under
`output/runs/`, and decide whether it becomes useful negative evidence,
comparison-only benchmark pressure, or a poor fit for the blocked handwritten
line.

## Acceptance Criteria

- [x] A bounded LOC comparison surface is defined and attributable before any OCR claim:
  - [x] the story records the exact official LOC dataset URL, ZIP URL, rights/access notes, and README-backed dataset shape in [benchmark_summary.json](/Users/cam/.codex/worktrees/eefa/doc-web/output/runs/story214-loc-gw-benchmark-r1/benchmark_summary.json) and [slice_manifest.json](/Users/cam/.codex/worktrees/eefa/doc-web/output/runs/story214-loc-gw-benchmark-r1/loc_gw_slice/slice_manifest.json)
  - [x] the story names the exact bounded slice selected from the 593 exported assets and why those rows are a better pressure surface than DiEm for the current blocked line: `367413` interrogations, `367466` receipts, and `780802` farm reports
  - [x] the story records that the benchmark uses raw `DownloadUrl` page images as the canonical surface, keeps PDF wrappers opt-in only, and normalizes transcripts only to UTF-8 text with a trailing newline
- [x] A fresh current-pass comparison-only benchmark exists on the selected LOC slice:
  - [x] the current maintained OCR lane runs unchanged first on the slice via `python scripts/spikes/loc_gw_benchmark.py --instrument --max-attempts 2`
  - [x] artifacts are written under `output/runs/` and manually inspected
  - [x] the benchmark records exact asset ids, LOC image URLs, transcript snippets, and score outputs in repo-local artifacts
- [x] The result is translated into honest repo truth:
  - [x] the story now treats the LOC slice as useful comparison-only negative evidence, not a durable eval lane and not a support claim
  - [x] `docs/evals/registry.yaml` and `tests/fixtures/formats/_coverage-matrix.json` remain unchanged because this story did not create a durable local eval surface
  - [x] the next concrete follow-up is to reuse this same three-asset LOC slice, especially receipt asset `367466` as the empty-output sentinel, in any later stronger-subject-model screen; do not open another source-scout story unless Story 215's Washington access blocker actually clears

## Out of Scope

- Fixing the maintained handwritten OCR runtime in the same story
- Marking `handwritten-notes` as `passing`
- Importing the full 593-asset LOC dataset into the repo
- Turning this public CSV export into a durable maintained eval line unless the story actually earns that surface
- Broad legal review beyond recording the visible LOC rights and access notes plus the concrete comparison-only repo usage posture
- Reopening Story 191 without fresh benchmark evidence that materially changes its unblock condition

## Approach Evaluation

- **Simplification baseline**: before writing new benchmark code, confirm that the official LOC JSON API, ZIP, CSV, and image URLs are all reachable in the current environment and that one bounded slice can be scored honestly with the existing handwritten harness pattern. That substrate already looks promising from create-story exploration.
- **AI-only**: a direct OCR call on the bounded LOC images is part of the benchmark, but it does not replace the deterministic work needed to select rows, normalize the volunteer transcript surface, and package reproducible evidence.
- **Hybrid**: likely best. Use code for LOC dataset fetch, slice definition, transcript extraction, and score packaging; use the existing OCR lane for the actual extraction.
- **Pure code**: only appropriate for orchestration and scoring. It cannot answer historical handwriting fidelity by itself.
- **Repo constraints / prior decisions**: Story 191 remains the blocked runtime line. Story 212 established the comparison-only benchmark pattern and Story 215 now honestly records the failed Washington access gate. The official LOC dataset page is public, exposes a public JSON API plus ZIP, and says the selected dataset collection is provided for educational and research purposes while warning that some contents may still carry rights restrictions. `docs/evals/README.md` says the registry should only change when a real maintained eval surface exists. ADR-002 and ADR-003 remain unchanged because this is evidence gathering, not a runtime-boundary change.
- **Existing patterns to reuse**: `scripts/spikes/diem_htr_benchmark.py`, `tests/test_diem_htr_benchmark.py`, `benchmarks/scripts/run_handwritten_notes_eval.py`, `benchmarks/scorers/handwritten_notes_transcription.py`, Story 208's bounded benchmark discipline, Story 212's comparison-only packaging pattern, and Scout 014's source-selection rubric.
- **Eval**: the deciding evidence is whether a bounded LOC slice can be fetched reproducibly, scored honestly from public image URLs plus reviewed volunteer transcriptions, and produce closer-language benchmark pressure than DiEm without widening the support claim by inertia. Success is a trustworthy comparison-only benchmark or an explicit negative fit, not a passing OCR score.

## Tasks

- [x] Verify and record the exact LOC dataset surface in the current pass:
  - [x] record the official item URL, JSON API URL, ZIP URL, rights/access note, and README-backed dataset shape
  - [x] verify the ZIP, CSV, and sample image URLs are fetchable from this environment
  - [x] document the usable transcript and metadata columns from the CSV
- [x] Define the smallest honest LOC benchmark slice:
  - [x] choose exact rows and explain why they pressure the blocked LOC handwritten line better than DiEm
  - [x] decide that the benchmark stays image-entry canonical and keeps wrapper PDFs as optional stress only
  - [x] record transcript normalization and row filtering: keep only non-empty volunteer transcriptions, preserve text verbatim, normalize only file encoding and trailing newline
- [x] Implement the smallest honest benchmark harness:
  - [x] add the story-local helper [scripts/spikes/loc_gw_benchmark.py](/Users/cam/.codex/worktrees/eefa/doc-web/scripts/spikes/loc_gw_benchmark.py)
  - [x] keep external-corpus handling explicit and bounded
  - [x] preserve raw source metadata, OCR outputs, and comparison summaries under `output/runs/story214-loc-gw-benchmark-r1/`
- [x] Run the maintained baseline on the selected slice and manually inspect artifacts
- [x] Decide that the LOC slice earns comparison-only negative evidence, not a durable eval follow-up in this pass
- [x] If this story changes documented format coverage or graduation reality: no coverage-matrix or methodology-state truth change was warranted because the benchmark stayed comparison-only evidence
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; no redundancy was proven beyond replacing vague LOC follow-up notes with this concrete helper/story surface
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test` (`568 passed, 4 warnings in 638.41s`)
  - [x] Default Python lint: `make lint`
  - [x] Benchmark helper verification: ran `python scripts/spikes/loc_gw_benchmark.py --instrument --max-attempts 2`, verified [benchmark_summary.json](/Users/cam/.codex/worktrees/eefa/doc-web/output/runs/story214-loc-gw-benchmark-r1/benchmark_summary.json), [handwritten_eval.json](/Users/cam/.codex/worktrees/eefa/doc-web/output/runs/story214-loc-gw-benchmark-r1/handwritten_eval.json), and representative `page_html_v1` artifacts under `output/runs/`
  - [x] If agent tooling changed: not applicable, no agent tooling changed
- [x] If this story graduates into a durable eval or golden surface: not applicable, no durable eval surface was created
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: benchmark outputs name exact LOC asset ids, URLs, OCR run ids, inspected artifact paths, and source hashes
  - [x] T1 — AI-First: the story measures the existing OCR lane before proposing any runtime rewrite
  - [x] T2 — Eval Before Build: public source fetch and benchmark shape were verified before helper code landed
  - [x] T3 — Fidelity: volunteer transcripts are preserved verbatim apart from file-format normalization, and the receipt empty-output failure is reported explicitly instead of patched away
  - [x] T4 — Modular: the work stays a story-local comparison helper and tests, not a shared runtime dependency
  - [x] T5 — Inspect Artifacts: benchmark summaries and OCR artifacts were opened and checked manually, not just scored

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

- **Owning module / area**: external handwritten-benchmark harnessing around `scripts/spikes/`, the existing handwritten OCR recipes, and story-local comparison artifacts rather than the maintained runtime itself
- **Methodology reality**: this work belongs to `spec:2` and `spec:8`. In `docs/methodology/state.yaml`, `C1` remains in `climb` and `B1` remains in `hold`; the relevant coverage row is `handwritten-notes`, which is still `has-fixture` and explicitly blocked by real OCR quality on the LOC pair
- **Substrate evidence**: verified in this pass that the repo already had the comparison-only benchmark pattern from Story 212 (`scripts/spikes/diem_htr_benchmark.py`, `tests/test_diem_htr_benchmark.py`), the maintained handwritten eval harness (`benchmarks/scripts/run_handwritten_notes_eval.py`), and the scorer (`benchmarks/scorers/handwritten_notes_transcription.py`). Fresh current-pass LOC verification added the missing public-source substrate: `https://www.loc.gov/item/2020446971/?fo=json` is publicly accessible; its `resources[0].files[0][0].url` points to public ZIP `https://tile.loc.gov/storage-services/master/gdc/gdcdatasets/2020446971/2020446971.zip`; that ZIP is fetchable here and contains one CSV plus README; and the CSV exposes `Campaign`, `Project`, `Item`, `ItemId`, `Asset`, `AssetId`, `AssetStatus`, `DownloadUrl`, `Transcription`, and `Tags`. This implementation pass then closed the remaining local gap with [scripts/spikes/loc_gw_benchmark.py](/Users/cam/.codex/worktrees/eefa/doc-web/scripts/spikes/loc_gw_benchmark.py), [tests/test_loc_gw_benchmark.py](/Users/cam/.codex/worktrees/eefa/doc-web/tests/test_loc_gw_benchmark.py), and the bounded artifact set under `output/runs/story214-loc-gw-benchmark-r1/`
- **Data contracts / schemas**: prefer story-local benchmark summaries plus existing `page_html_v1` outputs. No shared schema change is expected unless the story later graduates into a durable eval artifact
- **File sizes**: `docs/stories/story-214-loc-george-washington-papers-benchmark-slice.md` is 127 lines at bootstrap, `scripts/spikes/diem_htr_benchmark.py` is 634, `tests/test_diem_htr_benchmark.py` is 109, `benchmarks/scripts/run_handwritten_notes_eval.py` is 330, `benchmarks/scorers/handwritten_notes_transcription.py` is 119, `docs/evals/registry.yaml` is 2084, and `tests/fixtures/formats/_coverage-matrix.json` is 564. The DiEm helper and the canonical truth surfaces are already large, so new work should stay surgical and prefer new story-local files
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, Scout 014, and Stories 191/212/213. Search across `docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` found no narrower ADR or runbook governing LOC benchmark adoption beyond the current scout/story chain. ADR-002 and ADR-003 remain unchanged because this story does not alter the `doc-web` boundary

## Files to Modify

- `docs/stories/story-214-loc-george-washington-papers-benchmark-slice.md` — keep the story record, plan, and close-out truth current (127 lines at bootstrap)
- `scripts/spikes/loc_gw_benchmark.py` — bounded LOC dataset fetch, slice selection, and comparison helper (new file)
- `tests/test_loc_gw_benchmark.py` — unit coverage for the new LOC helper and transcript normalization logic (new file)
- `docs/evals/registry.yaml` — only if the story honestly creates a durable local eval/backlog surface (2084 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — only if the story materially changes the documented handwritten support reality (564 lines)

## Redundancy / Removal Targets

- Any vague "next public English longhand source" notes left behind in Story 212 once Story 214 becomes the owning packaging surface
- Avoid growing `scripts/spikes/diem_htr_benchmark.py` unless a tiny shared helper extraction is clearly cleaner than a new LOC-local script

## Notes

- New story justification: Story 212 closed a DiEm-specific benchmark slice, and Story 215 now preserves the failed Washington access gate. The LOC dataset is a different public source with a different transcript/image contract, so a new story is the honest packaging surface
- Public-source posture: the LOC item page and JSON API are publicly accessible in this environment, but the rights advisory still requires the story to keep the result comparison-only and to report any asset-level rights ambiguity honestly
- Comparison-only rule: even a successful LOC benchmark should not widen `handwritten-notes` support or create a maintained eval by default. It has to earn that claim explicitly
- Helper usage note: [scripts/spikes/loc_gw_benchmark.py](/Users/cam/.codex/worktrees/eefa/doc-web/scripts/spikes/loc_gw_benchmark.py) defaults to image-entry only, writes a local copy of the official ZIP plus README under `output/runs/story214-loc-gw-benchmark-r1/loc_dataset/`, and keeps PDF wrappers opt-in through `--include-pdf`
- Follow-up note: the clearest next model-screen subject inside this source is receipt asset `367466`, because the current rescue lane returns stamped empty HTML on it even after the built-in retry path

## Plan

1. Lock the bounded LOC slice and keep the canonical benchmark surface image-entry first. Exploration verified one honest three-asset slice across the actual campaign subprojects: `367413` (`mgw6a00007-4`, interrogations), `367466` (`mgw500029-9`, Revolutionary War receipts), and `780802` (`mgw438393-1`, farm report / work record). The helper should fetch or reuse the public ZIP, preserve the CSV rows verbatim in a local `slice_manifest.json`, download the exact `DownloadUrl` JPEGs, and write the volunteer `Transcription` text with only minimal file-format normalization (`UTF-8`, trailing newline, no content edits). Wrapper PDFs should stay optional stress only, not the canonical decision surface, because the public source is image-native and the no-code baseline already showed that PDF wrapping can add noise without adding source truth.
2. Implement one story-local LOC benchmark helper at `scripts/spikes/loc_gw_benchmark.py` with no shared schema changes. Reuse the existing handwritten eval path instead of inventing a new scorer: materialize the bounded slice under one story-local run root, call `benchmarks/scripts/run_handwritten_notes_eval.py` against the downloaded images, capture the resulting run IDs and `page_html_v1` artifact paths, and write a compact summary JSON that records project, item, `ItemId`, `Asset`, `AssetId`, `DownloadUrl`, transcript preview, score outputs, and OCR artifact paths. Prefer the Python standard library for ZIP/CSV/HTTP work so the helper does not inherit DiEm's `pandas` / parquet dependency shape.
3. Add narrow tests in `tests/test_loc_gw_benchmark.py`. The test surface should cover CSV-row parsing from a local ZIP fixture or in-memory ZIP stub, the slice-selection contract for the three chosen assets, and the transcript/file materialization rules. Keep network and model calls out of unit tests.
4. Use the current-pass no-code baseline as the plan's eval gate. Exploration already ran the maintained handwritten rescue recipes unchanged against a temporary three-fixture LOC corpus at `/tmp/story214_locgw_baseline/corpus.json`, writing `/tmp/story214_locgw_baseline/baseline.json`. Result: `pass_rate = 0.0`, `cases_passing = 0/6`, `overall_min_ratio = 0.0`, `page_min_ratio = 0.0`. Per-fixture image/PDF ratios were `367413` interrogations `0.696694 / 0.747903`, `367466` receipts `0.0 / 0.0`, and `780802` farm report `0.871189 / 0.36194`. Manual artifact inspection confirmed three distinct failure classes: semantically wrong but non-empty OCR on interrogations, total empty HTML on the receipt page, and closest-but-still-drifting OCR on the farm report. Implementation only needs to make that benchmark reproducible and inspectable from repo-local code; it does not need to improve the runtime in this story.
5. Keep scope and truth surfaces tight. Expected effort is `M`. No ADR, shared schema, or coverage-matrix change is justified by the current plan. `docs/evals/registry.yaml` and `tests/fixtures/formats/_coverage-matrix.json` should stay unchanged unless implementation proves this should become a durable maintained eval lane, which the current baseline does not support. If the implementation reproduces the receipt page's empty-output failure, record it as benchmark evidence rather than silently widening Story 214 into an OCR-runtime fix.

## Work Log

20260411-1624 — create-story: created Story 214 after verifying that a new ID is honest. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, Scout 014, and Stories 191/212/215. Result: a new story is honest instead of reopening Story 212 or rewriting Story 215 because the LOC path is a different public source seam and Story 215 should remain the explicit record that Washington is blocked on access. Fresh current-pass source verification established that `https://www.loc.gov/item/2020446971/?fo=json` is public, points to ZIP `https://tile.loc.gov/storage-services/master/gdc/gdcdatasets/2020446971/2020446971.zip`, and that the ZIP is fetchable here with one CSV, one README, 593 rows, direct `DownloadUrl` image links, and volunteer `Transcription` text. That makes the story honestly `Pending`, not `Draft`. Next step: `/build-story` should select a bounded slice from the accessible CSV and write the real benchmark plan.
20260411-1714 — /build-story exploration: re-read `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, Scout 014, Stories 191/212/213, and the `handwritten-notes` coverage row before touching code. Traced the local benchmark substrate in `scripts/spikes/diem_htr_benchmark.py`, `tests/test_diem_htr_benchmark.py`, `benchmarks/scripts/run_handwritten_notes_eval.py`, `benchmarks/scorers/handwritten_notes_transcription.py`, `configs/recipes/recipe-images-ocr-html-handwritten-notes-gemini-rescue.yaml`, `configs/recipes/recipe-pdf-ocr-html-handwritten-notes-gemini-rescue.yaml`, `modules/extract/ocr_ai_gpt51_v1/main.py`, and `tests/test_ocr_ai_gpt51_empty_page_recovery.py`. Fresh source verification in the current pass went beyond the JSON pointer: the public ZIP `2020446971.zip` contains one CSV plus one README; the README says the export contains `593` images, volunteer transcriptions released into the public domain, and blank `Transcription` cells that mean "nothing to transcribe"; `567` rows have non-empty transcription; all `593` rows are `completed`; and sample `DownloadUrl` probes returned `200 image/jpeg`. I then inspected candidate images and selected one bounded three-project slice that keeps the pressure honest: `367413` (`mgw6a00007-4`, interrogations), `367466` (`mgw500029-9`, receipts), and `780802` (`mgw438393-1`, farm report). Eval-first baseline in the same pass: created temporary local fixtures under `/tmp/story214_locgw_baseline/`, ran `python benchmarks/scripts/run_handwritten_notes_eval.py --corpus /tmp/story214_locgw_baseline/corpus.json --image-recipe configs/recipes/recipe-images-ocr-html-handwritten-notes-gemini-rescue.yaml --pdf-recipe configs/recipes/recipe-pdf-ocr-html-handwritten-notes-gemini-rescue.yaml --image-case-id image-handwritten-rescue --pdf-case-id pdf-handwritten-rescue --output /tmp/story214_locgw_baseline/baseline.json`, and inspected the resulting OCR artifacts under `output/runs/handwritten-loc-gw-*/02_ocr_ai_gpt51_v1/pages_html.jsonl`. Result: all six runs failed (`pass_rate = 0.0`, `overall_min_ratio = 0.0`, `page_min_ratio = 0.0`). Image/PDF ratios were `0.696694 / 0.747903` for interrogations, `0.0 / 0.0` for receipts, and `0.871189 / 0.36194` for the farm page. Manual artifact inspection showed mixed failure modes instead of one uniform blocker: the interrogations page is semantically wrong but non-empty, the receipt page stamps `ocr_empty_reason = "Empty HTML output for page 1"` on both entry seams, and the farm image case is closest but still drifts on names and quantities while the PDF wrapper degrades sharply. Critical substrate verified versus missing: the repo already has everything needed to score bounded public LOC rows without shared schema changes, but it does not yet have a story-local LOC helper, reproducible slice manifest, or repo-owned benchmark summary for this public source. Files likely to change remain the story, a new `scripts/spikes/loc_gw_benchmark.py`, and `tests/test_loc_gw_benchmark.py`; files at risk only if scope drifts are `benchmarks/scripts/run_handwritten_notes_eval.py`, the scorer, and `modules/extract/ocr_ai_gpt51_v1/main.py`. Surprise: the receipt failure is not the recipe's blank-page detector; the artifact carries `ocr_empty_reason = "Empty HTML output for page 1"`, so the current rescue path is returning empty OCR on that semi-structured handwritten receipt even after its built-in same-model retry. Next step: keep the story `Pending`, record image-entry as the canonical benchmark path, and wait for user approval before implementation.
20260411-1653 — implementation start: user approved the Story 214 plan, so the story is now `In Progress`. Immediate next steps in this pass are to regenerate the methodology surfaces for the status change, add a story-local LOC benchmark helper plus focused tests, and re-run the bounded slice through the helper with image-entry as the canonical benchmark path and PDF stress kept opt-in.
20260411-2318 — implementation + verification: added [scripts/spikes/loc_gw_benchmark.py](/Users/cam/.codex/worktrees/eefa/doc-web/scripts/spikes/loc_gw_benchmark.py) and [tests/test_loc_gw_benchmark.py](/Users/cam/.codex/worktrees/eefa/doc-web/tests/test_loc_gw_benchmark.py), then materialized the bounded LOC slice under [output/runs/story214-loc-gw-benchmark-r1/](/Users/cam/.codex/worktrees/eefa/doc-web/output/runs/story214-loc-gw-benchmark-r1/). The helper now copies the official ZIP and README locally, writes [slice_manifest.json](/Users/cam/.codex/worktrees/eefa/doc-web/output/runs/story214-loc-gw-benchmark-r1/loc_gw_slice/slice_manifest.json) plus [corpus.json](/Users/cam/.codex/worktrees/eefa/doc-web/output/runs/story214-loc-gw-benchmark-r1/loc_gw_slice/corpus.json), and runs the maintained handwritten rescue recipe unchanged against the three selected image fixtures. Fresh current-pass helper verification via `python scripts/spikes/loc_gw_benchmark.py --instrument --max-attempts 2` wrote [benchmark_summary.json](/Users/cam/.codex/worktrees/eefa/doc-web/output/runs/story214-loc-gw-benchmark-r1/benchmark_summary.json) and [handwritten_eval.json](/Users/cam/.codex/worktrees/eefa/doc-web/output/runs/story214-loc-gw-benchmark-r1/handwritten_eval.json) with `pass_rate = 0.0`, `cases_passing = 0/3`, `overall_min_ratio = 0.0`, and `page_min_ratio = 0.0`. Manual artifact inspection confirmed the same mixed failure classes through the story-local helper rather than only the temporary baseline: [interrogations image artifact](/Users/cam/.codex/worktrees/eefa/doc-web/output/runs/handwritten-loc-gw-interrogations-367413-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl) is non-empty but wrong at `0.737094`, [receipt image artifact](/Users/cam/.codex/worktrees/eefa/doc-web/output/runs/handwritten-loc-gw-receipts-367466-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl) stays fully empty with `ocr_empty_reason = "Empty HTML output for page 1"` and ratio `0.0`, and [farm image artifact](/Users/cam/.codex/worktrees/eefa/doc-web/output/runs/handwritten-loc-gw-farm-780802-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl) is the closest but still materially wrong at `0.871189`. Instrumentation inside [handwritten_eval.json](/Users/cam/.codex/worktrees/eefa/doc-web/output/runs/story214-loc-gw-benchmark-r1/handwritten_eval.json) also confirms the cost/behavior split is inspectable: interrogations took one Gemini call (`$0.004114`), receipts took two Gemini calls but still returned empty HTML (`$0.00486`), and farm stayed cheapest and closest. Focused checks passed (`python -m pytest tests/test_loc_gw_benchmark.py -q` => `5 passed`; `python -m ruff check scripts/spikes/loc_gw_benchmark.py tests/test_loc_gw_benchmark.py` clean), repo lint passed (`make lint`), and the full repo suite passed fresh (`make test` => `568 passed, 4 warnings in 638.41s`; only the pre-existing Pydantic deprecation warnings in `modules/portionize/portionize_headers_numeric_v1/main.py`). Decision: keep the story as comparison-only negative evidence, do not touch `docs/evals/registry.yaml` or the coverage matrix, and use this same three-asset slice as the named follow-up surface for any future stronger-subject-model screen instead of starting another source hunt.
20260411-2356 — validation + close-out: validated Story 214 against the completed implementation and confirmed all tasks, acceptance criteria, tenet checks, and doc updates are satisfied with fresh current-pass evidence. Re-ran repo checks on the current task branch tip (`make lint` clean; `make test` => `568 passed, 4 warnings in 653.45s`), and retained the story's bounded comparison-only benchmark posture because [benchmark_summary.json](/Users/cam/.codex/worktrees/eefa/doc-web/output/runs/story214-loc-gw-benchmark-r1/benchmark_summary.json), [handwritten_eval.json](/Users/cam/.codex/worktrees/eefa/doc-web/output/runs/story214-loc-gw-benchmark-r1/handwritten_eval.json), and the inspected `page_html_v1` artifacts still show public English longhand pressure without earning a maintained support claim. Validation remains complete rather than skipped, no eval-registry or coverage-matrix update is warranted, and the story now closes as `Done` with Story 215 preserved separately as the explicit Washington access blocker. Next step: `/check-in-diff`.
