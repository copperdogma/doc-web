---
title: "Expand the First Honest Grouped Image-Member Routing Seam to Direct-Folder Parity"
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

# Story 224 — Expand the First Honest Grouped Image-Member Routing Seam to Direct-Folder Parity

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/stories/story-180-widen-approved-intake-handoff-image-directory-proof.md`, `docs/stories/story-205-mixed-archive-intake-routing-seam.md`, `docs/stories/story-218-mixed-folder-direct-entry-seam.md`, `docs/stories/story-223-mixed-archive-pdf-member-approved-handoff-seam.md`, `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, `testdata/README.md`, `schemas.py`, `modules/intake/archive_unpack_manifest_v1/main.py`, `modules/intake/folder_members_manifest_v1/main.py`, `modules/intake/archive_route_members_v1/main.py`, `modules/intake/intake_plan_utils.py`, `modules/extract/images_dir_to_manifest_v1/main.py`, `tests/test_mixed_archive_zip_recipe.py`, `tests/test_mixed_folder_recipe.py`, `tests/test_image_directory_intake_recipe.py`, and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower mixed-archive grouped-image ADR or runbook`
**Depends On**: Stories `180`, `205`, and `218`

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

Story 224 already closed the first honest ZIP-only grouped image-member first-
artifact slice on the mixed-archive route/module seam. The remaining same-line
delta is direct-folder parity: the repo now has the grouped route-row
provenance contract, the bounded ZIP probe, and the maintained downstream
`images_dir` first-artifact proof, but the current direct-folder route still
stops short because grouped-image candidate detection only considers
`archive_format == "zip"`. Under the tightened anti-fragmentation rule, this
next slice belongs here instead of a new story because it stays on the same
`archive_route_members_v1` owner, same `mixed-archive` coverage row, same
fixture family, same grouped route contract, and same first downstream
`page_image_v1` validation boundary. This reopened story should widen the
grouped image-member proof to one bounded repo-owned source-native folder probe
while keeping later OCR/HTML continuation, broad folder-of-images semantics,
handwritten/scanned quality claims, and broader heterogeneous archive ownership
out of scope.

## Acceptance Criteria

- [x] This reopened story preserves the completed ZIP-only grouped image-member
      first-artifact proof and records why the remaining direct-folder parity
      delta belongs here instead of a new story:
  - [x] the work log cites that the direct-folder continuation stays on the
        same `archive_route_members_v1` owner, same `mixed-archive` coverage
        row, same grouped route-row provenance contract, same first downstream
        `page_image_v1` artifact boundary, and same operator-facing outcome as
        the completed ZIP slice
  - [x] the ZIP-only grouped-image proof remains recorded as completed evidence
        rather than being silently widened or discarded
- [x] A fresh current-pass baseline names the exact direct-folder grouped image-
      member gap from repo evidence:
  - [x] the work log records that
        `tests/fixtures/formats/_coverage-matrix.json`,
        `docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`, and
        `testdata/README.md` still exclude direct-folder grouped image-member
        parity before this reopened implementation pass
  - [x] the work log records that
        `modules/intake/archive_route_members_v1/main.py` still hard-limits
        `_grouped_image_candidates(...)` to `archive_format == "zip"` even
        though source-native folder members already flow through the same route
        module
  - [x] the work log cites the reusable substrate honestly:
        `folder_members_manifest_v1` already emits normalized source-native
        `member_path` / `extracted_path` rows for folder entry,
        `archive_route_members_v1` plus `schemas.py` already preserve
        `group_id`, `group_key`, `group_role`, `group_size`,
        `launch_input_path`, `downstream_run_id`, and
        `first_downstream_artifact` on the grouped ZIP slice,
        `MAINTAINED_RECIPES["images_dir"]` and `DRIVER_INPUT_FLAGS["images_dir"]`
        already support the downstream launch, and
        `images_dir_to_manifest_v1` already emits the expected first downstream
        `page_image_v1` artifact
- [x] The story lands one bounded direct-folder grouped image-member slice
      honestly:
  - [x] one repo-owned direct-folder probe exists under `testdata/` with at
        least two ordered page-image members under one shared parent directory,
        plus source or generation notes in `testdata/README.md`
  - [x] the chosen slice groups those image members into one inspectable
        `images_dir` launch candidate on the maintained mixed-folder recipe
        instead of launching one run per file or blocking each file separately
  - [x] the emitted route evidence preserves the same grouped ownership
        inspectably on folder entry via shared `group_id`, `group_key`,
        `group_role`, `group_size`, `launch_input_path`, `downstream_run_id`,
        and `first_downstream_artifact` fields
  - [x] if the probe includes non-image members, they remain explicit separate
        route rows or blocked outcomes rather than being silently folded into
        the image group
  - [x] a fresh `driver.py` run on the folder recipe produces and records the
        first downstream stamped artifact for the grouped launch under
        `output/runs/`, and that artifact is manually inspected
- [x] Direct-folder grouped image-member provenance stays source-honest on the
      claimed slice:
  - [x] source-native folder member paths, source-native launch directory,
        stable image order, downstream run id, and first downstream artifact
        remain inspectable end to end
  - [x] the grouping policy stays deterministic and explicit on the bounded
        slice (for example shared parent directory plus supported page-image
        suffixes) rather than a hidden second AI routing pass
  - [x] no claim is introduced for broad folder-of-images ownership, later
        OCR/HTML continuation, scanned or handwritten quality improvement,
        nested archives, attachment extraction, or broad heterogeneous archive
        ownership
- [x] Coverage, docs, and eval truth surfaces remain aligned with the reopened
      combined outcome:
  - [x] the ZIP-only grouped-image first-artifact proof remains documented as
        completed evidence
  - [x] `tests/fixtures/formats/_coverage-matrix.json`,
        `docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`, and
        `testdata/README.md` widen only as far as the fresh direct-folder proof
        justifies
  - [x] `approved-intake-handoff` and `auto-book-type-detection` remain
        unchanged unless fresh current-pass evidence proves this grouped folder-
        entry slice belongs in one of those top-level automation surfaces

## Out of Scope

- Broad “any folder of images inside any archive or source-native folder”
  ownership beyond one bounded repo-owned grouped probe
- Arbitrary photo-album clustering, duplicate-image collapse, cover/back-matter
  detection, or other broad image-set semantics
- Grouped-image continuation beyond the first downstream `page_image_v1`
  artifact
- Scanned or handwritten OCR quality improvements beyond the existing
  `image-directory-scans` and `handwritten-notes` proof lines
- PDF-member launch changes, nested archives, attachments, `.msg`, mailbox
  cleanup, or connector workflows
- Reopening Story 191 or changing the handwritten OCR blocker line
- New `doc-web` output-contract architecture beyond the minimum inspectable
  grouped-member provenance and first downstream artifact needed to prove the
  bounded slice

## Approach Evaluation

- **Simplification baseline**: first prove the remaining direct-folder gap is
  only the route bridge, not missing folder substrate or downstream image-dir
  support. A one-file-per-run fallback is still not honest for this line
  because `recipe-images-ocr-html-mvp.yaml` is the maintained multi-page
  directory lane, not a single-image direct-entry recipe.
- **AI-only**: weak first move. Grouping one bounded page-image set by shared
  parent path, supported suffix, and stable filename order is still a
  deterministic orchestration problem. The AI work already lives downstream in
  the maintained `images_dir` OCR lane.
- **Hybrid**: keep only as a fallback. If the chosen folder probe reveals real
  ambiguity that the current shared-parent grouping rule cannot express
  honestly, add the smallest possible bounded AI judgment with explicit
  provenance instead of widening semantics silently.
- **Pure code**: current front-runner. The verified remaining seam is widening
  the existing grouped route bridge from ZIP-only to source-native folder
  parity, not adding new image understanding.
- **Repo constraints / prior decisions**: `spec:1.1` keeps recipe ownership
  explicit under `C2`; ADR-002 keeps the accepted `doc-web` boundary
  inspectable; Story 180 already proved a repo-owned bounded `images_dir`
  launch into `recipe-images-ocr-html-mvp.yaml`; Story 218 proved the folder
  member-manifest substrate on the same mixed-input line; and Story 224's
  completed ZIP slice already established the grouped route-row contract.
- **Existing patterns to reuse**: `modules/intake/folder_members_manifest_v1`,
  `modules/intake/archive_route_members_v1`,
  `modules/intake/intake_plan_utils.py`,
  `modules/extract/images_dir_to_manifest_v1/main.py`,
  `tests/test_mixed_archive_zip_recipe.py`,
  `tests/test_mixed_folder_recipe.py`,
  `tests/test_image_directory_intake_recipe.py`, and the checked-in
  `testdata/handwritten-notes-mini-images` directory already used by Story 180.
- **Eval**: the deciding proof surface is a fresh `driver.py` run on one
  repo-owned direct-folder probe plus manual inspection of the grouped route
  evidence and the first downstream
  `01_images_dir_to_manifest_v1/pages_images_manifest.jsonl` artifact. If the
  grouped folder slice changes top-level automation truth, rerun the owning
  eval surface and update `docs/evals/registry.yaml`; otherwise keep the work
  on the explicit mixed-folder recipe line.

## Tasks

- [x] Close and preserve the ZIP-only grouped image-member first-artifact slice
      as completed evidence
- [x] Freeze the current direct-folder grouped image-member gap from repo
      reality:
  - [x] verify the `mixed-archive` coverage row and current methodology/docs
        wording still exclude direct-folder grouped image-member parity
  - [x] verify that source-native folder image members still stay ungrouped on
        the current mixed-folder line because grouped candidate detection is
        ZIP-only
  - [x] verify the reusable substrate honestly: current grouped route-row
        fields, existing folder manifest contract, existing `images_dir`
        maintained recipe/flag, and the current first downstream
        `page_image_v1` artifact contract
- [x] Choose one bounded repo-owned direct-folder grouped-image probe and
      grouping policy:
  - [x] default to a folder built from the checked-in
        `testdata/handwritten-notes-mini-images` pages under one shared parent
        directory unless a smaller repo-owned case is discovered
  - [x] decide whether one non-image member belongs in the probe to prove that
        non-image behavior remains unchanged
  - [x] document why the chosen probe is the smallest honest slice
- [x] Measure the smallest honest baseline before changing folder grouping
      logic:
  - [x] current `archive_route_members_v1` behavior on the chosen direct-folder
        grouped-image probe
  - [x] direct `--input-images` launch on the source-native group directory if
        that is needed to prove the downstream reuse path explicitly
  - [x] do not introduce a new archive-specific prompt until deterministic
        grouping is shown insufficient
- [x] Widen the grouped-image implementation from ZIP-only to direct-folder
      parity:
  - [x] keep the existing ZIP grouped contract unchanged
  - [x] add the minimum route/helper changes needed so folder entry reuses the
        same grouped provenance fields and the same maintained `images_dir`
        launch path
  - [x] keep source-native launch paths inspectable instead of silently copying
        the folder probe into a second staging tree
- [x] Add focused fixture-backed coverage for the direct-folder grouped image-
      member seam, including grouped provenance expectations and first
      downstream artifact checks
- [x] If this story changes documented format coverage or graduation reality:
      update `tests/fixtures/formats/_coverage-matrix.json` and any relevant
      methodology state honestly
- [x] Check whether the chosen implementation makes any existing code, helper
      paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for the reopened scope:
  - [x] Targeted regression checks:
        `pytest -q tests/test_mixed_folder_recipe.py tests/test_mixed_archive_zip_recipe.py tests/test_image_directory_intake_recipe.py`
  - [x] Default Python lint: `make lint`
  - [x] Default Python checks: `make test`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through
        `driver.py` on the folder recipe, verify artifacts in `output/runs/`,
        and manually inspect grouped route evidence plus sample downstream JSON
        or JSONL data
  - [x] If methodology truth surfaces changed: `make methodology-compile` and
        `make methodology-check`
  - [x] If agent tooling changed: `make skills-check` not needed unless the
        reopened work touches skill files
- [x] Evals or goldens stay unchanged unless the reopened truth surface proves
      otherwise; `docs/evals/registry.yaml` should remain untouched by default
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: the direct-folder grouped image-member claim traces
        to source-native member paths, grouping evidence, launch metadata, and
        inspected downstream artifacts
  - [x] T1 — AI-First: do not write grouping logic AI can already solve better,
        but do not add a new AI pass when deterministic routing is sufficient
  - [x] T2 — Eval Before Build: freeze the current direct-folder blocked
        behavior and deterministic grouping baseline before adding new glue
  - [x] T3 — Fidelity: preserve image order and membership faithfully without
        silently dropping or merging unrelated files
  - [x] T4 — Modular: reuse the maintained mixed-folder route plus existing
        `images_dir` recipe instead of inventing a second folder-image stack
  - [x] T5 — Inspect Artifacts: manually open the grouped route evidence and
        the first downstream `page_image_v1` artifact, not just the logs

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
  line. The likely owner remains `archive_route_members_v1` plus a small helper
  in `intake_plan_utils.py` only if the current grouped-image predicates need a
  shared adjustment. This is not a new `doc-web` boundary or a second
  archive/folder routing stack.
- **Methodology reality**: this reopened work still belongs primarily to
  `spec:1`, with supporting ties to `spec:6`, `spec:7`, `spec:8`, and
  `spec:9`. In the current repo state, `spec:1` substrate exists and `C2` /
  `B10` remain `climb`; the `mixed-archive` coverage row is already `passing`
  on five checked-in bounded probes across three behavior classes, but it still
  explicitly lists direct-folder grouped image-member parity as the next gap.
  Status is `Pending`, not `Draft`, because the grouped route contract,
  downstream recipe, and source-native folder manifest substrate already exist
  in code; the missing piece is one bounded widening of that same contract.
- **Substrate evidence**: verified in this pass that
  `modules/intake/folder_members_manifest_v1/main.py` already emits the same
  normalized member-path contract for source-native folder trees;
  `modules/intake/archive_route_members_v1/main.py` already owns the grouped
  route-row contract and only blocks folder parity because
  `_grouped_image_candidates(...)` skips non-ZIP rows; `modules/intake/intake_plan_utils.py`
  already defines the shared grouped-image predicates plus
  `MAINTAINED_RECIPES["images_dir"]` and `DRIVER_INPUT_FLAGS["images_dir"]`;
  `modules/extract/images_dir_to_manifest_v1/main.py` already accepts a
  directory and emits the first downstream `page_image_v1` manifest; and
  `tests/test_mixed_archive_zip_recipe.py` plus
  `tests/test_image_directory_intake_recipe.py` already prove the adjacent ZIP
  grouped-image and direct-entry image-directory seams. The main missing
  regression surface is folder-specific grouped-image coverage in
  `tests/test_mixed_folder_recipe.py`.
- **Data contracts / schemas**: `archive_member_route_v1` already carries the
  grouped-image provenance fields (`group_id`, `group_key`, `group_role`,
  `group_size`, `launch_input_path`, `downstream_run_id`, and
  `first_downstream_artifact`) that this reopened slice wants to reuse. No new
  schema work is expected unless the folder probe reveals a real provenance gap
  the current route rows cannot express honestly.
- **File sizes**: likely touch points are
  `modules/intake/archive_route_members_v1/main.py` (`450` lines),
  `modules/intake/intake_plan_utils.py` (`470` lines) only if shared helper
  behavior changes,
  `tests/test_mixed_folder_recipe.py` (`156` lines),
  `tests/test_mixed_archive_zip_recipe.py` (`850` lines) only if a shared
  grouped helper or guardrail must move,
  `README.md` (`538`, >500),
  `docs/RUNBOOK.md` (`979`, >500),
  `tests/fixtures/formats/_coverage-matrix.json` (`582`, >500),
  and `testdata/README.md` (`174`). Keep edits especially surgical in the
  oversized files.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`,
  `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002,
  Stories 180/205/218/223, `tests/fixtures/formats/_coverage-matrix.json`,
  `README.md`, `docs/RUNBOOK.md`, `testdata/README.md`, `schemas.py`,
  `modules/intake/folder_members_manifest_v1/main.py`,
  `modules/intake/archive_route_members_v1/main.py`,
  `modules/intake/intake_plan_utils.py`,
  `modules/extract/images_dir_to_manifest_v1/main.py`,
  `tests/test_mixed_archive_zip_recipe.py`,
  `tests/test_mixed_folder_recipe.py`, and
  `tests/test_image_directory_intake_recipe.py`. No narrower grouped-image
  mixed-archive ADR, runbook, scout note, or project note was found after
  search.

## Files to Modify

- `modules/intake/archive_route_members_v1/main.py` — widen grouped-image
  candidate detection from ZIP-only to the bounded direct-folder parity slice
  while preserving the existing grouped provenance contract (`450` lines)
- `modules/intake/intake_plan_utils.py` — only if the shared grouped-image
  predicates need a narrow helper adjustment rather than a route-local special
  case (`470` lines)
- `tests/test_mixed_folder_recipe.py` — add fixture-backed direct-folder
  grouped image-member routing coverage and first downstream artifact
  expectations (`156` lines)
- `tests/test_mixed_archive_zip_recipe.py` — touch only if the shared grouped
  helper or ZIP regression surface needs an explicit no-regression assertion
  (`850` lines)
- `tests/test_image_directory_intake_recipe.py` — extend only if the direct-
  folder grouped slice needs a shared ordering or first-artifact assertion
  (`276` lines)
- `testdata/mixed-folder-images-mini/` and
  `testdata/mixed-folder-images-mini.source.json` — repo-owned direct-folder
  grouped image-member probe and metadata (new files)
- `testdata/README.md` — record direct-folder grouped image-member probe
  provenance and generation notes (`174` lines)
- `tests/fixtures/formats/_coverage-matrix.json` — widen the `mixed-archive`
  row only as far as the shipped direct-folder parity slice justifies (`582`
  lines)
- `docs/methodology/state.yaml` — replace the current grouped-image gap wording
  only if the reopened story lands (truth-critical size)
- `README.md` — align supported mixed-archive wording with the exact bounded
  combined grouped-image slice if it lands (`538` lines)
- `docs/RUNBOOK.md` — add the verified direct-folder grouped image-member smoke
  command or blocker truth (`979` lines)
- `schemas.py` — only if the current grouped route-row fields prove
  insufficient for the source-native folder proof (`1375` lines)
- `modules/intake/folder_members_manifest_v1/main.py` — only if the chosen
  probe reveals a narrow source-native metadata hook is missing beyond current
  `member_path` and `extracted_path` (`121` lines)

## Redundancy / Removal Targets

- Doc wording that treats direct-folder grouped image-member routing as
  categorically out of scope after the bounded folder slice lands
- Duplicated ZIP-vs-folder grouped-image gating logic if one shared helper can
  own the candidate selection cleanly
- Any ad hoc scratch folder-probe generation notes once a repo-owned grouped-
  image folder probe is checked in under `testdata/`

## Notes

- Reopen justification: a new Story 225 would not be honest. The remaining
  direct-folder grouped-image delta stays on the same owning route module, same
  grouped route-row provenance contract, same `mixed-archive` coverage row,
  same fixture family, same downstream `images_dir` recipe, and same first
  downstream `page_image_v1` validation boundary as the completed ZIP slice.
- The existing completed ZIP slice remains the baseline evidence for grouped
  route-row fields and first-artifact validation. This reopened story widens
  only the entry surface from extracted ZIP members to source-native folder
  members.
- The default smallest candidate is `testdata/mixed-folder-images-mini/`,
  derived from `testdata/handwritten-notes-mini-images` under one shared
  `pages/` parent directory with one explicit blocked `notes/readme.txt`
  member, because Story 180 already proved that image directory as a bounded
  repo-owned `images_dir` launch surface and Story 218 already proved the
  source-native folder member-manifest seam on the same mixed-input line.
- Keep the grouping policy deterministic and inspectable by default. Prefer one
  shared parent directory plus supported image suffixes and stable filename
  order over any new AI route decision unless the baseline falsifies that
  simpler path.

## Plan

### Exploration Summary

- **Ideal alignment:** proceed. This reopened story closes a real `spec:1.1` /
  `C2` gap on the maintained mixed-archive line while reusing the existing
  grouped route-row contract and maintained `images_dir` direct-entry lane
  instead of adding a second folder-image runtime or a new AI route pass.
- **Relevant methodology state:** `docs/methodology/state.yaml` still records
  `spec:1`, `spec:6`, `spec:8`, and `spec:9` substrate as `exists`,
  `spec:7` as `partial`, and `C2` / `B10` as `climb`. The
  `maintained-intake-honesty` campaign and the `mixed-archive` coverage row now
  frame this line by behavior class, and both explicitly name direct-folder
  grouped image-member parity as the remaining bounded grouped-image gap.
- **Relevant coverage rows:** `image-directory-scans` is already `passing` on
  the maintained top-level `recipe-images-ocr-html-mvp.yaml` lane, while the
  `mixed-archive` row is already `passing` on five checked-in bounded probes
  across three behavior classes and still lists direct-folder grouped image-
  member parity as a known gap.
- **Decision docs consulted:** `docs/ideal.md`, `docs/spec.md`,
  `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002,
  Stories 180/205/218/223, the current `mixed-archive` and
  `image-directory-scans` coverage rows, `README.md`, `docs/RUNBOOK.md`,
  `testdata/README.md`, and the current mixed-folder / grouped-image runtime
  code and tests. No narrower mixed-archive grouped-image ADR, runbook, scout
  note, or project note was found.
