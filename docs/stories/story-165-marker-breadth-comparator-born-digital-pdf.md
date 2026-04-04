---
title: Benchmark `Marker` as a Breadth Comparator on the `born-digital-pdf` Gap
status: Done
priority: High
ideal_refs:
- 'Requirement #1 (Ingest), Requirement #5 (Structure), Requirement #6 (Validate),
  Any format, any condition, Dossier-ready output, Traceability is the Product'
spec_refs:
- spec:1
- spec:1.1
- spec:3
- spec:3.1
- spec:6
- spec:7
adr_refs: []
depends_on:
- '156'
- '164'
category_refs:
- spec:1
- spec:3
- spec:6
- spec:7
compromise_refs:
- C2
- C3
input_coverage_refs:
- born-digital-pdf
architecture_domains: []
roadmap_tags: []
legacy_system: ''
---

# Story 165 — Benchmark `Marker` as a Breadth Comparator on the `born-digital-pdf` Gap

**Priority**: High
**Status**: Done
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

- [x] The benchmark substrate is pinned before any adoption claim:
  - exact install/runtime path is recorded (isolated venv, container, or other bounded environment)
  - current code-license, model-license, and optional LLM-service posture are summarized from primary sources
  - the story names the explicit stop rule if the legal/runtime shape is already too awkward for a bounded benchmark
- [x] A narrow `Marker` benchmark exists on the `born-digital-pdf` gap:
  - mandatory first lane is repo-owned `testdata/tbotb-mini.pdf`
  - the benchmark writes inspectable markdown/json/html artifacts under `output/runs/`
  - artifacts are manually inspected for text fidelity, structure quality, image handling, and provenance-like metadata
- [x] The benchmark compares `Marker` honestly against the current repo state:
  - compare `Marker` against the current OCR-routed baseline or other maintained local baseline for the same PDF
  - explicitly state whether `Marker` meaningfully reduces pressure on the untested `born-digital-pdf` gap instead of only producing nicer-looking exports
  - explicitly state whether any missing provenance or licensing constraints block real adoption even if output quality looks strong
- [x] The story ends with a single decision:
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

- [x] Verify the missing substrate before promotion out of `Draft`:
  - confirm a bounded local `marker-pdf` runtime can be installed without contaminating the default repo runtime
  - record the current code-license, model-license, and optional LLM-service posture from primary sources plus local package metadata
  - record the real blockers that would keep this story in `Draft` (for example, unusable runtime setup, missing model downloads, or irreconcilable license posture)
- [x] Freeze the benchmark shape before coding:
  - mandatory first lane is `born-digital-pdf` on `testdata/tbotb-mini.pdf`
  - incumbent comparison surface is the current OCR-routed local path for the same PDF plus manual inspection against the source text extracted from the embedded text layer
  - define the exact success and stop criteria for "breadth comparator win," including what provenance or metadata must exist for the result to matter
- [x] Implement the smallest honest benchmark harness:
  - prefer a story-local spike under `scripts/spikes/`
  - only touch shared benchmark/scorer surfaces if reuse is clearly cleaner than story-local glue
  - avoid changes to the maintained runtime unless the benchmark result already justifies a second story
- [x] Run the benchmark in the isolated runtime, write artifacts under `output/runs/`, and manually inspect representative outputs
- [x] Publish the result:
  - update Scout 011 with the measured `Marker` read
  - update `docs/build-map.md` only if the result changes next-step prioritization or format-coverage strategy
  - create a follow-on integration story only if the win is real and scoped
- [x] If this story changes documented format coverage or graduation reality: update `docs/build-map.md` and record the before/after state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through the narrowest real `driver.py` path or spike harness, verify artifacts in `output/runs/`, and manually inspect sample data
  - [x] If agent tooling changed: `make skills-check`
