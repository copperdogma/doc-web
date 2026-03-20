# Story 159 — Tune `Docling` on the Onward Hard Case and Rank the Path to 100% Fidelity

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Fidelity to the source, Traceability is the Product, Dossier-ready output, Any format, any condition
**Spec Refs**: spec:2.1 C1 (Multi-Stage OCR Pipeline), spec:3.1 C3 (Heuristic + AI Layout Detection), spec:5.1 C7 (Page-Scope Extraction with Document-Level Consistency Planning), spec:6 (Validation, Provenance & Export), spec:7 (Graduation & Dossier Handoff)
**Build Map Refs**: spec:2 OCR & Text Extraction — substrate exists, `C1` climb; spec:3 Layout & Structure Understanding — substrate exists, `C3` climb; spec:5 Document Consistency Planning — substrate exists, `C7` climb; spec:6 Validation, Provenance & Export — provenance/export bar is active; spec:7 Graduation & Dossier Handoff — accepted `doc-web` direction remains incumbent; Input Coverage row `scanned-pdf-tables` is the primary hard-case lane
**Decision Refs**: `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md`, `docs/decisions/adr-001-source-aware-consistency-strategy/adr.md`, `docs/scout/scout-011-external-document-ingestion-systems.md`, `docs/stories/story-149-onward-scanned-genealogy-collapse-implementation.md`, `docs/stories/story-158-docling-doc-web-replacement-evaluation.md`
**Depends On**: Story 158

## Goal

Take the next non-handwavy step after Story 158: run a reproducible `Docling`
tuning sweep on the real Onward hard-case source, measure how much stock
configuration can close the gap to the current `doc-web` result, and leave a
ranked, evidence-backed recommendation for the smallest remaining intervention.
The intervention ladder must preserve upgradeability on purpose: use official
`Docling` config / built-in pipelines / documented extension seams first, move
to upstream-compatible deeper work only if that official path is falsified, and
only consider source-divergent ownership like a fork if the lower tiers cannot
honestly reach the bar. The story must identify which tier is actually
justified by the observed residual errors instead of guessing from first
impressions. This story stops once that ranking is evidence-backed and the thin
hybrid shape is proven or falsified on the Arthur failure slice; broader Tier 2
generalization is tracked separately in Story 160.

## Acceptance Criteria

- [x] This story remains a spike, not a project-direction change:
  - `docs/ideal.md`, `docs/spec.md`, and `docs/build-map.md` are not realigned
    here
  - `doc-web` remains the incumbent benchmark / acceptance bar until fresh
    evidence proves `Docling` yields a net gain strong enough to justify a
    separate methodology update
- [x] A reproducible local tuning harness exists for the Onward hard-case corpus
  and records, per run, the exact `Docling` options used, runtime, output root,
  and a short machine-readable summary under `output/runs/`
- [x] The sweep covers at minimum the current baseline plus a bounded set of
  realistic stock-tuning candidates, including:
  - OCR-engine and OCR-mode changes that exist in the installed `Docling` API
  - export/image-preservation flags needed for Storybook-facing inspection
  - table-structure options relevant to merged-column or subgroup-leak failures
  - if feasible without exploding cost, one stronger VLM-based conversion path
- [x] Manual inspection is recorded for the exact Onward failure region, not
  just aggregate counts, and names at least:
  - the opening Arthur narrative block
  - the first genealogy-table onset
  - at least one subgroup-heading leakage case
  - provenance continuity at document/page/block level
  - image/export behavior relevant to Storybook consumption
- [x] The story leaves a ranked next-step recommendation backed by artifact
  evidence:
  - tuned stock `Docling` is sufficient
  - or a thin hybrid repair layer is required
  - or a plugin / upstream PR / fork is justified
  And the write-up names the residual error classes that force that choice
- [x] The story records an explicit tiered escalation ladder for driving
  `Docling` to `100%` on the Onward golden lane:
  - Tier 1: official `Docling` surfaces only
    - stock configuration
    - built-in OCR / VLM / export options
    - documented plugin / serializer / extension seams
    - target outcome: upgrade-friendly adoption where a future `Docling`
      version bump only needs a quick smoke test before promotion
  - Tier 2: upstream-compatible deeper ownership only after Tier 1 is
    evidence-backed insufficient
    - thin repo-owned repair/adaptation layer
    - upstream PRs
    - replayable local patches that do not require a permanent fork
  - Tier 3: source-divergent ownership only after lower tiers are falsified
    - maintained fork
    - invasive long-lived patch stack
  - Any recommendation that moves below Tier 1 must name the exact evidence
    that falsified the higher tier
