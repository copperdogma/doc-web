---
title: "Establish a Bounded Digital Peter Historical-Handwriting Benchmark Slice"
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

# Story 225 — Establish a Bounded Digital Peter Historical-Handwriting Benchmark Slice

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, `docs/scout/scout-014-degraded-handwriting-eval-sources.md`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/stories/story-191-finish-real-handwritten-ocr-on-the-loc-fixture-pair.md`, `docs/stories/story-212-diem-htr-historical-handwriting-benchmark-slice.md`, `docs/stories/story-215-washington-database-english-longhand-benchmark-slice.md`, `docs/stories/story-217-loc-gw-receipt-only-image-entry-rescue-probe.md`, and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower ADR or runbook governing Digital Peter benchmark adoption beyond Scout 014 and the recent handwritten story chain
**Depends On**: Story `212`

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

Story 217 closed the receipt-only LOC image-entry rescue seam honestly with a negative result, so the next useful handwritten move is a materially different comparison surface rather than another prompt loop on asset `367466`. Scout 014 already identified `Digital Peter` as the best remaining permissive secondary historical-handwriting corpus after DiEm: it is public on Hugging Face, MIT-licensed, and exposes full-page images plus annotation JSON. This story should turn that sourcing result into one bounded comparison-only benchmark slice, using a direct `gpt-5.4` image-entry baseline on a manually selected public slice because the maintained Gemini rescue recipe is not currently usable in this shell. The story should determine whether `Digital Peter` adds useful pressure despite the Russian/Cyrillic mismatch and annotation-heavy truth shape, and end with one explicit decision: keep it as useful comparison-only evidence, or close it as a poor fit without widening the repo's handwritten support claim.

## Acceptance Criteria

- [x] A bounded Digital Peter benchmark slice is defined and attributable before any OCR claim:
  - [x] the story names the exact image IDs or split members selected, the visible MIT license / public file surface, and the current-access evidence from this environment
  - [x] the story records how benchmark truth is reconstructed from the dataset's COCO-style annotations or linked text fields, including any reading-order assumptions
  - [x] the slice stays bounded and comparison-only; the story does not silently import the full `images.zip` corpus into the repo
- [x] A fresh current-pass direct `gpt-5.4` image-entry baseline exists on the selected Digital Peter slice:
  - [x] the selected slice is run unchanged through `modules/extract/ocr_ai_gpt51_v1/main.py` with `model = gpt-5.4` before any new helper claim
  - [x] artifacts are written under `output/runs/` and manually inspected
  - [x] scoring or comparison output is reproducible from repo-local code plus the named public source files
- [x] The result is translated into honest repo truth:
  - [x] the story states whether Digital Peter is useful comparison-only benchmark evidence or a poor fit for the blocked handwritten line
  - [x] `docs/evals/registry.yaml` and `tests/fixtures/formats/_coverage-matrix.json` remain unchanged unless the work actually earns a durable maintained handwritten benchmark surface
  - [x] if Digital Peter is useful but still insufficient, the story names the exact next follow-up instead of leaving another vague dataset note

## Out of Scope

- Fixing the maintained handwritten OCR runtime in the same story
- Marking `handwritten-notes` as `passing`
- Importing the full Digital Peter corpus into the repo
- Reopening Story 191 from comparison-only evidence alone
- Repeating more prompt-only variants on LOC receipt `367466`
- Broad source-discovery work beyond this one bounded corpus and slice

## Approach Evaluation

- **Simplification baseline**: before writing much code, verify that the public Digital Peter repo is reachable now, then benchmark one bounded slice using the direct `gpt-5.4` OCR path plus the smallest story-local truth-reconstruction bridge. Current-pass exploration already did this on a three-page slice and got a catastrophically low baseline (`overall_ratio = 0.01607`, `page_min_ratio = 0.006515`), which proves the source is a real OCR pressure surface and gives the story a concrete decision floor.
- **AI-only**: not sufficient by itself. The OCR call is AI-driven, but the story still needs deterministic slice selection, annotation-to-truth extraction, and inspectable score packaging.
- **Hybrid**: likely best. Use code for dataset fetch, slice materialization, reading-order reconstruction, and comparison packaging; use the maintained OCR lane for extraction.
- **Pure code**: only appropriate for acquisition, annotation normalization, and benchmark orchestration. It cannot answer the handwriting-fidelity question on its own.
- **Repo constraints / prior decisions**: Story 191 remains blocked on OCR capability for real historical handwriting. Story 212 already proved bounded external benchmarking is useful on DiEm, but also showed that comparison-only evidence should not widen support claims by inertia. Story 215 is the closer-language Washington comparator, but it remains blocked on lawful access. Story 217 closed the narrow LOC receipt seam negative, so another same-source prompt loop is not the honest next move. Scout 014 explicitly frames Digital Peter as a permissive secondary source whose weakness is fit, not access.
- **Existing patterns to reuse**: `scripts/spikes/diem_htr_benchmark.py`, `tests/test_diem_htr_benchmark.py`, `benchmarks/scripts/run_handwritten_notes_eval.py`, `benchmarks/scorers/handwritten_notes_transcription.py`, Story 208's bounded benchmark discipline, and Story 212's comparison-only packaging pattern.
- **Eval**: the deciding evidence is whether a bounded Digital Peter slice yields a reproducible, inspectable benchmark that tells us something materially new about historical handwriting beyond DiEm and the blocked LOC pair. Success is not a passing OCR score; it is an honest decision about whether this corpus is worth keeping as comparison-only pressure.

## Tasks

- [x] Verify the exact Digital Peter acquisition path and truth shape before writing benchmark code:
  - [x] record the current public file surface (`README.md`, `images.zip`, annotation JSONs, `dataset_infos.json`) plus visible MIT license evidence
  - [x] verify the exact annotation fields and whether they support coherent page-level truth reconstruction for this repo's comparison shape
  - [x] choose exact image IDs or split members and document why they pressure the blocked handwritten line despite the language/script mismatch
- [x] Implement the smallest honest benchmark harness:
  - [x] prefer a new story-local helper under `scripts/spikes/` over inflating the already-large DiEm helper unless shared code is obviously reusable
  - [x] keep external-corpus handling explicit and bounded
  - [x] preserve raw source metadata, OCR outputs, and comparison summaries under `output/runs/`
- [x] Run the direct `gpt-5.4` image-entry baseline on the selected Digital Peter slice and manually inspect the resulting artifacts
- [x] Decide whether Digital Peter is useful comparison-only evidence or a poor fit, and update docs accordingly
- [x] If Digital Peter is useful but still insufficient, name the exact next follow-up: reopen Story `215` only if lawful Washington access becomes available; otherwise stop without reopening Story `191`
- [x] If this story changes documented format coverage or graduation reality: no coverage-matrix or methodology-state truth change was warranted because the result stayed comparison-only negative evidence
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; no shared helper or docs cleanup was warranted because the minimal path stayed story-local
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test` (`598 passed, 4 warnings in 686.86s (0:11:26)` on the fresh dedicated validation rerun; the previously suspicious quiet tail was confirmed to be slow disposable-venv dependency/install smokes rather than a deadlock)
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: ran the exact direct `gpt-5.4` OCR command on the bounded slice, wrote canonical summary artifacts under `/Users/cam/Documents/Projects/doc-web/output/runs/story225-digital-peter-benchmark-r1/`, and manually inspected the source images, `page_html_v1` outputs, and summary JSON
  - [x] If agent tooling changed: not applicable, no agent tooling changed
