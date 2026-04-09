# Pipeline Operations Runbook

**Audience:** AI Agents & Engineering Operators
**Scope:** Execution, Recovery, and Configuration of the Doc Forge pipeline.

## 🛑 Critical Safety Rules
1.  **NEVER use `--force` when resuming.** It deletes the entire run directory.
2.  **ALWAYS use `run_driver_monitored.sh`** for production runs (handles logging, PID tracking, crash detection).
3.  **CHECK `pipeline_state.json`** before resuming to confirm the correct `--start-from` stage.

---

## 🚀 Standard Execution

There is no single default recipe for the active mission. Choose the narrowest
recipe that matches the document family you are validating.

### Runtime Preflight

Use this before downstream pin bumps or consumer integration work:

```bash
python -m pip install .
doc-web contract --json
```

This is the machine-readable compatibility surface Dossier should check before
accepting a new pinned `doc-web` version.

If you want the repo's 7-day freshness gate on Python package resolution, run
the same installs through the repo wrapper instead of raw `pip`:

```bash
./scripts/install_with_age_gate.py .
./scripts/install_with_age_gate.py '.[driver]'
./scripts/install_with_age_gate.py '.[driver,docx]'
./scripts/install_with_age_gate.py '.[driver,pptx]'
./scripts/install_with_age_gate.py '.[driver,xlsx]'
./scripts/install_with_age_gate.py -r requirements.txt
```

The wrapper prefers `uv pip install --exclude-newer ...` and falls back to
`pip install --uploaded-prior-to ...` when your pip version supports it.

If you also need to run the repo-owned `driver.py` proof lanes from this
checkout, install the explicit driver extra first:

```bash
python -m pip install '.[driver]'
```

That extra covers the maintained fixture bundle smoke plus the maintained
book-like and non-TOC born-digital proof lanes. OCR-heavy recipes still use
the broader repo runtime from `requirements.txt`.

For the maintained DOCX lane, add the explicit DOCX extra:

```bash
python -m pip install '.[driver,docx]'
```

For the maintained XLSX lane, add the explicit XLSX extra:

```bash
python -m pip install '.[driver,xlsx]'
```

For the maintained PPTX lane, add the explicit PPTX extra:

```bash
python -m pip install '.[driver,pptx]'
```

The fuller repo runtime from `requirements.txt` also now includes DOCX, XLSX,
and PPTX support, but it is currently validated on Python 3.11/3.12 because
the pinned `unstructured==0.16.9` dependency is limited to that range.

### Structural Website / `doc-web` Runs
Use these when validating the active structural HTML bundle path.

```bash
scripts/run_driver_monitored.sh \
  --recipe <active_recipe> \
  --run-id <run_id> \
  --output-dir output/runs \
  -- --instrument --force
```
*   `--instrument`: Enables cost/timing tracking (Required for production).
*   `--force`: **DELETES** `<run_id>` dir if it exists. Use only for fresh starts.

Active recipe examples:
- `configs/recipes/recipe-images-ocr-html-mvp.yaml`
- `configs/recipes/recipe-pdf-ocr-html-mvp.yaml`
- `configs/recipes/recipe-docx-html-mvp.yaml`
- `configs/recipes/recipe-pptx-html-mvp.yaml`
- `configs/recipes/recipe-xlsx-html-mvp.yaml`
- `configs/recipes/recipe-onward-images-html-mvp.yaml`
- `configs/recipes/recipe-onward-pdf-html-mvp.yaml`
- `configs/recipes/onward-genealogy-build-regression.yaml` (artifact-reuse path; requires the referenced Story 140 / 143 artifacts under `output/`)
- `configs/recipes/doc-web-fixture-bundle-smoke.yaml` (repo-owned contract smoke lane; emits `manifest.json`, `provenance/blocks.jsonl`, one chapter HTML file, one fallback page HTML file, and bundle-local image assets)

### Smoke Test (Verification)
Use the same recipe you are actually touching, but narrow the run to the
smallest real slice that still exercises the changed seam.

