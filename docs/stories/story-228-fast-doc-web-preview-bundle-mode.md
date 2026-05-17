---
title: "Fast `doc-web` Preview Bundle Mode for Dossier and Storybook"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #1 (Detect), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Traceability is the Product, Dossier-ready output"
spec_refs:
  - "spec:1"
  - "spec:3"
  - "spec:6"
  - "spec:7"
adr_refs:
  - "ADR-002"
depends_on:
  - "152"
  - "154"
  - "156"
category_refs:
  - "spec:1"
  - "spec:3"
  - "spec:6"
  - "spec:7"
compromise_refs: []
input_coverage_refs:
  - "born-digital-pdf"
  - "scanned-pdf-prose"
  - "docx"
  - "xlsx"
  - "pptx"
architecture_domains:
  - "doc_web_runtime"
roadmap_tags:
  - "dossier-preview"
  - "storybook-preview"
  - "preview-bundle"
legacy_system: ""
---

# Story 228 — Fast `doc-web` Preview Bundle Mode for Dossier and Storybook

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #1 (Detect), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Traceability is the Product, Dossier-ready output
**Spec Refs**: spec:1 (Input Detection & Routing), spec:3 (Extraction & OCR), spec:6 (Validation, Provenance & Export), spec:7 (Graduation & Dossier Handoff)
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/doc-web-bundle-contract.md`, `docs/dossier-doc-web-handoff.md`, `docs/notes/standalone-dossier-intake-runtime-plan.md`, `/Users/cam/.codex/worktrees/759a/dossier/docs/stories/artifacts/story-143-doc-web-preview-requirements.md`
**Depends On**: Story 152, Story 154, Story 156

## Goal

Add a latency-bound preview preparation mode to `doc-web` that accepts raw documents and emits a normal-looking, explicitly non-final `doc-web` bundle that Dossier and Storybook can consume immediately. The preview bundle must keep the existing contract shape (`manifest.json`, `index.html`, semantic HTML entries, assets when useful, and `provenance/blocks.jsonl`) while adding preview-specific status, structural facts, cache identity, and preview-to-full selector continuity so Dossier never has to parse PDFs, Office files, images, or OCR output itself.

## Eval Ladder Context

- **Root surface**: the existing `doc-web` runtime contract and bundle smoke path from Story 156: `doc-web contract --json`, `doc_web_bundle_manifest_v1`, `doc_web_provenance_block_v1`, and fixture-backed `driver.py` bundle validation.
- **Parent gap**: current maintained lanes produce final-ish bundles after recipe execution, but there is no preview contract, no latency-bound preparation command, no preview coverage status, no cache identity, and no machine-readable mapping from sampled preview selectors to full-run selectors.
- **Measured child surface needed**: add a preview smoke harness that times first status, usable preview output, and hard timeout behavior on representative fixtures. This is not primarily an LLM-quality eval; the first failure to classify is contract/orchestration wrong versus parser/OCR substrate wrong.
- **Rerun trigger**: rerun the parent bundle smokes when preview shares bundle-building helpers, schema models, or cache artifacts with full processing.

## Acceptance Criteria

- [x] `doc-web` exposes a supported preview entry surface, preferably `doc-web preview`, that accepts raw maintained-format inputs and writes a preview bundle rooted like a normal bundle:
  - `manifest.json`
  - `index.html`
  - one or more semantic HTML entry files
  - `assets/` or existing bundle-local asset roots when useful and cheap
  - `provenance/blocks.jsonl`
- [x] The preview contract is an explicit extension of the existing bundle model, not a JSON-only side channel. The manifest or companion review metadata records preview mode, preview contract fingerprint, coverage state (`complete`, `sampled`, `partial`, or `deferred`), included/skipped pages or records, warnings, unsupported inferences, and structural facts.
- [x] Preview metadata returns a high-level, explicitly non-final content hint when enough text can be sampled, including a title guess, document-kind hint, summary, evidence snippets, quality/status, and warnings when the basis is sparse or noisy.
- [x] Preview provenance preserves stable `entry_id`, `block_id`, `block_kind`, source page or record identity when available, source element ids, text quote, confidence/OCR metadata when available, and page/record lineage that can be cited or mapped later.
- [x] The preview path emits honest status/progress stages Dossier and Storybook can show: `accepted`, `preparing_pages`, `detecting_text_or_ocr_need`, `reading_sample`, `building_preview_html`, `preview_ready`, `continuing_full_processing`, `ready`, and `failed`.
- [x] Latency behavior is measured and guarded on checked-in fixtures:
  - first status within 500 ms p95
  - usable preview bundle or honest partial/deferred response within 3 s p95 when a fast text layer or bounded sample is available
  - hard synchronous timeout at 8 s
- [x] Scan-heavy or OCR-blocked inputs either run a bounded fast OCR sample or return structural facts and warnings instead of fake completeness when useful preview text cannot be produced inside the budget.
- [x] Cache identity is explicit and test-backed: source identity/hash, `doc-web` version/ref, parser/OCR/rendering settings, preview contract fingerprint, and runtime options that affect output.
- [x] A later full run can reuse compatible preview work such as rendered pages, OCR output, parsed text, and asset caches. When preview blocks are regenerated, the full output either preserves identical `entry_id`/`block_id` values or emits a machine-readable preview-to-full selector mapping.
- [x] Acceptance fixtures cover:
  - born-digital PDF with immediate text-layer preview
  - scan/image-heavy PDF with structural facts plus honest partial or deferred text
  - image directory with structural facts plus bounded OCR sample or honest deferred text
  - pageless DOCX preview bundle
  - one larger multi-section fixture proving preview/full cache reuse and selector mapping

## Out of Scope

- Dossier-side or Storybook-side UI implementation
- Dossier parsing raw documents, running OCR, or inferring page counts from media files
- Treating preview summaries as extracted graph facts
- Full OCR quality improvement beyond what is needed to return honest preview status
- GEDCOM, spreadsheet, and presentation preview completeness beyond contract hooks and any cheap reuse of existing maintained adapters
- A long-running service or websocket API unless implementation proves the existing pinned runtime/CLI model cannot satisfy the consumer contract

## Approach Evaluation

- **Simplification baseline**: First prove what a thin preview wrapper around existing maintained lanes can do without adding new AI calls: format sniffing, structural facts, fast PDF text-layer sampling, DOCX/Office element sampling, existing bundle writer reuse, and immediate status metadata. If this can satisfy the fixture set and latency budget, do not add a new AI summarization path.
- **AI-only**: A single LLM call cannot safely own raw document parsing, cache identity, timing, provenance, or selector mapping. AI can optionally help choose useful sample pages or summarize preview text later, but it cannot replace the bundle/provenance contract.
- **Hybrid**: Use deterministic parser and cache plumbing for status, facts, and selector identity; use AI only if evidence shows semantic sampling needs a ranking pass that deterministic headings/TOC/front-matter signals cannot provide.
- **Pure code**: Plausible for the first slice because the requirement is mostly orchestration, contract metadata, and reuse of existing extract/bundle surfaces. This should remain the default unless preview sample quality is materially poor.
- **Repo constraints / prior decisions**: ADR-002 requires a standalone `doc-web` runtime and structural website bundle with provenance sidecars. Story 152 froze the bundle/provenance contract. Story 154 froze Dossier's consumer boundary. Story 156 made the installable runtime/CLI/preflight path real. The Dossier handoff explicitly says Dossier consumes `doc-web` semantic HTML and provenance, not raw files.
- **Existing patterns to reuse**: `doc_web/cli.py`, `doc_web/runtime_contract.py`, `modules/common/office_native_bundle.py`, `modules/common/marker_page_html.py`, `validate_artifact.py`, `tests/test_doc_web_cli_contract.py`, `configs/recipes/doc-web-fixture-bundle-smoke.yaml`, and maintained direct-entry recipes for PDF, DOCX, XLSX, PPTX, EPUB, EML, MBOX, and web pages.
- **Eval**: A new preview smoke/benchmark should distinguish the approaches by checking bundle validity, provenance completeness, status honesty, selector mapping, cache reuse, and timing on the representative fixture set.

## Tasks

- [x] Baseline the current runtime behavior against the Dossier requirement:
  - confirm no existing preview command or preview contract exists
  - record which existing maintained lanes can produce cheap structural facts or sampled semantic HTML without full OCR
  - measure current startup/first-output overhead on the candidate fixtures
- [x] Define the preview contract extension:
  - preview status and stage vocabulary
  - coverage state and included/skipped page or record inventory
  - structural facts/review metadata fields
  - cache identity/fingerprint fields
  - preview-to-full selector mapping artifact shape
  - compatibility/fingerprint exposure through `doc-web contract --json`
- [x] Implement the preview entry surface and dispatcher:
  - add `doc-web preview` or equivalent supported Python API
  - accept raw PDF, image-backed PDF, and DOCX in the first complete slice
  - add hooks for later spreadsheet, presentation, GEDCOM, EPUB, email, and archive adapters without claiming unsupported completeness
  - return early status/deferred metadata when full preview is not possible inside budget
- [x] Reuse existing bundle/provenance builders rather than creating a parallel preview format.
- [x] Add cache identity and reuse mechanics so a compatible full run can consume preview-rendered pages, parsed elements, OCR snippets, or asset caches.
- [x] Add high-level content hints for preview consumers without treating the hint as extracted graph truth.
- [x] Add bounded OCR sampling for image directories so scanned/no-text inputs can produce useful preview text when a cheap sample succeeds.
- [x] Add preview/full selector continuity:
  - preserve `entry_id`/`block_id` where content is identical
  - emit a preview-to-full mapping artifact when full processing regenerates sampled blocks
- [x] Add the required checked-in fixture set and preview smoke tests:
  - born-digital PDF immediate text-layer preview
  - scan-heavy PDF partial/deferred preview
  - DOCX pageless preview
  - larger multi-section preview/full reuse and selector mapping case
- [x] Add CLI, schema, and runtime-contract regression coverage for preview output and timing guards.
- [x] Update Dossier-facing docs and runbooks so downstream consumers know exactly which preview artifacts are safe to consume and which are non-final.
- [x] If this story changes documented format coverage or graduation reality: update `tests/fixtures/formats/_coverage-matrix.json` and any relevant methodology state honestly. No coverage-matrix change was needed because preview does not change final maintained format graduation truth.
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up.
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py` or the supported preview/full smoke path, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL/HTML data
  - [x] If agent tooling changed: `make skills-check`. Agent tooling did not change; not required.
