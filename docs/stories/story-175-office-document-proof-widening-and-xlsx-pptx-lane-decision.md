# Story 175 — Widen Office Document Proof and Decide XLSX/PPTX Lane Strategy

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #1 (Ingest), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Any format, any condition, Dossier-ready output, Traceability is the product
**Spec Refs**: spec:1 (spec:1.1, C2), spec:3 (spec:3.1, C3), spec:6, spec:7, spec:8 (B1)
**Build Map Refs**: Category 1 Intake & Format Routing (`exists`, C2 `climb`); Category 6 Validation, Provenance & Export (`exists`); Category 7 Graduation & Dossier Handoff (`partial`); Category 8 AI Harnesses & Tooling (`exists`, B1 `hold`); Input Coverage rows `docx` (`passing`), `xlsx` (`has fixture`), `pptx` (`has fixture`); Gap 3 — Office-document widening beyond the first DOCX slice; Gap 5 — Fixture breadth and graduation confidence
**Decision Refs**: `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/build-map.md`, `docs/requirements.md`, `docs/stories/story-172-maintained-docx-intake-lane.md`, `docs/stories/story-174-docx-runtime-surface-and-contract-compatibility-signaling.md`, `docs/scout/scout-011-external-document-ingestion-systems.md`, `testdata/README.md`, `None found after search in docs/decisions/ for office-family-specific ADRs`
**Depends On**: Story 172, Story 174

## Goal

Close the current office-document gap with one coherent chunk instead of another chain of narrow follow-ups. This story should widen DOCX from a single narrow proof fixture toward honest family-level confidence, baseline the real local XLSX and PPTX seams on repo-owned or reproducible fixtures, and either absorb the first tractable non-DOCX office lane into the same implementation pass or leave one explicit split/stay-together decision with updated truth surfaces. The point is to reduce ambiguity and backlog residue, not to claim full office-suite support prematurely.

## Acceptance Criteria

- [x] DOCX proof widens beyond the current single fixture in a way that can change the family-level truth surface:
  - [x] at least two additional repo-owned or reproducibly generated DOCX fixtures exist, for a total of at least three diverse DOCX proof fixtures
  - [x] each DOCX fixture is classified against the maintained lane as `supported`, `bounded unsupported`, or `failed`
  - [x] if all three fixtures clear the same supported slice with inspected outputs, the `docx` row moves from `has fixture` to `passing`; otherwise it stays bounded honestly with the exact failure boundary recorded
- [x] Fresh `driver.py` proof exists for each DOCX fixture that is claimed as supported:
  - [x] the maintained DOCX lane leaves inspectable artifacts in `output/runs/`
  - [x] manual inspection is recorded for representative extraction artifacts, `output/html/manifest.json`, and `output/html/provenance/blocks.jsonl`
  - [x] provenance stays pageless-source honest and does not fabricate printed or source page numbers
- [x] XLSX and PPTX both receive measured local seam probes on repo-owned or reproducibly generated mini fixtures:
  - [x] the story records what currently works via `unstructured`, `openpyxl`, or other locally real deterministic seams
  - [x] the story records the observed failure modes, missing dependencies, or contract gaps for each family
  - [x] the story leaves one explicit outcome for each family: absorb in-story now, or defer with a named reason
- [x] If either XLSX or PPTX can reach the accepted `doc-web` bundle/provenance boundary with only small bounded glue on the current substrate, this story absorbs that first maintained lane instead of forcing another story by default
- [x] `docs/build-map.md`, `tests/fixtures/formats/_coverage-matrix.json`, `testdata/README.md`, `docs/RUNBOOK.md`, and any affected README/docs reflect the exact post-story office-document reality with no vague "et al" residue

## Out of Scope

- Claiming full-fidelity support for advanced Word, Excel, or PowerPoint features in one pass
- Hidden auto-routing or planner dispatch beyond the explicit-recipe compromise in `spec:1.1`
- Reopening the accepted `doc-web` runtime boundary from ADR-002
- Silent office-to-PDF fallback as a maintained default when it weakens provenance or changes the product claim
- Presentation polish, site theming, or Dossier-side adapter work

