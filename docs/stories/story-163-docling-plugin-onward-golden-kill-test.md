# Story 163 — Probe Coordinated Official `Docling` Plugin Paths Against the Onward 100% Golden Bar

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Traceability is the Product, Fidelity to the source, Dossier-ready output, Graduate, don't accumulate
**Spec Refs**: spec:2.1 C1 (Multi-Stage OCR Pipeline), spec:3.1 C3 (Heuristic + AI Layout Detection), spec:5.1 C7 (Page-Scope Extraction with Document-Level Consistency Planning), spec:6 (Validation, Provenance & Export), spec:7 (Graduation & Dossier Handoff)
**Build Map Refs**: spec:2 OCR & Text Extraction — active `scanned-pdf-tables` climb; spec:3 Layout & Structure Understanding — active climb on repeated-structure genealogy failures; spec:5 Document Consistency Planning — Onward simplification candidate block remains the incumbent scoreboard; spec:6 Validation, Provenance & Export — provenance/export bar still governs any reopened `Docling` work; spec:7 Graduation & Dossier Handoff — `doc-web` remains the accepted boundary unless a materially different official seam earns reopening
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md`, `docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/final-synthesis.md`, `docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/onward-tuning-findings.md`, `docs/stories/story-149-onward-scanned-genealogy-collapse-implementation.md`, `docs/stories/story-158-docling-doc-web-replacement-evaluation.md`, `docs/stories/story-159-docling-onward-tuning-sweep.md`, `docs/stories/story-160-docling-tier2-onward-hybrid-generalization.md`, `docs/stories/story-161-integrate-generalized-docling-hybrid-into-maintained-onward-path.md`, `docs/stories/story-162-docling-final-boundary-decision-onward-high-cases.md`, `docs/build-map.md`
**Depends On**: Story 149, Story 158, Story 159, Story 160, Story 161, Story 162

## Goal

Test whether a coordinated set of official `Docling` plugin seams is the
“materially different documented official seam” that ADR-003 says would justify
reopening the closed replacement question on the Onward genealogy hard case.
The story should not assume plugins win. It should identify the exact plugin
families most likely to move the Leonidas / Marie-Louise failure class, prove
local plugin registration through `Docling`'s official
`allow_external_plugins` path without patching `Docling` source, and run a
kill test against the reviewed Onward golden bar. The outcome must still be
singular: either an official plugin stack materially threatens the incumbent
and earns a follow-on adoption story, or the repo records that even the
broader coordinated plugin path does not justify reopening the accepted
`doc-web` boundary.

## Acceptance Criteria

- [x] The exact official plugin seam to test is pinned with current-pass
  evidence:
  - the story names the `Docling` plugin family (OCR, layout, table structure,
    picture description, serializer, or another documented official seam)
  - records why that seam is the strongest hypothesis for the Leonidas /
    Marie-Louise failure class
  - records the exact local runtime / venv / commands needed to exercise it
- [x] A minimal repo-owned plugin harness or plugin package is exercised
  through official `Docling` plugin registration without patching or forking
  `Docling` source, and produces inspectable artifacts on at least one real
  Onward lane
- [x] The plugin kill test is run against the reviewed failure lanes that kept
  `doc-web` as the accepted boundary:
  - Leonidas and Marie-Louise are mandatory
  - Antoine is included if the narrow plugin proof is promising enough to
    justify widening
  - manual artifact inspection plus metrics compare the plugin result against
    the best stock baseline, the maintained Tier 2 hybrid path, and the
    reviewed incumbent/golden target
- [x] The story leaves no half-open recommendation:
  - if the plugin path materially closes Leonidas and Marie-Louise while
    staying official and upgrade-friendly, it names the follow-on story that
    should widen to the full reviewed slice / maintained path
  - if it fails, ADR-003/build-map research are updated to record that the
    official plugin seam also does not justify reopening the accepted
    `doc-web` boundary on this lane
- [x] If a single plugin family is insufficient, the story widens in-place to a
  coordinated plugin stack with an explicit stop rule:
  - names which additional official families are being added and why
  - keeps the ownership read honest about whether the result is still
    upgrade-friendly or is becoming plugin-shaped reimplementation of
    `doc-web`
  - stops if the added seams still do not materially close Leonidas and
    Marie-Louise or if the plugin stack becomes obviously nightmare-grade to
    maintain

## Out of Scope

- Maintaining a long-lived `Docling` fork or source patch stack
- Broad plugin combinatorics across every possible family or model just because
  the seam exists
- Storybook or Dossier ingestion migration
- Reviving the existing maintained Tier 2 wrapper path unless the plugin seam
  clearly beats it
- Quietly weakening the reviewed Story 149 acceptance bar

## Approach Evaluation

- **Simplification baseline**: this is not an untested greenfield seam. Stock
  `Docling` and the maintained Tier 2 wrapper have already been measured. The
  only reason to open this story is ADR-003's explicit reopen rule for a
  materially different documented official seam.
- **AI-only**: whole-chapter rereads could brute-force quality in places, but
  they do not answer the plugin question and would weaken the upgrade-friendly
  ownership story.
- **Hybrid**: the leading candidate here is an official `Docling` plugin plus
  a thin repo-owned harness that only loads and evaluates it. A coordinated
  multi-plugin package is still in scope if the first plugin family proves too
  local. That is still a lower-ownership path than reviving the current
  wrapper or patching source.
- **Pure code**: acceptable only for plugin registration, harness orchestration,
  artifact comparison, and score reporting. It should not regrow the incumbent
  rescue stack under a new name.
- **Repo constraints / prior decisions**: ADR-003 currently keeps `doc-web` as
  the accepted boundary and only allows reopening if a materially different
  documented official seam appears. Story 162 closed the current replacement
  track negatively on Leonidas and Marie-Louise. Story 159's tuning findings
  explicitly said future official-only work must be constrained to a concrete
  seam rather than more broad probing.
- **Existing patterns to reuse**:
  `scripts/spikes/docling_onward_tuning_sweep.py`,
  `scripts/spikes/docling_onward_parity_score.py`,
  `configs/recipes/onward-docling-hybrid-maintained.yaml`,
  `modules/transform/repair_docling_onward_genealogy_v1/`, and the reviewed
  Story 149 golden slice under
  `benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/`.
- **Eval**: the decisive eval is still a plugin kill test on Leonidas and
  Marie-Louise first, using the same artifact metrics that kept the incumbent:
  table count, subgroup rows, heading leaks, `BOY/GIRL` merges,
  `coarse_suspect`, summary-table shape, and provenance continuity. The story
  may widen from one plugin family to a coordinated plugin stack, but it
  should not widen beyond the narrow reviewed lanes unless that stack
  materially beats the current maintained Tier 2 evidence.

## Tasks

- [x] Verify and pin the plugin substrate before implementation:
  - confirm the exact local `Docling` runtime / version / venv that exposes the
    official plugin seam
  - confirm the registration surface (`allow_external_plugins`,
    CLI/API hooks, entrypoint format, and supported plugin families)
  - record which seam is actually plausible for the Onward failure class
- [x] Freeze the plugin kill-test hypothesis:
  - name the target stage to replace or augment
  - explain why that stage is the most credible fix for Leonidas /
    Marie-Louise rather than another broad stock retest
  - define explicit stop / widen conditions before coding
- [x] Re-freeze the widened multi-plugin hypothesis after the first negative
  single-plugin result:
  - identify which next official families are credible (`layout`, `ocr`, or
    both)
  - state whether the stack is aiming for plugin-only ownership or allows a
    very thin external orchestrator
  - record the explicit “nightmare” stop condition before implementation
- [x] Build the minimal repo-owned plugin harness:
  - implement the smallest local plugin package or registration shim needed to
    load through official `Docling` plugin discovery
  - avoid `Docling` source edits
  - emit inspectable artifacts and run summaries
- [x] Run the narrow kill test:
  - Leonidas and Marie-Louise through the official plugin path
  - compare against best stock baseline, Story 162 maintained path, and
    reviewed incumbent artifacts
  - manually inspect the produced HTML/JSON/image artifacts
- [x] If the narrow plugin proof materially wins, widen to the remaining
  reviewed slice and score the “100% via plugin” claim honestly; otherwise stop
  and publish the negative result without creating another provisional story
- [x] If the first plugin family is only partially helpful, build the next
  coordinated plugin seam(s) and rerun the same Leonidas / Marie-Louise kill
  test before concluding that official plugins are exhausted
- [x] Publish the result:
  - update ADR-003 research/build-map only if the plugin seam either earns a
    real reopen or is explicitly falsified
  - create a follow-on story only if the plugin result genuinely satisfies the
    reopen condition
- [x] If this story changes documented format coverage or graduation reality: update `docs/build-map.md` and record the before/after state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: run the narrowest real plugin harness, verify artifacts in `output/runs/`, and manually inspect sample HTML/JSON data
  - [x] If agent tooling changed: `make skills-check` (not applicable; no agent tooling changed)
- [x] If evals or goldens changed: run `/improve-eval` and update `docs/evals/registry.yaml` (not applicable; evals/goldens unchanged)
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every output traces to source page, OCR engine, confidence, processing step
  - [x] T1 — AI-First: didn't write code for a problem AI solves better
  - [x] T2 — Eval Before Build: measured SOTA before building complex logic
  - [x] T3 — Fidelity: source content preserved faithfully, no silent losses
  - [x] T4 — Modular: plugin seams remain isolated to a repo-owned package with no `Docling` fork or document-specific page IDs
  - [x] T5 — Inspect Artifacts: visually verified outputs, not just checked logs

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: plugin kill-test harness plus the `Docling`
  decision docs. This story should prove or kill the coordinated official
  plugin path, not deepen the incumbent wrapper or mutate `doc-web`.
- **Build-map reality**: this still belongs to `spec:2` / `spec:3` / `spec:5`
  climb work on the `scanned-pdf-tables` hard-case lane, judged against the
  `spec:6` / `spec:7` provenance and graduation bar. The current build-map
  state explicitly says the replacement question should only reopen for a
  materially different documented official seam.
- **Substrate evidence**: verified today that the repo still has the reviewed
  slice, goldens, stock tuning harness, parity scorer, maintained hybrid
  recipe, and Story 162 evidence. Verified in the isolated
  `.venv-story160-docling-arm64` runtime that `Docling` exposes
  `allow_external_plugins`, CLI text for `--show-external-plugins`, and plugin
  factory modules under `docling.models.factories.*` / `docling.models.plugins`.
  Also verified that the default repo Python does not have `Docling` installed.
  Fresh current-pass substrate proof now exists twice in the isolated runtime:
  first via a temporary throwaway external package, then via the repo-owned
  `docling_plugins/onward_table_structure_plugin.py` entrypoint package added in
  this story. In both cases the custom table-structure kind loaded only when
  `allow_external_plugins=True` and disappeared when
  `allow_external_plugins=False`.
- **Data contracts / schemas**: prefer local spike artifacts and report sidecars
  first. Do not add shared schema fields unless the plugin path wins enough to
  justify a maintained surface.
- **File sizes**: `docs/build-map.md` is 499 lines,
  ADR-003 is 237 lines, `scripts/spikes/docling_onward_tuning_sweep.py` is 424
  lines, `scripts/spikes/docling_onward_parity_score.py` is 528 lines,
  `configs/recipes/onward-docling-hybrid-maintained.yaml` is 215 lines,
  `modules/transform/repair_docling_onward_genealogy_v1/main.py` is 919 lines,
  and `tests/test_repair_docling_onward_genealogy_v1.py` is 187 lines. Avoid
  piling plugin logic into the existing 919-line maintained repair module.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`,
  `docs/build-map.md`, ADR-002, ADR-003, Story 149, Stories 158-162, and
  `docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/onward-tuning-findings.md`.

