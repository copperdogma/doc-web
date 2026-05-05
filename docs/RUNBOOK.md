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
./scripts/install_with_age_gate.py '.[driver,email]'
./scripts/install_with_age_gate.py '.[driver,epub]'
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

### Runtime Preview

Use preview mode when a downstream consumer needs a fast, explicitly non-final
HTML/provenance artifact for an uploaded raw PDF, DOCX, or image directory:

```bash
python -m pip install .
doc-web preview \
  --input testdata/flat-born-digital-mini.pdf \
  --out-dir output/runs/preview-flat-born-digital/output/html \
  --json
```

Preview mode writes a normal bundle root plus preview sidecars:

- `manifest.json`
- `index.html`
- `page-*.html` or `chapter-*.html`
- `provenance/blocks.jsonl`
- `preview_metadata.json`
- `preview_status.jsonl`
- `preview_to_full_selectors.json`
- `cache/cache_identity.json`
- `cache/parsed_units.jsonl`

Validate preview artifacts with:

```bash
python validate_artifact.py --schema doc_web_bundle_manifest_v1 \
  --file output/runs/preview-flat-born-digital/output/html/manifest.json
python validate_artifact.py --schema doc_web_provenance_block_v1 \
  --file output/runs/preview-flat-born-digital/output/html/provenance/blocks.jsonl
python validate_artifact.py --schema doc_web_preview_metadata_v1 \
  --file output/runs/preview-flat-born-digital/output/html/preview_metadata.json
python validate_artifact.py --schema doc_web_preview_selector_map_v1 \
  --file output/runs/preview-flat-born-digital/output/html/preview_to_full_selectors.json
```

The preview metadata `coverage_state` is authoritative. `deferred` means
`doc-web` found structural facts but did not produce source text inside the
preview budget. Dossier and Storybook may show this state, but should not claim
OCR quality or extracted facts beyond the emitted metadata. A later full
processing job may reuse `cache/parsed_units.jsonl` only when
`cache/cache_identity.json` matches the source and runtime settings.
For image directories, preview mode counts the image inventory, hashes the
directory source, and runs bounded Tesseract OCR over a small sample to populate
non-final preview text and `content_hint` when possible. If the OCR sample
cannot produce usable text inside the preview budget, the preview remains
honestly `deferred` and leaves `provenance/blocks.jsonl` empty until full OCR
runs.
Content hints default to `--content-hint-mode auto`: when
`DOC_WEB_OPENAI_API_KEY` is available, `doc-web` asks a bounded cheap OpenAI
model for one direct summary sentence over the already-sampled text. If the key
is absent, the call times out, or the model returns unusable JSON, preview keeps
the bundle valid and records the deterministic fallback in `content_hint`.

For the maintained XLSX lane, add the explicit XLSX extra:

```bash
python -m pip install '.[driver,xlsx]'
```

For the maintained PPTX lane, add the explicit PPTX extra:

```bash
python -m pip install '.[driver,pptx]'
```

For the maintained EPUB lane, add the explicit EPUB extra and ensure `pandoc`
is available on `PATH`:

```bash
python -m pip install '.[driver,epub]'
```

For the maintained plain-text `.eml` lane, add the explicit email extra:

```bash
python -m pip install '.[driver,email]'
```

The fuller repo runtime from `requirements.txt` also now includes DOCX, EPUB,
XLSX, PPTX, and `.eml` support, but it is currently validated on Python 3.11/3.12
because the pinned `unstructured==0.16.9` dependency is limited to that range.

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
- `configs/recipes/recipe-email-eml-html-mvp.yaml`
- `configs/recipes/recipe-epub-html-mvp.yaml`
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

# Degraded synthetic scanned-prose OCR proof
python driver.py \
  --recipe configs/recipes/recipe-pdf-ocr-html-mvp.yaml \
  --input-pdf testdata/scanned-prose-degraded.pdf \
  --run-id <run_id> \
  --allow-run-id-reuse \
  --end-at ocr_ai
