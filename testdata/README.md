# Test Data Fixtures

- `tbotb-mini.md` / `tbotb-mini.pdf`: 8-section micro branch adapted from **To Be or Not To Be** by Ryan North (2013). Licensed **CC BY-NC 3.0**; used here for non-commercial smoke testing. Source PDF: `input/Ryan North - To Be or Not To Be.pdf` (not modified).
- Story 157 uses `tbotb-mini.pdf` as the repo-owned maintained PDF-entry smoke fixture. It proves PDF-backed recipe wiring and extractor provenance, but it is not evidence that `scanned-pdf-prose` or native `born-digital-pdf` support is complete.
- `flat-born-digital-mini.md` / `flat-born-digital-mini.pdf`: repo-owned flat born-digital prose packet with no TOC and no printed page numbers. Story 171 uses it to prove the maintained non-TOC born-digital PDF lane can emit a final `doc-web` bundle without relying only on local user assets.
- `flat-born-digital-form-mini.md` / `flat-born-digital-form-mini.pdf`: repo-owned flat born-digital form-like packet with short label-style sections and an all-caps warning block. Story 177 uses it to widen the repeatable proof surface beyond the original prose-only mini fixture and to measure whether oversized in-body headings are a generic rough edge on the maintained non-TOC lane.
- `scanned-prose-mini.md` / `scanned-prose-mini.pdf`: original repo-owned prose source plus a generated image-only PDF fixture for `scanned-pdf-prose`. Story 167 uses it to prove maintained scanned-PDF entry, `page_image_v1` provenance, and a clean simple-prose OCR lane without relying on a shared local asset. This is passing evidence for the repo-owned simple-prose fixture, not a blanket claim about degraded or noisy scanned prose.
- `handwritten-notes-mini.txt` / `handwritten-notes-mini-images/` / `handwritten-notes-mini.pdf`: repo-owned synthetic handwritten-notes fixture generated from a checked-in transcript via `generate_handwritten_notes_fixture.py`. Story 179 uses it to prove the first narrow, highly legible handwritten-note slice on the maintained generic image-directory and PDF OCR lanes.
- `handwritten-notes-faded.txt` / `handwritten-notes-faded-images/` / `handwritten-notes-faded.pdf`: repo-owned synthetic handwritten-notes fixture generated from a checked-in transcript via `generate_handwritten_notes_fixture.py --preset faded`. Story 185 widens the maintained handwritten proof surface to a third synthetic slice with smaller, lighter, more jittered text than the current rough preset. Provenance: repo-authored transcript plus checked-in generated assets. Licensing: repo-owned. Status: `synthetic`, not evidence that real handwriting is broadly solved.
- `handwritten-notes-rough.txt` / `handwritten-notes-rough-images/` / `handwritten-notes-rough.pdf`: repo-owned synthetic handwritten-notes fixture generated from a checked-in transcript via `generate_handwritten_notes_fixture.py --preset rough`. Story 182 widens the maintained handwritten proof surface to two synthetic fixtures: one highly legible slice plus one rougher synthetic note on the same generic image-directory and PDF OCR lanes. This is still bounded synthetic evidence, not a claim about messy cursive, degraded diaries, or broader real-world handwriting.
- `handwritten-notes-barney-real.txt` / `handwritten-notes-barney-real-images/` / `handwritten-notes-barney-real.pdf`: first repo-owned real handwritten-notes fixture, derived from the Library of Congress item [Letter from Private George Washington Barney, Camp Warren, Meridian Hill, Washington, D.C., to his brother](https://www.loc.gov/pictures/item/2023637825/). The checked-in image is the `LC-DIG-ppmsca-86618` `pages 2-3` spread, the transcript file is a checked-in excerpt aligned to that visible spread and derived from the LOC transcript PDF `LC-DIG-ppmsca-86692`, and the PDF wrapper is an image-only local packaging of the same spread for maintained PDF-entry proof. Rights note from the source record: `No known restrictions on publication.` Status: `real`. Story 189 added bounded handwritten rescue recipes (`recipe-images-ocr-html-handwritten-notes-gemini-rescue.yaml` and `recipe-pdf-ocr-html-handwritten-notes-gemini-rescue.yaml`), but the fresh Story 191 maintained-baseline rerun still only reached `0.895587` on image entry and `0.756036` on PDF entry, and stronger direct-model probes in the same pass also stayed below bar. Scope note: this fixture proves only one bounded real handwritten historical-letter slice and should not be mistaken for broad support across cursive or degraded archival handwriting.
- `handwritten-notes-alverson-real.txt` / `handwritten-notes-alverson-real-images/` / `handwritten-notes-alverson-real.pdf`: second repo-owned real handwritten-notes fixture, derived from the Library of Congress item [Letter from George F. Alverson to his parents](https://www.loc.gov/pictures/item/2023637835/). The checked-in image is the front page (`LC-DIG-cwpb-08756`), and the PDF wrapper is an image-only local packaging of that same page for maintained PDF-entry proof. Rights note from the source record: `No known restrictions on publication.` Status: `real`, but currently blocked as a truth surface. Story 191 verified that the checked-in front-page image visibly ends at the same `...exceptable and` boundary where OCR stops and that the LOC source record exposes separate front/back images, so the current transcript file is not an honestly stable “front-page excerpt aligned to the visible page” claim. Until that alignment is corrected, treat this fixture as blocked evidence rather than as a clean OCR target.
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
- Synthetic handwritten-notes fixtures:
  ```bash
  python testdata/generate_handwritten_notes_fixture.py
  python testdata/generate_handwritten_notes_fixture.py --preset faded --transcript testdata/handwritten-notes-faded.txt --images-dir testdata/handwritten-notes-faded-images --pdf testdata/handwritten-notes-faded.pdf
  python testdata/generate_handwritten_notes_fixture.py --preset rough --transcript testdata/handwritten-notes-rough.txt --images-dir testdata/handwritten-notes-rough-images --pdf testdata/handwritten-notes-rough.pdf
  ```
- Real Barney handwritten wrapper regeneration from the checked-in image:
  ```bash
  img2pdf testdata/handwritten-notes-barney-real-images/page-001.jpg -o testdata/handwritten-notes-barney-real.pdf
  ```
- Real Alverson handwritten wrapper regeneration from the checked-in image:
  ```bash
  img2pdf testdata/handwritten-notes-alverson-real-images/page-001.jpg -o testdata/handwritten-notes-alverson-real.pdf
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
  The same check should print `[0, 0]` for `testdata/handwritten-notes-mini.pdf`, `[0, 0, 0]` for `testdata/handwritten-notes-rough.pdf`, and `[0]` for both real handwritten wrappers.
