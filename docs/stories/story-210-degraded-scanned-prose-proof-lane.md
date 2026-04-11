---
title: "Widen Scanned-Prose Proof Beyond the Clean Synthetic Fixture"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #1 (Ingest), Requirement #3 (Extract), Requirement #6 (Validate), Any format, any condition, Fidelity to the source, Minimum Viable Floor"
spec_refs:
  - "spec:1"
  - "spec:1.1"
  - "spec:2"
  - "spec:2.1"
  - "spec:2.2"
  - "spec:8"
adr_refs: []
depends_on:
  - "167"
category_refs:
  - "spec:1"
  - "spec:2"
  - "spec:8"
compromise_refs:
  - "C1"
  - "C2"
  - "C6"
  - "B1"
input_coverage_refs:
  - "scanned-pdf-prose"
architecture_domains:
  - "ocr_and_extraction"
roadmap_tags: []
legacy_system: ""
---

# Story 210 — Widen Scanned-Prose Proof Beyond the Clean Synthetic Fixture

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/RUNBOOK.md`, `docs/runbooks/golden-build.md`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/stories/story-157-pdf-intake-parity-with-image-directory-inputs.md`, `docs/stories/story-167-repo-owned-scanned-prose-pdf-fixture.md`, and `None found after search in docs/decisions/`, `docs/scout/`, and `docs/notes/` for a narrower degraded-scanned-prose proof ADR or note
**Depends On**: Story 167

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

Story 167 honestly proved the maintained scanned-PDF prose lane only on one
clean repo-owned synthetic fixture, `testdata/scanned-prose-mini.pdf`. The
coverage row still says broader noisy real-world scanned prose remains
unmeasured, which means the repo does not yet know whether `scanned-pdf-prose`
deserves a family-level `passing` claim or a narrower bounded proof note. This
story adds the next honest proof slice: a degraded/noisy scanned-prose input
with fresh `driver.py` evidence, artifact inspection, and an explicit rule
that the row may widen or narrow based on what the current maintained OCR lane
actually does.

## Acceptance Criteria

- [x] A degraded/noisy scanned-prose proof input exists and is documented honestly:
  - [x] a repo-owned reproducible degraded fixture now exists under `testdata/` via `generate_scanned_prose_fixture.py --preset degraded`, sharing the checked-in `scanned-prose-mini.md` source text and explicit preset settings
  - [x] the comparison-only fallback was not needed because the repo-owned path stayed honest in this pass
  - [x] the intended support slice stays explicit: degraded/noisy synthetic scanned prose only, not handwritten notes, tables, or born-digital PDFs
- [x] A fresh current-tip proof exists for the maintained generic PDF OCR lane on the widened slice:
  - [x] `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` was run through `driver.py` on `testdata/scanned-prose-degraded.pdf`
  - [x] the work log names the exact `output/runs/` artifact paths inspected, including `page_image_v1` provenance and `page_html_v1` OCR output
  - [x] the work log compares the OCR result against the checked-in source text and names representative success and failure modes
- [x] The story measures the smallest honest challenger only if the baseline is insufficient:
  - [x] baseline first: the current maintained OCR path ran unchanged before any runtime logic was considered
  - [x] a second candidate was not needed because the baseline result was already sufficient to widen the bounded claim
  - [x] the story did not turn a proof gap into a broad OCR bake-off
- [x] Canonical truth surfaces reflect the result honestly:
  - [x] `tests/fixtures/formats/_coverage-matrix.json` plus related docs now widen the `scanned-pdf-prose` claim with precise scope, date, and notes
  - [x] the row keeps the remaining caveat explicit instead of reading broader than the evidence
  - [x] `make methodology-compile` refreshes generated `docs/stories.md` and `docs/methodology/graph.json` after the authored story/truth surfaces were updated

## Out of Scope

- Handwritten-note support, cursive OCR, or any work on Story 191's blocked handwritten line
- Genealogy/table-heavy scanned PDFs already covered by the Onward lane
- Born-digital PDF routing or `doc-web` boundary changes already settled elsewhere
- Manual edits to OCR artifacts or transcripts that hide fidelity problems instead of measuring them
- A broad model sweep beyond the smallest bounded challenger needed to answer the scanned-prose breadth question

## Approach Evaluation

