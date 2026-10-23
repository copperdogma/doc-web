---
title: Lossless artifact validation at the driver boundary
status: Done
priority: High
ideal_refs: ["req:1", "req:5", "req:6", "req:7"]
spec_refs: ["spec:1", "spec:6", "spec:7"]
adr_refs: ["ADR-002"]
depends_on: []
category_refs: ["spec:1", "spec:6", "spec:7"]
compromise_refs: []
input_coverage_refs: ["docx", "xlsx", "pptx", "epub", "email-eml", "email-mbox", "born-digital-pdf"]
architecture_domains: ["doc_web_runtime"]
roadmap_tags: ["source-fidelity"]
legacy_system: ""
---

# Story 260 — Lossless artifact validation at the driver boundary

**Status**: Done
**Relative effort**: M
**Decision Refs**: ADR-002; `docs/spec.md` mandatory validation and append-only principles.

## Goal

Reject malformed stage artifacts before downstream execution while preserving
the rejected producer data for diagnosis. Apply the existing raw Unstructured
element schema to the seven producers that already declare it, preserving native
metadata and `_codex` provenance. Schema validation is a structural check, not
proof of source fidelity or permission to normalize away data.

## Acceptance Criteria

- [x] A malformed row, error record, invalid JSON or non-object row fails a
  registered-schema stage without deleting rows or rewriting the original.
- [x] Failure records identify artifact and row where available; driver stage,
  overall run and instrumentation report failure, and dependents do not execute.
- [x] Successful stamping publishes a complete replacement atomically; failed
  validation/serialization/replacement leaves the original bytes intact.
- [x] JSON object/list envelopes remain JSON; JSONL remains JSONL.
- [x] `unstructured_element_v1` is available in the CLI and driver. Native
  fields, metadata, `_codex` and unknown producer fields survive unchanged;
  existing producer provenance remains authoritative.
- [x] Representative native DOCX/XLSX and existing normalized artifact paths
  pass through real driver runs; produced data, final HTML and provenance are
  manually inspected. Controlled invalid artifacts stop in real driver runs.
- [x] Existing unknown/null output-schema behavior and empty-stream policy
  remain outside this bounded change; no blanket schema-coverage claim.

## Tasks

- [x] Reproduce the loss and inspect shared schema/driver/consumer contracts.
- [x] Compare existing story ownership, established serialization/publication
  practices, and current graph/state/coverage requirements.
- [x] Register raw elements and implement non-destructive validation/stamping.
- [x] Add focused failure/publication/format/provenance regression coverage.
- [x] Run real driver positive/negative probes and inspect saved artifacts.
- [x] Update runbook/changelog and regenerate methodology views.

## Workflow Gates

- [x] Build complete
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via /mark-story-done

## Plan

1. Register the existing `UnstructuredElement` in `validate_artifact.py`; expose
   its existing JSON/JSONL reader to the driver. Validate native rows without
   rewriting them, avoiding Pydantic normalization or `_codex` alias loss.
2. In `driver.py`, validate every registered-schema row before replacing a
   stamped artifact. Keep normalized schemas' established serialization, correct
   JSON envelopes, and use a same-directory temporary file plus `os.replace`.
   Never filter error/invalid rows into a successful artifact.
3. Route stamping and validation failures through failed stage/run bookkeeping
   and instrumentation; preserve the diagnostic artifact and stop dependents.
4. Measure regression cases before/after, then run the maintained native recipes
   and an existing normalized producer/reuse path. Inspect data and rendered
   output. No provider calls, dependencies or schema version changes are needed.

The standing user goal authorizes this bounded implementation. Pure orchestration
and exact schema contracts belong in code; model judgment would add uncertainty.
The shared driver publication boundary differs materially from the native-format
entry stories 174/193/201/202/203 and bundle-definition stories 152/153. Stories
015/016 cover historical module/DAG architecture; this story isolates the newly
demonstrated artifact-loss/failure transaction across maintained producers, rather
than creating one story per format. ADR-002's native provenance boundary remains.
`spec:6` has no active compromise; this restores a mandatory obligation. Graph
categories 1/6 exist, 7 is partial; coverage claims/scores will not be promoted.

## Research Notes

