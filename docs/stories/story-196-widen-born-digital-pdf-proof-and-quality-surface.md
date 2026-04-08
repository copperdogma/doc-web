---
title: "Widen Born-Digital PDF Proof and Add a Maintained Quality Surface"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #1 (Ingest), Requirement #3 (Extract), Requirement #6 (Validate), Requirement #7 (Export), Zero configuration, Any format, any condition, Dossier-ready output, Traceability is the product"
spec_refs:
  - "spec:1"
  - "spec:1.1"
  - "spec:3"
  - "spec:3.1"
  - "spec:6"
  - "spec:7"
  - "spec:8"
adr_refs: []
depends_on:
  - "168"
  - "171"
  - "177"
category_refs:
  - "spec:1"
  - "spec:3"
  - "spec:6"
  - "spec:7"
  - "spec:8"
compromise_refs:
  - "C2"
  - "C3"
  - "B1"
input_coverage_refs:
  - "born-digital-pdf"
architecture_domains:
  - "doc_web_runtime"
roadmap_tags:
  - "campaign:maintained-intake-honesty"
legacy_system: ""
---

# Story 196 — Widen Born-Digital PDF Proof and Add a Maintained Quality Surface

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/stories/story-168-marker-lite-maintained-born-digital-pdf-path.md`, `docs/stories/story-170-born-digital-pdf-native-text-widening-and-routing-decision.md`, `docs/stories/story-171-maintained-non-toc-born-digital-pdf-lane.md`, `docs/stories/story-177-born-digital-flat-proof-and-heading-cleanup.md`, `docs/stories/story-178-corpus-wide-approved-intake-handoff-benchmark.md`, `docs/stories/story-180-widen-approved-intake-handoff-image-directory-proof.md`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/RUNBOOK.md`, `docs/scout/scout-011-external-document-ingestion-systems.md` (historical context only), and `None found after search in docs/decisions/ for a narrower born-digital proof-widening or quality-harness ADR, or in docs/runbooks/ and docs/notes/ for a dedicated born-digital quality-harness workflow beyond the smoke commands in docs/RUNBOOK.md`
**Depends On**: Story 168, Story 171, Story 177

## Goal

Turn the `born-digital-pdf` coverage row into one honest maintained claim instead of a pile of bounded proofs. The repo already has a maintained book-like Marker-lite lane, a maintained flat/non-TOC lane, intake routing that distinguishes them, and approved-handoff evidence that can launch them, but the row in `tests/fixtures/formats/_coverage-matrix.json` still sits at `has-fixture` because the proof surface is thin and there is no dedicated repeatable quality/comparison harness for this family. This story widens the repo-owned proof surface across both maintained lanes, adds the smallest honest quality/comparison surface, and then uses fresh `driver.py` evidence to either promote `born-digital-pdf` to bounded `passing` or keep it narrower with an explicit, inspectable boundary.

## Acceptance Criteria

- [x] The maintained born-digital proof surface is widened across both current lanes from actual repo evidence:
  - [x] the story audits the existing repo-owned fixtures (`tbotb-mini`, `flat-born-digital-mini`, `flat-born-digital-form-mini`) and any licensed local comparison PDFs already referenced in the coverage row
  - [x] at least one additional repo-owned or reproducibly generated book-like born-digital PDF fixture is added, or the story records concrete current-pass evidence for why the family must remain narrower than `passing`
  - [x] every fixture reviewed by the story is classified as `supported`, `comparison-only`, `bounded unsupported`, or `out of scope`
- [x] Fresh `driver.py` proof exists for every fixture claimed inside the maintained born-digital slice:
  - [x] the correct maintained recipe is used per fixture (`recipe-born-digital-pdf-marker-lite-html-mvp.yaml` for book-like, `recipe-born-digital-pdf-non-toc-html-mvp.yaml` for flat/non-TOC)
  - [x] inspected artifacts are recorded for `pages_html.jsonl`, portion output, `output/html/manifest.json`, `output/html/provenance/blocks.jsonl`, and representative final HTML files
  - [x] the work log records whether any OCR-baseline comparison is still needed for honesty on the widened slice, and if so cites exact artifact paths
- [x] A repeatable born-digital quality/comparison surface exists after the story:
  - [x] a checked-in corpus file plus harness or benchmark script can rerun the maintained born-digital comparison from this repo
  - [x] the first score or summary lands in `docs/evals/registry.yaml` with clear retry conditions
  - [x] focused test coverage exists so the harness/corpus cannot silently drift
