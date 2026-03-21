# Scout 011 — external-document-ingestion-systems

**Source:** `Docling`, `OCRmyPDF`, `Surya` + `Marker`, and `GROBID`
**Scouted:** 2026-03-20
**Scope:** Compare external document-ingestion systems for reusable patterns or components relevant to intake routing, OCR/layout, and document-consistency work (`C1`, `C2`, `C3`, `C7`), with evaluation order `Docling` → `OCRmyPDF` → `Surya`/`Marker` → `GROBID`
**Previous:** ADR-001 research notes only (`xai-research-stub`, `opus-research-stub`, `openai-research-report`)
**Status:** Complete
**Alignment:** Created from inbox triage after checking `docs/ideal.md`, `docs/spec.md`, `docs/build-map.md`, `docs/evals/registry.yaml`, and ADRs 001-002. This scout targets active `climb` seams rather than the already-landed `doc-web` boundary work.

## Findings

1. **`Docling` is the best first external benchmark for active `C1`/`C2`/`C3`/`C7` seams** — HIGH value, story-sized
   What: Official `Docling` docs describe a parameterized converter architecture, a unified `DoclingDocument` representation, supported inputs across PDF, Office, HTML, images, and schema-specific XML, supported outputs including HTML, Markdown, JSON, and doctags, plus explicit layout, reading-order, and provenance fields. `Docling` also exposes page-level and document-level confidence reports (`layout_score`, `ocr_score`, `parse_score`, `table_score`) to guide review and routing.
   Us: This is the closest external system to the shape doc-forge currently needs while `C2` intake routing, `C3` layout understanding, and `C7` inspectable consistency remain in `climb`. It is materially stronger than the current contact-sheet intake stub for benchmarking a typed document IR, but it still needs local proof on hard scans and repeated-structure books.
   Recommendation: The next approved follow-up should be a `Docling` pilot on 2-3 representative local documents. Compare its JSON/HTML/confidence outputs against current artifact expectations for traceability, table fidelity, reading order, and repeated-structure consistency.
   Transfusion:
   Exemplar: `DoclingDocument` plus `ConfidenceReport`.
   Invariant: Keep a typed, inspectable intermediate with explicit layout/provenance and quality signals instead of hiding decisions inside prompts.
   Adaptation: Treat `Docling` as a benchmarked substrate or adapter candidate, not a blind replacement for doc-forge artifacts.
   Proof target: A local pilot yields inspectable `Docling` artifacts that can be scored against current `C1`/`C3`/`C7` failure modes and either justify a build story or rule `Docling` out.

2. **`OCRmyPDF` is useful only as a narrow pre-OCR/PDF-normalization seam** — MEDIUM value, `XS`-`S`
   What: Official `OCRmyPDF` docs position it as a Python application/library that adds OCR text layers to scanned PDFs while preserving the original PDF as much as possible. It offers deskew, rotation, cleanup, PDF/A generation, sidecar text export, a Python API, and plugin hooks for alternate OCR engines and image/PDF filtering. The same docs also state its core OCR limitations: Tesseract struggles with reading order and does not emit headings, paragraphs, or structural document semantics.
   Us: That makes `OCRmyPDF` relevant to `C1` when skew, cleanup, or PDF conditioning is the real bottleneck, but not to `C2`, `C3`, or `C7`. It also comes with review caveats: some cleanup modes can visually alter pages, and the sidecar text output intentionally omits pages that already had text or were skipped.
   Recommendation: Keep `OCRmyPDF` as an optional preprocessing experiment, not a candidate replacement pipeline. Only run it when artifact inspection shows scan conditioning is the actual failure source.

3. **`Surya` is the strongest component-level benchmark if we need a better layout/order/table engine** — MEDIUM value, story-sized
   What: The official `Surya` README exposes OCR in 90+ languages, line detection, layout analysis, reading-order detection, table recognition, per-line and per-word confidence, polygons/bboxes, and page-scoped JSON outputs. `Docling`'s own docs include a `docling-surya` integration and warn that using it may impose GPL obligations.
   Us: `Surya` maps well to the repo's `C1`/`C3` rescue problems and could challenge current layout/table rescue on hard scans. But it is a lower-level component than doc-forge's current provenance-rich artifacts, and direct adoption would force a licensing and packaging decision before it even reaches quality evaluation.
   Recommendation: Use `Surya` only as a downstream benchmark or narrow rescue candidate after the `Docling` pilot, not as the first repo-wide experiment.

