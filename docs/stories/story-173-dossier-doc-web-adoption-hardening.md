# Story 173 — Harden `doc-web` After the First Dossier Adoption Trial

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #3 (Extract), Requirement #6 (Validate), Requirement #7 (Export), Dossier-ready output, Transparency over magic, Graduate, don't accumulate
**Spec Refs**: spec:3 (spec:3.1, C3), spec:7, spec:8 (B3, B4)
**Build Map Refs**: Category 3 Layout & Structure Understanding (`exists`, C3 `climb`); Category 7 Graduation & Dossier Handoff (`partial`); Category 8 AI Harnesses & Tooling (`exists`, B3/B4 `hold`); Input Coverage row `born-digital-pdf` (`has fixture`)
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/RUNBOOK.md`, `docs/notes/doc-web-dossier-readiness-gap-analysis.md`, `docs/build-map.md`, `docs/stories/story-156-pinned-doc-web-runtime-adoption-and-dossier-readiness.md`, `docs/stories/story-168-marker-lite-maintained-born-digital-pdf-path.md`, `docs/stories/story-171-maintained-non-toc-born-digital-pdf-lane.md`, `None found after search in docs/decisions/ for packaging- or progress-specific ADRs`
**Depends On**: Story 156, Story 168, Story 171

## Goal

Close the first concrete gaps exposed when Dossier tried to consume `doc-web` as the maintained runtime boundary. The repo currently presents a pinned-consumer install loop that is not honest for `driver.py`, and the maintained non-TOC born-digital PDF lane is still hard to operate because its long-running Marker-lite stage is mostly silent and emits avoidable deprecation warnings from maintained code paths. This story should make the documented consumer install surface match reality, make the maintained non-TOC lane meaningfully observable, and remove the known warning noise without widening the runtime boundary or changing the accepted `doc-web` bundle contract.

## Acceptance Criteria

- [x] The supported Dossier-facing install story is singular and honest:
  - [x] `README.md`, `docs/RUNBOOK.md`, `docs/dossier-doc-web-handoff.md`, and `docs/notes/doc-web-dossier-readiness-gap-analysis.md` no longer imply that `python -m pip install .` is enough to run maintained `driver.py` smoke lanes unless that is freshly true
  - [x] if `driver.py` remains outside the base install, the docs and automated proof clearly split contract-only preflight from full runtime install
  - [x] the exact documented loop succeeds in a clean supported Python 3.12 environment, or the docs are explicitly split and test-backed
- [x] The repo keeps repeatable proof of the chosen install surface:
  - [x] automated clean-venv coverage exists for `doc-web contract --json`
  - [x] automated or scriptable smoke coverage exists for the documented `driver.py` adoption lane
  - [x] any remaining non-Python runtime dependencies for maintained smoke lanes are surfaced explicitly before import-time failure
- [x] The maintained non-TOC born-digital PDF lane is operationally observable:
  - [x] `pipeline_events.jsonl` or the equivalent progress surface emits substep events for container reuse/probe/bootstrap, `pdftotext`, docker copy in, Marker execution, docker copy out, and normalization/write
  - [x] a fresh flat-PDF proof run no longer spends most of the extract stage behind a single vague "Preparing repo-local Marker-lite runtime..." message
- [x] The maintained Dossier-facing runtime paths are free of the specific known deprecation warnings from the Dossier note:
  - [x] maintained `driver.py` paths stop using Pydantic v2 deprecated `__fields__` / `.dict()` APIs
  - [x] maintained reported paths stop using timezone-naive `datetime.utcnow()` helpers, including any additional helper modules exercised by the documented proof lanes
  - [x] if any warning is intentionally left outside the maintained surface, the story records it explicitly instead of leaving it in the success path silently
- [x] Fresh end-to-end evidence is recorded for both reported problem areas:
  - [x] `configs/recipes/doc-web-fixture-bundle-smoke.yaml` runs with inspected bundle/provenance artifacts under `output/runs/`
  - [x] `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml` runs with inspected `pages_html.jsonl`, `pipeline_events.jsonl`, `output/html/manifest.json`, and `output/html/provenance/blocks.jsonl`

## Out of Scope

- Dossier-side installer, pin manifest, or adapter changes in the Dossier repo
- Replacing the current Docker-backed Marker-lite runtime or solving its cold-start/runtime cost in this story
- Broad dependency-graph cleanup for legacy or unmaintained paths unrelated to the documented Dossier consumer surface
- Changing the frozen `doc-web` bundle / provenance contract unless the chosen install-surface fix requires a new explicit machine-readable manifest
- General born-digital PDF widening beyond the already maintained non-TOC proof lane

## Approach Evaluation

- **Simplification baseline**: start by reproducing the two reported failures exactly: a clean Python 3.12 venv running the documented pinned-consumer loop, and a fresh non-TOC born-digital rerun capturing `pipeline_events.jsonl` plus warning output. If the base package is intentionally only for `doc-web contract --json`, a docs-only split may be sufficient for Issue 1. If Dossier is meant to run maintained smoke lanes directly from the documented install, then the real choice is broader than package metadata alone: either expose a supported runtime extra or narrow the eager import surface so the documented smoke lane does not drag OCR dependencies it never uses. For Issue 2, the smallest plausible fix is thin progress hooks plus API swaps, not a runtime redesign.
- **AI-only**: low value. A model can draft doc wording or progress-message text, but it cannot prove package metadata, clean-venv behavior, or the absence of runtime warnings.
- **Hybrid**: likely strongest. Use deterministic clean-env repro plus real `driver.py` runs to choose the install surface, then land thin code changes for package metadata/docs, progress instrumentation, and deprecation cleanup.
- **Pure code**: possible, but risky if it over-corrects by shoving every driver dependency into the base package or by adding noisy logging everywhere. The story should not expand the install surface or runtime verbosity more than the evidence requires.
- **Repo constraints / prior decisions**: ADR-002 fixes the boundary at a versioned `doc-web` runtime consumed by Dossier. Story 156 intentionally introduced a minimal package surface and pinned-consumer docs. Stories 168 and 171 created the maintained Marker-lite and non-TOC born-digital lanes but left their runtime burden explicit. `docs/build-map.md` still marks Category 7 as `partial` and keeps `born-digital-pdf` at `has fixture`, so this story must harden the current maintained surface honestly rather than claim broader support.
- **Existing patterns to reuse**: `pyproject.toml`, `tests/test_doc_web_cli_contract.py`, `README.md`, `docs/RUNBOOK.md`, `docs/dossier-doc-web-handoff.md`, `driver.py`'s existing `ProgressLogger`, `modules/extract/extract_pdf_marker_lite_html_v1/main.py`, `modules/common/marker_lite_runtime.py`, and the fresh proof discipline already established in Stories 156, 168, and 171.
- **Eval**: the deciding proof is a clean-venv run of the documented consumer flow plus a fresh non-TOC born-digital rerun whose `pipeline_events.jsonl` shows meaningful substeps and whose stderr/run logs are free of the known deprecations. The approach fails if the documented install loop still needs undeclared Python dependencies, or if the long Marker-lite stage still looks hung from the operator surface.

## Tasks

- [x] Reproduce and freeze the Dossier-reported failures in this checkout:
  - [x] create a clean supported Python environment and run `python -m pip install .`, `doc-web contract --json`, and the documented `configs/recipes/doc-web-fixture-bundle-smoke.yaml` flow
  - [x] rerun the maintained non-TOC born-digital lane on `testdata/flat-born-digital-mini.pdf` while capturing `pipeline_events.jsonl` and warning output
  - [x] trace the exact import and warning sources in code before changing anything, so the fix is not guessed from one missing package at a time
  - [x] record the exact current failure/warning sources in the work log before changing code
- [x] Choose and land the honest pinned-consumer install surface:
  - [x] decide whether the right fix is docs-only split, package metadata movement, an explicit runtime extra such as `.[runtime]` / `.[driver]`, or narrowing eager OCR imports so the fixture smoke lane can run without the full OCR stack
  - [x] align `README.md`, `docs/RUNBOOK.md`, and `docs/dossier-doc-web-handoff.md` with the chosen surface
  - [x] update `docs/notes/doc-web-dossier-readiness-gap-analysis.md` so it no longer overstates repo-side readiness
  - [x] if `driver.py` remains outside base install, make the split explicit and test-backed instead of leaving the current README implication in place
- [x] Add repeatable validation for the documented consumer flow:
  - [x] extend or add clean-venv package smoke coverage for the documented `driver.py` lane
  - [x] ensure the maintained install proof checks both preflight and the published smoke path rather than only `doc-web contract --json`
  - [x] surface any remaining external system requirements up front if they cannot be represented in Python package metadata
- [x] Improve maintained non-TOC born-digital lane observability without changing its contract:
  - [x] thread `ProgressLogger` or equivalent progress hooks through `ensure_runtime_container()` and `run_lite_api()`
  - [x] emit operator-meaningful substep events for container reuse/probe/bootstrap, `pdftotext`, docker copy in, Marker execution, docker copy out, and normalization/write
  - [x] keep the event stream bounded and useful; do not replace one vague message with page-level noise
- [x] Remove known deprecations from the maintained reported paths:
  - [x] replace `__fields__` with `model_fields`
  - [x] replace `.dict()` with `model_dump()`
  - [x] replace timezone-naive `datetime.utcnow()` helpers with timezone-aware UTC helpers in maintained files touched by the reported flow
  - [x] include helper modules exercised by the documented proof lanes if they would still emit Python 3.12 warnings after the first swaps
- [x] If this story changes documented format coverage or graduation reality: update `docs/build-map.md` and record the before/after state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data for:
    - [x] `configs/recipes/doc-web-fixture-bundle-smoke.yaml`
    - [x] `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`
  - [x] If agent tooling changed: `make skills-check` (not expected; no agent tooling changes are planned)
- [x] If evals or goldens changed: run `/improve-eval` and update `docs/evals/registry.yaml` (not expected unless the implementation changes a scored truth surface)
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: install and observability hardening do not weaken bundle/provenance outputs
  - [x] T1 — AI-First: keep the fix at the packaging/instrumentation boundary; do not add AI to a plumbing problem
  - [x] T2 — Eval Before Build: reproduce the failures in a clean environment and fresh runs before choosing docs-only vs metadata changes
  - [x] T3 — Fidelity: preserve the existing maintained outputs while adding progress events and warning cleanup
  - [x] T4 — Modular: keep packaging/install concerns separate from optional or legacy stacks; keep progress hooks in shared runtime helpers rather than scattering them
  - [x] T5 — Inspect Artifacts: inspect real bundle/provenance artifacts and the event log surface, not just test output

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: this story lives at the Dossier-facing runtime boundary and the maintained born-digital extract seam. The likely owners are package metadata, docs, and possibly `modules/common/__init__.py` for Issue 1, plus `driver.py` instrumentation/stamping and the shared Marker-lite runtime helper for Issue 2.
- **Build-map reality**: Category 7 owns the Dossier adoption surface and remains `partial`, so fixing the documented install loop is directly in-bounds. Category 3 owns the maintained born-digital extraction seam and the `born-digital-pdf` coverage row remains only `has fixture`, so this story should harden the existing non-TOC lane rather than broaden the claim. Category 8 already has real orchestration/validation substrate, which makes progress logging and deprecation cleanup buildable rather than speculative.
- **Substrate evidence**: baseline clean Python 3.12 repro in this session showed `pip install .` and `doc-web contract --json` both succeed, then the documented smoke lane fails first on missing `yaml`, and after adding `PyYAML` fails next on missing `pdf2image` because `driver.py -> modules.common.utils -> modules.common.__init__ -> modules.common.ocr` eagerly imports the OCR stack even for the fixture smoke recipe. After implementation, `pyproject.toml` now declares an explicit `.[driver]` extra, `requirements.txt` explicitly pins `beautifulsoup4`, `modules/common/__init__.py` lazy-loads OCR exports so the fixture smoke lane no longer imports OCR deps it never uses, `tests/test_doc_web_cli_contract.py` proves both the contract CLI and the documented `driver.py` smoke in a clean venv, `driver.py` plus the maintained helper modules now use `model_fields` / `model_dump()` and timezone-aware UTC helpers, and `modules/extract/extract_pdf_marker_lite_html_v1/main.py` plus `modules/common/marker_lite_runtime.py` emit the requested Marker-lite substep progress.
- **Data contracts / schemas**: no `doc_web_bundle_manifest_v1` or `doc_web_provenance_block_v1` change is expected. If the chosen install fix introduces a new machine-readable runtime requirements manifest, define its shape explicitly. If any maintained output artifact gains new fields, add them to `schemas.py` before relying on them because `driver.py` stamping drops undeclared keys.
- **File sizes**: likely touch points range from small docs/package files to several very large runtime files. Current sizes: `pyproject.toml` 27, `requirements.txt` 9, `README.md` 165, `docs/RUNBOOK.md` 278, `docs/dossier-doc-web-handoff.md` 197, `docs/notes/doc-web-dossier-readiness-gap-analysis.md` 148, `tests/test_doc_web_cli_contract.py` 79, `modules/common/__init__.py` 29, `modules/common/utils.py` 241, `modules/common/load_artifact_v1/main.py` 124, `modules/extract/extract_pdf_marker_lite_html_v1/main.py` 168, `modules/portionize/portionize_headings_html_v1/main.py` 229, `docs/build-map.md` 581, `modules/common/run_registry.py` 586, `modules/common/marker_lite_runtime.py` 763, `modules/build/build_chapter_html_v1/main.py` 1686, `driver.py` 2216. Avoid broad edits in files already over 500 lines; prefer small helpers where possible.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md` (`spec:3`, `spec:7`, `spec:8`), `docs/build-map.md`, ADR-002, `docs/notes/doc-web-dossier-readiness-gap-analysis.md`, and Stories 156/168/171. No new ADR is recommended unless the fix turns into a new published runtime-manifest contract rather than a bounded package/docs/runtime-hardening change.

