# Story 138 — Onward Genealogy Table Continuation and Header Regressions

**Priority**: High
**Status**: Pending
**Ideal Refs**: Requirement #3 (Extract), Requirement #6 (Validate), Fidelity to Source
**Spec Refs**: C1 (OCR quality), C3 (layout detection)
**Depends On**: Story 131 (table structure fidelity), Story 129 (HTML output polish)

## Goal

Fix the reviewed Onward genealogy-table regressions that remain in final HTML despite earlier table-fidelity work: merged headers, family-table tails drifting into the next family’s chapter, and terminal summary rows or family headers getting detached or lost.

## Acceptance Criteria

- [ ] Reviewed genealogy tables stay attached to the correct family chapter in the current verification run; no reviewed chapter begins with the previous family’s leftover table rows
- [ ] Reviewed genealogy tables include their own terminal rows and summary counts (`Total/Descendants/Living/Deceased`) instead of spilling those rows into the next family
- [ ] Reviewed family table headers render correctly, including separate `BOY` and `GIRL` columns and the missing `Antoine L'Heureux` family header
- [ ] Manual verification of regenerated chapters confirms the reviewed Arthur/Josephine-Paul/Roseanna-Antoinette-Emilie/Pierre-Antoine table spans are structurally correct and self-contained

## Out of Scope

- Missing prose pages or chapter-boundary defects
- Image placement, image attachment, or caption pairing issues
- New table golden-reference creation unrelated to the reviewed regressions

## Approach Evaluation

- **Simplification baseline**: Trace the reviewed failing tables through the existing rescued-table artifacts and compare them to final HTML. If the rows already exist upstream, fix the continuation or export stages instead of re-solving OCR.
- **AI-only**: Re-run only the flagged table pages through a stronger table rescue prompt/model. This is justified only if the table tails are actually missing from upstream rescued HTML.
- **Literal-row fallback**: If direct image-to-HTML rescue is still model-wrong on the reviewed pages, test a stricter "one visual line = one JSONL row" transcription pass on just the flagged spans, then assemble HTML deterministically. Treat this as a fallback tactic inside this story, not a new default pipeline architecture.
- **Hybrid**: Use deterministic tracing to find whether the problem is in rescue, continuation fixing, or export; apply targeted AI only to the pages whose table structure is genuinely unresolved.
- **Pure code**: If the reviewed summary rows exist upstream but are dropped or misaligned later, fix the post-processing/continuation logic deterministically.
- **Eval**: Reviewed-table fidelity is the gate: the cited headers and terminal count rows must appear in final HTML on the correct family chapter, with no cross-family leakage.

## Tasks

- [ ] Trace the reviewed table-bleed defects through `table_rescue_onward_tables_v1`, `table_fix_continuations_v1`, chapter portionization, and final HTML to identify the exact failure stage
- [ ] Diagnose whether each reviewed defect is model-wrong, post-processing-wrong, or export-wrong
- [ ] If upstream rescue is still model-wrong on the reviewed spans, compare the current direct-HTML prompt against a literal-row JSONL stepping-stone prompt before adding more deterministic cleanup
- [ ] Fix the highest-leverage root cause for the reviewed header and tail-row regressions
- [ ] Add regression coverage or eval coverage for the reviewed table tails and header alignment cases
- [ ] Regenerate and manually verify the reviewed chapters
- [ ] Run required checks:
  - [ ] `python -m pytest tests/`
  - [ ] `python -m ruff check modules/ tests/`
- [ ] Search all docs and update any related to what we touched
- [ ] Verify Central Tenets:
  - [ ] T0 — Traceability: every output traces to source page, OCR engine, confidence, processing step
  - [ ] T1 — AI-First: didn't write code for a problem AI solves better
  - [ ] T2 — Eval Before Build: measured SOTA before building complex logic
  - [ ] T3 — Fidelity: source content preserved faithfully, no silent losses
  - [ ] T4 — Modular: new recipe not new code; no hardcoded book assumptions
  - [ ] T5 — Inspect Artifacts: visually verified outputs, not just checked logs

## Files to Modify

