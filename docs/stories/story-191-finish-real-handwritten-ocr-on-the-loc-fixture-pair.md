---
title: "Finish Real Handwritten OCR on the LOC Fixture Pair"
status: "Blocked"
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
  - "189"
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

# Story 191 — Finish Real Handwritten OCR on the LOC Fixture Pair

**Priority**: High
**Status**: Blocked
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/runbooks/golden-build.md`, `docs/stories/story-179-repo-owned-handwritten-notes-fixture-and-baseline-transcription.md`, `docs/stories/story-182-widen-handwritten-notes-fixture-breadth.md`, `docs/stories/story-185-widen-handwritten-proof-beyond-synthetic-pair.md`, `docs/stories/story-186-real-handwritten-fixture-proof-surface.md`, `docs/stories/story-189-improve-real-handwritten-barney-fidelity.md`, `docs/stories/story-190-fix-story-progression-and-anti-fragmentation-workflow.md`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower handwritten full-page rescue ADR or runbook
**Depends On**: Story 189

## Goal

Story 189 closed the evidence line honestly: the handwritten family now has two repo-owned real LOC fixtures, and the current bounded Gemini rescue seam still fails both of them. Story 192 then corrected the Alverson fixture to an honest front-page-only truth surface and reran the maintained corpus; Barney still remains wrong on names and phrasing, and corrected-scope Alverson still remains wrong on visible-page OCR fidelity. This story is therefore the blocked OCR-runtime line: land one generic maintained OCR/escalation path that can read both real LOC fixtures on both image-directory and PDF entry while preserving the synthetic fixtures, or stay blocked until a materially stronger OCR substrate exists instead of spawning another same-surface follow-up.

## Acceptance Criteria

- [ ] A fresh current-tip baseline exists for the full five-fixture handwritten corpus (`3` synthetic + `2` real) using the current maintained handwritten recipe surface, and the work log names the exact artifact paths inspected for Barney drift and corrected-scope Alverson front-page OCR failure rather than only aggregate ratios.
- [ ] The story measures at least one generic full-page handwritten recovery candidate beyond the current rescue seam on both real fixtures and the synthetic regression set. Compared candidates must use the existing handwritten scorer/eval surface, and the work log must name the exact artifact paths, ratios, and dominant failure modes.
- [ ] If a winning maintained path exists, the maintained handwritten image-directory and PDF recipes (or their honest successor recipes) clear `overall_min_ratio >= 0.99`, `page_min_ratio >= 0.99`, and `pass_rate = 1.0` on the five-fixture corpus, with fresh `driver.py` proofs under `output/runs/` and manual artifact inspection confirming that Barney and corrected-scope Alverson both preserve their visible source content faithfully.
- [ ] If no candidate clears that bar, this story must not close `Done`; it must close `Blocked` with a named blocker, explicit blocker evidence, and an unblock condition, and the handwritten truth surfaces must remain at `has-fixture` without creating another same-surface handwriting story.

## Out of Scope

- Adding more handwritten fixtures without changing the maintained runtime behavior
- Barney-specific or Alverson-specific deterministic text replacements, patches, or transcript cleanup
- Broad archive-scale cursive support beyond the current bounded LOC fixture pair
- Changes to the `doc-web` / Dossier runtime boundary in ADR-002
- Manual artifact edits that hide OCR failure instead of fixing the pipeline

## Approach Evaluation

- **Simplification baseline**: already tested and still negative after the truth-surface repair. Story 192 corrected the Alverson transcript to the visible front-page boundary and reran the maintained rescue seam at `pass_rate = 0.6` / `overall_min_ratio = 0.677267`; Barney still stayed below bar and corrected-scope Alverson still failed materially. Historical direct `gpt-5` / `claude-opus-4-6` probes from Story 191 did not reveal a winner before that correction, so the next honest move is not another paperwork story; it is a materially stronger OCR substrate or continued blockage.
- **AI-only**: still worth checking only if there is genuinely new model evidence. Current repo evidence says a single full-page direct call is not enough for the LOC pair, especially for the corrected Alverson front page and the dense Barney spread.
- **Hybrid**: current leading candidate. The likely winning shape is a generic full-page handwritten rescue loop such as full-page OCR plus coverage/truncation detection plus targeted page-window or vertical-slice re-read with overlap merge and validation. This stays AI-first while using code only for orchestration, segmentation, merge discipline, and proof.
- **Pure code**: only appropriate for manifest slicing, overlap merge, coverage/truncation detection, provenance-safe stitching, and driver/recipe plumbing. It is not appropriate for word correction or handwritten normalization.
- **Repo constraints / prior decisions**: `spec:1.1` keeps recipe ownership explicit, `spec:2.1` and `spec:2.2` keep OCR evidence-driven and cost-aware, Story 190 requires one final same-surface story instead of serial micro follow-ups, and Story 189 already recorded negative evidence for the current low-risk direct-model and upscaling probes. No narrower local ADR settles the full-page handwritten rescue design.
- **Existing patterns to reuse**: `modules/extract/ocr_ai_gpt51_v1/main.py` for provider invocation and page-level HTML output; `benchmarks/scripts/run_handwritten_notes_eval.py` and `benchmarks/scorers/handwritten_notes_transcription.py` for repeatable corpus scoring; `modules/extract/split_pages_from_manifest_v1/main.py` as an example of page-image manifest rewriting, even though it currently only solves left/right spread splitting; `modules/common/onward_openai_ocr.py` as the existing pattern for OpenAI parameter compatibility.
- **Eval**: `handwritten-notes-transcription` is the primary decision surface. Success is `pass_rate = 1.0` and both `overall_min_ratio` / `page_min_ratio` at `>= 0.99` on the five-fixture corpus, plus manual inspection of the real-fixture `page_html_v1` artifacts showing faithful corrected-front-page recovery on Alverson and no semantic drift regression on Barney.

## Tasks

- [x] Re-freeze the five-fixture handwritten baseline on the current tip and inspect the exact Barney / Alverson failure artifacts before changing code
- [ ] Measure the smallest honest generic full-page recovery candidate set before landing new logic:
  - [ ] at least one candidate must target the corrected Alverson front-page OCR fidelity failure directly
  - [ ] every candidate must be measured on both real fixtures and checked for regression against the three synthetic fixtures
- [ ] Land the smallest maintained implementation that wins:
  - [ ] prefer a generic page-window / coverage-aware rescue seam or sibling helper over document-specific branching
  - [ ] keep provenance and final artifact shape unchanged unless a schema change is explicitly justified
  - [ ] do not hardcode Barney or Alverson strings
- [ ] Add or extend tests for the chosen seam, including recipe wiring plus any new segmentation / merge / coverage logic
- [ ] Clear stale `*.pyc`, run through `driver.py` on both real fixtures for both image-directory and PDF entry, verify artifacts in `output/runs/`, and manually inspect the repaired real-fixture content
- [ ] If the maintained path now changes handwritten graduation truth: update `tests/fixtures/formats/_coverage-matrix.json`, `docs/evals/registry.yaml`, and any relevant methodology state honestly
- [x] If the story cannot clear the required bar, convert it to `Blocked` with blocker summary, blocker evidence, and unblock condition instead of closing it as another negative `Done`
- [ ] Check whether the chosen implementation makes the current handwritten hint-only rescue recipe or any temporary comparison paths redundant; remove them or create a concrete follow-up
- [ ] Run required checks for touched scope:
  - [ ] Default Python checks: `make test`
  - [ ] Default Python lint: `make lint`
  - [ ] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [ ] If agent tooling changed: `make skills-check`
- [ ] If evals or goldens changed: run `/improve-eval` and update `docs/evals/registry.yaml`
- [ ] Search all docs and update any related to what we touched
- [ ] Verify Central Tenets:
  - [ ] T0 — Traceability: every support claim traces to named fixtures, run IDs, models, and inspected artifacts
  - [ ] T1 — AI-First: code only orchestrates segmentation / retries / merge; no deterministic handwriting correction logic
  - [ ] T2 — Eval Before Build: candidate paths are measured on the five-fixture corpus before the runtime is changed
  - [ ] T3 — Fidelity: the corrected real-fixture source content is recovered faithfully with no silent omission or normalization
  - [ ] T4 — Modular: the winning solution is a bounded generic handwritten seam, not document-specific code
  - [ ] T5 — Inspect Artifacts: Barney and Alverson artifacts are manually opened and checked, not just scored

## Workflow Gates

- [ ] Build complete: implementation finished, required checks run, and summary shared
- [ ] Validation complete or explicitly skipped by user
- [ ] Story marked done via `/mark-story-done`

## Blocker Summary

After Story 192 corrected the Alverson transcript to the visible front-page boundary, the current checked-in LOC handwritten proof pair still cannot honestly clear the `0.99` handwritten bar in this repo state because the maintained rescue seam remains below bar on both real fixtures and no fresher stronger OCR substrate has been verified on the corrected corpus.

## Blocker Evidence

- Story 192 corrected the Alverson transcript to the exact visible front-page boundary and reran the maintained handwritten corpus, writing `benchmarks/results/handwritten-notes-story192-alverson-frontpage.json` with `pass_rate = 0.6`, `overall_min_ratio = 0.677267`, and `page_min_ratio = 0.677267`. The six synthetic rescue cases still passed at `1.0`, but the real fixtures stayed below bar: Barney scored `0.908567` on image entry and `0.886568` on PDF entry, while corrected-scope Alverson scored `0.677267` on image entry and `0.681952` on PDF entry.
- Manual artifact inspection on that corrected rerun confirmed the remaining issue is OCR quality on visible source content, not hidden continuation text. Alverson artifacts at `output/runs/handwritten-handwritten-notes-alverson-real-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl` and `output/runs/handwritten-handwritten-notes-alverson-real-pdf-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl` still misread the visible front page with errors such as leading `nothing`, `Battle of Chickamauga`, `lates novels`, and `excepatable`. Barney artifacts at `output/runs/handwritten-handwritten-notes-barney-real-image-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl` and `output/runs/handwritten-handwritten-notes-barney-real-pdf-handwritten-rescue/02_ocr_ai_gpt51_v1/pages_html.jsonl` still drift on names and phrases such as `Harlen`, `genesee`, and `father has had gone`.
- Story 191's fresh direct `gpt-5` / `claude-opus-4-6` probes remain only historical negative evidence because they were measured before Story 192 corrected the Alverson transcript surface. They did not produce a winning OCR substrate then, and no newer corrected-corpus stronger-model winner has been verified since. That keeps this story blocked on missing OCR capability rather than on missing paperwork.
- 2026-04-05 bounded `/improve-eval handwritten-notes-transcription` rechecked the retry gate after verifying current model availability with `python scripts/discover-models.py --check-new`. Fresh maintained rescue reruns under `benchmarks/results/handwritten-notes-improve-eval-20260405-barney-baseline.json` and `benchmarks/results/handwritten-notes-improve-eval-20260405-alverson-baseline.json` reproduced the current blocker instead of revealing silent drift: Barney stayed at `0.883604` image / `0.756036` pdf, and corrected-scope Alverson stayed at `0.677267` image / `0.681952` pdf. The fresh image-only subject-model screen at `benchmarks/results/handwritten-notes-improve-eval-20260405-image-screen.json` also failed to produce a winner. `gpt-5.4-pro` wrote empty `page_html_v1` artifacts at `output/runs/eval-barney-image-gpt-5-4-pro/01_ocr_ai_gpt51_v1/pages_html.jsonl` and `output/runs/eval-alverson-image-gpt-5-4-pro/01_ocr_ai_gpt51_v1/pages_html.jsonl` (`overall_ratio = 0.0` both), which is current integration/pipeline-wrong evidence rather than a usable OCR result. `gemini-3.1-pro-preview` improved Barney only to `0.843434` at `output/runs/eval-barney-image-gemini-3-1-pro-preview/01_ocr_ai_gpt51_v1/pages_html.jsonl` and left corrected-scope Alverson at `0.262102` at `output/runs/eval-alverson-image-gemini-3-1-pro-preview/01_ocr_ai_gpt51_v1/pages_html.jsonl`, still with the same visible-source failure class. No fresh candidate materially beat both corrected real fixtures, so this story remains blocked and should not reopen yet.

## Unblock Condition

Unblock this story only when a materially different OCR substrate or maintained recovery seam is ready to be tested against the corrected corpus and it produces fresh current-pass `driver.py` / eval artifacts that bring Barney and the corrected Alverson front-page fixture to `overall_min_ratio >= 0.99`, `page_min_ratio >= 0.99`, and `pass_rate = 1.0`. If a future story intentionally widens Alverson to the full two-page letter, that fixture-scope work must happen first and be rebaselined separately before it can count as OCR evidence here.

## Architectural Fit

- **Owning module / area**: the OCR extraction / rescue seam around `ocr_ai_gpt51_v1`, the maintained handwritten rescue recipes, and any new generic segmentation or coverage-aware merge helper needed to recover full-page archival handwriting.
- **Methodology reality**: this belongs to `spec:1`, `spec:2`, and `spec:8`. Current substrate is `exists` for all three categories in `docs/methodology/state.yaml`, with `C1`, `C2`, and `B5` still active. The relevant coverage row is `handwritten-notes`, which is still `has-fixture` after the corrected five-fixture corpus still fell to `pass_rate = 0.6` with a `0.677267` floor.
- **Substrate evidence**: verified in repo that `modules/extract/ocr_ai_gpt51_v1/main.py` already provides page-level OCR, `benchmarks/scripts/run_handwritten_notes_eval.py` already supports both corpus and single-fixture mode, `benchmarks/scorers/handwritten_notes_transcription.py` scores the exact handwritten artifact we care about, the LOC Barney and Alverson fixtures are checked in, and smoke/test coverage exists for the handwritten image/PDF entry paths. Important gap verified in code: there is no existing generic vertical page-window OCR or overlap-merge module for full-page handwritten recovery; `modules/extract/split_pages_from_manifest_v1/main.py` only handles left/right spread splitting. That means the story is buildable, but if the winning path is page-window segmentation, it will likely need a new helper rather than just a prompt tweak.
- **Data contracts / schemas**: prefer to keep the final runtime artifacts on existing `page_image_v1` / `page_html_v1`. If the winning path needs an intermediate segmentation or merge artifact that crosses stage boundaries, add or reuse a schema explicitly instead of smuggling fields into stamped output.
- **File sizes**: likely owner files are `modules/extract/ocr_ai_gpt51_v1/main.py` (758 lines), `benchmarks/scripts/run_handwritten_notes_eval.py` (330), `benchmarks/scorers/handwritten_notes_transcription.py` (119), `tests/test_handwritten_notes_eval.py` (170), `tests/test_image_directory_intake_recipe.py` (276), `tests/test_pdf_intake_recipe.py` (197), `tests/fixtures/formats/_coverage-matrix.json` (464), `docs/evals/registry.yaml` (1405), `configs/recipes/recipe-images-ocr-html-handwritten-notes-gemini-rescue.yaml` (91), `configs/recipes/recipe-pdf-ocr-html-handwritten-notes-gemini-rescue.yaml` (92), `modules/extract/split_pages_from_manifest_v1/main.py` (319), and `modules/extract/split_pages_from_manifest_v1/module.yaml` (11). `ocr_ai_gpt51_v1/main.py` and `docs/evals/registry.yaml` are already over 500 lines, so keep edits especially surgical there.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/runbooks/golden-build.md`, Stories 186/189/190, `docs/evals/registry.yaml`, and `tests/fixtures/formats/_coverage-matrix.json`. No narrower local ADR or runbook was found that already resolves the handwritten full-page recovery design.

