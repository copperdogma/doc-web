---
title: "Expand the First Honest PDF-Member Approved-Handoff Seam to Direct-Folder Parity and First Maintained-PDF Launch"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #1 (Ingest), Requirement #2 (Detect), Requirement #6 (Validate), Zero configuration, Transparency over magic"
spec_refs:
  - "spec:1"
  - "spec:1.1"
  - "spec:6"
  - "spec:7"
  - "spec:8"
  - "spec:9"
adr_refs:
  - "ADR-002"
depends_on:
  - "176"
  - "180"
  - "196"
  - "205"
  - "221"
  - "222"
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

# Story 223 — Expand the First Honest PDF-Member Approved-Handoff Seam to Direct-Folder Parity and First Maintained-PDF Launch

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/stories/story-176-confirmed-intake-handoff-to-explicit-recipe-runs.md`, `docs/stories/story-180-widen-approved-intake-handoff-image-directory-proof.md`, `docs/stories/story-194-office-intake-recommendation-and-handoff-boundary.md`, `docs/stories/story-196-widen-born-digital-pdf-proof-and-quality-surface.md`, `docs/stories/story-205-mixed-archive-intake-routing-seam.md`, `docs/stories/story-221-mixed-archive-pdf-member-routing-seam.md`, `docs/stories/story-222-mixed-folder-pdf-member-routing-seam.md`, `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, `modules/intake/archive_route_members_v1/main.py`, `modules/intake/intake_plan_utils.py`, `modules/intake/run_dispatch_v1/main.py`, `modules/intake/confirm_plan_v1/main.py`, `configs/recipes/recipe-intake-contact-sheet-confirmed-handoff.yaml`, `tests/test_mixed_archive_zip_recipe.py`, and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower mixed-archive approved-handoff ADR or runbook`
**Depends On**: Stories `176`, `180`, `196`, `205`, `221`, and `222`

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

Story 223 already closed the first honest ZIP-only PDF-member approved-handoff
slice and the direct-folder approved-handoff continuation on the bounded mixed-
archive route/module seam. The remaining same-line delta is now the shared
post-handoff launch bug: on the checked-in born-digital PDF member probes, the
route stage can emit a valid approved plan plus a valid `intake_handoff_v1`
artifact, but `launch` mode still collapses to `pdf_member_handoff_blocked:None`
before the final maintained PDF recipe starts. Under the tightened anti-
fragmentation rule, this first launched-PDF proof belongs here instead of in a
new story because it stays on the same `archive_route_members_v1` plus
member-local `overview_plan_final.jsonl` / `intake_handoff_v1` artifact line.
This reopened story should fix that shared launch-path bug and prove the first
downstream maintained born-digital PDF launch on the checked-in ZIP and
direct-folder probes, while keeping scanned/handwritten PDF-member launch
ownership, broader archive semantics, and top-level automation-surface widening
out of scope.

## Acceptance Criteria

- [x] A fresh current-pass baseline names the exact mixed-archive
      approved-handoff gap from repo evidence:
  - [x] the work log records that
        `tests/fixtures/formats/_coverage-matrix.json`,
        `docs/methodology/state.yaml`, `README.md`, and `docs/RUNBOOK.md`
        still excluded archive-contained approved handoff or final maintained
        PDF launch before this implementation pass
  - [x] the work log records that
        `modules/intake/archive_route_members_v1/main.py` still stopped ZIP
        PDF members at `terminal_reason = pdf_member_recommendation_only`
        before the route change
  - [x] the work log cites the verified reusable substrate honestly: Story
        221's emitted member-local `intake_plan_v1`, Story 176 / Story 180's
        approved-handoff substrate, `modules/intake/confirm_plan_v1/main.py`,
        `modules/intake/run_dispatch_v1/main.py`,
        `modules/intake/intake_plan_utils.py`, and the existing born-digital
        PDF launch path already proven from the emitted plan artifact
- [x] The story lands one bounded ZIP-only approved-handoff slice honestly:
  - [x] the shipping slice stays on the existing repo-owned
        `mixed-archive-pdf-mini.zip` fixture and the existing born-digital PDF
        member; folder parity and scanned/handwritten PDF-member approval stay
        out of scope
  - [x] the chosen slice writes an inspectable route row plus adjacent
        member-local approved-handoff artifact for the PDF member
  - [x] the chosen slice stops at member-local approved handoff, and the
        emitted `intake_handoff_v1` artifact under `output/runs/` is manually
        inspected alongside the approved plan artifact
  - [x] the implementation keeps final maintained PDF launch unclaimed instead
        of silently auto-launching it
- [x] Mixed-archive PDF-member provenance and approval semantics stay
      inspectable on the claimed slice:
  - [x] archive-relative `member_path`, emitted `intake_plan_v1` path,
        `approval_mode`, `intake_handoff_v1`, launch input path, and
        downstream `run_id` remain traceable end to end
  - [x] no archive-wide planner, hidden second AI routing pass, combined
        archive-level HTML bundle, or broader archive/folder launch claim is
        introduced
  - [x] the new route-row fields were added to `schemas.py` before stamped
        artifacts relied on them
- [x] Coverage, eval, and docs truth surfaces remain aligned with the result:
  - [x] `tests/fixtures/formats/_coverage-matrix.json`,
        `docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`, and
        `testdata/README.md` now reflect the exact bounded approved-handoff
        claim rather than a vague archive-PDF automation promise
  - [x] the owning `approved-intake-handoff` eval surface remains top-level
        direct-entry only, so `docs/evals/registry.yaml` did not need a rerun
        or update for this nested archive-route change
  - [x] grouped image-member interpretation, direct-folder parity,
        scanned/handwritten PDF-member approval, nested archives, attachment
        extraction, and broad heterogeneous archive ownership remain explicitly
        out of scope unless fresh evidence justifies separate follow-up work
- [x] This reopened story records why the current direct-folder approved-handoff
      delta belongs here instead of a new story:
  - [x] the work log cites that the direct-folder continuation stays on the
        same owning route module, same checked-in mixed fixture family, same
        member-local plan/handoff artifact chain, and same operator-facing
        outcome as the already-completed ZIP slice
  - [x] the useful Story 224 exploration evidence is folded into this story and
        the standalone fragment shell is removed
- [x] A fresh current-pass baseline names the exact direct-folder
      approved-handoff gap from repo evidence:
  - [x] the work log records that
        `tests/fixtures/formats/_coverage-matrix.json`,
        `docs/methodology/state.yaml`, `README.md`, and `docs/RUNBOOK.md`
        still exclude direct-folder PDF-member approved handoff or final
        maintained PDF launch before this reopened implementation pass
  - [x] the work log records that the maintained direct-folder proof still
        stops at `terminal_reason = pdf_member_recommendation_only`
  - [x] the work log cites the verified reusable substrate honestly: Story
        222's emitted member-local `intake_plan_v1`, Story 223's completed ZIP
        `intake_handoff_v1` proof, `driver.py --input-folder`,
        `modules/intake/archive_route_members_v1/main.py`,
        `modules/intake/confirm_plan_v1/main.py`,
        `modules/intake/run_dispatch_v1/main.py`, and
        `modules/intake/intake_plan_utils.py`
- [x] The story lands one bounded direct-folder approved-handoff slice
      honestly:
  - [x] the shipping slice stays on the existing repo-owned
        `mixed-folder-pdf-mini/` fixture and the existing born-digital PDF
        member; the ZIP approved-handoff slice remains completed evidence and
        scanned/handwritten folder-PDF approval stays out of scope
  - [x] the chosen slice writes an inspectable route row plus adjacent
        member-local approved-handoff artifact for the direct-folder PDF member
  - [x] the chosen slice stops at member-local approved handoff, and the
        emitted `intake_handoff_v1` artifact under `output/runs/` is manually
        inspected alongside the approved plan artifact
  - [x] the implementation keeps final maintained PDF launch unclaimed instead
        of silently auto-launching it
- [x] Coverage, eval, and docs truth surfaces remain aligned with the reopened
      combined outcome:
  - [x] the ZIP-only approved-handoff proof remains recorded as already
        completed evidence
  - [x] `tests/fixtures/formats/_coverage-matrix.json`,
        `docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`, and
        `testdata/README.md` widen only as far as the fresh direct-folder proof
        justifies
  - [x] final maintained PDF launch, scanned/handwritten folder-PDF approval,
        grouped image-member interpretation, nested archives, attachment
        extraction, and broad heterogeneous archive ownership remain explicitly
        out of scope unless fresh evidence justifies a separate expansion
- [x] A fresh current-pass launch baseline names the exact shared post-handoff
      bug from repo evidence:
  - [x] the work log records that the maintained ZIP and direct-folder recipes
        still shipped `pdf_member_handoff_mode: dry_run` before this expansion
  - [x] a fresh `launch` probe on the checked-in folder PDF member reproduced
        `terminal_reason = pdf_member_handoff_blocked:None` on the route row
        before the fix
  - [x] the emitted `intake_handoff_v1` artifact from that same probe was
        manually inspected and shown to contain a valid downstream driver
        command for the born-digital PDF recipe despite the blocked route row
- [x] The shared route/handoff seam launches the bounded born-digital PDF
      member honestly on both checked-in entry surfaces:
  - [x] the ZIP PDF-member probe reaches a launched route row and a launched
        `intake_handoff_v1` row
  - [x] the direct-folder PDF-member probe reaches a launched route row and a
        launched `intake_handoff_v1` row
  - [x] each launched probe produces and records at least one inspected first
        downstream stamped artifact from the born-digital PDF recipe
- [x] Coverage, docs, and methodology truth surfaces widen only as far as the
      launched proof justifies:
  - [x] `tests/fixtures/formats/_coverage-matrix.json`,
        `docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`, and
        `testdata/README.md` move from approved-handoff-only wording to the
        exact bounded launched-PDF claim if and only if the maintained recipes
        now ship that behavior
  - [x] scanned/handwritten PDF-member launch, grouped image-member routing,
        nested archives, attachments, broad heterogeneous ownership, and the
        top-level `approved-intake-handoff` eval surface remain unchanged unless
        fresh current-pass evidence proves they also moved

## Out of Scope

- Any PDF-member launch beyond the one checked-in born-digital PDF member on
  `mixed-archive-pdf-mini.zip` and `mixed-folder-pdf-mini/`
- Scanned or handwritten PDF-member approval or launch ownership
- Broad “any PDF inside any archive/folder” auto-approval or auto-dispatch
- Grouped image-member interpretation, nested archives, attachments, `.msg`,
  mailbox/thread cleanup, or connector workflows
- Reopening Story 191 or changing handwritten OCR behavior
- New `doc-web` output-contract architecture beyond the minimum inspectable
  route, plan, handoff, and first downstream artifact needed to prove the
  bounded slice

## Approach Evaluation

- **Simplification baseline**: first measure whether the existing Story 221
  member-local `intake_plan_v1` plus current `run_dispatch_v1 --plan` or a
  bounded `confirm_plan_v1 --auto-approve` path already produces an honest
  archive-contained handoff or launch with no new archive logic. Story 221
  already proved the emitted plan can drive a dry-run and a real
  born-digital-PDF launch manually; the missing seam is packaging explicit
  approval into maintained archive routing, not raw downstream capability.
- **AI-only**: weak first move. No new model should decide approval or launch
  on a seam where the relevant AI recommendation artifact already exists.
- **Hybrid**: likely front-runner. Keep archive inventory and PDF-member
  recommendation AI work unchanged, then add the smallest deterministic
  approval/handoff continuation once the approval contract is explicit and
  inspectable.
- **Pure code**: plausible if the existing emitted plan artifact,
  `confirm_plan_v1`, `run_dispatch_v1`, and `archive_member_route_v1` fields
  already cover the bounded slice. Only add narrow glue if the baseline proves
  missing wiring.
- **Repo constraints / prior decisions**: `spec:1.1` keeps recipe ownership
  explicit under `C2`; Stories 176 and 180 keep human approval explicit and
  inspectable; Story 194 keeps the top-level recommendation-only and
  approved-handoff eval surfaces narrower than the direct-entry lanes; and
  Story 221 explicitly treated archive-contained approved handoff or final
  maintained PDF launch as a larger follow-on scope that needs an explicit
  approval contract. ADR-002 keeps the accepted `doc-web` boundary inspectable.
- **Existing patterns to reuse**: `configs/recipes/recipe-intake-contact-sheet-confirmed-handoff.yaml`,
  `modules/intake/confirm_plan_v1/main.py`,
  `modules/intake/run_dispatch_v1/main.py`,
  `modules/intake/intake_plan_utils.py`,
  `modules/intake/archive_route_members_v1/main.py`,
  `tests/test_mixed_archive_zip_recipe.py`, Story 176's and Story 180's
  approved-handoff proofs, Story 221's member-local plan emission, and the
  existing repo-owned `mixed-archive-pdf-mini.zip` probe.
- **Eval**: the deciding proof surface is a fresh `driver.py` run on
  `configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml` with
  `testdata/mixed-archive-pdf-mini.zip`, plus manual inspection of the route
  row, any emitted `intake_handoff_v1`, and the first downstream stamped
  artifact for the born-digital PDF member. If the approved-handoff truth
  surface changes materially, rerun the owning `approved-intake-handoff` eval
  and update `docs/evals/registry.yaml`.

## Tasks

- [x] Freeze the current mixed-archive approved-handoff gap from repo reality:
  - [x] verify the `mixed-archive` coverage row, methodology-state note,
        README, and runbook still excluded archive-contained approved handoff
        or final maintained PDF launch before implementation
  - [x] verify `archive_route_members_v1` still stopped ZIP PDF members at
        `pdf_member_recommendation_only`
  - [x] verify the reusable substrate honestly: the emitted member-local
        `overview_plan_final.jsonl` from Story 221, `confirm_plan_v1`,
        `run_dispatch_v1`, `intake_plan_utils.py`, and the born-digital PDF
        recipe/input-forwarding seam already proven outside archive routing
- [x] Measure the smallest honest baseline before adding new routing logic:
  - [x] current ZIP route behavior on `mixed-archive-pdf-mini.zip`
  - [x] existing `run_dispatch_v1` dry-run and real launch from the emitted
        member-local plan artifact
  - [x] `recipe-intake-contact-sheet.yaml` already carried explicit
        `auto_approve` semantics, so no new sibling recipe was required
  - [x] do not introduce a new archive-specific prompt or second AI routing
        pass until those reuse paths are measured
- [x] Land the smallest coherent implementation the baseline justifies:
  - [x] add the minimum route, helper, recipe, or schema changes needed to
        record member-local approved handoff honestly
  - [x] keep ZIP-only and born-digital-only as the default shipping slice
        without widening the claim
  - [x] preserve current `.eml` / HTML launches and blocked `.txt` behavior
        unchanged
- [x] Add focused fixture-backed coverage for route semantics, approval
      contract handling, and the new handoff artifact expectations
- [x] Update `tests/fixtures/formats/_coverage-matrix.json` and relevant
      methodology state honestly for the new bounded claim
- [x] Check whether the chosen implementation makes any existing code, helper
      paths, or docs redundant; no extra removal beyond the truth-surface
      wording cleanup was needed in this pass
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through
        `driver.py`, verify artifacts in `output/runs/`, and manually inspect
        sample JSON/JSONL data
  - [x] Agent tooling unchanged; `make skills-check` not required
- [x] The `approved-intake-handoff` eval surface did not change, so
      `docs/evals/registry.yaml` did not require a rerun or update
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: the member path, emitted plan, approval signal,
        and `intake_handoff_v1` remain inspectable end to end
  - [x] T1 — AI-First: no new AI was added to an approval/plumbing problem the
        existing recommendation artifact already solved
  - [x] T2 — Eval Before Build: the reuse path from the existing emitted plan
        was measured before adding archive-specific logic
  - [x] T3 — Fidelity: the born-digital PDF member's source path and approved
        recipe are preserved without silent substitution or hidden approval
  - [x] T4 — Modular: existing routing and approved-handoff seams were reused
        instead of inventing a parallel archive runtime
  - [x] T5 — Inspect Artifacts: the route row, emitted handoff artifact, and
        supporting approved plan artifact were manually inspected on the chosen
        dry-run slice
- [x] Consolidate the current problem line into this story:
  - [x] carry forward the useful exploration evidence from the fragment shell
        into this story's work log and plan
  - [x] remove the standalone fragment story so the backlog matches the actual
        story line
- [x] Freeze the current direct-folder approved-handoff gap from repo reality:
  - [x] verify the `mixed-archive` coverage row, methodology-state note,
        README, and runbook still exclude direct-folder PDF-member approved
        handoff or final maintained PDF launch before implementation
  - [x] verify the current direct-folder proof still stops at
        `pdf_member_recommendation_only`
  - [x] verify the reusable substrate honestly: Story 222's emitted
        `overview_plan_final.jsonl`, this story's completed ZIP-only handoff
        proof, `driver.py --input-folder`,
        `archive_route_members_v1.pdf_member_handoff_mode`,
        `confirm_plan_v1 --auto-approve`, `run_dispatch_v1`, and
        `intake_plan_utils.py`
- [x] Measure the smallest honest direct-folder baseline before adding new
      routing logic:
  - [x] current direct-folder route behavior on `mixed-folder-pdf-mini/`
  - [x] existing route continuation in `dry_run` mode on the same fixture
  - [x] existing `launch` continuation only if the same pass proves a healthy,
        bounded downstream runtime
  - [x] do not introduce a new folder-specific prompt or second AI routing
        pass until those reuse paths are measured
- [x] Land the smallest coherent direct-folder implementation the baseline
      justifies:
  - [x] add the minimum route, helper, recipe, or schema changes needed to
        record member-local approved handoff honestly on the folder probe
  - [x] keep the already-completed ZIP proof intact while adding direct-folder
        parity without widening the claim
  - [x] preserve existing `.eml` / HTML launches and blocked `.txt` behavior
        unchanged
- [x] Add focused fixture-backed coverage for route semantics, approval
      contract handling, and the direct-folder handoff artifact expectations
- [x] Update `tests/fixtures/formats/_coverage-matrix.json` and relevant
      methodology state honestly for the widened bounded claim
- [x] Freeze the current shared launch-path bug from repo reality:
  - [x] verify the maintained ZIP and direct-folder recipes still shipped
        `pdf_member_handoff_mode: dry_run` before this expansion
  - [x] capture a fresh current-pass `launch` probe that reproduced
        `pdf_member_handoff_blocked:None`
  - [x] inspect the emitted `intake_handoff_v1` artifact from the same probe
        to confirm the downstream launch command is otherwise valid
- [x] Land the smallest coherent shared launch fix the baseline justifies:
  - [x] fix the route-stage handoff/launch logic without widening unrelated
        archive-member behavior
  - [x] preserve existing `.eml` / HTML launches and blocked `.txt` behavior
        unchanged
  - [x] decide that the maintained mixed-archive and mixed-folder recipes now
        ship `pdf_member_handoff_mode: launch`
- [x] Add focused fixture-backed regression coverage for launched ZIP and
      direct-folder PDF members on the shared route contract
- [x] Run required checks for the widened launch scope:
  - [x] targeted pytest for the launch contract
  - [x] `make lint`
  - [x] `make test`
  - [x] clear stale `*.pyc`, run through `driver.py` on both checked-in probes,
        and inspect the launched artifacts in `output/runs/`
- [x] Update docs and truth surfaces only as far as the launch proof earns:
  - [x] refresh recipe defaults plus the exact bounded claim lines in
        `tests/fixtures/formats/_coverage-matrix.json`,
        `docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`, and
        `testdata/README.md` if launch becomes the maintained default
  - [x] leave the top-level `approved-intake-handoff` eval surface unchanged
        unless the nested launch expansion actually changes that maintained
        boundary
- [x] Verify Central Tenets for the widened launch slice:
  - [x] T0 — Traceability: route rows, handoff rows, and first downstream
        artifacts stay source-linked and inspectable
  - [x] T1 — AI-First: the change remains plumbing-first and does not add a new
        AI routing/approval pass
  - [x] T2 — Eval Before Build: the fresh launch baseline was reproduced before
        fixing the route logic
  - [x] T3 — Fidelity: the launched born-digital PDF member preserves the same
        source file and recipe choice already proven at approved-handoff scope
  - [x] T4 — Modular: reuse the existing route/handoff/runtime seam rather than
        inventing a parallel archive launch path
  - [x] T5 — Inspect Artifacts: manually open the launched route, handoff, and
        first downstream artifacts for both checked-in probes

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

- **Owning module / area**: the intake-routing seam between
  `archive_route_members_v1` and the approved-handoff substrate for one
  bounded ZIP PDF member plus the matching source-native folder parity slice.
  Primary ownership should stay in `modules/intake/`, the mixed
  archive/folder recipe/tests, and the truth surfaces that describe the
  bounded claim.
- **Methodology reality**: this story belongs to `spec:1`, `spec:6`,
  `spec:7`, `spec:8`, and `spec:9`. In `docs/methodology/state.yaml`,
  `spec:1`, `spec:6`, `spec:8`, and `spec:9` have substrate `exists`, while
  `spec:7` remains `partial`; the relevant compromise phases are `C2 = climb`
  and `B10 = climb`. The relevant coverage row is `mixed-archive`, which is
  currently `passing` on four bounded probes while now naming ZIP-only and
  direct-folder PDF-member approved handoff as proven, with final maintained
  PDF launch still an explicit known gap.
- **Substrate evidence**: verified in the completed ZIP pass and the current
  direct-folder exploration that
  `modules/intake/archive_route_members_v1/main.py` now routes ZIP PDF members
  into a nested recommendation intake run, records the emitted approved
  `overview_plan_final.jsonl` as `first_downstream_artifact`, and can write a
  member-local `intake_handoff_v1` sidecar in the same route stage;
  `modules/intake/intake_plan_utils.py` already resolves approved-plan source
  input and builds explicit `driver.py` launch commands, now with caller-owned
  downstream output roots;
  `modules/intake/run_dispatch_v1/main.py` already writes `intake_handoff_v1`
  and launches explicit recipes from an approved plan;
  `modules/intake/confirm_plan_v1/main.py` already supports `--auto-approve`;
  `configs/recipes/recipe-intake-contact-sheet-confirmed-handoff.yaml` exists
  as the maintained approved-handoff sibling recipe; `schemas.py` and
  `validate_artifact.py` now register the widened `archive_member_route_v1`
  plus `intake_handoff_v1`; Story 221's work log already proved dry-run and
  real launch from the emitted member-local plan artifact; and current
  direct-folder exploration already proves the bounded `dry_run` handoff
  artifact on `mixed-folder-pdf-mini/`. The missing current-pass proof is not
  substrate capability; it is keeping the approved-handoff story line honest
  by absorbing the folder parity slice here and updating tests/docs/truth
  surfaces without yet widening final maintained PDF launch.
- **Data contracts / schemas**: the likely touched surfaces are
  `archive_member_route_v1`, `intake_plan_v1`, and `intake_handoff_v1`. The
  current schema substrate already exists; if the chosen implementation needs
  route rows to reference a nested handoff artifact or explicit approval flag
  across stage boundaries, add those fields to `schemas.py` before stamped
  artifacts rely on them.
- **File sizes**: likely owner files are
  `modules/intake/archive_route_members_v1/main.py` (`273` lines),
  `modules/intake/intake_plan_utils.py` (`419` lines),
  `modules/intake/run_dispatch_v1/main.py` (`91` lines),
  `modules/intake/confirm_plan_v1/main.py` (`52` lines),
  `configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml` (`20` lines),
  `configs/recipes/recipe-intake-contact-sheet-confirmed-handoff.yaml`
  (`59` lines), `tests/test_mixed_archive_zip_recipe.py` (`374` lines),
  `docs/evals/registry.yaml` (`2266` lines), the coverage matrix (`582`
  lines), `README.md` (`533` lines), `docs/RUNBOOK.md` (`953` lines),
  `schemas.py` (`1373` lines), and `driver.py` (`3204` lines). `docs/evals/registry.yaml`,
  `tests/fixtures/formats/_coverage-matrix.json`, `README.md`,
  `docs/RUNBOOK.md`, `schemas.py`, and `driver.py` are already >500 lines, so
  keep edits surgical and run `make check-size` if they grow materially.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`,
  `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002,
  Stories 176 / 180 / 194 / 196 / 205 / 221 / 222, the `mixed-archive`
  coverage row, `README.md`, `docs/RUNBOOK.md`, and the current intake-routing
  modules/recipes/tests. Search across `docs/decisions/`, `docs/runbooks/`,
  `docs/scout/`, and `docs/notes/` found no narrower owner for
  archive-contained approved handoff beyond those story records.

## Files to Modify

- `docs/stories/story-223-mixed-archive-pdf-member-approved-handoff-seam.md`
  — reopened story scope, plan, and work log
- `modules/intake/archive_route_members_v1/main.py` — extend the bounded ZIP
  PDF-member continuation only if the direct-folder baseline exposes missing
  wiring rather than already-working dry-run proof
- `modules/intake/intake_plan_utils.py` — reuse or widen helpers for
  member-local plan-to-handoff resolution if archive-member metadata needs a
  narrow bridge into the existing approved-handoff seam (`419` lines)
- `modules/intake/run_dispatch_v1/main.py` — only if the current handoff row
  needs narrow new metadata or outcome handling for the member-local approved
  seam (`91` lines)
- `configs/recipes/recipe-mixed-folder-routing-mvp.yaml` — expose any bounded
  approval or route parameter needed for the reopened direct-folder parity seam
- `configs/recipes/recipe-intake-contact-sheet-confirmed-handoff.yaml` — only
  if the existing maintained approved-handoff recipe is the smallest honest
  reuse path for the nested PDF-member seam (`59` lines)
- `tests/test_mixed_archive_zip_recipe.py` — add focused approved-handoff or
  launched-outcome expectations only if the shared route contract changes
- `tests/test_mixed_folder_recipe.py` — codify the direct-folder approved-
  handoff proof on the checked-in folder probe
- `docs/evals/registry.yaml` — only if the approved-handoff truth surface
  changes materially (`2266` lines)
- `tests/fixtures/formats/_coverage-matrix.json` — update the bounded gap note
  only if the shipped behavior changes the documented mixed-archive reality
  (`582` lines)
- `docs/methodology/state.yaml` — narrow the campaign / known-gap note only if
  the shipped behavior changes that truth (`132` lines)
- `README.md` and `docs/RUNBOOK.md` — align the public bounded claim with the
  implementation outcome (`533` / `953` lines)
- `schemas.py` — only if the chosen route or handoff artifact needs new
  cross-boundary fields (`1373` lines)

## Redundancy / Removal Targets

- The standalone Story 224 fragment shell once its useful exploration evidence
  has been absorbed here
- The old blanket “direct-folder PDF-member approved handoff or final
  maintained PDF launch” wording in the mixed-archive truth surfaces, now
  expected to narrow to the remaining unproven gaps after the folder parity
  slice lands
- Any temporary route-row flags or helper branches added only for the first
  direct-folder parity probe once the maintained contract is stable

## Notes

- Under the tightened anti-fragmentation rule, the direct-folder approved-
  handoff and launch continuation is not a separate story. It stays on the same
  `archive_route_members_v1` route/module, same checked-in mixed fixture
  family, same `overview_plan_final.jsonl` / `intake_handoff_v1` artifact
  chain, and same operator-facing outcome as the completed ZIP slice.
- The ZIP and direct-folder approved-handoff proofs in this story remain
  completed evidence. The reopened delta is the first bounded launched-PDF
  proof plus the truth-surface updates needed to claim that wider slice
  honestly.
- Do not widen the top-level `approved-intake-handoff` surface casually. The
  story is about member-local approved-handoff truth inside the bounded
  mixed-archive route/module seam, not about turning every direct-entry family
  into an archive-owned automation surface by implication.

## Plan

Reopened scope under the tightened anti-fragmentation rule: keep Story 223 as
the single owner of the bounded born-digital PDF-member line from recommendation
to approved handoff to first downstream maintained launch, across the checked-in
ZIP and direct-folder probes on the same route/module seam.

Current baseline evidence:

- The maintained ZIP and direct-folder recipes still ship
  `pdf_member_handoff_mode: dry_run`, and the current docs/coverage surfaces
  still describe those probes as approved-handoff-only slices.
- The shared dry-run contract is already green in repo tests:
  `python -m pytest tests/test_mixed_archive_zip_recipe.py -q -k 'handoff or folder_pdf_member_writes_handoff_artifact'`
  passed `2/2` on the current tip.
- Fresh current-pass launch reproduction on the checked-in direct-folder probe
  now exists outside historical story prose. Running
  `python -m modules.intake.archive_route_members_v1.main --manifest <temp manifest> --outdir <temp route dir> --run-id story223-launch-baseline --allow-run-id-reuse --pdf-member-handoff-mode launch`
  wrote a route row with `terminal_reason = pdf_member_handoff_blocked:None`
  while the emitted `intake_handoff_v1` row already contained a valid
  `driver.py` command for
  `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`, a concrete
  downstream run id, and the correct `--input-pdf` source path back to
  `testdata/mixed-folder-pdf-mini/docs/proposal.pdf`.

Implementation order:

1. Fix the shared launch-path bug in the route stage.
   - Primary owner: `modules/intake/archive_route_members_v1/main.py`.
   - Keep the change narrow to PDF-member handoff handling; do not redesign the
     approval artifact contract if the bug is only the route-stage launch
     decision.
   - Touch `modules/intake/intake_plan_utils.py` or `modules/intake/run_dispatch_v1/main.py`
     only if the fresh baseline proves a real metadata gap instead of the
     current default-state ordering bug.
2. Decide the maintained shipping surface from fresh proof.
   - If the shared fix launches cleanly on both checked-in probes and produces
     inspectable first downstream artifacts, switch the maintained mixed-input
     recipes from `dry_run` to `launch`.
   - If a second downstream blocker appears after the launch bug is fixed, keep
     the maintained recipes at `dry_run`, record the blocker explicitly, and do
     not widen the truth surfaces beyond approved handoff.
3. Add focused regression coverage for the widened behavior.
   - Update `tests/test_mixed_archive_zip_recipe.py` with launch-mode coverage
     for both ZIP and direct-folder PDF members on the shared route contract.
   - Update `tests/test_mixed_folder_recipe.py` only if the maintained folder
     recipe default or fixture metadata claim changes.
4. Refresh only the truth surfaces the launch proof earns.
   - If launch becomes the maintained default, update
     `configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml`,
     `configs/recipes/recipe-mixed-folder-routing-mvp.yaml`,
     `tests/fixtures/formats/_coverage-matrix.json`,
     `docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`, and
     `testdata/README.md` to the exact bounded launched-PDF claim.
   - Keep scanned/handwritten PDF-member launch, grouped image-member routing,
     nested archives, attachments, and the top-level
     `approved-intake-handoff` eval surface out of scope unless fresh evidence
     says otherwise.

Verification and done criteria:

- Targeted pytest for the route/handoff launch contract.
- `make lint`
- `make test`
- Fresh `driver.py` runs on both:
  - `configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml` with
    `testdata/mixed-archive-pdf-mini.zip`
  - `configs/recipes/recipe-mixed-folder-routing-mvp.yaml` with
    `testdata/mixed-folder-pdf-mini/`
- Manual inspection of:
  - `02_archive_route_members_v1/archive_member_routes.jsonl`
  - nested `05_confirm_plan_v1/overview_plan_final.jsonl`
  - emitted `intake_handoff.jsonl`
  - first downstream stamped artifact from the launched born-digital PDF recipe

Structural health and risk notes:

- `tests/test_mixed_archive_zip_recipe.py` is already the densest contract file
  on this seam; keep new assertions flat and fixture-specific instead of
  building helper abstraction for two probes.
- `schemas.py`, `README.md`, `docs/RUNBOOK.md`, the coverage matrix, and
  `docs/methodology/state.yaml` are already large. Edit only the exact claim
  lines required by the widened bounded slice.
- The current critical substrate is verified in code: the emitted plan artifact,
  `prepare_confirmed_handoff(...)`, `run_dispatch_v1`, and the born-digital PDF
  recipe all already exist. The fresh baseline says this is a route-stage logic
  bug, not a missing runtime seam.

Approval note:

The user explicitly approved this same-story scope expansion on 2026-04-17.
Proceed with the bounded launch fix and proof; do not spin out another story
shell for the same route/module line.

## Work Log

20260417-0038 — launch fix + close-out: completed the reopened launched-PDF
delta on Story 223 and closed the story again on fresh current-pass evidence.
Implementation shipped in this pass:
`modules/intake/archive_route_members_v1/main.py` now only treats a handoff row
as blocked when `prepare_confirmed_handoff(...)` actually returned a
non-launchable result and now mirrors the nested launch exit code back onto the
route row; `configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml` and
`configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml` no longer
pin the stale `story168-marker-cpu-3662` runtime container; and both
`recipe-mixed-archive-zip-routing-mvp.yaml` and
`recipe-mixed-folder-routing-mvp.yaml` now ship
`pdf_member_handoff_mode: launch`. Focused regression coverage widened in
`tests/test_mixed_archive_zip_recipe.py`,
`tests/test_mixed_folder_recipe.py`, and
`tests/test_pdf_intake_recipe.py`; fixture metadata moved forward in
`testdata/mixed-archive-pdf-mini.source.json` and
`testdata/mixed-folder-pdf-mini.source.json`; and the bounded launched-PDF
claim was refreshed in `tests/fixtures/formats/_coverage-matrix.json`,
`docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`, and
`testdata/README.md`. Fresh baseline evidence preserved from the reopened
exploration remains valid: before the fix, a current-pass folder `launch` probe
reproduced `pdf_member_handoff_blocked:None` while the emitted
`intake_handoff_v1` artifact already held a valid downstream born-digital PDF
driver command. Fresh checks in this close-out pass:
`python -m pytest tests/test_mixed_archive_zip_recipe.py tests/test_mixed_folder_recipe.py tests/test_pdf_intake_recipe.py -q`
→ `25 passed in 28.27s`; `make methodology-compile` refreshed
`docs/methodology/graph.json` and `docs/stories.md`; `make lint` passed; and
`make test` passed at `594 passed, 4 warnings in 680.98s (0:11:20)`, with the
same pre-existing Pydantic deprecation warnings in
`modules/portionize/portionize_headers_numeric_v1/main.py`. Fresh real pipeline
proofs after `find modules -name "*.pyc" -delete`: ZIP launch run
`story223-launch-zip-r2` completed with `Archive routing complete: launched=3, blocked=1, skipped=0, failed=0`, and direct-folder launch run
`story223-launch-folder-r1` completed with the same summary. Manual artifact
inspection in the same fresh pass:
`output/runs/story223-launch-zip-r2/02_archive_route_members_v1/archive_member_routes.jsonl`
shows the ZIP PDF member with `recommended_recipe =
configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`,
`approval_mode = confirm_plan_auto_approve`, `terminal_reason =
pdf_member_launched_from_approved_plan`, and `handoff_artifact_path` pointing at
the member-local sidecar; the paired handoff artifact at
`output/runs/story223-launch-zip-r2/02_archive_route_members_v1/pdf_member_handoffs/member-001/intake_handoff.jsonl`
records the same source PDF, the launched born-digital child run id, and
`terminal_outcome = launched`; and the first downstream born-digital artifact at
`output/runs/story223-launch-zip-r2-member-001-approved-handoff-recipe-born-digital-pdf-non-toc-html-mvp/01_extract_pdf_marker_lite_html_v1/pages_html.jsonl`
contains clean stamped HTML for both pages, including page 1 heading
`Acme Community Arts Initiative` and the full non-TOC body text. The matching
bundle manifest at
`output/runs/story223-launch-zip-r2-member-001-approved-handoff-recipe-born-digital-pdf-non-toc-html-mvp/output/html/manifest.json`
shows two chapter entries titled `Requested information:` and
`Accessibility notes:`. The direct-folder proof matches the same bounded claim:
`output/runs/story223-launch-folder-r1/02_archive_route_members_v1/archive_member_routes.jsonl`
shows the source-native PDF member with `terminal_reason =
pdf_member_launched_from_approved_plan`; the paired handoff artifact at
`output/runs/story223-launch-folder-r1/02_archive_route_members_v1/pdf_member_handoffs/member-001/intake_handoff.jsonl`
records `terminal_outcome = launched`; and the first downstream born-digital
artifact at
`output/runs/story223-launch-folder-r1-member-001-approved-handoff-recipe-born-digital-pdf-non-toc-html-mvp/01_extract_pdf_marker_lite_html_v1/pages_html.jsonl`
contains the same clean two-page HTML extraction from the source-native folder
PDF. Supporting `.eml` / HTML launches and blocked `.txt` routing stayed intact
on both entry surfaces. Close-out note: the earlier Story 223 changelog entries
cover the prior bounded slices, and the launched-PDF expansion is recorded
separately for landing. Outcome: Story 223 now honestly owns and proves the
first bounded approved-plan-to-launched-PDF continuation on both the checked-in
ZIP and direct-folder mixed-input probes while leaving scanned/handwritten
PDF-member launch, grouped image members, nested archives, attachments, and
top-level automation-surface widening out of scope. Next step:
`/check-in-diff`.

20260417-0018 — reopen + build-story exploration for launched-PDF expansion:
re-read `docs/ideal.md`, `docs/spec.md` (`spec:1`, `spec:1.1`, `spec:6`,
`spec:7`, `spec:8`, `spec:9`), `docs/methodology/state.yaml`,
`docs/methodology/graph.json`, ADR-002, Stories 176/180/194/196/205/221/222,
the `mixed-archive` coverage row, `README.md`, `docs/RUNBOOK.md`,
`testdata/README.md`, `schemas.py`, `modules/intake/archive_route_members_v1/main.py`,
`modules/intake/intake_plan_utils.py`, `modules/intake/run_dispatch_v1/main.py`,
`configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml`,
`configs/recipes/recipe-mixed-folder-routing-mvp.yaml`,
`tests/test_mixed_archive_zip_recipe.py`, and `tests/test_mixed_folder_recipe.py`.
Ideal-alignment result: proceed. This is the smallest honest next deletion of a
known compromise on the active `maintained-intake-honesty` line, because the
route/handoff/runtime substrate already exists and the remaining issue is a real
repo bug, not a missing external trigger. Fresh baseline evidence in this pass:
the maintained recipes still default to `pdf_member_handoff_mode: dry_run`; the
current dry-run contract remains green (`python -m pytest tests/test_mixed_archive_zip_recipe.py -q -k 'handoff or folder_pdf_member_writes_handoff_artifact'`
→ `2 passed`); and a fresh launch-mode module run on the checked-in direct-folder
probe wrote a route row with `terminal_reason = pdf_member_handoff_blocked:None`
while the emitted handoff row already contained a valid downstream
`driver.py --recipe configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml --input-pdf ...`
command, a concrete downstream run id, and the correct source PDF path. Critical
substrate verified versus missing: `archive_route_members_v1`, `prepare_confirmed_handoff(...)`,
`run_dispatch_v1`, and the born-digital PDF runtime all exist in code and are
already proven at approved-handoff scope; no new schema boundary is required
yet; the missing slice is the shared launch-path logic in the route stage. Files
most likely to change: `modules/intake/archive_route_members_v1/main.py`, both
mixed-input recipe YAMLs if launch becomes the maintained default,
`tests/test_mixed_archive_zip_recipe.py`, `tests/test_mixed_folder_recipe.py`,
and the exact bounded-claim lines in `tests/fixtures/formats/_coverage-matrix.json`,
`docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`, and
`testdata/README.md`. Structural-health note: the large truth surfaces are
already above the preferred size, so edits there must stay surgical. Scope
decision: this remains one story under the anti-fragmentation rule because the
new work stays on the same owning route module, checked-in fixture family,
artifact chain, and operator-facing outcome. Next step: set Story 223 `In Progress`,
recompile methodology views, then fix the shared launch-path bug and prove the
first downstream maintained PDF launch on both checked-in probes.

20260416-1438 — create-story: created Story 223 after `/triage` identified the
next actionable intake-routing residue and the user approved the recommended
action. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`,
`docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, Stories
176 / 180 / 194 / 196 / 205 / 221 / 222, the `mixed-archive` coverage row,
`README.md`, `docs/RUNBOOK.md`,
`modules/intake/archive_route_members_v1/main.py`,
`modules/intake/intake_plan_utils.py`,
`modules/intake/run_dispatch_v1/main.py`,
`modules/intake/confirm_plan_v1/main.py`,
`configs/recipes/recipe-intake-contact-sheet-confirmed-handoff.yaml`, and
`tests/test_mixed_archive_zip_recipe.py`. Result: a new story is honest instead
of reopening Story 221 because Story 221 closed the recommendation-only ZIP
PDF-member seam and explicitly left archive-contained approved handoff or final
maintained PDF launch out of scope. Fresh repo-backed substrate check in this
pass: the current mixed-archive truth surfaces still exclude archive-contained
approved handoff or final maintained PDF launch; the route module still stops
ZIP PDF members at `pdf_member_recommendation_only`; the emitted member-local
plan artifact already exists on the checked-in ZIP probe; `confirm_plan_v1`
already supports `--auto-approve`; and `run_dispatch_v1` plus
`intake_plan_utils.py` already support dry-run and real launch from an approved
plan. Status is `Pending`, not `Draft`, because the missing work is a bounded
approval-packaging and truth-surface continuation, not missing runtime
substrate. Next step: `/build-story` should measure the smallest honest reuse
path from the emitted member-local plan and then choose the smallest ZIP-only
approved-handoff continuation that preserves explicit approval semantics.

20260416-1448 — build-story explore: verified the current mixed-archive
approved-handoff baseline with fresh code reads and fresh run artifacts, then
narrowed the honest shipping slice to member-local approved handoff by default.
Evidence from repo truth surfaces:
`tests/fixtures/formats/_coverage-matrix.json`,
`docs/methodology/state.yaml`, `README.md`, and `docs/RUNBOOK.md` all still
exclude archive-contained approved handoff or final maintained PDF launch.
Fresh baseline run:
`python driver.py --recipe configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml --input-zip testdata/mixed-archive-pdf-mini.zip --run-id story223-baseline-r1 --allow-run-id-reuse --output-dir output/runs --force`
produced
`output/runs/story223-baseline-r1/02_archive_route_members_v1/archive_member_routes.jsonl`
with `member_path = docs/proposal.pdf`,
`terminal_reason = pdf_member_recommendation_only`,
`recommended_recipe = configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`,
and
`first_downstream_artifact = output/runs/story223-baseline-r1-member-001-recipe-intake-contact-sheet/05_confirm_plan_v1/overview_plan_final.jsonl`.
Fresh code check of `configs/recipes/recipe-intake-contact-sheet.yaml` showed
that nested artifact is already an explicitly auto-approved plan because the
`confirm_plan_v1` stage sets `auto_approve: true`; the missing maintained seam
is dispatch from that approved plan, not approval substrate. Fresh dry-run
dispatch:
`python modules/intake/run_dispatch_v1/main.py --plan output/runs/story223-baseline-r1-member-001-recipe-intake-contact-sheet/05_confirm_plan_v1/overview_plan_final.jsonl --out output/runs/story223-manual-dryrun-r1/intake_handoff.jsonl --run-id story223-manual-dryrun-r1 --allow-run-id-reuse --dry-run`
wrote `output/runs/story223-manual-dryrun-r1/intake_handoff.jsonl` with the
correct `--input-pdf` path back to the extracted archive member PDF, proving
the current substrate already materializes a member-local `intake_handoff_v1`
without new AI logic. Fresh real dispatch:
`python modules/intake/run_dispatch_v1/main.py --plan output/runs/story223-baseline-r1-member-001-recipe-intake-contact-sheet/05_confirm_plan_v1/overview_plan_final.jsonl --out output/runs/story223-manual-launch-r2/intake_handoff.jsonl --run-id story223-manual-launch-r2 --allow-run-id-reuse --downstream-end-at marker_lite_html`
launched the correct born-digital recipe and then failed inside
`output/runs/story223-manual-launch-r2-recipe-born-digital-pdf-non-toc-html-mvp/pipeline_events.jsonl`
20260416-1640 — anti-fragmentation reopen: reran the current story line under
the tightened triage rule and concluded that Story 224 was a fragment of this
story, not an honest new owner. Evidence from current repo state: the direct-
folder continuation stays on the same `archive_route_members_v1` route/module,
same checked-in mixed fixture family, same member-local
`overview_plan_final.jsonl` / `intake_handoff_v1` artifact chain, and same
operator-facing outcome as the ZIP-approved-handoff slice already completed
here. Carried over the useful direct-folder exploration evidence from the
fragment shell: baseline folder run
`output/runs/story224-baseline-r1/02_archive_route_members_v1/archive_member_routes.jsonl`
still ends at `pdf_member_recommendation_only`; the bounded `dry_run` probe
already proves the approved-handoff artifact at
`output/runs/story224-dryrun-r1/02_archive_route_members_v1/pdf_member_handoffs/member-001/intake_handoff.jsonl`;
and the bounded `launch` probe fails with
`pdf_member_handoff_blocked:None`, exposing a separate launch/runtime bug
rather than missing approved-handoff substrate. Result: reopened Story 223 as
`Pending`, expanded its scope/tasks/plan to absorb the direct-folder parity
delta, and removed Story 224 instead of keeping a same-line fragment in the
backlog. Next: implement the reopened folder parity slice here, starting with
regression codification and truth-surface updates, and only expand to launch if
the user explicitly wants that larger success surface.
because Docker could not start `story168-marker-cpu-3662`; a fresh
`docker start story168-marker-cpu-3662` still reports
`invalid mount config for type "bind": bind source path does not exist: /host_mnt/Users/cam/.codex/worktrees/cb9b/doc-web`.
Impact: Story 223 remains honestly buildable because the route, approved-plan,
and handoff substrate already exist in repo reality. The only fresh risk is the
local Marker runtime state after dispatch, so the safest default implementation
target is an inspectable member-local approved-handoff artifact, with final
maintained PDF launch left as an optional extra proof if the environment is
repaired in the same pass. Files most likely to change:
`modules/intake/archive_route_members_v1/main.py`,
`modules/intake/intake_plan_utils.py`, `schemas.py`,
`tests/test_mixed_archive_zip_recipe.py`, and the exact claim lines in the
coverage matrix, methodology state, `README.md`, and `docs/RUNBOOK.md`. Next
step: present the narrowed implementation plan for user approval, then build
the bounded route-to-handoff continuation without overstating final-launch
coverage.

20260416-1514 — build-story implement: shipped the bounded ZIP-only
mixed-archive PDF-member approved-handoff seam and refreshed the truth
surfaces to match. Code changes: `archive_route_members_v1` now accepts
`pdf_member_handoff_mode`, reuses the emitted approved plan via
`prepare_confirmed_handoff(...)`, writes a member-local
`02_archive_route_members_v1/pdf_member_handoffs/<member_id>/intake_handoff.jsonl`
artifact, and records `approval_mode` plus `handoff_artifact_path` on the
route row; `intake_plan_utils.py` now forwards a caller-owned downstream
output root; `schemas.py` widened `archive_member_route_v1`; and
`recipe-mixed-archive-zip-routing-mvp.yaml` now ships the ZIP PDF-member lane
in `dry_run` approved-handoff mode by default. Coverage/tests: added focused
fixture assertions in `tests/test_mixed_archive_zip_recipe.py` and
`tests/test_intake_plan_utils.py`. Fresh checks in this pass:
`pytest -q tests/test_intake_plan_utils.py`,
`pytest -q tests/test_mixed_archive_zip_recipe.py`, `make lint`, and
`make test` (`591 passed, 4 warnings in 705.37s`; warnings are the existing
Pydantic deprecation notices in
`modules/portionize/portionize_headers_numeric_v1/main.py`). Fresh pipeline
proof after `find modules/intake -name "*.pyc" -delete`:
`python driver.py --recipe configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml --input-zip testdata/mixed-archive-pdf-mini.zip --run-id story223-impl-r1 --allow-run-id-reuse --output-dir output/runs --force`
completed successfully with `archive_route` summary
`launched=2, blocked=1, skipped=1`. Manual artifact inspection:
`output/runs/story223-impl-r1/02_archive_route_members_v1/archive_member_routes.jsonl`
shows `docs/proposal.pdf` with `terminal_reason =
pdf_member_approved_handoff_dry_run`, `approval_mode =
confirm_plan_auto_approve`, `first_downstream_artifact` pointing at the nested
approved plan, and `handoff_artifact_path` pointing at the new sidecar;
`output/runs/story223-impl-r1/02_archive_route_members_v1/pdf_member_handoffs/member-001/intake_handoff.jsonl`
shows `launch_input_flag = --input-pdf`, `launch_input_path` back to the
extracted archive member, `recommended_recipe =
configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`, and
`terminal_reason = dry_run`; and
`output/runs/story223-impl-r1-member-001-recipe-intake-contact-sheet/05_confirm_plan_v1/overview_plan_final.jsonl`
still records the approved PDF-member plan with `signals = ["forms"]`,
`warnings = ["Missing capabilities: forms"]`, and the correct
`meta.source_input.source_pdf` path. Supporting direct-entry members remained
intact: email bundle title `Fixture Subject` and web bundle title `Book` were
manually confirmed from the stamped HTML manifests. Schema validation also
passed on the new stamped artifacts via `validate_artifact.py` for
`archive_member_route_v1`, `intake_handoff_v1`, and `intake_plan_v1`. Docs
updated in this pass:
`tests/fixtures/formats/_coverage-matrix.json`,
`docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`, and
`testdata/README.md` now claim one ZIP-only PDF-member approved-handoff slice
while leaving direct-folder PDF-member approved handoff and final maintained
PDF launch explicitly out of scope. Eval note: `docs/evals/registry.yaml` was
not rerun because `approved-intake-handoff` still measures the top-level
direct-entry surface rather than this nested archive-route continuation. Next
step: `/validate 223` can now focus on the completed bounded slice instead of a
missing routing seam.

20260416-1532 — validate: reviewed the full local change set with
`git status --short`, `git diff --stat`, `git diff`, and
`git ls-files --others --exclude-standard`; the only untracked file is this
Story 223 file, which is part of the intended change set. Re-read
`docs/ideal.md`, ADR-002, the `approved-intake-handoff` registry entry, and
the direct-entry boundary test so the validation verdict stays aligned with the
project's runtime-boundary decisions. Fresh verification in this validation
pass: `make lint` passed; `make test` passed at `591 passed, 4 warnings in
665.31s`, with the same pre-existing Pydantic deprecation warnings in
`modules/portionize/portionize_headers_numeric_v1/main.py`; previously
inspected Story 223 artifacts still match the bounded claim, and no new
implementation gaps surfaced during diff review. Validation result: the story's
implementation slice is complete and coherent, the remaining work is close-out
bookkeeping (`/mark-story-done`), and the recommended disposition is
`Close now`.

20260416-1536 — mark-story-done: Story 223 closed after fresh close-out review
confirmed the implementation slice is complete, the dependency stories
(`176`, `180`, `196`, `205`, `221`) are already `Done`, and the shipped claim
still matches the inspected artifacts. Fresh close-out evidence reused from the
current pass: `make lint`, `make test` (`591 passed, 4 warnings`), route and
handoff artifact inspection on `story223-impl-r1`, and the validation review
of `docs/ideal.md`, ADR-002, and the `approved-intake-handoff` eval boundary.
Result: status set to `Done`, the final workflow gate is checked, generated
story views were refreshed, and `CHANGELOG.md` now records the Story 223
landing summary. Next step: `/check-in-diff`.

20260416-1648 — consolidation follow-up: superseded the earlier close-out state
after rerunning the story line under the tightened anti-fragmentation rule.
Story 223 is now the honest owner for the remaining direct-folder parity work,
because that delta stays on the same route/module, checked-in fixture family,
member-local plan/handoff artifact chain, and operator-facing outcome as the
completed ZIP slice. Removed the standalone Story 224 fragment shell, reopened
Story 223 as `Pending`, and refreshed the goal, acceptance criteria, tasks,
notes, and plan so the backlog matches the actual work line. Fresh evidence
preserved in this pass: `story224-baseline-r1` still ends at
`pdf_member_recommendation_only`, `story224-dryrun-r1` already proves the
bounded direct-folder `intake_handoff_v1` artifact, and `story224-launch-r1`
still exposes a separate launch/runtime blocker rather than a missing approved-
handoff substrate. Next step: build the reopened folder parity slice inside
Story 223 rather than reviving a separate fragment story.

20260416-1725 — build-story implement: landed the direct-folder parity slice
inside Story 223 instead of fragmenting the same route/module line again.
Runtime/files changed in this pass:
`configs/recipes/recipe-mixed-folder-routing-mvp.yaml` now ships
`archive_route_members_v1` with `pdf_member_handoff_mode: dry_run`;
`tests/test_mixed_archive_zip_recipe.py` now adds focused direct-folder
approved-handoff regression coverage next to the shared ZIP route contract;
`tests/test_mixed_folder_recipe.py` now pins the maintained folder recipe
default plus the fixture metadata claim; and
`testdata/mixed-folder-pdf-mini.source.json`,
`tests/fixtures/formats/_coverage-matrix.json`,
`docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`, and
`testdata/README.md` now all describe the same bounded direct-folder
approved-handoff dry-run slice. Fresh baseline evidence carried into this
pass from the reopened exploration: before the recipe change, the maintained
direct-folder proof still stopped at
`output/runs/story224-baseline-r1/02_archive_route_members_v1/archive_member_routes.jsonl`
with `terminal_reason = pdf_member_recommendation_only`, while
`story224-dryrun-r1` already proved the reusable folder-side handoff substrate
and `story224-launch-r1` exposed a separate shared launch-path blocker
(`pdf_member_handoff_blocked:None`). Fresh checks in this implementation pass:
`python -m pytest tests/test_mixed_archive_zip_recipe.py tests/test_mixed_folder_recipe.py -q`
→ `10 passed`; `make lint` → clean; `make test` → `592 passed, 4 warnings`
(same pre-existing Pydantic deprecation warnings in
`modules/portionize/portionize_headers_numeric_v1/main.py`). Fresh pipeline
proof after clearing stale `*.pyc`:
`python driver.py --recipe configs/recipes/recipe-mixed-folder-routing-mvp.yaml --input-folder testdata/mixed-folder-pdf-mini --run-id story223-mixed-folder-impl-r1 --allow-run-id-reuse --force`
completed with `Archive routing complete: launched=2, blocked=1, skipped=1`.
Fresh schema validation passed on the stamped manifest, route, approved plan,
and handoff sidecar via `validate_artifact.py`. Manual artifact inspection in
the same fresh run: `output/runs/story223-mixed-folder-impl-r1/02_archive_route_members_v1/archive_member_routes.jsonl`
shows `docs/proposal.pdf` with `archive_format = folder`,
`terminal_reason = pdf_member_approved_handoff_dry_run`,
`approval_mode = confirm_plan_auto_approve`,
`first_downstream_artifact = .../05_confirm_plan_v1/overview_plan_final.jsonl`,
and `handoff_artifact_path = .../pdf_member_handoffs/member-001/intake_handoff.jsonl`;
`output/runs/story223-mixed-folder-impl-r1-member-001-recipe-intake-contact-sheet/05_confirm_plan_v1/overview_plan_final.jsonl`
still records `recommended_recipe = configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`,
`signals = [forms]`, `warnings = [Missing capabilities: forms]`, and
`meta.source_input.source_pdf` pointing back to
`testdata/mixed-folder-pdf-mini/docs/proposal.pdf`; and
`output/runs/story223-mixed-folder-impl-r1/02_archive_route_members_v1/pdf_member_handoffs/member-001/intake_handoff.jsonl`
records `launch_input_flag = --input-pdf`, `launch_input_path` back to that
same source-native PDF member, downstream run id
`story223-mixed-folder-impl-r1-member-001-approved-handoff-recipe-born-digital-pdf-non-toc-html-mvp`,
and `terminal_reason = dry_run`. Supporting direct-entry members stayed intact:
the nested email bundle manifest at
`output/runs/story223-mixed-folder-impl-r1-member-002-recipe-email-eml-html-mvp/output/html/manifest.json`
still titles `Fixture Subject`, and the nested web bundle manifest at
`output/runs/story223-mixed-folder-impl-r1-member-004-recipe-web-page-html-mvp/output/html/manifest.json`
still carries entry title `Example Domain`. Outcome: Story 223 now proves the
bounded approved-handoff slice on both the checked-in ZIP and direct-folder
PDF-member entry surfaces while still keeping final maintained PDF launch as a
documented separate issue. Next step: `/validate 223`.

20260416-2008 — mark-story-done close-out: revalidated the completed Story 223
slice on the current branch tip and closed the reopened direct-folder parity
work inside the existing mixed-archive approved-handoff story line. Fresh
close-out checks in this pass: `make lint` → clean; `make test` →
`592 passed, 4 warnings in 680.10s (0:11:20)` with the same pre-existing
Pydantic deprecation warnings in
`modules/portionize/portionize_headers_numeric_v1/main.py`; and
`git diff --check` → clean. Reconfirmed the bounded runtime proof from the
fresh validation run `validate-story223-mixed-folder-20260416`: the stamped
route artifact at
`output/runs/validate-story223-mixed-folder-20260416/02_archive_route_members_v1/archive_member_routes.jsonl`
still records the source-native folder PDF member with
`terminal_reason = pdf_member_approved_handoff_dry_run`,
`approval_mode = confirm_plan_auto_approve`, and a populated
`handoff_artifact_path`; the approved plan artifact at
`output/runs/validate-story223-mixed-folder-20260416-member-001-recipe-intake-contact-sheet/05_confirm_plan_v1/overview_plan_final.jsonl`
still recommends
`configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml` with
`meta.source_input.source_pdf` pointing back to
`testdata/mixed-folder-pdf-mini/docs/proposal.pdf`; and the handoff sidecar at
`output/runs/validate-story223-mixed-folder-20260416/02_archive_route_members_v1/pdf_member_handoffs/member-001/intake_handoff.jsonl`
still records `launch_input_flag = --input-pdf`, the same source PDF, the
approved-handoff downstream run id, and `terminal_reason = dry_run`. Supporting
members remain intact in the same fresh validation run: the nested email
manifest still titles `Fixture Subject`, the nested web manifest still titles
`Example Domain`, and the parent route summary stayed
`launched=2, blocked=1, skipped=1`. Outcome: the maintained mixed-input claim
now honestly covers both the checked-in ZIP and direct-folder PDF-member
approved-handoff dry-run seams while still leaving final maintained PDF launch
out of scope. Next step: `/check-in-diff`.