## Approach Evaluation

- **Simplification baseline**: office documents already carry native structure. The first question is whether current deterministic office-native seams plus the existing `doc-web` bundle boundary already solve the supported slice. Measure that before adding AI or new abstractions.
- **AI-only**: possible for hard PPTX mixed-layout cases, but a weak starting point for office formats because it discards native source structure and provenance too early. Use only if deterministic seams demonstrably fail on the claimed slice.
- **Hybrid**: likely strongest overall. Keep DOCX/XLSX/PPTX parsing native and deterministic where possible, then reserve AI for bounded repair only if a real artifact review shows a specific structure class that deterministic extraction flattens.
- **Pure code**: plausible for DOCX and XLSX because headings, cells, and table boundaries already exist in the source. Less obviously sufficient for PPTX because slide reading order and mixed-layout ownership may require more judgment.
- **Repo constraints / prior decisions**: `spec:1.1` keeps recipe selection explicit. ADR-002 fixes the output boundary at `doc-web` bundle + provenance sidecars. Story 172 and Story 174 already proved the first DOCX lane and the pageless provenance / contract signaling rules. Build Map Gap 3 and Next Action 1 name this exact office-document follow-up.
- **Existing patterns to reuse**: `configs/recipes/recipe-docx-html-mvp.yaml`, `modules/extract/unstructured_docx_intake_v1/`, `modules/transform/docx_elements_to_bundle_v1/`, `tests/test_docx_intake_recipe.py`, `testdata/generate_docx_fixture.py`, bundle-contract tests, and the repo-owned fixture discipline from Stories 167, 171, and 172.
- **Eval**: the deciding evidence is fresh artifact proof, not theoretical capability. For each office family:
  - maintained recipe or seam probe completes on a repo-owned/reproducible fixture
  - final `doc-web` bundle validates if the lane is claimed as maintained
  - manual inspection confirms the claimed supported slice and provenance honesty
  If the story adds a new office-family benchmark or golden surface, update `docs/evals/registry.yaml`; otherwise document why artifact proof is sufficient.

## Tasks

- [x] Freeze the broader office proof surface:
  - [x] add at least two additional repo-owned or reproducibly generated DOCX fixtures that broaden the currently supported slice
  - [x] add minimal repo-owned or reproducibly generated XLSX and PPTX fixtures for seam probing
  - [x] document the intended supported slice for each office family fixture
- [x] Measure the local office-native seams before broadening implementation:
  - [x] rerun the maintained DOCX lane on the widened fixture set and inspect the resulting artifacts
  - [x] probe XLSX with `unstructured.partition.xlsx`, `openpyxl`, and any other locally real low-complexity seam
  - [x] probe PPTX with `unstructured.partition.pptx` and any locally real deterministic slide seam; if a dependency or runtime gap blocks that path, record it explicitly instead of hand-waving it away
- [x] Implement the smallest coherent office-document chunk the evidence supports:
  - [x] widen the maintained DOCX lane only where fresh artifact evidence shows generic gaps, including generic heading/title normalization if wider fixtures expose false chapter splits
  - [x] if XLSX is absorbed, add an explicit maintained input path in `driver.py` / `RunConfig` instead of hiding workbook paths in recipe-only params
  - [x] if XLSX or PPTX can reach accepted bundle/provenance output with bounded glue, absorb that first maintained explicit lane into this story
  - [x] if not, leave one explicit split/stay-together decision with the next single lane named and justified
- [x] Add repeatable proof and contract coverage:
  - [x] extend or add focused office recipe tests and fixture generators
  - [x] extend bundle/provenance contract assertions only if new office-source anchors or semantics require it
  - [x] run real `driver.py` proofs for every lane claimed as maintained and manually inspect the resulting artifacts in `output/runs/`
