---
title: "Establish the First Honest Mixed-Archive Intake/Routing Seam"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #1 (Ingest), Requirement #2 (Detect), Requirement #6 (Validate), Any format, any condition, Transparency over magic"
spec_refs:
  - "spec:1"
  - "spec:1.1"
  - "spec:6"
  - "spec:7"
  - "spec:8"
  - "spec:9"
adr_refs:
  - "ADR-002"
depends_on: []
category_refs:
  - "spec:1"
  - "spec:6"
  - "spec:7"
  - "spec:8"
  - "spec:9"
compromise_refs:
  - "C2"
  - "B10"
input_coverage_refs:
  - "mixed-archive"
architecture_domains:
  - "intake_and_routing"
roadmap_tags:
  - "campaign:maintained-intake-honesty"
legacy_system: ""
---

# Story 205 — Establish the First Honest Mixed-Archive Intake/Routing Seam

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/stories/story-194-office-intake-recommendation-and-handoff-boundary.md`, `docs/stories/story-200-web-page-direct-entry-seam.md`, `docs/stories/story-202-eml-direct-entry-seam.md`, `docs/stories/story-203-mbox-archive-seam.md`, `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, `modules/intake/intake_plan_utils.py`, `modules/intake/run_dispatch_v1/main.py`, `benchmarks/scripts/intake_scope.py`, and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower mixed-archive routing ADR or runbook
**Depends On**: None

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

`mixed-archive` is now the last fully untested input family in the coverage
matrix. The repo already owns bounded maintained lanes for `pdf`,
`images_dir`, `docx`, `xlsx`, `pptx`, `epub`, `web-page`, `.eml`, and `.mbox`,
but it still has no archive/folder inventory surface, no repo-owned mixed
archive fixture, and no inspectable routing seam that can unpack a ZIP or
mixed folder, preserve archive-relative provenance, and hand each member to an
existing maintained recipe or an explicit blocked/no-recipe outcome. This
story should determine the first honest mixed-archive slice: either land a
bounded archive-manifest + per-member handoff seam on one repo-owned fixture,
or stop with an explicit blocker instead of letting `mixed-archive` remain an
implicit future promise.

## Acceptance Criteria

- [x] A fresh current-pass baseline names the exact mixed-archive gap from repo
      evidence:
  - [x] the work log captures that
        `tests/fixtures/formats/_coverage-matrix.json` starts this pass with
        `mixed-archive` marked `untested`
  - [x] the work log records that `schemas.py` / `driver.py` expose no
        `input_archive` / `input_zip` / `--input-archive` surface, and that
        current maintained overrides stop at `pdf`, `images_dir`, `docx`,
        `xlsx`, `pptx`, `epub`, `html`, `.eml`, and `.mbox`
  - [x] the work log cites the verified absence of a repo-owned mixed-archive
        fixture, archive manifest schema/module, and archive unpack/router lane
        before implementation
  - [x] the work log records the existing reusable substrate honestly:
        bounded direct-entry recipes already exist for several member families,
        `prepare_confirmed_handoff(...)` already emits inspectable per-run
        handoff rows, and `zipfile` use in the repo is currently EPUB-specific
        rather than a general archive-routing substrate
- [x] The story either lands one bounded mixed-archive slice or closes
      `Blocked` honestly:
  - [x] one repo-owned mixed archive fixture exists under `testdata/` with
        capture/generation notes in `testdata/README.md`
  - [x] the chosen shipping slice emits an inspectable archive/member manifest
        with archive-relative member identity, detected input kind or route
        decision, and explicit terminal status per member
  - [x] if dispatch is part of the slice, at least one member launches into an
        existing maintained recipe through `driver.py`, and at least one
        member-level blocked/skip/out-of-scope outcome is inspectable when the
        fixture warrants it
  - [x] explicit blocker path not needed; the bounded ZIP slice proved viable
        on the repo-owned fixture instead of requiring a `Blocked` close
- [x] Mixed-archive provenance stays source-honest on the claimed slice:
  - [x] archive-relative paths or member IDs remain inspectable end to end
  - [x] no fabricated page anchors, recursive attachment guarantees, or broad
        “supports any archive” claims are introduced
  - [x] any new fields that cross artifact boundaries are added to
        `schemas.py` before stamped artifacts rely on them