## Files to Modify

- `pyproject.toml` — align package metadata or add an explicit runtime extra if the chosen install surface needs it (27 lines)
- `requirements.txt` — reconcile or narrow the maintained runtime dependency story if the install surface changes (9 lines)
- `README.md` — fix the pinned-consumer install loop and adoption guidance (165 lines)
- `docs/RUNBOOK.md` — publish the precise supported smoke/install commands for maintained Dossier consumers (278 lines)
- `docs/dossier-doc-web-handoff.md` — keep downstream handoff expectations aligned with the chosen install surface (197 lines)
- `docs/notes/doc-web-dossier-readiness-gap-analysis.md` — remove the now-false claim that all repo-side blockers are already closed (148 lines)
- `tests/test_doc_web_cli_contract.py` or a new clean-venv smoke test — prove the documented preflight plus smoke flow (79 lines today)
- `modules/common/__init__.py` — optional narrow fix surface if the chosen install story avoids pulling OCR deps into the fixture smoke lane (29 lines)
- `driver.py` — remove deprecated Pydantic/UTC usage in maintained stamping/instrumentation paths (2216 lines)
- `modules/common/utils.py` — replace shared timezone-naive `_utc()` helper if the documented proof lanes still rely on it under Python 3.12 (241 lines)
- `modules/common/load_artifact_v1/main.py` — replace JSONL stamping `datetime.utcnow()` if the fixture smoke lane remains part of the documented consumer proof (124 lines)
- `modules/common/run_registry.py` — replace shared run-registry UTC helper if the documented proof lane still surfaces Python 3.12 warnings through run registration (586 lines)
- `modules/common/marker_lite_runtime.py` — emit substep progress around runtime bootstrap/copy/Marker execution (763 lines)
- `modules/extract/extract_pdf_marker_lite_html_v1/main.py` — wire progress reporting from the shared runtime helper into the extract stage (168 lines)
- `modules/portionize/portionize_headings_html_v1/main.py` — replace maintained-path `datetime.utcnow()` usage if still touched by the reported flow (229 lines)
- `modules/build/build_chapter_html_v1/main.py` — replace maintained-path `datetime.utcnow()` usage in the final bundle builder (1686 lines)
- `docs/build-map.md` — only if the story materially changes documented Dossier-handoff or born-digital operational reality (581 lines)

