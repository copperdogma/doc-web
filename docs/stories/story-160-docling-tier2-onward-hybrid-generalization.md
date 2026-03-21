# Story 160 — Generalize Tier 2 `Docling` Hybrid Repair on the Onward Lane

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Fidelity to the source, Traceability is the Product, Dossier-ready output, Graduate, don't accumulate
**Spec Refs**: spec:2.1 C1 (Multi-Stage OCR Pipeline), spec:3.1 C3 (Heuristic + AI Layout Detection), spec:5.1 C7 (Page-Scope Extraction with Document-Level Consistency Planning), spec:6 (Validation, Provenance & Export), spec:7 (Graduation & Dossier Handoff)
**Build Map Refs**: spec:2 OCR & Text Extraction — substrate exists, `C1` climb; spec:3 Layout & Structure Understanding — substrate exists, `C3` climb; spec:5 Document Consistency Planning — substrate exists, `C7` climb; spec:6 Validation, Provenance & Export — provenance/export bar is active; spec:7 Graduation & Dossier Handoff — `doc-web` remains incumbent until a separate net-gain decision is earned; Input Coverage row `scanned-pdf-tables` remains the active hard-case lane; the Onward scanned genealogy simplification candidate block in `docs/build-map.md` remains the authoritative active workaround inventory and collapse proof bar
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

- [x] This story remains a spike and does not realign `docs/ideal.md`,
  `docs/spec.md`, or `docs/build-map.md`; `doc-web` remains the incumbent
  benchmark until a separate net-gain decision is justified
- [x] A generalized Tier 2 repair harness exists under `scripts/spikes/` that:
  - starts from stock `Docling` `baseline-images` artifacts, regenerating that
    baseline first if the prior Story 158 run roots are absent in the current
    shared `output/`
  - selects repair targets from inspectable signals instead of hard-coded Arthur
    page numbers, family labels, or one-off string matches
  - records a machine-readable repair plan/report under `output/runs/` with
    page or region targets, reason codes, source inputs, runtime, and output
    roots
- [x] A broader Onward run is executed and inspected manually, covering:
  - the Arthur lane that currently scores `89.0 / 100`
  - at least one later repeated-structure failure region outside the original
    two-page proof window
  - preserved provenance continuity at document/page/block level after repair
- [x] The story leaves a measured thinness decision backed by artifacts:
  - continue Tier 2 because the generalized layer still looks materially
    smaller than the current `doc-web` workaround stack
  - or stop / rethink because the layer is regrowing into document-specific or
    thick runtime logic
  - or reopen Tier 1 only if a newly surfaced documented official seam is
    specific enough to justify another official-only pass
  - explicitly map the result against the current Onward workaround stack in
    `docs/build-map.md` and name which layers would be deleted, narrowed,
    retained, or replaced if Tier 2 continues
- [x] The story updates ADR-003 research notes with the exact residual error
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

- [x] Freeze the Tier 2 generalization bar before coding:
  - define the broader Onward slice to run
  - define the repair-target signals that are allowed
  - define the thinness report fields that decide whether Tier 2 still looks
    small against the active Onward workaround stack named in
    `docs/build-map.md`
- [x] Re-establish the missing local Docling substrate for this story pass:
  - recreate a working isolated `Docling` runtime if the old Story 158 venv is
    absent
  - regenerate the minimum stock `baseline-images` artifacts needed for the
    broader pass if the prior `output/runs/story158-*` roots are absent
  - record the rebuilt runtime / artifact roots in the work log and findings
- [x] Implement a generalized repair harness under `scripts/spikes/`:
  - start from `baseline-images`
  - derive target pages or regions from measured signals
  - emit a machine-readable repair plan/report and reproducible output roots
- [x] Run the generalized hybrid pass and inspect artifacts manually:
  - Arthur lane parity rerun
  - at least one later repeated-structure failure region
  - provenance continuity and export/citation behavior after repair
- [x] Publish the result and update ADR-003 research notes:
  - continue Tier 2
  - or stop / rethink because the repair layer is regrowing
  - or reopen Tier 1 only if a genuinely new documented seam appears
  - include a file-level mapping against the current Onward workaround stack
    and candidate deletion / merge targets in `docs/build-map.md`
