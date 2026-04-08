---
title: "Clean Up Legacy Active Story Drift and Refresh Audit Memory"
status: "Done"
priority: "High"
ideal_refs:
  - "The Execution Ideal"
  - "Transparency over magic."
spec_refs:
  - "spec:8"
  - "spec:9"
adr_refs: []
depends_on:
  - "190"
category_refs:
  - "spec:8"
  - "spec:9"
compromise_refs:
  - "B7"
  - "B8"
input_coverage_refs: []
architecture_domains:
  - "methodology_tooling"
roadmap_tags:
  - "campaign:methodology-workflow-repair"
legacy_system: ""
---

# Story 195 — Clean Up Legacy Active Story Drift and Refresh Audit Memory

**Priority**: High
**Status**: Done
**Decision Refs**: `AGENTS.md`, `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/stories.md`, `docs/runbooks/migrate-problem-first-triage-and-story-workflow.md`, `docs/stories/story-190-fix-story-progression-and-anti-fragmentation-workflow.md`, `docs/stories/story-193-widen-xlsx-proof-and-recheck-pptx-runtime-seam.md`, `docs/stories/story-194-office-intake-recommendation-and-handoff-boundary.md`, and `None found after search in docs/decisions/ for a repo-local ADR that already resolves legacy-story quarantine or architecture-audit memory refresh`
**Depends On**: Story 190

## Goal

Clean the methodology truth surfaces after Story 190 by auditing the ten uncategorized legacy stories that still sit in non-done states and by refreshing stale architecture-audit memory for the recent office intake/runtime line. The outcome should be one honest planning surface: legacy FF/gamebook residue no longer competes with the maintained `doc-web` mission as if it were current active work, and `docs/methodology/state.yaml`, `docs/methodology/graph.json`, and `docs/stories.md` all reflect the real current queue and recent audit context.

## Acceptance Criteria

- [x] The current uncategorized non-done set is audited from actual repo evidence: Stories `015`, `018`, `021`, `023`, `028`, `058`, `077`, `099`, `104`, and `136` are each reviewed in their story file plus current mission context, and the work log records one honest disposition for each story.
- [x] Any story moved to `Done` in this cleanup is backed by current-pass evidence from the repo state we inspected now (story logs alone are not enough); if that fresh evidence is missing, the story is reclassified another honest way (`Obsolete`, `Won't Do`, or explicit open status with rationale) instead of being mechanically closed.
- [x] Any uncategorized legacy story that remains non-done after the cleanup carries explicit current-mission rationale and honest metadata; otherwise it leaves the active status set through a status/category update that the generated graph and index reflect after `make methodology-compile`.
- [x] `docs/stories.md` and `docs/methodology/graph.json` no longer imply stale default-queue work from legacy uncategorized `In Progress` / `To Do` residue; the active line after regeneration is centered on the maintained intake/runtime mission plus any explicitly justified exceptions.
- [x] `docs/methodology/state.yaml` architecture-audit memory is refreshed for the domains touched by recent work, including the office intake/runtime line proved by Stories `193` and `194`, and the story records whether further architecture action is actually due or whether a no-op refresh is the honest answer.
- [x] Fresh methodology validation passes for the touched scope:
  - [x] `make methodology-compile`
  - [x] `make methodology-check`
  - [x] Compiler logic stayed unchanged, so targeted `tests/test_methodology_graph.py` / `ruff` reruns were not required.

## Out of Scope

- Reopening the blocked handwritten OCR line in Story `191` without new unblock evidence
- Implementing any product/runtime work from the legacy FF/gamebook stories being reclassified
- Changing ADR-002 or ADR-003, or reopening the accepted `doc-web` runtime boundary
- Bulk rewriting every historical legacy story; this story only cleans the residual non-done drift and the stale audit-memory surfaces it affects

## Approach Evaluation

