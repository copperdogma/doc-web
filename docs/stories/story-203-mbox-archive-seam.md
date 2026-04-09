---
title: "Establish the First Honest MBOX Archive Seam"
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
depends_on:
  - "202"
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
  - "email-mbox"
architecture_domains:
  - "doc_web_runtime"
roadmap_tags:
  - "campaign:maintained-intake-honesty"
legacy_system: ""
---

# Story 203 — Establish the First Honest MBOX Archive Seam

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/stories/story-194-office-intake-recommendation-and-handoff-boundary.md`, `docs/stories/story-202-eml-direct-entry-seam.md`, `tests/fixtures/formats/_coverage-matrix.json`, `modules/extract/unstructured_email_intake_v1/main.py`, `modules/transform/email_elements_to_bundle_v1/main.py`, `modules/intake/intake_plan_utils.py`, `README.md`, `docs/RUNBOOK.md`, and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower `.mbox`-specific ADR or runbook
**Depends On**: Story 202

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

`email-mbox` is now the smallest remaining email-family coverage gap after Story 202 established the first honest plain-text `.eml` seam. The coverage matrix still marks `.mbox` archives `untested`, there is no maintained `input_mbox` / `--input-mbox` runtime seam, no repo-owned `.mbox` fixture, and no archive transform that can turn multiple pageless messages into an inspectable `doc-web` bundle. This story should test the thinnest honest archive slice first: one repo-owned multi-message `.mbox` fixture, stdlib `mailbox.mbox` splitting plus the existing `partition_email(...)` substrate, and either a bounded explicit-recipe direct-entry lane with fresh `driver.py` artifact proof or a named blocker instead of silently widening the email claim.

## Acceptance Criteria

- [x] A fresh current-pass baseline names the exact `.mbox` gap from repo evidence:
  - [x] the work log captures that `tests/fixtures/formats/_coverage-matrix.json` starts this pass with `email-mbox` marked `untested`
  - [x] the work log captures that `schemas.py` / `driver.py` currently expose no `input_mbox` / `--input-mbox`
  - [x] the work log cites the verified absence of a maintained `.mbox` recipe/module pair and repo-owned `.mbox` fixture before implementation
  - [x] the work log records the current substrate split honestly: stdlib `mailbox.mbox` works in this checkout, `unstructured.partition.email.partition_email` is callable for per-message parsing, and no dedicated `.mbox` parser/module or maintained runtime seam currently exists
- [x] The bounded archive seam reaches the accepted `doc-web` boundary and lands one honest maintained `.mbox` direct-entry slice:
  - [x] one repo-owned bounded multi-message `.mbox` fixture exists under `testdata/` with source metadata and capture/generation notes in `testdata/README.md`
  - [x] a maintained direct-entry recipe completes through `driver.py` on that fixture
  - [x] the final bundle publishes one HTML entry per message in archive order on the bounded fixture instead of collapsing the archive into one document page
  - [x] manual artifact inspection is recorded for the emitted intake artifact, bundle report, `output/html/manifest.json`, `output/html/provenance/blocks.jsonl`, and representative published HTML entry pages
- [x] `.mbox` provenance stays source-honest on the claimed slice:
  - [x] message ordering and message-level metadata remain inspectable in the resulting artifacts
  - [x] no fabricated printed-page, mailbox-thread, or attachment-native guarantees are introduced
  - [x] no new cross-artifact schema fields are relied on without being added explicitly to the relevant schema first
- [x] Coverage, docs, and intake-boundary surfaces remain aligned with the outcome:
  - [x] `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, and `testdata/README.md` reflect the exact supported `.mbox` slice rather than a vague mailbox promise
  - [x] if the lane lands, direct-entry-only scope helpers and focused benchmark tests treat `email-mbox` honestly
  - [x] `mixed-archive`, attachment extraction, quoted-thread cleanup, `.msg`, and mailbox connector workflows remain explicitly out of scope unless fresh evidence justifies separate follow-up work

## Out of Scope

- Gmail, mailbox connector, or authenticated inbox workflows
- Attachment extraction, recursive ingestion of attached files, or multipart archive handling
- Thread reconstruction, quoted-thread cleanup, deduplication across replies, or mailbox graph semantics
- `.msg` parity or any claim that one email-family parser automatically proves another
- `mixed-archive` unpacking, ZIP routing, or cross-family archive orchestration
- Recommendation-only intake or approved-handoff automation expansion beyond explicit direct-entry scope reporting