- [x] If this story changes the Onward simplification roadmap, active workaround
  inventory, candidate deletion / merge targets, or documented format coverage /
  graduation reality: update `docs/build-map.md` and record the before / after
  state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] If this remains script + research work: run targeted syntax/runtime checks for new scripts
  - [x] No shipped runtime surfaces changed, so story-scope `make test` was not required; close-out validation still ran `python -m pytest tests/`
  - [x] No shipped runtime surfaces changed, so story-scope `make lint` was not required; close-out validation still ran `python -m ruff check modules/ tests/`
  - [x] No maintained pipeline module changed; story-local spike commands produced fresh `output/runs/` artifacts that were inspected manually
  - [x] Agent tooling unchanged; `make skills-check` not required
- [x] Evals and goldens unchanged; `/improve-eval` and `docs/evals/registry.yaml` updates not required
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: repaired outputs still trace to source page/block and repair step
  - [x] T1 — AI-First: targeted rereads are used only where the measured signals justify them
  - [x] T2 — Eval Before Build: the generalized pass is judged against the existing parity surface and explicit thinness bar
  - [x] T3 — Fidelity: repeated-structure fixes are verified against reviewed Onward output, not inferred from logs
  - [x] T4 — Modular: targeting and repair stay reusable and do not hard-code book-specific values
  - [x] T5 — Inspect Artifacts: generated JSON/HTML/Markdown outputs are opened and checked manually

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: repo-local spike scripts and ADR research notes.
  This story should stay out of `modules/` and `doc_web/` unless the spike
  proves a much narrower production-worthy seam first.
- **Build-map reality**: the work still belongs to `spec:2`, `spec:3`, and
  `spec:5` `climb` seams, judged against the provenance/export and graduation
  bars in `spec:6` and `spec:7`. Thinness is not an abstract judgment here; it
  must be scored against the active workaround stack and simplification proof
  bar in the tracked Onward candidate block in `docs/build-map.md`. The
  relevant input-coverage lane remains `scanned-pdf-tables`.
- **Substrate evidence**: Story 158 pinned the local Onward hard-case corpus and
  verified the Onward source corpus under
  `/Users/cam/Documents/Projects/Onward to the Unknown Book Scan/`, including
  the processed page-image set and split-book PDFs. The original Story 158
  runtime and `output/runs/story158-*` artifacts referenced by prior docs are
  not present in this checkout anymore, so this story now includes the small
  coherent delta of recreating the isolated `Docling` runtime and regenerating
  the minimum `baseline-images` substrate before the broader Tier 2 pass can be
  run honestly.
- **Data contracts / schemas**: no pipeline schema changes are expected in the
  first pass. New machine-readable repair reports can live as story-local JSON
  or Markdown artifacts under `output/runs/` unless they cross a shared artifact
  boundary.
- **File sizes**: Story 159 and the ADR-003 findings surface are already large
  enough that new repair logic belongs in a dedicated spike script rather than
  ballooning prior story or decision docs further.
- **Decision context**: reviewed `docs/ideal.md`, the active build-map lanes for
  `spec:2` / `spec:3` / `spec:5` / `spec:6` / `spec:7`, ADR-003, ADR-001,
  Scout 011, Story 149, Story 158, and Story 159.

## Files to Modify

- `docs/stories/story-160-docling-tier2-onward-hybrid-generalization.md` — track the follow-up scope, acceptance bar, align notes, and work log
- `docs/stories/story-158-docling-doc-web-replacement-evaluation.md` — sync the umbrella keep / hybrid / replace evaluation if the broader Tier 2 result materially changes that read
- `docs/stories.md` — update Story 160 backlog metadata only if its index entry changes
- `scripts/spikes/docling_onward_hybrid_generalization.py` — generalized Tier 2 repair harness and plan/report emitter (new file)
- `scripts/spikes/docling_onward_parity_score.py` — extend or reuse the existing parity scorer only if broader-lane scoring needs a small shared hook
- `docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/onward-tuning-findings.md` — capture the generalized Tier 2 result and thinness mapping
- `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md` — update the Tier 2 read only if the broader pass materially changes it
- `docs/build-map.md` — update the tracked Onward simplification candidate block if this spike changes the active workaround inventory or the next collapse move

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
- Current result: the signal-driven Tier 2 path stays thin enough to continue.
  The new harness selects Arthur `[3, 4]` and Pierre `[4, 5, 6]` from stock
  `baseline-images` page/block signals, lifts the Arthur full candidate to
  `97.3 / 100` on the frozen lane, and restores the Pierre later spill to the
  incumbent chapter's coarse structure (`2` tables, `37` subgroup rows, `0`
  heading leaks). Remaining gaps are now explicitly narrower: Arthur still has
  later repeated-structure defects outside the repaired onset window, so this
  is not yet full Onward parity or a maintained production path.

