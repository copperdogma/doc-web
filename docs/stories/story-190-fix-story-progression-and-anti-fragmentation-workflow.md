---
title: "Fix Story Progression and Anti-Fragmentation Workflow"
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
  - "187"
  - "188"
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

# Story 190 - Fix Story Progression and Anti-Fragmentation Workflow

**Priority**: High
**Status**: Done
**Decision Refs**: `AGENTS.md`, `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/methodology-artifact-audit-and-migration.md`, `docs/runbooks/migrate-problem-first-triage-and-story-workflow.md`, Story 187, Story 188, Stories 179/182/185/186/189, `/Users/cam/Documents/Projects/Storybook/storybook/docs/runbooks/migrate-methodology-to-graph-state.md`, `/Users/cam/Documents/Projects/Storybook/storybook/docs/methodology-artifact-audit-and-migration.md`, `/Users/cam/Documents/Projects/Storybook/storybook/docs/stories/story-079-methodology-artifact-audit-and-graph-design.md`, `/Users/cam/Documents/Projects/Storybook/storybook/docs/stories/story-081-legacy-metadata-backfill.md`, `/Users/cam/Documents/Projects/Storybook/storybook/docs/methodology-ideal-spec-compromise.md`, `/Users/cam/Documents/Projects/Storybook/storybook/AGENTS.md`, `None found after search in docs/decisions/ for a repo-local ADR that already resolves story progression semantics`
**Depends On**: Story 187, Story 188

## Goal

Repair the repo's story workflow so it behaves like one coherent planning system
instead of a backlog ceremony generator. The fix needs to address three linked
failures now visible after the graph+state migration: coherent work is being
split into serial micro-stories, `/build-story` dead-ends on detailed Draft
stories instead of doing the obvious promotion step, and the current status
model is enforced as manual process overhead rather than as low-friction
execution state. The default direction for this story is to keep the canonical
five-status model, but make it behave honestly: `/create-story` should be able
to end in `Draft`, `Pending`, or `Blocked` based on actual repo reality, and
`/build-story` should promote or block stories when its exploration proves that
the current state is wrong. The outcome should be a problem-first story
workflow that keeps related work in one story by default and makes build
readiness obvious.

## Acceptance Criteria

- [x] This story records a repo-specific audit of the current workflow failure
      mode with concrete evidence from local skills, local graph/state truth,
      and the handwritten story chain (`179`, `182`, `185`, `186`, `189`)
- [x] The repo has an explicit canonical story-progression policy for the
      graph+state framework that keeps
      `Draft` / `Pending` / `In Progress` / `Blocked` / `Done`, and defines
      honest transitions between them:
  - [x] `/create-story` can emit `Draft`, `Pending`, or `Blocked` based on the
        completeness of the story and the blocker evidence it finds
  - [x] `Pending` means fully fleshed out and honestly buildable now
  - [x] `Blocked` means the work is well-enough specified to preserve, but
        cannot proceed because of a named blocker with explicit evidence and an
        unblock condition
  - [x] `Draft` remains the right state for ideas or partial scopes that are not
        yet concrete enough, not a dumping ground for already-buildable stories
- [x] `/create-story` defaults to whole usable slices rather than backend-only
      partials when the functionality is meant to be user-facing:
  - [x] if a feature needs an operator or end-user UI to actually be used or
        inspected, the default story shape includes that UI slice
  - [x] backend-only stories remain valid only when the functionality is
        genuinely non-UI or when the story explicitly records why the UI is
        intentionally deferred or owned elsewhere
- [x] `triage-stories`, `create-story`, `build-story`, `validate`, and
      `mark-story-done` all enforce the same anti-fragmentation rule: work in
      the same subsystem, same validation boundary, and same success surface
      stays in one story unless it becomes materially distinct, crosses into a
      new runtime seam, or would make validation unclear
- [x] `/triage` and `triage-stories` use a problem-first weighting model:
  - [x] existing story shells do not carry major intrinsic priority just because
        they exist
  - [x] continuity / momentum remains a positive bias for active or recently
        advanced work lines with an unresolved success surface
  - [x] story existence acts as packaging / tie-break context, not as a primary
        value signal by itself
- [x] `/build-story` no longer hard-stops on a sufficiently detailed Draft story
      when the required sections and substrate already exist; it performs the
      obvious promotion path or equivalent low-friction transition and records
      that decision explicitly
- [x] Blocked-story recording becomes inspectable and consistent:
  - [x] the story template has a canonical place for blocker summary, blocker
        evidence, and unblock condition
  - [x] if the compiler/graph participates in story-truth consumption, blocked
        story metadata is surfaced there well enough for triage to reason about
        it without hidden notes
- [x] `AGENTS.md`, the relevant methodology skills, and any graph/compiler/test
      surfaces teach one consistent story-lifecycle contract, and the resulting
      generated methodology artifacts stay current after the change
- [x] A reusable migration runbook exists for other repos, is updated only with
      settled/landed changes during implementation, and captures the final
      migration steps without preserving false starts
