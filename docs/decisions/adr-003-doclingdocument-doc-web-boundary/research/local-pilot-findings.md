---
type: local-pilot-findings
topic: "doclingdocument-doc-web-boundary"
created: "2026-03-20"
pilot-run-id: "story157-docling-pilot-r1"
---

# Local Pilot Findings

## Environment

- Isolated runtime: `.venv-story157-docling-arm64`
- `Docling`: `2.80.0`
- `docling-parse`: `5.6.0`
- Important operational note: the arm-native Python `3.14` path installed cleanly
  using the available `docling-parse` wheel, while the earlier x86_64 Python
  `3.12` attempt fell into a slow source build and is not a good default on this
  machine.

## Inputs

- Control PDF: [testdata/tbotb-mini.pdf](/Users/cam/.codex/worktrees/eb88/doc-web/testdata/tbotb-mini.pdf)
- Onward hard-case image-only slice: [onward-hardcase-slice-imageonly.pdf](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story157-docling-pilot-r1/input/onward-hardcase-slice-imageonly.pdf)
- Onward Arthur OCR-backed split PDF: `/Users/cam/Documents/Projects/Onward to the Unknown Book Scan/Split Book/05 ARTHUR L'HEUREUX.pdf`
- Corpus manifest: [source_manifest.json](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story157-docling-pilot-r1/input/source_manifest.json)
- Incumbent baseline: [dossier-doc-web-handoff-v1](/Users/cam/.codex/worktrees/eb88/doc-web/benchmarks/golden/onward/dossier-doc-web-handoff-v1)

## Control Result

- Output root: [tbotb-mini](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story157-docling-pilot-r1/docling/tbotb-mini)
- Summary: [conversion_summary.json](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story157-docling-pilot-r1/docling/tbotb-mini/conversion_summary.json)
- Native JSON: [tbotb-mini.json](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story157-docling-pilot-r1/docling/tbotb-mini/tbotb-mini.json)
- Markdown: [tbotb-mini.md](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story157-docling-pilot-r1/docling/tbotb-mini/tbotb-mini.md)

Observed:

- Conversion succeeded in `67.87s`.
- Markdown is coherent and reads cleanly.
- Native JSON preserves page-aware provenance at the text-item level through
  `prov[].page_no` and `prov[].bbox`.
- This is enough to prove the API/export harness before interpreting hard-case
  failures.

## Onward Hard-Case Slice Result

- Output root: [onward-hardcase-slice](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story157-docling-pilot-r1/docling/onward-hardcase-slice)
- Summary: [conversion_summary.json](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story157-docling-pilot-r1/docling/onward-hardcase-slice/conversion_summary.json)
- Native JSON: [onward-hardcase-slice-imageonly.json](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story157-docling-pilot-r1/docling/onward-hardcase-slice/onward-hardcase-slice-imageonly.json)
- HTML: [onward-hardcase-slice-imageonly.html](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story157-docling-pilot-r1/docling/onward-hardcase-slice/onward-hardcase-slice-imageonly.html)
- Markdown: [onward-hardcase-slice-imageonly.md](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story157-docling-pilot-r1/docling/onward-hardcase-slice/onward-hardcase-slice-imageonly.md)

Observed:

- Conversion succeeded in `68.248s`.
- Native JSON contains `40` pages, `312` text items, `20` tables, and `7`
  pictures.
- Narrative extraction is surprisingly strong in several places. Example: the
  opening Arthur paragraph in the native markdown closely matches the incumbent
  accepted paragraph from [chapter-010.html](/Users/cam/.codex/worktrees/eb88/doc-web/benchmarks/golden/onward/dossier-doc-web-handoff-v1/chapter-010.html).
- `Docling` does recover many real table objects with cell-level structure and
  page/bbox provenance. This is much better than a total collapse to plain text.
- Repeated-structure fidelity is still mixed. The Arthur section shows clear
  pre-table flattening before the first recovered table, and several subgroup
  headings leak into ordinary table cells instead of staying cleanly separated.
- Export fit is not yet Dossier-ready:
  - HTML has `0` `<img>` tags even though `7` pictures were detected.
  - HTML has `0` `id=` attributes, so there are no stable block anchors similar
    to `blk-*`.
  - Markdown contains `7` `<!-- image -->` placeholders rather than exported
    image references.
  - Picture objects in JSON contain `prov` and `captions`, but no obvious image
    payload or file reference for a Dossier consumer to use directly.

## Arthur OCR-Backed Split Result

- Output root: [onward-arthur-split-ocr](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story157-docling-pilot-r1/docling/onward-arthur-split-ocr)
- Summary: [conversion_summary.json](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story157-docling-pilot-r1/docling/onward-arthur-split-ocr/conversion_summary.json)
- Native JSON: [onward-arthur-split-ocr.json](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story157-docling-pilot-r1/docling/onward-arthur-split-ocr/onward-arthur-split-ocr.json)
- Markdown: [onward-arthur-split-ocr.md](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story157-docling-pilot-r1/docling/onward-arthur-split-ocr/onward-arthur-split-ocr.md)

Observed:

- Conversion succeeded in `18.814s`.
- Native JSON contains `10` pages, `162` text items, `5` tables, and `1`
  picture.
- The opening Arthur narrative paragraphs are readable and the Ulric paragraph is
  cleaner here than in the raw-scan slice.
- The main genealogy table onset is not better. In this OCR-backed input,
  `Docling` flattened more of the Arthur family table before the first recovered
  markdown table than it did on the raw image-only slice.
- Export-fit gaps remain the same: `0` HTML `<img>` tags, `0` HTML `id=`
  anchors, and markdown image placeholders rather than exported image assets.

## Provisional Read

- `Docling` is a credible upstream substrate candidate.
  Reason: it produces a native page-aware IR, readable narrative extraction, and
  real table objects on the raw hard-case slice without any repo-specific tuning.
- Native `DoclingDocument` plus built-in HTML/Markdown exports does not yet meet
  the current Dossier-facing `doc-web` bar.
  Reason: the built-in export surface lacks stable block anchors, bundle-local
  image exports, and clean enough repeated-structure segmentation to replace the
  accepted handoff pack directly.
- The current evidence points more strongly toward `hybrid` than immediate
  `replace`.
  Reason: the substrate is strong enough to be worth adapting or improving, but
  the native consumer surface still misses concrete contract requirements that
  `doc-web` already satisfies.
