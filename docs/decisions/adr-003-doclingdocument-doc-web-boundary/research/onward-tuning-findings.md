---
type: tuning-findings
topic: "doclingdocument-doc-web-boundary"
created: "2026-03-20"
story: 158
pilot-run-id: "story158-docling-tuning-r1"
---

# Onward Tuning Findings

## Status

First stock sweep complete. Thin hybrid proof complete. Arthur-lane parity
surface complete. Official VLM lane follow-up complete. Tier 1 source-image
closure pass complete. Tier 2 broader generalization pass complete. Official
plugin follow-up complete.

## Output Root

- [story158-docling-tuning-r1](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tuning-r1)
- [story158-docling-hybrid-proof-r1](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-hybrid-proof-r1)
- [story158-docling-parity-r1](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-parity-r1)
- [story158-docling-vlm-lane-r1](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-vlm-lane-r1)
- [story158-docling-parity-r3](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-parity-r3)
- [story158-docling-tier1-lane-r1](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tier1-lane-r1)
- [story158-docling-parity-r4](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-parity-r4)
- [story160-docling-baseline-arthur-r1](/Users/cam/.codex/worktrees/c09a/doc-web/output/runs/story160-docling-baseline-arthur-r1)
- [story160-docling-baseline-pierre-r1](/Users/cam/.codex/worktrees/c09a/doc-web/output/runs/story160-docling-baseline-pierre-r1)
- [story160-docling-generalization-r1](/Users/cam/.codex/worktrees/c09a/doc-web/output/runs/story160-docling-generalization-r1)
- [story160-docling-generalization-r1/arthur-parity](/Users/cam/.codex/worktrees/c09a/doc-web/output/runs/story160-docling-generalization-r1/arthur-parity)
- [story163-docling-plugin-killtest-r1](/Users/cam/.codex/worktrees/c09a/doc-web/output/runs/story163-docling-plugin-killtest-r1)
- [story163-docling-plugin-killtest-r2](/Users/cam/.codex/worktrees/c09a/doc-web/output/runs/story163-docling-plugin-killtest-r2)

## Notes

- Environment:
  - Runtime: `.venv-story157-docling-arm64`
  - `Docling`: `2.80.0`
  - `docling-parse`: `5.6.0`
  - Harness: [docling_onward_tuning_sweep.py](/Users/cam/.codex/worktrees/eb88/doc-web/scripts/spikes/docling_onward_tuning_sweep.py)
  - Hybrid proof: [docling_onward_hybrid_repair_proof.py](/Users/cam/.codex/worktrees/eb88/doc-web/scripts/spikes/docling_onward_hybrid_repair_proof.py)
  - Parity scorer: [docling_onward_parity_score.py](/Users/cam/.codex/worktrees/eb88/doc-web/scripts/spikes/docling_onward_parity_score.py)
  - Official VLM lane probe: [docling_onward_vlm_lane_probe.py](/Users/cam/.codex/worktrees/eb88/doc-web/scripts/spikes/docling_onward_vlm_lane_probe.py)
  - Tier 1 image-lane probe: [docling_onward_tier1_lane_probe.py](/Users/cam/.codex/worktrees/eb88/doc-web/scripts/spikes/docling_onward_tier1_lane_probe.py)
- Story 160 runtime refresh:
  - Runtime: `.venv-story160-docling-arm64`
  - `Docling`: `2.80.0`
  - repo-helper compatibility additions: `openai==1.52.2`, `pdf2image`,
    `pytesseract`, `httpx<0.28`
  - Generalization harness:
    [docling_onward_hybrid_generalization.py](/Users/cam/.codex/worktrees/c09a/doc-web/scripts/spikes/docling_onward_hybrid_generalization.py)