4. **`Marker` is the strongest off-the-shelf end-to-end comparator, but its fit is benchmark-first, not adoption-first** — MEDIUM value, story-sized
   What: The official `Marker` README says it converts PDF/image/PPTX/DOCX/XLSX/HTML/EPUB into Markdown, JSON, chunks, and HTML; removes headers/footers; extracts images; supports schema-guided structured extraction; and can raise accuracy with an optional LLM mode. It also documents that the pipeline mixes heuristics with `Surya`, and that the open-source code is GPL while model weights carry a restricted commercial license.
   Us: That makes `Marker` relevant to `C2`/`C3`/`C7`, especially because it already supports schema-shaped extraction and explicit per-page stats. But its provenance model is not obviously strong enough for doc-forge's traceability-first product bar, and its license posture is materially less attractive than `Docling` or `GROBID`.
   Recommendation: Keep `Marker` as a secondary benchmark after `Docling`, mainly to pressure-test schema-guided extraction and table quality. Do not treat it as the first adoption candidate.

5. **`GROBID` is valuable mainly as a design reference, not as the next benchmark target** — LOW value now, story-sized later
   What: Official `GROBID` docs and README describe a machine-learning library for extracting scholarly PDFs into structured TEI/XML, with coordinate annotations for selected structures and specialized "flavors" for alternate document families. The project is Apache-2.0, and the docs note that specialized processes now include domains such as standards documents in addition to standard scientific-article flows.
   Us: The coordinate-rich TEI output and explicit flavor model are useful design references, but the repo's active problems are scanned books, intake routing, and repeated genealogy structures, not scholarly metadata or citation parsing.
   Recommendation: Skip `GROBID` as an implementation target for now. Revisit only if doc-forge takes on technical/scientific PDFs or wants to borrow the flavor pattern for recipe governance.
   Transfusion:
   Exemplar: `GROBID` flavors plus coordinate-enriched TEI.
   Invariant: Format-specific variants should stay explicit and inspectable, not turn into hidden prompt branches.
   Adaptation: Keep doc-forge's YAML recipe/build-map governance, but remember `GROBID`'s flavor pattern if recipe families start multiplying.
   Proof target: If a future story introduces recipe-family specialization, it should carry visible routing plus per-structure coordinates/evidence rather than hidden one-off logic.

## Deepened Decision Surface

This section closes the remaining ambiguity after the `Docling` chain. The
question is no longer "what do these tools do?" but "what kind of ownership do
they imply inside doc-forge, and what is the smallest honest proof worth
running next?"

### `OCRmyPDF`

- **Best-fit seam:** `C1` only, and only when source-PDF conditioning is the real problem.
- **Most credible local use:** a child-process preprocessing step that deskews, rotates, normalizes to PDF/A when useful, and optionally emits a sidecar OCR text file for audit comparison.
- **Why not more:** the official docs are explicit that it rasterizes for OCR, adds an OCR layer back into the original PDF, and inherits Tesseract's inability to infer reading order, paragraphs, or headings. That makes it a scan-conditioning tool, not a structure engine.
- **Operational shape:** viable as a subprocess or narrow recipe module. The official Python API exists, but the docs recommend process isolation because the library spawns workers, uses subprocesses, and is not thread-safe for parallel runs in one interpreter.
- **Spend rule:** only spike this when manual artifact review shows skew, rotation, damaged PDFs, or text-layer conditioning are the dominant blocker. Do not use it to chase layout/table/document-consistency problems.

### `Surya`

