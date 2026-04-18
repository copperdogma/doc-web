---
title: "Extend the First Honest Grouped Image-Member Continuation to the First OCR Artifact"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #1 (Ingest), Requirement #2 (Detect), Requirement #3 (Extract), Requirement #6 (Validate), Any format, any condition, Transparency over magic"
spec_refs:
  - "spec:1"
  - "spec:1.1"
  - "spec:2"
  - "spec:2.1"
  - "spec:6"
  - "spec:7"
  - "spec:8"
  - "spec:9"
adr_refs:
  - "ADR-002"
depends_on:
  - "180"
  - "205"
  - "218"
category_refs:
  - "spec:1"
  - "spec:6"
  - "spec:7"
  - "spec:8"
  - "spec:9"
compromise_refs:
  - "C1"
  - "C2"
  - "B10"
input_coverage_refs:
  - "mixed-archive"
  - "image-directory-scans"
architecture_domains:
  - "intake_and_routing"
roadmap_tags:
  - "campaign:maintained-intake-honesty"
legacy_system: ""
---

# Story 224 — Extend the First Honest Grouped Image-Member Continuation to the First OCR Artifact

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/stories/story-179-repo-owned-handwritten-notes-fixture-and-baseline-transcription.md`, `docs/stories/story-180-widen-approved-intake-handoff-image-directory-proof.md`, `docs/stories/story-205-mixed-archive-intake-routing-seam.md`, `docs/stories/story-218-mixed-folder-direct-entry-seam.md`, `docs/stories/story-223-mixed-archive-pdf-member-approved-handoff-seam.md`, `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, `testdata/README.md`, `schemas.py`, `configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml`, `configs/recipes/recipe-mixed-folder-routing-mvp.yaml`, `configs/recipes/recipe-images-ocr-html-mvp.yaml`, `modules/intake/archive_unpack_manifest_v1/main.py`, `modules/intake/folder_members_manifest_v1/main.py`, `modules/intake/archive_route_members_v1/main.py`, `modules/intake/intake_plan_utils.py`, `modules/extract/images_dir_to_manifest_v1/main.py`, `modules/extract/ocr_ai_gpt51_v1/main.py`, `tests/test_mixed_archive_zip_recipe.py`, `tests/test_mixed_folder_recipe.py`, `tests/test_image_directory_intake_recipe.py`, and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower mixed-archive grouped-image ADR or runbook`
**Depends On**: Stories `180`, `205`, and `218`

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

Story 224 already proved the bounded grouped image-member route bridge on both
checked-in entry surfaces through the first downstream `page_image_v1`
artifact. The remaining same-line delta is later-state continuation on those
same grouped probes: prove the grouped child run reaches the first OCR/HTML
artifact (`02_ocr_ai_gpt51_v1/pages_html.jsonl`) on both the ZIP and
source-native folder fixtures without changing the existing PDF-member launch
behavior or widening broader archive claims.

Fresh current-pass exploration shows this stays on the same problem line
instead of earning a new story ID. The owning module is still
`archive_route_members_v1`; the checked-in fixtures remain
`mixed-archive-images-mini.zip` and `mixed-folder-images-mini/`; the grouped
route-row provenance contract is unchanged; the child run still enters the same
maintained `recipe-images-ocr-html-mvp.yaml` lane; and the operator-facing
outcome is still "grouped page-image members continue together through the
maintained downstream recipe." The real missing slice is narrower than a new
runtime seam: `archive_route_members_v1` can already launch grouped child runs
to `ocr_ai` when called directly with `--downstream-end-at ocr_ai`, but the
maintained mixed recipes have no grouped-image-specific continuation surface,
and the existing shared `downstream_end_at` plumbing would also hit PDF-member
launches. This story should add the smallest honest grouped-image-specific stop
surface, prove the bounded OCR continuation on both probes, and keep later
table rescue / build / bundle continuation, OCR-quality widening, and broad
archive ownership out of scope.

## Acceptance Criteria

- [x] This reopened story preserves the completed first-artifact grouped-image
      proof and records why the later OCR boundary still belongs on the same
      Story 224 line instead of creating a new story:
  - [x] the work log cites that the OCR-boundary continuation stays on the
        same `archive_route_members_v1` owner, same checked-in ZIP and
        source-native folder probes, same grouped route-row provenance
        contract, same child `recipe-images-ocr-html-mvp.yaml` run, and same
        operator-facing grouped-member outcome as the completed first-artifact
        slice
  - [x] the existing ZIP and direct-folder first-artifact proof remains
        recorded as completed evidence rather than being silently widened or
        discarded
- [x] A fresh current-pass baseline names the exact maintained grouped-image
      OCR continuation gap from repo evidence:
  - [x] the work log records that
        `tests/fixtures/formats/_coverage-matrix.json`,
        `docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`, and
        `testdata/README.md` still stop the grouped-image claim at the first
        downstream `page_image_v1` artifact before this reopened pass
  - [x] the work log records that the top-level `driver.py` surface rejects
        `--downstream-end-at`, and the maintained mixed recipes expose no
        grouped-image-specific later stop even though
        `archive_route_members_v1` already accepts `--downstream-end-at`
  - [x] the work log cites the reusable substrate honestly:
        `folder_members_manifest_v1` and `archive_unpack_manifest_v1` already
        emit the checked-in grouped-image manifests, `archive_route_members_v1`
        already forwards `--end-at` into grouped child runs, and fresh direct
        route-module runs on the checked-in ZIP and folder manifests already
        emit `02_ocr_ai_gpt51_v1/pages_html.jsonl` under the grouped child run
        ids
- [x] The story lands one bounded grouped-image continuation to the first
      `page_html_v1` artifact honestly on both checked-in entry surfaces:
  - [x] the existing `mixed-archive-images-mini.zip` and
        `mixed-folder-images-mini/` probes remain the only grouped-image
        fixtures; no new archive semantics or probe families are introduced
  - [x] the maintained ZIP and direct-folder mixed recipes (or an honest
        successor on the same route/module line) continue grouped image-member
        child runs to `ocr_ai` and write inspectable
        `02_ocr_ai_gpt51_v1/pages_html.jsonl` artifacts
  - [x] the emitted route evidence preserves the grouped ownership contract
        inspectably on both entry surfaces via shared `group_id`, `group_key`,
        `group_role`, `group_size`, `launch_input_path`, `downstream_run_id`,
        and `first_downstream_artifact`, and either records or clearly derives
        the later OCR artifact path
  - [x] the existing `.txt` blocked rows and PDF-member launch behavior remain
        unchanged rather than being silently altered by the grouped-image
        continuation wiring
- [x] Grouped-image OCR continuation stays source-honest and inspectable on
      the claimed slice:
  - [x] source-native folder member paths, extracted ZIP member paths, grouped
        launch directories, stable image order, child run ids, and inspected
        `page_html_v1` outputs remain traceable end to end
  - [x] the continuation surface stays deterministic and explicit; no new AI
        route pass or archive-wide planner is introduced
  - [x] no claim is introduced for table rescue, chapter build, final HTML
        bundle continuation, scanned or handwritten OCR quality improvement,
        nested archives, attachment extraction, or broad heterogeneous archive
        ownership
- [x] Coverage, docs, and eval truth surfaces remain aligned with the reopened
      combined outcome:
  - [x] the completed first-artifact grouped-image proof remains documented as
        prior evidence
  - [x] `tests/fixtures/formats/_coverage-matrix.json`,
        `docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`, and
        `testdata/README.md` widen only as far as the fresh ZIP and
        direct-folder OCR-boundary proof justifies
  - [x] `approved-intake-handoff` and `auto-book-type-detection` remain
        unchanged unless fresh current-pass evidence proves this grouped-image
        continuation also belongs in one of those top-level automation
        surfaces

## Out of Scope

- Broad “any folder or archive of images” ownership beyond the existing two
  checked-in grouped probes
- Arbitrary photo-album clustering, duplicate-image collapse, cover/back-matter
  detection, or other broad image-set semantics
- Grouped-image continuation beyond the first downstream `page_html_v1`
  artifact (for example table rescue, illustration crop, portionize, chapter
  build, or final HTML bundle proof)
- Scanned or handwritten OCR quality improvements beyond proving that the
  existing checked-in grouped probes can reach the first OCR artifact
- PDF-member launch changes, nested archives, attachments, `.msg`, mailbox
  cleanup, or connector workflows
- Reopening Story 191 or changing the handwritten OCR blocker line
- New `doc-web` output-contract architecture beyond the minimum inspectable
  grouped-member provenance and later OCR-artifact lookup needed to prove the
  bounded slice

## Approach Evaluation

- **Simplification baseline**: already measured in this pass. Fresh direct
  `archive_route_members_v1` runs on the checked-in ZIP and folder manifests
  with `--downstream-end-at ocr_ai` both launched grouped child runs that
  emitted `02_ocr_ai_gpt51_v1/pages_html.jsonl`, which means the OCR runtime
  and grouped child-run substrate already exist. The missing seam is the
  maintained parameter surface and, if needed, one more inspectable artifact
  pointer on the route row.
- **AI-only**: not the right move. There is no new reasoning gap on this line;
  grouped member detection already exists and the OCR model already runs in the
  child recipe.
- **Hybrid**: only consider if current route-row provenance cannot expose the
  later OCR artifact honestly without a tiny helper. No new model decision is
  justified yet.
- **Pure code**: current front-runner. The likely work is a grouped-image-
  specific downstream stop in `archive_route_members_v1` plus recipe/test/doc
  wiring, while preserving the PDF-member launch continuation on the same
  mixed recipes.
- **Repo constraints / prior decisions**: `spec:1.1` keeps recipe ownership
  explicit under `C2`; `spec:2.1` makes the first OCR artifact a real extract
  boundary; ADR-002 keeps the accepted `doc-web` boundary inspectable; Story
  179 already proved the same underlying `handwritten-notes-mini-images` pages
  can clear `ocr_ai_gpt51_v1` on the maintained generic image-directory lane;
  Story 223 keeps PDF-member launch live on the same mixed ZIP/folder recipes,
  so any new grouped-image stop must not hijack that path.
- **Existing patterns to reuse**: `modules/intake/archive_route_members_v1`,
  `modules/intake/intake_plan_utils.py`,
  `modules/extract/images_dir_to_manifest_v1/main.py`,
  `modules/extract/ocr_ai_gpt51_v1/main.py`,
  `tests/test_mixed_archive_zip_recipe.py`,
  `tests/test_mixed_folder_recipe.py`,
  `tests/test_image_directory_intake_recipe.py`, and Story 179's checked-in
  OCR surface on the same mini handwritten pages.
- **Eval**: the deciding proof surface is a fresh maintained `driver.py` run
  on the checked-in ZIP and folder grouped-image probes plus manual inspection
  of the route rows and the grouped child
  `02_ocr_ai_gpt51_v1/pages_html.jsonl` artifacts. If the route-row contract
  needs a new later-artifact field, prove that need during implementation
  before widening `schemas.py`.

## Tasks

- [x] Preserve the completed first-artifact grouped-image proof as prior
      evidence while reopening the same line for the OCR-boundary slice
- [x] Freeze the current maintained grouped-image OCR continuation gap from repo
      reality:
  - [x] verify the `mixed-archive` coverage row and current methodology/docs
        wording still stop at the first downstream `page_image_v1` artifact
  - [x] verify that top-level `driver.py` still rejects
        `--downstream-end-at`, so the maintained mixed recipes cannot expose
        the later grouped stop through normal entry
  - [x] verify the reusable substrate honestly: fresh manifest-only runs on the
        checked-in ZIP and folder probes plus direct route-module invocations
        with `--downstream-end-at ocr_ai` already emit grouped child
        `page_html_v1` artifacts
- [x] Land the smallest grouped-image-specific maintained continuation surface:
  - [x] prefer a grouped-image-specific downstream stop parameter over reusing
        the shared route-wide `downstream_end_at`, so PDF-member launches on
        the same mixed recipes stay unchanged
  - [x] keep the existing ZIP and direct-folder grouped route-row contract
        intact and source-honest
  - [x] keep the existing route-row schema because `downstream_run_id` plus the
        grouped child run layout is honest enough for OCR-artifact lookup; no
        `schemas.py` change was needed
- [x] Add focused regression coverage for the OCR-boundary grouped-image slice:
  - [x] recipe wiring expectations for the maintained ZIP and folder recipes
  - [x] grouped route contract assertions for both entry surfaces
  - [x] explicit no-regression assertions that PDF-member launch behavior on
        the same mixed recipes is unchanged
- [x] If this story changes documented format coverage or graduation reality:
      update `tests/fixtures/formats/_coverage-matrix.json` and any relevant
      methodology state honestly
- [x] Check whether the chosen implementation makes any existing code, helper
      paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for the reopened scope:
  - [x] Targeted regression checks:
        `pytest -q tests/test_mixed_archive_zip_recipe.py tests/test_mixed_folder_recipe.py tests/test_image_directory_intake_recipe.py`
  - [x] Default Python lint: `make lint`
  - [x] Default Python checks: `make test`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through
        `driver.py` on the checked-in ZIP and folder grouped-image recipes,
        verify artifacts in `output/runs/`, and manually inspect grouped route
        evidence plus the child `02_ocr_ai_gpt51_v1/pages_html.jsonl` data
  - [x] If methodology truth surfaces changed: `make methodology-compile` and
        `make methodology-check`
  - [x] If agent tooling changed: not needed; agent tooling stayed unchanged
- [x] Evals or goldens stay unchanged unless the widened grouped-image truth
      surface proves otherwise; `docs/evals/registry.yaml` should remain
      untouched by default
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: the grouped-image OCR continuation claim traces to
        member paths, group metadata, child run ids, and inspected
        `page_html_v1` artifacts
  - [x] T1 — AI-First: do not add a new AI routing pass when existing grouped
        routing plus the maintained OCR model already solve the slice
  - [x] T2 — Eval Before Build: freeze the current maintained recipe gap and
        the direct route-module OCR baseline before adding glue
  - [x] T3 — Fidelity: preserve image order and member provenance faithfully
        while carrying the grouped child run to the first OCR artifact
  - [x] T4 — Modular: reuse the existing mixed ZIP/folder recipes plus the
        maintained `images_dir` OCR lane instead of inventing a second grouped
        image stack
  - [x] T5 — Inspect Artifacts: manually open the route rows and grouped child
        `page_html_v1` output, not just the logs

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

- **Owning module / area**: intake and routing on the existing mixed-archive
  line, with the likely implementation owner still
  `archive_route_members_v1`. `intake_plan_utils.py` may need a narrow helper
  touch only if the grouped-image-specific downstream stop belongs in shared
  command-building logic. This is not a new `doc-web` boundary or a second
  grouped-image runtime.
- **Methodology reality**: this reopened work now spans `spec:1` and
  `spec:2`, with supporting ties to `spec:6`, `spec:7`, `spec:8`, and
  `spec:9`. In the current repo state, `spec:1`, `spec:2`, `spec:6`,
  `spec:8`, and `spec:9` substrate exists; `spec:7` remains `partial`; and
  `C1`, `C2`, and `B10` remain `climb`. The `mixed-archive` coverage row is
  still `passing` on six checked-in probes across three behavior classes, and
  this story now widens the grouped-image claim from the first downstream
  `page_image_v1` artifact to the first downstream `page_html_v1` artifact on
  the same checked-in ZIP and source-native folder probes. Status is `Done`,
  not `Draft`, because the code, tests, real driver proofs, truth-surface
  updates, and close-out gates are all complete in this pass.
- **Substrate evidence**: verified in this pass that
  `modules/intake/archive_route_members_v1/main.py` already parses
  `--downstream-end-at` and forwards it into grouped child runs,
  `modules/intake/intake_plan_utils.py` already appends `--end-at` through
  `build_explicit_recipe_driver_command(...)`, and fresh direct route-module
  runs on manifests from the checked-in ZIP and folder grouped probes emitted
  `02_ocr_ai_gpt51_v1/pages_html.jsonl` under
  `story224-ocr-baseline-*-member-002-grouped-recipe-images-ocr-html-mvp`.
  Shipped slice: `archive_route_members_v1` now accepts
  `--grouped-image-downstream-end-at`, the maintained mixed ZIP/folder recipes
  now set that bounded surface to `ocr_ai`, focused tests prove grouped child
  commands stop at `ocr_ai` while PDF-member launches stay unchanged, and fresh
  real driver runs on `story224-ocr-zip-r1` plus `story224-ocr-folder-r1`
  emitted grouped child `02_ocr_ai_gpt51_v1/pages_html.jsonl` artifacts on both
  entry surfaces.
- **Data contracts / schemas**: `archive_member_route_v1` already carries the
  grouped-image provenance fields (`group_id`, `group_key`, `group_role`,
  `group_size`, `launch_input_path`, `downstream_run_id`, and
  `first_downstream_artifact`) that this reopened slice reuses. Fresh baseline
  evidence also showed that `first_downstream_artifact` still points at
  `01_images_dir_to_manifest_v1/pages_images_manifest.jsonl` even when the
  child run reaches `ocr_ai`. The current pass kept that contract unchanged and
  resolved the open question in favor of no schema change: the route rows plus
  shared `downstream_run_id` are inspectable enough to derive
  `02_ocr_ai_gpt51_v1/pages_html.jsonl`, and README/RUNBOOK wording now makes
  that lookup explicit.
- **File sizes**: likely touch points are
  `modules/intake/archive_route_members_v1/main.py` (`523` lines after recent
  growth),
  `modules/intake/intake_plan_utils.py` (`390` lines),
  `configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml` (`21` lines),
  `configs/recipes/recipe-mixed-folder-routing-mvp.yaml` (`21` lines),
  `tests/test_mixed_archive_zip_recipe.py` (`1049` lines, >500),
  `tests/test_mixed_folder_recipe.py` (`292` lines),
  `README.md` (large),
  `docs/RUNBOOK.md` (large),
  `tests/fixtures/formats/_coverage-matrix.json` (large),
  and `schemas.py` (large, only if the artifact-pointer question requires it).
  Keep edits especially surgical in the oversized files.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`,
  `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002,
  Stories 179/180/205/218/223, `tests/fixtures/formats/_coverage-matrix.json`,
  `README.md`, `docs/RUNBOOK.md`, `testdata/README.md`, `schemas.py`,
  `configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml`,
  `configs/recipes/recipe-mixed-folder-routing-mvp.yaml`,
  `configs/recipes/recipe-images-ocr-html-mvp.yaml`,
  `modules/intake/archive_unpack_manifest_v1/main.py`,
  `modules/intake/folder_members_manifest_v1/main.py`,
  `modules/intake/archive_route_members_v1/main.py`,
  `modules/intake/intake_plan_utils.py`,
  `modules/extract/images_dir_to_manifest_v1/main.py`,
  `modules/extract/ocr_ai_gpt51_v1/main.py`,
  `tests/test_mixed_archive_zip_recipe.py`,
  `tests/test_mixed_folder_recipe.py`, and
  `tests/test_image_directory_intake_recipe.py`. No narrower grouped-image
  mixed-archive ADR, runbook, scout note, or project note was found after
  search.

## Files to Modify

- `modules/intake/archive_route_members_v1/main.py` — add the smallest
  grouped-image-specific later-stop surface while preserving ZIP/folder grouped
  routing and PDF-member launch behavior
- `modules/intake/intake_plan_utils.py` — only if the grouped-image-specific
  stop belongs in shared driver-command construction rather than route-local
  logic
- `configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml` — expose the
  maintained grouped-image OCR-boundary stop on the checked-in ZIP probe
- `configs/recipes/recipe-mixed-folder-routing-mvp.yaml` — expose the
  maintained grouped-image OCR-boundary stop on the checked-in source-native
  folder probe
- `tests/test_mixed_archive_zip_recipe.py` — extend grouped-image contract
  coverage to the OCR-boundary slice and assert no PDF-member regressions
- `tests/test_mixed_folder_recipe.py` — extend grouped-image contract coverage
  to the OCR-boundary slice on the checked-in source-native folder probe
- `README.md` — widen the bounded grouped-image claim only as far as the new
  OCR-boundary proof justifies
- `docs/RUNBOOK.md` — replace the first-artifact grouped-image smoke guidance
  with the bounded OCR-boundary guidance if it lands
- `tests/fixtures/formats/_coverage-matrix.json` — widen the `mixed-archive`
  row only as far as the shipped OCR-boundary slice justifies
- `docs/methodology/state.yaml` — replace the current grouped-image
  first-artifact note only if this reopened slice lands
- `testdata/README.md` — update the grouped-image probe notes from
  `images_to_manifest` to the bounded OCR-boundary claim if shipped
- `schemas.py` — only if the later-artifact lookup question cannot be answered
  honestly through the existing route-row contract
- `tests/test_image_directory_intake_recipe.py` — only if the grouped-image OCR
  continuation needs a shared no-regression assertion on the underlying
  `images_dir` OCR lane

## Redundancy / Removal Targets

- Doc wording that still treats grouped-image support as stopping at the first
  downstream `page_image_v1` artifact once the OCR-boundary proof lands
- Any duplicated route logic that tries to special-case grouped-image later
  stops separately from the existing grouped child-run path
- Any temporary artifact-lookup workaround if one bounded route-row field ends
  up being the cleaner inspectable contract

## Notes

- Reopen justification: a new Story 226 would not be honest. This is later-
  state progression on the same grouped-image route/module line: same owner,
  same probes, same grouped route-row contract, same child recipe, and same
  operator-facing grouped-member continuation. The validation boundary moves
  from the first child artifact to the first OCR artifact, but the runtime seam
  stays the same.
- The existing completed ZIP and direct-folder first-artifact slices remain the
  baseline evidence for grouped route rows and grouped child-run identity. This
  reopened story widens only the continuation depth on those same checked-in
  grouped probes.
- The checked-in grouped probes already reuse the `handwritten-notes-mini`
  pages that Story 179 proved on the maintained generic OCR lane, so the
  current reopened slice can use those same pages as a bounded OCR target
  without widening the real handwritten support claim.
- Keep the continuation policy deterministic and inspectable by default.
  Prefer a grouped-image-specific later stop and the existing grouped child-run
  contract over any new AI route decision or archive-wide planner.

## Plan

### Exploration Summary

- **Ideal alignment:** proceed. This reopened slice closes a real `spec:1.1` /
  `C2` honesty gap on the maintained mixed-archive line and reaches the first
  real extract boundary in `spec:2.1` without adding a new runtime or AI route
  pass.
- **Relevant methodology state:** `docs/methodology/state.yaml` still records
  the active bias as `campaign:maintained-intake-honesty`; `spec:1`,
  `spec:2`, `spec:6`, `spec:8`, and `spec:9` substrate exists; `spec:7`
  remains `partial`; and the intake notes explicitly say grouped-image support
  stops at the first downstream `page_image_v1` artifact today.
- **Relevant coverage rows:** the `mixed-archive` row is already `passing` on
  six checked-in probes across three behavior classes, but it still documents
  grouped-image support only through the first downstream `page_image_v1`
  artifact. Story 179's `handwritten-notes-mini-images` proof on the generic
  OCR lane is the local quality reference for the reused page images inside the
  grouped probes.
- **Decision docs consulted:** `docs/ideal.md`, `docs/spec.md`,
  `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002,
  Stories 179/180/205/218/223, the current `mixed-archive` coverage row,
  `README.md`, `docs/RUNBOOK.md`, `testdata/README.md`, and the current
  mixed-archive runtime code/tests. No narrower grouped-image ADR, runbook,
  scout note, or project note was found.
