# Story 160 — Generalize Tier 2 `Docling` Hybrid Repair on the Onward Lane

**Priority**: High
**Status**: Pending
**Ideal Refs**: Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Fidelity to the source, Traceability is the Product, Dossier-ready output, Graduate, don't accumulate
**Spec Refs**: spec:2.1 C1 (Multi-Stage OCR Pipeline), spec:3.1 C3 (Heuristic + AI Layout Detection), spec:5.1 C7 (Page-Scope Extraction with Document-Level Consistency Planning), spec:6 (Validation, Provenance & Export), spec:7 (Graduation & Dossier Handoff)
**Build Map Refs**: spec:2 OCR & Text Extraction — substrate exists, `C1` climb; spec:3 Layout & Structure Understanding — substrate exists, `C3` climb; spec:5 Document Consistency Planning — substrate exists, `C7` climb; spec:6 Validation, Provenance & Export — provenance/export bar is active; spec:7 Graduation & Dossier Handoff — `doc-web` remains incumbent until a separate net-gain decision is earned; Input Coverage row `scanned-pdf-tables` remains the active hard-case lane
**Decision Refs**: `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md`, `docs/decisions/adr-001-source-aware-consistency-strategy/adr.md`, `docs/scout/scout-011-external-document-ingestion-systems.md`, `docs/stories/story-149-onward-scanned-genealogy-collapse-implementation.md`, `docs/stories/story-158-docling-doc-web-replacement-evaluation.md`, `docs/stories/story-159-docling-onward-tuning-sweep.md`
**Depends On**: Story 159

## Goal

Take the measured next step after Story 159: prove or falsify whether the
currently demonstrated Tier 2 hybrid shape can stay thin when generalized
beyond the Arthur two-page proof. The story should start from stock
`baseline-images` `Docling` output, replace hard-coded page targeting with
inspectable signals, run on a broader Onward slice, and leave an evidence-backed
answer to the only question ADR-003 still has open at Tier 2: does this remain
a small repair/adaptation layer worth pursuing, or does it start regrowing into
most of `doc-web`?

## Acceptance Criteria

- [ ] This story remains a spike and does not realign `docs/ideal.md`,
  `docs/spec.md`, or `docs/build-map.md`; `doc-web` remains the incumbent
  benchmark until a separate net-gain decision is justified
- [ ] A generalized Tier 2 repair harness exists under `scripts/spikes/` that:
  - starts from stock `Docling` `baseline-images` artifacts
  - selects repair targets from inspectable signals instead of hard-coded Arthur
    page numbers, family labels, or one-off string matches
  - records a machine-readable repair plan/report under `output/runs/` with
    page or region targets, reason codes, source inputs, runtime, and output
    roots
- [ ] A broader Onward run is executed and inspected manually, covering:
  - the Arthur lane that currently scores `89.0 / 100`
  - at least one later repeated-structure failure region outside the original
    two-page proof window
  - preserved provenance continuity at document/page/block level after repair
- [ ] The story leaves a measured thinness decision backed by artifacts:
  - continue Tier 2 because the generalized layer still looks materially
    smaller than the current `doc-web` workaround stack
  - or stop / rethink because the layer is regrowing into document-specific or
    thick runtime logic
  - or reopen Tier 1 only if a newly surfaced documented official seam is
    specific enough to justify another official-only pass
- [ ] The story updates ADR-003 research notes with the exact residual error
  classes, the generalized repair footprint, and the next recommended move

## Out of Scope

- Storybook or Dossier integration work
- Superseding ADR-002 or rewriting project-direction docs
- Claiming full Onward `100%` parity if the generalized pass still leaves later
  defects unresolved
- Maintaining a long-lived fork or invasive `Docling` patch stack
- Reopening broad stock `Docling` sweeps without a new specific documented
  Tier 1 seam

## Approach Evaluation

- **Simplification baseline**: Reuse Story 159's parity surface, `baseline-images`
  substrate, and thin hybrid proof before adding any new code. If a newly
  surfaced documented Tier 1 seam appears and can credibly threaten the current
  `89.0 / 100` Arthur control, test it first; otherwise treat Tier 1 as
  operationally exhausted on this lane.
- **AI-only**: A model could rewrite whole pages or chapters, but that would
  trade one-off improvement for weak control over provenance, repair targeting,
  and repeatability. It is not a credible Storybook-facing path by itself.