- [x] If evals or goldens changed: run `/improve-eval` and update `docs/evals/registry.yaml`
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: benchmark artifacts name the exact runtime, input file, and output paths, and explicitly record any provenance gaps
  - [x] T1 — AI-First: benchmark the external AI-rich converter before writing new local born-digital PDF logic
  - [x] T2 — Eval Before Build: measure `Marker` before proposing any integration work
  - [x] T3 — Fidelity: compare output against the actual embedded-text PDF content, not just cosmetic formatting
  - [x] T4 — Modular: keep the work isolated to a benchmark harness plus tracking docs
  - [x] T5 — Inspect Artifacts: manually inspect the emitted markdown/json/html, not just logs

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: external benchmark harnesses and external-systems tracking. The likely owners are `scripts/spikes/`, this story file, and Scout 011; maintained runtime modules should stay untouched in the first pass.
- **Build-map reality**: Category 1 remains `partial` / `climb`, and `born-digital-pdf` is still high-priority untested. Category 7 remains partial because the repo does not yet have a proven Dossier-facing path for born-digital PDF intake. This story is a benchmark against those gaps, not a shipping-format story.
- **Substrate evidence**: verified locally that the default repo runtime has no `marker-pdf` package (`python -m pip show marker-pdf` fails) and no importable `marker` module. Verified repo-owned benchmark input exists at `testdata/tbotb-mini.pdf`, that `pdffonts` shows embedded `Helvetica` fonts, and that `pdftotext` extracts coherent text from the fixture. Since story creation, the bounded runtime proof has become real via Docker: a `python:3.12-slim-bookworm` container works after upgrading `pip` to `26.0.1` and installing `marker-pdf 1.10.2` against the PyTorch CPU index plus PyPI, and `marker_single --help` runs successfully there. The first live `tbotb-mini.pdf` smoke starts in that container, but before any files appear under `output/runs/story165-marker-smoke-r1/` it triggers a `1.35 GB` layout-model download under `/root/.cache/datalab/models/layout/2025_09_23`. The next deeper runtime finding is that `--disable_ocr` does not keep Marker lightweight on this born-digital lane: it still triggers a second `1.34 GB` text-recognition model download, staged through `/tmp/tmp*/model.safetensors` before the final cache move, so interrupted runs waste large amounts of progress instead of resuming cleanly.
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
- Current host-runtime evidence is still mixed and should not be the maintained path:
  - `.venv-story165-marker` on Python `3.14.3` installs current `marker-pdf 1.10.2`, but `marker_single` fails immediately with a Pillow native symbol error (`_jpeg_resync_to_restart`) before even printing `--help`
  - `.venv-story165-marker311` on Python `3.11.13` resolves only by backtracking to legacy `marker-pdf 0.2.6` + `surya-ocr 0.4.5`, and the first `marker_single --help` / `tbotb-mini.pdf` smoke attempts produced no output or artifacts before manual termination
- Current bounded runtime proof is now real via Docker:
  - `python:3.12-slim-bookworm` becomes usable after upgrading `pip` to `26.0.1`
  - `marker-pdf 1.10.2` installs cleanly when `torch` is sourced from `https://download.pytorch.org/whl/cpu` instead of the default Linux wheel path
  - `marker_single --help` runs successfully in that container, proving current-package CLI startup on this machine without contaminating the repo runtime
  - the first real `tbotb-mini.pdf` smoke starts in that container, but before any output artifacts appear it triggers a `1.35 GB` layout-model download followed by a separate `1.34 GB` text-recognition model download even with `--disable_ocr`
  - the text-recognition weights stage through `/tmp/tmp*/model.safetensors` before final cache placement, so interrupted runs leave orphaned partial files and do not cheaply resume
- Local interpreter/arch reality still matters:
  - available Python `3.11` binaries on this machine are both `x86_64` (`/usr/local/bin/python3.11` and `/Users/cam/miniconda3/bin/python`)
  - the only local `arm64` Python is `3.14`, which is currently where the current `marker-pdf 1.10.2` stack fails in Pillow
  - Docker is installed and the daemon is reachable, and it is now the honest runtime path for this story rather than a hypothetical fallback