- **Fresh current-pass code evidence:**
  - `archive_route_members_v1` already parses `--downstream-end-at` and uses
    it for grouped child runs.
  - `build_explicit_recipe_driver_command(...)` already appends `--end-at` to
    child `driver.py` invocations.
  - The maintained mixed ZIP/folder recipes currently expose only
    `pdf_member_handoff_mode: launch`; there is no grouped-image-specific later
    stop in recipe params.
  - The top-level `driver.py` surface rejects `--downstream-end-at`, so the
    existing maintained grouped-image proofs cannot be widened by command-line
    override alone.
- **Fresh current-pass runtime baseline:**
  - `python driver.py --recipe configs/recipes/recipe-mixed-folder-routing-mvp.yaml --input-folder testdata/mixed-folder-images-mini --run-id story224-ocr-baseline-folder-manifest-r1 --allow-run-id-reuse --output-dir output/runs --end-at folder_manifest --force`
    produced
    `output/runs/story224-ocr-baseline-folder-manifest-r1/01_folder_members_manifest_v1/archive_members_manifest.jsonl`.
  - `python driver.py --recipe configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml --input-zip testdata/mixed-archive-images-mini.zip --run-id story224-ocr-baseline-zip-manifest-r1 --allow-run-id-reuse --output-dir output/runs --end-at archive_unpack --force`
    produced
    `output/runs/story224-ocr-baseline-zip-manifest-r1/01_archive_unpack_manifest_v1/archive_members_manifest.jsonl`.
  - Direct route-module invocations with `PYTHONPATH=. python modules/intake/archive_route_members_v1/main.py ... --downstream-end-at ocr_ai`
    on those fresh manifests launched grouped child runs that emitted:
    - `output/runs/story224-ocr-baseline-folder-manifest-r1-member-002-grouped-recipe-images-ocr-html-mvp/02_ocr_ai_gpt51_v1/pages_html.jsonl`
    - `output/runs/story224-ocr-baseline-zip-manifest-r1-member-002-grouped-recipe-images-ocr-html-mvp/02_ocr_ai_gpt51_v1/pages_html.jsonl`
  - Manual inspection of those OCR artifacts confirmed the reused mini
    handwritten pages remain clean enough for a bounded OCR proof on this seam:
    page 2 still contains "The letters from Aunt Elise are tied with green
    ribbon, not red." and "bring the small brass compass back to the desk
    drawer." on both the folder and ZIP grouped child runs.