```

Expected extractor outputs:

- `output/runs/<run_id>/01_extract_pdf_images_fast_v1/pages_images_manifest.jsonl`
- `output/runs/<run_id>/01_extract_pdf_images_fast_v1/extraction_report.jsonl`
- `output/runs/<run_id>/01_extract_pdf_images_fast_v1/extraction_summary.json`

Notes:

- `testdata/tbotb-mini.pdf` proves maintained PDF entry wiring only for a small born-digital PDF.
- `testdata/scanned-prose-mini.pdf` is a repo-owned image-only simple-prose scanned fixture. Story 167 proved the maintained lane through `ocr_ai` and matched the checked-in source text exactly after normalization on 2026-03-27; broader noisy scanned-prose quality still needs separate validation.
- `testdata/scanned-prose-degraded.pdf` is a repo-owned image-only degraded/noisy synthetic scanned fixture generated from the same checked-in source text. The current preset is intentionally visibly rougher than the clean scanned-prose slice: softer text, lower contrast, added noise, mild skew, and faint edge shadow. Story 210 widened the bounded support slice on 2026-04-10 with fresh `ocr_ai` proof (`ocr_quality` `0.94-0.96`, normalized text ratio `0.996038`) while still leaving broader real-world degraded scanned-prose quality unclaimed.

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

### Repo-Owned MBOX Intake Smoke

Use this when you need a cheap real-run proof that the maintained bounded
plain-text `.mbox` lane still emits a final `doc-web` bundle plus pageless
provenance from the checked-in two-message archive fixture:

```bash
python -m pip install '.[driver,email]'
python driver.py \
  --recipe configs/recipes/recipe-email-mbox-html-mvp.yaml \
  --input-mbox testdata/email-mbox-mini.mbox \
  --run-id <run_id> \
  --allow-run-id-reuse
python validate_artifact.py \
  --schema doc_web_bundle_manifest_v1 \
  --file output/runs/<run_id>/output/html/manifest.json
python validate_artifact.py \
  --schema doc_web_provenance_block_v1 \
  --file output/runs/<run_id>/output/html/provenance/blocks.jsonl
```

Story 203 established the first maintained `.mbox` slice on
`testdata/email-mbox-mini.mbox`. The current maintained claim is intentionally
bounded to one plain-text multi-message fixture with stdlib `mailbox.mbox`
splitting, subject/from/to metadata preserved per message in `elements.jsonl`
and the bundle report, one HTML entry per message in archive order, and
pageless provenance via `source_element_ids`. Quoted-thread cleanup,
attachments, multipart HTML normalization, `.msg`, broader mixed-archive
ownership beyond the separate ZIP seam, and broader mailbox/thread ownership
remain out of scope for this lane.

Expected bundle outputs:

- `output/runs/<run_id>/01_mailbox_mbox_intake_v1/elements.jsonl`
- `output/runs/<run_id>/02_mbox_elements_to_bundle_v1/email_archive_bundle_report.json`
- `output/runs/<run_id>/output/html/index.html`
- `output/runs/<run_id>/output/html/page-001.html`
- `output/runs/<run_id>/output/html/page-002.html`
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

### Repo-Owned EPUB Intake Smoke

Use this when you need a cheap real-run proof that the maintained EPUB lane
still emits a final `doc-web` bundle plus pageless provenance from the
checked-in bounded probe fixture:

```bash
python -m pip install '.[driver,epub]'
python driver.py \
  --recipe configs/recipes/recipe-epub-html-mvp.yaml \
  --input-epub testdata/epub-mini.epub \
  --run-id <run_id> \
  --allow-run-id-reuse
python validate_artifact.py \
  --schema doc_web_bundle_manifest_v1 \
  --file output/runs/<run_id>/output/html/manifest.json
python validate_artifact.py \
  --schema doc_web_provenance_block_v1 \
  --file output/runs/<run_id>/output/html/provenance/blocks.jsonl
