# Current-page decode reuse

Story226 continuation in support of Ingester Story028, 2026-10-03. This measures
cached local crop execution and exact nonregression against Attempt054's
corrected outputs. Its residual p005 background hold remains; whole-manual
quality and whole-game economics are not qualified.

The corrected all32 native run was profiled before changing code:32.663s total,
63OpenCV decodes/6.911s,4.811s PIL source decoding,14.389s PNG encoding, and
ten local Tesseract calls/7.246s cumulative. Cumulative helper times overlap;
do not sum these numbers. Repeated OpenCV decoding is material, although
encoding/local OCR remain larger costs.

Freeze: private `corrected-baseline-frozen.json` hashes all corrected95figure
artifacts before the candidate. Compare path memoization with explicit arrays:
the smaller safe change passes one readonly native OpenCV BGR decode of the
current selected source page into four existing trimming/expansion helpers.
There is no global cache, path-key reuse, cross-page lookup, model decision,
new transform or request. The next page/invocation reads its source again.
Helper direct calls retain their normal decode behavior. A meaningful control
uses two targets sharing a page, then replaces pixels at the same path and
calls the cropper again: one color decode per invocation, refreshed output.

Three serial actual `driver.py` repetitions per arm use identical private
recipes, native OCR/planner/source inputs, PNG/auto controls and disabled API
rescue. The provider key is removed from each process environment. Crop-stage
seconds:

| Arm | Repeat1 | Repeat2 | Repeat3 | Median |
|---|---:|---:|---:|---:|
| Corrected baseline |36.96|35.92|35.92|35.92|
| Page-local decode |31.63|31.64|32.25|31.64|

Median local crop time is11.915%lower. Every run has95identical filenames,
95byte-identical PNGs,95exact RGBA arrays,95exact ICC values and95exact
normalized full manifest rows/bboxes. Only `run_id` and `created_at` are
excluded from row equality. Frozen corrected artifacts remain unchanged.
This includes alpha, unlike a visible-RGB-only comparison. Separately,
Attempt054's17larger crops have17/17exact RGBA in their old source-coordinate
overlap, zero newly hidden previously visible pixels.

77affected crop/planner/recipe-contract/semantic-pipeline tests pass3.64s;
selected Ruff passes. New provider calls/cost:0/0. Local Tesseract runs remain
included in crop execution; agent work and prior API spend are not zeroed.

Limits: three warm-machine repetitions per arm, baseline then candidate rather
than randomized/interleaved; OS caching/load/local OCR variance remain.
No separate held-out game, cold start or whole-document/game throughput claim.
The correction's p005-001 background/decoration hold remains explicit. No
subject inputs, goldens, existing receipts or published assets are overwritten.
Story226 stays In Progress. Root owns independent inspection and adoption.

Private evidence: `output/runs/story028-manual-speed-proof/` contains the
frozen baseline, profile/logs, unchanged recipe, all six driver outputs and
timings, `comparison.json`, and affected tests. Reproduce with a fresh output
directory/run ID using that recipe and `driver.py --instrument`; the exact
executed arguments are saved in baseline/candidate measurement JSON files.
[Tracked result](055-page-local-decode-reuse-result.json) records the current
candidate module hash, metrics and complete equality counts.

Integration numbering note: this was local Attempt054 when executed and is now
global055. The PNG producer comment using historical `Attempt055` refers to
the following PNG experiment, now global056; native code and proofs are unchanged.
