# Story 185 — Widen Handwritten Proof Beyond the Synthetic Pair

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #1 (Ingest), Requirement #2 (Detect), Requirement #3 (Extract), Any format, any condition, Fidelity to the source, Minimum Viable Floor
**Spec Refs**: spec:1 (spec:1.1, C2), spec:2 (spec:2.1, spec:2.2, C1, C6), spec:8 (B1, B5)
**Build Map Refs**: Category 1 Intake & Format Routing (`exists`, C2 `climb`); Category 2 OCR & Text Extraction (`exists`, C1 `climb`, C6 `hold`); Category 8 AI Harnesses & Tooling (`exists`, B1 `hold`, B5 `climb`); Input Coverage row `handwritten-notes` (`passing` on a wider but still synthetic three-fixture slice); Gap 4 — Handwritten document transcription; Gap 5 — Fixture breadth and graduation confidence; Next Actions 1 and 2
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/runbooks/golden-build.md`, `docs/stories/story-179-repo-owned-handwritten-notes-fixture-and-baseline-transcription.md`, `docs/stories/story-182-widen-handwritten-notes-fixture-breadth.md`, `docs/stories/story-167-repo-owned-scanned-prose-pdf-fixture.md`, `docs/stories/story-157-pdf-intake-parity-with-image-directory-inputs.md`, `None found after search in docs/decisions/`, `docs/scout/`, and `docs/notes/` for narrower handwriting-breadth-specific guidance
**Depends On**: Story 182

## Goal

Story 182 widened handwritten proof from one easy synthetic note to a broader two-fixture synthetic slice, but the build map still says the family is not broadly supported because the repo has no real or more degraded third fixture. This story should add one more handwritten proof case beyond the current synthetic pair, rerun the maintained generic image-directory and PDF OCR lanes on the widened corpus, and update the truth surfaces only as far as the new evidence supports. The point is breadth and honesty, not a premature handwritten-only runtime seam.

## Acceptance Criteria

- [x] At least one additional handwritten fixture exists beyond `handwritten-notes-mini` and `handwritten-notes-rough`, and it is meaningfully different from the current pair:
  - [x] prefer a repo-owned or permissively licensed real sample if it can be kept reproducible and legally clean in this repo,
  - [x] otherwise add a more degraded synthetic or reproducibly transformed handwritten sample with explicit limits,
  - [x] and record provenance, licensing, and `real` vs `synthetic` status in `testdata/README.md`.
- [x] The handwriting proof surface covers at least three distinct fixtures total and records per-fixture evidence for:
  - [x] normalized transcription quality,
  - [x] image-only PDF verification where a PDF wrapper is used,
  - [x] and the exact maintained lane exercised (`recipe-images-ocr-html-mvp.yaml` and/or `recipe-pdf-ocr-html-mvp.yaml`).
- [x] Fresh `driver.py` proofs exist under `output/runs/` for every fixture the story claims as supported on the maintained generic OCR seam, and the work log records manual inspection of:
  - [x] stamped manifest artifacts,
  - [x] stamped `page_html_v1` artifacts,
  - [x] and at least one representative hard snippet per new fixture showing what the current generic seam preserved or lost.
- [x] If any new fixture is weak or ambiguous on the generic seam, the story compares the smallest stronger direct handwritten-transcription baseline on that same fixture before recommending a new maintained seam; if not needed, the story leaves the generic image-directory/PDF OCR path as the explicit maintained handwritten seam for the widened slice.
- [x] `docs/build-map.md`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, and `testdata/README.md` move only as far as the fresh evidence justifies, and the residual real/degraded handwriting gap stays explicit if it is not closed.

## Out of Scope

- Broad support for messy cursive archives, multilingual handwriting collections, or archive-scale note ingestion
- A new handwritten-only production runtime path unless the widened measured baseline proves the generic seam is insufficient
- Changing the accepted `doc-web` runtime boundary or Dossier handoff model from ADR-002
- Routing or approved-handoff changes outside the already maintained generic image-directory and PDF OCR seams
- Manual transcript cleanup that narrows the product requirement or hides OCR failures
- A broad provider sweep when one bounded direct baseline on the weakest new fixture would answer the question more cheaply

## Approach Evaluation

- **Simplification baseline**: the current maintained generic OCR seam may already clear a third handwritten fixture without any new runtime logic. Story 179 and Story 182 already proved the helper, corpus, and run-ID pattern, so the first move is to widen evidence, not architecture.
- **AI-only**: a stronger direct multimodal transcription call on the new fixture may outperform the generic OCR path, but it is only useful here as a bounded comparison baseline on a weak or ambiguous case. It should not become the maintained path just because it wins one difficult page.
- **Hybrid**: likely the leading candidate. Add the third fixture, rerun the maintained image-directory/PDF OCR lanes, and only use a stronger direct baseline where the generic seam looks weak enough to justify comparison.
- **Pure code**: appropriate only for fixture generation or import, corpus wiring, focused test updates, and truth-surface edits. Handwriting recognition itself stays AI-first.
- **Repo constraints / prior decisions**: `spec:1.1` still keeps the recipe surface explicit; `spec:2.1` and `spec:2.2` treat OCR as an expensive seam that should be measured before it is redesigned; `docs/runbooks/golden-build.md` warns against turning benchmark scoping into product policy; Story 182 explicitly left the real/degraded gap open; ADR-002 is unaffected because this work stays inside the existing `page_image_v1 -> page_html_v1 -> doc_web_bundle` boundary.
- **Existing patterns to reuse**: `testdata/generate_handwritten_notes_fixture.py`, `benchmarks/scripts/run_handwritten_notes_eval.py`, `benchmarks/scorers/handwritten_notes_transcription.py`, `benchmarks/golden/handwritten-notes/corpus.json`, `tests/test_handwritten_notes_eval.py`, `tests/test_image_directory_intake_recipe.py`, `tests/test_pdf_intake_recipe.py`, Story 179's baseline-first handwriting proof pattern, Story 182's multi-fixture widening pattern, Story 167's small fixture-plus-proof workflow, and Story 157's maintained scan-entry parity checks.
- **Eval**: the deciding surface is a widened handwritten corpus with fresh `driver.py` runs plus manual artifact inspection. If the generic seam is weak or ambiguous on the new fixture, compare one stronger direct handwritten-transcription baseline on that same fixture before proposing any new maintained seam. `/build-story` should prefer the lightest current helper/corpus path over a new promptfoo surface unless it proves insufficient.

## Tasks

- [x] Freeze the third handwritten proof slice:
  - [x] identify the smallest honest third fixture candidate beyond the current synthetic pair,
  - [x] add the asset or reproducible generation path under `testdata/`,
  - [x] and document provenance, licensing, and `real` vs `synthetic` status in `testdata/README.md`.
  - [x] if the chosen fixture originates from an external public source, keep the checked-in copy and original source URL/rights note in repo docs instead of making tests depend on a live download.
- [x] Measure the current maintained generic OCR seam before adding new logic:
  - [x] rerun `recipe-images-ocr-html-mvp.yaml` and `recipe-pdf-ocr-html-mvp.yaml` on every fixture in the widened corpus,
  - [x] inspect the stamped artifacts in `output/runs/`,
  - [x] and record exact hard snippets that either pass cleanly or expose failure boundaries.
- [x] If the new fixture is weak or ambiguous, compare the smallest stronger direct handwritten-transcription baseline on that same source slice before proposing any maintained runtime change.
- [x] Land the smallest honest handwriting eval widening:
  - [x] extend `benchmarks/golden/handwritten-notes/corpus.json` to include the new fixture,
  - [x] widen `benchmarks/scripts/run_handwritten_notes_eval.py` only as needed for the new fixture metadata or case handling,
  - [x] and extend `tests/test_handwritten_notes_eval.py` plus any cheap recipe smoke tests so the widened proof surface remains repeatable.
- [x] Update truth surfaces only as far as the evidence justifies:
  - [x] `docs/build-map.md`,
  - [x] `docs/evals/registry.yaml`,
  - [x] `tests/fixtures/formats/_coverage-matrix.json`,
  - [x] `testdata/README.md`.
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] Fresh `driver.py` proofs through the maintained image-directory and PDF OCR lanes for every widened fixture, with manual inspection of resulting artifacts in `output/runs/`
  - [x] Agent tooling is not expected to change; run `make skills-check` only if that changes
- [x] If evals or goldens changed: run `/improve-eval` discipline inline and update `docs/evals/registry.yaml`
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every support claim traces to named fixtures, run IDs, and inspected artifacts
  - [x] T1 — AI-First: do not add deterministic handwritten logic where the current or stronger model path already solves the measured slice
  - [x] T2 — Eval Before Build: widen the corpus and measure the maintained seam before proposing new runtime logic
  - [x] T3 — Fidelity: keep any preserved or lost handwritten content explicit instead of smoothing it away
  - [x] T4 — Modular: widen fixture/eval coverage and explicit recipe claims rather than hiding handwritten-specific branches inside the pipeline
  - [x] T5 — Inspect Artifacts: verify real `output/runs/` artifacts, not just helper summaries or pass/fail counts

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: handwritten fixture generation/import, the handwritten eval surface, and the truth-surface docs around the existing scan-entry OCR seam.
- **Build-map reality**: this story sits in Category 1 and Category 2 with Category 8 support work. The implementation widens `handwritten-notes` from the earlier two-fixture synthetic slice to a three-fixture synthetic slice; Gap 4 and Gap 5 stay open because the repo still lacks a reproducible real handwritten proof case.
- **Substrate evidence**: the maintained recipes already exist in `configs/recipes/recipe-images-ocr-html-mvp.yaml` and `configs/recipes/recipe-pdf-ocr-html-mvp.yaml`; the runtime entrypoints already exist in `modules/extract/images_dir_to_manifest_v1/main.py`, `modules/extract/extract_pdf_images_fast_v1/main.py`, and `modules/extract/ocr_ai_gpt51_v1/main.py`; the handwriting helper, scorer, and corpus already exist in `benchmarks/scripts/run_handwritten_notes_eval.py`, `benchmarks/scorers/handwritten_notes_transcription.py`, and `benchmarks/golden/handwritten-notes/corpus.json`; cheap smoke coverage already exists in `tests/test_handwritten_notes_eval.py`, `tests/test_image_directory_intake_recipe.py`, and `tests/test_pdf_intake_recipe.py`; and the fixture-generation substrate already exists in `testdata/generate_handwritten_notes_fixture.py`. The missing substrate is explicit and local to this story: there is no third handwritten fixture beyond the current synthetic pair.
- **Data contracts / schemas**: the story should stay inside existing `page_image_v1` and `page_html_v1` artifacts plus the current handwritten eval payload shape. No `schemas.py` change is expected unless implementation introduces new stamped fields across artifact boundaries.
- **File sizes**: likely touch points are `benchmarks/scripts/run_handwritten_notes_eval.py` (226 lines), `benchmarks/scorers/handwritten_notes_transcription.py` (119), `testdata/generate_handwritten_notes_fixture.py` (231), `tests/test_handwritten_notes_eval.py` (49), `tests/test_image_directory_intake_recipe.py` (90), `tests/test_pdf_intake_recipe.py` (105), `testdata/README.md` (85), `benchmarks/golden/handwritten-notes/corpus.json` (22), `tests/fixtures/formats/_coverage-matrix.json` (434), `docs/build-map.md` (597), and `docs/evals/registry.yaml` (1140). `docs/build-map.md` and `docs/evals/registry.yaml` are already large and should only take narrow, evidence-backed edits.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, the Category 1 / 2 / 8 portions of `docs/build-map.md`, ADR-002, `docs/runbooks/golden-build.md`, Story 179, Story 182, Story 167, Story 157, and a search across `docs/decisions/`, `docs/scout/`, and `docs/notes/` that found no narrower handwriting-breadth-specific guidance beyond the benchmark-scope warning in `golden-build.md`.

## Files to Modify

- `docs/stories/story-185-widen-handwritten-proof-beyond-synthetic-pair.md` — record implementation evidence and close-out decisions (new file)
- `docs/stories.md` — keep Story 185 indexed and in sync with its current status (193 lines)
- `testdata/` — add one third handwritten fixture set or a reproducible import/generation path with any paired PDF wrapper needed for parity checks
- `testdata/README.md` — document the new handwritten fixture and exactly what widened support it proves (85 lines)
- `testdata/generate_handwritten_notes_fixture.py` — extend generator or transform support only if the new fixture stays synthetic-first (231 lines)
- `benchmarks/golden/handwritten-notes/corpus.json` — widen the maintained handwritten corpus to include the third fixture (22 lines)
- `benchmarks/scripts/run_handwritten_notes_eval.py` — widen the helper only as needed for the new fixture metadata, run shape, or reporting (226 lines)
- `tests/test_handwritten_notes_eval.py` — keep corpus loading and run-ID behavior honest as the third fixture lands (49 lines)
- `tests/test_image_directory_intake_recipe.py` — add cheap extract-only smoke coverage for any new handwritten image-directory fixture (90 lines)
- `tests/test_pdf_intake_recipe.py` — add image-only verification and extract-only smoke coverage for any new handwritten PDF wrapper (105 lines)
- `docs/evals/registry.yaml` — widen the `handwritten-notes-transcription` surface or record a bounded comparison result if the new fixture changes the story the repo can honestly tell (1140 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — move the `handwritten-notes` row only as far as the widened evidence supports (434 lines)
- `docs/build-map.md` — update the handwritten row, Gap 4, Gap 5, and/or Next Actions if the new evidence changes them (597 lines)

## Redundancy / Removal Targets

- Two-fixture-only wording that becomes stale once the widened handwritten corpus lands
- Any one-off handwritten comparison helper or scratch fixture path created during implementation instead of being folded into the maintained handwritten helper/corpus
- Duplicate caveat wording across the build map, registry, and fixture docs if one concise updated statement can replace it

## Notes

- Prefer a real permissively licensed handwritten sample only if it can be kept reproducible and legally clean inside this repo; otherwise a more degraded synthetic or reproducibly transformed sample is acceptable as long as the support claim stays explicitly bounded.
- Reuse the same image-only verification discipline from Stories 167, 179, and 182 for any new handwritten PDF wrapper.
- Follow `docs/runbooks/golden-build.md`: a scoped fixture can make the benchmark fairer, but it must not shrink the product requirement or be mistaken for broad real-world handwriting support.
- If the cleanest widened proof would require a new runtime dependency, schema change, or broader architecture decision, stop and surface that explicitly during `/build-story` instead of silently expanding scope.

## Plan

### Exploration Summary

- **Ideal alignment:** proceed. This story closes a live Ideal gap around “Any format, any condition” and faithful handwritten extraction instead of optimizing a dead-end workaround.
- **Relevant build-map state:** Category 1 and Category 2 are both real and still `climb`; the `handwritten-notes` row is explicitly “broader but still synthetic,” and the current top next action is to add a real or more degraded third fixture before treating the family as broadly supported.
- **Critical substrate verified in code:** the maintained scan-entry recipes already exist, the handwritten eval helper already supports multi-fixture corpora plus ad hoc single-fixture overrides, the current corpus already has fixture-specific run IDs, and cheap recipe smoke coverage already exists for image-directory and PDF entry. No missing runtime substrate was found.
- **Fresh baseline:** `python benchmarks/scripts/run_handwritten_notes_eval.py --output benchmarks/results/handwritten-notes-story185-baseline.json` returned `pass_rate = 1.0`, `overall_min_ratio = 1.0`, `page_min_ratio = 1.0`, `cases_total = 4`, `fixture_count = 2`, and image-only PDF verification of `{"handwritten-notes-mini": [0, 0], "handwritten-notes-rough": [0, 0, 0]}` on the current code.
- **Candidate third-fixture read:**
  - **Preferred real-sample candidate:** the Library of Congress Civil War letter item `https://www.loc.gov/pictures/item/2023637835/` currently exposes a downloadable handwritten front image, a transcript PDF link, and `Rights Advisory: No known restrictions on publication`. The medium front JPEG is small enough to vendor cleanly (fresh planning probe: about `108 KB`, `1126x1435`). Practical caveat found during exploration: direct transcript/back-image fetches were intermittently `503`, so the honest path would be to check in the source asset(s) plus transcript and record the original source URL/rights note, not to make the repo depend on live external fetches.
  - **Fallback if the real sample path stalls:** add a third, materially more degraded synthetic preset and transcript variant under `testdata/` rather than stalling the story on external-source friction.
