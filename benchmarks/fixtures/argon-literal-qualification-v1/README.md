# Argon literal qualification fixtures v1

This folder contains an independently authored synthetic corpus for the proposed
Story 245 source-only table reader qualification. It has eight new pages: native
text N1–N3, image-only R1–R3, and held source-uncertainty cases A1–A2. The
material is synthetic and contains no real people, private records, copyrighted
source documents, provider answers, or downstream Ingester inputs.

The source table response golds use the maintained exact shape:

```json
{"source_table_count": 1, "tables": [{"bbox": [0, 0, 1, 1], "html": "<table>...</table>", "uncertain_cells": []}]}
```

Gold HTML encodes visible source characters and structural ownership using the
maintained `table` / `tr` / `th` / `td` markup with positive spans. N2 contains
printed `<` and `&` characters, escaped in its HTML gold. N3 includes a visible
two-column group header with two subheaders beneath each group. Empty cells and
dash characters remain separate. N3 and R3 each have two tables; every page is
at or below 40 cell slots. A1's Code cell uses an embedded Andale Mono font
variant where lowercase `l` and digit `1` map to the same glyph and advance. Its
two allowed readings are optically indistinguishable; neither is designated as
the intended literal. `proof/A1-counterfactual-proof.json` and its two PNGs show
the byte-identical counterfactual renderings. A2 marks the abraded Reading cell
uncertain with no candidate alternatives. Neither hold gold asserts hidden
author intent as visible truth, and no page contains a printed ambiguity cue.

## Regeneration

Run from the repository root with the driver's Python at
`/Users/cam/miniconda3/bin/python`. The frozen outputs here were generated and
rendered with this interpreter (Python 3.11.5, Pillow 10.4.0), ReportLab,
fontTools, pdf2image, Poppler and the project's renderer dependencies:

```sh
PYTHONPATH="$PWD" /Users/cam/miniconda3/bin/python benchmarks/fixtures/argon-literal-qualification-v1/generate_fixture.py
```

Render all sources through the maintained 300-DPI composited-PNG module:

```sh
PYTHONPATH="$PWD" /Users/cam/miniconda3/bin/python modules/extract/extract_pdf_images_capped_v1/main.py \
  --pdf benchmarks/fixtures/argon-literal-qualification-v1/source/native.pdf \
  --outdir benchmarks/fixtures/argon-literal-qualification-v1/build/render-native \
  --dpi-cap 300 --baseline-dpi 300 --min-dpi 300 --sample-count 0 \
  --image-format png --start 1 --end 3
PYTHONPATH="$PWD" /Users/cam/miniconda3/bin/python modules/extract/extract_pdf_images_capped_v1/main.py \
  --pdf benchmarks/fixtures/argon-literal-qualification-v1/source/raster.pdf \
  --outdir benchmarks/fixtures/argon-literal-qualification-v1/build/render-raster \
  --dpi-cap 300 --baseline-dpi 300 --min-dpi 300 --sample-count 0 \
  --image-format png --start 1 --end 3
PYTHONPATH="$PWD" /Users/cam/miniconda3/bin/python modules/extract/extract_pdf_images_capped_v1/main.py \
  --pdf benchmarks/fixtures/argon-literal-qualification-v1/source/holds.pdf \
  --outdir benchmarks/fixtures/argon-literal-qualification-v1/build/render-holds \
  --dpi-cap 300 --baseline-dpi 300 --min-dpi 300 --sample-count 0 \
  --image-format png --start 1 --end 2
```

Copy the numbered outputs to `renders/{N1,N2,N3,R1,R2,R3,A1,A2}.png` in page
order. After rendering, seal the inventory and corpus index with:

```sh
PYTHONPATH="$PWD" /Users/cam/miniconda3/bin/python benchmarks/fixtures/argon-literal-qualification-v1/seal_manifest.py
```

It records exact source, gold, generator, font, renderer and lossless
page-render SHA-256 values plus interpreter/dependency versions and renderer
settings, and regenerates both `manifest.json` and `corpus.json`.
The corpus index lists each case's source PDF/page, gold, render, density,
table/cell/span counts, uncertainty count and gold/render hashes.

The source geometry is US Letter at a fixed 300-DPI final render (2550 × 3300
pixels). Native pages retain searchable text as supporting provenance. Raster
and hold PDFs contain only a page image; the source-only reader receives the
composited PNG. No crop, OCR, or native text enters the gold.
