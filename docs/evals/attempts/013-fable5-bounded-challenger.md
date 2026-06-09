# Claude Fable 5 Bounded Challenger

Date: 2026-06-09
Repo HEAD at measurement: `70a65b5`

## Trigger

The inbox noted Conductor Scout 044's claim that Anthropic's `claude-fable-5`
is a very expensive ceiling-model candidate for tiny hard-document/OCR slices,
not a maintained OCR or crop-default candidate.

Official Anthropic sources confirmed the model is real and current at release:

- Release announcement: <https://www.anthropic.com/news/claude-fable-5-mythos-5>
- Models overview: <https://docs.anthropic.com/en/docs/about-claude/models/overview>
- Pricing: <https://docs.anthropic.com/en/docs/about-claude/pricing>

API facts relevant to this eval: model id `claude-fable-5`, general Claude API
availability, 1M context, always-on adaptive thinking, and standard pricing of
`$10/M` input and `$50/M` output tokens. A live `/v1/models` check through the
repo-local Anthropic key returned both `claude-fable-5` and `claude-opus-4-8`.

## Harness Compatibility

The repo-local Anthropic credential is present.

I reused the direct Anthropic/no-sampling promptfoo provider created for Opus
4.8, because promptfoo's built-in Anthropic provider is still not the trusted
surface for these frontier models in this repo. The provider now accepts
environment-provided token prices so challenger result artifacts can record
the correct model-specific cost instead of hard-coding Opus 4.8 pricing.

A one-case page-context smoke passed with `0` provider errors before the full
run.

## Page-Context Crop Result

| Surface | Current maintained winner | Fable 5 high-effort result | Decision |
| --- | ---: | ---: | --- |
| `crop-page-level-deletion-gate` | GPT-5.5 Responses: `1.0`, `22/22`, about `$1.3094` total | `0.9091`, `20/22`, about `$2.1137` total | Fails quality, costs more, and is slower |

Command:

```bash
cd benchmarks && \
ANTHROPIC_OPUS48_MODEL=claude-fable-5 \
ANTHROPIC_MESSAGES_INPUT_PRICE_PER_1M=10 \
ANTHROPIC_MESSAGES_OUTPUT_PRICE_PER_1M=50 \
../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/crop-page-level-deletion-gate.yaml \
  --providers python:$(pwd)/providers/anthropic_opus48_messages.py \
  --output results/fable5-crop-page-level-deletion-gate-20260609.json \
  --no-cache -j 1
```

Metrics:

- Result: `benchmarks/results/fable5-crop-page-level-deletion-gate-20260609.json`
- `20/22`, `0` provider errors
- Mean score: `0.9091`
- Prompt tokens: `197513`
- Completion tokens: `2771`
- Total estimated Fable 5 cost: about `$2.1137`
- Average latency: `7423 ms`
- Failures:
  - `page-122-001`: false negative; Fable passed the crop even though it leaks
    the neighboring Sophie L'Heureux portrait.
  - `page-126-000`: false negative; Fable passed the crop even though visible
    adjacent page/plaque text appears at the left edge.

## Failure Classification

The two failures are model-wrong, not scorer-wrong or golden-wrong.

Manual image inspection:

- `benchmarks/input/source-pages-b64/Image121.b64.txt` and
  `benchmarks/input/crop-validation-b64/page-122-001.b64.txt`: the crop
  includes both the Moise/Edward double portrait and the neighboring Sophie
  L'Heureux portrait area, matching the corrected fail label.
- `benchmarks/input/source-pages-b64/Image125.b64.txt` and
  `benchmarks/input/crop-validation-b64/page-126-000.b64.txt`: the crop includes
  visible text from the adjacent plaque/page area along the left edge, matching
  the fail label.

These are the same hard residue cases Opus 4.8 missed. No prompt, scorer, or
golden change is justified from this run.

## Decision

Do not alter maintained providers.

Fable 5 is callable through the repo-local Anthropic key and the existing
direct Messages provider pattern, but it is not a replacement for the
maintained `openai:responses:gpt-5.5` page-context deletion gate:

- It fails the required `22/22` quality contract.
- It repeats the same two false negatives as Opus 4.8.
- It costs more than the current GPT-5.5 Responses winner.
- It is slower than the current GPT-5.5 Responses winner on this surface.

No higher-effort retry is warranted: even a repaired quality score would not
clear the inbox guardrail that quality, latency, and cost must all win.
