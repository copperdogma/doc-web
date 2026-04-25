# Gemini Page-Context Corrected-Golden Rerun

Date: 2026-04-24
Repo HEAD at measurement: `aa5b577`

## Trigger

The `page-122-001` page-context golden was corrected from `pass` to `fail`
after manual source-page inspection showed the crop leaks into a neighboring
portrait. The first Gemini regression rerun was blocked by the revoked shared
Google credential, so the corrected-golden score needed a fresh run after the
repo switched promptfoo child processes to `DOC_WEB_GEMINI_API_KEY`.

## Command

```bash
cd benchmarks && ../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/crop-page-level-deletion-gate.yaml \
  --no-cache \
  --filter-providers '^google:gemini-3\.1-flash-lite-preview$' \
  --output results/g31-crop-page-level-deletion-gate-promptfix-rerun-20260424.json \
  -j 1
```

## Result

| Surface | Model | Result | Notes |
| --- | --- | ---: | --- |
| `crop-page-level-deletion-gate` | Gemini 3.1 Flash Lite | `21/22` | `1` scorer failure, `0` provider errors |

Run metrics:

- Result: `benchmarks/results/g31-crop-page-level-deletion-gate-promptfix-rerun-20260424.json`
- Prompt tokens: `59636`
- Completion tokens: `1092`
- Total tokens: `60728`
- Average latency: `5454 ms`

## Failure Classification

- `page-122-001`: model-wrong false negative. Gemini returned
  `{"verdict": "pass"}` with the reason that the crop excluded surrounding
  caption text. The corrected page-context golden intentionally fails this crop
  because the source-page view shows a visible slice of the neighboring Sophie
  L'Heureux portrait at the crop edge.

## Decision

The previous Gemini `22/22` score is stale because it predates the corrected
`page-122-001` label. Record Gemini 3.1 Flash Lite as `21/22` on the corrected
page-context gate. GPT-5.5 Responses remains the only current `22/22` validator
on this corrected surface.