- [x] A behavior-certification matrix exists and is checked during this story,
      covering at least these scenarios:
  - [x] rough idea or underspecified story lands as `Draft`
  - [x] concrete, substrate-verified story lands as `Pending`
  - [x] concrete but blocked story lands as `Blocked`
  - [x] a user-facing feature story includes the needed UI slice by default, or
        explicitly records why UI is out of scope
  - [x] `/build-story` promotes a buildable Draft instead of hard-stopping
  - [x] `/build-story` marks a story `Blocked` when exploration proves a real
        blocker
  - [x] `/triage` favors continuity on an active unresolved work line over an
        unrelated backlog shell when leverage is otherwise comparable
  - [x] `/validate` recommends `Keep open` for coherent same-surface remaining
        work instead of defaulting to `Rescope then close`
  - [x] `/mark-story-done` only recommends `Rescope then close` when the
        remaining work is genuinely separate
- [x] Fresh methodology validation passes after the last fix:
  - [x] `make methodology-compile`
  - [x] `make methodology-check`
  - [x] `make skills-check`
  - [x] `python -m pytest tests/test_methodology_graph.py -q`
  - [x] `python -m ruff check scripts/methodology_graph.py tests/test_methodology_graph.py`

## Out of Scope

- Rewriting the whole methodology architecture beyond the story-lifecycle and
  workflow-consumer surfaces that actually cause this problem
- Changing runtime document-conversion behavior, schemas, or coverage-matrix
  truth for file formats
- Bulk-cleaning every historical `In Progress`, `To Do`, `Won't Do`, or
  `Obsolete` legacy story unless that cleanup becomes necessary to land the new
  canonical policy
- Creating a new methodology ADR unless implementation proves the story
  lifecycle itself is now a hard-to-reverse cross-project architecture decision

## Approach Evaluation

- **Simplification baseline**: this is a workflow-contract and tool-behavior
  problem, not a missing-ideas problem. A single LLM call can suggest better
  policy, but it cannot fix the repo until the current consumer logic, graph
  contract, and docs all agree.
- **AI-only**: rejected as the full solution. More prose or better prompting
  would not stop `build-story` from hard-stopping on Draft or `triage-stories`
  from recommending serial follow-up stories for the same work line.
- **Hybrid**: likely winner. Use the current repo plus Storybook migration
  references to audit responsibilities, then make narrow deterministic changes to
  the workflow skills, graph/compiler contract if needed, and core docs.
- **Pure code**: only partially viable. If the right answer is to derive
  build-readiness automatically, code changes are needed, but the policy still
  has to be documented in `AGENTS.md` and the skills.
- **Repo constraints / prior decisions**: Story 187 and Story 188 established
  the graph+state model and migrated the core methodology surfaces. The new
  Storybook references still use the same nominal status set, so the framework
  did not itself mandate a different taxonomy; the consumer behavior is where
  the local drift appears. `AGENTS.md` already says coherent scope expansion is
  the default, so the fix should tighten consumers toward that rule instead of
  inventing a conflicting policy.
- **Existing patterns to reuse**: the current methodology compiler, generated
  story index, story frontmatter template, local scope-expansion rules in
  `AGENTS.md` and `build-story`, and the Storybook migration audit's consumer
  hotspot method.
- **Eval**: success is a clean methodology compile/check pass plus direct review
  of the updated skill text, generated story/index output, and a behavior
  certification matrix covering the key transition and triage scenarios. The key
  proof is not just that the repo teaches one story-progression model, but that
  the updated workflow surfaces now imply the same next action in the same
  concrete cases.

## Tasks

- [x] Write the workflow audit into this story and the work log before changing
      tooling: current status counts, current Draft/Pending behavior, the
      handwritten fragmentation example, and the Storybook-framework comparison
- [x] Lock in the canonical five-status model
      (`Draft/Pending/In Progress/Blocked/Done`) and document the transition
      rules with explicit rationale
- [x] Update `/triage` so its cross-domain synthesis weights real leverage,
      Ideal movement, and active-problem continuity above simple backlog-shell
      existence
- [x] Update `triage-stories` so it can recommend continuing, reopening,
      expanding, or consolidating a current problem line instead of only picking
      the next story shell, and so Draft/Pending presence is only a small
      packaging/tie-break signal rather than a primary value signal
- [x] Update `create-story` so it checks whether the requested work is actually
      an expansion of a recent story in the same subsystem/validation surface
      before normalizing it into a new story ID, so it can honestly end in
      `Draft`, `Pending`, or `Blocked`, and so it biases user-facing work toward
      whole usable slices that include the needed UI
- [x] Update `build-story` so a sufficiently detailed Draft can move into the
      obvious build-ready state without a dead-end manual stop, and so it can
      mark a story `Blocked` when exploration proves a real blocker exists
- [x] Update `validate` so it stops nudging coherent same-surface work toward
      `Rescope then close` by default and instead stays aligned with the
      anti-fragmentation rule
- [x] Update `mark-story-done` so it defaults to keeping same-surface work in
      the current story, using `Rescope then close` only when the remaining work
      is genuinely separate
- [x] Update `AGENTS.md` and any related methodology docs so the written policy
      matches the tooling behavior
- [x] Create and maintain a migration runbook that other repos can follow to
      adopt the same story-progression and triage-weighting changes; update it
      during implementation with settled decisions and landed steps only
- [x] If the chosen status policy changes the canonical graph contract, update
      `scripts/methodology_graph.py`, `tests/test_methodology_graph.py`,
      `docs/methodology/graph.json`, and `docs/stories.md` accordingly