- Story 163 official plugin follow-up:
  - Runtime: `.venv-story160-docling-arm64`
  - `Docling`: `2.80.0`
  - repo-owned plugin package:
    [onward_layout_plugin.py](/Users/cam/.codex/worktrees/c09a/doc-web/docling_plugins/onward_layout_plugin.py)
    and
    [onward_table_structure_plugin.py](/Users/cam/.codex/worktrees/c09a/doc-web/docling_plugins/onward_table_structure_plugin.py)
  - harness:
    [docling_onward_plugin_kill_test.py](/Users/cam/.codex/worktrees/c09a/doc-web/scripts/spikes/docling_onward_plugin_kill_test.py)
- Session summary: [summary.json](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tuning-r1/summary.json) and [summary.md](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tuning-r1/summary.md)
- Hybrid proof summary: [summary.json](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-hybrid-proof-r1/summary.json) and [summary.md](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-hybrid-proof-r1/summary.md)
- Arthur-lane parity summary: [summary.json](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-parity-r1/summary.json) and [summary.md](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-parity-r1/summary.md)
- Official VLM lane summary: [summary.json](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-vlm-lane-r1/summary.json) and [summary.md](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-vlm-lane-r1/summary.md)
- Arthur-lane parity follow-up: [summary.json](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-parity-r3/summary.json) and [summary.md](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-parity-r3/summary.md)
- Tier 1 image-lane summary: [summary.json](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tier1-lane-r1/summary.json) and [summary.md](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tier1-lane-r1/summary.md)
- Arthur-lane parity closure: [summary.json](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-parity-r4/summary.json) and [summary.md](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-parity-r4/summary.md)

## Results

| Config | Seconds | Pages | Texts | Tables | Pictures | HTML `<img>` | HTML `id=` | MD image placeholders | Read |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `baseline-auto` | 61.829 | 40 | 312 | 20 | 7 | 0 | 0 | 7 | Matches Story 158 baseline exactly |
| `baseline-images` | 55.239 | 40 | 312 | 20 | 7 | 7 | 0 | 0 | Image export works when enabled |
| `ocrmac-fullpage` | 56.715 | 40 | 312 | 20 | 7 | 0 | 0 | 7 | No meaningful structural change from baseline |
| `tesseract-fullpage` | 82.787 | 40 | 415 | 20 | 7 | 0 | 0 | 7 | Some table-body cleanup, but still flattening and noisier runtime |
| `table-nocellmatch` | 58.923 | 40 | 312 | 20 | 7 | 0 | 0 | 7 | Regresses header/cell assignment on Onward |
| `combo-ocrmac-nocellmatch-images` | 64.713 | 40 | 312 | 20 | 7 | 7 | 0 | 0 | Export improves, structure still regresses like `table-nocellmatch` |

## Manual Inspection

### 1. Arthur opening narrative

- Baseline and `ocrmac-fullpage` remain essentially identical in the opening
  Arthur prose region.
- `tesseract-fullpage` changes tokenization and increases total text blocks, but
  this does not translate into a clean fix for the core genealogy-table onset.

Evidence:

- [baseline-images markdown](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tuning-r1/docling/baseline-images/onward-hardcase-slice-imageonly.md)
- [tesseract-fullpage markdown](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tuning-r1/docling/tesseract-fullpage/onward-hardcase-slice-imageonly.md)

### 2. First genealogy-table onset

- The central failure from Story 158 remains in every realistic stock variant:
  the first Arthur family table still begins as a long flattened prose block
  before the first proper markdown table appears.
- `ocrmac-fullpage` does not improve this region.
- `tesseract-fullpage` slightly improves some later row content, but the onset is
  still flattened and therefore still fails the Onward bar.

Evidence:

- [baseline-images markdown](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tuning-r1/docling/baseline-images/onward-hardcase-slice-imageonly.md)
- [ocrmac-fullpage markdown](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tuning-r1/docling/ocrmac-fullpage/onward-hardcase-slice-imageonly.md)
- [tesseract-fullpage markdown](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tuning-r1/docling/tesseract-fullpage/onward-hardcase-slice-imageonly.md)

### 3. Subgroup-heading leakage