## Files to Modify

- `docs/stories/story-163-docling-plugin-onward-golden-kill-test.md` — scope
  the official plugin reopen story and record the result (new file)
- `scripts/spikes/docling_onward_plugin_kill_test.py` — narrow plugin harness
  and comparison runner for the reviewed Onward slice (new file)
- `pyproject.toml` — add the minimum local package/entrypoint support only if
  official plugin registration requires editable installation of a repo-owned
  plugin package
- `docling_plugins/onward_layout_plugin.py` — repo-owned local layout plugin
  that collapses same-page genealogy fragments before table structure runs
- `docling_plugins/onward_table_structure_plugin.py` — repo-owned local
  table-structure plugin implementation loaded through `Docling`'s official
  seam (new file)
- `tests/test_docling_plugin_registration.py` — prove the repo-owned plugin
  package registers through the official `Docling` seam without patching source
- `docs/decisions/adr-003-doclingdocument-doc-web-boundary/research/onward-tuning-findings.md` — record the plugin-specific official-seam result if this story runs
- `docs/build-map.md` — update reopen status only if the plugin result changes
  the accepted reading (499 lines)
- `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md` — update
  only if the plugin seam truly reopens or explicitly closes the remaining
  official-only question on this lane (237 lines)
- `docs/stories.md` — track Story 163 status changes