- [x] Update the story template so blocked stories have a canonical place to
      record blocker evidence and unblock conditions instead of relying on
      ad-hoc notes
- [x] Add and complete a behavior-certification matrix in the story and the
      migration runbook so the new workflow is verified by concrete scenarios,
      not just by clean graph rebuilds
- [x] Check whether the chosen implementation makes any skill wording,
      boilerplate status guidance, or manual promotion ceremony redundant; remove
      it or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] `make methodology-compile`
  - [x] `make methodology-check`
  - [x] `make skills-check`
  - [x] `python -m pytest tests/test_methodology_graph.py -q`
  - [x] `python -m ruff check scripts/methodology_graph.py tests/test_methodology_graph.py`
  - [x] `git diff --check`
  - [x] No pipeline runtime change is expected, so `driver.py` validation is
        not required unless scope expands unexpectedly
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 - Traceability: story-progression decisions trace back to explicit
        graph/state/skill evidence instead of hidden habit or guesswork
  - [x] T1 - AI-First: keep the workflow as thin as possible; do not preserve
        manual process steps that only exist to compensate for old agent habits
  - [x] T2 - Eval Before Build: use the current repo behavior and story history
        as the measured baseline before rewriting the workflow contract
  - [x] T3 - Fidelity: preserve the true scope of the work instead of slicing it
        into misleading micro-stories or silently weakening close-out criteria
  - [x] T4 - Modular: keep the status/compiler contract, skill behavior, and
        docs aligned instead of scattering separate story rules across surfaces
  - [x] T5 - Inspect Artifacts: manually inspect the generated graph/index and
        updated skill/docs after the change, not just the command exit codes

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: methodology tooling, story lifecycle policy, and AI
  workflow surfaces under `AGENTS.md`, `.agents/skills/`, and
  `scripts/methodology_graph.py`
- **Methodology reality**: this belongs to `spec:8` and `spec:9`. Both category
  substrates are currently `exists`, and the relevant compromises `B7` and `B8`
  are both in `hold`, which makes simplification and friction removal the right
  kind of work now. No coverage-matrix row changes are expected.
- **Substrate evidence**: the current graph/state/tooling stack already exists
  in `docs/methodology/state.yaml`, `docs/methodology/graph.json`,
  `scripts/methodology_graph.py`, `docs/stories.md`, `AGENTS.md`,
  `.agents/skills/create-story/SKILL.md`,
  `.agents/skills/triage-stories/SKILL.md`,
  `.agents/skills/build-story/SKILL.md`, and
  `.agents/skills/mark-story-done/SKILL.md`. After Story 190 moved to
  `In Progress`, the graph showed `Draft 1`, `Pending 0`, and `In Progress 5`
  on 2026-04-04. That reinforced `Pending` as a transitional planning state
  rather than an active stable queue.
- **Data contracts / schemas**: no runtime product schema changes are expected.
  The contract that may change is the canonical story status set and its sort /
  validation semantics in `scripts/methodology_graph.py` plus any generated
  views that depend on it.
- **File sizes**: `AGENTS.md` is 453 lines, `.agents/skills/triage/SKILL.md` is
  125 lines, `.agents/skills/triage-stories/SKILL.md` is 146 lines,
  `.agents/skills/create-story/SKILL.md` is 154 lines,
  `.agents/skills/create-story/templates/story.md` is 121 lines,
  `.agents/skills/build-story/SKILL.md` is 180 lines,
  `.agents/skills/validate/SKILL.md` is 229 lines,
  `.agents/skills/mark-story-done/SKILL.md` is 130 lines,
  `scripts/methodology_graph.py` is 764 lines,
  `tests/test_methodology_graph.py` is 243 lines, and
  `docs/runbooks/migrate-problem-first-triage-and-story-workflow.md` is
  355 lines. Keep compiler edits narrow and tested.
- **Decision context**: reviewed the local methodology spine, Story 187,
  Story 188, the handwritten story chain, and the Storybook graph/state
  migration references. No local ADR currently settles story progression
  semantics after the migration.

## Files to Modify

- `docs/stories/story-190-fix-story-progression-and-anti-fragmentation-workflow.md`
  - story artifact and execution log for this work
- `AGENTS.md` - align the written story-lifecycle and scope-expansion policy
  with the chosen behavior (436 lines)
- `.agents/skills/triage/SKILL.md` - change full-sweep synthesis so it ranks
  problems before backlog shells and preserves continuity bias correctly
- `.agents/skills/triage-stories/SKILL.md` - change candidate/recommendation
  logic away from backlog-first micro-story creation (126 lines)
- `.agents/skills/create-story/SKILL.md` - add anti-fragmentation and
  expansion-vs-new-story checks plus UI-complete story-shaping defaults
  (121 lines)
- `.agents/skills/create-story/templates/story.md` - add canonical blocked-story
  recording fields/section and any status guidance needed by the new policy
- `.agents/skills/build-story/SKILL.md` - remove the Draft hard-stop behavior
  for already-buildable stories (172 lines)
- `.agents/skills/validate/SKILL.md` - align validation recommendations with the
  same anti-fragmentation and blocked-story policy
- `.agents/skills/mark-story-done/SKILL.md` - tighten close-out guidance so same
  problem-line work stays in one story by default (123 lines)
