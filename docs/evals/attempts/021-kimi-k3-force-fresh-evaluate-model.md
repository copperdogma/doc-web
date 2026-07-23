# Kimi K3 Force-Fresh `/evaluate-model` Attempt

Date: 2026-07-22
Repo HEAD at start: `b54f0d93735ebc43a57b6324902f17599406efd6`
Status: Complete — no adoption; detector quality improved, but the page-context safety gate failed

## Brief, ownership, and alignment

The user explicitly requested a fresh Kimi K3 rerun using `/evaluate-model`.
That force-fresh instruction overrides duplicate-evidence suppression but not
access, transport, fairness, privacy, or spend gates. The primary decision
surface remains the 13-case `image-crop-extraction` C4 detector owned by Story
207. Story 209's 22-case `crop-page-level-deletion-gate` remains a progressive
follow-on only after a candidate clears the detector prerequisite.

This route is aligned with the Ideal's fidelity, traceability, and eval-before-
build tenets and with the active C4/C5 compromise gates. No narrower crop ADR
applies. Only checked-in public fixtures were payload-eligible for the quality
run because neither route establishes zero data retention. The user explicitly
authorized sending those fixtures through OpenRouter before the scored run.

## Predeclared decision contract

- Candidate: exact first-party Moonshot model `kimi-k3`.
- Candidate configuration: `reasoning_effort=max`, `max_completion_tokens=4096`,
  strict JSON Schema, maintained `conservative-count` prompt, no sampling
  controls, `--no-cache`, concurrency `1`.
- Fresh incumbent: maintained `google:gemini-3-flash-preview` on the same frozen
  prompt, 13 fixtures, scorer, and golden.
- Detector target: overall at least `0.95`, pass rate at least `0.90`, and an
  honestly competitive result against the fresh incumbent.
- Page-context gate: run only if K3 clears the detector prerequisite; compare
  against maintained `openai:responses:gpt-5.5` and its hard `22/22` contract.
- Transport ladder: exact-ID access, minimal strict-schema text, native vision,
  one-case PromptFoo parity, full detector, conditional page-context gate.
- Reliability gate: exact served model, exactly one choice, terminal
  `finish_reason=stop`, valid usage evidence, and locally validated schema.
- Diagnostic cap: at most two evidence-led repair/configuration arms.
- Shared candidate-plus-incumbent spend ceiling: US$5.

The same decision contract was written to Stories 207 and 209 before the first
live provider request.

After direct Moonshot authentication failed, the user explicitly authorized
copying a sibling repo's OpenRouter key into doc-web's ignored `.env`. The exact
candidate route therefore changed from first-party `kimi-k3` to OpenRouter's
dedicated `moonshotai/kimi-k3` alias, which the authenticated catalog maps to
canonical snapshot `moonshotai/kimi-k3-20260715` and a single Moonshot AI
provider. Prompt, fixtures, scorer, golden, reasoning effort, thresholds, and
the `$5` aggregate cap remain frozen.

## Current first-party contract

Moonshot's current K3 documentation identifies `kimi-k3` as a native vision
model with a 1M context window. It always reasons and accepts
`reasoning_effort` values `low`, `high`, and `max`, defaulting to `max`. The
Chat Completions endpoint is
`POST https://api.moonshot.ai/v1/chat/completions`; `max_completion_tokens` is
the current completion limit field. K3 supports strict structured output via
`response_format.type=json_schema` with `strict=true`. Current direct pricing
is `$0.30/M` cached input, `$3/M` uncached input, and `$15/M` output. Moonshot's
tier limits make concurrency `1` the conservative qualification setting.

Official references:

- <https://platform.kimi.ai/docs/guide/kimi-k3-quickstart>
- <https://platform.kimi.ai/docs/api/chat>
- <https://platform.kimi.ai/docs/api/models-overview>
- <https://platform.kimi.ai/docs/pricing/chat-k3>
- <https://platform.kimi.ai/docs/pricing/limits>
- <https://platform.kimi.ai/docs/agreement/userprivacy>

## Harness qualification repair