- `baseline-auto`, `baseline-images`, and `ocrmac-fullpage` still leak subgroup
  headings into ordinary cells, for example `ALICE'S FAMILY Barbara Hodges`.
- `table-nocellmatch` and the combo variant make this worse by smearing headings
  across multiple columns and effectively degrading the table header.
- `tesseract-fullpage` is the only stock variant that improved some of this
  leakage, but not enough to make the table onset trustworthy.

Evidence:

- [baseline-images markdown](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tuning-r1/docling/baseline-images/onward-hardcase-slice-imageonly.md)
- [table-nocellmatch markdown](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tuning-r1/docling/table-nocellmatch/onward-hardcase-slice-imageonly.md)
- [combo markdown](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tuning-r1/docling/combo-ocrmac-nocellmatch-images/onward-hardcase-slice-imageonly.md)

### 4. Provenance continuity

- Provenance remained intact in every stock variant inspected:
  - document identity via `origin.filename`
  - block identity via `self_ref`
  - page/bbox provenance via `prov[].page_no` and `prov[].bbox`
- This confirms the remaining problem is fidelity/tunability, not traceability.

Evidence:

- [baseline-images JSON](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tuning-r1/docling/baseline-images/onward-hardcase-slice-imageonly.json)
- [tesseract-fullpage JSON](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tuning-r1/docling/tesseract-fullpage/onward-hardcase-slice-imageonly.json)

### 5. Image/export behavior

- Story 158's earlier "missing images" concern is now narrowed significantly:
  `baseline-images` and the combo variant prove that stock `Docling` can export
  picture images and emit HTML `<img>` tags when page/picture image generation is enabled.
- Generated outputs include:
  - `40` saved page images
  - `7` picture images
  - `20` table images
- The remaining export gap is not "no images"; it is packaging and citation:
  native HTML still has `0` stable `id=` anchors, and image paths are emitted as
  `_artifacts/...png` references rather than a Storybook-specific bundle layout.

Evidence:

- [baseline-images HTML](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tuning-r1/docling/baseline-images/onward-hardcase-slice-imageonly.html)
- [baseline-images images dir](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tuning-r1/docling/baseline-images/images)
- [combo HTML](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tuning-r1/docling/combo-ocrmac-nocellmatch-images/onward-hardcase-slice-imageonly.html)

### 6. Thin hybrid repair proof

- The new hybrid proof keeps `baseline-images` as the substrate and only repairs
  the two explicit hard-case pages at the Arthur onset:
  - page 3 rescues the flattened pre-table genealogy block into a real table;
  - page 4 rescues the continuation leak where subgroup labels were collapsing
    into ordinary cells such as `ALICE'S FAMILY Barbara Hodges`.
- The scripted proof succeeds on that exact slice:
  - Arthur pre-table paragraphs: `8 -> 0`
  - Arthur excerpt subgroup rows: `0 -> 46`
  - `ALICE'S FAMILY Barbara Hodges`: `True -> False`
- Manual inspection of the repaired Arthur excerpt confirms the expected local
  subgroup rows now exist in the merged chapter HTML:
  - `ARTHUR'S FAMILY`
  - `DORILLA'S FAMILY`
  - `IRENE'S FAMILY`
  - `RAYMOND'S FAMILY`
  - `THEODORE'S FAMILY`
  - `ODELIE'S FAMILY`
  - `ALICE'S FAMILY`
  - `PAUL'S FAMILY`
  - `YVETTE'S FAMILY`
  - `JOE'S FAMILY`
  - `ROBERT'S FAMILY`
- This is still a proof-of-shape, not a full Onward solution. The repaired
  chapter continues to show later repeated-structure defects outside the two-page
  Arthur slice, so the correct read is "thin hybrid repair is plausible and
  locally demonstrated", not "the whole `Docling` path is solved."

Evidence:

- [story158 hybrid summary](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-hybrid-proof-r1/summary.md)
- [Arthur before excerpt](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-hybrid-proof-r1/arthur-before.html)
- [Arthur after excerpt](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-hybrid-proof-r1/arthur-after.html)
- [Merged two-page chapter HTML](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-hybrid-proof-r1/merged-two-page.html)
- [Page 3 cleaned rescue](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-hybrid-proof-r1/page3-clean.html)
- [Page 4 cleaned rescue](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-hybrid-proof-r1/page4-clean.html)

### 7. Arthur-lane parity score surface

- The new parity scorer freezes the currently accepted Arthur hard-case lane
  against repo-owned Onward goldens instead of comparing by memory or taste.
- Current scores:
  - `baseline-images`: `16.9 / 100`
  - `hybrid-two-page`: `89.0 / 100`
- What the score now makes explicit:
  - stock `baseline-images` is nowhere near credible parity on this lane;
  - the current hybrid proof has already solved onset, header shape, leak
    hygiene, and all seven checkpoint pairs;
  - the remaining gap is now a narrower ordering/window problem, not a generic
    "Arthur table still broken" problem.
- The decisive residuals in the current hybrid lane are:
  - first divergence at subgroup position `#14`: gold expects `PAUL'S FAMILY`,
    hybrid emits `ANTHONY'S FAMILY`
  - still missing inside the first 30-subgroup window:
    `DONALD'S FAMILY`, `Joe's Grandchildren`, `MARIE'S FAMILY`
  - still extra inside that same window:
    `ANTHONY'S FAMILY`, `GARY'S FAMILY`, `RONDALD'S FAMILY`
- This is exactly the kind of delta that can now guide the next `Docling`
  experiment honestly: either an official lever can clean up subgroup ordering
  and promotion in this window, or the hybrid layer starts to grow.

Evidence:

- [Arthur-lane parity summary](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-parity-r1/summary.md)
- [Baseline Arthur lane](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-parity-r1/baseline-images-arthur-lane.html)
- [Hybrid Arthur lane](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-parity-r1/hybrid-two-page-arthur-lane.html)
- [Gold Arthur lane](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-parity-r1/gold-arthur-lane.html)

### 8. Official `Docling` VLM lane probes

- The next honest official-lever test was a bounded page-range VLM probe on the
  same Arthur lane, not a whole-document rerun.
- `smoldocling-transformers` was operationally viable and completed in `40.07s`,
  but the quality result was still effectively baseline-level:
  - rescored Arthur-lane parity: `17.9 / 100`
  - no usable subgroup-row promotion
  - broken header shape
  - family markers such as `ARTHUR'S FAMILY`, `IRENE'S FAMILY`, and
    `THEODORE'S FAMILY` still leaked into ordinary cells instead of becoming
    subgroup rows
- `granite-vision-transformers` was not operationally viable in this bounded
  local pass:
  - no `page-range` artifact emitted before termination
  - manually stopped after roughly `265.0s`
  - observed RSS reached `2378656 KB`
- The VLM follow-up therefore answered the exact next question opened by the
  parity scorer: in this environment, current official VLM presets do not close
  the remaining Arthur-lane gap and do not beat the current thin hybrid proof.

Evidence:

- [VLM lane summary](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-vlm-lane-r1/summary.md)
- [Smoldocling Arthur lane HTML](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-vlm-lane-r1/smoldocling-transformers/page-range.html)
- [Parity follow-up summary](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-parity-r3/summary.md)
- [Granite timeout meta](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-vlm-lane-r1/granite-vision-transformers/meta.json)

### 9. Tier 1 source-image closure pass

- The remaining honest Tier 1 question was whether direct source-image input
  could outperform the earlier PDF-wrapper path on the Arthur lane.
- The answer in this local install is negative:
  - `image-default` fails immediately on raw source image `Image030.jpg`
  - `image-ocrmac` fails the same way
  - both failures are operational, not just qualitative:
    `ConversionError` caused by Pillow's decompression-bomb guard on
    `302940000`-pixel source images