- **Substrate verdict:** the story is honestly buildable. The missing slice is fixture ownership and widened evidence, not OCR/runtime wiring.

### Candidate Approaches

1. **Real handwritten sample import** (`S`, recommended first)
   - Add one small, legally clean checked-in real handwritten sample plus transcript.
   - Best match to the build-map next action because it actually pressures the “real handwriting” gap rather than only synthetic breadth.
   - Main risk: source-fetch friction or transcript cleanup if the official transcript asset is not easily retrievable in one pass.

2. **More degraded synthetic third fixture** (`S`)
   - Extend the existing generator with a materially harsher preset and new transcript content.
   - Lower operational risk, fully reproducible, and still satisfies the build map’s “real or more degraded” wording.
   - Lower leverage than a real sample because it still leaves the real-handwriting gap open.

3. **New maintained handwritten-only runtime seam** (`M-L`, reject unless baseline forces it)
   - Only justified if the widened measured baseline plus one stronger direct comparison show the generic seam is materially insufficient.
   - Exploration found no evidence yet that this is necessary.

### Recommended Implementation Plan

1. Freeze the third-fixture candidate (`XS-S`)
   - Start with the LOC real-sample path because it best matches the build-map next action.
   - If the transcript asset remains operationally flaky after one bounded retrieval attempt, fall back in the same story to a more degraded synthetic fixture instead of stalling the entire slice.
   - Files likely to change first: `testdata/`, `testdata/README.md`, and possibly `testdata/generate_handwritten_notes_fixture.py`.