- [x] A parity score surface exists for the accepted Arthur hard-case lane and
  is rerun on the current stock baseline plus the current hybrid proof:
  - the score is anchored to incumbent Onward reviewed/golden artifacts rather
    than to chat-only judgments
  - the score names the exact remaining delta to `100%` before any methodology
    realignment would be justified
  - the score is honest about lane scope and does not claim full-Onward parity
    if later Arthur / broader Onward defects still survive

## Out of Scope

- Building the full Storybook integration for `DoclingDocument`
- Superseding ADR-002 or rewriting the accepted `doc-web` handoff docs in this story
- Realigning `docs/ideal.md`, `docs/spec.md`, or `docs/build-map.md` around
  `Docling` before net-gain evidence exists
- Generalizing the sweep beyond Onward-class repeated-structure documents
- Implementing a large custom repair system before stock-tuning evidence exists
- Generalizing the Tier 2 hybrid repair beyond the Arthur proof window; that
  follow-up now lives in Story 160

## Approach Evaluation

- **Simplification baseline**: Run the exact Story 158 baseline again inside a
  reusable harness so later comparisons are attributable to config changes, not
  to hand-run drift.
- **AI-only**: The only meaningful AI-first candidate here is a stronger native
  `Docling` VLM pipeline. That is worth measuring if install/runtime cost stays
  bounded, but a generic LLM call does not replace the need for reproducible
  page-aware provenance and table structure.
- **Hybrid**: Stock `Docling` plus a thin repair layer remains the leading
  fallback if tuning closes most of the gap but leaves a small set of explicit
  failure classes.
- **Escalation discipline**: the ideal path is not merely "get to 100%"; it is
  "get to 100% while preserving cheap `Docling` upgrades." That means official
  `Docling` config and documented extension seams must be exhausted before
  accepting repo-owned repair layers, upstream patch work, or a fork.
- **Pure code**: Recreating Onward-specific rescue logic before the stock matrix
  is exhausted would repeat the same mistake Story 158 was trying to avoid.
- **Repo constraints / prior decisions**: ADR-003 already says `hybrid`
  currently leads, but that is still based on first-pass pilot evidence. Story
  149 proves this repo can reach a high Onward bar with custom logic, which
  makes Onward a legitimate fidelity gate rather than an aspirational benchmark.
- **Existing patterns to reuse**: Story 158's pinned corpus and output roots,
  `output/runs/story157-docling-pilot-r1/input/source_manifest.json`, the
  incumbent handoff pack under
  `benchmarks/golden/onward/dossier-doc-web-handoff-v1/`, and repo-side
  experiment scripts under `scripts/spikes/` and `scripts/bench/`.
- **Eval**: The first eval remains a manual scorecard plus machine-readable run
  summaries. If the sweep stabilizes into a durable benchmark, promote it into
  `docs/evals/registry.yaml` later instead of pretending it already exists.
- **Direction-control rule**: this story is allowed to strengthen or weaken the
  `Docling` replacement case, but it is not allowed to declare the methodology
  shifted. The most it can do is prove whether that larger change is earned.

## Tasks

- [x] Define the bounded tuning matrix and success rubric:
  - name the exact configurations to run
  - keep the matrix small enough to finish locally
  - define the failure classes that matter for the Onward decision
- [x] Implement a reusable local sweep harness:
  - input: pinned Onward hard-case source or an explicitly named onset-focused subset
  - output: per-run artifacts plus a compact summary JSON/Markdown table
  - preserve enough metadata to rerun the best candidate later
- [x] Run the first tuning sweep and inspect artifacts manually:
  - baseline default
  - image/export-preserving variant
  - at least one OCR-engine or OCR-mode variant
  - at least one table-structure variant
  - optionally one VLM path if it is installable and cost-bounded
- [x] Publish the findings and rank the next intervention:
  - tuned stock `Docling`
  - thin hybrid repair layer
  - plugin / PR / fork
  - update ADR-003 research notes if the evidence materially changes the current read