- General problem: lossy validation before publication, plus serialization of
  aliased producer data. Pydantic documents that `model_dump()` normalizes models
  and aliases require `by_alias=True`:
  https://docs.pydantic.dev/latest/concepts/serialization/ . Native validation
  therefore checks the original rows without reserializing through the model.
- Python documents atomic successful replacement on the same filesystem:
  https://docs.python.org/3/library/os.html#os.replace . Use a temporary sibling,
  validate/serialize fully, then replace. This is atomic visibility, not a
  crash-durable storage or concurrent-writer guarantee.
- Local baseline: `output/triage-20261023-validation-audit/baseline.json` records
  two `element_core_v1` rows becoming one after stamping; the missing-ID row is
  silently discarded and the producer artifact overwritten. Raw Unstructured
  schema is absent from `SCHEMA_MAP` despite seven declaring producers.

## Central Tenet Verification

- [x] T0 Traceability: preserve source identity and native `_codex` metadata.
- [x] T1 AI-first: deterministic validation/publication requires no AI judgment.
- [x] T2 Eval-before-build: retained failing baseline and measured regressions.
- [x] T3 Fidelity: rejected rows remain inspectable, never silently disappear.
- [x] T4 Modularity: apply shared registered contracts, no format permutations.
- [x] T5 Inspect artifacts: real driver data/render inspection recorded below.

## Work Log

20261023-1727 — Full triage ranked this reproduced validation loss above a real
scanned-prose qualification preflight and stable coverage score references. The
raw-schema gap surfaced during Story193's CLI checks; its direct-model checks
were valid but did not establish driver/CLI enforcement. Existing source/metadata
contracts, driver failure accounting, and ADR-002 were inspected. Research chose
validate-before-publish and atomic replacement with native rows kept intact.
No source or provider work is required; no commits/pushes authorized.

20261023-1737 — Implemented whole-artifact admission, failure bookkeeping and
atomic publication. Review caught `doc_web_cache_identity_v1`, whose strict
contract deliberately lacks stamp fields: that and other models without a
stamping envelope now receive validation only. Native producer bytes remain
unchanged; declared envelope fields alone are stamped elsewhere. No schema
versions, dependencies or model choices changed. The user subsequently requested
finish/validate/check-in/push, authorizing close-out and ending new triage work.

Validation so far: `focused-tests-final.log` reports108 passed, including the
cache identity control, three real invalid-output driver regressions and the
existing driver/bundle consumers. `make lint`, skill sync and diff whitespace
checks pass. The additional `codex review --uncommitted` signal was attempted but
exited101 when rollout storage ran out; no completed verdict is claimed. A
bounded semantic worker review found the cache identity issue above; its fix is
covered by the final focused tests. Root `driver.py` has eight pre-existing Ruff
findings outside `make lint`; no new root-file finding was introduced.

`output/triage-20261023-validation-audit/driver-results.json` records12 real
driver runs: four deliberate failures (missing core ID, missing native ID,
producer error, invalid JSON-list member), two successful normalized/reuse paths,
and six maintained native recipes (DOCX/XLSX/PPTX/EPUB/EML/MBOX). All four rejected
artifacts retain both rows, fail stage/run/instrumentation, and never execute the
dependent stage. The six native runs pass18 CLI schema checks. Manually read
saved element samples and `_codex` identities: DOCX Family Snapshot/Parents Ada
and Lin, XLSX Roster Ada/Researcher/Foothills County and Visits2024/3,2025/4,
PPTX Slide One/Ada/Lin, EPUB Chapter One and Ada/Lin list entries, EML Hello Bob
through Alice, MBOX ordered message IDs and Hello Bob/Hello Dana. Raw element
artifacts live in `output/runs/triage-20261023-validation-{format}/01_*/elements.jsonl`;
final bundles are under each run's `output/html/`. Browser inspection confirmed
the XLSX Roster3×3 and Visits3×2 tables and Next/Previous navigation. This checks
structural admission and representative data preservation, not corpus fidelity.