- [x] If this story changes documented format coverage or graduation reality: update `docs/build-map.md` and record the before/after state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [ ] If agent tooling changed: `make skills-check`
- [x] If evals or goldens changed: run `/improve-eval` and update `docs/evals/registry.yaml`
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every output traces back to honest office-source anchors, not fabricated page metadata
  - [x] T1 — AI-First: only add AI where deterministic office-native seams actually fail on the supported slice
  - [x] T2 — Eval Before Build: measure the real local seams on fixtures before adding new lane abstractions
  - [x] T3 — Fidelity: office structure survives extraction without silent flattening or misleading normalization
  - [x] T4 — Modular: prefer explicit recipe/lane growth over an office-specific side system
  - [x] T5 — Inspect Artifacts: validate real bundle/provenance outputs, not just conversion logs

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: Category 1 office-document intake plus the Category 6/7 `doc-web` bundle/provenance boundary. Primary ownership starts with the maintained DOCX lane and may expand to one first non-DOCX office lane if the substrate is real enough to absorb coherently.
- **Build-map reality**: Category 1 is still `exists` and `climb`, but the office-family surface is materially clearer than when the story opened: `docx` is now `passing`, `xlsx` is now `has fixture` with a maintained first lane, and `pptx` is `has fixture` with an explicit measured runtime defer. Gap 3 is now about finishing office-family residue honestly rather than proving whether any non-DOCX office seam exists.
- **Substrate evidence**: the maintained DOCX lane remains real in code (`configs/recipes/recipe-docx-html-mvp.yaml`, `modules/extract/unstructured_docx_intake_v1/main.py`, `modules/transform/docx_elements_to_bundle_v1/main.py`, `tests/test_docx_intake_recipe.py`, and the three generated DOCX fixtures). Story 175 expanded that substrate with `modules/common/office_native_bundle.py`, `configs/recipes/recipe-xlsx-html-mvp.yaml`, `modules/extract/unstructured_xlsx_intake_v1/`, `modules/transform/xlsx_elements_to_bundle_v1/`, explicit `driver.py` / `RunConfig` XLSX input plumbing, focused XLSX tests, and repo-owned XLSX/PPTX probe fixtures. `unstructured.partition.xlsx` and `openpyxl` are real and working in this checkout; `unstructured.partition.pptx` is importable but still blocked by the missing `pptx` runtime dependency.
- **Fresh probe reality**: fresh post-implementation `driver.py` proofs now succeed on `testdata/docx-mini.docx`, `testdata/docx-sections-mini.docx`, `testdata/docx-nested-mini.docx`, and `testdata/xlsx-mini.xlsx`, with inspected bundle/provenance outputs under `output/runs/story175-*-r2/`. The previously observed DOCX false-chapter problem remains visible in raw Unstructured element types, but the maintained bundle boundary now normalizes those sentence-like top-level `Title` elements conservatively enough to keep the supported slice honest. PPTX remains explicitly blocked in the current checkout: `python -c "from unstructured.partition.pptx import partition_pptx; partition_pptx(filename='testdata/pptx-mini.pptx')"` still fails with `ModuleNotFoundError: No module named 'pptx'`.
- **Data contracts / schemas**: likely touched surfaces are `doc_web_bundle_manifest_v1` and `doc_web_provenance_block_v1`. The current pageless-source contract can already carry non-page-native `source_element_ids`, but spreadsheets or slides may require explicit row/cell/slide anchor conventions if a first maintained lane is absorbed here. Any new provenance fields that cross artifact boundaries must be added to `schemas.py` first.
- **File sizes**: existing likely touch points are `configs/recipes/recipe-docx-html-mvp.yaml` (25), `modules/extract/unstructured_docx_intake_v1/main.py` (215), `modules/transform/docx_elements_to_bundle_v1/main.py` (446), `tests/test_docx_intake_recipe.py` (81), `testdata/generate_docx_fixture.py` (57), `testdata/README.md` (63), `docs/RUNBOOK.md` (343), `README.md` (226), `tests/fixtures/formats/_coverage-matrix.json` (359), and `docs/build-map.md` (581). Only `docs/build-map.md` is already over 500 lines; keep edits there narrow. New XLSX/PPTX fixtures, recipes, or modules should stay small and explicit if they are absorbed.
- **Decision context**: reviewed `docs/ideal.md`, `docs/build-map.md`, `docs/requirements.md`, ADR-002, Stories 172 and 174, `testdata/README.md`, `tests/fixtures/formats/_coverage-matrix.json`, and Scout 011. No office-family-specific ADR currently exists; if office provenance semantics or routing ownership become broader than a single coherent implementation pass, stop and open that ADR question explicitly.

