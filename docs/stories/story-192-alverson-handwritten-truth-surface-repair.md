---
title: "Repair Alverson Handwritten Truth Surface and Rebaseline the Handwritten Corpus"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #1 (Ingest), Requirement #3 (Extract), Requirement #6 (Validate), Traceability is the product, Fidelity to the source"
spec_refs:
  - "spec:1"
  - "spec:1.1"
  - "spec:2"
  - "spec:2.1"
  - "spec:8"
adr_refs: []
depends_on: []
category_refs:
  - "spec:1"
  - "spec:2"
  - "spec:8"
compromise_refs:
  - "B1"
  - "B5"
  - "C1"
input_coverage_refs:
  - "handwritten-notes"
architecture_domains:
  - "ocr_and_extraction"
roadmap_tags:
  - "campaign:maintained-intake-honesty"
legacy_system: ""
---

# Story 192 — Repair Alverson Handwritten Truth Surface and Rebaseline the Handwritten Corpus

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/runbooks/golden-build.md`, `docs/stories/story-189-improve-real-handwritten-barney-fidelity.md`, `docs/stories/story-191-finish-real-handwritten-ocr-on-the-loc-fixture-pair.md`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, `testdata/README.md`, `benchmarks/golden/handwritten-notes/corpus.json`, `https://www.loc.gov/pictures/item/2023637835/`, and `None found after search in docs/decisions/`, `docs/scout/`, and `docs/notes/` for a narrower handwritten-fixture-alignment ADR or runbook
**Depends On**: —

## Goal

Story 191 is blocked for two reasons that should not stay coupled: the maintained handwritten OCR seam still misses the real Barney slice, and the Alverson fixture itself is not currently an honest OCR target because the checked-in front-page image ends where the transcript continues. This story repairs the Alverson source/transcript contract, reruns the maintained handwritten eval on a corrected real-fixture corpus, and leaves behind an honest answer about whether the remaining handwritten problem is now pure OCR quality or still blocked on fixture truth. It exists as a new story instead of reopening Story 191 because the validation surface is different: Story 191 is an OCR-runtime decision, while this story is a fixture/golden/eval-truth repair that must complete before more OCR tuning can be interpreted honestly.

## Acceptance Criteria

