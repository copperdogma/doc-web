---
title: "Scout Degraded-Handwriting and Historical-Script Eval Sources"
status: "Done"
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
**Status**: Done
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

- [x] A fresh scout expedition exists for external degraded-handwriting / historical-script eval sources:
  - [x] `/scout` is run and a new `docs/scout/scout-*.md` expedition is created and linked from `docs/scout.md`
  - [x] the scout compares at least four concrete candidates drawn from public OCR challenges, datasets, benchmark suites, transcription projects, or OCR libraries with reusable eval corpora
  - [x] each candidate is reviewed against primary-source documentation for license/access, degradation fit, ground-truth quality, and whether it is honestly reusable in this repo
- [x] The story translates the scout into a local eval decision instead of stopping at desk research:
  - [x] at least one top candidate is classified as one of: `comparison-only external benchmark`, `repo-owned fixture acquisition candidate`, `local benchmark harness candidate`, or `not usable`
  - [x] the work log names the exact next local action for the best candidate(s): new story, eval-registry update, fixture-import plan, or explicit rejection
  - [x] if no candidate is honestly reusable, the story records that negative result explicitly instead of leaving vague “interesting” notes
- [x] Canonical repo surfaces reflect the sourcing outcome honestly:
  - [x] `docs/scout.md` is updated with the new expedition row
  - [x] if a durable local eval or benchmark lane is warranted, the owning follow-up story or `docs/evals/registry.yaml` entry is created/updated in the same pass
  - [x] the handwritten truth surfaces remain bounded unless this story actually lands a new local eval/fixture substrate

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

- [x] Run `/scout` on public degraded-handwriting and historical-script eval sources:
  - [x] create a new scout expedition under `docs/scout/`
  - [x] target public OCR challenges, benchmark suites, datasets, transcription projects, and OCR libraries only insofar as they expose reusable degraded-handwriting / old-script evaluation surfaces
  - [x] verify candidate claims from primary sources rather than secondary hype or stale leaderboard summaries
- [x] Compare the candidates against local repo needs:
  - [x] degradation fit: degraded handwriting, historical script, archival scans, messy cursive, or similar hard surfaces
  - [x] truth-surface quality: transcript availability, page/image pairing, benchmark rubric, and inspectability
  - [x] repo usability: license/access posture, size, reproducibility, and whether the source can be comparison-only, fixture-backed, or neither
- [x] Decide the exact local next move for the strongest candidate(s):
  - [x] create or update the owning follow-up story if a fixture-import, benchmark harness, or comparison-only eval path is warranted
  - [x] update `docs/evals/registry.yaml` only if this story lands a durable local eval surface or backlog entry there
  - [x] explicitly reject unusable candidates with reasons instead of leaving them half-open
- [x] If this story changes documented format coverage or graduation reality: handwritten truth surfaces stayed bounded, so no coverage-matrix or methodology-state truth change was warranted in this pass
- [x] Check whether the chosen implementation makes any existing scout notes, handwritten blocker wording, or eval-planning docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: not applicable, this was a docs/scout/story pass only
  - [x] If agent tooling changed: not applicable, `make skills-check` was not needed
- [x] If evals or goldens changed: not applicable, no eval or golden surface changed in this story
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: the scout and follow-up story cite exact source URLs, licenses, and local artifact paths
  - [x] T1 — AI-First: the story prefers stronger external eval evidence over new deterministic handwriting logic
  - [x] T2 — Eval Before Build: source/eval discovery happened before any new handwritten runtime work
  - [x] T3 — Fidelity: candidate sources were judged on transcript/truth quality, not just marketing claims
  - [x] T4 — Modular: the result stays a bounded scout/eval-source line plus one follow-up story, not a runtime rewrite
  - [x] T5 — Inspect Artifacts: this pass inspected source metadata and local methodology artifacts; no new OCR artifacts were claimed

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

1. Bootstrap one bounded scout expedition first.
   - Files: `docs/scout.md`, new `docs/scout/scout-014-degraded-handwriting-eval-sources.md`, and this story file.
   - Work: run `.agents/skills/scout/scripts/start-scouting.sh degraded-handwriting-eval-sources`, set the expedition scope to public degraded-handwriting / historical-script eval sources, and keep the pass research-only except for the packaging artifacts this story explicitly owns.
   - Impact: no runtime or schema behavior changes; the only immediate graph-impacting files are the scout index/expedition and Story 211.
   - Done looks like: a tracked scout artifact exists with the candidate list, source links, and an explicit status instead of loose notes in a work log.

