# Story 164 — Benchmark `Surya` as a Component Candidate for Layout and Table Seams

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #1 (Ingest), Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Traceability is the Product, Fidelity to the source, Any format, any condition, Dossier-ready output
**Spec Refs**: spec:2 (spec:2.1, C1), spec:3 (spec:3.1, C3), spec:5 (spec:5.1, C7), spec:6
**Build Map Refs**: Category 2 OCR & Text Extraction (`exists`, C1 `climb`); Category 3 Layout & Structure Understanding (`exists`, C3 `climb`); Category 5 Document Consistency Planning (`exists`, C7 `climb`) as the downstream scoreboard; Input Coverage row `scanned-pdf-tables` is the active hard-case lane to pressure first
**Decision Refs**: `docs/scout/scout-011-external-document-ingestion-systems.md`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md`, `docs/stories/story-127-ocr-model-eval-genealogy.md`, `docs/stories/story-131-onward-table-structure-fidelity.md`, `docs/stories/story-149-onward-scanned-genealogy-collapse-implementation.md`, `docs/stories/story-163-docling-plugin-onward-golden-kill-test.md`, `docs/build-map.md`
**Depends On**: Story 127, Story 131, Story 149, Story 163

## Goal

Evaluate whether `Surya` is the strongest next external component worth
poaching into `doc-web` after the `Docling` track closed. This story should
not assume adoption. It should pin the exact licensing/runtime posture, choose
the smallest honest benchmark surface on the active `scanned-pdf-tables` lane,
and compare `Surya` against the incumbent layout/table path using existing
goldens and reviewed hard cases where possible. The outcome must be singular:
either `Surya` shows a modular upstream win large enough to justify a follow-on
integration story, or the repo records that `Surya` is not worth near-term
adoption on this seam.

## Acceptance Criteria

- [x] The benchmark substrate is pinned before any adoption claims:
  - exact install/runtime path is recorded (isolated venv, container, or other bounded environment)
  - current license posture is summarized from primary sources for both code and weights
  - the story names the explicit stop rule if the legal/runtime shape is already too awkward for a bounded benchmark
- [x] A narrow `Surya` component benchmark exists on the active genealogy/table seam:
  - mandatory benchmark surface is the `scanned-pdf-tables` lane with current reviewed Onward evidence
  - the benchmark uses existing goldens/scorers where they fit, or adds the smallest new harness needed without broadening the evaluation scope
  - artifacts are written under `output/runs/` and manually inspected
- [x] The benchmark result is compared against the current incumbent honestly:
  - compare against the current `doc-web` path on at least one hard reviewed lane
  - focus on layout/order/table structure quality, not just raw OCR text
  - explicitly state whether the result reduces pressure on `table_rescue_onward_tables_v1` or other active workaround ownership
- [x] The story ends with a single decision:
  - if `Surya` wins materially and modularly, create the next follow-on integration story and name the exact seam it should own
  - if `Surya` does not win cleanly, update the scout/build-map surfaces only as needed and stop without opening speculative adoption work

## Out of Scope

- Replacing `doc-web` as the accepted boundary
- Running a broad vendor bake-off with `Marker`, `OCRmyPDF`, or `GROBID` in the same story
- Quietly adopting GPL-bound code or model assets into the maintained runtime without an explicit follow-on decision
- Rebuilding the full Onward pipeline around `Surya` before a narrow benchmark win exists
- Changing Dossier or Storybook integration surfaces

## Approach Evaluation

- **Simplification baseline**: the current repo already has an incumbent answer on the active lane: `doc-web` plus the reviewed Story 149 slice and the `onward-table-fidelity` benchmark surface. `Surya` is only worth touching if it can beat or simplify that owned path enough to justify the extra dependency and license posture.
- **AI-only**: not the right primary question. The repo already benchmarked model-first OCR/table paths in Stories 127 and 131. This story is about whether a lower-level OCR/layout/table engine can improve the substrate that our current downstream modules consume.
- **Hybrid**: the leading candidate. Run `Surya` in an isolated runtime, produce page- or lane-level artifacts, and compare them against the current `doc-web` outputs or feed them into the smallest existing downstream normalization surface that makes the comparison honest.
- **Pure code**: acceptable only for orchestration, artifact conversion, benchmark reporting, and isolated install helpers. It should not turn into a parallel runtime or a shadow implementation of the whole pipeline.
- **Repo constraints / prior decisions**: Scout 011 says `Surya` is the strongest next external component candidate, but also flags GPL and model-license scrutiny as the blocker. ADR-002 keeps `doc-web` as the runtime boundary. ADR-003 closes the `Docling` replacement track and shifts the strategic posture toward poaching useful lower-level components rather than forcing a boundary swap.
- **Existing patterns to reuse**: `benchmarks/tasks/onward-table-fidelity.yaml`, `benchmarks/scorers/html_table_diff.py`, the reviewed Story 149 slice under `benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/`, `modules/adapter/table_rescue_onward_tables_v1/`, and the existing artifact-inspection rhythm from Stories 127, 131, 149, and 163.
- **Eval**: the decisive proof is not generic OCR speed or marketing claims. It is whether `Surya` materially improves the active genealogy/table seam on reviewed Onward evidence while staying modular enough to adopt. Existing `onward-table-fidelity` assets are the first reuse target, but this story must treat them honestly: the checked-in scorer/goldens exist while the legacy raw `input/onward-to-the-unknown-images/` image paths do not exist in this worktree. Reuse the committed goldens and repo-local run artifacts where possible, and add only the smallest benchmark harness needed.

## Tasks

- [x] Verify the missing substrate before promotion out of `Draft`:
  - confirmed a bounded local runtime exists without contaminating the default repo runtime: `.venv-story164-surya-045` with `surya-ocr==0.4.5` plus `numpy<2`
  - recorded current code-license and weight-license posture from Scout 011's refreshed primary-source review plus local package metadata
  - recorded the real blockers that narrow this story: current upstream `surya-ocr==0.17.1` is not locally runnable yet, and the old promptfoo raw-image paths under `input/onward-to-the-unknown-images/` are absent in this worktree
- [x] Freeze the benchmark shape before coding:
  - mandatory first lane is Marie-Louise on `scanned-pdf-tables`, using repo-local page images from `output/runs/story163-docling-plugin-killtest-r2/marie-louise/.../images/page-*.png`
  - incumbent comparison surface is the current reviewed `doc-web` slice under `benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/` plus the committed Onward goldens and per-page HTML under `benchmarks/golden/onward/`
  - define the exact success / stop criteria for “modular component win,” with layout/order first and table-CLI widening only if a runnable current-package substrate appears during the story
- [x] Implement the smallest honest benchmark harness:
  - prefer a spike script or isolated benchmark helper
  - only touch shared scorer/benchmark files if reuse is clearly cleaner than story-local glue
  - avoid changes to the maintained runtime unless the benchmark result already justifies a second story
- [x] Run the benchmark in the isolated runtime, write artifacts under `output/runs/`, and manually inspect representative outputs
- [x] Publish the result:
  - update Scout 011 with the measured `Surya` read
  - update `docs/build-map.md` only if the result changes next-step prioritization or seam strategy
  - create a follow-on integration story only if the win is real and scoped
- [x] If this story changes documented format coverage or graduation reality: updated `docs/build-map.md` to record the negative Surya result and the unchanged Onward boundary reality
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; removed the stale "Surya is still queued on this seam" assumption from Scout 011 and the build-map narrative
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: ran `python scripts/spikes/surya_component_benchmark.py`, verified artifacts under `output/runs/story164-surya-benchmark-r1/`, and manually inspected `summary.json`, `input-pages/results.json`, and `surya_layout.stderr.log`
  - [x] If agent tooling changed: not applicable; no agent tooling changed
- [x] If evals or goldens changed: not applicable; no evals or goldens changed
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: benchmark artifacts name the exact runtime, input pages, logs, and per-page box outputs under `output/runs/story164-surya-benchmark-r1/`
  - [x] T1 — AI-First: the work stayed benchmark-first and did not build a new deterministic replacement stack after the negative result
  - [x] T2 — Eval Before Build: measured Surya on the active Marie-Louise hard lane before proposing any integration story
  - [x] T3 — Fidelity: the benchmark consumed repo-local source page images and compared against reviewed gold pages without silent normalization
  - [x] T4 — Modular: kept the work isolated to a spike script plus tracking docs; no maintained runtime wiring was added
  - [x] T5 — Inspect Artifacts: manually inspected `output/runs/story164-surya-benchmark-r1/marie-louise/surya-layout-v045/summary.json`, `output/runs/story164-surya-benchmark-r1/marie-louise/surya-layout-v045/input-pages/results.json`, and `output/runs/story164-surya-benchmark-r1/marie-louise/surya-layout-v045/surya_layout.stderr.log`

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: external benchmark harness plus the external-tools/scouting surfaces. This story should prove or reject a component candidate, not mutate the core runtime by default.
- **Build-map reality**: this is primarily Category 2 and Category 3 work, judged against the active `scanned-pdf-tables` lane. Category 5 matters because the downstream consistency/planning stack is the current workaround surface that a better upstream component might narrow.
- **Substrate evidence**: verified there is no current maintained `Surya` wiring in repo code (`rg` finds scout/docs references plus one historical note), so this remains an isolated benchmark story. Verified a bounded local runtime does exist: `.venv-story164-surya-045` runs `surya_layout`, `surya_detect`, `surya_ocr`, and `surya_order` after pinning `surya-ocr==0.4.5` and `numpy<2`, with smoke artifacts at `output/runs/story164-surya-smoke-r2/tbotb-mini/results.json` and real Onward layout output at `output/runs/story164-surya-marie-layout-r1/page-004/results.json` (2 boxes, first labeled `Table`). Verified the current upstream package is still partially blocked locally: `.venv-story164-surya-arm64` installs `surya-ocr==0.17.1` and exposes `surya_table`, but the CLI fails on this machine with a Pillow symbol error; clean x86 install of `0.17.1` is blocked by unavailable `torch>=2.7`. Verified the incumbent benchmark/evidence substrate does exist: `benchmarks/tasks/onward-table-fidelity.yaml`, `benchmarks/scorers/html_table_diff.py`, the reviewed Story 149 slice, committed Onward goldens under `benchmarks/golden/onward/`, and repo-local Onward page images under prior run artifacts such as `output/runs/story163-docling-plugin-killtest-r2/marie-louise/.../images/page-004.png`. The direct promptfoo raw-image paths under `input/onward-to-the-unknown-images/` are missing in this worktree, so the benchmark must anchor to repo-local artifacts instead of that stale path.
- **Data contracts / schemas**: prefer story-local or spike-local artifacts first. No shared schema change is expected unless a benchmark win graduates into a maintained integration story.
- **File sizes**: `docs/build-map.md` is 524 lines, `docs/scout/scout-011-external-document-ingestion-systems.md` is 170 lines, `benchmarks/tasks/onward-table-fidelity.yaml` is 61 lines, `benchmarks/scorers/html_table_diff.py` is 212 lines, `modules/adapter/table_rescue_onward_tables_v1/main.py` is 1434 lines, `tests/test_table_rescue_onward_tables_v1.py` is 518 lines, and `docs/stories/story-149-onward-scanned-genealogy-collapse-implementation.md` is 211 lines. Do not casually deepen the existing 1434-line workaround module during the first benchmark pass.
- **Decision context**: reviewed `docs/ideal.md`, `docs/build-map.md`, Scout 011, ADR-002, ADR-003, Story 127, Story 131, Story 149, and Story 163. No new ADR is needed at story-creation time; create one later only if a `Surya` result would alter accepted runtime or licensing posture materially.

## Files to Modify

- `docs/stories/story-164-surya-component-benchmark-for-layout-and-table-seams.md` — benchmark story scaffold and result log (new file)
- `scripts/spikes/surya_component_benchmark.py` — isolated benchmark harness and report writer for the chosen lane(s) (new file)
- `benchmarks/tasks/onward-table-fidelity.yaml` — reuse or adapt the existing Onward table benchmark surface only if it fits the component benchmark honestly (61 lines)
- `benchmarks/scorers/html_table_diff.py` — extract shared scoring helpers only if reuse is cleaner than story-local code (212 lines)
- `docs/scout/scout-011-external-document-ingestion-systems.md` — record the measured `Surya` result and next-step recommendation (170 lines)
- `docs/build-map.md` — update the external benchmark/readiness read only if the result changes roadmap priority (524 lines)
- `docs/evals/registry.yaml` — only if the benchmark graduates into a durable eval surface
- `modules/adapter/table_rescue_onward_tables_v1/main.py` — only if a benchmark win is strong enough to justify a narrowly scoped side-by-side integration probe; do not touch in the first pass (1434 lines)

## Redundancy / Removal Targets

- The current assumption that `Surya` is the strongest next external component candidate without any local measured proof
- Any one-off benchmark glue that survives after a clearly negative result
- Any premature follow-on adoption stories if the benchmark does not show a modular win

## Notes

- This story is intentionally narrower than the closed `Docling` chain. It is a component benchmark, not a boundary-replacement investigation.
- The legal/runtime gate is real. If the install or license posture already makes bounded local benchmarking awkward, that is a valid negative result for this story.
- Preferred first comparison surface is the active Onward `scanned-pdf-tables` lane because it already has goldens, reviewed evidence, and a large owned workaround stack.
- The first honest local runtime is not the latest upstream package. Current worktree evidence supports a bounded benchmark on pinned `surya-ocr==0.4.5`; it does not yet support claiming that `surya-ocr==0.17.1` is runnable here.
- The first honest local benchmark input is not the legacy `input/onward-to-the-unknown-images/` folder. Use repo-local reviewed artifacts and extracted Onward page images already under `output/runs/`.

## Plan

1. Pin the benchmark substrate explicitly.
   Use `.venv-story164-surya-045` as the benchmark runtime because it is the only clean local Surya environment verified to run here in this pass. Record the mismatch against current upstream `0.17.1` rather than hand-waving it away. Done for this phase means the story, work log, and any benchmark helper all point to the same runtime and stop rule.
2. Freeze the first benchmark lane around repo-local Marie-Louise artifacts.
   Start with `output/runs/story163-docling-plugin-killtest-r2/marie-louise/.../images/page-*.png` as the raw page substrate, because those artifacts exist locally and correspond to the active Onward hard seam. Use `benchmarks/golden/onward/marie_louise.html`, the per-page committed goldens under `benchmarks/golden/onward/per_page/`, and the reviewed Story 149 slice as the scoreboards where they fit. Done for this phase means the story names the exact paths and comparison shape before any benchmark code lands.
3. Build the smallest honest harness.
   Prefer a story-local spike under `scripts/spikes/` that shells out to `surya_layout` and, if a runnable current-package substrate appears, optionally widens to `surya_table`. Do not create maintained runtime wiring. The harness should emit traceable JSON/summary artifacts under `output/runs/` and compare Surya's layout/table signals against the incumbent seam without pretending the old promptfoo image-list task can run unchanged here.
4. Use a strict stop rule.
   A win is only real if Surya materially improves the active layout/table seam in a way that plausibly narrows `table_rescue_onward_tables_v1` or adjacent workaround ownership. If the result only produces interesting boxes, depends on the broken `0.17.1` runtime, or cannot be compared honestly against the reviewed Onward slice, stop the story as negative and update the scout/build-map surfaces only.

## Work Log

20260320-2237 — story created: scoped `Surya` as the next bounded external component benchmark after Scout 011 and the closed `Docling` chain. Evidence: Scout 011 now marks `Surya` as the strongest next candidate, `docs/build-map.md` still shows `C1`/`C3`/`C7` in `climb`, the repo already has Onward benchmark/golden surfaces (`benchmarks/tasks/onward-table-fidelity.yaml`, Story 149 reviewed slice), and current `rg` confirmed there is no actual `Surya` runtime/config substrate in the repo yet. Next step: `/build-story` should verify isolated install/licensing reality before promoting this out of `Draft`.
20260320-2358 — draft promotion pass: verified the isolated substrate honestly enough to promote this story to `Pending`, but only with a narrower benchmark contract. Evidence: `python -m pip show surya-ocr` in the default environment shows `0.4.5` / `GPL-3.0-or-later`; a clean bounded venv at `.venv-story164-surya-045` runs `surya_layout` successfully after pinning `numpy<2`, writing `output/runs/story164-surya-smoke-r2/tbotb-mini/results.json`, and the same runtime also runs on a real Onward artifact at `output/runs/story164-surya-marie-layout-r1/page-004/results.json` where the first box is labeled `Table`. Current upstream `surya-ocr==0.17.1` is still locally partial: `.venv-story164-surya-arm64` installs and exposes `surya_table`, but the CLI fails on this machine with a Pillow symbol error; clean x86 install of `0.17.1` is blocked by unavailable `torch>=2.7`. The checked-in `benchmarks/tasks/onward-table-fidelity.yaml` scorer/goldens still exist, but its raw `input/onward-to-the-unknown-images/...` image paths do not exist in this worktree. Verified repo-local benchmark inputs do exist under prior run artifacts, especially `output/runs/story163-docling-plugin-killtest-r2/marie-louise/.../images/page-*.png`, and the reviewed Story 149 slice plus committed Onward goldens remain available under `benchmarks/golden/onward/`. Files likely to change when the story builds: this story file, `docs/stories.md`, a story-local spike under `scripts/spikes/`, Scout 011, and possibly the build map if the result materially changes priority. Files at risk: `benchmarks/tasks/onward-table-fidelity.yaml` and `benchmarks/scorers/html_table_diff.py` only if direct reuse is clearly cleaner than story-local glue. Surprise: the working local runtime is layout/order-only in practice for now, while the current upstream runtime advertises table CLI but is not runnable here; the benchmark must start layout-first and widen only if that substrate becomes real during implementation. Next step: `/build-story` can now proceed on the pinned runtime and repo-local Marie-Louise lane without pretending the missing legacy image folder is build substrate.
20260321-0037 — bounded benchmark built and came back negative for immediate Onward adoption. Implemented `scripts/spikes/surya_component_benchmark.py` as the smallest honest harness: it symlinks the overlapping Marie-Louise page images into a story-local input bundle, runs the pinned `.venv-story164-surya-045/bin/surya_layout` CLI, preserves stdout/stderr logs, summarizes page-level layout signals, and writes a traceable report at `output/runs/story164-surya-benchmark-r1/marie-louise/surya-layout-v045/summary.json`. Manual inspection confirms the result is mixed but insufficient: `page_079` is a clean true negative, `page_081` / `page_082` / `page_083` each receive one or more large `Table` boxes, but `page_080` is a hard false negative even though its gold page contains the onset genealogy table. Net result is `table_page_recall = 0.75`, `large_table_recall = 0.75`, `false_positive_pages = 0`, which is not a clean enough routing/layout win to justify even a narrow integration probe on this seam. The story therefore closes its build phase with a single decision: negative for immediate adoption on the active Onward seam. Published that read into `docs/scout/scout-011-external-document-ingestion-systems.md` and `docs/build-map.md`, shifting `Surya` from queued to benchmarked-negative on this lane. Fresh checks passed: `make lint`, `make test` (`367 passed, 12 warnings`), `python -m ruff check scripts/spikes/surya_component_benchmark.py`, `python scripts/spikes/surya_component_benchmark.py`, and `git diff --check`. Next step: `/validate`, then `/mark-story-done` if you want to close Story 164.
20260321-0118 — story closed via `/mark-story-done`: validation recommendation applied, story-specific Surya virtualenvs dropped out of the local change set via `.gitignore`, and Story 164 is now formally `Done`. Fresh closeout evidence: `python -m pytest tests/` passed (`367 passed, 12 warnings`), `python -m ruff check modules/ tests/` passed, `python scripts/spikes/surya_component_benchmark.py` still produced the negative benchmark decision at `output/runs/story164-surya-benchmark-r1/marie-louise/surya-layout-v045/summary.json`, and `git diff --check` passed. ADR alignment remains unchanged: this story reinforces ADR-003's accepted direction on the Onward seam and does not introduce a new architectural decision. Next step: `/check-in-diff`.