## Approach Evaluation

- **Simplification baseline**: first test whether stdlib `mailbox.mbox` iteration plus the existing `partition_email(file=...)` surface and thin deterministic multi-entry bundling already clears the bounded slice. Fresh current-pass evidence says this is plausible: `mailbox.mbox` works locally, and `partition_email` in this checkout accepts `filename` or `file` input.
- **AI-only**: low-value default. An LLM could summarize or normalize messages, but it would weaken inspectable header/body provenance before the repo has even measured whether the native archive split plus current email parser already solves the bounded slice.
- **Hybrid**: only justified if the native path is close but still needs bounded cleanup such as subject/body shaping, quoted-thread exclusion, or message-title normalization on the checked-in fixture. If needed, keep stdlib archive splitting and Unstructured parsing as the backbone and use AI only for the smallest inspectable repair step.
- **Pure code**: likely strongest for the first slice. The core work is archive splitting, direct-entry plumbing, fixture ownership, deterministic per-message shaping, and multi-entry bundle/provenance output.
- **Repo constraints / prior decisions**: `spec:1.1` keeps the recipe surface explicit, `spec:7` keeps the accepted `doc-web` bundle/provenance boundary versioned and inspectable, Story 194 kept direct-entry families outside recommendation-only and approved-handoff automation unless proven otherwise, and Story 202 explicitly left `.mbox` out of scope because no maintained archive substrate had been verified yet. No narrower `.mbox` ADR or runbook was found in this pass.
- **Existing patterns to reuse**: `modules/extract/unstructured_email_intake_v1/main.py`, `modules/transform/email_elements_to_bundle_v1/main.py`, `modules/common/office_native_bundle.py`, `modules/intake/unstructured_pdf_intake_v1/main.py` (`serialize_element`), `tests/test_email_intake_recipe.py`, `tests/test_doc_web_cli_contract.py`, `modules/intake/intake_plan_utils.py`, `benchmarks/scripts/intake_scope.py`, and the direct-entry story patterns from Stories 200, 201, and 202.
- **Eval**: the deciding proof surface is a fresh `driver.py` run on one repo-owned `.mbox` fixture plus manual inspection of emitted intake, bundle, provenance, and HTML artifacts. If a maintained lane lands, focused scope tests should also prove `email-mbox` is represented honestly as a direct explicit-recipe lane outside recommendation-only intake and approved handoff.

## Tasks

- [x] Freeze the current `.mbox` seam from repo reality before changing code:
  - [x] verify the `email-mbox` coverage row is still `untested`
  - [x] verify `schemas.py` / `driver.py` still have no `input_mbox` / `--input-mbox`
  - [x] verify there is still no maintained `.mbox` recipe/module pair or checked-in `.mbox` fixture
  - [x] record the current substrate split honestly: stdlib `mailbox.mbox` is available, `partition_email(...)` is callable for per-message parsing, and no dedicated `.mbox` parser/module or direct-entry runtime seam is currently verified
- [x] Add one repo-owned reproducible `.mbox` fixture:
  - [x] check in one bounded multi-message `.mbox` archive plus source metadata under `testdata/`
  - [x] record how the fixture was generated or captured in `testdata/README.md`
  - [x] keep future tests and reruns independent of live inbox, connector, or network access
- [x] Measure the smallest honest native archive baseline before adding cleanup logic:
  - [x] split the checked-in `.mbox` fixture with stdlib `mailbox.mbox`
  - [x] run per-message parsing through the current `partition_email(...)` path and inspect the emitted message metadata
  - [x] verify whether the current email bundle transform can be generalized honestly or whether a thin archive-specific sibling transform is required
  - [x] record the exact artifact paths and failure modes inspected for that before-state
- [x] If the bounded direct-entry seam is viable, land the smallest coherent `.mbox` lane:
  - [x] add `input_mbox` support in `schemas.py` / `driver.py`
  - [x] add `configs/recipes/recipe-email-mbox-html-mvp.yaml`
  - [x] add an `.mbox` intake module and the smallest honest bundle/provenance transform, reusing existing email helpers where possible
  - [x] ensure the resulting artifact shape preserves message-level metadata and ordering with pageless provenance rather than fabricating page anchors or mailbox-thread guarantees
  - [x] ensure the final manifest `reading_order` and HTML entry count match the bounded fixture's message count