- **Fresh current-pass code evidence:**
  - `folder_members_manifest_v1` already emits source-native member rows, so
    the folder entry surface is present.
  - `archive_route_members_v1` already owns the grouped route-row contract, but
    `_grouped_image_candidates(...)` still short-circuits on
    `archive_format != "zip"`.
  - `tests/test_mixed_folder_recipe.py` currently proves only the direct-entry
    and PDF-member folder slices; it has no grouped-image probe coverage.
  - `MAINTAINED_RECIPES["images_dir"]`,
    `DRIVER_INPUT_FLAGS["images_dir"]`, and
    `images_dir_to_manifest_v1` already prove the downstream launch target and
    first-artifact contract.
- **Fresh current-pass runtime baseline:**
  - Created a temporary source-native folder probe at
    `/tmp/story224-folder-baseline-src` with `pages/page-001.png`,
    `pages/page-002.png`, and `notes/readme.txt`, then ran
    `python driver.py --recipe configs/recipes/recipe-mixed-folder-routing-mvp.yaml --input-folder /tmp/story224-folder-baseline-src --run-id story224-folder-baseline-r1 --allow-run-id-reuse --output-dir output/runs --force`.
  - The stamped manifest at
    `output/runs/story224-folder-baseline-r1/01_folder_members_manifest_v1/archive_members_manifest.jsonl`
    proves source-native relative ordering and source-native `extracted_path`
    values for the bounded folder probe.
  - The stamped route artifact at
    `output/runs/story224-folder-baseline-r1/02_archive_route_members_v1/archive_member_routes.jsonl`
    isolates the exact current gap: `launched=0, blocked=3, skipped=0,
    failed=0`, with both page-image rows still stamped
    `terminal_reason = unsupported_archive_member_suffix:.png` and no grouped
    provenance fields populated.
  - A direct downstream reuse probe on the same source-native page directory —
    `python driver.py --recipe configs/recipes/recipe-images-ocr-html-mvp.yaml --input-images /tmp/story224-folder-baseline-src/pages --run-id story224-folder-images-direct-r1 --allow-run-id-reuse --output-dir output/runs --end-at images_to_manifest --force`
    — emitted
    `output/runs/story224-folder-images-direct-r1/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl`
    with ordered `page-001.png` then `page-002.png`, proving the remaining gap
    is the folder route bridge rather than downstream image-directory intake.