## Plan

1. Freeze the generalization bar before coding.
   - Files: this story, ADR-003 findings note.
   - Change: name the broader slice, allowed signals, and thinness report,
     including the file-level mapping against the current Onward workaround
     stack in `docs/build-map.md`.
   - Done looks like: the story answers "what counts as still thin?" before any
     new repair code exists.

2. Rebuild the minimum local substrate this story depends on.
   - Files: story work log, `output/runs/story160-.../` bootstrap artifacts,
     isolated runtime notes.
   - Change: recreate the missing isolated `Docling` runtime and regenerate the
     stock `baseline-images` output needed for the generalized pass.
   - Done looks like: the broader-pass script can start from real current-pass
     `baseline-images` artifacts instead of dead Story 158 paths.

3. Implement the generalized Tier 2 harness.
   - Files: `scripts/spikes/docling_onward_hybrid_generalization.py`
   - Change: take stock `baseline-images` output plus source material, derive
     repair targets from signals, run bounded rereads, and emit a repair
     plan/report.
   - Done looks like: the script can rerun the broader pass without hard-coded
     Arthur page numbers.

4. Run the broader Onward pass and inspect artifacts.
   - Files: `output/runs/story160-.../`, parity summaries, ADR findings note.
   - Change: rerun Arthur parity, inspect at least one later repeated-structure
     region, and record provenance continuity plus remaining defects.
   - Done looks like: the artifact set proves whether the generalized layer
     still looks thin or is starting to sprawl.

5. Update the decision surface.
   - Files: ADR-003, findings note, Story 158, and possibly `docs/build-map.md`
     if the simplification roadmap changes.
   - Change: name whether Tier 2 remains the measured next path, whether a new
     Tier 1 seam earned reconsideration, or whether the spike should stop; sync
     the umbrella keep / hybrid / replace read and any changed deletion targets.
   - Done looks like: a reader can tell what to do next without replaying chat
     history.

## Work Log

