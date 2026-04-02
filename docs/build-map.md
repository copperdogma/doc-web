# Build Map

> Central dashboard for system progress. Organized by category matching
> `spec.md` (spec:1–spec:9). Each category tracks: product need, tech need,
> substrate status, story coverage, and compromise phase.
>
> See `docs/spec.md` for compromise definitions and `docs/evals/registry.yaml`
> for current eval signals. Converged with Storybook ADR-019 via Story 145;
> reorganized to ADR-021 category/phase structure via Story 148.

## How to Read This Map

- **Product need** — what the category delivers to the user
- **Tech need** — what architectural substrate must exist in code
- **Substrate** — `exists` / `partial` / `missing` / `unplanned`
- **Phase** — `climb` (below target) / `hold` (at target) / `converge` (deletion gate passes)

---

## 1. Intake & Format Routing                                            `spec:1`

**Product need:** Accept source material in multiple formats and route it into the right pipeline.
**Tech need:** Format detection, manifest normalization, recipe selection, contact-sheet routing.
**Substrate:** exists

**Story coverage:** [x] complete
**Spec:** spec:1 (spec:1.1)
**ADR Refs:** None yet
**Absorbs:** Intake & Format Routing (old 1)

### Compromise Progress

- **C2: Format-Specific Conversion Recipes** (AI capability) — **climb**
  - Current: The maintained intake surface now has two explicit lanes: the recommendation-only recipe still emits `intake_plan_v1` across image-directory and PDF inputs, and the confirmed-handoff proof now carries a dedicated 11-case approved-handoff corpus through `run_dispatch_v1` into stamped `intake_handoff_v1` rows. That surface includes the locked 10-document maintained intake PDF corpus plus one repo-owned image-directory case (`testdata/handwritten-notes-mini-images`): `7` maintained launch cases stamp the expected first downstream artifact under bounded `--end-at` execution, and `4` `no-recipe-needed` cases stamp explicit skipped handoff rows. Manual recipe-path retyping is removed for that measured slice; the remaining gap is breadth, not absence of repo-owned image-directory proof.
  - Target: Auto-detect replaces manual recipe selection for 10 diverse documents.
  - Eval: `auto-book-type-detection` — `accuracy = 1.0`, `overall = 1.0`, `pass_rate = 1.0` on 2026-03-29 via Story 171's refreshed maintained-intake harness over the locked 10-document PDF recommendation corpus; and `approved-intake-handoff` — `pass_rate = 1.0`, `launched = 7`, `skipped = 4`, `failed_runs = 0` on 2026-04-02 via Story 180's driver-backed dedicated approved-handoff corpus over those same 10 PDF cases plus one repo-owned image-directory case. The compromise stays `climb` because only one bounded repo-owned image-directory case is measured so far, unsupported families still require manual recipe choice/config, and broader non-PDF/new-family intake remains unproven. Retry when: `new-input-family` or workflow changes that alter the final routing handoff.

---

## 2. OCR & Text Extraction                                              `spec:2`

**Product need:** Turn scanned pages and page images into faithful text/HTML.
**Tech need:** AI-first OCR, targeted downstream rescue for hard layouts, artifact reuse workflows.
**Substrate:** exists

**Story coverage:** [x] complete
**Spec:** spec:2 (spec:2.1, spec:2.2)
**ADR Refs:** None yet
**Absorbs:** OCR & Text Extraction (old 2)

### Compromise Progress

- **C1: Multi-Stage OCR Pipeline** (AI capability) — **climb**
  - Current: AI-first OCR as default, targeted rescue/rerun loops for failures. Strong signals from Stories 127, 131, 140, 144.
  - Target: Single-model OCR of a 400-page mixed-format book at ≥99% character accuracy, layout preserved, <$2 total cost.
  - Eval: No dedicated compromise-detection eval. Closest: `ocr-model-genealogy` at `character_accuracy = 0.97` (2026-02-20, target 0.99), `onward-table-fidelity` at `structure_preservation = 0.969` (2026-03-11, target 0.95). **FAIL** on deletion gate. Retry when: `new-subject-model` or `architecture-change`.

- **C6: Expensive OCR for Quality** (Economics) — **hold**
  - Current: GPT-5.1 AI OCR at ~$0.01/page. Artifact reuse workflows minimize re-runs. Story 134 validated 2048px downsampling as safe default.
  - Target: Current-quality OCR below $0.001/page sustained.
  - Eval: No deletion eval recorded. Trigger is economic, not model-quality. **hold** — acceptable cost, waiting on market.

---

## 3. Layout & Structure Understanding                                   `spec:3`

**Product need:** Detect boundaries, headings, tables, multi-column structure, and layout cues.
**Tech need:** Deterministic detectors, VLM escalation, section splitting, boundary ordering.
**Substrate:** exists

**Story coverage:** [x] complete
**Spec:** spec:3 (spec:3.1)
**ADR Refs:** None yet
**Absorbs:** Layout & Structure Understanding (old 3)

### Compromise Progress

