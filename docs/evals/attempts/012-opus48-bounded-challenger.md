# Claude Opus 4.8 Bounded Challenger

Date: 2026-05-28
Repo HEAD at measurement: `5254df1`

## Trigger

The inbox noted Conductor Scout 043's claim that Anthropic's
`claude-opus-4-8` is a plausible doc-web challenger for page-context
extraction, crop/OCR judgment, and stronger-OCR blocked lines.

Official Anthropic sources confirmed the model is real and current at release:

- Release announcement: <https://www.anthropic.com/news/claude-opus-4-8>
- Opus 4.8 API notes:
  <https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-8>
- Models overview:
  <https://platform.claude.com/docs/en/about-claude/models/overview>

API facts relevant to this eval: model id `claude-opus-4-8`, regular pricing
`$5/M` input and `$25/M` output, 1M context on the Claude API, adaptive
thinking support, and inherited Opus 4.7 sampling constraints.

## Harness Compatibility

The repo-local Anthropic credential is present.

The built-in promptfoo Anthropic provider is not usable for Opus 4.8 in the
repo's pinned promptfoo `0.121.1`: the one-case detector smoke failed with:

```text
400 {"type":"error","error":{"type":"invalid_request_error","message":"`temperature` is deprecated for this model."}}
```

I added `benchmarks/providers/anthropic_opus48_messages.py` as a narrow
promptfoo provider for this challenger. It calls Anthropic Messages directly,
converts the repo's existing OpenAI-style image blocks to Anthropic image
content, omits sampling parameters, enables adaptive thinking, and uses
`output_config.effort = high` by default. The one-case detector and page-context
smokes both passed with `0` provider errors.

I also updated `modules/common/anthropic_client.py` so direct OCR module calls
to `claude-opus-4-8` omit `temperature` and use adaptive thinking/high effort.
Focused test coverage:

```bash
python -m pytest tests/test_anthropic_client.py -q
```

Result: `2 passed`.

## Crop Results

| Surface | Current maintained winner | Opus 4.8 high-effort result | Decision |
| --- | ---: | ---: | --- |
| `image-crop-extraction` + `conservative-count` | Gemini 3 Flash: `0.9703`, `13/13`, about `$0.059` total | `0.7669`, `10/13`, about `$0.3215` total | Fails quality and costs more |
| `crop-page-level-deletion-gate` | GPT-5.5 Responses: `1.0`, `22/22`, about `$1.3094` total | `0.9091`, `20/22`, about `$1.0405` total | Fails the hard deletion gate |

Detector command:

```bash
cd benchmarks && ../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/image-crop-extraction.yaml \
  --providers python:$(pwd)/providers/anthropic_opus48_messages.py \
  --filter-prompts 'conservative-count' \
  --output results/opus48-image-crop-extraction-20260528.json \
  --no-cache -j 1
```

Detector metrics:

- Result: `benchmarks/results/opus48-image-crop-extraction-20260528.json`
- `10/13`, `0` provider errors
- Mean score: `0.7669`
- Prompt tokens: `56874`
- Completion tokens: `1485`
- Total estimated Opus 4.8 cost: about `$0.3215`
- Average latency: `4291 ms`
- Failures: `Image021`, `Image037`, `Image059`

Page-context command:

```bash
cd benchmarks && ../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/crop-page-level-deletion-gate.yaml \
  --providers python:$(pwd)/providers/anthropic_opus48_messages.py \
  --output results/opus48-crop-page-level-deletion-gate-20260528.json \
  --no-cache -j 1
```

Page-context metrics:

- Result:
  `benchmarks/results/opus48-crop-page-level-deletion-gate-20260528.json`
- `20/22`, `0` provider errors
- Mean score: `0.9091`
- Prompt tokens: `197513`
- Completion tokens: `2119`
- Total estimated Opus 4.8 cost: about `$1.0405`
- Average latency: `4853 ms`
- Failures:
  - `page-122-001`: false negative; passed the crop even though the corrected
    golden fails it for a neighboring portrait slice.
  - `page-126-000`: false negative; passed the crop even though the corrected
    golden fails it for visible book-page text at the left edge.