2. Compare a concrete candidate set against the repo's blocked handwritten gap.
   - Files: the new scout expedition, this story file, and optionally `docs/evals/registry.yaml` only if a durable eval/backlog entry is truly warranted.
   - Candidate set for the first pass:
     - `DiEm HTR` (Danish National Archives historical parish-register ground truth on Hugging Face)
     - `Digital Peter` (historical Peter the Great manuscripts on Hugging Face / GitHub)
     - `Saint Gall Database` (IAM-HistDB historical Latin manuscript corpus)
     - `Washington Database` (IAM-HistDB George Washington longhand corpus)
     - `HTR-United` catalog as a meta-source / harness candidate for further acquisition rather than as a final benchmark by itself
   - Work: verify each candidate from primary-source docs for license/access posture, degradation fit, transcript/granularity quality, reproducibility, and whether it can honestly map to one of the story's allowed outcomes (`comparison-only external benchmark`, `repo-owned fixture acquisition candidate`, `local benchmark harness candidate`, or `not usable`).
   - Impact: this is the eval-first gate for the handwritten line. The pass should make Story 191 more informed without reopening it.
   - Structural health note: avoid turning this into a broad corpus survey. If one or two sources are clearly stronger than the rest, prefer a narrow ranking plus explicit rejections over a long catalog.
   - Done looks like: at least four concrete candidates are compared on the same rubric and the scout names why each is or is not honestly reusable here.

3. Translate the scout into one exact local next move.
   - Files: this story file; the scout expedition; `docs/scout.md`; and, only if justified by the evidence, one new follow-up story or a surgical `docs/evals/registry.yaml` update.
   - Work: choose the single strongest next action from the scouting evidence:
     - create a follow-up story for fixture acquisition
     - create a follow-up story for a comparison-only external benchmark harness
     - add a durable eval-planning entry to `docs/evals/registry.yaml`
     - or record an explicit negative sourcing result if no candidate is good enough
   - Impact: keeps the handwritten truth surface honest without widening `handwritten-notes` support prematurely.
   - Human-approval blocker: if the best source requires checking in a large third-party corpus, do not import it in this story; package that as the follow-up instead.
   - Done looks like: the repo leaves Story 211 with one launchable next action that a future `yes` can execute directly.

4. Verify the packaging and stop.
   - Files: any docs touched above.
   - Work: run the narrowest honest checks for a docs/story/scout-only pass (`make lint`, `make test`, and methodology refresh/checks if story or scout index changes affect generated views), then re-read the updated scout artifact and story close-out.
   - Impact: generated methodology surfaces stay current if story status or linked artifacts changed.
   - Done looks like: the story remains `In Progress` with `Build complete` checked, validation evidence named, and `/validate` as the next recommended step.

### Scope Adjustment From Exploration

- **Folded in automatically**: treat `HTR-United` as a sourcing/harness candidate rather than forcing every candidate to be a direct downloadable benchmark. That keeps the pass honest about how historical-HTR corpora are actually discovered and licensed.
- **Not recommended**: adding new handwritten runtime experiments, new synthetic fixtures, or another same-surface model bake-off inside Story 211. Story 191 and Story 208 already cover that lane and currently say "wait for a new substrate or better benchmark surface."
- **Approval-sensitive expansion**: if the best candidate implies immediate acquisition of a non-trivial external corpus or a new benchmark script, stop at the follow-up story/eval packaging in this pass and do not silently absorb that implementation work here.

## Work Log

