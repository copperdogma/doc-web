---
title: "Benchmark GLM-OCR on the Handwritten Blocker and a Table-Heavy Scanned Seam"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #1 (Ingest), Requirement #3 (Extract), Requirement #6 (Validate), Any format, any condition, Fidelity to the source, Traceability is the product"
spec_refs:
  - "spec:1"
  - "spec:1.1"
  - "spec:2"
  - "spec:2.1"
  - "spec:2.2"
  - "spec:8"
adr_refs: []
depends_on:
  - "192"
  - "206"
category_refs:
  - "spec:1"
  - "spec:2"
  - "spec:8"
compromise_refs:
  - "C1"
  - "C6"
  - "B1"
input_coverage_refs:
  - "handwritten-notes"
  - "scanned-pdf-tables"
architecture_domains:
  - "ocr_and_extraction"
roadmap_tags:
  - "campaign:maintained-intake-honesty"
legacy_system: ""
---

# Story 208 — Benchmark GLM-OCR on the Handwritten Blocker and a Table-Heavy Scanned Seam

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/stories/story-191-finish-real-handwritten-ocr-on-the-loc-fixture-pair.md`, `docs/stories/story-192-alverson-handwritten-truth-surface-repair.md`, `docs/stories/story-206-onward-full-book-regression-recovery.md`, `docs/stories/story-164-surya-component-benchmark-for-layout-and-table-seams.md`, `docs/inbox.md`, `CHANGELOG.md`, official GLM-OCR sources (`https://huggingface.co/zai-org/GLM-OCR`, `https://huggingface.co/docs/transformers/main/model_doc/glm_ocr`, `https://arxiv.org/abs/2603.10910`), and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower GLM-OCR benchmark or handwritten-unblock decision doc
**Depends On**: Stories `192` and `206`

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

The GLM-OCR inbox handoff is now the only concrete stronger-OCR lead attached
to the blocked handwritten line. This story should not assume adoption from
leaderboard or social-post framing alone. It should pin the official
GLM-OCR runtime and license posture, benchmark the candidate first on the
corrected Barney/Alverson LOC handwritten pair and then on one explicit
table-heavy Onward scanned seam, compare the result against the maintained
incumbent surfaces, and end with one honest outcome: either the evidence is
strong enough to reopen Story 191 or create a narrow follow-on seam, or Story
191 stays blocked and the inbox handoff closes as negative evidence.

## Acceptance Criteria

- [x] The benchmark substrate is pinned before any adoption claim:
  - [x] the work log cites the official GLM-OCR model card, official usage docs, and technical report
  - [x] the exact bounded runtime path for this machine is recorded honestly (local weights, API path, or explicit blocker)
  - [x] the story names the stop rule if model access, installability, or image-input substrate is not actually runnable here
- [x] A narrow GLM-OCR benchmark exists on both required pressure surfaces:
  - [x] the corrected Story 192 Barney/Alverson LOC pair is scored through the existing handwritten benchmark surface
  - [x] one explicit Onward table-heavy scanned seam is benchmarked using repo-local or freshly regenerated page-image inputs plus existing goldens/scorers or the smallest new comparison harness needed
  - [x] artifacts are written under `output/runs/` and manually inspected
- [x] The result is compared against the current maintained incumbents honestly:
  - [x] the handwritten comparison cites the current maintained rescue baseline (`overall_min_ratio = 0.677267`, `pass_rate = 0.6`) and names the exact GLM artifact paths inspected
  - [x] the scanned comparison cites the current Onward incumbent/golden surface and states whether GLM looks genuinely competitive there or only interesting on paper
  - [x] the story does not overclaim broad handwritten or genealogy support from a narrow benchmark
- [x] The story ends with one explicit next-step decision:
  - [x] if GLM is a real bounded win, the story names the exact reopen or follow-on seam instead of hand-waving "use GLM somewhere"
  - [x] if GLM is not a clear win, Story 191 remains blocked, the inbox item is closed, and no speculative runtime work is opened

## Out of Scope