- The only surviving direct-image Tier 1 candidate was
  `image-smoldocling-transformers`, but it did not reopen the race:
  - runtime: `88.894s`
  - parity score: `15.0 / 100`
  - worse than the stock PDF baseline at `16.9 / 100`
  - far below the current hybrid proof at `89.0 / 100`
- Manual inspection of the merged source-image output confirms why the score is
  poor:
  - `Image030.jpg` becomes a malformed late-family table starting around
    `Yvette`, `Joe`, and `Robert`, not the expected Arthur-lane onset
  - `Image031.jpg` collapses into a long paragraph stream with no usable
    subgroup-row promotion
  - leak-like family labels still appear in ordinary cells, for example
    `YVETTE'S FAMILY`, `ROBERT'S FAMILY`, and `ANTHONY'S FAMILY`
- Optional OCR backends `rapidocr_onnxruntime` and `easyocr` are absent in the
  current `.venv-story157-docling-arm64` runtime, so they cannot be counted as
  honestly exercised Tier 1 seams in this pass.

Evidence:

- [Tier 1 image summary](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tier1-lane-r1/summary.md)

### 10. Tier 2 broader generalization pass

- Story 160 rebuilt the missing current-pass Docling substrate and then
  generalized the thin hybrid proof beyond the Arthur-local two-page slice.
  The new story-local harness starts from stock `baseline-images` artifacts,
  derives repair targets from Docling page/block signals instead of hard-coded
  page numbers or family labels, and emits inspectable repair plans plus merged
  HTML candidates under `output/runs/story160-docling-generalization-r1/`.
- The broader pass now covers two distinct Onward failure classes on current
  source artifacts:
  - Arthur onset collapse: selected pages `[3, 4]`
  - Pierre later repeated-structure spill: selected pages `[4, 5, 6]`
- Arthur result:
  - repaired excerpt moved from `3` pre-table paragraphs to `0`
  - repaired excerpt moved from `0` subgroup rows to `28`
  - frozen Arthur-lane parity moved from `22.1 / 100` on the regenerated stock
    baseline to `97.3 / 100` on the generalized full candidate
  - all seven checkpoint pairs now pass on the generalized candidate
- Manual inspection of the repaired Arthur excerpt confirms the generalized
  layer restores the expected local subgroup run in
  `output/runs/story160-docling-generalization-r1/arthur/merged-excerpt.html`,
  including:
  - `ARTHUR'S FAMILY`
  - `DORILLA'S FAMILY`
  - `IRENE'S FAMILY`
  - `RAYMOND'S FAMILY`
  - `THEODORE'S FAMILY`
  - `ODELIE'S FAMILY`
  - `ALICE'S FAMILY`
  - `PAUL'S FAMILY`
  - `YVETTE'S FAMILY`
  - `JOE'S FAMILY`
  - `ROBERT'S FAMILY`
- Arthur residuals are now narrower and explicit:
  - the generalized candidate is still not `100 / 100`
  - the remaining Arthur gap sits outside the original onset window: the first
    30-subgroup parity window is still missing `Joe's Grandchildren` and
    `MARIE'S FAMILY`
  - later Arthur pages beyond the repaired onset still leak subgroup headings
    and combined headers, so this is not yet full-Onward closure
- Pierre result:
  - baseline later region had `18` table-heading leaks, `0` subgroup rows, and
    `2` residual combined `BOY/GIRL` headers
  - repaired full candidate now has `0` heading leaks, `37` subgroup rows, and
    `0` combined `BOY/GIRL` headers
  - repaired full candidate now matches the incumbent reviewed chapter's coarse
    structure exactly on the tracked signals: `table_count 2`,
    `subgroup_row_count 37`, `external_family_heading_count 0`,
    `residual_boygirl_header_count 0`
- Manual inspection of
  `output/runs/story160-docling-generalization-r1/pierre/full-candidate.html`
  confirms the later repeated-structure region is back inside a coherent table
  and includes the expected subgroup sequence:
  - `JACQUELINE'S FAMILY (adopted by Jack Cameron)`
  - `Jacqueline's Grandchildren`
  - `DAVID'S FAMILY`
  - `JAMES' FAMILY`
  - `ANTONIO'S FAMILY`
  - plus a separate descendants summary table:
    `TOTAL DESCENDANTS 101`, `LIVING 95`, `DECEASED 6`