```bash
scripts/run_driver_monitored.sh \
  --recipe <active_recipe> \
  --run-id <smoke_run_id> \
  --output-dir output/runs \
  -- --instrument --max-pages <N> --force
```

- There is no generic `make smoke` target for the active intake / `doc-web`
  path.

### Repo-Owned `doc-web` Contract Smoke

Use this lane when you need a cheap real-run proof that the active repo still
emits the Dossier-facing bundle contract:

```bash
python -m pip install '.[driver]'
python driver.py \
  --recipe configs/recipes/doc-web-fixture-bundle-smoke.yaml \
  --run-id <run_id> \
  --allow-run-id-reuse \
  --force
python validate_artifact.py \
  --schema doc_web_bundle_manifest_v1 \
  --file output/runs/<run_id>/output/html/manifest.json
python validate_artifact.py \
  --schema doc_web_provenance_block_v1 \
  --file output/runs/<run_id>/output/html/provenance/blocks.jsonl
```

Expected bundle outputs:

- `output/runs/<run_id>/output/html/index.html`
- `output/runs/<run_id>/output/html/chapter-001.html`
- `output/runs/<run_id>/output/html/page-001.html`
- `output/runs/<run_id>/output/html/manifest.json`
- `output/runs/<run_id>/output/html/provenance/blocks.jsonl`

This smoke lane does not require the local OCR stack after install, but it does
require the `driver` extra because `driver.py` and the bundle builder depend on
YAML parsing plus HTML bundle tooling.

### Maintained Born-Digital Book-Like Smoke

Use this when you need a maintained proof run of the bounded book-like
born-digital PDF lane on the repo-owned supported slice:

```bash
python -m pip install '.[driver]'
python driver.py \
  --recipe configs/recipes/recipe-born-digital-pdf-marker-lite-html-mvp.yaml \
  --input-pdf testdata/born-digital-handbook-mini.pdf \
  --run-id <run_id> \
  --allow-run-id-reuse \
  --force
```

Additional non-Python requirements for this lane:

- Docker on `PATH`
- `pdftotext` on `PATH`

### Maintained Born-Digital Non-TOC Smoke

Use this when you need a maintained proof run of the non-TOC born-digital PDF
lane that emits substep progress throughout the long Marker-lite stage:

```bash
python -m pip install '.[driver]'
python driver.py \
  --recipe configs/recipes/recipe-born-digital-pdf-non-toc-html-mvp.yaml \
  --input-pdf testdata/flat-born-digital-mini.pdf \
  --run-id <run_id> \
  --allow-run-id-reuse \
  --force
```

Additional non-Python requirements for this lane:

- Docker on `PATH`
- `pdftotext` on `PATH`

### Maintained Born-Digital Benchmark

Use this when you need the maintained born-digital comparison surface across
the passing repo-owned slice plus the optional shared local comparison PDFs:

```bash
python -m pip install '.[driver]'
python benchmarks/scripts/run_born_digital_pdf_eval.py \
  --output benchmarks/results/born-digital-pdf-story196.json \
  --run-root output/runs/story196-born-digital-benchmark
```

This benchmark measures four repo-owned supported fixtures across both
maintained lanes (`tbotb-mini`, `born-digital-handbook-mini`,
`flat-born-digital-mini`, `flat-born-digital-form-mini`) and also reruns the
two shared local comparison-only PDFs (`rfp`, `release-forms`) when they are
available on disk.

### Repo-Owned PDF Intake Smoke

Use this when you need a cheap real-run proof that the maintained PDF entry
surface still emits a stamped `page_image_v1` manifest from a checked-in PDF:

```bash
# Born-digital entry smoke
python driver.py \
  --recipe configs/recipes/recipe-pdf-ocr-html-mvp.yaml \
  --input-pdf testdata/tbotb-mini.pdf \
  --run-id <run_id> \
  --allow-run-id-reuse \
  --end-at pdf_to_images

# Image-only scanned-prose fixture smoke
python driver.py \
  --recipe configs/recipes/recipe-pdf-ocr-html-mvp.yaml \
  --input-pdf testdata/scanned-prose-mini.pdf \
  --run-id <run_id> \
  --allow-run-id-reuse \
  --end-at pdf_to_images
```

