---
title: "Fix Source-Only Front Matter Replay in Non-TOC HTML Build"
status: "Done"
priority: "High"
ideal_refs:
  - "Requirement #3 (Extract), Requirement #5 (Structure), Requirement #6 (Validate), Requirement #7 (Export), Traceability is the product, Fidelity to the source"
spec_refs:
  - "spec:2"
  - "spec:3"
  - "spec:6"
  - "spec:7"
adr_refs:
  - "ADR-002"
depends_on: []
category_refs:
  - "spec:2"
  - "spec:3"
  - "spec:6"
  - "spec:7"
compromise_refs:
  - "C1"
  - "C3"
input_coverage_refs:
  - "scanned-pdf-prose"
architecture_domains:
  - "doc_web_runtime"
roadmap_tags:
  - "campaign:maintained-intake-honesty"
legacy_system: ""
---

# Story 213 — Fix Source-Only Front Matter Replay in Non-TOC HTML Build

**Priority**: High
**Status**: Done
**Decision Refs**: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, `docs/decisions/adr-002-doc-web-runtime-boundary/adr.md`, `docs/stories/story-206-onward-full-book-regression-recovery.md`, `tests/fixtures/formats/_coverage-matrix.json`, and `None found after search in docs/decisions/ and docs/runbooks/ for a narrower non-TOC front-matter replay owner`

## Goal

Prevent `build_chapter_html_v1` from replaying a chapter opening when
`portionize_headings_html_v1` emits an unnumbered front-matter heading followed
by the real printed chapter starting at the same numeric label. In the failing
memoir run, a source-only title-page portion with `source_pages=[1]` was
misread as printed page `1`, causing the chapter builder to merge the same
source page into `chapter-001.html` twice and preserve a worse truncated first
copy of the opening paragraph.

## Acceptance Criteria

- [x] A source-only heading portion in a mixed paginated document no longer
      steals the first printed chapter page in `build_chapter_html_v1`.
- [x] The affected source-only page remains available in final output via the
      fallback-page path instead of duplicating chapter content.
- [x] Regression coverage proves the memoir-shaped collision pattern yields one
      opening sequence only, with the continuation paragraph preserved once.
- [x] Fresh current-pass verification records an artifact path from a real
      `driver.py` run on the memoir PDF showing the duplicate opening is gone.

## Tasks

- [x] Trace the duplicate opening to the owning stage with artifact evidence.
- [x] Patch the non-TOC chapter builder to treat source-only front matter
      honestly in mixed paginated documents.
- [x] Add focused regression coverage for the source-page/printed-page `1`
      collision pattern.
- [x] Re-run the memoir pipeline through `driver.py` and inspect the rebuilt
      HTML/provenance artifacts.
- [x] Update this work log with current-pass evidence and any residual risk.
- [x] Search all docs and update any related to what we touched.
- [x] Verify Central Tenets:
  - [x] T0 — Traceability: the repaired chapter and fallback page still cite source-page-backed provenance rows end to end.
  - [x] T1 — AI-First: the fix repairs a deterministic assembly bug rather than replacing it with extra OCR or prompt churn.
  - [x] T2 — Eval Before Build: the bug was reproduced from final HTML plus provenance artifacts before code changed.
  - [x] T3 — Fidelity: the opening sequence now appears once and keeps the full continuation paragraph.
  - [x] T4 — Modular: the fix stays inside the generic non-TOC chapter-builder seam with a bounded regression test.
  - [x] T5 — Inspect Artifacts: the rebuilt memoir HTML and provenance outputs were manually reopened in this pass.

## Workflow Gates

- [x] Build complete: implementation finished, required checks run, and summary shared
- [x] Validation complete or explicitly skipped by user
- [x] Story marked done via `/mark-story-done`

## Work Log

20260411-1535 — exploration: reproduced the duplicate opening from `/Users/cam/Documents/Projects/doc-web/output/runs/rolland-alain-memoir-r01/output/html/chapter-001.html` and traced it into `output/html/provenance/blocks.jsonl`, where `blk-chapter-001-0001` through `0012` show page-2 source elements replayed twice. Repo-backed cause: `build_chapter_html_v1` preferred printed-page matches over `source_pages`, so the first `heading-derived-source-pages` portion (`source_pages=[1]`) grabbed source page 2 because its `printed_page_number` is `1`; the later real chapter portion then carry-back merged page 2 again. Files likely to change: `modules/build/build_chapter_html_v1/main.py`, `tests/test_build_chapter_html.py`, and this story file. Decision context checked: `docs/ideal.md`, `docs/spec.md`, `docs/methodology/state.yaml`, `docs/methodology/graph.json`, ADR-002, and Story 206. Next: land the smallest bounded builder fix and re-run the memoir path through `driver.py`.
20260411-1545 — implementation + verification: updated `build_chapter_html_v1` so `heading-derived-source-pages` portions resolve against `source_pages` instead of printed-page ranges, and in mixed paginated documents those source-only front-matter portions stay uncovered so the fallback-page path owns them rather than replaying the first printed chapter page. Added a focused CLI regression in `tests/test_build_chapter_html.py` for the memoir-shaped `source_pages=[1]` / `printed_page_number=1` collision; `python -m pytest tests/test_build_chapter_html.py -q` passed (`95 passed`), `make lint` passed, and `make methodology-compile && make methodology-check` refreshed the generated story surfaces cleanly. Fresh real-path proof: copied the memoir run artifacts locally to `output/runs/rolland-alain-memoir-r01/` and re-ran `driver.py` from `portionize_headings` with `/tmp/story213-memoir-non-toc.yaml`, reusing OCR/table/crop artifacts; the rebuilt artifacts now show `output/html/page-001.html` containing only the source-only cover heading `Memoires de Rolland Alain`, while `output/html/chapter-001.html` contains one opening sequence only. Manual checks: the rebuilt chapter has `March 7th 1985` once, the opening H1 once inside `<article>`, and provenance rows now advance directly from `blk-chapter-001-0001`/`p002-b1` through `blk-chapter-001-0006`/`['p002-b6','p003-b1']` without replaying `p002-b1`-`p002-b6` a second time. Residual risk: this fix is intentionally bounded to `heading-derived-source-pages` in mixed paginated docs; if a future document needs unnumbered front matter promoted to a real chapter instead of a fallback page, that should be handled as an explicit new policy decision rather than by reintroducing printed-page guessing here.
20260411-1556 — /mark-story-done closeout: re-ran the full required checks on the current story tip: `python -m pytest tests/` (`564 passed, 4 warnings in 0:10:41`), `python -m ruff check modules/ tests/`, `make lint`, `make methodology-compile`, and `make methodology-check`. Re-opened `output/runs/rolland-alain-memoir-r01/output/html/page-001.html`, `output/runs/rolland-alain-memoir-r01/output/html/chapter-001.html`, and `output/runs/rolland-alain-memoir-r01/output/html/provenance/blocks.jsonl`; the cover heading still lives only on the fallback page, the chapter opening still appears once, the truncated paragraph is absent, and the first provenance rows still advance cleanly from `p002-b1` through `['p002-b6','p003-b1']`. Story status set to `Done`, final workflow gate checked, and generated methodology/story views refreshed. Next: `/check-in-diff`.
