---
title: "Widen C5 Crop Deletion Gate to Page-Level Proof"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #4 (Illustrate), Requirement #6 (Validate), Traceability is the product, Fidelity to the source, Transparency over magic"
spec_refs:
  - "spec:4"
  - "spec:4.1"
  - "spec:4.2"
  - "spec:8"
adr_refs: []
depends_on:
  - "183"
  - "198"
  - "207"
category_refs:
  - "spec:4"
  - "spec:8"
compromise_refs:
  - "B1"
  - "C4"
  - "C5"
input_coverage_refs:
  - "image-directory-scans"
  - "scanned-pdf-tables"
architecture_domains:
  - "methodology_tooling"
roadmap_tags: []
legacy_system: ""
---

# Story 209 — Widen C5 Crop Deletion Gate to Page-Level Proof

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/registry.yaml`, `docs/runbooks/crop-eval-workflow.md`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/stories/story-183-crop-benchmark-substrate-and-c5-validation-surface.md`, `docs/stories/story-184-collapse-bounded-crop-runtime-to-single-stage-flash.md`, `docs/stories/story-198-delete-crop-runtime-validator-retry-residue.md`, `docs/stories/story-207-refresh-crop-c4-proof-and-coverage-truth-surfaces.md`, and `None found after search in docs/decisions/`, `docs/scout/`, and `docs/notes/` for a narrower crop-specific deletion-gate ADR or runbook
**Depends On**: Stories `183`, `198`, and `207`

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

The maintained crop line has an honest mismatch between what the repo can prove
and what `C5` still demands. `single-model-crop-detection` now clears the
bounded C4 deletion gate at `0.9703 / 1.0`, and the maintained runtime already
collapsed the old retry / refine / validator residue. But `crop-validation`
still measures only a bounded 40-crop pass/fail surface, while `docs/spec.md`
still says `C5` needs broader page-level evidence before `trim_layout_text`
and the surviving text-exclusion residue can be removed honestly. This story
widens or redesigns the C5 truth surface so it measures that page-level gate,
then uses current-pass evidence to decide whether `trim_layout_text` and the
remaining bounded caption-assist residue are still required on the maintained
Onward lane.

## Acceptance Criteria

- [x] A current-pass audit records the exact C5 proof gap from repo evidence:
  - [x] the work log names the current bounded `crop-validation` contract in `docs/evals/registry.yaml` and `docs/runbooks/crop-eval-workflow.md`
  - [x] the work log names the spec mismatch explicitly: `crop-validation` passes on the checked-in 40-crop corpus, but `docs/spec.md` still requires broader page-level evidence before the trim heuristics can be deleted
  - [x] the story names the concrete reviewed residue cases that still block honest deletion today, including the page-12 seal/text-bearing case and the page-122 caption-leak case from the maintained Onward seam
- [x] The story lands one honest repo-owned C5 page-level deletion-gate surface:
  - [x] either by widening the existing `crop-validation` task or by adding a sibling page-level task if that is cleaner
  - [x] the chosen surface has reproducible local inputs, explicit golden or verdict semantics, and focused integrity coverage so a clean checkout can run it
  - [x] if the maintained proof still depends on ignored `benchmarks/results/*.json`, a tracked proof note under `docs/evals/attempts/` anchors the new score or decision portably
  - [x] the surface is documented in `docs/evals/registry.yaml` and `docs/runbooks/crop-eval-workflow.md` with honest scope, target, and retry posture
- [x] Fresh current-pass evidence exists on the widened surface:
  - [x] the work log records the exact commands run and the exact result file(s) inspected
  - [x] manual inspection cites representative page-level artifacts or result rows for at least the page-12 seal/text-bearing case and one known fail-style case such as the page-122 caption leak
  - [x] the story ends with one explicit current-repo decision: either the remaining C5 residue is still required, or a concrete simplification follow-up is named because removal now looks honestly buildable
- [x] Canonical truth surfaces remain aligned with the outcome:
  - [x] `docs/evals/registry.yaml`, `docs/runbooks/crop-eval-workflow.md`, and any directly affected crop story/docs no longer imply that the 40-crop surface alone is the full C5 deletion gate if that is not still true
  - [x] if the result changes documented support claims or graduation truth, `tests/fixtures/formats/_coverage-matrix.json` and relevant methodology surfaces are updated honestly
  - [x] after `make methodology-compile`, generated `docs/stories.md` and `docs/methodology/graph.json` include the new story and stay consistent with the authored truth

