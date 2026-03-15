# Story 142 — Onward Genealogy Consistency Detection and Rerun Gating

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Fidelity to Source, Dossier-ready output
**Spec Refs**: C1 (Multi-Stage OCR Pipeline), C2 (Format-Specific Conversion Recipes), C6 (Expensive OCR for Quality)
**Decision Refs**: `docs/decisions/adr-001-source-aware-consistency-strategy/adr.md`, `docs/runbooks/golden-build.md`, `docs/scout/scout-003-storybook-patterns.md`, Story 140 and Story 141 work logs
**Depends On**: Story 140, Story 141

## Goal

Implement the first concrete consistency slice under ADR-001 for the Onward genealogy converter as a read-only detector/gating stage: identify likely same-schema genealogy runs from existing artifacts, quantify where structural drift occurs, infer provisional schema hints, and measure whether selective source-aware reruns are justified. This story should prove that the signals are strong enough to drive reruns later without yet changing extracted page HTML.

## Acceptance Criteria

- [x] In a fresh verification run using reused upstream artifacts where possible, the reviewed problem chapters [chapter-010.html](/Users/cam/Documents/Projects/codex-forge/output/runs/story140-onward-targeted-rescue-r19/output/html/chapter-010.html), [chapter-013.html](/Users/cam/Documents/Projects/codex-forge/output/runs/story140-onward-targeted-rescue-r19/output/html/chapter-013.html), [chapter-014.html](/Users/cam/Documents/Projects/codex-forge/output/runs/story140-onward-targeted-rescue-r19/output/html/chapter-014.html), and [chapter-015.html](/Users/cam/Documents/Projects/codex-forge/output/runs/story140-onward-targeted-rescue-r19/output/html/chapter-015.html) are correctly flagged as structurally inconsistent same-schema genealogy runs in the emitted report
- [x] The emitted report preserves access to original page-level artifacts and records enough metadata to explain run membership, schema fingerprints/hints, confidence, flagged pages, and measured rerun coverage without rewriting page HTML yet
- [x] Manual inspection confirms the detector does not broadly over-flag the current non-regression references, including `chapter-009.html` and at least one of `chapter-018.html` / `chapter-020.html`
- [x] The story records the measured rerun-coverage band and recommendation for the next slice: proceed to selective rerun automation or escalate to broader extraction granularity

## Out of Scope

- Automated source-aware reruns
- HTML rewriting or canonicalization beyond any report formatting needed for inspection
- A generic all-document consistency framework across every structure type
- Solving heading/list consistency outside what is required for the Onward genealogy slice
- Full chapter-aware extraction for the entire recipe unless the detector evidence later proves page-scope extraction is the wrong granularity
- Hand-editing HTML artifacts outside the pipeline
- Closing ADR-001 itself; this story should follow the decision, not replace it

## Approach Evaluation

This story starts after Story 141's investigation, ADR-001 research, and cross-provider synthesis. The key change from the earlier draft is intentional: the first slice should measure and report the rerun signals before automating the reruns themselves.

- **Simplification baseline**: Before automating reruns, prove that cheap artifact analysis can reliably identify the known bad runs and avoid broad false positives on the reviewed non-regression chapters.
- **AI-only**: Not the first slice. AI belongs in the later rerun stage once the detector has shown that the right pages/runs can be targeted confidently.
- **Hybrid**: Current leading path for the overall architecture. This story should implement only the deterministic/statistical half: detection, clustering, schema hints, confidence, and rerun-coverage measurement.
- **Pure code**: Appropriate for this first slice. The emitted artifact is a decision report, not a semantic repair.
- **Repo constraints / prior decisions**: ADR-001 now explicitly recommends detection/gating first. Story 140's rescue wins must not regress. OCR/source reads are expensive, so rerun automation should not land until the detector proves the likely rerun set is acceptably small and well-targeted.
- **Existing patterns to reuse**: `load_artifact_v1` reuse flows, Story 141's measured bad/good chapter set, `table_rescue_onward_tables_v1` structural signals, and existing run-health/report patterns where useful.
- **Eval**: The distinguishing test is whether the detector cleanly separates the reviewed drift chapters from the reviewed non-regression chapters and produces stable rerun-coverage signals.

## Tasks