- **Patterns to follow:** Story 224's existing grouped route-row contract,
  Story 223's discipline around not regressing PDF-member launch on the same
  mixed recipes, and Story 179's OCR artifact inspection discipline on the same
  page family.
- **Surprises found:** the runtime substrate for grouped OCR continuation is
  already present; the honest missing slice is narrower than expected. The open
  question is not OCR capability. It is maintained-surface wiring and whether
  the existing route-row contract exposes the later OCR artifact inspectably
  enough without one more field.
- **Files likely to change:** `modules/intake/archive_route_members_v1/main.py`,
  the two maintained mixed ZIP/folder recipes, grouped-image tests, and the
  mixed-archive truth surfaces in docs/state.
- **Files at risk:** `tests/test_mixed_archive_zip_recipe.py`, `README.md`,
  `docs/RUNBOOK.md`, `tests/fixtures/formats/_coverage-matrix.json`, and
  `schemas.py` are the high-attention files; keep edits surgical.

### Eval-First Gate

- **Baseline result:** fresh current-pass direct route-module runs already
  prove the grouped child OCR continuation succeeds on both checked-in probes.
  The current maintained gap is therefore not OCR failure; it is that the
  maintained mixed ZIP/folder recipes cannot expose that stop honestly.
- **Approach comparison:**
  - **No-code/manual workaround:** direct route-module invocation with
    `--downstream-end-at ocr_ai` works, but it is not an honest maintained
    recipe surface.
  - **AI-only:** rejected. No new AI reasoning surface is missing.
  - **Hybrid:** only if the route-row contract proves too opaque and one tiny
    helper is cleaner than a broader schema change.
  - **Pure code/plumbing:** current winner. The smallest likely path is a
    grouped-image-specific later-stop parameter plus recipe/test/doc wiring.