- [x] Coverage, routing, and handoff truth stay aligned with the new evidence:
  - [x] `tests/fixtures/formats/_coverage-matrix.json` moves to bounded `passing` only if the widened proof surface earns it; otherwise it remains narrower with explicit notes about which lane or fixture class is still unproven
  - [x] if the widened proof changes what intake or approved handoff can honestly recommend, rerun the relevant surfaces and update `docs/evals/registry.yaml`
  - [x] `docs/RUNBOOK.md`, `README.md`, and any affected story/methodology surfaces describe the post-story born-digital boundary exactly, with no stale `has-fixture` or over-broad language

## Out of Scope

- Reopening the accepted `doc-web` boundary from ADR-002 or the negative broader external-system posture from Scout 011
- Replacing the explicit-recipe compromise in `spec:1.1` with hidden auto-launch or planner-only routing
- Claiming full graduation readiness for all born-digital PDFs, or expanding support to `docx`, `xlsx`, `pptx`, `epub`, email, or web-page inputs
- Rewriting the Marker runtime, Docker/bootstrap ownership model, or OCR default for all PDFs before the widened proof surface says such a change is honest
- Shipping broad semantic form extraction or Dossier-side normalization beyond the current `doc-web` bundle/provenance contract

## Approach Evaluation

- **Simplification baseline**: first rerun the current maintained book-like and non-TOC lanes unchanged on the widened corpus and inspect the actual artifacts. The first honest no-new-runtime candidate is a dedicated comparison harness over existing `driver.py` outputs; if that is enough to settle the coverage row, the story should not invent more runtime code.
- **AI-only**: a model can help judge source-vs-output fidelity or classify whether a fixture belongs in the book-like or non-TOC lane, but it cannot replace end-to-end `driver.py` proof, provenance checks, or explicit coverage truth. AI-only scoring is useful only if wrapped in a repeatable harness and backed by artifact inspection.
- **Hybrid**: likely strongest. Use repo-owned fixture widening, deterministic artifact checks, and explicit recipe/routing metadata as the backbone, with optional model judgment only for semantic quality comparisons that deterministic checks cannot score well.
- **Pure code**: appropriate for corpus plumbing, harness scripts, structural scoring, docs updates, and narrow runtime/routing fixes if the widened proof exposes one generic issue. Pure code alone is not enough to decide semantic fidelity without some judged surface.
- **Repo constraints / prior decisions**: `spec:1.1` keeps recipe ownership explicit; `spec:7` is still `partial`; `C2` and `C3` are both in `climb`, and `B1` is in `hold` in `docs/methodology/state.yaml`. Story 168 proved the bounded book-like lane, Story 171 proved the non-TOC lane, Story 177 widened flat proof, and Stories 178/180 proved confirmed handoff on maintained slices. Scout 011 says the honest standing is still bounded until validation broadens.
- **Existing patterns to reuse**: `benchmarks/scripts/run_layout_section_splitting_eval.py` and `tests/test_layout_section_splitting_benchmark.py` for a non-promptfoo maintained harness pattern; `benchmarks/scripts/run_auto_book_type_detection_eval.py` and `benchmarks/scripts/run_approved_intake_handoff_eval.py` for corpus-driven proof surfaces; `modules/intake/intake_plan_utils.py`; `tests/test_pdf_intake_recipe.py`; `tests/test_intake_plan_utils.py`; `tests/test_extract_pdf_marker_lite_html_v1.py`; `configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml`; `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`; and `testdata/generate_flat_born_digital_fixture.py`.
- **Eval**: the deciding evidence is a widened corpus run through both maintained lanes with inspected `doc-web` outputs, plus a repeatable born-digital comparison surface that records score/summary, fixture classifications, and retry conditions in `docs/evals/registry.yaml`. If routing or approved-handoff expectations change, rerun those surfaces too.

## Tasks

- [x] Freeze the widened born-digital proof surface from current repo reality:
  - [x] audit the current repo-owned fixtures and the two local comparison PDFs already cited in the coverage row
  - [x] add at least one additional repo-owned or reproducibly generated book-like born-digital fixture if that is the smallest honest way to pressure the book-like lane beyond `tbotb-mini`
  - [x] record the expected recipe lane, output shape, and review dimensions for every fixture in scope