## Redundancy / Removal Targets

- The assumption that “official `Docling` seams are exhausted” without ever
  testing the documented plugin path in the local runtime
- Any follow-up wrapper/adoption stories if the plugin seam fails this kill test
- The plugin harness itself if it cannot materially beat the current stock /
  maintained evidence

## Notes

- Official docs checked on 2026-03-20 indicate that `Docling` supports external
  plugins via `allow_external_plugins`, with plugin families covering OCR,
  layout, table structure, and picture-description models.
- The local isolated arm-native runtime used in prior stories exposes plugin
  factory modules and CLI text for `--show-external-plugins`.
- Fresh current-pass substrate proof: a temporary external package registered a
  custom table-structure kind `story163_table_proof` through the official
  `docling` entrypoint group; `Docling` loaded and instantiated it only with
  `allow_external_plugins=True`, and rejected it with
  `allow_external_plugins=False`.
- Current best hypothesis is `table_structure_engines`, not OCR. The Story 162
  miss signatures are dominated by leaked family headings inside table cells,
  merged `BOY/GIRL` headers, wrong table splits, and wrong summary-table shape,
  which point more directly at table-structure interpretation than raw OCR text
  recovery.
- After the first negative plugin result, the next credible widening candidates
  are `layout_engines` first and `ocr_engines` second. The table plugin can
  clean up row headers and some family-label promotion, but the remaining miss
  class still looks broader than local cell normalization.