## Redundancy / Removal Targets

- README language that implies `python -m pip install .` is enough to run maintained `driver.py` smoke lanes when it is not
- Duplicate one-off UTC timestamp helpers if a shared timezone-aware helper can replace them cleanly
- The current single vague Marker-lite progress message if finer-grained substep events land successfully
- Divergent dependency declarations if the chosen install surface allows the maintained runtime dependency story to be stated in one place

## Notes

- This stays as one story because both reported issues block the same consumer journey: Dossier follows the supported `doc-web` path, then either fails before `driver.py` starts or cannot tell whether the maintained born-digital lane is healthy while it runs.
- A docs-only split is acceptable if the repo intentionally wants `python -m pip install .` to remain contract-only. The requirement is not "make the base package larger at any cost"; it is "make the documented consumer story match repo reality and prove it."
- The clean Python 3.12 repro in this session showed the install mismatch is not just one undeclared package: after adding `PyYAML`, the same documented smoke lane still fails because `modules/common/__init__.py` eagerly imports OCR helpers that the fixture smoke path does not actually need.
- Keep the accepted `doc-web` output contract stable unless the install-surface fix truly needs a new explicit manifest. Do not reopen ADR-002 or the broader release-model decision casually.

## Plan

### Exploration Summary

- **Ideal alignment:** proceed. This story closes a real gap in the accepted Dossier handoff model. A versioned runtime boundary only helps if consumers can install it honestly and operate the maintained proof lanes without guessing whether they are hung.
- **Relevant build-map state:** Category 7 remains `partial`, which makes the broken/ambiguous install surface an active handoff problem rather than a docs nit. Category 3 already has a maintained non-TOC born-digital lane, but the `born-digital-pdf` row still stays `has fixture` and carries explicit runtime burden. Category 8 already has mature orchestration substrate, so progress visibility and deprecation cleanup are real follow-up work, not new architecture.
- **Critical substrate verified in code:** `README.md`, `docs/RUNBOOK.md`, `docs/dossier-doc-web-handoff.md`, and `docs/notes/doc-web-dossier-readiness-gap-analysis.md` all currently describe or imply a smoother Dossier consumer story than the code supports; `tests/test_doc_web_cli_contract.py` proves the base package and `doc-web contract --json` work in isolation; `driver.py` imports `yaml` directly and then reaches `modules.common.__init__`, which eagerly imports OCR helpers from `modules/common/ocr.py`; `modules/extract/extract_pdf_marker_lite_html_v1/main.py` logs only one broad progress message; and `modules/common/marker_lite_runtime.py` already has distinct internal steps that can be surfaced.
- **Small scope deltas folded in:** update `docs/notes/doc-web-dossier-readiness-gap-analysis.md` because it currently claims the repo-side blockers are closed, and treat `modules/common/__init__.py` as an explicit candidate install-surface fix because the baseline repro showed eager OCR imports are part of the real problem.
- **Why one story instead of two:** the first Dossier consumer trial found both issues on one path. Fixing install honesty without runtime observability still leaves operators blocked on the maintained born-digital lane, and fixing progress/warnings without the install story still leaves Dossier blocked before the run starts.