- `modules/adapter/table_rescue_onward_tables_v1/main.py` — if the reviewed rows/headers are already wrong in rescue output
- `modules/adapter/table_fix_continuations_v1/main.py` — if reviewed tail rows disappear or shift during continuation repair
- `modules/build/build_chapter_html_v1/main.py` — if reviewed table tails exist upstream but are assigned to the wrong chapter during final HTML assembly
- `benchmarks/tasks/onward-table-fidelity.yaml` — if the reviewed regressions need to be promoted into eval coverage
- `tests/test_onward_table_regressions.py` — new regression coverage for reviewed header/tail cases

## Notes

- Manual review defects feeding this story:
  - `chapter-009.html` in the original review — `BOY/GIRL` merged, `Died` header displaced
  - `chapter-011.html`, `chapter-026.html`, `chapter-027.html`, `chapter-028.html` in the original review — missing terminal genealogy-table rows or summary counts
  - `story137-onward-verify` round-2 review:
    - `chapter-009.html` tail rows incorrectly start `chapter-010.html`
    - `chapter-011.html` tail rows incorrectly start `chapter-012.html`
    - `chapter-012.html` tail rows incorrectly start `chapter-013.html`
    - `chapter-013.html` tail rows incorrectly start `chapter-014.html`
    - `chapter-014.html` tail rows incorrectly start `chapter-015.html`
    - `chapter-017.html` cuts off the last half of Emilie Nolin’s table into `chapter-018.html`
    - `chapter-018.html` loses the bottom total/living/deceased counts into the next family page
    - `chapter-021.html` cuts off Pierre L'Heureux’s table into `chapter-022.html`
    - `chapter-022.html` starts with the prior family’s tail and is missing the `Antoine L'Heureux` table header
- Story 131 proved high benchmark fidelity on the golden tables. This story exists because real-run HTML still shows reviewed regressions that the benchmark set did not catch.

## Plan

{Written by build-story Phase 2}

## Work Log

### 20260312-1710 — story created from manual review
- **Result:** Created a focused follow-up story for reviewed genealogy-table regressions that remain in the final Onward HTML despite earlier table-fidelity work.
- **Evidence:** User review identified merged `BOY/GIRL` headers in `chapter-009.html` plus missing terminal summary rows/tails in `chapter-011.html`, `chapter-026.html`, `chapter-027.html`, and `chapter-028.html`.
- **Next:** Build-story should trace each reviewed defect through the rescued-table artifacts before deciding whether the fix belongs in rescue, continuation repair, or final HTML assembly.

### 20260313-0905 — round-2 manual review shows repeated cross-family table bleed
- **Result:** The latest verification run confirms the table problem is broader than missing terminal rows: genealogy-table tails are repeatedly assigned to the next family chapter.
- **Evidence:**
  - `output/runs/story137-onward-verify/output/html/chapter-009.html` through `chapter-015.html` show a repeated pattern where one family’s table tail appears at the start of the next family chapter
  - `output/runs/story137-onward-verify/output/html/chapter-017.html` through `chapter-022.html` show the same bleed pattern again, plus a missing `Antoine L'Heureux` table header
- **Decision:** Keep this story focused on family-table ownership and tail-row continuity, not just single-page header alignment.
- **Next:** Build this story from the current `story137-onward-verify` run and trace whether the bleed starts in `table_rescue_onward_tables_v1`, `table_fix_continuations_v1`, or chapter assignment.

### 20260313-1040 — inbox OCR stepping-stone idea folded into story
- **Result:** Triaged the inbox "two-step line-by-line transcription" idea into this story as a fallback experiment, not a new standalone story.
- **Evidence:** Story 131 already proved direct table rescue can hit the benchmark gate, but the real-run regressions in `story137-onward-verify` still show cross-family tail bleed and header loss that may warrant a stricter row-presence tactic on flagged spans.
- **Decision:** First trace whether the defect is post-processing/export. Only if the reviewed rows are genuinely wrong or missing upstream should this story compare direct HTML rescue against a literal-row JSONL stepping-stone pass.
- **Next:** During build-story execution, use the current reviewed spans to decide whether the fallback earns promotion into regression coverage or can be discarded after diagnosis.
