# Test Data Fixtures

- `tbotb-mini.md` / `tbotb-mini.pdf`: 8-section micro branch adapted from **To Be or Not To Be** by Ryan North (2013). Licensed **CC BY-NC 3.0**; used here for non-commercial smoke testing. Source PDF: `input/Ryan North - To Be or Not To Be.pdf` (not modified).
- Story 157 uses `tbotb-mini.pdf` as the repo-owned maintained PDF-entry smoke fixture. Stories 168 and 196 also use it as one bounded book-like `born-digital-pdf` proof item inside the passing Story 196 supported slice; it is still not blanket evidence that all native `born-digital-pdf` inputs are solved.
- `born-digital-handbook-mini.md` / `born-digital-handbook-mini.pdf`: repo-owned reproducible book-like born-digital handbook fixture generated from checked-in markdown via `generate_book_like_born_digital_fixture.py`. Story 196 uses it to widen the maintained book-like proof surface beyond `tbotb-mini` with an explicit TOC page plus four page-linked chapter pages.
- `flat-born-digital-mini.md` / `flat-born-digital-mini.pdf`: repo-owned flat born-digital prose packet with no TOC and no printed page numbers. Story 171 uses it to prove the maintained non-TOC born-digital PDF lane can emit a final `doc-web` bundle without relying only on local user assets.
- `flat-born-digital-form-mini.md` / `flat-born-digital-form-mini.pdf`: repo-owned flat born-digital form-like packet with short label-style sections and an all-caps warning block. Story 177 uses it to widen the repeatable proof surface beyond the original prose-only mini fixture and to measure whether oversized in-body headings are a generic rough edge on the maintained non-TOC lane.
- `scanned-prose-mini.md` / `scanned-prose-mini.pdf`: original repo-owned prose source plus a generated image-only PDF fixture for `scanned-pdf-prose`. Story 167 uses it to prove maintained scanned-PDF entry, `page_image_v1` provenance, and a clean simple-prose OCR lane without relying on a shared local asset. This is passing evidence for the repo-owned simple-prose fixture, not a blanket claim about degraded or noisy scanned prose.
- `handwritten-notes-mini.txt` / `handwritten-notes-mini-images/` / `handwritten-notes-mini.pdf`: repo-owned synthetic handwritten-notes fixture generated from a checked-in transcript via `generate_handwritten_notes_fixture.py`. Story 179 uses it to prove the first narrow, highly legible handwritten-note slice on the maintained generic image-directory and PDF OCR lanes.
- `handwritten-notes-faded.txt` / `handwritten-notes-faded-images/` / `handwritten-notes-faded.pdf`: repo-owned synthetic handwritten-notes fixture generated from a checked-in transcript via `generate_handwritten_notes_fixture.py --preset faded`. Story 185 widens the maintained handwritten proof surface to a third synthetic slice with smaller, lighter, more jittered text than the current rough preset. Provenance: repo-authored transcript plus checked-in generated assets. Licensing: repo-owned. Status: `synthetic`, not evidence that real handwriting is broadly solved.
- `handwritten-notes-rough.txt` / `handwritten-notes-rough-images/` / `handwritten-notes-rough.pdf`: repo-owned synthetic handwritten-notes fixture generated from a checked-in transcript via `generate_handwritten_notes_fixture.py --preset rough`. Story 182 widens the maintained handwritten proof surface to two synthetic fixtures: one highly legible slice plus one rougher synthetic note on the same generic image-directory and PDF OCR lanes. This is still bounded synthetic evidence, not a claim about messy cursive, degraded diaries, or broader real-world handwriting.
- `handwritten-notes-barney-real.txt` / `handwritten-notes-barney-real-images/` / `handwritten-notes-barney-real.pdf`: first repo-owned real handwritten-notes fixture, derived from the Library of Congress item [Letter from Private George Washington Barney, Camp Warren, Meridian Hill, Washington, D.C., to his brother](https://www.loc.gov/pictures/item/2023637825/). The checked-in image is the `LC-DIG-ppmsca-86618` `pages 2-3` spread, the transcript file is a checked-in excerpt aligned to that visible spread and derived from the LOC transcript PDF `LC-DIG-ppmsca-86692`, and the PDF wrapper is an image-only local packaging of the same spread for maintained PDF-entry proof. Rights note from the source record: `No known restrictions on publication.` Status: `real`. Story 189 added bounded handwritten rescue recipes (`recipe-images-ocr-html-handwritten-notes-gemini-rescue.yaml` and `recipe-pdf-ocr-html-handwritten-notes-gemini-rescue.yaml`), but the fresh Story 191 maintained-baseline rerun still only reached `0.895587` on image entry and `0.756036` on PDF entry, and stronger direct-model probes in the same pass also stayed below bar. Scope note: this fixture proves only one bounded real handwritten historical-letter slice and should not be mistaken for broad support across cursive or degraded archival handwriting.
- `handwritten-notes-alverson-real.txt` / `handwritten-notes-alverson-real-images/` / `handwritten-notes-alverson-real.pdf`: second repo-owned real handwritten-notes fixture, derived from the Library of Congress item [Letter from George F. Alverson to his parents](https://www.loc.gov/pictures/item/2023637835/). The checked-in image is the LOC front page (`LC-DIG-ppmsca-86651`; the same item also exposes a separate back page as `LC-DIG-ppmsca-86652`), and the PDF wrapper is an image-only local packaging of that same front page for maintained PDF-entry proof. Rights note from the source record: `No known restrictions on publication.` Status: `real`, front-page only. Story 192 trimmed the checked-in transcript to the exact visible front-page scope after re-verifying that the local image ends at the same `...exceptable and` boundary shown on the source page, so this fixture is now an honest one-page OCR target. It is not evidence that the repo owns or scores the full two-page letter; a future story would need to add the back page explicitly if that broader scope becomes necessary.
- `docx-mini.source.json` / `docx-mini.docx`, `docx-sections-mini.source.json` / `docx-sections-mini.docx`, and `docx-nested-mini.source.json` / `docx-nested-mini.docx`: repo-owned DOCX fixture set generated from checked-in structured source data. Story 175 widens the maintained DOCX lane to three repo-owned fixtures on the supported slice: heading-based sections, prose, nested subheadings, simple bullet lists, and a simple table. Provenance remains block-anchor based rather than page-based because DOCX is pageless in this lane.
- `xlsx-mini.source.json` / `xlsx-mini.xlsx`, `xlsx-multi-sheet.source.json` / `xlsx-multi-sheet.xlsx`, and `xlsx-two-tables.source.json` / `xlsx-two-tables.xlsx`: repo-owned XLSX fixture set generated from checked-in structured source data. Story 193 widened the maintained XLSX proof surface to three supported fixtures on one coherent slice: simple table-only sheets, one HTML entry per supported sheet/entry, multiple sheets, and multiple table regions on one sheet. Provenance remains anchor-based via `source_element_ids`; this lane still does not claim fabricated page numbers or cell-address precision.
- `xlsx-merged-formula.source.json` / `xlsx-merged-formula.xlsx`: repo-owned XLSX boundary probe generated from checked-in structured source data. Story 193 keeps it explicitly `bounded unsupported`: the fresh recheck showed Unstructured emitting `Budget Notes` and `Total` as heading blocks around the main table instead of preserving the merged-title / formula-summary structure inside the table.
- `pptx-mini.md` / `pptx-mini.pptx`: reproducible PPTX seam-probe fixture generated from checked-in markdown via `pandoc`. Story 193 rechecked the current checkout and kept PPTX explicitly blocked: `python - <<'PY' ... from unstructured.partition.pptx import partition_pptx ... PY` still fails with `ModuleNotFoundError: No module named 'pptx'`, so there is still no maintained PPTX recipe or provenance mapping here yet.

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
- Book-like born-digital handbook PDF:
  ```bash
  python testdata/generate_book_like_born_digital_fixture.py
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
- XLSX fixtures:
  ```bash
  python testdata/generate_xlsx_fixture.py
  python testdata/generate_xlsx_fixture.py --source testdata/xlsx-multi-sheet.source.json --output testdata/xlsx-multi-sheet.xlsx
  python testdata/generate_xlsx_fixture.py --source testdata/xlsx-two-tables.source.json --output testdata/xlsx-two-tables.xlsx
  python testdata/generate_xlsx_fixture.py --source testdata/xlsx-merged-formula.source.json --output testdata/xlsx-merged-formula.xlsx
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