2. Run the maintained generic OCR seam on the widened corpus before changing runtime logic (`S`)
   - Use the existing helper/corpus path for the committed fixtures.
   - If the new fixture is not yet committed, use the helper’s ad hoc single-fixture mode first to measure it cheaply before widening the canonical corpus.
   - Inspect the resulting `page_html_v1` artifacts manually and record exact snippets.

3. Only if the new fixture is weak or ambiguous, run one stronger direct baseline on that same fixture (`XS-S`)
   - Keep this bounded to the weakest new case rather than doing a provider sweep.
   - Decision rule:
     - if the generic seam still clears, keep architecture simple;
     - if a stronger direct call materially wins, document whether that exposes a real maintained-seam gap or only bounds the unsupported slice.

4. Widen the maintained corpus and truth surfaces (`XS-S`)
   - Add the third fixture to `benchmarks/golden/handwritten-notes/corpus.json`.
   - Update `tests/test_handwritten_notes_eval.py` and any cheap intake smoke tests needed for the new fixture.
   - Update `docs/evals/registry.yaml`, `docs/build-map.md`, `tests/fixtures/formats/_coverage-matrix.json`, and `testdata/README.md` only as far as the new evidence supports.

### Impact Analysis

- **Primary blast radius:** handwritten fixture assets, the handwritten eval helper/corpus, and the build-map / registry / coverage truth surfaces.
- **Secondary blast radius:** image-directory and PDF intake smoke coverage for the new fixture.
- **What could break:** corpus-loading assumptions, run-ID uniqueness, image-only PDF verification, or overstated support claims in large truth-surface docs.
- **Structural health note:** `docs/build-map.md` and `docs/evals/registry.yaml` are already large, so those edits should stay narrow and evidence-led.
- **Redundancy plan:** do not create a parallel handwritten comparison harness; fold any new case into the existing helper/corpus unless a one-off scratch probe is strictly temporary.

