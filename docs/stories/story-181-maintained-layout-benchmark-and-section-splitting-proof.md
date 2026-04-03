# Story 181 — Establish a Maintained Layout Benchmark and Provenance-Focused Section-Splitting Proof Surface

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Traceability is the product, Fidelity to the source, Transparency over magic
**Spec Refs**: spec:3 (spec:3.1, C3), spec:6, spec:8 (B1), spec:9 (B8)
**Build Map Refs**: Category 3 Layout & Structure Understanding (`exists`, C3 `climb`); Category 6 Validation, Provenance & Export (`exists`); Category 8 AI Harnesses & Tooling (`exists`, B1 `hold`); Category 9 Planning Infrastructure (`exists`, B8 `hold`); Input Coverage rows `docx` (`passing` on a bounded supported slice) and `born-digital-pdf` (`has fixture`)
**Decision Refs**: `docs/decisions/adr-001-source-aware-consistency-strategy/adr.md`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/stories/story-139-partial-toc-section-splitting-and-page-break-continuation.md`, `docs/stories/story-172-maintained-docx-intake-lane.md`, `docs/stories/story-177-born-digital-flat-proof-and-heading-cleanup.md`, `docs/inbox.md`, `tests/fixtures/formats/_coverage-matrix.json`, `None found after search in docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower maintained C3 benchmark or section-splitting-provenance runbook
**Depends On**: Story 172, Story 177

## Goal

Turn the current `C3` layout story from an unmeasured planning claim into an honest maintained benchmark and proof surface. The repo already has section-bearing, repo-owned fixtures on the maintained DOCX and flat born-digital lanes, but `docs/build-map.md` still says Category 3 has no dedicated eval and the inbox still carries a loose note that section splitting matters for provenance. This story should freeze a repo-owned benchmark corpus, score the current maintained section-splitting outputs against explicit section-order and provenance expectations, and record whether the current mixed heuristic+AI seam is healthy or whether a simpler challenger is already competitive on that bounded slice.

## Acceptance Criteria

- [x] A repo-owned or reproducibly generated benchmark corpus exists for at least 5 documents across at least 2 maintained section-bearing families and 3 section-layout patterns. The default starting slice is `testdata/docx-mini.docx`, `testdata/docx-sections-mini.docx`, `testdata/docx-nested-mini.docx`, `testdata/flat-born-digital-mini.pdf`, and `testdata/flat-born-digital-form-mini.pdf` unless `/build-story` finds a smaller honest substitute.
- [x] Each corpus case has checked-in expectations for:
  - top-level section or chapter order,
  - expected split boundaries or non-split behavior,
  - provenance assertions tied to the accepted final artifact surface (`manifest.json`, `provenance/blocks.jsonl`, and representative final HTML output).
- [x] Fresh `driver.py` proofs exist for every benchmark case using the maintained recipe for that family, and the story work log records manual inspection of:
  - the final bundle manifest,
  - the provenance sidecar,
  - and at least one representative HTML or portion artifact per family.
- [x] A new maintained benchmark surface exists in `benchmarks/` with the first recorded score in `docs/evals/registry.yaml`, and the story explicitly states whether that surface is:
  - a quality benchmark for the current maintained layout seam,
  - a compromise-detection surface for `C3`,
  - or a paired quality + challenger comparison that still leaves `C3` in `climb`.
- [x] The story measures at least one simpler challenger before adding runtime logic:
  - either a single-call model pass on a representative section-bearing slice,
  - or the thinnest no-new-logic direct-emitter baseline already present in the repo,
  - and records whether that challenger is honest enough to count as a real `C3` competitor on the bounded corpus.
- [x] Truth surfaces stay honest after the story lands:
  - `docs/build-map.md` no longer says Category 3 has no dedicated eval if this story adds one,
  - `docs/inbox.md` no longer carries the now-landed section-splitting note as untriaged,
  - and the docs do not imply scanned-layout or full `C3` closure beyond the repo-owned benchmark slice actually measured.

## Out of Scope