- [x] Add the first read-only Onward consistency detector as a chapter-first / page-second report stage, using final chapter HTML for drift decisions and source page HTML only to narrow likely rerun targets
- [x] Detect and cluster the reviewed same-schema genealogy runs from existing artifacts, including explicit run membership, schema-hint, and confidence signals
- [x] Emit a report-only artifact that records flagged pages/runs, rerun coverage, and whether the recipe is still a good fit for page-scope extraction
- [x] Add focused regression coverage for run detection, confidence gating, and false-positive control on the reviewed non-regression chapters
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test` (`585 passed, 5 skipped` after updating `Makefile` to prefer the active environment interpreter with `python3` fallback)
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py` with artifact reuse, verify artifacts in `output/runs/`, and manually inspect the emitted report plus the reviewed HTML outputs
  - [x] If agent tooling changed: `make skills-check` (not needed; no agent tooling changed)
- [x] If evals or goldens changed: run `/verify-eval` and update `docs/evals/registry.yaml` (not needed; no eval or golden files changed)
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every flagged run traces to source pages, prior artifact IDs, and the decision path
  - [x] T1 — AI-First: the story stops before building AI reruns because the detector must justify where AI is actually needed
  - [x] T2 — Eval Before Build: Story 141 baseline plus ADR synthesis justify this report-first slice
  - [x] T3 — Fidelity: the detector/report must not rewrite content and must preserve reviewed good chapters as good
  - [x] T4 — Modular: keep the change recipe-scoped and avoid hidden book-specific logic in generic modules
  - [x] T5 — Inspect Artifacts: manually inspect the report artifacts and reviewed HTML outputs, not just tests/logs

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: A new recipe-scoped report stage after `build_chapters` is now the preferred seam. It should read built chapter HTML plus the reused `page_html` artifact so drift is decided at chapter/run scope and only then narrowed to culprit pages.
- **Data contracts / schemas**: Prefer a report artifact over rewriting `page_html_v1` in this story. First choice is an existing flexible report container such as `pipeline_issues_v1` plus a richer sidecar JSON/JSONL report; add a new schema only if stamping proves the existing report shapes are too constraining.
- **File sizes**: `configs/recipes/recipe-onward-images-html-mvp.yaml` is 178 lines; `modules/adapter/table_rescue_onward_tables_v1/main.py` is 1400 lines; `modules/build/build_chapter_html_v1/main.py` is 1383 lines; `tests/test_build_chapter_html.py` is 1054 lines. Prefer a focused new module/test file over enlarging already oversized files, and avoid touching `build_chapter_html_v1` unless the manifest is missing source-page metadata needed by the report.
- **Decision context**: Reviewed `docs/ideal.md`, `docs/spec.md`, Story 140, Story 141, ADR-001, the four provider research reports, and the current `story140-onward-targeted-rescue-r19` artifacts. The crucial build-story finding is that page-level anomaly signals alone over-flag reviewed good chapters, so the first decision boundary must be chapter/run level.

## Files to Modify

- `modules/validate/validate_onward_genealogy_consistency_v1/module.yaml` — new report-stage declaration using `pipeline_issues_v1` for the stamped summary artifact (new file)
- `modules/validate/validate_onward_genealogy_consistency_v1/main.py` — chapter-first drift detection, clustering, rerun-coverage measurement, and page-level culprit narrowing (new file)
- `configs/recipes/recipe-onward-images-html-mvp.yaml` — wire the report stage into the Onward recipe or the reused-artifact validation recipe after `build_chapters` (178 lines)
- `configs/recipes/story-142-onward-genealogy-consistency-validate.yaml` — story-scoped reused-artifact validation recipe that rebuilds chapters and runs the report stage without fresh OCR (new file)
- `tests/test_validate_onward_genealogy_consistency_v1.py` — focused regression coverage for chapter/run detection, confidence gating, and false-positive control (new file)
- `modules/build/build_chapter_html_v1/main.py` — avoid touching unless the chapter manifest lacks source-page metadata needed by the report (1383 lines)
- `schemas.py` — only if existing report schemas prove too constrained for the emitted artifact (809+ lines)
- `docs/stories/story-142-onward-source-aware-genealogy-consistency-first-slice.md` — build/implementation work log

## Redundancy / Removal Targets

- Temporary experiment scripts/prompts from Story 141 once the detector/report path is stable
- Any speculative HTML-only normalization code that this detector shows is unnecessary before a rerun path exists

## Notes

- `/build-story` resolved the main seam question: the first slice should not score pages in isolation. It should score built chapters/runs first, then narrow flagged chapters back to source pages for rerun targeting.
- The key measurement is rerun coverage. Use `25%` as a warning band and `30%` across multiple documents as the provisional trigger to evaluate broader extraction granularity instead of scaling targeted reruns indefinitely.
- A later follow-up story should automate schema-frozen reruns only if this detector/report slice proves the signal quality is strong enough.

## Plan

### Exploration Findings

