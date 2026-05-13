# Crop Eval Workflow Runbook

Operational guide for running and improving the maintained crop benchmark
surfaces.

## Prerequisites

- promptfoo installed (`npm install -g promptfoo`)
- API keys for the provider/model slice you are running. The current maintained
  crop-only C5 command uses `DOC_WEB_GEMINI_API_KEY`, and the current
  page-context C5 deletion gate uses `DOC_WEB_OPENAI_API_KEY`, both through
  `scripts/run_with_doc_web_env.py`.
- Checked-in local crop benchmark fixtures under:
  - `benchmarks/input/source-pages-b64/`
  - `benchmarks/input/crop-validation-b64/`
- Checked-in goldens under:
  - `benchmarks/golden/image-crops.json`
  - `benchmarks/golden/crop-validation.json`
  - `benchmarks/golden/crop-page-level-deletion-gate.json`

## Running the Maintained Surfaces

```bash
# Detector-quality surface (C4-linked)
cd benchmarks && promptfoo eval -c tasks/image-crop-extraction.yaml --no-cache -j 3

# Dedicated bounded text-exclusion / crop-quality surface (C5-linked)
cd benchmarks && promptfoo eval -c tasks/crop-validation.yaml --no-cache \
  --filter-providers 'google:gemini-3.1-flash-lite' \
  --filter-prompts 'caption-focus' \
  --output results/crop-validation-story183-g31-caption-focus.json \
  -j 1

# Page-context deletion gate for the maintained runtime overlap corpus
cd benchmarks && ../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/crop-page-level-deletion-gate.yaml --no-cache \
  --output results/crop-page-level-deletion-gate-gpt55-responses-current-20260424.json \
  -j 1

# Clean-checkout smoke checks
cd benchmarks && ../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/image-crop-extraction.yaml --no-cache --filter-first-n 1 -j 1 --no-write
cd benchmarks && ../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/crop-validation.yaml --no-cache --filter-first-n 1 -j 1 --no-write
cd benchmarks && ../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/crop-page-level-deletion-gate.yaml --no-cache --filter-first-n 1 -j 1 --no-write
```

View results: `promptfoo view`

## Current State

- **Registry entries**:
  - `image-crop-extraction` — page-level detector-quality surface linked to `C4`
  - `crop-validation` — dedicated bounded crop-only text-exclusion / crop-quality surface linked to `C5`
  - `crop-page-level-deletion-gate` — page-context deletion-gate surface for the maintained runtime overlap corpus
- **Maintained detector prompt set**: `baseline`, `strict-exclude`, `two-step`, `conservative-count`
- **Current detector score**: `image-crop-extraction` best recorded result is `0.9703` overall / `1.0` pass rate (Gemini 3 Flash `conservative-count` on the maintained task, rerun on 2026-04-10; tracked proof note: `docs/evals/attempts/001-image-crop-extraction-story207-proof-refresh.md`)
- **Current C4 deletion-gate score**: `single-model-crop-detection` is `0.9703` overall / `1.0` pass rate on that same maintained single-stage rerun, so the bounded deletion gate still passes. Use the same tracked proof note above as the portable summary; the raw promptfoo JSON remains a local regenerable artifact.
- **Maintained runtime note**: Stories 184 and 198 proved the reviewed Onward
  lane can delete the retired retry / refine / validate surface from both the
  maintained recipe and the shared runtime without regressing the published
  crop/build seam. The maintained recipe still keeps
  `rescue_caption_second_pass` plus `trim_layout_text`; removing them widened
  the certificate/seal crop on page 12 and duplicated nearby text in the final
  HTML.
- **Current dedicated C5-linked score**: `crop-validation` is `1.0` overall / `1.0` pass rate on the checked-in 40-crop corpus (Gemini 3.1 Flash Lite + `caption-focus`, measured 2026-04-11)
- **Current page-context C5 deletion-gate score**: `crop-page-level-deletion-gate` is `1.0` overall / `1.0` pass rate on the checked-in `22`-case overlap corpus with GPT-5.5 Responses + `page-context` promptfix, measured 2026-04-24 on the corrected golden. The previous Gemini 3.1 Flash Lite `22/22` result is stale after the `page-122-001` golden correction; the fresh Gemini rerun is `21/22`.
- **Current C5 decision**: residue is still required. The page-context corpus still contains `5` explicit fail-labeled current-runtime cases (`page-018-000`, `page-092-000`, `page-122-000`, `page-122-001`, `page-126-000`), so `trim_layout_text` and bounded caption assist do not have an honest deletion proof yet.
- **Spec compromises**:
  - `C4` — Two-Stage Image Crop Detection
  - `C5` — Layout Text Trim Heuristics for Crops

## Improvement Cycle

Use `/improve-eval image-crop-extraction` when the question is detector quality,
and use the same evidence discipline for both `crop-validation` and
`crop-page-level-deletion-gate` when the question is crop/text-exclusion proof:
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
| `benchmarks/tasks/crop-page-level-deletion-gate.yaml` | page-context deletion-gate validation config |
| `benchmarks/scorers/image_crop_scorer.py` | IoU + count + text scoring |
| `benchmarks/scorers/crop_validation_scorer.py` | crop pass/fail scorer |
| `benchmarks/input/README.md` | tracked crop fixture contract |
| `benchmarks/golden/` | Golden bounding boxes and crop verdicts |
| `docs/evals/registry.yaml` | Score history and attempts |
| `modules/crop_illustrations/` | Pipeline module under test |

## Pitfalls

- **VLM non-determinism**: Gemini at temperature=0.0 still varies. Re-run evals with `--no-cache` and inspect artifacts instead of depending on retired runtime auto-retry behavior.
- **promptfoo provider formats**: OpenAI, Anthropic, and Google each need different image payload formats. Use JS prompt functions with `provider.id` detection.
- **Bbox format**: Gemini returns `[x0, y0, x1, y1]` (array), not `{x0, y0, x1, y1}` (dict). Parser handles both.
- **The `.b64.txt` fixtures are canonical**: the maintained crop fixtures are
  downscaled benchmark inputs, not trivial wrappers around raw JPEGs. Repointing
  the task configs to raw images changes the eval surface.
- **Keep the surfaces distinct**: `crop-validation` is still the bounded
  crop-only surface. `crop-page-level-deletion-gate` is the broader page-context
  C5 decision surface. Do not collapse them back together casually.
- **Keep the maintained prompt set honest**: the registry and runbook assume
  `tasks/image-crop-extraction.yaml` contains the winning `conservative-count`
  prompt. If that prompt drifts back out of the maintained task, the C4 surface
  becomes misleading even if the sidecar prompt-comparison task still exists.
