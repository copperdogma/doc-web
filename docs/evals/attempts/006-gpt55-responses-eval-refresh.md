# GPT-5.5 Responses Eval Refresh

Date: 2026-04-24
Repo HEAD at measurement: `aa5b577`

## Trigger

Live API verification showed `gpt-5.5-pro` is now callable through the OpenAI
Responses API, while it is still not a Chat Completions model. The previous
GPT-5.5 promptfoo runs used `openai:chat:gpt-5.5`, so this pass added a
Responses-compatible image message path and reran the surfaces where the Chat
interface could plausibly have affected output.

## Implementation

Updated the shared prompt helpers so `openai:responses:*` providers emit
Responses API content blocks:

- text: `input_text`
- images: `input_image`

Added provider rows for:

- `openai:responses:gpt-5.5` with `reasoning_effort: none`
- `openai:responses:gpt-5.5-pro` with `reasoning_effort: medium`

## Crop Results

| Surface | Model | Result | Prior GPT-5.5 Chat | Verdict |
| --- | --- | ---: | ---: | --- |
| `image-crop-extraction` | GPT-5.5 Responses | `0.791`, `10/13` | `0.8111`, `10/13` | still fails |
| `image-crop-extraction` | GPT-5.5 Pro Responses | one-case smoke passed; full detector did not complete interactively | n/a | not promptfoo-practical yet |
| `crop-validation` | GPT-5.5 Responses | `39/40` | `39/40` | still misses `page-126-000` |
| `crop-validation` | GPT-5.5 Pro Responses | `39/40` | n/a | same miss, slower/costlier |
| `crop-page-level-deletion-gate` | GPT-5.5 Responses | `20/22` | `16/22` | improved, still fails |
| `crop-page-level-deletion-gate` | GPT-5.5 Pro Responses | `15/22` | n/a | worse than base Responses |

## Failure Classification

GPT-5.5 Responses detector failures:

- `Image001`, `Image021`, `Image059`: model-wrong bbox precision failures.
  The Responses path changed the failure set versus Chat but did not improve
  the pass rate.

GPT-5.5 / Pro crop-only validation failure:

- `page-126-000`: model-wrong false negative. Both models passed a crop with
  external page/neighboring-plaque text at the crop edge.

GPT-5.5 Responses page-context failures:

- `page-021-001`: model-wrong false positive. GPT-5.5 Responses over-rejected
  the ranch image as too blank even though the pale sky/snow/photo background is
  image content.
- `page-122-001`: initially reported as a false positive against the then-current
  golden, later reclassified in
  `docs/evals/attempts/007-gpt55-page-context-prompt-repair.md` as a
  page-context golden error because the crop includes a neighboring portrait
  slice.

GPT-5.5 Pro Responses page-context failures:

- False positives on `page-004-000`, `page-012-001`, `page-021-001`, and
  `page-122-001`.
- Empty / unparsable outputs on `page-021-000`, `page-125-000`, and
  `page-126-000`.

No scorer or golden changes were made in this attempt.

## Non-Crop Check

The suspicious three-page Onward single-page OCR screen was rerun through
Responses for both GPT-5.5 and GPT-5.5 Pro:

- Result file: `benchmarks/results/gpt55-responses-onward-single-page-screen-20260424.json`
- GPT-5.5 Responses: `0/3`
- GPT-5.5 Pro Responses: `0/3`

Both still failed with `Output has no tables`, so the earlier single-page
failure was not solely a Chat Completions interface artifact.

## Commands

```bash
cd benchmarks && promptfoo eval -c tasks/image-crop-extraction.yaml \
  --no-cache --filter-providers '^openai:responses:gpt-5\.5$' \
  --filter-prompts 'conservative-count' \
  --output results/gpt55-responses-image-crop-extraction-gpt55-20260424.json -j 1

cd benchmarks && promptfoo eval -c tasks/crop-validation.yaml \
  --no-cache --filter-providers '^openai:responses:gpt-5\.5$' \
  --filter-prompts 'caption-focus' \
  --output results/gpt55-responses-crop-validation-20260424.json -j 1

cd benchmarks && PROMPTFOO_EVAL_TIMEOUT_MS=180000 promptfoo eval \
  -c tasks/crop-validation.yaml --no-cache \
  --filter-providers '^openai:responses:gpt-5\.5-pro$' \
  --filter-prompts 'caption-focus' \
  --output results/gpt55pro-responses-crop-validation-20260424.json -j 1

cd benchmarks && promptfoo eval -c tasks/crop-page-level-deletion-gate.yaml \
  --no-cache --filter-providers '^openai:responses:gpt-5\.5$' \
  --output results/gpt55-responses-crop-page-level-deletion-gate-20260424.json -j 1

cd benchmarks && PROMPTFOO_EVAL_TIMEOUT_MS=180000 promptfoo eval \
  -c tasks/crop-page-level-deletion-gate.yaml --no-cache \
  --filter-providers '^openai:responses:gpt-5\.5-pro$' \
  --output results/gpt55pro-responses-crop-page-level-deletion-gate-20260424.json -j 1

cd benchmarks && promptfoo eval -c tasks/onward-single-page-gpt54-screen.yaml \
  --no-cache \
  --filter-providers '^openai:responses:gpt-5\.5$|^openai:responses:gpt-5\.5-pro$' \
  --output results/gpt55-responses-onward-single-page-screen-20260424.json -j 1
```

## Decision

Keep GPT-5.5 and GPT-5.5 Pro Responses available in the benchmark configs, but
do not switch any maintained crop or Onward OCR choice to them. GPT-5.5
Responses was materially better than GPT-5.5 Chat on the page-context deletion
gate, but still missed the then-current gate. A follow-up prompt/golden repair
is recorded in `docs/evals/attempts/007-gpt55-page-context-prompt-repair.md`.
GPT-5.5 Pro is slower, costlier, and worse on the measured crop validation
surfaces.