## Files to Modify

- `testdata/generate_docx_fixture.py` — extend or factor DOCX fixture generation for broader proof slices (57 lines)
- `testdata/README.md` — document the widened office proof surface and any new generated fixtures (63 lines)
- `tests/test_docx_intake_recipe.py` — widen maintained DOCX recipe coverage across multiple fixtures (81 lines)
- `driver.py` — add explicit maintained XLSX input plumbing only if XLSX is absorbed; do not hide a new family behind recipe-only params
- `schemas.py` — extend `RunConfig` only if XLSX is absorbed through a maintained explicit input override
- `configs/recipes/recipe-docx-html-mvp.yaml` — adjust only if the widened DOCX fixtures expose generic recipe gaps (25 lines)
- `modules/extract/unstructured_docx_intake_v1/main.py` — fix DOCX extraction or provenance handling only if the broader proof surfaces real generic defects (215 lines)
- `modules/transform/docx_elements_to_bundle_v1/main.py` — fix broader DOCX proof gaps and/or extract a shared office-native bundle helper if XLSX is absorbed (446 lines)
- `tests/fixtures/formats/_coverage-matrix.json` — update `docx`, `xlsx`, and `pptx` rows to the exact proven state (359 lines)
- `docs/build-map.md` — update Gap 3, Gap 5, and office input-coverage truth narrowly (581 lines)
- `docs/RUNBOOK.md` — publish verified office proof commands and supported slices (343 lines)
- `README.md` — keep the user-facing office-family story aligned with reality (226 lines)
- `testdata/*.source.json`, `testdata/*.docx`, `testdata/*.xlsx`, `testdata/*.pptx` — new repo-owned or reproducible office fixtures if the story absorbs them
- `configs/recipes/recipe-xlsx-html-mvp.yaml` — likely if the first non-DOCX office lane absorbed is XLSX
- `modules/extract/unstructured_xlsx_intake_v1/` and matching focused tests — likely if the seam evidence support absorbing XLSX now
- `configs/recipes/recipe-pptx-html-mvp.yaml` / `modules/extract/*pptx*` and matching tests — only if PPTX runtime proof becomes real enough to absorb after the current baseline

## Redundancy / Removal Targets

- Another narrow DOCX-only follow-up if this story can absorb the wider office proof coherently
- Any vague "office docs later" notes once the post-story office-family decision is explicit
- Scratch XLSX/PPTX seam-probe scripts if the absorbed lane can be represented by real fixtures, recipes, and tests
- Any stale wording that treats DOCX as the whole office-document answer after this story lands

## Notes

- This story intentionally follows the user's preference for a larger office-document chunk. The default is to absorb the first tractable non-DOCX lane if the local substrate is honestly good enough, not to split reflexively.
- The corresponding guardrail is just as important: do not force XLSX and PPTX into one fake "office" abstraction if the artifact evidence shows they are materially different problems.
- DOCX should only move to `passing` if the widened fixture set actually earns it. A larger story is not permission to overstate support.
- PPTX is the most likely family to demand a hybrid or AI-repair path because slide layout and reading order are less source-explicit than DOCX or XLSX. That is a valid reason to split later if the baseline proves it.

## Plan

### Exploration Summary

