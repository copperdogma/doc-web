---
title: "Gemini SDK API-Version Hardening"
status: "Done"
priority: "Medium"
ideal_refs:
  - "Requirement #3 (Extract), Requirement #4 (Illustrate), Traceability is the product, Fidelity to the source"
spec_refs:
  - "spec:2"
  - "spec:2.1"
  - "spec:4"
  - "spec:4.1"
adr_refs: []
depends_on: []
category_refs:
  - "spec:2"
  - "spec:4"
compromise_refs:
  - "C1"
  - "C4"
input_coverage_refs:
  - "handwritten-notes"
  - "image-directory-scans"
architecture_domains:
  - "ocr_and_extraction"
  - "document_structure_and_consistency"
roadmap_tags:
  - "campaign:maintained-intake-honesty"
legacy_system: ""
---

# Story 227 — Gemini SDK API-Version Hardening

**Priority**: Medium
**Status**: Done
**Decision Refs**: Conductor Scout 027
(`/Users/cam/Documents/Projects/conductor/docs/scout/scout-027-gemini-sdk-v1-default-shift.md`),
Google Gemini API version docs (`https://ai.google.dev/gemini-api/docs/api-versions`),
Google Gemini libraries docs (`https://ai.google.dev/gemini-api/docs/libraries`),
`docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`,
`docs/methodology/graph.json`, `docs/evals/registry.yaml`, and no narrower
repo-local ADR found for Gemini SDK API-version policy
**Depends On**: None

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

Google has announced that the next major official Gemini SDK release in
February 2027 will default to the stable `v1` API endpoint instead of `v1beta`.
`doc-web` directly uses the official Python `google-genai` client for Gemini
vision OCR and crop helpers, and those clients currently rely on the SDK
default. This story makes the API version explicit so future SDK upgrades do
not silently change the maintained OCR/crop lane behavior.

## Eval Ladder Context

- **Eval ladder**: no new quality eval is needed for the first hardening pass.
  The current maintained Gemini-dependent surfaces are the OCR rescue and crop
  detector/validator lanes recorded in `docs/evals/registry.yaml`; this story
  is plumbing hardening that should preserve existing behavior by explicitly
  choosing the current beta channel.

## Acceptance Criteria

- [x] The shared Gemini client wrapper constructs official `google-genai`
  clients with an explicit API version rather than relying on SDK defaults.
- [x] Direct benchmark helpers that instantiate `google.genai.Client` also use
  the same explicit API-version configuration.
- [x] The default preserves current runtime behavior (`v1beta`) because the
  maintained lanes still include preview model IDs and beta-channel assumptions.
- [x] Focused tests cover the default and override path without requiring live
  Gemini credentials.
- [x] Generated methodology surfaces are refreshed and the story work log names
  the checks run.

## Out of Scope

- Migrating maintained Gemini traffic to the stable `v1` endpoint in this pass
- Rerunning paid Gemini OCR or crop evals
- Changing model IDs, promptfoo providers, recipe winners, or coverage-matrix
  claims
- Fixing Storybook, CineForge, or Dossier direct REST beta endpoint usage

## Approach Evaluation

- **Simplification baseline**: leaving the SDK default alone would keep working
  until a future major SDK upgrade, but it does not satisfy Google's explicit
  guidance to make the API version intentional.
- **AI-only**: not applicable. This is deterministic provider configuration.
- **Hybrid**: not needed. The correct split is code-level explicit versioning
  plus tests.
- **Pure code**: best fit. Add a small shared helper for Gemini API-version
  selection and use it wherever `google-genai` clients are constructed.
- **Repo constraints / prior decisions**: `doc-web` currently treats OCR calls
  as expensive and single-run, and the maintained Gemini lanes include preview
  model IDs such as `gemini-3.1-pro-preview` and `gemini-3-flash-preview`.
  Preserving current behavior is safer than moving to `v1` without a live
  compatibility/eval pass.
- **Existing patterns to reuse**: `doc_web.env` owns repo-local environment
  boundaries; `modules/common/google_client.py` already centralizes the main
  Gemini vision client.
