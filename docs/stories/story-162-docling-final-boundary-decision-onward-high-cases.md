# Story 162 — Reach Final `Docling` Boundary Decision on Widened Onward Hard Cases

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Traceability is the Product, Fidelity to the source, Dossier-ready output, Graduate, don't accumulate
**Spec Refs**: spec:2.1 C1 (Multi-Stage OCR Pipeline), spec:3.1 C3 (Heuristic + AI Layout Detection), spec:5.1 C7 (Page-Scope Extraction with Document-Level Consistency Planning), spec:6 (Validation, Provenance & Export), spec:7 (Graduation & Dossier Handoff)
**Build Map Refs**: spec:2 OCR & Text Extraction — substrate exists, maintained `Docling` path now exists; spec:3 Layout & Structure Understanding — substrate exists, `Docling` repair seam remains active; spec:5 Document Consistency Planning — substrate exists, Onward simplification candidate block remains the decision scoreboard; spec:6 Validation, Provenance & Export — provenance/export bar still governs any replacement path; spec:7 Graduation & Dossier Handoff — `doc-web` remains the incumbent until a final net-gain decision is earned; Input Coverage row `scanned-pdf-tables` remains the decisive hard-case lane
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md`, `docs/decisions/adr-001-source-aware-consistency-strategy/adr.md`, `docs/stories/story-149-onward-scanned-genealogy-collapse-implementation.md`, `docs/stories/story-158-docling-doc-web-replacement-evaluation.md`, `docs/stories/story-159-docling-onward-tuning-sweep.md`, `docs/stories/story-160-docling-tier2-onward-hybrid-generalization.md`, `docs/stories/story-161-integrate-generalized-docling-hybrid-into-maintained-onward-path.md`, `docs/build-map.md`
**Depends On**: Story 149, Story 158, Story 159, Story 160, Story 161

## Goal

Finish the `Docling` boundary decision instead of extending the current chain of
exploratory follow-ups. This story should widen the maintained Tier 2 path past
the Arthur/Pierre slice, isolate or eliminate the surviving helper ownership
that still comes from the incumbent Onward workaround stack, and end with a
real ADR-level yes/no call: either accept `Docling` plus a thin maintained
wrapper as the forward replacement direction, or stop and keep `doc-web` as the
accepted boundary. The story should close the architectural question, not spawn
another proof-of-concept unless a genuinely new blocker is discovered.

## Acceptance Criteria

- [x] A widened maintained `driver.py` path exists and is run on the reviewed
  Onward hard-case slice that still defines the incumbent quality bar:
  `chapter-010.html`, `chapter-011.html`, `chapter-017.html`,
  `chapter-022.html`, and `chapter-023.html`, or an equally strong current-pass
  source-page equivalent grounded in the same reviewed slice.
- [x] The widened maintained path no longer depends opaquely on
  `table_rescue_onward_tables_v1` as a broad owner:
  - either the needed logic is extracted/narrowed into an explicitly small
    shared helper seam
  - or the story records, with file-level evidence, why that dependency keeps
    the `Docling` wrapper too thick to justify adopting
- [x] Manual artifact inspection plus fresh validation make the final decision
  unambiguous:
  - if `Docling` hybrid wins, the maintained path stays materially smaller than
    the incumbent Onward stack while preserving provenance/fidelity on the
    reviewed slice
  - if it loses, the story records that the wrapper regrows too much of the
    incumbent stack or misses too much of the hard-case bar
- [x] ADR-003 is updated from an open/discussing state to a final accepted
  architectural decision on this question:
  - accept `Docling` + thin wrapper as the forward boundary direction
  - or reject it for now and keep `doc-web` as the accepted boundary
  - the decision must name concrete supersession, retention, or demotion targets
    rather than leaving the question half-open
- [x] The story leaves the next repo move explicit and singular:
  - if `Docling` hybrid wins, create or name the migration / adoption story and
    the surfaces that are now candidates for replacement
  - if `doc-web` wins, explicitly close the active replacement question and
    demote `Docling` to benchmark/reference status unless a new documented seam
    appears

## Out of Scope

- Native Dossier or Storybook ingestion migration itself
- Broad new Tier 1 probing unless a concrete documented extension seam appears
  during execution and is strong enough to threaten the maintained wrapper path
- A long-lived `Docling` fork or invasive local patch stack
- Expanding the hard-case lane beyond what is needed to settle the boundary
  decision honestly
- Rewriting unrelated intake stories or non-Docling roadmap items

## Approach Evaluation

- **Simplification baseline**: a single LLM call cannot decide the boundary.
  The missing work is evidence-based: widen the maintained recipe on the
  reviewed Onward slice and measure whether the owned surface stays smaller than
  the incumbent workaround stack.
- **AI-only**: whole-chapter or whole-book rewrites remain non-credible for the
  final decision because they weaken provenance and make upgrade-cost claims
  meaningless.
- **Hybrid**: this is the leading candidate. The repo now has a real
  maintained recipe/module seam that proved itself on Arthur/Pierre, so the
  remaining question is whether widening that seam still stays materially
  smaller than the incumbent stack.
- **Plugin / internal extension**: admissible only if a concrete documented
  `Docling` extension seam appears that is meaningfully different from the
  already-tested official paths. Do not reopen speculative plugin work as a
  parallel branch just because it sounds cleaner.
- **Pure code / keep incumbent**: this is the control and fallback. If the
  widened wrapper regrows into too much of the current stack, the correct
  decision is to keep `doc-web`, not to rename the same ownership shape.
- **Repo constraints / prior decisions**: ADR-003 already says Tier 1 is mostly
  exhausted locally and Tier 2 is the measured default. Story 149 defines the
  reviewed Onward hard-case slice and simplification bar. Story 161 proves only
  the first maintained slice, not the final boundary call.
- **Existing patterns to reuse**: `configs/recipes/onward-docling-hybrid-maintained.yaml`,
  `modules/transform/repair_docling_onward_genealogy_v1/`,
  `configs/recipes/onward-genealogy-build-regression.yaml`,
  `modules/common/onward_genealogy_html.py`,
  `scripts/spikes/docling_onward_parity_score.py`, and the reviewed golden
  slice under `benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/`.
- **Eval**: the deciding eval is a widened maintained `driver.py` run plus
  manual inspection on the reviewed hard-case slice, combined with a file-level
  ownership map against the active workaround stack. Success is not just better
  HTML; it is a smaller owned surface with preserved provenance.

## Tasks

- [x] Freeze the final decision bar before implementation:
  - define the exact reviewed hard-case slice the widened maintained path must
    satisfy
  - define what counts as "materially smaller" than the incumbent stack
  - define the explicit accept / reject conditions that will let ADR-003 move
    to a final decision instead of another provisional note
- [x] Refactor or narrow the surviving helper ownership in the maintained seam:
  - inspect the current dependency on `table_rescue_onward_tables_v1`
  - extract a clearly bounded shared helper if needed
  - or prove with file-level evidence that this dependency makes the wrapper too
    thick to adopt
- [x] Widen the maintained `Docling` path on the reviewed Onward hard-case
  slice:
  - extend the maintained recipe/module seam beyond Arthur/Pierre
  - run through `driver.py`
  - emit inspectable artifacts and per-lane summaries under `output/runs/`
- [x] Inspect the widened artifacts manually and score the decision honestly:
  - verify provenance continuity and inspectability
  - verify no reopened fragmentation / subgroup / row-shape regressions on the
    reviewed slice
  - compare owned files/modules against the incumbent stack and record what
    would be deleted, narrowed, retained, or rejected
- [x] Publish the final boundary decision:
  - update ADR-003 and synthesis to an explicit final yes/no call
  - update `docs/build-map.md` and any direction docs that actually change
  - if the decision favors `Docling` hybrid, create or name the adoption story
  - if the decision favors `doc-web`, explicitly close the active replacement
    question
- [x] If this story changes documented format coverage or graduation reality:
  update `docs/build-map.md` and record the before/after state honestly
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
  - [x] T0 — Traceability: every output traces to source page, OCR engine,
    confidence, processing step
  - [x] T1 — AI-First: didn't write code for a problem AI solves better
  - [x] T2 — Eval Before Build: measured SOTA before building complex logic
  - [x] T3 — Fidelity: source content preserved faithfully, no silent losses
  - [x] T4 — Modular: new recipe not new code; no hardcoded book assumptions
  - [x] T5 — Inspect Artifacts: visually verified outputs, not just checked
    logs

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: maintained `Docling` recipe/module seam plus ADR/build-map direction docs. This story should settle the boundary question, not deepen random spike code.
- **Build-map reality**: this still belongs to `spec:2` / `spec:3` / `spec:5` climb work judged against the `spec:6` / `spec:7` provenance and graduation bar. The decisive input-coverage lane is still `scanned-pdf-tables`.
- **Substrate evidence**: verified current maintained seam exists in `configs/recipes/onward-docling-hybrid-maintained.yaml` and `modules/transform/repair_docling_onward_genealogy_v1/`. Verified incumbent reviewed slice and simplification baseline exist in Story 149 artifacts and `benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/`. Verified current open gap in `docs/build-map.md`: the maintained proof must widen and helper ownership must be narrowed before the final decision is honest.
- **Data contracts / schemas**: no new cross-project schema should be introduced unless the final decision favors a new adopted boundary. Story-level artifacts can remain local JSON/HTML/Markdown outputs under `output/runs/`.
- **File sizes**: `modules/transform/repair_docling_onward_genealogy_v1/main.py` is already a medium-sized maintained seam, `modules/adapter/table_rescue_onward_tables_v1/main.py` is a large incumbent owner, `docs/build-map.md` and ADR-003 are already large docs. This story should prefer extraction/narrowing and explicit ownership mapping over piling more code into large legacy files.
- **Decision context**: reviewed `docs/ideal.md`, `docs/build-map.md`, `docs/spec.md`, ADR-002, ADR-003, ADR-001, and Stories 149 / 158 / 159 / 160 / 161.

## Files to Modify

- `docs/stories/story-162-docling-final-boundary-decision-onward-high-cases.md` — final decision story scope, acceptance bar, and work log
- `configs/recipes/onward-docling-hybrid-maintained.yaml` — widen the maintained recipe across the reviewed hard-case slice
- `modules/transform/repair_docling_onward_genealogy_v1/main.py` — widen or narrow the maintained repair seam only as needed to settle the decision
- `modules/transform/repair_docling_onward_genealogy_v1/module.yaml` — update maintained seam contract if required
- `modules/adapter/table_rescue_onward_tables_v1/main.py` — extract/narrow retained helper ownership only if that is the cleanest way to judge thinness honestly
- `modules/common/onward_genealogy_html.py` — retain or extend only if the widened maintained seam still legitimately needs shared genealogy HTML assembly
- `tests/test_repair_docling_onward_genealogy_v1.py` — widen tests for the maintained seam
- `tests/test_table_rescue_onward_tables_v1.py` — guard any narrowed/extracted incumbent helper ownership
- `docs/build-map.md` — final simplification and decision update
- `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md` — move to the final architectural decision
- `docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/final-synthesis.md` — collapse the remaining ambiguity into the final recommended path
- `docs/stories.md` — track Story 162 status changes

## Redundancy / Removal Targets

- Further use of the 158→161 chain as a substitute for making the actual boundary decision
- Broad ownership in `table_rescue_onward_tables_v1` if the maintained `Docling` wrapper can absorb or isolate the needed seam honestly
- `doc-web` as the forward boundary direction if the widened maintained wrapper actually wins the decision
- The active `Docling` replacement track itself if the widened maintained proof shows the wrapper regrows into too much incumbent ownership

## Notes

- This story exists specifically to stop the incremental drift of "one more
  Docling story" without a final call.
- The expected result is a decision, not another provisional recommendation.
- If a genuinely new documented `Docling` extension seam appears during this
  work and is strong enough to matter, it can be folded into this story. Do not
  split it out unless it becomes materially distinct.

## Plan

1. Freeze the decision bar around the committed reviewed slice and current-pass
   source PDFs.
   Files: this story, `configs/recipes/onward-docling-hybrid-maintained.yaml`.
   The widened proof will stay anchored to the reviewed Story 149 slice:
   `chapter-010.html`, `chapter-011.html`, `chapter-017.html`,
   `chapter-022.html`, `chapter-023.html`, which map to the split-book source
   PDFs `05 ARTHUR`, `06 LEONIDAS`, `12 MARIE-LOUISE`, `17 PIERRE`, and
   `18 ANTOINE`. "Materially smaller" means the maintained `Docling` path may
   own one bounded repair module plus small shared OCR/HTML helpers, but it may
   not keep broad planner/rerun ownership or keep reaching into
   `table_rescue_onward_tables_v1` as a hidden upstream owner.

2. Extract the surviving shared OCR/HTML normalization seam out of
   `table_rescue_onward_tables_v1`.
   Files: `modules/adapter/table_rescue_onward_tables_v1/main.py`,
   `modules/common/onward_genealogy_html.py`, new common helper module(s),
   `modules/transform/repair_docling_onward_genealogy_v1/main.py`,
   focused tests.
   Current verified coupling is narrower than the whole rescue module:
   `_call_ocr`, `_normalize_rescue_html`, and
   `_normalize_rescue_html_for_chapter_merge` are the live cross-owner imports.
   Move that surface into an explicit small shared owner so the final thinness
   judgment is honest.

3. Generalize the maintained repair seam from narrow onset/spill repairs to the
   broader reviewed hard-case block.
   Files: `modules/transform/repair_docling_onward_genealogy_v1/main.py`,
   `modules/transform/repair_docling_onward_genealogy_v1/module.yaml`,
   `tests/test_repair_docling_onward_genealogy_v1.py`.
   Current-pass baselines show the same broader failure class on the missing
   hard cases:
   - Leonidas baseline (`story162-docling-baseline-leonidas-r1`):
     `table_heading_leak_count=54`, `combined_boy_girl_header_count=7`,
     `subgroup_row_count=0`, with the broken genealogy span covering the first
     table through the last table (`pages 2–8`).
   - Marie-Louise baseline (`story162-docling-baseline-marie-louise-r1`):
     `table_heading_leak_count=39`, `combined_boy_girl_header_count=4`,
     `subgroup_row_count=0`, with a wide leaky genealogy block on `pages 3–7`
     and a title-variant heading mismatch.
   - Antoine baseline (`story162-docling-baseline-antoine-r1`):
     `table_heading_leak_count=9`, `combined_boy_girl_header_count=1`,
     `subgroup_row_count=0`, with the full genealogy content effectively living
     in the first table page.
   Implementation plan: add one generalized broad-block profile that starts at
   the first suspicious genealogy table page, extends through the last
   suspicious genealogy page, and replaces the later genealogy section from the
   matched chapter heading onward. Loosen heading matching enough to treat
   punctuation-only title variants as the same chapter heading.

4. Widen the maintained recipe across the full reviewed slice and keep the
   repair selective.
   Files: `configs/recipes/onward-docling-hybrid-maintained.yaml`.
   Add maintained lanes for Leonidas, Marie-Louise, and Antoine while keeping
   Arthur and Pierre on their existing narrower profiles. Use the new current-
   pass baseline runs as the stock `Docling` substrate:
   `output/runs/story162-docling-baseline-leonidas-r1/`,
   `output/runs/story162-docling-baseline-marie-louise-r1/`,
   `output/runs/story162-docling-baseline-antoine-r1/`.

5. Validate on the real maintained path, inspect artifacts, then make the
   final decision.
   Files: output artifacts under `output/runs/`, `docs/build-map.md`,
   ADR-003, final synthesis, this story, `docs/stories.md`, and possibly a new
   adoption/follow-up story if `Docling` hybrid wins.
   Run focused tests first, then `make lint`, `make test`, then a real
   `driver.py` run of the widened maintained recipe. Manual review must confirm
   that the widened outputs preserve subgroup rows, split `BOY`/`GIRL` headers,
   and summary tables on the reviewed slice. The final ADR call will be:
   accept `Docling` hybrid only if the widened maintained seam stays clearly
   smaller than the incumbent stack after helper extraction; otherwise reject it
   and keep `doc-web` as the accepted boundary.

## Work Log

20260321-0018 — story created to absorb the remaining `Docling` yes/no work
after Stories 158–161. Current repo state already answers most of the earlier
gating questions: stock/config-only `Docling` is not enough, the thin hybrid
shape generalizes, and the first maintained path works on Arthur/Pierre. The
only open architectural question left in ADR-003 and the build map is whether
that maintained wrapper stays materially smaller when widened across the
reviewed Onward hard-case slice and separated from incumbent helper ownership.
This story is therefore intentionally decision-oriented and should end the
active boundary question instead of creating another provisional proof note.
20260321-0137 — build-story exploration completed and the story is honestly
build-ready. Re-read the Ideal/build-map/ADR context, traced the maintained
recipe/module seam, and verified the real remaining blocker is not missing
runtime substrate but missing widened proof plus hidden helper ownership.
Concrete substrate verified:
- maintained replacement path already exists in
  `configs/recipes/onward-docling-hybrid-maintained.yaml` and
  `modules/transform/repair_docling_onward_genealogy_v1/`
- the repair seam still imports `_call_ocr` and `_normalize_rescue_html` from
  `modules/adapter/table_rescue_onward_tables_v1/main.py`, and
  `modules/common/onward_genealogy_html.py` still imports
  `_normalize_rescue_html_for_chapter_merge` from the same incumbent module
- the reviewed hard-case slice maps cleanly onto real source PDFs under
  `/Users/cam/Documents/Projects/Onward to the Unknown Book Scan/Split Book/`:
  `05 ARTHUR`, `06 LEONIDAS`, `12 MARIE-LOUISE`, `17 PIERRE`, `18 ANTOINE`
- fresh stock `baseline-images` runs now exist for the previously missing
  widened lanes:
  `output/runs/story162-docling-baseline-leonidas-r1/`,
  `output/runs/story162-docling-baseline-marie-louise-r1/`,
  `output/runs/story162-docling-baseline-antoine-r1/`
Exploration result: Arthur/Pierre's narrow onset/spill profiles are not enough
for the final slice. Leonidas, Marie-Louise, and Antoine all show the same
broader failure class: `Docling` preserves intro narrative but emits the later
genealogy block as leaky tables with `BOY/GIRL` merges and subgroup headings
inside cells. Leonidas baseline summary from
`story162-docling-baseline-leonidas-r1` shows `54` table-heading leaks and `7`
combined `BOY/GIRL` headers; Marie-Louise shows `39` leaks and `4` combined
 headers; Antoine shows `9` leaks and `1` combined header. This means the
coherent next move is helper extraction plus one generalized broad-block repair
profile, not another story split or another Arthur-only lane. Next step: start
implementation, widen the maintained recipe, and re-run the widened
`driver.py` path.
20260321-0038 — widened maintained proof completed and the final boundary
decision is now evidence-backed instead of provisional. Fresh stock
`baseline-images` runs were generated for the missing reviewed lanes under
`output/runs/story162-docling-baseline-leonidas-r1/`,
`output/runs/story162-docling-baseline-marie-louise-r1/`, and
`output/runs/story162-docling-baseline-antoine-r1/`, which confirmed the same
broader late-genealogy failure class outside the Arthur/Pierre slice:
Leonidas baseline showed `54` heading leaks and `7` combined `BOY/GIRL`
headers, Marie-Louise showed `39` leaks and `4` combined headers, and Antoine
showed `9` leaks with `1` combined header. Implementation then extracted the
shared OpenAI vision OCR request path into
`modules/common/onward_openai_ocr.py`, rewired the rescue/rerun/maintained
repair modules to use that honest small helper seam, widened
`configs/recipes/onward-docling-hybrid-maintained.yaml` across the full
reviewed slice, and generalized
`modules/transform/repair_docling_onward_genealogy_v1/main.py` with one broad
genealogy-block profile plus punctuation-tolerant heading matching. Fresh
checks for the touched implementation passed: focused pytest `50 passed`,
`make lint` passed, `make test` passed (`361 passed, 12 warnings`), and the
real maintained run succeeded under
`output/runs/story162-docling-maintained-r1/`. Manual artifact inspection made
the final call clear: Arthur stayed strong, Pierre reached the reviewed target
shape, and Antoine came close but still kept the descendants summary inside the
main genealogy table (`1` table instead of the reviewed `2`). Leonidas and
Marie-Louise improved materially but still failed the reviewed bar:
Leonidas finished at `12` tables with `coarse_suspect=true`,
`external_family_heading_count=8`, and only `74` subgroup rows versus the
reviewed `104`; Marie-Louise finished at `4` tables with `17` residual heading
leaks, retained pre-genealogy name-list artifacts, and only `42` subgroup rows
versus the reviewed `73`. A direct local re-check through the retained
chapter-merge normalizer still did not materially rescue Leonidas or
Marie-Louise, which means the remaining gap does not come from one omitted
 merge knob. Story result: keep `doc-web` as the accepted boundary, demote the
 maintained `Docling` path to benchmark/reference status on this seam, and stop
 the active replacement track unless a materially different documented seam
 appears. Next step: `/validate`, then `/mark-story-done`.
20260321-0054 — close-out validation completed and the story is ready to land
as `Done`. Fresh validation evidence from this close-out pass: `git status
--short`, `git diff --stat`, and `git ls-files --others --exclude-standard`
reviewed the full local change set; `git diff --check` passed; `python -m ruff
check modules/ tests/` passed; `python -m pytest tests/` passed
(`361 passed, 12 warnings`); and the widened maintained proof plus manual lane
inspection were rechecked from `output/runs/story162-docling-maintained-r1/`.
Alignment read after the accepted ADR update: Ideal/spec/requirements remain
aligned, the build-map and ADR now agree that `doc-web` stays the accepted
boundary, no new eval registry entry is warranted, and no follow-up adoption
story should be created from this chain. Story-scope conclusion: all
acceptance criteria and tasks are satisfied, the final boundary question is now
closed on current-pass evidence, and the repo's next move is singular: keep
`doc-web` as the accepted Onward seam and treat the maintained `Docling` path
as benchmark/reference only unless a materially different documented seam
appears. Recommended next step: `/check-in-diff`.
