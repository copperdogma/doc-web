---
title: "Establish the First Honest Mixed-Archive Grouped Image-Member Routing Seam"
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

# Story 224 — Establish the First Honest Mixed-Archive Grouped Image-Member Routing Seam

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/stories/story-180-widen-approved-intake-handoff-image-directory-proof.md`, `docs/stories/story-205-mixed-archive-intake-routing-seam.md`, `docs/stories/story-218-mixed-folder-direct-entry-seam.md`, `docs/stories/story-221-mixed-archive-pdf-member-routing-seam.md`, `docs/stories/story-223-mixed-archive-pdf-member-approved-handoff-seam.md`, `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, `testdata/README.md`, `schemas.py`, `modules/intake/archive_unpack_manifest_v1/main.py`, `modules/intake/archive_route_members_v1/main.py`, `modules/intake/intake_plan_utils.py`, `modules/extract/images_dir_to_manifest_v1/main.py`, `tests/test_mixed_archive_zip_recipe.py`, `tests/test_image_directory_intake_recipe.py`, and `None found after search in docs/decisions/`, `docs/runbooks/`, `docs/scout/`, and `docs/notes/` for a narrower mixed-archive grouped-image ADR or runbook`
**Depends On**: Stories `180` and `205`

> If this story is `Blocked`, replace `N/A` in `Blocker Summary`, `Blocker
> Evidence`, and `Unblock Condition` with repo-backed truth, and make the
> visible `## Plan` describe the unblock path or blocker reassessment work
> instead of stale "proceed now" steps. Leave those sections as `N/A`
> otherwise.

## Goal

Stories 205, 218, 221, and 223 now prove the bounded mixed-archive route/module
line for direct-entry members plus one born-digital PDF-member continuation, but
the current truth surfaces still explicitly exclude grouped image-member
routing. The repo already owns a maintained top-level `images_dir` lane and a
checked-in bounded image-directory proof from Story 180, yet the mixed-archive
substrate still inventories one file per member and only knows how to launch
direct-entry families or the PDF special case. This story should close the next
honest gap on that same line: one repo-owned ZIP probe whose ordered page-image
members are grouped into a single `images_dir` launch candidate with explicit
archive-relative provenance, while direct-folder parity, broad photo-album
semantics, OCR-quality claims, and broader heterogeneous archive ownership stay
out of scope.

## Acceptance Criteria

- [x] A fresh current-pass baseline names the exact grouped image-member gap
      from repo evidence:
  - [x] the work log records that
        `tests/fixtures/formats/_coverage-matrix.json`,
        `docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`, and
        `testdata/README.md` still exclude grouped image-member routing at
        story start
  - [x] the work log records that
        `modules/intake/intake_plan_utils.py` currently maps archive member
        suffixes only for direct-entry families plus `pdf`, so `.png`, `.jpg`,
        `.jpeg`, `.tif`, `.tiff`, `.webp`, and `.bmp` members still stay
        unclassified on the mixed-archive line
  - [x] the work log records that
        `modules/intake/archive_route_members_v1/main.py` still special-cases
        only `pdf` members and otherwise routes through
        `archive_member_recipe_for_input_kind(...)`, which currently has no
        grouped `images_dir` path
  - [x] the work log cites the reusable substrate honestly:
        `archive_unpack_manifest_v1` preserves archive-relative subdirectories
        under `extracted_members/`, `MAINTAINED_RECIPES` and
        `DRIVER_INPUT_FLAGS` already support `images_dir`,
        `images_dir_to_manifest_v1` already emits the expected first downstream
        `page_image_v1` artifact, and `tests/test_image_directory_intake_recipe.py`
        already proves that bounded direct-entry first-artifact contract
- [x] The story lands one bounded ZIP-only grouped image-member slice honestly:
  - [x] one repo-owned ZIP probe exists under `testdata/` with at least two
        ordered page-image members under one shared archive-relative parent
        directory, plus source or generation notes in `testdata/README.md`
  - [x] the chosen slice groups those image members into one inspectable launch
        candidate for `configs/recipes/recipe-images-ocr-html-mvp.yaml`
        instead of launching one run per file or blocking each file separately
  - [x] the emitted route evidence keeps the grouped ownership inspectable via
        route fields or a sibling group artifact that names the grouped
        `member_id`s or `member_path`s, the grouping key or parent directory,
        the launch input path, and the downstream `run_id`
  - [x] if the probe includes non-image members, they remain explicit separate
        route rows or blocked outcomes rather than being silently folded into
        the image group
  - [x] a fresh `driver.py` run produces and records the first downstream
        stamped artifact for the grouped launch under `output/runs/`, and that
        artifact is manually inspected
