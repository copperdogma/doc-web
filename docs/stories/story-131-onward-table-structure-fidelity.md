# Story 131 — Onward Table Structure Fidelity

**Priority**: High
**Status**: In Progress
**Ideal Refs**: Fidelity to Source (every table preserves its structure), Extract (layout preserved where it carries meaning — tables), Validate (prove output is correct)
**Spec Refs**: C1 (OCR accuracy), format-registry scanned-pdf-tables structure_preservation: 0.80
**Depends On**: Story 128 (golden references and eval infrastructure)
**Blocks**: Story 129 (HTML output polish), Story 130 (book website template)

## Goal

Drive the Onward scan-to-HTML pipeline's table structure fidelity from 0.80 to 0.95+, measured by the promptfoo eval against golden references. The pipeline should produce Dossier-ready HTML where every genealogy table faithfully represents the original scan — correct columns, no merged cells, no invented data, no LLM normalization.

HTML is the output format because it preserves semantics, images, basic layout, tables, and is excellent input for Dossier.

## Acceptance Criteria

- [ ] promptfoo `onward-table-fidelity` eval has a recorded baseline score in `docs/evals/registry.yaml`
- [ ] Structure preservation score reaches 0.95+ on the 3 golden reference families (alma, arthur, marie_louise)
- [ ] Format registry `scanned-pdf-tables` structure_preservation updated to reflect new measured score
- [ ] No regressions on text_fidelity (stays >= 0.93)
- [ ] Pipeline changes are in modules/prompts, not hand-edits to output artifacts

## Out of Scope