- **C3: Heuristic + AI Layout Detection** (AI capability) — **climb**
  - Current: Deterministic detectors for cheap/stable cases, AI escalation for ambiguity. System still depends on heuristics for stability and cost.
  - Target: VLM-only layout detection at 100% accuracy on a diverse 5-document benchmark with no heuristic fallbacks.
  - Eval: No dedicated deletion eval recorded. **no eval.** Retry when: layout benchmark exists or new subject model makes VLM-first credible.

---

## 4. Illustration Extraction                                            `spec:4`

**Product need:** Detect illustrations, crop them cleanly, exclude text, preserve source relationship.
**Tech need:** VLM crop detection, validator models, OCR-driven text trimming, retry logic.
**Substrate:** exists

**Story coverage:** [x] complete
**Spec:** spec:4 (spec:4.1, spec:4.2)
**ADR Refs:** None yet
**Absorbs:** Illustration Extraction (old 4)

### Compromise Progress

- **C4: Two-Stage Image Crop Detection** (AI capability) — **climb**
  - Current: Detector + validator architecture with retry-on-count-mismatch. Story 133 improved quality/cost with Gemini 3 Flash conservative-count prompt.
  - Target: Single-model crop detection ≥0.95 overall, ≥0.95 pass rate.
  - Eval: `single-model-crop-detection` — `overall = 0.856`, `pass_rate = 0.77` (2026-01-25). **FAIL.** Retry when: `new-subject-model`.

- **C5: Layout Text Trim Heuristics for Crops** (AI capability) — **climb**
  - Current: OCR-driven text trimming, conservative and inspectable.
  - Target: VLM crop detection excludes all non-illustration content on a 50-page benchmark.
  - Eval: No dedicated text-exclusion eval. Closest: `image-crop-extraction` at `overall = 0.900`, `pass_rate = 0.923` (2026-03-11, target 0.95). **FAIL.** Retry when: `new-subject-model` or dedicated text-exclusion benchmark.

---

## 5. Document Consistency Planning                                      `spec:5`

**Product need:** Ensure repeated structures render consistently across a whole document.
**Tech need:** Pattern discovery, consistency plan emission, plan-aware selective reruns, conformance reporting.
**Substrate:** exists

**Story coverage:** [x] complete
**Spec:** spec:5 (spec:5.1)
**ADR Refs:** ADR-001 (source-aware consistency strategy)
**Absorbs:** Document Consistency Planning (old 5)

### Compromise Progress

- **C7: Page-Scope Extraction with Document-Level Consistency Planning** (AI capability + cost) — **climb**
  - Current: Document-level planning explicit and inspectable. Plan-aware reruns instead of hidden normalization. Stories 141-146 established the pattern.
  - Target: On 3+ repeated-structure documents, one-pass extractor produces internally consistent structures without planning layer.
  - Eval: `onward-document-consistency-planning` at `missed_manual_format_coverage = 1.0` (2026-03-15) — proves planning layer works, not yet deletable. **FAIL** on deletion gate. Retry when: `new-approach` (second repeated-structure document) or `architecture-change`.

---

## 6. Validation, Provenance & Export                                    `spec:6`

**Product need:** Prove output is correct and Dossier-ready with full traceability.
**Tech need:** Schema validation, provenance stamping, run health, export formatting.
**Substrate:** exists

**Story coverage:** [x] complete
**Spec:** spec:6
**ADR Refs:** None yet
**Absorbs:** Validation, Provenance & Export (old 6)

No active compromises. Obligations flow from Non-Negotiable Design Principles #1-4.

Provenance completeness for verified scanned/image pipelines is `1.0` after
Story 132's envelope fixes. Validation and run health remain active cross-cutting
responsibilities.

---

## 7. Graduation & Dossier Handoff                                      `spec:7`

**Product need:** Provide a stable document-to-website runtime that Dossier can consume through a versioned boundary while keeping codex-forge focused on R&D.
**Tech need:** Graduation criteria, `doc-web` bundle/provenance contract, Dossier intake surface readiness, release discipline, fixture breadth.
**Substrate:** partial

**Story coverage:** [x] complete (Stories 151-156 landed; Dossier adoption remains downstream)
**Spec:** spec:7
**ADR Refs:** ADR-002 (`doc-web` runtime boundary)
**Absorbs:** Graduation & Dossier Handoff (old 7)

No active product compromises. Obligations flow from Non-Negotiable Design
Principle #5 (Graduate to Dossier) and the Mission. Accepted direction:
`doc-web` is the reusable structural-website runtime, and Dossier should
consume it via a versioned contract. `0` formats are handed off to Dossier
through that boundary today.

---

## 8. AI Harnesses & Tooling                                            `spec:8`

**Product need:** (execution category — no direct user-facing product need)
**Tech need:** Eval framework, prompt engineering, pipeline orchestration, schema validation, artifact inspection.
**Substrate:** exists

**Story coverage:** [x] complete
**Spec:** spec:8 (B1–B6)
**ADR Refs:** None yet
**Absorbs:** Project Operating System (old 8) — AI/tooling half

