# GPT-5.5 Page-Context Prompt Repair

Date: 2026-04-24
Repo HEAD at measurement: `aa5b577`

## Trigger

The direct OpenAI Responses rerun for `gpt-5.5` improved the
`crop-page-level-deletion-gate` result from the Chat path's `16/22` to `20/22`,
but still left two reported failures: `page-021-001` and `page-122-001`.

## Failure Classification

- `page-021-001`: prompt-wrong. Manual crop inspection showed a ranch photo
  with a large pale sky/snow/photo background area. The earlier prompt let the
  model treat that as excessive blank page margin, but it is real image
  content.
- `page-122-001`: golden-wrong for the page-context gate. Manual source-page
  inspection showed the crop includes a visible slice of the neighboring Sophie
  L'Heureux portrait. The crop-only golden remains unchanged because that eval
  intentionally ignores source-page composition, but the page-context deletion
  gate should fail neighboring visual leakage.
- `page-004-000`: prompt-wrong over-strictness discovered during the full
  rerun. GPT-5.5 Responses treated tight line-art framing as incompleteness.
  The source page shows the checked-in crop contains the intended wagon
  illustration without page text or neighboring visual leakage.

## Changes

- `benchmarks/prompts/validate-page-level-crop.js`
  - states that the page-context gate primarily checks page-text and
    neighboring-visual leakage, not fine-art composition;
  - counts sky, snow, walls, studio backdrops, faded photo backgrounds, and
    similar light image regions as image content;
  - tolerates tight line-art/photo framing unless the full-page context clearly
    shows a large missing part of the intended visual.
- `benchmarks/golden/crop-page-level-deletion-gate.json`
  - corrected `page-122-001` from `pass` to `fail`;
  - updated the page-context corpus count to `17` pass labels and `5` fail
    labels.

## Commands

```bash
cd benchmarks && promptfoo eval -c tasks/crop-page-level-deletion-gate.yaml \
  --no-cache --filter-providers '^openai:responses:gpt-5\.5$' \
  --filter-failing results/gpt55-responses-crop-page-level-deletion-gate-20260424.json \
  --output results/gpt55-responses-crop-page-level-deletion-gate-promptfix-targeted-20260424.json -j 1

cd benchmarks && promptfoo eval -c tasks/crop-page-level-deletion-gate.yaml \
  --no-cache --filter-providers '^openai:responses:gpt-5\.5$' \
  --filter-failing results/gpt55-responses-crop-page-level-deletion-gate-promptfix-20260424.json \
  --output results/gpt55-responses-crop-page-level-deletion-gate-promptfix-targeted3-20260424.json -j 1

cd benchmarks && promptfoo eval -c tasks/crop-page-level-deletion-gate.yaml \
  --no-cache --filter-providers '^openai:responses:gpt-5\.5$' \
  --output results/gpt55-responses-crop-page-level-deletion-gate-promptfix-final-20260424.json -j 1

cd benchmarks && promptfoo eval -c tasks/crop-page-level-deletion-gate.yaml \
  --no-cache --filter-providers '^google:gemini-3\.1-flash-lite-preview$' \
  --output results/g31-crop-page-level-deletion-gate-promptfix-20260424.json -j 1

cd benchmarks && ../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/crop-page-level-deletion-gate.yaml --no-cache \
  --filter-providers '^google:gemini-3\.1-flash-lite-preview$' \
  --output results/g31-crop-page-level-deletion-gate-promptfix-rerun-20260424.json -j 1
```

## Results

| Surface | Model | Result | Notes |
| --- | --- | ---: | --- |
| `crop-page-level-deletion-gate` | GPT-5.5 Responses | `22/22` | `0` failures, `0` errors |
| `crop-page-level-deletion-gate` | Gemini 3.1 Flash Lite | `21/22` | after `DOC_WEB_GEMINI_API_KEY` repair; `page-122-001` false negative |

GPT-5.5 Responses final token and cost summary:

- Result: `benchmarks/results/gpt55-responses-crop-page-level-deletion-gate-promptfix-final-20260424.json`
- Prompt tokens: `255127`
- Completion tokens: `1165`
- Average latency: `4911 ms`
- Estimated cost: about `$1.3106` total, `$0.0596` per case

Gemini corrected-golden rerun summary:

- Result: `benchmarks/results/g31-crop-page-level-deletion-gate-promptfix-rerun-20260424.json`
- Prompt tokens: `59636`
- Completion tokens: `1092`
- Average latency: `5454 ms`
- Provider/system errors: `0`
- Remaining mismatch: `page-122-001`, model-wrong false negative. Gemini
  passed the crop because it excluded surrounding caption text, but the
  corrected page-context golden fails it for visible neighboring portrait
  leakage.

## Evidence Inspected

- `/tmp/doc-web-gpt55-page-context/page-021-001.jpg`: ranch crop; pale
  background is part of the photograph.
- `/tmp/doc-web-gpt55-page-context/Image121.jpg` and
  `/tmp/doc-web-gpt55-page-context/page-122-001.jpg`: source page and crop show
  the crop includes a neighboring portrait slice at the right edge.
- `/tmp/doc-web-gpt55-page-context/Image003.jpg` and
  `/tmp/doc-web-gpt55-page-context/page-004-000.jpg`: source page and crop show
  tight wagon line-art framing without page text or neighboring visual leakage.

## Decision

Record GPT-5.5 Responses as a passing page-context validator on this corrected
gate. The fresh Gemini rerun is no longer blocked by credentials, but its
historical `22/22` result is stale after the `page-122-001` golden correction;
current Gemini is `21/22` on the corrected gate. The broader C5 compromise
remains active because the checked corpus still contains explicit fail-labeled
crop residue cases.