- [x] Grouped image-member provenance stays source-honest on the claimed slice:
  - [x] archive-relative image member paths, extracted group directory, stable
        image order, downstream run id, and first downstream artifact remain
        inspectable end to end
  - [x] the grouping policy is deterministic and explicit on the bounded slice
        (for example shared parent directory plus supported page-image suffixes)
        rather than a hidden second AI routing pass
  - [x] no claim is introduced for direct-folder grouped-image parity, broad
        arbitrary photo albums, scanned or handwritten OCR quality improvement,
        nested archives, attachment extraction, or broad heterogeneous archive
        ownership
- [x] Coverage, docs, and eval truth surfaces remain aligned with the outcome:
  - [x] `tests/fixtures/formats/_coverage-matrix.json`,
        `docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`, and
        `testdata/README.md` widen only as far as the fresh grouped-image proof
        justifies
  - [x] `approved-intake-handoff` and `auto-book-type-detection` remain
        unchanged unless fresh current-pass evidence proves this grouped
        mixed-archive slice belongs in one of those top-level automation
        surfaces
  - [x] if new grouped route fields or sidecar contracts cross artifact
        boundaries, they are added to `schemas.py` before stamped artifacts
        rely on them

## Out of Scope

- Direct-folder grouped image-member parity unless it falls out with the same
  truth surface and no additional ambiguity
- Broad “any folder of images inside any archive” ownership beyond one bounded
  repo-owned grouped probe
- Arbitrary photo-album clustering, duplicate-image collapse, cover/back-matter
  detection, or other broad image-set semantics
- Scanned or handwritten OCR quality improvements beyond the existing
  `image-directory-scans` and `handwritten-notes` proof lines
- PDF-member launch changes, nested archives, attachments, `.msg`, mailbox
  cleanup, or connector workflows
- Reopening Story 191 or changing the handwritten OCR blocker line
- New `doc-web` output-contract architecture beyond the minimum inspectable
  grouped-member provenance and first downstream artifact needed to prove the
  bounded slice

## Approach Evaluation

- **Simplification baseline**: first measure whether the existing ZIP extract
  tree already preserves a shared parent directory that can be passed directly
  to `--input-images` with no new AI and only the smallest inspectable grouped
  route contract. A one-file-per-run fallback is not honest for the bounded
  slice because `recipe-images-ocr-html-mvp.yaml` is the maintained
  multi-page-directory lane, not a single-image direct-entry recipe.
- **AI-only**: weak first move. Grouping the first bounded image set by shared
  parent path, supported suffix, and stable filename order is a deterministic
  orchestration problem. The AI work already lives downstream in the existing
  `images_dir` OCR lane.
- **Hybrid**: keep only as a fallback. If the scratch probe shows that a purely
  deterministic grouping rule cannot distinguish a page-image set from
  unrelated images on the bounded candidate fixture, add the smallest possible
  bounded AI judgment with explicit provenance instead of widening semantics
  silently.
- **Pure code**: likely front-runner. The verified missing seam is the grouped
  route bridge between existing mixed-archive intake and the already-maintained
  `images_dir` launch path, not image understanding.
- **Repo constraints / prior decisions**: `spec:1.1` keeps recipe ownership
  explicit under `C2`; ADR-002 keeps the accepted `doc-web` boundary
  inspectable; Story 180 already proved a repo-owned bounded `images_dir`
  launch into `recipe-images-ocr-html-mvp.yaml`; and Stories 205 / 218 / 221 /
  223 explicitly kept grouped image-member routing out of scope while proving
  the adjacent mixed-archive seams.
- **Existing patterns to reuse**: `modules/intake/archive_unpack_manifest_v1`,
  `modules/intake/archive_route_members_v1`,
  `modules/intake/intake_plan_utils.py`,
  `modules/extract/images_dir_to_manifest_v1/main.py`,
  `tests/test_mixed_archive_zip_recipe.py`,
  `tests/test_image_directory_intake_recipe.py`, and the checked-in
  `testdata/handwritten-notes-mini-images` directory already used by Story 180.
- **Eval**: the deciding proof surface is a fresh `driver.py` run on one
  repo-owned ZIP probe plus manual inspection of the grouped route evidence and
  the first downstream
  `01_images_dir_to_manifest_v1/pages_images_manifest.jsonl` artifact. If the
  grouped slice changes top-level automation truth, rerun the owning eval
  surface and update `docs/evals/registry.yaml`; otherwise keep the work on the
  explicit mixed-archive recipe line.

## Tasks

- [x] Freeze the current grouped image-member gap from repo reality:
  - [x] verify the `mixed-archive` coverage row and current methodology/docs
        wording still exclude grouped image-member routing
  - [x] verify that image suffixes still remain unclassified or blocked on the
        current mixed-archive line
  - [x] verify the reusable substrate honestly: preserved ZIP subdirectories,
        existing `images_dir` maintained recipe/flag, and the current first
        downstream `page_image_v1` artifact contract