- **Best-fit seam:** `C1` and `C3`, with possible pressure on `C2` if stronger reading order reduces routing ambiguity.
- **Most credible local use:** a bounded component benchmark against current OCR/layout/table surfaces, not a repo-wide replatform. Story 164 confirmed that this needs to start from an explicitly pinned runtime and repo-local reviewed artifacts, not from aspirational "latest package" or missing input paths.
- **Why it is the strongest next candidate:** the official README covers OCR, line detection, layout analysis, reading-order detection, and table recognition in one toolkit, which maps directly onto the parts of doc-forge we still own heavily.
- **Main blocker:** licensing and packaging. The public repo is GPL, the weights have a modified Open Rail-style license, and the project itself advertises managed API / on-prem commercial options. That means the legal posture must be explicit before we adopt code rather than merely benchmark it.
- **Measured result on the active seam:** Story 164 ran the first honest local benchmark at `output/runs/story164-surya-benchmark-r1/` using the pinned `surya-ocr==0.4.5` runtime. On the overlapping Marie-Louise hard-lane subset, Surya cleanly avoided false positives but only detected `3 / 4` gold table pages (`table_page_recall = 0.75`) and missed `page_080` entirely. Current upstream `surya-ocr==0.17.1` remains locally blocked in practice on this machine, so the table-capable runtime is not yet a real substrate here.
- **Spend rule:** do not spend more Onward-seam effort on Surya unless a runnable current-package table-capable runtime appears or a different document family makes page-routing-only wins worth adopting.

### `Marker`

- **Best-fit seam:** `C2`/`C3`/`C7` as a comparator, especially when we want to pressure-test schema-guided extraction and multi-format breadth quickly.
- **Most credible local use:** an end-to-end benchmark on a non-Onward document family where "good enough structured export" matters more than provenance-perfect genealogy repair.
- **Why it is not ahead of `Surya`:** the official README is attractive on breadth and output formats, but it is still GPL, uses restricted model weights for broader commercial use, and leans on optional LLM mode to do things like merge tables across pages. That makes it less attractive than `Surya` if the real goal is to poach one lower-level capability into `doc-web`.
- **Key read:** `Marker` is useful when we want a whole-pipeline comparator or a quick breadth check; it is not the cleanest source for a narrow substrate transplant.
- **Spend rule:** keep it behind `Surya`. Only benchmark it next if we specifically want to compare "full external converter breadth" rather than improve one owned seam.

### `GROBID`

- **Best-fit seam:** not the active scanned-book path. Its value is architectural transfusion: flavor-based specialization and coordinate-rich structured output.
- **Most credible local use:** design reference for future scientific/technical PDF work or for strengthening our own recipe-family governance and provenance model.
- **Why not now:** the official docs and README stay focused on technical/scientific publications and TEI/XML output. That is a different document family from the active genealogy/intake problems.
- **What is still worth stealing:** explicit `flavor=` routing and inspectable coordinate payloads are strong patterns for doc-forge if we later grow multiple specialized document families.
- **Spend rule:** no benchmark story unless the roadmap shifts toward scientific/technical PDFs or we need a concrete flavor-governance model for new recipe families.

## Tracking Ledger

This section is the durable tracker for the five external systems evaluated in
Scout 011. Stories own execution, ADRs own architecture-level decisions, and
this scout owns the portfolio view: current standing, linked proof, and what
would justify more work.

