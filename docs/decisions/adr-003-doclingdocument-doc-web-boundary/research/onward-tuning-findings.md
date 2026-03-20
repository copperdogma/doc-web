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
closure pass complete.

## Output Root

- [story158-docling-tuning-r1](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tuning-r1)
- [story158-docling-hybrid-proof-r1](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-hybrid-proof-r1)
- [story158-docling-parity-r1](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-parity-r1)
- [story158-docling-vlm-lane-r1](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-vlm-lane-r1)
- [story158-docling-parity-r3](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-parity-r3)
- [story158-docling-tier1-lane-r1](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-tier1-lane-r1)
- [story158-docling-parity-r4](/Users/cam/.codex/worktrees/eb88/doc-web/output/runs/story158-docling-parity-r4)

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
- Local package inspection did not surface an obvious
  `allow_external_plugins`-style registration seam, so the official seams
  exercised in this pass were stock OCR/table options plus bounded page-range
  VLM presets.
- For the hybrid proof, `gpt-5` was not used in the final scripted path because
  the first page-3 attempt exhausted an `8000` token output budget on reasoning
  without returning HTML. `gpt-4.1` returned usable page-local HTML for both
  page 3 and page 4 with no reasoning-token overrun and is the model recorded
  in the scripted artifact summary.

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
8. Use the hybrid proof as the current control path while keeping custom logic
   thin and measured.
   Reason: the best measured result is still `baseline-images` plus a
   page-scoped repair layer at `89.0 / 100`, which materially outperforms both
   stock PDF tuning and the official VLM follow-up.
9. If more official `Docling` work is justified, constrain it to clearly
   discoverable, evidence-backed seams.
   Reason: the current local install did not expose an obvious plugin
   registration seam, so further effort should target specific documented hooks
   or stop and accept that the remaining gap is repo-owned repair work.

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
discoverable seam might credibly close the remaining 11-point gap." The bounded
official VLM follow-up did not do that here: `smoldocling-transformers` scored
`17.9 / 100`, and `granite-vision-transformers` did not finish cleanly enough
to count as a viable narrow-lane answer. The later direct source-image closure
pass tightened the read further rather than weakening it: `image-default` and
`image-ocrmac` fail immediately on the raw Onward image scale, and the only
surviving source-image Tier 1 candidate (`image-smoldocling-transformers`)
scored `15.0 / 100`. On the Arthur lane, the currently discoverable locally
real Tier 1 seams are therefore materially exhausted unless a new documented
extension point appears.