- Adopting GLM-OCR into the maintained runtime in the same story
- Replacing the `doc-web` / Dossier boundary settled by ADR-002 and ADR-003
- Running a broad OCR bake-off beyond GLM-OCR plus the current incumbents needed for comparison
- Adding new handwritten fixtures, widening the Alverson scope to a front/back pair, or changing Story 191's blocker text without fresh benchmark evidence
- Changing coverage-matrix support claims unless a completed benchmark truly changes documented reality

## Approach Evaluation

- **Simplification baseline**: start with the smallest direct GLM-OCR path that
  the official sources support. If one bounded call path already materially
  beats the handwritten blocker on Barney and corrected-scope Alverson, there
  is no reason to invent heavier orchestration first. Current repo evidence
  says the maintained rescue lane still sits at `overall_min_ratio = 0.677267`
  / `pass_rate = 0.6` on the five-fixture corpus, so even a narrow handwriting
  win would matter.
- **AI-only**: likely the first honest benchmark move. GLM-OCR itself is the
  candidate substrate, so the first question is whether its official direct
  path can beat the maintained handwritten rescue lane and look credible on one
  table-heavy scanned seam without repo-specific logic.
- **Hybrid**: valid only if the direct benchmark is promising but needs thin
  conversion or evaluation glue. Examples: image-format conversion, output
  normalization into the existing handwritten scorer, or the smallest harness
  needed to compare scanned-table output against current goldens.
- **Pure code**: only appropriate for orchestration, artifact packaging, and
  comparison reporting. It must not turn into a new OCR stack or a pile of
  deterministic text repair for handwriting.
- **Repo constraints / prior decisions**: Story 191 is explicitly blocked until
  a materially different OCR substrate appears. Story 192 repaired the
  Alverson truth surface, so new evidence must use the corrected front-page
  scope. Story 206 restored the maintained Onward full-book fidelity surface,
  which keeps `scanned-pdf-tables` honest as the table-heavy comparison seam.
  Story 164 is the closest local pattern for a bounded external OCR/component
  benchmark. `spec:2.1` (`C1`) is still in `climb`, `spec:2.2` (`C6`) remains
  `hold`, and AGENTS requires eval-before-build and manual artifact inspection.
  The inbox handoff itself already warns that the old 2026-02-03 "SOTA" social
  framing is stale by the 2026-03-31 OmniDocBench v1.6 update, so this story
  must rely on current official sources and local artifacts rather than on
  tweet-level claims.
- **Existing patterns to reuse**: `benchmarks/scripts/run_handwritten_notes_eval.py`,
  `benchmarks/scorers/handwritten_notes_transcription.py`,
  `benchmarks/tasks/onward-table-fidelity.yaml`,
  `benchmarks/scorers/html_table_diff.py`,
  `scripts/spikes/surya_component_benchmark.py`, and the reviewed Onward
  golden surfaces under `benchmarks/golden/onward/`.
- **Eval**: the decisive proof is whether GLM-OCR materially changes the
  current blocked handwritten decision while also staying credible on one
  table-heavy scanned seam. The benchmark must therefore score both surfaces,
  name exact artifact paths, and end with a concrete reopen/no-reopen decision
  instead of a vague "interesting model" conclusion.

## Tasks

- [x] Verify the missing substrate before promotion out of `Draft`:
  - [x] record the official GLM-OCR runtime, license, and usage sources from primary docs
  - [x] verify a bounded runnable path exists on this machine without mutating the maintained runtime
  - [x] verify the exact benchmark inputs for Barney, Alverson, and the chosen Onward seam; if the current worktree still lacks the raw Onward images referenced by `benchmarks/tasks/onward-table-fidelity.yaml`, record the regeneration path or stop honestly
- [x] Freeze the benchmark shape and stop rule before coding:
  - [x] handwritten lane = corrected Story 192 Barney/Alverson pair scored with the existing handwritten harness
  - [x] scanned lane = one explicit Onward table-heavy page group with named goldens and page-image inputs
  - [x] define what counts as "strong enough to reopen Story 191" versus "interesting but not actionable"