- [x] Choose one bounded repo-owned grouped-image probe and grouping policy:
  - [x] default to a ZIP-only probe built from the checked-in
        `testdata/handwritten-notes-mini-images` pages under one shared parent
        directory unless a smaller repo-owned case is discovered
  - [x] decide whether one non-image member belongs in the probe to prove that
        non-image behavior remains unchanged
  - [x] document why the chosen probe is the smallest honest slice
- [x] Measure the smallest honest baseline before adding new routing logic:
  - [x] current `archive_route_members_v1` behavior on the chosen grouped-image
        ZIP probe
  - [x] direct `--input-images` launch on the extracted group directory if that
        is needed to prove the downstream reuse path explicitly
  - [x] do not introduce a new archive-specific prompt until deterministic
        grouping is shown insufficient
- [x] Land the smallest coherent grouped-image implementation the baseline
      justifies:
  - [x] add the minimum helper, route, and schema changes needed to emit
        inspectable grouped provenance and launch the existing `images_dir`
        recipe
  - [x] preserve existing ZIP direct-entry and PDF-member behavior unchanged
  - [x] keep ZIP-only as the default shipping surface unless direct-folder
        parity falls out with the same truth surface and no added ambiguity
- [x] Add focused fixture-backed coverage for the grouped image-member seam,
      including grouped provenance expectations and first downstream artifact
      checks
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
        grouped route evidence plus sample downstream JSON or JSONL data
  - [x] If agent tooling changed: `make skills-check` not needed; agent tooling
        was unchanged in this story
- [x] Evals or goldens unchanged for this story; `docs/evals/registry.yaml`
      remains untouched
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: the grouped image-member claim traces to archive
        member paths, grouping evidence, launch metadata, and inspected
        downstream artifacts
  - [x] T1 — AI-First: do not write grouping logic AI can already solve better,
        but do not add a new AI pass when deterministic routing is sufficient
  - [x] T2 — Eval Before Build: freeze the current blocked behavior and
        deterministic grouping baseline before adding new glue
  - [x] T3 — Fidelity: preserve image order and membership faithfully without
        silently dropping or merging unrelated files
  - [x] T4 — Modular: reuse the maintained mixed-archive route plus existing
        `images_dir` recipe instead of inventing a second image-archive stack
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
  line. The likely owner is `archive_route_members_v1` plus a small helper in
  `intake_plan_utils.py` or a narrowly adjacent sibling helper, not a new
  `doc-web` runtime boundary or a second archive-routing stack.
- **Methodology reality**: this work belongs primarily to `spec:1`, with
  supporting ties to `spec:6`, `spec:7`, `spec:8`, and `spec:9`. In the current
  repo state, `spec:1` substrate exists and `C2` / `B10` remain `climb`; the
  `mixed-archive` coverage row at story start was already `passing` on four
  checked-in bounded probes but still explicitly listed grouped image-member
  routing as a known gap; and `image-directory-scans` was already `passing` on
  the maintained top-level direct-entry lane. This story began `Pending`
  because both prerequisite seams already existed in code; the missing piece
  was the bounded grouping contract that bridges them.
- **Substrate evidence**: verified in this pass that
  `modules/intake/archive_unpack_manifest_v1/main.py` preserves ZIP
  subdirectories and extracted member paths under `extracted_members/`;
  `modules/intake/folder_members_manifest_v1/main.py` emits the same normalized
  member-path contract for source-native folder trees; `modules/intake/intake_plan_utils.py`
  already defines `MAINTAINED_RECIPES["images_dir"]` and
  `DRIVER_INPUT_FLAGS["images_dir"]`; `modules/extract/images_dir_to_manifest_v1/main.py`
  already accepts a directory and emits the first downstream `page_image_v1`
  manifest; and `modules/intake/archive_route_members_v1/main.py` currently
  stops short of grouped-image routing because it only special-cases `pdf` and
  otherwise uses the direct-entry-only map. `tests/test_mixed_archive_zip_recipe.py`
  and `tests/test_image_directory_intake_recipe.py` already prove the adjacent
  bounded seams.
- **Data contracts / schemas**: `archive_member_manifest_v1` and
  `archive_member_route_v1` are currently one-row-per-member contracts and do
  not yet carry grouped-image provenance. `/build-story` should choose the
  smallest honest contract: either a minimal extension to
  `archive_member_route_v1` (for example group key and grouped member paths) or
  a sibling sidecar artifact plus a representative route row. Any new
  cross-artifact fields must land in `schemas.py` before stamped artifacts rely
  on them.
- **File sizes**: likely touch points are
  `modules/intake/archive_route_members_v1/main.py` (`371` lines),
  `modules/intake/intake_plan_utils.py` (`424`),
  `modules/intake/archive_unpack_manifest_v1/main.py` (`121`) only if a narrow
  grouping hook is needed,
  `schemas.py` (`1375`, >500),
  `tests/test_mixed_archive_zip_recipe.py` (`850`, >500),
  `tests/test_image_directory_intake_recipe.py` (`276`),
  `README.md` (`538`, >500),
  `docs/RUNBOOK.md` (`979`, >500),
  `tests/fixtures/formats/_coverage-matrix.json` (`582`, >500),
  and `testdata/README.md` (`174`). Keep edits especially surgical in the
  oversized files.