20260320-1543 — story created: Story 159 closed the honest broad Tier 1 passes
and proved the two-page hybrid shape locally, but ADR-003 still has one open
question that belongs in a separate story: can that Tier 2 shape generalize
without regrowing into most of `doc-web`? This story tracks that follow-up
explicitly so Story 159 can close on the spike slice it actually delivered.
20260320-1607 — align pass tightened the story's methodology links before build
work starts. The thinness bar now has to map explicitly onto the tracked Onward
workaround stack in `docs/build-map.md`, the build-map update rule now covers
simplification-roadmap changes instead of only format-coverage drift, and the
story now names Story 158 as a downstream sync target so the umbrella keep /
hybrid / replace decision cannot close on Arthur-only evidence.
20260320-1616 — build-story exploration: verified the story is still aligned
with `spec:2`, `spec:3`, `spec:5`, the Onward simplification candidate block in
`docs/build-map.md`, and ADR-003's Tier 1 → Tier 2 decision ladder. Followed
the actual spike code in `scripts/spikes/docling_onward_hybrid_repair_proof.py`
and `scripts/spikes/docling_onward_parity_score.py`; the intended extension
seam is real. Critical substrate is only partial in this checkout: the Onward
source corpus still exists under `/Users/cam/Documents/Projects/Onward to the
Unknown Book Scan/`, but the old `.venv-story157-docling-arm64` runtime and the
referenced `output/runs/story157-*` / `story158-*` artifact roots are absent.
Small coherent scope delta folded into the story: recreate the isolated
`Docling` runtime and regenerate the minimum `baseline-images` substrate before
building the generalized pass. Files expected to change first: this story,
`docs/stories.md`, `scripts/spikes/docling_onward_hybrid_generalization.py`,
and fresh `output/runs/story160-.../` artifacts. Primary risk remains letting
Tier 2 regrow into the old workaround stack instead of proving a thinner seam.
20260320-1656 — generalized Tier 2 pass completed on a broader current-pass
slice. Recreated `.venv-story160-docling-arm64`, added the missing local
runtime deps (`pdf2image`, `pytesseract`, `httpx<0.28`) needed for the repo's
OpenAI/OCR helpers, and regenerated stock `baseline-images` artifacts for
Arthur and Pierre under `output/runs/story160-docling-baseline-arthur-r1/` and
`output/runs/story160-docling-baseline-pierre-r1/`. The new harness in
`scripts/spikes/docling_onward_hybrid_generalization.py` now derives target
pages from inspectable Docling page/block signals instead of hard-coded Arthur
page numbers: Arthur `[3, 4]` for the onset collapse, Pierre `[4, 5, 6]` for a
later repeated-structure spill. Manual artifact inspection confirmed the
generalized repairs on current-pass outputs. Arthur repaired excerpt
`output/runs/story160-docling-generalization-r1/arthur/merged-excerpt.html`
now contains a real opening genealogy table with clean subgroup rows such as
`ARTHUR'S FAMILY`, `DORILLA'S FAMILY`, `ALICE'S FAMILY`, `PAUL'S FAMILY`,
`YVETTE'S FAMILY`, `JOE'S FAMILY`, and `ROBERT'S FAMILY`. Arthur full candidate
`output/runs/story160-docling-generalization-r1/arthur/full-candidate.html`
removes the original onset collapse and scores `97.3 / 100` in
`output/runs/story160-docling-generalization-r1/arthur-parity/summary.json`
versus `22.1 / 100` for the regenerated stock baseline. The remaining Arthur
residuals are now outside the original proof window: later pages still leak
subgroup headings and miss `Joe's Grandchildren` / `MARIE'S FAMILY` in the
first 30-subgroup parity window. Pierre full candidate
`output/runs/story160-docling-generalization-r1/pierre/full-candidate.html`
restores the later `JACQUELINE'S FAMILY (adopted by Jack Cameron)` /
`Jacqueline's Grandchildren` / `DAVID'S FAMILY` / `JAMES' FAMILY` /
`ANTONIO'S FAMILY` sequence plus a separate descendants summary table
(`TOTAL DESCENDANTS 101`, `LIVING 95`, `DECEASED 6`). The repaired Pierre full
candidate now matches the incumbent reviewed chapter's coarse structure on the
tracked signals: `table_count 2`, `subgroup_row_count 37`,
`external_family_heading_count 0`, `residual_boygirl_header_count 0`. Thinness
read: continue Tier 2. The generalized layer is still materially smaller than
the active Onward workaround stack because it stays story-local, page-scoped,
and signal-driven. Current file-level mapping from this pass:
`table_rescue_onward_tables_v1` is the first plausible delete/replace target if
the shape graduates; `plan_onward_document_consistency_v1` plus
`rerun_onward_genealogy_consistency_v1` look more like future narrowing /
target-selection owners than full deletion candidates; and
`modules/common/onward_genealogy_html.py` with
`build_chapter_html_v1 --merge_contiguous_genealogy_tables` still looks like a
retained shared merge seam rather than a deletion candidate.
20260320-1812 — `/mark-story-done` close-out: Story 160 now closes as a
completed spike rather than remaining open-ended. Fresh close-out checks passed
on the current tree: `python -m pytest tests/` (`353 passed`) and
`python -m ruff check modules/ tests/` (`All checks passed!`). The story-local
artifact evidence remains the completion proof: regenerated stock baselines in
`output/runs/story160-docling-baseline-arthur-r1/` and
`output/runs/story160-docling-baseline-pierre-r1/`, generalized repairs in
`output/runs/story160-docling-generalization-r1/`, Arthur parity in
`output/runs/story160-docling-generalization-r1/arthur-parity/summary.json`,
and the synchronized decision surfaces in ADR-003 plus `docs/build-map.md`.
This story resolves ADR-003's immediate "does Tier 2 generalize at all?"
question enough to move the remaining work downstream to maintained-path
integration; it does not by itself make ADR-003 accepted. Next step:
`/check-in-diff`.