### Eval-First Gate

- **Baseline first:**
  1. Clean Python 3.12 venv, documented install loop exactly as written.
     - `python -m pip install .` → success
     - `doc-web contract --json` → success
     - documented fixture smoke via `driver.py` → immediate import failure: `ModuleNotFoundError: No module named 'yaml'`
     - after adding `PyYAML` in the same venv, the next failure is `ModuleNotFoundError: No module named 'pdf2image'` from the eager `modules.common.__init__ -> modules.common.ocr` import chain
  2. Current development environment, repo-owned `doc-web` fixture smoke lane.
     - `python driver.py --recipe configs/recipes/doc-web-fixture-bundle-smoke.yaml --run-id story173-docweb-smoke-baseline --allow-run-id-reuse --force` → success
     - `validate_artifact.py` on `output/runs/story173-docweb-smoke-baseline/output/html/manifest.json` and `.../provenance/blocks.jsonl` → both `Validation OK`
     - manual artifact spot check confirms expected entries `chapter-001` then `page-001`, plus four provenance rows with stable `blk-*` anchors
  3. Current development environment, maintained non-TOC born-digital lane.
     - `python driver.py --recipe configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml --input-pdf testdata/flat-born-digital-mini.pdf --run-id story173-nontoc-baseline --allow-run-id-reuse --force` → success
     - `marker_lite_html` wall time: `145.76s`
     - `pipeline_events.jsonl` total events: `14`; `marker_lite_html` events: `4`
     - only one substantive in-flight Marker event appears between start and completion, with a `143.5s` silence gap
     - fresh stderr reproduces the `driver.py` Pydantic deprecation warnings for `__fields__` and `.dict()`
     - `validate_artifact.py` on `output/runs/story173-nontoc-baseline/output/html/manifest.json` and `.../provenance/blocks.jsonl` → both `Validation OK`
