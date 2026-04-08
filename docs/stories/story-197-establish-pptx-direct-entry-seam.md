---
title: "Establish the First Honest PPTX Direct-Entry Seam"
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
adr_refs: []
depends_on:
  - "193"
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
  - "pptx"
architecture_domains:
  - "doc_web_runtime"
roadmap_tags:
  - "campaign:maintained-intake-honesty"
legacy_system: ""
---

# Story 197 — Establish the First Honest PPTX Direct-Entry Seam

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md`, `docs/stories/story-175-office-document-proof-widening-and-xlsx-pptx-lane-decision.md`, `docs/stories/story-193-widen-xlsx-proof-and-recheck-pptx-runtime-seam.md`, `docs/stories/story-194-office-intake-recommendation-and-handoff-boundary.md`, `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, `testdata/README.md`, `pyproject.toml`, and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower PPTX direct-entry ADR or runbook
**Depends On**: Story 193

## Goal

`pptx` is now the strongest explicit file-family hole with real repo substrate: the project has a reproducible probe fixture, current office-native patterns from DOCX/XLSX, and a fresh measured blocker, but still no maintained PPTX runtime, recipe, or provenance contract. This story should test the smallest honest direct-entry path first: add the missing runtime substrate, verify `unstructured.partition.pptx` on `testdata/pptx-mini.pptx`, and either land a bounded maintained PPTX recipe with fresh `driver.py` artifact proof or stop with a new named blocker instead of leaving PPTX as vague residue.

## Acceptance Criteria

- [x] A fresh current-pass baseline names the exact PPTX seam from repo evidence:
  - [x] the story cites the current blocked command on `testdata/pptx-mini.pptx`,
  - [x] the story names the missing substrate already verified in repo (`pyproject.toml` had no PPTX extra, `driver.py` had no `--input-pptx`, and no maintained PPTX recipe/module existed before this pass),
  - [x] and the work log records the exact files and command outputs inspected rather than relying on older story text alone
- [x] If the native seam can reach the accepted `doc-web` boundary on the bounded probe fixture, the story lands one honest maintained direct-entry PPTX slice:
  - [x] a maintained install path exists (`.[driver,pptx]`) and is covered by a fresh isolated-smoke contract check,
  - [x] `driver.py` / `RunConfig` accept `--input-pptx` / `input_pptx`,
  - [x] a maintained PPTX recipe completes through `driver.py` on `testdata/pptx-mini.pptx`,
  - [x] and manual inspection is recorded for `elements.jsonl`, bundle report output, `output/html/manifest.json`, `output/html/provenance/blocks.jsonl`, and representative HTML pages
- [x] PPTX provenance stays source-honest on the claimed slice:
  - [x] the story records that PPTX uses slide-number anchors from Unstructured `metadata.page_number` plus `source_element_ids`,
  - [x] no fabricated printed/source page guarantees are introduced,
  - [x] and no new cross-artifact provenance fields were needed beyond `input_pptx` in `RunConfig` because the existing `source_page_number` / manifest `source_pages` fields were already sufficient
