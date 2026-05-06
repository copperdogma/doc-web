---
title: "Refresh Crop C4 Proof and Coverage Truth Surfaces"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #4 (Illustrate), Requirement #6 (Validate), Traceability is the product, Fidelity to the source, Transparency over magic"
spec_refs:
  - "spec:4"
  - "spec:4.1"
  - "spec:4.2"
  - "spec:8"
  - "spec:9"
adr_refs: []
depends_on:
  - "183"
  - "198"
category_refs:
  - "spec:4"
  - "spec:8"
  - "spec:9"
compromise_refs:
  - "C4"
  - "C5"
  - "B1"
  - "B8"
input_coverage_refs:
  - "image-directory-scans"
  - "scanned-pdf-tables"
architecture_domains:
  - "methodology_tooling"
roadmap_tags: []
legacy_system: ""
---

# Story 207 — Refresh Crop C4 Proof and Coverage Truth Surfaces

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/runbooks/crop-eval-workflow.md`, `docs/stories/story-183-crop-benchmark-substrate-and-c5-validation-surface.md`, `docs/stories/story-184-collapse-bounded-crop-runtime-to-single-stage-flash.md`, `docs/stories/story-198-delete-crop-runtime-validator-retry-residue.md`, `docs/stories/story-204-methodology-roadmap-truth-refresh.md`, and `None found after search in docs/decisions/`, `docs/scout/`, and `docs/notes/` for a narrower crop-proof or proof-surface-alignment ADR
**Depends On**: Stories `183` and `198`

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

The recent crop line proved a stronger maintained C4 detector result than the canonical format coverage rows used to show. At story start, `docs/spec.md`, `docs/runbooks/crop-eval-workflow.md`, `docs/evals/registry.yaml`, and Story 184 all said the maintained crop surface reached `0.9678 / 1.0` on 2026-04-03, while `tests/fixtures/formats/_coverage-matrix.json` and the compiled methodology graph still recorded `illustration_extraction = 0.9` plus “below the 0.95 graduation target” for `scanned-pdf-tables` and `image-directory-scans`. This story reconciles those proof surfaces honestly: land fresh maintained evidence that justifies updating the canonical coverage rows, or narrow the detector claim if the rows cannot inherit it honestly.

## Acceptance Criteria

- [x] A current-pass audit records the exact crop proof mismatch from repo evidence:
  - [x] the work log names the `0.9678 / 1.0` claims in `docs/spec.md`, `docs/runbooks/crop-eval-workflow.md`, `docs/evals/registry.yaml`, and `docs/stories/story-184-collapse-bounded-crop-runtime-to-single-stage-flash.md`
  - [x] the work log names the `0.9` plus “below the 0.95 graduation target” claims in `tests/fixtures/formats/_coverage-matrix.json` and the compiled `docs/methodology/graph.json`
  - [x] the story explicitly decides whether those surfaces are meant to represent the same metric or intentionally different scopes
- [x] The story lands one honest canonical contract for the crop proof surfaces:
  - [x] the maintained format rows can honestly inherit the stronger proof, so `tests/fixtures/formats/_coverage-matrix.json` is updated with fresh evidence and the gap language changes accordingly
  - [x] detector-only narrowing was not needed because the current-pass audit showed the canonical rows intentionally inherit the maintained detector surface
  - [x] no contradictory `0.9` versus `0.9678` crop claims remain across the canonical authored sources after the story lands
- [x] Any fresh proof rerun needed to resolve the contract is current-pass and inspectable:
  - [x] the work log records the exact eval or `driver.py` commands run
  - [x] the work log names the exact result file(s) and representative crop/publication artifact path(s) inspected
  - [x] the story does not rely on stale or incompatible proof just because it is already in the repo
- [x] After `make methodology-compile`, generated `docs/stories.md` and `docs/methodology/graph.json` reflect the same crop truth
- [x] If the current compiler/test surface allowed this drift to persist silently, the story lands the smallest justified guardrail in `scripts/methodology_graph.py` and `tests/test_methodology_graph.py`; if metadata-only cleanup is sufficient, no unnecessary compiler change lands

## Out of Scope

- Reopening the crop runtime simplification or deletion work from Stories 184 or 198
- New crop heuristics, prompt redesign, or broad model sweeps beyond the smallest proof needed to settle the canonical score contract
- Claiming `C5` is deleted or widening illustration coverage beyond the reviewed `scanned-pdf-tables` and `image-directory-scans` families
- Unrelated handwritten OCR, intake-routing, or broader methodology redesign work

## Approach Evaluation

- **Simplification baseline**: first determine whether the existing 2026-04-03 crop eval plus the later maintained runtime proof already answer the coverage-row question. A single LLM call is not the problem here; the problem is proof-surface contract drift.
- **AI-only**: low value. AI can summarize the mismatch, but it cannot by itself prove whether a detector-level score should become a format-level coverage score.
- **Hybrid**: likely strongest. Use deterministic audit of authored surfaces, then run the smallest honest bounded eval or driver-backed proof only if the existing evidence is insufficient to resolve the row contract.
- **Pure code**: acceptable only if the current repo evidence already proves the correct scope and the work is just metadata/docs/guardrail cleanup.
- **Repo constraints / prior decisions**: Story 183 repaired the crop benchmark substrate and promoted the bounded C5 truth surface. Story 184 proved Flash-first crop simplification and explicitly said the format rows now inherit `illustration = 0.968`. Story 198 deleted retired crop runtime residue and treated format coverage as unchanged. Story 204 is the current pattern for methodology truth refresh plus a small compiler/test guardrail when drift can recur silently. `docs/methodology/state.yaml` still says `spec:4` substrate exists with `C4 = converge` and `C5 = climb`, while `spec:8` and `spec:9` remain in `hold`.
- **Existing patterns to reuse**: `docs/runbooks/crop-eval-workflow.md`, the `image-crop-extraction`, `single-model-crop-detection`, and `crop-validation` entries in `docs/evals/registry.yaml`, Story 204’s methodology truth-refresh guardrail pattern, and `scripts/methodology_graph.py` plus `tests/test_methodology_graph.py` if a small compiler/test fix is warranted.
- **Eval**: the distinguishing test is whether the canonical format-row `illustration_extraction` contract is meant to mirror the maintained 13-page crop detector surface. If that is not provable from current evidence, rerun the smallest honest crop proof needed to settle the contract, then inspect representative crop/publication artifacts before restating the score.

## Tasks

- [x] Freeze the current crop truth mismatch from repo evidence:
  - [x] record the current `0.9678 / 1.0` claims in the spec, runbook, eval registry, and recent crop story surfaces
  - [x] record the current `0.9` coverage-row score and “below target” gap language in the coverage matrix and compiled graph
  - [x] decide whether these surfaces are supposed to express one metric or two scoped metrics
- [x] Measure the smallest honest proof needed before changing truth surfaces:
  - [x] reuse the existing 2026-04-03 and 2026-04-08 evidence only after confirming it matches the canonical coverage-row contract
  - [x] run the narrowest bounded crop proof needed to justify the canonical row value
  - [x] a fresh driver-backed rerun was not needed because the current row contract stayed detector-derived; the reviewed Onward publication seam was inspected as artifact sanity evidence only
- [x] Update the canonical authored sources to one honest crop proof contract:
  - [x] `tests/fixtures/formats/_coverage-matrix.json`
  - [x] `docs/evals/registry.yaml`
  - [x] `docs/runbooks/crop-eval-workflow.md`
  - [x] `docs/spec.md`; recent closed crop stories stayed historical and did not need score-narrowing edits
- [x] If the current compiler/test surface allowed this drift silently, add the smallest justified guardrail in `scripts/methodology_graph.py` and `tests/test_methodology_graph.py` instead of inventing broader methodology machinery
- [x] Run `make methodology-compile` so `docs/stories.md` and `docs/methodology/graph.json` reflect the refreshed crop truth
- [x] If this story changes documented format coverage or graduation reality: update `tests/fixtures/formats/_coverage-matrix.json` and any relevant methodology state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] `make methodology-compile`
  - [x] `make methodology-check`
  - [x] If `scripts/methodology_graph.py` or `tests/test_methodology_graph.py` change: `python -m pytest tests/test_methodology_graph.py -q`
  - [x] If `scripts/methodology_graph.py` changes: `python -m ruff check scripts/methodology_graph.py tests/test_methodology_graph.py`
  - [x] If crop proof artifacts are rerun: run the exact bounded eval or `driver.py` commands used to justify the updated score and manually inspect the named result/artifact files
  - [x] Broader `make test` / `make lint` were not needed because code outside methodology tooling and benchmark surfaces did not change
- [x] If evals or goldens changed: refresh the crop proof evidence and update `docs/evals/registry.yaml` honestly
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every crop score claim names the exact result file, artifact path, and measured date it comes from
  - [x] T1 — AI-First: use AI only for the crop proof surface itself, not for papering over truth-surface drift
  - [x] T2 — Eval Before Build: do not ratchet the coverage matrix upward without matching proof
  - [x] T3 — Fidelity: keep the published crop quality claims honest; detector-derived row inheritance is now explicit instead of implicit drift
  - [x] T4 — Modular: reconcile score semantics in the owned truth surfaces instead of adding a parallel ad hoc status document
  - [x] T5 — Inspect Artifacts: if a rerun is part of the resolution, manually open the representative crop/publication artifacts, not just the score JSON

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

- **Owning module / area**: crop proof truth surfaces across `tests/fixtures/formats/_coverage-matrix.json`, `docs/evals/registry.yaml`, `docs/spec.md`, `docs/runbooks/crop-eval-workflow.md`, and the generated methodology outputs
- **Methodology reality**: this belongs primarily to `spec:4`, with supporting execution-truth ownership in `spec:8` and `spec:9`. In `docs/methodology/state.yaml`, `spec:4` substrate is `exists`, `C4 = converge`, and `C5 = climb`; `spec:8` substrate is `exists` with `B1 = hold`; `spec:9` substrate is `exists` with `B8 = hold`. The relevant coverage rows are `scanned-pdf-tables` and `image-directory-scans`, which still record `illustration_extraction = 0.9`, but their own notes describe that field as coming from the maintained crop eval rather than a different published-artifact-only metric.
- **Substrate evidence**: verified in this pass that `docs/evals/registry.yaml` contains 2026-04-03 `0.9678 / 1.0` scores for both `image-crop-extraction` and `single-model-crop-detection`; `docs/spec.md` and `docs/runbooks/crop-eval-workflow.md` repeat that stronger maintained score; `tests/fixtures/formats/_coverage-matrix.json` still records `illustration_extraction = 0.9` and “below the 0.95 graduation target” for both relevant format rows; Story 183 says those rows inherited the refreshed `0.918` detector signal; Story 184 and the archived 2026-04-04 build-map body both say the same rows now inherit `illustration = 0.968`; and `docs/methodology/graph.json` still compiles the stale lower row score today. Fresh current-pass proof also exists now: `benchmarks/results/story207-image-crop-baseline.json` reran the maintained `image-crop-extraction` task filtered to Gemini 3 Flash + `conservative-count` and reached `13/13` passes with a recomputed mean score of `0.9703` and pass rate `1.0`. Separately, the reviewed Onward publication seam still exists under `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/`, including `03_crop_illustrations_guided_v1/illustration_manifest.jsonl` and `output/html/chapter-003.html`, so a bounded artifact check remains available without rebuilding upstream OCR. The current repo-local registry result paths for the older 2026-04-03 promptfoo runs are missing from `benchmarks/results/`, which makes a fresh checked-in rerun the cleaner canonical proof if the row score is moved.
- **Data contracts / schemas**: no runtime schema or artifact-shape change is expected. The contracts in scope are the semantics of `illustration_extraction` in the coverage matrix, the crop score notes in `docs/evals/registry.yaml`, and the generated graph/index outputs that present those authored truth surfaces.
- **File sizes**: likely touch points are `docs/stories/story-207-refresh-crop-c4-proof-and-coverage-truth-surfaces.md` (206 lines), `tests/fixtures/formats/_coverage-matrix.json` (545), `docs/evals/registry.yaml` (1829), `docs/runbooks/crop-eval-workflow.md` (106), `docs/spec.md` (199), `scripts/methodology_graph.py` (819), `tests/test_methodology_graph.py` (433), `docs/stories/story-184-collapse-bounded-crop-runtime-to-single-stage-flash.md` (209), `docs/stories/story-198-delete-crop-runtime-validator-retry-residue.md` (278), generated `docs/stories.md` (251), and generated `docs/methodology/graph.json` (8079). `tests/fixtures/formats/_coverage-matrix.json`, `docs/evals/registry.yaml`, `scripts/methodology_graph.py`, and `docs/methodology/graph.json` are already large, so any change there should stay surgical.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/runbooks/crop-eval-workflow.md`, Stories 183/184/198/204, and the recent crop proof notes already compiled into the graph. Search across `docs/decisions/`, `docs/scout/`, and `docs/notes/` found no narrower ADR or decision package that already settles this crop-proof surface alignment question.