- [x] Coverage, docs, and routing-boundary surfaces remain aligned with the
      outcome:
  - [x] `tests/fixtures/formats/_coverage-matrix.json`, `README.md`,
        `docs/RUNBOOK.md`, and `testdata/README.md` reflect the exact supported
        mixed-archive slice rather than a vague archive promise
  - [x] recommendation-only intake and approved-handoff boundaries only change
        if the story ships fresh current-pass proof that they should
  - [x] handwritten OCR, mailbox/thread ownership, attachment extraction,
        nested archives, and broad archive-wide normalization remain explicitly
        out of scope unless fresh evidence justifies separate follow-up work

## Out of Scope

- Recursive nested archives, attachments, or archive-of-archives handling
- Direct folder input; the first bounded candidate slice is ZIP-only unless
  fresh evidence during implementation proves that broader entry surface is
  still coherent and low-risk
- Broad “any ZIP/folder” ownership beyond one bounded repo-owned fixture
- Reopening Story 191 or changing handwritten OCR/runtime behavior
- Gmail / mailbox connector workflows, multi-message thread reconstruction, or
  mailbox graph semantics beyond already-bounded `.eml` / `.mbox` seams
- Expanding recommendation-only contact-sheet intake or approved handoff unless
  fresh proof shows mixed-archive belongs there
- New `doc-web` output-contract architecture beyond the minimum inspectable
  archive/member artifacts needed to prove the bounded slice

## Approach Evaluation

- **Simplification baseline**: measured in this pass on a scratch ZIP built
  from repo-owned fixtures at `testdata/docx-mini.docx`,
  `testdata/email-eml-mini.eml`, `testdata/web-page-mini.html`, and
  `README.md`. Deterministic suffix routing over the unpacked member list
  already produced `3/4` launchable members (`docx`, `email-eml`, `web-page`)
  and `1/4` explicit blocked (`.txt`) with no AI involved. That is enough
  evidence to treat a ZIP-only first slice as a pure orchestration problem
  unless the checked-in fixture later introduces ambiguous members.
- **AI-only**: wrong first move on the bounded candidate slice. Letting a
  model reason over raw archive bytes or member content would hide provenance,
  add cost, and re-solve deterministic suffix-to-recipe decisions the repo
  already owns for several direct-entry families.
- **Hybrid**: keep only as a fallback. If the chosen fixture later needs
  ambiguous PDF handling, grouped image-member interpretation, or another case
  where suffix routing is not enough, introduce AI only for that narrow member
  decision surface.
- **Pure code**: current front-runner. The real missing seam is inspectable ZIP
  inventory plus member-to-recipe/blocked routing and launch plumbing, not
  language understanding.
- **Repo constraints / prior decisions**: `spec:1.1` keeps recipe ownership
  explicit under `C2`; ADR-002 keeps the accepted `doc-web` boundary
  inspectable; Story 194 deliberately kept recommendation-only and
  approved-handoff surfaces narrower than explicit direct-entry lanes; Stories
  200/202/203 proved that bounded direct-entry seams can land honestly without
  widening automation claims; `docs/methodology/state.yaml` now explicitly says
  intake/routing should wait for a fresh substrate such as mixed-archive
  routing rather than busy cleanup.
- **Existing patterns to reuse**: `driver.py` and `RunConfig` input overrides;
  `modules/intake/intake_plan_utils.py`; `modules/intake/run_dispatch_v1`;
  `benchmarks/scripts/intake_scope.py`; direct-entry recipe patterns from
  Stories 200/202/203; `modules/extract/mailbox_mbox_intake_v1/main.py` for
  archive/member metadata discipline; `contact_sheet_manifest_v1` as an example
  of an inspectable intake manifest; and the EPUB intake module's bounded
  `zipfile` handling as a concrete unpacking example.
- **Eval**: the deciding proof surface is now concrete. A fresh `driver.py`
  run on one repo-owned ZIP fixture should emit an inspectable archive/member
  manifest plus member route rows, launch at least one maintained direct-entry
  recipe through `driver.py`, and leave at least one blocked member row that
  stays archive-relative and inspectable. If the bounded ZIP fixture still
  shows ambiguity that suffix routing cannot resolve, add a focused mixed-
  archive routing truth surface before widening beyond the pure-code plan.

## Tasks

