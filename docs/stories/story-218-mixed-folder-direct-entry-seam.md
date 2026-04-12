---
title: "Establish the First Honest Mixed-Folder Direct-Entry Seam"
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
  - "205"
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

# Story 218 — Establish the First Honest Mixed-Folder Direct-Entry Seam

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/stories/story-194-office-intake-recommendation-and-handoff-boundary.md`, `docs/stories/story-200-web-page-direct-entry-seam.md`, `docs/stories/story-202-eml-direct-entry-seam.md`, `docs/stories/story-203-mbox-archive-seam.md`, `docs/stories/story-205-mixed-archive-intake-routing-seam.md`, `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, `schemas.py`, `driver.py`, `modules/intake/intake_plan_utils.py`, `modules/intake/archive_unpack_manifest_v1/main.py`, `modules/intake/archive_route_members_v1/main.py`, `tests/test_mixed_archive_zip_recipe.py`, `benchmarks/scripts/intake_scope.py`, and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower mixed-folder direct-entry ADR or runbook
**Depends On**: Story `205`

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

Story 205 closed the first honest `mixed-archive` slice on one checked-in ZIP
fixture, but the coverage row still explicitly excludes direct folder input.
The repo now owns `input_zip`, `archive_member_manifest_v1`, and
`archive_route_members_v1`, yet it still has no maintained heterogeneous
folder-entry surface, no repo-owned mixed-folder fixture, and no folder
inventory stage that can preserve relative member identity and route each file
into an existing direct-entry recipe or explicit blocked outcome. This story
should prove the smallest honest continuation of Story 205: one checked-in
mixed folder tree with nested member paths, deterministic inventory into the
existing archive-member routing seam, bounded dispatch into already-maintained
direct-entry recipes, and explicit blocked rows for unsupported files. Either
that slice lands with fresh `driver.py` proof and aligned docs/eval truth, or
the story closes `Blocked` instead of leaving direct folder input as an
implicit future promise.

## Acceptance Criteria

- [x] A fresh current-pass baseline names the exact mixed-folder gap from repo evidence:
  - [x] the work log records that `tests/fixtures/formats/_coverage-matrix.json` now marks `mixed-archive` `passing` only on one ZIP-only slice and still lists direct folder input as an explicit known gap
  - [x] the work log records that `schemas.py` and `driver.py` expose `input_zip` / `--input-zip` but no heterogeneous `input_folder` / `--input-folder` entry surface, and that `input_dir` currently appears only as image-directory stage plumbing rather than a maintained mixed-folder entry contract
  - [x] the work log cites the verified absence of a repo-owned mixed-folder fixture and a maintained folder-inventory module before implementation
  - [x] the work log records the current reusable substrate honestly: `archive_member_manifest_v1`, `archive_route_members_v1`, Story 205's ZIP fixture/tests, and the existing direct-entry recipe map already exist in repo
- [x] The story either lands one bounded mixed-folder slice or closes `Blocked` honestly:
  - [x] one repo-owned mixed-folder fixture exists under `testdata/` with nested member paths and capture/generation notes in `testdata/README.md`
  - [x] the chosen shipping slice emits an inspectable member manifest with relative member path, detected input kind, and explicit terminal status per member using source-native file paths rather than extracted archive copies
  - [x] at least one member launches into an existing maintained direct-entry recipe through `driver.py`, and at least one member-level blocked or skipped outcome is inspectable when the fixture warrants it
  - [x] if the existing `archive_route_members_v1` seam proves insufficient, the story records the smallest honest sibling helper or a named blocker instead of widening the scope casually
- [x] Mixed-folder provenance stays source-honest on the claimed slice:
  - [x] relative member paths remain inspectable end to end
  - [x] no fabricated archive wrapper, synthetic combined bundle, or archive-level page anchors are introduced
  - [x] any new fields that cross artifact boundaries are added to `schemas.py` before stamped artifacts rely on them