- **Simplification baseline**: this is primarily a repo-truth audit. A single bounded LLM pass over the ten story files may already be enough to classify which ones are stale versus still honest, so the first implementation step should measure whether metadata-only cleanup solves the problem before changing compiler behavior.
- **AI-only**: insufficient as the full solution. A model can recommend statuses, but the repo still needs deterministic story metadata, state, and generated-surface updates so future triage sees the same truth.
- **Hybrid**: likely winner. Use AI judgment to audit legacy story honesty against the current mission, then land deterministic metadata/state changes and regenerate the methodology artifacts. Add compiler/test guardrails only if the drift could otherwise recur silently.
- **Pure code**: only appropriate if metadata cleanup alone leaves the generated surfaces ambiguous or if the repo needs a regression test around uncategorized active legacy residue.
- **Repo constraints / prior decisions**: `docs/stories.md` already says historical FF/gamebook stories are not the default mission queue. Story `190` settled the problem-first, anti-fragmentation workflow policy, so this story should clean residual repo truth rather than invent new workflow semantics. `spec:8` and `spec:9` substrates exist, and `B7` / `B8` are both in `hold`, which favors simplification over new process.
- **Existing patterns to reuse**: Story `188` for story-metadata cleanup discipline, Story `190` for workflow-policy intent, `scripts/methodology_graph.py` plus `tests/test_methodology_graph.py` for generated-surface truth, and the `architecture_audits` structure in `docs/methodology/state.yaml`.
- **Eval**: success is determined by repo truth, not promptfoo. The deciding evidence is the audited story set, refreshed audit-memory fields, a regenerated `docs/stories.md` / `docs/methodology/graph.json`, and passing methodology checks. If compiler behavior changes, targeted graph tests are the regression surface.

## Tasks

- [x] Audit the ten uncategorized non-done stories (`015`, `018`, `021`, `023`, `028`, `058`, `077`, `099`, `104`, `136`) against their actual story files, current mission, and adjacent completed work; record one honest disposition for each.
- [x] For every story that looks “probably done,” inspect current code/tests/artifacts in this pass before using `Done`; use the archived hand-authored index only as secondary evidence, not as sufficient proof by itself.
- [x] Update story metadata for the audited set so stale legacy stories no longer present as active default-queue work unless the story now has explicit current-mission rationale and category ownership.
- [x] Refresh `docs/methodology/state.yaml` architecture-audit memory so the recent office intake/runtime line is represented honestly and stale `recent_story_refs` / `stories_since_audit` values no longer lag the April 4-7 work.
- [x] Metadata-only cleanup proved sufficient; no methodology compiler/test guardrail change was needed.
- [x] N/A by design: this story did not change format coverage or graduation reality, so `tests/fixtures/formats/_coverage-matrix.json` stayed untouched.
- [x] Check whether the chosen cleanup makes any stale legacy status wording, audit notes, or generated-index framing redundant; remove it or create a concrete follow-up.
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] `make methodology-compile`
  - [x] `make methodology-check`
  - [x] Compiler logic unchanged, so `python -m pytest tests/test_methodology_graph.py -q` was not required.
  - [x] Compiler logic unchanged, so `python -m ruff check scripts/methodology_graph.py tests/test_methodology_graph.py` was not required.
  - [x] Agent tooling and instructions were unchanged, so `make skills-check` was not required.
- [x] Evals and goldens stayed untouched, so `/improve-eval` and `docs/evals/registry.yaml` updates were not required.
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every story-state or audit-memory change is backed by cited local story/state/index evidence
  - [x] T1 — AI-First: use AI judgment for bounded classification work instead of preserving manual backlog ceremony
  - [x] T2 — Eval Before Build: audit the current repo truth before adding compiler or process logic
  - [x] T3 — Fidelity: preserve the real current mission and do not silently keep stale legacy work looking active
  - [x] T4 — Modular: keep story metadata, methodology state, compiler output, and index wording aligned instead of scattering separate truths
  - [x] T5 — Inspect Artifacts: manually inspect the regenerated story index and graph output, not just command success

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