- [x] If evals or goldens changed: run `/improve-eval` and update `docs/evals/registry.yaml`. No eval/golden files changed; not required.
- [x] Search all docs and update any related to what we touched.
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: preview and full output trace every block to source page/record, source element, confidence/OCR metadata when available, and processing/cache identity
  - [x] T1 — AI-First: use AI only where measured sample selection or extraction quality needs it; keep parsing, cache, and provenance as code-owned contract work
  - [x] T2 — Eval Before Build: baseline existing parser/LLM-free preview behavior before adding complex sampling or AI ranking
  - [x] T3 — Fidelity: preview output is explicitly non-final and never hides skipped, deferred, or OCR-blocked content
  - [x] T4 — Modular: preview mode extends maintained recipes/adapters through explicit knobs and artifacts, not document-specific branches
  - [x] T5 — Inspect Artifacts: manually inspect preview bundles, provenance rows, metadata, cache identity, and selector mapping artifacts

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

- **Owning module / area**: `doc_web` runtime CLI/API plus shared bundle/provenance helpers. This is a cross-format runtime seam, not a Dossier parser and not a one-format extraction story.
- **Methodology reality**: `docs/methodology/state.yaml` lists `spec:7` substrate as partial and the `doc_web_runtime` audit lane as currently honest after recent XLSX, born-digital PDF, PPTX, EPUB, EML, and MBOX proof. This story is the new trigger that makes another runtime story honest: a downstream Dossier requirement introduced a new latency/reuse contract that the current final-bundle lanes do not cover.
- **Substrate evidence**: Existing substrate includes `doc-web contract --json`, `doc_web_bundle_manifest_v1`, `doc_web_provenance_block_v1`, maintained bundle smokes in `tests/test_doc_web_cli_contract.py`, and maintained direct-entry coverage rows for born-digital PDF, scanned PDF, DOCX, XLSX, and PPTX. Missing substrate is the preview command, preview contract metadata, timing harness, cache reuse contract, and preview-to-full selector mapping.
- **Data contracts / schemas**: `doc_web_bundle_manifest_v1` and `doc_web_provenance_block_v1` remain canonical. Preview-specific fields that cross the consumer boundary need explicit schema coverage in `schemas.py` or a new preview metadata schema before code emits them.
- **File sizes**: `doc_web/cli.py` is 36 lines, `doc_web/runtime_contract.py` is 61 lines, `modules/common/office_native_bundle.py` is 375 lines, `tests/test_doc_web_cli_contract.py` is 674 lines, `schemas.py` is 1379 lines, `docs/RUNBOOK.md` is 1139 lines, `docs/doc-web-bundle-contract.md` is 234 lines, `docs/dossier-doc-web-handoff.md` is 212 lines, `tests/fixtures/formats/_coverage-matrix.json` is 595 lines, and `pyproject.toml` is 51 lines. Keep new preview orchestration in new focused modules rather than growing the largest shared files unnecessarily.
- **Decision context**: Reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/doc-web-bundle-contract.md`, `docs/dossier-doc-web-handoff.md`, ADR-002, the standalone Dossier intake runtime plan, recent runtime stories, the coverage matrix, and the upstream Dossier Story 143 requirement. No new ADR is required if preview remains an explicit extension of ADR-002's bundle/provenance boundary. Create or update an ADR only if implementation changes the accepted runtime ownership, release model, or consumer boundary.

## Files to Modify

- `/Users/cam/.codex/worktrees/4623/doc-web/doc_web/cli.py` — add the supported preview command surface (36 lines)
- `/Users/cam/.codex/worktrees/4623/doc-web/doc_web/runtime_contract.py` — expose preview contract/fingerprint support if it becomes a consumer gate (61 lines)
- `/Users/cam/.codex/worktrees/4623/doc-web/doc_web/preview.py` — implement preview orchestration and status output (new file)
- `/Users/cam/.codex/worktrees/4623/doc-web/schemas.py` — add preview metadata/cache/mapping schemas if they cross artifact boundaries (1379 lines)
- `/Users/cam/.codex/worktrees/4623/doc-web/modules/common/office_native_bundle.py` — reuse or extend bundle/provenance writing for pageless DOCX and future Office previews without forking the bundle format (375 lines)
- `/Users/cam/.codex/worktrees/4623/doc-web/modules/common/marker_page_html.py` — reuse or extend born-digital PDF bundle/provenance helpers if the first PDF preview slice uses Marker-lite output (780 lines)
- `/Users/cam/.codex/worktrees/4623/doc-web/configs/recipes/` — add or update preview/full reuse smoke recipes if `driver.py` integration is needed
- `/Users/cam/.codex/worktrees/4623/doc-web/tests/fixtures/` — add representative preview fixtures and expected metadata/mapping checks
- `/Users/cam/.codex/worktrees/4623/doc-web/tests/test_doc_web_cli_contract.py` — add CLI/runtime preview regression coverage (674 lines)
- `/Users/cam/.codex/worktrees/4623/doc-web/tests/test_doc_web_preview.py` — add focused preview contract, timing, cache, and selector-mapping tests (new file)
- `/Users/cam/.codex/worktrees/4623/doc-web/docs/doc-web-bundle-contract.md` — document the preview-mode extension if it changes the consumer-facing contract (234 lines)
- `/Users/cam/.codex/worktrees/4623/doc-web/docs/dossier-doc-web-handoff.md` — document the preview consumption boundary and Dossier non-responsibilities (212 lines)
- `/Users/cam/.codex/worktrees/4623/doc-web/docs/RUNBOOK.md` — add operator commands for preview smoke, full reuse validation, and artifact inspection (1139 lines)
- `/Users/cam/.codex/worktrees/4623/doc-web/tests/fixtures/formats/_coverage-matrix.json` — update only if the implemented preview slice changes documented format or graduation truth (595 lines)

## Redundancy / Removal Targets

- Any future Dossier-side raw-document parsing shim made unnecessary by the preview bundle contract
- Any ad hoc preview JSON output that duplicates bundle manifest/provenance fields without validating as a bundle extension
- Any local cache metadata that is not part of the explicit source/settings/fingerprint identity contract
- Any Storybook or Dossier wording that implies preview text is final extracted knowledge rather than a non-final `doc-web` artifact

## Notes

- The upstream Dossier requirement is preserved at `/Users/cam/.codex/worktrees/759a/dossier/docs/stories/artifacts/story-143-doc-web-preview-requirements.md`.
- This is a new story rather than a reopen of Story 154 or Story 156 because it adds a different runtime seam and success surface: latency-bound preview, progress states, cache reuse, and selector continuity. The older stories covered final bundle contract, handoff, and installable runtime preflight.
- The first implementation should bias toward honest partial/deferred preview over broad but fake completeness. A scan-heavy PDF with structural facts and warnings is a successful preview if it does not pretend OCR succeeded.
- Dossier consumption stays thin: it consumes semantic HTML plus provenance and can summarize preview text, but it does not parse raw PDFs/Office files or claim OCR quality beyond `doc-web` metadata.

## Plan

### Current Baseline / Eval

- `python -m doc_web contract --json` succeeds and emits the current runtime contract in about `0.93s` wall time on this checkout. Existing focused contract test also passes: `python -m pytest tests/test_doc_web_cli_contract.py::test_doc_web_module_cli_emits_machine_readable_contract_json -q` => `1 passed`.
- `python -m doc_web preview --help` fails in about `0.88s` with argparse rejecting `preview` because the CLI currently supports only `{contract}`. Baseline preview entry surface: `0/1`.
- `rg` found no preview-mode runtime contract, no preview/full selector mapping artifact, and no cache-identity contract outside generic artifact/run references.
- Cheap deterministic PDF sampling is viable for the first preview slice. `pypdf` sampled the first two pages of repo fixtures in milliseconds:
  - `testdata/flat-born-digital-mini.pdf`: `2` pages, `4160` sample chars, `0.0044s`
  - `testdata/tbotb-mini.pdf`: `3` pages, `3733` sample chars, `0.0035s`
  - `testdata/scanned-prose-mini.pdf`: `4` pages, `0` sample chars, `0.0017s`
  - `testdata/scanned-prose-degraded.pdf`: `4` pages, `0` sample chars, `0.0012s`
- Existing DOCX Unstructured partitioning is not a reliable preview-latency substrate cold. `partition_docx_with_unstructured(...)` took `26.3392s` on the first `docx-mini` call, then `0.0219s` after warm import/runtime state. `python-docx` is already importable in this environment and sampled the same checked-in DOCX fixtures in `0.0071-0.0137s`, so the first preview slice should use a light deterministic DOCX sampler and leave full Unstructured output to the full processing lane.
- This is pure orchestration/contract work first. No single LLM-call baseline is needed before implementation because raw parsing, timing, cache identity, status events, and selector mapping are not reasoning tasks. AI should stay out unless deterministic sample ranking fails on fixture proof.

### Scope Adjustment

- Fold in a small dependency/packaging delta: the supported preview command needs light raw-input readers in the installed runtime surface. The proposed implementation adds `pypdf` and `python-docx` as runtime dependencies, or an explicit `preview` extra if base install size becomes a concern. The recommended default is base runtime dependencies because Dossier/Storybook need preview without a separate optional install path.
- Keep spreadsheets/presentations/GEDCOM as contract hooks unless the first implementation can reuse existing light libraries cheaply without destabilizing the story. The first complete acceptance slice should be PDF + DOCX plus explicit unsupported/deferred behavior for the later adapters.

### Implementation Order

1. Define preview contract schemas and runtime metadata.
   - Files: `schemas.py`, `validate_artifact.py`, `doc_web/runtime_contract.py`, `docs/doc-web-bundle-contract.md`, `docs/dossier-doc-web-handoff.md`.
   - Changes: add `doc_web_preview_metadata_v1` and `doc_web_preview_selector_map_v1` or equivalent; expose preview contract fingerprint/support through `doc-web contract --json`; document coverage state, status vocabulary, cache identity, structural facts, and non-final semantics.
   - Done looks like: metadata and selector-map artifacts validate mechanically, and Dossier can tell preview support from the contract payload.
2. Add focused preview runtime modules.
   - Files: new `doc_web/preview.py`, `doc_web/cli.py`, maybe `doc_web/preview_pdf.py` / `doc_web/preview_docx.py` if splitting keeps files small.
   - Changes: implement `doc-web preview --input <path> --out-dir <dir>`, status events, timeout checks, source hashing, settings fingerprints, bundle writing, and honest deferred/partial handling.
   - Done looks like: born-digital PDF and DOCX produce valid non-final preview bundles; scanned PDF produces a valid deferred/partial bundle with page count/text-layer facts and warnings instead of fake OCR text.
3. Reuse the existing bundle/provenance contract instead of creating a parallel preview format.
   - Files: likely a new helper in `doc_web/preview.py` or a small shared helper, with minimal reuse from `modules/common/office_native_bundle.py`.
   - Changes: write `manifest.json`, `index.html`, entry HTML, and `provenance/blocks.jsonl` with stable `entry_id` / `block_id`. For deferred scanned PDFs, keep the bundle inspectable but mark text coverage as deferred and avoid provenance rows for invented text.
   - Done looks like: `validate_artifact.py --schema doc_web_bundle_manifest_v1` and `--schema doc_web_provenance_block_v1` pass on preview outputs.
4. Add cache identity and selector continuity proof.
   - Files: `doc_web/preview.py`, new tests, possibly a small mapping helper.
   - Changes: emit source hash, runtime version, parser settings, preview fingerprint, included/skipped inventory, and a preview-to-full mapping artifact or preserved-ID proof for the larger multi-section fixture.
   - Done looks like: a test demonstrates either identical preview/full block IDs for unchanged content or a validated mapping row from preview selector to full selector.
5. Add tests, fixtures, and docs.
   - Files: `tests/test_doc_web_preview.py`, `tests/test_doc_web_cli_contract.py`, `tests/fixtures/preview/` if needed, `docs/RUNBOOK.md`, `docs/dossier-doc-web-handoff.md`, `docs/doc-web-bundle-contract.md`, and this story.
   - Changes: cover CLI rejection baseline -> support, born-digital PDF immediate text preview, scanned PDF deferred preview, DOCX preview, timing guards, schema validation, and docs.
   - Done looks like: targeted preview tests pass, docs name exact commands/artifacts, and work log records manual inspection of preview `manifest.json`, `preview_metadata.json`, `provenance/blocks.jsonl`, representative HTML, and selector mapping.

### Impact / Risk

- Story-scope impact: closes the Dossier Story 143 upstream requirement by making preview a first-class `doc-web` runtime mode rather than a downstream Dossier workaround.
- Pipeline-scope impact: the full bundle lanes remain canonical; preview adds an early non-final artifact with explicit cache identity and reuse/mapping hooks.
- User-facing impact: Storybook/Dossier can show a real document preview quickly for text-layer PDFs and DOCX, and can show honest "OCR needed / deferred" status for scan-heavy PDFs instead of blocking or pretending text exists.
- Main risk: base runtime dependencies grow from contract-only (`pydantic`) to include raw-input preview readers. This is small and justified if preview is a supported Dossier/Storybook surface, but it is the one approval-sensitive packaging change.
- Secondary risk: selector continuity against the existing full lanes may require a mapping artifact rather than preserving IDs, especially where full processing uses Marker or Unstructured source element IDs that differ from lightweight preview samplers.

### Approval Gate

- Implementation should proceed only after approval for the packaging delta (`pypdf` + `python-docx` in base runtime, or a `preview` extra if preferred).
- Recommended approach: add them to the base runtime and keep preview deterministic for the first slice.

## Work Log

20260504-1641 — story created from upstream Dossier Story 143 requirement: read the Dossier preview requirements, current `doc-web` contract/handoff docs, ADR-002, methodology state/graph, coverage rows, recent runtime stories, CLI/runtime substrate, and bundle tests. Decision: new Story 228 is warranted because the requirement adds latency-bound preview, progress stages, cache identity/reuse, and preview/full selector continuity on top of the existing final bundle contract. Status set to `Pending` because the final bundle/runtime substrate exists and the missing preview seam is buildable, not blocked. Next: run `/build-story` when ready.
20260504-1648 — `/build-story` exploration and baseline: read the build-story skill, Story 228, `docs/ideal.md`, `docs/spec.md` (`spec:1`, `spec:3`, `spec:6`, `spec:7`), `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, ADR-003 background, `docs/doc-web-bundle-contract.md`, `docs/dossier-doc-web-handoff.md`, the standalone runtime plan, Dossier readiness gap analysis, coverage rows for born-digital PDF / scanned PDF / DOCX / XLSX / PPTX, current CLI/runtime files, schema/validator wiring, Office and Marker bundle helpers, and maintained recipe/test surfaces. Baselines: `python -m doc_web contract --json` succeeds (`runtime_version=0.1.0`, `schema_fingerprint=sha256:e2fd...`, about `0.93s`); `python -m doc_web preview --help` fails because only `contract` exists; focused contract CLI pytest passed (`1 passed`). Cheap sampler evidence: `pypdf` distinguishes born-digital PDFs with text (`4160` / `3733` chars in `0.0044s` / `0.0035s`) from scanned PDFs with no text (`0` chars in about `0.001s`), while `python-docx` samples repo DOCX fixtures in `0.007-0.014s`; Unstructured DOCX cold start took `26.3392s`, so it is not the right preview substrate for the latency budget. Critical substrate verified: final bundle schemas, contract preflight, maintained full lanes, and test fixtures exist. Missing substrate: preview command, preview schemas, status/timing contract, cache identity, and preview/full selector mapping. Files likely to change: `pyproject.toml`, `doc_web/cli.py`, new `doc_web/preview.py`, `doc_web/runtime_contract.py`, `schemas.py`, `validate_artifact.py`, preview tests, bundle/handoff docs, runbook, and possibly coverage truth surfaces only if shipped behavior changes documented format support. Next: present the plan gate and wait for approval before implementation code.
20260504-1748 — build implementation complete after approval for base runtime preview dependencies. Added `doc-web preview` and the Python API, split the preview runtime into focused modules (`doc_web/preview.py`, `doc_web/preview_pdf.py`, `doc_web/preview_docx.py`, `doc_web/preview_bundle.py`, `doc_web/preview_support.py`), added preview metadata and selector-map schemas plus validator registration, exposed preview schema versions/fingerprint/status vocabulary through `doc-web contract --json`, and added `pypdf` / `python-docx` to base runtime dependencies. Preview output remains a normal bundle with `manifest.json`, `index.html`, semantic entries, and `provenance/blocks.jsonl`, plus `preview_metadata.json`, `preview_status.jsonl`, `preview_to_full_selectors.json`, `cache/cache_identity.json`, and reusable `cache/parsed_units.jsonl`. Docs updated in `README.md`, `docs/doc-web-bundle-contract.md`, `docs/dossier-doc-web-handoff.md`, `docs/RUNBOOK.md`, and Dossier readiness/runtime notes. Artifact inspection evidence: `output/runs/story228-preview-flat-pdf/output/html/preview_metadata.json` reports `coverage_state=complete`, `page_count=2`, `text_layer_available=true`, `ocr_needed=false`, first status `7.639ms`, preview ready `28.433ms`; first provenance/cache row is `blk-page-001-0001` from `pdf-page-1-text-0001`, quote `Acme Community Arts Initiative`. `output/runs/story228-preview-scanned-pdf/output/html/preview_metadata.json` reports `coverage_state=deferred`, `page_count=4`, `text_layer_available=false`, `ocr_needed=true`, warning `No usable text layer was found inside the preview budget; OCR is deferred.`; both `provenance/blocks.jsonl` and `cache/parsed_units.jsonl` have `0` rows and `page-001.html` shows the deferred OCR message. `output/runs/story228-preview-docx/output/html/manifest.json` reads `chapter-001` / `chapter-002` with titles `Overview` / `Roster`; provenance and parsed cache have `6` rows with pageless `docx-paragraph-*` source ids, including `blk-chapter-001-0003` from `docx-paragraph-0004` for `The wider proof should keep both paragraphs...`; selector maps preserve preview/full block ids. Mechanical validation evidence: all three preview bundles validated as `doc_web_bundle_manifest_v1`, `doc_web_provenance_block_v1`, `doc_web_preview_metadata_v1`, and `doc_web_preview_selector_map_v1`; targeted preview/contract tests passed (`7 passed`); stale `*.pyc` cleared; `make lint` passed; `make check-size` passed and no new preview module exceeds 400 lines; `git diff --check` passed; full suite passed after the final refactor (`692 passed, 4 warnings in 714.34s`). Methodology/format notes: no coverage-matrix update needed because preview mode does not change final maintained format graduation truth, and no eval registry update needed because no eval/golden files changed. Result: Story 228 remains `In Progress`; `Build complete` is checked, while `/validate` and `/mark-story-done` remain pending.
20260504-1910 — performance follow-up on user-requested real inputs: tested `doc-web preview` against `/Users/cam/Documents/Projects/doc-web/input/f5-robo-rally-rulebook.pdf`, `/Users/cam/Documents/Projects/doc-web/input/Onward to the Unknown.pdf`, and `/Users/cam/Documents/Projects/doc-web/input/onward-to-the-unknown-images`. The first two PDFs already stayed inside budget; the image-directory input initially failed with `IsADirectoryError` because preview hashed only file inputs. Fixed that by adding directory source hashing and structural image-directory preview support (`doc_web/preview_images.py`), plus regression coverage in `tests/test_doc_web_preview.py`; docs now state that image-directory preview is structural-only and OCR-deferred. Five-run CLI timing evidence with default `max_sample_units=3`: RoboRally PDF is `6.7 MB`, `16` pages, sampled preview with `157` provenance rows; internal preview-ready max `360.426ms`, CLI wall max `715.673ms`. Onward PDF is `160 MB`, `127` pages, sampled preview with `11` provenance rows; internal preview-ready max `454.633ms`, CLI wall max `796.914ms`. Onward image directory is `200 MB`, `127` JPEGs, deferred structural preview with `0` provenance/cache text rows; internal preview-ready max `561.562ms`, CLI wall max `901.023ms`. Validated one final bundle from each case as `doc_web_bundle_manifest_v1`, `doc_web_provenance_block_v1`, `doc_web_preview_metadata_v1`, and `doc_web_preview_selector_map_v1`. Manual inspection: RoboRally metadata reports `page_count=16`, `sampled_page_count=3`, `text_layer_available=true`; Onward PDF metadata reports `page_count=127`, `metadata_creator=OCRmyPDF 16.6.2 / Tesseract OCR-hOCR 5.5.0`, and the sample text is low-quality OCR, so it is not evidence for never-OCRed input quality; Onward image metadata reports `format=image_directory`, `image_count=127`, `total_image_bytes=209560342`, `text_layer_available=false`, `ocr_needed=true`, `skipped_units=127`, and `page-001.html` shows the OCR-deferred image-directory status. Mechanical checks after the image-directory addition: `python -m pytest tests/test_doc_web_preview.py -q` passed (`6 passed`). Broader checks still need to be rerun before marking validation complete.
20260504-2022 — high-level content hint and bounded image OCR follow-up: reread the Dossier preview requirement and confirmed the preview bundle must say what the document basically appears to be, not only whether text exists. Added `content_hint` to preview metadata and CLI JSON output with status, title guess, document-kind hint, summary, evidence snippets, text-quality signal, basis, and warnings; the hint stays explicitly non-final and does not become extracted graph truth. Added fast Tesseract OCR sampling for image directories with a `2s` per-image timeout, `1600px` thumbnail cap, and early stop after useful text; default image previews now try the likely title page first and stop after enough text, preserving structural facts and sampled/deferred honesty. Fresh real-input evidence from `output/runs/story228-final-samples/`: RoboRally PDF (`6.7 MB`, `16` pages) sampled `3` pages, produced `157` provenance rows, content hint `available` / `game rulebook or guide`, first status `8.517ms`, preview ready `380.66ms`, CLI wall `1.07s`; Onward PDF (`160 MB`, `127` pages) sampled `3` pages, produced `11` provenance rows, content hint `low_quality` / `genealogy or family-history document` because the embedded OCR text is sparse/noisy, first status `9.528ms`, preview ready `516.201ms`, CLI wall `1.21s`; Onward image directory (`200 MB`, `127` JPEGs, no text layer) OCRed `1` image, produced `1` provenance row, content hint `available` / `biographical or historical document`, title `ONWARD TO THE UNKNOWN 1887 - 1987 Moise and Sophie L’Heureux`, first status `9.451ms`, preview ready `1879.606ms`, CLI wall `2.65s`. All three final sample bundles freshly validated as `doc_web_bundle_manifest_v1`, `doc_web_provenance_block_v1`, `doc_web_preview_metadata_v1`, and `doc_web_preview_selector_map_v1`. Focused mechanical checks after this patch: `python -m ruff check doc_web/preview_images.py doc_web/preview_content_hint.py doc_web/preview.py schemas.py tests/test_doc_web_preview.py` passed; `python -m pytest tests/test_doc_web_preview.py tests/test_doc_web_cli_contract.py::test_runtime_contract_payload_has_required_fields tests/test_doc_web_cli_contract.py::test_doc_web_module_cli_emits_machine_readable_contract_json -q` passed (`8 passed`). Next: rerun broader lint/size/methodology checks before `/validate`.
20260504-2036 — final verification after the content-hint/OCR patch: `make lint` passed, `make check-size` passed with only pre-existing large modules listed and no new preview module over the size threshold, `git diff --check` passed, `PYTHONDONTWRITEBYTECODE=1 make methodology-compile` regenerated `docs/methodology/graph.json` and `docs/stories.md`, `PYTHONDONTWRITEBYTECODE=1 make methodology-check` passed, and the full suite passed after the latest changes (`693 passed, 4 warnings in 769.06s`). Story remains `In Progress`; validation and mark-done gates remain open for the explicit `/validate` and `/mark-story-done` steps.
20260504-2048 — content-hint wording correction: removed hedging from end-user summaries (`Likely`, `titled or headed`) and kept uncertainty in structured `status`/`warnings` instead. Also added generic title cleanup for obvious source-site suffixes in PDF metadata, so `Robo Rally Rulebook - 1jour-1jeu.com` presents as `Robo Rally Rulebook`. Fresh regenerated sample summaries: RoboRally PDF => `Robo Rally Rulebook is a game rulebook or guide.`; Onward PDF => `Onward to the Unknown: A Genealogy and Biography of the L'Heureux Family is a genealogy or family history.` with `status=low_quality`; Onward image directory => `ONWARD TO THE UNKNOWN 1887 - 1987 Moise and Sophie L’Heureux is a family history or biography.`. Added regression coverage in `tests/test_doc_web_preview.py` to reject the bad phrases and assert the RoboRally direct summary. Checks after this wording patch: `python -m pytest tests/test_doc_web_preview.py -q` passed (`7 passed`), `python -m ruff check doc_web/preview_content_hint.py tests/test_doc_web_preview.py` passed, all three regenerated `preview_metadata.json` artifacts validate as `doc_web_preview_metadata_v1`, `make lint` passed, and `git diff --check` passed. Full suite was not rerun after this wording-only patch; latest full-suite evidence remains the 2036 run before this small template change.
20260504-2131 — AI content-hint summary pass: replaced the user-facing deterministic summary as the preferred path with `--content-hint-mode auto`, which uses a bounded `gpt-4.1-nano` JSON summary over sampled preview text when `DOC_WEB_OPENAI_API_KEY` is configured and otherwise records deterministic fallback. Kept deterministic classification as the fallback, removed joined synonym labels (`or`) from fallback kinds, added title/source-site cleanup, banned hedge phrases from accepted model summaries, normalized generic `The document...` openers to use the title, and disabled OpenAI SDK retries so timeouts cannot multiply past the preview deadline. Runtime cache identity now records requested/effective content-hint mode, provider/model, prompt version, sample hash, cache key, timeout, and fallback reason. Live `auto` samples with the main checkout OpenAI key loaded into the child process: RoboRally PDF summary `Robo Rally Rulebook provides rules and components for the Robo Rally tabletop game, including game setup, gameplay phases, and equipment.`, `summary_ms=1295.155`, `preview_ready_ms=1659.914`; Onward PDF summary `A family history detailing the genealogy and biography of the L'Heureux family.`, `status=low_quality`, `summary_ms=1440.63`, `preview_ready_ms=1954.087`; Onward image directory summary `A family history documenting the lives of Moise and Sophie L’Heureux from 1887 to 1987.`, `summary_ms=1155.657`, `preview_ready_ms=2614.909` after bounded Tesseract OCR of `1/127` images. Validation evidence: all three regenerated sample bundles validate as `doc_web_bundle_manifest_v1`, `doc_web_provenance_block_v1`, `doc_web_preview_metadata_v1`, and `doc_web_preview_selector_map_v1`; `python -m pytest tests/test_doc_web_preview.py tests/test_doc_web_cli_contract.py::test_runtime_contract_payload_has_required_fields tests/test_doc_web_cli_contract.py::test_doc_web_module_cli_emits_machine_readable_contract_json -q` passed (`12 passed`); `make lint` passed; `git diff --check` passed. Full suite was not rerun after this AI-summary patch; latest full-suite evidence remains the 2036 run.
20260504-2159 — `/validate 228` completed after fixing validation findings. Findings addressed during validation: explicit tiny preview timeouts previously raised a traceback instead of a machine-readable failed status, so `doc_web/cli.py` now catches `PreviewTimeout`, writes `preview_status.jsonl` with `stage=failed`, and exits `1` with a JSON failure payload; the installable preview path also imported repo-local `modules.common`, so preview JSON/time helpers now live in `doc_web/preview_support.py`, content hints use the packaged OpenAI SDK directly, `openai>=1.52,<2` is a base runtime dependency, and the pip-install smoke now runs `doc-web preview` from outside the repo root. Fresh focused checks passed: `python -m pytest tests/test_doc_web_preview.py tests/test_doc_web_cli_contract.py::test_runtime_contract_payload_has_required_fields tests/test_doc_web_cli_contract.py::test_doc_web_module_cli_emits_machine_readable_contract_json tests/test_doc_web_cli_contract.py::test_pip_install_exposes_doc_web_console_script -q` => `15 passed`. Fresh real sample outputs in `output/runs/story228-final-samples/`: RoboRally PDF (`6.7 MB`, `16` pages) produced `157` provenance rows, summary `Robo Rally Rulebook provides rules, components, and gameplay procedures for Robo Rally, a robot programming tabletop game.`, `content_hint.status=available`, `document_kind_hint=game rulebook`, `preview_ready_ms=2340.529`, CLI wall `3.05s`; Onward PDF (`160 MB`, `127` pages) produced `11` provenance rows, summary `A family history documenting the genealogy and biography of the L'Heureux family.`, `content_hint.status=low_quality`, warning about sparse/noisy preview text, `preview_ready_ms=2397.781`, CLI wall `3.04s`; Onward image directory (`200 MB`, `127` JPEGs, no internal text layer) OCR-sampled `1/127` images, produced `1` provenance row, summary `ONWARD TO THE UNKNOWN 1887-1987 is a family history about Moise and Sophie L’Heureux.`, `content_hint.status=available`, warning `Preview OCR sampled 1 of 127 images.`, `preview_ready_ms=1959.521`, CLI wall `2.51s`. All three final sample bundles freshly validated as `doc_web_bundle_manifest_v1`, `doc_web_provenance_block_v1`, `doc_web_preview_metadata_v1`, and `doc_web_preview_selector_map_v1`, and metadata was manually inspected with `jq`. Repo checks passed: `make lint`, `make check-size` (success; it now lists `doc_web/preview_content_hint.py` at `526` lines along with other large files), `git diff --check`, and full `make test` (`699 passed, 4 warnings in 881.46s`). Validation gate checked; story remains `In Progress` for `/mark-story-done`.
20260504-2223 — performance-first validation adjustment: tightened default AI content-hint timeout from `1.5s` to `0.75s`, made `auto` skip model calls for image-directory OCR previews, and improved deterministic fallback summaries so performance remains the primary metric when the cheap model misses the preview budget. Final sample outputs regenerated with defaults: RoboRally PDF (`6.7 MB`, `16` pages) produced `157` provenance rows, summary `Robo Rally Rulebook is a game rulebook covering components, setup, gameplay phases, and robot programming.`, `content_hint.status=available`, `preview_ready_ms=1975.239`, CLI wall `2.54s`; Onward PDF (`160 MB`, `127` pages) produced `11` provenance rows, summary `Onward to the Unknown is a family history about the L'Heureux family.`, `content_hint.status=low_quality`, warning about sparse/noisy preview text, `preview_ready_ms=1812.038`, CLI wall `2.25s`; Onward image directory (`200 MB`, `127` JPEGs, no internal text layer) OCR-sampled `1/127` images, produced `1` provenance row, summary `ONWARD TO THE UNKNOWN 1887-1987 is a family history about Moise and Sophie L’Heureux.`, `content_hint.status=available`, warning `Preview OCR sampled 1 of 127 images.`, `preview_ready_ms=2065.453`, CLI wall `2.83s`. Final sample bundles again validated as `doc_web_bundle_manifest_v1`, `doc_web_provenance_block_v1`, `doc_web_preview_metadata_v1`, and `doc_web_preview_selector_map_v1`; metadata and provenance row counts were manually inspected with `jq` and `wc -l`. Fresh checks after the final tuning: focused preview/install slice passed (`17 passed`), `make lint` passed, `make check-size` passed (success; `doc_web/preview_content_hint.py` is now `573` lines and listed with other large files), `git diff --check` passed, and full `make test` passed (`701 passed, 4 warnings in 778.45s`). Validation gate remains checked; story remains `In Progress` for `/mark-story-done`.
20260504-2233 — `/mark-story-done` close-out: rechecked Story 228 workflow gates, acceptance criteria, tasks, tenet checklist, dependency status, ADR-002 alignment, docs updates, and validation evidence. Dependencies Story 152, Story 154, and Story 156 are already `Done` in `docs/stories.md`; ADR-002 remains aligned because preview extends the standalone `doc-web` structural bundle/provenance boundary rather than moving parsing into Dossier. Fresh validation evidence from the current code tip remains the final `/validate` pass: three real sample bundles in `output/runs/story228-final-samples/` validated as `doc_web_bundle_manifest_v1`, `doc_web_provenance_block_v1`, `doc_web_preview_metadata_v1`, and `doc_web_preview_selector_map_v1`; focused preview/install slice passed (`17 passed`); `make lint`, `make check-size`, `git diff --check`, `make methodology-compile`, `make methodology-check`, and full `make test` passed (`701 passed, 4 warnings in 778.45s`). Marked status `Done`, checked the `/mark-story-done` gate, and added a CHANGELOG entry. Recommended next step: `/check-in-diff`.
20260506-0335 — post-closeout model refresh note: screened OpenAI `chat-latest` / GPT-5.5 Instant against the cheap content-hint preview seam. The current `doc_web/preview_content_hint.py` path uses Chat Completions and default `gpt-4.1-nano`; on representative Robo Rally rulebook sample text, `gpt-4.1-nano` succeeded with `summary_ms=2106.117`, while `chat-latest` failed before quality comparison with `Unsupported parameter: 'max_tokens' is not supported with this model` and correctly fell back to deterministic summary output. Result: no content-hint default or implementation changed; making the alias callable here would require a separate Responses preview path and has no measured quality/latency/cost win. Portable proof: `docs/evals/attempts/010-chat-latest-instant-bounded-challenger.md`.
20260506-1358 — post-closeout Storybook follow-up handoff: the Storybook-reported portability and mixed-PDF OCR defects are intentionally tracked in Story 229 instead of reopening Story 228. Story 228 remains the completed preview-mode baseline; see Story 229 for the follow-up acceptance criteria, implementation details, artifact inspection evidence, and validation checks.