- [x] Coverage, docs, and intake-boundary surfaces remain aligned with the outcome:
  - [x] `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, and `testdata/README.md` reflect the exact supported mixed-folder slice rather than a vague folder promise
  - [x] if direct folder input changes approved-handoff or recommendation-only intake truth, rerun the relevant maintained surfaces and update `docs/evals/registry.yaml`; otherwise direct-entry-only scope helpers/tests are updated honestly without overstating automation support
  - [x] ZIP-only mixed-archive proof remains intact, while broader PDF-member routing, grouped image-member interpretation, nested archives, attachment extraction, and broad heterogeneous folder ownership stay explicitly out of scope unless fresh evidence justifies separate follow-up work

## Out of Scope

- Nested archives, archive files inside the checked-in folder tree, or any archive-of-archives handling
- PDF-member routing, grouped image-member interpretation, or ambiguous AI-assisted route decisions
- Attachment extraction, mailbox/thread cleanup, `.msg` parity, or connector workflows
- Live arbitrary folder scanning, symlink policy expansion, or hidden-file policy beyond one checked-in bounded fixture
- Recommendation-only intake or approved-handoff expansion beyond explicit direct-entry truth unless fresh evidence proves those surfaces should change
- Reopening Story 191 or changing handwritten OCR/runtime behavior
- New `doc-web` output-contract architecture beyond the minimum inspectable member-manifest and route rows needed to prove the folder slice

## Approach Evaluation

- **Simplification baseline**: measured in this pass on a temporary mixed folder assembled from repo-owned fixtures (`testdata/docx-mini.docx`, `testdata/email-eml-mini.eml`, `testdata/web-page-mini.html`, and `README.md`). A hand-written `archive_member_manifest_v1` with `archive_format: folder` routed through the existing `archive_route_members_v1` seam and produced `3/4` launched members (`docx`, `email-eml`, `web-page`) plus `1/4` explicit blocked (`.txt`), with downstream artifacts present for every launched member. That proves the real missing slice is folder inventory plus maintained entry wiring, not a new routing system.
- **AI-only**: wrong first move on the bounded candidate slice. Letting a model reason over filenames or folder contents would hide deterministic routing evidence and re-solve suffix-to-recipe decisions the repo already owns.
- **Hybrid**: keep only as a fallback. If the chosen fixture later needs ambiguous PDF handling or grouped image-member interpretation, introduce AI only for that narrow member-decision surface.
- **Pure code**: confirmed front-runner. The measured gap is folder inventory plus maintained launch/block wiring, not language understanding.
- **Repo constraints / prior decisions**: `spec:1.1` keeps the recipe surface explicit under `C2`; ADR-002 keeps the accepted `doc-web` boundary inspectable; Story 205 deliberately kept direct folder input out of scope while proving the ZIP-only slice; Story 194 kept recommendation-only intake and approved handoff narrower than explicit direct-entry seams; and the current coverage row already says direct folder input is not yet owned.
- **Existing patterns to reuse**: `modules/intake/archive_unpack_manifest_v1/main.py`, `modules/intake/archive_route_members_v1/main.py`, `modules/intake/intake_plan_utils.py`, `tests/test_mixed_archive_zip_recipe.py`, Story 205's checked-in member mix, `build_explicit_recipe_driver_command(...)`, `default_downstream_run_id(...)`, and the direct-entry fixture patterns from Stories 200/202/203.
- **Eval**: the deciding proof surface is a fresh `driver.py` run on one checked-in mixed-folder fixture plus manual inspection of the emitted member manifest, route rows, and representative downstream artifacts. If the lane changes approved-handoff or recommendation-only truth, rerun the relevant maintained intake surfaces and update `docs/evals/registry.yaml`.

## Tasks

- [x] Freeze the current mixed-folder gap from repo reality:
  - [x] verify the `mixed-archive` row still excludes direct folder input
  - [x] verify `schemas.py` / `driver.py` still have no heterogeneous `input_folder` / `--input-folder` surface
  - [x] verify there is still no repo-owned mixed-folder fixture or maintained folder-inventory module
  - [x] record the current reusable substrate honestly: `input_zip`, `archive_member_manifest_v1`, `archive_route_members_v1`, Story 205's ZIP fixture/tests, and the existing direct-entry recipe map
- [x] Add one repo-owned bounded mixed-folder fixture under `testdata/` plus source metadata:
  - [x] check in one heterogeneous folder tree with nested member paths from already-maintained direct-entry families plus at least one intentionally unsupported member
  - [x] record capture/generation notes in `testdata/README.md`
  - [x] keep future tests and reruns independent of live network access
- [x] Measure the smallest honest baseline before adding routing logic:
  - [x] run deterministic recursive folder inventory on the chosen fixture and preserve relative member paths
  - [x] test whether the existing `archive_route_members_v1` seam can consume folder-inventoried rows unchanged or whether a thin sibling helper is required
  - [x] no LLM probe is needed unless the checked-in fixture introduces ambiguous member kinds
- [x] Decide the smallest honest shipping slice:
  - [x] folder-only member manifest plus route rows and bounded dispatch into existing maintained direct-entry recipes
  - [x] keep the existing ZIP path working unchanged
  - [x] keep ambiguous PDF/image grouping, nested archives, and broad heterogeneous ownership explicitly out of scope unless the bounded fixture proves otherwise
- [x] If the bounded seam is viable, land the smallest coherent implementation:
  - [x] add `input_folder` / `--input-folder` or a clearly superior bounded successor in `RunConfig` and `driver.py`
  - [x] add the minimum folder-inventory stage and recipe wiring needed to feed the existing route/dispatch seam
  - [x] preserve relative member provenance and explicit terminal status per member instead of flattening the folder into one synthetic document
- [x] Add focused fixture-backed coverage for the chosen seam:
  - [x] add a direct-entry smoke test that runs `driver.py` on the checked-in folder fixture and asserts manifest/route/downstream outputs
  - [x] extend direct-entry-only scope tests and focused intake benchmark tests only if the maintained workflow truth changes
- [x] If this story changes documented format coverage or graduation reality: update `tests/fixtures/formats/_coverage-matrix.json` and any relevant methodology state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [x] If agent tooling changed: `make skills-check`
- [x] If direct folder input changes approved-handoff or recommendation-only intake truth: rerun the relevant maintained intake surfaces and update `docs/evals/registry.yaml`
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every support claim traces to the checked-in folder fixture, relative member paths, run IDs, and inspected artifacts
  - [x] T1 — AI-First: no AI routing logic is added for a problem deterministic inventory already solves on the bounded slice
  - [x] T2 — Eval Before Build: the deterministic folder-inventory baseline is measured before new routing glue lands
  - [x] T3 — Fidelity: no member is silently dropped, merged, or mislabeled
  - [x] T4 — Modular: reuse the existing archive-member route and direct-entry recipe seams instead of inventing a second routing stack
  - [x] T5 — Inspect Artifacts: member manifest, route rows, and representative downstream artifacts are manually opened and checked

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

- **Owning module / area**: intake and routing. The likely shape is one bounded folder-inventory stage that feeds the existing `archive_route_members_v1` seam, not a second routing system or a new `doc-web` boundary.
- **Methodology reality**: this work belongs primarily to `spec:1`, with supporting ties to `spec:6`, `spec:7`, `spec:8`, and `spec:9`. In the current repo state, `spec:1` substrate exists and `C2` / `B10` remain `climb`; `spec:7` remains `partial`; and the relevant coverage row is `mixed-archive`, which now has bounded passing evidence on one ZIP slice plus one direct-folder slice over the same four-member mix.
- **Substrate evidence**: verified in this pass that `schemas.py` and `driver.py` now expose both `input_zip` / `--input-zip` and `input_folder` / `--input-folder`; `modules/intake/archive_unpack_manifest_v1/main.py` emits ZIP-backed manifest rows; `modules/intake/folder_members_manifest_v1/main.py` emits source-native folder-backed manifest rows; `modules/intake/archive_route_members_v1/main.py` launches existing direct-entry recipes from either manifest shape; and `tests/test_mixed_archive_zip_recipe.py` plus `tests/test_mixed_folder_recipe.py` now prove the bounded ZIP and direct-folder paths on checked-in fixtures. `driver.py` still mentions `input_dir`, but only as an internal stage-param rewrite for image-directory overrides rather than the mixed-folder entry contract.
- **Data contracts / schemas**: likely touched contracts are `RunConfig` in `schemas.py` and the new folder-entry recipe surface. Fresh exploration proved `archive_member_manifest_v1` and `archive_member_route_v1` already accept folder-backed rows because `member_path` is only validated as a normalized relative path and `archive_format` is already a free string. The preferred outcome is therefore no artifact-schema expansion beyond `RunConfig`; if folder-root metadata later needs to cross an artifact boundary, add it explicitly before stamped artifacts rely on it.
- **File sizes**: likely touch points are `schemas.py` (1372 lines, >500), `driver.py` (3159, >500), `README.md` (473), `docs/RUNBOOK.md` (782, >500), `docs/methodology/state.yaml` (size moderate but truth-critical), `tests/fixtures/formats/_coverage-matrix.json` (564, >500), `testdata/README.md` (139), `tests/test_run_config.py` (58), and `tests/test_mixed_archive_zip_recipe.py` (125) only if ZIP regression coverage needs a parity assertion. New focused files should stay small: `configs/recipes/recipe-mixed-folder-routing-mvp.yaml`, `modules/intake/folder_members_manifest_v1/{main.py,module.yaml}`, `tests/test_mixed_folder_recipe.py`, and `testdata/mixed-folder-mini.source.json`. Keep edits especially surgical in the oversized files.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, Stories 194/200/202/203/205, `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, `schemas.py`, `driver.py`, `modules/intake/intake_plan_utils.py`, `modules/intake/archive_unpack_manifest_v1/main.py`, `modules/intake/archive_route_members_v1/main.py`, `tests/test_mixed_archive_zip_recipe.py`, and `benchmarks/scripts/intake_scope.py`. No narrower mixed-folder ADR, runbook, scout, or note was found after search.

