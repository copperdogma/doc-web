# Story 165 — Benchmark `Marker` as a Breadth Comparator on the `born-digital-pdf` Gap

**Priority**: High
**Status**: Draft
**Ideal Refs**: Requirement #1 (Ingest), Requirement #5 (Structure), Requirement #6 (Validate), Any format, any condition, Dossier-ready output, Traceability is the Product
**Spec Refs**: spec:1 (spec:1.1, C2), spec:3 (spec:3.1, C3), spec:6, spec:7
**Build Map Refs**: Category 1 Intake & Format Routing (`partial`, C2 `climb`); Category 3 Layout & Structure Understanding (`exists`, C3 `climb`); Category 7 Graduation & Dossier Handoff (`partial`); Input Coverage row `born-digital-pdf` is currently high-priority untested and is the first honest breadth seam for `Marker`
**Decision Refs**: `docs/scout/scout-011-external-document-ingestion-systems.md`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md`, `docs/stories/story-157-pdf-intake-parity-with-image-directory-inputs.md`, `docs/stories/story-164-surya-component-benchmark-for-layout-and-table-seams.md`, `docs/build-map.md`
**Depends On**: Story 156, Story 164

## Goal

Evaluate whether `Marker` is worth pursuing as the next external breadth
comparator after the `Docling` and `Surya` tracks closed negative on the
active Onward seam. This story should not assume adoption. It should first pin
the real runtime and licensing posture, then benchmark `Marker` on the
high-priority `born-digital-pdf` gap using a repo-owned embedded-text fixture
instead of another genealogy kill test. The output should answer one question:
does `Marker` close enough of the current born-digital PDF gap, with strong
enough structure and traceability signals, to justify a follow-on integration
story or a broader multi-format probe?

## Acceptance Criteria

- [ ] The benchmark substrate is pinned before any adoption claim:
  - exact install/runtime path is recorded (isolated venv, container, or other bounded environment)
  - current code-license, model-license, and optional LLM-service posture are summarized from primary sources
  - the story names the explicit stop rule if the legal/runtime shape is already too awkward for a bounded benchmark
- [ ] A narrow `Marker` benchmark exists on the `born-digital-pdf` gap:
  - mandatory first lane is repo-owned `testdata/tbotb-mini.pdf`
  - the benchmark writes inspectable markdown/json/html artifacts under `output/runs/`
  - artifacts are manually inspected for text fidelity, structure quality, image handling, and provenance-like metadata
- [ ] The benchmark compares `Marker` honestly against the current repo state:
  - compare `Marker` against the current OCR-routed baseline or other maintained local baseline for the same PDF
  - explicitly state whether `Marker` meaningfully reduces pressure on the untested `born-digital-pdf` gap instead of only producing nicer-looking exports
  - explicitly state whether any missing provenance or licensing constraints block real adoption even if output quality looks strong
- [ ] The story ends with a single decision:
  - if `Marker` wins materially and modularly, create the next follow-on story and name the exact seam it should own
  - if `Marker` does not win cleanly, update Scout 011 and other tracking docs only as needed and stop

## Out of Scope

- Reopening the closed `Docling` or `Surya` decisions on the Onward seam
- Benchmarking `Marker` on Leonidas, Marie-Louise, or the other reviewed genealogy hard lanes first
- Quietly adopting GPL code or restricted model weights into the maintained runtime without an explicit follow-on decision
- Running a broad vendor bake-off with `OCRmyPDF` or `GROBID` in the same story
- Claiming `docx`, `xlsx`, `pptx`, or `epub` support unless the benchmark actually proves those lanes with repo-owned fixtures

## Approach Evaluation

- **Simplification baseline**: the active build-map already says `born-digital-pdf` is high-priority and untested while the current path is wastefully OCR-routed. `Marker` is only worth touching if it closes this gap faster or more honestly than extending the incumbent route ourselves.
- **AI-only**: not the right primary question. This is a converter/runtime comparison problem, not a prompt-tuning problem. The relevant question is whether a full external converter can cheaply pressure an unbuilt format seam.
- **Hybrid**: the leading candidate. Run `Marker` in an isolated runtime, collect markdown/json/html outputs plus any stats/debug metadata, and compare them against the current repo expectations for structure and provenance without wiring `Marker` into the maintained runtime.
- **Pure code**: acceptable only for orchestration, artifact conversion, benchmark reporting, and optional helper scripts. Do not build a shadow runtime around `Marker` before it wins a narrow benchmark.
- **Repo constraints / prior decisions**: Scout 011 positions `Marker` as a breadth comparator, not a first adoption target. ADR-002 keeps `doc-web` as the runtime boundary. ADR-003 closed the `Docling` replacement track on the Onward seam and shifted external-tool work toward bounded benchmarks and pattern-poaching. Story 157 explicitly keeps `born-digital-pdf` separate from the scanned-PDF parity problem.
- **Existing patterns to reuse**: Story 164's isolated-benchmark discipline, `testdata/tbotb-mini.pdf`, `testdata/README.md`, the `doc-web` bundle smoke surfaces under `tests/fixtures/doc_web_bundle_smoke/`, and any existing OCR-routed PDF recipe or smoke path that can serve as the local baseline.
- **Eval**: the deciding proof is whether `Marker` can pressure the `born-digital-pdf` row honestly:
  - does it preserve embedded-text content at least as well as the current OCR-routed path?
  - does its JSON/HTML output expose enough structure to be useful to `doc-web` or Dossier-facing export work?
  - does its licensing and provenance posture still make adoption plausible after inspection?
  If the answer is only "the markdown looks nice," that is not enough.

## Tasks

- [ ] Verify the missing substrate before promotion out of `Draft`:
  - confirm a bounded local `marker-pdf` runtime can be installed without contaminating the default repo runtime
  - record the current code-license, model-license, and optional LLM-service posture from primary sources plus local package metadata
  - record the real blockers that would keep this story in `Draft` (for example, unusable runtime setup, missing model downloads, or irreconcilable license posture)
- [ ] Freeze the benchmark shape before coding:
  - mandatory first lane is `born-digital-pdf` on `testdata/tbotb-mini.pdf`
  - incumbent comparison surface is the current OCR-routed local path for the same PDF plus manual inspection against the source text extracted from the embedded text layer
  - define the exact success and stop criteria for "breadth comparator win," including what provenance or metadata must exist for the result to matter
- [ ] Implement the smallest honest benchmark harness:
  - prefer a story-local spike under `scripts/spikes/`
  - only touch shared benchmark/scorer surfaces if reuse is clearly cleaner than story-local glue
  - avoid changes to the maintained runtime unless the benchmark result already justifies a second story
- [ ] Run the benchmark in the isolated runtime, write artifacts under `output/runs/`, and manually inspect representative outputs
- [ ] Publish the result:
  - update Scout 011 with the measured `Marker` read
  - update `docs/build-map.md` only if the result changes next-step prioritization or format-coverage strategy
  - create a follow-on integration story only if the win is real and scoped
- [ ] If this story changes documented format coverage or graduation reality: update `docs/build-map.md` and record the before/after state honestly
- [ ] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [ ] Run required checks for touched scope:
  - [ ] Default Python checks: `make test`
  - [ ] Default Python lint: `make lint`
  - [ ] If pipeline behavior changed: clear stale `*.pyc`, run through the narrowest real `driver.py` path or spike harness, verify artifacts in `output/runs/`, and manually inspect sample data
  - [ ] If agent tooling changed: `make skills-check`
- [ ] If evals or goldens changed: run `/improve-eval` and update `docs/evals/registry.yaml`
- [ ] Search all docs and update any related to what we touched
- [ ] Verify Central Tenets:
  - [ ] T0 — Traceability: benchmark artifacts name the exact runtime, input file, and output paths, and explicitly record any provenance gaps
  - [ ] T1 — AI-First: benchmark the external AI-rich converter before writing new local born-digital PDF logic
  - [ ] T2 — Eval Before Build: measure `Marker` before proposing any integration work
  - [ ] T3 — Fidelity: compare output against the actual embedded-text PDF content, not just cosmetic formatting
  - [ ] T4 — Modular: keep the work isolated to a benchmark harness plus tracking docs
  - [ ] T5 — Inspect Artifacts: manually inspect the emitted markdown/json/html, not just logs

## Workflow Gates

- [ ] Build complete: implementation finished, required checks run, and summary shared
- [ ] Validation complete or explicitly skipped by user
- [ ] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: external benchmark harnesses and external-systems tracking. The likely owners are `scripts/spikes/`, this story file, and Scout 011; maintained runtime modules should stay untouched in the first pass.
- **Build-map reality**: Category 1 remains `partial` / `climb`, and `born-digital-pdf` is still high-priority untested. Category 7 remains partial because the repo does not yet have a proven Dossier-facing path for born-digital PDF intake. This story is a benchmark against those gaps, not a shipping-format story.
- **Substrate evidence**: verified locally that the default repo runtime has no `marker-pdf` package (`python -m pip show marker-pdf` fails) and no importable `marker` module. Verified repo-owned benchmark input exists at `testdata/tbotb-mini.pdf`, that `pdffonts` shows embedded `Helvetica` fonts, and that `pdftotext` extracts coherent text from the fixture. This means the format lane is real while the external runtime substrate is still missing.
- **Data contracts / schemas**: no repo schema changes are expected in the first benchmark pass. If the story graduates into a maintained integration probe later, any new cross-artifact fields must be added to `schemas.py` before code emits them.
- **File sizes**: `docs/build-map.md` is 543 lines, so update it only if the benchmark changes coverage strategy materially. `docs/scout/scout-011-external-document-ingestion-systems.md` is 173 lines. `docs/stories.md` is 173 lines. `docs/stories/story-157-pdf-intake-parity-with-image-directory-inputs.md` is 154 lines. `testdata/README.md` is 7 lines. The new story file and any new spike script should stay small and bounded.
- **Decision context**: reviewed `docs/ideal.md`, `docs/build-map.md`, Scout 011, ADR-002, ADR-003, Story 157, and Story 164. No new ADR is needed at story-creation time; create one later only if a `Marker` result would alter the accepted runtime boundary or introduce a real licensing-policy decision.

## Files to Modify

- `docs/stories/story-165-marker-breadth-comparator-born-digital-pdf.md` — benchmark story scaffold and result log (new file)
- `docs/stories.md` — story index row for Story 165 (173 lines)
- `scripts/spikes/marker_breadth_benchmark.py` — isolated benchmark harness for the chosen lane(s) (new file)
- `docs/scout/scout-011-external-document-ingestion-systems.md` — record the active `Marker` benchmark path and later the measured result (173 lines)
- `docs/build-map.md` — update only if the benchmark changes format-coverage or next-step reality materially (543 lines)
- `docs/evals/registry.yaml` — only if the benchmark graduates into a durable eval surface
- `testdata/README.md` — only if the fixture usage needs to be documented more explicitly for this benchmark (7 lines)

## Redundancy / Removal Targets

- The current assumption that `Marker` is only a vague future breadth comparator with no concrete benchmark path
- Any one-off benchmark glue that survives after a clearly negative result
- Any premature adoption stories that appear before the first bounded benchmark win

## Notes

- `Marker` should not repeat the Onward seam unless it first wins on a breadth-oriented format gap where its full-converter posture is actually the point.
- `testdata/tbotb-mini.pdf` is currently the best repo-owned first lane because it is small, multi-page, and exposes embedded text directly (`pdffonts` shows `Helvetica`; `pdftotext` produces coherent section text).
- Current official README claims `marker-pdf` can convert PDF, image, PPTX, DOCX, XLSX, HTML, and EPUB into markdown, JSON, chunks, and HTML; can use custom processors/renderers; and can optionally boost quality with `--use_llm`. The same README also says the code is GPL and the model weights use a modified Open Rail-style license.
- Current local runtime evidence is still mixed, not promotion-grade:
  - `.venv-story165-marker` on Python `3.14.3` installs current `marker-pdf 1.10.2`, but `marker_single` fails immediately with a Pillow native symbol error (`_jpeg_resync_to_restart`) before even printing `--help`
  - `.venv-story165-marker311` on Python `3.11.13` resolves only by backtracking to legacy `marker-pdf 0.2.6` + `surya-ocr 0.4.5`, and the first `marker_single --help` / `tbotb-mini.pdf` smoke attempts produced no output or artifacts before manual termination
- Local interpreter/arch reality matters here:
  - available Python `3.11` binaries on this machine are both `x86_64` (`/usr/local/bin/python3.11` and `/Users/cam/miniconda3/bin/python`)
  - the only local `arm64` Python is `3.14`, which is currently where the current `marker-pdf 1.10.2` stack fails in Pillow
  - Docker is installed and the daemon is reachable, so a pinned container remains the strongest unresolved substrate candidate if host runtimes stay unstable
- Keep this story in `Draft` until a bounded runtime both installs and responds cleanly enough to prove the benchmark lane is executable on this machine.

## Plan

Pending only after runtime proof — `/build-story` should first verify a bounded
local `marker-pdf` runtime that actually starts cleanly on this machine. The
current evidence is not enough: Python `3.14` installs current `1.10.2` but
fails in Pillow before CLI startup, while Python `3.11` only resolves to
legacy `0.2.6` and still did not produce prompt CLI output or artifacts in the
first smoke pass. Docker is reachable and may provide the cleanest remaining
runtime path, but that substrate is not proven yet either. If the runtime
problem is not solved, keep the story in `Draft` or re-scope it before
building. If the substrate becomes real, the first build should stay narrow:
single-file benchmark, manual artifact inspection, and one clear keep/advance
decision.

## Work Log

20260321-0957 — story created: scoped `Marker` as the next bounded external
breadth comparator after Story 164 closed negative on the active Onward seam.
Evidence: Scout 011 now places `Marker` as the next unbenchmarked broad
comparator, the build map still lists `born-digital-pdf` as high-priority
untested, the default repo runtime has no `marker-pdf` substrate
(`python -m pip show marker-pdf` and `importlib.util.find_spec('marker')`
both fail), and the repo-owned fixture `testdata/tbotb-mini.pdf` is a real
embedded-text PDF (`pdffonts` shows `Helvetica`; `pdftotext` extracts coherent
text). Next step: `/build-story` should verify isolated install/licensing
reality before promoting this out of `Draft`.
20260321-1108 — runtime probe: the benchmark lane is real, but the local
`Marker` substrate is still not promotion-grade. Evidence: `.venv-story165-marker`
using Python `3.14.3` installed `marker-pdf 1.10.2` plus `surya-ocr 0.17.1`,
but `marker_single --help` and the first `tbotb-mini.pdf` smoke both failed
immediately with Pillow's `_jpeg_resync_to_restart` symbol error. A Python
`3.11.13` retry in `.venv-story165-marker311` only resolved by backtracking to
legacy `marker-pdf 0.2.6` plus `surya-ocr 0.4.5`; `marker_single --help` and a
`tbotb-mini.pdf` smoke run then sat without output or artifacts until manually
terminated. Next step: keep the story in `Draft` until a bounded runtime both
installs and responds cleanly enough to prove the benchmark can actually run.
20260325-1157 — deeper runtime probe: host substrate is still ambiguous, but
the exact shape is clearer now. Evidence: both available Python `3.11`
interpreters on this machine are `x86_64`, while the only `arm64` interpreter
is Python `3.14`. Rebuilding Pillow from source inside `.venv-story165-marker`
did not rescue the current `marker-pdf 1.10.2` arm64 stack; the same
`_jpeg_resync_to_restart` failure persists on `marker_single --help` and the
`tbotb-mini.pdf` smoke. Docker is installed and the daemon is reachable
(`docker ps` succeeds), so a pinned container is now the strongest remaining
substrate candidate, but even the first `python:3.11-slim` pull is not yet
proven in this pass. Next step: keep Story 165 in `Draft`, and treat a clean
containerized runtime as the next honest promotion gate.