Before provider spend, the existing Moonshot adapter was found insufficient for
an attributable K3 score: it requested loose JSON and discarded served-model
and terminal-state evidence. The adapter was hardened to:

- send separate strict JSON Schemas for detector and page-context tasks;
- preserve K3's no-sampling, `reasoning_effort` request contract;
- reject lossy prompt normalization before an image can be silently omitted;
- require exact served-model identity, exactly one choice, and
  `finish_reason=stop`;
- validate the returned JSON locally and retain only a SHA-256 fingerprint for
  invalid output;
- retain request/response IDs, requested settings, token use, and estimated
  model-specific cost while rejecting malformed usage evidence.

Focused validation passed before direct qualification and was extended after
the route change. These are harness results, not K3 quality evidence.

## Live access result

The first authenticated qualification request used the repo-local `.env`
through `scripts/run_with_doc_web_env.py`, without printing the key. A direct
`GET https://api.moonshot.ai/v1/models` returned HTTP `401` with provider error
type `incorrect_api_key_error` and message `Incorrect API key provided`.
Removing any ambient Moonshot variables and reloading only the repo credential
produced the same response; no ambient standard or doc-web Moonshot key was
present to shadow the file.

The user then explicitly authorized copying the sibling Dossier OpenRouter key
into doc-web's ignored `.env` as `DOC_WEB_OPENROUTER_API_KEY`; the value was
neither printed nor tracked. Authenticated `GET /api/v1/models` returned HTTP
200 and proved the exact `moonshotai/kimi-k3` alias, canonical snapshot
`moonshotai/kimi-k3-20260715`, Moonshot AI provider, native text/image input,
1,048,576-token context, strict structured-output support, and `max/high/low`
reasoning with default `max`. Current router pricing matches direct Moonshot:
`$0.30/M` cached input, `$3/M` uncached input, and `$15/M` output. Reference:
<https://openrouter.ai/moonshotai/kimi-k3-20260715>.

The repo environment wrapper now maps the doc-web-scoped key to
`OPENROUTER_API_KEY`. The adapter uses `max_tokens`, OpenRouter's normalized
`reasoning={effort:max, exclude:true}`, strict `response_format`, parameter
enforcement, and disabled fallbacks for this route. Two live calls succeeded:

- strict-schema text: exact served model `moonshotai/kimi-k3`, provider
  `Moonshot AI`, `finish_reason=stop`, 291 tokens, estimated cost `$0.001509`;
- generated synthetic-image vision: exact model/provider and terminal state,
  schema-valid bbox `[0.234, 0.234, 0.766, 0.766]` for the known black square,
  522 tokens, estimated cost `$0.004506`.

The qualification calls cost `$0.006015`. After the user explicitly authorized
the checked-in public fixtures, both task contracts passed a one-case no-cache
PromptFoo smoke with exact model/provider attribution and terminal success.

## Fresh scored comparison

All subject calls used the frozen prompts, fixtures, scorers, and goldens with
no cache. K3 used OpenRouter's exact `moonshotai/kimi-k3` route, Moonshot AI as
the only permitted provider, maximum reasoning, strict task-specific JSON
Schema, and concurrency `1`. Every one of the 35 scored K3 responses reported
the exact requested model, provider `Moonshot AI`, and `finish_reason=stop`;
there were no provider or contract errors.

| Surface | Model | Result | Mean score | Mean latency | Reported/estimated cost |
| --- | --- | ---: | ---: | ---: | ---: |
| C4 detector | Kimi K3 | `13/13` | `0.9844` | `28,919 ms` | `$0.2638671` |
| C4 detector | Gemini 3 Flash incumbent | `13/13` | `0.9635` | `7,395 ms` | `$0.0609785` |
| C5 page context | Kimi K3 | `21/22` | `0.9545` | `25,740 ms` | `$0.8133594` |
| C5 page context | GPT-5.5 Responses incumbent | `22/22` | `1.0000` | `4,095 ms` | `$1.310585` estimated from recorded usage |