```

Additional non-Python requirement for this lane:

- `pandoc` on `PATH`

Story 201 established the first maintained EPUB slice on
`testdata/epub-mini.epub`. The current maintained claim is intentionally
bounded to chapter-first prose with one short list, package metadata carried
through as document title/creator, and pageless provenance via
`source_element_ids`. Image-only EPUBs, embedded media, footnotes, scripted
content, and broader ebook ownership remain out of scope for this lane.

Expected bundle outputs:

- `output/runs/<run_id>/01_unstructured_epub_intake_v1/elements.jsonl`
- `output/runs/<run_id>/02_epub_elements_to_bundle_v1/epub_bundle_report.json`
- `output/runs/<run_id>/output/html/index.html`
- `output/runs/<run_id>/output/html/chapter-001.html`
- `output/runs/<run_id>/output/html/chapter-002.html`
- `output/runs/<run_id>/output/html/manifest.json`
- `output/runs/<run_id>/output/html/provenance/blocks.jsonl`

Alternative supported install shape for this lane:

- `python -m pip install -r requirements.txt` on Python 3.11/3.12, with `pandoc` on `PATH`

### Repo-Owned EML Intake Smoke

Use this when you need a cheap real-run proof that the maintained bounded
plain-text `.eml` lane still emits a final `doc-web` bundle plus pageless
provenance from the checked-in single-message fixture:

```bash
python -m pip install '.[driver,email]'
python driver.py \
  --recipe configs/recipes/recipe-email-eml-html-mvp.yaml \
  --input-eml testdata/email-eml-mini.eml \
  --run-id <run_id> \
  --allow-run-id-reuse
python validate_artifact.py \
  --schema doc_web_bundle_manifest_v1 \
  --file output/runs/<run_id>/output/html/manifest.json
python validate_artifact.py \
  --schema doc_web_provenance_block_v1 \
  --file output/runs/<run_id>/output/html/provenance/blocks.jsonl
```

Story 202 established the first maintained `.eml` slice on
`testdata/email-eml-mini.eml`. The current maintained claim is intentionally
bounded to one plain-text single-message fixture with subject/from/to metadata
preserved in `elements.jsonl` and the bundle report, plus pageless provenance
via `source_element_ids`. Multipart HTML emails, quoted-thread cleanup,
attachments, `.msg`, and broader mailbox/thread ownership remain out of scope
for this lane.

Expected bundle outputs:

- `output/runs/<run_id>/01_unstructured_email_intake_v1/elements.jsonl`
- `output/runs/<run_id>/02_email_elements_to_bundle_v1/email_bundle_report.json`
- `output/runs/<run_id>/output/html/index.html`
- `output/runs/<run_id>/output/html/page-001.html`
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

These maintained DOCX/XLSX/PPTX/EPUB/EML direct-entry lanes plus the bounded
web-page lane are still direct explicit-recipe entry points. They are not part
of the recommendation-only contact-sheet benchmark or the approved-handoff
automation surface.

### Repo-Owned Mixed-Archive ZIP Intake Smoke

Use this when you need a cheap real-run proof that the first bounded
mixed-archive lane still emits an archive/member manifest, archive-member route
rows, nested downstream runs for supported members, and explicit blocked rows
for unsupported members:

```bash
python -m pip install '.[driver,docx,email]'
find modules -name "*.pyc" -delete
python driver.py \
  --recipe configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml \
  --input-zip testdata/mixed-archive-mini.zip \
  --run-id <run_id> \
  --allow-run-id-reuse
python validate_artifact.py \
  --schema archive_member_manifest_v1 \
  --file output/runs/<run_id>/01_archive_unpack_manifest_v1/archive_members_manifest.jsonl
python validate_artifact.py \
  --schema archive_member_route_v1 \
  --file output/runs/<run_id>/02_archive_route_members_v1/archive_member_routes.jsonl
