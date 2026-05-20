# Kimi K2.6 Bounded Challenger

Date: 2026-05-20
Repo HEAD at measurement: `37ef4af`

## Trigger

Conductor Scout 038 flagged Kimi K2.6 as a plausible direct Moonshot
challenger for doc-web's maintained VLM/document evals. The inbox constraint was
narrow: use Moonshot's direct API with `kimi-k2.6`, compare against the current
OpenAI/Gemini winners on quality, latency, and cost, and do not alter defaults
unless eval evidence wins.

Official Kimi docs confirm the required harness assumptions:

- `kimi-k2.6` supports text and image input with a 256K context window.
- Moonshot exposes an OpenAI-compatible chat-completions endpoint at
  `https://api.moonshot.ai/v1/chat/completions`.
- K2.6 supports both thinking and non-thinking modes; thinking can be disabled
  with `{"thinking": {"type": "disabled"}}`.
- K2.6 supports JSON mode and automatic context caching.

## Harness Compatibility

Added `benchmarks/providers/moonshot_kimi_chat.py` as a narrow promptfoo
provider for direct Moonshot challenger runs. It calls Moonshot's first-party
Chat Completions endpoint, preserves the checked-in OpenAI-style image data-URI
prompt shape, requests JSON mode, and defaults to non-thinking mode for the
full comparable runs. `doc_web/env.py` now maps `DOC_WEB_MOONSHOT_API_KEY` to
`MOONSHOT_API_KEY`, and `DOC_WEB_ENV_FILE` can point a detached worktree at the
main checkout's local `.env` without copying secrets.

One-case smokes passed for both one-image and two-image prompt shapes:

```bash
cd benchmarks && DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/doc-web/.env \
  ../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/image-crop-extraction.yaml \
  --providers "python:$(pwd)/providers/moonshot_kimi_chat.py" \
  --filter-prompts 'conservative-count' \
  --filter-first-n 1 \
  --no-cache --no-write -j 1
```

Result: `1/1`, `0` provider errors.

```bash
cd benchmarks && DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/doc-web/.env \
  ../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/crop-page-level-deletion-gate.yaml \
  --providers "python:$(pwd)/providers/moonshot_kimi_chat.py" \
  --filter-first-n 1 \
  --no-cache --no-write -j 1
```

Result: `1/1`, `0` provider errors.

## Crop Results

| Surface | Current maintained winner | Kimi K2.6 result | Decision |
| --- | ---: | ---: | --- |
| `image-crop-extraction` + `conservative-count` | Gemini 3 Flash: `0.9703`, `13/13`, about `$0.059` total | `0.8981`, `12/13`, about `$0.0519` total | Fails quality despite similar cost |
| `crop-page-level-deletion-gate` | GPT-5.5 Responses: `1.0`, `22/22`, about `$1.3094` total | `0.9545`, `21/22`, about `$0.1646` total | Cheaper, but fails required quality |

Detector command:

```bash
cd benchmarks && DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/doc-web/.env \
  ../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/image-crop-extraction.yaml \
  --providers "python:$(pwd)/providers/moonshot_kimi_chat.py" \
  --filter-prompts 'conservative-count' \
  --output results/kimi-k26-image-crop-extraction-20260520.json \
  --no-cache -j 1
```

Detector metrics:

- Result: `benchmarks/results/kimi-k26-image-crop-extraction-20260520.json`
- `12/13`, `0` provider errors
- Mean score: `0.8981`
- Prompt tokens: `55288`
- Completion tokens: `1066`
- Cached tokens: `6163`
- Total tokens: `56354`
- Average latency: `6176 ms`
- Estimated Kimi K2.6 cost: about `$0.0519` total, `$0.0040` per case

Detector failure:

- `Image001`: model-wrong false negative. The page is a stylized title page
  whose title text is intentionally counted as standalone artwork by the
  maintained detector prompt/golden, but Kimi returned `{"images": []}`.

Page-context command:

```bash
cd benchmarks && DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/doc-web/.env \
  ../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/crop-page-level-deletion-gate.yaml \
  --providers "python:$(pwd)/providers/moonshot_kimi_chat.py" \
  --output results/kimi-k26-crop-page-level-deletion-gate-20260520.json \
  --no-cache -j 1
```

Page-context metrics:

- Result:
  `benchmarks/results/kimi-k26-crop-page-level-deletion-gate-20260520.json`
- `21/22`, `0` provider errors
- Mean score: `0.9545`
- Prompt tokens: `185354`
- Completion tokens: `2109`
- Cached tokens: `25166`
- Total tokens: `187463`
- Average latency: `9868 ms`
- Estimated Kimi K2.6 cost: about `$0.1646` total, `$0.0075` per case

Page-context failure:

- `page-122-001`: model-wrong false negative. Kimi returned `pass` and said
  the crop contains only the oval portraits, but manual source/crop inspection
  confirmed the corrected golden: the crop visibly includes a slice of the
  neighboring Sophie L'Heureux portrait at the right edge.

## Thinking-Mode Check

The only failed case from each full run was rerun with `MOONSHOT_KIMI_THINKING=enabled`:

```bash
cd benchmarks && DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/doc-web/.env \
  MOONSHOT_KIMI_THINKING=enabled \
  ../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/image-crop-extraction.yaml \
  --providers "python:$(pwd)/providers/moonshot_kimi_chat.py" \
  --filter-prompts 'conservative-count' \
  --filter-failing results/kimi-k26-image-crop-extraction-20260520.json \
  --output results/kimi-k26-image-crop-extraction-thinking-failures-20260520.json \
  --no-cache -j 1
```

Result: `Image001` still failed with `{"images": []}`.

```bash
cd benchmarks && DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/doc-web/.env \
  MOONSHOT_KIMI_THINKING=enabled \
  ../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/crop-page-level-deletion-gate.yaml \
  --providers "python:$(pwd)/providers/moonshot_kimi_chat.py" \
  --filter-failing results/kimi-k26-crop-page-level-deletion-gate-20260520.json \
  --output results/kimi-k26-crop-page-level-deletion-gate-thinking-failures-20260520.json \
  --no-cache -j 1
```

Result: `page-122-001` still failed as `pass`.

## Decision

Do not alter maintained providers.

Kimi K2.6 is directly callable, inexpensive, JSON-capable, and compatible with
the repo's checked-in multimodal promptfoo fixtures. It is not currently useful
as a maintained replacement for either crop surface because it misses the same
kind of critical edge case that these gates exist to catch. The page-context
result is cost-interesting but still fails the `1.0` deletion-gate requirement.
