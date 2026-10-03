# Critical crop foreground-preservation correction

Story226 continuation, 2026-10-03; initiated by Board Game Ingester Story028's
quality-first hillclimb. This repairs a measured deterministic loss, not a
maintained detector score or full-manual qualification.

The original native `p007-g01` planner rectangle ends at y1497. The generic
bottom-prose helper misclassified sparse card borders and shortened it to y1471;
the exported figure lost the lower borders/tips of five purple programming
cards. Direct source and crop inspection confirmed the missing pixels exist
in logical source page7 (native2829x3625, SHA256
`b5f6de09d204bd04ea8d2636ad0ae853ebc5aa72b0e506f9a13873862a806e76`).
Five minimum source-pixel support rectangles were frozen before the patch;
their evidence hash is recorded in the result JSON. These supports do not
define a full outline or background golden.

The candidate rejects a proposed prose trim when a connected dark/saturated
foreground component crosses the cut, and requires a background separator
before removing a detached band. It preserves the existing genuine detached
prose control. A synthetic gray card/border regression changes from original
y373 (amputated) to candidate y420 (retained). No game identifiers or geometry
answers enter the production helper. The deterministic choice preserves a
source rectangle; another semantic model call is unnecessary for the measured
cause and would add cost without correcting this downstream truncation.

Two actual `driver.py` runs load the unchanged retained native OCR/planner
artifacts, disable rescue, and use existing PNG/auto crop controls. Page7's
crop stage takes2.52s; all32 logical input pages take34.75s in the crop stage.
The latter emits the same95 filenames:78 PNGs byte-identical and17 larger
source rectangles. All95 visible RGB arrays equal their recorded native
source rectangles; five frozen p007 supports pass. No new provider calls or
provider cost. These execution times are not an economics comparison.

All17 changed figures were inspected against old crops and full sources on
three comparison sheets. Sixteen restore diagram/card/board/conveyor edges.
`page-005-001.png` restores lower register tops but also retains excessive
whitespace and hazard-stripe decoration from its broad planner target; this
is an explicit residual background-quality hold. Complete outlines, all-page
semantic quality, full-manual cleanliness, independent-game generalization,
source embedded-pixel qualification and whole-game economics remain open.
No original inputs, receipts, published packages or incumbent assets changed.

Private proof directory:
`output/runs/story028-manual-trim-proof/`, containing frozen support evidence,
`support-result.json`, `comparison.json`, `native-pixel-checks.json`, three
`changed-sheet-N.jpg` inspection sheets, full driver logs/timing/outputs, and
affected-test logs. The result summary tracks hashes/counts without private
scan bytes: [result](054-critical-crop-no-amputation-result.json).

Reproduction from this worktree (private recipes and retained inputs required):

```sh
PYTHONDONTWRITEBYTECODE=1 env -u OPENAI_API_KEY /Users/cam/miniconda3/bin/python3.11 driver.py --recipe output/runs/story028-manual-trim-proof/page7.yaml --run-id story028-manual-trim-page7 --output-dir output/runs/story028-manual-trim-proof/page7 --instrument
PYTHONDONTWRITEBYTECODE=1 env -u OPENAI_API_KEY /Users/cam/miniconda3/bin/python3.11 driver.py --recipe output/runs/story028-manual-trim-proof/all32.yaml --run-id story028-manual-trim-all32 --output-dir output/runs/story028-manual-trim-proof/all32 --instrument
```

Use fresh run IDs/output directories for a rerun; never overwrite the proof.
Affected crop, planner, recipe-contract and semantic-pipeline tests pass;
specific counts and applicable module hash are recorded with closeout evidence.
Story226 remains In Progress. Parent owns independent inspection and adoption.

Follow-up alpha audit compares all17 changed crops over their overlapping source
coordinates:17/17RGBAexact, zero newly hidden previously visible pixels. Thus
the larger rectangles did not introduce new alpha-mask loss in existing support.
The cached decode candidate in Attempt055 preserves every corrected PNG byte,
RGBA, ICC value and normalized manifest row across three independent outputs.
