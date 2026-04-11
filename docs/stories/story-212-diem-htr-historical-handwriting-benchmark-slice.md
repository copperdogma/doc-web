---
title: "Establish a Bounded DiEm HTR Historical-Handwriting Benchmark Slice"
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
  - "211"
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

# Story 212 — Establish a Bounded DiEm HTR Historical-Handwriting Benchmark Slice

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, `docs/scout/scout-014-degraded-handwriting-eval-sources.md`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/stories/story-191-finish-real-handwritten-ocr-on-the-loc-fixture-pair.md`, `docs/stories/story-211-scout-degraded-handwriting-and-historical-script-eval-sources.md`, and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower ADR or runbook governing external historical-handwriting benchmark adoption beyond the scout result
**Depends On**: Story `211`

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

Story 211 identified `DiEm HTR` as the strongest first external source for widening the repo's historical-handwriting pressure surface: public access, permissive `CC BY 4.0` terms, page-level images, and PAGE/ALTO transcription structure. This story should turn that sourcing result into one bounded benchmark slice without widening support claims prematurely. It should select a small representative DiEm subset, run the current maintained OCR lane against it as comparison-only evidence, write inspectable artifacts under `output/runs/`, and decide whether this external surface becomes a durable eval line, a one-off negative benchmark, or just a sourcing dead end.

## Acceptance Criteria

- [x] A bounded DiEm benchmark slice is defined and attributable before any OCR claim:
  - [x] the story names the exact DiEm rows or source-page IDs used, their historical/layout rationale, and the `CC BY 4.0` attribution path
  - [x] the slice stays comparison-only or uses the smallest lawful local cache needed for reproducibility; the story does not silently import a broad third-party corpus into the repo
  - [x] the work log records whether the selected pages are single-page or two-page spreads and how transcript truth is extracted from the PAGE/ALTO payloads
- [x] A fresh current-pass benchmark exists on the selected DiEm slice:
  - [x] the current maintained OCR path is run unchanged first on the slice
  - [x] artifacts are written under `output/runs/` and manually inspected
  - [x] scoring or comparison output is reproducible from repo-local code plus the named external source
- [x] The result is translated into honest repo truth:
  - [x] the story states whether DiEm should become a durable eval lane, remain comparison-only evidence, or be rejected as a poor fit
  - [x] `docs/evals/registry.yaml` remains unchanged because the DiEm slice stayed comparison-only negative evidence rather than a durable maintained eval surface
  - [x] the `handwritten-notes` coverage row remains bounded because the benchmark did not justify widening the repo's handwritten support claim
- [x] If the DiEm slice is useful but insufficient, the story names the exact next follow-up (`Washington Database` as the closer English longhand comparison-only source) instead of leaving the next source ambiguous

## Out of Scope

- Fixing the maintained handwritten OCR runtime in the same story
- Marking `handwritten-notes` as `passing`
- Importing the full DiEm dataset into the repo
- Solving licensing or acquisition for every other historical-handwriting corpus in the same pass
- Reopening Story 191 without fresh benchmark evidence strong enough to meet its unblock condition

## Approach Evaluation

- **Simplification baseline**: before importing any new fixture into the repo, benchmark a small comparison-only DiEm slice using exact dataset row IDs plus current OCR wiring. If that already gives useful pressure, there is no reason to own more external data first.
- **AI-only**: not sufficient by itself. The OCR call is AI-driven, but the story still needs deterministic page selection, transcript extraction from PAGE/ALTO, and inspectable scoring/reporting.
- **Hybrid**: likely best. Use code for dataset fetch/selection, transcript normalization, and score packaging; use the existing OCR lane for the actual text extraction.
- **Pure code**: only appropriate for orchestration, attribution capture, transcript extraction, and score computation. It cannot answer the handwriting-fidelity question on its own.
- **Repo constraints / prior decisions**: Story 191 stays blocked until a materially different benchmark or OCR substrate changes the decision surface. Story 211 selected DiEm as the first candidate specifically because it is page-level and permissively licensed. `docs/evals/README.md` requires durable eval entries only when a real maintained surface exists.
- **Existing patterns to reuse**: `benchmarks/scripts/run_handwritten_notes_eval.py`, `benchmarks/scorers/handwritten_notes_transcription.py`, Story 208's bounded benchmark discipline, and the comparison-only benchmark packaging pattern used elsewhere in `benchmarks/` and `scripts/spikes/`
- **Eval**: the deciding evidence is whether a bounded DiEm slice becomes a repeatable, inspectable benchmark that tells us something materially new about historical handwriting beyond Barney/Alverson. Success is not a support claim; it is a trustworthy benchmark artifact and an honest next decision.

## Tasks

- [x] Verify the exact DiEm slice and acquisition path before writing benchmark code:
  - [x] record the exact page IDs, language/layout rationale, and attribution/license notes from the dataset card
  - [x] verify the selected rows are reproducibly fetchable in the current environment
  - [x] verify whether the PAGE/ALTO structure gives enough ground truth for the benchmark shape we actually want
- [x] Implement the smallest honest benchmark harness:
  - [x] prefer a story-local script or a narrow helper over changes to the maintained OCR runtime
  - [x] keep external-corpus handling explicit and bounded
  - [x] preserve raw OCR outputs and comparison summaries under `output/runs/`
- [x] Run the maintained OCR baseline on the selected DiEm slice and manually inspect the resulting artifacts
- [x] Decide whether the result earns a durable eval surface, a comparison-only note, or a rejection, and update docs accordingly
- [x] If this story changes documented format coverage or graduation reality: no coverage-matrix or methodology-state truth change was warranted because the benchmark stayed comparison-only negative evidence
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; no shared runtime or registry path became redundant, and the DiEm bridge stays story-local until a durable external handwritten eval is honestly earned
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test` (`561 passed, 4 warnings in 652.25s`)
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: ran `python scripts/spikes/diem_htr_benchmark.py --max-attempts 2`, verified the direct `driver.py` image-entry artifacts under `output/runs/`, and manually inspected sample `page_html_v1` outputs
  - [x] If agent tooling changed: not applicable, no agent tooling changed