- [x] Measure the current maintained lanes unchanged before changing runtime or routing behavior:
  - [x] run the maintained book-like lane on every in-scope book-like fixture
  - [x] run the maintained non-TOC lane on every in-scope flat/non-TOC fixture
  - [x] inspect emitted `page_html_v1`, portions, final HTML, and provenance artifacts and record exact strengths/failures with artifact paths
- [x] Add the smallest repeatable born-digital quality/comparison surface that can settle the coverage row honestly:
  - [x] prefer a corpus-driven harness under `benchmarks/scripts/` or `tests/` over ad hoc manual notes
  - [x] keep fixture classification, score/summary, and retry conditions inspectable
  - [x] add focused coverage so the new corpus/harness cannot silently drift
- [x] Implement only the smallest runtime, routing, or normalization change the widened proof justifies:
  - [x] no runtime change is required if the widened proofs and harness alone settle the row honestly
  - [x] if a generic defect appears, keep the fix bounded to the existing born-digital seams rather than adding a parallel path
  - [x] rerun affected proofs after any code change
- [x] If this story changes documented format coverage or graduation reality: update `tests/fixtures/formats/_coverage-matrix.json` and any relevant methodology state honestly
- [x] If routing or confirmed-handoff expectations change for born-digital PDFs: rerun the relevant maintained surfaces and update `docs/evals/registry.yaml` (not required in this slice because the widened proof did not change maintained routing or confirmed-handoff recommendations beyond documenting the bounded passing surface)
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] `make methodology-compile`
  - [x] `make methodology-check`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL/HTML data
  - [x] If agent tooling changed: `make skills-check` (not required; agent tooling unchanged)
- [x] If evals or goldens changed: run `/improve-eval` and update `docs/evals/registry.yaml` (satisfied by the fresh maintained born-digital benchmark reruns and verified registry update; no separate eval-repair pass was needed because the new surface already passed cleanly)
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every support claim traces to named fixtures, run IDs, artifact paths, and inspected outputs
  - [x] T1 — AI-First: keep AI for judgment/scoring where it beats deterministic checks, not for hiding routing or fidelity uncertainty
  - [x] T2 — Eval Before Build: widen and score the current lanes before adding new runtime behavior
  - [x] T3 — Fidelity: do not promote the coverage row if any widened fixture still shows inspected silent text-loss or provenance regression
  - [x] T4 — Modular: reuse the existing book-like and non-TOC seams instead of creating a third born-digital runtime
  - [x] T5 — Inspect Artifacts: manually open the widened proof outputs, not just benchmark summaries

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