- **Decision context**: reviewed `docs/ideal.md`, `docs/spec.md`,
  `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002,
  Stories 180/205/218/221/223, `tests/fixtures/formats/_coverage-matrix.json`,
  `README.md`, `docs/RUNBOOK.md`, `testdata/README.md`, `schemas.py`,
  `modules/intake/archive_unpack_manifest_v1/main.py`,
  `modules/intake/archive_route_members_v1/main.py`,
  `modules/intake/intake_plan_utils.py`,
  `modules/extract/images_dir_to_manifest_v1/main.py`,
  `tests/test_mixed_archive_zip_recipe.py`, and
  `tests/test_image_directory_intake_recipe.py`. No narrower grouped-image
  mixed-archive ADR, runbook, scout note, or project note was found after
  search.

## Files to Modify

- `modules/intake/archive_route_members_v1/main.py` — add the bounded grouped
  image-member route path and emitted provenance for one `images_dir` launch
  candidate (`371` lines)
- `modules/intake/intake_plan_utils.py` — add bounded archive-image
  suffix or grouping helpers, or a clearly better shared successor (`424`
  lines)
- `schemas.py` — add grouped route or sidecar schema fields if the chosen
  contract crosses artifact boundaries (`1375` lines)
- `tests/test_mixed_archive_zip_recipe.py` — add fixture-backed grouped
  image-member routing coverage and first downstream artifact expectations
  (`850` lines)
- `tests/test_image_directory_intake_recipe.py` — extend only if the grouped
  slice needs a shared ordering or first-artifact assertion (`276` lines)
- `testdata/<new grouped-image probe>.zip` and
  `testdata/<new grouped-image probe>.source.json` — repo-owned grouped
  image-member ZIP fixture and metadata (new files)
- `testdata/README.md` — record grouped image-member probe provenance and
  generation notes (`174` lines)
- `tests/fixtures/formats/_coverage-matrix.json` — widen the `mixed-archive`
  row only as far as the shipped grouped-image slice justifies (`582` lines)
- `docs/methodology/state.yaml` — replace the current grouped-image gap wording
  only if the story lands (truth-critical size)
- `README.md` — align supported mixed-archive wording with the exact bounded
  grouped-image slice if it lands (`538` lines)
- `docs/RUNBOOK.md` — add the verified grouped image-member smoke command or
  blocker truth (`979` lines)
- `modules/intake/archive_unpack_manifest_v1/main.py` — only if the chosen
  grouped contract needs a narrow extraction-metadata hook beyond current
  `member_path` and `extracted_path` (`121` lines)

## Redundancy / Removal Targets

- Per-file image-member blocked reasoning on the chosen bounded probe if a
  grouped route row or sidecar cleanly supersedes it
- Doc wording that treats all mixed-archive image members as categorically out
  of scope after a bounded grouped-image slice lands
- Duplicated archive-image grouping logic split across route helpers when one
  shared helper can own it cleanly
- Any ad hoc scratch ZIP generation notes once a repo-owned grouped-image probe
  is checked in under `testdata/`

## Notes

- New story justification: reopening Story 223 would not be honest. Story 223
  closed a single-member PDF approved-handoff and launch continuation on the
  existing mixed-archive route/module seam. This follow-up changes the
  validation boundary from one member → one child run to multiple archive
  members → one grouped `images_dir` child run with explicit grouped
  provenance.
- The default smallest candidate is a ZIP built from
  `testdata/handwritten-notes-mini-images` under one shared parent directory,
  because Story 180 already proved that directory as a bounded repo-owned
  `images_dir` launch surface and the current ZIP extractor already preserves
  that directory shape.
- Keep the grouping policy deterministic and inspectable by default. Prefer one
  shared archive-relative parent directory plus supported image suffixes and
  stable filename order over any new AI route decision unless the baseline
  falsifies that simpler path.
- Keep direct-folder grouped-image parity explicitly deferred unless the exact
  same grouped contract and truth surface fall out without additional
  ambiguity.

## Plan

### Exploration Summary

- **Ideal alignment:** proceed. This story closes a real `spec:1.1` / `C2`
  gap on the maintained mixed-archive line while reusing the existing
  `images_dir` direct-entry lane instead of adding a second archive-image
  runtime or a new AI route pass.
- **Relevant methodology state:** `docs/methodology/state.yaml` still records
  `spec:1`, `spec:6`, `spec:8`, and `spec:9` substrate as `exists`,
  `spec:7` as `partial`, and `C2` / `B10` as `climb`. The
  `intake_and_routing` architecture-audit note explicitly names grouped
  image-member routing as still out of scope after Stories 205 / 218 / 221 /
  222 / 223.
- **Relevant coverage rows:** `image-directory-scans` is already `passing` on
  the maintained top-level `recipe-images-ocr-html-mvp.yaml` lane, while the
  `mixed-archive` row remains `passing` only on the four checked-in bounded
  direct-entry / PDF-member probes and still lists grouped image-member
  routing as a known gap.
- **Decision docs consulted:** `docs/ideal.md`, `docs/spec.md`,
  `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002,
  Stories 180 and 205, the current `mixed-archive` and `image-directory-scans`
  coverage rows, `README.md`, `docs/RUNBOOK.md`, `testdata/README.md`, and the
  current mixed-archive / image-directory runtime code and tests. No narrower
  mixed-archive grouped-image ADR, runbook, scout note, or project note was
  found.
