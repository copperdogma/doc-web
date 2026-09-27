# Attempt 042 — GPT-6 Sol and Luna crop evaluation

Date: 2026-09-26. Owner: Doc Web, Story 235. Base: `92f341e169f7e81775a7f006ae39757303a8e88f` (`origin/main`). This attempt is uncommitted on `codex/gpt6-sol-luna-eval-20260926`.

Registry lineage: detector story refs 133/183/207/232/235, categories spec:4/spec:8, compromise C4; page gate story refs 209/232/235, categories spec:4/spec:8, compromise C5.

## Frozen decision contract

Scout 076 item 2 selected exact direct OpenAI Responses `gpt-6-sol` and `gpt-6-luna`, Standard foreground, `store:false`, no router, no automatic retries and a shared US$3.00 ceiling inclusive of probes and fresh controls. The source inputs are Doc Web's established public Onward benchmark images. The runtime detector is Gemini 3 Flash. The configured page-context regression provider is GPT-5.5 Responses.

The detector uses medium reasoning, one source image, the frozen `conservative-count` prompt's integer 0–1000 branch, strict JSON Schema, local coordinate validation, the original scorer/goldens and a 4,096 output-token maximum. Screen Image011, then full13 only after valid grouping and transport. Require 13/13 scorer passes, mean `overall >= 0.95` and zero contract errors. Run a fresh same-input Gemini 3 Flash control after full-matrix admission.

The independent page-context lane uses none reasoning, the frozen source-page plus crop prompt, strict verdict schema, original scorer/goldens and a 2,048 output-token maximum. Screen `page-122-001`; any false-safe `pass` stops that candidate's page lane immediately. Full22 and fresh GPT-5.5 Responses control are conditional on that screen passing. Require 22/22 and zero false-safe decisions. A candidate's detector result cannot excuse a page safety miss, and a page stop does not cancel that candidate's detector run.

These selection-exposed goldens support bounded comparison only. A runtime change, C5 removal or promotion needs separately frozen held-out truth and exact production-output safety proof. No default, prompt, scorer, golden, runtime or account setting changed.