- **Patterns to follow:** Story 218's source-native folder proof discipline,
  Story 224's completed ZIP grouped-image route-row contract, and Story 180's
  first-downstream-artifact inspection discipline.
- **Surprises found:** no maintained recipe wiring change is obviously required
  for proof. `recipe-mixed-folder-routing-mvp.yaml` already accepts
  `--input-folder` overrides, so the reopened slice likely needs a new folder
  fixture and route/test/doc updates, not a new recipe default.
- **Files likely to change:** `modules/intake/archive_route_members_v1/main.py`,
  `tests/test_mixed_folder_recipe.py`, new grouped-image folder fixture files
  under `testdata/`, `testdata/README.md`,
  `tests/fixtures/formats/_coverage-matrix.json`, `docs/methodology/state.yaml`,
  `README.md`, and `docs/RUNBOOK.md`.
- **Files at risk:** `README.md` (`538`), `docs/RUNBOOK.md` (`979`),
  `tests/fixtures/formats/_coverage-matrix.json` (`582`), and
  `tests/test_mixed_archive_zip_recipe.py` (`850`) are the large files in
  scope; keep edits surgical. Existing grouped ZIP and PDF-member tests are the
  main no-regression surface.

### Eval-First Gate

- **Baseline result:** captured in this pass. The mixed-folder recipe on the
  temporary source-native probe wrote a stamped route artifact with both image
  members blocked as `unsupported_archive_member_suffix:.png`, while a direct
  `--input-images` run on the same `pages/` directory emitted the expected two-
  row `page_image_v1` manifest. The current direct-folder gap is therefore the
  grouped route bridge, not folder substrate or downstream image intake.