- **Owning module / area**: maintained born-digital PDF recipes, the Marker-lite extract/normalize seam, intake routing/handoff truth surfaces, and the coverage/eval docs that say what the family honestly supports.
- **Methodology reality**: this story belongs to `spec:1`, `spec:3`, `spec:6`, `spec:7`, and `spec:8`. In `docs/methodology/state.yaml`, substrates for `spec:1`, `spec:3`, `spec:6`, and `spec:8` already exist, while `spec:7` remains `partial`; the active phases are `C2 = climb`, `C3 = climb`, and `B1 = hold`. Story 196 promotes the relevant `born-digital-pdf` coverage row from `has-fixture` to a bounded `passing` slice: four repo-owned supported cases across the maintained book-like and flat/non-TOC lanes, with two local comparison-only PDFs kept outside the passing gate.
- **Substrate evidence**: verified in this pass that both maintained recipes exist and are wired in code (`configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml`, `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`), intake routing already distinguishes the two lanes in `modules/intake/intake_plan_utils.py`, and smoke/regression coverage already exists in `tests/test_pdf_intake_recipe.py`, `tests/test_intake_plan_utils.py`, and `tests/test_extract_pdf_marker_lite_html_v1.py`. Story 196 adds the missing dedicated born-digital quality/comparison harness plus a broader repo-owned book-like proof surface through `benchmarks/scripts/run_born_digital_pdf_eval.py`, `benchmarks/golden/born-digital-pdf/corpus.json`, `tests/test_born_digital_pdf_benchmark.py`, `testdata/born-digital-handbook-mini.md`, and `testdata/generate_book_like_born_digital_fixture.py`.
- **Data contracts / schemas**: likely touched contracts are `page_html_v1`, `portion_hyp_v1`, `doc_web_bundle_manifest_v1`, `doc_web_provenance_block_v1`, `intake_plan_v1`, and `intake_handoff_v1`. If the story adds any new stamped comparison artifact or new cross-stage fields, they must be added to `schemas.py` before relying on them.
- **File sizes**: likely owner files are `configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml` (42 lines), `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml` (47), `modules/extract/extract_pdf_marker_lite_html_v1/main.py` (192), `modules/common/marker_page_html.py` (780), `modules/common/marker_lite_runtime.py` (892), `tests/test_pdf_intake_recipe.py` (197), `tests/test_intake_plan_utils.py` (268), `benchmarks/scripts/run_layout_section_splitting_eval.py` (191), `tests/test_layout_section_splitting_benchmark.py` (210), `docs/evals/registry.yaml` (1582), `tests/fixtures/formats/_coverage-matrix.json` (483), `docs/RUNBOOK.md` (439), and `schemas.py` (1237). `marker_page_html.py`, `marker_lite_runtime.py`, `docs/evals/registry.yaml`, and `schemas.py` are already oversized, so prefer a new harness/corpus file or narrow helper over bloating those further.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, Stories 168/170/171/177/178/180, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/RUNBOOK.md`, `modules/intake/intake_plan_utils.py`, `tests/test_pdf_intake_recipe.py`, `tests/test_intake_plan_utils.py`, and Scout 011. No narrower ADR or dedicated runbook currently resolves the missing born-digital quality surface.

## Files to Modify

- `benchmarks/scripts/run_born_digital_pdf_eval.py` — new corpus-driven maintained quality/comparison harness for the born-digital family
- `benchmarks/golden/born-digital-pdf/corpus.json` — new checked-in corpus describing fixture classes, expected recipe lanes, and score inputs
- `tests/test_born_digital_pdf_benchmark.py` — focused coverage for the new harness/corpus surface
- `testdata/generate_flat_born_digital_fixture.py` or a sibling generator — add a reproducible born-digital fixture only if widened proof needs one beyond the current repo-owned set (64 lines for the existing generator)
- `tests/test_pdf_intake_recipe.py` — widen smoke/proof coverage if the supported slice or fixture set expands (197 lines)
- `tests/test_intake_plan_utils.py` — update routing expectations only if widened proof changes what is honest to recommend (268 lines)
- `configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml` — bounded recipe updates only if widened proof exposes a book-like lane issue (42 lines)
- `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml` — bounded recipe updates only if widened proof exposes a flat-lane issue (47 lines)
- `modules/extract/extract_pdf_marker_lite_html_v1/main.py` — generic extract-stage fixes if the widened proof exposes them (192 lines)
- `modules/common/marker_page_html.py` — only if the widened proof shows a cross-fixture normalization issue worth fixing now (780 lines)
- `modules/common/marker_lite_runtime.py` — only if the widened proof depends on bounded runtime/bootstrap reporting changes (892 lines)
- `docs/evals/registry.yaml` — record the new born-digital quality/comparison surface and any rerun history (1582 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — update the `born-digital-pdf` row honestly after widened proof lands (483 lines)
- `docs/RUNBOOK.md` and `README.md` — align operator guidance with the post-story born-digital boundary (439 lines for `docs/RUNBOOK.md`)

## Redundancy / Removal Targets

- Any stale `born-digital-pdf` wording that still says the family is only a loose `has-fixture` placeholder after the new proof surface exists
- Any ad hoc born-digital comparison notes or one-off commands that become redundant once a maintained harness and corpus land
- Any local-only comparison dependency in the coverage row if the story succeeds in replacing it with a repo-owned or reproducible fixture

## Notes

- A new story ID is honest here. Story 168 proved the first book-like lane, Story 171 proved the non-TOC lane, and Story 177 widened one bounded flat rough edge. None of them owns the row-level question “is `born-digital-pdf` now honestly `passing`, and what repeatable quality surface proves that?” Reopening any one of those would blur a cross-lane coverage truth change with a previously closed slice.
- The highest-value outcome is not necessarily promotion to `passing`. If widened proof shows the book-like lane is still too thin or too operationally expensive, the honest success case is a narrower explicit boundary plus a durable quality surface.
- Keep the book-like lane and flat/non-TOC lane distinct. The story should unify coverage truth, not collapse the two maintained recipes into one vague born-digital promise.

## Plan

### Exploration Summary

- **Ideal alignment:** proceed. The story closes a real mission gap in `docs/ideal.md`: born-digital PDFs are a maintained family with explicit recipes and handoff evidence, but the current proof surface is still too thin to state the family truth confidently.
- **Current truth surface:** `tests/fixtures/formats/_coverage-matrix.json` keeps `born-digital-pdf` at `has-fixture` because support still rests on three repo-owned fixtures and two local comparison PDFs, with only one repo-owned book-like proof item.
- **Critical substrate verified:** both maintained lanes already exist in code and are wired into routing/tests today. This is not a “create the first runtime seam” story.
- **Critical missing substrate:** there is no dedicated born-digital quality/comparison harness in `benchmarks/scripts/` or `tests/`, and there is no broader repo-owned book-like proof surface beyond `tbotb-mini`.
- **Status selection:** `Pending` is honest because the required runtime and test substrate exists in the repo today; the story needs proof widening and harness work, not a speculative architecture invention.

### Implementation Order

1. **Freeze the widened corpus** (`S`)
   - Audit the current repo-owned book-like and flat fixtures first.
   - Decide whether one additional repo-owned book-like fixture is required to make `passing` even possible.
   - Record the expected recipe lane and review dimensions per fixture.

2. **Measure the current maintained lanes unchanged** (`M`)
   - Run `driver.py` on the widened corpus with the current recipes.
   - Inspect `page_html_v1`, portions, final HTML, and provenance outputs before changing code.
   - Record whether OCR comparison is still needed for honesty on any slice.

3. **Add the maintained quality/comparison surface** (`M`)
   - Prefer a corpus-driven harness patterned after `run_layout_section_splitting_eval.py`.
   - Keep the first version small: fixture classifications, artifact-path reporting, summary metrics, and retry conditions.
   - Add focused tests so the corpus and harness stay honest.

4. **Land only the smallest fix the proof justifies** (`S`, conditional)
   - If the widened proof only changes coverage truth, stop at docs/eval updates.
   - If one generic runtime defect blocks an otherwise honest promotion, fix that seam and rerun the affected proofs.

5. **Update truth surfaces** (`S`)
   - Refresh `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, and any affected runbook/README wording.
   - If routing or approved handoff changes, rerun and update those maintained surfaces too.