- Fresh current-pass contract inspection in the installed `Docling 2.80.0`
  runtime confirmed that the official plugin surface exposed here is limited to
  four factories: OCR, layout, table structure, and picture description. No
  official serializer or document-level merge plugin seam is present in the
  local runtime, which matters because the remaining Onward gap is dominated by
  page-bounded table continuation rather than local OCR token cleanup.
- Final result from this story is negative. The corrected repo-owned
  table-structure plugin runs honestly through the official seam and does make
  small structural improvements (`BOY/GIRL` header splitting plus family-label
  canonicalization in the JSON table cells), but it does not materially reduce
  Leonidas / Marie-Louise table-count inflation or heading leaks enough to
  threaten the accepted `doc-web` boundary or even beat Story 162's maintained
  Tier 2 path.
- This story is now explicitly reopened by user instruction to test whether a
  coordinated official plugin stack can do better than the first
  table-structure-only result before the official-plugin path is finally
  judged exhausted.
- Reopened coordinated-plugin result is still negative. The repo-owned
  `layout_engines` plugin can merge the same-page split on Marie-Louise
  (`6 -> 5` tables) and makes the family heading read more honestly as
  `MARIE LOUISE'S FAMILY`, but Leonidas remains at `7` tables and both lanes
  still finish with `0` subgroup rows. Because the output remains page-bounded
  and no official document/serializer seam exists locally, the next candidate
  is not honestly OCR; the stop rule is triggered instead.