- [x] Implement the smallest honest benchmark harness:
  - [x] prefer a story-local spike under `scripts/spikes/` or a sibling helper over maintained runtime wiring
  - [x] preserve raw model outputs and comparison summaries under `output/runs/`
  - [x] keep maintained recipes/modules untouched unless the benchmark result itself justifies a follow-on story
- [x] Run the benchmark, manually inspect named artifacts, and publish one decision:
  - [x] update `docs/inbox.md` and the story work log with the final disposition
  - [x] if GLM is a real win, name the exact reopen or follow-on seam
  - [x] if GLM is not a clear win, keep Story 191 blocked and stop
- [x] If this story changes documented format coverage or graduation reality: no coverage or graduation claim changed, but the relevant methodology state was updated honestly during close-out to record Story 208 as completed negative evidence on the handwritten blocker
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test` (`550 passed, 4 warnings in 0:11:13` on 2026-04-10; the earlier interrupted run is superseded)
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through the chosen benchmark path or `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [x] If agent tooling changed: `make skills-check` was not needed because no agent tooling changed
- [x] If evals or goldens changed: no goldens changed and `/improve-eval` was not needed, but `docs/evals/registry.yaml` was updated honestly with Story 208's bounded current-pass handwritten and Marie-Louise candidate evidence
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: benchmark outputs cite exact source pages, model/runtime path, and inspected artifacts
  - [x] T1 — AI-First: the story tests a stronger OCR substrate before inventing new handwritten repair logic
  - [x] T2 — Eval Before Build: GLM is measured on the blocker surface before any maintained runtime change is proposed
  - [x] T3 — Fidelity: comparison stays source-faithful and does not normalize away OCR misses
  - [x] T4 — Modular: keep the work inside a bounded benchmark seam instead of baking GLM assumptions into the maintained path
  - [x] T5 — Inspect Artifacts: manually inspect the handwritten and scanned benchmark outputs, not just aggregate scores

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

- **Owning module / area**: external OCR benchmark harness plus the existing
  OCR/eval surfaces. This story should prove or reject a candidate substrate,
  not mutate the maintained OCR runtime by default.
- **Methodology reality**: this belongs to `spec:1`, `spec:2`, and `spec:8`.
  `docs/methodology/state.yaml` says the category substrates exist, `C1` is in
  `climb`, `C6` is in `hold`, and `B1` is in `hold`. The relevant coverage
  rows are `handwritten-notes` (`has-fixture`) and `scanned-pdf-tables`
  (`passing`). The story moved from `Draft` to `In Progress` in this pass
  after proving a bounded local `ollama` runtime path plus exact Barney,
  Alverson, and Marie-Louise benchmark inputs on this machine.
- **Substrate evidence**: verified local handwritten inputs at
  `testdata/handwritten-notes-barney-real-images/page-001.jpg` and
  `testdata/handwritten-notes-alverson-real-images/page-001.jpg`, plus the
  existing handwritten benchmark harness at
  `benchmarks/scripts/run_handwritten_notes_eval.py` and
  `benchmarks/scorers/handwritten_notes_transcription.py`. Verified the Onward
  comparison goldens exist under `benchmarks/golden/onward/`, and the actual
  machine-level page images exist at
  `/Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images-2048/Image080.jpg`
  through `Image083.jpg` with incumbent comparison HTML in
  `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/02_ocr_ai_gpt51_v1/pages_html.jsonl`.
  Exact runtime proof in this story now includes two paths: the repo-local
  benchmark harness runs through local `ollama`, while the repo's current
  Rosetta `x86_64` Python stack still cannot satisfy the published Hugging Face
  `transformers` backend floor because no matching `torch>=2.4` wheel resolves
  there. A later native `arm64` SDK probe did run the official `glmocr`
  self-hosted pipeline with `torch 2.11.0` / `transformers 5.5.3`, and that
  control still produced the same failing page-080 score.