### Recommended Implementation Plan

- **Recommended path:** reopen Story 224 in place and ship one grouped-image-
  specific OCR-boundary continuation on the existing checked-in ZIP and folder
  probes. Relative effort: `S`.

1. Reopen the same story line honestly (`XS`)
   - Files: this story plus generated methodology views.
   - Change: replace the stale direct-folder-parity scope with the current
     OCR-boundary slice while preserving the completed first-artifact proof in
     the work log and notes.
   - Done when: Story 224 is `Pending` again with acceptance criteria and tasks
     that match the real next slice.

2. Add the smallest grouped-image-specific later-stop surface (`S`)
   - Files: `modules/intake/archive_route_members_v1/main.py`,
     `configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml`, and
     `configs/recipes/recipe-mixed-folder-routing-mvp.yaml`.
   - Preferred change: add a grouped-image-specific downstream stop parameter
     (for example `grouped_image_downstream_end_at`) that only affects grouped
     image-member child runs. Keep the existing route-wide
     `downstream_end_at` behavior unchanged for PDF-member continuation and any
     other future call sites.
   - Done when: the maintained mixed ZIP/folder recipes can drive grouped child
     runs to `ocr_ai` without changing PDF-member launch behavior on the same
     recipes.

3. Decide the smallest honest inspectability contract (`XS`)
   - Files: maybe none beyond the route module; `schemas.py` only if needed.
   - Preferred change: first try to keep the existing route-row schema and use
     `downstream_run_id` plus `terminal_reason = grouped_image_end_at:ocr_ai`
     as the inspectable lookup key for the OCR artifact.
   - Escalation rule: only add a bounded later-artifact field to
     `archive_member_route_v1` if fresh implementation review shows the current
     lookup path is too opaque for operators or docs to use honestly.
   - Done when: the story can cite a concrete, inspectable OCR artifact path
     from the parent route evidence without hand-wavy lookup rules.

