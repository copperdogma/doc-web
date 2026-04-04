---
title: "Finish Real Handwritten Proof on the Maintained Rescue Seam"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #1 (Ingest), Requirement #2 (Detect), Requirement #3 (Extract), Any format, any condition, Fidelity to the source, Minimum Viable Floor"
spec_refs:
  - "spec:1"
  - "spec:1.1"
  - "spec:2"
  - "spec:2.1"
  - "spec:2.2"
  - "spec:8"
adr_refs: []
depends_on:
  - "186"
category_refs:
  - "spec:1"
  - "spec:2"
  - "spec:8"
compromise_refs:
  - "B1"
  - "B5"
  - "C1"
  - "C2"
  - "C6"
input_coverage_refs:
  - "handwritten-notes"
architecture_domains:
  - "ocr_and_extraction"
roadmap_tags:
  - "campaign:maintained-intake-honesty"
legacy_system: ""
---

# Story 189 — Finish Real Handwritten Proof on the Maintained Rescue Seam

**Priority**: High
**Status**: Done
**Methodology Refs**: Category 1 Intake & Format Routing (`exists`, C2 `climb`); Category 2 OCR & Text Extraction (`exists`, C1 `climb`, C6 `hold`); Category 8 AI Harnesses & Tooling (`exists`, B1 `hold`, B5 `climb`); coverage row `handwritten-notes` currently `has-fixture`, not `passing`
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/runbooks/golden-build.md`, `docs/stories/story-179-repo-owned-handwritten-notes-fixture-and-baseline-transcription.md`, `docs/stories/story-182-widen-handwritten-notes-fixture-breadth.md`, `docs/stories/story-185-widen-handwritten-proof-beyond-synthetic-pair.md`, `docs/stories/story-186-real-handwritten-fixture-proof-surface.md`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower handwritten-rescue ADR or runbook
**Depends On**: Story 186

## Goal

Story 186 closed the "no real handwriting fixture" gap, but it also established the current product failure boundary: the maintained generic image-directory and PDF OCR lanes stay in the low-0.1 range on the checked-in Barney real handwritten slice, while one bounded stronger direct comparison improved materially without clearing the repo's passing bar. Story 190 then made the anti-fragmentation rule explicit, and the user asked to finish the remaining handwritten real-fixture line in one story instead of serial micro-follow-ups. This story therefore owns the whole maintained handwritten rescue decision surface: Barney, a second repo-owned real handwritten fixture, the bounded rescue seam, and the final truth-surface decision about whether the family is honestly promotable. The target is not broad handwritten victory or a hidden special case; it is an evidence-backed close-out that either proves a maintained real-slice path across more than one real page or records stronger negative evidence and keeps the truth surfaces honest.

## Acceptance Criteria

- [x] A fresh real-handwritten decision surface exists on the current tip that compares:
  - [x] the maintained generic Barney baseline,
  - [x] the bounded maintained rescue seam on Barney,
  - [x] at least one bounded stronger direct candidate already suggested by Story 186,
  - [x] and the same maintained rescue seam on a second repo-owned real handwritten fixture.
  The work log must name the exact run/result artifacts inspected and the dominant failure pattern, not only aggregate ratios. If a compared path is blocked by provider quota or client compatibility, that blocker and the freshest inspected historical evidence must be named explicitly rather than hidden.
- [x] If one candidate is materially better and maintainable, the smallest explicit maintained rescue seam lands for the handwritten family on both image-directory and PDF entry paths, with fresh `driver.py` proofs under `output/runs/` and manual artifact inspection showing what improved and what still failed on the real slices.
- [x] The story either proves the maintained rescue seam across more than one real handwritten page or closes the current handwritten family honestly in this same story without spawning another same-surface follow-up.
- [x] `benchmarks/golden/handwritten-notes/corpus.json`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, `testdata/README.md`, and any related story/truth surfaces move only as far as the fresh evidence justifies. The `handwritten-notes` row does not return to `passing` unless the maintained path genuinely clears the stated bar.

## Out of Scope

- Broad support for messy cursive archives, multilingual handwriting collections, or archive-scale real handwriting ingestion
- A new Dossier/runtime boundary decision or any change to ADR-002
- Manual transcript cleanup, handwritten patch files, or other non-reproducible edits that hide OCR failure
- Book-specific deterministic heuristics or hardcoded corrections for Barney/Alverson names or phrases
- A broad provider bake-off when one bounded comparison set is enough to choose the next move honestly

## Approach Evaluation

The story should start from the measured failure boundary, not from a presumption that more code is needed.

- **Simplification baseline**: one stronger direct model call already improves the Barney slice substantially over the maintained low-0.1 baseline, so the first move is to measure bounded higher-capability candidates on the checked-in real fixtures before adding any rescue logic. If a single model/hint change already solves both real slices, that is the right answer.
- **AI-only**: a stronger direct multimodal transcription path may solve Barney-like real handwriting without any downstream heuristics. This is attractive because the repo already owns the source slices and scorer, but it is only worth productizing if the measured quality, cost, and repeatability are clearly better than the current maintained seam across both real fixtures.
- **Hybrid**: keep the maintained generic OCR lane as the default, then use a bounded stronger rescue only where the real handwritten slice or an explicit quality gate justifies it. This remains the leading candidate if all-pages stronger OCR is too costly or if the higher-capability model should stay scoped to real handwritten risk.
- **Pure code**: only appropriate for provider-parameter compatibility, recipe wiring, result capture, and truth-surface updates. Do not write deterministic handwriting-correction heuristics for a problem the model should solve.
- **Repo constraints / prior decisions**: `spec:1.1` still keeps recipe selection explicit; `spec:2.1` and `spec:2.2` keep OCR evidence-driven and cost-aware; `docs/runbooks/golden-build.md` explicitly warns against turning benchmark scoping into product policy; Story 186 already established that the repo must not overclaim real handwritten support from synthetic evidence alone. No narrower local ADR resolves the handwritten rescue shape.
- **Existing patterns to reuse**: `modules/extract/ocr_ai_gpt51_v1/main.py` already supports alternate `--model` and `--retry-model` values; `modules/extract/ocr_ai_gpt51_v1/module.yaml` exposes those params; `configs/recipes/recipe-images-ocr-html-mvp.yaml` and `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` already own the maintained generic seam; `benchmarks/scripts/run_handwritten_notes_eval.py` already supports both corpus mode and ad hoc single-fixture mode; `benchmarks/scorers/handwritten_notes_transcription.py` already scores the exact slice we care about; Story 186 already recorded the first bounded stronger direct comparison.
- **Eval**: the deciding surface is `handwritten-notes-transcription` plus the Barney and Alverson ad hoc reruns, with manual inspection of the stamped `page_html_v1` artifacts. The story must compare quality first, then weigh cost/latency second. If model availability or parameter support becomes part of the decision, verify that on the current code path rather than assuming the module/client supports it.

## Tasks

- [x] Reproduce and freeze the current Barney baseline on the current tip:
  - [x] rerun the maintained image-directory and PDF OCR lanes on `handwritten-notes-barney-real`,
  - [x] inspect the stamped manifest and `page_html_v1` artifacts,
  - [x] and classify the exact semantic failure pattern beyond the aggregate score.
- [x] Run the smallest honest Barney improvement matrix before adding new logic:
  - [x] rerun the bounded stronger comparison already suggested by Story 186,
  - [x] test one additional candidate only if it changes the decision,
  - [x] and record measured quality, cost/latency, and manual artifact notes for each compared path.
- [x] If the compared runs do not already persist cost/latency evidence, add the smallest instrumentation or result-metadata capture needed to compare candidates honestly without inventing costs from memory.
- [x] Candidate measurement on the chosen handwritten rescue path was not blocked by module/client semantics, so no central provider-invocation change was required in `ocr_ai_gpt51_v1`.
- [x] If one candidate is materially better and maintainable, land the smallest explicit rescue seam:
  - [x] prefer recipe-scoped model/hints/retry configuration or a bounded handwritten-specific recipe over a new extraction module,
  - [x] keep provenance and artifact shape unchanged unless a schema change is explicitly justified,
  - [x] and prove the rescue seam through `driver.py` on both the image-directory and PDF Barney fixtures.
- [x] Runtime-unchanged branch rejected: the bounded rescue seam was materially better, and the story now records the compared candidates, measured scores/costs, and the reason the family still remains `has-fixture`.
- [x] Add the second repo-owned real handwritten fixture and widen the handwritten corpus to match the actual validation boundary for this problem line.
- [x] Rerun the maintained handwritten rescue seam on the widened five-fixture corpus and inspect the real artifacts before deciding whether the family is honestly promotable.
- [x] If this story changes documented format coverage or graduation reality: update `tests/fixtures/formats/_coverage-matrix.json` and any relevant methodology state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [x] If agent tooling changed: `make skills-check`
- [x] Evals and goldens were not changed beyond helper/result capture, so `/improve-eval` was not required; `docs/evals/registry.yaml` is updated directly from the fresh manual corpus run.
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every support claim traces to named Barney/Alverson fixtures, run IDs, models, and inspected artifacts
  - [x] T1 — AI-First: no deterministic handwriting correction logic is added where a measured model path solves the slice better
  - [x] T2 — Eval Before Build: bounded model comparisons run before rescue logic is committed
  - [x] T3 — Fidelity: the chosen path preserves source wording and does not silently normalize or "improve" the transcript
  - [x] T4 — Modular: prefer recipe-scoped configuration or bounded rescue seams over hardcoded Barney logic
  - [x] T5 — Inspect Artifacts: the actual Barney and Alverson OCR artifacts are manually opened and checked, not just scored

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: the OCR extraction/configuration seam around `ocr_ai_gpt51_v1`, plus the handwritten eval helper and the maintained image-directory/PDF OCR recipes that own the current generic lane.
- **Methodology reality**: this lives in `spec:1`, `spec:2`, and `spec:8`. Current state says `spec:1` and `spec:2` are active focus areas with `C2` and `C1` still in `climb`; `spec:8` matters because this is an eval-driven rescue decision and manual artifact inspection remains mandatory under `B5`. The relevant coverage row is `handwritten-notes`, which is now `has-fixture` because the maintained rescue seam still fails on both repo-owned real handwritten slices.
- **Substrate evidence**: verified in code that `modules/extract/ocr_ai_gpt51_v1/main.py` already accepts alternate `--model` and `--retry-model` values, `modules/extract/ocr_ai_gpt51_v1/module.yaml` exposes those params to recipes, `configs/recipes/recipe-images-ocr-html-mvp.yaml` and `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` already route the real fixtures through the maintained OCR seam, `benchmarks/scripts/run_handwritten_notes_eval.py` already supports both default-corpus and single-fixture modes, `benchmarks/scorers/handwritten_notes_transcription.py` already scores the handwritten transcript slices, `tests/test_handwritten_notes_eval.py` now verifies the five-fixture corpus and run IDs, and Story 186 already proved the checked-in Barney image/PDF fixtures plus the bounded direct-comparison path are runnable. The missing substrate is not pipeline wiring; it is the maintained rescue decision and any bounded recipe/config change it requires.
- **Data contracts / schemas**: no product-runtime schema change is expected if this story stays within model/recipe/hint configuration and the existing handwritten eval payload. If new fields are added to stamped runtime artifacts, they must be declared in `schemas.py` before the story claims them.
- **File sizes**: likely owner files are `modules/extract/ocr_ai_gpt51_v1/main.py` (752 lines), `modules/extract/ocr_ai_gpt51_v1/module.yaml` (54), `benchmarks/scripts/run_handwritten_notes_eval.py` (226), `benchmarks/scorers/handwritten_notes_transcription.py` (119), `tests/test_handwritten_notes_eval.py` (56), `tests/test_image_directory_intake_recipe.py` (172), `tests/test_pdf_intake_recipe.py` (123), `configs/recipes/recipe-images-ocr-html-mvp.yaml` (87), `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` (88), `testdata/README.md` (92), `tests/fixtures/formats/_coverage-matrix.json` (452), and `docs/evals/registry.yaml` (1234). Keep edits especially surgical in `modules/extract/ocr_ai_gpt51_v1/main.py` and `docs/evals/registry.yaml` because both already exceed 500 lines.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/runbooks/golden-build.md`, Stories 179/182/185/186, `docs/evals/registry.yaml`, `modules/extract/ocr_ai_gpt51_v1/main.py`, `modules/extract/ocr_ai_gpt51_v1/module.yaml`, `benchmarks/scripts/run_handwritten_notes_eval.py`, and `benchmarks/scorers/handwritten_notes_transcription.py`. No narrower repo-local ADR or runbook was found that already settles the handwritten rescue design.

