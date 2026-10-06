# Literal table fidelity investigation — 2026-10-06

Planning evidence for [Story 245](../stories/story-245-preserve-literal-table-text.md).
No runtime change, source mutation, paid model call or new pipeline run occurred.

## Finding

The source prints `LSU: life support unit (r2l3)` with lowercase `l` in the
`r236 Equipment Table`, physical and printed page 19 of
`starsmuggler_eh_rules_11.pdf`. Source pixels and fresh native text extraction
agree. First saved DocWeb OCR already contains `r213` in `raw_html` and `html`;
page-number extraction, normalization and final HTML retain it. The earliest
observable failure is therefore at the OCR boundary. This does not distinguish
visual misreading, language-model normalization or raster preparation effects.

Final HTML links `r213` to `chapter-008.html#blk-chapter-008-0027`. A working
link does not prove fidelity. Source `r2l3` must survive even without a target.

## Evidence locations and identity

Read active Ingester thread **“Triage and complete project work”**, ID
`01a0f371-c93c-77f3-bf9a-483e80465100`, on 2026-10-06. Worktree:

`/Users/cam/.codex/worktrees/story038-land-1005/boardgame-ingester`

Paths below are relative to that worktree unless marked otherwise. These are
local diagnostic artifacts, not checked-in fixtures or globally trusted runs.

- Source: `output/story039-restart/fresh-e/raw-inputs/manuals/starsmuggler_eh_rules_11.pdf`.
  SHA256 `758215f3f4157b0a07873fdf7e59b56d55ab3ae44fd4334ea28f26b4b7aca334`.
- Run root (`R` below):
  `output/story039-restart/fresh-e/work/intake/manual-stages/primary/runs/manual-b16bc5770e564ac0a3a979a7be1d1033`.
- `R/snapshots/recipe.yaml`: requested `gpt-5.1`, `max_long_side: 2048`,
  `max_output_tokens: 8192`, concurrency 3; exact-rule-text/table instructions.
  Requested ID is not independently verified served-model evidence.
- `R/03_infer_logical_page_order_v1/pages_logical_manifest.jsonl`: page,
  page_number and original_page_number all 19; image is
  `R/02_split_pages_from_manifest_v1/images/page-019.png`.
- `R/04_ocr_ai_gpt51_v1/pages_html.jsonl` SHA256
  `6221f894c6cd955a475e5e9a6946fe58b705fc0b81d41e5b69364ea244ca49de`:
  both HTML fields contain LSU `r213`.
- `R/07_extract_page_numbers_html_v1/pages_html_with_page_numbers.jsonl` SHA256
  `bbf9cb76845553015418ae3e3ea58f2e2d30163694bcff2d0da5b1d2b64f11cc`:
  same text, explicit printed page 19, not inferred.
- `R/09_normalize_graphic_manual_html_v1/pages_manual_normalized.jsonl` SHA256
  `ce93f29c04c62e2cba1b32d6f831cb410e566489564d7d7f6679726366355dd5`:
  same cell text.
- `R/output/html/chapter-019.html` SHA256
  `5a16bc1d72f7df8ef859a6d8e1bcc17333078cc70472c8f17b929b80fa83f8e9`:
  linked `r213`, CU `1`, original note text.
- `output/story039-restart/continuation-f-independent-quality/final/table-review.md`
  and `table-grades.json`: sealed consumer audit reports 84/84 numeric cells,
  17/18 equipment rows, 0/2 group headers, 6/6 recovery rows. These are historical
  audit results, not new broad grading by this investigation.

The executed recipe has **no table_rescue_html_loop_v1 stage**. Run state marks
OCR skipped on a later `--skip-done` continuation; preserve recovery history
before reproducing a call. Do not rerun into this live Ingester worktree or
alter frozen packages. Before future upstream reuse, perform the prescribed
scope-specific run-health/assessment check.

Current and frozen `modules/extract/ocr_ai_gpt51_v1/main.py` match SHA256
`a9db81b3d7ed5066a25e4fe24f47c725677014dce677fc8449080b5e90552f6f`.
`_ocr_with_fallback` retains raw response HTML after fence/metadata removal,
then separately sanitizes it. The substitution predates sanitization in the
preserved data, subject to historical artifact lineage.

## Direct inspection and local controls

Opened the complete page-19 render and native glyph detail:

- `/Users/cam/.codex/worktrees/fresh-context-intake/boardgame-ingester/output/story038-completion-v4/independent-fresh-plan/rules-p19.png`
- `/Users/cam/.codex/worktrees/fresh-context-intake/boardgame-ingester/output/story038-completion-v4/independent-fresh-results/additional-source-reading-errata/T3-reference-glyph-native-detail.png`