4. Extend focused regression coverage (`S`)
   - Files: `tests/test_mixed_archive_zip_recipe.py` and
     `tests/test_mixed_folder_recipe.py`; `tests/test_image_directory_intake_recipe.py`
     only if a shared OCR no-regression assertion becomes necessary.
   - Change:
     - recipe wiring tests assert the grouped-image-specific later stop is
       configured on both maintained mixed recipes
     - grouped-image smoke tests assert grouped child driver commands end at
       `ocr_ai`, grouped route rows keep the existing provenance contract, and
       the child `02_ocr_ai_gpt51_v1/pages_html.jsonl` artifact exists
     - explicit no-regression checks confirm PDF-member launch still uses the
       existing continuation path
   - Done when: the OCR-boundary grouped-image slice is fixture-backed on both
     entry surfaces and existing mixed PDF/direct-entry tests still pass.

5. Run narrow real validation and inspect artifacts (`S`)
   - Files: no planned code changes; produces proof under `output/runs/`.
   - Command targets:
     - `python driver.py --recipe configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml --input-zip testdata/mixed-archive-images-mini.zip --run-id <zip_run> --allow-run-id-reuse --output-dir output/runs --force`
     - `python driver.py --recipe configs/recipes/recipe-mixed-folder-routing-mvp.yaml --input-folder testdata/mixed-folder-images-mini --run-id <folder_run> --allow-run-id-reuse --output-dir output/runs --force`
   - Artifact checks:
     - parent manifests and route rows for both probes
     - child `02_ocr_ai_gpt51_v1/pages_html.jsonl` for both grouped child runs
   - Manual inspection targets:
     - page 1 opening "March 3, 1985"
     - page 2 lines mentioning Aunt Elise's green ribbon and the brass compass
   - Done when: both maintained grouped probes reach `page_html_v1` and the
     inspected OCR text remains faithful on the bounded mini pages.