- **Approach comparison:**
  - **AI-only:** rejected by default. There is still no reasoning gap in repo
    evidence; the remaining issue is container-entry parity on an already
    deterministic grouping rule.
  - **Hybrid:** keep only as a fallback if the folder probe reveals ambiguity
    that the current shared-parent rule cannot express honestly.
  - **Pure code:** current winner. The missing work is widening the existing
    grouped route bridge to one source-native folder slice.
- **Recommended contract decision:** reuse the existing route-row grouped
  provenance fields rather than inventing a new sidecar artifact or schema.

### Recommended Implementation Plan

- **Recommended path:** ship one repo-owned direct-folder grouped-image probe
  using the existing mixed-folder route plus the maintained `images_dir`
  recipe. Relative effort: `S`.

1. Add one repo-owned direct-folder grouped-image probe (`XS`)
   - Files: new `testdata/mixed-folder-images-mini/` plus
     `testdata/mixed-folder-images-mini.source.json` and `testdata/README.md`.
   - Shape: start from `testdata/handwritten-notes-mini-images` under a shared
     `pages/` directory and optionally keep one explicit blocked
     `notes/readme.txt` member so non-image behavior remains visible.
   - Done when: the repo owns one checked-in grouped-image folder probe with
     explicit scope and regeneration notes.