The detail distinguishes LSU `r2l3` from nearby Utility Suit `r213` and Repair
Unit `r211b`. These source views support glyph reading; they are not new
current-pipeline render proofs.

Fresh read-only Poppler extraction against the original PDF:

```bash
pdftotext -f 19 -l 19 -layout "$source_pdf" -
pdftotext -f 19 -l 19 -bbox-layout "$source_pdf" -
```

Complete source row (cell separators added for readability):

`LSU: life support unit (r2l3) | 1 | need if good atmosphere is not present except when in starship or orbital shuttle`

`-bbox-layout` locates `(r2l3)` at xMin 147.000000, yMin 248.076000,
xMax 168.920000, yMax 257.380000 in its page coordinate system. First-cell line
bounds are xMin 60.400000, yMin 248.076000, xMax 168.920000, yMax 257.380000.
This demonstrates native text/location recovery here, not general table alignment.

Existing scorer `_score_matched_rows` on the two-cell row
`['LSU: life support unit (r2l3)', '1']` versus its `r213` variant reports 2
cells / 1 error; unchanged self-control reports 2 / 0. This diagnostic probe
is not a corpus eval. Review its broader alignment and quote normalization
before claiming exact literal/structure coverage.

## Bounded research and recommendation

General problem class: **source-faithful transcription with confusable glyphs
and independent evidence alignment**. Semantic plausibility is insufficient.

- [PyMuPDF text extraction documentation](https://pymupdf.readthedocs.io/en/latest/app1.html)
  describes word/character extraction with locations and extraction-order limits.
  Adopt region-bound evidence; flat text alone does not prove table ownership.
  Existing Poppler demonstrated corresponding functionality locally; no new
  PyMuPDF dependency was installed.
- [Library of Congress ALTO description](https://www.loc.gov/standards/alto/description.html)
  supplies an established model for OCR content, layout and source/processing
  information. Adapt that evidence principle to current sidecars; do not add
  ALTO as a new bundle boundary for this bug.
- [ADR-001](../decisions/adr-001-source-aware-consistency-strategy/adr.md) favors
  selective source-aware extraction over guessing from damaged HTML.
  [ADR-002](../decisions/adr-002-doc-web-runtime-boundary/adr.md) retains the
  structural HTML/provenance boundary.

Recommended experiment: freeze literal/structure goldens, compare current OCR
with a strongest practical single-call baseline, and test qualified native text
as independent evidence. If needed, detect disagreements in code and escalate
a bounded source region with row/column context. Accept source-supported text,
retain original artifacts and before/after evidence. Prefer a simple extraction
improvement if it clears the full gate; do not preselect a repair subsystem.

Native text is not universally authoritative: faulty encoding, invisible OCR
layers and ambiguous geometry can disagree with visible pixels. Use source-image
review or uncertainty in those cases. Image-only PDFs have no native witness,
so this evidence does not support a universal native-only fix.

## Substrate and remaining uncertainty

- Source/page/image/raw/cleaned HTML exist in `schemas.py` and real outputs;
  per-cell witness and repair contracts do not yet exist.
- Existing table rescue checks structural symptoms, not exact source literals,
  and did not run here. Any selected integration must reach the affected recipe.
- Historical Onward verification is prior art, not proof on this document.
  Reference resolution adds navigation but cannot restore transcription.
- Still unmeasured: current strongest model, image-preparation impact, native
  coverage across tables, alignment safety, cost/latency and independent
  confirmation. No production default or coverage score changes here.
- Ingester repair/snapshot work remains owned there. No message was sent to
  its thread and no Ingester file was modified.

## Completion evidence update — 2026-10-06

The initial unmeasured questions above were tested in Attempt 062. A stronger lossless300dpi singlecall preserves original equipment57/57cells, includingr2l3, but fails independently reserved workshop confirmation. FullOCRadoption is rejected. The selected opt-in recipe instead adds one source-image-only tableinventory/read, exact initial/source agreement and explicituncertainty, with bound typedreports and an enforced builder exportgate. No native authority or repair is added. Fresh clear native/image-only cases qualify36/36cells; a proved identical-glyph negative retains one transcriptionerror but flags both sourcecells and holds beforeexport. Original correct diagnosticHTML remains unqualified; original/workshop productiongates hold. This is generic conservative handling, not a claim to recover optically indistinguishable encodings.

See `docs/evals/attempts/062-literal-table-fidelity.md` and `docs/evals/evidence/062-literal-table-fidelity-summary.json` for inspected artifactpaths, rejected approaches, current source-backed policy, budgets, separate accuracy/coverage, and independentreview. Sharedscorer/runtime changes contain no exampletokens, documentnames or replacementpairs. Synthetic sources/proofs are retained under `testdata/literal-table-fidelity/`; no original privatePDF or Ingester workspace mutation. C1/C3/C6 and formatcoverage remain unchanged.