- **Ideal alignment:** this story closes a real Ideal gap. `docs/ideal.md` explicitly includes office documents, and the build map still names office intake beyond the first DOCX slice as an active gap.
- **Current build-map signal:** DOCX is now a first maintained lane but remains only `has fixture`; XLSX and PPTX are still `untested`. The build map's first next action is to widen DOCX proof and then decide whether XLSX/PPTX should split or stay together.
- **Critical substrate already verified:** the maintained DOCX lane and contract surfaces are real in this repo; the local runtime also exposes `unstructured.partition.xlsx`, `unstructured.partition.pptx`, and `openpyxl`, which was enough to justify a baseline-first office expansion pass. Fresh probe results sharpen the story materially:
  - current DOCX still passes on the checked-in fixture through `driver.py` with `entry_count=2` and `provenance_row_count=7`
  - broader temp DOCX probes exposed a real generic defect: Unstructured can misclassify some plain paragraphs as top-level `Title`, which causes false chapter splits in `docx_elements_to_bundle_v1`
  - XLSX is already near the accepted boundary on the current substrate: `openpyxl` loads the workbook directly, `unstructured.partition.xlsx` emits a `Table` element with `page_name`, `page_number`, and `text_as_html`, and that serialized element can already flow through the current bundle builder to a valid one-entry bundle + provenance sidecar
  - PPTX is not honestly runnable yet in this checkout: a temp `pandoc`-generated `.pptx` reaches `unstructured.partition.pptx`, but the partition call fails on missing `pptx`
- **Why `Pending` is honest:** the critical substrate for the first half of the story is already implemented, and the second half is explicitly framed as measured lane-decision work with optional absorption of one tractable family, not as a blind promise to ship all office formats.

### Eval-First Gate

- **Baseline numbers from current code:**
  1. `testdata/docx-mini.docx` still completes through `driver.py` on the maintained lane with `2` entries and `7` provenance rows.
  2. Temp broader DOCX probes currently fail the family-width bar honestly even when the run succeeds: one simple variant created a false chapter from a plain paragraph, and one nested-heading variant created a false chapter from top-level body text before the real appendix. That means DOCX widening is not docs-only; it needs a generic extraction/bundle normalization fix.
  3. Temp XLSX probe: `openpyxl` loaded the workbook exactly, `unstructured.partition.xlsx` returned one `Table` element with `page_name=Roster`, `page_number=1`, and `text_as_html`, and the serialized element already produced a valid one-entry `doc_web_bundle` plus one provenance row through the current bundle builder.
  4. Temp PPTX probe: `pandoc` generated a minimal `.pptx`, but `unstructured.partition.pptx` failed immediately with `ModuleNotFoundError: No module named 'pptx'`.
- **Decision rule for absorbing a non-DOCX lane:** absorb it in this story only if it can reach the accepted `doc-web` bundle/provenance boundary with small bounded glue and no new unresolved architecture. Current recommendation from the baseline is to absorb XLSX and to treat PPTX as an explicit measured defer unless the missing runtime seam becomes real without broadening the architecture.

### Implementation Outline

1. Add the broader office fixture surface.
   - Create or generate at least two more DOCX fixtures.
   - Create minimal XLSX and PPTX probe fixtures.
2. Fix the widened DOCX slice before claiming family breadth.
   - Add the fixture classifications.
   - Tighten DOCX heading/title handling so plain paragraphs do not become chapter boundaries when the broader proof surface exercises slightly different Word authoring patterns.
3. Absorb the XLSX lane on the current substrate unless fresh implementation evidence disproves it.
   - Add an explicit maintained XLSX recipe, fixture(s), and intake module wrapper.
   - Add explicit `driver.py` / `RunConfig` XLSX input plumbing instead of relying on hidden recipe params.
   - Reuse or extract the current bundle emitter logic instead of cloning a second near-identical office builder.
4. Keep PPTX as a measured decision, not an aspirational promise.
   - Re-run the PPTX seam probe on a repo-owned or reproducible mini fixture.
   - If the only blocker remains the missing runtime dependency, record that explicitly and defer PPTX with a named reason instead of forcing a half-maintained lane into the story.
