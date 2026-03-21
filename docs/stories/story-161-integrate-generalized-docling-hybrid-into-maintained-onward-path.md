# Story 161 — Integrate Generalized `Docling` Hybrid into a Maintained Onward Path

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Traceability is the Product, Fidelity to the source, Dossier-ready output, Graduate, don't accumulate
**Spec Refs**: spec:2.1 C1 (Multi-Stage OCR Pipeline), spec:3.1 C3 (Heuristic + AI Layout Detection), spec:5.1 C7 (Page-Scope Extraction with Document-Level Consistency Planning), spec:6 (Validation, Provenance & Export), spec:7 (Graduation & Dossier Handoff)
**Build Map Refs**: spec:2 OCR & Text Extraction — substrate exists, maintained `Docling` path missing; spec:3 Layout & Structure Understanding — substrate exists, `Docling` table/onset repair remains an active seam; spec:5 Document Consistency Planning — substrate exists, Onward simplification candidate block remains active; spec:6 Validation, Provenance & Export — provenance/export bar still governs any replacement path; spec:7 Graduation & Dossier Handoff — `doc-web` remains the incumbent until a maintained path proves net gain; Input Coverage row `scanned-pdf-tables` remains the hard-case lane
**Decision Refs**: `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md`, `docs/decisions/adr-001-source-aware-consistency-strategy/adr.md`, `docs/stories/story-149-onward-scanned-genealogy-collapse-implementation.md`, `docs/stories/story-158-docling-doc-web-replacement-evaluation.md`, `docs/stories/story-160-docling-tier2-onward-hybrid-generalization.md`, `docs/build-map.md`
**Depends On**: Story 149, Story 160

## Goal

Translate Story 160's signal-driven Tier 2 `Docling` hybrid from a story-local
spike into a real maintained `driver.py` path, or explicitly prove that such a
path regrows into too much of the current Onward workaround stack. This story
should keep `doc-web` as the incumbent boundary until the maintained path earns
more, but it must answer the next real simplification question with artifacts:
can the generalized `Docling` repair shape replace enough of the current
Onward stack on a maintained path to justify continuing toward `hybrid`?

## Acceptance Criteria

- [x] A maintained `driver.py` lane or clearly named replacement path exists
  under `configs/recipes/` and `modules/` that reuses stock `Docling`
  `baseline-images` output plus a bounded repair seam instead of relying on
  Story 160's standalone spike script.
- [x] A real run on that maintained or clearly proposed path produces artifacts
  in `output/runs/` for the Arthur onset lane and the Pierre later-spill lane,
  and manual inspection confirms that the key Story 160 repaired structures
  survive:
  - Arthur opening genealogy table recovers subgroup rows rather than flattened
    prose
  - Pierre retains the recovered `JACQUELINE'S FAMILY` through `ANTONIO'S
    FAMILY` sequence plus the descendants summary table
  - provenance and inspectability remain explicit at the repaired page/block
    seam
- [x] The story leaves a file-level simplification proof against the active
  Onward workaround stack in `docs/build-map.md`, naming which layers are now:
  - ready for deletion
  - ready only for narrowing
  - still required
  - or not honestly replaceable by the maintained `Docling` path
- [x] ADR-003 and the Onward build-map candidate block are updated with the
  maintained-path result:
  - continue `hybrid` if the maintained shape stays materially smaller than the
    incumbent stack
  - or demote `hybrid` and keep `doc-web` as the accepted boundary if the
    maintained path regrows too much ownership or loses provenance/fidelity

## Out of Scope

- Native `DoclingDocument` ingestion in Dossier
- Broad new Tier 1 seam hunting unless a specific documented extension point
  surfaces during implementation
- Claiming full Onward `100%` parity if the maintained path still leaves later
  residual defects
- Maintaining a long-lived `Docling` fork or large local patch stack
- Rewriting `docs/spec.md`, `docs/requirements.md`, or the `doc-web` handoff
  docs unless the maintained-path result actually changes accepted direction

## Approach Evaluation

- **Simplification baseline**: first test the cheapest maintained form of the
  existing generalized shape. That likely means importing or regenerating stock
  `Docling` `baseline-images` artifacts inside a recipe and applying a bounded
  repair stage, not rebuilding Story 160 as a second standalone script path.
