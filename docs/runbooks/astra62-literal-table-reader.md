# Opt-in Astra 6.2 source-only literal table review

From a checkout containing the reviewed patch, run the alternate recipe for
eligible public or authored synthetic PDFs requiring exact source-table review.
Use the lockfile environment (`uv sync --locked --extra driver` and then
`uv run --locked --extra driver python …`) or an existing environment with
OpenAI Python SDK 1.109.1 or the qualified 2.21.0. The legacy requirements file
pins an SDK from before the Responses API.

```bash
python scripts/run_with_doc_web_env.py python driver.py \
  --recipe configs/recipes/recipe-pdf-literal-tables-html-astra62.yaml \
  --input-pdf /absolute/path/to/eligible-source.pdf \
  --run-id reviewed-astra62-tables
```

The new recipe keeps the production Astra OCR first pass and explicitly uses
GPT-6.2 Astra for the independent source-only table review. The export gate
requires proof from that exact model and the unchanged source. A disagreement
or reported ambiguous glyph holds the page. Inspect the review report before
any further publication action. The recipe bounds the review to three pages
and three requests with conservative reservations. The native input count
refuses requests that exceed the $2 reserve at Standard rates including
30-minute cache writes and the entire reasoning/visible output allowance. The initial OCR has its own
existing operational limits.

Roll back by using `configs/recipes/recipe-pdf-literal-tables-html.yaml` with a
fresh run ID to select the previous OpenAI Astra source reader. Existing
outputs and records remain interpretable with their original recipe and
authority. The Argon opt-in recipe remains separately available. See
[Attempt097](../evals/attempts/097-gpt62-astra-source-fidelity.md) for the
source coverage, precise economics and replay limits.
