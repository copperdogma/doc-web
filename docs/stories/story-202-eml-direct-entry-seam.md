---
title: "Establish the First Honest EML Direct-Entry Seam"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #1 (Ingest), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Any format, any condition, Dossier-ready output, Transparency over magic"
spec_refs:
  - "spec:1"
  - "spec:1.1"
  - "spec:3"
  - "spec:3.1"
  - "spec:6"
  - "spec:7"
  - "spec:8"
  - "spec:9"
adr_refs:
  - "ADR-002"
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
  - "email-eml"
architecture_domains:
  - "doc_web_runtime"
roadmap_tags:
  - "campaign:maintained-intake-honesty"
legacy_system: ""
---

# Story 202 — Establish the First Honest EML Direct-Entry Seam

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/stories/story-194-office-intake-recommendation-and-handoff-boundary.md`, `docs/stories/story-197-establish-pptx-direct-entry-seam.md`, `docs/stories/story-200-web-page-direct-entry-seam.md`, `docs/stories/story-201-epub-direct-entry-seam.md`, `tests/fixtures/formats/_coverage-matrix.json`, `pyproject.toml`, `requirements.txt`, `modules/intake/intake_plan_utils.py`, `README.md`, `docs/RUNBOOK.md`, and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower email direct-entry ADR or runbook
**Depends On**: None

## Goal

`email-eml` is now the smallest untested single-document message family with verified native parser substrate in the current repo environment and reusable `doc-web` bundle patterns already on disk. The coverage matrix still marks `email-eml` untested, there is no maintained `--input-eml` / `input_eml` seam, no repo-owned `.eml` fixture, and no email recipe or bundle transform. This story should test the thinnest honest `.eml` slice first: add one repo-owned plain-text `.eml` fixture, measure a raw `partition_email(...)` baseline on it, and either land a bounded explicit-recipe direct-entry lane with fresh `driver.py` artifact proof or stop with a named blocker instead of leaving email as an unowned format claim. `email-mbox` and `mixed-archive` stay out of scope unless fresh substrate evidence makes them separate honest follow-ups.

## Acceptance Criteria

- [x] A fresh current-pass baseline named the exact `.eml` gap from repo evidence:
  - [x] the work log captures that `tests/fixtures/formats/_coverage-matrix.json` started this pass with `email-eml` marked `untested`
  - [x] the work log captures that `schemas.py` / `driver.py` started this pass with no `input_eml` / `--input-eml`
  - [x] the work log cites the verified absence of a maintained `.eml` recipe/module pair and repo-owned `.eml` fixture before implementation
  - [x] the work log records the native parser baseline already verified in this repo state: `unstructured.partition.email` is callable on a local temp `.eml` sample and emits structured elements with inspectable `subject`, `sent_from`, and `sent_to` metadata
- [x] The bounded native seam reached the accepted `doc-web` boundary and landed one honest maintained `.eml` direct-entry slice:
  - [x] one repo-owned bounded plain-text `.eml` fixture exists under `testdata/` with source metadata and capture notes recorded in `testdata/README.md`
  - [x] a maintained direct-entry recipe completes through `driver.py` on that fixture
  - [x] manual artifact inspection is recorded for the emitted `elements.jsonl`, bundle report, `output/html/manifest.json`, `output/html/provenance/blocks.jsonl`, and representative published HTML
- [x] `.eml` provenance stays source-honest on the claimed slice:
  - [x] the story records the actual anchor model exposed by the native parser and transform (pageless message structure with `source_element_ids` plus message metadata such as `subject`, `sent_from`, and `sent_to` where relevant)
  - [x] no fabricated printed-page guarantees or stronger archive/thread claims were introduced
  - [x] no new cross-artifact schema fields were required beyond the explicit `RunConfig.input_eml` / `driver.py` plumbing added before stamped outputs relied on the seam
- [x] Coverage, docs, and intake-boundary surfaces remain aligned with the outcome:
  - [x] `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, and `testdata/README.md` reflect the exact supported `.eml` slice rather than a vague email promise
  - [x] the direct-entry-only scope helpers and focused benchmark tests were updated so recommendation-only intake and approved handoff treat `email-eml` honestly
  - [x] `email-mbox` remains explicitly untested / out of scope because fresh current-pass substrate evidence still exposed no `mbox` parser/module
- [x] the seam crossed the accepted boundary honestly, validated cleanly, and closed without widening into a larger email/archive scope

## Out of Scope