- `scripts/methodology_graph.py` - update canonical status validation and sort
  semantics, and surface blocked-story metadata if the graph is used for triage
  truth (720 lines)
- `tests/test_methodology_graph.py` - cover any compiler/graph behavior changed
  by the new policy (152 lines)
- `docs/methodology/graph.json` - regenerated graph output
- `docs/stories.md` - regenerated story index output
- `docs/methodology-artifact-audit-and-migration.md` - only if the migration
  audit or active-surface contract needs to record the revised story lifecycle
  policy (391 lines)
- `docs/methodology-ideal-spec-compromise.md` - only if implementation needs a
  small graph-first methodology wording update so the long-lived reference stays
  aligned with the landed story workflow
- `docs/runbooks/migrate-problem-first-triage-and-story-workflow.md` - living
  cross-repo migration document written during implementation and finalized as
  the settled path

## Redundancy / Removal Targets

- Manual Draft-to-Pending ceremony when the story is already detailed and
  substrate-verified
- Backlog-first skill wording that treats "new story" as the default answer to
  "same problem, next evidence pass"
- Close-out guidance that encourages rescoping coherent work into serial
  follow-up stories just to achieve closure

## Notes

- **Issue summary**: the current workflow is over-slicing coherent work and
  charging full story overhead for tiny incremental steps. That is directly at
  odds with `docs/ideal.md`'s execution ideal of "No process overhead" and with
  `AGENTS.md`'s rule to default to coherent scope expansion.
- **What I found**:
  - `triage-stories` currently reads Draft/Pending stories as candidates and
    ends with "one next story action." It can recommend a Draft story, but it
    still frames the next move as selecting a story shell rather than continuing
    the same problem line.
  - `create-story` is optimized to bootstrap a new numbered story and does not
    require an explicit "why is this not just an expansion of the recent story
    on the same surface?" check.
  - `build-story` currently hard-stops on `Draft`, even when the story already
    has the sections and substrate needed to build. That means the agent stalls
    on obvious promotion work instead of just doing it.
  - `create-story` is also too willing to produce backend-only story shells for
    user-facing functionality. That leaves the repo with stories that technically
    advance plumbing but do not describe the usable slice the user actually
    needs.
  - `validate` still teaches a default preference for `Rescope then close` when
    remaining gaps are moved to follow-up stories, so fragmentation pressure
    still leaks in through the validation path even if the other story skills
    improve.
  - `mark-story-done` currently prefers `Rescope then close` once follow-up
    stories exist, which rewards early closure and makes fragmentation easier to
    normalize.
  - The handwritten sequence (`179`, `182`, `185`, `186`, `189`) is the clearest
    local proof of the failure mode. Stories `179`, `182`, `185`, and `186` are
    all phases of the same proof surface; only `189` is clearly separable
    because it changes the maintained runtime seam.
  - The current graph reinforces the friction signal: on 2026-04-04 there is
    `Draft 1` (Story 136), `Pending 1` (Story 190), and `In Progress 4`. That
    still makes `Pending` look more like manual ceremony than like an actively
    used planning state.
- **Story-status assessment under the new framework**:
  - The Storybook graph+state migration references still use the same five
    statuses, so the framework itself did not prove that a different taxonomy is
    required.
  - The recommended local direction is to keep the same five statuses, but make
    their entry and transition rules honest. `Draft`, `In Progress`, `Done`, and
    `Blocked` are clearly useful. `Pending` should stay only as the explicit
    "buildable now" state rather than as a manual promotion ceremony.
  - That means `/create-story` should be able to end in `Draft`, `Pending`, or
    `Blocked` based on what it actually finds. A fleshed-out, substrate-verified
    story should be born `Pending`. A researched story with a named blocker and
    clear unblock condition should be born `Blocked`. A rough idea or partially
    specified story should stay `Draft`.
  - `Blocked` should not mean "this seems hard." It should mean "this cannot
    honestly proceed right now because of X," with evidence and a concrete
    condition that would unblock it.
- **Suggested fixes**:
  - Same subsystem + same validation boundary + same success surface should stay
    in one story unless the work becomes materially distinct.
  - `/triage` should rank problems first, then choose the right vehicle. A story
    already existing should help packaging and continuity, but it should not
    create major priority by itself.
  - Continuity bias is still good when it reflects active work on the same
    unresolved problem line. If the repo is actively advancing one format family
    or one campaign, triage should prefer finishing that line over random
    context-switching.
  - `create-story` should be able to finish in `Draft`, `Pending`, or `Blocked`
    depending on the story it actually wrote and the blocker evidence it found.
  - `create-story` should default to the whole usable slice for user-facing
    functionality. If the feature needs UI to exist in any honest sense, the
    story should include that UI unless it explicitly records why not.
  - `build-story` should be able to promote a sufficiently detailed Draft into
    the build-ready state instead of hard-stopping, and it should also be able
    to move a story to `Blocked` if exploration proves the blocker is real.
  - `triage-stories` should be able to recommend continuing, reopening, or
    expanding an existing story, not only creating the next one.
  - `create-story` should require explicit justification when the requested work
    touches the same problem line as a recent story.
  - `validate` should stop reinforcing the old fragmentation pattern and should
    recommend keeping coherent same-surface work together unless there is a real
    reason to split or block it.
  - `mark-story-done` should default to `Keep open` for same-surface remaining
    work, reserving `Rescope then close` for genuinely separate follow-ups.
  - The repo should certify the new workflow with concrete scenario checks,
    not just graph rebuild success, so the semantic change is harder to drift
    away from later.
  - The repo should keep a living migration runbook during implementation so the
    final pattern can be ported to other repos without reconstructing decisions
    from work logs after the fact.