### Compromise Progress

Build-process compromises tracked in `spec:8`:

| ID | Process Element | Phase | Notes |
|---|---|---|---|
| B1 | Eval framework (promptfoo) | hold | Working; used actively for quality and deletion gates |
| B2 | Prompt engineering | hold | Prompts are stable for current pipelines |
| B3 | Pipeline orchestration (driver.py) | hold | Mature; handles recipes, stages, artifact management |
| B4 | Schema stamping & validation | hold | Working; catches structural drift |
| B5 | Manual artifact inspection | climb | Still required for every story completion |
| B6 | Escalation loops & retry caps | climb | Active in OCR, crop detection, consistency planning |

---

## 9. Planning Infrastructure                                           `spec:9`

**Product need:** (execution category — no direct user-facing product need)
**Tech need:** Stories, ADRs, build map, triage skills, runbooks.
**Substrate:** exists

**Story coverage:** [x] complete
**Spec:** spec:9 (B7–B10)
**ADR Refs:** None yet
**Absorbs:** Project Operating System (old 8) — planning half

### Compromise Progress

Build-process compromises tracked in `spec:9`:

| ID | Process Element | Phase | Notes |
|---|---|---|---|
| B7 | Story/backlog system | hold | Working; 148 stories tracked |
| B8 | Build map & phase tracking | hold | This document; reorganized per ADR-021 |
| B9 | ADR process | hold | 1 accepted ADR; process established |
| B10 | YAML recipe configuration | climb | Overlaps with C2; Stories 176 and 180 remove manual recipe-path retyping for the supported measured PDF plus repo-owned image-directory handoff slice, but unsupported/custom flows still rely on explicit YAML/configuration |

### Operating Rule — Quality First, Then Complexity Collapse

When an active converter or repair seam is still failing manual review, the next
job is to raise quality with the smallest coherent changes needed to clear that
bar. Once the reviewed output is acceptable, the next planned step should not
be another unbounded layer of workaround logic by default. It should be a
**complexity collapse** pass: inventory the active workaround stack, name the
deletion / merge targets, and define the evidence needed to simplify without
reopening the quality gap.

**Acceptable-quality bar:** a real `driver.py` validation run, artifacts in
`output/runs/`, manual inspection on the known hard cases, and no known
reviewed defects in the active slice. At that point remaining work should look
like semantic cleanup, broader fixture coverage, or deliberate architecture
simplification, not emergency structural repair.

**First tracked candidate:** the Onward scanned genealogy table path after Story
146 and run `story146-onward-build-stitch-r5`. That seam now has manually
accepted reviewed outputs on the previously failing table-continuity and
row-shape cases, so the next strategic step is a collapse / simplification
story rather than another opportunistic repair layer. See Story 147.

**Evidence run:** `story146-onward-build-stitch-r5`

**Story 149 result:** first collapse step landed. The maintained regression
path is now `configs/recipes/onward-genealogy-build-regression.yaml`, and the
retained shared genealogy HTML stitching logic now lives in
`modules/common/onward_genealogy_html.py` instead of being reused through
private build/rerun cross-imports.

**Current state:** `climb` on the full canonical Onward output, `hold` on the
reviewed table-continuity / row-shape slice, and not yet `converge`. The seam
has a reviewed trusted slice and a maintained regression path, but the full
Onward output is not yet blessed end-to-end and the workaround stack still
survives.

**Current blessed evidence run:** `story149-onward-build-regression-r1` is now
recorded `known_good` for scope `onward_genealogy_reviewed_html_slice`; generic
`html` remains `partial` until broader value-level verification is refreshed.
The committed reviewed slice for this baseline now lives under
`benchmarks/golden/onward/reviewed_html_slice/story149-onward-build-regression-r1/`.

**Active workaround stack:**
- `plan_onward_document_consistency_v1` plus its `pattern_inventory`,
  `consistency_plan`, and `conformance_report` sidecars still define the
  document-local policy for this recipe.
- `rerun_onward_genealogy_consistency_v1` turns planner / validator signals into
  bounded source-aware rereads.
- `table_rescue_onward_tables_v1` still carries page-level deterministic
  normalization that can beat or replace a weak OCR rerun on some genealogy
  pages.
- `modules/common/onward_genealogy_html.py` now owns the retained deterministic
  genealogy HTML stitching and row-shape normalization that both build and
  rerun still need.
- `build_chapter_html_v1 --merge_contiguous_genealogy_tables` is now narrowed to
  chapter-local continuity assembly that calls the shared helper instead of
  privately owning that normalization logic.
- `configs/recipes/onward-genealogy-build-regression.yaml` is the smaller
  artifact-reuse build/validate regression bundle for this seam; it remains the
  maintained reuse lane when the Story 140 / 143 artifacts are present under
  the shared `output/` root. The old Story 146 proof recipe is historical
  evidence only, not a maintained second operating path.