- `email-mbox` bulk archives, multi-message threading, or mailbox-level provenance
- `.msg` parity, authenticated mailbox ingestion, or Gmail / connector-backed email workflows
- Attachment extraction or recursive ingestion of attached PDFs, images, Office files, or archives
- Multipart HTML cleanup, quoted-thread pruning, or signature stripping beyond what one bounded fixture proves is necessary
- Recommendation-only intake or approved-handoff automation expansion beyond explicit direct-entry scope reporting
- `mixed-archive` unpacking, ZIP routing, or cross-file-family archive orchestration

## Approach Evaluation

- **Simplification baseline**: first test whether one native `partition_email(...)` call on a repo-owned bounded `.eml` fixture plus a thin deterministic transform is already enough to reach the accepted `doc-web` boundary. Current repo evidence already shows this is plausible: a local temp `.eml` sample partitioned into four elements (`Text`, `NarrativeText`, `Text`, `Title`) with `subject`, `sent_from`, and `sent_to` metadata in this checkout.
- **AI-only**: low-value default. A single LLM call could restate or normalize the message body, but it would throw away the native parser's structure and header metadata before the repo has even measured whether the native seam already clears the bounded slice.
- **Hybrid**: plausible only if the native `.eml` element stream is close but still needs bounded cleanup, such as subject/body entry shaping or quoted-thread exclusion on the chosen fixture. In that case, keep native parsing and metadata as the backbone and use AI only for the smallest inspectable repair step.
- **Pure code**: likely strongest for the first slice. The main work is direct-entry plumbing, fixture ownership, unstructured-element serialization, and a thin bundle/provenance transform. No language understanding beyond the native parser is currently justified by repo evidence.
- **Repo constraints / prior decisions**: `spec:1.1` keeps the recipe surface explicit, `spec:7` keeps the accepted `doc-web` bundle/provenance boundary versioned and inspectable, Story 194 deliberately kept recommendation-only intake and approved handoff narrower than direct-entry lanes, and ADR-002 says new families should land through the accepted `doc-web` boundary rather than through parallel output contracts. No narrower email-specific ADR or runbook was found.
- **Existing patterns to reuse**: `modules/extract/unstructured_docx_intake_v1/main.py`, `modules/extract/unstructured_pptx_intake_v1/main.py`, `modules/transform/docx_elements_to_bundle_v1/main.py`, `modules/transform/pptx_elements_to_bundle_v1/main.py`, `modules/common/office_native_bundle.py`, `modules/intake/unstructured_pdf_intake_v1/main.py` (`serialize_element`), `modules/intake/intake_plan_utils.py`, `benchmarks/scripts/intake_scope.py`, `tests/test_pptx_intake_recipe.py`, `tests/test_web_page_intake_recipe.py`, and the direct-entry pattern established in Stories 197, 200, and 201.
- **Eval**: the deciding proof surface is a fresh `driver.py` run on one repo-owned `.eml` fixture plus manual inspection of the emitted bundle/provenance artifacts. If a maintained direct-entry recipe lands, focused scope tests should also prove `email-eml` is represented honestly as direct-entry-only outside recommendation-only intake and approved handoff.

## Tasks

- [x] Freeze the current `.eml` seam from repo reality before changing code:
  - [x] verify the `email-eml` coverage row is still `untested`
  - [x] verify `schemas.py` / `driver.py` still have no `input_eml` / `--input-eml`
  - [x] verify there is still no maintained `.eml` recipe/module pair or checked-in `.eml` fixture
  - [x] record the current native substrate split honestly: `unstructured.partition.email` is callable in this environment, while no `mbox` parser/module or direct-entry runtime seam is currently verified
  - [x] record the install-surface gap honestly: `pip install .[driver]` does not install `unstructured`, so the maintained `.eml` seam needs an explicit documented dependency path
- [x] Add one repo-owned reproducible `.eml` fixture:
  - [x] check in one bounded plain-text `.eml` message plus source metadata under `testdata/`
  - [x] record how the fixture was generated or captured in `testdata/README.md`
  - [x] keep future tests and reruns independent of live inbox, connector, or network access
- [x] Measure the smallest honest native baseline before adding cleanup logic:
  - [x] run a raw `partition_email(...)` probe on the checked-in fixture and inspect the emitted element metadata
  - [x] verify whether the maintained install surface should add an `email` extra backed by bare `unstructured==0.16.9` instead of a nonexistent upstream `unstructured[email]` extra
  - [x] determine whether the existing bundle helper can support the claimed slice or whether a thin email-specific transform is required
  - [x] record the exact artifact paths and failure modes inspected for that before-state
