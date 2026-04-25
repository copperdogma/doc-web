# GPT-5.5 Non-Crop Eval Screens

Date: 2026-04-24
Repo HEAD at measurement: `aa5b577`

## Trigger

After the crop eval refresh and full `onward-table-fidelity` run, the remaining
nearby GPT-oriented promptfoo screens were checked with `gpt-5.5`.

## Commands

```bash
cd benchmarks && promptfoo eval -c tasks/onward-single-page-gpt54-screen.yaml \
  --no-cache --filter-providers 'openai:chat:gpt-5.5' \
  --output results/gpt55-onward-single-page-screen-20260424.json -j 1

cd benchmarks && promptfoo eval -c tasks/onward-table-fidelity-single-page-budget.yaml \
  --no-cache --filter-providers 'openai:chat:gpt-5.5' \
  --output results/gpt55-onward-single-page-budget-20260424.json -j 1
```

The genealogy table screen was also attempted:

```bash
cd benchmarks && promptfoo eval -c tasks/ocr-genealogy-tables-gpt-only.yaml \
  --no-cache --filter-providers 'openai:chat:gpt-5.5' \
  --filter-prompts 'table-strict' \
  --output results/gpt55-ocr-genealogy-tables-table-strict-20260424.json -j 1
```

That command aborted before any provider call because
`benchmarks/input/onward-pages-b64/Image007.b64.txt` is missing.

## Results

| Surface | Result | Tokens | Estimated Cost | Notes |
| --- | ---: | ---: | ---: | --- |
| `onward-single-page-gpt54-screen` | `0/3`, average score `0.0` | `2786` | `$0.0265` total | no provider errors |
| `onward-table-fidelity-single-page-budget` | `0/15`, average score `0.0` | `14957` | `$0.1633` total | no provider errors |
| `ocr-genealogy-tables-gpt-only` | blocked | `0` | `$0` | missing canonical `onward-pages-b64` fixtures |

The two completed single-page screens failed at the prompt/scorer-contract
level, not at API availability: GPT-5.5 returned HTML-shaped output, but the
`html_table_diff.py` scorer assigned zero structure preservation for every
case.

## Blocked Genealogy Screen

The missing genealogy table fixtures are not equivalent to the local raw
`input/onward-to-the-unknown-images/*.jpg` files. A temporary full-resolution
base64 directory was generated from those raw images, but the run was stopped
and the temporary directory was removed because those `5100x6600` encodings
would redefine the benchmark surface from the original downscaled canonical
fixtures.

## Pricing Refresh

OpenAI price rows used for these estimates were refreshed from official
OpenAI pricing/model pages:

- `gpt-5.5`: `$5.00` input / `$30.00` output per 1M tokens
- `gpt-5.5-pro`: `$30.00` input / `$180.00` output per 1M tokens
- `gpt-5.4`: `$2.50` input / `$15.00` output per 1M tokens
- `gpt-5.4-mini`: `$0.75` input / `$4.50` output per 1M tokens
- `gpt-5.4-nano`: `$0.20` input / `$1.25` output per 1M tokens

`gpt-5.5-pro` was not used in promptfoo because the current `openai:chat`
provider path returned "not a chat model"; official model docs position it for
Responses API use.

## Decision

Keep GPT-5.5 available in these benchmark configs, but do not adopt it for the
single-page Onward OCR lane. Restore or intentionally regenerate the canonical
`onward-pages-b64` fixtures before trying to compare GPT-5.5 on
`ocr-model-genealogy`.
