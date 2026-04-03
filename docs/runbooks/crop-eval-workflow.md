# Crop Eval Workflow Runbook

Operational guide for running and improving the maintained crop benchmark
surfaces.

## Prerequisites

- promptfoo installed (`npm install -g promptfoo`)
- API keys for the provider/model slice you are running. The current maintained
  dedicated C5-linked command uses `GEMINI_API_KEY`.
- Checked-in local crop benchmark fixtures under:
  - `benchmarks/input/source-pages-b64/`
  - `benchmarks/input/crop-validation-b64/`
- Checked-in goldens under:
  - `benchmarks/golden/image-crops.json`
  - `benchmarks/golden/crop-validation.json`

## Running the Maintained Surfaces

```bash
# Detector-quality surface (C4-linked)
cd benchmarks && promptfoo eval -c tasks/image-crop-extraction.yaml --no-cache -j 3

# Dedicated bounded text-exclusion / crop-quality surface (C5-linked)
cd benchmarks && promptfoo eval -c tasks/crop-validation.yaml --no-cache \
  --filter-providers 'google:gemini-3.1-flash-lite-preview' \
  --filter-prompts 'caption-focus' \
  --output results/crop-validation-story183-g31-caption-focus.json \
  -j 1

# Clean-checkout smoke checks
cd benchmarks && promptfoo eval -c tasks/image-crop-extraction.yaml --no-cache --filter-first-n 1 -j 1 --no-write
cd benchmarks && promptfoo eval -c tasks/crop-validation.yaml --no-cache --filter-first-n 1 -j 1 --no-write
```

View results: `promptfoo view`

## Current State

- **Registry entries**:
  - `image-crop-extraction` — page-level detector-quality surface linked to `C4`
  - `crop-validation` — dedicated bounded text-exclusion / crop-quality surface linked to `C5`
- **Maintained detector prompt set**: `baseline`, `strict-exclude`, `two-step`, `conservative-count`
- **Current detector score**: `image-crop-extraction` best recorded result is `0.918` overall / `1.0` pass rate (Gemini 3 Flash conservative-count prompt on the maintained task, measured 2026-04-03)
- **Current dedicated C5-linked score**: `crop-validation` is `1.0` overall / `1.0` pass rate on the checked-in 40-crop corpus (Gemini 3.1 Flash Lite + `caption-focus`, measured 2026-04-03)
- **Spec compromises**:
  - `C4` — Two-Stage Image Crop Detection
  - `C5` — Layout Text Trim Heuristics for Crops

## Improvement Cycle

Use `/improve-eval image-crop-extraction` when the question is detector quality,
and use the same evidence discipline for the dedicated `crop-validation`
surface:
1. Reads registry, checks if passing, reviews attempt history
2. Classifies failures before changing prompts, scorers, or goldens
3. Proposes approaches (never retries blocked ones)
4. Measures before/after
5. Records the verified attempt in the registry

## Verifying Results

After any eval run, keep the verification pass inside `/improve-eval` or an
equally explicit documented loop:
- **Model-wrong**: detector hallucinated a crop, missed one, or validator
  misclassified a checked crop
- **Golden-wrong**: golden bounding box or crop verdict is inaccurate or
  incomplete
- **Ambiguous**: edge case (decorative border, partial illustration, integral
  text versus page text)

Only verified scores are recorded in the registry.

## Key Files

| File | Purpose |
|------|---------|
| `benchmarks/tasks/image-crop-extraction.yaml` | promptfoo eval config |
| `benchmarks/tasks/crop-validation.yaml` | dedicated crop pass/fail validation config |
| `benchmarks/scorers/image_crop_scorer.py` | IoU + count + text scoring |
| `benchmarks/scorers/crop_validation_scorer.py` | crop pass/fail scorer |
| `benchmarks/input/README.md` | tracked crop fixture contract |
| `benchmarks/golden/` | Golden bounding boxes and crop verdicts |
| `docs/evals/registry.yaml` | Score history and attempts |
| `modules/crop_illustrations/` | Pipeline module under test |

## Pitfalls

- **VLM non-determinism**: Gemini at temperature=0.0 still varies. Auto-retry on count mismatch leverages this.
- **promptfoo provider formats**: OpenAI, Anthropic, and Google each need different image payload formats. Use JS prompt functions with `provider.id` detection.
- **Bbox format**: Gemini returns `[x0, y0, x1, y1]` (array), not `{x0, y0, x1, y1}` (dict). Parser handles both.
- **The `.b64.txt` fixtures are canonical**: the maintained crop fixtures are
  downscaled benchmark inputs, not trivial wrappers around raw JPEGs. Repointing
  the task configs to raw images changes the eval surface.
- **Keep the maintained prompt set honest**: the registry and runbook assume
  `tasks/image-crop-extraction.yaml` contains the winning `conservative-count`
  prompt. If that prompt drifts back out of the maintained task, the C4 surface
  becomes misleading even if the sidecar prompt-comparison task still exists.
