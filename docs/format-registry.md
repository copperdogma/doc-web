# Format Registry

Living document tracking codex-forge's format conversion capabilities. This is the north star — the goal is to handle every format Storybook users throw at us, with 100% accuracy, and graduate proven converters to Dossier.

Machine-readable source: `tests/fixtures/formats/_coverage-matrix.json`

## Current Status

**6 formats passing** | **0 graduated** | **10 untested** | **16 total tracked**

## Format Coverage

### Passing (pipeline built and tested)

| Format | Family | Intake Module | Text Fidelity | Structure | Illustrations | Provenance | Fixtures | Notes |
|--------|--------|---------------|--------------|-----------|---------------|------------|----------|-------|
| Scanned PDF (prose) | scanned-pdf | `extract_pdf_images_fast_v1` → `ocr_ai_gpt51_v1` | 0.97 | 0.95 | 0.856 | **0.984** | 1 | Primary pipeline. FF gamebook. |
| Scanned PDF (tables) | scanned-pdf | images → OCR → `table_rescue_html_loop_v1` | 0.93 | 0.95 | 0.856 | **0.956** | 1 | Claude Opus 4.6 single-call. Story 131. |
| Image directory | image-directory | `images_dir_to_manifest_v1` → `ocr_ai_gpt51_v1` | 0.93 | 0.95 | 0.856 | **0.956** | 1 | Same quality as PDF path. |
| Plain text | plain-text | `extract_text_v1` | 1.0 | — | — | — | 0 | Passthrough, no OCR. |
| Markdown | markdown | `extract_text_v1` | 1.0 | — | — | — | 0 | Passthrough. |
| HTML | html | `extract_text_v1` | 1.0 | — | — | — | 0 | Passthrough. |

### Has Fixture (test document exists, pipeline not yet passing)

(none currently)

### Untested (identified but no pipeline or fixtures)

| Format | Family | Complexity | Priority | Notes |
|--------|--------|------------|----------|-------|
| Born-digital PDF | born-digital-pdf | prose, tables, illustrations | High | Currently wastefully OCR'd. Should extract embedded text directly. |
| Word (.docx) | docx | prose, tables, illustrations | High | Storybook users will have these. python-docx or Unstructured. |
| Excel (.xlsx) | xlsx | tables | Medium | Family trees, genealogy data often in spreadsheets. |
| PowerPoint (.pptx) | pptx | mixed-layout, illustrations | Low | Less common for Storybook use cases. |
| EPUB | epub | prose, illustrations | Medium | E-books. Essentially zipped HTML + images. |
| Email (.eml) | email | prose | Medium | Personal correspondence, family letters. |
| Email archive (.mbox) | email | prose | Medium | Bulk email collections. |
| Web page | web-page | mixed-layout, illustrations | Medium | Online genealogy sites, memorial pages, articles. |
| Handwritten notes | handwritten | handwritten, degraded | High | Photos of letters, diaries, notebooks. VLM-based transcription. |
| Mixed archive | mixed-archive | mixed | Low | ZIP/folder with grab-bag of types. Needs format detection + routing. |

### Graduated (migrated to Dossier)

(none yet)

## Accuracy Dimensions

Every format is measured on four dimensions:

- **Text Fidelity** — Character-level accuracy vs source (target: ≥0.99)
- **Structure Preservation** — Tables, columns, headers, lists (target: ≥0.95)
- **Illustration Extraction** — Detection, cropping, cataloging (target: ≥0.95)
- **Provenance Completeness** — Every output traces to source page/location (target: 1.0). Measured by `scripts/measure_provenance.py` across 4 sub-dimensions: envelope fields (schema_version, module_id, run_id, created_at), page tracing, OCR confidence metadata, and gamebook section provenance.

## Known Gaps (Prioritized)

### Gap 1: Illustration Crop Quality — all image formats
- **Score:** 0.856 (eval: `image-crop-extraction`)
- **Root cause:** Two-stage detector+validator (spec compromise C4). VLM bounding boxes absorb nearby text.
- **Fix category:** Model improvement — waiting for single-model ≥0.95
- **Story:** Tracked in eval registry
- **Status:** Blocked on better models

### Gap 2: Provenance Envelope Gaps — scanned-pdf-prose, scanned-pdf-tables
- **Score:** 0.984 (prose), 0.956 (tables) → **Target:** 1.0
- **Root cause:** Several modules don't stamp all envelope fields:
  - `extract_pdf_images_fast_v1` — missing schema_version, module_id, run_id, created_at on raw image records (driver stamps only JSONL, this module writes its own)
  - `detect_boundaries_html_loop_v1` — boundary records missing envelope on ~47% of records
  - `build_chapter_html_v1` — emits no envelope fields at all
  - `portionize_headings_html_v1` — missing run_id, created_at
  - `load_artifact_v1` — loaded portion records missing run_id, created_at
- **Fix category:** `pipeline-improvement` — add envelope stamping to these modules
- **Estimated lift:** 0.984 → 1.0 (prose), 0.956 → 1.0 (tables)
- **Story:** Needs story
- **Status:** Measured 2026-03-10. Quick fix — each module just needs to populate envelope fields.
- **Measurement tool:** `python scripts/measure_provenance.py output/runs/<run_id> [--verbose] [--json]`

### Gap 3: Born-Digital PDF Text Extraction
- **Score:** N/A (untested)
- **Root cause:** No pipeline. Currently runs through OCR which is wasteful and lossy for born-digital PDFs.
- **Fix category:** New intake module — extract embedded text + images directly.
- **Estimated lift:** New capability
- **Story:** —
- **Status:** Needs story

### Gap 4: Office Document Support (DOCX/XLSX/PPTX)
- **Score:** N/A (untested)
- **Root cause:** No pipeline. Most common format for Storybook user uploads.
- **Fix category:** New intake modules.
- **Estimated lift:** New capability. High value for Storybook.
- **Story:** —
- **Status:** Needs story

### Gap 5: Handwritten Document Transcription
- **Score:** N/A (untested)
- **Root cause:** No pipeline. VLMs can transcribe handwriting but no intake module exists.
- **Fix category:** New intake module using VLM transcription.
- **Estimated lift:** New capability. High value for personal/family documents.
- **Story:** —
- **Status:** Needs story

## Resolved Gaps

### Resolved Gap: Table Structure Preservation — scanned-pdf-tables (Story 131)
- **Score:** 0.80 → 0.952 (Claude Opus 4.6)
- **Root cause was:** OCR lost column alignment on dense genealogy tables.
- **Fix:** LCS-aligned scorer, prompt engineering (section header separation, continuation row rules), model selection (Claude Opus 4.6).
- **Resolved:** 2026-03-10

## Graduation Criteria

A format converter is ready to graduate to Dossier when:
1. Text fidelity ≥ 0.99 on all test fixtures for that format
2. Structure preservation ≥ 0.95 (where applicable)
3. At least 3 diverse test fixtures passing
4. Converter has been stable (no changes) for 2+ stories
5. Dossier has an intake interface ready to accept the converter

## Next Actions

1. **Fix provenance envelope gaps** — 5 modules missing envelope fields. Quick win to reach 1.0 provenance. See Gap 2.
2. **Create story: Born-digital PDF intake** — Extract embedded text without OCR. Highest-value new capability.
3. **Create story: DOCX intake** — Most common Storybook user format.
4. **Create story: Handwritten transcription** — VLM-based, high value for personal documents.
5. **Expand test fixtures** — The three passing formats have minimal fixtures. Need more diverse test documents.
6. **Re-benchmark scanned-pdf-prose** — Scores 44 days stale, 3 recipe/module commits since last measurement.