## Out of Scope

- Deleting `trim_layout_text` or `rescue_caption_second_pass` without fresh current-pass evidence that the widened surface plus artifact review justify that removal
- Reopening broad crop detector model selection or repeating the already-failed Story 184 "remove caption assist immediately" move on the same evidence
- Reclassifying `C4` as unresolved; the maintained single-stage deletion gate still passes on the bounded detector surface
- Unrelated handwritten OCR, intake-routing, or Dossier handoff work
- Broad repo-wide benchmark redesign outside the crop seam unless the chosen page-level C5 surface proves that a small shared harness change is necessary

## Approach Evaluation

- **Simplification baseline**: first prove whether the existing 40-crop surface can be widened cheaply enough to answer the spec's page-level deletion question before inventing a new eval stack. A single LLM call is not the missing proof; the missing piece is an inspectable page-level validation surface that matches `C5`.
- **AI-only**: possible for pass/fail judgments on rendered page/crop outputs, but weak if it hides the page/crop mapping or makes the truth surface expensive and non-reproducible.
- **Hybrid**: likely strongest. Keep deterministic page/crop fixture ownership plus explicit fail reasons, then use the smallest model-assisted judgment surface that can score whether page-level crops still include non-illustration text strongly enough to require `trim_layout_text` or bounded caption assist.
- **Pure code**: acceptable only if the chosen page-level signal can be derived deterministically from existing crop/publication artifacts without losing semantic fidelity. This is less likely because the remaining residue is about visual/text-boundary judgment, not just metadata comparison.
- **Repo constraints / prior decisions**: Story 183 repaired the crop benchmark substrate and promoted the bounded 40-crop C5 surface; Story 184 proved the first caption-assist removal attempt regressed the page-12 seal/text-bearing case; Story 198 deleted the retired retry/validator residue and left only bounded caption assist plus `trim_layout_text`; Story 207 refreshed the C4 proof contract and kept the crop truth surfaces aligned. `docs/spec.md` still says C5 needs broader page-level evidence before the trim heuristics can be deleted. No crop-specific ADR exists.
- **Existing patterns to reuse**: `benchmarks/tasks/crop-validation.yaml`, `benchmarks/golden/crop-validation.json`, `benchmarks/input/crop-validation-b64/`, `tests/test_crop_benchmark_substrate.py`, `tests/test_crop_runtime_recipe_contract.py`, `docs/runbooks/crop-eval-workflow.md`, and the reviewed Onward publication seam used in Stories 184/198/207.
- **Eval**: the deciding proof is whether a widened page-level surface can show, on current repo evidence, that the maintained crop/build seam no longer needs `trim_layout_text` or bounded caption assist. If the new surface still fails on the page-12 or page-122 class, the honest outcome is to keep the residue and stop.

## Tasks

- [x] Freeze the current C5 gap from repo evidence:
  - [x] inspect the current `crop-validation` contract and record exactly why it is insufficient for the spec's broader page-level deletion gate
  - [x] inspect the maintained Onward residue evidence from Stories 184 and 198 so the widened surface targets real remaining failure modes instead of abstract "more breadth"
  - [x] confirm whether the same reviewed Onward run root and source-image inputs are still available for current-pass proof in this environment
- [x] Choose the smallest honest C5 page-level surface:
  - [x] decide whether to widen `benchmarks/tasks/crop-validation.yaml` directly or create a sibling page-level task/config
  - [x] define the checked-in fixture/input shape and explicit pass/fail or score semantics
  - [x] keep the surface reproducible from this repo and current local shared inputs; do not reintroduce hidden external benchmark dependencies
- [x] Land the chosen benchmark/truth-surface implementation:
  - [x] add or update the task config, golden data, scorer logic, and focused substrate-integrity coverage
  - [x] if the chosen surface needs page-plus-crop context, extend the prompt helper or add a sibling prompt path without mutating the current detector/C4 surface semantics accidentally
  - [x] update `docs/evals/registry.yaml` and `docs/runbooks/crop-eval-workflow.md` so the widened surface is the explicit C5 deletion-gate surface or is clearly documented as a new companion surface
  - [x] anchor any new maintained score or decision in a tracked `docs/evals/attempts/` proof note instead of depending only on ignored promptfoo result JSON
  - [x] update any directly affected crop docs/story references so the repo no longer implies the 40-crop surface alone is the page-level gate if that is no longer true