- [x] If evals or goldens changed: not applicable, no eval or golden surface changed
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: `slice_manifest.json`, `handwritten_eval.json`, and the inspected OCR artifacts tie each result to exact DiEm row IDs, XML truth files, and OCR run IDs
  - [x] T1 — AI-First: the story measured the maintained multimodal OCR path unchanged before proposing any runtime rewrite
  - [x] T2 — Eval Before Build: the DiEm slice became a measured benchmark surface before any wider handwritten-runtime work
  - [x] T3 — Fidelity: PAGE-derived truth was preserved verbatim and the blank / wrong OCR results were recorded explicitly instead of patched by hand
  - [x] T4 — Modular: the DiEm bridge remains a story-local helper plus tests, not a hard-coded corpus dependency in the maintained runtime
  - [x] T5 — Inspect Artifacts: the PAGE/ALTO truth files, benchmark summaries, and final `page_html_v1` artifacts were opened and checked manually

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

- **Owning module / area**: external benchmark harnessing around handwritten OCR, most likely a new benchmark script plus small scorer reuse rather than a maintained runtime module
- **Methodology reality**: this work belongs to `spec:2` and `spec:8`. `C1` remains in `climb`, `B1` remains in `hold`, and the relevant coverage row is `handwritten-notes`, still `has-fixture` with broader degraded historical handwriting unproven
- **Substrate evidence**: Story 211 verified that `benchmarks/scripts/run_handwritten_notes_eval.py`, `benchmarks/scorers/handwritten_notes_transcription.py`, and the handwritten registry line already exist, while the DiEm dataset card exposes public page-level image and PAGE/ALTO fields. The missing piece is the bounded bridge from DiEm row selection to the repo's OCR/scoring surface
- **Data contracts / schemas**: prefer story-local benchmark summaries and existing `page_html_v1` outputs. No shared schema change is expected unless the work graduates into a maintained eval artifact
- **File-size posture**: the shared benchmark/eval registry surfaces are materially larger than this story-local helper. Keep any future registry or coverage-matrix edits surgical
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, Scout 014, Story 191, Story 211, and the current `handwritten-notes` coverage row. No narrower ADR or runbook was found for bounded external historical-handwriting benchmark adoption

## Files to Modify

- `docs/stories/story-212-diem-htr-historical-handwriting-benchmark-slice.md` — keep the story record current
- `scripts/spikes/diem_htr_benchmark.py` — bounded DiEm fetch / transcript / benchmark helper for Story 212
- `tests/test_diem_htr_benchmark.py` — unit coverage for the XML extraction and benchmark-bridge helpers

