---
title: "Establish a Bounded Washington Database English-Longhand Benchmark Slice"
status: "Blocked"
priority: "High"
ideal_refs:
  - "Requirement #2 (Detect), Requirement #3 (Extract), Requirement #6 (Validate), Any format, any condition, Fidelity to the source, Traceability is the product"
spec_refs:
  - "spec:2"
  - "spec:2.1"
  - "spec:2.2"
  - "spec:8"
adr_refs: []
depends_on:
  - "212"
category_refs:
  - "spec:2"
  - "spec:8"
compromise_refs:
  - "C1"
  - "B1"
input_coverage_refs:
  - "handwritten-notes"
architecture_domains:
  - "ocr_and_extraction"
roadmap_tags:
  - "campaign:maintained-intake-honesty"
legacy_system: ""
---

# Story 215 — Establish a Bounded Washington Database English-Longhand Benchmark Slice

**Priority**: High
**Status**: Blocked
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, `docs/scout/scout-014-degraded-handwriting-eval-sources.md`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/stories/story-191-finish-real-handwritten-ocr-on-the-loc-fixture-pair.md`, `docs/stories/story-211-scout-degraded-handwriting-and-historical-script-eval-sources.md`, `docs/stories/story-212-diem-htr-historical-handwriting-benchmark-slice.md`, and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower ADR or runbook governing Washington benchmark adoption beyond Scout 014 and Story 212
**Depends On**: Story `212`

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

Story 212 proved that a bounded external historical-handwriting benchmark can
pressure the blocked handwritten OCR line without pretending it changes the
repo's maintained support claim, but its DiEm slice is still a worse
language/domain match than the Library of Congress blocker pair. Scout 014 and
Story 212 both identify `Washington Database` as the next closer English
longhand comparator, while also recording the real limits: registration-gated
access, non-commercial terms, and line/word-level truth rather than a public
page-level corpus. This story should determine whether the smallest lawful
Washington slice can become a comparison-only benchmark in this repo, or
whether the source should stay parked behind an explicit access/fit blocker
instead of surviving only as a vague next-step note.

## Acceptance Criteria

- [ ] A bounded Washington comparison surface is defined honestly before any OCR claim:
  - [ ] the story records the exact registration/access path, visible usage terms, and whether the current environment can lawfully reach the needed assets
  - [ ] the story names the exact page, line, and/or word IDs selected and explains whether the benchmark uses page images, line images, word images, or a documented reconstruction path
  - [ ] if lawful or reproducible access cannot be verified, the story does not fake benchmark readiness; it either stays `Draft` with explicit missing substrate or closes `Blocked` with blocker truth
- [ ] If access is viable, a fresh current-pass comparison-only benchmark exists:
  - [ ] the current maintained OCR lane or smallest comparable harness runs unchanged first on the selected Washington slice
  - [ ] artifacts are written under `output/runs/` and manually inspected
  - [ ] the benchmark records exact source IDs, truth files, and any normalization or mapping logic needed to compare the source to repo outputs
- [ ] The result is translated into honest repo truth:
  - [ ] the story states whether Washington is usable as comparison-only benchmark evidence, blocked on access/terms, or a poor fit
  - [ ] `docs/evals/registry.yaml` and `tests/fixtures/formats/_coverage-matrix.json` remain unchanged unless the work actually creates a durable local eval surface
  - [ ] if Washington is useful but still insufficient, the story names the exact next follow-up instead of leaving another vague dataset note

## Out of Scope

- Fixing the maintained handwritten OCR runtime in the same story
- Marking `handwritten-notes` as `passing`
- Importing the full Washington corpus into the repo
- Turning a comparison-only source into a durable maintained eval line unless this story actually proves that surface honestly
- Broad legal review beyond recording the visible registration and non-commercial posture plus the concrete repo-usage implications
- Reopening Story 191 without fresh evidence that materially changes its unblock condition

## Approach Evaluation

- **Simplification baseline**: before writing new benchmark code, verify whether the current environment can access a lawful Washington slice and whether the existing handwritten harness or a thin story-local adapter can benchmark it honestly. If access or truth-shape mapping fails, stop there instead of forcing a fake benchmark.
- **AI-only**: a direct OCR call on bounded Washington assets may be part of the benchmark once the source is available, but it cannot answer the access, terms, provenance, or source-to-truth mapping questions by itself.
- **Hybrid**: likely best. Use code for acquisition checks, bounded slice selection, truth normalization, and score packaging; use the existing OCR lane for the actual extraction.
- **Pure code**: only appropriate for access probing, source normalization, and benchmark orchestration. It cannot answer handwriting fidelity on its own.
- **Repo constraints / prior decisions**: Story 191 remains explicitly blocked on missing OCR capability for real historical handwriting. Story 211 narrowed the source options, and Story 212 proved one bounded external benchmark surface with negative evidence while routing the next follow-up to Washington. Scout 014 explicitly says Washington is comparison-only for this repo because access is registration-gated and terms are non-commercial. `docs/evals/README.md` says the registry should only change when a real maintained eval surface exists. ADR-002 and ADR-003 do not change this line because the work is evidence-gathering only, not a runtime-boundary change.
- **Existing patterns to reuse**: `scripts/spikes/diem_htr_benchmark.py`, `tests/test_diem_htr_benchmark.py`, `benchmarks/scripts/run_handwritten_notes_eval.py`, `benchmarks/scorers/handwritten_notes_transcription.py`, Story 208's bounded benchmark discipline, Scout 014's source rubric, and Story 212's comparison-only packaging pattern.
- **Eval**: the deciding evidence is whether a bounded Washington slice can be acquired lawfully, mapped to an inspectable comparison surface, and measured in a way that adds closer-language pressure than DiEm without widening the support claim by inertia. Success is a trustworthy comparison-only benchmark or an explicit blocker, not a passing OCR score.

## Tasks

- [ ] Verify the exact Washington acquisition path and visible usage constraints in the current environment:
  - [ ] record the registration/access steps and non-commercial terms from the primary source
  - [ ] verify whether the needed assets are actually reachable from this environment
  - [ ] verify whether page, line, or word assets are sufficient for an honest benchmark shape
- [ ] Define the smallest honest Washington slice and benchmark mapping:
  - [ ] choose exact source IDs and document why they pressure the blocked LOC line better than DiEm
  - [ ] decide whether the benchmark should run on page images, line images, word images, or a documented reconstruction path
  - [ ] if the source cannot support a coherent comparison shape, record that explicitly instead of forcing a benchmark
- [ ] Implement the smallest honest benchmark harness only if the access path is verified:
  - [ ] prefer a new story-local helper under `scripts/spikes/` over inflating the already-large DiEm helper unless the shared code is obviously reusable
  - [ ] keep external-corpus handling explicit and bounded
  - [ ] preserve raw source metadata, OCR outputs, and comparison summaries under `output/runs/`
- [ ] Run the maintained baseline on the selected slice and manually inspect artifacts if access succeeds
- [ ] Decide whether Washington earns a comparison-only note, an explicit blocked result, or a durable eval follow-up and update docs accordingly
- [ ] If this story changes documented format coverage or graduation reality: update `tests/fixtures/formats/_coverage-matrix.json` and any relevant methodology state honestly
- [ ] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [ ] Run required checks for touched scope:
  - [ ] Default Python checks: `make test`
  - [ ] Default Python lint: `make lint`
  - [ ] If the benchmark helper or pipeline behavior changes: run the exact story-local command, verify artifacts in `output/runs/`, and manually inspect the benchmark JSON/JSONL plus representative OCR outputs
  - [ ] If agent tooling changed: `make skills-check`
- [ ] If this story graduates into a durable eval or golden surface: run `/improve-eval` and update `docs/evals/registry.yaml`
- [ ] Search all docs and update any related to what we touched
- [ ] Verify Central Tenets:
  - [ ] T0 — Traceability: benchmark outputs name exact Washington IDs, truth files, OCR run IDs, and inspected artifact paths
  - [ ] T1 — AI-First: the story measures the existing OCR lane before proposing new deterministic logic
  - [ ] T2 — Eval Before Build: access and benchmark shape are verified before any broader runtime change
  - [ ] T3 — Fidelity: source truth is preserved verbatim and any unusable source/shape mismatch is reported explicitly
  - [ ] T4 — Modular: the work stays a bounded comparison helper or story-local harness, not a hard-coded shared runtime dependency
  - [ ] T5 — Inspect Artifacts: the benchmark summaries and OCR artifacts are opened and checked manually, not just scored

## Workflow Gates

- [ ] Build complete: implementation finished, required checks run, and summary shared
- [ ] Validation complete or explicitly skipped by user
- [ ] Story marked done via `/mark-story-done`

## Blocker Summary

Story 215 is currently blocked on external access, not on missing repo
benchmark substrate. The official Washington Database surface requires
registration before download, the unauthenticated archive URL redirects to a
login gate instead of serving the dataset, and this repo has no registered
session or lawful local cache to inspect. Without the actual archive contents,
the story cannot honestly select a bounded slice, verify the benchmark shape,
or run a comparison-only benchmark.

## Blocker Evidence

- Fresh current-pass primary-source verification on 2026-04-11:
  `https://fki.tic.heia-fr.ch/databases/washington-database` states that the
  Washington Database includes `20 pages`, `656 text lines`, and `4,894 word
  instances`; exposes `binarized and normalized text line images` and
  `binarized and normalized word images`; provides transcription at
  `line-level` and `word-level`; and says, "If not already done, we ask you to
  register before downloading the database."
