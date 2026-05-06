# Chat-Latest Instant Bounded Challenger

Date: 2026-05-06
Repo HEAD at measurement: `60942e2`

## Trigger

OpenAI's 2026-05-05 GPT-5.5 Instant release says ChatGPT's default Instant
model moved to GPT-5.5 Instant and that the API alias is `chat-latest`:
<https://openai.com/index/gpt-5-5-instant/>. OpenAI's model docs also list
GPT-5.5 image input support, Responses API support, and `$5.00 / $30.00` per
1M input/output token pricing: <https://platform.openai.com/docs/models/gpt-5.5>.

The inbox constraint was deliberately narrow: only treat the alias as a
challenger if `chat-latest` is callable through the eval harness with image
inputs, then compare it against the current maintained winners before changing
any defaults.

## Harness Compatibility

Direct model discovery confirmed that `/v1/models` includes `chat-latest`.
Promptfoo 0.121.1 did not handle the bare alias cleanly through its built-in
OpenAI providers:

- `openai:chat:chat-latest` sent `max_tokens` and failed with
  `Unsupported parameter: 'max_tokens' is not supported with this model`.
- `openai:responses:chat-latest` reached Responses-style image inputs only
  after task-level prompt formatting, but still sent unsupported `temperature`.

Added `benchmarks/providers/openai_chat_latest_responses.py` as a narrow
promptfoo provider for alias challenger runs. It calls `/v1/responses` with
`model=chat-latest`, maps chat-style promptfoo image blocks to
`input_text` / `input_image`, and intentionally omits `temperature` and
`max_tokens`.

One-case image smoke passed through the shim:

```bash
cd benchmarks && DOC_WEB_OPENAI_API_KEY="$OPENAI_API_KEY" \
  ../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/image-crop-extraction.yaml \
  --providers "python:$(pwd)/providers/openai_chat_latest_responses.py" \
  --no-cache \
  --filter-prompts 'conservative-count' \
  --filter-first-n 1 \
  --no-write \
  -j 1
```

Result: `1/1`, `0` provider errors, proving the alias is image-callable for a
bounded challenger measurement. The measured full runs used temporary task
copies with the same provider substitution so the maintained provider lists did
not change; the commands below show the equivalent provider override.

## Crop Results

| Surface | Current maintained winner | `chat-latest` result | Decision |
| --- | ---: | ---: | --- |
| `image-crop-extraction` + `conservative-count` | Gemini 3 Flash: `0.9703`, `13/13`, about `$0.059` total | `0.8006`, `11/13`, about `$0.1389` total | Fails quality and cost despite lower latency |
| `crop-page-level-deletion-gate` | GPT-5.5 Responses: `1.0`, `22/22`, about `$1.3094` total | `0.9545`, `21/22`, about `$0.4136` total | Fails quality; keep current winner |

Detector command:

```bash
cd benchmarks && DOC_WEB_OPENAI_API_KEY="$OPENAI_API_KEY" \
  ../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/image-crop-extraction.yaml \
  --providers "python:$(pwd)/providers/openai_chat_latest_responses.py" \
  --no-cache \
  --filter-prompts 'conservative-count' \
  --output results/chat-latest-image-crop-extraction-20260506.json \
  -j 1
```

Detector metrics:

- Result: `benchmarks/results/chat-latest-image-crop-extraction-20260506.json`
- `11/13`, `0` provider errors
- Mean score: `0.8006`
- Prompt tokens: `22355`
- Completion tokens: `903`
- Total tokens: `23258`
- Average latency: `3610 ms`
- Estimated GPT-5.5-rate cost: about `$0.1389` total, `$0.0107` per case

Detector failures:

- `Image013`: bbox undercovered the Moise and Sophie L'Heureux portrait
  (`score=0.5526`, IoU `0.380`).
- `Image021`: bbox undercovered the Henry and Alma Alain anniversary photo
  (`score=0.5852`, IoU `0.413`).

Page-context command:

```bash
cd benchmarks && DOC_WEB_OPENAI_API_KEY="$OPENAI_API_KEY" \
  ../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/crop-page-level-deletion-gate.yaml \
  --providers "python:$(pwd)/providers/openai_chat_latest_responses.py" \
  --no-cache \
  --output results/chat-latest-crop-page-level-deletion-gate-20260506.json \
  -j 1
```

Page-context metrics:

- Result:
  `benchmarks/results/chat-latest-crop-page-level-deletion-gate-20260506.json`
- `21/22`, `0` provider errors
- Mean score: `0.9545`
- Prompt tokens: `76266`
- Completion tokens: `1075`
- Total tokens: `77341`
- Average latency: `5698 ms`
- Estimated GPT-5.5-rate cost: about `$0.4136` total, `$0.0188` per case

Page-context failure:

- `page-122-001`: false negative. The model returned `pass` and said the crop
  cleanly contains the two oval portraits, but the corrected golden fails this
  crop because it includes a visible slice of the neighboring Sophie L'Heureux
  portrait.

## Content-Hint Preview Check

The current cheap content-hint pass is a text-only Chat Completions call in
`doc_web/preview_content_hint.py`, defaulting to `gpt-4.1-nano` with a `0.75s`
preview budget. A direct callability comparison on representative rulebook
sample text used a relaxed `3.0s` timeout to avoid confusing API compatibility
with budget misses:

- `gpt-4.1-nano`: succeeded, `summary_ms=2106.117`, summary:
  `The Robo Rally rulebook details robot racing, programming, game phases, and victory conditions across 16 pages.`
- `chat-latest`: failed in the current content-hint path with
  `Unsupported parameter: 'max_tokens' is not supported with this model`; the
  preview code correctly fell back to deterministic summary output.

No content-hint default should change. Making `chat-latest` work there would
require a Responses-specific preview path, and there is no evidence it would
beat the cheap default on the preview pass's quality/latency/cost tradeoff.

## Decision

Do not alter maintained providers.

`chat-latest` is callable through a bounded Responses shim with image inputs,
but it does not beat the current maintained quality evidence on either crop
surface. It is also not callable through the current cheap content-hint
implementation without changing that implementation from Chat Completions to
Responses.
