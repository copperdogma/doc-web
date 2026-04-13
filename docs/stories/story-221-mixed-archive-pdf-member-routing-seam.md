---
title: "Establish the First Honest Mixed-Archive PDF-Member Routing Seam"
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
depends_on:
  - "169"
  - "180"
  - "196"
  - "205"
  - "218"
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

# Story 221 — Establish the First Honest Mixed-Archive PDF-Member Routing Seam

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/stories/story-169-restore-contact-sheet-intake-and-benchmark-auto-book-type-detection.md`, `docs/stories/story-180-widen-approved-intake-handoff-image-directory-proof.md`, `docs/stories/story-194-office-intake-recommendation-and-handoff-boundary.md`, `docs/stories/story-196-widen-born-digital-pdf-proof-and-quality-surface.md`, `docs/stories/story-205-mixed-archive-intake-routing-seam.md`, `docs/stories/story-218-mixed-folder-direct-entry-seam.md`, `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, `modules/intake/intake_plan_utils.py`, `modules/intake/archive_route_members_v1/main.py`, `modules/intake/run_dispatch_v1/main.py`, `benchmarks/scripts/run_approved_intake_handoff_eval.py`, `benchmarks/scripts/run_auto_book_type_detection_eval.py`, and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower mixed-archive PDF-member routing ADR or runbook`
**Depends On**: Stories `169`, `180`, `196`, `205`, and `218`

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

Stories 205 and 218 closed the first honest mixed-archive ZIP and direct-folder
entry seams, but at story start the maintained mixed-archive lane still
explicitly excluded PDF-member routing:
`archive_route_members_v1` hard-blocked any detected `pdf` member with
`pdf_member_outside_bounded_mixed_archive_slice`, and the coverage matrix plus
methodology state both called PDF-member routing an open gap. This story lands
the first honest mixed-archive PDF-member slice without widening automation
semantics: one bounded repo-owned ZIP-contained flat born-digital PDF now
routes to an inspectable member-local recommendation artifact, while the `.eml`
and HTML members continue to launch through their existing maintained
direct-entry lanes and the unsupported `.txt` member stays explicitly blocked.
Direct-folder PDF-member parity and archive-contained approved handoff or final
maintained PDF launch remain out of scope.

## Acceptance Criteria

- [x] A fresh current-pass baseline names the exact mixed-archive PDF-member
      gap from repo evidence:
  - [x] the work log records that
        `tests/fixtures/formats/_coverage-matrix.json` and
        `docs/methodology/state.yaml` still treat PDF-member routing as
        intentionally unowned
  - [x] the work log records that
        `modules/intake/archive_route_members_v1/main.py` currently blocks any
        detected `pdf` member with
        `pdf_member_outside_bounded_mixed_archive_slice`
  - [x] the work log cites the verified reusable substrate honestly:
        `archive_member_manifest_v1` / `archive_member_route_v1` already exist,
        Story 205 and Story 218 already prove bounded archive-member dispatch
        for direct-entry families, and maintained PDF recommendation / handoff
        surfaces already exist outside archives in
        `modules/intake/intake_plan_utils.py`,
        `modules/intake/confirm_plan_v1/main.py`, and
        `modules/intake/run_dispatch_v1/main.py`
  - [x] the work log records which repo-owned PDF fixtures are viable first
        candidates and why the chosen candidate is the smallest honest slice
- [x] The story either lands one bounded mixed-archive PDF-member slice or
      closes `Blocked` honestly:
  - [x] one repo-owned bounded archive fixture exists under `testdata/` with at
        least one PDF member and capture / generation notes in
        `testdata/README.md`
  - [x] the chosen shipping slice writes an inspectable member route row for the
        PDF member that records the honest next step for that member:
        explicit launched downstream run, explicit member-local recommendation
        artifact, explicit member-local approved-handoff artifact, or explicit
        blocked outcome
  - [x] if the chosen slice launches downstream work, the first downstream
        stamped artifact exists under `output/runs/` and is manually inspected;
        if the chosen slice stops at recommendation or handoff, the emitted
        `intake_plan_v1` or `intake_handoff_v1` artifact is manually inspected
  - [x] if the current compromise boundary makes member-level launch dishonest,
        the story records the blocker explicitly instead of silently widening
        automation semantics
- [x] Mixed-archive PDF-member provenance stays source-honest on the claimed
      slice:
  - [x] archive-relative `member_path`, extracted or source-native member file
        path, and any downstream `run_id` or artifact paths remain inspectable
        end to end
  - [x] no combined archive-level HTML bundle, fabricated page anchors, or broad
        “supports PDFs inside archives” claim is introduced
  - [x] any new fields that cross artifact boundaries are added to `schemas.py`
        before stamped artifacts rely on them
- [x] Coverage, docs, and automation-boundary truth surfaces remain aligned with
      the outcome:
  - [x] `tests/fixtures/formats/_coverage-matrix.json`, `README.md`,
        `docs/RUNBOOK.md`, and `testdata/README.md` reflect the exact bounded
        PDF-member slice rather than a vague archive-PDF promise
  - [x] recommendation-only intake and approved-handoff eval surfaces only
        change if the story lands fresh current-pass proof that mixed-archive
        PDF members belong there
  - [x] grouped image-member interpretation, nested archives, attachment
        extraction, multi-PDF archive semantics, and broad heterogeneous
        archive ownership remain explicitly out of scope unless fresh evidence
        justifies separate follow-up work

## Out of Scope

- Grouped image-member interpretation or any archive-of-images seam
- Nested archives, attachments, `.msg`, mailbox/thread cleanup, or connector
  workflows
- Broad “any PDF inside any archive/folder” ownership beyond one bounded
  repo-owned fixture
- Widening both ZIP and direct-folder entry surfaces by default; folder parity
  is a follow-up unless the same implementation proves it honestly without a new
  truth-surface burden
- Auto-approving or auto-dispatching arbitrary PDF members without an explicit
  bounded approval story
- Reopening Story 191 or changing handwritten OCR behavior
- New `doc-web` output-contract architecture beyond the minimum inspectable
  member-route / recommendation / handoff artifacts needed to prove the bounded
  slice

## Approach Evaluation

- **Simplification baseline**: measured in this pass before implementation. The
  first honest baseline was not a brand-new archive-specific classifier; it was
  “how far can an existing repo-owned PDF member already travel through the
  maintained PDF intake / handoff surfaces with no new archive logic beyond
  routing glue?” The measured comparison covered:
  - direct current behavior (`pdf_member_outside_bounded_mixed_archive_slice`)
  - member-local recommendation-only intake on the extracted PDF member
  - member-local approved handoff only if the recommendation artifact can be
    approved honestly without widening global automation semantics
  Result: direct blocking was real, member-local recommendation-only intake was
  already viable on `flat-born-digital-mini.pdf`, and archive-level auto-launch
  was rejected because the approved-handoff reuse path still depended on an
  already-approved plan artifact rather than an honest unattended approval seam.
- **AI-only**: weak first move. Letting a model classify or route PDF members
  directly from archive context would duplicate the maintained PDF intake chain,
  hide provenance behind a new archive-specific prompt, and risk widening
  `spec:1.1` by accident.
- **Hybrid**: likely front-runner. Keep archive inventory, provenance, and
  routing orchestration deterministic in code, then reuse the existing PDF
  recommendation-only or approved-handoff surface only for the bounded PDF
  member decision.
- **Pure code**: only honest if baseline evidence shows one PDF subtype can be
  routed by deterministic repo-owned signals without inventing a new hidden
  policy. Do not assume this before measuring the candidate PDF member fixtures.
- **Repo constraints / prior decisions**: `spec:1.1` keeps recipe ownership
  explicit under `C2`; ADR-002 keeps the accepted `doc-web` boundary inspectable;
  Story 169 established recommendation-only intake, Story 180 widened the
  approved-handoff proof surface, Story 196 widened repo-owned born-digital PDF
  proof, and Stories 205 / 218 deliberately stopped before PDF-member routing.
  `docs/methodology/state.yaml` now explicitly records PDF-member routing as the
  next unproven archive seam.
- **Existing patterns to reuse**: `modules/intake/archive_unpack_manifest_v1`,
  `modules/intake/folder_members_manifest_v1`,
  `modules/intake/archive_route_members_v1`,
  `modules/intake/intake_plan_utils.py`,
  `modules/intake/contact_sheet_builder_v1`,
  `modules/intake/contact_sheet_overview_v1`,
  `modules/intake/confirm_plan_v1/main.py`,
  `modules/intake/run_dispatch_v1/main.py`,
  `benchmarks/scripts/run_approved_intake_handoff_eval.py`,
  `benchmarks/scripts/run_auto_book_type_detection_eval.py`,
  `tests/test_mixed_archive_zip_recipe.py`,
  `tests/test_mixed_folder_recipe.py`, and the repo-owned PDF fixtures already
  documented in `testdata/README.md`.
- **Eval**: the deciding proof surface is a fresh `driver.py` run on one
  repo-owned archive fixture with one PDF member. The winning approach must emit
  inspectable member-route evidence plus the smallest truthful downstream
  artifact: route row only, `intake_plan_v1`, `intake_handoff_v1`, or a first
  downstream recipe artifact. If this changes recommendation-only or
  approved-handoff truth, rerun the corresponding maintained eval surfaces and
  update `docs/evals/registry.yaml`.

## Tasks

- [x] Freeze the current mixed-archive PDF-member gap from repo reality:
  - [x] verify the `mixed-archive` coverage row and `state.yaml` audit note
        still exclude PDF-member routing
  - [x] verify `archive_route_members_v1` still blocks `pdf` members with the
        current explicit reason
  - [x] verify the existing PDF substrate that could be reused: repo-owned PDF
        fixtures, maintained PDF recipes, recommendation-only intake, and
        approved-handoff plumbing
- [x] Choose one bounded repo-owned PDF member candidate and fixture strategy:
  - [x] compare at least one born-digital candidate and one scanned-PDF
        candidate from the existing repo-owned fixture set
  - [x] default to a new ZIP-based probe fixture so Story 205's and Story 218's
        proven non-PDF seams stay stable while the first PDF-member variable is
        isolated
  - [x] document the chosen fixture and why it is the smallest honest slice
- [x] Measure the smallest honest baseline before adding new routing logic:
  - [x] current archive-route blocked behavior on the chosen PDF member
  - [x] existing recommendation-only intake on the member via `driver.py`
  - [x] approved-handoff feasibility only if recommendation-only output shows a
        bounded honest approval path
  - [x] do not introduce a new archive-specific prompt until those reuse paths
        are measured
- [x] Land the smallest coherent implementation the baseline justifies:
  - [x] add the minimum route/helper/schema changes needed to record the chosen
        PDF-member outcome honestly
  - [x] preserve existing non-PDF ZIP and folder behavior unchanged
  - [x] keep ZIP-only as the default shipping surface unless folder parity falls
        out with the same truth surface and no extra ambiguity
- [x] Add focused fixture-backed coverage for the chosen seam, including route
      semantics and any new member-local recommendation / handoff artifact
      expectations
- [x] If this story changes documented format coverage or graduation reality: update `tests/fixtures/formats/_coverage-matrix.json` and any relevant methodology state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through
        `driver.py`, verify artifacts in `output/runs/`, and manually inspect
        the member route rows plus the chosen PDF-member downstream artifacts
  - [x] If agent tooling changed: `make skills-check` (not needed; agent tooling unchanged)
- [x] If evals or goldens changed: rerun the relevant maintained intake surface
      via `/improve-eval` and update `docs/evals/registry.yaml` (not needed;
      evals and goldens unchanged)
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every PDF-member claim traces to the archive
        member path, member-local artifact, and inspected downstream artifact
  - [x] T1 — AI-First: no new archive-specific classifier is added if the
        existing maintained PDF intake surfaces already solve the member
        decision
  - [x] T2 — Eval Before Build: baseline member-routing candidates are measured
        before new glue lands
  - [x] T3 — Fidelity: the PDF member is not silently flattened, dropped, or
        mislabeled
  - [x] T4 — Modular: reuse the maintained archive route plus existing PDF
        recommendation / handoff seams instead of building a parallel stack
  - [x] T5 — Inspect Artifacts: route rows and the chosen PDF-member artifacts
        are manually opened and checked

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

- **Owning module / area**: intake and routing. The likely owner is
  `archive_route_members_v1` plus a small sibling helper or route-contract
  extension for PDF-member recommendation / handoff evidence, not a new general
  archive runtime.
- **Methodology reality**: this work belongs primarily to `spec:1`, with
  supporting ties to `spec:6`, `spec:7`, `spec:8`, and `spec:9`. In the current
  repo state, `spec:1` substrate exists, `spec:7` remains `partial`, and both
  `C2` and `B10` remain `climb`. The relevant coverage row is `mixed-archive`,
  which is currently `passing` only on the bounded DOCX / EML / HTML / TXT
  member mix and explicitly lists PDF-member routing as an unowned gap.
- **Substrate evidence**: verified in this pass that
  `modules/intake/archive_route_members_v1/main.py` exists and currently blocks
  `pdf` members with `pdf_member_outside_bounded_mixed_archive_slice`;
  `schemas.py` already defines `archive_member_manifest_v1` and
  `archive_member_route_v1`; `tests/test_mixed_archive_zip_recipe.py` and
  `tests/test_mixed_folder_recipe.py` already prove the bounded non-PDF archive
  seams; `modules/intake/intake_plan_utils.py` already exposes maintained PDF
  recipe selection plus confirmed-handoff helpers; and repo-owned PDF fixtures
  already exist under `testdata/` (`tbotb-mini.pdf`,
  `born-digital-handbook-mini.pdf`, `flat-born-digital-mini.pdf`,
  `scanned-prose-mini.pdf`, `scanned-prose-degraded.pdf`).
- **Data contracts / schemas**: likely touched contracts are
  `archive_member_route_v1`, and possibly `archive_member_manifest_v1` if the
  chosen slice needs extra member-local routing metadata. The preferred outcome
  is to keep `intake_plan_v1` and `intake_handoff_v1` unchanged and only add
  route-schema fields if member-local plan or handoff artifact paths must cross
  a stamped boundary.
- **File sizes**: likely owner files are
  `modules/intake/archive_route_members_v1/main.py` (238),
  `modules/intake/intake_plan_utils.py` (419), `schemas.py` (1373, oversized),
  `tests/test_mixed_archive_zip_recipe.py` (138),
  `tests/test_mixed_folder_recipe.py` (145),
  `modules/intake/run_dispatch_v1/main.py` (91),
  `modules/intake/confirm_plan_v1/main.py` (52), `driver.py` (3204, oversized),
  `README.md` (502, oversized), `docs/RUNBOOK.md` (836, oversized),
  `tests/fixtures/formats/_coverage-matrix.json` (570, oversized), and
  `testdata/README.md` (149). Keep edits especially surgical in `schemas.py`,
  `driver.py`, `README.md`, `docs/RUNBOOK.md`, and the coverage matrix.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`,
  `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, Stories
  169 / 180 / 194 / 196 / 205 / 218, the `mixed-archive` coverage row,
  `README.md`, `docs/RUNBOOK.md`, `modules/intake/intake_plan_utils.py`,
  `modules/intake/archive_route_members_v1/main.py`,
  `modules/intake/run_dispatch_v1/main.py`,
  `benchmarks/scripts/run_approved_intake_handoff_eval.py`, and
  `benchmarks/scripts/run_auto_book_type_detection_eval.py`. No narrower
  mixed-archive PDF-member ADR or runbook was found after search.

## Files to Modify

- `docs/stories/story-221-mixed-archive-pdf-member-routing-seam.md` — story
  scope, plan, and work log (127 lines before this edit)
- `modules/intake/archive_route_members_v1/main.py` — extend bounded routing for
  the chosen ZIP-only PDF-member outcome without regressing the existing non-PDF seams
  (238 lines)
- `modules/intake/intake_plan_utils.py` — add or refine shared member-local PDF
  recommendation-run helpers only if the chosen slice needs them (419 lines)
- `tests/test_mixed_archive_zip_recipe.py` — fixture-backed ZIP smoke for the
  chosen PDF-member behavior (138 lines)
- `schemas.py` — touch only if the existing route fields cannot honestly point
  at the member-local recommendation artifact after implementation (1373 lines)
- `testdata/README.md` — record source and generation notes for the new archive
  fixture (149 lines)
- `README.md` — align user-facing wording with the exact supported PDF-member
  slice if one lands (502 lines)
- `docs/RUNBOOK.md` — document the verified proof command and artifact checks
  for the bounded slice (836 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — widen the `mixed-archive`
  claim only as far as fresh current-pass PDF-member evidence justifies (570
  lines)
- `testdata/mixed-archive-pdf-mini.source.json` and the corresponding checked-in
  archive fixture — repo-owned bounded PDF-member proof asset (new files)
- `benchmarks/scripts/run_approved_intake_handoff_eval.py`,
  `benchmarks/scripts/run_auto_book_type_detection_eval.py`, and
  `docs/evals/registry.yaml` — leave untouched unless implementation evidence
  unexpectedly changes automation truth (341, 221, and current registry size
  respectively)

## Redundancy / Removal Targets

- Any ad hoc local PDF-member archive probes once a maintained repo-owned
  archive fixture and smoke test exist
- Any stale wording that implies mixed-archive still stops at the
  DOCX / EML / HTML / TXT member mix after a bounded PDF-member slice lands
- Any temptation to clone the entire PDF intake chain inside archive routing
  instead of reusing the maintained recommendation / handoff substrate
- Any workflow wording that accidentally promotes archive-contained PDF routing
  into broad automatic archive ownership

## Notes

- New story justification: reopening Stories 205 or 218 would not be honest.
  Both stories are closed proofs for bounded non-PDF member dispatch and both
  explicitly left PDF-member routing out of scope. The missing work here is a
  new success surface: member-local PDF recommendation / approval / dispatch
  semantics inside archives.
- Default first fixture shape: one new ZIP probe with one repo-owned PDF member
  plus a small number of already-proven non-PDF members, so the only new
  variable is the PDF-member seam rather than the entire archive lane.
- Candidate first PDF members should prefer repo-owned fixtures with already
  passing downstream proof surfaces. A flat born-digital or bounded book-like
  born-digital fixture is a better first candidate than a degraded scanned PDF
  if the goal is the smallest honest launchable slice.
- Fresh `/build-story` exploration now narrows that advice further: use
  `flat-born-digital-mini.pdf` as the first checked-in PDF member candidate and
  keep `scanned-prose-mini.pdf` only as a negative baseline. The flat fixture
  already produces a maintained non-TOC PDF recommendation and a clean
  downstream `doc-web` bundle once fed through the existing member-local
  recommendation and handoff helpers; the scanned fixture currently bottoms out
  at `recommended_recipe = no-recipe-needed`, so it is a bad first ownership
  slice for this story.
- The confirmed-handoff reuse surface is real but not automatically honest from
  inside archive routing yet. A fresh current-pass run of
  `recipe-intake-contact-sheet-confirmed-handoff.yaml` on
  `flat-born-digital-mini.pdf` failed at `confirm_plan_v1` with `EOFError`
  because that recipe still expects an interactive approval prompt. A manual
  `run_dispatch_v1` call against an already-written plan artifact does launch
  cleanly, but using that inside archive routing would silently turn
  recommendation-only output into implicit approval. The recommended first
  shipping slice should therefore stop at a member-local recommendation artifact
  unless the user explicitly approves a larger approval-semantics expansion.

## Plan

Alignment check:
- This story still moves toward the Ideal rather than away from it. It closes a
  real `spec:1.1` / `C2` gap in the maintained archive intake surface, keeps the
  accepted `doc-web` boundary intact under ADR-002, and reuses existing PDF
  recommendation / handoff seams instead of inventing a new archive-specific
  classifier by default.
- No narrower mixed-archive PDF-member ADR or runbook was found in this pass.

Measured current-pass baseline:
- `tests/fixtures/formats/_coverage-matrix.json` and
  `docs/methodology/state.yaml` both still treat PDF-member routing as outside
  the bounded mixed-archive claim.
- `modules/intake/archive_route_members_v1/main.py` explicitly blocks any
  detected `pdf` member with
  `pdf_member_outside_bounded_mixed_archive_slice`.
- Story 205 and Story 218 already proved the underlying archive inventory and
  non-PDF member dispatch seams through `archive_member_manifest_v1` and
  `archive_member_route_v1`.
- The PDF substrate is already real outside archives: maintained repo-owned PDF
  fixtures exist under `testdata/`, `modules/intake/intake_plan_utils.py`
  already chooses maintained PDF recipes, recommendation-only intake is live
  from Story 169, and approved handoff is live and freshly re-proved from Story
  180 through the 2026-04-13 eval refresh.
- Baseline runs from this pass:
  - `python driver.py --recipe configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml --input-zip /tmp/story221-flat-born-digital-member.zip --run-id story221-flat-member-blocked-r1 --allow-run-id-reuse --force`
    produced `launched=2`, `blocked=2`, `skipped=0`, `failed=0`; the inspected
    PDF route row at
    `output/runs/story221-flat-member-blocked-r1/02_archive_route_members_v1/archive_member_routes.jsonl`
    shows `member_path = docs/member.pdf`,
    `detected_input_kind = pdf`, and
    `terminal_reason = pdf_member_outside_bounded_mixed_archive_slice`.
  - `python driver.py --recipe configs/recipes/recipe-intake-contact-sheet.yaml --input-pdf testdata/flat-born-digital-mini.pdf --run-id story221-flat-intake-r1 --allow-run-id-reuse --force`
    wrote
    `output/runs/story221-flat-intake-r1/05_confirm_plan_v1/overview_plan_final.jsonl`
    with `recommended_recipe = configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`,
    `book_type = other`, `signals = [forms]`, and a bounded warning for missing
    `forms` capability.
  - `python driver.py --recipe configs/recipes/recipe-intake-contact-sheet.yaml --input-pdf testdata/scanned-prose-mini.pdf --run-id story221-scanned-intake-r1 --allow-run-id-reuse --force`
    wrote
    `output/runs/story221-scanned-intake-r1/05_confirm_plan_v1/overview_plan_final.jsonl`
    with `recommended_recipe = no-recipe-needed`, so the scanned probe does not
    justify the first owned archive-member slice.
  - `python modules/intake/run_dispatch_v1/main.py --plan output/runs/story221-flat-intake-r1/05_confirm_plan_v1/overview_plan_final.jsonl --out output/runs/story221-flat-intake-r1/06_manual_run_dispatch_v1/intake_handoff.jsonl --run-id story221-flat-manual-dispatch-r1 --allow-run-id-reuse --dry-run`
    wrote a clean `intake_handoff_v1` preview row showing
    `launch_input_path = testdata/flat-born-digital-mini.pdf`.
  - `python modules/intake/run_dispatch_v1/main.py --plan output/runs/story221-flat-intake-r1/05_confirm_plan_v1/overview_plan_final.jsonl --out output/runs/story221-flat-intake-r1/06_manual_run_dispatch_v1/intake_handoff_launch.jsonl --run-id story221-flat-manual-dispatch-r1 --allow-run-id-reuse`
    launched
    `story221-flat-manual-dispatch-r1-recipe-born-digital-pdf-non-toc-html-mvp`
    successfully. Manual inspection in this pass confirmed the handoff row at
    `output/runs/story221-flat-intake-r1/06_manual_run_dispatch_v1/intake_handoff_launch.jsonl`,
    the first stamped downstream HTML rows at
    `output/runs/story221-flat-manual-dispatch-r1-recipe-born-digital-pdf-non-toc-html-mvp/01_extract_pdf_marker_lite_html_v1/pages_html.jsonl`,
    the final bundle manifest at
    `output/runs/story221-flat-manual-dispatch-r1-recipe-born-digital-pdf-non-toc-html-mvp/output/html/manifest.json`,
    and provenance rows at
    `output/runs/story221-flat-manual-dispatch-r1-recipe-born-digital-pdf-non-toc-html-mvp/output/html/provenance/blocks.jsonl`.
    Page 1 begins with the heading `Acme Community Arts Initiative`, the bundle
    exposes `Requested information:` / `Accessibility notes:` chapter entries,
    and provenance quotes retain page-local text.
- Constraint surfaced by the same pass: a direct
  `python driver.py --recipe configs/recipes/recipe-intake-contact-sheet-confirmed-handoff.yaml --input-pdf testdata/flat-born-digital-mini.pdf --run-id story221-flat-approved-r1 --allow-run-id-reuse --force`
  run failed at `confirm_plan_v1` with `EOFError` because that recipe does not
  pass `auto_approve`. The approved-handoff substrate exists, but archive
  routing cannot honestly treat it as an unattended member-level launch seam
  without widening approval semantics.
- Result: this story is honestly `Pending`, not `Draft`. The critical runtime
  substrate already exists; the missing work is choosing and proving the first
  bounded archive-contained PDF-member route.

Recommended shipping slice:
- Keep this story ZIP-only.
- Choose `flat-born-digital-mini.pdf` as the first repo-owned PDF member
  candidate and package it inside a new checked-in
  `testdata/mixed-archive-pdf-mini.zip` alongside the already-proven `.eml`,
  HTML, and unsupported `.txt` members so the only new variable is the PDF
  member.
- Land a member-local recommendation seam, not an archive-level auto-launch
  seam. The PDF member should launch a nested
  `configs/recipes/recipe-intake-contact-sheet.yaml` run, record the resulting
  `overview_plan_final.jsonl` as the first downstream artifact, and stop there.
  This preserves provenance and surfaces the honest next step without silently
  converting recommendation output into unattended approval.
- Treat “auto-launch the recommended maintained PDF recipe from inside archive
  routing” as a larger follow-on scope expansion that is not included in this
  plan. That expansion would need an explicit approval contract rather than
  reusing auto-approved recommendation artifacts.

Implementation order:
1. Fixture and docs
   - Add `testdata/mixed-archive-pdf-mini.source.json` plus a checked-in ZIP
     fixture built from `flat-born-digital-mini.pdf`, `email-eml-mini.eml`,
     `web-page-mini.html`, and a bounded unsupported `.txt` member.
   - Update `testdata/README.md` with capture / regeneration notes for that ZIP.
   - Done looks like: the fixture is reproducible, checked in, and isolated to
     one new variable.
2. ZIP route behavior
   - Extend `archive_route_members_v1/main.py` so detected `pdf` members launch
     a nested recommendation-only intake run instead of blocking immediately.
   - Reuse existing `build_explicit_recipe_driver_command()` plumbing for the
     nested `driver.py` invocation and only add a tiny helper if deriving the
     plan artifact path or nested run id becomes repetitive.
   - Keep non-PDF ZIP behavior unchanged and do not widen folder parity.
   - Done looks like: the PDF member row points at the nested recommendation
     run and its inspected `intake_plan_v1` artifact instead of the old blocked
     reason.
3. Route-row contract
   - Prefer staying within the current `archive_member_route_v1` fields by
     treating the nested recommendation run as the downstream run and its
     `overview_plan_final.jsonl` artifact as `first_downstream_artifact`.
   - Populate `recommended_recipe` from the emitted member-local plan artifact
     if that stays clear; touch `schemas.py` only if a truly new path or status
     field is required after implementation.
   - Use an explicit non-terminal reason such as
     `pdf_member_recommendation_only` if needed to make the bounded stop
     obvious.
   - Done looks like: the route row itself explains why the flow stops where it
     does, and the artifact chain is inspectable end to end.
4. Focused proof
   - Add a ZIP smoke test in `tests/test_mixed_archive_zip_recipe.py` that
     proves the PDF member now launches the nested recommendation-only run,
     writes a plan artifact, preserves archive-relative provenance, keeps the
     `.eml` / HTML launches intact, and still blocks the unsupported `.txt`
     member.
   - Run the narrowest real `driver.py` proof on the checked-in fixture and
     manually inspect the route row plus the emitted plan artifact.
   - Done looks like: one repo-owned ZIP proof passes with inspected
     recommendation output for the PDF member.
5. Truth surfaces
   - Update `README.md`, `docs/RUNBOOK.md`, and
     `tests/fixtures/formats/_coverage-matrix.json` only to the exact bounded
     recommendation-only claim.
   - Leave `docs/evals/registry.yaml` and the approved-handoff / recommendation
     eval surfaces untouched unless implementation evidence unexpectedly proves
     a broader automation boundary.
   - Done looks like: the repo claims exactly one ZIP-only PDF-member
     recommendation seam and nothing broader.

Human-approval scope boundary:
- Recommended scope to implement now: ZIP-only PDF-member recommendation seam on
  `flat-born-digital-mini.pdf` with no archive-level auto-launch and no folder
  parity.
- Not included unless explicitly approved: member-local approved-handoff
  automation, direct archive-to-final-recipe launch for PDF members, folder
  parity, scanned-PDF ownership, or broader mixed-archive PDF claims.

## Work Log

20260413-0744 — story created from approved post-eval next step: verified that a new story is honest rather than reopening Stories 205 or 218 because both closed bounded non-PDF archive-member seams and both explicitly left PDF-member routing out of scope. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, the `mixed-archive` coverage row, ADR-002, Stories 169 / 180 / 194 / 196 / 205 / 218, `modules/intake/archive_route_members_v1/main.py`, `modules/intake/intake_plan_utils.py`, `modules/intake/run_dispatch_v1/main.py`, `tests/test_mixed_archive_zip_recipe.py`, and `tests/test_mixed_folder_recipe.py`. Fresh repo-backed baseline: the mixed-archive row is still bounded to the DOCX / EML / HTML / TXT member mix, the route module still blocks `pdf` members explicitly, and the maintained PDF recommendation / handoff substrate plus repo-owned PDF fixtures already exist. Result: Story 221 starts `Pending` because the missing work is selecting and proving the first honest PDF-member route, not inventing a prerequisite runtime. Next step: `/build-story` should measure the bounded candidate routes on one repo-owned archive-contained PDF member and choose the smallest honest shipping slice.
20260413-0909 — `/build-story` exploration froze the first honest scope around a ZIP-only member-local recommendation seam, not archive-level auto-launch. Fresh current-pass evidence: `tests/fixtures/formats/_coverage-matrix.json` and `docs/methodology/state.yaml` still mark mixed-archive PDF-member routing as unowned; `modules/intake/archive_route_members_v1/main.py` still hard-blocks `pdf` members with `pdf_member_outside_bounded_mixed_archive_slice`; and a baseline mixed-archive probe run at `output/runs/story221-flat-member-blocked-r1/02_archive_route_members_v1/archive_member_routes.jsonl` confirmed that exact blocked row on `docs/member.pdf` while the `.eml` and HTML members still launched. Candidate comparison: `flat-born-digital-mini.pdf` produced a viable member-local plan at `output/runs/story221-flat-intake-r1/05_confirm_plan_v1/overview_plan_final.jsonl` with `recommended_recipe = configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`, while `scanned-prose-mini.pdf` produced `recommended_recipe = no-recipe-needed` at `output/runs/story221-scanned-intake-r1/05_confirm_plan_v1/overview_plan_final.jsonl`, so the scanned probe is not the first honest ownership slice. Approved-handoff feasibility check: a direct run of `recipe-intake-contact-sheet-confirmed-handoff.yaml` failed at `confirm_plan_v1` with `EOFError`, proving that the existing recipe still expects interactive approval; however, a manual `run_dispatch_v1` dry-run wrote a clean handoff preview at `output/runs/story221-flat-intake-r1/06_manual_run_dispatch_v1/intake_handoff.jsonl`, and a real `run_dispatch_v1` launch from that already-written plan produced a successful handoff row at `output/runs/story221-flat-intake-r1/06_manual_run_dispatch_v1/intake_handoff_launch.jsonl` plus inspected downstream HTML / bundle artifacts under `output/runs/story221-flat-manual-dispatch-r1-recipe-born-digital-pdf-non-toc-html-mvp/`. Manual inspection in this pass verified that the first downstream stamped HTML row begins with `Acme Community Arts Initiative`, the final bundle manifest exposes `Requested information:` and `Accessibility notes:` chapter entries, and provenance rows preserve page-local text quotes. Decision: recommend implementing only the ZIP-only member-local recommendation seam on a new checked-in `mixed-archive-pdf-mini.zip` fixture, because it reuses real substrate, preserves provenance, and avoids silently converting recommendation output into implicit approval. Next step: get user approval for that bounded implementation plan before writing code.
20260413-0958 — implemented the bounded ZIP-only PDF-member recommendation seam and revalidated it end to end. Runtime/files changed in this pass: `modules/intake/archive_route_members_v1/main.py` now routes ZIP-contained `pdf` members into the nested recommendation-only recipe `configs/recipes/recipe-intake-contact-sheet.yaml`, records the emitted `overview_plan_final.jsonl` path as `first_downstream_artifact`, copies the member-local recommended maintained PDF recipe onto the route row, and tags the bounded stop as `terminal_reason = pdf_member_recommendation_only`; `tests/test_mixed_archive_zip_recipe.py` now adds focused coverage for ZIP-contained PDF recommendation routing plus an explicit guard that folder-contained PDF members stay blocked; `testdata/mixed-archive-pdf-mini.source.json` and `testdata/mixed-archive-pdf-mini.zip` add the checked-in four-member probe; `testdata/README.md`, `README.md`, `docs/RUNBOOK.md`, `tests/fixtures/formats/_coverage-matrix.json`, and `docs/methodology/state.yaml` now all describe the same bounded claim. Critical implementation note: no `schemas.py` or `intake_plan_utils.py` changes were needed because the existing `archive_member_route_v1` fields were sufficient once the route row treated the nested recommendation run as the downstream run and its final plan artifact as `first_downstream_artifact`. Focused checks in this pass: `python -m pytest tests/test_mixed_archive_zip_recipe.py -q` → `5 passed`; `python -m ruff check modules/intake/archive_route_members_v1/main.py tests/test_mixed_archive_zip_recipe.py` → clean; repo-wide `make lint` → clean; repo-wide `make test` → `588 passed, 4 warnings`; fresh post-`pyc` proof via `find modules -name '*.pyc' -delete` then `python driver.py --recipe configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml --input-zip testdata/mixed-archive-pdf-mini.zip --run-id story221-mixed-archive-pdf-mini-r2 --allow-run-id-reuse --force` completed with `Archive routing complete: launched=3, blocked=1, skipped=0, failed=0`; `validate_artifact.py` passed on the stamped manifest, route, and emitted plan artifact. Manual artifact inspection in the fresh `r2` run: `output/runs/story221-mixed-archive-pdf-mini-r2/02_archive_route_members_v1/archive_member_routes.jsonl` first row shows `member_path = docs/proposal.pdf`, `recommended_recipe = configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`, `first_downstream_artifact = .../05_confirm_plan_v1/overview_plan_final.jsonl`, and `terminal_reason = pdf_member_recommendation_only`; `output/runs/story221-mixed-archive-pdf-mini-r2-member-001-recipe-intake-contact-sheet/05_confirm_plan_v1/overview_plan_final.jsonl` shows `book_type = other`, `signals = [forms]`, `warnings = [Missing capabilities: forms]`, and `meta.source_input.source_pdf` pointing back to the extracted archive member; `output/runs/story221-mixed-archive-pdf-mini-r2-member-002-recipe-email-eml-html-mvp/output/html/manifest.json` still titles the email bundle `Fixture Subject`; and `output/runs/story221-mixed-archive-pdf-mini-r2-member-003-recipe-web-page-html-mvp/output/html/manifest.json` still exposes `Example Domain`. Residual boundary held intentionally: folder-contained PDF members stay blocked, the archive lane still does not auto-approve or auto-launch the final maintained PDF recipe, and no eval registry entries changed because the top-level recommendation-only and approved-handoff automation surfaces remain unchanged. Next step: hand off to `/validate 221`.
20260413-1027 — `/mark-story-done` close-out validation confirmed Story 221 is complete on the current branch and safe to close. Fresh current-pass validation in this close-out step: `python -m pytest tests/` → `588 passed, 4 warnings`; `python -m ruff check modules/ tests/` → clean; `find modules -name '*.pyc' -delete` then `python driver.py --recipe configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml --input-zip testdata/mixed-archive-pdf-mini.zip --run-id story221-mixed-archive-pdf-mini-close-r1 --allow-run-id-reuse --force` completed with `Archive routing complete: launched=3, blocked=1, skipped=0, failed=0`; `python validate_artifact.py --schema archive_member_manifest_v1 --file output/runs/story221-mixed-archive-pdf-mini-close-r1/01_archive_unpack_manifest_v1/archive_members_manifest.jsonl`, `python validate_artifact.py --schema archive_member_route_v1 --file output/runs/story221-mixed-archive-pdf-mini-close-r1/02_archive_route_members_v1/archive_member_routes.jsonl`, and `python validate_artifact.py --schema intake_plan_v1 --file output/runs/story221-mixed-archive-pdf-mini-close-r1-member-001-recipe-intake-contact-sheet/05_confirm_plan_v1/overview_plan_final.jsonl` all passed. Manual inspection in the fresh close-out run reconfirmed the PDF member route row at `output/runs/story221-mixed-archive-pdf-mini-close-r1/02_archive_route_members_v1/archive_member_routes.jsonl` with `recommended_recipe = configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`, `first_downstream_artifact = .../05_confirm_plan_v1/overview_plan_final.jsonl`, and `terminal_reason = pdf_member_recommendation_only`; the emitted plan at `output/runs/story221-mixed-archive-pdf-mini-close-r1-member-001-recipe-intake-contact-sheet/05_confirm_plan_v1/overview_plan_final.jsonl` still reports `book_type = other`, `signals = [forms]`, `warnings = [Missing capabilities: forms]`, and `meta.source_input.source_pdf` pointing back to the extracted archive member; the nested email bundle at `output/runs/story221-mixed-archive-pdf-mini-close-r1-member-002-recipe-email-eml-html-mvp/output/html/manifest.json` still titles `Fixture Subject`; and the nested web bundle at `output/runs/story221-mixed-archive-pdf-mini-close-r1-member-003-recipe-web-page-html-mvp/output/html/manifest.json` still carries the `Example Domain` chapter. Story status moved to `Done`, the validation and `/mark-story-done` workflow gates are now checked, and the remaining landing step is `/check-in-diff`.