- [x] If this story graduates into a durable eval or golden surface: not applicable, no eval or golden surface changed
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: benchmark outputs name exact Digital Peter IDs, source files, OCR run IDs, and inspected artifact paths
  - [x] T1 — AI-First: the story measures the existing OCR lane before proposing new deterministic repair logic
  - [x] T2 — Eval Before Build: source access and truth extraction were verified before any broader handwritten-runtime change
  - [x] T3 — Fidelity: source truth is preserved verbatim and the OCR miss is recorded explicitly as negative evidence instead of patched by hand
  - [x] T4 — Modular: the work stayed story-local and did not add a hard-coded shared runtime dependency
  - [x] T5 — Inspect Artifacts: the benchmark summaries and OCR artifacts were opened and checked manually, not just scored

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
- **Methodology reality**: this work belongs to `spec:2` and `spec:8`. In `docs/methodology/state.yaml`, `C1` remains in `climb` and `B1` remains in `hold`; the relevant coverage row is `handwritten-notes`, which is still `has-fixture` and explicitly blocked by OCR capability on the current real handwritten fixtures
- **Substrate evidence**: verified in this pass that the repo already has the bounded comparison-only benchmark pattern from Story 212 (`scripts/spikes/diem_htr_benchmark.py`, `tests/test_diem_htr_benchmark.py`), the direct OCR entry point at `modules/extract/ocr_ai_gpt51_v1/main.py`, the maintained handwritten eval harness (`benchmarks/scripts/run_handwritten_notes_eval.py`), and the scorer (`benchmarks/scorers/handwritten_notes_transcription.py`). Fresh environment proof in this pass also confirmed the required local Python deps are importable (`huggingface_hub`, `pandas`, `pyarrow`, `Pillow`, `pypdf`) and that the public `ai-forever/Peter` dataset repo is reachable from this environment: `README.md` fetched successfully, file listing shows `images.zip` plus `annotations_{train,val,test}.json`, and `dataset_infos.json` reports `662` full-page images across train/test/validation with about `997 MB` total download size. The truth-shape question is narrower now too: current-pass inspection of annotation sorting and extracted images shows that at least a small one-column slice can be reconstructed honestly enough for benchmarking. The direct `gpt-5.4` baseline path is also current-pass real and already measured on the exploratory three-page slice, so the story is buildable again under the revised contract.
- **Data contracts / schemas**: prefer story-local benchmark summaries plus existing `page_html_v1` outputs. If Digital Peter needs an intermediate annotation-normalized text artifact, keep it in story-local JSON rather than introducing a shared schema prematurely
- **File sizes**: `docs/stories/story-225-digital-peter-historical-handwriting-benchmark-slice.md` is 127 lines at bootstrap, `scripts/spikes/diem_htr_benchmark.py` is 634, `tests/test_diem_htr_benchmark.py` is 109, `benchmarks/scripts/run_handwritten_notes_eval.py` is 330, `benchmarks/scorers/handwritten_notes_transcription.py` is 119, `docs/scout/scout-014-degraded-handwriting-eval-sources.md` is 78, `tests/fixtures/formats/_coverage-matrix.json` is 595, and `docs/evals/registry.yaml` is 2266. The DiEm helper and truth surfaces are already large, so the Digital Peter line should stay surgical and prefer new story-local files over growing shared helpers by default
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, Scout 014, Stories 191/212/215/217, and the current `handwritten-notes` coverage row. Search across `docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` found no narrower ADR or runbook governing Digital Peter benchmark adoption beyond the scout result and recent handwritten chain