## Behavior Certification Matrix

- [x] Rough idea -> `Draft`
  Evidence: `.agents/skills/create-story/SKILL.md` now defines `Draft` as the
  preserve-but-not-buildable state and instructs status selection from research
  instead of default paperwork.
- [x] Concrete and buildable -> `Pending`
  Evidence: `.agents/skills/create-story/SKILL.md` now defines `Pending` as
  fully detailed and honestly buildable now, with graph/state substrate
  verification before assignment.
- [x] Concrete but blocked -> `Blocked`
  Evidence: `.agents/skills/create-story/SKILL.md`,
  `.agents/skills/create-story/templates/story.md`,
  `scripts/methodology_graph.py`, and
  `tests/test_methodology_graph.py` now require canonical blocker sections and
  validate missing blocker truth for `Blocked` stories.
- [x] User-facing functionality -> UI-complete story
  Evidence: `.agents/skills/create-story/SKILL.md`, `AGENTS.md`, and
  `docs/runbooks/migrate-problem-first-triage-and-story-workflow.md` now direct
  user-facing stories to include the needed UI slice unless the deferral is
  explicitly recorded.
- [x] Buildable Draft -> promote instead of stop
  Evidence: `.agents/skills/build-story/SKILL.md` now keeps buildable Drafts in
  flow, promoting them to `Pending` instead of hard-stopping on status
  paperwork.
- [x] Proven blocker during build -> `Blocked`
  Evidence: `.agents/skills/build-story/SKILL.md` now tells the agent to mark a
  story `Blocked` when exploration or deeper implementation proves a real
  blocker.
- [x] Continuity beats unrelated shell
  Evidence: `.agents/skills/triage/SKILL.md` and
  `.agents/skills/triage-stories/SKILL.md` now rank problems first, preserve
  active-line continuity, and demote story-shell existence to packaging /
  tie-break context.
- [x] Same-line request avoids new story ID
  Evidence: `.agents/skills/create-story/SKILL.md` now stops before running the
  bootstrap script when the requested work still belongs to an existing story's
  subsystem, validation boundary, and success surface.
- [x] Validation keeps coherent work together
  Evidence: `.agents/skills/validate/SKILL.md` now recommends `Keep open` for
  same-subsystem / same-validation-boundary / same-success-surface remaining
  work.
- [x] Close-out only splits truly separate work
  Evidence: `.agents/skills/mark-story-done/SKILL.md` now reserves
  `Rescope then close` for genuinely separate remaining work and prevents
  follow-up-story existence from acting as a closure vote by itself.

## Plan

1. **Baseline and contract lock**
   Files: [AGENTS.md](/Users/cam/.codex/worktrees/ecf0/doc-web/AGENTS.md), [story-190-fix-story-progression-and-anti-fragmentation-workflow.md](/Users/cam/.codex/worktrees/ecf0/doc-web/docs/stories/story-190-fix-story-progression-and-anti-fragmentation-workflow.md), [migrate-problem-first-triage-and-story-workflow.md](/Users/cam/.codex/worktrees/ecf0/doc-web/docs/runbooks/migrate-problem-first-triage-and-story-workflow.md), and only if needed [methodology-ideal-spec-compromise.md](/Users/cam/.codex/worktrees/ecf0/doc-web/docs/methodology-ideal-spec-compromise.md).
   Change: lock the five-status policy, the same-surface anti-fragmentation rule, the continuity-bias rule, and the UI-complete story-shaping rule into one written contract before changing consumer skills.
   Baseline: by direct skill-text inspection, the repo initially clearly satisfied 2 of the then-9 certification scenarios (`Draft` for rough ideas and `Pending` for concrete buildable stories), partially satisfied 1 (`Blocked` exists but blocker evidence was not yet canonicalized), and failed the remaining 6 scenarios.
   Risks: if the written contract stays split across old and new wording, the consumer updates will drift again.
   Done looks like: one consistent policy is visible in the core docs and migration runbook, with no remaining contradiction about Draft promotion, same-surface continuation, or UI-needed story shape.

2. **Make triage problem-first instead of backlog-first**
   Files: [triage/SKILL.md](/Users/cam/.codex/worktrees/ecf0/doc-web/.agents/skills/triage/SKILL.md) and [triage-stories/SKILL.md](/Users/cam/.codex/worktrees/ecf0/doc-web/.agents/skills/triage-stories/SKILL.md).
   Change: teach `/triage` to rank leverage, Ideal movement, and active-line continuity ahead of story-shell existence; teach `triage-stories` to recommend continue/reopen/expand/consolidate actions instead of only picking the next story shell.
   Impact: this is the highest-leverage behavioral fix because it changes what the repo sees as the "next best move" before any story is created or closed.
   Risks: overcorrecting could make triage ignore useful backlog packaging, so story existence should remain a tie-break and continuity aid rather than vanish entirely.
   Done looks like: both skills explicitly say story existence is a small packaging signal, continuity bias is preserved for active unresolved lines, and the recommended action can be something other than "create the next story."