K3 beat the fresh Gemini detector by `0.0209` mean score and won 9 of 13
individual cases. It was about `3.91x` slower and `4.33x` as expensive on that
surface. This is broad positive detector evidence, not an isolated fixture win.
It does not, however, justify a second production route by itself because the
maintained Gemini path still passed every case and is materially faster and
cheaper.

K3 then missed the hard `22/22` page-context gate. The sole false negative was
`page-122-001`: K3 returned `pass`, claiming the crop contained only the two
portrait photographs and excluded surrounding content. Manual inspection of
both `Image121` and the crop confirms the crop intended for Moise L'Heureux and
Edward includes the entire neighboring Sophie L'Heureux oval portrait. The
source-backed golden is correct; the valid, schema-compliant K3 answer is model-
wrong. This reproduces the same safety-relevant blind spot previously observed
with Kimi K2.6, despite K3 already using its maximum reasoning setting, so no
configuration retry was warranted.

The full cost ledger is `$2.523904` against the `$5` cap: `$1.1523405` reported
for K3 qualification, smokes, and scored calls; `$0.0609785` reported for
Gemini; and `$1.310585` conservatively estimated for GPT-5.5 from 255,127 input
plus 1,165 output tokens at the current standard `$5/M` input and `$30/M`
output rates. PromptFoo recorded `$0` for the OpenAI arm, so the estimate is
retained rather than presenting that row as free. Current pricing reference:
<https://developers.openai.com/api/docs/models/gpt-5.5>.

## Reproduction commands

Run from `benchmarks/` after loading Node 24. The repo wrapper maps the ignored
doc-web credential without printing it.

```bash
MOONSHOT_KIMI_API_ROUTE=openrouter MOONSHOT_KIMI_MODEL=moonshotai/kimi-k3 MOONSHOT_KIMI_REASONING_EFFORT=max PROMPTFOO_EVAL_TIMEOUT_MS=240000 ../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/image-crop-extraction.yaml --providers "python:$(pwd)/providers/moonshot_kimi_chat.py" --filter-prompts conservative-count --no-cache --output results/kimi-k3-force-fresh-openrouter-detector-20260722.json -j 1
../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/image-crop-extraction.yaml --filter-providers 'google:gemini-3-flash-preview' --filter-prompts conservative-count --no-cache --output results/kimi-k3-force-fresh-incumbent-gemini3-flash-20260722.json -j 1
MOONSHOT_KIMI_API_ROUTE=openrouter MOONSHOT_KIMI_MODEL=moonshotai/kimi-k3 MOONSHOT_KIMI_REASONING_EFFORT=max MOONSHOT_KIMI_OUTPUT_CONTRACT=page_context_validation PROMPTFOO_EVAL_TIMEOUT_MS=240000 ../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/crop-page-level-deletion-gate.yaml --providers "python:$(pwd)/providers/moonshot_kimi_chat.py" --no-cache --output results/kimi-k3-force-fresh-openrouter-page-context-20260722.json -j 1
../scripts/run_with_doc_web_env.py promptfoo eval -c tasks/crop-page-level-deletion-gate.yaml --filter-providers 'openai:responses:gpt-5.5' --no-cache --output results/kimi-k3-force-fresh-incumbent-gpt55-page-context-20260722.json -j 1
```

## Evaluated-code and evidence manifest

The run used base HEAD `b54f0d93735ebc43a57b6324902f17599406efd6`,
PromptFoo `0.121.1`, Node `v24.13.1`, and Darwin arm64. The scored adapter and
environment mapping were dirty, so the base SHA alone must not be used to
identify the evaluated transport.

| Relevant changed file | SHA-256 |
| --- | --- |
| `benchmarks/providers/moonshot_kimi_chat.py` | `f92459e17fca3d388f72ab2a181ff3c0a71e8d2545036f7d11f4a207bb3ac89a` |
| `doc_web/env.py` | `6153a345dc79252f45075b12f0b2c682c900016ab2558b6c1b074e3a4bd06fe8` |
| `tests/test_moonshot_kimi_chat_provider.py` | `79004d5fdf2649692880c9f7531840f174e61b9b7ace37a71ced44cc7002c989` |
| `tests/test_doc_web_env.py` | `d5625529d56d2322373585ec85d15341e74b75f11d8b7a872ce5e9ad87ec3b91` |