## Files to Modify

- `docs/stories/story-225-digital-peter-historical-handwriting-benchmark-slice.md` — keep the story record, validation truth, and close-out rationale current
- `docs/stories.md` — generated story index showing Story 225 status under `spec:2`
- `docs/methodology/graph.json` — generated methodology graph entry and actionability summary for Story 225

## Redundancy / Removal Targets

- Any vague “next public handwriting source” notes left behind once Story 225 becomes the owning packaging surface for the Digital Peter follow-up
- Avoid growing `scripts/spikes/diem_htr_benchmark.py` unless shared code is clearly reusable enough to justify touching an already-634-line helper

## Notes

- New story justification: reopening Story 212 would blur a completed DiEm benchmark with a new source/truth-shape seam, while reopening Story 215 would blur an explicit external-access blocker with a different public/permissive dataset. Story 217 also cannot honestly absorb this because it is a same-source prompt/entry probe that already closed negative.
- Current status rationale: this story is `Done`. It now stands as bounded comparison-only negative evidence on the handwritten line, with Story `215` remaining the only named follow-up if lawful Washington access appears.
- Comparison-only rule: even a successful Digital Peter benchmark should not widen `handwritten-notes` support or create a maintained eval by default. It has to earn that claim explicitly.
- Fit risk: Digital Peter is a permissive and reachable corpus, but its Russian/Cyrillic script and COCO-style annotation surface make it a weaker language match than Washington or the LOC fixtures. The story must be willing to close negative if the truth shape is too indirect for an honest page-level comparison.
- Current outcome: the direct `gpt-5.4` baseline is decisively negative on the bounded slice, but the corpus still counts as useful comparison-only pressure because the truth surface is inspectable and the miss is plainly model-wrong rather than a packaging artifact.
- Validation note: the fresh dedicated rerun completed cleanly at `598 passed, 4 warnings in 686.86s (0:11:26)`. The earlier quiet tail was real work in disposable-venv dependency/install smokes, not a deadlock.

## Plan

1. Keep the current bounded slice and canonical artifacts as the decision floor.
   - The verified comparison surface remains:
     `annotations_val.json:image_id=234:file_name=25_1.jpg`,
     `annotations_val.json:image_id=0:file_name=7_1.jpg`, and
     `annotations_test.json:image_id=305:file_name=46_1.jpg`.
   - Canonical evidence stays anchored to
     `/Users/cam/Documents/Projects/doc-web/output/runs/story225-digital-peter-explore-r1/baseline_probe/`,
     `/Users/cam/Documents/Projects/doc-web/output/runs/story225-digital-peter-explore-r1/direct-gpt54-slice/01_ocr_ai_gpt51_v1/pages_html.jsonl`,
     and `/Users/cam/Documents/Projects/doc-web/output/runs/story225-digital-peter-benchmark-r1/`.
