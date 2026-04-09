---
title: "Refresh Methodology Roadmap Truth and Audit Memory"
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
  - "195"
  - "199"
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
  - "campaign:methodology-graph-state-migration"
legacy_system: ""
---

# Story 204 — Refresh Methodology Roadmap Truth and Audit Memory

**Priority**: High
**Status**: Done
**Decision Refs**: `AGENTS.md`, `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/stories.md`, `docs/evals/registry.yaml`, `docs/runbooks/migrate-problem-first-triage-and-story-workflow.md`, `docs/stories/story-191-finish-real-handwritten-ocr-on-the-loc-fixture-pair.md`, `docs/stories/story-195-legacy-active-story-cleanup-and-audit-memory-refresh.md`, `docs/stories/story-199-methodology-hardening-followup.md`, `docs/stories/story-196-widen-born-digital-pdf-proof-and-quality-surface.md`, `docs/stories/story-197-establish-pptx-direct-entry-seam.md`, `docs/stories/story-200-web-page-direct-entry-seam.md`, `docs/stories/story-201-epub-direct-entry-seam.md`, `docs/stories/story-202-eml-direct-entry-seam.md`, `docs/stories/story-203-mbox-archive-seam.md`, `tests/fixtures/formats/_coverage-matrix.json`, and `None found after search in docs/decisions/ for a narrower roadmap-refresh ADR or audit-memory policy doc`
**Depends On**: Stories `195` and `199`

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

Stories 195 and 199 repaired the methodology workflow and compiler package, but
the authored roadmap state now lags the repo again. `docs/methodology/state.yaml`
still marks `maintained-intake-honesty` and
`methodology-graph-state-migration` as active using only already-finished story
refs, `docs/stories.md` repeats that stale active-focus framing, and the
architecture-audit memory stops short of the latest direct-entry seam work and
the current blocked handwritten line. This story refreshes the methodology
truth surfaces so the active roadmap, campaign continuity, and audit memory
match April 2026 repo reality instead of preserving outdated momentum.

## Acceptance Criteria

- [x] A current-pass roadmap audit is recorded from actual repo evidence:
      `docs/methodology/state.yaml`, generated `docs/stories.md`, generated
      `docs/methodology/graph.json`, `docs/evals/registry.yaml`,
      `tests/fixtures/formats/_coverage-matrix.json`, and the live story set.
      The work log must name the specific stale campaign refs, stale
      architecture-audit refs, and the current live blocked line instead of
      speaking only in generalities.
- [x] `docs/methodology/state.yaml` is updated so `roadmap.active_focus`,
      `roadmap.campaigns`, and `architecture_audits` reflect current repo
      reality after Stories `196`-`203` and blocked Story `191`. No campaign
      may remain `active` if it only points at completed work without an
      explicitly still-open problem line.
- [x] After `make methodology-compile`, generated
      `docs/stories.md` and `docs/methodology/graph.json` surface the refreshed
      roadmap truth and no longer advertise stale active-campaign context or
      outdated recent-story memory.
- [x] Blocked/product truth remains honest after the refresh: Story `191`
      stays blocked unless fresh unblock evidence appears, `handwritten-notes`
      remains `has-fixture`, and `mixed-archive` is not promoted into active
      roadmap work unless current-pass substrate evidence supports that claim.
- [x] If the current compiler/test surface allowed this drift to persist
      silently, the story lands the smallest justified guardrail in
      `scripts/methodology_graph.py` with targeted coverage in
      `tests/test_methodology_graph.py`; if metadata-only cleanup is sufficient,
      no unnecessary compiler change lands.

## Out of Scope

- Reopening Story `191` or running new handwritten OCR experiments without
  fresh unblock evidence
- Creating or building a `mixed-archive` intake/routing lane in this story
- Changing runtime behavior, recipe wiring, coverage claims, or eval results
  beyond the minimum planning-truth correction that current evidence requires
- Broad methodology redesign or a new ADR unless implementation uncovers a
  truly hard-to-reverse planning contract gap
