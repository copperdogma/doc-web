# Attempt 050 — Preserve planned critical figures in deterministic cropping

Owner: Story 226; spec:4 and spec:6; C4/C5 remain unchanged. This is source-bound runtime fidelity evidence, separately scoped from the maintained detector benchmark/model scores. No new provider calls.

At base009afed, the same frozen current Sol/low plan loses three complete targets during deterministic subdivision: a nine-card reference strip becomes seven sampled card crops, the page10 board with three linked callouts becomes two isolated gear squares, and a three-card reference strip becomes three crops. Generic target ownership guards preserve all101 nondecorative targets through the splitter boundary, compared with98/101 intact baseline targets. New split controls preserve detector metadata and target rectangles; legacy untargeted segmentation still runs. No document-name/page-coordinate branching or new recipe option.

Applicable direct source replay: `output/runs/story226-target-preservation-probe-20260930-v3/report.json`, source-plan SHA a3c3497f838deeb826b2bd3d333dbabc3110496f05a8acc9aba6bcfa15de7021. First two retained exploratory probes used non-recipe helper parameters or omitted area_ratio population and are diagnostic only. V3 matches actual stage defaults and area_ratio population. Native input/rectangles are retained; these are rule figures, not independently qualified physical production assets.

Actual zero-API partial `driver.py` continuation runs the current native graphics recipe from crop_illustrations through validate_manual_html against immutable prior OCR/plan/split outputs. Artifact root:
`/Users/cam/.codex/worktrees/native-material-eval/boardgame-ingester/output/story025-fresh-no-cache-20260930-v2/manual-stages/fresh/refinements/target-preservation/runs/refined-36cdcd35600e4d298ce3df424fea1305`.
The integration-owned output location is deliberate: the public Ingester workflow invokes the native doc-web driver and keeps the entire campaign's source/runtime/provider history together. No fake run or symlink was created in doc-web. The direct diagnostic probe lives under doc-web output/runs.

The native conformance report has22 pass/0 warning/0 failure checks,32 logical pages,108 crop artifacts,97 HTML figures and615 provenance rows. Manifest contains101 distinct complete planner targetIDs plus7untargeted crops, including six page25 fallback card regions. Personally opened actual page010whole board and page 25 fallback cards, plus direct native reference strips. Page10 now preserves the connected board, colored arrows and three callouts. Fallback page25's final two crops still omit card titles; six crops do not prove six complete faces. Retain this known fidelity/review limitation rather than claiming whole-manual perfection.

Focused validation:35 crop tests pass (2.59 s),142 planner/build/semantic-pipeline tests pass (16.98 s), affected Ruff check and gitdiffcheck pass; methodology compile/check pass. No paid detector rerun, golden edits, model replacement, new approval or unrelated original-checkout edits. The historical reviewed Story 226 baseline remains immutable.

Tracked source-safe result: `docs/evals/attempts/050-critical-figure-preservation-result.json`.