## Files to Modify

- `schemas.py` — add `input_folder` or the smallest honest heterogeneous folder-entry config if the maintained seam lands (1372 lines)
- `driver.py` — add `--input-folder` or equivalent bounded override plumbing for the folder-entry seam (3159 lines)
- `configs/recipes/recipe-mixed-folder-routing-mvp.yaml` — maintained bounded mixed-folder direct-entry recipe reusing the existing route/dispatch seam (new file)
- `modules/intake/folder_members_manifest_v1/main.py` and `module.yaml` — deterministic folder inventory stage that emits `archive_member_manifest_v1`-compatible rows or a clearly superior bounded successor (new files)
- `modules/intake/archive_route_members_v1/main.py` and `module.yaml` — keep the shared route seam honest for mixed-folder driver compatibility and non-ZIP wording (237 lines)
- `modules/common/run_registry.py` — let shared run metadata infer a useful label for folder-backed runs (240 lines)
- `tests/test_run_config.py` — add folder-entry config coverage if the run-config surface grows (58 lines)
- `tests/test_mixed_folder_recipe.py` — fixture-backed direct-entry smoke coverage for the bounded folder seam (new file)
- `tests/test_mixed_archive_zip_recipe.py` — extend only if the shared route seam needs a wording or parity assertion after the folder slice lands (125 lines)
- `testdata/mixed-folder-mini/` and `testdata/mixed-folder-mini.source.json` — repo-owned bounded heterogeneous folder fixture and source metadata (new files)
- `testdata/README.md` — record fixture source and generation/capture notes for the mixed-folder slice (139 lines)
- `docs/methodology/state.yaml` — replace the current “direct folder input remains out of scope” note with the narrower truth if the folder seam lands
- `tests/fixtures/formats/_coverage-matrix.json` — move the `mixed-archive` row only as far as fresh folder-slice evidence justifies (564 lines)
- `README.md` — align user-facing support wording with the exact bounded mixed-folder slice if it lands (473 lines)
- `docs/RUNBOOK.md` — document the verified mixed-folder direct-entry command or blocker outcome if the seam lands (782 lines)

