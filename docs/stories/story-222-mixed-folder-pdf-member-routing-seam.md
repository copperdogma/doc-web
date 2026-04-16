---
title: "Establish the First Honest Mixed-Folder PDF-Member Routing Seam"
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
  - "221"
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

# Story 222 — Establish the First Honest Mixed-Folder PDF-Member Routing Seam

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/stories/story-169-restore-contact-sheet-intake-and-benchmark-auto-book-type-detection.md`, `docs/stories/story-180-widen-approved-intake-handoff-image-directory-proof.md`, `docs/stories/story-196-widen-born-digital-pdf-proof-and-quality-surface.md`, `docs/stories/story-205-mixed-archive-intake-routing-seam.md`, `docs/stories/story-218-mixed-folder-direct-entry-seam.md`, `docs/stories/story-221-mixed-archive-pdf-member-routing-seam.md`, `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, `schemas.py`, `driver.py`, `modules/intake/intake_plan_utils.py`, `modules/intake/archive_route_members_v1/main.py`, `modules/intake/folder_members_manifest_v1/main.py`, `tests/test_mixed_folder_recipe.py`, `tests/test_mixed_archive_zip_recipe.py`, and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower mixed-folder PDF-member routing ADR or runbook`
**Depends On**: Stories `169`, `180`, `196`, `205`, `218`, and `221`

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

Stories 218 and 221 closed the first honest mixed-folder direct-entry seam and
the first honest ZIP-only PDF-member recommendation seam, but at story start
the maintained `mixed-archive` row still explicitly excluded direct-folder
PDF-member parity and `archive_route_members_v1` still hard-blocked
folder-contained `pdf` members with
`pdf_member_outside_bounded_mixed_archive_slice`. This story lands the first
honest direct-folder PDF-member continuation without widening automation
semantics: one bounded repo-owned source-native folder containing a PDF member
plus the existing `.eml` / HTML / blocked `.txt` mix now routes the PDF member
to an inspectable member-local recommendation artifact while preserving the
existing launched and blocked outcomes for the non-PDF members.
Archive-contained approved handoff or final maintained PDF launch remain out of
scope.

## Acceptance Criteria

- [x] A fresh current-pass baseline names the exact mixed-folder PDF-member gap
      from repo evidence:
  - [x] the work log records that
        `tests/fixtures/formats/_coverage-matrix.json` and
        `docs/methodology/state.yaml` still treat direct-folder PDF-member
        parity as intentionally unowned
  - [x] the work log records that
        `modules/intake/archive_route_members_v1/main.py` and
        `tests/test_mixed_archive_zip_recipe.py` still block folder-contained
        `pdf` members with `pdf_member_outside_bounded_mixed_archive_slice`
  - [x] the work log cites the verified reusable substrate honestly:
        `input_folder` / `--input-folder`, `folder_members_manifest_v1`,
        `archive_member_manifest_v1`, `archive_member_route_v1`,
        Story 218's source-native folder proof, Story 221's ZIP-only
        PDF-member recommendation proof, and the maintained PDF
        recommendation / handoff surfaces in `modules/intake/intake_plan_utils.py`,
        `modules/intake/confirm_plan_v1/main.py`, and
        `modules/intake/run_dispatch_v1/main.py`
  - [x] the work log records which repo-owned PDF fixtures are viable first
        candidates and why the chosen folder-backed candidate is the smallest
        honest slice
- [x] The story either lands one bounded mixed-folder PDF-member slice or
      closes `Blocked` honestly:
  - [x] one repo-owned bounded folder fixture exists under `testdata/` with at
        least one PDF member and capture / generation notes in
        `testdata/README.md`
  - [x] the chosen shipping slice writes an inspectable route row for the PDF
        member that records the honest next step for that member: explicit
        launched downstream run, explicit member-local recommendation artifact,
        explicit member-local approved-handoff artifact, or explicit blocked
        outcome
  - [x] if the chosen slice launches downstream work, the first downstream
        stamped artifact exists under `output/runs/` and is manually inspected;
        if the chosen slice stops at recommendation or handoff, the emitted
        `intake_plan_v1` or `intake_handoff_v1` artifact is manually inspected
  - [x] if the current compromise boundary makes member-level launch dishonest,
        the story records the blocker explicitly instead of silently widening
        automation semantics
- [x] Mixed-folder PDF-member provenance stays source-honest on the claimed
      slice:
  - [x] relative `member_path`, source-native member file path, and any
        downstream `run_id` or artifact paths remain inspectable end to end
  - [x] no synthetic archive wrapper, combined folder-level HTML bundle, or
        fabricated page anchors are introduced
  - [x] any new fields that cross artifact boundaries are added to `schemas.py`
        before stamped artifacts rely on them
- [x] Coverage, docs, and automation-boundary truth surfaces remain aligned
      with the outcome:
  - [x] `tests/fixtures/formats/_coverage-matrix.json`, `README.md`,
        `docs/RUNBOOK.md`, and `testdata/README.md` reflect the exact bounded
        folder PDF-member slice rather than a vague direct-folder PDF promise
  - [x] recommendation-only intake and approved-handoff eval surfaces stayed
        unchanged because the bounded folder PDF-member continuation still
        begins from explicit `--input-folder` entry and stops at a nested
        member-local recommendation artifact instead of widening either
        top-level automation surface
  - [x] ZIP-only PDF-member proof, existing non-PDF folder proof, grouped
        image-member interpretation, nested archives, attachment extraction,
        archive-contained approved handoff, final maintained PDF launch, and
        broad heterogeneous archive ownership remain explicitly out of scope
        unless fresh evidence justifies separate follow-up work

## Out of Scope

- Grouped image-member interpretation or any archive-of-images seam
- Nested archives, attachments, `.msg`, mailbox/thread cleanup, or connector
  workflows
- Broad “any PDF inside any folder/archive” ownership beyond one bounded
  repo-owned fixture
- Auto-approving or auto-dispatching arbitrary folder-contained PDF members
  without an explicit bounded approval story
- Reopening Story 191 or changing handwritten OCR behavior
- New `doc-web` output-contract architecture beyond the minimum inspectable
  member-route / recommendation / handoff artifacts needed to prove the bounded
  slice

## Approach Evaluation

- **Simplification baseline**: measured in the current pass before any code
  change. The first honest baseline was not a new folder-specific classifier;
  it was “how far can a source-native PDF member already travel through the
  maintained PDF intake / handoff surfaces with no new folder logic beyond
  parity glue?” The measured comparison covered current folder-route blocked
  behavior plus member-local recommendation-only intake on one born-digital
  candidate (`flat-born-digital-mini.pdf`) and one scanned candidate
  (`scanned-prose-mini.pdf`). Result: the pre-fix folder route baseline blocked
  the PDF member explicitly, the born-digital candidate emitted an inspectable
  `overview_plan_final.jsonl` with
  `recommended_recipe = configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`,
  the scanned candidate emitted an inspectable recommendation artifact with
  `recommended_recipe = no-recipe-needed`. That makes the born-digital PDF the
  smallest honest shipping slice, and the implemented route now reuses that
  same recommendation-only path on the checked-in direct-folder probe while
  keeping scanned comparison evidence in the work log.
- **AI-only**: weak first move. Letting a model classify or route folder
  members directly from directory context would duplicate the maintained PDF
  intake chain, hide provenance behind a new prompt, and risk widening
  `spec:1.1` by accident.
- **Hybrid**: likely front-runner. Keep folder inventory and routing
  orchestration deterministic in code, then reuse the existing PDF
  recommendation-only or approved-handoff surface only for the bounded PDF
  member decision.
- **Pure code**: only honest if baseline evidence shows one folder-contained PDF
  subtype can reuse the existing recommendation surface without inventing a new
  hidden policy. Do not assume this before measuring the candidate fixtures.
- **Repo constraints / prior decisions**: `spec:1.1` keeps recipe ownership
  explicit under `C2`; ADR-002 keeps the accepted `doc-web` boundary
  inspectable; Story 218 deliberately stopped before PDF-member routing while
  Story 221 deliberately stopped at ZIP-only recommendation, not folder parity
  or archive-contained approval. At story start the coverage row and
  methodology state named direct-folder PDF-member routing as an open gap; the
  implemented slice closes that gap only for one born-digital direct-folder
  recommendation path and still avoids silently widening approval semantics.
- **Existing patterns to reuse**: `modules/intake/folder_members_manifest_v1`,
  `modules/intake/archive_route_members_v1`,
  `modules/intake/intake_plan_utils.py`,
  `modules/intake/confirm_plan_v1/main.py`,
  `modules/intake/run_dispatch_v1/main.py`,
  `tests/test_mixed_folder_recipe.py`,
  `tests/test_mixed_archive_zip_recipe.py`, Story 218's checked-in folder
  proof, Story 221's ZIP-only PDF-member recommendation proof, and the existing
  repo-owned PDF fixtures already documented in `testdata/README.md`.
- **Eval**: the deciding proof surface is a fresh `driver.py` run on one
  repo-owned folder fixture with one PDF member. The winning approach must emit
  inspectable member-route evidence plus the smallest truthful downstream
  artifact: route row only, `intake_plan_v1`, `intake_handoff_v1`, or a first
  downstream recipe artifact. If this changes recommendation-only or approved-
  handoff truth, rerun the corresponding maintained intake surfaces and update
  `docs/evals/registry.yaml`.

## Tasks

- [x] Freeze the current mixed-folder PDF-member gap from repo reality:
  - [x] verify the `mixed-archive` coverage row and `state.yaml` audit note
        still exclude direct-folder PDF-member parity
  - [x] verify `archive_route_members_v1` plus the focused regression test
        still block folder-contained `pdf` members with the current explicit
        reason
  - [x] verify the existing reusable substrate honestly: `input_folder`,
        `folder_members_manifest_v1`, shared route/dispatch schemas, Story 218's
        source-native folder proof, Story 221's ZIP-only PDF-member
        recommendation proof, and the maintained PDF recommendation / handoff
        plumbing
- [x] Choose one bounded repo-owned folder PDF candidate and fixture strategy:
  - [x] compare at least one born-digital candidate and one scanned-PDF
        candidate from the existing repo-owned fixture set
  - [x] default to a new checked-in folder probe that mirrors Story 221's
        four-member ZIP PDF fixture so the only new variable is the direct-
        folder entry surface
  - [x] document the chosen fixture and why it is the smallest honest slice
- [x] Measure the smallest honest baseline before adding new routing logic:
  - [x] current folder-route blocked behavior on the chosen PDF member
  - [x] existing recommendation-only intake on the source-native member via
        `driver.py`
  - [x] approved-handoff feasibility only if recommendation-only output shows a
        bounded honest approval path
  - [x] do not introduce a new folder-specific or archive-specific prompt until
        those reuse paths are measured
- [x] Land the smallest coherent implementation the baseline justifies:
  - [x] add the minimum route/helper/fixture changes needed to record the
        chosen folder PDF-member outcome honestly
  - [x] preserve existing non-PDF folder behavior and ZIP-only PDF-member
        behavior unchanged
  - [x] keep direct-folder as the only shipping parity target unless the same
        implementation proves a broader claim honestly without a new truth-
        surface burden
- [x] Add focused fixture-backed coverage for the chosen seam, including route
      semantics and any new member-local recommendation / handoff artifact
      expectations
- [x] If this story changes documented format coverage or graduation reality:
      update `tests/fixtures/formats/_coverage-matrix.json` and any relevant
      methodology state honestly
- [x] Check whether the chosen implementation makes any existing code, helper
      paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through
        `driver.py`, verify artifacts in `output/runs/`, and manually inspect
        the member route rows plus the chosen folder PDF-member downstream
        artifacts
  - [x] Agent tooling did not change, so `make skills-check` was not needed
- [x] No recommendation-only intake or approved-handoff eval surface changed,
      so `docs/evals/registry.yaml` stayed untouched
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every folder PDF-member claim traces to the checked-
        in folder fixture, relative member path, member-local artifact, and
        inspected downstream artifact
  - [x] T1 — AI-First: no new folder-specific classifier is added if the
        existing maintained PDF intake surfaces already solve the member
        decision
  - [x] T2 — Eval Before Build: baseline member-routing candidates are measured
        before new glue lands
  - [x] T3 — Fidelity: the PDF member is not silently flattened, dropped, or
        mislabeled
  - [x] T4 — Modular: reuse the existing folder manifest + shared route + PDF
        recommendation / handoff seams instead of building a parallel stack
  - [x] T5 — Inspect Artifacts: route rows and the chosen folder PDF-member
        artifacts are manually opened and checked

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary
      shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Blocker Summary

N/A

## Blocker Evidence

N/A

## Unblock Condition

N/A

## Architectural Fit

- **Owning module / area**: intake and routing. The likely owner is still the
  existing `folder_members_manifest_v1 -> archive_route_members_v1` seam, not a
  second routing system or a new `doc-web` boundary.
- **Methodology reality**: this work belongs primarily to `spec:1`, with
  supporting ties to `spec:6`, `spec:7`, `spec:8`, and `spec:9`. In the current
  repo state, `spec:1` substrate exists and `C2` / `B10` remain `climb`;
  `spec:7` remains `partial`; and the relevant coverage row is `mixed-archive`,
  which now has bounded passing evidence on one ZIP direct-entry mix, one ZIP
  PDF-member recommendation mix, one source-native non-PDF folder mix, and one
  source-native born-digital folder PDF-member recommendation mix.
- **Substrate evidence**: verified in this pass that `schemas.py` and
  `driver.py` already expose `input_folder` / `--input-folder`;
  `modules/intake/folder_members_manifest_v1/main.py` emits source-native
  folder-backed `archive_member_manifest_v1` rows;
  `modules/intake/archive_route_members_v1/main.py` now routes bounded
  folder-contained `pdf` members through the same recommendation-only intake
  chain already proven for ZIP members; `tests/test_mixed_folder_recipe.py`
  proves the existing non-PDF folder lane and the new folder-PDF fixture
  metadata on checked-in fixtures; `tests/test_mixed_archive_zip_recipe.py`
  proves both ZIP-only PDF-member recommendation routing and direct-folder
  PDF-member recommendation parity; and the maintained PDF recommendation /
  handoff substrate already
  exists in `modules/intake/intake_plan_utils.py`,
  `modules/intake/confirm_plan_v1/main.py`, and
  `modules/intake/run_dispatch_v1/main.py`. Fresh current-pass baseline runs now
  also prove that both candidate PDFs can reach inspectable
  `overview_plan_final.jsonl` artifacts outside the mixed-folder route, so the
  shipping slice is now the bounded folder-backed fixture plus the landed route
  parity change that reuses the existing member-local recommendation path
  honestly on direct-folder entry.
- **Data contracts / schemas**: the existing `archive_member_manifest_v1` and
  `archive_member_route_v1` contracts are likely sufficient because Story 221
  already proved the route row can carry a member-local recommendation artifact
  path plus `recommended_recipe`. No schema change is expected unless folder-
  specific provenance needs to cross artifact boundaries in a new way.
- **File sizes**: likely touch points are
  `modules/intake/archive_route_members_v1/main.py` (273 lines),
  `modules/intake/folder_members_manifest_v1/main.py` (140),
  `modules/intake/intake_plan_utils.py` (419),
  `tests/test_mixed_folder_recipe.py` (145),
  `tests/test_mixed_archive_zip_recipe.py` (332),
  `testdata/README.md` (164),
  `docs/methodology/state.yaml` (132),
  `tests/fixtures/formats/_coverage-matrix.json` (576, >500),
  `README.md` (510, >500),
  `docs/RUNBOOK.md` (892, >500), and this story file (127). `schemas.py` and
  `driver.py` already own the direct-folder entry surface and are not expected
  touch points unless baseline evidence proves the current parity hook is
  missing.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`,
  `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002,
  Stories 169/180/196/205/218/221, `tests/fixtures/formats/_coverage-matrix.json`,
  `README.md`, `docs/RUNBOOK.md`, `schemas.py`, `driver.py`,
  `modules/intake/intake_plan_utils.py`,
  `modules/intake/archive_route_members_v1/main.py`,
  `modules/intake/folder_members_manifest_v1/main.py`,
  `tests/test_mixed_folder_recipe.py`, and
  `tests/test_mixed_archive_zip_recipe.py`. No narrower mixed-folder PDF-member
  ADR, runbook, scout, or note was found after search.

## Files to Modify

- `docs/stories/story-222-mixed-folder-pdf-member-routing-seam.md` — story
  record, work log, and proof expectations (127 lines)
- `modules/intake/archive_route_members_v1/main.py` — extend the bounded route
  seam if the measured baseline justifies folder-PDF parity without widening ZIP
  or non-PDF behavior (273 lines)
- `tests/test_mixed_folder_recipe.py` — add folder-PDF parity smoke / artifact
  expectations on the chosen checked-in fixture (145 lines)
- `tests/test_mixed_archive_zip_recipe.py` — preserve the current ZIP-only
  proof and update shared route-boundary assertions only if the implementation
  changes them (332 lines)
- `testdata/mixed-folder-pdf-mini/` and `testdata/mixed-folder-pdf-mini.source.json`
  — repo-owned bounded direct-folder PDF-member probe if the story ships the
  new parity fixture (new files)
- `testdata/README.md` — record fixture provenance, scope, and regeneration
  notes for the bounded folder-PDF slice (164 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — move the `mixed-archive` row
  only as far as fresh folder-PDF proof justifies (576 lines)
- `docs/methodology/state.yaml` — replace the current open-gap note with the
  narrower truth if the slice lands (132 lines)
- `README.md` — align user-facing support wording with the exact bounded
  mixed-folder PDF-member slice if it lands (510 lines)
- `docs/RUNBOOK.md` — document the verified mixed-folder PDF-member proof or
  blocker outcome if the seam lands (892 lines)
- `modules/intake/intake_plan_utils.py` — only if the baseline shows the
  existing recommendation / handoff helper boundary needs a narrow extension
  (419 lines)

## Redundancy / Removal Targets

- Any docs that still imply direct-folder PDF members are unproven after this
  bounded slice lands
- Any temptation to duplicate the shared route logic instead of extending the
  existing folder/ZIP seam surgically
- Any vague follow-up wording that turns one bounded direct-folder PDF-member
  probe into blanket archive/folder PDF ownership

## Notes

- New story justification: reopening Story 218 would not be honest because it
  closed the non-PDF direct-folder entry seam, and reopening Story 221 would
  blur a ZIP-contained PDF-member recommendation proof with a different entry
  contract and validation boundary. This story is the folder-parity continuation
  on the same subsystem, not the same completed slice.
- The tightest first candidate is a new `mixed-folder-pdf-mini/` fixture that
  mirrors Story 221's four-member ZIP probe with a source-native
  `flat-born-digital-mini.pdf` member so the only new variable is the direct-
  folder entry surface. Fresh current-pass candidate baselines now confirm that
  the born-digital member is the right shipping slice: it emits a maintained
  recommended recipe, while the scanned comparator emits `no-recipe-needed` and
  therefore does not prove a maintained folder-PDF recommendation continuation.
- Even if this slice lands, archive-contained approved handoff or final
  maintained PDF launch should remain a separate follow-up with an explicit
  workflow-change story.

## Plan

Implementation order:
1. Add the bounded folder-backed proof fixture:
   - create `testdata/mixed-folder-pdf-mini/` plus
     `testdata/mixed-folder-pdf-mini.source.json`
   - mirror Story 221's four-member probe using `flat-born-digital-mini.pdf`,
     `email-eml-mini.eml`, `web-page-mini.html`, and one unsupported `.txt`
     member so the only new variable is source-native folder entry
   - update `testdata/README.md` with generation notes and the bounded support
     claim
2. Extend the shared route seam without creating a folder-specific AI path:
   - update `modules/intake/archive_route_members_v1/main.py` so folder-backed
     PDF members reuse the same recommendation-only intake chain already proven
     for ZIP-backed PDF members
   - keep the route row contract unchanged unless fresh implementation evidence
     proves a missing provenance field; `schemas.py` is not expected to change
   - preserve the current `.eml`, HTML, and unsupported `.txt` behavior for
     mixed-folder routing and preserve ZIP behavior unchanged
3. Add focused fixture-backed coverage:
   - update `tests/test_mixed_archive_zip_recipe.py` so the current
     folder-PDF boundary test becomes a folder-PDF recommendation parity test
     with member-local `overview_plan_final.jsonl` evidence
   - update `tests/test_mixed_folder_recipe.py` with a smoke path on the new
     checked-in folder fixture and explicit artifact assertions for the PDF
     member plus the unchanged non-PDF members
4. Prove the bounded slice end to end and align docs:
   - clear stale `*.pyc` before rerunning pipeline proof
   - run the narrowest fresh `driver.py` proof on the checked-in
     `mixed-folder-pdf-mini/` fixture and manually inspect the route row plus
     the emitted member-local `intake_plan_v1` artifact
   - update `tests/fixtures/formats/_coverage-matrix.json`,
     `docs/methodology/state.yaml`, `README.md`, and `docs/RUNBOOK.md` so they
     claim only the bounded direct-folder PDF-member recommendation slice
   - regenerate `docs/methodology/graph.json` and `docs/stories.md`

Impact and risk notes:
- Expected coverage movement: the `mixed-archive` row should advance from “no
  direct-folder PDF-member parity” to “one checked-in direct-folder
  recommendation-only PDF-member slice” and nothing broader.
- Main break risk: accidentally widening all folder/ZIP PDF routing semantics
  beyond recommendation-only parity or regressing the existing `.eml` / HTML /
  `.txt` member behavior.
- Redundancy plan: reuse the existing shared route logic and member-local
  recommendation artifact path rather than adding a second folder-specific
  intake prompt or a parallel archive/folder router.
- Done for this story's implementation phase means: the new fixture is checked
  in, folder-PDF route rows launch to a member-local `overview_plan_final.jsonl`
  on the bounded fixture, non-PDF members remain unchanged, focused tests pass,
  and the truth surfaces/documentation all match the bounded claim.

## Work Log

20260416-1138 — story creation from `/triage` follow-through: created Story 222
after the user approved the next honest move. Evidence reviewed in this pass:
`docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`,
`docs/methodology/graph.json`, ADR-002, Stories 169/180/196/205/218/221,
`tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`,
`schemas.py`, `driver.py`, `modules/intake/intake_plan_utils.py`,
`modules/intake/archive_route_members_v1/main.py`,
`modules/intake/folder_members_manifest_v1/main.py`,
`tests/test_mixed_folder_recipe.py`, and
`tests/test_mixed_archive_zip_recipe.py`. Result: a new story is honest rather
than reopening Story 218 or Story 221 because the remaining work has a
different checked-in fixture shape, a different entry contract, and a different
validation boundary: source-native folder PDF-member parity. Status is
`Pending`, not `Draft`, because the routing substrate already exists in repo and
the missing slice is one bounded proof fixture plus the smallest parity glue the
baseline justifies. Next step: `/build-story` should freeze the current blocked
folder-PDF baseline, compare born-digital versus scanned-PDF candidates, and
choose the smallest honest shipping slice before any runtime code changes.
20260416-1146 — /build-story exploration + blocker discovery: verified the
critical substrate exists in code, but the current environment cannot produce a
fresh recommendation baseline. Evidence reviewed in this pass: `docs/ideal.md`,
`docs/spec.md` (`spec:1`, `spec:1.1`, `spec:6`, `spec:7`, `spec:8`, `spec:9`),
`docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, Stories
169/180/196/205/218/221, the `mixed-archive` coverage row, `schemas.py`,
`driver.py`, `modules/intake/intake_plan_utils.py`,
`modules/intake/archive_route_members_v1/main.py`,
`modules/intake/folder_members_manifest_v1/main.py`,
`tests/test_mixed_folder_recipe.py`, and
`tests/test_mixed_archive_zip_recipe.py`. Fresh current-pass route proof:
`python driver.py --recipe configs/recipes/recipe-mixed-folder-routing-mvp.yaml
--input-folder <tmp-folder> --run-id story222-folder-pdf-blocked-r1 --force`
completed and wrote
`output/runs/story222-folder-pdf-blocked-r1/02_archive_route_members_v1/archive_member_routes.jsonl`,
where `docs/proposal.pdf` remains blocked with
`pdf_member_outside_bounded_mixed_archive_slice`, `mail/message.eml` launches to
`...member-002-recipe-email-eml-html-mvp/01_unstructured_email_intake_v1/elements.jsonl`,
`web/snapshot.html` launches to
`...member-004-recipe-web-page-html-mvp/01_web_page_html_intake_v1/pages_html.jsonl`,
and `.txt` stays explicitly blocked. Fresh current-pass candidate baselines on
`testdata/flat-born-digital-mini.pdf` and `testdata/scanned-prose-mini.pdf`
both failed before plan emission:
`story222-flat-intake-r1` and `story222-scanned-intake-r1` stamped
`01_contact_sheet_builder_v1/build_contact_sheets.jsonl`, then failed at
`contact_sheet_overview_v1` with OpenAI `429 insufficient_quota`, as confirmed
by both stack traces and `pipeline_events.jsonl`. Result: the story is now
honestly `Blocked` because the repo cannot currently emit the fresh
recommendation artifacts needed to choose or verify the bounded shipping slice.
Next step: restore quota/provider access, rerun the three baselines, and reopen
only once at least one candidate emits an inspectable `overview_plan_final.jsonl`.
20260416-1208 — /build-story blocker reassessment: reran the three unblock
baselines after provider credit was restored and confirmed the story is
honestly buildable again. Fresh route proof:
`python driver.py --recipe configs/recipes/recipe-mixed-folder-routing-mvp.yaml
--input-folder <tmp-folder> --run-id story222-folder-pdf-r2 --force` still
wrote
`output/runs/story222-folder-pdf-r2/02_archive_route_members_v1/archive_member_routes.jsonl`,
where `docs/proposal.pdf` remains explicitly blocked while `.eml` and HTML
members still launch and `.txt` still blocks. Fresh recommendation baselines:
`story222-flat-intake-r2` now wrote
`output/runs/story222-flat-intake-r2/05_confirm_plan_v1/overview_plan_final.jsonl`
with `recommended_recipe =
configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`, and
`story222-scanned-intake-r2` wrote
`output/runs/story222-scanned-intake-r2/05_confirm_plan_v1/overview_plan_final.jsonl`
with `recommended_recipe = no-recipe-needed`. Result: the previous quota
blocker is cleared, the smallest honest shipping slice is the born-digital PDF
candidate, and Story 222 is restored to `Pending` with a concrete implementation
plan centered on a new checked-in `mixed-folder-pdf-mini/` fixture plus shared
route parity. Next step: after user approval, implement the bounded folder-PDF
recommendation slice and rerun focused proof/tests.
20260416-1208 — implemented the bounded direct-folder PDF-member recommendation
slice and revalidated it end to end. Runtime/files changed in this pass:
`modules/intake/archive_route_members_v1/main.py` now reuses the same
recommendation-only PDF intake chain for source-native folder members that
Story 221 already proved for ZIP members; `tests/test_mixed_archive_zip_recipe.py`
now covers folder-PDF recommendation parity on the checked-in folder probe;
`tests/test_mixed_folder_recipe.py` now covers the new fixture metadata/shape;
`testdata/mixed-folder-pdf-mini.source.json` plus the checked-in
`testdata/mixed-folder-pdf-mini/` fixture add the bounded four-member source-
native probe; and `testdata/README.md`, `README.md`, `docs/RUNBOOK.md`,
`tests/fixtures/formats/_coverage-matrix.json`, and
`docs/methodology/state.yaml` now all describe the same bounded claim. Critical
implementation note: no `schemas.py` or `modules/intake/intake_plan_utils.py`
changes were needed because the existing `archive_member_route_v1` contract was
already sufficient once the route row treated the nested recommendation run as
the downstream run and its `05_confirm_plan_v1/overview_plan_final.jsonl`
artifact as `first_downstream_artifact`. Focused checks in this pass:
`python -m pytest tests/test_mixed_archive_zip_recipe.py tests/test_mixed_folder_recipe.py -q`
→ `8 passed`; `python -m ruff check modules/intake/archive_route_members_v1/main.py tests/test_mixed_archive_zip_recipe.py tests/test_mixed_folder_recipe.py`
→ clean; repo-wide `make lint` → clean; repo-wide `make test` → `589 passed, 4 warnings`.
Fresh post-`pyc` proof via `find modules -name '*.pyc' -delete` then
`python driver.py --recipe configs/recipes/recipe-mixed-folder-routing-mvp.yaml --input-folder testdata/mixed-folder-pdf-mini --run-id story222-mixed-folder-pdf-mini-r1 --allow-run-id-reuse --force`
completed with `Archive routing complete: launched=3, blocked=1, skipped=0, failed=0`;
`validate_artifact.py` passed on the stamped manifest, route, and emitted plan
artifact. Manual artifact inspection in the fresh `r1` run:
`output/runs/story222-mixed-folder-pdf-mini-r1/02_archive_route_members_v1/archive_member_routes.jsonl`
shows `member_path = docs/proposal.pdf`, `archive_format = folder`,
`terminal_reason = pdf_member_recommendation_only`,
`recommended_recipe = configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`,
and `first_downstream_artifact = .../05_confirm_plan_v1/overview_plan_final.jsonl`;
`output/runs/story222-mixed-folder-pdf-mini-r1-member-001-recipe-intake-contact-sheet/05_confirm_plan_v1/overview_plan_final.jsonl`
shows `book_type = other`, `signals = [forms]`,
`warnings = [Missing capabilities: forms]`, and
`meta.source_input.source_pdf` pointing back to the checked-in
`testdata/mixed-folder-pdf-mini/docs/proposal.pdf`; the nested email bundle at
`output/runs/story222-mixed-folder-pdf-mini-r1-member-002-recipe-email-eml-html-mvp/output/html/manifest.json`
still titles `Fixture Subject`; and the nested web bundle at
`output/runs/story222-mixed-folder-pdf-mini-r1-member-004-recipe-web-page-html-mvp/output/html/manifest.json`
still exposes `Example Domain`. Residual boundary held intentionally: the new
proof is still recommendation-only, scanned or handwritten direct-folder PDF
members remain unproven, and no top-level recommendation-only or approved-
handoff eval surface changed. Next step: hand off to `/validate 222`.
20260416-1326 — validation cleanup after `/validate`: updated stale story
narrative in `## Goal`, `## Approach Evaluation`, and `## Architectural Fit`
so the story now describes the post-fix bounded direct-folder PDF-member
recommendation slice rather than the pre-fix blocked state. No runtime or test
files changed in this cleanup step. `make methodology-compile` regenerated
`docs/methodology/graph.json` and `docs/stories.md`, and a same-pass recheck
confirmed Story 222 is now internally consistent. Validation is complete; the
remaining close-out step is `/mark-story-done`.
20260416-1402 — `/mark-story-done` close-out validation confirmed Story 222 is
complete on the current branch and safe to close. Fresh current-pass
validation in this close-out step: `python -m ruff check modules/ tests/` →
clean; `python -m pytest tests/` → `589 passed, 4 warnings`; `find modules
-name '*.pyc' -delete` then `python driver.py --recipe
configs/recipes/recipe-mixed-folder-routing-mvp.yaml --input-folder
testdata/mixed-folder-pdf-mini --run-id
story222-mixed-folder-pdf-mini-close-r1 --allow-run-id-reuse --force`
completed with `Archive routing complete: launched=3, blocked=1, skipped=0,
failed=0`; `python validate_artifact.py --schema archive_member_manifest_v1
--file
output/runs/story222-mixed-folder-pdf-mini-close-r1/01_folder_members_manifest_v1/archive_members_manifest.jsonl`,
`python validate_artifact.py --schema archive_member_route_v1 --file
output/runs/story222-mixed-folder-pdf-mini-close-r1/02_archive_route_members_v1/archive_member_routes.jsonl`,
and `python validate_artifact.py --schema intake_plan_v1 --file
output/runs/story222-mixed-folder-pdf-mini-close-r1-member-001-recipe-intake-contact-sheet/05_confirm_plan_v1/overview_plan_final.jsonl`
all passed. Manual inspection in the fresh close-out run reconfirmed the
folder PDF route row at
`output/runs/story222-mixed-folder-pdf-mini-close-r1/02_archive_route_members_v1/archive_member_routes.jsonl`
with `recommended_recipe =
configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml`,
`first_downstream_artifact = .../05_confirm_plan_v1/overview_plan_final.jsonl`,
and `terminal_reason = pdf_member_recommendation_only`; the emitted plan at
`output/runs/story222-mixed-folder-pdf-mini-close-r1-member-001-recipe-intake-contact-sheet/05_confirm_plan_v1/overview_plan_final.jsonl`
still reports `book_type = other`, `signals = [forms]`, `warnings = [Missing
capabilities: forms]`, and `meta.source_input.source_pdf` pointing back to the
checked-in folder member; the nested email bundle at
`output/runs/story222-mixed-folder-pdf-mini-close-r1-member-002-recipe-email-eml-html-mvp/output/html/manifest.json`
still titles `Fixture Subject`; and the nested web bundle at
`output/runs/story222-mixed-folder-pdf-mini-close-r1-member-004-recipe-web-page-html-mvp/output/html/manifest.json`
still carries the `Example Domain` chapter. Story status moved to `Done`, all
workflow gates are now checked, and the remaining landing step is
`/check-in-diff`.
