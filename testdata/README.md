# Test Data Fixtures

- `tbotb-mini.md` / `tbotb-mini.pdf`: 8-section micro branch adapted from **To Be or Not To Be** by Ryan North (2013). Licensed **CC BY-NC 3.0**; used here for non-commercial smoke testing. Source PDF: `input/Ryan North - To Be or Not To Be.pdf` (not modified).
- Story 157 uses `tbotb-mini.pdf` as the repo-owned maintained PDF-entry smoke fixture. It proves PDF-backed recipe wiring and extractor provenance, but it is not evidence that `scanned-pdf-prose` or native `born-digital-pdf` support is complete.
- `flat-born-digital-mini.md` / `flat-born-digital-mini.pdf`: repo-owned flat born-digital prose packet with no TOC and no printed page numbers. Story 171 uses it to prove the maintained non-TOC born-digital PDF lane can emit a final `doc-web` bundle without relying only on local user assets.
- `flat-born-digital-form-mini.md` / `flat-born-digital-form-mini.pdf`: repo-owned flat born-digital form-like packet with short label-style sections and an all-caps warning block. Story 177 uses it to widen the repeatable proof surface beyond the original prose-only mini fixture and to measure whether oversized in-body headings are a generic rough edge on the maintained non-TOC lane.
- `scanned-prose-mini.md` / `scanned-prose-mini.pdf`: original repo-owned prose source plus a generated image-only PDF fixture for `scanned-pdf-prose`. Story 167 uses it to prove maintained scanned-PDF entry, `page_image_v1` provenance, and a clean simple-prose OCR lane without relying on a shared local asset. This is passing evidence for the repo-owned simple-prose fixture, not a blanket claim about degraded or noisy scanned prose.
- `handwritten-notes-mini.txt` / `handwritten-notes-mini-images/` / `handwritten-notes-mini.pdf`: repo-owned synthetic handwritten-notes fixture generated from a checked-in transcript via `generate_handwritten_notes_fixture.py`. Story 179 uses it to prove the narrow, highly legible handwritten-note slice on the maintained generic image-directory and PDF OCR lanes. This is passing evidence only for that synthetic legible slice, not for messy cursive, degraded diaries, or broader real-world handwriting.
- `docx-mini.source.json` / `docx-mini.docx`, `docx-sections-mini.source.json` / `docx-sections-mini.docx`, and `docx-nested-mini.source.json` / `docx-nested-mini.docx`: repo-owned DOCX fixture set generated from checked-in structured source data. Story 175 widens the maintained DOCX lane to three repo-owned fixtures on the supported slice: heading-based sections, prose, nested subheadings, simple bullet lists, and a simple table. Provenance remains block-anchor based rather than page-based because DOCX is pageless in this lane.
- `xlsx-mini.source.json` / `xlsx-mini.xlsx`: repo-owned XLSX workbook fixture with two simple table sheets (`Roster`, `Visits`). Story 175 uses it to prove the first maintained XLSX lane on the narrow supported slice: sheet-named entries, HTML table preservation, and anchor-based provenance with no fabricated page numbers.
- `pptx-mini.md` / `pptx-mini.pptx`: reproducible PPTX seam-probe fixture generated from checked-in markdown via `pandoc`. Story 175 uses it to make the current PPTX defer explicit: the probe file is repo-owned, but `unstructured.partition.pptx` still fails in this checkout because `python-pptx` is not installed.

Regeneration:
- PDF (requires `fpdf2`: `python -m pip install fpdf2` or use vendored `testdata/vendor`):  
  ```bash
  python - <<'PY'
  import sys
  from pathlib import Path
  sys.path.insert(0, str(Path('testdata/vendor').resolve()))
  from fpdf import FPDF

  src = Path('testdata/tbotb-mini.md').read_text().splitlines()
  pdf = FPDF()
  pdf.set_auto_page_break(auto=True, margin=15)
  pdf.add_page()
  pdf.set_font('Helvetica', 'B', 14)
  pdf.cell(0, 10, text='To Be or Not To Be -- Mini FF Branch', ln=1)
  pdf.set_font('Helvetica', '', 9)
  pdf.multi_cell(0, 5, text='Adapted from To Be or Not To Be by Ryan North (2013). Licensed CC BY-NC 3.0. For non-commercial smoke testing.')
  pdf.ln(4)

  for line in src:
      if line.startswith('## '):
          pdf.set_font('Helvetica', 'B', 12)
          pdf.cell(0, 8, line.replace('## ', '').strip(), ln=1)
          pdf.set_font('Helvetica', '', 11)
      elif line.startswith('#'):
          continue
      else:
          pdf.multi_cell(0, 6, line.strip())
          pdf.ln(1)

  Path('testdata/tbotb-mini.pdf').write_bytes(pdf.output(dest='S'))
  PY
  ```
- Optional images: `pdftoppm -png testdata/tbotb-mini.pdf testdata/tbotb-mini`
- Flat born-digital text PDF:
  ```bash
  python testdata/generate_flat_born_digital_fixture.py
  python testdata/generate_flat_born_digital_fixture.py --source testdata/flat-born-digital-form-mini.md --output testdata/flat-born-digital-form-mini.pdf
  ```
- Image-only scanned prose PDF:
  ```bash
  python testdata/generate_scanned_prose_fixture.py
  ```
- Synthetic handwritten-notes fixture:
  ```bash
  python testdata/generate_handwritten_notes_fixture.py
  ```
- DOCX fixtures:
  ```bash
  python testdata/generate_docx_fixture.py
  python testdata/generate_docx_fixture.py --source testdata/docx-sections-mini.source.json --output testdata/docx-sections-mini.docx
  python testdata/generate_docx_fixture.py --source testdata/docx-nested-mini.source.json --output testdata/docx-nested-mini.docx
  ```
- XLSX fixture:
  ```bash
  python testdata/generate_xlsx_fixture.py
  ```
- PPTX probe fixture (requires `pandoc`):
  ```bash
  python testdata/generate_pptx_fixture.py
  ```
- Optional image-only verification:
  ```bash
  python - <<'PY'
  from pypdf import PdfReader

  reader = PdfReader('testdata/scanned-prose-mini.pdf')
  print([len((page.extract_text() or '').strip()) for page in reader.pages])
  PY
  ```
  The same check should print `[0, 0]` for `testdata/handwritten-notes-mini.pdf`.