- Keep the benchmark narrow until the first-run model acquisition cost is measured honestly against the emitted artifacts. The honest stop rule is now: if `tbotb-mini.pdf` still needs multi-gigabyte warmup and the resulting metadata lacks useful page/provenance-like signals, stop after updating Scout 011/build-map rather than widening to more formats.
- Final measured read is now sharper than the original comparator framing:
  - stock `Marker` CLI is not a good adoption candidate on this machine; it eagerly drags in a multi-gigabyte model stack even for `--disable_ocr`
  - the thinner Marker-internals path is materially more interesting than the stock product: `output/runs/story165-marker-benchmark-r1/tbotb-mini/marker-v1102/summary.json` shows `1.0` heading coverage and `1.0` token coverage versus `pdftotext`, with `page_stats` and `table_of_contents` metadata present
  - the current local baseline is still wastefully OCR-routed on the same PDF: `output/runs/story165-docweb-baseline-r1/ocr_ensemble/ocr_source_histogram.json` shows all `3` pages sourced from `tesseract` even though `pdftext_text_pct = 1.0`, and `output/runs/story165-docweb-baseline-r1/ocr_ensemble/ocr_quality_report.json` still flags page `3` for escalation
  - that is enough to justify a follow-on story for a thin Marker-internals born-digital substrate, but not enough to justify stock `Marker` adoption into the maintained runtime

## Plan