```

Story 205 established the first maintained mixed-archive slice on the checked-in
`testdata/mixed-archive-mini.zip` fixture. The maintained claim is intentionally
narrow: one repo-owned ZIP archive with nested DOCX, plain-text `.eml`, and
static HTML members plus one intentionally unsupported `.txt` member; a stamped
archive/member manifest; member-level route rows with archive-relative
provenance; nested `driver.py` launches into existing maintained direct-entry
recipes for the supported members; and an explicit blocked row for the
unsupported member. That ZIP lane is now complemented by a separate bounded
direct-folder proof lane on the same member mix, a separate ZIP-only
PDF-member approved-handoff launch probe, a separate ZIP-only grouped
image-member first-artifact probe, a separate direct-folder born-digital
PDF-member approved-handoff probe, and a separate direct-folder grouped
image-member first-artifact probe; scanned or handwritten direct-folder
PDF-member routing, grouped-image continuation beyond the first downstream
`page_image_v1` artifact, nested archives, attachment extraction, and broad
heterogeneous archive normalization remain out of scope.

Expected outputs:

- `output/runs/<run_id>/01_archive_unpack_manifest_v1/archive_members_manifest.jsonl`
- `output/runs/<run_id>/02_archive_route_members_v1/archive_member_routes.jsonl`
- `output/runs/<member_run_id>/output/html/manifest.json` for each launched supported member run referenced from `archive_member_routes.jsonl`

These maintained DOCX/XLSX/PPTX/EPUB/EML direct-entry lanes plus the bounded
web-page and mixed-archive ZIP lanes are still explicit-recipe entry points.
They are not part of the recommendation-only contact-sheet benchmark or the
approved-handoff automation surface.

### Repo-Owned Mixed-Archive ZIP PDF-Member Approved-Handoff Launch Smoke

Use this when you need a cheap real-run proof that the bounded ZIP-only
PDF-member continuation emits an archive/member route row pointing at an
inspectable member-local `intake_plan_v1`, `intake_handoff_v1`, and launched
born-digital PDF child run while the `.eml` and HTML members still launch and
the unsupported `.txt` member still blocks:

```bash
python -m pip install '.[driver,email]'
find modules -name "*.pyc" -delete
python driver.py \
  --recipe configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml \
  --input-zip testdata/mixed-archive-pdf-mini.zip \
  --run-id <run_id> \
  --allow-run-id-reuse
python validate_artifact.py \
  --schema archive_member_manifest_v1 \
  --file output/runs/<run_id>/01_archive_unpack_manifest_v1/archive_members_manifest.jsonl
python validate_artifact.py \
  --schema archive_member_route_v1 \
  --file output/runs/<run_id>/02_archive_route_members_v1/archive_member_routes.jsonl
python validate_artifact.py \
  --schema intake_plan_v1 \
  --file output/runs/<run_id>-member-001-recipe-intake-contact-sheet/05_confirm_plan_v1/overview_plan_final.jsonl
python validate_artifact.py \
  --schema intake_handoff_v1 \
  --file output/runs/<run_id>/02_archive_route_members_v1/pdf_member_handoffs/member-001/intake_handoff.jsonl
```

Stories 221 and 223 established this bounded continuation on the checked-in
`testdata/mixed-archive-pdf-mini.zip` fixture. The maintained claim is
intentionally narrow: one repo-owned ZIP archive with a flat born-digital PDF
member, plain-text `.eml`, static HTML snapshot, and one intentionally
unsupported `.txt` member; a stamped archive/member manifest; a PDF member
route row with archive-relative provenance, `approval_mode =
confirm_plan_auto_approve`, `terminal_reason =
pdf_member_launched_from_approved_plan`, the emitted
`05_confirm_plan_v1/overview_plan_final.jsonl` plan artifact recorded as
`first_downstream_artifact`; a launched member-local
`02_archive_route_members_v1/pdf_member_handoffs/member-001/intake_handoff.jsonl`
artifact; a launched
`output/runs/<run_id>-member-001-approved-handoff-recipe-born-digital-pdf-non-toc-html-mvp/01_extract_pdf_marker_lite_html_v1/pages_html.jsonl`
artifact from the maintained born-digital PDF lane; existing maintained
direct-entry launches for the `.eml` and HTML members; and an explicit blocked
row for the unsupported member. It is not evidence for direct-folder
PDF-member routing, scanned or handwritten PDF-member launch, grouped
image-member routing, nested archives, attachment extraction, or broad
heterogeneous archive normalization.

Expected outputs:

- `output/runs/<run_id>/01_archive_unpack_manifest_v1/archive_members_manifest.jsonl`
- `output/runs/<run_id>/02_archive_route_members_v1/archive_member_routes.jsonl`
- `output/runs/<run_id>-member-001-recipe-intake-contact-sheet/05_confirm_plan_v1/overview_plan_final.jsonl`
- `output/runs/<run_id>/02_archive_route_members_v1/pdf_member_handoffs/member-001/intake_handoff.jsonl`
- `output/runs/<run_id>-member-001-approved-handoff-recipe-born-digital-pdf-non-toc-html-mvp/01_extract_pdf_marker_lite_html_v1/pages_html.jsonl`
- `output/runs/<run_id>-member-002-recipe-email-eml-html-mvp/output/html/manifest.json`
- `output/runs/<run_id>-member-003-recipe-web-page-html-mvp/output/html/manifest.json`

This bounded PDF-member continuation still sits outside the top-level
recommendation-only contact-sheet benchmark and the approved-handoff
automation surface. It starts from explicit `driver.py --recipe ... --input-zip`
entry and emits a nested approved plan, a launched member-local handoff
artifact, and a bounded born-digital PDF child run after the archive route
stage.

### Repo-Owned Mixed-Archive ZIP Grouped Image-Member Smoke

Use this when you need a cheap real-run proof that the bounded ZIP-only grouped
image-member continuation emits grouped route rows for a shared-parent page set,
launches exactly one `--input-images` child run, and reaches the first grouped
`page_html_v1` artifact while the unsupported `.txt` member still blocks
explicitly:

```bash
python -m pip install '.[driver]'
find modules -name "*.pyc" -delete
python driver.py \
  --recipe configs/recipes/recipe-mixed-archive-zip-routing-mvp.yaml \
  --input-zip testdata/mixed-archive-images-mini.zip \
  --run-id <run_id> \
  --allow-run-id-reuse \
  --force