Expected extractor outputs:

- `output/runs/<run_id>/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl`
- `output/runs/<run_id>/01_extract_pdf_images_fast_v1/extraction_report.jsonl`
- `output/runs/<run_id>/01_extract_pdf_images_fast_v1/extraction_summary.json`

Notes:

- `testdata/tbotb-mini.pdf` proves maintained PDF entry wiring only for a small born-digital PDF.
- `testdata/scanned-prose-mini.pdf` is a repo-owned image-only simple-prose scanned fixture. Story 167 proved the maintained lane through `ocr_ai` and matched the checked-in source text exactly after normalization on 2026-03-27; broader noisy scanned-prose quality still needs separate validation.

### Repo-Owned DOCX Intake Smoke

Use this when you need a cheap real-run proof that the maintained DOCX lane
still emits a final `doc-web` bundle plus pageless block provenance from the
checked-in DOCX fixtures:

```bash
python -m pip install '.[driver,docx]'
python driver.py \
  --recipe configs/recipes/recipe-docx-html-mvp.yaml \
  --input-docx testdata/docx-mini.docx \
  --run-id <run_id> \
  --allow-run-id-reuse
python validate_artifact.py \
  --schema doc_web_bundle_manifest_v1 \
  --file output/runs/<run_id>/output/html/manifest.json
python validate_artifact.py \
  --schema doc_web_provenance_block_v1 \
  --file output/runs/<run_id>/output/html/provenance/blocks.jsonl
```

Story 175 widened the maintained DOCX proof surface to three repo-owned
fixtures on the same supported slice:

- `testdata/docx-mini.docx`
- `testdata/docx-sections-mini.docx`
- `testdata/docx-nested-mini.docx`

Expected bundle outputs:

- `output/runs/<run_id>/01_unstructured_docx_intake_v1/elements.jsonl`
- `output/runs/<run_id>/02_docx_elements_to_bundle_v1/docx_bundle_report.json`
- `output/runs/<run_id>/output/html/index.html`
- `output/runs/<run_id>/output/html/chapter-001.html`
- `output/runs/<run_id>/output/html/chapter-002.html`
- `output/runs/<run_id>/output/html/manifest.json`
- `output/runs/<run_id>/output/html/provenance/blocks.jsonl`

Alternative supported install shape for this lane:

- `python -m pip install -r requirements.txt` on Python 3.11/3.12

### Repo-Owned XLSX Intake Smoke

Use this when you need a cheap real-run proof that the maintained XLSX lane
still emits a final `doc-web` bundle plus sheet-anchored provenance from the
checked-in workbook fixtures on the supported slice:

```bash
python -m pip install '.[driver,xlsx]'
python driver.py \
  --recipe configs/recipes/recipe-xlsx-html-mvp.yaml \
  --input-xlsx testdata/xlsx-mini.xlsx \
  --run-id <run_id> \
  --allow-run-id-reuse
python validate_artifact.py \
  --schema doc_web_bundle_manifest_v1 \
  --file output/runs/<run_id>/output/html/manifest.json
python validate_artifact.py \
  --schema doc_web_provenance_block_v1 \
  --file output/runs/<run_id>/output/html/provenance/blocks.jsonl
```

Story 193 widened the maintained XLSX proof surface to three supported
checked-in fixtures on the same slice:

- `testdata/xlsx-mini.xlsx`
- `testdata/xlsx-multi-sheet.xlsx`
- `testdata/xlsx-two-tables.xlsx`

The maintained claim is still bounded to simple table-only sheets, including
multiple table regions on one sheet, with sheet-named entries and
`source_element_ids` provenance. `testdata/xlsx-merged-formula.xlsx` is a
checked-in boundary probe, not a supported smoke fixture: in the fresh Story
193 recheck, Unstructured split the merged title and `Total` summary into
heading blocks instead of preserving that summary row as table content.