- [x] Add focused fixture-backed coverage for the new seam:
  - [x] add a direct-entry smoke test that runs `driver.py` on the checked-in `.mbox` fixture and asserts bundle/provenance outputs
  - [x] extend direct-entry-only scope helper tests and focused benchmark-surface tests so `email-mbox` is treated honestly if the lane lands
  - [x] extend install-contract coverage only if the existing maintained email dependency path needs new `.mbox`-specific proof
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
  - [x] If agent tooling changed: `make skills-check`
  - [x] No agent tooling changed, so `make skills-check` was correctly not needed for this pass
- [x] If evals or goldens changed: update the relevant intake benchmark truth surfaces honestly and run `/improve-eval` only if an existing eval surface is intentionally widened
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every support claim traces to the archive fixture, message ordering, message metadata, and inspected provenance rows
  - [x] T1 — AI-First: no deterministic archive cleanup is introduced for a problem the measured native parser path already solves
  - [x] T2 — Eval Before Build: the stdlib/archive plus native `partition_email(...)` baseline is measured before adding new runtime logic
  - [x] T3 — Fidelity: message body and header metadata survive extraction without silent loss or fabricated mailbox/thread claims
  - [x] T4 — Modular: extend the explicit-recipe email family pattern instead of inventing a parallel archive runtime
  - [x] T5 — Inspect Artifacts: emitted `.mbox` bundle/provenance outputs are manually inspected, not just split/parser logs

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

- **Owning module / area**: direct email-archive intake plus the accepted `doc-web` bundle/provenance boundary for multi-message pageless sources. Ownership should extend the maintained email direct-entry seam from Story 202 rather than the recommendation-only intake automation.
- **Methodology reality**: this belongs to `spec:1`, `spec:3`, `spec:6`, `spec:7`, `spec:8`, and `spec:9`. In `docs/methodology/state.yaml`, `spec:1`, `spec:3`, `spec:6`, `spec:8`, and `spec:9` substrates exist, `spec:7` is still `partial`, and the relevant phases are `C2 = climb`, `C3 = climb`, `B10 = climb`, and `B1 = hold`. The relevant coverage row is now `email-mbox = passing` on one bounded repo-owned archive fixture; `mixed-archive` remains a separate untested archive family.
- **Substrate evidence**: verified in this pass that stdlib `mailbox.mbox` works locally; `unstructured.partition.email.partition_email` is installed in this checkout and accepts `filename` or `file` input; the repo now owns `input_mbox` / `--input-mbox`, `configs/recipes/recipe-email-mbox-html-mvp.yaml`, `modules/extract/mailbox_mbox_intake_v1/main.py`, `modules/transform/mbox_elements_to_bundle_v1/main.py`, `tests/test_email_mbox_intake_recipe.py`, the checked-in `testdata/email-mbox-mini.mbox` fixture, and direct-entry boundary helpers that block `email-mbox` outside recommendation-only intake and approved handoff. The implementation keeps the existing `.eml` seam from Story 202 intact by using a sibling archive transform instead of widening the single-message path.
- **Data contracts / schemas**: likely touched contracts are `RunConfig` in `schemas.py`, `unstructured_element_v1`, `doc_web_bundle_manifest_v1`, and `doc_web_provenance_block_v1`. If archive-level metadata such as message index, archive source, or per-message identifiers must cross artifact boundaries beyond normalized element metadata or final bundle reports, add those fields explicitly to the relevant schema before stamped outputs rely on them.
- **File sizes**: likely touch points are `schemas.py` (1241 lines), `driver.py` (2354), `modules/intake/intake_plan_utils.py` (311), `benchmarks/scripts/intake_scope.py` (47), `tests/test_doc_web_cli_contract.py` (596), `tests/test_run_config.py` (55), `tests/test_intake_plan_utils.py` (272), `README.md` (418), `docs/RUNBOOK.md` (679), `tests/fixtures/formats/_coverage-matrix.json` (523), `modules/extract/unstructured_email_intake_v1/main.py` (214), `modules/transform/email_elements_to_bundle_v1/main.py` (159), `tests/test_email_intake_recipe.py` (103), `pyproject.toml` (51), and `requirements.txt` (10). Files already over 500 lines: `schemas.py`, `driver.py`, `tests/test_doc_web_cli_contract.py`, `docs/RUNBOOK.md`, and `tests/fixtures/formats/_coverage-matrix.json`; keep edits especially surgical there.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, Stories 194 and 202, `tests/fixtures/formats/_coverage-matrix.json`, `modules/extract/unstructured_email_intake_v1/main.py`, `modules/transform/email_elements_to_bundle_v1/main.py`, `modules/intake/intake_plan_utils.py`, `README.md`, and `docs/RUNBOOK.md`. No narrower `.mbox`-specific ADR, runbook, scout, or note was found after search.

