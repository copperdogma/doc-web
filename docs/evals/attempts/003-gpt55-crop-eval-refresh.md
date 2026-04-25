# GPT-5.5 Crop Eval Refresh

Date: 2026-04-24
Repo HEAD at measurement: `aa5b577`

## Trigger

`gpt-5.5` appeared in the local OpenAI model list on 2026-04-24, satisfying the
`new-subject-model` retry condition for the maintained crop evals.

Confirmed callable model IDs from `https://api.openai.com/v1/models` included
`gpt-5.5` and `gpt-5.5-2026-04-23`. `gpt-5.5` works through the current
promptfoo OpenAI chat provider. A short-lived `gpt-5.5-pro` provider row was
tested and removed because the chat endpoint returned 404 "not a chat model".

## Commands

```bash
cd benchmarks && promptfoo eval -c tasks/image-crop-extraction.yaml \
  --no-cache --filter-providers 'openai:chat:gpt-5.5' \
  --filter-prompts 'conservative-count' \
  --output results/gpt55-image-crop-extraction-20260424.json -j 1

cd benchmarks && promptfoo eval -c tasks/crop-validation.yaml \
  --no-cache --filter-providers 'openai:chat:gpt-5.5' \
  --filter-prompts 'caption-focus' \
  --output results/gpt55-crop-validation-20260424.json -j 1

cd benchmarks && promptfoo eval -c tasks/crop-page-level-deletion-gate.yaml \
  --no-cache --filter-providers 'openai:chat:gpt-5.5' \
  --output results/gpt55-crop-page-level-deletion-gate-20260424.json -j 1
```

Promptfoo version warning during the run: installed `0.121.1`, latest available
reported by promptfoo as `0.121.7`.

## Results

| Surface | Incumbent | GPT-5.5 Result | Verdict |
| --- | --- | --- | --- |
| `image-crop-extraction` | Gemini 3 Flash, `0.9703` overall / `1.0` pass rate | `0.8111` overall / `0.7692` pass rate (`10/13`) | Fails detector replacement |
| `crop-validation` | Gemini 3.1 Flash Lite, `1.0` overall / `1.0` pass rate | `0.975` overall / `0.975` pass rate (`39/40`) | Close, but misses target |
| `crop-page-level-deletion-gate` | Gemini 3.1 Flash Lite, `1.0` overall / `1.0` pass rate | `0.7273` overall / `0.7273` pass rate (`16/22`) | Fails page-context C5 gate |

Current GPT-5.5 API cost estimates from token counts, using `$5/$30` per 1M
input/output tokens:

- `image-crop-extraction`: `$0.4080` total (`$0.0314` per case)
- `crop-validation`: `$1.3258` total (`$0.0331` per case)
- `crop-page-level-deletion-gate`: `$1.3984` total (`$0.0636` per case)

## Failure Classification

Detector failures:

- `Image001`: model-wrong bbox precision. GPT-5.5 cropped only the stylized
  title region instead of matching the maintained title/title-caption golden
  contract.
- `Image013`: model-wrong bbox precision. The portrait was undercovered.
- `Image020`: model-wrong bbox precision. The second ranch photo was
  undercovered.

Crop-only validation failure:

- `page-126-000`: model-wrong false negative. GPT-5.5 returned `pass` because it
  treated all visible text as plaque text inside the photo, but manual
  inspection confirmed external page text is visible along the crop's left
  edge.

Page-context deletion-gate failures:

- False positives on `page-004-000`, `page-012-001`, `page-021-000`,
  `page-021-001`, and `page-122-001`: GPT-5.5 over-rejected golden pass crops as
  incomplete or neighboring-visual leakage.
- False negative on `page-126-000`: same external-text miss as the crop-only
  surface.

No scorer or golden changes were made.

## Decision

Keep the current Gemini crop choices. GPT-5.5 should remain available in the
benchmark configs for future sweeps, but it is not a current replacement for
the maintained crop detector, crop-only validator, or page-context C5 deletion
gate.