- Reclassifying historical done stories again unless the current roadmap audit
  proves a specific story status is still inconsistent

## Approach Evaluation

- **Simplification baseline**: first test whether a no-code authored-state
  refresh solves the problem. Current evidence suggests most of the drift lives
  in `docs/methodology/state.yaml`, not in missing runtime or compiler
  substrate.
- **AI-only**: insufficient as the full solution. AI can identify the honest
  current planning shape, but the repo still needs deterministic updates to the
  authored state plus regenerated graph/index outputs.
- **Hybrid**: likely winner. Use bounded audit judgment to determine the honest
  current roadmap and architecture-memory state, then land minimal state edits
  and add a tiny compiler/test guardrail only if the audit shows a real silent
  drift vector.
- **Pure code**: possible but low-value by default. Automatically deriving
  campaign truth from recent stories would add policy complexity that Story 190
  and Story 199 deliberately tried to avoid unless the authored-state model has
  proven too fragile.
- **Repo constraints / prior decisions**: Story `190` settled problem-first
  triage and blocked-story honesty, Story `195` cleaned stale legacy active
  residue, and Story `199` hardened the methodology compiler/test boundary.
  `spec:8` and `spec:9` are both execution-compromise categories with `B7` and
  `B8` in `hold`, so the preferred move is simplification and truth refresh,
  not more planning machinery.
- **Existing patterns to reuse**: Story `195` for audit-memory refresh
  discipline, Story `199` for compiler/test hardening scope, the roadmap and
  architecture-audit surfaces in `docs/methodology/state.yaml`, and the current
  render/validation path in `scripts/methodology_graph.py` plus
  `tests/test_methodology_graph.py`.
- **Eval**: the deciding proof surface is methodology compile/check plus manual
  inspection of the regenerated outputs. If compiler logic changes, targeted
  `tests/test_methodology_graph.py` and `ruff` on the touched methodology files
  are the regression surface; no promptfoo eval is warranted.

## Tasks

- [x] Audit the current roadmap truth from `docs/methodology/state.yaml`,
      generated `docs/stories.md`, generated `docs/methodology/graph.json`,
      `docs/evals/registry.yaml`, `tests/fixtures/formats/_coverage-matrix.json`,
      and the live story set; record which campaign, active-focus, and
      architecture-audit fields are stale.
- [x] Decide the honest post-refresh planning shape: which categories still
      belong in `active_focus`, whether the current campaigns should be closed,
      replaced, or retagged, and whether blocked handwriting should remain only
      a health flag instead of active roadmap work.
- [x] Update `docs/methodology/state.yaml` with the minimal honest roadmap and
      `architecture_audits` refresh, then regenerate `docs/stories.md` and
      `docs/methodology/graph.json` via `make methodology-compile`.
- [x] If the current compiler/test surface allows this drift to recur
      silently, add the smallest guardrail in `scripts/methodology_graph.py`
      and `tests/test_methodology_graph.py`; otherwise keep the change
      metadata-only.
- [x] N/A by design: this story should not change documented format coverage or
      graduation reality unless the audit finds one of the methodology truth
      surfaces already disagrees with the current passing/blocked evidence.
- [x] Check whether the chosen cleanup makes any stale campaign or audit-memory
      wording redundant in active docs or generated surfaces; remove it or
      create a concrete follow-up.
- [x] Run required checks for touched scope:
  - [x] `make methodology-compile`
  - [x] `make methodology-check`
  - [x] If `scripts/methodology_graph.py` or `tests/test_methodology_graph.py`
        change: `python -m pytest tests/test_methodology_graph.py -q`
  - [x] If `scripts/methodology_graph.py` changes:
        `python -m ruff check scripts/methodology_graph.py tests/test_methodology_graph.py`
  - [x] If broader Python/runtime surfaces change beyond state/docs:
        `make lint` and `make test` not required; broader runtime untouched
- [x] Evals and goldens should stay unchanged; do not run `/improve-eval`
      unless the audit discovers a real registry/state mismatch that requires a
      fresh eval action instead of a roadmap refresh.