**Current Tier 2 evidence:** Story 160 supplied the broader spike proof under
`output/runs/story160-docling-generalization-r1/`, Story 161 translated that
shape into the first maintained recipe/module path under
`configs/recipes/onward-docling-hybrid-maintained.yaml` and
`modules/transform/repair_docling_onward_genealogy_v1/`, and Story 162 widened
that maintained path across the full reviewed hard-case slice under
`output/runs/story162-docling-maintained-r1/`.

The widened maintained proof is informative but negative as a final replacement
decision:
- Arthur keeps the repaired onset shape and the frozen parity lane still holds
  at `97.3 / 100`.
- Pierre reaches the reviewed target shape cleanly: `2` tables,
  `37` subgroup rows, `0` heading leaks, `0` combined `BOY/GIRL` headers, and
  `coarse_suspect=false`.
- Antoine is close but still not fully at the reviewed shape: the maintained
  candidate clears heading leaks and restores `16` subgroup rows, but keeps the
  descendants summary inside the main genealogy table (`1` table) instead of
  the reviewed `2`-table shape.
- Leonidas improves materially (`54 -> 9` table-heading leaks,
  `7 -> 0` combined `BOY/GIRL` headers, `0 -> 74` subgroup rows), but it still
  finishes at `12` tables with `coarse_suspect=true` and
  `external_family_heading_count=8`; the reviewed target is `2` tables,
  `104` subgroup rows, and no leak signal.
- Marie-Louise also improves materially (`39 -> 17` table-heading leaks,
  `4 -> 0` combined headers, `0 -> 42` subgroup rows), but it still lands at
  `4` tables vs the reviewed `2`, preserves a pre-genealogy name-list block
  outside the repaired section, and remains structurally short of the reviewed
  target (`73` subgroup rows).
- Re-running the widened Leonidas and Marie-Louise excerpts through the
  retained chapter-merge normalizer does not materially rescue those lanes, so
  the remaining gap is not a small omitted merge setting.

The widened maintained path therefore does not earn simplification or
replacement on this seam. It is maintained benchmark evidence, not a promoted
replacement direction. `doc-web` remains the accepted boundary.

**Current Tier 1 plugin evidence:** Story 163 widened the documented external
plugin seam into a coordinated official plugin stack under
`output/runs/story163-docling-plugin-killtest-r2/`. The repo now has
repo-owned `layout_engines` and `table_structure_engines` plugins registering
cleanly through the official `docling` entrypoint group and loading only when
`allow_external_plugins=True`, so the seam is real rather than hypothetical.
The coordinated pass remains negative as a reopen candidate:
- Leonidas does not materially move. `layout+table` still ends at `7` tables,
  `55` heading leaks, `5` combined `BOY/GIRL` headers, and `0` subgroup rows.
  The HTML remains page-bounded across pages `[2] [3] [4] [5] [6] [7] [8]`.
- Marie-Louise improves only narrowly. `layout` can merge the same-page split
  from `6 -> 5` tables and restore `MARIE LOUISE'S FAMILY`, while
  `layout+table` keeps combined headers at `2`, but the lane still ends with
  `49` heading leaks, `0` subgroup rows, and page-bounded tables on
  `[3] [4] [5] [6] [7]`.
- The local runtime still exposes no official serializer or document-level
  merge plugin seam, so the remaining gap is not an honest OCR follow-up. The
  coordinated plugin stack still underperforms the already-negative Story 162
  maintained path on the structural signal that matters most (`0` subgroup rows
  here versus `74` / `42` in the maintained benchmark lanes).
- Result: even the broadened official plugin path does not reopen the Onward
  boundary decision.

**Current external component benchmark evidence:** Story 164 tested `Surya` as
the next lower-level component candidate under
`output/runs/story164-surya-benchmark-r1/`. The first honest local substrate is
the pinned `surya-ocr==0.4.5` runtime, which exposes layout/order/OCR CLIs but
not the newer `surya_table` CLI. On the overlapping Marie-Louise reviewed
subset, the layout benchmark stays negative for immediate adoption:
- `page_079` is a clean non-table true negative.
- `page_081`, `page_082`, and `page_083` each receive one or more large `Table`
  boxes (`largest_table_area_ratio` `0.3848`, `0.6176`, and `0.5447`).
- `page_080` is a hard false negative: the gold page contains the onset
  genealogy table, but Surya emits only `Text` boxes and no `Table` box there.
- Net result: `table_page_recall = 0.75`, `large_table_recall = 0.75`,
  `false_positive_pages = 0`.

That is not a clean enough routing/layout win to justify even a narrow
integration probe on this seam, especially because the current-package
table-capable runtime (`surya-ocr==0.17.1`) is still locally blocked on this
machine. Story 164 therefore closes as negative for immediate Onward adoption.

**Current external breadth benchmark evidence:** Story 165 tested `Marker` on
the repo-owned `born-digital-pdf` fixture under
`output/runs/story165-marker-benchmark-r1/` and reached a split result that
matters for the input-coverage roadmap:
- Stock `Marker` CLI is not an honest adoption candidate here. On this machine
  it still drags in a multi-gigabyte model stack even for `--disable_ocr`, and
  the code/model license posture remains materially awkward for the maintained
  runtime.