## Redundancy / Removal Targets

- Any vague “find another handwriting dataset” notes left behind after Scout 014 and this story made DiEm the explicit first benchmark source and Washington the explicit next closer-language follow-up
- Do not promote the DiEm helper into shared runtime code until an external handwritten benchmark actually becomes durable enough to maintain

## Notes

- New story justification: Story 211 is the sourcing/packaging line; Story 212 is the first implementation line that turns that sourcing result into a real benchmark. Reopening Story 211 would blur research output with benchmark implementation.
- Current outcome: DiEm is useful as bounded comparison-only negative evidence, but not as a durable maintained handwritten eval lane for this repo yet.
- Helper usage note: `scripts/spikes/diem_htr_benchmark.py` is intentionally story-local, defaults to image-entry benchmarking, and expects `huggingface_hub`, `pandas` plus a parquet engine such as `pyarrow`, `Pillow`, and `pypdf` in the local environment.
- Named follow-up: the next comparison-only source should be `Washington Database` because it is the closest English longhand comparator to the blocked LOC handwriting line, even though it remains registration-gated and non-commercial.

## Plan

1. Preserve the completed bounded DiEm comparison surface exactly as built.
   - The canonical story artifacts live under `output/runs/story212-diem-htr-benchmark-r1/`, with the slice definition in `diem_slice/slice_manifest.json`, the scored comparison in `handwritten_eval.json`, and the summary surface in `benchmark_summary.json`.
   - The canonical benchmark path is image-entry OCR with `configs/recipes/recipe-images-ocr-html-handwritten-notes-gemini-rescue.yaml`; PDF-entry remains opt-in stress only via `--include-pdf`.
2. Close the story without widening repo truth beyond what the artifacts support.
   - Keep DiEm as comparison-only negative evidence.
   - Leave `docs/evals/registry.yaml` and `tests/fixtures/formats/_coverage-matrix.json` unchanged unless a later follow-up lands a durable maintained handwritten benchmark surface.
3. Carry the handwriting-eval lane forward with the next best comparison-only source.
   - Package `Washington Database` as the next closer-language benchmark follow-up, because it pressures the blocked English longhand surface more directly than DiEm did.

## Work Log