2. Close the story cleanly.
   - Implementation and validation are complete in the current pass.
   - The remaining step is `/mark-story-done`, preserving the decision that
     Digital Peter is comparison-only negative evidence with Story `215` as the
     only named follow-up.

## Work Log

20260417-1637 — create-story: created Story 225 after inspecting Story 217's negative receipt-only result and verifying that a different handwritten follow-on seam is warranted. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, Scout 014, Stories 191/212/215/217, `scripts/spikes/diem_htr_benchmark.py`, `tests/test_diem_htr_benchmark.py`, `benchmarks/scripts/run_handwritten_notes_eval.py`, and `benchmarks/scorers/handwritten_notes_transcription.py`. Fresh substrate verification in the same pass proved that the benchmark pattern already exists locally, the required Python dependencies are importable, and the public `ai-forever/Peter` dataset is reachable now: `README.md` fetched successfully, file listing exposes `images.zip` plus annotation JSONs, and `dataset_infos.json` reports a `662`-image split corpus behind an MIT-licensed public surface. Result: a new `Pending` story is honest because this is a different source/truth-shape seam from the completed DiEm benchmark, the blocked Washington line, and the exhausted LOC receipt probe. Next step: `/build-story` should verify the exact annotation-to-truth path on one bounded Digital Peter slice, then either land a comparison-only benchmark or close the source negative if the truth shape is not honest for this repo.
20260417-1730 — `/build-story` exploration: re-read `docs/ideal.md`, `docs/spec.md` (`spec:2`, `spec:2.1`, `spec:2.2`, `spec:8`), `docs/methodology/state.yaml`, `docs/methodology/graph.json`, Scout 014, Stories 191/212/215/217, the `handwritten-notes` coverage row, `scripts/spikes/diem_htr_benchmark.py`, `tests/test_diem_htr_benchmark.py`, `benchmarks/scripts/run_handwritten_notes_eval.py`, and `benchmarks/scorers/handwritten_notes_transcription.py` before touching any implementation code. Fresh substrate verification in this pass proved that the public Digital Peter dataset is genuinely reachable here and not just scout-paperwork: `README.md`, `dataset_infos.json`, and all three annotation JSONs fetched successfully; `images.zip` downloaded; and current-pass inspection showed that the annotations carry per-region text in `attributes.translation`. I then stress-tested the truth shape on real source pages instead of trusting the JSON blind: extracted `7_1.jpg`, `24_35.jpg`, `25_1.jpg`, `27_24.jpg`, `46_1.jpg`, and `48_6.jpg` into `/Users/cam/Documents/Projects/doc-web/output/runs/story225-digital-peter-explore-r1/selected_images/`, opened them visually, and confirmed that at least a bounded one-column slice is honest for page-level comparison. The strongest current slice candidates are `25_1.jpg`, `7_1.jpg`, and `46_1.jpg`, which were materialized into `/Users/cam/Documents/Projects/doc-web/output/runs/story225-digital-peter-explore-r1/baseline_probe/` with `images/`, `slice_manifest.json`, and a bbox-sorted `transcript.txt`. Important surprise: the maintained Gemini recipe still fails in this shell with `API_KEY_INVALID`, but that no longer blocks the story because the user approved revising the baseline contract away from that path. The revised direct `gpt-5.4` baseline is now current-pass real: a one-page probe on `page-002.jpg` first scored `0.275556`, then the three-page slice run at `/Users/cam/Documents/Projects/doc-web/output/runs/story225-digital-peter-explore-r1/direct-gpt54-slice/01_ocr_ai_gpt51_v1/pages_html.jsonl` measured `overall_ratio = 0.01607`, `page_min_ratio = 0.006515`, and `0/3` exact page matches. Manual artifact inspection confirms the failure is model-wrong, not truth-shape-wrong: page 1 reads as a different Russian document, page 2 mostly gives up as unreadable, and page 3 hallucinates another letter form while still returning fluent-looking HTML. Result: Story 225 is honestly buildable again under the revised direct-baseline contract and remains `Pending`; the likely smallest implementation is a manual/story-local benchmark summary plus explicit decision, not a shared helper. Next step: write that implementation plan into the story and wait for approval before any code or packaging work.
20260417-1856 — implementation: kept the minimal path story-local and did not add a helper. I promoted Story 225 to `In Progress`, wrote canonical benchmark artifacts at `/Users/cam/Documents/Projects/doc-web/output/runs/story225-digital-peter-benchmark-r1/benchmark_summary.json` and `/Users/cam/Documents/Projects/doc-web/output/runs/story225-digital-peter-benchmark-r1/handwritten_eval.json`, and anchored them to the current bounded slice (`25_1.jpg`, `7_1.jpg`, `46_1.jpg`) plus the direct `gpt-5.4` OCR artifact at `/Users/cam/Documents/Projects/doc-web/output/runs/story225-digital-peter-explore-r1/direct-gpt54-slice/01_ocr_ai_gpt51_v1/pages_html.jsonl`. Manual inspection in the same pass confirms the benchmark is decisively negative but honest: page 1 returns a semantically different Russian document, page 2 mostly emits an unreadable-text disclaimer, and page 3 hallucinates a different letter form while preserving only superficial structure. Current decision: keep Digital Peter as comparison-only negative evidence; do not reopen Story 191 and do not create a durable eval lane from this corpus. Fresh checks in this pass: `make methodology-check`, `git diff --check`, and `make lint` all passed. `make test` started cleanly and advanced deep into the suite without surfacing a failure, but it did not complete to a clean final pass in this pass after a long-running tail, so I am not claiming a fresh full-suite pass. Next step: `/validate 225` should confirm the story record, canonical benchmark artifacts, and whether the incomplete `make test` result is acceptable for close-out.
20260417-2055 — validation-follow-up: fixed the story-state inconsistencies called out by `/validate` and investigated the `make test` tail before changing any close-out claim. Fresh evidence in this pass: `git status --short`, `git diff --stat`, `git diff`, and `git ls-files --others --exclude-standard` confirmed the local change set is still just Story 225 plus generated methodology views; `make lint`, `make methodology-check`, and `git diff --check` all still pass; `python -m pytest --collect-only -q tests` mapped the earlier stall boundary to `tests/test_doc_web_cli_contract.py::test_requirements_txt_supports_pptx_import_on_supported_python` and `...::test_requirements_txt_supports_epub_partition_on_supported_python`; both of those tests then passed in isolation (`147.86s` and `145.71s`) in fresh disposable venvs. A fresh interrupted full-suite rerun still did not produce a clean final `make test` pass in this pass, but the investigation now says the quiet tail is dominated by slow fresh-venv dependency/install smokes rather than a proven deadlock. Result: Story 225 stays honestly `In Progress`, `Build complete` is no longer checked ahead of the open test requirement, and the remaining gap is explicit validation completion rather than benchmark ambiguity. Next step: either let a full `make test` pass run to completion in a dedicated validation pass or explicitly narrow the required-check expectation before trying to close the story.
20260417-2121 — dedicated validation rerun: let the full suite run through the previously suspicious quiet tail and captured the clean final result. Fresh evidence in this pass: `make test` completed at `598 passed, 4 warnings in 686.86s (0:11:26)`, `make lint` passed, `make methodology-check` passed, and `git diff --check` passed. The earlier apparent stall is now explained by slow disposable-venv dependency/install smokes inside `tests/test_doc_web_cli_contract.py`, not by a deadlock. Result: Story 225 is implementation-complete and validation-complete as comparison-only negative evidence. The only remaining step is close-out via `/mark-story-done`, with Story `215` still the only named handwritten follow-up if lawful Washington access appears.
20260417-2205 — `/mark-story-done` close-out: revalidated Story 225 against `docs/ideal.md`, `spec:2`, `spec:8`, the current handwritten story chain, and the bounded Digital Peter artifacts before closing it. Fresh close-out evidence in this pass: the canonical benchmark summary at `/Users/cam/Documents/Projects/doc-web/output/runs/story225-digital-peter-benchmark-r1/benchmark_summary.json`, the scored metrics at `/Users/cam/Documents/Projects/doc-web/output/runs/story225-digital-peter-benchmark-r1/handwritten_eval.json`, `make test` (`598 passed, 4 warnings in 686.86s (0:11:26)`), `make lint`, and `make methodology-check`. Result: Story 225 is closed honestly as comparison-only negative evidence; it does not widen `handwritten-notes` support, does not reopen Story 191, and leaves Story `215` as the only named handwritten follow-up if lawful Washington access appears. Next step: `/check-in-diff`.