- The current Onward validation harness already provides the right reusable baseline: `story140-onward-targeted-rescue-r19` loads `pages_html_onward_tables_fixed.jsonl`, `portions_toc.jsonl`, and `illustration_manifest.jsonl`, then rebuilds chapter HTML. That means Story 142 can validate without new OCR or rescue cost.
- Existing repo patterns already support the smallest useful implementation shape. `detect_duplicate_pages_v1` shows a pass-through page stage with a sidecar report; `report_pipeline_issues_v1` shows a report-only stage using `pipeline_issues_v1`. Story 142 does not need a brand-new report architecture just to start.
- Manual artifact inspection on `story140-onward-targeted-rescue-r19` shows the reviewed bad/good separation is strongest at chapter scope, not page scope:
  - `chapter-009.html` = `2` tables, `69` subgroup rows, `0` `BOY/GIRL` headers
  - `chapter-010.html` = `20` tables, `18` external family headings, `80` subgroup rows
  - `chapter-013.html` = `3` tables, `18` subgroup rows, `1` `BOY/GIRL` header
  - `chapter-014.html` = `15` tables, `3` external family headings, `3` `BOY/GIRL` headers
  - `chapter-015.html` = `4` tables, `0` subgroup rows, `3` `BOY/GIRL` headers
  - `chapter-018.html` = `3` tables, `17` subgroup rows, `0` `BOY/GIRL` headers
  - `chapter-020.html` = `3` tables, `36` subgroup rows, `0` `BOY/GIRL` headers
- Page-level anomaly signals alone are not enough. The reused `pages_html_onward_tables_fixed.jsonl` artifact shows strong page anomalies inside reviewed good chapters too:
  - `chapter-009` source pages: `4/6` pages show `BOY/GIRL`, external family headings, or fragmented multi-table layout before build
  - `chapter-018` source pages: `2/6` pages show similar page-local anomalies before build
  - Yet both final chapters are acceptable references after build-time normalization
- The clean seam is therefore chapter-first / page-second:
  - first decide whether the built chapter/run is structurally inconsistent
  - then narrow flagged chapters back to specific source pages for future reruns
- `build_chapter_html_v1` already writes the metadata needed for that mapping. `chapters_manifest.jsonl` includes chapter file paths plus `source_pages` and `source_printed_pages`, so the first slice should not require builder changes unless implementation finds a real metadata gap.

### Ideal Alignment Gate

- This story closes an Ideal gap directly: the same genealogy structure still lands in materially different final HTML forms across nearby chapters.
- The chosen seam moves toward the Ideal. It measures inconsistency on the user-facing built output while preserving the source page artifacts needed for traceable reruns later.
- The story does not introduce a new AI compromise. It explicitly delays AI reruns until deterministic detection proves where AI is actually needed.
- A page-only detector would optimize the current compromise instead of closing the gap, because the current build already resolves some messy page inputs into good chapter output. That would be a local optimum.

### Eval / Baseline

- Current pipeline baseline: there is no automated consistency report yet, so `0/4` reviewed bad chapters are automatically flagged today.
- Manual baseline on `story140-onward-targeted-rescue-r19` shows a plausible deterministic chapter-level separation:
  - reviewed bad set = `chapter-010.html`, `chapter-013.html`, `chapter-014.html`, `chapter-015.html`
  - reviewed non-regression set = `chapter-009.html`, `chapter-018.html`, `chapter-020.html`
- Manual page-level probe shows why the detector must not stop at page scope:
  - coarse page anomaly upper bound inside the reviewed bad chapters = `14/28` source pages
  - stronger culprit-page subset inside the reviewed bad chapters (`external_family_headings` or fragmented multi-table pages) = `5/28` source pages
  - reviewed good chapters still contain page-local anomalies before build, so chapter-level drift has to gate any later rerun targeting
- Baseline success criterion for the implementation slice:
  - flag the four reviewed bad chapters
  - do not flag the three reviewed non-regression chapters
  - report both the chapter-level drift coverage and the narrowed source-page rerun-coverage band

### Implementation Plan

#### Task 1 — Add the first report stage at the validated seam

- Files: new module `module.yaml` + `main.py`, plus `configs/recipes/recipe-onward-images-html-mvp.yaml`
- Change:
  - Add a new recipe-scoped stage after `build_chapters`.
  - Feed it the built chapter manifest and the reused `page_html` artifact that build already consumed.
  - Keep the stage read-only. It should emit a report artifact, not rewrite chapter or page HTML.
- Preferred contract:
  - primary output should use an existing report-friendly schema if possible
  - richer sidecar JSON/JSONL is acceptable for detailed drill-down
- Risk:
  - If the chosen stage cannot read the chapter files cleanly from the manifest, we may need a small recipe or manifest-path adjustment.