## Redundancy / Removal Targets

- Any scratch folder-walk probes or ad hoc manifest notes once a maintained folder fixture and recipe exist
- Any docs that still imply mixed-archive is ZIP-only after a folder slice lands
- Any temptation to duplicate `archive_route_members_v1` instead of extending or reusing the existing route seam surgically
- Any workflow wording that accidentally treats direct folder input as broad heterogeneous ownership beyond the checked-in bounded fixture

## Notes

- New story justification: expanding Story 205 would not be honest. Story 205 closed a ZIP-only entry surface with extracted member paths and one bounded archive-manifest/runtime seam. This story adds a different entry contract, a different repo-owned fixture shape, and a different validation boundary: source-native folder inventory with no archive wrapper.
- The tightest first candidate is to mirror Story 205's four-member mix as a checked-in folder tree so the only new variable is the entry surface, not the downstream routing mix.
- Even if the seam lands, this story should not widen `mixed-archive` into broad heterogeneous folder ownership by inertia. PDF/image grouping, nested archives, and attachment semantics remain separate future lines.

## Plan

Alignment check:
- This story still moves toward the Ideal rather than away from it. It closes a real remaining `spec:1.1` / `C2` input-seam gap, keeps the accepted `doc-web` boundary unchanged under ADR-002, and reuses existing routing substrate instead of adding a parallel system.
- No narrower mixed-folder ADR or runbook was found in this pass.