| System | Role Hypothesis | Status | Current Tracking | Current Read | Next Proof Needed |
|---|---|---|---|---|---|
| `Docling` | Strongest external benchmark; possible upstream substrate or replacement candidate | Benchmarked; decision made | [ADR-003](/Users/cam/.codex/worktrees/c09a/doc-web/docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md), [Stories 158-163](/Users/cam/.codex/worktrees/c09a/doc-web/docs/stories.md#L163) | Fully explored on the hard Onward seam. Keep `doc-web` as the accepted boundary; keep `Docling` as benchmark/reference and pattern source, not the forward replacement path on this lane. | Only reopen if a materially different documented seam appears or if `Docling` is used as an optional upstream substrate for a different document family with a new proof surface. |
| `OCRmyPDF` | Narrow pre-OCR PDF conditioning and normalization seam | Parked | This scout only | Viable only as a child-process preprocessing seam for scan cleanup, rotation, PDF/A normalization, and sidecar text comparisons. Not a structure engine and not a replacement candidate. | Run a narrow preprocessing spike only when artifact inspection proves source-PDF conditioning, not OCR/layout/consistency, is the dominant failure source. |
| `Surya` | Component benchmark for stronger OCR/layout/reading-order/table recognition | Benchmarked negative on active Onward seam | [Story 164](/Users/cam/.codex/worktrees/c09a/doc-web/docs/stories/story-164-surya-component-benchmark-for-layout-and-table-seams.md) | Story 164 proved the bounded runtime and benchmark shape, then came back negative for immediate adoption on the active Onward seam: pinned `0.4.5` layout avoids false positives but only reaches `0.75` table-page recall on Marie-Louise, and the current-package table-capable runtime is still locally blocked. | Only reopen if a runnable current-package substrate exists or if a different document family has a narrower routing/layout problem where page-level table detection alone would be enough value. |
| `Marker` | End-to-end external comparator for schema-guided extraction and multi-format breadth | Queued behind `Surya` | This scout only | Best kept as a breadth comparator, not a first adoption target. Strong on formats and outputs, weaker on provenance fit and licensing posture. | Only benchmark if `Surya`/other component options are insufficient or if a new multi-format comparison becomes high leverage. |
| `GROBID` | Design reference for flavor-based specialization and coordinate-rich structured output | Parked design reference | This scout only | Still not relevant to the active genealogy/intake seams. Valuable mainly as a future pattern source for recipe families and coordinate-rich export on scientific/technical PDFs. | No benchmarking now. Revisit only if technical/scientific PDFs or recipe-family specialization become active roadmap items. |

## Recommendation

1. Treat the `Docling` track as resolved for the reviewed Onward seam. The repo now has enough evidence to keep `Docling` as benchmark/reference and pattern source rather than continuing replacement-driven probing on this lane.
2. Consider the scouting phase effectively complete for these five tools. The next work should be bounded spikes, not more desk research, unless one of the upstream projects changes materially.
3. `Surya` is no longer just queued on the active Onward seam. Story 164 measured it and came back negative for immediate adoption there, so further Surya work should wait for a runnable current-package substrate or a different document family.
4. Keep `OCRmyPDF` as a narrow preprocessing experiment only when artifact inspection shows PDF conditioning is the actual blocker.
5. `Marker` is now the next unbenchmarked broad comparator, but still not an automatic next story; only pull it forward if we want a breadth comparison rather than a lower-level substrate transplant.
6. Keep `GROBID` parked as a design reference unless the active roadmap shifts toward scholarly/technical PDFs or explicit recipe-family specialization.

## Approved

- [x] 1. Bootstrap Scout 011 and preserve the Docling-first evaluation order — Landed as the inbox routing artifact
- [x] 2. Run the actual external-systems scout and produce adopt/skip recommendations — Completed as a research-only comparison against official sources and local `C1`/`C2`/`C3`/`C7` seams; no implementation items approved in this pass
- [x] 3. Execute the recommended `Docling` follow-up as the first full external benchmark chain — Completed later through [ADR-003](/Users/cam/.codex/worktrees/c09a/doc-web/docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md) and [Stories 158-163](/Users/cam/.codex/worktrees/c09a/doc-web/docs/stories.md#L163); result: negative as a replacement path on the reviewed Onward seam, positive as benchmark/reference and pattern source

## Skipped / Rejected

- Row-structured fallback experiment — not part of this scout; already tracked as a deferred `C7` follow-up in `story-146` and `docs/evals/registry.yaml`
- Direct adoption of `OCRmyPDF`, `Surya`, `Marker`, or `GROBID` in this pass — this scout stayed research-only; any implementation or benchmarking follow-up still needs explicit approval
- Treating any external system as a drop-in replacement for doc-forge provenance — rejected; every candidate would still need artifact-level proof against traceability and inspection requirements
- Treating `Docling` as the forward replacement boundary on the reviewed Onward lane — rejected later by [ADR-003](/Users/cam/.codex/worktrees/c09a/doc-web/docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md) after the full story chain (`158-163`) failed to clear the accepted bar honestly
- Treating desk research itself as the next bottleneck after this update — rejected; for `OCRmyPDF`, `Surya`, `Marker`, and `GROBID`, the next useful evidence is now implementation- or benchmark-level, not more high-level reading

## Verification

- Read local methodology and seam context: `docs/inbox.md`, `docs/ideal.md`, `docs/spec.md`, `docs/build-map.md`, `docs/evals/registry.yaml`, `docs/stories/story-027-contact-sheet-auto-intake.md`, `docs/stories/story-028-market-discovery.md`, `docs/stories/story-146-onward-plan-aware-genealogy-reruns.md`, `docs/stories/story-149-onward-scanned-genealogy-collapse-implementation.md`, `modules/intake/contact_sheet_overview_v1/main.py`, `modules/intake/contact_sheet_builder_v1/module.yaml`, `modules/extract/ocr_ai_gpt51_v1/module.yaml`, and `modules/adapter/table_rescue_onward_tables_v1/module.yaml`
- Read primary-source docs for each candidate:
  - `Docling`: architecture, `DoclingDocument`, supported formats, confidence scores, visual grounding, and `SuryaOCR` integration docs
  - `OCRmyPDF`: introduction, cookbook, API, plugin system, and advanced-feature docs
  - `Surya`: official README
  - `Marker`: official README
  - `GROBID`: official README plus documentation for coordinates and specialized processes
- Re-read the primary sources after closing the `Docling` chain to finish the remaining scouting ambiguity:
  - `OCRmyPDF`: current stable introduction/API/cookbook/plugin docs (`17.3.0`) for PDF/A defaults, sidecar caveats, process-isolation guidance, and plugin seams
  - `Surya`: current README / repository metadata for OCR/layout/order/table scope, installation/runtime shape, and GPL + model-license posture
  - `Marker`: current README / repository metadata for supported formats, LLM hybrid mode, structured extraction, and GPL + model-license posture
  - `GROBID`: current README plus flavor and coordinate docs for TEI focus, `flavor=` routing, and coordinate-bearing JSON/TEI surfaces
- No code or benchmark runs were executed in this pass; this was a research-only scout
- Follow-up proof now exists for the top recommendation:
  - [ADR-003](/Users/cam/.codex/worktrees/c09a/doc-web/docs/decisions/adr-003-doclingdocument-doc-web-boundary/adr.md)
  - [Story 158](/Users/cam/.codex/worktrees/c09a/doc-web/docs/stories/story-158-docling-doc-web-replacement-evaluation.md)
  - [Story 159](/Users/cam/.codex/worktrees/c09a/doc-web/docs/stories/story-159-docling-onward-tuning-sweep.md)
  - [Story 160](/Users/cam/.codex/worktrees/c09a/doc-web/docs/stories/story-160-docling-tier2-onward-hybrid-generalization.md)
  - [Story 161](/Users/cam/.codex/worktrees/c09a/doc-web/docs/stories/story-161-integrate-generalized-docling-hybrid-into-maintained-onward-path.md)
  - [Story 162](/Users/cam/.codex/worktrees/c09a/doc-web/docs/stories/story-162-docling-final-boundary-decision-onward-high-cases.md)
  - [Story 163](/Users/cam/.codex/worktrees/c09a/doc-web/docs/stories/story-163-docling-plugin-onward-golden-kill-test.md)
- Follow-up proof now also exists for the strongest post-Docling component candidate:
  - [Story 164](/Users/cam/.codex/worktrees/c09a/doc-web/docs/stories/story-164-surya-component-benchmark-for-layout-and-table-seams.md)

## Evidence

- Local seam evidence:
  - `docs/build-map.md` still shows `C2`, `C1`, `C3`, and `C7` in `climb`
  - `docs/evals/registry.yaml` still shows `auto-book-type-detection` with no scores and `onward-document-consistency-planning` waiting on a `new-approach`
  - `modules/intake/contact_sheet_overview_v1/main.py` still advertises an intake overview classifier as a stub
- Primary sources reviewed:
  - `https://docling-project.github.io/docling/concepts/docling_document/`
  - `https://docling-project.github.io/docling/concepts/architecture/`
  - `https://docling-project.github.io/docling/usage/supported_formats/`
  - `https://docling-project.github.io/docling/concepts/confidence_scores/`
  - `https://docling-project.github.io/docling/examples/visual_grounding/`
  - `https://docling-project.github.io/docling/examples/suryaocr_with_custom_models/`
  - `https://ocrmypdf.readthedocs.io/en/stable/introduction.html`
  - `https://ocrmypdf.readthedocs.io/en/stable/cookbook.html`
  - `https://ocrmypdf.readthedocs.io/en/stable/api.html`
  - `https://ocrmypdf.readthedocs.io/en/stable/plugins.html`
  - `https://github.com/datalab-to/surya`
  - `https://github.com/datalab-to/marker`
  - `https://github.com/grobidOrg/grobid`
  - `https://grobid.readthedocs.io/en/latest/Principles/`
  - `https://grobid.readthedocs.io/en/latest/Grobid-specialized-processes/`
  - `https://grobid.readthedocs.io/en/latest/Coordinates-in-PDF/`