- **AI-only**: a model could rewrite whole chapters, but that would weaken
  provenance, repair targeting, and replayability. It is not credible as a
  maintained Dossier-facing seam.
- **Hybrid**: recipe-driven reuse of stock `Docling` output plus bounded target
  selection and reread/repair remains the leading candidate because Story 160
  already proved the shape on Arthur and Pierre.
- **Pure code**: deterministic HTML rewriting without a reread step is unlikely
  to preserve the recovered structures on the hard cases unless the baseline
  `Docling` output improves materially.
- **Repo constraints / prior decisions**: ADR-003 currently recommends
  `hybrid` first but keeps `doc-web` as the incumbent until a maintained-path
  proof exists. Story 149 defines the active simplification proof bar for the
  Onward workaround stack. ADR-001 keeps direct HTML as the default repair
  target unless a stronger structure-preserving seam is proven.
- **Existing patterns to reuse**: `modules/common/load_artifact_v1`,
  `modules/common/onward_genealogy_html.py`,
  `configs/recipes/onward-genealogy-build-regression.yaml`,
  `scripts/spikes/docling_onward_tuning_sweep.py`,
  `scripts/spikes/docling_onward_hybrid_generalization.py`, and the Story 149
  maintained regression lane.
- **Eval**: the deciding evidence is a real maintained run plus manual
  inspection on Arthur and Pierre, backed by the existing Arthur parity surface
  and a file-level thinness map against the active workaround stack.

## Tasks

- [x] Freeze the maintained-path entry seam before coding:
  - decide whether the first maintained slice reuses prebuilt `Docling`
    baseline artifacts via `load_artifact_v1`, regenerates them through a thin
    wrapper stage, or does both behind one explicit recipe contract
  - define what still counts as "thin enough" against the current Onward
    workaround stack before building new modules
- [x] Implement the maintained `Docling` hybrid path under `modules/` and
  `configs/recipes/`:
  - create the minimal module or modules needed to import/regenerate stock
    `Docling` output
  - create the bounded repair stage that carries the Story 160 targeting logic
    without hard-coded family-name branching
  - emit inspectable repair-plan / summary artifacts under `output/runs/`
- [x] Run the maintained path through `driver.py` and inspect artifacts
  manually:
  - Arthur onset lane
  - Pierre later repeated-structure spill
  - repaired-page provenance / inspectability artifacts
- [x] Publish the simplification result:
  - update ADR-003 and `docs/build-map.md` with the maintained-path read
  - name deletion, narrowing, retention, or rejection targets in the active
    Onward workaround stack
  - if the maintained path fails thinness or fidelity, record that explicitly
    and stop instead of stretching the layer further
- [x] If this story changes documented graduation reality: update
  `docs/build-map.md`, `docs/spec.md`, `docs/requirements.md`, and any handoff
  docs with the before/after state honestly (the maintained-path result changed
  the build-map / ADR direction surfaces but did not earn a spec, requirements,
  or handoff change)
- [x] Check whether the chosen implementation makes any existing code, helper
  paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through
    `driver.py`, verify artifacts in `output/runs/`, and manually inspect
    sample JSON/HTML/Markdown data
  - [x] If agent tooling changed: `make skills-check` (not needed; agent tooling unchanged)
- [x] If evals or goldens changed: run `/improve-eval` and update
  `docs/evals/registry.yaml` (not needed; no eval or golden files changed)
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: the maintained path preserves inspectable source
    page/block ownership for repaired content
  - [x] T1 — AI-First: rereads stay bounded to measured failure pages rather
    than expanding deterministic workaround code first
  - [x] T2 — Eval Before Build: the maintained path is judged against Story
    160's artifact bar and the active simplification map, not vibes
  - [x] T3 — Fidelity: repaired Arthur and Pierre structures match reviewed
    incumbent output closely enough to justify the simplification claim
  - [x] T4 — Modular: the maintained path adds a reusable seam rather than a
    second story-local runtime
  - [x] T5 — Inspect Artifacts: final `output/runs/` HTML/JSON artifacts are
    opened and checked manually

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: new maintained extract/adapter recipe seams plus
  Onward simplification documentation. This story should create the minimum
  real module/recipe surface needed to replace the spike path, not deepen
  `doc_web/`.