- [x] Run the current-pass proof and make one explicit decision:
  - [x] rerun the widened surface and manually inspect representative evidence
  - [x] if the result still says the residue is needed, record that blocker honestly and do not touch the maintained runtime
  - [x] if the result suggests the residue can be deleted, either name the exact follow-up simplification story or absorb only the smallest same-boundary simplification if validation remains coherent
- [x] Reviewed `tests/fixtures/formats/_coverage-matrix.json` and methodology state impact; this proof-only story does not change documented format coverage or graduation truth
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] Pipeline behavior did not change and no runtime simplification landed, so a fresh `driver.py` rerun is not required in this proof-only story
  - [x] Agent tooling did not change; `make skills-check` is not required
- [x] Evals and goldens changed, the fresh reruns were completed, and `docs/evals/registry.yaml` was updated in the same pass
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every C5 claim cites exact page/crop fixtures, result files, and inspected artifacts
  - [x] T1 — AI-First: use the smallest model-assisted judgment surface that can answer the page-level deletion question; do not hardcode text-boundary policy into ad hoc code first
  - [x] T2 — Eval Before Build: widen the proof surface before deleting the remaining crop residue
  - [x] T3 — Fidelity: page-level crop/publication decisions preserve the source content faithfully and do not hide duplicate or leaked text
  - [x] T4 — Modular: keep the new proof surface bounded to the crop eval/runtime seam instead of growing a generic benchmark overhaul
  - [x] T5 — Inspect Artifacts: manually inspect representative page-level cases, not just aggregate scores

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

