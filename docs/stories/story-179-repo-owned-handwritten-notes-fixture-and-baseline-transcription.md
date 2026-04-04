---
title: Repo-Owned Handwritten Notes Fixture and Baseline Transcription
status: Done
priority: High
ideal_refs:
- 'Requirement #1 (Ingest), Requirement #2 (Detect), Requirement #3 (Extract), Any
  format, any condition, Minimum Viable Floor'
spec_refs:
- spec:1
- spec:1.1
- spec:2
- spec:2.1
- spec:2.2
- spec:8
adr_refs: []
depends_on:
- '157'
- '167'
category_refs:
- spec:1
- spec:2
- spec:8
compromise_refs:
- B1
- B5
- C1
- C2
- C6
input_coverage_refs:
- handwritten-notes
architecture_domains: []
roadmap_tags: []
legacy_system: ''
---

# Story 179 — Repo-Owned Handwritten Notes Fixture and Baseline Transcription

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #1 (Ingest), Requirement #2 (Detect), Requirement #3 (Extract), Any format, any condition, Minimum Viable Floor
**Spec Refs**: spec:1 (spec:1.1, C2), spec:2 (spec:2.1, spec:2.2), spec:8 (B1, B5)
**Build Map Refs**: Category 1 Intake & Format Routing (`exists`, C2 `climb`); Category 2 OCR & Text Extraction (`exists`, C1 `climb`, C6 `hold`); Category 8 AI Harnesses & Tooling (`exists`, B1 `hold`, B5 `climb`); Input Coverage row `handwritten-notes` now has bounded synthetic `passing` proof on the maintained generic image-directory and PDF OCR lanes
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/runbooks/golden-build.md`, `docs/stories/story-157-pdf-intake-parity-with-image-directory-inputs.md`, `docs/stories/story-167-repo-owned-scanned-prose-pdf-fixture.md`, `docs/ocr-model-research/20251219-opus4.5.md`, `None found after search in docs/decisions/ for a handwriting-specific ADR`
**Depends On**: Story 157, Story 167

## Goal

The build map now calls out handwritten notes as the top unbuilt intake gap, but the repo still has no honest proof surface for that family: no fixture, no scored baseline, and no bounded maintained seam. This story should add a small repo-owned handwritten-notes fixture set with checked-in reference transcript(s), measure the current OCR/transcription baselines on the existing scan lanes, and then choose the smallest honest maintained path: either prove that the current image-directory/PDF OCR seam already clears a narrow handwritten slice, or document that a dedicated handwritten transcription lane is still needed and exactly why.

## Acceptance Criteria

- [x] A small repo-owned handwritten-notes fixture set exists under `testdata/` with clear provenance/licensing and checked-in reference transcript(s); if the fixture is synthetic rather than a real permissively licensed handwriting sample, the story explicitly bounds the support claim to that narrow slice instead of overstating real-world handwriting coverage.
- [x] A baseline proof surface exists for the fixture set and records at least:
  - the current maintained scan OCR path (`recipe-images-ocr-html-mvp.yaml` and/or `recipe-pdf-ocr-html-mvp.yaml`)
  - one stronger direct handwritten-transcription baseline if the generic OCR path is materially weak
  - normalized text-quality evidence plus manual artifact inspection notes
- [x] The story leaves an honest maintained-seam decision:
  - if the current OCR seam clears the narrow fixture bar, handwritten-notes is proven on that existing path without inventing a new module
  - if it does not, the story lands or scopes the smallest explicit handwritten seam needed, with no hidden heuristics or manual patching
- [x] `docs/build-map.md`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/evals/registry.yaml`, and fixture docs move the `handwritten-notes` row only as far as fresh evidence justifies (`has fixture` or `passing` on a clearly bounded slice, not beyond)

## Out of Scope

- Broad support for messy diaries, cursive archives, or multi-document handwriting collections beyond the tiny first proof surface
- Silent prompt-only fixes or manual transcription patch files that bypass reproducible artifact generation
- Provider-wide OCR benchmarking across every external service in one story
- Graduation to Dossier or any change to the accepted `doc-web` runtime boundary
- Reworking unrelated scan-routing or layout systems unless the handwriting baseline proves they are the real blocker

