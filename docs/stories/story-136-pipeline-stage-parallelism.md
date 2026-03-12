# Story 136 — Parallelize Crop Detection and Table Rescue Stages

**Priority**: High
**Status**: Draft
**Ideal Refs**: Ideal "instant" processing — "A 400-page scanned book processes before you finish your coffee"; MVF "under 30 minutes at reasonable cost"
**Spec Refs**: None
**Depends On**: None

## Goal

The Onward pipeline takes 51 minutes. OCR (13.7m) is already parallelized via `--concurrency 5`, but crop detection (16m) and table rescue (21.2m) are strictly sequential — one API call at a time. Adding ThreadPoolExecutor-based concurrency to these stages should bring total pipeline time well under 30 minutes (the MVF target). The pattern already exists in `ocr_ai_gpt51_v1` and can be replicated.

## Acceptance Criteria

- [ ] `crop_illustrations_guided_v1` supports a `--concurrency N` parameter for parallel page processing
- [ ] `table_rescue_html_loop_v1` supports a `--concurrency N` parameter for parallel page processing
- [ ] `table_rescue_onward_tables_v1` supports a `--concurrency N` parameter (if it exists as separate module)
- [ ] Recipe config passes concurrency to all parallelized stages
- [ ] Full Onward pipeline completes in under 30 minutes
- [ ] No change in output quality (same crops, same table content)
- [ ] Thread-safe JSONL writes (use locking pattern from OCR module)

## Out of Scope

- Inter-stage parallelism in `driver.py` (running OCR and crop detection simultaneously) — that's a larger architectural change
- Async/await rewrite — ThreadPoolExecutor matches existing pattern and is sufficient
- Rate limit tuning per API provider — use conservative defaults, let recipes override

## Approach Evaluation

- **Pure code**: This is strictly orchestration/plumbing — wrapping existing sequential loops in ThreadPoolExecutor. No reasoning involved. The OCR module already proves the pattern works.
- **Eval**: Before/after wall-clock time on full Onward pipeline. Output diff to verify no quality regression.

## Tasks

- [ ] Add `--concurrency` arg to `crop_illustrations_guided_v1` (default 1 for backward compat)
- [ ] Wrap page processing loop in ThreadPoolExecutor with thread-safe manifest writes
- [ ] Add `--concurrency` arg to `table_rescue_html_loop_v1`
- [ ] Wrap page processing loop in ThreadPoolExecutor with thread-safe JSONL writes
- [ ] Check `table_rescue_onward_tables_v1` for same pattern
- [ ] Update `recipe-onward-images-html-mvp.yaml` with concurrency settings for all stages
- [ ] Run full pipeline, compare wall time and output quality against baseline
- [ ] Run required checks:
  - [ ] `python -m pytest tests/`
  - [ ] `python -m ruff check modules/ tests/`
- [ ] Search all docs and update any related to what we touched
- [ ] Verify Central Tenets:
  - [ ] T0 — Traceability
  - [ ] T1 — AI-First
  - [ ] T2 — Eval Before Build
  - [ ] T3 — Fidelity
  - [ ] T4 — Modular
  - [ ] T5 — Inspect Artifacts

## Files to Modify

- `modules/extract/crop_illustrations_guided_v1/main.py` — add ThreadPoolExecutor, `--concurrency` arg, thread-safe writes
- `modules/extract/table_rescue_html_loop_v1/main.py` — same pattern
- `modules/extract/table_rescue_onward_tables_v1/main.py` — same pattern (if applicable)
- `configs/recipes/recipe-onward-images-html-mvp.yaml` — add concurrency params to crop/table stages

## Notes

- **Current parallelism state:**
  - OCR: `ThreadPoolExecutor(max_workers=concurrency)` with `--concurrency 5` — already fast (13.7m for 127 pages)
  - Crop detection: Sequential. 16 minutes for ~29 pages with images. Each page does CV detection + optional VLM rescue + optional VLM validation — multiple API calls per page.
  - Table rescue (both modules): Sequential. 21.2 minutes combined. Each page does one VLM call.
- **Rate limits**: OCR module adds 200ms delay between submissions when concurrency > 5. Similar throttling may be needed for crop/table stages depending on API provider limits.
- **Thread safety**: OCR module uses `threading.Lock()` for JSONL writes — same pattern should be used everywhere.
- **Expected speedup**: With concurrency=5, crop detection should drop from 16m to ~4m, table rescue from 21m to ~5m. Total pipeline: ~23m (under 30m target).
- **Inter-stage parallelism opportunity**: OCR and crop detection operate on the same pages independently. A future story could pipeline them (start cropping page N while OCR-ing page N+1). But intra-stage parallelism alone should hit the MVF target.

## Plan

{Written by build-story Phase 2}

## Work Log

{Entries added during implementation}
