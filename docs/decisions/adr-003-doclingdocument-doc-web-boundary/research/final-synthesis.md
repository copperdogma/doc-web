---
type: synthesis-report
topic: "doclingdocument-doc-web-boundary"
synthesis-model: ""
source-reports:
  - "docs/scout/scout-011-external-document-ingestion-systems.md"
  - "local-pilot-scorecard.md"
  - "local-pilot-findings.md"
  - "onward-tuning-matrix.md"
  - "onward-tuning-findings.md"
  - "openai-research-report.md"
  - "gemini-research-report.md"
  - "opus-research-stub.md"
  - "xai-research-stub.md"
synthesized: ""
---

# Final Synthesis

## Recommended Choice

Keep `doc-web` as the accepted boundary.

Current evidence says `Docling` is strong enough to remain a serious benchmark
and research substrate, but not strong enough to replace the current `doc-web`
boundary on the reviewed Onward hard-case slice without still wanting too much
of the incumbent rescue behavior.

## Ownership Ladder

The recommended path is tiered, not flat:

1. Tier 1: official `Docling` surfaces only
   - stock configuration
   - built-in OCR / VLM / export options
   - documented plugin / serializer / extension seams
   - ideal because it keeps future `Docling` upgrades cheap: pull a new
     version, rerun a narrow smoke/parity lane, and promote if it still passes
2. Tier 2: upstream-compatible deeper ownership
   - thin repo-owned repair or adaptation layer
   - upstream PRs
   - replayable local patches that do not require a permanent fork
   - only justified when Tier 1 is falsified with measured quality or
     operational evidence
3. Tier 3: source-divergent ownership
   - maintained fork
   - invasive long-lived patch stack
   - only justified when lower tiers cannot honestly reach the bar

## Why

- The local pilot shows real value on hard documents without repo-specific
  tuning: the image-only Onward slice produced readable narrative extraction, a
  page-aware native IR, `20` recovered tables, and `7` detected pictures.
- Story 159's stock-tuning sweep narrows one earlier concern: image export is
  largely a configuration issue. When page/picture image generation is enabled,
  `Docling` emits HTML `<img>` tags and saves page, picture, and table images.
- Story 159's thin hybrid proof is the first direct evidence that the remaining
  Onward gap is repairable without recreating the whole runtime. On top of the
  `baseline-images` substrate, a two-page OCR rescue removed the flattened
  Arthur pre-table onset and the page-4 `ALICE'S FAMILY Barbara Hodges` leak
  while preserving the surrounding genealogy-table run.
- Story 160's broader Tier 2 pass strengthens that result beyond the Arthur
  two-page proof. A new signal-driven harness under
  `scripts/spikes/docling_onward_hybrid_generalization.py` now derives repair
  targets from stock `Docling` page/block signals, lifts the Arthur full
  candidate to `97.3 / 100`, and restores the later Pierre spill to the
  incumbent chapter's coarse structure without reintroducing heading leaks.
- Story 162 closes the remaining question by widening the maintained path across
  the full reviewed Story 149 slice in
  `output/runs/story162-docling-maintained-r1/`.
  The result is mixed, not adoption-grade:
  - Arthur remains strong.
  - Pierre reaches the reviewed target shape.
  - Antoine is close, but still keeps the descendants summary inside the main
    genealogy table instead of matching the reviewed two-table shape.
  - Leonidas and Marie-Louise both improve materially, but still remain
    structurally short of the reviewed target shape.
    Leonidas finishes with `12` tables and `coarse_suspect=true`;
    Marie-Louise finishes with `4` tables, `17` residual heading leaks, and
    retained pre-genealogy name-list artifacts before the repaired block.
- Story 163 then widened the documented external plugin seam into a coordinated
  official plugin stack under `output/runs/story163-docling-plugin-killtest-r2/`.
  The result is still negative:
  - the repo-owned `layout` and `table-structure` plugins both register cleanly
    through `allow_external_plugins=True` with no `Docling` source edits;
  - Leonidas still finishes at `7` tables with `55` heading leaks and
    `0` subgroup rows;
  - Marie-Louise improves only from `6 -> 5` tables, but still finishes with
    `49` heading leaks and `0` subgroup rows;
  - the only material gain beyond the earlier table-only pass is one same-page
    merge on Marie-Louise plus cleaner header/label cleanup, which is not
    enough to threaten the accepted boundary or even beat the widened
    maintained Tier 2 path on the structural signal that matters.
- The one clearly honest shared extraction that survived Story 162 is the
  OpenAI vision OCR request path in `modules/common/onward_openai_ocr.py`.
  The remaining normalization gap still points back toward broader incumbent
  rescue behavior rather than a clearly smaller adopted wrapper.
- The same pilot and tuning sweep still show concrete native-surface gaps against the accepted
  `doc-web` bar:
  - no stable block anchors in HTML;
  - image export exists, but not yet in a Storybook-specific citation/bundle layout;
  - repeated-structure subgroup headings leaking into table cells.
- The OCR-backed Arthur follow-up and later stock-tuning sweep did not rescue
  the main genealogy-table onset, which weakens the claim that trivial OCR or
  table-option changes alone make native `DoclingDocument` immediately
  Dossier-ready.

## Runner-Up

Pursue `hybrid` first.

That was the right intermediate move through Stories 158–161, and it produced
useful evidence. Story 162 is what closes it off: the widened maintained proof
does not stay thin enough while also clearing the reviewed slice.

## Avoid

Do not recommend native `DoclingDocument` replacement today.

The current pilot does not justify superseding ADR-002 because the built-in
consumer surface still misses contract features Dossier already relies on.

## Next Step

Close the active `Docling` replacement track on this seam.

- Keep `doc-web` as the accepted boundary direction.
- Treat the maintained `Docling` recipe/module path as benchmark/reference
  evidence only.
- Do not continue slicing follow-up adoption stories from this proof chain.
- Only reopen the question if a materially different documented official seam
  or demonstrably thinner hybrid path appears that can clear Leonidas and
  Marie-Louise without regrowing the incumbent rescue ownership. Story 163 has
  now falsified the currently most plausible coordinated documented external
  plugin seam on this lane.