- Fresh current-pass primary-source verification on 2026-04-11:
  `https://fki.tic.heia-fr.ch/register` is a live registration form requiring
  user-specific fields (`firstname`, `lastname`, `organisation`, `email`,
  `password`) and repeats the visible terms: "This database may be used for
  non-commercial research purpose only."
- Fresh current-pass environment probe on 2026-04-11:
  unauthenticated `GET https://fki.tic.heia-fr.ch/DBs/iamHistDB/data/washingtondb-v1.0.zip`
  returns `302` with `Location: http://fki.tic.heia-fr.ch/login` and does not
  serve dataset bytes. Follow-up attempts from this environment time out at the
  redirected login host, so the archive is not reachable here without a
  registered/login-backed path.
- Local substrate is otherwise present. Verified in this pass that the repo
  already has a bounded comparison-only benchmark pattern
  (`scripts/spikes/diem_htr_benchmark.py`), a test surface for that helper
  (`tests/test_diem_htr_benchmark.py`), and a handwritten eval harness that
  only needs `transcript`, `images`, and `pdf` fixture paths
  (`benchmarks/scripts/run_handwritten_notes_eval.py`). That means the blocker
  is access to Washington assets, not missing local orchestration code.

## Unblock Condition

Unblock this story only when one of these is true:

1. A lawful Washington access path is available in the current environment:
   a registered/login-backed session or a user-provided local cache of the
   archive that can be inspected and used under the source's non-commercial
   terms.
2. The accessible archive contents are verified in the current pass and shown
   to support one honest benchmark shape for this repo: direct line-image
   comparison, word-image comparison, or a documented wrapper path into the
   existing handwritten harness.

If neither condition is met, keep this story blocked and prefer another public
historical-handwriting source over forcing a benchmark from metadata alone.

## Architectural Fit

- **Owning module / area**: external handwritten-benchmark harnessing around `scripts/spikes/`, the existing handwritten OCR recipes, and story-local comparison artifacts rather than the maintained runtime itself
- **Methodology reality**: this work belongs to `spec:2` and `spec:8`. In `docs/methodology/state.yaml`, `C1` remains in `climb` and `B1` remains in `hold`; the relevant coverage row is `handwritten-notes`, which is still `has-fixture` and explicitly blocked by real OCR quality on the LOC pair
- **Substrate evidence**: verified in this pass that the repo already has the comparison-only benchmark pattern from Story 212 (`scripts/spikes/diem_htr_benchmark.py`, `tests/test_diem_htr_benchmark.py`), the maintained handwritten eval harness (`benchmarks/scripts/run_handwritten_notes_eval.py`), the scorer (`benchmarks/scorers/handwritten_notes_transcription.py`), and the story/scout decision record naming Washington as the next comparator. Missing or partial substrate is equally explicit: there is no Washington acquisition helper, no Washington-local cache, and no repo-verified archive to inspect. The official public metadata says the downloadable surface is line/word-based, but the actual archive bytes are still unreachable here because the unauthenticated download redirects to login. That is why this story is now `Blocked`, not `Pending`
- **Data contracts / schemas**: prefer story-local benchmark summaries plus existing `page_html_v1` outputs where possible. If the source only supports line/word-level comparison, keep that contract in story-local JSON rather than introducing a shared schema prematurely
- **File sizes**: `docs/stories/story-215-washington-database-english-longhand-benchmark-slice.md` is 127 lines at bootstrap, `docs/stories/story-212-diem-htr-historical-handwriting-benchmark-slice.md` is 174, `docs/scout/scout-014-degraded-handwriting-eval-sources.md` is 78, `scripts/spikes/diem_htr_benchmark.py` is 634, `tests/test_diem_htr_benchmark.py` is 109, `benchmarks/scripts/run_handwritten_notes_eval.py` is 330, `benchmarks/scorers/handwritten_notes_transcription.py` is 119, `docs/evals/registry.yaml` is 2084, and `tests/fixtures/formats/_coverage-matrix.json` is 564. The DiEm helper and the two canonical truth surfaces are already large, so any follow-up should stay surgical or prefer new story-local files
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, Scout 014, and Stories 191/211/212. Search across `docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` found no narrower ADR or runbook governing Washington benchmark adoption beyond the scout and recent story handoff. ADR-002 and ADR-003 remain unchanged because this story does not alter the `doc-web` boundary

## Files to Modify