Current build should use the proven container path, not the host Python paths.
The working substrate is `python:3.12-slim-bookworm` with `pip` upgraded to
`26.0.1`, `marker-pdf 1.10.2` installed against the PyTorch CPU index plus
PyPI, and `marker_single` invoked from inside that container. The first build
should stay narrow: single-file `tbotb-mini.pdf`, inspectable
markdown/json/html outputs under `output/runs/`, and one explicit decision on
whether the runtime/model footprint is still acceptable for a bounded breadth
comparator. If first-run model acquisition keeps swallowing the benchmark
without producing artifacts, re-scope around that blocker before widening to
more formats. The story-local harness should codify the proven container path
and compare Marker's emitted text against `pdftotext` output from the same
fixture so the decision stays tied to fidelity, not just presentation.

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
20260326-1545 — container runtime proof: Story 165 is no longer blocked on
"can current Marker run here at all?" Evidence: inside a bounded
`python:3.12-slim-bookworm` container, upgrading `pip` to `26.0.1` and
installing `marker-pdf 1.10.2` against `https://download.pytorch.org/whl/cpu`
plus PyPI produced a working `marker_single --help` on this machine. The host
paths remain negative (`3.14` dies in Pillow; `3.11` only resolves to legacy
`0.2.6`), so the honest runtime path is container-first. A first live
`marker_single testdata/tbotb-mini.pdf --output_dir output/runs/story165-marker-smoke-r1 --output_format json --disable_ocr --disable_multiprocessing`
smoke also started successfully in that container, but before any output
artifacts appeared it triggered a `1.35 GB` layout-model download under
`/root/.cache/datalab/models/layout/2025_09_23`. No files existed yet under
`output/runs/story165-marker-smoke-r1/` when this entry was recorded. Next
step: continue the bounded smoke from the proven container recipe, decide
whether the first-run model footprint is still acceptable for this benchmark,
then add the story-local harness and artifact inspection.
20260326-1920 — live smoke follow-up: Marker's first real born-digital run is
heavier than the initial Docker proof implied. Evidence: the detached smoke log
at `output/runs/story165-marker-smoke-r1/marker.log` shows that after the
`1.35 GB` layout model, `marker_single` still triggers a separate `1.34 GB`
text-recognition model download even with `--disable_ocr`; by the time this
entry was recorded the log had advanced to roughly `317M / 1.34G` on the active
download. Inspection inside the container showed the active text-recognition
payload staging through `/tmp/tmp32ks1fdg/model.safetensors` and an orphaned
partial file from an interrupted earlier attempt at
`/tmp/tmpwim6_3wj/model.safetensors` (`883M`), which means restarts waste
progress instead of resuming cheaply. `output/runs/story165-marker-smoke-r1/`
still contained only `marker.log`; no JSON/HTML/markdown artifacts existed yet.
Next step: let the current smoke continue uninterrupted, and land a
story-local benchmark harness so the final comparison can use the proven
container recipe instead of ad hoc shell commands.
20260326-1942 — harness landed and benchmark shape frozen: the first reusable
benchmark surface now exists at `scripts/spikes/marker_breadth_benchmark.py`.
Evidence: `python scripts/spikes/marker_breadth_benchmark.py --help` succeeds,
`python -m ruff check scripts/spikes/marker_breadth_benchmark.py` passes, and
the runtime probe baked into the script now reports the real Docker substrate:
`marker-pdf 1.10.2`, `surya-ocr 0.17.1`, `torch 2.11.0+cpu`, plus cache
signals showing a completed `1.45 GB` layout model and staged temporary
`model.safetensors` downloads under `/tmp/`. The benchmark shape is now
explicitly frozen around three output formats (`markdown`, `json`, `html`),
comparison against `pdftotext` output from the same fixture, and a stop rule
that treats multi-gigabyte warmup plus weak metadata/provenance as a negative.
The actual output-quality decision is still open because the live smoke in
`output/runs/story165-marker-smoke-r1/marker.log` had only reached about
`447M / 1.34G` on the text-recognition download and still had not emitted the
first `tbotb-mini.*` artifact. Next step: let the uninterrupted smoke finish,
then run the new harness on the warmed container to capture `markdown/json/html`
artifacts and a benchmark summary under
`output/runs/story165-marker-benchmark-r1/`.
20260326-1241 — benchmark decision landed: Story 165 now has a complete,
inspectable result instead of a substrate-only read. Evidence: the canonical
summary at `output/runs/story165-marker-benchmark-r1/tbotb-mini/marker-v1102/summary.json`
now includes both the `lite_api` Marker result and the current local baseline.
Manual inspection confirmed that Marker emitted coherent
`markdown/json/html` artifacts under
`output/runs/story165-marker-benchmark-r1/tbotb-mini/marker-v1102/lite-api/`,
with all `14 / 14` tracked headings present, `1.0` token coverage versus the
embedded text layer, `table_of_contents` polygons, and `page_stats` entries
showing `text_extraction_method = "pdftext"`. Manual inspection also confirmed
the real weaknesses: the markdown and HTML duplicate the attribution paragraph,
the rendered `Contents` heading loses its bullet list body, and the outputs do
not expose `doc-web`-grade stable block anchors or block-level provenance.
The honest local comparison is now explicit too: the current repo baseline at
`output/runs/story165-docweb-baseline-r1/ocr_ensemble/` still routed all
three pages through `tesseract` despite `pdftext_pages_with_text = 3`, and
page `3` remained flagged for escalation with a duplicated terminal line
(`YOU SURVIVE` plus `YOU SURVIVE™`) in
`ocr_ensemble/pages/page-003.json`. Decision: stock `Marker` does not earn
adoption, but the thinner Marker-internals path wins enough on born-digital
structure to justify a follow-on substrate story rather than closing this as a
pure negative. Next step: publish the measured read to Scout 011/build-map,
create the follow-on story around the thin internal seam, then run the normal
checks and close Story 165.
20260326-1245 — closeout checks complete: Story 165 is now at the normal
validation gate rather than still being implementation-open. Evidence:
`make lint` passed, `make test` passed (`367 passed, 12 warnings`), `make skills-check`
passed, and `git diff --check` passed in this validation pass. The follow-on
story now exists at `docs/stories/story-166-marker-internals-born-digital-pdf-substrate.md`,
which is the concrete redundancy-management step this benchmark earned instead
of leaving the next seam implicit. Next step: run `/validate`, then either
close Story 165 directly or rescope-then-close if validation finds any drift.
20260326-1246 — story closed: Story 165 now stands as a coherent bounded
benchmark rather than an open-ended external-tools probe. Evidence: the final
result lives in `output/runs/story165-marker-benchmark-r1/tbotb-mini/marker-v1102/summary.json`,
the current local baseline evidence lives in
`output/runs/story165-docweb-baseline-r1/ocr_ensemble/`, the tracker docs are
updated in Scout 011 and `docs/build-map.md`, and the remaining forward work is
now explicitly split into
`docs/stories/story-166-marker-internals-born-digital-pdf-substrate.md`.
Recommended next step: `/check-in-diff`.
