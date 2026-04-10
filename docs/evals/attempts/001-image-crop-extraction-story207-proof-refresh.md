# Attempt 001 — image-crop-extraction: Story 207 proof refresh

**Eval:** `image-crop-extraction`
**Date:** 2026-04-10
**Worker Model:** `gpt-5` Codex
**Subject Model / Surface:** `Gemini 3 Flash` + `conservative-count` on `benchmarks/tasks/image-crop-extraction.yaml`
**Mission:** Refresh the maintained crop detector proof from `0.9678 / 1.0` to a current-pass verified score and give the coverage-row truth refresh a durable repo-backed proof anchor.
**Registry Lineage:** `story_refs: [133, 183, 207]`; `category_refs: [spec:4, spec:8]`; `compromise_refs: [C4]`

## Prior Attempts

- Story 133 first moved the maintained detector surface to Gemini 3 Flash and
  landed the `0.900` detector proof.
- Story 183 repaired the promptfoo substrate and restored the maintained
  `conservative-count` prompt, lifting the comparable detector score to
  `0.918 / 1.0`.
- Story 184 refined the maintained prompt contract to exclude heading-style
  display text and recorded `0.9678 / 1.0`, but the linked repo-local result
  JSON later proved unavailable in the current worktree.
- Story 207 exists because the canonical coverage rows stayed at `0.9` even
  though the crop proof surfaces had already moved higher.

## Plan

1. Rerun the maintained `image-crop-extraction` task on the current tip using
   the winning Gemini 3 Flash + `conservative-count` slice.
2. Recompute the aggregate from the written JSON instead of trusting a UI-only
   summary.
3. Re-open the reviewed Onward publication seam from Stories 184 and 198 so the
   coverage-row uplift still ties back to a real crop/publication surface.
4. Record the verified result in a tracked note so spec/runbook/registry do not
   depend on an ignored local `benchmarks/results/*.json` path.

## Work Log

20260410-1355 — Ran:

```bash
cd benchmarks && promptfoo eval -c tasks/image-crop-extraction.yaml --no-cache \
  --filter-providers 'google:gemini-3-flash-preview' \
  --filter-prompts 'conservative-count' \
  --output results/story207-image-crop-baseline.json \
  -j 1
```

The run completed successfully with `13/13` passes, `0` failures, and `0`
errors. Recomputing the mean from the per-case scores in
`benchmarks/results/story207-image-crop-baseline.json` yielded `0.9703`.
Supporting signals from the same JSON: total duration `104537 ms`, prompt tokens
`17329`, completion tokens `1180`, reasoning tokens `15523`, total tokens
`34032`, and total eval cost about `$0.059`. Weakest cases in the same pass:
`Image000 = 0.8164`, `Image124 = 0.9566`, `Image037 = 0.9676`.

20260410-1358 — Re-opened the reviewed Onward publication seam instead of
rerunning OCR/build stages. Verified
`/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/03_crop_illustrations_guided_v1/illustration_manifest.jsonl`
exists with `40` rows and still includes two `page-012-*` crops. Verified
`/Users/cam/Documents/Projects/codex-forge/output/runs/onward-full-audit-20260318-r1/output/html/chapter-003.html`
exists and still embeds both `page-012-000.jpg` and `page-012-001.jpg`.
Conclusion: the detector proof refresh still sits on top of the same reviewed
publication seam used by Stories 184 and 198.

20260410-1422 — Validation follow-up found that
`benchmarks/results/story207-image-crop-baseline.json` is ignored by
`benchmarks/.gitignore`, so it should remain a regenerable execution artifact
rather than the sole canonical proof path. This tracked note now serves as the
repo-backed proof anchor, while the ignored JSON remains the local raw output
that produced the summarized metrics above.

## Conclusion

**Result:** succeeded

**Score before:** `0.9678 / 1.0` overall / pass rate on the maintained detector
surface (2026-04-03)
**Score after:** `0.9703 / 1.0` overall / pass rate on the maintained detector
surface (2026-04-10), average latency about `7878 ms` per page, total eval cost
about `$0.059`

**What worked:**
- Reusing the maintained `conservative-count` slice gave a clean comparable rerun.
- Recomputing the mean from the stored per-case scores avoided relying on a UI
  summary alone.
- Re-checking the reviewed Onward manifest/HTML seam kept the coverage-row
  uplift tied to a real publication surface.
- Moving the proof summary into this tracked note fixed the portability gap in
  the canonical truth surfaces.

**What did not work:**
- `Image000` remains the weakest maintained case at `0.8164`; the detector is
  still slightly inset on the full-cover crop.
- The full promptfoo JSON remains an ignored local artifact and should not be
  cited as the only long-term proof anchor.

**What not to retry without new evidence:**
- Do not reopen a broad model sweep just to chase a small decimal improvement;
  the maintained crop gate already clears comfortably.
- Do not resurrect a detector-vs-format split story for these two coverage rows
  unless a new authored source explicitly changes that contract.

**Retry when:**
- `new-subject-model`: a later Gemini or GPT release may materially improve the
  remaining `Image000` full-cover weakness.
- `golden-fix`: if the maintained 13-page crop corpus changes, rerun and update
  this proof note plus the registry.

## Definition of Done

- [x] Read the target eval's prior attempts first
- [x] Confirm the eval's explicit lineage fields in `docs/evals/registry.yaml`
- [x] Measured a before state or confirmed the current recorded baseline
- [x] Recorded after-state metrics
- [x] Updated `docs/evals/registry.yaml`
- [x] Classified major mismatches when the eval used a golden or rubric
- [x] Filled in the Conclusion section completely
- [x] Documented retry conditions or dead ends if the attempt failed