- [x] Fold a thin hybrid repair proof into this story and run it on top of `baseline-images`:
  - rescue the flattened Arthur pre-table onset with a page-scoped OCR pass
  - rescue the page-4 continuation leakage where subgroup headings collapse into ordinary cells
  - splice the repaired fragments back into the stock `Docling` chapter HTML and inspect the result manually
- [x] Add a parity scorer for the accepted Arthur hard-case lane and rerun it on
  the current baseline plus hybrid proof:
  - anchor the score to repo-owned Onward goldens, not to ad hoc impressions
  - publish machine-readable and Markdown summaries under `output/runs/`
  - name the exact remaining delta to `100%` before any project-direction
    change would be credible
- [x] Run bounded official `Docling` VLM lane probes and rescore them against
  the Arthur parity surface:
  - test the narrowest credible official VLM path on pages 3-4 of the pinned
    hard-case PDF
  - record both quality and operational viability
  - treat timeout / no-artifact outcomes as real evidence, not as invisible noise
- [x] Run the bounded Tier 1 closure pass on source-derived Arthur page images
  and rescore it against the same parity surface:
  - use official `ImageFormatOption` input rather than the PDF wrapper
  - test only locally real official seams in this install
  - record optional-backend absences as operational evidence rather than
    pretending those seams were honestly tested
  - stop if the image-input path still does not materially threaten the current
    `89.0 / 100` hybrid control
- [x] Encode the tiered `Docling` escalation ladder in the story and decision
  package:
  - make Tier 1 official-only upgradeability the ideal path
  - require written falsification before dropping to Tier 2 or Tier 3
  - keep the current measured result honest about which tier currently leads
- [x] This story does not change documented graduation reality, so
  `docs/build-map.md` remains unchanged by design
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] If this remains script + research work: run targeted syntax/runtime checks for new scripts
  - [x] If code touches shipped runtime surfaces: `make test` was not applicable during build because shipped runtime surfaces were untouched
  - [x] If code touches shipped runtime surfaces: `make lint` was not applicable during build because shipped runtime surfaces were untouched
  - [x] For the sweep itself: clear stale `*.pyc` when relevant, run the selected `Docling` commands, verify artifacts under `output/runs/`, and manually inspect sample JSON/HTML/Markdown data
  - [x] If agent tooling changed: `make skills-check` was not applicable because no agent tooling changed
- [x] If a durable benchmark or eval artifact is added: run `/improve-eval` and update `docs/evals/registry.yaml`, or explicitly record why the comparison remains manual research only
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: tuned outputs still preserve source document/page/block provenance
  - [x] T1 — AI-First: exhaust realistic stock/VLM `Docling` options before building bespoke repair code
  - [x] T2 — Eval Before Build: choose the next intervention from measured failures, not intuition
  - [x] T3 — Fidelity: the Onward genealogy onset and subgroup structure are inspected directly
  - [x] T4 — Modular: if repairs are needed, isolate them instead of re-expanding `doc-web` by accident
  - [x] T5 — Inspect Artifacts: inspect actual generated JSON/HTML/Markdown outputs, not just logs

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: a repo-local experiment harness plus ADR research
  artifacts. This should not start in `modules/` or mutate `doc_web/` until the
  sweep proves a narrower implementation target.
- **Build-map reality**: this story is owned by the active `climb` seams in
  `spec:2`, `spec:3`, and `spec:5`, with `spec:6` and `spec:7` acting as the
  acceptance bar. The relevant input-coverage lane is `scanned-pdf-tables`.
- **Substrate evidence**: Story 158 already pinned the local Onward corpus and
  verified a working `Docling 2.80.0` runtime in `.venv-story157-docling-arm64`.
  The exact baseline artifacts exist under
  `output/runs/story157-docling-pilot-r1/docling/`. The installed API exposes
  the expected knobs: `do_ocr`, `ocr_options`, `force_backend_text`,
  `do_table_structure`, `table_structure_options`, `generate_page_images`,
  `generate_picture_images`, `generate_table_images`, and `images_scale`.
- **Data contracts / schemas**: no pipeline schema changes are expected in the
  first pass because this story operates on external `Docling` artifacts and
  research outputs.
- **File sizes**: `docs/stories/story-159-docling-onward-tuning-sweep.md` (92
  lines before this edit), `docs/stories.md` (166 lines), and
  `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md` (155 lines)
  are all comfortably below the repo's size-risk threshold. Expected new files
  are a small sweep script and two research notes.