- **Owning module / area**: methodology tooling and planning truth surfaces under `docs/stories/`, `docs/methodology/state.yaml`, `scripts/methodology_graph.py`, and the generated `docs/stories.md` / `docs/methodology/graph.json`.
- **Methodology reality**: this belongs to `spec:8` and `spec:9`. Both category substrates exist in `docs/methodology/state.yaml`, and the relevant execution compromises `B7` and `B8` are in `hold`, making simplification and stale-truth cleanup the right next move. No coverage-matrix rows are directly in scope.
- **Substrate evidence**: the current compiled graph and generated index already expose the residue this story needs to clean. `docs/stories.md` still shows ten uncategorized non-done legacy stories, while `docs/methodology/state.yaml` still records pre-April office `recent_story_refs` for `intake_and_routing` and `doc_web_runtime`. Story `190` and its migration runbook already provide the governing workflow policy; the missing piece is repo-truth cleanup on top of that policy.
- **Data contracts / schemas**: no pipeline schema change is expected. If the methodology compiler gains a new regression guard or output rule, keep `scripts/methodology_graph.py` and `tests/test_methodology_graph.py` aligned so the generated story/index contract remains explicit and testable.
- **File sizes**: likely touched files are `docs/methodology/state.yaml` (142 lines), `docs/stories.md` (240 lines, generated), `scripts/methodology_graph.py` (764 lines, already above 500), `tests/test_methodology_graph.py` (243 lines), and the ten audited story files: `story-015` (125), `story-018` (94), `story-021` (66), `story-023` (77), `story-028` (57), `story-058` (474), `story-077` (443), `story-099` (46), `story-104` (200), `story-136` (98).
- **Decision context**: reviewed `AGENTS.md`, `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/stories.md`, `docs/runbooks/migrate-problem-first-triage-and-story-workflow.md`, Story `190`, Story `193`, and Story `194`. No narrower ADR exists in `docs/decisions/` for this specific cleanup because this is residual methodology truth maintenance, not a new architecture decision.

## Files to Modify

- `docs/methodology/state.yaml` — refresh stale architecture-audit memory and notes for the domains touched by recent work (142 lines)
- `docs/stories/story-015-modular-pipeline.md` — reclassify or annotate if this legacy shell is no longer honest current work (125 lines)
- `docs/stories/story-018-enrichment-alt-mods.md` — reclassify or annotate if this legacy shell is no longer honest current work (94 lines)
- `docs/stories/story-021-dashboard-ui-polish.md` — resolve stale `In Progress` status or add explicit current-mission rationale (66 lines)
- `docs/stories/story-023-section-target-guard.md` — reclassify or annotate if this legacy shell is no longer honest current work (77 lines)
- `docs/stories/story-028-market-discovery.md` — resolve stale `In Progress` status or add explicit current-mission rationale (57 lines)
- `docs/stories/story-058-post-ocr-text-quality.md` — resolve stale `In Progress` status or add explicit current-mission rationale (474 lines)
- `docs/stories/story-077-ai-ocr-simplification.md` — reclassify or annotate if this legacy shell is no longer honest current work (443 lines)
- `docs/stories/story-099-remove-dev-backcompat-note.md` — reclassify or annotate if this legacy shell is no longer honest current work (46 lines)
- `docs/stories/story-104-gamebook-output-tweaks.md` — resolve stale `In Progress` status or add explicit current-mission rationale (200 lines)
- `docs/stories/story-136-pipeline-stage-parallelism.md` — reclassify or annotate if this draft shell is no longer honest current work (98 lines)
- `docs/stories.md` — generated story index should reflect the cleaned story truth after compilation (240 lines)
- `scripts/methodology_graph.py` — only if a small guardrail is needed around uncategorized active legacy residue (764 lines)
- `tests/test_methodology_graph.py` — add or adjust regression coverage if compiler behavior changes (243 lines)

## Redundancy / Removal Targets

- Stale uncategorized `In Progress` / `To Do` statuses that keep legacy FF/gamebook work looking active by accident
- Stale `architecture_audits` `recent_story_refs`, `stories_since_audit`, or notes that still stop at pre-April office-line work
- Any generated-index phrasing or compiler allowance that lets residual legacy active drift survive invisibly after the cleanup

## Notes