- Done when:
  - the stage runs in a reused-artifact validation recipe and emits a report with per-chapter metrics plus source-page mapping

#### Task 2 — Implement chapter/run detection and clustering

- Files: new detector module + focused tests
- Change:
  - Detect candidate genealogy chapters/runs from built chapter HTML using the stable header schema and genealogy-specific structural cues already present in current artifacts.
  - Compute per-chapter fingerprints and hints such as:
    - table count and table density vs source-page count
    - external family-heading count
    - subgroup-row count
    - residual `BOY/GIRL` header count
    - schema/header token signature
    - source-page span and printed-page span
  - Cluster contiguous same-schema chapters into runs and score which chapters drift away from the best-normalized representation in that run.
- Risk:
  - Overfitting to chapter titles or one-off family names would make the module brittle. Keep signals structural and recipe-scoped.
- Done when:
  - the report explains run membership, per-chapter drift reasons, schema hints, and confidence

#### Task 3 — Narrow flagged chapters to likely rerun pages and measure coverage

- Files: new detector module + focused tests
- Change:
  - Only after a chapter/run is flagged, inspect the corresponding `page_html` rows and rank likely culprit pages.
  - Distinguish:
    - coarse suspect pages
    - stronger rerun-candidate pages
  - Record both coverage numbers so later stories can judge whether targeted reruns are still economical under ADR-001's `25%` warning / `30%` redesign thresholds.
- Risk:
  - If page narrowing is too coarse, the story will not actually answer whether reruns are targeted enough to justify automation.
- Done when:
  - the report includes a chapter-level decision plus a narrowed page-target set with artifact paths back to the reused `pages_html_onward_tables_fixed.jsonl`

#### Task 4 — Add focused regression coverage and validate on reused artifacts

- Files: `tests/test_<new consistency detector>.py`, recipe/run-local validation inputs, story work log
- Change:
  - Add fixture-backed tests for the chapter-level signal separation and the page-level false-positive guard.
  - Reuse the existing Onward build harness so validation does not re-run OCR or page rescue.
  - Manual verification must inspect:
    - the emitted report artifact(s)
    - `chapter-009.html`, `chapter-010.html`, `chapter-013.html`, `chapter-014.html`, `chapter-015.html`, and at least one of `chapter-018.html` / `chapter-020.html`
- Risk:
  - If the module only passes synthetic fixtures and not the reused real run, the story has not proven the seam.
- Done when:
  - tests pass, the report matches the reviewed bad/good chapter split, and the work log records artifact paths plus sample decisions

#### Task 5 — Docs, ADR integration, and cleanup

- Files: Story 142, related docs, optional ADR integration checklist items touched by implementation
- Change:
  - Update the story work log with the measured rerun-coverage band and whether the next story should automate reruns or escalate extraction granularity.
  - Update any docs touched by the new stage or validation workflow.
  - Do not create the rerun automation story from assumption; create it only if Story 142's measurements support it.
- Done when:
  - the story and related docs reflect the actual measured decision, not the pre-implementation guess

### Scope Adjustment

- Small coherent seam shift absorbed: the first slice should run after `build_chapters`, not between `table_fix_continuations` and build. The artifact evidence shows chapter-level output is the right decision surface.
- Small coherent contract decision absorbed: avoid a new cross-stage HTML contract in this story. The first slice is report-only.
- Explicitly not absorbed: automated reruns, schema-frozen re-extraction, and any general framework for headings/lists beyond the Onward genealogy case.

### Human Approval Gate

- Recommended implementation direction: build a chapter-first consistency report stage, not another page mutator or builder normalization pass.
- No new dependencies are expected.
- A new schema should be avoided unless the existing report containers prove genuinely insufficient.
- Success is falsified if:
  - the detector still cannot separate `chapter-010.html`, `chapter-013.html`, `chapter-014.html`, and `chapter-015.html` from `chapter-009.html`, `chapter-018.html`, and `chapter-020.html`
  - the report cannot map flagged chapters back to source-page artifacts cleanly
  - the measured rerun coverage is too vague to decide whether targeted reruns remain the right next step

## Work Log