## Files to Modify

- `schemas.py` — add `input_mbox` to `RunConfig` if a maintained `.mbox` direct-entry lane lands (1241 lines)
- `driver.py` — add `--input-mbox` plumbing and recipe input override handling if the lane becomes maintained (2354 lines)
- `configs/recipes/recipe-email-mbox-html-mvp.yaml` — maintained bounded `.mbox` direct-entry recipe reusing the accepted `doc-web` bundle/provenance boundary (new file)
- `modules/extract/mailbox_mbox_intake_v1/main.py` and `modules/extract/mailbox_mbox_intake_v1/module.yaml` — archive intake module that splits `.mbox` messages and serializes per-message email elements or a clearly superior bounded successor (new files)
- `modules/transform/mbox_elements_to_bundle_v1/main.py` and `modules/transform/mbox_elements_to_bundle_v1/module.yaml` — multi-message bundle/provenance transform or the smallest honest generalization of the current email helper pattern (new files)
- `modules/transform/email_elements_to_bundle_v1/main.py` — extend only if message-level shaping should be shared instead of duplicated (159 lines)
- `modules/extract/unstructured_email_intake_v1/main.py` — reuse or extract shared per-message parsing logic only if the `.mbox` lane needs a common helper path (214 lines)
- `tests/test_run_config.py` — add `input_mbox` config coverage if the RunConfig surface grows (55 lines)
- `tests/test_email_mbox_intake_recipe.py` — focused `.mbox` direct-entry smoke coverage on the checked-in fixture (new file)
- `tests/test_doc_web_cli_contract.py` — extend install/smoke coverage only if the maintained email dependency path or CLI contract changes materially (596 lines)
- `modules/intake/intake_plan_utils.py` — add `email-mbox` to the direct-entry-only boundary table only if a maintained `.mbox` recipe lands (311 lines)
- `benchmarks/scripts/intake_scope.py` — extend direct-entry-only scope handling if `email-mbox` joins that boundary class (47 lines)
- `tests/test_auto_book_type_detection_benchmark.py` — keep recommendation-only boundary truth aligned if `email-mbox` becomes explicit direct-entry-only scope (82 lines)
- `tests/test_approved_intake_handoff_benchmark.py` — keep approved-handoff boundary truth aligned if `email-mbox` becomes explicit direct-entry-only scope (175 lines)
- `testdata/email-mbox-mini.mbox` / `testdata/email-mbox-mini.source.json` — repo-owned bounded `.mbox` fixture and provenance metadata for the first maintained slice (new files)
- `testdata/README.md` — record fixture source, generation/capture note, and maintained scope (117 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — move the `email-mbox` row only as far as fresh evidence justifies (523 lines)
- `README.md` — align user-facing format support wording with the actual `.mbox` seam (418 lines)
- `docs/RUNBOOK.md` — publish the verified bounded `.mbox` direct-entry command or the blocker if the seam cannot land (679 lines)

## Redundancy / Removal Targets

- stale `email-mbox` `untested` wording in coverage/docs once a maintained direct-entry slice exists
- any ad hoc local `.mbox` split/probe commands or scratch scripts that become redundant after a maintained recipe/test lane lands
- any temptation to treat `.mbox` as a hidden `mixed-archive` special case instead of keeping the archive seam explicit and bounded

## Notes

- New story justification: reopening Story 202 would blur a closed single-message `.eml` seam with a materially different multi-message archive seam. Story 202 explicitly left `.mbox` out of scope, and this story has a different fixture shape, intake contract, and validation boundary.
- The first honest slice should stay tightly bounded to a small multi-message plain-text `.mbox` archive. Attachments, quoted-thread cleanup, connector workflows, `.msg`, and mixed-archive routing remain separate future lines.

## Plan

Alignment check:
- This story still moves toward the Ideal rather than away from it. It closes a real format-coverage gap under `spec:1.1` / `C2`, keeps the accepted `doc-web` contract as the output bar under `spec:6` / `spec:7` and ADR-002, and does not introduce a new hidden archive or mailbox compromise.
- No narrower `.mbox` ADR or runbook was found after the fresh search in this pass.

Measured baseline from this exploration pass:
- **Current repo direct-entry runtime baseline: 0/1 passing.** `email-mbox` is still `untested` in the coverage matrix; `schemas.py` and `driver.py` expose no `input_mbox` / `--input-mbox`; there is no maintained `.mbox` recipe/module pair or repo-owned fixture.
- **Archive split + native parser substrate baseline: 2/2 messages split and parsed.** A scratch two-message archive created in this pass opened cleanly through stdlib `mailbox.mbox`, and both messages partitioned through `unstructured.partition.email.partition_email(file=..., content_source='text/plain', process_attachments=False)` with inspectable `subject`, `sent_from`, and `sent_to` metadata.
- **Current single-message transform baseline: 0/1 for archive shaping.** Feeding those two parsed messages into the existing `_build_bundle(...)` path in `modules/transform/email_elements_to_bundle_v1/main.py` produced `entry_count = 1` and `document_title = 'Subject 0'`, proving the current `.eml` transform collapses an archive into one entry instead of preserving message boundaries.
- **Shared bundle writer baseline: 1/1 for multi-entry output.** A direct scratch call to `modules.common.office_native_bundle.write_bundle(...)` with two explicit entry specs emitted `entry_count = 2` and `reading_order = ['page-001', 'page-002']`, so the real missing seam is grouping/transform logic plus runtime plumbing, not the final bundle writer.
- **Fixture-quality surprise:** the trivial scratch messages partitioned into only one `Title` element each. That is enough to prove the substrate exists, but it is too thin to prove message-body fidelity. The maintained `.mbox` fixture should therefore be patterned after the richer checked-in `.eml` slice from Story 202 rather than raw `EmailMessage()` defaults.

Approach choice after the fresh baseline:
- **AI-only** remains the wrong first move. The measured gap is structural: archive splitting, grouping, and runtime plumbing. An LLM would add cost while weakening the inspectable header/body provenance we already get from native parsing.
- **Hybrid** is only a fallback if the native archive path proves close but not sufficient on the repo-owned fixture. At that point, limit AI to the smallest inspectable repair step.
- **Pure code + native parsing** is the planned first implementation path because the bundle writer already supports multi-entry output and the only failing seam is message grouping plus `driver.py` / recipe exposure.

Implementation order:
1. **Freeze a repo-owned bounded archive fixture (`S`)**
   - Files: `testdata/email-mbox-mini.mbox`, `testdata/email-mbox-mini.source.json`, `testdata/README.md`, this story file.
   - Change: create a small multi-message `.mbox` archive with at least two checked-in plain-text messages modeled on the richer `.eml` proof slice, and record exactly how it was generated.
   - Impact/risk: fixture quality matters because the trivial scratch messages only yielded `Title` elements; a weak fixture would under-prove the lane.
   - Done looks like: the repo owns a stable archive fixture whose messages contain enough body structure to exercise the bundle output honestly.
2. **Add the runtime input seam (`S`)**
   - Files: `schemas.py`, `driver.py`, `configs/recipes/recipe-email-mbox-html-mvp.yaml`, `tests/test_run_config.py`.
   - Change: add `input_mbox` / `--input-mbox`, mirror the existing direct-entry override flow, and add the maintained recipe skeleton.
   - Impact/risk: `schemas.py` and `driver.py` are already oversized, so changes must stay minimal and parallel to the existing `.eml` pattern.
   - Done looks like: a dry driver invocation can resolve a recipe with `input_mbox` without disturbing existing direct-entry lanes.
3. **Implement archive intake using the proven substrate (`M`)**
   - Files: `modules/extract/mailbox_mbox_intake_v1/main.py`, `modules/extract/mailbox_mbox_intake_v1/module.yaml`, optionally `modules/extract/unstructured_email_intake_v1/main.py`.
   - Change: split archive messages via stdlib `mailbox.mbox`, parse each message through the existing native email path with `process_attachments=false`, and serialize enough per-message metadata to preserve ordering and grouping without fabricating mailbox-thread semantics.
   - Impact/risk: if per-message grouping needs shared helper extraction from the `.eml` module, keep that change narrow so Story 202's single-message lane does not regress.
   - Done looks like: the intake artifact makes message boundaries and ordering explicit enough for a downstream multi-entry bundle transform.
4. **Implement the archive bundle transform (`M`)**
   - Files: `modules/transform/mbox_elements_to_bundle_v1/main.py`, `modules/transform/mbox_elements_to_bundle_v1/module.yaml`, optionally `modules/transform/email_elements_to_bundle_v1/main.py`.
   - Change: group parsed elements by message, derive one entry title per message, preserve archive order in `reading_order`, and reuse `write_bundle(...)` instead of inventing a second HTML/provenance emitter.
   - Impact/risk: this is the core shape change. The existing `.eml` transform currently hardcodes one entry, so either add a sibling transform or extract just enough shared helper logic to avoid duplication without coupling the two lanes too tightly.
   - Done looks like: the final manifest publishes one entry per message on the bounded fixture and the story can point to the exact bundle/provenance artifact paths that prove it.
5. **Keep direct-entry boundary truth aligned (`S`)**
   - Files: `modules/intake/intake_plan_utils.py`, `benchmarks/scripts/intake_scope.py`, `tests/test_intake_plan_utils.py`, `tests/test_auto_book_type_detection_benchmark.py`, `tests/test_approved_intake_handoff_benchmark.py`.
   - Change: if the lane lands, classify `email-mbox` the same way as the other explicit direct-entry families outside recommendation-only intake and approved handoff.
   - Impact/risk: do not widen automation surfaces accidentally; Story 194's explicit boundary remains the source of truth.
   - Done looks like: benchmark/helper tests block `email-mbox` with an explicit direct-entry-only reason rather than treating it as unsupported or silently supported.
6. **Fresh verification and artifact inspection (`M`)**
   - Files/tests: `tests/test_email_mbox_intake_recipe.py`, `tests/test_doc_web_cli_contract.py` only if the existing email extra needs new proof, `make test`, `make lint`, and the narrow real `driver.py` `.mbox` path.
   - Change: run the fixture-backed smoke, then run the real maintained recipe through `driver.py`, inspect the intake artifact, bundle report, manifest, provenance blocks, and at least two published message HTML files.
   - Done looks like: the story can cite exact artifact paths and sample observations for message ordering, metadata preservation, and pageless provenance.

Structural health and risk notes:
- Highest-risk files are `schemas.py`, `driver.py`, `tests/test_doc_web_cli_contract.py`, `docs/RUNBOOK.md`, and `tests/fixtures/formats/_coverage-matrix.json` because they are already large.
- The main regression risk is accidentally breaking Story 202's `.eml` lane while extracting shared helpers. Prefer a sibling `.mbox` transform unless shared code clearly reduces duplication without entangling the single-message path.
- Expected coverage movement: `email-mbox` should move from `untested` to bounded `passing` only if the maintained fixture, driver proof, and artifact inspection all clear. `mixed-archive` should remain untouched.

Human-approval blockers:
- No new dependency blocker is visible yet; the existing maintained email dependency path already exposes `partition_email(...)`.
- If honest grouping requires new cross-artifact schema fields beyond normalized metadata or bundle reports, that is acceptable inside this story but should be called out before implementation rather than smuggled through stamped outputs.

Scope adjustments discovered during exploration:
- **Small coherent delta folded in now:** the story now explicitly requires one HTML entry per message and a manifest `reading_order` that matches archive order. Exploration proved this is the real failing seam.
- **Large expansion not recommended:** threading, quoted-thread cleanup, attachments, `.msg`, and `mixed-archive` remain separate future lines and should not be absorbed here.

## Work Log

20260409-1329 — create-story: created Story 203 after `/triage` found no actionable `In Progress`, `Pending`, or `Draft` line beyond blocked Story 191 and the user approved the next honest coverage move. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, Stories 194 and 202, `tests/fixtures/formats/_coverage-matrix.json`, `modules/extract/unstructured_email_intake_v1/main.py`, `modules/transform/email_elements_to_bundle_v1/main.py`, `modules/intake/intake_plan_utils.py`, `README.md`, and `docs/RUNBOOK.md`. Fresh substrate evidence: `email-mbox` remains `untested`; the repo still has no `input_mbox`, no maintained `.mbox` recipe/module pair, and no checked-in `.mbox` fixture; stdlib `mailbox.mbox` works locally; and `unstructured.partition.email.partition_email` in this checkout accepts `filename` or `file` input while the existing `.eml` seam from Story 202 already provides reusable per-message parsing and bundle/provenance patterns. Result: a new `Pending` story is honest because `.mbox` is a distinct multi-message archive seam that Story 202 explicitly left out of scope, and the missing work is bounded archive orchestration plus fixture ownership rather than a missing parser substrate. Next step: `/build-story` should freeze the baseline, create the repo-owned archive fixture, and decide whether the thinnest stdlib-plus-Unstructured path already clears the accepted boundary or should be blocked explicitly.
20260409-1335 — /build-story exploration + plan: re-read `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, Stories 202 and 194, the `email-eml` / `email-mbox` / `mixed-archive` coverage rows, the current `.eml` recipe/module/test path, and the driver/schema override surface. Fresh substrate reality from this pass: `email-mbox` still has no `input_mbox`, fixture, recipe, or module; stdlib `mailbox.mbox` split a scratch two-message archive successfully; `partition_email(file=..., content_source='text/plain', process_attachments=False)` parsed both messages with inspectable metadata; the current `_build_bundle(...)` path from `email_elements_to_bundle_v1` collapsed both parsed messages into one output entry titled by the first subject; and `write_bundle(...)` itself already emitted two ordered entries when given explicit `entry_specs`. Result: the story remains honestly `Pending`, and the real missing seam is archive grouping plus runtime plumbing, not the final bundle writer. Small scope delta folded into the story: acceptance criteria and tasks now explicitly require one HTML entry per message and manifest ordering that matches the archive. Files likely to change: new `.mbox` fixture + metadata, `schemas.py`, `driver.py`, a new archive intake module, a new archive transform (or a very small shared-helper extraction from the current `.eml` modules), focused smoke tests, boundary-helper tests, and docs/coverage truth surfaces. Files at risk: oversized `driver.py`, `schemas.py`, `tests/test_doc_web_cli_contract.py`, `docs/RUNBOOK.md`, and the existing single-message `.eml` seam if shared helper extraction is too broad. Surprise worth keeping explicit: trivial scratch email messages only yielded `Title` elements, so the maintained `.mbox` fixture needs richer body content modeled on the checked-in `.eml` slice instead of raw `EmailMessage()` defaults. Next step: wait for human approval before starting implementation.
20260409-2006 — implementation + verification: landed the bounded `.mbox` direct-entry seam with a repo-owned two-message fixture (`testdata/email-mbox-mini.mbox` + `.source.json`), new runtime plumbing in `schemas.py` / `driver.py`, `configs/recipes/recipe-email-mbox-html-mvp.yaml`, `mailbox_mbox_intake_v1`, `mbox_elements_to_bundle_v1`, focused recipe smoke coverage, direct-entry boundary updates, docs, and coverage-matrix truth. Key implementation decision: keep Story 202's `.eml` path stable by using a sibling archive transform instead of widening `email_elements_to_bundle_v1`; store archive/message grouping fields inside `metadata` so driver stamping keeps `unstructured_element_v1` rows honest without schema surgery. Fresh checks and evidence from this pass: `python -m pytest tests/test_email_intake_recipe.py tests/test_email_mbox_intake_recipe.py -q` passed (`4 passed`), `python -m pytest tests/test_doc_web_cli_contract.py -q -k mbox_smoke` passed (`1 passed, 11 deselected`), `make lint` passed, and `make test` passed (`517 passed, 4 warnings`). Fresh driver proof: `python driver.py --recipe configs/recipes/recipe-email-mbox-html-mvp.yaml --input-mbox testdata/email-mbox-mini.mbox --run-id story203-mbox-smoke --allow-run-id-reuse --force` completed successfully after clearing `*.pyc`, writing `output/runs/story203-mbox-smoke/01_mailbox_mbox_intake_v1/elements.jsonl` and `output/runs/story203-mbox-smoke/02_mbox_elements_to_bundle_v1/email_archive_bundle_report.json`, plus final `doc-web` artifacts under `output/runs/story203-mbox-smoke/output/html/`. Manual inspection results: `elements.jsonl` shows `archive_message_index = 1/2`, `subject = Fixture Subject / Fixture Follow-up`, and message-level `sent_from` / `sent_to` metadata anchored back to the checked-in `.mbox`; `email_archive_bundle_report.json` shows `entry_count = 2`, `reading_order = ['page-001', 'page-002']`, and per-message report rows with archive dates and message IDs; `output/html/manifest.json` points back to `/Users/cam/.codex/worktrees/28f2/doc-web/testdata/email-mbox-mini.mbox` with two ordered entries titled by the two subjects; `output/html/provenance/blocks.jsonl` validates as `doc_web_provenance_block_v1` with pageless `source_element_ids`; and `output/html/page-001.html` / `page-002.html` render the expected bodies (`Hello Bob...` and `Hello Dana...`) as separate navigable pages. Remaining note for `/validate`: no broader mailbox semantics were claimed; quoted-thread cleanup, attachments, `.msg`, and mixed-archive routing remain explicitly out of scope.
20260409-2048 — provenance-id repair after `/validate`: fresh validation on `validate-story203-mbox-pass2` exposed an honest traceability bug in the bounded `.mbox` lane: the same upstream Unstructured `element.id` (`44ef95ef3a1139dd435192f6f299a0ac`) appeared on two different archive rows for the repeated `Regards,` line, which made `source_element_ids` ambiguous across messages even though the bundle otherwise looked correct. Fix: scope every serialized intake row to a deterministic archive-local id (`mbox-message-<message>-element-<sequence>`) inside `mailbox_mbox_intake_v1`, while preserving the original Unstructured id in `metadata.archive_native_element_id` for debugging. Coverage: extend `tests/test_email_mbox_intake_recipe.py` to assert unique intake ids, distinct repeated-content ids across messages, and one-to-one mapping from provenance `source_element_ids` back to upstream rows. Next step: rerun focused email/mbox tests, lint, the full suite, and a fresh `driver.py` smoke, then re-inspect the emitted artifacts before asking `/validate` to reassess closure.
20260409-1533 — /mark-story-done close-out: re-read `docs/ideal.md`, `docs/spec.md`, ADR-002, the full Story 203 body, and searched `docs/decisions/` again for a narrower `.mbox` ADR; none exists. Fresh close-out evidence from this pass: `python -m pytest tests/test_email_mbox_intake_recipe.py tests/test_email_intake_recipe.py tests/test_doc_web_cli_contract.py -q -k 'email or mbox_smoke'` passed (`6 passed, 10 deselected`), `make lint` passed, `make methodology-check` passed, `make test` passed (`517 passed, 4 warnings`), and `python driver.py --recipe configs/recipes/recipe-email-mbox-html-mvp.yaml --input-mbox testdata/email-mbox-mini.mbox --run-id validate-story203-mbox-pass4 --allow-run-id-reuse --force` produced a fresh bounded archive proof run. Manual inspection in this pass confirmed unique archive-scoped intake ids in `output/runs/validate-story203-mbox-pass4/01_mailbox_mbox_intake_v1/elements.jsonl`, ordered two-message bundle metadata in `output/runs/validate-story203-mbox-pass4/02_mbox_elements_to_bundle_v1/email_archive_bundle_report.json`, two ordered HTML entries in `output/runs/validate-story203-mbox-pass4/output/html/manifest.json`, unambiguous pageless provenance rows in `output/runs/validate-story203-mbox-pass4/output/html/provenance/blocks.jsonl`, and correct message bodies in `output/runs/validate-story203-mbox-pass4/output/html/page-001.html` plus `page-002.html`. Result: all acceptance criteria and tasks are now satisfied, the workflow gates are complete, and Story 203 is ready to land. Next step: `/check-in-diff`.
