---
title: "Establish a Bounded DiEm HTR Historical-Handwriting Benchmark Slice"
status: "Pending"
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
**Status**: Pending
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

- [ ] A bounded DiEm benchmark slice is defined and attributable before any OCR claim:
  - [ ] the story names the exact DiEm rows or source-page IDs used, their historical/layout rationale, and the `CC BY 4.0` attribution path
  - [ ] the slice stays comparison-only or uses the smallest lawful local cache needed for reproducibility; the story does not silently import a broad third-party corpus into the repo
  - [ ] the work log records whether the selected pages are single-page or two-page spreads and how transcript truth is extracted from the PAGE/ALTO payloads
- [ ] A fresh current-pass benchmark exists on the selected DiEm slice:
  - [ ] the current maintained OCR path is run unchanged first on the slice
  - [ ] artifacts are written under `output/runs/` and manually inspected
  - [ ] scoring or comparison output is reproducible from repo-local code plus the named external source
- [ ] The result is translated into honest repo truth:
  - [ ] the story states whether DiEm should become a durable eval lane, remain comparison-only evidence, or be rejected as a poor fit
  - [ ] `docs/evals/registry.yaml` is updated only if the story truly lands a durable benchmark surface
  - [ ] the `handwritten-notes` coverage row remains bounded unless the story lands enough new evidence to justify a wording change
- [ ] If the DiEm slice is useful but insufficient, the story names the exact next follow-up (for example `Digital Peter`, `Washington`, or `Saint Gall`) instead of leaving the next source ambiguous

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

- [ ] Verify the exact DiEm slice and acquisition path before writing benchmark code:
  - [ ] record the exact page IDs, language/layout rationale, and attribution/license notes from the dataset card
  - [ ] verify the selected rows are reproducibly fetchable in the current environment
  - [ ] verify whether the PAGE/ALTO structure gives enough ground truth for the benchmark shape we actually want
- [ ] Implement the smallest honest benchmark harness:
  - [ ] prefer a story-local script or a narrow helper over changes to the maintained OCR runtime
  - [ ] keep external-corpus handling explicit and bounded
  - [ ] preserve raw OCR outputs and comparison summaries under `output/runs/`
- [ ] Run the maintained OCR baseline on the selected DiEm slice and manually inspect the resulting artifacts
- [ ] Decide whether the result earns a durable eval surface, a comparison-only note, or a rejection, and update docs accordingly
- [ ] If this story changes documented format coverage or graduation reality: update `tests/fixtures/formats/_coverage-matrix.json` and any relevant methodology state honestly
- [ ] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [ ] Run required checks for touched scope:
  - [ ] Default Python checks: `make test`
  - [ ] Default Python lint: `make lint`
  - [ ] If pipeline behavior changed: clear stale `*.pyc`, run through the narrowest real benchmark or `driver.py` path, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [ ] If agent tooling changed: `make skills-check`
- [ ] If evals or goldens changed: run `/improve-eval` and update `docs/evals/registry.yaml`
- [ ] Search all docs and update any related to what we touched
- [ ] Verify Central Tenets:
  - [ ] T0 — Traceability: every output traces to source page, OCR engine, confidence, processing step
  - [ ] T1 — AI-First: didn't write code for a problem AI solves better
  - [ ] T2 — Eval Before Build: measured SOTA before building complex logic
  - [ ] T3 — Fidelity: source content preserved faithfully, no silent losses
  - [ ] T4 — Modular: new benchmark lane should stay bounded and source-aware rather than hard-coding one corpus into the runtime
  - [ ] T5 — Inspect Artifacts: visually verified outputs, not just checked logs

## Workflow Gates

- [ ] Build complete: implementation finished, required checks run, and summary shared
- [ ] Validation complete or explicitly skipped by user
- [ ] Story marked done via `/mark-story-done`

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
- **File sizes**: `benchmarks/scripts/run_handwritten_notes_eval.py` is 330 lines, `benchmarks/scorers/handwritten_notes_transcription.py` is 119 lines, `docs/evals/registry.yaml` is 2084 lines, `tests/fixtures/formats/_coverage-matrix.json` is 564 lines, and this story file begins at 127 lines. Keep registry and coverage-matrix edits surgical
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, Scout 014, Story 191, Story 211, and the current `handwritten-notes` coverage row. No narrower ADR or runbook was found for bounded external historical-handwriting benchmark adoption

## Files to Modify

- `docs/stories/story-212-diem-htr-historical-handwriting-benchmark-slice.md` — keep the story record current (127 lines)
- `benchmarks/scripts/run_handwritten_notes_eval.py` — reuse or extend only if the external-slice path fits cleanly (330 lines)
- `benchmarks/scorers/handwritten_notes_transcription.py` — reuse or extend only if PAGE/ALTO transcript extraction needs a cleaner scorer boundary (119 lines)
- `docs/evals/registry.yaml` — update only if the DiEm benchmark becomes a durable maintained eval line (2084 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — update only if the new benchmark changes documented handwritten reality (564 lines)
- likely new bounded helper under `benchmarks/scripts/` or `scripts/spikes/` — fetch/select DiEm rows and package benchmark outputs (new file)

## Redundancy / Removal Targets

- Any vague “find another handwriting dataset” notes left behind after Scout 014 and this story make DiEm the explicit next benchmark source
- Any temporary DiEm download or transcript-normalization helper that remains after the benchmark shape is settled

## Notes

- New story justification: Story 211 is the sourcing/packaging line; Story 212 is the first implementation line that turns that sourcing result into a real benchmark. Reopening Story 211 would blur research output with benchmark implementation.
- The honest outcome may still be negative. If DiEm turns out to be too clean, too domain-specific, or too awkward to score cleanly, the story should say so and route the next follow-up explicitly.

## Plan

1. Freeze the exact DiEm slice and why it belongs in the benchmark.
   - Choose a very small set of representative rows, record attribution/licensing, and verify the transcript/granularity before writing benchmark glue.
2. Build the smallest comparison-only bridge from DiEm to the existing OCR eval surface.
   - Prefer a thin benchmark helper over any maintained runtime mutation.
3. Run the current OCR baseline, inspect artifacts, and decide what DiEm becomes.
   - Durable eval, comparison-only benchmark, or explicit rejection.

## Work Log

20260411-0130 — create-story: created Story 212 from Scout 014 after verifying that a new ID is honest. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, Story 191, Story 211, and `docs/scout/scout-014-degraded-handwriting-eval-sources.md`. Result: a new story is honest because Story 211 owns source discovery and packaging, while this follow-up owns the first bounded benchmark implementation on the selected external corpus. The story starts `Pending`, not `Draft`, because the benchmark harness substrate already exists locally and the source selection has been narrowed to one publicly documented candidate. Next step: `/build-story` should verify the exact DiEm slice and benchmark bridge before changing any benchmark code.