python validate_artifact.py \
  --schema archive_member_manifest_v1 \
  --file output/runs/<run_id>/01_archive_unpack_manifest_v1/archive_members_manifest.jsonl
python validate_artifact.py \
  --schema archive_member_route_v1 \
  --file output/runs/<run_id>/02_archive_route_members_v1/archive_member_routes.jsonl
GROUP_RUN_ID="$(python - <<'PY'
import json
from pathlib import Path

rows = Path('output/runs/<run_id>/02_archive_route_members_v1/archive_member_routes.jsonl').read_text().splitlines()
for line in rows:
    row = json.loads(line)
    if row.get('group_role') == 'primary':
        print(row['downstream_run_id'])
        break
PY
)"
python validate_artifact.py \
  --schema page_image_v1 \
  --file output/runs/$GROUP_RUN_ID/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl
python validate_artifact.py \
  --schema page_html_v1 \
  --file output/runs/$GROUP_RUN_ID/02_ocr_ai_gpt51_v1/pages_html.jsonl
```

Story 224 established this bounded continuation on the checked-in
`testdata/mixed-archive-images-mini.zip` fixture. The maintained claim is
intentionally narrow: one repo-owned ZIP archive with two page-image members
under `pages/` plus one intentionally unsupported `.txt` member; a stamped
archive/member manifest; grouped member route rows with archive-relative
provenance plus shared `group_id`, `group_key`, `group_role`, `group_size`,
`launch_input_path`, `downstream_run_id`, and `first_downstream_artifact`
fields; one grouped `--input-images` child run into the maintained
`recipe-images-ocr-html-mvp.yaml` lane; the emitted
`01_images_dir_to_manifest_v1/pages_images_manifest.jsonl` artifact recorded as
`first_downstream_artifact`; the grouped `02_ocr_ai_gpt51_v1/pages_html.jsonl`
artifact derived from the shared child run id; and an explicit blocked row for
the unsupported member. The grouped continuation intentionally stops at
`ocr_ai` on this probe, because the checked-in two-page image set does not
claim the later table-rescue / TOC / HTML bundle surface. It is not evidence
for broad photo-album semantics, grouped-image continuation beyond the first
downstream `page_html_v1` artifact, scanned or handwritten OCR quality
changes, nested archives, attachment extraction, or broad heterogeneous
archive normalization.

Expected outputs:

- `output/runs/<run_id>/01_archive_unpack_manifest_v1/archive_members_manifest.jsonl`
- `output/runs/<run_id>/02_archive_route_members_v1/archive_member_routes.jsonl`
- `output/runs/<group_run_id>/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl`
- `output/runs/<group_run_id>/02_ocr_ai_gpt51_v1/pages_html.jsonl`

This bounded grouped-image continuation still sits outside the top-level
recommendation-only contact-sheet benchmark and the approved-handoff
automation surface. It starts from explicit `driver.py --recipe ... --input-zip`
entry and proves only the grouped route bridge plus the first downstream
stamped `page_html_v1` artifact.

### Repo-Owned Mixed-Folder PDF-Member Approved-Handoff Launch Smoke

Use this when you need a cheap real-run proof that the bounded direct-folder
PDF-member continuation emits a source-native member route row pointing at an
inspectable approved `intake_plan_v1` artifact, a launched member-local
`intake_handoff_v1` sidecar, and a launched born-digital PDF child run while
the `.eml` and HTML members still launch and the unsupported `.txt` member
still blocks:

```bash
python -m pip install '.[driver,email]'
find modules -name "*.pyc" -delete
python driver.py \
  --recipe configs/recipes/recipe-mixed-folder-routing-mvp.yaml \
  --input-folder testdata/mixed-folder-pdf-mini \
  --run-id <run_id> \
  --allow-run-id-reuse \
  --force
