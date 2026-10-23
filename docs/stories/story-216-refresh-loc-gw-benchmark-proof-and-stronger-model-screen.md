---
title: "Refresh LOC George Washington Benchmark Proof and Bounded Stronger-Model Screen"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #3 (Extract), Requirement #6 (Validate), Any format, any condition, Fidelity to the source, Traceability is the product"
spec_refs:
  - "spec:2"
  - "spec:2.1"
  - "spec:2.2"
  - "spec:8"
adr_refs: []
depends_on:
  - "214"
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

# Story 216 — Refresh LOC George Washington Benchmark Proof and Bounded Stronger-Model Screen

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/stories/story-191-finish-real-handwritten-ocr-on-the-loc-fixture-pair.md`, `docs/stories/story-208-glm-ocr-benchmark-for-handwritten-and-table-heavy-seams.md`, `docs/stories/story-212-diem-htr-historical-handwriting-benchmark-slice.md`, `docs/stories/story-214-loc-george-washington-papers-benchmark-slice.md`, `docs/stories/story-215-washington-database-english-longhand-benchmark-slice.md`, `docs/scout/scout-014-degraded-handwriting-eval-sources.md`, `scripts/discover-models.py`, and `None found after search in docs/decisions/`, `docs/runbooks/`, and `docs/notes/` for a narrower LOC proof-refresh or stronger-model-screen ADR/runbook beyond the recent story chain
**Depends On**: Story `214`

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

Story 214 closed the first public LOC George Washington benchmark slice honestly:
the helper and tests exist, the three-asset comparison surface is fixed
(`367413` interrogations, `367466` receipts, `780802` farm reports), and the
story explicitly named that same slice as the next stronger-subject-model proof
surface. In the current pass, however, the shared project `output/` root no
longer contains the Story 214 benchmark run IDs or the `handwritten-loc-gw-*`
artifacts cited in the close-out, so the next honest move is not to reopen
Story 191 on memory alone. This story refreshes the LOC proof under the shared
project output root, runs one bounded stronger-model screen on the exact same
three-asset slice with receipt asset `367466` as the empty-output sentinel, and
ends with one explicit decision: keep Story 191 blocked, name a narrower
follow-on seam, or reopen Story 191 only if the refreshed evidence materially
changes the blocked handwritten failure surface.

## Acceptance Criteria

- [x] A fresh current-pass proof refresh exists on the exact Story 214 LOC
      slice before any new challenger claim:
  - [x] the work log records the current shared-project truth honestly,
        including whether `output/run_manifest.jsonl` or `output/run_health.jsonl`
        still expose the prior Story 214 / `handwritten-loc-gw-*` runs
  - [x] `python scripts/spikes/loc_gw_benchmark.py --out-root <shared-output-run-root> --instrument --max-attempts 2`
        or an equally honest successor command writes fresh
        `benchmark_summary.json`, `handwritten_eval.json`, and
        `loc_gw_slice/slice_manifest.json` under the shared project `output/`
        root
  - [x] manual artifact inspection in the same pass cites the exact shared-root
        paths for receipt sentinel `367466` plus at least one non-empty but
        wrong case (`367413` or `780802`)
- [x] One bounded stronger-subject-model screen exists on the same fixed
      three-asset slice:
  - [x] the story names the exact candidate list and stop rule before running;
        this is a bounded screen, not a broad OCR bake-off
  - [x] the screen keeps image-entry canonical on the same Story 214 assets and
        records per-asset artifact paths, scores, and dominant failure modes
  - [x] the story does not blindly re-run already-broken paths unchanged; if a
        prior candidate only produced integration-wrong empty artifacts, this
        pass must either change the invocation materially or leave that path out
- [x] The result is translated into honest repo truth:
  - [x] if no candidate materially beats the refreshed Story 214 baseline and
        resolves the receipt empty-output sentinel, Story 191 stays blocked and
        no runtime follow-on is opened by inertia
  - [x] if a candidate materially changes the comparison surface, the story
        names the exact reopen or follow-on seam instead of vaguely claiming
        “better handwriting OCR”
  - [x] `docs/evals/registry.yaml` and
        `tests/fixtures/formats/_coverage-matrix.json` stay unchanged unless the
        story actually changes durable tracked truth rather than only refreshing
        comparison-only evidence

## Out of Scope

- Changing the maintained handwritten OCR runtime in the same story
- Marking `handwritten-notes` as `passing`
- Replacing Story 215's blocked Washington access line with a new source hunt
- Turning the LOC comparison slice into a durable maintained eval lane unless
  this story actually earns that promotion
- A broad cross-provider OCR bake-off beyond one bounded stronger-subject-model
  screen
- Manual edits to OCR output or transcripts that hide model failures instead of
  measuring them
- Reopening Story 191 on external comparison evidence alone without naming the
  exact repo-owned verification move or unblock rationale

## Approach Evaluation

- **Simplification baseline**: rerun the existing Story 214 helper unchanged
  under the shared project `output/` root before touching benchmark code or
  model selection. The current pass already proves the harness exists in repo
  and supports `--out-root`; the unresolved gap is fresh shared-root evidence,
  not missing benchmark substrate.
- **AI-only**: a stronger direct OCR model on the fixed LOC slice is the first
  honest challenger move once the baseline is refreshed. If one bounded
  subject-model screen materially clears the receipt empty-output sentinel and
  improves the other two assets, there is no reason to invent heavier runtime
  orchestration first.
- **Hybrid**: likely strongest if the baseline refresh works but the helper
  needs thin extensions for candidate selection, per-candidate summary output,
  or shared-root ergonomics. Keep slice materialization deterministic and add
  only the minimum screen glue needed to compare candidates honestly.
- **Pure code**: appropriate for shared-root reruns, artifact-presence checks,
  summary packaging, and stop-rule enforcement. It is not an OCR improvement
  strategy by itself.
- **Repo constraints / prior decisions**: Story 191 remains blocked until a
  materially different OCR substrate or recovery seam changes the real failure
  surface; Story 208 already exercised one stronger-substrate retry and closed
  negative; Story 214 closed the LOC source/harness seam and explicitly named
  the same three-asset slice as the next screen surface; Story 215 is blocked
  on access and should not be substituted back into the queue. `spec:2.1`
  (`C1`) is still in `climb`, `spec:8` still requires eval-before-build and
  manual artifact inspection, and the `handwritten-notes-transcription` line in
  `docs/evals/registry.yaml` is currently trigger-exhausted rather than
  reopened.
- **Existing patterns to reuse**: `scripts/spikes/loc_gw_benchmark.py`,
  `tests/test_loc_gw_benchmark.py`,
  `benchmarks/scripts/run_handwritten_notes_eval.py`,
  `benchmarks/scorers/handwritten_notes_transcription.py`, Story 214's fixed
  three-asset slice, Story 191's bounded subject-model screen discipline, Story
  208's stronger-substrate benchmark packaging, and `scripts/discover-models.py`
  for candidate discovery.
- **Eval**: the deciding proof is a current-pass rerun on the exact Story 214
  slice under the shared project `output/` root plus a bounded candidate screen
  on that same fixed corpus. The story needs per-asset artifact inspection,
  especially receipt `367466`, not just one aggregate score.

## Tasks

- [x] Freeze the current proof-refresh gap from repo evidence:
  - [x] verify in the current pass whether the shared project `output/` root
        still contains the Story 214 benchmark run IDs and `handwritten-loc-gw-*`
        artifacts cited in the story close-out
  - [x] record the exact absence/presence signal from
        `output/run_manifest.jsonl`, `output/run_health.jsonl`, and the shared
        `output/runs/` tree so the story starts from fresh evidence rather than
        from stale close-out links
  - [x] confirm the reusable substrate still exists in code:
        `scripts/spikes/loc_gw_benchmark.py`, `tests/test_loc_gw_benchmark.py`,
        `benchmarks/scripts/run_handwritten_notes_eval.py`, and
        `benchmarks/scorers/handwritten_notes_transcription.py`
- [x] Refresh the exact Story 214 baseline under the shared project output root
      before screening new models:
  - [x] rerun the helper on the fixed three-asset LOC slice with a new shared
        run root
  - [x] inspect `benchmark_summary.json`, `handwritten_eval.json`,
        `slice_manifest.json`, and representative `page_html_v1` artifacts
  - [x] record the refreshed baseline ratios and the current receipt-empty-output
        sentinel behavior explicitly
- [x] Freeze the bounded stronger-model screen before changing code:
  - [x] verify current candidate availability with
        `python scripts/discover-models.py --check-new`
  - [x] if the candidate set depends on newly released provider capabilities or
        model names, verify them against current official docs before claiming
        the trigger is real (`not needed in this pass`; `gpt-5.4` was already
        callable and repo-known via current discovery plus prior registry use)
  - [x] choose the smallest honest candidate set and explicit stop rule; do not
        re-run the previously broken `gpt-5.4-pro` empty-output path unchanged
- [x] Implement the smallest honest benchmark/screen glue only if the refresh
      shows it is needed:
  - [x] prefer extending `scripts/spikes/loc_gw_benchmark.py` or adding a small
        sibling helper over mutating maintained runtime code
  - [x] if the shared-root refresh keeps failing on transient provider-demand
        errors, add the smallest helper-local retry/reporting hardening needed
        to finish the baseline honestly without mutating maintained recipes or
        OCR runtime code
  - [x] keep output-root handling, candidate metadata, and comparison summaries
        inside story-local artifacts
  - [x] add focused tests only for the new screen or shared-root logic actually
        introduced
- [x] Run the bounded screen, manually inspect artifacts, and publish one
      decision:
  - [x] if no candidate materially changes the LOC slice, keep Story 191
        blocked and stop
  - [x] if a candidate materially changes the LOC slice, name the exact reopen
        or follow-on seam needed for repo-owned verification instead of hand
        waving
  - [x] update Story 214 or this story's notes if the owning follow-up guidance
        changes
- [x] If this story changes documented format coverage or graduation reality: no coverage-matrix or methodology-state truth change was warranted because the result stayed comparison-only evidence
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; no additional redundancy was proven beyond replacing the older shared-root assumption with the hardened helper path and this story's owning decision record
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior or story-local harness behavior changed: clear stale `*.pyc` was not needed because the maintained OCR runtime module did not change; reran the exact benchmark helper / screen command, verified artifacts in `output/runs/`, and manually inspected sample JSON/JSONL data
  - [x] If agent tooling changed: `make skills-check` not needed because no agent tooling changed
- [x] If evals or goldens changed: not applicable, no eval or golden source changed
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every benchmark claim cites exact LOC asset ids, run
        roots, candidate names, and inspected artifact paths
  - [x] T1 — AI-First: benchmark stronger subject models before proposing any
        new runtime glue
  - [x] T2 — Eval Before Build: refresh the fixed comparison surface before
        broadening candidate scope or reopening the runtime line
  - [x] T3 — Fidelity: the receipt empty-output sentinel and other OCR failures
        are reported explicitly instead of normalized away
  - [x] T4 — Modular: keep the work inside bounded benchmark helpers and story
        artifacts rather than baking source-specific logic into the maintained
        runtime
  - [x] T5 — Inspect Artifacts: manually inspect refreshed shared-root outputs
        and candidate artifacts, not just aggregate scores

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

- **Owning module / area**: external handwritten benchmark harnessing around
  `scripts/spikes/loc_gw_benchmark.py`, the existing handwritten eval helper,
  and story-local comparison artifacts. This story should refresh proof and
  screen candidates, not mutate the maintained OCR runtime by default.
- **Methodology reality**: this work belongs to `spec:2` and `spec:8`. In
  `docs/methodology/state.yaml`, `C1` remains in `climb`, `B1` remains in
  `hold`, and the relevant coverage row is `handwritten-notes`, which still
  sits at `has-fixture` because the maintained rescue seam fails the two real
  LOC fixtures. Story 191 remains the blocked runtime line; Story 214 is the
  completed comparison-only LOC source/harness line; Story 215 remains the
  blocked Washington access line.
- **Substrate evidence**: verified in the current pass that
  `scripts/spikes/loc_gw_benchmark.py` and
  `tests/test_loc_gw_benchmark.py` exist locally, the helper already supports
  `--out-root`, and the shared project output surfaces
  `/Users/cam/Documents/Projects/doc-web/output/run_manifest.jsonl` and
  `/Users/cam/Documents/Projects/doc-web/output/run_health.jsonl` still exist.
  Also verified that current searches across that shared output root do not
  expose Story 214 benchmark runs or `handwritten-loc-gw-*` run ids in this
  pass, which makes a proof refresh necessary rather than optional. The
  existing handwritten scorer and helper remain in place at
  `benchmarks/scripts/run_handwritten_notes_eval.py` and
  `benchmarks/scorers/handwritten_notes_transcription.py`.
- **Data contracts / schemas**: prefer story-local benchmark summaries and the
  existing `page_html_v1` artifacts. No shared schema change is expected unless
  new benchmark metadata must cross artifact boundaries; if that becomes
  necessary, add it explicitly instead of smuggling fields into stamped output.
- **File sizes**: likely touch points are
  `docs/stories/story-216-refresh-loc-gw-benchmark-proof-and-stronger-model-screen.md`
  (127 lines),
  `scripts/spikes/loc_gw_benchmark.py` (617 lines),
  `tests/test_loc_gw_benchmark.py` (133 lines),
  `benchmarks/scripts/run_handwritten_notes_eval.py` (330 lines),
  `benchmarks/scorers/handwritten_notes_transcription.py` (119 lines),
  `scripts/discover-models.py` (689 lines),
  `docs/evals/registry.yaml` (2084 lines), and
  `tests/fixtures/formats/_coverage-matrix.json` (564 lines). Keep edits
  especially surgical in `scripts/spikes/loc_gw_benchmark.py`,
  `scripts/discover-models.py`, `docs/evals/registry.yaml`, and the coverage
  matrix because each is already over 500 lines.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`,
  `docs/methodology/state.yaml`, `docs/methodology/graph.json`,
  `docs/evals/README.md`, `docs/evals/registry.yaml`,
  `tests/fixtures/formats/_coverage-matrix.json`, Stories 191/208/212/214/215,
  Scout 014, `scripts/discover-models.py`, and the LOC benchmark helper/tests.
  Search across `docs/decisions/`, `docs/runbooks/`, and `docs/notes/` found no
  narrower ADR or runbook for this specific LOC proof-refresh / stronger-model
  follow-on.

