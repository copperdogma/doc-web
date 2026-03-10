# Crop Eval Workflow Runbook

Operational guide for running and improving the image crop extraction eval.

## Prerequisites

- promptfoo installed (`npm install -g promptfoo`)
- API keys: `GEMINI_API_KEY` (in `.zshrc`, may need `source ~/.zshrc` for bash)
- Golden references in `benchmarks/golden/`

## Running the Eval

```bash
cd benchmarks && promptfoo eval -c tasks/image-crop-extraction.yaml --no-cache -j 3
```

View results: `promptfoo view`

## Current State

- **Registry entry**: `image-crop-extraction` in `docs/evals/registry.yaml`
- **Target**: overall ≥ 0.95, pass_rate ≥ 0.90
- **Best score**: 0.856 (Gemini 3 Pro detector + Gemini 2.5 Flash validator)
- **Spec compromise**: C4 (Two-Stage Image Crop Detection)

## Improvement Cycle

Use `/improve-eval image-crop-extraction` for the structured loop:
1. Reads registry, checks if passing, reviews attempt history
2. Diagnoses failure modes from scorer output
3. Proposes approaches (never retries blocked ones)
4. Measures before/after
5. Records attempt in registry

## Verifying Results

After any eval run, use `/verify-eval` to classify mismatches:
- **Model-wrong**: Detector hallucinated a crop or missed one
- **Golden-wrong**: Golden bounding box is inaccurate or missing a valid crop
- **Ambiguous**: Edge case (decorative border, partial illustration)

Only verified scores are recorded in the registry.

## Key Files

| File | Purpose |
|------|---------|
| `benchmarks/tasks/image-crop-extraction.yaml` | promptfoo eval config |
| `benchmarks/scorers/image_crop_scorer.py` | IoU + count + text scoring |
| `benchmarks/golden/` | Golden bounding boxes per page |
| `docs/evals/registry.yaml` | Score history and attempts |
| `modules/crop_illustrations/` | Pipeline module under test |

## Pitfalls

- **VLM non-determinism**: Gemini at temperature=0.0 still varies. Auto-retry on count mismatch leverages this.
- **promptfoo provider formats**: OpenAI, Anthropic, and Google each need different image payload formats. Use JS prompt functions with `provider.id` detection.
- **Bbox format**: Gemini returns `[x0, y0, x1, y1]` (array), not `{x0, y0, x1, y1}` (dict). Parser handles both.