- Deleting `C3` outright without a passing benchmark and evidence that heuristic fallbacks are genuinely unnecessary
- Building a new universal layout runtime path before the maintained benchmark says the current seams are insufficient
- Reopening the Onward scanned genealogy repair stack or relying on non-repo-owned local source trees as the default benchmark corpus
- Changing the accepted `doc-web` bundle contract or Dossier boundary
- Broad new format-family work beyond the maintained DOCX and flat born-digital proof slices

## Approach Evaluation

- **Simplification baseline**: first measure whether a single-call or no-new-logic challenger can already produce an acceptable section map plus provenance story on a representative slice. This benchmark should not assume the current mixed seam is necessary if a thinner path already clears the bar.
- **AI-only**: a model could read source artifacts and emit section boundaries or ownership directly, but that is only useful here if it can be scored against explicit section/provenance expectations and remain inspectable enough to pressure `C3` honestly.
- **Hybrid**: likely best. Use driver-backed maintained outputs plus deterministic scoring as the primary truth surface, and optionally run a single-call challenger on the same corpus to measure how much custom layout logic still buys us.
- **Pure code**: plausible for the first implementation slice if the work stays in benchmark harnesses, goldens, scoring, and truth-surface updates. Runtime code should only change if the benchmark exposes one small generic defect worth fixing immediately.
- **Repo constraints / prior decisions**: ADR-002 keeps the public output boundary at the `doc-web` bundle and block-level provenance. ADR-001 favors explicit inspectable policy over prompt-only normalization. Story 172 and Story 177 already proved bounded repo-owned section-bearing fixtures. The current build map explicitly says `C3` has no dedicated eval, and the inbox note says section splitting matters for provenance. The story should resolve that benchmark gap before inventing more layout logic.
- **Existing patterns to reuse**: `benchmarks/scripts/run_auto_book_type_detection_eval.py`, `benchmarks/scripts/run_approved_intake_handoff_eval.py`, `benchmarks/scripts/run_handwritten_notes_eval.py`, `tests/test_approved_intake_handoff_benchmark.py`, `tests/test_doc_web_cli_contract.py`, `tests/test_pdf_intake_recipe.py`, `tests/test_build_chapter_html.py`, `tests/test_portionize_toc_html.py`, `tests/test_portionize_headings_html_v1.py`, `modules/transform/docx_elements_to_bundle_v1/main.py`, `modules/build/build_chapter_html_v1/main.py`, and `modules/common/marker_page_html.py`.
- **Eval**: the deciding proof is a repo-owned harness that scores final layout outputs against explicit section-splitting and provenance expectations. `/build-story` should decide whether the new surface belongs in `docs/evals/registry.yaml` as:
  - a quality benchmark for the current maintained seam,
  - a `C3` compromise-detection benchmark,
  - or a quality benchmark plus challenger comparison that still leaves the deletion gate open.

## Tasks

- [x] Freeze the maintained benchmark corpus and expected outcomes:
  - [x] start with the 5 repo-owned section-bearing fixtures already in this checkout unless `/build-story` finds a smaller honest slice,
  - [x] record expected section order, split boundaries, and provenance assertions for each case,
  - [x] keep non-repo-owned scanned-layout examples out of the default corpus unless the story proves they are reproducible in this worktree.
- [x] Measure the current maintained baselines before adding new logic:
  - [x] run the maintained `driver.py` path for each corpus document,
  - [x] inspect the final bundle manifest, provenance sidecar, and representative HTML or portion artifacts,
  - [x] record current layout strengths and failures with concrete artifact paths.
- [x] Measure the simplest challenger before expanding runtime work:
  - [x] test at least one thinner no-new-logic or single-call baseline on a representative case per family,
  - [x] record whether it is a real `C3` competitor or just contextual evidence,
  - [x] do not assume a benchmark-only story has to mutate runtime code.
- [x] Land the smallest honest benchmark surface:
  - [x] add a benchmark harness, scorer, and checked-in goldens,
  - [x] add focused benchmark test coverage,
  - [x] update `docs/evals/registry.yaml` with the first score, attempt history, and retry conditions,
  - [x] make the benchmark classification explicit (`quality`, `compromise`, or paired).