These proofs precede integration with23 newer main commits. The later change
that preserves models without a stamping envelope is covered by108 focused
tests; native admission is unchanged. Combined-tree checks and affected driver
proofs will run after integration. Story remains In Progress until that validation
finishes. Disk repeatedly reached zero free space; removed only two task-owned
dependency-test virtual environments, three reproducible reconstruction scratch
copies (retaining the parent proof and sealed receipt archive), and disposable
environments from the interrupted review. Asked the user to free5GB before broad
checks; observed free space subsequently recovered enough to proceed. No paid evaluations or new provider calls occurred during this fix.


## Approach Evaluation and Files

- Normalize all producers through Pydantic serialization: rejected for native
  representations and fingerprinted records, whose original bytes and unknown
  metadata are part of the contract. Alias-aware dumps alone cannot preserve them.
- Validate native/no-envelope records without rewriting, and validate then
  atomically stamp declared envelopes: selected; the retained two-to-one loss
  baseline, native extra-field control, cache fingerprint control and real driver
  probes distinguish these mechanisms. A model call cannot establish exact typed
  contracts or atomic publication and is unnecessary orchestration cost.
- A new snapshot store or concurrent-writer protocol would broaden the outcome
  without a demonstrated need; this is not crash durability or race-free capture.

Files changed: `driver.py`, `validate_artifact.py`,
`tests/test_driver_artifact_validation.py`,
`tests/test_driver_stamping_preserves_pagelines_provenance.py` (existing control,
unchanged), `tests/test_doc_web_bundle_contract.py`,
`tests/driver_integration_test.py`, `tests/test_reference_integration.py`,
`docs/RUNBOOK.md`, this story, changelog and generated methodology records.
The existing console failure and retained artifact path are the operator surface;
no new UI is needed to inspect this admission failure.

20261023-1758 — /validate: no remaining material finding; GradeA, seven of seven
acceptance criteria met. Combined `make test` covered2624 cases:2619 passed,
one skipped, four initially failed. Two were malformed positive test scaffolds:
CleanPage omitted required raw_text/clean_text/confidence, and an upstream parser
surface test supplied a placeholder outside the actual reader choices. Corrected
only those fixtures, added retained-content and parser/schema-choice assertions;
`corrected-fixture-tests.log` passes50 checks. Two requirements installations
failed with explicit OSError28/No space left. Removed their two task-owned partial
virtual environments while retaining the captured errors, then reran the exact
checks serially with normal installs: `requirements-retry.log`,2 passed134.75s.
No dependency constraints or runtime acceptance were weakened. Thus all2623
non-skipped suite cases have applicable passing evidence; the whole suite was
not repeated over unchanged code. Environment: macOS, Python3.11.5, pytest9.0.2,
Pydantic2.12.5; clean requirements checks exercise pinned Pydantic2.9.2. Pytest's
standard tmp_path_retention_policy=failed removes passed disposable environments.

The final combined driver proof repeats all12 expected outcomes with current
source hashes and18 CLI schema checks. An additional real maintained HTML run
`output/runs/triage-20261023-closeout-html/` succeeds with the merged builder;
its manifest and provenance pass two more CLI checks. Manually inspected all11
citation rows p001-b1 through p001-b11 and rendered chapter-001.html: Harbor Field
Guide headings, four list items, North Pier8/12.4 and Outer Reef21/10.1 remain
faithful. The table is one citation unit; no cell-anchor promotion. Earlier
per-story evidence is reused for unchanged archive, source-feature, discovery
and paid-campaign content, supplemented by the combined full consumer suite.

Fresh milestone review used /root/closeout_milestone_review with requested
strongest eligible gpt-6-astra/ultra (served identity independently unverified).
It inspected primary artifacts before the executor verdict and recommended
continue-to-land, with no new triage, evals or broader architecture. Its initially
pending checks are now resolved above. ADR-002 remains ACCEPTED; this restores
its traceability boundary without changing its remaining graduation work.
Learning-review considered: existing verify/inspect mandates already cover the
false-green fixture lesson; no distinct workflow candidate is proposed.

/mark-story-done: tasks, ACs, tenets and all workflow gates verified and checked.
Close now; return to /finish-and-push for the explicitly authorized landing.
Unknown/null schemas, broad source fidelity, crash durability, concurrent writers
and the existing external/model blockers remain outside the completed claim.