- **Hybrid**: Signal-driven target detection plus bounded OCR/reread/repair on
  top of stock `Docling` is the leading candidate because Story 159 already
  proved this shape locally on the Arthur onset and page-4 continuation slice.
- **Pure code**: Deterministic HTML/table rewriting without a reread signal is
  unlikely to recover collapsed content robustly enough for the remaining
  Onward defects.
- **Repo constraints / prior decisions**: ADR-003 now explicitly prefers the
  lowest-ownership path that reaches the bar. Story 159 already closed the
  honest broad Tier 1 probes in this environment and left the open question as
  Tier 2 thinness, not Tier 1 curiosity. Story 149 proves the repo can reach a
  very high Onward bar, which is useful as a quality benchmark but also a risk:
  this story must not quietly regrow that whole workaround stack.
- **Existing patterns to reuse**: `scripts/spikes/docling_onward_hybrid_repair_proof.py`,
  `scripts/spikes/docling_onward_parity_score.py`,
  `output/runs/story158-docling-tuning-r1/`,
  `output/runs/story158-docling-hybrid-proof-r1/`,
  `output/runs/story158-docling-parity-r4/`, and the incumbent reviewed Arthur
  lane in `benchmarks/golden/onward/arthur.html`.
- **Eval**: The distinguishing eval is still artifact-backed parity plus a
  thinness report. Success is not just a higher score; it is a higher score with
  bounded, inspectable ownership.

## Tasks

- [ ] Freeze the Tier 2 generalization bar before coding:
  - define the broader Onward slice to run
  - define the repair-target signals that are allowed
  - define the thinness report fields that decide whether Tier 2 still looks small
- [ ] Implement a generalized repair harness under `scripts/spikes/`:
  - start from `baseline-images`
  - derive target pages or regions from measured signals
  - emit a machine-readable repair plan/report and reproducible output roots
- [ ] Run the generalized hybrid pass and inspect artifacts manually:
  - Arthur lane parity rerun
  - at least one later repeated-structure failure region
  - provenance continuity and export/citation behavior after repair
- [ ] Publish the result and update ADR-003 research notes:
  - continue Tier 2
  - or stop / rethink because the repair layer is regrowing
  - or reopen Tier 1 only if a genuinely new documented seam appears
- [ ] If this story changes documented format coverage or graduation reality: update `docs/build-map.md` and record the before/after state honestly
- [ ] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [ ] Run required checks for touched scope:
  - [ ] If this remains script + research work: run targeted syntax/runtime checks for new scripts
  - [ ] If code touches shipped runtime surfaces: `make test`
  - [ ] If code touches shipped runtime surfaces: `make lint`
  - [ ] If pipeline behavior changes materially: clear stale `*.pyc`, run the selected local lane, verify artifacts in `output/runs/`, and manually inspect sample JSON/HTML/Markdown data
  - [ ] If agent tooling changes: `make skills-check`
- [ ] If evals or goldens change: run `/improve-eval` and update `docs/evals/registry.yaml`
- [ ] Search all docs and update any related to what we touched
- [ ] Verify Central Tenets:
  - [ ] T0 — Traceability: repaired outputs still trace to source page/block and repair step
  - [ ] T1 — AI-First: targeted rereads are used only where the measured signals justify them
  - [ ] T2 — Eval Before Build: the generalized pass is judged against the existing parity surface and explicit thinness bar
  - [ ] T3 — Fidelity: repeated-structure fixes are verified against reviewed Onward output, not inferred from logs
  - [ ] T4 — Modular: targeting and repair stay reusable and do not hard-code book-specific values
  - [ ] T5 — Inspect Artifacts: generated JSON/HTML/Markdown outputs are opened and checked manually

## Workflow Gates

- [ ] Build complete: implementation finished, required checks run, and summary shared
- [ ] Validation complete or explicitly skipped by user
- [ ] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: repo-local spike scripts and ADR research notes.
  This story should stay out of `modules/` and `doc_web/` unless the spike
  proves a much narrower production-worthy seam first.
- **Build-map reality**: the work still belongs to `spec:2`, `spec:3`, and
  `spec:5` `climb` seams, judged against the provenance/export and graduation
  bars in `spec:6` and `spec:7`. The relevant input-coverage lane remains
  `scanned-pdf-tables`.
