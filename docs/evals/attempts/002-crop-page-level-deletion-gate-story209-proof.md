# Attempt 002 — crop-page-level-deletion-gate: Story 209 proof

**Eval:** `crop-page-level-deletion-gate`
**Date:** 2026-04-11
**Worker Model:** `gpt-5` Codex
**Subject Model / Surface:** `Gemini 3.1 Flash Lite` + `page-context` prompt on `benchmarks/tasks/crop-page-level-deletion-gate.yaml`
**Mission:** Create a repo-owned page-context C5 deletion-gate surface that pairs maintained runtime crops with source-page context, then decide whether `trim_layout_text` and bounded caption assist are still required on the maintained Onward lane.
**Registry Lineage:** `story_refs: [209]`; `category_refs: [spec:4, spec:8]`; `compromise_refs: [C5]`

## Prior Attempts

- Story 183 repaired the bounded `crop-validation` substrate and promoted the
  40-crop crop-only validator as the maintained C5-linked surface.
- Story 209 first reran that bounded validator on 2026-04-10 and confirmed it
  still scored `1.0 / 1.0`, which proved the benchmark was healthy but still
  crop-only.
- The first page-context prompt run in this story reached `21/22` on
  2026-04-11 and missed `page-126-000`; the mismatch was prompt-wrong because
  the prompt tolerated “minimal” external plaque text leakage that the golden
  correctly labels as a fail.

## Plan

1. Expand the checked-in full-page fixture set just enough to cover the known
   fail pages missing from the original 13-page detector corpus.
2. Add a sibling page-context task that shows the source page and maintained
   crop together while reusing the maintained crop pass/fail semantics.
3. Run the new surface, inspect representative pass/fail rows, and anchor the
   result in a tracked note instead of relying on ignored promptfoo JSON.
4. Use the labeled corpus itself to make the C5 decision: if explicit fail
   cases remain in the current maintained page-context corpus, keep the
   remaining residue and stop.

## Work Log

20260411-0018 — Expanded the checked-in page fixture corpus by adding
`Image017.b64.txt`, `Image091.b64.txt`, and `Image125.b64.txt` under
`benchmarks/input/source-pages-b64/`, all resized to the same `1545x2000`
shape as the existing maintained detector fixtures. This widened the
page-context overlap corpus from `18` crop/page pairs with `1` fail-labeled
case to `22` crop/page pairs with `4` fail-labeled cases:
`page-018-000`, `page-092-000`, `page-122-000`, and `page-126-000`.

20260411-0021 — Added the new sibling maintained surface:
`benchmarks/tasks/crop-page-level-deletion-gate.yaml`,
`benchmarks/prompts/validate-page-level-crop.js`, and
`benchmarks/golden/crop-page-level-deletion-gate.json`. The new task pairs each
checked-in crop with its checked-in source page context and reuses the existing
crop pass/fail scorer logic through
`benchmarks/scorers/crop_validation_scorer.py` plus a new `golden_relpath`
override. Focused integrity coverage now checks both page and crop assets in
`tests/test_crop_benchmark_substrate.py`.

20260411-0026 — First full run:

```bash
cd benchmarks && promptfoo eval -c tasks/crop-page-level-deletion-gate.yaml \
  --no-cache \
  --output results/story209-crop-page-level-deletion-gate-g31-page-context.json \
  -j 1
```

Result: `21/22` passes, `1` failure, `0` errors. The only miss was
`page-126-000`, where the model returned
`{"verdict":"pass","has_page_text":true,...}` because the prompt tolerated
small adjacent plaque-text leakage. Classification: prompt-wrong, not
golden-wrong.

20260411-0029 — Tightened `benchmarks/prompts/validate-page-level-crop.js` to
fail any surrounding page text from an adjacent plaque, neighboring figure, or
page layout even when the main subject is correct, then reran:

```bash
cd benchmarks && promptfoo eval -c tasks/crop-page-level-deletion-gate.yaml \
  --no-cache \
  --output results/story209-crop-page-level-deletion-gate-g31-page-context-v2.json \
  -j 1
```

Final result: `22/22` passes, `0` failures, `0` errors, mean score `1.0`,
duration `61863 ms`, and total tokens `56945`. Representative inspected rows
from the written JSON:

- `page-012-001` → `pass` / TN, with the reason that the seal text is integral
  to the visual element.
- `page-018-000` → `fail` / TP for page-level caption text leakage.
- `page-122-000` → `fail` / TP for caption text below the reunion photo.
- `page-126-000` → `fail` / TP after the prompt fix, for neighboring plaque
  text visible on the left side.

20260411-0032 — Re-opened the reviewed runtime-publication seam used by
Stories 184 and 198 to keep the new surface tied to real maintained artifacts.
Confirmed:

- `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/images/page-012-001.jpg`
  still exists and is referenced from
  `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/chapter-003.html`
  with the expected `page-012-001.jpg` figure and figcaption.
- `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/images/page-122-000.jpg`
  still exists and is referenced from
  `/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/chapter-024.html`
  alongside `page-122-001.jpg`.

## Conclusion

**Result:** succeeded

**Score before:** no maintained page-context C5 deletion-gate surface

**Score after:** `1.0 / 1.0` overall / pass rate on the new 22-case
page-context overlap corpus (Gemini 3.1 Flash Lite + `page-context`, measured
2026-04-11)

**What worked:**
- Adding only the missing fail-page source fixtures kept the new surface small
  and repo-owned while making the fail corpus honest.
- Reusing the existing crop pass/fail semantics kept the scorer simple and made
  the distinction from the older 40-crop bounded surface explicit.
- One prompt-tightening pass was enough to remove the only false negative.

**What did not work:**
- The first prompt draft was too tolerant about minimal adjacent plaque-text
  leakage and misclassified `page-126-000`.
- The raw promptfoo JSON remains ignored and should stay a local execution
  artifact rather than the sole proof anchor.

**Decision:** the remaining C5 residue is still required. The new page-context
surface is now honest and passing as a judge, but the corpus it judges still
contains `4` explicit fail-labeled current-runtime residue cases:
`page-018-000`, `page-092-000`, `page-122-000`, and `page-126-000`. That is
not an honest basis for deleting `trim_layout_text` or bounded caption assist
from the maintained Onward lane.

**What not to retry without new evidence:**
- Do not reopen the Story 184 “remove caption assist now” move on the same
  maintained runtime.
- Do not treat the bounded 40-crop `crop-validation` surface as the full C5
  deletion gate now that the page-context companion surface exists.

**Retry when:**
- `new-subject-model`: a materially stronger validator or detector may reduce
  the current fail-labeled page-context cases.
- `runtime-change`: a fresh maintained runtime simplification or crop logic
  change should rerun this page-context surface before any C5 deletion claim.
- `golden-fix`: if the page-context corpus or fail reasons change, rerun and
  update this note.

## Definition of Done

- [x] Read the target eval's prior attempts first
- [x] Confirm the eval's explicit lineage fields in `docs/evals/registry.yaml`
- [x] Measured a before state or confirmed the current recorded baseline
- [x] Recorded after-state metrics
- [x] Updated `docs/evals/registry.yaml`
- [x] Classified major mismatches when the eval used a golden or rubric
- [x] Filled in the Conclusion section completely
- [x] Documented retry conditions or dead ends if the attempt failed
