---
title: "Establish the First Honest Web-Page Direct-Entry Seam"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #1 (Ingest), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Any format, any condition, Zero configuration, Dossier-ready output, Transparency over magic"
spec_refs:
  - "spec:1"
  - "spec:1.1"
  - "spec:3"
  - "spec:3.1"
  - "spec:6"
  - "spec:7"
  - "spec:8"
  - "spec:9"
adr_refs: []
depends_on: []
category_refs:
  - "spec:1"
  - "spec:3"
  - "spec:6"
  - "spec:7"
  - "spec:8"
  - "spec:9"
compromise_refs:
  - "B1"
  - "C2"
  - "C3"
  - "B10"
input_coverage_refs:
  - "web-page"
architecture_domains:
  - "intake_and_routing"
roadmap_tags:
  - "campaign:maintained-intake-honesty"
legacy_system: ""
---

# Story 200 — Establish the First Honest Web-Page Direct-Entry Seam

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/stories/story-169-restore-contact-sheet-intake-and-benchmark-auto-book-type-detection.md`, `docs/stories/story-180-widen-approved-intake-handoff-image-directory-proof.md`, `docs/stories/story-194-office-intake-recommendation-and-handoff-boundary.md`, `docs/stories/story-197-establish-pptx-direct-entry-seam.md`, `tests/fixtures/formats/_coverage-matrix.json`, `benchmarks/scripts/run_auto_book_type_detection_eval.py`, `benchmarks/scripts/run_approved_intake_handoff_eval.py`, `benchmarks/scripts/intake_scope.py`, `README.md`, `docs/RUNBOOK.md`, and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower web-page direct-entry ADR or runbook`
**Depends On**: None

## Goal

`web-page` is now the clearest maintained intake gap with reusable downstream substrate already in repo. The coverage matrix still marks it `untested`, yet the repo already owns a viable HTML-to-`doc-web` chain through `page_html_v1`, heading-based portionization, and the existing bundle/provenance builder. This story should test the smallest honest web-page slice first: capture one public URL into a repo-owned reproducible HTML snapshot, prove that snapshot can travel through a maintained direct explicit-recipe lane into a `doc-web` bundle, and then leave one honest boundary behind. Either the bounded web-page row becomes a passing direct-entry slice with fresh `driver.py` artifact proof and updated intake-scope truth surfaces, or the repo records a named blocker instead of leaving web pages as an unowned format claim.

## Acceptance Criteria

- [x] A fresh current-pass baseline names the exact current web-page gap from repo evidence:
  - [x] the story records that `tests/fixtures/formats/_coverage-matrix.json` still marks `web-page` as `untested`
  - [x] the work log cites the verified absence of `input_html` / `input_url` support in `schemas.py` and `driver.py`
  - [x] the work log names the verified absence of a maintained `web-page` recipe/module pair in `configs/recipes/` and `modules/`
  - [x] and the intake benchmark scripts are cited with their current bounded scope (`pdf` only for recommendation-only intake, `pdf` plus `images_dir` for approved handoff) instead of relying on older prose
- [x] If the bounded seam reaches the accepted `doc-web` boundary, the repo lands one honest maintained web-page direct-entry slice:
  - [x] one repo-owned HTML snapshot fixture exists under `testdata/` with its source URL and capture note recorded in `testdata/README.md`, and tests do not depend on a live download
  - [x] a maintained direct-entry recipe completes through `driver.py` on that checked-in snapshot
  - [x] and manual artifact inspection is recorded for the emitted `page_html_v1` or equivalent intake artifact, final `output/html/manifest.json`, `output/html/provenance/blocks.jsonl`, and a representative published HTML entry
- [x] The bounded web-page lane reuses the existing HTML/`doc-web` path honestly:
  - [x] the story either proves the existing non-TOC HTML build chain is sufficient on the snapshot or records the smallest additional cleanup seam needed
  - [x] no parallel web-specific bundle/provenance contract is introduced if the existing `doc_web_bundle` surface is already adequate
  - [x] and no fabricated printed-page guarantees are added for a source family that is inherently pageless