- The thinner Marker-internals path is materially more interesting than the
  product-level CLI. On `testdata/tbotb-mini.pdf`, the `lite_api` benchmark
  preserves all tracked headings and `1.0` token coverage versus `pdftotext`,
  while also emitting `page_stats` and `table_of_contents` metadata under
  `output/runs/story165-marker-benchmark-r1/tbotb-mini/marker-v1102/`.
- The current local baseline remains wastefully OCR-routed on the same born-
  digital fixture. `output/runs/story165-docweb-baseline-r1/ocr_ensemble/ocr_source_histogram.json`
  shows all `3` pages sourced from `tesseract` even though `pdftext_text_pct`
  is `1.0`, and page `3` still triggers escalation with a duplicated terminal
  line in `ocr_ensemble/pages/page-003.json`.

Story 168 now converts that proof into a maintained optional lane under
`output/runs/story168-marker-lite-proof-r4/`:
- the explicit recipe `recipe-born-digital-pdf-marker-lite-html-mvp.yaml`
  drives a maintained `extract_pdf_marker_lite_html_v1` stage through
  `driver.py`
- the fresh run emits stamped `page_html_v1`, a `doc_web_bundle` manifest, and
  `doc_web_bundle/provenance/blocks.jsonl` inside the accepted `doc-web`
  boundary
- the known normalization defects are fixed on the repo-owned fixture:
  page-2 section headings normalize consistently and page 3's merged choice
  prompt is split into two blocks, while `token_coverage_vs_pdftotext` remains
  `1.0`

That is still not enough to mark `born-digital-pdf` as passing. The evidence is
still one tiny fixture, the maintained native-text lane remains optional rather
than default, and the runtime cost is materially heavier than the OCR baseline
(`521.44s` cold extract for the Marker-lite run versus `11.84s` for the OCR
stage on the same fixture). The current read therefore changes from "missing
maintained native-text path" to "bounded maintained path exists, but broader
coverage and operator discipline are still missing."

**Ownership read after Story 162:**
- Explicitly narrowed shared helper that survived honestly:
  `modules/common/onward_openai_ocr.py` now owns the shared OpenAI vision OCR
  request path used by rescue, rerun, and the `Docling` repair lane.
- Still-justified incumbent owners:
  `table_rescue_onward_tables_v1` for page-level deterministic normalization,
  `plan_onward_document_consistency_v1`,
  `rerun_onward_genealogy_consistency_v1`,
  `modules/common/onward_genealogy_html.py`, and
  `build_chapter_html_v1 --merge_contiguous_genealogy_tables`.
- Not promoted to deletion or adoption targets:
  `configs/recipes/onward-docling-hybrid-maintained.yaml` plus
  `modules/transform/repair_docling_onward_genealogy_v1`.
  Keep them as benchmark/reference surfaces, not as the forward Onward
  boundary.

**Reopen conditions:** only reopen the `Docling` replacement question on this
lane if a materially different documented official seam or demonstrably thinner
hybrid path appears that can clear Leonidas and Marie-Louise without regrowing
the current rescue ownership. The current coordinated official plugin path
(`layout` + `table_structure`) has now been tested and does not satisfy that
condition.

**Non-goal:** this does not claim that C7, C1, or C3 are resolved. It records
that the current `Docling` replacement path failed to earn the final
simplification/deletion proof on the reviewed Onward slice.

**Tracking model:** this build-map section remains the high-level dashboard for
the Onward seam: trusted slice, active workaround ownership, and the current
reason the replacement question is closed.
The detailed operational truth lives elsewhere:
- `output/run_assessments.jsonl` is the trust ledger for blessed runs and
  scopes (`known_good`, `partial`, `unsafe`, `superseded`).
- `output/run_health.jsonl` and `output/run_manifest.jsonl` track reuse safety,
  provenance, and exact run discovery.
- `benchmarks/golden/onward/` holds the committed Onward golden slices used by
  evals and spot-checked regression work today.
- `docs/runbooks/golden-build.md` defines how those goldens are created and
  maintained.
- Long-term direction: these scoped trusted slices should accumulate toward one
  canonical 100%-correct Onward baseline, but until that exists the registry
  and committed goldens describe which parts of that baseline are actually
  verified.

**Reusable pattern:** when another seam clears the acceptable-quality bar, reuse
this same mini-template: evidence run, active workaround stack, candidate
deletion / merge targets, and proof needed before simplification. Do not add an
empty dedicated section until a second candidate exists.

---

## Input Coverage

> Cross-cutting section spanning multiple categories. Machine-readable source:
> `tests/fixtures/formats/_coverage-matrix.json`

### Current Status

**7 formats passing** | **3 have fixture** | **6 untested** | **0 graduated** | **16 total tracked**

### Passing