- This story should be treated as a kill test, not a promise that plugins are
  the right path.
- If the plugin only works by embedding broad incumbent rescue behavior or by
  effectively patching `Docling` outside the official seam, count that as a
  failure of the “official plugin path” hypothesis.

## Plan

1. Pin the plugin hypothesis on the narrowest credible failure owner.
   Files: this story, `scripts/spikes/docling_onward_plugin_kill_test.py`,
   `docling_plugins/onward_table_structure_plugin.py`.
   Approach: treat `table_structure_engines` as the default target seam because
   the current misses are structural, not obviously OCR-text losses. Keep OCR
   or layout as fallbacks only if early plugin runs show table-structure
   substitution cannot even move the key signals.
   Done when: the story names the target seam, the temporary substrate proof is
   captured in the work log, and the repo-owned plugin package picks one
   explicit kind / options path rather than a broad multi-seam probe.

2. Land a minimal repo-owned official plugin package and registration proof.
   Files: `pyproject.toml`,
   `docling_plugins/onward_table_structure_plugin.py`,
   `tests/test_docling_plugin_registration.py`.
   Approach: add the smallest local package/entrypoint needed for the isolated
   `Docling` runtime to discover a repo-owned plugin via the official
   `docling` entrypoint group. Prefer a narrow no-op or delegating
   table-structure plugin first so the proof isolates registration and
   instantiation from quality claims.
   Risk: editable-install coupling and the non-default `Docling` venv can make
   this fragile. Keep the proof explicit about which interpreter/venv owns it.
   Done when: a focused test proves the custom plugin kind is discoverable and
   instantiable only with `allow_external_plugins=True`.

3. Build the narrow Leonidas / Marie-Louise kill-test harness.
   Files: `scripts/spikes/docling_onward_plugin_kill_test.py`,
   possibly `configs/recipes/` only if a recipe becomes cheaper than a story
   spike.
   Approach: reuse the Story 162 baseline/golden comparison surfaces and run
   the plugin seam on Leonidas and Marie-Louise first. Emit summary JSON/HTML
   sidecars that compare stock baseline, plugin candidate, maintained hybrid,
   and reviewed golden metrics.
   Done when: one command reruns the plugin lane and leaves inspectable output
   under `output/runs/` or a story-scoped artifact directory.

4. Score the reopen question honestly and stop early if the seam is weak.
   Files: story work log, ADR/build-map research docs only if warranted.
   Approach: if the plugin cannot materially reduce heading leaks, table-count
   inflation, or summary-table shape errors on Leonidas / Marie-Louise, record
   that and stop. Only widen to Antoine or the full reviewed slice if the
   narrow pass clearly beats stock and materially threatens the incumbent.
   Done when: the story says either “plugin seam earned reopening” or
   “plugin seam falsified” with artifact evidence, not another provisional
   note.

5. Validate touched scope and keep the repo graph honest.
   Files: touched code/tests/docs plus this story.
   Checks: focused plugin-registration test first, then `make lint`,
   `make test`, and the narrowest real plugin run with manual artifact
   inspection.
   Done when: the story is `In Progress` with `Build complete` checked or is
   explicitly left blocked if the maintained plugin harness cannot be made
   honest.

6. Widen from one plugin family to a coordinated plugin stack only if the
   partial gains justify it.
   Files: this story, `docling_plugins/`, the kill-test harness, and decision
   docs only if the result changes the read.
   Approach: target `layout` first, then `ocr` only if the layout/plugin
   evidence still points upstream text assignment as the main blocker. Reuse
   the same Leonidas / Marie-Louise kill-test lanes so the comparison stays
   honest.
   Stop rule: stop immediately if the stack still does not materially improve
   table count / heading leaks over the current table-only plugin result, or if
   the required plugin ownership is obviously turning into a plugin-shaped
   clone of the incumbent rescue stack.
   Done when: the story either has a coordinated plugin stack with materially
   better lane metrics or a clear current-pass reason that the official plugin
   path should finally be treated as exhausted.