Expected bundle outputs:

- `output/runs/<run_id>/01_unstructured_xlsx_intake_v1/elements.jsonl`
- `output/runs/<run_id>/02_xlsx_elements_to_bundle_v1/xlsx_bundle_report.json`
- `output/runs/<run_id>/output/html/index.html`
- `output/runs/<run_id>/output/html/page-001.html`
- `output/runs/<run_id>/output/html/page-00N.html` for any additional supported sheet/entry
- `output/runs/<run_id>/output/html/manifest.json`
- `output/runs/<run_id>/output/html/provenance/blocks.jsonl`

Alternative supported install shape for this lane:

- `python -m pip install -r requirements.txt` on Python 3.11/3.12

### Repo-Owned PPTX Intake Smoke

Use this when you need a cheap real-run proof that the maintained PPTX lane
still emits a final `doc-web` bundle plus slide-number provenance from the
checked-in bounded probe fixture:

```bash
python -m pip install '.[driver,pptx]'
python driver.py \
  --recipe configs/recipes/recipe-pptx-html-mvp.yaml \
  --input-pptx testdata/pptx-mini.pptx \
  --run-id <run_id> \
  --allow-run-id-reuse
python validate_artifact.py \
  --schema doc_web_bundle_manifest_v1 \
  --file output/runs/<run_id>/output/html/manifest.json
python validate_artifact.py \
  --schema doc_web_provenance_block_v1 \
  --file output/runs/<run_id>/output/html/provenance/blocks.jsonl
```

Story 197 established the first maintained PPTX slice on
`testdata/pptx-mini.pptx`. The current maintained claim is still intentionally
bounded to slide-numbered title/list/prose output on that verified probe
surface. Speaker notes, embedded media, charts, animations, and broader
mixed-layout deck ownership remain out of scope for this lane.

Expected bundle outputs:

- `output/runs/<run_id>/01_unstructured_pptx_intake_v1/elements.jsonl`
- `output/runs/<run_id>/02_pptx_elements_to_bundle_v1/pptx_bundle_report.json`
- `output/runs/<run_id>/output/html/index.html`
- `output/runs/<run_id>/output/html/page-001.html`
- `output/runs/<run_id>/output/html/page-00N.html` for any additional supported slide entry
- `output/runs/<run_id>/output/html/manifest.json`
- `output/runs/<run_id>/output/html/provenance/blocks.jsonl`

Alternative supported install shape for this lane:

- `python -m pip install -r requirements.txt` on Python 3.11/3.12

### Repo-Owned Web-Page Intake Smoke

Use this when you need a cheap real-run proof that the maintained bounded
web-page lane still emits a stamped `page_html_v1` artifact plus a final
`doc-web` bundle from the checked-in HTML snapshot:

```bash
python -m pip install '.[driver]'
python driver.py \
  --recipe configs/recipes/recipe-web-page-html-mvp.yaml \
  --input-html testdata/web-page-mini.html \
  --run-id <run_id> \
  --allow-run-id-reuse
python validate_artifact.py \
  --schema page_html_v1 \
  --file output/runs/<run_id>/01_web_page_html_intake_v1/pages_html.jsonl
python validate_artifact.py \
  --schema doc_web_bundle_manifest_v1 \
  --file output/runs/<run_id>/output/html/manifest.json
python validate_artifact.py \
  --schema doc_web_provenance_block_v1 \
  --file output/runs/<run_id>/output/html/provenance/blocks.jsonl
```

Story 200 established the first maintained web-page slice on
`testdata/web-page-mini.html`, a checked-in static HTML snapshot captured from
`https://example.com/`. The maintained claim is intentionally narrow: one
repo-owned HTML snapshot with clear heading/prose structure, routed through the
existing `page_html_v1` to `doc-web` chain. Live URL fetch, JavaScript-rendered
pages, multi-page crawling, and broader website cleanup remain out of scope.

