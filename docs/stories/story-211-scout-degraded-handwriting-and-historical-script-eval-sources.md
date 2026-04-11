---
title: "Scout Degraded-Handwriting and Historical-Script Eval Sources"
status: "Pending"
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
  - "208"
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

# Story 211 — Scout Degraded-Handwriting and Historical-Script Eval Sources

**Priority**: High
**Status**: Pending
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/scout.md`, `docs/scout/scout-011-external-document-ingestion-systems.md`, `docs/evals/README.md`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, `docs/stories/story-191-finish-real-handwritten-ocr-on-the-loc-fixture-pair.md`, `docs/stories/story-208-glm-ocr-benchmark-for-handwritten-and-table-heavy-seams.md`, and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower handwriting-eval-source ADR or prior scout focused on degraded historical-script corpora
**Depends On**: Story 208

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

Story 191 is correctly blocked because the current real-fixture handwritten
surface is too narrow and no stronger OCR substrate has cleared it. Story 208
then closed one named challenger as negative evidence. The next honest move is
not another same-surface OCR guess. It is to scout external degraded
handwriting and historical-script eval sources, challenges, datasets, and
OCR-adjacent benchmark surfaces that already contain the pressure cases this
repo lacks: degraded handwriting, archival script, older letterforms, messy
historical documents, or harder transcription truth surfaces. This story
should end with an inspectable sourcing recommendation for our own evals:
which sources are actually usable, under what license/access constraints, and
what exact next local benchmark or fixture-acquisition story they justify.

## Acceptance Criteria

- [ ] A fresh scout expedition exists for external degraded-handwriting / historical-script eval sources:
  - [ ] `/scout` is run and a new `docs/scout/scout-*.md` expedition is created and linked from `docs/scout.md`
  - [ ] the scout compares at least four concrete candidates drawn from public OCR challenges, datasets, benchmark suites, transcription projects, or OCR libraries with reusable eval corpora
  - [ ] each candidate is reviewed against primary-source documentation for license/access, degradation fit, ground-truth quality, and whether it is honestly reusable in this repo
- [ ] The story translates the scout into a local eval decision instead of stopping at desk research:
  - [ ] at least one top candidate is classified as one of: `comparison-only external benchmark`, `repo-owned fixture acquisition candidate`, `local benchmark harness candidate`, or `not usable`
  - [ ] the work log names the exact next local action for the best candidate(s): new story, eval-registry update, fixture-import plan, or explicit rejection
  - [ ] if no candidate is honestly reusable, the story records that negative result explicitly instead of leaving vague “interesting” notes
- [ ] Canonical repo surfaces reflect the sourcing outcome honestly:
  - [ ] `docs/scout.md` is updated with the new expedition row
  - [ ] if a durable local eval or benchmark lane is warranted, the owning follow-up story or `docs/evals/registry.yaml` entry is created/updated in the same pass
  - [ ] the handwritten truth surfaces remain bounded unless this story actually lands a new local eval/fixture substrate

## Out of Scope

- Fixing the maintained handwritten OCR runtime in the same story
- Importing or checking in large third-party corpora without first deciding that the source is legally and operationally usable
- Changing the `handwritten-notes` coverage row to `passing`
- Broad legal review beyond recording the visible license/access posture and concrete repo-usage constraints
- Re-benchmarking the same GLM-OCR or current maintained OCR surfaces without a new source/eval substrate

## Approach Evaluation

- **Simplification baseline**: before inventing more synthetic fixtures or another same-surface OCR challenger, check whether strong public degraded-handwriting / historical-script eval sources already exist and can be reused honestly. If they do, that is simpler and more informative than guessing at harder local synthetic probes.
- **AI-only**: not sufficient by itself. A model can help enumerate candidate sources, but the story still needs primary-source verification for license, access, benchmark scope, and truth-surface quality.
- **Hybrid**: likely best. Use a scout-first research pass to verify external sources, then map the usable ones onto the repo’s existing handwritten eval harness and fixture truth surfaces.
- **Pure code**: only appropriate if the scout result earns a thin local metadata or harness update. The first pass is primarily research and packaging.
- **Repo constraints / prior decisions**: Story 191 is explicitly blocked on missing OCR capability for real historical handwriting. Story 208 proved one stronger OCR challenger was not enough to reopen that line. Scout 011 already surveyed OCR systems, but not degraded-handwriting / old-script eval corpora. `docs/evals/README.md` and `docs/evals/registry.yaml` already define the durable eval surface, and the `handwritten-notes` coverage row remains `has-fixture` with explicit known gaps for degraded and broader real-world handwriting.
- **Existing patterns to reuse**: `/scout`, `docs/scout.md`, `docs/scout/scout-011-external-document-ingestion-systems.md`, `benchmarks/scripts/run_handwritten_notes_eval.py`, `benchmarks/scorers/handwritten_notes_transcription.py`, Story 191’s blocker record, and Story 208’s bounded challenger-comparison discipline.
- **Eval**: the deciding evidence is not an OCR score yet; it is whether the scout produces one or more concrete external sources that can honestly feed local degraded-handwriting / historical-script evaluation. Success means the repo leaves the story with a named next benchmark/fixture action, not just a list of links.

## Tasks

- [ ] Run `/scout` on public degraded-handwriting and historical-script eval sources:
  - [ ] create a new scout expedition under `docs/scout/`
  - [ ] target public OCR challenges, benchmark suites, datasets, transcription projects, and OCR libraries only insofar as they expose reusable degraded-handwriting / old-script evaluation surfaces
  - [ ] verify candidate claims from primary sources rather than secondary hype or stale leaderboard summaries
- [ ] Compare the candidates against local repo needs:
  - [ ] degradation fit: degraded handwriting, historical script, archival scans, messy cursive, or similar hard surfaces
  - [ ] truth-surface quality: transcript availability, page/image pairing, benchmark rubric, and inspectability
  - [ ] repo usability: license/access posture, size, reproducibility, and whether the source can be comparison-only, fixture-backed, or neither
- [ ] Decide the exact local next move for the strongest candidate(s):
  - [ ] create or update the owning follow-up story if a fixture-import, benchmark harness, or comparison-only eval path is warranted
  - [ ] update `docs/evals/registry.yaml` only if this story lands a durable local eval surface or backlog entry there
  - [ ] explicitly reject unusable candidates with reasons instead of leaving them half-open
- [ ] If this story changes documented format coverage or graduation reality: update `tests/fixtures/formats/_coverage-matrix.json` and any relevant methodology state honestly
- [ ] Check whether the chosen implementation makes any existing scout notes, handwritten blocker wording, or eval-planning docs redundant; remove them or create a concrete follow-up
- [ ] Run required checks for touched scope:
  - [ ] Default Python checks: `make test`
  - [ ] Default Python lint: `make lint`
  - [ ] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [ ] If agent tooling changed: `make skills-check`
- [ ] If evals or goldens changed: run `/improve-eval` and update `docs/evals/registry.yaml`
- [ ] Search all docs and update any related to what we touched
- [ ] Verify Central Tenets:
  - [ ] T0 — Traceability: the scout and any follow-up decision cite exact sources, licenses, and candidate local artifact paths
  - [ ] T1 — AI-First: prefer strong external eval evidence over building deterministic local heuristics first
  - [ ] T2 — Eval Before Build: source/eval discovery happens before any new handwritten runtime work
  - [ ] T3 — Fidelity: candidate sources are judged on transcript/truth quality, not just marketing claims
  - [ ] T4 — Modular: keep the result as a bounded scout/eval-source line, not a broad runtime rewrite
  - [ ] T5 — Inspect Artifacts: if the story lands any benchmark or fixture acquisition step, inspect real source artifacts rather than just metadata

## Workflow Gates

- [ ] Build complete: implementation finished, required checks run, and summary shared
- [ ] Validation complete or explicitly skipped by user
- [ ] Story marked done via `/mark-story-done`

## Blocker Summary

N/A

## Blocker Evidence

N/A

## Unblock Condition

N/A

## Architectural Fit

- **Owning module / area**: the scout/eval-planning surface around handwritten OCR, primarily `docs/scout/`, `docs/scout.md`, the handwritten eval registry entry, and any resulting follow-up story packaging.
- **Methodology reality**: this work belongs to `spec:2` and `spec:8`. In `docs/methodology/state.yaml`, both category substrates already exist; `C1` remains in `climb`, `B1` remains in `hold`, and the directly relevant coverage row is `handwritten-notes`, which is still `has-fixture` with explicit gaps for degraded and broader real-world handwriting.
- **Substrate evidence**: verified in this pass that `/scout` exists as a first-class workflow (`.agents/skills/scout/SKILL.md`), `docs/scout.md` already tracks expeditions, `docs/evals/registry.yaml` already owns the durable handwritten eval surface (`handwritten-notes-transcription`), and the existing handwritten benchmark harness lives in `benchmarks/scripts/run_handwritten_notes_eval.py` plus `benchmarks/scorers/handwritten_notes_transcription.py`. Story 191’s blocker record and Story 208’s negative challenger evidence prove why a source-scouting line is distinct and actionable now.
- **Data contracts / schemas**: no schema change is expected for the scout pass. If the story graduates into a local benchmark harness or fixture import, that follow-up should own any schema/artifact additions explicitly.
- **File sizes**: `docs/scout.md` is 19 lines, `docs/evals/registry.yaml` is 2084 lines, `benchmarks/scripts/run_handwritten_notes_eval.py` is 330 lines, `benchmarks/scorers/handwritten_notes_transcription.py` is 119 lines, `tests/fixtures/formats/_coverage-matrix.json` is 564 lines, and this story file starts at 127 lines. Keep `docs/evals/registry.yaml` and the coverage matrix surgical because they are already large truth surfaces.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/scout.md`, Scout 011, Story 191, Story 208, `docs/evals/README.md`, `docs/evals/registry.yaml`, and `tests/fixtures/formats/_coverage-matrix.json`. No narrower local ADR, runbook, or prior scout was found for degraded historical-handwriting eval-source discovery, so a new story is honest.