- `docs/stories/story-215-washington-database-english-longhand-benchmark-slice.md` — keep the story record, plan, and close-out truth current (127 lines at bootstrap)
- `scripts/spikes/washington_database_benchmark.py` — bounded Washington acquisition and comparison helper if the access path proves viable (new file)
- `tests/test_washington_database_benchmark.py` — unit coverage for any new Washington helper or normalization logic (new file)
- `docs/evals/registry.yaml` — only if the story honestly creates a durable local eval/backlog surface (2084 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — only if the story materially changes the documented handwritten support reality (564 lines)
- `docs/scout/scout-014-degraded-handwriting-eval-sources.md` — only if the source posture or next-step packaging needs a surgical follow-up note (78 lines)

## Redundancy / Removal Targets

- Any vague Washington follow-up notes left behind in Story 212 or Scout 014 once Story 215 becomes the owning packaging surface
- Avoid growing `scripts/spikes/diem_htr_benchmark.py` unless shared code is clearly reusable enough to justify touching an already-634-line helper

## Notes

- New story justification: Story 212 closed a DiEm-specific benchmark slice and validated that comparison-only external benchmarking is useful. Washington is a different acquisition, licensing, and truth-granularity seam, so reopening Story 212 would blur completed evidence with a new substrate-verification problem
- Current status rationale: this story is now `Blocked` because the access path is externally gated and the archive itself is not available in the current environment. `/build-story` should only reopen it after a lawful access path or user-provided cache exists
- Comparison-only rule: even a successful Washington benchmark should not widen `handwritten-notes` support or create a maintained eval by default. It has to earn that claim explicitly

## Plan

This story is blocked on access, so the visible plan is the unblock path rather
than immediate implementation.

1. Obtain or provide lawful dataset access.
   - Supply a registered/login-backed Washington session or a local cache of
     `washingtondb-v1.0.zip` that is lawful for this repo's comparison-only,
     non-commercial benchmark use.
   - Without that, do not build benchmark code against guessed archive
     contents.
2. Reassess the benchmark shape from the real archive.
   - Inspect the archive structure and README.
   - Confirm whether a bounded line-image, word-image, or wrapped-image slice
     is the honest fit for the existing handwritten benchmark harness.
3. Reopen only if those checks pass.
   - If access succeeds and the archive supports a coherent slice, promote the
     story out of `Blocked`, write the real implementation plan, and then build
     the smallest story-local helper.
   - If access still fails or the archive shape is unusable, keep the story
     blocked and prefer a different public source.

## Work Log

20260411-1429 — create-story: created Story 215 after `/triage` found no open build-ready story and Story 212 explicitly named `Washington Database` as the next bounded comparator. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, Scout 014, and Stories 191/211/212. Result: a new story is honest instead of reopening Story 212 because DiEm benchmarking is complete and Washington introduces a different acquisition/terms/truth-shape seam. The story starts `Draft`, not `Pending`, because the repo does not yet verify Washington access, lawful comparison-only use, or the exact benchmark mapping from source assets into the existing handwritten harness. Next step: `/build-story` should verify the acquisition path first, then either promote the story with a bounded benchmark plan or convert it to an explicit blocker if access/terms fail.
20260411-1441 — /build-story exploration: re-read `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/evals/registry.yaml`, Scout 014, and Stories 191/211/212 before tracing the current benchmark substrate in `scripts/spikes/diem_htr_benchmark.py`, `tests/test_diem_htr_benchmark.py`, `benchmarks/scripts/run_handwritten_notes_eval.py`, and `benchmarks/scorers/handwritten_notes_transcription.py`. Fresh primary-source verification on 2026-04-11 confirmed that `https://fki.tic.heia-fr.ch/databases/washington-database` publicly documents only a registration-gated download and a line/word-level benchmark surface, and `https://fki.tic.heia-fr.ch/register` is a live registration form with non-commercial terms. Fresh environment probe on 2026-04-11 showed `GET https://fki.tic.heia-fr.ch/DBs/iamHistDB/data/washingtondb-v1.0.zip` returns `302` to `http://fki.tic.heia-fr.ch/login` instead of serving dataset bytes, and follow-up access attempts from this environment time out at that login host. Result: the local benchmark harness is sufficient, but the archive substrate is not available, so the story is no longer an honest `Draft`; it is a concrete external-access blocker. Next step: mark Story 215 `Blocked`, regenerate methodology views, and wait for lawful Washington access or a user-provided local cache before reopening.
20260412-0012 — landing renumber: while rebasing the Story 214 landing branch onto `origin/main`, a different mainline change had already claimed Story `213`. To preserve unique story identifiers, this blocked Washington benchmark record was renumbered from Story `213` to Story `215` without changing its blocked posture, evidence, or unblock condition. Next step: reopen only if a lawful Washington access path or user-provided local cache becomes available.
