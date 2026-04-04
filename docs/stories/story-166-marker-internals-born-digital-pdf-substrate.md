---
title: Use Marker Internals as a Thin Born-Digital PDF Substrate
status: Done
priority: High
ideal_refs:
- 'Requirement #1 (Ingest), Requirement #3 (Extract), Requirement #5 (Structure),
  Requirement #6 (Validate), Any format, any condition, Traceability is the Product'
spec_refs:
- spec:1
- spec:1.1
- spec:3
- spec:3.1
- spec:6
- spec:7
adr_refs: []
depends_on:
- '157'
- '165'
category_refs:
- spec:1
- spec:3
- spec:6
- spec:7
compromise_refs:
- C2
- C3
input_coverage_refs:
- born-digital-pdf
architecture_domains: []
roadmap_tags: []
legacy_system: ''
---

# Story 166 — Use Marker Internals as a Thin Born-Digital PDF Substrate

**Priority**: High
**Status**: Done
**Ideal Refs**: Requirement #1 (Ingest), Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Any format, any condition, Traceability is the Product
**Spec Refs**: spec:1 (spec:1.1, C2), spec:3 (spec:3.1, C3), spec:6, spec:7
**Build Map Refs**: Category 1 Intake & Format Routing (`partial`, C2 `climb`); Category 3 Layout & Structure Understanding (`exists`, C3 `climb`); Category 7 Graduation & Dossier Handoff (`partial`); Input Coverage row `born-digital-pdf` remains high-priority untested
**Decision Refs**: `docs/scout/scout-011-external-document-ingestion-systems.md`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/stories/story-157-pdf-intake-parity-with-image-directory-inputs.md`, `docs/stories/story-165-marker-breadth-comparator-born-digital-pdf.md`, `docs/build-map.md`
**Depends On**: Story 157, Story 165

## Goal

Story 165 answered the broad comparator question: stock `Marker` is too heavy
and awkward to adopt as a product-level converter here, but the thinner
Marker-internals path preserved born-digital PDF structure more usefully than
the current local OCR-routed baseline on `testdata/tbotb-mini.pdf`. This story
should determine whether that thinner internal seam can become a real upstream
substrate for `born-digital-pdf` intake inside `doc-web`, without adopting the
stock Marker CLI and without violating the repo's traceability-first runtime
boundary. The output should answer one question: can selected Marker internals
feed a thin, inspectable born-digital path that reduces pressure on Story 157's
PDF intake gap while keeping `doc-web` as the canonical boundary?

## Acceptance Criteria

- [x] The exact seam is frozen before any maintained integration claim:
  - stock `Marker` CLI remains explicitly out of scope for adoption
  - the specific Marker internal classes/processors to reuse are named
  - code-license and model-license posture are summarized against the proposed ownership boundary
- [x] A thin prototype exists on the active `born-digital-pdf` seam:
  - uses the repo-owned `tbotb-mini.pdf` fixture first
  - is reproducible from this checkout without depending on a long-lived Docker container bound to a different worktree
  - writes inspectable artifacts under `output/runs/`
  - proves whether Marker internals can be normalized into an existing `doc-web`-useful artifact surface instead of remaining a standalone export
- [x] The prototype is compared honestly against the current local baseline:
  - compare against the current OCR-routed/pagelines baseline from Story 165
  - explicitly record what gets better, what provenance gets worse, and what remains missing
  - do not count cosmetic markdown improvements as a win if the normalized artifact surface is still unusable downstream
- [x] The story ends with a single boundary decision:
  - if the thin seam wins cleanly, name the exact maintained integration story or ADR follow-up
  - if it does not, park Marker as a parts-bin reference and stop

## Out of Scope

- Adopting stock `Marker` CLI into the maintained runtime
- Claiming `born-digital-pdf` is shipped or passing before a real maintained path exists
- Reopening the closed Onward `Docling` or `Surya` seams
- Claiming multi-format `Marker` breadth beyond the explicitly tested PDF lane
- Quietly accepting GPL or model-license constraints into the maintained boundary without an explicit decision

## Approach Evaluation

- **Simplification baseline**: the current local baseline already exists and is cheap enough to measure: Story 165's `story165-docweb-baseline-r1` still OCR-routes a born-digital PDF even when `pdftext` covers every page. This story is only worth building if the thin Marker seam beats that baseline on structure quality, not just presentation.
- **AI-only**: not sufficient. A one-shot LLM rewrite of PDF text would not answer the ownership/runtime/provenance question and would bypass the very substrate this story is evaluating.
- **Hybrid**: the leading candidate. Reuse the proven Marker internals seam from Story 165, then normalize it into an existing `doc-web`-useful artifact surface while keeping `doc-web` in control of downstream ownership and provenance reporting.
- **Pure code**: viable fallback only if Story 165's Marker result turns out to be mostly reproducible with lighter local embedded-text plus deterministic structuring. Do not assume that without measurement.
- **Repo constraints / prior decisions**: ADR-002 keeps `doc-web` as the runtime boundary. Story 157 keeps scanned-PDF parity separate from born-digital PDF. Story 165 already said "no" to stock Marker adoption and "maybe" to a thin internal substrate. Scout 011 now tracks Marker as a scoped follow-on candidate, not a broad product adoption path.
- **Existing patterns to reuse**: `scripts/spikes/marker_breadth_benchmark.py`, Story 165 benchmark artifacts, Story 157's PDF-intake framing, `tests/fixtures/doc_web_bundle_smoke/`, the `doc_web` bundle contract, and the lessons from the closed `Docling` chain about keeping external tools outside the accepted runtime boundary until they earn it.
- **Eval**: the deciding proof is a normalized born-digital substrate comparison:
  - can the thin Marker seam preserve embedded-text structure better than the current OCR-routed baseline?
  - can it emit an artifact shape that is actually useful to `doc-web` or Dossier-facing export work?
  - are the license/runtime/provenance costs still acceptable after inspection?
  If the answer is only "Marker markdown looks nicer," the story should stop.

## Tasks

- [x] Re-prove the exact reusable seam before any integration claim:
  - record the specific internal Marker classes/processors that Story 165 proved locally
  - repair or replace the stale named-container bootstrap so the seam can run honestly from this checkout
  - record the license/runtime constraints that still block stock CLI adoption
  - stop and record the blocker if the thin internal seam still cannot be reproduced cleanly outside the Story 165 spike harness
- [x] Freeze the prototype surface before coding:
  - mandatory first lane is `testdata/tbotb-mini.pdf`
  - define the exact normalized artifact target (`page_html_v1`, bundle-adjacent HTML, or another existing surface)
  - define the stop rule if provenance loss or licensing awkwardness makes the seam not worth integrating
- [x] Implement the smallest honest prototype:
  - keep it isolated to a story-local spike or clearly optional adapter seam
  - do not wire stock Marker CLI into recipes or operator workflows
  - prefer proving the normalization path before touching maintained runtime surfaces
- [x] Compare the prototype against the current local baseline(s) and manually inspect representative outputs
- [x] If this story changes documented format coverage or graduation reality: update `docs/build-map.md` and record the before/after state honestly
- [x] Check whether the chosen implementation makes any existing code, helper paths, or docs redundant; remove them or create a concrete follow-up
- [x] Run required checks for touched scope:
  - [x] Default Python checks: `make test`
  - [x] Default Python lint: `make lint`
  - [x] If pipeline behavior changed: clear stale `*.pyc`, run through `driver.py` or `make smoke`, verify artifacts in `output/runs/`, and manually inspect sample JSON/JSONL data
  - [x] If agent tooling changed: not applicable in this story; no agent tooling changed
- [x] If evals or goldens changed: not applicable in this story; no evals or goldens changed
- [x] Search all docs and update any related to what we touched
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: every output traces to source page, OCR engine, confidence, processing step
  - [x] T1 — AI-First: didn't write code for a problem AI solves better
  - [x] T2 — Eval Before Build: measured SOTA before building complex logic
  - [x] T3 — Fidelity: source content preserved faithfully, no silent losses
  - [x] T4 — Modular: new recipe not new code; no hardcoded book assumptions
  - [x] T5 — Inspect Artifacts: visually verified outputs, not just checked logs

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Architectural Fit

- **Owning module / area**: born-digital intake/adaptation and external benchmark transfer. The likely owners are a story-local spike or optional adapter seam plus the tracker docs; the maintained runtime should stay untouched until the thin seam actually wins.
- **Build-map reality**: Category 1 is still `partial` / `climb`, Category 3 still owns structure extraction, and `born-digital-pdf` remains unshipped. This story exists because Story 165 produced enough evidence to justify a narrower substrate experiment without claiming coverage.
- **Substrate evidence**: this checkout freshly verifies the maintained `doc-web` side of the substrate in `tests/test_pdf_intake_recipe.py`, `tests/test_doc_web_bundle_contract.py`, `tests/test_doc_web_cli_contract.py`, `doc_web/runtime_contract.py`, and `schemas.py`. The Marker side is now real but still story-local: `scripts/spikes/marker_breadth_benchmark.py` can rebuild the target runtime from the cached local image `doc-web/story165-marker-cpu:9f4f` with repo-local `/work`, pip, and model-cache mounts, and `scripts/spikes/marker_page_html_prototype.py` now emits both `page_html_v1` and contract-aligned `doc_web` bundle/provenance proof under `output/runs/story166-marker-page-html-r2/`. The maintained runtime path remains intentionally untouched.
- **Frozen reusable seam**: the exact thin seam is the story-local `LiteBornDigitalConverter` in `scripts/spikes/marker_breadth_benchmark.py`: `provider_from_filepath()` -> `LayoutBuilder` -> `LineBuilder` -> `DocumentBuilder(disable_ocr=True)` -> `StructureBuilder` -> `OrderProcessor`, `BlockRelabelProcessor`, `LineMergeProcessor`, `BlockquoteProcessor`, `DocumentTOCProcessor`, `IgnoreTextProcessor`, `LineNumbersProcessor`, `ListProcessor`, `PageHeaderProcessor`, `SectionHeaderProcessor`, `TextProcessor`, `ReferenceProcessor`, and `BlankPageProcessor` -> `HTMLRenderer` / `JSONRenderer` / `MarkdownRenderer`. Stock Marker CLI remains explicitly out of scope.
- **Ownership / license posture**: the maintained ownership boundary is still `doc-web`; Marker and Surya stay outside it in this story. The current optional runtime still carries `marker-pdf` and `surya-ocr` under `GPL-3.0-or-later`, a restricted commercial model-license posture, and multi-gigabyte model loads. That is acceptable for a bounded spike proving a seam, but not yet for direct maintained runtime adoption.
- **Data contracts / schemas**: expected to reuse existing artifact contracts if possible. If the prototype needs new cross-artifact fields, they must be added to `schemas.py` before code emits them.
- **File sizes**: `scripts/spikes/marker_breadth_benchmark.py` is already a live story-local harness and should stay the main reuse point. `docs/build-map.md` is large, so only touch it if this story materially changes coverage or next-step reality. Any new adapter code should stay small and bounded until the seam is proven.
- **Decision context**: reviewed `docs/ideal.md`, `docs/build-map.md`, Scout 011, ADR-002, Story 157, and Story 165. No new ADR is required at creation time because this is still a bounded spike, not an accepted runtime-boundary change.

## Files to Modify

- `docs/stories/story-166-marker-internals-born-digital-pdf-substrate.md` — this story file and work log (new file)
- `docs/stories.md` — story index row for Story 166
- `scripts/spikes/marker_breadth_benchmark.py` — likely reuse or extension point for the thin-seam prototype
- `scripts/spikes/marker_page_html_prototype.py` — story-local normalizer from Marker JSON into `page_html_v1` plus minimal `doc_web` bundle/provenance proof
- `tests/test_marker_page_html_prototype.py` — focused regression for the thin `page_html_v1` prototype
- `docs/scout/scout-011-external-document-ingestion-systems.md` — update only if the result changes Marker's tracked standing again
- `docs/build-map.md` — update only if the story materially changes born-digital next-step reality
- optional new spike or adapter file under `scripts/spikes/` or `modules/` — only if the prototype surface is actually proven

## Redundancy / Removal Targets

- the idea that `Marker` must be treated only as a full-converter product rather than a parts-bin source
- any temporary story-local normalization glue if the thin seam proves out and moves into a cleaner maintained surface
- any premature stock-CLI adoption notes that survive after the thin-seam result is known

## Notes

- Story 165 already answered the first useful question. This story exists only because the answer was mixed, not cleanly negative.
- The most important open question is boundary honesty: can we steal the useful structure-preserving part of Marker without taking on an ugly runtime/license/provenance burden?
- If the answer is "only by effectively embedding Marker as a hidden second runtime," the story should stop.

## Plan

1. Re-establish a reproducible Marker-internals entry point (`S`)
   - Files: `scripts/spikes/marker_breadth_benchmark.py`, optional new helper under `scripts/spikes/`, and this story file/work log.
   - Change: remove the implicit dependency on the stale `story165-marker-cpu` container that is bound to another worktree, or replace it with a repo-local bootstrap that can run from this checkout. Keep stock Marker CLI out of recipes and maintained operator flows.
   - Impact / risk: this is the main substrate risk. If the seam cannot run without hidden environment coupling, the story should stop with a negative boundary decision instead of forcing an integration.
   - Done when: the exact Marker internal classes/processors are named in story evidence and the spike entry point can execute or fail with an honest, repo-local reason from this checkout.

2. Freeze the normalized target surface before code spreads (`XS`)
   - Files: this story file first; `schemas.py` only if the prototype proves an existing contract is almost sufficient and needs a tiny explicit extension.
   - Change: choose the smallest existing `doc-web`-useful target, with `page_html_v1` as the default first choice and bundle-adjacent HTML as the fallback only if page-level HTML cannot preserve the needed structure/provenance. Keep the maintained `doc_web` runtime boundary from ADR-002 intact.
   - Impact / risk: choosing the wrong target would produce a prettier export that is still unusable downstream. Any schema-boundary expansion beyond existing contracts is a human-approval checkpoint before maintained integration claims.
   - Done when: the target artifact shape, required provenance fields, and stop rule are explicit in the story and implementation notes.

3. Build the smallest honest prototype on `tbotb-mini.pdf` (`M`)
   - Files: likely `scripts/spikes/marker_breadth_benchmark.py` plus one bounded spike/adapter file under `scripts/spikes/`; optional touch to `schemas.py` only if step 2 proved necessary.
   - Change: run the Marker-internals seam on `testdata/tbotb-mini.pdf`, normalize the result into the chosen target surface, and write inspectable artifacts under `output/runs/story166-*`. Do not wire this into maintained recipes yet.
   - Impact / risk: the main failure mode is provenance loss or unstable anchors. If Marker output cannot map cleanly enough into inspectable source-page ownership, the prototype should be treated as a dead end even if the HTML looks better.
   - Done when: the prototype produces artifacts in `output/runs/` that can be manually inspected against the baseline and the chosen surface is actually consumable by existing `doc-web` expectations.

4. Compare against the current baseline and record the boundary decision (`S`)
   - Files: this story file; `docs/build-map.md` and `docs/scout/scout-011-external-document-ingestion-systems.md` only if the result changes tracked reality.
   - Baseline / eval: fresh current-pass baseline is `python -m pytest tests/test_pdf_intake_recipe.py -q` (`2 passed`) plus `python -m pytest tests/test_doc_web_bundle_contract.py tests/test_doc_web_cli_contract.py -q` (`16 passed`). The Marker benchmark baseline is currently blocked in this checkout by the stale container mount and must be repaired as part of step 1 before any comparison claim is honest.
   - Candidate approaches considered: AI-only is rejected because it dodges the substrate question; hybrid Marker-internals plus thin normalization is the leading path; pure-code fallback remains the existing `extract_pdf_text()` seam and should only win if it can match the structure gain without Marker.
   - Impact / risk: if the prototype wins only on markdown cosmetics, nothing should move into the maintained runtime. If it wins cleanly on structure with acceptable provenance/licensing cost, the output should name the exact follow-up integration story or ADR.
   - Done when: the story records what improved, what got worse, what remained missing, and whether Marker graduates to a maintained follow-up or is parked as a parts-bin reference.

Structural health notes:
- Relevant build-map context remains Category 1 `partial` / C2 `climb`, Category 3 `exists` / C3 `climb`, and Input Coverage still shows `born-digital-pdf` as a real gap despite the maintained PDF-entry smoke lane.
- Existing patterns to reuse are the Story 165 benchmark harness, the maintained PDF intake smoke test, and the frozen `doc_web` bundle/provenance contracts. Avoid introducing a second hidden runtime or broad recipe branching.
- Recommended scope adjustment discovered during exploration: absorb the reproducibility/bootstrap repair into Story 166. It is a small tightly coupled prerequisite, not a separate story.
- Human approval blockers: any new external runtime dependency beyond the current optional spike setup, any non-trivial schema-boundary change, or any plan that would push stock Marker CLI into maintained recipes/operators.

## Work Log

20260326-1241 — story created: Story 165 closed the broad comparator question
enough to justify a narrower follow-on around Marker internals, not stock
Marker adoption. Evidence: `output/runs/story165-marker-benchmark-r1/tbotb-mini/marker-v1102/summary.json`
shows `1.0` heading coverage and `1.0` token coverage for the `lite_api` path,
while `output/runs/story165-docweb-baseline-r1/ocr_ensemble/ocr_source_histogram.json`
still routes all pages through `tesseract` despite full `pdftext` coverage.
Next step: `/build-story` should verify the exact reusable seam and freeze the
normalized artifact target before promoting this story out of `Draft`.

20260327-1026 — promoted to Pending: user approved moving Story 166 out of the
draft gate so `/build-story` can run. The story remains a bounded spike, not an
implementation commitment. Next step: verify the cited Marker seam and local
baseline in this checkout, then either write the implementation plan or record
the blocker if the substrate is not reproducible enough to build honestly.

20260327-1121 — explored substrate and wrote implementation plan: reviewed
`docs/ideal.md`, the cited `spec` sections, the `born-digital-pdf` build-map
rows, Scout 011, ADR-002, Story 157, and Story 165. Fresh baseline checks pass
in this checkout: `python -m pytest tests/test_pdf_intake_recipe.py -q`
(`2 passed`) and `python -m pytest tests/test_doc_web_bundle_contract.py
tests/test_doc_web_cli_contract.py -q` (`16 passed`). Verified maintained
`doc-web` substrate in `doc_web/runtime_contract.py`, `schemas.py`, and the
contract/smoke tests. Surprise: the `story165-marker-cpu` container is mounted
to `/Users/cam/.codex/worktrees/c09a/doc-web`, so the Marker `lite_api` seam is
not honestly reproducible from this checkout until that bootstrap is repaired
or replaced; the cited `story165-*` run artifacts are also absent under
`output/runs/` here. Small scope delta absorbed: Story 166 now includes the
repo-local reproducibility slice as a prerequisite to the thin normalization
prototype. Next step: wait for user approval on the written plan, then move the
story to `In Progress` and implement the reproducibility fix plus prototype.

20260327-1133 — implementation started: moved Story 166 to `In Progress` after
user approval and began on the reproducibility/bootstrap slice first. Next
step: patch the Marker benchmark harness so it can run honestly from this
worktree instead of depending on the stale `story165-marker-cpu` container
mount.

20260327-1219 — repaired the reproducibility seam and proved the Marker
runtime locally: `scripts/spikes/marker_breadth_benchmark.py` now defaults to a
repo-local worktree container (`story165-marker-cpu-9f4f`) and can rebuild it
from the stale provisioned seed container when needed. Fresh run:
`python scripts/spikes/marker_breadth_benchmark.py --mode lite_api --formats json --out-root output/runs/story166-marker-probe-r1`
completed successfully and wrote
`output/runs/story166-marker-probe-r1/tbotb-mini/marker-v1102/summary.json`.
Evidence: the bootstrap metadata in that summary shows `action =
"rebuilt_from_seed_container"` with `/Users/cam/.codex/worktrees/9f4f/doc-web`
mounted at `/work`, and the Marker decision read stays
`candidate_for_follow_on_story` with `1.0` heading and token coverage on the
fixture. Next step: normalize the proven Marker JSON seam into an existing
`doc-web` artifact surface and compare it against a fresh maintained baseline.

20260327-1238 — built and inspected the thin `page_html_v1` prototype: added
`scripts/spikes/marker_page_html_prototype.py` plus
`tests/test_marker_page_html_prototype.py` and normalized the Marker JSON seam
into `output/runs/story166-marker-page-html-r1/tbotb-mini/marker-v1102/lite-api/pages_html.jsonl`
with a separate provenance sidecar at
`output/runs/story166-marker-page-html-r1/tbotb-mini/marker-v1102/lite-api/marker_blocks.jsonl`.
Fresh checks: `python -m pytest tests/test_marker_page_html_prototype.py -q`
(`1 passed`), `python validate_artifact.py --schema page_html_v1 --file .../pages_html.jsonl`
(`Validation OK: 3 rows`), and `PYTHONPATH=. python modules/adapter/html_to_blocks_v1/main.py --pages .../pages_html.jsonl --out page_blocks.jsonl`
followed by `python validate_artifact.py --schema page_html_blocks_v1 --file .../page_blocks.jsonl`
(`Validation OK: 3 rows`). Manual artifact inspection:
- `.../pages_html.jsonl` page 1 now keeps the TOC lines as separate `<p block-type="Line">` elements and preserves the combat rules as a `<ul><li>` list.
- `.../marker_blocks.jsonl` preserves Marker block ids/bboxes (for example `marker_block_id = /page/0/TableOfContents/6`, `child_count = 5`, page 1) so the prototype's provenance loss is inspectable rather than hidden.
- `.../page_blocks.jsonl` shows the normalized pages are consumable by an existing downstream `doc-web` block parser.
Next step: compare the prototype against a freshly generated maintained OCR
baseline on the same fixture and record the boundary read honestly.

20260327-1256 — compared against the current maintained baseline and updated
tracker docs: ran
`python driver.py --recipe configs/recipes/recipe-pdf-ocr-html-mvp.yaml --input-pdf testdata/tbotb-mini.pdf --run-id story166-docweb-html-baseline-r1 --allow-run-id-reuse --output-dir output/runs/story166-docweb-html-baseline-r1 --end-at ocr_ai`
to produce
`output/runs/story166-docweb-html-baseline-r1/02_ocr_ai_gpt51_v1/pages_html.jsonl`,
validated it, and converted it with `html_to_blocks_v1` for a like-for-like
surface comparison. Wrote the comparison summary to
`output/runs/story166-marker-page-html-r1/tbotb-mini/marker-v1102/lite-api/comparison_summary.json`
and updated `docs/build-map.md` to replace the stale "no pipeline, no fixture,
no eval" born-digital gap language. Manual read:
- Marker and the maintained OCR baseline both reach `1.0` token coverage versus `pdftotext` on this 3-page fixture.
- Marker is structurally better in some ways: it preserves list semantics on page 1 and exposes a block-provenance sidecar (`marker_blocks.jsonl`) that the maintained OCR baseline does not have.
- Marker is still worse in other ways: page 2 section heading levels are inconsistent (`h4`/`h3`/`h2`), and page 3 keeps two choice sentences merged into one paragraph while the maintained OCR baseline splits them cleanly.
- Boundary decision for this story slice: the thin Marker seam is now a real repo-local native-text prototype and justifies a maintained follow-up story, but it does **not** yet clear the accepted `doc-web` provenance/runtime boundary for direct integration.
Fresh repo checks after the implementation and docs update: `make lint`
passed; `make test` passed (`377 passed`). Next step: run `/validate`, then
decide whether to keep this story open for the maintained follow-up or mark it
done as a bounded spike with the negative integration guard still explicit.

20260327-1947 — upgraded the prototype to a contract-aligned `doc-web` proof:
`scripts/spikes/marker_page_html_prototype.py` now annotates Marker-resolved
HTML with source ids/bboxes, writes a minimal `doc_web_bundle` pack, and emits
accepted `doc_web_provenance_block_v1` rows instead of leaving block
provenance in a story-local sidecar only. Fresh proof:
`python scripts/spikes/marker_page_html_prototype.py --input-pdf testdata/tbotb-mini.pdf --marker-json output/runs/story166-marker-probe-r1/tbotb-mini/marker-v1102/lite-api/json/tbotb-mini.json --marker-meta output/runs/story166-marker-probe-r1/tbotb-mini/marker-v1102/lite-api/json/tbotb-mini_meta.json --pdftotext output/runs/story166-marker-probe-r1/tbotb-mini/marker-v1102/tbotb-mini.pdftotext.txt --outdir output/runs/story166-marker-page-html-r2/tbotb-mini/marker-v1102/lite-api --run-id story166-marker-page-html-r2`
completed successfully. Validation passed for `page_html_v1`,
`doc_web_bundle_manifest_v1`, and `doc_web_provenance_block_v1`; the focused
regression `python -m pytest tests/test_marker_page_html_prototype.py -q`
also passed (`1 passed`). Manual inspection:
- `output/runs/story166-marker-page-html-r2/tbotb-mini/marker-v1102/lite-api/doc_web_bundle/provenance/blocks.jsonl`
  now contains `50` accepted provenance rows such as
  `blk-page-001-0001 -> /page/0/SectionHeader/0` with source bbox and
  `confidence = 1.0` under the explicit pdftext/zero-LLM policy.
- `output/runs/story166-marker-page-html-r2/tbotb-mini/marker-v1102/lite-api/runtime_trace.json`
  records `text_extraction_method = pdftext`, `llm_request_count = 0`, and the
  processing step for all three pages.
- `output/runs/story166-marker-page-html-r2/tbotb-mini/marker-v1102/lite-api/doc_web_bundle/page-003.html`
  still exposes the remaining defect honestly: the two choice prompts remain
  merged into a single paragraph.
Next step: rerun the literal pagelines baseline from Story 165's comparison
surface and fold it into the final boundary decision.

20260327-1956 — reran the current pagelines baseline and made the comparison
literal: `PYTHONPATH=. python modules/extract/extract_ocr_ensemble_v1/main.py --pdf testdata/tbotb-mini.pdf --outdir output/runs/story166-docweb-pagelines-baseline-r1 --start 1 --end 3`
completed successfully and wrote
`output/runs/story166-docweb-pagelines-baseline-r1/ocr_ensemble/pages/page-001.json`,
`page-002.json`, `page-003.json`, `pagelines_index.json`,
`ocr_quality_report.json`, and `ocr_source_histogram.json`. Surprise: the
current local pagelines baseline has drifted since Story 165. It still reaches
`1.0` token coverage and `1.0` heading-hit ratio on this fixture, but it now
shows `pdftext_text_pct = 0.0`, `source_histogram = {tesseract: 2, easyocr: 1}`,
and `pages_needing_escalation = [1, 2, 3]`. Wrote the literal comparison to
`output/runs/story166-marker-page-html-r2/tbotb-mini/marker-v1102/lite-api/comparison_pagelines_summary.json`.
Manual read:
- Marker is now stronger on the boundary this story cares about: native-text
  routing plus accepted `doc-web` block provenance.
- The pagelines baseline still retains line-level bboxes on `26` lines, so
  Marker is not strictly better on every provenance dimension.
- Marker still loses on two normalization details: page 2 heading levels are
  inconsistent and page 3 merges the two choice prompts.
Next step: lock the boundary decision against the exact follow-on story.

20260327-2006 — closed the story's decision ambiguity: created
`docs/stories/story-168-marker-lite-maintained-born-digital-pdf-path.md` as
the exact maintained follow-on story required by this slice and updated
`docs/stories.md`. Also reran the runtime bootstrap proof against the cached
local image with no seed-container dependency:
`python scripts/spikes/marker_breadth_benchmark.py --container-name story165-marker-cpu-9f4f --bootstrap-from-container story165-marker-cpu-missing --bootstrap-image doc-web/story165-marker-cpu:9f4f --mode lite_api --formats json --out-root output/runs/story166-marker-probe-r2`
followed by a `--skip-run` refresh against
`output/runs/story166-docweb-pagelines-baseline-r1`. The resulting
`output/runs/story166-marker-probe-r2/tbotb-mini/marker-v1102/summary.json`
shows `runtime.bootstrap.action = rebuilt_from_cached_image` with repo-local
`/work`, pip-cache, and model-cache mounts, which closes the original
worktree-bound container problem. Final boundary read for Story 166: positive
enough to justify maintained follow-on Story 168, but not clean enough for
direct runtime integration in this story because the heading/paragraph defects
still need maintained normalization work.

20260327-2036 — closed the remaining validation gaps without rescoping the
story: tightened the story prose to freeze the exact reusable seam
(`provider_from_filepath` -> `LayoutBuilder` -> `LineBuilder` ->
`DocumentBuilder(disable_ocr=True)` -> `StructureBuilder` ->
`OrderProcessor` / `BlockRelabelProcessor` / `LineMergeProcessor` /
`BlockquoteProcessor` / `DocumentTOCProcessor` / `IgnoreTextProcessor` /
`LineNumbersProcessor` / `ListProcessor` / `PageHeaderProcessor` /
`SectionHeaderProcessor` / `TextProcessor` / `ReferenceProcessor` /
`BlankPageProcessor` -> renderer) and made the ownership boundary explicit:
Marker/Surya remain optional spike-only because the current runtime still
carries GPL code, restricted commercial model-license posture, and
multi-gigabyte model loads. Also corrected the benchmark harness so the probe
summary now treats the current pagelines baseline as OCR-routed whenever it
falls back to OCR or escalation, not only when every page is `tesseract`.
Fresh verification on the final state:
- `python scripts/spikes/marker_breadth_benchmark.py --container-name story165-marker-cpu-9f4f --bootstrap-from-container story165-marker-cpu-missing --bootstrap-image doc-web/story165-marker-cpu:9f4f --mode lite_api --formats json --out-root output/runs/story166-marker-probe-r2 --skip-run --docweb-baseline-root output/runs/story166-docweb-pagelines-baseline-r1`
  rewrote `output/runs/story166-marker-probe-r2/tbotb-mini/marker-v1102/summary.json`
  with `current_local_baseline_is_still_ocr_routed = true`.
- `python -m py_compile scripts/spikes/marker_breadth_benchmark.py scripts/spikes/marker_page_html_prototype.py`
  passed.
- `python -m pytest tests/test_marker_page_html_prototype.py -q` passed (`1 passed`).
- `make lint` passed.
- `make test` passed (`377 passed`).
Local cache directories created by the repo-local bootstrap are now ignored via
`.gitignore`, so the story leaves no untracked runtime-noise behind.

20260327-2112 — story closed via `/mark-story-done`: fresh close-out validation
confirms the bounded spike is complete on current-pass evidence and the
remaining maintained integration work is explicitly split into Story 168
instead of being left ambiguous in this story. Fresh checks:
- `python -m ruff check modules/ tests/` passed.
- `python -m pytest tests/` passed (`377 passed`).
- `python scripts/spikes/marker_breadth_benchmark.py --container-name story165-marker-cpu-9f4f --bootstrap-from-container story165-marker-cpu-missing --bootstrap-image doc-web/story165-marker-cpu:9f4f --mode lite_api --formats json --out-root output/runs/story166-marker-probe-r2 --skip-run --docweb-baseline-root output/runs/story166-docweb-pagelines-baseline-r1`
  refreshed `output/runs/story166-marker-probe-r2/tbotb-mini/marker-v1102/summary.json`
  with `current_local_baseline_is_still_ocr_routed = true`.
- `python validate_artifact.py --schema page_html_v1 --file output/runs/story166-marker-page-html-r2/tbotb-mini/marker-v1102/lite-api/pages_html.jsonl`
  passed.
- `python validate_artifact.py --schema doc_web_bundle_manifest_v1 --file output/runs/story166-marker-page-html-r2/tbotb-mini/marker-v1102/lite-api/doc_web_bundle/manifest.json`
  passed.
- `python validate_artifact.py --schema doc_web_provenance_block_v1 --file output/runs/story166-marker-page-html-r2/tbotb-mini/marker-v1102/lite-api/doc_web_bundle/provenance/blocks.jsonl`
  passed.
Manual artifact inspection on this pass re-confirmed accepted block provenance
in `.../doc_web_bundle/provenance/blocks.jsonl`, page-level runtime trace in
`.../runtime_trace.json`, and the still-explicit heading/paragraph defects in
`.../doc_web_bundle/page-002.html` and `page-003.html`, which remain owned by
Story 168 rather than hidden here. ADR-002 remains satisfied: `doc-web` stays
the maintained boundary and Marker remains optional spike-only in this story.
Next step: `/check-in-diff`.