- **Critical substrate verified in code:**
  - `archive_unpack_manifest_v1` already preserves ZIP member directories under
    `extracted_members/<member_path>`, so a shared-parent directory can be
    passed to `--input-images` without another unpack layer.
  - `archive_route_members_v1` currently blocks `.png` members because
    `archive_member_recipe_for_input_kind(...)` only maps direct-entry families
    and `pdf` is the only special case.
  - `MAINTAINED_RECIPES["images_dir"]`,
    `DRIVER_INPUT_FLAGS["images_dir"]`, and
    `images_dir_to_manifest_v1` already prove the downstream launch target and
    first-artifact contract.
- **Fresh baseline evidence:** the current mixed-archive line is blocked only
  at the route bridge, not at ZIP extraction or downstream image intake.
  - Scratch ZIP baseline run:
    `python driver.py --recipe configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml --input-zip /tmp/story224-grouped-images-baseline.zip --run-id story224-baseline-r1 --allow-run-id-reuse --output-dir output/runs --force`
    emitted
    `output/runs/story224-baseline-r1/01_archive_unpack_manifest_v1/archive_members_manifest.jsonl`
    and
    `output/runs/story224-baseline-r1/02_archive_route_members_v1/archive_member_routes.jsonl`
    with `launched=0, blocked=3, skipped=0, failed=0`.
  - Manual artifact inspection showed `pages/page-001.png`,
    `pages/page-002.png`, and `notes/readme.txt` were all preserved as ZIP
    members, but both `.png` rows still stamped
    `terminal_reason = unsupported_archive_member_suffix:.png`.
  - Direct downstream reuse probe:
    `python driver.py --recipe configs/recipes/recipe-images-ocr-html-mvp.yaml --input-images output/runs/story224-baseline-r1/01_archive_unpack_manifest_v1/extracted_members/pages --run-id story224-images-direct-r1 --output-dir output/runs --end-at images_to_manifest --allow-run-id-reuse --force`
    emitted
    `output/runs/story224-images-direct-r1/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl`
    with two `page_image_v1` rows sourced from the extracted directory.
- **Surprises found:** ZIP member order is not stable enough to trust for page
  order on this seam. The scratch ZIP manifest listed `page-002.png` before
  `page-001.png`, but `images_dir_to_manifest_v1` re-sorted the extracted
  directory back to `page-001`, `page-002`. The grouped route should therefore
  choose a deterministic primary row and rely on the existing directory sort in
  `images_dir_to_manifest_v1`, not on ZIP member order.
- **Patterns to follow:** Story 205's eval-first scratch-probe workflow,
  Story 180's first-downstream-artifact inspection discipline, and the current
  `archive_member_route_v1` per-member provenance shape.
- **Files likely to change:** `modules/intake/archive_route_members_v1/main.py`,
  `modules/intake/intake_plan_utils.py`, `schemas.py`,
  `tests/test_mixed_archive_zip_recipe.py`, new grouped-image fixture files
  under `testdata/`, `testdata/README.md`,
  `tests/fixtures/formats/_coverage-matrix.json`, `docs/methodology/state.yaml`,
  `README.md`, and `docs/RUNBOOK.md`.
- **Files at risk:** `schemas.py` (`1375`), `tests/test_mixed_archive_zip_recipe.py`
  (`850`), `README.md` (`538`), `docs/RUNBOOK.md` (`979`), and
  `tests/fixtures/formats/_coverage-matrix.json` (`582`) are the large files in
  scope; keep edits surgical. Existing mixed-archive PDF-member tests are the
  main runtime-regression surface.

### Eval-First Gate

- **Baseline result:** current code already proves that a shared extracted
  image directory is viable downstream and that the only missing seam is the
  grouped mixed-archive route bridge.
- **Approach comparison:**
  - **AI-only:** rejected. There is no reasoning gap yet; the bounded scratch
    probe shows a deterministic route is enough.
  - **Hybrid:** keep only as a fallback if a later probe reveals real ambiguity
    that shared-parent grouping cannot express honestly.
  - **Pure code:** current winner. The missing work is explicit grouped
    provenance plus a single `--input-images` launch bridge.
