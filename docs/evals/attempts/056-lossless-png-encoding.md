# Lossless PNG encoding speed/size tradeoff

Story226 continuation for Ingester Story028, 2026-10-03. This measures one
encoding-only change after Attempt055's page-local decode reuse. Foreground
correction, source selection, masks, transforms and p005 background hold stay
unchanged. No model or source-family tuning.

Freeze the corrected+decode-reuse95figure outputs and producer hash before
the candidate. The existing Pillow PNG save surface permits compression3
instead of its default6. A native95image probe measures+8.725%total PNG bytes.
Predeclared bounded admission: every decoded pixel/alpha/ICC/manifest invariant
passes, median local crop time improves at least5%, and total PNG size grows
no more than25%. The candidate sets compression3 on all four PNG export save
branches (cover, RGBA, ordinary PNG, generated alpha); JPEG policy stays intact.
PNG compression changes the lossless bitstream, never dimensions or sampling.

Three fresh serial actual cached `driver.py` runs per arm use the identical
recipe, retained OCR/planner/native sources and rescue disabled:

| Arm | Repeat1 | Repeat2 | Repeat3 | Median |
|---|---:|---:|---:|---:|
| Decode reuse, PNG6 |33.02s|31.90s|31.93s|31.93s|
| Decode reuse, PNG3 |25.33s|25.51s|25.35s|25.35s|

Median local crop time is20.608%lower. PNG bytes increase from45,520,699 to
49,492,322 (+8.725%,3.79MiB), within the declared storage bound. All95PNG
bitstreams differ explicitly; every run retains95exact RGBA arrays (including
alpha),95exact ICC values,95exact normalized full manifest rows/bboxes and
the same filenames. Only `run_id`/`created_at` are excluded from row equality.
Original corrected frozen files remain unchanged. Key p007 candidate image
was opened and inspected; the restored five purple card bottoms remain whole.
Earlier source-coordinate alpha audits remain applicable because decoded
candidate arrays are identical to the corrected incumbent.

79affected crop/planner/recipe-contract/semantic-pipeline tests pass2.41s;
selected Ruff passes. Two new RGB/RGBA controls assert exact native source
pixels and ICC metadata through public crop export. Zero new provider calls
or provider cost; local OCR remains included in execution, and agent effort
and prior API spend are not relabelled as zero.

Limits: warm-machine repetitions, baseline followed by candidate rather than
interleaved/randomized; OS/load/local OCR variation remains. PNG bytes are
larger, a declared storage tradeoff; this is local crop-stage evidence, not
cold-start/whole-game economics. p005-001 broad planner background/decoration
remains a quality hold. No independent-game/full-manual or physical-family
promotion. Story226 stays In Progress; root owns independent adoption/landing.

Private proof: `output/runs/story028-manual-png-proof/` contains the prechange
freeze, one-level probe, identical recipe, six native driver outputs/logs,
measurement arguments/timings, equality/size comparison and affected checks.
[Tracked result](056-lossless-png-encoding-result.json) binds the current
producer hash and complete measured counts. Reruns require fresh run IDs and
output directories, using the retained recipe and `driver.py --instrument`.

Integration numbering note: this was local Attempt055 when executed. A concurrent
upstream attempt occupied global053, so the three local public notes became
054/055/056. Private proof directories, measured producer hashes and native
outputs remain unchanged. The producer's historical `Attempt055` comment refers
to this PNG experiment; no source edit was made just to renumber documentation.