- [x] Search all docs and update any related to what we touched.
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: refreshed roadmap claims cite the exact story,
        eval, and coverage evidence they rely on
  - [x] T1 — AI-First: use AI for bounded audit judgment, not for inventing
        new planning ceremony
  - [x] T2 — Eval Before Build: inspect the current truth surfaces before
        adding any compiler guardrail
  - [x] T3 — Fidelity: keep blocked and supported-scope truth honest instead of
        over-promoting finished or unproven work
  - [x] T4 — Modular: refresh authored state and generated views instead of
        adding another planning surface
  - [x] T5 — Inspect Artifacts: manually inspect regenerated
        `docs/stories.md` and `docs/methodology/graph.json`, not just command
        success

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

- **Owning module / area**: methodology tooling and authored planning state
  under `docs/methodology/state.yaml`, `scripts/methodology_graph.py`,
  `tests/test_methodology_graph.py`, generated `docs/stories.md`, and generated
  `docs/methodology/graph.json`.
- **Methodology reality**: this belongs to `spec:8` and `spec:9`. Both
  category substrates exist in `docs/methodology/state.yaml`, and `B7` / `B8`
  are in `hold`, which makes simplification and truth maintenance the right
  next move. The story reads but should not directly rewrite coverage rows
  unless it finds a documented-truth mismatch.
- **Substrate evidence**: verified in repo that
  `scripts/methodology_graph.py` already validates campaign and
  architecture-audit story refs and renders the active-focus section in
  `docs/stories.md`; `tests/test_methodology_graph.py` already covers the
  methodology compiler; `docs/methodology/state.yaml` already owns `roadmap`
  and `architecture_audits`; and generated `docs/stories.md` currently shows
  Story `191` as explicitly blocked while Story `204` is the active
  methodology line. This pass also adds a narrow compiler/test guardrail
  against leaving an `active` campaign pointed only at terminal-status stories;
  stale recent-story memory remains authored-state policy rather than an
  inferred compiler rule.
- **Data contracts / schemas**: no runtime schema change is expected. The
  contract in scope is the authored methodology state and its compiled
  projection into `docs/methodology/graph.json` and `docs/stories.md`. If new
  validation rules land, keep `scripts/methodology_graph.py` and
  `tests/test_methodology_graph.py` aligned.
- **File sizes**: likely touched files are
  `docs/stories/story-204-methodology-roadmap-truth-refresh.md` (127 lines
  before drafting), `docs/methodology/state.yaml` (142 lines),
  `scripts/methodology_graph.py` (804 lines, already above 500),
  `tests/test_methodology_graph.py` (362 lines),
  `docs/stories.md` (249 lines, generated), and
  `docs/methodology/graph.json` (7851 lines, generated). Keep any compiler
  change surgical and prefer state-only cleanup if it is honest.
- **Decision context**: reviewed `AGENTS.md`, `docs/ideal.md`, `docs/spec.md`,
  `docs/methodology/state.yaml`, `docs/methodology/graph.json`,
  `docs/stories.md`, `docs/evals/registry.yaml`,
  `tests/fixtures/formats/_coverage-matrix.json`,
  `docs/runbooks/migrate-problem-first-triage-and-story-workflow.md`,
  Stories `191`, `195`, `199`, and Stories `196`-`203`. No narrower local ADR
  or runbook was found for refreshing stale roadmap/campaign truth after later
  story churn.

## Files to Modify

- `docs/stories/story-204-methodology-roadmap-truth-refresh.md` — keep the
  story record and work log current (127 lines before drafting)
- `docs/methodology/state.yaml` — refresh authored roadmap/campaign truth and
  architecture-audit memory (142 lines)
- `docs/stories.md` — regenerated story index after compile (249 lines,
  generated)
- `docs/methodology/graph.json` — regenerated compiled graph after compile
  (7851 lines, generated)
- `scripts/methodology_graph.py` — only if a minimal guardrail is needed around
  stale active campaigns or audit-memory drift (804 lines)
- `tests/test_methodology_graph.py` — only if compiler logic changes (362
  lines)