Official sources checked 2026-09-26: [Sol](https://developers.openai.com/api/docs/models/gpt-6-sol), [Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [pricing](https://developers.openai.com/api/docs/pricing), [image accounting](https://developers.openai.com/api/docs/guides/images-vision), [data controls](https://developers.openai.com/api/docs/guides/your-data), and [Gemini 3 pricing](https://ai.google.dev/gemini-api/docs/pricing). At up to 272K input tokens, Sol is $2 input/$0.20 cached/$2.50 cache write/$10 output per million; Luna is $0.10/$0.01/$0.125/$0.50. Gemini 3 Flash is $0.50 input/$3 output per million. This run did not use long context, hosted tools or premium processing. OpenAI standard abuse logs may retain content; `store:false` is not ZDR. Only approved public images were sent.

## Zero-cost preflight and qualification

The primary checkout had unrelated dirty work and was read-only. This isolated worktree began at current remote `origin/main`. The existing ignored Doc Web `.env` had both OpenAI and Gemini variables present by name; the owner wrapper mapped them without copying a value. Conductor's vault had no OpenAI mapping and was not used. Authenticated `GET /v1/models/gpt-6-sol` and `/gpt-6-luna` each returned HTTP 200 and the exact ID. Owner discovery also listed the exact IDs. Catalog access was then separately confirmed by native inference.

Four projected detector/page tasks were checked row-for-row against the maintained YAML. The executed detector full tasks each contain 13 unique original rows; executed page screen tasks each contain the original `page-122-001` row; the Gemini control has those same 13 detector rows. Cases are independent single-message prompts, one image for detector and source page then crop for safety. The rendered detector text retained the existing integer-coordinate branch; page text remained unchanged. Each row has one Python structural assertion. The stale YAML comment naming an Anthropic judge does not invoke one; judge cost is zero. No conversation chain, implicit judge, subject cache or parallel dispatch was used. All fixtures and golden keys resolved before spending. Projected full22 templates were discarded after both safety stops, so no runnable page-full task remains from this attempt.

Before each call or batch, reservation used up to 20,000 input tokens **per high-detail image**, the full configured output maximum including reasoning, the higher cache-write input rate for candidates, and the provider's standard output price. The Sol full13 reserve was below $1.19, Luna full13 below $0.06, and fresh Gemini full13 below $0.77. Native probes, both screens and all admitted batches fit below $3 even with these conservative reservations. After each response, actual usage, cache reads and cache writes replaced its reservation. No unresolved billing remains. The owner adapter was updated to record `cache_write_tokens` separately from ordinary input and to retain complete raw envelopes before parsing; focused tests passed.

Each candidate passed a direct native generated-square strict integer detector probe and a distinct two-image strict page-schema probe. All four returned exact served IDs, terminal `completed`, valid usage and contract-valid JSON. The owner adapter then passed Promptfoo parity on real Image011 and page-122-001 inputs: exact served ID, lossless image normalization, strict schema, `store:false`, usage and raw-envelope hash were present. No HTTP error, incomplete response, wrong identity or local contract rejection occurred. Complete raw responses were saved in ignored mode-0600 owner storage before validation. [The manifest](../evidence/042-gpt6-sol-luna-crop-manifest.md) records all 34 direct Responses raw envelopes plus seven Promptfoo result files with hashes and sizes.

## Measured stages

| Stage | Sol | Luna | Fresh Gemini 3 Flash |
| --- | ---: | ---: | ---: |
| Image011 detector screen | pass, 0.9774; $0.0098735 | pass, 0.9834; $0.000521675 | not separately screened |
| Full13 detector | **13/13, 0.978308**; $0.110163 | **13/13, 0.987554**; $0.00582015 | **13/13, 0.961238**; $0.0562295 |
| Full13 mean / p50 / p95 latency | 3,404 / 3,418 / 5,006 ms | 3,077 / 3,072 / 4,146 ms | 6,805 / 6,434 / 12,973 ms |
| Page-122-001 safety screen | **false-safe pass**, $0.016351 | **false-safe pass**, $0.00082205 | not this lane's control |
| Full22 / fresh GPT-5.5 safety control | stopped, not measured | stopped, not measured | not applicable |

Sol's 13 detector rows used 41,366 input and 1,407 output tokens; Luna's used the same 41,366 input and 2,031 output tokens. Gemini's native Promptfoo arm used 17,329 input, 1,137 visible output and 14,718 reasoning tokens. The completed full matrices had zero provider/schema errors. Sol's weakest detector row was `Image000` at 0.8316 but remained a scorer pass. Luna's mean exceeded Sol and fresh Gemini; the observed bounded detector-quality ranking is Luna, Sol, Gemini. The same-input Gemini control is the current comparison; prior Astra and GPT-5.6 scores are historical context, not fresh parity arms in this campaign.

The page-context golden marks `page-122-001` fail. Sol and Luna both emitted contract-valid `pass` and described the crop as containing two portraits while excluding captions. Manual inspection of the source page and extracted crop confirms the left oval is Moise and Edward while the entire right oval is the separate Sophie L'Heureux portrait. This is neighboring-visual leakage from a different intended crop. Each failure is **prompt/pipeline-wrong → model-wrong** on the frozen safety truth surface, not a transport, scorer or golden defect. The full22 and fresh GPT-5.5 control were never admitted, so no 22-case candidate score or current GPT-5.5 superiority claim is made.

All-call usage-priced spend, including native probes and deliberately repeated screens in the full detector tasks: **Sol $0.137977500; Luna $0.007437875; fresh Gemini $0.056229500; total $0.201644875 / $3.00**. This is estimated from response usage and official token rates, including cache writes; no retry or judge call occurred. The ignored full JSON and raw envelopes are local; the tracked manifest provides durable hashes, byte sizes and stage provenance.

## Exact execution and verdict

The following command shape was used for each executed OpenAI Promptfoo task from `benchmarks/`, with the task/output pairs below. `PRICE_*` were the explicit Sol or Luna rates in the preceding paragraph. The owner wrapper read the existing ignored primary `.env`; these commands contain no credential value.

```bash
DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/doc-web/.env \
OPENAI_RESPONSES_RAW_ENVELOPE_DIR=/Users/cam/.codex/worktrees/gpt6-sol-luna-eval-20260926/doc-web/benchmarks/results/gpt6-sol-luna-20260926/raw \
OPENAI_RESPONSES_INPUT_PRICE_PER_1M=PRICE_INPUT \
OPENAI_RESPONSES_CACHED_INPUT_PRICE_PER_1M=PRICE_CACHED \
OPENAI_RESPONSES_CACHE_WRITE_PRICE_PER_1M=PRICE_WRITE \
OPENAI_RESPONSES_OUTPUT_PRICE_PER_1M=PRICE_OUTPUT \
PROMPTFOO_PYTHON=/Users/cam/miniconda3/bin/python \
PROMPTFOO_EVAL_TIMEOUT_MS=180000 \
../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/TASK \
  --no-cache --no-share --no-table -j 1 --output results/gpt6-sol-luna-20260926/OUT
```

Executed `(TASK, OUT)` in order: `(gpt6-sol-detector-screen-20260926.yaml, sol-detector-screen.json)`, `(gpt6-sol-page-screen-20260926.yaml, sol-page-screen.json)`, `(gpt6-luna-detector-screen-20260926.yaml, luna-detector-screen.json)`, `(gpt6-luna-page-screen-20260926.yaml, luna-page-screen.json)`, `(gpt6-sol-detector-full-20260926.yaml, sol-detector-full.json)`, `(gpt6-luna-detector-full-20260926.yaml, luna-detector-full.json)`. For Sol the four `PRICE_*` values above were `2`, `0.2`, `2.5`, `10`; for Luna they were `0.1`, `0.01`, `0.125`, `0.5`. The native probes used the same adapter `_build_body`, generated 32-pixel black PNG input, strict schema and 1,024 maximum output tokens through direct `POST /v1/responses`. Their four raw hashes are in the manifest. The fresh control command was:

```bash
DOC_WEB_ENV_FILE=/Users/cam/Documents/Projects/doc-web/.env \
PROMPTFOO_EVAL_TIMEOUT_MS=180000 \
../scripts/run_with_doc_web_env.py promptfoo eval \
  -c tasks/gpt6-detector-gemini-control-20260926.yaml \
  --no-cache --no-share --no-table -j 1 \
  --output results/gpt6-sol-luna-20260926/gemini-detector-full.json
```

Run these only as a new authorized attempt with fresh budget accounting. In particular, do not run full22 for these frozen page arms as a continuation of Attempt 042: each already hit its hard false-safe stop.

**Access:** available and exact direct inference verified for both candidates. **Transport:** qualified for both frozen schemas and owner harness. **Reliability:** all 34 direct OpenAI calls completed without transport or schema error; production reliability remains unmeasured. **Capability:** both pass the bounded 13-page detector contract and exceed fresh Gemini on mean score; Luna has the strongest bounded detector value here. Both fail the targeted page-context safety differentiator; full22 is not measured. **Economics:** Luna's full detector was cheaper and faster than the fresh Gemini arm; Sol was faster but cost more. **Adoption:** retain Gemini 3 Flash as runtime detector and GPT-5.5 Responses as page-context regression provider. Do not adopt Sol or Luna for the page-context safety role under this contract. Their detector quality remains a useful candidate signal, but neither is promoted from this exposed corpus without separate held-out and production-output safety evidence. Keep C5 residue.

Focused verification: `python -m pytest -q tests/test_openai_responses_model_provider.py tests/test_crop_benchmark_substrate.py` passed 24 tests after adapter changes. No pipeline runtime module or recipe was changed, so no `driver.py` run was claimed. No commit or push occurred.
