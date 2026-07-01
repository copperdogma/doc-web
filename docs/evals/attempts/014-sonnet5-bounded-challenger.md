# Claude Sonnet 5 Bounded Challenger

Date: 2026-06-30
Repo HEAD at measurement: `fb2d00b`

## Trigger

The user asked to evaluate Anthropic's new Sonnet 5 model and recommend whether
doc-forge should use it.

Current model discovery confirmed `claude-sonnet-5` is live in the repo-local
Anthropic account:

```bash
python scripts/discover-models.py --check-new
```

That command found all three repo-scoped provider keys, listed
`claude-sonnet-5` as `Claude Sonnet 5`, and reported it as a new Anthropic
mid-tier model created `2026-06-29`.

Official Anthropic references used for the API facts:

- Models overview: <https://docs.anthropic.com/en/docs/about-claude/models/overview>
- What's new in Claude Sonnet 5: <https://docs.anthropic.com/en/docs/about-claude/models/whats-new-sonnet-5>
- Pricing: <https://docs.anthropic.com/en/docs/about-claude/pricing>

API facts relevant to this eval: model id `claude-sonnet-5`, 1M context,
adaptive thinking support, and introductory pricing of `$2/M` input tokens and
`$10/M` output tokens through 2026-08-31. OpenRouter was not used because the
direct Anthropic credential and Messages path worked.

## Harness Compatibility

The repo-local Anthropic credential is present.

I reused the direct Anthropic/no-sampling promptfoo provider created for Opus
4.8 because promptfoo's built-in Anthropic provider is not the trusted path for
these newer Anthropic models in this repo. The provider was configured with:

- `ANTHROPIC_OPUS48_MODEL=claude-sonnet-5`
- `ANTHROPIC_MESSAGES_INPUT_PRICE_PER_1M=2`
- `ANTHROPIC_MESSAGES_OUTPUT_PRICE_PER_1M=10`

Both full eval runs completed with `0` provider errors, so this is a quality
decision rather than an access-path blocker.

## Crop Results

| Surface | Current maintained winner | Sonnet 5 high-effort result | Decision |
| --- | ---: | ---: | --- |
| `image-crop-extraction` + `conservative-count` | Gemini 3 Flash: `0.9703`, `13/13`, about `$0.059` total | `0.5334`, `5/13`, about `$0.1279` total | Fails quality and costs more |
| `crop-page-level-deletion-gate` | GPT-5.5 Responses: `1.0`, `22/22`, about `$1.3094` total | `0.9091`, `20/22`, about `$0.4126` total | Cheaper and faster, but fails the hard quality gate |

Detector command:

```bash
cd benchmarks && \
ANTHROPIC_OPUS48_MODEL=claude-sonnet-5 \
ANTHROPIC_MESSAGES_INPUT_PRICE_PER_1M=2 \
ANTHROPIC_MESSAGES_OUTPUT_PRICE_PER_1M=10 \
../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/image-crop-extraction.yaml \
  --providers python:$(pwd)/providers/anthropic_opus48_messages.py \
  --filter-prompts 'conservative-count' \
  --output results/sonnet5-image-crop-extraction-20260630.json \
  --no-cache -j 1
```

Detector metrics:

- Result: `benchmarks/results/sonnet5-image-crop-extraction-20260630.json`
- `5/13`, `0` provider errors
- Mean score: `0.5334`
- Prompt tokens: `56874`
- Completion tokens: `1416`
- Total estimated Sonnet 5 cost: about `$0.1279`
- Average latency: `3834 ms`
- Failures: `Image001`, `Image003`, `Image011`, `Image013`, `Image021`,
  `Image037`, `Image124`, and `Image126`

Page-context command:

```bash
cd benchmarks && \
ANTHROPIC_OPUS48_MODEL=claude-sonnet-5 \
ANTHROPIC_MESSAGES_INPUT_PRICE_PER_1M=2 \
ANTHROPIC_MESSAGES_OUTPUT_PRICE_PER_1M=10 \
../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/crop-page-level-deletion-gate.yaml \
  --providers python:$(pwd)/providers/anthropic_opus48_messages.py \
  --output results/sonnet5-crop-page-level-deletion-gate-20260630.json \
  --no-cache -j 1
```

Page-context metrics:

- Result:
  `benchmarks/results/sonnet5-crop-page-level-deletion-gate-20260630.json`
- `20/22`, `0` provider errors
- Mean score: `0.9091`
- Prompt tokens: `197513`
- Completion tokens: `1757`
- Total estimated Sonnet 5 cost: about `$0.4126`
- Average latency: `3827 ms`
- Failures:
  - `page-122-000`: false negative; Sonnet passed the crop even though it
    includes printed caption text below the family reunion photo.
  - `page-122-001`: false negative; Sonnet passed the crop even though it spans
    two separate oval portrait images and therefore leaks a neighboring portrait.

## Effort Retry

I reran only the two failed page-context cases with `ANTHROPIC_OPUS48_EFFORT=xhigh`.

Command:

```bash
cd benchmarks && \
ANTHROPIC_OPUS48_MODEL=claude-sonnet-5 \
ANTHROPIC_OPUS48_EFFORT=xhigh \
ANTHROPIC_MESSAGES_INPUT_PRICE_PER_1M=2 \
ANTHROPIC_MESSAGES_OUTPUT_PRICE_PER_1M=10 \
../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/crop-page-level-deletion-gate.yaml \
  --providers python:$(pwd)/providers/anthropic_opus48_messages.py \
  --filter-failing-only results/sonnet5-crop-page-level-deletion-gate-20260630.json \
  --output results/sonnet5-crop-page-level-deletion-gate-xhigh-failures-20260630.json \
  --no-cache -j 1
```

Result:

- `1/2` repaired
- `page-122-000` changed to the correct `fail`
- `page-122-001` remained a false negative
- Total estimated failed-subset cost: about `$0.0441`
- Average failed-subset latency: `6577 ms`

Because the failed-case retry still missed `page-122-001`, no full xhigh rerun
is warranted.

## Failure Classification

The failures are model-wrong, not scorer-wrong or golden-wrong.

Manual image inspection:

- `benchmarks/input/source-pages-b64/Image013.b64.txt`: the source page has one
  lower-left portrait image. Sonnet found the right semantic object but emitted
  a bad box (`[148, 836, 740, 1394]`) that does not overlap the normalized
  golden box, which is a coordinate/box-quality failure.
- `benchmarks/input/source-pages-b64/Image121.b64.txt` and
  `benchmarks/input/crop-validation-b64/page-122-000.b64.txt`: the crop includes
  printed caption text below the family reunion photo, matching the checked-in
  fail label.
- `benchmarks/input/source-pages-b64/Image121.b64.txt` and
  `benchmarks/input/crop-validation-b64/page-122-001.b64.txt`: the crop spans
  the Moise/Edward double portrait plus the neighboring Sophie L'Heureux
  portrait area, matching the checked-in fail label.

No prompt, scorer, or golden change is justified from this run.

## Decision

Do not alter maintained providers.

Sonnet 5 is callable through the repo-local Anthropic key and is materially
cheaper than Fable 5. It is also faster and cheaper than the current GPT-5.5
Responses page-context winner in this run. But it does not meet the quality bar
on either maintained doc-web crop surface:

- Detector quality is far below the Gemini 3 Flash winner (`0.5334` vs
  `0.9703`).
- Page-context validation misses the required `22/22` contract at high effort.
- `xhigh` effort still misses the neighboring-portrait residue case.

No maintained providers, prompts, scorers, or goldens should change.