- [x] Freeze the current mixed-archive gap from repo reality:
  - [x] verify the `mixed-archive` coverage row is still `untested`
  - [x] verify there is still no repo-owned mixed archive fixture, no archive
        manifest schema/module, and no `input_archive` / `input_zip` driver
        surface
  - [x] record which maintained direct-entry families and automation boundaries
        already exist so the story does not overbuild routing logic that the
        repo already owns
- [x] Add one repo-owned bounded mixed-archive fixture under `testdata/` plus
      capture/generation notes in `testdata/README.md`
- [x] Measure the smallest honest baseline before building routing logic:
  - [x] deterministic ZIP unpack/inventory on the chosen fixture using stdlib
        `zipfile`
  - [x] inspect whether current maintained recipes plus
        `prepare_confirmed_handoff(...)` or sibling helper logic can already
        represent per-member launched/blocked outcomes
  - [x] no LLM probe was needed because the bounded fixture routed honestly by
        deterministic suffix and existing direct-entry recipe ownership
- [x] Decide the smallest honest shipping slice:
  - [x] ZIP-only archive/member manifest plus per-member route rows and bounded
        dispatch into existing maintained direct-entry recipes
  - [x] keep mixed-folder input, ambiguous PDF routing, and grouped image-member
        semantics explicitly out of scope unless the bounded fixture proves they
        are already solved
  - [x] explicit blocker path was not needed because unsupported members stay
        inspectable as blocked rows on the bounded fixture
- [x] If a bounded seam is viable, land the smallest coherent implementation:
  - [x] add a ZIP-specific run-config / driver input only if a maintained
        archive entry surface is justified
  - [x] add the minimum archive unpack/inventory substrate and any bounded
        routing helper
  - [x] preserve archive-relative member provenance and explicit terminal
        status per member instead of fabricating a flat single-document output
- [x] Add focused fixture-backed coverage for the chosen seam, including any
      new archive manifest contract and routing truth-surface tests
- [x] If this story changes documented format coverage or graduation reality: update `tests/fixtures/formats/_coverage-matrix.json` and any relevant methodology state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect archive/member JSON/JSONL plus representative downstream artifacts
  - [x] If agent tooling changed: `make skills-check` was not needed because no agent tooling changed
- [x] If evals or goldens changed: no eval or golden changes were needed
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: archive/member provenance is inspectable end to end
  - [x] T1 — AI-First: AI is only introduced if it improves routing beyond the
        measured baseline
  - [x] T2 — Eval Before Build: baseline routing approaches are measured before
        new archive glue lands
  - [x] T3 — Fidelity: no member is silently dropped, merged, or mislabeled
  - [x] T4 — Modular: reuse existing maintained recipes instead of inventing
        new per-format runtime paths
  - [x] T5 — Inspect Artifacts: archive manifest, handoff rows, and
        representative downstream artifacts are manually opened and checked

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

- **Owning module / area**: intake and routing. The likely shape is a new
  ZIP unpack/inventory stage plus a bounded member routing/dispatch stage that
  reuses existing direct-entry recipe seams, not a new `doc-web` runtime
  boundary.
- **Methodology reality**: this work belongs primarily to `spec:1`, with
  supporting ties to `spec:6`, `spec:7`, `spec:8`, and `spec:9`. In the
  current repo state, `spec:1` substrate exists and `C2` / `B10` remain
  `climb`; `spec:7` remains `partial`; and the coverage row has now moved from
  `untested` to a bounded `passing` claim for the ZIP-only mixed-archive seam.
  The story started `Draft` because no archive-manifest/routing substrate had
  been verified. That gap is now closed for the checked-in ZIP fixture and
  explicit direct-entry member families this story owns.
- **Substrate evidence**: verified reusable routing substrate in code:
  `RunConfig` and `driver.py` now support `input_zip` / `--input-zip` in
  addition to the existing `pdf`, `images_dir`, `docx`, `xlsx`, `pptx`,
  `epub`, `html`, `.eml`, and `.mbox` entry surfaces; direct-entry-only
  families remain encoded in `benchmarks/scripts/intake_scope.py` and
  `modules/intake/intake_plan_utils.py`; `run_dispatch_v1` still proves the
  nested `driver.py` launch pattern; and the new `archive_unpack_manifest_v1`
  plus `archive_route_members_v1` modules now own the bounded archive-member
  inventory and routing seam. The remaining intentional gap is broader archive
  ownership: no direct folder input, no nested archives, and no PDF/image-
  member ambiguity handling are claimed here.