python validate_artifact.py \
  --schema archive_member_manifest_v1 \
  --file output/runs/<run_id>/01_folder_members_manifest_v1/archive_members_manifest.jsonl
python validate_artifact.py \
  --schema archive_member_route_v1 \
  --file output/runs/<run_id>/02_archive_route_members_v1/archive_member_routes.jsonl
python validate_artifact.py \
  --schema intake_plan_v1 \
  --file output/runs/<run_id>-member-001-recipe-intake-contact-sheet/05_confirm_plan_v1/overview_plan_final.jsonl
python validate_artifact.py \
  --schema intake_handoff_v1 \
  --file output/runs/<run_id>/02_archive_route_members_v1/pdf_member_handoffs/member-001/intake_handoff.jsonl
```

Story 222 established the direct-folder recommendation substrate on the
checked-in `testdata/mixed-folder-pdf-mini/` fixture, and Story 223 extends
that same fixture to the maintained approved-handoff launch continuation. The
maintained claim is intentionally narrow: one repo-owned source-native folder
tree with a flat born-digital PDF member, plain-text `.eml`, static HTML
snapshot, and one intentionally unsupported `.txt` member; a stamped member
manifest that keeps `extracted_path` source-native; a PDF member route row
with relative provenance, `terminal_reason = pdf_member_launched_from_approved_plan`,
`approval_mode = confirm_plan_auto_approve`, the emitted
`05_confirm_plan_v1/overview_plan_final.jsonl` plan artifact recorded as
`first_downstream_artifact`, a launched `intake_handoff_v1` sidecar, and a
launched
`output/runs/<run_id>-member-001-approved-handoff-recipe-born-digital-pdf-non-toc-html-mvp/01_extract_pdf_marker_lite_html_v1/pages_html.jsonl`
artifact; existing maintained direct-entry launches for the `.eml` and HTML
members; and an explicit blocked row for the unsupported member. It is not
evidence for scanned or handwritten direct-folder PDF-member launch, grouped
image-member routing, nested archives, attachment extraction, or broad
heterogeneous archive normalization.

Expected outputs:

- `output/runs/<run_id>/01_folder_members_manifest_v1/archive_members_manifest.jsonl`
- `output/runs/<run_id>/02_archive_route_members_v1/archive_member_routes.jsonl`
- `output/runs/<run_id>-member-001-recipe-intake-contact-sheet/05_confirm_plan_v1/overview_plan_final.jsonl`
- `output/runs/<run_id>/02_archive_route_members_v1/pdf_member_handoffs/member-001/intake_handoff.jsonl`
- `output/runs/<run_id>-member-001-approved-handoff-recipe-born-digital-pdf-non-toc-html-mvp/01_extract_pdf_marker_lite_html_v1/pages_html.jsonl`
- `output/runs/<run_id>-member-002-recipe-email-eml-html-mvp/output/html/manifest.json`
- `output/runs/<run_id>-member-004-recipe-web-page-html-mvp/output/html/manifest.json`

This bounded direct-folder PDF-member continuation still sits outside the
top-level recommendation-only contact-sheet benchmark and the approved-handoff
automation surface. It starts from explicit `driver.py --recipe ... --input-folder`
entry and emits a nested approved plan, a launched member-local handoff
artifact, and a bounded born-digital PDF child run after the archive route
stage.

### Repo-Owned Mixed-Folder Grouped Image-Member Smoke

Use this when you need a cheap real-run proof that the bounded direct-folder
grouped image-member continuation emits grouped route rows for a shared-parent
page set, launches exactly one source-native `--input-images` child run, and
reaches the first grouped `page_html_v1` artifact while the unsupported `.txt`
member still blocks explicitly:

```bash
python -m pip install '.[driver]'
find modules -name "*.pyc" -delete
python driver.py \
  --recipe configs/recipes/recipe-mixed-folder-routing-mvp.yaml \
  --input-folder testdata/mixed-folder-images-mini \
  --run-id <run_id> \
  --allow-run-id-reuse \
  --force