- [x] If the bounded direct-entry seam is viable, land the smallest coherent `.eml` lane:
  - [x] add `input_eml` support in `schemas.py` / `driver.py`
  - [x] add `configs/recipes/recipe-email-eml-html-mvp.yaml`
  - [x] add an `.eml` intake module and the smallest honest bundle/provenance transform, reusing existing helpers where possible
  - [x] ensure the transform preserves message metadata and pageless provenance honestly instead of fabricating page anchors
- [x] Add focused fixture-backed coverage for the new seam:
  - [x] a direct-entry smoke test that runs `driver.py` on the checked-in `.eml` fixture and asserts bundle/provenance outputs
  - [x] add isolated install-contract smoke coverage similar to the existing DOCX/PPTX/EPUB checks
  - [x] update the intake-scope helper tests and focused benchmark-surface tests so `email-eml` is treated explicitly as direct-entry-only
- [x] Run real `driver.py` verification and artifact inspection if the lane lands:
  - [x] clear stale `*.pyc`
  - [x] run the maintained recipe through `driver.py`
  - [x] verify artifacts exist in `output/runs/`
  - [x] manually inspect sample JSON/JSONL and published HTML data
- [x] If this story changes documented format coverage or graduation reality: update `tests/fixtures/formats/_coverage-matrix.json` and any relevant methodology state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [x] If agent tooling changed: not applicable; no agent tooling changed
- [x] If evals or goldens changed: not applicable; no eval or golden files changed
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every support claim traces to the fixture path, run ID, message metadata, and inspected provenance rows
  - [x] T1 — AI-First: no AI was added because the native `.eml` parser and current bundle patterns already solve the bounded slice
  - [x] T2 — Eval Before Build: the raw `partition_email(...)` baseline was measured before adding new runtime logic
  - [x] T3 — Fidelity: message body and header metadata survive extraction without silent loss or fabricated page claims
  - [x] T4 — Modular: the explicit-recipe direct-entry pattern was extended instead of inventing a parallel email runtime
  - [x] T5 — Inspect Artifacts: emitted `.eml` bundle/provenance outputs were manually inspected, not just parser import success or test logs

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

- **Owning module / area**: direct email-native intake plus the accepted `doc-web` bundle/provenance boundary for pageless structured sources. Ownership should mirror the current DOCX/PPTX/EPUB direct-entry seams rather than the recommendation-only intake automation.
- **Methodology reality**: this belongs to `spec:1`, `spec:3`, `spec:6`, `spec:7`, `spec:8`, and `spec:9`. In `docs/methodology/state.yaml`, `spec:1`, `spec:3`, `spec:6`, `spec:8`, and `spec:9` substrates exist, `spec:7` is still `partial`, and the relevant phases are `C2 = climb`, `C3 = climb`, `B10 = climb`, and `B1 = hold`. The relevant coverage row now moves to bounded `passing` on the first maintained plain-text `.eml` slice; `email-mbox` remains a separate untested archive family.
- **Substrate evidence**: fresh current-pass implementation evidence now exists in code, tests, and artifacts. `pyproject.toml` exposes an explicit `email` extra backed by `unstructured==0.16.9`; `schemas.py` / `driver.py` now expose `input_eml` / `--input-eml`; `modules/intake/intake_plan_utils.py` and `benchmarks/scripts/intake_scope.py` classify `email-eml` as direct-entry-only alongside the other explicit lanes; `configs/recipes/recipe-email-eml-html-mvp.yaml` plus `modules/extract/unstructured_email_intake_v1` and `modules/transform/email_elements_to_bundle_v1` now provide the maintained direct-entry seam; and the real proof run `output/runs/story202-eml-proof/` shows the accepted `doc-web` boundary on the checked-in fixture. Package discovery still exposes no `mbox` parser/module, so the story remains intentionally bounded to plain-text `.eml`.
- **Data contracts / schemas**: likely touched contracts are `RunConfig` in `schemas.py`, `unstructured_element_v1`, `doc_web_bundle_manifest_v1`, and `doc_web_provenance_block_v1`. If message metadata such as `subject`, `sent_from`, or `sent_to` must cross artifact boundaries beyond the unstructured element stream or final report, add those fields explicitly to the relevant schema before stamped outputs rely on them.
- **File sizes**: likely touch points are `pyproject.toml` (48 lines), `requirements.txt` (10), `schemas.py` (1240), `driver.py` (2325), `modules/intake/intake_plan_utils.py` (310), `benchmarks/scripts/intake_scope.py` (47), `benchmarks/scripts/run_auto_book_type_detection_eval.py` (221), `benchmarks/scripts/run_approved_intake_handoff_eval.py` (341), `tests/test_doc_web_cli_contract.py` (535), `tests/test_run_config.py` (53), `tests/test_intake_plan_utils.py` (271), `tests/test_auto_book_type_detection_benchmark.py` (76), `tests/test_approved_intake_handoff_benchmark.py` (169), `README.md` (383), `docs/RUNBOOK.md` (627), `testdata/README.md` (116), and `tests/fixtures/formats/_coverage-matrix.json` (512). Oversized files to keep especially surgical are `schemas.py`, `driver.py`, `tests/test_doc_web_cli_contract.py`, `docs/RUNBOOK.md`, and `tests/fixtures/formats/_coverage-matrix.json`.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, Stories 194/197/200/201, `tests/fixtures/formats/_coverage-matrix.json`, `pyproject.toml`, `requirements.txt`, `modules/intake/intake_plan_utils.py`, `README.md`, and `docs/RUNBOOK.md`. No narrower email-specific ADR, runbook, scout, or note was found after search.