## Files to Modify

- `docs/stories/story-211-scout-degraded-handwriting-and-historical-script-eval-sources.md` — keep the story record, plan, and close-out truth current (new file)
- `docs/scout.md` — add the new scout expedition row (19 lines)
- `docs/scout/scout-0xx-*.md` — new scout expedition capturing findings, source comparisons, and approved next move (new file)
- `docs/evals/registry.yaml` — only if the scout lands a durable new eval-source backlog line or local benchmark entry (2084 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — only if a shipped local eval/fixture substrate changes the documented handwritten reality (564 lines)
- `benchmarks/scripts/run_handwritten_notes_eval.py` — only if the chosen next move extends the existing handwritten harness in the same story (330 lines)
- `benchmarks/scorers/handwritten_notes_transcription.py` — only if the chosen next move needs scorer-side source metadata or richer reporting (119 lines)

## Redundancy / Removal Targets

- Any stale “next OCR challenger” notes that survive after the scout identifies a more honest eval-source path
- Any duplicate handwriting-eval planning notes outside the new scout expedition and the owning story/work log

## Notes

- New story justification: Story 191 is the blocked runtime line, and Story 208 is one completed challenger-comparison line. This new work has a different success surface: source discovery and eval-substrate expansion for degraded handwriting and historical script. Reopening either older story would blur the difference between “OCR runtime attempt” and “find better pressure surfaces to measure against.”
- The honest outcome may still be negative. If no external source is truly reusable, this story should say so explicitly and stop instead of minting a fake local benchmark plan.
- Prefer sources that can be reused with inspectable provenance and transcript quality over leaderboard prestige.

## Plan

1. Start with `/scout`, not implementation.
   - Build one current expedition focused on public degraded-handwriting, archival-script, and old-script eval sources so the repo stops guessing from memory or hype.
2. Classify the candidates against local eval needs.
   - Decide whether each source is comparison-only, fixture-import-worthy, benchmark-harness-worthy, or unusable in this repo.
3. End with one concrete local next move.
   - The story is only successful if it yields an exact next story/eval action or an explicit negative sourcing result.

## Work Log

20260410-2359 — story created after Story 210 close-out prep and a fresh review of the blocked handwritten line. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/scout.md`, `docs/scout/scout-011-external-document-ingestion-systems.md`, `docs/evals/README.md`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, Story 191, and Story 208. Result: a new story is honest instead of reopening Story 191 or Story 208 because the missing work is no longer “try one more OCR runtime” but “find better degraded-handwriting / historical-script eval sources that can feed our own measurement surface.” The story starts `Pending`, not `Draft`, because the scout workflow, handwritten eval registry, and existing benchmark harness all exist today; the missing slice is the actual source-discovery and packaging decision. Next step: `/build-story` should begin with `/scout`, compare candidate sources against repo use constraints, and end with one concrete local eval/fixture action or an explicit negative result.