The frozen detector task/prompt/scorer/golden hashes are respectively
`7edae5fe3c935517396a8d37cd8f148cb2b592ed4d206168dbb62273d758cf3e`,
`9a22e566f30eac6258a78a28107d77a17940eca06858dd20cb8d7bc97fc84aba`,
`7fcf07e05726bf3ebbc2488a503a9d7f165dde79649890cbd65f12a6ce4c19e7`,
and `2ac0a8f01e00a252439da1f4827a85bc5118bf96460a3ff1780e642eafc60f90`.
The page-context equivalents are
`b2b8d2ca4cfd48a09936764715941d914d5c1e4e6115e30d7916fe2ebe770e63`,
`2ccc8c96ef69c14102d7ffd13b5a39715e5cd136b497510b1b2f88243009a5a0`,
`12eb63725523bd00d59ce12b7486db8c9244124a0c57bb68cae8b8e9e7d288fb`,
and `4bcba8f4ab8a742608e7cfc1438464a71cf56aa4cd9cbe9e0a67e4a410ac18a5`.

| Ignored raw artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| `kimi-k3-force-fresh-openrouter-smoke-20260722.json` | `d3398ed1fab92da2d84a531f39706df9f27a4b821ab352d336a27e54e1a831c3` | 1,203,799 |
| `kimi-k3-force-fresh-openrouter-detector-20260722.json` | `a4c530dfb28f6238e3a0b9e92f8821cfcb10a451101de23bfe9d2390c18c370e` | 9,625,267 |
| `kimi-k3-force-fresh-incumbent-gemini3-flash-20260722.json` | `c5513f481cae03e913542824c861bc18c03ba3a8b651d62d0cb48a98594153b1` | 9,689,313 |
| `kimi-k3-force-fresh-openrouter-page-context-smoke-20260722.json` | `f82d7f5c32c0c860c385ea93cfab52eb9af1513da9bc5727ddd5f17bedfdfd30` | 9,132,617 |
| `kimi-k3-force-fresh-openrouter-page-context-20260722.json` | `5043f11e5e7f8d6bc7bafc83d075c5316acca229e78e0091b3fc5ee08aee335e` | 90,978,782 |
| `kimi-k3-force-fresh-incumbent-gpt55-page-context-20260722.json` | `ef452254f6acf71eefd3dacbd4ba3873a9ac5ea7cfcc1e3bb934926b613e3fda` | 91,102,614 |

The hashes authenticate the retained local copies; the aggregate and decisive
case evidence above remain the portable record because raw result JSON is
ignored.

## Validation

- `python -m pytest tests/test_moonshot_kimi_chat_provider.py tests/test_doc_web_env.py -q` — `15 passed` after adding the OpenRouter route and key mapping.
- `python -m ruff check benchmarks/providers/moonshot_kimi_chat.py tests/test_moonshot_kimi_chat_provider.py` — passed.
- `python -m ruff format --check benchmarks/providers/moonshot_kimi_chat.py tests/test_moonshot_kimi_chat_provider.py` — passed.
- `make methodology-compile && make methodology-check` — generated graph and story index are current.
- `make lint` — passed.
- Final `make test` — `903 passed`, with the same four unrelated Pydantic deprecation warnings in `portionize_headers_numeric_v1`, in `822.90s`.
- `git diff --check` — passed.

## Decision

**Do not adopt Kimi K3 as either maintained crop default.** It is a stronger
detector on this frozen sample, but the existing Gemini detector already clears
the maintained gate at roughly one quarter of K3's latency and cost. More
importantly, K3 fails the hard page-context deletion-safety contract on a
source-verified neighboring-portrait leak that GPT-5.5 catches. Keep both
maintained providers unchanged and retain K3 as positive detector evidence plus
negative page-context evidence.

There is no immediate rerun warranted. Revisit only for a materially revised K3
snapshot or a new source-backed detector failure population large enough to
predeclare an escalation-value gate that could justify the extra route.