20260411-0130 — create-story: created Story 212 from Scout 014 after verifying that a new ID is honest. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, Story 191, Story 211, and `docs/scout/scout-014-degraded-handwriting-eval-sources.md`. Result: a new story is honest because Story 211 owns source discovery and packaging, while this follow-up owns the first bounded benchmark implementation on the selected external corpus. The story starts `Pending`, not `Draft`, because the benchmark harness substrate already exists locally and the source selection has been narrowed to one publicly documented candidate. Next step: `/build-story` should verify the exact DiEm slice and benchmark bridge before changing any benchmark code.
20260411-1128 — /build-story exploration + story promotion: re-read `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, Story 191, Story 211, the `handwritten-notes` coverage row, and the current DiEm dataset card snapshot at `~/.cache/huggingface/hub/datasets--RA-Data-Science--DiEm_HTR/snapshots/6984292ba5992f039ea8a90b3f0fce709ad63093/README.md`. Critical substrate verified in the current pass: `huggingface_hub` can fetch both `README.md` and `data/DiEm_GT_HTR.parquet`; the handwritten benchmark harness still exists at `benchmarks/scripts/run_handwritten_notes_eval.py`; the scorer still exists at `benchmarks/scorers/handwritten_notes_transcription.py`; and the maintained rescue recipes still run only through `ocr_ai` in that helper. I locally profiled all 975 rows / 16 books from the current parquet snapshot and selected a bounded three-page slice that actually widens layout pressure instead of reusing one book: `8033700071-12391767:27` (`Vinding`, bad condition/layout, visually verified portrait-oriented two-page spread, 110 PAGE/ALTO lines), `8034392541-22064545:28` (`Tranekær`, narrow portrait-oriented two-page spread, early-model-corrected annotation subset, 75 PAGE/ALTO lines), and `8010610941-6469506:76` (`Jersie`, wide landscape two-page spread from the manually transcribed subset, 118 PAGE/ALTO lines). Surprises: the Hugging Face datasets row API fails with HTTP 500 beyond `first-rows`, so the honest reproducible access path is the repo-local parquet snapshot via `hf_hub_download`; also, DiEm images are often open-book spreads even when their aspect ratio looks portrait, so I verified geometry visually instead of inferring physical-page count from width/height alone. No larger scope expansion appeared, so the story is now honestly `In Progress`. Next step: implement the bounded DiEm bridge plus XML extraction tests, regenerate methodology views for the status change, and then run the maintained handwritten rescue path unchanged on the slice.
20260411-1149 — bounded DiEm benchmark implementation + manual inspection: added `scripts/spikes/diem_htr_benchmark.py` and `tests/test_diem_htr_benchmark.py`, then materialized the exact slice at `output/runs/story212-diem-htr-benchmark-r1/diem_slice/`. The slice manifest now captures the exact three selected rows, `CC BY 4.0` attribution, and PAGE-vs-ALTO parity evidence: `diem-vinding-27` (`0.998662`), `diem-tranekaer-28` (`0.999771`), and `diem-jersie-76` (`0.999003`). I manually inspected the resulting source and OCR artifacts at `output/runs/story212-diem-htr-benchmark-r1/diem_slice/slice_manifest.json`, `output/runs/handwritten-diem-vinding-27-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl`, `output/runs/handwritten-diem-tranekaer-28-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl`, and `output/runs/handwritten-diem-jersie-76-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl`. Result: the maintained image-entry handwritten rescue recipe stays deeply negative on this slice. Vinding returned dense but semantically wrong HTML (`overall_ratio=0.137766`), Tranekær returned a stamped blank page (`overall_ratio=0.0`), and Jersie returned structurally plausible but still badly wrong text (`overall_ratio=0.079027`). This is useful benchmark pressure, but not durable eval quality. Decision: keep DiEm as comparison-only negative evidence, leave `docs/evals/registry.yaml` and `tests/fixtures/formats/_coverage-matrix.json` unchanged, and route the next follow-up to the closer-language `Washington Database` comparison-only surface rather than reopening Story 191.
20260411-1153 — fresh verification: reran the story-local helper end to end with `python scripts/spikes/diem_htr_benchmark.py --max-attempts 2`, which completed successfully and rewrote `output/runs/story212-diem-htr-benchmark-r1/benchmark_summary.json` plus `output/runs/story212-diem-htr-benchmark-r1/handwritten_eval.json`. The current-pass helper output confirms the same result on the bounded image-only decision surface: `pass_rate=0.0`, `cases_passing=0/3`, `overall_min_ratio=0.0`, and `page_min_ratio=0.0`. I also reran the required test surface for touched code: `make test` passed fresh (`561 passed, 4 warnings in 652.25s`), with only the pre-existing Pydantic deprecation warnings in `modules/portionize/portionize_headers_numeric_v1/main.py`, and `make lint` had already passed earlier in this pass. Next step: refresh the generated methodology views for the updated story state, then leave the story `In Progress` pending `/validate` and `/mark-story-done`.
20260411-1158 — methodology refresh: reran `make methodology-compile` and `make methodology-check` after updating the story close-out details. Result: `docs/methodology/graph.json` and `docs/stories.md` are freshly regenerated and the methodology graph is current on the story's new checklist and work-log state. Story 212 remains `In Progress` because build is complete but `/validate` and `/mark-story-done` have not happened yet.
20260411-1225 — validation-grade polish: aligned the story notes/plan with the actual image-only canonical benchmark path and documented the helper's dependency preflight explicitly in both the story and script help text. Added narrow regression coverage for the helper's env policy and image-only default so the documented behavior is now test-backed instead of implied.
20260411-1304 — /mark-story-done closeout: re-checked the completed Story 212 slice against the current repo state, including the image-only DiEm benchmark artifacts under `output/runs/story212-diem-htr-benchmark-r1/`, helper help text, targeted DiEm helper tests, `make lint`, `make test` (`563 passed, 4 warnings in 632.34s`), and regenerated methodology views. Result: all acceptance criteria, tasks, and tenet checks remain satisfied on the current tip; validation is complete; and the story is now closed honestly as bounded comparison-only negative evidence rather than a durable handwritten eval lane. Recommended next step: `/check-in-diff`.