6. Update truth surfaces narrowly (`XS`)
   - Files: `tests/fixtures/formats/_coverage-matrix.json`,
     `docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`,
     `testdata/README.md`, and this story file.
   - Change: widen the grouped-image claim only from "first downstream
     `page_image_v1` artifact" to "first downstream `page_html_v1` artifact" on
     the existing ZIP and folder grouped probes. Keep later continuation,
     broader archive semantics, and handwritten quality claims unchanged.
   - Done when: docs and state say exactly what the shipped OCR-boundary proof
     says, and no more.

### Impact Analysis

- **Primary blast radius:** grouped-image child-run plumbing in
  `archive_route_members_v1` and the two maintained mixed ZIP/folder recipes.
- **Secondary blast radius:** grouped-image tests plus support wording in the
  coverage matrix, methodology state, README, RUNBOOK, and `testdata/README.md`.
- **What could break:** PDF-member launch on the same mixed recipes if the new
  later-stop surface is not grouped-image-specific; ZIP/folder grouped-image
  tests if the existing grouped provenance contract regresses; route evidence
  if the later OCR artifact cannot be found inspectably after the recipe
  change.
- **Redundancy plan:** remove wording that still says grouped-image support
  stops at `images_to_manifest` if the OCR-boundary slice lands.
- **Human-approval blockers:** one small design choice remains open.
  Recommended default is "no schema change unless the current route-row lookup
  is too opaque." If that proves false during implementation, the scope would
  expand modestly to include a bounded `archive_member_route_v1` field update.

## Work Log

20260417-2331 — mark-story-done close-out: validated Story 224 complete on the
current tip, set the story status to `Done`, checked `Validation complete` plus
`Story marked done via /mark-story-done`, regenerated the methodology views,
and updated the existing Story 224 changelog entry instead of duplicating it.
Fresh close-out evidence in this pass: `python -m ruff check modules/ tests/`
passed; `python -m pytest tests/` passed at `598 passed, 4 warnings` in
`701.73s`; `validate_artifact.py` passed again on
`output/runs/story224-ocr-zip-r1/02_archive_route_members_v1/archive_member_routes.jsonl`,
`output/runs/story224-ocr-zip-r1-member-002-grouped-recipe-images-ocr-html-mvp/02_ocr_ai_gpt51_v1/pages_html.jsonl`,
`output/runs/story224-ocr-folder-r1/02_archive_route_members_v1/archive_member_routes.jsonl`,
and
`output/runs/story224-ocr-folder-r1-member-002-grouped-recipe-images-ocr-html-mvp/02_ocr_ai_gpt51_v1/pages_html.jsonl`;
manual inspection again confirmed `grouped_image_end_at:ocr_ai` plus the
expected March 3 / Aunt Elise / brass compass OCR text on the bounded grouped
child runs. ADR-002 remains `ACCEPTED`; this story does not newly resolve an
ADR-002 `Remaining Work` item enough to change that parent ADR. Next step:
`/check-in-diff`.

20260417-2312 — build-story verify: completed the OCR-boundary implementation
pass and left Story 224 in the correct handoff state for `/validate 224`.
Fresh checks in this pass: `pytest -q tests/test_mixed_archive_zip_recipe.py
tests/test_mixed_folder_recipe.py tests/test_image_directory_intake_recipe.py`
passed at `21 passed, 2 skipped`; `python -m ruff check
modules/intake/archive_route_members_v1/main.py
tests/test_mixed_archive_zip_recipe.py tests/test_mixed_folder_recipe.py`
passed; `make lint` passed; and `make test` passed fresh at `598 passed, 4
warnings` in `681.84s`. Fresh real driver proofs after clearing stale bytecode:
`python driver.py --recipe configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml --input-zip testdata/mixed-archive-images-mini.zip --run-id story224-ocr-zip-r1 --allow-run-id-reuse --output-dir output/runs --force`
and
`python driver.py --recipe configs/recipes/recipe-mixed-folder-routing-mvp.yaml --input-folder testdata/mixed-folder-images-mini --run-id story224-ocr-folder-r1 --allow-run-id-reuse --output-dir output/runs --force`
both completed successfully. `validate_artifact.py` passed on the parent
manifests and route artifacts for both runs plus the grouped child
`page_html_v1` artifacts. Manual inspection confirmed
`grouped_image_end_at:ocr_ai`, shared grouped provenance, and explicit blocked
`.txt` rows at
`output/runs/story224-ocr-zip-r1/02_archive_route_members_v1/archive_member_routes.jsonl`
and
`output/runs/story224-ocr-folder-r1/02_archive_route_members_v1/archive_member_routes.jsonl`;
the grouped child OCR artifacts at
`output/runs/story224-ocr-zip-r1-member-002-grouped-recipe-images-ocr-html-mvp/02_ocr_ai_gpt51_v1/pages_html.jsonl`
and
`output/runs/story224-ocr-folder-r1-member-002-grouped-recipe-images-ocr-html-mvp/02_ocr_ai_gpt51_v1/pages_html.jsonl`
preserve the expected bounded text including "March 3, 1985" on page 1 and the
Aunt Elise / brass compass lines on page 2. Result: grouped image-members now
continue to the first OCR artifact on both maintained entry surfaces without a
schema change and without altering PDF-member launch behavior. Truth surfaces
were updated narrowly, `docs/evals/registry.yaml` stayed untouched, and
`Build complete` is now checked while validation and close-out remain pending.
Next step: `/validate 224`.

20260417-2258 — build-story implement: added one grouped-image-specific later
stop instead of reusing the shared route-wide `downstream_end_at` surface.
`modules/intake/archive_route_members_v1/main.py` now accepts
`--grouped-image-downstream-end-at` and uses it only for grouped image-member
child runs, falling back to the old behavior when the grouped-specific flag is
absent. `modules/intake/archive_route_members_v1/module.yaml` now exposes that
param to driver-managed recipe execution, and both maintained mixed ZIP/folder
recipes set `grouped_image_downstream_end_at: ocr_ai`. Focused regression
coverage widened in `tests/test_mixed_archive_zip_recipe.py` and
`tests/test_mixed_folder_recipe.py`: grouped-image expectations now assert
`grouped_image_end_at:ocr_ai`, derive and inspect the grouped child
`02_ocr_ai_gpt51_v1/pages_html.jsonl` artifact, and keep one explicit
no-regression assertion that PDF-member recommendation commands do not inherit
the grouped-only stop. Result: the maintained surface now matches the already-
verified direct route-module OCR substrate without widening route-row schema or
touching PDF-member continuation behavior.

