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
- **Current detector score**: the fresh comparable quality leader is GPT-5.6 Terra at `0.9689` / `13/13`; the symmetric Gemini 3 Flash control scored `0.9595` / `13/13`. Terra is not production-eligible because its exact Onward runtime proof retained captions on two page-122 crops. See Attempt 029.
- **Current C4 deletion-gate score**: `single-model-crop-detection` is `0.9703` overall / `1.0` pass rate on that same maintained single-stage rerun, so the bounded deletion gate still passes. Use the same tracked proof note above as the portable summary; the raw promptfoo JSON remains a local regenerable artifact.
- **Maintained runtime note**: Stories 184 and 198 proved the reviewed Onward
  lane can delete the retired retry / refine / validate surface from both the
  maintained recipe and the shared runtime without regressing the published
  crop/build seam. The maintained recipe still keeps
  `rescue_caption_second_pass` plus `trim_layout_text`; removing them widened
  the certificate/seal crop on page 12 and duplicated nearby text in the final
  HTML. Story 231 added a strict, attributable OpenAI Responses crop route for
  `gpt-5.6-luna`, but a production-equivalent comparison rejected Luna as the
  maintained detector. The cover bypass was identical; Luna recovered all nine
  expected crops and was faster, while Gemini produced eight after combining
  the two page-12 signatures. However, Luna included printed captions in two
  page-122 crops that Gemini kept clean. Keep `gemini-3-flash-preview` in the
  maintained Onward recipe because C5 text exclusion is a hard gate; Luna
  remains the frozen-benchmark value winner and a callable challenger, not the
  production default. Story 232 later gave Terra the same exact-runtime check:
  it also recovered nine crops but retained printed captions below both
  page-122 portraits. Keep `gemini-3-flash-preview`; benchmark leadership does
  not waive the runtime text-exclusion gate.
- **Current dedicated C5-linked score**: `crop-validation` is `1.0` overall / `1.0` pass rate on the checked-in 40-crop corpus (Gemini 3.1 Flash Lite + `caption-focus`, measured 2026-04-11)
- **Current page-context C5 deletion-gate score**: `crop-page-level-deletion-gate` is `1.0` overall / `1.0` pass rate on the checked-in `22`-case overlap corpus with GPT-5.5 Responses + `page-context` promptfix, measured 2026-04-24 on the corrected golden. The previous Gemini 3.1 Flash Lite `22/22` result is stale after the `page-122-001` golden correction; the fresh Gemini rerun is `21/22`.
- **Provider-role boundary**: detector selection does not select the
  page-context validator. Keep that task pinned to
  `openai:responses:gpt-5.5`; Luna's `19/22` result is still disqualifying for
  this safety role.
- **Current C5 decision**: residue is still required. The page-context corpus still contains `5` explicit fail-labeled current-runtime cases (`page-018-000`, `page-092-000`, `page-122-000`, `page-122-001`, `page-126-000`), so `trim_layout_text` and bounded caption assist do not have an honest deletion proof yet.
- **Selection-validity status**: the existing hand-authored goldens are the
  authoritative bounded model-selection surface. Their prior use is a disclosed
  generalization limit, not a blocker that invents a second held-out corpus.
  Rank models on the complete goldens, and separately enforce every hard
  production/runtime gate before changing a default.
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

## Selection-validity workflow

1. Keep every source-backed label as authoritative truth; do not weaken a
   safety case because many models miss it.
2. Freeze prompts, adapters, schemas, reasoning settings, scorers, and goldens
   before a comparison, and give candidate and incumbent symmetric treatment.
3. Require unique, complete, attributable rows and fail closed on malformed,
   missing, extra, or duplicate evidence.
4. Name the best comparable score as the measured quality leader, even when it
   misses an absolute target.
5. Treat benchmark selection and production adoption as separate decisions.
   A runtime/default change still requires all transport, schema, privacy,
   cost, latency, and exact production-output safety gates.
6. Disclose that repeated use of the bounded goldens limits claims about unseen
   books. A future hand-curated book can broaden coverage, but it is not a
   prerequisite for decisions on the current authoritative set.

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
