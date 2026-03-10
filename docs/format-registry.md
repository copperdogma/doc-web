# Format Registry

Living document tracking codex-forge's format conversion capabilities. This is the north star — the goal is to handle every format Storybook users throw at us, with 100% accuracy, and graduate proven converters to Dossier.

Machine-readable source: `tests/fixtures/formats/_coverage-matrix.json`

## Current Status

**6 formats passing** | **0 graduated** | **10 untested** | **16 total tracked**

## Format Coverage

### Passing (pipeline built and tested)

| Format | Family | Intake Module | Text Fidelity | Structure | Illustrations | Fixtures | Notes |
|--------|--------|---------------|--------------|-----------|---------------|----------|-------|
| Scanned PDF (prose) | scanned-pdf | `extract_pdf_images_fast_v1` → `ocr_ai_gpt51_v1` | 0.97 | 0.95 | 0.856 | 1 | Primary pipeline. FF gamebook. |
| Scanned PDF (tables) | scanned-pdf | images → OCR → `table_rescue_html_loop_v1` | 0.93 | 0.80 | 0.856 | 1 | Tables are the weak point. |
| Image directory | image-directory | `images_dir_to_manifest_v1` → `ocr_ai_gpt51_v1` | 0.93 | 0.80 | 0.856 | 1 | Same quality as PDF path. |
| Plain text | plain-text | `extract_text_v1` | 1.0 | — | — | 0 | Passthrough, no OCR. |
| Markdown | markdown | `extract_text_v1` | 1.0 | — | — | 0 | Passthrough. |
| HTML | html | `extract_text_v1` | 1.0 | — | — | 0 | Passthrough. |

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
- **Provenance Completeness** — Every output traces to source page/location (target: 1.0)

## Known Gaps (Prioritized)

### Gap 1: Table Structure Preservation — scanned-pdf-tables
- **Score:** 0.80 structure preservation
- **Root cause:** OCR loses column alignment on dense genealogy tables. `table_rescue_html_loop_v1` partially recovers.
- **Fix category:** Pipeline improvement — better table-aware OCR or VLM-based table extraction.
- **Estimated lift:** +0.15 structure preservation
- **Story:** —
- **Status:** Diagnosed

### Gap 2: Illustration Crop Quality — all image formats
- **Score:** 0.856 (eval: `image-crop-extraction`)
- **Root cause:** Two-stage detector+validator (spec compromise C4). VLM bounding boxes absorb nearby text.
- **Fix category:** Model improvement — waiting for single-model ≥0.95
- **Story:** Tracked in eval registry
- **Status:** Blocked on better models

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

(none yet)

## Graduation Criteria

A format converter is ready to graduate to Dossier when:
1. Text fidelity ≥ 0.99 on all test fixtures for that format
2. Structure preservation ≥ 0.95 (where applicable)
3. At least 3 diverse test fixtures passing
4. Converter has been stable (no changes) for 2+ stories
5. Dossier has an intake interface ready to accept the converter

## Next Actions

1. **Create story: Born-digital PDF intake** — Extract embedded text without OCR. Highest-value quick win.
2. **Create story: DOCX intake** — Most common Storybook user format.
3. **Create story: Handwritten transcription** — VLM-based, high value for personal documents.
4. **Expand test fixtures** — The three passing formats have minimal fixtures. Need more diverse test documents.
5. **Run `/format-gap-analysis`** — After adding fixtures, diagnose gaps systematically.
