# Story 156 — Adopt Storybook-Style Pinned `doc-web` Runtime Pattern and Close Dossier Readiness Gaps

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Traceability is the Product, Dossier-ready output, Graduate, don't accumulate
**Spec Refs**: spec:6 (Validation, Provenance & Export), spec:7 (Graduation & Dossier Handoff)
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/doc-web-bundle-contract.md`, `docs/dossier-doc-web-handoff.md`, `docs/notes/standalone-dossier-intake-runtime-plan.md`, `docs/notes/doc-web-dossier-readiness-gap-analysis.md`, `/Users/cam/Documents/Projects/Storybook/storybook/dossier-runtime.json`, `/Users/cam/Documents/Projects/Storybook/storybook/scripts/dossier-runtime.mjs`, `/Users/cam/Documents/Projects/Storybook/storybook/packages/backend/src/ai/dossier-runtime.ts`, `/Users/cam/Documents/Projects/Storybook/storybook/packages/backend/src/ai/dossier-adapter.ts`, `/Users/cam/Documents/Projects/Storybook/storybook/docs/runbooks/dossier-runtime.md`
**Depends On**: Story 151, Story 152, Story 153, Story 154, Story 155

## Goal

Make `doc-web` presentable to Dossier as a real pinned dependency, not just a contract doc set and fixture pack. Storybook already proved the right consumer pattern for an AI-heavy repo dependency: repo-owned pin manifest, pinned install root, explicit install/check-upstream/bump commands, pinned-by-default with explicit local overrides, contract preflight, and deploys built from a pinned source snapshot. This story ports that pattern to `doc-web` at the boundary where it belongs: `doc-web` must expose an installable package/CLI, a machine-readable contract preflight, and a live build path that actually emits the published Dossier bundle contract. The result should be that Dossier can adopt `doc-web` through a narrow, versioned runtime surface instead of a sibling checkout or whole-repo dependency.

## Acceptance Criteria

- [x] `doc-web` exposes an installable runtime surface from this repo, with package metadata, explicit Python requirement, version source, and a supported CLI entry point rather than relying on `driver.py` or ambient source checkout semantics.
- [x] `doc-web` exposes a machine-readable preflight surface, such as `doc-web contract --json`, that returns enough data for a downstream consumer to block incompatible upgrades:
  - contract name and version
  - schema fingerprint or equivalent compatibility token
  - package/runtime version
  - Python requirement
  - supported bundle schema versions
- [x] A real current-repo `driver.py` path emits the Dossier-facing bundle contract from source data, not only committed fixture packs:
  - `manifest.json` validating as `doc_web_bundle_manifest_v1`
  - `provenance/blocks.jsonl` validating as `doc_web_provenance_block_v1`
  - HTML documents with matching stable `blk-*` anchors
  - manual artifact inspection recorded with exact artifact paths and sample rows
- [x] Repo docs publish the Storybook-style consumer pattern in `doc-web` terms:
  - repo-owned pin manifest shape
  - pinned install root under `.runtime/`
  - install / check-upstream / bump flow
  - pinned-by-default policy with explicit local override requirements
  - source snapshot / deploy expectations
- [x] The readiness gap analysis is updated to reflect final state, separating:
  - gaps closed in this story
  - remaining Dossier-only downstream work
  - later non-blocking improvements such as performance and new formats

## Out of Scope

- Implementing the Dossier-side adapter or runtime-management scripts in the Dossier repo itself
- Performance tuning, OCR quality work, or adding new document formats
- Replacing `driver.py` as the doc-forge R&D orchestrator
- Private package-registry infrastructure if tagged releases plus contract tests remain sufficient
- Visual website theming, publication UX, or presentation polish beyond the structural bundle contract

## Approach Evaluation

- **Simplification baseline**: First prove whether a thin package/CLI wrapper around the current repo plus the existing frozen contract is enough. If an isolated install can expose `doc-web contract --json` and the live builder can already emit the published bundle surfaces, then the remaining work is mostly packaging and docs. If the live build still only writes transitional artifacts, baseline fails and emitter/runtime work must be folded in.
- **AI-only**: An LLM can draft the pin-manifest shape and the preflight JSON contract, but it cannot prove that pip installation, CLI entry points, version metadata, or live emitted bundles actually work.
- **Hybrid**: Reuse the Storybook runtime pattern as the operator model, then implement and verify the minimal `doc-web` surfaces with real install smoke, contract smoke, and `driver.py` artifact inspection. This is the leading candidate because the problem is half boundary design and half executable plumbing.
- **Pure code**: Point Dossier at this repo directly, tell it to run `driver.py`, or rely on a sibling checkout and environment variables. Fastest to wire, but it directly violates ADR-002's standalone-runtime boundary and reproduces the same ambiguity the handoff stories were meant to eliminate.
- **Repo constraints / prior decisions**: ADR-002 settled the target model: standalone `doc-web`, tagged SemVer releases, explicit version pins, and contract tests. Story 152 froze the bundle/provenance contract. Story 154 froze the downstream handoff pack. Story 155 removed legacy surfaces that would otherwise pollute the dependency boundary. The current repo still has no `pyproject.toml`, no package version source, no contract-preflight CLI, and a live builder path that still writes `chapter_html_manifest_v1` rows from `modules/build/build_chapter_html_v1/main.py`.
- **Existing patterns to reuse**: `docs/dossier-doc-web-handoff.md`, `docs/doc-web-bundle-contract.md`, `tests/test_doc_web_bundle_contract.py`, `validate_artifact.py`, and the Storybook dependency-management pattern under `/Users/cam/Documents/Projects/Storybook/storybook/`.
- **Eval**: The deciding proof is an isolated install plus runtime preflight plus a real current-repo bundle build. Success is falsified if `doc-web contract --json` cannot be executed from an installed target, or if the live `driver.py` path still diverges from the published Dossier-facing contract.

## Tasks

- [x] Refresh and lock the readiness baseline in `docs/notes/doc-web-dossier-readiness-gap-analysis.md`:
  - classify `ready now`, `doc-web blockers`, `Dossier-only downstream work`, and `later/non-blocking improvements`
  - cite exact evidence for each blocker so the story does not drift into vague "packaging later" language
- [x] Add an installable `doc-web` package surface:
  - create package metadata (`pyproject.toml` or equivalent)
  - declare supported Python version explicitly
  - expose package version from code rather than story prose or changelog conventions
  - add a supported CLI entry point
- [x] Add a machine-readable runtime preflight surface:
  - `doc-web contract --json` or equivalent
  - contract name/version
  - schema fingerprint or compatibility token
  - bundle schema support
  - runtime/package version and Python requirement
- [x] Align the live current-repo bundle emission path with the published Dossier contract:
  - emit `manifest.json`
  - emit `provenance/blocks.jsonl`
  - ensure stable `blk-*` DOM ids match provenance rows
  - validate the emitted artifacts with `validate_artifact.py`
- [x] Add focused install and contract smoke coverage:
  - isolated local install test for the package/CLI
  - preflight JSON contract test
  - regression coverage tying fresh emitted outputs back to `doc_web_bundle_manifest_v1` and `doc_web_provenance_block_v1`
- [x] Add a repo-owned fixture-backed `driver.py` validation lane for the active `doc-web` path:
  - commit minimal `pages_html`, `portion_hypothesis`, and `illustration_manifest` fixture inputs plus the image asset they reference
  - add a narrow recipe that exercises `load_artifact_v1` + `build_chapter_html_v1` without depending on `/tmp` or ambient historical `output/runs/` state
  - use that lane for the story’s required artifact inspection and future smoke guidance
- [x] Publish the consumer/operator pattern in repo docs:
  - repo-owned pin manifest shape for Dossier
  - install / check-upstream / bump sequence
  - explicit `pinned` default and `local` override rules
  - deploy/source-snapshot expectations
  - split between doc-web-owned work and Dossier-owned work
- [x] Expand repo verification targets to cover the new runtime package surface:
  - ensure `make lint` checks the new `doc_web/` package
  - update any adjacent developer guidance that would otherwise leave the new runtime code outside the normal quality gate
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] Clear stale `*.pyc`, run through `driver.py`, verify bundle artifacts in `output/runs/`, and manually inspect sample JSON/JSONL + HTML data
  - [x] Agent tooling did not change, so `make skills-check` was not required
- [x] If evals or goldens changed materially: run `/improve-eval` and update `docs/evals/registry.yaml` (not needed; no eval or golden contract changed materially)
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: the installable runtime still preserves bundle and block provenance rather than hiding it behind packaging
  - [x] T1 — AI-First: keep the dependency boundary thin; do not rebuild intelligence in deterministic wrappers
  - [x] T2 — Eval Before Build: prove a thin package/CLI plus contract smoke is insufficient before adding heavier release infrastructure
  - [x] T3 — Fidelity: live emitted bundle output matches the published contract without dropping source mappings
  - [x] T4 — Modular: separate doc-web runtime ownership cleanly from Dossier consumer ownership and doc-forge R&D orchestration
  - [x] T5 — Inspect Artifacts: inspect real emitted bundle files, not just fixture packs or test logs

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: This story spans the runtime boundary layer, not the full pipeline. The owning surfaces are package metadata, a new `doc_web` CLI/preflight package area, the current structural bundle emitter path, and the handoff/runbook docs Dossier will read.
- **Data contracts / schemas**: `doc_web_bundle_manifest_v1` and `doc_web_provenance_block_v1` remain the canonical downstream bundle schemas. If the runtime preflight JSON becomes a durable machine contract, it should be structured and test-backed rather than emitted ad hoc. Any new emitted artifact fields still need `schemas.py` coverage so stamping does not drop them.
- **File sizes**: `modules/build/build_chapter_html_v1/main.py` is 1345 lines and `schemas.py` is 1215 lines, so new package/CLI logic should not be stuffed into either file. `README.md` is 80 lines, `docs/RUNBOOK.md` is 167 lines, `docs/doc-web-bundle-contract.md` is 218 lines, `docs/dossier-doc-web-handoff.md` is 148 lines, `validate_artifact.py` is 112 lines, and `tests/test_doc_web_bundle_contract.py` is 294 lines.
- **Decision context**: Reviewed `docs/ideal.md`, `docs/spec.md` (`spec:6`, `spec:7`), ADR-002, the extraction-plan note, the frozen contract docs, the current bundle-contract tests, the live `build_chapter_html_v1` emitter path, and Storybook's pinned-Dossier runtime surfaces. No new ADR is required unless implementation changes the accepted release/dependency model rather than merely making it executable.

## Files to Modify

- README.md — clarify the installable runtime boundary and point readers at the pinned-consumer flow (80 lines)
- docs/RUNBOOK.md — add operator guidance for runtime install, contract preflight, bundle smoke, and release verification (167 lines)
- docs/doc-web-bundle-contract.md — update only if live runtime packaging or preflight work reveals a true contract ambiguity (218 lines)
- docs/dossier-doc-web-handoff.md — align downstream expectations with the real package/CLI/preflight surface and the Storybook-style consumption model (148 lines)
- docs/notes/standalone-dossier-intake-runtime-plan.md — record the pinned-runtime milestone and what still remains Dossier-side afterward (105 lines)
- docs/notes/doc-web-dossier-readiness-gap-analysis.md — baseline and close out the blocker inventory (new file)
- Makefile — extend lint/format/check-size coverage to the new runtime package surface
- pyproject.toml — define package metadata, Python support, version source, and CLI entry points (new file)
- doc_web/__init__.py — expose runtime version and contract metadata from code (new file)
- doc_web/cli.py — implement `contract --json` and any narrow runtime-preflight commands (new file)
- doc_web/runtime_contract.py — centralize contract metadata and schema-fingerprint calculation if needed (new file)
- configs/recipes/doc-web-fixture-bundle-smoke.yaml — committed fixture-backed `driver.py` validation lane for the active bundle surface (new file)
- tests/fixtures/doc_web_bundle_smoke/ — minimal page HTML, portions, illustration manifest, and image asset for the committed smoke lane (new directory)
- modules/build/build_chapter_html_v1/main.py — ensure the live current-repo path emits the published bundle surfaces (1345 lines)
- schemas.py — preserve any emitted bundle/provenance fields that cross artifact boundaries (1215 lines)
- validate_artifact.py — keep bundle/provenance validation wired into package and smoke flows (112 lines)
- tests/test_doc_web_bundle_contract.py — extend coverage to fresh emitted outputs and runtime-preflight behavior (294 lines)
- tests/test_doc_web_cli_contract.py — isolated install/preflight regression coverage (new file)

## Redundancy / Removal Targets

- Any documentation that still implies Dossier should depend on a sibling checkout or the whole repo instead of a versioned runtime surface
- Any workflow that treats `driver.py` as the downstream consumer interface rather than an R&D orchestration tool
- Any ambiguity between ADR-002's SemVer pinning model and the repo's currently non-executable release metadata
- Any ad hoc local override guidance that does not require explicit `local` source configuration

## Notes

- Storybook is the pattern donor, not the code destination. The important part is the operating model: repo-owned pin, pinned-by-default, explicit local override, install metadata, preflight contract, and source snapshot for deploy builds.
- The biggest current blocker is not missing docs; it is the gap between the published handoff contract and the live current-repo install/build surface.
- Dossier-side code remains a downstream story after this one. This story should make that downstream work boring and unambiguous.

## Plan

### Eval Baseline

- Contract regression baseline:
  - `python -m pytest tests/test_doc_web_bundle_contract.py -q`
  - Result: `13 passed`
  - Interpretation: the frozen contract docs, schemas, and committed handoff pack are healthy.
- Installability baseline:
  - `python -m pip install --disable-pip-version-check --target <tmp>/site-packages .`
  - Result: exit `1` with `ERROR: Directory '.' is not installable. Neither 'setup.py' nor 'pyproject.toml' found.`
  - Interpretation: the runtime boundary is still non-installable.
- Live bundle baseline:
  - fixture-backed `driver.py` run using `load_artifact_v1` + `build_chapter_html_v1`
  - Result: `4/6` expected bundle surfaces present
  - Present: `chapters_manifest_fixture.jsonl`, `index.html`, `page-001.html`, `page-002.html`
  - Missing: `output/html/manifest.json`, `output/html/provenance/blocks.jsonl`
  - Interpretation: current code still proves only the transitional builder surface, not the final Dossier-facing contract.

### Small Scope Expansion Folded Into This Story

- Add a committed fixture-backed smoke lane for the active `doc-web` path.
  - Rationale: the only recent real `driver.py` validation recipe lives in ignored `output/runs/` snapshots and points at `/tmp`, so it is not a durable verification surface for this story or for future bumps.
- Expand repo quality gates to include the new `doc_web/` package.
  - Rationale: introducing a new runtime package while leaving `make lint` blind to it would make the story’s stated verification incomplete.

### Implementation Order

1. Add package metadata and a minimal `doc_web` package surface.
   - Files: `pyproject.toml`, `doc_web/__init__.py`, `doc_web/cli.py`, `doc_web/runtime_contract.py`
   - Changes: define package metadata, supported Python version, runtime version source, and a supported CLI entry point.
   - Done looks like: `pip install --target ... .` succeeds and the installed target can execute `doc-web contract --json`.
2. Add runtime preflight metadata and tests.
   - Files: `doc_web/runtime_contract.py`, `doc_web/cli.py`, `tests/test_doc_web_cli_contract.py`, `tests/test_doc_web_bundle_contract.py`
   - Changes: expose contract name/version, schema fingerprint or compatibility token, supported bundle schema versions, package version, and Python requirement in machine-readable form.
   - Done looks like: preflight JSON is stable, test-backed, and sufficient for a downstream pinned consumer to reject incompatible upgrades.
3. Close the live bundle-emission gap while preserving the transitional row manifest.
   - Files: `modules/build/build_chapter_html_v1/main.py`, `schemas.py`, `validate_artifact.py`, `tests/test_build_chapter_html.py`, `tests/test_doc_web_bundle_contract.py`
   - Changes: emit `manifest.json`, `provenance/blocks.jsonl`, and matching `blk-*` anchors from the real builder path; keep `chapter_html_manifest_v1` as a transitional build-local artifact rather than breaking existing local consumers silently.
   - Done looks like: a fresh bundle validates mechanically against `doc_web_bundle_manifest_v1` and `doc_web_provenance_block_v1`, and the HTML/provenance anchor mapping holds.
4. Add a committed fixture-backed `driver.py` validation lane.
   - Files: `configs/recipes/doc-web-fixture-bundle-smoke.yaml`, `tests/fixtures/doc_web_fixture_bundle/`, possibly `docs/RUNBOOK.md`
   - Changes: move the current ad hoc `/tmp` fixture pattern into repo-owned fixture inputs and a committed recipe so the active `doc-web` path has a reproducible real-run smoke lane.
   - Done looks like: `driver.py` can rebuild the active bundle seam from repo-owned fixtures without depending on ambient `output/runs/` history.
5. Update developer/operator docs and repo verification targets.
   - Files: `README.md`, `docs/RUNBOOK.md`, `docs/dossier-doc-web-handoff.md`, `docs/notes/standalone-dossier-intake-runtime-plan.md`, `docs/notes/doc-web-dossier-readiness-gap-analysis.md`, `Makefile`
   - Changes: publish the Storybook-style pinned consumption model in `doc-web` terms, separate remaining Dossier-only work from repo blockers, and ensure `make lint` covers the new runtime package.
   - Done looks like: Dossier can copy the consumption model directly from the docs, and local repo validation actually covers the new runtime code.

### Impact / Risk

- Files most likely to break:
  - `modules/build/build_chapter_html_v1/main.py` because it is still the single live emitter choke point
  - `tests/test_build_chapter_html.py` because current CLI integration assertions stop at HTML + row manifest
  - `Makefile` because current lint coverage excludes any new top-level runtime package
  - `docs/RUNBOOK.md` because current active validation guidance does not point to a committed self-contained smoke lane
- No new runtime dependency is planned. Recommended packaging path is standard `pyproject.toml` + setuptools build metadata only.
- No new ADR is recommended. The accepted boundary, release model, and contract ownership already exist in ADR-002.
- Relative effort: M

## Work Log

20260319-1648 — story created: user approved adopting the Storybook-style pinned dependency pattern for `doc-web`. Exploration confirmed the correct consumer model lives in Storybook (`dossier-runtime.json`, installer/check-upstream/bump scripts, pinned/default vs local override, preflight contract), while `doc-web` still lacks an installable package surface, runtime preflight CLI, and a proven live current-repo build that emits the published Dossier contract. Added `docs/notes/doc-web-dossier-readiness-gap-analysis.md` as the baseline blocker inventory. Next step: `/build-story` should make the accepted runtime boundary executable by adding package/CLI/preflight surfaces, proving a real bundle build, and then tightening the downstream handoff docs around the final pinned-consumer flow.
20260319-1718 — exploration and planning: traced `docs/ideal.md`, `docs/spec.md` (`spec:6`, `spec:7`), ADR-002, Stories 151-155, `docs/doc-web-bundle-contract.md`, `docs/dossier-doc-web-handoff.md`, `docs/notes/standalone-dossier-intake-runtime-plan.md`, `docs/notes/doc-web-dossier-readiness-gap-analysis.md`, the Storybook pinned-runtime surfaces, `modules/build/build_chapter_html_v1/main.py`, `modules/build/build_chapter_html_v1/module.yaml`, `validate_artifact.py`, `schemas.py`, `tests/test_doc_web_bundle_contract.py`, `tests/test_build_chapter_html.py`, `modules/common/load_artifact_v1/main.py`, current recipes, and the recent `output/runs/story155-docweb-fixture-build-r2` evidence. Result: this story closes a real Ideal/spec gap and does not reopen architecture, but the runtime boundary is still non-executable. Baseline evals: `python -m pytest tests/test_doc_web_bundle_contract.py -q` → `13 passed`; `python -m pip install --disable-pip-version-check --target <tmp>/site-packages .` → exit `1` because neither `setup.py` nor `pyproject.toml` exists; a fixture-backed `driver.py` run using the current builder produced only `4/6` expected bundle surfaces (`chapters_manifest_fixture.jsonl`, `index.html`, `page-001.html`, `page-002.html` present; `manifest.json` and `provenance/blocks.jsonl` missing). Files expected to change: package metadata + new `doc_web` package, `build_chapter_html_v1`, `schemas.py`, `validate_artifact.py`, contract/runtime tests, `README.md`, `docs/RUNBOOK.md`, handoff/migration/readiness docs, and `Makefile`. Files at risk: `build_chapter_html_v1` remains the emitter choke point; `tests/test_build_chapter_html.py` currently stops at HTML + row manifest; `Makefile` does not lint any future `doc_web/` package; the only recent real-run fixture recipe is trapped in ignored `output/runs/` snapshots and points at `/tmp`. ADRs consulted: ADR-002 only; no new ADR is needed unless implementation changes the settled release model. Patterns to follow: Storybook’s repo-owned pin + pinned/default-local override + preflight contract; keep the runtime surface narrow; preserve `chapter_html_manifest_v1` as transitional rather than silently breaking current builder-local consumers. Surprise: the contract docs and committed handoff pack are ahead of the live builder code in this repo, and there is still no committed self-contained smoke lane for the active `doc-web` path. Next: human approval on the plan, including the small scope expansion to add a repo-owned fixture-backed `driver.py` lane and extend `make lint` coverage to the new package.
20260319-2238 — implementation and verification: added `pyproject.toml`, the new `doc_web/` package (`__init__.py`, `__main__.py`, `cli.py`, `runtime_contract.py`), and `tests/test_doc_web_cli_contract.py` so the repo now installs cleanly and exposes `doc-web contract --json` with package version, Python requirement, supported bundle schema versions, and a schema fingerprint. Extended `modules/build/build_chapter_html_v1/main.py` so the live builder emits `manifest.json`, `provenance/blocks.jsonl`, and stable `blk-*` DOM ids while preserving `chapter_html_manifest_v1` as the transitional build-local artifact. Added the repo-owned smoke lane in `configs/recipes/doc-web-fixture-bundle-smoke.yaml` plus `tests/fixtures/doc_web_bundle_smoke/`, and updated `README.md`, `docs/RUNBOOK.md`, `docs/dossier-doc-web-handoff.md`, `docs/notes/standalone-dossier-intake-runtime-plan.md`, `docs/notes/doc-web-dossier-readiness-gap-analysis.md`, and `Makefile` so the pinned consumer pattern is documented against the real runtime surface. One follow-on fix surfaced during manual inspection: fallback pages were still being forced ahead of chapters in bundle reading order, so the builder now sorts emitted entries by source-page order so `manifest.json`, prev/next navigation, and `index.html` agree. Validation: `python -m pytest tests/test_doc_web_cli_contract.py -q` → `3 passed`; `python -m pytest tests/test_build_chapter_html.py::TestCLIIntegration::test_produces_valid_html5_output -q` → `1 passed`; `make lint` → clean; `make test` → `353 passed`; `python driver.py --recipe configs/recipes/doc-web-fixture-bundle-smoke.yaml --run-id story156-docweb-fixture-bundle-r1 --allow-run-id-reuse --force` → success; `python validate_artifact.py --schema doc_web_bundle_manifest_v1 --file output/runs/story156-docweb-fixture-bundle-r1/output/html/manifest.json` → `Validation OK`; `python validate_artifact.py --schema doc_web_provenance_block_v1 --file output/runs/story156-docweb-fixture-bundle-r1/output/html/provenance/blocks.jsonl` → `Validation OK`. Manual artifact inspection: `output/runs/story156-docweb-fixture-bundle-r1/output/html/manifest.json` contains `document_id: fixture-book`, reading order `chapter-001`, `page-001`, `asset_roots: ["images"]`, and relative `source_artifact: 01_load_artifact_v1/pages_html_fixture.jsonl`; `output/runs/story156-docweb-fixture-bundle-r1/output/html/provenance/blocks.jsonl` contains four rows with block ids `blk-chapter-001-0001`, `blk-chapter-001-0002`, `blk-page-001-0001`, and `blk-page-001-0002` mapped back to synthetic source element ids `p001-b1`, `p001-b2`, `p002-b1`, and `p002-b2`; `output/runs/story156-docweb-fixture-bundle-r1/output/html/chapter-001.html` contains `<h1 id="blk-chapter-001-0001">Fixture Chapter</h1>` and `<p id="blk-chapter-001-0002">Opening material for the repo-owned bundle smoke fixture.</p>`; `output/runs/story156-docweb-fixture-bundle-r1/output/html/page-001.html` contains `<p id="blk-page-001-0001">The fixture family</p>` plus `<figure id="blk-page-001-0002">` referencing `images/photo.jpg`; `output/runs/story156-docweb-fixture-bundle-r1/output/html/index.html` lists `Fixture Chapter` before `Page 2`, matching bundle reading order. Story is ready for `/validate` and `/mark-story-done`.
20260319-2347 — validation follow-up: tightened the package smoke after `/validate` found that the prior test inherited host site-packages and used `--no-deps`, which overstated the strength of the isolated-install proof. `tests/test_doc_web_cli_contract.py` now creates a clean venv (`system_site_packages=False`) and performs a normal `pip install .` so the installed `doc-web` console script has to resolve declared dependencies the same way Dossier would. Updated `docs/notes/doc-web-dossier-readiness-gap-analysis.md` to describe this as a clean-venv install smoke rather than a vague isolated-install claim. Revalidation: `python -m pytest tests/test_doc_web_cli_contract.py -q` → `3 passed`.
20260320-0019 — closeout and landing prep: updated `README.md` with an explicit Dossier-consumer handoff path so downstream users can start there, then follow `docs/dossier-doc-web-handoff.md` for the contract and `docs/RUNBOOK.md` for smoke commands. Added `.gitignore` coverage for generated packaging residue (`build/`, `*.egg-info/`) so the clean-venv package smoke no longer dirties the worktree during routine validation. Final validation: `make lint` → clean; `make test` → `353 passed`; `python driver.py --recipe configs/recipes/doc-web-fixture-bundle-smoke.yaml --run-id story156-docweb-fixture-bundle-r2 --allow-run-id-reuse --force` → success; `python validate_artifact.py --schema doc_web_bundle_manifest_v1 --file output/runs/story156-docweb-fixture-bundle-r2/output/html/manifest.json` → `Validation OK`; `python validate_artifact.py --schema doc_web_provenance_block_v1 --file output/runs/story156-docweb-fixture-bundle-r2/output/html/provenance/blocks.jsonl` → `Validation OK`. Manual inspection confirmed `output/runs/story156-docweb-fixture-bundle-r2/output/html/manifest.json` contains `document_id: fixture-book`, reading order `chapter-001`, `page-001`, and `asset_roots: ["images"]`; `output/runs/story156-docweb-fixture-bundle-r2/output/html/provenance/blocks.jsonl` contains four rows from `blk-chapter-001-0001` through `blk-page-001-0002`; `output/runs/story156-docweb-fixture-bundle-r2/output/html/index.html`, `chapter-001.html`, and `page-001.html` contain the expected `Fixture Chapter`, `Contents`, stable `blk-*` DOM ids, and `images/photo.jpg` reference. Story is ready to land.