## Work Log

20260320-1837 — story created to test the only reopen condition still left by
ADR-003: a materially different documented official seam. Current context
reviewed before writing: Story 162 closed the maintained wrapper path
negatively and kept `doc-web` as the accepted boundary; the build map now says
the replacement question should reopen only for a materially different official
seam or a demonstrably thinner hybrid path; and the tuning findings already
warned that future official-only work must be constrained to a concrete seam.
Fresh substrate evidence gathered in this pass: the default repo Python does
not have `Docling` installed, but the isolated `.venv-story160-docling-arm64`
runtime used in prior stories does expose `allow_external_plugins`, CLI help
for `--show-external-plugins`, and plugin factory modules under
`docling.models.factories.*` / `docling.models.plugins`. That is enough to
justify a real story, but not enough to mark it `Pending` yet because local
repo-owned plugin registration and a runnable harness are still unverified.
Next step: verify local registration with a minimal plugin package/shim, then
promote or revise the story based on that evidence.
20260320-1851 — build-story exploration verified that the official plugin seam
is locally real and specific enough to justify promotion to `Pending`. Fresh
current-pass substrate proof: in `.venv-story160-docling-arm64`, a throwaway
editable package was installed outside the repo with a `docling` entrypoint
named `story163_proof` and a custom table-structure kind
`story163_table_proof`. `Docling` loaded and instantiated that plugin through
`get_table_structure_factory(allow_external_plugins=True)`, and the same plugin
was explicitly excluded with `allow_external_plugins=False`. This is the exact
official seam ADR-003 said would justify reopening the question if it proved
material. The failure signatures from Story 162 also sharpen the target:
Leonidas and Marie-Louise are dominated by structural misses (`12` vs `2`
tables, leaked family headings inside table cells, merged `BOY/GIRL` headers,
wrong summary-table shape), so `table_structure_engines` is now the most
credible first plugin family, not OCR. Story promoted from `Draft` to
`Pending`; next step is to land a repo-owned registration proof and run the
narrow Leonidas / Marie-Louise kill test before widening.
20260320-1918 — repo-owned official plugin harness landed and the registration
proof is now local to this repo instead of an external throwaway package.
Added the `docling` entrypoint in `pyproject.toml`, the self-contained plugin
package `docling_plugins/onward_table_structure_plugin.py`, the narrow harness
`scripts/spikes/docling_onward_plugin_kill_test.py`, and focused coverage in
`tests/test_docling_plugin_registration.py`. Fresh current-pass evidence:
`python -m pytest tests/test_docling_plugin_registration.py` passed, and in
`.venv-story160-docling-arm64` the repo-owned kind
`onward_table_structure_v1` appears in
`get_table_structure_factory(allow_external_plugins=True).registered_kind` and
is absent when `allow_external_plugins=False`. Manual proof command also
successfully instantiated the plugin options/model through the real `Docling`
factory.
20260320-1944 — first kill-test pass exposed a real implementation mistake
before the story was allowed to conclude: the initial plugin delegated to
`TableFormerV2`, which is not the best stock Onward owner behind the measured
`baseline-images` substrate. That pass ran through the official seam, but it
massively regressed both lanes (Leonidas `54 -> 428` heading leaks,
Marie-Louise `39 -> 288`) and therefore falsified the initial owner choice,
not the official plugin seam itself. The plugin was corrected to wrap the
stock `TableStructureModel` (`TableStructureOptions`) and to promote
single-cell family-heading rows even when the leaked heading lived in a narrow
interior column.
20260320-2012 — corrected v1-based plugin kill test completed under
`output/runs/story163-docling-plugin-killtest-r1/` and the official seam is
now honestly judged. Manual inspection covered:
- `output/runs/story163-docling-plugin-killtest-r1/leonidas/docling/plugin-onward-table-structure-v1/06 LEONIDAS L'HEUREUX.html`
- `output/runs/story163-docling-plugin-killtest-r1/leonidas/docling/plugin-onward-table-structure-v1/06 LEONIDAS L'HEUREUX.json`
- `output/runs/story163-docling-plugin-killtest-r1/marie-louise/docling/plugin-onward-table-structure-v1/12 MARIE-LOUISE (L'HEUREUX) LaCLARE.html`
- `output/runs/story163-docling-plugin-killtest-r1/marie-louise/docling/plugin-onward-table-structure-v1/12 MARIE-LOUISE (L'HEUREUX) LaCLARE.json`
Observed impact:
- Leonidas plugin lane still ends at `7` tables and `54` heading leaks, but
  improves combined `BOY/GIRL` headers from `7 -> 5`; JSON inspection confirms
  row-section promotion/canonicalization for headings such as `ALICE'S FAMILY`,
  `CLAIRE'S FAMILY`, `PATRICIA'S FAMILY`, and `MARCEL'S FAMILY`.
