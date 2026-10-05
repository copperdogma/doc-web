# Attempt 058 — Source-preserving manual runtime repairs

**Date:** 2026-10-04 (America/Edmonton)  
**Eval:** image-crop-extraction, bounded runtime continuation  
**Owning story:** 226; linked consumer: Board Game Ingester Story036  
**Registry lineage:** story_refs 133/183/207/226/232/235/236/237/238/239; category_refs spec:4/spec:8; compromise_refs C4.

The frozen Star Smuggler intake exposed downstream losses after the paid visual planner had already selected complete figures. Cleanup shortened sparse graph axes and removed integrated labels. The repair preserves planner-owned rectangles as lossless source-pixel PNGs, bypassing content-removal/rescue heuristics and rejecting out-of-source bounds. Non-planner cleanup remains available. A text-only booklet also exposed an invalid requirement for at least one essential figure, a catalog code misidentified as a folio, and dice ranges counted as physical spreads.

The validator now admits a zero-figure result only with exhaustive, distinct page coverage in both manifests, zero essential/useful/uncertain decisions and no unresolved page uncertainty. Printed-number fallback requires a terminal numeric paragraph plus independent sequence corroboration; a lone explicitly marked folio remains observed but cannot extrapolate a book. Physical-spread counts follow actual L/R split metadata, retaining unlabelled physical splits as unresolved.

## Applicable evidence

The [result manifest](058-star-smuggler-source-fidelity-result.json) binds all eight changed runtime/test files and the external immutable proof artifacts by SHA256. The prior focused backend suite records **241 passing tests in49.49s**; its invocation was not retained. Fresh close-out verification passes **241 tests in18.87s** plus **3 planner controls in0.53s**, with exact commands, Python versions, scope-file identities and check-configuration hashes now recorded in the result manifest. Actual partial `driver.py` proofs live in `output/runs/story036-printed-folio-driver-proof/` and `output/runs/story036-logical-map-driver-proof/`; the real consumer rules/events refinements also execute the native driver. The original paid OCR/planner ledgers remain unchanged and the repairs issue **zero provider calls**.

Independent inspection verifies all eight rules figures equal their recorded source rectangles, including all six graph topologies, ten system labels, Hopper labels/capacities and the full Antelope compartment plan. The events refinement retains all20 physical pages,231 event bodies and607 nonfigure blocks with unsupported printed labels null. Heading levels h2→h3 are an explicit structural delta; wording and source physical identities are preserved. The formal consumer package passes12/12 checks after copying away from producers with their paths and network access denied.

[Rules figure inspection](/Users/cam/.codex/worktrees/native-material-eval/boardgame-ingester/output/story036-star-smuggler-full-intake/independent-validation/refined-rules-graphics-validation.md), [events fidelity inspection](/Users/cam/.codex/worktrees/native-material-eval/boardgame-ingester/output/story036-star-smuggler-full-intake/independent-validation/refined-events-v3-text-equivalence-and-packet.md), [published owner review](/Users/cam/.codex/worktrees/native-material-eval/boardgame-ingester/output/story036-star-smuggler-full-intake/production-package-v2/review.html), and [isolated-copy proof](/Users/cam/.codex/worktrees/native-material-eval/boardgame-ingester/output/story036-star-smuggler-full-intake/portability-proof/report.md) are locally retained.

## Conclusion and limits

The bounded runtime repairs are validated. No maintained detector score, model default, golden, cost/speed claim or broad corpus admission changes. Source pixels are from qualified PDF-composited rasters; embedded byte/channel identity is not claimed. Consumer text restoration/navigation and remaining source-edition questions are separate. Story226 remains In Progress with its existing Robo Rally qualification holds. Revalidate affected code and driver artifacts if the bound runtime inputs or check environment change; do not rerun paid OCR simply to land this repair.

## Close-out check configuration

Fresh scoped command (no paid inference):

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/cam/.codex/worktrees/native-material-eval/boardgame-ingester/output/story036-star-smuggler-full-intake/runtime/bin/python -m pytest -q tests/test_crop_illustrations_guided_v1.py tests/test_extract_page_numbers_html_v1.py tests/test_graphic_manual_semantic_pipeline.py tests/test_infer_logical_page_order_v1.py tests/test_build_chapter_html.py tests/test_normalize_graphic_manual_html_v1.py tests/test_crop_runtime_recipe_contract.py
```

The same Python3.12.11 command separately runs `tests/test_plan_critical_graphics_vlm_v1.py` (3 passing controls). Ruff0.15.2 under established miniconda Python3.11.5 checks all eight changed files and passes; the result manifest gives the exact invocation. The private proof Python has no Ruff, so the initial probe failed before switching checker environments. The 30 pytest warnings are retained in the fresh log. No fresh full-suite claim, inference run or dependency installation is implied.