### Human-Approval Blockers

- **Fixture choice:** preferred path is a checked-in real handwritten sample if the rights/transcript retrieval is clean enough in one bounded pass; fallback is a third more degraded synthetic fixture in the same story.
- **No runtime expansion yet:** exploration did not justify a handwritten-only maintained seam, so implementation should stay fixture/eval-first unless the widened baseline falsifies that.

### What Done Looks Like

- The repo has a third handwritten proof case beyond the current synthetic pair.
- The maintained generic image-directory and PDF OCR lanes have fresh current-pass evidence on the widened corpus.
- If the new fixture is weak, one bounded stronger baseline explains whether the problem is evidence breadth or a real runtime seam.
- The build map, coverage matrix, eval registry, and fixture docs all tell the same post-story truth.

## Work Log

20260403-2135 — story created from `/triage`: converted the build map's top next action into a build-ready handwriting-breadth story after verifying the current substrate in code. Evidence reviewed in this pass: `docs/build-map.md` still says the maintained handwritten lane is only proven on a broader but still synthetic two-fixture slice and names a real or more degraded third fixture as the top next action; `benchmarks/scripts/run_handwritten_notes_eval.py`, `benchmarks/golden/handwritten-notes/corpus.json`, `tests/test_handwritten_notes_eval.py`, `tests/test_image_directory_intake_recipe.py`, `tests/test_pdf_intake_recipe.py`, and `testdata/generate_handwritten_notes_fixture.py` prove the maintained OCR/eval substrate already exists; `docs/runbooks/golden-build.md` is the only narrower handwriting-related guidance found outside the story chain. Result: this story is `Pending`, not `Draft`, because the missing slice is bounded to fixture/evidence widening rather than missing runtime substrate. Next step: `/build-story` should choose the third fixture candidate, rerun the maintained lanes on the widened corpus, and only consider a stronger direct baseline if the new fixture is weak or ambiguous.
20260403-2201 — `/build-story` exploration and baseline planning: verified the story is honestly buildable on existing maintained OCR/eval substrate and wrote the implementation plan without changing code. Context reviewed in this pass: `docs/ideal.md`, `docs/spec.md` (`spec:1.1`, `spec:2.1`, `spec:2.2`, `spec:8`), the handwritten row / Gap 4 / Gap 5 / Next Actions in `docs/build-map.md`, ADR-002, `docs/runbooks/golden-build.md`, Stories 179 and 182, `testdata/generate_handwritten_notes_fixture.py`, `benchmarks/scripts/run_handwritten_notes_eval.py`, `benchmarks/scorers/handwritten_notes_transcription.py`, `tests/test_handwritten_notes_eval.py`, `tests/test_image_directory_intake_recipe.py`, and `tests/test_pdf_intake_recipe.py`. Critical substrate verified in code: maintained image-directory/PDF OCR recipes exist; helper supports corpus mode plus ad hoc single-fixture mode; fixture-specific run IDs already prevent clobbering; cheap intake smoke coverage exists for current handwritten fixtures. Fresh baseline on current code via `python benchmarks/scripts/run_handwritten_notes_eval.py --output benchmarks/results/handwritten-notes-story185-baseline.json` returned `pass_rate = 1.0`, `overall_min_ratio = 1.0`, `page_min_ratio = 1.0`, `cases_total = 4`, `fixture_count = 2`, and image-only PDF verification of `[0, 0]` / `[0, 0, 0]`. Candidate-fixture exploration found one promising real-sample path: LOC item `https://www.loc.gov/pictures/item/2023637835/` exposes a handwritten letter image and states `Rights Advisory: No known restrictions on publication`; the front image fetched cleanly in planning at about `108 KB` and `1126x1435`, but transcript/back-image fetches intermittently returned `503`, so any real-sample path should check in the asset plus transcript and document the source URL instead of depending on a live fetch. Files likely to change in implementation: `testdata/`, `testdata/README.md`, `benchmarks/golden/handwritten-notes/corpus.json`, `benchmarks/scripts/run_handwritten_notes_eval.py`, `tests/test_handwritten_notes_eval.py`, `tests/test_image_directory_intake_recipe.py`, `tests/test_pdf_intake_recipe.py`, `docs/build-map.md`, `docs/evals/registry.yaml`, and `tests/fixtures/formats/_coverage-matrix.json`. Files at risk only if scope expands badly: `testdata/generate_handwritten_notes_fixture.py` and the large truth-surface docs. Surprise found: runtime substrate is not the hard part here; fixture ownership is. The cleanest real-sample candidate exists, but the honest implementation must avoid making repo reproducibility depend on a flaky live source. Next step: human gate on the plan before any code, fixture, or truth-surface changes.
20260403-2215 — implemented and closed the widened handwritten proof slice with the bounded synthetic fallback. I first re-tested the preferred real-fixture path against the Library of Congress item `https://www.loc.gov/pictures/item/2023637835/`; the rights signal was clean, but repeated live fetches for the second page and transcript returned `503`, so I kept reproducibility honest and fell back to a third repo-owned degraded synthetic fixture instead of vendoring a flaky partial import. Landed `testdata/handwritten-notes-faded.txt`, widened `testdata/generate_handwritten_notes_fixture.py` with the new `faded` preset, generated `testdata/handwritten-notes-faded-images/` plus `testdata/handwritten-notes-faded.pdf`, and widened `benchmarks/golden/handwritten-notes/corpus.json`, `tests/test_handwritten_notes_eval.py`, `tests/test_image_directory_intake_recipe.py`, and `tests/test_pdf_intake_recipe.py` to carry the third fixture. Fresh widened proof via `python benchmarks/scripts/run_handwritten_notes_eval.py --output benchmarks/results/handwritten-notes-story185-widened.json` returned `pass_rate = 1.0`, `overall_min_ratio = 1.0`, `page_min_ratio = 1.0`, `cases_total = 6`, `fixture_count = 3`, with image-only PDF verification of `{"handwritten-notes-mini": [0, 0], "handwritten-notes-faded": [0, 0], "handwritten-notes-rough": [0, 0, 0]}`. Manual artifact inspection in this same pass covered stamped manifest artifacts at `output/runs/handwritten-handwritten-notes-mini-image-generic/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl`, `output/runs/handwritten-handwritten-notes-faded-image-generic/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl`, `output/runs/handwritten-handwritten-notes-rough-image-generic/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl`, `output/runs/handwritten-handwritten-notes-mini-pdf-generic/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl`, `output/runs/handwritten-handwritten-notes-faded-pdf-generic/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl`, and `output/runs/handwritten-handwritten-notes-rough-pdf-generic/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl`; each stamped the expected absolute fixture source and page count. I also manually opened `output/runs/handwritten-handwritten-notes-faded-image-generic/02_ocr_ai_gpt51_v1/pages_html.jsonl` and `output/runs/handwritten-handwritten-notes-faded-pdf-generic/02_ocr_ai_gpt51_v1/pages_html.jsonl`; both preserved the harder page-2 snippet `The parcel for J. Mercer should include 3 seals, one wax cord, and the note from April 8.` exactly after normalization, with `ocr_quality = 0.98`, `ocr_integrity = 1.0`, and no need for a stronger direct handwritten-only baseline because the maintained generic seam already cleared the widened slice. Updated `docs/build-map.md`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, and `testdata/README.md` to reflect the wider but still synthetic three-fixture claim and the remaining real-handwriting gap. Validation in this close-out pass: `pytest -q tests/test_handwritten_notes_eval.py tests/test_image_directory_intake_recipe.py tests/test_pdf_intake_recipe.py`, `make lint`, and `make test` (`441 passed`, `4` pre-existing deprecation warnings). Recommended next step: `/check-in-diff`.
