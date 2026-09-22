# Grok 4.7 Direct xAI Crop Evaluation

Date measured: 2026-09-22
Repo base: `35798b9af598f9a0f5829b3ccead5637392afe9f`
Scope: Story 207's frozen `image-crop-extraction` detector only

## Contract

The approved candidate was exact `grok-4.7` at `https://api.x.ai/v1/responses`,
with `reasoning.effort=low`, high image detail, `store=false`, serial
concurrency, no cache, and xAI's strict JSON schema. The maintained task now
uses 0–1000 integer coordinates. The existing direct-xAI adapter still declared
normalized floats, so this evaluation repaired the adapter schema and prompted
xAI's provider ID to use the maintained integer instruction before any call.

Only owner-confirmed public benchmark images and a generated black-square image
were sent. xAI's disclosed default retention is 30 days and it does not train
on inputs without permission; ZDR was not required for this approved public
payload. Response storage was disabled. No runtime default, prompt semantic,
golden, scorer, page-context, crop-only, or deployment change was authorized.

The progressive contract was native synthetic image/schema qualification, the
same synthetic request through the owner adapter, Image011, then full13 only
after Image011 passed. The full detector required `13/13`, `overall >=0.95`,
zero provider/schema errors. A fresh Gemini 3 Flash incumbent run was required
only if Grok cleared that detector contract. Total provider spend cap: US$0.50.

## Transport and reliability

Two direct native synthetic probes completed while recovering host-output state;
both returned exact `grok-4.7`, terminal `completed`, valid usage, and valid
strict integer output. This duplicate is retained as an orchestration error,
not presented as a reliability repeat. The subsequent owner-adapter parity
probe also returned exact identity and valid strict integer output. The adapter
now retains raw HTTP bodies before response parsing/status handling when its
ignored raw-envelope path is configured.

Image011 ran through Promptfoo with the frozen `conservative-count` semantic
prompt and structural scorer. It passed the scorer at `0.7375`, correctly
grouping the seal and signatures. Its upper emblem crop was loose, so this was
a weak screen pass rather than evidence of superior localization.

## Frozen detector result

Command, from `benchmarks/` with the temporary ignored `XAI_API_KEY` available
only through `../scripts/run_with_doc_web_env.py`:

```bash
XAI_GROK_MODEL=grok-4.7 XAI_GROK_EXPECTED_SERVED_MODEL=grok-4.7 \
XAI_GROK_REASONING_EFFORT=low XAI_GROK_MAX_OUTPUT_TOKENS=2048 \
XAI_GROK_RAW_ENVELOPE_DIR="$WORKTREE/benchmarks/results/grok47-20260922/raw" \
PROMPTFOO_EVAL_TIMEOUT_MS=120000 ../scripts/run_with_doc_web_env.py \
promptfoo eval -c tasks/image-crop-extraction.yaml \
--providers "python:$WORKTREE/benchmarks/providers/xai_grok_responses.py" \
--filter-prompts conservative-count --no-cache --no-share \
--output results/grok47-20260922/full13.json --no-table -j 1
```

| Metric | Result |
| --- | ---: |
| structural passes | 11/13 |
| overall mean | 0.745785 |
| provider/schema errors | 0 |
| mean row latency | 8059 ms |
| full13 reported cost | $0.116280 |
| all-call reported spend | $0.147314 / $0.50 |

The two failing rows were manually source-checked.

- **Image001:** the source contains the large stylized `ONWARD TO THE UNKNOWN`
  title artwork, while Grok returned `{"images": []}`. This is model-wrong
  omission, not a golden or scorer defect.
- **Image059:** Grok found both photographs but started each crop too low,
  missing their upper regions. The source and frozen goldens confirm
  model-wrong undercoverage.

## Layered verdict

| Layer | Verdict |
| --- | --- |
| access | available |
| transport | qualified for direct strict image/integer schema and owner-adapter parity |
| reliability | one serial bounded campaign returned valid responses; this is not production reliability evidence |
| capability | fails frozen-detector acceptance (`11/13`, `0.745785`; required `13/13`, `>=0.95`) |
| economics | measured: `$0.147314` all calls, including qualification and duplicate exposure |
| adoption | do not adopt for the crop detector; defaults unchanged |

The fresh Gemini control was not decision-bearing after Grok failed the detector
entry gate, so it was not run. The crop-only and 22-case page-context/deletion
gates remain **not measured**, rather than failed. Retry only for a materially
revised Grok checkpoint or source-backed visual-grounding change; do not repeat
this same model/configuration automatically.

Raw response/result hashes and safe regeneration pointers are in
`docs/evals/evidence/039-grok47-direct-xai-manifest.md`.