- **Build-map reality**: this is still `spec:2` / `spec:3` / `spec:5` climb
  work judged against the active provenance/export and graduation bar in
  `spec:6` / `spec:7`. The Onward candidate block remains the simplification
  scoreboard.
- **Substrate evidence**: verified reusable substrate exists in
  `modules/common/load_artifact_v1/main.py`,
  `modules/common/onward_genealogy_html.py`,
  `configs/recipes/onward-genealogy-build-regression.yaml`, the current recipe
  / driver framework, and the fresh Story 160 artifacts under
  `output/runs/story160-docling-generalization-r1/`. Missing substrate is the
  maintained `Docling` integration seam itself; that is the point of this
  story.
- **Data contracts / schemas**: no shared schema change should be introduced
  unless a new cross-stage artifact becomes part of the maintained path. If new
  fields cross stage boundaries, update `schemas.py` before relying on them.
- **File sizes**: `modules/common/load_artifact_v1/main.py` is 124 lines,
  `modules/common/onward_genealogy_html.py` is 506 lines,
  `scripts/spikes/docling_onward_hybrid_generalization.py` is 863 lines,
  `scripts/spikes/docling_onward_tuning_sweep.py` is 424 lines,
  `configs/recipes/onward-genealogy-build-regression.yaml` is 63 lines,
  `docs/build-map.md` is 476 lines, and ADR-003 is 228 lines. The size risk is
  to accidentally turn the spike script into a second runtime instead of
  extracting only the reusable seam.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`,
  `docs/build-map.md`, ADR-003, ADR-001, Story 149, Story 158, and Story 160.

## Files to Modify

- `docs/stories/story-161-integrate-generalized-docling-hybrid-into-maintained-onward-path.md` — track the maintained-path proof scope and work log (new file)
- `modules/common/load_artifact_v1/main.py` — extend only if artifact reuse needs a small generic seam (124 lines)
- `modules/common/onward_genealogy_html.py` — reuse retained genealogy merge/stitch logic if the maintained path still needs it (506 lines)
- `configs/recipes/onward-genealogy-build-regression.yaml` — update or derive the maintained regression lane if it becomes the comparison baseline (63 lines)
- `configs/recipes/onward-docling-hybrid-maintained.yaml` — maintained recipe for the new `Docling` hybrid path (new file)
- `modules/transform/repair_docling_onward_genealogy_v1/main.py` — bounded maintained repair seam derived from Story 160 signals (new file)
- `modules/transform/repair_docling_onward_genealogy_v1/module.yaml` — maintained transform-module contract for the repair seam (new file)
- `tests/test_load_artifact_v1.py` — guard any generic artifact-reuse extension (existing file)
- `tests/test_repair_docling_onward_genealogy_v1.py` — focused tests for the maintained repair seam (new file)
- `docs/build-map.md` — update the Onward simplification candidate block with the maintained-path result (476 lines)
- `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md` — update the recommendation once the maintained-path result exists (228 lines)

## Redundancy / Removal Targets

- Story 160's standalone hybrid spike path if a maintained recipe replaces it
- `table_rescue_onward_tables_v1` if the maintained `Docling` path can absorb
  that responsibility honestly
- Planner/rerun layers that become targeting-only helpers instead of full
  workaround owners
- Any temporary recipe/module seam that recreates a second permanent runtime
  instead of tightening the existing Onward simplification path

## Notes

- This story is where the current `hybrid` recommendation either becomes a real
  maintained path or gets demoted.
- `doc-web` remains the incumbent Dossier-facing boundary unless this story
  proves a smaller maintained ownership shape with preserved provenance and
  fidelity.
- Story 160 already answered the "does Tier 2 generalize at all?" question.
  This story owns the next one: "does the generalized shape survive contact
  with a maintained path?"

## Plan

1. Freeze the maintained seam around existing substrate, not a new runtime.
   Files: `modules/common/load_artifact_v1/main.py`, `driver.py`,
   `configs/recipes/onward-docling-hybrid-maintained.yaml`,
   `modules/transform/repair_docling_onward_genealogy_v1/`.
   Approach: reuse `load_artifact_v1` to copy Story 160 baseline summary/html/json
   plus sibling `images/`, then run one generic `transform` stage per lane using
   driver-managed named artifact inputs (`--baseline-summary`, `--baseline-html`,
   `--baseline-json`). Do not add a second extract/import runtime unless the
   existing recipe contract proves insufficient.
   Done when: Arthur and Pierre can be invoked from one maintained recipe with no
   story-local script entrypoint.

2. Extract only the reusable repair seam from the Story 160 spike.
   Files: `modules/transform/repair_docling_onward_genealogy_v1/main.py`,
   `modules/transform/repair_docling_onward_genealogy_v1/module.yaml`,
   `tests/test_repair_docling_onward_genealogy_v1.py`.
   Approach: keep signal scan, target-page selection, bounded reread, merge, and
   HTML replacement logic; drop sweep/report code that only exists to support the
   one-off spike. Emit inspectable side artifacts (`page-signals.json`,
   `page-XXX-{clue,raw,clean}.html`, `merged-excerpt.html`, `full-candidate.html`,
   `summary.json`, `summary.md`) so provenance and manual review stay explicit.
   Structural risk: this module can easily regrow into a second runtime if it
   absorbs baseline generation or wider Onward planner ownership. Keep it lane-
   bounded and recipe-driven.
   Done when: focused tests cover target-page selection and the two replacement
   modes, and the module interface matches the recipe/driver contract cleanly.

3. Prove the maintained path through `driver.py` with fresh artifacts.
   Files: `configs/recipes/onward-docling-hybrid-maintained.yaml`,
   `output/runs/story161-docling-maintained-r1/...`.
   Approach: run the new recipe against the Arthur onset lane and Pierre later-
   spill lane, then manually open the produced HTML/JSON/Markdown artifacts to
   verify the repaired structures from Story 160 survive on the maintained path.
   Impact/risk: this is the story's real acceptance bar; unit tests alone do not
   answer the maintained-path question.
   Done when: Arthur regains subgroup rows in the opening table, Pierre preserves
   the `JACQUELINE'S FAMILY` through `ANTONIO'S FAMILY` sequence plus descendants
   summary, and the lane summaries show explicit target-page provenance.

4. Publish the simplification read honestly.
   Files: `docs/build-map.md`,
   `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md`,
   `docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/final-synthesis.md`,
   `docs/stories/story-161-integrate-generalized-docling-hybrid-into-maintained-onward-path.md`.
   Approach: compare the maintained path against the active Onward workaround
   stack at file level. Name what is ready for deletion, ready only for narrowing,
   still required, or not honestly replaceable. If the maintained path regrows too
   much ownership, record that and stop instead of stretching the layer further.
   Done when: ADR-003 and the build-map candidate block say whether `hybrid`
   continues or is demoted, with concrete file targets instead of prose-only
   optimism.

5. Validate touched scope with the repo's normal gates.
   Files: touched module/tests/docs plus the Story 161 work log.
   Checks: focused pytest first, then default `make test` and `make lint`; if the
   maintained recipe works, clear stale `*.pyc`, run `driver.py`, and inspect final
   artifacts manually before claiming success.
   Done when: the story stays `In Progress` with `Build complete` checked and fresh
   evidence recorded for the next `/validate` or `/mark-story-done` pass.

## Work Log

20260320-1834 — follow-up story created during Story 158 close-out. Story 158
produced the evaluation package and a formal `hybrid`-first recommendation, but
it should not also own the maintained-path proof needed to justify deleting or
narrowing the current Onward workaround stack. Verified substrate before
promoting this story to `Pending`: the repo already has the `driver.py` recipe
system, artifact-reuse seam `modules/common/load_artifact_v1/main.py`, retained
genealogy merge helper `modules/common/onward_genealogy_html.py`, the current
Onward maintained regression recipe, and the fresh Story 160 Arthur/Pierre
artifacts. Missing substrate is the maintained `Docling` integration seam
itself, which is the point of this story rather than a blocker to its build
readiness. Next step: `/build-story 161`.

20260320-1924 — `/build-story` exploration completed and story promoted to `In Progress`.
Re-checked Ideal/spec/build-map/ADR alignment before coding and confirmed the
smallest honest maintained seam is one recipe plus one `transform` module, not a
new baseline-import runtime. Verified `driver.py` already passes named artifact
inputs to `transform` stages, so `load_artifact_v1` can copy Story 160 baseline
summary/html/json artifacts and sibling `images/` into the run while the new
module consumes them as `--baseline-summary`, `--baseline-html`, and
`--baseline-json`. Files expected to change: Story 161, `docs/stories.md`,
`configs/recipes/onward-docling-hybrid-maintained.yaml`,
`modules/transform/repair_docling_onward_genealogy_v1/`, focused tests, and
result docs (`docs/build-map.md`, ADR-003, synthesis) once the maintained run is
proven. Risk to avoid: turning the 160 spike into a second permanent runtime
instead of a bounded repair seam. Next step: tighten the new module/recipe/tests,
run focused checks, then prove the path through `driver.py`.

20260320-2349 — maintained-path proof landed and the methodology docs were updated to match. Implemented the maintained seam in `configs/recipes/onward-docling-hybrid-maintained.yaml` plus `modules/transform/repair_docling_onward_genealogy_v1/`, with focused tests in `tests/test_repair_docling_onward_genealogy_v1.py`. First runtime attempt exposed a real seam-specific issue: `gpt-5` over-reasoned on the Arthur reread just as the earlier research notes warned, so the maintained path was tightened to explicit `gpt-4.1` recipe settings and per-page progress logging before re-running. Fresh checks: focused pytest `5 passed`, `make lint` passed, `make test` passed (`358 passed`), and `driver.py` succeeded on `output/runs/story161-docling-maintained-r2/`. Manual artifact review: Arthur lane summary at `output/runs/story161-docling-maintained-r2/07_repair_docling_onward_genealogy_v1/summary.json` shows target pages `[3, 4]`, `pretable_paragraph_count: 3 -> 0`, `subgroup_row_count: 0 -> 28`, and explicit page/image/request/ref provenance; `output/runs/story161-docling-arthur-parity-r1/summary.json` keeps Arthur at `97.3 / 100` on the frozen parity lane. Pierre lane summary at `output/runs/story161-docling-maintained-r2/08_repair_docling_onward_genealogy_v1/summary.json` shows target pages `[4, 5, 6]`, `table_heading_leak_count: 18 -> 2`, `combined_boy_girl_header_count: 2 -> 0`, `subgroup_row_count: 0 -> 36`, and `coarse_suspect: false`; manual HTML inspection of `output/runs/story161-docling-maintained-r2/08_repair_docling_onward_genealogy_v1/full-candidate.html` confirmed the recovered `JACQUELINE'S FAMILY` through `ANTONIO'S FAMILY` sequence plus the descendants summary table (`TOTAL DESCENDANTS 101`, `LIVING 95`, `DECEASED 6`). Simplification read recorded in `docs/build-map.md` and ADR-003: continue `hybrid`, but treat `table_rescue_onward_tables_v1` and the planner/rerun stack as narrowing targets rather than claiming broad deletions yet. Next step: `/validate`, then `/mark-story-done` or widen the maintained slice if the user wants the next simplification move.
20260321-0008 — close-out validation completed and the story is ready to land as `Done`. Fresh validation evidence from this close-out pass: `git status --short`, `git diff --stat`, and `git ls-files --others --exclude-standard` reviewed the full local change set; `make lint` passed; `make test` passed (`358 passed, 12 warnings`); `git diff --check` passed; and the maintained `driver.py` proof plus manual artifact reads were rechecked from `output/runs/story161-docling-maintained-r2/` and `output/runs/story161-docling-arthur-parity-r1/`. Story-scope conclusion: all acceptance criteria and tasks are satisfied, no eval/golden or agent-tooling follow-up was required, and the story delivered a coherent maintained-path proof rather than a partial slice. Recommended next step: `/check-in-diff`.