- **Decision context**: reviewed `docs/ideal.md`, the active `spec:2` /
  `spec:3` / `spec:5` / `spec:6` / `spec:7` build-map lanes, ADR-003, ADR-001,
  Scout 011, Story 149, and Story 158.

## Files to Modify

- `docs/stories/story-159-docling-onward-tuning-sweep.md` — story execution and work log
- `docs/stories.md` — add Story 159 to the index
- `scripts/spikes/docling_onward_tuning_sweep.py` — runnable sweep harness for local `Docling` configs
- `scripts/spikes/docling_onward_hybrid_repair_proof.py` — runnable two-page hybrid proof on top of `baseline-images`
- `scripts/spikes/docling_onward_parity_score.py` — Arthur-lane parity scorer against incumbent Onward goldens
- `scripts/spikes/docling_onward_vlm_lane_probe.py` — bounded official VLM probe runner for Arthur-lane page ranges
- `scripts/spikes/docling_onward_tier1_lane_probe.py` — bounded source-image Tier 1 probe runner for Arthur-lane official seams
- `docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/onward-tuning-matrix.md` — explicit matrix and scoring rubric
- `docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/onward-tuning-findings.md` — per-run findings and ranked recommendation
- `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md` — only if the sweep materially changes the current provisional recommendation

## Redundancy / Removal Targets

- Any ad hoc shell snippets or one-off run notes for `Docling` pilots that the
  sweep script supersedes
- If tuned stock `Docling` clearly wins, parts of the future hybrid-adapter
  exploration surface may become unnecessary; if it clearly fails, a stock-only
  tuning loop becomes a dead end and should be recorded as such

## Notes

- The user's explicit bar is not "better than average external tool quality";
  it is "can Onward get to the same practical correctness as the current
  `doc-web` result, or what exactly blocks that?"
- Storybook currently has no live `doc-web` integration, so this story should
  optimize for best future ingestion substrate rather than for incumbent
  compatibility theater.
- The user's explicit preference is now part of the spike bar: the ideal answer
  is not just "Docling reaches 100% on Onward", but "Docling reaches 100% using
  official config or extension seams that make future upgrades cheap and
  routine."
- Even if `Docling` starts winning locally, this story should still report that
  as spike evidence, not as permission to rewrite the project direction. The
  methodology only moves after the net-gain case is proven on an explicit bar.
- Story 160 now owns the next Tier 2 question: whether the proven two-page
  hybrid repair can generalize without regrowing into most of `doc-web`.

## Plan

1. Define the first bounded matrix in repo-owned research notes.
   - Files: `docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/onward-tuning-matrix.md`
   - Change: freeze the exact configs, inspection targets, and success/falsifier bar before adding any repair logic.
   - Planned matrix:
     - `baseline-auto`: current Story 158 baseline
     - `baseline-images`: baseline plus `generate_page_images=True`, `generate_picture_images=True`, `images_scale=2.0`
     - `ocrmac-fullpage`: `OcrMacOptions(force_full_page_ocr=True)`
     - `tesseract-fullpage`: `TesseractCliOcrOptions(force_full_page_ocr=True)`
     - `table-nocellmatch`: baseline plus `table_structure_options.do_cell_matching=False`
     - `combo-ocrmac-nocellmatch-images`: combine the most promising stock knobs into one "best realistic stock" attempt
     - `vlm-granite` only if the built-in VLM path starts cleanly without exploding setup/runtime cost
   - Done looks like: a reader can rerun the same matrix without reconstructing the intent from chat history.

2. Implement a reusable sweep harness under `scripts/spikes/`.
   - Files: `scripts/spikes/docling_onward_tuning_sweep.py`
   - Change: add a small CLI that converts the pinned Onward hard-case slice with named configs, writes per-run JSON/HTML/Markdown outputs under `output/runs/story158-docling-tuning-r1/`, and emits a compact `summary.json` / `summary.md`.
   - Reuse: Story 158's pinned input path and the local `.venv-story157-docling-arm64` runtime; keep the harness external to `modules/` and `doc_web/`.
   - Done looks like: one command can rerun the stock sweep and produces inspectable artifact roots plus configuration metadata.