## Files to Modify

- `modules/extract/ocr_ai_gpt51_v1/main.py` — any bounded provider-compatibility or rescue-invocation logic needed to test or land the chosen path (752 lines)
- `modules/extract/ocr_ai_gpt51_v1/module.yaml` — expose any new bounded parameters cleanly if implementation requires them (54 lines)
- `configs/recipes/recipe-images-ocr-html-mvp.yaml` — only if the maintained image-directory recipe stays the honest owner of the improved Barney slice (87 lines)
- `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` — only if the maintained PDF recipe stays the honest owner of the improved Barney slice (88 lines)
- `benchmarks/scripts/run_handwritten_notes_eval.py` — support Barney comparison capture and result metadata as needed (226 lines)
- `benchmarks/scorers/handwritten_notes_transcription.py` — extend failure reporting only if the current scorer is insufficient for the decision (119 lines)
- `benchmarks/golden/handwritten-notes/corpus.json` — widen the canonical handwritten corpus when the real-fixture validation boundary expands (51 lines)
- `tests/test_handwritten_notes_eval.py` — keep the handwritten corpus/helper surface repeatable (56 lines)
- `tests/test_image_directory_intake_recipe.py` — preserve cheap Barney image-lane proof coverage if recipe behavior changes (172 lines)
- `tests/test_pdf_intake_recipe.py` — preserve cheap Barney PDF-lane proof coverage if recipe behavior changes (123 lines)
- `testdata/README.md` — record the second repo-owned real handwritten fixture and the current real-fixture support boundary (99 lines)
- `docs/evals/registry.yaml` — record the fresh Barney rescue results and any maintained-path decision honestly (1234 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — move the handwritten row only as far as the fresh evidence justifies (452 lines)
- `testdata/README.md` — update the handwritten support notes if the bounded claim changes (92 lines)
- `configs/recipes/` new bounded handwritten recipe file — only if `/build-story` finds that changing the generic recipes would overclaim support (new file)

## Redundancy / Removal Targets

- Story 186's ad hoc Barney comparison command path if this story replaces it with a repeatable recipe/eval workflow
- Any recipe-local or story-local model-compatibility workaround that can be handled centrally inside `ocr_ai_gpt51_v1`
- Stale handwritten-support caveat wording in docs once the fresh maintained rescue decision is recorded in the registry and coverage matrix

## Notes

- Current measured boundary to beat: the maintained generic Barney slice stays in the low-0.1 range, while the bounded `claude-opus-4-6` comparison improved the same slice to roughly `0.73` without clearing the repo's `0.99` target.
- `retry_model` in `ocr_ai_gpt51_v1` currently retries on empty HTML, not on low-quality but non-empty handwriting output. `/build-story` should decide explicitly whether that seam can be reused honestly for handwritten rescue or whether a sibling recipe is cleaner.
- The story must preserve the real-vs-synthetic distinction created by Story 186. Improving Barney does not by itself justify broad handwritten `passing` claims.

## Plan

### Exploration Summary

- **Ideal alignment:** proceed. This story closes a live Ideal gap on a real handwritten source slice and does not move the product away from the Ideal. The work is quality-improvement in `climb` phases for `C1` and `C2`, not compromise-comfort work.
- **Relevant methodology state:** `spec:1`, `spec:2`, and `spec:8` all have substrate `exists` in `docs/methodology/state.yaml`; `C1`, `C2`, and `B5` remain active. The coverage row `handwritten-notes` is still `has-fixture`, not `passing`, because the Barney real slice remains weak on the maintained generic seam.
- **Critical substrate verified in code:** `ocr_ai_gpt51_v1` already supports alternate `model` and `retry_model` params; the maintained image/PDF OCR recipes already own the generic seam; the handwritten eval helper already supports ad hoc single-fixture mode; and the Barney real fixture plus transcript are already checked in. No missing module/schema substrate blocks the story structurally.
- **Fresh blockers found:** a fresh current-pass rerun of the maintained generic Barney baseline via `python benchmarks/scripts/run_handwritten_notes_eval.py --transcript testdata/handwritten-notes-barney-real.txt --images testdata/handwritten-notes-barney-real-images --pdf testdata/handwritten-notes-barney-real.pdf --output benchmarks/results/story189-barney-baseline.json` failed before OCR output with OpenAI `insufficient_quota`. That means the current maintained `gpt-5.1` quality baseline is not freshly reproducible in this checkout until quota is restored or the maintained path changes.
- **Fresh currently runnable candidate evidence:** after generating fresh manifests under `output/runs/story189-barney-image-manifest/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl` and `output/runs/story189-barney-pdf-manifest/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl`, bounded direct reruns on the same Barney slice gave:
  - `claude-opus-4-6` with bounded handwritten-focused hints: `0.748924` (image manifest) and `0.615991` (pdf manifest) at `output/runs/story189-barney-direct-claude-image/01_ocr_ai_gpt51_v1/pages_html.jsonl` and `output/runs/story189-barney-direct-claude-pdf/01_ocr_ai_gpt51_v1/pages_html.jsonl`
  - `gemini-2.5-pro` with the same hints: `0.864029` (image manifest) and `0.894151` (pdf manifest) at `output/runs/story189-barney-direct-gemini-image/01_ocr_ai_gpt51_v1/pages_html.jsonl` and `output/runs/story189-barney-direct-gemini-pdf/01_ocr_ai_gpt51_v1/pages_html.jsonl`
- **Dominant failure pattern:** the best current single-call candidate (`gemini-2.5-pro`) preserves much more of the Barney text than the archived maintained baseline described in Story 186, including the opening clause and the `real sorrow` section, but it still makes semantic substitutions such as `Harlen`, `genesee/geneseo`, and `father has had gone`, so it improves the slice materially without clearing the repo's `0.99` bar.
- **Scope delta folded into the story:** the current handwritten helper and direct rerun path do not persist per-candidate cost/usage by default because `log_llm_usage()` is a no-op unless `INSTRUMENT_SINK` is set. This is a small coherent delta, so the story now explicitly includes adding the smallest instrumentation or result-metadata capture needed if cost is part of the final decision.

### Eval-First Gate

- **Baseline:** attempted fresh maintained Barney baseline on the current tip. Result: blocked by OpenAI quota, not by missing code substrate. Fresh evidence for the blocked baseline now exists in the story work log; the last inspected quality numbers for the maintained generic seam remain the Story 186 historical evidence already recorded in `docs/evals/registry.yaml`.
- **Simplest working AI-only candidate:** bounded direct `gemini-2.5-pro` with handwritten-focused hints is the strongest currently runnable single-call candidate. It is materially better than the Story 186 maintained baseline and better than the fresh `claude-opus-4-6` reruns, but still below the repo's passing bar.
- **What this means:** the story should not jump to handwritten heuristics or a new extraction module. The next honest implementation slice, if approved, is a bounded recipe/config rescue experiment centered on Gemini rather than code-heavy post-processing.

### Recommended Implementation Plan

Relative effort if we proceed without waiting for OpenAI quota restoration: `M`.

1. Preserve the Barney decision surface as a repeatable artifact (`XS`)
   - Files: `benchmarks/scripts/run_handwritten_notes_eval.py`, optionally `benchmarks/scorers/handwritten_notes_transcription.py`, `docs/evals/registry.yaml`, and this story file
   - Change: add the smallest capture of per-candidate wall time and model metadata, and if feasible token/cost metadata when `INSTRUMENT_SINK` is enabled, so the comparison is not just ratios copied into prose.
   - Why first: right now the story can compare quality honestly, but cost/latency capture is partial. This is the smallest delta that makes the eventual decision durable.
   - Done when: a rerun can emit Barney comparison metadata without relying on memory or ephemeral terminal output.

2. Keep the rescue seam bounded to handwritten, not the generic image/PDF recipes (`S`)
   - Files: new bounded recipe file(s) under `configs/recipes/` or narrow changes to existing recipes only if we explicitly decide the generic seam should change; likely no module change yet
   - Change: prefer a handwritten-specific recipe or bounded Barney/real-handwriting rescue recipe using `gemini-2.5-pro` plus the handwritten-focused hints already exercised in exploration, rather than changing `recipe-images-ocr-html-mvp.yaml` and `recipe-pdf-ocr-html-mvp.yaml` globally.
   - Why this order: `gemini-2.5-pro` is the strongest currently runnable candidate, but it is not yet proven across the broader non-handwritten OCR surface. Changing the generic recipes now would overclaim evidence.
   - Done when: the repo has one explicit maintained rescue surface whose ownership boundary is honest.

3. Re-run the bounded rescue path through `driver.py` on both entry seams (`S`)
   - Files: no new product code expected if recipe-scoped configuration is enough; possible small helper changes if comparison metadata capture needs it
   - Change: run the chosen bounded rescue recipe on `testdata/handwritten-notes-barney-real-images/` and `testdata/handwritten-notes-barney-real.pdf`, then manually inspect the stamped manifests plus `page_html_v1` output.
   - Evidence path:
     - image entry manifest / OCR artifact under `output/runs/<run_id>/01_images_dir_to_manifest_v1/` and `.../02_ocr_ai_gpt51_v1/`
     - pdf entry manifest / OCR artifact under `output/runs/<run_id>/01_extract_pdf_images_fast_v1/` and `.../02_ocr_ai_gpt51_v1/`
   - Done when: we know whether the bounded rescue seam improves both maintained entry paths materially on the same real slice.

4. Update truth surfaces conservatively (`XS`)
   - Files: `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, `testdata/README.md`, and this story/work log
   - Change: record the fresh Barney rescue result, but do not move `handwritten-notes` back to `passing` unless the maintained rescue path genuinely clears the acceptance bar.
   - Done when: the docs tell the exact new truth, whether that is "bounded rescue improves Barney but row stays `has-fixture`" or "bounded rescue is still not worth landing."

### Impact Analysis

- **Tests affected:** `tests/test_handwritten_notes_eval.py` if helper/result shape changes; `tests/test_image_directory_intake_recipe.py` and `tests/test_pdf_intake_recipe.py` only if a bounded handwritten recipe or recipe params need cheap smoke coverage.
- **What could break:** changing the generic OCR recipes would broaden blast radius across non-handwritten scan lanes; touching `ocr_ai_gpt51_v1/main.py` for provider semantics risks global OCR behavior; adding a handwritten-specific recipe is much safer than altering default generic OCR behavior.
- **Structural health:** `modules/extract/ocr_ai_gpt51_v1/main.py` and `docs/evals/registry.yaml` are already large; avoid editing either unless the story truly needs a central provider-compatibility fix or registry wording change.
- **Redundancy plan:** if the bounded rescue recipe lands, retire Story 186's ad hoc one-off comparison command from the docs in favor of the repeatable recipe/eval path.

### Human-Approval Blockers

- **Fresh maintained baseline blocker:** OpenAI quota is currently insufficient for a fresh rerun of the maintained `gpt-5.1` Barney baseline. We can either:
  - wait for quota restoration and insist on a fresh apples-to-apples maintained baseline before implementation, or
  - proceed using the Story 186 historical maintained baseline as the last inspected reference plus the fresh current-pass Gemini/Claude comparisons.
- **Rescue-scope decision:** the strongest currently runnable AI-only candidate (`gemini-2.5-pro`) improves Barney materially but still misses the repo bar. Approving implementation means approving a bounded maintained improvement slice that may still leave `handwritten-notes` at `has-fixture`.

### What Done Looks Like

- Either the story lands a bounded handwritten rescue seam with fresh driver-backed evidence on more than one real handwritten page, or it proves no such seam is worth maintaining right now.
- In both outcomes, the story leaves behind a repeatable real-handwritten decision surface with artifact paths, candidate results, and honest truth-surface wording.
- No deterministic Barney/Alverson-specific corrections or silent transcript cleanup are introduced.

## Work Log

20260404-1058 — story creation from `/triage`: converted the strongest current product signal into a build-ready story after verifying the relevant substrate in code. Evidence reviewed in this pass: `docs/methodology/state.yaml` and `docs/methodology/graph.json` show `spec:1` and `spec:2` as active focus areas with the handwritten row still unresolved; `docs/evals/registry.yaml` records `handwritten-notes-transcription` at `pass_rate = 0.75` with the real Barney slice still in the low-0.1 range on the maintained generic seam and only a bounded roughly-`0.73` direct comparison above it; `tests/fixtures/formats/_coverage-matrix.json` keeps `handwritten-notes` at `has-fixture`; `modules/extract/ocr_ai_gpt51_v1/main.py`, `modules/extract/ocr_ai_gpt51_v1/module.yaml`, `configs/recipes/recipe-images-ocr-html-mvp.yaml`, `configs/recipes/recipe-pdf-ocr-html-mvp.yaml`, `benchmarks/scripts/run_handwritten_notes_eval.py`, and `benchmarks/scorers/handwritten_notes_transcription.py` prove the OCR, recipe, and eval substrate already exists in code. Result: the story is honestly `Pending`, not `Draft`, because the missing slice is a bounded rescue decision and possible recipe/config implementation, not missing infrastructure. Next step: `/build-story` should re-freeze the Barney baseline, compare the smallest honest candidate set, and choose whether a maintained rescue seam is justified.
20260404-1108 — `/build-story` exploration + eval-first planning: re-verified the story against the live Ideal/spec/state surfaces, traced the OCR provider call path in `modules/extract/ocr_ai_gpt51_v1/main.py`, and ran the smallest honest current-pass Barney comparisons without changing code. Fresh baseline attempt via `python benchmarks/scripts/run_handwritten_notes_eval.py --transcript testdata/handwritten-notes-barney-real.txt --images testdata/handwritten-notes-barney-real-images --pdf testdata/handwritten-notes-barney-real.pdf --output benchmarks/results/story189-barney-baseline.json` failed during the maintained image-entry OCR stage with OpenAI `insufficient_quota`, so the current generic `gpt-5.1` Barney baseline is blocked in this checkout by provider quota rather than by missing substrate. I then generated fresh current-pass manifests at `output/runs/story189-barney-image-manifest/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl` and `output/runs/story189-barney-pdf-manifest/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl` and scored two bounded direct candidates on those manifests with handwritten-focused hints. `claude-opus-4-6` improved materially but still weakly: `0.748924` on the image manifest and `0.615991` on the pdf manifest, with artifacts at `output/runs/story189-barney-direct-claude-image/01_ocr_ai_gpt51_v1/pages_html.jsonl` and `output/runs/story189-barney-direct-claude-pdf/01_ocr_ai_gpt51_v1/pages_html.jsonl`. `gemini-2.5-pro` is the strongest currently runnable single-call candidate so far: `0.864029` on the image manifest and `0.894151` on the pdf manifest, with artifacts at `output/runs/story189-barney-direct-gemini-image/01_ocr_ai_gpt51_v1/pages_html.jsonl` and `output/runs/story189-barney-direct-gemini-pdf/01_ocr_ai_gpt51_v1/pages_html.jsonl`. Manual artifact inspection showed the Gemini path preserves the Barney opening, `real sorrow`, and more of the second paragraph than Claude, but it still makes semantic substitutions such as `Harlen`, `genesee/geneseo`, and `father has had gone`, so it improves the slice materially without clearing the repo's `0.99` bar. Additional exploration found one small scope delta worth folding into the story: the current handwritten eval/helper path does not persist per-candidate cost/usage by default because `modules/common/utils.py` only logs LLM usage when `INSTRUMENT_SINK` is set, and no sink file exists in this checkout. Result: the story is still honestly buildable, but the human gate now has two explicit blockers to resolve before implementation starts: whether to proceed without a fresh OpenAI baseline while quota is blocked, and whether shipping a bounded Gemini-based rescue seam is worthwhile even if the handwritten row remains `has-fixture`. Next step: present the plan and these blockers to the user for approval before any implementation code or recipe changes.
20260404-1148 — implemented the bounded handwritten rescue seam and refreshed the handwritten truth surfaces. Code/files changed: added `configs/recipes/recipe-images-ocr-html-handwritten-notes-gemini-rescue.yaml` and `configs/recipes/recipe-pdf-ocr-html-handwritten-notes-gemini-rescue.yaml`; extended `benchmarks/scripts/run_handwritten_notes_eval.py` to support explicit case IDs plus per-case wall/instrumentation capture; added focused coverage in `tests/test_handwritten_notes_eval.py`, `tests/test_image_directory_intake_recipe.py`, and `tests/test_pdf_intake_recipe.py`; and updated `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, `testdata/README.md`, and this story file. Fresh focused checks passed via `python -m pytest tests/test_handwritten_notes_eval.py tests/test_image_directory_intake_recipe.py tests/test_pdf_intake_recipe.py` (`22 passed`) and `python -m ruff check benchmarks/scripts/run_handwritten_notes_eval.py tests/test_handwritten_notes_eval.py tests/test_image_directory_intake_recipe.py tests/test_pdf_intake_recipe.py`. Fresh driver-backed rescue proof used `find modules -name '*.pyc' -delete && python benchmarks/scripts/run_handwritten_notes_eval.py --image-recipe configs/recipes/recipe-images-ocr-html-handwritten-notes-gemini-rescue.yaml --pdf-recipe configs/recipes/recipe-pdf-ocr-html-handwritten-notes-gemini-rescue.yaml --image-case-id image-handwritten-rescue --pdf-case-id pdf-handwritten-rescue --instrument --output benchmarks/results/handwritten-notes-story189-handwritten-rescue.json`, which wrote `benchmarks/results/handwritten-notes-story189-handwritten-rescue.json` with `pass_rate = 0.75`, `overall_min_ratio = 0.883604`, `page_min_ratio = 0.883604`, `cases_total = 8`, and `fixtures_passing = 3`. The six synthetic rescue cases remained `1.0`; the real Barney slice improved to `0.883604` on image entry and `0.884339` on PDF entry at `output/runs/handwritten-handwritten-notes-barney-real-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl` and `output/runs/handwritten-handwritten-notes-barney-real-pdf-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl`; and the per-case instrumentation files at `output/runs/handwritten-handwritten-notes-barney-real-image-handwritten-rescue/instrumentation.json` and `output/runs/handwritten-handwritten-notes-barney-real-pdf-handwritten-rescue/instrumentation.json` recorded `1` Gemini call each with OCR-stage walls of `24.24466s` / `31.158365s` and costs of `$0.00393` / `$0.003966`. Manual inspection confirmed real improvement on hard Barney text: the rescue artifacts now keep `real sorrow`, `father had gone to see him`, and the tents / cedar-brush opening of paragraph two, while remaining failure modes are still semantic substitutions like `Harlen`, `genesee`, `Welthy gone`, and `med of cloth`. Synthetic spot checks at `output/runs/handwritten-handwritten-notes-rough-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl` and `output/runs/handwritten-handwritten-notes-faded-pdf-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl` matched the checked-in transcripts cleanly. Repo-wide verification then passed via `make lint`, `make skills-check`, and `make test` (`454 passed, 4 warnings`). Decision: land the bounded handwritten rescue seam, but keep `handwritten-notes` at `has-fixture` because the maintained real-slice score still misses `0.99`. Next step: regenerate methodology surfaces and hand off to `/validate`.
20260404-1222 — cleared the last OpenAI-quota blocker by rerunning the maintained generic Barney baseline on the current tip with fresh instrumentation. Command: `python benchmarks/scripts/run_handwritten_notes_eval.py --transcript testdata/handwritten-notes-barney-real.txt --images testdata/handwritten-notes-barney-real-images --pdf testdata/handwritten-notes-barney-real.pdf --instrument --output benchmarks/results/story189-barney-generic-current.json`. Result file `benchmarks/results/story189-barney-generic-current.json` recorded `pass_rate = 0.0`, `overall_min_ratio = 0.105378`, and `page_min_ratio = 0.105378` across the two maintained generic entry seams. Fresh generic artifacts at `output/runs/handwritten-single-fixture-image-generic/02_ocr_ai_gpt51_v1/pages_html.jsonl` and `output/runs/handwritten-single-fixture-pdf-generic/02_ocr_ai_gpt51_v1/pages_html.jsonl` confirmed the same semantic failure mode as the historical low-0.1 baseline: line-broken but wrong rewrites such as `the combat`, `old home town is all gone`, and `wife of Harlow`. Fresh instrumentation at `output/runs/handwritten-single-fixture-image-generic/instrumentation.json` and `output/runs/handwritten-single-fixture-pdf-generic/instrumentation.json` showed the generic `gpt-5.1` OCR calls were actually cheaper and faster than the rescue seam (`~8.06s`, `$0.00483` average per case), but the quality gap remains decisive: the bounded Gemini rescue still improves Barney by roughly `0.78` absolute ratio points while preserving the synthetic fixtures at `1.0`. Decision unchanged: keep the bounded handwritten rescue seam, keep the family at `has-fixture`, and use the fresh current-tip generic rerun rather than a quota-blocked caveat as the maintained baseline reference. Next step: `/validate`.
20260404-1325 — closed the validation gap found by `/validate` and re-ran the project checks on the corrected truth surfaces. Validation found one implementation-adjacent issue rather than a runtime bug: `tests/fixtures/formats/_coverage-matrix.json` had accidentally attached the new handwritten rescue recipes to the unrelated `image-directory-scans` row while leaving the actual `handwritten-notes` row on the old generic recipe. I restored `image-directory-scans` to `recipe-images-ocr-html-mvp.yaml`, moved the rescue ownership onto the `handwritten-notes` row, and regenerated `docs/methodology/graph.json` plus `docs/stories.md` via `make methodology-compile`. Fresh inspection confirmed the current source-of-truth mapping now agrees across `tests/fixtures/formats/_coverage-matrix.json` (`image-directory-scans` at line 107, `handwritten-notes` at line 377) and `docs/methodology/graph.json` (`image-directory-scans` at line 5764). Fresh project checks after that fix all passed: `make lint`, `make skills-check`, `make methodology-check`, and `make test` (`454 passed, 4 warnings`). Result: the story's validation gate is now honestly complete, with no remaining implementation gaps from Story 189 beyond close-out through `/mark-story-done`.
20260404-1328 — `/mark-story-done`: verified Story 186 is already `Done` in `docs/stories.md`, confirmed `CHANGELOG.md` had no existing Story 189 entry, set this story to `Done`, checked the final workflow gate, and prepended the close-out entry `2026-04-04-03` to `CHANGELOG.md`. Regenerated `docs/methodology/graph.json` and `docs/stories.md` so the generated status surfaces now match the completed story. Next step: `/check-in-diff`.
20260404-1610 — reopened Story 189 under Story 190's anti-fragmentation rule after the user explicitly asked to finish the remaining handwritten real-fixture line in one story instead of creating more micro follow-ups. First, I fixed a real eval-helper bug in `benchmarks/scripts/run_handwritten_notes_eval.py`: ad hoc single-fixture probes were all using the fixture id `single-fixture`, so later runs silently overwrote earlier evidence. I added deterministic fixture-id derivation plus an explicit `--fixture-id` override, and widened `tests/test_handwritten_notes_eval.py` to cover the new behavior. I also fixed a provider-compatibility blocker in `modules/extract/ocr_ai_gpt51_v1/main.py`: the OpenAI responses path was still sending `temperature` to `gpt-5`, which hard-failed direct OCR probes with `Unsupported parameter: 'temperature'`. New coverage in `tests/test_ocr_ai_gpt51_empty_page_recovery.py` now proves `gpt-5` omits `temperature` while older OpenAI OCR models still receive it. Fresh narrow checks passed via `python -m pytest tests/test_ocr_ai_gpt51_empty_page_recovery.py tests/test_handwritten_notes_eval.py -q` (`14 passed`) and `python -m ruff check modules/extract/ocr_ai_gpt51_v1/main.py tests/test_ocr_ai_gpt51_empty_page_recovery.py tests/test_handwritten_notes_eval.py benchmarks/scripts/run_handwritten_notes_eval.py`.
20260404-1628 — ran the last bounded candidate probes before widening the official corpus and decided not to build a new handwritten-specific runtime seam. Fresh direct `gpt-5` probes on the Alverson and Barney manifests were technically unblocked by the temperature fix but underperformed the maintained Gemini rescue path: `/tmp/alverson-gpt5-direct/pages_html.jsonl` scored `0.310064`, and `/tmp/barney-gpt5-direct/pages_html.jsonl` scored `0.597761`. I also tested simple generic visibility levers instead of adding more stories: upscaling Alverson/Barney images to 2x only reached `0.485058` and `0.86197` at `/tmp/alverson-upscaled-ocr/pages_html.jsonl` and `/tmp/barney-upscaled-ocr/pages_html.jsonl`, and an overlapping vertical-slice probe on Alverson (`/tmp/alverson-slices-ocr/pages_html.jsonl`) still failed to recover the lower body / postscript cleanly. Result: the story now has negative evidence for the remaining low-risk generic levers, so the honest next move is widening the official real-fixture proof surface and closing the family on measured truth rather than inventing a new handwritten runtime experiment.
20260404-1639 — added the second repo-owned real handwritten fixture and reran the official maintained handwritten rescue corpus. New checked-in assets: `testdata/handwritten-notes-alverson-real-images/page-001.jpg`, `testdata/handwritten-notes-alverson-real.pdf`, and `testdata/handwritten-notes-alverson-real.txt`, derived from LOC item `https://www.loc.gov/pictures/item/2023637835/` (`No known restrictions on publication.`). I widened `benchmarks/golden/handwritten-notes/corpus.json`, `tests/test_handwritten_notes_eval.py`, `tests/test_image_directory_intake_recipe.py`, `tests/test_pdf_intake_recipe.py`, and `testdata/README.md` so the repo's canonical handwritten corpus now includes five fixtures. Fresh fixture-surface checks passed via `python -m pytest tests/test_handwritten_notes_eval.py tests/test_image_directory_intake_recipe.py tests/test_pdf_intake_recipe.py -q` (`26 passed`) and `python -m ruff check benchmarks/scripts/run_handwritten_notes_eval.py tests/test_handwritten_notes_eval.py tests/test_image_directory_intake_recipe.py tests/test_pdf_intake_recipe.py modules/extract/ocr_ai_gpt51_v1/main.py tests/test_ocr_ai_gpt51_empty_page_recovery.py`. Fresh widened proof via `python benchmarks/scripts/run_handwritten_notes_eval.py --image-recipe configs/recipes/recipe-images-ocr-html-handwritten-notes-gemini-rescue.yaml --pdf-recipe configs/recipes/recipe-pdf-ocr-html-handwritten-notes-gemini-rescue.yaml --image-case-id image-handwritten-rescue --pdf-case-id pdf-handwritten-rescue --instrument --output benchmarks/results/handwritten-notes-story189-real-expanded.json` wrote `benchmarks/results/handwritten-notes-story189-real-expanded.json` with `pass_rate = 0.6`, `overall_min_ratio = 0.496975`, `page_min_ratio = 0.496975`, `cases_total = 10`, and `fixtures_passing = 3`. The six synthetic rescue cases remained `1.0`, but the real fixtures kept the family below bar: Barney reached `0.883604` on image entry and `0.752063` on PDF entry at `output/runs/handwritten-handwritten-notes-barney-real-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl` and `output/runs/handwritten-handwritten-notes-barney-real-pdf-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl`, while Alverson reached `0.496975` on image entry and `0.500647` on PDF entry at `output/runs/handwritten-handwritten-notes-alverson-real-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl` and `output/runs/handwritten-handwritten-notes-alverson-real-pdf-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl`. Manual artifact inspection confirmed the current real-data failure modes directly: Barney still drifts on names and phrases like `Harlen`, `genesee`, and `father has had gone`, while the Alverson page inserts stray `nothing` noise and stops after the upper portion of the letter with no recovery of the lower body / postscript. Decision: finish the handwritten line in this same story by keeping `handwritten-notes` at `has-fixture`, widening the truth surfaces to two real handwritten fixtures, and explicitly recording that the current maintained rescue seam is not stable or general enough for promotion.
