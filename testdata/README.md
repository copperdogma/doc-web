# Test Data Fixtures

- `tbotb-mini.md` / `tbotb-mini.pdf`: 8-section micro branch adapted from **To Be or Not To Be** by Ryan North (2013). Licensed **CC BY-NC 3.0**; used here for non-commercial smoke testing. Source PDF: `input/Ryan North - To Be or Not To Be.pdf` (not modified).
- Story 157 uses `tbotb-mini.pdf` as the repo-owned maintained PDF-entry smoke fixture. It proves PDF-backed recipe wiring and extractor provenance, but it is not evidence that `scanned-pdf-prose` or native `born-digital-pdf` support is complete.
- `flat-born-digital-mini.md` / `flat-born-digital-mini.pdf`: repo-owned flat born-digital prose packet with no TOC and no printed page numbers. Story 171 uses it to prove the maintained non-TOC born-digital PDF lane can emit a final `doc-web` bundle without relying only on local user assets.
- `scanned-prose-mini.md` / `scanned-prose-mini.pdf`: original repo-owned prose source plus a generated image-only PDF fixture for `scanned-pdf-prose`. Story 167 uses it to prove maintained scanned-PDF entry, `page_image_v1` provenance, and a clean simple-prose OCR lane without relying on a shared local asset. This is passing evidence for the repo-owned simple-prose fixture, not a blanket claim about degraded or noisy scanned prose.
- `docx-mini.source.json` / `docx-mini.docx`: repo-owned DOCX fixture generated from checked-in structured source data. Story 172 uses it to prove the first maintained DOCX lane on the narrow supported slice: document title, heading-based sections, prose, simple bullet lists, and a simple table. Provenance is block-anchor based rather than page-based because DOCX is pageless in this lane.
- `docx-structured.source.json` / `docx-structured.docx`: repo-owned widened DOCX fixture for the currently claimed maintained slice. Story 175 uses it to prove the lane still holds on a broader heading-based document with longer prose, repeated simple lists, and repeated simple tables.
- `docx-page-break.source.json` / `docx-page-break.docx`: repo-owned DOCX boundary fixture with an explicit manual page break between sections. Story 175 uses it to confirm the lane still builds clean final artifacts with pageless block provenance, while keeping page-break semantics outside the maintained claim.

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
  ```
- Image-only scanned prose PDF:
  ```bash
  python testdata/generate_scanned_prose_fixture.py
  ```
- DOCX fixture:
  ```bash
  python testdata/generate_docx_fixture.py
  python testdata/generate_docx_fixture.py --source testdata/docx-structured.source.json --output testdata/docx-structured.docx
  python testdata/generate_docx_fixture.py --source testdata/docx-page-break.source.json --output testdata/docx-page-break.docx
  ```
- Optional image-only verification:
  ```bash
  python - <<'PY'
  from pypdf import PdfReader

  reader = PdfReader('testdata/scanned-prose-mini.pdf')
  print([len((page.extract_text() or '').strip()) for page in reader.pages])
  PY
  ```