## Files to Modify

- `modules/extract/ocr_ai_gpt51_v1/main.py` — add the smallest generic OCR orchestration hook needed if the winning path lives inside the shared OCR module (758 lines)
- `configs/recipes/recipe-images-ocr-html-handwritten-notes-gemini-rescue.yaml` — keep or replace the maintained handwritten image-entry rescue ownership honestly (91 lines)
- `configs/recipes/recipe-pdf-ocr-html-handwritten-notes-gemini-rescue.yaml` — keep or replace the maintained handwritten PDF-entry rescue ownership honestly (92 lines)
- `benchmarks/scripts/run_handwritten_notes_eval.py` — capture any extra result metadata needed to compare full-page rescue candidates honestly (330 lines)
- `benchmarks/scorers/handwritten_notes_transcription.py` — extend failure reporting only if the current scorer is insufficient to distinguish truncation / merge outcomes (119 lines)
- `tests/test_handwritten_notes_eval.py` — keep the handwritten corpus/eval helper repeatable (170 lines)
- `tests/test_image_directory_intake_recipe.py` — preserve image-entry handwritten smoke coverage if recipe behavior changes (276 lines)
- `tests/test_pdf_intake_recipe.py` — preserve PDF-entry handwritten smoke coverage if recipe behavior changes (197 lines)
- `docs/evals/registry.yaml` — record the final handwritten-arc outcome honestly (1405 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — move the handwritten row only as far as fresh evidence justifies (464 lines)
- `docs/stories/story-191-finish-real-handwritten-ocr-on-the-loc-fixture-pair.md` — keep the implementation/work-log record current (this file)
- Likely new helper under `modules/extract/` or `modules/adapter/` for generic page-window segmentation / overlap merge if the hybrid path wins (new file)

## Redundancy / Removal Targets

- The current handwritten hint-only rescue recipe pair if a more structured generic full-page rescue path supersedes them
- Any temporary comparison-only wiring or probe-specific helper logic that would remain after the maintained path is chosen

## Notes

- New story justification: Story 189 already closed the evidence/truth-surface line honestly. This new work is a materially different implementation seam aimed at either making the handwritten family pass or blocking it explicitly; folding it back into Story 189 would blur validated history.
- This should be the final handwriting-arc story unless the work proves to cross a genuinely different runtime boundary or reveals a blocker that belongs in an ADR rather than in a story.

## Plan

This section is intentionally no longer an active implementation plan.

The earlier `/build-story` recommendation to add a bounded handwritten recovery
helper was superseded by the blocker closeout and the later bounded
`/improve-eval` retry. The current authoritative guidance for triage is the
blocker record above:

- this story remains `Blocked`
- it should not reopen on the same evidence again
- it only becomes actionable when the `Unblock Condition` is met in a fresh pass

If future exploration finds a materially different OCR substrate or recovery
seam, reopen from the `Unblock Condition`, not from the stale pre-block
implementation sketch that used to live here.

### Scope Adjustment From Exploration

- **Folded in automatically**: the story should explicitly prefer a helper inside `ocr_ai_gpt51_v1` over a brand-new stage/module on the first pass. That keeps the runtime slice coherent and avoids an unnecessary new schema boundary.
- **Not recommended**: reviving `modules/extract/extract_ocr_ensemble_v1` or introducing a new intermediate manifest/schema before the bounded helper is attempted. Exploration found legacy overlap/alignment utilities there, but the ensemble path is materially broader than Story 191's needs and would make validation noisier.
- **Approval-sensitive expansion**: if the bounded helper cannot make the recovery inspectable enough without carrying extra per-window data across stage boundaries, the work may need a new intermediate schema/stage. That is the only currently visible structural expansion that should trigger a second user check before continuing.

## Work Log

20260404-1704 — story creation: created one final handwritten-arc story after verifying that a new ID is honest. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, `docs/runbooks/golden-build.md`, Stories 186/189/190, `docs/evals/registry.yaml`, and `tests/fixtures/formats/_coverage-matrix.json`. Result: Story 189 already closed the current evidence surface truthfully, but the remaining work is a materially different runtime attempt to make the maintained handwritten path pass across both real LOC fixtures. The story is honestly `Pending`, not `Draft`, because the OCR/eval/fixture substrate exists in code today; the only missing piece is the generic full-page handwritten rescue implementation. Next step: `/build-story` should freeze the five-fixture baseline, compare the smallest honest candidate set, and either land a passing maintained path or convert this story to `Blocked` with explicit blocker metadata.
20260404-1715 — /build-story explore+plan: verified Story 191 remains honestly buildable, but the missing substrate is still real. Files traced in this pass: `modules/extract/ocr_ai_gpt51_v1/main.py`, `modules/extract/ocr_ai_gpt51_v1/module.yaml`, `configs/recipes/recipe-images-ocr-html-handwritten-notes-gemini-rescue.yaml`, `configs/recipes/recipe-pdf-ocr-html-handwritten-notes-gemini-rescue.yaml`, `benchmarks/scripts/run_handwritten_notes_eval.py`, `benchmarks/scorers/handwritten_notes_transcription.py`, `schemas.py`, `tests/test_handwritten_notes_eval.py`, `tests/test_image_directory_intake_recipe.py`, and `tests/test_pdf_intake_recipe.py`. ADR / decision context rechecked: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, and `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`; no narrower handwritten full-page rescue ADR or runbook was found. Relevant methodology surface confirmed from current compiled truth: `spec:1`, `spec:2`, and `spec:8` all show substrate `exists`; the handwritten coverage row in `tests/fixtures/formats/_coverage-matrix.json` is still `has-fixture`; the maintained handwritten eval command in `docs/evals/registry.yaml` still points at the Gemini rescue recipes. Fresh baseline evidence: `python benchmarks/scripts/run_handwritten_notes_eval.py --image-recipe configs/recipes/recipe-images-ocr-html-handwritten-notes-gemini-rescue.yaml --pdf-recipe configs/recipes/recipe-pdf-ocr-html-handwritten-notes-gemini-rescue.yaml --image-case-id image-handwritten-rescue --pdf-case-id pdf-handwritten-rescue --output benchmarks/results/handwritten-notes-story191-baseline-20260404.json` completed on current tip with `pass_rate = 0.6`, `overall_min_ratio = 0.499136`, and `page_min_ratio = 0.499136`. Manual artifact inspection in the same pass confirmed that the synthetic fixtures still hold at `1.0`, while the real fixtures still fail: Barney image/PDF artifacts under `output/runs/handwritten-handwritten-notes-barney-real-*/02_ocr_ai_gpt51_v1/pages_html.jsonl` now score `0.895587` / `0.756036` and still drift on names/phrasing; Alverson image/PDF artifacts under `output/runs/handwritten-handwritten-notes-alverson-real-*/02_ocr_ai_gpt51_v1/pages_html.jsonl` now score `0.499136` / `0.500647` and still truncate at `...acceptable and`, omitting the lower body, signature, and postscript. Critical substrate verified versus missing: the page-level OCR stage, scorer, eval harness, recipes, schemas, and both LOC fixtures all exist and are usable now; there is still no existing generic vertical/page-window handwritten rescue or overlap-merge helper in the maintained runtime. Patterns to follow: keep the final contract on `page_html_v1`, keep the rescue recipe-gated per `spec:1.1`, and isolate any new recovery logic in a helper rather than further bloating `main.py`. Files at risk if implementation proceeds: `modules/extract/ocr_ai_gpt51_v1/main.py` because it is already large, `schemas.py` if the work tries to smuggle new output fields across stamping boundaries, and the handwritten recipe smoke tests because they encode current stage/module ownership. Potential redundancy/removal target: the current hint-only handwritten rescue path should be replaced cleanly if a structured opt-in recovery seam wins; the legacy `extract_ocr_ensemble_v1` path should not be revived for this story unless the bounded helper clearly fails. Surprises: the first baseline rerun failed on a transient Gemini TLS decode error for `handwritten-notes-rough` page 2 before scoring; the second rerun succeeded unchanged. Another surprise from code exploration: the current OCR metadata self-report is not a reliable completeness gate, because Alverson can report high integrity while still missing roughly forty percent of the transcript. Next step: wait for user approval on the bounded helper plan before any implementation code.
20260404-1718 — implementation start: user approved the bounded-helper plan, so Story 191 moved to `In Progress` under `/build-story`. Immediate next steps in this pass were to regenerate the compiled methodology surfaces so the story index matched the live status, then run one last no-code direct-call candidate on the real LOC pair before changing the OCR runtime. Guardrail carried forward: do not expand to a new staged schema unless the bounded in-module handwritten recovery path proves insufficient.
20260404-1818 — blocked after current-pass candidate sweep: fresh no-code and bounded local rescue probes did not reveal an honest maintained path to `0.99`, and source review exposed a truth-surface blocker on Alverson. Evidence recorded in this pass: fresh maintained baseline `benchmarks/results/handwritten-notes-story191-baseline-20260404.json` stayed at `pass_rate = 0.6`, `overall_min_ratio = 0.499136`, `page_min_ratio = 0.499136`; direct `gpt-5` image/PDF probes under `output/runs/story191-*-gpt5-direct/02_ocr_ai_gpt51_v1/pages_html.jsonl` stayed materially worse than the maintained rescue seam (`0.192010`, `0.010297`, `0.221929`, `0.362143`); direct `claude-opus-4-6` image probes under `output/runs/story191-barney-image-claude-direct/02_ocr_ai_gpt51_v1/pages_html.jsonl` and `output/runs/story191-alverson-image-claude-direct/02_ocr_ai_gpt51_v1/pages_html.jsonl` only reached `0.725708` and `0.193325`. I also ran one-off local cropped-window and contrast/upscale probes to test the proposed bounded helper direction before touching runtime code; they did not recover the Alverson continuation or produce a convincing Barney win, so I am not landing speculative OCR glue. Most important new finding: the checked-in Alverson source image `testdata/handwritten-notes-alverson-real-images/page-001.jpg` visibly ends at the same `...exceptable and` boundary where OCR stops, and it matches the LOC front-page large JPEG size (`638x1024`) while the source record exposes separate `Front` and `Back` images. That makes the current Alverson transcript/fixture pairing at least partially misaligned to the visible source, so the story is now honestly `Blocked` rather than “one more OCR tweak away.” Next step: keep the handwritten family honest, update the generated graph/index and related truth surfaces, and stop instead of landing a misleading partial runtime patch.
20260404-1826 — blocked closeout + truth-surface sync: updated the handwritten truth surfaces instead of landing runtime code. Changes in this pass: `docs/evals/registry.yaml` now records the fresh Story 191 maintained baseline (`0.499136 / 0.499136 / 0.6`) plus the blocked direct `gpt-5` / `claude-opus-4-6` comparison attempt; `tests/fixtures/formats/_coverage-matrix.json` now records the fresh Barney ratios and the Alverson source/transcript blocker explicitly; `testdata/README.md` now stops claiming that `handwritten-notes-alverson-real.txt` is a clean front-page transcript aligned to the visible page. Regenerated `docs/methodology/graph.json` and `docs/stories.md`, which now show Story 191 as `Blocked`. Narrow validation in the same pass: `make methodology-check` passed and `git diff --check` passed. No runtime/module code was changed because the blocker evidence removed the case for speculative implementation.
20260404-2018 — Story 192 follow-up reclassified the blocker surface: after Story 192 trimmed `testdata/handwritten-notes-alverson-real.txt` to the visible front-page boundary and reran `benchmarks/results/handwritten-notes-story192-alverson-frontpage.json`, the handwritten floor rose from `0.499136` to `0.677267` without any OCR runtime change. Updated this blocked story so it no longer claims a live source/transcript mismatch inside the checked-in Alverson fixture. Fresh evidence now points at OCR-only remaining failures on the corrected corpus: Barney still scores `0.908567` / `0.886568`, corrected-scope Alverson still scores `0.677267` / `0.681952`, and manual artifact inspection shows visible-page OCR errors rather than hidden continuation text. Next step: keep this story blocked until a materially stronger OCR substrate is ready to rerun against the corrected corpus.
20260405-0349 — bounded `/improve-eval handwritten-notes-transcription` retry-ready subject-model screen completed and did not justify reopening the story. First, I verified current provider availability with `python scripts/discover-models.py --check-new`, which confirmed fresh callable candidates including `gpt-5.4-pro` and Gemini 3.x in this checkout. I then re-ran the maintained handwritten rescue baseline on the corrected real pair: `benchmarks/results/handwritten-notes-improve-eval-20260405-barney-baseline.json` reproduced Barney at `0.883604` image / `0.756036` pdf, and `benchmarks/results/handwritten-notes-improve-eval-20260405-alverson-baseline.json` reproduced corrected-scope Alverson at `0.677267` image / `0.681952` pdf. With that baseline re-verified, I screened the fresh image-entry candidates under `benchmarks/results/handwritten-notes-improve-eval-20260405-image-screen.json`. `gpt-5.4-pro` returned empty `page_html_v1` artifacts on both fixtures (`overall_ratio = 0.0` at `output/runs/eval-barney-image-gpt-5-4-pro/01_ocr_ai_gpt51_v1/pages_html.jsonl` and `output/runs/eval-alverson-image-gpt-5-4-pro/01_ocr_ai_gpt51_v1/pages_html.jsonl`), which is current integration/pipeline-wrong evidence rather than a usable OCR win. `gemini-3.1-pro-preview` improved Barney only to `0.843434` at `output/runs/eval-barney-image-gemini-3-1-pro-preview/01_ocr_ai_gpt51_v1/pages_html.jsonl` and left corrected-scope Alverson at `0.262102` at `output/runs/eval-alverson-image-gemini-3-1-pro-preview/01_ocr_ai_gpt51_v1/pages_html.jsonl`, still with visible-source misreads such as the spurious leading `nothing` / `Battle of Chickamauga` pattern. Because no fresh subject model materially beat both corrected real fixtures, I did not promote any candidate to a PDF-entry or full five-fixture rerun, and Story 191 remains honestly `Blocked`.
20260404-2238 — stale-plan cleanup: removed the pre-block implementation plan from this story after it started biasing `/triage` back toward handwriting even though the current blocker evidence and unblock condition say the line should stay parked. Result: the story now carries one consistent instruction surface for future triage passes. Next step: keep the line as a health flag only until a fresh pass can honestly satisfy the unblock condition.