- **Decision rule:** choose the smallest change that makes the docs and proof honest. For Issue 1 there are three real candidates now, not two:
  - docs-only split if the base package is intentionally contract-only
  - runtime extra / broader package metadata if Dossier really should run maintained smoke lanes from the advertised install shape
  - narrowing eager imports so the documented fixture smoke lane does not need the OCR stack it never executes
  For Issue 2, prefer thin progress hooks and API swaps over changes to the extraction contract or lane selection.

### Implementation Outline

1. Decide the install contract from the real baseline (`S`).
   - Files: story docs first, then either `pyproject.toml` / `requirements.txt` or `modules/common/__init__.py`
   - Changes:
     - pick one supported story: contract-only base install, broader runtime install, or narrower eager imports for the fixture smoke lane
     - update the readiness-gap note so it no longer claims repo-side blockers are already closed
   - Done looks like: there is one supported consumer story, and all downstream-facing docs say the same thing.
2. Land repeatable proof for the chosen install surface (`S-M`).
   - Files: `tests/test_doc_web_cli_contract.py` or a new clean-venv smoke test, plus any doc updates
   - Changes:
     - extend clean-venv coverage beyond `doc-web contract --json`
     - prove either the documented smoke lane works from the chosen install shape or that the contract-only/runtime split is explicit and enforced
   - Done looks like: the clean-environment test fails if docs drift back to the current misleading story.
3. Land progress visibility in the maintained non-TOC lane (`S`).
   - Files: `modules/common/marker_lite_runtime.py`, `modules/extract/extract_pdf_marker_lite_html_v1/main.py`
   - Changes:
     - emit operator-meaningful substeps around container reuse/probe/bootstrap, `pdftotext`, docker copy in, Marker execution, docker copy out, and normalization/write
   - Done looks like: `pipeline_events.jsonl` no longer has a single 143.5-second blind gap inside `marker_lite_html`.