- **Data contracts / schemas**: no shared schema change is expected for the
  first benchmark pass. Prefer story-local summaries and raw benchmark
  artifacts. If the result graduates into a durable eval or maintained runtime
  surface, update `docs/evals/registry.yaml` and any schema-bearing artifacts
  only in that follow-on work.
- **File sizes**: `docs/stories/story-208-glm-ocr-benchmark-for-handwritten-and-table-heavy-seams.md` is 127 lines after bootstrap, `docs/methodology/state.yaml` is 132 lines, `benchmarks/scripts/run_handwritten_notes_eval.py` is 330 lines, `benchmarks/scorers/handwritten_notes_transcription.py` is 119 lines, `benchmarks/tasks/onward-table-fidelity.yaml` is 61 lines, `benchmarks/scorers/html_table_diff.py` is 212 lines, `scripts/spikes/surya_component_benchmark.py` is 333 lines, and `docs/evals/registry.yaml` is 1900 lines. Avoid growing the registry or shared benchmark files unless the benchmark result really earns durable tracking.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`,
  `docs/methodology/state.yaml`, `docs/methodology/graph.json`, Stories 164,
  191, 192, and 206, `docs/inbox.md`, `CHANGELOG.md`, and the official GLM-OCR
  model card/docs/report. No narrower local ADR, scout, note, or runbook
  exists for this GLM-specific benchmark line, which is why a new story is
  honest instead of a reopen of Story 191.

## Files to Modify

- `docs/stories/story-208-glm-ocr-benchmark-for-handwritten-and-table-heavy-seams.md` — benchmark story scaffold, plan, and work log (127 lines after bootstrap)
- `scripts/spikes/glm_ocr_benchmark.py` — isolated benchmark harness for the bounded handwritten/scanned surfaces (new file)
- `benchmarks/scripts/run_handwritten_notes_eval.py` — extend only if reuse is cleaner than story-local glue (330 lines)
- `benchmarks/scorers/handwritten_notes_transcription.py` — adjust only if GLM output needs the smallest honest normalization for scoring (119 lines)
- `benchmarks/tasks/onward-table-fidelity.yaml` — reuse or patch only if the scanned seam can honestly stay on the existing task surface (61 lines)
- `benchmarks/scorers/html_table_diff.py` — reuse or adapt only if it is cleaner than a story-local comparison helper (212 lines)
- `docs/evals/registry.yaml` — update only if the benchmark becomes durable tracked evidence or changes the handwritten decision surface (1900 lines)

## Redundancy / Removal Targets

- The unprocessed GLM-OCR inbox item once this story owns the benchmark line
- Any stale assumption that a leaderboard or social-post claim alone justifies reopening Story 191
- Any temporary GLM-specific spike glue that remains after a clearly negative result

## Notes

- New story justification: reopening Story 191 immediately would be dishonest
  because its unblock condition requires fresh evidence from a materially
  different OCR substrate. This story has a narrower validation boundary:
  determine whether GLM-OCR is that materially different substrate on the
  corrected handwritten corpus plus one table-heavy scanned seam.
- Official GLM-OCR availability was verified in this pass from the model card,
  official Transformers docs, and the technical report; the repo does not yet
  own a narrower local scout document for it.
- The Onward scanned-table seam is now verified on this machine through the
  shared local paths `/Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images{,-2048}`
  plus the maintained run root
  `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/`.
  The published Hugging Face `transformers` route remains blocked in the repo's
  current Rosetta `x86_64` Python environment because `transformers>=5`
  expects `torch>=2.4` there. A separate native `arm64` Python 3.14 SDK probe
  can run the official self-hosted `glmocr` pipeline on CPU with local Ollama,
  but the page-080 control still scores `0.1689`, so that fuller vendor path
  does not change the benchmark decision.

## Plan

Implementation followed the substrate-first plan below. The remaining closeout
work is validation/documentation, not more benchmark shaping.

1. Verify the bounded GLM runtime path.
   Files: `docs/stories/story-208-glm-ocr-benchmark-for-handwritten-and-table-heavy-seams.md` first; likely a new story-local helper such as `scripts/spikes/glm_ocr_benchmark.py` only after approval.
   Work: use the official GLM-OCR sources to pin the minimum runnable isolated path on this machine, likely through `uv` or a temp virtualenv rather than the maintained repo environment. Record the exact dependency delta, whether `accelerate` or other extras are required, and whether model load is realistic on this x86_64 macOS host with 48 GB RAM.
   Risks: local `transformers==4.41.2` cannot import `GlmOcr*`; a naive benchmark attempt from the repo env will fail before scoring anything. Weight size / runtime support may turn this into explicit negative evidence instead of a runnable benchmark.
   Done looks like: one exact import/load command is proven or the story records an explicit stop rule and remains `Draft`.

2. Freeze the comparison seams around already-verified surfaces.
   Files: `docs/stories/story-208-glm-ocr-benchmark-for-handwritten-and-table-heavy-seams.md`, optionally `benchmarks/scripts/run_handwritten_notes_eval.py` only if direct reuse is cleaner than story-local glue.
   Work: handwritten seam stays the corrected Barney/Alverson LOC pair with Story 191 / 192 as the incumbent evidence surface; scanned seam should use Marie-Louise pages 79-83 via `/Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images-2048/Image079.jpg` through `Image083.jpg` plus the committed per-page goldens under `benchmarks/golden/onward/per_page/`.
   Risks: reusing the multi-page promptfoo task directly is heavier than necessary; story-local scoring may be cleaner so long as it reuses the existing scorer logic instead of inventing a new bar.
   Done looks like: one handwritten lane and one scanned lane are pinned with exact input paths, goldens, and incumbent comparison references.

3. Implement the smallest honest benchmark harness after approval.
   Files: likely new `scripts/spikes/glm_ocr_benchmark.py`, possibly small read-only reuse of `benchmarks/scripts/run_handwritten_notes_eval.py` and `benchmarks/scorers/html_table_diff.py` without mutating the maintained OCR runtime.
   Work: run GLM directly on the four handwritten entry cases and one explicit Marie-Louise scanned seam, preserve raw model outputs under `output/runs/story208-*`, then score against the existing handwritten scorer and the existing HTML table diff scorer or the thinnest wrapper around them.
   Risks: schema drift is unnecessary here; keep artifacts story-local and avoid touching `modules/extract/ocr_ai_gpt51_v1/main.py` unless the benchmark itself earns a follow-on story. The scanned seam should prefer page-level goldens to avoid conflating model quality with multi-page prompt truncation.
   Done looks like: reproducible raw outputs and comparison summaries exist under `output/runs/` with no maintained-runtime mutation.

4. Make the benchmark decision explicit.
   Files: `docs/stories/story-208-glm-ocr-benchmark-for-handwritten-and-table-heavy-seams.md`, and only if warranted `docs/evals/registry.yaml` or `docs/stories/story-191-finish-real-handwritten-ocr-on-the-loc-fixture-pair.md`.
   Work: compare against the maintained handwritten baseline (`overall_min_ratio = 0.677267`, `pass_rate = 0.6`) and the maintained Onward goldens; manually inspect artifacts before naming either a reopen path for Story 191 or a negative closeout.
   Risks: a partial win on tables but not handwriting is not enough to reopen Story 191. A handwriting-only win that collapses on the scanned seam is still useful evidence, but it should become a narrow follow-on rather than an overclaim.
   Done looks like: the story ends with one decision surface only: reopen Story 191, create one narrow follow-on seam, or keep Story 191 blocked with negative GLM evidence.

Implementation blocker resolved in this pass: Story 208 now has a bounded local `ollama` runtime plus committed evidence artifacts. Structural health note remains unchanged: no schema or coverage-matrix change was warranted because the benchmark produced negative evidence instead of a durable support win.

## Work Log

20260410-1505 — create-story: created Story 208 from the GLM-OCR inbox handoff after verifying that reopening Story 191 immediately would be dishonest. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, Stories 164/191/192/206, `docs/inbox.md`, `CHANGELOG.md`, the local handwritten fixtures under `testdata/`, the existing handwritten benchmark harness, the Onward goldens/task files under `benchmarks/`, and the official GLM-OCR model card/docs/report. Result: a new ID is honest because Story 191 is blocked on an OCR-runtime outcome, while this story has a narrower validation boundary: benchmark whether GLM-OCR is a materially different substrate on the corrected handwritten pair plus one table-heavy scanned seam. The story starts `Draft` because the handwritten substrate is verified locally, but the exact GLM runtime path and the raw Onward image-input path referenced by the current table-fidelity task are not yet verified in this worktree. Next step: `/build-story` should pin the runnable GLM path, re-verify or regenerate the scanned-page inputs, and promote the story only if the benchmark substrate is real.
20260410-1548 — build-story exploration: re-read `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, Stories 164/191/192/206/208, and the relevant coverage rows in `tests/fixtures/formats/_coverage-matrix.json`. Code and harness exploration covered `benchmarks/scripts/run_handwritten_notes_eval.py`, `benchmarks/scorers/handwritten_notes_transcription.py`, `benchmarks/tasks/onward-table-fidelity.yaml`, `benchmarks/tasks/onward-table-fidelity-single-page-budget.yaml`, `benchmarks/scorers/html_table_diff.py`, `modules/extract/ocr_ai_gpt51_v1/main.py`, and `scripts/spikes/surya_component_benchmark.py`. Alignment result: the story still closes a real Ideal gap instead of optimizing a dead compromise, and no narrower ADR or runbook exists for this GLM-specific benchmark line. Relevant methodology surface remains `spec:1`, `spec:2`, and `spec:8`; `handwritten-notes` stays `has-fixture`, while `scanned-pdf-tables` remains `passing` and gives this story a table-heavy incumbent seam rather than a blank-slate eval.