20260417-2229 — build-story explore/plan: reopened Story 224 from the
completed first-artifact grouped-image proof to the next same-line OCR-boundary
slice after triage confirmed this is still the strongest actionable move inside
`campaign:maintained-intake-honesty`. Fresh current-pass evidence for the new
scope: `tests/fixtures/formats/_coverage-matrix.json`,
`docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`, and
`testdata/README.md` still stop grouped-image support at the first downstream
`page_image_v1` artifact; top-level `driver.py` rejects
`--downstream-end-at`; and the maintained mixed ZIP/folder recipes expose no
grouped-image-specific later stop. Verified reusable substrate instead of
guessing: fresh manifest-only runs on `testdata/mixed-archive-images-mini.zip`
and `testdata/mixed-folder-images-mini/` plus direct
`archive_route_members_v1` invocations with `--downstream-end-at ocr_ai`
already launched grouped child runs that emitted
`02_ocr_ai_gpt51_v1/pages_html.jsonl` under the grouped child run ids, and
manual inspection on both probes confirmed clean page text including "March 3,
1985" and the Aunt Elise / brass compass lines. Result: the missing slice is
maintained grouped-image-specific continuation wiring, not OCR capability.
Updated the story goal, acceptance criteria, tasks, notes, and plan to reflect
that same-line continuation honestly; recommended default remains no schema
change unless `downstream_run_id` plus `terminal_reason` proves too opaque for
artifact lookup. Next step: recompile methodology views, present the plan, and
wait for explicit approval before implementation code.

20260417-2236 — build-story start: user approved the OCR-boundary plan, so
Story 224 is now `In Progress`. Next step: land a grouped-image-specific later
stop on the existing mixed ZIP/folder route/module line, prove it reaches
`ocr_ai` without altering PDF-member launches, and then rerun the bounded real
driver proofs plus truth-surface updates.