- [x] Coverage, docs, and intake-boundary surfaces stay aligned with the outcome:
  - [x] `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, and `testdata/README.md` reflect the exact supported slice rather than a vague web promise
  - [x] the recommendation-only and approved-handoff benchmark surfaces are rerun or updated so the new family is represented honestly, whether that means an explicit direct-entry-only boundary case or a broader supported scope backed by fresh evidence
  - [x] and if the seam cannot be made honest on the chosen snapshot, the story does not close `Done`; it converts to `Blocked` with explicit blocker evidence and an unblock condition

## Out of Scope

- Multi-page crawling, sitemap traversal, login/authenticated pages, or generic website ingestion beyond one bounded checked-in snapshot
- Browser automation or JavaScript-rendered page capture if the first maintained slice can be proven on static HTML instead
- Expanding recommendation-only intake or approved-handoff automation to browse arbitrary live URLs as part of this story
- EPUB, email, or mixed-archive support
- Broad readability tuning, ad stripping, or boilerplate cleanup across arbitrary web layouts if the bounded fixture does not require it
- Tests or docs that depend on live network access after the fixture is captured

## Approach Evaluation

- **Simplification baseline**: first test the thinnest path that adds no new cleanup logic beyond a bounded HTML intake wrapper. The existing non-TOC HTML build chain already exists in repo, so the first question is whether a checked-in web snapshot can simply become one `page_html_v1` row and flow through `extract_page_numbers_html_v1` plus `portionize_headings_html_v1` into `build_chapter_html_v1`. A live model-only URL read is not current repo evidence and is not reproducible enough to be the maintained baseline by itself.
- **AI-only**: plausible only as a bounded comparison if the raw snapshot is too noisy. A one-shot model pass might help strip navigation or isolate the main article region, but that adds cost and a harder-to-reproduce failure surface before the repo has even measured whether the existing HTML path is already enough on the chosen fixture.
- **Hybrid**: likely winner if the raw snapshot alone is too noisy. Keep capture and HTML wrapping deterministic, reuse the existing HTML-to-`doc-web` chain, and only introduce a bounded AI or readability cleanup step if fresh artifact inspection shows the direct path fails on obvious boilerplate or heading ownership.
- **Pure code**: viable if the chosen snapshot is article-like and the existing heading/paragraph structure survives as-is. This is the cheapest and simplest maintained outcome, but it must be proven with fresh bundle/provenance artifacts rather than assumed from the input family label.
- **Repo constraints / prior decisions**: `spec:1.1` keeps the recipe surface explicit, `spec:7` keeps the `doc-web` boundary versioned and inspectable, Story 194 intentionally left recommendation-only intake limited to `pdf` and `images_dir`, and ADR-002 says the right move is to land new direct-entry seams through the accepted `doc-web` boundary rather than inventing parallel output contracts. No narrower web-page ADR or runbook already settles the source-capture or direct-entry question.
- **Existing patterns to reuse**: `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml` already proves the `page_html_v1` to `doc_web_bundle` chain for pageless HTML-like input; `modules/transform/extract_page_numbers_html_v1/main.py`, `modules/portionize/portionize_headings_html_v1/main.py`, `modules/adapter/html_to_blocks_v1/main.py`, and `modules/common/html_utils.py` provide reusable HTML handling; Stories 169, 180, 194, and 197 provide the current intake-boundary and direct-entry precedent.
- **Eval**: the deciding proof surface is a fresh `driver.py` run on the checked-in HTML snapshot plus manual artifact inspection, then a rerun or boundary-truth update for `auto-book-type-detection` and `approved-intake-handoff`. If the story introduces any new AI cleanup step, it should add a bounded fixture-backed regression or eval surface before claiming the seam is stable.

## Tasks

- [x] Freeze the current web-page seam from repo reality before changing code:
  - [x] verify the `web-page` row is still `untested`
  - [x] verify `schemas.py` / `driver.py` still have no `input_html` or `input_url`
  - [x] verify there is still no maintained `web-page` recipe/module pair
  - [x] and record the current bounded scope of the intake benchmark scripts and their explicit scope-blocking helper
- [x] Add one repo-owned reproducible web snapshot fixture:
  - [x] capture one public URL into a bounded checked-in HTML artifact plus source metadata under `testdata/`
  - [x] record source URL, capture note, and any rights/licensing caveat in `testdata/README.md`
  - [x] and keep all tests and future reruns independent of live network access
- [x] Measure the smallest honest implementation baseline before adding cleanup logic:
  - [x] test whether a raw HTML snapshot can be wrapped into existing `page_html_v1` and flow through the current non-TOC HTML build chain unchanged
  - [x] only if that fails, compare the smallest bounded cleanup candidate on the same snapshot (`not needed`; the raw snapshot path succeeded)
  - [x] and record the exact artifact paths and failure modes inspected for the before-state
- [x] If the bounded direct-entry seam is viable, land the smallest coherent web-page lane:
  - [x] add `input_html` support in `schemas.py` / `driver.py` or the smallest honest successor input contract
  - [x] add a maintained `recipe-web-page-html-mvp.yaml`
  - [x] add a web-page intake module that emits existing `page_html_v1`-compatible output from the checked-in snapshot
  - [x] reuse `extract_page_numbers_html_v1`, `portionize_headings_html_v1`, and `build_chapter_html_v1` rather than inventing a parallel web bundle transform
- [x] Add focused fixture-backed coverage for the new seam:
  - [x] a direct-entry smoke test that runs `driver.py` on the checked-in snapshot and asserts bundle/provenance outputs
  - [x] and benchmark-surface coverage or explicit scope-case tests so recommendation-only intake and approved handoff represent the new family honestly
- [x] Run real `driver.py` verification and artifact inspection if the lane lands:
  - [x] clear stale `*.pyc`
  - [x] run the maintained recipe through `driver.py`
  - [x] verify artifacts exist in `output/runs/`
  - [x] and manually inspect sample JSON/JSONL and published HTML data
- [x] If the seam cannot honestly cross the accepted boundary on the chosen snapshot, convert the story to `Blocked` with named blocker evidence instead of widening scope casually (`not needed`; the verified slice passed)
- [x] If this story changes documented format coverage or graduation reality: update `tests/fixtures/formats/_coverage-matrix.json` and any relevant methodology state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py` or `make smoke`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [x] If agent tooling changed: `make skills-check` (`not needed`; no agent tooling changed)
- [x] If evals or goldens changed: run `/improve-eval` and update `docs/evals/registry.yaml` (`not needed`; no eval or golden files changed)
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every support claim names the source URL, checked-in snapshot, run ID, and inspected bundle/provenance artifacts
  - [x] T1 — AI-First: no custom cleanup logic lands before the bounded baseline proves it is needed
  - [x] T2 — Eval Before Build: the raw-snapshot baseline and intake-boundary truth surfaces are measured before adding new logic
  - [x] T3 — Fidelity: the checked-in snapshot content is preserved faithfully on the claimed slice, with any excluded boilerplate or unsupported behavior made explicit
  - [x] T4 — Modular: the winning seam reuses the existing HTML/`doc-web` path instead of creating a parallel web-only runtime
  - [x] T5 — Inspect Artifacts: manually inspect the emitted `page_html_v1`, bundle manifest, provenance rows, and final HTML output

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