Critical substrate verified versus missing in this pass:
- Verified handwritten inputs: `testdata/handwritten-notes-barney-real-images/page-001.jpg` and `testdata/handwritten-notes-alverson-real-images/page-001.jpg` both exist locally, and the existing scorer/harness path is real at `benchmarks/scripts/run_handwritten_notes_eval.py` plus `benchmarks/scorers/handwritten_notes_transcription.py`.
- Verified scanned seam: the repo task files still reference missing relative `input/onward-to-the-unknown-images*.jpg` paths, but the actual machine-level source images exist at `/Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images/` and `/Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images-2048/`, including `Image079.jpg` through `Image083.jpg`. The maintained incumbent run root `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/02_ocr_ai_gpt51_v1/pages_html.jsonl` also exists and maps rows 79-83 back to that shared source directory, which makes the Marie-Louise seam concrete on this machine.
- Missing GLM runtime proof: the current repo Python environment reports `torch==2.2.1`, `transformers==4.41.2`, `huggingface_hub==0.36.2`, no `accelerate`, `uv 0.6.3`, and 48 GB RAM on x86_64 macOS. `transformers` in this env does not expose `GlmOcrForConditionalGeneration`, `GlmOcrProcessor`, or `GlmOcrConfig`, which matches the official HF docs saying GLM-OCR was only added to Transformers on 2026-01-27. That means the exact isolated runtime path is still unproven here and the story should remain `Draft`.