5. Update truth surfaces.
   - Build map, coverage matrix, README, runbook, and testdata docs should all tell the same office-document story.

### Impact Analysis

- **Primary blast radius:** office fixtures, the maintained DOCX lane, explicit office-family input plumbing in `driver.py` / `RunConfig`, and office-family truth surfaces.
- **Secondary blast radius:** bundle/provenance contract tests plus any shared bundle-emitter extraction if XLSX absorbs the current DOCX builder logic.
- **Main risk:** over-claiming office support because the story is intentionally larger. The current probes reduce that ambiguity rather than increasing it: XLSX now looks small and coherent, while PPTX still looks meaningfully blocked.
- **Structural health note:** if XLSX is absorbed, do not ship it through a misleading DOCX-only module name or duplicate `DocWebBundleManifest` / `DocWebProvenanceBlock` writing logic again. Prefer a small shared office-native bundle helper or an honestly generalized module boundary.
- **Approval blocker:** none right now. The main stop condition is architectural, not scope size: if XLSX ends up needing new cross-cutting provenance semantics beyond `source_element_ids`, or if PPTX needs more than a bounded runtime fix plus proof, stop and record that explicitly instead of broadening the story by inertia.

### What Done Looks Like

- DOCX is either promoted to an honestly broader supported family or remains explicitly bounded with concrete failure edges.
- XLSX and PPTX are no longer vague backlog residue: one is absorbed now if tractable, or the story leaves a clear next single lane with measured reasons.
- Office-document reality in docs and coverage surfaces is materially simpler and more trustworthy than it is today.

## Work Log