3. **Fix story creation and build transitions**
   Files: [create-story/SKILL.md](/Users/cam/.codex/worktrees/ecf0/doc-web/.agents/skills/create-story/SKILL.md), [story.md](/Users/cam/.codex/worktrees/ecf0/doc-web/.agents/skills/create-story/templates/story.md), and [build-story/SKILL.md](/Users/cam/.codex/worktrees/ecf0/doc-web/.agents/skills/build-story/SKILL.md).
   Change: add the "why is this not an expansion of the current line?" check, allow `/create-story` to end in `Draft`, `Pending`, or `Blocked`, require canonical blocker fields in the template, bias user-facing work toward usable UI-complete slices, and let `/build-story` promote a buildable Draft or mark a story Blocked when exploration proves a real blocker.
   Impact: this removes the manual promotion dead-end and reduces backend-only or serial micro-story creation at the source.
   Risks: the transition rules could become too eager if "blocked" or "promote" are underspecified, so blocker evidence and unblock conditions need to be explicit and inspectable.
   Done looks like: `create-story` and `build-story` share one honest progression model, and the template gives blocked stories a stable place to record why they cannot proceed.

4. **Fix closeout semantics so they stop re-fragmenting work**
   Files: [validate/SKILL.md](/Users/cam/.codex/worktrees/ecf0/doc-web/.agents/skills/validate/SKILL.md) and [mark-story-done/SKILL.md](/Users/cam/.codex/worktrees/ecf0/doc-web/.agents/skills/mark-story-done/SKILL.md).
   Change: remove the current bias toward `Rescope then close` for coherent same-surface remaining work, keep `Keep open` as the default when the work still belongs to the same problem line, and reserve closeout splitting for genuinely separate follow-ups.
   Impact: this closes the remaining leak path that can undo the rest of the story-lifecycle repair during validation or closeout.
   Risks: if the wording is too soft, stories may linger without a clear next action; the updated guidance needs firm recommendations for keep-open, blocked, or truly separate follow-up cases.
   Done looks like: both closeout surfaces recommend the same answer for the same scenario, and same-surface remaining work no longer gets split just to make the story status look cleaner.

5. **Patch the graph/compiler surface only where policy becomes canonical truth**
   Files: [methodology_graph.py](/Users/cam/.codex/worktrees/ecf0/doc-web/scripts/methodology_graph.py), [test_methodology_graph.py](/Users/cam/.codex/worktrees/ecf0/doc-web/tests/test_methodology_graph.py), [graph.json](/Users/cam/.codex/worktrees/ecf0/doc-web/docs/methodology/graph.json), and [stories.md](/Users/cam/.codex/worktrees/ecf0/doc-web/docs/stories.md).
   Change: if blocked-story metadata becomes part of inspectable story truth, parse and surface it in the graph; otherwise keep compiler changes minimal. Add focused tests for any new parser or sort behavior and regenerate the compiled artifacts.
   Structural health note: [methodology_graph.py](/Users/cam/.codex/worktrees/ecf0/doc-web/scripts/methodology_graph.py) is already 720 lines, so compiler edits should stay narrow and test-backed.
   Human-approval blocker: none expected unless implementation proves the graph contract itself must widen more than the current story already anticipates.
   Done looks like: graph/test surfaces match the written policy, generated artifacts rebuild cleanly, and there is no hidden blocked-state truth that triage must infer from prose.

6. **Land the migration runbook and certification matrix as implementation proof**
   Files: [story-190-fix-story-progression-and-anti-fragmentation-workflow.md](/Users/cam/.codex/worktrees/ecf0/doc-web/docs/stories/story-190-fix-story-progression-and-anti-fragmentation-workflow.md) and [migrate-problem-first-triage-and-story-workflow.md](/Users/cam/.codex/worktrees/ecf0/doc-web/docs/runbooks/migrate-problem-first-triage-and-story-workflow.md).
   Change: keep the runbook updated only with settled decisions, and complete the certification matrix against the final landed wording and compiler behavior.
   Impact: this is the portability proof for other repos and the regression shield against future drift.
   Evidence target: after implementation, the repo should be able to demonstrate all 10 certification scenarios directly from the landed skill/docs/template/graph surfaces.
   Done looks like: another repo can port the change set without replaying this investigation, and this story contains the final certification evidence instead of only design intent.

7. **Verification pass after the last functional edit**
   Files/tests: [AGENTS.md](/Users/cam/.codex/worktrees/ecf0/doc-web/AGENTS.md), the touched skill files under [/Users/cam/.codex/worktrees/ecf0/doc-web/.agents/skills](/Users/cam/.codex/worktrees/ecf0/doc-web/.agents/skills), [methodology_graph.py](/Users/cam/.codex/worktrees/ecf0/doc-web/scripts/methodology_graph.py), and [test_methodology_graph.py](/Users/cam/.codex/worktrees/ecf0/doc-web/tests/test_methodology_graph.py).
   Checks: `make methodology-compile`, `make methodology-check`, `make skills-check`, `python -m pytest tests/test_methodology_graph.py -q`, `python -m ruff check scripts/methodology_graph.py tests/test_methodology_graph.py`, and `git diff --check`.
   Risk focus: generated graph/index drift, inconsistent skill wording, or parser/test gaps around blocked metadata.
   Done looks like: all required checks pass after the final edit, and manual inspection of the regenerated story/graph surfaces confirms the repo now teaches one coherent workflow.