- [x] Coverage, docs, and office-boundary truth surfaces remain aligned with the outcome:
  - [x] `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, `testdata/README.md`, and the office-boundary eval surfaces now reflect maintained direct explicit recipe support instead of `runtime_blocked`
  - [x] `modules/intake/intake_plan_utils.py` and its tests now classify PPTX as a direct-entry-only office recipe rather than leaving stale `unsupported_recommended_recipe` / `runtime_blocked` behavior around the Story 194 boundary
  - [x] N/A by outcome: PPTX reached the maintained boundary in this pass, so no blocker conversion was needed

## Out of Scope

- Recommendation-only intake or approved-handoff automation expansion beyond the direct-entry boundary established in Story 194
- Full PPTX support across speaker notes, embedded media, animations, charts, complex slide-master behavior, or OCR fallback on image-heavy decks
- Reopening ADR-002 or ADR-003, or changing the accepted `doc-web` runtime boundary
- Inventing an AI-first PPTX repair path before the native `partition_pptx` seam is freshly measured on the bounded probe slice
- Treating one `pandoc`-generated probe deck as proof of broad PowerPoint support if the resulting slice is still too thin to claim honestly

## Approach Evaluation

- **Simplification baseline**: start from the native PPTX seam, not an LLM. A single model call is not the right first move because the current repo already prefers native office structure when it exists, and the measured blocker is missing runtime substrate rather than semantic ambiguity.
- **AI-only**: possible later for slide-order or mixed-layout repair, but low-value until `unstructured.partition.pptx` is actually runnable on the bounded probe fixture. AI should not become the first maintained owner of a file family whose native structure has not been honestly measured yet.
- **Hybrid**: plausible if the native seam becomes runnable and the resulting simple slide output still needs bounded help on ordering or grouping. In that case, keep native partitioning and provenance as the backbone and use AI only for the smallest inspectable repair seam.
- **Pure code**: likely strongest for the first pass. The likely initial work is dependency plumbing, `driver.py` / `RunConfig` input support, a PPTX intake module, a bundle/provenance transform that reuses the office-native helper, and focused tests.
- **Repo constraints / prior decisions**: `spec:1.1` keeps recipe ownership explicit, `C2` remains `climb`, Story 193 already proved PPTX was blocked at import time in the current checkout, and Story 194 explicitly kept PPTX outside recommendation-only automation because the runtime substrate was not maintained. ADR-002 and ADR-003 keep the Dossier-facing runtime boundary explicit and versioned.
- **Existing patterns to reuse**: `configs/recipes/recipe-docx-html-mvp.yaml`, `configs/recipes/recipe-xlsx-html-mvp.yaml`, `modules/extract/unstructured_docx_intake_v1/main.py`, `modules/extract/unstructured_xlsx_intake_v1/main.py`, `modules/transform/docx_elements_to_bundle_v1/main.py`, `modules/transform/xlsx_elements_to_bundle_v1/main.py`, `modules/common/office_native_bundle.py`, `tests/test_doc_web_cli_contract.py`, `tests/test_docx_intake_recipe.py`, `tests/test_xlsx_intake_recipe.py`, and `testdata/generate_pptx_fixture.py`
- **Eval**: the deciding proof is a fresh current-pass native probe plus a real `driver.py` run on `testdata/pptx-mini.pptx`, not promptfoo. If PPTX direct-entry support lands, rerun the Story 194 office-boundary probes so `pptx` shifts from `runtime_blocked` to the honest direct-entry-only reason; if it stays blocked, sync those same truth surfaces to the new blocker evidence.

## Tasks

- [x] Freeze the current PPTX seam from repo reality before changing code:
  - [x] rerun the exact `partition_pptx` probe on `testdata/pptx-mini.pptx`
  - [x] verify the current absence of a PPTX extra in `pyproject.toml`
  - [x] verify the current absence of `input_pptx` in `RunConfig` / `driver.py`
  - [x] verify there is still no maintained PPTX recipe/module pair in `configs/recipes/` or `modules/`
- [x] Measure the smallest honest native substrate repair before considering AI or broader architecture:
  - [x] add a maintained PPTX dependency/install path and confirm it makes `partition_pptx` runnable
  - [x] N/A by outcome: the dependency repair did not expose a deeper runtime blocker
  - [x] continue to the maintained lane only after the native seam produced inspectable PPTX elements on the bounded probe fixture
- [x] If the native seam becomes runnable, land the smallest coherent direct-entry PPTX path:
  - [x] add `input_pptx` support to `schemas.py` / `RunConfig` and `driver.py`
  - [x] add a maintained `recipe-pptx-html-mvp.yaml`
  - [x] add a PPTX intake module and a bundle/provenance transform, using the existing office-native helper for shared bundle output while keeping slide grouping specific to PPTX
  - [x] add focused recipe/tests plus an isolated install-contract smoke similar to the DOCX/XLSX extras
- [x] Run real `driver.py` verification and artifact inspection on `testdata/pptx-mini.pptx` if the lane becomes maintained:
  - [x] clear stale `*.pyc`
  - [x] run the maintained PPTX recipe through `driver.py`
  - [x] verify artifacts in `output/runs/`
  - [x] manually inspect sample JSON/JSONL and published HTML data
- [x] If PPTX direct-entry support changes documented reality:
  - [x] update `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, and `testdata/README.md`
  - [x] update `modules/intake/intake_plan_utils.py` and `tests/test_intake_plan_utils.py` so maintained PPTX support changes the honest direct-entry office boundary to `direct_entry_recipe_outside_confirmed_handoff_scope:pptx`
  - [x] rerun the Story 194 office-boundary probes and update `docs/evals/registry.yaml` now that the benchmark reasons changed from `runtime_blocked` to a maintained direct-entry boundary