| Format | ID | Family | Current Pipeline | Text | Structure | Illustration | Provenance | Notes |
|---|---|---|---|---:|---:|---:|---:|---|
| Scanned PDF (prose) | `scanned-pdf-prose` | `scanned-pdf` | `extract_pdf_images_fast_v1 -> ocr_ai_gpt51_v1` | 1.00 | 1.00 | - | 1.00 | Story 167 adds `testdata/scanned-prose-mini.pdf`, a repo-owned image-only simple-prose fixture. Fresh `driver.py` proof plus source-text comparison on 2026-03-27 matched the checked-in source text exactly after normalization; broader noisy scanned-prose quality remains a separate question. |
| Scanned PDF (tables) | `scanned-pdf-tables` | `scanned-pdf` | `extract_pdf_images_fast_v1 -> ocr_ai_gpt51_v1 -> table_rescue_html_loop_v1` | 0.93 | 0.95 | 0.900 | 1.00 | Onward-style genealogy path. Story 157 restored a maintained PDF-backed entry recipe; the shared Onward PDF and image-directory source are both 127 pages. Story 176 adds a fresh confirmed-handoff proof from intake approval into `recipe-pdf-ocr-html-mvp.yaml`, with inspected `intake_handoff_v1` plus downstream `page_image_v1` manifest artifacts under `story176-scanned-proof*`. |
| Image directory | `image-directory-scans` | `image-directory` | `images_dir_to_manifest_v1 -> ocr_ai_gpt51_v1` | 0.93 | 0.95 | 0.900 | 1.00 | Same source quality as the scanned-PDF image path once pages are extracted. Story 176 adds a fresh confirmed-handoff proof from intake approval into `recipe-images-ocr-html-mvp.yaml`, with inspected `intake_handoff_v1` plus downstream `page_image_v1` manifest artifacts under `story176-image-proof*`. |
| Handwritten notes | `handwritten-notes` | `handwritten` | `images_dir_to_manifest_v1 -> ocr_ai_gpt51_v1` | 1.00 | 1.00 | - | 1.00 | Story 179 adds `testdata/handwritten-notes-mini-images/` plus the image-only wrapper `testdata/handwritten-notes-mini.pdf`. Fresh `driver.py` proof on 2026-04-01 matched the checked-in transcript exactly after normalization on both maintained generic image-directory and PDF OCR lanes, and `benchmarks/scripts/run_handwritten_notes_eval.py` now reruns that bounded proof surface. This is passing only for the narrow highly legible synthetic slice; messy cursive and degraded handwriting remain unproven. |
| Plain text | `plain-text` | `plain-text` | `extract_text_v1` | 1.00 | - | - | - | Passthrough, no OCR. |
| Markdown | `markdown` | `markdown` | `extract_text_v1` | 1.00 | - | - | - | Passthrough. |
| HTML | `html-files` | `html` | `extract_text_v1` | 1.00 | - | - | - | Passthrough. |
| Word (.docx) | `docx` | `docx` | `testdata/docx-mini.docx`, `testdata/docx-sections-mini.docx`, and `testdata/docx-nested-mini.docx` via `recipe-docx-html-mvp.yaml` | - | - | - | 1.00 | Story 175 widens the maintained DOCX lane to three repo-owned fixtures on the supported slice: heading-based sections, prose, nested subheadings, simple bullet lists, and a simple table. Fresh `driver.py` proof on 2026-04-01 produced final `doc_web_bundle` manifests plus pageless block provenance for all three fixtures. The lane now normalizes sentence-like stray top-level `Title` elements before chapter splitting so wider prose fixtures do not invent false chapters. Advanced Word features such as tracked changes, comments, text boxes, and embedded charts remain unproven. |

### Has Fixture (pipeline not yet passing)