python validate_artifact.py \
  --schema archive_member_manifest_v1 \
  --file output/runs/<run_id>/01_folder_members_manifest_v1/archive_members_manifest.jsonl
python validate_artifact.py \
  --schema archive_member_route_v1 \
  --file output/runs/<run_id>/02_archive_route_members_v1/archive_member_routes.jsonl
GROUP_RUN_ID="$(python - <<'PY'
import json
from pathlib import Path

rows = Path('output/runs/<run_id>/02_archive_route_members_v1/archive_member_routes.jsonl').read_text().splitlines()
for line in rows:
    row = json.loads(line)
    if row.get('group_role') == 'primary':
        print(row['downstream_run_id'])
        break
PY
)"
python validate_artifact.py \
  --schema page_image_v1 \
  --file output/runs/$GROUP_RUN_ID/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl
python validate_artifact.py \
  --schema page_html_v1 \
  --file output/runs/$GROUP_RUN_ID/02_ocr_ai_gpt51_v1/pages_html.jsonl
```

Story 224 widened the same grouped-image seam to this checked-in
`testdata/mixed-folder-images-mini/` source-native folder fixture. The
maintained claim is intentionally narrow: one repo-owned source-native folder
tree with two page-image members under `pages/` plus one intentionally
unsupported `.txt` member; a stamped member manifest that keeps
`extracted_path` and `launch_input_path` source-native; grouped member route
rows with relative provenance plus shared `group_id`, `group_key`,
`group_role`, `group_size`, `downstream_run_id`, and
`first_downstream_artifact` fields; one grouped `--input-images` child run
into the maintained `recipe-images-ocr-html-mvp.yaml` lane; the emitted
`01_images_dir_to_manifest_v1/pages_images_manifest.jsonl` artifact recorded as
`first_downstream_artifact`; the grouped `02_ocr_ai_gpt51_v1/pages_html.jsonl`
artifact derived from the shared child run id; and an explicit blocked row for
the unsupported member. The grouped continuation intentionally stops at
`ocr_ai` on this probe, because the checked-in two-page image set does not
claim the later table-rescue / TOC / HTML bundle surface. It is not evidence
for broad photo-album semantics, grouped-image continuation beyond the first
downstream `page_html_v1` artifact, scanned or handwritten OCR quality
changes, nested archives, attachment extraction, or
broad heterogeneous archive normalization.

Expected outputs:

- `output/runs/<run_id>/01_folder_members_manifest_v1/archive_members_manifest.jsonl`
- `output/runs/<run_id>/02_archive_route_members_v1/archive_member_routes.jsonl`
- `output/runs/<group_run_id>/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl`
- `output/runs/<group_run_id>/02_ocr_ai_gpt51_v1/pages_html.jsonl`

This bounded grouped-image continuation still sits outside the top-level
recommendation-only contact-sheet benchmark and the approved-handoff
automation surface. It starts from explicit `driver.py --recipe ... --input-folder`
entry and proves only the grouped route bridge plus the first downstream
stamped `page_html_v1` artifact.

### Repo-Owned Mixed-Folder Intake Smoke

Use this when you need a cheap real-run proof that the bounded source-native
folder lane still emits a member manifest, archive-member route rows, nested
downstream runs for supported members, and an explicit blocked row for the
unsupported member:

```bash
python -m pip install '.[driver,docx,email]'
find modules -name "*.pyc" -delete
python driver.py \
  --recipe configs/recipes/recipe-mixed-folder-routing-mvp.yaml \
  --input-folder testdata/mixed-folder-mini \
  --run-id <run_id> \
  --force
python validate_artifact.py \
  --schema archive_member_manifest_v1 \
  --file output/runs/<run_id>/01_folder_members_manifest_v1/archive_members_manifest.jsonl
python validate_artifact.py \
  --schema archive_member_route_v1 \
  --file output/runs/<run_id>/02_archive_route_members_v1/archive_member_routes.jsonl