- New story justification: this is not a reopen of Story `190`. Story `190` fixed the workflow contract and blocked-line behavior; this story cleans the residual repo truth that still predates those rules. The subsystem is the same, but the success surface is different: repository-state cleanup and audit-memory refresh rather than workflow-policy design.
- The likely honest outcome is that most or all ten audited stories leave the active default queue. If one survives as current work, the story must explain why it still belongs in the maintained mission instead of relying on legacy inertia.

## Plan

### Exploration Summary

- **Ideal alignment:** proceed. This story removes planning drag and stale queue noise, which moves the repo toward the Execution Ideal and the vision-level preference for transparency rather than away from it. It optimizes `B7` / `B8`, but it does so by deleting misleading process residue rather than adding new process.
- **Methodology state:** `spec:8` and `spec:9` both have substrate `exists` in `docs/methodology/state.yaml`; `B7` and `B8` are both `hold`. No coverage-matrix rows are directly involved.
- **Baseline eval surface:** current methodology truth, not promptfoo. Fresh baseline in this pass:
  - `build_graph()` currently reports `validation_errors = []` and `validation_warnings = []`
  - the graph still contains `10` uncategorized non-done stories: `015`, `018`, `021`, `023`, `028`, `058`, `077`, `099`, `104`, `136`
  - archived hand-authored index evidence shows a split:
    - likely pure status drift: `015`, `018`, `023`, `058`, `077` were already recorded as `Done` there
    - still-open historical statuses: `021`, `028`, `104`, `099`, `136`
  - `architecture_audits` memory is stale relative to recent office work: `intake_and_routing` still ends at `176/178/180`, and `doc_web_runtime` still ends at `173/174/175`, even though Stories `193` and `194` are the latest relevant office-line proofs
- **Critical substrate verified versus missing:**
  - verified: story metadata compilation, uncategorized grouping, status ordering, and audit-memory consumption all exist today in `scripts/methodology_graph.py`
  - verified: current repo substrate still supports likely historical-completion candidates such as the module-driver path (`driver.py`, `validate_artifact.py`), `section_target_guard_v1`, the dashboard highlighting code in `docs/pipeline-visibility.html`, and successor/defer stories like `081` and `107`
  - missing: there is no current validation guard that treats uncategorized active legacy residue as suspicious, which is why the misleading queue currently passes clean checks
- **Patterns to follow:** prefer metadata/state cleanup first, then regenerate and inspect `docs/stories.md` / `docs/methodology/graph.json`; only touch compiler/test logic if the generated surfaces still make stale residue easy to miss.
- **Scope delta folded in:** any story moved to `Done` must be backed by current-pass repo evidence, not only by historical work logs or the archived hand-authored index. If that evidence is not cheap or not honest to establish, use `Obsolete` / `Won't Do` / explicit rationale instead of mechanically closing it.

### Implementation Order

1. **Audit and classify the ten-story residue** (`M`)
   - Files: the ten story files plus `docs/archive/stories-index-hand-authored-2026-04-04.md`
   - What changes:
     - split the set into `pure stale-status drift`, `historical but superseded`, and `still-open with explicit rationale`
     - use current repo evidence to determine whether a story can honestly become `Done` now or should become `Obsolete` / `Won't Do`
   - Provisional recommendations from exploration:
     - likely `Done` after current-pass verification: `015`, `023`, `058`, `077`, and probably `104`
     - likely `Done` or `Obsolete` depending on current substrate check: `018`, `021`
     - likely `Obsolete` / `Won't Do` unless a strong current-mission rationale is found: `028`, `099`, `136`
   - Done when: every one of the ten stories has a written, evidence-backed disposition and no “just left open because it was already open” cases remain.

2. **Apply metadata cleanup to the audited stories** (`M`)
   - Files: the ten story files
   - What changes:
     - update frontmatter `status`
     - add brief work-log notes where the story needs an explicit cleanup rationale
     - add category refs only if a story truly still belongs to the maintained mission
   - Risk:
     - the biggest honesty risk is turning a story into `Done` without fresh evidence
     - second risk is keeping a legacy story open without explaining why it still belongs in the active mission
   - Done when: the story files themselves, not just the generated index, tell the honest current state.