| Format | ID | Family | Fixture / Current Pipeline | Priority | Notes |
|---|---|---|---|---|---|
| Born-digital PDF | `born-digital-pdf` | `born-digital-pdf` | `testdata/tbotb-mini.pdf` via `recipe-pdf-ocr-html-mvp.yaml` and `recipe-born-digital-pdf-marker-lite-html-mvp.yaml`; `testdata/flat-born-digital-mini.pdf` and `testdata/flat-born-digital-form-mini.pdf` via `recipe-born-digital-pdf-non-toc-html-mvp.yaml`; Story 171 validation assets `rfp` and `release-forms` | High | Story 157 keeps the maintained OCR-entry lane, Story 168 adds an explicit maintained optional Marker-lite native-text recipe on the repo-owned book-like fixture, and Story 171 adds an explicit maintained non-TOC sibling recipe for flat born-digital PDFs. Story 177 widens the repo-owned flat proof surface to `flat-born-digital-mini.pdf` plus `flat-born-digital-form-mini.pdf`, and fresh `driver.py` proof now exists on those two repo-owned fixtures plus the local `rfp` and `release-forms` comparison assets under `story177-*`: all four produce stamped `page_html_v1`, non-empty portion artifacts, final `doc_web_bundle` manifests, and page-linked provenance. Story 177 also absorbs a bounded final-HTML polish on the proven slice: repeated short in-body `h1`/`h2` labels are demoted to calmer subheads, and the pathological long warning block on `release-forms` is flattened into an emphasis paragraph. Story 176 adds a confirmed-handoff proof from intake approval into the reviewed Marker-lite book-like lane on `testdata/tbotb-mini.pdf`, with inspected `intake_handoff_v1` plus downstream `page_html_v1` artifacts under `story176-born-proof*`. The family still stays `has fixture`, not passing: proof breadth is still small, the lane still depends on Docker plus a cached GPL/model-license-constrained Marker runtime, and cold-start cost remains materially higher than the OCR baseline. |
| Excel (.xlsx) | `xlsx` | `xlsx` | `testdata/xlsx-mini.xlsx` via `recipe-xlsx-html-mvp.yaml` | Medium | Story 175 adds the first maintained explicit XLSX lane on a repo-owned two-sheet workbook. Fresh `driver.py` proof on 2026-04-01 produced a final `doc_web_bundle` manifest with one HTML page per sheet (`Roster`, `Visits`) plus anchor-based provenance rows for each table. The family still stays `has fixture`, not passing: only the simple-table workbook slice is reviewed, and formulas, charts, merged cells, images, comments, and cell-address anchors remain unproven. |
| PowerPoint (.pptx) | `pptx` | `pptx` | `testdata/pptx-mini.pptx` reproducible seam-probe fixture | Low | Story 175 adds a reproducible PPTX probe fixture, but there is still no maintained lane. The current local seam remains blocked: `unstructured.partition.pptx` fails in this checkout on missing `python-pptx`, so PPTX now has an explicit measured defer reason instead of vague backlog residue. |

### Untested

| Format | ID | Family | Complexity | Priority | Notes |
|---|---|---|---|---|---|
| EPUB | `epub` | `epub` | prose, illustrations | Medium | Zipped HTML + image intake remains unbuilt. |
| Email (.eml) | `email-eml` | `email` | prose | Medium | Personal correspondence import path still missing. |
| Email archive (.mbox) | `email-mbox` | `email` | prose | Medium | Bulk archive support still missing. |
| Web page | `web-page` | `web-page` | mixed-layout, illustrations | Medium | Online sources remain a routing/intake gap. |
| Mixed archive | `mixed-archive` | `mixed-archive` | mixed | Low | Needs auto-routing plus multi-format unpacking. |

### Graduated

None yet.

## Accuracy Dimensions

- **Text Fidelity** — character-level accuracy versus source (target: `>= 0.99`)
- **Structure Preservation** — tables, columns, headers, lists (target: `>= 0.95`)
- **Illustration Extraction** — detection, cropping, and cataloging quality
  (target: `>= 0.95`)
- **Provenance Completeness** — every output traces to source page/location
  (target: `1.0`)

## Known Gaps (Prioritized)

### Gap 1 — Illustration crop quality on image-bearing formats

- **Current signal:** `image-crop-extraction` is at `0.900` overall against a
  `0.95` target, and the true deletion gate `single-model-crop-detection`
  remains at `0.856 / 0.77`.
- **Root cause:** C4 (spec:4.1) and C5 (spec:4.2) still hold. Single-stage crop detection is not good
  enough to remove validator + trim heuristics.
- **Fix category:** Model-selection / compromise-detection.
- **Status:** Still open; blocked on better single-model performance or a
  stronger benchmark signal.

### Gap 2 — Born-digital PDF native text extraction

- **Current signal:** Story 168 still provides the maintained optional native-text lane on `testdata/tbotb-mini.pdf` via `recipe-born-digital-pdf-marker-lite-html-mvp.yaml`, with accepted `doc_web_bundle` / provenance sidecars and no inspected text-loss signal on that reviewed fixture. Story 171 adds `recipe-born-digital-pdf-non-toc-html-mvp.yaml` plus the first repo-owned flat fixture (`testdata/flat-born-digital-mini.pdf`). Story 177 widens that flat proof surface to a second repo-owned fixture (`testdata/flat-born-digital-form-mini.pdf`) and reruns the same maintained lane on local `rfp` / `release-forms`; all four now complete through `build_chapter_html_v1` with stamped `page_html_v1`, non-empty `portion_hyp_v1`, final bundle manifests, and inspected provenance sidecars. Story 177 also absorbs bounded final-HTML polish on the proven slice: repeated short in-body `h1` / `h2` labels are demoted to calmer subheads, and the pathological long warning block on `release-forms` is flattened into an emphasis paragraph. Runtime burden remains real: the first fresh Story 177 rerun (`story177-flat-baseline-r1`) took `176.0s` for 2 pages after the worktree-local Marker runtime had to rebuild, even though warm reruns dropped into the `24s`-`28s` range on the local comparison PDFs.
- **Root cause:** The missing maintained path and the immediate heading-cleanup follow-up are no longer the blockers on the proven slice. The remaining limitations are breadth and runtime: proof still covers only two repo-owned flat fixtures plus two local comparison PDFs, and the optional native-text lane still carries explicit Docker + cached Marker runtime burden plus a heavy cold-start path.
- **Fix category:** Further fixture widening plus runtime/cost discipline on the maintained native-text lane.
- **Status:** Gap narrowed again from "maintained lane with limited proof breadth and visible heading roughness" to "maintained lane with limited proof breadth and explicit runtime burden." Keep `born-digital-pdf` in `has fixture` until the non-TOC lane is validated across more diverse flat born-digital inputs and the runtime burden is reduced or accepted.