- [x] N/A by outcome: the seam reached the maintained boundary, so no blocker conversion was needed
- [x] If this story changes documented format coverage or graduation reality: update `tests/fixtures/formats/_coverage-matrix.json` and keep methodology truth surfaces honest; no extra state mutation beyond the compiled graph/index was required
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove or update stale `runtime_blocked` office-boundary wording instead of leaving parallel PPTX stories of truth
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] Pipeline behavior changed: cleared stale `*.pyc`, ran `driver.py`, verified artifacts in `output/runs/`, and manually inspected sample JSON/JSONL data
  - [x] Agent tooling unchanged; `make skills-check` not required
- [x] If office-boundary eval surfaces changed: rerun them and update `docs/evals/registry.yaml`
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every support claim names the exact fixture, run ID, result file, and inspected artifact paths
  - [x] T1 — AI-First: do not add AI where the native PPTX seam and existing office patterns are sufficient
  - [x] T2 — Eval Before Build: remeasure the native seam before adding new PPTX runtime code
  - [x] T3 — Fidelity: slide content survives extraction without fabricated page guarantees or silent omission
  - [x] T4 — Modular: extend the existing office-native pattern instead of inventing a parallel PPTX subsystem
  - [x] T5 — Inspect Artifacts: manually inspect PPTX outputs, not just import success or test logs

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

- **Owning module / area**: direct office-native intake plus the `doc-web` bundle/provenance boundary for non-page-native sources. Primary ownership should mirror the existing DOCX/XLSX direct-entry seams rather than the recommendation-only intake automation.
- **Methodology reality**: this story belongs to `spec:1`, `spec:3`, `spec:6`, `spec:7`, `spec:8`, and the adjacent `spec:9` direct-entry boundary surface. In `docs/methodology/state.yaml`, `spec:1`, `spec:3`, `spec:6`, `spec:8`, and `spec:9` substrates exist, `spec:7` is still `partial`, and the relevant active phases are `C2 = climb`, `C3 = climb`, `B10 = climb`, and `B1 = hold`. The relevant coverage row now moves `pptx` from `has-fixture` to bounded `passing`.
- **Substrate evidence**: verified in repo in this pass that `testdata/pptx-mini.md`, `testdata/pptx-mini.pptx`, and `testdata/generate_pptx_fixture.py` already exist; `pyproject.toml` now exposes a maintained `pptx` extra; `schemas.py` / `RunConfig` and `driver.py` now expose `input_pptx` / `--input-pptx`; `configs/recipes/recipe-pptx-html-mvp.yaml` plus `modules/extract/unstructured_pptx_intake_v1` and `modules/transform/pptx_elements_to_bundle_v1` now provide the maintained PPTX direct-entry lane; and `tests/test_doc_web_cli_contract.py` now proves the extra in a clean venv. Fresh raw probe evidence also showed `partition_pptx(...)` returning 8 elements with real `metadata.page_number` slide anchors on the bounded checked-in fixture.
- **Data contracts / schemas**: touched contracts were `RunConfig` in `schemas.py`, `unstructured_element_v1`, `doc_web_bundle_manifest_v1`, and `doc_web_provenance_block_v1`. No new slide-specific schema field beyond `input_pptx` was required because existing manifest `source_pages` and provenance `source_page_number` already supported honest slide-number anchors.
- **File sizes**: current likely touch points are `pyproject.toml` (42 lines), `driver.py` (2250), `schemas.py` (1237), `modules/intake/intake_plan_utils.py` (307), `modules/extract/unstructured_docx_intake_v1/main.py` (215), `modules/extract/unstructured_xlsx_intake_v1/main.py` (166), `modules/transform/docx_elements_to_bundle_v1/main.py` (170), `modules/transform/xlsx_elements_to_bundle_v1/main.py` (126), `modules/common/office_native_bundle.py` (359), `tests/test_doc_web_cli_contract.py` (306), `tests/test_docx_intake_recipe.py` (114), `tests/test_xlsx_intake_recipe.py` (124), `tests/test_intake_plan_utils.py` (268), `testdata/generate_pptx_fixture.py` (43), `testdata/README.md` (106), `README.md` (293), `docs/RUNBOOK.md` (477), `tests/fixtures/formats/_coverage-matrix.json` (490), and `docs/evals/registry.yaml` (1664). Oversized files to keep especially surgical are `driver.py`, `schemas.py`, and `docs/evals/registry.yaml`.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, ADR-003, Stories 175/193/194, the current `pptx` coverage row, `pyproject.toml`, `driver.py`, `schemas.py`, `README.md`, `docs/RUNBOOK.md`, and `testdata/README.md`. No narrower PPTX-specific ADR or runbook already resolves this work.