Frozen current-pass baseline:
- `tests/fixtures/formats/_coverage-matrix.json` marks `mixed-archive` `passing` only on one checked-in ZIP slice and still names direct folder input as an explicit known gap.
- `schemas.py` / `driver.py` already support `input_zip` / `--input-zip`, but they expose no heterogeneous `input_folder` / `--input-folder` surface. `driver.py` does mention `input_dir`, but only as image-directory override plumbing.
- `archive_member_manifest_v1`, `archive_unpack_manifest_v1`, `archive_route_members_v1`, and `tests/test_mixed_archive_zip_recipe.py` prove the current ZIP manifest + route/dispatch substrate exists in code.
- Fresh eval-first probe from this pass: a temporary folder-backed `archive_member_manifest_v1` built from repo fixtures (`docx-mini.docx`, `email-eml-mini.eml`, `web-page-mini.html`, `README.md`) ran through `archive_route_members_v1` with `PYTHONPATH` set and produced `3/4` launched rows plus `1/4` explicit blocked `.txt`, with downstream artifacts present for every launched member. This is sufficient evidence that the router already accepts folder-backed rows unchanged.
- No checked-in mixed-folder fixture or maintained folder-inventory stage exists yet.

Small scope adjustment folded into the story:
- `modules/intake/archive_route_members_v1/main.py`, `modules/intake/archive_route_members_v1/module.yaml`, `modules/intake/intake_plan_utils.py`, `benchmarks/scripts/intake_scope.py`, the direct-entry benchmark boundary tests, and `docs/evals/registry.yaml` are no longer planned changes by default. Touch them only if implementation reveals a real compatibility or workflow-boundary issue.

Implementation order:
1. Fixture + metadata
   - Files: `testdata/mixed-folder-mini/**`, `testdata/mixed-folder-mini.source.json`, `testdata/README.md`
   - Change: check in one heterogeneous folder tree that mirrors Story 205's four-member mix with nested paths and one intentionally unsupported member.
   - Done looks like: the fixture is repo-owned, deterministic, and documents exactly how it was assembled.
2. Folder inventory stage
   - Files: `modules/intake/folder_members_manifest_v1/main.py`, `modules/intake/folder_members_manifest_v1/module.yaml`
   - Change: implement a bounded recursive folder walk that emits `archive_member_manifest_v1` rows using source-native file paths, normalized relative `member_path`s, deterministic ordering, `file_size_bytes`, `sha256`, and detected input kind.
   - Patterns to follow: `modules/intake/archive_unpack_manifest_v1/main.py` for manifest shape and `modules/extract/images_dir_to_manifest_v1/main.py` for source-path honesty and lightweight logging.
   - Done looks like: the first-stage artifact validates as `archive_member_manifest_v1` and references original fixture files rather than copied extracts.
3. Entry surface + recipe wiring
   - Files: `schemas.py`, `driver.py`, `configs/recipes/recipe-mixed-folder-routing-mvp.yaml`, `tests/test_run_config.py`
   - Change: add `input_folder` / `--input-folder` beside the existing explicit direct-entry overrides and wire the new recipe to `folder_members_manifest_v1 -> archive_route_members_v1`.
   - Risks: `schemas.py` and `driver.py` are large, so edits must stay adjacent to the existing input-override cluster and must not perturb ZIP behavior.
   - Done looks like: `driver.py --input-folder testdata/mixed-folder-mini` rewrites recipe input cleanly and `RunConfig` accepts the same surface.