- [x] Update truth surfaces only as far as the evidence justifies:
  - [x] `docs/build-map.md`,
  - [x] `docs/inbox.md`,
  - [x] `tests/fixtures/formats/_coverage-matrix.json` not needed; the measured support claim did not change.
- [x] If the benchmark exposes a bounded generic runtime defect on the supported slice:
  - [x] no bounded production runtime defect surfaced on the supported slice; benchmark-side flat-PDF runtime isolation was sufficient for proof.
  - [x] no follow-up runtime repair story was needed in this pass.
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] Fresh `driver.py` benchmark proofs were rerun and manually inspected under `output/runs/story181-layout-benchmark-*`
  - [x] If agent tooling changed: not needed; agent tooling did not change
- [x] If evals or goldens changed: new eval + golden pack added directly in this story, benchmark rerun, and `docs/evals/registry.yaml` updated (`/improve-eval` not needed because this was eval creation, not iteration)
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: the benchmark scores real provenance-bearing outputs, not abstract labels alone
  - [x] T1 — AI-First: measured thinner challengers before considering any new runtime work
  - [x] T2 — Eval Before Build: benchmarked the current seam before adding layout logic
  - [x] T3 — Fidelity: section splits and non-splits were checked against the source-bearing artifacts, not just a preferred rendering style
  - [x] T4 — Modular: added a benchmark harness and truth-surface updates rather than another bespoke layout subsystem
  - [x] T5 — Inspect Artifacts: manually opened the generated outputs and provenance rows, not just the score JSON

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: Category 3 layout understanding and its benchmark truth surface. Primary ownership should stay in `benchmarks/` plus the maintained DOCX and flat born-digital recipe paths, not in a new layout-only runtime seam.
- **Build-map reality**: Category 3 is `exists` / `climb` because the runtime substrate exists but the benchmark surface does not. Category 6 matters because the proof must score accepted final provenance-bearing outputs. Category 8 matters because this is benchmark/tooling work before it is runtime work. Relevant input rows are `docx` and `born-digital-pdf`; this story intentionally does not claim the scanned-layout side of `C3` is closed.
- **Substrate evidence**: verified in this pass that the repo-owned fixtures exist under `testdata/` (`docx-mini`, `docx-sections-mini`, `docx-nested-mini`, `flat-born-digital-mini`, `flat-born-digital-form-mini`), the maintained recipe entrypoints exist in `configs/recipes/recipe-docx-html-mvp.yaml` and `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`, and the core section/provenance seams are implemented in `modules/transform/docx_elements_to_bundle_v1/main.py`, `modules/build/build_chapter_html_v1/main.py`, `modules/common/marker_page_html.py`, `modules/portionize/portionize_toc_html_v1/main.py`, and `modules/portionize/portionize_headings_html_v1/main.py`. Existing proof tests also exist in `tests/test_pdf_intake_recipe.py`, `tests/test_doc_web_cli_contract.py`, `tests/test_build_chapter_html.py`, `tests/test_portionize_toc_html.py`, and `tests/test_portionize_headings_html_v1.py`. Missing substrate is explicit: there is no maintained `C3` benchmark harness, scorer, or registry entry today.
- **Data contracts / schemas**: the likely scored contracts are `doc_web_bundle_manifest_v1`, `doc_web_provenance_block_v1`, and possibly `page_html_v1` or `portion_hyp_v1` if the benchmark needs intermediate-stage diagnostics. If the story introduces new runtime fields across artifact boundaries, they must be added to `schemas.py` before relying on stamped output.
- **File sizes**: likely truth-surface files are already large: `docs/build-map.md` is 586 lines and `docs/evals/registry.yaml` is 776 lines. Likely runtime files are also large: `modules/build/build_chapter_html_v1/main.py` is 1732 lines, `tests/test_build_chapter_html.py` is 1668 lines, and `modules/common/marker_page_html.py` is 780 lines. Smaller likely-at-risk files are `modules/portionize/portionize_toc_html_v1/main.py` (168), `modules/portionize/portionize_headings_html_v1/main.py` (228), `modules/transform/docx_elements_to_bundle_v1/main.py` (170), `tests/test_pdf_intake_recipe.py` (96), `tests/test_portionize_toc_html.py` (140), `tests/test_portionize_headings_html_v1.py` (84), `docs/stories.md` (189), and `docs/inbox.md` (7). Prefer new benchmark files and narrow targeted edits over bloating the oversized files.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/build-map.md`, ADR-001, ADR-002, Story 139, Story 172, Story 177, `tests/fixtures/formats/_coverage-matrix.json`, and `docs/inbox.md`. Search across `docs/runbooks/`, `docs/scout/`, and `docs/notes/` found no narrower maintained layout-benchmark decision surface to reuse.

## Files to Modify

- `benchmarks/scripts/run_layout_section_splitting_eval.py` — driver-backed maintained layout benchmark harness (new file)
- `benchmarks/scorers/layout_section_splitting.py` — section-order, split-boundary, and provenance scorer (new file)
- `benchmarks/golden/layout-section-splitting/` — corpus definitions, expected section maps, and inspected provenance assertions (new files)
- `tests/test_layout_section_splitting_benchmark.py` — benchmark harness and scorer coverage (new file)
- `docs/evals/registry.yaml` — register the first maintained layout benchmark score and retry conditions (776 lines)
- `docs/build-map.md` — replace the current `C3` “no eval” state with measured benchmark truth and residual caveats (586 lines)
- `docs/inbox.md` — remove the now-landed section-splitting note from the untriaged list (7 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — only if the benchmark changes what is honest to claim for `docx` or `born-digital-pdf`
- `modules/build/build_chapter_html_v1/main.py` — only if the benchmark exposes a bounded generic split/provenance defect in bundle assembly (1732 lines)
- `modules/portionize/portionize_toc_html_v1/main.py` — only if the benchmark shows TOC-owned splitting still needs a generic correction (168 lines)
- `modules/portionize/portionize_headings_html_v1/main.py` — only if the benchmark shows heading-owned splitting drift on the repo-owned flat slice (228 lines)
- `modules/transform/docx_elements_to_bundle_v1/main.py` — only if the benchmark exposes a DOCX-native section/provenance drift on the supported slice (170 lines)
- `modules/common/marker_page_html.py` — only if the benchmark shows flat born-digital heading normalization still distorts section ownership (780 lines)
- `tests/test_pdf_intake_recipe.py` — extend maintained born-digital regression coverage only if a bounded runtime fix lands (96 lines)
- `tests/test_build_chapter_html.py` — add narrow runtime regressions only if a bounded bundle fix lands (1668 lines)
- `tests/test_portionize_toc_html.py` — add regression coverage only if TOC splitting behavior changes (140 lines)
- `tests/test_portionize_headings_html_v1.py` — add regression coverage only if heading splitting behavior changes (84 lines)

## Redundancy / Removal Targets

- The current `docs/build-map.md` `C3` note that says there is no dedicated eval
- The untriaged section-splitting note in `docs/inbox.md` once this story lands
- Ad hoc story-local section-splitting proof commands if the new benchmark harness becomes the canonical maintained surface
- Any duplicate benchmark expectation logic scattered across story work logs instead of one checked-in scorer/golden pack

## Notes

- The default benchmark corpus is intentionally repo-owned. Story 139 remains the most useful design reference for scanned/TOC-driven section splitting, but it depends on harder-to-reproduce historical artifacts and should not silently become the maintained benchmark corpus in this story.
- This story may legitimately finish with no runtime code changes if the benchmark and challenger measurement already answer the next `C3` question honestly.
- If the benchmark exposes a larger layout gap than one bounded generic fix can handle, split the repair into a follow-up story instead of smuggling a broad runtime refactor into a benchmark story.
- Landing this story does not itself prove that VLM-only layout detection is ready to delete heuristics. It proves the project finally has a maintained benchmark and proof surface for the currently supported repo-owned slice.

## Plan

### Exploration Summary

- **Ideal alignment:** proceed. This story closes a real Category 3 gap that the current planning surfaces already call out: section splitting affects provenance quality, but the repo still lacks a maintained benchmark that measures that seam directly.
- **Relevant build-map state:** Category 3 is `exists` / `climb` and explicitly says there is no dedicated eval. Category 6 already defines the provenance bar. Category 8 already has the benchmark/tooling substrate, so the missing piece is the layout-specific harness and truth surface, not a new framework.
- **Critical substrate verified in this pass:** the repo-owned section-bearing fixtures, maintained DOCX and flat born-digital recipes, accepted final `doc-web` contracts, and relevant regression tests all exist locally. That makes the story honestly `Pending`, not `Draft`.
- **Critical missing slice:** no `benchmarks/` harness or scorer currently measures section order, split boundaries, and provenance on the maintained layout slice, and the current docs do not distinguish “no benchmark” from “benchmark failed.”
- **Current corpus reality:** the repo-owned maintained corpus is strong enough to start on native-text section-bearing layouts today (`docx` plus flat born-digital), but it does not yet justify claiming the scanned-layout side of `C3` is measured. The story should make that limitation explicit rather than hiding it.
- **Fresh baseline reality:** the maintained DOCX lane already produces inspectable final bundle + provenance output on all three repo-owned fixtures, including the nested-heading case. The maintained flat born-digital lane is buildable in principle but currently has a workflow hazard: the recipe hard-codes a shared Marker container name, so concurrent proof runs collide, and an isolated cold-start extract still did not yield `pages_html.jsonl` within the planning pass. The benchmark harness should therefore assume serialized flat-PDF proofs or explicit runtime-name isolation until the runtime surface is hardened.

### Eval-First Gate

- First freeze the benchmark corpus and run the current maintained recipes unchanged.
- Then measure one thinner challenger on a representative case per family before deciding whether any runtime logic is worth touching.
- Only after both measurements should the story decide whether the new eval belongs in the registry as a quality benchmark, a `C3` deletion-pressure benchmark, or a paired surface that still leaves `C3` in `climb`.

### Recommended Implementation Plan

1. Create the checked-in corpus and expectation pack.
   - Record expected section order, split and non-split boundaries, and provenance assertions per fixture.
   - Keep the expectations tied to accepted final artifacts, not vague visual judgments.
2. Add the maintained harness and scorer.
   - Reuse the existing repo pattern from the intake and handwriting benchmark scripts.
   - Keep the result JSON simple enough to summarize pass/fail, residual mismatches, and representative artifact paths.
   - For flat born-digital cases, serialize maintained proof runs by default or provide isolated runtime naming; do not assume the current recipe can safely run those cases in parallel.
3. Run fresh driver-backed proofs and manually inspect artifacts.
   - One fresh run root per corpus document or per family is acceptable as long as the work log names the exact artifacts inspected.
   - DOCX proofs can run cheaply across the full maintained slice; flat born-digital proofs should bias toward one-at-a-time runs until the shared Marker runtime seam is explicitly stabilized.
4. Measure the thinner challenger.
   - Keep it bounded and evidence-oriented. The goal is not to win with AI by force; it is to find out whether the current custom layout seam is still buying real value.
5. Update truth surfaces and only then decide whether a small runtime repair belongs in the same story.
   - If the benchmark shows only a tiny generic defect, absorb it and rerun.
   - If it shows a larger hole, record a follow-up instead of expanding scope blindly.

### Impact Analysis

- **Primary blast radius:** `benchmarks/` plus documentation truth surfaces.
- **Secondary blast radius:** the maintained DOCX and flat born-digital runtime seams only if the benchmark uncovers a bounded defect worth fixing immediately.
- **Main risks:** overstating the benchmark as “the C3 gate” when it is really the first maintained benchmark on a bounded repo-owned slice; and accidentally treating the current flat-PDF runtime bootstrap as parallel-safe when the recipe still shares one hard-coded Marker container name. The story should bias toward explicit caveats and serialized proof over inflated closure claims.
- **Structural health:** prefer new benchmark files over adding more policy logic into `build_chapter_html_v1` or `marker_page_html` without proof.

### What Done Looks Like

- The repo has a checked-in maintained layout benchmark and scorer.
- Fresh driver-backed artifacts and manual inspection back the first recorded score.
- `docs/build-map.md` no longer treats `C3` as unmeasured.
- The inbox note about section splitting and provenance is no longer floating as untriaged context.

## Work Log

20260402-0752 — story created from `/triage`: scoped the missing maintained `C3` benchmark after verifying that the repo already has section-bearing, repo-owned substrate on the DOCX and flat born-digital lanes but still no dedicated layout eval. Evidence reviewed in this pass: `docs/build-map.md` says Category 3 is `exists` / `climb` with “no eval”; `docs/inbox.md` still carried one untriaged note that section splitting matters for provenance; repo-owned fixtures exist at `testdata/docx-mini.docx`, `testdata/docx-sections-mini.docx`, `testdata/docx-nested-mini.docx`, `testdata/flat-born-digital-mini.pdf`, and `testdata/flat-born-digital-form-mini.pdf`; maintained recipes exist at `configs/recipes/recipe-docx-html-mvp.yaml` and `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`; and the relevant runtime/test substrate exists in `modules/transform/docx_elements_to_bundle_v1/main.py`, `modules/build/build_chapter_html_v1/main.py`, `modules/common/marker_page_html.py`, `tests/test_pdf_intake_recipe.py`, `tests/test_doc_web_cli_contract.py`, `tests/test_build_chapter_html.py`, `tests/test_portionize_toc_html.py`, and `tests/test_portionize_headings_html_v1.py`. Result: the story is `Pending`, not `Draft`, because the missing work is the benchmark/proof surface, not a prerequisite runtime seam. Next step: `/build-story` should freeze the repo-owned corpus, run the maintained baselines, measure one thinner challenger, and choose the smallest honest eval shape.
20260402-1752 — `/build-story` exploration and baseline proof: reviewed the cited Ideal/spec/build-map context plus Stories 172 and 177, then ran fresh maintained-driver baselines on the repo-owned DOCX slice and the flat born-digital entrypoint. Fresh DOCX proofs all completed and were manually inspected: `output/runs/story181-docx-mini/output/html/chapter-001.html` preserves the expected section/list/table structure from `testdata/docx-mini.source.json`; `output/runs/story181-docx-sections/output/html/chapter-001.html` keeps both overview paragraphs inside one chapter instead of inventing a split; `output/runs/story181-docx-nested/output/html/chapter-001.html` keeps `Subsection A` attached under `Overview`; and the corresponding `output/html/provenance/blocks.jsonl` files preserve non-empty `source_element_ids` and block-level `text_quote` rows for every inspected block. Flat born-digital baseline evidence was mixed in a way that matters to the story plan: `output/runs/story181-flat-mini/pipeline_events.jsonl` shows the maintained recipe failed in `marker_lite_html` after `2.46s` because `extract_pdf_marker_lite_html_v1` tried to rebuild the shared container `story168-marker-cpu-3662` while another run was touching the same runtime, and the isolated `story181-flat-form` rerun only reached `marker.execute` plus `marker_raw/flat-born-digital-form-mini.pdftotext.txt` before the planning pass stopped it, with no `pages_html.jsonl` emitted yet. Planning impact: Story 181 remains honestly buildable, but the benchmark harness should treat the DOCX slice as the cheap always-on proof surface and should serialize or isolate flat born-digital runtime usage instead of assuming parallel maintained proofs are currently safe. Next step: present the refined implementation plan for approval before writing benchmark code.
20260402-1833 — implementation completed and the first maintained C3 proof surface is now checked in. Code/files changed: added `benchmarks/golden/layout-section-splitting/corpus.json`, `benchmarks/scorers/layout_section_splitting.py`, `benchmarks/scripts/run_layout_section_splitting_eval.py`, and `tests/test_layout_section_splitting_benchmark.py`; updated `docs/evals/registry.yaml`, `docs/build-map.md`, `docs/stories.md`, and this story file. No production runtime modules changed: the benchmark passed without exposing a bounded generic defect on the supported slice, so the only flat-PDF runtime accommodation stayed in the benchmark harness, which materializes temporary isolated recipe copies with unique Marker container names to avoid shared-runtime collisions during proof runs. Fresh focused checks passed via `python -m pytest tests/test_layout_section_splitting_benchmark.py -q` (`5 passed`) and `python -m ruff check benchmarks/scorers/layout_section_splitting.py benchmarks/scripts/run_layout_section_splitting_eval.py tests/test_layout_section_splitting_benchmark.py` (`All checks passed!`). Fresh repo checks also passed: `make lint` and `make test` (`427 passed, 4 warnings`). Fresh driver-backed benchmark proof passed on all 5 repo-owned cases via `python benchmarks/scripts/run_layout_section_splitting_eval.py --output benchmarks/results/layout-section-splitting-story181.json --run-root output/runs/story181-layout-benchmark`, producing `pass_rate = 1.0`, `overall = 1.0`, `failed_runs = 0`, `challenger_cases = 2`, `challenger_real_competitors = 0`, and `challenger_overall = 0.6`. Manual artifact inspection in this pass covered: `output/runs/story181-layout-benchmark-docx-mini/output/html/manifest.json` plus `output/runs/story181-layout-benchmark-docx-mini/output/html/provenance/blocks.jsonl`, confirming pageless DOCX provenance with stable `source_element_ids` and the expected `Family Snapshot` / `Notes` split; `output/runs/story181-layout-benchmark-docx-nested/output/html/chapter-001.html`, confirming `Subsection A` stays attached under `Overview`; `output/runs/story181-layout-benchmark-flat-born-digital-mini/output/html/chapter-001.html` plus `output/runs/story181-layout-benchmark-flat-born-digital-mini/output/html/provenance/blocks.jsonl`, confirming `Requested information:` is the chapter title while `Budget notes:`, `Review notes:`, `Submission checklist:`, and `Operational details:` remain non-split in the same chapter with page-linked provenance rows (`p001-b5`, `p001-b7`, `p001-b9`, `p001-b11`, `p001-b13`); and `output/runs/story181-layout-benchmark-flat-born-digital-form-mini/output/html/chapter-001.html`, confirming the one-page form stays as one chapter rooted at `Participant information:` while preserving `Emergency contact:`, `Accessibility checklist:`, `Required acknowledgments:`, and `Signature block:` as in-chapter headings. Challenger conclusion recorded by the benchmark JSON and registry: the representative DOCX single-entry baseline derived from `01_unstructured_docx_intake_v1/elements.jsonl` is not an honest competitor because it misses expected splits and is not an accepted final bundle surface, and the flat extract-stage `doc_web_bundle` is also not an honest competitor because it preserves page-level provenance but fails the checked-in section expectations. Classification: this landed as a quality benchmark with challenger comparison, so C3 remains in `climb` rather than closing. Next step: `/validate`.
20260402-2349 — `/mark-story-done` close-out completed. Fresh validation in this close-out pass passed via `python -m pytest tests/` (`427 passed, 4 warnings`) and `python -m ruff check modules/ tests/` (`All checks passed!`). Rechecked dependency status in `docs/stories.md` and the dependent story files: Stories 172 and 177 are both `Done`. Reconfirmed the benchmark truth surface and registry/build-map alignment against `benchmarks/golden/layout-section-splitting/corpus.json`, `benchmarks/scorers/layout_section_splitting.py`, `benchmarks/scripts/run_layout_section_splitting_eval.py`, `docs/evals/registry.yaml`, and `docs/build-map.md`; no new ADR was needed because the story stays inside the accepted `doc-web` bundle/provenance boundary from ADR-002 and follows ADR-001's inspectable-artifact preference. Residual note kept explicit rather than blocking close-out: flat-PDF Marker container isolation still lives in the benchmark harness, so parallel-safe maintained runtime hardening remains a possible follow-up, not unfinished Story 181 scope. Next step: `/check-in-diff`.