20260417-0021 — create-story bootstrap: created Story 224 for the grouped
image-member seam after verifying a new owner was honest at that time. Evidence
reviewed: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`,
`docs/methodology/graph.json`, Stories 180/205/218/221/223, the
`mixed-archive` and `image-directory-scans` coverage rows, and the current
mixed-archive runtime code and tests. Next step: finalize the bounded grouped-
image scope and verify whether the route bridge is buildable now.

20260417-0036 — build-story explore: confirmed the original ZIP slice was
honestly buildable. Fresh baseline evidence in that pass showed a scratch ZIP
preserved the shared `pages/` directory while both `.png` members still blocked
as `unsupported_archive_member_suffix:.png`; a direct downstream reuse probe on
that extracted directory then emitted ordered `page_image_v1` rows. Result: the
missing seam was the grouped route bridge, not ZIP extraction or downstream
image intake.

20260417-0757 — build-story implement: shipped the bounded ZIP-only grouped
image-member route-row contract. `archive_route_members_v1` now groups one
shared-parent page-image set on ZIP entry, launches exactly one
`--input-images` child run into `recipe-images-ocr-html-mvp.yaml`, and stamps
`group_id`, `group_key`, `group_role`, `group_size`, shared
`launch_input_path`, shared `downstream_run_id`, and shared
`first_downstream_artifact` on each grouped member row while leaving direct-
entry and PDF-member paths unchanged. Added the checked-in ZIP probe plus
focused grouped-image coverage in `tests/test_mixed_archive_zip_recipe.py`.

20260417-0918 — build-story verify: aligned the mixed-archive truth surfaces
with the shipped ZIP-only grouped-image slice and reran repo-level checks.
Evidence from that pass: `make methodology-compile`, `make lint`, and
`make test` all passed; the shipped claim was narrowed to one ZIP-only grouped
image-member continuation to the first downstream `page_image_v1` artifact, and
direct-folder parity remained explicitly out of scope.

20260417-1052 — mark-story-done close-out: revalidated the ZIP-only slice on
the current branch tip and closed the story as the bounded grouped-image first-
artifact seam. Fresh evidence from that pass included `make lint`, `make test`,
a fresh driver run on `testdata/mixed-archive-images-mini.zip`, schema
validation of the mixed-archive manifest and route artifacts, schema validation
of the child `pages_images_manifest.jsonl`, and manual artifact inspection
confirming the two page images share one grouped child run while the `.txt`
member stays explicitly blocked.

20260417-1135 — anti-fragmentation reopen: reran the grouped-image line under
the tightened behavior-class rule after triage confirmed the only remaining
bounded grouped-image gap is direct-folder parity. Fresh repo evidence in this
pass: `tests/fixtures/formats/_coverage-matrix.json` and
`docs/methodology/state.yaml` still explicitly exclude direct-folder grouped
image-member parity; `modules/intake/archive_route_members_v1/main.py` still
gates `_grouped_image_candidates(...)` behind `archive_format == "zip"`; and
`modules/intake/folder_members_manifest_v1/main.py` plus
`tests/test_mixed_folder_recipe.py` confirm the source-native folder substrate
exists but lacks grouped-image proof. Result: reopened Story 224 as `Pending`,
expanded its goal/ACs/tasks/plan to one bounded direct-folder grouped-image
continuation on the same route/module and first-artifact line, and kept the
completed ZIP slice as prior evidence instead of creating a new story. Next
step: `/build-story 224` should freeze the direct-folder baseline, add one
repo-owned folder grouped-image probe, and implement the smallest source-native
parity change that preserves the existing ZIP contract.

20260417-1440 — build-story explore: froze the direct-folder grouped-image
baseline with fresh runtime evidence and narrowed the likely implementation
surface. Created a temporary source-native folder probe at
`/tmp/story224-folder-baseline-src` with
`pages/page-001.png`, `pages/page-002.png`, and `notes/readme.txt`, then ran
`python driver.py --recipe configs/recipes/recipe-mixed-folder-routing-mvp.yaml --input-folder /tmp/story224-folder-baseline-src --run-id story224-folder-baseline-r1 --allow-run-id-reuse --output-dir output/runs --force`.
The stamped manifest at
`output/runs/story224-folder-baseline-r1/01_folder_members_manifest_v1/archive_members_manifest.jsonl`
proved source-native relative ordering and source-native `extracted_path`
values for the bounded folder probe. The stamped route artifact at
`output/runs/story224-folder-baseline-r1/02_archive_route_members_v1/archive_member_routes.jsonl`
isolated the exact current gap: `launched=0, blocked=3, skipped=0, failed=0`,
with both page-image rows still stamped
`terminal_reason = unsupported_archive_member_suffix:.png` and no grouped
provenance fields populated. A direct downstream reuse probe on the same page
directory —
`python driver.py --recipe configs/recipes/recipe-images-ocr-html-mvp.yaml --input-images /tmp/story224-folder-baseline-src/pages --run-id story224-folder-images-direct-r1 --allow-run-id-reuse --output-dir output/runs --end-at images_to_manifest --force`
— emitted
`output/runs/story224-folder-images-direct-r1/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl`
with ordered `page-001.png` then `page-002.png`. Impact: the remaining gap is
the folder route bridge only, not missing folder substrate, schema, or
downstream image-directory support. The likely coherent implementation slice is
therefore one new repo-owned folder fixture
(`testdata/mixed-folder-images-mini/` plus metadata), one route change in
`archive_route_members_v1` with no recipe default change unless new evidence
forces it, focused coverage in `tests/test_mixed_folder_recipe.py`, and narrow
truth-surface updates if the proof lands. Next step: present this plan for user
approval before writing implementation code.

20260417-1450 — build-story start: user approved the implementation plan, so
Story 224 is now `In Progress`. Next step: land the bounded direct-folder
grouped-image parity slice in code, fixtures, tests, and truth surfaces, then
prove it with a real `driver.py` folder run and artifact inspection.

20260417-1605 — build-story implement: widened the grouped-image route bridge
from ZIP-only to ZIP-or-folder entry by changing
`modules/intake/archive_route_members_v1/main.py` so
`_grouped_image_candidates(...)` now accepts `archive_format in {"zip",
"folder"}` while leaving the existing ZIP grouped contract untouched. Added the
repo-owned source-native grouped-image probe under
`testdata/mixed-folder-images-mini/` plus
`testdata/mixed-folder-images-mini.source.json`, and extended
`tests/test_mixed_folder_recipe.py` with fixture-shape and mixed-folder smoke
coverage that asserts shared `group_id` / `group_key` / `group_role` /
`group_size`, source-native `launch_input_path`, shared
`downstream_run_id` / `first_downstream_artifact`, the blocked `.txt` row, and
the ordered child `page_image_v1` manifest. Fresh checks in this pass:
`python -m ruff check modules/intake/archive_route_members_v1/main.py tests/test_mixed_folder_recipe.py`,
`python -m pytest -q tests/test_mixed_folder_recipe.py tests/test_mixed_archive_zip_recipe.py tests/test_image_directory_intake_recipe.py`,
and a fresh real driver proof after clearing stale bytecode with
`find modules -name '*.pyc' -delete` then
`python driver.py --recipe configs/recipes/recipe-mixed-folder-routing-mvp.yaml --input-folder testdata/mixed-folder-images-mini --run-id story224-folder-impl-r2 --allow-run-id-reuse --output-dir output/runs --force`.
Manual artifact inspection on
`output/runs/story224-folder-impl-r2/01_folder_members_manifest_v1/archive_members_manifest.jsonl`,
`output/runs/story224-folder-impl-r2/02_archive_route_members_v1/archive_member_routes.jsonl`,
and
`output/runs/story224-folder-impl-r2-member-002-grouped-recipe-images-ocr-html-mvp/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl`
confirmed one blocked `notes/readme.txt` row, two grouped `pages/page-00N.png`
rows sharing `group_id = images-dir:pages`, a source-native
`launch_input_path` pointing at `testdata/mixed-folder-images-mini/pages`, and
an ordered child manifest that points back to the checked-in source-native
images. This closes the bounded direct-folder grouped-image parity slice on the
same route/module and first-artifact line. Next step: rerun methodology plus
full repo checks, then hand off to `/validate 224` without marking the story
Done.

20260417-1626 — build-story verify: reran the truth-surface and repo-level
checks after the implementation patch and left the story in the correct
handoff state. Fresh evidence in this pass: `make methodology-compile` rewrote
`docs/methodology/graph.json` and `docs/stories.md`; `make methodology-check`
confirmed the graph is current; `make lint` passed; and `make test` passed
fresh at `598 passed, 4 warnings` in `681.32s`. Result: Story 224 now has
`Build complete` checked while `Validation complete` and `Story marked done`
stay intentionally unchecked for the next `/validate 224` pass. Practical
impact: operators can now hand a mixed source-native folder containing one
shared-parent page-image set plus unrelated blocked members to the maintained
mixed-folder recipe and get the same inspectable grouped route bridge and first
downstream `page_image_v1` artifact that previously existed only on the ZIP
probe. Residual limit: the grouped claim still stops at `images_to_manifest`
for this bounded fixture and does not widen later OCR/HTML or broader archive
ownership semantics. Next step: `/validate 224` should re-check the bounded
claim, artifact quality, and truth-surface alignment without marking the story
done prematurely.

20260417-1540 — mark-story-done close-out: validated Story 224 complete and
set the story status to `Done`. Fresh evidence in this pass:
`python -m pytest tests/` passed at `598 passed, 4 warnings` in `657.21s`;
`python -m ruff check modules/ tests/` passed; `make skills-check` passed for
the adjacent agent-guidance edits in the intended landing set; and a fresh real
proof run —
`python driver.py --recipe configs/recipes/recipe-mixed-folder-routing-mvp.yaml --input-folder testdata/mixed-folder-images-mini --run-id story224-folder-close-r3 --allow-run-id-reuse --output-dir output/runs --force`
— emitted
`output/runs/story224-folder-close-r3/01_folder_members_manifest_v1/archive_members_manifest.jsonl`,
`output/runs/story224-folder-close-r3/02_archive_route_members_v1/archive_member_routes.jsonl`,
and
`output/runs/story224-folder-close-r3-member-002-grouped-recipe-images-ocr-html-mvp/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl`.
`validate_artifact.py` passed on the parent manifest, parent routes, and child
`page_image_v1` manifest, and manual inspection confirmed one blocked
`notes/readme.txt` row plus two grouped source-native page-image rows whose
shared `launch_input_path` points at
`testdata/mixed-folder-images-mini/pages` and whose child manifest preserves
ordered `page-001.png` then `page-002.png`. Updated the existing Story 224
changelog entry instead of duplicating it. ADR-002 remains `ACCEPTED` with no
Remaining Work item newly resolved by this close-out. Next step:
`/check-in-diff`.