Files likely to change once approved: this story file first, then a bounded helper such as `scripts/spikes/glm_ocr_benchmark.py`; possibly tiny reuse hooks in `benchmarks/scripts/run_handwritten_notes_eval.py` or `benchmarks/scorers/html_table_diff.py` if that is cleaner than duplicating logic. Files at risk if scope drifts: `modules/extract/ocr_ai_gpt51_v1/main.py` and `docs/evals/registry.yaml` should stay untouched unless the benchmark earns a follow-on runtime or durable eval update. Patterns to follow: Story 164's external-component benchmark shape, story-local artifacts under `output/runs/`, page-level goldens for the scanned seam, and no schema changes. Surprises found: the machine-level Onward substrate is stronger than the worktree suggested, but the repo Python env is too old for GLM-OCR even though `torch` and `transformers` are installed. Next step: keep Story 208 `Draft`, get approval for the isolated runtime install/download path, and only then implement the bounded benchmark harness.
20260410-1733 — runtime proof + story promotion: attempted the published Hugging Face path first in an isolated env at `.venv-story208-glm` using `transformers==5.5.3`, `accelerate==1.13.0`, and the repo's current Python `3.11.5` runtime, which is running under Rosetta as `x86_64`. Import/load evidence was mixed but decisive for that stack: `AutoModelForImageTextToText` support is present in current `transformers`, yet the runtime disables model backends unless `torch>=2.4`, and `uv pip install 'torch>=2.4,<3' torchvision` fails for that `macOS x86_64` Python because no matching `torch>=2.4` wheel resolves. I therefore switched to another official model-card runtime, verified `ollama 0.17.7` was already installed locally, pulled `glm-ocr` successfully (`ollama pull glm-ocr` downloaded a `2.2 GB` F16 package), and proved the first real OCR call through `http://localhost:11434/api/generate` on `testdata/handwritten-notes-barney-real-images/page-001.jpg`. That moved the story from `Draft` to `Pending`, then to `In Progress`, and I regenerated `docs/methodology/graph.json` plus `docs/stories.md` after each status change so the truth surfaces matched the live state. Exact bounded runtime path for the main benchmark harness is now: local Ollama daemon + `glm-ocr` model, not the published Hugging Face `transformers` path in the repo's current x86_64 Python env.
20260410-1820 — implementation + benchmark complete with negative evidence: added `scripts/spikes/glm_ocr_benchmark.py` as a bounded benchmark harness that reuses the existing handwritten scorer and HTML-table scorer while keeping maintained runtime code untouched. Fresh artifacts were written under `output/runs/story208-glm-ocr-benchmark-r1/`. Handwritten results are decisively negative against the Story 191/192 maintained baseline (`overall_min_ratio = 0.677267`, `pass_rate = 0.6`): `handwritten/results.json` reports `pass_rate = 0.0`, `overall_min_ratio = 0.097473`, with per-case ratios `barney-image = 0.283231`, `barney-pdf = 0.283231`, `alverson-image = 0.097473`, `alverson-pdf = 0.292624`. Manual artifact inspection confirms visible-source drift and hallucination rather than a narrow scoring quirk: `output/runs/story208-glm-ocr-benchmark-r1/handwritten/barney-image/pages_html.jsonl` starts `health and can again stand among my comrade... dead slave and policing...`, while `testdata/handwritten-notes-barney-real.txt` begins `health, and can again stand among my comrads... alvira and welington was dead...`; `output/runs/story208-glm-ocr-benchmark-r1/handwritten/alverson-pdf/pages_html.jsonl` invents `battle of Chickensapege`, `important article`, and `Bowls`, while the checked-in transcript says `battle of Chickamaga`, `contraband article`, and `Towels`. The scanned seam is also clearly non-competitive: `output/runs/story208-glm-ocr-benchmark-r1/onward-marie-louise/results.json` shows GLM `glm_average_score = 0.318375` / `glm_min_score = 0.1689` across Marie-Louise pages 080-083, versus the current maintained incumbent `incumbent_average_score = 0.93075` / `incumbent_min_score = 0.7489` from `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/02_ocr_ai_gpt51_v1/pages_html.jsonl`. Manual page inspection supports that score gap: `output/runs/story208-glm-ocr-benchmark-r1/onward-marie-louise/page-080/glm_output.html` is valid HTML but misses large portions of the committed table (`Matched 14/51 rows (27%), 246 cell errors`), and page 081 reaches only `0.473` against an incumbent `0.9917`. Decision: GLM-OCR is not a real bounded win on either pressure surface in this environment, Story 191 stays blocked, and this story does not justify a reopen or a new runtime follow-on seam.
20260410-1829 — verification + residual risk: `python -m py_compile scripts/spikes/glm_ocr_benchmark.py`, `make methodology-check`, and `make lint` all passed in this pass. `make test` did not complete cleanly: after `201 passed in 383.99s (0:06:23)`, pytest went idle and I interrupted it, which surfaced a `KeyboardInterrupt` in `subprocess.py`. That means the benchmark result itself is freshly verified and the touched script compiles/lints, but I do not have a fresh full-suite `make test` pass for this turn. Next step: use `/validate` for any additional closeout the user wants, then `/mark-story-done` if the interrupted suite result is acceptable or after a separate clean full test pass.
20260410-1905 — official SDK control on native arm64: after the user questioned whether the direct `ollama` benchmark might be under-using GLM-OCR, I re-checked the official SDK repo and proved a fuller vendor path on this machine. The critical correction is architectural, not score-related: the earlier dependency dead-end was true for the repo's Rosetta `x86_64` Python env, but the underlying host is `arm64`. In a fresh native arm64 Python 3.14 env at `/tmp/glmocr-sdk-arm64`, `pip install -e '/tmp/GLM-OCR[selfhosted]'` succeeded with `torch 2.11.0`, `torchvision 0.26.0`, and `transformers 5.5.3`; `PPDocLayoutV3` then loaded on CPU and detected a single `table` region on `/Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images-2048/Image080.jpg`. I ran the official `glmocr` self-hosted pipeline against local Ollama `/api/generate`, saved the artifact copy under `output/runs/story208-glm-ocr-sdk-page080-r1/`, and rescored `Image080.json` against `benchmarks/golden/onward/per_page/page_080.html`. The result is still `score = 0.1689`, identical to the earlier model-only benchmark, with the incumbent remaining `1.0`. Manual diff against `output/runs/story208-glm-ocr-benchmark-r1/onward-marie-louise/page-080/glm_output.html` shows the SDK path mostly adds formatting (`<strong>` wrappers, curly apostrophes, one extra family-heading row) rather than recovering the missing table rows. Impact: the critique was worth testing, but the fuller official SDK control does not reopen Story 191 or weaken the negative benchmark decision.
20260410-1938 — validation closeout evidence: fixed the mutable methodology-state inconsistency surfaced by `/validate` so `docs/methodology/state.yaml` now records Story 208 in `ocr_and_extraction.recent_story_refs` with `stories_since_audit = 1`, then regenerated `docs/methodology/graph.json` and `docs/stories.md` via `make methodology-compile && make methodology-check`. Re-ran the full default Python test target to completion: `make test` finished at `550 passed, 4 warnings in 673.47s (0:11:13)`, superseding the earlier interrupted run. I also rechecked `python -m py_compile scripts/spikes/glm_ocr_benchmark.py`, `git diff --check`, and `make lint`, and manually reopened the main negative evidence artifacts (`output/runs/story208-glm-ocr-benchmark-r1/summary.json`, the Barney and Alverson handwritten outputs, and the native-arm64 SDK page-080 control under `output/runs/story208-glm-ocr-sdk-page080-r1/`). No additional redundancy worth removing was found beyond the already-processed inbox item and the bounded story-local benchmark artifacts. Result: validation is now complete, Story 208 remains an honest negative benchmark line, and the remaining close-out step is `/mark-story-done`, not more implementation.
20260410-1948 — mark-story-done closeout: recorded Story 208's bounded current-pass benchmark evidence in `docs/evals/registry.yaml` under both `handwritten-notes-transcription` and `onward-table-fidelity`, updated the mutable methodology state to describe Story 208 as completed negative evidence rather than an active current line, and then reran `make methodology-compile && make methodology-check` so the generated views reflect `Done`. Fresh closeout verification for this completion pass remains: `make test` (`550 passed, 4 warnings in 0:11:13`), `make lint`, `python -m py_compile scripts/spikes/glm_ocr_benchmark.py`, and manual reopening of the main negative benchmark artifacts in `output/runs/story208-glm-ocr-benchmark-r1/` and `output/runs/story208-glm-ocr-sdk-page080-r1/`. Result: the story is now complete, documented, and ready for `/check-in-diff`.