3. Run the stock sweep and inspect the same failure region across variants.
   - Files: `output/runs/story158-docling-tuning-r1/...` and `docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/onward-tuning-findings.md`
   - Change: execute the first bounded matrix, then inspect the Arthur opening narrative, first genealogy-table onset, subgroup leakage rows, provenance continuity, and image/export behavior.
   - Done looks like: the findings note names the best stock variant, the residual failure classes, and whether a second-stage repair/plugin path is now justified.

4. Update decision docs only if the evidence changed the architecture read.
   - Files: `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md` if needed
   - Change: narrow ADR-003 only if the sweep materially shifts the current `hybrid currently leads` stance.
   - Done looks like: the ADR stays honest about whether stock `Docling` moved closer to "enough" or merely clarified the repair target.

5. Run the thinnest honest hybrid repair proof on the exact residual failure class.
   - Files: `scripts/spikes/docling_onward_hybrid_repair_proof.py`,
     `output/runs/story158-docling-hybrid-proof-r1/`,
     `docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/onward-tuning-findings.md`,
     and `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md`
   - Change: keep the stock `baseline-images` artifact as the substrate, rescue page 3
     and page 4 of the Arthur onset with targeted OCR, splice those repaired
     fragments back into the chapter HTML, and rerun the shared genealogy merger.
   - Done looks like: the Arthur onset no longer starts as flattened prose, the
     page-4 `ALICE'S FAMILY`-style leak is removed from the repaired excerpt, and
     the notes can point to concrete before/after artifacts instead of another
     theoretical adapter discussion.

6. Freeze a parity score surface against the incumbent Arthur lane.
   - Files: `scripts/spikes/docling_onward_parity_score.py`,
     `output/runs/story158-docling-parity-r1/`,
     `docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/onward-tuning-findings.md`
   - Change: compare the accepted Arthur hard-case lane from repo-owned Onward
     goldens with the current `baseline-images` stock output and the current
     two-page hybrid proof so future `Docling` experiments have a concrete
     `100%` target.
   - Done looks like: the score report makes the current spike state explicit:
   where stock `Docling` still fails badly, where the hybrid proof closes the
   gap, and what exact residual issues still block a project-direction change.

7. Close the remaining honest Tier 1 question on direct source-image input.
   - Files: `scripts/spikes/docling_onward_tier1_lane_probe.py`,
     `output/runs/story158-docling-tier1-lane-r1/`,
     `output/runs/story158-docling-parity-r4/`,
     `docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/onward-tuning-findings.md`,
     and `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md` if
     the result materially changes the current read.
   - Change: run only the remaining locally real official seams on the Arthur
     lane using direct page-image input from the pinned Onward source, not the
     PDF wrapper. Candidate configs should stay bounded to what this install can
     honestly exercise: default image input, image input plus `OcrMac`, and the
     currently viable official image-VLM preset. Optional OCR backends whose
     packages are not installed should be recorded as unavailable rather than
     silently implied.
   - Done looks like: the story can say whether current Tier 1 official seams
     are materially exhausted on this lane, using parity scores and operational
     evidence instead of chat-level intuition.

Impact analysis:
- Story-scope impact: this closes the main open question left by Story 158, namely whether stock `Docling` still has obvious headroom before custom work is justified.
- Pipeline-scope impact: the sweep should tell us whether the key Onward failure is primarily OCR, table-cell assignment, export configuration, or something deeper in layout/table understanding.
- Scope expansion folded in after user approval: because the sweep showed the
  residual error class was narrow and page-local, this story now absorbs a
  small two-page hybrid proof instead of splitting that work into Story 160.
- Scope expansion folded in after further user clarification: this story now
  also owns a lane-scoped parity score surface so future `Docling` experiments
  can be judged against the incumbent Arthur hard-case output without implying
  that the wider repo direction has already changed.
- Scope expansion folded in after parity scoring: because the remaining gap was
  now specific and measurable, this story also absorbed one bounded official
  `Docling` VLM follow-up on the same lane instead of splitting it into another
  story prematurely.
- Files at risk: limited to the new script plus ADR research notes unless results are strong enough to justify updating ADR-003.
- Human-approval blockers already resolved: user explicitly approved creating the story and starting the sweep.
- Operational blockers to watch:
  - VLM path may require additional model downloads and could be deferred if it bloats the pass
  - Tesseract language data may not match Onward's French/English mix perfectly; record that if it distorts conclusions
  - If the matrix runtime grows beyond a coherent local pass, stop after the stock PDF-pipeline variants and publish partial findings