## Files to Modify

- `pyproject.toml` — add a maintained PPTX optional dependency path if the native seam becomes runnable with bounded package changes (42 lines)
- `schemas.py` — add `input_pptx` to `RunConfig` if a maintained direct-entry lane lands (1237 lines)
- `driver.py` — add `--input-pptx` plumbing and recipe input override handling if the lane becomes maintained (2250 lines)
- `modules/intake/intake_plan_utils.py` — add PPTX to the direct-entry office boundary table if a maintained recipe lands so Story 194 surfaces stay honest (307 lines)
- `configs/recipes/recipe-pptx-html-mvp.yaml` — maintained PPTX direct-entry recipe on the bounded probe slice (new file)
- `modules/extract/unstructured_pptx_intake_v1/main.py` — PPTX-native intake patterned after the existing DOCX/XLSX unstructured seams if the import path clears (new file)
- `modules/transform/pptx_elements_to_bundle_v1/main.py` — PPTX bundle/provenance transform or the smallest honest generalization of the office-native helper (new file)
- `modules/common/office_native_bundle.py` — extend only if a shared PPTX render/provenance helper is honestly better than duplicating office output code (359 lines)
- `tests/test_doc_web_cli_contract.py` — add isolated install/smoke coverage for a maintained PPTX extra if one lands (306 lines)
- `tests/test_pptx_intake_recipe.py` — focused PPTX direct-entry smoke coverage on `testdata/pptx-mini.pptx` (new file)
- `tests/test_intake_plan_utils.py` and Story 194 office-boundary tests — update only if the maintained PPTX result changes the explicit boundary reason from `runtime_blocked` to `direct_entry_recipe_only` (268 lines plus sibling test files)
- `testdata/README.md` — describe the post-story PPTX seam honestly (106 lines)
- `README.md` — align the user-facing office support description with the maintained PPTX outcome (293 lines)
- `docs/RUNBOOK.md` — publish the verified PPTX direct-entry command or the fresh blocker state (477 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — update the `pptx` row to the exact post-story truth (490 lines)
- `docs/evals/registry.yaml` — update office-boundary benchmark history only if the Story 194 surfaces materially change (1664 lines)

## Redundancy / Removal Targets

- The special `pptx:runtime_blocked` scope reason in the Story 194 office-boundary surfaces if PPTX becomes a maintained direct-entry lane
- Any stale docs that still describe PPTX only as an import-seam blocker once a maintained recipe/test lane exists
- Any ad hoc one-off PPTX probe commands or notes that become redundant after a maintained direct-entry recipe and smoke test land

## Notes

- New story justification: reopening Story 193 would blur an already-validated XLSX widening story with a new runtime/build surface. Story 193 stopped at a fresh measured blocker; this story is the first one whose success surface is “make PPTX directly runnable and prove it” rather than “recheck whether it is still blocked.”
- The existing direct explicit-recipe interface is already the honest operator surface here. This story does not need a new UI slice; recommendation-only intake and approved handoff remain owned by Story 194 unless fresh PPTX direct-entry support forces those truth surfaces to change.
- If the simple `pptx-mini` probe immediately reveals a broader slide-order or provenance question that cannot be settled inside the current office-native pattern, stop and record that architecture question explicitly instead of sneaking it through as “just one more file family.”

## Plan

Current baseline in this pass:
- `python - <<'PY' ... from unstructured.partition.pptx import partition_pptx ... PY` on `testdata/pptx-mini.pptx` still fails immediately with `ModuleNotFoundError: No module named 'pptx'`
- `pyproject.toml` still has `docx` / `xlsx` extras only, `schemas.py` / `driver.py` still expose only `input_docx` / `input_xlsx`, and `configs/recipes/`, `modules/extract/`, and `modules/transform/` still have no maintained PPTX lane
- The bounded fixture is intentionally small and slide-shaped: `testdata/pptx-mini.md` yields a title slide plus two content slides (`Slide One`, `Slide Two`) with a list and a paragraph, so the first honest success surface is a bounded three-entry PPTX direct lane, not broad PowerPoint support

Relevant methodology context:
- This work closes an Ideal gap rather than polishing a compromise in place: `pptx` is still the strongest office-family coverage hole with a checked-in probe fixture
- Expected truth-surface movement is either `pptx: has-fixture -> passing` on a bounded maintained slice or `pptx: has-fixture -> blocked with a fresher named runtime blocker`
- The active constraints remain `C2 = climb`, `C3 = climb`, `B10 = climb`, `B1 = hold`, with `spec:7` still only `partial`

Implementation sequence after approval:
1. Dependency gate and native-seam proof (`S`)
   - Files: `pyproject.toml`, `tests/test_doc_web_cli_contract.py`
   - Change: add a maintained `pptx` extra mirroring the current DOCX/XLSX version pin, then add the smallest isolated install/probe smoke so `.[driver,pptx]` is proven in a clean venv before broader runtime wiring
   - Risk: dependency resolution or supported-Python differences may still prevent `partition_pptx` import even after the extra exists; if that happens, stop and convert the story to `Blocked` instead of writing a fake recipe/module layer
   - Done looks like: a fresh clean-environment check can import `unstructured.partition.pptx` and produce inspectable elements from `testdata/pptx-mini.pptx`
2. Driver and recipe plumbing (`S`)
   - Files: `schemas.py`, `driver.py`, `configs/recipes/recipe-pptx-html-mvp.yaml`
   - Change: add `input_pptx` / `--input-pptx`, mirror the existing DOCX/XLSX override flow, and add the maintained PPTX recipe skeleton pointing at the new intake/transform modules
   - Risk: `driver.py` and `schemas.py` are oversized, schema-stamped, and easy to edit sloppily; keep the patch surgical and parallel to the existing office-native branches only
   - Done looks like: `driver.py --recipe configs/recipes/recipe-pptx-html-mvp.yaml --input-pptx testdata/pptx-mini.pptx ...` can launch the lane end-to-end
3. Thin PPTX intake + bundle path (`M`)
   - Files: `modules/extract/unstructured_pptx_intake_v1/main.py`, `modules/transform/pptx_elements_to_bundle_v1/main.py`, and only if needed `modules/common/office_native_bundle.py` / `schemas.py`
   - Change: implement the intake module as a DOCX/XLSX-style Unstructured sibling with clear missing-extra guidance, then inspect the raw PPTX element metadata before deciding the honest bundle grouping. Default target is slide-scoped entries with provenance anchored by `source_element_ids`; only add new schema fields if Unstructured exposes a real slide anchor that the stamped outputs need explicitly
   - Risk: PPTX may expose slide metadata differently from DOCX/XLSX (`page_number`, title metadata, or only raw element IDs). The transform should follow the raw element reality from the fresh probe rather than invent page semantics or over-generalize `office_native_bundle.py`
   - Done looks like: the lane writes `elements.jsonl`, a bundle report, `output/html/manifest.json`, `output/html/provenance/blocks.jsonl`, and at least one representative HTML page with an explicitly recorded slide-anchor model
4. Tests and boundary truth alignment (`M`)
   - Files: `tests/test_pptx_intake_recipe.py`, `tests/test_doc_web_cli_contract.py`, `modules/intake/intake_plan_utils.py`, `tests/test_intake_plan_utils.py`, `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, `testdata/README.md`, and Story 194 / `docs/evals/registry.yaml` surfaces only if the maintained boundary reason changes
   - Small scope expansion already folded in: if PPTX lands, add it to `DIRECT_ENTRY_ONLY_RECIPES` so confirmed handoff reports `direct_entry_recipe_outside_confirmed_handoff_scope:pptx` instead of stale `unsupported_recommended_recipe` / `runtime_blocked` wording
   - Risk: Story 194 office-boundary tests and helper expectations currently assume PPTX is unsupported; update only the explicit direct-entry boundary slice, not the broader recommendation-only intake automation
   - Done looks like: recipe smoke, isolated extra smoke, direct-entry boundary tests, and repo docs all describe the same PPTX outcome
5. Real pipeline verification and stop condition (`M`)
   - Files: no new implementation files expected here; this is the required proof pass through `driver.py`
   - Change: clear stale `*.pyc`, run the maintained PPTX recipe on `testdata/pptx-mini.pptx`, inspect `01_unstructured_pptx_intake_v1/elements.jsonl`, the bundle report, `output/html/manifest.json`, `output/html/provenance/blocks.jsonl`, and at least one HTML page, then record exact artifact paths and sample content in the work log
   - Risk: a green run without honest slide anchors or visibly correct HTML would still fail the story; artifact inspection is the gate, not the exit code
   - Done looks like: the story can name the exact run ID, artifact paths, and checked sample content, or else it switches to `Blocked` with a named blocker and fresh evidence

Human-approval blockers before implementation:
- New maintained runtime dependency surface: add a `pptx` optional extra in `pyproject.toml`
- New explicit CLI / schema surface: add `input_pptx` to `RunConfig` and `--input-pptx` to `driver.py`
- Possible adjacent boundary update: add PPTX to `modules/intake/intake_plan_utils.py` only if the maintained direct-entry recipe exists

Approach choice:
- `AI-only` is still the wrong first move because the current failure is an import/runtime seam, not a semantic extraction problem
- `Pure code + native Unstructured partitioning` remains the simplest honest first pass
- If the native seam produces elements but the slide grouping is ambiguous, the first plan response is still to inspect the raw metadata and keep provenance explicit, not to jump to an LLM repair layer

## Work Log

20260408-1632 — create-story: created Story 197 after `/triage` identified PPTX as the strongest remaining actionable format gap and the user approved that next action. Evidence reviewed in this pass: `tests/fixtures/formats/_coverage-matrix.json` still marks `pptx` as `has-fixture`; `testdata/pptx-mini.md`, `testdata/pptx-mini.pptx`, and `testdata/generate_pptx_fixture.py` prove the repo already has a reproducible probe fixture; `pyproject.toml`, `schemas.py`, and `driver.py` still expose DOCX/XLSX direct-entry support but no PPTX counterpart; Story 193 recorded a fresh `ModuleNotFoundError: No module named 'pptx'`; and Story 194 kept PPTX explicitly outside recommendation-only automation for that reason. Result: a new `Pending` story is honest because the direct-entry office-native substrate pattern already exists in repo, while the missing PPTX-specific substrate is exactly the work this story should try. Next step: `/build-story` should rerun the native PPTX probe, test the smallest dependency repair, and then either land a bounded maintained PPTX recipe/provenance proof or convert the story to `Blocked` with fresh evidence.
20260408-1254 — /build-story exploration: read `/Users/cam/Documents/Projects/doc-web/.agents/skills/build-story/SKILL.md` and rechecked the governing context in this pass: `docs/ideal.md`; `docs/spec.md` (`spec:1`, `spec:1.1`, `spec:3`, `spec:3.1`, `spec:6`, `spec:7`, `spec:8`, `spec:9`); `docs/methodology/state.yaml`; `docs/methodology/graph.json`; ADR-002; ADR-003; Stories 193 and 194; `tests/fixtures/formats/_coverage-matrix.json`; `pyproject.toml`; `driver.py`; `schemas.py`; `modules/extract/unstructured_docx_intake_v1/main.py`; `modules/extract/unstructured_xlsx_intake_v1/main.py`; `modules/transform/docx_elements_to_bundle_v1/main.py`; `modules/transform/xlsx_elements_to_bundle_v1/main.py`; `modules/common/office_native_bundle.py`; `modules/intake/intake_plan_utils.py`; `tests/test_docx_intake_recipe.py`; `tests/test_xlsx_intake_recipe.py`; `tests/test_doc_web_cli_contract.py`; `tests/test_intake_plan_utils.py`; `README.md`; `docs/RUNBOOK.md`; `testdata/README.md`; `testdata/pptx-mini.md`; and `testdata/generate_pptx_fixture.py`. Fresh baseline today: `python - <<'PY' ... from unstructured.partition.pptx import partition_pptx ... PY` against `testdata/pptx-mini.pptx` still fails with `ModuleNotFoundError: No module named 'pptx'`; repo evidence still shows no `pptx` extra in `pyproject.toml`, no `input_pptx` / `--input-pptx` in `schemas.py` / `driver.py`, and no PPTX recipe or extract/transform module under `configs/recipes/`, `modules/extract/`, or `modules/transform/`. Relevant methodology state remains `spec:1/3/6/8/9 = exists`, `spec:7 = partial`, `C2/C3/B10 = climb`, and `B1 = hold`; the `pptx` coverage row remains `has-fixture`. Files likely to change if the seam clears: `pyproject.toml`, `schemas.py`, `driver.py`, new PPTX recipe + extract/transform modules, `tests/test_doc_web_cli_contract.py`, new PPTX recipe smoke coverage, and truth surfaces in `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, and `testdata/README.md`. Files at risk: oversized `driver.py`, oversized `schemas.py`, and the Story 194 office-boundary helpers/tests that currently treat PPTX as unsupported. Patterns to follow: thin DOCX/XLSX-style Unstructured intake siblings, shared `modules/common/office_native_bundle.py`, and isolated extra-install smokes in `tests/test_doc_web_cli_contract.py`. Potential redundancy if PPTX lands: stale `runtime_blocked` wording in Story 194 boundary surfaces and docs. Surprise found: the only coherent adjacent scope expansion needed is adding PPTX to `modules/intake/intake_plan_utils.py` so confirmed-handoff truth stays aligned once a maintained direct-entry recipe exists. Next step: wait for approval before touching runtime code.
20260408-1320 — implementation: the dependency gate cleared and the bounded maintained PPTX lane now exists end-to-end. Added `pptx = ["unstructured[pptx]==0.16.9"]` to `pyproject.toml`, installed `.[driver,pptx]`, and reran the native probe: `partition_pptx(filename="testdata/pptx-mini.pptx")` now returns 8 elements with real `metadata.page_number` slide anchors. Added `input_pptx` / `--input-pptx` in `schemas.py` and `driver.py`, created `configs/recipes/recipe-pptx-html-mvp.yaml`, added `modules/extract/unstructured_pptx_intake_v1` and `modules/transform/pptx_elements_to_bundle_v1`, and extended `modules/common/office_native_bundle.py` only enough to pass through optional source-page anchors without perturbing DOCX/XLSX defaults. The maintained PPTX transform keeps the title slide plus two content slides as three explicit entries, normalizes nested PPTX `Title` elements with `category_depth > 0` into list items on the bounded probe, and uses existing `source_page_number` / manifest `source_pages` fields instead of inventing new schema fields. Story 194 boundary truth also moved in the same pass: `modules/intake/intake_plan_utils.py`, `benchmarks/scripts/intake_scope.py`, `tests/test_auto_book_type_detection_benchmark.py`, `tests/test_approved_intake_handoff_benchmark.py`, `tests/test_intake_plan_utils.py`, and `docs/evals/registry.yaml` now treat `pptx` the same as `docx` / `xlsx` for automation scope purposes: maintained direct explicit recipe, not `runtime_blocked`. Fresh targeted verification in this pass: `python -m pytest tests/test_pptx_intake_recipe.py tests/test_doc_web_cli_contract.py tests/test_intake_plan_utils.py tests/test_auto_book_type_detection_benchmark.py tests/test_approved_intake_handoff_benchmark.py -q` → `38 passed in 206.33s`.
20260408-1320 — driver-proof + docs: ran the real maintained lane through `driver.py` with `story197-pptx-proof-20260408` after clearing stale `*.pyc`. Manual artifact inspection:
  - `output/runs/story197-pptx-proof-20260408/01_unstructured_pptx_intake_v1/elements.jsonl` contains 8 stamped elements; sampled rows confirm `Office Probe Slides` on `page_number = 1`, `Slide One` plus `Ada` / `Lin` on `page_number = 2`, and `Slide Two` plus the narrative sentence on `page_number = 3`
  - `output/runs/story197-pptx-proof-20260408/output/html/manifest.json` records `reading_order = ["page-001", "page-002", "page-003"]` and `source_pages = [1] / [2] / [3]`
  - `output/runs/story197-pptx-proof-20260408/output/html/provenance/blocks.jsonl` contains 6 rows with `source_page_number = 1, 2, 2, 2, 3, 3` and stable `source_element_ids`
  - `output/runs/story197-pptx-proof-20260408/output/html/page-002.html` renders `<h1>Slide One</h1>` plus an unordered list with `Ada` and `Lin`; `page-003.html` renders the narrative slide paragraph cleanly
  - fresh schema checks on those artifacts passed via `python validate_artifact.py --schema doc_web_bundle_manifest_v1 ...` and `python validate_artifact.py --schema doc_web_provenance_block_v1 ...`
  Reran the Story 194 office-boundary probes with the new runtime: `benchmarks/results/auto-book-type-detection-story197-office-boundary.json` and `benchmarks/results/approved-intake-handoff-story197-office-boundary.json` now show `docx`, `xlsx`, and `pptx` all blocked at `failure_step = scope` with `scope_policy = direct_explicit_recipe_only`. Updated `README.md`, `docs/RUNBOOK.md`, `testdata/README.md`, `tests/fixtures/formats/_coverage-matrix.json`, and `docs/evals/registry.yaml` to match that exact current state.
20260408-1320 — verification: `make lint` → pass. `make test` → `484 passed, 4 warnings in 275.48s (0:04:35)`. Methodology views still need one final compile after this story-file update; next step is to regenerate `docs/methodology/graph.json` and `docs/stories.md`, then hand off for `/validate`.
20260408-1347 — validation follow-up fix: `/validate` found one remaining install-truth mismatch after the PPTX lane landed. Fresh repo evidence showed `requirements.txt` still pinned `unstructured[docx,pdf,xlsx]==0.16.9` while `README.md`, `docs/RUNBOOK.md`, and the PPTX intake module all claimed `python -m pip install -r requirements.txt` supported PPTX. Fixed that mismatch by widening the repo runtime line to `unstructured[docx,pdf,pptx,xlsx]==0.16.9`, aligning the README/runbook/install hints, and adding a new clean-venv proof in `tests/test_doc_web_cli_contract.py` that installs `-r requirements.txt` and imports `unstructured.partition.pptx`. Also tightened the office-runtime smoke tests so DOCX/XLSX/PPTX clean-venv proofs all encode the documented Python 3.11/3.12 support boundary. Fresh verification in this pass: `python -m pytest -q tests/test_doc_web_cli_contract.py -k "extra_supports_repo_owned or requirements_txt_supports_pptx"` → `5 passed, 3 deselected in 340.92s`; `python -m pytest -q tests/test_pptx_intake_recipe.py` → `2 passed in 5.24s`. Result: the previous validation gap is closed and the story now has fresh evidence behind the validation gate, but `/mark-story-done` is still the remaining close-out step.
20260408-1357 — `/mark-story-done` close-out: marked Story 197 `Done` after fresh close-out validation confirmed the bounded PPTX direct-entry lane and the repaired install-truth surface on the current tip. Fresh close-out evidence in this pass: `python -m pytest tests/` → `485 passed, 4 warnings in 408.40s (0:06:48)`; `python -m ruff check modules/ tests/` → pass; `python -m pytest -q tests/test_doc_web_cli_contract.py -k "extra_supports_repo_owned or requirements_txt_supports_pptx"` → `5 passed, 3 deselected in 340.92s`; `python -m pytest -q tests/test_pptx_intake_recipe.py` → `2 passed in 5.24s`; and the previously verified `story197-pptx-proof-20260408` artifacts still provide the required real-run bundle/provenance evidence for this story’s success surface. Impact: Story 197 now closes with a maintained PPTX runtime seam, honest slide-number provenance on the bounded probe slice, aligned office-boundary truth surfaces, and a verified `requirements.txt` install path for PPTX on the supported Python range. Next step: `/check-in-diff`.