4. Focused smoke coverage
   - Files: `tests/test_mixed_folder_recipe.py`; `tests/test_mixed_archive_zip_recipe.py` only if parity coverage is needed after touching shared route wording or behavior
   - Change: run `driver.py` on the checked-in folder fixture and assert manifest rows preserve nested relative paths, route rows show `3 launched / 1 blocked`, and launched member artifacts exist.
   - Done looks like: the new smoke test proves the bounded folder slice without weakening the ZIP smoke.
5. Truth-surface alignment
   - Files: `tests/fixtures/formats/_coverage-matrix.json`, `docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`
   - Generated outputs after compile: `docs/methodology/graph.json`, `docs/stories.md`
   - Change: widen the supported claim only to one bounded repo-owned mixed-folder seam and keep PDF-member routing, grouped image members, nested archives, attachments, and broad heterogeneous ownership explicitly out of scope.
   - Done looks like: the truth surfaces stop saying direct folder input is unproven, while the broader archive limitations remain explicit.

Verification plan:
- Before implementation changes: keep the measured `3 launched / 1 blocked` folder-route baseline as the proof that new router work is unnecessary.
- Focused tests after implementation: `pytest -q tests/test_run_config.py tests/test_mixed_archive_zip_recipe.py tests/test_mixed_folder_recipe.py`
- Fresh real-run proof: clear stale `*.pyc` under touched modules, run `python driver.py --recipe configs/recipes/recipe-mixed-folder-routing-mvp.yaml --input-folder testdata/mixed-folder-mini --run-id <run_id> --force`, validate `archive_member_manifest_v1` and `archive_member_route_v1`, then manually inspect the manifest rows, route rows, and representative downstream `output/html/manifest.json` artifacts.
- Mixed-folder rerun note: use a fresh parent `run_id` for clean repeated proof runs. Reusing the same parent `run_id` after nested member runs already exist currently collides with the child output directories, so `--allow-run-id-reuse` is not the right default for this lane.
- Not planning benchmark reruns or `docs/evals/registry.yaml` changes unless implementation unexpectedly widens recommendation-only intake or approved-handoff workflow truth.

Human-approval blockers / risks:
- New maintained input surface: `input_folder` / `--input-folder`.
- Generated methodology truth surfaces will change after `make methodology-compile`.
- Main structural risk is accidental scope creep into a generic “all archives” abstraction; current-pass evidence says that broader generalization is unnecessary for this story.

## Work Log