4. Remove maintained-path deprecation warnings (`S`).
   - Files: `driver.py` first, then any helper modules still exercised by the proof lanes under Python 3.12 (`modules/common/utils.py`, `modules/common/load_artifact_v1/main.py`, `modules/common/run_registry.py`, `modules/portionize/portionize_headings_html_v1/main.py`, `modules/build/build_chapter_html_v1/main.py`)
   - Changes:
     - swap `__fields__` -> `model_fields`
     - swap `.dict()` -> `model_dump()`
     - replace timezone-naive UTC helpers with timezone-aware UTC helpers where the proof lanes still hit them
   - Done looks like: fresh proof-lane runs are clean of the known warnings, or any deliberately deferred warning source is documented explicitly.
5. Re-run the two real proof lanes and inspect artifacts (`S`).
   - Files: no new code by default; verification only
   - Changes:
     - rerun the repo-owned `doc-web` fixture smoke
     - rerun the maintained non-TOC born-digital lane
     - validate `manifest.json` and `provenance/blocks.jsonl`
     - inspect representative rows plus the event log
   - Done looks like: the work log cites exact artifact/event paths and sample data from the current pass.

### Impact Analysis

- **Primary blast radius:** package metadata and handoff docs for Issue 1; `driver.py`, Marker-lite runtime helpers, and maintained extract paths for Issue 2.
- **Main risks:** over-expanding the base install surface, inflating already-large files (`driver.py`, `marker_lite_runtime.py`, `build_chapter_html_v1`), or conflating operator visibility with broader runtime redesign. The story should bias toward bounded deltas.
- **Structural health:** prefer a narrow import-surface fix in `modules/common/__init__.py` over dragging OCR deps into the base package unless the repo explicitly wants that heavier install. Prefer a small shared timezone-aware UTC helper or tiny local helper reuse over repeated ad hoc replacements. Prefer progress-hook plumbing in shared Marker-lite helpers rather than duplicating status messages at every call site.
- **Approval blocker:** none identified at story-creation time. The only possible split point is if the install-surface decision turns into a new published runtime-manifest contract; if that happens and it is larger than a small adjunct artifact, recommend a separate follow-up instead of silently widening this story.
- **Relative effort:** M

### What Done Looks Like

- A Dossier engineer can follow the documented `doc-web` install guidance and either run the maintained smoke lane successfully or see an explicit, documented contract-only/runtime split instead of an import surprise.
- A fresh maintained non-TOC born-digital run shows meaningful progress throughout the long Marker-lite stage and does not emit the known deprecation warnings from maintained repo paths.
- The story closes with fresh `driver.py` evidence and manual artifact inspection, not just updated docs and passing unit tests.

## Work Log