- Marie-Louise plugin lane still ends at `6` tables and `39` heading leaks,
  but improves combined-header count from `4 -> 2`; JSON inspection confirms
  row-section promotion for `CLAUDE'S FAMILY`, `PAUL'S FAMILY`,
  `MARIE'S FAMILY`, `JOHN'S FAMILY`, and related rows.
- The HTML improvement is real but narrow: first-table headers split into
  `BOY` / `GIRL`, yet the reviewed gold target remains far away at `2` tables
  and `0` heading leaks on both lanes.
- The plugin result is also weaker than the Story 162 maintained Tier 2 path:
  Leonidas maintained evidence still reaches `74` subgroup rows and
  `0` residual combined headers (even though the lane remains negative overall),
  while Marie-Louise maintained evidence reaches `4` tables, `42` subgroup
  rows, and `0` combined headers. The plugin seam does not materially threaten
  that path, much less the accepted incumbent.
Decision: stop at the narrow kill test and publish the negative result.
20260320-2028 — closure validation completed for Story 163. Fresh repo-wide
checks passed: `make lint`, `make test` (`365 passed, 12 warnings`), and
`git diff --check`. The real plugin harness was rerun in the isolated
`.venv-story160-docling-arm64` runtime after the corrected v1 delegate landed,
and the inspected artifacts/summaries are now the official story evidence.
Updated ADR-003, the Onward tuning findings, the build map, and the final
synthesis so the repo now records that the current documented external plugin
seam does not justify reopening the accepted `doc-web` boundary on this lane.
Next step: `/check-in-diff`.
20260320-2046 — user explicitly reopened this story instead of creating a
follow-up. Scope expansion accepted in-place: test whether a coordinated
official plugin stack (`layout`, then `ocr` if justified, alongside the
existing table plugin) can materially outperform the first table-only plugin
result without becoming nightmare-grade to maintain. Story status moved back to
`In Progress`, workflow gates reopened, and the acceptance/task surface now
requires a current-pass decision on the broader plugin stack rather than
freezing at the first negative single-plugin read. Next step: inspect the
layout and OCR plugin contracts in the installed `Docling 2.80.0` runtime and
choose the highest-leverage next owner before implementing more code.
20260320-2119 — coordinated-plugin hypothesis re-frozen after fresh runtime
inspection. Current-pass evidence from the installed `Docling 2.80.0` runtime:
the official factory surface exposed locally is `ocr_engines`,
`layout_engines`, `table_structure_engines`, and `picture_description`; no
serializer or document-level merge plugin seam exists in this install. That
changes the ownership read. The remaining gap on Leonidas / Marie-Louise is
not mainly OCR text recovery; it is page-bounded genealogy-table continuation.
Decision for widening: implement `layout` next, keep the existing table plugin
as the only coordinated companion, and treat `ocr` as unjustified unless the
layout pass materially changes the chapter shape. Nightmare stop condition
frozen explicitly: stop if the coordinated stack still leaves the output
page-bounded or requires plugin-local behavior that is effectively a hidden
clone of the incumbent document-level merge/rescue stack.
20260320-2154 — coordinated official plugin stack landed and the widened kill
test completed under `output/runs/story163-docling-plugin-killtest-r2/`.
Fresh implementation in this pass:
- `pyproject.toml` now registers both `onward_layout_v1` and
  `onward_table_structure_v1` through the official `docling` entrypoint group.