20260412-1209 — story creation from `/triage` follow-through: created Story 218 after the user approved the next honest move. Evidence reviewed in this pass: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, Stories 194/200/202/203/205, `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, `schemas.py`, `driver.py`, `modules/intake/intake_plan_utils.py`, `modules/intake/archive_unpack_manifest_v1/main.py`, `modules/intake/archive_route_members_v1/main.py`, `tests/test_mixed_archive_zip_recipe.py`, and `benchmarks/scripts/intake_scope.py`. Result: a new story is honest instead of reopening Story 205 because the ZIP-only archive seam is already closed and the remaining work has a different entry contract and validation boundary: source-native folder inventory. Status is `Pending`, not `Draft`, because the archive-member routing substrate already exists in repo and the missing slice is a bounded folder-entry seam that this story itself can build. Next step: `/build-story` should choose the checked-in folder fixture, freeze the deterministic folder-inventory baseline, and decide whether the existing member-manifest/route shapes can be reused unchanged.
20260412-1219 — `/build-story` exploration + eval-first baseline: re-read `docs/ideal.md`, `docs/spec.md` (`spec:1`, `spec:1.1`, `spec:6`, `spec:7`, `spec:8`, `spec:9`), `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, Stories 194/200/202/203/205, the `mixed-archive` coverage row, `README.md`, `docs/RUNBOOK.md`, `schemas.py`, `driver.py`, `modules/intake/intake_plan_utils.py`, `modules/intake/archive_unpack_manifest_v1/main.py`, `modules/intake/archive_route_members_v1/main.py`, `tests/test_mixed_archive_zip_recipe.py`, `tests/test_run_config.py`, `tests/test_image_directory_intake_recipe.py`, `modules/extract/images_dir_to_manifest_v1/main.py`, `benchmarks/scripts/intake_scope.py`, and the maintained intake benchmark harnesses before planning implementation. Fresh substrate reality in this pass: `RunConfig` / `driver.py` still expose `input_zip` / `--input-zip` but no heterogeneous `input_folder` / `--input-folder` surface; `archive_member_manifest_v1` and `archive_member_route_v1` already allow normalized relative `member_path` values and non-`zip` `archive_format` labels; and Story 205's ZIP-only route seam is real code, not just planning prose. Measured baseline: a temporary mixed folder assembled from `testdata/docx-mini.docx`, `testdata/email-eml-mini.eml`, `testdata/web-page-mini.html`, and `README.md` was expressed as a folder-backed `archive_member_manifest_v1` and run through `archive_route_members_v1` with `PYTHONPATH` set, producing `3/4` launched members (`docs/reference.docx`, `mail/message.eml`, `web/snapshot.html`) plus `1/4` explicit blocked (`notes/readme.txt` with `unsupported_archive_member_suffix:.txt`), and every launched row pointed to a real downstream artifact. Manual proof from the same pass: the nested DOCX run emitted `output/html/manifest.json` titled `DOCX Mini Fixture`, the EML run emitted `Fixture Subject`, and the HTML run launched successfully before truncation in the console output; the route summary captured all four terminal outcomes explicitly. Surprises found: direct module invocation of `archive_route_members_v1/main.py` needs `PYTHONPATH` set even though the nested `driver.py` launches work fine, and the image-directory manifest pattern lives in `modules/extract/` rather than `modules/intake/`, which reinforces that the new mixed-folder manifest should be its own explicit intake module instead of piggybacking on image-only plumbing. Decision from exploration: Story 218 remains honestly `Pending`; the missing slice is bounded folder inventory plus maintained entry wiring, so the implementation plan was tightened to new fixture + new manifest module + thin `RunConfig` / `driver.py` / recipe wiring, with route-module, benchmark-boundary, and eval-registry edits now out of scope unless fresh implementation evidence forces them. Next step: present the narrowed plan for approval before writing code or changing story status.
20260412-1251 — implementation + proof: landed the bounded direct-folder continuation as `schemas.py` / `driver.py` `input_folder` support, `configs/recipes/recipe-mixed-folder-routing-mvp.yaml`, `modules/intake/folder_members_manifest_v1`, the checked fixture tree `testdata/mixed-folder-mini/` plus `testdata/mixed-folder-mini.source.json`, focused smoke coverage in `tests/test_mixed_folder_recipe.py`, and aligned truth-surface updates in `tests/fixtures/formats/_coverage-matrix.json`, `docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`, and `testdata/README.md`. Fresh targeted verification passed in this pass: `pytest -q tests/test_run_config.py tests/test_mixed_archive_zip_recipe.py tests/test_mixed_folder_recipe.py` completed `7 passed, 2 skipped` under the outer shell interpreter after adding the same optional-dependency skip discipline the repo already uses for direct-entry smoke tests, and the repo-standard checks `make lint` and `make test` both passed on the project Python (`573 passed, 4 warnings`). Fresh real-run proof also passed: after clearing stale `*.pyc`, `python driver.py --recipe configs/recipes/recipe-mixed-folder-routing-mvp.yaml --input-folder testdata/mixed-folder-mini --run-id story218-mixed-folder-proof --allow-run-id-reuse --force` completed successfully, and `python validate_artifact.py --schema archive_member_manifest_v1 --file output/runs/story218-mixed-folder-proof/01_folder_members_manifest_v1/archive_members_manifest.jsonl` plus `python validate_artifact.py --schema archive_member_route_v1 --file output/runs/story218-mixed-folder-proof/02_archive_route_members_v1/archive_member_routes.jsonl` both returned `Validation OK`. Manual artifact inspection in the same pass: `output/runs/story218-mixed-folder-proof/01_folder_members_manifest_v1/archive_members_manifest.jsonl` preserved source-native file paths for `docs/reference.docx`, `mail/message.eml`, `notes/readme.txt`, and `web/snapshot.html` with `archive_format = folder`; `output/runs/story218-mixed-folder-proof/02_archive_route_members_v1/archive_member_routes.jsonl` recorded `3 launched / 1 blocked`, with `notes/readme.txt` blocked as `unsupported_archive_member_suffix:.txt`; `output/runs/story218-mixed-folder-proof-member-001-recipe-docx-html-mvp/output/html/manifest.json` stayed titled `DOCX Mini Fixture`; `output/runs/story218-mixed-folder-proof-member-002-recipe-email-eml-html-mvp/output/html/manifest.json` stayed titled `Fixture Subject`; and `output/runs/story218-mixed-folder-proof-member-004-recipe-web-page-html-mvp/output/html/manifest.json` kept the expected web entry title `Example Domain`. Minor adjacent fixes folded into the same pass: `archive_route_members_v1` now accepts the forwarded `--folder` flag for driver compatibility and no longer describes itself as ZIP-only, `modules/common/run_registry.py` can infer folder-backed run labels, and the mixed-archive ZIP smoke now uses the repo's established optional-dependency skip pattern instead of failing spuriously under interpreters without the DOCX/email extras. Result: Story 218 now has fresh current-pass proof for one bounded source-native folder seam while the ZIP proof remains intact and broader archive semantics stay explicitly separate future work. Next step: `/validate 218`.
20260412-1417 — validation hardening for an `A` close-out: re-opened Story 218 after `/validate` identified two non-runtime gaps that kept the grade at `B`. Fresh evidence in this pass: `docs/methodology/state.yaml` still claimed the intake/routing audit note had absorbed Story 218 while leaving `stories_since_audit` at `1` and `recent_story_refs` without `218`, and a same-`run_id` mixed-folder rerun using `python driver.py --recipe configs/recipes/recipe-mixed-folder-routing-mvp.yaml --input-folder testdata/mixed-folder-mini --run-id story218-mixed-folder-validate-rerun-20260412 --allow-run-id-reuse --force` failed before execution because the nested member-run directories already existed. Follow-up landed here: methodology state now counts Story 218 in the intake/routing audit memory and the active maintained-intake campaign, while `README.md`, `docs/RUNBOOK.md`, and the story verification notes now direct operators to use a fresh parent `run_id` for clean repeated proof runs instead of implying same-`run_id` reruns are safe on this lane. This does not widen runtime scope; it removes bookkeeping drift and aligns the user-facing proof instructions with the actual nested-run behavior.
20260412-1458 — `/mark-story-done` close-out: confirmed Story 218 is complete on fresh current-pass evidence and applied the close-out bookkeeping. Fresh validation from this pass: `make lint` passed; `make test` passed (`573 passed, 4 warnings in 679.18s`); `python driver.py --recipe configs/recipes/recipe-mixed-folder-routing-mvp.yaml --input-folder testdata/mixed-folder-mini --run-id story218-mixed-folder-validate-A-20260412 --force` completed with `3 launched / 1 blocked`; `python validate_artifact.py --schema archive_member_manifest_v1 --file output/runs/story218-mixed-folder-validate-A-20260412/01_folder_members_manifest_v1/archive_members_manifest.jsonl` and `python validate_artifact.py --schema archive_member_route_v1 --file output/runs/story218-mixed-folder-validate-A-20260412/02_archive_route_members_v1/archive_member_routes.jsonl` both returned `Validation OK`; and manual inspection of those two stamped artifacts plus the representative downstream bundle manifests under `story218-mixed-folder-validate-a-20260412-member-001-recipe-docx-html-mvp`, `...member-002-recipe-email-eml-html-mvp`, and `...member-004-recipe-web-page-html-mvp` confirmed source-native member paths, explicit `.txt` blocking, and the expected DOCX/EML/web titles. Close-out applied here: story status is now `Done`, both remaining workflow gates are checked, and the next landing step is `/check-in-diff`.