## Redundancy / Removal Targets

- Stale `roadmap.campaigns` entries that still present already-finished story
  bundles as active current work
- Stale `architecture_audits.domains.*.recent_story_refs` and
  `stories_since_audit` values that stop before Stories `199` or `196`-`203`
- Any generated index wording that continues to imply active roadmap momentum
  where the current repo only has a blocked handwriting health flag

## Notes

- New story justification: this is not a reopen of Story `195` or Story `199`.
  Story `195` cleaned legacy non-done drift and refreshed audit memory through
  April 7; Story `199` hardened the compiler/package contract. The current
  success surface is a later authored-state refresh after the direct-entry seam
  stories (`196`-`203`) and the fresh blocked handwriting evidence in Story
  `191`.
- The likely honest outcome is not a bigger roadmap. It may be a smaller one:
  closing stale campaigns, narrowing `active_focus`, and treating handwriting
  as a health flag until a real unblock appears.
- `mixed-archive` is currently the only `untested` coverage row, but current
  repo evidence shows no verified runtime substrate for it yet. This story
  should not smuggle a product-priority decision for that family into a
  methodology cleanup without fresh substrate verification.

## Plan

### Exploration Summary

- **Ideal alignment:** proceed. This story closes an Execution Ideal gap by
  removing stale planning claims, improving traceability, and keeping active
  methodology surfaces honest. It does not widen product claims or reopen a
  blocked OCR line without new evidence.
- **Relevant methodology state:** `spec:8` and `spec:9` both have substrate
  `exists` in `docs/methodology/state.yaml`, and `B7` / `B8` are both in
  `hold`, which favors simplification and truth maintenance over adding new
  planning machinery.
- **Fresh current-pass baseline:** `make methodology-check` passes on the
  current repo state, which confirms the compiler/test substrate is healthy but
  also proves the current validation surface does not catch this class of
  roadmap drift.
- **Current stale planning surface, from actual files:**
  - `docs/stories.md` still renders `active_focus` as `spec:1`, `spec:2`,
    `spec:7`, `spec:9`, even though the only live pre-existing delivery line is
    blocked Story `191` and the new open story is this methodology refresh.
  - `maintained-intake-honesty` is still `active` in
    `docs/methodology/state.yaml` / `docs/stories.md` but points only at done
    stories `176`, `180`, `186`, and `189`.
  - `methodology-graph-state-migration` is still `active` but points only at
    done stories `187` and `188`, even though later methodology follow-up work
    landed in Stories `199` and now `204`.
  - `architecture_audits` memory visibly lags same-domain work: at minimum
    `methodology_tooling`, `intake_and_routing`, `ocr_and_extraction`,
    `document_structure_and_consistency`, and `doc_web_runtime` all stop before
    later relevant stories now present in the repo.
- **Blocked/product truth to preserve:** Story `191` remains `Blocked`;
  `tests/fixtures/formats/_coverage-matrix.json` still shows
  `handwritten-notes` as `has-fixture` and `mixed-archive` as `untested`; and
  `docs/evals/registry.yaml` records the fresh failed handwritten retry on
  `2026-04-05`.
- **Critical substrate verified versus missing:**
  - Verified: `docs/methodology/state.yaml` already owns `roadmap` and
    `architecture_audits`; `scripts/methodology_graph.py` already validates
    story refs and renders `docs/stories.md`; `tests/test_methodology_graph.py`
    already covers methodology compiler behavior.
  - Missing: there is no current validation or render guardrail for an
    `active` campaign whose `story_refs` all resolve to terminal statuses, and
    there is no narrow test protecting against stale audit-memory lag.
- **Patterns to follow:** keep the first attempt metadata-only, regenerate the
  graph/index, and inspect the rendered truth surfaces manually before adding
  any compiler logic.

### Scope Adjustment

- **Small coherent delta folded in:** refresh every architecture-audit domain
  that obviously lags the post-April story set, not just `methodology_tooling`,
  because the acceptance criteria already require the state to reflect Stories
  `196`-`203` and blocked Story `191`.