3. **Refresh architecture-audit memory** (`S`)
   - Files: `docs/methodology/state.yaml`
   - What changes:
     - update `recent_story_refs`, `stories_since_audit`, and notes for `intake_and_routing` and `doc_web_runtime`
     - decide whether `methodology_tooling` also needs a note refresh now that Story `195` exists
   - Expected outcome:
     - likely a no-op architecture decision with fresher memory, not a new cleanup story
   - Done when: the audit-memory lane names the April office work honestly and no longer lags the repo by two stories.

4. **Recompile and inspect generated surfaces** (`S`)
   - Files: generated `docs/stories.md`, generated `docs/methodology/graph.json`
   - What changes:
     - rerun `make methodology-compile`
     - inspect whether the legacy uncategorized active bucket is now honest and small enough
   - Done when: the generated index no longer presents stale active legacy work as the de facto queue.

5. **Add the smallest guardrail only if cleanup alone is insufficient** (`S`, conditional)
   - Files: `scripts/methodology_graph.py`, `tests/test_methodology_graph.py`
   - What changes:
     - only if needed, add a narrow warning or test around uncategorized active legacy residue
   - Human-approval blocker:
     - none for metadata-only cleanup
     - if the compiler rule starts enforcing a new policy rather than surfacing drift, call that out before landing
   - Done when: either no compiler change is necessary, or the smallest change is covered by a targeted regression test.

### Structural Health Notes

- `scripts/methodology_graph.py` is already 764 lines, so prefer not to touch it unless the regenerated surfaces remain ambiguous after metadata cleanup.
- `docs/methodology/state.yaml` is small and low-risk; it is the right place for the audit-memory refresh.
- Most likely work is story-frontmatter/status cleanup plus generated-surface inspection. That is coherent and buildable now with no schema or runtime prerequisite.

## Work Log