### Gap 3 — Office document intake beyond the first DOCX slice

- **Current signal:** Story 175 resolves the original "single DOCX slice" framing. DOCX now has three repo-owned passing fixtures on the supported slice via `recipe-docx-html-mvp.yaml`, and XLSX now has a first maintained explicit lane on `testdata/xlsx-mini.xlsx` via `recipe-xlsx-html-mvp.yaml`. PPTX is no longer vague; `testdata/pptx-mini.pptx` exists as a reproducible seam-probe fixture, and the current block is explicit (`python-pptx` missing in this checkout).
- **Root cause:** Intake coverage (spec:1) is still skewed toward PDFs and image directories at family breadth. Office coverage is now real, but uneven: DOCX is passing on a bounded slice, XLSX is only a first fixture-backed maintained lane, and PPTX still has no honest runtime substrate.
- **Fix category:** XLSX breadth expansion only if demand warrants it, plus an explicit PPTX runtime / provenance decision when slide support becomes worth the cost.
- **Status:** Gap narrowed substantially. The repo now has passing DOCX and a first maintained XLSX slice, with PPTX reduced to an explicit measured defer instead of an ambiguous missing family.

### Gap 4 — Handwritten document transcription

- **Current signal:** Story 179 adds a repo-owned synthetic handwritten-notes fixture and `benchmarks/scripts/run_handwritten_notes_eval.py`; the maintained generic image-directory and PDF OCR seams now score `1.0` on that bounded slice with image-only PDF verification (`[0, 0]` extract-text lengths).
- **Root cause:** The "no handwriting path" gap is closed for one narrow highly legible synthetic slice, but breadth is still thin: the repo has no permissively licensed real handwriting fixture and no evidence yet on messier cursive or degraded note scans.
- **Fix category:** Fixture expansion and eval widening, not a new runtime path.
- **Status:** Narrowed from missing capability to bounded breadth gap.

### Gap 5 — Fixture breadth and graduation confidence

- **Current signal:** Story 175 gives DOCX three diverse repo-owned passing
  fixtures on its supported slice, and Story 177 gives born-digital PDF a
  second repo-owned flat fixture plus a fresh four-asset proof surface on the
  maintained non-TOC lane. Most other active families still rely on at most two
  repo-owned fixtures and/or a small set of local comparison assets.
- **Root cause:** Capability coverage grew faster than repeatable benchmark
  breadth.
- **Fix category:** Fixture expansion and rerun discipline.
- **Status:** Open cross-cutting quality gap, but narrower now that DOCX has crossed the three-fixture proof bar and born-digital flat proof no longer rests on a single repo-owned mini fixture.

## Resolved Gaps

### Resolved — Provenance completeness on verified scanned/image pipelines

- **Previous state:** provenance completeness was `0.984` (scanned-pdf-prose)
  and `0.956` (table/image paths).
- **Fix:** Story 132 stamped the missing envelope fields and verified the
  relevant pipeline path at `1.0`.
- **Resolved:** 2026-03-11 verification run `provenance-verify-132`.

### Resolved — Table structure preservation on dense genealogy tables

- **Previous state:** OCR/layout handling lost table shape on Onward-style
  content.
- **Fix:** Story 131 aligned the scorer, tuned the prompt, and selected the
  strongest subject model.
- **Resolved:** 2026-03-11 with `onward-table-fidelity = 0.969`.

## Graduation Criteria

A converter is ready to graduate to Dossier (spec:7) when:

1. Text fidelity is `>= 0.99` on all test fixtures for that format
2. Structure preservation is `>= 0.95` where structure matters
3. At least 3 diverse fixtures pass for that format family
4. The converter has been stable for 2+ stories without churn
5. Dossier has an intake surface ready to receive it

## Next Actions

1. Expand handwritten fixture breadth beyond the first synthetic, highly legible slice before treating the family as broadly supported.
2. Expand fixture breadth for already-passing formats so graduation decisions
   can be trusted.
3. Widen born-digital proof beyond the current repo-owned prose + form mini
   fixtures if the family becomes a near-term graduation target, or explicitly
   accept the native-text runtime burden instead of leaving it implicit.
4. Decide whether PPTX should remain explicitly deferred or gain a maintained runtime surface once `python-pptx` and slide-provenance expectations are worth absorbing.
5. Re-run stale capability measurements where the code changed but the benchmark
   signal did not.