- **Owning module / area**: the bounded web-page direct-entry seam should live at intake/runtime boundary edges, not as a new bundle subsystem. Likely ownership is one new HTML snapshot intake module plus the existing `page_html_v1` to `doc_web_bundle` chain and the intake-scope benchmark surfaces.
- **Methodology reality**: this belongs to `spec:1`, `spec:3`, `spec:6`, `spec:7`, `spec:8`, and `spec:9`. In `docs/methodology/state.yaml`, `spec:1`, `spec:3`, `spec:6`, `spec:8`, and `spec:9` substrates already exist, while `spec:7` is still `partial`. Relevant active phases are `C2 = climb`, `C3 = climb`, `B1 = hold`, and `B10 = climb`. The relevant coverage row is `web-page`, which is still `untested`.
- **Substrate evidence**: verified in this pass that `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml` already proves a maintained `page_html_v1` to `build_chapter_html_v1` chain; `modules/transform/extract_page_numbers_html_v1/main.py`, `modules/portionize/portionize_headings_html_v1/main.py`, `modules/adapter/html_to_blocks_v1/main.py`, and `modules/common/html_utils.py` provide reusable HTML handling; and the benchmark scope helper already owns explicit boundary reasons for non-supported input kinds. Also verified in this pass that `schemas.py` and `driver.py` have `input_pdf`, `input_images`, `input_docx`, `input_xlsx`, and `input_pptx`, but no `input_html` or `input_url`; there is no maintained `web-page` recipe/module pair; and there is no checked-in web-page fixture yet. That makes the story honestly `Pending`: the downstream bundle substrate exists, while the missing work is the bounded intake seam itself.
- **Data contracts / schemas**: the preferred outcome is to reuse existing `page_html_v1`, `portion_hyp_v1`, `doc_web_bundle_manifest_v1`, and `doc_web_provenance_block_v1` without inventing a new web-page artifact contract. The likely schema change is only `RunConfig` support for a bounded HTML input override (`input_html` or an explicitly justified successor). If source URL metadata needs to survive beyond the fixture README, it should be added explicitly to the relevant schema instead of being hidden in ad hoc sidecars.
- **File sizes**: likely large touch points are `driver.py` (2270 lines), `schemas.py` (1238), `docs/RUNBOOK.md` (526), and `docs/evals/registry.yaml` (1733) if eval history changes. Mid-sized likely touch points are `benchmarks/scripts/run_approved_intake_handoff_eval.py` (341), `README.md` (321), and `modules/intake/intake_plan_utils.py` (308) only if the story ends up changing direct-entry recipe classification there. Existing reusable HTML path files are smaller: `modules/portionize/portionize_headings_html_v1/main.py` (228), `benchmarks/scripts/run_auto_book_type_detection_eval.py` (221), `modules/adapter/html_to_blocks_v1/main.py` (257), `tests/test_approved_intake_handoff_benchmark.py` (157), `modules/transform/extract_page_numbers_html_v1/main.py` (154), `testdata/README.md` (106), `tests/fixtures/formats/_coverage-matrix.json` (490), and `benchmarks/scripts/intake_scope.py` (47). Keep edits especially surgical in the oversized files.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, Stories 169/180/194/197, the `web-page` coverage row, the intake benchmark scripts, `benchmarks/scripts/intake_scope.py`, and the current reusable HTML path files. No narrower web-page-specific ADR, runbook, scout, or note was found after search.

## Files to Modify