- [x] A fresh source audit exists for LOC item `2023637835` that names the exact checked-in Alverson page scope the repo will score going forward, cites the source asset(s) used, and records whether the honest fix is a front-page-only transcript trim or a widened front/back fixture pair.
- [x] The checked-in Alverson fixture package becomes source-faithful: transcript, image asset(s), PDF wrapper, `benchmarks/golden/handwritten-notes/corpus.json`, tests, and `testdata/README.md` all agree on the same page scope, and the work log names the specific lines or page segments manually verified against source.
- [x] A fresh rerun of `handwritten-notes-transcription` exists under `benchmarks/results/` and `output/runs/` on the corrected corpus, and the work log cites the exact Alverson and Barney artifact paths inspected plus the new corpus-wide ratios.
- [x] `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, and the blocked Story 191 record are updated so future triage can tell whether the remaining handwritten blocker is now OCR-only, still mixed, or cleared enough to reopen the runtime line honestly.

## Out of Scope

- Adding a new handwritten OCR rescue helper, overlap-merge path, or model-specific runtime logic
- Barney-specific or Alverson-specific deterministic text repair
- Widening the handwritten family beyond the current repo-owned LOC/ synthetic corpus
- Changing the accepted `doc-web` / Dossier boundary or any other non-handwritten format lane
- Hiding OCR misses by masking in-scope source content without documenting the scope change explicitly

## Approach Evaluation

- **Simplification baseline**: first verify whether the story is solved by the smallest possible truth-surface correction: trim `testdata/handwritten-notes-alverson-real.txt` to the visible checked-in front page and rerun the existing corpus. If that makes the eval honest enough to isolate the remaining blocker, no new page asset or runtime code should be added.
- **AI-only**: a multimodal model could propose front/back transcript boundaries or help transcribe a missing back page, but the model cannot become the final authority. Any AI-generated alignment must still be manually verified against the LOC source before it becomes a committed golden.
- **Hybrid**: likely the honest default. Use the official LOC source plus the current checked-in transcript to decide scope, let AI assist only where the boundary is ambiguous, and keep code changes limited to fixture metadata, tests, and eval plumbing.
- **Pure code**: only appropriate for fixture packaging, PDF wrapper regeneration, corpus metadata updates, smoke-test expectations, and methodology/eval docs. Pure code is not sufficient to infer the correct transcript boundary without source review.
- **Repo constraints / prior decisions**: `docs/ideal.md` and `spec:2` require fidelity to the visible source, not the transcript we hoped we had. `docs/runbooks/golden-build.md` requires manual source verification before updating goldens. Story 191 already proved that more OCR probing against the current Alverson package is misleading, so this story must repair truth first and must not smuggle a weaker handwritten product claim into benchmark scoping.
- **Existing patterns to reuse**: reuse `benchmarks/scripts/run_handwritten_notes_eval.py`, `benchmarks/golden/handwritten-notes/corpus.json`, the handwritten image/PDF smoke tests, the `testdata/README.md` regeneration guidance, and Story 191's blocker evidence rather than inventing a new handwritten benchmark surface.
- **Eval**: the discriminator is the existing `handwritten-notes-transcription` surface in `docs/evals/registry.yaml`. Success is not “Alverson passes”; success is that the corrected corpus is source-faithful, rerun results are fresh, and the remaining blocker is classified honestly. Manual inspection of the corrected Alverson artifacts is mandatory.

## Tasks

- [x] Re-audit LOC item `2023637835` against the checked-in Alverson assets and record the exact visible source boundary plus the smallest honest repair candidate set:
  - [x] Option A chosen: trim the transcript to the checked-in front-page image only
  - [x] Option B rejected after source audit because the repo-owned fixture and benchmark scope remain front-page-only in this story
- [x] Implement the smallest honest truth-surface repair and manually verify the corrected transcript/page scope against source before changing any eval claims
- [x] Update the handwritten corpus package coherently:
  - [x] `benchmarks/golden/handwritten-notes/corpus.json` — confirmed the existing front-page-only metadata remained accurate; no edit needed
  - [x] `testdata/README.md`
  - [x] `tests/test_handwritten_notes_eval.py`
  - [x] `tests/test_image_directory_intake_recipe.py` — confirmed the existing one-page smoke coverage remained accurate; no edit needed
  - [x] `tests/test_pdf_intake_recipe.py` — confirmed the existing one-page smoke coverage remained accurate; no edit needed
- [x] Rerun `handwritten-notes-transcription` on the corrected corpus, inspect the corrected Alverson and Barney `page_html_v1` artifacts under `output/runs/`, and record the exact ratios plus sample text checked manually
- [x] Update `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, and the blocked Story 191 record so the handwritten status and next-step recommendation reflect the corrected corpus rather than the current mixed truth surface
- [x] Regenerate generated methodology views with `make methodology-compile` and confirm the story/index surfaces stay aligned
- [x] If this story changes documented format coverage or graduation reality: update `tests/fixtures/formats/_coverage-matrix.json` and any relevant methodology state honestly
- [x] Check whether the chosen implementation makes any existing transcript variant, fixture note, or blocker wording redundant; remove it or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: not applicable; no runtime/module behavior changed in this story
  - [x] If agent tooling changed: not applicable
- [x] If evals or goldens changed: run `/improve-eval` and update `docs/evals/registry.yaml`
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: the corrected Alverson transcript and page asset(s) trace cleanly to named LOC source pages and checked-in repo files
  - [x] T1 — AI-First: AI is used only where it improves source alignment work; no unnecessary handwritten heuristics are added
  - [x] T2 — Eval Before Build: the existing handwritten eval is rerun before any recommendation to reopen OCR runtime work
  - [x] T3 — Fidelity: the golden/transcript no longer claims text that is absent from the visible source
  - [x] T4 — Modular: the fix stays inside fixture/eval/docs ownership unless a later story explicitly reopens OCR runtime work
  - [x] T5 — Inspect Artifacts: corrected Alverson and Barney artifacts are manually opened and checked, not just scored

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