20260329-2213 — story created from Dossier adoption note: turned the reported install-surface mismatch and maintained non-TOC observability/warning gaps into one `Pending` story after verifying the current substrate in this checkout. Evidence: `README.md` still documents `python -m pip install .` followed by the `doc-web` smoke lane; `pyproject.toml` only declares `pydantic` while `requirements.txt` still holds `pdf2image`, `pytesseract`, `pyyaml`, and `unstructured[pdf]`; `driver.py` still contains `__fields__`, `.dict()`, and multiple `datetime.utcnow()` uses; `modules/extract/extract_pdf_marker_lite_html_v1/main.py` emits only one long-running progress message; and `modules/common/marker_lite_runtime.py` already contains the substeps Dossier asked to see surfaced. Next step: `/build-story` should reproduce both failures fresh, choose the honest install surface, and then land progress/deprecation cleanup with real `driver.py` proof on the maintained smoke and non-TOC born-digital lanes.
20260329-2240 — exploration and planning: verified the cited context (`docs/ideal.md`, `docs/spec.md` `spec:3/spec:7/spec:8`, `docs/build-map.md`, ADR-002, Stories 156/168/171, `docs/RUNBOOK.md`, and `docs/notes/doc-web-dossier-readiness-gap-analysis.md`) and traced the actual install/runtime seams in `README.md`, `docs/dossier-doc-web-handoff.md`, `pyproject.toml`, `requirements.txt`, `tests/test_doc_web_cli_contract.py`, `driver.py`, `modules/common/__init__.py`, `modules/common/ocr.py`, `modules/common/utils.py`, `modules/common/load_artifact_v1/main.py`, `modules/common/run_registry.py`, `modules/extract/extract_pdf_marker_lite_html_v1/main.py`, `modules/common/marker_lite_runtime.py`, and the maintained recipe/test surfaces. Ideal-alignment verdict: proceed; this closes a real Dossier handoff gap and does not move away from the Ideal. Critical substrate verdict: buildable with small coherent scope expansion, not blocked. Fresh baseline evidence:
- clean Python 3.12 venv using the documented loop: `python -m pip install .` and `doc-web contract --json` both succeeded, but the documented fixture smoke failed immediately on `ModuleNotFoundError: No module named 'yaml'`; after installing `PyYAML` in the same venv, the next failure was `ModuleNotFoundError: No module named 'pdf2image'` from `driver.py -> modules.common.utils -> modules.common.__init__ -> modules.common.ocr`, proving the install-surface gap is deeper than one missing dependency and making eager-import narrowing a real candidate alongside docs-only split or runtime extra.
- current dev-env bundle smoke: `python driver.py --recipe configs/recipes/doc-web-fixture-bundle-smoke.yaml --run-id story173-docweb-smoke-baseline --allow-run-id-reuse --force` succeeded; `python validate_artifact.py --schema doc_web_bundle_manifest_v1 --file output/runs/story173-docweb-smoke-baseline/output/html/manifest.json` and the matching provenance validation both returned `Validation OK`; manual inspection confirmed `chapter-001` then `page-001` reading order and four provenance rows anchored to `blk-*` ids.
- current dev-env maintained non-TOC baseline: `python driver.py --recipe configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml --input-pdf testdata/flat-born-digital-mini.pdf --run-id story173-nontoc-baseline --allow-run-id-reuse --force` succeeded; `marker_lite_html` took `145.76s`; `pipeline_events.jsonl` recorded only `4` `marker_lite_html` events with a `143.5s` gap between the one in-flight progress message and completion; fresh stderr reproduced the `driver.py` Pydantic deprecation warnings for `__fields__` and `.dict()`; and final manifest/provenance validation both returned `Validation OK`.
Files likely to change: `pyproject.toml`, `requirements.txt`, `README.md`, `docs/RUNBOOK.md`, `docs/dossier-doc-web-handoff.md`, `docs/notes/doc-web-dossier-readiness-gap-analysis.md`, `tests/test_doc_web_cli_contract.py` or a new clean-venv smoke test, `modules/common/__init__.py`, `driver.py`, `modules/common/utils.py`, `modules/common/load_artifact_v1/main.py`, `modules/common/run_registry.py`, `modules/common/marker_lite_runtime.py`, `modules/extract/extract_pdf_marker_lite_html_v1/main.py`, `modules/portionize/portionize_headings_html_v1/main.py`, and `modules/build/build_chapter_html_v1/main.py`. Files at risk: `driver.py`, `modules/common/marker_lite_runtime.py`, `modules/common/run_registry.py`, and `modules/build/build_chapter_html_v1/main.py` because they are already large cross-cutting surfaces. Patterns to follow: keep the runtime boundary narrow, prefer a minimal import-surface fix over stuffing unused OCR deps into the base package unless the repo explicitly wants a heavier install, reuse shared progress plumbing via `ProgressLogger`, and reuse the existing repo-owned smoke lanes plus schema validators rather than inventing new verification surfaces. Potential redundant docs/code to remove or collapse: the stale readiness-gap claim that repo-side blockers are closed, the README wording that implies the documented smoke lane works from the base install today, and the current single vague Marker-lite progress message. Surprise found: the repo-owned fixture smoke lane itself is healthy in the dev environment; the consumer failure is primarily packaging/import-surface drift, not a broken smoke recipe. Second surprise: the `datetime.utcnow()` deprecation was not freshly emitted by the full baseline run because the active dev environment used Python 3.11, but Python 3.12 deprecates it generically and the exact maintained-path call sites still exist in `driver.py`, `modules/common/utils.py`, `modules/common/load_artifact_v1/main.py`, `modules/common/run_registry.py`, `modules/portionize/portionize_headings_html_v1/main.py`, and `modules/build/build_chapter_html_v1/main.py`. Next step: human approval on the plan before any implementation code is written.
20260329-2315 — implementation started: moved the story to `In Progress` and committed to the narrow install-surface fix path. The chosen shape is `pip install .` for contract preflight only plus an explicit `.[driver]` extra for the repo-owned `driver.py` proof lanes, paired with a lazy OCR import in `modules/common/__init__.py` so the fixture smoke path no longer pulls `pdf2image`/`pytesseract` at import time when it never executes OCR. This keeps the pinned Dossier boundary small, makes the README/runbook split testable, and avoids hiding the broader OCR/runtime stack behind a misleading base install.
20260329-2358 — implementation and verification complete: landed the explicit `.[driver]` extra in `pyproject.toml`, pinned `beautifulsoup4` in `requirements.txt`, lazy-loaded OCR exports from `modules/common/__init__.py`, updated all downstream-facing docs to split contract-only preflight from repo-owned `driver.py` smoke lanes, and extended `tests/test_doc_web_cli_contract.py` with a clean-venv fixture-smoke proof. Landed maintained-path warning cleanup in `driver.py`, `schemas.py`, `modules/common/utils.py`, `modules/common/run_registry.py`, `modules/common/load_artifact_v1/main.py`, `modules/portionize/portionize_headings_html_v1/main.py`, and `modules/build/build_chapter_html_v1/main.py`, then threaded bounded substep progress through `modules/common/marker_lite_runtime.py` and `modules/extract/extract_pdf_marker_lite_html_v1/main.py`. Fresh evidence:
- `python -m pytest tests/test_doc_web_cli_contract.py -q` → `4 passed` including the new clean-venv `.[driver]` smoke proof.
- `python driver.py --recipe configs/recipes/doc-web-fixture-bundle-smoke.yaml --run-id story173-docweb-smoke-r2 --allow-run-id-reuse --force` → success; `validate_artifact.py` returned `Validation OK` for `output/runs/story173-docweb-smoke-r2/output/html/manifest.json` and `.../provenance/blocks.jsonl`; manual inspection confirmed entries `chapter-001` then `page-001` and provenance rows `blk-chapter-001-0001`/`blk-page-001-0002` with source ids `p001-b1` / `p002-b2`.
- `python driver.py --recipe configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml --input-pdf testdata/flat-born-digital-mini.pdf --run-id story173-nontoc-r2 --allow-run-id-reuse --force` → success; `pipeline_events.jsonl` now records `15` `marker_lite_html` events with substeps `container.inspect`, `container.probe`, `container.reuse`, `pdftotext`, `marker.temp_workspace`, `marker.copy_in`, `marker.execute`, `marker.copy_out`, `marker.cleanup`, `normalize`, and `write`; manifest/provenance validation both returned `Validation OK`; manual inspection confirmed `chapter-001` / `chapter-002` and provenance rows like `blk-chapter-001-0001` → `p001-b1`.
- clean Python 3.12 verification: created `/tmp/story173-py312-1b6Olu/venv`, installed `.[driver]`, and re-ran both the fixture smoke and the maintained non-TOC lane with `-W default`; after fixing the additional maintained-path `schemas.py` class-config warnings, both runs completed without deprecation output.
- repo gates: `make test` → `393 passed` with unrelated residual warnings in `modules/portionize/portionize_headers_numeric_v1/main.py` (`.dict()` usage outside this story’s maintained Dossier-facing path); `make lint` → passed. No `docs/build-map.md` or eval-registry change was needed because this story hardened the existing documented surfaces rather than changing coverage or scored truth.
20260330-0018 — story closed via `/mark-story-done`: refreshed close-out validation on the final diff, reran `make test` and `make lint`, revalidated the checked-in proof artifacts under `output/runs/story173-docweb-smoke-r2/` and `output/runs/story173-nontoc-r2/`, and reran both documented proof lanes in the Python 3.12 clean venv without deprecation output. Status is now `Done`, workflow gates are complete, and the story/index truth surfaces match the shipped slice. Next step: `/check-in-diff`.
20260331-1035 — post-close install hardening follow-up: the axios npm compromise made the remaining package-resolution risk concrete, so I audited whether repo-local release-age gating would actually protect this checkout. Verdict: yes for newly published Python packages, but only if the gate is enforced on the install path we document today. Landed `doc_web/install_with_age_gate.py` plus `scripts/install_with_age_gate.py`, which apply a 7-day cutoff via `uv pip install --exclude-newer ...` or `pip install --uploaded-prior-to ...` when available, and added `[tool.uv] exclude-newer = "7 days"` in `pyproject.toml` for repo-local `uv` project workflows. Updated `README.md`, `docs/RUNBOOK.md`, `benchmarks/README.md`, and `AGENTS.md` so the hardened Python path is explicit and the npm/promptfoo story no longer overclaims protection that a repo-local file cannot enforce for global installs. Fresh verification: `python -m pytest tests/test_install_with_age_gate.py -q` passes, and `python scripts/install_with_age_gate.py --dry-run .` plus `python scripts/install_with_age_gate.py --dry-run -r requirements.txt` emit the expected age-gated installer commands from this checkout. Impact: this adds a real cooldown control for the repo's Python dependency updates while keeping the existing `pip`-shaped workflows usable; it does not solve long-lived malicious releases or global npm installs by itself.
