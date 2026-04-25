# GPT-5.5 Page-Context Applied Default

Date: 2026-04-24
Repo HEAD at measurement: `aa5b577`

## Trigger

The corrected-golden reruns showed that GPT-5.5 Responses is the only current
`22/22` page-context crop validator. Gemini 3.1 Flash Lite's old `22/22` score
predates the `page-122-001` golden correction, and its fresh rerun is `21/22`.

## Changes

- `benchmarks/tasks/crop-page-level-deletion-gate.yaml`
  - narrowed the maintained provider list to `openai:responses:gpt-5.5`;
  - removed non-winning challenger providers from the default task surface.
- `tests/test_crop_benchmark_substrate.py`
  - added a regression check that the maintained page-context task defaults to
    the current corrected-golden winner.
- `docs/evals/registry.yaml`, `benchmarks/README.md`, and
  `docs/runbooks/crop-eval-workflow.md`
  - updated the maintained command and current-result guidance.

## Command

```bash
cd benchmarks && ../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/crop-page-level-deletion-gate.yaml \
  --no-cache \
  --output results/crop-page-level-deletion-gate-gpt55-responses-current-20260424.json \
  -j 1
```

## Result

| Surface | Model | Result | Notes |
| --- | --- | ---: | --- |
| `crop-page-level-deletion-gate` | GPT-5.5 Responses | `22/22` | `0` failures, `0` provider errors |

Run metrics:

- Result: `benchmarks/results/crop-page-level-deletion-gate-gpt55-responses-current-20260424.json`
- Prompt tokens: `255127`
- Completion tokens: `1127`
- Total tokens: `256254`
- Average latency: `5253 ms`
- Estimated cost: about `$1.3094` total, `$0.0595` per case

## Decision

Apply GPT-5.5 Responses as the maintained page-context C5 deletion-gate
validator. This does not switch the bounded crop-only `crop-validation` surface,
where Gemini 3.1 Flash Lite remains the current `40/40` winner.