2. Freeze the direct-folder baseline (`XS`)
   - Files: no planned code changes; produces proof under `output/runs/`.
   - Command target: a fresh `driver.py` run on the checked-in folder probe
     before implementation.
   - Artifact checks:
     - `output/runs/<run_id>/01_folder_members_manifest_v1/archive_members_manifest.jsonl`
     - `output/runs/<run_id>/02_archive_route_members_v1/archive_member_routes.jsonl`
   - Done when: the work log records the exact current folder failure mode and
     the source-native substrate that already exists.

3. Widen grouped-image candidate detection to direct-folder parity (`S`)
   - Files: `modules/intake/archive_route_members_v1/main.py` and
     `modules/intake/intake_plan_utils.py` only if the shared helper surface
     actually needs it.
   - Change: reuse the existing grouped-image predicates and route-row contract
     for `archive_format in {"zip", "folder"}` while preserving the existing
     ZIP behavior, deterministic `member_path` sorting, and source-native
     `launch_input_path` on the folder slice.
   - Non-goal: do not change the maintained mixed-folder recipe default input
     unless a later reason emerges; the proof run can override `--input-folder`
     the same way the current baseline already did.
   - Done when: one grouped folder directory launches `--input-images` once
     and every grouped member row carries the same inspectable group
     provenance as the ZIP proof.