Expected bundle outputs:

- `output/runs/<run_id>/01_web_page_html_intake_v1/pages_html.jsonl`
- `output/runs/<run_id>/02_extract_page_numbers_html_v1/pages_html_with_page_numbers.jsonl`
- `output/runs/<run_id>/03_portionize_headings_html_v1/portions_non_toc.jsonl`
- `output/runs/<run_id>/output/html/index.html`
- `output/runs/<run_id>/output/html/chapter-001.html`
- `output/runs/<run_id>/output/html/manifest.json`
- `output/runs/<run_id>/output/html/provenance/blocks.jsonl`

These maintained office-native lanes plus the bounded web-page lane are still
direct explicit-recipe entry points. They are not part of the
recommendation-only contact-sheet benchmark or the approved-handoff automation
surface.

### Office Intake Boundary Probe

Use this when you need a cheap rerunnable proof that office files remain
outside recommendation-only intake automation and approved handoff while the
direct DOCX/XLSX/PPTX smoke lanes above stay maintained separately:

```bash
python benchmarks/scripts/run_auto_book_type_detection_eval.py \
  --corpus benchmarks/input/office-intake-boundary-corpus.json \
  --output benchmarks/results/auto-book-type-detection-story194-office-boundary.json \
  --run-root output/runs/story194-auto-book-type-detection-office-boundary

python benchmarks/scripts/run_approved_intake_handoff_eval.py \
  --corpus benchmarks/input/office-intake-boundary-corpus.json \
  --output benchmarks/results/approved-intake-handoff-story194-office-boundary.json \
  --run-root output/runs/story194-approved-intake-handoff-office-boundary
```

Expected outcome:

- `docx`, `xlsx`, and `pptx` return explicit blocked scope rows that point
  back to the maintained direct explicit-recipe office lanes
- no office probe should crash inside `contact_sheet_builder_v1`

---

## 🔄 Recovery & Resume (The "Happy Path")

**Scenario:** The pipeline crashed (API error, quota limit, timeout) mid-run.
**Goal:** Resume without losing expensive OCR data.

### 1. Identify Failed Stage
Check `output/runs/<run_id>/pipeline_events.jsonl` or `driver.log`.

### 2. Resume Command
**Crucial:** Remove `--force`. Add `--start-from <stage_id>`.

```bash
scripts/run_driver_monitored.sh \
  --recipe <original_recipe> \
  --run-id <original_run_id> \
  --output-dir output/runs \
  -- --instrument --start-from <failed_stage_id>
```

*   **`--start-from <stage_id>`**: Driver loads state up to this stage and resumes execution.
*   **Automatic Skipping:** Most expensive modules (OCR, Extract) support internal resuming. If they see partial output, they skip completed items.
*   **`--skip-done`**: Optional. Tells driver to skip any stage that has a valid output artifact in `pipeline_state.json`. Useful if you aren't sure exactly which stage failed but know earlier ones are good.

---

## 🛠️ Configuration Reference

### Recipes (`configs/recipes/`)
| Recipe | Purpose |
| :--- | :--- |
| `recipe-images-ocr-html-mvp.yaml` | Active structural HTML bundle path for image-directory inputs. |
| `recipe-pdf-ocr-html-mvp.yaml` | Active structural HTML bundle path for generic PDF-backed inputs. |
| `recipe-docx-html-mvp.yaml` | Maintained DOCX structural bundle path for the repo-owned heading/prose/list/table slice, widened to three checked-in fixtures. |
| `recipe-pptx-html-mvp.yaml` | Maintained PPTX structural bundle path for the verified bounded slide slice: one HTML page per supported slide entry with slide-number provenance. |
| `recipe-web-page-html-mvp.yaml` | Maintained checked-HTML web-page path for one repo-owned static snapshot that reuses the existing `page_html_v1` to `doc-web` chain. |
| `recipe-xlsx-html-mvp.yaml` | Maintained XLSX structural bundle path for the verified simple-table slice: one HTML page per supported sheet/entry, including multiple table regions on one sheet, with anchor-based provenance. |
| `recipe-onward-images-html-mvp.yaml` | **Genealogy.** Specialized for *Onward* tables. |
| `recipe-onward-pdf-html-mvp.yaml` | **Genealogy.** PDF-backed maintained Onward lane with the same downstream table-repair flow. |
| `onward-genealogy-build-regression.yaml` | No-AI artifact-reuse regression path that rebuilds chapters and genealogy validation from accepted Onward artifacts already present under the shared `output/` root. |