## Files to Modify

- `pyproject.toml` — add a maintained email optional dependency path only if the native `.eml` seam needs one beyond the existing pinned `unstructured` surface (48 lines)
- `requirements.txt` — keep the documented install truth aligned if email direct-entry support changes the maintained dependency surface (10 lines)
- `schemas.py` — add `input_eml` to `RunConfig` if a maintained `.eml` direct-entry lane lands (1240 lines)
- `driver.py` — add `--input-eml` plumbing and recipe input override handling if the lane becomes maintained (2325 lines)
- `configs/recipes/recipe-email-eml-html-mvp.yaml` — maintained bounded `.eml` direct-entry recipe reusing the accepted `doc-web` bundle/provenance boundary (new file)
- `modules/extract/unstructured_email_intake_v1/main.py` and `modules/extract/unstructured_email_intake_v1/module.yaml` — `.eml`-native intake module patterned after the existing Unstructured direct-entry seams (new files)
- `modules/transform/email_elements_to_bundle_v1/main.py` and `modules/transform/email_elements_to_bundle_v1/module.yaml` — `.eml` bundle/provenance transform or the smallest honest generalization of the current helper pattern (new files)
- `modules/common/office_native_bundle.py` — extend only if the current helper is honestly the shared home for `.eml` bundle rendering/provenance (375 lines)
- `tests/test_run_config.py` — add `input_eml` config coverage if the RunConfig surface grows (53 lines)
- `tests/test_email_intake_recipe.py` — focused `.eml` direct-entry smoke coverage on the checked-in fixture (new file)
- `tests/test_doc_web_cli_contract.py` — add isolated install/smoke coverage only if a maintained email extra lands (535 lines)
- `modules/intake/intake_plan_utils.py` — add `email-eml` to the direct-entry-only boundary table only if a maintained `.eml` recipe lands and the confirmed-handoff helper should classify it explicitly (310 lines)
- `benchmarks/scripts/intake_scope.py` — extend direct-entry-only scope handling if `email-eml` joins that boundary class (47 lines)
- `tests/test_auto_book_type_detection_benchmark.py` — keep recommendation-only boundary truth aligned if `email-eml` becomes explicit direct-entry-only scope (76 lines)
- `tests/test_approved_intake_handoff_benchmark.py` — keep approved-handoff boundary truth aligned if `email-eml` becomes explicit direct-entry-only scope (169 lines)
- `testdata/email-eml-mini.eml` / `testdata/email-eml-mini.source.json` — repo-owned bounded `.eml` fixture and provenance metadata for the first maintained slice (new files)
- `testdata/README.md` — record fixture source, generation/capture note, and maintained scope (116 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — move the `email-eml` row only as far as fresh evidence justifies (512 lines)
- `README.md` — align user-facing format support wording with the actual `.eml` seam (383 lines)
- `docs/RUNBOOK.md` — publish the verified bounded `.eml` direct-entry command or the blocker if the seam cannot land (627 lines)

## Redundancy / Removal Targets

- stale `email-eml` `untested` wording in coverage/docs once a maintained direct-entry slice exists
- any ad hoc local `.eml` probe commands or notes that become redundant after a maintained recipe/test lane lands
- any temptation to widen the same story into `email-mbox`, attachment extraction, or mixed-archive routing instead of keeping those as separate future seams if needed

## Notes

- New story justification: it would not be honest to reopen Story 191 or recycle Story 201. Story 191 is an OCR-capability blocker on handwritten images/PDFs, not an email direct-entry seam, and Story 201 already closed the EPUB-specific slice. `.eml` is a different input family with different fixture, metadata, and provenance rules.
- The existing explicit-recipe operator surface is already the honest first slice here. Recommendation-only intake and approved handoff should change only enough to represent the direct-entry boundary truthfully if a maintained `.eml` lane lands.
- Exploration result folded into scope: the first maintained slice should stay strictly plain-text `.eml`. Current parser and bundle probes already succeed there, so widening to multipart HTML, quoted-thread cleanup, or attachment handling would add blast radius without improving the first honest coverage claim.

## Plan

Alignment check:
- This story still moves toward `docs/ideal.md` rather than polishing a dead-end compromise: it widens explicit format coverage one bounded family at a time under `spec:1.1` / `C2`, keeps the accepted `doc-web` bundle/provenance contract as the output bar under `spec:6` / `spec:7` and ADR-002, and preserves inspectable boundary truth for automation surfaces under `spec:8` / `spec:9`.
- No conflicting narrower ADR or runbook was found after the fresh search in this pass.

Measured baseline from this `/build-story` exploration pass:
- **Current repo direct-entry runtime baseline: 0/1 passing.** `email-eml` is still `untested` in the coverage matrix; `schemas.py` and `driver.py` expose direct-entry overrides for `docx`, `xlsx`, `pptx`, `epub`, and `html`, but not for `.eml`; `modules/intake/intake_plan_utils.py` currently treats only `docx`, `epub`, `pptx`, `web-page`, and `xlsx` as direct-entry-only families; and there is no maintained `.eml` recipe, intake module, transform, or repo-owned `.eml` fixture.
- **Native parser baseline in current repo environment: 1/1 passing.** A temp plain-text `.eml` sample partitioned successfully through `unstructured.partition.email` into four structured elements (`Text`, `NarrativeText`, `Text`, `Title`) with inspectable `subject`, `sent_from`, and `sent_to` metadata.
- **Install-surface baseline: 0/1 for `.[driver]`, 1/1 for bare `unstructured`.** A clean temp venv with `pip install .[driver]` did not install `unstructured` at all, so the current package surface cannot support `.eml` yet. A separate clean temp venv with `pip install unstructured==0.16.9` successfully imported `partition_email`, and installed metadata shows upstream provides no `email` extra. That means a maintained `.eml` seam likely needs a new repo-local `email` extra backed by the base `unstructured==0.16.9` pin rather than `unstructured[email]`.
- **Existing bundle-helper baseline: 1/1 passing.** A temp probe that serialized the email elements and called `modules.common.office_native_bundle.write_bundle(...)` with one page entry produced a valid one-entry HTML bundle with four provenance rows and the expected body text. This proves the shared bundle/provenance helper is already sufficient for the bounded message slice.
- **Existing transform reuse baseline: 0/1 passing.** Running `modules/transform/docx_elements_to_bundle_v1/main.py` on the same serialized email elements with a document-title override completed, but it titled the single entry `Alice` (from the signature `Title`) instead of the message subject. That is enough evidence that the first slice needs a thin email-specific transform even though it can still reuse the shared bundle helper.
- **Scope boundary baseline: 0/1 for `mbox`.** Package discovery in the current environment exposed `unstructured.partition.email` and `unstructured.partition.msg`, but no `mbox` parser/module. `email-mbox` therefore remains out of scope for this story.

Approach choice after the fresh baseline:
- **AI-only** remains the wrong first move. The parser and helper substrate already handle the bounded plain-text `.eml` slice, so an LLM would only add cost and hide inspectable message metadata.
- **Hybrid** is not needed for the first slice. Nothing in the baseline suggests quoted-thread cleanup or richer normalization is required on the plain-text probe.
- **Pure code + native `partition_email(...)`** is the simplest honest path: own the missing install/direct-entry plumbing, add one repo-owned plain-text fixture, and add a thin email-specific transform that derives the document and entry title from message metadata while keeping provenance pageless.

Implementation order:
1. Repo-owned fixture + baseline capture (`XS`)
   - Files: `testdata/email-eml-mini.eml`, `testdata/email-eml-mini.source.json`, `testdata/README.md`, and this story work log.
   - Change: check in one plain-text `.eml` probe with source/generation metadata, then rerun the raw `partition_email(...)` baseline on that exact fixture so the story stops depending on a temp sample.
   - Impact/risk: no runtime risk; this freezes the maintained slice and keeps `email-mbox`, multipart HTML, and attachments out of scope.
   - Done looks like: the fixture is repo-owned, documented, and the work log cites the exact raw parser output shape.
2. Direct-entry install + driver plumbing (`S`)
   - Files: `pyproject.toml`, `requirements.txt` if needed for truth alignment, `schemas.py`, `driver.py`, and `tests/test_run_config.py`.
   - Change: add a repo-local `email` extra pinned to bare `unstructured==0.16.9`, add `input_eml` / `--input-eml`, and keep the override wiring parallel to the existing DOCX/PPTX/EPUB/HTML seams.
   - Impact/risk: touches the oversized config/runtime files `schemas.py` and `driver.py`; keep edits surgical and reuse the existing direct-entry override pattern exactly.
   - Done looks like: `RunConfig` accepts `input_eml`, `driver.py` applies the override cleanly, and the install truth is explicit instead of relying on transitive luck from unrelated extras.
3. Email-native intake + thin bundle transform (`S`)
   - Files: `configs/recipes/recipe-email-eml-html-mvp.yaml`, `modules/extract/unstructured_email_intake_v1/main.py`, `modules/extract/unstructured_email_intake_v1/module.yaml`, `modules/transform/email_elements_to_bundle_v1/main.py`, `modules/transform/email_elements_to_bundle_v1/module.yaml`, and possibly `modules/common/office_native_bundle.py` only if a tiny helper extraction meaningfully reduces duplication.
   - Change: follow the existing unstructured direct-entry intake pattern, reuse `serialize_element(...)`, and write a small transform that:
     - derives document title from `subject`,
     - emits one bounded entry,
     - keeps `source_pages` empty to avoid fabricated page anchors,
     - preserves source element IDs and message metadata honestly,
     - reuses `write_bundle(...)` rather than inventing a new bundle subsystem.
   - Impact/risk: the main risk is over-reusing the DOCX transform and inheriting the wrong title semantics; avoid that by owning the subject-based naming in the new email transform.
   - Done looks like: the recipe writes `elements.jsonl`, a bundle report, `output/html/manifest.json`, `output/html/provenance/blocks.jsonl`, and one representative HTML page on the `.eml` fixture.
4. Tests and truth-surface alignment (`S`)
   - Files: `tests/test_email_intake_recipe.py`, `tests/test_doc_web_cli_contract.py`, `modules/intake/intake_plan_utils.py`, `tests/test_intake_plan_utils.py`, `benchmarks/scripts/intake_scope.py`, `tests/test_auto_book_type_detection_benchmark.py`, `tests/test_approved_intake_handoff_benchmark.py`, `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, and `docs/RUNBOOK.md`.
   - Small scope expansion already folded in: if `.eml` lands, add `email-eml` to the direct-entry-only boundary surfaces so confirmed-handoff/intake-scope reporting stays honest instead of continuing to look unsupported by omission.
   - Change: add one recipe smoke, one install-contract smoke for the new `email` extra, and boundary-truth updates so automation surfaces say `direct_explicit_recipe_only` for `email-eml`.
   - Impact/risk: no product-runtime risk beyond documentation/test drift, but multiple truth surfaces must move in one pass to avoid the same stale-boundary residue Story 194 cleaned up for office lanes.
   - Done looks like: tests encode the supported slice, docs match the new explicit-recipe boundary, and the coverage row moves from `untested` to a bounded `passing` claim only if the real driver proof succeeds.
5. Real-run verification and closeout prep (`S`)
   - Files: no new owner files beyond the touched implementation/docs/test set; work lands through the story work log and task checkboxes.
   - Change: clear stale `*.pyc`, run the narrow real `driver.py` proof on the repo-owned `.eml` fixture, validate the emitted bundle/provenance artifacts, manually inspect the HTML and JSON/JSONL outputs, then run the touched test/lint surface.
   - Impact/risk: if the real run reveals missing metadata or title/body regressions, stop and fix inside the same story rather than leaving a half-claimed coverage row.
   - Done looks like: the story can stay `In Progress` with `Build complete` checked and a clean handoff to `/validate`.

Structural health notes:
- Oversized files at risk: `schemas.py` (1240), `driver.py` (2325), `tests/test_doc_web_cli_contract.py` (535), `docs/RUNBOOK.md` (627), and `tests/fixtures/formats/_coverage-matrix.json` (512). Keep those edits small and pattern-matched to existing direct-entry seams.
- No schema-boundary blocker is visible yet. `unstructured_element_v1`, `doc_web_bundle_manifest_v1`, and `doc_web_provenance_block_v1` are sufficient for the bounded plain-text slice if we keep the final artifact pageless.
- No large scope expansion is recommended. The honest first slice is plain-text `.eml`; multipart HTML, attachments, `msg`, `mbox`, and mixed archives remain separate lines.

Human-approval blockers:
- None if you want the bounded plain-text `.eml` slice only.
- If you want the first slice to include multipart HTML normalization, attachment handling, or `mbox`, that is a larger expansion and I would recommend keeping it out of Story 202.

## Work Log

20260409-0954 — create-story: created Story 202 after `/triage` found no actionable `In Progress`, `Pending`, or `Draft` line beyond blocked Story 191 and the user approved the next action to package the first honest `.eml` seam. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, Stories 194/197/200/201, `tests/fixtures/formats/_coverage-matrix.json`, `pyproject.toml`, `requirements.txt`, `modules/intake/intake_plan_utils.py`, `README.md`, and `docs/RUNBOOK.md`. Fresh substrate evidence: `email-eml` remains `untested`; `schemas.py` / `driver.py` currently expose no `input_eml` / `--input-eml`; there is no maintained `.eml` recipe/module pair or repo-owned fixture; `unstructured.partition.email` and `unstructured.partition.msg` import in this checkout; a temp `.eml` sample partitioned successfully into four elements with `subject`, `sent_from`, and `sent_to` metadata; and no comparable `mbox` module was discovered. Result: a new `Pending` story is honest because the parser and bundle substrate already exist while the missing work is the bounded direct-entry seam itself. Next step: `/build-story` should freeze the repo-owned fixture, verify install truth, and decide whether a thin email-specific transform is required beyond the current helper pattern.
20260409-1010 — /build-story explore + plan: verified that Story 202 remains honestly buildable and narrowed the first slice to plain-text `.eml` only. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, Stories 194/197/201, `tests/fixtures/formats/_coverage-matrix.json`, `pyproject.toml`, `requirements.txt`, `schemas.py`, `driver.py`, `modules/intake/intake_plan_utils.py`, `benchmarks/scripts/intake_scope.py`, `tests/test_intake_plan_utils.py`, `modules/common/office_native_bundle.py`, `modules/extract/unstructured_docx_intake_v1/main.py`, `modules/extract/unstructured_pptx_intake_v1/main.py`, `modules/transform/docx_elements_to_bundle_v1/main.py`, `modules/transform/pptx_elements_to_bundle_v1/main.py`, `tests/test_pptx_intake_recipe.py`, `tests/test_web_page_intake_recipe.py`, `README.md`, and `docs/RUNBOOK.md`. Fresh measured baseline: `email-eml` is still `untested`; `driver.py`/`RunConfig` still expose no `.eml` override; `.[driver]` in a clean temp venv installs no `unstructured`; bare `unstructured==0.16.9` in a clean temp venv does expose `partition_email`; installed metadata shows no upstream `email` extra; a temp `.eml` sample partitioned into four elements with message metadata; `write_bundle(...)` already emitted a valid one-entry pageless HTML bundle from those serialized elements; and reusing `docx_elements_to_bundle_v1` unchanged gave the wrong entry title (`Alice`) even with a subject override, which is enough evidence that a thin email-specific transform is required. Package/module discovery still exposed no `mbox` parser, so `email-mbox` stays out of scope. Files likely to change and files at risk are captured in the plan above; main risk is oversized config/runtime truth surfaces (`schemas.py`, `driver.py`, `tests/test_doc_web_cli_contract.py`, `docs/RUNBOOK.md`, coverage matrix) rather than missing runtime substrate. Potential redundancy to remove later: stale `email-eml` untested wording and any ad hoc local probe notes once the maintained recipe/test lane exists. Next step: wait for user approval, then move Story 202 to `In Progress` and implement the bounded plain-text `.eml` seam.
20260409-1028 — implement pass started: user approved the bounded plain-text `.eml` seam, so Story 202 moved to `In Progress` before runtime edits. Re-read the existing direct-entry patterns in `pyproject.toml`, `schemas.py`, `driver.py`, `modules/intake/intake_plan_utils.py`, `benchmarks/scripts/intake_scope.py`, `tests/test_run_config.py`, `tests/test_doc_web_cli_contract.py`, `tests/test_intake_plan_utils.py`, `tests/test_auto_book_type_detection_benchmark.py`, `tests/test_approved_intake_handoff_benchmark.py`, `testdata/README.md`, `configs/recipes/recipe-epub-html-mvp.yaml`, `modules/extract/unstructured_epub_intake_v1/module.yaml`, and `modules/transform/epub_elements_to_bundle_v1/{main.py,module.yaml}` to keep the `.eml` seam pattern-matched to current DOCX/PPTX/EPUB wiring. Fresh implementation constraint confirmed in this pass: `requirements.txt` already brings in base `unstructured==0.16.9`, but `pyproject.toml` still lacks a repo-exposed email-capable extra, so the packaging truth will need to be made explicit instead of assuming transitive coverage from `requirements.txt`. Next step: recompile methodology with the `In Progress` status, then add fixture, runtime plumbing, native intake/transform modules, and direct-entry boundary updates in one coherent pass.
20260409-1638 — build complete: landed the bounded plain-text `.eml` seam and verified it end-to-end. Code/runtime changes: added the repo-owned fixture pair `testdata/email-eml-mini.eml` and `testdata/email-eml-mini.source.json`; added `pyproject.toml` `email` extra backed by `unstructured==0.16.9`; added `RunConfig.input_eml` plus `driver.py` `--input-eml` override wiring and extract/intake argument plumbing; added `configs/recipes/recipe-email-eml-html-mvp.yaml`; added `modules/extract/unstructured_email_intake_v1` with raw-metadata normalization so `subject`, `sent_from`, and `sent_to` survive as inspectable JSON primitives; added `modules/transform/email_elements_to_bundle_v1` to derive document title from the message subject, downgrade parser-emitted `Title` body blocks to narrative text, and emit report-side `message_metadata` / `anchor_model`; updated direct-entry-only boundary helpers and tests for `email-eml`; and updated `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, and `testdata/README.md` to describe the exact supported slice. Fresh verification in this pass: `python -m pytest tests/test_run_config.py tests/test_intake_plan_utils.py tests/test_auto_book_type_detection_benchmark.py tests/test_approved_intake_handoff_benchmark.py tests/test_email_intake_recipe.py -q` passed; `python -m pytest tests/test_doc_web_cli_contract.py -q -k email_extra_supports_repo_owned_eml_smoke` passed in a fresh venv; `git diff --check` passed; `make lint` passed; and `make test` passed with `511 passed, 4 warnings in 669.67s`. Real driver proof: `find modules/extract/unstructured_email_intake_v1 modules/transform/email_elements_to_bundle_v1 -name "*.pyc" -delete` then `python driver.py --recipe configs/recipes/recipe-email-eml-html-mvp.yaml --input-eml testdata/email-eml-mini.eml --run-id story202-eml-proof --allow-run-id-reuse --force` completed successfully. Manual artifact inspection recorded on `output/runs/story202-eml-proof/01_unstructured_email_intake_v1/elements.jsonl`, `output/runs/story202-eml-proof/02_email_elements_to_bundle_v1/email_bundle_report.json`, `output/runs/story202-eml-proof/output/html/manifest.json`, `output/runs/story202-eml-proof/output/html/provenance/blocks.jsonl`, and `output/runs/story202-eml-proof/output/html/page-001.html`: first element row carries `subject = "Fixture Subject"`, `sent_from = ["Alice Example <alice@example.com>"]`, and `sent_to = ["Bob Example <bob@example.com>"]`; the bundle report exposes the same `message_metadata` plus `anchor_model = {"source_pages": "none", "provenance": "source_element_ids"}`; the manifest title is `Fixture Subject` with creator `Alice Example <alice@example.com>` and `reading_order = ["page-001"]`; the provenance rows carry four `source_element_ids` with no `source_page_number`; and the published HTML renders the message body as four paragraphs (`Hello Bob,`, the core proof sentence, `Regards,`, `Alice`) without fabricating headings or printed-page anchors. Residual scope truth: `email-mbox`, multipart HTML emails, quoted-thread cleanup, attachments, `.msg`, and broader mailbox/thread ownership remain explicitly out of scope for this story. Next step: `/validate`, then `/mark-story-done` if no new issues surface.
20260409-1304 — `/mark-story-done` close-out completed. Fresh completion evidence in this close-out sequence used the immediately preceding `/validate` pass plus regenerated methodology surfaces on the post-close-out story metadata: `make test` passed with `511 passed, 4 warnings`, `make lint` passed, `make methodology-check` passed, `git diff --check` passed, and `python driver.py --recipe configs/recipes/recipe-email-eml-html-mvp.yaml --input-eml testdata/email-eml-mini.eml --run-id validate-story202-eml --allow-run-id-reuse --force` produced the validated `.eml` bundle outputs with manual inspection on `output/runs/validate-story202-eml/01_unstructured_email_intake_v1/elements.jsonl`, `output/runs/validate-story202-eml/02_email_elements_to_bundle_v1/email_bundle_report.json`, `output/runs/validate-story202-eml/output/html/manifest.json`, `output/runs/validate-story202-eml/output/html/provenance/blocks.jsonl`, and `output/runs/validate-story202-eml/output/html/page-001.html`. Minor close-out fix applied during this step: frontmatter now cites ADR-002 so the generated methodology graph records the decision alignment already described in the story body. Story 202 is now closed as the first honest bounded plain-text `.eml` direct-entry seam; remaining email families (`email-mbox`, `.msg`, attachments, multipart HTML, mailbox/thread ownership) stay explicit follow-up scope rather than hidden residual debt. Next step: `/check-in-diff`.