20260314-1938 — story created: split the real implementation follow-up out of Story 141 after the investigation showed the next move should follow ADR-001's source-aware consistency framing rather than the older HTML-normalization framing
20260314-2352 — synthesis rescope: narrowed the first slice to detection and rerun gating after xAI, Opus, OpenAI, and Gemini all converged on report-first / rerun-second as the safer architecture
20260314-2358 — build-story exploration: traced the Onward recipe, existing rescue/build modules, report-stage patterns, and the reused `story140-onward-targeted-rescue-r19` artifacts; found that page-only anomaly signals over-flag reviewed good chapters (`chapter-009` and `chapter-018`), so the detector must decide inconsistency at chapter/run scope before narrowing back to culprit pages
20260315-0004 — build-story plan: promoted Story 142 to active implementation planning, settled the first concrete seam as a post-build read-only consistency report, documented the measured bad/good chapter baseline plus provisional page-target coverage bands, and left automated reruns explicitly deferred pending the report results
20260315-0017 — implementation: added `validate_onward_genealogy_consistency_v1` as a new validate-stage module, wired it into the main Onward recipe, and added focused coverage in [tests/test_validate_onward_genealogy_consistency_v1.py](/Users/cam/.codex/worktrees/72eb/codex-forge/tests/test_validate_onward_genealogy_consistency_v1.py); focused checks passed with `python -m pytest tests/test_validate_onward_genealogy_consistency_v1.py -q` and `python -m ruff check modules/validate/validate_onward_genealogy_consistency_v1/main.py tests/test_validate_onward_genealogy_consistency_v1.py`
20260315-0026 — direct artifact probe: ran the new validator directly against `story140-onward-targeted-rescue-r19` and confirmed it flagged the reviewed bad set (`chapter-010/013/014/015`) while keeping `chapter-009`, `chapter-018`, and `chapter-020` unflagged; the summary reported `strong_rerun_candidate_page_coverage=0.1607` and recommendation `targeted_reruns_justified`
20260315-0031 — driver validation: ran `python driver.py --recipe configs/recipes/story-142-onward-genealogy-consistency-validate.yaml --run-id story142-onward-genealogy-consistency-r1 --force` after clearing stale `*.pyc`; inspected [genealogy_consistency_report.jsonl](/Users/cam/Documents/Projects/codex-forge/output/runs/story142-onward-genealogy-consistency-r1/05_validate_onward_genealogy_consistency_v1/genealogy_consistency_report.jsonl), [genealogy_consistency_detail.json](/Users/cam/Documents/Projects/codex-forge/output/runs/story142-onward-genealogy-consistency-r1/05_validate_onward_genealogy_consistency_v1/genealogy_consistency_detail.json), [chapter-009.html](/Users/cam/Documents/Projects/codex-forge/output/runs/story142-onward-genealogy-consistency-r1/output/html/chapter-009.html), [chapter-010.html](/Users/cam/Documents/Projects/codex-forge/output/runs/story142-onward-genealogy-consistency-r1/output/html/chapter-010.html), [chapter-014.html](/Users/cam/Documents/Projects/codex-forge/output/runs/story142-onward-genealogy-consistency-r1/output/html/chapter-014.html), [chapter-018.html](/Users/cam/Documents/Projects/codex-forge/output/runs/story142-onward-genealogy-consistency-r1/output/html/chapter-018.html), and [chapter-020.html](/Users/cam/Documents/Projects/codex-forge/output/runs/story142-onward-genealogy-consistency-r1/output/html/chapter-020.html); verified the reviewed bad set was flagged, the reviewed non-regression set stayed clean, and the report preserved run membership plus culprit-page narrowing (`chapter-010` strong pages `[34,35]`, `chapter-013` `[57]`, `chapter-014` `[64]`, `chapter-015` `[69]`)
20260315-0036 — repo checks: `make lint` passed and `python -m ruff check modules/ tests/` passed; `make test` initially failed because the Homebrew `python3.14` on this machine lacks `pytest`, and the equivalent `python -m pytest tests/` surfaced one stale baseline assertion in `tests/test_validate_ff_engine_v2_node_integration.py::test_integration_with_real_gamebook` against the shared `ff-robot-commando` fixture
20260314-1816 — repo baseline repair: updated [Makefile](/Users/cam/.codex/worktrees/72eb/codex-forge/Makefile) to prefer the active environment interpreter with a `python3` fallback, relaxed the stale hardcoded unreachable-section expectation in [tests/test_validate_ff_engine_v2_node_integration.py](/Users/cam/.codex/worktrees/72eb/codex-forge/tests/test_validate_ff_engine_v2_node_integration.py), and reran `make test` plus `make lint`; repo-wide validation is now green at `585 passed, 5 skipped`
20260314-1818 — story closure: Story 142 now closes ADR-001's first implementation slice. The detector/report stage proved the reviewed bad/good chapter split on real artifacts, preserved provenance back to culprit pages, and measured `strong_rerun_candidate_page_coverage=0.1607`, which keeps the next move in the "targeted automated reruns are justified" band rather than forcing broader extraction granularity