- `schemas.py` — likely add `input_html` or the smallest honest direct-entry web snapshot input contract (1238 lines)
- `driver.py` — likely add `--input-html` override plumbing parallel to the existing direct-entry seams (2270 lines)
- `configs/recipes/recipe-web-page-html-mvp.yaml` — maintained bounded web-page direct-entry recipe reusing the existing non-TOC HTML build chain (new file)
- `modules/extract/web_page_html_intake_v1/main.py` — intake module that wraps a checked-in HTML snapshot into `page_html_v1`-compatible output (new file)
- `tests/test_web_page_intake_recipe.py` — focused driver smoke and artifact assertions for the bounded web-page fixture (new file)
- `benchmarks/scripts/intake_scope.py` — generalize or extend the explicit direct-entry-only scope handling if web pages join that boundary class (47 lines)
- `benchmarks/scripts/run_auto_book_type_detection_eval.py` — update the recommendation-only intake surface if web-page scope cases need to be exercised honestly (221 lines)
- `benchmarks/scripts/run_approved_intake_handoff_eval.py` — update the approved-handoff surface if web-page scope cases or reasons change (341 lines)
- `tests/test_auto_book_type_detection_benchmark.py` — keep the recommendation-only benchmark truth aligned with the new family boundary (64 lines)
- `tests/test_approved_intake_handoff_benchmark.py` — keep the approved-handoff benchmark truth aligned with the new family boundary (157 lines)
- `benchmarks/golden/auto-book-type-detection/corpus.json` — update only if the maintained benchmark corpus should explicitly exercise the new family boundary (82 lines)
- `benchmarks/golden/approved-intake-handoff/corpus.json` — update only if the maintained benchmark corpus should explicitly exercise the new family boundary (90 lines)
- `testdata/web-page-mini.html` — bounded repo-owned HTML snapshot fixture for the first maintained web-page slice (new file)
- `testdata/web-page-mini.source.json` — source URL and capture metadata for the snapshot fixture (new file)
- `testdata/README.md` — record the source URL, capture note, and why tests do not depend on the live page (106 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — move the `web-page` row only as far as fresh evidence justifies (490 lines)
- `README.md` — align user-facing format support wording with the actual web-page seam (321 lines)
- `docs/RUNBOOK.md` — publish the verified bounded web-page direct-entry command or the blocker if the seam cannot land (526 lines)
- `docs/evals/registry.yaml` — update intake benchmark history only if the web-page boundary changes those surfaces materially (1733 lines)

## Redundancy / Removal Targets

- The `OFFICE_DIRECT_ENTRY_INPUT_KINDS` naming in `benchmarks/scripts/intake_scope.py` if the helper starts covering a broader direct-entry class than office files alone
- Any ad hoc note or doc wording that still treats `web-page` as an entirely unowned family after a bounded direct-entry slice lands
- Any temptation to add a parallel web-only bundle/provenance path if the existing HTML/`doc-web` chain is already sufficient
- Any live-fetch-only test or script path that would make CI or future reruns depend on the network after the fixture is checked in

## Notes

- New story justification: it would not be honest to reopen Story 194 or Story 197. Story 194 settled the recommendation-only and approved-handoff boundary for the then-real families, and Story 197 settled the PPTX direct-entry seam. `web-page` is a different input family with a different fixture, intake contract, and validation boundary.
- This story does not need a new operator UI slice. The existing explicit-recipe interface is the honest first maintained surface for a single checked-in web snapshot, and the recommendation-only automation should only change enough to represent that boundary truthfully.
- If the chosen public source page cannot be checked in honestly because of rights, instability, or hidden dynamic dependencies, stop and pick a better bounded source or block the story explicitly. Do not smuggle a live copyrighted dependency into the maintained test surface.

## Plan

`/build-story` should decide the thinnest honest lane from the verified substrate above.

Current baseline from this create-story pass:
- `web-page` is still `untested` in the coverage matrix.
- `schemas.py` and `driver.py` expose direct-entry overrides for `pdf`, `images_dir`, `docx`, `xlsx`, and `pptx`, but not for HTML snapshots or live URLs.
- the reusable downstream HTML path already exists through `recipe-born-digital-pdf-non-toc-html-mvp.yaml`, `extract_page_numbers_html_v1`, `portionize_headings_html_v1`, and `build_chapter_html_v1`.
- the intake benchmark surfaces still deliberately scope recommendation-only intake to `pdf` and approved handoff to `pdf` plus `images_dir`.

Expected next step:
- promote the story to `In Progress`
- land the smallest honest `input_html` + checked-snapshot intake seam
- rerun the direct-entry proof through `driver.py`
- and then align coverage/docs/intake-boundary surfaces to the verified result

## Work Log

20260408-1955 — create-story: created Story 200 after `/triage` found no actionable `In Progress`, `Pending`, or `Draft` line beyond blocked Story 191 and the user approved the next action to open the first honest `web-page` seam. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, Stories 169/180/194/197, `tests/fixtures/formats/_coverage-matrix.json`, `benchmarks/scripts/run_auto_book_type_detection_eval.py`, `benchmarks/scripts/run_approved_intake_handoff_eval.py`, `benchmarks/scripts/intake_scope.py`, `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`, `modules/transform/extract_page_numbers_html_v1/main.py`, `modules/portionize/portionize_headings_html_v1/main.py`, `modules/adapter/html_to_blocks_v1/main.py`, `modules/common/html_utils.py`, `schemas.py`, and `driver.py`. Fresh baseline evidence: the coverage row is still `web-page: untested`; the driver/runtime currently has no `input_html` or `input_url`; the intake benchmark scripts still scope recommendation-only intake to `pdf` and approved handoff to `pdf` plus `images_dir`; and there is no maintained `web-page` recipe/module pair. Result: a new `Pending` story is honest because the downstream HTML-to-`doc-web` substrate already exists, while the missing work is a bounded new intake seam rather than a blocked research question. Next step: `/build-story` should freeze the raw baseline, choose the bounded snapshot source, and test whether the existing HTML path already clears the first web-page proof surface.

20260408-2146 — build-story start: promoted Story 200 to `In Progress` after a fresh substrate recheck and a manual baseline proof on the chosen bounded source. Verified again that `tests/fixtures/formats/_coverage-matrix.json` still marks `web-page` as `untested`; `schemas.py` `RunConfig` plus `driver.py` only expose direct-entry overrides for `pdf`, `images`, `docx`, `xlsx`, and `pptx`; and the intake benchmark scripts still keep recommendation-only intake scoped to `pdf` and approved handoff scoped to `pdf` plus `images_dir`. Chosen bounded source: `https://example.com/`, captured as a tiny stable public HTML page suitable for a repo-owned snapshot without introducing browser automation or live test dependence. Fresh manual baseline: a one-row `page_html_v1` JSONL built from that page's body HTML successfully flowed through `extract_page_numbers_html_v1`, `portionize_headings_html_v1 --allow-unnumbered --fallback-mode single-document`, and `build_chapter_html_v1`, producing one chapter titled `Example Domain`. Result: the downstream HTML/`doc-web` chain is already sufficient on the probe, so the implementation should stay tightly scoped to a checked-snapshot intake module, `driver.py` `input_html` plumbing, a maintained explicit recipe, and aligned docs/coverage/scope truth rather than adding a parallel web-specific bundle contract.

20260408-2218 — implementation + proof: landed the bounded direct-entry seam as `schemas.py` / `driver.py` `input_html` support, `modules/extract/web_page_html_intake_v1`, `configs/recipes/recipe-web-page-html-mvp.yaml`, the checked fixture pair `testdata/web-page-mini.html` + `testdata/web-page-mini.source.json`, focused smoke coverage in `tests/test_web_page_intake_recipe.py`, and explicit direct-entry-only boundary updates in `benchmarks/scripts/intake_scope.py`, `tests/test_auto_book_type_detection_benchmark.py`, `tests/test_approved_intake_handoff_benchmark.py`, and `tests/test_intake_plan_utils.py`. Fresh targeted verification passed in this pass: `pytest -q tests/test_run_config.py tests/test_intake_plan_utils.py tests/test_auto_book_type_detection_benchmark.py tests/test_approved_intake_handoff_benchmark.py tests/test_web_page_intake_recipe.py` → `38 passed in 2.27s`. Fresh real-run proof also passed: `python driver.py --recipe configs/recipes/recipe-web-page-html-mvp.yaml --input-html testdata/web-page-mini.html --run-id story200-web-page-mini --allow-run-id-reuse --force`, followed by schema validation on `output/runs/story200-web-page-mini/01_web_page_html_intake_v1/pages_html.jsonl`, `output/runs/story200-web-page-mini/output/html/manifest.json`, and `output/runs/story200-web-page-mini/output/html/provenance/blocks.jsonl`. Manual artifact inspection in the same pass: the intake artifact preserved the checked snapshot plus source URL; `manifest.json` emitted one entry titled `Example Domain` with `source_pages: [1]`; `provenance/blocks.jsonl` contained three coherent block rows (`Example Domain`, the body paragraph, `Learn more`) with `source_page_number = 1` and null printed-page fields; and `output/html/chapter-001.html` rendered the expected heading, paragraph, and link. Automation boundary truth stayed narrow by design: targeted reruns of both benchmark harnesses on a temporary one-case web-page corpus produced explicit blocked rows with `scope_policy = direct_explicit_recipe_only` and boundary reasons `outside_recommendation_only_intake:web-page:direct_explicit_recipe_only` and `outside_approved_intake_handoff:web-page:direct_explicit_recipe_only`.

20260408-2241 — mark-story-done: revalidated Story 200 before close-out against the accepted `doc-web` boundary in ADR-002 and the relevant `spec:1` / `spec:7` explicit-recipe constraints. Fresh close-out evidence in this pass: `make test` → `498 passed, 4 warnings`; `make lint` → pass; `python driver.py --recipe configs/recipes/recipe-web-page-html-mvp.yaml --input-html testdata/web-page-mini.html --run-id story200-web-page-validate --allow-run-id-reuse --force` → pass; `python validate_artifact.py --schema page_html_v1 --file output/runs/story200-web-page-validate/01_web_page_html_intake_v1/pages_html.jsonl`; `python validate_artifact.py --schema doc_web_bundle_manifest_v1 --file output/runs/story200-web-page-validate/output/html/manifest.json`; and `python validate_artifact.py --schema doc_web_provenance_block_v1 --file output/runs/story200-web-page-validate/output/html/provenance/blocks.jsonl` all passed. Manual inspection in the same pass reconfirmed the checked snapshot plus source URL in the intake artifact, one `Example Domain` chapter in the final manifest, three coherent provenance blocks, and the expected rendered heading/body/link in the published HTML. Result: all acceptance criteria, task checkboxes, Central Tenet checks, and workflow gates are now satisfied; Story 200 is ready for landing. Next step: `/check-in-diff`.


## October 23 continuation — keep excluded snapshot content excluded

20261023-1508 — build-story plan: reopened this same intake/module/recipe boundary under the standing triage-and-fix goal. The last meaningful proof was April 8; new current-runtime evidence is a real driver success on an inactive-only body that republishes the very script/template tags the wrapper removed. `output/triage-20261023-web-snapshot-audit/baseline.json` and `baseline-driver.log` bind the offline counterexample; `output/runs/triage-20261023-web-inactive-baseline/01_web_page_html_intake_v1/pages_html.jsonl` restores the complete raw document in `html`, and `output/html/chapter-001.html` contains its script inside the article. The source is a harmless synthetic throw sentinel, never rendered or executed. No provider requests.

This is the general fail-open cleaning pattern: an empty cleaned result falls back to the unclean source. The cause and correction are directly demonstrated, so no speculative research or new sanitizer is needed. Deterministic code fits the existing exact exclusion policy; a decision model or language model adds uncertainty and cost without improving the known tag/empty-result rule. Preserve `raw_html` for accepted snapshots, return only the cleaned body/fragment, and reject an empty cleaned result with a source-path diagnostic before publishing artifacts. This is not a claim to sanitize arbitrary active HTML or support JavaScript-dependent capture. ADR-002 and spec:1.1/3.1/6/7 remain the owning boundary; no narrower ADR changes the repair, recipe choice or output schema.

Continuation acceptance and validation:
- [x] Excluded script/noscript/template nodes never reappear when cleaning empties a full document or fragment.
- [x] Empty cleaned snapshots fail through driver.py with the source path and do not publish a page artifact or bundle.
- [x] Body prose, fragment prose and image markup retain their existing intake behavior; accepted `raw_html` and source provenance remain accurate.
- [x] Focused regressions pass, actual maintained positive driver runs produce schema-valid artifacts in output/runs/, and manual data plus rendered inspection covers the changed boundary.

Plan: first add failing regressions against the existing wrapper; remove its raw fallback and reject empty cleaned input; run the narrow local recipe tests and lint; execute positive controls and the negative counterexample through driver.py; inspect page rows, block quotes, manifests and rendered positive HTML; then close this continuation with the existing story. Do not change coverage scores, providers, defaults, broad HTML policy or unrelated worktree changes.

20261023-1512 — implementation, validation and mark-story-done continuation: the new regressions first failed (9 failed, 8 passed), directly covering raw-source restoration and the previously successful inactive-only driver. Removed the raw fallback and added an explicit empty-cleaned-input failure before saving a row. Fixed the negative test's run directory to match its actual run id before accepting the result. `python -m pytest tests/test_web_page_intake_recipe.py -q` now passes all17; `make lint` passes. The only production change is the existing wrapper's cleaning result and empty check. This does not add an HTML security sanitizer or alter accepted nonempty markup policy.

Fresh completion proof: `output/triage-20261023-web-snapshot-audit/run_proofs.py` cleared this module's Python cache and executed the maintained recipe on three accepted inputs plus the original rejected counterexample. `output/runs/triage-20261023-web-maintained-proof/`, `triage-20261023-web-mixed-proof/` and `triage-20261023-web-fragment-proof/` each contain real `01_web_page_html_intake_v1/pages_html.jsonl`, `output/html/manifest.json`, `output/html/provenance/blocks.jsonl` and `output/html/chapter-001.html`; all nine schema checks pass. `output/runs/triage-20261023-web-inactive-proof/pipeline_state.json` records failed intake, the driver exits1 with the source-path diagnostic, and neither a page artifact nor bundle is published. No downstream work runs for that rejected input. Logs and exact checked data are in `output/triage-20261023-web-snapshot-audit/driver-results.json` and its four driver logs.

Manual data inspection opened all three page rows and nine provenance records. Maintained fixture quotes remain Example Domain, its complete documentation-domain paragraph, and Learn more; source remains the checked snapshot plus https://example.com/. Both body and fragment controls preserve exactly Safe Snapshot / Retained source prose. / Second source paragraph., each anchored to source page1 with null printed-page fields. Accepted raw_html equals its original snapshot, source paths remain correct, and page/chapter HTML contains no excluded tags. A hidden local browser render of the mixed control visibly showed the heading and both paragraphs with navigation, no inactive/template text, and no stray metadata document; the temporary tab/server were closed afterward. Image-only markup remains covered by the positive unit controls without an unsupported general illustration claim.

Findings-first review checked the three-line production correction, actual call site, negative artifact absence, raw/source retention and unchanged accepted content. T0 source/raw provenance is retained; T1 exact policy stays in code rather than a model; T2 the deterministic failing baseline establishes the needed repair without paid inference; T3 nine source quotes and raw inputs match; T4 the existing module/recipe/schema remain in use; T5 actual rendered output was inspected. Proportional validation uses these focused checks and fresh driver/artifact proofs; no broad-suite or unchanged intake-benchmark rerun is claimed. No registry, score, coverage, default, API or account change, commit or push. All continuation gates are satisfied; Story200 returns to Done. The next independent triage candidates are confirmed ZIP destination-alias loss and mutable folder-member identity (read-only lane packet); the discovery repair remains gated on the pending credential decision.


## October 23 continuation — local HTML coverage truth

20261023 — triage/build-story plan: bounded zero-inference audit found that the existing .html/.htm routing and checked-HTML recipe already preserve a local static file's headings, lists, table, emphasis and link in the published chapter. The canonical html-files row still points to retired legacy text passthrough and says no semantic extraction, so it misdescribes the maintained available lane. Keep this in Story200's same module/fixture/artifact/operator surface. Promote the public synthetic Harbor fixture from the exploratory audit to `testdata/static-html-mini.html` with source notes, rerun the unchanged maintained driver against that exact checked-in path, manually inspect structured chapter plus page-level provenance and visual output, then correct the existing inventory row without inventing numerical quality scores. No implementation change, new recipe, new story, model call, or general HTML/CSS/browser/asset support claim. State/spec/ADR002 boundaries remain unchanged. The row must explicitly retain lack of cell/list-item provenance and arbitrary-site rendering qualification.

Continuation acceptance:
- [x] A checked-in synthetic heading/list/table fixture runs through the existing real driver and produces validated artifacts with exact local source identity.
- [x] Source values/markup and visible output are manually inspected; prose/list/table-level claims are separated from current whole-main provenance.
- [x] Canonical coverage points at the demonstrated maintained lane, drops unsupported legacy numeric scores, preserves limits, and generated methodology plus diff hygiene pass.

20261023 — `/validate` and `/mark-story-done`: checked-in fixture command `python driver.py --recipe configs/recipes/recipe-web-page-html-mvp.yaml --input-html testdata/static-html-mini.html --run-id triage-20261023-static-html-fixture-proof` exits0. Artifacts under `output/runs/triage-20261023-static-html-fixture-proof/`: `01_web_page_html_intake_v1/pages_html.jsonl`, `02_extract_page_numbers_html_v1/pages_html_with_page_numbers.jsonl`, `03_portionize_headings_html_v1/portions_non_toc.jsonl`, `04_build_chapter_html_v1/chapters_manifest.jsonl`, and `output/html/{manifest.json,chapter-001.html,provenance/blocks.jsonl}`. All five relevant schemas pass. Parent manually opened source/intake/portion/provenance and inspected the published chapter in the browser: one Harbor Field Guide chapter, source path exactly `testdata/static-html-mini.html`, raw_html byte-identical, ordered Compass/Field notebook and unordered Fresh water/Dry clothing lists, all nine table cells (Station/Depth (m)/Temperature (C); North Pier/8/12.4; Outer Reef/21/10.1), emphasis and expected link retained. H2s become chapter-internal h3s; no claim of exact arbitrary DOM heading-level preservation. Provenance is one `other` block with `source_page_number=1`, `source_original_page_number=1`, `source_element_ids=[p001-b1]`, and flattened quote containing both rows; no cell/list-item provenance claim. Browser tab and localhost server closed after inspection. Logs: `output/triage-20261023-static-html-audit/static-html-fixture-{proof,validation}.log`.

20261023 — coverage/closure: existing html-files row now points at `recipe-web-page-html-mvp.yaml` and the checked-in public synthetic fixture instead of legacy text passthrough. Removed the old passthrough1.0 score rather than fabricating a measured modern fidelity number; passing remains bounded, with explicit browser/CSS/linked-asset and cell/list-item provenance limits. No new recipe/code/runtime or broad support promotion. T0 verified local source/page binding; T1/T2 simplest existing deterministic path succeeds without inference; T3 literal values/markup inspected; T4 same checked-HTML line; T5 real artifacts and visible table/list inspected. All three continuation acceptance items met. Proportional checks are five driver artifact schemas, strict coverage JSON parse, methodology compile/check, and diff hygiene; existing code tests remain applicable because this slice changes only fixture/documented coverage. Story returns to Done. Continue the active triage goal; `/finish-and-push` requires a separate explicit landing request.


## October 23 continuation — main-wrapped block citations

20261023-1645 — /triage and /build-story plan under the standing autonomous goal. Fresh three neutral lane packets cover stories/architecture, inbox/health and evals. Main-thread facts are `output/triage-20261023-post-argon-facts.json`: graph clean,16 coverage rows, no due architecture domain, no newly actionable eval retry. The old Gemini3.5 inbox lead is not a new paid trigger. Argon comparison is closed. Top three actionable candidates: (1) repair main-wrapped block citations, (2) baseline the existing explicitly excluded merged-title/formula XLSX fixture under Story193, (3) make current coverage score authority explicit rather than list-position dependent under Story199. Choose (1): actual driver output from today's static-HTML fixture proves loss of paragraph-default citation granularity, whereas (2) needs a failure measurement and (3) has correct current values. The Ideal's broad real-OCR fidelity floor is still distant; current deterministic structural/provenance substrate can close this bounded concrete gap without inference.

Evidence: `_iter_provenance_tags` recursively handles article/section/div but not main. A local wrapper-equivalence probe returns heading/paragraph/two list_item/table descriptors under div/article/section and one flattened other record under main. ADR002 explicitly requires block-level citations with paragraph default; spec:3/6/7 owns source structure/export, category substrate exists. C3 climb benefits from faithful authored structure, no AI decision or new compromise. Keep this in Story200's existing checked-HTML/fixture/artifact contract, not a new entry permutation story. The shared builder is at risk: source descriptors and emitted block anchors must use the same traversal, table/figure units remain atomic, and existing content/links must remain unchanged.

Bounded primary-source check: https://html.spec.whatwg.org/multipage/grouping-content.html#the-main-element defines main as the dominant document contents with flow content; https://html.spec.whatwg.org/multipage/sections.html#the-article-element confirms the existing article container analogy. Adapt the existing recursive traversal for main, not a new DOM parser or semantic classifier. No header/footer/nav/aside generalization, table-cell anchors, boilerplate policy, custom-element semantics or schema change in this slice. A conservative container-text fallback is tightly coupled: recursion must not lose citation coverage when meaningful direct text exists outside child blocks. Keep such a container atomic rather than discard that text or invent paragraph markup; malformed/mixed content remains coarse. This is exact authored DOM traversal, so deterministic code fits; decision/LLM classification would add uncertainty and cost.

Plan and continuation acceptance:
- [x] Add a failing main-versus-supported-wrapper citation test covering heading/prose/list/table, source page/element identities and unchanged content; include unstructured/direct container text and comment controls.
- [x] Extend the shared provenance traversal for main while retaining atomic table/figure behavior and the existing coarse main anchor for unstructured text. Existing wrapper traversal and explicit child ownership remain unchanged. No HTML content mutation beyond existing ids.
- [x] Run focused builder/HTML consumer tests, lint, real maintained driver on the checked-in static and existing snapshot fixtures; validate schemas and manually inspect source data, block anchors, published HTML and visible output.
- [x] Correct current coverage provenance limits only as demonstrated, record exact artifacts/evidence, then /validate and /mark-story-done with generated graph/index and diff checks. No numerical quality claim, API calls, commit or push.


20261023-1651 — implementation/review correction: initial14-case baseline had8 failures, including six pre-existing unwrapped-text cases in div/article/section. The first broad coarse fallback passed local tests but independent semantic review demonstrated it swallowed a child figure's explicit page8/crop ownership and incorrectly attributed it to page7. Rejected that implementation before acceptance. Narrowed the text guard to the newly traversed main only; existing wrappers keep their prior recursion. The additional direct-text inventory gaps in existing wrappers are not repaired or promoted by this slice. Final11-case scope loaded the actual HEAD traversal in memory (no file mutation):2 main/source-identity regressions failed,9 controls passed. All11 pass on final code, including3 explicit page8/original43/crop-id preservation controls. Same-boundary main traversal and conservative retention only; no new semantic wrapper family or schema.

20261023-1651 — final real driver proof: after the last code correction and clearing builder pyc, `triage-20261023-html-citations-final-static`, `triage-20261023-html-citations-final-snapshot` and `triage-20261023-html-citations-final-mixed-text` each ran the maintained `recipe-web-page-html-mvp.yaml` through driver.py with exit0. All15 page/portion/chapter-manifest/bundle/provenance schema checks pass. Exact commands, source/builder digests, schemas and full inspected rows: `output/triage-20261023-static-html-audit/citation-final-driver-results.json`. Artifacts under each corresponding `output/runs/<run-id>/`: `01_web_page_html_intake_v1/pages_html.jsonl`, `03_portionize_headings_html_v1/portions_non_toc.jsonl`, `04_build_chapter_html_v1/chapters_manifest.jsonl`, `output/html/manifest.json`, `output/html/provenance/blocks.jsonl`, and `output/html/chapter-001.html`.

Parent manually opened all15 final provenance records: static fixture has11 rows instead of1 (four headings, two paragraphs, four list items and one table), synthetic source/original page1, stable p001-b1 through p001-b11, with usable HTML blk-chapter-001-0001 through0011 ids. Samples: Coastal Survey=p001-b3; Survey notes for the northern inlet.=p001-b4; Compass=p001-b6; Field notebook=p001-b7; Fresh water=p001-b8; Dry clothing=p001-b9; table=p001-b11. All nine cells remain Station/Depth(m)/Temperature(C), North Pier/8/12.4, Outer Reef/21/10.1; original emphasis and reference href survive. Raw HTML equals source bytes and local source path is exact. Existing Example Domain snapshot remains3 source-bound rows with its original source URL and complete prose. The mixed-text main control retains one coarse source-bound quote containing Before, Separate paragraph., After and inline text; no direct text is discarded. Final chapter browser/AX inspection shows all11 content anchors, complete list/table, emphasis and link with unchanged visible layout; no cell-level or arbitrary-HTML fidelity claim. Table/figure atomic units remain the established contract.

20261023 — /validate and /mark-story-done: final406 focused/consumer tests pass across new traversal, builder, checked-HTML route, manual navigation, literal fidelity, bundle contract and graphic-manual consumers; fresh make lint passes. Logs `provenance-scoped-baseline-tests.log` and `provenance-final-tests.log` distinguish rejected and accepted scope. Re-review found no material regression after narrowing. Coverage and fixture notes now describe11 structured main block anchors, atomic tables and coarse unstructured-main limits; no scores/defaults changed. Final source-note edits only describe verified scope; intake consumes neither supported_scope nor known_gaps, so they do not change the built data. Full broad suite is not rerun: these directly affected shared builder/contract consumers plus real driver/artifact checks cover this correction proportionally. /learning-review considered because of rejected broad fallback: existing bounded semantic review caught the ownership regression; no separate durable workflow change is proposed. T0 distinct source-bound units verified; T1 exact DOM boundaries stay deterministic; T2 failing maintained-contract baseline precedes repair; T3 source values/markup and explicit figure identities retained; T4 same builder/recipe/schema; T5 final artifacts and rendering inspected. All four continuation acceptance items met; graph/index and diff hygiene checked. Story returns to Done under standing authorization; no commit or push. Continue goal with fresh source-to-output triage; /finish-and-push requires explicit landing authorization. Latest strategic loop-review remains16:24UTC; carry the roughly30-minute/three-substantive-round cadence into the next pass.