- **Not recommended:** broader compiler policy that tries to infer the “right”
  campaign or audit state automatically from story churn. That would add more
  planning machinery than this cleanup warrants.

### Implementation Order

1. **Choose the authored-state target in `docs/methodology/state.yaml`** (`S`)
   - Decide the honest `roadmap.active_focus` for the current repo.
   - Current recommendation: narrow active focus to the methodology work that
     is actually buildable now (`spec:8`, `spec:9`) unless implementation finds
     a stronger reason to keep blocked handwriting categories visible as active
     focus instead of a health flag.
   - Refresh campaign truth:
     - `maintained-intake-honesty` must no longer remain `active` while
       pointing only at done stories. The implementation should either remove it
       from the active campaign list or rewrite it so it explicitly references a
       still-open line and says that line is blocked/health-flag-only.
     - `methodology-graph-state-migration` may stay `active` only if it is
       updated to point at the still-open methodology line (`204`) and its
       notes describe the remaining refresh/hardening work honestly.
   - Done when: the authored roadmap no longer implies active product momentum
     that the repo cannot currently execute.

2. **Refresh `architecture_audits` memory in `docs/methodology/state.yaml`** (`S`)
   - Update `recent_story_refs`, `stories_since_audit`, `last_audited_at`, and
     notes for the domains whose memory now lags repo reality.
   - Current expected domains and recent evidence slices:
     - `methodology_tooling`: Story `199` and Story `204`
     - `intake_and_routing`: Story `194` and Story `200`
     - `ocr_and_extraction`: Stories `189`, `191`, `192`
     - `document_structure_and_consistency`: Story `198`
     - `doc_web_runtime`: Stories `193`, `196`, `197`, `201`, `202`, `203`
   - Done when: no domain’s audit-memory slice obviously stops before later
     same-domain stories already recorded in the repo.

3. **Recompile and inspect the generated truth surfaces** (`S`)
   - Run `make methodology-compile`.
   - Inspect the regenerated `docs/stories.md` and
     `docs/methodology/graph.json` manually.
   - Verify the generated views no longer advertise stale active campaigns or
     outdated audit memory, while still showing Story `191` as blocked and
     keeping `mixed-archive` out of the active roadmap.
   - Done when: the rendered story index and compiled graph match the authored
     state without creating a new over-promise.

4. **Decide whether a compiler/test guardrail is justified** (`S`, conditional)
   - Baseline evidence for possible guardrail: `make methodology-check`
     currently passes even though two active campaigns point only at completed
     work and audit memory lags later same-domain stories.
   - Lowest-risk candidate: add a warning or error in
     `scripts/methodology_graph.py` when an `active` campaign resolves entirely
     to terminal-status stories, plus one targeted regression in
     `tests/test_methodology_graph.py`.
   - Higher-risk candidate, not recommended unless implementation proves it is
     necessary: automatic inference or strict validation around stale
     `architecture_audits` lag, because that policy is more subjective and more
     likely to overfit today’s story set.
   - Done when: either the cleanup stays metadata-only with a clear rationale,
     or the smallest justified warning-level guardrail is covered by a targeted
     test.

5. **Run verification for the touched scope** (`S`)
   - Required: `make methodology-compile`, `make methodology-check`.
   - Conditional: `python -m pytest tests/test_methodology_graph.py -q` and
     `python -m ruff check scripts/methodology_graph.py tests/test_methodology_graph.py`
     only if compiler/test files change.
   - Manual inspection remains mandatory for:
     - `docs/stories.md` Active Focus section
     - `docs/methodology/graph.json` `roadmap` slice
     - `docs/methodology/graph.json` `architecture_audits` slice
   - Done when: acceptance criteria are met with fresh current-pass evidence,
     not just a green command.

### Structural Health Notes

- `scripts/methodology_graph.py` is already large, so any code change should be
  surgical and warning-focused.
- `docs/stories.md` renders every campaign present in state under `## Active
  Focus`, which means campaign status wording directly affects user-facing
  planning truth.