- Thinness read: continue Tier 2. The generalized layer is still materially
  smaller than the current Onward workaround stack because it remains
  story-local, page-scoped, and signal-driven instead of recreating the
  planner/rerun/build runtime. Current file-level mapping from the broader pass:
  - first plausible delete/replace target if this shape graduates:
    `table_rescue_onward_tables_v1`
  - likely narrowing targets, not clean deletions:
    `plan_onward_document_consistency_v1` and
    `rerun_onward_genealogy_consistency_v1`
  - likely retained shared seam for now:
    `modules/common/onward_genealogy_html.py` plus
    `build_chapter_html_v1 --merge_contiguous_genealogy_tables`
- The broader pass therefore answers the open Tier 2 question from Story 159:
  the hybrid path no longer looks Arthur-only or obviously as large as
  `doc-web`, but it still needs a maintained `driver.py` path before any
  production simplification claim is honest.

Evidence:

- [Arthur generalized summary](/Users/cam/.codex/worktrees/c09a/doc-web/output/runs/story160-docling-generalization-r1/arthur/summary.md)
- [Arthur parity summary](/Users/cam/.codex/worktrees/c09a/doc-web/output/runs/story160-docling-generalization-r1/arthur-parity/summary.md)
- [Arthur merged excerpt](/Users/cam/.codex/worktrees/c09a/doc-web/output/runs/story160-docling-generalization-r1/arthur/merged-excerpt.html)
- [Pierre generalized summary](/Users/cam/.codex/worktrees/c09a/doc-web/output/runs/story160-docling-generalization-r1/pierre/summary.md)
- [Pierre full candidate](/Users/cam/.codex/worktrees/c09a/doc-web/output/runs/story160-docling-generalization-r1/pierre/full-candidate.html)
- [Story 160 run summary](/Users/cam/.codex/worktrees/c09a/doc-web/output/runs/story160-docling-generalization-r1/summary.json)
- [Smoldocling source-image merged HTML](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tier1-lane-r1/image-smoldocling-transformers/merged.html)
- [Parity closure summary](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-parity-r4/summary.md)

## Operational Findings

- `tesseract-fullpage` completed, but emitted repeated orientation/script
  detection warnings on sparse OCR regions and took the longest runtime.
- `ocrmac-fullpage` was operationally clean but did not materially move the
  Onward failure mode.
- The later bounded official VLM follow-up produced mixed operational evidence:
  - `smoldocling-transformers` ran successfully
  - `granite-vision-transformers` failed to emit a usable artifact before
    manual termination after roughly `265.0s` and `2378656 KB` RSS
- The later Tier 1 source-image closure pass produced even stronger
  operational evidence against the remaining official-only seams in this
  runtime:
  - raw source-image `image-default` and `image-ocrmac` fail immediately on
    Pillow's decompression-bomb pixel limit
  - `image-smoldocling-transformers` runs, but at `88.894s` and with a worse
    parity result than the already-bad stock PDF baseline
- The `granite_docling` MLX path is not runnable in this local environment
  without extra dependency work; the local error was
  `ImportError: mlx-vlm is not installed. Please install it via pip install mlx-vlm`.
- The later Story 163 follow-up verified that the official plugin seam is real
  in this local install: external packages can register through the `docling`
  entrypoint group and are loaded only when `allow_external_plugins=True`.
  The seam is therefore no longer hypothetical; it is now measured and
  decision-negative on the Onward reviewed lanes.
- For the hybrid proof, `gpt-5` was not used in the final scripted path because
  the first page-3 attempt exhausted an `8000` token output budget on reasoning
  without returning HTML. `gpt-4.1` returned usable page-local HTML for both
  page 3 and page 4 with no reasoning-token overrun and is the model recorded
  in the scripted artifact summary.