- **Simplification baseline**: first run the existing maintained `recipe-pdf-ocr-html-mvp.yaml` path unchanged on a degraded/noisy scanned-prose input. If the current one-pass OCR lane already preserves fidelity on that wider slice, there is no reason to invent new runtime logic.
- **AI-only**: a stronger direct OCR call could be a bounded challenger if the maintained baseline clearly fails, but only after the degraded/noisy proof surface exists. It is a comparison move, not the starting point.
- **Hybrid**: likely strongest. Reuse code for fixture generation, degradation controls, comparison helpers, and cheap smoke coverage, while leaving OCR intelligence to the maintained AI lane and any single bounded challenger.
- **Pure code**: appropriate only for fixture generation, degradation, smoke wiring, and comparison/reporting. It cannot answer the OCR quality question by itself.
- **Repo constraints / prior decisions**: `spec:1.1` keeps explicit recipes in place; `spec:2.1` and `spec:2.2` mean OCR quality must be measured and cost-aware; Story 157 already proved maintained PDF entry; Story 167 proved only the clean synthetic scanned-prose slice; `docs/runbooks/golden-build.md` provides the repo-owned truth-surface discipline. No narrower ADR changes the direction.
- **Existing patterns to reuse**: `testdata/generate_scanned_prose_fixture.py`, `tests/test_pdf_intake_recipe.py`, `configs/recipes/recipe-pdf-ocr-html-mvp.yaml`, Story 167's fixture/proof workflow, Story 179's bounded fixture-plus-scored-baseline pattern, and the current `scanned-pdf-prose` coverage-row notes in `tests/fixtures/formats/_coverage-matrix.json`.
- **Eval**: the deciding evidence is fresh `driver.py` proof on a degraded/noisy scanned-prose input plus manual artifact inspection against an explicit source/ground-truth surface. If the baseline is clearly below bar, the story may compare one bounded challenger before deciding whether the row should widen or narrow.

## Tasks

- [x] Freeze the current gap from repo evidence:
  - [x] recorded that `scanned-pdf-prose` was previously `passing` only on `testdata/scanned-prose-mini.pdf`
  - [x] recorded the exact known-gap language that broader noisy real-world scanned prose remained unmeasured
  - [x] inspected Story 167 and the current coverage row so the new proof surface did not silently overstep what was already known
- [x] Add or pin the degraded/noisy proof input:
  - [x] landed a repo-owned reproducibly generated degraded/noisy scanned-prose fixture under `testdata/`
  - [x] the comparison-only fallback path was not needed
  - [x] source-text provenance stays explicit via the shared checked-in `scanned-prose-mini.md`
- [x] Run the baseline proof before changing runtime behavior:
  - [x] ran `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` through `driver.py`
  - [x] inspected `page_image_v1` provenance and `page_html_v1` OCR artifacts in `output/runs/`
  - [x] compared output against the checked-in source and recorded the remaining representative fidelity caveat
- [x] Measure the smallest honest challenger only if the baseline result leaves the coverage decision unresolved
- [x] Add or extend the smallest repeatable proof surface needed for future passes:
  - [x] extended the existing scanned-prose generator with a deterministic `degraded` preset
  - [x] added cheap smoke coverage in `tests/test_pdf_intake_recipe.py`
- [x] If this story changes documented format coverage or graduation reality: update `tests/fixtures/formats/_coverage-matrix.json` and any relevant methodology state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] cleared stale `*.pyc`, ran through `driver.py`, verified artifacts in `output/runs/`, and manually inspected sample JSON/JSONL data
  - [x] not applicable: agent tooling did not change, so `make skills-check` was not needed
- [x] If evals or goldens changed: not applicable, no eval registry or golden surface changed
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: the widened proof names the exact fixture/input, run ID, and inspected artifacts
  - [x] T1 — AI-First: no deterministic OCR repair logic was added because the maintained OCR lane answered the question directly
  - [x] T2 — Eval Before Build: baseline proof was measured before the coverage claim changed
  - [x] T3 — Fidelity: source content was compared honestly, with the remaining heading-tag caveat recorded rather than patched away
  - [x] T4 — Modular: the maintained generic PDF OCR recipe and existing fixture-generation pattern were reused instead of inventing a prose-only runtime lane
  - [x] T5 — Inspect Artifacts: real `output/runs/` artifacts were inspected, not just test exits or aggregate scores

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