- `docs/methodology/graph.json` is generated and large; manual inspection
  should stay focused on the changed roadmap and audit-memory slices rather than
  diff noise elsewhere.

### Risks And Approval Points

- **Active-focus semantics:** the main judgment call is whether blocked
  handwriting should still keep `spec:1` / `spec:2` in `active_focus`, or
  whether the honest current roadmap is methodology-only and handwriting should
  remain visible only as a blocked health flag.
- **Campaign representation:** if we want to preserve an inactive campaign
  record inside `state.yaml`, the current render path may still surface it under
  `## Active Focus`; that may push the implementation either toward removing the
  stale campaign from the active list entirely or toward a small render/validator
  follow-up.
- **Audit-memory policy:** updating stale `recent_story_refs` is low risk;
  encoding stronger compiler policy around that lag is more subjective and
  should remain optional.

### What “Done” Looks Like

- The story work log names the exact stale campaign refs, stale audit-memory
  domains, baseline methodology-check result, and blocked handwriting evidence
  reviewed in this pass.
- `docs/methodology/state.yaml` expresses one honest current roadmap and audit
  memory state.
- Regenerated `docs/stories.md` and `docs/methodology/graph.json` match that
  authored truth and stop advertising stale active campaign context.
- Any compiler/test change is minimal, targeted, and justified by the observed
  silent-drift gap rather than by a desire to automate planning policy.

## Work Log

