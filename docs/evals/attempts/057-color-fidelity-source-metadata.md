# Visible source-channel color metadata

Story226 continuation for Board Game Ingester Story028, 2026-10-03. This is a
bounded source-metadata correction, not a detector/model promotion or a claim
that the whole manual is qualified.

Independent review of the live Robo Rally serial arm found visibly colored,
source-exact PNGs marked `is_color=false`. The existing `_is_bw_image` compared
whole-image channel means, allowing balanced colors to cancel, then compared
mean chroma, allowing neutral backgrounds to dilute colored accents. Eight of
nine live serial crops were falsely marked B&W. Original PNGs were saved before
classification, and default transparency was disabled, so their pixels were
preserved. D's HTML builder uses original filenames/bytes; Ingester preserves
the exact manifest as evidence without branching on this flag. Optional
transparency would generate grayscale alpha derivatives from falsely B&W crops.

Six new controls fail on the frozen incumbent; three neutral controls pass.
The minimal correction classifies actual visible RGB channels: any channel
difference means color, alpha-zero pixels are ignored, and partly visible chroma
counts. Source paper tint remains source color. There are no thresholds, game
names, source-specific exceptions or new model calls. Exact channel equality
is a deterministic source property; model classification would add uncertainty
and cost without strengthening this pixel-preservation contract.

Nine controls cover balanced saturated colors, sparse color, source tint,
neutral RGB/L/1, hidden transparent chroma, partly visible chroma and actual
optional-transparency crop export. The integration control requires identical
original RGBA, ICC and geometry, correct metadata and no grayscale derivative.

A real cached driver replay uses the unchanged32-page OCR/planner/native inputs,
rescue disabled, empty API key and an unreachable local provider URL. Crop stage
completes in23.15s; this is one local execution observation, not a timing win.
All95 PNG files are byte-identical to the frozen compression3 incumbent; all95
RGBA arrays, ICC profiles and bboxes are identical. Full manifest rows match
excluding only `run_id`, `created_at` and the corrected `is_color` field.
All95 visible RGB arrays independently equal their native source rectangles.
92 false flags become true, taking the color count from3 to95. Existing source
tint is counted conservatively. Original frozen outputs and inputs are unchanged.

The source/original/candidate comparison sheet was inspected for p007 purple
cards/rainbow reserve, p008 blue conveyors, and p005 broad planner region.
They retain identical pixels. p005-001 still includes excess background and
hazard decoration; its existing quality hold remains. No crop golden changes,
whole-manual semantic claim, physical-family qualification or held-out tuning.

A broader affected run exposed an existing stale high-resolution custody test:
its planner omitted coordinate dimensions/source identity and used native bounds
as preview coordinates. The identical failure was reproduced using the exact
prepatch producer SHA. The fixture now supplies the actual100×80 preview basis,
source/page identity and half-size planner bounds mapping to the same intended
native rectangle (10,10)-(85,100). Runtime geometry guards and existing assertions
remain intact. After this fixture repair,111 affected color/crop/runtime/custody
controls pass in3.26s; selected Ruff and diff checks pass.

The current producer hash is
`1415611d111af76b588d33471ab137849aff1e0ad5f83351c70af6e07e90cbb9`.
Historical055/056 timing evidence and outputs are retained; this metadata-only
change does not reinterpret their measurements. Story226 remains In Progress.
The parent owns independent adoption and landing.

Private evidence: `output/story028-color-metadata-proof/` holds the baseline
failures, exact candidate, matched stale-fixture failure and test logs;
`output/runs/story028-color-metadata-proof/` holds the frozen95-output inventory,
recipe, real driver output/logs, complete comparison and source comparison sheet.
[Tracked result](057-color-fidelity-source-metadata-result.json) records exact
counts and changed metadata without bundling scans or provider payloads.
