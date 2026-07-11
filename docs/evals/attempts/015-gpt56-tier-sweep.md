# GPT-5.6 Tier Sweep

Date: 2026-07-11
Repo HEAD at measurement: `5efaa80`

## Trigger

The user asked to evaluate GPT-5.6 after release, including the multiple
intelligence tiers.

Official OpenAI references used for the API facts:

- Latest model guide: <https://developers.openai.com/api/docs/guides/latest-model.md>
- Pricing: <https://platform.openai.com/docs/pricing>

Current OpenAI docs list `gpt-5.6-sol` as the latest flagship model, state that
the `gpt-5.6` alias routes to `gpt-5.6-sol`, and expose three tiers:
`gpt-5.6-sol`, `gpt-5.6-terra`, and `gpt-5.6-luna`. The docs also list
reasoning efforts `none`, `low`, `medium`, `high`, `xhigh`, and `max`, plus
pro mode through `reasoning.mode = "pro"`.

The pricing page listed these standard short-context prices per 1M tokens at
evaluation time:

| Model | Input | Cached input | Cache write | Output |
| --- | ---: | ---: | ---: | ---: |
| `gpt-5.6-sol` | `$5.00` | `$0.50` | `$6.25` | `$30.00` |
| `gpt-5.6-terra` | `$2.50` | `$0.25` | `$3.125` | `$15.00` |
| `gpt-5.6-luna` | `$1.00` | `$0.10` | `$1.25` | `$6.00` |

Repo-local discovery confirmed the three OpenAI slugs are visible:

```bash
python scripts/discover-models.py --check-new
```

That command reported all provider keys configured and listed `gpt-5.6-sol`,
`gpt-5.6-terra`, and `gpt-5.6-luna` as new OpenAI models created
`2026-06-23`.

## Harness Compatibility

Promptfoo 0.121.1 could not be used through the built-in
`openai:responses:gpt-5.6-sol` provider for these image prompts. The smoke run
failed with a Responses API `400` because promptfoo sent chat-style content
items with `type: "text"` instead of Responses content items with
`type: "input_text"`.

I added `benchmarks/providers/openai_responses_model.py`, a narrow promptfoo
Python provider for challenger runs. It normalizes chat-style `text` and
`image_url` content into Responses `input_text` and `input_image` content, then
selects the model, reasoning effort, and pricing via environment variables.

Smoke checks through the shim passed:

- `benchmarks/results/gpt56-sol-smoke-image-crop-shim.json`: `1/1`, `0`
  provider errors
- `benchmarks/results/gpt56-sol-smoke-page-context-shim.json`: `1/1`, `0`
  provider errors

## Detector Results

Surface: `benchmarks/tasks/image-crop-extraction.yaml` with the maintained
`conservative-count` prompt and `OPENAI_RESPONSES_REASONING_EFFORT=none`.

| Model | Result | Mean score | Avg latency | Total estimated cost | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| Current maintained Gemini 3 Flash | `13/13` | `0.9703` | `7878 ms` | about `$0.059` | Current default |
| GPT-5.6 Sol | `13/13` | `0.9403` | `3223 ms` | `$0.2827` | Fails to beat current score |
| GPT-5.6 Terra | `13/13` | `0.9723` | `2641 ms` | `$0.1416` | Best GPT-5.6 detector challenger, but costlier |
| GPT-5.6 Luna | `13/13` | `0.9623` | `2187 ms` | `$0.0565` | Cheap and fast, but lower quality |

Representative command shape:

```bash
cd benchmarks && \
OPENAI_RESPONSES_MODEL=gpt-5.6-terra \
OPENAI_RESPONSES_REASONING_EFFORT=none \
OPENAI_RESPONSES_INPUT_PRICE_PER_1M=2.5 \
OPENAI_RESPONSES_OUTPUT_PRICE_PER_1M=15 \
../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/image-crop-extraction.yaml \
  --providers "python:$(pwd)/providers/openai_responses_model.py" \
  --filter-prompts 'conservative-count' \
  --output results/gpt56-terra-image-crop-extraction-20260711.json \
  --no-cache -j 1
```

Result artifacts:

- `benchmarks/results/gpt56-sol-image-crop-extraction-20260711.json`
- `benchmarks/results/gpt56-terra-image-crop-extraction-20260711.json`
- `benchmarks/results/gpt56-luna-image-crop-extraction-20260711.json`

Terra is a real detector challenger: it slightly improves the maintained mean
score (`0.9723` vs `0.9703`) and is faster in this pass. I did not switch the
maintained detector because the score gain is tiny and the total estimated cost
is more than 2x the maintained proof.

## Page-Context Results

Surface: `benchmarks/tasks/crop-page-level-deletion-gate.yaml`.

| Model / effort | Result | Score | Avg latency | Total estimated cost | Failed cases |
| --- | ---: | ---: | ---: | ---: | --- |
| Current maintained GPT-5.5 Responses | `22/22` | `1.0` | `5253 ms` | `$1.3094` | none |
| GPT-5.6 Sol / none | `18/22` | `0.8182` | `4743 ms` | `$1.4157` | `page-001-000`, `page-122-001`, `page-125-000`, `page-126-000` |
| GPT-5.6 Terra / none | `21/22` | `0.9545` | `3963 ms` | `$0.7077` | `page-122-001` |
| GPT-5.6 Luna / none | `19/22` | `0.8636` | `4225 ms` | `$0.2841` | `page-001-000`, `page-021-001`, `page-122-001` |
| GPT-5.6 Terra / low | `21/22` | `0.9545` | `4928 ms` | `$0.7256` | `page-126-000` |
| GPT-5.6 Terra / medium | `20/22` | `0.9091` | `4945 ms` | `$0.7343` | `page-125-000`, `page-126-000` |

The targeted Terra low-effort retry of the original `page-122-001` failure did
pass that single case:

- `benchmarks/results/gpt56-terra-low-crop-page-level-targeted-20260711.json`
- Result: `1/1`
- Total estimated cost: `$0.0518`

The full low-effort run regressed to a different hard miss (`page-126-000`),
and the full medium-effort run regressed further. No higher-effort full rerun is
warranted because the maintained GPT-5.5 Responses gate is already `22/22` and
the GPT-5.6 runs were not monotonic with effort.

Page-context result artifacts:

- `benchmarks/results/gpt56-sol-crop-page-level-deletion-gate-20260711.json`
- `benchmarks/results/gpt56-terra-crop-page-level-deletion-gate-20260711.json`
- `benchmarks/results/gpt56-luna-crop-page-level-deletion-gate-20260711.json`
- `benchmarks/results/gpt56-terra-low-crop-page-level-deletion-gate-20260711.json`
- `benchmarks/results/gpt56-terra-medium-crop-page-level-deletion-gate-20260711.json`

## Failure Classification

I decoded the failed source/crop images and manually inspected the contact
sheet:

- `/tmp/doc-web-gpt56-inspect/failure-contact-sheet.jpg`

Manual classification:

- `page-001-000`: clean cover landscape crop. Sol and Luna over-rejected it as
  incomplete or text-contaminated. Model-wrong false positive.
- `page-021-001`: clean ranch photo with sky and light background inside the
  photograph. Luna over-rejected it as excessive blank background. Model-wrong
  false positive.
- `page-122-001`: crop includes the Moise/Edward double portrait plus visible
  neighboring Sophie portrait area. The checked-in fail label is sound. Models
  passing it are model-wrong false negatives.
- `page-125-000`: clean covered wagon sketch crop. Sol and Terra medium
  over-rejected it as incomplete. Model-wrong false positive.
- `page-126-000`: crop includes adjacent plaque/page text along the left/top
  edge. The checked-in fail label is sound. Models passing it are model-wrong
  false negatives.

No prompt, scorer, or golden change is justified from this run.

## Decision

Do not alter maintained providers.

GPT-5.6 Terra is a credible detector challenger, but not enough to justify
replacing the maintained Gemini 3 Flash detector by default. It slightly wins on
score and latency, but costs more than 2x the current maintained proof.

Do not replace the page-context validator. GPT-5.6 Terra is cheaper and faster
than the maintained GPT-5.5 Responses gate, but it fails the hard `22/22`
quality contract. The stronger Sol tier is worse on this task, and additional
Terra reasoning effort was not reliably better.

No maintained providers, prompts, scorers, or goldens should change.