20260407-2304 — create-story: created Story 195 after `/triage` identified the highest-leverage open problem as planning-surface honesty rather than a new product feature. Evidence reviewed in the same pass: `docs/stories.md` still lists ten uncategorized non-done legacy stories (`015`, `018`, `021`, `023`, `028`, `058`, `077`, `099`, `104`, `136`), `docs/methodology/state.yaml` still records pre-April office-line `recent_story_refs` for `intake_and_routing` and `doc_web_runtime`, Story `190` already settled the anti-fragmentation workflow contract, and Stories `193` / `194` closed the recent office line without refreshing that methodology memory. Result: a new `Pending` story is honest because the remaining work is a bounded repo-truth cleanup with verified substrate, not a reopen of the Story 190 policy design. Next step: `/build-story` should audit the ten stories, choose the smallest honest metadata/compiler cleanup, and recompile the methodology surfaces.
20260407-2320 — `/build-story` exploration and planning baseline completed with no implementation changes. Ideal-alignment result: proceed. Context reviewed in this pass: `docs/ideal.md`; `docs/spec.md` (`spec:8`, `spec:9`); `docs/methodology/state.yaml`; `docs/methodology/graph.json`; `docs/stories.md`; Story `190`; Story `193`; Story `194`; `docs/runbooks/migrate-problem-first-triage-and-story-workflow.md`; `scripts/methodology_graph.py`; `tests/test_methodology_graph.py`; the ten audited story files; and `docs/archive/stories-index-hand-authored-2026-04-04.md` as secondary status evidence. Fresh baseline evidence: `build_graph()` currently reports `validation_errors = []` and `validation_warnings = []` even though the graph still carries `10` uncategorized non-done stories (`015`, `018`, `021`, `023`, `028`, `058`, `077`, `099`, `104`, `136`). Current-vs-archive comparison shows two distinct cleanup buckets: pure likely status drift (`015`, `018`, `023`, `058`, `077` are already `Done` in the archived hand-authored index) versus stories still historically open there (`021`, `028`, `104`, `099`, `136`) that need a real present-tense decision rather than a mechanical sync. Critical substrate verified in code: `scripts/methodology_graph.py` already compiles story metadata, uncategorized grouping, and `architecture_audits`; the repo still contains current substrate for likely historical-completion candidates such as `driver.py` + module scanning, `section_target_guard_v1`, the dashboard highlighting code in `docs/pipeline-visibility.html`, and successor/defer stories `081` and `107`. Critical substrate missing: there is no current warning/test for misleading uncategorized active legacy residue, so stale queue truth passes clean checks today. Small scope delta folded into the story: any story moved to `Done` must be backed by current-pass repo evidence, not only by historical work logs or the archived index; otherwise the honest move is `Obsolete`, `Won't Do`, or explicit open-status rationale. Patterns to follow: metadata/state cleanup first, then regenerate and inspect the compiled surfaces; avoid touching `scripts/methodology_graph.py` unless that cleanup still leaves drift too easy to miss. Potential redundancy/removal targets: stale uncategorized active statuses, stale audit-memory refs, and any needlessly permissive compiler assumption that legacy active residue is harmless. Next step: present the plan and disposition recommendations for approval before touching story metadata or methodology state.
20260407-2357 — implementation: moved Story 195 to `In Progress`, reclassified the ten targeted legacy stories, refreshed `architecture_audits` memory in `docs/methodology/state.yaml`, regenerated the methodology surfaces, and validated that metadata-only cleanup was sufficient. Final dispositions landed in this pass: `015 -> Done`, `018 -> Obsolete`, `021 -> Done`, `023 -> Done`, `028 -> Won't Do`, `058 -> Obsolete`, `077 -> Done`, `099 -> Won't Do`, `104 -> Obsolete`, `136 -> Obsolete`. Fresh current-pass evidence backed every `Done` decision (`driver.py` / `validate_artifact.py` / `extract_text_v1` for Story 015; current `docs/pipeline-visibility.html` highlighting/pretty-print wiring for Story 021; `section_target_guard_v1` code + test substrate for Story 023; successor Story 081 marked `Done` for Story 077), while historical stories lacking fresh artifact proof or current mission relevance were retired honestly instead of being mechanically closed (`058` and `104` both cited run artifacts that are not present in the current workspace). Regeneration surfaced one adjacent residue outside the original ten-story list: Story `017` still used the non-canonical status `Complete`, so the graph treated it as active; this pass normalized it to `Done` because its close-out log and current driver/module substrate show it was already closed. Fresh validation in this pass: `make methodology-compile`, `make methodology-check`, `make lint`, and `make test` all passed; `make test` completed with `475 passed` and only existing Pydantic deprecation warnings outside the touched files. Fresh output inspection after regeneration: `docs/stories.md` now shows Story `195` as the active methodology item, the legacy/uncategorized block contains only `Done` / `Obsolete` / `Won't Do` rows for the targeted residue, and `docs/methodology/graph.json` now reports `0` uncategorized non-done stories. Result: no compiler or test guardrail change was needed, because authored metadata cleanup plus the one status normalization removed the misleading queue truth. Next step: hand off to `/validate`, then `/mark-story-done` if the validation pass agrees the story can close.
20260408-0836 — close-out: Story 195 marked `Done` via `/mark-story-done` after fresh validation and changelog audit. Fresh current-pass evidence rechecked during close-out: `make methodology-compile`, `make methodology-check`, `make lint`, and `make test` all passed on the current branch tip; `make test` again finished with `475 passed` and only the pre-existing Pydantic deprecation warnings in `modules/portionize/portionize_headers_numeric_v1/main.py`. Fresh output inspection still shows `docs/stories.md` carrying Story `195` in the active methodology section before this final status flip, the legacy/uncategorized block reduced to `Done` / `Obsolete` / `Won't Do`, and `docs/methodology/graph.json` still reporting `0` uncategorized non-done stories. Close-out fixes applied in the same pass: removed the duplicate unchecked task line from the story checklist and dropped the unrelated autogenerated `.codex` file from the worktree so only intended story files remain. Dependency check remains satisfied because Story `190` is already `Done`. Next step: `/check-in-diff`.