- **Owning module / area**: handwritten fixture ownership under `testdata/`, handwritten eval/golden ownership under `benchmarks/golden/handwritten-notes/` and `benchmarks/scripts/run_handwritten_notes_eval.py`, plus handwritten truth surfaces in docs.
- **Methodology reality**: this belongs to `spec:1`, `spec:2`, and `spec:8`. `docs/methodology/state.yaml` marks all three substrates as `exists`, with `spec:1` and `spec:2` in active focus and `C1` / `B5` still in `climb`. The relevant coverage row is `handwritten-notes`, which remains `has-fixture` after this story because the corrected corpus is now honestly blocked by OCR misses on Barney and the visible Alverson front page, not by an internal source/transcript mismatch.
- **Substrate evidence**: verified locally that `benchmarks/golden/handwritten-notes/corpus.json`, `benchmarks/scripts/run_handwritten_notes_eval.py`, `testdata/handwritten-notes-alverson-real.txt`, `testdata/handwritten-notes-alverson-real-images/page-001.jpg`, `testdata/handwritten-notes-alverson-real.pdf`, and focused handwritten smoke coverage in `tests/test_handwritten_notes_eval.py`, `tests/test_image_directory_intake_recipe.py`, and `tests/test_pdf_intake_recipe.py` already exist. No new runtime substrate is needed before this story can start.
- **Data contracts / schemas**: no pipeline schema change is expected. The story should stay within fixture files, eval metadata, tests, and methodology/docs. If implementation unexpectedly changes output fields or artifact shapes, the story must add `schemas.py` updates explicitly before any stamped artifact claim.
- **File sizes**: likely touched files are `docs/stories/story-191-finish-real-handwritten-ocr-on-the-loc-fixture-pair.md` (277 lines), `benchmarks/golden/handwritten-notes/corpus.json` (53), `testdata/README.md` (97), `testdata/handwritten-notes-alverson-real.txt` (25), `tests/test_handwritten_notes_eval.py` (170), `tests/test_image_directory_intake_recipe.py` (276), `tests/test_pdf_intake_recipe.py` (197), `docs/evals/registry.yaml` (1429), and `tests/fixtures/formats/_coverage-matrix.json` (465). `docs/evals/registry.yaml` is already well over 500 lines, so edits there must stay surgical.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/runbooks/golden-build.md`, Story 189, Story 191, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, `testdata/README.md`, and the official LOC item page for `2023637835`. No narrower ADR or runbook was found for handwritten fixture-truth repair, which is why this story keeps the scope at fixture/eval honesty rather than architecture.

## Files to Modify

- `testdata/handwritten-notes-alverson-real.txt` — trim or split the transcript so it matches the committed source page scope (25 lines)
- `testdata/handwritten-notes-alverson-real-images/` — possibly replace or widen the checked-in Alverson source page assets to the exact LOC scope being scored (binary asset, current checked-in front page only)
- `testdata/handwritten-notes-alverson-real.pdf` — regenerate the image-only PDF wrapper so it matches the corrected page scope (binary asset)
- `benchmarks/golden/handwritten-notes/corpus.json` — correct fixture metadata and any page-scope assumptions for the Alverson row (53 lines)
- `tests/test_handwritten_notes_eval.py` — keep handwritten corpus expectations aligned with the corrected fixture scope (170 lines)
- `tests/test_image_directory_intake_recipe.py` — update Alverson image-entry smoke expectations if page count or asset shape changes (276 lines)
- `tests/test_pdf_intake_recipe.py` — update Alverson PDF-entry smoke expectations if wrapper page count changes (197 lines)
- `testdata/README.md` — document the corrected Alverson fixture scope, provenance, and regeneration instructions (97 lines)
- `docs/evals/registry.yaml` — record the corrected-corpus rerun and the remaining handwritten blocker honestly (1429 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — reflect the corrected handwritten fixture scope and remaining gap claims (465 lines)
- `docs/stories/story-191-finish-real-handwritten-ocr-on-the-loc-fixture-pair.md` — update the blocked OCR-runtime line to point at the corrected truth surface and next honest status (277 lines)

## Redundancy / Removal Targets

- The current over-scoped Alverson transcript lines that extend beyond the visible checked-in front-page source, if the honest repair is a front-page trim
- Any stale README, coverage-matrix, or eval-registry wording that still implies the current Alverson front-page package is already a clean OCR target
- Any temporary local source-alignment notes that are superseded once the corrected fixture scope is committed and documented

## Notes

- New story justification: reopening Story 191 immediately would be dishonest because it would mix fixture-truth repair with OCR-runtime improvement under one success surface. This story isolates the golden/fixture contract first; Story 191 can reopen only if the corrected corpus leaves a clean OCR-only blocker.
- Bias toward the smallest honest scope repair. If a front-page transcript trim is sufficient to make the benchmark honest, prefer that over widening the fixture pair. If the intended OCR target genuinely needs both pages, then widen explicitly and split the transcript per page instead of pretending a one-page fixture contains two pages of text.
- Do not turn benchmark scoping into product policy. Repairing the Alverson golden may make the handwritten eval fairer, but it does not strengthen the repo’s handwritten support claim unless the rerun evidence actually improves.

## Plan

### Recommendation

Proceed with the front-page transcript repair first, not a widened front/back fixture pair. Fresh source review in this pass confirms that LOC item `2023637835` exposes separate front/back original images (`LC-DIG-ppmsca-86651` / `LC-DIG-ppmsca-86652`) while the checked-in repo asset is a single front-page image (`638x1024`) that visibly ends at the same `...exceptable and` boundary where OCR stops. A no-code trim probe against a fresh current-pass Alverson run improved the maintained rescue score from `0.496975 / 0.501513` to `0.678867 / 0.685174` (image / pdf), which is strong evidence that the current benchmark is partially golden-wrong even though OCR quality is still below bar. That makes a transcript trim the smallest honest first move.

### Implementation Order

1. **Record the source audit and trim the transcript to the visible front page** (`XS`)
   - **Files**:
     - `testdata/handwritten-notes-alverson-real.txt`
     - `testdata/README.md`
     - this story file
   - **What changes**:
     - trim the committed Alverson transcript so it ends at the visible front-page boundary instead of continuing into the missing back-page text
     - update README provenance text to cite the current LOC front/back split and make the front-page-only scope explicit
     - log the exact evidence used: current local image dimensions `(638, 1024)`, visible ending at `...exceptable and`, and LOC item page metadata showing separate front/back download surfaces
   - **Impact / risk**:
     - smallest possible truth-surface repair
     - no recipe/runtime blast radius
     - risk is only that the visible boundary is transcribed incorrectly, so manual image review is mandatory
   - **Done looks like**:
     - the transcript claims only text visible on the checked-in front page
     - README no longer implies the repo fixture contains the full letter

2. **Keep the handwritten corpus and smoke tests aligned with the new scope** (`S`)
   - **Files**:
     - `benchmarks/golden/handwritten-notes/corpus.json`
     - `tests/test_handwritten_notes_eval.py`
     - `tests/test_image_directory_intake_recipe.py`
     - `tests/test_pdf_intake_recipe.py`
   - **What changes**:
     - keep the Alverson row/page-count assumptions explicitly front-page-only
     - update any test copy or fixture commentary that still treats the transcript as broader than the checked-in source
   - **Impact / risk**:
     - protects the corrected truth surface from drifting back
     - likely low-risk because page counts remain `1` unless unexpected fixture packaging issues surface
   - **Done looks like**:
     - corpus metadata and smoke expectations all agree on the front-page-only scope

3. **Rerun the handwritten eval on the corrected corpus and inspect artifacts** (`S`)
   - **Files**:
     - run outputs under `output/runs/`
     - result JSON under `benchmarks/results/` or a scoped temp result promoted into the work log
   - **What changes**:
     - rerun the Alverson single-fixture probe first to confirm the trimmed transcript behaves as expected
     - rerun the full `handwritten-notes-transcription` corpus after the committed trim
     - manually inspect the fresh Alverson and Barney `page_html_v1` artifacts
   - **Impact / risk**:
     - this is the discriminator between “fixture was wrong” and “OCR is still wrong”
     - if the corpus still fails after the trim, that is acceptable; the important outcome is an honest baseline
   - **Done looks like**:
     - fresh result files exist
     - the work log names the artifact paths and the new ratios

4. **Sync the truth surfaces and next-step recommendation** (`S`)
   - **Files**:
     - `docs/evals/registry.yaml`
     - `tests/fixtures/formats/_coverage-matrix.json`
     - `docs/stories/story-191-finish-real-handwritten-ocr-on-the-loc-fixture-pair.md`
   - **What changes**:
     - record the corrected-corpus rerun
     - reword the handwritten row and Story 191 blocker so future triage knows the Alverson benchmark is now front-page-faithful but still below quality bar
     - state clearly whether Story 191 should reopen as an OCR-only blocker or remain blocked for another reason
   - **Impact / risk**:
     - keeps methodology truth synchronized with the repaired corpus
     - highest risk is accidental overclaiming if the improved score is mistaken for a passing lane
   - **Done looks like**:
     - registry, coverage matrix, and Story 191 all tell the same post-trim story

### Structural Health Notes

- No pipeline schema change is expected; stay off `schemas.py` unless a stamped artifact changes shape unexpectedly.
- `docs/evals/registry.yaml` is already very large, so keep edits surgical.
- If the front-page trim fully resolves the benchmark mismatch but leaves Alverson still materially below `0.99`, do not widen scope in this story to chase OCR improvements. Hand the remaining problem back to Story 191 as an OCR-runtime question.
- If source review unexpectedly proves the checked-in front-page image is not the actual source used for the current transcript, stop and reclassify the story before touching goldens.

## Work Log

20260404-1822 — create-story: created Story 192 from `/triage` after confirming this is a new validation surface, not an honest reopen of Story 191. Evidence reviewed in this pass: `docs/methodology/state.yaml` and `docs/methodology/graph.json` show handwritten work still sits in the active intake-honesty campaign; Story 191's blocker evidence and `tests/fixtures/formats/_coverage-matrix.json` both show the current Alverson front-page fixture is misaligned with its transcript; `benchmarks/golden/handwritten-notes/corpus.json`, `testdata/README.md`, and the handwritten smoke tests prove the fixture/eval substrate already exists locally; the official LOC item `2023637835` remains the source of truth for the page scope. Result: a new `Pending` story is honest because the remaining work is fixture/golden repair plus eval rebaseline, not OCR runtime implementation. Next step: `/build-story` should audit the source, choose the smallest honest fixture repair, rerun the handwritten corpus, and then decide whether Story 191 should reopen.
20260404-1859 — build-story explore+plan: verified the story is honestly buildable on the fixture/eval seam with no missing runtime substrate. Additional evidence gathered in this pass: local inspection of `testdata/handwritten-notes-alverson-real-images/page-001.jpg` confirmed the checked-in image is a single front page at `(638, 1024)` and visibly ends at the same `...exceptable and` boundary where the current OCR output stops; the LOC item page for `2023637835` explicitly lists separate front/back originals (`LC-DIG-ppmsca-86651` / `LC-DIG-ppmsca-86652`) plus a transcript PDF; `benchmarks/scripts/run_handwritten_notes_eval.py` and the handwritten smoke tests already support a bounded single-fixture rerun without code changes. Fresh current-pass baseline probe via `python benchmarks/scripts/run_handwritten_notes_eval.py --transcript testdata/handwritten-notes-alverson-real.txt --images testdata/handwritten-notes-alverson-real-images --pdf testdata/handwritten-notes-alverson-real.pdf --fixture-id alverson-truth-probe --image-recipe configs/recipes/recipe-images-ocr-html-handwritten-notes-gemini-rescue.yaml --pdf-recipe configs/recipes/recipe-pdf-ocr-html-handwritten-notes-gemini-rescue.yaml --image-case-id image-handwritten-rescue --pdf-case-id pdf-handwritten-rescue --output /tmp/alverson-truth-probe.json` reproduced the current broken truth surface at `0.496975` image / `0.501513` pdf. A no-code trim experiment against those same fresh artifacts, using a temporary front-page-only transcript ending at `exceptable`, raised the scores to `0.678867` image / `0.685174` pdf while still leaving visible OCR errors like leading `nothing`, `Chickamauga`, `Cates novels`, and `excepatable`. Result: the smallest honest repair is a committed front-page transcript trim, not a widened front/back fixture pair, and the story should stay on the fixture/eval/docs seam. Next step: mark the story `In Progress`, implement the transcript/package repair, rerun the handwritten eval, and then sync the handwritten truth surfaces.
20260404-1936 — truth-surface implementation: trimmed `testdata/handwritten-notes-alverson-real.txt` to the exact visible front-page boundary ending at `exceptable and`, updated `testdata/README.md` to document the repo-owned scope as the LOC front page only, and added `test_alverson_real_transcript_matches_front_page_scope` in `tests/test_handwritten_notes_eval.py` so the transcript cannot silently widen again. I also rechecked `benchmarks/golden/handwritten-notes/corpus.json`, `tests/test_image_directory_intake_recipe.py`, and `tests/test_pdf_intake_recipe.py`; they already remained honest because the fixture and wrapper stayed one page. Narrow validation in the same pass: `python -m pytest tests/test_handwritten_notes_eval.py -q` passed (`9 passed`) and `python -m ruff check tests/test_handwritten_notes_eval.py` passed. Result: the checked-in Alverson package is now source-faithful on the repo-owned front-page scope. Next step: rerun the handwritten eval and inspect the fresh real-fixture artifacts.
20260404-1953 — corrected-corpus reruns + artifact inspection: first reran the single-fixture probe via `python benchmarks/scripts/run_handwritten_notes_eval.py --transcript testdata/handwritten-notes-alverson-real.txt --images testdata/handwritten-notes-alverson-real-images --pdf testdata/handwritten-notes-alverson-real.pdf --fixture-id alverson-truth-frontpage --image-recipe configs/recipes/recipe-images-ocr-html-handwritten-notes-gemini-rescue.yaml --pdf-recipe configs/recipes/recipe-pdf-ocr-html-handwritten-notes-gemini-rescue.yaml --image-case-id image-handwritten-rescue --pdf-case-id pdf-handwritten-rescue --output /tmp/alverson-truth-frontpage.json`, which confirmed the corrected one-page fixture still fails at `overall_min_ratio = 0.677267` / `page_min_ratio = 0.677267`. Then reran the full maintained handwritten corpus via `python benchmarks/scripts/run_handwritten_notes_eval.py --image-recipe configs/recipes/recipe-images-ocr-html-handwritten-notes-gemini-rescue.yaml --pdf-recipe configs/recipes/recipe-pdf-ocr-html-handwritten-notes-gemini-rescue.yaml --image-case-id image-handwritten-rescue --pdf-case-id pdf-handwritten-rescue --output benchmarks/results/handwritten-notes-story192-alverson-frontpage.json`, which wrote `benchmarks/results/handwritten-notes-story192-alverson-frontpage.json` with `pass_rate = 0.6`, `overall_min_ratio = 0.677267`, `page_min_ratio = 0.677267`, `cases_total = 10`, and `fixtures_passing = 3`. Manual artifact inspection showed the remaining failures are now OCR-only on the visible source: Barney image/PDF artifacts at `output/runs/handwritten-handwritten-notes-barney-real-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl` and `output/runs/handwritten-handwritten-notes-barney-real-pdf-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl` score `0.908567` / `0.886568` and still drift on names; corrected-scope Alverson image/PDF artifacts at `output/runs/handwritten-handwritten-notes-alverson-real-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl` and `output/runs/handwritten-handwritten-notes-alverson-real-pdf-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl` score `0.677267` / `0.681952` and still misread visible text with `nothing`, `Battle of Chickamauga`, `lates novels`, and `excepatable`. Result: the prior `0.499136` floor was partially golden-wrong, but the corrected corpus still stays below bar because OCR quality is not good enough.
20260404-2028 — truth-surface sync + repo validation: updated `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, and `docs/stories/story-191-finish-real-handwritten-ocr-on-the-loc-fixture-pair.md` so future triage sees the remaining handwritten blocker as OCR-only on the corrected corpus rather than a live source/transcript mismatch. The eval registry now records Story 192 as a **test-wrong / golden-wrong** correction that raised the floor from `0.499136` to `0.677267` without runtime changes. Repo validation in this pass: `make test` passed (`463 passed`), `make lint` passed, and `git diff --check` passed. Next step: regenerate the compiled methodology surfaces, mark the build gate, and hand the story off for `/validate` rather than reopening OCR runtime work speculatively.
20260404-2042 — methodology finalize + handoff: reran `make methodology-compile` until the generated surfaces stabilized, then verified them with `make methodology-check`. Result: `docs/methodology/graph.json` and `docs/stories.md` now include Story 192 and carry the corrected handwritten blocker state from Story 191 and the coverage matrix. This story remains `In Progress` with `Build complete` checked and the validation / done gates intentionally left open. Next step: use `/validate` if a separate validation pass is wanted before `/mark-story-done`.
20260404-2210 — /mark-story-done closeout: reran the full close-out validation in this pass and closed the story. Fresh evidence rechecked now: `git diff` still matches the intended Story 192 scope; the corrected transcript at `testdata/handwritten-notes-alverson-real.txt` still stops at the visible front-page boundary; `benchmarks/results/handwritten-notes-story192-alverson-frontpage.json` still records the corrected corpus floor at `0.677267`; manual artifact reads on the Barney and Alverson maintained-rescue outputs still show the remaining blocker is OCR quality, not source/transcript mismatch. Validation rerun in this closeout pass: `make test` passed (`463 passed`), `make lint` passed, and `make methodology-check` passed. Result: Story 192 is now `Done`; the implementation surface is complete and only git landing remains. Next step: `/check-in-diff`.