20260410-2359 — story created after Story 210 close-out prep and a fresh review of the blocked handwritten line. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/scout.md`, `docs/scout/scout-011-external-document-ingestion-systems.md`, `docs/evals/README.md`, `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`, Story 191, and Story 208. Result: a new story is honest instead of reopening Story 191 or Story 208 because the missing work is no longer “try one more OCR runtime” but “find better degraded-handwriting / historical-script eval sources that can feed our own measurement surface.” The story starts `Pending`, not `Draft`, because the scout workflow, handwritten eval registry, and existing benchmark harness all exist today; the missing slice is the actual source-discovery and packaging decision. Next step: `/build-story` should begin with `/scout`, compare candidate sources against repo use constraints, and end with one concrete local eval/fixture action or an explicit negative result.
20260411-0107 — /build-story exploration + plan: re-read `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/evals/README.md`, `docs/scout.md`, Scout 011, Story 191, Story 208, and the `handwritten-notes` coverage row before tracing the local scout/eval substrate. Verified local buildability in code and docs: `.agents/skills/scout/SKILL.md` and `.agents/skills/scout/scripts/start-scouting.sh` provide a first-class scout bootstrap path; `docs/scout.md` currently tracks 13 expeditions, so this pass would create `scout-014-*`; `docs/evals/registry.yaml` already owns the durable `handwritten-notes-transcription` surface; and the existing benchmark harness remains at `benchmarks/scripts/run_handwritten_notes_eval.py` plus `benchmarks/scorers/handwritten_notes_transcription.py`. No narrower ADR, runbook, or prior scout was found for degraded historical-handwriting eval-source discovery, so the story remains a coherent `Pending` build candidate rather than an architectural no-op. Fresh source reconnaissance for planning confirmed a concrete candidate set from primary docs: `DiEm HTR` (historical Danish handwriting with CC-BY-4.0, PAGE/XML and ALTO on Hugging Face), `Digital Peter` (historical Peter the Great manuscripts with MIT license and full-page annotations on Hugging Face / GitHub), `Saint Gall Database` (9th-century Latin manuscript pages with exact line-level transcription but non-commercial research-only terms via IAM-HistDB), `Washington Database` (18th-century longhand line/word corpus with non-commercial research-only terms via IAM-HistDB), and `HTR-United` as a FAIR-style catalog/meta-source with explicit PAGE/ALTO + image + license metadata expectations rather than a single benchmark corpus. Critical substrate verified versus missing: the repo already has the workflow and truth surfaces needed to package a sourcing decision, but it does not yet have any broader degraded-handwriting benchmark line beyond the narrow Barney/Alverson pair. Patterns to follow: Scout 011's research-only packaging, Story 208's bounded decision discipline, and the existing scout-template structure. Potential redundant output to avoid: any new “try another OCR model” note that ignores Story 191's blocker and Story 208's negative evidence. Next step: present the concrete plan and candidate set for approval before creating the expedition and writing the scout results.
20260411-0130 — implementation: bootstrapped `docs/scout/scout-014-degraded-handwriting-eval-sources.md`, completed the primary-source scout, updated `docs/scout.md`, and packaged the strongest next move as Story 212. Decision from the finished scout: `DiEm HTR` is the first honest benchmark source because it combines page-level images, PAGE/ALTO transcription structure, and `CC BY 4.0` terms; `Digital Peter` remains the best permissive secondary source; `Washington` and `Saint Gall` stay comparison-only due non-commercial/registration constraints; and `HTR-United` is a sourcing rubric, not a benchmark corpus. Result: Story 211 now has the exact next local move it was supposed to produce, so the remaining work is verification plus close-out, not more source discovery. Next step: rerun generated methodology views and the narrow verification surface, then leave the story `In Progress` with `/validate` as the next move.
20260411-0146 — verification + build handoff: reran `make methodology-compile`, `make methodology-check`, `make lint`, and `make test` after the final scout/story edits. Results: the methodology graph is current, `ruff` passes cleanly, and the full suite passed (`555 passed, 4 warnings in 629.20s`), with the same pre-existing Pydantic deprecation warnings limited to `modules/portionize/portionize_headers_numeric_v1/main.py`. Re-read the finished scout artifact and follow-up story after regeneration to confirm the current handoff surface: `docs/scout/scout-014-degraded-handwriting-eval-sources.md` now records the five-candidate comparison plus explicit DiEm-first recommendation, `docs/scout.md` links the new expedition, and Story 212 exists as the exact next benchmark move. Result: build work is complete and freshly verified; the story remains `In Progress` pending `/validate` and `/mark-story-done`.
20260411-1047 — /mark-story-done closeout: confirmed Story 211 is implementation-complete on the current tip, then checked the validation and completion workflow gates, updated the generated story/methodology views, and prepared the landing set. Fresh close-out evidence remains the same current-pass validation surface from Story 211's handoff: `make methodology-compile`, `make methodology-check`, `make lint`, and `make test` (`555 passed, 4 warnings in 629.20s`). The closed slice is explicit and self-contained: `docs/scout/scout-014-degraded-handwriting-eval-sources.md` records the five-candidate comparison, `docs/scout.md` links the expedition, and Story 212 captures the exact next benchmark move without widening the handwritten support claim. Next step: `/check-in-diff`.