## Effort Retry

I reran only the failed cases with `ANTHROPIC_OPUS48_EFFORT=xhigh`.

Detector failed-case retry:

- Result:
  `benchmarks/results/opus48-image-crop-extraction-xhigh-failures-20260528.json`
- `0/3` repaired
- Mean score across the failed subset: `0.6449`
- Total estimated cost: about `$0.0755`

Page-context failed-case retry:

- Result:
  `benchmarks/results/opus48-crop-page-level-deletion-gate-xhigh-failures-20260528.json`
- `0/2` repaired
- Total estimated cost: about `$0.1173`

Higher effort did not change the promotion decision.

## Handwritten OCR Screen

I ran a bounded image-entry screen on the corrected real Barney and Alverson
fixtures using the same OCR prompt family and `claude-opus-4-8` through
`ocr_ai_gpt51_v1`.

Commands used the existing image manifests and direct OCR module path:

```bash
env PYTHONPATH=. INSTRUMENT_SINK=output/runs/eval-barney-image-opus-4-8/instrumentation_calls.jsonl \
  RUN_ID=eval-barney-image-opus-4-8 \
  scripts/run_with_doc_web_env.py python modules/extract/ocr_ai_gpt51_v1/main.py \
  --pages output/runs/eval-barney-image-opus-4-8/01_images_dir_to_manifest_v1/pages_images_manifest.jsonl \
  --outdir output/runs/eval-barney-image-opus-4-8/02_ocr_ai_gpt51_v1 \
  --out pages_html.jsonl --model claude-opus-4-8 --max-long-side 2048 \
  --concurrency 1 --skip-blank-pages \
  --ocr-hints 'This page is handwritten historical correspondence or diary-style prose. Preserve wording exactly as written, including misspellings, grammar, and punctuation. Do not normalize names into more common spellings. If a word is uncertain, prefer the most literal plausible reading over an invented confident substitution. Use plain paragraph HTML unless stronger structure is explicitly visible.' \
  --force --run-id eval-barney-image-opus-4-8
```

The Alverson command was the same shape under
`output/runs/eval-alverson-image-opus-4-8/`.

Scores:

- Barney image-entry:
  `output/runs/eval-barney-image-opus-4-8/02_ocr_ai_gpt51_v1/pages_html.jsonl`
  scored `overall_ratio = 0.711207`.
- Alverson image-entry:
  `output/runs/eval-alverson-image-opus-4-8/02_ocr_ai_gpt51_v1/pages_html.jsonl`
  scored `overall_ratio = 0.680902`.
- Screen floor: `overall_min_ratio = 0.680902`, `0/2` cases cleared the
  `0.99` bar.
- Instrumented token use across both one-page calls: `4027` prompt tokens,
  `918` completion tokens, estimated Opus 4.8 cost about `$0.0431`.

This does not beat the maintained handwritten rescue decision surface. It
barely clears the corrected Alverson image baseline, but Barney regresses
materially from the current maintained image-entry evidence (`0.908567` in
Story 192 / `0.883604` in the later improve-eval rerun). Manual inspection
shows the same visible-source OCR failure class: plausible prose with wrong
names and phrases rather than faithful transcription.

## Decision

Do not alter maintained providers.

Opus 4.8 is callable with the repo-local Anthropic key once sampling parameters
are omitted, and the custom promptfoo provider is useful for future Anthropic
frontier challenger runs. It is not a replacement for the maintained crop
detector, page-context deletion gate, or handwritten rescue lane:

- Detector quality is far below the Gemini 3 Flash winner.
- Page-context misses two fail-labeled residue cases, including the critical
  neighboring-portrait case that prior challengers also missed.
- `xhigh` effort does not repair the failed crop cases.
- Handwritten OCR remains far below the `0.99` bar and regresses Barney.

No maintained providers, prompts, scorers, or goldens should change.