4. Add focused regression coverage (`S`)
   - Files: `tests/test_mixed_folder_recipe.py`, plus
     `tests/test_mixed_archive_zip_recipe.py` only if a shared no-regression
     assertion belongs there.
   - Change: add a folder grouped-image routing contract test that asserts the
     image rows share one `group_id`, `group_key`, `group_size`, and downstream
     run while the optional non-image member stays explicitly blocked. Reuse the
     existing fake grouped-image child-run pattern from
     `tests/test_mixed_archive_zip_recipe.py` where practical instead of
     inventing a second fake-launch contract.
   - Done when: direct-folder grouped-image routing is fixture-backed and the
     existing ZIP grouped-image tests still pass unchanged.

5. Run narrow real validation and inspect artifacts (`S`)
   - Files: no planned code changes; produces proof under `output/runs/`.
   - Command target: a fresh `driver.py` run on the checked-in grouped-image
     folder probe after implementation.
   - Artifact checks:
     - `output/runs/<run_id>/01_folder_members_manifest_v1/archive_members_manifest.jsonl`
     - `output/runs/<run_id>/02_archive_route_members_v1/archive_member_routes.jsonl`
     - `output/runs/<group_run_id>/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl`
   - Done when: the route rows show one bounded grouped-folder launch and the
     downstream first artifact contains the expected ordered page images from
     the source-native directory.