- **Recommended contract decision:** use route-row fields, not a new sibling
  sidecar, for the first bounded slice. Add optional grouped-image provenance
  fields to `archive_member_route_v1`:
  `group_id`, `group_key`, `group_role`, and `group_size`.
  Then emit one route row per grouped image member, with the shared
  `launch_input_path`, `downstream_run_id`, and `first_downstream_artifact`
  repeated across the group's rows. This keeps grouped ownership inspectable
  without introducing another artifact family.

### Recommended Implementation Plan

- **Recommended path:** ship one ZIP-only grouped-image probe using the
  existing mixed-archive route plus the maintained `images_dir` recipe.
  Relative effort: `S`.

1. Add one repo-owned grouped-image ZIP probe (`XS`)
   - Files: new `testdata/mixed-archive-images-mini.zip` and
     `testdata/mixed-archive-images-mini.source.json`, plus `testdata/README.md`.
   - Shape: start from `testdata/handwritten-notes-mini-images` under a shared
     `pages/` directory and keep one explicit blocked `notes/readme.txt`
     member so non-image behavior remains visible.
   - Done when: the repo owns one checked-in grouped-image ZIP probe with
     explicit scope and regeneration notes.

2. Add bounded grouped-image candidate detection and grouping (`S`)
   - Files: `modules/intake/intake_plan_utils.py`,
     `modules/intake/archive_route_members_v1/main.py`.
   - Change: add narrow archive-image helpers, detect grouped image members at
     route time, and group them by shared parent directory inside
     `archive_route_members_v1` while stamping `detected_input_kind =
     images_dir` on the emitted grouped route rows.
   - Contract: only group members that share the same archive-relative parent
     directory and supported image suffixes; choose the primary row by sorted
     `member_path`, not ZIP order; preserve existing direct-entry and PDF-member
     branches unchanged.
   - Done when: one grouped image directory launches `--input-images` once and
     every grouped member row carries the shared group provenance.

3. Extend the route schema for grouped provenance (`XS`)
   - Files: `schemas.py`.
   - Change: add optional `group_id`, `group_key`, `group_role`, and
     `group_size` to `ArchiveMemberRoute`.
   - Rationale: the grouped member list stays reconstructable from the route
     rows themselves, so a sidecar artifact is not needed for this first slice.
   - Done when: stamped route artifacts preserve the grouped-image fields.

4. Add focused regression coverage (`S`)
   - Files: `tests/test_mixed_archive_zip_recipe.py`.
   - Change: add a grouped-image routing contract test that writes two grouped
     image members plus one blocked `.txt` member, fakes the downstream
     `recipe-images-ocr-html-mvp.yaml` run, and asserts:
     - both image rows share one `group_id`
     - `group_key` matches the shared parent directory
     - `group_role` is deterministic (`primary` on sorted `page-001.png`)
     - both image rows carry `launch_input_flag = --input-images`,
       the shared extracted directory path, the shared downstream run id, and
       the same first downstream artifact
     - the `.txt` row remains explicitly blocked
   - Done when: grouped-image routing is fixture-backed and existing mixed-archive
     direct-entry / PDF-member tests still pass unchanged.

5. Run narrow real validation and inspect artifacts (`S`)
   - Files: no planned code changes; produces proof under `output/runs/`.
   - Command target: a fresh `driver.py` run on the checked-in grouped-image
     ZIP probe after implementation.
   - Artifact checks:
     - `output/runs/<run_id>/01_archive_unpack_manifest_v1/archive_members_manifest.jsonl`
     - `output/runs/<run_id>/02_archive_route_members_v1/archive_member_routes.jsonl`
     - `output/runs/<group_run_id>/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl`
   - Done when: the route rows show one bounded grouped-image launch and the
     downstream first artifact contains the expected ordered page images from
     the extracted directory.

6. Update truth surfaces narrowly (`XS`)
   - Files: `tests/fixtures/formats/_coverage-matrix.json`,
     `docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`,
     `testdata/README.md`, and this story file.
   - Change: widen only the `mixed-archive` bounded support claim to include
     the checked-in grouped-image ZIP probe. Keep direct-folder grouped-image
     parity, broad photo albums, OCR-quality claims, and top-level automation
     surfaces unchanged unless fresh evidence moves them too.
   - Done when: docs say exactly one bounded grouped-image mixed-archive slice
     exists and no more.

### Impact Analysis

- **Primary blast radius:** `archive_route_members_v1` route semantics and
  `archive_member_route_v1` schema.
- **Secondary blast radius:** mixed-archive route tests and user-facing support
  wording in the coverage matrix, methodology state, README, RUNBOOK, and
  `testdata/README.md`.