- **Owning module / area**: crop benchmark/eval surfaces under `benchmarks/` plus the maintained crop runtime proof seam that currently lives in `configs/recipes/recipe-onward-images-html-mvp.yaml`, `modules/extract/crop_illustrations_guided_v1/main.py`, and the reviewed Onward publication artifacts.
- **Methodology reality**: this belongs primarily to `spec:4`, with execution-truth ownership in `spec:8`. `docs/methodology/state.yaml` says `spec:4` substrate exists, `C4 = converge`, and `C5 = climb`; `spec:8` substrate exists and `B1 = hold`. The relevant coverage rows are `scanned-pdf-tables` and `image-directory-scans`, which both currently inherit `illustration_extraction = 0.9703` from the maintained detector proof while C5 still lacks the broader page-level deletion signal the spec calls for.
- **Substrate evidence**: verified in this pass that `benchmarks/tasks/crop-validation.yaml`, `benchmarks/golden/crop-validation.json`, `benchmarks/input/crop-validation-b64/` (40 files), `benchmarks/input/source-pages-b64/` (16 files), `tests/test_crop_benchmark_substrate.py`, `tests/test_crop_runtime_recipe_contract.py`, `configs/recipes/recipe-onward-images-html-mvp.yaml`, and `modules/extract/crop_illustrations_guided_v1/main.py` all exist locally. Also verified the shared reviewed proof seam still exists in this environment at `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/` and `/Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images/`.
- **Data contracts / schemas**: no stamped pipeline schema change is expected for the proof-surface work itself. The main contracts in scope are the promptfoo task vars, scorer outputs, golden semantics, and the authored registry/runbook/spec language that defines what C5's deletion gate really measures. If the story later carries a runtime simplification across artifact boundaries, update `schemas.py` first if any stamped fields change.
- **File sizes**: likely touch points are `benchmarks/tasks/crop-validation.yaml` (327 lines), `benchmarks/golden/crop-validation.json` (210), `docs/evals/registry.yaml` (1955), `docs/runbooks/crop-eval-workflow.md` (106), `tests/test_crop_benchmark_substrate.py` (73), `tests/test_crop_runtime_recipe_contract.py` (76), `configs/recipes/recipe-onward-images-html-mvp.yaml` (182), and `modules/extract/crop_illustrations_guided_v1/main.py` (3676). Avoid broad surgery in `modules/extract/crop_illustrations_guided_v1/main.py`; prefer benchmark/truth-surface changes first.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/registry.yaml`, `docs/runbooks/crop-eval-workflow.md`, `tests/fixtures/formats/_coverage-matrix.json`, and Stories 183/184/198/207. No narrower crop-specific ADR or note was found under `docs/decisions/`, `docs/scout/`, or `docs/notes/`.

## Files to Modify

- `docs/stories/story-209-crop-c5-page-level-deletion-gate.md` — story body, work log, and close-out evidence for the new C5 proof line
- `docs/stories.md` — generated story index after `make methodology-compile`
- `benchmarks/tasks/crop-validation.yaml` — widen or refactor the current C5-linked task if it remains the right vehicle (327 lines)
- `benchmarks/tasks/crop-page-level-deletion-gate.yaml` — likely cleaner sibling task if the current crop-only validator should remain bounded and unchanged
- `benchmarks/golden/crop-validation.json` — widen the checked-in verdict/golden surface if the current 40-crop corpus is kept and expanded (210 lines)
- `benchmarks/golden/crop-page-level-deletion-gate.json` — likely sibling golden for explicit page-level verdicts if the new surface stays distinct
- `benchmarks/prompts/_image-helpers.js` — small shared helper change if the new surface needs page image plus crop image in one provider-safe prompt
- `benchmarks/prompts/validate-page-level-crop.js` — likely new prompt if the page-level gate becomes a sibling task
- `benchmarks/scorers/crop_validation_scorer.py` — shared scorer extended so the page-context golden can stay on the same pass/fail contract
- `benchmarks/input/README.md` — fixture inventory updated after the page-context overlap corpus added tracked source pages
- `benchmarks/README.md` — benchmark catalog updated so the bounded crop-only surface and the broader page-context gate are both described honestly
- `docs/evals/registry.yaml` — record the widened C5 deletion-gate surface and fresh current-pass evidence (1955 lines)
- `docs/evals/attempts/` — tracked proof note if the maintained result must stay portable while raw promptfoo JSON remains ignored
- `docs/runbooks/crop-eval-workflow.md` — explain the widened C5 surface and its relation to the maintained crop/runtime seam (106 lines)
- `tests/test_crop_benchmark_substrate.py` — protect the chosen widened surface from clean-checkout drift (73 lines)
- `tests/test_crop_runtime_recipe_contract.py` — update only if the story changes what residue the maintained recipe is expected to keep explicitly (76 lines)
- `configs/recipes/recipe-onward-images-html-mvp.yaml` — only if the story lands a small same-boundary runtime simplification after the widened proof passes (182 lines)
- `modules/extract/crop_illustrations_guided_v1/main.py` — only if a bounded runtime deletion actually ships from this story; otherwise leave untouched (3676 lines)

## Redundancy / Removal Targets

- The current assumption that the 40-crop `crop-validation` surface is the only maintained C5 truth surface if the page-level gate requires a wider or sibling task
- Any docs that imply the bounded 40-crop surface alone answers the full `C5` deletion question
- If the widened proof clears the residue honestly, the maintained runtime's explicit dependence on `trim_layout_text` or bounded caption assist becomes a candidate follow-up removal target rather than permanent architecture

## Notes

- New story justification: this is the same crop problem line as Stories 183/184/198/207, but a new ID is honest because the validation boundary is different. Story 183 repaired and promoted the bounded C5 surface, Story 184 and Story 198 simplified the maintained runtime as far as current proof allowed, and Story 207 aligned the C4 proof surfaces. Story 209 is the next explicit proof-surface expansion: establish the broader page-level deletion gate that the spec still requires before the remaining crop residue can be removed honestly.
- The preferred outcome is not predetermined. An honest success for this story could be either:
  - proving the remaining C5 residue is still required and making that explicit with stronger evidence, or
  - proving the residue can now be simplified and naming the exact next move.
- Do not repeat the already-failed Story 184 "remove caption assist on the same evidence" path. The widened proof surface must answer a new question, not replay a closed one.

## Plan

### Eval-First Baseline

- Fresh current-pass baseline rerun completed on the existing maintained C5
  surface:
  - command: `source ~/.nvm/nvm.sh && nvm use 24 > /dev/null 2>&1 && cd benchmarks && promptfoo eval -c tasks/crop-validation.yaml --no-cache --filter-providers 'google:gemini-3.1-flash-lite-preview' --filter-prompts 'caption-focus' --output results/story209-crop-validation-baseline.json -j 1`
  - result: `40/40` passes, `0` failures, `0` errors, mean score `1.0`, duration `2m 6s`, total tokens `59086`
  - inspected rows: `page-012-001` still scores a clean pass as integral text; `page-122-000` still scores a clean fail for caption leakage
- Conclusion: the current dedicated `crop-validation` surface is still healthy
  and still distinguishes the known residue cases, but it remains a crop-only
  validator. It does not answer the wider page-level deletion question that
  blocks honest removal of `trim_layout_text` or bounded caption assist.

### Recommended Approach

1. Freeze the exact proof gap without mutating the current C4 or crop-only C5
   surfaces (`S`)
   - Files: this story, `docs/evals/registry.yaml`, `docs/runbooks/crop-eval-workflow.md`
   - Change: record explicitly why the existing surfaces are insufficient:
     - `crop-validation` prompt/scorer only see the crop image, not the source page or crop provenance
     - `image-crop-extraction` / `single-model-crop-detection` are detector-quality surfaces, not runtime-publication C5 proof
     - concrete mismatch evidence from this pass:
       - `Image011` detector golden second box is `[611, 4528, 4472, 5918]`, while the reviewed runtime crop `page-012-001.jpg` is narrower at `[602, 4521, 3713, 5900]` and still carries a `caption_box`
       - `Image121` detector golden expects `3` crops, while the reviewed runtime page `122` currently publishes only `page-122-000.jpg` and `page-122-001.jpg`
   - Done looks like: the repo no longer implies that either existing surface is already the wider C5 deletion gate

2. Add a sibling page-level deletion-gate task instead of widening
   `crop-validation` in place (`M`)
   - Files: likely `benchmarks/tasks/crop-page-level-deletion-gate.yaml`,
     `benchmarks/golden/crop-page-level-deletion-gate.json`,
     `benchmarks/prompts/validate-page-level-crop.js`,
     `benchmarks/scorers/crop_page_level_deletion_gate_scorer.py`,
     `tests/test_crop_benchmark_substrate.py`, and possibly
     `benchmarks/prompts/_image-helpers.js`
   - Change: keep the current 40-crop validator intact as the bounded crop-only
     surface, and add a companion task that measures the page-level C5 question
     on the repo-owned 13-page detector corpus plus explicit runtime-linked
     verdicts for the critical residue cases (`Image011` / page 12,
     `Image121` / page 122, and representative clean pages)
   - Structural health note: if the prompt needs both the source page and the
     extracted crop, extend the shared helper surgically so provider-specific
     image payload logic stays in one place instead of being duplicated inside a
     new prompt file
   - Done looks like: the new task runs from a clean checkout, has explicit
     goldens/verdicts, and leaves the existing `crop-validation` semantics
     unchanged

3. Anchor the maintained proof portably (`XS`)
   - Files: `docs/evals/attempts/`, `docs/evals/registry.yaml`,
     `docs/runbooks/crop-eval-workflow.md`
   - Change: follow the Story 207 pattern by summarizing any new maintained
     result in a tracked proof note rather than depending only on ignored
     `benchmarks/results/*.json`
   - Done looks like: registry/runbook can cite a repo-backed proof artifact
     even though raw promptfoo JSON remains a local execution artifact

4. Run the new surface, inspect artifacts, and make one explicit decision (`M`)
   - Files: the new task/golden/scorer/result paths plus the reviewed Onward
     seam under `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/`
   - Change:
     - run the new page-level surface on the current tip
     - manually inspect the resulting rows for at least page 12 and page 122
     - re-open the reviewed runtime-publication seam (`illustration_manifest.jsonl`,
       `page-012-001.jpg`, `page-122-000.jpg`, `chapter-003.html`,
       `chapter-024.html`) so the benchmark decision still ties back to the
       maintained artifact surface
   - Decision rule:
     - if the new surface still says the residue is needed, stop at truth-surface
       cleanup and keep runtime code untouched
     - if the new surface says deletion now looks honest, recommend a focused
       follow-up simplification story by default; only absorb a tiny same-boundary
       runtime deletion here if the diff and validation stay obviously coherent
   - Done looks like: the story ends with an explicit current-repo decision on
     whether the residue is still required

### Options Considered

- Widen `crop-validation` directly: not recommended. It would conflate the
  bounded crop-only validator with the broader page-level deletion gate and make
  the registry/runbook history harder to interpret.
- Use the reviewed external Onward run root as the only proof surface: not
  recommended as the maintained benchmark because it is not clean-checkout
  reproducible. It remains useful as artifact sanity evidence after the new
  repo-owned task runs.

### Impact Analysis

- Primary blast radius: benchmark harness files under `benchmarks/` plus the
  registry/runbook truth surfaces
- Secondary blast radius: the shared prompt helper if multi-image support is
  needed for the page-level task
- Runtime code is not part of the first implementation pass; any later runtime
  deletion should happen only after the new surface proves it honestly and after
  a separate driver-backed artifact check

### Human-Approval Blockers

- No substrate blocker is visible. The key repo-owned ingredients already exist:
  the 40-crop corpus, the 13 full-page detector fixtures, the current crop-only
  validator, and the reviewed Onward publication seam.
- Small scope delta already folded in:
  - add a tracked proof note because `benchmarks/results/*.json` is ignored
  - allow a small `_image-helpers.js` extension if the new task needs both page
    and crop images in one prompt

### What Done Looks Like For This Build Pass

- The repo keeps the current bounded `crop-validation` surface intact and gains
  a distinct page-level C5 deletion-gate task
- The new task is clean-checkout runnable and protected by substrate-integrity
  tests
- Registry and runbook tell the truth about both surfaces and cite a tracked
  proof note
- The story records a current-pass yes/no decision on whether `trim_layout_text`
  and bounded caption assist still need to remain

## Outcome

- Story 209 landed a sibling page-context C5 proof surface instead of widening
  the bounded crop-only validator in place.
- The new surface passes cleanly on the checked-in `22`-case overlap corpus,
  but its own labeled cases still show `5` current-runtime fail examples.
- Current-repo decision: keep `trim_layout_text` and the remaining bounded
  caption-assist residue in place; no runtime simplification shipped from this
  story.

## Work Log

20260410-2005 — create-story: created Story 209 after `/triage` was updated to treat phase as default work pressure rather than defaulting to `no-op`. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/registry.yaml`, `docs/runbooks/crop-eval-workflow.md`, `tests/fixtures/formats/_coverage-matrix.json`, and Stories 183/184/198/207. Result: a new story ID is honest instead of reopening Story 183 or Story 198 because the prior crop line closed benchmark-substrate repair, bounded runtime simplification, and truth-surface alignment, while the remaining open work is a different validation boundary: widen the C5 deletion gate from the current 40-crop surface to the broader page-level proof the spec still requires before deleting `trim_layout_text` or the remaining bounded caption-assist residue. Verified current substrate in this pass: `benchmarks/input/crop-validation-b64/` still has 40 files, `benchmarks/input/source-pages-b64/` still has 13 files, `benchmarks/tasks/crop-validation.yaml`, `benchmarks/golden/crop-validation.json`, `tests/test_crop_benchmark_substrate.py`, and `tests/test_crop_runtime_recipe_contract.py` all exist locally, and the reviewed Onward proof seam still exists at `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/` with source images under `/Users/cam/Documents/Projects/codex-forge/input/onward-to-the-unknown-images/`. Status is `Pending` because the proof, benchmark, and reviewed-artifact substrate are all present and the next move is concrete. Next step: run `make methodology-compile`, verify the generated views include Story 209, and then use `/build-story` to choose the smallest honest page-level deletion-gate surface.
20260410-2346 — /build-story exploration: re-read `docs/ideal.md`, `docs/spec.md` (`spec:4`, `spec:8`), `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/registry.yaml`, `docs/runbooks/crop-eval-workflow.md`, `tests/fixtures/formats/_coverage-matrix.json`, and dependency Stories 183/198/207 before tracing the current crop benchmark seam. Verified no narrower crop-specific ADR exists beyond the previously recorded search across `docs/decisions/`, `docs/scout/`, and `docs/notes/`. Critical substrate verified in code and artifacts: `benchmarks/tasks/crop-validation.yaml` and `benchmarks/scorers/crop_validation_scorer.py` currently operate on crop-only image inputs; `benchmarks/tasks/image-crop-extraction.yaml` and `benchmarks/golden/image-crops.json` provide a separate 13-page detector-quality surface; `benchmarks/input/source-pages-b64/` contains repo-owned full-page fixtures for `Image011` (page 12) and `Image121` (page 122); and the reviewed runtime-publication seam still exists at `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/illustration_manifest.jsonl` plus `output/html/chapter-003.html` and `output/html/chapter-024.html`. Important surprises found: the existing C4 and C5 surfaces are related but not interchangeable. `Image011` detector golden crop 2 is `[611, 4528, 4472, 5918]`, while the reviewed runtime crop `page-012-001.jpg` is narrower at `[602, 4521, 3713, 5900]` and still carries a `caption_box`; `Image121` detector golden expects `3` crops, while the reviewed runtime page 122 currently publishes only `page-122-000.jpg` and `page-122-001.jpg`. That means the existing detector scorer is not already the wider C5 runtime deletion gate. Additional portability constraint: `benchmarks/.gitignore` still ignores `results/*.json`, so any new maintained proof must be summarized in a tracked `docs/evals/attempts/` note rather than leaving canonical docs dependent on local raw JSON. Result: Story 209 remains honestly buildable, but the smallest honest implementation is now clearer than at story creation — add a sibling page-level C5 surface instead of mutating the current crop-only validator or pretending the existing C4 scorer already answers the runtime deletion question. Next step after approval: implement the sibling benchmark surface, keep the current 40-crop validator intact, and anchor the new proof in a tracked attempt note.
20260410-2349 — eval baseline: ran `source ~/.nvm/nvm.sh && nvm use 24 > /dev/null 2>&1 && cd benchmarks && promptfoo eval -c tasks/crop-validation.yaml --no-cache --filter-providers 'google:gemini-3.1-flash-lite-preview' --filter-prompts 'caption-focus' --output results/story209-crop-validation-baseline.json -j 1` to remeasure the existing maintained C5 surface on current code. The run completed successfully with `40/40` passes, `0` failures, `0` errors, mean score `1.0`, duration `2m 6s`, and total tokens `59086`; the local raw result JSON exists at `benchmarks/results/story209-crop-validation-baseline.json` and is about `131 MB`. Manual inspection in the same pass confirmed the key residue examples still behave as expected on the crop-only surface: `page-012-001` returned a clean `pass` / TN with the reason that the text is integral to the seal image, while `page-122-000` returned a clean `fail` / TP with the reason that the crop includes the page caption text below the photograph. Result: the current dedicated `crop-validation` task is still healthy and still distinguishes the known pass/fail cases, which means the open problem is not benchmark breakage or a failing maintained score. The honest remaining gap is that this surface still sees only the cropped image and therefore still does not answer whether page-level detection plus the reviewed runtime-publication seam can delete `trim_layout_text` or bounded caption assist. Next step after approval: build the sibling page-level deletion-gate surface and use it, not the already-passing crop-only validator, to make the residue decision.
20260411-0018 — implementation: added the sibling page-context proof surface under `benchmarks/tasks/crop-page-level-deletion-gate.yaml` with its tracked verdict file `benchmarks/golden/crop-page-level-deletion-gate.json`, the new prompt `benchmarks/prompts/validate-page-level-crop.js`, and a small multi-image extension in `benchmarks/prompts/_image-helpers.js` so one prompt can see both the full source page and the extracted crop without changing existing detector or crop-only semantics. Extended `benchmarks/scorers/crop_validation_scorer.py` so the page-context task can stay on the same pass/fail contract while reading a separate golden path, added `tests/test_crop_benchmark_substrate.py` coverage for the new page/crop overlap corpus, updated `benchmarks/input/README.md`, and checked in three additional page fixtures (`Image017`, `Image091`, `Image125`) so the source-page pool now covers all `22` page-context cases from a clean checkout. Result: the repo now owns a reproducible page-level C5 deletion-gate surface instead of depending on crop-only judgment or an external reviewed run root.
20260411-0025 — first page-context proof run: ran `HOME=/tmp/story209-promptfoo-home PROMPTFOO_DISABLE_WAL_MODE=true /bin/bash -lc 'source /Users/cam/.nvm/nvm.sh && nvm use 24 >/dev/null 2>&1 && cd /Users/cam/.codex/worktrees/35de/doc-web/benchmarks && promptfoo eval -c tasks/crop-page-level-deletion-gate.yaml --no-cache --output results/story209-crop-page-level-deletion-gate-g31-page-context.json -j 1'` after a one-case smoke check with `--filter-first-n 1 --no-write`. The clean full run produced `21/22` passes with a single miss on `page-126-000`; manual inspection of `benchmarks/results/story209-crop-page-level-deletion-gate-g31-page-context.json` showed the model incorrectly treated neighboring plaque text as minimal and still answered `pass`. Result: the new substrate and labels were sound enough to run from a clean checkout, but the initial page-context prompt under-enforced adjacent-text leakage and needed one bounded prompt revision rather than a golden rewrite.
20260411-0029 — prompt fix and final proof: tightened `benchmarks/prompts/validate-page-level-crop.js` so surrounding text from adjacent plaques or neighboring visuals must fail, then reran `HOME=/tmp/story209-promptfoo-home PROMPTFOO_DISABLE_WAL_MODE=true /bin/bash -lc 'source /Users/cam/.nvm/nvm.sh && nvm use 24 >/dev/null 2>&1 && cd /Users/cam/.codex/worktrees/35de/doc-web/benchmarks && promptfoo eval -c tasks/crop-page-level-deletion-gate.yaml --no-cache --output results/story209-crop-page-level-deletion-gate-g31-page-context-v2.json -j 1'`. The final run passed cleanly at `22/22`, `0` failures, `0` errors, mean score `1.0`, total tokens `56945`, and duration `61863 ms`. Manual row inspection from the result JSON confirmed `page-012-001` as `pass` / TN, `page-018-000` as `fail` / TP, `page-122-000` as `fail` / TP, and `page-126-000` as `fail` / TP. Re-opened the reviewed maintained seam in `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/` and confirmed `output/html/chapter-003.html` still publishes `page-012-001.jpg` with the `Hon. Gordon MacMurchy` / `Celebrate Saskatchewan` caption context, while `output/html/chapter-024.html` still publishes `page-122-000.jpg` and `page-122-001.jpg`. Result: the widened surface now answers the spec's broader page-level deletion question honestly, and the answer is still "keep the surviving C5 residue." The checked-in overlap corpus itself contains `4` explicit fail-labeled current-runtime cases, so Story 209 does not delete `trim_layout_text` or the remaining bounded caption assist.
20260411-0044 — verification and generated surfaces: reran `python -m pytest tests/test_crop_benchmark_substrate.py -q` (`4 passed in 0.07s`), `make lint` (`ruff check` clean), `make test` (`554 passed, 4 warnings in 886.00s`), `make methodology-compile` (rewrote `docs/stories.md` and `docs/methodology/graph.json`), and `make methodology-check` (graph current). The only fresh warnings were pre-existing Pydantic deprecation warnings in `modules/portionize/portionize_headers_numeric_v1/main.py`; they are unrelated to the crop seam touched here. Result: the Story 209 build pass is complete and the generated methodology surfaces are aligned, but the story stays `In Progress` pending a separate `/validate` pass and close-out via `/mark-story-done`.
20260411-0050 — mark-story-done: reran `make lint` (`ruff check` clean) and `make test` (`554 passed, 4 warnings in 652.05s`) on the current branch tip, with the same unrelated pre-existing Pydantic deprecation warnings still limited to `modules/portionize/portionize_headers_numeric_v1/main.py`. Rechecked the page-context proof artifact at `benchmarks/results/story209-crop-page-level-deletion-gate-g31-page-context-v2.json`, confirmed the representative pass/fail rows for `page-012-001`, `page-018-000`, `page-122-000`, and `page-126-000`, and re-opened the maintained publication seam in `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/chapter-003.html` and `chapter-024.html`. Story status is now `Done`; workflow gates are complete; the outcome remains unchanged: keep `trim_layout_text` and the remaining bounded caption-assist residue. Next step: `/check-in-diff`.
20260424-1930 — post-closeout model refresh application: after the GPT-5.5 API refresh and corrected-golden reruns, narrowed `benchmarks/tasks/crop-page-level-deletion-gate.yaml` to the current corrected-golden winner, `openai:responses:gpt-5.5`, while keeping the bounded crop-only `crop-validation` surface on Gemini 3.1 Flash Lite. The applied full rerun `benchmarks/results/crop-page-level-deletion-gate-gpt55-responses-current-20260424.json` passed `22/22` with `0` failures and `0` provider errors; the fresh Gemini corrected-golden rerun is now recorded as `21/22` because it misses `page-122-001` neighboring-portrait leakage. Added a narrow substrate test so the page-context task cannot silently drift back to a weaker default provider. Result: Story 209 stays Done, but its maintained validator and truth surfaces now reflect the current best measured model and the corrected `5` fail-labeled residue cases.