20260331-2135 — story created from triage plus user direction: turned Build Map Next Action 1 into a broader office-document follow-up instead of another narrow DOCX-only stub. Evidence gathered in this pass: `docs/build-map.md` still ranks office-document widening first; the `docx` row remains `has fixture` on one narrow lane while `xlsx` and `pptx` remain `untested`; `configs/recipes/recipe-docx-html-mvp.yaml`, `modules/extract/unstructured_docx_intake_v1/main.py`, and `modules/transform/docx_elements_to_bundle_v1/main.py` prove the maintained DOCX substrate is real; `importlib.util.find_spec(...)` also found `unstructured.partition.xlsx`, `unstructured.partition.pptx`, and `openpyxl`, while direct `pptx` import is currently missing. Result: this story is buildable as a single coherent office-doc chunk with an absorb-if-tractable rule for XLSX/PPTX instead of automatic story splitting. Next step: `/build-story` should lock the widened DOCX fixture set first, then run the XLSX/PPTX seam probes before deciding what gets absorbed.
20260401-0404 — exploration and planning: verified `docs/ideal.md`, `docs/spec.md` (`spec:1`, `spec:3`, `spec:6`, `spec:7`, `spec:8`), `docs/build-map.md`, ADR-002, `docs/requirements.md`, Stories 172/174, `README.md`, `docs/RUNBOOK.md`, `driver.py`, `schemas.py`, `modules/extract/unstructured_docx_intake_v1/main.py`, `modules/transform/docx_elements_to_bundle_v1/main.py`, `tests/test_docx_intake_recipe.py`, and the coverage matrix rows for `docx` / `xlsx` / `pptx`. Fresh baseline evidence from temp probe runs:
- DOCX current baseline still holds on the checked-in fixture: a fresh `driver.py` run on `testdata/docx-mini.docx` under `/var/folders/8f/3nlcf3sj1s5bbk1g_3dt3djm0000gn/T/story175-office-probe-vsti_mde/docx-run/story175-docx-baseline/` produced `entry_count=2`, `provenance_row_count=7`, empty `source_pages`, and pageless provenance rows with stable `source_element_ids`.
- Broader DOCX proof is not a docs-only exercise: two temp generated DOCX probes under `/var/folders/8f/3nlcf3sj1s5bbk1g_3dt3djm0000gn/T/story175-docx-xlsx-followup-2f7m1h7b/` both completed through the maintained lane, but Unstructured promoted some plain body paragraphs to top-level `Title`, which made `docx_elements_to_bundle_v1` create false chapter splits (`entry_titles` included body prose such as `A simple maintained DOCX with two top-level sections.` and `Top-level context paragraph.`). Result: Story 175 needs a generic DOCX heading/title normalization fix if it is going to widen proof honestly.
- XLSX substrate is real enough to absorb with bounded glue: `openpyxl` loaded a temp workbook exactly; `unstructured.partition.xlsx` returned a single `Table` element with `page_name=Roster`, `page_number=1`, and `text_as_html`; and a serialized XLSX element already flowed through the current bundle builder to a valid one-entry bundle + provenance shape under `/var/folders/8f/3nlcf3sj1s5bbk1g_3dt3djm0000gn/T/story175-xlsx-builder2-7yaukkdg/output/html/`.
- PPTX substrate is not yet honest enough to absorb: `pandoc` generated a temp `.pptx` successfully, but `unstructured.partition.pptx` failed in this checkout with `ModuleNotFoundError: No module named 'pptx'`. Additional static seam finding: `driver.py` and `RunConfig` currently expose explicit override plumbing for `pdf` and `docx`, but not for `xlsx` or `pptx`, so any absorbed non-DOCX maintained lane should add an explicit input path rather than burying it in recipe params.
Result: the story remains honestly buildable, but the coherent implementation target is now sharper than when it was created. Recommendation is to widen/fix DOCX and absorb XLSX in the same pass, while treating PPTX as an explicit measured defer unless a bounded runtime fix plus artifact proof materializes during implementation. Next step: present this plan to the user for the human gate before touching code.
20260401-0506 — implementation, proof, and docs alignment complete for the build phase. Shipped a shared office-native bundle helper (`modules/common/office_native_bundle.py`), refactored `docx_elements_to_bundle_v1` onto it, and added a conservative sentence-title normalization rule so widened DOCX fixtures stop turning sentence-like `Title` misclassifications into bogus chapter boundaries. Added the first maintained XLSX lane with explicit `driver.py` / `RunConfig` plumbing, `configs/recipes/recipe-xlsx-html-mvp.yaml`, `modules/extract/unstructured_xlsx_intake_v1/`, `modules/transform/xlsx_elements_to_bundle_v1/`, repo-owned XLSX fixture generation, and focused recipe / clean-venv contract coverage. Also widened the repo-owned office fixture surface with two more generated DOCX fixtures plus reproducible XLSX and PPTX mini fixtures, then updated `README.md`, `docs/RUNBOOK.md`, `testdata/README.md`, `docs/build-map.md`, and `tests/fixtures/formats/_coverage-matrix.json` to reflect the post-story reality.

Fresh maintained-lane proof after clearing `*.pyc`:
- DOCX fixture classification:
  - `testdata/docx-mini.docx` — `supported` for the maintained slice (simple headings, prose, bullets, table)
  - `testdata/docx-sections-mini.docx` — `supported`; raw intake still emits a sentence as `Title`, but bundle output keeps it inside `Overview` instead of inventing a third chapter
  - `testdata/docx-nested-mini.docx` — `supported`; raw intake still emits `Top-level context paragraph.` as `Title`, but bundle output preserves it as paragraph content under `Overview` and keeps nested `Subsection A` attached to the first chapter
- XLSX fixture outcome:
  - `testdata/xlsx-mini.xlsx` — absorbed in-story as the first maintained XLSX slice (`supported` for simple sheet-table workbooks with pageless provenance and sheet-backed entry titles)
- PPTX fixture outcome:
  - `testdata/pptx-mini.pptx` — deferred with named reason: `python -c "from unstructured.partition.pptx import partition_pptx; partition_pptx(filename='testdata/pptx-mini.pptx')"` still fails immediately in this checkout with `ModuleNotFoundError: No module named 'pptx'`, so there is no honest maintained PPTX runtime seam yet