## Work Log

20260408-1022 — create-story: created Story 196 after `/triage` identified the strongest actionable gap as row-level born-digital proof breadth rather than reopening the blocked handwritten OCR line. Evidence reviewed in this pass: `docs/methodology/graph.json` shows no `In Progress`, `Pending`, or `Draft` stories; `tests/fixtures/formats/_coverage-matrix.json` still marks `born-digital-pdf` as `has-fixture`; `modules/intake/intake_plan_utils.py`, `tests/test_pdf_intake_recipe.py`, `tests/test_intake_plan_utils.py`, and the two maintained born-digital recipes prove the runtime and routing substrate already exists; `docs/evals/registry.yaml` shows routing/handoff proof but no dedicated born-digital quality surface. Result: a new `Pending` story is honest because the missing work is proof widening plus a harness, not a missing runtime seam. Next step: `/build-story` should freeze the widened corpus, measure the current lanes unchanged, and decide whether the coverage row can honestly move to `passing` or must stay narrower with a new maintained quality surface.
20260408-1049 — /build-story exploration baseline: verified the story remains honestly buildable and identified the real missing slice. Context rechecked in this pass: `docs/ideal.md`; `docs/spec.md` (`spec:1`, `spec:3`, `spec:6`, `spec:7`, `spec:8`); `docs/methodology/state.yaml`; `docs/methodology/graph.json`; ADR-002; Stories `168`, `170`, `171`, `177`, `178`, and `180`; `tests/fixtures/formats/_coverage-matrix.json`; `docs/evals/registry.yaml`; `docs/RUNBOOK.md`; `testdata/README.md`; `modules/extract/extract_pdf_marker_lite_html_v1/main.py`; `modules/common/marker_page_html.py`; `modules/common/marker_lite_runtime.py`; `modules/intake/intake_plan_utils.py`; `tests/test_pdf_intake_recipe.py`; and `tests/test_extract_pdf_marker_lite_html_v1.py`. Fresh substrate evidence: `docker --version` and `pdftotext -v` both succeeded in this checkout; `choose_maintained_recipe(...)` still distinguishes the current book-like and flat/non-TOC born-digital lanes; and fresh baseline `driver.py` proofs succeeded on all three repo-owned born-digital fixtures without any code changes: `story196-tbotb-baseline` completed through the book-like lane with `3` stamped `page_html_v1` rows, `5` TOC portions, `3` published HTML entries, and `51` provenance rows; `story196-flat-mini-baseline` completed through the non-TOC lane with `2` stamped `page_html_v1` rows, `2` portions, `2` published HTML entries, and `22` provenance rows; `story196-flat-form-baseline` completed through the non-TOC lane with `1` stamped `page_html_v1` row, `1` portion, `1` published HTML entry, and `12` provenance rows. Runtime burden remains real in the current environment (`162.89s` for the 3-page book-like proof, versus `27.13s` and `19.48s` for the two flat proofs), but no fresh generic runtime defect surfaced on the existing repo-owned slice. Critical substrate verified versus missing: the maintained runtime, routing, and smoke-test substrate all exist and work; the real missing pieces are still a second repo-owned book-like proof item and a dedicated born-digital quality/comparison harness. Patterns to follow: reuse the corpus-driven maintained-harness shape from `benchmarks/scripts/run_layout_section_splitting_eval.py` and keep any widened proof or runtime changes bounded to the existing born-digital seams. Files likely to change are still the harness/corpus/tests/doc surfaces already named in `Files to Modify`; files at highest structural risk remain `modules/common/marker_page_html.py`, `modules/common/marker_lite_runtime.py`, `docs/evals/registry.yaml`, and `schemas.py` because they are already large. Next step: add the smallest reproducible second book-like fixture, then build the maintained harness around the already-working lanes instead of inventing new runtime logic first.
20260408-1103 — implementation start: promoted Story 196 to `In Progress` before widening the proof surface. Began landing the smallest reproducible second book-like fixture as repo-owned substrate by adding `testdata/born-digital-handbook-mini.md` and `testdata/generate_book_like_born_digital_fixture.py`. First generation attempt failed with an `FPDFException` caused by `multi_cell(...)` cursor handling after section/title writes; patched the generator to reset to `LMARGIN/NEXT` explicitly so the fixture remains deterministic instead of relying on fragile default cursor state. Impact so far: the story has moved from planning into executable substrate work without touching the maintained runtime seams, which keeps the proof-widening effort honest and low-blast-radius. Next step: regenerate `testdata/born-digital-handbook-mini.pdf`, verify extractable native text, and run a fresh book-like `driver.py` proof on the new fixture before building the corpus-driven quality harness.
20260408-1138 — widened the repo-owned book-like slice and corrected a fixture-coherence failure before treating it as proof. `testdata/generate_book_like_born_digital_fixture.py` now honors explicit `<<<PAGEBREAK>>>` markers, and `testdata/born-digital-handbook-mini.md` uses them so the synthetic TOC matches the actual section pages. Fresh proof after the fix: `story196-handbook-baseline` completed through `recipe-born-digital-pdf-marker-lite-html-mvp.yaml` with `5` stamped `page_html_v1` rows, `4` TOC portions, `5` published HTML entries, and `20` provenance rows. Manual inspection in the same pass covered `output/runs/story196-handbook-baseline/output/html/manifest.json`, `output/runs/story196-handbook-baseline/output/html/page-001.html`, `output/runs/story196-handbook-baseline/output/html/chapter-001.html`, `output/runs/story196-handbook-baseline/output/html/chapter-004.html`, and `output/runs/story196-handbook-baseline/output/html/provenance/blocks.jsonl`; the corrected fixture now preserves the cover/contents page as `page-001.html` and cleanly maps each TOC line to one real chapter page. Impact: the story no longer depends on a single repo-owned book-like born-digital proof item, and the new fixture is honest enough to join the maintained supported slice instead of becoming synthetic noise.
20260408-1230 — added the maintained born-digital comparison surface and used it to settle the coverage row honestly. New substrate: `benchmarks/golden/born-digital-pdf/corpus.json`, `benchmarks/scorers/born_digital_pdf.py`, `benchmarks/scripts/run_born_digital_pdf_eval.py`, and `tests/test_born_digital_pdf_benchmark.py`. Fresh benchmark run via `python benchmarks/scripts/run_born_digital_pdf_eval.py --output benchmarks/results/born-digital-pdf-story196.json --run-root output/runs/story196-born-digital-benchmark` completed `6/6` present cases with `supported_docs = 4`, `comparison_docs = 2`, `pass_rate = 1.0`, `comparison_pass_rate = 1.0`, `overall = 1.0`, and `failed_runs = 0`. Manual inspection in the same pass covered `benchmarks/results/born-digital-pdf-story196.json`, `output/runs/story196-born-digital-benchmark-born-digital-handbook-mini/output/html/manifest.json`, `output/runs/story196-born-digital-benchmark-born-digital-handbook-mini/output/html/chapter-001.html`, `output/runs/story196-born-digital-benchmark-flat-born-digital-mini/output/html/provenance/blocks.jsonl`, `output/runs/story196-born-digital-benchmark-rfp/output/html/manifest.json`, and `output/runs/story196-born-digital-benchmark-release-forms/output/html/chapter-001.html`. Decision from that evidence: `tests/fixtures/formats/_coverage-matrix.json` can honestly promote `born-digital-pdf` to bounded `passing` for the four repo-owned supported fixtures across the two explicit lanes, while the two shared local PDFs stay comparison-only rather than carrying the passing claim. Follow-on doc truth updated in the same slice: `docs/evals/registry.yaml`, `docs/RUNBOOK.md`, `README.md`, and `testdata/README.md`.
20260408-1326 — validation follow-up fixed the remaining benchmark portability defect and reverified the story end to end. `tests/test_born_digital_pdf_benchmark.py` no longer hard-codes the current machine's checkout path and now loads the corpus through `DEFAULT_CORPUS` from the benchmark runner. Fresh validation in this pass: `pytest tests/test_born_digital_pdf_benchmark.py -q` passed (`5 passed`), `python benchmarks/scripts/run_born_digital_pdf_eval.py --output benchmarks/results/born-digital-pdf-story196-validate-fix.json --run-root output/runs/story196-born-digital-benchmark-validate-fix` completed `6/6` cases with `supported_docs = 4`, `comparison_docs = 2`, `pass_rate = 1.0`, `comparison_pass_rate = 1.0`, and `failed_runs = 0`, `make lint` passed, `make methodology-check` passed, and `make test` passed (`480 passed`). Additional same-pass artifact inspection covered `benchmarks/results/born-digital-pdf-story196-validate-fix.json`, `output/runs/story196-born-digital-benchmark-validate-fix-born-digital-handbook-mini/output/html/manifest.json`, and `output/runs/story196-born-digital-benchmark-validate-fix-born-digital-handbook-mini/output/html/chapter-001.html`. Impact: the maintained born-digital quality surface now validates cleanly without depending on this checkout's absolute path, so the story is ready for `/mark-story-done`.
20260408-1550 — `/mark-story-done` close-out: marked Story 196 `Done`, checked the workflow gate, and refreshed the generated methodology surfaces and changelog. Fresh close-out evidence in this pass: `pytest tests/test_born_digital_pdf_benchmark.py -q` passed (`5 passed`), `make lint` passed, `make methodology-compile` regenerated `docs/methodology/graph.json` and `docs/stories.md`, `make methodology-check` passed, `make test` passed (`480 passed`), and `python benchmarks/scripts/run_born_digital_pdf_eval.py --output benchmarks/results/born-digital-pdf-story196-validate-20260408b.json --run-root output/runs/story196-born-digital-benchmark-validate-20260408b` completed with `supported_docs = 4`, `comparison_docs = 2`, `pass_rate = 1.0`, `comparison_pass_rate = 1.0`, and `failed_runs = 0`. Additional artifact inspection in the same pass covered `output/runs/story196-born-digital-benchmark-validate-20260408b-born-digital-handbook-mini/01_extract_pdf_marker_lite_html_v1/pages_html.jsonl`, `output/runs/story196-born-digital-benchmark-validate-20260408b-born-digital-handbook-mini/03_portionize_toc_html_v1/portions_toc.jsonl`, `output/runs/story196-born-digital-benchmark-validate-20260408b-born-digital-handbook-mini/output/html/manifest.json`, `output/runs/story196-born-digital-benchmark-validate-20260408b-born-digital-handbook-mini/output/html/chapter-001.html`, and `output/runs/story196-born-digital-benchmark-validate-20260408b-flat-born-digital-mini/output/html/provenance/blocks.jsonl`. Impact: Story 196 now closes with a portable maintained benchmark, a bounded passing born-digital coverage claim, and fresh end-to-end evidence for both maintained lanes. Next step: `/check-in-diff`.