## Work Log

20260404-1535 - story creation audit: captured the workflow problem before any
implementation changes. Evidence from local consumers shows the failure is real
and current: `build-story` stops on Draft instead of performing the obvious
promotion path, `triage-stories` and `create-story` normalize work into new
story actions, and `mark-story-done` prefers follow-up-story closure once the
work has already been split. Evidence from local story history shows the cost:
the handwritten proof line was fragmented across Stories `179`, `182`, `185`,
`186`, and `189`, even though most of that sequence stayed in the same
subsystem and validation surface. Evidence from current graph truth sharpens the
status question: on 2026-04-04 the repo has `Draft 1`, `Pending 1`,
`In Progress 4`, which still suggests `Pending` is currently more ceremony than
queue.
Storybook's graph+state references still keep the same five nominal statuses, so
the stronger issue is consumer behavior, not just taxonomy drift. Follow-up
direction after review: keep the five statuses, but make `/create-story`
responsible for choosing `Draft`, `Pending`, or `Blocked` based on repo reality,
and make `/build-story` responsible for promoting or blocking based on fresh
exploration evidence. Next: patch the affected skills/docs so the workflow
becomes problem-first instead of backlog-first.
20260404-1605 - review refinement: widened the planned fix after checking the
actual triage surfaces against the execution ideal. The story now covers not
just story-lifecycle semantics but also meta-triage weighting: existing
Draft/Pending stories should not get major priority just because they exist,
while continuity bias should remain for active or recently advanced work lines
with an unresolved success surface. Also added the missing template-level
requirement so blocked stories have a canonical place to record blocker
evidence and unblock conditions instead of relying on ad-hoc notes. Evidence:
`/triage` currently synthesizes cross-domain recommendations in
`.agents/skills/triage/SKILL.md`, but Story 190 had only scoped
`triage-stories`; the story template also lacked a canonical blocked-story
surface. Added follow-on requirement: keep a living migration runbook while
implementing Story 190 so the final pattern can be handed to other repos
without replaying false starts. Next: implement the weighting, template, and
migration-document changes alongside the story-lifecycle fixes.
20260404-1625 - triple-check review: tightened the story again after comparing
it against the execution ideal, the graph-first methodology reference, and the
remaining workflow consumers. Two more leak paths were still open: `/validate`
still preferred `Rescope then close` in cases that should remain one coherent
story, and the story only required paper-clean graph checks rather than
concrete behavior certification. The story now scopes `/validate`, requires a
behavior-certification matrix, and pushes blocked-story truth toward canonical
template/graph visibility instead of hidden notes. Evidence: `AGENTS.md`
already points toward coherent scope expansion and low process overhead, while
`.agents/skills/validate/SKILL.md` still taught the older close-out bias.
Next: implement the remaining consumer, template, compiler, and certification
changes as one coherent methodology pass.
20260404-1640 - UI-slice refinement: added one more story-creation rule after
reviewing a recurring failure mode in user-facing work. The story now requires
`/create-story` to bias toward whole usable slices when functionality needs a UI
to actually be used or inspected, instead of normalizing user-facing work into
backend-only stories by default. Evidence: repeated repo stories have advanced
plumbing without carrying the operator surface needed to make the capability
real. Next: implement the create-story and template guidance so UI-needed work
is story-shaped honestly.
20260404-1648 - build-story exploration: verified that Story 190 is honestly
buildable under the current repo substrate and replaced the broad pre-build plan
with an implementation-ordered one. Fresh graph evidence shows `Draft 1`,
`Pending 1`, and `In Progress 4` on 2026-04-04, with Story 190 as the only
`Pending` story. That corrects the stale `Pending 0` notes already in this
story and reinforces the same conclusion: `Pending` exists, but it is still not
functioning as an active stable queue. Fresh skill inspection confirmed the
exact leak path the story needs to repair: `build-story` still hard-stops on
Draft, `triage-stories` still treats Draft/Pending shells as recommendable
backlog objects, `validate` still prefers `Rescope then close` once work moves
to follow-up stories, `mark-story-done` still reinforces that closeout bias,
and the story template still has no canonical blocked-story fields. The current
baseline against this story's 9-scenario certification matrix is 2 clear passes
(`Draft`, `Pending`), 1 partial (`Blocked` exists but is not yet canonicalized
through the template/graph), and 6 failures (UI-complete story shaping, Draft
promotion in `/build-story`, blocker transition in `/build-story`,
problem-first continuity weighting in `/triage`, and the closeout defaults in
`/validate` and `/mark-story-done`). Critical substrate verified: all touched
workflow files, the graph compiler, the graph test file, and the migration
runbook already exist locally, so there is no prerequisite blocker. Pattern to
follow: keep the change narrow and synchronized across docs, skills, template,
and compiler/test truth rather than fixing one consumer in isolation. Small
coherent scope delta accepted into the plan: if blocked-story metadata becomes
canonical graph truth, update the long-lived methodology reference wording too,
but do not widen the story beyond workflow consumers and graph-state truth.
Next: wait for approval, then move Story 190 to `In Progress` and implement the
consumer/template/compiler changes in one pass.
20260404-1650 - planning artifact validation: regenerated
`docs/methodology/graph.json` and `docs/stories.md` after the planning edits and
ran `make methodology-check` to confirm the story still compiles cleanly inside
the graph/state workflow. Evidence: `make methodology-compile` rewrote the
compiled graph and story index without error, and `make methodology-check`
reported the graph current. Impact: the implementation plan is now recorded in
the story and verified against the live methodology surfaces before any code or
skill behavior changes begin. Next: hold at the human gate and start the
implementation pass only if approved.
20260404-1702 - implementation pass: landed the coordinated workflow repair
across story creation, triage, build, validation, close-out, repo policy, and
graph truth surfaces. Patched `.agents/skills/triage/SKILL.md`,
`.agents/skills/triage-stories/SKILL.md`,
`.agents/skills/create-story/SKILL.md`,
`.agents/skills/create-story/templates/story.md`,
`.agents/skills/build-story/SKILL.md`,
`.agents/skills/validate/SKILL.md`,
`.agents/skills/mark-story-done/SKILL.md`, `AGENTS.md`,
`docs/methodology-ideal-spec-compromise.md`, `scripts/methodology_graph.py`,
and `tests/test_methodology_graph.py`. Also ran `make skills-sync` so the
cross-CLI wrappers stayed current. Impact: the repo now treats story shells as
packaging instead of priority signals, keeps same-surface work together by
default, allows honest `Draft` / `Pending` / `Blocked` assignment at creation
time, promotes buildable Drafts during `/build-story`, and makes blocked-story
truth inspectable through both the story template and the compiled graph. Next:
rebuild generated artifacts, inspect the graph/index and landed skill text, and
run the targeted methodology checks.
20260404-1703 - verification and artifact inspection: completed the required
methodology and agent-tooling checks after the last functional edit and manually
inspected the generated graph/index plus representative skill text. Commands:
`make methodology-compile`, `make methodology-check`, `make skills-check`,
`python -m pytest tests/test_methodology_graph.py -q`,
`python -m ruff check scripts/methodology_graph.py tests/test_methodology_graph.py`,
and `git diff --check` all passed in this pass. Artifact inspection: opened
`docs/methodology/graph.json` to confirm blocked-story fields now exist in the
compiled story truth, opened `docs/stories.md` to confirm Story 190 is listed as
`In Progress` under `spec:8`, and re-opened the landed `build-story`,
`create-story`, and `validate` skill text to confirm the new Draft-promotion,
problem-first, and keep-open semantics are actually present in the repo. Impact:
the build phase is now complete with fresh evidence and a certified
behavior-matrix record inside the story. Next: hand off to `/validate`.
20260404-1706 - full repo validation: ran the generic repo validation targets
from `/build-story` in addition to the story-scoped methodology checks. Evidence:
`make lint` passed cleanly, and `make test` passed with `456 passed` and `4`
warnings, all from existing `PydanticDeprecatedSince20` notices in
`modules/portionize/portionize_headers_numeric_v1/main.py`. Impact: Story 190's
workflow change is now backed not only by the targeted methodology tests but by
the full current repo test suite as well. Next: `/validate`.
20260404-1712 - review-gap repair: addressed the last workflow hole found during
post-build review. Evidence: `.agents/skills/create-story/SKILL.md` now has an
explicit stop-before-bootstrap branch when the requested work still belongs to
the same subsystem, validation boundary, and success surface as an existing
story, and `docs/runbooks/migrate-problem-first-triage-and-story-workflow.md`
now teaches the same no-new-ID rule for cross-repo adoption. Impact: the
anti-fragmentation rule is now enforced at story creation time instead of being
advisory only, which closes the remaining path that could still mint a serial
micro-story after the rest of this workflow landed. Next: regenerate the graph
and story index, rerun the touched checks, and hand the story back to
`/validate`.
20260404-1718 - certification-count cleanup: corrected the remaining stale
scenario-count wording after the no-new-ID case was added to the certification
matrix. Evidence: `docs/runbooks/migrate-problem-first-triage-and-story-workflow.md`
and this story's `## Plan` now both refer to all 10 certified scenarios instead
of the old nine-scenario count. Impact: the cross-repo migration doc and the
local plan no longer disagree with the actual matrix shape, which removes one
more source of avoidable confusion for future agents. Next: rebuild the
generated methodology artifacts, rerun the touched checks, and complete the
final review pass.
20260404-1720 - close-out: completed `/validate` and `/mark-story-done` for
Story 190 and converted the record from active build state to archived done
state. Evidence: this pass re-reviewed the full diff and untracked files, then
re-ran `make lint`, `make test`, `make methodology-compile`,
`make methodology-check`, `make skills-check`,
`python -m pytest tests/test_methodology_graph.py -q`,
`python -m ruff check scripts/methodology_graph.py tests/test_methodology_graph.py`,
and `git diff --check`; all passed, with only the pre-existing
`PydanticDeprecatedSince20` warnings in
`modules/portionize/portionize_headers_numeric_v1/main.py`. Impact: the story is
now formally `Done`, the workflow gates reflect the completed validation and
close-out path, and the archived story text no longer carries stale present-tense
notes about the intermediate graph state. Next: `/check-in-diff`.