- **Data contracts / schemas**: likely touched contracts are `RunConfig` in
  `schemas.py`, a new archive/member manifest schema, and a new archive-member
  route/handoff schema if the seam lands. Reusing `intake_handoff_v1` directly
  is optional; a sibling schema is more likely because archive-member identity
  needs to stay first-class. Any new archive/member fields must be added to
  `schemas.py` before stamped artifacts rely on them.
- **File sizes**: likely touch points are `schemas.py` (1308 lines, >500),
  `driver.py` (3121, >500), `modules/intake/intake_plan_utils.py` (345),
  `README.md` (444), `docs/RUNBOOK.md` (725, >500),
  `tests/fixtures/formats/_coverage-matrix.json` (534, >500),
  `tests/test_run_config.py` (56), and `tests/test_intake_plan_utils.py`
  (283). Likely new files are a ZIP fixture, a mixed-archive recipe, archive
  inventory/routing modules, and focused recipe/helper tests. Keep edits
  especially surgical in the oversized files.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`,
  `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002,
  Stories 194/200/202/203, `tests/fixtures/formats/_coverage-matrix.json`,
  `README.md`, `docs/RUNBOOK.md`, `modules/intake/intake_plan_utils.py`,
  `modules/intake/run_dispatch_v1/main.py`,
  `modules/extract/mailbox_mbox_intake_v1/main.py`,
  `modules/extract/unstructured_epub_intake_v1/main.py`,
  `benchmarks/scripts/intake_scope.py`, `modules/common/office_native_bundle.py`,
  and the focused email/mbox recipe tests. No narrower mixed-archive ADR,
  runbook, scout, or note was found after search.

## Files to Modify

- `schemas.py` — add a ZIP-specific run-config field plus
  `archive_member_manifest_v1` / `archive_member_route_v1` style schemas if the
  maintained slice lands (1308 lines)
- `driver.py` — add `--input-zip` / similar override plumbing for the bounded
  ZIP-only entry surface if the seam becomes maintained (3121 lines)
- `modules/intake/intake_plan_utils.py` — add or extract archive-member launch
  helpers so direct-entry recipe maps and launch-flag resolution are not copied
  into a second place (345 lines)
- `tests/test_run_config.py` — add ZIP-input coverage if the run-config surface
  grows (56 lines)