- **Eval**: focused unit tests can prove the client configuration is explicit.
  A paid live compatibility check can be a later story if the repo wants to
  migrate from explicit `v1beta` to stable `v1`.

## Tasks

- [x] Add a shared Gemini API-version helper with default `v1beta` and an
  optional `DOC_WEB_GEMINI_API_VERSION` override for bounded compatibility
  testing.
- [x] Pass `http_options={"api_version": ...}` to the shared
  `genai.Client(...)` construction.
- [x] Update direct benchmark helpers under `benchmarks/scripts/` that
  instantiate `google.genai.Client(...)`.
- [x] Add focused tests for default and override behavior without live Gemini
  calls.
- [x] Run required checks for touched scope:
  - [x] Focused unit tests for Gemini client configuration
  - [x] Default Python lint: `make lint`
  - [x] Default methodology check: `make methodology-compile` and
        `make methodology-check`
  - [x] Full default tests because this touched shared provider client plumbing
- [x] Search all docs and update any related to what we touched.
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: no artifact provenance is weakened by provider
        configuration
  - [x] T1 — AI-First: no deterministic code replaces model judgment
  - [x] T2 — Eval Before Build: no quality claim is made without a live eval
  - [x] T3 — Fidelity: current Gemini OCR/crop behavior is preserved by default
  - [x] T4 — Modular: configuration stays in the shared client/env boundary
  - [x] T5 — Inspect Artifacts: no pipeline artifacts are generated in this
        hardening slice; tests and source inspection are the evidence

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

- **Owning module / area**: `modules/common/google_client.py` owns official
  Gemini SDK client construction; the direct benchmark helpers should reuse the
  same API-version helper.
- **Methodology reality**: this belongs to `spec:2` OCR/extraction and `spec:4`
  illustration extraction because those maintained lanes use Gemini. In
  `docs/methodology/state.yaml`, the relevant domains are
  `ocr_and_extraction` and `document_structure_and_consistency`.
- **Substrate evidence**: `modules/common/google_client.py` imports
  `google.genai` and currently constructs `genai.Client(api_key=...)`;
  `benchmarks/scripts/eval_image_gate.py` and
  `benchmarks/scripts/eval_permissive_gate.py` instantiate
  `google.genai.Client(...)` directly.
- **Data contracts / schemas**: no artifact schema changes. This is provider
  client configuration only.
- **File sizes**: after implementation, `modules/common/google_client.py` is
  143 lines, `benchmarks/scripts/eval_image_gate.py` is 204 lines,
  `benchmarks/scripts/eval_permissive_gate.py` is 159 lines, and
  `tests/test_google_client.py` is 59 lines.
- **Decision context**: reviewed the Conductor scout result, Google docs,
  `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`,
  `docs/methodology/graph.json`, and the Gemini mentions in
  `docs/evals/registry.yaml`. No repo-local ADR directly governs Gemini
  SDK API-version policy.

## Files to Modify

- `modules/common/google_client.py` — add shared API-version helper and pass
  explicit `http_options` into `genai.Client(...)`
- `benchmarks/scripts/eval_image_gate.py` — pass the shared API-version
  options into direct `Client(...)` construction
- `benchmarks/scripts/eval_permissive_gate.py` — same direct helper update
- `tests/test_google_client.py` — focused unit coverage for default and
  override configuration
- `docs/stories/story-227-gemini-sdk-api-version-hardening.md` — story record
- `docs/stories.md` and `docs/methodology/graph.json` — generated views after
  methodology compile

## Redundancy / Removal Targets

- Any duplicated direct `Client(api_key=...)` construction for `google-genai`
  in this repo should either use `GeminiVisionClient` or the shared
  `get_gemini_client_http_options()` helper.

## Notes

- Story number note: this isolated branch is based on `origin/main`, which has
  stories through 225. The primary checkout already has an untracked Story 226
  in progress, so this story intentionally uses 227 to avoid colliding with
  live shared-workspace state.