Verification plan:
- Targeted script syntax/runtime checks for the new harness
- Real `Docling` sweep runs under `output/runs/story158-docling-tuning-r1/`
- Real parity score runs under `output/runs/story158-docling-parity-r1/`
- Manual inspection of generated JSON/HTML/Markdown artifacts
- `git diff --check` after docs/script edits
- If the story recommends dropping below Tier 1, the triggering evidence must
  point to specific artifact-backed misses or operational blockers, not to
  impatience

## Work Log

20260320-1140 — story created: user approved the next concrete step after Story
157 and explicitly asked for a real Onward tuning pilot rather than more
architecture debate. This story exists to answer the only question that now
matters for `Docling`: whether realistic stock tuning can close the Onward gap,
and if not, what the smallest justified next intervention is. Next step:
execute `/build-story`, implement the sweep harness, and run the first bounded
matrix on the pinned hard-case corpus.
20260320-1148 — build-story exploration: reviewed `docs/ideal.md`, the active
`spec:2` / `spec:3` / `spec:5` / `spec:6` / `spec:7` build-map lanes, ADR-003,
ADR-001, Story 149, Story 158, and existing repo experiment-script patterns in
`scripts/quick_ocr_target_test.py` and `scripts/bench/bench_harness.py`. The
critical substrate is real, not aspirational: Story 158 already pinned the
Onward hard-case slice under
`output/runs/story157-docling-pilot-r1/input/onward-hardcase-slice-imageonly.pdf`,
and `.venv-story157-docling-arm64` exposes the required `Docling` tuning knobs
(`OcrAutoOptions`, `OcrMacOptions`, `TesseractCliOcrOptions`,
`RapidOcrOptions`, `TableFormerMode`, image-generation flags, and the VLM
pipeline modules). `tesseract` is present on this machine at
`/usr/local/bin/tesseract`. Small coherent scope choice: keep the first pass in
a repo-local sweep harness plus ADR research notes; do not touch `doc_web/` or
`modules/` yet. Next step: land the matrix note, implement the harness, and run
the stock variants on the 40-page hard-case slice.
20260320-1238 — first stock sweep complete: implemented
`scripts/spikes/docling_onward_tuning_sweep.py`, froze the matrix in
`docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/onward-tuning-matrix.md`,
and executed the bounded stock sweep under
`output/runs/story158-docling-tuning-r1/`. Fresh evidence: `baseline-auto`
reproduced Story 158 exactly; `baseline-images` preserved the same structural
result while solving the image-export gap (`7` HTML `<img>` tags, `40` page
images, `7` picture images, `20` table images); `ocrmac-fullpage` left the
decisive genealogy-table onset unchanged; `table-nocellmatch` regressed
header/cell integrity; `tesseract-fullpage` improved some later table rows but
still left the first genealogy onset flattened and emitted repeated OSD
warnings. Updated `onward-tuning-findings.md`, ADR-003, and the ADR final
synthesis accordingly. Redundancy note: this script now supersedes ad hoc
one-off shell runs for future stock `Docling` sweeps. Eval note: the sweep is
still manual research, not a durable benchmark, so `docs/evals/registry.yaml`
was intentionally left untouched in this pass. Next step: validate this story
package, then build the thinnest hybrid repair proof on top of the
image-preserving stock config.
20260320-1308 — thin hybrid proof complete: implemented
`scripts/spikes/docling_onward_hybrid_repair_proof.py` and ran it successfully
under `output/runs/story158-docling-hybrid-proof-r1/`. The scripted proof keeps
`baseline-images` as the substrate, rescues page 3 and page 4 of the Arthur
hard-case slice with targeted `gpt-4.1` OCR, splices those two repaired
fragments back into the stock chapter HTML, and reruns the shared genealogy
merger. Fresh evidence from `summary.json` / `summary.md`: the Arthur excerpt
went from `8` pre-table paragraphs and `0` subgroup rows to `0` pre-table
paragraphs and `46` subgroup rows, and the specific page-4 leak
`ALICE'S FAMILY Barbara Hodges` is gone in the repaired excerpt. Manual
inspection of `arthur-after.html` confirms the repaired slice now has a real
Arthur genealogy table with explicit subgroup rows for `ARTHUR'S FAMILY`,
`DORILLA'S FAMILY`, `IRENE'S FAMILY`, `RAYMOND'S FAMILY`, `THEODORE'S FAMILY`,
`ODELIE'S FAMILY`, `ALICE'S FAMILY`, `PAUL'S FAMILY`, `YVETTE'S FAMILY`,
`JOE'S FAMILY`, and `ROBERT'S FAMILY`. Script verification passed via
`.venv-story157-docling-arm64/bin/python -m py_compile` and a full scripted
run; `git diff --check` also passed. Scope read: the hybrid path is now
evidence-backed on the exact remaining Onward failure class, but the repaired
chapter still has later repeated-structure defects outside the two-page proof
window, so this is a successful proof-of-shape, not yet a full replacement for
the Onward path.
20260320-1418 — spike rule and parity scope expanded: the user explicitly
clarified that this work should remain a spike until `Docling` proves a real
net gain, so the story now makes that constraint explicit in acceptance
criteria and scope. New task added: freeze a parity score surface against the
incumbent Arthur hard-case lane so future `Docling` experiments are measured
against repo-owned reviewed/golden output instead of against chat-level
impressions. Next step: implement the scorer, run it on `baseline-images` and
the current hybrid proof, and record exactly what still blocks a methodology
realignment.
20260320-1435 — Arthur-lane parity score frozen: implemented
`scripts/spikes/docling_onward_parity_score.py`, ran it successfully under
`output/runs/story158-docling-parity-r1/`, and manually inspected
`summary.md`, `baseline-images-arthur-lane.html`, and
`hybrid-two-page-arthur-lane.html`. The scorer anchors the current spike to
the repo-owned Arthur gold table in `benchmarks/golden/onward/arthur.html`
using a 30-subgroup lane window plus targeted person/spouse checkpoint pairs.
Fresh evidence: `baseline-images` scores `16.9 / 100`, while the current
hybrid proof scores `89.0 / 100`. The remaining gap is now explicit instead of
fuzzy: the hybrid proof fixed onset, header shape, leak hygiene, and the key
checkpoint rows, but it still diverges at subgroup position `#14` where the
gold expects `PAUL'S FAMILY` and the current lane emits `ANTHONY'S FAMILY`,
and it still misses `DONALD'S FAMILY`, `Joe's Grandchildren`, and
`MARIE'S FAMILY` inside the first 30-subgroup window. Script verification
passed via `.venv-story157-docling-arm64/bin/python -m py_compile`; the real
score run completed successfully; manual inspection confirmed the baseline lane
still contains `ALICE'S FAMILY Barbara Hodges`, while the hybrid lane no
longer does. Next step: use this score surface to test the next honest
`Docling` levers on the narrow remaining failure class instead of reopening the
already-solved onset/leak questions.
20260320-1532 — official `Docling` VLM lane probes run: implemented
`scripts/spikes/docling_onward_vlm_lane_probe.py` and used it to probe the
same Arthur lane with official `Docling` VLM presets on page range `3-4`. The
strong read from this pass is that the official VLM path did not beat the
current hybrid proof on either quality or operational simplicity. Fresh
evidence:
`smoldocling-transformers` completed in `40.07s` under
`output/runs/story158-docling-vlm-lane-r1/smoldocling-transformers/`, but the
rescored lane in `output/runs/story158-docling-parity-r3/summary.json` is only
`17.9 / 100`: no subgroup-row promotion, broken header shape, and only one of
seven checkpoint pairs passing. Manual inspection of
`page-range.html` confirms that family markers like `ARTHUR'S FAMILY` and
`IRENE'S FAMILY` are still leaking into ordinary cells rather than becoming
subgroup rows. The stronger `granite-vision-transformers` leg never produced a
page-range artifact before manual termination after roughly `265s` and
`2378656 KB` RSS; that operational failure is recorded in
`output/runs/story158-docling-vlm-lane-r1/granite-vision-transformers/meta.json`.
Local package inspection also failed to surface a discoverable
`allow_external_plugins`-style registration seam in this install, so the
official seams exercised here were page-range VLM presets rather than plugin
replacement hooks. Net read: official VLM levers in this environment do not
currently close the remaining Arthur-lane gap, which strengthens the case that
the measured path forward is still `baseline-images` plus a thin repo-owned
repair layer rather than native `Docling` replacement.
20260320-1604 — tiered ideal path clarified: the user made the preferred
decision ladder explicit, and the story now records it as an acceptance bar
instead of leaving it implicit. Tier 1 is the ideal: official `Docling`
configuration, built-in pipelines, and documented extension seams that preserve
cheap future upgrades plus a quick smoke-test path. Tier 2 is only allowed once
Tier 1 is falsified with artifact-backed misses or operational blockers, and
Tier 3 is the true last resort for long-lived source divergence like a fork.
This does not change the measured result from the current spike; it changes the
decision discipline for future passes. Next step: keep using the Arthur parity
surface to prove or falsify remaining official seams before accepting deeper
ownership.
20260320-1628 — Tier 1 closure-pass exploration: refreshed `docs/ideal.md`,
`docs/build-map.md`, ADR-003, and the current Story 159 state before choosing
the next pass. Local substrate findings now narrow the honest official-only
question substantially. `ImageFormatOption` is real in the installed
`Docling 2.80.0` package, which means direct source-image input is a genuine
remaining Tier 1 seam. `RapidOcrOptions` and `EasyOcrOptions` also exist as API
types, but their optional runtime packages are not installed in
`.venv-story157-docling-arm64`, so they are not honest same-pass candidates
without widening dependency setup. A quick no-edit probe on page images 3-4
showed `image-default` and `image-ocrmac` both run quickly, while
`image-smoldocling` is slower but still operational and at least recovers a
table on page 3 where the earlier PDF-VLM path stayed poor. Small coherent
scope expansion folded into the story: add one bounded source-image Tier 1
closure pass and judge it against the existing Arthur parity surface before
accepting Tier 2 as the default path.
20260320-1742 — bounded Tier 1 source-image closure pass complete: implemented
`scripts/spikes/docling_onward_tier1_lane_probe.py`, compiled it, and ran the
pass under `output/runs/story158-docling-tier1-lane-r1/`, then rescored the
surviving candidate under `output/runs/story158-docling-parity-r4/`. The result
is materially negative for the remaining locally real Tier 1 seams on this
lane. Fresh evidence:
`image-default` and `image-ocrmac` both fail immediately on the raw Onward
source images with `ConversionError` because Pillow rejects the `302940000`
pixel pages as a decompression-bomb scale before usable output is emitted.
`image-smoldocling-transformers` does finish in `88.894s`, but the parity score
is only `15.0 / 100`, worse than the `16.9 / 100` PDF baseline and far behind
the `89.0 / 100` hybrid proof. Manual inspection of `merged.html` confirms the
failure shape: page 030 becomes a malformed late-family table starting around
`Yvette` / `Joe` / `Robert`, while page 031 degrades into a long flat paragraph
stream with no usable subgroup promotion. Optional backends
`rapidocr_onnxruntime` and `easyocr` are also absent in this runtime, so they
cannot be counted as honestly exercised Tier 1 seams in this pass. Net read:
current locally real official-only seams are materially exhausted on the Arthur
lane unless a new documented extension point appears; the measured next path is
Tier 2 generalization of the thin hybrid repair, not more random stock probing.
20260320-1543 — rescope-for-closeout applied: validation confirmed this story's
delivered slice is complete as a spike, but the remaining work belonged to a
separate follow-up. Broader Tier 2 hybrid generalization is now split into
Story 160 so this story can close on what it actually proved: bounded stock
`Docling` tuning, Tier 1 closure on the Arthur lane, and local thin-hybrid
feasibility on the Arthur failure slice. Next step: run close-out checks, then
mark Story 159 done if the repo-level status stays green.
20260320-1548 — mark-story-done closeout complete: full repo-level closeout
checks passed even though this story only touched spike scripts and research
docs. Fresh evidence: `python -m pytest tests/` passed with `353 passed,
12 warnings in 36.60s`, `python -m ruff check modules/ tests/` passed cleanly,
and `git diff --check` passed after the rescope split. Story 160 now tracks the
remaining Tier 2 generalization work, while this story closes on the delivered
spike slice: bounded stock sweep, thin-hybrid feasibility proof, Arthur-lane
parity surface, and Tier 1 closure on the Onward Arthur lane. Next step:
`/check-in-diff`.