## Files to Modify

- `docs/stories/story-207-refresh-crop-c4-proof-and-coverage-truth-surfaces.md` — story plan, work log, and verification record (206 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — reconcile the canonical `illustration_extraction` score and gap language for `scanned-pdf-tables` and `image-directory-scans` (545 lines)
- `docs/evals/registry.yaml` — keep crop score semantics, attempt notes, and retry guidance aligned with the canonical proof claim (1829 lines)
- `docs/runbooks/crop-eval-workflow.md` — restate the maintained crop proof surface and its scope honestly (106 lines)
- `docs/spec.md` — ensure the C4/C5 wording matches the canonical scoped score instead of over-claiming a format-level proof (199 lines)
- `scripts/methodology_graph.py` — only if a narrow compiler guardrail is justified (819 lines)
- `tests/test_methodology_graph.py` — guardrail coverage if compiler/test logic changes (433 lines)
- `docs/stories/story-184-collapse-bounded-crop-runtime-to-single-stage-flash.md` — only if the closed-out wording needs to be narrowed or footnoted to stay honest (209 lines)
- `docs/stories/story-198-delete-crop-runtime-validator-retry-residue.md` — only if its follow-through assumptions about canonical coverage truth need correction (278 lines)
- `docs/stories.md` — generated story index after `make methodology-compile` (251 lines)
- `docs/methodology/graph.json` — generated compiled truth surface after `make methodology-compile` (8079 lines)

## Redundancy / Removal Targets

- Contradictory `0.9` versus `0.9678` crop claims across the coverage matrix, eval registry, runbook, spec, and recent crop stories
- Stale “Illustration extraction remains below the 0.95 graduation target” wording if fresh current-pass proof justifies deleting or narrowing it
- Any story wording that implies the format rows inherit the detector score without canonical follow-through in the owned truth surfaces

## Notes

- New story justification: a new ID is honest instead of reopening Story 184 or Story 198 because those stories validated runtime simplification and residue deletion on the maintained crop lane. This story has a different success surface: reconciling canonical proof claims across the coverage matrix, eval registry, spec/runbook language, and generated methodology outputs.
- The story should not assume the stronger number wins. If the current `0.9` coverage rows are the more honest format-level claim, the correct outcome is to narrow the over-broad `0.9678` wording rather than ratchet the matrix upward.
- No additional UI slice is needed. This is internal proof-surface and methodology-truth work, and it remains honestly inspectable through the existing eval results, run artifacts, and generated docs.

## Plan

### Exploration Summary

- **Ideal alignment**: proceed. This story closes a traceability gap in the current proof surfaces. The repo should not claim two different crop quality truths for the same maintained families without making the scope difference explicit.
- **Relevant methodology state**: `spec:4` already has implemented substrate and sits at `C4 = converge`, so a proof-surface mismatch is higher leverage than more speculative crop architecture work. `spec:8` and `spec:9` are both in `hold`, which favors a narrow truth refresh and guardrail over new planning machinery.
- **Critical substrate verified in this pass**:
  - `docs/evals/registry.yaml` already carries the stronger 2026-04-03 crop results
  - `tests/fixtures/formats/_coverage-matrix.json` already carries the lower canonical row values
  - `docs/runbooks/crop-eval-workflow.md` and `docs/spec.md` already repeat the stronger score
  - `scripts/methodology_graph.py` already compiles those authored sources into `docs/methodology/graph.json`
- **Score-contract finding**: the authored sources strongly indicate the coverage rows and the maintained detector surface are supposed to represent the same crop-quality contract, not two intentionally different scopes. The coverage-row notes explicitly say illustration quality comes from the crop eval, Story 183 says the rows inherited `0.918`, Story 184 says they now inherit `0.968`, and the archived 2026-04-04 build-map body carries those rows at `0.968`. The current `0.9` rows therefore read as stale follow-through, not an intentional detector-versus-format split.
- **Fresh baseline**: reran the maintained `image-crop-extraction` task in this pass with `promptfoo eval -c tasks/image-crop-extraction.yaml --no-cache --filter-providers 'google:gemini-3-flash-preview' --filter-prompts 'conservative-count' --output results/story207-image-crop-baseline.json -j 1`. The run completed on 2026-04-10 with `13/13` passes, `0` failures, `0` errors, and a recomputed mean score of `0.9703` across the 13 maintained cases. The weakest case remains `Image000` at `0.8164`, but the maintained aggregate still clears the `0.95` gate.
- **Evidence caveat**: the registry cites older repo-local result files such as `benchmarks/results/single-model-crop-detection-g3flash-20260403-promptfix.json`, but those files are not present in the current worktree. That does not make the authored score false, but it does make a fresh current-pass rerun the cleaner basis for any canonical row move.
- **Artifact substrate**: the reviewed Onward proof lane from Stories 184 and 198 is still inspectable. Verified in this pass that `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/illustration_manifest.jsonl` exists with 40 rows and that `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/chapter-003.html` still embeds the refreshed crop assets, so the row uplift can stay tied to a real publication seam instead of promptfoo-only rhetoric.
- **Compiler gap**: `scripts/methodology_graph.py` and `tests/test_methodology_graph.py` currently validate references and campaign drift, but they have no check that a canonical coverage row has drifted away from a newer active proof claim in eval/spec/runbook/story surfaces. That is why the contradiction can survive today with `validation.warnings = []`.
- **Status choice**: `Pending` is honest. The proof, coverage, and methodology substrate all exist in the repo today, and the story is concrete enough to build without needing a new runtime or new ADR.

### Recommended Build Direction

1. Lock the contract explicitly before touching generated outputs.
   - Treat `illustration_extraction` for `scanned-pdf-tables` and `image-directory-scans` as the maintained detector-derived crop score unless a source in this pass proves otherwise. Current authored evidence points to that interpretation.
2. Use the fresh 2026-04-10 rerun as the canonical proof anchor.
   - Record the current-pass `results/story207-image-crop-baseline.json` outcome in the story work log and, if the row score moves, in `docs/evals/registry.yaml` so the canon stops depending on missing 2026-04-03 result files.
   - Reuse the existing reviewed Onward publication artifacts only as the artifact-level sanity check that the maintained runtime proof lane still exists.
3. Refresh the owned truth surfaces in one pass.
   - Update `tests/fixtures/formats/_coverage-matrix.json` for both format rows with the honest maintained crop score/date/notes and remove the stale below-target known-gap language if the row now clears `0.95`.
   - Sync `docs/evals/registry.yaml`, `docs/runbooks/crop-eval-workflow.md`, and `docs/spec.md` so they all describe the same maintained crop contract and cite the fresh current-pass proof cleanly.
   - Only touch Stories 184/198 if a short footnote is needed to explain the older missing result-file references or the score/date refresh.
4. Decide whether a narrow compiler guardrail is justified after the metadata refresh.
   - Preferred guardrail shape: a targeted validation warning or error when crop-linked coverage rows referenced by active crop stories lag an active `>= 0.95` crop proof claim in the eval/spec/runbook surfaces.
   - Skip the compiler change if the guardrail would require brittle prose parsing rather than a small metadata-based rule.

### Approval Blockers

- No new ADR or external dependency blocker is visible.
- Main judgment call: whether to preserve the older `0.9678` number for continuity or promote the fresh `0.9703` rerun as the new canonical score. The current-pass evidence is strong enough for either, but using `0.9703` is cleaner if this story is going to refresh the registry and coverage-row dates anyway.
- If the story adds a compiler guardrail, keep it metadata-first. Do not build a large prose-scraping subsystem just to catch this one crop drift.

## Work Log

20260410-1330 — create-story: created Story 207 after `/triage` found no active actionable backlog except a concrete crop proof-surface mismatch. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/runbooks/crop-eval-workflow.md`, Stories 183/184/198/204, and a search across `docs/decisions/`, `docs/scout/`, and `docs/notes/`. Result: a new ID is honest instead of reopening Story 184 or 198 because the runtime line is already validated and closed, while the current work has a different validation boundary: reconciling the canonical crop proof surfaces and adding a narrow guardrail if needed. Current mismatch recorded for the next pass: `docs/spec.md`, `docs/runbooks/crop-eval-workflow.md`, and `docs/evals/registry.yaml` cite `0.9678 / 1.0` on the maintained crop surface, while `tests/fixtures/formats/_coverage-matrix.json` and the compiled graph still report `illustration_extraction = 0.9` plus below-target gap language for `scanned-pdf-tables` and `image-directory-scans`. Status is `Pending` because the proof, coverage, and methodology substrate all exist in repo now. Next step: `/build-story` should decide whether the existing evidence already settles the row contract or whether a bounded fresh crop proof rerun is needed before any canonical score is changed.
20260410-1355 — /build-story exploration+plan: re-read `docs/ideal.md`, `docs/spec.md` (`spec:4`, `spec:8`, `spec:9`), `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/runbooks/crop-eval-workflow.md`, Stories 183/184/198/204, the archived `docs/archive/build-map-hand-authored-2026-04-04.md`, `scripts/methodology_graph.py`, and `tests/test_methodology_graph.py`. The key scope decision is now clearer than when the story was created: the coverage rows are not described anywhere in current authored canon as a separate published-artifact metric. Their own notes say illustration quality comes from the crop eval, Story 183 says the same rows inherited `0.918`, Story 184 says they now inherit `0.968`, and the archived build-map body also carries them at `0.968`. Result: the `0.9` rows look like stale follow-through, not an intentional detector-vs-format split. Fresh baseline in this pass: `cd benchmarks && promptfoo eval -c tasks/image-crop-extraction.yaml --no-cache --filter-providers 'google:gemini-3-flash-preview' --filter-prompts 'conservative-count' --output results/story207-image-crop-baseline.json -j 1` completed successfully with `13/13` passes, `0` failures, `0` errors, and a recomputed mean score of `0.9703`; weakest case remains `Image000` at `0.8164`. Evidence caveat also recorded: the older 2026-04-03 registry result paths are missing from `benchmarks/results/`, so a fresh rerun is the cleaner canonical anchor than prose that points at absent local files. Artifact substrate still exists for bounded sanity checks: verified `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/illustration_manifest.jsonl` and `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/chapter-003.html`, and confirmed the crop manifest still contains 40 rows plus the published HTML still embeds the refreshed crop assets. Compiler gap: `scripts/methodology_graph.py` currently emits no warning for this contradiction class, so a small metadata-first guardrail may be warranted if implementation can do it without brittle prose parsing. Next step after approval: set the story `In Progress`, refresh the coverage matrix and crop truth surfaces around either `0.9678` or the fresh `0.9703` score, regenerate methodology outputs, and add a narrow guardrail only if the metadata cleanup alone still leaves this drift invisible.
20260410-1403 — implementation started after user approval to use the fresh `0.9703` recommendation. Next step: regenerate the methodology views for the status change, then update the canonical crop truth surfaces and the minimal guardrail in one pass.
20260410-1408 — implementation completed for the build pass. Canonical truth refresh: updated `tests/fixtures/formats/_coverage-matrix.json` so `scanned-pdf-tables` and `image-directory-scans` now both carry `illustration_extraction = 0.9703` measured `2026-04-10`, removed the stale below-target gap language, and added explicit `score_sources` metadata tying those row scores to `image-crop-extraction.overall`. Updated `docs/evals/registry.yaml` so both `image-crop-extraction` and `single-model-crop-detection` now have fresh top score entries at `0.9703 / 1.0` on 2026-04-10 plus current-pass attempt history anchored to `benchmarks/results/story207-image-crop-baseline.json`; also refreshed `docs/runbooks/crop-eval-workflow.md` and `docs/spec.md` to cite that current canonical proof. Guardrail: extended `scripts/methodology_graph.py` and `tests/test_methodology_graph.py` so coverage rows can declare `score_sources` and the compiler now fails if the declared row score or measured date drifts from its eval source. Fresh checks in this pass: `python -m pytest tests/test_methodology_graph.py -q` (`14 passed in 0.84s`), `python -m ruff check scripts/methodology_graph.py tests/test_methodology_graph.py` (`All checks passed!`), `make methodology-compile`, and `make methodology-check` (`Methodology graph is current: docs/methodology/graph.json`). Fresh proof/artifact evidence used in this pass: `cd benchmarks && promptfoo eval -c tasks/image-crop-extraction.yaml --no-cache --filter-providers 'google:gemini-3-flash-preview' --filter-prompts 'conservative-count' --output results/story207-image-crop-baseline.json -j 1` completed with `13/13` scorer passes, `0` failures, `0` errors, recomputed mean `0.9703`, average latency about `7878 ms` per page, and total eval cost about `$0.059`; manual inspection covered `benchmarks/results/story207-image-crop-baseline.json`, `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/illustration_manifest.jsonl`, and `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/chapter-003.html`. Result: the coverage rows now honestly inherit the maintained detector-derived crop score, the generated methodology outputs reflect the same truth, and the compiler will now catch this row-vs-eval drift class instead of letting it pass silently. Next step: `/validate`, then `/mark-story-done` if no broader documentation or methodology concerns surface.
20260410-1422 — validate follow-up fixed the remaining proof-anchor portability gap. `benchmarks/results/story207-image-crop-baseline.json` is ignored by `benchmarks/.gitignore`, so citing it directly in the spec/runbook as the sole canonical proof would have recreated the same non-portable evidence problem that triggered this story. This pass added tracked proof note `docs/evals/attempts/001-image-crop-extraction-story207-proof-refresh.md`, repointed `docs/spec.md`, `docs/runbooks/crop-eval-workflow.md`, and the fresh 2026-04-10 notes in `docs/evals/registry.yaml` to that durable repo-backed summary, and left the large promptfoo JSON as a regenerable local raw artifact only. Fresh checks in this pass: `make methodology-compile` and `make methodology-check` both passed again after the note/citation refresh. Result: the canonical crop proof is now portable in-repo, not just locally inspectable on this machine. Next step: rerun `/validate`; if it agrees the proof-anchor gap is gone, the story should be ready for `/mark-story-done`.
20260410-1424 — validation rerun completed after the proof-note portability fix. Fresh checks in this pass: `python -m pytest tests/test_methodology_graph.py -q` (`14 passed in 0.86s`), `python -m ruff check scripts/methodology_graph.py tests/test_methodology_graph.py` (`All checks passed!`), `make methodology-compile`, and ordered `make methodology-check` (`Methodology graph is current: docs/methodology/graph.json`). Fresh validation-specific evidence also confirmed that `benchmarks/results/story207-image-crop-baseline.json` remains ignored by `benchmarks/.gitignore` while the tracked note `docs/evals/attempts/001-image-crop-extraction-story207-proof-refresh.md` now carries the portable proof summary, and that `docs/spec.md`, `docs/runbooks/crop-eval-workflow.md`, and `docs/evals/registry.yaml` all point at the tracked note instead of depending on the ignored JSON as their sole anchor. Result: validation is complete and the remaining close-out work now belongs to `/mark-story-done`.
20260410-1438 — `/mark-story-done` close-out completed. Re-validated Story 207 against the current repo state: all tasks, acceptance criteria, and tenet checks remain satisfied; dependency stories 183 and 198 are both `Done`; and no narrower ADR was found beyond the previously recorded search across `docs/decisions/`. Fresh full-suite checks in this pass: `python -m pytest tests/` (`550 passed, 4 warnings in 668.39s`) and `python -m ruff check modules/ tests/` (`All checks passed!`). Result: Story 207 is now `Done`, the workflow gates are complete, and the remaining next step is `/check-in-diff`.
20260506-0335 — post-closeout model refresh note: screened OpenAI `chat-latest` / GPT-5.5 Instant as a bounded detector challenger after the 2026-05-05 release. The alias was image-callable through `benchmarks/providers/openai_chat_latest_responses.py`, but the maintained detector run `benchmarks/results/chat-latest-image-crop-extraction-20260506.json` scored `0.8006` with `11/13` passes, `0` provider errors, average latency about `3610 ms`, and estimated cost about `$0.1389` total. Manual result inspection found the two failures were bbox undercoverage on `Image013` and `Image021`. Result: Story 207's maintained Gemini 3 Flash detector evidence remains stronger; no maintained provider, prompt, scorer, golden, or coverage truth changed. Portable proof: `docs/evals/attempts/010-chat-latest-instant-bounded-challenger.md`.