- Defaulting to explicit `v1beta` is deliberate: it preserves current behavior
  while satisfying Google's future-proofing guidance. A later story can attempt
  `v1` migration if live compatibility checks show the maintained preview lanes
  work there.

## Plan

1. Add `DOC_WEB_GEMINI_API_VERSION` / `v1beta` configuration in
   `modules/common/google_client.py` and use it when constructing the shared
   `genai.Client`.
2. Update the two benchmark scripts that instantiate `google.genai.Client`
   directly so their explicit version matches the runtime helper.
3. Add focused tests that monkeypatch the optional SDK module and verify both
   the default `v1beta` and override `v1` paths.
4. Run focused tests, methodology compile/check, lint, and `git diff --check`.
   Run broader tests if the focused checks expose cross-module risk.

## Work Log

20260430-1105 — create/build-story: created this story from the Conductor Scout
027 finding and promoted it directly to `In Progress` because Cam approved the
explicit implementation step. Fresh evidence before edits: isolated worktree
`/Users/cam/.codex/worktrees/gemini-sdk-api-version-doc-web` is on
`codex/gemini-sdk-api-version` from current `origin/main`; the primary
checkout is dirty and has an untracked Story 226, so this branch uses Story 227
to avoid collision. Source scans found official `google-genai` construction in
`modules/common/google_client.py` plus direct benchmark helper construction in
`benchmarks/scripts/eval_image_gate.py` and
`benchmarks/scripts/eval_permissive_gate.py`. Next step: implement explicit
API-version configuration with tests.

20260430-1122 — implementation complete: added `DOC_WEB_GEMINI_API_VERSION`
with default `v1beta` in `modules/common/google_client.py`, routed the shared
`GeminiVisionClient` through explicit `http_options`, and updated the two
direct benchmark helpers to use the same API-version helper. Added
`tests/test_google_client.py` to prove the default `v1beta`, override `v1`, and
invalid-version paths without live Gemini credentials. Fresh checks in this
pass: `python -m pytest tests/test_google_client.py -q` (`3 passed in 0.92s`),
`python -m py_compile modules/common/google_client.py
benchmarks/scripts/eval_image_gate.py
benchmarks/scripts/eval_permissive_gate.py tests/test_google_client.py`,
`PYTHONDONTWRITEBYTECODE=1 make methodology-compile`,
`PYTHONDONTWRITEBYTECODE=1 make methodology-check`, `make lint`,
`git diff --check`, and full `make test` (`604 passed, 4 warnings in 771.65s
(0:12:51)`). Result: the maintained Gemini SDK path now preserves current
`v1beta` behavior explicitly and can be switched to `v1` later through a
repo-local environment override for bounded compatibility checks. Next step:
`/validate 227`.

20260430-1148 — `/validate 227`: reviewed the full local change set including
untracked `docs/stories/story-227-gemini-sdk-api-version-hardening.md` and
`tests/test_google_client.py`, checked the implementation against all acceptance
criteria, and found no material defects or remaining implementation gaps. Fresh
validation commands in this pass: `git status --short`, `git diff --stat`,
`git diff`, `git ls-files --others --exclude-standard`,
`python -m pytest tests/test_google_client.py -q` (`3 passed in 0.97s`),
`PYTHONDONTWRITEBYTECODE=1 make methodology-check`, `make lint`,
`git diff --check`, and full `make test` (`604 passed, 4 warnings in 866.36s
(0:14:26)`). Result: implementation and validation are complete; the remaining
workflow gap is close-out via `/mark-story-done`.

20260430-1155 — `/mark-story-done 227`: rechecked the completed Story 227
criteria, confirmed the build and validation gates were already satisfied by
the implementation and validation passes, added the close-out changelog entry,
and marked the story `Done`. Fresh close-out evidence before final landing:
`git status --short --branch` showed only the intended Story 227 and Gemini
API-version hardening files changed. Next step: regenerate methodology surfaces,
run the final check-in validation slice, commit, and push to `main`.