```

Use a fresh `<run_id>` for clean reruns of this bounded proof. Reusing the
same parent run id after nested member runs already exist currently collides
with those child output directories; `--allow-run-id-reuse` is only useful for
resume-style recovery before that nested output tree is already populated.

Story 218 established the first maintained direct-folder continuation of the
same bounded mixed-input seam on the checked-in `testdata/mixed-folder-mini/`
fixture. The maintained claim is intentionally narrow: one repo-owned folder
tree with nested DOCX, plain-text `.eml`, and static HTML members plus one
intentionally unsupported `.txt` member; a stamped member manifest that keeps
`extracted_path` source-native; member-level route rows with relative
provenance; nested `driver.py` launches into existing maintained direct-entry
recipes for the supported members; and an explicit blocked row for the
unsupported member. Story 222 adds a second bounded direct-folder probe for one
born-digital PDF member, and Story 223 extends that same probe through a
member-local approved-handoff launch into the maintained born-digital PDF
recipe. Story 224 adds a third bounded direct-folder probe for one grouped
page-image member set and extends that same route/module line through the
first downstream `page_html_v1` artifact; scanned or handwritten PDF-member
launch, grouped-image continuation beyond that first artifact, nested
archives, attachment extraction, and broad heterogeneous folder/archive
normalization remain out of scope.

Expected outputs:

- `output/runs/<run_id>/01_folder_members_manifest_v1/archive_members_manifest.jsonl`
- `output/runs/<run_id>/02_archive_route_members_v1/archive_member_routes.jsonl`
- `output/runs/<member_run_id>/output/html/manifest.json` for each launched supported member run referenced from `archive_member_routes.jsonl`

These maintained DOCX/XLSX/PPTX/EPUB/EML direct-entry lanes plus the bounded
web-page, mixed-archive ZIP, and mixed-folder lanes are still explicit-recipe
entry points. The mixed-archive ZIP PDF-member continuation, the mixed-archive
ZIP grouped image-member continuation, and the mixed-folder PDF-member
continuation, and the mixed-folder grouped image-member continuation all emit
bounded member-local continuations after explicit entry; none is part of the
top-level recommendation-only contact-sheet benchmark or the approved-handoff
automation surface.

### Office Intake Boundary Probe

Use this when you need a cheap rerunnable proof that direct-entry files remain
outside recommendation-only intake automation and approved handoff while the
direct DOCX/XLSX/PPTX/EPUB smoke lanes above stay maintained separately:

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

- `docx`, `email-eml`, `email-mbox`, `epub`, `xlsx`, and `pptx` return explicit blocked scope rows that point
  back to the maintained direct explicit-recipe lanes
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
| `recipe-email-eml-html-mvp.yaml` | Maintained plain-text `.eml` structural bundle path for one verified single-message slice with pageless provenance. |
| `recipe-email-mbox-html-mvp.yaml` | Maintained plain-text `.mbox` structural bundle path for one verified two-message archive slice with one HTML entry per message and pageless provenance. |
| `recipe-epub-html-mvp.yaml` | Maintained EPUB structural bundle path for the verified bounded chapter-first prose slice with pageless provenance. |
| `recipe-mixed-archive-zip-routing-mvp.yaml` | Maintained ZIP-only mixed-archive path that manifests archive members, routes supported members into existing direct-entry recipes, records blocked members explicitly, and includes bounded ZIP-only PDF-member and grouped image-member OCR-boundary continuations on checked-in probes. |
| `recipe-mixed-folder-routing-mvp.yaml` | Maintained source-native mixed-folder path that inventories bounded folder trees, routes supported members into existing direct-entry recipes, and records blocked members explicitly, including one direct-folder PDF-member approved-handoff launch continuation and one direct-folder grouped image-member OCR-boundary continuation. |
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
*   `--input-eml <path>`: Override `input.eml` on maintained plain-text `.eml` recipes.
*   `--input-mbox <path>`: Override `input.mbox` on maintained plain-text `.mbox` recipes.
*   `--input-epub <path>`: Override `input.epub` on maintained EPUB-backed recipes.
*   `--input-folder <path>`: Override `input.folder` on the maintained mixed-folder routing recipe.
*   `--input-zip <path>`: Override `input.zip` on the maintained ZIP-only mixed-archive recipe.
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