20260409-1611 — story creation: created Story 204 after verifying that a new ID
is honest. Evidence reviewed in this pass: `AGENTS.md`, `docs/ideal.md`,
`docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`,
`docs/stories.md`, `docs/evals/registry.yaml`,
`tests/fixtures/formats/_coverage-matrix.json`, the methodology compiler/test
substrate, Story `191`, Story `195`, Story `199`, and Stories `196`-`203`.
Result: there is no active buildable story to reopen besides blocked Story
`191`, but the roadmap state is stale because `maintained-intake-honesty`
still points only at `176/180/186/189`, `methodology-graph-state-migration`
still points only at `187/188`, and the audit-memory refs stop before later
direct-entry and methodology follow-up work. This story is honestly `Pending`,
not `Draft`, because the state/compiler/generated-view substrate already exists
in code and the remaining work is a bounded planning-truth refresh. Next step:
`/build-story` should audit the authored roadmap shape, decide the smallest
honest update, and only touch `scripts/methodology_graph.py` if metadata-only
cleanup proves insufficient.
20260409-1620 — /build-story explore+plan: re-read the build-story workflow and
audited the current planning truth from `docs/ideal.md`, `docs/spec.md`,
`docs/methodology/state.yaml`, `docs/methodology/graph.json`,
`docs/stories.md`, `docs/evals/registry.yaml`,
`tests/fixtures/formats/_coverage-matrix.json`, Stories `191`, `192`, `193`,
`194`, `195`, `196`, `197`, `198`, `199`, `200`, `201`, `202`, `203`, the
methodology compiler/test substrate, and `docs/runbooks/triage-architecture.md`.
Fresh findings: `make methodology-check` still passes even though
`docs/stories.md` advertises `active_focus = spec:1/spec:2/spec:7/spec:9` and
two `active` campaigns whose story refs all resolve to done stories; Story
`191` remains blocked on the corrected handwritten corpus; the coverage matrix
still keeps `handwritten-notes` at `has-fixture` and `mixed-archive` at
`untested`; and at least five `architecture_audits` domains visibly lag later
same-domain stories now present in repo state. Critical substrate verified:
`docs/methodology/state.yaml` already owns the roadmap/audit-memory contract,
`scripts/methodology_graph.py` already validates story refs and renders the
generated views, and `tests/test_methodology_graph.py` already covers targeted
methodology rules. Critical missing guardrail: there is no current warning or
error for an `active` campaign that points only at terminal-status stories.
Files likely to change if implementation is approved: this story file,
`docs/methodology/state.yaml`, generated `docs/stories.md`, generated
`docs/methodology/graph.json`, and only conditionally
`scripts/methodology_graph.py` plus `tests/test_methodology_graph.py`. Next
step: wait for user approval on the plan, then implement the metadata refresh
first and add a tiny compiler/test guardrail only if the metadata-only pass
still leaves a real silent-drift gap.
20260409-1638 — implementation: refreshed the authored methodology state,
regenerated the compiled surfaces, and landed one narrow compiler/test
guardrail. `docs/methodology/state.yaml` now narrows `active_focus` to
`spec:8/spec:9`, keeps `methodology-graph-state-migration` active via Stories
`187/188/199/204`, keeps `maintained-intake-honesty` active only because it now
explicitly references blocked Story `191` plus the recently completed bounded
proof/direct-entry line (`196/197/200/201/202/203`), rewrites the generated
index guidance so Story `191` is a blocked health flag rather than an active
build lane, and refreshes all five stale `architecture_audits` domains to the
April 9 repo state. Because the current compiler had allowed this drift to pass
cleanly, `scripts/methodology_graph.py` now fails validation when an `active`
campaign points only at terminal-status stories, and
`tests/test_methodology_graph.py` adds a focused regression for that rule.
Fresh verification in this pass: `make methodology-compile`,
`make methodology-check`, `python -m pytest tests/test_methodology_graph.py -q`
(`13 passed in 0.77s`), and
`python -m ruff check scripts/methodology_graph.py tests/test_methodology_graph.py`
all passed. Manual artifact inspection: `docs/stories.md` now shows `Active
categories: spec:8, spec:9`, both active campaigns explain their real open
line, Story `204` renders as `In Progress`, Story `191` remains `Blocked`, and
`docs/methodology/graph.json` now carries refreshed `roadmap` and
`architecture_audits` slices with `validation.errors = []` and
`validation.warnings = []`. Blocked/product truth stayed unchanged: the
coverage matrix still keeps `handwritten-notes` at `has-fixture` and
`mixed-archive` at `untested`, and no eval or runtime claim was widened.
20260409-1652 — /mark-story-done closeout: revalidated the completed story on
current tip before closing it. Fresh evidence in this pass: `make
methodology-compile`, `make methodology-check`,
`python -m pytest tests/test_methodology_graph.py -q` (`13 passed in 0.84s`),
`python -m ruff check scripts/methodology_graph.py tests/test_methodology_graph.py`,
and `git diff --check` all passed. Manual inspection confirmed
`docs/stories.md` now renders `Active categories: spec:8, spec:9`, shows Story
`204` as the active methodology line, and keeps Story `191` visible only as a
blocked health flag; `docs/methodology/graph.json` carries the refreshed
`roadmap` and `architecture_audits` slices with `validation.errors = []` and
`validation.warnings = []`. Result: Story 204 is complete and safe to close;
the remaining work is landing hygiene only. Next step: `/check-in-diff`.
20260409-1656 — closeout fix: marking Story 204 `Done` triggered the new
active-campaign guardrail as intended because
`methodology-graph-state-migration` then referenced only terminal stories.
Resolved that minor closeout issue by retiring the finished methodology
campaign from the active roadmap, leaving `maintained-intake-honesty` as the
only active campaign, and updating the recommended-order prose so Story `204`
is recorded as the completed planning refresh rather than a still-open lane.
Next step: rerun methodology compile/check on the final closeout state, then
continue `/check-in-diff`.
20260409-1700 — completion note: reran the full close-out validation suite on
the final Story 204 tree. Fresh evidence in this pass: `make
methodology-compile`, `make methodology-check`, `python -m pytest tests/`
(`518 passed, 4 warnings in 661.50s`), `python -m ruff check modules/ tests/`,
`python -m pytest tests/test_methodology_graph.py -q` (`13 passed in 0.84s`),
`python -m ruff check scripts/methodology_graph.py tests/test_methodology_graph.py`,
and `git diff --check` all passed. Result: the story is now fully validated and
closed, the generated methodology surfaces reflect `Done`, and the remaining
work is git landing only. Next step: `/check-in-diff`.