### 10. Official plugin kill test

- Story 163 first tested the most plausible documented official seam that
  remained after Story 162: `table_structure_engines` via
  `allow_external_plugins=True`, then widened the same story into a coordinated
  `layout + table_structure` stack when the first pass was only partially
  helpful.
- The seam is operationally real in the local runtime:
  - the repo-owned kinds `onward_layout_v1` and
    `onward_table_structure_v1` are discoverable only with external plugins
    enabled;
  - the widened harness produces inspectable HTML/JSON/image artifacts for
    Leonidas and Marie-Louise under
    `output/runs/story163-docling-plugin-killtest-r2/`.
- The quality result is still negative as a reopen candidate:
  - Leonidas is effectively flat under `layout+table`: `7` tables,
    `55` table-heading leaks, `5` combined `BOY/GIRL` headers, and
    `0` subgroup rows;
  - Marie-Louise improves only narrowly: `layout` merges the same-page split
    from `6 -> 5` tables and restores `MARIE LOUISE'S FAMILY`, but
    `layout+table` still lands at `49` table-heading leaks, `2` combined
    headers, and `0` subgroup rows;
  - manual HTML/JSON inspection confirms the coordinated stack remains
    page-bounded (`[2]..[8]` on Leonidas, `[3]..[7]` on Marie-Louise) and far
    from the reviewed two-table gold shape.
- The widened plugin result is still weaker than the widened maintained Tier 2
  path from Story 162 on the structural signal that matters (`0` subgroup rows
  here versus `74` / `42` in the maintained lanes), so this official seam does
  not reopen the replacement race.
- The local runtime exposes no official serializer or document-level merge
  plugin seam, which means the remaining page-bounded continuation gap is not a
  sensible OCR follow-up inside the current documented plugin surface.

Evidence:

- [Leonidas coordinated plugin summary](/Users/cam/.codex/worktrees/c09a/doc-web/output/runs/story163-docling-plugin-killtest-r2/leonidas/docling/plugin-onward-layout-table-v1/summary.json)
- [Marie-Louise coordinated plugin summary](/Users/cam/.codex/worktrees/c09a/doc-web/output/runs/story163-docling-plugin-killtest-r2/marie-louise/docling/plugin-onward-layout-table-v1/summary.json)
- [Leonidas coordinated plugin HTML](/Users/cam/.codex/worktrees/c09a/doc-web/output/runs/story163-docling-plugin-killtest-r2/leonidas/docling/plugin-onward-layout-table-v1/06%20LEONIDAS%20L'HEUREUX.html)
- [Marie-Louise coordinated plugin HTML](/Users/cam/.codex/worktrees/c09a/doc-web/output/runs/story163-docling-plugin-killtest-r2/marie-louise/docling/plugin-onward-layout-table-v1/12%20MARIE-LOUISE%20(L'HEUREUX)%20LaCLARE.html)

## Ranked Recommendation

1. Keep `baseline-images` as the current best stock `Docling` substrate.
   Reason: it preserves the baseline structural quality while solving the image-export gap.
2. Treat the thin hybrid repair layer as the leading next implementation path.
   Reason: the two-page Arthur proof shows that stock `Docling` output plus
   targeted OCR rescue can eliminate the explicit onset/leakage failure class
   without rebuilding the whole pipeline.
3. Do not use `table-nocellmatch` on Onward-class documents.
   Reason: it worsens header integrity and spreads subgroup headings across columns.
4. Treat `tesseract-fullpage` as a narrow diagnostic branch, not the default answer.
   Reason: it improves some later table rows but does not fix the decisive table-onset failure and is operationally noisier.
5. Use the Arthur-lane parity score as the next control surface.
   Reason: the current spike now has a credible numeric delta (`16.9 -> 89.0`)
   and a named residual ordering/window problem instead of an abstract "still
   not good enough" read.
6. Do not treat the current official VLM presets as the leading path on this
   lane.
   Reason: `smoldocling-transformers` only reached `17.9 / 100`, and
   `granite-vision-transformers` failed operationally before producing a usable
   lane artifact.
7. Treat the currently discoverable Tier 1 seams in this local environment as
   materially exhausted on the Arthur lane.
   Reason: the direct source-image closure pass failed to reopen the race:
   `image-default` and `image-ocrmac` die on the raw Onward image scale, and
   `image-smoldocling-transformers` only reached `15.0 / 100`.
8. Do not reopen the question on the current official plugin seam.
   Reason: Story 163 proved the seam is operational even as a coordinated
   `layout + table_structure` stack, but Leonidas still lands at
   `7` tables / `55` heading leaks / `0` subgroup rows and Marie-Louise still
   lands at `5` tables / `49` heading leaks / `0` subgroup rows, which is
   weaker than the maintained Tier 2 evidence on the structural signal that
   matters and nowhere near the reviewed gold bar.
9. Use the hybrid proof as the current control path while keeping custom logic
   thin and measured.
   Reason: the best measured result is still `baseline-images` plus a
   page-scoped repair layer at `89.0 / 100`, which materially outperforms both
   stock PDF tuning and the official VLM follow-up.
10. If more official `Docling` work is justified, constrain it to materially
    different, evidence-backed seams.
    Reason: the current local install does expose a plugin registration seam,
    and Story 163 still failed to reopen the race even after widening to the
    most credible coordinated plugin stack. Further official-only effort should
    therefore target only a different documented seam with a sharper
    hypothesis, or stop and accept that the remaining gap is repo-owned repair
    work.
11. Continue Tier 2 on the broader Onward slice rather than reverting to
    Arthur-local proof or broad Tier 1 curiosity.
    Reason: Story 160 generalized the same thin shape to Arthur and Pierre from
    stock `baseline-images`, lifted Arthur to `97.3 / 100`, and restored the
    Pierre later spill to the incumbent chapter's coarse structure without
    growing a second runtime boundary.

## Bottom Line

Stock tuning moved one important gap from "hard blocker" to "configuration
issue": image export. It did **not** close the Onward fidelity gap by itself.
The new two-page hybrid proof then answered the next question: a small,
page-scoped repair layer can in fact fix the exact Arthur onset / page-4 leakage
slice on top of `baseline-images`. The new parity surface tightens that read
further: the current hybrid proof is already `89.0 / 100` on the accepted
Arthur lane, and the residual gap is now a specific subgroup-ordering window,
not a general table-collapse problem. The best evidence-backed next step is
therefore no longer "prove a hybrid path exists"; it is "use the hybrid path as
the control, and only keep probing official `Docling` levers when a concrete
discoverable seam might credibly close the remaining gap." Story 160 then
answered the next question too: the generalized signal-driven repair path stays
thin enough to continue on a broader Onward slice. Arthur now reaches
`97.3 / 100` on the frozen lane, and the same story-local harness restores the
later Pierre repeated-structure spill to the reviewed incumbent's coarse
structure. The bounded official VLM follow-up did not do that here:
`smoldocling-transformers` scored `17.9 / 100`, and
`granite-vision-transformers` did not finish cleanly enough to count as a
viable narrow-lane answer. The later direct source-image closure pass tightened
the read further rather than weakening it: `image-default` and `image-ocrmac`
fail immediately on the raw Onward image scale, and the only surviving
source-image Tier 1 candidate (`image-smoldocling-transformers`) scored
`15.0 / 100`. On the Arthur lane, the currently discoverable locally real Tier
1 seams are therefore materially exhausted unless a new documented extension
point appears. Story 163 then widened the most plausible documented extension
that remained, the external plugin seam, into a coordinated `layout + table`
stack and still found only narrow same-page cleanup instead of a real reopen.
The measured next step is therefore no longer any form of broad official-only
probing. It is to keep `doc-web` as the accepted boundary on this seam unless a
materially different documented seam appears.