### Presets (`configs/presets/`)
| Preset | Usage |
| :--- | :--- |
| `cost.ocr.yaml` | Low cost (gpt-4.1-mini). |
| `quality.ocr.yaml` | Max quality (gpt-5). |
| `speed.text.yaml` | Fast text processing. |

### CLI Overrides
Append these after `--` in the wrapper script.

*   `--model <name>`: Global model override.
*   `--input-pdf <path>`: Override `input.pdf` on maintained PDF-backed recipes.
*   `--input-docx <path>`: Override `input.docx` on maintained DOCX-backed recipes.
*   `--input-pptx <path>`: Override `input.pptx` on maintained PPTX-backed recipes.
*   `--input-html <path>`: Override `input.html` on maintained checked-HTML web-page recipes.
*   `--input-xlsx <path>`: Override `input.xlsx` on maintained XLSX-backed recipes.
*   `--max-pages <N>`: Stop after N pages.
*   `--start-from <stage>`: Resume point.
*   `--end-at <stage>`: Halt point.
*   `--dry-run`: Validate recipe/graph without execution.

---

## 🔍 Troubleshooting

### Common Failures

**429 RESOURCE_EXHAUSTED (Quota)**
*   **Fix:** Pause. Wait for quota reset (UTC midnight). Resume using **Recovery** steps above.

**TypeError: Object of type ResponseUsage...**
*   **Fix:** Code bug in Gemini client serialization. Update module to convert `usage` object to dict.

**KeyError: 'stage_id' (during resume)**
*   **Cause:** Artifacts missing. Did you use `--force` by mistake?
*   **Fix:** Restart from scratch or restore artifacts from backup.

### Monitoring
*   **Tail Logs:** `scripts/monitor_run.sh output/runs/<run_id> output/runs/<run_id>/driver.pid 5`
*   **Dashboard:** `python -m http.server 8000` -> `http://localhost:8000/docs/pipeline-visibility.html`

## Run Registry

Use the shared output-root registries before reusing an old run for validation or as an upstream.

Registry files:
*   `output/run_manifest.jsonl`: factual run index
*   `output/run_health.jsonl`: machine-generated health facts
*   `output/run_assessments.jsonl`: AI-written review judgments

### Reuse Safety Check

Ask the registry whether a run is safe for a specific scope before citing it as a validation source.

```bash
python tools/run_registry.py check-reuse \
  --run-id <run_id> \
  --scope page_presence
```

Recommended scopes:
*   `page_presence`
*   `chapter_structure`
*   `page_break_stitching`
*   `table_fidelity`
*   `full_book_fidelity`

If `recommendation` is `unsafe`, do not use that run for review even if older notes said it was good.

From a git worktree, omit `--output-root`; the CLI resolves the shared project `output/` root automatically. Only pass `--output-root` when you are intentionally targeting a different output tree.

### Recording Review Notes

When a human reviews a run in conversation, the AI should convert that judgment into a structured assessment entry.

```bash
python tools/run_registry.py record-assessment \
  --run-id <run_id> \
  --scope page_presence \
  --status unsafe \
  --summary "Missing printed pages 6 and 8 in source page HTML." \
  --finding "Pages 6 and 8 are empty in extract_page_numbers_html output." \
  --evidence output/runs/<run_id>/05_extract_page_numbers_html_v1/pages_html.jsonl
```

Assessments are scope-specific. A run can be safe for one scope and unsafe for another.