- **Owning module / area**: the repo-owned scanned-prose fixture/generation surface, the maintained generic PDF OCR proof lane, and the canonical format-coverage truth surfaces.
- **Methodology reality**: this work belongs to `spec:1`, `spec:2`, and `spec:8`. In `docs/methodology/state.yaml`, the category substrates already exist; `C2` and `C1` remain in `climb`, `C6` remains in `hold`, and this story widens the `scanned-pdf-prose` row from clean-only evidence to a bounded clean-plus-synthetic-degraded support slice while keeping broader real-world degraded prose explicitly unmeasured.
- **Substrate evidence**: verified in this pass that `testdata/generate_scanned_prose_fixture.py` now owns deterministic `clean` and `degraded` presets from the same checked-in source text, `tests/test_pdf_intake_recipe.py` now carries degraded scanned-prose extract-only smoke coverage, `configs/recipes/recipe-pdf-ocr-html-mvp.yaml` remains the maintained generic PDF OCR lane, and the fresh proof run `story210-scanned-prose-degraded-proof` recorded both `page_image_v1` provenance and `page_html_v1` OCR output on the committed degraded fixture.
- **Data contracts / schemas**: prefer to keep the story inside existing `page_image_v1` and `page_html_v1` artifacts. No schema change is expected unless a new cross-stage proof artifact is introduced, which should be avoided if a story-local or benchmark-local result file is sufficient.
- **File sizes**: `testdata/generate_scanned_prose_fixture.py` is 169 lines, `tests/test_pdf_intake_recipe.py` is 217 lines, `testdata/README.md` is 137 lines, `tests/fixtures/formats/_coverage-matrix.json` is 557 lines, and `docs/RUNBOOK.md` is 773 lines. The coverage matrix and runbook are already large; edits there should stay surgical.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/RUNBOOK.md`, `docs/runbooks/golden-build.md`, Story 157, Story 167, and `tests/fixtures/formats/_coverage-matrix.json`. Search across `docs/decisions/`, `docs/scout/`, and `docs/notes/` found no narrower degraded-scanned-prose decision document, so a new story is the honest packaging.

## Files to Modify

- `docs/stories/story-210-degraded-scanned-prose-proof-lane.md` — keep the story record, work log, and close-out truth current (127 lines)
- `testdata/generate_scanned_prose_fixture.py` — widen the existing generator or split out the smallest explicit degraded/noisy variant path (169 lines)
- `testdata/README.md` — document the widened scanned-prose fixture surface and any generation caveats (137 lines)
- `tests/test_pdf_intake_recipe.py` — add cheap proof coverage for the degraded/noisy scanned-prose input if it becomes repo-owned (217 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — widen or narrow the `scanned-pdf-prose` claim honestly based on fresh evidence (557 lines)
- `docs/RUNBOOK.md` — publish the exact proof command and caveat if this story changes the documented support surface (773 lines)
- `testdata/scanned-prose-*` — new or updated repo-owned source/generation assets for the degraded/noisy proof slice (new files)
- `docs/evals/registry.yaml` or a new narrow helper under `benchmarks/` — only if the story promotes a durable scored proof surface beyond story-local comparison notes

## Redundancy / Removal Targets

- Any wording that lets the clean `scanned-prose-mini` proof read like broader degraded/noisy scanned-prose support
- Any ad hoc local comparison notes that become unnecessary once a repo-owned degraded/noisy fixture lands
- Any duplicate degraded-fixture helper path if the existing scanned-prose generator can own the new slice cleanly

## Notes

- New story justification: Story 167 closed the clean synthetic repo-owned fixture seam and validated it. This new work has a different validation boundary: degraded/noisy scanned-prose breadth. Reopening Story 167 would blur already-verified history and the wider claim decision this story needs to make.
- The honest outcome may be negative. If the degraded/noisy proof fails, the story should narrow the support claim instead of preserving `passing` by inertia.
- Prefer repo-owned proof where licensing and reproducibility allow. If the only honest widened input is comparison-only, the story should say so explicitly and keep the shipped claim narrow.

## Plan

1. Lock the exact current claim and gap before changing files.
   - Re-read the `scanned-pdf-prose` row, Story 167, and the maintained PDF OCR recipe so the story starts from explicit bounded truth rather than a vague "more realism" goal.
2. Choose the smallest honest degraded/noisy proof input.
   - Prefer a repo-owned or reproducibly generated degraded variant of the existing scanned-prose source text.
   - Fall back to a comparison-only local input only if the repo-owned path is not honest in this pass.
3. Run the maintained baseline unchanged.
   - Fresh `driver.py` proof and artifact inspection come before any new runtime or benchmark work.
4. Decide the row truth from evidence, not optimism.
   - If the widened proof is strong, update the row/docs narrowly.
   - If it is weak or mixed, narrow the claim or keep it explicitly bounded.

## Work Log

20260410-2246 — story created from `/triage`: identified the strongest unblocked honesty gap after verifying that Story 191 remains blocked, the inbox is empty, the crop C5 page-context gate has just closed negative, and the intake/direct-entry eval surfaces are fresh. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/RUNBOOK.md`, `docs/runbooks/golden-build.md`, Story 157, Story 167, `testdata/generate_scanned_prose_fixture.py`, `tests/test_pdf_intake_recipe.py`, and `configs/recipes/recipe-pdf-ocr-html-mvp.yaml`. Result: a new story is honest instead of reopening Story 167 because the old story closed the clean synthetic fixture seam, while this follow-up has a different success surface: degraded/noisy scanned-prose breadth that may widen or narrow the family claim. The story starts `Pending`, not `Draft`, because the maintained PDF OCR lane, fixture-generation pattern, smoke coverage, and proof path all exist in the repo today; the missing slice is the widened degraded/noisy proof input and the resulting support decision. Next step: `/build-story` should lock the smallest honest degraded/noisy proof input, run the maintained baseline unchanged, and only then decide whether the row widens or narrows.
20260410-2306 — exploration + baseline probe: re-read Story 167, the current `scanned-pdf-prose` coverage row, `tests/test_pdf_intake_recipe.py`, `docs/RUNBOOK.md`, and the existing generator to lock the exact current claim before editing. The row was still bounded to `testdata/scanned-prose-mini.pdf` with the explicit gap text `Current evidence is a clean synthetic scanned fixture only; broader noisy real-world scanned-prose quality remains unmeasured.` I then built a scratch degraded probe at `/tmp/scanned-prose-degraded-probe.pdf` from the same checked-in source text, verified it stayed image-only (`pypdf` extract-text lengths `[0, 0, 0, 0]`), and ran the maintained lane unchanged through `driver.py` (`story210-degraded-probe`). Artifact inspection showed the baseline already answered the story without any challenger: `output/runs/story210-degraded-probe/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl` preserved four `page_image_v1` rows, `output/runs/story210-degraded-probe/02_ocr_ai_gpt51_v1/pages_html.jsonl` recorded `ocr_quality` `0.96`, `0.97`, `0.97`, `0.99`, and a normalized comparison against `testdata/scanned-prose-mini.md` produced ratio `0.996038`. Representative caveat from the probe: some section-transition headings at page boundaries degraded to paragraph tags even though the prose stayed intact. Result: the smallest honest next move was fixture + truth-surface work only; no runtime OCR change or challenger run was needed. Next step: land the deterministic degraded preset in the repo, add cheap smoke coverage, and rerun the proof on the committed fixture path.
20260410-2313 — implementation + verification: extended `testdata/generate_scanned_prose_fixture.py` with deterministic `clean` and `degraded` presets, generated the committed fixture `testdata/scanned-prose-degraded.pdf` (4 pages, 1.0 MB), added degraded extract-only smoke coverage in `tests/test_pdf_intake_recipe.py`, and updated `testdata/README.md`, `docs/RUNBOOK.md`, and `tests/fixtures/formats/_coverage-matrix.json` so the bounded support claim matches current evidence. Fresh checks: `python -m pytest tests/test_pdf_intake_recipe.py -q` passed (`13 passed in 6.99s`); `find modules -name '*.pyc' -delete` cleared stale bytecode; `python driver.py --recipe configs/recipes/recipe-pdf-ocr-html-mvp.yaml --input-pdf testdata/scanned-prose-degraded.pdf --run-id story210-scanned-prose-degraded-proof --output-dir output/runs/story210-scanned-prose-degraded-proof --allow-run-id-reuse --force --end-at ocr_ai` completed successfully. Manual artifact inspection: `output/runs/story210-scanned-prose-degraded-proof/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl` contains four stamped `page_image_v1` rows all sourced from `/Users/cam/.codex/worktrees/9525/doc-web/testdata/scanned-prose-degraded.pdf`; `output/runs/story210-scanned-prose-degraded-proof/02_ocr_ai_gpt51_v1/pages_html.jsonl` contains four stamped `page_html_v1` rows with `ocr_quality` `0.97`, `0.98`, `0.97`, and `0.99`. Comparison against the shared checked-in source `testdata/scanned-prose-mini.md` produced normalized ratio `0.996038`: prose content stayed intact, page 1 preserved `Harbor Ledger Notes` / `Morning Light` with proper heading tags, and the remaining representative failure mode is that later section-transition headings such as `The Index Table` and `Closing the Shutters` still arrived as paragraphs on some page boundaries. Result: the row widened honestly to one bounded synthetic degraded/noisy simple-prose slice, while broader real-world degraded scans remain explicitly unmeasured. Next step: run `make lint`, `make test`, and `make methodology-check`, then leave the story ready for `/validate`.
20260410-2325 — repo-wide verification + build handoff: regenerated the methodology views with `make methodology-compile`, then ran `make lint`, `make methodology-check`, and `make test`. Results: `ruff` passed cleanly, the methodology graph check reported `docs/methodology/graph.json` current, and the full suite passed (`555 passed, 4 warnings in 654.99s`). The warnings are pre-existing Pydantic V2 deprecations in `modules/portionize/portionize_headers_numeric_v1/main.py`, not regressions from this story. Result: the implementation is build-complete and freshly verified at the repo level, but the story stays `In Progress` with the validation/done gates open for a separate `/validate` / `/mark-story-done` pass. Next step: independent validation of the new degraded scanned-prose support claim and artifact review path.
20260410-2339 — degraded fixture strengthened after manual visual review: the first committed `degraded` preset looked too close to the clean scanned-prose slice, so the generator was tightened instead of papering over that mismatch in docs. `testdata/generate_scanned_prose_fixture.py` now applies heavier blur, lower contrast, stronger scan noise, mild skew, a downsample/upscale pass, and faint edge shadow to the degraded preset. Visual check on `output/runs/story210-degraded-visual-check/01_extract_pdf_images_fast_v1/images/page-001.jpg` confirmed the page is now visibly rougher than the clean slice while remaining clearly prose, not handwriting. Fresh checks after the stronger preset: `python -m pytest tests/test_pdf_intake_recipe.py -q` passed again (`13 passed in 7.26s`); `testdata/scanned-prose-degraded.pdf` still reports extract-text lengths `[0, 0, 0, 0]`; `python driver.py --recipe configs/recipes/recipe-pdf-ocr-html-mvp.yaml --input-pdf testdata/scanned-prose-degraded.pdf --run-id story210-scanned-prose-degraded-proof --output-dir output/runs/story210-scanned-prose-degraded-proof --allow-run-id-reuse --force --end-at ocr_ai` re-completed successfully. Manual artifact inspection on the rerun showed `output/runs/story210-scanned-prose-degraded-proof/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl` still stamping all four `page_image_v1` rows back to the committed fixture, and `output/runs/story210-scanned-prose-degraded-proof/02_ocr_ai_gpt51_v1/pages_html.jsonl` now reports lower page-level `ocr_quality` values `0.96`, `0.96`, `0.94`, `0.96` while preserving the same normalized text ratio `0.996038` against `testdata/scanned-prose-mini.md`. Result: the support claim remains widened, but now against a visibly rougher synthetic degraded scan instead of an asset that looked nearly pristine. Next step: refresh the docs/truth surfaces to the new current metrics and rerun lightweight verification (`make lint`, `make methodology-check`) for this final preset adjustment.
20260411-0008 — story closed via `/mark-story-done`: reran the full validation surface after the stronger degraded preset so the close-out rests on current evidence, not the earlier milder asset. Fresh close-out checks in this pass: `python -m pytest tests/` passed (`555 passed, 4 warnings in 655.99s`), `make lint` passed, `make methodology-compile` regenerated the story/index views, and `make methodology-check` confirmed the compiled graph is current. Fresh artifact evidence remains the same bounded but now visually rougher proof surface: `output/runs/story210-scanned-prose-degraded-proof/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl` still traces all four `page_image_v1` rows to `testdata/scanned-prose-degraded.pdf`; `output/runs/story210-scanned-prose-degraded-proof/02_ocr_ai_gpt51_v1/pages_html.jsonl` still preserves the prose with normalized ratio `0.996038` while page-level `ocr_quality` sits at `0.96`, `0.96`, `0.94`, and `0.96`; and `output/runs/story210-degraded-visual-check/01_extract_pdf_images_fast_v1/images/page-001.jpg` confirms the final degraded preset now looks meaningfully rougher than the clean scanned-prose slice. Result: Story 210 closes honestly as a bounded support-widening pass for synthetic degraded scanned prose, with the real-world degraded-handwriting / historical-script gap explicitly split into Story 211. Next step: `/check-in-diff`.