Manual artifact inspection from fresh `driver.py` runs under `output/runs/`:
- `story175-docx-mini-r2`
  - `01_unstructured_docx_intake_v1/elements.jsonl` shows the expected simple DOCX mix (`Title`, `NarrativeText`, `ListItem`, `Table`)
  - `output/html/manifest.json` shows `reading_order=["chapter-001","chapter-002"]` with titles `Family Snapshot` and `Notes`
  - `output/html/provenance/blocks.jsonl` includes pageless provenance rows such as `blk-chapter-001-0002` quoting `The DOCX fixture exercises...` and `blk-chapter-001-0003` quoting `Parents: Ada and Lin`; no `source_pages` or `printed_pages` were fabricated
- `story175-docx-sections-r2`
  - `01_unstructured_docx_intake_v1/elements.jsonl` still contains the misclassified raw `Title` `A simple maintained DOCX with two top-level sections.`
  - `output/html/manifest.json` stays at exactly two chapters, `Overview` and `Roster`
  - `output/html/provenance/blocks.jsonl` records that sentence as `blk-chapter-001-0002` with `block_kind="paragraph"`, proving the normalization is applied at the supported boundary
- `story175-docx-nested-r2`
  - `01_unstructured_docx_intake_v1/elements.jsonl` still contains raw `Title` nodes for `Top-level context paragraph.` and nested `Subsection A`
  - `output/html/manifest.json` stays at exactly two chapters, `Overview` and `Appendix`
  - `output/html/provenance/blocks.jsonl` records `Top-level context paragraph.` as a paragraph block and `Subsection A` as a heading inside `chapter-001`
- `story175-xlsx-mini-r2`
  - `01_unstructured_xlsx_intake_v1/elements.jsonl` contains two `Table` elements with sheet metadata (`page_name=Roster`, `page_name=Visits`) plus HTML table payloads
  - `output/html/manifest.json` shows `reading_order=["page-001","page-002"]` with titles `Roster` and `Visits`
  - `output/html/provenance/blocks.jsonl` records two pageless table provenance rows and `output/html/page-001.html` renders the expected workbook table including `Foothills County`

Checks run:
- `python -m pytest tests/test_docx_intake_recipe.py tests/test_xlsx_intake_recipe.py tests/test_run_config.py -q` → `10 passed`
- `python -m pytest tests/test_doc_web_cli_contract.py -q` → `6 passed`
- `make lint` → passed
- `make test` → `404 passed, 4 warnings`

Impact:
- Story-scope impact: Story 175 now closes the office-doc ambiguity it was opened for. DOCX crosses the three-fixture proof bar and moves to `passing`, XLSX stops being a vague follow-up and becomes the first maintained non-DOCX office lane, and PPTX is no longer backlog fog because its current runtime blocker is measured and named.
- Pipeline-scope impact: the supported office-native path now reuses one bundle/provenance emitter, exposes XLSX as an explicit maintained input override, and preserves pageless provenance honesty while preventing false DOCX chapter splits from sentence-like `Title` misclassification.
- Eval note: no benchmark tasks, golden sets, or registry rows changed in this story; artifact proof and fresh driver runs were the governing evidence surface, so `/improve-eval` was not needed.
- Next: run `/validate` against the current diff, then close the story with `/mark-story-done` if the validation pass agrees with the inspected artifact evidence.
20260331-2303 — `/mark-story-done` close-out: re-validated the completed Story 175 implementation against fresh current-state evidence before marking it done. In this pass, `make lint` passed, `make test` passed (`404 passed, 4 warnings`), the maintained DOCX/XLSX proof artifacts still validated against `doc_web_bundle_manifest_v1` and `doc_web_provenance_block_v1`, and the PPTX defer remained reproducible on the checked-in probe fixture with `ModuleNotFoundError: No module named 'pptx'`. Updated the story status to `Done`, checked the validation and done workflow gates, and aligned `docs/stories.md` plus `CHANGELOG.md` with the shipped slice. Recommended next step: `/check-in-diff`.