- **What could break:** existing mixed-archive ZIP / folder / PDF-member tests
  if image-suffix classification intercepts the wrong members; schema stamping
  if the new grouped fields are not added before artifacts are stamped; route
  determinism if implementation trusts ZIP order instead of stable sorted
  `member_path`.
- **Redundancy plan:** remove per-file blocked image-member wording on the new
  grouped probe once grouped route rows exist. Do not introduce a sidecar
  artifact unless the route-row contract proves insufficient during
  implementation.
- **Human-approval blockers:** none beyond the route-contract choice itself.
  Recommended choice: grouped provenance lives directly on
  `archive_member_route_v1` rows, not in a new sidecar artifact.

## Work Log

20260417-0021 — create-story bootstrap: created the Story 224 shell with `.agents/skills/create-story/scripts/start-story.sh mixed-archive-grouped-image-member-routing-seam High`; evidence: new `docs/stories/story-224-mixed-archive-grouped-image-member-routing-seam.md`; next step: replace the template with repo-backed grouped-image scope and verify whether a new story ID is honest.
20260417-0026 — create-story research: verified that `tests/fixtures/formats/_coverage-matrix.json`, `README.md`, `docs/RUNBOOK.md`, `testdata/README.md`, and `docs/methodology/state.yaml` still exclude grouped image-member routing, while `archive_unpack_manifest_v1` already preserves ZIP subdirectories and `intake_plan_utils.py` plus `images_dir_to_manifest_v1` already prove the downstream `images_dir` launch path; next step: finalize the pending story and regenerate generated methodology views.
20260417-0029 — create-story verify: ran `make methodology-compile` and confirmed Story 224 appears in `docs/stories.md` and `docs/methodology/graph.json`; evidence: generated index row and graph story entry both point at `docs/stories/story-224-mixed-archive-grouped-image-member-routing-seam.md`; next step: use `/build-story` to choose the exact grouped route contract and first repo-owned ZIP probe.
20260417-0036 — build-story explore: read `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, Stories 180 and 205, the `image-directory-scans` and `mixed-archive` coverage rows, and the current mixed-archive / image-directory runtime code and tests. Result: the story is honestly buildable now; the missing seam is the grouped route bridge, not ZIP extraction or downstream image intake. Fresh baseline evidence: `python driver.py --recipe configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml --input-zip /tmp/story224-grouped-images-baseline.zip --run-id story224-baseline-r1 --allow-run-id-reuse --output-dir output/runs --force` emitted a stamped mixed-archive manifest and route artifact with `launched=0, blocked=3, skipped=0, failed=0`, and manual inspection showed both `.png` members blocked as `unsupported_archive_member_suffix:.png` while the shared `pages/` directory was preserved under `output/runs/story224-baseline-r1/01_archive_unpack_manifest_v1/extracted_members/pages`. A direct downstream reuse probe on that extracted directory — `python driver.py --recipe configs/recipes/recipe-images-ocr-html-mvp.yaml --input-images output/runs/story224-baseline-r1/01_archive_unpack_manifest_v1/extracted_members/pages --run-id story224-images-direct-r1 --output-dir output/runs --end-at images_to_manifest --allow-run-id-reuse --force` — emitted `output/runs/story224-images-direct-r1/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl` with two ordered `page_image_v1` rows, proving the downstream path already works. Surprise: the ZIP manifest listed `page-002.png` before `page-001.png`, but `images_dir_to_manifest_v1` restored stable order, so implementation should rely on sorted `member_path` plus the existing directory sort rather than ZIP order. Files to change: `modules/intake/archive_route_members_v1/main.py`, `modules/intake/intake_plan_utils.py`, `schemas.py`, `tests/test_mixed_archive_zip_recipe.py`, new grouped-image fixture files, and the mixed-archive truth surfaces; next step: present the route-row grouped-provenance plan for approval before implementation.
20260417-0757 — build-story implement: shipped the bounded ZIP-only grouped image-member route-row contract. Added archive-image grouping helpers in `modules/intake/intake_plan_utils.py`; taught `modules/intake/archive_route_members_v1/main.py` to group supported shared-parent image members on ZIP entry, launch exactly one `--input-images` child run into `recipe-images-ocr-html-mvp.yaml`, and stamp `group_id`, `group_key`, `group_role`, `group_size`, shared `launch_input_path`, shared `downstream_run_id`, and shared `first_downstream_artifact` on each grouped member row while leaving direct-entry and PDF-member paths unchanged; and extended `schemas.py` so the stamped route artifact preserves those grouped fields. Added `testdata/mixed-archive-images-mini.source.json`, checked in `testdata/mixed-archive-images-mini.zip`, and expanded `tests/test_mixed_archive_zip_recipe.py` with grouped-image fixture and route assertions, including the non-stable ZIP-order case. Fresh implementation checks: `python -m ruff check modules/intake/archive_route_members_v1/main.py modules/intake/intake_plan_utils.py schemas.py tests/test_mixed_archive_zip_recipe.py`, `python -m pytest -q tests/test_mixed_archive_zip_recipe.py tests/test_mixed_folder_recipe.py tests/test_image_directory_intake_recipe.py`, `find modules -name '*.pyc' -delete`, `python driver.py --recipe configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml --input-zip testdata/mixed-archive-images-mini.zip --run-id story224-impl-r2 --allow-run-id-reuse --output-dir output/runs --force`, `python validate_artifact.py --schema archive_member_manifest_v1 --file output/runs/story224-impl-r2/01_archive_unpack_manifest_v1/archive_members_manifest.jsonl`, `python validate_artifact.py --schema archive_member_route_v1 --file output/runs/story224-impl-r2/02_archive_route_members_v1/archive_member_routes.jsonl`, and `python validate_artifact.py --schema page_image_v1 --file output/runs/story224-impl-r2-member-002-grouped-recipe-images-ocr-html-mvp/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl` all passed. Manual artifact inspection confirmed `pages/page-001.png` and `pages/page-002.png` now share `group_id = images-dir:pages`, `group_key = pages`, `group_size = 2`, `launch_input_flag = --input-images`, one grouped child `downstream_run_id`, and `terminal_reason = grouped_image_end_at:images_to_manifest` inside `output/runs/story224-impl-r2/02_archive_route_members_v1/archive_member_routes.jsonl`, while `notes/readme.txt` stays explicitly blocked as `.txt`; the child `output/runs/story224-impl-r2-member-002-grouped-recipe-images-ocr-html-mvp/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl` records ordered `page = 1` / `page = 2` rows with `image` paths ending in `page-001.png` then `page-002.png`. Small scope correction discovered during verification: the unbounded child image recipe fell over later at TOC synthesis on this checked-in two-page probe, so the shipped grouped route now stops at `images_to_manifest` by default and claims only the first downstream stamped `page_image_v1` artifact, not the full later OCR/HTML bundle line. Next step: keep Story 224 `In Progress`, leave the validation and done gates for `/validate` and `/mark-story-done`, and align the mixed-archive truth surfaces with this bounded shipped slice.
20260417-0918 — build-story verify: aligned the mixed-archive truth surfaces and re-ran the repo-level checks. Updated `tests/fixtures/formats/_coverage-matrix.json`, `docs/methodology/state.yaml`, `README.md`, `docs/RUNBOOK.md`, `testdata/README.md`, and the story checklists/workflow gates so the shipped claim now says the same bounded thing everywhere: one ZIP-only grouped image-member continuation to the first downstream `page_image_v1` artifact, with direct-folder parity and later OCR/HTML stages still out of scope. Fresh verification: `make methodology-compile` rewrote `docs/methodology/graph.json` and `docs/stories.md`; `make lint` passed; and `make test` passed as `596 passed, 4 warnings in 639.49s (0:10:39)`. The warning surface is unchanged and comes from the existing deprecated `dict()` call in `modules/portionize/portionize_headers_numeric_v1/main.py:96`, not from Story 224. Next step: use `/validate` for an explicit validation pass or accept the current build handoff and keep Story 224 open until that validation and `/mark-story-done` happen.
20260417-1052 — mark-story-done close-out: revalidated Story 224 on the current branch tip and closed it. Fresh evidence this pass: `git status --short`, `git diff --stat`, the full `git diff`, and `git ls-files --others --exclude-standard`; `make lint`; `make test` (`596 passed, 4 warnings in 687.06s (0:11:27)`, with unchanged existing warnings from `modules/portionize/portionize_headers_numeric_v1/main.py:96`); `find modules -name '*.pyc' -delete`; `python driver.py --recipe configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml --input-zip testdata/mixed-archive-images-mini.zip --run-id story224-validate-r1 --allow-run-id-reuse --output-dir output/runs --force`; `python validate_artifact.py --schema archive_member_manifest_v1 --file output/runs/story224-validate-r1/01_archive_unpack_manifest_v1/archive_members_manifest.jsonl`; `python validate_artifact.py --schema archive_member_route_v1 --file output/runs/story224-validate-r1/02_archive_route_members_v1/archive_member_routes.jsonl`; and `python validate_artifact.py --schema page_image_v1 --file output/runs/story224-validate-r1-member-002-grouped-recipe-images-ocr-html-mvp/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl`. Manual artifact inspection confirmed `pages/page-001.png` and `pages/page-002.png` launch as one grouped `images_dir` child run with shared `group_id = images-dir:pages`, shared `downstream_run_id`, and `terminal_reason = grouped_image_end_at:images_to_manifest`, while `notes/readme.txt` remains explicitly blocked; the child `pages_images_manifest.jsonl` still records `page-001.png` then `page-002.png` in order. Result: all acceptance criteria and tasks remain met, validation is complete, and Story 224 now closes as the bounded ZIP-only grouped image-member first-artifact seam. Next step: `/check-in-diff`.