6. Update truth surfaces narrowly (`XS`)
   - Files: `tests/fixtures/formats/_coverage-matrix.json`,
     `docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`,
     `testdata/README.md`, and this story file.
   - Change: widen only the `mixed-archive` bounded support claim to include
     the checked-in grouped-image direct-folder probe. Keep later OCR/HTML
     continuation, broad folder-of-images ownership, OCR-quality claims, and
     top-level automation surfaces unchanged unless fresh evidence moves them
     too.
   - Done when: docs say exactly one bounded grouped-image ZIP slice and one
     bounded grouped-image direct-folder slice, and no more.

### Impact Analysis

- **Primary blast radius:** `archive_route_members_v1` grouped candidate
  selection on the mixed-folder entry surface.
- **Secondary blast radius:** mixed-folder route tests and user-facing support
  wording in the coverage matrix, methodology state, README, RUNBOOK, and
  `testdata/README.md`.
- **What could break:** existing ZIP grouped-image tests if the widened helper
  regresses the current grouped contract; existing mixed-folder direct-entry or
  PDF-member tests if folder image grouping intercepts the wrong members; route
  provenance if the folder slice stops being source-native.
- **Redundancy plan:** remove wording that treats direct-folder grouped-image
  routing as categorically out of scope once the bounded folder proof exists.
- **Human-approval blockers:** none for packaging. Implementation still needs
  the usual `/build-story` approval before code changes.

## Work Log

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
