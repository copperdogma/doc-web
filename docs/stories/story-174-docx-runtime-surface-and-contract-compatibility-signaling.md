---
title: Harden Maintained DOCX Runtime Surface and Clarify `doc-web` Contract Compatibility
  Signaling
status: Done
priority: High
ideal_refs:
- 'Requirement #1 (Ingest), Requirement #6 (Validate), Requirement #7 (Export), Any
  format, any condition, Dossier-ready output, Transparency over magic'
spec_refs:
- spec:1
- spec:1.1
- spec:6
- spec:7
- spec:8
adr_refs: []
depends_on:
- '156'
- '172'
- '173'
category_refs:
- spec:1
- spec:6
- spec:7
- spec:8
compromise_refs:
- C2
input_coverage_refs:
- docx
architecture_domains:
- doc_web_runtime
roadmap_tags: []
legacy_system: ''
---

# Story 174 — Harden Maintained DOCX Runtime Surface and Clarify `doc-web` Contract Compatibility Signaling

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #1 (Ingest), Requirement #6 (Validate), Requirement #7 (Export), Any format, any condition, Dossier-ready output, Transparency over magic
**Spec Refs**: spec:1 (spec:1.1), spec:6, spec:7, spec:8
**Build Map Refs**: Category 1 Intake & Format Routing (`exists`, C2 `climb`); Category 6 Validation, Provenance & Export (`exists`); Category 7 Graduation & Dossier Handoff (`partial`); Input Coverage row `docx` (`has fixture`); Gap 3 — Office document intake beyond the first DOCX slice
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/doc-web-bundle-contract.md`, `docs/dossier-doc-web-handoff.md`, `docs/RUNBOOK.md`, `docs/build-map.md`, `docs/stories/story-156-pinned-doc-web-runtime-adoption-and-dossier-readiness.md`, `docs/stories/story-172-maintained-docx-intake-lane.md`, `docs/stories/story-173-dossier-doc-web-adoption-hardening.md`, `None found after search in docs/decisions/ for a separate contract-version policy ADR`
**Depends On**: Story 156, Story 172, Story 173

## Goal

Close the next two upstream-worthy gaps Dossier found in the maintained `doc-web` path. First, the repo now advertises a maintained DOCX recipe, but the supported runtime surface does not yet honestly guarantee the DOCX dependencies that `unstructured_docx_intake_v1` imports. Second, pageless provenance widened the effective downstream contract while `doc-web contract --json` still reports `contract_version = 1`, which makes compatibility signaling ambiguous if a consumer keys on version but not schema fingerprint. This story should make the maintained DOCX lane runnable from one explicit supported install shape, and make the contract compatibility policy explicit and test-backed so downstream adopters know which token actually gates breakage.

## Acceptance Criteria

- [x] The maintained DOCX lane has one honest, documented runtime install story:
  - [x] a clean supported environment using the repo-supported install shape for maintained smoke lanes can run `configs/recipes/recipe-docx-html-mvp.yaml` successfully against `testdata/docx-mini.docx`
  - [x] DOCX has an explicit extra beyond the default `.[driver]` maintained surface, and that extra is documented directly next to the maintained recipe and backed by automation so the gap is explicit rather than an import surprise
- [x] The repo keeps repeatable proof for the maintained DOCX runtime surface:
  - [x] automated clean-env coverage exists for the DOCX recipe path, not only the contract CLI or ambient-dev test environment
  - [x] the proof validates the final `doc_web_bundle` manifest plus provenance sidecar, not just stage-local artifacts
- [x] `doc-web` compatibility signaling is explicit and aligned across machine-readable and human-readable surfaces:
  - [x] the relationship between `contract_version`, `supported_bundle_schema_versions`, and `schema_fingerprint` is defined in code, tests, and downstream docs
  - [x] the story intentionally keeps `contract_version = 1` and makes the fingerprint/schema-version policy explicit instead of implying that unchanged coarse version means unchanged schema
  - [x] docs no longer imply that `contract_version` alone is sufficient
- [x] Downstream contract docs stay honest for pageless sources:
  - [x] `docs/dossier-doc-web-handoff.md` and the touched contract docs no longer require `source_page_number` for sources like DOCX when the accepted schema allows `null`
  - [x] the published contract guidance matches the current accepted schema and proof artifacts
- [x] Fresh evidence is recorded for both reported problem areas:
  - [x] a clean-env DOCX recipe proof runs under the chosen supported install shape and leaves inspectable artifacts under `output/runs/` or an equivalent test output directory
  - [x] a fresh `doc-web contract --json` payload is inspected after the change and compared against the intended compatibility policy

## Out of Scope

- Broad DOCX feature widening beyond the existing maintained slice (tracked changes, comments, text boxes, complex tables, SmartArt, etc.)
- Building new `xlsx` or `pptx` maintained lanes
- Reopening ADR-002's repo-boundary decision or creating a new release/distribution model for `doc-web`
- Dossier-side adapter changes or downstream gating policy implementation in the Dossier repo
- Reversing the accepted pageless-provenance shape unless exploration proves the current schema change was a mistake

## Approach Evaluation

- **Simplification baseline**: reproduce the two concrete failures exactly: clean-env DOCX recipe run from the repo-supported runtime surface, and current `doc-web contract --json` versus the previous reviewed fingerprint. This is plumbing and contract-discipline work; the simplest path is almost certainly deterministic metadata/docs/tests, not AI logic.
- **AI-only**: low value. A model can summarize compatibility policy wording, but it cannot prove whether `requirements.txt` or `.[driver]` actually installs the DOCX path or whether the runtime payload changed in a consumer-visible way.
- **Hybrid**: plausible only for the doc wording itself. Use deterministic runtime-contract inspection plus clean-env smoke tests to decide whether this is a runtime-surface bug, docs drift, or both.
- **Pure code**: likely correct. The core work is dependency metadata, runtime smoke coverage, contract payload semantics, and downstream docs/tests.
- **Repo constraints / prior decisions**: ADR-002 fixes the boundary at a versioned `doc-web` runtime plus structural bundle/provenance contract. Story 156 made that boundary installable and exposed `schema_fingerprint`. Story 172 intentionally widened the provenance contract for pageless sources. Story 173 already split contract-only install from repo-owned driver extras, so this story should reuse that boundary instead of silently widening the base package.
- **Existing patterns to reuse**: `tests/test_doc_web_cli_contract.py` for clean-venv package proof, `tests/test_docx_intake_recipe.py` for recipe smoke, `doc_web/runtime_contract.py` for machine-readable contract payload, `docs/doc-web-bundle-contract.md` and `docs/dossier-doc-web-handoff.md` for downstream compatibility language, and the maintained DOCX recipe/docs from Story 172.
- **Eval**: the deciding proofs are:
  1. a clean-env DOCX smoke using the chosen supported runtime install shape;
  2. a fresh runtime-contract payload diff inspected against the intended versioning policy;
  3. schema validation and artifact inspection on the maintained DOCX run.

## Tasks

- [x] Reproduce and freeze the Dossier-reported gaps in this checkout:
  - [x] create a clean supported environment that installs the repo-supported maintained runtime surface and run the maintained DOCX recipe against `testdata/docx-mini.docx`
  - [x] capture the exact import/runtime failure chain if the lane still fails
  - [x] inspect the current `doc-web contract --json` payload and compare it to the last reviewed fingerprint/version state
- [x] Choose and land the honest maintained DOCX install surface:
  - [x] decide whether the fix belongs in `requirements.txt`, an explicit maintained extra such as `.[driver]` or `.[docx]`, narrower import wiring, or docs that more precisely define the supported maintained install shape
  - [x] make the maintained DOCX recipe runnable from that chosen install shape
  - [x] align `README.md`, `docs/RUNBOOK.md`, and any other touched user-facing docs with that chosen shape
- [x] Define and land the compatibility policy between `contract_version` and `schema_fingerprint`:
  - [x] decide whether `contract_version` must bump for the pageless provenance widening or whether fingerprint/schema versions are the canonical consumer gate
  - [x] encode that policy in `doc_web/runtime_contract.py`, focused tests, and downstream docs
  - [x] update any stale handoff language that still treats `source_page_number` as mandatory for pageless sources
- [x] Add repeatable proof for the resolved surfaces:
  - [x] extend clean-env test coverage to the maintained DOCX lane
  - [x] assert the intended runtime-contract semantics in tests so future schema drift cannot hide behind a stable coarse version without an explicit policy decision
  - [x] run a real DOCX proof and inspect the final manifest/provenance artifacts
- [x] If this story changes documented format coverage or graduation reality: update `docs/build-map.md` and record the before/after state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [x] If agent tooling changed: `make skills-check` (not needed; no agent tooling changes)
- [x] If evals or goldens changed: run `/improve-eval` and update `docs/evals/registry.yaml` (not needed; no eval or golden changes)
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: the DOCX lane still emits honest source-element lineage, and compatibility signaling remains inspectable instead of implicit
  - [x] T1 — AI-First: keep the fix in deterministic packaging/contract surfaces; do not add AI to a packaging or version-policy problem
  - [x] T2 — Eval Before Build: reproduce the runtime failure and inspect the current contract payload before choosing a fix
  - [x] T3 — Fidelity: preserve pageless provenance honesty and do not paper over the change with misleading version language
  - [x] T4 — Modular: keep runtime-surface fixes, contract semantics, and docs/tests aligned without widening unrelated package surfaces casually
  - [x] T5 — Inspect Artifacts: validate and inspect real DOCX bundle/provenance artifacts plus the machine-readable contract payload

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: this story sits at the maintained DOCX intake boundary plus the Dossier-facing runtime contract surface. Primary owners are package metadata and maintained-recipe docs for Issue 1, plus `doc_web/runtime_contract.py` and downstream handoff docs/tests for Issue 2.
- **Build-map reality**: Category 1 owns the maintained DOCX lane and the `docx` input-coverage row, which is only `has fixture`. Category 6 owns the schema/provenance contract, and Category 7 owns the Dossier-facing runtime boundary and compatibility signaling. The substrate exists, but it is only partially hardened.
- **Substrate evidence**: `requirements.txt` currently pins `unstructured[pdf]==0.16.9` and does not state a DOCX-specific extra; `pyproject.toml` exposes only a narrow `driver` extra; `modules/extract/unstructured_docx_intake_v1/main.py` imports `unstructured.partition.docx` and exits with a message that misleadingly tells users to `pip install -r requirements.txt`; `tests/test_docx_intake_recipe.py` proves the lane only in the ambient repo environment; `doc_web/runtime_contract.py` hard-codes `CONTRACT_VERSION = "1"` while deriving `schema_fingerprint` from the live manifest/provenance schemas; `tests/test_doc_web_cli_contract.py` currently asserts `contract_version == "1"` but does not encode the compatibility policy; and `docs/dossier-doc-web-handoff.md` still says every provenance row must contain `source_page_number` even though the accepted schema and Story 172 proof allow `null` for pageless sources.
- **Data contracts / schemas**: likely touched surfaces are `doc_web/runtime_contract.py`, runtime-contract tests, and downstream docs. `schemas.py` may remain unchanged if the story only clarifies policy, but any additional compatibility token or contract-field change must be added there before use. The accepted `doc_web_provenance_block_v1` schema already allows `source_page_number = null` for pageless sources.
- **File sizes**: likely touch points are `doc_web/runtime_contract.py` (53 lines), `requirements.txt` (10 lines), `pyproject.toml` (33 lines), `modules/extract/unstructured_docx_intake_v1/main.py` (212 lines), `tests/test_doc_web_cli_contract.py` (161 lines), `tests/test_docx_intake_recipe.py` (81 lines), `docs/dossier-doc-web-handoff.md` (201 lines), `docs/doc-web-bundle-contract.md` (219 lines), `docs/RUNBOOK.md` (315 lines), `README.md` (190 lines), and possibly `docs/build-map.md` (581 lines). Only `docs/build-map.md` exceeds 500 lines; prefer narrow edits.
- **Decision context**: reviewed `docs/ideal.md`, `docs/build-map.md`, ADR-002, `docs/doc-web-bundle-contract.md`, `docs/dossier-doc-web-handoff.md`, Stories 156/172/173, and the current runtime-contract/tests/package metadata. No separate ADR currently defines how `contract_version` should relate to `schema_fingerprint`.

## Files to Modify

- `requirements.txt` — align the maintained runtime dependency surface with the shipped DOCX lane if the fix belongs in the repo-supported runtime install (10 lines)
- `pyproject.toml` — adjust maintained extras if the supported DOCX install shape should be expressed there instead of or in addition to `requirements.txt` (33 lines)
- `modules/extract/unstructured_docx_intake_v1/main.py` — correct misleading dependency guidance and only adjust import/runtime messaging if needed (212 lines)
- `doc_web/runtime_contract.py` — encode the chosen compatibility policy in the machine-readable contract payload (53 lines)
- `tests/test_doc_web_cli_contract.py` — add policy and clean-env runtime-surface coverage (161 lines)
- `tests/test_docx_intake_recipe.py` or a new focused clean-env smoke test — prove the maintained DOCX lane from the supported install shape (81 lines today)
- `README.md` — keep user-facing install guidance honest if the maintained DOCX surface changes (190 lines)
- `docs/RUNBOOK.md` — publish the exact maintained DOCX install/run path (315 lines)
- `docs/dossier-doc-web-handoff.md` — align downstream mandatory checks and versioning language with the actual contract policy (201 lines)
- `docs/doc-web-bundle-contract.md` — clarify contract-version versus schema-fingerprint semantics if this story settles that policy (219 lines)
- `docs/build-map.md` — update only if shipped runtime/support reality changes enough to warrant a build-map note (581 lines)

## Redundancy / Removal Targets

- Any stale wording that implies `requirements.txt` or the current maintained runtime surface already guarantees the DOCX lane when it does not
- Any stale downstream guidance that treats `source_page_number` as universally mandatory after pageless provenance was accepted
- Any ambiguous contract wording that encourages consumers to key on `contract_version` alone when the actual compatibility gate is the schema fingerprint or supported schema versions

## Notes

- This stays as one story because both findings hit the same Dossier adoption boundary: one breaks a maintained recipe at install/runtime time, and the other leaves downstream compatibility checks ambiguous once that recipe family introduced pageless provenance.
- The earlier Dossier pageless-provenance mismatch itself is not being treated as a `doc-web` bug here; the upstream-worthy part is the contract-signaling ambiguity created after the schema widened under the same coarse contract version.
- Story 173 already established that the base package is contract-only and the repo-owned smoke lanes use a separate maintained runtime surface. This story should preserve that discipline unless the evidence shows the maintained DOCX lane needs a different explicit extra or requirements shape.

## Plan

### Exploration Summary

- **Ideal alignment:** proceed. This story closes two real Ideal gaps at the Dossier-facing boundary: office-document support only matters if the maintained lane is actually runnable, and provenance only stays trustworthy if downstream compatibility signaling is explicit instead of implicit.
- **Relevant build-map state:** Category 1 now has a maintained DOCX lane, but the `docx` row is still only `has fixture`, not `passing`, so the support claim must stay narrow and honest. Category 6 owns the provenance contract, and Category 7 remains `partial`, which makes the runtime-contract ambiguity a direct handoff problem rather than a doc nit.
- **Critical substrate verified in code:** `modules/extract/unstructured_docx_intake_v1/main.py` imports `unstructured.partition.docx` and emits an error message that still points users at `requirements.txt`; `requirements.txt` pins `unstructured[pdf]==0.16.9`; `pyproject.toml` exposes a narrow `.[driver]` extra; `tests/test_docx_intake_recipe.py` proves the DOCX lane only in the ambient dev environment; `doc_web/runtime_contract.py` still hard-codes `CONTRACT_VERSION = "1"`; and `docs/dossier-doc-web-handoff.md` still requires `source_page_number` for every provenance row even though the accepted schema allows `null`.
- **Fresh runtime-surface repros captured in this pass:**
  - local default `python3` is `3.14.3`; on that interpreter, `pip install -r requirements.txt` fails before any recipe run because `unstructured==0.16.9` has no matching distribution for Python 3.14
  - on `Python 3.12.11`, `pip install '.[driver]'` succeeds, but running `recipe-docx-html-mvp.yaml` fails immediately with `No module named 'unstructured'`
  - on `Python 3.12.11`, `pip install -r requirements.txt` succeeds, but the same DOCX recipe then fails with `No module named 'docx'`, matching Dossier's upstream report
- **Fresh contract-policy repro captured in this pass:**
  - current `main` payload from `python -m doc_web contract --json` reports `contract_version = "1"` and `schema_fingerprint = "sha256:e2fd6deb7e122956974d2b9e7d210c60dc22ea8ce3f51df3531ec56c99eeef47"`
  - a temp archive of commit `28c88c2` (Story 156) run through the same `build_runtime_contract()` helper reports `contract_version = "1"` and `schema_fingerprint = "sha256:4c275e0090969b06e5615d83bc197aec461fef0d41cdb01fd25e65c4026577df"`
  - `git diff 28c88c2..8756b20` shows the consumer-visible schema widening came from Story 172 in `schemas.py`, `docs/doc-web-bundle-contract.md`, and `tests/test_doc_web_bundle_contract.py`, while `doc_web/runtime_contract.py` itself did not change
- **Small scope delta folded into the story:** if the chosen maintained DOCX install shape continues to rely on `requirements.txt`, the story must also make the supported Python story honest for that runtime surface because the current pinned `unstructured==0.16.9` does not resolve on Python 3.14. This is tightly coupled to the install-surface claim and should not be hidden as a separate surprise.

### Eval-First Gate

- **Baseline first:**
  1. `Python 3.12.11` + `pip install '.[driver]'` + maintained DOCX recipe → install succeeds, run fails with `No module named 'unstructured'`
  2. `Python 3.12.11` + `pip install -r requirements.txt` + maintained DOCX recipe → install succeeds, run fails with `No module named 'docx'`
  3. local default `Python 3.14.3` + `pip install -r requirements.txt` → install fails because `unstructured==0.16.9` is unavailable on Python 3.14
  4. contract replay at `28c88c2` versus current `main` → same `contract_version`, different schema fingerprint, with the diff isolated to the pageless-provenance schema/docs/tests
- **Decision rule:** choose the smallest fix that makes the maintained DOCX lane runnable from one explicitly supported runtime surface without widening unrelated package surfaces casually, and make the compatibility key explicit enough that a downstream consumer cannot mistake `contract_version` for the only upgrade gate.

### Implementation Outline

1. Decide and encode the maintained DOCX install surface (`S`).
   - Files: `requirements.txt`, `pyproject.toml`, `modules/extract/unstructured_docx_intake_v1/main.py`, `README.md`, `docs/RUNBOOK.md`
   - Recommended path:
     - keep the base package contract-only
     - keep Story 173's split between lightweight pinned preflight and broader maintained runtime surfaces
     - make the fuller maintained runtime surface honest for DOCX by adding the missing DOCX dependency support to `requirements.txt`
     - update the DOCX intake error message and the docs so the maintained DOCX recipe explicitly names the required install shape instead of implying users can guess
   - Alternative to evaluate during implementation if the above proves awkward:
     - add a dedicated DOCX extra rather than widening `.[driver]`, but do not silently turn `.[driver]` into a catch-all heavy runtime unless the evidence shows that is the cleanest maintained boundary
   - Done looks like: a clean Python 3.12 environment using the chosen supported install shape can run `recipe-docx-html-mvp.yaml` successfully.

2. Make the supported Python/runtime claim honest for the chosen surface (`S`).
   - Files: likely `README.md`, `docs/RUNBOOK.md`, possibly `pyproject.toml` if the chosen fix requires a narrower or more explicit Python support statement
   - Changes:
     - document which Python versions are actually supported for the maintained DOCX/full-runtime path
     - if needed, narrow or qualify the published guidance so the local Python 3.14 `requirements.txt` failure is not an undocumented trap
   - Done looks like: the runtime docs no longer overstate compatibility for the chosen DOCX install surface.

3. Define and encode the contract compatibility policy (`S`).
   - Files: `doc_web/runtime_contract.py`, `tests/test_doc_web_cli_contract.py`, `docs/dossier-doc-web-handoff.md`, `docs/doc-web-bundle-contract.md`
   - Recommended path:
     - keep `contract_version = 1` as the coarse runtime-boundary family marker
     - make `schema_fingerprint` and `supported_bundle_schema_versions` the explicit downstream compatibility gates in code comments, tests, and handoff docs
     - remove stale handoff language that still requires `source_page_number` for pageless sources
   - Stronger alternative if exploration during implementation disproves the above:
     - bump `contract_version` and propagate the new value everywhere
   - Done looks like: a downstream consumer reading the machine-readable preflight plus the handoff docs cannot reasonably infer that `contract_version` alone is sufficient.

4. Add repeatable proof for the resolved surfaces (`M`).
   - Files: `tests/test_doc_web_cli_contract.py`, `tests/test_docx_intake_recipe.py`, possibly a narrow helper script if the clean-env full-runtime proof is too heavy for the default suite
   - Changes:
     - add a clean-env proof for the maintained DOCX install shape
     - assert the intended contract-version/fingerprint policy directly in tests
   - Done looks like: future drift in either DOCX runtime support or compatibility semantics fails a focused regression check.

5. Re-run real proofs and inspect artifacts (`S`).
   - Files: verification only
   - Changes:
     - rerun the maintained DOCX recipe from the chosen supported install shape
     - validate `manifest.json` and `provenance/blocks.jsonl`
     - inspect representative pageless provenance rows plus the fresh `doc-web contract --json` output
   - Done looks like: the work log cites exact current-pass artifact paths and payload values.

### Impact Analysis

- **Primary blast radius:** package/runtime install surfaces for the maintained DOCX lane; runtime-contract semantics and downstream compatibility docs.
- **Main risks:** accidentally widening the lightweight `.[driver]` extra into a heavier runtime than Story 173 intended; leaving the Python-version story implicit; or clarifying the docs without giving downstream tests a real compatibility gate.
- **Structural health:** prefer narrow dependency/documentation changes over broad driver/package refactors. Avoid touching `schemas.py` unless the story truly needs a new machine-readable contract field or decides to bump `contract_version`.
- **Human-approval blocker:** none on architecture. The main product choice is install-surface preference: requirements-backed DOCX runtime versus a new dedicated extra. Recommendation: keep the base/runtime split from Story 173 and fix the fuller maintained runtime surface plus its docs first.
- **Relative effort:** M

### What Done Looks Like

- A clean supported environment can run the maintained DOCX recipe from one explicit repo-supported install shape without missing-module surprises.
- The downstream handoff docs and `doc-web contract --json` make it clear that compatibility gating depends on the schema fingerprint and supported schema versions unless the story explicitly chooses a `contract_version` bump.
- The pageless DOCX proof remains honest: provenance still validates with `source_page_number = null`, and the docs no longer contradict that fact.

## Work Log

20260330-1038 — story created from the next Dossier follow-up: split the new findings into one coherent `Pending` story after verifying the adjacent substrate in this checkout. Evidence: `docs/build-map.md` still marks `docx` as `has fixture`; `modules/extract/unstructured_docx_intake_v1/main.py` imports `unstructured.partition.docx` while `requirements.txt` still only declares `unstructured[pdf]==0.16.9`; `doc_web/runtime_contract.py` still hard-codes `CONTRACT_VERSION = "1"` while deriving `schema_fingerprint` from the live schemas; `tests/test_doc_web_cli_contract.py` still asserts version `1`; and `docs/dossier-doc-web-handoff.md` still requires `source_page_number` on every provenance row despite the accepted pageless DOCX contract. Next step: run the clean-env DOCX repro and contract-diff exploration, then write the implementation plan before changing code.
20260330-1117 — exploration and planning: verified `docs/ideal.md`, `docs/build-map.md`, ADR-002, `docs/doc-web-bundle-contract.md`, `docs/dossier-doc-web-handoff.md`, Stories 156/172/173, `requirements.txt`, `pyproject.toml`, `doc_web/runtime_contract.py`, `modules/extract/unstructured_docx_intake_v1/main.py`, `tests/test_doc_web_cli_contract.py`, and `tests/test_docx_intake_recipe.py`. Fresh baseline evidence:
- local default `python3` is `3.14.3`; `pip install -r requirements.txt` fails before any run because `unstructured==0.16.9` has no matching distribution on Python 3.14
- on `Python 3.12.11`, `pip install '.[driver]'` succeeded, but `python driver.py --recipe configs/recipes/recipe-docx-html-mvp.yaml --input-docx testdata/docx-mini.docx ...` failed immediately with `No module named 'unstructured'`
- on `Python 3.12.11`, `pip install -r requirements.txt` succeeded, but the same DOCX recipe failed immediately with `No module named 'docx'`, matching Dossier's reported issue
- current `python -m doc_web contract --json` on `main` reports `contract_version = "1"` with `schema_fingerprint = "sha256:e2fd6deb7e122956974d2b9e7d210c60dc22ea8ce3f51df3531ec56c99eeef47"`
- a temp archive of commit `28c88c2` (Story 156) run through `build_runtime_contract()` reports the previously reviewed fingerprint `sha256:4c275e0090969b06e5615d83bc197aec461fef0d41cdb01fd25e65c4026577df` under the same `contract_version = "1"`
- `git diff 28c88c2..8756b20` isolates the consumer-visible contract widening to Story 172 changes in `schemas.py`, `docs/doc-web-bundle-contract.md`, and `tests/test_doc_web_bundle_contract.py`, while `doc_web/runtime_contract.py` did not change and `docs/dossier-doc-web-handoff.md` still incorrectly requires `source_page_number`
Substrate conclusion: the story is buildable and the critical gaps are real. Small scope delta folded in: if the chosen DOCX install surface remains `requirements.txt`, the docs and possibly the published supported-Python story must acknowledge the Python 3.14 incompatibility surfaced by the current `unstructured` pin. Recommended path: keep the contract-only/base split from Story 173, make the maintained DOCX runtime surface honest without casually bloating `.[driver]`, and clarify in code/tests/docs that `schema_fingerprint` plus supported schema versions are the downstream compatibility gates unless the implementation chooses to bump `contract_version`. Next step: wait for user approval before implementation code.
20260330-1950 — implementation and verification: moved the story to `In Progress`, kept the base-package/driver split from Story 173, and landed an explicit `docx` extra while also fixing the fuller repo runtime surface. Changes: `requirements.txt` now uses `unstructured[docx,pdf]==0.16.9`; `pyproject.toml` adds `.[docx]`; `modules/extract/unstructured_docx_intake_v1/main.py` now points missing-DOCX users at `.[driver,docx]` or `requirements.txt`; `doc_web/runtime_contract.py` now publishes `compatibility_policy`; `tests/test_doc_web_cli_contract.py` now asserts that policy and provisions a clean-venv DOCX smoke via `.[driver,docx]`; and the README/runbook/contract/handoff/build-map/readiness docs now describe the explicit DOCX install shape and the fact that `schema_fingerprint` plus `supported_bundle_schema_versions`, not `contract_version` alone, are the downstream compatibility gates. Fresh evidence:
- `python -m pytest tests/test_doc_web_cli_contract.py -q` → `5 passed` in `72.07s`
- `python -m pytest tests/test_docx_intake_recipe.py tests/test_doc_web_bundle_contract.py -q` → `17 passed`
- `make test` → `394 passed`, with the same unrelated 4 residual warnings from `modules/portionize/portionize_headers_numeric_v1/main.py`
- `make lint` → passed
- `python driver.py --recipe configs/recipes/recipe-docx-html-mvp.yaml --input-docx testdata/docx-mini.docx --run-id story174-docx-r1 --allow-run-id-reuse --force` → success; `validate_artifact.py` returned `Validation OK` for [manifest.json](/Users/cam/.codex/worktrees/70a4/doc-web/output/runs/story174-docx-r1/output/html/manifest.json) and [blocks.jsonl](/Users/cam/.codex/worktrees/70a4/doc-web/output/runs/story174-docx-r1/output/html/provenance/blocks.jsonl); manual inspection confirmed `reading_order = ["chapter-001", "chapter-002"]` and pageless provenance rows such as `blk-chapter-001-0001` with stable `source_element_ids` and no `source_page_number`
- `python -m doc_web contract --json` now emits `compatibility_policy = {"contract_version_role": "coarse-runtime-boundary-family", "consumer_gate_fields": ["schema_fingerprint", "supported_bundle_schema_versions"]}` while keeping `contract_version = "1"` and the current fingerprint `sha256:e2fd6deb7e122956974d2b9e7d210c60dc22ea8ce3f51df3531ec56c99eeef47`
- clean Python `3.12.11` repo-runtime repro for the originally reported surface: created `/tmp/story174-req-verify-6FWnFT/venv`, ran `pip install -r requirements.txt`, then ran the maintained DOCX recipe successfully; the resulting [manifest.json](/tmp/story174-req-verify-6FWnFT/output/story174-req312-r1/output/html/manifest.json) and [blocks.jsonl](/tmp/story174-req-verify-6FWnFT/output/story174-req312-r1/output/html/provenance/blocks.jsonl) both validated
Result: the maintained DOCX lane is now runnable from both the explicit checkout DOCX extra and the broader repo runtime, and the contract-signaling ambiguity is now explicit in code/tests/docs rather than left to inference. Next step: recommend `/validate`.
20260330-2325 — validation and close-out: `/validate` confirmed all 5 acceptance-criteria groups are met and the remaining work was only close-out bookkeeping. Fresh close-out evidence:
- `python -m pytest tests/` → `394 passed`, with the same unrelated 4 residual warnings from `modules/portionize/portionize_headers_numeric_v1/main.py`
- `python -m ruff check modules/ tests/` → `All checks passed!`
- `python validate_artifact.py --schema doc_web_bundle_manifest_v1 --file output/runs/story174-docx-r1/output/html/manifest.json` → `Validation OK: 1 rows match doc_web_bundle_manifest_v1`
- `python validate_artifact.py --schema doc_web_provenance_block_v1 --file output/runs/story174-docx-r1/output/html/provenance/blocks.jsonl` → `Validation OK: 7 rows match doc_web_provenance_block_v1`
- `python validate_artifact.py --schema doc_web_bundle_manifest_v1 --file /tmp/story174-req-verify-6FWnFT/output/story174-req312-r1/output/html/manifest.json` → `Validation OK: 1 rows match doc_web_bundle_manifest_v1`
- `python validate_artifact.py --schema doc_web_provenance_block_v1 --file /tmp/story174-req-verify-6FWnFT/output/story174-req312-r1/output/html/provenance/blocks.jsonl` → `Validation OK: 7 rows match doc_web_provenance_block_v1`
- `python -m doc_web contract --json` → confirmed `compatibility_policy.consumer_gate_fields = ["schema_fingerprint", "supported_bundle_schema_versions"]` while `contract_version` remains `1`
Close-out changes: set Story 174 to `Done`, checked the validation and mark-done workflow gates, synced [docs/stories.md](/Users/cam/.codex/worktrees/70a4/doc-web/docs/stories.md), and prepared the changelog entry. Next step: `/check-in-diff`.