## Approach Evaluation

- **Simplification baseline**: the current maintained scan seams may already be enough for a narrow handwritten slice. Before adding any handwritten-specific module, measure the existing `image-directory` and PDF OCR paths on a real fixture and inspect the stamped `page_html_v1` output against the checked-in transcript.
- **AI-only**: a single multimodal transcription call on handwritten page images may outperform the current generic OCR lane on this family, but without a repo-owned fixture and scored baseline it is just speculation. This is only attractive if the story can compare it cheaply and honestly against the existing maintained path.
- **Hybrid**: likely the leading candidate. Reuse the existing scan-entry substrate for images/PDFs, add deterministic transcript scoring and artifact inspection, and only escalate to a stronger handwritten-focused call or dedicated recipe if the measured baseline is weak.
- **Pure code**: only appropriate for fixture generation, scoring, and recipe wiring. Handwriting recognition itself should stay AI-first.
- **Repo constraints / prior decisions**: `spec:1.1` still keeps recipe selection explicit; `spec:2.1` and `spec:2.2` treat OCR as an expensive seam that must be measured rather than guessed; ADR-002 keeps the runtime boundary unchanged, so this story should stay inside existing `page_image_v1` -> `page_html_v1` -> `doc_web_bundle` surfaces. `docs/runbooks/golden-build.md` and Story 167 already establish the pattern for a tiny repo-owned fixture plus honest support-level claims.
- **Existing patterns to reuse**: `testdata/generate_scanned_prose_fixture.py`, `tests/test_pdf_intake_recipe.py`, `configs/recipes/recipe-pdf-ocr-html-mvp.yaml`, `configs/recipes/recipe-images-ocr-html-mvp.yaml`, Story 157's maintained scan-entry proof pattern, Story 167's fixture-plus-proof workflow, and the existing `benchmarks/` task/scorer layout if the story needs a first handwriting eval.
- **Eval**: the deciding evidence is a repo-owned fixture plus measured transcription quality, not a hunch. Candidate approaches should be distinguished by:
  - normalized text fidelity against the checked-in reference transcript
  - artifact honesty and provenance quality on the maintained path
  - cost/latency relative to the narrow handwritten slice being proved
  There is no handwriting-specific eval today, so this story should add the smallest honest benchmark surface if the comparison cannot live cleanly in a focused regression helper.

## Tasks

- [x] Add a small repo-owned handwritten-notes fixture set under `testdata/`:
  - prefer a permissively licensed real handwriting sample if one can be kept repo-owned cleanly
  - otherwise add a clearly labeled synthetic handwritten fixture plus checked-in source text/transcript and generation notes
  - if a PDF wrapper is added, verify whether it is image-only or contains extractable text
- [x] Measure the simplification baseline on the current maintained scan seams:
  - run the existing image-directory and/or PDF OCR recipe through `driver.py`
  - inspect stamped `page_html_v1` artifacts in `output/runs/`
  - compare normalized output against the checked-in transcript so the story can say whether the current generic OCR path already clears a narrow handwriting bar
- [x] Add the smallest honest benchmark/eval surface for this family:
  - a focused regression helper or benchmark under `benchmarks/`
  - compare the maintained OCR path with at least one stronger direct handwritten-transcription baseline if the generic path is weak
  - update `docs/evals/registry.yaml` with the new baseline or explicit gap measurement
- [x] If the measured baseline does not clear the narrow slice, add the smallest explicit maintained handwritten seam: not needed, because the fresh checked-in generic image-directory and PDF OCR proofs already cleared the bounded slice exactly after normalization
  - prefer a sibling recipe or clearly scoped stronger-model path over invasive driver changes
  - no hidden one-off heuristics, no manual text edits, and no untracked local assets