- `tests/test_intake_plan_utils.py` — cover archive-member routing/launch truth
  if shared helpers land here (283 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — move the `mixed-archive`
  row only as far as fresh ZIP-slice evidence justifies (534 lines)
- `README.md` — align user-facing support wording with the exact bounded
  mixed-archive ZIP slice if one lands (444 lines)
- `docs/RUNBOOK.md` — document the verified mixed-archive ZIP command or blocker
  outcome if the seam lands (725 lines)
- `testdata/README.md` — record fixture source and generation/capture notes
  for the chosen mixed archive ZIP fixture (122 lines)
- `testdata/mixed-archive-mini.zip` / `testdata/mixed-archive-mini.source.json`
  — repo-owned bounded mixed archive ZIP fixture and scope metadata (new files)
- `configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml` — bounded
  mixed-archive ZIP recipe only if the seam becomes maintained (new file)
- `modules/intake/archive_unpack_manifest_v1/main.py` and `module.yaml` —
  inspectable ZIP/member inventory substrate or clearly superior bounded
  successor (new files)
- `modules/intake/archive_route_members_v1/main.py` and `module.yaml` — member
  routing / dispatch helper for the bounded ZIP slice if baseline evidence says
  it is justified (new files)
- `tests/test_mixed_archive_zip_recipe.py` and/or focused sibling tests —
  fixture-backed recipe smoke plus archive/member truth-surface assertions for
  the bounded ZIP slice (new file[s])

## Redundancy / Removal Targets

- ad hoc local mixed-archive probe commands once a maintained archive fixture
  and routing seam exist
- any temptation to widen `.mbox` or other archive-family stories into generic
  mixed-archive ownership instead of keeping the new seam explicit
- overly vague “future archive routing” wording in docs once the first bounded
  slice or blocker is recorded honestly

## Notes

- New story justification: expanding Story 203 would not be honest because that
  story closed a bounded plain-text `.mbox` lane with one message-per-entry
  bundle proof, not a cross-family archive unpack/router seam. Expanding Story
  194 would also blur a closed automation-boundary decision with a new
  substrate problem. Mixed-archive routing is a different subsystem slice with
  a new fixture shape, new provenance requirements, and a different validation
  surface.
- Fresh exploration resolves the first candidate slice narrowly: start with one
  repo-owned ZIP archive containing nested member paths from already-maintained
  direct-entry families plus one intentionally unsupported file. Keep direct
  folder input and ambiguous PDF/image-member grouping out of scope unless the
  bounded ZIP implementation proves those broader cases are already coherent.
- The current likely value is not “archive rendering” but explicit member-level
  routing into already-maintained lanes. The story should resist inventing a
  second parallel runtime when reuse is possible.

## Plan

Alignment check:
- This story still moves toward the Ideal rather than away from it. It closes a
  real remaining `spec:1.1` / `C2` input-family gap, keeps the accepted
  `doc-web` boundary unchanged under ADR-002, and does not widen the
  recommendation-only intake or approved-handoff automation surfaces.
- No narrower mixed-archive ADR or runbook was found in this pass.

Measured baseline from this exploration pass:
- **Current repo coverage baseline: 0/1.** `mixed-archive` is still `untested`
  in the coverage matrix; there is no repo-owned mixed archive fixture, no
  archive manifest schema/module, and no `input_archive` / `input_zip`
  runtime surface.
- **Current reusable routing substrate baseline: buildable.** `RunConfig` and
  `driver.py` already support `pdf`, `images_dir`, `docx`, `xlsx`, `pptx`,
  `epub`, `html`, `.eml`, and `.mbox`; `modules/intake/intake_plan_utils.py`
  already centralizes maintained and direct-entry recipe knowledge; and
  `run_dispatch_v1` already proves the nested `driver.py` launch pattern.
- **Scratch ZIP routing baseline: 3/4 launchable, 1/4 blocked.** A temporary
  ZIP built from repo-owned fixtures with nested members
  (`docs/reference.docx`, `mail/message.eml`, `web/snapshot.html`,
  `notes/readme.txt`) routed cleanly by suffix to `docx`, `email-eml`, and
  `web-page`, while `.txt` stayed explicitly blocked. That is enough evidence
  that AI is not required on the first bounded slice.
- **Archive-substrate baseline: partial patterns, no general seam.**
  `mailbox_mbox_intake_v1` proves inspectable archive/member metadata patterns
  and `unstructured_epub_intake_v1` proves bounded stdlib `zipfile` unpacking,
  but neither provides a heterogeneous member manifest or route/dispatch helper.
- **Helper-boundary surprise:** `prepare_confirmed_handoff(...)` is not the
  final mixed-archive answer. It only launches maintained PDF/image flows and
  explicitly blocks direct-entry-only recipes. The first mixed-archive slice
  therefore needs a sibling archive-member routing helper rather than pretending
  the contact-sheet handoff path already solves heterogeneous ZIP contents.

Approach choice after the fresh baseline:
- **AI-only** is not justified for the first pass. The measured gap is archive
  inventory plus member launch/block wiring, not content understanding.
- **Hybrid** should stay a fallback only for future ambiguous member kinds such
  as PDFs or grouped image sets.
- **Pure code** is the current front-runner for a ZIP-only first slice with
  already-maintained direct-entry member families and one explicit blocked
  unsupported member.

Implementation order:
1. **Freeze the bounded ZIP fixture (`S`)**
   - Files: `testdata/mixed-archive-mini.zip`,
     `testdata/mixed-archive-mini.source.json`, `testdata/README.md`
   - Change: check in one repo-owned ZIP archive with nested member paths from
     already-maintained direct-entry families and at least one intentionally
     unsupported member. Recommended shape: one `docx`, one `.eml`, one checked
     HTML snapshot, and one `.txt`.
   - Done looks like: the repo owns a stable ZIP fixture whose member mix
     proves both launchable and blocked outcomes without introducing ambiguous
     PDF or grouped-image semantics.
2. **Add the bounded ZIP entry + manifest substrate (`M`)**
   - Files: `schemas.py`, `driver.py`,
     `configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml`,
     `modules/intake/archive_unpack_manifest_v1/main.py`,
     `modules/intake/archive_unpack_manifest_v1/module.yaml`,
     `tests/test_run_config.py`
   - Change: add a ZIP-specific input surface (`input_zip` / `--input-zip`, or
     a clearly justified equally narrow name) plus a first-stage inventory
     module that unpacks the archive under the run directory and emits one
     inspectable manifest row per member with archive-relative path, extracted
     path, suffix, and stable member identity.
   - Risks: `driver.py` and `schemas.py` are already large, so keep the new
     input surface surgical and avoid implying folder support.
   - Done looks like: a real run can accept the ZIP fixture and produce a
     stamped archive/member manifest before any downstream recipe launches.
3. **Add member routing + bounded dispatch (`M`)**
   - Files: `modules/intake/intake_plan_utils.py`,
     `modules/intake/archive_route_members_v1/main.py`,
     `modules/intake/archive_route_members_v1/module.yaml`,
     `tests/test_intake_plan_utils.py`, and focused new route-module tests if
     needed
   - Change: centralize a suffix-to-input-kind / recipe helper that reuses the
     repo's existing maintained and direct-entry recipe tables, then emit one
     route row per archive member with explicit terminal outcome. Launch
     supported direct-entry members through `driver.py` and leave unsupported
     members blocked with inspectable reasons.
   - Risks: avoid copying recipe maps into a second subsystem and avoid using
     generic `intake_handoff_v1` if that would hide archive-member identity.
   - Done looks like: the route artifact shows at least one launched maintained
     member and at least one blocked member while preserving archive-relative
     provenance.
4. **Add focused fixture-backed proof (`S`)**
   - Files: `tests/test_mixed_archive_zip_recipe.py` and any small focused
     helper/module tests required
   - Change: add a smoke test that runs the new mixed-archive ZIP recipe on the
     checked-in fixture and asserts the archive/member manifest, route rows, and
     representative downstream artifact paths.
   - Done looks like: regressions in ZIP inventory, route decisions, or member
     launch wiring fail cheaply before a full manual proof run.
5. **Align docs and coverage truth (`S`)**
   - Files: `tests/fixtures/formats/_coverage-matrix.json`, `README.md`,
     `docs/RUNBOOK.md`, `testdata/README.md`
   - Change: document the exact bounded ZIP slice and keep folder input,
     ambiguous PDFs, grouped image members, nested archives, and broader archive
     ownership explicitly out of scope unless fresh proof changes that.
   - Expected coverage movement: if the maintained ZIP lane lands with fresh run
     proof and manual inspection, `mixed-archive` can move from `untested` to a
     bounded supported state with explicit known gaps. If the proof surface
     stalls at manifest-only or reveals unresolved ambiguity, keep the coverage
     row narrower or stop at a blocker instead of overstating support.
6. **Validation (`M`)**
   - Checks: `make test`, `make lint`
   - Real-run proof: clear stale `*.pyc`, run the new ZIP recipe through
     `driver.py`, inspect the archive/member manifest and route rows, and open
     at least one nested downstream output plus one blocked row.
   - Done looks like: the story has fresh current-pass evidence for the new ZIP
     seam and does not rely on logs alone.

Impact analysis:
- Recommendation-only intake and approved-handoff automation should stay
  untouched unless the implementation unexpectedly proves mixed-archive belongs
  there. The current plan assumes no benchmark-surface changes.
- The main blast radius is `driver.py`, `schemas.py`, and any shared helper
  extraction from `modules/intake/intake_plan_utils.py`.
- The main correctness risk is provenance drift: every route row must retain
  archive-relative member identity and point to the exact extracted member path
  or downstream run path that belongs to that member.

Structural health notes:
- Keep the first slice ZIP-only. A generic `input_archive` or folder-support
  surface would overclaim the verified substrate in this pass.
- Prefer a sibling archive-member route schema over stretching
  `intake_handoff_v1` if the older shape obscures archive-member identity.
- Reuse the existing recipe tables in `modules/intake/intake_plan_utils.py`
  rather than hardcoding new maps inside the archive module.

Recommended scope adjustments folded into the story now:
- The first candidate slice is explicitly ZIP-only rather than “ZIP or folder.”
- The first maintained fixture should avoid PDFs and grouped image members so
  the story measures routing glue instead of reopening ambiguity the repo has
  not solved.

Human-approval blockers:
- Recommended naming choice: use `input_zip` / `--input-zip` rather than a
  broader `input_archive` surface to keep the claim honest.
- Recommended execution choice: launch supported members through `driver.py`
  inside the routing stage instead of stopping at manifest-only, because the
  story already has enough substrate to prove at least one real downstream
  launch on the bounded slice.

Story status recommendation:
- The user approved the ZIP-only plan and the story was promoted before code
  changes started.
- Keep the story `In Progress` until `/validate` rechecks the post-fix tree and
  `/mark-story-done` closes the line.

## Work Log

20260409-1726 — story creation from `/triage`: created Story 205 after the user approved the recommended next action. Evidence reviewed in this pass: `tests/fixtures/formats/_coverage-matrix.json` still marks `mixed-archive` `untested`; `schemas.py` / `driver.py` expose maintained overrides for `pdf`, `images_dir`, `docx`, `xlsx`, `pptx`, `epub`, `html`, `.eml`, and `.mbox` but nothing for a general archive input; `benchmarks/scripts/intake_scope.py` and `modules/intake/intake_plan_utils.py` show that current automation truth stops at `pdf` / `images_dir` plus direct-entry-only families; and the only repo `zipfile` use is the EPUB-specific path in `modules/extract/unstructured_epub_intake_v1/main.py`. Result: a new story is honest, but it must start `Draft` rather than `Pending` because the archive-manifest/routing substrate is still missing in implemented reality. Next step: `/build-story` should choose one repo-owned mixed archive fixture, freeze the routing baseline, and decide whether archive-manifest + explicit per-member handoff is viable or blocked.
20260409-1738 — /build-story exploration + plan: re-read `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, Stories 194/200/202/203, the `mixed-archive` coverage row, `README.md`, `docs/RUNBOOK.md`, `schemas.py`, `driver.py`, `modules/intake/intake_plan_utils.py`, `modules/intake/run_dispatch_v1/main.py`, `benchmarks/scripts/intake_scope.py`, `modules/extract/mailbox_mbox_intake_v1/main.py`, `modules/extract/unstructured_epub_intake_v1/main.py`, `modules/common/office_native_bundle.py`, and the focused `.eml` / `.mbox` recipe tests. Fresh substrate reality: the repo now already owns direct-entry runtime surfaces for `docx`, `xlsx`, `pptx`, `epub`, `html`, `.eml`, and `.mbox`, plus bounded archive patterns from Story 203; the actual missing seam is not “archive support at all” but a heterogeneous ZIP/member manifest plus route/dispatch helper. Measured baseline: a scratch ZIP assembled from repo-owned fixtures with nested member paths (`docs/reference.docx`, `mail/message.eml`, `web/snapshot.html`, `notes/readme.txt`) routed cleanly by suffix to `3/4` launchable members and `1/4` explicit blocked with no AI, which makes a ZIP-only pure-code first slice honestly buildable. Key surprise: `prepare_confirmed_handoff(...)` cannot launch direct-entry-only recipes, so the story needs a sibling archive-member routing helper rather than pretending the contact-sheet handoff seam already solves this. Small coherent scope delta folded into the story: narrow the first maintained candidate to one repo-owned ZIP fixture with already-maintained direct-entry members plus one unsupported file; keep direct folder input, ambiguous PDFs, grouped image members, nested archives, and broader archive ownership out of scope. Result: the story should remain `Draft` only until the user approves the plan; once implementation begins, it should be promoted to `Pending` before code changes. Next step: wait for human approval, then implement the ZIP fixture, `input_zip` plumbing, archive/member manifest, route rows, focused tests, docs, and real-run proof.
20260409-1818 — implementation + real-run proof: promoted the story to `Pending`, then `In Progress`, and landed the bounded ZIP-only mixed-archive seam across `schemas.py`, `validate_artifact.py`, `driver.py`, `modules/intake/intake_plan_utils.py`, new `archive_unpack_manifest_v1` / `archive_route_members_v1` modules, `configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml`, the checked-in `testdata/mixed-archive-mini.zip` fixture plus metadata, focused tests, and the coverage/docs/state truth surfaces. Fresh checks in this pass: `make methodology-compile`, `make methodology-check`, `make lint`, and focused pytest (`tests/test_mixed_archive_zip_recipe.py`, `tests/test_run_config.py`, `tests/test_intake_plan_utils.py`, plus the direct-entry recipe tests earlier in the pass) all passed. First driver proof on `story205-mixed-archive-zip-smoke` exposed a real integration bug: `archive_route_members_v1` assumed basename `--out` values, but `driver.py` passed a relative artifact path under the default repo output root, so the route artifact landed in the wrong place and stamping failed. Fixed by resolving driver-style relative artifact paths explicitly and added a regression test. Fresh rerun with `python driver.py --recipe configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml --input-zip testdata/mixed-archive-mini.zip --run-id story205-mixed-archive-zip-smoke-v2 --allow-run-id-reuse --force` now succeeds end to end: `archive_members_manifest.jsonl` stamps four archive-relative members (`docs/reference.docx`, `mail/message.eml`, `web/snapshot.html`, `notes/readme.txt`), `archive_member_routes.jsonl` records three launched downstream runs plus one blocked `.txt` row with `unsupported_archive_member_suffix:.txt`, and the inspected downstream bundle manifests show `DOCX Mini Fixture`, `Fixture Subject`, and `Example Domain` content on the launched members. Representative inspected artifacts: `output/runs/story205-mixed-archive-zip-smoke-v2/01_archive_unpack_manifest_v1/archive_members_manifest.jsonl`, `output/runs/story205-mixed-archive-zip-smoke-v2/02_archive_route_members_v1/archive_member_routes.jsonl`, `output/runs/story205-mixed-archive-zip-smoke-v2-member-001-recipe-docx-html-mvp/output/html/chapter-001.html`, `output/runs/story205-mixed-archive-zip-smoke-v2-member-002-recipe-email-eml-html-mvp/output/html/page-001.html`, `output/runs/story205-mixed-archive-zip-smoke-v2-member-003-recipe-web-page-html-mvp/output/html/chapter-001.html`, and the blocked extracted member at `output/runs/story205-mixed-archive-zip-smoke-v2/01_archive_unpack_manifest_v1/extracted_members/notes/readme.txt`. Next step: finish a fresh full `make test` pass on the post-fix tree, then check the remaining story tasks/workflow gate and hand off to `/validate`.
20260409-1826 — final validation refresh: reran `make test` on the exact post-fix tree after adding the route-path regression test and story/docs truth-surface updates. Result: `532 passed, 4 warnings in 676.53s`; the new mixed-archive suite now collects three tests in `tests/test_mixed_archive_zip_recipe.py`, and the only warnings are the pre-existing Pydantic `dict()` deprecation notices in `modules/portionize/portionize_headers_numeric_v1/main.py`. Combined with the already-fresh `make lint`, `make methodology-check`, stamped archive-manifest/route validation, and the inspected `driver.py` proof run, this is enough to mark the build handoff complete while leaving `/validate` and `/mark-story-done` as the remaining workflow gates. Next step: run `/validate` against Story 205, then close it via `/mark-story-done` if the validation sweep agrees with the current evidence.
20260410-0024 — `/mark-story-done` close-out: rechecked Story 205 against `docs/ideal.md`, `docs/spec.md`, ADR-002, the updated story body, and the current diff after `/validate`. Fresh evidence used for close-out in this sequence: `make lint` passed, `make methodology-check` passed, `make test` passed (`532 passed, 4 warnings`), and `python driver.py --recipe configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml --input-zip testdata/mixed-archive-mini.zip --run-id validate-story205-mixed-archive-zip --allow-run-id-reuse --force` produced a fresh bounded ZIP proof run. Manual inspection in this close-out sequence reconfirmed `output/runs/validate-story205-mixed-archive-zip/01_archive_unpack_manifest_v1/archive_members_manifest.jsonl`, `output/runs/validate-story205-mixed-archive-zip/02_archive_route_members_v1/archive_member_routes.jsonl`, `output/runs/validate-story205-mixed-archive-zip-member-001-recipe-docx-html-mvp/output/html/chapter-001.html`, `output/runs/validate-story205-mixed-archive-zip-member-002-recipe-email-eml-html-mvp/output/html/page-001.html`, `output/runs/validate-story205-mixed-archive-zip-member-003-recipe-web-page-html-mvp/output/html/chapter-001.html`, and the blocked member at `output/runs/validate-story205-mixed-archive-zip/01_archive_unpack_manifest_v1/extracted_members/notes/readme.txt`. Minor close-out fixes applied here: refreshed the stale planning-era `Architectural Fit` prose so it matches the landed `input_zip` seam and bounded `passing` coverage claim, and updated methodology state so Story 205 is recorded as a completed bounded proof line rather than an active build line. Result: Story 205 now closes honestly as the first maintained ZIP-only mixed-archive routing seam, while broader archive ownership remains explicitly separate future work. Next step: `/check-in-diff`.