- **Substrate evidence**: Story 158 pinned the local Onward hard-case corpus and
  verified the arm64 `Docling 2.80.0` runtime in `.venv-story157-docling-arm64`.
  Story 159 then produced the stock `baseline-images` substrate in
  `output/runs/story158-docling-tuning-r1/`, the local two-page hybrid proof in
  `output/runs/story158-docling-hybrid-proof-r1/`, and Arthur-lane parity
  evidence in `output/runs/story158-docling-parity-r4/`.
- **Data contracts / schemas**: no pipeline schema changes are expected in the
  first pass. New machine-readable repair reports can live as story-local JSON
  or Markdown artifacts under `output/runs/` unless they cross a shared artifact
  boundary.
- **File sizes**: `docs/stories/story-159-docling-onward-tuning-sweep.md` is
  `529` lines, `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md`
  is `200` lines, `docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/onward-tuning-findings.md`
  is `351` lines, and `docs/stories.md` is `167` lines. Keep new repair logic
  in a new spike script rather than making Story 159 or ADR-003 balloon further.
- **Decision context**: reviewed `docs/ideal.md`, the active build-map lanes for
  `spec:2` / `spec:3` / `spec:5` / `spec:6` / `spec:7`, ADR-003, ADR-001,
  Scout 011, Story 149, Story 158, and Story 159.

## Files to Modify

- `docs/stories/story-160-docling-tier2-onward-hybrid-generalization.md` — track the follow-up scope, acceptance bar, and work log (new file)
- `docs/stories.md` — add Story 160 to the index (`167` lines)
- `scripts/spikes/docling_onward_hybrid_generalization.py` — generalized Tier 2 repair harness and plan/report emitter (new file)
- `scripts/spikes/docling_onward_parity_score.py` — extend or reuse the parity scorer only if broader-lane scoring needs a small shared hook (new file in current worktree)
- `docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/onward-tuning-findings.md` — capture the generalized Tier 2 result (`351` lines)
- `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md` — update the Tier 2 read only if the broader pass materially changes it (`200` lines)

## Redundancy / Removal Targets

- Hard-coded page targeting inside the current two-page proof if signal-driven
  targeting succeeds
- Any ad hoc manual splice steps or one-off rescue fragments that the
  generalized harness supersedes
- The whole Tier 2 path itself if the broader pass shows the repair layer is
  regrowing into thick document-specific logic

## Notes

- The current Arthur control is `89.0 / 100`, not `100`, so this story should
  not pretend the only possible success is total parity. The real question is
  whether the next gains stay cheap enough to justify continuing Tier 2.
- `Story 159` already established that official broad Tier 1 probes in this
  environment are not currently threatening the hybrid path. Do not reopen broad
  stock sweeps here unless a specific documented seam is surfaced first.
- Preserve provenance as first-class output. Even if repaired structure changes,
  Storybook still needs document/page/block traceability from the underlying
  `Docling` substrate.

## Plan

1. Freeze the generalization bar before coding.
   - Files: this story, ADR-003 findings note.
   - Change: name the broader slice, allowed signals, and thinness report.
   - Done looks like: the story answers "what counts as still thin?" before any
     new repair code exists.

2. Implement the generalized Tier 2 harness.
   - Files: `scripts/spikes/docling_onward_hybrid_generalization.py`
   - Change: take stock `baseline-images` output plus source material, derive
     repair targets from signals, run bounded rereads, and emit a repair
     plan/report.
   - Done looks like: the script can rerun the broader pass without hard-coded
     Arthur page numbers.

3. Run the broader Onward pass and inspect artifacts.
   - Files: `output/runs/story160-.../`, parity summaries, ADR findings note.
   - Change: rerun Arthur parity, inspect at least one later repeated-structure
     region, and record provenance continuity plus remaining defects.
   - Done looks like: the artifact set proves whether the generalized layer
     still looks thin or is starting to sprawl.

4. Update the decision surface.
   - Files: ADR-003, findings note, possibly follow-up docs if warranted.
   - Change: name whether Tier 2 remains the measured next path, whether a new
     Tier 1 seam earned reconsideration, or whether the spike should stop.
   - Done looks like: a reader can tell what to do next without replaying chat
     history.

## Work Log

20260320-1543 — story created: Story 159 closed the honest broad Tier 1 passes
and proved the two-page hybrid shape locally, but ADR-003 still has one open
question that belongs in a separate story: can that Tier 2 shape generalize
without regrowing into most of `doc-web`? This story tracks that follow-up
explicitly so Story 159 can close on the spike slice it actually delivered.