- Creating new golden references beyond the 3 from story-128
- Non-table content improvements (prose, illustrations)
- Website/presentation layer (that's story-130)
- Graduating the converter to Dossier

## Approach Evaluation

The eval already exists (`benchmarks/tasks/onward-table-fidelity.yaml`). The question is what intervention drives the score up most efficiently.

- **Simplification baseline**: Run the existing eval as-is. The eval has never been run — we don't actually know the current score. Maybe a model already nails it.
- **Model swap**: The eval tests Gemini 3 Pro, Gemini 2.5 Pro, GPT-4o — but the pipeline uses gpt-5.1. Add gpt-5.1 to the eval. A better model may solve this without code changes.
- **Prompt engineering**: The Onward tables have a specific 7-column layout (NAME/BORN/MARRIED/SPOUSE/BOY/GIRL/DIED). A more explicit prompt with column schema and examples may prevent LLM normalization.
- **Post-processing improvement**: `table_rescue_onward_tables_v1` already has BOY/GIRL splitting and header enforcement. These heuristics may need tuning or expansion based on eval failure patterns.
- **Scorer calibration**: The current scorer uses strict exact-match cell text. If it's failing on whitespace/punctuation differences that don't affect fidelity, the scorer needs adjustment before we chase phantom failures.
- **Eval**: `benchmarks/tasks/onward-table-fidelity.yaml` with `benchmarks/scorers/html_table_diff.py` is the gate. A test passes only when structural diff score >= 0.95.

## Tasks

- [ ] Run the existing eval to establish baseline scores for all 3 providers
- [ ] Register the eval and baseline in `docs/evals/registry.yaml`
- [ ] Analyze failure patterns from baseline (scorer output → classify as model-wrong vs scorer-wrong)
- [ ] Calibrate scorer if needed (whitespace normalization, header handling)
- [ ] Add gpt-5.1 to eval providers (it's the actual pipeline model)
- [ ] Implement highest-leverage fix based on failure analysis
- [ ] Re-run eval, record improvement
- [ ] Iterate until 0.95+ or document accepted limitations
- [ ] Update format registry scores
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

- `benchmarks/tasks/onward-table-fidelity.yaml` — add gpt-5.1 provider, tune config
- `benchmarks/scorers/html_table_diff.py` — calibrate if needed
- `modules/adapter/table_rescue_onward_tables_v1/main.py` — post-processing fixes
- `docs/evals/registry.yaml` — register eval and scores
- `tests/fixtures/formats/_coverage-matrix.json` — update structure_preservation score
- `docs/format-registry.md` — update prose to match

## Notes

- Story 128 produced the golden references and eval infrastructure. This story uses them.
- The eval has never been run — step 1 is establishing what we're actually working with.
- Known failure modes from story-128: BOY/GIRL count merging, continuation-row misalignment, date drift, column count mismatches, running head/page number leaking into cells.
- The scorer may have a header double-counting bug (see story-128 research) — investigate early.

## Plan

### Phase 1: Establish Baseline (eval-first)

**Task: Fix scorer bugs before running**
- `benchmarks/scorers/html_table_diff.py` — header parsing bug: `find_all('th')` on the whole table grabs colspan title rows (e.g., "Alma L'Heureux Alain") as a header row, creating phantom mismatches. Fix: parse headers from the first `<tr>` in `<thead>` (or first `<tr>` with `<th>` elements), not all `<th>` globally.
- `benchmarks/prompts/onward_ocr.js` — prompt says "6-column layout" but lists 7 columns. Fix the count.

**Task: Add gpt-5.1 to eval providers**
- `benchmarks/tasks/onward-table-fidelity.yaml` — add gpt-5.1 since it's the actual pipeline model. Also add `max_tokens` for OpenAI providers (AGENTS.md pitfall: truncation without it).

**Task: Run eval, record baseline**
- `cd benchmarks && promptfoo eval -c tasks/onward-table-fidelity.yaml --no-cache -j 3`
- Record results in `docs/evals/registry.yaml` as a new `onward-table-fidelity` entry.

### Phase 2: Diagnose Failures

**Task: Classify failures**
- For each test case × provider, examine scorer output
- Classify as: `model-wrong` (VLM produced bad HTML), `scorer-wrong` (scorer too strict), or `golden-wrong` (golden ref has issues)
- If scorer is the bottleneck (whitespace, punctuation, trivial formatting), calibrate it first
- Identify the top 3 failure patterns across models

### Phase 3: Fix & Iterate

**Task: Implement highest-leverage fix**
- Based on failure analysis, pick the approach that moves the score most:
  - Prompt improvement (column schema, examples, anti-normalization instructions)
  - Model swap (if one model already scores much higher)
  - Post-processing in `table_rescue_onward_tables_v1` (if failures are systematic and fixable)
- Re-run eval after each fix, record delta

**Task: Update format registry**
- `tests/fixtures/formats/_coverage-matrix.json` — update `structure_preservation`
- `docs/format-registry.md` — update prose

### Human Approval Blockers
- None anticipated — all changes are to existing eval/module files
- If scorer needs major redesign (fuzzy matching, partial credit), will flag before implementing

### What "done" looks like
- Eval registered in `docs/evals/registry.yaml` with baseline + improvement scores
- Structure preservation ≥ 0.95 on the 3 golden families, OR documented accepted limitations with rationale
- Format registry updated to reflect measured score
- No regressions on text fidelity

## Work Log

### 20260310-0001 — Exploration & plan
- **Files that will change**: `benchmarks/scorers/html_table_diff.py` (scorer bugs), `benchmarks/tasks/onward-table-fidelity.yaml` (add gpt-5.1), `benchmarks/prompts/onward_ocr.js` (prompt bug), `docs/evals/registry.yaml` (register eval), `tests/fixtures/formats/_coverage-matrix.json` + `docs/format-registry.md` (update scores)
- **Files at risk**: `modules/adapter/table_rescue_onward_tables_v1/main.py` (may need post-processing fixes depending on failure analysis)
- **Surprises found**: (1) Scorer has header parsing bug that will produce false failures on every test case (colspan title rows counted as data). (2) Prompt says 6 columns, lists 7. (3) Eval has literally never been run. (4) Pipeline model (gpt-5.1) not in the eval providers.
- **Pattern to follow**: Same eval-iterate loop as story-125/126 (image-crop-extraction)
- **Next**: Fix scorer + prompt bugs, add gpt-5.1 provider, run baseline eval
