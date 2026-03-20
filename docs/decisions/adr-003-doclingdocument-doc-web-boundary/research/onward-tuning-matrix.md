---
type: tuning-matrix
topic: "doclingdocument-doc-web-boundary"
created: "2026-03-20"
story: 158
pilot-run-id: "story158-docling-tuning-r1"
---

# Onward Tuning Matrix

## Goal

Measure how far realistic stock `Docling` tuning can move the pinned Onward
hard-case slice before any custom repair layer, plugin, upstream PR, or fork is
proposed.

## Input

- Pinned hard-case slice: [onward-hardcase-slice-imageonly.pdf](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story157-docling-pilot-r1/input/onward-hardcase-slice-imageonly.pdf)
- Incumbent comparison pack: [dossier-doc-web-handoff-v1](/Users/cam/.codex/worktrees/eb88/doc-web/benchmarks/golden/onward/dossier-doc-web-handoff-v1)

## Inspection Targets

Every variant is judged against the same concrete targets:

1. Arthur opening narrative block remains coherent and provenance-linked.
2. The first genealogy-table onset does not collapse into a giant prose blob.
3. Subgroup headings do not leak into ordinary data cells unless clearly marked.
4. Document / page / block provenance remains intact.
5. Export behavior is inspectable for Storybook needs:
   - images can be preserved/exported when requested
   - block-level surface can be deterministically identified even if native HTML lacks stable ids

## Config Matrix

| Config | Purpose | Expected win | Falsifier |
|---|---|---|---|
| `baseline-auto` | Reconfirm Story 158 baseline inside the reusable harness | Stable reference point | Output diverges materially from Story 158 without an intentional config change |
| `baseline-images` | Turn on page/picture image generation and higher image scale | Confirms whether missing images were mostly a config/export issue | Still no usable image exports or referenced images in outputs |
| `ocrmac-fullpage` | Use Vision OCR with full-page OCR | Improves narrative and table text on the image-only source | Table onset and subgroup leakage remain materially unchanged |
| `tesseract-fullpage` | Use Tesseract CLI with full-page OCR | Alternative OCR stack may improve line assignment or mixed French/English text | Output gets noisier or table structure worsens |
| `table-nocellmatch` | Use structure-predicted table text instead of mapped PDF cells | Reduces merged columns or subgroup leakage | Tables lose too much text fidelity or become less coherent |
| `combo-ocrmac-nocellmatch-images` | Best realistic stock combo | If stock `Docling` has headroom, this is where it should show up | Still leaves the same core error classes as baseline |
| `vlm-granite` | Stronger VLM path | Tests whether a more capable native model closes the remaining gap | Setup/runtime cost is disproportionate or output still misses the same failure classes |

## Success Bar

- **Stock sufficient**: one variant is close enough that the remaining gap is
  superficial export/citation shaping, not document-understanding failure.
- **Hybrid required**: the best stock variant preserves provenance and improves
  quality, but a small number of explicit Onward failure classes remain.
- **Plugin / PR / fork required**: the best stock variant still fails at the
  same underlying document-understanding step, making a mere wrapper unlikely to
  reach the required Onward bar.

## Current Assumption

Story 158 currently points toward `hybrid`. This matrix exists to test whether
that recommendation survives contact with realistic stock tuning.

## First-Pass Execution Note

The first bounded stock pass executed all standard PDF-pipeline variants except
`vlm-granite`. That VLM path remains a possible follow-up, but it was deferred
after the stock sweep already showed a clear pattern:

- image/export gaps were largely configuration-level;
- the decisive remaining Onward gap stayed structural;
- the next highest-leverage step is a thin hybrid repair proof, not a broader
  random sweep.