- `docling_plugins/onward_layout_plugin.py` delegates to stock layout, then
  collapses same-page genealogy fragments into a single table region when the
  page already exhibits genealogy markers and no summary-table signal.
- `scripts/spikes/docling_onward_plugin_kill_test.py` now runs three official
  variants on the mandatory lanes: `table-only`, `layout-only`, and
  `layout+table`.
- `tests/test_docling_plugin_registration.py` gained pure helper coverage for
  the new layout heuristics.
Fresh checks in this pass:
- `python -m pytest tests/test_docling_plugin_registration.py`
- `python -m ruff check docling_plugins scripts/spikes/docling_onward_plugin_kill_test.py tests/test_docling_plugin_registration.py`
- `python -m py_compile docling_plugins/onward_layout_plugin.py scripts/spikes/docling_onward_plugin_kill_test.py tests/test_docling_plugin_registration.py`
- `.venv-story160-docling-arm64/bin/pip install -e .`
- `.venv-story160-docling-arm64/bin/python scripts/spikes/docling_onward_plugin_kill_test.py`
Manual artifact inspection covered:
- `output/runs/story163-docling-plugin-killtest-r2/leonidas/docling/plugin-onward-layout-table-v1/06 LEONIDAS L'HEUREUX.html`
- `output/runs/story163-docling-plugin-killtest-r2/marie-louise/docling/plugin-onward-layout-table-v1/12 MARIE-LOUISE (L'HEUREUX) LaCLARE.html`
- `output/runs/story163-docling-plugin-killtest-r2/leonidas/docling/plugin-onward-layout-table-v1/summary.json`
- `output/runs/story163-docling-plugin-killtest-r2/marie-louise/docling/plugin-onward-layout-table-v1/summary.json`
Observed impact:
- Leonidas does not materially move. `layout+table` still ends at `7` tables,
  `55` table-heading leaks, `5` combined `BOY/GIRL` headers, and `0` subgroup
  rows. The HTML remains page-bounded (`[2] [3] [4] [5] [6] [7] [8]`) and
  still flattens continuation rows like `Josephine Dion Josephine`.
- Marie-Louise improves only narrowly. `layout` merges the same-page split
  from `6 -> 5` tables and restores the opening heading to
  `MARIE LOUISE'S FAMILY`, but `layout+table` still lands at
  `49` table-heading leaks, `2` combined headers, and `0` subgroup rows. The
  remaining tables are still page-bounded (`[3] [4] [5] [6] [7]`), far from
  the reviewed two-table target.
- Relative to Story 162, the coordinated plugin stack still underperforms the
  maintained wrapper on the structural signal that matters most. The maintained
  path reaches `74` subgroup rows on Leonidas and `42` on Marie-Louise; the
  coordinated plugin stack reaches `0` on both.
Decision: stop at `layout+table`. An OCR plugin is not justified by the
current-pass evidence because the dominant remaining defect is document-level
multi-page table continuation and no official serializer/document plugin seam
exists in the local runtime to own that cleanly.
20260320-2122 — `/mark-story-done` closeout validation completed and the story
is now formally closed. Fresh closeout checks passed on the current tree:
`python -m pytest tests/` (`367 passed, 12 warnings`),
`python -m ruff check modules/ tests/`, the widened official plugin harness in
`.venv-story160-docling-arm64`, and `git diff --check`. Acceptance criteria,
tasks, tenet checks, and docs updates are all complete, and the coordinated
plugin result is now fully reflected in ADR-003, the build map, Scout 011, the
Onward tuning findings, the final synthesis, and the changelog. Final
disposition: close Story 163 as a negative boundary-reopen result and treat the
official plugin path as exhausted for this Onward seam unless a materially
different documented seam appears. Next step: `/check-in-diff`.