- [x] If this story changes documented format coverage or graduation reality: update `docs/build-map.md` and record the before/after state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: not applicable; pipeline code stayed unchanged, but fresh `driver.py` proofs and manual artifact inspection were still run for the support-level claim
  - [x] If agent tooling changed: not applicable
- [x] If evals or goldens changed: new eval surface added directly and `docs/evals/registry.yaml` updated; `/improve-eval` was not applicable because this eval did not exist before Story 179
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: the image-directory and PDF-backed proofs both stamp source paths back to the checked-in fixture assets
  - [x] T1 — AI-First: no handwriting-specific runtime code path was added because the measured generic OCR seam already cleared the bounded slice
  - [x] T2 — Eval Before Build: planning measured a stronger direct baseline on the scratch slice; implementation then reran the maintained generic OCR path and recorded a repeatable eval on the checked-in fixture before deciding not to add new logic
  - [x] T3 — Fidelity: the maintained generic OCR seam matched the checked-in transcript exactly after normalization on both image-directory and PDF lanes
  - [x] T4 — Modular: the story reused the maintained generic OCR recipes and added only fixture/eval/test assets, not a hidden handwritten branch
  - [x] T5 — Inspect Artifacts: inspected the stamped manifests and `page_html_v1` artifacts under `output/runs/`, not just the helper summary

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: the fixture + proof seam around existing scan OCR entry paths. Primary ownership should stay in `testdata/`, scan-entry recipes, focused tests/benchmarks, and the truth surfaces that describe the `handwritten-notes` family honestly.
- **Build-map reality**: Category 1 owns the input-family gap, Category 2 owns the OCR/transcription seam, and Category 8 owns the baseline-measurement discipline. After implementation, the `handwritten-notes` row now has bounded synthetic passing proof on the maintained generic image-directory and PDF OCR lanes.
- **Substrate evidence**: verified in repo that `configs/recipes/recipe-images-ocr-html-mvp.yaml` and `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` already exist, `images_dir_to_manifest_v1`, `extract_pdf_images_fast_v1`, and `ocr_ai_gpt51_v1` are maintained, `tests/test_pdf_intake_recipe.py` already proves cheap scan-entry smoke coverage, and `testdata/generate_scanned_prose_fixture.py` already provides a reproducible image-only fixture pattern to adapt. Story 179 adds the previously missing repo-owned handwritten fixture, focused transcript-scoring helper, cheap image/PDF smoke coverage, and measured proof that the maintained generic OCR seam clears the bounded checked-in slice.
- **Data contracts / schemas**: no schema change is expected for the narrow baseline path if the story stays within existing `page_image_v1`, `page_html_v1`, and final bundle surfaces. If a new persisted benchmark/report artifact crosses module boundaries, it must reuse existing JSON conventions or add schema support explicitly before the story claims that artifact as part of the maintained seam.
- **File sizes**: `testdata/generate_scanned_prose_fixture.py` is 169 lines, `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` is 88 lines, `configs/recipes/recipe-images-ocr-html-mvp.yaml` is 87 lines, `tests/test_pdf_intake_recipe.py` is 87 lines, `testdata/README.md` is 77 lines, `docs/build-map.md` is 586 lines, `tests/fixtures/formats/_coverage-matrix.json` is 399 lines, and `docs/evals/registry.yaml` is 666 lines. Avoid casual growth in the build map and eval registry; prefer focused new benchmark files over bloating those truth surfaces with prose.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/build-map.md`, ADR-002, `docs/runbooks/golden-build.md`, Story 157, Story 167, the coverage matrix, and searched `docs/decisions/` for a handwriting-specific ADR. None exists today, which is fine because this story is meant to establish the first honest proof surface rather than settle a hard-to-reverse architecture question.

## Files to Modify

- `testdata/` — add the repo-owned handwritten fixture source, transcript, generated assets, and any reproduction helper needed
- `testdata/README.md` — document the handwritten fixture and exactly what support level it proves (77 lines)
- `tests/test_pdf_intake_recipe.py` and/or a new focused handwriting baseline test — add cheap proof coverage around the chosen scan-entry path (87 lines for the current PDF smoke file)
- `benchmarks/scorers/handwritten_notes_transcription.py` — normalized transcript scoring for the focused handwritten regression helper (new file)
- `benchmarks/scripts/run_handwritten_notes_eval.py` — rerun the maintained generic image-directory and PDF OCR paths and score them against the checked-in transcript (new file)
- `configs/recipes/recipe-images-ocr-html-mvp.yaml` and/or `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` — only if the current maintained path proves insufficient; Story 179 ended up not touching the recipes because the generic seam already cleared the bounded slice
- `tests/fixtures/formats/_coverage-matrix.json` — move `handwritten-notes` only as far as the fresh evidence justifies (399 lines)
- `docs/build-map.md` — update Gap 4 / Input Coverage / Next Actions truth surfaces honestly (586 lines)
- `docs/evals/registry.yaml` — record the new baseline/eval surface if the story adds one (666 lines)

## Redundancy / Removal Targets

- The current vague `handwritten-notes` gap wording in `docs/build-map.md` and the coverage matrix once the family has a real measured proof surface
- Any pressure to create a handwritten-specific recipe before the measured baseline proves the generic OCR seam is insufficient
- Any local-only note or benchmark result that would leave handwriting "known" in practice but still undocumented in the repo truth surfaces

## Notes

- The first fixture should be tiny and honest. If the only clean repo-owned option is synthetic handwriting, the story must say that explicitly and keep the support claim narrow rather than pretending it proves messy real-world cursive.
- The likely product-shape winner is image-directory first, because the current coverage row is phrased as photos of handwritten notes, letters, and diaries. A PDF wrapper may still be useful for parity with the maintained scan-entry surface.
- This story should prefer proving or falsifying the current OCR path before inventing a handwriting-specific recipe. If the maintained seam already works on the narrow slice, the right outcome is probably a truth-surface update plus maybe a benchmark, not new runtime complexity.

## Plan

1. Fixture choice and transcript baseline (`S`)
   - Add one tiny repo-owned handwritten fixture set plus checked-in transcript(s).
   - Decide whether the fixture is real permissive handwriting or synthetic handwriting, and write the support-level caveat up front.
   - Done when the repo has a reproducible, inspectable fixture that future runs can reuse.

2. Baseline proof on existing scan seams (`S`)
   - Run the current maintained image-directory and/or PDF OCR path through `driver.py`.
   - Inspect `page_html_v1` output against the checked-in transcript and capture where the current seam fails or succeeds.
   - Done when the story can say, with artifact evidence, whether the generic OCR path already clears a narrow handwritten bar.

3. Add the smallest comparison surface (`S`-`M`)
   - If the current OCR seam is weak, compare it against one stronger direct handwritten-transcription baseline on the same checked-in fixture.
   - Start with the lightest honest surface: a focused regression helper that normalizes transcript fidelity and records artifact paths. Only add a promptfoo benchmark if that helper cannot carry the maintained comparison cleanly.
   - Provisional scratch evidence says a stronger direct call is not an automatic win, so avoid pre-committing to a handwritten-only runtime path before the checked-in fixture rerun.
   - Done when the repo has a repeatable way to answer "is generic OCR good enough here?"

4. Decide the maintained seam (`S`-`M`)
   - If the generic OCR seam already clears, keep the architecture simple and avoid a handwritten-only module.
   - If it does not, prefer the smallest explicit sibling recipe or stronger-model path that honestly improves the measured slice over invasive OCR-module branching.
   - The likely conservative outcome is that the row moves to `has fixture` unless the checked-in rerun materially beats the provisional scratch baseline.

5. Truth-surface updates and verification (`S`)
   - Update `docs/build-map.md`, the coverage matrix, fixture docs, and the eval registry as far as the fresh evidence justifies.
   - Run `make lint`, `make test`, and any required real `driver.py` proof. Record specific artifact paths and sample content inspected.

### Impact Analysis

- **Primary blast radius:** fixture assets, baseline benchmark files, and the truth surfaces that describe the `handwritten-notes` row.
- **Secondary blast radius:** scan-entry recipe parameters only if the measured baseline proves a small explicit handwritten seam is necessary.
- **Main risk:** overclaiming a narrow synthetic or unusually legible fixture as general handwriting support. The story should bias toward a smaller honest claim over an inflated `passing` status.
- **Repo-fit evidence:** the critical runtime substrate already exists, so this story is buildable now. The missing parts are measurement and fixture ownership, not core pipeline scaffolding.

### Planning Baseline Snapshot

- **Scratch fixture only:** used a temporary two-page image-first handwritten sample under `/tmp/story179_plan/` to probe the current maintained seams before touching the repo fixture surface. This is planning evidence, not the final maintained proof.
- **Image/PDF substrate check:** the same sample was wrapped as an image-only PDF, and `pypdf` extracted `[0, 0]` characters, confirming the baseline really exercises the OCR seam rather than hidden PDF text.
- **Maintained-path result:** `output/runs/story179-plan-image-baseline/02_ocr_ai_gpt51_v1/pages_html.jsonl` and `output/runs/story179-plan-pdf-baseline/02_ocr_ai_gpt51_v1/pages_html.jsonl` both completed through `driver.py`, but page 2 dropped the clause `are tied with green ribbon, not red` and clipped `small brass compass back to the desk drawer`. Normalized whole-document similarity was about `0.739` for the image path and `0.741` for the PDF path on this scratch sample.
- **Stronger direct probe:** a direct `gpt-5.2` page-2 OCR probe improved metadata integrity but still omitted the middle clause and only reached about `0.810` normalized similarity for that page. That is enough to justify keeping the stronger-baseline comparison in scope, but not enough to treat "just switch models" as already proven.

### Human-Approval Blockers

- None discovered in planning for the intended narrow slice.
- If implementation discovers that the cleanest comparison needs a new runtime dependency, schema change, or a broader handwritten-specific architecture decision, stop and ask before expanding the seam.

## Work Log

20260401-2211 — story created from `/triage`: turned the build-map top next action into a concrete, baseline-first handwriting story. Evidence reviewed in this pass: `docs/build-map.md` still marks `handwritten-notes` as `untested` and calls it the top next action; `tests/fixtures/formats/_coverage-matrix.json` still has no fixtures or recipe for that row; `configs/recipes/recipe-images-ocr-html-mvp.yaml`, `configs/recipes/recipe-pdf-ocr-html-mvp.yaml`, `images_dir_to_manifest_v1`, `extract_pdf_images_fast_v1`, and `ocr_ai_gpt51_v1` prove the generic scan substrate already exists; `tests/test_pdf_intake_recipe.py` and Story 167 prove the repo already has a pattern for tiny scan fixtures plus honest `driver.py` verification. Result: the story is `Pending`, not `Draft`, because the missing slice is bounded to fixture ownership, baseline measurement, and an explicit maintained-seam decision. Next step: `/build-story` should choose the smallest honest fixture shape, measure the current OCR seam before adding new runtime logic, and only promote a handwritten-specific path if the measured baseline actually requires it.
20260401-2322 — `/build-story` exploration and eval-first planning: verified the story is honestly buildable on existing scan-entry substrate and tightened the implementation plan around measured evidence instead of assumptions. Files likely to change in implementation: `testdata/` handwritten fixture assets plus generation notes, `testdata/README.md`, a focused handwriting regression helper or bounded benchmark files under `benchmarks/`, `tests/test_pdf_intake_recipe.py` or a sibling focused test, `docs/evals/registry.yaml`, `docs/build-map.md`, and `tests/fixtures/formats/_coverage-matrix.json`; files at risk if the seam expands: `configs/recipes/recipe-images-ocr-html-mvp.yaml`, `configs/recipes/recipe-pdf-ocr-html-mvp.yaml`, and the OCR module wiring around `modules/extract/ocr_ai_gpt51_v1/main.py`. Decision/docs consulted in this pass: `docs/ideal.md`, `docs/spec.md`, the Category 1 / Category 2 / Category 8 portions of `docs/build-map.md`, ADR-002, `docs/runbooks/golden-build.md`, Story 157, Story 167, and a search of `docs/decisions/` that found no handwriting-specific ADR. Build-map/input context: Category 1 `exists` with C2 `climb`, Category 2 `exists` with C1 `climb` and C6 `hold`, Category 8 `exists` with B1 `hold` and B5 `climb`, and the `handwritten-notes` row is still `untested`. Critical substrate verified in code: `configs/recipes/recipe-images-ocr-html-mvp.yaml` and `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` already route images/PDFs into `modules/extract/images_dir_to_manifest_v1/main.py`, `modules/extract/extract_pdf_images_fast_v1/main.py`, and `modules/extract/ocr_ai_gpt51_v1/main.py`; missing substrate is the repo-owned handwritten fixture, transcript scoring/eval surface, and the documented maintained-seam decision. Patterns to follow: Story 167's tiny fixture-plus-proof workflow, Story 157's maintained scan-entry parity checks, `testdata/generate_scanned_prose_fixture.py` for reproducible image-only assets, and the existing benchmark scorer layout if a helper is not enough. Surprises found: the provisional scratch render was materially weaker than the eventual checked-in fixture, and the earlier direct `gpt-5.2` probe therefore did not predict the final outcome cleanly. Scratch planning evidence: `/tmp/story179_plan/handwritten-note.pdf` is image-only (`pypdf` extracted `[0, 0]` chars); `output/runs/story179-plan-image-baseline/02_ocr_ai_gpt51_v1/pages_html.jsonl` and `output/runs/story179-plan-pdf-baseline/02_ocr_ai_gpt51_v1/pages_html.jsonl` both dropped `are tied with green ribbon, not red` on page 2 and clipped the compass sentence, yielding about `0.739` and `0.741` normalized whole-document similarity; a direct `gpt-5.2` page-2 probe still omitted the same middle clause at about `0.810` normalized similarity. Redundancy/removal conclusion: do not add a heavyweight promptfoo surface or handwritten-only recipe unless the checked-in fixture rerun proves a lighter helper or the generic seam is insufficient. Next step: add the tiny repo-owned fixture, codify the comparison helper, rerun the maintained path on checked-in assets, and move the truth surfaces only as far as that fresh evidence supports.
20260402-0048 — implementation + verification: added the repo-owned synthetic handwritten fixture set under `testdata/`: checked-in transcript `handwritten-notes-mini.txt`, generator `generate_handwritten_notes_fixture.py`, generated image directory `handwritten-notes-mini-images/`, and image-only PDF wrapper `handwritten-notes-mini.pdf` (2 pages, 224 KB PDF; PNG pages ~62 KB and ~59 KB). Verified the PDF wrapper is honest scanned evidence rather than embedded text: `pypdf` extract-text lengths are `[0, 0]`. Added cheap maintained smoke coverage for both scan-entry seams: `tests/test_image_directory_intake_recipe.py` now proves `recipe-images-ocr-html-mvp.yaml` can stamp `page_image_v1` rows from the checked-in image directory, and `tests/test_pdf_intake_recipe.py` now proves the handwritten PDF wrapper is image-only and can stamp `page_image_v1` rows through `recipe-pdf-ocr-html-mvp.yaml`; targeted scope passed fresh with `python -m pytest tests/test_pdf_intake_recipe.py tests/test_image_directory_intake_recipe.py -q` => `6 passed in 3.36s`. Added the focused regression surface instead of a promptfoo task: `benchmarks/scorers/handwritten_notes_transcription.py` scores normalized transcript fidelity, and `benchmarks/scripts/run_handwritten_notes_eval.py` reruns the maintained generic image-directory and PDF OCR paths and writes `benchmarks/results/handwritten-notes-story179.json`. Fresh helper result: `pass_rate = 1.0`, `overall_min_ratio = 1.0`, `page_min_ratio = 1.0`, and `pdf_extractable_text_lengths = [0, 0]`. Fresh real `driver.py` proof on the checked-in assets also cleared the narrow slice without any handwritten-only recipe: `output/runs/story179-image-generic/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl` stamps both pages back to `/Users/cam/.codex/worktrees/a30d/doc-web/testdata/handwritten-notes-mini-images`, `output/runs/story179-image-generic/02_ocr_ai_gpt51_v1/pages_html.jsonl` matches the checked-in transcript exactly after normalization on both pages, `output/runs/story179-pdf-generic/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl` stamps both pages back to `/Users/cam/.codex/worktrees/a30d/doc-web/testdata/handwritten-notes-mini.pdf`, and `output/runs/story179-pdf-generic/02_ocr_ai_gpt51_v1/pages_html.jsonl` also matches exactly after normalization. Manual artifact inspection in this pass confirmed the page-level HTML preserves the full page-2 clause `The letters from Aunt Elise are tied with green ribbon, not red.` plus `bring the small brass compass back to the desk drawer.` on both maintained lanes, with OCR metadata at `ocr_quality 0.98-1.0`, `ocr_integrity 1.0`, and low continuation risk. Decision: the checked-in fixture proves the maintained generic OCR seam already clears this bounded synthetic handwritten slice, so no handwritten-only runtime seam was added. Updated truth surfaces accordingly: `testdata/README.md`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/build-map.md`, and `docs/evals/registry.yaml` now record the bounded synthetic passing claim and explicitly keep messy cursive / degraded handwriting out of scope. Fresh repo checks passed: `make lint` clean; `make test` => `420 passed, 4 warnings in 190.07s`. Impact: Story-scope gap closed by adding the first repo-owned handwritten proof surface plus repeatable scoring harness. Pipeline-scope impact: the maintained generic image-directory and PDF OCR lanes now have inspectable exact-match proof on one narrow handwritten family instead of leaving `handwritten-notes` entirely untested. Evidence: `benchmarks/results/handwritten-notes-story179.json`, `output/runs/story179-image-generic/02_ocr_ai_gpt51_v1/pages_html.jsonl`, and `output/runs/story179-pdf-generic/02_ocr_ai_gpt51_v1/pages_html.jsonl`. Next step: `/validate` should independently review the bounded passing claim and the synthetic-slice caveat before `/mark-story-done`.
20260402-0112 — `/mark-story-done` close-out: fresh validation confirmed the story is ready to close. Evidence re-checked in this pass: `make lint` passed cleanly; `make test` passed (`420 passed, 4 warnings in 187.34s`); `python -m pytest tests/test_pdf_intake_recipe.py tests/test_image_directory_intake_recipe.py -q` passed (`6 passed in 3.33s`); `python benchmarks/scripts/run_handwritten_notes_eval.py --output benchmarks/results/handwritten-notes-validate.json` returned `pass_rate = 1.0`, `overall_min_ratio = 1.0`, `page_min_ratio = 1.0`, and `pdf_extractable_text_lengths = [0, 0]`; manual artifact inspection of `output/runs/handwritten-notes-image-generic/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl`, `output/runs/handwritten-notes-image-generic/02_ocr_ai_gpt51_v1/pages_html.jsonl`, `output/runs/handwritten-notes-pdf-generic/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl`, and `output/runs/handwritten-notes-pdf-generic/02_ocr_ai_gpt51_v1/pages_html.jsonl` again showed source traceability back to the checked-in fixture and exact normalized transcript matches on both maintained lanes. Result: set Story 179 status to `Done`, checked the validation and mark-done workflow gates, and prepared the landing set plus changelog entry. Next step: `/check-in-diff`.
20260402-0124 — close-out cleanup before `/check-in-diff`: fixed the handwritten eval helper to stamp `measured_at` and default result filenames in local time instead of UTC so generated evidence no longer drifts a day ahead of the repo’s truth-surface dating convention near midnight UTC. Scope stayed narrow to `benchmarks/scripts/run_handwritten_notes_eval.py`; the support claim and measured ratios remain unchanged. Next step: rerun the focused helper, then stage the Story 179 landing set.