## Files to Modify

- `docs/stories/story-216-refresh-loc-gw-benchmark-proof-and-stronger-model-screen.md` — story record, work log, and close-out truth for the follow-up screen (127 lines)
- `scripts/spikes/loc_gw_benchmark.py` — shared-output proof refresh and any bounded candidate-screen glue (617 lines)
- `tests/test_loc_gw_benchmark.py` — focused coverage for any new helper/screen behavior (133 lines)
- `docs/stories/story-214-loc-george-washington-papers-benchmark-slice.md` — only if this follow-up changes the owning “next step” note or needs a proof-refresh cross-reference (188 lines)
- `benchmarks/scripts/run_handwritten_notes_eval.py` — only if the stronger-model screen needs a small reusable helper extension for the fixed LOC slice (330 lines)
- `benchmarks/scorers/handwritten_notes_transcription.py` — only if refreshed comparison reporting needs extra inspectable failure detail (119 lines)
- `scripts/discover-models.py` — only if candidate discovery/reporting needs a narrow extension for this story (689 lines)
- `docs/evals/registry.yaml` — only if the story honestly changes durable eval-tracking truth rather than remaining comparison-only evidence (2084 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — only if the story materially changes the documented handwritten-support reality (564 lines)

## Redundancy / Removal Targets

- Any vague “future stronger-model screen” note left behind in Story 214 once
  this story becomes the owning packaging surface
- Any worktree-local output-root assumption in the LOC helper or story prose if
  the shared-root refresh path becomes the maintained benchmark posture
- Ad hoc one-off stronger-model command notes if the helper grows a bounded,
  tested candidate-screen path

## Notes

- New story justification: a new ID is honest even though this stays on the
  same external LOC slice. Story 214 closed the source-selection and
  story-local harness-creation seam with validated baseline evidence. This
  follow-up owns a later proof-refresh / candidate-screen seam on the fixed
  slice and should not blur that closed baseline with later challenger evidence.
- The story should stay comparison-only by default. External LOC slice wins do
  not widen `handwritten-notes` support by inertia.
- The receipt page `367466` is the current stop-rule anchor because Story 214
  found it could collapse all the way to empty HTML while the other two assets
  still produced inspectable but wrong text.

## Plan

Current eval-first baseline from `/build-story` exploration:

- The shared project registries at
  `/Users/cam/Documents/Projects/doc-web/output/run_manifest.jsonl`,
  `/Users/cam/Documents/Projects/doc-web/output/run_health.jsonl`, and the
  shared `output/runs/` tree still do not expose the Story 214 benchmark run
  ids or `handwritten-loc-gw-*` artifacts cited in the earlier close-out.
- Fresh current-pass refresh attempts with the existing helper did prove that
  the source/materialization substrate still works under the shared root:
  `python scripts/spikes/loc_gw_benchmark.py --out-root /Users/cam/Documents/Projects/doc-web/output/runs/story216-loc-gw-proof-refresh-r1 --instrument --max-attempts 2`
  wrote `loc_dataset/2020446971.zip`,
  `loc_dataset/README_ordinary-lives-in-george-washingtons-papers-the-revolutionary-war_2023-07-18.txt`,
  `loc_gw_slice/corpus.json`, and `loc_gw_slice/slice_manifest.json` for the
  fixed assets `367413`, `367466`, and `780802`.
- The baseline is still operationally incomplete in this pass because both
  refresh attempts failed before `benchmark_summary.json` or
  `handwritten_eval.json` could be written. The first OCR case
  `handwritten-loc-gw-interrogations-367413-image-handwritten-rescue` died in
  `ocr_ai_gpt51_v1` with Gemini `503 UNAVAILABLE` high-demand errors recorded
  in `output/runs/handwritten-loc-gw-interrogations-367413-image-handwritten-rescue/pipeline_events.jsonl`.
- Story 191 remains `Blocked`, Story 214 remains `Done`, Story 215 remains
  `Blocked`, and the `handwritten-notes-transcription` line in
  `docs/evals/registry.yaml` remains trigger-exhausted.

Implementation order:

1. Make the shared-root proof refresh complete deterministically enough to
   measure.
   Files: `scripts/spikes/loc_gw_benchmark.py`, possibly
   `tests/test_loc_gw_benchmark.py`.
   Change: keep the LOC slice and maintained handwritten recipe unchanged, but
   harden the story-local helper around transient provider failures if the
   current shared-root refresh keeps dying on demand spikes. Prefer
   helper-local retry/reporting or resume behavior over touching maintained OCR
   runtime or recipes.
   Impact/risk: the main risk is accidentally masking real OCR failures as
   retryable noise. The helper must stay explicit about when a run truly fails.
   Done when the exact refresh command writes `benchmark_summary.json`,
   `handwritten_eval.json`, and `loc_gw_slice/slice_manifest.json` under the
   shared output root, and the receipt sentinel `367466` plus one non-empty but
   wrong case are manually inspected from that fresh pass.

2. Freeze the bounded challenger set before any broader helper expansion.
   Files: this story file first; no code file should move yet.
   Candidate list: one image-entry direct `gpt-5.4` challenger on the fixed
   three-asset slice. Explicit exclusions: do not rerun `gpt-5.4-pro`
   unchanged because the corrected-corpus screen already produced empty
   artifacts; do not widen to `gemini-3.1-pro-preview` or GLM-OCR because the
   repo already has fresher negative evidence for those lines.
   Stop rule: if refreshed baseline still shows the receipt `367466` empty
   sentinel and the `gpt-5.4` challenger does not clear that sentinel while
   also materially improving at least one of the other two assets, stop and
   keep Story 191 blocked. No second challenger belongs in this story unless
   the first run fails for a non-quality operational reason.
   Impact/risk: widening back to a multi-model bake-off would repeat Story
   191's failed comparison pattern and blur the decision surface.
   Done when the story records the candidate and stop rule before the screen
   command runs.

3. Add only the minimum screen glue needed to run and summarize that one
   challenger.
   Files: likely `scripts/spikes/loc_gw_benchmark.py`, maybe
   `tests/test_loc_gw_benchmark.py`; touch
   `benchmarks/scripts/run_handwritten_notes_eval.py` only if a tiny reusable
   hook is clearly cleaner than story-local duplication.
   Change: reuse the fixed LOC slice materialization and existing scorer, add
   bounded per-candidate metadata/summary output, and prefer a direct
   image-entry `ocr_ai_gpt51_v1` path (`--model gpt-5.4`, optional
   `--retry-model gpt-5.2`) over new maintained recipes or runtime mutations.
   Impact/risk: `scripts/spikes/loc_gw_benchmark.py` is already medium-large,
   so new code should stay local and summary-oriented rather than growing into
   a generic benchmark framework.
   Done when one bounded command can produce comparable per-asset outputs and
   scores for baseline plus the `gpt-5.4` challenger.

4. Run the bounded screen, inspect artifacts, and translate the result into
   repo truth.
   Files: this story file first; `docs/evals/registry.yaml` and
   `tests/fixtures/formats/_coverage-matrix.json` should stay untouched unless
   durable tracked truth genuinely changes.
   Change: execute the refreshed baseline and the one-candidate challenger,
   inspect receipt `367466` plus one non-empty wrong case, and publish one
   explicit decision: keep Story 191 blocked, name a narrower follow-on seam,
   or reopen Story 191.
   Impact/risk: the main false-positive risk is treating a modest gain on one
   easier page as a handwriting unblock. The decision must stay anchored to the
   receipt sentinel and the whole three-asset slice.
   Done when the story records exact artifact paths, per-asset scores,
   dominant failure modes, and the resulting reopen/no-reopen decision.

Graph/state expectations:

- No category, compromise-phase, or coverage movement is expected from the
  bounded comparison-only path. `spec:2` stays `exists`, `spec:8` stays
  `exists`, `C1` stays `climb`, `B1` stays `hold`, and
  `handwritten-notes` should remain `has-fixture` unless a later runtime-owned
  story changes durable truth.
- `docs/evals/registry.yaml` should remain unchanged unless this story earns a
  durable tracked comparison surface instead of only refreshing story-local
  evidence.

Structural health notes:

- `scripts/spikes/loc_gw_benchmark.py` is already one of the larger story-local
  helpers, so edits should stay surgical.
- `benchmarks/scripts/run_handwritten_notes_eval.py` and
  `modules/extract/ocr_ai_gpt51_v1/main.py` are higher-risk boundaries; avoid
  touching them unless helper-local hardening cannot honestly complete the
  refresh and one-candidate screen.
- The shared-root LOC slice is already partially materialized under
  `/Users/cam/Documents/Projects/doc-web/output/runs/story216-loc-gw-proof-refresh-r1/`,
  so the implementation should reuse that deterministic slice when possible
  instead of treating the source fetch as the blocker.

Scope adjustment from exploration:

- Folded in automatically: Story 216 now includes a tiny operational-hardening
  slice for transient provider-demand failures on the shared-root refresh path.
  This is tightly coupled to the proof-refresh goal and smaller than opening a
  separate story.
- Not recommended: broadening back to a multi-model bake-off, touching the
  maintained handwritten runtime in the same pass, or reopening Story 191 by
  inertia from external benchmark evidence alone.
- Approval-sensitive expansion: if helper-local hardening is not enough and the
  story needs shared eval-helper or OCR-module changes, bring that scope change
  back to the user before implementation continues.

Expected effort: `M`

## Work Log

20260411-2246 — create-story: created Story 216 after the user approved `/triage`'s recommendation for the next honest handwritten move. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, Stories 191/208/212/214/215, Scout 014, `scripts/discover-models.py`, `scripts/spikes/loc_gw_benchmark.py`, and `tests/test_loc_gw_benchmark.py`. Fresh repo-state finding: the LOC helper and tests still exist and the helper already supports `--out-root`, but the shared project `output/` root does not currently expose the Story 214 benchmark run ids or `handwritten-loc-gw-*` artifacts cited in the close-out. Result: a new `Pending` story is honest instead of reopening Story 214 because the baseline/harness-creation seam is already closed, while the missing work now is proof refresh plus a bounded stronger-model screen on that fixed slice. Next step: `/build-story` should rerun the baseline under the shared output root, freeze the candidate list and stop rule, and only then decide whether Story 191 is still blocked.
20260411-2314 — `/build-story` exploration + plan refresh: re-read `docs/ideal.md`, `docs/spec.md` (`spec:2`, `spec:2.1`, `spec:2.2`, `spec:8`), `docs/methodology/state.yaml`, `docs/methodology/graph.json`, the `handwritten-notes` coverage row, Story 214, and the blocked Stories 191/215 before tracing the current LOC benchmark and OCR substrate in `scripts/spikes/loc_gw_benchmark.py`, `tests/test_loc_gw_benchmark.py`, `benchmarks/scripts/run_handwritten_notes_eval.py`, `benchmarks/scorers/handwritten_notes_transcription.py`, and `modules/extract/ocr_ai_gpt51_v1/main.py`. Fresh shared-root audit confirmed that `/Users/cam/Documents/Projects/doc-web/output/run_manifest.jsonl`, `/Users/cam/Documents/Projects/doc-web/output/run_health.jsonl`, and the shared `output/runs/` tree still do not expose the Story 214 benchmark run ids or `handwritten-loc-gw-*` artifacts named in the earlier close-out, so the proof gap remains current-pass real. Eval-first baseline in the same pass: ran `python scripts/spikes/loc_gw_benchmark.py --out-root /Users/cam/Documents/Projects/doc-web/output/runs/story216-loc-gw-proof-refresh-r1 --instrument --max-attempts 2` twice without changing code. Both runs proved the source/materialization substrate is present by writing `loc_dataset/2020446971.zip`, the LOC README copy, `loc_gw_slice/corpus.json`, and `loc_gw_slice/slice_manifest.json` for the fixed assets `367413`, `367466`, and `780802`, but both failed before `benchmark_summary.json` and `handwritten_eval.json` were produced because the first image-entry OCR case `handwritten-loc-gw-interrogations-367413-image-handwritten-rescue` failed inside `ocr_ai_gpt51_v1` with Gemini `503 UNAVAILABLE` high-demand errors recorded in `output/runs/handwritten-loc-gw-interrogations-367413-image-handwritten-rescue/pipeline_events.jsonl`. I also rechecked current callable models with `python scripts/discover-models.py --check-new`; it still reports callable frontier options including `gpt-5.4`, `gpt-5.4-pro`, `gpt-5.2-pro`, and Gemini 3.x. Result: Story 216 remains honestly buildable and should stay `Pending`, because the missing slice is no longer "LOC proof substrate does not exist" but "the shared-root refresh needs bounded operational hardening plus one explicitly frozen challenger path." Small scope delta folded into the story: allow the smallest helper-local retry/reporting hardening needed to finish the shared-root refresh honestly if transient provider-demand failures keep aborting the first OCR case. Candidate recommendation narrowed from the discovery set before implementation starts: use one image-entry `gpt-5.4` challenger only, exclude unchanged `gpt-5.4-pro`, and do not widen back to a multi-model bake-off. Next step: wait for user approval on this refreshed plan before any implementation code or status change.
20260411-2324 — implementation start: user approved the refreshed `/build-story` plan, so Story 216 moves to `In Progress`. Immediate next steps in this pass are to regenerate the compiled methodology surfaces for the status change, harden the LOC helper just enough to survive transient provider-demand failures on the shared-root refresh path, and then run the bounded `gpt-5.4` image-entry challenger on the same fixed three-asset slice.
20260411-2351 — implementation + bounded screen: extended `scripts/spikes/loc_gw_benchmark.py` and `tests/test_loc_gw_benchmark.py` instead of touching maintained OCR runtime code. The helper now routes driver runs into the shared project output root, records richer failure summaries, reuses completed baseline cases on rerun, adds bounded backoff for retryable provider-demand failures, and can run one optional direct-image challenger with recipe-aligned OCR params. Focused verification passed in the same pass: `python -m pytest tests/test_loc_gw_benchmark.py -q` (`7 passed`) and `python -m ruff check scripts/spikes/loc_gw_benchmark.py tests/test_loc_gw_benchmark.py` (`All checks passed!`). Fresh baseline proof refresh under `/Users/cam/Documents/Projects/doc-web/output/runs/story216-loc-gw-proof-refresh-r1/` required bounded operational hardening but completed honestly on the fixed Story 214 slice: `benchmark_summary.json`, `handwritten_eval.json`, and `loc_gw_slice/slice_manifest.json` now exist under that shared root. Manual artifact inspection in the same pass confirmed the refreshed maintained failure surface: interrogations `367413` is non-empty but wrong at `0.696694` in `/Users/cam/Documents/Projects/doc-web/output/runs/handwritten-loc-gw-interrogations-367413-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl`; receipt sentinel `367466` remains stamped empty with `ocr_empty_reason = "Empty HTML output for page 1"` at `0.0` in `/Users/cam/Documents/Projects/doc-web/output/runs/handwritten-loc-gw-receipts-367466-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl`; and farm `780802` is non-empty but wrong at `0.855009` in `/Users/cam/Documents/Projects/doc-web/output/runs/handwritten-loc-gw-farm-780802-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl`. I then ran the single frozen challenger `gpt-5.4` with optional `gpt-5.2` empty-output retry through the same helper, which wrote `/Users/cam/Documents/Projects/doc-web/output/runs/story216-loc-gw-proof-refresh-r1/candidate-screen-gpt-5-4.json` plus per-asset artifacts under shared `output/runs/`. Result: the challenger materially changed only the receipt sentinel, not the overall decision surface. It cleared receipt `367466` from empty to non-empty (`overall_ratio = 0.16971`) at `/Users/cam/Documents/Projects/doc-web/output/runs/story216-loc-gw-receipts-367466-image-gpt-5-4/01_ocr_ai_gpt51_v1/pages_html.jsonl`, but it regressed interrogations to `0.429601` and farm to `0.529925`, both far below the refreshed maintained baseline. Decision: Story 191 stays blocked. The exact narrower follow-on seam, if anyone reopens this line later, is a receipt-only image-entry rescue probe on asset `367466` using the `gpt-5.4` path or close prompt/entry variants; it is not a general handwritten-runtime reopen and does not justify changing durable truth surfaces in this pass.
20260411-2359 — validation + residual risk: `make lint` passed fresh, `python -m py_compile scripts/spikes/loc_gw_benchmark.py tests/test_loc_gw_benchmark.py` passed, and `git diff --check` passed. Full `make test` did not complete cleanly in this pass: pytest progressed to `211 passed in 463.48s (0:07:43)` and then went idle until I interrupted it, surfacing `KeyboardInterrupt` in `subprocess.py`. That means the touched helper/tests and the benchmark artifacts are freshly verified, but I do not have a fresh clean full-suite `make test` pass for this turn. No `docs/evals/registry.yaml`, coverage-matrix, or methodology-state truth change was warranted because this remained comparison-only evidence. Next step: `/validate 216` should treat the bounded implementation as complete, recheck the incomplete full-suite target if needed, and then decide whether the current no-reopen / receipt-only-follow-on conclusion is ready for `/mark-story-done`.
20260412-0111 — `/mark-story-done` close-out: revalidated the completed Story 216 slice against `docs/ideal.md`, `spec:2`, `spec:8`, and the existing decision chain. Fresh checks now pass cleanly on the story branch tip: `python -m pytest tests/` (`571 passed, 4 warnings in 645.54s`), `python -m ruff check modules/ tests/` (`All checks passed!`), `make lint`, `make methodology-compile`, `make methodology-check`, `python -m py_compile scripts/spikes/loc_gw_benchmark.py tests/test_loc_gw_benchmark.py`, and `git diff --check`. I re-opened the shared-root benchmark artifacts and confirmed the final repo-truth decision still holds: baseline receipt `367466` remains empty at `/Users/cam/Documents/Projects/doc-web/output/runs/handwritten-loc-gw-receipts-367466-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl`, while the bounded `gpt-5.4` challenger only improves that one receipt case at `/Users/cam/Documents/Projects/doc-web/output/runs/story216-loc-gw-receipts-367466-image-gpt-5-4/01_ocr_ai_gpt51_v1/pages_html.jsonl` and regresses the other two assets. Result: Story 216 is complete as a comparison-only proof refresh and bounded screen, Story 191 remains blocked, no eval-registry or coverage-matrix truth change is warranted, and the recommended next step is `/check-in-diff`.


## October 23 continuation — trustworthy provider catalog discovery

20261023 — triage/build-story plan: reopen this existing discovery/reporting owner under the standing autonomous triage/fix goal. No OCR benchmark or provider inference is authorized by this continuation. New synthetic-only baseline (output/triage-20261023-discovery-audit/baseline.json) proves Google puts credentials into an exception-visible URL and Anthropic HTTP failure returns a guessed static list labelled successful. Main/reviewer inspection also shows ignored pagination and a registry matcher that collapses GPT6 Sol/Astra/Luna identities. Historical discovery claims remain historical; no past score, source adjudication, default or coverage row is being rewritten. The user explicitly approved reuse of existing project keys, resolving the API-key skill gate; do not ask again for this scope.

Why now: these are demonstrated credential exposure and false decision-input defects, while handwritten retry triggers remain waiting/exhausted and Story226's exact cached replay lacks authentic original planner files. Story218's stale-inventory continuation is complete. State/graph still assign spec:2/8 substrate and C1/B1 to their existing posture; no discovered name alone reopens Story191. ADR-002/runtime boundaries are unchanged; no narrower discovery ADR applies. Existing Story216 explicitly owns scripts/discover-models.py, so this is a same-story helper continuation rather than a new feature story.

Bounded primary research: Google documents x-goog-api-key header auth (https://ai.google.dev/api), pageSize up to1000 and nextPageToken (https://ai.google.dev/api/models); Anthropic documents after_id/last_id and has_more with limit up to1000 (https://platform.claude.com/docs/en/api/models/list). OpenAI Docs search/fetch was followed by the official endpoint reference (https://developers.openai.com/api/reference/resources/models/methods/list); current helper's model-list API version/auth remains unchanged. Adopt provider-observed catalogs with complete-or-unavailable reporting, no static fallback, finite pagination, and constant diagnostic categories instead of exception bodies/URLs. Exact identities and credentials belong in code, not a decision model or LLM. Registry name matching is only a score-reference lead, not tested quality or inference access. Keep heuristic tiers labelled as heuristics; do not broaden into a taxonomy redesign.

Continuation acceptance/tasks:
- [x] Dummy secrets never appear in request URLs, diagnostic streams, reports or cached output, including HTTP/transport/parse/unexpected failures.
- [x] Failed or incomplete providers contribute no guessed/partial success catalog; multi-page Google/Anthropic traversal terminates under a finite cap and rejects invalid/repeated cursors or response shapes.
- [x] Distinct model siblings, snapshots and preview identities cannot inherit a generic score-name match; report labels describe registry references rather than qualification.
- [x] Cache output stays valid structured YAML even when summary output is also requested; empty/error/skipped providers remain explicit in every report mode.
- [x] Failing offline regressions precede the fix, focused lint/skill/methodology checks pass, and one bounded read-only live catalog pass is manually inspected without inference or default/score changes.

Plan: add focused offline tests with synthetic credentials and mocked HTTP; remove URL credentials/raw-error serialization/static fallback; follow provider pagination with a20-page cap and validate response records; make registry identity parsing conservative and labels explicit. Preserve model filters except a demonstrated bare reasoning-ID omission; no capability inference from a prefix. Keep CLI cache structured, update the discovery skill's key/status semantics, validate all report modes and synthetic leak scans, then run one existing-key catalog-only discovery. Preserve exact observation artifacts and assess whether a specific newly observed identity satisfies an existing retry trigger; stop the discovery pass if no qualifying delta exists. No paid eval, package/API-version/account change, commit or push.

20261023 — implementation/validation: initial synthetic regressions reproduced 34 failures before the discovery repair. Removed query-string credentials, raw exception serialization and static Anthropic success fallback; implemented complete-or-unavailable bounded pagination and response identity checks; retained model sibling/snapshot/preview boundaries; labelled registry matching only as score-name references. An independent semantic review found the optional-parser fallback could promote an attempt's `requested_model` to a score reference. Six more regressions reproduced five failures before fixing this: unavailable/malformed/missing registry input now returns an explicit unassessed state, never a guessed empty or matched history. Final focused result: `python -m pytest tests/test_discover_models.py -q --tb=short` =50passed; focused Ruff passed; independent reviewer confirmed the fallback correction clean. No pipeline behavior changed, so CLI/report evidence is the applicable completion surface; no driver/OCR rerun is needed. T0: hashed code and exact catalog snapshot retained; T1/T2: deterministic identity/authentication rules, offline failure proof before repair, no speculative model adoption; T3: provider errors/incomplete catalogs preserved as unavailable; T4: same discovery helper, no new framework; T5: manually opened YAML, text summary, diagnostics and runtime binding.

20261023 — authorized live observation: `output/triage-20261023-discovery-audit/live_catalog_proof.py` invoked the actual CLI once with `--cache --summary` under the approved existing project credentials. `live-proof.json` records exactly three fixed-endpoint GETs, all HTTP200, zero inference requests, interpreter/platform, and SHA256 bindings for helper/tests/skill/cache. Provider results: OpenAI65, Anthropic14, Google27 filtered catalog entries; all completed in one page, so multi-page safety is covered by offline tests rather than this live sample. Credential scan found no configured key in saved diagnostics/summary/cache. Manually opened `live-catalog.yaml` and `live-summary.txt`: exact IDs include `gpt-6.1-sol`, bare `o3`, `claude-opus-5-5`, `claude-haiku-5-5`, `gemini-3.8-flash` and `gemini-4-argon`; snapshot IDs remain separate, and75 catalog IDs have no matching score-name reference. The cache at `docs/evals/models-available.yaml` is structured YAML even with summary output. These are account catalog observations, not inference/modality/quality evidence. Full text rendered from the same cached observations is `live-full-report.txt`; no second catalog call was made. New identity leads are being checked against existing attempts and official contracts before the next triage recommendation; no score/default/coverage mutation follows from discovery alone.

20261023 — triage outcome and `/mark-story-done`: all five continuation acceptance items met, 50 offline tests and focused Ruff pass; skill compatibility check (29 canonical skills), methodology build/check and diff hygiene pass. Live helper/test/skill/cache SHA bindings still match the executed candidate. No new score, default, coverage support claim or OCR unblock. Story216 returns to Done; this tool-only continuation is independently complete and does not wait on a future inference campaign. An independent read-only model review verified official contracts for stable `gemini-4-argon` (https://ai.google.dev/gemini-api/docs/models/gemini-4-argon) and `gemini-3.8-flash` (https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash), both absent from the inspected registry/attempt identities. These materially support investigation under the existing new-subject-model trigger, especially the detector trigger naming Gemini4; prepare a separate bounded decision contract, exact served identity/image/strict-schema/owner parity qualification and source-reviewed screens before any full suite. Resolve catalog Argon32768 versus documented65536 output-limit discrepancy conservatively during qualification. `claude-haiku-5-5` is a lower-priority economics lead (https://www.anthropic.com/claude-haiku-5-5). `claude-opus-5-5` is already measured in Attempt041/Story232 despite no score-name reference; do not repeat its unchanged failed detector/page-safety arms. Existing exhausted attempts remain closed; Story191 still requires both real fixtures at .99, and literal-table confirmation requires fresh reserved material. No provider inference was performed.

20261023 — strategic `/loop-review` checkpoint: bounded read-only reviewer configured `gpt-6-astra/ultra` from existing current-runtime selection evidence; served identity unavailable. Prior recommendation followed through: Story218 stale-inventory proof is complete and discovery resumed only after the user approved existing-key reuse. Outcome: aligned/progressing; stop catalog work after this one complete observation per provider, retain new model leads separately, and return to product-boundary verification. Next falsifiable hypothesis is whether valid-plus-cleaned-empty HTML mixed intake can claim misleading parent/member success. Reuse existing composition proof if applicable; otherwise one zero-inference driver composition, stop after one clean proof or reproducible defect, preserving existing story ownership. This reuses the established end-product validation alternative (https://www.nasa.gov/reference/5-4-product-validation/) rather than extending catalog taxonomy without a demonstrated defect. Next strategic review after roughly30active minutes or three substantive rounds. Continue `/triage` under the standing goal; `/finish-and-push` remains available only after an explicit landing request.
